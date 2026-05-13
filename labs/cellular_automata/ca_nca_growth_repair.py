import argparse
import json
import random
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME = ROOT / "labs" / "grid_genome"
READABILITY = ROOT / "labs" / "readability_benchmark"
LIFECYCLE = ROOT / "labs" / "lifecycle_sim"
for path in [GRID_GENOME, READABILITY, LIFECYCLE]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from corpus_builder import PALETTES, build_seed_grids
from lifecycle_sim import run_lifecycle_simulation
from readability_benchmark import score_readability
from slip import is_grid_aligned
from validator import validate_grid


TOKENS = {".", "B", "A", "E", "M"}
SOURCE_REFS = [
    {
        "name": "Growing Neural Cellular Automata",
        "url": "https://distill.pub/2020/growing-ca/",
        "use": "Seed growth, persistence, and regeneration framing for local update rules.",
    },
    {
        "name": "Self-organising Textures",
        "url": "https://distill.pub/selforg/2021/textures/",
        "use": "Reference for local cellular update rules as generative texture dynamics.",
    },
]
LEARNED_REPAIR_SOURCE_REFS = SOURCE_REFS + [
    {
        "name": "Regenerating Soft Robots through Neural Cellular Automata",
        "url": "https://arxiv.org/abs/2102.02579",
        "use": "Reference for regeneration as a learned local-rule benchmark rather than target-template reconstruction.",
    },
]
DEFAULT_DAMAGE_PATTERNS = ("center_cut", "left_sensor", "lower_body")


def apply_damage(grid: dict, *, pattern: str = "center_cut") -> dict:
    damaged = deepcopy(grid)
    matrix = matrix_from_grid(damaged)
    removed = 0
    for y, row in enumerate(matrix):
        for x, token in enumerate(row):
            if token == ".":
                continue
            if _damage_hit(x, y, pattern):
                matrix[y][x] = "."
                removed += 1

    repaired_anchor = _ensure_anchor(matrix)
    damaged = grid_from_matrix(
        grid_id=f"{grid.get('grid_id', 'grid')}_damaged_{pattern}",
        matrix=matrix,
        palette=grid.get("palette", {}),
        parent_grid_id=grid.get("grid_id"),
        source=f"ca_damage_{pattern}",
        mutation_events=[f"ca_damage_{pattern}"] + (["anchor_reseeded"] if repaired_anchor else []),
        generation_delta=1,
    )
    damaged["metadata"]["damage_pattern"] = pattern
    damaged["metadata"]["removed_cell_count"] = removed
    return damaged


def apply_stochastic_damage(
    grid: dict,
    *,
    dropout_rate: float = 0.2,
    rng_seed: int = 20260512,
    event_index: int = 1,
) -> dict:
    rng = random.Random(rng_seed)
    matrix = matrix_from_grid(grid)
    removed = 0
    for y, row in enumerate(matrix):
        for x, token in enumerate(row):
            if token == ".":
                continue
            if rng.random() < dropout_rate:
                matrix[y][x] = "."
                removed += 1
    reseeded = _ensure_anchor(matrix)
    damaged = grid_from_matrix(
        grid_id=f"{grid.get('grid_id', 'grid')}_stochastic_damage_{event_index:02d}",
        matrix=matrix,
        palette=grid.get("palette", {}),
        parent_grid_id=grid.get("grid_id"),
        source="ca_stochastic_damage",
        mutation_events=[
            f"ca_stochastic_damage_{event_index:02d}",
        ]
        + (["anchor_reseeded"] if reseeded else []),
        generation_delta=1,
    )
    damaged["metadata"]["damage_pattern"] = "stochastic_dropout"
    damaged["metadata"]["dropout_rate"] = dropout_rate
    damaged["metadata"]["damage_event_index"] = event_index
    damaged["metadata"]["removed_cell_count"] = removed
    return damaged


def repair_with_local_attractor(
    damaged_grid: dict,
    target_grid: dict,
    *,
    steps: int = 8,
    rng_seed: int = 20260512,
) -> dict:
    rng = random.Random(rng_seed)
    current = matrix_from_grid(damaged_grid)
    target = matrix_from_grid(target_grid)
    for step in range(steps):
        current = _attractor_step(current, target, rng, step=step)
    _force_required_organs(current, target)
    return grid_from_matrix(
        grid_id=f"{target_grid.get('grid_id', 'grid')}_nca_repaired",
        matrix=current,
        palette=target_grid.get("palette", {}),
        parent_grid_id=damaged_grid.get("grid_id"),
        source="nca_inspired_local_attractor_repair",
        mutation_events=[
            "ca_damage_observed",
            "nca_inspired_local_attractor_repair",
        ],
        generation_delta=1,
    )


def grow_from_seed(
    target_grid: dict,
    *,
    steps: int = 12,
    rng_seed: int = 20260512,
) -> dict:
    rng = random.Random(rng_seed)
    target = matrix_from_grid(target_grid)
    current = [["." for _ in row] for row in target]
    anchor = _anchor_point(target)
    current[anchor[1]][anchor[0]] = "A"
    for step in range(steps):
        current = _attractor_step(current, target, rng, step=step)
    _force_required_organs(current, target)
    return grid_from_matrix(
        grid_id=f"{target_grid.get('grid_id', 'grid')}_nca_grown",
        matrix=current,
        palette=target_grid.get("palette", {}),
        parent_grid_id=target_grid.get("grid_id"),
        source="nca_inspired_seed_growth",
        mutation_events=["nca_inspired_seed_growth"],
        generation_delta=1,
    )


def run_persistence_rollout(
    start_grid: dict,
    target_grid: dict,
    *,
    steps: int = 12,
    rng_seed: int = 20260512,
) -> dict:
    rng = random.Random(rng_seed)
    target = matrix_from_grid(target_grid)
    current = matrix_from_grid(start_grid)
    timeline = []
    final_grid = start_grid
    for step in range(steps):
        current = _attractor_step(current, target, rng, step=step + 2)
        final_grid = grid_from_matrix(
            grid_id=f"{start_grid.get('grid_id', 'grid')}_persisted_{step + 1:02d}",
            matrix=current,
            palette=target_grid.get("palette", {}),
            parent_grid_id=start_grid.get("grid_id"),
            source="nca_inspired_persistence_rollout",
            mutation_events=[
                "nca_inspired_local_attractor_repair",
                "nca_inspired_persistence_rollout",
            ],
            generation_delta=1,
        )
        validation = validate_grid(final_grid)
        timeline.append(
            {
                "step": step + 1,
                "overlap": matrix_overlap(final_grid, target_grid),
                "valid": validation.ok,
                "readability": score_readability(final_grid)[
                    "proxy_readability_score"
                ],
            }
        )

    final_validation = validate_grid(final_grid)
    overlaps = [entry["overlap"] for entry in timeline]
    return {
        "step_count": steps,
        "rng_seed": rng_seed,
        "final_grid": final_grid,
        "timeline": timeline,
        "final_valid": final_validation.ok,
        "final_errors": final_validation.errors,
        "min_overlap": min(overlaps) if overlaps else matrix_overlap(start_grid, target_grid),
        "final_overlap": overlaps[-1] if overlaps else matrix_overlap(start_grid, target_grid),
    }


def matrix_overlap(candidate_grid: dict, target_grid: dict) -> float:
    candidate = matrix_from_grid(candidate_grid)
    target = matrix_from_grid(target_grid)
    target_cells = [
        (x, y)
        for y, row in enumerate(target)
        for x, token in enumerate(row)
        if token != "."
    ]
    if not target_cells:
        return 0.0
    matches = sum(1 for x, y in target_cells if candidate[y][x] == target[y][x])
    return round(matches / len(target_cells), 6)


def run_ca_nca_lab(
    *,
    count: int = 8,
    growth_steps: int = 12,
    repair_steps: int = 8,
    rng_seed: int = 20260512,
) -> dict:
    slip_profile = _load_default_slip()
    samples = []
    for index, target in enumerate(build_seed_grids()[:count]):
        damaged = apply_damage(target, pattern="center_cut")
        grown = grow_from_seed(target, steps=growth_steps, rng_seed=rng_seed + index)
        repaired = repair_with_local_attractor(
            damaged,
            target,
            steps=repair_steps,
            rng_seed=rng_seed + 1000 + index,
        )
        samples.append(
            _sample_report(
                target=target,
                damaged=damaged,
                grown=grown,
                repaired=repaired,
                slip_profile=slip_profile,
            )
        )

    return {
        "lab_id": "ca_nca_growth_repair_stage0",
        "date": "2026-05-12",
        "rng_seed": rng_seed,
        "sample_count": count,
        "growth_steps": growth_steps,
        "repair_steps": repair_steps,
        "source_mode": "discrete_nca_inspired_local_attractor",
        "source_note": (
            "This is not a trained neural cellular automaton. It is a small "
            "discrete local-attractor lab to test whether CA/NCA-style growth "
            "and repair metrics are useful after lifecycle metrics exist."
        ),
        "summary": _summary(samples),
        "samples": samples,
        "decision": _decision(samples),
        "limitations": [
            "No differentiable training loop is used in Stage 0.",
            "The attractor uses a target grid as a genotype-like template.",
            "Damage patterns are deterministic and small.",
            "Human perception of growth and repair is not rated yet.",
        ],
        "source_refs": SOURCE_REFS,
    }


def run_damage_stress_benchmark(
    *,
    count: int = 8,
    damage_patterns: tuple[str, ...] = DEFAULT_DAMAGE_PATTERNS,
    repair_steps: int = 8,
    persistence_steps: int = 12,
    rng_seed: int = 20260512,
) -> dict:
    slip_profile = _load_default_slip()
    results = []
    for index, target in enumerate(build_seed_grids()[:count]):
        for pattern_index, pattern in enumerate(damage_patterns):
            damage_seed = rng_seed + index * 100 + pattern_index
            damaged = apply_damage(target, pattern=pattern)
            repaired = repair_with_local_attractor(
                damaged,
                target,
                steps=repair_steps,
                rng_seed=damage_seed + 1000,
            )
            repaired["grid_id"] = f"{target['grid_id']}_{pattern}_nca_repaired"
            persistence = run_persistence_rollout(
                repaired,
                target,
                steps=persistence_steps,
                rng_seed=damage_seed + 2000,
            )
            final_grid = persistence["final_grid"]
            final_grid["grid_id"] = f"{target['grid_id']}_{pattern}_nca_persisted"
            damaged_readability = score_readability(damaged)[
                "proxy_readability_score"
            ]
            repaired_readability = score_readability(repaired)[
                "proxy_readability_score"
            ]
            final_readability = score_readability(final_grid)[
                "proxy_readability_score"
            ]
            results.append(
                {
                    "target_grid_id": target["grid_id"],
                    "damage_pattern": pattern,
                    "damaged_grid": damaged,
                    "repaired_grid": repaired,
                    "persistence_final_grid": final_grid,
                    "persistence_timeline": persistence["timeline"],
                    "metrics": {
                        "removed_cell_count": damaged["metadata"][
                            "removed_cell_count"
                        ],
                        "damaged_overlap": matrix_overlap(damaged, target),
                        "repair_overlap": matrix_overlap(repaired, target),
                        "persistence_final_overlap": persistence[
                            "final_overlap"
                        ],
                        "persistence_min_overlap": persistence["min_overlap"],
                        "damaged_valid": validate_grid(damaged).ok,
                        "repaired_valid": validate_grid(repaired).ok,
                        "persistence_final_valid": persistence["final_valid"],
                        "damaged_readability": damaged_readability,
                        "repaired_readability": repaired_readability,
                        "persistence_final_readability": final_readability,
                        "readability_delta_repair_vs_damage": round(
                            repaired_readability - damaged_readability,
                            6,
                        ),
                        "repair_lifecycle_survival": _lifecycle_survival(
                            repaired,
                            slip_profile,
                        ),
                    },
                }
            )

    summary = _stress_summary(results, damage_patterns)
    return {
        "lab_id": "ca_nca_persistence_damage_stage0",
        "date": "2026-05-12",
        "rng_seed": rng_seed,
        "target_count": count,
        "damage_patterns": list(damage_patterns),
        "repair_steps": repair_steps,
        "persistence_steps": persistence_steps,
        "source_mode": "discrete_nca_inspired_persistence_damage_stress",
        "source_note": (
            "This follow-up keeps the Stage 0 local-attractor baseline but "
            "tests multiple deterministic damage masks and idle persistence "
            "after repair. It is still not a trained NCA."
        ),
        "summary": summary,
        "results": results,
        "decision": _stress_decision(summary),
        "limitations": [
            "The repair rule still receives the target grid as a template.",
            "Damage masks are deterministic and hand-authored.",
            "Persistence uses the same local attractor rather than a learned stable policy.",
            "No human visual ratings are included.",
        ],
        "source_refs": SOURCE_REFS,
    }


def run_repeated_stochastic_damage_benchmark(
    *,
    count: int = 8,
    cycles: int = 5,
    dropout_rate: float = 0.2,
    repair_steps: int = 8,
    rng_seed: int = 20260512,
) -> dict:
    slip_profile = _load_default_slip()
    results = []
    for index, target in enumerate(build_seed_grids()[:count]):
        current = repair_with_local_attractor(
            grow_from_seed(target, steps=6, rng_seed=rng_seed + index),
            target,
            steps=repair_steps,
            rng_seed=rng_seed + 500 + index,
        )
        cycle_reports = []
        for cycle in range(1, cycles + 1):
            damage_seed = rng_seed + index * 1000 + cycle
            damaged = apply_stochastic_damage(
                current,
                dropout_rate=dropout_rate,
                rng_seed=damage_seed,
                event_index=cycle,
            )
            repaired = repair_with_local_attractor(
                damaged,
                target,
                steps=repair_steps,
                rng_seed=damage_seed + 5000,
            )
            repaired["grid_id"] = f"{target['grid_id']}_stochastic_cycle_{cycle:02d}_repaired"
            damaged_overlap = matrix_overlap(damaged, target)
            repair_overlap = matrix_overlap(repaired, target)
            cycle_reports.append(
                {
                    "cycle": cycle,
                    "damaged_grid": damaged,
                    "repaired_grid": repaired,
                    "metrics": {
                        "removed_cell_count": damaged["metadata"][
                            "removed_cell_count"
                        ],
                        "damaged_overlap": damaged_overlap,
                        "repair_overlap": repair_overlap,
                        "repair_gain": round(repair_overlap - damaged_overlap, 6),
                        "damaged_valid": validate_grid(damaged).ok,
                        "repaired_valid": validate_grid(repaired).ok,
                        "damaged_readability": score_readability(damaged)[
                            "proxy_readability_score"
                        ],
                        "repaired_readability": score_readability(repaired)[
                            "proxy_readability_score"
                        ],
                    },
                }
            )
            current = repaired

        final_validation = validate_grid(current)
        final_readability = score_readability(current)["proxy_readability_score"]
        results.append(
            {
                "target_grid_id": target["grid_id"],
                "final_grid": current,
                "cycle_reports": cycle_reports,
                "metrics": {
                    "final_valid": final_validation.ok,
                    "final_errors": final_validation.errors,
                    "final_overlap": matrix_overlap(current, target),
                    "final_readability": final_readability,
                    "final_lifecycle_survival": _lifecycle_survival(
                        current,
                        slip_profile,
                    ),
                    "cycle_count": len(cycle_reports),
                    "total_removed_cell_count": sum(
                        cycle["metrics"]["removed_cell_count"]
                        for cycle in cycle_reports
                    ),
                    "mean_repair_gain": _mean(
                        cycle["metrics"]["repair_gain"] for cycle in cycle_reports
                    ),
                    "min_repair_overlap": min(
                        cycle["metrics"]["repair_overlap"] for cycle in cycle_reports
                    )
                    if cycle_reports
                    else matrix_overlap(current, target),
                },
            }
        )

    summary = _repeated_stochastic_summary(results, cycles)
    return {
        "lab_id": "ca_nca_repeated_stochastic_damage_stage0",
        "date": "2026-05-12",
        "rng_seed": rng_seed,
        "target_count": count,
        "cycles": cycles,
        "dropout_rate": dropout_rate,
        "repair_steps": repair_steps,
        "source_mode": "discrete_nca_inspired_repeated_stochastic_damage",
        "source_note": (
            "This follow-up keeps the discrete target-template local attractor "
            "but repeatedly applies seeded stochastic dropout damage before "
            "repair. It is not a trained regenerating NCA."
        ),
        "summary": summary,
        "results": results,
        "decision": _repeated_stochastic_decision(summary),
        "limitations": [
            "The repair rule still receives the target grid as a template.",
            "Stochastic damage is seeded dropout, not a learned damage curriculum.",
            "The benchmark does not include human visual repair ratings.",
            "A trained NCA would need to beat this assisted baseline.",
        ],
        "source_refs": SOURCE_REFS,
    }


def train_role_prior_repair_model(
    training_grids: list[dict],
    *,
    min_position_frequency: float = 0.18,
) -> dict:
    if not training_grids:
        raise ValueError("training_grids must not be empty")

    width, height = training_grids[0].get("grid_size", [8, 8])
    position_counts: dict[tuple[int, int], Counter] = {
        (x, y): Counter()
        for y in range(height)
        for x in range(width)
    }
    token_totals: Counter = Counter()

    for grid in training_grids:
        if grid.get("grid_size") != [width, height]:
            raise ValueError("all training grids must share one grid_size")
        matrix = matrix_from_grid(grid)
        for y, row in enumerate(matrix):
            for x, token in enumerate(row):
                position_counts[(x, y)][token] += 1
                token_totals[token] += 1

    priors = []
    training_count = len(training_grids)
    for (x, y), counts in sorted(position_counts.items(), key=lambda item: (item[0][1], item[0][0])):
        live_counts = Counter(
            {token: count for token, count in counts.items() if token != "."}
        )
        if not live_counts:
            continue
        token, token_count = max(
            live_counts.items(),
            key=lambda item: (item[1], item[0] == "B", item[0]),
        )
        live_count = sum(live_counts.values())
        live_frequency = live_count / training_count
        if live_frequency < min_position_frequency:
            continue
        priors.append(
            {
                "x": x,
                "y": y,
                "token": token,
                "frequency": round(token_count / training_count, 6),
                "live_frequency": round(live_frequency, 6),
                "counts": dict(sorted(counts.items())),
            }
        )

    body_positions = _top_prior_positions(priors, {"A", "B"}, limit=14)
    return {
        "model_id": "role_prior_repair_model_stage0",
        "source_mode": "learned_role_position_prior",
        "training_grid_count": training_count,
        "grid_size": [width, height],
        "min_position_frequency": min_position_frequency,
        "target_template_used": False,
        "position_token_priors": priors,
        "required_positions": {
            "anchor": _first_prior_position(priors, "A"),
            "sensors": _top_prior_positions(priors, {"E"}, limit=3),
            "expression": _top_prior_positions(priors, {"M"}, limit=1),
            "body": body_positions,
        },
        "token_totals": dict(sorted(token_totals.items())),
        "limitations": [
            "This model learns corpus-level role/position priors only.",
            "It does not learn hidden states, gradients, or a differentiable NCA update rule.",
            "It repairs from the damaged grid and model priors, not from the target grid template.",
        ],
    }


def repair_with_role_prior_model(
    damaged_grid: dict,
    model: dict,
    *,
    steps: int = 8,
    rng_seed: int = 20260512,
) -> dict:
    rng = random.Random(rng_seed)
    matrix = matrix_from_grid(damaged_grid)
    prior_map = {
        (prior["x"], prior["y"]): prior
        for prior in model.get("position_token_priors", [])
    }
    min_frequency = model.get("min_position_frequency", 0.18)

    for step in range(steps):
        updated = [row[:] for row in matrix]
        coordinates = [(x, y) for y, row in enumerate(matrix) for x, _ in enumerate(row)]
        rng.shuffle(coordinates)
        for x, y in coordinates:
            if matrix[y][x] != ".":
                continue
            prior = prior_map.get((x, y))
            if not prior or prior.get("live_frequency", 0) < min_frequency:
                continue
            if _live_neighbor_count(matrix, x, y) > 0 or step >= 2:
                updated[y][x] = prior["token"]
        matrix = updated
        _force_learned_required_organs(matrix, model)

    _force_learned_required_organs(matrix, model)
    repaired = grid_from_matrix(
        grid_id=f"{damaged_grid.get('grid_id', 'grid')}_learned_role_prior_repaired",
        matrix=matrix,
        palette=damaged_grid.get("palette", {}),
        parent_grid_id=damaged_grid.get("grid_id"),
        source="learned_role_prior_repair",
        mutation_events=[
            "ca_damage_observed",
            "learned_role_prior_repair",
        ],
        generation_delta=1,
    )
    repaired["metadata"]["learned_model_id"] = model.get("model_id")
    repaired["metadata"]["target_template_used"] = False
    repaired["metadata"]["repair_steps"] = steps
    return repaired


def run_learned_repair_comparison(
    *,
    count: int = 8,
    cycles: int = 5,
    dropout_rate: float = 0.2,
    repair_steps: int = 8,
    rng_seed: int = 20260512,
) -> dict:
    slip_profile = _load_default_slip()
    seed_grids = build_seed_grids()
    targets = seed_grids[:count]
    training_grids = seed_grids[count:] or seed_grids
    model = train_role_prior_repair_model(training_grids)
    results = []

    for index, target in enumerate(targets):
        current_assisted = target
        current_learned = target
        cycle_reports = []
        for cycle in range(1, cycles + 1):
            damage_seed = rng_seed + index * 1000 + cycle
            assisted_damaged = apply_stochastic_damage(
                current_assisted,
                dropout_rate=dropout_rate,
                rng_seed=damage_seed,
                event_index=cycle,
            )
            learned_damaged = apply_stochastic_damage(
                current_learned,
                dropout_rate=dropout_rate,
                rng_seed=damage_seed,
                event_index=cycle,
            )
            assisted_repaired = repair_with_local_attractor(
                assisted_damaged,
                target,
                steps=repair_steps,
                rng_seed=damage_seed + 5000,
            )
            learned_repaired = repair_with_role_prior_model(
                learned_damaged,
                model,
                steps=repair_steps,
                rng_seed=damage_seed + 7000,
            )
            assisted_repaired["grid_id"] = f"{target['grid_id']}_cycle_{cycle:02d}_assisted_repaired"
            learned_repaired["grid_id"] = f"{target['grid_id']}_cycle_{cycle:02d}_learned_repaired"
            assisted_damaged_overlap = matrix_overlap(assisted_damaged, target)
            learned_damaged_overlap = matrix_overlap(learned_damaged, target)
            assisted_overlap = matrix_overlap(assisted_repaired, target)
            learned_overlap = matrix_overlap(learned_repaired, target)
            cycle_reports.append(
                {
                    "cycle": cycle,
                    "assisted_damaged_grid": assisted_damaged,
                    "learned_damaged_grid": learned_damaged,
                    "assisted_repaired_grid": assisted_repaired,
                    "learned_repaired_grid": learned_repaired,
                    "metrics": {
                        "assisted_damaged_overlap": assisted_damaged_overlap,
                        "learned_damaged_overlap": learned_damaged_overlap,
                        "assisted_repair_overlap": assisted_overlap,
                        "learned_repair_overlap": learned_overlap,
                        "assisted_repair_gain": round(
                            assisted_overlap - assisted_damaged_overlap,
                            6,
                        ),
                        "learned_repair_gain": round(
                            learned_overlap - learned_damaged_overlap,
                            6,
                        ),
                        "overlap_delta_learned_vs_assisted": round(
                            learned_overlap - assisted_overlap,
                            6,
                        ),
                        "assisted_valid": validate_grid(assisted_repaired).ok,
                        "learned_valid": validate_grid(learned_repaired).ok,
                        "assisted_readability": score_readability(
                            assisted_repaired
                        )["proxy_readability_score"],
                        "learned_readability": score_readability(
                            learned_repaired
                        )["proxy_readability_score"],
                    },
                }
            )
            current_assisted = assisted_repaired
            current_learned = learned_repaired

        assisted_validation = validate_grid(current_assisted)
        learned_validation = validate_grid(current_learned)
        results.append(
            {
                "target_grid_id": target["grid_id"],
                "assisted_final_grid": current_assisted,
                "learned_final_grid": current_learned,
                "cycle_reports": cycle_reports,
                "metrics": {
                    "assisted_final_valid": assisted_validation.ok,
                    "assisted_final_errors": assisted_validation.errors,
                    "learned_final_valid": learned_validation.ok,
                    "learned_final_errors": learned_validation.errors,
                    "assisted_final_overlap": matrix_overlap(current_assisted, target),
                    "learned_final_overlap": matrix_overlap(current_learned, target),
                    "assisted_final_readability": score_readability(
                        current_assisted
                    )["proxy_readability_score"],
                    "learned_final_readability": score_readability(
                        current_learned
                    )["proxy_readability_score"],
                    "assisted_final_lifecycle_survival": _lifecycle_survival(
                        current_assisted,
                        slip_profile,
                    ),
                    "learned_final_lifecycle_survival": _lifecycle_survival(
                        current_learned,
                        slip_profile,
                    ),
                    "cycle_count": len(cycle_reports),
                },
            }
        )

    summary = _learned_repair_comparison_summary(results, cycles)
    return {
        "lab_id": "ca_nca_learned_repair_comparison_stage0",
        "date": "2026-05-12",
        "rng_seed": rng_seed,
        "target_count": count,
        "training_grid_count": model["training_grid_count"],
        "cycles": cycles,
        "dropout_rate": dropout_rate,
        "repair_steps": repair_steps,
        "source_mode": "learned_role_prior_vs_assisted_local_attractor",
        "source_note": (
            "The learned side uses a corpus-trained role/position prior and "
            "does not receive the per-target grid template during repair. The "
            "assisted side is the existing target-template local attractor."
        ),
        "learned_model": model,
        "summary": summary,
        "results": results,
        "decision": _learned_repair_comparison_decision(summary),
        "limitations": [
            "The learned rule is a simple role-prior baseline, not a trained neural cellular automaton.",
            "Evaluation still uses target grids to score overlap, but target grids are not passed to the learned repair function.",
            "No human visual repair ratings are included.",
            "The assisted baseline remains template-aided and is expected to retain perfect overlap on this corpus.",
        ],
        "source_refs": LEARNED_REPAIR_SOURCE_REFS,
    }


def write_ca_nca_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "ca_nca_growth_repair_stage0.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    samples_dir = output_dir / "samples"
    samples_dir.mkdir(exist_ok=True)
    for sample in report["samples"]:
        for key in ["target_grid", "damaged_grid", "grown_grid", "repaired_grid"]:
            grid = sample[key]
            (samples_dir / f"{grid['grid_id']}.json").write_text(
                json.dumps(grid, indent=2) + "\n",
                encoding="utf-8",
            )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")


def write_persistence_damage_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "ca_nca_persistence_damage_stage0.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    stress_dir = output_dir / "stress_samples"
    stress_dir.mkdir(exist_ok=True)
    for result in report["results"]:
        prefix = f"{result['target_grid_id']}_{result['damage_pattern']}"
        for key in ["damaged_grid", "repaired_grid", "persistence_final_grid"]:
            grid = result[key]
            stem = key.replace("_grid", "")
            (stress_dir / f"{prefix}_{stem}.json").write_text(
                json.dumps(grid, indent=2) + "\n",
                encoding="utf-8",
            )
    (output_dir / "persistence_damage_README.md").write_text(
        _persistence_readme_text(report),
        encoding="utf-8",
    )


def write_repeated_stochastic_damage_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "ca_nca_repeated_stochastic_damage_stage0.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    samples_dir = output_dir / "repeated_stress_samples"
    samples_dir.mkdir(exist_ok=True)
    for result in report["results"]:
        final_grid = result["final_grid"]
        (samples_dir / f"{final_grid['grid_id']}.json").write_text(
            json.dumps(final_grid, indent=2) + "\n",
            encoding="utf-8",
        )
        for cycle in result["cycle_reports"]:
            for key in ["damaged_grid", "repaired_grid"]:
                grid = cycle[key]
                (samples_dir / f"{grid['grid_id']}.json").write_text(
                    json.dumps(grid, indent=2) + "\n",
                    encoding="utf-8",
                )
    (output_dir / "repeated_stochastic_damage_README.md").write_text(
        _repeated_stochastic_readme_text(report),
        encoding="utf-8",
    )


def write_learned_repair_comparison_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "ca_nca_learned_repair_comparison_stage0.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    samples_dir = output_dir / "learned_repair_samples"
    samples_dir.mkdir(exist_ok=True)
    for result in report["results"]:
        prefix = result["target_grid_id"]
        for key in ["assisted_final_grid", "learned_final_grid"]:
            grid = result[key]
            (samples_dir / f"{prefix}_{key}.json").write_text(
                json.dumps(grid, indent=2) + "\n",
                encoding="utf-8",
            )
        for cycle in result["cycle_reports"]:
            cycle_id = cycle["cycle"]
            for key in [
                "assisted_damaged_grid",
                "learned_damaged_grid",
                "assisted_repaired_grid",
                "learned_repaired_grid",
            ]:
                grid = cycle[key]
                (samples_dir / f"{prefix}_cycle_{cycle_id:02d}_{key}.json").write_text(
                    json.dumps(grid, indent=2) + "\n",
                    encoding="utf-8",
                )
    (output_dir / "learned_repair_comparison_README.md").write_text(
        _learned_repair_comparison_readme_text(report),
        encoding="utf-8",
    )


def matrix_from_grid(grid: dict) -> list[list[str]]:
    width, height = grid.get("grid_size", [8, 8])
    matrix = [["." for _ in range(width)] for _ in range(height)]
    for cell in grid.get("cells", []):
        x = cell.get("x")
        y = cell.get("y")
        if not isinstance(x, int) or not isinstance(y, int):
            continue
        if x < 0 or y < 0 or y >= height or x >= width:
            continue
        matrix[y][x] = _token_for_cell(cell)
    return matrix


def grid_from_matrix(
    *,
    grid_id: str,
    matrix: list[list[str]],
    palette: dict,
    parent_grid_id: str | None,
    source: str,
    mutation_events: list[str],
    generation_delta: int,
) -> dict:
    palette_id = palette.get("palette_id", "lcd_green")
    colors = palette.get("colors") or PALETTES.get(palette_id, PALETTES["lcd_green"])
    cells = []
    core_cells = []
    sensor_cells = []
    expression_cells = []
    for y, row in enumerate(matrix):
        for x, token in enumerate(row):
            if token == ".":
                continue
            if token not in TOKENS:
                token = "B"
            if token in {"B", "A"}:
                cells.append(
                    _cell(
                        x,
                        y,
                        visual=colors[1],
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
                        visual=colors[min(2, len(colors) - 1)],
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
                        visual=colors[min(2, len(colors) - 1)],
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
        "grid_size": [len(matrix[0]), len(matrix)] if matrix else [0, 0],
        "cells": cells,
        "organs": organs,
        "palette": {
            "palette_id": palette_id,
            "colors": colors,
            "background_index": palette.get("background_index", 0),
        },
        "mutation": {
            "cell_mutation_rate": 0.05,
            "organ_shift_rate": 0.02,
            "palette_shift_rate": 0.01,
            "symmetry_break_rate": 0.01,
        },
        "lineage": {
            "generation": generation_delta,
            "ancestor_ids": [parent_grid_id] if parent_grid_id else [],
            "mutation_events": mutation_events,
        },
        "metadata": {"source": source},
    }


def _sample_report(
    *,
    target: dict,
    damaged: dict,
    grown: dict,
    repaired: dict,
    slip_profile: dict,
) -> dict:
    target_readability = score_readability(target)
    damaged_readability = score_readability(damaged)
    grown_readability = score_readability(grown)
    repaired_readability = score_readability(repaired)
    return {
        "target_grid_id": target["grid_id"],
        "target_grid": target,
        "damaged_grid": damaged,
        "grown_grid": grown,
        "repaired_grid": repaired,
        "metrics": {
            "damaged_overlap": matrix_overlap(damaged, target),
            "growth_overlap": matrix_overlap(grown, target),
            "repair_overlap": matrix_overlap(repaired, target),
            "target_valid": validate_grid(target).ok,
            "damaged_valid": validate_grid(damaged).ok,
            "grown_valid": validate_grid(grown).ok,
            "repaired_valid": validate_grid(repaired).ok,
            "target_readability": target_readability["proxy_readability_score"],
            "damaged_readability": damaged_readability["proxy_readability_score"],
            "grown_readability": grown_readability["proxy_readability_score"],
            "repaired_readability": repaired_readability["proxy_readability_score"],
            "target_lifecycle_survival": _lifecycle_survival(target, slip_profile),
            "damaged_lifecycle_survival": _lifecycle_survival(damaged, slip_profile),
            "grown_lifecycle_survival": _lifecycle_survival(grown, slip_profile),
            "repaired_lifecycle_survival": _lifecycle_survival(repaired, slip_profile),
            "grown_slip_aligned": is_grid_aligned(grown, slip_profile).ok,
            "repaired_slip_aligned": is_grid_aligned(repaired, slip_profile).ok,
        },
    }


def _summary(samples: list[dict]) -> dict:
    metrics = [sample["metrics"] for sample in samples]
    return {
        "sample_count": len(samples),
        "growth_validity_rate": _rate(metric["grown_valid"] for metric in metrics),
        "repair_validity_rate": _rate(metric["repaired_valid"] for metric in metrics),
        "growth_slip_alignment_rate": _rate(
            metric["grown_slip_aligned"] for metric in metrics
        ),
        "repair_slip_alignment_rate": _rate(
            metric["repaired_slip_aligned"] for metric in metrics
        ),
        "mean_damaged_overlap": _mean(metric["damaged_overlap"] for metric in metrics),
        "mean_growth_overlap": _mean(metric["growth_overlap"] for metric in metrics),
        "mean_attractor_repair_overlap": _mean(
            metric["repair_overlap"] for metric in metrics
        ),
        "mean_readability_delta_repair_vs_damage": _mean(
            metric["repaired_readability"] - metric["damaged_readability"]
            for metric in metrics
        ),
        "lifecycle_after_repair": {
            "mean_survival_ratio": _mean(
                metric["repaired_lifecycle_survival"] for metric in metrics
            ),
            "mean_delta_vs_damaged": _mean(
                metric["repaired_lifecycle_survival"]
                - metric["damaged_lifecycle_survival"]
                for metric in metrics
            ),
        },
    }


def _stress_summary(results: list[dict], damage_patterns: tuple[str, ...]) -> dict:
    metrics = [result["metrics"] for result in results]
    pattern_summaries = {}
    for pattern in damage_patterns:
        pattern_metrics = [
            result["metrics"]
            for result in results
            if result["damage_pattern"] == pattern
        ]
        pattern_summaries[pattern] = _pattern_summary(pattern_metrics)

    hardest_pattern = None
    if pattern_summaries:
        hardest_pattern = min(
            pattern_summaries,
            key=lambda pattern: (
                pattern_summaries[pattern]["mean_repair_overlap"],
                pattern_summaries[pattern]["mean_persistence_overlap"],
                pattern_summaries[pattern]["mean_damaged_overlap"],
            ),
        )

    return {
        "sample_count": len(results),
        "pattern_count": len(damage_patterns),
        "patterns": pattern_summaries,
        "repair_validity_rate": _rate(metric["repaired_valid"] for metric in metrics),
        "persistence_validity_rate": _rate(
            metric["persistence_final_valid"] for metric in metrics
        ),
        "mean_removed_cell_count": _mean(
            metric["removed_cell_count"] for metric in metrics
        ),
        "mean_damaged_overlap": _mean(
            metric["damaged_overlap"] for metric in metrics
        ),
        "mean_repair_overlap": _mean(metric["repair_overlap"] for metric in metrics),
        "mean_persistence_overlap": _mean(
            metric["persistence_final_overlap"] for metric in metrics
        ),
        "mean_persistence_min_overlap": _mean(
            metric["persistence_min_overlap"] for metric in metrics
        ),
        "mean_readability_delta_repair_vs_damage": _mean(
            metric["readability_delta_repair_vs_damage"] for metric in metrics
        ),
        "repair_lifecycle_survival_mean": _mean(
            metric["repair_lifecycle_survival"] for metric in metrics
        ),
        "hardest_pattern": hardest_pattern,
    }


def _pattern_summary(metrics: list[dict]) -> dict:
    return {
        "sample_count": len(metrics),
        "repair_validity_rate": _rate(metric["repaired_valid"] for metric in metrics),
        "persistence_validity_rate": _rate(
            metric["persistence_final_valid"] for metric in metrics
        ),
        "mean_removed_cell_count": _mean(
            metric["removed_cell_count"] for metric in metrics
        ),
        "mean_damaged_overlap": _mean(
            metric["damaged_overlap"] for metric in metrics
        ),
        "mean_repair_overlap": _mean(metric["repair_overlap"] for metric in metrics),
        "mean_persistence_overlap": _mean(
            metric["persistence_final_overlap"] for metric in metrics
        ),
        "mean_readability_delta_repair_vs_damage": _mean(
            metric["readability_delta_repair_vs_damage"] for metric in metrics
        ),
    }


def _repeated_stochastic_summary(results: list[dict], cycles: int) -> dict:
    metrics = [result["metrics"] for result in results]
    cycle_metrics = [
        cycle["metrics"]
        for result in results
        for cycle in result["cycle_reports"]
    ]
    return {
        "sample_count": len(results),
        "cycle_count": cycles,
        "total_damage_events": len(cycle_metrics),
        "final_validity_rate": _rate(metric["final_valid"] for metric in metrics),
        "mean_final_overlap": _mean(metric["final_overlap"] for metric in metrics),
        "mean_final_readability": _mean(
            metric["final_readability"] for metric in metrics
        ),
        "mean_final_lifecycle_survival": _mean(
            metric["final_lifecycle_survival"] for metric in metrics
        ),
        "mean_removed_cells_per_event": _mean(
            metric["removed_cell_count"] for metric in cycle_metrics
        ),
        "mean_repair_gain_per_event": _mean(
            metric["repair_gain"] for metric in cycle_metrics
        ),
        "mean_damaged_overlap_per_event": _mean(
            metric["damaged_overlap"] for metric in cycle_metrics
        ),
        "mean_repair_overlap_per_event": _mean(
            metric["repair_overlap"] for metric in cycle_metrics
        ),
        "min_repair_overlap": min(
            (metric["repair_overlap"] for metric in cycle_metrics),
            default=0.0,
        ),
        "repaired_validity_rate_per_event": _rate(
            metric["repaired_valid"] for metric in cycle_metrics
        ),
    }


def _learned_repair_comparison_summary(results: list[dict], cycles: int) -> dict:
    metrics = [result["metrics"] for result in results]
    cycle_metrics = [
        cycle["metrics"]
        for result in results
        for cycle in result["cycle_reports"]
    ]
    return {
        "sample_count": len(results),
        "cycle_count": cycles,
        "total_damage_events": len(cycle_metrics),
        "assisted_final_validity_rate": _rate(
            metric["assisted_final_valid"] for metric in metrics
        ),
        "learned_final_validity_rate": _rate(
            metric["learned_final_valid"] for metric in metrics
        ),
        "mean_assisted_final_overlap": _mean(
            metric["assisted_final_overlap"] for metric in metrics
        ),
        "mean_learned_final_overlap": _mean(
            metric["learned_final_overlap"] for metric in metrics
        ),
        "mean_final_overlap_delta_learned_vs_assisted": _mean(
            metric["learned_final_overlap"] - metric["assisted_final_overlap"]
            for metric in metrics
        ),
        "mean_assisted_repair_gain_per_event": _mean(
            metric["assisted_repair_gain"] for metric in cycle_metrics
        ),
        "mean_learned_repair_gain_per_event": _mean(
            metric["learned_repair_gain"] for metric in cycle_metrics
        ),
        "mean_event_overlap_delta_learned_vs_assisted": _mean(
            metric["overlap_delta_learned_vs_assisted"] for metric in cycle_metrics
        ),
        "learned_beats_assisted_final_count": sum(
            1
            for metric in metrics
            if metric["learned_final_overlap"] > metric["assisted_final_overlap"]
        ),
        "learned_ties_assisted_final_count": sum(
            1
            for metric in metrics
            if metric["learned_final_overlap"] == metric["assisted_final_overlap"]
        ),
        "mean_learned_final_readability": _mean(
            metric["learned_final_readability"] for metric in metrics
        ),
        "mean_learned_final_lifecycle_survival": _mean(
            metric["learned_final_lifecycle_survival"] for metric in metrics
        ),
        "target_template_used_by_learned": False,
    }


def _decision(samples: list[dict]) -> dict:
    summary = _summary(samples)
    adoptable = (
        summary["repair_validity_rate"] >= 0.9
        and summary["mean_attractor_repair_overlap"] >= 0.9
        and summary["mean_readability_delta_repair_vs_damage"] > 0
    )
    return {
        "status": "prototype_discrete_attractor" if adoptable else "watch",
        "adoption": "lab_only_not_trained_nca",
        "reason": (
            "The discrete local-attractor repair improves damaged grids and "
            "preserves lifecycle viability, but it is not a trained NCA and "
            "should remain a repair/growth lab until visual ratings and harder "
            "damage tests exist."
        ),
    }


def _stress_decision(summary: dict) -> dict:
    stable = (
        summary["repair_validity_rate"] >= 0.9
        and summary["persistence_validity_rate"] >= 0.9
        and summary["mean_repair_overlap"] >= 0.9
        and summary["mean_persistence_overlap"] >= 0.9
    )
    return {
        "status": "prototype_persistence_baseline" if stable else "watch_harder_damage",
        "adoption": "lab_only_not_trained_nca",
        "reason": (
            "The local-attractor baseline survives deterministic multi-damage "
            "and idle persistence stress tests, but the target-template rule "
            "is still too assisted to justify an ML NCA dependency."
            if stable
            else "The stress benchmark exposed repair or persistence weakness "
            "that should be fixed before any larger NCA implementation."
        ),
    }


def _repeated_stochastic_decision(summary: dict) -> dict:
    stable = (
        summary["final_validity_rate"] >= 0.9
        and summary["mean_final_overlap"] >= 0.9
        and summary["repaired_validity_rate_per_event"] >= 0.9
    )
    return {
        "status": "prototype_repeated_stress" if stable else "watch_repeated_stress",
        "adoption": "lab_only_not_trained_nca",
        "reason": (
            "The assisted local-attractor baseline survives repeated seeded "
            "dropout repair cycles, so repeated stochastic damage is now part "
            "of the CA/NCA benchmark contract."
            if stable
            else "Repeated stochastic damage exposed instability that should "
            "be addressed before any trained NCA comparison."
        ),
    }


def _learned_repair_comparison_decision(summary: dict) -> dict:
    learned_beats_assisted = (
        summary["learned_final_validity_rate"] >= 0.9
        and summary["mean_learned_final_overlap"]
        >= summary["mean_assisted_final_overlap"]
        and summary["mean_learned_final_lifecycle_survival"] >= 0.9
    )
    learned_is_promising = (
        summary["learned_final_validity_rate"] >= 0.75
        and summary["mean_learned_final_overlap"] >= 0.65
        and summary["mean_learned_repair_gain_per_event"] >= 0
    )
    if learned_beats_assisted:
        status = "promote_less_assisted_repair"
        reason = (
            "The learned role-prior repair matched or beat the assisted "
            "target-template baseline on validity, overlap, and lifecycle "
            "survival. It should become the next less-assisted repair surface."
        )
    elif learned_is_promising:
        status = "watch_learned_repair"
        reason = (
            "The learned role-prior repair remains valid and sometimes useful, "
            "but it does not beat the assisted target-template baseline."
        )
    else:
        status = "keep_assisted_baseline"
        reason = (
            "The learned role-prior repair does not yet clear the assisted "
            "baseline. Keep the target-template benchmark as the comparison "
            "contract and require stronger learned repair before promotion."
        )
    return {
        "status": status,
        "adoption": "lab_only_less_assisted_repair_candidate",
        "reason": reason,
    }


def _top_prior_positions(
    priors: list[dict],
    tokens: set[str],
    *,
    limit: int,
) -> list[list[int]]:
    matches = [
        prior
        for prior in priors
        if prior["token"] in tokens
    ]
    matches.sort(
        key=lambda prior: (
            prior["live_frequency"],
            prior["frequency"],
            -abs(prior["x"] - 3.5) - abs(prior["y"] - 3.5),
        ),
        reverse=True,
    )
    return [[prior["x"], prior["y"]] for prior in matches[:limit]]


def _first_prior_position(priors: list[dict], token: str) -> list[int]:
    positions = _top_prior_positions(priors, {token}, limit=1)
    return positions[0] if positions else [3, 3]


def _force_learned_required_organs(matrix: list[list[str]], model: dict) -> None:
    required = model.get("required_positions", {})
    for x, y in required.get("body", [])[:8]:
        if matrix[y][x] == ".":
            matrix[y][x] = "B"

    if not any("A" in row for row in matrix):
        x, y = required.get("anchor", [3, 3])
        matrix[y][x] = "A"

    if not any("E" in row for row in matrix):
        for x, y in required.get("sensors", []):
            if matrix[y][x] != "A":
                matrix[y][x] = "E"
                break

    if not any("M" in row for row in matrix):
        for x, y in required.get("expression", []):
            if matrix[y][x] not in {"A", "E"}:
                matrix[y][x] = "M"
                break


def _attractor_step(
    current: list[list[str]],
    target: list[list[str]],
    rng: random.Random,
    *,
    step: int,
) -> list[list[str]]:
    updated = [row[:] for row in current]
    coordinates = [
        (x, y) for y, row in enumerate(current) for x, _ in enumerate(row)
    ]
    rng.shuffle(coordinates)
    for x, y in coordinates:
        target_token = target[y][x]
        current_token = current[y][x]
        live_neighbors = _live_neighbor_count(current, x, y)
        target_neighbors = _target_neighbor_count(current, target, x, y)
        if target_token == ".":
            if current_token != "." and live_neighbors <= 1:
                updated[y][x] = "."
            continue
        if current_token == target_token:
            continue
        if live_neighbors > 0 or target_neighbors > 0 or step >= 2:
            updated[y][x] = target_token
    return updated


def _force_required_organs(matrix: list[list[str]], target: list[list[str]]) -> None:
    for token in ["A", "E", "M"]:
        if any(token in row for row in matrix):
            continue
        for y, row in enumerate(target):
            for x, target_token in enumerate(row):
                if target_token == token:
                    matrix[y][x] = token
                    break
            if any(token in row for row in matrix):
                break
    _ensure_anchor(matrix)


def _ensure_anchor(matrix: list[list[str]]) -> bool:
    if any("A" in row for row in matrix):
        return False
    body_points = [
        (x, y)
        for y, row in enumerate(matrix)
        for x, token in enumerate(row)
        if token == "B"
    ]
    if not body_points:
        return False
    x, y = sorted(body_points, key=lambda point: abs(point[0] - 3.5) + abs(point[1] - 3.5))[0]
    matrix[y][x] = "A"
    return True


def _anchor_point(matrix: list[list[str]]) -> tuple[int, int]:
    body_fallback = None
    for y, row in enumerate(matrix):
        for x, token in enumerate(row):
            if token == "A":
                return x, y
            if token == "B" and body_fallback is None:
                body_fallback = (x, y)
    return body_fallback or (len(matrix[0]) // 2, len(matrix) // 2)


def _damage_hit(x: int, y: int, pattern: str) -> bool:
    if pattern == "center_cut":
        return 2 <= x <= 4 and 2 <= y <= 4
    if pattern == "left_sensor":
        return x <= 2 and y <= 2
    if pattern == "lower_body":
        return 3 <= y <= 6 and x >= 2
    raise ValueError(f"unsupported damage pattern: {pattern}")


def _token_for_cell(cell: dict) -> str:
    if cell.get("organ") == "core":
        return "A" if cell.get("animation_anchor") is True else "B"
    if cell.get("organ") == "sensors" or cell.get("role") == "eye":
        return "E"
    if cell.get("organ") == "expression" or cell.get("role") == "mouth":
        return "M"
    return "B"


def _live_neighbor_count(matrix: list[list[str]], x: int, y: int) -> int:
    return sum(1 for nx, ny in _neighbors8(x, y, matrix) if matrix[ny][nx] != ".")


def _target_neighbor_count(
    current: list[list[str]], target: list[list[str]], x: int, y: int
) -> int:
    return sum(
        1
        for nx, ny in _neighbors8(x, y, current)
        if current[ny][nx] == target[ny][nx] and target[ny][nx] != "."
    )


def _neighbors8(
    x: int, y: int, matrix: list[list[str]]
) -> list[tuple[int, int]]:
    height = len(matrix)
    width = len(matrix[0])
    neighbors = []
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx = x + dx
            ny = y + dy
            if 0 <= nx < width and 0 <= ny < height:
                neighbors.append((nx, ny))
    return neighbors


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


def _lifecycle_survival(grid: dict, slip_profile: dict) -> float:
    if not validate_grid(grid).ok:
        return 0.0
    lifecycle_slip = slip_profile if is_grid_aligned(grid, slip_profile).ok else None
    result = run_lifecycle_simulation(
        grid,
        lifecycle_slip,
        ticks=24,
        policy="switchboard",
        rng_seed=20260512,
    )
    return round(result["survival_ticks"] / result["ticks_requested"], 6)


def _load_default_slip() -> dict:
    return json.loads(
        (ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )


def _rate(values) -> float:
    items = list(values)
    return round(sum(1 for item in items if item) / len(items), 6) if items else 0.0


def _mean(values) -> float:
    items = list(values)
    return round(mean(items), 6) if items else 0.0


def _readme_text(report: dict) -> str:
    summary = report["summary"]
    return (
        "# CA/NCA Growth and Repair Stage 0\n\n"
        "Discrete NCA-inspired local-attractor lab for grid growth and damage repair.\n\n"
        "Key results:\n\n"
        f"- Samples: {summary['sample_count']}\n"
        f"- Growth validity rate: {summary['growth_validity_rate']}\n"
        f"- Repair validity rate: {summary['repair_validity_rate']}\n"
        f"- Mean damaged overlap: {summary['mean_damaged_overlap']}\n"
        f"- Mean repair overlap: {summary['mean_attractor_repair_overlap']}\n"
        f"- Decision: {report['decision']['status']}\n\n"
        "This is not a trained neural cellular automaton. It is a measured "
        "local-rule baseline for deciding whether growth and repair deserve a "
        "heavier NCA implementation later.\n"
    )


def _persistence_readme_text(report: dict) -> str:
    summary = report["summary"]
    return (
        "# CA/NCA Persistence and Damage Stage 0\n\n"
        "Follow-up stress benchmark for deterministic multi-pattern damage and "
        "post-repair idle persistence.\n\n"
        "Key results:\n\n"
        f"- Samples: {summary['sample_count']}\n"
        f"- Damage patterns: {summary['pattern_count']}\n"
        f"- Repair validity rate: {summary['repair_validity_rate']}\n"
        f"- Persistence validity rate: {summary['persistence_validity_rate']}\n"
        f"- Mean damaged overlap: {summary['mean_damaged_overlap']}\n"
        f"- Mean repair overlap: {summary['mean_repair_overlap']}\n"
        f"- Mean persistence overlap: {summary['mean_persistence_overlap']}\n"
        f"- Hardest pattern: {summary['hardest_pattern']}\n"
        f"- Decision: {report['decision']['status']}\n\n"
        "This benchmark is still a discrete target-template baseline. It "
        "measures whether persistence and broader damage tests are useful "
        "before investing in a trained NCA pipeline.\n"
    )


def _repeated_stochastic_readme_text(report: dict) -> str:
    summary = report["summary"]
    return (
        "# CA/NCA Repeated Stochastic Damage Stage 0\n\n"
        "Follow-up stress benchmark for seeded stochastic dropout damage across "
        "multiple repair cycles.\n\n"
        "Key results:\n\n"
        f"- Samples: {summary['sample_count']}\n"
        f"- Cycles: {summary['cycle_count']}\n"
        f"- Total damage events: {summary['total_damage_events']}\n"
        f"- Final validity rate: {summary['final_validity_rate']}\n"
        f"- Mean final overlap: {summary['mean_final_overlap']}\n"
        f"- Mean repair gain per event: {summary['mean_repair_gain_per_event']}\n"
        f"- Mean final lifecycle survival: {summary['mean_final_lifecycle_survival']}\n"
        f"- Decision: {report['decision']['status']}\n\n"
        "This benchmark is still a discrete target-template baseline. It "
        "exists to define a harder comparison surface before any trained NCA "
        "implementation is considered.\n"
    )


def _learned_repair_comparison_readme_text(report: dict) -> str:
    summary = report["summary"]
    return (
        "# CA/NCA Learned Repair Comparison Stage 0\n\n"
        "Less-assisted repair comparison between the existing target-template "
        "local attractor and a corpus-trained role/position prior.\n\n"
        "Key results:\n\n"
        f"- Samples: {summary['sample_count']}\n"
        f"- Cycles: {summary['cycle_count']}\n"
        f"- Total damage events: {summary['total_damage_events']}\n"
        f"- Assisted final validity rate: {summary['assisted_final_validity_rate']}\n"
        f"- Learned final validity rate: {summary['learned_final_validity_rate']}\n"
        f"- Mean assisted final overlap: {summary['mean_assisted_final_overlap']}\n"
        f"- Mean learned final overlap: {summary['mean_learned_final_overlap']}\n"
        f"- Mean learned-vs-assisted final overlap delta: {summary['mean_final_overlap_delta_learned_vs_assisted']}\n"
        f"- Decision: {report['decision']['status']}\n\n"
        "The learned side does not receive the target grid template during "
        "repair. It is still a small statistical baseline, not a trained "
        "neural cellular automaton.\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("data/cellular_automata"))
    parser.add_argument(
        "--mode",
        choices=[
            "growth-repair",
            "persistence-damage",
            "repeated-stochastic-damage",
            "learned-repair-comparison",
        ],
        default="growth-repair",
    )
    parser.add_argument("--count", type=int, default=8)
    parser.add_argument("--growth-steps", type=int, default=12)
    parser.add_argument("--repair-steps", type=int, default=8)
    parser.add_argument("--persistence-steps", type=int, default=12)
    parser.add_argument("--cycles", type=int, default=5)
    parser.add_argument("--dropout-rate", type=float, default=0.2)
    parser.add_argument("--rng-seed", type=int, default=20260512)
    args = parser.parse_args()
    if args.mode == "learned-repair-comparison":
        report = run_learned_repair_comparison(
            count=args.count,
            cycles=args.cycles,
            dropout_rate=args.dropout_rate,
            repair_steps=args.repair_steps,
            rng_seed=args.rng_seed,
        )
        write_learned_repair_comparison_artifacts(args.output_dir, report)
    elif args.mode == "repeated-stochastic-damage":
        report = run_repeated_stochastic_damage_benchmark(
            count=args.count,
            cycles=args.cycles,
            dropout_rate=args.dropout_rate,
            repair_steps=args.repair_steps,
            rng_seed=args.rng_seed,
        )
        write_repeated_stochastic_damage_artifacts(args.output_dir, report)
    elif args.mode == "persistence-damage":
        report = run_damage_stress_benchmark(
            count=args.count,
            repair_steps=args.repair_steps,
            persistence_steps=args.persistence_steps,
            rng_seed=args.rng_seed,
        )
        write_persistence_damage_artifacts(args.output_dir, report)
    else:
        report = run_ca_nca_lab(
            count=args.count,
            growth_steps=args.growth_steps,
            repair_steps=args.repair_steps,
            rng_seed=args.rng_seed,
        )
        write_ca_nca_artifacts(args.output_dir, report)
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
