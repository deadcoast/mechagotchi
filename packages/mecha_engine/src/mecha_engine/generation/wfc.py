"""The adopted WFC/constraint generator (cycle 10 B3, DR 0031).

Verbatim semantic port of the research lab ``labs/wfc_grid/wfc_grid.py``
— the bake-off winner (B2: validity 1.0 at 16x16, all 100 silhouettes
unique, the full DR 0015 alphabet emitted; the documented hybrid was
REFUTED by the pre-registered rule). Identical model dictionaries, RNG
streams, error strings, and source labels are pinned by the lab-side
parity test (``labs/wfc_grid/test_package_wfc_parity.py``), so trained
models and generated corpora stay byte-comparable with the research
generator for the same corpus and seeds.

This is an ADDITIVE seam: the constrained stabilizer
(``generate_candidate``/``generate_batch``) is untouched and remains the
parent-based path. DR0038 later made that path vocabulary-complete and
DR0042 made it the evolution default; WFC remains a distinct optional arm. Position-channel overlapping WFC: per-cell observed-token
candidate sets plus observed right/down adjacency, minimum-entropy
collapse with arc-consistent propagation, bounded deterministic
restarts, and the documented stabilizer finishing (largest-core
retention, global cardinality restarts at the DR 0029 floor and sensor
presence, the promoted anchor semantics).
"""

from __future__ import annotations

import random
from collections import deque
from copy import deepcopy

from mecha_engine.genome.validation import body_core_min_cells

from .generate import PALETTES, _weighted_sample

MAX_RESTARTS = 8

# The rich authoring alphabet (DR 0015): token ->
# (role, material, organ_id, palette_index). "A" is a body cell carrying
# the animation anchor flag.
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

TOKEN_FOR_ROLE = {
    role: token
    for token, (role, _material, _organ, _index) in RICH_TOKENS.items()
    if token != "A"
}
TOKEN_FOR_ROLE["anchor"] = "A"

_DIRECTIONS = {
    "right": (1, 0),
    "left": (-1, 0),
    "down": (0, 1),
    "up": (0, -1),
}


def rich_matrix_from_grid(grid: dict) -> list[list[str]]:
    """Project a grid onto the rich token matrix (the full vocabulary)."""
    width, height = grid["grid_size"]
    matrix = [["." for _ in range(width)] for _ in range(height)]
    for cell in grid.get("cells", []):
        x, y = cell.get("x"), cell.get("y")
        if not isinstance(x, int) or not isinstance(y, int):
            continue
        if not (0 <= x < width and 0 <= y < height):
            continue
        if cell.get("animation_anchor") is True:
            matrix[y][x] = "A"
        else:
            matrix[y][x] = TOKEN_FOR_ROLE.get(cell.get("role"), "B")
    return matrix


def train_wfc_model(train_grids: list[dict]) -> dict:
    if not train_grids:
        raise ValueError("train_grids must not be empty")
    sizes = {tuple(grid.get("grid_size", [8, 8])) for grid in train_grids}
    if len(sizes) != 1:
        raise ValueError(
            "training corpus must share a single grid size, found: "
            + ", ".join(f"{w}x{h}" for w, h in sorted(sizes))
        )
    ((width, height),) = sizes

    position_candidates: dict[str, dict[str, int]] = {
        f"{x},{y}": {} for y in range(height) for x in range(width)
    }
    adjacency: dict[str, dict[str, dict[str, int]]] = {"right": {}, "down": {}}
    total_pairs = 0
    for grid in train_grids:
        matrix = rich_matrix_from_grid(grid)
        for y, row in enumerate(matrix):
            for x, token in enumerate(row):
                counts = position_candidates[f"{x},{y}"]
                counts[token] = counts.get(token, 0) + 1
                if x + 1 < width:
                    _count_pair(adjacency["right"], token, row[x + 1])
                    total_pairs += 1
                if y + 1 < height:
                    _count_pair(adjacency["down"], token, matrix[y + 1][x])
                    total_pairs += 1

    return {
        "width": width,
        "height": height,
        "position_candidates": position_candidates,
        "adjacency": adjacency,
        "total_pairs": total_pairs,
        "training_grid_ids": [grid["grid_id"] for grid in train_grids],
    }


def generate_wfc_grid(
    model: dict,
    *,
    grid_id: str,
    rng_seed: int,
    max_restarts: int = MAX_RESTARTS,
    trace: list[dict] | None = None,
) -> dict:
    """Collapse one creature; deterministic per (grid_id, rng_seed).

    Optional trace receives detached JSON observations, including failed
    attempts. It consumes no randomness and never changes returned metadata.
    Errors still raise with their original type/message; prior observations
    remain available. Each call appends a wfc_trace_v1 generation boundary.
    """
    rng = random.Random(f"{rng_seed}:{grid_id}")
    last_error: str | None = None
    attempts_run = 0
    _trace_event(trace, 'generation_started', trace_format='wfc_trace_v1',
                 grid_id=grid_id, rng_seed=rng_seed, max_restarts=max_restarts)
    for attempt in range(max_restarts):
        attempts_run = attempt + 1
        _trace_event(trace, 'attempt_started', attempt=attempt + 1)
        matrix = _collapse(model, rng, trace=trace)
        if matrix is None:
            last_error = "wave contradiction"
            _trace_event(trace, 'attempt_rejected', attempt=attempt + 1, reason=last_error)
            continue
        matrix, finish_error = _finish(matrix, rng, trace=trace)
        if matrix is None:
            last_error = finish_error
            _trace_event(trace, 'attempt_rejected', attempt=attempt + 1, reason=last_error)
            continue
        palette_id = rng.choice(sorted(PALETTES))
        _trace_event(trace, 'palette_selected', palette_id=palette_id)
        grid = _grid_from_rich_matrix(
            grid_id,
            ["".join(row) for row in matrix],
            palette_id,
            size=model["width"],
            source="wfc_grid_lab",
            mutation_events=["wfc_wave_collapsed"],
        )
        _trace_event(trace, 'generated', attempt=attempt + 1, grid_id=grid_id)
        return grid
    _trace_event(trace, 'exhausted', attempts=attempts_run, max_restarts=max_restarts, reason=last_error)
    raise ValueError(
        f"WFC could not collapse {grid_id} (rng_seed {rng_seed}) in "
        f"{max_restarts} attempts: {last_error}"
    )


def build_wfc_corpus(model: dict, *, count: int, rng_seed: int) -> list[dict]:
    return [
        generate_wfc_grid(
            model, grid_id=f"mg_wfc_{index:03d}", rng_seed=rng_seed
        )
        for index in range(count)
    ]


def _count_pair(bucket: dict[str, dict[str, int]], left: str, right: str) -> None:
    counts = bucket.setdefault(left, {})
    counts[right] = counts.get(right, 0) + 1


def _allowed_neighbors(
    model: dict, tokens: list[str], direction: str
) -> set[str]:
    """Tokens legal in ``direction`` next to a cell holding any of ``tokens``."""
    adjacency = model["adjacency"]
    allowed: set[str] = set()
    if direction == "right":
        for token in tokens:
            allowed.update(adjacency["right"].get(token, {}))
    elif direction == "down":
        for token in tokens:
            allowed.update(adjacency["down"].get(token, {}))
    elif direction == "left":
        for left, rights in adjacency["right"].items():
            if any(token in rights for token in tokens):
                allowed.add(left)
    elif direction == "up":
        for upper, lowers in adjacency["down"].items():
            if any(token in lowers for token in tokens):
                allowed.add(upper)
    return allowed


def _trace_event(trace, event, **fields):
    if trace is not None:
        trace.append({'event': event, **deepcopy(fields)})


def _collapse(model: dict, rng: random.Random, *, trace=None) -> list[list[str]] | None:
    width, height = model["width"], model["height"]
    wave: dict[tuple[int, int], dict[str, int]] = {
        (x, y): dict(model["position_candidates"][f"{x},{y}"])
        for y in range(height)
        for x in range(width)
    }

    if trace is not None:
        _trace_event(trace, 'wave_started', width=width, height=height,
                     cells={f'{x},{y}': candidates for (x, y), candidates in wave.items()},
                     training_grid_ids=model.get('training_grid_ids'))

    def propagate(start: tuple[int, int]) -> bool:
        queue: deque[tuple[int, int]] = deque([start])
        while queue:
            x, y = queue.popleft()
            tokens = list(wave[(x, y)])
            for direction, (dx, dy) in _DIRECTIONS.items():
                nx, ny = x + dx, y + dy
                if not (0 <= nx < width and 0 <= ny < height):
                    continue
                allowed = _allowed_neighbors(model, tokens, direction)
                neighbor = wave[(nx, ny)]
                filtered = {
                    token: count
                    for token, count in neighbor.items()
                    if token in allowed
                }
                if len(filtered) != len(neighbor):
                    if not filtered:
                        _trace_event(trace, 'contradiction', source=[x, y], target=[nx, ny],
                                     direction=direction, before=neighbor, remaining=filtered)
                        return False
                    _trace_event(trace, 'propagated', source=[x, y], target=[nx, ny],
                                 direction=direction, before=neighbor, remaining=filtered)
                    wave[(nx, ny)] = filtered
                    queue.append((nx, ny))
        return True

    while True:
        undetermined = [
            (len(candidates), position[1], position[0], position)
            for position, candidates in wave.items()
            if len(candidates) > 1
        ]
        if not undetermined:
            break
        _, _, _, position = min(undetermined)
        token = _weighted_sample(wave[position], rng)
        _trace_event(trace, 'cell_collapsed', position=list(position), choices=wave[position], token=token)
        wave[position] = {token: 1}
        if not propagate(position):
            return None

    matrix = [["." for _ in range(width)] for _ in range(height)]
    for (x, y), candidates in wave.items():
        matrix[y][x] = next(iter(candidates))
    if trace is not None:
        _trace_event(trace, 'collapsed', matrix=[''.join(row) for row in matrix])
    return matrix


def _finish(
    matrix: list[list[str]], rng: random.Random, *, trace=None
) -> tuple[list[list[str]] | None, str]:
    """The documented post-generator stabilizer pass + global constraints.

    Largest 8-connected core component retained (stray core deleted,
    deterministic tie-break by smallest (y, x) member); global
    cardinality restarts: the retained core must clear the ratified
    floor (DR 0029) and at least one eye must exist; anchor normalized
    exactly as the constrained generator does it.
    """
    normalized = [row[:] for row in matrix]
    core: set[tuple[int, int]] = set()
    has_eye = False
    for y, row in enumerate(normalized):
        for x, token in enumerate(row):
            if token == "A":
                normalized[y][x] = "B"
            if normalized[y][x] == "B":
                core.add((x, y))
            if token == "E":
                has_eye = True
    if not core:
        _trace_event(trace, 'finish_rejected', reason='no core cells')
        return None, "no core cells"
    if not has_eye:
        _trace_event(trace, 'finish_rejected', reason='no eye cells')
        return None, "no eye cells"

    largest = _largest_component(core)
    height = len(normalized)
    floor = max(4, 18 * len(normalized[0]) * height // 256)
    if len(largest) < floor:
        _trace_event(trace, 'finish_rejected', reason=f'largest core component below the ratified floor {floor}',
                     retained_core_count=len(largest), floor=floor)
        return None, f"largest core component below the ratified floor {floor}"
    for x, y in core - largest:
        normalized[y][x] = "."

    anchor_x, anchor_y = rng.choice(sorted(largest))
    normalized[anchor_y][anchor_x] = "A"
    if trace is not None:
        _trace_event(trace, 'finished', matrix=[''.join(row) for row in normalized],
                     anchor=[anchor_x, anchor_y], retained_core=[list(point) for point in sorted(largest)],
                     dropped_core=[list(point) for point in sorted(core - largest)], floor=floor,
                     normalized_anchors=[[x, y] for y, row in enumerate(matrix) for x, token in enumerate(row) if token == 'A'])
    return normalized, ""


def _largest_component(points: set[tuple[int, int]]) -> set[tuple[int, int]]:
    remaining = set(points)
    best: set[tuple[int, int]] = set()
    while remaining:
        start = min(remaining, key=lambda point: (point[1], point[0]))
        remaining.discard(start)
        component = {start}
        queue: deque[tuple[int, int]] = deque([start])
        while queue:
            x, y = queue.popleft()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    neighbor = (x + dx, y + dy)
                    if neighbor in remaining:
                        remaining.discard(neighbor)
                        component.add(neighbor)
                        queue.append(neighbor)
        if len(component) > len(best):
            best = component
    return best


def _grid_from_rich_matrix(
    grid_id: str,
    rows: list[str],
    palette_id: str,
    *,
    size: int,
    source: str,
    mutation_events: list[str] | None = None,
) -> dict:
    """Build a grid payload from a rich-token blueprint (lab-verbatim)."""
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
