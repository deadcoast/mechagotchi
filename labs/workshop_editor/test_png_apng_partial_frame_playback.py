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

from png_apng_partial_frame_playback import (
    PLAYBACK_SCENARIO_IDS,
    decode_apng_partial_frame_playback,
    export_apng_partial_frame_playback_cases,
    make_invalid_blend_probe,
    make_invalid_dispose_probe,
    make_missing_default_idat_probe,
    make_missing_frame_data_probe,
    make_out_of_bounds_probe,
    run_apng_partial_frame_playback_lab,
    write_apng_partial_frame_playback_artifacts,
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


class APNGPartialFramePlaybackTests(unittest.TestCase):
    def test_export_builds_partial_frame_scenarios_with_expected_pixel_hashes(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        cases = export_apng_partial_frame_playback_cases(grid, profile)
        scenario_ids = [case["scenario_id"] for case in cases]

        self.assertEqual(PLAYBACK_SCENARIO_IDS, scenario_ids)
        for case in cases:
            decoded = decode_apng_partial_frame_playback(case["png_bytes"])
            self.assertEqual(case["expected_display_hashes"], decoded["display_hashes"])
            self.assertEqual(case["expected_after_dispose_hashes"], decoded["after_dispose_hashes"])
            self.assertEqual(case["expected_final_hash"], decoded["final_output_hash"])
            self.assertTrue(any(not frame["full_canvas"] for frame in decoded["frames"]))

    def test_decoder_applies_source_and_over_blend_differently(self):
        profile = load_profile(VALID_PROFILE_PATHS[1])
        grid = first_grid_for(profile)
        cases = {
            case["scenario_id"]: case
            for case in export_apng_partial_frame_playback_cases(grid, profile)
        }

        source = decode_apng_partial_frame_playback(cases["source_patch_dispose_none"]["png_bytes"])
        over = decode_apng_partial_frame_playback(cases["over_patch_dispose_none"]["png_bytes"])

        self.assertNotEqual(source["display_hashes"][1], over["display_hashes"][1])
        self.assertEqual(0, source["frames"][1]["blend_op"])
        self.assertEqual(1, over["frames"][1]["blend_op"])
        self.assertEqual(1, source["frames"][1]["x_offset"])
        self.assertEqual(1, over["frames"][1]["x_offset"])

    def test_decoder_applies_background_and_previous_disposal(self):
        profile = load_profile(VALID_PROFILE_PATHS[2])
        grid = first_grid_for(profile)
        cases = {
            case["scenario_id"]: case
            for case in export_apng_partial_frame_playback_cases(grid, profile)
        }

        background = decode_apng_partial_frame_playback(cases["background_disposal"]["png_bytes"])
        previous = decode_apng_partial_frame_playback(cases["previous_disposal"]["png_bytes"])

        self.assertEqual(1, background["frames"][1]["dispose_op"])
        self.assertEqual(2, previous["frames"][1]["dispose_op"])
        self.assertNotEqual(background["display_hashes"][1], background["after_dispose_hashes"][1])
        self.assertNotEqual(previous["display_hashes"][1], previous["after_dispose_hashes"][1])
        self.assertEqual(previous["display_hashes"][0], previous["after_dispose_hashes"][1])

    def test_decoder_rejects_invalid_partial_frame_bounds_control_and_data(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        reference = export_apng_partial_frame_playback_cases(grid, profile)[0]

        probes = [
            (make_out_of_bounds_probe(reference["png_bytes"]), "apng_frame_bounds_invalid"),
            (make_invalid_dispose_probe(reference["png_bytes"]), "apng_dispose_op_invalid"),
            (make_invalid_blend_probe(reference["png_bytes"]), "apng_blend_op_invalid"),
            (make_missing_default_idat_probe(reference["png_bytes"]), "apng_idat_missing"),
            (make_missing_frame_data_probe(reference["png_bytes"]), "apng_frame_data_missing"),
        ]

        for png_bytes, family in probes:
            decoded = decode_apng_partial_frame_playback(png_bytes)
            self.assertFalse(decoded["ok"])
            self.assertIn(family, decoded["error_families"])

    def test_lab_report_closes_partial_frame_subset_without_full_conformance_claim(self):
        report = run_apng_partial_frame_playback_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("apng_partial_frame_playback_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(12, report["playback_case_count"])
        self.assertEqual(12, report["playback_case_success_count"])
        self.assertEqual(5, report["invalid_probe_count"])
        self.assertEqual(5, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["playback_case_success_rate"])
        self.assertIn("apng_partial_frame_offset_playback", report["closed_states"])
        self.assertIn("apng_blend_source_over_playback", report["closed_states"])
        self.assertIn("apng_dispose_background_previous_playback", report["closed_states"])
        self.assertIn("full_apng_png_conformance", report["blocked_states"])
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])

    def test_write_artifacts_creates_apngs_report_and_app_payload(self):
        report = run_apng_partial_frame_playback_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_apng_partial_frame_playback_artifacts(output_dir, report)

            summary_path = output_dir / "apng_partial_frame_playback_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "cases" / "slip_lcd_seed_source_patch_dispose_none.png").exists())
            self.assertTrue((output_dir / "cases" / "slip_lcd_seed_previous_disposal.png").exists())
            app_data = (output_dir / "apng_partial_frame_playback_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_APNG_PARTIAL_FRAME_PLAYBACK", app_data)


if __name__ == "__main__":
    unittest.main()
