"""Cycle 22 L3: is the scale geometry STALE, or merely INCONSISTENT?

K3 named the frozen derivation edges as the mechanism behind its four
measure-thin bins — one bin missing its boundary by 0.0014, two behind
windows 0.0069 and 0.0094 wide, one suspected quantization emptiness —
and asked whether the geometry itself should re-derive under the
adopted generation layer. The cycle-22 plan carried that question
forward on a stated premise: that the octile edges were "calibrated
empirically over a 600-candidate population produced by the
*pre-DR-0038* generation layer".

**That premise is testable, and this module tests it first.** The E1
derivation protocol is re-run verbatim under today's code and compared
to the committed edges. If the frozen edges are stale, they will move.

The instrument then asks the question the staleness test cannot: the
repo does not have *one* scale geometry, it has several derivation
RECIPES, and they are not all the same. Three are named here because
three are in live use:

* ``incumbent`` — ``build_population(600, seed, TRAIN, wfc_model)``:
  E1's own protocol, whose output is the committed frozen edges that
  ``evaluation_loop_scale`` and ``coverage_qd_gates`` consume via
  ``load_frozen_scale_edges``. Every coverage and QD number the ledger
  reports is measured in THIS geometry.
* ``probe`` — ``build_population(600, seed, ALL SEEDS, wfc_model)``:
  what ``reachability_probe`` and ``occupancy_saturation`` derive
  live, every run, instead of loading the frozen edges. Every
  reachability and support number is measured in THIS geometry.
* ``loop_stream`` — ``constrained_population`` via the promoted
  ``generate_candidate`` under the SLIP: the candidate stream the
  archive is actually FILLED from since DR 0042 adopted it.

A descriptor bin index only means something relative to the edges that
produced it, so two numbers derived under different recipes are not
comparable — comparing them is the same class of error L1 caught in
K2's failure rate one task earlier.

THE RULE IS PRE-REGISTERED HERE, BEFORE ANY RUN, and it is
INCUMBENT-FAVOURING: the frozen geometry stands unless re-running its
own protocol moves the edges by more than sampling noise can explain.
The noise floor is not a constant — it is MEASURED, by deriving the
same recipe twice at different seeds and recording how far the edges
move on their own. Regeneration is recommended only at
``drift >= DRIFT_CONTROL_FACTOR x control``.

**This module never moves the geometry.** Re-deriving the edges would
silently change the meaning of every coverage number in the ledger;
that is a gated change with its own record, not a rider on an
instrument.
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
    scale_axis_values,
    _load_default_slip,
)
from corpus_builder import build_seed_grids_16  # noqa: E402
from wfc_grid import split_corpus, train_wfc_model  # noqa: E402
from wfc_population_throughput import (  # noqa: E402
    constrained_population,
    load_frozen_scale_edges,
)

from mecha_engine.generation import train_generation_model  # noqa: E402

ARTIFACT_ID = "geometry_consistency_stage0"
REPORT_DATE = "2026-07-26"

# The named derivation recipes in live use (see the module docstring).
RECIPES = ("incumbent", "probe", "loop_stream")

# Pre-registered: how many times the measured sampling control a drift
# must exceed before regeneration is recommended. Incumbent-favouring.
DRIFT_CONTROL_FACTOR = 2.0

PRE_REGISTERED_RULE = (
    "pre-registered (cycle 22 L3), incumbent-favouring: the frozen "
    "geometry STANDS unless re-running E1's own derivation protocol "
    "under today's code moves the edges by at least "
    f"{DRIFT_CONTROL_FACTOR}x the MEASURED sampling control (the same "
    "recipe derived twice at different seeds). The bar derives from "
    "evidence, never from a constant, and the instrument never moves "
    "the geometry itself."
)


def edge_separation(first: dict, second: dict) -> dict:
    """The largest absolute edge move between two geometries."""
    per_axis: dict[str, float] = {}
    for name in sorted(set(first) | set(second)):
        a, b = first.get(name, []), second.get(name, [])
        if len(a) != len(b):
            raise ValueError(
                f"edge sets for {name!r} differ in length: {len(a)} vs {len(b)}"
            )
        per_axis[name] = max((abs(x - y) for x, y in zip(a, b)), default=0.0)
    return {
        "per_axis": {k: round(v, 6) for k, v in per_axis.items()},
        "max_abs": round(max(per_axis.values(), default=0.0), 6),
    }


def octile_occupancy(values: list[float], edges: list[float]) -> dict:
    """How evenly a population falls into a geometry's octiles.

    Octile edges are DEFINED so their calibration population splits
    1/8 per bin. Measuring another population against them shows how
    far that population's shape has moved.
    """
    counts = [0] * (len(edges) + 1)
    for value in values:
        index = 0
        while index < len(edges) and value >= edges[index]:
            index += 1
        counts[index] += 1
    total = len(values) or 1
    uniform = 1.0 / len(counts)
    return {
        "counts": counts,
        "total_variation": round(
            0.5 * sum(abs(count / total - uniform) for count in counts), 6
        ),
        "empty_octiles": sum(1 for count in counts if count == 0),
        "sample_size": len(values),
    }


def judge_geometry(*, drift: float, control: float) -> dict:
    """Apply the pre-registered, incumbent-favouring rule."""
    if control <= 0.0:
        raise ValueError(
            "the sampling control must be positive — a zero control would "
            "make every drift infinitely significant; measure it, never "
            "assume it"
        )
    ratio = drift / control
    return {
        "verdict": (
            "regenerate" if ratio >= DRIFT_CONTROL_FACTOR else "withhold_regeneration"
        ),
        "drift": round(drift, 6),
        "control": round(control, 6),
        "ratio": round(ratio, 6),
        "factor": DRIFT_CONTROL_FACTOR,
        "rule": PRE_REGISTERED_RULE,
    }


def _axis_samples(population: list[dict], slip_profile: dict) -> dict:
    samples = {name: [] for name in SCALE_DESCRIPTOR_NAMES}
    for grid in population:
        values = scale_axis_values(grid, slip_profile=slip_profile)
        for name in SCALE_DESCRIPTOR_NAMES:
            samples[name].append(values[name])
    return samples


def _edges_from(samples: dict) -> dict:
    return {
        name: derive_scale_bin_edges(samples[name])
        for name in SCALE_DESCRIPTOR_NAMES
    }


def build_geometry_consistency_report(
    *,
    derivation_count: int = 600,
    control_count: int = 600,
    rng_seed: int = DEFAULT_RNG_SEED,
) -> dict:
    started = time.perf_counter()
    slip_profile = _load_default_slip()
    seeds = build_seed_grids_16()
    train, _, _ = split_corpus(seeds)
    wfc_model = train_wfc_model(train)

    # --- the three live recipes -------------------------------------
    incumbent_pop, incumbent_comp = build_population(
        derivation_count, rng_seed, train, wfc_model
    )
    probe_pop, _ = build_population(derivation_count, rng_seed, seeds, wfc_model)

    generation_model = train_generation_model(seeds)
    loop_pop, loop_refusals = constrained_population(
        seeds,
        generation_model,
        population=derivation_count,
        generation_index=0,
        rng_seed=rng_seed,
        slip_profile=slip_profile,
    )

    samples = {
        "incumbent": _axis_samples(incumbent_pop, slip_profile),
        "probe": _axis_samples(probe_pop, slip_profile),
        "loop_stream": _axis_samples(loop_pop, slip_profile),
    }
    edges = {name: _edges_from(samples[name]) for name in RECIPES}
    frozen = load_frozen_scale_edges()

    # --- the staleness test ------------------------------------------
    frozen_vs_incumbent = edge_separation(frozen, edges["incumbent"])

    # --- the MEASURED sampling control -------------------------------
    # The same recipe, a different seed: how far the edges move on their
    # own. This is the bar; it is never a constant.
    control_pop, _ = build_population(
        control_count, rng_seed + EVALUATION_STREAM_OFFSET, train, wfc_model
    )
    control_edges = _edges_from(_axis_samples(control_pop, slip_profile))
    sampling_control = edge_separation(edges["incumbent"], control_edges)

    judged = judge_geometry(
        drift=frozen_vs_incumbent["max_abs"], control=sampling_control["max_abs"]
    )

    # --- the geometry split -------------------------------------------
    recipe_separation = {
        "incumbent_vs_probe": edge_separation(edges["incumbent"], edges["probe"]),
        "incumbent_vs_loop_stream": edge_separation(
            edges["incumbent"], edges["loop_stream"]
        ),
    }

    # How the FROZEN geometry splits each recipe's population. Its own
    # calibration population is uniform by construction; anything else
    # shows how far that recipe's distribution sits from the geometry
    # every coverage number is reported in.
    occupancy_under_frozen = {
        recipe: {
            name: octile_occupancy(samples[recipe][name], frozen[name])
            for name in SCALE_DESCRIPTOR_NAMES
        }
        for recipe in RECIPES
    }

    wall_clock_s = round(time.perf_counter() - started, 3)

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0",
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 22 L3: test whether the frozen scale geometry is STALE "
            "(K3's named question) and, separately, whether the repo's "
            "several live derivation recipes agree with each other."
        ),
        "source_artifacts": [
            "data/archives/niche_scale_archive_stage0.json",
            "data/archives/reachability_escalation_stage0.json",
            "data/archives/occupancy_saturation_stage0.json",
            "data/archives/evaluation_loop_scale_stage0.json",
        ],
        "parameters": {
            "derivation_count": derivation_count,
            "control_count": control_count,
            "rng_seed": rng_seed,
            "incumbent_composition": incumbent_comp,
            "loop_stream_produced": len(loop_pop),
            "loop_stream_refused": len(loop_refusals),
        },
        "metrics": {
            "recipes": {
                name: {
                    "edges": edges[name],
                    "sample_size": len(samples[name][SCALE_DESCRIPTOR_NAMES[0]]),
                }
                for name in RECIPES
            },
            "frozen_edges": frozen,
            "frozen_vs_incumbent": frozen_vs_incumbent,
            "sampling_control": sampling_control,
            "recipe_separation": recipe_separation,
            "occupancy_under_frozen_geometry": occupancy_under_frozen,
            "wall_clock_s": wall_clock_s,
        },
        "closed_states": [
            "the staleness question is answered by measurement: E1's own "
            "protocol re-run under today's code, compared to the committed "
            "edges",
            "the bar is the MEASURED sampling control, not a constant",
            "the repo's live derivation recipes are named and compared "
            "against each other",
        ],
        "blocked_states": [
            "this instrument never moves the geometry: re-deriving the "
            "edges would change the meaning of every coverage number in "
            "the ledger and is its own gated record",
            "the loop_stream recipe is measured from SEED parents, not "
            "from the loop's steady-state elites — L1 showed seed parents "
            "are largely SLIP-illegal, so its sample is small and biased; "
            "it bounds the question, it does not settle it",
            "K3's blocking-axis windows are NOT re-measured here — that "
            "needs the probe re-run, which is its own slice",
        ],
        "decision": judged,
        "next_research_step": (
            "L4: animation_density judged as a candidate axis — which "
            "must state which geometry it would join."
        ),
    }


def write_geometry_consistency_artifacts(
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
    args = parser.parse_args()

    report = build_geometry_consistency_report(
        derivation_count=args.derivation_count
    )
    metrics = report["metrics"]
    decision = report["decision"]
    print(
        f"staleness drift {decision['drift']} vs measured control "
        f"{decision['control']} (ratio {decision['ratio']}) -> "
        f"{decision['verdict'].upper()}"
    )
    for label, sep in metrics["recipe_separation"].items():
        print(f"  {label:28} max edge move {sep['max_abs']}  {sep['per_axis']}")
    for path in write_geometry_consistency_artifacts(args.output_dir, report):
        print(f"wrote {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
