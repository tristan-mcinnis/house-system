"""Tests for house_status: at-risk detection on real temporary Git repositories."""

from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import house_status  # noqa: E402
from house_status import inspect, load_children, main  # noqa: E402


def run(cwd: Path, *args: str) -> None:
    subprocess.run(args, cwd=cwd, check=True, capture_output=True)


def commit(repo: Path, name: str) -> None:
    (repo / name).write_text(name, encoding="utf-8")
    run(repo, "git", "add", name)
    run(repo, "git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-qm", name)


class HouseStatusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.origin = self.base / "origin.git"
        run(self.base, "git", "init", "-q", "--bare", "-b", "main", str(self.origin))

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def repo(self, name: str, remote: bool = True) -> Path:
        path = self.base / name
        path.mkdir()
        run(path, "git", "init", "-q", "-b", "main")
        commit(path, "first")
        if remote:
            run(path, "git", "remote", "add", "origin", str(self.origin))
            run(path, "git", "push", "-q", "-u", "origin", "main")
        return path

    def test_pushed_clean_repo_is_ok(self):
        state = inspect("a", self.repo("a"))
        self.assertFalse(state.at_risk)
        self.assertEqual(state.unpushed, 0)

    def test_unpushed_commit_is_at_risk(self):
        path = self.repo("b")
        commit(path, "second")
        state = inspect("b", path)
        self.assertTrue(state.at_risk)
        self.assertEqual(state.unpushed, 1)
        self.assertIn("1 unpushed", state.reasons())

    def test_no_remote_is_at_risk(self):
        state = inspect("c", self.repo("c", remote=False))
        self.assertTrue(state.at_risk)
        self.assertEqual(state.reasons(), ["no remote"])

    def test_uncommitted_alone_is_not_at_risk(self):
        path = self.repo("d")
        (path / "draft.txt").write_text("wip", encoding="utf-8")
        state = inspect("d", path)
        self.assertFalse(state.at_risk)
        self.assertEqual(state.uncommitted, 1)

    def test_new_local_branch_with_pushed_commits_is_ok(self):
        # A fresh work branch has no upstream yet, but every commit on it is
        # already on the remote, so nothing exists only on this machine.
        path = self.repo("e")
        run(path, "git", "switch", "-q", "-c", "work")
        state = inspect("e", path)
        self.assertFalse(state.has_upstream)
        self.assertFalse(state.at_risk, state.reasons())

    def test_new_local_branch_with_local_commits_is_at_risk(self):
        path = self.repo("f")
        run(path, "git", "switch", "-q", "-c", "work")
        commit(path, "second")
        state = inspect("f", path)
        self.assertTrue(state.at_risk)
        self.assertEqual(state.unpushed, 1)
        self.assertEqual(state.reasons(), ["no upstream branch", "1 unpushed"])

    def test_dirty_tree_is_reported_not_plain_ok(self):
        path = self.repo("dirty")
        state = inspect("dirty", path)
        self.assertFalse(state.dirty)
        self.assertEqual(state.verdict(), "ok")
        (path / "wip.txt").write_text("wip", encoding="utf-8")
        (path / "wip2.txt").write_text("wip", encoding="utf-8")
        state = inspect("dirty", path)
        self.assertTrue(state.dirty)
        self.assertFalse(state.at_risk)
        self.assertEqual(state.verdict(), "ok (DIRTY: 2 uncommitted)")
        self.assertIn("DIRTY: 2 uncommitted", house_status.render([state]))
        self.assertIn("1 dirty", house_status.render([state]))

    def test_at_risk_and_dirty_show_both(self):
        path = self.repo("both", remote=False)
        (path / "wip.txt").write_text("wip", encoding="utf-8")
        verdict = inspect("both", path).verdict()
        self.assertEqual(verdict, "AT RISK: no remote (DIRTY: 1 uncommitted)")

    def test_json_carries_dirty(self):
        path = self.repo("j")
        (path / "wip.txt").write_text("wip", encoding="utf-8")
        atlas = self.base / "atlas.yaml"
        atlas.write_text("projects:\n  j:\n    path: j\n", encoding="utf-8")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(main(["--atlas", str(atlas), "--json"]), 0)
        self.assertIs(json.loads(out.getvalue())[0]["dirty"], True)

    def test_missing_atlas_is_one_error_line_not_a_traceback(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = main(["--atlas", str(self.base / "absent.yaml")])
        self.assertEqual(code, 2)
        self.assertEqual(err.getvalue().strip().count("\n"), 0)
        self.assertTrue(err.getvalue().startswith("error: atlas not found"))
        self.assertNotIn("Traceback", err.getvalue())

    def test_env_atlas_is_used_and_missing_env_atlas_is_an_error(self):
        self.repo("ok")
        atlas = self.base / "atlas.yaml"
        atlas.write_text("projects:\n  ok:\n    path: ok\n", encoding="utf-8")
        with mock.patch.dict(os.environ, {"HOUSE_ATLAS": str(atlas)}), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--json"]), 0)
        err = io.StringIO()
        with mock.patch.dict(os.environ, {"HOUSE_ATLAS": str(self.base / "absent.yaml")}), contextlib.redirect_stderr(err):
            self.assertEqual(main([]), 2)
        self.assertIn("atlas not found", err.getvalue())

    def test_missing_child_is_at_risk(self):
        state = inspect("gone", self.base / "gone")
        self.assertTrue(state.at_risk)
        self.assertEqual(state.reasons(), ["missing"])

    def test_git_timeout_is_reported_not_raised(self):
        # A hung git call (a locked index, a stalled filesystem) must not stop
        # the whole report, and must not pass as ok.
        path = self.repo("slow")
        real_run = subprocess.run

        def hang_on_status(cmd, *args, **kwargs):
            if "status" in cmd:
                raise subprocess.TimeoutExpired(cmd, kwargs.get("timeout"))
            return real_run(cmd, *args, **kwargs)

        with mock.patch.object(house_status.subprocess, "run", side_effect=hang_on_status):
            state = inspect("slow", path)
        self.assertTrue(state.at_risk)
        self.assertEqual(state.reasons(), ["git status timed out after 30 s"])

    def test_atlas_drives_children_and_exit_status(self):
        self.repo("ok")
        atlas = self.base / "atlas.yaml"
        atlas.write_text("projects:\n  ok:\n    path: ok\n", encoding="utf-8")
        self.assertEqual([name for name, _ in load_children(atlas)], ["ok"])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--atlas", str(atlas), "--json"]), 0)
        atlas.write_text("projects:\n  ok:\n    path: ok\n  gone:\n    path: gone\n", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--atlas", str(atlas), "--json"]), 1)


if __name__ == "__main__":
    unittest.main()
