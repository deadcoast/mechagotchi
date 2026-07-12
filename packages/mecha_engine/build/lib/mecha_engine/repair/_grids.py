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

TOKENS: frozenset[str] = frozenset({".", "B", "A", "E", "M"})

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
    core_cells: list[list[int]] = []
    sensor_cells: list[list[int]] = []
    expression_cells: list[list[int]] = []
    for y, row in enumerate(matrix):
        for x, token in enumerate(row):
            if token == ".":
                continue
            if token not in TOKENS:
                token = "B"
            if token in {"B", "A"}:
                cells.append(
                    _cell(
                        x,
                        y,
                        visual=colors[1],
                        role="body",
                        material="hard",
                        organ="core",
                        animation_anchor=token == "A",
                    )
                )
                core_cells.append([x, y])
            elif token == "E":
                cells.append(
                    _cell(
                        x,
                        y,
                        visual=colors[min(2, len(colors) - 1)],
                        role="eye",
                        material="glass",
                        organ="sensors",
                    )
                )
                sensor_cells.append([x, y])
            elif token == "M":
                cells.append(
                    _cell(
                        x,
                        y,
                        visual=colors[min(2, len(colors) - 1)],
                        role="mouth",
                        material="soft",
                        organ="expression",
                    )
                )
                expression_cells.append([x, y])
    organs: dict[str, dict] = {
        "core": {"role": "body_core", "cells": core_cells, "required": True},
        "sensors": {"role": "sensor", "cells": sensor_cells, "required": True},
    }
    if expression_cells:
        organs["expression"] = {
            "role": "expression",
            "cells": expression_cells,
            "required": False,
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
