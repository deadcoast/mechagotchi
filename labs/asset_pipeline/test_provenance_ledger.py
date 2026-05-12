import json
import tempfile
import unittest
from pathlib import Path

from provenance_ledger import (
    build_stage0_ledger,
    generate_attribution_manifest,
    hash_included_path,
    validate_ledger,
    write_stage0_artifacts,
)


class ProvenanceLedgerTests(unittest.TestCase):
    def test_hash_included_path_is_stable_for_files_and_directories(self):
        file_hash = hash_included_path(Path("data/workshop_editor/workshop_export_stage0.json"))
        directory_hash = hash_included_path(Path("data/seed_grids"))

        self.assertEqual("sha256", file_hash["hash_algorithm"])
        self.assertEqual(64, len(file_hash["hash"]))
        self.assertEqual("sha256-tree", directory_hash["hash_algorithm"])
        self.assertEqual(64, len(directory_hash["hash"]))

    def test_build_stage0_ledger_contains_included_and_reference_only_entries(self):
        ledger = build_stage0_ledger(Path("."))
        asset_ids = {entry["asset_id"] for entry in ledger["assets"]}

        self.assertIn("internal_seed_grid_corpus_v1", asset_ids)
        self.assertIn("workshop_editor_stage0_export", asset_ids)
        self.assertIn("piskel_reference_only", asset_ids)
        self.assertIn("libresprite_reference_only", asset_ids)

    def test_validate_ledger_accepts_stage0_entries(self):
        ledger = build_stage0_ledger(Path("."))
        result = validate_ledger(ledger, Path("."))

        self.assertTrue(result["ok"], result["errors"])
        self.assertGreaterEqual(result["summary"]["included_count"], 3)
        self.assertGreaterEqual(result["summary"]["reference_only_count"], 3)

    def test_validate_ledger_rejects_missing_hash_for_included_asset(self):
        ledger = build_stage0_ledger(Path("."))
        ledger["assets"][0]["hash"] = ""

        result = validate_ledger(ledger, Path("."))

        self.assertFalse(result["ok"])
        self.assertIn("included asset missing hash", "\n".join(result["errors"]))

    def test_validate_ledger_rejects_core_share_alike_without_review(self):
        ledger = build_stage0_ledger(Path("."))
        ledger["assets"].append(
            {
                "asset_id": "bad_share_alike_core",
                "title": "Bad Share Alike Core Asset",
                "asset_type": "sprite",
                "creator": "External Creator",
                "source": "external",
                "source_url": "https://example.invalid/asset",
                "download_date": "2026-05-12",
                "license": "Creative Commons Attribution-ShareAlike 4.0 International",
                "spdx_id": "CC-BY-SA-4.0",
                "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
                "derivative_of": "",
                "modifications": "none",
                "hash_algorithm": "sha256",
                "hash": "a" * 64,
                "included_in_repo": True,
                "included_path": "data/seed_grids/README.md",
                "shipping_scope": "core",
                "commercial_allowed": True,
                "redistribution_allowed": True,
                "share_alike_required": True,
                "attribution_required": True,
                "attribution_text": "Bad Share Alike Core Asset by External Creator",
                "review_status": "approved",
                "reviewer": "research_lead",
                "notes": "intentional test fixture",
            }
        )

        result = validate_ledger(ledger, Path("."))

        self.assertFalse(result["ok"])
        self.assertIn("share-alike asset cannot be core", "\n".join(result["errors"]))

    def test_generate_attribution_manifest_includes_only_required_attribution(self):
        ledger = build_stage0_ledger(Path("."))
        manifest = generate_attribution_manifest(ledger)

        self.assertEqual("0.1.0", manifest["manifest_version"])
        self.assertTrue(
            all(entry["attribution_text"] for entry in manifest["attributions"])
        )
        self.assertNotIn(
            "internal_seed_grid_corpus_v1",
            {entry["asset_id"] for entry in manifest["attributions"]},
        )

    def test_write_stage0_artifacts_creates_ledger_validation_and_attribution(self):
        ledger = build_stage0_ledger(Path("."))
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_stage0_artifacts(output_dir, ledger, Path("."))

            self.assertTrue((output_dir / "ledger.json").exists())
            self.assertTrue((output_dir / "validation_report.json").exists())
            self.assertTrue((output_dir / "attribution_manifest.json").exists())
            validation = json.loads(
                (output_dir / "validation_report.json").read_text(encoding="utf-8")
            )
            self.assertTrue(validation["ok"], validation["errors"])


if __name__ == "__main__":
    unittest.main()
