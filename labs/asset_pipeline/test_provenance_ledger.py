import json
import tempfile
import unittest
from pathlib import Path

from provenance_ledger import (
    build_stage0_ledger,
    build_provenance_ci_report,
    generate_attribution_manifest,
    hash_included_path,
    parse_spdx_expression,
    validate_ledger,
    write_stage0_artifacts,
)


ROOT = Path(__file__).resolve().parents[2]


class ProvenanceLedgerTests(unittest.TestCase):
    def test_hash_included_path_is_stable_for_files_and_directories(self):
        file_hash = hash_included_path(ROOT / "data/workshop_editor/workshop_export_stage0.json")
        directory_hash = hash_included_path(ROOT / "data/seed_grids")

        self.assertEqual("sha256", file_hash["hash_algorithm"])
        self.assertEqual(64, len(file_hash["hash"]))
        self.assertEqual("sha256-tree", directory_hash["hash_algorithm"])
        self.assertEqual(64, len(directory_hash["hash"]))

    def test_build_stage0_ledger_contains_included_and_reference_only_entries(self):
        ledger = build_stage0_ledger(ROOT)
        asset_ids = {entry["asset_id"] for entry in ledger["assets"]}

        self.assertIn("internal_seed_grid_corpus_v1", asset_ids)
        self.assertIn("workshop_editor_stage0_export", asset_ids)
        self.assertIn("piskel_reference_only", asset_ids)
        self.assertIn("libresprite_reference_only", asset_ids)

    def test_validate_ledger_accepts_stage0_entries(self):
        ledger = build_stage0_ledger(ROOT)
        result = validate_ledger(ledger, ROOT)

        self.assertTrue(result["ok"], result["errors"])
        self.assertGreaterEqual(result["summary"]["included_count"], 3)
        self.assertGreaterEqual(result["summary"]["reference_only_count"], 3)

    def test_parse_spdx_expression_accepts_compound_operators_and_refs(self):
        parsed = parse_spdx_expression(
            "(MIT OR Apache-2.0) AND "
            "(GPL-2.0-or-later WITH Autoconf-exception-3.0) AND "
            "LicenseRef-Mechagotchi-Internal-Research"
        )

        self.assertTrue(parsed["ok"], parsed["errors"])
        self.assertEqual(
            [
                "Apache-2.0",
                "GPL-2.0-or-later",
                "LicenseRef-Mechagotchi-Internal-Research",
                "MIT",
            ],
            parsed["license_ids"],
        )
        self.assertEqual(["Autoconf-exception-3.0"], parsed["exception_ids"])
        self.assertEqual(["AND", "OR", "WITH"], parsed["operators"])
        self.assertTrue(parsed["contains_copyleft"])

    def test_parse_spdx_expression_rejects_lowercase_operators(self):
        parsed = parse_spdx_expression("MIT or Apache-2.0")

        self.assertFalse(parsed["ok"])
        self.assertIn("unexpected token", "\n".join(parsed["errors"]))

    def test_validate_ledger_rejects_missing_hash_for_included_asset(self):
        ledger = build_stage0_ledger(ROOT)
        ledger["assets"][0]["hash"] = ""

        result = validate_ledger(ledger, ROOT)

        self.assertFalse(result["ok"])
        self.assertIn("included asset missing hash", "\n".join(result["errors"]))

    def test_validate_ledger_rejects_core_share_alike_without_review(self):
        ledger = build_stage0_ledger(ROOT)
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
                "spdx_expression": "CC-BY-SA-4.0",
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
                "decision_record": "",
                "notes": "intentional test fixture",
            }
        )

        result = validate_ledger(ledger, ROOT)

        self.assertFalse(result["ok"])
        joined_errors = "\n".join(result["errors"])
        self.assertIn("share-alike asset cannot be core", joined_errors)
        self.assertIn("share-alike or copyleft asset requires decision_record", joined_errors)

    def test_validate_ledger_rejects_unknown_license_inside_expression(self):
        ledger = build_stage0_ledger(ROOT)
        ledger["assets"][3]["spdx_expression"] = "MIT OR MadeUp-1.0"

        result = validate_ledger(ledger, ROOT)

        self.assertFalse(result["ok"])
        self.assertIn("unknown SPDX license identifier MadeUp-1.0", "\n".join(result["errors"]))

    def test_build_provenance_ci_report_summarizes_expression_and_gate_status(self):
        ledger = build_stage0_ledger(ROOT)
        report = build_provenance_ci_report(ledger, ROOT)

        self.assertTrue(report["ok"], report["errors"])
        self.assertTrue(report["checks"]["ledger_validation_ok"])
        self.assertTrue(report["checks"]["spdx_expressions_ok"])
        self.assertEqual(len(ledger["assets"]), report["spdx_summary"]["expression_count"])
        self.assertIn("LicenseRef-Mechagotchi-Internal-Research", report["spdx_summary"]["license_ids"])

    def test_generate_attribution_manifest_includes_only_required_attribution(self):
        ledger = build_stage0_ledger(ROOT)
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
        ledger = build_stage0_ledger(ROOT)
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_stage0_artifacts(output_dir, ledger, ROOT)

            self.assertTrue((output_dir / "ledger.json").exists())
            self.assertTrue((output_dir / "validation_report.json").exists())
            self.assertTrue((output_dir / "attribution_manifest.json").exists())
            self.assertTrue((output_dir / "provenance_ci_report.json").exists())
            validation = json.loads(
                (output_dir / "validation_report.json").read_text(encoding="utf-8")
            )
            self.assertTrue(validation["ok"], validation["errors"])
            ci_report = json.loads(
                (output_dir / "provenance_ci_report.json").read_text(encoding="utf-8")
            )
            self.assertTrue(ci_report["ok"], ci_report["errors"])


if __name__ == "__main__":
    unittest.main()
