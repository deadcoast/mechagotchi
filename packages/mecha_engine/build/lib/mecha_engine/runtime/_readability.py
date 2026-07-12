"""Private learned-readability scoring for mecha_engine.runtime (C1).

Verbatim copies — never imports across lab boundaries — of the R3
learned-readability scoring path (decision record 0019):

- ``learned_readability_score``, ``extract_readability_features``, and
  ``_sigmoid`` from ``labs/readability_benchmark/learned_readability.py``;
- the structural-feature helpers they call from
  ``labs/readability_benchmark/readability_benchmark.py``
  (``_organ_points``, ``_component_count``, ``_neighbors8``,
  ``_silhouette_entropy``, ``_symmetry_score``, ``_organ_detectability``,
  ``_palette_contrast_score``, ``_contrast_ratio``,
  ``_relative_luminance``, ``_animation_anchor_coverage``, ``_clamp``).

The same private-copy rule as ``_damage.py`` and ``_cubff.py``: another
module's private file is copied, not imported, and the lab-side parity
test (``labs/readability_benchmark/test_package_readability_parity.py``)
pins this mirror against the lab source so drift cannot be silent.
Identical arithmetic, iteration order, and rounding, so the promoted
``evolve``'s readability-selection reproduces the lab loop bit-for-bit.
"""

from __future__ import annotations

import math
from collections import deque
from statistics import mean


def _clamp(value: object) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0.0
    return max(0.0, min(1.0, number))


def _organ_points(grid: dict, organ_name: str) -> set[tuple[int, int]]:
    points = set()
    organ = grid.get("organs", {}).get(organ_name, {})
    for point in organ.get("cells", []) if isinstance(organ, dict) else []:
        if isinstance(point, list) and len(point) == 2:
            points.add((point[0], point[1]))
    return points


def _component_count(points: set[tuple[int, int]]) -> int:
    remaining = set(points)
    count = 0
    while remaining:
        count += 1
        start = remaining.pop()
        queue: deque[tuple[int, int]] = deque([start])
        while queue:
            x, y = queue.popleft()
            for neighbor in _neighbors8(x, y):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    queue.append(neighbor)
    return count


def _neighbors8(x: int, y: int) -> tuple[tuple[int, int], ...]:
    return (
        (x - 1, y - 1),
        (x, y - 1),
        (x + 1, y - 1),
        (x - 1, y),
        (x + 1, y),
        (x - 1, y + 1),
        (x, y + 1),
        (x + 1, y + 1),
    )


def _silhouette_entropy(points: set[tuple[int, int]], width: int, height: int) -> float:
    if not points or width <= 0 or height <= 0:
        return 0.0
    row_counts = [sum(1 for x, y in points if y == row) for row in range(height)]
    col_counts = [sum(1 for x, y in points if x == col) for col in range(width)]
    distribution = [value for value in row_counts + col_counts if value > 0]
    total = sum(distribution)
    if not total:
        return 0.0
    entropy = -sum((value / total) * math.log2(value / total) for value in distribution)
    return _clamp(entropy / math.log2(width + height))


def _symmetry_score(grid: dict) -> float:
    width = grid.get("grid_size", [0, 0])[0]
    occupied = {(cell.get("x"), cell.get("y"), cell.get("role")) for cell in grid.get("cells", [])}
    if not occupied or not width:
        return 0.0
    mirrored = 0
    for x, y, role in occupied:
        if (width - 1 - x, y, role) in occupied:
            mirrored += 1
    return mirrored / len(occupied)


def _organ_detectability(
    core: set[tuple[int, int]],
    sensors: set[tuple[int, int]],
    expression: set[tuple[int, int]],
) -> float:
    if not core:
        return 0.0
    core_y = mean(y for _, y in core)
    score = 0.0
    if sensors:
        sensor_above_core = sum(1 for _, y in sensors if y <= core_y) / len(sensors)
        score += 0.45 * sensor_above_core
        score += 0.15 if len(sensors) <= 4 else 0.05
    if expression:
        expression_below_sensors = 1.0
        if sensors:
            expression_below_sensors = sum(
                1 for _, y in expression if y >= mean(sensor_y for _, sensor_y in sensors)
            ) / len(expression)
        score += 0.3 * expression_below_sensors
        score += 0.1 if len(expression) <= 3 else 0.03
    return _clamp(score)


def _palette_contrast_score(grid: dict) -> float:
    palette = grid.get("palette", {})
    colors = palette.get("colors", [])
    background_index = palette.get("background_index", 0)
    if not isinstance(colors, list) or not colors:
        return 0.0
    background = colors[background_index] if background_index < len(colors) else colors[0]
    foreground = [cell.get("visual") for cell in grid.get("cells", []) if cell.get("visual")]
    if not foreground:
        return 0.0
    ratios = [_contrast_ratio(background, color) for color in foreground]
    return _clamp(mean(ratios) / 7.0)


def _contrast_ratio(left: str, right: str) -> float:
    left_lum = _relative_luminance(left)
    right_lum = _relative_luminance(right)
    lighter = max(left_lum, right_lum)
    darker = min(left_lum, right_lum)
    return (lighter + 0.05) / (darker + 0.05)


def _relative_luminance(color: str) -> float:
    color = color.lstrip("#")
    if len(color) != 6:
        return 0.0
    channels = [int(color[index : index + 2], 16) / 255 for index in (0, 2, 4)]
    linear = []
    for channel in channels:
        if channel <= 0.03928:
            linear.append(channel / 12.92)
        else:
            linear.append(((channel + 0.055) / 1.055) ** 2.4)
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _animation_anchor_coverage(grid: dict) -> float:
    anchors = [
        cell for cell in grid.get("cells", []) if cell.get("animation_anchor") is True
    ]
    if not anchors:
        return 0.0
    if len(anchors) == 1 and anchors[0].get("organ") == "core":
        return 1.0
    return 0.5


def extract_readability_features(grid: dict) -> dict[str, float]:
    """Raw structural measurables — the model's input, never the
    heuristic's blended score."""
    width, height = grid.get("grid_size", [0, 0])
    cells = grid.get("cells", [])
    occupied = {(cell.get("x"), cell.get("y")) for cell in cells}
    core = {
        (cell.get("x"), cell.get("y"))
        for cell in cells
        if cell.get("organ") == "core"
    }
    sensors = _organ_points(grid, "sensors")
    expression = _organ_points(grid, "expression")
    component_count = _component_count(occupied)
    return {
        "inverse_component_count": round(
            1.0 / component_count if component_count else 0.0, 6
        ),
        "body_mass_ratio": round(
            len(core) / (width * height) if width and height else 0.0, 6
        ),
        "silhouette_entropy": round(
            _silhouette_entropy(occupied, width, height), 6
        ),
        "symmetry_score": round(_symmetry_score(grid), 6),
        "organ_detectability": round(
            _organ_detectability(core, sensors, expression), 6
        ),
        "palette_contrast": round(_palette_contrast_score(grid), 6),
        "animation_anchor_coverage": round(
            _animation_anchor_coverage(grid), 6
        ),
    }


def _sigmoid(value: float) -> float:
    value = max(-30.0, min(30.0, value))
    return 1.0 / (1.0 + math.exp(-value))


def learned_readability_score(grid: dict, model: dict) -> float:
    """The LEARNED model's readability opinion for one grid, in [0, 1].

    A pairwise ranker only defines score DIFFERENCES (any bias cancels
    in training), so the absolute score is anchored on the model's
    `reference_features` — the training corpus's mean feature vector.
    Above the corpus average reads > 0.5; without the anchor the
    sigmoid saturates at 1.0 for every healthy grid and the score
    cannot discriminate."""
    features = extract_readability_features(grid)
    reference = model.get("reference_features", {})
    raw = sum(
        model["weights"][name]
        * (features[name] - reference.get(name, 0.0))
        for name in model["weights"]
    )
    return round(_sigmoid(raw), 6)
