import argparse
import json
import random
from pathlib import Path


from corpus_builder import PALETTES, build_seed_grids
from validator import validate_grid


START = "START"


def train_model(seed_grids: list[dict]) -> dict:
    transitions: dict[tuple[str, str], dict[str, int]] = {}
    global_counts: dict[str, int] = {}
    for grid in seed_grids:
        matrix = _matrix_from_grid(grid)
        for y, row in enumerate(matrix):
            for x, token in enumerate(row):
                left = row[x - 1] if x > 0 else START
                up = matrix[y - 1][x] if y > 0 else START
                _increment(transitions.setdefault((left, up), {}), token)
                _increment(global_counts, token)

    return {
        "width": 8,
        "height": 8,
        "transitions": transitions,
        "global_counts": global_counts,
        "global_total": sum(global_counts.values()),
    }


def generate_grid(model: dict, grid_id: str, rng_seed: int) -> dict:
    rng = random.Random(f"{rng_seed}:{grid_id}")
    matrix: list[list[str]] = []
    for y in range(model["height"]):
        row: list[str] = []
        for x in range(model["width"]):
            left = row[x - 1] if x > 0 else START
            up = matrix[y - 1][x] if y > 0 else START
            counts = model["transitions"].get((left, up), model["global_counts"])
            row.append(_sample(counts, rng))
        matrix.append(row)

    palette_id = rng.choice(sorted(PALETTES))
    return _grid_from_matrix(grid_id, matrix, palette_id, rng_seed)


def build_markov_corpus(
    seed_grids: list[dict], count: int = 100, rng_seed: int = 4242
) -> list[dict]:
    model = train_model(seed_grids)
    return [
        generate_grid(model, grid_id=f"mg_markov_{index:03d}", rng_seed=rng_seed)
        for index in range(count)
    ]


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


def write_markov_corpus(generated_dir: Path, generated_grids: list[dict]) -> None:
    generated_dir.mkdir(parents=True, exist_ok=True)
    for grid in generated_grids:
        path = generated_dir / f"{grid['grid_id']}.json"
        path.write_text(json.dumps(grid, indent=2) + "\n", encoding="utf-8")


def _matrix_from_grid(grid: dict) -> list[list[str]]:
    width, height = grid["grid_size"]
    matrix = [["." for _ in range(width)] for _ in range(height)]
    for cell in grid["cells"]:
        if cell["role"] == "body":
            matrix[cell["y"]][cell["x"]] = "A" if cell["animation_anchor"] else "B"
        elif cell["role"] == "eye":
            matrix[cell["y"]][cell["x"]] = "E"
        elif cell["role"] == "mouth":
            matrix[cell["y"]][cell["x"]] = "M"
    return matrix


def _grid_from_matrix(
    grid_id: str, matrix: list[list[str]], palette_id: str, rng_seed: int
) -> dict:
    palette = PALETTES[palette_id]
    cells: list[dict] = []
    core_cells: list[list[int]] = []
    sensor_cells: list[list[int]] = []
    expression_cells: list[list[int]] = []

    for y, row in enumerate(matrix):
        for x, token in enumerate(row):
            if token == ".":
                continue
            if token in {"B", "A"}:
                cells.append(
                    _cell(
                        x,
                        y,
                        visual=palette[1],
                        role="body",
                        material="hard",
                        organ="core",
                        animation_anchor=token == "A",
                    )
                )
                core_cells.append([x, y])
            elif token == "E":
                cells.append(
                    _cell(
                        x,
                        y,
                        visual=palette[2],
                        role="eye",
                        material="glass",
                        organ="sensors",
                    )
                )
                sensor_cells.append([x, y])
            elif token == "M":
                cells.append(
                    _cell(
                        x,
                        y,
                        visual=palette[2],
                        role="mouth",
                        material="soft",
                        organ="expression",
                    )
                )
                expression_cells.append([x, y])

    organs = {
        "core": {"role": "body_core", "cells": core_cells, "required": True},
        "sensors": {"role": "sensor", "cells": sensor_cells, "required": True},
    }
    if expression_cells:
        organs["expression"] = {
            "role": "expression",
            "cells": expression_cells,
            "required": False,
        }

    return {
        "grid_id": grid_id,
        "schema_version": "0.1.0",
        "parent_grid_id": None,
        "grid_size": [len(matrix[0]), len(matrix)],
        "cells": cells,
        "organs": organs,
        "palette": {
            "palette_id": palette_id,
            "colors": palette,
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
            "mutation_events": ["markov_local_generation"],
        },
        "metadata": {
            "source": "markov_grid_lab",
            "rng_seed": rng_seed,
        },
    }


def _cell(
    x: int,
    y: int,
    *,
    visual: str,
    role: str,
    material: str,
    organ: str,
    animation_anchor: bool = False,
) -> dict:
    return {
        "x": x,
        "y": y,
        "visual": visual,
        "role": role,
        "material": material,
        "mutation_weight": 0.1,
        "animation_anchor": animation_anchor,
        "organ": organ,
        "stress": 0,
        "damage": 0,
        "locked": False,
    }


def _increment(counts: dict[str, int], token: str) -> None:
    counts[token] = counts.get(token, 0) + 1


def _sample(counts: dict[str, int], rng: random.Random) -> str:
    total = sum(counts.values())
    pick = rng.randint(1, total)
    cursor = 0
    for token, count in sorted(counts.items()):
        cursor += count
        if pick <= cursor:
            return token
    raise RuntimeError("unreachable sample state")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated-dir", type=Path, default=Path("data/generated_grids/markov_local"))
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--rng-seed", type=int, default=4242)
    args = parser.parse_args()

    generated = build_markov_corpus(
        build_seed_grids(), count=args.count, rng_seed=args.rng_seed
    )
    write_markov_corpus(args.generated_dir, generated)
    print(json.dumps(run_baseline(generated), indent=2))


if __name__ == "__main__":
    main()
