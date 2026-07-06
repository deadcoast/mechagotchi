import sys
import unittest
from pathlib import Path

from corpus_builder import build_seed_grids
from micro_switchboard import SWITCHBOARD_THREAD_NAMES, run_switchboard
from slip import validate_slip

ROOT = Path(__file__).resolve().parents[2]
LIFECYCLE = ROOT / "labs" / "lifecycle_sim"
if str(LIFECYCLE) not in sys.path:
    sys.path.insert(0, str(LIFECYCLE))

from lifecycle_sim import initial_lifecycle_state  # noqa: E402


def _v2_profile(**overrides) -> dict:
    profile = {
        "slip_version": "0.2.0",
        "profile_id": "slip_v2_switch_test",
        "name": "V2 Switch Test",
        "grid": {
            "allowed_palettes": ["lcd_green"],
            "body_mass_min": 4,
            "body_mass_max": 24,
            "required_organ_roles": ["sensor", "expression"],
        },
        "mutation": {
            "cell_mutation_rate_max": 0.15,
            "organ_shift_rate_max": 0.05,
            "palette_shift_rate_max": 0.05,
            "symmetry_break_rate_max": 0.05,
        },
        "behavior": {"curiosity": 0.6, "neediness": 0.4, "sleepiness": 0.5},
        "survival_weights": {"stability": 0.5, "novelty": 0.25, "bond": 0.25},
        "learning_switches": {"mutation_risk_scorer": False},
    }
    profile.update(overrides)
    return profile


class LearningSwitchesValidationTests(unittest.TestCase):
    """DR 0012 rung T3.3: the og learning toggles, version-gated."""

    def test_v2_profile_with_switches_validates(self):
        result = validate_slip(_v2_profile())
        self.assertEqual([], result.errors)

    def test_v1_profile_with_switches_is_version_gated(self):
        result = validate_slip(_v2_profile(slip_version="0.1.0"))
        self.assertFalse(result.ok)
        self.assertTrue(any("0.2.0" in error for error in result.errors))

    def test_bad_shapes_are_rejected(self):
        for switches in (
            {"unknown_thread": False},
            {"mutation_risk_scorer": "off"},
            {"mutation_risk_scorer": 0},
            {},
            ["mutation_risk_scorer"],
        ):
            result = validate_slip(_v2_profile(learning_switches=switches))
            self.assertFalse(result.ok, switches)

    def test_switch_names_pin_to_the_switchboard(self):
        self.assertEqual(
            {
                "recent_interaction_ewma",
                "hidden_mood_estimator",
                "action_preference_bandit",
                "mutation_risk_scorer",
            },
            set(SWITCHBOARD_THREAD_NAMES),
        )


class LearningSwitchConsumerTests(unittest.TestCase):
    STRESSED = {
        "hunger": 0.4,
        "energy": 0.6,
        "stress": 0.7,
        "grid_stability": 0.4,
        "recent_interactions": [1, 1],
        "action_rewards": {},
    }

    def test_absent_switches_run_every_thread_bit_for_bit(self):
        baseline = run_switchboard(dict(self.STRESSED))
        all_on = run_switchboard(
            dict(
                self.STRESSED,
                learning_switches={name: True for name in SWITCHBOARD_THREAD_NAMES},
            )
        )
        self.assertEqual(baseline, all_on)
        self.assertEqual(4, len(baseline["threads"]))

    def test_a_disabled_thread_does_not_run_or_contribute(self):
        decision = run_switchboard(
            dict(
                self.STRESSED,
                learning_switches={"mutation_risk_scorer": False},
            )
        )
        names = [thread["name"] for thread in decision["threads"]]
        self.assertNotIn("mutation_risk_scorer", names)
        self.assertEqual(3, len(names))
        baseline = run_switchboard(dict(self.STRESSED))
        self.assertNotEqual(
            baseline["utilities"], decision["utilities"]
        )

    def test_all_off_is_the_rules_only_baseline(self):
        decision = run_switchboard(
            dict(
                self.STRESSED,
                learning_switches={
                    name: False for name in SWITCHBOARD_THREAD_NAMES
                },
            )
        )
        self.assertEqual([], decision["threads"])
        self.assertEqual("idle", decision["action"])


class LearningSwitchLifecycleWiringTests(unittest.TestCase):
    def test_v2_profile_stashes_switches_into_state(self):
        state = initial_lifecycle_state(build_seed_grids()[0], _v2_profile())
        self.assertEqual(
            {"mutation_risk_scorer": False}, state["learning_switches"]
        )

    def test_v1_profile_leaves_state_untouched(self):
        profile = _v2_profile(slip_version="0.1.0")
        del profile["learning_switches"]
        state = initial_lifecycle_state(build_seed_grids()[0], profile)
        self.assertNotIn("learning_switches", state)


if __name__ == "__main__":
    unittest.main()
