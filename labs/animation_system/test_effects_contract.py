"""C5 pins: the retro effects pipeline and ui_hints, contract-side.

The dossier's packet carries ``"effects": ["scanline", "lcd_ghosting"]``
and ``ui_hints``. The contract is renderer-neutral (DR 0026: consumers
rasterize, the engine never does): names in the documented list shape,
deterministic parameters alongside, everything derived from engine
state — and the lab/package builders stay verbatim twins.
"""

import sys
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
GRID_GENOME = REPO_ROOT / "labs" / "grid_genome"
PACKAGE_SRC = REPO_ROOT / "packages" / "mecha_engine" / "src"
for path in [LAB_DIR, GRID_GENOME, PACKAGE_SRC]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from animation_states import (  # noqa: E402
    build_render_packet_v2 as lab_packet_v2,
)
from corpus_builder import build_seed_grids_16  # noqa: E402

from mecha_engine.genome import render_packet_v2  # noqa: E402


def _beetle() -> dict:
    return next(
        grid
        for grid in build_seed_grids_16()
        if grid["grid_id"].endswith("beetle")
    )


class EffectsContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.beetle = _beetle()

    def test_the_lcd_identity_always_rides_the_packet(self):
        packet = render_packet_v2(self.beetle)
        self.assertEqual(["scanline", "lcd_ghosting"], packet["effects"])
        self.assertIn("scanline", packet["effect_parameters"])
        self.assertIn("lcd_ghosting", packet["effect_parameters"])
        self.assertEqual(
            {
                "show_hunger_icon": False,
                "show_sleep_icon": False,
                "show_attention_ping": False,
            },
            packet["ui_hints"],
        )

    def test_glitch_rides_the_ill_display_with_the_engine_stress(self):
        packet = render_packet_v2(
            self.beetle, {"stress": 0.9, "hunger": 0.2, "energy": 0.8}
        )
        self.assertEqual("ill", packet["animation"])
        self.assertIn("glitch", packet["effects"])
        self.assertEqual(
            0.9, packet["effect_parameters"]["glitch"]["amplitude"]
        )
        self.assertTrue(packet["ui_hints"]["show_attention_ping"])

    def test_bloom_rides_the_beg_display_and_hints_mirror_thresholds(self):
        packet = render_packet_v2(
            self.beetle, {"stress": 0.1, "hunger": 0.9, "energy": 0.8}
        )
        self.assertEqual("beg", packet["animation"])
        self.assertIn("crt_bloom", packet["effects"])
        self.assertTrue(packet["ui_hints"]["show_hunger_icon"])
        self.assertTrue(packet["ui_hints"]["show_attention_ping"])
        sleepy = render_packet_v2(
            self.beetle, {"stress": 0.1, "hunger": 0.2, "energy": 0.1}
        )
        self.assertTrue(sleepy["ui_hints"]["show_sleep_icon"])

    def test_clip_packets_carry_the_same_contract(self):
        packet = render_packet_v2(
            self.beetle,
            {"stress": 0.9, "hunger": 0.2, "energy": 0.8},
            clip="ill",
            frame_index=1,
        )
        self.assertIn("glitch", packet["effects"])
        self.assertIn("ui_hints", packet)

    def test_lab_and_package_builders_stay_verbatim_twins(self):
        for state in [
            None,
            {"stress": 0.9, "hunger": 0.2, "energy": 0.8},
            {"stress": 0.1, "hunger": 0.9, "energy": 0.8},
            {"stress": 0.1, "hunger": 0.2, "energy": 0.1},
        ]:
            with self.subTest(state=state):
                self.assertEqual(
                    lab_packet_v2(self.beetle, state),
                    render_packet_v2(self.beetle, state),
                )


if __name__ == "__main__":
    unittest.main()
