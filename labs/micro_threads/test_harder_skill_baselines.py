"""Pins for cycle 26 P4: the harder baselines N3 named and did not run.

DR 0051 kept condition E (`qtable_policy`) on skill **+55.459% against
uniform random** and recorded, in its own "does NOT do" list, that the
uniform baseline is a weak opponent; it also recorded that F's stump
baseline gets a full-sample oracle while the tree runs online — an
asymmetry that runs *against* the tree. P4 runs both harder
comparisons as a NEW artifact (DR 0053: the committed measurement is
reproduced or superseded, never improved):

* **E vs the incumbent frozen reactive rule** — the switchboard's own
  frozen decision on the same replayed states, scored by the same
  empirical-regret statistic, judged at the same documented 5% bar.
* **F vs a like-for-like ONLINE stump** — the depth-1 stump's
  recommendation computed from only the records seen so far within
  each lifecycle (the same online footing the tree has), valued under
  the same full-sample means as the committed framing.

The collector is a superset of N3's (same harness, same seeds, same
order) and must REPRODUCE all three committed skill numbers exactly at
the committed budget before either harder statistic is trusted.
**No roster changes in any branch, pre-registered**: DR 0051's keep
and drops were by the documented rule and stand; this artifact answers
the harder questions and its findings become dated notes beside
DR 0051.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from harder_skill_baselines import (  # noqa: E402
    ARTIFACT_ID,
    PRE_REGISTERED_RULE,
    PRE_RUN_PREDICTION,
    build_harder_baselines_report,
    judge_harder_baselines,
    online_stump_recommendation,
    write_harder_baselines_artifacts,
)


class PreRegistrationTests(unittest.TestCase):
    def test_the_rule_names_the_bar_and_the_no_roster_change_clause(self):
        rule = PRE_REGISTERED_RULE.lower()
        self.assertIn("pre-registered", rule)
        self.assertIn("5%", PRE_REGISTERED_RULE)
        self.assertIn("no roster change", rule)

    def test_the_prediction_is_recorded_before_the_run(self):
        prediction = PRE_RUN_PREDICTION.lower()
        self.assertIn("qtable", prediction)
        self.assertIn("stump", prediction)


class JudgeTests(unittest.TestCase):
    def test_e_beats_the_rule_only_over_the_documented_bar(self):
        judged = judge_harder_baselines(
            q_vs_rule_pct=12.0, tree_vs_online_stump_pct=0.0,
            keep_threshold_pct=5.0,
        )
        self.assertEqual(judged["e_verdict"], "beats_incumbent_rule")

    def test_e_within_the_bar_is_indistinguishable(self):
        judged = judge_harder_baselines(
            q_vs_rule_pct=2.0, tree_vs_online_stump_pct=0.0,
            keep_threshold_pct=5.0,
        )
        self.assertEqual(judged["e_verdict"], "indistinguishable_from_rule")

    def test_e_under_the_bar_loses(self):
        judged = judge_harder_baselines(
            q_vs_rule_pct=-9.0, tree_vs_online_stump_pct=0.0,
            keep_threshold_pct=5.0,
        )
        self.assertEqual(judged["e_verdict"], "loses_to_incumbent_rule")

    def test_f_drop_holds_under_the_bar(self):
        judged = judge_harder_baselines(
            q_vs_rule_pct=0.0, tree_vs_online_stump_pct=3.0,
            keep_threshold_pct=5.0,
        )
        self.assertEqual(judged["f_verdict"], "drop_holds_like_for_like")

    def test_f_drop_overturned_over_the_bar_is_a_first_class_finding(self):
        judged = judge_harder_baselines(
            q_vs_rule_pct=0.0, tree_vs_online_stump_pct=8.5,
            keep_threshold_pct=5.0,
        )
        self.assertEqual(judged["f_verdict"], "drop_overturned_like_for_like")

    def test_no_branch_changes_the_roster(self):
        for e_pct in (-20.0, 0.0, 20.0):
            for f_pct in (-20.0, 20.0):
                judged = judge_harder_baselines(
                    q_vs_rule_pct=e_pct,
                    tree_vs_online_stump_pct=f_pct,
                    keep_threshold_pct=5.0,
                )
                self.assertFalse(judged["roster_changed"])

    def test_a_non_positive_bar_is_refused(self):
        with self.assertRaises(ValueError):
            judge_harder_baselines(
                q_vs_rule_pct=0.0, tree_vs_online_stump_pct=0.0,
                keep_threshold_pct=0.0,
            )


class OnlineStumpTests(unittest.TestCase):
    def test_the_stump_is_cold_before_two_actions_are_seen(self):
        running = {}
        self.assertIsNone(online_stump_recommendation(running, "hungry"))
        running = {("hungry", "feed"): [0.5]}
        self.assertIsNone(online_stump_recommendation(running, "hungry"))

    def test_the_stump_recommends_the_best_running_mean(self):
        running = {
            ("hungry", "feed"): [0.8, 0.9],
            ("hungry", "play"): [0.4],
        }
        self.assertEqual(
            online_stump_recommendation(running, "hungry"), "feed"
        )

    def test_the_stump_only_sees_its_own_side(self):
        running = {
            ("hungry", "feed"): [0.9],
            ("sated", "play"): [1.0],
            ("sated", "sleep"): [0.2],
        }
        self.assertEqual(online_stump_recommendation(running, "sated"), "play")
        self.assertIsNone(online_stump_recommendation(running, "hungry"))


class ReportTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        # A reduced budget keeps the suite fast; the committed-number
        # instrument gate binds only at the committed budget, which the
        # real run uses (main()).
        cls.report = build_harder_baselines_report(
            lifecycles_per_keeper=2, ticks=60
        )

    def test_report_carries_every_required_artifact_key(self):
        for key in (
            "artifact_id",
            "status",
            "date",
            "purpose",
            "source_artifacts",
            "parameters",
            "metrics",
            "closed_states",
            "blocked_states",
            "decision",
            "next_research_step",
        ):
            self.assertIn(key, self.report)
        self.assertEqual(self.report["artifact_id"], ARTIFACT_ID)

    def test_the_instrument_gate_records_its_applicability(self):
        check = self.report["metrics"]["instrument_check"]
        self.assertFalse(check["applicable"])
        self.assertIn("committed", json.dumps(check))

    def test_the_verdicts_are_in_the_pre_registered_vocabulary(self):
        decision = self.report["decision"]
        self.assertIn(
            decision["e_verdict"],
            (
                "beats_incumbent_rule",
                "indistinguishable_from_rule",
                "loses_to_incumbent_rule",
            ),
        )
        self.assertIn(
            decision["f_verdict"],
            ("drop_holds_like_for_like", "drop_overturned_like_for_like"),
        )
        self.assertFalse(decision["roster_changed"])
        self.assertEqual(decision["rule"], PRE_REGISTERED_RULE)

    def test_source_artifact_paths_are_repo_relative(self):
        for path in self.report["source_artifacts"]:
            self.assertFalse(Path(path).is_absolute())
            self.assertNotIn("\\", path)

    def test_artifact_round_trips_as_json(self):
        with tempfile.TemporaryDirectory() as directory:
            written = write_harder_baselines_artifacts(
                directory, self.report
            )
            self.assertEqual(len(written), 1)
            reloaded = json.loads(written[0].read_text(encoding="utf-8"))
        self.assertEqual(reloaded["artifact_id"], ARTIFACT_ID)


if __name__ == "__main__":
    unittest.main()
