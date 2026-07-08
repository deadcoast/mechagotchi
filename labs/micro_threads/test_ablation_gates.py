import json
import tempfile
import unittest
from pathlib import Path

from ablation_gates import (
    build_ablation_gate_report,
    keeper_respond,
    run_ablation_conditions,
    run_dependent_lifecycle,
    write_ablation_gate_artifacts,
)

LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]


def _seed_grid() -> dict:
    import sys

    grid_genome = REPO_ROOT / "labs" / "grid_genome"
    if str(grid_genome) not in sys.path:
        sys.path.insert(0, str(grid_genome))
    from corpus_builder import build_seed_grids

    return build_seed_grids()[0]


class DependentModeTests(unittest.TestCase):
    def test_keeper_respond_reacts_to_the_beg_display(self):
        import random

        state = {"hunger": 0.7, "energy": 0.6, "bond": 0.6, "age_ticks": 5}
        # Attentive answers a beg almost always; neglectful almost never.
        attentive_feeds = sum(
            1
            for seed in range(100)
            if keeper_respond("attentive", state, True, random.Random(seed))
            == "feed"
        )
        neglectful_feeds = sum(
            1
            for seed in range(100)
            if keeper_respond("neglectful", state, True, random.Random(seed))
            == "feed"
        )
        self.assertGreater(attentive_feeds, 80)
        self.assertLess(neglectful_feeds, 20)

    def test_dependent_lifecycles_are_deterministic(self):
        grid = _seed_grid()
        first = run_dependent_lifecycle(
            grid, "attentive", ticks=80, rng_seed=5, condition="full_fleet"
        )
        second = run_dependent_lifecycle(
            grid, "attentive", ticks=80, rng_seed=5, condition="full_fleet"
        )
        self.assertEqual(first, second)

    def test_welfare_charges_death_against_requested_ticks(self):
        grid = _seed_grid()
        summary = run_dependent_lifecycle(
            grid, "neglectful", ticks=200, rng_seed=5, condition="frozen"
        )
        # Neglect kills early in dependent mode; welfare must reflect it.
        self.assertLess(summary["survival_ticks"], 200)
        self.assertLess(summary["welfare"], 0.3)

    def test_rules_only_is_a_valid_condition(self):
        grid = _seed_grid()
        summary = run_dependent_lifecycle(
            grid, "attentive", ticks=60, rng_seed=5, condition="rules_only"
        )
        self.assertIn("welfare", summary)


class ConditionTests(unittest.TestCase):
    def test_pilot_conditions_cover_the_documented_set(self):
        conditions = run_ablation_conditions(lifecycles_per_keeper=2, ticks=40)
        names = {entry["condition"] for entry in conditions["conditions"]}
        self.assertIn("rules_only", names)
        self.assertIn("frozen", names)
        self.assertIn("full_fleet", names)
        self.assertIn("minus_hunger_forecast", names)
        self.assertIn("minus_hidden_mood_hmm", names)
        # rules_only + frozen + full + 11 remove-one conditions.
        self.assertEqual(14, len(names))


class ReportTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = build_ablation_gate_report(
            lifecycles_per_keeper=3, ticks=60
        )

    def test_report_shape(self):
        for key in [
            "artifact_id",
            "status",
            "date",
            "purpose",
            "source_artifacts",
            "metrics",
            "closed_states",
            "blocked_states",
            "decision",
            "next_research_step",
        ]:
            self.assertIn(key, self.report)
        self.assertEqual("ablation_gates_stage0", self.report["artifact_id"])
        self.assertEqual(self.report, json.loads(json.dumps(self.report)))

    def test_the_documented_gates_are_evaluated(self):
        gates = self.report["metrics"]["gates"]
        self.assertIn("full_vs_rules_only_welfare_pct", gates)
        self.assertIn("full_vs_rules_only_meets_15pct", gates)
        self.assertIn("fleet_vs_frozen_welfare_pct", gates)

    def test_every_thread_has_a_keep_or_drop_verdict_with_evidence(self):
        verdicts = self.report["metrics"]["thread_verdicts"]
        self.assertEqual(11, len(verdicts))
        for verdict in verdicts:
            self.assertIn(verdict["decision"], ["keep", "drop"])
            self.assertIn("welfare_removal_cost_pct", verdict)
            self.assertIn("skill_metric", verdict)
        by_name = {verdict["thread"]: verdict for verdict in verdicts}
        # The documented <5% rule applied without sentiment: the two
        # thin-margin predictors are DROPPED on their own D2 numbers.
        self.assertEqual("drop", by_name["boredom_novelty"]["decision"])
        self.assertEqual("drop", by_name["attention_forecast"]["decision"])
        self.assertEqual("keep", by_name["hunger_forecast"]["decision"])
        self.assertEqual("keep", by_name["hidden_mood_hmm"]["decision"])

    def test_write_artifacts_round_trips(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            write_ablation_gate_artifacts(output_dir, self.report)
            written = output_dir / "ablation_gates_stage0.json"
            self.assertTrue(written.exists())
            self.assertEqual(
                self.report,
                json.loads(written.read_text(encoding="utf-8")),
            )


if __name__ == "__main__":
    unittest.main()
