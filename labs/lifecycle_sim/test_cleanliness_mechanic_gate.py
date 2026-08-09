"""Pins for cycle 26 P3: the cleanliness mechanic, gated.

DR 0048 measured the gap precisely: *"there is no clean action — and no
state accumulates dirt... it needs a need, a decay, an action that
answers it, and its interaction with the switchboard policy and the
reward function."* The seam exists (opt-in, byte-identical off, every
parameter derived from the incumbent engine); this gate decides whether
it may SHIP, with the verdicts the charter names first-class:

* ``withhold`` — a structural failure (no decay, an unresponsive verb).
* ``blocked_on_mechanic`` — the charter's own refusal: the smallest
  honest mechanic is indistinguishable from the incumbent engine at the
  documented budgets (a need nobody can measure is not a need).
* ``refuse_as_lethal_cosmetic`` — the opposite failure: a cosmetic axis
  that kills the companion or moves the documented welfare statistic
  beyond the D6 ablation bar has outgrown "smallest".
* ``adopt`` — every gate holds.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from cleanliness_mechanic_gate import (  # noqa: E402
    ARTIFACT_ID,
    D6_WELFARE_BAR,
    PRE_REGISTERED_RULE,
    PRE_RUN_PREDICTION,
    build_cleanliness_mechanic_report,
    judge_mechanic,
    write_cleanliness_mechanic_artifacts,
)


class PreRegistrationTests(unittest.TestCase):
    def test_the_rule_names_every_verdict(self):
        rule = PRE_REGISTERED_RULE.lower()
        self.assertIn("pre-registered", rule)
        self.assertIn("blocked_on_mechanic", rule)
        self.assertIn("refuse_as_lethal_cosmetic", rule)
        self.assertIn("withhold", rule)

    def test_a_prediction_is_recorded_before_the_run(self):
        prediction = PRE_RUN_PREDICTION.lower()
        self.assertIn("adopt", prediction)
        self.assertIn("absorb", prediction)

    def test_the_welfare_bar_is_the_documented_d6_bar(self):
        self.assertEqual(D6_WELFARE_BAR, 0.05)


class JudgeTests(unittest.TestCase):
    def _judge(self, **overrides):
        base = dict(
            need_decays=True,
            keeper_response=0.32,
            incumbent_response_floor=0.0685,
            clean_answers=True,
            consequence_measurable=True,
            survival_unchanged=True,
            welfare_impact=0.001,
        )
        base.update(overrides)
        return judge_mechanic(**base)

    def test_a_mechanic_passing_every_gate_is_adopted(self):
        self.assertEqual(self._judge()["verdict"], "adopt")

    def test_a_need_that_does_not_decay_is_withheld(self):
        judged = self._judge(need_decays=False)
        self.assertEqual(judged["verdict"], "withhold")
        self.assertIn("G1_need_decays", judged["failed_gates"])

    def test_an_unresponsive_verb_is_withheld(self):
        judged = self._judge(keeper_response=0.01)
        self.assertEqual(judged["verdict"], "withhold")
        self.assertIn("G2_keeper_responsive", judged["failed_gates"])

    def test_a_verb_that_does_not_answer_is_withheld(self):
        judged = self._judge(clean_answers=False)
        self.assertEqual(judged["verdict"], "withhold")
        self.assertIn("G4_clean_answers", judged["failed_gates"])

    def test_an_unmeasurable_consequence_is_blocked_on_mechanic(self):
        judged = self._judge(consequence_measurable=False)
        self.assertEqual(judged["verdict"], "blocked_on_mechanic")
        self.assertIn("G3a_consequence_measurable", judged["failed_gates"])

    def test_a_lethal_cosmetic_is_refused(self):
        judged = self._judge(survival_unchanged=False)
        self.assertEqual(judged["verdict"], "refuse_as_lethal_cosmetic")
        self.assertIn("G3b_survival_unchanged", judged["failed_gates"])

    def test_a_welfare_bust_is_refused(self):
        judged = self._judge(welfare_impact=0.12)
        self.assertEqual(judged["verdict"], "refuse_as_lethal_cosmetic")
        self.assertIn("G3b_welfare_bounded", judged["failed_gates"])

    def test_the_refusals_outrank_the_withholdings(self):
        judged = self._judge(need_decays=False, survival_unchanged=False)
        self.assertEqual(judged["verdict"], "refuse_as_lethal_cosmetic")

    def test_a_negative_floor_is_refused(self):
        with self.assertRaises(ValueError):
            self._judge(incumbent_response_floor=-0.1)


class ReportTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = build_cleanliness_mechanic_report()

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

    def test_the_instrument_reproduced_the_committed_episodes(self):
        check = self.report["metrics"]["instrument_check"]
        self.assertTrue(check["switchboard_reproduced"])
        self.assertTrue(check["idle_reproduced"])
        self.assertEqual(check["committed_need_balance"], 0.789129)

    def test_the_keeper_floor_is_the_committed_n5_floor(self):
        check = self.report["metrics"]["instrument_check"]
        self.assertEqual(check["committed_keeper_floor"], 0.0685)

    def test_the_verdict_is_in_the_pre_registered_vocabulary(self):
        self.assertIn(
            self.report["decision"]["verdict"],
            (
                "adopt",
                "withhold",
                "blocked_on_mechanic",
                "refuse_as_lethal_cosmetic",
            ),
        )
        self.assertEqual(self.report["decision"]["rule"], PRE_REGISTERED_RULE)

    def test_the_absorption_finding_is_recorded_either_way(self):
        # The attentive keeper's care may absorb the dirt pressure
        # entirely — a finding about the mechanic's fairness, recorded
        # whatever it measures.
        self.assertIn(
            "care_absorbs_dirt_pressure", self.report["metrics"]["findings"]
        )

    def test_source_artifact_paths_are_repo_relative(self):
        for path in self.report["source_artifacts"]:
            self.assertFalse(Path(path).is_absolute())
            self.assertNotIn("\\", path)

    def test_artifact_round_trips_as_json(self):
        with tempfile.TemporaryDirectory() as directory:
            written = write_cleanliness_mechanic_artifacts(
                directory, self.report
            )
            self.assertEqual(len(written), 1)
            reloaded = json.loads(written[0].read_text(encoding="utf-8"))
        self.assertEqual(reloaded["artifact_id"], ARTIFACT_ID)


if __name__ == "__main__":
    unittest.main()
