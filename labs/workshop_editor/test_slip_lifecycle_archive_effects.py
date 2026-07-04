import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


WORKSHOP_DIR = Path(__file__).resolve().parent
if str(WORKSHOP_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSHOP_DIR))

from slip_lifecycle_archive_effects import (
    run_profile_effect_probe,
    run_slip_lifecycle_archive_effect_lab,
    write_slip_lifecycle_archive_effect_artifacts,
)


VALID_PROFILE_PATHS = [
    ROOT / "data/slips/valid/slip_lcd_seed.json",
    ROOT / "data/slips/valid/slip_gray_stable.json",
    ROOT / "data/slips/valid/slip_amber_social.json",
]
GENERATED_ROOT = ROOT / "data/slips/multi_profile_generation_stage0"


class SLIPLifecycleArchiveEffectTests(unittest.TestCase):
    def test_profile_probe_links_preview_lifecycle_and_archive_metrics(self):
        probe = run_profile_effect_probe(
            VALID_PROFILE_PATHS[0],
            GENERATED_ROOT,
            candidate_limit=8,
            lifecycle_ticks=16,
            archive_lifecycle_ticks=8,
            rng_seed=17,
        )

        self.assertTrue(probe["validation"]["ok"])
        self.assertEqual("slip_lcd_seed", probe["profile_id"])
        self.assertEqual("slip_lcd_seed", probe["lifecycle_effect"]["profile_id"])
        self.assertIn("social_pull", probe["preview_signals"])
        self.assertIn("mutation_pressure", probe["preview_signals"])
        self.assertGreater(probe["lifecycle_effect"]["survival_ticks"], 0)
        self.assertEqual(16, probe["lifecycle_effect"]["ticks_requested"])
        self.assertIn("play", probe["lifecycle_effect"]["action_counts"])
        self.assertGreater(probe["archive_effect"]["occupied_niches"], 0)
        self.assertIn(
            "behavior_neediness",
            probe["archive_effect"]["descriptor_names"],
        )
        self.assertIn(
            "lifecycle_survival",
            probe["archive_effect"]["descriptor_names"],
        )
        self.assertGreaterEqual(len(probe["preview_effect_fingerprint"]), 5)
        self.assertIn(
            "lifecycle_need_balance",
            probe["measured_effect_fingerprint"],
        )
        self.assertIn(
            "archive_qd_score",
            probe["measured_effect_fingerprint"],
        )

    def test_lab_report_measures_profiles_without_claiming_evolution(self):
        report = run_slip_lifecycle_archive_effect_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
            candidate_limit=8,
            lifecycle_ticks=16,
            archive_lifecycle_ticks=8,
            rng_seed=20260512,
        )

        self.assertEqual("slip_lifecycle_archive_effects_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(3, report["preview_request_success_count"])
        self.assertEqual(3, report["lifecycle_effect_count"])
        self.assertEqual(3, report["archive_effect_count"])
        self.assertEqual(2, report["invalid_probe_rejected_count"])
        self.assertTrue(
            report["metrics"]["preview_to_lifecycle_archive_effects_measured"]
        )
        self.assertEqual(3, report["metrics"]["distinct_preview_fingerprints"])
        self.assertGreaterEqual(
            report["metrics"]["distinct_lifecycle_fingerprints"],
            2,
        )
        self.assertGreaterEqual(
            report["metrics"]["distinct_archive_fingerprints"],
            1,
        )
        self.assertIn("slip_preview_lifecycle_effect_probe", report["closed_states"])
        self.assertIn("slip_preview_archive_effect_probe", report["closed_states"])
        self.assertIn(
            "invalid_profile_rejected_before_lifecycle_archive",
            report["closed_states"],
        )
        self.assertIn("profile_weighted_evolution", report["blocked_states"])
        self.assertNotIn("behavior_preview", report["blocked_states"])
        self.assertNotIn("mutation_preview_ui", report["blocked_states"])
        self.assertNotEqual("profile_weighted_evolution", report["decision"])

    def test_invalid_profile_and_mismatched_grid_rejected_before_effects(self):
        report = run_slip_lifecycle_archive_effect_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
            candidate_limit=4,
            lifecycle_ticks=8,
            archive_lifecycle_ticks=6,
            rng_seed=7,
        )

        invalids = report["invalid_probe_results"]
        self.assertEqual(2, len(invalids))
        for result in invalids:
            self.assertFalse(result["validation"]["ok"], result["probe_id"])
            self.assertFalse(result["effects_started"], result["probe_id"])
            self.assertEqual([], result["validation"]["preview_surfaces"])

        families = {
            family
            for result in invalids
            for family in result["validation"]["error_families"]
        }
        self.assertIn("schema_version_unsupported", families)
        self.assertIn("slip_alignment", families)

    def test_write_artifacts_creates_summary_profile_payloads_and_app_data(self):
        report = run_slip_lifecycle_archive_effect_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
            candidate_limit=4,
            lifecycle_ticks=8,
            archive_lifecycle_ticks=6,
            rng_seed=23,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_slip_lifecycle_archive_effect_artifacts(output_dir, report)

            summary_path = output_dir / "slip_lifecycle_archive_effects_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue(
                (output_dir / "slip_lcd_seed_lifecycle_archive_effects.json").exists()
            )
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (
                output_dir / "slip_lifecycle_archive_effects_data.js"
            ).read_text(encoding="utf-8")
            self.assertIn("MECHAGOTCHI_SLIP_LIFECYCLE_ARCHIVE_EFFECTS", app_data)


if __name__ == "__main__":
    unittest.main()
