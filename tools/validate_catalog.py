#!/usr/bin/env python3
"""Validate the House System catalog. Exit code 0 when clean, 1 on error.

Usage:
    python3 tools/validate_catalog.py [--catalog PATH] [--atlas PATH] [--quiet]

Checks (deterministic, no network, no writes):
  - catalog shape: schema version, scope, authority, every collection present
  - every record has its required fields, a valid status and a valid visibility
  - ids are globally unique
  - every cross-reference resolves to a real id
  - exactly one owner claims each source-of-truth authority
  - no absolute home path, email address or credential shape anywhere in the file
  - every project slug exists in the group atlas (--atlas, then HOUSE_ATLAS, then
    ../atlas.yaml). The default file may be absent on a fresh clone: that is a
    warning. A path you chose that is absent is an error.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_lib import ATLAS_ENV, DEFAULT_CATALOG, load_catalog, resolve_atlas, validate  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the House System catalog.")
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG))
    parser.add_argument("--atlas", default=None, help=f"group atlas (default: ${ATLAS_ENV}, then ../atlas.yaml)")
    parser.add_argument("--quiet", action="store_true", help="print only the verdict")
    args = parser.parse_args(argv)

    catalog_path = Path(args.catalog)
    if not catalog_path.exists():
        print(f"error: catalog not found: {catalog_path}")
        return 1

    catalog = load_catalog(catalog_path)
    text = catalog_path.read_text(encoding="utf-8")
    atlas_path, chosen = resolve_atlas(args.atlas)
    if chosen and not atlas_path.is_file():
        print(f"error: atlas not found: {atlas_path}")
        return 1
    result = validate(catalog, text, atlas_path=atlas_path)

    if not args.quiet:
        for note in result["notes"]:
            print(f"note: {note}")
        for warning in result["warnings"]:
            print(f"warning: {warning}")
    for error in result["errors"]:
        print(f"error: {error}")

    if result["errors"]:
        print(f"FAIL: {len(result['errors'])} error(s)")
        return 1
    print(f"OK: catalog valid ({len(result['warnings'])} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
