"""Renderer-neutral render packets built from validated grids.

Contract source: research/package_specs/mecha_engine_genome_contract_gate.md
("Render Packet Acceptance"). The packet is a JSON-serializable data
boundary with at least ``grid_id``, ``grid_size``, ``palette``, ``cells``,
and ``state``. It must fail for grids that do not pass ``validate_grid`` and
it must not own frontend rendering, animation playback, or UI layout.
"""

from __future__ import annotations

from copy import deepcopy

from .validation import validate_grid


def render_packet_from_grid(grid: dict, state: dict | None = None) -> dict:
    """Build a JSON-serializable renderer-neutral packet from a valid grid.

    Raises ``ValueError`` when ``grid`` does not pass ``validate_grid``.
    Neither ``grid`` nor ``state`` is mutated; the packet holds deep copies
    so callers cannot alias engine inputs through the render boundary.
    """
    result = validate_grid(grid)
    if not result.ok:
        raise ValueError(
            "render packet requires a valid grid; validation errors: "
            + "; ".join(result.errors)
        )
    return {
        "grid_id": grid["grid_id"],
        "grid_size": deepcopy(grid["grid_size"]),
        "palette": deepcopy(grid["palette"]),
        "cells": deepcopy(grid["cells"]),
        "state": deepcopy(state) if state is not None else None,
    }
