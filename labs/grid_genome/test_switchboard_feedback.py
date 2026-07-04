import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LIFECYCLE = ROOT / "labs" / "lifecycle_sim"
for path in [ROOT, LIFECYCLE]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from switchboard_feedback import (  # noqa: E402
    run_feedback_episode,
    run_switchboard_feedback_stress_suite,
    run_switchboard_feedback_lab,
    write_switchboard_feedback_stress_artifacts,
    write_switchboard_feedback_artifacts,
)


class SwitchboardFeedbackTests(unittest.TestCase):
    def test_feedback_episode_updates_action_rewards_from_lifecycle_outcomes(self):
        episode = run_feedback_episode(ticks=24, feedback_enabled=True, rng_seed=20260512)

        self.assertEqual("feedback_switchboard", episode["policy"])
        self.assertGreater(episode["reward_update_count"], 0)
        self.assertGreater(episode["survival_ticks"], 0)
        self.assertTrue(episode["final_action_reward_means"])
        self.assertNotEqual(
            episode["initial_action_reward_means"],
            episode["final_action_reward_means"],
        )
        self.assertIn("observed_reward", episode["history"][0])

    def test_frozen_episode_records_rewards_without_learning_from_them(self):
        episode = run_feedback_episode(ticks=24, feedback_enabled=False, rng_seed=20260512)

        self.assertEqual("frozen_switchboard", episode["policy"])
        self.assertEqual(0, episode["reward_update_count"])
        self.assertEqual(
            episode["initial_action_reward_means"],
            episode["final_action_reward_means"],
        )

    def test_feedback_lab_compares_adaptive_and_frozen_switchboards(self):
        report = run_switchboard_feedback_lab(ticks=48, rng_seed=20260512)

        self.assertEqual("switchboard_lifecycle_feedback_stage0", report["lab_id"])
        self.assertIn("feedback_switchboard", report["episodes"])
        self.assertIn("frozen_switchboard", report["episodes"])
        self.assertGreater(
            report["summary"]["feedback_reward_update_count"],
            report["summary"]["frozen_reward_update_count"],
        )
        self.assertGreaterEqual(
            report["summary"]["feedback_need_balance"],
            report["summary"]["frozen_need_balance"],
        )
        self.assertIn(report["decision"]["status"], {"prototype", "watch"})

    def test_feedback_corrects_stale_idle_memory_and_beats_frozen_baseline(self):
        report = run_switchboard_feedback_lab(ticks=48, rng_seed=20260512)

        summary = report["summary"]
        self.assertGreater(summary["need_balance_delta"], 0)
        self.assertGreaterEqual(summary["survival_delta"], 0)
        feedback = report["episodes"]["feedback_switchboard"]
        frozen = report["episodes"]["frozen_switchboard"]
        # The frozen policy keeps acting on the stale idle-favoring reward
        # memory; the feedback policy corrects the idle mean from observed
        # lifecycle rewards and re-engages with active care actions.
        self.assertLess(
            feedback["action_counts"]["idle"],
            frozen["action_counts"]["idle"],
        )
        self.assertGreater(
            feedback["action_counts"]["play"],
            frozen["action_counts"]["play"],
        )
        self.assertEqual("prototype", report["decision"]["status"])

    def test_feedback_delta_is_deterministic_across_repeat_runs(self):
        first = run_switchboard_feedback_lab(ticks=48, rng_seed=20260512)
        second = run_switchboard_feedback_lab(ticks=48, rng_seed=20260512)

        self.assertEqual(first["summary"], second["summary"])

    def test_write_switchboard_feedback_artifacts_creates_report(self):
        report = run_switchboard_feedback_lab(ticks=12, rng_seed=7)
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_switchboard_feedback_artifacts(output_dir, report)

            report_path = output_dir / "switchboard_lifecycle_feedback_stage0.json"
            self.assertTrue(report_path.exists())
            loaded = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual("switchboard_lifecycle_feedback_stage0", loaded["lab_id"])

    def test_stress_suite_compares_feedback_and_frozen_across_dynamic_scenarios(self):
        report = run_switchboard_feedback_stress_suite(ticks=60, rng_seed=20260512)

        self.assertEqual("switchboard_feedback_dynamic_stress_stage0", report["lab_id"])
        self.assertGreaterEqual(report["summary"]["scenario_count"], 3)
        self.assertEqual(
            report["summary"]["scenario_count"],
            len(report["scenarios"]),
        )
        self.assertIn("feedback_better_need_balance_count", report["summary"])
        self.assertIn("mean_need_balance_delta", report["summary"])
        for scenario in report["scenarios"]:
            self.assertIn("feedback_switchboard", scenario["episodes"])
            self.assertIn("frozen_switchboard", scenario["episodes"])
            self.assertGreater(
                scenario["episodes"]["feedback_switchboard"]["reward_update_count"],
                scenario["episodes"]["frozen_switchboard"]["reward_update_count"],
            )
            self.assertGreater(len(scenario["events_applied"]), 0)

    def test_write_switchboard_feedback_stress_artifacts_creates_report(self):
        report = run_switchboard_feedback_stress_suite(ticks=24, rng_seed=7)
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_switchboard_feedback_stress_artifacts(output_dir, report)

            report_path = output_dir / "switchboard_feedback_dynamic_stress_stage0.json"
            self.assertTrue(report_path.exists())
            loaded = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual("switchboard_feedback_dynamic_stress_stage0", loaded["lab_id"])


if __name__ == "__main__":
    unittest.main()
