"""Pins for cycle 26 P2: `happiness` — a CHOSEN definition, gated.

`validity-research.md` §1.17 names `happiness` a VISIBLE companion
state axis; M5 measured that the engine has no source for it and
DR 0048 put it out of scope *pending a documented definition*. P2 is
that gate, the N5 → O2 pattern run end to end: candidates declared
CHOSEN up front, gates and prediction pre-registered before the run,
refusal first-class and reachable for every candidate — plus one gate
N5 did not need: **G5, distinct-from-shown**. A happiness that is
byte-identical, tick for tick, to a readout already on the player's
screen under another name (bond, or the health readout) is one engine
number wearing two visible names — the honest-labelling law violated
in the opposite direction from a euphemism — and earns
``refuse_as_duplicate``.

Selection among eligible candidates is pre-registered too: the LOWEST
reading on the neglected corpse (N5's own refusal logic — what the bar
shows at death measures the label's honesty — made into the selection
statistic), ties broken toward the definition that reads fewer engine
fields.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from happiness_definition_gate import (  # noqa: E402
    ARTIFACT_ID,
    CANDIDATES,
    KEEPER_ACTIONS,
    PRE_REGISTERED_RULE,
    PRE_RUN_PREDICTION,
    build_happiness_definition_report,
    judge_candidate,
    need_balance_mirror,
    social_warmth,
    write_happiness_definition_artifacts,
)


class CandidateDeclarationTests(unittest.TestCase):
    def test_the_three_candidates_are_carried(self):
        self.assertEqual(
            sorted(CANDIDATES),
            ["bond_rename", "need_balance", "social_warmth"],
        )

    def test_every_candidate_is_declared_chosen_and_names_what_it_reads(self):
        for name, spec in CANDIDATES.items():
            self.assertTrue(spec["chosen"], name)
            self.assertTrue(spec["reads"], name)

    def test_the_rule_and_prediction_are_pre_registered(self):
        rule = PRE_REGISTERED_RULE.lower()
        self.assertIn("pre-registered", rule)
        self.assertIn("refuse_as_euphemism", rule)
        self.assertIn("refuse_as_duplicate", rule)
        prediction = PRE_RUN_PREDICTION.lower()
        self.assertIn("bond_rename", prediction)
        self.assertIn("social_warmth", prediction)


class ValueFunctionTests(unittest.TestCase):
    def test_social_warmth_is_the_mean_of_the_interaction_window(self):
        self.assertEqual(social_warmth([1, 0, 1, 1, 0]), 0.6)
        self.assertEqual(social_warmth([0, 0, 0, 0, 0]), 0.0)
        self.assertEqual(social_warmth([1, 1, 1, 1, 1]), 1.0)

    def test_social_warmth_of_an_empty_window_is_zero(self):
        self.assertEqual(social_warmth([]), 0.0)

    def test_need_balance_mirror_matches_the_stage0_formula(self):
        # 1 - mean(|value - target|) over the five axes, clamped.
        snap = {
            "hunger": 0.34,
            "energy": 0.68,
            "stress": 0.18,
            "bond": 0.72,
            "grid_stability": 0.92,
        }
        self.assertEqual(need_balance_mirror(snap), 1.0)


class JudgeTests(unittest.TestCase):
    def _judge(self, **overrides):
        base = dict(
            candidate="social_warmth",
            reads=["recent_interactions"],
            keeper_action_response={"feed": 0.083333, "play": 0.083333},
            incumbent_response_floor=0.0685,
            distress_relief=0.2,
            care_coupled=True,
            duplicate_of=None,
        )
        base.update(overrides)
        return judge_candidate(**base)

    def test_a_candidate_passing_every_gate_is_eligible(self):
        self.assertEqual(self._judge()["verdict"], "eligible")

    def test_a_flat_candidate_is_withheld(self):
        judged = self._judge(
            keeper_action_response={"feed": 0.001, "play": 0.001}
        )
        self.assertEqual(judged["verdict"], "withhold")
        self.assertIn("G2_keeper_responsive", judged["failed_gates"])

    def test_an_uncoupled_candidate_is_withheld(self):
        judged = self._judge(care_coupled=False)
        self.assertEqual(judged["verdict"], "withhold")
        self.assertIn("G3_care_coupled", judged["failed_gates"])

    def test_relief_that_does_not_raise_the_bar_is_a_euphemism(self):
        judged = self._judge(distress_relief=0.0)
        self.assertEqual(judged["verdict"], "refuse_as_euphemism")
        self.assertIn("G4_honest_label", judged["failed_gates"])

    def test_a_per_tick_identity_with_a_shown_readout_is_a_duplicate(self):
        judged = self._judge(duplicate_of="bond")
        self.assertEqual(judged["verdict"], "refuse_as_duplicate")
        self.assertIn("G5_distinct_from_shown", judged["failed_gates"])

    def test_the_duplicate_verdict_outranks_the_euphemism_verdict(self):
        # One number under two names is the sharper accusation: nothing
        # about the number is wrong, only the second name.
        judged = self._judge(duplicate_of="bond", distress_relief=0.0)
        self.assertEqual(judged["verdict"], "refuse_as_duplicate")

    def test_a_negative_floor_is_refused(self):
        with self.assertRaises(ValueError):
            self._judge(incumbent_response_floor=-0.1)

    def test_refusal_is_reachable_for_every_candidate(self):
        for name in CANDIDATES:
            judged = self._judge(
                candidate=name, reads=list(CANDIDATES[name]["reads"]),
                distress_relief=-0.05,
            )
            self.assertIn(judged["verdict"], ("refuse_as_euphemism",))


class ReportTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = build_happiness_definition_report(
            ticks=200, lifecycles=3
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

    def test_the_instrument_reproduced_the_committed_floor(self):
        check = self.report["metrics"]["instrument_check"]
        self.assertTrue(check["floor_matches_committed"])
        self.assertEqual(check["committed_floor"], 0.0685)

    def test_the_balance_mirror_is_pinned_against_the_engine(self):
        parity = self.report["metrics"]["balance_mirror_parity"]
        self.assertEqual(parity["max_abs_difference"], 0.0)
        self.assertGreater(parity["ticks_compared"], 0)

    def test_every_candidate_is_judged_and_the_verdicts_are_the_vocabulary(self):
        candidates = self.report["decision"]["candidates"]
        self.assertEqual(sorted(candidates), sorted(CANDIDATES))
        for entry in candidates.values():
            self.assertIn(
                entry["verdict"],
                (
                    "adopt",
                    "eligible_not_selected",
                    "withhold",
                    "refuse_as_euphemism",
                    "refuse_as_duplicate",
                ),
            )

    def test_bond_rename_is_refused_as_a_duplicate(self):
        judged = self.report["decision"]["candidates"]["bond_rename"]
        self.assertEqual(judged["verdict"], "refuse_as_duplicate")
        self.assertEqual(judged["duplicate_of"], "bond")

    def test_at_most_one_candidate_is_adopted(self):
        adopted = self.report["decision"]["adopted"]
        self.assertLessEqual(len(adopted), 1)

    def test_the_selection_statistic_is_recorded_for_every_eligible(self):
        # The pre-registered rule: lowest neglect-arm final reading wins.
        decision = self.report["decision"]
        if decision["adopted"]:
            winner = decision["adopted"][0]
            readings = {
                name: entry["neglect_final_reading"]
                for name, entry in decision["candidates"].items()
                if entry["verdict"] in ("adopt", "eligible_not_selected")
            }
            self.assertEqual(
                min(readings, key=lambda name: (readings[name], name)),
                winner,
            )

    def test_source_artifact_paths_are_repo_relative(self):
        for path in self.report["source_artifacts"]:
            self.assertFalse(Path(path).is_absolute())
            self.assertNotIn("\\", path)

    def test_artifact_round_trips_as_json(self):
        with tempfile.TemporaryDirectory() as directory:
            written = write_happiness_definition_artifacts(
                directory, self.report
            )
            self.assertEqual(len(written), 1)
            reloaded = json.loads(written[0].read_text(encoding="utf-8"))
        self.assertEqual(reloaded["artifact_id"], ARTIFACT_ID)
        self.assertEqual(
            reloaded["decision"]["rule"], PRE_REGISTERED_RULE
        )

    def test_keeper_actions_are_the_game_verbs(self):
        self.assertEqual(tuple(KEEPER_ACTIONS), ("feed", "play"))


if __name__ == "__main__":
    unittest.main()
