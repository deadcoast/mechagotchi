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

from png_apng_zlib_header_policy import (
    PNG_APNG_ZLIB_HEADER_POLICY_CASE_IDS,
    decode_png_apng_zlib_header_policy,
    export_png_apng_zlib_header_policy_cases,
    make_apng_cinfo_too_large_probe,
    make_apng_cmf_flg_check_probe,
    make_apng_fdict_probe,
    make_png_cmf_flg_check_probe,
    make_png_fdict_probe,
    make_png_reserved_cm_probe,
    run_png_apng_zlib_header_policy_lab,
    write_png_apng_zlib_header_policy_artifacts,
)


VALID_PROFILE_PATHS = [
    Path("data/slips/valid/slip_lcd_seed.json"),
    Path("data/slips/valid/slip_gray_stable.json"),
    Path("data/slips/valid/slip_amber_social.json"),
]
GENERATED_ROOT = Path("data/slips/multi_profile_generation_stage0")
EXPECTED_CASE_IDS = [
    "png_zlib_window_512",
    "png_zlib_window_4096",
    "png_zlib_window_32768",
    "apng_fdat_zlib_window_512",
    "apng_fdat_zlib_window_4096",
    "apng_fdat_zlib_window_32768",
]


def load_profile(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def first_grid_for(profile: dict) -> dict:
    grid_path = sorted((GENERATED_ROOT / profile["profile_id"]).glob("*.json"))[0]
    return json.loads(grid_path.read_text(encoding="utf-8"))


class PNGAPNGZlibHeaderPolicyTests(unittest.TestCase):
    def test_export_builds_png_and_apng_zlib_window_cases(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        cases = export_png_apng_zlib_header_policy_cases(grid, profile)

        self.assertEqual(EXPECTED_CASE_IDS, PNG_APNG_ZLIB_HEADER_POLICY_CASE_IDS)
        self.assertEqual(EXPECTED_CASE_IDS, [case["case_id"] for case in cases])
        self.assertEqual({"png", "apng"}, {case["carrier_family"] for case in cases})
        self.assertEqual({1, 4, 7}, {case["expected_zlib_header"]["compression_info"] for case in cases})
        for case in cases:
            decoded = decode_png_apng_zlib_header_policy(case["png_bytes"])
            self.assertTrue(decoded["ok"], decoded["errors"])
            self.assertEqual(case["carrier_family"], decoded["carrier_family"])
            self.assertEqual(0, decoded["ihdr_compression_method"])
            self.assertEqual(8, decoded["zlib_header"]["compression_method"])
            self.assertFalse(decoded["zlib_header"]["fdict"])
            self.assertTrue(decoded["zlib_header"]["cmf_flg_check_passed"])
            self.assertEqual(case["expected_zlib_header"]["compression_info"], decoded["zlib_header"]["compression_info"])
            self.assertEqual(case["expected_raw_image_data_hash"], decoded["raw_image_data_hash"])
            self.assertEqual(case["expected_pixel_hash"], decoded["pixel_hash"])

    def test_zlib_window_headers_preserve_raw_scanlines_per_carrier(self):
        profile = load_profile(VALID_PROFILE_PATHS[1])
        grid = first_grid_for(profile)
        cases = export_png_apng_zlib_header_policy_cases(grid, profile)

        png_decoded = [
            decode_png_apng_zlib_header_policy(case["png_bytes"])
            for case in cases
            if case["carrier_family"] == "png"
        ]
        apng_decoded = [
            decode_png_apng_zlib_header_policy(case["png_bytes"])
            for case in cases
            if case["carrier_family"] == "apng"
        ]

        self.assertEqual([1, 4, 7], [decoded["zlib_header"]["compression_info"] for decoded in png_decoded])
        self.assertEqual([1, 4, 7], [decoded["zlib_header"]["compression_info"] for decoded in apng_decoded])
        self.assertEqual(1, len({decoded["raw_image_data_hash"] for decoded in png_decoded}))
        self.assertEqual(1, len({decoded["raw_image_data_hash"] for decoded in apng_decoded}))
        self.assertGreaterEqual(len({decoded["compressed_data_hash"] for decoded in png_decoded}), 2)
        self.assertGreaterEqual(len({decoded["compressed_data_hash"] for decoded in apng_decoded}), 2)

    def test_decoder_rejects_invalid_zlib_header_policy_inputs(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        by_case = {
            case["case_id"]: case["png_bytes"]
            for case in export_png_apng_zlib_header_policy_cases(grid, profile)
        }
        probes = [
            (
                make_png_fdict_probe(by_case["png_zlib_window_512"]),
                "png_image_data_decompression_failed",
            ),
            (
                make_png_cmf_flg_check_probe(by_case["png_zlib_window_4096"]),
                "png_image_data_decompression_failed",
            ),
            (
                make_png_reserved_cm_probe(by_case["png_zlib_window_32768"]),
                "png_image_data_decompression_failed",
            ),
            (
                make_apng_fdict_probe(by_case["apng_fdat_zlib_window_512"]),
                "apng_frame_decompression_failed",
            ),
            (
                make_apng_cmf_flg_check_probe(by_case["apng_fdat_zlib_window_4096"]),
                "apng_frame_decompression_failed",
            ),
            (
                make_apng_cinfo_too_large_probe(by_case["apng_fdat_zlib_window_32768"]),
                "apng_frame_decompression_failed",
            ),
        ]

        for png_bytes, expected_family in probes:
            decoded = decode_png_apng_zlib_header_policy(png_bytes)
            self.assertFalse(decoded["ok"], expected_family)
            self.assertEqual(expected_family, decoded["error_family"])

    def test_lab_report_closes_header_policy_subset_without_full_conformance_claim(self):
        report = run_png_apng_zlib_header_policy_lab(VALID_PROFILE_PATHS, GENERATED_ROOT)

        self.assertEqual("png_apng_zlib_header_policy_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(18, report["case_count"])
        self.assertEqual(18, report["case_success_count"])
        self.assertEqual(6, report["invalid_probe_count"])
        self.assertEqual(6, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["case_success_ratio"])
        self.assertEqual(1.0, report["metrics"]["invalid_probe_rejection_ratio"])
        self.assertEqual([1, 4, 7], report["metrics"]["zlib_cinfo_values_covered"])
        self.assertEqual(18, report["metrics"]["fdict_false_case_count"])
        self.assertIn("png_zlib_window_header_reconstruction", report["closed_states"])
        self.assertIn("apng_fdat_zlib_window_header_reconstruction", report["closed_states"])
        self.assertIn("png_apng_fdict_rejection", report["closed_states"])
        self.assertIn("full_apng_png_conformance", report["blocked_states"])
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])
        self.assertIn("package_runtime_lifecycle_integration", report["blocked_states"])

    def test_write_artifacts_creates_pngs_report_and_app_payload(self):
        report = run_png_apng_zlib_header_policy_lab(VALID_PROFILE_PATHS, GENERATED_ROOT)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = write_png_apng_zlib_header_policy_artifacts(root, report)

            self.assertTrue(paths["summary_json"].exists())
            self.assertTrue(paths["artifact_summary_json"].exists())
            self.assertTrue(paths["app_js"].exists())
            self.assertTrue(paths["artifact_app_js"].exists())
            self.assertTrue(paths["readme"].exists())
            self.assertEqual(18, len(list((paths["artifact_dir"] / "cases").glob("*.png"))))
            self.assertIn(
                "MECHAGOTCHI_PNG_APNG_ZLIB_HEADER_POLICY",
                paths["app_js"].read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
