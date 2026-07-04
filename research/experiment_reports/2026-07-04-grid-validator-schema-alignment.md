# Grid Validator Schema Alignment

Date: 2026-07-04

Status: `research_grid_validator_schema_alignment_no_package_code`

## Purpose

Fix review findings M-07, M-08, L-01 (remainder), L-03, and L-05 from
`docs/03-code_review/2026-07-04-code_review.md`, and close L-02 as verified.
Hard invariant 1 in `research/grid_genome/grid_invariants.md` declares full
schema validity a validation requirement, but `labs/grid_genome/validator.py`
enforced only a subset of `grid_genome.schema.json`.

## What changed

1. **M-07** — `validate_grid` now enforces the schema surfaces it previously
   ignored: `schema_version` const `0.1.0`, `grid_id` pattern
   `^[a-z0-9][a-z0-9_-]{2,63}$`, `grid_size` dimensions 8..64, `cell.role`
   (12-value enum), `cell.material` (7-value enum), `organ.role` (6-value
   enum), and the full `palette` block (id pattern, 2..16 `#RRGGBB` colors).
2. **M-08** — the body-core minimum is now a named constant
   (`BODY_CORE_MIN_CELLS = 4`) and hard invariant 5 in `grid_invariants.md`
   states the threshold explicitly, marking it a lab invariant layered on top
   of the schema (which only requires organ `cells` `minItems 1`).
3. **L-01 (remainder)** — new negative tests: body core below minimum mass,
   unknown cell role/material, unknown organ role, undersized grid, bad
   schema_version/grid_id/palette color. `test_validator.py` previously never
   exercised the body-mass branch.
4. **L-02 (verified, no change)** — the 8-neighbor connectivity choice was
   already documented as deliberate in hard invariant 6; the review flag is
   closed as consistent-by-design.
5. **L-03** — `switchboard_feedback.run_feedback_episode` reports
   `episode_deterministic: true` beside `rng_seed`, which is recorded for
   interface parity only (no code path consumes it at Stage 0).
6. **L-05** — `labs/grid_genome/slip.py` no longer imports
   `corpus_builder.PALETTES` for contract validation; it carries the same
   literal palette set as the authoritative `slip_validator.py`, pinned by
   the Batch 2 cross-validator agreement test.

## Result

```powershell
python -B -m unittest discover -s labs/grid_genome -p "test_*.py"
# Ran 53 tests in 0.535s
# OK  (was 48 before this change)
```

Corpus behavior is unchanged under the stricter validator: 50/50 seed grids
remain valid, 200/200 invalid grids remain rejected, and all
validator-consuming lab suites (cellular_automata, map_elites_archive,
lifecycle_sim, readability_benchmark, ctm_ticks, cubff_transducer) re-ran
green — everything in-tree was already schema-conformant.

`data/micro_learners/switchboard_lifecycle_feedback_stage0.json` regenerated
(adds `episode_deterministic`); JSON validated.

## Decision

`validate_grid` is now the executable form of hard invariant 1 for the
surfaces the schema can express, plus the two documented lab invariants
(body-core minimum, 8-neighbor connectivity). Future schema enum or range
changes must be mirrored in the constants at the top of `validator.py`.

## Verification

```powershell
python -B -m unittest discover -s labs/grid_genome -p "test_*.py"
python -B labs/grid_genome/switchboard_feedback.py
python -m json.tool data/micro_learners/switchboard_lifecycle_feedback_stage0.json
```

## Sources

- `docs/03-code_review/2026-07-04-code_review.md`
- `labs/grid_genome/validator.py`
- `labs/grid_genome/test_validator.py`
- `labs/grid_genome/slip.py`
- `labs/grid_genome/switchboard_feedback.py`
- `research/grid_genome/grid_genome.schema.json`
- `research/grid_genome/grid_invariants.md`
- `data/micro_learners/switchboard_lifecycle_feedback_stage0.json`
