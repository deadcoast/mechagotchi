"""Fixed feature layout and softmax core for mecha_engine.repair.

Contract sources:

- research/package_specs/mecha_engine_repair_interface_spec.md
  ("RepairModel": per-class weight rows over the fixed feature layout;
  deterministic full-batch training)
- The research cellular-automata growth/repair lab (verbatim port pinned
  by the lab-side parity test): one-hot 5x5 neighborhood live-token
  features, a one-hot cell-position block, and a bias term; zero-initial
  full-batch gradient descent on a convex weighted softmax loss, so the
  training run is exactly reproducible with no RNG.

Semantics, iteration order, and rounding are kept identical to the
research lab so trained weights match bit-for-bit.
"""

from __future__ import annotations

import math

LIVE_TOKENS: list[str] = ["B", "A", "E", "M"]
CLASS_TOKENS: list[str] = [".", "B", "A", "E", "M"]
CLASS_INDEX: dict[str, int] = {
    token: index for index, token in enumerate(CLASS_TOKENS)
}
LIVE_INDEX: dict[str, int] = {
    token: index for index, token in enumerate(LIVE_TOKENS)
}
NEIGHBORHOOD_OFFSETS: list[tuple[int, int]] = [
    (dx, dy)
    for dy in range(-2, 3)
    for dx in range(-2, 3)
    if not (dx == 0 and dy == 0)
]
POSITION_FEATURE_BASE: int = len(NEIGHBORHOOD_OFFSETS) * len(LIVE_TOKENS)
NEIGHBORHOOD_FEATURE_COUNT: int = POSITION_FEATURE_BASE + 64 + 1
BIAS_FEATURE_INDEX: int = NEIGHBORHOOD_FEATURE_COUNT - 1


def neighborhood_features(
    matrix: list[list[str]], x: int, y: int
) -> list[tuple[int, float]]:
    """Sparse one-hot features for the 5x5 neighborhood of a cell."""
    features: list[tuple[int, float]] = []
    for offset_index, (dx, dy) in enumerate(NEIGHBORHOOD_OFFSETS):
        nx = x + dx
        ny = y + dy
        if 0 <= nx < 8 and 0 <= ny < 8:
            token = matrix[ny][nx]
            if token != ".":
                features.append(
                    (offset_index * len(LIVE_TOKENS) + LIVE_INDEX[token], 1.0)
                )
    features.append((POSITION_FEATURE_BASE + y * 8 + x, 1.0))
    features.append((BIAS_FEATURE_INDEX, 1.0))
    return features


def train_softmax(
    examples: list[tuple[list[tuple[int, float]], int, float]],
    *,
    epochs: int,
    learning_rate: float,
) -> tuple[list[list[float]], float, float]:
    """Deterministic full-batch gradient descent from zero-initial weights."""
    class_count = len(CLASS_TOKENS)
    weights = [[0.0] * NEIGHBORHOOD_FEATURE_COUNT for _ in range(class_count)]
    total_weight = sum(weight for _, _, weight in examples)
    initial_loss = final_loss = 0.0
    for epoch in range(epochs):
        gradients = [
            [0.0] * NEIGHBORHOOD_FEATURE_COUNT for _ in range(class_count)
        ]
        loss = 0.0
        for features, label, example_weight in examples:
            probs = softmax_probs(weights, features)
            loss -= example_weight * math.log(max(probs[label], 1e-12))
            for class_index in range(class_count):
                error = example_weight * (
                    probs[class_index] - (1.0 if class_index == label else 0.0)
                )
                if error:
                    gradient = gradients[class_index]
                    for feature_index, value in features:
                        gradient[feature_index] += error * value
        for class_index in range(class_count):
            weight_row = weights[class_index]
            gradient_row = gradients[class_index]
            for feature_index in range(NEIGHBORHOOD_FEATURE_COUNT):
                weight_row[feature_index] -= (
                    learning_rate * gradient_row[feature_index] / total_weight
                )
        if epoch == 0:
            initial_loss = loss / total_weight
        final_loss = loss / total_weight
    return (
        [[round(value, 6) for value in row] for row in weights],
        round(initial_loss, 6),
        round(final_loss, 6),
    )


def softmax_probs(
    weights: list[list[float]], features: list[tuple[int, float]]
) -> list[float]:
    """Numerically stable softmax over per-class sparse dot products."""
    logits = [
        sum(row[index] * value for index, value in features)
        for row in weights
    ]
    peak = max(logits)
    exps = [math.exp(logit - peak) for logit in logits]
    total = sum(exps)
    return [value / total for value in exps]
