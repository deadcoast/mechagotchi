"""Grid genome contract surface for mecha_engine.

Promoted first per the contract traceability matrix
(research/package_specs/mecha_engine_contract_traceability_matrix.md).
Public surface per research/package_specs/mecha_engine_genome_contract_gate.md:

- ``ValidationResult(ok, errors, warnings)``
- ``validate_grid(grid) -> ValidationResult``
- ``validate_grid_file(path) -> ValidationResult``
- ``grid_signature(grid) -> str``
- ``render_packet_from_grid(grid, state=None) -> dict``

Additive publics per decision record 0013 (T4/T16 lab semantics, verbatim;
``render_packet_from_grid`` stays exactly v1):

- ``ANIMATION_STATES`` — the og five-state vocabulary
- ``project_animation_state(grid, state) -> dict`` — deterministic,
  visual-only genome projection (idle is the identity)
- ``render_packet_v2(grid, lifecycle_state=None, *, animation=None) ->
  dict`` — the v1 packet plus ``animation``/``mood``/
  ``animation_vocabulary``, cells carrying the selected state's projection

The implementation is self-contained package code (stdlib only, no research
lab imports) and performs no Stage 0 artifact writes on import.
"""

from .animation import (
    ANIMATION_STATES,
    CLIP_STATES,
    clip_frame,
    clip_frame_count,
    clip_names,
    project_animation_state,
    render_packet_v2,
)
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
    "ANIMATION_STATES",
    "BODY_CORE_MIN_CELLS",
    "CLIP_STATES",
    "clip_frame",
    "clip_frame_count",
    "clip_names",
    "GRID_SIZE_MAX",
    "GRID_SIZE_MIN",
    "REQUIRED_TOP_LEVEL_FIELDS",
    "SCHEMA_VERSION",
    "ValidationResult",
    "grid_signature",
    "project_animation_state",
    "render_packet_from_grid",
    "render_packet_v2",
    "validate_grid",
    "validate_grid_file",
]
