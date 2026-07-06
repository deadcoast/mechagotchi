import sys
import unittest
from pathlib import Path

from corpus_builder import build_seed_grids
from micro_switchboard import mutation_risk_scorer, run_switchboard
from slip import validate_slip

ROOT = Path(__file__).resolve().parents[2]
LIFECYCLE = ROOT / "labs" / "lifecycle_sim"
if str(LIFECYCLE) not in sys.path:
    sys.path.insert(0, str(LIFECYCLE))

from lifecycle_sim import initial_lifecycle_state  # noqa: E402


def _v2_profile(**overrides) -> dict:
    profile = {
        "slip_version": "0.2.0",
        "profile_id": "slip_v2_risk_test",
        "name": "V2 Risk Test",
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
        "risk_tolerances": {"mutation": 0.8},
    }
    profile.update(overrides)
    return profile


class RiskTolerancesValidationTests(unittest.TestCase):
    """DR 0012 rung T3.2, version-gated like every ladder field."""

    def test_v2_profile_with_risk_tolerances_validates(self):
        result = validate_slip(_v2_profile())
        self.assertEqual([], result.errors)

    def test_v1_profile_with_risk_tolerances_is_version_gated(self):
        result = validate_slip(_v2_profile(slip_version="0.1.0"))
        self.assertFalse(result.ok)
        self.assertTrue(any("0.2.0" in error for error in result.errors))

    def test_bad_shapes_are_rejected(self):
        for tolerances in (
            {"mutation": 1.5},
            {"mutation": True},
            {"unknown": 0.5},
            {},
            "high",
        ):
            result = validate_slip(_v2_profile(risk_tolerances=tolerances))
            self.assertFalse(result.ok, tolerances)


class RiskToleranceConsumerTests(unittest.TestCase):
    """The census-designed consumer: mutation_risk_scorer under stress."""

    STRESSED = {
        "hunger": 0.4,
        "energy": 0.6,
        "stress": 0.7,
        "grid_stability": 0.4,
        "recent_interactions": [1, 1],
        "action_rewards": {},
    }

    def test_absent_tolerance_is_utility_identical_to_baseline(self):
        # Explicit tolerance 0.35 is the neutral point: same utilities and
        # action as the frozen baseline (the annotated explanation/input
        # fields differ by design — they surface the tolerance).
        baseline = run_switchboard(dict(self.STRESSED))
        neutral = run_switchboard(
            dict(self.STRESSED, risk_tolerance_mutation=0.35)
        )
        self.assertEqual(baseline["utilities"], neutral["utilities"])
        self.assertEqual(baseline["action"], neutral["action"])

    def test_tolerance_monotonically_raises_mutation_utility(self):
        utilities = []
        for tolerance in (0.1, 0.35, 0.9):
            state = dict(self.STRESSED, risk_tolerance_mutation=tolerance)
            utilities.append(run_switchboard(state)["utilities"]["mutate"])
        self.assertLess(utilities[0], utilities[1])
        self.assertLess(utilities[1], utilities[2])

    def test_thread_explains_the_tolerance_when_set(self):
        thread = mutation_risk_scorer(
            dict(self.STRESSED, risk_tolerance_mutation=0.9)
        )
        self.assertIn("risk_tolerance_mutation", thread["input"])
        self.assertIn("risk tolerance", thread["explanation"])
        thread_default = mutation_risk_scorer(dict(self.STRESSED))
        self.assertNotIn("risk_tolerance_mutation", thread_default["input"])


class RiskToleranceLifecycleWiringTests(unittest.TestCase):
    def test_v2_profile_stashes_the_tolerance_into_state(self):
        state = initial_lifecycle_state(build_seed_grids()[0], _v2_profile())
        self.assertEqual(0.8, state["risk_tolerance_mutation"])

    def test_v1_profile_leaves_state_untouched(self):
        profile = _v2_profile(slip_version="0.1.0")
        del profile["risk_tolerances"]
        state = initial_lifecycle_state(build_seed_grids()[0], profile)
        self.assertNotIn("risk_tolerance_mutation", state)


if __name__ == "__main__":
    unittest.main()
