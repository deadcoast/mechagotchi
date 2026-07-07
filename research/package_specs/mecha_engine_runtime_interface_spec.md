# Mecha Engine Runtime Module Interface Spec

Date: 2026-07-05

## Status

Contract reference for `mecha_engine.runtime` (decision record 0008,
**accepted 2026-07-05**). Evidence basis: the runtime integration lab's
two composed-loop artifacts, both green (`runtime_loop_composed`,
`evolution_loop_composed`).

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
- `evolve(seed_grids, slip_profile, generation_model, repair_model, *,
  readability_scorer, generations=4, population=8, damage_cycles=3,
  ticks=72, dropout_rate=0.2, rng_seed=20260512) -> (archive, report)`
  Generation 0 parents from the profile-aligned subset of `seed_grids`;
  later parents from archive elites sorted by niche key; every creature
  goes through the live-cycle semantics, then scores and inserts through
  `mecha_engine.archive`. Readability is injected via
  `readability_scorer` (a deterministic callable, the "equivalent
  metrics hook" — no proxy scorer is ported; the record's
  manual-rating status stays visible in every score). Signature
  amendment vs the proposal draft, documented here: `seed_grids` and the
  callable form of the readability hook are required for the evolution
  semantics to be reproducible.

## Hard gates for the port

- Lab-parity pin: reproduce the evolution-loop artifact through the
  package surface over the same seeds — summary equal (32/32, 96 damage
  events, retention 1.0, 15 niches, QD 13.92, fitness-by-generation list
  equal) and per-creature cycle records equal, with the lab's proxy
  readability injected as the scorer. (Amendment vs the proposal draft:
  the single-generation artifact keeps the lab as its harness — its
  pre/post-episode shape is the integration record, not a runtime
  surface — the evolution artifact subsumes the composition claim.)
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

## founder_grids (decision record 0016, 2026-07-06)

`evolve` accepts keyword-only `founder_grids: list[dict] | None =
None`: released creatures admitted through the engine's own gates
(validate_grid + SLIP alignment, rejections verbatim in the report's
`founders` block); admitted founders LEAD the generation-0 pool
(`parent_source: founders_plus_seed_pool`). `None` is byte-identical
to the pre-0016 contract (parity pins unmodified).
