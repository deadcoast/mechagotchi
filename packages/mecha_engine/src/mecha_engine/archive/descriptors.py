"""Behavior-descriptor computation for the mecha_engine archive.

Contract sources:

- research/package_specs/mecha_engine_archive_contract_gate.md
  ("Descriptor Acceptance")
- research/package_specs/mecha_engine_module_interfaces.md ("archive")

Two descriptor modes are supported, both returning deterministic integer
tuples:

- ``baseline`` — the 3D descriptor option (body mass, sensor count,
  symmetry);
- ``extended`` — the calibrated 7D Stage 0 descriptor (adds readability,
  lifecycle survival, mutation stability, and behavior neediness).

PROVISIONAL THRESHOLDS: every bin edge below is the calibrated Stage 0
proxy value and remains explicitly *unlocked*. Manual readability ratings
must be incorporated before final descriptor thresholds are locked
(archive contract gate, "Descriptor Acceptance"); until then archives and
summaries carry ``final_descriptor_thresholds_locked: False`` and the
proxy readability calibration status.
"""

from __future__ import annotations

from . import _metrics

BASELINE_MODE = "baseline"
EXTENDED_MODE = "extended"

EXTENDED_DESCRIPTOR_NAMES: list[str] = [
    "body_mass",
    "sensor_count",
    "symmetry",
    "readability",
    "lifecycle_survival",
    "mutation_stability",
    "behavior_neediness",
]

BASELINE_DESCRIPTOR_NAMES: list[str] = EXTENDED_DESCRIPTOR_NAMES[:3]

# Calibrated Stage 0 bin edges (provisional until manual readability
# ratings exist; see module docstring). ``_bin`` maps value <= edge[i] to
# bin i, values above the last edge to the final bin.
BIN_THRESHOLDS: dict[str, list[float]] = {
    "body_mass": [6, 9, 12, 16],
    "sensor_count": [1, 2, 3, 4],
    "symmetry": [0.25, 0.5, 0.75, 0.9],
    "readability": [0.35, 0.55, 0.7, 0.85],
    "lifecycle_survival": [0.2, 0.4, 0.6, 0.8],
    "mutation_stability": [0.3, 0.5, 0.7, 0.9],
    "behavior_neediness": [0.2, 0.4, 0.6, 0.8],
}

FINAL_DESCRIPTOR_THRESHOLDS_LOCKED = False
READABILITY_CALIBRATION_STATUS = "proxy_only_manual_ratings_not_collected"

# DR 0029/0030 pattern (cycle 09 A4): the body-mass bin edges are cell
# counts denominated at the 8x8 reference canvas and scale by area —
# an exact identity at 8x8, [24, 36, 48, 64] at the ratified 16x16 —
# so the mass axis keeps discriminating instead of collapsing into the
# top bin at scale. Every other axis is dimensionless or discrete and
# keeps its calibrated edges.
MASS_REFERENCE_AREA = 64


def grid_area_of(grid: dict) -> int:
    """The candidate's canvas area; malformed sizes read as the reference."""
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
        return grid_size[0] * grid_size[1]
    return MASS_REFERENCE_AREA


def mass_bin_thresholds(grid_area: int = MASS_REFERENCE_AREA) -> list[float]:
    if grid_area == MASS_REFERENCE_AREA:
        return BIN_THRESHOLDS["body_mass"]
    return [
        edge * grid_area // MASS_REFERENCE_AREA
        for edge in BIN_THRESHOLDS["body_mass"]
    ]

_MODES: dict[str, list[str]] = {
    BASELINE_MODE: BASELINE_DESCRIPTOR_NAMES,
    EXTENDED_MODE: EXTENDED_DESCRIPTOR_NAMES,
}


def descriptor_names(mode: str) -> list[str]:
    if mode not in _MODES:
        raise ValueError(f"unsupported descriptor mode: {mode}")
    return list(_MODES[mode])


def descriptor_cardinalities(mode: str) -> list[int]:
    return [len(BIN_THRESHOLDS[name]) + 1 for name in descriptor_names(mode)]


def total_possible_niches(mode: str) -> int:
    total = 1
    for cardinality in descriptor_cardinalities(mode):
        total *= cardinality
    return total


def descriptor_key(descriptor: tuple[int, ...]) -> str:
    return ",".join(str(value) for value in descriptor)


def descriptor_for_candidate(
    candidate: dict, metrics: dict, *, mode: str = EXTENDED_MODE
) -> tuple[int, ...]:
    """Return the deterministic integer descriptor tuple for a candidate.

    ``baseline`` mode needs only the candidate grid morphology; ``extended``
    mode additionally consumes the readability, lifecycle, SLIP-alignment,
    and mutation-cap context from the ``metrics`` bundle, rejecting missing
    metric inputs with explicit errors. Neither input is mutated.
    """
    if mode not in _MODES:
        raise ValueError(f"unsupported descriptor mode: {mode}")
    grid = _metrics.require_candidate(candidate)
    if mode == BASELINE_MODE:
        _metrics.require_metrics(metrics)
        values = {
            "body_mass": _metrics.body_mass(grid),
            "sensor_count": _metrics.sensor_count(grid),
            "symmetry": _metrics.symmetry_score(grid),
        }
    else:
        resolved = _metrics.resolve_candidate_metrics(candidate, metrics)
        values = descriptor_axis_values(resolved)
    return descriptor_from_axis_values(values, mode, grid_area=grid_area_of(grid))


def descriptor_axis_values(resolved: dict) -> dict:
    """Raw (unbinned) extended axis values from a resolved metric bundle."""
    return {
        "body_mass": resolved["body_mass"],
        "sensor_count": resolved["sensor_count"],
        "symmetry": resolved["symmetry"],
        "readability": resolved["readability_value"],
        "lifecycle_survival": resolved["lifecycle"]["survival_ratio"],
        "mutation_stability": resolved["mutation_stability"],
        "behavior_neediness": resolved["behavior_neediness"],
    }


def descriptor_from_axis_values(
    values: dict, mode: str, *, grid_area: int = MASS_REFERENCE_AREA
) -> tuple[int, ...]:
    return tuple(
        _bin(
            values[name],
            mass_bin_thresholds(grid_area)
            if name == "body_mass"
            else BIN_THRESHOLDS[name],
        )
        for name in descriptor_names(mode)
    )


def descriptor_metrics(resolved: dict) -> dict:
    """Rounded per-axis metric values for elite/audit records."""
    return {
        "body_mass": resolved["body_mass"],
        "sensor_count": resolved["sensor_count"],
        "symmetry": round(resolved["symmetry"], 6),
        "readability": resolved["readability_value"],
        "lifecycle_survival": resolved["lifecycle"]["survival_ratio"],
        "mutation_stability": round(resolved["mutation_stability"], 6),
        "behavior_neediness": round(resolved["behavior_neediness"], 6),
    }


def check_descriptor(descriptor: object, mode: str) -> tuple[int, ...]:
    """Validate a caller-supplied descriptor against the mode's geometry."""
    cardinalities = descriptor_cardinalities(mode)
    if not isinstance(descriptor, tuple | list) or len(descriptor) != len(cardinalities):
        raise ValueError(
            f"descriptor must be a tuple of {len(cardinalities)} integers "
            f"for mode {mode}: {descriptor!r}"
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


def _bin(value: float, thresholds: list[float]) -> int:
    for index, threshold in enumerate(thresholds):
        if value <= threshold:
            return index
    return len(thresholds)
