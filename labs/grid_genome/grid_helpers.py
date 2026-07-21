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

# Rich authoring alphabet (DR 0015 vocabulary): token ->
# (role, material, organ_id, palette_index). "A" is a body cell carrying
# the animation anchor flag (so the symmetry metric sees mirrored body
# roles). Shared by the 16x16 pilot exemplars (invariant_scaling) and the
# 16x16 seed corpus (corpus_builder) — one source, per finding L-04.
RICH_TOKENS = {
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
RICH_ORGAN_ROLES = {
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

# DR 0038: the generator paths speak the SAME alphabet as the authoring
# path. One token per ratified role for projection (body's anchor bearer
# projects as "A"); the canonical organ order keeps legacy-only matrices
# reconstructing byte-identically (core, sensors, expression — exactly
# the historical layout — with the new organs slotting in between only
# when their tokens actually appear).
ROLE_TOKENS = {
    role: token
    for token, (role, _material, _organ, _index) in RICH_TOKENS.items()
    if token != "A"
}
ORGAN_ORDER = [
    "core",
    "carapace",
    "sensors",
    "antennae",
    "expression",
    "joints",
    "limbs",
    "trim",
    "aura",
]


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

    DR 0038: the full RICH_TOKENS alphabet reconstructs — every token
    synthesizes its ratified role/material/organ pairing, so the
    generator paths can spell the whole DR 0011 vocabulary.
    ``strict_tokens=True`` raises on tokens outside the ratified
    alphabet (blueprint authoring path); otherwise unknown tokens are
    skipped (generator paths). Legacy-only matrices (B/A/E/M)
    reconstruct byte-identically to the historical shape.
    ``rng_seed`` is recorded in metadata only when provided.
    """
    palette = PALETTES[palette_id]
    cells: list[dict] = []
    organ_cells: dict[str, list[list[int]]] = {}

    for y, row in enumerate(matrix):
        for x, token in enumerate(row):
            if token == ".":
                continue
            if token not in RICH_TOKENS:
                if strict_tokens:
                    raise ValueError(
                        f"{grid_id} has unsupported token {token!r}"
                    )
                continue
            role, material, organ, palette_index = RICH_TOKENS[token]
            cells.append(
                _cell(
                    x,
                    y,
                    visual=palette[palette_index],
                    role=role,
                    material=material,
                    organ=organ,
                    animation_anchor=token == "A",
                )
            )
            organ_cells.setdefault(organ, []).append([x, y])

    organs = {
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
    for organ_id in ORGAN_ORDER:
        if organ_id in organs or organ_id not in organ_cells:
            continue
        organ_role, organ_required = RICH_ORGAN_ROLES[organ_id]
        organs[organ_id] = {
            "role": organ_role,
            "cells": organ_cells[organ_id],
            "required": organ_required,
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


def grid_from_rich_matrix(
    grid_id: str,
    rows: list[str],
    palette_id: str,
    *,
    size: int,
    source: str,
    mutation_events: list[str] | None = None,
) -> dict:
    """Build a grid from a rich-token blueprint (strict authoring path).

    Rejects unknown tokens, wrong dimensions, and any anchor count other
    than exactly one — hand-authored blueprints fail loudly.
    """
    if len(rows) != size or any(len(row) != size for row in rows):
        raise ValueError(f"{grid_id} must be a {size}x{size} blueprint")
    palette = PALETTES[palette_id]
    cells: list[dict] = []
    organ_cells: dict[str, list[list[int]]] = {}
    anchors = 0
    for y, row in enumerate(rows):
        for x, token in enumerate(row):
            if token == ".":
                continue
            if token not in RICH_TOKENS:
                raise ValueError(f"{grid_id} has unsupported token {token!r}")
            role, material, organ, visual_index = RICH_TOKENS[token]
            if token == "A":
                anchors += 1
            cells.append(
                {
                    "x": x,
                    "y": y,
                    "visual": palette[visual_index],
                    "role": role,
                    "material": material,
                    "mutation_weight": 0.1,
                    "animation_anchor": token == "A",
                    "organ": organ,
                    "stress": 0,
                    "damage": 0,
                    "locked": False,
                }
            )
            organ_cells.setdefault(organ, []).append([x, y])
    if anchors != 1:
        raise ValueError(f"{grid_id} must carry exactly one anchor, has {anchors}")
    return {
        "grid_id": grid_id,
        "schema_version": "0.1.0",
        "parent_grid_id": None,
        "grid_size": [size, size],
        "cells": cells,
        "organs": {
            organ: {
                "role": RICH_ORGAN_ROLES[organ][0],
                "cells": organ_cells[organ],
                "required": RICH_ORGAN_ROLES[organ][1],
            }
            for organ in organ_cells
        },
        "palette": {
            "palette_id": palette_id,
            "colors": list(palette),
            "background_index": 0,
        },
        "mutation": {
            "cell_mutation_rate": 0.05,
            "organ_shift_rate": 0.02,
            "palette_shift_rate": 0.01,
            "symmetry_break_rate": 0.01,
        },
        "lineage": {
            "generation": 0,
            "ancestor_ids": [],
            "mutation_events": list(mutation_events or []),
        },
        "metadata": {"source": source},
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
