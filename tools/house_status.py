#!/usr/bin/env python3
"""Report the Git state of every House child repository.

The child list comes from `house/atlas.yaml`, which owns it; this tool never
restates it. For each child it reads local Git state only (no fetch, no network,
no writes): whether an upstream remote exists, commits not yet pushed to the
upstream as last fetched, uncommitted files, and the last commit date.

A child is AT RISK when its work exists only on this machine: it has no remote,
or it has commits no remote has. A branch with no upstream yet (a fresh work
branch) is fine while every commit on it is already on a remote. Uncommitted
files are reported but are normal during work. A child whose Git call times
out is reported as at risk with that reason, so one hung repository neither
stops the report nor passes as fine. A child with uncommitted files is shown
as DIRTY, never plain "ok", but it does not change the exit status. Exit status
is 1 when any child is at risk or missing, so a scheduled caller can alert on
it.

Usage:
    python3 tools/house_status.py            # table
    python3 tools/house_status.py --json     # machine-readable
    python3 tools/house_status.py --atlas PATH

The atlas is --atlas, then the HOUSE_ATLAS environment variable, then
../atlas.yaml. When none exists the tool prints one error line and exits 2.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalog_lib import ATLAS_ENV, AtlasError, read_atlas, resolve_atlas  # noqa: E402


@dataclass
class ChildState:
    name: str
    exists: bool
    is_repo: bool = False
    has_remote: bool = False
    has_upstream: bool = False
    unpushed: int = 0
    uncommitted: int = 0
    last_commit: str = ""
    error: str = ""

    @property
    def at_risk(self) -> bool:
        if self.error or not self.exists or not self.is_repo:
            return True
        return not self.has_remote or self.unpushed > 0

    @property
    def dirty(self) -> bool:
        return self.uncommitted > 0

    def verdict(self) -> str:
        if self.at_risk:
            out = "AT RISK: " + ", ".join(self.reasons())
        else:
            out = "ok"
        if self.dirty:
            out += f" (DIRTY: {self.uncommitted} uncommitted)"
        return out

    def reasons(self) -> list[str]:
        if not self.exists:
            return ["missing"]
        if self.error:
            return [self.error]
        if not self.is_repo:
            return ["not a git repository"]
        out = []
        if not self.has_remote:
            out.append("no remote")
        elif not self.has_upstream and self.unpushed:
            out.append("no upstream branch")
        if self.unpushed:
            out.append(f"{self.unpushed} unpushed")
        return out


GIT_TIMEOUT = 30


def git(path: Path, *args: str) -> tuple[int, str]:
    result = subprocess.run(["git", "-C", str(path), *args],
                            capture_output=True, text=True, timeout=GIT_TIMEOUT)
    return result.returncode, result.stdout.strip()


def inspect(name: str, path: Path) -> ChildState:
    state = ChildState(name=name, exists=path.is_dir())
    if not state.exists:
        return state
    try:
        _read_git_state(state, path)
    except subprocess.TimeoutExpired as exc:
        verb = exc.cmd[3] if isinstance(exc.cmd, list) and len(exc.cmd) > 3 else "git"
        state.error = f"git {verb} timed out after {GIT_TIMEOUT} s"
    return state


def _read_git_state(state: ChildState, path: Path) -> None:
    rc, _ = git(path, "rev-parse", "--git-dir")
    state.is_repo = rc == 0 and (path / ".git").exists()
    if not state.is_repo:
        return
    state.has_remote = bool(git(path, "remote")[1])
    rc, _ = git(path, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    state.has_upstream = rc == 0
    # With an upstream, count what it lacks. Without one, count what no
    # remote-tracking ref holds, so a fresh branch off pushed work is not
    # reported as work that exists only here.
    if state.has_remote:
        count = ["@{u}..HEAD"] if state.has_upstream else ["HEAD", "--not", "--remotes"]
        rc, out = git(path, "rev-list", "--count", *count)
        state.unpushed = int(out) if rc == 0 and out.isdigit() else 0
    state.uncommitted = len([line for line in git(path, "status", "--porcelain")[1].splitlines() if line])
    state.last_commit = git(path, "log", "-1", "--format=%cs")[1]


def load_children(atlas_path: Path) -> list[tuple[str, Path]]:
    atlas = read_atlas(atlas_path)
    base = atlas_path.parent
    return [(name, base / (entry or {}).get("path", name))
            for name, entry in (atlas.get("projects") or {}).items()]


def render(states: list[ChildState]) -> str:
    rows = [f"{'child':<18} {'last commit':<11} {'unpushed':>8} {'uncommitted':>11}  state"]
    for s in states:
        rows.append(f"{s.name:<18} {s.last_commit or '-':<11} {s.unpushed:>8} {s.uncommitted:>11}  {s.verdict()}")
    risky = sum(s.at_risk for s in states)
    dirty = sum(s.dirty for s in states)
    rows.append(f"\n{len(states)} children, {risky} at risk (work that exists only on this machine), {dirty} dirty (uncommitted files).")
    return "\n".join(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--atlas", type=Path, default=None, help=f"group atlas (default: ${ATLAS_ENV}, then ../atlas.yaml)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    atlas_path, _chosen = resolve_atlas(args.atlas)
    try:
        children = load_children(atlas_path)
    except AtlasError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    states = [inspect(name, path) for name, path in children]
    if args.json:
        print(json.dumps([asdict(s) | {"at_risk": s.at_risk, "dirty": s.dirty, "reasons": s.reasons()} for s in states], indent=2))
    else:
        print(render(states))
    return 1 if any(s.at_risk for s in states) else 0


if __name__ == "__main__":
    sys.exit(main())
