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

from png_apng_filtered_frame_data import (
    FILTER_FDAT_CASE_IDS,
    decode_apng_filtered_frame_data,
    export_apng_filtered_frame_data_cases,
    make_fdat_sequence_gap_probe,
    make_invalid_filter_probe,
    make_missing_fdat_continuation_probe,
    make_truncated_scanline_probe,
    run_apng_filtered_frame_data_lab,
    write_apng_filtered_frame_data_artifacts,
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


class APNGFilteredFrameDataTests(unittest.TestCase):
    def test_export_builds_filter_cases_with_split_fdat_expected_hashes(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        cases = export_apng_filtered_frame_data_cases(grid, profile)

        self.assertEqual(FILTER_FDAT_CASE_IDS, [case["case_id"] for case in cases])
        for case in cases:
            decoded = decode_apng_filtered_frame_data(case["png_bytes"])
            self.assertTrue(decoded["ok"])
            self.assertEqual(case["expected_display_hashes"], decoded["display_hashes"])
            self.assertEqual(case["expected_final_hash"], decoded["final_output_hash"])
            self.assertEqual(2, decoded["frames"][1]["fdat_chunk_count"])
            self.assertEqual([case["filter_type"]], decoded["frames"][1]["filter_types_seen"])
            self.assertEqual(case["expected_patch_hash"], decoded["frames"][1]["pixel_hash"])

    def test_decoder_reconstructs_all_five_png_filter_types(self):
        profile = load_profile(VALID_PROFILE_PATHS[1])
        grid = first_grid_for(profile)

        cases = export_apng_filtered_frame_data_cases(grid, profile)
        observed = {
            decode_apng_filtered_frame_data(case["png_bytes"])["frames"][1]["filter_types_seen"][0]
            for case in cases
        }

        self.assertEqual({0, 1, 2, 3, 4}, observed)

    def test_decoder_concatenates_multiple_fdat_chunks_in_sequence_order(self):
        profile = load_profile(VALID_PROFILE_PATHS[2])
        grid = first_grid_for(profile)
        case = {
            case["case_id"]: case
            for case in export_apng_filtered_frame_data_cases(grid, profile)
        }["filter_paeth_split_fdat"]

        decoded = decode_apng_filtered_frame_data(case["png_bytes"])

        self.assertTrue(decoded["ok"])
        self.assertEqual(["fcTL", "IDAT", "fcTL", "fdAT", "fdAT"], decoded["animation_chunk_order"])
        self.assertEqual([0, 1, 2, 3], decoded["sequence_numbers"])
        self.assertEqual(2, decoded["frames"][1]["fdat_chunk_count"])

    def test_decoder_rejects_invalid_filter_scanline_and_fdat_sequences(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        reference = export_apng_filtered_frame_data_cases(grid, profile)[0]

        probes = [
            (make_invalid_filter_probe(reference["png_bytes"]), "apng_filter_type_invalid"),
            (make_truncated_scanline_probe(reference["png_bytes"]), "apng_scanline_length_mismatch"),
            (make_fdat_sequence_gap_probe(reference["png_bytes"]), "apng_sequence_number_invalid"),
            (make_missing_fdat_continuation_probe(reference["png_bytes"]), "apng_frame_decompression_failed"),
        ]

        for png_bytes, family in probes:
            decoded = decode_apng_filtered_frame_data(png_bytes)
            self.assertFalse(decoded["ok"])
            self.assertIn(family, decoded["error_families"])

    def test_lab_report_closes_filtered_fdat_subset_without_full_conformance_claim(self):
        report = run_apng_filtered_frame_data_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("apng_filtered_frame_data_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(15, report["case_count"])
        self.assertEqual(15, report["case_success_count"])
        self.assertEqual(4, report["invalid_probe_count"])
        self.assertEqual(4, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["case_success_rate"])
        self.assertEqual(5, report["metrics"]["filter_family_count"])
        self.assertIn("apng_filter_method_0_frame_reconstruction", report["closed_states"])
        self.assertIn("apng_split_fdat_frame_data_reconstruction", report["closed_states"])
        self.assertIn("full_apng_png_conformance", report["blocked_states"])
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])

    def test_write_artifacts_creates_apngs_report_and_app_payload(self):
        report = run_apng_filtered_frame_data_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_apng_filtered_frame_data_artifacts(output_dir, report)

            summary_path = output_dir / "apng_filtered_frame_data_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "cases" / "slip_lcd_seed_filter_none_split_fdat.png").exists())
            self.assertTrue((output_dir / "cases" / "slip_lcd_seed_filter_paeth_split_fdat.png").exists())
            app_data = (output_dir / "apng_filtered_frame_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_APNG_FILTERED_FRAME_DATA", app_data)


if __name__ == "__main__":
    unittest.main()
