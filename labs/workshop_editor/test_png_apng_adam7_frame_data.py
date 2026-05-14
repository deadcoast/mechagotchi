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

from png_adam7_interlace_decoder import ADAM7_PASSES
from png_apng_adam7_frame_data import (
    APNG_ADAM7_CASE_IDS,
    decode_apng_adam7_frame_data,
    export_apng_adam7_frame_data_cases,
    make_invalid_bit_depth_color_type_probe,
    make_invalid_filter_probe,
    make_non_adam7_interlace_probe,
    make_sequence_gap_probe,
    make_truncated_adam7_scanline_probe,
    run_apng_adam7_frame_data_lab,
    write_apng_adam7_frame_data_artifacts,
)


VALID_PROFILE_PATHS = [
    Path("data/slips/valid/slip_lcd_seed.json"),
    Path("data/slips/valid/slip_gray_stable.json"),
    Path("data/slips/valid/slip_amber_social.json"),
]
GENERATED_ROOT = Path("data/slips/multi_profile_generation_stage0")
EXPECTED_CASE_IDS = [
    "rgba8_adam7_fdat",
    "grayscale1_adam7_fdat",
    "indexed4_adam7_trns_fdat",
    "truecolor16_adam7_fdat",
    "grayscale_alpha16_adam7_over_fdat",
    "truecolor_alpha16_adam7_over_fdat",
]


def load_profile(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def first_grid_for(profile: dict) -> dict:
    grid_path = sorted((GENERATED_ROOT / profile["profile_id"]).glob("*.json"))[0]
    return json.loads(grid_path.read_text(encoding="utf-8"))


class APNGAdam7FrameDataTests(unittest.TestCase):
    def test_export_builds_adam7_apng_frame_data_cases(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        cases = export_apng_adam7_frame_data_cases(grid, profile)

        self.assertEqual(EXPECTED_CASE_IDS, APNG_ADAM7_CASE_IDS)
        self.assertEqual(EXPECTED_CASE_IDS, [case["case_id"] for case in cases])
        self.assertEqual({0, 2, 3, 4, 6}, {case["color_type"] for case in cases})
        self.assertEqual({1, 4, 8, 16}, {case["bit_depth"] for case in cases})
        for case in cases:
            decoded = decode_apng_adam7_frame_data(case["png_bytes"])
            self.assertTrue(decoded["ok"], decoded["errors"])
            self.assertEqual(1, decoded["interlace_method"])
            self.assertEqual(2, decoded["frame_count"])
            self.assertEqual(case["expected_frame_hashes"], decoded["frame_pixel_hashes"])
            self.assertEqual(case["expected_display_hashes"], decoded["display_hashes"])
            self.assertEqual(case["expected_final_hash"], decoded["final_canvas_hash"])
            self.assertEqual([1, 2, 3, 4, 5, 6, 7], decoded["pass_order"])
            self.assertEqual([0, 1, 2, 3, 4], decoded["filter_types_seen"])
            self.assertEqual(2, decoded["frames"][1]["fdat_chunk_count"])
            for frame in decoded["frames"]:
                self.assertEqual(7, frame["non_empty_pass_count"])
                self.assertEqual([spec["pass_index"] for spec in ADAM7_PASSES], frame["pass_order"])
                self.assertEqual(7, len(frame["pass_summaries"]))

    def test_decoder_restores_indexed_transparency_and_alpha_over_from_adam7_frames(self):
        profile = load_profile(VALID_PROFILE_PATHS[1])
        grid = first_grid_for(profile)
        cases = {
            case["case_id"]: case
            for case in export_apng_adam7_frame_data_cases(grid, profile)
        }

        indexed = cases["indexed4_adam7_trns_fdat"]["decoded"]
        self.assertTrue(indexed["palette"]["present"])
        self.assertTrue(indexed["transparency"]["present"])
        self.assertGreater(indexed["frames"][1]["transparent_pixel_count"], 0)

        for case_id in [
            "grayscale_alpha16_adam7_over_fdat",
            "truecolor_alpha16_adam7_over_fdat",
        ]:
            decoded = cases[case_id]["decoded"]
            self.assertEqual(1, decoded["frames"][1]["blend_op"])
            self.assertGreater(decoded["frames"][1]["partial_alpha_pixel_count"], 0)
            self.assertNotEqual(decoded["display_hashes"][0], decoded["display_hashes"][1])

    def test_decoder_rejects_invalid_adam7_apng_frame_data_inputs(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        by_case = {
            case["case_id"]: case["png_bytes"]
            for case in export_apng_adam7_frame_data_cases(grid, profile)
        }
        probes = [
            (
                make_non_adam7_interlace_probe(by_case["rgba8_adam7_fdat"]),
                "apng_adam7_interlace_required",
            ),
            (
                make_invalid_bit_depth_color_type_probe(by_case["truecolor16_adam7_fdat"]),
                "png_bit_depth_color_type_invalid",
            ),
            (
                make_truncated_adam7_scanline_probe(by_case["grayscale1_adam7_fdat"]),
                "apng_adam7_scanline_length_mismatch",
            ),
            (
                make_invalid_filter_probe(by_case["grayscale_alpha16_adam7_over_fdat"]),
                "png_filter_type_unsupported",
            ),
            (
                make_sequence_gap_probe(by_case["truecolor_alpha16_adam7_over_fdat"]),
                "apng_sequence_number_invalid",
            ),
        ]

        for png_bytes, expected_family in probes:
            decoded = decode_apng_adam7_frame_data(png_bytes)
            self.assertFalse(decoded["ok"], expected_family)
            self.assertEqual(expected_family, decoded["error_family"])

    def test_lab_report_closes_adam7_apng_subset_without_full_conformance_claim(self):
        report = run_apng_adam7_frame_data_lab(VALID_PROFILE_PATHS, GENERATED_ROOT)

        self.assertEqual("apng_adam7_frame_data_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(18, report["case_count"])
        self.assertEqual(18, report["case_success_count"])
        self.assertEqual(5, report["invalid_probe_count"])
        self.assertEqual(5, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["case_success_ratio"])
        self.assertEqual([0, 2, 3, 4, 6], report["metrics"]["supported_color_types"])
        self.assertEqual([1, 4, 8, 16], report["metrics"]["supported_bit_depths"])
        self.assertEqual(18, report["metrics"]["split_fdat_frame_count"])
        self.assertIn("apng_adam7_frame_reconstruction", report["closed_states"])
        self.assertIn("apng_adam7_deep_sample_reconstruction", report["closed_states"])
        self.assertIn("apng_adam7_invalid_probe_rejection", report["closed_states"])
        self.assertIn("full_apng_png_conformance", report["blocked_states"])
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])
        self.assertIn("package_runtime_lifecycle_integration", report["blocked_states"])

    def test_write_artifacts_creates_apngs_report_and_app_payload(self):
        report = run_apng_adam7_frame_data_lab(VALID_PROFILE_PATHS, GENERATED_ROOT)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = write_apng_adam7_frame_data_artifacts(root, report)

            self.assertTrue(paths["summary_json"].exists())
            self.assertTrue(paths["artifact_summary_json"].exists())
            self.assertTrue(paths["app_js"].exists())
            self.assertTrue(paths["artifact_app_js"].exists())
            self.assertTrue(paths["readme"].exists())
            self.assertEqual(18, len(list((paths["artifact_dir"] / "cases").glob("*.png"))))
            self.assertIn(
                "MECHAGOTCHI_APNG_ADAM7_FRAME_DATA",
                paths["app_js"].read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
