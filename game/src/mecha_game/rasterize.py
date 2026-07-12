"""The pure compositor — packet to pixels, pygame-free (DR 0033 dec. 4).

The compositing spec any Mechagotchi client must reproduce, kept as
deterministic stdlib math so it is headless-testable and reusable by a
future Godot/web client. Semantics follow the shared workshop drawer
(`workshop/shared/draw.js`, the canonical packet consumer):

- body raster: background from the packet's own palette
  (``colors[background_index]``), one filled block per cell from its
  ``visual`` — the engine's projected color, never a client guess;
- ``scanline``: a black overlay of the declared ``opacity`` on rows
  ``y % (period * 2) < period`` (the drawer's fill, as arithmetic:
  ``round(channel * (1 - opacity))``);
- ``lcd_ghosting``: the Phase-C remainder this client implements FIRST
  (the static drawer honestly skips it). Physical reading: the LCD's
  pixels ARE the grid cells, so persistence blends at GRID resolution
  before scaling — ``round(current * (1 - alpha) + previous * alpha)``
  per channel, with the pre-scanline raster as the carried state.

The state-driven pair completes the documented contract (F3):
``glitch`` is the ill display's odd-row shear with amplitude equal to
the engine's own stress number, ``crt_bloom`` the beg display's white
halo — both the shared drawer's exact math. An effect a packet
declares that this compositor does not know is still REPORTED in
``skipped``, never silently dropped.
"""

from __future__ import annotations

from dataclasses import dataclass

Rgb = tuple[int, int, int]
Buffer = tuple[tuple[Rgb, ...], ...]

# The full documented effects contract (F3): the LCD identity plus the
# state-driven pair (crt_bloom rides beg, glitch rides ill).
IMPLEMENTED_EFFECTS = ("scanline", "lcd_ghosting", "crt_bloom", "glitch")


@dataclass(frozen=True)
class ComposedFrame:
    """One presented frame: display pixels, the grid-resolution ghost
    state carried to the next frame, and the honest effect ledger."""

    pixels: Buffer
    ghost: Buffer
    applied: list[str]
    skipped: list[str]


def hex_to_rgb(value: str) -> Rgb:
    digits = value.lstrip("#")
    return (
        int(digits[0:2], 16),
        int(digits[2:4], 16),
        int(digits[4:6], 16),
    )


def rasterize_cells(packet: dict) -> Buffer:
    """The body raster at grid resolution: palette background, one
    block per cell from the engine's ``visual``."""
    width, height = packet["grid_size"]
    palette = packet["palette"]
    background = hex_to_rgb(palette["colors"][palette["background_index"]])
    rows = [[background] * width for _ in range(height)]
    for cell in packet["cells"]:
        rows[cell["y"]][cell["x"]] = hex_to_rgb(cell["visual"])
    return tuple(tuple(row) for row in rows)


def blend_ghosting(
    current: Buffer, previous: Buffer | None, alpha: float
) -> Buffer:
    """LCD persistence: the previous panel state bleeds through at the
    packet's declared ``alpha``; the first frame has nothing to ghost."""
    if previous is None:
        return current
    keep = 1 - alpha
    return tuple(
        tuple(
            (
                round(cur[0] * keep + prev[0] * alpha),
                round(cur[1] * keep + prev[1] * alpha),
                round(cur[2] * keep + prev[2] * alpha),
            )
            for cur, prev in zip(cur_row, prev_row)
        )
        for cur_row, prev_row in zip(current, previous)
    )


def scale_buffer(fb: Buffer, cell_px: int) -> Buffer:
    """Nearest-neighbor upscale: one LCD cell becomes a
    ``cell_px``-square block — crisp retro pixels, no interpolation."""
    return tuple(
        tuple(pixel for pixel in row for _ in range(cell_px))
        for row in fb
        for _ in range(cell_px)
    )


def apply_glitch(fb: Buffer, *, amplitude: float, cell_px: int) -> Buffer:
    """The ill display's row shear, the shared drawer's exact math:
    odd LCD-cell rows shift right by ``max(1, round(amplitude *
    cell_px * 0.5))`` display pixels — amplitude IS the engine's own
    stress number (C5). The uncovered left edge keeps its original
    pixels (the drawer's putImageData semantics)."""
    shift = max(1, round(amplitude * cell_px * 0.5))
    return tuple(
        tuple(
            row[x - shift] if x >= shift else row[x]
            for x in range(len(row))
        )
        if (y // cell_px) % 2 == 1
        else row
        for y, row in enumerate(fb)
    )


def apply_bloom(fb: Buffer, *, intensity: float) -> Buffer:
    """The beg display's halo, the shared drawer's exact math: a white
    overlay at ``intensity * 0.4`` alpha over the whole frame."""
    alpha = intensity * 0.4
    keep = 1 - alpha
    return tuple(
        tuple(
            (
                round(r * keep + 255 * alpha),
                round(g * keep + 255 * alpha),
                round(b * keep + 255 * alpha),
            )
            for r, g, b in row
        )
        for row in fb
    )


def apply_scanline(fb: Buffer, *, period: int, opacity: float) -> Buffer:
    keep = 1 - opacity
    return tuple(
        tuple(
            (round(r * keep), round(g * keep), round(b * keep))
            for r, g, b in row
        )
        if y % (period * 2) < period
        else row
        for y, row in enumerate(fb)
    )


def stack_buffers(top: Buffer, bottom: Buffer) -> Buffer:
    """Concatenate two buffers vertically (panel above HUD)."""
    return tuple(top) + tuple(bottom)


def compose_frame(
    packet: dict, *, previous_ghost: Buffer | None, cell_px: int
) -> ComposedFrame:
    """Compose one display frame from a render packet.

    Order is physical, not declaration order: ghosting is the panel's
    own persistence (grid resolution, before scaling); after scaling
    come the display artifacts in the shared drawer's order — glitch,
    bloom, then the scanline overlay. ``applied``/``skipped``
    partition the packet's declared effects against
    ``IMPLEMENTED_EFFECTS`` in declaration order.
    """
    declared = list(packet.get("effects") or [])
    parameters = packet.get("effect_parameters") or {}
    applied = [name for name in declared if name in IMPLEMENTED_EFFECTS]
    skipped = [name for name in declared if name not in IMPLEMENTED_EFFECTS]

    ghost = rasterize_cells(packet)
    if "lcd_ghosting" in applied:
        alpha = (parameters.get("lcd_ghosting") or {}).get("alpha", 0.35)
        ghost = blend_ghosting(ghost, previous_ghost, alpha)

    pixels = scale_buffer(ghost, cell_px)
    if "glitch" in applied:
        glitch = parameters.get("glitch") or {}
        pixels = apply_glitch(
            pixels,
            amplitude=glitch.get("amplitude", 0.5),
            cell_px=cell_px,
        )
    if "crt_bloom" in applied:
        bloom = parameters.get("crt_bloom") or {}
        pixels = apply_bloom(
            pixels, intensity=bloom.get("intensity", 0.3)
        )
    if "scanline" in applied:
        scanline = parameters.get("scanline") or {}
        pixels = apply_scanline(
            pixels,
            period=scanline.get("period", 2),
            opacity=scanline.get("opacity", 0.12),
        )
    return ComposedFrame(
        pixels=pixels, ghost=ghost, applied=applied, skipped=skipped
    )
