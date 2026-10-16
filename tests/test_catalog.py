"""Validation tests for the House System catalog."""

from __future__ import annotations

import contextlib
import copy
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from catalog_lib import (  # noqa: E402
    ATLAS_ENV,
    DEFAULT_ATLAS,
    DEFAULT_CATALOG,
    AtlasError,
    load_catalog,
    read_atlas,
    resolve_atlas,
    scan_text,
    validate,
)

# The live atlas is in the non-git group folder, so tests use a committed copy.
FIXTURE_ATLAS = ROOT / "tests" / "fixtures" / "atlas.yaml"


class CatalogValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.path = DEFAULT_CATALOG
        cls.text = cls.path.read_text(encoding="utf-8")
        cls.catalog = load_catalog(cls.path)

    def result(self, catalog=None, text=None):
        return validate(catalog or self.catalog, text or self.text, atlas_path=FIXTURE_ATLAS)

    def test_catalog_is_clean(self):
        result = self.result()
        self.assertEqual([], result["errors"], msg="\n".join(result["errors"]))
        self.assertEqual([], result["warnings"], msg="\n".join(result["warnings"]))

    def test_every_collection_is_populated(self):
        for name in ("surfaces", "shared_interaction", "orchestration", "connectors", "organs", "sources", "relationships"):
            self.assertTrue(self.catalog.get(name), msg=f"{name} is empty")
        for name in ("tools", "skills", "extensions", "hooks", "workflows", "policies"):
            self.assertTrue(self.catalog["execution_fabric"].get(name), msg=f"execution_fabric.{name} is empty")

    def test_duplicate_id_is_an_error(self):
        broken = copy.deepcopy(self.catalog)
        broken["surfaces"][1]["id"] = broken["surfaces"][0]["id"]
        errors = self.result(broken)["errors"]
        self.assertTrue(any("duplicate id" in e for e in errors), errors)

    def test_unknown_reference_is_an_error(self):
        broken = copy.deepcopy(self.catalog)
        broken["surfaces"][0]["uses"] = ["no-such-organ"]
        errors = self.result(broken)["errors"]
        self.assertTrue(any("references unknown id" in e for e in errors), errors)

    def test_bad_status_is_an_error(self):
        broken = copy.deepcopy(self.catalog)
        broken["surfaces"][0]["status"] = "finished"
        errors = self.result(broken)["errors"]
        self.assertTrue(any("status" in e for e in errors), errors)

    def test_duplicate_authority_is_an_error(self):
        broken = copy.deepcopy(self.catalog)
        broken["sources"][1]["authority"] = broken["sources"][0]["authority"]
        errors = self.result(broken)["errors"]
        self.assertTrue(any("already claimed" in e for e in errors), errors)

    def test_missing_required_field_is_an_error(self):
        broken = copy.deepcopy(self.catalog)
        del broken["surfaces"][0]["description"]
        errors = self.result(broken)["errors"]
        self.assertTrue(any("missing required field description" in e for e in errors), errors)

    def test_public_candidate_requires_private(self):
        broken = copy.deepcopy(self.catalog)
        broken["surfaces"][2]["visibility"] = "public"
        errors = self.result(broken)["errors"]
        self.assertTrue(any("public_candidate" in e for e in errors), errors)

    def test_relationship_status_is_optional_and_checked(self):
        edge = copy.deepcopy(self.catalog)
        edge["relationships"][0]["status"] = "aspirational"
        result = self.result(edge)
        self.assertEqual([], result["errors"] + result["warnings"])
        edge["relationships"][0]["status"] = "pending"
        errors = self.result(edge)["errors"]
        self.assertTrue(any("status 'pending'" in e for e in errors), errors)

    def test_catalog_repo_slugs_match_atlas(self):
        # The validator already cross-checks; this test asserts the check ran.
        notes = self.result()["notes"]
        self.assertTrue(any("atlas cross-check" in n for n in notes), notes)


class AtlasResolutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_flag_beats_env_beats_default(self):
        with mock.patch.dict(os.environ, {ATLAS_ENV: "/from/env.yaml"}):
            self.assertEqual(resolve_atlas("/from/flag.yaml"), (Path("/from/flag.yaml"), True))
            self.assertEqual(resolve_atlas(None), (Path("/from/env.yaml"), True))
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(ATLAS_ENV, None)
            self.assertEqual(resolve_atlas(None), (DEFAULT_ATLAS, False))

    def test_fixture_covers_every_catalog_project_slug(self):
        result = validate(load_catalog(DEFAULT_CATALOG), DEFAULT_CATALOG.read_text(encoding="utf-8"), atlas_path=FIXTURE_ATLAS)
        self.assertEqual([], result["errors"])
        self.assertTrue(any("atlas cross-check" in n for n in result["notes"]), result["notes"])

    def test_missing_atlas_is_a_one_line_error(self):
        with self.assertRaises(AtlasError) as ctx:
            read_atlas(self.base / "nope.yaml")
        self.assertNotIn("\n", str(ctx.exception))
        self.assertIn("nope.yaml", str(ctx.exception))

    def test_unreadable_atlas_is_a_one_line_error(self):
        bad = self.base / "bad.yaml"
        bad.write_text("projects: [unclosed\n  - x: : :\n", encoding="utf-8")
        with self.assertRaises(AtlasError) as ctx:
            read_atlas(bad)
        self.assertNotIn("\n", str(ctx.exception))
        listy = self.base / "list.yaml"
        listy.write_text("- a\n- b\n", encoding="utf-8")
        with self.assertRaises(AtlasError):
            read_atlas(listy)

    def test_absent_default_atlas_is_a_warning_not_an_error(self):
        result = validate(load_catalog(DEFAULT_CATALOG), atlas_path=self.base / "absent.yaml")
        self.assertEqual([], result["errors"])
        self.assertTrue(any("atlas not found" in w for w in result["warnings"]), result["warnings"])

    def test_validate_cli_chosen_atlas_missing_is_an_error(self):
        import validate_catalog
        out = io.StringIO()
        with mock.patch.dict(os.environ, {ATLAS_ENV: str(self.base / "absent.yaml")}), contextlib.redirect_stdout(out):
            code = validate_catalog.main([])
        self.assertEqual(code, 1)
        self.assertEqual(out.getvalue().strip().count("\n"), 0)
        self.assertIn("atlas not found", out.getvalue())

    def test_validate_cli_uses_env_atlas(self):
        import validate_catalog
        out = io.StringIO()
        with mock.patch.dict(os.environ, {ATLAS_ENV: str(FIXTURE_ATLAS)}), contextlib.redirect_stdout(out):
            code = validate_catalog.main([])
        self.assertEqual(code, 0, out.getvalue())
        self.assertIn("atlas cross-check", out.getvalue())


class SafetyScanTests(unittest.TestCase):
    def test_absolute_home_path_is_caught(self):
        self.assertTrue(scan_text("lives at /" + "Users/someone/Documents", "t"))

    def test_email_is_caught(self):
        self.assertTrue(scan_text("write to person@example.com", "t"))

    def test_token_shapes_are_caught(self):
        for sample in ("sk-" + "abcdefghijklmnopqrstuvwxyz", "gh" + "p_" + "0123456789" * 3 + "012345", "AK" + "IAIOSFODNN7EXAMPLE"):
            self.assertTrue(scan_text(sample, "t"), sample)

    def test_normal_prose_passes(self):
        prose = "The local model daemon serves completion and vision requests over localhost."
        self.assertEqual([], scan_text(prose, "t"))

    def test_committed_catalog_passes_safety_scan(self):
        text = DEFAULT_CATALOG.read_text(encoding="utf-8")
        self.assertEqual([], scan_text(text, "catalog"))


if __name__ == "__main__":
    unittest.main()
