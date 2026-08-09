"""Cycle 25 O3: the headline studies restated under the adopted default.

DR 0052 adopted `insertion` as the `slip_admission` default and DR 0053
flipped it — **prospectively**, with all eight historical callers pinned
to the incumbent so no committed number moved. DR 0053 then named the
only two whose migration is a real question rather than an
evidence-destroying regeneration:

* **`evaluation_loop_scale`** — the source of **DR 0042's headline
  coverage 0.8984**, quoted across decision records, gate reports and
  ONBOARDING;
* **`coverage_qd_gates`** — the documented **E4 gates**.

**THIS RESTATES; IT NEVER OVERWRITES.** DR 0053's rule 2 is the whole
shape of this task: *a measurement does not improve — it is reproduced,
or superseded by a new measurement answering a new question.* "What does
the loop achieve under the adopted default" **is** a new question, so it
gets a **new artifact**, and both committed incumbent artifacts stay
exactly as they are.

WHAT IS RE-RUN, AND WHAT IS DELIBERATELY NOT
============================================

Only the **MAP-Elites arm under `insertion`**, at the documented ten
seeds. Everything else is **read from committed evidence**:

* the **incumbent** E4 runs — DR 0053 rule 2 forbids re-running them,
  and they are the measurement they are;
* the **GA control** — ``run_ga_baseline`` takes no ``slip_admission``,
  so the plain GA is *structurally unaffected* by the arm. Re-running it
  would spend an hour reproducing numbers that cannot have moved;
* **DR 0042's headline**, read from `evaluation_loop_scale_stage0.json`,
  and its adopted-side counterpart, read from N4's
  `slip_admission_default_stage0.json` — N4 already measured `insertion`
  at DR 0042's own seed and configuration, so measuring it again would
  be a second measurement of a committed number.

THE RULE IS PRE-REGISTERED HERE, BEFORE ANY RUN
===============================================

The documented E4 gates are re-judged **VERBATIM** — ``judge_gates`` is
imported from `coverage_qd_gates`, never re-implemented, because a
second copy of the judgement could score the adopted arm by a rule the
incumbent was never held to.

**The gate that can fail**: a documented gate that **PASSED** under the
incumbent and **FAILS** under the adopted default is a **regression**,
and a blocking finding — the adoption's consequence would need its own
record rather than being absorbed into a restatement.

A gate that was **already failing** is explicitly **not** a regression.
DR 0032's GA-advantage clause has been refuted three times; failing
again is the incumbent's own state, and blaming the arm for it would be
a false accusation. A gate that failed and now **passes** is recorded as
a recovery, and never allowed to offset a regression elsewhere.
"""

import argparse
import json
import sys
import time
from pathlib import Path
from statistics import mean

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from coverage_qd_gates import DEFAULT_SEEDS, judge_gates  # noqa: E402
from evaluation_loop_scale import (  # noqa: E402
    DEFAULT_LIFECYCLE_TICKS,
    run_evaluation_loop,
)

ARTIFACT_ID = "adopted_default_restatement_stage0"
REPORT_DATE = "2026-07-28"

INCUMBENT_ARM = "none"
ADOPTED_ARM = "insertion"

_E4_ARTIFACT = ROOT / "data" / "archives" / "coverage_qd_gates_stage0.json"
_LOOP_ARTIFACT = ROOT / "data" / "archives" / "evaluation_loop_scale_stage0.json"
_N4_ARTIFACT = ROOT / "data" / "archives" / "slip_admission_default_stage0.json"

PRE_REGISTERED_RULE = (
    "pre-registered (cycle 25 O3). This RESTATES and NEVER OVERWRITES: "
    "DR 0053's rule 2 says a measurement does not improve, it is "
    "reproduced or superseded by a new measurement answering a new "
    "question — so 'what does the loop achieve under the adopted "
    "default' gets its own artifact and both committed incumbent "
    "artifacts stay exactly as they are. Only the MAP-Elites arm under "
    "`insertion` is re-run; the incumbent runs are read (rule 2 forbids "
    "re-running them), the GA control is read because run_ga_baseline "
    "takes no slip_admission and is structurally unaffected by the arm, "
    "and DR 0042's headline is read from its own artifact with its "
    "adopted-side counterpart read from N4's. The documented E4 gates "
    "are re-judged VERBATIM (judge_gates IMPORTED, never "
    "re-implemented, because a second copy could score the adopted arm "
    "by a rule the incumbent was never held to). THE GATE THAT CAN "
    "FAIL: a documented gate that PASSED under the incumbent and FAILS "
    "under the adopted default is a REGRESSION and a blocking finding, "
    "needing its own record rather than absorption into a restatement. "
    "A gate that was ALREADY failing is explicitly NOT a regression "
    "(DR 0032's GA-advantage clause has been refuted three times; "
    "blaming the arm for it would be a false accusation), and a gate "
    "that recovers is recorded but never offsets a regression."
)


def load_committed_e4() -> dict:
    """The incumbent E4 evidence, READ — never re-run (DR 0053 rule 2)."""
    artifact = json.loads(_E4_ARTIFACT.read_text(encoding="utf-8"))
    metrics = artifact["metrics"]
    return {
        "map_elites_runs": metrics["map_elites_runs"],
        "ga_runs": metrics["ga_runs"],
        "verdict": metrics["verdict"],
        "protocol": metrics.get("protocol", {}),
        "source": "data/archives/coverage_qd_gates_stage0.json",
    }


def load_committed_headline() -> dict:
    """DR 0042's headline and its adopted-side counterpart, both READ.

    The incumbent number comes from the artifact DR 0042 quotes; the
    adopted one from N4, which already measured `insertion` at the same
    seed and configuration. Measuring either again would be a second
    measurement of a committed number.
    """
    loop = json.loads(_LOOP_ARTIFACT.read_text(encoding="utf-8"))
    n4 = json.loads(_N4_ARTIFACT.read_text(encoding="utf-8"))
    incumbent_summary = loop["metrics"]["final_archive"]
    rng_seed = int(n4["parameters"]["seeds"][0])
    adopted = next(
        entry
        for entry in n4["metrics"]["per_seed"][ADOPTED_ARM]
        if int(entry["rng_seed"]) == rng_seed
    )
    incumbent_at_seed = next(
        entry
        for entry in n4["metrics"]["per_seed"][INCUMBENT_ARM]
        if int(entry["rng_seed"]) == rng_seed
    )
    return {
        "rng_seed": rng_seed,
        "incumbent_coverage": incumbent_summary["coverage"],
        "incumbent_qd": incumbent_summary["qd_score"],
        "incumbent_occupied": incumbent_summary["occupied_niches"],
        # N4's incumbent at the same seed must equal DR 0042's committed
        # figure; if it does not, the two artifacts disagree and the
        # restatement is comparing different loops.
        "incumbent_coverage_reproduced": (
            incumbent_at_seed["coverage"] == incumbent_summary["coverage"]
        ),
        "adopted_coverage": adopted["coverage"],
        "adopted_qd": adopted["qd_score"],
        "adopted_occupied": adopted["occupied_niches"],
        "adopted_refusals": adopted["refusals"],
        "adopted_illegal_elites": adopted["slip_illegal_elites"],
        "sources": [
            "data/archives/evaluation_loop_scale_stage0.json",
            "data/archives/slip_admission_default_stage0.json",
        ],
    }


def judge_gate_regressions(*, incumbent: dict, adopted: dict) -> dict:
    """Compare every documented gate. A pass that became a fail blocks."""
    missing = set(incumbent) ^ set(adopted)
    if missing:
        raise ValueError(
            "every documented gate must appear on both sides — silently "
            f"skipping one would let a regression hide: {sorted(missing)}"
        )
    regressed = sorted(
        name for name in incumbent if incumbent[name] and not adopted[name]
    )
    recovered = sorted(
        name for name in incumbent if not incumbent[name] and adopted[name]
    )
    already_failing = sorted(
        name for name in incumbent if not incumbent[name] and not adopted[name]
    )
    return {
        "verdict": "regression" if regressed else "no_regression",
        "regressed_gates": regressed,
        "recovered_gates": recovered,
        "already_failing_gates": already_failing,
        "compared_gates": sorted(incumbent),
        "basis": (
            "a gate that PASSED under the incumbent and FAILS under the "
            "adopted default is a blocking finding; a gate that was "
            "already failing is not a regression and blaming the arm "
            "for it would be a false accusation; a recovery is recorded "
            "but never offsets a regression"
        ),
    }


def _gate_booleans(judged: dict) -> dict:
    return {name: bool(value) for name, value in judged.items() if name.endswith("_met")}


def build_restatement_report(
    *,
    seeds: list[int] | None = None,
    population: int = 256,
    target_evaluations: int = 20_480,
    lifecycle_ticks: int = DEFAULT_LIFECYCLE_TICKS,
    cache_dir: str | Path | None = None,
) -> dict:
    started = time.perf_counter()
    seeds = list(DEFAULT_SEEDS if seeds is None else seeds)
    committed = load_committed_e4()
    headline = load_committed_headline()

    adopted_runs: list[dict] = []
    computed = 0
    replayed = 0
    for seed in seeds:
        cached = None
        path = None
        if cache_dir is not None:
            directory = Path(cache_dir)
            directory.mkdir(parents=True, exist_ok=True)
            path = directory / (
                f"e4_{ADOPTED_ARM}_p{population}_e{target_evaluations}"
                f"_t{lifecycle_ticks}_s{seed}.json"
            )
            if path.exists():
                cached = json.loads(path.read_text(encoding="utf-8"))
        if cached is None:
            loop = run_evaluation_loop(
                population=population,
                target_evaluations=target_evaluations,
                rng_seed=seed,
                lifecycle_ticks=lifecycle_ticks,
                generation="constrained",
                slip_admission=ADOPTED_ARM,
            )
            summary = loop["archive_summary"]
            cached = {
                "rng_seed": seed,
                "evaluations_total": loop["evaluations_total"],
                "generations_run": len(loop["trajectory"]),
                "occupied_niches": summary["occupied_niches"],
                "coverage": summary["coverage"],
                "qd_score": summary["qd_score"],
                "best_fitness": summary["best_fitness"],
                "mean_elite_fitness": summary["mean_elite_fitness"],
            }
            computed += 1
            if path is not None:
                path.write_text(json.dumps(cached, indent=2) + "\n", encoding="utf-8")
        else:
            replayed += 1
        adopted_runs.append(cached)

    # The documented gates, re-judged VERBATIM against the SAME GA
    # control the incumbent was judged against.
    adopted_judged = judge_gates(
        map_elites_runs=adopted_runs, ga_runs=committed["ga_runs"]
    )
    incumbent_judged = committed["verdict"]
    regressions = judge_gate_regressions(
        incumbent=_gate_booleans(incumbent_judged),
        adopted=_gate_booleans(adopted_judged),
    )

    def delta(key: str) -> float | None:
        left, right = incumbent_judged.get(key), adopted_judged.get(key)
        if isinstance(left, int | float) and isinstance(right, int | float):
            return round(right - left, 6)
        return None

    wall_clock_s = round(time.perf_counter() - started, 3)

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0",
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 25 O3: restate DR 0042's headline coverage and the "
            "documented E4 gates under the ADOPTED `slip_admission` "
            "default, without overwriting either committed incumbent "
            "artifact — DR 0053's rule 2 makes this a new measurement "
            "answering a new question, not a regeneration."
        ),
        "source_artifacts": [
            "data/archives/coverage_qd_gates_stage0.json",
            "data/archives/evaluation_loop_scale_stage0.json",
            "data/archives/slip_admission_default_stage0.json",
            "data/archives/slip_admission_arms_stage0.json",
        ],
        "parameters": {
            "seeds": seeds,
            "population": population,
            "target_evaluations": target_evaluations,
            "lifecycle_ticks": lifecycle_ticks,
            "incumbent_arm": INCUMBENT_ARM,
            "adopted_arm": ADOPTED_ARM,
            "generation": "constrained (DR 0042's adopted layer)",
            "ga_control": (
                "READ from the committed artifact — run_ga_baseline takes "
                "no slip_admission and is structurally unaffected by the "
                "arm, so re-running it would reproduce numbers that "
                "cannot have moved"
            ),
        },
        "metrics": {
            "headline": {
                **headline,
                "delta": round(
                    headline["adopted_coverage"] - headline["incumbent_coverage"], 6
                ),
                "qd_delta": round(
                    headline["adopted_qd"] - headline["incumbent_qd"], 6
                ),
                "niche_delta": (
                    headline["adopted_occupied"] - headline["incumbent_occupied"]
                ),
            },
            "e4": {
                "incumbent_verdict": incumbent_judged,
                "adopted_verdict": adopted_judged,
                "deltas": {
                    key: delta(key)
                    for key in (
                        "map_elites_coverage_mean",
                        "map_elites_best_fitness_mean",
                        "coverage_advantage_over_ga",
                    )
                },
                "adopted_runs": adopted_runs,
                "incumbent_runs_source": committed["source"],
            },
            "compute": {
                "runs_computed_this_invocation": computed,
                "runs_read_from_cache": replayed,
                "wall_clock_s": wall_clock_s,
            },
        },
        "closed_states": [
            "DR 0042's headline is restated under the adopted default "
            "with its delta, and BOTH numbers are read from committed "
            "artifacts rather than re-measured",
            "the documented E4 gates are re-judged VERBATIM (judge_gates "
            "imported, never re-implemented) against the SAME GA control "
            "the incumbent was judged against",
            "a gate that passed and now fails is a REGRESSION and a "
            "blocking finding; a gate that was already failing is "
            "explicitly not one",
            "only the adopted arm is re-run — the incumbent runs and the "
            "GA control are read, the latter because the arm cannot "
            "structurally affect it",
        ],
        "blocked_states": [
            "this study NEVER OVERWRITES either committed incumbent "
            "artifact: `evaluation_loop_scale_stage0.json` and "
            "`coverage_qd_gates_stage0.json` remain the measurements "
            "they were, and DR 0053's rule 2 is why",
            "the other six loop callers stay pinned to the incumbent "
            "(DR 0053 records which and why); four of them MEASURE the "
            "defect and must never migrate",
            "DR 0046's comparability rule applies: every coverage and QD "
            "number here is an incumbent-GEOMETRY number, and the "
            "restatement changes the admission arm, not the geometry",
            "one SLIP profile (slip_lcd_seed) — DR 0047's inherited "
            "limit; a wider palette would reject fewer bootstrap "
            "creatures and move every cost",
        ],
        "decision": {
            "regressions": regressions,
            "rule": PRE_REGISTERED_RULE,
        },
        "next_research_step": (
            "O4: Stage 2's undispositioned generator arms — shape "
            "grammar and CPPN, named in the dossier and never judged."
        ),
    }


def write_restatement_artifacts(
    output_dir: str | Path, report: dict
) -> list[Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{ARTIFACT_ID}.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return [path]


def main() -> None:
    parser = argparse.ArgumentParser(description="Cycle 25 O3: the adopted-default restatement.")
    parser.add_argument("--output-dir", default=str(ROOT / "data" / "archives"))
    parser.add_argument("--cache-dir", default=None)
    args = parser.parse_args()

    report = build_restatement_report(cache_dir=args.cache_dir)
    metrics = report["metrics"]
    head = metrics["headline"]
    print(
        f"DR 0042 headline (seed {head['rng_seed']}): coverage "
        f"{head['incumbent_coverage']} -> {head['adopted_coverage']} "
        f"(delta {head['delta']:+.6f}); QD {head['incumbent_qd']} -> "
        f"{head['adopted_qd']} ({head['qd_delta']:+.6f}); niches "
        f"{head['incumbent_occupied']} -> {head['adopted_occupied']} "
        f"({head['niche_delta']:+d})"
    )
    print(
        f"  incumbent headline reproduced from N4: "
        f"{head['incumbent_coverage_reproduced']}; refusals under the "
        f"adopted default: {head['adopted_refusals']}; illegal elites: "
        f"{head['adopted_illegal_elites']}"
    )
    e4 = metrics["e4"]
    print("\nE4 gates, re-judged verbatim over the documented ten seeds:")
    for key, value in e4["deltas"].items():
        print(f"  {key}: delta {value}")
    for name in sorted(_gate_booleans(e4["incumbent_verdict"])):
        was = _gate_booleans(e4["incumbent_verdict"])[name]
        now = _gate_booleans(e4["adopted_verdict"]).get(name)
        print(f"  {name}: {was} -> {now}")
    regressions = report["decision"]["regressions"]
    print(f"\n{regressions['verdict'].upper()}")
    if regressions["regressed_gates"]:
        print(f"  REGRESSED: {regressions['regressed_gates']}")
    if regressions["already_failing_gates"]:
        print(f"  already failing (not a regression): {regressions['already_failing_gates']}")
    if regressions["recovered_gates"]:
        print(f"  recovered: {regressions['recovered_gates']}")
    compute = metrics["compute"]
    print(
        f"  computed {compute['runs_computed_this_invocation']}, "
        f"replayed {compute['runs_read_from_cache']}, "
        f"{compute['wall_clock_s']} s"
    )
    for path in write_restatement_artifacts(args.output_dir, report):
        print(f"wrote {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
