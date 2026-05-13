# Algorithm Card: SLIP Long-Horizon Behavior Gate

## Purpose

Measure whether current SLIP-selected offspring and held-out generated
candidates survive a longer lifecycle horizon under active care, while keeping
manual readability calibration and persistent evolution out of scope.

## Mathematical Basis

Policy-contrast gate over the same grid/profile pair:

```txt
survival_ratio = survival_ticks / ticks_requested
need_delta = need_balance(switchboard) - need_balance(idle)
long_horizon_pass = switchboard_survival_ratio == 1.0 and idle_survival_ratio < 1.0
```

Missing ticks after death count as `0.0` in lifecycle need balance, so early
death cannot improve the average by shortening the run.

## Inputs

- Valid SLIP profile
- Selected offspring from `slip_offspring_lineage_gate`
- Held-out generated candidates after the parent-selection window
- Lifecycle simulator
- Manual readability benchmark artifact

## Outputs

- Selected-offspring switchboard-vs-idle long-horizon summaries
- Held-out candidate switchboard-vs-idle long-horizon summaries
- Invalid-probe rejections
- Manual readability calibration status
- Closed and blocked state ledger

## Strengths

- Tests real selected offspring rather than only parent elites.
- Uses held-out generated candidates outside the parent-selection window.
- Compares active switchboard care against idle neglect.
- Keeps human-readability readiness explicit instead of folding proxy metrics
  into an evolution claim.

## Weaknesses

- Stage 0 still uses deterministic synthetic care, not player traces.
- The held-out set is small and generated from the current three profiles.
- No package runtime loop exists yet.
- Manual readability ratings remain uncollected.

## Failure Modes

- A candidate can pass synthetic switchboard survival while still failing human
  readability.
- The current care policy may be overfit to the Stage 0 lifecycle equations.
- Profile-weighted evolution can be overclaimed if this gate is treated as a
  persistent runtime instead of a behavior probe.

## Integration Risk

Medium.

## License Status

No external code selected.

## Prototype Result

Stage 0 long-horizon behavior proof completed on 2026-05-13.

```txt
profile_count: 3
long_horizon_success_count: 3
selected_offspring_full_survival_count: 3
held_out_candidate_count: 18
held_out_switchboard_full_survival_count: 18
held_out_idle_death_count: 18
invalid_probe_rejected_count: 2
mean_switchboard_survival_ratio: 1.0
mean_idle_survival_ratio: 0.114583
mean_switchboard_need_balance: 0.782108
mean_idle_need_balance: 0.090432
mean_need_balance_delta_vs_idle: 0.691676
manual_readability_calibration_ready: false
```

## Decision

Keep as active prototype. This closes the Stage 0 held-out long-horizon
behavior-test gap, but does not close manual readability calibration,
profile-weighted evolution, or package runtime integration.

## Go/No-Go Gate

Promote only after the SLIP long-horizon readability packet is filled by
reviewers, proxy readability is calibrated, and package runtime integration
exists.
