# Experiment Report: CA/NCA Growth and Repair

Date: 2026-05-12

## Objective

Continue the post-v0.1 research plan by starting CA/NCA growth and repair now
that lifecycle metrics exist.

## Source Basis

Growing Neural Cellular Automata demonstrate seed growth, persistence, and
regeneration as local update-rule problems. The broader differentiable
self-organising systems thread also frames NCA as local pattern-generation
systems whose updates depend on immediate neighborhoods.

Sources:

- https://distill.pub/2020/growing-ca/
- https://distill.pub/selforg/2021/textures/

## Scope

Included:

- deterministic damage mask
- seed growth from one anchor cell
- NCA-inspired local-attractor repair
- grid validity checks
- proxy readability deltas
- lifecycle survival after growth/repair
- sample grid exports under `data/cellular_automata/samples/`

Not included:

- differentiable neural update training
- learned hidden channels
- stochastic damage curriculum
- human visual ratings of growth/repair
- runtime animation preview

## Method

For each of 8 seed grids:

1. Apply a deterministic center-cut damage mask.
2. Grow a grid from the target anchor cell using local neighborhood updates.
3. Repair the damaged grid using the same local-attractor rule.
4. Validate target, damaged, grown, and repaired grids.
5. Measure target-overlap, readability, SLIP alignment, and lifecycle survival.

The implementation deliberately labels the result as
`discrete_nca_inspired_local_attractor` because it is not a trained NCA.

## Verification

RED command:

```powershell
python -B -m unittest discover -s labs\cellular_automata -p 'test_*.py'
```

Initial result:

```txt
ModuleNotFoundError: No module named 'ca_nca_growth_repair'
```

GREEN command:

```powershell
python -B -m unittest discover -s labs\cellular_automata -p 'test_*.py'
```

Result:

```txt
Ran 5 tests in 0.084s
OK
```

Lab command:

```powershell
python -B labs\cellular_automata\ca_nca_growth_repair.py --output-dir data\cellular_automata --count 8 --growth-steps 12 --repair-steps 8 --rng-seed 20260512
```

Result summary:

```json
{
  "sample_count": 8,
  "growth_validity_rate": 1.0,
  "repair_validity_rate": 1.0,
  "growth_slip_alignment_rate": 0.25,
  "repair_slip_alignment_rate": 0.25,
  "mean_damaged_overlap": 0.321388,
  "mean_growth_overlap": 1.0,
  "mean_attractor_repair_overlap": 1.0,
  "mean_readability_delta_repair_vs_damage": 0.430918,
  "lifecycle_after_repair": {
    "mean_survival_ratio": 1.0,
    "mean_delta_vs_damaged": 1.0
  }
}
```

## Findings

The discrete attractor rule proves the contract: growth and repair can be
measured against grid validity, readability, and lifecycle survival. Damaged
grids are often invalid or lifecycle-dead; repaired grids return to valid,
lifecycle-viable forms.

This is not evidence that a trained NCA should become a dependency. The result
is an inspectable baseline showing what a later trained system must beat.

The LCD SLIP alignment rate is 0.25 because the sample set uses mixed seed
palettes while the current default profile only allows the LCD palette. That is
a profile-coverage issue, not a repair failure.

## Decision

Prototype the discrete CA/NCA-inspired local-attractor lab. Do not adopt a
trained NCA dependency until the project has harder damage cases, persistence
tests, and human visual ratings for growth/repair readability.
