"""The mechas look: an LCD-handheld theme shared by every command.

One place defines the palette, the console factory, the wordmark banner,
and the small layout helpers, so every workflow renders as part of the
same device instead of inventing its own styling. Palette hexes come from
the project's own `lcd_green` creature palette.
"""

from __future__ import annotations

import sys

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme


LCD_GREEN = "#5dbb63"
LCD_PALE = "#d8ffd6"
LCD_DARK = "#07140d"
AMBER = "#d9a04a"
DANGER = "#d1705a"

THEME = Theme(
    {
        "mechas.title": f"bold {LCD_PALE}",
        "mechas.accent": f"bold {LCD_GREEN}",
        "mechas.dim": "grey62",
        "mechas.ok": f"bold {LCD_GREEN}",
        "mechas.warn": f"bold {AMBER}",
        "mechas.err": f"bold {DANGER}",
        "mechas.path": f"italic {LCD_PALE}",
        "mechas.key": LCD_GREEN,
        "mechas.value": "default",
    }
)

# A tiny resident creature for the banner — half-block pixel art in the
# LCD palette, small enough to stay a signature rather than a gimmick.
_SPRITE_ROWS = (
    (" ▄ ▄ ", LCD_PALE),
    ("▀███▀", LCD_GREEN),
    (" ▀▄▀ ", LCD_GREEN),
)


def console() -> Console:
    # Legacy Windows consoles default to cp1252 and would crash on the
    # sprite's block glyphs. The CLI must never trade a crash for a
    # decoration: force a lossy-but-safe UTF-8 stream instead.
    for stream in (sys.stdout, sys.stderr):
        try:
            encoding = getattr(stream, "encoding", "") or ""
            if "utf" not in encoding.lower():
                stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    return Console(theme=THEME)


def sprite() -> Text:
    art = Text()
    for index, (row, color) in enumerate(_SPRITE_ROWS):
        art.append(row, style=color)
        if index < len(_SPRITE_ROWS) - 1:
            art.append("\n")
    return art


def banner(subtitle: str) -> Panel:
    body = Text()
    for row, color in _SPRITE_ROWS:
        body.append(f"  {row}   ", style=color)
        body.append("\n")
    body.append("  mechas", style="mechas.title")
    body.append("  ·  ", style="mechas.dim")
    body.append(subtitle, style="mechas.dim")
    return Panel(body, border_style=LCD_GREEN, padding=(0, 2), expand=False)


def kv_table(rows: list[tuple[str, str, str]]) -> Table:
    """Two-column status table: (key, value, style-name-for-value)."""
    table = Table(show_header=False, box=None, padding=(0, 1, 0, 0))
    table.add_column(style="mechas.key", justify="right", no_wrap=True)
    # Values fold instead of truncating — a clipped URL is a dead end for
    # the user (audit finding, 2026-07-05).
    table.add_column(overflow="fold")
    for key, value, style in rows:
        table.add_row(key, Text.from_markup(value, style=style))
    return table


def next_steps(steps: list[str]) -> Panel:
    body = Text()
    for index, step in enumerate(steps, start=1):
        body.append(f" {index} ", style="mechas.accent")
        body.append_text(Text.from_markup(step))
        if index < len(steps):
            body.append("\n")
    return Panel(
        body,
        title="next steps",
        title_align="left",
        border_style="grey35",
        padding=(0, 2),
        expand=False,
    )
