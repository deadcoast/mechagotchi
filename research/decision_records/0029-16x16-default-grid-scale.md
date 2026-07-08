# Decision Record 0029: 16×16 Ratified as the Proven Default Grid Scale

Date: 2026-07-08

## Status

**Accepted** (cycle 09 · ENGINE track · Phase A, task A1; gap analysis
`docs/gap-analysis.md` §3 row 1 — the foundational gap). This is the
size-adoption record DR 0014 required: "Any size adoption takes its own
decision record citing [the measurement's] numbers." DR 0014's 8×8
commitment was phase-scoped and is superseded for the default; 8×8
remains valid input and keeps its own ratified invariants.

## Context

The documents name 16×16 as the primary creature scale (validity-research
§1.34: the 16×16 creature "proves the entire thesis"; the deep-research
dossier's bake-off protocol, SLIP grid ranges 12×12–24×24, and its 16×16
invariants block: `min_body_mass: 18`, sensor pair, one connected
component). Everything ever proven in this repository was proven at 8×8
with ~13-cell bodies. The 8×8 numbers do not scale by fiat (DR 0014
documented exactly which constants are 8×8-coupled), so A1 measured.

## Evidence (labs/grid_genome/invariant_scaling.py, 2026-07-08)

All numbers in `data/grid_genome/invariant_scaling_16x16_stage0.json`.

- **8×8 census (50 proven seeds):** core mass 9–14 (p50 10), occupancy
  0.1875–0.2656 (p50 0.2031), symmetry 0.286–0.857 spanning 4 of 5
  descriptor bins, exactly 1 anchor each, ≥2 eyes each; **26% of seed
  cores are 8-connected but not 4-connected** — the diagonal tolerance
  is load-bearing, not decorative.
- **2×-upscaled controls (50):** core mass exactly 4× the parent,
  every dimensionless statistic preserved — the area law confirmed, and
  the "upscaled blob" anti-goal characterized (A2 must not look like
  this population).
- **Ten 16×16 pilot exemplars** (hand-authored, all five palettes, full
  DR 0015 vocabulary, lab- and package-validator clean): core mass
  18–60 (p50 44), occupancy 0.109–0.4375, symmetry 0.128–1.0 across
  3+ descriptor bins; one pilot's core is 8- but not 4-connected.
  Deliberate probes: an 18-core strider at the documented floor, a
  60-core turtle near the ceiling, a 0.13-symmetry serpent, a
  0.65-symmetry golem.
- **Chance-pass rejection (4,000 seeded trials per config):** scattered
  cells pass mass+connectivity by chance at 0.625% for the 8×8 floor
  (k=4); at 16×16 every candidate floor measured 0 — scale strengthens
  the invariant below the ≤2% false-accept bar.
- **Density-matched noise characterization (1,000 trials):** the largest
  accidental 8-connected component at 16×16 (52 scattered cells, the
  corpus median density) is p50 9, **p95 17**, max 27.

## Decisions

1. **16×16 is the proven default target scale.** 8×8 stays valid input
   (SLIP ranges span sizes); every downstream Phase A task (A2–A5)
   proves its surface at 16×16 without breaking the 8×8 pins.
2. **Body-core floor at 16×16 = 18** (hard invariant 5), the documented
   dossier value, adopted because no empirical gate refutes it and the
   noise characterization favors it: candidates {4, 8, 24} fail the
   canvas-share band (±25% of the ratified 8×8 share); 16 and 18 pass
   every gate; 18 additionally exceeds the p95 accidental blob (17
   cells), which 16 does not.
3. **The size-parametric floor law** for schema-legal but unratified
   sizes: `body_core_min_cells(w, h) = max(4, 18·w·h // 256)`. It
   reproduces both ratified points (8×8 → 4, 16×16 → 18); any other
   size ratifies on its own corpus before becoming a proven target.
4. **Connectivity topology unchanged:** 8-neighbor BFS (invariant 6),
   reaffirmed by the measured 4-connectivity shortfall in both corpora.
5. **Sensor pair at 16×16 is a soft expectation and an A2 corpus gate**
   (the dossier's `requires_sensor_pair`); hard invariant 7 (≥1 required
   sensor/expression organ) is unchanged. Hard-validator status is
   revisited in A3 with generator evidence.
6. **Measured soft bands at 16×16** (SLIP-weightable, archive-binnable):
   symmetry full-range with evidence at low/mid/high; occupancy soft
   ceiling ~0.44; exactly one animation anchor per creature remains the
   corpus norm (hard invariant 8 stays ≥1).
7. **Engine adoption is task A3, RED-first and size-parametric** — the
   lab/package validators keep the 8×8 constant and its exact error
   string until then; parity pins stay unbroken. The same task ladder
   carries the SLIP size-relative mass bounds and the archive stress
   probe renormalization DR 0014 anticipated.
8. **No new dependency needed for A1** — pure-stdlib counting sufficed.
   NumPy enters where A3's retraining/generation scale demands it
   (DR 0028), justified there.

## Consequences

- A2 builds the ≥50-creature 16×16 seed corpus (the pilots are its
  precursor and quality bar) plus the invalid corpus and editor canvas.
- A3 re-proves generator/validator/repair/lifecycle at 16×16 against
  these ratified numbers.
- `research/grid_genome/grid_invariants.md` §"Scale Ratification" is the
  living statement of the ratified floors; the schema's `grid_size`
  description now names the ratified scales.

## Sources

- `docs/gap-analysis.md` (Phase A), `audits/TODO.md` (cycle 09, A1)
- `labs/grid_genome/invariant_scaling.py` (+ `test_invariant_scaling.py`)
- `data/grid_genome/invariant_scaling_16x16_stage0.json`
- `data/grid_genome/pilot_16x16/`
- `research/grid_genome/grid_invariants.md`, `research/grid_genome/grid_genome.schema.json`
- `research/experiment_reports/2026-07-08-16x16-invariant-scaling.md`
- `research/decision_records/0014-grid-size-commitment.md`, `0015-dormant-vocabulary-coverage.md`, `0028-license-and-dependency-policy.md`
- `docs/project-research/validity-research.md` (§1.34), `docs/project-research/deep-research/01/deep-research.md`
