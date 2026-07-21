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
# DR 0039: perception coarsening by palette family (verbatim mirror of
# the research CA lab) — the LEGACY 5-class head PERCEIVES rich tokens
# as their legacy family; projection/reconstruction preserve them
# verbatim.
PERCEPTION_LIVE: dict[str, str] = {
    "S": "B",
    "J": "B",
    "L": "B",
    "N": "E",
    "P": "E",
    "D": "E",
    "F": "E",
}
# DR 0041: the 11-class regrowth head (verbatim mirror of the research
# CA lab). The head's class vocabulary is a model-level property chosen
# at training time: "legacy" is the historical 5-class head with the
# DR 0039 coarsening, byte-identical; "rich" is the full ratified live
# alphabet in declaration order (a 12-way softmax with empty) with
# IDENTITY perception.
RICH_LIVE_TOKENS: list[str] = [
    "B", "A", "S", "J", "L", "E", "M", "N", "P", "D", "F",
]
RICH_CLASS_TOKENS: list[str] = ["."] + RICH_LIVE_TOKENS
RICH_LIVE_INDEX: dict[str, int] = {
    token: index for index, token in enumerate(RICH_LIVE_TOKENS)
}
REPAIR_VOCABULARIES: dict[str, tuple[list[str], list[str], dict[str, str]]] = {
    "legacy": (LIVE_TOKENS, CLASS_TOKENS, PERCEPTION_LIVE),
    "rich": (RICH_LIVE_TOKENS, RICH_CLASS_TOKENS, {}),
}
LIVE_INDEX_FOR_VOCABULARY: dict[str, dict[str, int]] = {
    "legacy": LIVE_INDEX,
    "rich": RICH_LIVE_INDEX,
}
NEIGHBORHOOD_OFFSETS: list[tuple[int, int]] = [
    (dx, dy)
    for dy in range(-2, 3)
    for dx in range(-2, 3)
    if not (dx == 0 and dy == 0)
]
POSITION_FEATURE_BASE: int = len(NEIGHBORHOOD_OFFSETS) * len(LIVE_TOKENS)
# The historical 8x8 layout constants. The layout is size-parametric since
# cycle 09 A3 (DR 0029): feature_count_for(w, h) generalizes the count and
# reproduces these values exactly at 8x8, so 8x8 weights stay bit-for-bit.
NEIGHBORHOOD_FEATURE_COUNT: int = POSITION_FEATURE_BASE + 64 + 1
BIAS_FEATURE_INDEX: int = NEIGHBORHOOD_FEATURE_COUNT - 1


def feature_count_for(
    width: int, height: int, live_token_count: int = len(LIVE_TOKENS)
) -> int:
    """Feature-vector width for a grid scale (position one-hot + bias).

    DR 0041: the layout derives from the live-token count exactly as it
    derives from grid scale (DR 0029); at the legacy count every value
    reproduces the historical layout bit-for-bit.
    """
    return (
        len(NEIGHBORHOOD_OFFSETS) * live_token_count + width * height + 1
    )


def model_vocabulary(model: dict) -> tuple[list[str], list[str], dict[str, str]]:
    """(live_tokens, class_tokens, perception) for a trained model.

    Pre-DR-0041 models carry no ``vocabulary`` key and are legacy (the
    ``require_model_scale`` compat precedent). A model whose recorded
    ``class_tokens`` contradict its vocabulary is refused loudly — a
    model must never be decoded through the wrong alphabet.
    """
    name = model.get("vocabulary", "legacy")
    if name not in REPAIR_VOCABULARIES:
        raise ValueError(
            "repair model vocabulary must be one of "
            + ", ".join(sorted(REPAIR_VOCABULARIES))
            + f": {name}"
        )
    live_tokens, class_tokens, perception = REPAIR_VOCABULARIES[name]
    recorded = model.get("class_tokens")
    if recorded is not None and list(recorded) != class_tokens:
        raise ValueError(
            f"repair model class_tokens do not match its {name} vocabulary"
        )
    return live_tokens, class_tokens, perception


def neighborhood_features(
    matrix: list[list[str]],
    x: int,
    y: int,
    *,
    live_index: dict[str, int] = LIVE_INDEX,
    perception: dict[str, str] = PERCEPTION_LIVE,
) -> list[tuple[int, float]]:
    """Sparse one-hot features for the 5x5 neighborhood of a cell.

    The layout derives from the matrix's own dimensions and the
    vocabulary's live-token count (DR 0041); at 8x8 with the legacy
    defaults every index is identical to the historical fixed layout.
    """
    height = len(matrix)
    width = len(matrix[0]) if height else 0
    position_base = len(NEIGHBORHOOD_OFFSETS) * len(live_index)
    features: list[tuple[int, float]] = []
    for offset_index, (dx, dy) in enumerate(NEIGHBORHOOD_OFFSETS):
        nx = x + dx
        ny = y + dy
        if 0 <= nx < width and 0 <= ny < height:
            token = matrix[ny][nx]
            if token != ".":
                features.append(
                    (
                        offset_index * len(live_index)
                        + live_index[perception.get(token, token)],
                        1.0,
                    )
                )
    features.append((position_base + y * width + x, 1.0))
    features.append((position_base + width * height, 1.0))
    return features


def train_softmax(
    examples: list[tuple[list[tuple[int, float]], int, float]],
    *,
    epochs: int,
    learning_rate: float,
    feature_count: int = NEIGHBORHOOD_FEATURE_COUNT,
    class_count: int = len(CLASS_TOKENS),
) -> tuple[list[list[float]], float, float]:
    """Deterministic full-batch gradient descent from zero-initial weights."""
    weights = [[0.0] * feature_count for _ in range(class_count)]
    total_weight = sum(weight for _, _, weight in examples)
    initial_loss = final_loss = 0.0
    for epoch in range(epochs):
        gradients = [
            [0.0] * feature_count for _ in range(class_count)
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
            for feature_index in range(feature_count):
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


def require_model_scale(model: dict, matrix: list[list[str]]) -> None:
    """Reject a model/grid scale mismatch loudly (cycle 09 A3).

    Models trained before the size-parametric layout carry no scale keys
    and are treated as the historical 8x8.
    """
    model_width = model.get("width", 8)
    model_height = model.get("height", 8)
    height = len(matrix)
    width = len(matrix[0]) if height else 0
    if (model_width, model_height) != (width, height):
        raise ValueError(
            f"repair model was trained at {model_width}x{model_height} "
            f"but the grid is {width}x{height}"
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
