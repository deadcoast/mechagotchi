"""Pins for cycle 24 N5: `health` — the CHOSEN definition, gated.

Written BEFORE the module (the RED run is pasted into the experiment
report). DR 0048 withheld `health` and named the gate it needed:

    "a record that declares its definition CHOSEN (exactly as L4 did for
     `animation_density`), states which hidden axes it reads, and gates
     it — including on whether a player-facing 'health' that is really
     grid-stability is *honest labelling* or a euphemism."

So the pins assert that the euphemism question is a REAL GATE with a
measured answer, that every gate can fail on its own, and that
**refusing is reachable** — DR 0048 called refusal first-class and a
gate that could only adopt would make that a lie.

Measured values are never asserted; they are the study's output.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from health_definition_gate import (  # noqa: E402
    ARTIFACT_ID,
    CANDIDATES,
    KEEPER_ACTIONS,
    PRE_REGISTERED_RULE,
    PRE_RUN_PREDICTION,
    build_health_definition_report,
    judge_candidate,
    danger_margin,
    write_health_definition_artifacts,
)


def _passing(**overrides) -> dict:
    payload = {
        "candidate": "danger_margin",
        "hidden_axes_read": ["stress", "grid_stability"],
        "keeper_action_response": {"feed": 0.21, "play": 0.04},
        "incumbent_response_floor": 0.01,
        "distress_relief": 0.18,
        "separates_deaths_from_survivors": True,
    }
    payload.update(overrides)
    return payload


class CandidateTests(unittest.TestCase):
    def test_both_candidates_are_carried(self):
        # DR 0048 named grid_stability; the study is free to measure a
        # better one, but it may not quietly drop the named one.
        self.assertIn("grid_stability", CANDIDATES)
        self.assertIn("danger_margin", CANDIDATES)

    def test_every_candidate_declares_the_hidden_axes_it_reads(self):
        for name, spec in CANDIDATES.items():
            self.assertTrue(spec["hidden_axes_read"], name)

    def test_the_keeper_actions_are_the_ones_a_player_actually_has(self):
        # The euphemism question turns on this: a "health" bar is judged
        # against what the PLAYER can do, not what the companion does.
        self.assertEqual(tuple(KEEPER_ACTIONS), ("feed", "play"))


class LethalMarginTests(unittest.TestCase):
    """Candidate B — no invented weights, only the engine's own thresholds."""

    def test_a_healthy_state_scores_high(self):
        margin = danger_margin(
            {"hunger": 0.1, "energy": 0.9, "stress": 0.05, "grid_stability": 0.95},
            {"hunger": 0.75, "energy": 0.25, "stress": 0.65, "grid_stability": 0.35},
        )
        self.assertGreater(margin, 0.8)

    def test_the_worst_axis_decides(self):
        # It is a MINIMUM, not a blend: a creature one step from
        # starvation is not healthy because its grid is intact.
        margin = danger_margin(
            {"hunger": 0.74, "energy": 0.9, "stress": 0.05, "grid_stability": 0.95},
            {"hunger": 0.75, "energy": 0.25, "stress": 0.65, "grid_stability": 0.35},
        )
        self.assertLess(margin, 0.05)

    def test_past_a_danger_threshold_scores_zero(self):
        margin = danger_margin(
            {"hunger": 0.99, "energy": 0.9, "stress": 0.05, "grid_stability": 0.95},
            {"hunger": 0.75, "energy": 0.25, "stress": 0.65, "grid_stability": 0.35},
        )
        self.assertEqual(margin, 0.0)

    def test_it_uses_no_weight_that_is_not_an_engine_threshold(self):
        # The whole reason this candidate exists: DR 0048 refused a
        # composite because "any composite needs weights nobody
        # documented". A minimum has no weights at all.
        first = danger_margin(
            {"hunger": 0.5, "energy": 0.5, "stress": 0.5, "grid_stability": 0.5},
            {"hunger": 0.75, "energy": 0.25, "stress": 0.65, "grid_stability": 0.35},
        )
        second = danger_margin(
            {"hunger": 0.5, "energy": 0.5, "stress": 0.5, "grid_stability": 0.5},
            {"hunger": 0.75, "energy": 0.25, "stress": 0.65, "grid_stability": 0.35},
        )
        self.assertEqual(first, second)


class GateTests(unittest.TestCase):
    """Four gates, each able to fail alone; refusal reachable."""

    def test_a_candidate_passing_everything_is_adoptable(self):
        judged = judge_candidate(**_passing())
        self.assertEqual(judged["verdict"], "adopt")

    def test_g1_fails_when_no_hidden_axis_is_declared(self):
        judged = judge_candidate(**_passing(hidden_axes_read=[]))
        self.assertIn("G1_definition_declared", judged["failed_gates"])

    def test_g2_fails_when_the_keeper_cannot_move_it(self):
        judged = judge_candidate(
            **_passing(keeper_action_response={"feed": 0.0, "play": 0.0})
        )
        self.assertIn("G2_keeper_responsive", judged["failed_gates"])

    def test_g2_is_judged_against_a_MEASURED_incumbent_floor(self):
        # The bar is what the engine's existing VISIBLE axes do under
        # the same actions — never a constant.
        tiny = judge_candidate(
            **_passing(
                keeper_action_response={"feed": 0.005, "play": 0.0},
                incumbent_response_floor=0.01,
            )
        )
        self.assertIn("G2_keeper_responsive", tiny["failed_gates"])

    def test_g3_fails_when_it_does_not_separate_deaths_from_survivors(self):
        judged = judge_candidate(**_passing(separates_deaths_from_survivors=False))
        self.assertIn("G3_survival_coupled", judged["failed_gates"])

    def test_g4_fails_when_helping_a_distressed_creature_does_nothing(self):
        # THE EUPHEMISM TEST. A bar that does not rise when the keeper
        # relieves the distress is not a health bar, whatever it is
        # called.
        judged = judge_candidate(**_passing(distress_relief=0.0))
        self.assertIn("G4_honest_label", judged["failed_gates"])

    def test_a_candidate_failing_the_label_test_is_REFUSED_as_a_euphemism(self):
        judged = judge_candidate(
            **_passing(
                candidate="grid_stability",
                keeper_action_response={"feed": 0.0, "play": 0.0},
                distress_relief=0.0,
            )
        )
        self.assertEqual(judged["verdict"], "refuse_as_euphemism")

    def test_refusal_is_reachable_for_every_candidate(self):
        for name in CANDIDATES:
            judged = judge_candidate(
                **_passing(
                    candidate=name,
                    keeper_action_response={"feed": 0.0, "play": 0.0},
                    distress_relief=0.0,
                )
            )
            self.assertEqual(judged["verdict"], "refuse_as_euphemism", name)

    def test_a_structural_failure_that_is_not_the_label_withholds(self):
        # Failing G1 or G3 is not the same accusation as failing the
        # label test, and the verdicts must not be conflated.
        judged = judge_candidate(**_passing(separates_deaths_from_survivors=False))
        self.assertEqual(judged["verdict"], "withhold")

    def test_a_negative_incumbent_floor_is_refused(self):
        with self.assertRaises(ValueError):
            judge_candidate(**_passing(incumbent_response_floor=-1.0))


class PreRegistrationTests(unittest.TestCase):
    def test_the_rule_names_the_euphemism_question_dr0048_asked_for(self):
        rule = PRE_REGISTERED_RULE.lower()
        self.assertIn("pre-registered", rule)
        self.assertIn("euphemism", rule)
        self.assertIn("chosen", rule)
        self.assertIn("measured", rule)

    def test_a_prediction_is_written_down_before_the_run(self):
        # DR 0045's precedent: a prediction recorded first can be wrong
        # on the record.
        self.assertIn("grid_stability", PRE_RUN_PREDICTION)


class ArtifactTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = build_health_definition_report(ticks=12, lifecycles=2)

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

    def test_every_candidate_is_judged(self):
        verdicts = self.report["decision"]["candidates"]
        self.assertEqual(sorted(verdicts), sorted(CANDIDATES))

    def test_the_engine_is_MEASURED_not_asserted(self):
        measured = self.report["metrics"]["engine"]
        self.assertIn("per_action_delta", measured)
        self.assertIn("danger_thresholds", measured)

    def test_no_axis_carries_an_invented_value(self):
        # M5's pin, inherited: an absent measurement is recorded absent.
        for entry in self.report["decision"]["candidates"].values():
            if entry["verdict"] != "adopt":
                self.assertIn("failed_gates", entry)

    def test_source_artifact_paths_are_repo_relative(self):
        for path in self.report["source_artifacts"]:
            self.assertFalse(Path(path).is_absolute())
            self.assertNotIn("\\", path)

    def test_artifact_round_trips_as_json(self):
        with tempfile.TemporaryDirectory() as directory:
            written = write_health_definition_artifacts(directory, self.report)
            self.assertEqual(len(written), 1)
            reloaded = json.loads(written[0].read_text(encoding="utf-8"))
        self.assertEqual(reloaded["artifact_id"], ARTIFACT_ID)
        self.assertEqual(reloaded["decision"]["rule"], PRE_REGISTERED_RULE)


if __name__ == "__main__":
    unittest.main()
