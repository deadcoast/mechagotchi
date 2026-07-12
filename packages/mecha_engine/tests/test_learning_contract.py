"""Learning contract tests for the mecha_engine package surface.

Traceability: research/package_specs/mecha_engine_learning_interface_spec.md
("Proposed public surface", "The bounded claim", "Hard gates for the port",
"Non-goals"), research/package_specs/mecha_engine_contract_traceability_matrix.md
("Cross-Cut Negative Tests"), and
research/decision_records/0009-create-mecha-engine-learning-target.md.

Import mechanics match ``tests/test_package_imports.py`` and the other
contract suites: the probes run in one ``python -B`` subprocess whose
PYTHONPATH points at this package's own ``src`` directory (standard
src-layout semantics; an installed package satisfies the same probe),
executed by ``tests/helpers/learning_contract_driver.py`` through
``mecha_engine.learning`` and its promoted dependencies. This module never
mutates the interpreter module search path and never points the subprocess
at research lab directories. Fixtures are frozen repository corpora:
``data/seed_grids/mg_seed_001.json`` and
``data/slips/valid/slip_lcd_seed.json``.

The sheltered wellbeing pin is asserted here from values the driver
computes through the package surface: feedback need balance 0.790524 vs
frozen 0.750884 on the seed fixture (48 ticks), delta exactly +0.03964 —
the recorded artifact values
(data/micro_learners/switchboard_lifecycle_feedback_stage0.json). Both
arms survive all 48 ticks: the pin is need balance, never survival
(decision record 0009's bounded claim). The verbatim reproduction of the
lab episode records and the stress benchmark's per-candidate arms is
pinned by the lab-side parity test
(``labs/grid_genome/test_package_learning_parity.py``); this suite proves
the package contract directly.
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
DRIVER = Path(__file__).resolve().parent / "helpers" / "learning_contract_driver.py"

# The contracted three plus the fleet surface (the spec's additive
# "fleet surface" section, cycle 14 F3b — export only, opt-in silent).
REQUIRED_PUBLIC_SURFACE = [
    "ACTIONS",
    "FLEET_THREAD_NAMES",
    "decide",
    "fleet_signals",
    "observe_fleet",
    "run_feedback_episode",
]
# The lab's action set, order load-bearing (deterministic tie-breaks).
REQUIRED_ACTIONS = ["feed", "play", "sleep", "idle", "mutate"]
# Interface-spec signatures (learning interface spec, "Proposed public
# surface").
REQUIRED_DECIDE_DEFAULTS = {"state": "REQUIRED"}
REQUIRED_EPISODE_DEFAULTS = {
    "grid": "REQUIRED",
    "slip_profile": "REQUIRED",
    "ticks": "48",
    "feedback_enabled": "True",
    "miscalibrate": "True",
}
REQUIRED_DECISION_FIELDS = [
    "action",
    "confidence",
    "explanation",
    "threads",
    "utilities",
]
REQUIRED_EPISODE_FIELDS = [
    "action_counts",
    "alive",
    "death_cause",
    "episode_deterministic",
    "final_action_reward_means",
    "history",
    "initial_action_reward_means",
    "need_balance",
    "policy",
    "recovery_events",
    "reward_update_count",
    "survival_ticks",
    "ticks_requested",
]
REQUIRED_HISTORY_ENTRY_FIELDS = [
    "action",
    "alive",
    "death_cause",
    "decision_confidence",
    "need_balance",
    "observed_reward",
    "reward_means_after",
    "reward_means_before",
    "tick",
]
# Recorded sheltered-measurement values
# (data/micro_learners/switchboard_lifecycle_feedback_stage0.json summary).
SHELTERED_FEEDBACK_NEED_BALANCE = 0.790524
SHELTERED_FROZEN_NEED_BALANCE = 0.750884
SHELTERED_NEED_BALANCE_DELTA = 0.03964
SHELTERED_TICKS = 48


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
        timeout=600,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"learning contract driver failed ({result.returncode}): {result.stderr}"
        )
    return json.loads(result.stdout)


class MechaEngineLearningContractTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = _run_driver()

    # -- Public surface -----------------------------------------------------

    def test_public_surface_is_the_contracted_names(self):
        self.assertEqual(
            REQUIRED_PUBLIC_SURFACE, self.report["surface"]["public_all"]
        )

    def test_actions_pin_matches_the_lab_action_set(self):
        self.assertEqual(REQUIRED_ACTIONS, self.report["surface"]["actions"])

    def test_decide_signature_matches_interface_spec(self):
        defaults = self.report["surface"]["signature_defaults"]["decide"]
        self.assertEqual(REQUIRED_DECIDE_DEFAULTS, defaults)

    def test_run_feedback_episode_signature_matches_interface_spec(self):
        defaults = self.report["surface"]["signature_defaults"][
            "run_feedback_episode"
        ]
        self.assertEqual(REQUIRED_EPISODE_DEFAULTS, defaults)

    def test_tuning_parameters_are_keyword_only_including_miscalibrate(self):
        keyword_only = self.report["surface"]["keyword_only_parameters"]
        self.assertEqual(
            ["ticks", "feedback_enabled", "miscalibrate"],
            keyword_only["run_feedback_episode"],
        )
        self.assertEqual([], keyword_only["decide"])

    def test_keyword_only_parameters_reject_positional_use(self):
        probe = self.report["keyword_only"]
        self.assertIsNotNone(probe["positional_ticks_raised"])
        self.assertIn("TypeError", probe["positional_ticks_raised"])
        self.assertIsNotNone(probe["positional_flags_raised"])
        self.assertIn("TypeError", probe["positional_flags_raised"])

    def test_learning_surface_loads_no_lab_modules(self):
        self.assertEqual([], self.report["lab_modules_loaded"])

    # -- Decide acceptance ----------------------------------------------------

    def test_decide_is_deterministic_over_a_real_initial_state(self):
        probe = self.report["decide"]
        self.assertTrue(probe["deterministic_repeat_identical"])
        self.assertTrue(probe["decision_json_roundtrip"])

    def test_decide_returns_the_contracted_decision_shape(self):
        probe = self.report["decide"]
        self.assertEqual(REQUIRED_DECISION_FIELDS, probe["decision_fields"])
        self.assertTrue(probe["action_in_actions"])
        self.assertTrue(probe["utilities_cover_actions"])
        self.assertEqual(4, probe["thread_count"])
        self.assertTrue(probe["confidence_in_unit_interval"])

    def test_decide_never_mutates_the_state(self):
        self.assertFalse(self.report["decide"]["state_mutated"])

    # -- SLIP v0.2 switchboard consumers (decision record 0013) ----------------

    def test_absent_learning_switches_run_every_thread_bit_for_bit(self):
        probe = self.report["decide_v2"]
        self.assertEqual(4, probe["baseline_thread_count"])
        self.assertTrue(probe["absent_switches_equal_all_on"])

    def test_a_disabled_thread_does_not_run_or_contribute(self):
        probe = self.report["decide_v2"]
        self.assertEqual(
            [
                "recent_interaction_ewma",
                "hidden_mood_estimator",
                "action_preference_bandit",
            ],
            probe["one_off_thread_names"],
        )
        self.assertTrue(probe["one_off_utilities_differ"])

    def test_all_switches_off_is_the_rules_only_idle_baseline(self):
        probe = self.report["decide_v2"]
        self.assertEqual(0, probe["all_off_thread_count"])
        self.assertEqual("idle", probe["all_off_action"])

    def test_risk_tolerance_raises_mutation_utility_monotonically(self):
        probe = self.report["decide_v2"]
        low, neutral, high = probe["mutate_utilities_by_tolerance"]
        self.assertLess(low, neutral)
        self.assertLess(neutral, high)
        # Explicit tolerance 0.35 is the neutral point: identical utilities
        # to the frozen baseline (the annotated thread fields differ by
        # design — they surface the tolerance).
        self.assertTrue(probe["neutral_tolerance_utilities_equal_baseline"])

    def test_risk_tolerance_is_surfaced_in_the_thread_record(self):
        probe = self.report["decide_v2"]
        self.assertTrue(probe["tolerance_in_thread_input"])
        self.assertTrue(probe["tolerance_explained"])
        self.assertTrue(probe["baseline_input_has_no_tolerance"])

    def test_v2_initial_states_gate_and_tolerate_end_to_end(self):
        probe = self.report["decide_v2"]
        self.assertEqual(
            [
                "recent_interaction_ewma",
                "action_preference_bandit",
                "mutation_risk_scorer",
            ],
            probe["v2_state_thread_names"],
        )
        self.assertTrue(probe["v2_state_tolerance_visible"])

    # -- Episode acceptance -----------------------------------------------------

    def test_both_arms_are_deterministic_and_json_serializable(self):
        probe = self.report["episodes"]
        self.assertTrue(probe["feedback_deterministic"])
        self.assertTrue(probe["frozen_deterministic"])
        self.assertTrue(probe["feedback_json_roundtrip"])
        self.assertTrue(probe["frozen_json_roundtrip"])

    def test_episode_report_mirrors_the_lab_shape(self):
        probe = self.report["episodes"]
        self.assertEqual(REQUIRED_EPISODE_FIELDS, probe["episode_fields"])
        self.assertEqual(
            REQUIRED_HISTORY_ENTRY_FIELDS, probe["history_entry_fields"]
        )
        self.assertEqual("feedback_switchboard", probe["feedback_policy"])
        self.assertEqual("frozen_switchboard", probe["frozen_policy"])
        self.assertTrue(probe["history_length_equals_survival_ticks"])

    def test_feedback_updates_count_ticks_survived_and_frozen_counts_zero(self):
        probe = self.report["episodes"]
        self.assertTrue(probe["feedback_updates_equal_ticks_survived"])
        self.assertEqual(
            SHELTERED_TICKS, probe["feedback_reward_update_count"]
        )
        self.assertEqual(0, probe["frozen_reward_update_count"])

    def test_frozen_arm_reward_memory_stays_at_the_initial_means(self):
        probe = self.report["episodes"]
        self.assertTrue(probe["frozen_final_means_equal_initial"])
        self.assertTrue(probe["feedback_final_means_differ_from_initial"])

    def test_sheltered_wellbeing_pin_feedback_beats_frozen_need_balance(self):
        # The bounded claim's sheltered measurement, computed in-driver from
        # the package surface: a wellbeing pin, never a survival claim (both
        # arms survive all 48 ticks; survival is morphology-decided).
        probe = self.report["episodes"]
        self.assertGreater(
            probe["feedback_need_balance"], probe["frozen_need_balance"]
        )
        self.assertEqual(
            SHELTERED_FEEDBACK_NEED_BALANCE, probe["feedback_need_balance"]
        )
        self.assertEqual(
            SHELTERED_FROZEN_NEED_BALANCE, probe["frozen_need_balance"]
        )
        self.assertEqual(
            SHELTERED_NEED_BALANCE_DELTA, probe["need_balance_delta"]
        )

    def test_sheltered_survival_is_policy_independent(self):
        probe = self.report["episodes"]
        self.assertEqual(SHELTERED_TICKS, probe["feedback_survival_ticks"])
        self.assertEqual(SHELTERED_TICKS, probe["frozen_survival_ticks"])
        self.assertTrue(probe["feedback_alive"])
        self.assertTrue(probe["frozen_alive"])

    # -- miscalibrate=False path --------------------------------------------------

    def test_miscalibrate_off_path_runs_and_is_deterministic(self):
        # No pin on its delta: the recorded learnable-gap measurements both
        # require the miscalibrated start (interface spec).
        probe = self.report["miscalibrate_off"]
        self.assertTrue(probe["deterministic_repeat_identical"])
        self.assertTrue(probe["episode_json_roundtrip"])
        self.assertEqual(REQUIRED_EPISODE_FIELDS, probe["episode_fields"])
        self.assertTrue(probe["feedback_updates_equal_ticks_survived"])
        self.assertEqual(0, probe["frozen_reward_update_count"])

    # -- Negative checks ------------------------------------------------------

    def test_episodes_never_mutate_caller_inputs(self):
        self.assertFalse(self.report["fixtures_mutated"])


if __name__ == "__main__":
    unittest.main()
