"""Shared grid-construction helpers for the grid_genome lab.

Single source of truth for helpers that were previously duplicated across
corpus_builder, markov_grid, constrained_generator, random_mutation, and
slip_profile_benchmark (review finding L-04; drift between such copies
previously produced finding H-02).

Deliberate per-module divergences are expressed as parameters here and
pinned by thin wrappers in the owning modules:
- grid_from_matrix: metadata "source" label, optional metadata "rng_seed",
  lineage mutation_events/parent linkage, and strict token checking (only
  the hand-authored blueprint path in corpus_builder rejects unknown
  tokens; generator paths silently skip them).
- run_baseline: constrained_generator's report inserts "unique_signatures"
  between "validity_rate" and "error_counts"; the other generators do not.
"""

import random

from validator import validate_grid


PALETTES = {
    "lcd_green": ["#07140d", "#5dbb63", "#d8ffd6"],
    "gameboy_gray": ["#111814", "#7e8f76", "#d7dfc7"],
    "amber_terminal": ["#1c1005", "#d98428", "#ffe0a3"],
    "crt_blue": ["#06131f", "#3e8fbf", "#d6f3ff"],
    "pocket_plum": ["#160e1f", "#7e5aa6", "#f2dcff"],
}


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


def grid_from_matrix(
    grid_id: str,
    matrix: list[list[str]] | list[str],
    palette_id: str,
    *,
    source: str,
    rng_seed: int | None = None,
    mutation_events: list[str] | None = None,
    parent_grid_id: str | None = None,
    strict_tokens: bool = False,
) -> dict:
    """Build a grid payload from a token matrix (rows of tokens).

    ``strict_tokens=True`` raises on tokens outside {., B, A, E, M}
    (blueprint authoring path); otherwise unknown tokens are skipped
    (generator paths, where sampled tokens come from the seed alphabet).
    ``rng_seed`` is recorded in metadata only when provided.
    """
    palette = PALETTES[palette_id]
    cells: list[dict] = []
    core_cells: list[list[int]] = []
    sensor_cells: list[list[int]] = []
    expression_cells: list[list[int]] = []

    for y, row in enumerate(matrix):
        for x, token in enumerate(row):
            if token == ".":
                continue
            if token in {"B", "A"}:
                cells.append(
                    _cell(
                        x,
                        y,
                        visual=palette[1],
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
                        visual=palette[2],
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
                        visual=palette[2],
                        role="mouth",
                        material="soft",
                        organ="expression",
                    )
                )
                expression_cells.append([x, y])
            elif strict_tokens:
                raise ValueError(f"{grid_id} has unsupported token {token!r}")

    organs = {
        "core": {"role": "body_core", "cells": core_cells, "required": True},
        "sensors": {"role": "sensor", "cells": sensor_cells, "required": True},
    }
    if expression_cells:
        organs["expression"] = {
            "role": "expression",
            "cells": expression_cells,
            "required": False,
        }

    metadata: dict = {"source": source}
    if rng_seed is not None:
        metadata["rng_seed"] = rng_seed

    return {
        "grid_id": grid_id,
        "schema_version": "0.1.0",
        "parent_grid_id": parent_grid_id,
        "grid_size": [len(matrix[0]), len(matrix)],
        "cells": cells,
        "organs": organs,
        "palette": {
            "palette_id": palette_id,
            "colors": palette,
            "background_index": 0,
        },
        "mutation": {
            "cell_mutation_rate": 0.05,
            "organ_shift_rate": 0.02,
            "palette_shift_rate": 0.01,
            "symmetry_break_rate": 0.01,
        },
        "lineage": {
            "generation": 1 if parent_grid_id else 0,
            "ancestor_ids": [parent_grid_id] if parent_grid_id else [],
            "mutation_events": list(mutation_events or []),
        },
        "metadata": metadata,
    }


def run_baseline(generated_grids: list[dict], *, signature=None) -> dict:
    """Validate a generated corpus and report counts.

    ``signature`` (optional callable grid -> hashable) adds a
    "unique_signatures" field between "validity_rate" and "error_counts",
    preserving the constrained_generator report's key order.
    """
    error_counts: dict[str, int] = {}
    valid_count = 0
    for grid in generated_grids:
        result = validate_grid(grid)
        if result.ok:
            valid_count += 1
        for error in result.errors:
            error_counts[error] = error_counts.get(error, 0) + 1

    candidate_count = len(generated_grids)
    invalid_count = candidate_count - valid_count
    report = {
        "candidate_count": candidate_count,
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "validity_rate": valid_count / candidate_count if candidate_count else 0,
    }
    if signature is not None:
        report["unique_signatures"] = len(
            {signature(grid) for grid in generated_grids}
        )
    report["error_counts"] = dict(sorted(error_counts.items()))
    return report


def grid_signature(grid: dict) -> str:
    return "|".join(
        f"{cell['x']},{cell['y']}:{cell['role']}:{int(cell['animation_anchor'])}"
        for cell in sorted(
            grid["cells"], key=lambda item: (item["y"], item["x"], item["role"])
        )
    )


def weighted_sample(counts: dict[str, int], rng: random.Random) -> str:
    total = sum(counts.values())
    pick = rng.randint(1, total)
    cursor = 0
    for token, count in sorted(counts.items()):
        cursor += count
        if pick <= cursor:
            return token
    raise RuntimeError("unreachable sample state")
