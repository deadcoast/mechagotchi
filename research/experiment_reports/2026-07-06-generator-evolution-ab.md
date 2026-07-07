# Experiment Report: Constrained-vs-Hybrid Generator A/B (T17 follow-up)

Date: 2026-07-06

## Objective

T17 found the constrained arm matching the shipped hybrid's perfect
holdout validity with 2.4x the novelty. The queued question: does that
novelty translate into a better MAP-Elites archive? Identical
evaluation, budgets, and parent pools — only the generator differs
(150 evals x 3 seeds per arm).

## Verification

RED -> GREEN (24 lab tests incl. 2 new A/B tests); artifact
`data/archives/generator_evolution_ab_stage0.json`.

## Measured verdict — a dead heat, and the hybrid stands

```txt
                 coverage   qd_score   best     mean
package_hybrid     76.0       69.46    0.9644   0.9140
constrained_wfc    76.0       69.29    0.9653   0.9119
decision: shipped_hybrid_stands
```

## Findings

1. **Raw novelty does not equal archive coverage.** Both arms fill the
   same 76 niches at this budget: the descriptor grid, not the
   generator's cell-set novelty, bounds diversity. T17's 2.4x novelty
   difference dissolves once creatures are projected into descriptor
   space and lifecycle-evaluated.
2. No generator switch: the hybrid stands (and remains simpler to
   operate — one trained model, package-native). The constrained arm
   stays a proven equal-quality alternative should descriptor axes ever
   grow finer.
3. Method note: the A/B reused the T18 comparator harness by
   parameterizing its candidate stream — protocol labs composing, as
   intended.

## Sources

- `labs/map_elites_archive/archive_comparators.py`, `labs/map_elites_archive/test_archive_comparators.py`
- `data/archives/generator_evolution_ab_stage0.json`
- `research/experiment_reports/2026-07-06-generation-bakeoff-formal.md`, `2026-07-06-archive-comparators.md`
