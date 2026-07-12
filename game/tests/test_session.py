"""F2 gates — the companion loop as a product (MVP 0.1).

Every beat is the engine's own machinery, in the DOCUMENTED game
interaction model (D5's honest zero forced it; D6 operationalized it;
DR 0021 names it): the companion cannot feed itself — its autonomous
"feed" decision is a BEG DISPLAY executed as idle, and only the
keeper's feed fills hunger. Death is honest and refusal-not-noop
(W1 semantics); succession is `generation.generate_candidate` from
the dead parent (lineage preserved by the engine, never invented);
the lineage file records verbatim engine blocks. Deterministic: the
only nondeterminism in a companion's life is the player.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for _src in (ROOT / "game" / "src", ROOT / "packages" / "mecha_engine" / "src"):
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))

from mecha_game.session import (  # noqa: E402
    HISTORY_WINDOW,
    CompanionSession,
    load_session_inputs,
)

SEED_PATH = ROOT / "data" / "seed_grids_16x16" / "mg_seed16_001_beetle.json"
SLIP_PATH = ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"


def _session(name: str = "test") -> CompanionSession:
    grid, slip_profile, model = load_session_inputs(SEED_PATH, SLIP_PATH)
    return CompanionSession(grid, slip_profile, model=model, name=name)


def _run_to_death(session: CompanionSession, limit: int = 400) -> None:
    for _ in range(limit):
        if not session.alive:
            return
        session.advance()
    raise AssertionError("companion did not die within the limit")


class SessionLoopTests(unittest.TestCase):
    def test_adoption_is_the_engines_gate(self):
        session = _session()
        self.assertTrue(session.alive)
        self.assertEqual(0, session.state["age_ticks"])
        self.assertEqual(1, len(session.lineage))
        self.assertEqual(
            session.grid["grid_id"], session.lineage[0]["grid_id"]
        )

    def test_keeper_action_is_the_engine_vocabulary(self):
        session = _session()
        session.advance(player_action="feed")
        entry = session.log[-1]
        self.assertEqual("keeper", entry["actor"])
        self.assertEqual("feed", entry["action"])
        self.assertEqual(1, session.state["age_ticks"])
        with self.assertRaises(ValueError):
            session.advance(player_action="tickle")

    def test_beg_mediation_is_the_documented_model(self):
        # Drive hunger above the reflex threshold: the autonomous
        # decision becomes feed -> the companion BEGS and idles; only
        # the keeper's feed fills hunger (D6 semantics).
        session = _session()
        session.state = dict(session.state)
        session.state["hunger"] = 0.9
        hunger_before = session.state["hunger"]
        session.advance()
        self.assertTrue(session.begging)
        entry = session.log[-1]
        self.assertEqual("companion", entry["actor"])
        self.assertEqual("idle", entry["action"])
        self.assertTrue(entry["begging"])
        self.assertGreaterEqual(session.state["hunger"], hunger_before)
        # The keeper answers: hunger falls.
        session.advance(player_action="feed")
        self.assertLess(session.state["hunger"], hunger_before)

    def test_autonomous_non_feed_decisions_execute(self):
        session = _session()
        session.state = dict(session.state)
        session.state["energy"] = 0.05  # the sleep reflex
        session.advance()
        entry = session.log[-1]
        self.assertEqual("companion", entry["actor"])
        self.assertEqual("sleep", entry["action"])
        self.assertFalse(entry["begging"])

    def test_neglect_kills_and_death_is_refusal_not_noop(self):
        session = _session()
        _run_to_death(session)
        self.assertFalse(session.alive)
        self.assertTrue(session.death_cause)
        self.assertEqual(
            session.death_cause, session.lineage[-1]["death_cause"]
        )
        with self.assertRaises(ValueError):
            session.advance()

    def test_succession_is_the_engines_child(self):
        session = _session()
        _run_to_death(session)
        parent_id = session.grid["grid_id"]
        with self.assertRaises(ValueError):
            # A living companion cannot be succeeded — but a dead one
            # cannot be tended; succeed() only works on the dead.
            session.advance()
        child_id = session.succeed()
        self.assertTrue(session.alive)
        self.assertEqual(child_id, session.grid["grid_id"])
        self.assertEqual(parent_id, session.grid["parent_grid_id"])
        self.assertEqual(2, len(session.lineage))
        record = session.lineage[-1]
        self.assertEqual(parent_id, record["parent_grid_id"])
        self.assertEqual(
            session.grid["lineage"], record["lineage"]
        )

    def test_succeed_refused_while_alive(self):
        session = _session()
        with self.assertRaises(ValueError):
            session.succeed()

    def test_lineage_file_round_trips(self):
        session = _session()
        _run_to_death(session)
        session.succeed()
        with tempfile.TemporaryDirectory() as tmp:
            path = session.save_lineage(Path(tmp) / "lineage.json")
            document = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual("keeper_lineage_v1", document["lineage_format"])
        self.assertEqual(session.lineage, document["records"])
        self.assertEqual(2, len(document["records"]))

    def test_sessions_are_deterministic_without_a_player(self):
        first = _session()
        second = _session()
        for _ in range(40):
            if first.alive:
                first.advance()
            if second.alive:
                second.advance()
        self.assertEqual(first.state, second.state)
        self.assertEqual(first.log, second.log)

    def test_history_trim_does_not_change_decisions(self):
        # The D5-measured hotspot: advance_tick deepcopies history.
        # The session trims to HISTORY_WINDOW; PIN that trimming never
        # changes an executed decision vs the untrimmed engine loop.
        session = _session()
        actions: list[str] = []
        for _ in range(60):
            if not session.alive:
                break
            session.advance()
            actions.append(session.log[-1]["action"])
        self.assertLessEqual(
            len(session.state["history"]), HISTORY_WINDOW
        )
        grid, slip_profile, _model = load_session_inputs(
            SEED_PATH, SLIP_PATH
        )
        from mecha_engine.lifecycle import (
            advance_tick,
            choose_action_detailed,
            initial_state,
        )
        import random

        state = initial_state(grid, slip_profile)
        rng = random.Random(0)
        untrimmed: list[str] = []
        for _ in range(len(actions)):
            decision, thought = choose_action_detailed(
                "switchboard", state, rng
            )
            begging = decision == "feed"
            executed = "idle" if begging else decision
            state = advance_tick(state, executed, deliberation=thought)
            untrimmed.append(executed)
        self.assertEqual(untrimmed, actions)

    def test_snapshot_is_the_read_model(self):
        session = _session()
        snapshot = session.snapshot()
        self.assertTrue(snapshot["alive"])
        self.assertIn("hunger", snapshot["needs"])
        self.assertIn("energy", snapshot["needs"])
        self.assertEqual(0, snapshot["age_ticks"])
        self.assertIn("mood", snapshot)
        self.assertFalse(snapshot["begging"])
        self.assertEqual(1, snapshot["generation_count"])


class SessionPacketTests(unittest.TestCase):
    def test_packet_is_engine_truth_with_state_selected_clip(self):
        session = _session()
        packet = session.packet(0)
        self.assertIn("animation", packet)
        self.assertIsInstance(packet["animation"], dict)
        self.assertIn(packet["animation"]["clip"], ["idle", "blink"])
        self.assertIn("scanline", packet["effects"])

    def test_begging_shows_the_beg_display(self):
        session = _session()
        session.state = dict(session.state)
        session.state["hunger"] = 0.9
        session.advance()
        self.assertTrue(session.begging)
        packet = session.packet(0)
        self.assertEqual("beg", packet["animation"]["clip"])


if __name__ == "__main__":
    unittest.main()
