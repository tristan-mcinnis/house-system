"""Tests for the generated system map: freshness, determinism, safety."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from catalog_lib import DEFAULT_CATALOG, DEFAULT_MAP, all_ids, load_catalog, render_system_map, scan_text  # noqa: E402


class SystemMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_catalog(DEFAULT_CATALOG)
        cls.rendered = render_system_map(cls.catalog)

    def test_committed_map_is_current(self):
        self.assertTrue(DEFAULT_MAP.exists(), "docs/system-map.md is missing; run make map")
        self.assertEqual(
            DEFAULT_MAP.read_text(encoding="utf-8"),
            self.rendered,
            msg="docs/system-map.md is stale; run make map and commit",
        )

    def test_render_is_deterministic(self):
        self.assertEqual(self.rendered, render_system_map(load_catalog(DEFAULT_CATALOG)))

    def test_map_covers_every_id(self):
        for record_id in all_ids(self.catalog):
            self.assertIn(f"`{record_id}`", self.rendered, msg=f"{record_id} missing from the map")

    def test_map_has_no_unsafe_text(self):
        self.assertEqual([], scan_text(self.rendered, "system-map"))

    def test_unbuilt_edge_is_marked_in_the_map(self):
        import copy
        catalog = copy.deepcopy(self.catalog)
        edge = catalog["relationships"][0]
        edge["status"] = "aspirational"
        rendered = render_system_map(catalog)
        self.assertIn(f"-.->|{edge['kind']}|", rendered)
        self.assertIn(f"| {edge['kind']} (aspirational) |", rendered)

    def test_relationships_render_once_with_their_endpoints(self):
        self.assertNotIn("\n## Relationships\n", self.rendered)
        edge = self.catalog["relationships"][0]
        self.assertEqual(1, self.rendered.count(f"| `{edge['id']}` |"))
        self.assertIn(f"| `{edge['id']}` | `{edge['from']}` | `{edge['to']}` |", self.rendered)

    def test_map_states_the_relationship_authority(self):
        self.assertIn("atlas.yaml", self.rendered)


if __name__ == "__main__":
    unittest.main()
