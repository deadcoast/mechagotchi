import json
import tempfile
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

WORKSHOP_DIR = Path(__file__).resolve().parent
GRID_GENOME_DIR = WORKSHOP_DIR.parents[0] / "grid_genome"
for import_path in [WORKSHOP_DIR, GRID_GENOME_DIR]:
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

from png_apng_partial_sample_frame_data import (
    PARTIAL_SAMPLE_CASE_IDS,
    decode_apng_partial_sample_frame_data,
    export_apng_partial_sample_frame_data_cases,
    make_invalid_bit_depth_color_type_probe,
    make_invalid_filter_probe,
    make_out_of_bounds_probe,
    make_sequence_gap_probe,
    make_truncated_partial_scanline_probe,
    run_apng_partial_sample_frame_data_lab,
    write_apng_partial_sample_frame_data_artifacts,
)
from png_deep_color_sidecar_decoder import _scanline_byte_length


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


class APNGPartialSampleFrameDataTests(unittest.TestCase):
    def test_export_builds_partial_sample_cases(self):
        cases = []
        for profile_path in VALID_PROFILE_PATHS:
            profile = load_profile(profile_path)
            cases.extend(export_apng_partial_sample_frame_data_cases(first_grid_for(profile), profile))

        self.assertEqual(len(cases), 15)
        self.assertEqual(
            sorted({case["case_id"] for case in cases}),
            sorted(PARTIAL_SAMPLE_CASE_IDS),
        )
        self.assertEqual({case["decoded"]["ihdr"]["color_type"] for case in cases}, {0, 2, 3, 4, 6})
        self.assertEqual({case["decoded"]["ihdr"]["bit_depth"] for case in cases}, {1, 4, 16})

        for case in cases:
            decoded = decode_apng_partial_sample_frame_data(case["png_bytes"])
            self.assertTrue(decoded["ok"])
            self.assertEqual(decoded["frame_count"], 2)
            self.assertFalse(decoded["frames"][1]["full_canvas"])
            self.assertEqual(decoded["frames"][1]["fdat_chunk_count"], 2)
            self.assertEqual(
                decoded["display_hashes"],
                case["expected_display_hashes"],
                case["case_id"],
            )
            self.assertEqual(decoded["final_canvas_hash"], case["expected_final_hash"], case["case_id"])

    def test_decoder_composes_source_and_over_regions_by_sample_model(self):
        profile = load_profile(VALID_PROFILE_PATHS[1])
        profile_id = profile["profile_id"]
        cases = {
            case["case_id"]: case
            for case in export_apng_partial_sample_frame_data_cases(first_grid_for(profile), profile)
        }

        indexed = cases[f"{profile_id}_indexed4_trns_source_patch"]["decoded"]
        self.assertTrue(indexed["palette"]["present"])
        self.assertTrue(indexed["transparency"]["present"])
        self.assertGreater(indexed["frames"][1]["transparent_pixel_count"], 0)

        for case_id in [
            f"{profile_id}_grayscale_alpha16_over_patch",
            f"{profile_id}_truecolor_alpha16_over_patch",
        ]:
            decoded = cases[case_id]["decoded"]
            patch = decoded["frames"][1]
            self.assertEqual(patch["blend_op"], 1)
            self.assertGreater(patch["partial_alpha_pixel_count"], 0)
            self.assertNotEqual(decoded["display_hashes"][0], decoded["display_hashes"][1])

        for case in cases.values():
            patch = case["decoded"]["frames"][1]
            ihdr = case["decoded"]["ihdr"]
            self.assertGreater(patch["x_offset"], 0)
            self.assertGreater(patch["y_offset"], 0)
            self.assertEqual(
                patch["scanline_byte_length"],
                _scanline_byte_length(
                    patch["width"],
                    ihdr["color_type"],
                    ihdr["bit_depth"],
                ),
            )

    def test_decoder_rejects_invalid_partial_sample_inputs(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        case = export_apng_partial_sample_frame_data_cases(first_grid_for(profile), profile)[0]
        probes = [
            (make_out_of_bounds_probe(case["png_bytes"]), "apng_frame_bounds_invalid"),
            (
                make_invalid_bit_depth_color_type_probe(case["png_bytes"]),
                "png_bit_depth_color_type_invalid",
            ),
            (
                make_truncated_partial_scanline_probe(case["png_bytes"]),
                "apng_scanline_length_mismatch",
            ),
            (make_invalid_filter_probe(case["png_bytes"]), "png_filter_type_unsupported"),
            (make_sequence_gap_probe(case["png_bytes"]), "apng_sequence_number_invalid"),
        ]

        for png_bytes, expected_family in probes:
            decoded = decode_apng_partial_sample_frame_data(png_bytes)
            self.assertFalse(decoded["ok"], expected_family)
            self.assertEqual(decoded["error_family"], expected_family)

    def test_lab_report_closes_partial_sample_subset_without_full_conformance_claim(self):
        report = run_apng_partial_sample_frame_data_lab()

        self.assertEqual(report["artifact_id"], "apng_partial_sample_frame_data_stage0")
        self.assertEqual(report["profile_count"], 3)
        self.assertEqual(report["case_count"], 15)
        self.assertEqual(report["case_success_count"], 15)
        self.assertEqual(report["invalid_probe_count"], 5)
        self.assertEqual(report["invalid_probe_rejected_count"], 5)
        self.assertEqual(report["metrics"]["case_success_ratio"], 1.0)
        self.assertEqual(report["supported_bit_depths"], [1, 4, 16])
        self.assertEqual(report["supported_color_types"], [0, 2, 3, 4, 6])
        self.assertIn("apng_partial_sample_offset_reconstruction", report["closed_states"])
        self.assertIn("apng_partial_low_bit_region_reconstruction", report["closed_states"])
        self.assertIn("apng_partial_16bit_region_reconstruction", report["closed_states"])
        self.assertIn("apng_partial_alpha_over_sample_reconstruction", report["closed_states"])
        self.assertIn("apng_partial_sample_invalid_probe_rejection", report["closed_states"])
        self.assertIn("full_apng_png_conformance", report["blocked_states"])
        self.assertIn("package_runtime_lifecycle_integration", report["blocked_states"])

    def test_write_artifacts_creates_apngs_report_and_app_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = write_apng_partial_sample_frame_data_artifacts(root)

            self.assertTrue(paths["summary_json"].exists())
            self.assertTrue(paths["app_js"].exists())
            self.assertTrue(paths["artifact_dir"].exists())
            self.assertTrue(paths["artifact_summary_json"].exists())
            self.assertTrue(paths["artifact_app_js"].exists())
            self.assertGreaterEqual(len(list((paths["artifact_dir"] / "cases").glob("*.png"))), 15)
            self.assertIn(
                "MECHAGOTCHI_APNG_PARTIAL_SAMPLE_FRAME_DATA",
                paths["app_js"].read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
