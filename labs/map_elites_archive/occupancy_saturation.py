"""Cycle 19 I5b: occupancy saturation past ~62% — measured, not guessed.

What bounds coverage over the documented 512-niche geometry? The
Phase-E remainder (narrowed by DR 0036: the collapsed neediness axis
was wasting a dimension; coverage moved 0.535 → 0.623) names three
candidate levers. This lab measures the two that exist without
changing any generator, plus the hard bound that scopes them all:

- **support_ceiling** — distinct descriptor bins present in the
  evaluation population under the run's own derived edges: the hard
  upper bound on occupancy for ANY selection scheme over that
  population. If baseline occupancy ≈ the ceiling, selection is not
  the bound — generation is.
- **in_sample_edges** — the same population binned by edges derived
  from itself (the calibration lever's theoretical best; degenerate
  by design as calibration practice — measured here only to size the
  lever, never to adopt in-sample calibration silently).
- **novelty_pool** — the SAME scored-evaluation budget drawn
  novelty-first (one candidate per unseen descriptor, then generation
  order) from a ``pool_factor``× generation pool. Generation is
  cheap; evaluation is the budget — the trade is explicit, and the
  pool's own distinct-descriptor count scopes what more generation
  volume can ever buy.

The mutation-heavy arm is NAMED, not run: the constrained generator
exposes no temperature knob; adding one is a generator change with
its own record.
"""

import argparse
import json
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from niche_scale_archive import (  # noqa: E402
    DEFAULT_LIFECYCLE_TICKS,
    DEFAULT_RNG_SEED,
    EVALUATION_STREAM_OFFSET,
    SCALE_DESCRIPTOR_NAMES,
    build_population,
    build_scale_archive,
    derive_scale_bin_edges,
    scale_archive_summary,
    scale_axis_values,
    scale_descriptor_for_values,
    _load_default_slip,
)
from corpus_builder import build_seed_grids_16  # noqa: E402
from wfc_grid import split_corpus, train_wfc_model  # noqa: E402

ARTIFACT_ID = "occupancy_saturation_stage0"
REPORT_DATE = "2026-07-20"
# Pre-registered reading rules: a lever "moves the plateau" only past
# this coverage delta; selection is "not the bound" at or above this
# utilization of the support ceiling.
LEVER_THRESHOLD = 0.02
SUPPORT_UTILIZATION_BAR = 0.9
NOVELTY_POOL_FACTOR = 3


def _descriptor_set(
    candidates: list[dict],
    edges: dict[str, list[float]],
    *,
    slip_profile: dict | None,
) -> set[tuple[int, ...]]:
    return {
        scale_descriptor_for_values(
            scale_axis_values(grid, slip_profile=slip_profile), edges
        )
        for grid in candidates
    }


def _novelty_first_selection(
    pool: list[dict],
    budget: int,
    edges: dict[str, list[float]],
    *,
    slip_profile: dict | None,
) -> list[dict]:
    """One candidate per unseen descriptor first, generation order for

    the remainder — deterministic, no scoring spent during selection.
    """
    seen: set[tuple[int, ...]] = set()
    novel: list[dict] = []
    rest: list[dict] = []
    for grid in pool:
        descriptor = scale_descriptor_for_values(
            scale_axis_values(grid, slip_profile=slip_profile), edges
        )
        if descriptor in seen:
            rest.append(grid)
        else:
            seen.add(descriptor)
            novel.append(grid)
    selected = (novel + rest)[:budget]
    return selected


def build_occupancy_report(
    *,
    derivation_count: int = 600,
    evaluation_count: int = 3000,
    pool_factor: int = NOVELTY_POOL_FACTOR,
    rng_seed: int = DEFAULT_RNG_SEED,
    lifecycle_ticks: int = DEFAULT_LIFECYCLE_TICKS,
) -> dict:
    slip_profile = _load_default_slip()
    seeds = build_seed_grids_16()
    train, _, _ = split_corpus(seeds)
    wfc_model = train_wfc_model(train)

    derivation, _ = build_population(
        derivation_count, rng_seed, seeds, wfc_model
    )
    derived_edges = {
        name: derive_scale_bin_edges(
            [
                scale_axis_values(grid, slip_profile=slip_profile)[name]
                for grid in derivation
            ]
        )
        for name in SCALE_DESCRIPTOR_NAMES
    }

    evaluation_seed = rng_seed + EVALUATION_STREAM_OFFSET
    evaluation, composition = build_population(
        evaluation_count, evaluation_seed, seeds, wfc_model
    )

    # Arm 1 — baseline: the niche-scale run's own configuration.
    baseline_archive = build_scale_archive(
        evaluation,
        slip_profile=slip_profile,
        lifecycle_ticks=lifecycle_ticks,
        rng_seed=rng_seed,
        edges=derived_edges,
    )
    baseline = scale_archive_summary(baseline_archive)

    # The hard bound: what this population can EVER fill.
    support = _descriptor_set(
        evaluation, derived_edges, slip_profile=slip_profile
    )

    # Arm 2 — in-sample edges: the calibration lever's maximum.
    in_sample_edges = {
        name: derive_scale_bin_edges(
            [
                scale_axis_values(grid, slip_profile=slip_profile)[name]
                for grid in evaluation
            ]
        )
        for name in SCALE_DESCRIPTOR_NAMES
    }
    in_sample = scale_archive_summary(
        build_scale_archive(
            evaluation,
            slip_profile=slip_profile,
            lifecycle_ticks=lifecycle_ticks,
            rng_seed=rng_seed,
            edges=in_sample_edges,
        )
    )

    # Arm 3 — novelty-first from a larger pool, the SAME scored budget.
    pool_seed = evaluation_seed + EVALUATION_STREAM_OFFSET
    pool, _ = build_population(
        evaluation_count * pool_factor, pool_seed, seeds, wfc_model
    )
    pool_support = _descriptor_set(
        pool, derived_edges, slip_profile=slip_profile
    )
    novelty_candidates = _novelty_first_selection(
        pool,
        evaluation_count,
        derived_edges,
        slip_profile=slip_profile,
    )
    novelty = scale_archive_summary(
        build_scale_archive(
            novelty_candidates,
            slip_profile=slip_profile,
            lifecycle_ticks=lifecycle_ticks,
            rng_seed=rng_seed,
            edges=derived_edges,
        )
    )

    support_utilization = round(
        baseline["occupied_niches"] / len(support), 6
    )
    levers = {
        "in_sample_edges": round(
            in_sample["coverage"] - baseline["coverage"], 6
        ),
        "novelty_pool": round(
            novelty["coverage"] - baseline["coverage"], 6
        ),
    }

    selection_is_bound = support_utilization < SUPPORT_UTILIZATION_BAR
    moving_levers = [
        name
        for name, delta in levers.items()
        if delta >= LEVER_THRESHOLD
    ]
    if not selection_is_bound and not moving_levers:
        finding = (
            "generation_support_is_the_bound: the baseline already "
            "fills the population's descriptor support and no "
            "measured lever moves the plateau — coverage past this "
            "point needs generators that REACH new descriptor bins, "
            "not better selection or calibration"
        )
    elif moving_levers:
        finding = (
            "measured_levers_move_the_plateau: " + ", ".join(moving_levers)
        )
    else:
        finding = (
            "selection_headroom_exists: the baseline leaves measured "
            "support unfilled"
        )

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete",
        "date": REPORT_DATE,
        "purpose": (
            "Measure what bounds archive coverage past the DR 0036 "
            "level (~0.62) with pre-registered instruments: the "
            "population support ceiling, the in-sample edge lever, "
            "and the novelty-first pool lever at the same scored "
            "budget."
        ),
        "source_artifacts": [
            "labs/map_elites_archive/niche_scale_archive.py",
            "data/archives/niche_scale_archive_stage0.json",
            "research/decision_records/0036-neediness-scale-recalibration.md",
            "research/experiment_reports/2026-07-09-phase-e-gate.md",
        ],
        "parameters": {
            "derivation_count": derivation_count,
            "evaluation_count": evaluation_count,
            "pool_factor": pool_factor,
            "rng_seed": rng_seed,
            "lifecycle_ticks": lifecycle_ticks,
            "lever_threshold": LEVER_THRESHOLD,
            "support_utilization_bar": SUPPORT_UTILIZATION_BAR,
            "population_composition": composition,
        },
        "metrics": {
            "support_ceiling": {
                "distinct_descriptors": len(support),
                "of_total_niches": baseline["total_possible_niches"],
            },
            "novelty_pool_support": {
                "pool_size": evaluation_count * pool_factor,
                "distinct_descriptors": len(pool_support),
            },
            "arms": {
                "baseline": baseline,
                "in_sample_edges": in_sample,
                "novelty_pool": novelty,
            },
            "support_utilization": support_utilization,
            "levers": levers,
            "finding": finding,
        },
        "closed_states": [
            "occupancy_bound_instrumented (support ceiling + two "
            "measured levers at the same scored budget)",
        ],
        "blocked_states": [
            "mutation_heavy_arm_not_run (the constrained generator "
            "exposes no mutation-temperature knob; adding one is a "
            "generator change with its own decision record — named, "
            "never smuggled)",
        ],
        "decision": finding,
        "next_research_step": (
            "if generation support is the bound: a "
            "descriptor-targeted generator increment (its own record); "
            "otherwise adopt the winning lever with its own gate"
        ),
    }


def write_occupancy_artifacts(
    output_dir: str | Path, report: dict
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{ARTIFACT_ID}.json"
    path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--derivation-count", type=int, default=600)
    parser.add_argument("--evaluation-count", type=int, default=3000)
    parser.add_argument(
        "--pool-factor", type=int, default=NOVELTY_POOL_FACTOR
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "archives"
    )
    args = parser.parse_args()
    report = build_occupancy_report(
        derivation_count=args.derivation_count,
        evaluation_count=args.evaluation_count,
        pool_factor=args.pool_factor,
    )
    written = write_occupancy_artifacts(args.output_dir, report)
    print(f"wrote {written}")
    print(json.dumps(report["metrics"]["levers"], indent=2))
    print(report["metrics"]["support_utilization"])
    print(report["metrics"]["finding"])
