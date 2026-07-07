# Decision Record 0024: Grid-Schema Animation/Species Fields (R7) — Projections and Covenant Identity Supersede Stored Fields

Date: 2026-07-07

## Status

**Accepted** (DR 0017 R7 = cycle-01 T7, carried; DR 0011 verdict #5's
T7 half). The og starter grid schema proposed grid-level animation and
species surfaces; this record resolves both against what actually
shipped, closing R7 by its own terms ("implement per the og starter
schema, or record the T4 projection design as the superseding decision").

## Decision 1 — Animation: the T4 projection design SUPERSEDES stored fields

No animation-state fields enter the grid schema. The og intent is fully
delivered by shipped surfaces, without storing a single frame:

- Per-cell `animation_anchor` — ALREADY in the shipped schema, exactly
  as the og starter schema itself carried it (the og's only grid-side
  animation surface; its `invariants.requires_animation_anchor` is the
  shipped hard invariant).
- Animation STATES are deterministic genome projections (T4,
  `animstate_300`: 300/300 valid across idle/blink/sleep/beg/ill) —
  derived, never stored, so they can never drift from the body.
- State SELECTION rides render packet v2 (T16), which is where the og
  starter schema put animation in the first place (its `animation`
  block lives on the render-packet artefact, not the grid).
- The species' animation VOCABULARY is the covenant's
  `visual_grammar.animation_vocab` (T3.5), packet-consumed with the
  honest-mood fallback.

Storing per-state frames or state fields on the grid would duplicate
state the projections derive — the anti-drift rule rejects it.

## Decision 2 — Species: covenant identity; the grid-level field is REJECTED (with a re-opener)

`species_class` lives in the SLIP (T3.5): validated as a lowercase
identifier across all four lab/package `_slip` mirrors, consumed by the
evolution loop's report identity, and enforced on grids CONTEXTUALLY
through the species' `visual_grammar` alignment. Species is the
covenant's identity — "the Keeper's covenant with their species is the
SLIP profile" (DR 0021) — and every shipped consumer reads it with the
covenant in hand: evolution reports carry it, campaign records persist
the full profile per era (DR 0022's `slip_profiles` table), and grid
ancestry is the `lineage` chain.

A grid-level `species_class` copy would today be a decorative
duplicate: no consumer reads species FROM the grid, and the shipped
rule — every field is enforced or consumed, never decorative — rejects
it exactly as DR 0011 rejected the og `value` byte channel.

**Designated re-opener**: mixed-species soups — the moment one era runs
creatures under MULTIPLE covenants, per-creature species becomes
load-bearing without covenant context, and a grid-level (or
archive-record-level) species tag earns its consumer. That decision
cites this record plus the game-loop task that introduces
multi-covenant eras.

## Consequences

- R7 is closed by resolution: og animation intent shipped as
  projections + packet selection + covenant vocabulary; og species
  intent shipped as covenant identity; neither adds grid fields.
- DR 0011 verdict #5 ("species_class required in SLIP + grid — WATCH →
  queued T3.5/T7") is now fully resolved: SLIP half ADOPTED (T3.5),
  grid half REJECTED with the re-opener above.
- The grid schema stays minimal: bodies are bodies; identity and
  display live where their consumers are.

## Sources

- `docs/project-research/deep-research/01/deep-research.md` (the og starter schemas: grid `species_class`, packet-side `animation` block)
- `audits/complete/01/audit-devspec.md` (the T7 finding)
- `research/decision_records/0011-run-one-run-two-reconciliation.md` (verdict #5; the decorative-field doctrine)
- `research/experiment_reports/2026-07-05-slip-ladder-species-grammar.md` (T3.5: species_class + visual_grammar)
- `data/grid_genome/animstate_300.json` + `research/algorithm_cards/animation_states.md` (T4: the projection design)
- `research/grid_genome/grid_genome.schema.json` (`animation_anchor`, the shipped grid-side surface)
- `research/decision_records/0021-game-loop.md` (the covenant as species identity)
- `research/decision_records/0022-storage-module.md` (per-era profile persistence)
