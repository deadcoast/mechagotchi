"""Pins for cycle 26 P3's landing: the opt-in cleanliness mechanic in the client.

DR 0059 adopted the engine's opt-in cleanliness mechanic through the
five-gate lab study. The landing is OPT-IN end to end: a session
constructed with ``mechanics=("cleanliness",)`` shows the axis in its
needs (engine truth — the state's own value, verbatim), offers the
keeper the ``clean`` verb, and preserves the mechanic across succession
and save/resume. A DEFAULT session is byte-identical to the pre-seam
client: no cleanliness anywhere in the snapshot, no clean verb, and the
engine's own verbatim refusal if one is attempted.
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

import tempfile  # noqa: E402

from evidence import _new_session  # noqa: E402
from mecha_game.packets import HELLO_SEED, HELLO_SLIP  # noqa: E402
from mecha_game.session import (  # noqa: E402
    CompanionSession,
    load_session_inputs,
)


def _opt_in_session() -> CompanionSession:
    grid, slip_profile, model = load_session_inputs(
        ROOT / HELLO_SEED, ROOT / HELLO_SLIP
    )
    return CompanionSession(
        grid,
        slip_profile,
        model=model,
        mechanics=("cleanliness",),
    )


class DefaultSessionTests(unittest.TestCase):
    """Byte-identical when off — the client side of the seam law."""

    def test_a_default_session_never_mentions_cleanliness(self):
        snapshot = _new_session().snapshot()
        self.assertNotIn("cleanliness", json.dumps(snapshot).lower())

    def test_a_default_session_offers_no_clean_verb(self):
        snapshot = _new_session().snapshot()
        self.assertNotIn("clean", snapshot["actions"])

    def test_cleaning_without_the_mechanic_is_refused_verbatim(self):
        session = _new_session()
        with self.assertRaises(ValueError) as caught:
            session.advance("clean")
        self.assertIn("unsupported lifecycle action: clean", str(caught.exception))


class OptInSessionTests(unittest.TestCase):
    def test_the_readout_appears_in_the_needs(self):
        needs = _opt_in_session().snapshot()["needs"]
        self.assertIn("cleanliness", needs)
        self.assertEqual(needs["cleanliness"]["label"], "cleanliness")
        self.assertEqual(needs["cleanliness"]["good_when"], "high")

    def test_the_number_is_the_engine_state_verbatim(self):
        session = _opt_in_session()
        session.advance("feed")
        self.assertEqual(
            session.snapshot()["needs"]["cleanliness"]["value"],
            session.state["cleanliness"],
        )

    def test_the_need_falls_over_a_tended_life(self):
        session = _opt_in_session()
        before = session.snapshot()["needs"]["cleanliness"]["value"]
        for action in ("feed", "play", "sleep"):
            session.advance(action)
        after = session.snapshot()["needs"]["cleanliness"]["value"]
        self.assertLess(after, before)

    def test_the_keeper_can_clean(self):
        session = _opt_in_session()
        for action in ("feed", "play", "sleep", "feed", "play", "sleep"):
            session.advance(action)
        before = session.state["cleanliness"]
        session.advance("clean")
        self.assertGreater(session.state["cleanliness"], before)

    def test_the_clean_verb_is_offered(self):
        self.assertIn("clean", _opt_in_session().snapshot()["actions"])

    def test_succession_preserves_the_mechanic(self):
        session = _opt_in_session()
        while session.alive:
            session.advance()  # autonomy without keeper care ends in death
        session.succeed()
        self.assertIn("cleanliness", session.state)

    def test_save_and_resume_preserve_the_mechanic(self):
        session = _opt_in_session()
        session.advance("feed")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "keeper_session.json"
            session.save(path)
            resumed = CompanionSession.load(path)
        self.assertIn("cleanliness", resumed.state)
        before = resumed.state["cleanliness"]
        resumed.advance("clean")
        self.assertGreaterEqual(resumed.state["cleanliness"], before)


if __name__ == "__main__":
    unittest.main()
