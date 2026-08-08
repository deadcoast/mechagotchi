"""Bounded lifecycle simulation contract surface for mecha_engine.

Promoted third, in the contract traceability matrix's fixed order
(research/package_specs/mecha_engine_contract_traceability_matrix.md).
Public surface per
research/package_specs/mecha_engine_lifecycle_contract_gate.md:

- ``initial_state(grid, slip_profile=None) -> dict``
- ``advance_tick(state, action, deliberation=None) -> dict``
- ``run_episode(grid, slip_profile=None, policy=None, actions=None, ticks=72, rng_seed=None) -> dict``
- ``reward_for_transition(previous_state, next_state, action) -> float``
- ``choose_action_detailed(policy, state, rng) -> (action, record | None)``
  (F1's seam, exported for W1's living companion: interactive callers
  drive ``advance_tick`` with the switchboard's own choices and see the
  deliberation record — no new engine number, the F1 surface made
  public)
- ``ACTIONS`` — the action vocabulary (feed/play/sleep/idle/mutate);
  a player's buttons ARE these actions.
- ``DANGER_THRESHOLDS`` — the per-axis boundaries at which a companion
  is in trouble (cycle 25 O1). Promoted so a consumer can ask *how close
  to trouble is this creature* without reaching past ``__all__`` into a
  submodule: decision record 0054 adopted ``danger_margin`` — the
  minimum normalised safety margin across these thresholds — as the
  CHOSEN definition of the documented VISIBLE axis ``health``, and a
  definition built on an unpromised surface is a definition that can
  break without notice. **The constant is promoted; the margin formula
  is NOT** — whether that belongs in the engine is its own decision, and
  a package test pins that neither ``danger_margin`` nor ``health``
  appears on this surface. **These are DANGER thresholds, not lethal
  ones**: ``bond`` has a threshold and is not a death condition, which
  is why decision record 0054 renamed its own candidate away from
  "lethal".

Invalid grids are rejected through ``mecha_engine.genome.validate_grid``
before any simulation state exists, continuous state stays clamped in
``[0, 1]``, death causes are explicit, and episodes are deterministic per
RNG seed. Online reward shaping, contextual-bandit learner memory, and
feedback learners stay lab-only per the contract gate: this module ships
only the frozen switchboard policy needed to reproduce the pinned Stage 0
comparator. The implementation is self-contained package code (stdlib only,
no research lab imports) and performs no Stage 0 artifact writes on import.
"""

from ._policy import ACTIONS, choose_action_detailed
from .simulate import (
    DANGER_THRESHOLDS,
    advance_tick,
    initial_state,
    reward_for_transition,
    run_episode,
)

__all__ = [
    "ACTIONS",
    "DANGER_THRESHOLDS",
    "advance_tick",
    "choose_action_detailed",
    "initial_state",
    "reward_for_transition",
    "run_episode",
]
