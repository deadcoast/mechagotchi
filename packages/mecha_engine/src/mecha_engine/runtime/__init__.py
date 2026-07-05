"""Runtime contract surface for mecha_engine — the composed engine's entry point.

Promoted seventh, per decision record 0008
(research/decision_records/0008-propose-mecha-engine-runtime-target.md,
accepted 2026-07-05). Public surface per
research/package_specs/mecha_engine_runtime_interface_spec.md:

- ``live_cycle(grid, slip_profile, repair_model, *, damage_cycles=3,
  ticks=72, dropout_rate=0.2, rng_seed=20260512, damage_events=None) ->
  dict`` — one creature's life under fire: per cycle a seeded damage event
  (private synthesizer, ``removed_cells`` reported per the repair
  observability contract), SLIP-aware wound-site repair, per-cycle grid-id
  reassignment, and a full lifecycle episode. Injected damage events (a
  future gameplay source) replace the synthesizer via ``damage_events``
  without changing cycle semantics; a zero-cell event is a no-op repair.
- ``evolve(seed_grids, slip_profile, generation_model, repair_model, *,
  readability_scorer, generations=4, population=8, damage_cycles=3,
  ticks=72, dropout_rate=0.2, rng_seed=20260512) -> (archive, report)`` —
  generation 0 parents from the profile-aligned subset of ``seed_grids``,
  later parents from archive elites sorted by niche key; every creature
  lives through the live-cycle semantics, then scores and inserts through
  ``mecha_engine.archive``.

This module serves the composed engine: it is the single supported entry
point over the promoted ``mecha_engine.genome``, ``generation``,
``lifecycle``, ``archive``, and ``repair`` public surfaces (only public
cross-module imports; no other module's private files), encoding the
runtime integration lab's five lessons — SLIP-aware repair, profile-scoped
parent selection, per-cycle grid-id reassignment, legal zero-cell no-op
repairs, and readability as an injected, visibly uncalibrated input (no
proxy scorer is ported; manual-rating status stays visible in every
score). The repair observability and no-template contracts pass through
unchanged (``target_template_used == false`` everywhere). Known non-goal
for this first port: lineage-counter accumulation through repair
(ancestry truth is the parent-id chain). The runtime returns data, not
frames. The implementation is self-contained package code (stdlib plus
promoted mecha_engine modules, no research lab imports) and performs no
Stage 0 artifact writes on import.
"""

from .evolve import evolve
from .live import live_cycle

__all__ = [
    "evolve",
    "live_cycle",
]
