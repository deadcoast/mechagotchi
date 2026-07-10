"""The archive at documented niche scale (cycle 13 E1).

The dossier's "MAP-Elites archive test" names the first-pass descriptor
space explicitly: THREE axes — symmetry, visual complexity, and
neediness — with 8x8x8 niches. The same dossier's experiment table
states the coverage gate as ">= 25% on a 576-cell repertoire after 20k
evaluations". 8x8x8 = 512, not 576; both documented figures are carried
verbatim in ``DOCUMENTED_REPERTOIRE_FIGURES`` and the geometry follows
the explicit comparator spec (8 bins per axis, 512 niches). Coverage
gates in Phase E read against the geometry's own cell count.

No new statistics: every axis is an existing canonical surface —

- ``symmetry`` — the calibrated mirror-symmetry descriptor formula
  (identical in the extended lab and ``mecha_engine.archive``);
- ``visual_complexity`` — the readability feature extractor's
  ``silhouette_entropy`` (the dossier's own named complexity metric);
- ``behavior_neediness`` — the calibrated extended descriptor axis.

Bin edges are DERIVED EMPIRICALLY (the Phase-A discipline: measure,
never assume): interior octiles of the measured axis distributions over
a seeded derivation population, with per-axis degenerate-distribution
diagnostics recorded honestly. The archive itself is then built from a
DISJOINT evaluation population (different rng stream) so occupancy is
never read off the calibration data.

Elite mechanics are the package's, verbatim: an empty niche accepts the
first valid candidate; an occupied niche is replaced only by strictly
higher fitness; equal fitness keeps the incumbent; invalid grids are
blocked and never become elites. ``test_niche_scale_archive.py`` pins
this by rebuilding the package's extended-mode archive through these
mechanics and comparing elites and summary byte-for-byte. One deliberate
divergence, for scale: the package's ``insert_candidate`` deep-copies
the whole archive per insertion (a persistent-value API); this lab
accumulates in place, because at 20k+ evaluations the per-insert copy is
quadratic. The DECISIONS are pinned identical; only the mutation
discipline differs, and the package keeps its own contract.

Wall-clock FIRST (DR 0028): ``measure_evaluation_unit`` times the full
Phase-E evaluation unit (constrained generation -> validation ->
stress-probed lifecycle -> descriptor -> score -> insert) at a pilot
sample and projects to the documented 20k and 50k evaluation budgets.
Machine-dependent numbers live only in the artifact's ``measured``
section; tests assert shape and arithmetic, never values.
"""

import argparse
import json
import sys
import time
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[2]
for sub in [
    "labs/map_elites_archive",
    "labs/grid_genome",
    "labs/readability_benchmark",
    "labs/lifecycle_sim",
    "labs/wfc_grid",
]:
    path = str(ROOT / sub)
    if path not in sys.path:
        sys.path.insert(0, path)

from constrained_generator import build_constrained_corpus  # noqa: E402
from corpus_builder import build_seed_grids_16  # noqa: E402
from extended_descriptors import (  # noqa: E402
    DESCRIPTOR_NAMES as EXTENDED_DESCRIPTOR_NAMES,
    _behavior_neediness,
    _bin,
    _symmetry_score,
    extended_descriptor_for_grid,
    score_extended_candidate,
)
from learned_readability import extract_readability_features  # noqa: E402
from validator import validate_grid  # noqa: E402
from wfc_grid import build_wfc_corpus, split_corpus, train_wfc_model  # noqa: E402


REPORT_DATE = "2026-07-09"
ARTIFACT_ID = "niche_scale_archive_stage0"
DEFAULT_RNG_SEED = 20260709
DEFAULT_LIFECYCLE_TICKS = 24
# Disjoint rng stream offset between the derivation and evaluation
# populations (edges are never scored on their own calibration data).
EVALUATION_STREAM_OFFSET = 1_000_003

SCALE_DESCRIPTOR_NAMES = ["symmetry", "visual_complexity", "behavior_neediness"]
SCALE_BINS_PER_AXIS = 8
TOTAL_SCALE_NICHES = SCALE_BINS_PER_AXIS ** len(SCALE_DESCRIPTOR_NAMES)

# Both documented figures, verbatim (deep-research.md "MAP-Elites archive
# test" comparator C vs the mecha_darwin experiment table). 8x8x8 = 512;
# the 576-cell repertoire figure does not factor as 8x8x8. The geometry
# follows the explicit comparator; the discrepancy is recorded, never
# averaged away.
DOCUMENTED_REPERTOIRE_FIGURES = {
    "niches_8x8x8": 512,
    "table_repertoire_cells": 576,
}

_GEOMETRIES = {
    "scale": {
        "names": SCALE_DESCRIPTOR_NAMES,
        "cardinalities": [SCALE_BINS_PER_AXIS] * len(SCALE_DESCRIPTOR_NAMES),
    },
    # The package's extended geometry, for the mechanics parity pin only.
    "extended_parity": {
        "names": EXTENDED_DESCRIPTOR_NAMES,
        "cardinalities": [5] * len(EXTENDED_DESCRIPTOR_NAMES),
    },
}


def derive_scale_bin_edges(
    values: list[float], bins: int = SCALE_BINS_PER_AXIS
) -> list[float]:
    """Interior quantile edges (``bins - 1`` octiles for the scale geometry).

    Deterministic linear interpolation between closest ranks (the standard
    inclusive method): for sorted values ``v`` of length ``n`` the edge at
    probability ``p = i / bins`` sits at rank ``h = (n - 1) * p``. Duplicate
    edges from degenerate distributions are returned as-is — the honesty
    lives in ``edge_diagnostics``, never in silent jitter.
    """
    if not isinstance(values, list) or len(values) < bins:
        raise ValueError(
            f"edge derivation needs at least {bins} measured values, "
            f"got {len(values) if isinstance(values, list) else values!r}"
        )
    ordered = sorted(float(value) for value in values)
    n = len(ordered)
    edges = []
    for i in range(1, bins):
        h = (n - 1) * i / bins
        lower = int(h)
        frac = h - lower
        upper = ordered[lower + 1] if lower + 1 < n else ordered[lower]
        edges.append(round(ordered[lower] + frac * (upper - ordered[lower]), 6))
    return edges


def edge_diagnostics(values: list[float], edges: list[float]) -> dict:
    """Per-axis honesty record: can this distribution support 8 bins?"""
    distinct = len(set(edges))
    return {
        "distinct_edge_count": distinct,
        "supports_full_bins": distinct == len(edges),
        "value_min": round(min(values), 6),
        "value_max": round(max(values), 6),
        "value_mean": round(mean(values), 6),
    }


def scale_axis_values(grid: dict, *, slip_profile: dict | None = None) -> dict:
    """The three documented axes from their canonical surfaces."""
    return {
        "symmetry": round(_symmetry_score(grid), 6),
        "visual_complexity": extract_readability_features(grid)[
            "silhouette_entropy"
        ],
        "behavior_neediness": round(_behavior_neediness(grid, slip_profile), 6),
    }


def scale_descriptor_for_values(
    values: dict, edges: dict[str, list[float]]
) -> tuple[int, ...]:
    return tuple(
        _bin(values[name], edges[name]) for name in SCALE_DESCRIPTOR_NAMES
    )


def new_scale_archive(geometry: str = "scale") -> dict:
    if geometry not in _GEOMETRIES:
        raise ValueError(f"unsupported archive geometry: {geometry}")
    names = list(_GEOMETRIES[geometry]["names"])
    return {
        "archive_kind": "map_elites",
        "geometry": geometry,
        "descriptor_names": names,
        "descriptor_cardinalities": list(_GEOMETRIES[geometry]["cardinalities"]),
        "elites": {},
        "observed_bins": {name: [] for name in names},
        "candidate_count": 0,
        "blocked_invalid_count": 0,
        "events": [],
    }


def insert_scale_candidate(
    archive: dict, grid: dict, score: dict, descriptor: tuple[int, ...]
) -> dict:
    """The package elite rule, verbatim, accumulated in place.

    Decision semantics are pinned identical to
    ``mecha_engine.archive.insert_candidate`` (first valid candidate takes
    an empty niche; strictly higher fitness replaces; ties keep the
    incumbent; invalid grids are blocked). In-place accumulation replaces
    the package's per-insert deep copy — the scale divergence documented
    in the module docstring.
    """
    checked = _check_descriptor(archive, descriptor)
    if not isinstance(score, dict) or not isinstance(
        score.get("fitness"), int | float
    ):
        raise ValueError(f"score must carry a numeric fitness: {score!r}")
    fitness = score["fitness"]
    niche = ",".join(str(value) for value in checked)
    grid_id = grid.get("grid_id", "unknown_grid")

    archive["candidate_count"] += 1
    for name, value in zip(archive["descriptor_names"], checked):
        observed = set(archive["observed_bins"][name])
        observed.add(value)
        archive["observed_bins"][name] = sorted(observed)

    if not validate_grid(grid).ok:
        archive["blocked_invalid_count"] += 1
        _log(
            archive,
            event="blocked_invalid_candidate",
            niche=niche,
            grid_id=grid_id,
            fitness=fitness,
        )
        return archive

    incumbent = archive["elites"].get(niche)
    if incumbent is None:
        archive["elites"][niche] = _elite_entry(grid_id, fitness, checked, score)
        _log(
            archive,
            event="inserted_empty_niche",
            niche=niche,
            grid_id=grid_id,
            fitness=fitness,
        )
    elif fitness > incumbent["fitness"]:
        archive["elites"][niche] = _elite_entry(grid_id, fitness, checked, score)
        _log(
            archive,
            event="replaced_elite",
            niche=niche,
            grid_id=grid_id,
            fitness=fitness,
            incumbent_grid_id=incumbent["grid_id"],
            incumbent_fitness=incumbent["fitness"],
        )
    else:
        _log(
            archive,
            event=(
                "kept_incumbent_tie"
                if fitness == incumbent["fitness"]
                else "kept_incumbent_higher_fitness"
            ),
            niche=niche,
            grid_id=grid_id,
            fitness=fitness,
            incumbent_grid_id=incumbent["grid_id"],
            incumbent_fitness=incumbent["fitness"],
        )
    return archive


def build_scale_archive(
    candidates: list[dict],
    *,
    slip_profile: dict | None = None,
    lifecycle_ticks: int = DEFAULT_LIFECYCLE_TICKS,
    rng_seed: int = DEFAULT_RNG_SEED,
    geometry: str = "scale",
    edges: dict[str, list[float]] | None = None,
) -> dict:
    """Score and insert every candidate through the canonical surfaces.

    Fitness is ``score_extended_candidate`` (the calibrated Stage 0
    weights) with the archive's standard per-candidate ``rng_seed + index``
    stream. The ``scale`` geometry bins ``scale_axis_values`` with the
    derived ``edges``; ``extended_parity`` reuses the calibrated extended
    descriptor so the mechanics pin can compare against the package.
    """
    if geometry == "scale" and edges is None:
        raise ValueError("the scale geometry requires derived bin edges")
    archive = new_scale_archive(geometry)
    for index, grid in enumerate(candidates):
        score = score_extended_candidate(
            grid,
            slip_profile=slip_profile,
            lifecycle_ticks=lifecycle_ticks,
            rng_seed=rng_seed + index,
        )
        if geometry == "extended_parity":
            descriptor = tuple(
                extended_descriptor_for_grid(
                    grid,
                    slip_profile=slip_profile,
                    lifecycle_ticks=lifecycle_ticks,
                    rng_seed=rng_seed + index,
                )["values"]
            )
        else:
            descriptor = scale_descriptor_for_values(
                scale_axis_values(grid, slip_profile=slip_profile), edges
            )
        insert_scale_candidate(archive, grid, score, descriptor)
    return archive


def scale_archive_summary(archive: dict) -> dict:
    elites = archive["elites"]
    total_niches = 1
    for cardinality in archive["descriptor_cardinalities"]:
        total_niches *= cardinality
    qd_score = sum(elite["fitness"] for elite in elites.values())
    return {
        "archive_kind": archive["archive_kind"],
        "geometry": archive["geometry"],
        "descriptor_names": list(archive["descriptor_names"]),
        "descriptor_cardinalities": list(archive["descriptor_cardinalities"]),
        "total_possible_niches": total_niches,
        "occupied_niches": len(elites),
        "coverage": round(len(elites) / total_niches, 6),
        "descriptor_bin_spread": {
            name: len(archive["observed_bins"][name])
            for name in archive["descriptor_names"]
        },
        "best_fitness": max(
            (elite["fitness"] for elite in elites.values()), default=0
        ),
        "mean_elite_fitness": round(qd_score / len(elites), 6) if elites else 0,
        "qd_score": round(qd_score, 6),
        "candidate_count": archive["candidate_count"],
        "blocked_invalid_count": archive["blocked_invalid_count"],
        "event_counts": _event_counts(archive),
    }


def build_population(
    count: int, rng_seed: int, seeds: list[dict], wfc_model: dict
) -> tuple[list[dict], dict]:
    """A mixed 16x16 candidate population: constrained + WFC halves.

    The constrained arm is the promoted evolve inner-loop path; the WFC
    arm is the adopted generation layer (DR 0031). Mixing both keeps the
    edge calibration and the occupancy evidence tied to the generators
    Phase E actually runs.
    """
    constrained_count = count // 2
    wfc_count = count - constrained_count
    constrained = build_constrained_corpus(
        seeds, count=constrained_count, rng_seed=rng_seed
    )
    wfc = build_wfc_corpus(wfc_model, count=wfc_count, rng_seed=rng_seed)
    composition = {"constrained": constrained_count, "wfc": wfc_count}
    return constrained + wfc, composition


def build_niche_scale_report(
    *,
    derivation_count: int = 600,
    evaluation_count: int = 3000,
    rng_seed: int = DEFAULT_RNG_SEED,
    lifecycle_ticks: int = DEFAULT_LIFECYCLE_TICKS,
) -> dict:
    slip_profile = _load_default_slip()
    seeds = build_seed_grids_16()
    train, _, _ = split_corpus(seeds)
    wfc_model = train_wfc_model(train)

    derivation_seed = rng_seed
    evaluation_seed = rng_seed + EVALUATION_STREAM_OFFSET
    derivation_population, derivation_composition = build_population(
        derivation_count, derivation_seed, train, wfc_model
    )
    evaluation_population, evaluation_composition = build_population(
        evaluation_count, evaluation_seed, train, wfc_model
    )

    axis_samples = {name: [] for name in SCALE_DESCRIPTOR_NAMES}
    for grid in derivation_population:
        values = scale_axis_values(grid, slip_profile=slip_profile)
        for name in SCALE_DESCRIPTOR_NAMES:
            axis_samples[name].append(values[name])
    edges = {
        name: derive_scale_bin_edges(axis_samples[name])
        for name in SCALE_DESCRIPTOR_NAMES
    }
    diagnostics = {
        name: edge_diagnostics(axis_samples[name], edges[name])
        for name in SCALE_DESCRIPTOR_NAMES
    }

    archive = build_scale_archive(
        evaluation_population,
        slip_profile=slip_profile,
        lifecycle_ticks=lifecycle_ticks,
        rng_seed=evaluation_seed,
        geometry="scale",
        edges=edges,
    )
    summary = scale_archive_summary(archive)
    degenerate_axes = sorted(
        name
        for name in SCALE_DESCRIPTOR_NAMES
        if not diagnostics[name]["supports_full_bins"]
    )

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete",
        "date": REPORT_DATE,
        "purpose": (
            "Derive the documented first-pass 8x8x8 descriptor geometry "
            "(symmetry, visual complexity, behavior neediness — deep-research "
            "'MAP-Elites archive test') with EMPIRICAL octile bin edges from "
            "a measured derivation population, then prove the package-parity "
            "archive mechanics at hundreds of occupied niches on a disjoint "
            "evaluation population (cycle 13 E1)."
        ),
        "source_artifacts": [
            "labs/map_elites_archive/extended_descriptors.py",
            "labs/readability_benchmark/learned_readability.py",
            "labs/grid_genome/constrained_generator.py",
            "labs/wfc_grid/wfc_grid.py",
            "data/seed_grids_16x16",
            "packages/mecha_engine/src/mecha_engine/archive/store.py",
            "docs/project-research/deep-research/01/deep-research.md",
        ],
        "metrics": {
            "documented_repertoire_figures": dict(DOCUMENTED_REPERTOIRE_FIGURES),
            "geometry": {
                "descriptor_names": list(SCALE_DESCRIPTOR_NAMES),
                "bins_per_axis": SCALE_BINS_PER_AXIS,
                "total_possible_niches": TOTAL_SCALE_NICHES,
            },
            "edge_derivation": {
                "method": (
                    "interior octiles, linear interpolation between closest "
                    "ranks, over the derivation population's measured axis "
                    "values"
                ),
                "edges": edges,
                "diagnostics": diagnostics,
            },
            "populations": {
                "derivation": {
                    "candidate_count": derivation_count,
                    "rng_seed": derivation_seed,
                    "composition": derivation_composition,
                },
                "evaluation": {
                    "candidate_count": evaluation_count,
                    "rng_seed": evaluation_seed,
                    "composition": evaluation_composition,
                },
            },
            "archive": summary,
        },
        "closed_states": [
            "scale_geometry_is_the_documented_first_pass_spec",
            "bin_edges_derived_empirically_from_measured_distributions",
            "elite_mechanics_parity_pinned_against_the_package",
            "edges_and_occupancy_measured_on_disjoint_populations",
        ],
        "blocked_states": [
            "documented_figure_discrepancy_512_vs_576 (both dossier figures "
            "recorded verbatim; the geometry follows the explicit 8x8x8 "
            "comparator spec; Phase-E coverage gates read against the "
            "geometry's own 512 cells)",
            "package_scale_geometry_seam_not_promoted (the engine archive "
            "still exposes baseline/extended modes only; promoting the "
            "scale geometry is a package change with its own spec update "
            "and gate, consumed by E3's evolve run)",
        ]
        + (
            [
                "degenerate_axis_distributions ("
                + ", ".join(degenerate_axes)
                + " cannot support 8 distinct octile edges on the derivation "
                "population — recorded, not jittered)"
            ]
            if degenerate_axes
            else []
        ),
        "decision": (
            "The documented 8x8x8 geometry is derivable from the calibrated "
            "descriptor surfaces with empirical octile edges, and the "
            "package-parity mechanics hold at scale: "
            f"{summary['occupied_niches']} of {TOTAL_SCALE_NICHES} niches "
            f"occupied (coverage {summary['coverage']}) over "
            f"{summary['candidate_count']} evaluated candidates."
        ),
        "next_research_step": (
            "E2: WFC generation throughput at populations in the hundreds "
            "per generation, parents drawn from these archive elites, "
            "against the dossier's <=250 ms bar."
        ),
    }


def measure_evaluation_unit(
    *,
    sample_count: int = 200,
    rng_seed: int = DEFAULT_RNG_SEED,
    lifecycle_ticks: int = DEFAULT_LIFECYCLE_TICKS,
) -> dict:
    """Wall-clock pilot for the Phase-E evaluation unit (DR 0028: FIRST).

    One unit = constrained generation -> validation -> stress-probed
    lifecycle -> descriptor -> score -> insert. Machine-dependent; lives
    only in the artifact's ``measured`` section. Placeholder uniform edges
    are used for binning — edge choice does not affect timing.
    """
    seeds = build_seed_grids_16()
    train, _, _ = split_corpus(seeds)
    slip_profile = _load_default_slip()
    pilot_edges = {
        name: [round(i / SCALE_BINS_PER_AXIS, 6) for i in range(1, SCALE_BINS_PER_AXIS)]
        for name in SCALE_DESCRIPTOR_NAMES
    }

    generation_start = time.perf_counter()
    candidates = build_constrained_corpus(
        train, count=sample_count, rng_seed=rng_seed
    )
    generation_ms = (time.perf_counter() - generation_start) * 1000

    evaluation_start = time.perf_counter()
    archive = new_scale_archive()
    for index, grid in enumerate(candidates):
        score = score_extended_candidate(
            grid,
            slip_profile=slip_profile,
            lifecycle_ticks=lifecycle_ticks,
            rng_seed=rng_seed + index,
        )
        descriptor = scale_descriptor_for_values(
            scale_axis_values(grid, slip_profile=slip_profile), pilot_edges
        )
        insert_scale_candidate(archive, grid, score, descriptor)
    evaluation_ms = (time.perf_counter() - evaluation_start) * 1000

    total_ms = generation_ms + evaluation_ms
    # Rounded FIRST so the recorded unit value and the projections stay
    # arithmetically consistent inside the artifact.
    mean_ms = round(total_ms / sample_count, 4)
    return {
        "context": (
            "stage-0 dev machine; excludes one-time seed/model setup; "
            "constrained generation (the promoted evolve inner-loop path) "
            f"+ {lifecycle_ticks}-tick stress-probed lifecycle scoring"
        ),
        "evaluation_unit": {
            "sample_count": sample_count,
            "lifecycle_ticks": lifecycle_ticks,
            "generation_ms_total": round(generation_ms, 2),
            "scoring_and_insert_ms_total": round(evaluation_ms, 2),
            "mean_ms_per_evaluation": mean_ms,
        },
        "projections": {
            "evaluations_20k_s": round(mean_ms * 20_000 / 1000, 2),
            "evaluations_50k_s": round(mean_ms * 50_000 / 1000, 2),
        },
    }


def write_niche_scale_artifacts(
    output_dir: Path, report: dict, measured: dict | None = None
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = dict(report)
    if measured is not None:
        payload["measured"] = measured
    (output_dir / f"{ARTIFACT_ID}.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def _elite_entry(
    grid_id: str, fitness: float, descriptor: tuple[int, ...], score: dict
) -> dict:
    return {
        "grid_id": grid_id,
        "fitness": fitness,
        "descriptor": {
            "values": list(descriptor),
            "key": ",".join(str(value) for value in descriptor),
        },
        "fitness_components": dict(score.get("components", {})),
    }


def _check_descriptor(archive: dict, descriptor: object) -> tuple[int, ...]:
    cardinalities = archive["descriptor_cardinalities"]
    if not isinstance(descriptor, tuple | list) or len(descriptor) != len(
        cardinalities
    ):
        raise ValueError(
            f"descriptor must be a tuple of {len(cardinalities)} integers "
            f"for geometry {archive['geometry']}: {descriptor!r}"
        )
    checked = []
    for value, cardinality in zip(descriptor, cardinalities):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"descriptor values must be integers: {descriptor!r}")
        if not 0 <= value < cardinality:
            raise ValueError(
                f"descriptor value {value} outside bin range 0..{cardinality - 1}"
            )
        checked.append(value)
    return tuple(checked)


def _event_counts(archive: dict) -> dict:
    counts: dict[str, int] = {}
    for event in archive["events"]:
        counts[event["event"]] = counts.get(event["event"], 0) + 1
    return dict(sorted(counts.items()))


def _log(archive: dict, **event_fields: object) -> None:
    archive["events"].append(event_fields)


def _load_default_slip() -> dict:
    return json.loads(
        (ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="The archive at documented niche scale (cycle 13 E1)."
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "archives"
    )
    parser.add_argument("--derivation-count", type=int, default=600)
    parser.add_argument("--evaluation-count", type=int, default=3000)
    parser.add_argument("--rng-seed", type=int, default=DEFAULT_RNG_SEED)
    parser.add_argument("--pilot-count", type=int, default=200)
    parser.add_argument("--skip-timing", action="store_true")
    args = parser.parse_args()

    # DR 0028 discipline: the wall-clock pilot runs FIRST, before the
    # full-scale artifact build.
    measured = (
        None
        if args.skip_timing
        else measure_evaluation_unit(
            sample_count=args.pilot_count, rng_seed=args.rng_seed
        )
    )
    if measured is not None:
        print(json.dumps(measured, indent=2))

    report = build_niche_scale_report(
        derivation_count=args.derivation_count,
        evaluation_count=args.evaluation_count,
        rng_seed=args.rng_seed,
    )
    write_niche_scale_artifacts(args.output_dir, report, measured)
    printable = {
        key: value
        for key, value in report["metrics"]["archive"].items()
        if key != "event_counts"
    }
    print(json.dumps({"archive": printable}, indent=2))
    print(json.dumps({"edge_diagnostics": report["metrics"]["edge_derivation"]["diagnostics"]}, indent=2))
    print(report["decision"])


if __name__ == "__main__":
    main()
