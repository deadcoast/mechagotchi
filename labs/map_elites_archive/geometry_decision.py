"""Cycle 23 M2: the geometry split, DECIDED.

L3 diagnosed and deliberately did not repair: the repo runs **two** scale
geometries at once.

* ``incumbent`` — ``build_population(600, seed, TRAIN, wfc_model)``,
  frozen and committed. ``evaluation_loop_scale`` and
  ``coverage_qd_gates`` consume it via ``load_frozen_scale_edges``.
  **Every coverage, QD and E4 number in the ledger is measured here.**
* ``probe`` — ``build_population(600, seed, ALL 50 SEEDS, wfc_model)``,
  re-derived **live on every run**. ``reachability_probe`` and
  ``occupancy_saturation`` use it. **Every reachability and support
  number is measured here.**

The edge sets differ by up to 0.0375, which L3 measured at 3.7× its own
sampling control. The consequence is that ``460/512 occupied`` and
``508/512 reachable`` are counted in different coordinate systems — and
have been read against each other in prose.

**THIS MODULE MEASURES THE SPLIT IN THE UNIT THAT MATTERS.** L3 measured
it in *edge distance*, which is diagnostic but is not the unit any
ledger number is expressed in. A reader cannot tell from "the edges
differ by 0.0375" whether that moves one creature or four hundred. So
the statistic here is the **bin disagreement rate**: given one common
population, how often does the same creature receive a **different
address** under the two geometries? That is exactly the unit
``460/512`` is counted in.

THE RULE IS PRE-REGISTERED HERE, BEFORE ANY RUN.

* **Status-quo-favouring**: the split **stands** unless the geometries
  disagree by more than sampling can explain. Instruments are not
  rewired without measured cause.
* The bar is **MEASURED, never a constant** (L3's and M1's precedent):
  the same recipe derived at two different seeds, binned over the same
  population, is how much a geometry disagrees *with itself*. Both
  recipes are controlled and the **larger** is taken, which makes
  ``converge`` harder to reach.
* ``converge`` at ``>= DISAGREEMENT_CONTROL_FACTOR × control``,
  ``freeze_split`` otherwise. Both verdicts are first-class.

**WHETHER to converge is decided by the measurement. WHICH WAY is
decided by a principle fixed here, before the measurement**, so the
direction can never be chosen to suit the number that comes back.

Finally, the module re-measures the one cross-geometry claim L3 named by
name: K2's headline that *"460 occupied niches is **exactly** the
measured support ceiling"*. The 460 is counted in the incumbent
geometry, the ceiling in the probe geometry. Here the support ceiling is
computed in **both**, from one population, so the claim can be judged
with both numbers in the same coordinate system for the first time.

**This module never moves the geometry.** It measures and it decides;
re-deriving anything is the consequence of the record it feeds
(DR 0046), carried out by the surfaces that own those numbers.
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
    TOTAL_SCALE_NICHES,
    build_population,
    derive_scale_bin_edges,
    scale_axis_values,
    scale_descriptor_for_values,
    _load_default_slip,
)
from corpus_builder import build_seed_grids_16  # noqa: E402
from wfc_grid import split_corpus, train_wfc_model  # noqa: E402
from wfc_population_throughput import load_frozen_scale_edges  # noqa: E402

ARTIFACT_ID = "geometry_decision_stage0"
REPORT_DATE = "2026-07-27"

GEOMETRIES = ("incumbent", "probe")

# Pre-registered: how many times the MEASURED control the bin
# disagreement must reach before the instruments are rewired. L3's and
# M1's factor; here it resists changing the status quo.
DISAGREEMENT_CONTROL_FACTOR = 2.0

# THE DIRECTION, FIXED BEFORE THE MEASUREMENT (see the docstring). The
# measurement decides whether to converge; this decides which way, and
# it is pinned so the choice cannot be made after seeing the number.
CONVERGENCE_TARGET = "incumbent"

CONVERGENCE_TARGET_REASON = (
    "The incumbent geometry is the frozen, committed one, and it is "
    "where every coverage, QD and E4 number in the ledger already "
    "lives. Converging ONTO it therefore changes no historical "
    "number: the probe-side surfaces re-derive, and every committed "
    "coverage artifact keeps both its value and its meaning. "
    "Converging the other way would leave every coverage number in the "
    "repo true-but-incomparable to the geometry it is quoted beside — "
    "the very hazard L3 named. There is also a substantive reason and "
    "not merely a bookkeeping one: reachability is a claim ABOUT the "
    "archive's coordinate system ('how many of the archive's bins can "
    "be reached'), so it has to be counted in the archive's own "
    "coordinates or it does not bear on the archive at all. The probe "
    "explores the space; it does not get to redefine it."
)

PRE_REGISTERED_RULE = (
    "pre-registered (cycle 23 M2), status-quo-favouring, both verdicts "
    "first-class: the two-geometry split STANDS unless the geometries "
    "disagree by at least "
    f"{DISAGREEMENT_CONTROL_FACTOR}x the MEASURED control. The "
    "statistic is the BIN DISAGREEMENT RATE — the fraction of one "
    "common population that receives a different descriptor address "
    "under the two geometries — because that is the unit every "
    "coverage number is counted in, and edge distance is not. The "
    "control is the same recipe derived at two different seeds "
    "(how far a geometry disagrees with ITSELF), measured for both "
    "recipes with the LARGER taken. WHETHER to converge is decided "
    f"here by measurement; WHICH WAY is fixed in advance "
    f"(CONVERGENCE_TARGET = {CONVERGENCE_TARGET!r}) so the direction "
    "cannot be chosen to suit the result."
)

# The queue's explicit requirement, carried in the artifact rather than
# left to prose: whatever is decided, no historical artifact becomes
# wrong.
HISTORICAL_VALIDITY_NOTE = (
    "Every historical artifact stays true under the edges it was "
    "measured with. Nothing in this decision retracts a committed "
    "number: coverage 0.8984, QD 404.618236 and the 460 occupied "
    "niches remain exactly what they were, measured in the incumbent "
    "geometry. What changes is what may be COMPARED with what — a "
    "descriptor bin index means nothing except relative to the edges "
    "that produced it, so numbers from different geometries may not be "
    "read against each other, and any claim that does so must be "
    "re-measured in one geometry before it is restated."
)


def bin_disagreement(
    first: list[tuple[int, ...]], second: list[tuple[int, ...]]
) -> float:
    """Fraction of a population that changes ADDRESS between geometries.

    A descriptor is a whole address: one axis off by one octile is a
    different niche, not a partial match. This is the unit
    ``460/512`` is counted in.
    """
    if len(first) != len(second):
        raise ValueError(
            "the same population must be addressed under both "
            f"geometries: {len(first)} vs {len(second)}"
        )
    if not first:
        raise ValueError("an empty population has no addresses to compare")
    differing = sum(1 for a, b in zip(first, second) if a != b)
    return round(differing / len(first), 6)


def per_axis_disagreement(
    first: list[tuple[int, ...]], second: list[tuple[int, ...]]
) -> dict:
    """Where the split lives — the headline rate says only that it does."""
    if len(first) != len(second):
        raise ValueError(
            "the same population must be addressed under both "
            f"geometries: {len(first)} vs {len(second)}"
        )
    if not first:
        raise ValueError("an empty population has no addresses to compare")
    return {
        name: round(
            sum(1 for a, b in zip(first, second) if a[index] != b[index])
            / len(first),
            6,
        )
        for index, name in enumerate(SCALE_DESCRIPTOR_NAMES)
    }


def judge_geometry_split(*, disagreement: float, control: float) -> dict:
    """Apply the pre-registered rule. Both verdicts are first-class."""
    if control <= 0.0:
        raise ValueError(
            "the sampling control must be positive — a zero control "
            "would make every disagreement infinitely significant; "
            "measure it, never assume it"
        )
    ratio = disagreement / control
    converge = ratio >= DISAGREEMENT_CONTROL_FACTOR
    return {
        "verdict": "converge" if converge else "freeze_split",
        "disagreement": round(disagreement, 6),
        "control": round(control, 6),
        "ratio": round(ratio, 6),
        "factor": DISAGREEMENT_CONTROL_FACTOR,
        "convergence_target": CONVERGENCE_TARGET if converge else None,
        "convergence_target_reason": (
            CONVERGENCE_TARGET_REASON if converge else None
        ),
        "historical_validity": HISTORICAL_VALIDITY_NOTE,
        "rule": PRE_REGISTERED_RULE,
    }


def _edges_from(population: list[dict], slip_profile: dict) -> dict:
    samples: dict[str, list[float]] = {
        name: [] for name in SCALE_DESCRIPTOR_NAMES
    }
    for grid in population:
        values = scale_axis_values(grid, slip_profile=slip_profile)
        for name in SCALE_DESCRIPTOR_NAMES:
            samples[name].append(values[name])
    return {
        name: derive_scale_bin_edges(samples[name])
        for name in SCALE_DESCRIPTOR_NAMES
    }


def _address(
    population: list[dict], edges: dict, slip_profile: dict
) -> list[tuple[int, ...]]:
    return [
        scale_descriptor_for_values(
            scale_axis_values(grid, slip_profile=slip_profile), edges
        )
        for grid in population
    ]


def build_geometry_decision_report(
    *,
    derivation_count: int = 600,
    evaluation_count: int = 3000,
    rng_seed: int = DEFAULT_RNG_SEED,
    control_rng_seed: int = DEFAULT_RNG_SEED + EVALUATION_STREAM_OFFSET,
) -> dict:
    started = time.perf_counter()
    slip_profile = _load_default_slip()
    seeds = build_seed_grids_16()
    train, _, _ = split_corpus(seeds)
    wfc_model = train_wfc_model(train)

    # --- the two live geometries, reproduced exactly ------------------
    incumbent_edges = load_frozen_scale_edges()
    probe_population, _ = build_population(
        derivation_count, rng_seed, seeds, wfc_model
    )
    probe_edges = _edges_from(probe_population, slip_profile)

    # --- the controls: each recipe against ITSELF at another seed -----
    incumbent_control_pop, _ = build_population(
        derivation_count, control_rng_seed, train, wfc_model
    )
    incumbent_control_edges = _edges_from(incumbent_control_pop, slip_profile)
    probe_control_pop, _ = build_population(
        derivation_count, control_rng_seed, seeds, wfc_model
    )
    probe_control_edges = _edges_from(probe_control_pop, slip_profile)

    # --- one common population, addressed under everything ------------
    evaluation, composition = build_population(
        evaluation_count, rng_seed + EVALUATION_STREAM_OFFSET, seeds, wfc_model
    )
    addressed = {
        "incumbent": _address(evaluation, incumbent_edges, slip_profile),
        "probe": _address(evaluation, probe_edges, slip_profile),
        "incumbent_control": _address(
            evaluation, incumbent_control_edges, slip_profile
        ),
        "probe_control": _address(evaluation, probe_control_edges, slip_profile),
    }

    disagreement = bin_disagreement(
        addressed["incumbent"], addressed["probe"]
    )
    per_axis = per_axis_disagreement(
        addressed["incumbent"], addressed["probe"]
    )
    control_by_recipe = {
        "incumbent": bin_disagreement(
            addressed["incumbent"], addressed["incumbent_control"]
        ),
        "probe": bin_disagreement(addressed["probe"], addressed["probe_control"]),
    }
    measured_control = max(control_by_recipe.values())

    judged = judge_geometry_split(
        disagreement=disagreement, control=measured_control
    )

    # --- K2's cross-geometry claim, both numbers in one geometry ------
    # "460 occupied niches is EXACTLY the measured support ceiling" —
    # the 460 counted in the incumbent geometry, the ceiling in the
    # probe geometry. Counted here in both, from one population.
    support_ceiling = {
        name: len(set(addressed[name])) for name in GEOMETRIES
    }

    wall_clock_s = round(time.perf_counter() - started, 3)

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0",
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 23 M2: decide L3's two-geometry split by measuring it "
            "in the unit ledger numbers are counted in — the fraction of "
            "one population that changes descriptor address between the "
            "geometries — against a MEASURED control, with the direction "
            "of convergence fixed before the run."
        ),
        "source_artifacts": [
            "data/archives/geometry_consistency_stage0.json",
            "data/archives/niche_scale_archive_stage0.json",
            "data/archives/occupancy_saturation_stage0.json",
            "data/archives/reachability_probe_stage0.json",
            "data/archives/reachability_escalation_stage0.json",
            "data/archives/evaluation_loop_scale_stage0.json",
            "data/archives/elite_population_measures_stage0.json",
        ],
        "parameters": {
            "derivation_count": derivation_count,
            "evaluation_count": evaluation_count,
            "rng_seed": rng_seed,
            "control_rng_seed": control_rng_seed,
            "population_composition": composition,
            "recipes": {
                "incumbent": (
                    "build_population(N, seed, TRAIN, wfc_model) — frozen "
                    "and committed; consumed by evaluation_loop_scale and "
                    "coverage_qd_gates via load_frozen_scale_edges"
                ),
                "probe": (
                    "build_population(N, seed, ALL 50 SEEDS, wfc_model) — "
                    "re-derived live every run by reachability_probe and "
                    "occupancy_saturation"
                ),
            },
        },
        "metrics": {
            "edges": {
                "incumbent": incumbent_edges,
                "probe": probe_edges,
            },
            "bin_disagreement": disagreement,
            "per_axis_disagreement": per_axis,
            "control_by_recipe": control_by_recipe,
            "measured_control": measured_control,
            "support_ceiling": support_ceiling,
            "total_niches": TOTAL_SCALE_NICHES,
            "wall_clock_s": wall_clock_s,
        },
        "closed_states": [
            "the split is measured in the unit ledger numbers are "
            "counted in (address changes), not only in edge distance",
            "the bar is the MEASURED self-disagreement of each recipe at "
            "two seeds, with the larger taken — never a constant",
            "the direction of convergence was fixed before the "
            "measurement, so it could not be chosen to suit the result",
            "K2's cross-geometry claim is re-measured with the support "
            "ceiling counted in BOTH geometries from one population",
            HISTORICAL_VALIDITY_NOTE,
        ],
        "blocked_states": [
            "this module never moves a geometry: it measures and "
            "decides. Re-deriving the probe-side surfaces is the "
            "CONSEQUENCE of the record this feeds (DR 0046), carried "
            "out by the surfaces that own those numbers",
            "the reachability numbers (508/512 proven, the four bins "
            "bounded by K3's blocking-axis instrument) are NOT re-run "
            "here — that is a full probe re-run under the decided "
            "geometry and is named as required follow-on work, with its "
            "cost, rather than estimated",
            "the support ceiling here is counted over this module's "
            "evaluation population; it is the SAME recipe and size "
            "occupancy_saturation uses, but a ceiling is a property of "
            "the population it is counted over, so it is reported as "
            "this population's ceiling and not substituted for that "
            "artifact's",
        ],
        "decision": judged,
        "next_research_step": (
            "M3: the unbreedable bootstrap elites, whose fix trades "
            "against coverage — with M1's measured denominator (48 of "
            "460 elites are bootstrap creatures)."
        ),
    }


def write_geometry_decision_artifacts(
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
    parser.add_argument("--evaluation-count", type=int, default=3000)
    args = parser.parse_args()

    report = build_geometry_decision_report(
        derivation_count=args.derivation_count,
        evaluation_count=args.evaluation_count,
    )
    metrics, decision = report["metrics"], report["decision"]
    print(
        f"bin disagreement {decision['disagreement']} vs measured control "
        f"{decision['control']} (x{decision['ratio']}) -> "
        f"{decision['verdict'].upper()}"
    )
    print(f"  per-axis: {metrics['per_axis_disagreement']}")
    print(f"  controls: {metrics['control_by_recipe']}")
    ceiling = metrics["support_ceiling"]
    print(
        f"  support ceiling: incumbent {ceiling['incumbent']} vs probe "
        f"{ceiling['probe']} (of {metrics['total_niches']})"
    )
    if decision["convergence_target"]:
        print(f"  converge onto: {decision['convergence_target']}")
    for path in write_geometry_decision_artifacts(args.output_dir, report):
        print(f"wrote {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
