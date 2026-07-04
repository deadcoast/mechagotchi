import argparse
import json
import random
from pathlib import Path


from corpus_builder import PALETTES, build_seed_grids

# run_baseline is re-exported from grid_helpers: tests and callers use
# `from markov_grid import run_baseline` (identical to random_mutation's;
# constrained_generator's variant adds unique_signatures).
from grid_helpers import grid_from_matrix, run_baseline  # noqa: F401
from grid_helpers import weighted_sample as _sample
from validator import validate_grid  # noqa: F401  (kept for API compatibility)


ROOT = Path(__file__).resolve().parents[2]


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
    # This lab's fixed labels: source "markov_grid_lab" and the
    # "markov_local_generation" lineage event.
    return grid_from_matrix(
        grid_id,
        matrix,
        palette_id,
        source="markov_grid_lab",
        rng_seed=rng_seed,
        mutation_events=["markov_local_generation"],
    )


def _increment(counts: dict[str, int], token: str) -> None:
    counts[token] = counts.get(token, 0) + 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated-dir", type=Path, default=ROOT / "data/generated_grids/markov_local")
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
