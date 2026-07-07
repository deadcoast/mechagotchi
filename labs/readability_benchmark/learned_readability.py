"""Learned readability — TRUE ML as the primary path (R3, DR 0019).

The manual rating pipeline stays exactly as built as the FALLBACK and
future calibration check; this module delivers the primary path: a
model that LEARNS readability from engine-derived signals with no human
in the training loop.

Training signal: physics-supervised pairwise learning. For any grid the
engine manufactures a provably-less-readable counterpart (contrast
collapse, organ scatter, silhouette noise, anchor erosion), and every
pair is VERIFIED against the physical metric its family targets before
it may enter the corpus — labels come from measurable physics (WCAG
relative luminance, connected-component counts, organ layout geometry,
anchor coverage), never from a person and never assumed.

Model: a linear pairwise ranker trained with the Bradley-Terry/logistic
objective P(a preferred over b) = sigmoid(w . (f(a) - f(b))) by
stochastic gradient ascent (stdlib math only). Features are raw
measurables — NOT the hand-designed heuristic's blended score — so the
weights are learned, not copied. The trained weights are reported per
feature: the model's opinion is auditable.

Honest gates (asserted by tests and reported): heldout accuracy well
above chance; leave-one-family-out generalization (trained WITHOUT one
degradation family, must still rank that family's pairs — learning
readability, not the degradation trick); determinism; the manual
fallback untouched.
"""

import argparse
import json
import math
import random
import sys
from copy import deepcopy
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME = ROOT / "labs" / "grid_genome"
if str(GRID_GENOME) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME))

from corpus_builder import build_seed_grids  # noqa: E402

from readability_benchmark import (  # noqa: E402
    _animation_anchor_coverage,
    _component_count,
    _organ_detectability,
    _organ_points,
    _palette_contrast_score,
    _silhouette_entropy,
    _symmetry_score,
    score_readability,
)


ARTIFACT_ID = "learned_readability_stage0"

FEATURE_NAMES = [
    "inverse_component_count",
    "body_mass_ratio",
    "silhouette_entropy",
    "symmetry_score",
    "organ_detectability",
    "palette_contrast",
    "animation_anchor_coverage",
]

# family -> the physical metric that must STRICTLY DECREASE for a
# manufactured pair to be admitted (the physics label, verified).
DEGRADATION_FAMILIES = {
    "contrast_collapse": "palette_contrast",
    "organ_scatter": "organ_detectability",
    "silhouette_noise": "inverse_component_count",
    "anchor_erosion": "animation_anchor_coverage",
}

_MAX_ATTEMPTS_PER_PAIR = 24

# Mild secondary degraders eligible per primary family (never itself).
_SECONDARIES = {
    family: [other for other in DEGRADATION_FAMILIES if other != family]
    for family in DEGRADATION_FAMILIES
}


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


def _blend_toward(color: str, background: str, factor: float) -> str:
    color = color.lstrip("#")
    background = background.lstrip("#")
    channels = []
    for index in (0, 2, 4):
        fg = int(color[index : index + 2], 16)
        bg = int(background[index : index + 2], 16)
        channels.append(round(bg + (fg - bg) * (1.0 - factor)))
    return "#" + "".join(f"{channel:02x}" for channel in channels)


def _degrade_contrast_collapse(
    grid: dict, rng: random.Random, *, mild: bool = False
) -> dict:
    degraded = deepcopy(grid)
    palette = degraded.get("palette", {})
    colors = palette.get("colors", ["#000000"])
    background = colors[palette.get("background_index", 0)]
    factor = rng.uniform(0.15, 0.35) if mild else rng.uniform(0.7, 0.95)
    for cell in degraded.get("cells", []):
        if cell.get("visual"):
            cell["visual"] = _blend_toward(cell["visual"], background, factor)
    return degraded


def _degrade_organ_scatter(
    grid: dict, rng: random.Random, *, mild: bool = False
) -> dict:
    """Swap organ MEMBERSHIP between sensor/expression points and core
    points — on both schema surfaces (the organs coordinate map, which
    the detectability physics reads, and the per-cell organ/role tags)
    so the degraded foil stays internally consistent."""
    degraded = deepcopy(grid)
    organs = degraded.get("organs", {})
    by_pos = {
        (cell.get("x"), cell.get("y")): cell
        for cell in degraded.get("cells", [])
    }
    swaps = 1 if mild else rng.randint(2, 4)
    for _ in range(swaps):
        organ_name = ("sensors", "expression")[rng.randrange(2)]
        points = organs.get(organ_name, {}).get("cells", [])
        core_points = organs.get("core", {}).get("cells", [])
        if not points or not core_points:
            continue
        i = rng.randrange(len(points))
        j = rng.randrange(len(core_points))
        organ_pos = (points[i][0], points[i][1])
        core_pos = (core_points[j][0], core_points[j][1])
        points[i], core_points[j] = (
            [core_pos[0], core_pos[1]],
            [organ_pos[0], organ_pos[1]],
        )
        organ_cell = by_pos.get(organ_pos)
        core_cell = by_pos.get(core_pos)
        if organ_cell and core_cell:
            for key in ("organ", "role"):
                organ_cell[key], core_cell[key] = (
                    core_cell[key],
                    organ_cell[key],
                )
    return degraded


def _degrade_silhouette_noise(
    grid: dict, rng: random.Random, *, mild: bool = False
) -> dict:
    degraded = deepcopy(grid)
    cells = degraded.get("cells", [])
    width, height = degraded.get("grid_size", [0, 0])
    occupied = {(cell.get("x"), cell.get("y")) for cell in cells}
    empty = [
        (x, y)
        for x in range(width)
        for y in range(height)
        if (x, y) not in occupied
    ]
    rng.shuffle(empty)
    movable = [
        index
        for index, cell in enumerate(cells)
        if cell.get("organ") != "core"
    ]
    rng.shuffle(movable)
    budget = 1 if mild else 3
    for index in movable[: min(budget, len(empty))]:
        x, y = empty.pop()
        cells[index]["x"], cells[index]["y"] = x, y
    return degraded


def _degrade_anchor_erosion(
    grid: dict, rng: random.Random, *, mild: bool = False
) -> dict:
    degraded = deepcopy(grid)
    for cell in degraded.get("cells", []):
        cell["animation_anchor"] = False
    return degraded


_DEGRADERS = {
    "contrast_collapse": _degrade_contrast_collapse,
    "organ_scatter": _degrade_organ_scatter,
    "silhouette_noise": _degrade_silhouette_noise,
    "anchor_erosion": _degrade_anchor_erosion,
}


def build_degradation_pairs(
    grids: list[dict], *, pairs_per_family: int, rng_seed: int
) -> list[dict]:
    """Physics-verified (better, worse) comparisons. A pair is admitted
    only if the family's target metric STRICTLY decreased — the label
    is checked, never assumed."""
    rng = random.Random(rng_seed)
    pairs = []
    for grid in grids:
        better = extract_readability_features(grid)
        for family, metric in DEGRADATION_FAMILIES.items():
            produced = 0
            attempts = 0
            while (
                produced < pairs_per_family
                and attempts < _MAX_ATTEMPTS_PER_PAIR
            ):
                attempts += 1
                degraded = _DEGRADERS[family](grid, rng)
                # Composite degradation: real damage co-occurs, so half
                # the pairs carry a MILD secondary perturbation from
                # another family. Families overlap in feature space —
                # the reason a model trained without one family can
                # still generalize to it. BOTH perturbed metrics must
                # verifiably decrease (an unverified secondary would
                # feed the trainer sign-flipped physics); otherwise the
                # pure primary degradation is kept.
                if rng.random() < 0.5:
                    secondary = _SECONDARIES[family][
                        rng.randrange(len(_SECONDARIES[family]))
                    ]
                    candidate = _DEGRADERS[secondary](degraded, rng, mild=True)
                    candidate_features = extract_readability_features(candidate)
                    secondary_metric = DEGRADATION_FAMILIES[secondary]
                    if (
                        candidate_features[secondary_metric]
                        < better[secondary_metric]
                        and candidate_features[metric] < better[metric]
                    ):
                        degraded = candidate
                worse = extract_readability_features(degraded)
                if worse[metric] < better[metric]:
                    produced += 1
                    pairs.append(
                        {
                            "family": family,
                            "grid_id": grid.get("grid_id", "unknown_grid"),
                            "better_features": better,
                            "worse_features": worse,
                        }
                    )
    return pairs


def _sigmoid(value: float) -> float:
    value = max(-30.0, min(30.0, value))
    return 1.0 / (1.0 + math.exp(-value))


def _margin(weights: dict[str, float], pair: dict) -> float:
    return sum(
        weights[name]
        * (pair["better_features"][name] - pair["worse_features"][name])
        for name in weights
    )


def train_pairwise_ranker(
    pairs: list[dict],
    *,
    rng_seed: int,
    epochs: int = 300,
    learning_rate: float = 0.5,
    l2: float = 1e-4,
) -> dict:
    """Bradley-Terry/logistic pairwise SGD from zero-initialized
    weights. Deterministic for a fixed seed."""
    rng = random.Random(rng_seed)
    weights = {name: 0.0 for name in FEATURE_NAMES}
    order = list(range(len(pairs)))
    for _ in range(epochs):
        rng.shuffle(order)
        for index in order:
            pair = pairs[index]
            probability = _sigmoid(_margin(weights, pair))
            for name in FEATURE_NAMES:
                difference = (
                    pair["better_features"][name]
                    - pair["worse_features"][name]
                )
                gradient = (1.0 - probability) * difference - l2 * weights[name]
                weights[name] += learning_rate * gradient
    weights = {name: round(value, 9) for name, value in weights.items()}
    correct = sum(1 for pair in pairs if _margin(weights, pair) > 0.0)
    return {
        "objective": "bradley_terry_logistic_pairwise",
        "feature_names": list(FEATURE_NAMES),
        "weights": weights,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "l2": l2,
        "train_pair_count": len(pairs),
        "train_accuracy": round(correct / len(pairs), 6) if pairs else 0.0,
    }


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


def _pairwise_accuracy(model: dict, pairs: list[dict]) -> float:
    if not pairs:
        return 0.0
    correct = sum(
        1 for pair in pairs if _margin(model["weights"], pair) > 0.0
    )
    return round(correct / len(pairs), 6)


def _kendall_tau(left: list[float], right: list[float]) -> float:
    concordant = 0
    discordant = 0
    for i in range(len(left)):
        for j in range(i + 1, len(left)):
            product = (left[i] - left[j]) * (right[i] - right[j])
            if product > 0:
                concordant += 1
            elif product < 0:
                discordant += 1
    total = concordant + discordant
    return round((concordant - discordant) / total, 6) if total else 0.0


def build_learned_readability_report(*, rng_seed: int) -> dict:
    grids = build_seed_grids()
    pairs = build_degradation_pairs(grids, pairs_per_family=3, rng_seed=rng_seed)
    rng = random.Random(rng_seed)
    shuffled = list(pairs)
    rng.shuffle(shuffled)
    split = int(len(shuffled) * 0.8)
    train_pairs, heldout_pairs = shuffled[:split], shuffled[split:]

    model = train_pairwise_ranker(train_pairs, rng_seed=rng_seed)
    corpus_features = [extract_readability_features(grid) for grid in grids]
    model["reference_features"] = {
        name: round(
            sum(features[name] for features in corpus_features)
            / len(corpus_features),
            6,
        )
        for name in FEATURE_NAMES
    }
    heldout_accuracy = _pairwise_accuracy(model, heldout_pairs)

    leave_one_family_out = {}
    for family in DEGRADATION_FAMILIES:
        without = [pair for pair in pairs if pair["family"] != family]
        only = [pair for pair in pairs if pair["family"] == family]
        loo_model = train_pairwise_ranker(without, rng_seed=rng_seed)
        leave_one_family_out[family] = {
            "training_pair_count": len(without),
            "unseen_family_pair_count": len(only),
            "unseen_family_accuracy": _pairwise_accuracy(loo_model, only),
        }

    learned_scores = [learned_readability_score(grid, model) for grid in grids]
    heuristic_scores = [
        score_readability(grid)["proxy_readability_score"] for grid in grids
    ]
    per_family_counts = {
        family: sum(1 for pair in pairs if pair["family"] == family)
        for family in DEGRADATION_FAMILIES
    }

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "learned_model_trained_and_validated",
        "date": date.today().isoformat(),
        "purpose": (
            "R3 (decision record 0019): TRUE ML as the primary readability "
            "path — a linear pairwise ranker trained on physics-verified "
            "degradation comparisons (no human labels in the loop). The "
            "manual rating pipeline stays exactly as built as the FALLBACK "
            "and calibration check."
        ),
        "readability_authority": "learned_model_primary_manual_rating_fallback",
        "source_artifacts": [
            "labs/grid_genome/corpus_builder.py",
            "labs/readability_benchmark/readability_benchmark.py",
            "research/decision_records/0019-learned-readability.md",
        ],
        "rng_seed": rng_seed,
        "corpus": {
            "grid_count": len(grids),
            "pair_count": len(pairs),
            "pairs_per_family_requested": 3,
            "per_family_pair_counts": per_family_counts,
            "train_pair_count": len(train_pairs),
            "heldout_pair_count": len(heldout_pairs),
        },
        "model": model,
        "metrics": {
            "heldout_accuracy": heldout_accuracy,
            "leave_one_family_out": leave_one_family_out,
            "heuristic_rank_agreement": _kendall_tau(
                learned_scores, heuristic_scores
            ),
            "learned_score_mean": round(
                sum(learned_scores) / len(learned_scores), 6
            ),
        },
        "closed_states": [
            "physics_verified_pair_factory",
            "pairwise_ranker_trained_from_zero_init",
            "heldout_evaluation",
            "leave_one_family_out_generalization",
            "deterministic_training",
        ],
        "blocked_states": [
            "manual_calibration_check",
            "nonlinear_model_ceiling_study",
        ],
        "decision": (
            "Adopt the learned model as the primary readability signal. "
            "manual_calibration_check is the FALLBACK path's job when the "
            "owner schedules the human study (human DATA comes only from "
            "humans) — a quality check on this model, never a development "
            "blocker. A nonlinear model is warranted only if the linear "
            "ceiling is measured and found wanting."
        ),
        "next_research_step": (
            "Wire learned readability into the evolution loop's parent "
            "selection (the DR 0019 live consumer) and measure the A/B "
            "at a fixed seed; later, promote the scorer by its own record."
        ),
    }


def write_learned_readability_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{ARTIFACT_ID}.json"
    path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "data" / "readability_benchmark",
    )
    parser.add_argument("--rng-seed", type=int, default=20260706)
    args = parser.parse_args()
    report = build_learned_readability_report(rng_seed=args.rng_seed)
    write_learned_readability_artifacts(args.output_dir, report)
    print(
        json.dumps(
            {
                "artifact_id": report["artifact_id"],
                "heldout_accuracy": report["metrics"]["heldout_accuracy"],
                "leave_one_family_out": {
                    family: entry["unseen_family_accuracy"]
                    for family, entry in report["metrics"][
                        "leave_one_family_out"
                    ].items()
                },
                "weights": report["model"]["weights"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
