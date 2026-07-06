import json
import tempfile
import unittest
from pathlib import Path

from switchboard_ablation import (
    ABLATION_CONDITIONS,
    USER_MODELS,
    build_switchboard_ablation_report,
    write_switchboard_ablation_artifacts,
)


class SwitchboardAblationTests(unittest.TestCase):
    """T19: RUN TWO's remove-one ablation at Stage 0 scale."""

    @classmethod
    def setUpClass(cls):
        cls.report = build_switchboard_ablation_report(ticks=48)

    def test_conditions_are_slip_authored_via_learning_switches(self):
        names = [c["condition"] for c in ABLATION_CONDITIONS]
        self.assertEqual(
            [
                "full",
                "minus_recent_interaction_ewma",
                "minus_hidden_mood_estimator",
                "minus_action_preference_bandit",
                "minus_mutation_risk_scorer",
                "rules_only",
            ],
            names,
        )
        for condition in ABLATION_CONDITIONS:
            profile = condition["profile"]
            if condition["condition"] == "full":
                self.assertNotIn("learning_switches", profile)
            else:
                self.assertEqual("0.2.0", profile["slip_version"])
                self.assertTrue(
                    all(v is False for v in profile["learning_switches"].values())
                )

    def test_the_og_user_models_all_run(self):
        self.assertEqual(
            ["attentive", "neglectful", "erratic", "punitive", "exploratory"],
            list(USER_MODELS),
        )
        episodes = self.report["episodes"]
        self.assertEqual(30, len(episodes))  # 5 users x 6 conditions
        for episode in episodes:
            self.assertGreater(episode["survival_ticks"], 0)
            self.assertIn("need_balance", episode)
            self.assertIn("action_counts", episode)

    def test_keep_gate_derives_from_measured_deltas(self):
        gate = self.report["keep_gate"]
        for thread, verdict in gate.items():
            self.assertIn(verdict["decision"], ("keep", "dead_weight"))
            self.assertIsInstance(verdict["worst_need_balance_decline_pct"], float)
            expected = (
                "keep"
                if verdict["worst_need_balance_decline_pct"] >= 5.0
                and not verdict["survival_improved_when_removed"]
                else "dead_weight"
            )
            self.assertEqual(expected, verdict["decision"], thread)

    def test_full_vs_rules_only_headline_is_measured(self):
        headline = self.report["summary"]["full_vs_rules_only"]
        self.assertIn("need_balance_delta_pct_by_user", headline)
        self.assertEqual(5, len(headline["need_balance_delta_pct_by_user"]))
        self.assertIsInstance(headline["full_beats_rules_only"], bool)

    def test_deterministic(self):
        self.assertEqual(
            self.report, build_switchboard_ablation_report(ticks=48)
        )

    def test_artifacts_write(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir)
            write_switchboard_ablation_artifacts(output, self.report)
            artifact = output / "switchboard_ablation_stage0.json"
            self.assertTrue(artifact.exists())
            loaded = json.loads(artifact.read_text(encoding="utf-8"))
            self.assertEqual("switchboard_ablation_stage0", loaded["artifact_id"])


if __name__ == "__main__":
    unittest.main()
