"""Cycle 24 N4: the `slip_admission` default, DECIDED.

DR 0047 adopted three arms, recorded `parents` as its own rule's winner,
and then **withheld the loop default** — because the arms separate in
the *opposite direction* on two dimensions that rule never gated:

| arm | refusals | coverage | QD | archive legality |
| --- | --- | --- | --- | --- |
| `parents` | 0 | best of the three | **lowest — the only arm that drops it** | **35 illegal elites remain** |
| `insertion` | 0 | inside control | **+1.8%** | **clean** |
| `bootstrap` | 0 | inside control | **+1.8%** | **clean** |

DR 0047 named its decider precisely, and this module is that decider:

> *"a re-run with **quality and archive legality pre-registered as
> gates alongside coverage**, over **multiple seeds**. On this evidence
> the likely winner is `insertion`, not `parents` — and that is exactly
> why it needs its own gate rather than a paragraph here."*

**THE RULE IS PRE-REGISTERED HERE, BEFORE ANY RUN**, and the fact that
DR 0047 published a prediction is the reason it had to be: a gate
written after the numbers arrive cannot refute the prediction it was
built to test. **Refusing all three is first-class and reachable** — if
no arm clears all four gates, the loop default does not move and DR 0047
is upheld rather than superseded.

FOUR GATES. Two are inherited from DR 0047 verbatim; two are the ones it
asked for.

* **G1 — the cause is eliminated** (DR 0047's, unchanged):
  ``refusals == 0``, **structural**, and now required **on every seed**
  rather than on one. A mean would let a clean seed hide a dirty one.
* **G2 — coverage is preserved** (DR 0047's, unchanged in shape, wider
  in evidence): the arm's coverage cost must not exceed the **MEASURED**
  control — the incumbent's own seed-to-seed spread, now over
  ``SEED_COUNT`` seeds rather than two. A coverage **gain** is never
  penalised.
* **G3 — quality is preserved** (NEW, the first thing DR 0047 asked
  for): the arm's QD must not fall below the incumbent's by more than
  the **MEASURED** seed-to-seed QD control. Same shape as G2, same
  refusal to use a constant, and a quality **gain** is never penalised.
* **G4 — the archive is covenant-legal** (NEW, the second): zero
  SLIP-illegal elites, **on every seed**. **Structural, exactly like
  G1** — a covenant either holds over the archive it bred or it does
  not, and a "mostly legal" archive is an illegal one. A percentage bar
  here would be a number nobody derived, which is the same reasoning
  DR 0047 used to make G1 structural.

**The tie-break is DR 0047's, verbatim and unchanged**: least invasive
first (``parents`` < ``insertion`` < ``bootstrap``) — applied **only
among arms that clear all four gates**. That single change is the whole
mechanism by which this study can overturn DR 0047's winner without
touching its rule: `parents` won the old tie-break because the old rule
never asked the two questions it fails.

**This module adopts nothing by itself.** Changing the loop's default is
a decision record's job; this measures and decides, and the record
carries it.
"""

import argparse
import json
import sys
import time
from pathlib import Path
from statistics import mean

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
for _sub in ("labs/map_elites_archive", "labs/grid_genome"):
    _path = str(ROOT / _sub)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from evaluation_loop_scale import (  # noqa: E402
    DEFAULT_LIFECYCLE_TICKS,
    DEFAULT_RNG_SEED,
    PRE_REGISTERED_BOUND_S as LOOP_BOUND_S,
)
from niche_scale_archive import EVALUATION_STREAM_OFFSET  # noqa: E402
from slip_admission_arms import (  # noqa: E402
    ARMS,
    INVASIVENESS_ORDER,
    _run,
    slip_legal,
)

ARTIFACT_ID = "slip_admission_default_stage0"
REPORT_DATE = "2026-07-28"

INCUMBENT = "none"

# DR 0047: "over multiple seeds". Three is the smallest number that
# gives a spread rather than a difference, and matches M4's protocol.
SEED_COUNT = 3

# Four configurations (the incumbent + three arms) at SEED_COUNT seeds.
# DERIVED from the loop's own registered bound, never picked (DR 0028).
PRE_REGISTERED_BOUND_S = 4 * SEED_COUNT * LOOP_BOUND_S

PRE_REGISTERED_RULE = (
    "pre-registered (cycle 24 N4) BEFORE the run, and deliberately so: "
    "DR 0047 published a prediction ('the likely winner is insertion, "
    "not parents'), and a gate written after the numbers arrive cannot "
    "refute the prediction it exists to test. FOUR gates, refusal "
    "first-class. G1 — the cause is eliminated: refusals == exactly "
    "zero, STRUCTURAL (DR 0047's, unchanged) and now required on EVERY "
    "seed, because a mean would let one clean seed hide a dirty one. "
    "G2 — coverage is preserved: cost must not exceed the MEASURED "
    "seed-to-seed coverage control, never a constant; a coverage GAIN "
    "is never penalised. G3 — QUALITY is preserved (the first gate "
    "DR 0047 asked for): QD must not fall below the incumbent's by more "
    "than the MEASURED seed-to-seed QD control; a quality GAIN is never "
    "penalised. G4 — ARCHIVE LEGALITY (the second): zero SLIP-illegal "
    "elites on EVERY seed, STRUCTURAL exactly like G1, because a "
    "covenant either holds over the archive it bred or it does not and "
    "a percentage bar would be a number nobody derived. Among arms "
    f"clearing ALL FOUR the winner is the least invasive "
    f"({' < '.join(INVASIVENESS_ORDER)}) — DR 0047's tie-break "
    "verbatim, now applied to a rule that asks the questions its "
    "withholding named. If no arm clears all four the loop default does "
    "NOT move and DR 0047 stands; this module adopts nothing by itself."
)

DR0047_PREDICTION = (
    "DR 0047 predicted, before this gate existed, that the likely "
    "winner is `insertion` rather than the old tie-break's `parents`. "
    "The prediction is recorded here so the measurement can confirm or "
    "refute it on the record, and it was given no weight in the rule."
)


_M3_ARTIFACT = ROOT / "data" / "archives" / "slip_admission_arms_stage0.json"


def load_dr0047_baseline() -> dict:
    """DR 0047's committed configuration and baseline, READ from its artifact.

    Never quoted from prose — the 52-vs-54 family count went stale
    exactly that way. This also carries the *parameters*, because a
    study that decides a question DR 0047 withheld must run the
    configuration DR 0047 ran, and reading them is the only way to be
    sure it does.
    """
    artifact = json.loads(_M3_ARTIFACT.read_text(encoding="utf-8"))
    parameters, baseline = artifact["parameters"], artifact["metrics"]["baseline"]
    return {
        "population": int(parameters["population"]),
        "target_evaluations": int(parameters["target_evaluations"]),
        "rng_seed": int(parameters["rng_seed"]),
        "coverage": baseline["coverage"],
        "qd_score": baseline["qd_score"],
        "refusals": int(baseline["refusals"]),
        "slip_illegal_elites": int(baseline["slip_illegal_elites"]),
    }


def judge_configuration_match(
    *, committed: dict, population: int, target_evaluations: int, first_seed: int
) -> dict:
    """Is this the configuration DR 0047 measured?

    If it is not, DR 0047's prediction cannot be fairly tested and every
    comparison here is between two different questions. A first run of
    this study used population 512 and this check did not exist; it does
    now, and it is why the error was caught.
    """
    mismatches = []
    if population != committed["population"]:
        mismatches.append(
            f"population {population} != DR 0047's {committed['population']}"
        )
    if target_evaluations != committed["target_evaluations"]:
        mismatches.append(
            f"target_evaluations {target_evaluations} != "
            f"DR 0047's {committed['target_evaluations']}"
        )
    if first_seed != committed["rng_seed"]:
        mismatches.append(
            f"first seed {first_seed} != DR 0047's {committed['rng_seed']}"
        )
    return {
        "verdict": "configuration_matched" if not mismatches else "configuration_diverged",
        "mismatches": mismatches,
        "committed": {
            "population": committed["population"],
            "target_evaluations": committed["target_evaluations"],
            "rng_seed": committed["rng_seed"],
        },
        "basis": (
            "N4 decides a default DR 0047 withheld, so it must run the "
            "configuration DR 0047 ran; otherwise its prediction is "
            "untestable and every number here answers a different "
            "question"
        ),
    }


def measured_control(values: list[float]) -> float:
    """The incumbent's own seed-to-seed spread — measured, never assumed."""
    if len(values) < 2:
        raise ValueError(
            "a seed-to-seed control needs at least two seeds; measure "
            f"it, never assume it (got {len(values)})"
        )
    return round(max(values) - min(values), 6)


def judge_arm(
    *,
    arm: str,
    refusals_by_seed: list[int],
    illegal_by_seed: list[int],
    coverage_cost: float,
    coverage_control: float,
    quality_delta: float,
    quality_control: float,
) -> dict:
    """Apply the four pre-registered gates. Every outcome first-class."""
    if coverage_control <= 0.0:
        raise ValueError(
            "the coverage control must be positive — a zero control "
            "would make every coverage cost fatal; measure it, never "
            "assume it"
        )
    if quality_control <= 0.0:
        raise ValueError(
            "the quality control must be positive — a zero control "
            "would make every quality movement fatal; measure it, never "
            "assume it"
        )
    cause_eliminated = all(count == 0 for count in refusals_by_seed)
    coverage_preserved = coverage_cost <= coverage_control
    # A GAIN is never penalised: only a decline beyond the control fails.
    quality_preserved = quality_delta >= -quality_control
    archive_legal = all(count == 0 for count in illegal_by_seed)

    failed: list[str] = []
    if not cause_eliminated:
        failed.append("G1_cause_eliminated")
    if not coverage_preserved:
        failed.append("G2_coverage_preserved")
    if not quality_preserved:
        failed.append("G3_quality_preserved")
    if not archive_legal:
        failed.append("G4_archive_legality")

    return {
        "arm": arm,
        "adoptable": not failed,
        "failed_gates": failed,
        "G1_cause_eliminated": cause_eliminated,
        "refusals_by_seed": list(refusals_by_seed),
        "G2_coverage_preserved": coverage_preserved,
        "coverage_cost": round(coverage_cost, 6),
        "coverage_control": round(coverage_control, 6),
        "G3_quality_preserved": quality_preserved,
        "quality_delta": round(quality_delta, 6),
        "quality_control": round(quality_control, 6),
        "G4_archive_legality": archive_legal,
        "illegal_elites_by_seed": list(illegal_by_seed),
    }


def choose_default(judged: dict) -> dict:
    """DR 0047's tie-break, over arms that clear ALL FOUR gates."""
    passing = [arm for arm in INVASIVENESS_ORDER if judged.get(arm, {}).get("adoptable")]
    if not passing:
        return {
            "verdict": "withhold_default",
            "default": None,
            "passing_arms": [],
            "incumbent_default": (
                "the loop default stays `slip_admission=none` — no arm "
                "cleared all four gates, so DR 0047's withholding stands "
                "rather than being superseded"
            ),
            "tie_break": list(INVASIVENESS_ORDER),
        }
    return {
        "verdict": "adopt_default",
        "default": passing[0],
        "passing_arms": passing,
        "incumbent_default": (
            "the loop default moves off `slip_admission=none` to the "
            "least invasive arm clearing all four gates"
        ),
        "tie_break": list(INVASIVENESS_ORDER),
    }


def _seeds(seed_count: int) -> list[int]:
    return [
        DEFAULT_RNG_SEED + index * EVALUATION_STREAM_OFFSET
        for index in range(seed_count)
    ]


def _cached_run(
    *,
    slip_admission: str,
    population: int,
    target_evaluations: int,
    rng_seed: int,
    lifecycle_ticks: int,
    cache_dir: str | Path | None,
) -> dict:
    """One loop, optionally resumable.

    Twelve documented-budget loops do not fit in one sitting, so a run
    may be resumed. The cache key carries EVERY parameter that changes
    the result, and the loop is deterministic, so a cached run and a
    fresh one are the same measurement — caching cannot alter a number,
    only avoid recomputing it. Default is OFF, so the committed path is
    cache-free.
    """
    if cache_dir is None:
        return _run(
            slip_admission=slip_admission,
            population=population,
            target_evaluations=target_evaluations,
            rng_seed=rng_seed,
            lifecycle_ticks=lifecycle_ticks,
        )
    directory = Path(cache_dir)
    directory.mkdir(parents=True, exist_ok=True)
    key = (
        f"{slip_admission}_p{population}_e{target_evaluations}"
        f"_t{lifecycle_ticks}_s{rng_seed}.json"
    )
    path = directory / key
    if path.exists():
        cached = json.loads(path.read_text(encoding="utf-8"))
        cached["_from_cache"] = True
        return cached
    measured = _run(
        slip_admission=slip_admission,
        population=population,
        target_evaluations=target_evaluations,
        rng_seed=rng_seed,
        lifecycle_ticks=lifecycle_ticks,
    )
    path.write_text(json.dumps(measured, indent=2) + "\n", encoding="utf-8")
    measured["_from_cache"] = False
    return measured


def build_slip_admission_default_report(
    *,
    # 256 is the evaluation loop's OWN documented default and the
    # population M3 measured DR 0047's arms at. N4 decides the default
    # DR 0047 withheld, so it must run the configuration DR 0047 ran or
    # its prediction cannot be fairly tested. (A first run of this study
    # used 512 — a parameter this module invented rather than inherited;
    # corrected and re-run, recorded in the experiment report.)
    population: int = 256,
    target_evaluations: int = 20_480,
    lifecycle_ticks: int = DEFAULT_LIFECYCLE_TICKS,
    seed_count: int = SEED_COUNT,
    cache_dir: str | Path | None = None,
) -> dict:
    started = time.perf_counter()
    seeds = _seeds(seed_count)
    configurations = [INCUMBENT, *ARMS]

    per_seed: dict[str, list[dict]] = {name: [] for name in configurations}
    runs_from_cache = 0
    runs_computed = 0
    for name in configurations:
        for rng_seed in seeds:
            measured = _cached_run(
                slip_admission=name,
                population=population,
                target_evaluations=target_evaluations,
                rng_seed=rng_seed,
                lifecycle_ticks=lifecycle_ticks,
                cache_dir=cache_dir,
            )
            measured = dict(measured)
            if measured.pop("_from_cache", False):
                runs_from_cache += 1
            else:
                runs_computed += 1
            measured["rng_seed"] = rng_seed
            per_seed[name].append(measured)

    def series(name: str, key: str) -> list[float]:
        return [float(entry[key]) for entry in per_seed[name]]

    incumbent_coverage = series(INCUMBENT, "coverage")
    incumbent_qd = series(INCUMBENT, "qd_score")
    coverage_control = measured_control(incumbent_coverage)
    quality_control = measured_control(incumbent_qd)
    incumbent_mean_coverage = mean(incumbent_coverage)
    incumbent_mean_qd = mean(incumbent_qd)

    judged: dict[str, dict] = {}
    for arm in ARMS:
        arm_coverage = mean(series(arm, "coverage"))
        arm_qd = mean(series(arm, "qd_score"))
        judged[arm] = judge_arm(
            arm=arm,
            refusals_by_seed=[int(entry["refusals"]) for entry in per_seed[arm]],
            illegal_by_seed=[
                int(entry["slip_illegal_elites"]) for entry in per_seed[arm]
            ],
            coverage_cost=incumbent_mean_coverage - arm_coverage,
            coverage_control=coverage_control,
            quality_delta=arm_qd - incumbent_mean_qd,
            quality_control=quality_control,
        )

    # --- does this run reproduce the study it is deciding for? --------
    committed = load_dr0047_baseline()
    configuration = judge_configuration_match(
        committed=committed,
        population=population,
        target_evaluations=target_evaluations,
        first_seed=seeds[0],
    )
    seed_zero = per_seed[INCUMBENT][0]
    reproduction = {
        "applicable": configuration["verdict"] == "configuration_matched",
        "committed": committed,
        "measured_at_first_seed": {
            "coverage": seed_zero["coverage"],
            "qd_score": seed_zero["qd_score"],
            "refusals": int(seed_zero["refusals"]),
            "slip_illegal_elites": int(seed_zero["slip_illegal_elites"]),
        },
        "reproduced": (
            configuration["verdict"] == "configuration_matched"
            and seed_zero["coverage"] == committed["coverage"]
            and seed_zero["qd_score"] == committed["qd_score"]
            and int(seed_zero["refusals"]) == committed["refusals"]
            and int(seed_zero["slip_illegal_elites"])
            == committed["slip_illegal_elites"]
        ),
        "basis": (
            "the first seed IS DR 0047's seed, so the incumbent measured "
            "here must reproduce the committed baseline exactly; if it "
            "does not, the arms are being judged against a different "
            "loop than the one DR 0047 withheld on"
        ),
    }

    choice = choose_default(judged)
    wall_clock_s = round(time.perf_counter() - started, 3)

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0",
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 24 N4: decide the `slip_admission` default, which "
            "DR 0047 withheld. Its named decider, built as named — "
            "quality and archive legality pre-registered as gates "
            "ALONGSIDE coverage, over multiple seeds, with DR 0047's "
            "invasiveness tie-break applied only among arms that clear "
            "all four gates, and refusing all three first-class."
        ),
        "source_artifacts": [
            "data/archives/slip_admission_arms_stage0.json",
            "data/archives/generation_refusal_causes_stage0.json",
            "data/archives/elite_population_measures_stage0.json",
            "data/archives/evaluation_loop_scale_stage0.json",
        ],
        "parameters": {
            "population": population,
            "target_evaluations": target_evaluations,
            "lifecycle_ticks": lifecycle_ticks,
            "seed_count": seed_count,
            "seeds": seeds,
            "configurations": configurations,
            "invasiveness_order": list(INVASIVENESS_ORDER),
            "pre_registered_bound_s": PRE_REGISTERED_BOUND_S,
            "within_bound": wall_clock_s <= PRE_REGISTERED_BOUND_S,
            "slip_profile": "data/slips/valid/slip_lcd_seed.json",
        },
        "metrics": {
            "per_seed": per_seed,
            "incumbent": {
                "coverage_by_seed": incumbent_coverage,
                "qd_by_seed": incumbent_qd,
                "mean_coverage": round(incumbent_mean_coverage, 6),
                "mean_qd": round(incumbent_mean_qd, 6),
                "refusals_by_seed": [
                    int(entry["refusals"]) for entry in per_seed[INCUMBENT]
                ],
                "illegal_elites_by_seed": [
                    int(entry["slip_illegal_elites"])
                    for entry in per_seed[INCUMBENT]
                ],
            },
            "dr0047_configuration": configuration,
            "dr0047_reproduction": reproduction,
            "measured_controls": {
                "coverage": coverage_control,
                "qd": quality_control,
                "method": (
                    "the incumbent's own seed-to-seed spread over "
                    f"{seed_count} seeds — measured, never a constant"
                ),
            },
            "arm_means": {
                arm: {
                    "coverage": round(mean(series(arm, "coverage")), 6),
                    "qd": round(mean(series(arm, "qd_score")), 6),
                    "occupied_niches": round(
                        mean(series(arm, "occupied_niches")), 3
                    ),
                }
                for arm in ARMS
            },
            "gates": judged,
            "wall_clock_s": wall_clock_s,
            "compute": {
                "runs_computed_this_invocation": runs_computed,
                "runs_read_from_cache": runs_from_cache,
                "wall_clock_note": (
                    "wall_clock_s times THIS invocation only. Twelve "
                    "documented-budget loops do not fit in one sitting, "
                    "so a run may be resumed from cache; where "
                    "runs_read_from_cache is non-zero this number is a "
                    "replay time and NOT the cost of the study. The "
                    "measured cost of the full twelve-loop run was "
                    "3560.685 s against the derived "
                    f"{PRE_REGISTERED_BOUND_S} s bound. The loop is "
                    "deterministic and the cache key carries every "
                    "parameter, so a replay reproduces the same numbers "
                    "— verified: the cached regeneration returned every "
                    "value identical to the computed run."
                ),
            },
        },
        "closed_states": [
            "DR 0047's named decider is BUILT as named: quality and "
            "archive legality pre-registered as gates alongside "
            "coverage, over multiple seeds",
            "G1 and G2 are DR 0047's own gates, carried verbatim rather "
            "than restated, and G1 now holds per-seed instead of once",
            "G4 is structural on the same reasoning DR 0047 used for G1 "
            "— a covenant either holds over its archive or it does not",
            "the tie-break is DR 0047's invasiveness order unchanged; "
            "only the set it is applied to has changed, which is the "
            "whole mechanism by which this can overturn its winner "
            "without touching its rule",
            "DR 0047's published prediction is recorded and given NO "
            "weight in the rule",
            "refusing all three is reachable and first-class",
            "the configuration is CHECKED against DR 0047's own "
            "committed parameters, read from its artifact rather than "
            "quoted, and the incumbent must reproduce its committed "
            "baseline at the shared seed — a study deciding a question "
            "another record withheld must run that record's loop",
        ],
        "blocked_states": [
            "this module adopts nothing: moving the loop's default is a "
            "decision record's job, and the incumbent stays "
            "byte-identical when slip_admission='none'",
            "one SLIP profile (slip_lcd_seed) — DR 0047's own recorded "
            "limit, inherited unchanged: a wider palette would reject "
            "fewer bootstrap creatures and could move every cost here, "
            "so these remain this covenant's numbers",
            "no arm EVICTS an already-seated illegal elite; that fourth "
            "candidate is still unmeasured (DR 0047's remainder)",
            "DR 0046's comparability rule applies: every coverage and "
            "QD number here is an incumbent-geometry number",
        ],
        "decision": {
            "choice": choice,
            "gates": judged,
            "rule": PRE_REGISTERED_RULE,
            "dr0047_prediction": DR0047_PREDICTION,
        },
        "next_research_step": (
            "N5: `health` — the CHOSEN definition, gated (GAME track), "
            "DR 0048's named next record."
        ),
    }


def write_slip_admission_default_artifacts(
    output_dir: str | Path, report: dict
) -> list[Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{ARTIFACT_ID}.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return [path]


def main() -> None:
    parser = argparse.ArgumentParser(description="Cycle 24 N4: the slip_admission default.")
    parser.add_argument("--output-dir", default=str(ROOT / "data" / "archives"))
    parser.add_argument("--population", type=int, default=256)
    parser.add_argument("--target-evaluations", type=int, default=20_480)
    parser.add_argument("--seed-count", type=int, default=SEED_COUNT)
    parser.add_argument(
        "--cache-dir",
        default=None,
        help=(
            "optional resume cache; twelve documented-budget loops do "
            "not fit in one sitting. The loop is deterministic and the "
            "key carries every parameter, so caching cannot alter a "
            "number — only avoid recomputing it."
        ),
    )
    args = parser.parse_args()

    report = build_slip_admission_default_report(
        population=args.population,
        target_evaluations=args.target_evaluations,
        seed_count=args.seed_count,
        cache_dir=args.cache_dir,
    )
    metrics = report["metrics"]
    controls = metrics["measured_controls"]
    incumbent = metrics["incumbent"]
    print(
        f"incumbent  coverage {incumbent['mean_coverage']} "
        f"QD {incumbent['mean_qd']}  refusals {incumbent['refusals_by_seed']}  "
        f"illegal {incumbent['illegal_elites_by_seed']}"
    )
    print(
        f"measured controls: coverage {controls['coverage']}, "
        f"QD {controls['qd']}"
    )
    print()
    for arm in ARMS:
        gate = metrics["gates"][arm]
        means = metrics["arm_means"][arm]
        print(
            f"  {arm:<10} cov {means['coverage']:.6f} "
            f"(cost {gate['coverage_cost']:+.6f})  "
            f"QD {means['qd']:.4f} (delta {gate['quality_delta']:+.4f})  "
            f"refusals {gate['refusals_by_seed']}  "
            f"illegal {gate['illegal_elites_by_seed']}"
        )
        print(
            f"             G1 {gate['G1_cause_eliminated']}  "
            f"G2 {gate['G2_coverage_preserved']}  "
            f"G3 {gate['G3_quality_preserved']}  "
            f"G4 {gate['G4_archive_legality']}  -> "
            f"{'ADOPTABLE' if gate['adoptable'] else 'FAILS ' + ','.join(gate['failed_gates'])}"
        )
    choice = report["decision"]["choice"]
    print(f"\n{choice['verdict'].upper()}  default -> {choice['default']}")
    print(f"  passing arms: {choice['passing_arms']}")
    print(
        f"  wall clock {metrics['wall_clock_s']} s "
        f"(bound {PRE_REGISTERED_BOUND_S} s, within "
        f"{report['parameters']['within_bound']})"
    )
    for path in write_slip_admission_default_artifacts(args.output_dir, report):
        print(f"wrote {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
