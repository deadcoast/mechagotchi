# Decision Record 0024: og Starter Grid Schema — Animation/Species Disposition (R7)

Date: 2026-07-07

## Status

**Accepted** (DR 0017 R7 = cycle-01 T7, carried; the task's own terms:
"implement per the og starter schema, or record the T4 projection
design as the superseding decision — either way, developed then
marked"). This record is the superseding decision: every animation and
species field the og starter grid schema proposed now traces to a
shipped mechanism or to an explicit rejection with a revival condition.
It also closes DR 0011 verdict #5's queue pointer (grid-side
`species_class`, "lands with the taxonomy work" — resolved below).

## The og starter grid schema, field by field

The og proposal (`docs/project-research/deep-research/01/
deep-research.md`, "proposed starter schemas, not final standards")
carried these animation/species-relevant surfaces on the GRID:

| og field | Disposition | Where it lives now |
| --- | --- | --- |
| per-cell `animation_anchor` | **SHIPPED verbatim** | `research/grid_genome/grid_genome.schema.json` (required per cell; hard invariant "required animation anchor" enforced by the validator) |
| animation states / clips stored on the creature | **SUPERSEDED by the T4 projection design** | animation states are deterministic visual-only GENOME PROJECTIONS (`labs/grid_genome/animation_states.py`, 300/300 valid — `animstate_300`); the render packet v2 selects a state at render time (T16 `animation` selection); the species' vocabulary is covenant-side (`visual_grammar.animation_vocab`, T3.5) |
| `species_class` on the grid | **REJECTED-until-consumer** (this record) | species taxonomy is COVENANT-side: SLIP `species_class` (T3.5), consumed by evolution identity — the species is the covenant, the grid is an individual |
| `symmetry {mode, bias}` on the grid | superseded | symmetry is a measured morphology metric (archive descriptors/stress probe), not stored state; SLIP caps `symmetry_break_rate_max` |
| `invariants {...}` inline on the grid | superseded | the numbered hard/soft invariants live in `research/grid_genome/grid_invariants.md`, enforced by the validator — invariants are the ecosystem's law, not per-creature declarations |
| `value` byte channel, `material: sensor/shell` naming, 16x16 size | already decided |