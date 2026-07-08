"""Stress-probe scaling: the /16 denominator re-derived at 16x16 (A3).

The archive's contracted morphology stress probe
(``mecha_engine.archive._metrics.lifecycle_probe_grid``):

    load = clamp(body_mass / 16 + (1 - symmetry) * 0.65 - sensor_count * 0.08)

was calibrated at 8x8 — DR 0014 flagged the /16 mass constant as
8x8-coupled and REQUIRED the replacement family be "re-derived from
evidence, never scaled by fiat". The A1/A2 measurements sharpened the
warning: the 16x16 corpus's median core FRACTION is higher than 8x8's
(51.5/256 = 0.201 vs 10/64 = 0.156), so the naive area law shifts the
load distribution upward. This lab is the required evidence: it measures
the EXACT engine statistic (the engine's own body_mass / symmetry_score /
sensor_count / clamp, and real ``run_episode`` survival) over the proven
corpora under three candidate denominator laws, all of which reproduce
the shipped /16 at 8x8:

- ``status_quo_16``   — D(w, h) = 16 (the shipped constant, unchanged)
- ``area_over_4``     — D(w, h) = w*h/4 (DR 0014's named family)
- ``four_x_floor``    — D(w, h) = 4 * body_core_min_cells(w, h) (tied to
  the DR 0029 ratified floor law; 4*4 = 16 at 8x8, 4*18 = 72 at 16x16)

The probe's own documented purpose decides: without a per-candidate load
the survival axis collapses into a single bin. Gates: 8x8 identity,
survival axis alive at 16x16 (>= 2 of the archive's 5 bins), no bin
regression against the measured 8x8 baseline, and bounded saturation.
Adoption picks the surviving law whose 16x16 load median lands closest
to the measured 8x8 baseline median (distribution preservation).
"""

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from statistics import median


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME = ROOT / "labs" / "grid_genome"
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
for path in [GRID_GENOME, PACKAGE_SRC]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from corpus_builder import build_seed_grids, build_seed_grids_16  # noqa: E402

# The exact engine statistic, not a reconstruction (honesty norm: measure
# what the engine computes; the parity test pins load_for against
# lifecycle_probe_grid at the shipped denominator).
from mecha_engine.archive._metrics import (  # noqa: E402
    body_mass,
    clamp,
    sensor_count,
    symmetry_score,
)
from mecha_engine.genome.validation import body_core_min_cells  # noqa: E402
from mecha_engine.lifecycle import run_episode  # noqa: E402


REPORT_DATE = "2026-07-08"
ARTIFACT_ID = "stress_probe_scaling_stage0"
# The archive's own episode configuration (DEFAULT_LIFECYCLE_TICKS) and a
# fixed seed: the measurement runs the statistic the archive runs.
EPISODE_TICKS = 24
RNG_SEED = 11
# The archive's lifecycle_survival bin edges (descriptors.BIN_THRESHOLDS).
SURVIVAL_BIN_EDGES = [0.2, 0.4, 0.6, 0.8]

DENOMINATOR_LAWS = {
    "status_quo_16": lambda width, height: 16,
    "area_over_4": lambda width, height: (width * height) // 4,
    "four_x_floor": lambda width, height: 4 * body_core_min_cells(width, height),
}


def load_for(grid: dict, denominator: int) -> float:
    """The engine's probe load with a parametric mass denominator."""
    return clamp(
        body_mass(grid) / denominator
        + (1 - symmetry_score(grid)) * 0.65
        - sensor_count(grid) * 0.08
    )


def probe_with_load(grid: dict, load: float) -> dict:
    probe = deepcopy(grid)
    for cell in probe.get("cells", []):
        cell["stress"] = round(load, 6)
    return probe


def measure_population(grids: list[dict], denominator: int) -> dict:
    loads: list[float] = []
    ratios: list[float] = []
    bins: set[int] = set()
    for grid in grids:
        load = load_for(grid, denominator)
        loads.append(load)
        episode = run_episode(
            probe_with_load(grid, load),
            None,
            policy="switchboard",
            ticks=EPISODE_TICKS,
            rng_seed=RNG_SEED,
        )
        ratio = episode["survival_ticks"] / EPISODE_TICKS
        ratios.append(ratio)
        bins.add(_survival_bin(ratio))
    return {
        "denominator": denominator,
        "population": len(grids),
        "load": _stat_triplet(loads),
        "saturated_fraction": round(
            sum(1 for load in loads if load >= 1.0) / len(loads), 6
        ),
        "survival_ratio": _stat_triplet(ratios),
        "full_survival_fraction": round(
            sum(1 for ratio in ratios if ratio == 1.0) / len(ratios), 6
        ),
        "survival_bins": sorted(bins),
        "survival_bins_covered": len(bins),
    }


def build_stress_probe_scaling_report() -> dict:
    seeds_8 = build_seed_grids()
    seeds_16 = build_seed_grids_16()
    baseline = measure_population(seeds_8, 16)

    candidates: dict[str, dict] = {}
    for name, law in sorted(DENOMINATOR_LAWS.items()):
        row = measure_population(seeds_16, law(16, 16))
        row["gates"] = {
            "reproduces_16_at_8x8": law(8, 8) == 16,
            "survival_axis_alive": row["survival_bins_covered"] >= 2,
            "no_bin_regression_vs_baseline": (
                row["survival_bins_covered"] >= baseline["survival_bins_covered"]
            ),
            "saturation_not_total": row["saturated_fraction"] < 1.0,
        }
        candidates[name] = row

    passing = [
        name
        for name, row in sorted(candidates.items())
        if all(row["gates"].values())
    ]
    if passing:
        adopted_law = min(
            passing,
            key=lambda name: (
                -candidates[name]["survival_bins_covered"],
                abs(
                    candidates[name]["load"]["p50"] - baseline["load"]["p50"]
                ),
                candidates[name]["saturated_fraction"],
                name,
            ),
        )
        adopted = {
            "law": adopted_law,
            "denominator_16x16": candidates[adopted_law]["denominator"],
            "denominator_8x8": 16,
        }
        status = "complete"
    else:
        adopted = {"law": None, "denominator_16x16": None, "denominator_8x8": 16}
        status = "refuted"

    return {
        "artifact_id": ARTIFACT_ID,
        "status": status,
        "date": REPORT_DATE,
        "purpose": (
            "Re-derive the archive stress probe's 8x8-coupled /16 mass "
            "denominator at the ratified 16x16 scale from evidence (DR 0014's "
            "requirement): measure the exact engine load statistic and real "
            "run_episode survival over both proven corpora under candidate "
            "denominator laws that all reproduce /16 at 8x8, gate on the "
            "probe's own documented purpose (a non-collapsed survival axis), "
            "and adopt by distribution preservation."
        ),
        "source_artifacts": [
            "packages/mecha_engine/src/mecha_engine/archive/_metrics.py",
            "packages/mecha_engine/src/mecha_engine/lifecycle",
            "data/seed_grids",
            "data/seed_grids_16x16",
            "research/decision_records/0014-grid-size-commitment.md",
            "research/decision_records/0029-16x16-default-grid-scale.md",
            "data/grid_genome/invariant_scaling_16x16_stage0.json",
        ],
        "metrics": {
            "episode_ticks": EPISODE_TICKS,
            "rng_seed": RNG_SEED,
            "survival_bin_edges": SURVIVAL_BIN_EDGES,
            "baseline_8x8": baseline,
            "candidates_16x16": candidates,
            "adopted": adopted,
        },
        "closed_states": (
            [
                "stress_probe_denominator_law_adopted",
                "all_candidate_laws_reproduce_16_at_8x8",
                "survival_axis_measured_not_assumed",
            ]
            if status == "complete"
            else ["all_candidate_laws_refuted_at_16x16"]
        ),
        "blocked_states": [
            "engine_probe_still_ships_the_8x8_constant (adoption lands with this A3 increment across the engine and its verbatim mirrors)",
            "repair_model_not_retrained_at_16x16 (next A3 increment)",
            "slip_mass_bounds_still_8x8_denominated (A3, DR 0012 extension ladder)",
        ],
        "decision": (
            (
                f"Adopt denominator law '{adopted['law']}' "
                f"(D = 16 at 8x8, D = {adopted['denominator_16x16']} at 16x16) "
                "into lifecycle_probe_grid and every verbatim mirror; 8x8 "
                "behavior byte-identical by the identity gate."
            )
            if status == "complete"
            else (
                "No candidate law kept the survival axis alive at 16x16; the "
                "denominator needs a corpus-fit design, recorded here as a "
                "refutation, before any engine change."
            )
        ),
        "next_research_step": (
            "Adopt the law in mecha_engine.archive._metrics plus the four "
            "verbatim mirrors (runtime lab probe, archive contract oracle, "
            "extended-descriptors lab, workshop morphology panel), then "
            "retrain repair at 16x16."
        ),
    }


def write_stress_probe_scaling_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{ARTIFACT_ID}.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )


def _survival_bin(ratio: float) -> int:
    for index, edge in enumerate(SURVIVAL_BIN_EDGES):
        if ratio <= edge:
            return index
    return len(SURVIVAL_BIN_EDGES)


def _stat_triplet(values: list[float]) -> dict:
    ordered = sorted(values)
    return {
        "min": round(ordered[0], 6),
        "p50": round(median(ordered), 6),
        "p95": round(ordered[int(0.95 * (len(ordered) - 1))], 6),
        "max": round(ordered[-1], 6),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Stress-probe scaling lab (A3).")
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "archives"
    )
    args = parser.parse_args()
    report = build_stress_probe_scaling_report()
    write_stress_probe_scaling_artifacts(args.output_dir, report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "baseline_8x8": report["metrics"]["baseline_8x8"],
                "candidates_16x16": report["metrics"]["candidates_16x16"],
                "adopted": report["metrics"]["adopted"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
