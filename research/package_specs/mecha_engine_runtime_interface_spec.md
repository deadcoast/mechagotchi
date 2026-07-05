# Mecha Engine Runtime Module Interface Spec

Date: 2026-07-05

## Status

Research interface specification for a proposed `mecha_engine.runtime`
module (decision record 0008, **awaiting owner acceptance** — this
document designs the surface; it does not create the target). Evidence
basis: the runtime integration lab's two composed-loop artifacts, both
green (`runtime_loop_composed`, `evolution_loop_composed`).

## Why a runtime surface

Six modules are promoted and proven to compose, but composition knowledge
currently lives only in a research lab. A runtime module gives the engine
one supported entry point — the surface the future product (and the
mecha_workshop tooling) builds on — encoding the integration lessons the
lab discovered executable-first:

1. Repair must run SLIP-aware (the alignment seam).
2. Parents are selected from the profile-aligned pool (generation rejects
   profile-incompatible parents).
3. Grid ids are reassigned per damage/repair cycle (64-char cap).
4. A stochastic damage event may destroy zero cells (no-op repair is
   legal).
5. Readability is an injected, visibly-uncalibrated input.

## Proposed public surface

- `live_cycle(grid, slip_profile, repair_model, *, damage_cycles=3,
  ticks=72, dropout_rate=0.2, rng_seed=20260512) -> dict`
  One creature's life under fire: per cycle, a seeded damage event
  (private synthesizer, `removed_cells` reported per the repair
  observability contract), SLIP-aware wound-site repair, and a full
  lifecycle episode. Returns per-cycle digests (removed cells,
  restoration fidelity, guard substitutions, validity, alignment,
  episode) plus a final-state digest. Deterministic; inputs never
  mutated. Injected damage events (a future gameplay source) replace the
  synthesizer via an optional `damage_events` parameter without changing
  cycle semantics.
- `evolve(slip_profile, generation_model, repair_model, *,
  generations=4, population=8, damage_cycles=3, ticks=72,
  dropout_rate=0.2, rng_seed=20260512, readability_by_grid_id) ->
  (archive, report)`
  Generation 0 parents from the profile-aligned inputs; later parents
  from archive elites sorted by niche key; every creature goes through
  `live_cycle`, then scores and inserts through `mecha_engine.archive`.
  Readability values are injected (`readability_by_grid_id` or an
  equivalent metrics hook) — no proxy scorer is ported.

## Hard gates for the port (if DR 0008 is accepted)

- Lab-parity pin: reproduce both runtime-lab artifact summaries through
  the package surface over the same seeds — single loop
  (12/12, retention 1.0, 10 niches, QD 9.29) and evolution
  (32/32, 96 damage events, retention 1.0, 15 niches, QD 13.92,
  fitness-by-generation list equal).
- Deterministic end to end; JSON-serializable reports; no input
  mutation.
- Stdlib-only; imports only `mecha_engine.*`; no `labs`, no `sys.path`
  (boundary scan).
- The observability and no-template contracts of `repair` pass through
  unchanged; `target_template_used == false` everywhere.
- Zero-cell damage events are handled as no-op repairs (measured lab
  behavior).
- Known non-goal for the first port: lineage-counter accumulation
  through repair (parity-reviewed follow-up; ancestry truth is the
  parent-id chain).

## Non-goals

- No gameplay/UI; the runtime returns data, not frames.
- No readability scorer; no calibration claims (owner-deferred data).
- No new learning surfaces (the `learning` module remains its own
  roadmap item with its own decision record).

## Sources

- `research/decision_records/0008-propose-mecha-engine-runtime-target.md`
- `labs/runtime_integration/mecha_engine_runtime_loop.py`
- `data/runtime_integration/mecha_engine_runtime_loop_stage0.json`
- `data/runtime_integration/mecha_engine_evolution_loop_stage0.json`
- `research/experiment_reports/2026-07-05-mecha-engine-runtime-loop.md`
- `research/experiment_reports/2026-07-05-mecha-engine-evolution-loop.md`
- `research/package_specs/mecha_engine_module_interfaces.md`
- `research/package_specs/mecha_engine_repair_interface_spec.md`
