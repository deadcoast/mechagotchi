"""Cycle 23 M1: the archive measured on its own inhabitants.

Phase L produced one finding it never planned for, and it arrived four
separate times without anyone looking for it:

    Every instrument measures a different population from the one the
    archive is actually filled with.

L1 found the elites that hold niches forever are SLIP-illegal
**bootstrap** creatures. L2 found the dominant founder lines are
bootstrap-founded, not seed-founded. L3 found the geometry is calibrated
on ``build_population`` while the archive is filled by
``generate_candidate`` — and its one attempt to measure that stream
produced 120 of 600 requested, a bound only. L4 judged a candidate axis
on the derivation population *because that is what every instrument
uses*, and named the gap in its own remainder.

This module turns the instruments around. It re-measures, on the loop's
**steady-state elites**, the three things the ledger reports from the
derivation population:

1. the **descriptor distribution** — where the population falls in the
   frozen (incumbent) octile geometry, per axis;
2. **octile occupancy** — how many of the eight octiles per axis carry
   any weight at all, and how far the shape sits from the uniform 1/8
   split the geometry is *defined* to produce on its calibration
   population;
3. **L4's ``animation_density`` candidate** — as far as it can honestly
   be carried (see THE UNDEFINED GATES below).

THE RULE IS PRE-REGISTERED HERE, BEFORE ANY RUN.

The queue's own warning is the design constraint: *"pre-register what
counts as a material difference before running, so 'the elites look
different' cannot become a conclusion in search of a bar."* So:

* The statistic is the **total variation distance** between two octile
  histograms — a shape comparison, because the elite set (~460) and the
  derivation population (600) differ in size by construction and
  comparing counts would report a difference for two identical
  distributions.
* The bar is **MEASURED, never a constant** (L3's precedent). The same
  population *type* is drawn twice at different seeds and the statistic
  is computed between those two draws: that is how far it moves for
  reasons that are not the population type. Two controls are measured,
  one per type — a derivation control (cheap) **and an elite control
  (a second full loop)** — and the bar takes the **larger** of the two.
  The elite set is an extreme-value selection from a stochastic
  process, so assuming it is no more variable than a plain draw would
  understate the control and make "material" too easy to claim.
* A difference is **material** only at
  ``>= MATERIAL_CONTROL_FACTOR x control``; otherwise
  ``within_sampling_noise``. Both verdicts are first-class, and
  "the elites are indistinguishable from the derivation population"
  is a real, publishable outcome of this study.

THE UNDEFINED GATES — stated before the run, not discovered after.

L4's remainder says ``animation_density`` was "judged on the derivation
population, not on the loop's elites". Carrying that out shows the
remainder was **understated**: two of L4's four gates cannot be measured
on the elite population *at all*, and not for want of budget.

The archive holds **exactly one elite per niche**. Therefore:

* **A3 (discrimination)** — "among population pairs sharing the SAME
  three-axis bin, what fraction land in different animation octiles?" —
  has a structurally **zero denominator** among elites. No two elites
  share a three-axis bin; that is what a niche *is*.
* **A4 (coverage cost)** — "occupied cells at 3 axes vs at 4" — is
  degenerate for the same reason: every elite already occupies a
  distinct 3-axis cell, so adding a fourth axis maps each to a distinct
  4-axis cell and ``occupied_4 == occupied_3`` by construction, for any
  fourth axis whatsoever.

These are reported as **undefined**, with the reason, and **no number is
substituted for them** — not a zero, not a proxy. What *would* answer
L4's question is the loop's **scored candidate stream** (every creature
evaluated, not only the winners), which is a different seam and a
different slice; it is named here as a remainder rather than smuggled in.

A1 (spread) and A2 (independence) *are* defined on the elites and are
re-measured.

**This module is an INSTRUMENT.** It changes no geometry, adopts
nothing, and moves no bar. L4's verdict
(``adoptable_pending_blocked_clause``) is untouched: the documented
interpretability clause still needs the owner-deferred human panel, and
nothing here substitutes for it.
"""

import argparse
import json
import sys
import time
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from niche_scale_archive import (  # noqa: E402
    DEFAULT_RNG_SEED,
    EVALUATION_STREAM_OFFSET,
    SCALE_DESCRIPTOR_NAMES,
    build_population,
    derive_scale_bin_edges,
    edge_diagnostics,
    scale_axis_values,
    _load_default_slip,
)
from corpus_builder import build_seed_grids_16  # noqa: E402
from wfc_grid import split_corpus, train_wfc_model  # noqa: E402
from wfc_population_throughput import load_frozen_scale_edges  # noqa: E402

from evaluation_loop_scale import (  # noqa: E402
    DEFAULT_LIFECYCLE_TICKS,
    PRE_REGISTERED_BOUND_S as LOOP_BOUND_S,
    run_evaluation_loop,
)

# The axis is L4's, imported and never redefined: a re-measure that
# re-implemented the definition would be measuring a different thing
# under the same name. `pearson` likewise — one implementation, pinned.
from animation_density_axis import (  # noqa: E402
    ANIMATING_ROLES,
    animation_density,
    pearson,
)

ARTIFACT_ID = "elite_population_measures_stage0"
REPORT_DATE = "2026-07-27"

# Pre-registered: how many times the MEASURED control a difference must
# exceed before it is called material. L3's factor, and the same
# conservative direction — here it resists calling a difference real.
MATERIAL_CONTROL_FACTOR = 2.0

# DR 0028 discipline, pre-registered BEFORE the run: measuring an elite
# control means running the documented-budget loop TWICE, so the bound
# is DERIVED from the loop's own pre-registered bound rather than picked
# — two loops plus two derivation draws. If stdlib could not hold at
# this cost, the record would cite the measurement.
PRE_REGISTERED_BOUND_S = 2 * LOOP_BOUND_S

PRE_REGISTERED_RULE = (
    "pre-registered (cycle 23 M1), both verdicts first-class: a "
    "derivation-vs-elite difference in a descriptor's octile "
    "distribution is MATERIAL only at >= "
    f"{MATERIAL_CONTROL_FACTOR}x the MEASURED sampling control, and "
    "'within_sampling_noise' otherwise. The control is the same "
    "statistic computed between two draws of the SAME population type "
    "at different seeds — measured once per type (derivation and "
    "elite), with the LARGER taken, because the elite set is an "
    "extreme-value selection from a stochastic process and assuming it "
    "is no more variable than a plain draw would understate the bar. "
    "The bar derives from evidence, never from a constant, and this "
    "instrument moves no geometry and adopts nothing."
)

# The structural reasons two of L4's four gates cannot be measured on
# this population. Stated before the run; no number is substituted.
_ONE_PER_NICHE = (
    "the archive holds exactly one elite per niche, so no two elites "
    "can share a three-axis bin"
)

UNDEFINED_ON_ELITES = {
    "A3_discrimination": (
        f"UNDEFINED, not un-run: {_ONE_PER_NICHE}. L4's A3 asks what "
        "fraction of same-three-axis-bin PAIRS land in different "
        "animation octiles; among elites that denominator is "
        "structurally zero. No value is reported — a 0.0 here would "
        "read as 'the axis discriminates nothing', which is the "
        "opposite of what the structure says."
    ),
    "A4_coverage_cost": (
        f"UNDEFINED, not un-run: {_ONE_PER_NICHE}, so every elite "
        "already occupies a distinct 3-axis cell and any fourth axis "
        "maps it to a distinct 4-axis cell — occupied_4 == occupied_3 "
        "by construction, for ANY fourth axis. The cost of a fourth "
        "axis is a property of a POPULATION, not of an elite set."
    ),
}

# The statistics judged against the measured control. Named here so the
# control, the difference and the verdict cannot drift apart.
JUDGED_STATISTICS = (*SCALE_DESCRIPTOR_NAMES, "animation_density")


def octile_histogram(values: list[float], edges: list[float]) -> list[int]:
    """Bin values into ``len(edges) + 1`` octiles.

    The boundary convention is ``value >= edge`` steps up, matching
    ``niche_scale_archive._bin`` and L3's ``octile_occupancy`` exactly —
    a histogram binned the other way would not be comparable with any
    number already in the ledger.
    """
    counts = [0] * (len(edges) + 1)
    for value in values:
        index = 0
        while index < len(edges) and value >= edges[index]:
            index += 1
        counts[index] += 1
    return counts


def histogram_tvd(first: list[int], second: list[int]) -> float:
    """Total variation distance between two histograms' SHAPES.

    Normalised per histogram, because the elite set and the derivation
    population differ in size by construction; comparing raw counts
    would report a large difference between two identical distributions.
    """
    if len(first) != len(second):
        raise ValueError(
            "histograms must share a geometry to be compared: "
            f"{len(first)} bins vs {len(second)}"
        )
    total_first, total_second = sum(first), sum(second)
    if total_first <= 0 or total_second <= 0:
        raise ValueError(
            "an empty population has no distribution to compare: "
            f"totals {total_first} and {total_second}"
        )
    return round(
        0.5
        * sum(
            abs(a / total_first - b / total_second)
            for a, b in zip(first, second)
        ),
        6,
    )


def judge_material(*, difference: float, control: float) -> dict:
    """Apply the pre-registered rule. Both verdicts are first-class."""
    if control <= 0.0:
        raise ValueError(
            "the sampling control must be positive — a zero control "
            "would make every difference infinitely significant; "
            "measure it, never assume it"
        )
    ratio = difference / control
    return {
        "verdict": (
            "material"
            if ratio >= MATERIAL_CONTROL_FACTOR
            else "within_sampling_noise"
        ),
        "difference": round(difference, 6),
        "control": round(control, 6),
        "ratio": round(ratio, 6),
        "factor": MATERIAL_CONTROL_FACTOR,
        "rule": PRE_REGISTERED_RULE,
    }


def same_three_axis_bin_pairs(descriptors: list[tuple[int, ...]]) -> int:
    """L4's A3 denominator: pairs sharing a three-axis bin.

    Measured rather than argued, so the structural zero among elites is
    evidence in the artifact instead of a claim in prose.
    """
    counts: dict[tuple[int, ...], int] = {}
    for descriptor in descriptors:
        counts[descriptor] = counts.get(descriptor, 0) + 1
    return sum(n * (n - 1) // 2 for n in counts.values())


def elite_animation_density(grid: dict) -> float:
    """L4's axis, applied to an elite grid. One definition, imported."""
    return animation_density(grid)


def _axis_samples(population: list[dict], slip_profile: dict) -> dict:
    samples: dict[str, list[float]] = {
        name: [] for name in SCALE_DESCRIPTOR_NAMES
    }
    samples["animation_density"] = []
    for grid in population:
        values = scale_axis_values(grid, slip_profile=slip_profile)
        for name in SCALE_DESCRIPTOR_NAMES:
            samples[name].append(values[name])
        samples["animation_density"].append(elite_animation_density(grid))
    return samples


def _histograms(samples: dict, frozen: dict, density_edges: list[float]) -> dict:
    histograms = {
        name: octile_histogram(samples[name], frozen[name])
        for name in SCALE_DESCRIPTOR_NAMES
    }
    histograms["animation_density"] = octile_histogram(
        samples["animation_density"], density_edges
    )
    return histograms


def _distance(first: dict, second: dict) -> dict:
    return {
        name: histogram_tvd(first[name], second[name])
        for name in JUDGED_STATISTICS
    }


def _elite_population(
    *,
    population: int,
    target_evaluations: int,
    rng_seed: int,
    lifecycle_ticks: int,
) -> tuple[list[dict], dict]:
    """The loop's steady-state elites, as whole grids, via the M1 seam."""
    result = run_evaluation_loop(
        population=population,
        target_evaluations=target_evaluations,
        rng_seed=rng_seed,
        lifecycle_ticks=lifecycle_ticks,
        generation="constrained",
        collect_elite_grids=True,
    )
    collection = result["elite_grid_collection"]
    grids = [record["grid"] for record in collection["elites"]]
    origins = {"bootstrap": 0, "loop_offspring": 0}
    for record in collection["elites"]:
        origins[record["origin"]] += 1
    context = {
        "occupied_niches": collection["occupied_niches"],
        "coverage": result["archive_summary"]["coverage"],
        "qd_score": result["archive_summary"]["qd_score"],
        "evaluations_total": result["evaluations_total"],
        "generations_run": len(result["trajectory"]),
        "elite_origin_counts": origins,
        "elite_origin_bootstrap_share": (
            round(origins["bootstrap"] / collection["occupied_niches"], 6)
            if collection["occupied_niches"]
            else 0.0
        ),
        "niches": [record["niche"] for record in collection["elites"]],
    }
    return grids, context


def build_elite_population_report(
    *,
    derivation_count: int = 600,
    population: int = 256,
    target_evaluations: int = 20_480,
    rng_seed: int = DEFAULT_RNG_SEED,
    control_rng_seed: int = DEFAULT_RNG_SEED + EVALUATION_STREAM_OFFSET,
    lifecycle_ticks: int = DEFAULT_LIFECYCLE_TICKS,
) -> dict:
    started = time.perf_counter()
    slip_profile = _load_default_slip()
    seeds = build_seed_grids_16()
    train, _, _ = split_corpus(seeds)
    wfc_model = train_wfc_model(train)
    frozen = load_frozen_scale_edges()

    # --- the two populations, and a control draw of each --------------
    derivation, derivation_composition = build_population(
        derivation_count, rng_seed, train, wfc_model
    )
    derivation_control, _ = build_population(
        derivation_count, control_rng_seed, train, wfc_model
    )
    elites, elite_context = _elite_population(
        population=population,
        target_evaluations=target_evaluations,
        rng_seed=rng_seed,
        lifecycle_ticks=lifecycle_ticks,
    )
    elites_control, elite_control_context = _elite_population(
        population=population,
        target_evaluations=target_evaluations,
        rng_seed=control_rng_seed,
        lifecycle_ticks=lifecycle_ticks,
    )

    samples = {
        "derivation": _axis_samples(derivation, slip_profile),
        "derivation_control": _axis_samples(derivation_control, slip_profile),
        "elite": _axis_samples(elites, slip_profile),
        "elite_control": _axis_samples(elites_control, slip_profile),
    }

    # The animation axis has no frozen edges — it is a CANDIDATE, and L4
    # never moved the geometry. Its octiles are derived from the
    # derivation population, so the elite histogram is read against the
    # same reference every other L4 number used.
    density_edges = derive_scale_bin_edges(samples["derivation"]["animation_density"])

    histograms = {
        key: _histograms(sample, frozen, density_edges)
        for key, sample in samples.items()
    }

    derivation_vs_elite = _distance(histograms["derivation"], histograms["elite"])
    derivation_control_distance = _distance(
        histograms["derivation"], histograms["derivation_control"]
    )
    elite_control_distance = _distance(
        histograms["elite"], histograms["elite_control"]
    )
    measured_controls = {
        name: max(
            derivation_control_distance[name], elite_control_distance[name]
        )
        for name in JUDGED_STATISTICS
    }
    judgements = {
        name: judge_material(
            difference=derivation_vs_elite[name],
            control=measured_controls[name],
        )
        for name in JUDGED_STATISTICS
    }

    driving_statistic = max(
        JUDGED_STATISTICS, key=lambda name: judgements[name]["ratio"]
    )
    headline = judgements[driving_statistic]

    # --- L4's gates, as far as they are DEFINED here ------------------
    elite_density = samples["elite"]["animation_density"]
    elite_density_edges = derive_scale_bin_edges(elite_density)
    a1 = edge_diagnostics(elite_density, elite_density_edges)
    correlations = {
        name: pearson(elite_density, samples["elite"][name])
        for name in SCALE_DESCRIPTOR_NAMES
    }
    measured_r = [abs(r) for r in correlations.values() if r is not None]
    max_abs_correlation = max(measured_r) if measured_r else 0.0

    # The structural zero, measured on the real archive.
    elite_descriptors = [
        tuple(int(part) for part in niche.split(","))
        for niche in elite_context["niches"]
    ]
    elite_same_bin_pairs = same_three_axis_bin_pairs(elite_descriptors)

    empty_octiles = {
        key: {
            name: sum(1 for count in histograms[key][name] if count == 0)
            for name in JUDGED_STATISTICS
        }
        for key in ("derivation", "elite")
    }

    wall_clock_s = round(time.perf_counter() - started, 3)

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0",
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 23 M1: re-measure the descriptor distribution, octile "
            "occupancy and L4's animation_density candidate against the "
            "loop's STEADY-STATE ELITES rather than the "
            "derivation/bootstrap population every instrument has used — "
            "Phase L's convergent finding, acted on. An INSTRUMENT: it "
            "changes no geometry and adopts nothing."
        ),
        "source_artifacts": [
            "data/archives/evaluation_loop_scale_stage0.json",
            "data/archives/geometry_consistency_stage0.json",
            "data/archives/animation_density_axis_stage0.json",
            "data/archives/lineage_dominance_stage0.json",
            "data/archives/generation_refusal_causes_stage0.json",
            "data/archives/niche_scale_archive_stage0.json",
        ],
        "parameters": {
            "derivation_count": derivation_count,
            "population": population,
            "target_evaluations": target_evaluations,
            "rng_seed": rng_seed,
            "control_rng_seed": control_rng_seed,
            "lifecycle_ticks": lifecycle_ticks,
            "generation": "constrained (the DR 0042 adopted default)",
            "selection": "novelty_first (the DR 0040 adopted default)",
            "geometry": (
                "incumbent (frozen train-derived edges) — the geometry "
                "coverage and QD are reported in, per L3; the candidate "
                "animation axis uses derivation-derived octiles, the "
                "same reference L4 used"
            ),
            "derivation_composition": derivation_composition,
            "animating_roles": sorted(ANIMATING_ROLES),
        },
        "metrics": {
            "elite_run": elite_context,
            "elite_control_run": elite_control_context,
            "sample_sizes": {
                key: len(sample["animation_density"])
                for key, sample in samples.items()
            },
            "frozen_edges": frozen,
            # The reference the candidate axis is binned against, recorded
            # so a reader can check it against L4's committed edges
            # without re-deriving it (same recipe, same seed, same count).
            "animation_density_reference_edges": density_edges,
            "octile_histograms": histograms,
            "derivation_vs_elite": derivation_vs_elite,
            "derivation_control": derivation_control_distance,
            "elite_control": elite_control_distance,
            "measured_controls": measured_controls,
            "judgements": judgements,
            "empty_octiles": empty_octiles,
            "animation_density_gates_on_elites": {
                "A1_spread": a1,
                "A2_independence": {
                    "correlation_with_incumbent": {
                        name: (None if r is None else round(r, 6))
                        for name, r in correlations.items()
                    },
                    "max_abs_correlation": round(max_abs_correlation, 6),
                },
            },
            "undefined_on_elites": UNDEFINED_ON_ELITES,
            "elite_same_three_axis_bin_pairs": elite_same_bin_pairs,
            "wall_clock_s": wall_clock_s,
            "pre_registered_bound_s": PRE_REGISTERED_BOUND_S,
            "within_bound": wall_clock_s <= PRE_REGISTERED_BOUND_S,
        },
        "closed_states": [
            "the descriptor distribution, octile occupancy and the "
            "animation_density candidate are measured on the loop's "
            "steady-state elites — the population the archive is "
            "actually filled with — for the first time",
            "the material-difference bar is MEASURED (two population "
            "types, each drawn twice at different seeds) and was "
            "pre-registered before the run, with both verdicts "
            "first-class",
            "the elite control is a SECOND FULL LOOP, not the "
            "derivation control reused: the larger of the two is the bar",
            "the elites' origin (bootstrap vs loop offspring) is "
            "measured by membership, cross-checking L1 and L2 directly "
            "rather than by inference",
        ],
        "blocked_states": [
            "L4's A3 (discrimination) and A4 (coverage cost) are "
            "STRUCTURALLY UNDEFINED on this population, not un-run: the "
            "archive holds exactly one elite per niche, so the same-bin "
            "pair denominator is zero and occupied_4 == occupied_3 for "
            "any fourth axis. No number is substituted for either — a "
            "0.0 would read as a measurement",
            "what WOULD answer L4's A3/A4 on the filled population is "
            "the loop's SCORED CANDIDATE STREAM (every creature "
            "evaluated, not only the winners); that is a different seam "
            "and a different slice, named here rather than smuggled in",
            "the documented interpretability clause "
            "(deep-research.md:204) stays BLOCKED on the owner-deferred "
            "human panel — L4's verdict is untouched and nothing here "
            "moves it toward adoption",
            "two loop seeds bound the elite control; a distributional "
            "claim about elite variability needs E4's ten-seed protocol",
            "the animation axis's octile edges are derived from the "
            "derivation population (L4's reference). Deriving them from "
            "the elites instead would compare a population against "
            "edges defined by itself — the degenerate in-sample case "
            "occupancy_saturation already names",
        ],
        "decision": {
            "verdict": headline["verdict"],
            "driving_statistic": driving_statistic,
            "difference": headline["difference"],
            "control": headline["control"],
            "ratio": headline["ratio"],
            "factor": MATERIAL_CONTROL_FACTOR,
            "per_statistic": {
                name: judgements[name]["verdict"] for name in JUDGED_STATISTICS
            },
            "rule": PRE_REGISTERED_RULE,
        },
        "next_research_step": (
            "M2: the geometry split, decided by record (L3's named gated "
            "decision) — which must state what prior coverage numbers do "
            "and do not mean afterwards."
        ),
    }


def write_elite_population_artifacts(
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
    parser.add_argument("--derivation-count", type=int, default=600)
    parser.add_argument("--population", type=int, default=256)
    parser.add_argument("--target-evaluations", type=int, default=20_480)
    parser.add_argument("--rng-seed", type=int, default=DEFAULT_RNG_SEED)
    args = parser.parse_args()

    report = build_elite_population_report(
        derivation_count=args.derivation_count,
        population=args.population,
        target_evaluations=args.target_evaluations,
        rng_seed=args.rng_seed,
    )
    metrics, decision = report["metrics"], report["decision"]
    run = metrics["elite_run"]
    print(
        f"elites {run['occupied_niches']} (coverage {run['coverage']}) "
        f"vs derivation {metrics['sample_sizes']['derivation']}"
    )
    print(
        "  elite origin: "
        f"{run['elite_origin_counts']} "
        f"(bootstrap share {run['elite_origin_bootstrap_share']})"
    )
    for name in JUDGED_STATISTICS:
        judged = metrics["judgements"][name]
        print(
            f"  {name:20} tvd {judged['difference']:.6f} vs control "
            f"{judged['control']:.6f} (x{judged['ratio']:.2f}) -> "
            f"{judged['verdict']}"
        )
    gates = metrics["animation_density_gates_on_elites"]
    print(
        f"  A1 supports_full_bins : {gates['A1_spread']['supports_full_bins']}"
    )
    print(
        "  A2 max |r|            : "
        f"{gates['A2_independence']['max_abs_correlation']}"
    )
    print(
        "  A3/A4                 : UNDEFINED on elites "
        f"(same-bin pairs = {metrics['elite_same_three_axis_bin_pairs']})"
    )
    print(
        f"VERDICT: {decision['verdict'].upper()} "
        f"(driven by {decision['driving_statistic']})"
    )
    for path in write_elite_population_artifacts(args.output_dir, report):
        print(f"wrote {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
