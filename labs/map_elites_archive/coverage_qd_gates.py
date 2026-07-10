"""The documented coverage/QD gates + the plain-GA baseline (cycle 13 E4).

The dossier's MAP-Elites archive test decision gate, verbatim: "Keep
MAP-Elites if it yields at least 25% greater archive coverage than GA
at the same budget while keeping best-fitness within 10% of the
strongest comparator." The gap table adds the standing coverage figure:
>= 25% of the niche space after 20k evaluations. E4 judges all three
on E3's instrument:

- **MAP-Elites arm** — ``run_evaluation_loop`` (E3): the generational
  WFC parent path over the E1 scale geometry, 20,480 stress-probed
  lifecycle evaluations per seed.
- **Plain GA arm** — the classical control under the IDENTICAL budget,
  seed, bootstrap, variation operator (WFC retrained on the selected
  parents) and evaluation unit; the ONLY difference is the mechanism
  under test: scalar truncation selection (top half by fitness,
  deterministic tie-break) with full generational replacement, no
  archive, no niches. GA coverage is measured EXTERNALLY over its full
  evaluation history mapped into the 512-niche space (the standard QD
  comparison — the most favorable reading for the GA).

Protocol, recorded: the dossier prescribes 50,000 evaluations x ten
random seeds per comparator; this artifact runs the documented 20k
lower bound x the documented TEN paired seeds per comparator (twenty
full-scale runs; E3 measured the per-run unit first, DR 0028). History:
a three-seed compute adaptation ran first and returned a NEAR MISS on
the GA-advantage gate (+22.9% vs the >= 25% bar) — the non-sentimental
resolution was to execute the documented seed count in full, with
consecutive seeds fixed in advance and the ten-seed verdict operative
whichever way it lands. Failed gates are recorded, never fudged —
``judge_gates`` returns plain booleans either way.
"""

import argparse
import json
import sys
import time
from pathlib import Path
from statistics import mean


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
from evaluation_loop_scale import run_evaluation_loop  # noqa: E402
from extended_descriptors import score_extended_candidate  # noqa: E402
from niche_scale_archive import (  # noqa: E402
    TOTAL_SCALE_NICHES,
    build_population,
    scale_axis_values,
    scale_descriptor_for_values,
)
from wfc_grid import split_corpus  # noqa: E402
from wfc_grid import train_wfc_model as lab_train_wfc_model  # noqa: E402
from wfc_population_throughput import (  # noqa: E402
    load_frozen_scale_edges,
    wfc_population,
)


REPORT_DATE = "2026-07-09"
ARTIFACT_ID = "coverage_qd_gates_stage0"
DEFAULT_RNG_SEED = 20260709
DEFAULT_LIFECYCLE_TICKS = 24
# The documented gates, verbatim.
COVERAGE_GATE = 0.25  # >= 25% of the niche space
GA_COVERAGE_ADVANTAGE_GATE = 0.25  # MAP-Elites >= 25% greater coverage than GA
BEST_FITNESS_TOLERANCE = 0.10  # within 10% of the strongest comparator
# The documented ten seeds, fixed consecutively in advance (the
# three-seed adaptation's near-miss escalated to the full documented
# protocol — see the module docstring).
DEFAULT_SEEDS = [DEFAULT_RNG_SEED + offset for offset in range(10)]


def run_ga_baseline(
    *,
    population: int = 256,
    target_evaluations: int = 20_480,
    rng_seed: int = DEFAULT_RNG_SEED,
    lifecycle_ticks: int = DEFAULT_LIFECYCLE_TICKS,
) -> dict:
    """The plain GA under the identical budget — the documented control.

    Scalar truncation selection (top half by fitness, ties broken by
    grid_id), full generational replacement, the same WFC variation
    operator retrained on the selected parents, the same bootstrap and
    per-candidate seed scheme as the MAP-Elites arm. No archive, no
    niches — coverage is measured externally over the evaluation
    history.
    """
    edges = load_frozen_scale_edges()
    slip_profile = _load_default_slip()
    seeds = build_seed_grids_16()
    train, _, _ = split_corpus(seeds)

    evaluations = 0
    history_niches: set[tuple[int, ...]] = set()
    best_fitness = 0.0

    def evaluate(grid: dict, run_seed: int) -> float:
        nonlocal evaluations, best_fitness
        score = score_extended_candidate(
            grid,
            slip_profile=slip_profile,
            lifecycle_ticks=lifecycle_ticks,
            rng_seed=run_seed,
        )
        history_niches.add(
            scale_descriptor_for_values(
                scale_axis_values(grid, slip_profile=slip_profile), edges
            )
        )
        evaluations += 1
        best_fitness = max(best_fitness, score["fitness"])
        return score["fitness"]

    bootstrap, _ = build_population(
        population, rng_seed, train, lab_train_wfc_model(train)
    )
    scored = [
        (grid, evaluate(grid, rng_seed + index))
        for index, grid in enumerate(bootstrap)
    ]

    trajectory: list[dict] = []
    generation_index = 0
    while evaluations < target_evaluations:
        generation_index += 1
        ranked = sorted(
            scored, key=lambda pair: (-pair[1], pair[0]["grid_id"])
        )
        parents = [grid for grid, _ in ranked[: max(1, population // 2)]]
        candidates, failures = wfc_population(
            parents,
            population=population,
            generation_index=generation_index,
            rng_seed=rng_seed,
        )
        scored = [
            (
                candidate,
                evaluate(
                    candidate,
                    rng_seed + generation_index * 100_000 + index,
                ),
            )
            for index, candidate in enumerate(candidates)
        ]
        trajectory.append(
            {
                "generation": generation_index,
                "evaluations_total": evaluations,
                "collapse_failures": len(failures),
                "generation_best": round(
                    max((fitness for _, fitness in scored), default=0.0), 6
                ),
                "best_fitness_so_far": round(best_fitness, 6),
                "history_niches_touched": len(history_niches),
            }
        )

    return {
        "rng_seed": rng_seed,
        "population": population,
        "evaluations_total": evaluations,
        "generations_run": len(trajectory),
        "trajectory": trajectory,
        "best_fitness": round(best_fitness, 6),
        "history_niches_touched": len(history_niches),
        "history_coverage": round(len(history_niches) / TOTAL_SCALE_NICHES, 6),
        "selection": "truncation_top_half_scalar_fitness",
    }


def judge_gates(*, map_elites_runs: list[dict], ga_runs: list[dict]) -> dict:
    """The three documented gates over paired-seed means. Booleans, no
    sentiment."""
    map_coverage = round(mean(run["coverage"] for run in map_elites_runs), 6)
    ga_coverage = round(
        mean(run["history_coverage"] for run in ga_runs), 6
    )
    map_best = round(mean(run["best_fitness"] for run in map_elites_runs), 6)
    ga_best = round(mean(run["best_fitness"] for run in ga_runs), 6)
    strongest_best = max(map_best, ga_best)
    advantage = (
        round(map_coverage / ga_coverage - 1, 6) if ga_coverage else None
    )
    return {
        "map_elites_coverage_mean": map_coverage,
        "ga_coverage_mean": ga_coverage,
        "map_elites_best_fitness_mean": map_best,
        "ga_best_fitness_mean": ga_best,
        "strongest_best_fitness_mean": strongest_best,
        "coverage_gate": COVERAGE_GATE,
        "coverage_gate_met": map_coverage >= COVERAGE_GATE,
        "coverage_advantage_over_ga": advantage,
        "ga_advantage_gate": GA_COVERAGE_ADVANTAGE_GATE,
        "ga_advantage_gate_met": (
            advantage is not None and advantage >= GA_COVERAGE_ADVANTAGE_GATE
        ),
        "best_fitness_tolerance": BEST_FITNESS_TOLERANCE,
        "best_fitness_within_tolerance": (
            map_best >= strongest_best * (1 - BEST_FITNESS_TOLERANCE)
        ),
    }


def build_coverage_gate_report(
    *,
    population: int = 256,
    target_evaluations: int = 20_480,
    seeds: list[int] | None = None,
    lifecycle_ticks: int = DEFAULT_LIFECYCLE_TICKS,
) -> dict:
    seeds = list(DEFAULT_SEEDS) if seeds is None else list(seeds)
    map_elites_runs: list[dict] = []
    ga_runs: list[dict] = []
    for seed in seeds:
        loop = run_evaluation_loop(
            population=population,
            target_evaluations=target_evaluations,
            rng_seed=seed,
            lifecycle_ticks=lifecycle_ticks,
        )
        summary = loop["archive_summary"]
        map_elites_runs.append(
            {
                "rng_seed": seed,
                "evaluations_total": loop["evaluations_total"],
                "generations_run": len(loop["trajectory"]),
                "occupied_niches": summary["occupied_niches"],
                "coverage": summary["coverage"],
                "qd_score": summary["qd_score"],
                "best_fitness": summary["best_fitness"],
                "mean_elite_fitness": summary["mean_elite_fitness"],
                "descriptor_bin_spread": summary["descriptor_bin_spread"],
                # E5's clustering inputs, per independent seeded run.
                "elite_records": loop["elite_records"],
            }
        )
        ga_runs.append(
            run_ga_baseline(
                population=population,
                target_evaluations=target_evaluations,
                rng_seed=seed,
                lifecycle_ticks=lifecycle_ticks,
            )
        )
    verdict = judge_gates(map_elites_runs=map_elites_runs, ga_runs=ga_runs)

    gates_met = (
        verdict["coverage_gate_met"]
        and verdict["ga_advantage_gate_met"]
        and verdict["best_fitness_within_tolerance"]
    )
    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete" if gates_met else "refuted",
        "date": REPORT_DATE,
        "purpose": (
            "Judge the documented Phase-E gates on E3's instrument: coverage "
            ">= 25% of the 512-niche space; MAP-Elites >= 25% greater "
            "coverage than a plain GA under identical budgets, seeds, "
            "bootstrap, variation operator, and evaluation unit; "
            "best-fitness within 10% of the strongest comparator "
            "(cycle 13 E4)."
        ),
        "source_artifacts": [
            "labs/map_elites_archive/evaluation_loop_scale.py",
            "labs/map_elites_archive/niche_scale_archive.py",
            "labs/wfc_grid/wfc_population_throughput.py",
            "data/archives/evaluation_loop_scale_stage0.json",
            "docs/project-research/deep-research/01/deep-research.md",
        ],
        "metrics": {
            "protocol": {
                "population": population,
                "target_evaluations": target_evaluations,
                "seeds_run": len(seeds),
                "seeds": seeds,
                "lifecycle_ticks": lifecycle_ticks,
                "documented_protocol": (
                    "the dossier prescribes 50,000 evaluations x ten random "
                    "seeds per comparator; run at the documented 20k lower "
                    "bound with the documented ten paired seeds. History: a "
                    "three-seed compute adaptation returned a near miss on "
                    "the GA-advantage gate (+22.9% vs >= 25%); the "
                    "escalation to the full documented seed count was fixed "
                    "in advance (consecutive seeds, verdict operative "
                    "whichever way it lands) — recorded, never silent"
                ),
                "ga_design": (
                    "plain generational GA: truncation selection (top half "
                    "by scalar fitness, grid_id tie-break), full "
                    "replacement, the SAME WFC variation operator retrained "
                    "on selected parents, the SAME bootstrap/seed scheme/"
                    "evaluation unit; coverage measured over the full "
                    "evaluation history (the GA-favorable reading)"
                ),
            },
            "map_elites_runs": map_elites_runs,
            "ga_runs": ga_runs,
            "verdict": verdict,
        },
        "closed_states": [
            "documented_coverage_gate_judged",
            "ga_baseline_run_under_identical_budgets",
            "qd_score_and_per_axis_spread_recorded_per_run",
            "elite_records_recorded_per_seed_for_e5",
        ],
        "blocked_states": [
            "recurrent_families_not_yet_identified (E5 clusters the "
            "per-seed elite records)",
            "package_scale_geometry_seam_not_promoted (standing; named "
            "for the Phase-E gate)",
        ],
        "decision": (
            (
                "All three documented gates are MET: "
                if gates_met
                else "A documented gate FAILED — recorded, not fudged: "
            )
            + f"MAP-Elites coverage mean {verdict['map_elites_coverage_mean']}"
            f" (gate >= {COVERAGE_GATE}); advantage over the plain GA "
            f"{verdict['coverage_advantage_over_ga']} (gate >= "
            f"{GA_COVERAGE_ADVANTAGE_GATE}, GA history-coverage mean "
            f"{verdict['ga_coverage_mean']}); best fitness "
            f"{verdict['map_elites_best_fitness_mean']} vs strongest "
            f"{verdict['strongest_best_fitness_mean']} (tolerance "
            f"{BEST_FITNESS_TOLERANCE})."
        ),
        "next_research_step": (
            "E5: >= 5 recurrent morphological families across these "
            "independent seeded runs (clustering over the recorded elite "
            "records) — recurrence recorded, not curated."
        ),
    }


def write_coverage_gate_artifacts(
    output_dir: Path, report: dict, measured: dict | None = None
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = dict(report)
    if measured is not None:
        payload["measured"] = measured
    (output_dir / f"{ARTIFACT_ID}.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def _load_default_slip() -> dict:
    return json.loads(
        (ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="The documented coverage/QD gates + GA baseline (cycle 13 E4)."
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "archives"
    )
    parser.add_argument("--population", type=int, default=256)
    parser.add_argument("--target-evaluations", type=int, default=20_480)
    parser.add_argument(
        "--seeds", type=int, nargs="+", default=list(DEFAULT_SEEDS)
    )
    args = parser.parse_args()

    start = time.perf_counter()
    report = build_coverage_gate_report(
        population=args.population,
        target_evaluations=args.target_evaluations,
        seeds=args.seeds,
    )
    wall_clock = round(time.perf_counter() - start, 2)
    measured = {
        "context": (
            f"stage-0 dev machine; {len(args.seeds) * 2} full-scale runs "
            f"({len(args.seeds)} paired seeds x two comparators) at the "
            "documented 20k budget; E3 measured the per-run unit first "
            "(DR 0028)"
        ),
        "total_wall_clock_s": wall_clock,
        "runs": len(args.seeds) * 2,
    }
    write_coverage_gate_artifacts(args.output_dir, report, measured)
    print(json.dumps(report["metrics"]["verdict"], indent=2))
    print(json.dumps(measured, indent=2))
    print(report["decision"])


if __name__ == "__main__":
    main()
