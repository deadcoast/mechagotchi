"""Token-matrix <-> grid-genome conversion for mecha_engine.repair.

Verbatim port of the research cellular-automata lab's grid helpers (pinned
by the lab-side parity test): the token alphabet, the matrix projection,
the grid reconstruction (cell fields, organ membership, palette handling,
mutation-rate defaults, lineage), and the deterministic anchor-promotion
rule used by damage synthesis. Reconstruction keys, iteration order, and
tie-breaks are load-bearing — repaired grids must match the research lab
bit-for-bit.
"""

from __future__ import annotations

# DR 0039: repair preserves what it cannot yet spell — projection and
# reconstruction speak the FULL ratified alphabet (verbatim mirror of
# the research CA lab; drift caught by the lab-side parity test).
TOKENS: frozenset[str] = frozenset(
    {".", "B", "A", "S", "J", "L", "E", "M", "N", "P", "D", "F"}
)
RICH_TOKENS: dict[str, tuple[str, str, str, int]] = {
    "B": ("body", "hard", "core", 1),
    "A": ("body", "hard", "core", 1),
    "S": ("shell", "hard", "carapace", 1),
    "J": ("joint", "joint", "joints", 1),
    "L": ("limb", "hard", "limbs", 1),
    "E": ("eye", "glass", "sensors", 2),
    "M": ("mouth", "soft", "expression", 2),
    "N": ("antenna", "signal", "antennae", 2),
    "P": ("sensor", "signal", "antennae", 2),
    "D": ("decoration", "light", "trim", 2),
    "F": ("effect", "signal", "aura", 2),
}
RICH_ORGAN_ROLES: dict[str, tuple[str, bool]] = {
    "core": ("body_core", True),
    "carapace": ("body_core", False),
    "sensors": ("sensor", True),
    "antennae": ("sensor", False),
    "expression": ("expression", False),
    "joints": ("locomotion", False),
    "limbs": ("locomotion", False),
    "trim": ("ornament", False),
    "aura": ("effect", False),
}
_RICH_ROLE_TOKENS: dict[str, str] = {
    "shell": "S",
    "joint": "J",
    "limb": "L",
    "antenna": "N",
    "sensor": "P",
    "decoration": "D",
    "effect": "F",
}
_ORGAN_ORDER: tuple[str, ...] = (
    "core",
    "carapace",
    "sensors",
    "antennae",
    "expression",
    "joints",
    "limbs",
    "trim",
    "aura",
)

# Stage 0 palette fallback table — verbatim copy of the research corpus
# builder's palette table (the grid_genome research lab's ``PALETTES``,
# mirrored by the SLIP palette enum in research/slip/slip.schema.json and
# by ``mecha_engine.generation``'s private copy). Embedded privately here
# because ``mecha_engine.generation`` exposes no public palette helper.
PALETTES: dict[str, list[str]] = {
    "lcd_green": ["#07140d", "#5dbb63", "#d8ffd6"],
    "gameboy_gray": ["#111814", "#7e8f76", "#d7dfc7"],
    "amber_terminal": ["#1c1005", "#d98428", "#ffe0a3"],
    "crt_blue": ["#06131f", "#3e8fbf", "#d6f3ff"],
    "pocket_plum": ["#160e1f", "#7e5aa6", "#f2dcff"],
}


def matrix_from_grid(grid: dict) -> list[list[str]]:
    """Project a grid genome onto its token matrix (out-of-range cells skipped)."""
    width, height = grid.get("grid_size", [8, 8])
    matrix = [["." for _ in range(width)] for _ in range(height)]
    for cell in grid.get("cells", []):
        x = cell.get("x")
        y = cell.get("y")
        if not isinstance(x, int) or not isinstance(y, int):
            continue
        if x < 0 or y < 0 or y >= height or x >= width:
            continue
        matrix[y][x] = _token_for_cell(cell)
    return matrix


def grid_from_matrix(
    *,
    grid_id: str,
    matrix: list[list[str]],
    palette: dict,
    parent_grid_id: str | None,
    source: str,
    mutation_events: list[str],
    generation_delta: int,
) -> dict:
    """Rebuild a full grid genome dictionary from a token matrix."""
    palette_id = palette.get("palette_id", "lcd_green")
    colors = palette.get("colors") or PALETTES.get(palette_id, PALETTES["lcd_green"])
    cells: list[dict] = []
    organ_cells: dict[str, list[list[int]]] = {}
    # DR 0039: the full RICH_TOKENS alphabet reconstructs — surviving
    # rich cells keep their ratified pairings; truly-unknown tokens
    # keep the defensive "B" coercion.
    for y, row in enumerate(matrix):
        for x, token in enumerate(row):
            if token == ".":
                continue
            if token not in RICH_TOKENS:
                token = "B"
            role, material, organ, palette_index = RICH_TOKENS[token]
            cells.append(
                _cell(
                    x,
                    y,
                    visual=colors[min(palette_index, len(colors) - 1)],
                    role=role,
                    material=material,
                    organ=organ,
                    animation_anchor=token == "A",
                )
            )
            organ_cells.setdefault(organ, []).append([x, y])
    organs: dict[str, dict] = {
        "core": {
            "role": "body_core",
            "cells": organ_cells.get("core", []),
            "required": True,
        },
        "sensors": {
            "role": "sensor",
            "cells": organ_cells.get("sensors", []),
            "required": True,
        },
    }
    for organ_id in _ORGAN_ORDER:
        if organ_id in organs or organ_id not in organ_cells:
            continue
        organ_role, organ_required = RICH_ORGAN_ROLES[organ_id]
        organs[organ_id] = {
            "role": organ_role,
            "cells": organ_cells[organ_id],
            "required": organ_required,
        }
    return {
        "grid_id": grid_id,
        "schema_version": "0.1.0",
        "parent_grid_id": parent_grid_id,
        "grid_size": [len(matrix[0]), len(matrix)] if matrix else [0, 0],
        "cells": cells,
        "organs": organs,
        "palette": {
            "palette_id": palette_id,
            "colors": colors,
            "background_index": palette.get("background_index", 0),
        },
        "mutation": {
            "cell_mutation_rate": 0.05,
            "organ_shift_rate": 0.02,
            "palette_shift_rate": 0.01,
            "symmetry_break_rate": 0.01,
        },
        "lineage": {
            "generation": generation_delta,
            "ancestor_ids": [parent_grid_id] if parent_grid_id else [],
            "mutation_events": mutation_events,
        },
        "metadata": {"source": source},
    }


def ensure_anchor(matrix: list[list[str]]) -> bool:
    """Promote the most central body cell to the anchor if none survived."""
    if any("A" in row for row in matrix):
        return False
    body_points = [
        (x, y)
        for y, row in enumerate(matrix)
        for x, token in enumerate(row)
        if token == "B"
    ]
    if not body_points:
        return False
    x, y = sorted(
        body_points, key=lambda point: abs(point[0] - 3.5) + abs(point[1] - 3.5)
    )[0]
    matrix[y][x] = "A"
    return True


def _token_for_cell(cell: dict) -> str:
    if cell.get("organ") == "core":
        return "A" if cell.get("animation_anchor") is True else "B"
    if cell.get("organ") == "sensors" or cell.get("role") == "eye":
        return "E"
    if cell.get("organ") == "expression" or cell.get("role") == "mouth":
        return "M"
    # DR 0039: rich roles project to their own tokens (the standalone
    # anchor role normalizes to "A"); unknown cells keep the defensive
    # legacy fallback.
    rich = _RICH_ROLE_TOKENS.get(cell.get("role"))
    if rich is not None:
        return rich
    if cell.get("role") == "anchor":
        return "A"
    return "B"


def _cell(
    x: int,
    y: int,
    *,
    visual: str,
    role: str,
    material: str,
    organ: str,
    animation_anchor: bool = False,
) -> dict:
    return {
        "x": x,
        "y": y,
        "visual": visual,
        "role": role,
        "material": material,
        "mutation_weight": 0.1,
        "animation_anchor": animation_anchor,
        "organ": organ,
        "stress": 0,
        "damage": 0,
        "locked": False,
    }
