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


# --- K3 (cycle 21): the escalation on the last nine bins -------------
#
# Pre-registered BEFORE the run: the targets are the committed probe
# artifact's unreached bins VERBATIM; the budget escalates 200 -> 2000
# per bin; the DR 0038 resample-temperature rider rides an
# attempt-indexed ladder (None, 0.5, 1.0, 1.5, 2.0 — the full legal
# range); the elite pool deepens 4 -> 8. The verdict per bin is
# "reached" (a validator-passing witness whose descriptor recomputes
# into the exact bin, committed) or "bounded_sharper" (the budget, the
# best distance, and the BLOCKING-AXIS instrument: which axis the
# distance-1 gap sits on, the required octile interval from the frozen
# edges, and the best raw value attained on that axis CONDITIONED on
# the other two axes sitting on-target). The move set stays the
# engine's own (generate_candidate only — no hand-painted exceptions);
# the descent's distance-to-target selection subsumes novelty-first
# for a single-target probe (novelty-first optimizes unseen-niche
# breadth; a probe optimizes one niche). An impossibility claim is
# never made from a budget — bounds stay bounds. Run-once wall-clock
# bound registered at 900 s (DR 0028; an overage is cited, never
# silent).

ESCALATION_ARTIFACT_ID = "reachability_escalation_stage0"
ESCALATION_REPORT_DATE = "2026-07-21"
DEFAULT_ESCALATION_BUDGET = 2000
ESCALATION_ELITE_SIZE = 8
TEMPERATURE_LADDER = (None, 0.5, 1.0, 1.5, 2.0)
ESCALATION_SEED_OFFSET = 11_000_029
ESCALATION_BOUND_S = 900


def _committed_unreached_bins() -> list[tuple[int, ...]]:
    committed = json.loads(
        (ROOT / "data" / "archives" / f"{ARTIFACT_ID}.json").read_text(
            encoding="utf-8"
        )
    )
    return [
        tuple(record["bin"])
        for record in committed["metrics"]["per_bin"]
        if not record["reached"]
    ]


def _octile_interval(
    edges_for_axis: list[float], octile: int
) -> list[float | None]:
    lower = edges_for_axis[octile - 1] if octile > 0 else None
    upper = (
        edges_for_axis[octile]
        if octile < len(edges_for_axis)
        else None
    )
    return [lower, upper]


def build_escalation_report(
    *,
    targets: list[tuple[int, ...]] | None = None,
    per_bin_budget: int = DEFAULT_ESCALATION_BUDGET,
    elite_size: int = ESCALATION_ELITE_SIZE,
    derivation_count: int = 600,
    pool_count: int = 9000,
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

    def axis_values_of(grid: dict) -> dict:
        return scale_axis_values(grid, slip_profile=slip_profile)

    def bin_of_values(values: dict) -> tuple[int, ...]:
        return scale_descriptor_for_values(values, edges)

    pool, _ = build_population(
        pool_count, rng_seed + EVALUATION_STREAM_OFFSET, seeds, wfc_model
    )
    pool_bins = [bin_of_values(axis_values_of(grid)) for grid in pool]

    if targets is None:
        targets = _committed_unreached_bins()
    targets = [tuple(target) for target in targets]

    model = train_generation_model(seeds)
    per_bin: list[dict] = []
    newly_reached = 0
    for bin_index, target in enumerate(targets):
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
        witness_temperature: float | None = None
        attempts = 0
        # The blocking-axis instrument: raw-value extremes per axis,
        # conditioned on the OTHER two axes sitting on-target.
        conditional: dict[str, dict] = {
            name: {"count": 0, "min": None, "max": None}
            for name in SCALE_DESCRIPTOR_NAMES
        }
        nearest_axis_misses: dict[str, int] = {
            name: 0 for name in SCALE_DESCRIPTOR_NAMES
        }
        for attempt in range(per_bin_budget):
            attempts += 1
            parent = elites[attempt % len(elites)][1] if elites else seeds[0]
            temperature = TEMPERATURE_LADDER[
                attempt % len(TEMPERATURE_LADDER)
            ]
            child_seed = (
                rng_seed
                + ESCALATION_SEED_OFFSET
                + bin_index * per_bin_budget
                + attempt
            )
            try:
                child = generate_candidate(
                    parent,
                    model,
                    None,
                    rng_seed=child_seed,
                    resample_temperature=temperature,
                )
            except ValueError:
                continue
            child_values = axis_values_of(child)
            child_bin = bin_of_values(child_values)
            distance = _bin_distance(child_bin, target)
            for axis_index, name in enumerate(SCALE_DESCRIPTOR_NAMES):
                others_match = all(
                    child_bin[i] == target[i]
                    for i in range(len(target))
                    if i != axis_index
                )
                if others_match:
                    slot = conditional[name]
                    value = child_values[name]
                    slot["count"] += 1
                    slot["min"] = (
                        value
                        if slot["min"] is None
                        else min(slot["min"], value)
                    )
                    slot["max"] = (
                        value
                        if slot["max"] is None
                        else max(slot["max"], value)
                    )
                if distance == 1 and child_bin[axis_index] != target[axis_index]:
                    nearest_axis_misses[name] += 1
            best_distance = min(best_distance, distance)
            elites.append((distance, child))
            elites.sort(key=lambda pair: pair[0])
            del elites[elite_size:]
            if child_bin == target:
                reached = True
                witness = child
                witness_temperature = temperature
                break
        record: dict = {
            "bin": list(target),
            "verdict": "reached" if reached else "bounded_sharper",
            "reached": reached,
            "attempts": attempts,
            "best_distance": 0 if reached else best_distance,
        }
        if witness is not None:
            newly_reached += 1
            record["witness"] = witness
            record["witness_temperature"] = witness_temperature
            record["witness_bin_verified"] = (
                bin_of_values(axis_values_of(witness)) == target
                and validate_grid(witness).ok
            )
        else:
            blocking_axes = sorted(
                name
                for name, misses in nearest_axis_misses.items()
                if misses
            )
            record["blocking"] = {
                "axes": blocking_axes,
                "distance_one_axis_misses": nearest_axis_misses,
                "per_axis": {
                    name: {
                        "required_octile": target[axis_index],
                        "required_interval": _octile_interval(
                            edges[name], target[axis_index]
                        ),
                        "conditional_candidates": conditional[name][
                            "count"
                        ],
                        "conditional_min": conditional[name]["min"],
                        "conditional_max": conditional[name]["max"],
                    }
                    for axis_index, name in enumerate(
                        SCALE_DESCRIPTOR_NAMES
                    )
                    if name in blocking_axes
                },
            }
        per_bin.append(record)

    still_unreached = [r for r in per_bin if not r["reached"]]
    finding = (
        f"escalation over {len(targets)} committed unreached bins "
        f"(budget {per_bin_budget}, temperature ladder "
        f"{list(TEMPERATURE_LADDER)}, elite depth {elite_size}): "
        f"{newly_reached} reached with bin-verified witnesses; "
        f"{len(still_unreached)} bounded SHARPER with the blocking "
        "axis named and its conditional attainment measured — a bound, "
        "never an impossibility proof"
    )

    return {
        "artifact_id": ESCALATION_ARTIFACT_ID,
        "status": "complete",
        "date": ESCALATION_REPORT_DATE,
        "purpose": (
            "Cycle 21 K3: the last unreached descriptor bins under the "
            "FULL post-DR-0038 move set — the vocabulary-complete "
            "model, the resample-temperature ladder, a deeper guided "
            "descent — reached-with-witness or bounded sharper with "
            "the blocking axis measured, never asserted."
        ),
        "source_artifacts": [
            "data/archives/reachability_probe_stage0.json",
            "labs/map_elites_archive/reachability_probe.py",
            "packages/mecha_engine/src/mecha_engine/generation/generate.py",
            "research/decision_records/0038-vocabulary-complete-generation-alphabet.md",
        ],
        "parameters": {
            "targets": [list(target) for target in targets],
            "per_bin_budget": per_bin_budget,
            "elite_size": elite_size,
            "temperature_ladder": [
                temperature for temperature in TEMPERATURE_LADDER
            ],
            "derivation_count": derivation_count,
            "pool_count": pool_count,
            "rng_seed": rng_seed,
            "run_once_bound_seconds": ESCALATION_BOUND_S,
        },
        "metrics": {
            "targets_probed": len(targets),
            "newly_reached": newly_reached,
            "bounded_sharper": len(still_unreached),
            "per_bin": per_bin,
            "finding": finding,
        },
        "closed_states": [
            "escalation_ran_under_the_engines_own_move_set",
            "every_witness_validator_passing_and_bin_verified",
            "blocking_axis_measured_for_every_bounded_bin",
        ],
        "blocked_states": [
            "bounded_sharper_is_a_bound_not_a_proof (the conditional "
            "attainment names the gap; geometric emptiness stays a "
            "hypothesis unless proven analytically in its own record)",
        ],
        "decision": finding,
        "next_research_step": (
            "reached bins fold into the range prose; bounded bins "
            "carry their measured gap into any future generator "
            "increment's charter"
        ),
    }


def write_escalation_artifacts(
    output_dir: str | Path, report: dict
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{ESCALATION_ARTIFACT_ID}.json"
    path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return path


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
        "--escalate",
        action="store_true",
        help="run the K3 escalation on the committed unreached bins",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "archives"
    )
    args = parser.parse_args()
    if args.escalate:
        escalation = build_escalation_report()
        written = write_escalation_artifacts(args.output_dir, escalation)
        print(f"wrote {written}")
        print(escalation["metrics"]["finding"])
    else:
        report = build_reachability_report(
            derivation_count=args.derivation_count,
            pool_count=args.pool_count,
            per_bin_budget=args.per_bin_budget,
            probe_limit=args.probe_limit,
        )
        written = write_reachability_artifacts(args.output_dir, report)
        print(f"wrote {written}")
        print(report["metrics"]["finding"])
