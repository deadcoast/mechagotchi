"""F1 gates — the pure compositor (DR 0033 decision 4).

The packet→pixel math is pygame-free stdlib so the compositing spec is
headless-testable and reusable by any future client. Semantics follow
the shared workshop drawer (`workshop/shared/draw.js`, the canonical
consumer): background from the packet's own palette, one filled block
per cell from its `visual`, scanline as a black overlay of the declared
opacity every `period * 2` rows. `lcd_ghosting` is the Phase-C
remainder this client implements FIRST: per-LCD-pixel persistence at
grid resolution, `blended = round(current * (1 - alpha) + previous *
alpha)`. Declared-but-unimplemented effects are REPORTED, never
silently dropped.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for _src in (ROOT / "game" / "src", ROOT / "packages" / "mecha_engine" / "src"):
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))

from mecha_game.rasterize import (  # noqa: E402
    apply_bloom,
    apply_glitch,
    apply_scanline,
    blend_ghosting,
    compose_frame,
    hex_to_rgb,
    rasterize_cells,
    scale_buffer,
)


def _packet(effects=None, parameters=None) -> dict:
    return {
        "grid_id": "test_grid",
        "grid_size": [4, 4],
        "palette": {
            "palette_id": "test",
            "colors": ["#000000", "#ff0000", "#ffffff"],
            "background_index": 0,
        },
        "cells": [
            {"x": 1, "y": 2, "visual": "#ff0000"},
            {"x": 3, "y": 0, "visual": "#ffffff"},
        ],
        "state": None,
        "effects": ["scanline", "lcd_ghosting"] if effects is None else effects,
        "effect_parameters": {
            "scanline": {"period": 2, "opacity": 0.12},
            "lcd_ghosting": {"alpha": 0.35},
        }
        if parameters is None
        else parameters,
    }


class HexToRgbTests(unittest.TestCase):
    def test_parses_hex_colors(self):
        self.assertEqual((0, 0, 0), hex_to_rgb("#000000"))
        self.assertEqual((216, 255, 214), hex_to_rgb("#d8ffd6"))


class RasterizeCellsTests(unittest.TestCase):
    def test_background_everywhere_except_body(self):
        buffer = rasterize_cells(_packet())
        self.assertEqual(4, len(buffer))
        self.assertEqual(4, len(buffer[0]))
        self.assertEqual((255, 0, 0), buffer[2][1])
        self.assertEqual((255, 255, 255), buffer[0][3])
        self.assertEqual((0, 0, 0), buffer[0][0])
        self.assertEqual((0, 0, 0), buffer[3][3])


class GhostingTests(unittest.TestCase):
    def test_first_frame_has_no_ghost(self):
        fb = (((10, 20, 30),),)
        self.assertEqual(fb, blend_ghosting(fb, None, 0.35))

    def test_blend_math_is_the_documented_alpha(self):
        current = (((100, 100, 100),),)
        previous = (((200, 200, 200),),)
        blended = blend_ghosting(current, previous, 0.35)
        self.assertEqual((135, 135, 135), blended[0][0])


class ScaleTests(unittest.TestCase):
    def test_nearest_neighbor_blocks(self):
        fb = (((1, 2, 3), (4, 5, 6)),)
        scaled = scale_buffer(fb, 2)
        self.assertEqual(2, len(scaled))
        self.assertEqual(4, len(scaled[0]))
        self.assertEqual((1, 2, 3), scaled[0][0])
        self.assertEqual((1, 2, 3), scaled[1][1])
        self.assertEqual((4, 5, 6), scaled[0][2])
        self.assertEqual((4, 5, 6), scaled[1][3])


class ScanlineTests(unittest.TestCase):
    def test_darkens_the_documented_rows(self):
        fb = tuple(
            tuple((100, 100, 100) for _ in range(2)) for _ in range(8)
        )
        lined = apply_scanline(fb, period=2, opacity=0.12)
        darkened = (88, 88, 88)  # round(100 * (1 - 0.12))
        for y in range(8):
            expected = darkened if y % 4 < 2 else (100, 100, 100)
            self.assertEqual(expected, lined[y][0], f"row {y}")


class GlitchTests(unittest.TestCase):
    def test_odd_cell_rows_shear_by_the_drawers_math(self):
        # 2x2 cells at cell_px=2 -> 4x4 display; distinct row colors.
        rows = [(10, 0, 0), (20, 0, 0), (30, 0, 0), (40, 0, 0)]
        fb = tuple(tuple(rows[y] for _ in range(4)) for y in range(4))
        # amplitude 1.0, cell_px 2 -> shift = max(1, round(1.0)) = 1.
        sheared = apply_glitch(fb, amplitude=1.0, cell_px=2)
        self.assertEqual(fb[0], sheared[0])  # even cell row untouched
        self.assertEqual(fb[1], sheared[1])
        # Odd cell row (display rows 2-3): shifted right by 1, the
        # uncovered left edge keeps its original pixel.
        self.assertEqual(fb[2][0], sheared[2][0])
        self.assertEqual(fb[2][0], sheared[2][1])
        self.assertEqual(fb[2][2], sheared[2][3])

    def test_amplitude_floor_is_one_pixel(self):
        fb = (((1, 1, 1), (2, 2, 2)), ((3, 3, 3), (4, 4, 4)))
        sheared = apply_glitch(fb, amplitude=0.01, cell_px=1)
        self.assertEqual(fb[0], sheared[0])
        self.assertEqual((3, 3, 3), sheared[1][1])


class BloomTests(unittest.TestCase):
    def test_white_overlay_at_the_drawers_alpha(self):
        fb = (((100, 100, 100),),)
        bloomed = apply_bloom(fb, intensity=0.3)
        # alpha = 0.12 -> round(100 * 0.88 + 255 * 0.12) = 119
        self.assertEqual((119, 119, 119), bloomed[0][0])


class ComposeFrameTests(unittest.TestCase):
    def test_applies_the_declared_lcd_identity(self):
        composed = compose_frame(_packet(), previous_ghost=None, cell_px=2)
        self.assertEqual(["scanline", "lcd_ghosting"], composed.applied)
        self.assertEqual([], composed.skipped)
        self.assertEqual(8, len(composed.pixels))
        self.assertEqual(8, len(composed.pixels[0]))
        self.assertEqual(4, len(composed.ghost))

    def test_ghost_state_carries_between_frames(self):
        first = compose_frame(_packet(), previous_ghost=None, cell_px=1)
        moved = _packet()
        moved["cells"] = [{"x": 0, "y": 0, "visual": "#ffffff"}]
        second = compose_frame(moved, previous_ghost=first.ghost, cell_px=1)
        # The red cell the first frame lit persists as a 35% ghost.
        self.assertEqual((89, 0, 0), second.ghost[2][1])

    def test_unknown_declared_effects_are_reported(self):
        packet = _packet(
            effects=["scanline", "lcd_ghosting", "vhs_wobble"],
        )
        composed = compose_frame(packet, previous_ghost=None, cell_px=1)
        self.assertEqual(["scanline", "lcd_ghosting"], composed.applied)
        self.assertEqual(["vhs_wobble"], composed.skipped)

    def test_state_driven_effects_complete_the_contract(self):
        packet = _packet(
            effects=["scanline", "lcd_ghosting", "crt_bloom", "glitch"],
            parameters={
                "scanline": {"period": 2, "opacity": 0.12},
                "lcd_ghosting": {"alpha": 0.35},
                "crt_bloom": {"radius": 1, "intensity": 0.3},
                "glitch": {"amplitude": 0.9},
            },
        )
        composed = compose_frame(packet, previous_ghost=None, cell_px=2)
        self.assertEqual(
            ["scanline", "lcd_ghosting", "crt_bloom", "glitch"],
            composed.applied,
        )
        self.assertEqual([], composed.skipped)

    def test_composition_is_deterministic(self):
        first = compose_frame(_packet(), previous_ghost=None, cell_px=3)
        second = compose_frame(_packet(), previous_ghost=None, cell_px=3)
        self.assertEqual(first.pixels, second.pixels)
        self.assertEqual(first.ghost, second.ghost)


if __name__ == "__main__":
    unittest.main()
