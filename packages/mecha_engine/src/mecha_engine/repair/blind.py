"""Blind neighborhood repair — the below-bar benchmark comparator.

BENCHMARK COMPARATOR, NOT THE PRODUCTION REPAIR SURFACE. This is the
blind arm of the repair benchmark: it observes no damage-site information
at all, and its measured quality on the held-out benchmark stays below
the assisted stability bar (final overlap 0.862546, structural agreement
0.631871 vs the >= 0.9 bars;
``meets_assisted_stability_bar = false``). It is kept as the honest
permanent record of observability-free repair quality
(research/package_specs/mecha_engine_repair_interface_spec.md, "Hard
gates for a future package port"). Use ``repair_wound_sites`` — the
site-aware surface — for actual repair.

Verbatim lab semantics, pinned by the lab-side parity test.
"""

from __future__ import annotations

from ._features import (
    LIVE_INDEX_FOR_VOCABULARY,
    model_vocabulary,
    neighborhood_features,
    require_model_scale,
    softmax_probs,
)
from ._grids import grid_from_matrix, matrix_from_grid


def repair_blind(
    damaged_grid: dict,
    model: dict,
    *,
    steps: int = 8,
) -> dict:
    """Iteratively fill empty cells using the trained softmax rule (blind arm).

    Explicitly labelled benchmark comparator: no wound sites, no template —
    the below-bar record of observability-free repair. A cell is filled when
    the model puts more probability mass on live tokens than on empty,
    taking the most likely live token. The update is synchronous and fully
    deterministic; no target grid is consulted.
    """
    weights = model["weights"]
    live_tokens, class_tokens, perception = model_vocabulary(model)
    live_index = LIVE_INDEX_FOR_VOCABULARY[model.get("vocabulary", "legacy")]
    matrix = matrix_from_grid(damaged_grid)
    require_model_scale(model, matrix)
    height = len(matrix)
    width = len(matrix[0]) if height else 0
    for _ in range(steps):
        updated = [row[:] for row in matrix]
        changed = False
        for y in range(height):
            for x in range(width):
                if matrix[y][x] != ".":
                    continue
                probs = softmax_probs(
                    weights,
                    neighborhood_features(
                        matrix, x, y,
                        live_index=live_index, perception=perception,
                    ),
                )
                if probs[0] < 0.5:
                    best = max(range(1, len(class_tokens)), key=lambda c: probs[c])
                    updated[y][x] = class_tokens[best]
                    changed = True
        matrix = updated
        if not changed:
            break

    repaired = grid_from_matrix(
        grid_id=f"{damaged_grid.get('grid_id', 'grid')}_trained_repaired",
        matrix=matrix,
        palette=damaged_grid.get("palette", {}),
        parent_grid_id=damaged_grid.get("grid_id"),
        source="learned_neighborhood_softmax_repair",
        mutation_events=[
            "ca_damage_observed",
            "learned_neighborhood_softmax_repair",
        ],
        generation_delta=1,
    )
    repaired["metadata"]["learned_model_id"] = model.get("model_id")
    repaired["metadata"]["target_template_used"] = False
    repaired["metadata"]["repair_steps"] = steps
    return repaired
