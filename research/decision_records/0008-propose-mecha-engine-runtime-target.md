# Decision Record 0008: Create the Mecha Engine Runtime Package Target

Date: 2026-07-05

## Status

**Accepted** (owner: "accept 0008", 2026-07-05). Authorizes creating
`packages/mecha_engine/src/mecha_engine/runtime` and promoting the
runtime surface under the same rules as the previous six modules. The
proposal history: the owner authorized making this proposal earlier the
same day ("GO: … a runtime package target proposal").

## Context

The runtime integration lab composed all six promoted modules into one
deterministic creature-lifetime loop and then into multi-generation
evolution, with every module contract holding:

- Single-generation loop: 12/12 creatures complete the full pipeline
  (`runtime_loop_composed`), SLIP-alignment retention 1.0 after the
  SLIP-aware repair guard, archive 10 niches / QD 9.29.
- Evolution loop: 4 generations × 8 creatures × 3 damage cycles — all 32
  creatures validate, survive 96 damage events with full episodes between
  regenerations, retention 1.0, archive grows to 15 niches / QD 13.92,
  archive elites genuinely reproduce (`evolution_loop_composed`).

The runtime card's go/no-go evidence gate (`slip_alignment_retention_rate
== 1.0` at full size) is satisfied. Two integration seams were found and
resolved by the lab before this proposal (the SLIP-aware guard;
profile-scoped parent selection) — the composition knowledge a runtime
surface must encode now exists as executable evidence.

## Proposed decision

Create the seventh package module target:

```txt
packages/mecha_engine/src/mecha_engine/runtime/
```

and promote a runtime surface under the same rules as the previous six
(contract tests through the package `src` surface, lab-side parity pins,
gate re-derivations, stdlib-only, no `labs` imports, no `sys.path`).

Proposed public surface (detailed in
`research/package_specs/mecha_engine_runtime_interface_spec.md`):

- `live_cycle(grid, slip_profile, repair_model, *, damage_cycles, ticks,
  dropout_rate, rng_seed) -> dict` — one creature's repeated
  damage/repair/episode cycle, deterministic, SLIP-aware repair
  throughout; carries its own private seeded damage synthesizer (the
  documented per-module factoring) while real gameplay damage events can
  be injected instead.
- `evolve(slip_profile, generation_model, repair_model, *, generations,
  population, damage_cycles, ticks, dropout_rate, rng_seed) ->
  (archive, report)` — the elites-become-parents evolution step over the
  package archive.
- Readability stays an injected input (as in `archive`); no proxy scorer
  is ported, and the uncalibrated status stays visible.

## Consequences (if accepted)

- The engine gains a single supported entry point for "run creatures" —
  the surface the future product and the mecha_workshop both build on.
- The runtime lab remains the research harness; a lab-side parity pin
  must reproduce its two artifacts' summaries through the package
  surface.
- Known follow-up carried into the spec: the lineage counter resets
  through repair reconstruction (ancestry truth is the parent-id chain);
  accumulating it is a parity-reviewed change, not part of the first
  port.

## Evidence

- `research/experiment_reports/2026-07-05-mecha-engine-runtime-loop.md`
- `research/experiment_reports/2026-07-05-mecha-engine-evolution-loop.md`
- `research/experiment_reports/2026-07-05-slip-aware-repair-guard.md`
- `data/runtime_integration/mecha_engine_runtime_loop_stage0.json`
- `data/runtime_integration/mecha_engine_evolution_loop_stage0.json`
- `research/algorithm_cards/mecha_engine_runtime_loop.md`
- `research/package_specs/mecha_engine_runtime_interface_spec.md`
- `research/decision_records/0006-create-mecha-engine-repair-target.md`
  (the promotion pattern this proposal follows)
