"""Lifecycle contract tests for the mecha_engine package surface.

Traceability: research/package_specs/mecha_engine_lifecycle_contract_gate.md
("Initial State Acceptance", "Transition Acceptance", "Episode Acceptance",
"Reward Acceptance", "Negative Checks"),
research/package_specs/mecha_engine_contract_traceability_matrix.md
("Lifecycle Test Obligations"), and
research/package_specs/mecha_engine_property_negative_test_strategy.md
(P4, invalid-grid rejection, bounded state).

Import mechanics match ``tests/test_package_imports.py``,
``tests/test_genome_contract.py``, and ``tests/test_generation_contract.py``:
the probes run in one ``python -B`` subprocess whose PYTHONPATH points at
this package's own ``src`` directory (standard src-layout semantics; an
installed package satisfies the same probe), executed by
``tests/helpers/lifecycle_contract_driver.py`` through
``mecha_engine.lifecycle`` and ``mecha_engine.genome``. This module never
mutates the interpreter module search path and never points the subprocess
at research lab directories. Fixtures are the frozen repository corpora
fixed by the test fixture manifest: ``data/seed_grids/mg_seed_001.json``
(the Stage 0 comparator grid), ``data/invalid_grids/*.json``, and
``data/slips/valid/slip_lcd_seed.json``.
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACKAGE_ROOT.parents[1]
SRC_DIR = PACKAGE_ROOT / "src"
DRIVER = Path(__file__).resolve().parent / "helpers" / "lifecycle_contract_driver.py"

# W1 (the living companion) widened the contracted surface: the F1
# chooser and the action vocabulary became public so interactive
# callers can drive `advance_tick` with the switchboard's own choices —
# see the gate doc's "Interactive surface" amendment.
REQUIRED_PUBLIC_SURFACE = [
    "ACTIONS",
    "advance_tick",
    "choose_action_detailed",
    "initial_state",
    "reward_for_transition",
    "run_episode",
]
REQUIRED_EPISODE_FIELDS = [
    "ticks_requested",
    "survival_ticks",
    "alive",
    "death_cause",
    "need_balance",
    "recovery_events",
    "action_counts",
    "final_state",
    "history",
]
REQUIRED_HISTORY_ENTRY_FIELDS = [
    "action",
    "alive",
    "balance",
    "death_cause",
    "recoveries",
    "state",
    "tick",
]
CONTINUOUS_STATE_KEYS = ["bond", "energy", "grid_stability", "hunger", "stress"]
REQUIRED_DEATH_CAUSES = {
    "starvation",
    "energy_collapse",
    "stress_collapse",
    "grid_collapse",
}
# Pinned Stage 0 comparator (mecha_engine_lifecycle_contract_gate.md and
# data/lifecycle/lifecycle_stage0.json): mg_seed_001 + slip_lcd_seed,
# ticks=72, rng_seed=20260512.
STAGE0_COMPARATOR = {
    "switchboard": {
        "survival_ticks": 72,
        "alive": True,
        "need_balance": 0.789129,
        "recovery_events": 14,
        "death_cause": None,
    },
    "idle": {
        "survival_ticks": 11,
        "alive": False,
        "need_balance": 0.121004,
        "recovery_events": 0,
        "death_cause": "starvation",
    },
    "random": {
        "survival_ticks": 21,
        "alive": False,
        "need_balance": 0.236001,
        "recovery_events": 2,
        "death_cause": "starvation",
    },
}


def _run_driver() -> dict:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(SRC_DIR) + (os.pathsep + existing if existing else "")
    result = subprocess.run(
        [sys.executable, "-B", str(DRIVER), "--repo-root", str(REPO_ROOT)],
        capture_output=True,
        text=True,
        env=env,
        cwd=PACKAGE_ROOT,
        timeout=300,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"lifecycle contract driver failed ({result.returncode}): {result.stderr}"
        )
    return json.loads(result.stdout)


class MechaEngineLifecycleContractTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = _run_driver()

    # -- Public surface -----------------------------------------------------

    def test_public_surface_is_exactly_the_contracted_set(self):
        surface = self.report["surface"]
        self.assertEqual(REQUIRED_PUBLIC_SURFACE, surface["public_all"])

    def test_run_episode_signature_matches_interface_spec(self):
        defaults = self.report["surface"]["run_episode_defaults"]
        self.assertIsNone(defaults["slip_profile"])
        self.assertIsNone(defaults["policy"])
        self.assertIsNone(defaults["actions"])
        self.assertEqual(72, defaults["ticks"])
        self.assertIsNone(defaults["rng_seed"])

    def test_no_learner_named_public_surface(self):
        # Online reward shaping, feedback learners, and bandit memory stay
        # lab-only; the package exposes no learner-shaped surface at all.
        self.assertEqual([], self.report["surface"]["learner_named_public_surface"])

    def test_lifecycle_surface_loads_no_lab_modules(self):
        self.assertEqual([], self.report["lab_modules_loaded"])

    # -- Initial state acceptance --------------------------------------------

    def test_initial_state_preserves_identity_and_starts_bounded(self):
        initial = self.report["initial"]
        self.assertTrue(initial["grid_id_preserved"])
        self.assertTrue(initial["slip_profile_id_preserved"])
        self.assertTrue(initial["no_profile_slip_id_none"])
        self.assertTrue(initial["alive"])
        self.assertTrue(initial["age_ticks_zero"])
        self.assertTrue(initial["death_cause_none"])
        self.assertTrue(initial["continuous_bounded"])
        self.assertTrue(initial["history_empty"])
        self.assertTrue(initial["recovery_events_zero"])
        self.assertTrue(initial["action_counts_zeroed"])

    def test_initial_state_derives_behavior_priors_from_slip(self):
        initial = self.report["initial"]
        self.assertTrue(initial["behavior_priors_from_profile"])
        self.assertTrue(initial["profile_changes_priors"])

    def test_initial_state_never_mutates_grid_or_profile(self):
        initial = self.report["initial"]
        self.assertFalse(initial["grid_mutated"])
        self.assertFalse(initial["profile_mutated"])
        self.assertFalse(self.report["fixtures_mutated"])

    def test_invalid_grid_rejected_before_simulation(self):
        initial = self.report["initial"]
        for key in [
            "invalid_grid_raised",
            "invalid_grid_with_profile_raised",
            "non_dict_grid_raised",
        ]:
            raised = initial[key]
            self.assertIsNotNone(raised, key)
            self.assertNotIn("UNEXPECTED", raised)
            self.assertIn("invalid grid", raised)

    def test_invalid_or_misaligned_slip_rejected_before_state_creation(self):
        initial = self.report["initial"]
        invalid_raised = initial["invalid_profile_raised"]
        self.assertIsNotNone(invalid_raised)
        self.assertNotIn("UNEXPECTED", invalid_raised)
        self.assertIn("curiosity", invalid_raised)
        misaligned_raised = initial["misaligned_grid_raised"]
        self.assertIsNotNone(misaligned_raised)
        self.assertNotIn("UNEXPECTED", misaligned_raised)
        self.assertIn("SLIP", misaligned_raised)

    # -- Transition acceptance ------------------------------------------------

    def test_deliberation_rides_history_under_a_thinking_covenant(self):
        # F1 (the seen thought): switchboard ticks under a deliberation
        # covenant carry the R1 record; reflexes/idle/frozen flows never
        # gain the key (byte-identical histories).
        probe = self.report["deliberation_history"]
        self.assertGreater(probe["thoughts_recorded"], 0)
        self.assertTrue(probe["thought_counts_bounded"])
        self.assertTrue(probe["thought_carries_max_and_threshold"])
        self.assertTrue(probe["frozen_flow_has_no_key"])
        self.assertTrue(probe["idle_policy_never_thinks"])
        self.assertTrue(probe["deterministic_repeat_identical"])

    def test_advance_tick_accepts_only_supported_actions(self):
        raised = self.report["transitions"]["unsupported_action_raised"]
        self.assertIsNotNone(raised)
        self.assertNotIn("UNEXPECTED", raised)
        self.assertIn("unsupported lifecycle action", raised)

    def test_advance_tick_returns_new_state_without_mutating_input(self):
        self.assertFalse(self.report["transitions"]["input_state_mutated"])

    def test_advance_tick_ages_counts_and_records_history(self):
        transitions = self.report["transitions"]
        self.assertTrue(transitions["age_ticks_incremented"])
        self.assertTrue(transitions["action_count_updated"])
        self.assertTrue(transitions["history_appended_once"])
        self.assertEqual(
            REQUIRED_HISTORY_ENTRY_FIELDS, transitions["history_entry_fields"]
        )

    def test_state_variables_remain_bounded_at_every_forced_corner(self):
        self.assertTrue(self.report["transitions"]["bounded_after_corner_sweep"])

    def test_death_is_always_explicit_with_the_four_contracted_causes(self):
        transitions = self.report["transitions"]
        self.assertFalse(transitions["death_without_cause_seen"])
        self.assertTrue(
            set(transitions["corner_sweep_death_causes_explicit"]).issubset(
                REQUIRED_DEATH_CAUSES
            )
        )
        for cause, probe in transitions["death_probes"].items():
            with self.subTest(cause=cause):
                self.assertFalse(probe["alive"])
                self.assertEqual(cause, probe["death_cause"])
                # Pinned survival arithmetic: the death tick is counted.
                self.assertTrue(probe["tick_counted"])

    def test_dangerous_need_recovery_is_recorded(self):
        self.assertTrue(self.report["transitions"]["hunger_recovery_recorded"])

    def test_dead_states_pass_through_unchanged(self):
        transitions = self.report["transitions"]
        self.assertTrue(transitions["dead_state_unchanged"])
        self.assertTrue(transitions["dead_state_history_not_grown"])

    # -- Episode acceptance -----------------------------------------------------

    def test_episode_summary_reports_all_contracted_fields(self):
        episodes = self.report["episodes"]
        self.assertEqual(
            REQUIRED_EPISODE_FIELDS, episodes["required_fields_present"]
        )
        self.assertEqual(CONTINUOUS_STATE_KEYS, episodes["final_state_keys"])
        self.assertTrue(episodes["json_roundtrip"])

    def test_episode_reproduces_stage0_policy_comparator(self):
        comparator = self.report["episodes"]["comparator"]
        for policy, expected in STAGE0_COMPARATOR.items():
            with self.subTest(policy=policy):
                self.assertEqual(expected, comparator[policy])

    def test_episode_defaults_are_72_switchboard_ticks(self):
        episodes = self.report["episodes"]
        self.assertEqual(72, episodes["default_ticks_requested"])
        self.assertTrue(episodes["default_policy_is_switchboard"])

    def test_episode_is_deterministic_per_rng_seed(self):
        episodes = self.report["episodes"]
        self.assertTrue(episodes["deterministic_repeat_identical"])
        self.assertTrue(episodes["reseeded_differs"])
        self.assertTrue(episodes["seed_none_matches_stage0_seed"])

    def test_episode_history_is_complete_bounded_and_explicit(self):
        episodes = self.report["episodes"]
        self.assertTrue(episodes["history_ticks_sequential_and_complete"])
        self.assertTrue(episodes["history_states_bounded"])
        self.assertTrue(episodes["history_balances_bounded"])
        self.assertTrue(episodes["death_causes_explicit"])
        self.assertTrue(episodes["action_counts_sum_matches_survival"])

    def test_need_balance_scores_the_full_horizon_with_zero_fill(self):
        episodes = self.report["episodes"]
        self.assertTrue(episodes["horizon_score_matches_zero_fill"])
        self.assertTrue(episodes["early_death_not_inflated"])

    def test_explicit_action_streams_are_supported(self):
        episodes = self.report["episodes"]
        self.assertTrue(episodes["stream_policy_field_none"])
        self.assertEqual(12, episodes["stream_ticks_requested"])
        self.assertTrue(episodes["stream_actions_followed"])

    def test_ambiguous_and_malformed_episode_requests_are_rejected(self):
        episodes = self.report["episodes"]
        for key, needle in [
            ("ambiguous_request_raised", "ambiguous"),
            ("short_stream_raised", "action stream"),
            ("bad_stream_action_raised", "unsupported lifecycle action"),
            ("bad_policy_raised", "unsupported lifecycle policy"),
        ]:
            raised = episodes[key]
            self.assertIsNotNone(raised, key)
            self.assertNotIn("UNEXPECTED", raised)
            self.assertIn(needle, raised)

    def test_run_episode_rejects_invalid_grids_before_simulation(self):
        raised = self.report["episodes"]["invalid_grid_raised"]
        self.assertIsNotNone(raised)
        self.assertNotIn("UNEXPECTED", raised)
        self.assertIn("invalid grid", raised)

    def test_run_episode_never_mutates_grid_or_profile(self):
        episodes = self.report["episodes"]
        self.assertFalse(episodes["grid_mutated"])
        self.assertFalse(episodes["profile_mutated"])

    # -- Reward acceptance ----------------------------------------------------

    def test_rewards_stay_in_unit_interval_across_a_full_episode(self):
        rewards = self.report["rewards"]
        self.assertTrue(rewards["episode_rewards_bounded"])
        self.assertEqual(72, rewards["episode_reward_count"])
        self.assertTrue(rewards["reward_in_unit_interval"])

    def test_reward_is_deterministic_and_pure(self):
        rewards = self.report["rewards"]
        self.assertTrue(rewards["reward_deterministic"])
        self.assertFalse(rewards["inputs_mutated"])

    def test_reward_includes_the_four_recovery_signals(self):
        rewards = self.report["rewards"]
        self.assertTrue(rewards["improvement_bonus_positive"])
        deltas = rewards["recovery_signal_deltas"]
        self.assertGreater(deltas["hunger"], 0)
        self.assertGreater(deltas["energy"], 0)
        self.assertGreater(deltas["stress"], 0)
        self.assertGreater(deltas["bond"], 0)

    def test_reward_rejects_unsupported_actions_and_malformed_states(self):
        rewards = self.report["rewards"]
        for key in ["unsupported_action_raised", "missing_state_key_raised"]:
            raised = rewards[key]
            self.assertIsNotNone(raised, key)
            self.assertNotIn("UNEXPECTED", raised)

    # -- SLIP v0.2 acceptance (decision record 0013) ---------------------------

    def test_v2_profile_stashes_ladder_state_and_v1_omits_it(self):
        probe = self.report["slip_v2"]
        self.assertEqual(0.8, probe["v2_state_risk_tolerance"])
        self.assertEqual(
            {"mutation_risk_scorer": False}, probe["v2_state_learning_switches"]
        )
        self.assertTrue(probe["v1_state_has_no_ladder_keys"])

    def test_ladder_fields_are_version_gated_with_the_exact_error(self):
        raised = self.report["slip_v2"]["version_gate_raised"]
        self.assertIsNotNone(raised)
        self.assertNotIn("UNEXPECTED", raised)
        self.assertIn(
            "profile risk_tolerances requires slip_version 0.2.0", raised
        )

    def test_unknown_slip_version_is_rejected_with_the_exact_error(self):
        raised = self.report["slip_v2"]["unknown_version_raised"]
        self.assertIsNotNone(raised)
        self.assertNotIn("UNEXPECTED", raised)
        self.assertIn("slip_version must be one of 0.1.0, 0.2.0", raised)

    def test_forbidden_traits_alignment_errors_are_verbatim(self):
        probe = self.report["slip_v2"]
        role_raised = probe["forbidden_role_raised"]
        self.assertIsNotNone(role_raised)
        self.assertNotIn("UNEXPECTED", role_raised)
        self.assertIn("forbidden role present in grid: body", role_raised)
        material_raised = probe["forbidden_material_raised"]
        self.assertIsNotNone(material_raised)
        self.assertNotIn("UNEXPECTED", material_raised)
        self.assertIn(
            "forbidden material present in grid: hard", material_raised
        )

    def test_forbidding_a_required_organs_cell_role_is_a_contradiction(self):
        raised = self.report["slip_v2"]["contradiction_raised"]
        self.assertIsNotNone(raised)
        self.assertNotIn("UNEXPECTED", raised)
        self.assertIn(
            "forbidden role eye contradicts required organ role sensor", raised
        )

    def test_v2_episodes_run_deterministically_without_mutating_the_profile(self):
        probe = self.report["slip_v2"]
        self.assertEqual(24, probe["v2_episode_survival_ticks"])
        self.assertTrue(probe["v2_episode_deterministic"])
        self.assertFalse(probe["v2_profile_mutated"])

    # -- Negative checks ---------------------------------------------------------

    def test_no_online_learner_memory_across_episodes(self):
        memory = self.report["no_learner_memory"]
        self.assertTrue(memory["cross_episode_results_identical"])
        self.assertTrue(memory["action_reward_rings_bounded"])


if __name__ == "__main__":
    unittest.main()
