# Algorithm Card: Repair-Validity Boundary Study (mortal-wound gradient)

- **Name**: Repair-validity boundary — production-surface measurement of
  aligned-but-lifecycle-invalid repairs across the damage regime, with
  cause diagnosis.
- **Purpose**: C6 — answer the open question the G2 promotion-drift fix
  left: is the `skipped_invalid` skip correct biology, or should
  wound-site repair guarantee a connected core? Decide with evidence.
- **Mathematical basis**: frequency estimation over the production
  `runtime.evolve` surface — for each regime `(dropout, cycles)`, the
  rate `skipped_invalid / total_creatures` across N rng seeds, read from
  each report's own per-creature `archive_decision`; cause diagnosis by
  reproducing the mechanism (deep candidate → `live_cycle` at heavy
  damage) and validating the resulting bodies for their error
  vocabulary.
- **Inputs**: the seed corpus, the fixture SLIP, the promoted
  generation/repair models; the regime grid.
- **Outputs**: per-regime rates, the in-band (session) rate, the cause
  histogram, and an evidence-backed verdict.
- **Strengths**: measures the REAL surface (not a reconstruction —
  which two false starts proved necessary); the verdict is data-driven
  and the invariant is named, not assumed; determinism pinned.
- **Weaknesses**: rates are on the fixture profile at Stage-0 evolve
  parameters; a different covenant or population scale would re-measure
  (the method transfers, the numbers don't).
- **Failure modes**: the study's OWN two failure modes are recorded as
  the finding's spine — grid_id-overflow (harness bug masquerading as
  biology, fixed by per-cycle id reassignment) and
  reconstruction-blindness (same `validate_grid` on both sides, fixed by
  measuring production `evolve`).
- **Integration risk**: none — read-only over public surfaces.
- **License status**: original stdlib implementation.
- **Prototype result**: hypothesis "extreme-damage-only" REFUTED — a
  damage-scaled mortality gradient present throughout (0.025 at 0.2×1 →
  0.10 at 0.9×4), ~0.0125 in the session band; the ONLY failing
  invariant is the disconnected required body core; the skip is retained
  as correct biology, the connected-core contract rejected.
- **Decision**: adopt (measurement + verdict); revisit only via the
  repair model's core-preservation tuning if a difficulty curve ever
  needs it — not by reopening the verdict.
- **Go-No-Go gate**: production-surface measurement with per-creature
  decision accounting; determinism; the failing invariant named by
  diagnosis (core disconnect the only cause); the refuted hypothesis and
  the rejected alternative both on the record.

## Sources

- `research/experiment_reports/2026-07-07-repair-validity-boundary.md`
- `labs/repair_boundary/repair_validity_boundary.py` (+ `test_repair_validity_boundary.py`)
- `data/repair_boundary/repair_validity_boundary_stage0.json`
- `packages/mecha_engine/src/mecha_engine/runtime/evolve.py`
- `packages/mecha_engine/src/mecha_engine/genome/validation.py`
