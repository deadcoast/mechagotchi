# Grid Genome Invariants

These invariants are the first Stage 0 validation contract. They separate hard
engine requirements from SLIP preferences.

## Hard Invariants

1. Schema validity: every grid must validate against
   `grid_genome.schema.json`.
2. Bounds: every cell coordinate must be inside `grid_size`.
3. Unique occupancy: at most one cell definition may exist for a coordinate.
4. Renderability: each non-empty cell must reference a valid palette color or
   visual token resolvable by the renderer.
5. Body mass: the required body-core organ must contain at least
   `max(4, 18 * width * height // 256)` cells — the size-parametric floor
   ratified by DR 0029 from measurement (4 at 8×8, unchanged; 18 at 16×16,
   the documented dossier value). This is a lab invariant layered on top of
   the schema, which only requires organ `cells` `minItems 1`. The engine
   validator (`BODY_CORE_MIN_CELLS` in `labs/grid_genome/validator.py` and
   the promoted `mecha_engine.genome`) still applies the 8×8 constant 4 at
   every size; the size-parametric port is cycle-09 task A3 (RED-first,
   8×8 parity pins unbroken).
6. Connectedness: required body-core cells must form one connected component
   under the selected neighborhood topology. The Stage 0 validator uses
   8-neighbor connectivity because pixel-art bodies can be visually connected
   through diagonal contact.
7. Sensor presence: at least one required sensor or expression organ must exist.
8. Animation readiness: at least one animation anchor must exist.
9. Organ integrity: every organ cell coordinate must point to a matching cell.
10. Mutation bounds: every mutation rate and per-cell mutation weight must be in
    the inclusive range 0..1.

## Soft Invariants

These can be weighted by SLIP rather than hard-coded globally:

- symmetry range
- maximum body mass
- eye count
- limb count
- palette contrast target
- novelty pressure
- lineage resemblance
- acceptable stress or damage range

## First Validation Report Targets

The first validator report should measure:

| Metric | Target for seed corpus |
| --- | --- |
| Valid schema parse rate | 100 percent |
| False accept rate on invalid corpus | <= 2 percent |
| False reject rate on valid corpus | <= 5 percent |
| Render packet emission | 100 percent for valid seeds |
| Human readability median | >= 4/5 for hand-authored seeds |

## Required Test Corpora

- `50 hand-made seed grids`
- `100 generated test grids`
- `200 invalid counterexample grids`

These corpora exist at 8×8 (see the Stage 0 baseline below) and, since
cycle-09 task A2, at the ratified 16×16 default: 50 hand-authored seeds
in `data/seed_grids_16x16/` (grown from the pilot exemplars in
`data/grid_genome/pilot_16x16/`) and 200 counterexamples in
`data/invalid_grids_16x16/`, gated by
`labs/grid_genome/test_corpus_builder.py` (`Corpus16Tests`: core floor
18, sensor pair, one anchor, palette spread, DR 0015 vocabulary,
distinct silhouettes). The 100-grid *generated* corpus at 16×16 arrives
with A3's generator work.

## Stage 0 Baseline Result

The first validator baseline now exists:

| Corpus | Count | Result |
| --- | ---: | --- |
| Hand-authored seed grids | 50 | 50 accepted, 0 rejected |
| Invalid counterexample grids | 200 | 0 accepted, 200 rejected |

Recorded in:

- `research/experiment_reports/2026-05-12-grid-validator-baseline.md`
- `data/seed_grids/`
- `data/invalid_grids/`

## Scale Ratification — 16×16 (2026-07-08, DR 0029)

The invariants above were first proven at 8×8. Cycle 09 task A1 re-derived
them at the documented primary scale (16×16) empirically — census of the
proven 8×8 corpus as dimensionless statistics, a 2×-upscaled control
population (area-law anchor), ten hand-authored 16×16 pilot exemplars
across the DR 0015 vocabulary, and seeded noise experiments. Evidence:
`data/grid_genome/invariant_scaling_16x16_stage0.json` (lab:
`labs/grid_genome/invariant_scaling.py`).

### Ratified hard-invariant floors

| Scale | Body-core floor (invariant 5) | Status |
| --- | ---: | --- |
| 8×8 | 4 | ratified (Stage 0, unchanged) |
| 16×16 | 18 | ratified (A1 measurement; dossier value adopted) |
| other sizes 8–64 | `max(4, 18·w·h // 256)` | interim law; each scale ratifies on its own corpus |

The law reproduces both ratified points (18·64//256 = 4). Candidate floors
{4, 8, 16, 18, 24} were gated on: all pilots pass, all upscaled controls
pass, chance-pass rate ≤ 2% (the false-accept bar), and canvas-share
within ±25% of the ratified 8×8 share (4/64). Floors 4/8/24 fail the
share band; 16 and 18 pass everything; 18 is adopted because it is the
documented value AND exceeds the p95 accidental blob of density-matched
noise at 16×16 (17 cells), which 16 does not.

### Reaffirmed and measured at 16×16

- **Connectivity (invariant 6):** 8-neighbor topology unchanged. It is
  load-bearing: 26% of the proven 8×8 seed cores and one pilot (the
  turtle's diagonal neck) are 8-connected but not 4-connected.
- **Chance-pass rejection:** scattered-cell genomes pass mass+connectivity
  by chance at 0.625% for the 8×8 floor; at 16×16 every candidate floor
  measured 0 in 4,000 trials — scale strengthens the invariant.
- **Sensor presence (invariant 7):** unchanged (≥1 required sensor or
  expression organ). The dossier's 16×16 sensor PAIR is ratified as a
  soft expectation and an A2 corpus gate (every 8×8 seed and every pilot
  already carries ≥2 eyes); its hard-validator status is revisited in A3
  with generator evidence.
- **Soft bands measured at 16×16** (pilot population): symmetry
  0.128–1.0 spanning ≥3 of 5 descriptor bins (asymmetric serpent 0.13,
  golem 0.65, symmetric-bilateral majority ≥0.9 — the dossier's
  bilateral-bias regime); occupancy fraction 0.109–0.4375 (soft ceiling
  ~0.44 at 16×16 vs the 8×8 corpus band 0.1875–0.2656 — 16×16 affords
  heavier silhouettes without filling the canvas); anchors exactly 1
  per creature in every population.

### Sources

- `research/decision_records/0029-16x16-default-grid-scale.md`
- `research/experiment_reports/2026-07-08-16x16-invariant-scaling.md`
- `labs/grid_genome/invariant_scaling.py` (+ `test_invariant_scaling.py`)
- `data/grid_genome/invariant_scaling_16x16_stage0.json`
- `data/grid_genome/pilot_16x16/`
- `docs/project-research/deep-research/01/deep-research.md` (dossier invariants block)
- `research/decision_records/0014-grid-size-commitment.md` (the re-opener this fulfills)
