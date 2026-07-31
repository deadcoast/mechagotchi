"""Cycle 20 J3: novelty-first at the evolution surface (DR 0040).

Three arms of the E3 loop at a matched scored budget — baseline,
novelty_first (pool_factor x generation, scored population drawn
first-of-unseen-niche first), and blend (novelty on even
generations) — judged by DR 0040's PRE-REGISTERED rule: an arm needs
coverage gain >= +0.02 AND qd_score >= 0.95 x baseline to be
adoptable; the highest-coverage adoptable arm wins; otherwise REJECT
and the loop keeps its baseline. Adopt, blend, and reject are all
first-class outcomes.
"""

import argparse
import json
import sys
import time
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from evaluation_loop_scale import (  # noqa: E402
    DEFAULT_LIFECYCLE_TICKS,
    DEFAULT_RNG_SEED,
    run_evaluation_loop,
)

ARTIFACT_ID = "novelty_evolution_stage0"
REPORT_DATE = "2026-07-20"
# DR 0040's pre-registered bars, verbatim.
COVERAGE_GAIN_BAR = 0.02
QD_COST_FACTOR = 0.95
ARMS = ("baseline", "novelty_first", "blend")


def build_novelty_evolution_report(
    *,
    population: int = 256,
    target_evaluations: int = 20_480,
    rng_seed: int = DEFAULT_RNG_SEED,
    lifecycle_ticks: int = DEFAULT_LIFECYCLE_TICKS,
    pool_factor: int = 3,
) -> dict:
    arms: dict[str, dict] = {}
    for arm_name in ARMS:
        started = time.perf_counter()
        result = run_evaluation_loop(
            population=population,
            target_evaluations=target_evaluations,
            rng_seed=rng_seed,
            lifecycle_ticks=lifecycle_ticks,
            selection=arm_name,
            pool_factor=pool_factor,
            # Pinned to the incumbent (cycle 24 N7): DR 0040 adopted
            # novelty-first on a bake-off between selection arms, and a
            # bake-off is only readable if every arm shares every other
            # setting with the run that decided it.
            slip_admission="none",
        )
        summary = result["archive_summary"]
        arms[arm_name] = {
            "evaluations_total": result["evaluations_total"],
            "generations": len(result["trajectory"]),
            "occupied_niches": summary["occupied_niches"],
            "coverage": summary["coverage"],
            "qd_score": summary["qd_score"],
            "mean_elite_fitness": summary["mean_elite_fitness"],
            "best_fitness": summary["best_fitness"],
            "wall_clock_s": round(time.perf_counter() - started, 3),
            "final_trajectory_entry": result["trajectory"][-1]
            if result["trajectory"]
            else None,
        }

    base = arms["baseline"]
    levers: dict[str, dict] = {}
    eligible: list[tuple[float, str]] = []
    for arm_name in ("novelty_first", "blend"):
        arm = arms[arm_name]
        gain = round(arm["coverage"] - base["coverage"], 6)
        qd_ratio = round(
            arm["qd_score"] / base["qd_score"], 6
        ) if base["qd_score"] else 0.0
        meets_gain = gain >= COVERAGE_GAIN_BAR
        meets_qd = arm["qd_score"] >= QD_COST_FACTOR * base["qd_score"]
        levers[arm_name] = {
            "coverage_gain": gain,
            "qd_ratio": qd_ratio,
            "meets_coverage_gain_bar": meets_gain,
            "meets_qd_cost_bar": meets_qd,
        }
        if meets_gain and meets_qd:
            eligible.append((arm["coverage"], arm_name))

    verdict = "adopt:" + max(eligible)[1] if eligible else "reject"
    decision = {
        "verdict": verdict,
        "rule": (
            f"coverage gain >= +{COVERAGE_GAIN_BAR} AND qd_score >= "
            f"{QD_COST_FACTOR} x baseline; highest-coverage adoptable "
            "arm wins; otherwise reject (DR 0040, pre-registered)"
        ),
        "reason": (
            "an arm met both pre-registered bars"
            if eligible
            else "no arm met both pre-registered bars — the loop "
            "keeps its baseline selection; novelty-first stays a "
            "recorded instrument finding"
        ),
    }

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete",
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 20 J3 (DR 0040): the I5b novelty lever judged at "
            "the surface that owns the trade — the E3 evolution loop "
            "at the documented budget, three arms, pre-registered "
            "bars, the decision on the numbers."
        ),
        "source_artifacts": [
            "labs/map_elites_archive/evaluation_loop_scale.py",
            "data/archives/occupancy_saturation_stage0.json",
            "research/decision_records/0040-novelty-first-evolution-surface.md",
        ],
        "parameters": {
            "population": population,
            "target_evaluations": target_evaluations,
            "rng_seed": rng_seed,
            "lifecycle_ticks": lifecycle_ticks,
            "pool_factor": pool_factor,
            "coverage_gain_bar": COVERAGE_GAIN_BAR,
            "qd_cost_factor": QD_COST_FACTOR,
        },
        "metrics": {"arms": arms, "levers": levers},
        "closed_states": [
            "novelty_lever_judged_at_the_evolution_surface",
        ],
        "blocked_states": [
            "game_repertoire_wiring_is_the_consumers_increment_on_adopt",
        ],
        "decision": decision,
        "next_research_step": (
            "fill DR 0040's decision section from this artifact; the "
            "loop's default follows the verdict"
        ),
    }


def write_novelty_evolution_artifacts(
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
    parser.add_argument("--population", type=int, default=256)
    parser.add_argument("--target-evaluations", type=int, default=20_480)
    parser.add_argument("--pool-factor", type=int, default=3)
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "archives"
    )
    args = parser.parse_args()
    report = build_novelty_evolution_report(
        population=args.population,
        target_evaluations=args.target_evaluations,
        pool_factor=args.pool_factor,
    )
    written = write_novelty_evolution_artifacts(args.output_dir, report)
    print(f"wrote {written}")
    print(json.dumps(report["metrics"]["levers"], indent=2))
    print(report["decision"]["verdict"])
