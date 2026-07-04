"""Grid genome contract surface for mecha_engine.

Promoted first per the contract traceability matrix
(research/package_specs/mecha_engine_contract_traceability_matrix.md).
Public surface per research/package_specs/mecha_engine_genome_contract_gate.md:

- ``ValidationResult(ok, errors, warnings)``
- ``validate_grid(grid) -> ValidationResult``
- ``validate_grid_file(path) -> ValidationResult``
- ``grid_signature(grid) -> str``
- ``render_packet_from_grid(grid, state=None) -> dict``

The implementation is self-contained package code (stdlib only, no research
lab imports) and performs no Stage 0 artifact writes on import.
"""

from .render import render_packet_from_grid
from .signature import grid_signature
from .validation import (
    BODY_CORE_MIN_CELLS,
    GRID_SIZE_MAX,
    GRID_SIZE_MIN,
    REQUIRED_TOP_LEVEL_FIELDS,
    SCHEMA_VERSION,
    ValidationResult,
    validate_grid,
    validate_grid_file,
)

__all__ = [
    "BODY_CORE_MIN_CELLS",
    "GRID_SIZE_MAX",
    "GRID_SIZE_MIN",
    "REQUIRED_TOP_LEVEL_FIELDS",
    "SCHEMA_VERSION",
    "ValidationResult",
    "grid_signature",
    "render_packet_from_grid",
    "validate_grid",
    "validate_grid_file",
]
