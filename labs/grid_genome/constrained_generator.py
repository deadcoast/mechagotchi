import argparse
import json
import random
from copy import deepcopy
from pathlib import Path

from corpus_builder import PALETTES, build_seed_grids
from grid_helpers import grid_from_matrix
from grid_helpers import grid_signature as _signature
from grid_helpers import run_baseline as _run_baseline
from grid_helpers import weighted_sample as _weighted_sample
from markov_grid import _matrix_from_grid
from slip import is_grid_aligned, validate_slip
from validator import validate_grid


ROOT = Path(__file__).resolve().parents[2]


TOKENS = [".", "B", "A", "E", "M"]

# Per-rate ceilings for the deterministic mutation-rate jitter (review
# finding L-12). When no SLIP profile is supplied the ceilings are the fixed
# default vector grid_from_matrix emits, so jittered rates never exceed the
# historical defaults; with a SLIP profile the ceilings are the profile's
# *_max caps, so jittered grids always stay is_grid_aligned.
DEFAULT_MUTATION_RATE_CAPS = {
    "cell_mutation_rate": 0.05,
    "organ_shift_rate": 0.02,
    "palette_shift_rate": 0.01,
    "symmetry_break_rate": 0.01,
}

SLIP_MUTATION_CAP_KEYS = {
    "cell_mutation_rate": "cell_mutation_rate_max",
    "organ_shift_rate": "organ_shift_rate_max",
    "palette_shift_rate": "palette_shift_rate_max",
    "symmetry_break_rate": "symmetry_break_rate_max",
}


def train_constraints(seed_grids: list[dict]) -> dict:
    # DR 0029 / cycle 09 A3: dimensions derive from the corpus (an 8x8
    # corpus trains the identical historical model); mixed sizes fail
    # loudly instead of silently training wrong-position statistics.
    sizes = {tuple(grid["grid_size"]) for grid in seed_grids}
    if len(sizes) != 1:
        raise ValueError(
            "seed corpus must share a single grid size, found: "
            + ", ".join(f"{w}x{h}" for w, h in sorted(sizes))
        )
    ((width, height),) = sizes

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
        "width": width,
        "height": height,
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
    variant = _ensure_semantic_variation(safe_variant, rng)
    _apply_mutation_temperature(variant, grid_id, rng_seed, slip)
    return variant


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
    # Divergence from markov_grid/random_mutation run_baseline: this lab's
    # report also counts unique cell signatures (diversity metric).
    return _run_baseline(generated_grids, signature=_signature)


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


def _grid_from_matrix(
    grid_id: str,
    matrix: list[list[str]],
    palette_id: str,
    rng_seed: int,
    mutation_events: list[str],
    parent_grid_id: str | None = None,
) -> dict:
    # This lab's fixed label: source "constrained_wfc_style_lab"; lineage
    # events and parent linkage vary per call (unlike markov_grid's).
    return grid_from_matrix(
        grid_id,
        matrix,
        palette_id,
        source="constrained_wfc_style_lab",
        rng_seed=rng_seed,
        mutation_events=mutation_events,
        parent_grid_id=parent_grid_id,
    )


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


def _apply_mutation_temperature(
    grid: dict, grid_id: str, rng_seed: int, slip: dict | None
) -> None:
    """Deterministically vary the candidate's mutation vector (finding L-12).

    Every candidate previously inherited grid_from_matrix's fixed rate vector
    (0.05/0.02/0.01/0.01), which collapsed the extended archive's
    mutation_stability descriptor axis to a single bin. Each candidate now
    draws a "mutation temperature" in [0.05, 1.0) from its own dedicated rng
    stream (separate from the structural stream, so cell layouts are
    byte-identical to the pre-jitter generator) and scales every rate ceiling
    by it:

        rate = round(cap * temperature, 6)

    Determinism: the stream is seeded with f"{rng_seed}:{grid_id}:mutation",
    so the same seed always reproduces the same vector. Safety: rates stay in
    (0, cap], so validate_grid (rates in [0, 1]) and is_grid_aligned (rates
    <= the profile's *_max caps) both keep passing.
    """
    rng = random.Random(f"{rng_seed}:{grid_id}:mutation")
    temperature = 0.05 + 0.95 * rng.random()
    caps = DEFAULT_MUTATION_RATE_CAPS
    if slip is not None:
        caps = {
            rate_key: float(slip["mutation"][cap_key])
            for rate_key, cap_key in SLIP_MUTATION_CAP_KEYS.items()
        }
    grid["mutation"] = {
        rate_key: round(cap * temperature, 6) for rate_key, cap in caps.items()
    }


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated-dir", type=Path, default=ROOT / "data/generated_grids/constrained_wfc_style")
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
