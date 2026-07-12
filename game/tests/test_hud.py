"""F2 gates — the HUD strip is pure, engine-truth pixels.

Bars show the state's OWN numbers (hunger/energy, MVP 0.1's visible
needs); icons mirror the packet's `ui_hints` verbatim (the C5
threshold contract) — the HUD never re-derives a threshold. Pure
stdlib buffers like the compositor, in the packet's own palette.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for _src in (ROOT / "game" / "src", ROOT / "packages" / "mecha_engine" / "src"):
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))

from mecha_game.hud import HUD_HEIGHT, render_hud  # noqa: E402
from mecha_game.rasterize import stack_buffers  # noqa: E402

PALETTE = {
    "palette_id": "test",
    "colors": ["#000000", "#5dbb63", "#d8ffd6"],
    "background_index": 0,
}
BACKGROUND = (0, 0, 0)
BAR = (93, 187, 99)
ICON = (216, 255, 214)


def _hud(state=None, hints=None):
    return render_hud(
        state or {"hunger": 0.5, "energy": 1.0},
        hints
        or {
            "show_hunger_icon": False,
            "show_sleep_icon": False,
            "show_attention_ping": False,
        },
        width=16,
        palette=PALETTE,
    )


class HudTests(unittest.TestCase):
    def test_dimensions(self):
        hud = _hud()
        self.assertEqual(HUD_HEIGHT, len(hud))
        self.assertEqual(16, len(hud[0]))

    def test_bars_are_the_states_own_numbers(self):
        hud = _hud({"hunger": 0.5, "energy": 1.0})
        hunger_filled = sum(1 for px in hud[0] if px == BAR)
        energy_filled = sum(1 for px in hud[2] if px == BAR)
        self.assertEqual(8, hunger_filled)
        self.assertEqual(16, energy_filled)

    def test_bars_clamp_out_of_range_values(self):
        hud = _hud({"hunger": 1.7, "energy": -0.3})
        self.assertEqual(16, sum(1 for px in hud[0] if px == BAR))
        self.assertEqual(0, sum(1 for px in hud[2] if px == BAR))

    def test_icons_mirror_ui_hints_verbatim(self):
        dark = _hud()
        self.assertEqual(0, sum(1 for px in dark[4] if px == ICON))
        lit = _hud(
            hints={
                "show_hunger_icon": True,
                "show_sleep_icon": True,
                "show_attention_ping": True,
            }
        )
        self.assertGreater(sum(1 for px in lit[4] if px == ICON), 0)
        partial = _hud(
            hints={
                "show_hunger_icon": True,
                "show_sleep_icon": False,
                "show_attention_ping": False,
            }
        )
        lit_count = sum(1 for px in lit[4] if px == ICON)
        partial_count = sum(1 for px in partial[4] if px == ICON)
        self.assertLess(partial_count, lit_count)
        self.assertGreater(partial_count, 0)

    def test_deterministic(self):
        self.assertEqual(_hud(), _hud())


class StackTests(unittest.TestCase):
    def test_stack_concatenates_rows(self):
        top = (((1, 1, 1),),)
        bottom = (((2, 2, 2),), ((3, 3, 3),))
        stacked = stack_buffers(top, bottom)
        self.assertEqual(3, len(stacked))
        self.assertEqual((1, 1, 1), stacked[0][0])
        self.assertEqual((3, 3, 3), stacked[2][0])


if __name__ == "__main__":
    unittest.main()
