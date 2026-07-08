# Algorithm Card: WFC Grid Generator

## Purpose

The documented generation architecture's missing constraint layer
(gap-analysis Phase B): a wave-function-collapse generator over the full
DR 0015 vocabulary at 16×16 — closing Phase A's named remainder (the
4-token generation alphabet).

## Mathematical Basis

- **Overlapping-model WFC with a position channel**: per-cell candidate
  sets are the tokens observed at that (x, y) across the training grids
  (creatures live in the canvas middle), weighted by observed counts;
  legal neighborhoods are the observed right/down token adjacencies,
  applied symmetrically during arc-consistent propagation (AC-3-style
  worklist).
- **Minimum-entropy collapse**: fewest-candidates-first with a
  deterministic (y, x) tie-break; frequency-weighted token choice from a
  string-seeded RNG; bounded restarts on contradiction with the RNG
  stream continuing, so the same (grid_id, seed) always reproduces the
  same creature.
- **The documented stabilizer finishing** (the dossier's own WFC
  recommendation: "use as validator or post-generator stabilizer"):
  local adjacency cannot see global structure — measured: 98%
  disconnected cores from pure collapse. The pass keeps the largest
  8-connected core component, enforces global cardinality constraints
  as restart conditions (core ≥ the DR 0029 floor; at least one eye),
  and normalizes the anchor exactly as the promoted generator does.
  No validator-gated resampling — that is the constrained arm's trick,
  and keeping the arms distinct keeps the B2 bake-off meaningful.

## Inputs

- The 16×16 seed corpus under the adapted 30/10/10 stratified split
  (the dossier's 72/24/24 protocol over the real 50-creature corpus)

## Outputs

- Deterministic 16×16 candidates over the full rich alphabet
- `data/wfc_grid/wfc_grid_stage0.json`

## Strengths

- Validity 1.0 over the 50-candidate stage-0 batch, with all six rich
  roles emitted, 50 unique silhouettes, zero training copies, and core
  masses 31–60 — real morphological variety, not upscaled blobs
- Deterministic end to end; stdlib-only; the split protocol is recorded

## Weaknesses

- The stabilizer deletes stray core blobs, which can strand attached
  limbs/decorations visually (legal; readability judges it in B2)
- Position priors tie the generator to the corpus's spatial layout —
  novelty lives in recombination, not in body-plan relocation

## Failure Modes

- A future corpus with sparse per-position coverage would shrink
  candidate sets toward memorization; the copy-rate metric watches this

## Integration Risk

Medium — adoption into `mecha_engine.generation` happens only through
the B2 bake-off verdict and a B3 decision record.

## License Status

Original stdlib-only code, Apache-2.0.

## Prototype Result

Pure collapse: validity 0.02 (98% disconnected cores) — the negative
result that motivated the documented stabilizer usage. With finishing:
validity 1.0, rich_role_count 6, copy rate 0.0.

## Decision

**Prototype → bake-off** (B2). Go gate: the dossier thresholds
(validity ≥85–95%, ≤250 ms per candidate at 16×16) judged across all
five arms, winner adopted by decision record (B3).

## Sources

- `labs/wfc_grid/wfc_grid.py` (+ `test_wfc_grid.py`)
- `data/wfc_grid/wfc_grid_stage0.json`
- `research/experiment_reports/2026-07-08-wfc-grid-lab.md`
- `docs/project-research/deep-research/01/deep-research.md` (the constraint-systems row)
- `docs/gap-analysis.md` (Phase B), `audits/TODO.md` (cycle 10 B1)
