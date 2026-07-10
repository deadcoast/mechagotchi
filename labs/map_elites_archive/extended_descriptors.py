import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME = ROOT / "labs" / "grid_genome"
READABILITY = ROOT / "labs" / "readability_benchmark"
LIFECYCLE = ROOT / "labs" / "lifecycle_sim"
for path in [GRID_GENOME, READABILITY, LIFECYCLE]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from constrained_generator import (
    DEFAULT_MUTATION_RATE_CAPS,
    SLIP_MUTATION_CAP_KEYS,
    build_constrained_corpus,
)
from corpus_builder import build_seed_grids
from darwin_archive import (
    _mass_bin_thresholds as _darwin_mass_thresholds,
    build_map_elites_archive,
    descriptor_for_grid,
)
from lifecycle_sim import run_lifecycle_simulation
from readability_benchmark import score_readability
from slip import is_grid_aligned
from validator import validate_grid


DESCRIPTOR_NAMES = [
    "body_mass",
    "sensor_count",
    "symmetry",
    "readability",
    "lifecycle_survival",
    "mutation_stability",
    "behavior_neediness",
]

DESCRIPTOR_CARDINALITIES = [5, 5, 5, 5, 5, 5, 5]

FITNESS_WEIGHTS = {
    "survival": 0.28,
    "readability": 0.24,
    "validity": 0.18,
    "bond": 0.12,
    "mutation_stability": 0.1,
    "slip_alignment": 0.08,
}


def extended_descriptor_for_grid(
    grid: dict,
    *,
    slip_profile: dict | None = None,
    lifecycle_ticks: int = 24,
    rng_seed: int = 20260512,
) -> dict:
    readability = score_readability(grid)
    lifecycle = _lifecycle_or_empty(
        grid, slip_profile=slip_profile, lifecycle_ticks=lifecycle_ticks, rng_seed=rng_seed
    )
    mutation_stability = _mutation_stability(grid, slip_profile)
    neediness = _behavior_neediness(grid, slip_profile)

    values = (
        # DR 0029/0030 pattern (cycle 09 A4): the mass edges scale by the
        # grid's own area from the 8x8 reference (darwin_archive mirror).
        _bin(_body_mass(grid), _darwin_mass_thresholds(grid)),
        _bin(_sensor_count(grid), [1, 2, 3, 4]),
        _bin(_symmetry_score(grid), [0.25, 0.5, 0.75, 0.9]),
        _bin(readability["proxy_readability_score"], [0.35, 0.55, 0.7, 0.85]),
        _bin(lifecycle["survival_ratio"], [0.2, 0.4, 0.6, 0.8]),
        _bin(mutation_stability, [0.3, 0.5, 0.7, 0.9]),
        _bin(neediness, [0.2, 0.4, 0.6, 0.8]),
    )
    return {
        "names": DESCRIPTOR_NAMES,
        "values": values,
        "key": _descriptor_key(values),
        "metrics": {
            "body_mass": _body_mass(grid),
            "sensor_count": _sensor_count(grid),
            "symmetry": round(_symmetry_score(grid), 6),
            "readability": readability["proxy_readability_score"],
            "lifecycle_survival": lifecycle["survival_ratio"],
            "mutation_stability": round(mutation_stability, 6),
            "behavior_neediness": round(neediness, 6),
        },
    }


def score_extended_candidate(
    grid: dict,
    *,
    slip_profile: dict | None = None,
    lifecycle_ticks: int = 24,
    rng_seed: int = 20260512,
) -> dict:
    validation = validate_grid(grid)
    readability = score_readability(grid)
    lifecycle = _lifecycle_or_empty(
        grid, slip_profile=slip_profile, lifecycle_ticks=lifecycle_ticks, rng_seed=rng_seed
    )
    mutation_stability = _mutation_stability(grid, slip_profile)
    slip_alignment = 1.0 if slip_profile is None or is_grid_aligned(grid, slip_profile).ok else 0.0
    bond = lifecycle["final_state"].get("bond", 0.0)

    components = {
        "survival": lifecycle["survival_ratio"],
        "readability": readability["proxy_readability_score"],
        "validity": 1.0 if validation.ok else 0.0,
        "bond": bond,
        "mutation_stability": mutation_stability,
        "slip_alignment": slip_alignment,
    }
    fitness = sum(components[name] * FITNESS_WEIGHTS[name] for name in FITNESS_WEIGHTS)
    return {
        "fitness": round(_clamp(fitness), 6),
        "components": {key: round(value, 6) for key, value in components.items()},
        "readability": readability,
        "lifecycle": lifecycle,
        "validation_errors": validation.errors,
    }


def build_extended_map_elites_archive(
    candidates: list[dict],
    *,
    slip_profile: dict | None = None,
    lifecycle_ticks: int = 24,
    rng_seed: int = 20260512,
) -> dict:
    elites: dict[str, dict] = {}
    observed_bins: dict[str, set[int]] = {name: set() for name in DESCRIPTOR_NAMES}
    for index, grid in enumerate(candidates):
        descriptor = extended_descriptor_for_grid(
            grid,
            slip_profile=slip_profile,
            lifecycle_ticks=lifecycle_ticks,
            rng_seed=rng_seed + index,
        )
        for name, value in zip(DESCRIPTOR_NAMES, descriptor["values"]):
            observed_bins[name].add(value)
        score = score_extended_candidate(
            grid,
            slip_profile=slip_profile,
            lifecycle_ticks=lifecycle_ticks,
            rng_seed=rng_seed + index,
        )
        current = elites.get(descriptor["key"])
        if current is None or score["fitness"] > current["fitness"]:
            elites[descriptor["key"]] = {
                "grid_id": grid["grid_id"],
                "fitness": score["fitness"],
                "descriptor": descriptor,
                "score_components": score["components"],
            }

    total_niches = _total_niches()
    qd_score = sum(elite["fitness"] for elite in elites.values())
    return {
        "archive_id": "map_elites_extended_stage0",
        "date": "2026-07-04",
        "descriptor_names": DESCRIPTOR_NAMES,
        "descriptor_dimensions": len(DESCRIPTOR_NAMES),
        "descriptor_cardinalities": DESCRIPTOR_CARDINALITIES,
        "total_possible_niches": total_niches,
        "occupied_niches": len(elites),
        "coverage": round(len(elites) / total_niches, 6),
        # Distinct bins observed per axis across all candidates. An axis with
        # spread 1 is degenerate for this run and inflates total_possible_niches
        # relative to what the candidate set can actually reach (H-03 guard).
        "descriptor_bin_spread": {
            name: len(observed_bins[name]) for name in DESCRIPTOR_NAMES
        },
        "best_fitness": max((elite["fitness"] for elite in elites.values()), default=0),
        "mean_elite_fitness": round(qd_score / len(elites), 6) if elites else 0,
        "qd_score": round(qd_score, 6),
        "elites": {key: elites[key] for key in sorted(elites)},
        "parameters": {
            "candidate_count": len(candidates),
            "lifecycle_ticks": lifecycle_ticks,
            "rng_seed": rng_seed,
        },
    }


def compare_extended_to_legacy(
    candidates: list[dict],
    *,
    slip_profile: dict | None = None,
    lifecycle_ticks: int = 24,
    rng_seed: int = 20260512,
) -> dict:
    legacy = build_map_elites_archive(candidates, slip=slip_profile)
    extended = build_extended_map_elites_archive(
        candidates,
        slip_profile=slip_profile,
        lifecycle_ticks=lifecycle_ticks,
        rng_seed=rng_seed,
    )
    legacy_niches = {descriptor_for_grid(grid) for grid in candidates}
    extended_niches = {
        tuple(
            extended_descriptor_for_grid(
                grid,
                slip_profile=slip_profile,
                lifecycle_ticks=lifecycle_ticks,
                rng_seed=rng_seed + index,
            )["values"]
        )
        for index, grid in enumerate(candidates)
    }
    return {
        "candidate_count": len(candidates),
        "legacy_descriptor_dimensions": 3,
        "extended_descriptor_dimensions": len(DESCRIPTOR_NAMES),
        "legacy_unique_candidate_niches": len(legacy_niches),
        "extended_unique_candidate_niches": len(extended_niches),
        "legacy_occupied_niches": legacy["occupied_niches"],
        "extended_occupied_niches": extended["occupied_niches"],
        "legacy_coverage": legacy["coverage"],
        "extended_coverage": extended["coverage"],
        "legacy_best_fitness": legacy["best_fitness"],
        "extended_best_fitness": extended["best_fitness"],
        "extended_qd_score": extended["qd_score"],
        "descriptor_expansion": len(DESCRIPTOR_NAMES) - 3,
    }


def write_extended_archive_artifacts(
    output_path: Path, archive: dict, comparison: dict
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "archive": archive,
        "comparison": comparison,
        "source_refs": [
            {
                "name": "Illuminating search spaces by mapping elites",
                "url": "https://arxiv.org/abs/1504.04909",
                "use": "Original MAP-Elites reference for behavior-space archives.",
            },
            {
                "name": "QDax MAP-Elites docs",
                "url": "https://qdax.readthedocs.io/en/develop/api_documentation/core/map_elites/",
                "use": "Implementation reference for repertoires, descriptors, and metrics.",
            },
        ],
        "decision": "prototype",
        "limitations": [
            "Lifecycle metrics use synthetic switchboard policy simulations.",
            "Readability is still proxy-scored until manual ratings are collected.",
            "Descriptor cardinalities are hand-set and need calibration.",
            (
                "The lifecycle probe stresses each candidate with a "
                "morphology-derived load, but the stage-0 switchboard sim is "
                "bistable: a candidate either stabilizes (full survival) or "
                "enters a terminal stress spiral lasting ~12-14 ticks, so the "
                "lifecycle_survival axis reaches only 2 of its 5 bins. "
                "Intermediate survival bins await a harsher lifecycle model."
            ),
            (
                "mutation_stability is cap-normalized (share of the SLIP "
                "mutation budget used); raw mean rates cannot leave the top "
                "bin under profile caps."
            ),
        ],
    }
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    # The folder README covers every archive artifact (it used to describe
    # only this lab's output and clobbered the fuller listing on regen).
    (output_path.parent / "README.md").write_text(
        "# MAP-Elites Archive Artifacts\n\n"
        "Measured archive evidence produced by `labs/map_elites_archive/`.\n\n"
        "- `map_elites_stage0.json` - the legacy 3-axis baseline archive\n"
        "  (body mass, sensor count, symmetry).\n"
        "- `map_elites_extended_stage0.json` - the calibrated 7-axis extended\n"
        "  archive (adds readability, lifecycle survival, mutation stability,\n"
        "  behavior neediness); the package parity pins read its numbers.\n"
        "- `archive_comparators_stage0.json` - scalar/novelty comparators kept\n"
        "  OUTSIDE the archive (the repertoire is never a leaderboard).\n"
        "- `stress_probe_scaling_stage0.json` - the size-parametric lifecycle\n"
        "  stress-probe denominator evidence (cycle 09 A3).\n"
        "- `generator_evolution_ab_stage0.json` - the generator-vs-evolution\n"
        "  A/B evidence.\n"
        "- `niche_scale_archive_stage0.json` - cycle 13 E1: the documented\n"
        "  first-pass 8x8x8 geometry (symmetry, silhouette-entropy visual\n"
        "  complexity, behavior neediness) with empirically derived octile\n"
        "  edges; 274/512 niches occupied over a disjoint 3000-candidate\n"
        "  evaluation population; the evaluation-unit wall-clock pilot\n"
        "  (6.29 ms -> 125.8 s @ 20k) in its `measured` section.\n"
        "- `evaluation_loop_scale_stage0.json` - cycle 13 E3: the full\n"
        "  generational loop at the documented budget - 20,480 stress-probed\n"
        "  lifecycle evaluations over 79 generations of population 256 (WFC\n"
        "  parent path per E2). 281/512 niches (coverage 0.549), QD 222.1,\n"
        "  zero collapse failures; measured 174.12 s vs the pre-registered\n"
        "  600 s bound - stdlib holds. The honest saturation observation:\n"
        "  occupancy plateaus ~gen 50; late generations refine fitness.\n"
        "- `coverage_qd_gates_stage0.json` - cycle 13 E4: the documented gate\n"
        "  at the documented ten-seed protocol (20 full-scale runs). Coverage\n"
        "  MET 0.549 vs >=0.25; best fitness identical across arms; the\n"
        "  GA-advantage gate REFUTED (+22.6% vs >=25%, converged) - recorded,\n"
        "  dispositioned by DR 0032 (MAP-Elites stays adopted; named\n"
        "  re-openers). Carries per-seed elite rosters for E5.\n"
        "- `recurrent_families_stage0.json` - cycle 13 E5: 52 recurrent\n"
        "  morphological families across ALL TEN independent seeded runs vs\n"
        "  the documented >=5 (strict intersection over 4x4x4 coarse\n"
        "  descriptor cells; nothing curated). Species memory, measured.\n",
        encoding="utf-8",
    )


def _lifecycle_probe_grid(grid: dict) -> dict:
    """Return a copy of the grid carrying a morphology-derived stress load.

    Generated candidates ship with pristine cells (stress 0, damage 0) and
    the SLIP behavior profile is constant for an archive run, so every valid
    candidate used to share one identical lifecycle trajectory and the
    lifecycle_survival axis collapsed into a single bin (review finding
    L-12). The archive therefore probes each candidate under a deterministic
    structural stress load derived from its own morphology:

        load = clamp(body_mass / (width * height / 4) + (1 - symmetry) * 0.65
                     - sensor_count * 0.08)

    - body_mass / (w*h/4): heavier bodies strain the substrate. The
      denominator is size-parametric since cycle 09 A3 (16 at 8x8 — the
      original calibrated constant — and 64 at the ratified 16x16;
      measured in stress_probe_scaling.py after DR 0014 flagged the /16
      as 8x8-coupled);
    - (1 - symmetry) * 0.65: asymmetric silhouettes carry unbalanced load;
    - sensor_count * 0.08: sensor coverage relieves load (needs are noticed
      and regulated sooner).

    The load is written to every cell's "stress" field on a deep copy;
    initial_lifecycle_state translates mean cell stress into the starting
    stress/grid_stability, and whether the switchboard policy can stabilize
    that starting point decides survival. lifecycle_sim's drift, action, and
    death arithmetic are untouched.
    """
    probe = deepcopy(grid)
    load = _clamp(
        _body_mass(grid) / _probe_mass_denominator(grid)
        + (1 - _symmetry_score(grid)) * 0.65
        - _sensor_count(grid) * 0.08
    )
    for cell in probe.get("cells", []):
        cell["stress"] = round(load, 6)
    return probe


def _probe_mass_denominator(grid: dict) -> int:
    # Mirrors mecha_engine.archive._metrics._probe_mass_denominator
    # (evidence: stress_probe_scaling.py, cycle 09 A3).
    grid_size = grid.get("grid_size")
    if (
        isinstance(grid_size, list)
        and len(grid_size) == 2
        and all(
            isinstance(dimension, int)
            and not isinstance(dimension, bool)
            and dimension > 0
            for dimension in grid_size
        )
    ):
        return max(1, (grid_size[0] * grid_size[1]) // 4)
    return 16


def _lifecycle_or_empty(
    grid: dict,
    *,
    slip_profile: dict | None,
    lifecycle_ticks: int,
    rng_seed: int,
) -> dict:
    if not validate_grid(grid).ok:
        return {
            "survival_ratio": 0.0,
            "need_balance": 0.0,
            "recovery_events": 0,
            "final_state": {"bond": 0.0},
        }
    try:
        result = run_lifecycle_simulation(
            _lifecycle_probe_grid(grid),
            slip_profile,
            ticks=lifecycle_ticks,
            policy="switchboard",
            rng_seed=rng_seed,
        )
    except ValueError:
        return {
            "survival_ratio": 0.0,
            "need_balance": 0.0,
            "recovery_events": 0,
            "final_state": {"bond": 0.0},
        }
    return {
        "survival_ratio": round(result["survival_ticks"] / lifecycle_ticks, 6)
        if lifecycle_ticks
        else 0.0,
        "need_balance": result["need_balance"],
        "recovery_events": result["recovery_events"],
        "final_state": result["final_state"],
    }


def _body_mass(grid: dict) -> int:
    return sum(1 for cell in grid.get("cells", []) if cell.get("organ") == "core")


def _sensor_count(grid: dict) -> int:
    return len(grid.get("organs", {}).get("sensors", {}).get("cells", []))


def _symmetry_score(grid: dict) -> float:
    width = grid.get("grid_size", [0, 0])[0]
    occupied = {(cell["x"], cell["y"], cell["role"]) for cell in grid.get("cells", [])}
    if not occupied:
        return 0.0
    mirrored = 0
    for x, y, role in occupied:
        if (width - 1 - x, y, role) in occupied:
            mirrored += 1
    return mirrored / len(occupied)


def _mutation_stability(grid: dict, slip_profile: dict | None) -> float:
    # Cap-normalized stability (review finding L-12). The previous metric,
    # 1 - mean(raw rates), could not leave the top descriptor bin for any
    # SLIP-compliant grid: the LCD profile caps the four rates at
    # 0.15/0.05/0.05/0.05, so the raw mean never exceeds 0.075 and stability
    # was pinned above 0.925 (> the 0.9 top bin edge). Measuring the share of
    # the permitted mutation budget a genome actually uses spans [0, 1] for
    # any profile:
    #
    #     stability = 1 - mean(rate_i / cap_i), each ratio clamped to [0, 1]
    #
    # Caps come from the archive run's SLIP profile (*_max limits) or, when
    # no profile is supplied, from the generator's default rate vector.
    mutation = grid.get("mutation", {})
    caps = DEFAULT_MUTATION_RATE_CAPS
    if slip_profile is not None:
        caps = {
            rate_key: _clamp(slip_profile.get("mutation", {}).get(cap_key, 0.0))
            for rate_key, cap_key in SLIP_MUTATION_CAP_KEYS.items()
        }
    ratios = []
    for rate_key, cap in caps.items():
        rate = _clamp(mutation.get(rate_key, 1.0))
        if cap <= 0:
            # A zero cap permits no mutation: any positive rate exhausts it.
            ratios.append(1.0 if rate > 0 else 0.0)
        else:
            ratios.append(min(1.0, rate / cap))
    return _clamp(1.0 - mean(ratios))


def _behavior_neediness(grid: dict, slip_profile: dict | None) -> float:
    # Descriptor axes must vary per candidate: a SLIP profile is constant for
    # an archive run, so using its neediness directly collapsed this axis to a
    # single bin (review finding H-03). The grid-derived term carries the
    # per-candidate signal; the profile neediness acts as a prior shift only.
    body_mass = _body_mass(grid)
    sensor_count = _sensor_count(grid)
    grid_term = 0.35 + sensor_count * 0.08 - body_mass * 0.01
    if slip_profile is not None:
        behavior = slip_profile.get("behavior", {})
        if "neediness" in behavior:
            return _clamp(grid_term + (_clamp(behavior["neediness"]) - 0.5) * 0.2)
    return _clamp(grid_term)


def _bin(value: float, thresholds: list[float]) -> int:
    for index, threshold in enumerate(thresholds):
        if value <= threshold:
            return index
    return len(thresholds)


def _descriptor_key(descriptor: tuple[int, ...]) -> str:
    return ",".join(str(value) for value in descriptor)


def _total_niches() -> int:
    total = 1
    for cardinality in DESCRIPTOR_CARDINALITIES:
        total *= cardinality
    return total


def _load_default_slip() -> dict:
    return json.loads(
        (ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )


def _clamp(value: object) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0.0
    return max(0.0, min(1.0, number))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "data/archives/map_elites_extended_stage0.json")
    parser.add_argument("--count", type=int, default=160)
    parser.add_argument("--rng-seed", type=int, default=20260512)
    parser.add_argument("--lifecycle-ticks", type=int, default=24)
    args = parser.parse_args()

    slip_profile = _load_default_slip()
    candidates = build_constrained_corpus(
        build_seed_grids(),
        count=args.count,
        rng_seed=args.rng_seed,
        slip=slip_profile,
    )
    archive = build_extended_map_elites_archive(
        candidates,
        slip_profile=slip_profile,
        lifecycle_ticks=args.lifecycle_ticks,
        rng_seed=args.rng_seed,
    )
    comparison = compare_extended_to_legacy(
        candidates,
        slip_profile=slip_profile,
        lifecycle_ticks=args.lifecycle_ticks,
        rng_seed=args.rng_seed,
    )
    write_extended_archive_artifacts(args.output, archive, comparison)
    print(json.dumps({"archive": {k: v for k, v in archive.items() if k != "elites"}, "comparison": comparison}, indent=2))


if __name__ == "__main__":
    main()
