import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


WORKSHOP_DIR = Path(__file__).resolve().parent
GRID_GENOME_DIR = WORKSHOP_DIR.parents[0] / "grid_genome"
for import_path in [WORKSHOP_DIR, GRID_GENOME_DIR]:
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

from png_apng_chunk_order_conformance import (
    CONFORMANCE_CASE_IDS,
    duplicate_ihdr,
    export_png_apng_chunk_order_conformance_cases,
    insert_chunk_after_iend,
    insert_text_between_idats,
    move_actl_after_idat,
    move_plte_after_idat,
    move_trns_before_plte,
    rewrite_first_fctl_sequence,
    run_png_apng_chunk_order_conformance_lab,
    validate_png_apng_chunk_order,
    write_png_apng_chunk_order_conformance_artifacts,
)


VALID_PROFILE_PATHS = [
    ROOT / "data/slips/valid/slip_lcd_seed.json",
    ROOT / "data/slips/valid/slip_gray_stable.json",
    ROOT / "data/slips/valid/slip_amber_social.json",
]
GENERATED_ROOT = ROOT / "data/slips/multi_profile_generation_stage0"


def load_profile(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def first_grid_for(profile: dict) -> dict:
    grid_path = sorted((GENERATED_ROOT / profile["profile_id"]).glob("*.json"))[0]
    return json.loads(grid_path.read_text(encoding="utf-8"))


class PNGAPNGChunkOrderConformanceTests(unittest.TestCase):
    def test_export_builds_static_indexed_split_idat_and_apng_conformance_cases(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        cases = export_png_apng_chunk_order_conformance_cases(grid, profile)
        case_ids = [case["case_id"] for case in cases]

        self.assertEqual(CONFORMANCE_CASE_IDS, case_ids)
        for case in cases:
            validation = validate_png_apng_chunk_order(
                case["png_bytes"],
                expected_animation=case["expected_animation"],
            )
            self.assertTrue(validation["ok"], validation["errors"])
            self.assertEqual(case["case_id"], validation["case_id"])
            self.assertIn("IHDR", validation["chunks"])
            self.assertIn("IDAT", validation["chunks"])
            self.assertEqual("IEND", validation["chunks"][-1])

    def test_static_validation_rejects_png_chunk_order_and_cardinality_violations(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        cases = {
            case["case_id"]: case
            for case in export_png_apng_chunk_order_conformance_cases(grid, profile)
        }

        probes = [
            (
                duplicate_ihdr(cases["static_rgba_single_idat"]["png_bytes"]),
                "png_ihdr_duplicate",
            ),
            (
                insert_chunk_after_iend(cases["static_rgba_single_idat"]["png_bytes"]),
                "png_iend_not_last",
            ),
            (
                move_plte_after_idat(cases["indexed_plte_trns"]["png_bytes"]),
                "png_plte_after_idat",
            ),
            (
                move_trns_before_plte(cases["indexed_plte_trns"]["png_bytes"]),
                "png_trns_before_plte",
            ),
            (
                insert_text_between_idats(cases["rgba_split_idat"]["png_bytes"]),
                "png_idat_not_consecutive",
            ),
        ]

        for png_bytes, family in probes:
            validation = validate_png_apng_chunk_order(png_bytes)
            self.assertFalse(validation["ok"])
            self.assertIn(family, validation["error_families"])

    def test_apng_validation_rejects_control_order_and_sequence_violations(self):
        profile = load_profile(VALID_PROFILE_PATHS[1])
        grid = first_grid_for(profile)
        cases = {
            case["case_id"]: case
            for case in export_png_apng_chunk_order_conformance_cases(grid, profile)
        }
        apng_bytes = cases["apng_static_first_frame"]["png_bytes"]

        probes = [
            (
                move_actl_after_idat(apng_bytes),
                "apng_actl_after_idat",
            ),
            (
                rewrite_first_fctl_sequence(apng_bytes, sequence_number=3),
                "apng_sequence_number_gap",
            ),
        ]

        for png_bytes, family in probes:
            validation = validate_png_apng_chunk_order(
                png_bytes,
                expected_animation=True,
            )
            self.assertFalse(validation["ok"])
            self.assertIn(family, validation["error_families"])

    def test_lab_report_closes_chunk_order_matrix_without_full_conformance_claim(self):
        report = run_png_apng_chunk_order_conformance_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("png_apng_chunk_order_conformance_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(12, report["conformance_case_count"])
        self.assertEqual(12, report["conformance_case_success_count"])
        self.assertEqual(7, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["conformance_case_success_rate"])
        self.assertIn("png_critical_chunk_order_matrix", report["closed_states"])
        self.assertIn("apng_control_chunk_order_matrix", report["closed_states"])
        self.assertIn("full_apng_png_conformance", report["blocked_states"])
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])
        self.assertIn("production_import_export_carrier_selection_final_decision", report["blocked_states"])

    def test_write_artifacts_creates_case_files_report_and_app_payload(self):
        report = run_png_apng_chunk_order_conformance_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_png_apng_chunk_order_conformance_artifacts(output_dir, report)

            summary_path = output_dir / "png_apng_chunk_order_conformance_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "README.md").exists())
            self.assertTrue((output_dir / "cases" / "slip_lcd_seed_static_rgba_single_idat.png").exists())
            self.assertTrue((output_dir / "cases" / "slip_lcd_seed_apng_static_first_frame.png").exists())
            app_data = (output_dir / "png_apng_chunk_order_conformance_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_PNG_APNG_CHUNK_ORDER_CONFORMANCE", app_data)


if __name__ == "__main__":
    unittest.main()
