"""Pins for cycle 24 N3: the micro-learner ablation conditions E/F/G.

Written BEFORE the module (the RED run is pasted into the experiment
report). The dossier names conditions E (full minus Q-table), F (full
minus tiny tree) and G (full minus Bayesian counter); the Phase-D fleet
built eleven threads and **none of them is any of those three**, so the
conditions have been unmet since cycle 12.

The pins assert the pre-registered RULE, each learner's MECHANISM, and
the property that protects the committed Phase-D numbers: the three
candidates are **additive and byte-identical when off**, pinned against
a FROZEN name list rather than by comparing new code to new code (the
trap M3 shipped and external review caught).

Measured values are never asserted; they are the study's output.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
for sub in ("labs/micro_threads", "labs/grid_genome", "labs/lifecycle_sim"):
    path = str(ROOT / sub)
    if path not in sys.path:
        sys.path.insert(0, path)

from thread_fleet import (  # noqa: E402
    CANDIDATE_THREAD_NAMES,
    CANDIDATE_THREADS,
    EXTENDED_FLEET_THREADS,
    FLEET_THREAD_NAMES,
    bayes_keeper_counter_observe,
    bayes_keeper_counter_signal,
    fleet_signals,
    observe_fleet,
    qtable_policy_observe,
    qtable_policy_signal,
    tiny_tree_router_observe,
    tiny_tree_router_signal,
)
from candidate_learner_ablation import (  # noqa: E402
    ARTIFACT_ID,
    CONDITION_LETTERS,
    KEEP_THRESHOLD_PCT,
    PRE_REGISTERED_RULE,
    build_candidate_ablation_report,
    judge_candidate,
    write_candidate_ablation_artifacts,
)

# The eleven Phase-D fleet threads, frozen here as a literal. This is
# the "off-mode key set pinned against a frozen list" the cycle-23 trap
# requires: comparing two calls to the NEW code cannot catch a key both
# calls gained.
PHASE_D_FLEET_NAMES = [
    "hunger_forecast",
    "energy_forecast",
    "boredom_novelty",
    "attention_forecast",
    "interaction_timing",
    "animation_bandit",
    "hidden_mood_hmm",
    "mutation_stability",
    "readability",
    "slip_compat",
    "lineage_survival",
]


def _state(**overrides) -> dict:
    state = {
        "alive": True,
        "age_ticks": 3,
        "hunger": 0.5,
        "energy": 0.5,
        "stress": 0.2,
        "bond": 0.5,
        "recent_interactions": [],
        "history": [],
    }
    state.update(overrides)
    return state


def _tick(action: str, balance: float) -> dict:
    return {"tick": 1, "action": action, "balance": balance}


class RegistryTests(unittest.TestCase):
    def test_the_three_documented_conditions_are_named(self):
        self.assertEqual(
            sorted(CONDITION_LETTERS), ["E", "F", "G"]
        )

    def test_each_letter_maps_to_the_dossier_mechanism(self):
        self.assertEqual(CONDITION_LETTERS["E"], "qtable_policy")
        self.assertEqual(CONDITION_LETTERS["F"], "tiny_tree_router")
        self.assertEqual(CONDITION_LETTERS["G"], "bayes_keeper_counter")

    def test_candidates_are_exactly_the_three(self):
        self.assertEqual(len(CANDIDATE_THREADS), 3)
        self.assertEqual(sorted(CANDIDATE_THREAD_NAMES), sorted(CONDITION_LETTERS.values()))

    def test_candidates_are_disjoint_from_the_phase_d_fleet(self):
        self.assertEqual(
            set(CANDIDATE_THREAD_NAMES) & set(FLEET_THREAD_NAMES), set()
        )

    def test_extended_fleet_is_the_fleet_plus_the_candidates(self):
        self.assertEqual(
            [name for name, _o, _s in EXTENDED_FLEET_THREADS],
            FLEET_THREAD_NAMES + CANDIDATE_THREAD_NAMES,
        )


class ByteIdenticalWhenOffTests(unittest.TestCase):
    """The committed Phase-D numbers must not move because of this slice."""

    def test_the_phase_d_fleet_roster_is_unchanged_against_a_frozen_list(self):
        self.assertEqual(FLEET_THREAD_NAMES, PHASE_D_FLEET_NAMES)

    def test_observe_fleet_emits_no_candidate_key_when_they_are_off(self):
        state = _state(
            learning_switches={name: True for name in PHASE_D_FLEET_NAMES}
        )
        observed = observe_fleet(state)
        self.assertEqual(set(observed) - set(PHASE_D_FLEET_NAMES), set())

    def test_fleet_signals_emits_no_candidate_signal_when_they_are_off(self):
        state = _state(
            learning_switches={name: True for name in PHASE_D_FLEET_NAMES}
        )
        names = {signal["name"] for signal in fleet_signals(state)}
        self.assertEqual(names - set(PHASE_D_FLEET_NAMES), set())

    def test_a_profile_that_names_no_switches_runs_no_candidate(self):
        self.assertEqual(observe_fleet(_state()), {})
        self.assertEqual(fleet_signals(_state()), [])

    def test_candidates_require_an_explicit_true_not_mere_presence(self):
        state = _state(
            learning_switches={name: False for name in CANDIDATE_THREAD_NAMES}
        )
        self.assertEqual(observe_fleet(state), {})

    def test_the_default_full_fleet_condition_switches_exactly_the_eleven(self):
        # The harness gained a fleet_names parameter; called WITHOUT it,
        # it must still produce the Phase-D condition exactly — pinned
        # against the frozen literal, not against a second call.
        from ablation_gates import _condition_switches

        switches, observes = _condition_switches("full_fleet")
        self.assertTrue(observes)
        self.assertEqual(switches, {name: True for name in PHASE_D_FLEET_NAMES})

    def test_the_default_minus_condition_refuses_a_candidate_name(self):
        # A candidate is not part of the Phase-D fleet, so the default
        # roster must not silently accept it as a removable thread.
        from ablation_gates import _condition_switches

        with self.assertRaises(ValueError):
            _condition_switches("minus_qtable_policy")


class QTableMechanismTests(unittest.TestCase):
    """E — a Q-table over a tightly scoped discrete state."""

    def test_cold_start_is_silent_rather_than_confident(self):
        signal = qtable_policy_signal({}, _state())
        self.assertEqual(signal["confidence"], 0.0)
        self.assertEqual(signal["effects"], {})

    def test_observe_records_the_bucket_it_will_credit_next_tick(self):
        updated = qtable_policy_observe({}, _state())
        self.assertIn("pending_bucket", updated)

    def test_the_executed_action_is_credited_not_the_recommended_one(self):
        # The keeper can override the companion's choice, so the table
        # must learn from what actually happened.
        first = qtable_policy_observe({}, _state())
        second = qtable_policy_observe(
            first, _state(history=[_tick("play", 0.9)])
        )
        keys = list((second.get("q") or {}).keys())
        self.assertTrue(any(key.endswith("|play") for key in keys))

    def test_repeated_visits_raise_confidence(self):
        state = _state()
        low = qtable_policy_observe({}, state)
        for _ in range(6):
            low = qtable_policy_observe(low, _state(history=[_tick("feed", 0.8)]))
        signal = qtable_policy_signal(low, state)
        self.assertGreater(signal["confidence"], 0.0)

    def test_the_table_prefers_the_action_with_the_better_return(self):
        memory = qtable_policy_observe({}, _state())
        for _ in range(8):
            memory = qtable_policy_observe(
                memory, _state(history=[_tick("feed", 0.9)])
            )
            memory = qtable_policy_observe(
                memory, _state(history=[_tick("sleep", -0.9)])
            )
        signal = qtable_policy_signal(memory, _state())
        self.assertEqual(signal["output"]["best_action"], "feed")


class TinyTreeMechanismTests(unittest.TestCase):
    """F — an interpretable depth-limited router."""

    def test_cold_start_is_silent(self):
        signal = tiny_tree_router_signal({}, _state())
        self.assertEqual(signal["confidence"], 0.0)
        self.assertEqual(signal["effects"], {})

    def test_the_signal_reports_a_human_readable_route(self):
        memory = tiny_tree_router_observe({}, _state())
        for _ in range(10):
            memory = tiny_tree_router_observe(
                memory, _state(hunger=0.9, history=[_tick("feed", 0.8)])
            )
            memory = tiny_tree_router_observe(
                memory, _state(hunger=0.1, history=[_tick("play", 0.7)])
            )
        signal = tiny_tree_router_signal(memory, _state(hunger=0.9))
        self.assertIn("route", signal["output"])
        self.assertIsInstance(signal["output"]["route"], str)

    def test_the_tree_routes_the_two_sides_differently(self):
        memory = tiny_tree_router_observe({}, _state())
        for _ in range(12):
            memory = tiny_tree_router_observe(
                memory, _state(hunger=0.9, history=[_tick("feed", 0.9)])
            )
            memory = tiny_tree_router_observe(
                memory, _state(hunger=0.1, history=[_tick("play", 0.9)])
            )
        hungry = tiny_tree_router_signal(memory, _state(hunger=0.95))
        sated = tiny_tree_router_signal(memory, _state(hunger=0.05))
        self.assertNotEqual(
            hungry["output"]["best_action"], sated["output"]["best_action"]
        )

    def test_depth_is_bounded_so_the_tree_stays_tiny(self):
        memory = tiny_tree_router_observe({}, _state())
        for index in range(40):
            memory = tiny_tree_router_observe(
                memory,
                _state(
                    hunger=index / 40,
                    energy=(index * 7 % 40) / 40,
                    history=[_tick("idle", 0.1)],
                ),
            )
        leaves = (memory.get("leaf_returns") or {})
        self.assertLessEqual(len(leaves), 4)


class BayesCounterMechanismTests(unittest.TestCase):
    """G — a Beta-Bernoulli tracker with uncertainty."""

    def test_cold_start_is_silent(self):
        signal = bayes_keeper_counter_signal({}, _state())
        self.assertEqual(signal["confidence"], 0.0)
        self.assertEqual(signal["effects"], {})

    def test_posterior_moves_toward_a_responsive_keeper(self):
        memory = {}
        for _ in range(20):
            memory = bayes_keeper_counter_observe(
                memory, _state(recent_interactions=[1])
            )
        signal = bayes_keeper_counter_signal(memory, _state())
        self.assertGreater(signal["output"]["responsiveness"], 0.5)

    def test_posterior_moves_toward_a_neglectful_keeper(self):
        memory = {}
        for _ in range(20):
            memory = bayes_keeper_counter_observe(
                memory, _state(recent_interactions=[0])
            )
        signal = bayes_keeper_counter_signal(memory, _state())
        self.assertLess(signal["output"]["responsiveness"], 0.5)

    def test_uncertainty_shrinks_as_evidence_accumulates(self):
        few = {}
        for _ in range(4):
            few = bayes_keeper_counter_observe(few, _state(recent_interactions=[1]))
        many = dict(few)
        for _ in range(40):
            many = bayes_keeper_counter_observe(many, _state(recent_interactions=[1]))
        self.assertLess(
            bayes_keeper_counter_signal(many, _state())["output"]["uncertainty"],
            bayes_keeper_counter_signal(few, _state())["output"]["uncertainty"],
        )

    def test_a_neglectful_keeper_suppresses_begging(self):
        # The domain point: a companion that has learned begging is not
        # answered should stop spending ticks on it.
        memory = {}
        for _ in range(30):
            memory = bayes_keeper_counter_observe(
                memory, _state(recent_interactions=[0])
            )
        effects = bayes_keeper_counter_signal(memory, _state(hunger=0.8))["effects"]
        self.assertLessEqual(effects.get("feed", 0.0), 0.0)


class PreRegisteredRuleTests(unittest.TestCase):
    def test_the_keep_threshold_is_the_documented_five_percent(self):
        self.assertEqual(KEEP_THRESHOLD_PCT, 5.0)

    def test_rule_names_its_pre_registration_and_the_documented_gate(self):
        rule = PRE_REGISTERED_RULE.lower()
        self.assertIn("pre-registered", rule)
        self.assertIn("5%", rule)
        self.assertIn("removal", rule)

    def test_a_learner_is_kept_on_welfare_removal_cost(self):
        judged = judge_candidate(
            thread="qtable_policy", removal_cost_pct=7.0, skill_pct=0.0
        )
        self.assertEqual(judged["decision"], "keep")

    def test_a_learner_is_kept_on_its_own_skill_metric(self):
        judged = judge_candidate(
            thread="qtable_policy", removal_cost_pct=0.0, skill_pct=9.0
        )
        self.assertEqual(judged["decision"], "keep")

    def test_a_learner_below_both_bars_is_dropped(self):
        judged = judge_candidate(
            thread="tiny_tree_router", removal_cost_pct=1.0, skill_pct=2.0
        )
        self.assertEqual(judged["decision"], "drop")

    def test_dropping_is_first_class_and_carries_its_reason(self):
        judged = judge_candidate(
            thread="bayes_keeper_counter", removal_cost_pct=0.0, skill_pct=0.0
        )
        self.assertEqual(judged["decision"], "drop")
        self.assertIn("5%", judged["note"])

    def test_a_missing_skill_metric_is_not_silently_zero(self):
        # An absent skill claim must be recorded as absent, never
        # substituted with a number.
        judged = judge_candidate(
            thread="qtable_policy", removal_cost_pct=0.0, skill_pct=None
        )
        self.assertIsNone(judged["skill_pct"])
        self.assertEqual(judged["decision"], "drop")


class ArtifactTests(unittest.TestCase):
    def test_report_carries_every_required_artifact_key(self):
        report = build_candidate_ablation_report(
            lifecycles_per_keeper=1, ticks=6
        )
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
            self.assertIn(key, report)
        self.assertEqual(report["artifact_id"], ARTIFACT_ID)

    def test_report_judges_all_three_documented_conditions(self):
        report = build_candidate_ablation_report(
            lifecycles_per_keeper=1, ticks=6
        )
        verdicts = report["metrics"]["candidate_verdicts"]
        self.assertEqual(
            sorted(entry["thread"] for entry in verdicts),
            sorted(CANDIDATE_THREAD_NAMES),
        )
        for entry in verdicts:
            self.assertIn(entry["condition_letter"], ("E", "F", "G"))

    def test_report_rejudges_the_incumbent_eleven_on_the_new_baseline(self):
        # "A drop that changes the kept-five roster would be a real
        # result" — so the incumbents must be re-judged, not assumed.
        report = build_candidate_ablation_report(
            lifecycles_per_keeper=1, ticks=6
        )
        incumbent = report["metrics"]["incumbent_reverdicts"]
        self.assertEqual(
            sorted(entry["thread"] for entry in incumbent),
            sorted(FLEET_THREAD_NAMES),
        )

    def test_source_artifact_paths_are_repo_relative(self):
        report = build_candidate_ablation_report(
            lifecycles_per_keeper=1, ticks=6
        )
        for path in report["source_artifacts"]:
            self.assertFalse(Path(path).is_absolute())
            self.assertNotIn("\\", path)

    def test_artifact_round_trips_as_json(self):
        report = build_candidate_ablation_report(
            lifecycles_per_keeper=1, ticks=6
        )
        with tempfile.TemporaryDirectory() as directory:
            written = write_candidate_ablation_artifacts(directory, report)
            self.assertEqual(len(written), 1)
            reloaded = json.loads(written[0].read_text(encoding="utf-8"))
        self.assertEqual(reloaded["artifact_id"], ARTIFACT_ID)
        self.assertEqual(reloaded["decision"]["rule"], PRE_REGISTERED_RULE)


if __name__ == "__main__":
    unittest.main()
