"""Bounded lifecycle simulation contract surface for mecha_engine.

Promoted third, in the contract traceability matrix's fixed order
(research/package_specs/mecha_engine_contract_traceability_matrix.md).
Public surface per
research/package_specs/mecha_engine_lifecycle_contract_gate.md:

- ``initial_state(grid, slip_profile=None) -> dict``
- ``advance_tick(state, action) -> dict``
- ``run_episode(grid, slip_profile=None, policy=None, actions=None, ticks=72, rng_seed=None) -> dict``
- ``reward_for_transition(previous_state, next_state, action) -> float``

Invalid grids are rejected through ``mecha_engine.genome.validate_grid``
before any simulation state exists, continuous state stays clamped in
``[0, 1]``, death causes are explicit, and episodes are deterministic per
RNG seed. Online reward shaping, contextual-bandit learner memory, and
feedback learners stay lab-only per the contract gate: this module ships
only the frozen switchboard policy needed to reproduce the pinned Stage 0
comparator. The implementation is self-contained package code (stdlib only,
no research lab imports) and performs no Stage 0 artifact writes on import.
"""

from .simulate import advance_tick, initial_state, reward_for_transition, run_episode

__all__ = [
    "advance_tick",
    "initial_state",
    "reward_for_transition",
    "run_episode",
]
