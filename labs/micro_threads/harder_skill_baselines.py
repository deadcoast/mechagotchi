"""Cycle 26 P4: the harder baselines N3 named and did not run. (ENGINE.)

DR 0051 kept condition E (`qtable_policy`) on skill **+55.459% against
uniform random**, and its own "What this record does NOT do" list names
both of this module's questions: the uniform baseline is *"a weak
opponent"* (the harder comparison against the incumbent frozen reactive
rule was not run), and F's stump baseline *"gets a full-sample oracle
while the tree is scored on its online recommendation — an asymmetry
that runs against the tree."*

This is a NEW artifact (DR 0053: a measurement is reproduced or
superseded, never improved). The committed N3 artifact stays exactly as
it is; this module's collector is a SUPERSET of N3's — the same
harness, the same seeds, the same record order, with two extra fields —
and at the committed budget it must REPRODUCE all three committed skill
numbers exactly before either harder statistic is trusted (the
instrument gate raises otherwise).

THE TWO HARDER QUESTIONS, PRE-REGISTERED
========================================

* **E vs the incumbent frozen reactive rule.** The rule's own choice is
  computed per record by running the switchboard on the same pre-tick
  state with the fleet's inputs stripped exactly as the harness's
  ``frozen`` condition strips them. Scored by the same empirical-regret
  statistic over the same bucket means, judged at the documented D6 5%
  bar: ``beats_incumbent_rule`` / ``indistinguishable_from_rule`` /
  ``loses_to_incumbent_rule``.
* **F vs a like-for-like ONLINE stump.** The stump's recommendation is
  computed from only the records seen so far WITHIN the record's own
  lifecycle (the same per-companion online footing the tree has: its
  thread state resets every life), cold until its side has seen two
  distinct actions (the tree's own cold-start skipping), and valued
  under the same full-sample means as the committed framing:
  ``drop_holds_like_for_like`` / ``drop_overturned_like_for_like``.

**NO ROSTER CHANGE in any branch, pre-registered.** DR 0051's keep and
drops were made by the documented rule and stand; whatever these harder
measurements say becomes dated notes beside DR 0051, never a re-score.

**A PREDICTION IS RECORDED BEFORE THE RUN** — see
``PRE_RUN_PREDICTION``. If the measurement disagrees, it ships anyway.
"""

import argparse
import json
import random
import sys
import time
from pathlib import Path
from statistics import mean

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
    SEED_BASE,
    run_dependent_lifecycle,
)
from candidate_learner_ablation import (  # noqa: E402
    EXTENDED_FLEET_NAMES,
    _brier,
    _group_means,
    _pct_reduction,
    _policy_regret,
)
from synthetic_keepers import KEEPER_IDS, _keeper_evidence  # noqa: E402
from thread_fleet import (  # noqa: E402
    _qtable_bucket,
    _tree_leaf,
    bayes_keeper_counter_signal,
    qtable_policy_signal,
    tiny_tree_router_signal,
)

ARTIFACT_ID = "harder_skill_baselines_stage0"
REPORT_DATE = "2026-08-09"
COMMITTED_N3 = "data/micro_threads/candidate_learner_ablation_stage0.json"

# The keys the harness's `frozen` condition never carries — stripping
# them from a full-fleet state reproduces the frozen reactive rule's
# decision input exactly (`_condition_switches("frozen")` sets no
# switches and observes no fleet).
_FLEET_ONLY_KEYS = (
    "learning_switches",
    "thread_states",
    "evidence",
    "last_animation",
)

PRE_REGISTERED_RULE = (
    "pre-registered (cycle 26 P4). Both harder statistics are judged at "
    "the documented D6 bar (5%), on the SAME harness, seeds and record "
    "order as the committed N3 artifact, and the collector must "
    "REPRODUCE all three committed skill numbers exactly at the "
    "committed budget before either is trusted (the instrument gate "
    "raises otherwise). E: the qtable's empirical regret against the "
    "incumbent frozen reactive rule's regret over the same bucket "
    "means - beats_incumbent_rule at >= +5%, loses_to_incumbent_rule "
    "at <= -5%, indistinguishable_from_rule between. F: the tree's "
    "mean return against a like-for-like ONLINE stump (per-lifecycle "
    "running means, cold until its side has seen two actions, valued "
    "under the same full-sample means) - drop_overturned_like_for_like "
    "only above +5%, drop_holds_like_for_like otherwise. NO ROSTER "
    "CHANGE in any branch: DR 0051's verdicts were made by the "
    "documented rule and stand; these findings become dated notes "
    "beside DR 0051, never a re-score."
)

PRE_RUN_PREDICTION = (
    "Written before the run: the frozen reactive rule is expected to "
    "be a far harder opponent than uniform random - the qtable's "
    "+55.459% is expected to COLLAPSE toward the +-5% band "
    "(indistinguishable_from_rule, direction unknown), because the "
    "empirical bucket means are made largely of the rule's own "
    "behaviour. The like-for-like online stump is expected to lose "
    "some of its oracle advantage, narrowing F's -1.776% toward zero "
    "without crossing the +5% bar (drop_holds_like_for_like). Either "
    "refutation ships as the finding."
)


def online_stump_recommendation(running: dict, side: str):
    """The depth-1 stump on the tree's own online footing: argmax of
    the running per-(side, action) means, cold (None) until its side
    has seen at least two distinct actions."""
    options = {
        action: mean(values)
        for (grouped, action), values in running.items()
        if grouped == side and values
    }
    if len(options) < 2:
        return None
    return max(sorted(options), key=lambda action: options[action])


def judge_harder_baselines(
    *,
    q_vs_rule_pct: float,
    tree_vs_online_stump_pct: float,
    keep_threshold_pct: float,
) -> dict:
    """The pre-registered verdicts. No branch changes the roster."""
    if keep_threshold_pct <= 0:
        raise ValueError(
            "the keep threshold is the documented positive bar, got "
            f"{keep_threshold_pct!r}"
        )
    if q_vs_rule_pct >= keep_threshold_pct:
        e_verdict = "beats_incumbent_rule"
    elif q_vs_rule_pct <= -keep_threshold_pct:
        e_verdict = "loses_to_incumbent_rule"
    else:
        e_verdict = "indistinguishable_from_rule"
    f_verdict = (
        "drop_overturned_like_for_like"
        if tree_vs_online_stump_pct > keep_threshold_pct
        else "drop_holds_like_for_like"
    )
    return {
        "e_verdict": e_verdict,
        "f_verdict": f_verdict,
        "q_vs_rule_pct": round(q_vs_rule_pct, 3),
        "tree_vs_online_stump_pct": round(tree_vs_online_stump_pct, 3),
        "keep_threshold_pct": keep_threshold_pct,
        "roster_changed": False,
    }


def collect_records(
    *, lifecycles_per_keeper: int, ticks: int, seed_base: int = SEED_BASE
) -> list[dict]:
    """N3's instrumented pass, superset fields: the same harness, the
    same seeds, the same order — plus the frozen rule's own choice and
    the record's lifecycle identity."""
    from corpus_builder import build_seed_grids
    from micro_switchboard import run_switchboard

    seeds = build_seed_grids()
    evidence_by_grid = _keeper_evidence(seeds)
    records: list[dict] = []

    for keeper_index, keeper_id in enumerate(KEEPER_IDS):
        for index in range(lifecycles_per_keeper):
            grid = seeds[index % len(seeds)]
            interactions_seen = 0
            ticks_seen = 0
            life = f"{keeper_id}:{index}"

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
                interacted = 1 if payload["executed"] in ("feed", "play") else 0
                running_rate = (
                    interactions_seen / ticks_seen if ticks_seen else 0.5
                )
                # The incumbent frozen reactive rule's own choice on the
                # same pre-tick state: the fleet's inputs stripped
                # exactly as the harness's `frozen` condition never
                # carries them.
                stripped = {
                    key: value
                    for key, value in state.items()
                    if key not in _FLEET_ONLY_KEYS
                }
                frozen_choice = run_switchboard(stripped)["action"]
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
                        "frozen_recommendation": frozen_choice,
                        "life": life,
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


def _committed_statistics(records: list[dict], seed_base: int) -> dict:
    """N3's three committed statistics, recomputed from THIS collector's
    records with the same choosers and the same RNG stream — the
    instrument-parity half of the artifact."""
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
    tree_returns = [
        leaf_means[(record["leaf"], record["tree_recommendation"])]
        for record in records
        if record["tree_recommendation"] is not None
        and (record["leaf"], record["tree_recommendation"]) in leaf_means
    ]
    oracle_returns = []
    for record in records:
        options = {
            action: value
            for (side, action), value in stump_means.items()
            if side == record["hunger_side"]
        }
        if options:
            oracle_returns.append(max(options.values()))
    scored = [r for r in records if r["bayes_prediction"] is not None]
    bayes_brier = _brier(
        [r["bayes_prediction"] for r in scored],
        [r["interacted"] for r in scored],
    )
    running_brier = _brier(
        [r["running_rate"] for r in scored],
        [r["interacted"] for r in scored],
    )
    tree_mean = mean(tree_returns) if tree_returns else None
    oracle_mean = mean(oracle_returns) if oracle_returns else None
    return {
        "records_scored": len(records),
        "q_regret": None if q_regret is None else round(q_regret, 6),
        "uniform_regret": (
            None if uniform_regret is None else round(uniform_regret, 6)
        ),
        "q_vs_uniform_pct": (
            None
            if q_regret is None or uniform_regret is None
            else round(_pct_reduction(uniform_regret, q_regret), 3)
        ),
        "tree_mean_return": None if tree_mean is None else round(tree_mean, 6),
        "stump_oracle_return": (
            None if oracle_mean is None else round(oracle_mean, 6)
        ),
        "tree_vs_oracle_pct": (
            None
            if tree_mean is None or oracle_mean in (None, 0)
            else round((tree_mean - oracle_mean) / abs(oracle_mean) * 100.0, 3)
        ),
        "bayes_vs_running_pct": round(
            _pct_reduction(running_brier, bayes_brier), 3
        ),
        "bucket_means": bucket_means,
        "leaf_means": leaf_means,
        "stump_means": stump_means,
    }


def _harder_statistics(
    records: list[dict], committed: dict
) -> dict:
    """The two harder statistics this artifact exists for."""
    # E: the frozen reactive rule's regret over the same bucket means.
    rule_regret = _policy_regret(
        records,
        committed["bucket_means"],
        "bucket",
        lambda record, options: options.get(record["frozen_recommendation"]),
    )
    q_regret = committed["q_regret"]
    q_vs_rule_pct = (
        None
        if rule_regret in (None, 0) or q_regret is None
        else round(_pct_reduction(rule_regret, q_regret), 3)
    )

    # F: the like-for-like ONLINE stump — per-lifecycle running means,
    # predict-then-update, valued under the same full-sample means.
    stump_means = committed["stump_means"]
    online_returns: list[float] = []
    running: dict = {}
    current_life = None
    for record in records:
        if record["life"] != current_life:
            current_life = record["life"]
            running = {}
        recommendation = online_stump_recommendation(
            running, record["hunger_side"]
        )
        if (
            recommendation is not None
            and (record["hunger_side"], recommendation) in stump_means
        ):
            online_returns.append(
                stump_means[(record["hunger_side"], recommendation)]
            )
        running.setdefault(
            (record["hunger_side"], record["executed"]), []
        ).append(record["balance"])
    online_mean = mean(online_returns) if online_returns else None
    tree_mean = committed["tree_mean_return"]
    tree_vs_online_pct = (
        None
        if tree_mean is None or online_mean in (None, 0)
        else round((tree_mean - online_mean) / abs(online_mean) * 100.0, 3)
    )
    return {
        "rule_regret": None if rule_regret is None else round(rule_regret, 6),
        "q_vs_rule_pct": q_vs_rule_pct,
        "online_stump_return": (
            None if online_mean is None else round(online_mean, 6)
        ),
        "online_stump_scored": len(online_returns),
        "tree_vs_online_stump_pct": tree_vs_online_pct,
    }


def build_harder_baselines_report(
    *,
    lifecycles_per_keeper: int = FULL_LIFECYCLES_PER_KEEPER,
    ticks: int = FULL_TICKS,
    seed_base: int = SEED_BASE,
) -> dict:
    started = time.perf_counter()
    committed_artifact = json.loads(
        (ROOT / COMMITTED_N3).read_text(encoding="utf-8")
    )
    committed_skills = committed_artifact["metrics"]["candidate_skills"]

    records = collect_records(
        lifecycles_per_keeper=lifecycles_per_keeper,
        ticks=ticks,
        seed_base=seed_base,
    )
    reproduced = _committed_statistics(records, seed_base)

    applicable = (
        lifecycles_per_keeper
        == committed_artifact["parameters"]["lifecycles_per_keeper"]
        and ticks == committed_artifact["parameters"]["ticks_per_lifecycle"]
        and seed_base == committed_artifact["parameters"]["seed_base"]
    )
    comparisons = {
        "records_scored": (
            committed_skills["records_scored"],
            reproduced["records_scored"],
        ),
        "q_vs_uniform_pct": (
            committed_skills["qtable_policy"]["value_pct"],
            reproduced["q_vs_uniform_pct"],
        ),
        "q_regret": (
            committed_skills["qtable_policy"]["detail"]["qtable_regret"],
            reproduced["q_regret"],
        ),
        "uniform_regret": (
            committed_skills["qtable_policy"]["detail"]["uniform_regret"],
            reproduced["uniform_regret"],
        ),
        "tree_vs_oracle_pct": (
            committed_skills["tiny_tree_router"]["value_pct"],
            reproduced["tree_vs_oracle_pct"],
        ),
        "tree_mean_return": (
            committed_skills["tiny_tree_router"]["detail"]["tree_mean_return"],
            reproduced["tree_mean_return"],
        ),
        "stump_oracle_return": (
            committed_skills["tiny_tree_router"]["detail"]["stump_mean_return"],
            reproduced["stump_oracle_return"],
        ),
        "bayes_vs_running_pct": (
            committed_skills["bayes_keeper_counter"]["value_pct"],
            reproduced["bayes_vs_running_pct"],
        ),
    }
    instrument_check: dict = {
        "applicable": applicable,
        "committed_artifact": COMMITTED_N3,
        "comparisons": {
            key: {"committed": pair[0], "reproduced": pair[1]}
            for key, pair in comparisons.items()
        },
    }
    if applicable:
        mismatched = sorted(
            key
            for key, (committed_value, reproduced_value) in comparisons.items()
            if committed_value != reproduced_value
        )
        if mismatched:
            raise ValueError(
                "instrument drift: this collector did not reproduce the "
                f"committed N3 statistics on {mismatched}; the harder "
                "baselines may not be judged with an unverified instrument"
            )
        instrument_check["reproduced_committed_statistics"] = True
    else:
        instrument_check["reproduced_committed_statistics"] = (
            "not_applicable (budget differs from the committed run)"
        )

    harder = _harder_statistics(records, reproduced)
    judged = judge_harder_baselines(
        q_vs_rule_pct=harder["q_vs_rule_pct"],
        tree_vs_online_stump_pct=harder["tree_vs_online_stump_pct"],
        keep_threshold_pct=KEEP_THRESHOLD_PCT,
    )

    predicted = {
        "e_verdict": "indistinguishable_from_rule",
        "f_verdict": "drop_holds_like_for_like",
    }
    measured = {
        "e_verdict": judged["e_verdict"],
        "f_verdict": judged["f_verdict"],
    }
    prediction_outcome = (
        "prediction_confirmed"
        if measured == predicted
        else f"prediction_refuted: predicted {predicted}, measured {measured}"
    )

    # The nested means are working state, not artifact content.
    reproduced_public = {
        key: value
        for key, value in reproduced.items()
        if key not in ("bucket_means", "leaf_means", "stump_means")
    }

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0",
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 26 P4: run the two harder baselines DR 0051 named "
            "and did not run — the qtable against the incumbent frozen "
            "reactive rule, and the tree against a like-for-like ONLINE "
            "stump — as a NEW artifact on the same harness, with the "
            "collector required to reproduce all three committed skill "
            "numbers exactly before either is trusted. No roster change "
            "in any branch."
        ),
        "source_artifacts": [
            COMMITTED_N3,
            "labs/micro_threads/candidate_learner_ablation.py",
            "labs/micro_threads/ablation_gates.py",
            "labs/micro_threads/thread_fleet.py",
            "research/decision_records/0051-micro-learner-conditions-efg.md",
        ],
        "parameters": {
            "lifecycles_per_keeper": lifecycles_per_keeper,
            "ticks_per_lifecycle": ticks,
            "seed_base": seed_base,
            "keep_threshold_pct": KEEP_THRESHOLD_PCT,
            "frozen_rule_stripping": list(_FLEET_ONLY_KEYS),
            "online_stump": (
                "per-lifecycle running (side, action) means, "
                "predict-then-update, cold until the side has seen two "
                "distinct actions, valued under the same full-sample "
                "means as the committed framing"
            ),
        },
        "metrics": {
            "instrument_check": instrument_check,
            "reproduced": reproduced_public,
            "harder": harder,
            "judged": judged,
            "wall_clock_s": round(time.perf_counter() - started, 3),
        },
        "closed_states": [
            "both harder questions DR 0051 named are now measured, on "
            "the committed harness with the committed seeds",
            "the collector reproduced the committed N3 statistics "
            "exactly before either harder statistic was judged"
            if applicable
            else "reduced-budget run: the instrument gate binds at the "
            "committed budget",
            "a prediction was recorded BEFORE the run",
        ],
        "blocked_states": [
            "no roster change in any branch (pre-registered): DR 0051's "
            "verdicts stand and these findings become dated notes "
            "beside it",
            "the empirical bucket means are made largely of the "
            "harness's own executed behaviour, so every regret here is "
            "regret against an empirical optimum, not a counterfactual "
            "simulator (N3's inherited framing)",
            "one extended-fleet condition; the harder baselines are "
            "measured where the candidates actually ran",
        ],
        "decision": {
            "e_verdict": judged["e_verdict"],
            "f_verdict": judged["f_verdict"],
            "roster_changed": judged["roster_changed"],
            "judged": judged,
            "rule": PRE_REGISTERED_RULE,
            "pre_run_prediction": PRE_RUN_PREDICTION,
            "prediction_outcome": prediction_outcome,
        },
        "next_research_step": (
            "Record both findings as dated notes beside DR 0051; then "
            "P5 (the probe artifacts carry their own edges) and P6 (the "
            "Phase-P gate)."
        ),
    }


def write_harder_baselines_artifacts(
    output_dir: str | Path, report: dict
) -> list[Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{ARTIFACT_ID}.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return [path]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cycle 26 P4: the harder skill baselines."
    )
    parser.add_argument(
        "--output-dir", default=str(ROOT / "data" / "micro_threads")
    )
    parser.add_argument(
        "--lifecycles-per-keeper", type=int, default=FULL_LIFECYCLES_PER_KEEPER
    )
    parser.add_argument("--ticks", type=int, default=FULL_TICKS)
    args = parser.parse_args()

    report = build_harder_baselines_report(
        lifecycles_per_keeper=args.lifecycles_per_keeper, ticks=args.ticks
    )
    metrics = report["metrics"]
    print(
        "instrument: committed statistics reproduced = "
        f"{metrics['instrument_check']['reproduced_committed_statistics']}"
    )
    reproduced = metrics["reproduced"]
    harder = metrics["harder"]
    print(
        f"E  committed q-vs-uniform {reproduced['q_vs_uniform_pct']}%  "
        f"rule_regret {harder['rule_regret']}  "
        f"q_vs_rule {harder['q_vs_rule_pct']}%"
    )
    print(
        f"F  committed tree-vs-oracle {reproduced['tree_vs_oracle_pct']}%  "
        f"online stump {harder['online_stump_return']} "
        f"({harder['online_stump_scored']} scored)  "
        f"tree_vs_online {harder['tree_vs_online_stump_pct']}%"
    )
    decision = report["decision"]
    print(
        f"\nE: {decision['e_verdict'].upper()}   "
        f"F: {decision['f_verdict'].upper()}   "
        f"roster changed: {decision['roster_changed']}"
    )
    print(decision["prediction_outcome"])
    print(f"wall clock {metrics['wall_clock_s']} s")
    for path in write_harder_baselines_artifacts(args.output_dir, report):
        print(f"wrote {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
