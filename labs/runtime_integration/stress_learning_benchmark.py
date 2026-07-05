"""Stress learning benchmark: the learning module's falsifiable bar.

The learning candidate is the feedback-enabled micro-switchboard: the
lifecycle state carries per-action reward histories, `run_switchboard`
selects actions from them, and feedback means letting observed rewards
update those histories online. Prior evidence
(`data/micro_learners/switchboard_lifecycle_feedback_stage0.json`)
measured survival delta 0 — the old sheltered saturation hid the answer.

This lab reruns the comparison where survival actually varies: generated
candidates evaluated on the archive's contracted morphology stress probe
(the regime from `2026-07-05-stress-regime-evolution.md`). Both arms use
the exact tick machinery of the original feedback lab — identical
miscalibrated reward start, identical switchboard, identical
`advance_tick` — differing ONLY in whether observed rewards update the
action histories. Whatever the numbers say becomes decision record 0009's
evidence; a learning module is promotable only against a measured bar.
"""

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[2]
LAB_DIR = Path(__file__).resolve().parent
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
GRID_GENOME = ROOT / "labs" / "grid_genome"
LIFECYCLE = ROOT / "labs" / "lifecycle_sim"
for path in [LAB_DIR, PACKAGE_SRC, GRID_GENOME, LIFECYCLE]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from corpus_builder import build_seed_grids  # noqa: E402
from lifecycle_sim import advance_tick, initial_lifecycle_state  # noqa: E402
from micro_switchboard import run_switchboard  # noqa: E402
from slip import is_grid_aligned  # noqa: E402

# The benchmark must share the original feedback lab's reward
# miscalibration exactly, or the learning-room premise would differ
# between the sheltered and stress measurements — hence the deliberate
# import of its private helper.
from switchboard_feedback import _miscalibrate_rewards  # noqa: E402

from mecha_engine.generation import (  # noqa: E402
    generate_candidate,
    train_generation_model,
)

from mecha_engine_runtime_loop import _stress_probe  # noqa: E402


ARTIFACT_ID = "stress_learning_benchmark_stage0"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "runtime_integration"
SLIP_PROFILE_PATH = ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
SOURCE_REFS = [
    {
        "name": "A Contextual-Bandit Approach to Personalized News Article Recommendation",
        "url": "https://arxiv.org/abs/1003.0146",
        "use": "Reference for updating action preferences from observed contextual rewards.",
    },
    {
        "name": "Reinforcement Learning: An Introduction",
        "url": "http://incompleteideas.net/book/the-book-2nd.html",
        "use": "Reference for reward signals and action-value style learning.",
    },
]


def _policy_episode(
    probed_grid: dict,
    slip_profile: dict,
    *,
    ticks: int,
    feedback_enabled: bool,
) -> dict:
    """One deterministic episode, mirroring the original feedback lab.

    The frozen arm resets the action-reward histories after every tick, so
    the switchboard keeps deciding from the same miscalibrated start; the
    feedback arm lets observed rewards accumulate. Everything else is
    identical.
    """
    state = initial_lifecycle_state(probed_grid, slip_profile)
    state = _miscalibrate_rewards(state)
    initial_rewards = deepcopy(state["action_rewards"])
    balances = []
    reward_update_count = 0
    for _ in range(ticks):
        if not state["alive"]:
            break
        action = run_switchboard(state)["action"]
        next_state = advance_tick(state, action)
        if feedback_enabled:
            reward_update_count += 1
        else:
            next_state["action_rewards"] = deepcopy(initial_rewards)
        balances.append(next_state["history"][-1]["balance"])
        state = next_state
    if balances and len(balances) < ticks:
        balances = balances + [0.0] * (ticks - len(balances))
    return {
        "survival_ticks": state["age_ticks"],
        "survival_ratio": round(state["age_ticks"] / ticks, 6) if ticks else 0.0,
        "alive": state["alive"],
        "death_cause": state["death_cause"],
        "need_balance": round(mean(balances), 6) if balances else 0.0,
        "recovery_events": state["recovery_events"],
        "reward_update_count": reward_update_count,
    }


def run_stress_learning_benchmark(
    *,
    count: int = 24,
    ticks: int = 72,
    rng_seed: int = 20260512,
) -> dict:
    """Feedback vs frozen switchboard over stress-probed morphologies."""
    slip_profile = json.loads(SLIP_PROFILE_PATH.read_text(encoding="utf-8"))
    seeds = build_seed_grids()
    generation_model = train_generation_model(seeds)
    pool = [seed for seed in seeds if is_grid_aligned(seed, slip_profile).ok]
    if not pool:
        raise ValueError("no seed grid satisfies the SLIP profile")

    records = []
    for index in range(count):
        candidate = generate_candidate(
            pool[index % len(pool)],
            generation_model,
            slip_profile,
            rng_seed=rng_seed + index,
        )
        probed, load = _stress_probe(candidate)
        feedback = _policy_episode(
            probed, slip_profile, ticks=ticks, feedback_enabled=True
        )
        frozen = _policy_episode(
            probed, slip_profile, ticks=ticks, feedback_enabled=False
        )
        records.append(
            {
                "candidate_grid_id": candidate["grid_id"],
                "stress_load": load,
                "feedback": feedback,
                "frozen": frozen,
                "survival_delta_ticks": feedback["survival_ticks"]
                - frozen["survival_ticks"],
                "need_balance_delta": round(
                    feedback["need_balance"] - frozen["need_balance"], 6
                ),
            }
        )

    summary = _benchmark_summary(records)
    return {
        "lab_id": ARTIFACT_ID,
        "date": "2026-07-05",
        "rng_seed": rng_seed,
        "count": count,
        "ticks": ticks,
        "survival_regime": "stress_probe",
        "purpose": (
            "Measure the learning candidate (feedback-enabled "
            "micro-switchboard) against the frozen switchboard where "
            "survival is morphology-dependent — the falsifiable bar for "
            "decision record 0009."
        ),
        "source_artifacts": [
            "data/micro_learners/switchboard_lifecycle_feedback_stage0.json",
            "data/runtime_integration/mecha_engine_evolution_hard_regime_stage0.json",
        ],
        "candidates": records,
        "summary": summary,
        "decision": _benchmark_decision(summary),
        "limitations": [
            "The learner is the Stage 0 reward-mean switchboard, not a contextual bandit or deeper learner; this benchmark bounds THIS candidate, not learning in general.",
            "Both arms start from the original lab's deliberate reward miscalibration, preserving the learnable-gap premise for comparability.",
            "Single-episode evaluation per morphology; no cross-episode transfer is claimed.",
        ],
        "source_refs": SOURCE_REFS,
    }


def _benchmark_summary(records: list[dict]) -> dict:
    count = len(records)
    feedback_alive = sum(1 for r in records if r["feedback"]["alive"])
    frozen_alive = sum(1 for r in records if r["frozen"]["alive"])
    return {
        "count": count,
        "mean_stress_load": round(
            sum(r["stress_load"] for r in records) / count, 6
        ),
        "feedback_survival_rate": round(feedback_alive / count, 6),
        "frozen_survival_rate": round(frozen_alive / count, 6),
        "mean_survival_ratio_feedback": round(
            sum(r["feedback"]["survival_ratio"] for r in records) / count, 6
        ),
        "mean_survival_ratio_frozen": round(
            sum(r["frozen"]["survival_ratio"] for r in records) / count, 6
        ),
        "mean_survival_ratio_delta": round(
            sum(
                r["feedback"]["survival_ratio"] - r["frozen"]["survival_ratio"]
                for r in records
            )
            / count,
            6,
        ),
        "mean_need_balance_delta": round(
            sum(r["need_balance_delta"] for r in records) / count, 6
        ),
        "saved_by_feedback_count": sum(
            1
            for r in records
            if r["feedback"]["alive"] and not r["frozen"]["alive"]
        ),
        "lost_by_feedback_count": sum(
            1
            for r in records
            if not r["feedback"]["alive"] and r["frozen"]["alive"]
        ),
    }


def _benchmark_decision(summary: dict) -> dict:
    beats_survival = (
        summary["feedback_survival_rate"] > summary["frozen_survival_rate"]
    )
    beats_need_balance = summary["mean_need_balance_delta"] > 0
    if beats_survival:
        status = "learning_beats_frozen_under_stress"
        reason = (
            "Online reward feedback keeps more morphologies alive than the "
            "frozen switchboard under the stress regime "
            f"({summary['feedback_survival_rate']} vs "
            f"{summary['frozen_survival_rate']}; "
            f"{summary['saved_by_feedback_count']} saved, "
            f"{summary['lost_by_feedback_count']} lost). The learning "
            "module's promotion claim has measured support."
        )
    elif summary["feedback_survival_rate"] == summary["frozen_survival_rate"]:
        status = "learning_matches_frozen_under_stress"
        reason = (
            "Feedback neither saves nor loses morphologies relative to the "
            "frozen switchboard under stress; survival is decided by the "
            "morphology load, not the policy. Need-balance remains the "
            "only measured learning benefit "
            f"(delta {summary['mean_need_balance_delta']}). A learning "
            "module promotion cannot claim survival improvement on this "
            "evidence."
        )
    else:
        status = "learning_loses_to_frozen_under_stress"
        reason = (
            "Online reward feedback keeps FEWER morphologies alive than "
            "the frozen switchboard under stress "
            f"({summary['feedback_survival_rate']} vs "
            f"{summary['frozen_survival_rate']}). A negative result, "
            "recorded as first-class evidence: this learning candidate "
            "must not be promoted on a survival claim."
        )
    return {
        "status": status,
        "adoption": "evidence_for_decision_record_0009",
        "reason": reason,
        "thresholds": {
            "feedback_beats_frozen_survival": beats_survival,
            "feedback_beats_frozen_need_balance": beats_need_balance,
        },
    }


def write_stress_learning_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{ARTIFACT_ID}.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    summary = report["summary"]
    (output_dir / "stress_learning_README.md").write_text(
        "# Stress Learning Benchmark Stage 0\n\n"
        "Feedback-enabled vs frozen micro-switchboard over stress-probed "
        "morphologies — the learning module's falsifiable bar (decision "
        "record 0009 evidence).\n\n"
        "Key results:\n\n"
        f"- Candidates: {summary['count']} at {report['ticks']} ticks "
        f"(mean stress load {summary['mean_stress_load']})\n"
        f"- Survival rate: feedback {summary['feedback_survival_rate']} vs "
        f"frozen {summary['frozen_survival_rate']}\n"
        f"- Mean survival-ratio delta: {summary['mean_survival_ratio_delta']}\n"
        f"- Mean need-balance delta: {summary['mean_need_balance_delta']}\n"
        f"- Saved / lost by feedback: {summary['saved_by_feedback_count']} / "
        f"{summary['lost_by_feedback_count']}\n"
        f"- Decision: {report['decision']['status']}\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the stress learning benchmark."
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--count", type=int, default=24)
    parser.add_argument("--ticks", type=int, default=72)
    parser.add_argument("--rng-seed", type=int, default=20260512)
    args = parser.parse_args()
    report = run_stress_learning_benchmark(
        count=args.count, ticks=args.ticks, rng_seed=args.rng_seed
    )
    write_stress_learning_artifacts(args.output_dir, report)
    print(json.dumps(report["summary"], indent=2))
    print(json.dumps(report["decision"], indent=2))


if __name__ == "__main__":
    main()
