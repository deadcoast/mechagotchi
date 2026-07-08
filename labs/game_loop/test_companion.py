"""W1 gates: the companion is engine truth end to end — the engine's own
gate judges adoption, the player's buttons are the action vocabulary,
the switchboard lives the idle moments (thoughts included), death is
honest and refusal-not-noop, and the state persists."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from companion import (  # noqa: E402
    COMPANION_FORMAT,
    adopt_companion,
    autonomous_tick,
    companion_snapshot,
    load_companion,
    player_act,
    save_companion,
)


def _grid() -> dict:
    return json.loads(
        (ROOT / "data" / "seed_grids" / "mg_seed_001.json").read_text(
            encoding="utf-8"
        )
    )


def _profile(deliberation: dict | None = None) -> dict:
    profile = json.loads(
        (ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )
    if deliberation is not None:
        profile["slip_version"] = "0.2.0"
        profile["deliberation"] = deliberation
    return profile


class CompanionTests(unittest.TestCase):
    def _adopt(self, deliberation=None):
        return adopt_companion(
            _grid(),
            _profile(deliberation),
            source={"kind": "seed", "name": "mg_seed_001"},
            name="test_companion",
        )

    # -- adoption is the engine's gate ----------------------------------

    def test_adoption_creates_a_living_engine_state(self):
        companion = self._adopt()
        self.assertEqual(COMPANION_FORMAT, companion["companion_format"])
        self.assertTrue(companion["state"]["alive"])
        self.assertEqual(0, companion["state"]["age_ticks"])

    def test_misaligned_adoption_is_refused_with_engine_errors(self):
        wrong = _profile()
        wrong["grid"]["allowed_palettes"] = ["amber_terminal"]
        with self.assertRaises(ValueError) as caught:
            adopt_companion(
                _grid(), wrong, source={"kind": "seed", "name": "x"}
            )
        self.assertIn("SLIP", str(caught.exception))

    def test_invalid_body_is_refused_by_the_validator(self):
        broken = {"grid_id": "broken", "cells": []}
        with self.assertRaises(ValueError):
            adopt_companion(
                broken, _profile(), source={"kind": "seed", "name": "x"}
            )

    # -- tending: the player's buttons are engine actions ------------------

    def test_player_actions_are_engine_ticks(self):
        companion = self._adopt()
        before = companion["state"]["hunger"]
        state = player_act(companion, "feed")
        self.assertEqual(1, state["age_ticks"])
        self.assertLess(state["hunger"], before)  # feeding feeds
        self.assertEqual("keeper", companion["log"][-1]["actor"])
        self.assertEqual("feed", companion["log"][-1]["action"])

    def test_unknown_actions_are_refused(self):
        companion = self._adopt()
        with self.assertRaises(ValueError):
            player_act(companion, "cuddle")

    def test_the_snapshot_is_packet_v2_over_the_live_state(self):
        companion = self._adopt()
        snapshot = companion_snapshot(companion)
        self.assertTrue(snapshot["alive"])
        self.assertIn(snapshot["animation"], snapshot["animation_vocabulary"])
        self.assertEqual(
            snapshot["packet"]["animation"], snapshot["animation"]
        )
        for need in snapshot["needs"].values():
            self.assertGreaterEqual(need["value"], 0.0)
            self.assertLessEqual(need["value"], 1.0)
        json.dumps(snapshot)

    def test_the_covenant_bounds_the_companions_expressions(self):
        # A species whose grammar has no beg shows idle for a hungry
        # frame while the mood stays honest (E1's gate, live).
        profile = _profile()
        profile["slip_version"] = "0.2.0"
        profile["visual_grammar"] = {"animation_vocab": ["idle", "sleep"]}
        companion = adopt_companion(
            _grid(), profile, source={"kind": "seed", "name": "mg_seed_001"}
        )
        companion["state"]["hunger"] = 0.9  # hungry -> beg would select
        snapshot = companion_snapshot(companion)
        self.assertEqual(["idle", "sleep"], snapshot["animation_vocabulary"])
        self.assertEqual("idle", snapshot["animation"])
        self.assertEqual("hungry", snapshot["mood"])

    # -- living: the switchboard plays the idle moments --------------------

    def test_autonomous_ticks_are_the_switchboards_choices(self):
        companion = self._adopt()
        state, action, thought = autonomous_tick(companion)
        self.assertIn(action, companion_snapshot(companion)["actions"])
        self.assertEqual(1, state["age_ticks"])
        self.assertIsNone(thought)  # no deliberation covenant, no thought
        self.assertEqual("companion", companion["log"][-1]["actor"])

    def test_a_thinking_covenant_thinks_visibly(self):
        companion = self._adopt(
            deliberation={"max_ticks": 4, "confidence_threshold": 0.72}
        )
        thoughts = []
        for _ in range(12):
            if not companion["state"]["alive"]:
                break
            _, _, thought = autonomous_tick(companion)
            if thought is not None:
                thoughts.append(thought)
        self.assertTrue(thoughts)
        for thought in thoughts:
            self.assertGreaterEqual(thought["tick_count"], 1)
            self.assertLessEqual(thought["tick_count"], 4)
        self.assertTrue(
            any("thought" in entry for entry in companion["log"])
        )

    def test_autonomous_ticks_are_deterministic_given_the_state(self):
        first = self._adopt()
        second = self._adopt()
        for _ in range(6):
            autonomous_tick(first)
            autonomous_tick(second)
        self.assertEqual(first["state"], second["state"])
        self.assertEqual(first["log"], second["log"])

    # -- death is honest -----------------------------------------------------

    def test_neglect_kills_and_tending_the_dead_is_refused(self):
        companion = self._adopt()
        # Pure neglect: idle every tick — starvation lands ~tick 11
        # (the measured lifecycle bistability).
        for _ in range(20):
            if not companion["state"]["alive"]:
                break
            player_act(companion, "idle")
        self.assertFalse(companion["state"]["alive"])
        self.assertIsNotNone(companion["state"]["death_cause"])
        with self.assertRaises(ValueError) as caught:
            player_act(companion, "feed")
        self.assertIn(companion["state"]["death_cause"], str(caught.exception))
        with self.assertRaises(ValueError):
            autonomous_tick(companion)
        snapshot = companion_snapshot(companion)
        self.assertFalse(snapshot["alive"])

    # -- persistence ----------------------------------------------------------

    def test_the_companion_persists_and_reloads(self):
        companion = self._adopt()
        player_act(companion, "play")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "companion.json"
            save_companion(companion, path)
            loaded = load_companion(path)
            self.assertEqual(companion, loaded)
            save_companion(companion, path)
            self.assertTrue((Path(tmp) / "companion.bak.json").exists())
        self.assertIsNone(load_companion(Path(tmp) / "companion.json"))


if __name__ == "__main__":
    unittest.main()
