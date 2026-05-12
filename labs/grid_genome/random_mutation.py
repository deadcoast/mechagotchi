import argparse
import json
import random
from copy import deepcopy
from pathlib import Path


from corpus_builder import build_seed_grids
from validator import validate_grid


def mutate_grid(parent: dict, mutation_index: int, rng_seed: int) -> dict:
    rng = random.Random(f"{rng_seed}:{parent['grid_id']}:{mutation_index}")
    child = deepcopy(parent)
    child["grid_id"] = f"{parent['grid_id']}_rm_{mutation_index:03d}"
    child["parent_grid_id"] = parent["grid_id"]
    child["lineage"]["generation"] = parent.get("lineage", {}).get("generation", 0) + 1
    child["lineage"]["ancestor_ids"] = [parent["grid_id"]]
    child["lineage"]["mutation_events"] = []
    child["metadata"] = {
        **child.get("metadata", {}),
        "source": "random_mutation_baseline",
        "rng_seed": rng_seed,
        "mutation_index": mutation_index,
    }

    operation = rng.choice(
        [
            _shift_cell_without_organ_update,
            _remove_animation_anchor,
            _add_body_cell,
            _mutate_rate,
            _remove_sensor_cell,
            _palette_shift,
        ]
    )
    operation(child, rng)
    return child


def run_baseline(generated_grids: list[dict]) -> dict:
    error_counts: dict[str, int] = {}
    valid_count = 0
    for grid in generated_grids:
        result = validate_grid(grid)
        if result.ok:
            valid_count += 1
        for error in result.errors:
            error_counts[error] = error_counts.get(error, 0) + 1

    candidate_count = len(generated_grids)
    invalid_count = candidate_count - valid_count
    return {
        "candidate_count": candidate_count,
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "validity_rate": valid_count / candidate_count if candidate_count else 0,
        "error_counts": dict(sorted(error_counts.items())),
    }


def build_generated_corpus(
    seed_grids: list[dict], per_seed: int = 2, rng_seed: int = 90210
) -> list[dict]:
    generated = []
    mutation_index = 0
    for parent in seed_grids:
        for _ in range(per_seed):
            generated.append(mutate_grid(parent, mutation_index, rng_seed))
            mutation_index += 1
    return generated


def write_generated_corpus(generated_dir: Path, generated_grids: list[dict]) -> None:
    generated_dir.mkdir(parents=True, exist_ok=True)
    for grid in generated_grids:
        path = generated_dir / f"{grid['grid_id']}.json"
        path.write_text(json.dumps(grid, indent=2) + "\n", encoding="utf-8")


def _shift_cell_without_organ_update(grid: dict, rng: random.Random) -> None:
    cell = rng.choice(grid["cells"])
    dx, dy = rng.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
    cell["x"] += dx
    cell["y"] += dy
    grid["lineage"]["mutation_events"].append("shift_cell_without_organ_update")


def _remove_animation_anchor(grid: dict, rng: random.Random) -> None:
    for cell in grid["cells"]:
        cell["animation_anchor"] = False
    grid["lineage"]["mutation_events"].append("remove_animation_anchor")


def _add_body_cell(grid: dict, rng: random.Random) -> None:
    width, height = grid["grid_size"]
    occupied = {(cell["x"], cell["y"]) for cell in grid["cells"]}
    core = [cell for cell in grid["cells"] if cell.get("organ") == "core"]
    rng.shuffle(core)
    for source in core:
        candidates = [
            (source["x"] - 1, source["y"]),
            (source["x"] + 1, source["y"]),
            (source["x"], source["y"] - 1),
            (source["x"], source["y"] + 1),
        ]
        rng.shuffle(candidates)
        for x, y in candidates:
            if 0 <= x < width and 0 <= y < height and (x, y) not in occupied:
                grid["cells"].append(
                    {
                        "x": x,
                        "y": y,
                        "visual": grid["palette"]["colors"][1],
                        "role": "body",
                        "material": "hard",
                        "mutation_weight": 0.15,
                        "animation_anchor": False,
                        "organ": "core",
                        "stress": 0,
                        "damage": 0,
                        "locked": False,
                    }
                )
                grid["organs"]["core"]["cells"].append([x, y])
                grid["lineage"]["mutation_events"].append("add_body_cell")
                return
    grid["lineage"]["mutation_events"].append("add_body_cell_noop")


def _mutate_rate(grid: dict, rng: random.Random) -> None:
    key = rng.choice(
        [
            "cell_mutation_rate",
            "organ_shift_rate",
            "palette_shift_rate",
            "symmetry_break_rate",
        ]
    )
    grid["mutation"][key] = rng.choice([-0.1, 0.0, 0.25, 1.2])
    grid["lineage"]["mutation_events"].append(f"mutate_rate:{key}")


def _remove_sensor_cell(grid: dict, rng: random.Random) -> None:
    sensor_points = {
        tuple(point) for point in grid.get("organs", {}).get("sensors", {}).get("cells", [])
    }
    grid["cells"] = [
        cell for cell in grid["cells"] if (cell["x"], cell["y"]) not in sensor_points
    ]
    grid["lineage"]["mutation_events"].append("remove_sensor_cell")


def _palette_shift(grid: dict, rng: random.Random) -> None:
    colors = grid["palette"]["colors"]
    if len(colors) > 2:
        colors[1], colors[2] = colors[2], colors[1]
    grid["lineage"]["mutation_events"].append("palette_shift")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated-dir", type=Path, default=Path("data/generated_grids/random_mutation_baseline"))
    parser.add_argument("--per-seed", type=int, default=2)
    parser.add_argument("--rng-seed", type=int, default=90210)
    args = parser.parse_args()

    generated = build_generated_corpus(
        build_seed_grids(), per_seed=args.per_seed, rng_seed=args.rng_seed
    )
    write_generated_corpus(args.generated_dir, generated)
    print(json.dumps(run_baseline(generated), indent=2))


if __name__ == "__main__":
    main()
