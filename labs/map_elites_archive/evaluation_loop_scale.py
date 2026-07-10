"""The evaluation loop at documented scale (cycle 13 E3).

The dossier's MAP-Elites archive test budgets 50,000 evaluations per
run; the gap table demands 20k–50k stress-probed lifecycle evaluations.
This lab runs the full generational evolve loop at that budget over the
E1 scale geometry (8×8×8, frozen empirical edges):

    bootstrap population → [parents = archive elites (the promoted
    evolve ordering) → WFC retrain on the elite pool → generate the
    population → stress-probed lifecycle scoring → elite insertion]
    repeated until the evaluation budget is reached.

The parent path is WFC — E2's measured evidence (validity 1.0,
unique-signature rate 1.0, 7.04 ms/candidate WITH retraining, archive
growth 171→233) — recorded in the protocol, with the constrained
bootstrap mixing both promoted generator families exactly as E1/E2 did.

DR 0028 discipline, in order:

1. the wall-clock PILOT runs first and projects to 20k/50k;
2. the bound is PRE-REGISTERED before the full run:
   ``PRE_REGISTERED_BOUND_S = 600`` (the D5 precedent — one run-once
   evidence build on the stage-0 dev machine);
3. the full run's measured wall-clock is recorded against that bound in
   the artifact's ``measured`` section — if stdlib could not hold, the
   NumPy decision record would cite the measurement.

Determinism is pinned under seeds by the test suite (identical seeds →
identical trajectories and elites, byte-for-byte). Elite records carry
descriptor + axis values + a morphology signature hash so E5's family
clustering never needs the full grids in the artifact.

SLIP alignment stays out of this harness (generation measured without
profile constraints — the standing E2 scope note); the engine archive's
scale-geometry seam stays lab-side (the promotion is its own gated
package change, named for the Phase-E gate).
"""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
for sub in [
    "labs/map_elites_archive",
    "labs/grid_genome",
    "labs/readability_benchmark",
    "labs/lifecycle_sim",
    "labs/wfc_grid",
]:
    path = str(ROOT / sub)
    if path not in sys.path:
        sys.path.insert(0, path)
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from corpus_builder import build_seed_grids_16  # noqa: E402
from extended_descriptors import score_extended_candidate  # noqa: E402
from niche_scale_archive import (  # noqa: E402
    build_population,
    insert_scale_candidate,
    new_scale_archive,
    scale_archive_summary,
    scale_axis_values,
    scale_descriptor_for_values,
)
from wfc_grid import _signature, split_corpus  # noqa: E402
from wfc_grid import train_wfc_model as lab_train_wfc_model  # noqa: E402
from wfc_population_throughput import (  # noqa: E402
    load_frozen_scale_edges,
    parents_from_archive,
    wfc_population,
)


REPORT_DATE = "2026-07-09"
ARTIFACT_ID = "evaluation_loop_scale_stage0"
DEFAULT_RNG_SEED = 20260709
DEFAULT_LIFECYCLE_TICKS = 24
# Pre-registered BEFORE the full-scale run (the D5 precedent): one
# run-once evidence build must fit 600 s on the stage-0 dev machine, or
# the NumPy decision record cites the measurement (DR 0028).
PRE_REGISTERED_BOUND_S = 600.0


def run_evaluation_loop(
    *,
    population: int = 256,
    target_evaluations: int = 20_480,
    rng_seed: int = DEFAULT_RNG_SEED,
    lifecycle_ticks: int = DEFAULT_LIFECYCLE_TICKS,
) -> dict:
    """The full generational loop to the documented evaluation budget.

    Deterministic under ``rng_seed``: the bootstrap population, every
    generation's WFC collapse, every stress-probed lifecycle score, and
    every elite decision replay identically. Returns the archive, the
    per-generation trajectory, and lean elite records (descriptor, axis
    values, signature hash — E5's clustering inputs).
    """
    edges = load_frozen_scale_edges()
    slip_profile = _load_default_slip()
    seeds = build_seed_grids_16()
    train, _, _ = split_corpus(seeds)

    archive = new_scale_archive()
    elite_grids: dict[str, dict] = {}
    evaluations = 0

    def evaluate_and_insert(grid: dict, run_seed: int) -> None:
        nonlocal evaluations
        score = score_extended_candidate(
            grid,
            slip_profile=slip_profile,
            lifecycle_ticks=lifecycle_ticks,
            rng_seed=run_seed,
        )
        descriptor = scale_descriptor_for_values(
            scale_axis_values(grid, slip_profile=slip_profile), edges
        )
        insert_scale_candidate(archive, grid, score, descriptor)
        evaluations += 1
        event = archive["events"][-1]["event"]
        if event in ("inserted_empty_niche", "replaced_elite"):
            elite_grids[grid["grid_id"]] = grid

    bootstrap_population, bootstrap_composition = build_population(
        population, rng_seed, train, lab_train_wfc_model(train)
    )
    for index, grid in enumerate(bootstrap_population):
        evaluate_and_insert(grid, rng_seed + index)

    trajectory: list[dict] = []
    generation_index = 0
    while evaluations < target_evaluations:
        generation_index += 1
        parents = parents_from_archive(archive, elite_grids)
        candidates, failures = wfc_population(
            parents,
            population=population,
            generation_index=generation_index,
            rng_seed=rng_seed,
        )
        replacements_before = _replacement_count(archive)
        for index, candidate in enumerate(candidates):
            evaluate_and_insert(
                candidate,
                rng_seed + generation_index * 100_000 + index,
            )
        summary = scale_archive_summary(archive)
        trajectory.append(
            {
                "generation": generation_index,
                "evaluations_total": evaluations,
                "parent_count": len(parents),
                "collapse_failures": len(failures),
                "occupied_niches": summary["occupied_niches"],
                "coverage": summary["coverage"],
                "qd_score": summary["qd_score"],
                "best_fitness": summary["best_fitness"],
                "replacements_this_generation": _replacement_count(archive)
                - replacements_before,
            }
        )
        # Bound the working set: only current elites' grids parent the
        # next generation.
        current_elite_ids = {
            elite["grid_id"] for elite in archive["elites"].values()
        }
        elite_grids = {
            grid_id: grid
            for grid_id, grid in elite_grids.items()
            if grid_id in current_elite_ids
        }

    summary = scale_archive_summary(archive)
    elite_records = [
        {
            "niche": niche,
            "grid_id": elite["grid_id"],
            "fitness": elite["fitness"],
            "descriptor": elite["descriptor"]["values"],
            "axis_values": scale_axis_values(
                elite_grids[elite["grid_id"]], slip_profile=slip_profile
            ),
            "signature_hash": hashlib.sha256(
                _signature(elite_grids[elite["grid_id"]]).encode("utf-8")
            ).hexdigest()[:16],
        }
        for niche, elite in sorted(archive["elites"].items())
    ]
    return {
        "archive": archive,
        "archive_summary": summary,
        "trajectory": trajectory,
        "evaluations_total": evaluations,
        "bootstrap_composition": bootstrap_composition,
        "elite_records": elite_records,
    }


def build_evaluation_loop_report(
    *,
    population: int = 256,
    target_evaluations: int = 20_480,
    rng_seed: int = DEFAULT_RNG_SEED,
    lifecycle_ticks: int = DEFAULT_LIFECYCLE_TICKS,
) -> dict:
    result = run_evaluation_loop(
        population=population,
        target_evaluations=target_evaluations,
        rng_seed=rng_seed,
        lifecycle_ticks=lifecycle_ticks,
    )
    summary = result["archive_summary"]
    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete",
        "date": REPORT_DATE,
        "purpose": (
            "Run the full generational evolve loop at the documented "
            "evaluation budget (20k+ stress-probed lifecycle evaluations) "
            "over the E1 scale geometry with the E2-evidenced WFC parent "
            "path; wall-clock measured first against the pre-registered "
            "bound; determinism pinned under seeds (cycle 13 E3)."
        ),
        "source_artifacts": [
            "labs/map_elites_archive/niche_scale_archive.py",
            "labs/wfc_grid/wfc_population_throughput.py",
            "data/archives/niche_scale_archive_stage0.json",
            "data/wfc_grid/wfc_population_throughput_stage0.json",
            "data/seed_grids_16x16",
            "packages/mecha_engine/src/mecha_engine/generation",
            "docs/project-research/deep-research/01/deep-research.md",
        ],
        "metrics": {
            "protocol": {
                "population": population,
                "target_evaluations": target_evaluations,
                "rng_seed": rng_seed,
                "lifecycle_ticks": lifecycle_ticks,
                "wall_clock_bound_s": PRE_REGISTERED_BOUND_S,
                "parent_path": "wfc",
                "parent_path_evidence": (
                    "E2 (data/wfc_grid/wfc_population_throughput_stage0."
                    "json): validity 1.0, unique-signature rate 1.0, "
                    "7.04 ms/candidate with retraining, archive growth "
                    "171->233 under the WFC parent path"
                ),
                "bootstrap_composition": result["bootstrap_composition"],
                "frozen_edges_source": (
                    "data/archives/niche_scale_archive_stage0.json"
                ),
                "slip_alignment": (
                    "not enforced in this harness (the standing E2 scope "
                    "note); alignment gates belong to the ecosystem loop, "
                    "not the archive evaluation budget"
                ),
            },
            "evaluations_total": result["evaluations_total"],
            "generations_run": len(result["trajectory"]),
            "trajectory": result["trajectory"],
            "final_archive": summary,
            "elite_records": result["elite_records"],
        },
        "closed_states": [
            "documented_evaluation_budget_reached",
            "determinism_pinned_under_seeds",
            "wall_clock_bound_pre_registered_before_the_run",
            "trajectory_recorded_per_generation_for_the_e4_gates",
            "elite_records_carry_e5_clustering_inputs",
        ],
        "blocked_states": [
            "coverage_qd_gates_not_judged_here (E4 runs the documented "
            "gates including the GA baseline under identical budgets)",
            "package_scale_geometry_seam_not_promoted (still lab-side; "
            "named for the Phase-E gate)",
            "slip_alignment_not_enforced_in_this_harness (the standing "
            "E2 scope note)",
        ],
        "decision": (
            f"The loop ran {result['evaluations_total']} stress-probed "
            f"lifecycle evaluations over {len(result['trajectory'])} "
            f"generations of population {population}: "
            f"{summary['occupied_niches']} of 512 niches occupied "
            f"(coverage {summary['coverage']}), QD score "
            f"{summary['qd_score']}, best fitness "
            f"{summary['best_fitness']} — deterministic under seed "
            f"{rng_seed}."
        ),
        "next_research_step": (
            "E4: the documented coverage/QD gates plus the plain-GA "
            "baseline under identical budgets (MAP-Elites >=25% coverage "
            "over GA)."
        ),
    }


def measure_loop_pilot(
    *,
    population: int = 64,
    generations: int = 2,
    rng_seed: int = DEFAULT_RNG_SEED,
    lifecycle_ticks: int = DEFAULT_LIFECYCLE_TICKS,
) -> dict:
    """DR 0028: the pilot wall-clock, measured FIRST, projected to 20k/50k."""
    start = time.perf_counter()
    result = run_evaluation_loop(
        population=population,
        target_evaluations=population * (generations + 1),
        rng_seed=rng_seed,
        lifecycle_ticks=lifecycle_ticks,
    )
    elapsed_ms = (time.perf_counter() - start) * 1000
    mean_ms = round(elapsed_ms / result["evaluations_total"], 4)
    projection_20k = round(mean_ms * 20_000 / 1000, 2)
    projection_50k = round(mean_ms * 50_000 / 1000, 2)
    return {
        "context": (
            "stage-0 dev machine; the full loop unit (WFC retrain + "
            "collapse + stress-probed lifecycle scoring + elite "
            "insertion), bootstrap included"
        ),
        "pilot": {
            "population": population,
            "generations": generations,
            "evaluations": result["evaluations_total"],
            "mean_ms_per_evaluation": mean_ms,
        },
        "projections": {
            "evaluations_20k_s": projection_20k,
            "evaluations_50k_s": projection_50k,
            "projection_meets_bound_20k": projection_20k
            <= PRE_REGISTERED_BOUND_S,
            "projection_meets_bound_50k": projection_50k
            <= PRE_REGISTERED_BOUND_S,
        },
        "pre_registered_bound_s": PRE_REGISTERED_BOUND_S,
    }


def write_evaluation_loop_artifacts(
    output_dir: Path, report: dict, measured: dict | None = None
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = dict(report)
    if measured is not None:
        payload["measured"] = measured
    (output_dir / f"{ARTIFACT_ID}.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def _replacement_count(archive: dict) -> int:
    return sum(
        1
        for event in archive["events"]
        if event["event"] == "replaced_elite"
    )


def _load_default_slip() -> dict:
    return json.loads(
        (ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="The evaluation loop at documented scale (cycle 13 E3)."
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "archives"
    )
    parser.add_argument("--population", type=int, default=256)
    parser.add_argument("--target-evaluations", type=int, default=20_480)
    parser.add_argument("--rng-seed", type=int, default=DEFAULT_RNG_SEED)
    parser.add_argument("--skip-timing", action="store_true")
    args = parser.parse_args()

    # DR 0028 discipline, in order: pilot first, bound already
    # pre-registered, full run measured against it.
    measured = (
        None
        if args.skip_timing
        else measure_loop_pilot(rng_seed=args.rng_seed)
    )
    if measured is not None:
        print(json.dumps(measured, indent=2))

    full_start = time.perf_counter()
    report = build_evaluation_loop_report(
        population=args.population,
        target_evaluations=args.target_evaluations,
        rng_seed=args.rng_seed,
    )
    full_wall_clock = round(time.perf_counter() - full_start, 2)
    if measured is not None:
        measured["full_run"] = {
            "wall_clock_s": full_wall_clock,
            "meets_bound": full_wall_clock <= PRE_REGISTERED_BOUND_S,
            "bound_s": PRE_REGISTERED_BOUND_S,
        }

    write_evaluation_loop_artifacts(args.output_dir, report, measured)
    print(json.dumps(report["metrics"]["final_archive"], indent=2))
    print(json.dumps(report["metrics"]["trajectory"][-3:], indent=2))
    if measured is not None:
        print(json.dumps(measured["full_run"], indent=2))
    print(report["decision"])


if __name__ == "__main__":
    main()
