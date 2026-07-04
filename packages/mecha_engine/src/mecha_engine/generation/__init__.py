"""Constrained candidate-generation contract surface for mecha_engine.

Promoted second, in the contract traceability matrix's fixed order
(research/package_specs/mecha_engine_contract_traceability_matrix.md).
Public surface per
research/package_specs/mecha_engine_generation_contract_gate.md:

- ``train_generation_model(seed_grids) -> GenerationModel``
- ``generate_candidate(parent_grid, model, slip_profile=None, rng_seed=None) -> dict``
- ``generate_batch(seed_grids, count, slip_profile=None, rng_seed=None) -> list[dict]``
- ``explain_generation(candidate) -> dict``

Raw Markov-style local adjacency statistics are a proposal source only; the
sole production path is validator-gated constrained stabilization through
``mecha_engine.genome.validate_grid`` (plus SLIP alignment when a profile is
supplied), so no raw Markov generator is exposed. The implementation is
self-contained package code (stdlib only, no research lab imports) and
performs no Stage 0 artifact writes on import.
"""

from .explain import explain_generation
from .generate import generate_batch, generate_candidate
from .model import GenerationModel, train_generation_model

__all__ = [
    "GenerationModel",
    "explain_generation",
    "generate_batch",
    "generate_candidate",
    "train_generation_model",
]
