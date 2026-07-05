"""Private damage-event synthesis and injection for mecha_engine.runtime.

``apply_stochastic_damage`` is the runtime's private seeded damage
synthesizer (research/package_specs/mecha_engine_runtime_interface_spec.md,
"Proposed public surface": ``live_cycle`` "carries its own private seeded
damage synthesizer — the documented per-module factoring"). It is a
verbatim copy of ``mecha_engine.repair._damage.apply_stochastic_damage``
(itself the verbatim port of the research cellular-automata lab's
synthesizer, pinned by the repair lab-side parity test), copied — never
imported across module boundaries — because it is another module's private
file: identical ``random.Random`` seeding, iteration order, anchor
promotion, grid-id suffix, mutation events, and metadata, so the runtime
lab-parity pin reproduces the evolution-loop artifact bit-for-bit.

``apply_damage_event`` is the injected-event adapter (spec: "Injected
damage events (a future gameplay source) replace the synthesizer via an
optional ``damage_events`` parameter without changing cycle semantics"):
it applies an externally supplied event's ``removed_cells`` through the
exact same matrix machinery.

Observability contract (research/package_specs/
mecha_engine_repair_interface_spec.md): the damage event reports which
cells it destroyed — live before, empty after — in
``metadata.removed_cells``. A position healed by the event itself (the
anchor reseed promoting a surviving body cell) is not a removed cell, and
a requested position that was already empty is not a removed cell either.
The event never carries the destroyed tokens.
"""

from __future__ import annotations

import random

from ._grids import ensure_anchor, grid_from_matrix, matrix_from_grid


def apply_stochastic_damage(
    grid: dict,
    *,
    dropout_rate: float = 0.2,
    rng_seed: int = 20260512,
    event_index: int = 1,
) -> dict:
    """Seeded dropout damage that reports the destroyed positions."""
    rng = random.Random(rng_seed)
    before = matrix_from_grid(grid)
    matrix = [row[:] for row in before]
    for y, row in enumerate(before):
        for x, token in enumerate(row):
            if token == ".":
                continue
            if rng.random() < dropout_rate:
                matrix[y][x] = "."
    reseeded = ensure_anchor(matrix)
    # The damage event reports which cells it destroyed (live before, empty
    # after) — the observability the wound-site repair arm relies on.
    removed_cells = [
        [x, y]
        for y in range(len(before))
        for x in range(len(before[y]))
        if before[y][x] != "." and matrix[y][x] == "."
    ]
    removed = len(removed_cells)
    damaged = grid_from_matrix(
        grid_id=f"{grid.get('grid_id', 'grid')}_stochastic_damage_{event_index:02d}",
        matrix=matrix,
        palette=grid.get("palette", {}),
        parent_grid_id=grid.get("grid_id"),
        source="ca_stochastic_damage",
        mutation_events=[
            f"ca_stochastic_damage_{event_index:02d}",
        ]
        + (["anchor_reseeded"] if reseeded else []),
        generation_delta=1,
    )
    damaged["metadata"]["damage_pattern"] = "stochastic_dropout"
    damaged["metadata"]["dropout_rate"] = dropout_rate
    damaged["metadata"]["damage_event_index"] = event_index
    damaged["metadata"]["removed_cell_count"] = removed
    damaged["metadata"]["removed_cells"] = removed_cells
    return damaged


def apply_damage_event(grid: dict, event: dict, *, event_index: int = 1) -> dict:
    """Apply an injected damage event's destroyed positions to a grid.

    The event is a mapping carrying ``removed_cells`` (a list of ``[x, y]``
    positions) — exactly what the observability contract allows: destroyed
    positions, never destroyed tokens, never a template. The positions run
    through the same matrix machinery as the internal synthesizer (cell
    knockout, deterministic anchor promotion, grid reconstruction), so
    downstream repair/episode semantics are unchanged. The reported
    ``metadata.removed_cells`` is recomputed as live-before/empty-after
    (an already-empty requested position is not a removed cell — refilling
    it would grow the creature and break the wound-site contract), so an
    event with empty ``removed_cells`` yields a zero-site no-op repair,
    the measured lab behavior for zero-cell damage events.
    """
    if not isinstance(event, dict) or "removed_cells" not in event:
        raise ValueError("damage event must be a mapping with 'removed_cells'")
    requested = event["removed_cells"]
    if not isinstance(requested, list):
        raise ValueError("damage event removed_cells must be a list of [x, y] positions")
    before = matrix_from_grid(grid)
    matrix = [row[:] for row in before]
    height = len(matrix)
    width = len(matrix[0]) if matrix else 0
    for site in requested:
        if (
            not isinstance(site, list | tuple)
            or len(site) != 2
            or any(isinstance(value, bool) or not isinstance(value, int) for value in site)
        ):
            raise ValueError(f"damage event position must be an [x, y] pair: {site!r}")
        x, y = site
        if not (0 <= x < width and 0 <= y < height):
            raise ValueError(f"damage event position outside the grid: {site!r}")
        matrix[y][x] = "."
    reseeded = ensure_anchor(matrix)
    removed_cells = [
        [x, y]
        for y in range(len(before))
        for x in range(len(before[y]))
        if before[y][x] != "." and matrix[y][x] == "."
    ]
    damaged = grid_from_matrix(
        grid_id=f"{grid.get('grid_id', 'grid')}_injected_damage_{event_index:02d}",
        matrix=matrix,
        palette=grid.get("palette", {}),
        parent_grid_id=grid.get("grid_id"),
        source="injected_damage_event",
        mutation_events=[
            f"injected_damage_event_{event_index:02d}",
        ]
        + (["anchor_reseeded"] if reseeded else []),
        generation_delta=1,
    )
    damaged["metadata"]["damage_pattern"] = "injected_event"
    damaged["metadata"]["damage_event_index"] = event_index
    damaged["metadata"]["removed_cell_count"] = len(removed_cells)
    damaged["metadata"]["removed_cells"] = removed_cells
    return damaged
