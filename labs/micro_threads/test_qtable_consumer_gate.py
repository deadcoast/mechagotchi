"""Pins for cycle 27 Q1: the Q-table earns its consumer — or the seam stays empty.

P4 measured `qtable_policy` beating the incumbent frozen reactive rule
by 44.685% at per-tick recommendation quality — but today that
recommendation enters the decision only as one diluted additive nudge
among ~15 threads. DR 0051 decision 3: joining the fleet *"needs a
consumer asking for it."* Q1 builds that consumer as an OPT-IN seam in
the switchboard — a new `qtable_consumer` learning switch (explicit
True, the D1 rule) that FOLLOWS the thread's recommendation when the
thread itself reports full confidence (its own committed
QTABLE_CONFIDENT_VISITS semantics; no new constant) — and gates the
end-to-end question by the D6 rule verbatim on the D6 harness.

**Byte-identical when off, proven against committed numbers**: the
committed switchboard scenarios artifact must reproduce parsed-equal
with the seam in the module, and (at the committed budget) the
committed full_fleet welfare and N3 skill statistics must reproduce
exactly. **`eligible_not_promoted` is the expected verdict** — the D6
lesson: the decision seam's welfare is near-saturated — and ships as
the finding with the seam left opt-in. Refusal is first-class; nothing
deletes the incumbent rule.
"""

import json
import sys
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
for sub in ("labs/micro_threads", "labs/grid_genome", "labs/lifecycle_sim"):
    path = str(ROOT / sub)
    if path not in sys.path:
        sys.path.insert(0, path)

import tempfile  # noqa: E402

from micro_switchboard import (  # noqa: E402
    QTABLE_CONSUMER_SWITCH,
    run_scenarios,
    run_switchboard,
)
from thread_fleet import (  # noqa: E402
    QTABLE_CONFIDENT_VISITS,
    _qtable_bucket,
)
from qtable_consumer_gate import (  # noqa: E402
    ARTIFACT_ID,
    PRE_REGISTERED_RULE,
    PRE_RUN_PREDICTION,
    build_qtable_consumer_report,
    judge_consumer,
    write_qtable_consumer_artifacts,
)


def _fixture_state(**overrides) -> dict:
    state = {
        "hunger": 0.55,
        "energy": 0.55,
        "bond": 0.5,
        "stress": 0.2,
        "grid_stability": 0.9,
        "recent_interactions": [1, 0, 1],
        "action_rewards": {"feed": [0.5], "play": [0.5]},
        "history": [],
    }
    state.update(overrides)
    return state


def _warm_qtable_state(state: dict, best_action: str) -> dict:
    bucket = _qtable_bucket(state)
    return {
        "q": {
            f"{bucket}|{best_action}": {
                "mean": 0.9,
                "n": QTABLE_CONFIDENT_VISITS,
            },
            f"{bucket}|idle": {"mean": 0.1, "n": QTABLE_CONFIDENT_VISITS},
        },
        "pending_bucket": bucket,
    }


class SeamOffTests(unittest.TestCase):
    """Byte-identical when off — against committed evidence."""

    def test_a_switchless_decision_carries_no_consumer_key(self):
        decision = run_switchboard(_fixture_state())
        self.assertNotIn("qtable_consumer", decision)

    def test_the_committed_scenarios_artifact_reproduces(self):
        committed = json.loads(
            (ROOT / "data" / "micro_learners" / "switchboard_stage0.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(run_scenarios(), committed)

    def test_the_consumer_switch_alone_is_not_enough(self):
        # The consumer follows the THREAD; a consumer switched on while
        # the thread itself is not opted in has nothing to follow.
        state = _fixture_state(
            learning_switches={QTABLE_CONSUMER_SWITCH: True}
        )
        decision = run_switchboard(state)
        self.assertNotIn("qtable_consumer", decision)


class SeamOnTests(unittest.TestCase):
    def _consumer_state(self, best_action: str = "play") -> dict:
        state = _fixture_state(
            learning_switches={
                "qtable_policy": True,
                QTABLE_CONSUMER_SWITCH: True,
            },
        )
        state["thread_states"] = {
            "qtable_policy": _warm_qtable_state(state, best_action)
        }
        return state

    def test_a_warm_confident_thread_is_followed(self):
        decision = run_switchboard(self._consumer_state("play"))
        self.assertEqual(decision["action"], "play")
        consumer = decision["qtable_consumer"]
        self.assertTrue(consumer["followed"])
        self.assertEqual(consumer["recommended"], "play")
        self.assertIn("base_action", consumer)
        self.assertIn("agreed", consumer)

    def test_a_cold_thread_is_not_followed(self):
        state = self._consumer_state("play")
        state["thread_states"] = {"qtable_policy": {}}
        decision = run_switchboard(state)
        self.assertNotIn("qtable_consumer", decision)

    def test_an_unconfident_thread_is_not_followed(self):
        state = self._consumer_state("play")
        bucket = _qtable_bucket(state)
        state["thread_states"] = {
            "qtable_policy": {
                "q": {
                    f"{bucket}|play": {"mean": 0.9, "n": 3},
                    f"{bucket}|idle": {"mean": 0.1, "n": 3},
                },
                "pending_bucket": bucket,
            }
        }
        decision = run_switchboard(state)
        self.assertNotIn("qtable_consumer", decision)

    def test_the_followed_decision_reports_the_thread_confidence(self):
        decision = run_switchboard(self._consumer_state("play"))
        self.assertEqual(decision["confidence"], 1.0)


class JudgeTests(unittest.TestCase):
    def _judge(self, **overrides):
        base = dict(
            welfare_pct=0.4,
            fired_fraction=0.3,
            keep_threshold_pct=5.0,
        )
        base.update(overrides)
        return judge_consumer(**base)

    def test_within_the_band_is_eligible_not_promoted(self):
        self.assertEqual(
            self._judge()["verdict"], "eligible_not_promoted"
        )

    def test_over_the_bar_is_an_adoption_candidate(self):
        self.assertEqual(
            self._judge(welfare_pct=7.5)["verdict"],
            "adopt_into_default_candidate",
        )

    def test_under_the_bar_is_refused_as_consumer(self):
        judged = self._judge(welfare_pct=-6.2)
        self.assertEqual(judged["verdict"], "refuse_as_consumer")

    def test_a_consumer_that_never_fires_is_withheld(self):
        judged = self._judge(fired_fraction=0.0)
        self.assertEqual(judged["verdict"], "withhold")
        self.assertIn("G2_consumer_fires", judged["failed_gates"])

    def test_a_non_positive_bar_is_refused(self):
        with self.assertRaises(ValueError):
            self._judge(keep_threshold_pct=0.0)


class PreRegistrationTests(unittest.TestCase):
    def test_the_rule_names_the_verdicts_and_the_bar(self):
        rule = PRE_REGISTERED_RULE.lower()
        self.assertIn("pre-registered", rule)
        self.assertIn("eligible_not_promoted", rule)
        self.assertIn("refuse_as_consumer", rule)
        self.assertIn("5%", PRE_REGISTERED_RULE)

    def test_the_prediction_expects_the_saturated_seam(self):
        prediction = PRE_RUN_PREDICTION.lower()
        self.assertIn("eligible_not_promoted", prediction)
        self.assertIn("beg", prediction)


class ReportTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = build_qtable_consumer_report(
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

    def test_the_scenarios_instrument_gate_always_binds(self):
        check = self.report["metrics"]["instrument_check"]
        self.assertTrue(check["scenarios_reproduced"])

    def test_the_beg_interaction_is_measured_not_gated(self):
        begs = self.report["metrics"]["beg_interaction"]
        self.assertIn("incumbent_beg_ticks", begs)
        self.assertIn("consumer_beg_ticks", begs)
        self.assertIn("recorded_not_gated", begs["note"])

    def test_the_verdict_is_in_the_pre_registered_vocabulary(self):
        decision = self.report["decision"]
        self.assertIn(
            decision["verdict"],
            (
                "adopt_into_default_candidate",
                "eligible_not_promoted",
                "refuse_as_consumer",
                "withhold",
            ),
        )
        self.assertEqual(decision["rule"], PRE_REGISTERED_RULE)

    def test_source_artifact_paths_are_repo_relative(self):
        for path in self.report["source_artifacts"]:
            self.assertFalse(Path(path).is_absolute())
            self.assertNotIn("\\", path)

    def test_artifact_round_trips_as_json(self):
        with tempfile.TemporaryDirectory() as directory:
            written = write_qtable_consumer_artifacts(
                directory, self.report
            )
            self.assertEqual(len(written), 1)
            reloaded = json.loads(written[0].read_text(encoding="utf-8"))
        self.assertEqual(reloaded["artifact_id"], ARTIFACT_ID)


if __name__ == "__main__":
    unittest.main()
