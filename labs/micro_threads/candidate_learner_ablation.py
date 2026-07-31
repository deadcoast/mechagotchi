"""Cycle 24 N3: the micro-learner ablation conditions E / F / G.

The dossier's micro-learner ablation names eight conditions. Phase D
(cycle 12) built the eleven-thread fleet and ran A/B/remove-one over it,
keeping five and dropping six — but **none of the eleven is a Q-table, a
tiny decision tree, or a Bayesian counter**, so conditions

    E. full minus Q-table
    F. full minus tiny tree
    G. full minus Bayesian counter

have been *documented and unmet since cycle 12*. This slice builds the
three learners and runs them through the **same D6 gates, verbatim, on
the same harness** — `ablation_gates.run_ablation_conditions` is
IMPORTED, never re-implemented, because a second copy of the harness
could score a learner the real one would have judged differently.

**THE RULE IS PRE-REGISTERED HERE, BEFORE ANY RUN**, and it is D6's rule
unchanged rather than a new one invented for the candidates:

> *"Keep a learner only if its removal causes at least a 5% decline in
> one target metric without improving another more important metric."*

Operationally, exactly as D6 applied it: a thread keeps its place on
**EITHER** its welfare removal cost **OR** its own documented skill
metric, at the same 5% bar. **Dropping all three is a first-class
outcome** — the dossier's own weakness column predicts trouble for each
(state explosion, overfitting, limited expressivity), and this cycle has
already shipped three refusals.

**AND THE INCUMBENT ELEVEN ARE RE-JUDGED, NOT ASSUMED.** Adding threads
changes the `full_fleet` baseline every removal cost is measured
against, so the kept-five roster is recomputed here. The charter names
that explicitly: *"a drop that changes the kept-five roster would be a
real result about the fleet."*

**What is known before the run, and why the gate still matters.** D6
measured every welfare removal cost at ~0 — the frozen reactive rules
already sit near the autonomous-behavior welfare optimum, and *"the
remaining welfare belongs to the keeper"*. So all five kept threads were
kept on their **skill** metric, not on welfare. The honest expectation is
therefore that the candidates' welfare costs also land near zero and
their fate rests on skill. That is a prediction, written down first, and
the measurement is free to refute it.

Each candidate's skill metric follows an existing D6 precedent rather
than a new statistic invented to flatter it:

* **E `qtable_policy`** — action-regret reduction against a uniform
  random policy over the same buckets (the `animation_bandit`
  precedent, which reduces regret against uniform rotation).
* **F `tiny_tree_router`** — return improvement against a **depth-1
  stump** on the same data. The baseline is deliberately the tree's own
  simpler self: if depth 2 cannot beat depth 1, the second split is
  decoration.
* **G `bayes_keeper_counter`** — next-interaction Brier reduction
  against the **running interaction rate** (the `attention_forecast`
  precedent, which is the harsher of the available baselines).

All three are measured on the harness itself through an additive,
read-only observer hook, so no learner is scored on a replay that
differs from the run it was judged in.
"""

import argparse
import json
import random
import sys
import time
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
for sub in ("labs/micro_threads", "labs/grid_genome", "labs/lifecycle_sim"):
    path = str(ROOT / sub)
    if path not in sys.path:
        sys.path.insert(0, path)

from ablation_gates import (  # noqa: E402
    FULL_LIFECYCLES_PER_KEEPER,
    FULL_TICKS,
    KEEP_THRESHOLD_PCT,
    RULES_GATE_PCT,
    SEED_BASE,
    run_ablation_conditions,
    run_dependent_lifecycle,
)
from synthetic_keepers import KEEPER_IDS, _keeper_evidence  # noqa: E402
from thread_fleet import (  # noqa: E402
    CANDIDATE_THREAD_NAMES,
    FLEET_THREAD_NAMES,
    _qtable_bucket,
    _tree_leaf,
    bayes_keeper_counter_signal,
    qtable_policy_signal,
    tiny_tree_router_signal,
)

ARTIFACT_ID = "candidate_learner_ablation_stage0"
REPORT_DATE = "2026-07-28"

# The dossier's own condition letters, so the artifact answers the
# document's question in the document's own vocabulary.
CONDITION_LETTERS = {
    "E": "qtable_policy",
    "F": "tiny_tree_router",
    "G": "bayes_keeper_counter",
}

EXTENDED_FLEET_NAMES = FLEET_THREAD_NAMES + CANDIDATE_THREAD_NAMES

PRE_REGISTERED_RULE = (
    "pre-registered (cycle 24 N3) and NOT a new rule — it is D6's rule "
    "verbatim, applied to the dossier's unmet conditions E/F/G. The "
    "dossier: 'Keep a learner only if its removal causes at least a 5% "
    "decline in one target metric without improving another more "
    "important metric.' Operationally as D6 applied it: a learner keeps "
    "its place on EITHER its welfare removal cost OR its own documented "
    "skill metric, at the same 5% bar. Skill baselines follow existing "
    "D6 precedents rather than new statistics: regret reduction vs a "
    "uniform random policy (the animation_bandit precedent), return "
    "improvement vs a DEPTH-1 STUMP (the tree's own simpler self — if "
    "depth 2 cannot beat depth 1 the second split is decoration), and "
    "next-interaction Brier reduction vs the running interaction rate "
    "(the attention_forecast precedent, the harsher baseline). "
    "DROPPING ALL THREE IS FIRST-CLASS. The incumbent eleven are "
    "RE-JUDGED on the new full_fleet baseline, because adding threads "
    "moves the baseline every removal cost is measured against and a "
    "changed kept-five roster would be a real result about the fleet."
)

PRE_RUN_EXPECTATION = (
    "Written before the run: D6 measured every welfare removal cost at "
    "~0 (the frozen reactive rules already sit near the "
    "autonomous-behavior welfare optimum; the remaining welfare belongs "
    "to the keeper), so all five kept threads were kept on SKILL rather "
    "than welfare. The candidates are therefore expected to show "
    "near-zero welfare cost too, with their fate resting on skill. The "
    "measurement is free to refute this."
)

BYTE_IDENTICAL_NOTE = (
    "The candidates are additive and byte-identical when off: "
    "FLEET_THREADS is untouched, the extension rides the same opt-in "
    "seam, and a thread without an explicit learning_switches[name] is "
    "True never runs and holds no memory. The off-mode roster is pinned "
    "against a FROZEN literal list of the Phase-D eleven, not against a "
    "second call to the new code (the cycle-23 trap)."
)


def judge_candidate(
    *, thread: str, removal_cost_pct: float, skill_pct: float | None
) -> dict:
    """D6's rule, applied. Both verdicts first-class."""
    effective_skill = 0.0 if skill_pct is None else skill_pct
    keep = max(removal_cost_pct, effective_skill) >= KEEP_THRESHOLD_PCT
    if keep and removal_cost_pct >= KEEP_THRESHOLD_PCT:
        note = "kept on welfare removal cost"
    elif keep:
        note = (
            "kept on its documented skill metric; decision-seam welfare "
            "contribution below the 5% bar (recorded)"
        )
    else:
        note = (
            "DROPPED by the documented 5% rule on BOTH welfare removal "
            "cost and its own skill metric — recorded, not kept for "
            "sentiment"
        )
    return {
        "thread": thread,
        "decision": "keep" if keep else "drop",
        "welfare_removal_cost_pct": round(removal_cost_pct, 3),
        "skill_pct": None if skill_pct is None else round(skill_pct, 3),
        "note": note,
    }


def _brier(predictions: list[float], outcomes: list[int]) -> float:
    if not predictions:
        return 0.0
    return sum(
        (p - o) ** 2 for p, o in zip(predictions, outcomes)
    ) / len(predictions)


def _pct_reduction(baseline: float, measured: float) -> float | None:
    """None when the baseline is zero — never a fabricated percentage."""
    if baseline == 0:
        return None
    return (baseline - measured) / abs(baseline) * 100.0


def collect_skill_records(
    *,
    lifecycles_per_keeper: int,
    ticks: int,
    seed_base: int = SEED_BASE,
) -> list[dict]:
    """One instrumented pass over the SAME harness the gates use."""
    from corpus_builder import build_seed_grids

    seeds = build_seed_grids()
    evidence_by_grid = _keeper_evidence(seeds)
    records: list[dict] = []

    for keeper_index, keeper_id in enumerate(KEEPER_IDS):
        for index in range(lifecycles_per_keeper):
            grid = seeds[index % len(seeds)]
            interactions_seen = 0
            ticks_seen = 0

            def observer(payload: dict) -> None:
                nonlocal interactions_seen, ticks_seen
                state = payload["state"]
                threads = state.get("thread_states") or {}
                qsignal = qtable_policy_signal(
                    threads.get("qtable_policy") or {}, state
                )
                tsignal = tiny_tree_router_signal(
                    threads.get("tiny_tree_router") or {}, state
                )
                bsignal = bayes_keeper_counter_signal(
                    threads.get("bayes_keeper_counter") or {}, state
                )
                leaf, _, _ = _tree_leaf(
                    threads.get("tiny_tree_router") or {}, state
                )
                # Score the learner on the event it can actually
                # OBSERVE. `recent_interactions` records `1 if action in
                # {feed, play}` (lifecycle_sim), so that — not the
                # keeper's override — is what this thread's Beta
                # posterior estimates. A first run scored it against
                # `override is not None` and produced a large negative
                # skill; that was the instrument marking the learner
                # wrong on a question it was never asked. Corrected and
                # re-run; see the experiment report.
                interacted = 1 if payload["executed"] in ("feed", "play") else 0
                running_rate = (
                    interactions_seen / ticks_seen if ticks_seen else 0.5
                )
                records.append(
                    {
                        "bucket": _qtable_bucket(state),
                        "leaf": leaf,
                        "hunger_side": leaf[0],
                        "executed": payload["executed"],
                        "balance": float(payload["entry"]["balance"]),
                        "q_recommendation": qsignal["output"]["best_action"],
                        "tree_recommendation": tsignal["output"]["best_action"],
                        "bayes_prediction": bsignal["output"]["responsiveness"]
                        if not bsignal["output"]["cold_start"]
                        else None,
                        "running_rate": running_rate,
                        "interacted": interacted,
                    }
                )
                interactions_seen += interacted
                ticks_seen += 1

            run_dependent_lifecycle(
                grid,
                keeper_id,
                ticks=ticks,
                rng_seed=seed_base + keeper_index * 100_000 + index,
                condition="full_fleet",
                evidence=evidence_by_grid[grid["grid_id"]],
                fleet_names=EXTENDED_FLEET_NAMES,
                observer=observer,
            )
    return records


def _group_means(records: list[dict], key: str) -> dict:
    totals: dict[tuple[str, str], list[float]] = {}
    for record in records:
        totals.setdefault((record[key], record["executed"]), []).append(
            record["balance"]
        )
    return {
        group: sum(values) / len(values) for group, values in totals.items()
    }


def _policy_regret(
    records: list[dict], means: dict, key: str, chooser
) -> float | None:
    """Mean shortfall against the empirically best action per group."""
    regrets = []
    for record in records:
        group = record[key]
        options = {
            action: value
            for (grouped, action), value in means.items()
            if grouped == group
        }
        if len(options) < 2:
            continue
        best = max(options.values())
        chosen = chooser(record, options)
        if chosen is None:
            continue
        regrets.append(best - chosen)
    if not regrets:
        return None
    return sum(regrets) / len(regrets)


def measure_candidate_skills(
    *, lifecycles_per_keeper: int, ticks: int, seed_base: int = SEED_BASE
) -> dict:
    records = collect_skill_records(
        lifecycles_per_keeper=lifecycles_per_keeper,
        ticks=ticks,
        seed_base=seed_base,
    )
    bucket_means = _group_means(records, "bucket")
    leaf_means = _group_means(records, "leaf")
    stump_means = _group_means(records, "hunger_side")
    rng = random.Random(seed_base)

    q_regret = _policy_regret(
        records,
        bucket_means,
        "bucket",
        lambda record, options: options.get(record["q_recommendation"]),
    )
    uniform_regret = _policy_regret(
        records,
        bucket_means,
        "bucket",
        lambda record, options: options[rng.choice(sorted(options))],
    )
    q_reduction = (
        None
        if q_regret is None or uniform_regret is None
        else _pct_reduction(uniform_regret, q_regret)
    )

    tree_returns = [
        leaf_means[(record["leaf"], record["tree_recommendation"])]
        for record in records
        if record["tree_recommendation"] is not None
        and (record["leaf"], record["tree_recommendation"]) in leaf_means
    ]
    stump_returns = []
    for record in records:
        options = {
            action: value
            for (side, action), value in stump_means.items()
            if side == record["hunger_side"]
        }
        if options:
            stump_returns.append(max(options.values()))
    tree_mean = sum(tree_returns) / len(tree_returns) if tree_returns else None
    stump_mean = (
        sum(stump_returns) / len(stump_returns) if stump_returns else None
    )
    tree_improvement = (
        None
        if tree_mean is None or stump_mean is None or stump_mean == 0
        else (tree_mean - stump_mean) / abs(stump_mean) * 100.0
    )

    scored = [record for record in records if record["bayes_prediction"] is not None]
    bayes_brier = _brier(
        [record["bayes_prediction"] for record in scored],
        [record["interacted"] for record in scored],
    )
    running_brier = _brier(
        [record["running_rate"] for record in scored],
        [record["interacted"] for record in scored],
    )
    bayes_reduction = _pct_reduction(running_brier, bayes_brier)

    return {
        "records_scored": len(records),
        "qtable_policy": {
            "name": "action_regret_reduction_vs_uniform_random_policy",
            "value_pct": None if q_reduction is None else round(q_reduction, 3),
            "detail": {
                "qtable_regret": None if q_regret is None else round(q_regret, 6),
                "uniform_regret": (
                    None if uniform_regret is None else round(uniform_regret, 6)
                ),
            },
            "source": "measured on the D6 harness (this artifact)",
        },
        "tiny_tree_router": {
            "name": "route_return_improvement_vs_depth1_stump",
            "value_pct": (
                None if tree_improvement is None else round(tree_improvement, 3)
            ),
            "detail": {
                "tree_mean_return": None if tree_mean is None else round(tree_mean, 6),
                "stump_mean_return": (
                    None if stump_mean is None else round(stump_mean, 6)
                ),
            },
            "source": "measured on the D6 harness (this artifact)",
        },
        "bayes_keeper_counter": {
            "name": "next_interaction_brier_reduction_vs_running_rate",
            "value_pct": (
                None if bayes_reduction is None else round(bayes_reduction, 3)
            ),
            "detail": {
                "bayes_brier": round(bayes_brier, 6),
                "running_rate_brier": round(running_brier, 6),
                "scored_ticks": len(scored),
            },
            "source": "measured on the D6 harness (this artifact)",
        },
    }


def measure_ablation_unit(*, sample_ticks: int = 200) -> dict:
    """Wall-clock pilot (DR 0028: FIRST, and derived rather than picked)."""
    from corpus_builder import build_seed_grids

    seeds = build_seed_grids()
    evidence_by_grid = _keeper_evidence(seeds)
    grid = seeds[0]
    started = time.perf_counter()
    run_dependent_lifecycle(
        grid,
        KEEPER_IDS[0],
        ticks=sample_ticks,
        rng_seed=SEED_BASE,
        condition="full_fleet",
        evidence=evidence_by_grid[grid["grid_id"]],
        fleet_names=EXTENDED_FLEET_NAMES,
    )
    elapsed_ms = (time.perf_counter() - started) * 1000
    conditions = 3 + len(EXTENDED_FLEET_NAMES)
    lifecycles = conditions * len(KEEPER_IDS) * FULL_LIFECYCLES_PER_KEEPER
    per_lifecycle_ms = elapsed_ms * (FULL_TICKS / sample_ticks)
    return {
        "context": (
            "stage-0 dev machine; one unit is a full keeper-dependent "
            "lifecycle at the extended 14-thread fleet"
        ),
        "ablation_unit": {
            "sample_ticks": sample_ticks,
            "lifecycle_ms": round(elapsed_ms, 2),
        },
        "projections": {
            "conditions": conditions,
            "full_lifecycles": lifecycles,
            "full_run_s": round(per_lifecycle_ms * lifecycles / 1000, 2),
            "skill_pass_s": round(
                per_lifecycle_ms
                * len(KEEPER_IDS)
                * FULL_LIFECYCLES_PER_KEEPER
                / 1000,
                2,
            ),
        },
    }


def build_candidate_ablation_report(
    *,
    lifecycles_per_keeper: int = FULL_LIFECYCLES_PER_KEEPER,
    ticks: int = FULL_TICKS,
    seed_base: int = SEED_BASE,
) -> dict:
    started = time.perf_counter()
    ablation = run_ablation_conditions(
        lifecycles_per_keeper=lifecycles_per_keeper,
        ticks=ticks,
        seed_base=seed_base,
        fleet_names=EXTENDED_FLEET_NAMES,
    )
    by_condition = {entry["condition"]: entry for entry in ablation["conditions"]}
    rules = by_condition["rules_only"]["welfare"]
    frozen = by_condition["frozen"]["welfare"]
    full = by_condition["full_fleet"]["welfare"]
    full_vs_rules_pct = (full - rules) / rules * 100.0 if rules else 0.0
    fleet_vs_frozen_pct = (full - frozen) / frozen * 100.0 if frozen else 0.0

    skills = measure_candidate_skills(
        lifecycles_per_keeper=lifecycles_per_keeper,
        ticks=ticks,
        seed_base=seed_base,
    )

    letter_by_thread = {name: letter for letter, name in CONDITION_LETTERS.items()}
    candidate_verdicts = []
    for name in CANDIDATE_THREAD_NAMES:
        minus = by_condition[f"minus_{name}"]["welfare"]
        removal_cost_pct = (full - minus) / full * 100.0 if full else 0.0
        judged = judge_candidate(
            thread=name,
            removal_cost_pct=removal_cost_pct,
            skill_pct=skills[name]["value_pct"],
        )
        judged["condition_letter"] = letter_by_thread[name]
        judged["skill_metric"] = skills[name]
        candidate_verdicts.append(judged)

    # The incumbents re-judged on the NEW baseline — never assumed.
    incumbent_reverdicts = []
    for name in FLEET_THREAD_NAMES:
        minus = by_condition[f"minus_{name}"]["welfare"]
        removal_cost_pct = (full - minus) / full * 100.0 if full else 0.0
        incumbent_reverdicts.append(
            {
                "thread": name,
                "welfare_removal_cost_pct": round(removal_cost_pct, 3),
                "meets_welfare_bar": removal_cost_pct >= KEEP_THRESHOLD_PCT,
            }
        )

    keep_count = sum(
        1 for verdict in candidate_verdicts if verdict["decision"] == "keep"
    )
    wall_clock_s = round(time.perf_counter() - started, 3)

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0",
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 24 N3: build the dossier's micro-learner ablation "
            "conditions E (Q-table), F (tiny decision tree) and G "
            "(Bayesian counter) — named in the protocol and never "
            "instantiated since cycle 12 — and run them through the D6 "
            "gates VERBATIM on the same harness, letting the measured "
            "rule keep or drop each."
        ),
        "source_artifacts": [
            "data/micro_threads/ablation_gates_stage0.json",
            "data/micro_threads/need_predictors_stage0.json",
            "data/micro_threads/animation_bandit_hmm_mood_stage0.json",
            "data/micro_threads/evidence_threads_stage0.json",
            "docs/project-research/deep-research/01/deep-research.md",
        ],
        "parameters": {
            "lifecycles_per_keeper": lifecycles_per_keeper,
            "ticks_per_lifecycle": ticks,
            "seed_base": seed_base,
            "keepers": list(KEEPER_IDS),
            "condition_letters": dict(CONDITION_LETTERS),
            "incumbent_fleet": list(FLEET_THREAD_NAMES),
            "candidates": list(CANDIDATE_THREAD_NAMES),
            "full_scale_run": (
                lifecycles_per_keeper == FULL_LIFECYCLES_PER_KEEPER
                and ticks == FULL_TICKS
            ),
        },
        "metrics": {
            "gates": {
                "full_vs_rules_only_welfare_pct": round(full_vs_rules_pct, 3),
                "full_vs_rules_only_meets_15pct": full_vs_rules_pct >= RULES_GATE_PCT,
                "fleet_vs_frozen_welfare_pct": round(fleet_vs_frozen_pct, 3),
                "candidate_keep_count": keep_count,
                "candidate_drop_count": len(candidate_verdicts) - keep_count,
            },
            "ablation": ablation,
            "candidate_skills": skills,
            "candidate_verdicts": candidate_verdicts,
            "incumbent_reverdicts": incumbent_reverdicts,
            "wall_clock_s": wall_clock_s,
        },
        "closed_states": [
            "the dossier's conditions E/F/G are INSTANTIATED and judged, "
            "unmet since cycle 12",
            "the D6 harness is IMPORTED, never re-implemented — the "
            "candidates are judged by the same code that judged the "
            "incumbent eleven",
            "the D6 keep/drop rule is applied verbatim at the same 5% "
            "bar, with dropping first-class",
            "each candidate's skill baseline follows an existing D6 "
            "precedent rather than a new statistic",
            "the incumbent eleven are RE-JUDGED on the new full_fleet "
            "baseline rather than assumed unchanged",
            BYTE_IDENTICAL_NOTE,
            PRE_RUN_EXPECTATION,
        ],
        "blocked_states": [
            "no candidate is promoted into FLEET_THREADS by this study: "
            "a kept candidate would need its own decision record, and "
            "the Phase-D fleet roster is unchanged here",
            "the welfare seam is known to be saturated (D6 measured "
            "every removal cost at ~0 and recorded that the remaining "
            "welfare belongs to the keeper), so a near-zero candidate "
            "welfare cost bounds the decision seam rather than the "
            "learner's value",
            "the skill metrics are measured on this harness and these "
            "five documented keepers only; a different keeper "
            "distribution would move them",
            "a learner with no measurable skill baseline records None "
            "and is judged on welfare alone — never a substituted zero",
        ],
        "decision": {
            "candidate_verdicts": candidate_verdicts,
            "rule": PRE_REGISTERED_RULE,
            "pre_run_expectation": PRE_RUN_EXPECTATION,
            "byte_identical": BYTE_IDENTICAL_NOTE,
        },
        "next_research_step": (
            "N4: the slip_admission default, decided — DR 0047's named "
            "decider, with quality and archive legality pre-registered "
            "alongside coverage."
        ),
    }


def write_candidate_ablation_artifacts(
    output_dir: str | Path, report: dict
) -> list[Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{ARTIFACT_ID}.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return [path]


def main() -> None:
    parser = argparse.ArgumentParser(description="Cycle 24 N3: conditions E/F/G.")
    parser.add_argument(
        "--output-dir", default=str(ROOT / "data" / "micro_threads")
    )
    parser.add_argument(
        "--lifecycles-per-keeper", type=int, default=FULL_LIFECYCLES_PER_KEEPER
    )
    parser.add_argument("--ticks", type=int, default=FULL_TICKS)
    parser.add_argument("--skip-timing", action="store_true")
    args = parser.parse_args()

    if not args.skip_timing:
        print(json.dumps(measure_ablation_unit(), indent=2))

    report = build_candidate_ablation_report(
        lifecycles_per_keeper=args.lifecycles_per_keeper, ticks=args.ticks
    )
    metrics = report["metrics"]
    gates = metrics["gates"]
    print(
        f"\nfull vs rules_only {gates['full_vs_rules_only_welfare_pct']}% "
        f"(>=15%: {gates['full_vs_rules_only_meets_15pct']}); "
        f"fleet vs frozen {gates['fleet_vs_frozen_welfare_pct']}%"
    )
    print("\nCANDIDATES (the dossier's E/F/G):")
    for verdict in metrics["candidate_verdicts"]:
        skill = verdict["skill_metric"]
        print(
            f"  {verdict['condition_letter']}  {verdict['thread']:<22} "
            f"{verdict['decision'].upper():<5} "
            f"welfare {verdict['welfare_removal_cost_pct']:>8}%  "
            f"skill {str(verdict['skill_pct']):>9}%  ({skill['name']})"
        )
    print("\nINCUMBENT ELEVEN, re-judged on the new baseline:")
    for entry in metrics["incumbent_reverdicts"]:
        print(
            f"  {entry['thread']:<22} welfare "
            f"{entry['welfare_removal_cost_pct']:>8}%  "
            f"meets_bar {entry['meets_welfare_bar']}"
        )
    print(
        f"\nkept {gates['candidate_keep_count']} / dropped "
        f"{gates['candidate_drop_count']} of 3"
    )
    for path in write_candidate_ablation_artifacts(args.output_dir, report):
        print(f"wrote {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
