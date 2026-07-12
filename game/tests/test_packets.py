"""F1 gates — the hello creature is engine truth end to end.

The client's packet source may only relay the engine: adoption is
`lifecycle.initial_state` (the engine's own gate, refusing with its own
errors), and every frame is `genome.render_packet_v2` driving the idle
clip. Nothing here invents a number (DR 0021 first law; DR 0033).
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for _src in (ROOT / "game" / "src", ROOT / "packages" / "mecha_engine" / "src"):
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))

from mecha_game.packets import (  # noqa: E402
    HelloCreature,
    default_fixture_paths,
    hello_packet,
    load_hello_creature,
)

SEED_PATH = ROOT / "data" / "seed_grids_16x16" / "mg_seed16_001_beetle.json"
SLIP_PATH = ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"


class HelloCreatureTests(unittest.TestCase):
    def _creature(self) -> HelloCreature:
        return load_hello_creature(SEED_PATH, SLIP_PATH)

    def test_adoption_is_the_engines_gate(self):
        creature = self._creature()
        self.assertTrue(creature.lifecycle_state["alive"])
        self.assertEqual(0, creature.lifecycle_state["age_ticks"])
        self.assertEqual("idle", creature.clip)
        self.assertEqual(4, creature.frame_count)
        self.assertEqual([16, 16], creature.grid["grid_size"])

    def test_misaligned_covenant_is_refused_with_engine_errors(self):
        profile = json.loads(SLIP_PATH.read_text(encoding="utf-8"))
        profile["grid"]["allowed_palettes"] = ["amber_terminal"]
        with self.assertRaises(ValueError):
            load_hello_creature(SEED_PATH, slip_profile=profile)

    def test_hello_packet_drives_the_idle_clip(self):
        creature = self._creature()
        packet = hello_packet(creature, 0)
        self.assertEqual("idle", packet["animation"]["clip"])
        self.assertEqual(0, packet["animation"]["frame_index"])
        self.assertEqual(4, packet["animation"]["frame_count"])
        self.assertIn("scanline", packet["effects"])
        self.assertIn("lcd_ghosting", packet["effects"])
        self.assertIn("ui_hints", packet)
        self.assertTrue(packet["state"]["alive"])

    def test_frame_index_cycles_the_clip(self):
        creature = self._creature()
        indices = [
            hello_packet(creature, tick)["animation"]["frame_index"]
            for tick in range(8)
        ]
        self.assertEqual([0, 1, 2, 3, 0, 1, 2, 3], indices)

    def test_packets_are_deterministic_and_json_serializable(self):
        creature = self._creature()
        first = hello_packet(creature, 3)
        second = hello_packet(creature, 3)
        self.assertEqual(first, second)
        self.assertEqual(first, json.loads(json.dumps(first)))

    def test_default_fixtures_resolve_from_the_repo(self):
        seed, slip = default_fixture_paths(start=ROOT / "game")
        self.assertTrue(seed.is_file())
        self.assertTrue(slip.is_file())
        creature = load_hello_creature(seed, slip)
        self.assertTrue(creature.lifecycle_state["alive"])


if __name__ == "__main__":
    unittest.main()
