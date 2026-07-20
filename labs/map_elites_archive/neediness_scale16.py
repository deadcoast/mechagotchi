"""Cycle 19 I5: behavior_neediness at 16x16 — measured, then judged.

The Phase-E gate's named remainder: behavior_neediness is
MASS-DOMINATED at 16x16. The formula's ``- body_mass * 0.01`` term was
calibrated against 8x8 masses (~6-16 core cells); 16x16 masses are ~4x
larger and swamp the ``+ sensor_count * 0.08`` signal, so the
descriptor axis stops measuring behavior and starts mirroring mass.

The candidate recalibration is the cycle 09 A4 pattern exactly —
reference-canvas scaling, an EXACT identity at 8x8:

    mass_term = body_mass * 0.01 * (64 / (width * height))

This lab MEASURES both formulas over both committed seed corpora
(the engine's own 8x8 and 16x16 grids) and judges pre-registered
gates on the numbers:

- ``identity_8x8``: the recalibrated formula changes NOTHING at the
  reference canvas (max abs diff 0.0 over the 8x8 corpus).
- ``mass_domination_reduced``: |pearson(neediness, mass)| at 16x16
  drops under the recalibration.
- ``sensor_signal_present``: pearson(neediness, sensors) at 16x16 is
  positive under the recalibration.

All three met -> ``recalibrate``; anything refuted ->
``remainder_stands`` (a first-class finding, never an error).
"""

import argparse
import json
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
GRID_GENOME_DIR = LAB_DIR.parent / "grid_genome"
for _path in (LAB_DIR, GRID_GENOME_DIR):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from extended_descriptors import (  # noqa: E402
    _body_mass,
    _clamp,
    _sensor_count,
)
from corpus_builder import build_seed_grids, build_seed_grids_16  # noqa: E402

ARTIFACT_ID = "neediness_scale16_stage0"
REPORT_DATE = "2026-07-20"
REFERENCE_AREA = 64
NEEDINESS_BIN_EDGES = [0.2, 0.4, 0.6, 0.8]


def pearson(xs: list[float], ys: list[float]) -> float:
    """Pearson correlation; 0.0 when either series has no variance

    (undefined, reported as absence-of-signal rather than fabricated).
    """
    count = len(xs)
    if count < 2:
        return 0.0
    mean_x = sum(xs) / count
    mean_y = sum(ys) / count
    var_x = sum((x - mean_x) ** 2 for x in xs)
    var_y = sum((y - mean_y) ** 2 for y in ys)
    if var_x == 0 or var_y == 0:
        return 0.0
    covariance = sum(
        (x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)
    )
    return covariance / (var_x**0.5 * var_y**0.5)


def neediness_original(grid: dict, slip_profile: dict | None) -> float:
    """The PRE-recalibration formula, frozen verbatim as the measured

    baseline. After DR 0036 the live sites carry the recalibration, so
    the historical formula must live here for the measurement to keep
    meaning what it measured.
    """
    grid_term = (
        0.35 + _sensor_count(grid) * 0.08 - _body_mass(grid) * 0.01
    )
    if slip_profile is not None:
        behavior = slip_profile.get("behavior", {})
        if "neediness" in behavior:
            return _clamp(
                grid_term + (_clamp(behavior["neediness"]) - 0.5) * 0.2
            )
    return _clamp(grid_term)


def neediness_recalibrated(grid: dict, slip_profile: dict | None) -> float:
    """The current formula with the mass term scaled to the reference

    canvas — an exact identity at 8x8 (64 / 64 = 1).
    """
    size = grid.get("grid_size", [8, 8])
    area = max(1, int(size[0]) * int(size[1]))
    grid_term = (
        0.35
        + _sensor_count(grid) * 0.08
        - _body_mass(grid) * 0.01 * (REFERENCE_AREA / area)
    )
    if slip_profile is not None:
        behavior = slip_profile.get("behavior", {})
        if "neediness" in behavior:
            return _clamp(
                grid_term + (_clamp(behavior["neediness"]) - 0.5) * 0.2
            )
    return _clamp(grid_term)


def _bin_index(value: float) -> int:
    for index, edge in enumerate(NEEDINESS_BIN_EDGES):
        if value <= edge:
            return index
    return len(NEEDINESS_BIN_EDGES)


def _measure(grids: list[dict], formula) -> dict:
    values = [formula(grid, None) for grid in grids]
    masses = [float(_body_mass(grid)) for grid in grids]
    sensors = [float(_sensor_count(grid)) for grid in grids]
    return {
        "grid_count": len(grids),
        "value_min": round(min(values), 6),
        "value_max": round(max(values), 6),
        "distinct_values": len({round(value, 6) for value in values}),
        "distinct_bins": len({_bin_index(value) for value in values}),
        "pearson_mass": round(pearson(values, masses), 6),
        "pearson_sensors": round(pearson(values, sensors), 6),
    }


def build_neediness_scale_report() -> dict:
    seeds_8 = build_seed_grids()
    seeds_16 = build_seed_grids_16()

    original = {
        "scale8": _measure(seeds_8, neediness_original),
        "scale16": _measure(seeds_16, neediness_original),
    }
    recalibrated = {
        "scale8": _measure(seeds_8, neediness_recalibrated),
        "scale16": _measure(seeds_16, neediness_recalibrated),
    }
    recalibrated["scale8"]["max_abs_diff_vs_original"] = round(
        max(
            abs(
                neediness_original(grid, None)
                - neediness_recalibrated(grid, None)
            )
            for grid in seeds_8
        ),
        9,
    )

    package_src = ROOT / "packages" / "mecha_engine" / "src"
    if str(package_src) not in sys.path:
        sys.path.insert(0, str(package_src))
    from extended_descriptors import _behavior_neediness  # noqa: PLC0415
    from mecha_engine.archive._metrics import (  # noqa: PLC0415
        behavior_neediness as package_neediness,
    )

    application = {
        "lab_site_matches": all(
            _behavior_neediness(grid, None)
            == neediness_recalibrated(grid, None)
            for grid in seeds_16 + seeds_8
        ),
        "package_site_matches": all(
            package_neediness(grid, None)
            == neediness_recalibrated(grid, None)
            for grid in seeds_16 + seeds_8
        ),
    }

    gates = {
        "identity_8x8": recalibrated["scale8"]["max_abs_diff_vs_original"]
        == 0.0,
        "mass_domination_reduced": abs(
            recalibrated["scale16"]["pearson_mass"]
        )
        < abs(original["scale16"]["pearson_mass"]),
        "sensor_signal_present": recalibrated["scale16"][
            "pearson_sensors"
        ]
        > 0,
    }
    decision = (
        "recalibrate" if all(gates.values()) else "remainder_stands"
    )

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete",
        "date": REPORT_DATE,
        "purpose": (
            "Measure the Phase-E named remainder — behavior_neediness "
            "mass-domination at 16x16 — and judge the reference-canvas "
            "recalibration on the engine's own numbers."
        ),
        "source_artifacts": [
            "labs/map_elites_archive/extended_descriptors.py",
            "packages/mecha_engine/src/mecha_engine/archive/_metrics.py",
            "labs/grid_genome/corpus_builder.py (both committed corpora)",
            "research/experiment_reports/2026-07-09-phase-e-gate.md",
        ],
        "formula_original": "0.35 + sensors * 0.08 - body_mass * 0.01",
        "formula_recalibrated": (
            "0.35 + sensors * 0.08 - body_mass * 0.01 * (64 / area)"
        ),
        "original": original,
        "recalibrated": recalibrated,
        "application": application,
        "gates": gates,
        "decision": decision,
        "closed_states": (
            ["neediness_mass_domination_measured_at_both_scales"]
            + (
                ["recalibration_applied_at_both_parity_sites"]
                if all(application.values())
                else []
            )
        ),
        "blocked_states": (
            []
            if all(application.values())
            and decision == "recalibrate"
            else ["recalibration_not_live_at_every_parity_site"]
        ),
        "next_research_step": (
            "the occupancy-saturation measurement (the second I5 item)"
            if decision == "recalibrate" and all(application.values())
            else "name the sharper remainder from the measured refutation"
        ),
    }


def write_neediness_scale_artifacts(
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
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "data" / "archives",
    )
    args = parser.parse_args()
    report = build_neediness_scale_report()
    written = write_neediness_scale_artifacts(args.output_dir, report)
    print(f"wrote {written}")
    print(json.dumps(report["gates"], indent=2))
    print(report["decision"])
