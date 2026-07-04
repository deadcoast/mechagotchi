import argparse
import json
from pathlib import Path


from constrained_generator import build_constrained_corpus
from corpus_builder import build_seed_grids
from slip import is_grid_aligned
from validator import validate_grid


ROOT = Path(__file__).resolve().parents[2]


def descriptor_for_grid(grid: dict) -> tuple[int, int, int]:
    body_mass = _body_mass(grid)
    sensor_count = _sensor_count(grid)
    symmetry = _symmetry_score(grid)
    return (
        _bin(body_mass, [6, 9, 12, 16]),
        _bin(sensor_count, [1, 2, 3, 4]),
        _bin(symmetry, [0.25, 0.5, 0.75, 0.9]),
    )


def score_grid(grid: dict, slip: dict | None = None) -> float:
    validation = 1.0 if validate_grid(grid).ok else 0.0
    body_mass = _body_mass(grid)
    mass_score = _triangular_score(body_mass, ideal=10, span=12)
    sensor_score = min(_sensor_count(grid), 4) / 4
    symmetry_score = _symmetry_score(grid)
    anchor_score = 1.0 if any(cell.get("animation_anchor") for cell in grid["cells"]) else 0.0
    slip_score = 1.0 if slip is None or is_grid_aligned(grid, slip).ok else 0.0
    fitness = (
        validation * 0.35
        + mass_score * 0.2
        + sensor_score * 0.15
        + symmetry_score * 0.15
        + anchor_score * 0.1
        + slip_score * 0.05
    )
    return round(max(0.0, min(1.0, fitness)), 6)


def build_map_elites_archive(candidates: list[dict], slip: dict | None = None) -> dict:
    elites: dict[str, dict] = {}
    for grid in candidates:
        descriptor = descriptor_for_grid(grid)
        descriptor_key = _descriptor_key(descriptor)
        fitness = score_grid(grid, slip=slip)
        current = elites.get(descriptor_key)
        if current is None or fitness > current["fitness"]:
            elites[descriptor_key] = {
                "grid_id": grid["grid_id"],
                "fitness": fitness,
                "descriptor": descriptor,
                "body_mass": _body_mass(grid),
                "sensor_count": _sensor_count(grid),
                "symmetry": round(_symmetry_score(grid), 6),
            }
    return {
        "elites": elites,
        "occupied_niches": len(elites),
        "coverage": len(elites) / 125,
        "best_fitness": max((elite["fitness"] for elite in elites.values()), default=0),
        "mean_elite_fitness": round(
            sum(elite["fitness"] for elite in elites.values()) / len(elites), 6
        )
        if elites
        else 0,
    }


def compare_with_scalar_baseline(
    candidates: list[dict], top_k: int, slip: dict | None = None
) -> dict:
    archive = build_map_elites_archive(candidates, slip=slip)
    scalar_top = sorted(
        candidates, key=lambda grid: score_grid(grid, slip=slip), reverse=True
    )[:top_k]
    scalar_niches = {descriptor_for_grid(grid) for grid in scalar_top}
    return {
        "candidate_count": len(candidates),
        "top_k": top_k,
        "map_elites_occupied_niches": archive["occupied_niches"],
        "map_elites_coverage": archive["coverage"],
        "map_elites_best_fitness": archive["best_fitness"],
        "map_elites_mean_elite_fitness": archive["mean_elite_fitness"],
        "scalar_top_occupied_niches": len(scalar_niches),
        "scalar_top_coverage": len(scalar_niches) / 125,
        "scalar_top_best_fitness": score_grid(scalar_top[0], slip=slip)
        if scalar_top
        else 0,
    }


def archive_to_jsonable(archive: dict) -> dict:
    return {
        **archive,
        "elites": {key: value for key, value in sorted(archive["elites"].items())},
    }


def write_archive(path: Path, archive: dict, comparison: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "archive": archive_to_jsonable(archive),
        "comparison": comparison,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


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


def _triangular_score(value: int, *, ideal: int, span: int) -> float:
    return max(0.0, 1.0 - abs(value - ideal) / span)


def _bin(value: float, thresholds: list[float]) -> int:
    for index, threshold in enumerate(thresholds):
        if value <= threshold:
            return index
    return len(thresholds)


def _descriptor_key(descriptor: tuple[int, int, int]) -> str:
    return ",".join(str(value) for value in descriptor)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=200)
    parser.add_argument("--rng-seed", type=int, default=818)
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--output", type=Path, default=ROOT / "data/archives/map_elites_stage0.json")
    args = parser.parse_args()

    candidates = build_constrained_corpus(
        build_seed_grids(), count=args.count, rng_seed=args.rng_seed
    )
    archive = build_map_elites_archive(candidates)
    comparison = compare_with_scalar_baseline(candidates, top_k=args.top_k)
    write_archive(args.output, archive, comparison)
    print(json.dumps({"archive": archive_to_jsonable(archive), "comparison": comparison}, indent=2))


if __name__ == "__main__":
    main()
