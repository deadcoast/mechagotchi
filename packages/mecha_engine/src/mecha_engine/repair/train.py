"""Deterministic repair-model training for mecha_engine.repair.

Contract sources:

- research/package_specs/mecha_engine_repair_interface_spec.md
  ("RepairModel", "Required public surface": deterministic full-batch
  training; identical inputs give identical weights;
  ``target_template_used: false`` is a hard invariant)
- research/decision_records/0006-create-mecha-engine-repair-target.md
  (verbatim lab semantics, pinned by the lab-side parity test)
"""

from __future__ import annotations

from ._damage import apply_stochastic_damage
from ._features import (
    CLASS_INDEX,
    CLASS_TOKENS,
    NEIGHBORHOOD_FEATURE_COUNT,
    neighborhood_features,
    train_softmax,
)
from ._grids import matrix_from_grid


def train_repair_model(
    training_grids: list[dict],
    *,
    dropout_rates: tuple[float, ...] = (0.1, 0.2, 0.3, 0.4),
    damage_instances: int = 1,
    epochs: int = 150,
    learning_rate: float = 1.5,
    live_class_weight: float = 3.0,
    rng_seed: int = 20260512,
) -> dict:
    """Train a per-cell softmax repair rule by deterministic gradient descent.

    Training pairs are (damaged 5x5 neighborhood + cell position -> target
    token) examples generated from seeded stochastic damage over the training
    corpus. The model never receives a target template at repair time; it
    learns corpus-level shape statistics through its weights. Full-batch
    gradient descent from zero-initialised weights on a convex softmax loss
    makes the training run exactly reproducible.
    """
    if not training_grids:
        raise ValueError("training_grids must not be empty")
    examples: list[tuple[list[tuple[int, float]], int, float]] = []
    for grid_index, grid in enumerate(training_grids):
        target = matrix_from_grid(grid)
        for rate_index, rate in enumerate(dropout_rates):
            for instance in range(damage_instances):
                seed = rng_seed + grid_index * 1000 + rate_index * 100 + instance
                damaged = apply_stochastic_damage(
                    grid,
                    dropout_rate=rate,
                    rng_seed=seed,
                    event_index=1,
                )
                damaged_matrix = matrix_from_grid(damaged)
                for y in range(8):
                    for x in range(8):
                        if damaged_matrix[y][x] != ".":
                            continue
                        label = CLASS_INDEX[target[y][x]]
                        weight = live_class_weight if label != 0 else 1.0
                        examples.append(
                            (
                                neighborhood_features(damaged_matrix, x, y),
                                label,
                                weight,
                            )
                        )

    weights, initial_loss, final_loss = train_softmax(
        examples,
        epochs=epochs,
        learning_rate=learning_rate,
    )
    return {
        "model_id": "neighborhood_softmax_repair_model_stage0",
        "source_mode": "learned_neighborhood_softmax_gradient_descent",
        "training_grid_count": len(training_grids),
        "training_grid_ids": [grid.get("grid_id") for grid in training_grids],
        "example_count": len(examples),
        "feature_count": NEIGHBORHOOD_FEATURE_COUNT,
        "class_tokens": list(CLASS_TOKENS),
        "dropout_rates": list(dropout_rates),
        "damage_instances": damage_instances,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "live_class_weight": live_class_weight,
        "rng_seed": rng_seed,
        "initial_loss": initial_loss,
        "final_loss": final_loss,
        "target_template_used": False,
        "weights": weights,
        "limitations": [
            "The model is a linear softmax over one-hot neighborhood and position features, not a neural cellular automaton with hidden state.",
            "It only fills empty cells; it cannot relocate or delete misplaced cells.",
            "It learns one species-level shape prior across the corpus and cannot distinguish individual grid variants.",
        ],
    }
