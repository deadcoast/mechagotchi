# Experiment Report: Grid Validator Baseline

Date: 2026-05-12

## Objective

Complete the next Stage 0 research task from `docs/02-research_plan.md`:
create the first seed corpus, create invalid counterexamples, implement the
first validator lab, and emit a validation report.

## Scope

Included:

- 50 hand-authored 8x8 seed grid blueprints.
- 200 invalid counterexample grids.
- Minimal semantic validator under `labs/grid_genome/`.
- Unit tests for hard invariants and corpus counts.
- Baseline corpus validation run.

Not included:

- JSON Schema engine integration.
- Render packet generation.
- Human readability rating panel.
- Random mutation, Markov, or WFC generator tests.

## Validator Rules Tested

- grid bounds
- duplicate coordinates
- mutation unit intervals
- organ reference integrity
- required sensor or expression organ
- animation anchor presence
- minimum body-core mass
- required body-core connectedness

The connectedness topology is 8-neighbor. This was selected because several
valid pixel-art silhouettes are visually connected through diagonal contact.

## Data Products

| Artifact | Count | Path |
| --- | ---: | --- |
| Valid seed grids | 50 | `data/seed_grids/` |
| Invalid counterexamples | 200 | `data/invalid_grids/` |
| Validator tests | 11 | `labs/grid_genome/test_*.py` |

## Validation Results

Command:

```powershell
python -m unittest discover -s labs\grid_genome -p 'test_*.py'
```

Result:

```txt
Ran 11 tests in 0.019s
OK
```

Corpus check:

```json
{
  "seed_count": 50,
  "seed_accepted": 50,
  "seed_rejected": 0,
  "invalid_count": 200,
  "invalid_accepted": 0,
  "invalid_rejected": 200,
  "seed_failures": {},
  "invalid_false_accepts": []
}
```

## Metric Summary

| Metric | Result |
| --- | ---: |
| Valid seed acceptance | 50/50 |
| Seed false reject rate | 0 percent |
| Invalid rejection | 200/200 |
| Invalid false accept rate | 0 percent |
| Render packet emission | Not tested |
| Human readability median | Not tested |

## Findings

The first semantic validator is sufficient to distinguish the initial positive
and negative corpora. It is not yet a complete schema validator. The next
validator step should integrate the JSON Schema contract or generate it from a
Pydantic model, then compare schema-level failures with semantic failures.

The authored seed corpus is intentionally small at 8x8. This keeps the first
generator bake-off cheap while still testing body mass, sensors, expression
cells, anchors, palette references, and organ membership.

## Decision

Proceed to the random mutation baseline. The generator bake-off should use this
corpus as the first training/evaluation input until a larger 16x16 corpus is
authored.

## Sources

- `docs/02-research_plan.md`
- `research/grid_genome/grid_invariants.md`
- JSON Schema Draft 2020-12 validation specification:
  https://json-schema.org/draft/2020-12/json-schema-validation
- Python `unittest` documentation:
  https://docs.python.org/3/library/unittest.html

