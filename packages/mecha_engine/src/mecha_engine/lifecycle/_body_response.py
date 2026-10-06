"""Preregistered workload-v1 body/action projection (designed game mechanic).

Identical private lab/package implementation. No covenant preferences, history,
reward or repair rules enter this projection. See cycle-38-body-workload.md.
"""
from __future__ import annotations

import math

BODY_RESPONSES = ("legacy", "workload-v1")
PLAY_REFERENCE_COST = 0.07
SLEEP_REFERENCE_RESTORE = 0.34
_WORKLOAD_FIELDS = {"occupied_mass", "functional_capacity", "capacity_floor", "play_energy_cost"}


def validate_body_response(value: object) -> str:
    if not isinstance(value, str) or value not in BODY_RESPONSES:
        raise ValueError("unsupported lifecycle body response: " + str(value))
    return value


def _finite_number(value: object) -> bool:
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def project_body_workload(grid: dict) -> dict:
    """Project actual occupied mass and intact semantic action-support cells.

    The caller validates the genome. This stricter opt-in integrity guard also
    rejects nonfinite damage without changing the incumbent genome validator.
    Coordinate sets make duplicate references and organ naming irrelevant.
    """
    occupied = {}
    for cell in grid["cells"]:
        damage = cell.get("damage", 0)
        if not _finite_number(damage) or not 0 <= damage <= 1:
            raise ValueError("workload-v1 requires finite cell damage in [0, 1]")
        if cell.get("role") != "empty" and cell.get("material") != "void":
            occupied[(cell["x"], cell["y"])] = cell
    mass = len(occupied)
    if not mass:
        raise ValueError("workload-v1 requires positive occupied mass")
    functional_points = {
        tuple(point)
        for organ in grid["organs"].values()
        if organ["role"] in {"body_core", "locomotion"}
        for point in organ["cells"]
        if tuple(point) in occupied
    }
    capacity = math.fsum(1.0 - occupied[point].get("damage", 0)
                         for point in sorted(functional_points))
    floor = max(1.0, mass * PLAY_REFERENCE_COST / SLEEP_REFERENCE_RESTORE)
    return {"occupied_mass": mass, "functional_capacity": capacity,
            "capacity_floor": floor,
            "play_energy_cost": round(PLAY_REFERENCE_COST * mass / max(capacity, floor), 6)}


def workload_for_state(state: dict) -> dict | None:
    """Validate the saved projection before any active transition.

    Loaders additionally bind this projection to the actual saved genome by
    recomputing initial_state. Arithmetic consistency alone cannot prove a
    projection belongs to a body; this function never claims that it can.
    """
    if "body_response" not in state and "body_workload" not in state:
        return None
    if state.get("body_response") != "workload-v1":
        raise ValueError("invalid saved lifecycle body response")
    workload = state.get("body_workload")
    if not isinstance(workload, dict) or set(workload) != _WORKLOAD_FIELDS:
        raise ValueError("invalid saved lifecycle body workload fields")
    mass = workload["occupied_mass"]
    capacity = workload["functional_capacity"]
    floor = workload["capacity_floor"]
    cost = workload["play_energy_cost"]
    if (type(mass) is not int or not 1 <= mass <= 64 * 64 or
            not all(_finite_number(value) for value in (capacity, floor, cost)) or
            not 0 <= capacity <= mass):
        raise ValueError("invalid saved lifecycle body workload values")
    expected_floor = max(1.0, mass * PLAY_REFERENCE_COST / SLEEP_REFERENCE_RESTORE)
    expected_cost = round(PLAY_REFERENCE_COST * mass / max(capacity, expected_floor), 6)
    if floor != expected_floor or cost != expected_cost:
        raise ValueError("saved lifecycle body workload contradicts workload-v1")
    return workload
