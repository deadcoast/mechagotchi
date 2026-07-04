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

from png_apng_bit_depth_frame_data import (
    BIT_DEPTH_FRAME_CASE_IDS,
    decode_apng_bit_depth_frame_data,
    export_apng_bit_depth_frame_data_cases,
    make_invalid_bit_depth_color_type_probe,
    make_invalid_filter_probe,
    make_sequence_gap_probe,
    make_truncated_scanline_probe,
    run_apng_bit_depth_frame_data_lab,
    write_apng_bit_depth_frame_data_artifacts,
)


VALID_PROFILE_PATHS = [
    ROOT / "data/slips/valid/slip_lcd_seed.json",
    ROOT / "data/slips/valid/slip_gray_stable.json",
    ROOT / "data/slips/valid/slip_amber_social.json",
]
GENERATED_ROOT = ROOT / "data/slips/multi_profile_generation_stage0"
EXPECTED_CASE_IDS = [
    "grayscale1_fdat",
    "grayscale2_fdat",
    "grayscale4_fdat",
    "grayscale16_fdat",
    "indexed1_fdat",
    "indexed2_fdat",
    "indexed4_fdat",
    "truecolor16_fdat",
    "grayscale_alpha16_fdat",
    "truecolor_alpha16_fdat",
]


def load_profile(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def first_grid_for(profile: dict) -> dict:
    grid_path = sorted((GENERATED_ROOT / profile["profile_id"]).glob("*.json"))[0]
    return json.loads(grid_path.read_text(encoding="utf-8"))


def expected_scanline_bytes(width: int, color_type: int, bit_depth: int) -> int:
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color_type]
    return (width * channels * bit_depth + 7) // 8


class APNGBitDepthFrameDataTests(unittest.TestCase):
    def test_export_builds_low_bit_and_16bit_apng_cases(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        cases = export_apng_bit_depth_frame_data_cases(grid, profile)

        self.assertEqual(EXPECTED_CASE_IDS, BIT_DEPTH_FRAME_CASE_IDS)
        self.assertEqual(BIT_DEPTH_FRAME_CASE_IDS, [case["case_id"] for case in cases])
        self.assertEqual({1, 2, 4, 16}, {case["bit_depth"] for case in cases})
        self.assertEqual({0, 2, 3, 4, 6}, {case["color_type"] for case in cases})
        for case in cases:
            decoded = decode_apng_bit_depth_frame_data(case["png_bytes"])
            self.assertTrue(decoded["ok"], decoded["errors"])
            self.assertEqual(case["expected_frame_hashes"], decoded["frame_pixel_hashes"])
            self.assertEqual(case["expected_display_hashes"], decoded["display_hashes"])
            self.assertEqual(case["expected_final_hash"], decoded["final_output_hash"])
            self.assertEqual(case["bit_depth"], decoded["bit_depth"])
            self.assertEqual(case["color_type"], decoded["color_type"])
            self.assertEqual(2, decoded["frame_count"])
            self.assertEqual(2, decoded["frames"][1]["fdat_chunk_count"])

    def test_decoder_restores_packed_scanlines_and_16bit_samples(self):
        profile = load_profile(VALID_PROFILE_PATHS[1])
        grid = first_grid_for(profile)
        width = grid["grid_size"][0]
        cases = {
            case["case_id"]: case
            for case in export_apng_bit_depth_frame_data_cases(grid, profile)
        }

        for case_id, case in cases.items():
            with self.subTest(case_id=case_id):
                decoded = decode_apng_bit_depth_frame_data(case["png_bytes"])
                self.assertEqual(
                    expected_scanline_bytes(width, case["color_type"], case["bit_depth"]),
                    decoded["scanline_byte_length"],
                )
                self.assertEqual([0, 1, 2, 3, 4], decoded["frames"][0]["filter_types_seen"])
                self.assertEqual([0, 1, 2, 3, 4], decoded["frames"][1]["filter_types_seen"])
                self.assertEqual(width * grid["grid_size"][1], decoded["frames"][0]["pixel_count"])

        indexed = decode_apng_bit_depth_frame_data(cases["indexed4_fdat"]["png_bytes"])
        grayscale_alpha = decode_apng_bit_depth_frame_data(cases["grayscale_alpha16_fdat"]["png_bytes"])
        rgba = decode_apng_bit_depth_frame_data(cases["truecolor_alpha16_fdat"]["png_bytes"])
        self.assertTrue(indexed["has_plte"])
        self.assertTrue(indexed["has_trns"])
        self.assertTrue(any(frame["transparent_pixel_count"] > 0 for frame in indexed["frames"]))
        self.assertTrue(any(frame["partial_alpha_pixel_count"] > 0 for frame in grayscale_alpha["frames"]))
        self.assertTrue(any(frame["partial_alpha_pixel_count"] > 0 for frame in rgba["frames"]))

    def test_decoder_rejects_invalid_bit_depth_frame_data(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        cases = {
            case["case_id"]: case
            for case in export_apng_bit_depth_frame_data_cases(grid, profile)
        }

        probes = [
            (
                make_invalid_bit_depth_color_type_probe(cases["truecolor16_fdat"]["png_bytes"]),
                "png_bit_depth_color_type_invalid",
            ),
            (
                make_truncated_scanline_probe(cases["grayscale1_fdat"]["png_bytes"]),
                "apng_scanline_length_mismatch",
            ),
            (
                make_invalid_filter_probe(cases["grayscale16_fdat"]["png_bytes"]),
                "png_filter_type_unsupported",
            ),
            (
                make_sequence_gap_probe(cases["truecolor_alpha16_fdat"]["png_bytes"]),
                "apng_sequence_number_invalid",
            ),
        ]

        for png_bytes, family in probes:
            decoded = decode_apng_bit_depth_frame_data(png_bytes)
            self.assertFalse(decoded["ok"])
            self.assertIn(family, decoded["error_families"])

    def test_lab_report_closes_bit_depth_subset_without_full_conformance_claim(self):
        report = run_apng_bit_depth_frame_data_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("apng_bit_depth_frame_data_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(30, report["case_count"])
        self.assertEqual(30, report["case_success_count"])
        self.assertEqual(4, report["invalid_probe_count"])
        self.assertEqual(4, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["case_success_rate"])
        self.assertEqual([1, 2, 4, 16], report["metrics"]["supported_bit_depths"])
        self.assertEqual([0, 2, 3, 4, 6], report["metrics"]["supported_color_types"])
        self.assertIn("apng_low_bit_packed_frame_reconstruction", report["closed_states"])
        self.assertIn("apng_16bit_frame_reconstruction", report["closed_states"])
        self.assertIn("full_apng_png_conformance", report["blocked_states"])
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])

    def test_write_artifacts_creates_apngs_report_and_app_payload(self):
        report = run_apng_bit_depth_frame_data_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_apng_bit_depth_frame_data_artifacts(output_dir, report)

            summary_path = output_dir / "apng_bit_depth_frame_data_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "cases" / "slip_lcd_seed_grayscale1_fdat.png").exists())
            self.assertTrue((output_dir / "cases" / "slip_lcd_seed_truecolor_alpha16_fdat.png").exists())
            app_data = (output_dir / "apng_bit_depth_frame_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_APNG_BIT_DEPTH_FRAME_DATA", app_data)


if __name__ == "__main__":
    unittest.main()
