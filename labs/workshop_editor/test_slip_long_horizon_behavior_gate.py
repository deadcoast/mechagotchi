import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


WORKSHOP_DIR = Path(__file__).resolve().parent
if str(WORKSHOP_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSHOP_DIR))

from slip_long_horizon_behavior_gate import (
    run_profile_long_horizon_probe,
    run_slip_long_horizon_behavior_gate_lab,
    write_slip_long_horizon_behavior_gate_artifacts,
)


VALID_PROFILE_PATHS = [
    ROOT / "data/slips/valid/slip_lcd_seed.json",
    ROOT / "data/slips/valid/slip_gray_stable.json",
    ROOT / "data/slips/valid/slip_amber_social.json",
]
GENERATED_ROOT = ROOT / "data/slips/multi_profile_generation_stage0"


class SLIPLongHorizonBehaviorGateTests(unittest.TestCase):
    def test_profile_probe_runs_selected_offspring_and_held_out_long_horizon(self):
        probe = run_profile_long_horizon_probe(
            VALID_PROFILE_PATHS[0],
            GENERATED_ROOT,
            candidate_limit=8,
            heldout_count=4,
            short_ticks=12,
            long_ticks=96,
            rng_seed=41,
        )

        self.assertTrue(probe["validation"]["ok"])
        self.assertTrue(probe["gate_started"])
        self.assertEqual("long_horizon_behavior_gate_v0", probe["policy"]["policy_id"])
        self.assertEqual(96, probe["long_horizon_ticks"])
        self.assertGreater(probe["held_out_candidate_count"], 0)
        self.assertEqual(
            96,
            probe["selected_offspring_long_horizon"]["switchboard"]["survival_ticks"],
        )
        self.assertLess(
            probe["selected_offspring_long_horizon"]["idle"]["survival_ticks"],
            probe["selected_offspring_long_horizon"]["switchboard"]["survival_ticks"],
        )
        self.assertEqual(
            probe["held_out_candidate_count"],
            probe["held_out_summary"]["switchboard_full_survival_count"],
        )
        self.assertEqual(
            probe["held_out_candidate_count"],
            probe["held_out_summary"]["idle_death_count"],
        )
        self.assertEqual(
            "not_collected",
            probe["manual_readability_calibration"]["status"],
        )
        self.assertTrue(
            probe["manual_readability_calibration"][
                "blocks_profile_weighted_evolution"
            ]
        )

    def test_lab_report_closes_long_horizon_without_claiming_manual_calibration_or_evolution(self):
        report = run_slip_long_horizon_behavior_gate_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
            candidate_limit=8,
            heldout_count=4,
            short_ticks=12,
            long_ticks=96,
            rng_seed=20260513,
        )

        self.assertEqual("slip_long_horizon_behavior_gate_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(3, report["long_horizon_success_count"])
        self.assertEqual(2, report["invalid_probe_rejected_count"])
        self.assertTrue(report["metrics"]["long_horizon_behavior_tests_specified"])
        self.assertFalse(report["metrics"]["manual_readability_calibration_ready"])
        self.assertEqual(1.0, report["metrics"]["mean_switchboard_survival_ratio"])
        self.assertLess(report["metrics"]["mean_idle_survival_ratio"], 0.2)
        self.assertGreater(report["metrics"]["mean_need_balance_delta_vs_idle"], 0.6)
        self.assertIn("held_out_long_horizon_behavior_tests", report["closed_states"])
        self.assertIn("manual_readability_calibration", report["blocked_states"])
        self.assertIn("profile_weighted_evolution", report["blocked_states"])
        self.assertIn(
            "persistent_multigeneration_lineage_runner",
            report["blocked_states"],
        )
        self.assertNotIn(
            "held_out_long_horizon_behavior_tests",
            report["blocked_states"],
        )

    def test_invalid_profile_and_mismatched_candidate_corpus_stop_before_gate(self):
        report = run_slip_long_horizon_behavior_gate_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
            candidate_limit=4,
            heldout_count=2,
            short_ticks=8,
            long_ticks=24,
            rng_seed=17,
        )

        invalids = report["invalid_probe_results"]
        self.assertEqual(2, len(invalids))
        for result in invalids:
            self.assertFalse(result["validation"]["ok"], result["probe_id"])
            self.assertFalse(result["gate_started"], result["probe_id"])

        families = {
            family
            for result in invalids
            for family in result["validation"]["error_families"]
        }
        self.assertIn("schema_version_unsupported", families)
        self.assertIn("slip_alignment", families)

    def test_write_artifacts_creates_summary_profile_payloads_and_app_data(self):
        report = run_slip_long_horizon_behavior_gate_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
            candidate_limit=4,
            heldout_count=2,
            short_ticks=8,
            long_ticks=24,
            rng_seed=29,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_slip_long_horizon_behavior_gate_artifacts(output_dir, report)

            summary_path = output_dir / "slip_long_horizon_behavior_gate_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue(
                (output_dir / "slip_lcd_seed_long_horizon_behavior_gate.json").exists()
            )
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (
                output_dir / "slip_long_horizon_behavior_gate_data.js"
            ).read_text(encoding="utf-8")
            self.assertIn("MECHAGOTCHI_SLIP_LONG_HORIZON_BEHAVIOR_GATE", app_data)


if __name__ == "__main__":
    unittest.main()
