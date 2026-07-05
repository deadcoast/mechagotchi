"""Training-time stochastic damage synthesizer for mecha_engine.repair.

Part of the training algorithm (not a public damage surface): the trainer
generates (damaged neighborhood -> target token) examples from seeded
stochastic dropout over the training corpus. Verbatim port of the research
cellular-automata lab's synthesizer (pinned by the lab-side parity test):
identical ``random.Random`` seeding, iteration order, anchor promotion,
grid-id suffix, mutation events, and metadata.

Observability contract (research/package_specs/
mecha_engine_repair_interface_spec.md): the damage event reports which
cells it destroyed — live before, empty after — in
``metadata.removed_cells``. A position healed by the event itself (the
anchor reseed promoting a surviving body cell) is not a removed cell. The
event never carries the destroyed tokens.
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
