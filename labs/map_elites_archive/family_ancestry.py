"""Cycle 23 M4: ancestry versus morphology — do the recurrent families share ancestors?

L2 named the question and never asked it:

> Phase E measured **recurrent morphological families** by coarse-descriptor
> intersection across ten seeds; L2 measured **founder lines** by recorded
> ancestry. They are different objects — descriptor similarity versus who
> descends from whom — and both are now exposed. Do morphologically-recurrent
> families trace to common ancestors, or **converge from different lines**?

Convergence would be a genuine ALife result about the descriptor space
rather than a bookkeeping fact, and it bears directly on **Evolution Q3**
(*"Can lineage continuity be measured independently from visual
novelty?"*).

**WHY THE QUESTION IS ASKABLE NOW, AND WAS NOT IN PHASE E.** E5 chose
descriptor clustering over ancestry for a stated reason: *"the WFC parent
path retrains on the whole elite pool, so children carry no single
parent"*. That was true of the incumbent generation layer at the time.
Since **DR 0042** the loop's default is `constrained`, whose promoted
`generate_candidate` preserves `lineage.ancestor_ids` on every candidate
it emits — which is exactly what L2 exploited. E5's blocker is therefore
**retired by the adopted layer**, not worked around here.

**AND THE QUESTION HAS TO BE RESHAPED BEFORE IT CAN BE ANSWERED.** Asking
whether recurrent families share ancestry *across runs* is **not well
posed**: every run builds its own bootstrap population, so a founder id
in one run is not the same object as a founder id in another. The
ancestry spaces are disjoint. Families recur **morphologically**; their
ancestry cannot recur, because there is no shared ancestor pool to recur
in. The well-posed question, asked here, is:

> **Within a run, do elites sharing a coarse morphological family share a
> founder more often than chance?** — and is the answer consistent across
> independent runs?

THE RULE IS PRE-REGISTERED HERE, BEFORE ANY RUN.

* **The statistic** — the mean, over families with at least two members,
  of the family's **largest-founder share**. Single-member families are
  **excluded and counted**: their share is 1.0 by construction and
  including them would manufacture common descent out of arithmetic.
* **The null is MEASURED by shuffling**, never assumed: founder labels
  are permuted across elites — preserving both the family sizes and the
  founder-line sizes exactly, so the null differs from the observation
  only in the *pairing* — and the statistic recomputed over many rounds.
  That is what "more than chance" has to mean here.
* **The rule** — ``common_descent`` when the observed share stands at
  least ``COMMON_DESCENT_Z`` standard deviations above the shuffled
  null; ``convergent`` otherwise.
* **``convergent`` is the NULL, and the module says so.** It is an
  *absence of evidence* for common descent, not positive proof of
  convergence. The positive evidence is reported separately and
  independently: the **mean number of distinct founder lines per
  family**.

Both the family rule (``recurrent_families.family_key``) and the founder
rule (``lineage_dominance.founder_of``) are **imported, never
re-implemented**, so this study cannot quietly measure different objects
than the two it is comparing.

**This module adopts nothing.** It answers a documented open question.
"""

import argparse
import json
import random
import sys
import time
from pathlib import Path
from statistics import mean, pstdev

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from evaluation_loop_scale import (  # noqa: E402
    DEFAULT_LIFECYCLE_TICKS,
    DEFAULT_RNG_SEED,
    PRE_REGISTERED_BOUND_S as LOOP_BOUND_S,
    run_evaluation_loop,
)
from lineage_dominance import founder_of  # noqa: E402
from recurrent_families import (  # noqa: E402
    ARTIFACT_ID as E5_ARTIFACT_ID,
    COARSENING_FACTOR,
    cluster_families,
    family_key,
    find_recurrent_families,
)

ARTIFACT_ID = "family_ancestry_stage0"
REPORT_DATE = "2026-07-27"

# Pre-registered: how many standard deviations above the MEASURED
# shuffled null the observed concentration must stand before common
# descent is claimed.
COMMON_DESCENT_Z = 2.0

DEFAULT_SHUFFLE_ROUNDS = 200
DEFAULT_RNG_SEEDS = (DEFAULT_RNG_SEED, DEFAULT_RNG_SEED + 1, DEFAULT_RNG_SEED + 2)

# Three loops at the documented budget, bound DERIVED from the loop's own
# registered bound rather than picked (DR 0028).
PRE_REGISTERED_BOUND_S = 3 * LOOP_BOUND_S

PRE_REGISTERED_RULE = (
    "pre-registered (cycle 23 M4): the statistic is the mean "
    "largest-founder share over families with >= 2 members "
    "(single-member families excluded and counted — their share is 1.0 "
    "by construction). The null is MEASURED by permuting founder labels "
    "across elites, preserving both family sizes and founder-line sizes "
    "so the null differs from the observation only in the pairing. "
    f"Verdict 'common_descent' when the observed share stands >= "
    f"{COMMON_DESCENT_Z} standard deviations above that null, "
    "'convergent' otherwise. 'convergent' IS THE NULL — an absence of "
    "evidence for common descent, never positive proof of convergence; "
    "the positive evidence is reported separately as the mean number of "
    "distinct founder lines per family."
)

CROSS_RUN_NOT_WELL_POSED = (
    "Asking whether recurrent families share ancestry ACROSS runs is "
    "not well posed, and that is a structural fact rather than a "
    "budget limit: every run builds its own bootstrap population, so a "
    "founder id in one run is not the same object as a founder id in "
    "another and the ancestry spaces are disjoint. Families recur "
    "MORPHOLOGICALLY; their ancestry cannot recur, because there is no "
    "shared ancestor pool for it to recur in. The question is therefore "
    "asked WITHIN each run and its answer compared across runs."
)


def family_founder_stats(elites: list[dict]) -> dict:
    """Founder concentration within morphological families.

    ``elites`` carry a ``family`` key and a ``founder`` key. Families with
    a single member are excluded (share 1.0 by construction) and counted.
    """
    grouped: dict[tuple[int, ...], list[str]] = {}
    for record in elites:
        grouped.setdefault(record["family"], []).append(record["founder"])

    scored = {key: names for key, names in grouped.items() if len(names) >= 2}
    excluded = len(grouped) - len(scored)
    if not scored:
        raise ValueError(
            "no family has two or more members: there is nothing to "
            "compare against chance, and averaging single-member "
            "families would report 1.0 as if it were a measurement"
        )

    shares = []
    distinct = []
    for names in scored.values():
        counts: dict[str, int] = {}
        for name in names:
            counts[name] = counts.get(name, 0) + 1
        shares.append(max(counts.values()) / len(names))
        distinct.append(len(counts))

    return {
        "families_total": len(grouped),
        "families_scored": len(scored),
        "single_member_families_excluded": excluded,
        "mean_largest_founder_share": round(mean(shares), 6),
        "mean_distinct_founders_per_family": round(mean(distinct), 6),
        "max_distinct_founders_in_a_family": max(distinct),
        "scored_members": sum(len(names) for names in scored.values()),
    }


def shuffled_null(
    elites: list[dict], *, rounds: int = DEFAULT_SHUFFLE_ROUNDS, rng_seed: int
) -> dict:
    """The MEASURED null: founder labels permuted, marginals preserved."""
    founders = [record["founder"] for record in elites]
    families = [record["family"] for record in elites]
    rng = random.Random(rng_seed)
    samples = []
    for _ in range(rounds):
        shuffled = founders[:]
        rng.shuffle(shuffled)
        samples.append(
            family_founder_stats(
                [
                    {"family": family, "founder": founder}
                    for family, founder in zip(families, shuffled)
                ]
            )["mean_largest_founder_share"]
        )
    return {
        "rounds": rounds,
        "mean": round(mean(samples), 6),
        "stdev": round(pstdev(samples), 6),
        "min": round(min(samples), 6),
        "max": round(max(samples), 6),
        # Pinned: the permutation preserves the founder multiset exactly.
        "founder_multiset": sorted(founders),
    }


def judge_ancestry(
    *, observed: float, null_mean: float, null_stdev: float
) -> dict:
    """Apply the pre-registered rule. Both verdicts are first-class."""
    if null_stdev <= 0.0:
        raise ValueError(
            "the shuffled null must have positive spread — a zero "
            "spread would make every deviation infinitely significant; "
            "measure it, never assume it"
        )
    # Judged on the ROUNDED z — the same value the artifact reports.
    # Judging on the raw float would let a verdict contradict its own
    # published number: at the boundary (0.5 - 0.4) / 0.05 evaluates to
    # 1.9999999999999996, which reports as 2.0 and would refuse. That is
    # float representation, not science (the L2 precedent, where a pin
    # asserting rounded shares summed to 1.0 failed at 1.000003 and was
    # replaced for asserting rounding rather than a measurement).
    z = round((observed - null_mean) / null_stdev, 6)
    common = z >= COMMON_DESCENT_Z
    return {
        "verdict": "common_descent" if common else "convergent",
        "observed": round(observed, 6),
        "null_mean": round(null_mean, 6),
        "null_stdev": round(null_stdev, 6),
        "z": z,
        "bar_z": COMMON_DESCENT_Z,
        "interpretation": (
            "families are more founder-homogeneous than chance: the "
            "morphology travels with a lineage"
            if common
            else (
                "families are no more founder-homogeneous than chance. "
                "This is an ABSENCE OF EVIDENCE for common descent, not "
                "positive proof of convergence — the positive evidence "
                "is the distinct-founder count reported beside it"
            )
        ),
        "rule": PRE_REGISTERED_RULE,
    }


def _run_elites(
    *, rng_seed: int, population: int, target_evaluations: int, lifecycle_ticks: int
) -> list[dict]:
    """One loop's elites, carrying BOTH their family and their founder."""
    result = run_evaluation_loop(
        population=population,
        target_evaluations=target_evaluations,
        rng_seed=rng_seed,
        lifecycle_ticks=lifecycle_ticks,
        generation="constrained",
        collect_lineage=True,
    )
    lineage_by_niche = {
        record["niche"]: record
        for record in result["lineage_collection"]["elites"]
    }
    elites = []
    for record in result["elite_records"]:
        lineage_record = lineage_by_niche[record["niche"]]
        elites.append(
            {
                "niche": record["niche"],
                "grid_id": record["grid_id"],
                "descriptor": record["descriptor"],
                "axis_values": record["axis_values"],
                "fitness": record["fitness"],
                "family": family_key(record["descriptor"]),
                "founder": founder_of(lineage_record),
            }
        )
    return elites


def _e5_recurrence() -> dict:
    """The committed E5 artifact's own count, read rather than quoted.

    The number moved 52 -> 54 when the DR 0038 vocabulary landed (the
    commit message records it) and the prose never followed. This study
    reads the artifact and recomputes from its own records, so it can
    never repeat a stale figure from a document.
    """
    path = ROOT / "data" / "archives" / f"{E5_ARTIFACT_ID}.json"
    artifact = json.loads(path.read_text(encoding="utf-8"))
    metrics = artifact["metrics"]
    return {
        "artifact": path.relative_to(ROOT).as_posix(),
        "committed_recurrent_family_count": metrics["verdict"][
            "recurrent_family_count"
        ],
        "recomputed_from_artifact": len(metrics["recurrent_families"]),
        "runs_analyzed": metrics["protocol"]["runs_analyzed"],
        "stale_prose_note": (
            "Documents across research/ state 52. The committed artifact "
            "says 54: the count moved when the DR 0038 vocabulary "
            "regenerated E4's elite rosters (commit f8c171b's own message "
            "records 'recurrent families 52 -> 54'), and the prose was "
            "never updated. The historical documents stay true as what "
            "they measured under the pre-DR-0038 vocabulary; dated notes "
            "now sit beside them."
        ),
    }


def build_family_ancestry_report(
    *,
    population: int = 256,
    target_evaluations: int = 20_480,
    rng_seeds: tuple[int, ...] = DEFAULT_RNG_SEEDS,
    lifecycle_ticks: int = DEFAULT_LIFECYCLE_TICKS,
    shuffle_rounds: int = DEFAULT_SHUFFLE_ROUNDS,
) -> dict:
    started = time.perf_counter()

    runs = []
    rosters = []
    for rng_seed in rng_seeds:
        elites = _run_elites(
            rng_seed=rng_seed,
            population=population,
            target_evaluations=target_evaluations,
            lifecycle_ticks=lifecycle_ticks,
        )
        rosters.append(elites)
        stats = family_founder_stats(elites)
        null = shuffled_null(
            elites, rounds=shuffle_rounds, rng_seed=rng_seed
        )
        judged = judge_ancestry(
            observed=stats["mean_largest_founder_share"],
            null_mean=null["mean"],
            null_stdev=null["stdev"],
        )
        runs.append(
            {
                "rng_seed": rng_seed,
                "elites": len(elites),
                "distinct_founders": len({e["founder"] for e in elites}),
                **stats,
                "null": {k: v for k, v in null.items() if k != "founder_multiset"},
                "z": judged["z"],
                "verdict": judged["verdict"],
            }
        )

    verdicts = {run["verdict"] for run in runs}
    consistent = len(verdicts) == 1
    overall = verdicts.pop() if consistent else "inconsistent_across_runs"

    # Families occupied in EVERY run of THIS study — E5's recurrence rule
    # applied to these rosters. Reported for its morphology only; founder
    # identity across runs is not well posed (see the module docstring).
    recurrent_here = find_recurrent_families(rosters)

    wall_clock_s = round(time.perf_counter() - started, 3)

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0",
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 23 M4: ask L2's named question — do morphologically "
            "recurrent families trace to common ancestors, or converge "
            "from different founder lines? (Evolution Q3.) The question "
            "is reshaped first, because asking it across runs is not "
            "well posed."
        ),
        "source_artifacts": [
            "data/archives/recurrent_families_stage0.json",
            "data/archives/lineage_dominance_stage0.json",
            "data/archives/coverage_qd_gates_stage0.json",
            "data/archives/elite_population_measures_stage0.json",
            "data/archives/evaluation_loop_scale_stage0.json",
        ],
        "parameters": {
            "population": population,
            "target_evaluations": target_evaluations,
            "rng_seeds": list(rng_seeds),
            "lifecycle_ticks": lifecycle_ticks,
            "shuffle_rounds": shuffle_rounds,
            "coarsening_factor": COARSENING_FACTOR,
            "generation": "constrained (the DR 0042 adopted default)",
            "family_rule": "recurrent_families.family_key (imported)",
            "founder_rule": "lineage_dominance.founder_of (imported)",
        },
        "metrics": {
            "runs": runs,
            "verdict_consistent_across_runs": consistent,
            "e5_recurrence": _e5_recurrence(),
            "recurrent_families_in_this_study": len(recurrent_here),
            "wall_clock_s": wall_clock_s,
            "pre_registered_bound_s": PRE_REGISTERED_BOUND_S,
            "within_bound": wall_clock_s <= PRE_REGISTERED_BOUND_S,
        },
        "closed_states": [
            "L2's named question is asked for the first time, with the "
            "family rule and the founder rule both IMPORTED from the "
            "instruments that own them",
            "the null is MEASURED by permutation with both marginals "
            "preserved, so 'more than chance' has an operational meaning",
            "single-member families are excluded and counted rather than "
            "averaged in at a structural 1.0",
            "E5's stated reason for using descriptor clustering instead "
            "of ancestry (the WFC parent path carrying no single parent) "
            "is retired by DR 0042's adopted constrained layer, which "
            "records ancestry on every candidate",
            "the committed E5 recurrent-family count is READ from the "
            "artifact, not quoted from prose that has gone stale",
        ],
        "blocked_states": [
            CROSS_RUN_NOT_WELL_POSED,
            "the statistic covers EVERY family in each run with >= 2 "
            "members, not only the families common to all runs. Review "
            "flagged the mismatch against the report's 'recurrent "
            "families' framing and it is real but bounded: the "
            "intersection here is 63 while the runs carry 63/64/64 "
            "families, so at most ONE non-recurrent family per run "
            "enters the mean and its null. It is recorded rather than "
            "re-scored — restricting the statistic after seeing the "
            "numbers is exactly the re-scoring this repo forbids (M1's "
            "size-matched-control precedent), and the verdict is not "
            "close to its bar at z +21.39 / +15.96 / +17.39. A "
            "recurrent-only variant is named for whoever runs it next",
            "'convergent' is the NULL: it is an absence of evidence for "
            "common descent, never positive proof of convergence. The "
            "positive evidence is the distinct-founder count, reported "
            "separately and never folded into the verdict",
            "a coarse family is E5's 4x4x4 cell, which is a descriptor "
            "region rather than a visually-verified morphological type; "
            "whether members of one cell look alike to a human is the "
            "owner-deferred survey's question and no proxy is offered",
            "DR 0046's comparability rule applies: these descriptors are "
            "incumbent-geometry addresses and may not be read against "
            "probe-geometry counts",
        ],
        "decision": {
            "verdict": overall,
            "consistent_across_runs": consistent,
            "per_run": {
                str(run["rng_seed"]): {
                    "verdict": run["verdict"],
                    "z": run["z"],
                    "mean_largest_founder_share": run[
                        "mean_largest_founder_share"
                    ],
                    "mean_distinct_founders_per_family": run[
                        "mean_distinct_founders_per_family"
                    ],
                }
                for run in runs
            },
            "rule": PRE_REGISTERED_RULE,
        },
        "next_research_step": (
            "M5: the documented visible companion state — the GAME-track "
            "slice; five of the eight documented visible axes have no "
            "engine field."
        ),
    }


def write_family_ancestry_artifacts(
    output_dir: str | Path, report: dict
) -> list[Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{ARTIFACT_ID}.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return [path]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(ROOT / "data" / "archives"))
    parser.add_argument("--population", type=int, default=256)
    parser.add_argument("--target-evaluations", type=int, default=20_480)
    parser.add_argument(
        "--shuffle-rounds", type=int, default=DEFAULT_SHUFFLE_ROUNDS
    )
    args = parser.parse_args()

    report = build_family_ancestry_report(
        population=args.population,
        target_evaluations=args.target_evaluations,
        shuffle_rounds=args.shuffle_rounds,
    )
    metrics, decision = report["metrics"], report["decision"]
    rec = metrics["e5_recurrence"]
    print(
        f"E5 committed recurrent families: "
        f"{rec['committed_recurrent_family_count']} "
        f"(prose across research/ says 52)"
    )
    for run in metrics["runs"]:
        print(
            f"  seed {run['rng_seed']}: {run['families_scored']} scorable "
            f"families ({run['single_member_families_excluded']} single "
            f"excluded), share {run['mean_largest_founder_share']:.6f} vs "
            f"null {run['null']['mean']:.6f}±{run['null']['stdev']:.6f} "
            f"(z {run['z']:+.2f}) -> {run['verdict'].upper()}"
        )
        print(
            f"      distinct founders per family: "
            f"{run['mean_distinct_founders_per_family']:.4f} "
            f"(max {run['max_distinct_founders_in_a_family']}), "
            f"{run['distinct_founders']} founder lines over "
            f"{run['elites']} elites"
        )
    print(
        f"VERDICT: {decision['verdict'].upper()} "
        f"(consistent across runs: {decision['consistent_across_runs']})"
    )
    for path in write_family_ancestry_artifacts(args.output_dir, report):
        print(f"wrote {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
