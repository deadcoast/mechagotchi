"""Parity pin: lab switchboard vs mecha_engine.learning.decide on v0.2 states.

The frozen v0.1 pin (``test_package_learning_parity.py``: ``decide`` equal
to the lab ``run_switchboard`` over every state visited by a full feedback
episode) stays untouched. This file adds the decision-record-0013 surface:
package ``decide`` must equal the lab ``run_switchboard`` over states
carrying the SLIP v0.2 ladder keys — ``learning_switches`` (thread gating,
every single-off combination plus all-off/all-on) and
``risk_tolerance_mutation`` (the mutation-risk flip point, across the
tolerance range including the 0.35 neutral point and the clamp edges) —
and over real v0.2 lifecycle states produced by
``initial_lifecycle_state`` with a ladder-carrying profile, advanced
through several ticks.

Direction note: labs may import the package for regression evidence; the
reverse (package importing labs) stays forbidden by the learning interface
spec, and this file lives on the lab side precisely so the package tree
keeps zero lab references.
"""

import json
import sys
import unittest
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
LIFECYCLE = REPO_ROOT / "labs" / "lifecycle_sim"
PACKAGE_SRC = REPO_ROOT / "packages" / "mecha_engine" / "src"
for path in [LAB_DIR, LIFECYCLE]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from corpus_builder import build_seed_grids  # noqa: E402
from lifecycle_sim import (  # noqa: E402
    advance_tick as lab_advance_tick,
    initial_lifecycle_state,
)
from micro_switchboard import (  # noqa: E402
    SWITCHBOARD_THREAD_NAMES,
    run_switchboard,
)

from mecha_engine.learning import decide  # noqa: E402


STRESSED = {
    "hunger": 0.4,
    "energy": 0.6,
    "stress": 0.7,
    "grid_stability": 0.4,
    "recent_interactions": [1, 1],
    "action_rewards": {},
}
TOLERANCES = [0.0, 0.1, 0.35, 0.6, 0.9, 1.0, 1.5, -0.5]  # clamp edges included


def load_lcd_slip() -> dict:
    return json.loads(
        (REPO_ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )


class SwitchboardV2GatingParityTests(unittest.TestCase):
    def test_every_single_switch_combination_matches_the_lab(self):
        combos = [
            {},
            {name: True for name in SWITCHBOARD_THREAD_NAMES},
            {name: False for name in SWITCHBOARD_THREAD_NAMES},
        ] + [{name: False} for name in SWITCHBOARD_THREAD_NAMES]
        for switches in combos:
            state = dict(STRESSED)
            if switches:
                state["learning_switches"] = dict(switches)
            with self.subTest(switches=switches):
                self.assertEqual(run_switchboard(state), decide(state))

    def test_tolerance_range_matches_the_lab_including_clamp_edges(self):
        for tolerance in TOLERANCES:
            state = dict(STRESSED, risk_tolerance_mutation=tolerance)
            with self.subTest(tolerance=tolerance):
                self.assertEqual(run_switchboard(state), decide(state))

    def test_switches_and_tolerance_combined_match_the_lab(self):
        state = dict(
            STRESSED,
            risk_tolerance_mutation=0.9,
            learning_switches={"hidden_mood_estimator": False},
        )
        self.assertEqual(run_switchboard(state), decide(state))
        gated_off = dict(
            STRESSED,
            risk_tolerance_mutation=0.9,
            learning_switches={"mutation_risk_scorer": False},
        )
        self.assertEqual(run_switchboard(gated_off), decide(gated_off))


class SwitchboardV2LifecycleStateParityTests(unittest.TestCase):
    def test_decide_matches_the_lab_over_real_v2_states(self):
        grid = build_seed_grids()[0]
        profile = load_lcd_slip()
        profile["slip_version"] = "0.2.0"
        profile["risk_tolerances"] = {"mutation": 0.8}
        profile["learning_switches"] = {"hidden_mood_estimator": False}
        state = initial_lifecycle_state(grid, profile)
        self.assertIn("risk_tolerance_mutation", state)
        self.assertIn("learning_switches", state)
        for tick, action in enumerate(
            ["feed", "play", "idle", "sleep", "mutate", "idle", "play", "feed"]
        ):
            with self.subTest(tick=tick):
                lab_decision = run_switchboard(state)
                self.assertEqual(lab_decision, decide(state))
                state = lab_advance_tick(state, action)


if __name__ == "__main__":
    unittest.main()
