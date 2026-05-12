import argparse
import json
import random
from copy import deepcopy
from pathlib import Path

from corpus_builder import PALETTES, build_seed_grids
from markov_grid import _matrix_from_grid
from slip import is_grid_aligned, validate_slip
from validator import validate_grid


TOKENS = [".", "B", "A", "E", "M"]


def train_constraints(seed_grids: list[dict]) -> dict:
    adjacency = {"right": {}, "down": {}}
    token_counts = {token: 0 for token in TOKENS}
    total_pairs = 0
    for grid in seed_grids:
        matrix = _matrix_from_grid(grid)
        for y, row in enumerate(matrix):
            for x, token in enumerate(row):
                token_counts[token] = token_counts.get(token, 0) + 1
                if x + 1 < len(row):
                    _add_pair(adjacency["right"], token, row[x + 1])
                    total_pairs += 1
                if y + 1 < len(matrix):
                    _add_pair(adjacency["down"], token, matrix[y + 1][x])
                    total_pairs += 1

    return {
        "width": 8,
        "height": 8,
        "adjacency": adjacency,
        "token_counts": token_counts,
        "total_pairs": total_pairs,
    }


def generate_constrained_grid(
    model: dict,
    seed_grids: list[dict],
    grid_id: str,
    rng_seed: int,
    slip: dict | None = None,
) -> dict:
    rng = random.Random(f"{rng_seed}:{grid_id}")
    parent_pool = _filter_seed_pool(seed_grids, slip)
    parent = deepcopy(rng.choice(parent_pool))
    parent_grid_id = parent["grid_id"]
    parent["grid_id"] = grid_id
    parent["parent_grid_id"] = parent_grid_id
    parent.setdefault("metadata", {})["source"] = "constrained_wfc_style_lab"
    parent["metadata"]["rng_seed"] = rng_seed
    parent["lineage"]["mutation_events"] = ["seed_parent_selected"]
    parent["lineage"]["generation"] = parent.get("lineage", {}).get("generation", 0) + 1
    parent["lineage"]["ancestor_ids"] = [parent_grid_id]

    matrix = _matrix_from_grid(parent)
    for _ in range(12):
        proposal = deepcopy(matrix)
        _attempt_local_resample(proposal, model, rng)
        candidate = _grid_from_matrix(
            grid_id,
            proposal,
            _choose_palette(rng, slip),
            rng_seed,
            mutation_events=["seed_parent_selected", "validator_gated_resample"],
            parent_grid_id=parent_grid_id,
        )
        if _acceptable(candidate, slip):
            matrix = proposal

    safe_variant = _grid_from_matrix(
        grid_id,
        matrix,
        _choose_palette(rng, slip),
        rng_seed,
        mutation_events=["seed_parent_selected", "validator_gated_resample"],
        parent_grid_id=parent_grid_id,
    )
    return _ensure_semantic_variation(safe_variant, rng)


def build_constrained_corpus(
    seed_grids: list[dict],
    count: int = 100,
    rng_seed: int = 77,
    slip: dict | None = None,
) -> list[dict]:
    model = train_constraints(seed_grids)
    return [
        generate_constrained_grid(
            model,
            seed_grids,
            grid_id=f"mg_constrained_{index:03d}",
            rng_seed=rng_seed,
            slip=slip,
        )
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
        "unique_signatures": len({_signature(grid) for grid in generated_grids}),
        "error_counts": dict(sorted(error_counts.items())),
    }


def write_constrained_corpus(generated_dir: Path, generated_grids: list[dict]) -> None:
    generated_dir.mkdir(parents=True, exist_ok=True)
    for grid in generated_grids:
        path = generated_dir / f"{grid['grid_id']}.json"
        path.write_text(json.dumps(grid, indent=2) + "\n", encoding="utf-8")


def _add_pair(adjacency: dict[str, dict[str, int]], left: str, right: str) -> None:
    counts = adjacency.setdefault(left, {})
    counts[right] = counts.get(right, 0) + 1


def _attempt_local_resample(
    matrix: list[list[str]], model: dict, rng: random.Random
) -> None:
    x = rng.randrange(model["width"])
    y = rng.randrange(model["height"])
    candidates = _candidate_tokens(matrix, model, x, y)
    if not candidates:
        return
    matrix[y][x] = _weighted_sample(candidates, rng)


def _candidate_tokens(
    matrix: list[list[str]], model: dict, x: int, y: int
) -> dict[str, int]:
    candidates = dict(model["token_counts"])
    for token in list(candidates):
        if not _allowed_at(matrix, model, x, y, token):
            del candidates[token]
    return candidates


def _allowed_at(matrix: list[list[str]], model: dict, x: int, y: int, token: str) -> bool:
    adjacency = model["adjacency"]
    width = model["width"]
    height = model["height"]
    if x > 0 and token not in adjacency["right"].get(matrix[y][x - 1], {}):
        return False
    if x + 1 < width and matrix[y][x + 1] not in adjacency["right"].get(token, {}):
        return False
    if y > 0 and token not in adjacency["down"].get(matrix[y - 1][x], {}):
        return False
    if y + 1 < height and matrix[y + 1][x] not in adjacency["down"].get(token, {}):
        return False
    return True


def _weighted_sample(counts: dict[str, int], rng: random.Random) -> str:
    total = sum(counts.values())
    pick = rng.randint(1, total)
    cursor = 0
    for token, count in sorted(counts.items()):
        cursor += count
        if pick <= cursor:
            return token
    raise RuntimeError("unreachable sample state")


def _grid_from_matrix(
    grid_id: str,
    matrix: list[list[str]],
    palette_id: str,
    rng_seed: int,
    mutation_events: list[str],
    parent_grid_id: str | None = None,
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
        "parent_grid_id": parent_grid_id,
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
            "generation": 1 if parent_grid_id else 0,
            "ancestor_ids": [parent_grid_id] if parent_grid_id else [],
            "mutation_events": mutation_events,
        },
        "metadata": {
            "source": "constrained_wfc_style_lab",
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


def _filter_seed_pool(seed_grids: list[dict], slip: dict | None) -> list[dict]:
    if slip is None:
        return seed_grids
    result = validate_slip(slip)
    if not result.ok:
        raise ValueError("; ".join(result.errors))
    aligned = [grid for grid in seed_grids if is_grid_aligned(grid, slip).ok]
    if not aligned:
        raise ValueError("no seed grids satisfy SLIP constraints")
    return aligned


def _choose_palette(rng: random.Random, slip: dict | None) -> str:
    if slip is None:
        return rng.choice(sorted(PALETTES))
    return rng.choice(sorted(slip["grid"]["allowed_palettes"]))


def _acceptable(grid: dict, slip: dict | None) -> bool:
    if not validate_grid(grid).ok:
        return False
    return slip is None or is_grid_aligned(grid, slip).ok


def _ensure_semantic_variation(grid: dict, rng: random.Random) -> dict:
    variant = deepcopy(grid)
    core_cells = [
        cell for cell in variant["cells"] if cell.get("organ") == "core"
    ]
    if core_cells:
        for cell in core_cells:
            cell["animation_anchor"] = False
        rng.choice(core_cells)["animation_anchor"] = True
        if "anchor_repositioned" not in variant["lineage"]["mutation_events"]:
            variant["lineage"]["mutation_events"].append("anchor_repositioned")
    return variant if validate_grid(variant).ok else grid


def _signature(grid: dict) -> str:
    return "|".join(
        f"{cell['x']},{cell['y']}:{cell['role']}:{int(cell['animation_anchor'])}"
        for cell in sorted(grid["cells"], key=lambda item: (item["y"], item["x"], item["role"]))
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated-dir", type=Path, default=Path("data/generated_grids/constrained_wfc_style"))
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--rng-seed", type=int, default=77)
    parser.add_argument("--slip", type=Path)
    args = parser.parse_args()

    slip = None
    if args.slip:
        slip = json.loads(args.slip.read_text(encoding="utf-8"))
    generated = build_constrained_corpus(
        build_seed_grids(), count=args.count, rng_seed=args.rng_seed, slip=slip
    )
    write_constrained_corpus(args.generated_dir, generated)
    print(json.dumps(run_baseline(generated), indent=2))


if __name__ == "__main__":
    main()
