"""Cycle 27 Q1: the Q-table earns its consumer — or the seam stays empty. (ENGINE.)

P4 measured `qtable_policy` beating the incumbent frozen reactive rule
by **44.685%** at per-tick recommendation quality — but that
recommendation enters the decision today only as one diluted additive
nudge among ~15 threads. DR 0051 decision 3: joining the fleet *"needs
a consumer asking for it."* This module is that consumer's gate.

THE SEAM (built with this study, judged by it): the switchboard's new
`qtable_consumer` learning switch — explicit True required (the D1
rule) — under which the decision FOLLOWS the kept thread's
recommendation whenever the thread itself reports full confidence (its
own committed QTABLE_CONFIDENT_VISITS semantics; no new constant). The
override is recorded rung-conditionally in the decision, so off-mode
decisions never gain a key.

THE RULE IS PRE-REGISTERED HERE, BEFORE ANY RUN
===============================================

* **G0 — instruments before verdicts.** The committed switchboard
  scenarios artifact must reproduce parsed-equal with the seam in the
  module (ALWAYS — any budget); at the committed budget the committed
  N3 `full_fleet` welfare numbers must reproduce exactly. Any mismatch
  raises instead of judging.
* **G2 — the consumer FIRES.** Under the `qtable_consumer` condition
  the override must fire on a nonzero fraction of live ticks; a
  consumer that never fires is not a consumer → ``withhold``.
* **G3 — the D6 rule verbatim, end to end.** Welfare under the
  consumer condition against the incumbent `full_fleet` condition on
  the same harness, seeds and budgets, judged at the documented 5%
  bar: ``adopt_into_default_candidate`` at >= +5% (a DR and package
  work would still follow — the verdict names eligibility, never
  ships adoption by itself), ``refuse_as_consumer`` at <= -5% (the
  recommendation quality does not survive end to end — first-class),
  ``eligible_not_promoted`` between (the seam works and stays opt-in).
* **The beg interaction is MEASURED, NOT GATED.** The companion's
  autonomous `feed` choice is the beg display; a learner that begs
  more is a design change, not a free win. Beg ticks and keeper feeds
  are recorded beside the verdict for the adoption record to own if
  adoption ever arises.

**`eligible_not_promoted` is the expected verdict** (see
``PRE_RUN_PREDICTION``): D6 measured the decision seam's welfare as
near-saturated, and P4's regret advantage is a per-tick statistic, not
an end-to-end one. Nothing here deletes or weakens the incumbent rule.
"""

import argparse
import json
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
from candidate_learner_ablation import EXTENDED_FLEET_NAMES  # noqa: E402
from micro_switchboard import run_scenarios  # noqa: E402
from synthetic_keepers import KEEPER_IDS, _keeper_evidence  # noqa: E402

ARTIFACT_ID = "qtable_consumer_gate_stage0"
REPORT_DATE = "2026-08-09"
COMMITTED_N3 = "data/micro_threads/candidate_learner_ablation_stage0.json"
COMMITTED_SCENARIOS = "data/micro_learners/switchboard_stage0.json"

PRE_REGISTERED_RULE = (
    "pre-registered (cycle 27 Q1). G0 instruments before verdicts: the "
    "committed switchboard scenarios artifact must reproduce "
    "parsed-equal with the seam in the module (always), and at the "
    "committed budget the committed N3 full_fleet welfare must "
    "reproduce exactly - any mismatch raises. G2 the consumer FIRES "
    "under its condition on a nonzero fraction of live ticks, else "
    "withhold. G3 the D6 rule verbatim at the documented 5% bar, "
    "consumer condition vs the incumbent full_fleet condition on the "
    "same harness, seeds and budgets: adopt_into_default_candidate at "
    ">= +5% (eligibility only - a decision record and package work "
    "would still follow), refuse_as_consumer at <= -5%, "
    "eligible_not_promoted between (the seam works and stays opt-in). "
    "The beg interaction is measured and recorded beside the verdict, "
    "never gated here. Nothing deletes or weakens the incumbent rule."
)

PRE_RUN_PREDICTION = (
    "Written before the run: eligible_not_promoted. D6 measured the "
    "decision seam's welfare as near-saturated (the attentive keeper "
    "dominates welfare and fleet-vs-frozen sits at ~1%), so the "
    "consumer's end-to-end welfare delta is expected inside the +-5% "
    "band even though its recommendation quality beats the incumbent "
    "rule by 44.685% per tick. The consumer is expected to FIRE on a "
    "real fraction of mid-to-late-life ticks (warm buckets accumulate "
    "with age), and the beg interaction is expected to move only "
    "marginally. A welfare delta clearing the bar in either direction "
    "refutes this and ships as the finding."
)


def judge_consumer(
    *,
    welfare_pct: float,
    fired_fraction: float,
    keep_threshold_pct: float,
) -> dict:
    """The pre-registered verdicts."""
    if keep_threshold_pct <= 0:
        raise ValueError(
            "the keep threshold is the documented positive bar, got "
            f"{keep_threshold_pct!r}"
        )
    failed = []
    if fired_fraction <= 0.0:
        failed.append("G2_consumer_fires")
    if failed:
        verdict = "withhold"
    elif welfare_pct >= keep_threshold_pct:
        verdict = "adopt_into_default_candidate"
    elif welfare_pct <= -keep_threshold_pct:
        verdict = "refuse_as_consumer"
    else:
        verdict = "eligible_not_promoted"
    return {
        "verdict": verdict,
        "failed_gates": failed,
        "welfare_pct": round(welfare_pct, 3),
        "fired_fraction": round(fired_fraction, 6),
        "keep_threshold_pct": keep_threshold_pct,
    }


def _run_condition(
    condition: str,
    *,
    lifecycles_per_keeper: int,
    ticks: int,
    seed_base: int,
) -> dict:
    from corpus_builder import build_seed_grids

    seeds = build_seed_grids()
    evidence_by_grid = _keeper_evidence(seeds)
    runs = []
    fired = 0
    agreed = 0
    observed_ticks = 0

    for keeper_index, keeper_id in enumerate(KEEPER_IDS):
        for index in range(lifecycles_per_keeper):
            grid = seeds[index % len(seeds)]

            def observer(payload: dict) -> None:
                nonlocal fired, agreed, observed_ticks
                observed_ticks += 1
                consumer = payload["decision"].get("qtable_consumer")
                if consumer is not None:
                    fired += 1
                    if consumer["agreed"]:
                        agreed += 1

            runs.append(
                run_dependent_lifecycle(
                    grid,
                    keeper_id,
                    ticks=ticks,
                    rng_seed=seed_base + keeper_index * 100_000 + index,
                    condition=condition,
                    evidence=evidence_by_grid[grid["grid_id"]],
                    fleet_names=EXTENDED_FLEET_NAMES,
                    observer=observer,
                )
            )

    by_keeper: dict[str, list[float]] = {}
    for run in runs:
        by_keeper.setdefault(run["keeper_id"], []).append(run["welfare"])
    return {
        "condition": condition,
        "welfare": round(mean(run["welfare"] for run in runs), 6),
        "welfare_by_keeper": {
            keeper: round(mean(values), 6)
            for keeper, values in sorted(by_keeper.items())
        },
        "mean_survival_ticks": round(
            mean(run["survival_ticks"] for run in runs), 3
        ),
        "beg_ticks": sum(run["beg_ticks"] for run in runs),
        "keeper_feeds": sum(run["keeper_feeds"] for run in runs),
        "observed_ticks": observed_ticks,
        "consumer_fired_ticks": fired,
        "consumer_agreed_ticks": agreed,
    }


def build_qtable_consumer_report(
    *,
    lifecycles_per_keeper: int = FULL_LIFECYCLES_PER_KEEPER,
    ticks: int = FULL_TICKS,
    seed_base: int = SEED_BASE,
) -> dict:
    started = time.perf_counter()

    # G0a — the scenarios instrument, ALWAYS.
    committed_scenarios = json.loads(
        (ROOT / COMMITTED_SCENARIOS).read_text(encoding="utf-8")
    )
    if run_scenarios() != committed_scenarios:
        raise ValueError(
            "instrument drift: the switchboard's committed scenarios "
            "artifact no longer reproduces with the consumer seam in "
            "the module; the off-mode is not byte-identical and this "
            "gate refuses to judge"
        )

    committed_n3 = json.loads(
        (ROOT / COMMITTED_N3).read_text(encoding="utf-8")
    )
    committed_full_fleet = next(
        entry
        for entry in committed_n3["metrics"]["ablation"]["conditions"]
        if entry["condition"] == "full_fleet"
    )
    applicable = (
        lifecycles_per_keeper
        == committed_n3["parameters"]["lifecycles_per_keeper"]
        and ticks == committed_n3["parameters"]["ticks_per_lifecycle"]
        and seed_base == committed_n3["parameters"]["seed_base"]
    )

    incumbent = _run_condition(
        "full_fleet",
        lifecycles_per_keeper=lifecycles_per_keeper,
        ticks=ticks,
        seed_base=seed_base,
    )
    # G0b — the committed full_fleet welfare, at the committed budget.
    if applicable:
        mismatched = sorted(
            key
            for key, committed_value in (
                ("welfare", committed_full_fleet["welfare"]),
                ("mean_survival_ticks", committed_full_fleet["mean_survival_ticks"]),
                ("welfare_by_keeper", committed_full_fleet["welfare_by_keeper"]),
            )
            if incumbent[key] != committed_value
        )
        if mismatched:
            raise ValueError(
                "instrument drift: the incumbent full_fleet condition did "
                f"not reproduce the committed N3 numbers on {mismatched}; "
                "this gate refuses to judge with an unverified instrument"
            )

    consumer = _run_condition(
        "qtable_consumer",
        lifecycles_per_keeper=lifecycles_per_keeper,
        ticks=ticks,
        seed_base=seed_base,
    )

    welfare_pct = round(
        (consumer["welfare"] - incumbent["welfare"])
        / incumbent["welfare"]
        * 100.0,
        3,
    )
    fired_fraction = round(
        consumer["consumer_fired_ticks"] / consumer["observed_ticks"], 6
    ) if consumer["observed_ticks"] else 0.0

    judged = judge_consumer(
        welfare_pct=welfare_pct,
        fired_fraction=fired_fraction,
        keep_threshold_pct=KEEP_THRESHOLD_PCT,
    )
    prediction_outcome = (
        "prediction_confirmed"
        if judged["verdict"] == "eligible_not_promoted"
        else (
            "prediction_refuted: predicted eligible_not_promoted, "
            f"measured {judged['verdict']}"
        )
    )

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0",
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 27 Q1: gate the Q-table's CONSUMER — the opt-in "
            "switchboard seam that follows the kept thread's fully-warm "
            "recommendation — end to end by the D6 rule on the D6 "
            "harness, against the incumbent full_fleet condition at the "
            "committed budget. eligible_not_promoted is the expected "
            "verdict and ships as the finding; refusal is first-class."
        ),
        "source_artifacts": [
            COMMITTED_N3,
            COMMITTED_SCENARIOS,
            "data/micro_threads/harder_skill_baselines_stage0.json",
            "labs/grid_genome/micro_switchboard.py",
            "labs/micro_threads/ablation_gates.py",
            "research/decision_records/0051-micro-learner-conditions-efg.md",
        ],
        "parameters": {
            "lifecycles_per_keeper": lifecycles_per_keeper,
            "ticks_per_lifecycle": ticks,
            "seed_base": seed_base,
            "keep_threshold_pct": KEEP_THRESHOLD_PCT,
            "conditions": ["full_fleet", "qtable_consumer"],
            "consumer_semantics": (
                "explicit-True learning switch; follows qtable_policy's "
                "best_action only when the thread is warm and reports "
                "full confidence (its own committed "
                "QTABLE_CONFIDENT_VISITS semantics)"
            ),
        },
        "metrics": {
            "instrument_check": {
                "scenarios_reproduced": True,
                "committed_scenarios": COMMITTED_SCENARIOS,
                "full_fleet_reproduced": (
                    True
                    if applicable
                    else "not_applicable (budget differs from the committed run)"
                ),
                "committed_full_fleet_welfare": committed_full_fleet["welfare"],
            },
            "incumbent": incumbent,
            "consumer": consumer,
            "welfare_pct": welfare_pct,
            "fired_fraction": fired_fraction,
            "agreement_fraction": round(
                consumer["consumer_agreed_ticks"]
                / consumer["consumer_fired_ticks"],
                6,
            )
            if consumer["consumer_fired_ticks"]
            else None,
            "beg_interaction": {
                "incumbent_beg_ticks": incumbent["beg_ticks"],
                "consumer_beg_ticks": consumer["beg_ticks"],
                "beg_delta": consumer["beg_ticks"] - incumbent["beg_ticks"],
                "incumbent_keeper_feeds": incumbent["keeper_feeds"],
                "consumer_keeper_feeds": consumer["keeper_feeds"],
                "note": (
                    "recorded_not_gated — the companion's autonomous feed "
                    "choice is the beg display; a learner that begs more "
                    "is a design change, not a free win, and the adoption "
                    "record owns this if adoption ever arises"
                ),
            },
            "judged": judged,
            "wall_clock_s": round(time.perf_counter() - started, 3),
        },
        "closed_states": [
            "the consumer seam exists, opt-in, byte-identical off — "
            "pinned against the committed scenarios artifact on every "
            "run of this gate",
            "the end-to-end question DR 0051 said a promotion needs is "
            "now measured by the D6 rule on the D6 harness",
            "the beg interaction is measured beside the verdict",
            "a prediction was recorded BEFORE the run",
        ],
        "blocked_states": [
            "adopt_into_default_candidate, if ever measured, names "
            "eligibility only: adoption into the default fleet is a "
            "decision record plus package work, never this artifact's "
            "act",
            "the consumer follows at FULL thread confidence only — a "
            "graded follow policy (confidence-weighted blending) is a "
            "different consumer with its own gate",
            "one seed corpus, the five documented keepers, the committed "
            "budgets (N3's inherited frame)",
        ],
        "decision": {
            "verdict": judged["verdict"],
            "judged": judged,
            "rule": PRE_REGISTERED_RULE,
            "pre_run_prediction": PRE_RUN_PREDICTION,
            "prediction_outcome": prediction_outcome,
        },
        "next_research_step": (
            "Record the disposition as DR 0060; then Q2 (the SLIP "
            "mechanics rung), Q3 (the default-covenant flip record), Q4 "
            "(the hidden half of §1.17), Q5 (the Phase-Q gate)."
        ),
    }


def write_qtable_consumer_artifacts(
    output_dir: str | Path, report: dict
) -> list[Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{ARTIFACT_ID}.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return [path]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cycle 27 Q1: the Q-table consumer gate."
    )
    parser.add_argument(
        "--output-dir", default=str(ROOT / "data" / "micro_threads")
    )
    parser.add_argument(
        "--lifecycles-per-keeper", type=int, default=FULL_LIFECYCLES_PER_KEEPER
    )
    parser.add_argument("--ticks", type=int, default=FULL_TICKS)
    args = parser.parse_args()

    report = build_qtable_consumer_report(
        lifecycles_per_keeper=args.lifecycles_per_keeper, ticks=args.ticks
    )
    metrics = report["metrics"]
    check = metrics["instrument_check"]
    print(
        f"instrument: scenarios reproduced {check['scenarios_reproduced']}; "
        f"full_fleet reproduced {check['full_fleet_reproduced']}"
    )
    print(
        f"incumbent welfare {metrics['incumbent']['welfare']}  "
        f"consumer welfare {metrics['consumer']['welfare']}  "
        f"delta {metrics['welfare_pct']}%  (bar {KEEP_THRESHOLD_PCT}%)"
    )
    print(
        f"consumer fired on {metrics['fired_fraction']} of ticks "
        f"(agreement {metrics['agreement_fraction']})"
    )
    begs = metrics["beg_interaction"]
    print(
        f"beg ticks {begs['incumbent_beg_ticks']} -> "
        f"{begs['consumer_beg_ticks']} (delta {begs['beg_delta']})  "
        f"keeper feeds {begs['incumbent_keeper_feeds']} -> "
        f"{begs['consumer_keeper_feeds']}"
    )
    print(f"\nverdict: {report['decision']['verdict'].upper()}")
    print(report["decision"]["prediction_outcome"])
    print(f"wall clock {metrics['wall_clock_s']} s")
    for path in write_qtable_consumer_artifacts(args.output_dir, report):
        print(f"wrote {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
