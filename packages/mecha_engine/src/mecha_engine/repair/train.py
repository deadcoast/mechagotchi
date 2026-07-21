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
    LIVE_INDEX_FOR_VOCABULARY,
    REPAIR_VOCABULARIES,
    feature_count_for,
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
    vocabulary: str = "legacy",
) -> dict:
    """Train a per-cell softmax repair rule by deterministic gradient descent.

    Training pairs are (damaged 5x5 neighborhood + cell position -> target
    token) examples generated from seeded stochastic damage over the training
    corpus. The model never receives a target template at repair time; it
    learns corpus-level shape statistics through its weights. Full-batch
    gradient descent from zero-initialised weights on a convex softmax loss
    makes the training run exactly reproducible.

    ``vocabulary`` (DR 0041) selects the head's class alphabet:
    ``"legacy"`` is the historical 5-class head with the DR 0039
    perception coarsening, byte-identical (the model dict gains no new
    key); ``"rich"`` trains over the full ratified live alphabet with
    identity perception, recorded in the model as ``vocabulary`` and a
    distinct ``model_id``.
    """
    if not training_grids:
        raise ValueError("training_grids must not be empty")
    if vocabulary not in REPAIR_VOCABULARIES:
        raise ValueError(
            "repair vocabulary must be one of "
            + ", ".join(sorted(REPAIR_VOCABULARIES))
            + f": {vocabulary}"
        )
    live_tokens, class_tokens, perception = REPAIR_VOCABULARIES[vocabulary]
    live_index = LIVE_INDEX_FOR_VOCABULARY[vocabulary]
    class_index = {token: index for index, token in enumerate(class_tokens)}
    # DR 0029 / cycle 09 A3: the feature layout derives from the corpus's
    # own grid size (an 8x8 corpus trains bit-identical historical
    # weights); mixed sizes would silently corrupt the position one-hot,
    # so they fail loudly.
    sizes = {tuple(grid.get("grid_size", [8, 8])) for grid in training_grids}
    if len(sizes) != 1:
        raise ValueError(
            "training corpus must share a single grid size, found: "
            + ", ".join(f"{w}x{h}" for w, h in sorted(sizes))
        )
    ((width, height),) = sizes
    feature_count = feature_count_for(width, height, len(live_tokens))
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
                for y in range(height):
                    for x in range(width):
                        if damaged_matrix[y][x] != ".":
                            continue
                        label = class_index[
                            perception.get(target[y][x], target[y][x])
                        ]
                        weight = live_class_weight if label != 0 else 1.0
                        examples.append(
                            (
                                neighborhood_features(
                                    damaged_matrix,
                                    x,
                                    y,
                                    live_index=live_index,
                                    perception=perception,
                                ),
                                label,
                                weight,
                            )
                        )

    weights, initial_loss, final_loss = train_softmax(
        examples,
        epochs=epochs,
        learning_rate=learning_rate,
        feature_count=feature_count,
        class_count=len(class_tokens),
    )
    model = {
        "model_id": "neighborhood_softmax_repair_model_stage0"
        if vocabulary == "legacy"
        else f"neighborhood_softmax_repair_model_{vocabulary}_stage0",
        "source_mode": "learned_neighborhood_softmax_gradient_descent",
        "training_grid_count": len(training_grids),
        "training_grid_ids": [grid.get("grid_id") for grid in training_grids],
        "width": width,
        "height": height,
        "example_count": len(examples),
        "feature_count": feature_count,
        "class_tokens": list(class_tokens),
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
    # DR 0041 rider pattern: the key is recorded ONLY when non-legacy,
    # so every committed legacy model dict is byte-identical.
    if vocabulary != "legacy":
        model["vocabulary"] = vocabulary
    return model
