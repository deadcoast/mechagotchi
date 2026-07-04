import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[2]
LIFECYCLE = ROOT / "labs" / "lifecycle_sim"
if str(LIFECYCLE) not in sys.path:
    sys.path.insert(0, str(LIFECYCLE))

from corpus_builder import build_seed_grids  # noqa: E402
from lifecycle_sim import advance_tick, initial_lifecycle_state  # noqa: E402
from micro_switchboard import ACTIONS, run_switchboard  # noqa: E402


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


def run_feedback_episode(
    *,
    ticks: int = 48,
    feedback_enabled: bool = True,
    rng_seed: int = 20260512,
    scenario: dict | None = None,
) -> dict:
    grid = build_seed_grids()[0]
    slip_profile = _load_default_slip()
    state = initial_lifecycle_state(grid, slip_profile)
    state = _miscalibrate_rewards(state)
    state = _apply_state_overrides(state, (scenario or {}).get("initial_state", {}))
    initial_rewards = deepcopy(state["action_rewards"])
    initial_means = _reward_means(initial_rewards)
    history = []
    events_applied = []
    reward_update_count = 0

    for tick_index in range(1, ticks + 1):
        if not state["alive"]:
            break
        for event in (scenario or {}).get("events", []):
            if event.get("tick") == tick_index:
                state = _apply_scenario_event(state, event)
                events_applied.append(
                    {
                        "tick": tick_index,
                        "event_id": event["event_id"],
                        "description": event.get("description", ""),
                    }
                )
        decision = run_switchboard(state)
        action = decision["action"]
        before_means = _reward_means(state["action_rewards"])
        next_state = advance_tick(state, action)
        observed_reward = next_state["action_rewards"][action][-1]

        if feedback_enabled:
            reward_update_count += 1
            after_means = _reward_means(next_state["action_rewards"])
        else:
            next_state["action_rewards"] = deepcopy(initial_rewards)
            after_means = _reward_means(next_state["action_rewards"])

        history.append(
            {
                "tick": next_state["age_ticks"],
                "action": action,
                "decision_confidence": decision["confidence"],
                "observed_reward": observed_reward,
                "need_balance": next_state["history"][-1]["balance"],
                "reward_means_before": before_means,
                "reward_means_after": after_means,
                "alive": next_state["alive"],
                "death_cause": next_state["death_cause"],
            }
        )
        state = next_state

    balances = [entry["need_balance"] for entry in history]
    if balances and len(balances) < ticks:
        balances = balances + [0.0] * (ticks - len(balances))

    return {
        "policy": "feedback_switchboard" if feedback_enabled else "frozen_switchboard",
        "ticks_requested": ticks,
        # rng_seed is recorded for interface parity only: the Stage 0 episode
        # is fully deterministic and no code path consumes the seed (L-03).
        "rng_seed": rng_seed,
        "episode_deterministic": True,
        "survival_ticks": state["age_ticks"],
        "alive": state["alive"],
        "death_cause": state["death_cause"],
        "need_balance": round(mean(balances), 6) if balances else 0.0,
        "recovery_events": state["recovery_events"],
        "action_counts": state["action_counts"],
        "reward_update_count": reward_update_count,
        "initial_action_reward_means": initial_means,
        "final_action_reward_means": _reward_means(state["action_rewards"]),
        "scenario_id": (scenario or {}).get("scenario_id"),
        "events_applied": events_applied,
        "history": history,
    }


def run_switchboard_feedback_lab(
    *,
    ticks: int = 48,
    rng_seed: int = 20260512,
) -> dict:
    feedback = run_feedback_episode(
        ticks=ticks,
        feedback_enabled=True,
        rng_seed=rng_seed,
    )
    frozen = run_feedback_episode(
        ticks=ticks,
        feedback_enabled=False,
        rng_seed=rng_seed,
    )
    summary = {
        "ticks_requested": ticks,
        "feedback_survival_ticks": feedback["survival_ticks"],
        "frozen_survival_ticks": frozen["survival_ticks"],
        "feedback_need_balance": feedback["need_balance"],
        "frozen_need_balance": frozen["need_balance"],
        "feedback_reward_update_count": feedback["reward_update_count"],
        "frozen_reward_update_count": frozen["reward_update_count"],
        "feedback_recovery_events": feedback["recovery_events"],
        "frozen_recovery_events": frozen["recovery_events"],
        "need_balance_delta": round(
            feedback["need_balance"] - frozen["need_balance"],
            6,
        ),
        "survival_delta": feedback["survival_ticks"] - frozen["survival_ticks"],
    }
    return {
        "lab_id": "switchboard_lifecycle_feedback_stage0",
        "date": "2026-05-12",
        "source_grid_id": build_seed_grids()[0]["grid_id"],
        "slip_profile_id": _load_default_slip()["profile_id"],
        "source_mode": "contextual_reward_feedback_switchboard",
        "source_note": (
            "This lab explicitly compares a switchboard that keeps lifecycle "
            "reward updates with one that observes the same rewards but freezes "
            "its action-reward memory. Both policies start from the same stale "
            "idle-favoring reward memory: the frozen policy locks into idle in "
            "the curious-mood band, while the feedback policy corrects the idle "
            "mean from observed lifecycle rewards and resumes active care."
        ),
        "summary": summary,
        "episodes": {
            "feedback_switchboard": feedback,
            "frozen_switchboard": frozen,
        },
        "decision": _decision(summary),
        "limitations": [
            "The reward function is still synthetic and hand-authored.",
            "The scenario starts from a deliberately stale idle-favoring reward memory; "
            "the advantage is specific to miscalibrations the bandit thread can act on.",
            "The bandit thread's utility contribution is capped at +/-0.125 * confidence, "
            "so mood-heuristic-favored miscalibrations (for example stale play rewards) "
            "remain undetectable in this architecture.",
            "The lifecycle reward is dominated by the global need balance, which limits "
            "how sharply the learner can differentiate action quality.",
            "No persisted online learner state is promoted into packages yet.",
            "No human non-annoyance or attachment rating is included.",
        ],
        "source_refs": SOURCE_REFS,
    }


def build_switchboard_feedback_stress_scenarios() -> list[dict]:
    return [
        {
            "scenario_id": "attention_dropout",
            "description": "Starts with recent attention, then removes attention and adds stress.",
            "initial_state": {
                "hunger": 0.46,
                "energy": 0.58,
                "stress": 0.34,
                "bond": 0.62,
                "grid_stability": 0.76,
                "recent_interactions": [1, 1, 1, 1, 1],
            },
            "events": [
                {
                    "tick": 12,
                    "event_id": "attention_stops",
                    "description": "No user interactions arrive for a run of ticks.",
                    "recent_interactions": [0, 0, 0, 0, 0],
                    "state_delta": {"bond": -0.16, "stress": 0.12},
                },
                {
                    "tick": 32,
                    "event_id": "late_attention_returns",
                    "description": "User attention resumes after the bond dip.",
                    "recent_interactions": [0, 1, 0, 1, 1],
                    "state_delta": {"bond": 0.08, "stress": -0.04},
                },
            ],
        },
        {
            "scenario_id": "sleep_debt_then_feed_pressure",
            "description": "Energy debt appears first, followed by hunger pressure.",
            "initial_state": {
                "hunger": 0.38,
                "energy": 0.3,
                "stress": 0.42,
                "bond": 0.55,
                "grid_stability": 0.78,
                "recent_interactions": [1, 0, 0, 1, 0],
            },
            "events": [
                {
                    "tick": 10,
                    "event_id": "energy_crash",
                    "description": "The companion enters a low-energy stretch.",
                    "state_delta": {"energy": -0.18, "stress": 0.08},
                },
                {
                    "tick": 28,
                    "event_id": "hunger_spike",
                    "description": "Hunger rises after recovery from sleep debt.",
                    "state_delta": {"hunger": 0.22, "energy": 0.04},
                },
            ],
        },
        {
            "scenario_id": "overplay_grid_instability",
            "description": "High attention encourages play while stability degrades.",
            "initial_state": {
                "hunger": 0.35,
                "energy": 0.62,
                "stress": 0.22,
                "bond": 0.7,
                "grid_stability": 0.68,
                "recent_interactions": [1, 1, 1, 1, 0],
            },
            "events": [
                {
                    "tick": 14,
                    "event_id": "overplay_fatigue",
                    "description": "Repeated interaction costs energy.",
                    "state_delta": {"energy": -0.16, "stress": 0.1},
                    "recent_interactions": [1, 1, 1, 1, 1],
                },
                {
                    "tick": 36,
                    "event_id": "grid_instability",
                    "description": "Grid stability drops and mutation risk should be suppressed.",
                    "state_delta": {"grid_stability": -0.22, "stress": 0.1},
                },
            ],
        },
    ]


def run_switchboard_feedback_stress_suite(
    *,
    ticks: int = 60,
    rng_seed: int = 20260512,
) -> dict:
    scenario_reports = []
    for scenario in build_switchboard_feedback_stress_scenarios():
        feedback = run_feedback_episode(
            ticks=ticks,
            feedback_enabled=True,
            rng_seed=rng_seed,
            scenario=scenario,
        )
        frozen = run_feedback_episode(
            ticks=ticks,
            feedback_enabled=False,
            rng_seed=rng_seed,
            scenario=scenario,
        )
        comparison = {
            "need_balance_delta": round(
                feedback["need_balance"] - frozen["need_balance"],
                6,
            ),
            "survival_delta": feedback["survival_ticks"] - frozen["survival_ticks"],
            "recovery_delta": feedback["recovery_events"] - frozen["recovery_events"],
            "feedback_reward_update_count": feedback["reward_update_count"],
            "frozen_reward_update_count": frozen["reward_update_count"],
        }
        scenario_reports.append(
            {
                "scenario_id": scenario["scenario_id"],
                "description": scenario["description"],
                "events_applied": feedback["events_applied"],
                "comparison": comparison,
                "episodes": {
                    "feedback_switchboard": feedback,
                    "frozen_switchboard": frozen,
                },
            }
        )

    deltas = [scenario["comparison"]["need_balance_delta"] for scenario in scenario_reports]
    survival_deltas = [
        scenario["comparison"]["survival_delta"] for scenario in scenario_reports
    ]
    summary = {
        "ticks_requested": ticks,
        "scenario_count": len(scenario_reports),
        "dynamic_event_count": sum(
            len(scenario["events_applied"]) for scenario in scenario_reports
        ),
        "feedback_better_need_balance_count": sum(1 for delta in deltas if delta > 0),
        "feedback_tied_need_balance_count": sum(1 for delta in deltas if delta == 0),
        "feedback_worse_need_balance_count": sum(1 for delta in deltas if delta < 0),
        "mean_need_balance_delta": round(mean(deltas), 6) if deltas else 0.0,
        "feedback_better_survival_count": sum(
            1 for delta in survival_deltas if delta > 0
        ),
        "feedback_worse_survival_count": sum(
            1 for delta in survival_deltas if delta < 0
        ),
    }
    return {
        "lab_id": "switchboard_feedback_dynamic_stress_stage0",
        "date": "2026-05-12",
        "source_mode": "dynamic_need_and_interaction_stress",
        "summary": summary,
        "scenarios": scenario_reports,
        "decision": _stress_decision(summary),
        "limitations": [
            "Stress events are deterministic and hand-authored.",
            "No real user interaction traces are included.",
            "The feedback memory is still per-episode and is not persisted.",
            "Human non-annoyance and attachment ratings remain absent.",
        ],
        "source_refs": SOURCE_REFS,
    }


def write_switchboard_feedback_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "switchboard_lifecycle_feedback_stage0.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")


def write_switchboard_feedback_stress_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "switchboard_feedback_dynamic_stress_stage0.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "switchboard_feedback_dynamic_stress_README.md").write_text(
        _stress_readme_text(report),
        encoding="utf-8",
    )


def _miscalibrate_rewards(state: dict) -> dict:
    """Install a stale, behaviorally harmful action-reward memory.

    The memory claims idling is the most rewarding action (as if calibrated
    during an earlier quiet phase), while the other actions carry flat,
    uninformative reward means. In the curious-mood band only the bandit
    thread separates idle from active care, so a frozen switchboard acting
    on this memory locks into idle and lets bond and stress drift, while the
    feedback switchboard corrects the idle mean from observed lifecycle
    rewards within roughly a dozen ticks and re-engages.

    Diagnosis of the earlier zero-delta result: the previous revision
    miscalibrated `play` upward instead. Play is already favored by the
    mood and interaction-EWMA threads, whose utility contributions (0.16 to
    0.50) dominate the bandit thread's capped contribution (at most
    +/-0.125 * confidence), so the stale play memory never flipped a single
    action choice and both policies traced identical trajectories.
    """
    updated = deepcopy(state)
    updated["hunger"] = 0.35
    updated["energy"] = 0.45
    updated["stress"] = 0.12
    updated["bond"] = 0.6
    updated["grid_stability"] = 0.85
    updated["recent_interactions"] = [1, 0, 0, 1, 0]
    updated["action_rewards"] = {
        "feed": [0.5],
        "play": [0.5],
        "sleep": [0.5],
        "idle": [0.95, 0.94, 0.96],
        "mutate": [0.5],
    }
    return updated


def _apply_state_overrides(state: dict, overrides: dict) -> dict:
    updated = deepcopy(state)
    for key, value in overrides.items():
        if key == "recent_interactions":
            updated[key] = list(value)
        elif key in {"hunger", "energy", "stress", "bond", "grid_stability"}:
            updated[key] = round(_clamp(value), 6)
        else:
            updated[key] = value
    return updated


def _apply_scenario_event(state: dict, event: dict) -> dict:
    updated = deepcopy(state)
    for key, delta in event.get("state_delta", {}).items():
        if key in {"hunger", "energy", "stress", "bond", "grid_stability"}:
            updated[key] = round(_clamp(float(updated.get(key, 0.0)) + float(delta)), 6)
    if "recent_interactions" in event:
        updated["recent_interactions"] = list(event["recent_interactions"])
    return updated


def _reward_means(rewards: dict) -> dict[str, float]:
    means = {}
    for action in ACTIONS:
        samples = list(rewards.get(action, []))
        means[action] = round(mean(samples), 6) if samples else 0.0
    return means


def _decision(summary: dict) -> dict:
    beats_frozen = (
        summary["feedback_reward_update_count"] > summary["frozen_reward_update_count"]
        and summary["need_balance_delta"] > 0
        and summary["feedback_survival_ticks"] >= summary["frozen_survival_ticks"]
    )
    return {
        "status": "prototype" if beats_frozen else "watch",
        "adoption": "lab_only_feedback_loop",
        "reason": (
            "Lifecycle reward feedback corrects a stale idle-favoring action "
            "memory and strictly improves need balance over the frozen "
            "baseline without reducing survival in this Stage 0 scenario."
            if beats_frozen
            else "Lifecycle reward feedback needs better shaping before it can "
            "beat the frozen switchboard baseline."
        ),
    }


def _stress_decision(summary: dict) -> dict:
    if (
        summary["feedback_better_need_balance_count"]
        > summary["feedback_worse_need_balance_count"]
        and summary["mean_need_balance_delta"] > 0
    ):
        status = "prototype_stress_feedback"
        reason = (
            "Feedback improves mean need balance across the dynamic stress suite, "
            "but remains lab-only until validated on broader traces."
        )
    else:
        status = "watch_reward_shaping"
        reason = (
            "Feedback updates are mechanically active under dynamic stress, but "
            "do not yet clearly beat the frozen baseline."
        )
    return {
        "status": status,
        "adoption": "lab_only_dynamic_stress",
        "reason": reason,
    }


def _load_default_slip() -> dict:
    return json.loads(
        (ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )


def _clamp(value: object) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0.0
    return max(0.0, min(1.0, number))


def _readme_text(report: dict) -> str:
    summary = report["summary"]
    return (
        "# Switchboard Lifecycle Feedback Stage 0\n\n"
        "Compares lifecycle-reward feedback against a frozen action-reward "
        "switchboard baseline.\n\n"
        "Key results:\n\n"
        f"- Ticks requested: {summary['ticks_requested']}\n"
        f"- Feedback need balance: {summary['feedback_need_balance']}\n"
        f"- Frozen need balance: {summary['frozen_need_balance']}\n"
        f"- Feedback reward updates: {summary['feedback_reward_update_count']}\n"
        f"- Frozen reward updates: {summary['frozen_reward_update_count']}\n"
        f"- Decision: {report['decision']['status']}\n"
    )


def _stress_readme_text(report: dict) -> str:
    summary = report["summary"]
    return (
        "# Switchboard Feedback Dynamic Stress Stage 0\n\n"
        "Compares lifecycle-reward feedback against a frozen action-reward "
        "baseline under changing need and user-interaction scenarios.\n\n"
        "Key results:\n\n"
        f"- Scenario count: {summary['scenario_count']}\n"
        f"- Dynamic events: {summary['dynamic_event_count']}\n"
        f"- Feedback better need-balance count: "
        f"{summary['feedback_better_need_balance_count']}\n"
        f"- Feedback worse need-balance count: "
        f"{summary['feedback_worse_need_balance_count']}\n"
        f"- Mean need-balance delta: {summary['mean_need_balance_delta']}\n"
        f"- Decision: {report['decision']['status']}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/micro_learners")
    parser.add_argument("--ticks", type=int, default=48)
    parser.add_argument("--rng-seed", type=int, default=20260512)
    parser.add_argument("--stress", action="store_true")
    args = parser.parse_args()
    if args.stress:
        report = run_switchboard_feedback_stress_suite(
            ticks=args.ticks,
            rng_seed=args.rng_seed,
        )
        write_switchboard_feedback_stress_artifacts(args.output_dir, report)
    else:
        report = run_switchboard_feedback_lab(ticks=args.ticks, rng_seed=args.rng_seed)
        write_switchboard_feedback_artifacts(args.output_dir, report)
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
