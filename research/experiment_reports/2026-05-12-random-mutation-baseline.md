# Experiment Report: Random Mutation Baseline

Date: 2026-05-12

## Objective

Complete the next research sequence item after the grid validator baseline:
build a random mutation baseline and create the first 100 generated test grids.

## Scope

Included:

- deterministic random mutation lab under `labs/grid_genome/random_mutation.py`
- tests for child lineage, generated corpus size, uniqueness, and validation
  counts
- generated corpus under `data/generated_grids/random_mutation_baseline/`
- baseline metric report

Not included:

- Markov model
- WFC generator
- mutation repair
- SLIP-weighted mutation
- visual readability scoring

## Mutation Operators

The baseline randomly chooses one naive operation per child:

- shift one cell without updating organ references
- remove all animation anchors
- add one adjacent body cell
- mutate one mutation-rate field
- remove sensor cells without updating organ references
- swap foreground palette colors

These operators are intentionally rough. The point is to create a minimum
quality bar, not a production generator.

## Data Products

| Artifact | Count | Path |
| --- | ---: | --- |
| Generated random-mutation grids | 100 | `data/generated_grids/random_mutation_baseline/` |
| Random mutation tests | 3 | `labs/grid_genome/test_random_mutation.py` |
| Total lab tests | 14 | `labs/grid_genome/test_*.py` |

## Verification

Command:

```powershell
python -m unittest discover -s labs\grid_genome -p 'test_*.py'
```

Result:

```txt
Ran 14 tests in 0.042s
OK
```

Generation command:

```powershell
python labs\grid_genome\random_mutation.py --generated-dir data\generated_grids\random_mutation_baseline --per-seed 2 --rng-seed 90210
```

## Baseline Metrics

```json
{
  "candidate_count": 100,
  "valid_count": 42,
  "invalid_count": 58,
  "validity_rate": 0.42
}
```

## Dominant Failure Classes

The error profile is useful for generator design:

- missing animation anchor: 14 cases
- missing organ references: common when cells move or sensors are removed
- duplicate coordinates: common when naive shifts collide with existing cells
- mutation rates outside 0..1: expected from unbounded random rate mutation
- expression/core organ mismatch: rare but important semantic error

## Decision

Keep random mutation as the baseline comparator. The next generator experiment
should be Markov grid generation, using the seed corpus as training input and
this random baseline as the minimum quality bar.

## Markov/WFC Gate

A candidate generator must beat 42 percent validity before repair. If a method
uses repair or constraint propagation, it must report both raw validity and
post-repair validity so results are not inflated.

