import argparse
import json
import sys
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME = ROOT / "labs" / "grid_genome"
READABILITY = ROOT / "labs" / "readability_benchmark"
LIFECYCLE = ROOT / "labs" / "lifecycle_sim"
for path in [GRID_GENOME, READABILITY, LIFECYCLE]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from constrained_generator import build_constrained_corpus
from corpus_builder import build_seed_grids
from darwin_archive import build_map_elites_archive, descriptor_for_grid
from lifecycle_sim import run_lifecycle_simulation
from readability_benchmark import score_readability
from slip import is_grid_aligned
from validator import validate_grid


DESCRIPTOR_NAMES = [
    "body_mass",
    "sensor_count",
    "symmetry",
    "readability",
    "lifecycle_survival",
    "mutation_stability",
    "behavior_neediness",
]

DESCRIPTOR_CARDINALITIES = [5, 5, 5, 5, 5, 5, 5]

FITNESS_WEIGHTS = {
    "survival": 0.28,
    "readability": 0.24,
    "validity": 0.18,
    "bond": 0.12,
    "mutation_stability": 0.1,
    "slip_alignment": 0.08,
}


def extended_descriptor_for_grid(
    grid: dict,
    *,
    slip_profile: dict | None = None,
    lifecycle_ticks: int = 24,
    rng_seed: int = 20260512,
) -> dict:
    readability = score_readability(grid)
    lifecycle = _lifecycle_or_empty(
        grid, slip_profile=slip_profile, lifecycle_ticks=lifecycle_ticks, rng_seed=rng_seed
    )
    mutation_stability = _mutation_stability(grid)
    neediness = _behavior_neediness(grid, slip_profile)

    values = (
        _bin(_body_mass(grid), [6, 9, 12, 16]),
        _bin(_sensor_count(grid), [1, 2, 3, 4]),
        _bin(_symmetry_score(grid), [0.25, 0.5, 0.75, 0.9]),
        _bin(readability["proxy_readability_score"], [0.35, 0.55, 0.7, 0.85]),
        _bin(lifecycle["survival_ratio"], [0.2, 0.4, 0.6, 0.8]),
        _bin(mutation_stability, [0.3, 0.5, 0.7, 0.9]),
        _bin(neediness, [0.2, 0.4, 0.6, 0.8]),
    )
    return {
        "names": DESCRIPTOR_NAMES,
        "values": values,
        "key": _descriptor_key(values),
        "metrics": {
            "body_mass": _body_mass(grid),
            "sensor_count": _sensor_count(grid),
            "symmetry": round(_symmetry_score(grid), 6),
            "readability": readability["proxy_readability_score"],
            "lifecycle_survival": lifecycle["survival_ratio"],
            "mutation_stability": round(mutation_stability, 6),
            "behavior_neediness": round(neediness, 6),
        },
    }


def score_extended_candidate(
    grid: dict,
    *,
    slip_profile: dict | None = None,
    lifecycle_ticks: int = 24,
    rng_seed: int = 20260512,
) -> dict:
    validation = validate_grid(grid)
    readability = score_readability(grid)
    lifecycle = _lifecycle_or_empty(
        grid, slip_profile=slip_profile, lifecycle_ticks=lifecycle_ticks, rng_seed=rng_seed
    )
    mutation_stability = _mutation_stability(grid)
    slip_alignment = 1.0 if slip_profile is None or is_grid_aligned(grid, slip_profile).ok else 0.0
    bond = lifecycle["final_state"].get("bond", 0.0)

    components = {
        "survival": lifecycle["survival_ratio"],
        "readability": readability["proxy_readability_score"],
        "validity": 1.0 if validation.ok else 0.0,
        "bond": bond,
        "mutation_stability": mutation_stability,
        "slip_alignment": slip_alignment,
    }
    fitness = sum(components[name] * FITNESS_WEIGHTS[name] for name in FITNESS_WEIGHTS)
    return {
        "fitness": round(_clamp(fitness), 6),
        "components": {key: round(value, 6) for key, value in components.items()},
        "readability": readability,
        "lifecycle": lifecycle,
        "validation_errors": validation.errors,
    }


def build_extended_map_elites_archive(
    candidates: list[dict],
    *,
    slip_profile: dict | None = None,
    lifecycle_ticks: int = 24,
    rng_seed: int = 20260512,
) -> dict:
    elites: dict[str, dict] = {}
    observed_bins: dict[str, set[int]] = {name: set() for name in DESCRIPTOR_NAMES}
    for index, grid in enumerate(candidates):
        descriptor = extended_descriptor_for_grid(
            grid,
            slip_profile=slip_profile,
            lifecycle_ticks=lifecycle_ticks,
            rng_seed=rng_seed + index,
        )
        for name, value in zip(DESCRIPTOR_NAMES, descriptor["values"]):
            observed_bins[name].add(value)
        score = score_extended_candidate(
            grid,
            slip_profile=slip_profile,
            lifecycle_ticks=lifecycle_ticks,
            rng_seed=rng_seed + index,
        )
        current = elites.get(descriptor["key"])
        if current is None or score["fitness"] > current["fitness"]:
            elites[descriptor["key"]] = {
                "grid_id": grid["grid_id"],
                "fitness": score["fitness"],
                "descriptor": descriptor,
                "score_components": score["components"],
            }

    total_niches = _total_niches()
    qd_score = sum(elite["fitness"] for elite in elites.values())
    return {
        "archive_id": "map_elites_extended_stage0",
        "date": "2026-07-04",
        "descriptor_names": DESCRIPTOR_NAMES,
        "descriptor_dimensions": len(DESCRIPTOR_NAMES),
        "descriptor_cardinalities": DESCRIPTOR_CARDINALITIES,
        "total_possible_niches": total_niches,
        "occupied_niches": len(elites),
        "coverage": round(len(elites) / total_niches, 6),
        # Distinct bins observed per axis across all candidates. An axis with
        # spread 1 is degenerate for this run and inflates total_possible_niches
        # relative to what the candidate set can actually reach (H-03 guard).
        "descriptor_bin_spread": {
            name: len(observed_bins[name]) for name in DESCRIPTOR_NAMES
        },
        "best_fitness": max((elite["fitness"] for elite in elites.values()), default=0),
        "mean_elite_fitness": round(qd_score / len(elites), 6) if elites else 0,
        "qd_score": round(qd_score, 6),
        "elites": {key: elites[key] for key in sorted(elites)},
        "parameters": {
            "candidate_count": len(candidates),
            "lifecycle_ticks": lifecycle_ticks,
            "rng_seed": rng_seed,
        },
    }


def compare_extended_to_legacy(
    candidates: list[dict],
    *,
    slip_profile: dict | None = None,
    lifecycle_ticks: int = 24,
    rng_seed: int = 20260512,
) -> dict:
    legacy = build_map_elites_archive(candidates, slip=slip_profile)
    extended = build_extended_map_elites_archive(
        candidates,
        slip_profile=slip_profile,
        lifecycle_ticks=lifecycle_ticks,
        rng_seed=rng_seed,
    )
    legacy_niches = {descriptor_for_grid(grid) for grid in candidates}
    extended_niches = {
        tuple(
            extended_descriptor_for_grid(
                grid,
                slip_profile=slip_profile,
                lifecycle_ticks=lifecycle_ticks,
                rng_seed=rng_seed + index,
            )["values"]
        )
        for index, grid in enumerate(candidates)
    }
    return {
        "candidate_count": len(candidates),
        "legacy_descriptor_dimensions": 3,
        "extended_descriptor_dimensions": len(DESCRIPTOR_NAMES),
        "legacy_unique_candidate_niches": len(legacy_niches),
        "extended_unique_candidate_niches": len(extended_niches),
        "legacy_occupied_niches": legacy["occupied_niches"],
        "extended_occupied_niches": extended["occupied_niches"],
        "legacy_coverage": legacy["coverage"],
        "extended_coverage": extended["coverage"],
        "legacy_best_fitness": legacy["best_fitness"],
        "extended_best_fitness": extended["best_fitness"],
        "extended_qd_score": extended["qd_score"],
        "descriptor_expansion": len(DESCRIPTOR_NAMES) - 3,
    }


def write_extended_archive_artifacts(
    output_path: Path, archive: dict, comparison: dict
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "archive": archive,
        "comparison": comparison,
        "source_refs": [
            {
                "name": "Illuminating search spaces by mapping elites",
                "url": "https://arxiv.org/abs/1504.04909",
                "use": "Original MAP-Elites reference for behavior-space archives.",
            },
            {
                "name": "QDax MAP-Elites docs",
                "url": "https://qdax.readthedocs.io/en/develop/api_documentation/core/map_elites/",
                "use": "Implementation reference for repertoires, descriptors, and metrics.",
            },
        ],
        "decision": "prototype",
        "limitations": [
            "Lifecycle metrics use synthetic switchboard policy simulations.",
            "Readability is still proxy-scored until manual ratings are collected.",
            "Descriptor cardinalities are hand-set and need calibration.",
        ],
    }
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (output_path.parent / "README.md").write_text(
        "# Extended MAP-Elites Archive Stage 0\n\n"
        "Descriptor-expanded MAP-Elites artifact for the post-v0.1 research gate.\n\n"
        "Primary artifact:\n\n"
        "- `map_elites_extended_stage0.json`\n\n"
        "The archive keeps the original body mass, sensor count, and symmetry\n"
        "dimensions, then adds readability, lifecycle survival, mutation stability,\n"
        "and behavior neediness.\n",
        encoding="utf-8",
    )


def _lifecycle_or_empty(
    grid: dict,
    *,
    slip_profile: dict | None,
    lifecycle_ticks: int,
    rng_seed: int,
) -> dict:
    if not validate_grid(grid).ok:
        return {
            "survival_ratio": 0.0,
            "need_balance": 0.0,
            "recovery_events": 0,
            "final_state": {"bond": 0.0},
        }
    try:
        result = run_lifecycle_simulation(
            grid,
            slip_profile,
            ticks=lifecycle_ticks,
            policy="switchboard",
            rng_seed=rng_seed,
        )
    except ValueError:
        return {
            "survival_ratio": 0.0,
            "need_balance": 0.0,
            "recovery_events": 0,
            "final_state": {"bond": 0.0},
        }
    return {
        "survival_ratio": round(result["survival_ticks"] / lifecycle_ticks, 6)
        if lifecycle_ticks
        else 0.0,
        "need_balance": result["need_balance"],
        "recovery_events": result["recovery_events"],
        "final_state": result["final_state"],
    }


def _body_mass(grid: dict) -> int:
    return sum(1 for cell in grid.get("cells", []) if cell.get("organ") == "core")


def _sensor_count(grid: dict) -> int:
    return len(grid.get("organs", {}).get("sensors", {}).get("cells", []))


def _symmetry_score(grid: dict) -> float:
    width = grid.get("grid_size", [0, 0])[0]
    occupied = {(cell["x"], cell["y"], cell["role"]) for cell in grid.get("cells", [])}
    if not occupied:
        return 0.0
    mirrored = 0
    for x, y, role in occupied:
        if (width - 1 - x, y, role) in occupied:
            mirrored += 1
    return mirrored / len(occupied)


def _mutation_stability(grid: dict) -> float:
    mutation = grid.get("mutation", {})
    values = [
        mutation.get("cell_mutation_rate", 1.0),
        mutation.get("organ_shift_rate", 1.0),
        mutation.get("palette_shift_rate", 1.0),
        mutation.get("symmetry_break_rate", 1.0),
    ]
    mean_rate = mean(float(value) for value in values)
    return _clamp(1.0 - mean_rate)


def _behavior_neediness(grid: dict, slip_profile: dict | None) -> float:
    # Descriptor axes must vary per candidate: a SLIP profile is constant for
    # an archive run, so using its neediness directly collapsed this axis to a
    # single bin (review finding H-03). The grid-derived term carries the
    # per-candidate signal; the profile neediness acts as a prior shift only.
    body_mass = _body_mass(grid)
    sensor_count = _sensor_count(grid)
    grid_term = 0.35 + sensor_count * 0.08 - body_mass * 0.01
    if slip_profile is not None:
        behavior = slip_profile.get("behavior", {})
        if "neediness" in behavior:
            return _clamp(grid_term + (_clamp(behavior["neediness"]) - 0.5) * 0.2)
    return _clamp(grid_term)


def _bin(value: float, thresholds: list[float]) -> int:
    for index, threshold in enumerate(thresholds):
        if value <= threshold:
            return index
    return len(thresholds)


def _descriptor_key(descriptor: tuple[int, ...]) -> str:
    return ",".join(str(value) for value in descriptor)


def _total_niches() -> int:
    total = 1
    for cardinality in DESCRIPTOR_CARDINALITIES:
        total *= cardinality
    return total


def _load_default_slip() -> dict:
    return json.loads(
        (ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )


def _clamp(value: object) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0.0
    return max(0.0, min(1.0, number))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/archives/map_elites_extended_stage0.json"))
    parser.add_argument("--count", type=int, default=160)
    parser.add_argument("--rng-seed", type=int, default=20260512)
    parser.add_argument("--lifecycle-ticks", type=int, default=24)
    args = parser.parse_args()

    slip_profile = _load_default_slip()
    candidates = build_constrained_corpus(
        build_seed_grids(),
        count=args.count,
        rng_seed=args.rng_seed,
        slip=slip_profile,
    )
    archive = build_extended_map_elites_archive(
        candidates,
        slip_profile=slip_profile,
        lifecycle_ticks=args.lifecycle_ticks,
        rng_seed=args.rng_seed,
    )
    comparison = compare_extended_to_legacy(
        candidates,
        slip_profile=slip_profile,
        lifecycle_ticks=args.lifecycle_ticks,
        rng_seed=args.rng_seed,
    )
    write_extended_archive_artifacts(args.output, archive, comparison)
    print(json.dumps({"archive": {k: v for k, v in archive.items() if k != "elites"}, "comparison": comparison}, indent=2))


if __name__ == "__main__":
    main()
