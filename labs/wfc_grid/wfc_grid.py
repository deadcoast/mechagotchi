"""The WFC/constraint generator lab (cycle 10 B1, gap-analysis Phase B).

The documented generation architecture is Markov -> WFC/constraints ->
mutation -> validator -> MAP-Elites, but no WFC lab ever existed — the
historical bake-off ran without the documented field, and Phase A left a
named remainder: the generation alphabet was {., B, A, E, M}, so children
of rich 16x16 parents lost their shells, limbs, and antennae. This lab is
the constraint layer over the FULL DR 0015 alphabet.

The model is corpus-learned, twice over:

- **Position candidates**: the tokens observed at each (x, y) across the
  training grids, with counts (creatures live in the canvas middle; the
  overlapping-WFC "position channel" flavor).
- **Adjacency**: observed right/down token pairs (applied symmetrically
  during propagation).

Generation is classic wave collapse, deterministic under a seed:
lowest-entropy cell first ((y, x) tie-break), frequency-weighted token
choice, arc-consistent constraint propagation, and bounded restarts on
contradiction (the RNG stream continues across restarts, so the same
seed always reproduces the same creature). A semantic finishing pass
normalizes the animation anchor exactly the way the promoted generator
does (every A becomes body, one core cell is re-anointed via the RNG).
No validator-gated resampling happens inside this arm — that trick
belongs to the constrained-stabilizer arm, and keeping the arms distinct
is what makes the bake-off (B2) meaningful.

The dossier's 72/24/24 corpus protocol is adapted to the real corpus:
30/10/10, stratified six/two/two per palette — recorded as a protocol
decision in the cycle plan.
"""

import argparse
import json
import random
import sys
from collections import deque
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME = ROOT / "labs" / "grid_genome"
if str(GRID_GENOME) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME))

from grid_helpers import (  # noqa: E402
    PALETTES,
    RICH_TOKENS,
    grid_from_rich_matrix,
    run_baseline,
    weighted_sample,
)
from validator import validate_grid  # noqa: E402


REPORT_DATE = "2026-07-08"
ARTIFACT_ID = "wfc_grid_stage0"
MAX_RESTARTS = 8

# Inverse of the rich alphabet: cell role -> token. "A" is reachable only
# through the anchor flag ("body" maps to "B"); the vocab lab's dedicated
# "anchor" role also reads as "A" for robustness.
TOKEN_FOR_ROLE = {
    role: token
    for token, (role, _material, _organ, _index) in RICH_TOKENS.items()
    if token != "A"
}
TOKEN_FOR_ROLE["anchor"] = "A"

_DIRECTIONS = {
    "right": (1, 0),
    "left": (-1, 0),
    "down": (0, 1),
    "up": (0, -1),
}


def rich_matrix_from_grid(grid: dict) -> list[list[str]]:
    """Project a grid onto the rich token matrix (the full vocabulary)."""
    width, height = grid["grid_size"]
    matrix = [["." for _ in range(width)] for _ in range(height)]
    for cell in grid.get("cells", []):
        x, y = cell.get("x"), cell.get("y")
        if not isinstance(x, int) or not isinstance(y, int):
            continue
        if not (0 <= x < width and 0 <= y < height):
            continue
        if cell.get("animation_anchor") is True:
            matrix[y][x] = "A"
        else:
            matrix[y][x] = TOKEN_FOR_ROLE.get(cell.get("role"), "B")
    return matrix


def split_corpus(
    seeds: list[dict],
) -> tuple[list[dict], list[dict], list[dict]]:
    """The dossier's 72/24/24 adapted to the real corpus: 30/10/10,
    stratified six/two/two per palette, deterministic by grid_id."""
    by_palette: dict[str, list[dict]] = {}
    for grid in seeds:
        by_palette.setdefault(grid["palette"]["palette_id"], []).append(grid)
    train: list[dict] = []
    dev: list[dict] = []
    holdout: list[dict] = []
    for palette in sorted(by_palette):
        bucket = sorted(by_palette[palette], key=lambda grid: grid["grid_id"])
        train.extend(bucket[:6])
        dev.extend(bucket[6:8])
        holdout.extend(bucket[8:10])
    return train, dev, holdout


def train_wfc_model(train_grids: list[dict]) -> dict:
    if not train_grids:
        raise ValueError("train_grids must not be empty")
    sizes = {tuple(grid.get("grid_size", [8, 8])) for grid in train_grids}
    if len(sizes) != 1:
        raise ValueError(
            "training corpus must share a single grid size, found: "
            + ", ".join(f"{w}x{h}" for w, h in sorted(sizes))
        )
    ((width, height),) = sizes

    position_candidates: dict[str, dict[str, int]] = {
        f"{x},{y}": {} for y in range(height) for x in range(width)
    }
    adjacency: dict[str, dict[str, dict[str, int]]] = {"right": {}, "down": {}}
    total_pairs = 0
    for grid in train_grids:
        matrix = rich_matrix_from_grid(grid)
        for y, row in enumerate(matrix):
            for x, token in enumerate(row):
                counts = position_candidates[f"{x},{y}"]
                counts[token] = counts.get(token, 0) + 1
                if x + 1 < width:
                    _count_pair(adjacency["right"], token, row[x + 1])
                    total_pairs += 1
                if y + 1 < height:
                    _count_pair(adjacency["down"], token, matrix[y + 1][x])
                    total_pairs += 1

    return {
        "width": width,
        "height": height,
        "position_candidates": position_candidates,
        "adjacency": adjacency,
        "total_pairs": total_pairs,
        "training_grid_ids": [grid["grid_id"] for grid in train_grids],
    }


def generate_wfc_grid(
    model: dict,
    *,
    grid_id: str,
    rng_seed: int,
    max_restarts: int = MAX_RESTARTS,
    trace: list[dict] | None = None,
) -> dict:
    """Collapse one creature; deterministic per (grid_id, rng_seed).

    Optional trace receives detached JSON observations, including failed
    attempts. It consumes no randomness and never changes returned metadata.
    Errors still raise with their original type/message; prior observations
    remain available. Each call appends a wfc_trace_v1 generation boundary.
    """
    rng = random.Random(f"{rng_seed}:{grid_id}")
    last_error: str | None = None
    attempts_run = 0
    _trace_event(trace, 'generation_started', trace_format='wfc_trace_v1',
                 grid_id=grid_id, rng_seed=rng_seed, max_restarts=max_restarts)
    for attempt in range(max_restarts):
        attempts_run = attempt + 1
        _trace_event(trace, 'attempt_started', attempt=attempt + 1)
        matrix = _collapse(model, rng, trace=trace)
        if matrix is None:
            last_error = "wave contradiction"
            _trace_event(trace, 'attempt_rejected', attempt=attempt + 1, reason=last_error)
            continue
        matrix, finish_error = _finish(matrix, rng, trace=trace)
        if matrix is None:
            last_error = finish_error
            _trace_event(trace, 'attempt_rejected', attempt=attempt + 1, reason=last_error)
            continue
        palette_id = rng.choice(sorted(PALETTES))
        _trace_event(trace, 'palette_selected', palette_id=palette_id)
        grid = grid_from_rich_matrix(
            grid_id,
            ["".join(row) for row in matrix],
            palette_id,
            size=model["width"],
            source="wfc_grid_lab",
            mutation_events=["wfc_wave_collapsed"],
        )
        _trace_event(trace, 'generated', attempt=attempt + 1, grid_id=grid_id)
        return grid
    _trace_event(trace, 'exhausted', attempts=attempts_run, max_restarts=max_restarts, reason=last_error)
    raise ValueError(
        f"WFC could not collapse {grid_id} (rng_seed {rng_seed}) in "
        f"{max_restarts} attempts: {last_error}"
    )


def build_wfc_corpus(model: dict, *, count: int, rng_seed: int) -> list[dict]:
    return [
        generate_wfc_grid(
            model, grid_id=f"mg_wfc_{index:03d}", rng_seed=rng_seed
        )
        for index in range(count)
    ]


def build_wfc_report() -> dict:
    from corpus_builder import build_seed_grids_16

    train, dev, holdout = split_corpus(build_seed_grids_16())
    model = train_wfc_model(train)
    corpus = build_wfc_corpus(model, count=50, rng_seed=1030)
    baseline = run_baseline(corpus, signature=_signature)

    roles = {cell["role"] for grid in corpus for cell in grid["cells"]}
    rich_roles = sorted(roles - {"body", "eye", "mouth"})
    train_signatures = {_signature(grid) for grid in train}
    copies = sum(
        1 for grid in corpus if _signature(grid) in train_signatures
    )
    core_masses = sorted(_core_mass(grid) for grid in corpus)

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete",
        "date": REPORT_DATE,
        "purpose": (
            "Establish the documented WFC/constraint generator lab over the "
            "full DR 0015 alphabet (gap-analysis Phase B: no WFC lab ever "
            "existed): position-prior + adjacency wave collapse with "
            "deterministic restarts and the promoted generator's anchor "
            "semantics, measured over the 16x16 corpus under the adapted "
            "30/10/10 protocol. This arm is honest-local: no validator-gated "
            "resampling inside (that is the constrained arm's trick); the "
            "bake-off (B2) compares the arms on the dossier metrics."
        ),
        "source_artifacts": [
            "labs/grid_genome/grid_helpers.py",
            "labs/grid_genome/corpus_builder.py",
            "data/seed_grids_16x16",
            "docs/project-research/deep-research/01/deep-research.md",
            "research/decision_records/0015-dormant-vocabulary-coverage.md",
            "research/decision_records/0029-16x16-default-grid-scale.md",
        ],
        "metrics": {
            "split": {"train": len(train), "dev": len(dev), "holdout": len(holdout)},
            "candidate_count": baseline["candidate_count"],
            "valid_count": baseline["valid_count"],
            "validity_rate": baseline["validity_rate"],
            "unique_signatures": baseline["unique_signatures"],
            "error_counts": baseline["error_counts"],
            "rich_roles_emitted": rich_roles,
            "rich_role_count": len(rich_roles),
            "training_copy_count": copies,
            "training_copy_rate": round(copies / len(corpus), 6),
            "core_mass": {
                "min": core_masses[0],
                "p50": core_masses[len(core_masses) // 2],
                "max": core_masses[-1],
            },
        },
        "closed_states": [
            "wfc_lab_exists_over_the_rich_alphabet",
            "wave_collapse_deterministic_per_seed",
            "protocol_split_adapted_and_recorded",
        ],
        "blocked_states": [
            "bakeoff_not_run (B2: random/Markov/constrained/WFC/hybrid on the dossier metrics)",
            "no_engine_adoption (B3: the measured winner, by decision record)",
            "human_pairwise_preference_not_collected (owner-deferred survey; recorded, never a blocker)",
        ],
        "decision": (
            "The documented WFC arm exists and emits the rich vocabulary at "
            "16x16; its honest-local validity is recorded here and judged "
            "in the B2 bake-off, not by this lab alone."
        ),
        "next_research_step": (
            "B2: the real documented bake-off — all five arms on the dossier "
            "metrics with measured generation time."
        ),
    }


def write_wfc_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{ARTIFACT_ID}.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )


def _count_pair(bucket: dict[str, dict[str, int]], left: str, right: str) -> None:
    counts = bucket.setdefault(left, {})
    counts[right] = counts.get(right, 0) + 1


def _allowed_neighbors(
    model: dict, tokens: list[str], direction: str
) -> set[str]:
    """Tokens legal in ``direction`` next to a cell holding any of ``tokens``."""
    adjacency = model["adjacency"]
    allowed: set[str] = set()
    if direction == "right":
        for token in tokens:
            allowed.update(adjacency["right"].get(token, {}))
    elif direction == "down":
        for token in tokens:
            allowed.update(adjacency["down"].get(token, {}))
    elif direction == "left":
        for left, rights in adjacency["right"].items():
            if any(token in rights for token in tokens):
                allowed.add(left)
    elif direction == "up":
        for upper, lowers in adjacency["down"].items():
            if any(token in lowers for token in tokens):
                allowed.add(upper)
    return allowed


def _trace_event(trace, event, **fields):
    if trace is not None:
        trace.append({'event': event, **deepcopy(fields)})


def _collapse(model: dict, rng: random.Random, *, trace=None) -> list[list[str]] | None:
    width, height = model["width"], model["height"]
    wave: dict[tuple[int, int], dict[str, int]] = {
        (x, y): dict(model["position_candidates"][f"{x},{y}"])
        for y in range(height)
        for x in range(width)
    }

    if trace is not None:
        _trace_event(trace, 'wave_started', width=width, height=height,
                     cells={f'{x},{y}': candidates for (x, y), candidates in wave.items()},
                     training_grid_ids=model.get('training_grid_ids'))

    def propagate(start: tuple[int, int]) -> bool:
        queue: deque[tuple[int, int]] = deque([start])
        while queue:
            x, y = queue.popleft()
            tokens = list(wave[(x, y)])
            for direction, (dx, dy) in _DIRECTIONS.items():
                nx, ny = x + dx, y + dy
                if not (0 <= nx < width and 0 <= ny < height):
                    continue
                allowed = _allowed_neighbors(model, tokens, direction)
                neighbor = wave[(nx, ny)]
                filtered = {
                    token: count
                    for token, count in neighbor.items()
                    if token in allowed
                }
                if len(filtered) != len(neighbor):
                    if not filtered:
                        _trace_event(trace, 'contradiction', source=[x, y], target=[nx, ny],
                                     direction=direction, before=neighbor, remaining=filtered)
                        return False
                    _trace_event(trace, 'propagated', source=[x, y], target=[nx, ny],
                                 direction=direction, before=neighbor, remaining=filtered)
                    wave[(nx, ny)] = filtered
                    queue.append((nx, ny))
        return True

    while True:
        undetermined = [
            (len(candidates), position[1], position[0], position)
            for position, candidates in wave.items()
            if len(candidates) > 1
        ]
        if not undetermined:
            break
        _, _, _, position = min(undetermined)
        token = weighted_sample(wave[position], rng)
        _trace_event(trace, 'cell_collapsed', position=list(position), choices=wave[position], token=token)
        wave[position] = {token: 1}
        if not propagate(position):
            return None

    matrix = [["." for _ in range(width)] for _ in range(height)]
    for (x, y), candidates in wave.items():
        matrix[y][x] = next(iter(candidates))
    if trace is not None:
        _trace_event(trace, 'collapsed', matrix=[''.join(row) for row in matrix])
    return matrix


def _finish(
    matrix: list[list[str]], rng: random.Random, *, trace=None
) -> tuple[list[list[str]] | None, str]:
    """The documented post-generator stabilizer pass + global constraints.

    Local adjacency cannot see global structure (the first measurement:
    98% disconnected cores from pure collapse — position priors mix
    different creatures' body plans into separate blobs). The dossier's
    own recommendation for WFC is "use as validator or post-generator
    stabilizer", so the arm finishes with constraint stabilization, never
    validator-gated resampling:

    - keep the LARGEST 8-connected core component, deleting stray core
      cells (deterministic tie-break by smallest (y, x) member);
    - global cardinality constraints as restart conditions: the retained
      core must clear the ratified floor (18 at 16x16, DR 0029) and at
      least one eye must exist (the sensors organ);
    - anchor normalization exactly as the promoted generator does it
      (every A reads as body, one core cell re-anointed via the RNG).
    """
    normalized = [row[:] for row in matrix]
    core: set[tuple[int, int]] = set()
    has_eye = False
    for y, row in enumerate(normalized):
        for x, token in enumerate(row):
            if token == "A":
                normalized[y][x] = "B"
            if normalized[y][x] == "B":
                core.add((x, y))
            if token == "E":
                has_eye = True
    if not core:
        _trace_event(trace, 'finish_rejected', reason='no core cells')
        return None, "no core cells"
    if not has_eye:
        _trace_event(trace, 'finish_rejected', reason='no eye cells')
        return None, "no eye cells"

    largest = _largest_component(core)
    height = len(normalized)
    floor = max(4, 18 * len(normalized[0]) * height // 256)
    if len(largest) < floor:
        _trace_event(trace, 'finish_rejected', reason=f'largest core component below the ratified floor {floor}',
                     retained_core_count=len(largest), floor=floor)
        return None, f"largest core component below the ratified floor {floor}"
    for x, y in core - largest:
        normalized[y][x] = "."

    anchor_x, anchor_y = rng.choice(sorted(largest))
    normalized[anchor_y][anchor_x] = "A"
    if trace is not None:
        _trace_event(trace, 'finished', matrix=[''.join(row) for row in normalized],
                     anchor=[anchor_x, anchor_y], retained_core=[list(point) for point in sorted(largest)],
                     dropped_core=[list(point) for point in sorted(core - largest)], floor=floor,
                     normalized_anchors=[[x, y] for y, row in enumerate(matrix) for x, token in enumerate(row) if token == 'A'])
    return normalized, ""


def _largest_component(points: set[tuple[int, int]]) -> set[tuple[int, int]]:
    remaining = set(points)
    best: set[tuple[int, int]] = set()
    while remaining:
        start = min(remaining, key=lambda point: (point[1], point[0]))
        remaining.discard(start)
        component = {start}
        queue: deque[tuple[int, int]] = deque([start])
        while queue:
            x, y = queue.popleft()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    neighbor = (x + dx, y + dy)
                    if neighbor in remaining:
                        remaining.discard(neighbor)
                        component.add(neighbor)
                        queue.append(neighbor)
        if len(component) > len(best):
            best = component
    return best


def _signature(grid: dict) -> str:
    return "|".join(
        f"{cell['x']},{cell['y']}:{cell['role']}"
        for cell in sorted(
            grid["cells"], key=lambda cell: (cell["y"], cell["x"], cell["role"])
        )
    )


def _core_mass(grid: dict) -> int:
    return sum(
        len(organ["cells"])
        for organ in grid["organs"].values()
        if organ.get("role") == "body_core" and organ.get("required") is True
    )


def write_wfc_corpus(generated_dir: Path, generated_grids: list[dict]) -> None:
    generated_dir.mkdir(parents=True, exist_ok=True)
    for grid in generated_grids:
        (generated_dir / f"{grid['grid_id']}.json").write_text(
            json.dumps(grid, indent=2) + "\n", encoding="utf-8"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="WFC grid lab (cycle 10 B1).")
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "wfc_grid"
    )
    parser.add_argument(
        "--generated-dir",
        type=Path,
        default=ROOT / "data" / "generated_grids" / "wfc_16x16",
    )
    args = parser.parse_args()
    report = build_wfc_report()
    write_wfc_artifacts(args.output_dir, report)
    from corpus_builder import build_seed_grids_16

    train = split_corpus(build_seed_grids_16())[0]
    model = train_wfc_model(train)
    write_wfc_corpus(
        args.generated_dir, build_wfc_corpus(model, count=50, rng_seed=1030)
    )
    print(json.dumps(report["metrics"], indent=2))


if __name__ == "__main__":
    main()
