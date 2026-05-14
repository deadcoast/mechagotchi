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

from png_apng_zlib_compression_matrix import (
    PNG_APNG_ZLIB_COMPRESSION_CASE_IDS,
    decode_png_apng_zlib_compression,
    export_png_apng_zlib_compression_cases,
    make_corrupt_fdat_adler_probe,
    make_corrupt_idat_zlib_header_probe,
    make_invalid_compression_method_probe,
    make_sequence_gap_probe,
    make_truncated_fdat_probe,
    make_truncated_idat_probe,
    run_png_apng_zlib_compression_lab,
    write_png_apng_zlib_compression_artifacts,
)


VALID_PROFILE_PATHS = [
    Path("data/slips/valid/slip_lcd_seed.json"),
    Path("data/slips/valid/slip_gray_stable.json"),
    Path("data/slips/valid/slip_amber_social.json"),
]
GENERATED_ROOT = Path("data/slips/multi_profile_generation_stage0")
EXPECTED_CASE_IDS = [
    "png_zlib_stored_blocks",
    "png_zlib_fixed_huffman",
    "png_zlib_filtered_strategy",
    "apng_fdat_zlib_stored_blocks",
    "apng_fdat_zlib_fixed_huffman",
    "apng_fdat_zlib_rle_strategy",
]


def load_profile(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def first_grid_for(profile: dict) -> dict:
    grid_path = sorted((GENERATED_ROOT / profile["profile_id"]).glob("*.json"))[0]
    return json.loads(grid_path.read_text(encoding="utf-8"))


class PNGAPNGZlibCompressionMatrixTests(unittest.TestCase):
    def test_export_builds_static_png_and_apng_zlib_strategy_cases(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        cases = export_png_apng_zlib_compression_cases(grid, profile)

        self.assertEqual(EXPECTED_CASE_IDS, PNG_APNG_ZLIB_COMPRESSION_CASE_IDS)
        self.assertEqual(EXPECTED_CASE_IDS, [case["case_id"] for case in cases])
        self.assertEqual({"png", "apng"}, {case["carrier_family"] for case in cases})
        self.assertEqual(
            {"stored_blocks", "fixed_huffman", "filtered_strategy", "rle_strategy"},
            {case["compression_strategy_id"] for case in cases},
        )
        for case in cases:
            decoded = decode_png_apng_zlib_compression(case["png_bytes"])
            self.assertTrue(decoded["ok"], decoded["errors"])
            self.assertEqual(case["carrier_family"], decoded["carrier_family"])
            self.assertEqual(0, decoded["ihdr_compression_method"])
            self.assertEqual(8, decoded["zlib_header"]["compression_method"])
            self.assertTrue(decoded["zlib_header"]["cmf_flg_check_passed"])
            self.assertEqual(case["expected_pixel_hash"], decoded["pixel_hash"])
            self.assertEqual(case["expected_raw_image_data_hash"], decoded["raw_image_data_hash"])
            self.assertEqual(case["expected_compressed_data_hash"], decoded["compressed_data_hash"])
            self.assertEqual(case["expected_data_chunk_count"], decoded["data_chunk_count"])

        apng_cases = [case for case in cases if case["carrier_family"] == "apng"]
        self.assertTrue(all(case["expected_fdat_chunk_count"] == 2 for case in apng_cases))

    def test_valid_zlib_variants_preserve_raw_scanlines_with_different_streams(self):
        profile = load_profile(VALID_PROFILE_PATHS[1])
        grid = first_grid_for(profile)
        cases = export_png_apng_zlib_compression_cases(grid, profile)

        png_decoded = [
            decode_png_apng_zlib_compression(case["png_bytes"])
            for case in cases
            if case["carrier_family"] == "png"
        ]
        apng_decoded = [
            decode_png_apng_zlib_compression(case["png_bytes"])
            for case in cases
            if case["carrier_family"] == "apng"
        ]

        self.assertEqual(1, len({decoded["raw_image_data_hash"] for decoded in png_decoded}))
        self.assertEqual(1, len({decoded["raw_image_data_hash"] for decoded in apng_decoded}))
        self.assertGreaterEqual(len({decoded["compressed_data_hash"] for decoded in png_decoded}), 2)
        self.assertGreaterEqual(len({decoded["compressed_data_hash"] for decoded in apng_decoded}), 2)
        self.assertEqual({"png"}, {decoded["carrier_family"] for decoded in png_decoded})
        self.assertEqual({"apng"}, {decoded["carrier_family"] for decoded in apng_decoded})

    def test_decoder_rejects_invalid_zlib_and_compression_method_inputs(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        by_case = {
            case["case_id"]: case["png_bytes"]
            for case in export_png_apng_zlib_compression_cases(grid, profile)
        }
        probes = [
            (
                make_invalid_compression_method_probe(by_case["png_zlib_stored_blocks"]),
                "png_method_unsupported",
            ),
            (
                make_corrupt_idat_zlib_header_probe(by_case["png_zlib_fixed_huffman"]),
                "png_image_data_decompression_failed",
            ),
            (
                make_truncated_idat_probe(by_case["png_zlib_filtered_strategy"]),
                "png_image_data_decompression_failed",
            ),
            (
                make_truncated_fdat_probe(by_case["apng_fdat_zlib_stored_blocks"]),
                "apng_frame_decompression_failed",
            ),
            (
                make_corrupt_fdat_adler_probe(by_case["apng_fdat_zlib_fixed_huffman"]),
                "apng_frame_decompression_failed",
            ),
            (
                make_sequence_gap_probe(by_case["apng_fdat_zlib_rle_strategy"]),
                "apng_sequence_number_invalid",
            ),
        ]

        for png_bytes, expected_family in probes:
            decoded = decode_png_apng_zlib_compression(png_bytes)
            self.assertFalse(decoded["ok"], expected_family)
            self.assertEqual(expected_family, decoded["error_family"])

    def test_lab_report_closes_zlib_subset_without_full_conformance_claim(self):
        report = run_png_apng_zlib_compression_lab(VALID_PROFILE_PATHS, GENERATED_ROOT)

        self.assertEqual("png_apng_zlib_compression_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(18, report["case_count"])
        self.assertEqual(18, report["case_success_count"])
        self.assertEqual(6, report["invalid_probe_count"])
        self.assertEqual(6, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["case_success_ratio"])
        self.assertEqual(1.0, report["metrics"]["invalid_probe_rejection_ratio"])
        self.assertEqual(9, report["metrics"]["png_case_count"])
        self.assertEqual(9, report["metrics"]["apng_case_count"])
        self.assertEqual(18, report["metrics"]["ihdr_compression_method_0_count"])
        self.assertEqual(18, report["metrics"]["zlib_cm8_case_count"])
        self.assertIn("png_idat_zlib_deflate_variant_reconstruction", report["closed_states"])
        self.assertIn("apng_fdat_zlib_deflate_variant_reconstruction", report["closed_states"])
        self.assertIn("full_apng_png_conformance", report["blocked_states"])
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])
        self.assertIn("package_runtime_lifecycle_integration", report["blocked_states"])

    def test_write_artifacts_creates_pngs_report_and_app_payload(self):
        report = run_png_apng_zlib_compression_lab(VALID_PROFILE_PATHS, GENERATED_ROOT)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = write_png_apng_zlib_compression_artifacts(root, report)

            self.assertTrue(paths["summary_json"].exists())
            self.assertTrue(paths["artifact_summary_json"].exists())
            self.assertTrue(paths["app_js"].exists())
            self.assertTrue(paths["artifact_app_js"].exists())
            self.assertTrue(paths["readme"].exists())
            self.assertEqual(18, len(list((paths["artifact_dir"] / "cases").glob("*.png"))))
            self.assertIn(
                "MECHAGOTCHI_PNG_APNG_ZLIB_COMPRESSION",
                paths["app_js"].read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
