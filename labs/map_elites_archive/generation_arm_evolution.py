"""Cycle 21 K2: the generation layer revisited in the loop (DR 0042).

The regenerated 16x16 bake-off flipped to constrained-wins by DR 0031's
own pre-registered one-shot rule — but cycle 20's J3 measured that
one-shot verdicts can dissolve in the loop, and the WFC adoption's real
consumer IS the loop (the E3 evolution surface the game's repertoire
inherits). So the revisit is judged at the consumer: both generation
arms run the FULL loop as adopted (novelty-first selection, DR 0040) at
the matched documented budget, and the rule is pre-registered and
incumbent-favoring: `constrained` becomes the loop's generation default
ONLY IF coverage gain >= +0.02 AND qd_score >= 0.95 x the WFC arm;
otherwise WFC stands where it is consumed and the bake-off flip is
recorded as one-shot-only evidence. The elites' role texture rides as a
recorded observation, never a gate.
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

ARTIFACT_ID = "generation_arm_evolution_stage0"
REPORT_DATE = "2026-07-21"
# DR 0042's pre-registered bars — DR 0040's, verbatim; wfc incumbent.
COVERAGE_GAIN_BAR = 0.02
QD_COST_FACTOR = 0.95
ARMS = ("wfc", "constrained")


def build_generation_arm_report(
    *,
    population: int = 256,
    target_evaluations: int = 20_480,
    rng_seed: int = DEFAULT_RNG_SEED,
    lifecycle_ticks: int = DEFAULT_LIFECYCLE_TICKS,
) -> dict:
    arms: dict[str, dict] = {}
    for arm_name in ARMS:
        started = time.perf_counter()
        result = run_evaluation_loop(
            population=population,
            target_evaluations=target_evaluations,
            rng_seed=rng_seed,
            lifecycle_ticks=lifecycle_ticks,
            generation=arm_name,
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
            "collapse_failures_total": sum(
                entry["collapse_failures"]
                for entry in result["trajectory"]
            ),
            "elite_role_summary": result["elite_role_summary"],
            "wall_clock_s": round(time.perf_counter() - started, 3),
            "final_trajectory_entry": result["trajectory"][-1]
            if result["trajectory"]
            else None,
        }

    incumbent = arms["wfc"]
    challenger = arms["constrained"]
    gain = round(challenger["coverage"] - incumbent["coverage"], 6)
    qd_ratio = (
        round(challenger["qd_score"] / incumbent["qd_score"], 6)
        if incumbent["qd_score"]
        else 0.0
    )
    meets_gain = gain >= COVERAGE_GAIN_BAR
    meets_qd = (
        challenger["qd_score"] >= QD_COST_FACTOR * incumbent["qd_score"]
    )
    lever = {
        "coverage_gain": gain,
        "qd_ratio": qd_ratio,
        "meets_coverage_gain_bar": meets_gain,
        "meets_qd_cost_bar": meets_qd,
    }
    adoptable = meets_gain and meets_qd
    decision = {
        "verdict": "adopt:constrained" if adoptable else "reject",
        "rule": (
            f"constrained vs the wfc incumbent: coverage gain >= "
            f"+{COVERAGE_GAIN_BAR} AND qd_score >= {QD_COST_FACTOR} x "
            "wfc; otherwise the incumbent stands at its consumer "
            "(DR 0042, pre-registered; ties favor the incumbent)"
        ),
        "reason": (
            "the challenger met both pre-registered bars in the loop"
            if adoptable
            else "the challenger did not meet both bars in the loop — "
            "WFC stands where it is consumed; the flipped one-shot "
            "bake-off is recorded as one-shot-only evidence (the J3 "
            "dissolution, mirrored)"
        ),
    }

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete",
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 21 K2 (DR 0042): DR 0031's revisit judged at its "
            "consumer — both generation arms through the FULL adopted "
            "loop at the matched documented budget, the rule "
            "pre-registered and incumbent-favoring."
        ),
        "source_artifacts": [
            "labs/map_elites_archive/evaluation_loop_scale.py",
            "labs/wfc_grid/wfc_population_throughput.py",
            "data/wfc_grid/generation_bakeoff16_stage0.json",
            "research/decision_records/0042-generation-layer-loop-revisit.md",
            "research/decision_records/0031-wfc-generation-adoption.md",
            "research/decision_records/0040-novelty-first-evolution-surface.md",
        ],
        "parameters": {
            "population": population,
            "target_evaluations": target_evaluations,
            "rng_seed": rng_seed,
            "lifecycle_ticks": lifecycle_ticks,
            "selection": "novelty_first (the DR 0040 adopted default)",
            "coverage_gain_bar": COVERAGE_GAIN_BAR,
            "qd_cost_factor": QD_COST_FACTOR,
        },
        "metrics": {"arms": arms, "lever": lever},
        "closed_states": [
            "generation_layer_revisit_judged_in_the_loop",
        ],
        "blocked_states": [
            "one_shot_bakeoff_and_loop_verdicts_reconciled_in_the_"
            "experiment_report",
        ],
        "decision": decision,
        "next_research_step": (
            "fill DR 0042's measured-verdict section from this "
            "artifact; the loop's generation default follows the "
            "verdict; either way both arms stay runnable"
        ),
    }


def write_generation_arm_artifacts(
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
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "archives"
    )
    args = parser.parse_args()
    report = build_generation_arm_report(
        population=args.population,
        target_evaluations=args.target_evaluations,
    )
    written = write_generation_arm_artifacts(args.output_dir, report)
    print(f"wrote {written}")
    print(json.dumps(report["metrics"]["lever"], indent=2))
    print(report["decision"]["verdict"])
