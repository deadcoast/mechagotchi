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

from png_apng_image_data_chunking import (
    PNG_APNG_IMAGE_DATA_CHUNKING_CASE_IDS,
    decode_png_apng_image_data_chunking,
    export_png_apng_image_data_chunking_cases,
    make_corrupt_fdat_probe,
    make_corrupt_idat_probe,
    make_idat_nonconsecutive_probe,
    make_missing_fdat_probe,
    make_missing_idat_probe,
    make_sequence_gap_probe,
    run_png_apng_image_data_chunking_lab,
    write_png_apng_image_data_chunking_artifacts,
)


VALID_PROFILE_PATHS = [
    ROOT / "data/slips/valid/slip_lcd_seed.json",
    ROOT / "data/slips/valid/slip_gray_stable.json",
    ROOT / "data/slips/valid/slip_amber_social.json",
]
GENERATED_ROOT = ROOT / "data/slips/multi_profile_generation_stage0"
EXPECTED_CASE_IDS = [
    "png_idat_leading_empty_chunk",
    "png_idat_zlib_header_split",
    "png_idat_adler32_split",
    "apng_fdat_leading_empty_frame_data",
    "apng_fdat_zlib_header_split",
    "apng_fdat_adler32_split",
]


def load_profile(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def first_grid_for(profile: dict) -> dict:
    grid_path = sorted((GENERATED_ROOT / profile["profile_id"]).glob("*.json"))[0]
    return json.loads(grid_path.read_text(encoding="utf-8"))


class PNGAPNGImageDataChunkingTests(unittest.TestCase):
    def test_export_builds_static_png_and_apng_chunk_boundary_cases(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        cases = export_png_apng_image_data_chunking_cases(grid, profile)

        self.assertEqual(EXPECTED_CASE_IDS, PNG_APNG_IMAGE_DATA_CHUNKING_CASE_IDS)
        self.assertEqual(EXPECTED_CASE_IDS, [case["case_id"] for case in cases])
        self.assertEqual({"png", "apng"}, {case["carrier_family"] for case in cases})
        for case in cases:
            decoded = decode_png_apng_image_data_chunking(case["png_bytes"])
            self.assertTrue(decoded["ok"], decoded["errors"])
            self.assertEqual(case["carrier_family"], decoded["carrier_family"])
            self.assertEqual(case["expected_pixel_hash"], decoded["pixel_hash"])
            self.assertEqual(case["expected_idat_data_lengths"], decoded["idat_data_lengths"])
            self.assertEqual(case["expected_fdat_frame_data_lengths"], decoded["fdat_frame_data_lengths"])
            self.assertEqual(case["expected_data_chunk_count"], decoded["data_chunk_count"])

        png_cases = [case for case in cases if case["carrier_family"] == "png"]
        apng_cases = [case for case in cases if case["carrier_family"] == "apng"]
        self.assertTrue(any(0 in case["expected_idat_data_lengths"] for case in png_cases))
        self.assertTrue(any(0 in case["expected_fdat_frame_data_lengths"] for case in apng_cases))
        self.assertTrue(any(case["split_target"] == "adler32" for case in cases))

    def test_decoder_reconstructs_pixels_across_arbitrary_data_chunk_boundaries(self):
        profile = load_profile(VALID_PROFILE_PATHS[1])
        grid = first_grid_for(profile)
        cases = {
            case["case_id"]: case
            for case in export_png_apng_image_data_chunking_cases(grid, profile)
        }

        png_header = decode_png_apng_image_data_chunking(cases["png_idat_zlib_header_split"]["png_bytes"])
        self.assertTrue(png_header["ok"], png_header["errors"])
        self.assertEqual([1], png_header["idat_data_lengths"][:1])
        self.assertEqual(cases["png_idat_zlib_header_split"]["expected_pixel_hash"], png_header["pixel_hash"])

        png_adler = decode_png_apng_image_data_chunking(cases["png_idat_adler32_split"]["png_bytes"])
        self.assertTrue(png_adler["ok"], png_adler["errors"])
        self.assertEqual(5, png_adler["data_chunk_count"])
        self.assertEqual(cases["png_idat_adler32_split"]["expected_pixel_hash"], png_adler["pixel_hash"])

        apng_adler = decode_png_apng_image_data_chunking(cases["apng_fdat_adler32_split"]["png_bytes"])
        self.assertTrue(apng_adler["ok"], apng_adler["errors"])
        self.assertEqual(5, apng_adler["fdat_chunk_count"])
        self.assertEqual(cases["apng_fdat_adler32_split"]["expected_pixel_hash"], apng_adler["pixel_hash"])

    def test_decoder_rejects_invalid_image_data_chunking_inputs(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        by_case = {
            case["case_id"]: case["png_bytes"]
            for case in export_png_apng_image_data_chunking_cases(grid, profile)
        }
        probes = [
            (
                make_idat_nonconsecutive_probe(by_case["png_idat_zlib_header_split"]),
                "png_idat_not_consecutive",
            ),
            (
                make_corrupt_idat_probe(by_case["png_idat_adler32_split"]),
                "png_image_data_decompression_failed",
            ),
            (
                make_missing_idat_probe(by_case["png_idat_leading_empty_chunk"]),
                "png_idat_missing",
            ),
            (
                make_missing_fdat_probe(by_case["apng_fdat_leading_empty_frame_data"]),
                "apng_frame_data_missing",
            ),
            (
                make_sequence_gap_probe(by_case["apng_fdat_zlib_header_split"]),
                "apng_sequence_number_invalid",
            ),
            (
                make_corrupt_fdat_probe(by_case["apng_fdat_adler32_split"]),
                "apng_frame_decompression_failed",
            ),
        ]

        for png_bytes, expected_family in probes:
            decoded = decode_png_apng_image_data_chunking(png_bytes)
            self.assertFalse(decoded["ok"], expected_family)
            self.assertEqual(expected_family, decoded["error_family"])

    def test_lab_report_closes_chunk_boundary_subset_without_full_conformance_claim(self):
        report = run_png_apng_image_data_chunking_lab(VALID_PROFILE_PATHS, GENERATED_ROOT)

        self.assertEqual("png_apng_image_data_chunking_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(18, report["case_count"])
        self.assertEqual(18, report["case_success_count"])
        self.assertEqual(6, report["invalid_probe_count"])
        self.assertEqual(6, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["case_success_ratio"])
        self.assertEqual(1.0, report["metrics"]["invalid_probe_rejection_ratio"])
        self.assertEqual(9, report["metrics"]["png_case_count"])
        self.assertEqual(9, report["metrics"]["apng_case_count"])
        self.assertEqual(6, report["metrics"]["zero_length_data_chunk_case_count"])
        self.assertEqual(6, report["metrics"]["adler32_split_case_count"])
        self.assertIn("png_idat_arbitrary_boundary_reconstruction", report["closed_states"])
        self.assertIn("apng_fdat_arbitrary_boundary_reconstruction", report["closed_states"])
        self.assertIn("full_apng_png_conformance", report["blocked_states"])
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])
        self.assertIn("package_runtime_lifecycle_integration", report["blocked_states"])

    def test_write_artifacts_creates_pngs_report_and_app_payload(self):
        report = run_png_apng_image_data_chunking_lab(VALID_PROFILE_PATHS, GENERATED_ROOT)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = write_png_apng_image_data_chunking_artifacts(root, report)

            self.assertTrue(paths["summary_json"].exists())
            self.assertTrue(paths["artifact_summary_json"].exists())
            self.assertTrue(paths["app_js"].exists())
            self.assertTrue(paths["artifact_app_js"].exists())
            self.assertTrue(paths["readme"].exists())
            self.assertEqual(18, len(list((paths["artifact_dir"] / "cases").glob("*.png"))))
            self.assertIn(
                "MECHAGOTCHI_PNG_APNG_IMAGE_DATA_CHUNKING",
                paths["app_js"].read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
