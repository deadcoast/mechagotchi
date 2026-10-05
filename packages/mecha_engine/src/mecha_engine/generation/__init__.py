"""Constrained candidate-generation contract surface for mecha_engine.

Promoted second, in the contract traceability matrix's fixed order
(research/package_specs/mecha_engine_contract_traceability_matrix.md).
Public surface per
research/package_specs/mecha_engine_generation_contract_gate.md:

- ``train_generation_model(seed_grids) -> GenerationModel``
- ``generate_candidate(parent_grid, model, slip_profile=None, rng_seed=None) -> dict``
- ``generate_batch(seed_grids, count, slip_profile=None, rng_seed=None) -> list[dict]``
- ``explain_generation(candidate) -> dict``

WFC surface (cycle 10 B3, DR 0031 — the bake-off winner, the
rich-alphabet generator, optional since DR0042; an additive seam, the constrained
stabilizer above is untouched):

- ``train_wfc_model(train_grids) -> dict``
- ``generate_wfc_grid(model, *, grid_id, rng_seed, max_restarts=8, trace=None) -> dict``
- ``build_wfc_corpus(model, *, count, rng_seed) -> list[dict]``

W4 adds optional detached observational trace events to WFC; outputs, RNG
consumption and failures are unchanged. DR0042 keeps constrained generation
as the evolution default. WFC remains a distinct additive arm.

Raw Markov-style local adjacency statistics are a proposal source only; the
production paths are validator-gated constrained stabilization and the
constraint-finished WFC collapse — no raw Markov generator is exposed. The
implementation is self-contained package code (stdlib only, no research lab
imports) and performs no Stage 0 artifact writes on import.
"""

from .explain import explain_generation
from .generate import generate_batch, generate_candidate
from .model import GenerationModel, train_generation_model
from .wfc import build_wfc_corpus, generate_wfc_grid, train_wfc_model

__all__ = [
    "GenerationModel",
    "build_wfc_corpus",
    "explain_generation",
    "generate_batch",
    "generate_candidate",
    "generate_wfc_grid",
    "train_generation_model",
    "train_wfc_model",
]
