import json
import sys
import tempfile
import unittest
from pathlib import Path


WORKSHOP_DIR = Path(__file__).resolve().parent
GRID_GENOME_DIR = WORKSHOP_DIR.parents[0] / "grid_genome"
for import_path in [WORKSHOP_DIR, GRID_GENOME_DIR]:
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

from png_private_chunk_policy import (
    export_png_private_chunk_bundle,
    import_png_private_chunk,
)
from png_private_chunk_preservation_matrix import (
    SCENARIO_POLICIES,
    run_png_private_chunk_preservation_matrix_lab,
    simulate_png_editor_preservation_scenario,
    write_png_private_chunk_preservation_matrix_artifacts,
)


VALID_PROFILE_PATHS = [
    Path("data/slips/valid/slip_lcd_seed.json"),
    Path("data/slips/valid/slip_gray_stable.json"),
    Path("data/slips/valid/slip_amber_social.json"),
]
GENERATED_ROOT = Path("data/slips/multi_profile_generation_stage0")


def load_profile(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def first_grid_for(profile: dict) -> dict:
    grid_path = sorted((GENERATED_ROOT / profile["profile_id"]).glob("*.json"))[0]
    return json.loads(grid_path.read_text(encoding="utf-8"))


class PNGPrivateChunkPreservationMatrixTests(unittest.TestCase):
    def test_exact_private_chunk_preservation_remains_importable(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        bundle = export_png_private_chunk_bundle(grid, profile)

        simulated = simulate_png_editor_preservation_scenario(
            bundle["png_bytes"],
            "preserve_exact_bytes",
        )
        imported = import_png_private_chunk(simulated["png_bytes"], source_grid=grid)

        self.assertTrue(imported["ok"], imported["errors"])
        self.assertEqual(1.0, imported["semantic_fidelity"])
        self.assertEqual("private_chunk_preserved_valid", simulated["expected_outcome"])

    def test_ancillary_only_private_chunk_copy_is_rejected_by_current_hash_policy(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        bundle = export_png_private_chunk_bundle(grid, profile)

        simulated = simulate_png_editor_preservation_scenario(
            bundle["png_bytes"],
            "preserve_private_after_ancillary_append",
        )
        imported = import_png_private_chunk(simulated["png_bytes"], source_grid=grid)

        self.assertFalse(imported["ok"])
        self.assertIn("png_private_chunk_canonical_hash_mismatch", imported["error_families"])
        self.assertEqual("strict_hash_rejects_ancillary_change", simulated["expected_outcome"])

    def test_lossless_reencode_stale_copy_rejects_strip_loses_and_rebind_recovers(self):
        profile = load_profile(VALID_PROFILE_PATHS[1])
        grid = first_grid_for(profile)
        bundle = export_png_private_chunk_bundle(grid, profile)

        stale = simulate_png_editor_preservation_scenario(
            bundle["png_bytes"],
            "preserve_private_after_lossless_reencode",
        )
        stripped = simulate_png_editor_preservation_scenario(
            bundle["png_bytes"],
            "strip_private_after_lossless_reencode",
        )
        rebound = simulate_png_editor_preservation_scenario(
            bundle["png_bytes"],
            "mechagotchi_rebind_after_lossless_reencode",
        )

        stale_import = import_png_private_chunk(stale["png_bytes"], source_grid=grid)
        stripped_import = import_png_private_chunk(stripped["png_bytes"], source_grid=grid)
        rebound_import = import_png_private_chunk(rebound["png_bytes"], source_grid=grid)

        self.assertFalse(stale_import["ok"])
        self.assertIn("png_private_chunk_canonical_hash_mismatch", stale_import["error_families"])
        self.assertFalse(stripped_import["ok"])
        self.assertIn("png_private_chunk_missing", stripped_import["error_families"])
        self.assertTrue(rebound_import["ok"], rebound_import["errors"])
        self.assertEqual(1.0, rebound_import["semantic_fidelity"])
        self.assertEqual("private_chunk_rebound_valid", rebound["expected_outcome"])

    def test_lab_report_closes_simulated_private_chunk_preservation_matrix_only(self):
        report = run_png_private_chunk_preservation_matrix_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("png_private_chunk_preservation_matrix_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(len(SCENARIO_POLICIES), report["scenario_count"])
        self.assertEqual(18, report["matrix_result_count"])
        self.assertEqual(18, report["expected_outcome_match_count"])
        self.assertEqual(6, report["recoverable_import_count"])
        self.assertEqual(6, report["missing_metadata_count"])
        self.assertEqual(6, report["stale_private_chunk_rejection_count"])
        self.assertEqual(3, report["strict_ancillary_rejection_count"])
        self.assertEqual(1.0, report["metrics"]["expected_outcome_match_rate"])
        self.assertEqual(1.0, report["metrics"]["recoverable_semantic_fidelity_mean"])
        self.assertIn("png_private_chunk_editor_preservation_matrix_simulated", report["closed_states"])
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])
        self.assertIn("final_png_production_carrier_selection", report["blocked_states"])
        self.assertNotIn("private_chunk_editor_preservation_matrix", report["blocked_states"])

    def test_write_artifacts_creates_matrix_report_payload_and_rewritten_pngs(self):
        report = run_png_private_chunk_preservation_matrix_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_png_private_chunk_preservation_matrix_artifacts(output_dir, report)

            summary_path = output_dir / "png_private_chunk_preservation_matrix_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "png_private_chunk_preservation_matrix_data.js").exists())
            self.assertTrue((output_dir / "README.md").exists())
            self.assertTrue(
                (
                    output_dir
                    / "slip_lcd_seed_preserve_exact_bytes_private_chunk_matrix.png"
                ).exists()
            )


if __name__ == "__main__":
    unittest.main()
