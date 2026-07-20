"""Cycle 20 J1: descriptor-bin reachability under the engine's own

move set. I5b measured the bound (the generators' descriptor RANGE:
374 of 512 bins at 3x volume) — this probe asks, per unreached bin,
whether the ENGINE ITSELF can reach it: a guided descent that may
only use promoted surfaces (the trained generation model +
``generate_candidate`` + package validation) and the geometry's own
descriptors. A bin counts as REACHED only with a validator-passing
witness whose descriptor recomputes into that exact bin; an unreached
bin is "unreached within budget" — a measured bound, never an
impossibility proof. No hand-painted exceptions: every candidate the
probe considers comes out of ``generate_candidate``.
"""

import argparse
import itertools
import json
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
GRID_GENOME_DIR = LAB_DIR.parent / "grid_genome"
WFC_DIR = LAB_DIR.parent / "wfc_grid"
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
for _path in (LAB_DIR, GRID_GENOME_DIR, WFC_DIR, PACKAGE_SRC):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from niche_scale_archive import (  # noqa: E402
    DEFAULT_RNG_SEED,
    EVALUATION_STREAM_OFFSET,
    SCALE_BINS_PER_AXIS,
    SCALE_DESCRIPTOR_NAMES,
    _load_default_slip,
    build_population,
    derive_scale_bin_edges,
    scale_axis_values,
    scale_descriptor_for_values,
)
from corpus_builder import build_seed_grids_16  # noqa: E402
from wfc_grid import split_corpus, train_wfc_model  # noqa: E402

from mecha_engine.generation import (  # noqa: E402
    generate_candidate,
    train_generation_model,
)
from mecha_engine.genome import validate_grid  # noqa: E402

ARTIFACT_ID = "reachability_probe_stage0"
REPORT_DATE = "2026-07-20"
DEFAULT_PER_BIN_BUDGET = 200
DEFAULT_ELITE_SIZE = 4
PROBE_SEED_OFFSET = 7_000_017


def _bin_distance(a: tuple[int, ...], b: tuple[int, ...]) -> int:
    return sum(abs(x - y) for x, y in zip(a, b))


def build_reachability_report(
    *,
    derivation_count: int = 600,
    pool_count: int = 9000,
    per_bin_budget: int = DEFAULT_PER_BIN_BUDGET,
    elite_size: int = DEFAULT_ELITE_SIZE,
    probe_limit: int | None = None,
    rng_seed: int = DEFAULT_RNG_SEED,
) -> dict:
    slip_profile = _load_default_slip()
    seeds = build_seed_grids_16()
    train, _, _ = split_corpus(seeds)
    wfc_model = train_wfc_model(train)

    derivation, _ = build_population(
        derivation_count, rng_seed, seeds, wfc_model
    )
    edges = {
        name: derive_scale_bin_edges(
            [
                scale_axis_values(grid, slip_profile=slip_profile)[name]
                for grid in derivation
            ]
        )
        for name in SCALE_DESCRIPTOR_NAMES
    }

    def bin_of(grid: dict) -> tuple[int, ...]:
        return scale_descriptor_for_values(
            scale_axis_values(grid, slip_profile=slip_profile), edges
        )

    pool, _ = build_population(
        pool_count, rng_seed + EVALUATION_STREAM_OFFSET, seeds, wfc_model
    )
    pool_bins = [bin_of(grid) for grid in pool]
    reached_by_generators = set(pool_bins)

    axes = range(SCALE_BINS_PER_AXIS)
    all_bins = [
        bins for bins in itertools.product(axes, axes, axes)
    ]
    unreached = sorted(set(all_bins) - reached_by_generators)
    probed_targets = (
        unreached[:probe_limit] if probe_limit is not None else unreached
    )

    model = train_generation_model(seeds)
    per_bin: list[dict] = []
    newly_reached = 0
    for bin_index, target in enumerate(probed_targets):
        ranked = sorted(
            range(len(pool)),
            key=lambda i: (_bin_distance(pool_bins[i], target), i),
        )
        elites: list[tuple[int, dict]] = []
        for pool_index in ranked:
            if len(elites) >= elite_size:
                break
            if validate_grid(pool[pool_index]).ok:
                elites.append(
                    (
                        _bin_distance(pool_bins[pool_index], target),
                        pool[pool_index],
                    )
                )
        best_distance = elites[0][0] if elites else 3 * SCALE_BINS_PER_AXIS
        reached = False
        witness: dict | None = None
        attempts = 0
        for attempt in range(per_bin_budget):
            attempts += 1
            parent = elites[attempt % len(elites)][1] if elites else seeds[0]
            child_seed = (
                rng_seed
                + PROBE_SEED_OFFSET
                + bin_index * per_bin_budget
                + attempt
            )
            try:
                child = generate_candidate(
                    parent, model, None, rng_seed=child_seed
                )
            except ValueError:
                continue
            child_bin = bin_of(child)
            distance = _bin_distance(child_bin, target)
            best_distance = min(best_distance, distance)
            elites.append((distance, child))
            elites.sort(key=lambda pair: pair[0])
            del elites[elite_size:]
            if child_bin == target:
                reached = True
                witness = child
                break
        record: dict = {
            "bin": list(target),
            "reached": reached,
            "attempts": attempts,
            "best_distance": 0 if reached else best_distance,
        }
        if witness is not None:
            record["witness"] = witness
            newly_reached += 1
        per_bin.append(record)

    still_unreached = [r for r in per_bin if not r["reached"]]
    axis_emptiness = {
        name: {
            str(value): sum(
                1
                for record in still_unreached
                if record["bin"][axis_index] == value
            )
            for value in axes
        }
        for axis_index, name in enumerate(SCALE_DESCRIPTOR_NAMES)
    }

    unprobed = len(unreached) - len(probed_targets)
    finding = (
        f"generators reach {len(reached_by_generators)}/512; the probe "
        f"reached {newly_reached} more of {len(probed_targets)} probed "
        f"bins under the engine's own move set; "
        f"{len(still_unreached)} stay unreached within budget "
        f"{per_bin_budget} — a measured bound, not an impossibility "
        "proof"
    )

    blocked_states = [
        "unreached_within_budget_is_a_bound_not_a_proof (geometric "
        "emptiness of the remaining bins is a HYPOTHESIS the "
        "axis-emptiness table informs, never a conclusion)",
    ]
    if probe_limit is not None and unprobed:
        blocked_states.append(
            f"probe_limit_cap ({unprobed} unreached bins left unprobed "
            "by the explicit limit — named, never silent)"
        )

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete",
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 20 J1: per-bin reachability of the 512-niche "
            "geometry under the engine's OWN move set (the promoted "
            "generation model + generate_candidate + package "
            "validation), witnesses verified, bounds honest."
        ),
        "source_artifacts": [
            "data/archives/occupancy_saturation_stage0.json",
            "labs/map_elites_archive/niche_scale_archive.py",
            "packages/mecha_engine/src/mecha_engine/generation/generate.py",
            "research/experiment_reports/2026-07-20-occupancy-saturation.md",
        ],
        "parameters": {
            "derivation_count": derivation_count,
            "pool_count": pool_count,
            "per_bin_budget": per_bin_budget,
            "elite_size": elite_size,
            "probe_limit": probe_limit,
            "rng_seed": rng_seed,
        },
        "metrics": {
            "total_niches": len(all_bins),
            "edges": edges,
            "reached_by_generators": len(reached_by_generators),
            "probed": {
                "count": len(probed_targets),
                "newly_reached": newly_reached,
                "unreached_within_budget": len(still_unreached),
            },
            "unprobed_bins": unprobed,
            "axis_emptiness_of_unreached": axis_emptiness,
            "per_bin": per_bin,
            "finding": finding,
        },
        "closed_states": [
            "reachability_probed_under_the_engines_own_move_set",
            "every_witness_validator_passing_and_bin_verified",
        ],
        "blocked_states": blocked_states,
        "decision": finding,
        "next_research_step": (
            "J2: motion-role emission measurement and the gated "
            "generator increment — the axis-emptiness table says where "
            "range must come from"
        ),
    }


def write_reachability_artifacts(
    output_dir: str | Path, report: dict
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{ARTIFACT_ID}.json"
    path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--derivation-count", type=int, default=600)
    parser.add_argument("--pool-count", type=int, default=9000)
    parser.add_argument(
        "--per-bin-budget", type=int, default=DEFAULT_PER_BIN_BUDGET
    )
    parser.add_argument("--probe-limit", type=int, default=None)
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "archives"
    )
    args = parser.parse_args()
    report = build_reachability_report(
        derivation_count=args.derivation_count,
        pool_count=args.pool_count,
        per_bin_budget=args.per_bin_budget,
        probe_limit=args.probe_limit,
    )
    written = write_reachability_artifacts(args.output_dir, report)
    print(f"wrote {written}")
    print(report["metrics"]["finding"])
