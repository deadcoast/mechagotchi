# Decision Record 0030: SLIP Mass Bounds Scale by Reference Canvas

Date: 2026-07-08

## Status

**Accepted** (cycle 09 · ENGINE track · Phase A, task A3 — the last A3
increment). This is the "size-relative mass bounds in SLIP" item DR 0014
placed on the ladder (RUN TWO's idea, DR 0011 verdict 1), sequenced by
DR 0029 decision 7.

## Context

Every SLIP profile's `grid.body_mass_min/max` is an absolute cell count
denominated at the 8×8 canvas (e.g. the zoo's 4..24). At the ratified
16×16 default (DR 0029), every corpus creature (core 18–85) violates
every shipped profile, which blocks SLIP-aligned generation, exports,
and — in A4 — profile-filtered evolution at 16×16. The DR 0012 ladder
governs SLIP surface changes; both alignment surfaces (the lab authority
`labs/grid_genome/slip.py` and the promoted `mecha_engine.slip`) are
verbatim twins pinned by the F2 pair test over 2,080 alignment cases.

## Decision

**Mass bounds are denominated at the 8×8 reference canvas and scale by
area.** `is_grid_aligned` compares against effective bounds:

    effective_bound = authored_bound * width * height // 64

- At 8×8 this is an exact identity (`bound·64//64 = bound`): every
  historical verdict and error string is byte-identical, so the 2,080
  pinned alignment cases and the zoo/fuzz corpora are untouched.
- At 16×16 the zoo's 4..24 becomes 16..96 — the corpus (18–85) fits,
  and the validator's ratified floor (18) remains the stricter hard
  gate beneath the SLIP preference layer.
- Malformed `grid_size` falls back to the authored bounds (the
  historical behavior for grids that already fail validation).
- The alignment error message reports the EFFECTIVE bounds, so the
  player/author always sees the numbers that were actually applied.

**No schema change**: profiles keep their authored fields and every
fixture stays valid — the scaling is alignment semantics, ratified
here, implemented identically on both surfaces in the same change.

## Alternatives rejected

- *Per-size bound fields* (`body_mass_min_16x16`, …): unbounded key
  growth, fixture churn, and a migration for every existing profile.
- *Fraction fields* (`body_mass_fraction_min/max`) alongside the
  absolute ones: two competing sources of truth in one block, with
  precedence rules the four-surface parity would have to carry forever.
- *Leaving bounds absolute and authoring new 16×16 profiles*: forks the
  zoo per size and contradicts the dossier's own SLIP design (one
  profile spanning grid-size ranges).

## Consequences

- 16×16 creatures align with the shipped profiles wherever palette and
  organ rules allow — the A2 workshop export limitation closes for
  aligned creatures.
- A4's evolution surfaces can filter 16×16 founders by profile.
- The dossier's `grid_size_min/max` generator priors remain a named
  FUTURE extension (they gate generation, not alignment); they enter
  the DR 0012 ladder when Phase B's generator needs them, not before.

## Sources

- `labs/grid_genome/slip.py`, `packages/mecha_engine/src/mecha_engine/slip/authority.py`
- `labs/grid_genome/test_slip_constraints.py`, `labs/grid_genome/test_package_slip_parity.py`
- `research/decision_records/0011-run-one-run-two-reconciliation.md` (verdict 1), `0012-slip-schema-extension-ladder.md`, `0014-grid-size-commitment.md`, `0029-16x16-default-grid-scale.md`
- `research/experiment_reports/2026-07-08-slip-size-relative-bounds.md`
- `data/slips/valid/`, `data/seed_grids_16x16/`
