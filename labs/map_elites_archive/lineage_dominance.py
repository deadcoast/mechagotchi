"""Cycle 22 L2: the documented lineage-dominance clause, judged at last.

`docs/project-research/deep-research/01/deep-research.md:205` states the
MAP-Elites evaluation gate in two halves:

    archive coverage >= 25% on a 576-cell repertoire after 20k
    evaluations; no single lineage > 40% of occupied cells

The coverage half has been judged five times — the Phase-E gate,
DR 0032's disposition, and K2's symmetric E4 re-run under the adopted
generation layer. **The dominance half has never been measured at all.**
It is not blocked and never was: the promoted `generate_candidate`
preserves `lineage.ancestor_ids` on every candidate it emits, so every
elite's founder has been recoverable for as long as the archive has
existed. It was simply never looked at — the same shape of omission
L1 found one task ago.

THE RULE IS PRE-REGISTERED HERE, BEFORE ANY RUN, and both outcomes are
first-class:

* A **lineage** is a founder line. An elite's founder is
  `lineage.ancestor_ids[0]` when ancestry is recorded (the promoted
  generator composes `[*parent_ancestors, parent_grid_id]`, so the list
  is oldest-first and element 0 is the origin of the line), and the
  elite's own `grid_id` when it has no recorded ancestry.
* `max_founder_share` = the largest share of OCCUPIED cells held by any
  single founder line.
* **pass** if `max_founder_share <= 0.40`; **refuse** otherwise. The
  documented wording is "> 40%", so exactly 40% is not a violation —
  the boundary is part of the rule and is pinned.

Nothing is re-scored after the fact, and a refusal ships as the finding
(the DR 0032 / DR 0041 precedent).

**One divergence is declared, not silently substituted.** The documented
clause pairs with a *576-cell* repertoire; this repo's proven geometry
is the *512-cell* 8x8x8 octile archive (DR 0029, E1), which is the
population every coverage judgement has also used. The dominance share
is a fraction of OCCUPIED cells, so it is well-defined either way — but
judging one bar against the other's population without saying so is
exactly the statistic error L1 caught in K2, so the artifact carries
both numbers and this module refuses to pretend they are the same.

This clause is also the quantitative form of **Evolution Q1**
(`research/questions.md`: "Can MAP-Elites preserve multiple companion
families instead of one dominant optimum?"), which Phase E answered
qualitatively — 52 recurrent families — but never against this bar.
"""

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from evaluation_loop_scale import (  # noqa: E402
    DEFAULT_LIFECYCLE_TICKS,
    DEFAULT_RNG_SEED,
    PRE_REGISTERED_BOUND_S,
    run_evaluation_loop,
)

ARTIFACT_ID = "lineage_dominance_stage0"
REPORT_DATE = "2026-07-26"

# The documented bar, verbatim from deep-research.md:205. A constant of
# the DOCUMENTATION, never tuned to the measurement.
DOMINANCE_BAR = 0.40

# The declared divergence (see the module docstring).
ARCHIVE_CELLS = 512
DOCUMENTED_REPERTOIRE_CELLS = 576

DOCUMENTED_RULE = (
    "pre-registered (cycle 22 L2), quoting deep-research.md:205 — "
    "\"no single lineage > 40% of occupied cells\". A lineage is a "
    "founder line (lineage.ancestor_ids[0], else the grid itself); "
    "pass if max_founder_share <= 0.40, refuse otherwise. Exactly 40% "
    "is not a violation, per the documented wording."
)

MAX_REPORTED_FOUNDERS = 25

DEFAULT_PARAMETERS = {
    "population": 256,
    "target_evaluations": 20_480,
    "rng_seed": DEFAULT_RNG_SEED,
    "lifecycle_ticks": DEFAULT_LIFECYCLE_TICKS,
}


def founder_of(entry: dict) -> str:
    """The founder of a grid's (or elite record's) line.

    `ancestor_ids` accumulates oldest-first — the promoted generator
    composes `[*parent_ancestors, parent_grid_id]` — so element 0 is
    the origin of the line. A creature with no recorded ancestry founds
    its own line; an ancestor is never invented.
    """
    lineage = entry.get("lineage")
    ancestors = lineage.get("ancestor_ids") if isinstance(lineage, dict) else None
    if isinstance(ancestors, list) and ancestors:
        return str(ancestors[0])
    return str(entry.get("grid_id"))


def judge_dominance(max_founder_share: float) -> dict:
    """Apply the pre-registered rule. Both verdicts are first-class."""
    return {
        "verdict": "pass" if max_founder_share <= DOMINANCE_BAR else "refuse",
        "max_founder_share": round(max_founder_share, 6),
        "bar": DOMINANCE_BAR,
        "rule": DOCUMENTED_RULE,
    }


def build_lineage_dominance_report(
    *,
    population: int = DEFAULT_PARAMETERS["population"],
    target_evaluations: int = DEFAULT_PARAMETERS["target_evaluations"],
    rng_seed: int = DEFAULT_PARAMETERS["rng_seed"],
    lifecycle_ticks: int = DEFAULT_PARAMETERS["lifecycle_ticks"],
) -> dict:
    started = time.perf_counter()
    result = run_evaluation_loop(
        population=population,
        target_evaluations=target_evaluations,
        rng_seed=rng_seed,
        lifecycle_ticks=lifecycle_ticks,
        generation="constrained",
        collect_lineage=True,
    )
    wall_clock_s = round(time.perf_counter() - started, 3)

    collection = result["lineage_collection"]
    elites = collection["elites"]
    occupied = collection["occupied_niches"]

    founders: Counter[str] = Counter()
    depths: Counter[str] = Counter()
    self_founded = 0
    for record in elites:
        founders[founder_of(record)] += 1
        lineage = record.get("lineage") or {}
        depths[str(lineage.get("generation"))] += 1
        if not (lineage.get("ancestor_ids") or []):
            self_founded += 1

    share = {name: count / occupied for name, count in founders.items()} if occupied else {}
    max_share = max(share.values()) if share else 0.0
    judged = judge_dominance(max_share)

    # Concentration beyond the single-largest line: how many founders
    # it takes to hold half the archive. A clause about ONE lineage
    # cannot see a cartel of three, so the instrument reports both.
    ranked = founders.most_common()
    cumulative = 0
    founders_for_half = 0
    for _, count in ranked:
        cumulative += count
        founders_for_half += 1
        if cumulative * 2 >= occupied:
            break

    metrics = {
        "occupied_niches": occupied,
        "archive_cells": ARCHIVE_CELLS,
        "documented_repertoire_cells": DOCUMENTED_REPERTOIRE_CELLS,
        "repertoire_divergence_note": (
            "the documented clause pairs with a 576-cell repertoire; "
            "this archive's proven geometry is 512 (8x8x8 octiles, "
            "DR 0029/E1) — the same population every coverage "
            "judgement has used. The share is a fraction of OCCUPIED "
            "cells and so is well-defined under either, but the two "
            "are named separately rather than silently equated."
        ),
        "distinct_founders": len(founders),
        "max_founder_share": round(max_share, 6),
        "founders_holding_half_the_archive": founders_for_half,
        "self_founded_elites": self_founded,
        "founder_histogram": dict(ranked[:MAX_REPORTED_FOUNDERS]),
        "founder_share": {name: round(value, 6) for name, value in share.items()},
        "elite_lineage_depth_histogram": dict(depths.most_common()),
        "reported_founder_cap": MAX_REPORTED_FOUNDERS,
        "wall_clock_s": wall_clock_s,
        "pre_registered_bound_s": PRE_REGISTERED_BOUND_S,
        "within_bound": wall_clock_s <= PRE_REGISTERED_BOUND_S,
    }

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0",
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 22 L2: judge the documented MAP-Elites gate's second "
            "clause — 'no single lineage > 40% of occupied cells' "
            "(deep-research.md:205) — which has never been measured."
        ),
        "source_artifacts": [
            "data/archives/evaluation_loop_scale_stage0.json",
            "data/archives/generation_arm_evolution_stage0.json",
            "data/archives/recurrent_families_stage0.json",
        ],
        "parameters": {
            "population": population,
            "target_evaluations": target_evaluations,
            "rng_seed": rng_seed,
            "lifecycle_ticks": lifecycle_ticks,
            "generation": "constrained (the DR 0042 adopted default)",
            "selection": "novelty_first (the DR 0040 adopted default)",
        },
        "metrics": metrics,
        "closed_states": [
            "the documented lineage-dominance clause is measured, not "
            "merely cited",
            "the founder rule is derived from the engine's own recorded "
            "ancestry and lives in one pinned place",
            "the 576-vs-512 repertoire divergence is declared in the "
            "artifact rather than silently substituted",
        ],
        "blocked_states": [
            "the clause judges a SINGLE lineage; concentration across "
            "several founder lines is reported as an observation "
            "(founders_holding_half_the_archive) and is NOT part of the "
            "documented bar",
            "one seed, one parameter set — E4's ten-seed protocol is "
            "what any distributional claim would need",
            "a founder line is not the same object as an E5 recurrent "
            "morphological family: one is ancestry, the other is "
            "descriptor similarity. The two are not compared here",
        ],
        "decision": {
            "verdict": judged["verdict"],
            "max_founder_share": judged["max_founder_share"],
            "bar": judged["bar"],
            "rule": judged["rule"],
        },
        "next_research_step": (
            "L3: the derivation edges re-derived under the adopted "
            "generation layer (K3's named geometry question)."
        ),
    }


def write_lineage_dominance_artifacts(
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
    parser.add_argument(
        "--population", type=int, default=DEFAULT_PARAMETERS["population"]
    )
    parser.add_argument(
        "--target-evaluations",
        type=int,
        default=DEFAULT_PARAMETERS["target_evaluations"],
    )
    parser.add_argument(
        "--rng-seed", type=int, default=DEFAULT_PARAMETERS["rng_seed"]
    )
    args = parser.parse_args()

    report = build_lineage_dominance_report(
        population=args.population,
        target_evaluations=args.target_evaluations,
        rng_seed=args.rng_seed,
    )
    metrics = report["metrics"]
    decision = report["decision"]
    print(
        f"occupied {metrics['occupied_niches']} / {ARCHIVE_CELLS} cells; "
        f"{metrics['distinct_founders']} founder lines"
    )
    print(
        f"max founder share {decision['max_founder_share']} vs bar "
        f"{decision['bar']} -> {decision['verdict'].upper()}"
    )
    print(
        "founders holding half the archive: "
        f"{metrics['founders_holding_half_the_archive']}"
    )
    for name, count in list(metrics["founder_histogram"].items())[:6]:
        print(f"   {count:5}  {name}")
    for path in write_lineage_dominance_artifacts(args.output_dir, report):
        print(f"wrote {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
