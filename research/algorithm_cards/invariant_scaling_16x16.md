# Algorithm Card: 16×16 Invariant Scaling

## Purpose

Re-derive the grid-genome hard/soft invariants at the documented primary
scale (16×16) empirically — census, controls, pilot exemplars, and noise
rejection — so Phase A builds on measured numbers instead of 8×8
constants scaled by fiat (the failure mode DR 0014 warned against).

## Mathematical Basis

- **Dimensionless re-expression**: each 8×8 invariant becomes a
  canvas-share statistic (floor 4/64 = 6.25%) measured over the proven
  corpus, so candidate 16×16 floors can be compared across scaling laws
  (linear ×2, area ×4, the documented dossier anchor 18).
- **Area law anchor**: nearest-neighbor 2× upscaling maps every cell to
  a 2×2 block, multiplying mass by exactly 4 and preserving the mirror
  symmetry score (`1 − mirrored_hamming/occupied`, the promoted archive
  metric) — verified, not assumed.
- **Chance-pass probability**: Monte Carlo estimate (seeded, 4,000
  trials/config) of P(k uniformly scattered cells form one 8-connected
  component) — the validator's actual false-accept semantic for a
  scatter genome — plus largest-component statistics of density-matched
  scatter (sub-percolation regime; Moore-neighborhood site percolation
  threshold ≈ 0.407 vs the corpus median density 0.203).

## Inputs

- The 50 proven 8×8 seeds (`corpus_builder.build_seed_grids`)
- Ten hand-authored 16×16 pilot blueprints (DR 0015 vocabulary, five
  palettes, deliberate lean/heavy/asymmetric/diagonal probes)
- The lab and promoted-package validators (both must accept every pilot)
- Candidate floors {4, 8, 16, 18, 24} and the empirical gates

## Outputs

- `data/grid_genome/invariant_scaling_16x16_stage0.json` (census of all
  three populations, chance-connectivity and noise tables, per-candidate
  gate rows, the ratified numbers)
- `data/grid_genome/pilot_16x16/` (the ten pilots + README — A2's
  precursor corpus)

## Strengths

- Measures instead of assumes; adopts the documented value only after
  no gate refutes it
- The floor law `max(4, 18·w·h // 256)` reproduces BOTH ratified scales,
  so 8×8 pins survive untouched
- Deterministic end to end (string-seeded RNG, fixed report date)
- Pilots are package-validator-clean, so A2/A3 inherit them directly

## Weaknesses

- Ten pilots are a precursor, not a corpus — soft bands (symmetry,
  occupancy ceiling) are provisional until A2's ≥50
- Chance-pass at 16×16 measured 0 in 4,000 trials: an upper bound
  (<0.025%), not a point estimate
- Hand-authored probes were designed to bracket the documented floor;
  the report says so (the strider's 18-core is deliberate, not
  discovered)

## Failure Modes

- If A2's organic corpus minimum lands below 18, the floor must be
  re-ratified (the gate rows make the re-check one lab run)
- Non-square sizes inherit the area law without their own evidence
  until ratified

## Integration Risk

Low — research lab only; the engine keeps its 8×8 constant until A3's
RED-first size-parametric port.

## License Status

Original stdlib-only code, Apache-2.0 (DR 0028).

## Prototype Result

Floor 18 adopted at 16×16 (all gates pass; exceeds the p95=17 accidental
noise blob, which the area-preserving 16 does not); 8-neighbor topology
reaffirmed (26% of seed cores are diagonal-dependent); chance-pass
rejection strengthens to 0/4,000 at scale; pilots span core 18–60,
symmetry 0.128–1.0, occupancy ≤0.4375.

## Decision

**Adopt** (DR 0029). Go gate: A3 re-proves generator/validator/repair/
lifecycle against these numbers at 16×16 without breaking any 8×8 pin.

## Sources

- `labs/grid_genome/invariant_scaling.py`, `labs/grid_genome/test_invariant_scaling.py`
- `data/grid_genome/invariant_scaling_16x16_stage0.json`, `data/grid_genome/pilot_16x16/`
- `research/experiment_reports/2026-07-08-16x16-invariant-scaling.md`
- `research/decision_records/0029-16x16-default-grid-scale.md`
- `research/grid_genome/grid_invariants.md`
