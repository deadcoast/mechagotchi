"""MAP-Elites archive contract surface for mecha_engine.

Promoted fourth, in the contract traceability matrix's fixed order
(research/package_specs/mecha_engine_contract_traceability_matrix.md).
Public surface per
research/package_specs/mecha_engine_archive_contract_gate.md:

- ``descriptor_for_candidate(candidate, metrics) -> tuple[int, ...]``
- ``score_candidate(candidate, metrics) -> dict``
- ``insert_candidate(archive, candidate, score, descriptor) -> dict``
- ``build_archive(candidates, metrics_by_grid_id) -> dict``
- ``archive_summary(archive) -> dict``

The archive preserves diverse high-performing companion families by
behavior-descriptor niche: baseline 3D (body mass, sensor count, symmetry)
and calibrated extended 7D descriptors, deterministic integer tuples, the
strictly-higher-fitness elite replacement rule with incumbent-keeping tie
handling, and coverage/QD summary metrics with per-axis observed bin
spread. Scalar top-k selection remains a comparator only — no ranked
top-k surface exists in this module. Candidate grids are validated
through ``mecha_engine.genome.validate_grid`` before insertion, and
survival descriptors run through ``mecha_engine.lifecycle`` episodes on
the calibrated morphology-derived stress probe when the metrics bundle
carries no precomputed lifecycle summary.

Documented factoring: readability, lifecycle summaries, SLIP alignment
results, and mutation caps are archive *inputs* per the interface spec
(the per-candidate ``metrics`` bundle); no proxy-readability scorer is
ported into the package, proxy scores stay marked as uncalibrated, and
final descriptor thresholds remain unlocked until manual readability
ratings are collected. The implementation is self-contained package code
(stdlib plus promoted mecha_engine modules, no research lab imports) and
performs no Stage 0 artifact writes on import.
"""

from ._metrics import lifecycle_probe_grid
from .descriptors import descriptor_for_candidate
from .scoring import score_candidate
from .store import archive_summary, build_archive, insert_candidate

__all__ = [
    "archive_summary",
    "build_archive",
    "descriptor_for_candidate",
    "insert_candidate",
    "lifecycle_probe_grid",
    "score_candidate",
]
