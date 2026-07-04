"""Deterministic semantic grid signatures.

Contract source: research/package_specs/mecha_engine_genome_contract_gate.md
("Signature Acceptance"). The signature must be deterministic, must change
when cell coordinates, cell roles, cell organs, palette id, palette colors,
grid size, or schema version change, and must ignore volatile metadata such
as notes, timestamps, or reviewer information.

The cell ordering and cell surface extend the Stage 0 research signature
(grid_genome lab helpers): cells are still ordered by (y, x, role) and carry
the animation-anchor flag, and the package signature additionally covers the
organ assignment, palette, grid size, and schema version required by the
contract gate.
"""

from __future__ import annotations

import hashlib
import json


def grid_signature(grid: dict) -> str:
    """Return a deterministic semantic signature string for a grid."""
    cells = [
        {
            "x": cell["x"],
            "y": cell["y"],
            "role": cell["role"],
            "organ": cell.get("organ"),
            "anchor": bool(cell["animation_anchor"]),
        }
        for cell in sorted(
            grid["cells"], key=lambda item: (item["y"], item["x"], item["role"])
        )
    ]
    palette = grid.get("palette")
    palette_surface = (
        {
            "palette_id": palette.get("palette_id"),
            "colors": list(palette.get("colors", [])),
        }
        if isinstance(palette, dict)
        else None
    )
    payload = {
        "schema_version": grid.get("schema_version"),
        "grid_size": list(grid.get("grid_size", [])),
        "palette": palette_surface,
        "cells": cells,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
