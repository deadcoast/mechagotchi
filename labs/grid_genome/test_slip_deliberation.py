import json
import sys
import unittest
from pathlib import Path

from corpus_builder import build_seed_grids
from micro_switchboard import run_switchboard
from slip import validate_slip

ROOT = Path(__file__).resolve().parents[2]
for extra in [ROOT / "labs" / "lifecycle_sim", ROOT / "labs" / "ctm_ticks"]:
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))

from ctm_inspired_ticks import run_deliberative_switchboard  # noqa: E402
from lifecycle_sim import initial_lifecycle_state  # noqa: E402


def _v2_profile(**overrides) -> dict:
    profile = json.loads(
        (ROOT / "data/slips/valid/slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )
    profile["slip_version"] = "0.2.0"
    profile["profile_id"] = "slip_v2_thinker"
    profile["deliberation"] = {"max_ticks": 4, "confidence_threshold": 0.72}
    profile.update(overrides)
    return profile


# A torn state: utilities nearly tie, so baseline confidence is low and
# deliberation has real work to do.
TORN_STATE = {
    "hunger": 0.52,
    "energy": 0.5,
    "stress": 0.32,
    "bond": 0.5,
    "grid_stability": 0.55,
    "recent_interactions": [1, 0, 1],
    "action_rewards": {},
}


class DeliberationValidationTests(unittest.TestCase):
    """R1 (DR 0017): the CTM deliberation field, version-gated."""

    def test_v2_profile_with_deliberation_validates(self):
        result = validate_slip(_v2_profile())
        self.assertEqual([], result.errors)

    def test_v1_profile_with_deliberation_is_version_gated(self):
        result = validate_slip(_v2_profile(slip_version="0.1.0"))
        self.assertFalse(result.ok)
        self.assertTrue(any("0.2.0" in error for error in result.errors))

    def test_bad_shapes_are_rejected(self):
        for deliberation in (
            {"max_ticks": 1, "confidence_threshold": 0.7},  # <2 pointless
            {"max_ticks": 9, "confidence_threshold": 0.7},  # runaway cap
            {"max_ticks": 4, "confidence_threshold": 1.5},
            {"max_ticks": 4},
            {"confidence_threshold": 0.7},
            {"max_ticks": True, "confidence_threshold": 0.7},
            {"unknown": 1},
            {},
        ):
            result = validate_slip(_v2_profile(deliberation=deliberation))
            self.assertFalse(result.ok, deliberation)


class DeliberationConsumerTests(unittest.TestCase):
    """The live switchboard deliberates with the CTM lab's exact semantics."""

    def test_live_path_matches_the_ctm_lab_verbatim(self):
        lab = run_deliberative_switchboard(
            dict(TORN_STATE), max_ticks=4, confidence_threshold=0.72
        )
        live = run_switchboard(
            dict(
                TORN_STATE,
                deliberation_max_ticks=4,
                deliberation_confidence_threshold=0.72,
            )
        )
        self.assertEqual(
            lab["final_decision"]["action"], live["action"]
        )
        self.assertEqual(
            lab["final_decision"]["utilities"], live["utilities"]
        )
        self.assertEqual(lab["tick_count"], live["deliberation"]["tick_count"])
        self.assertGreater(live["deliberation"]["tick_count"], 1)

    def test_confident_states_act_immediately(self):
        confident = dict(
            TORN_STATE,
            energy=0.05,  # exhausted: sleep dominates
            deliberation_max_ticks=4,
            deliberation_confidence_threshold=0.72,
        )
        decision = run_switchboard(confident)
        self.assertEqual(1, decision["deliberation"]["tick_count"])

    def test_absent_keys_are_bit_for_bit_frozen(self):
        baseline = run_switchboard(dict(TORN_STATE))
        self.assertNotIn("deliberation", baseline)


class DeliberationLifecycleWiringTests(unittest.TestCase):
    def test_v2_profile_stashes_deliberation_into_state(self):
        state = initial_lifecycle_state(build_seed_grids()[0], _v2_profile())
        self.assertEqual(4, state["deliberation_max_ticks"])
        self.assertEqual(0.72, state["deliberation_confidence_threshold"])

    def test_v1_profile_leaves_state_untouched(self):
        profile = _v2_profile(slip_version="0.1.0")
        del profile["deliberation"]
        state = initial_lifecycle_state(build_seed_grids()[0], profile)
        self.assertNotIn("deliberation_max_ticks", state)


if __name__ == "__main__":
    unittest.main()
