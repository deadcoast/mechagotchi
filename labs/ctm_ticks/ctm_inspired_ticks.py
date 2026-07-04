import argparse
import json
import sys
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME = ROOT / "labs" / "grid_genome"
if str(GRID_GENOME) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME))

from micro_switchboard import ACTIONS, run_switchboard  # noqa: E402


SOURCE_REFS = [
    {
        "name": "Continuous Thought Machines",
        "url": "https://pub.sakana.ai/ctm/",
        "use": "Internal temporal axis, neuron synchronization, and observable reasoning-over-time framing.",
    },
    {
        "name": "SakanaAI continuous-thought-machines",
        "url": "https://github.com/SakanaAI/continuous-thought-machines",
        "use": "Reference implementation and Apache-2.0 license check; no code is reused.",
    },
]


def run_deliberative_switchboard(
    state: dict,
    *,
    max_ticks: int = 4,
    confidence_threshold: float = 0.72,
) -> dict:
    baseline = run_switchboard(state)
    aggregate_utilities = {
        action: float(baseline["utilities"].get(action, 0.0)) for action in ACTIONS
    }
    # Recompute the baseline confidence with the same _clamp(0.5 + margin)
    # formula used by _decision_from_utilities (applied to the baseline
    # utilities before any tick pressure is added), so confidence_gain
    # compares like with like instead of mixing run_switchboard's internal
    # confidence with the deliberative recomputation.
    baseline_confidence = _decision_from_utilities(dict(aggregate_utilities), 1)[
        "confidence"
    ]
    trace = [
        _trace_entry(
            tick=1,
            decision=baseline,
            utilities=aggregate_utilities,
            pressure={action: 0.0 for action in ACTIONS},
            mode="single_pass_switchboard",
        )
    ]
    final_decision = baseline

    for tick in range(2, max(1, max_ticks) + 1):
        if final_decision["confidence"] >= confidence_threshold:
            break
        pressure = _state_pressure(state)
        gain = _tick_gain(tick)
        for action, value in pressure.items():
            aggregate_utilities[action] = aggregate_utilities.get(action, 0.0) + value * gain
        final_decision = _decision_from_utilities(aggregate_utilities, tick)
        trace.append(
            _trace_entry(
                tick=tick,
                decision=final_decision,
                utilities=aggregate_utilities,
                pressure=pressure,
                mode="confidence_gated_internal_tick",
            )
        )

    # Apply the same formula to the final utilities so both sides of the
    # subtraction share one confidence definition. When no extra tick ran the
    # utilities are unchanged and the gain is exactly zero.
    final_confidence = _decision_from_utilities(dict(aggregate_utilities), len(trace))[
        "confidence"
    ]
    return {
        "baseline_decision": baseline,
        "baseline_confidence_like_for_like": baseline_confidence,
        "final_decision": final_decision,
        "tick_count": len(trace),
        "max_ticks": max_ticks,
        "confidence_threshold": confidence_threshold,
        "confidence_gain": round(
            final_confidence - baseline_confidence,
            6,
        ),
        "final_utilities": final_decision["utilities"],
        "trace": trace,
        "source_mode": "ctm_inspired_confidence_gated_ticks",
    }


def run_ctm_tick_lab(
    *,
    max_ticks: int = 4,
    confidence_threshold: float = 0.72,
) -> dict:
    evaluations = []
    for name, scenario in _scenarios().items():
        result = run_deliberative_switchboard(
            scenario["state"],
            max_ticks=max_ticks,
            confidence_threshold=confidence_threshold,
        )
        baseline_action = result["baseline_decision"]["action"]
        final_action = result["final_decision"]["action"]
        evaluations.append(
            {
                "scenario": name,
                "expected_action": scenario["expected_action"],
                "baseline_action": baseline_action,
                "deliberative_action": final_action,
                "baseline_correct": baseline_action == scenario["expected_action"],
                "deliberative_correct": final_action == scenario["expected_action"],
                "baseline_confidence": result["baseline_decision"]["confidence"],
                "deliberative_confidence": result["final_decision"]["confidence"],
                "confidence_gain": result["confidence_gain"],
                "tick_count": result["tick_count"],
                "trace": result["trace"],
            }
        )

    summary = _summary(evaluations)
    return {
        "lab_id": "ctm_inspired_ticks_stage0",
        "date": "2026-05-12",
        "max_ticks": max_ticks,
        "confidence_threshold": confidence_threshold,
        "source_mode": "ctm_inspired_lightweight_internal_ticks",
        "source_note": (
            "This lab does not implement CTM. It adapts the useful CTM idea "
            "of an internal temporal axis into confidence-gated switchboard "
            "ticks and measures whether extra ticks improve decisions."
        ),
        "summary": summary,
        "evaluations": evaluations,
        "decision": _decision(summary),
        "limitations": [
            "No neural CTM architecture or synchronization training is used.",
            "State pressure is hand-authored and deterministic.",
            "The scenario set is small and synthetic.",
            "No user-facing latency or animation readability test is included.",
        ],
        "source_refs": SOURCE_REFS,
    }


def write_ctm_tick_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "ctm_inspired_ticks_stage0.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")


def _state_pressure(state: dict) -> dict[str, float]:
    hunger = _clamp(state.get("hunger", 0.5))
    energy = _clamp(state.get("energy", 0.5))
    bond = _clamp(state.get("bond", 0.5))
    stress = _clamp(state.get("stress", 0.0))
    stability = _clamp(state.get("grid_stability", 0.5))
    interaction = _interaction_ewma(state.get("recent_interactions", []))
    return {
        "feed": round(hunger * 0.22, 6),
        "sleep": round((1 - energy) * 0.22, 6),
        "play": round(bond * 0.12 + interaction * 0.18 + (1 - stress) * 0.05, 6),
        "idle": round(stress * 0.14 + (1 - interaction) * 0.05, 6),
        "mutate": round((stability - stress) * 0.12, 6),
    }


def _tick_gain(tick: int) -> float:
    return round(0.55 / tick, 6)


def _decision_from_utilities(utilities: dict[str, float], tick: int) -> dict:
    sorted_actions = sorted(utilities.items(), key=lambda item: item[1], reverse=True)
    action, top_score = sorted_actions[0]
    next_score = sorted_actions[1][1] if len(sorted_actions) > 1 else 0.0
    margin = top_score - next_score
    return {
        "action": action,
        "confidence": round(_clamp(0.5 + margin), 6),
        "utilities": {key: round(value, 6) for key, value in sorted(utilities.items())},
        "explanation": (
            f"Selected {action} after {tick} confidence-gated internal ticks."
        ),
    }


def _trace_entry(
    *,
    tick: int,
    decision: dict,
    utilities: dict[str, float],
    pressure: dict[str, float],
    mode: str,
) -> dict:
    sorted_scores = sorted(utilities.values(), reverse=True)
    margin = sorted_scores[0] - sorted_scores[1] if len(sorted_scores) > 1 else 0.0
    return {
        "tick": tick,
        "mode": mode,
        "action": decision["action"],
        "confidence": decision["confidence"],
        "sync_margin": round(margin, 6),
        "utilities": {key: round(value, 6) for key, value in sorted(utilities.items())},
        "state_pressure": pressure,
    }


def _scenarios() -> dict:
    return {
        "ambiguous_attention": {
            "expected_action": "play",
            "state": {
                "hunger": 0.58,
                "energy": 0.42,
                "bond": 0.6,
                "stress": 0.48,
                "grid_stability": 0.66,
                "recent_interactions": [1, 0, 1, 0, 1],
                "action_rewards": {
                    "feed": [0.5],
                    "play": [0.55],
                    "sleep": [0.52],
                    "idle": [0.48],
                    "mutate": [0.5],
                },
            },
        },
        "low_energy": {
            "expected_action": "sleep",
            "state": {
                "hunger": 0.18,
                "energy": 0.08,
                "bond": 0.45,
                "stress": 0.3,
                "grid_stability": 0.8,
                "recent_interactions": [0, 0, 1, 0, 0],
                "action_rewards": {
                    "feed": [0.3],
                    "play": [0.2],
                    "sleep": [0.9, 0.8],
                    "idle": [0.5],
                },
            },
        },
        "hungry_uncertain_rewards": {
            "expected_action": "feed",
            "state": {
                "hunger": 0.78,
                "energy": 0.48,
                "bond": 0.4,
                "stress": 0.22,
                "grid_stability": 0.86,
                "recent_interactions": [0, 1, 0, 0, 1],
                "action_rewards": {
                    "feed": [0.54],
                    "play": [0.52],
                    "sleep": [0.48],
                    "idle": [0.45],
                    "mutate": [0.5],
                },
            },
        },
        "stress_recovery": {
            "expected_action": "idle",
            "state": {
                "hunger": 0.42,
                "energy": 0.5,
                "bond": 0.35,
                "stress": 0.78,
                "grid_stability": 0.28,
                "recent_interactions": [0, 0, 0, 1, 0],
                "action_rewards": {
                    "feed": [0.5],
                    "play": [0.44],
                    "sleep": [0.52],
                    "idle": [0.62],
                    "mutate": [0.2],
                },
            },
        },
    }


def _summary(evaluations: list[dict]) -> dict:
    return {
        "scenario_count": len(evaluations),
        "baseline_accuracy": _rate(item["baseline_correct"] for item in evaluations),
        "deliberative_accuracy": _rate(
            item["deliberative_correct"] for item in evaluations
        ),
        "mean_baseline_confidence": _mean(
            item["baseline_confidence"] for item in evaluations
        ),
        "mean_deliberative_confidence": _mean(
            item["deliberative_confidence"] for item in evaluations
        ),
        "mean_confidence_gain": _mean(item["confidence_gain"] for item in evaluations),
        "mean_tick_count": _mean(item["tick_count"] for item in evaluations),
        "extra_tick_case_count": sum(1 for item in evaluations if item["tick_count"] > 1),
        "decision_change_count": sum(
            1
            for item in evaluations
            if item["baseline_action"] != item["deliberative_action"]
        ),
    }


def _decision(summary: dict) -> dict:
    keep = (
        summary["deliberative_accuracy"] >= summary["baseline_accuracy"]
        and summary["mean_confidence_gain"] > 0
        and summary["extra_tick_case_count"] > 0
    )
    return {
        "status": "prototype" if keep else "watch",
        "adoption": "concept_only_no_ctm_dependency",
        "reason": (
            "Confidence-gated ticks improved decision confidence without "
            "reducing scenario accuracy, so the idea is useful as a small "
            "switchboard mechanism."
            if keep
            else "The tick wrapper did not improve enough over the single-pass "
            "switchboard to justify integration."
        ),
    }


def _interaction_ewma(interactions: list) -> float:
    value = 0.0
    alpha = 0.45
    for event in interactions:
        value = alpha * _clamp(event) + (1 - alpha) * value
    return round(value, 6)


def _rate(values) -> float:
    items = list(values)
    return round(sum(1 for item in items if item) / len(items), 6) if items else 0.0


def _mean(values) -> float:
    items = list(values)
    return round(mean(items), 6) if items else 0.0


def _clamp(value: object) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0.0
    return max(0.0, min(1.0, number))


def _readme_text(report: dict) -> str:
    summary = report["summary"]
    return (
        "# CTM-Inspired Internal Ticks Stage 0\n\n"
        "Lightweight confidence-gated switchboard ticks inspired by CTM's "
        "internal temporal-axis framing. No CTM code or model is used.\n\n"
        "Key results:\n\n"
        f"- Scenarios: {summary['scenario_count']}\n"
        f"- Baseline accuracy: {summary['baseline_accuracy']}\n"
        f"- Deliberative accuracy: {summary['deliberative_accuracy']}\n"
        f"- Mean confidence gain: {summary['mean_confidence_gain']}\n"
        f"- Extra-tick cases: {summary['extra_tick_case_count']}\n"
        f"- Decision: {report['decision']['status']}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("data/ctm_ticks"))
    parser.add_argument("--max-ticks", type=int, default=4)
    parser.add_argument("--confidence-threshold", type=float, default=0.72)
    args = parser.parse_args()
    report = run_ctm_tick_lab(
        max_ticks=args.max_ticks,
        confidence_threshold=args.confidence_threshold,
    )
    write_ctm_tick_artifacts(args.output_dir, report)
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
