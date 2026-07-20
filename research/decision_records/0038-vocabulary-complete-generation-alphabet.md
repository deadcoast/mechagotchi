# Decision Record 0038: The Vocabulary-Complete Generation Alphabet

Date: 2026-07-20

## Status

**Accepted — implementation pending** (cycle 20 · Phase J, task J2's
second half). This record charters the gated change; the
implementation lands as its own commit(s) judged by the gates below.
Until then the alphabet stays as-is and the measured blindness stands
recorded.

## Context

The J2 measurement (`2026-07-20-role-emission.md`,
`data/grid_genome/role_emission_stage0.json`) found the constrained
generation path — including the PROMOTED `generate_batch`, the exact
surface the game's evolution breeds offspring through — emitting the
DR 0011/0015 motion trio at **exactly 0.0** while its own training
corpus carries it at 0.48. The mechanism: every grid is projected
through the 5-token matrix alphabet
(`TOKENS = [".", "B", "A", "E", "M"]`), and `_matrix_from_grid` maps
ONLY body/eye/mouth — **seven ratified roles (shell, sensor, antenna,
limb, joint, decoration, effect) are erased in projection** and can
never be reconstructed. The alphabet predates DR 0011's vocabulary
ratification and DR 0015's coverage ruling; the generator simply was
never taught the words.

The consequences are measured, not hypothetical: the I5b coverage
ceiling (the generators' descriptor range), the J1 probe's structured
emptiness (95 bins concentrated at the octile corners), the I4
exemplar's isolation, and evolved populations without legs — the game
cannot breed what the breeding surface cannot spell.

## Decision

Extend the generation alphabet to the RATIFIED vocabulary at both
parity sites (the lab constrained generator + `mecha_engine.generation`),
as one gated change:

1. **Projection**: `_matrix_from_grid` maps every schema cell role to
   a distinct token (the DR 0011 vocabulary, one token per role;
   anchor-bearing body keeps its distinct token).
2. **Statistics**: the adjacency model trains over the full alphabet
   (same counting machinery, wider token set).
3. **Reconstruction**: `grid_from_matrix` synthesizes VALIDATOR-LEGAL
   structure for the new tokens — organ membership per role
   (limbs/joints into locomotion organs, decoration into ornament,
   effect into aura, antenna/sensor into their sensor organs),
   materials per the exemplar's ratified pairings, reference
   integrity and connectivity per the numbered invariants. No
   token may produce a cell the validator would reject.
4. **The mutation-temperature knob** (I5b's named-not-run arm) rides
   this record as a secondary surface: an explicit, capped temperature
   parameter on the constrained resample — OFF by default
   (byte-identical when unset).

WFC is untouched (it already carries the vocabulary at 0.80 and works
over grid patterns directly).

## Pre-registered gates (the implementation is judged, not assumed)

1. **Emission up**: the constrained path's motion-trio emission
   leaves 0.0 and reaches at least HALF its training corpus's rate
   (≥ 0.24 against the 16×16 seed corpus's 0.48) —
   `role_emission_stage0.json` re-run as the instrument.
2. **Validity held at 1.0**: every `generate_batch` candidate still
   passes package genome validation (the existing contract, now over
   the wider alphabet).
3. **Descriptor support widened**: the J1 reachability probe re-run
   reaches STRICTLY MORE than 417/512 proven-reachable bins.
4. **Additivity**: trained and generated from a corpus containing
   only the legacy roles (body/eye/mouth), behavior is preserved
   (the historical 8×8 corpora regenerate equivalent artifacts).
5. **Parity**: lab and package agree verbatim (the existing
   generation parity pins extended to the new alphabet).

Any refuted gate is a first-class finding recorded in the
implementing report — the alphabet change is reverted or narrowed,
never fudged.

## Sources

- `research/experiment_reports/2026-07-20-role-emission.md` (the measurement + mechanism), `2026-07-20-reachability-probe.md` (the instrument)
- `labs/grid_genome/constrained_generator.py`, `markov_grid.py` (`_matrix_from_grid`), `grid_helpers.py` (`grid_from_matrix`)
- `packages/mecha_engine/src/mecha_engine/generation/` (the parity mirror)
- `research/decision_records/0011-run-one-run-two-reconciliation.md`, `0015-dormant-vocabulary-coverage.md`, `0031-wfc-generation-adoption.md`
- `research/grid_genome/grid_invariants.md` (the numbered invariants reconstruction must honor)
