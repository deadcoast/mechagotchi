# Decision Record 0014: Grid Size — 8×8 Committed for the Current Phase

Date: 2026-07-05

## Status

**Accepted** (audit task T6; owner: "Next action: T6 --go"). Answers og
research question 2 ("8×8, 16×16, 24×24, 32×32?") — until now an
undecided default, not a decision.

## Evidence (executable probe, 2026-07-05)

A seed grid scaled 2× to 16×16 (cells → 2×2 blocks, organs remapped,
single anchor preserved):

- **Validator: size-generic already** — the 16×16 grid passes
  `validate_grid` cleanly (schema admits 8–64; connectivity/anchor/
  organ invariants scale).
- **Everything calibrated is 8×8-coupled**: body mass 10 → 40 blows the
  profile bounds (4..24) — every SLIP fixture and the mass invariants
  assume the 64-cell canvas; the archive's contracted stress probe
  (`load = mass/16 …`) reads 2.5 at 16×16 — saturated nonsense (16 is
  half of 8×8's 64 cells, an 8×8 constant); the generation model trains
  per-position on 8×8 seeds and cannot emit other sizes; the readability
  proxy's features and the pending human calibration are 8×8; the
  workshop editor, animation projections, codecs fixtures, and
  `animstate_300` are all 8×8 corpora.

## Decision

**8×8 is the committed creature size for the current phase.** Reasons:

1. Every calibrated constant, corpus, gate, and pending human
   calibration is 8×8-denominated; a size change today would invalidate
   the evidence base mid-phase for no measured need.
2. Expressiveness is not the binding constraint: 50 seeds, 25 archive
   niches, a measurable selection gradient, five animation states, and
   the workshop flows were all achieved at 8×8. The og bar was
   "expressive but manageable" — met, with margin.
3. The LCD-tiny legibility thesis is the product identity; 8×8 is its
   sharpest test.

## The multi-size path (planned, not abandoned)

- The schema stays 8–64 (already true); the validator stays
  size-generic (probe-proven).
- **T17, the formal bake-off, is the designated re-opener** — og's own
  protocol demands 16×16 and 24×24 arms, which force the real work:
  per-size generator training corpora, renormalized stress probe
  (`mass / (w·h/4)`-family, re-derived from evidence, never scaled by
  fiat), size-relative mass bounds in SLIP (RUN TWO's min/max_size idea,
  DR 0011 verdict 1, enters the ladder then), per-size readability
  calibration, and workshop/editor size support.
- Any size adoption takes its own decision record citing T17's numbers.

## Sources

- `audits/TODO.md` (T6, T17), `.depreciated/01-formatted.md` (question 2), `.depreciated/02-design.md` (bake-off protocol)
- `research/grid_genome/grid_genome.schema.json` (8–64), `research/grid_genome/grid_invariants.md`
- `packages/mecha_engine/src/mecha_engine/archive/_metrics.py` (the /16 constant)
- `research/decision_records/0011-run-one-run-two-reconciliation.md` (verdict 1)
