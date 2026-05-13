# Experiment Report: CA/NCA Learned Repair Comparison

Date: 2026-05-12

## Objective

Compare a less-assisted learned repair rule against the existing assisted
CA/NCA local-attractor repair baseline.

## Source Basis

Growing Neural Cellular Automata frame regeneration as a learned local-rule
problem where damage exposure broadens the basin of attraction for repair. The
self-organising textures work reinforces asynchronous local cellular updates as
a useful pattern-formation substrate. The soft-robot NCA paper provides another
primary example of regeneration as a learned local cellular policy rather than
direct target-template reconstruction.

Sources:

- https://distill.pub/2020/growing-ca/
- https://distill.pub/selforg/2021/textures/
- https://arxiv.org/abs/2102.02579

## Scope

Included:

- corpus-trained role/position prior model
- leave-forward training split: first 8 grids evaluated, remaining 42 grids used
  for the learned prior
- seeded stochastic dropout damage
- five damage/repair cycles per evaluated grid
- direct comparison against the target-template local-attractor repair baseline
- validity, overlap, readability, repair gain, and lifecycle survival metrics

Not included:

- differentiable neural cellular automata training
- hidden state channels
- gradient-based repair policy learning
- human repair-readability ratings
- package promotion into `packages/mecha_engine`

## Method

The assisted baseline is the existing `repair_with_local_attractor` rule. It
receives the damaged grid and the exact target grid template.

The learned comparison rule is `repair_with_role_prior_model`. It receives only
the damaged grid and a corpus-level model trained by
`train_role_prior_repair_model`. The model records role/token priors by grid
position and required organ fallback positions. It does not receive a target
grid during repair.

For each of 8 target grids, the benchmark runs five cycles:

1. Apply seeded stochastic dropout damage to the assisted and learned current
   states.
2. Repair the assisted state with the target-template local attractor.
3. Repair the learned state with the role-prior model.
4. Score both against the original target for evaluation only.

## Verification

RED command:

```powershell
python -B .\labs\cellular_automata\test_ca_nca_growth_repair.py
```

Initial result:

```txt
ImportError: cannot import name 'repair_with_role_prior_model'
```

GREEN command:

```powershell
python -B .\labs\cellular_automata\test_ca_nca_growth_repair.py
```

Result:

```txt
Ran 14 tests in 0.310s
OK
```

Lab command:

```powershell
python -B .\labs\cellular_automata\ca_nca_growth_repair.py --mode learned-repair-comparison --output-dir .\data\cellular_automata --count 8 --cycles 5 --dropout-rate 0.2 --repair-steps 8 --rng-seed 20260512
```

Result summary:

```json
{
  "sample_count": 8,
  "cycle_count": 5,
  "total_damage_events": 40,
  "assisted_final_validity_rate": 1.0,
  "learned_final_validity_rate": 1.0,
  "mean_assisted_final_overlap": 1.0,
  "mean_learned_final_overlap": 0.778563,
  "mean_final_overlap_delta_learned_vs_assisted": -0.221437,
  "mean_assisted_repair_gain_per_event": 0.205373,
  "mean_learned_repair_gain_per_event": 0.148998,
  "mean_event_overlap_delta_learned_vs_assisted": -0.159211,
  "learned_beats_assisted_final_count": 0,
  "learned_ties_assisted_final_count": 1,
  "mean_learned_final_readability": 0.795148,
  "mean_learned_final_lifecycle_survival": 1.0,
  "target_template_used_by_learned": false
}
```

## Findings

The learned role-prior repair is less assisted and remained valid across the
full comparison. It also preserved lifecycle survival. However, it did not beat
the assisted local-attractor baseline. The assisted baseline retained full
overlap, while the learned rule averaged `0.778563` final overlap and trailed
by `0.221437`.

This is useful evidence: a simple corpus prior is enough to repair valid
Mechagotchi-like anatomy, but it is not enough to replace the assisted
target-template benchmark. A future trained NCA or stronger learned rule must
beat this comparison without receiving the exact target grid during repair.

## Decision

Status: `watch_learned_repair`.

Keep the assisted CA/NCA baseline as the benchmark contract. Do not promote
learned repair into the engine package yet. The next repair research step should
use either a stronger learned local rule or a true trained NCA damage curriculum
and compare against this artifact.

