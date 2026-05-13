# Experiment Report: CA/NCA Repeated Stochastic Damage

Date: 2026-05-12

## Objective

Continue the CA/NCA research thread by testing repair under repeated stochastic
damage rather than one-time deterministic masks.

## Source Basis

Growing Neural Cellular Automata distinguish growth, persistence, and
regeneration. They also frame stronger regeneration as requiring damage
exposure. The self-organising texture work reinforces the same local update
view and stochastic/asynchronous cellular dynamics.

Sources:

- https://distill.pub/2020/growing-ca/
- https://distill.pub/selforg/2021/textures/

## Scope

Included:

- seeded stochastic dropout damage
- five damage/repair cycles per sample
- final validity, overlap, readability, and lifecycle survival
- per-cycle damage overlap, repair overlap, and repair gain
- sample exports under `data/cellular_automata/repeated_stress_samples/`

Not included:

- trained NCA
- hidden state channels
- differentiable damage curriculum
- adversarial damage
- human visual repair ratings

## Method

For each of 8 seed grids, the lab starts from a grown/repaired baseline and then
runs five cycles:

1. Apply seeded stochastic dropout damage at rate 0.2.
2. Repair with the existing discrete local attractor.
3. Record damage severity, repair gain, validity, and readability.

The implementation remains labeled
`discrete_nca_inspired_repeated_stochastic_damage` because the repair rule still
receives the target grid as a template.

## Verification

RED command:

```powershell
python -B .\labs\cellular_automata\test_ca_nca_growth_repair.py
```

Initial result:

```txt
ImportError: cannot import name 'apply_stochastic_damage'
```

GREEN command:

```powershell
python -B .\labs\cellular_automata\test_ca_nca_growth_repair.py
```

Result:

```txt
Ran 11 tests in 0.254s
OK
```

Lab command:

```powershell
python -B .\labs\cellular_automata\ca_nca_growth_repair.py --mode repeated-stochastic-damage --output-dir .\data\cellular_automata --count 8 --cycles 5 --dropout-rate 0.2 --repair-steps 8 --rng-seed 20260512
```

Result summary:

```json
{
  "sample_count": 8,
  "cycle_count": 5,
  "total_damage_events": 40,
  "final_validity_rate": 1.0,
  "mean_final_overlap": 1.0,
  "mean_final_readability": 0.862129,
  "mean_final_lifecycle_survival": 1.0,
  "mean_removed_cells_per_event": 2.675,
  "mean_repair_gain_per_event": 0.205373,
  "mean_damaged_overlap_per_event": 0.794627,
  "mean_repair_overlap_per_event": 1.0,
  "min_repair_overlap": 1.0,
  "repaired_validity_rate_per_event": 1.0
}
```

## Findings

The repeated stochastic benchmark is stricter than the prior deterministic
damage benchmark. Across 40 damage events, the local-attractor baseline
recovered to valid, full-overlap grids after each repair cycle.

This is still an assisted baseline. It proves the measurement surface for
repeated repair, not trained morphogenesis. Any future learned NCA must beat
this baseline without relying on the exact target grid as a repair template.

## Decision

Prototype repeated stochastic damage as part of the CA/NCA benchmark contract.
Do not adopt a trained NCA dependency until a less-assisted or learned repair
system beats this baseline and human repair-readability ratings exist.
