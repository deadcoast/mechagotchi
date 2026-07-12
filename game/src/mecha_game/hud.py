"""The HUD strip — engine-truth pixels below the LCD panel (F2).

Pure stdlib buffers in the packet's own palette, like the compositor.
Bars show the state's OWN numbers (hunger and energy — MVP 0.1's
named visible needs, alongside the app layer's mood/age text); icons
mirror the packet's `ui_hints` verbatim (the C5 threshold contract) —
the HUD never re-derives a threshold or invents a number.
"""

from __future__ import annotations

from .rasterize import Buffer, Rgb, hex_to_rgb

HUD_HEIGHT = 6
# Icon cell columns on the icon row (row 4), two cells each.
ICON_CELLS = {
    "show_hunger_icon": (0, 1),
    "show_sleep_icon": (3, 4),
    "show_attention_ping": (6, 7),
}


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _bar_row(
    filled: int, width: int, bar: Rgb, background: Rgb
) -> tuple[Rgb, ...]:
    return tuple(bar if x < filled else background for x in range(width))


PING_PERIOD = 4  # render frames per attention-ping phase


def render_hud(
    state: dict,
    ui_hints: dict,
    *,
    width: int,
    palette: dict,
    frame: int = 0,
) -> Buffer:
    """The strip: hunger bar (rows 0-1), energy bar (rows 2-3), the
    ui_hints icon row (row 4), a separator (row 5). The attention ping
    PINGS — lit on alternating ``PING_PERIOD``-frame phases (a
    deterministic function of the render frame, C5's hint consumed as
    the contract names it)."""
    colors = palette["colors"]
    background = hex_to_rgb(colors[palette["background_index"]])
    bar = hex_to_rgb(colors[1 % len(colors)])
    icon = hex_to_rgb(colors[2 % len(colors)])

    hunger_filled = round(_clamp(state.get("hunger", 0.0)) * width)
    energy_filled = round(_clamp(state.get("energy", 0.0)) * width)
    hunger_row = _bar_row(hunger_filled, width, bar, background)
    energy_row = _bar_row(energy_filled, width, bar, background)

    ping_phase = (frame // PING_PERIOD) % 2 == 0
    icon_row = [background] * width
    for hint, cells in ICON_CELLS.items():
        lit = ui_hints.get(hint) and (
            hint != "show_attention_ping" or ping_phase
        )
        if lit:
            for x in cells:
                if x < width:
                    icon_row[x] = icon

    return (
        hunger_row,
        hunger_row,
        energy_row,
        energy_row,
        tuple(icon_row),
        tuple([background] * width),
    )
