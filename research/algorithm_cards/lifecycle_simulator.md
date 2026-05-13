# Algorithm Card: Lifecycle Simulator

## Purpose

Measure whether a grid-genome companion can survive over ticks while balancing
hunger, energy, stress, bond, and grid stability.

## Mathematical Basis

Discrete-time state simulation with bounded state variables, action effects,
full-horizon scoring, and recovery-event counting. The Stage 0 policy
comparison uses deterministic switchboard actions, idle neglect, and random
actions.

## Inputs

- Valid grid genome
- Optional SLIP profile
- Tick horizon
- Policy name
- Random seed

## Outputs

- Survival ticks
- Alive/dead status and death cause
- Full-horizon need balance score
- Recovery event count
- Action counts
- Final state
- Per-tick history

## Strengths

- Gives the switchboard a measurable survival feedback loop.
- Penalizes early death instead of rewarding short high-average runs.
- Keeps the first lifecycle contract small enough to inspect and test.
- Produces machine-readable artifacts for future archive descriptors.

## Weaknesses

- Uses synthetic care actions rather than player traces.
- Need balance is a proxy, not yet a human-validated experience score.
- Grid stability is scalar; local cell stress propagation is not active.
- Recovery logic is threshold-based and may need richer physiology later.

## Failure Modes

- Reward shaping can over-favor one action.
- Survival can become trivial if thresholds are too forgiving.
- Averages can hide oscillation without per-tick history review.
- Random policy results depend on seed and action distribution.

## Integration Risk

Medium.

## License Status

No external code selected.

## Prototype Result

First lifecycle simulator prototype completed on 2026-05-12.

```txt
policy        survival_ticks  alive  need_balance  recovery_events
switchboard   72              true   0.789129      14
idle          11              false  0.121004       0
random        21              false  0.236001       2
```

The switchboard policy survived the 72-tick horizon and beat idle/random on
full-horizon need balance.

SLIP runtime selection follow-up completed on 2026-05-13.

```txt
selection_success_count: 3
mean_selected_need_balance: 0.793865
mean_selected_survival_ratio: 1.0
```

SLIP long-horizon behavior follow-up completed on 2026-05-13.

```txt
long_horizon_success_count: 3
held_out_candidate_count: 18
held_out_switchboard_full_survival_count: 18
held_out_idle_death_count: 18
mean_switchboard_survival_ratio: 1.0
mean_idle_survival_ratio: 0.114583
mean_need_balance_delta_vs_idle: 0.691676
```

## Decision

Keep as active prototype. Lifecycle metrics are now connected to a Stage 0
archive elite selector and held-out long-horizon behavior gate, but package
runtime integration and manual readability calibration remain open.

## Go/No-Go Gate

Adopt into the engine only after package runtime integration exists and manual
readability/care calibration is collected.
