import argparse
import json
import math
import sys
from collections import deque
from copy import deepcopy
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME = ROOT / "labs" / "grid_genome"
if str(GRID_GENOME) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME))

from constrained_generator import build_constrained_corpus
from corpus_builder import build_seed_grids
from markov_grid import build_markov_corpus
from validator import validate_grid


WEIGHTS = {
    "validity": 0.18,
    "component_score": 0.14,
    "body_mass_score": 0.12,
    "silhouette_score": 0.12,
    "symmetry_score": 0.1,
    "organ_detectability": 0.18,
    "palette_contrast": 0.1,
    "animation_anchor_coverage": 0.06,
}


def score_readability(grid: dict) -> dict:
    validation = validate_grid(grid)
    width, height = grid.get("grid_size", [0, 0])
    cells = grid.get("cells", [])
    occupied = {(cell.get("x"), cell.get("y")) for cell in cells}
    core = {(cell.get("x"), cell.get("y")) for cell in cells if cell.get("organ") == "core"}
    sensors = _organ_points(grid, "sensors")
    expression = _organ_points(grid, "expression")

    component_count = _component_count(occupied)
    component_score = 1.0 if component_count == 1 else max(0.0, 1.0 - (component_count - 1) * 0.25)
    body_mass_ratio = len(core) / (width * height) if width and height else 0.0
    body_mass_score = _triangular_score(body_mass_ratio, ideal=0.16, span=0.14)
    silhouette_entropy = _silhouette_entropy(occupied, width, height)
    silhouette_score = _triangular_score(silhouette_entropy, ideal=0.62, span=0.38)
    symmetry_score = _symmetry_score(grid)
    organ_detectability = _organ_detectability(core, sensors, expression)
    palette_contrast = _palette_contrast_score(grid)
    animation_anchor_coverage = _animation_anchor_coverage(grid)
    validity = 1.0 if validation.ok else 0.0

    components = {
        "validity": validity,
        "component_score": component_score,
        "body_mass_score": body_mass_score,
        "silhouette_score": silhouette_score,
        "symmetry_score": symmetry_score,
        "organ_detectability": organ_detectability,
        "palette_contrast": palette_contrast,
        "animation_anchor_coverage": animation_anchor_coverage,
    }
    proxy_readability = sum(components[key] * WEIGHTS[key] for key in WEIGHTS)

    return {
        "grid_id": grid.get("grid_id", "unknown_grid"),
        "valid": validation.ok,
        "validation_errors": validation.errors,
        "proxy_readability_score": round(_clamp(proxy_readability), 6),
        "metrics": {
            "connected_components": component_count,
            "body_mass_ratio": round(body_mass_ratio, 6),
            "silhouette_entropy": round(silhouette_entropy, 6),
            "symmetry_score": round(symmetry_score, 6),
            "organ_detectability": round(organ_detectability, 6),
            "palette_contrast": round(palette_contrast, 6),
            "animation_anchor_coverage": round(animation_anchor_coverage, 6),
        },
        "score_components": {key: round(value, 6) for key, value in components.items()},
        "human_readability_rating": None,
        "manual_rating_status": "not_collected",
    }


def manual_rating_protocol() -> dict:
    return {
        "protocol_id": "readability_rating_v0_1",
        "ratings_collected": False,
        "rating_scale": [1, 2, 3, 4, 5],
        "questions": {
            "silhouette": "Can the creature body be recognized from its outline alone?",
            "organ_clarity": "Are sensors, expression cells, and body core easy to identify?",
            "palette_contrast": "Does the palette separate body, organs, and background?",
            "animation_readiness": "Is there a clear anchor or pose feature for simple motion?",
            "companion_appeal": "Does the grid read as a plausible companion rather than noise?",
        },
        "instructions": [
            "Rate each sample independently before seeing generator source.",
            "Use 1 for unreadable/noisy, 3 for usable but ambiguous, and 5 for immediately legible.",
            "Do not treat novelty as readability unless the creature remains recognizable.",
            "Record reviewer id, timestamp, and optional notes separately from proxy metrics.",
        ],
        "minimum_reviewers": 3,
        "aggregation": "median_per_question_then_mean",
        "status": "protocol_defined_no_human_ratings_yet",
    }


def build_heldout_readability_benchmark(
    *, count_per_source: int = 10, rng_seed: int = 20260512
) -> dict:
    seeds = build_seed_grids()
    samples: list[dict] = []
    for grid in seeds[-count_per_source:]:
        samples.append(_sample_entry("seed_holdout", grid))

    constrained = build_constrained_corpus(
        seeds, count=count_per_source, rng_seed=rng_seed + 101
    )
    for grid in constrained:
        samples.append(_sample_entry("constrained_holdout", grid))

    markov = build_markov_corpus(seeds, count=count_per_source, rng_seed=rng_seed + 202)
    for grid in markov:
        samples.append(_sample_entry("markov_holdout", grid))

    by_source = {}
    for source in sorted({sample["source"] for sample in samples}):
        group = [sample for sample in samples if sample["source"] == source]
        scores = [sample["readability"]["proxy_readability_score"] for sample in group]
        valid_count = sum(1 for sample in group if sample["readability"]["valid"])
        by_source[source] = {
            "sample_count": len(group),
            "valid_count": valid_count,
            "mean_proxy_readability": round(mean(scores), 6) if scores else 0,
            "min_proxy_readability": min(scores) if scores else 0,
            "max_proxy_readability": max(scores) if scores else 0,
        }

    return {
        "lab_id": "readability_benchmark_stage0",
        "date": "2026-05-12",
        "rng_seed": rng_seed,
        "count_per_source": count_per_source,
        "summary": {
            "sample_count": len(samples),
            "source_count": len(by_source),
            "mean_proxy_readability": round(
                mean(sample["readability"]["proxy_readability_score"] for sample in samples),
                6,
            )
            if samples
            else 0,
            "by_source": by_source,
        },
        "manual_rating_protocol": manual_rating_protocol(),
        "samples": samples,
        "source_refs": [
            {
                "name": "On the Evaluation of Procedural Level Generation Systems",
                "url": "https://arxiv.org/abs/2404.18657",
                "use": "Supports explicit, reusable evaluation frameworks for generated content.",
            },
            {
                "name": "On the Challenges of Generating Pixel Art Character Sprites Using GANs",
                "url": "https://ojs.aaai.org/index.php/AIIDE/article/view/21951",
                "use": "Pixel-art sprite generation reference using visual inspection and quantitative metrics.",
            },
            {
                "name": "Generating Pixel Art Character Sprites using GANs",
                "url": "https://arxiv.org/abs/2208.06413",
                "use": "Reference for combining visual inspection with quantitative image metrics.",
            },
        ],
        "decision": "prototype",
        "limitations": [
            "Human ratings are protocol-defined but not collected in Stage 0.",
            "Proxy readability weights are hand-set and must be calibrated against ratings.",
            "The held-out set is deterministic and small; it is a benchmark seed, not a final study.",
        ],
    }


def write_readability_artifacts(output_dir: Path, benchmark: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "readability_stage0.json").write_text(
        json.dumps(benchmark, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "manual_rating_protocol.md").write_text(
        _protocol_markdown(benchmark["manual_rating_protocol"]),
        encoding="utf-8",
    )
    (output_dir / "README.md").write_text(
        "# Readability Benchmark Stage 0\n\n"
        "Held-out readability benchmark for semantic grid-genome samples.\n\n"
        "Artifacts:\n\n"
        "- `readability_stage0.json`\n"
        "- `manual_rating_protocol.md`\n\n"
        "Human ratings have not been collected yet; the protocol is included so later\n"
        "ratings can be compared with the proxy metric without changing the sample set.\n",
        encoding="utf-8",
    )


def _sample_entry(source: str, grid: dict) -> dict:
    grid_copy = deepcopy(grid)
    return {
        "sample_id": f"{source}:{grid_copy.get('grid_id', 'unknown')}",
        "source": source,
        "grid_id": grid_copy.get("grid_id", "unknown_grid"),
        "grid": grid_copy,
        "readability": score_readability(grid_copy),
        "manual_rating": None,
    }


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


def _triangular_score(value: float, *, ideal: float, span: float) -> float:
    return _clamp(1.0 - abs(value - ideal) / span)


def _protocol_markdown(protocol: dict) -> str:
    lines = [
        "# Manual Readability Rating Protocol",
        "",
        f"Protocol: `{protocol['protocol_id']}`",
        "",
        "## Rating Scale",
        "",
        "- 1: unreadable or noisy",
        "- 2: weakly readable",
        "- 3: usable but ambiguous",
        "- 4: clear",
        "- 5: immediately legible",
        "",
        "## Questions",
        "",
    ]
    for key, question in protocol["questions"].items():
        lines.append(f"- `{key}`: {question}")
    lines.extend(
        [
            "",
            "## Instructions",
            "",
        ]
    )
    for instruction in protocol["instructions"]:
        lines.append(f"- {instruction}")
    lines.extend(
        [
            "",
            f"Minimum reviewers: {protocol['minimum_reviewers']}",
            f"Aggregation: `{protocol['aggregation']}`",
            "",
        ]
    )
    return "\n".join(lines)


def _clamp(value: object) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0.0
    return max(0.0, min(1.0, number))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("data/readability"))
    parser.add_argument("--count-per-source", type=int, default=10)
    parser.add_argument("--rng-seed", type=int, default=20260512)
    args = parser.parse_args()
    benchmark = build_heldout_readability_benchmark(
        count_per_source=args.count_per_source,
        rng_seed=args.rng_seed,
    )
    write_readability_artifacts(args.output_dir, benchmark)
    print(json.dumps(benchmark["summary"], indent=2))


if __name__ == "__main__":
    main()
