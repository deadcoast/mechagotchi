# Experiment Report: Markov Local Generator

Date: 2026-05-12

## Objective

Prototype the first Markov grid generator from `docs/02-research_plan.md` and
compare raw validity against the random mutation baseline.

## Scope

Included:

- local first-order Markov model under `labs/grid_genome/markov_grid.py`
- tests for model training, generation, corpus size, and metrics
- 100 generated Markov candidates under `data/generated_grids/markov_local/`
- baseline comparison against random mutation

Not included:

- semantic repair
- hard constraints
- SLIP weighting
- WFC pattern propagation
- visual readability scoring

## Method

Each seed grid is converted into an 8x8 token matrix:

```txt
. empty
B body core
A body core with animation anchor
E sensor
M expression
```

The model counts local transitions:

```txt
(left token, up token) -> current token
```

Generation samples an 8x8 token grid row by row, then compiles it back into a
semantic grid genome.

## Verification

Command:

```powershell
python -m unittest discover -s labs\grid_genome -p 'test_*.py'
```

Result:

```txt
Ran 18 tests in 0.069s
OK
```

Generation command:

```powershell
python labs\grid_genome\markov_grid.py --generated-dir data\generated_grids\markov_local --count 100 --rng-seed 4242
```

## Metrics

```json
{
  "candidate_count": 100,
  "valid_count": 13,
  "invalid_count": 87,
  "validity_rate": 0.13,
  "error_counts": {
    "body mass below minimum: required body core has fewer than 4 cells": 32,
    "missing animation anchor": 70,
    "required body core is disconnected": 45
  }
}
```

## Baseline Comparison

| Generator | Candidates | Valid | Invalid | Validity rate |
| --- | ---: | ---: | ---: | ---: |
| Random mutation | 100 | 42 | 58 | 0.42 |
| Raw local Markov | 100 | 13 | 87 | 0.13 |

## Findings

Raw local Markov generation does not beat random mutation. The generator learns
common local token neighborhoods, but it does not preserve global obligations:
minimum body mass, connected core, and required animation anchor.

This supports the planning thesis: Markov should not be used alone as the body
generator. It needs one of these next:

- validator repair pass
- grammar constraints
- WFC-style local pattern propagation
- explicit anchor and organ priors

## Decision

Do not adopt raw local Markov as the core generator. Keep it as a prototype and
use it as the proposal stage for the next constrained or repaired generator
experiment.

