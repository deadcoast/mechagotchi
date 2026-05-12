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
5. Body mass: non-empty body cells must meet a minimum mass threshold.
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

The current repository does not yet contain these corpora. Creating them is the
next required research action after this ontology pass.

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
