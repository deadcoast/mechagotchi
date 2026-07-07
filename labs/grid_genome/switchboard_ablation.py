"""Micro-learner remove-one ablation (audit T19, RUN TWO's design).

Stage 0 scale, honestly bounded: five deterministic synthetic user
models x six SLIP-authored conditions x one seed creature x one episode
each. The conditions ARE `learning_switches` profiles (rung T3.3's
harness): full switchboard, remove-one per thread, rules-only (all off).
RUN TWO's full protocol (500 lifecycles per cell, variance analysis) is
the scale-up; this lab delivers the mechanism, the measured keep-gate,
and the og "full switchboard beats rules-only" headline as numbers.

Keep-gate (og Layer 6 / RUN TWO): a thread is KEPT only if removing it
costs >= 5% need-balance under at least one user model WITHOUT improving
survival — measured from the episode deltas, never asserted.

Synthetic user models (deterministic tick patterns, no RNG):

- attentive   — interacts every tick.
- neglectful  — never interacts.
- erratic     — interacts on a 3-tick on/off-off cycle.
- punitive    — interacts every 4th tick and each interaction adds
  +0.08 stress (rough handling).
- exploratory — interacts on alternating ticks.
"""

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = ROOT / "data" / "micro_learners"
LIFECYCLE = ROOT / "labs" / "lifecycle_sim"
if str(LIFECYCLE) not in sys.path:
    sys.path.insert(0, str(LIFECYCLE))

from corpus_builder import build_seed_grids  # noqa: E402
from lifecycle_sim import advance_tick, initial_lifecycle_state  # noqa: E402
from slip import is_grid_aligned  # noqa: E402
from micro_switchboard import (  # noqa: E402
    SWITCHBOARD_THREAD_NAMES,
    run_switchboard,
)


def _user(pattern):
    return pattern


USER_MODELS = {
    "attentive": lambda tick: (1, 0.0),
    "neglectful": lambda tick: (0, 0.0),
    "erratic": lambda tick: (1 if tick % 3 == 0 else 0, 0.0),
    "punitive": lambda tick: (1 if tick % 4 == 0 else 0, 0.08 if tick % 4 == 0 else 0.0),
    "exploratory": lambda tick: (tick % 2, 0.0),
}


def _base_profile() -> dict:
    return json.loads(
        (ROOT / "data/slips/valid/slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )


def _condition_profile(disabled: list[str]) -> dict:
    profile = _base_profile()
    if disabled:
        profile["slip_version"] = "0.2.0"
        profile["profile_id"] = "slip_ablation_" + "_".join(
            name[:6] for name in disabled
        )[:40]
        profile["learning_switches"] = {name: False for name in disabled}
    return profile


ABLATION_CONDITIONS = [
    {"condition": "full", "profile": _condition_profile([])},
    *[
        {
            "condition": f"minus_{name}",
            "profile": _condition_profile([name]),
        }
        for name in SWITCHBOARD_THREAD_NAMES
    ],
    {
        "condition": "rules_only",
        "profile": _condition_profile(list(SWITCHBOARD_THREAD_NAMES)),
    },
]


def _episode(profile: dict, user_model, ticks: int, grid: dict) -> dict:
    state = initial_lifecycle_state(grid, profile)
    balances = []
    action_counts = {action: 0 for action in ("feed", "play", "sleep", "idle", "mutate")}
    for tick in range(1, ticks + 1):
        if not state["alive"]:
            break
        interaction, stress_bump = user_model(tick)
        window = state.get("recent_interactions", [])[-4:] + [interaction]
        state["recent_interactions"] = window
        if stress_bump:
            state["stress"] = min(1.0, state["stress"] + stress_bump)
        action = run_switchboard(state)["action"]
        action_counts[action] += 1
        state = advance_tick(state, action)
        balances.append(state["history"][-1]["balance"])
    if balances and len(balances) < ticks:
        balances = balances + [0.0] * (ticks - len(balances))
    return {
        "survival_ticks": state["age_ticks"],
        "alive": state["alive"],
        "need_balance": round(mean(balances), 6) if balances else 0.0,
        "recovery_events": state["recovery_events"],
        "action_counts": action_counts,
    }


def build_switchboard_ablation_report(
    *, ticks: int = 48, creature_count: int = 1
) -> dict:
    """creature_count > 1 is the T19 scaled rerun: episodes run per seed
    creature and the keep-gate uses per-user MEAN declines with variance
    reported — the honest step toward RUN TWO's 500-lifecycle protocol.
    """
    base = _base_profile()
    creatures = [
        seed
        for seed in build_seed_grids()
        if is_grid_aligned(seed, base).ok
    ][:creature_count]
    episodes = []
    # table[user][condition] -> list of per-creature episodes
    table: dict[str, dict[str, list[dict]]] = {}
    for user_name, user_model in USER_MODELS.items():
        for condition in ABLATION_CONDITIONS:
            for grid in creatures:
                episode = _episode(
                    deepcopy(condition["profile"]), user_model, ticks, grid
                )
                episode.update(
                    {
                        "user_model": user_name,
                        "condition": condition["condition"],
                        "creature": grid["grid_id"],
                    }
                )
                episodes.append(episode)
                table.setdefault(user_name, {}).setdefault(
                    condition["condition"], []
                ).append(episode)

    from statistics import pstdev

    keep_gate = {}
    for thread in SWITCHBOARD_THREAD_NAMES:
        mean_declines = []
        all_declines = []
        survival_improved = False
        for user_name in USER_MODELS:
            pair_declines = []
            for full, removed in zip(
                table[user_name]["full"],
                table[user_name]["minus_" + thread],
            ):
                base = full["need_balance"] or 1e-9
                pair_declines.append(
                    (full["need_balance"] - removed["need_balance"])
                    / base
                    * 100
                )
                if removed["survival_ticks"] > full["survival_ticks"]:
                    survival_improved = True
            mean_declines.append(round(mean(pair_declines), 3))
            all_declines.extend(pair_declines)
        worst = max(mean_declines)
        keep_gate[thread] = {
            "mean_need_balance_decline_pct_by_user": dict(
                zip(USER_MODELS, mean_declines)
            ),
            "worst_mean_decline_pct": worst,
            "decline_stdev_pct": round(pstdev(all_declines), 3)
            if len(all_declines) > 1
            else 0.0,
            "survival_improved_when_removed": survival_improved,
            "decision": (
                "keep"
                if worst >= 5.0 and not survival_improved
                else "dead_weight"
            ),
        }

    headline_deltas = {}
    for user_name in USER_MODELS:
        full = mean(e["need_balance"] for e in table[user_name]["full"])
        rules = mean(
            e["need_balance"] for e in table[user_name]["rules_only"]
        ) or 1e-9
        headline_deltas[user_name] = round((full - rules) / rules * 100, 3)

    scaled = creature_count > 1
    return {
        "artifact_id": (
            "switchboard_ablation_scaled_stage0"
            if scaled
            else "switchboard_ablation_stage0"
        ),
        "status": "stage0_complete",
        "date": "2026-07-05",
        "purpose": (
            "RUN TWO's remove-one switchboard ablation at Stage 0 scale: "
            "SLIP-authored conditions (T3.3 learning_switches), five "
            "synthetic user models, measured keep-gate per thread and the "
            "full-vs-rules-only headline (audit T19)."
        ),
        "ticks": ticks,
        "creature_count": creature_count,
        "source_artifacts": [
            "research/micro_learners/thread_census.md",
            "research/decision_records/0012-slip-schema-extension-ladder.md",
        ],
        "episodes": episodes,
        "keep_gate": keep_gate,
        "summary": {
            "episode_count": len(episodes),
            "full_vs_rules_only": {
                "need_balance_delta_pct_by_user": headline_deltas,
                "full_beats_rules_only": all(
                    delta > 0 for delta in headline_deltas.values()
                ),
            },
            "keep_decisions": {
                thread: verdict["decision"]
                for thread, verdict in keep_gate.items()
            },
        },
        "limitations": [
            "Stage 0 scale: one seed creature, one deterministic episode per cell (RUN TWO's 500-lifecycle protocol with variance analysis is the scale-up).",
            "Synthetic user models are deterministic tick patterns, not learned user behavior.",
            "A dead_weight verdict at this scale queues the thread for the scaled rerun before any removal.",
        ],
        "next_research_step": (
            "Scale the grid (creatures x lifecycles) and add variance "
            "before acting on dead_weight verdicts; wire the boredom "
            "predictor (census gap 1) into the same harness."
        ),
    }


def write_switchboard_ablation_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / (report["artifact_id"] + ".json")).write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the switchboard ablation.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--ticks", type=int, default=48)
    parser.add_argument("--creatures", type=int, default=1)
    args = parser.parse_args()
    report = build_switchboard_ablation_report(
        ticks=args.ticks, creature_count=args.creatures
    )
    write_switchboard_ablation_artifacts(args.output_dir, report)
    print(json.dumps(report["summary"], indent=2))
    print(json.dumps(report["keep_gate"], indent=2))


if __name__ == "__main__":
    main()
