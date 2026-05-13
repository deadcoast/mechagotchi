# Experiment Report: CA/NCA Persistence and Damage Benchmark

Date: 2026-05-12

## Objective

Continue the CA/NCA research thread by testing whether the Stage 0 local
attractor remains useful beyond the first center-cut repair demo.

## Source Basis

Growing Neural Cellular Automata frame growth, persistence, and regeneration as
local update-rule problems. The self-organising texture work reinforces the same
local-neighborhood update framing for pattern formation.

Sources:

- https://distill.pub/2020/growing-ca/
- https://distill.pub/selforg/2021/textures/

## Scope

Included:

- three deterministic damage masks: `center_cut`, `left_sensor`, and
  `lower_body`
- local-attractor repair after each damage mask
- idle persistence rollout after repair
- validity, overlap, readability, and lifecycle survival metrics
- stress sample exports under `data/cellular_automata/stress_samples/`

Not included:

- trained neural cellular automata
- hidden state channels
- stochastic damage curriculum
- adversarial or repeated damage during persistence
- human visual ratings

## Method

For each of 8 seed grids, the benchmark applies each damage mask, repairs the
damaged grid with the discrete local attractor, then runs 12 idle persistence
ticks. Each case is measured against the original target grid.

The benchmark is labeled
`discrete_nca_inspired_persistence_damage_stress` to keep the distinction clear:
this is a target-template baseline, not learned morphogenesis.

## Verification

RED command:

```powershell
python -B -m unittest labs.cellular_automata.test_ca_nca_growth_repair
```

Initial result:

```txt
ImportError: cannot import name 'run_damage_stress_benchmark'
```

GREEN command:

```powershell
python -B -m unittest labs.cellular_automata.test_ca_nca_growth_repair
```

Result:

```txt
Ran 8 tests in 0.198s
OK
```

Lab command:

```powershell
python -B .\labs\cellular_automata\ca_nca_growth_repair.py --mode persistence-damage --output-dir .\data\cellular_automata --count 8 --repair-steps 8 --persistence-steps 12 --rng-seed 20260512
```

Result summary:

```json
{
  "sample_count": 24,
  "pattern_count": 3,
  "repair_validity_rate": 1.0,
  "persistence_validity_rate": 1.0,
  "mean_removed_cell_count": 6.083333,
  "mean_damaged_overlap": 0.519015,
  "mean_repair_overlap": 1.0,
  "mean_persistence_overlap": 1.0,
  "mean_persistence_min_overlap": 1.0,
  "mean_readability_delta_repair_vs_damage": 0.192677,
  "repair_lifecycle_survival_mean": 1.0,
  "hardest_pattern": "center_cut"
}
```

## Findings

The local-attractor baseline repaired every measured damage case and preserved
full target overlap through 12 idle persistence ticks.

The `center_cut` mask remains the hardest deterministic pattern by damage
severity, with mean damaged overlap of 0.321388 before repair. The `left_sensor`
mask barely harms most seed grids and produced a slight negative mean proxy
readability delta after repair, so it is not a strong stressor by itself.

The result is useful as a benchmark contract, not as proof that Mechagotchi
needs a trained NCA dependency. The current rule is still assisted by the target
grid and should be beaten by any future learned or less-template-driven system.

## Decision

Prototype the persistence benchmark as part of the CA/NCA lab. Keep the trained
NCA adoption decision on hold until repeated/stochastic damage and human visual
ratings exist.
