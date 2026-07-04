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

from png_apng_color_type_frame_data import (
    COLOR_TYPE_CASE_IDS,
    decode_apng_color_type_frame_data,
    export_apng_color_type_frame_data_cases,
    make_alpha_trns_conflict_probe,
    make_invalid_trns_probe,
    make_missing_plte_probe,
    make_unsupported_color_type_probe,
    run_apng_color_type_frame_data_lab,
    write_apng_color_type_frame_data_artifacts,
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


class APNGColorTypeFrameDataTests(unittest.TestCase):
    def test_export_builds_all_png_color_type_apng_cases(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        cases = export_apng_color_type_frame_data_cases(grid, profile)

        self.assertEqual(COLOR_TYPE_CASE_IDS, [case["case_id"] for case in cases])
        self.assertEqual({0, 2, 3, 4, 6}, {case["color_type"] for case in cases})
        for case in cases:
            decoded = decode_apng_color_type_frame_data(case["png_bytes"])
            self.assertTrue(decoded["ok"])
            self.assertEqual(case["expected_frame_hashes"], decoded["frame_pixel_hashes"])
            self.assertEqual(case["expected_display_hashes"], decoded["display_hashes"])
            self.assertEqual(case["expected_final_hash"], decoded["final_output_hash"])
            self.assertEqual(case["color_type"], decoded["color_type"])
            self.assertEqual(2, decoded["frame_count"])

    def test_decoder_restores_palette_and_alpha_semantics(self):
        profile = load_profile(VALID_PROFILE_PATHS[1])
        grid = first_grid_for(profile)
        cases = {
            case["case_id"]: case
            for case in export_apng_color_type_frame_data_cases(grid, profile)
        }

        indexed = decode_apng_color_type_frame_data(cases["indexed8_trns_fdat"]["png_bytes"])
        grayscale_alpha = decode_apng_color_type_frame_data(cases["grayscale_alpha8_fdat"]["png_bytes"])
        truecolor_alpha = decode_apng_color_type_frame_data(cases["truecolor_alpha8_fdat"]["png_bytes"])

        self.assertTrue(indexed["has_plte"])
        self.assertTrue(indexed["has_trns"])
        self.assertTrue(any(frame["transparent_pixel_count"] > 0 for frame in indexed["frames"]))
        self.assertFalse(grayscale_alpha["has_trns"])
        self.assertTrue(any(frame["transparent_pixel_count"] > 0 for frame in grayscale_alpha["frames"]))
        self.assertTrue(any(frame["partial_alpha_pixel_count"] > 0 for frame in truecolor_alpha["frames"]))

    def test_decoder_applies_color_type_specific_channel_widths(self):
        profile = load_profile(VALID_PROFILE_PATHS[2])
        grid = first_grid_for(profile)
        cases = {
            case["case_id"]: case
            for case in export_apng_color_type_frame_data_cases(grid, profile)
        }

        grayscale = decode_apng_color_type_frame_data(cases["grayscale8_fdat"]["png_bytes"])
        truecolor = decode_apng_color_type_frame_data(cases["truecolor8_fdat"]["png_bytes"])
        indexed = decode_apng_color_type_frame_data(cases["indexed8_trns_fdat"]["png_bytes"])
        grayscale_alpha = decode_apng_color_type_frame_data(cases["grayscale_alpha8_fdat"]["png_bytes"])
        truecolor_alpha = decode_apng_color_type_frame_data(cases["truecolor_alpha8_fdat"]["png_bytes"])

        self.assertEqual(1, grayscale["bytes_per_pixel"])
        self.assertEqual(3, truecolor["bytes_per_pixel"])
        self.assertEqual(1, indexed["bytes_per_pixel"])
        self.assertEqual(2, grayscale_alpha["bytes_per_pixel"])
        self.assertEqual(4, truecolor_alpha["bytes_per_pixel"])

    def test_decoder_rejects_trailing_bytes_after_iend(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        reference = export_apng_color_type_frame_data_cases(grid, profile)[0]

        decoded = decode_apng_color_type_frame_data(reference["png_bytes"] + b"junk")

        self.assertFalse(decoded["ok"])
        self.assertEqual(["png_trailing_bytes"], decoded["error_families"])

    def test_decoder_rejects_invalid_color_type_metadata(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        cases = {
            case["case_id"]: case
            for case in export_apng_color_type_frame_data_cases(grid, profile)
        }

        probes = [
            (make_missing_plte_probe(cases["indexed8_trns_fdat"]["png_bytes"]), "png_plte_missing"),
            (make_invalid_trns_probe(cases["indexed8_trns_fdat"]["png_bytes"]), "png_trns_invalid"),
            (make_unsupported_color_type_probe(cases["truecolor8_fdat"]["png_bytes"]), "png_color_type_unsupported"),
            (make_alpha_trns_conflict_probe(cases["truecolor_alpha8_fdat"]["png_bytes"]), "png_trns_forbidden"),
        ]

        for png_bytes, family in probes:
            decoded = decode_apng_color_type_frame_data(png_bytes)
            self.assertFalse(decoded["ok"])
            self.assertIn(family, decoded["error_families"])

    def test_lab_report_closes_color_type_subset_without_full_conformance_claim(self):
        report = run_apng_color_type_frame_data_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("apng_color_type_frame_data_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(15, report["case_count"])
        self.assertEqual(15, report["case_success_count"])
        self.assertEqual(4, report["invalid_probe_count"])
        self.assertEqual(4, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["case_success_rate"])
        self.assertEqual(5, report["metrics"]["color_type_family_count"])
        self.assertIn("apng_color_type_frame_reconstruction", report["closed_states"])
        self.assertIn("apng_palette_trns_frame_reconstruction", report["closed_states"])
        self.assertIn("full_apng_png_conformance", report["blocked_states"])
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])

    def test_write_artifacts_creates_apngs_report_and_app_payload(self):
        report = run_apng_color_type_frame_data_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_apng_color_type_frame_data_artifacts(output_dir, report)

            summary_path = output_dir / "apng_color_type_frame_data_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "cases" / "slip_lcd_seed_indexed8_trns_fdat.png").exists())
            self.assertTrue((output_dir / "cases" / "slip_lcd_seed_grayscale_alpha8_fdat.png").exists())
            app_data = (output_dir / "apng_color_type_frame_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_APNG_COLOR_TYPE_FRAME_DATA", app_data)


if __name__ == "__main__":
    unittest.main()
