"""Pins for cycle 26 P2's landing: the `happiness` readout on screen.

DR 0058 adopted **`social_warmth`** — the mean of the engine's own
`recent_interactions` window (feed/play, last 5 ticks) — as the CHOSEN
definition of the documented VISIBLE axis `happiness`, through the
five-gate lab study (`labs/architecture/happiness_definition_gate.py`).
The O2 lesson binds: adopted-but-not-landed is the debt that quietly
becomes permanent, so the readout ships in the same slice.

The formula is MIRRORED into the game, never imported from a lab
(boundary law), and pinned against the committed lab artifact's
`game_mirror_parity_values`, so drift in either direction fails the
suite. The readout's legibility surface is engine truth only: the
number can fall for exactly one reason — the keeper stopped tending —
and the surface says so with the window's own counts, never an
invented word.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for _src in (
    ROOT / "game",
    ROOT / "game" / "src",
    ROOT / "packages" / "mecha_engine" / "src",
):
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))

from evidence import _new_session  # noqa: E402
from mecha_game.happiness import (  # noqa: E402
    happiness_readout,
    social_warmth,
)

COMMITTED_GATE = (
    ROOT / "data" / "architecture" / "happiness_definition_gate_stage0.json"
)


class MirrorParityTests(unittest.TestCase):
    """The game mirror against the committed lab artifact — drift in
    either direction fails the suite (the O2 health pattern)."""

    def test_the_mirror_reproduces_every_committed_parity_value(self):
        committed = json.loads(COMMITTED_GATE.read_text(encoding="utf-8"))
        parity = committed["metrics"]["game_mirror_parity_values"]
        self.assertTrue(parity)
        for entry in parity:
            self.assertEqual(
                social_warmth(entry["window"]), entry["value"], entry
            )

    def test_the_committed_gate_adopted_social_warmth(self):
        committed = json.loads(COMMITTED_GATE.read_text(encoding="utf-8"))
        self.assertEqual(committed["decision"]["adopted"], ["social_warmth"])


class ReadoutSurfaceTests(unittest.TestCase):
    def test_the_readout_says_what_it_is(self):
        state = {"recent_interactions": [1, 0, 1]}
        readout = happiness_readout(state)
        self.assertEqual(readout["label"], "happiness")
        self.assertEqual(readout["definition"], "social_warmth")
        self.assertTrue(readout["chosen"])
        self.assertEqual(readout["good_when"], "high")

    def test_the_number_is_the_window_mean(self):
        readout = happiness_readout({"recent_interactions": [1, 1, 0, 1, 1]})
        self.assertEqual(readout["value"], 0.8)

    def test_the_legibility_surface_is_the_window_itself(self):
        # O2's lesson: a number that can fall for a legible reason must
        # say why — here in engine truth, never an invented word.
        readout = happiness_readout({"recent_interactions": [0, 0, 0, 0, 1]})
        self.assertEqual(readout["tended_ticks"], 1)
        self.assertEqual(readout["window_ticks"], 5)

    def test_a_missing_window_reads_zero_not_an_error(self):
        readout = happiness_readout({})
        self.assertEqual(readout["value"], 0.0)
        self.assertEqual(readout["window_ticks"], 0)


class LiveClientTests(unittest.TestCase):
    """The measured case, from the live client (the O2 pattern)."""

    def test_snapshot_carries_the_happiness_readout(self):
        snapshot = _new_session().snapshot()
        self.assertIn("happiness", snapshot)
        self.assertEqual(snapshot["happiness"]["definition"], "social_warmth")
        self.assertTrue(snapshot["happiness"]["chosen"])

    def test_an_ignored_companion_reads_zero(self):
        session = _new_session()
        for _ in range(5):
            session.advance("sleep")
        self.assertEqual(session.snapshot()["happiness"]["value"], 0.0)

    def test_the_keeper_tending_raises_it(self):
        session = _new_session()
        for _ in range(5):
            session.advance("sleep")
        before = session.snapshot()["happiness"]["value"]
        session.advance("feed")
        after = session.snapshot()["happiness"]["value"]
        self.assertGreater(after, before)

    def test_play_raises_happiness_while_health_falls(self):
        # The differentiation the lab measured, reproduced in the live
        # client: the two readouts answer different questions, and the
        # keeper can see both move honestly in opposite directions.
        session = _new_session()
        for _ in range(3):
            session.advance("sleep")
        before = session.snapshot()
        session.advance("play")
        after = session.snapshot()
        self.assertGreater(
            after["happiness"]["value"], before["happiness"]["value"]
        )
        self.assertLess(after["health"]["value"], before["health"]["value"])

    def test_every_number_shown_is_engine_truth(self):
        # The readout's value equals the mirror applied to the state's
        # own window — nothing smoothed, nothing invented.
        session = _new_session()
        session.advance("feed")
        snapshot = session.snapshot()
        self.assertEqual(
            snapshot["happiness"]["value"],
            social_warmth(session.state["recent_interactions"]),
        )


if __name__ == "__main__":
    unittest.main()
