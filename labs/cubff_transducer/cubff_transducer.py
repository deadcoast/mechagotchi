import argparse
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


GRID_GENOME_DIR = Path(__file__).resolve().parents[1] / "grid_genome"
if str(GRID_GENOME_DIR) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME_DIR))

from constrained_generator import generate_constrained_grid, train_constraints
from corpus_builder import build_seed_grids
from slip import is_grid_aligned
from validator import validate_grid


RAW_PALETTE = ["#0f1115", "#59616f", "#9aa4b5", "#e8ecf2"]


def extract_cubff_features(snapshot: dict) -> dict:
    tape = _tape_values(snapshot)
    replication_scores = [
        float(value) for value in snapshot.get("replication_scores", []) if _is_number(value)
    ]
    lineage_events = snapshot.get("lineage_events", [])
    if not isinstance(lineage_events, list):
        lineage_events = []

    entropy = _normalized_entropy(tape)
    motif_counts = _motif_counts(tape)
    motif_repetition_rate = _motif_repetition_rate(motif_counts)
    instruction_diversity = len(set(tape)) / len(tape) if tape else 0
    high_replication_count = sum(1 for score in replication_scores if score >= 48)
    replication_rate = (
        high_replication_count / len(replication_scores) if replication_scores else 0
    )
    score_sum = sum(replication_scores)
    replication_dominance = max(replication_scores) / score_sum if score_sum else 0
    lineage_churn = min(1, len(lineage_events) / max(1, len(replication_scores)))
    compression_ratio = _compression_ratio(snapshot, tape)
    instability = _clamp(
        0.45 * entropy
        + 0.3 * lineage_churn
        + 0.25 * (1 - replication_dominance if replication_scores else 0.5)
    )
    semantic_pressure = _clamp(
        0.5 * replication_rate + 0.25 * motif_repetition_rate + 0.25 * lineage_churn
    )

    return {
        "snapshot_id": str(snapshot.get("snapshot_id", "cubff_snapshot")),
        "epoch": int(snapshot.get("epoch", 0)) if isinstance(snapshot.get("epoch", 0), int) else 0,
        "language": str(snapshot.get("language", "unknown")),
        "tape_length": len(tape),
        "symbol_entropy": round(entropy, 6),
        "instruction_diversity": round(instruction_diversity, 6),
        "motif_repetition_rate": round(motif_repetition_rate, 6),
        "replication_rate": round(replication_rate, 6),
        "replication_dominance": round(replication_dominance, 6),
        "lineage_churn": round(lineage_churn, 6),
        "compression_ratio": round(compression_ratio, 6),
        "instability": round(instability, 6),
        "semantic_pressure": round(semantic_pressure, 6),
        "top_motifs": [
            {"motif": motif, "count": count}
            for motif, count in sorted(
                motif_counts.items(), key=lambda item: (-item[1], item[0])
            )[:5]
        ],
    }


def direct_tape_to_grid(snapshot: dict, grid_id: str) -> dict:
    tape = _tape_values(snapshot)
    padded = (tape + [0] * 64)[:64]
    cells = []
    for index, value in enumerate(padded):
        x = index % 8
        y = index // 8
        cells.append(
            {
                "x": x,
                "y": y,
                "visual": RAW_PALETTE[value % len(RAW_PALETTE)],
                "role": "raw_byte",
                "material": "signal",
                "mutation_weight": round((value % 256) / 255, 6),
                "animation_anchor": False,
                "organ": None,
                "stress": 0,
                "damage": 0,
                "locked": False,
            }
        )

    return {
        "grid_id": grid_id,
        "schema_version": "0.1.0",
        "parent_grid_id": None,
        "grid_size": [8, 8],
        "cells": cells,
        "organs": {},
        "palette": {
            "palette_id": "cubff_raw_gray",
            "colors": RAW_PALETTE,
            "background_index": 0,
        },
        "mutation": {
            "cell_mutation_rate": 0.05,
            "organ_shift_rate": 0.02,
            "palette_shift_rate": 0.01,
            "symmetry_break_rate": 0.01,
        },
        "lineage": {
            "generation": 0,
            "ancestor_ids": [],
            "mutation_events": ["cubff_direct_tape_projection"],
        },
        "metadata": {
            "source": "cubff_direct_visual_baseline",
            "cubff_snapshot_id": str(snapshot.get("snapshot_id", "cubff_snapshot")),
            "readability_score": 0,
        },
    }


def compile_semantic_grid(
    snapshot: dict,
    seed_grids: list[dict],
    slip_profile: dict,
    *,
    grid_id: str,
    rng_seed: int,
) -> dict:
    features = extract_cubff_features(snapshot)
    model = train_constraints(seed_grids)
    grid = generate_constrained_grid(
        model,
        seed_grids,
        grid_id=grid_id,
        rng_seed=rng_seed,
        slip=slip_profile,
    )
    traits = features_to_traits(features)
    mutation_limits = slip_profile["mutation"]
    grid["metadata"]["source"] = "cubff_semantic_transducer"
    grid["metadata"]["cubff_snapshot_id"] = features["snapshot_id"]
    grid["metadata"]["cubff_features"] = features
    grid["metadata"]["cubff_traits"] = traits
    grid["metadata"]["readability_score"] = score_readability(grid)
    grid["lineage"]["mutation_events"].append("cubff_semantic_pressure")
    grid["mutation"]["cell_mutation_rate"] = min(
        mutation_limits["cell_mutation_rate_max"],
        round(0.02 + traits["mutation_pressure"] * 0.13, 6),
    )
    grid["mutation"]["organ_shift_rate"] = min(
        mutation_limits["organ_shift_rate_max"],
        round(0.01 + traits["structural_pressure"] * 0.04, 6),
    )
    grid["mutation"]["palette_shift_rate"] = min(
        mutation_limits["palette_shift_rate_max"],
        round(0.005 + traits["temperament"]["curiosity"] * 0.025, 6),
    )
    grid["mutation"]["symmetry_break_rate"] = min(
        mutation_limits["symmetry_break_rate_max"],
        round(0.005 + traits["animation_instability"] * 0.035, 6),
    )
    return grid


def features_to_traits(features: dict) -> dict:
    mutation_pressure = _clamp(
        0.45 * features["instability"]
        + 0.35 * features["semantic_pressure"]
        + 0.2 * features["instruction_diversity"]
    )
    structural_pressure = _clamp(
        0.55 * features["replication_rate"] + 0.45 * features["motif_repetition_rate"]
    )
    curiosity = _clamp(0.25 + 0.55 * features["symbol_entropy"])
    neediness = _clamp(0.2 + 0.5 * features["lineage_churn"])
    sleepiness = _clamp(0.75 - 0.45 * features["replication_rate"])

    return {
        "mutation_pressure": round(mutation_pressure, 6),
        "structural_pressure": round(structural_pressure, 6),
        "animation_instability": round(features["instability"], 6),
        "temperament": {
            "curiosity": round(curiosity, 6),
            "neediness": round(neediness, 6),
            "sleepiness": round(sleepiness, 6),
        },
    }


def run_transducer_lab(
    snapshots: list[dict],
    seed_grids: list[dict],
    slip_profile: dict,
    *,
    rng_seed: int = 5150,
    semantic_grids: list[dict] | None = None,
) -> dict:
    direct_grids = [
        direct_tape_to_grid(snapshot, grid_id=f"cubff_direct_{index:03d}")
        for index, snapshot in enumerate(snapshots)
    ]
    if semantic_grids is None:
        semantic_grids = [
            compile_semantic_grid(
                snapshot,
                seed_grids,
                slip_profile,
                grid_id=f"cubff_semantic_{index:03d}",
                rng_seed=rng_seed + index,
            )
            for index, snapshot in enumerate(snapshots)
        ]
    features = [extract_cubff_features(snapshot) for snapshot in snapshots]
    trait_vectors = [features_to_traits(feature) for feature in features]

    direct = _summarize_grids(direct_grids, slip_profile)
    hybrid = _summarize_grids(semantic_grids, slip_profile)
    direct["pipeline"] = "A: raw tape to pixels"
    hybrid["pipeline"] = "D: CUBFF traits plus constrained grid plus SLIP validator"

    report = {
        "lab_id": "cubff_semantic_transducer_stage0",
        "snapshot_count": len(snapshots),
        "source_mode": "synthetic_cubff_style_snapshots",
        "source_note": (
            "This lab uses synthetic CUBFF-style snapshots shaped after the public "
            "CuBFF state fields. It is not a CUDA CuBFF simulation result."
        ),
        "direct_visual_baseline": direct,
        "statistical_transducer": {
            "pipeline": "B: tape statistics to trait vector",
            "mean_replication_rate": _mean(feature["replication_rate"] for feature in features),
            "mean_semantic_pressure": _mean(
                feature["semantic_pressure"] for feature in features
            ),
            "trait_vectors": trait_vectors,
        },
        "behavioral_transducer": {
            "pipeline": "C: dynamics to temperament and mutation pressure",
            "mean_mutation_pressure": _mean(
                trait["mutation_pressure"] for trait in trait_vectors
            ),
            "mean_animation_instability": _mean(
                trait["animation_instability"] for trait in trait_vectors
            ),
            "temperament_vectors": [
                trait["temperament"] for trait in trait_vectors
            ],
        },
        "hybrid_semantic_compiler": hybrid,
        "decision": _decision(direct, hybrid),
        "source_anchors": [
            "https://arxiv.org/abs/2406.19108",
            "https://github.com/paradigms-of-intelligence/cubff",
        ],
    }
    return report


def score_readability(grid: dict) -> float:
    result = validate_grid(grid)
    organs = grid.get("organs", {})
    present_roles = {
        organ.get("role") for organ in organs.values() if isinstance(organ, dict)
    }
    cells = grid.get("cells", [])
    body_mass = sum(1 for cell in cells if cell.get("organ") == "core")
    has_anchor = any(cell.get("animation_anchor") is True for cell in cells)

    score = 0
    if result.ok:
        score += 0.5
    if "sensor" in present_roles:
        score += 0.18
    if "expression" in present_roles:
        score += 0.12
    if "body_core" in present_roles:
        score += 0.1
    if has_anchor:
        score += 0.06
    if 4 <= body_mass <= 24:
        score += 0.04
    return round(_clamp(score), 6)


def write_lab_outputs(
    output_dir: Path,
    report: dict,
    snapshots: list[dict],
    semantic_grids: list[dict],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "synthetic_snapshots.json").write_text(
        json.dumps(snapshots, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "cubff_transducer_stage0_report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    grids_dir = output_dir / "semantic_grids"
    grids_dir.mkdir(exist_ok=True)
    for grid in semantic_grids:
        (grids_dir / f"{grid['grid_id']}.json").write_text(
            json.dumps(grid, indent=2) + "\n", encoding="utf-8"
        )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")


def build_synthetic_snapshots(count: int, rng_seed: int) -> list[dict]:
    rng = random.Random(rng_seed)
    snapshots = []
    for index in range(count):
        tape = []
        motif = [rng.randrange(0, 32), rng.randrange(0, 32), rng.randrange(0, 32)]
        for position in range(64):
            if position % 7 in {0, 1, 2}:
                tape.append(motif[position % 3])
            else:
                tape.append(rng.randrange(0, 64))
        replication_scores = [
            rng.choice([0, 4, 8, 12, 24, 48, 64]) for _ in range(8)
        ]
        if index % 2 == 0:
            replication_scores[rng.randrange(8)] = 64
        parent = rng.randrange(0, 8)
        lineage_events = [
            {"parent": parent, "child": rng.randrange(0, 8)}
            for _ in range(rng.randrange(1, 5))
        ]
        snapshots.append(
            {
                "snapshot_id": f"cubff_synth_{index:03d}",
                "epoch": 128 + index * 16,
                "language": "bff_noheads",
                "program_size": 64,
                "tape": tape,
                "replication_scores": replication_scores,
                "brotli_size": rng.randrange(24, 58),
                "lineage_events": lineage_events,
            }
        )
    return snapshots


def _summarize_grids(grids: list[dict], slip_profile: dict) -> dict:
    valid_count = 0
    aligned_count = 0
    readability_scores = []
    errors: dict[str, int] = {}
    for grid in grids:
        result = validate_grid(grid)
        if result.ok:
            valid_count += 1
        for error in result.errors:
            errors[error] = errors.get(error, 0) + 1
        if is_grid_aligned(grid, slip_profile).ok:
            aligned_count += 1
        readability_scores.append(score_readability(grid))

    count = len(grids)
    return {
        "candidate_count": count,
        "valid_count": valid_count,
        "invalid_count": count - valid_count,
        "validity_rate": valid_count / count if count else 0,
        "slip_aligned_count": aligned_count,
        "slip_alignment_rate": aligned_count / count if count else 0,
        "mean_readability": _mean(readability_scores),
        "error_counts": dict(sorted(errors.items())),
    }


def _decision(direct: dict, hybrid: dict) -> dict:
    improves_readability = (
        hybrid["mean_readability"] > direct["mean_readability"]
    )
    improves_validity = hybrid["validity_rate"] > direct["validity_rate"]
    if improves_readability and improves_validity:
        status = "watch_synthetic_only"
        reason = (
            "Semantic compilation beats direct tape projection here, but the input "
            "snapshots are synthetic. Real CuBFF snapshot ingestion is required "
            "before any adoption decision."
        )
    else:
        status = "reject_direct_mapping"
        reason = (
            "Semantic compilation did not beat direct tape projection on both "
            "validity and readability, so this comparison is rejected. The input "
            "snapshots are synthetic, and real CuBFF snapshot ingestion is "
            "required before any adoption decision."
        )
    return {
        "status": status,
        "adoption": "do_not_adopt_core_dependency_from_synthetic_lab",
        "reason": reason,
    }


def _tape_values(snapshot: dict) -> list[int]:
    raw_tape = snapshot.get("tape", snapshot.get("soup", []))
    if isinstance(raw_tape, bytes):
        return list(raw_tape)
    if not isinstance(raw_tape, list):
        return []
    return [int(value) % 256 for value in raw_tape if isinstance(value, int)]


def _normalized_entropy(values: list[int]) -> float:
    if not values:
        return 0
    counts = Counter(values)
    entropy = 0.0
    for count in counts.values():
        probability = count / len(values)
        entropy -= probability * math.log2(probability)
    return entropy / 8


def _motif_counts(values: list[int]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for index in range(len(values) - 2):
        motif = f"{values[index]},{values[index + 1]},{values[index + 2]}"
        counts[motif] = counts.get(motif, 0) + 1
    return counts


def _motif_repetition_rate(motif_counts: dict[str, int]) -> float:
    if not motif_counts:
        return 0
    repeated = sum(count - 1 for count in motif_counts.values() if count > 1)
    total = sum(motif_counts.values())
    return repeated / total if total else 0


def _compression_ratio(snapshot: dict, tape: list[int]) -> float:
    brotli_size = snapshot.get("brotli_size")
    if not _is_number(brotli_size) or not tape:
        return 0
    return float(brotli_size) / len(tape)


def _is_number(value: object) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def _mean(values) -> float:
    items = list(values)
    if not items:
        return 0
    return round(sum(items) / len(items), 6)


def _clamp(value: float) -> float:
    return max(0, min(1, float(value)))


def _readme_text(report: dict) -> str:
    return (
        "# CUBFF Semantic Transducer Stage 0\n\n"
        "Synthetic CUBFF-style snapshots were used to test the Mechagotchi "
        "semantic transducer contract without requiring a CUDA CuBFF run.\n\n"
        "Key results:\n\n"
        f"- Direct visual validity: {report['direct_visual_baseline']['valid_count']}/"
        f"{report['direct_visual_baseline']['candidate_count']}\n"
        f"- Hybrid semantic validity: {report['hybrid_semantic_compiler']['valid_count']}/"
        f"{report['hybrid_semantic_compiler']['candidate_count']}\n"
        f"- Hybrid SLIP alignment: {report['hybrid_semantic_compiler']['slip_aligned_count']}/"
        f"{report['hybrid_semantic_compiler']['candidate_count']}\n"
        f"- Decision: {report['decision']['status']}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/cubff_transducer")
    parser.add_argument("--count", type=int, default=12)
    parser.add_argument("--rng-seed", type=int, default=5150)
    parser.add_argument(
        "--slip", type=Path, default=ROOT / "data/slips/valid/slip_lcd_seed.json"
    )
    args = parser.parse_args()

    snapshots = build_synthetic_snapshots(args.count, args.rng_seed)
    profile = json.loads(args.slip.read_text(encoding="utf-8"))
    seed_grids = build_seed_grids()
    semantic_grids = [
        compile_semantic_grid(
            snapshot,
            seed_grids,
            profile,
            grid_id=f"cubff_semantic_{index:03d}",
            rng_seed=args.rng_seed + index,
        )
        for index, snapshot in enumerate(snapshots)
    ]
    report = run_transducer_lab(
        snapshots,
        seed_grids,
        profile,
        rng_seed=args.rng_seed,
        semantic_grids=semantic_grids,
    )
    write_lab_outputs(args.output_dir, report, snapshots, semantic_grids)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
