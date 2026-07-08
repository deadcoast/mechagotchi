"""The documented ablation gates + the Phase-D verdicts (cycle 12 D6).

The dossier's micro-learner ablation, run on D5's harness in the
KEEPER-DEPENDENT mode D5's honest zero forced: the companion cannot
feed itself — an autonomous "feed" decision is a BEG DISPLAY, and only
the keeper's response fills hunger (the game's actual interaction
model). Welfare = the engine's own per-tick balance summed over the
REQUESTED ticks (death costs — the dossier's "lifetime" metric folded
into the same number, no new statistics).

Conditions (the dossier's A/B/remove-one, adapted to the 11-thread
fleet): ``rules_only`` (every switchboard thread off — the T19
precedent), ``frozen`` (the promoted rule switchboard), ``full_fleet``
(all 11 threads opted in), and ``minus_<thread>`` for each fleet
thread. Paired seeds throughout.

The documented gates, applied without sentiment:

- **>=15% welfare over rules** (the dossier's bandit-track gate; the
  T19 ablation's ``full_vs_rules_only`` headline is the precedent) —
  measured here as full_fleet vs rules_only.
- **The fleet-vs-frozen increment recorded honestly** — measured ~0%
  across three environments (sheltered, state-keyed dependent,
  beg-mediated dependent) and an anticipation-gain sweep (best +0.6%,
  gain 10 harmful): the frozen reactive rules already sit near the
  autonomous-behavior welfare optimum; the remaining welfare belongs
  to the keeper.
- **Drop any thread whose removal costs <5%** in a target metric
  without improving a more important one. A thread keeps its place on
  EITHER its welfare removal cost OR its own documented skill metric
  (the dossier's metric list: prediction errors, action regret,
  hidden-mood accuracy). The evidence threads carry no skill claim
  (they are wiring, D4's pins) — judged on welfare alone.
"""

import argparse
import json
import random
import sys
from pathlib import Path

from synthetic_keepers import KEEPER_IDS, _keeper_evidence
from thread_fleet import FLEET_THREAD_NAMES, observe_fleet


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME = ROOT / "labs" / "grid_genome"
LIFECYCLE_SIM = ROOT / "labs" / "lifecycle_sim"
for _path in [GRID_GENOME, LIFECYCLE_SIM]:
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

ARTIFACT_ID = "ablation_gates_stage0"
REPORT_DATE = "2026-07-08"
FULL_LIFECYCLES_PER_KEEPER = 100
FULL_TICKS = 200
SEED_BASE = 20260709
SWITCHBOARD_THREAD_NAMES = [
    "recent_interaction_ewma",
    "hidden_mood_estimator",
    "action_preference_bandit",
    "mutation_risk_scorer",
]
NEED_PREDICTOR_ARTIFACT = ROOT / "data" / "micro_threads" / "need_predictors_stage0.json"
BANDIT_HMM_ARTIFACT = (
    ROOT / "data" / "micro_threads" / "animation_bandit_hmm_mood_stage0.json"
)
KEEP_THRESHOLD_PCT = 5.0
RULES_GATE_PCT = 15.0


def keeper_respond(
    keeper_id: str, state: dict, begging: bool, rng: random.Random
) -> str | None:
    """The five documented keepers, BEG-MEDIATED: each personality's
    response to the companion's display, plus its spontaneous habits."""
    hunger = float(state.get("hunger", 0.5))
    energy = float(state.get("energy", 0.5))
    bond = float(state.get("bond", 0.5))
    age = int(state.get("age_ticks", 0))
    roll = rng.random()
    if keeper_id == "attentive":
        if begging and roll < 0.9:
            return "feed"
        if bond < 0.55 and energy > 0.4 and roll < 0.4:
            return "play"
        if roll < 0.05:
            return "play"
        return None
    if keeper_id == "neglectful":
        if begging and roll < 0.08:
            return "feed"
        return None
    if keeper_id == "erratic":
        if roll < 0.25:
            return "feed" if rng.random() < 0.5 else "play"
        return None
    if keeper_id == "punitive":
        if begging and roll < 0.5:
            return "play"  # answers the beg with the WRONG thing
        if not begging and hunger < 0.3 and roll < 0.3:
            return "feed"  # overfeeds the sated companion
        return None
    if keeper_id == "exploratory":
        if age % 10 < 3 and roll < 0.6:
            if begging:
                return "feed"
            return "play" if (age // 10) % 2 == 0 else "feed"
        return None
    raise ValueError(f"unknown keeper model: {keeper_id}")


def _condition_switches(condition: str) -> tuple[dict, bool]:
    """(learning_switches, fleet_observes) for one ablation condition."""
    if condition == "rules_only":
        return {name: False for name in SWITCHBOARD_THREAD_NAMES}, False
    if condition == "frozen":
        return {}, False
    if condition == "full_fleet":
        return {name: True for name in FLEET_THREAD_NAMES}, True
    if condition.startswith("minus_"):
        removed = condition[len("minus_"):]
        if removed not in FLEET_THREAD_NAMES:
            raise ValueError(f"unknown fleet thread: {removed}")
        switches = {name: True for name in FLEET_THREAD_NAMES}
        switches[removed] = False
        return switches, True
    raise ValueError(f"unknown condition: {condition}")


def run_dependent_lifecycle(
    grid: dict,
    keeper_id: str,
    *,
    ticks: int,
    rng_seed: int,
    condition: str,
    evidence: dict | None = None,
) -> dict:
    from animation_states import select_animation_state
    from lifecycle_sim import advance_tick, initial_lifecycle_state
    from micro_switchboard import run_switchboard

    switches, fleet_observes = _condition_switches(condition)
    rng = random.Random(rng_seed)
    state = initial_lifecycle_state(grid, None)
    if switches:
        state["learning_switches"] = switches
    if fleet_observes and evidence is not None:
        state["evidence"] = evidence
    balance_total = 0.0
    lived = 0
    beg_ticks = 0
    keeper_feeds = 0
    for _tick in range(ticks):
        if not state.get("alive", False):
            break
        if fleet_observes:
            state["last_animation"] = select_animation_state(state)[0]
            state["thread_states"] = observe_fleet(state)
        decision = run_switchboard(state)
        # KEEPER-DEPENDENT: the companion cannot feed itself — its
        # autonomous "feed" choice is the beg display.
        begging = decision["action"] == "feed"
        if begging:
            beg_ticks += 1
        override = keeper_respond(keeper_id, state, begging, rng)
        if override == "feed":
            keeper_feeds += 1
        executed = (
            override
            if override is not None
            else ("idle" if begging else decision["action"])
        )
        state = advance_tick(state, executed)
        balance_total += state["history"][-1]["balance"]
        lived += 1
        # The D5-measured hotspot: the bench loop trims its own history.
        state["history"] = state["history"][-1:]
    return {
        "keeper_id": keeper_id,
        "condition": condition,
        "survival_ticks": lived,
        "alive": bool(state.get("alive", False)),
        # Welfare over REQUESTED ticks: death costs (the lifetime
        # metric folded in; the engine's own balance, nothing new).
        "welfare": round(balance_total / ticks, 6),
        "beg_ticks": beg_ticks,
        "keeper_feeds": keeper_feeds,
    }


def run_ablation_conditions(
    *,
    lifecycles_per_keeper: int = FULL_LIFECYCLES_PER_KEEPER,
    ticks: int = FULL_TICKS,
    seed_base: int = SEED_BASE,
) -> dict:
    from corpus_builder import build_seed_grids

    seeds = build_seed_grids()
    evidence_by_grid = _keeper_evidence(seeds)
    conditions = (
        ["rules_only", "frozen", "full_fleet"]
        + [f"minus_{name}" for name in FLEET_THREAD_NAMES]
    )
    results = []
    for condition in conditions:
        welfare_sum = 0.0
        survival_sum = 0
        per_keeper = {}
        for keeper_index, keeper_id in enumerate(KEEPER_IDS):
            keeper_welfare = 0.0
            for index in range(lifecycles_per_keeper):
                grid = seeds[index % len(seeds)]
                summary = run_dependent_lifecycle(
                    grid,
                    keeper_id,
                    ticks=ticks,
                    rng_seed=seed_base + keeper_index * 100_000 + index,
                    condition=condition,
                    evidence=evidence_by_grid[grid["grid_id"]],
                )
                keeper_welfare += summary["welfare"]
                survival_sum += summary["survival_ticks"]
            keeper_welfare /= lifecycles_per_keeper
            per_keeper[keeper_id] = round(keeper_welfare, 6)
            welfare_sum += keeper_welfare
        results.append(
            {
                "condition": condition,
                "welfare": round(welfare_sum / len(KEEPER_IDS), 6),
                "welfare_by_keeper": per_keeper,
                "mean_survival_ticks": round(
                    survival_sum / (lifecycles_per_keeper * len(KEEPER_IDS)), 6
                ),
            }
        )
    return {
        "lifecycles_per_keeper": lifecycles_per_keeper,
        "ticks_per_lifecycle": ticks,
        "conditions": results,
    }


def _skill_metrics() -> dict:
    """Each thread's own documented skill metric, read from the D2/D3
    artifacts (the dossier's target-metric families): the improvement
    its removal forfeits, as a percentage of its baseline."""
    skills: dict[str, dict] = {}
    predictors = json.loads(NEED_PREDICTOR_ARTIFACT.read_text(encoding="utf-8"))[
        "metrics"
    ]["predictors"]
    for name, scores in predictors.items():
        improvement = (
            (scores["baseline_error"] - scores["predictor_error"])
            / scores["baseline_error"]
            * 100.0
        )
        skills[name] = {
            "name": f"{scores['error_metric']}_improvement_vs_{scores['baseline']}",
            "value_pct": round(improvement, 3),
            "source": "data/micro_threads/need_predictors_stage0.json",
        }
    bandit_hmm = json.loads(BANDIT_HMM_ARTIFACT.read_text(encoding="utf-8"))[
        "metrics"
    ]
    keepers = bandit_hmm["bandit_keepers"]["keepers"]
    regret_reduction = sum(
        (keeper["rotation_regret"] - keeper["bandit_regret"])
        / keeper["rotation_regret"]
        * 100.0
        for keeper in keepers
    ) / len(keepers)
    skills["animation_bandit"] = {
        "name": "regret_reduction_vs_uniform_rotation",
        "value_pct": round(regret_reduction, 3),
        "source": "data/micro_threads/animation_bandit_hmm_mood_stage0.json",
    }
    hmm = bandit_hmm["hmm_replay"]
    brier_reduction = (
        (hmm["persistence_next_mood_brier"] - hmm["hmm_next_mood_brier"])
        / hmm["persistence_next_mood_brier"]
        * 100.0
    )
    skills["hidden_mood_hmm"] = {
        "name": "next_mood_brier_reduction_vs_persistence",
        "value_pct": round(brier_reduction, 3),
        "source": "data/micro_threads/animation_bandit_hmm_mood_stage0.json",
    }
    for name in ["mutation_stability", "readability", "slip_compat", "lineage_survival"]:
        skills[name] = {
            "name": "none (evidence conduit; D4 wiring pins carry no skill claim)",
            "value_pct": None,
            "source": "data/micro_threads/evidence_threads_stage0.json",
        }
    return skills


def build_ablation_gate_report(
    *,
    lifecycles_per_keeper: int = FULL_LIFECYCLES_PER_KEEPER,
    ticks: int = FULL_TICKS,
) -> dict:
    ablation = run_ablation_conditions(
        lifecycles_per_keeper=lifecycles_per_keeper, ticks=ticks
    )
    by_condition = {
        entry["condition"]: entry for entry in ablation["conditions"]
    }
    rules = by_condition["rules_only"]["welfare"]
    frozen = by_condition["frozen"]["welfare"]
    full = by_condition["full_fleet"]["welfare"]
    full_vs_rules_pct = (full - rules) / rules * 100.0 if rules else 0.0
    fleet_vs_frozen_pct = (full - frozen) / frozen * 100.0 if frozen else 0.0

    skills = _skill_metrics()
    verdicts = []
    for name in FLEET_THREAD_NAMES:
        minus = by_condition[f"minus_{name}"]["welfare"]
        removal_cost_pct = (full - minus) / full * 100.0 if full else 0.0
        skill = skills[name]
        skill_pct = skill["value_pct"] if skill["value_pct"] is not None else 0.0
        decision = (
            "keep"
            if max(removal_cost_pct, skill_pct) >= KEEP_THRESHOLD_PCT
            else "drop"
        )
        verdicts.append(
            {
                "thread": name,
                "decision": decision,
                "welfare_removal_cost_pct": round(removal_cost_pct, 3),
                "skill_metric": skill,
                "note": (
                    "kept on its documented skill metric; decision-seam "
                    "welfare contribution ~0 (recorded)"
                    if decision == "keep" and removal_cost_pct < KEEP_THRESHOLD_PCT
                    else (
                        "DROPPED by the documented <5% rule — recorded, "
                        "not kept for sentiment"
                        if decision == "drop"
                        else "kept on welfare removal cost"
                    )
                ),
            }
        )
    keep_count = sum(1 for verdict in verdicts if verdict["decision"] == "keep")
    gate_15_met = full_vs_rules_pct >= RULES_GATE_PCT
    complete = gate_15_met and len(verdicts) == len(FLEET_THREAD_NAMES)
    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete" if complete else "refuted",
        "date": REPORT_DATE,
        "purpose": (
            "D6: the documented ablation gates over D5's harness in the "
            "keeper-dependent beg-mediated mode (the companion cannot "
            "feed itself; the keeper answers the beg display). Gates: "
            ">=15% welfare over rules_only (the T19 precedent headline); "
            "the fleet-vs-frozen increment recorded honestly; every "
            "fleet thread kept or DROPPED by the <5% rule on welfare "
            "removal cost OR its own documented skill metric."
        ),
        "source_artifacts": [
            "labs/micro_threads/synthetic_keepers.py",
            "labs/micro_threads/thread_fleet.py",
            "data/micro_threads/need_predictors_stage0.json",
            "data/micro_threads/animation_bandit_hmm_mood_stage0.json",
            "data/micro_threads/evidence_threads_stage0.json",
            "data/micro_learners/switchboard_ablation_stage0.json",
            "docs/project-research/deep-research/01/deep-research.md",
        ],
        "metrics": {
            "scale": {
                "lifecycles_per_keeper": lifecycles_per_keeper,
                "ticks_per_lifecycle": ticks,
                "full_scale_run": lifecycles_per_keeper
                == FULL_LIFECYCLES_PER_KEEPER
                and ticks == FULL_TICKS,
            },
            "gates": {
                "full_vs_rules_only_welfare_pct": round(full_vs_rules_pct, 3),
                "full_vs_rules_only_meets_15pct": gate_15_met,
                "fleet_vs_frozen_welfare_pct": round(fleet_vs_frozen_pct, 3),
                "keep_count": keep_count,
                "drop_count": len(verdicts) - keep_count,
            },
            "ablation": ablation,
            "thread_verdicts": verdicts,
        },
        "closed_states": (
            [
                "documented_gates_run_in_the_keeper_dependent_mode",
                "full_beats_rules_only_by_more_than_15pct",
                "fleet_vs_frozen_increment_recorded_honestly",
                "every_thread_kept_or_dropped_by_the_documented_rule",
                "drops_recorded_not_kept_for_sentiment",
            ]
            if complete
            else ["d6_bar_not_met_recorded_honestly"]
        ),
        "blocked_states": [
            "decision_seam_welfare_contribution_of_the_fleet_is_~0 "
            "(measured across three environments and a gain sweep: the "
            "frozen reactive rules already sit near the autonomous-"
            "behavior welfare optimum; the remaining welfare belongs to "
            "the keeper — the fleet's proven value is prediction skill, "
            "personalization, and interpretability, streamed for the "
            "GAME's consumers)",
            "dropped_threads_stay_in_the_registry_as_parity_pinned_code "
            "(the T19 precedent: verdicts are recorded; default profiles "
            "must not opt dropped threads in)",
            "live_loop_wiring_of_evidence_and_last_animation "
            "(Phase F's consumption)",
        ],
        "decision": (
            f"Full fleet beats rules_only by {round(full_vs_rules_pct, 1)}% "
            f"(gate >=15% MET); fleet-vs-frozen is "
            f"{round(fleet_vs_frozen_pct, 2)}% (recorded honestly); "
            f"{keep_count} threads kept, {len(verdicts) - keep_count} "
            "dropped by the documented rule."
            if complete
            else "The D6 bar is NOT met — recorded, not fudged."
        ),
        "next_research_step": (
            "The Phase-D gate report; gap-analysis Phase D checked off; "
            "cycle 12 archived; cycle 13 opens Phase E — evolution at "
            "documented scale."
        ),
    }


def write_ablation_gate_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{ARTIFACT_ID}.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ablation gates lab (cycle 12 D6)."
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "micro_threads"
    )
    args = parser.parse_args()
    report = build_ablation_gate_report()
    write_ablation_gate_artifacts(args.output_dir, report)
    print(json.dumps(report["metrics"]["gates"], indent=2))
    for verdict in report["metrics"]["thread_verdicts"]:
        print(
            verdict["thread"],
            verdict["decision"],
            "welfare_cost",
            verdict["welfare_removal_cost_pct"],
            "skill",
            verdict["skill_metric"]["value_pct"],
        )
    print(report["decision"])


if __name__ == "__main__":
    main()
