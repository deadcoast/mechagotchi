"""Parity pin: lab lifecycle vs mecha_engine.lifecycle on SLIP v0.2 inputs.

The frozen v0.1 pin (``test_package_lifecycle_parity.py``) stays untouched.
This file adds the decision-record-0013 surface: with a v0.2 profile the
package ``initial_state`` must stash ``risk_tolerance_mutation`` and
``learning_switches`` exactly as the lab ``initial_lifecycle_state`` does
(and omit both for v0.1 profiles, byte-identically), and full episodes over
v0.2 profiles must stay byte-identical to the lab — which pins that the
package's episode-side switchboard consumes the stashed keys with the
lab's exact gating and tolerance semantics (the lab consumes them through
``micro_switchboard.run_switchboard``; the package through its private
policy port).

Direction note: labs may import the package for regression evidence; the
reverse (package importing labs) stays forbidden by the lifecycle contract
gate, and this file lives on the lab side precisely so the package tree
keeps zero lab references.
"""

import json
import sys
import unittest
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
GRID_GENOME = REPO_ROOT / "labs" / "grid_genome"
PACKAGE_SRC = REPO_ROOT / "packages" / "mecha_engine" / "src"
for path in [LAB_DIR, GRID_GENOME]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from corpus_builder import build_seed_grids  # noqa: E402
from lifecycle_sim import (  # noqa: E402
    advance_tick as lab_advance_tick,
    initial_lifecycle_state,
    run_lifecycle_simulation,
)

from mecha_engine.lifecycle import (  # noqa: E402
    advance_tick as package_advance_tick,
    initial_state,
    run_episode,
)


POLICIES = ["switchboard", "idle", "random"]


def _v2_profile(**ladder_fields) -> dict:
    profile = json.loads(
        (REPO_ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )
    profile["slip_version"] = "0.2.0"
    profile.update(ladder_fields)
    return profile


FULL_LADDER = dict(
    risk_tolerances={"mutation": 0.8},
    learning_switches={"hidden_mood_estimator": False},
    forbidden_traits={"roles": ["shell"], "materials": ["light"]},
    lineage_preferences={"parent_selection": "fitness_weighted"},
)


class PackageLifecycleV2StateParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid = build_seed_grids()[0]

    def test_v2_initial_state_parity_with_full_ladder(self):
        profile = _v2_profile(**FULL_LADDER)
        lab_state = initial_lifecycle_state(self.grid, profile)
        package_state = initial_state(self.grid, profile)
        self.assertEqual(lab_state, package_state)
        self.assertEqual(0.8, package_state["risk_tolerance_mutation"])
        self.assertEqual(
            {"hidden_mood_estimator": False}, package_state["learning_switches"]
        )

    def test_v2_initial_state_parity_per_single_rung(self):
        for field, value in [
            ("risk_tolerances", {"mutation": 0.15}),
            ("learning_switches", {"mutation_risk_scorer": False}),
            ("forbidden_traits", {"roles": ["shell"]}),
            ("lineage_preferences", {"parent_selection": "uniform"}),
        ]:
            with self.subTest(field=field):
                profile = _v2_profile(**{field: value})
                self.assertEqual(
                    initial_lifecycle_state(self.grid, profile),
                    initial_state(self.grid, profile),
                )

    def test_v1_states_omit_the_ladder_keys_byte_identically(self):
        profile = json.loads(
            (
                REPO_ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
            ).read_text(encoding="utf-8")
        )
        lab_state = initial_lifecycle_state(self.grid, profile)
        package_state = initial_state(self.grid, profile)
        self.assertEqual(lab_state, package_state)
        self.assertNotIn("risk_tolerance_mutation", package_state)
        self.assertNotIn("learning_switches", package_state)

    def test_v2_transition_parity_for_every_action(self):
        profile = _v2_profile(**FULL_LADDER)
        for action in ["feed", "sleep", "play", "idle", "mutate"]:
            with self.subTest(action=action):
                self.assertEqual(
                    lab_advance_tick(
                        initial_lifecycle_state(self.grid, profile), action
                    ),
                    package_advance_tick(
                        initial_state(self.grid, profile), action
                    ),
                )


class PackageLifecycleV2EpisodeParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid = build_seed_grids()[0]

    def test_v2_episode_parity_across_policies(self):
        profile = _v2_profile(**FULL_LADDER)
        for policy in POLICIES:
            with self.subTest(policy=policy):
                self.assertEqual(
                    run_lifecycle_simulation(
                        self.grid, profile, ticks=72, policy=policy,
                        rng_seed=20260512,
                    ),
                    run_episode(
                        self.grid, profile, policy=policy, ticks=72,
                        rng_seed=20260512,
                    ),
                )

    def test_v2_episode_parity_across_tolerances_and_switch_combos(self):
        cases = [
            dict(risk_tolerances={"mutation": 0.0}),
            dict(risk_tolerances={"mutation": 1.0}),
            dict(learning_switches={"action_preference_bandit": False}),
            dict(
                risk_tolerances={"mutation": 0.9},
                learning_switches={
                    "recent_interaction_ewma": False,
                    "mutation_risk_scorer": True,
                },
            ),
        ]
        for ladder_fields in cases:
            with self.subTest(ladder=ladder_fields):
                profile = _v2_profile(**ladder_fields)
                self.assertEqual(
                    run_lifecycle_simulation(
                        self.grid, profile, ticks=96, policy="switchboard",
                        rng_seed=777,
                    ),
                    run_episode(
                        self.grid, profile, policy="switchboard", ticks=96,
                        rng_seed=777,
                    ),
                )


if __name__ == "__main__":
    unittest.main()
