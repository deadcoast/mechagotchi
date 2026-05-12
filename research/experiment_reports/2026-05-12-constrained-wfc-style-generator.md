# Experiment Report: Constrained WFC-Style Generator

Date: 2026-05-12

## Objective

Continue Stage 2 grid generation research by testing whether local pattern
constraints can stabilize generated grid bodies better than raw Markov and
random mutation.

## Scope

Included:

- learned right/down token adjacency constraints from the 50 seed grids
- validator-gated local resampling from valid parent grids
- 100 generated candidates under
  `data/generated_grids/constrained_wfc_style/`
- tests for constraint training, valid generation, and validity-gate comparison

Not included:

- full entropy-minimizing overlapping WFC
- contradiction backtracking
- SLIP constraints
- human readability panel
- novelty scoring beyond unique semantic signatures

## Method

The lab follows the research-plan instruction to use WFC as a stabilizer rather
than the entire creature engine.

The implementation trains adjacency counts from seed-token matrices:

```txt
. empty
B body core
A body core with animation anchor
E sensor
M expression
```

It records observed right/down token pairs, starts each candidate from a valid
seed parent, attempts local resampling under learned adjacency constraints, and
commits only proposals that pass the semantic validator.

This is WFC-style constraint stabilization, not a full overlapping WFC
implementation. It corresponds to the plan's "WFC / constraints -> structural
validity" role.

## Verification

Command:

```powershell
python -m unittest discover -s labs\grid_genome -p 'test_*.py'
```

Result:

```txt
Ran 21 tests in 0.147s
OK
```

Generation command:

```powershell
python labs\grid_genome\constrained_generator.py --generated-dir data\generated_grids\constrained_wfc_style --count 100 --rng-seed 77
```

## Metrics

```json
{
  "candidate_count": 100,
  "valid_count": 100,
  "invalid_count": 0,
  "validity_rate": 1.0,
  "unique_signatures": 100,
  "error_counts": {}
}
```

## Baseline Comparison

| Generator | Candidates | Valid | Invalid | Validity rate |
| --- | ---: | ---: | ---: | ---: |
| Random mutation | 100 | 42 | 58 | 0.42 |
| Raw local Markov | 100 | 13 | 87 | 0.13 |
| Constrained WFC-style stabilizer | 100 | 100 | 0 | 1.00 |

## Findings

The constrained stabilizer clears the first validity gate. It also supports the
earlier Markov finding: local probability by itself is insufficient, but local
patterns become useful when paired with semantic validation and constrained
proposal commits.

The result should not be overinterpreted. This lab starts from valid seed
parents, so it proves stabilization and safe variation more than open-ended
birth. A future full WFC or hybrid generator must report:

- raw generation validity
- repair/stabilized validity
- exact-parent copy rate
- unique signature count
- human readability
- ancestor resemblance

## Decision

Adopt constrained local-pattern stabilization as the next generator direction.
Do not claim full WFC adoption yet. The next research step should add SLIP-style
constraints or a repair pass around raw Markov proposals, then compare whether
the system can generate valid bodies from weaker initial states.

## Source Notes

The official WaveFunctionCollapse reference describes local similarity through
observed NxN patterns, observation-propagation, contradictions, and constrained
synthesis. This lab uses the constrained-synthesis role but not the complete
entropy-collapse algorithm.

Source: https://github.com/mxgmn/WaveFunctionCollapse

