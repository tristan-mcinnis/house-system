#!/usr/bin/env python3
"""Generate docs/system-map.md from the House System catalog.

Usage:
    python3 tools/build_system_map.py [--catalog PATH] [--out PATH] [--check]

The output is deterministic: no timestamps, no set iteration, order follows the
catalog file. `--check` renders in memory and compares against the file on disk,
exiting 1 if it is stale or if the rendered text trips a safety pattern.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_lib import DEFAULT_CATALOG, DEFAULT_MAP, load_catalog, render_system_map, scan_text  # noqa: E402


def build(catalog_path: Path) -> str:
    catalog = load_catalog(catalog_path)
    rendered = render_system_map(catalog)
    findings = scan_text(rendered, "system-map")
    if findings:
        raise SystemExit("refusing to emit unsafe output:\n" + "\n".join(findings))
    return rendered


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the House System map.")
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG))
    parser.add_argument("--out", default=str(DEFAULT_MAP))
    parser.add_argument("--check", action="store_true", help="fail if the committed map is stale")
    args = parser.parse_args(argv)

    rendered = build(Path(args.catalog))
    out = Path(args.out)

    if args.check:
        if not out.exists():
            print(f"FAIL: {out} does not exist; run make map")
            return 1
        current = out.read_text(encoding="utf-8")
        if current != rendered:
            print(f"FAIL: {out} is stale; run make map")
            return 1
        print(f"OK: {out} is current")
        return 0

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(rendered, encoding="utf-8")
    print(f"wrote {out} ({len(rendered.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
