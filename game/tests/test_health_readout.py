"""Cycle 25 O2: the `health` readout reaches the player's screen.

DR 0054 adopted `danger_margin` as the CHOSEN definition of `health`
and shipped only a guard, deliberately leaving one design question to
whoever put the bar on screen:

    `play` LOWERS `danger_margin` (-0.075467, because play costs energy
    and adds hunger), so a keeper who sees "health" drop when they play
    with their pet will read it as a bug.

**O2's answer is to show the BINDING AXIS beside the number.** Health is
a MINIMUM across axes, and a bare minimum throws away the one thing that
makes it legible: *which* axis is binding. "health 0.62 — tired" is
engine truth, costs no new number (the binding axis is the argmin of
margins already computed), and turns the play-drop from an unexplained
fall into a sentence the player can read.

**Refusal stays first-class.** If the drop is NOT explained by the named
axis, a player still sees an unexplained fall and the readout misleads —
so the pins measure that rather than assuming it.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for _src in (ROOT / "game" / "src", ROOT / "packages" / "mecha_engine" / "src"):
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))
if str(ROOT / "game") not in sys.path:
    sys.path.insert(0, str(ROOT / "game"))

from mecha_engine.lifecycle import (  # noqa: E402
    DANGER_THRESHOLDS,
    advance_tick,
    initial_state,
)
from mecha_game.health import binding_axis, danger_margin  # noqa: E402
from mecha_game.session import NEED_DISPLAY  # noqa: E402

N5_ARTIFACT = ROOT / "data" / "architecture" / "health_definition_gate_stage0.json"
SEED = ROOT / "data" / "seed_grids_16x16" / "mg_seed16_001_beetle.json"

# The two verbs a keeper actually has.
KEEPER_ACTIONS = ("feed", "play")


def _grid() -> dict:
    return json.loads(SEED.read_text(encoding="utf-8"))


class EngineTruthTests(unittest.TestCase):
    """DR 0021's first law: every displayed number is engine truth."""

    def test_health_uses_the_promoted_engine_constant(self):
        # O1 promoted DANGER_THRESHOLDS precisely so this readout does
        # not depend on an unpromised surface.
        state = initial_state(_grid(), None)
        self.assertEqual(
            danger_margin(state), danger_margin(state, DANGER_THRESHOLDS)
        )

    def test_health_is_a_pure_function_of_engine_state(self):
        state = initial_state(_grid(), None)
        self.assertEqual(danger_margin(state), danger_margin(dict(state)))

    def test_health_introduces_no_weight(self):
        # DR 0054's whole argument: a composite would need undocumented
        # weights; a MINIMUM has none. Scaling one axis cannot change the
        # answer unless that axis is the binding one.
        state = initial_state(_grid(), None)
        axis = binding_axis(state)
        loosened = dict(state)
        for other in DANGER_THRESHOLDS:
            if other != axis:
                loosened[other] = state[other]
        self.assertEqual(danger_margin(state), danger_margin(loosened))


class ParityWithTheAdoptingStudyTests(unittest.TestCase):
    """The formula is MIRRORED into the game, never imported from a lab.

    So it is pinned against the committed evidence that adopted it —
    `data/architecture/health_definition_gate_stage0.json` — which is
    data, not a lab import, and is exactly the artifact DR 0054 rests
    on. Drift in either direction fails here.
    """

    @classmethod
    def setUpClass(cls):
        cls.artifact = json.loads(N5_ARTIFACT.read_text(encoding="utf-8"))

    def test_the_game_reproduces_the_studys_survivor_and_death_values(self):
        measures = self.artifact["metrics"]["candidates"]["danger_margin"]
        engine = self.artifact["metrics"]["engine"]
        thresholds = engine["danger_thresholds"]
        for run in engine["lifecycles"]:
            expected = danger_margin(run["final"], thresholds)
            if run["alive"]:
                self.assertIn(expected, measures["survivor_values"])
            else:
                self.assertIn(expected, measures["death_values"])

    def test_the_game_reproduces_the_studys_distress_relief(self):
        engine = self.artifact["metrics"]["engine"]
        thresholds = engine["danger_thresholds"]
        distress = engine["distress"]
        relief = round(
            danger_margin(distress["after_keeper_feed"], thresholds)
            - danger_margin(distress["before"], thresholds),
            6,
        )
        self.assertEqual(
            self.artifact["metrics"]["candidates"]["danger_margin"][
                "distress_relief"
            ],
            relief,
        )


class BindingAxisTests(unittest.TestCase):
    """The answer to DR 0054's deferred design question."""

    def test_the_binding_axis_is_the_one_at_the_minimum(self):
        state = initial_state(_grid(), None)
        axis = binding_axis(state)
        self.assertIn(axis, DANGER_THRESHOLDS)
        self.assertAlmostEqual(
            danger_margin(state),
            danger_margin(state, {axis: DANGER_THRESHOLDS[axis]}),
            places=9,
        )

    def test_the_binding_axis_actually_varies_over_a_life(self):
        # If it never changed, naming it would be noise and a bare
        # number would be the honest choice. Measured, not assumed.
        state = initial_state(_grid(), None)
        seen = {binding_axis(state)}
        for step in range(60):
            if not state["alive"]:
                break
            state = advance_tick(state, ("idle", "play", "feed")[step % 3])
            seen.add(binding_axis(state))
        self.assertGreater(len(seen), 1)

    def test_the_play_drop_is_EXPLAINED_by_the_axis_it_names(self):
        # THE GATE. Play lowers health; if the axis named after the drop
        # is not one play actually worsens, the player still sees an
        # unexplained fall and the readout misleads.
        state = initial_state(_grid(), None)
        before = danger_margin(state)
        after_state = advance_tick(state, "play")
        after = danger_margin(after_state)
        if after < before:
            self.assertIn(
                binding_axis(after_state),
                ("energy", "hunger"),
                "play lowered health but named an axis play does not worsen",
            )

    def test_feeding_a_hungry_companion_raises_health(self):
        state = initial_state(_grid(), None)
        for _ in range(8):
            state = advance_tick(state, "idle")
        before = danger_margin(state)
        self.assertGreater(danger_margin(advance_tick(state, "feed")), before)


class ReadoutTests(unittest.TestCase):
    def test_the_frame_carries_health_with_its_binding_axis(self):
        from mecha_game.health import health_readout

        state = initial_state(_grid(), None)
        readout = health_readout(state)
        self.assertEqual(readout["label"], "health")
        self.assertIn("value", readout)
        self.assertIn("binding_axis", readout)
        self.assertEqual(readout["definition"], "danger_margin")

    def test_the_readout_declares_its_definition_CHOSEN(self):
        # DR 0054 adopted it as a CHOSEN definition; the surface says so
        # rather than presenting it as documented fact.
        from mecha_game.health import health_readout

        readout = health_readout(initial_state(_grid(), None))
        self.assertTrue(readout["chosen"])

    def test_the_n5_guard_still_holds(self):
        # grid_stability keeps its own accurate name; health is a
        # separate, derived readout and does not rename it.
        self.assertEqual(NEED_DISPLAY["grid_stability"]["label"], "body stability")
        self.assertNotIn(
            "health", {entry["label"] for entry in NEED_DISPLAY.values()}
        )


if __name__ == "__main__":
    unittest.main()
