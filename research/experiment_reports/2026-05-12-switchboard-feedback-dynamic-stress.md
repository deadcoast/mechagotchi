# Experiment Report: Switchboard Feedback Dynamic Stress

Date: 2026-05-12

## Objective

Continue the v0.3 next-step item to stress switchboard feedback under changing
needs and user-interaction patterns.

## Scope

Included:

- Dynamic attention dropout scenario
- Sleep-debt followed by hunger pressure
- Overplay followed by grid instability
- Feedback switchboard vs frozen switchboard comparison
- Need-balance, survival, recovery, event, and reward-update metrics

Not included:

- Real user interaction traces
- Persistent learner state
- Human non-annoyance or attachment ratings
- Package promotion

## Method

Each scenario starts from a deliberately miscalibrated action-reward memory.
Both policies observe the same lifecycle rewards:

- `feedback_switchboard` retains reward updates.
- `frozen_switchboard` resets action rewards after each tick.

Each scenario applies deterministic stress events during the episode so the
policy sees changing need pressure and interaction patterns.

## Verification

RED command:

```powershell
python -B .\labs\grid_genome\test_switchboard_feedback.py
```

Initial result:

```txt
ImportError: cannot import name 'run_switchboard_feedback_stress_suite'
```

GREEN command:

```powershell
python -B .\labs\grid_genome\test_switchboard_feedback.py
```

Result:

```txt
Ran 6 tests
OK
```

Lab command:

```powershell
python -B .\labs\grid_genome\switchboard_feedback.py --output-dir .\data\micro_learners --ticks 60 --rng-seed 20260512 --stress
```

Result summary:

```json
{
  "ticks_requested": 60,
  "scenario_count": 3,
  "dynamic_event_count": 6,
  "feedback_better_need_balance_count": 0,
  "feedback_tied_need_balance_count": 2,
  "feedback_worse_need_balance_count": 1,
  "mean_need_balance_delta": -0.002226,
  "feedback_better_survival_count": 0,
  "feedback_worse_survival_count": 0
}
```

Per-scenario deltas:

| Scenario | Need-balance delta | Survival delta | Recovery delta |
| --- | ---: | ---: | ---: |
| `attention_dropout` | -0.006677 | 0 | 0 |
| `sleep_debt_then_feed_pressure` | 0.0 | 0 | 0 |
| `overplay_grid_instability` | 0.0 | 0 | 0 |

## Findings

The feedback mechanism remains mechanically active under dynamic stress: the
feedback policy retained 60 reward updates per scenario while the frozen
baseline retained none.

The outcome is not adoption evidence. Feedback did not improve survival in any
scenario and produced a slightly negative mean need-balance delta. This suggests
the current reward memory can react to lifecycle outcomes, but the shaping rule
is still too weak or too delayed to outperform the frozen baseline.

## Decision

Status: `watch_reward_shaping`.

Keep the feedback loop as lab-only research. Do not promote online reward
shaping into package interfaces until it beats the frozen baseline under dynamic
stress and real or more realistic interaction traces.

## Outputs

- `labs/grid_genome/switchboard_feedback.py`
- `labs/grid_genome/test_switchboard_feedback.py`
- `data/micro_learners/switchboard_feedback_dynamic_stress_stage0.json`
- `data/micro_learners/switchboard_feedback_dynamic_stress_README.md`

## Update (2026-07-04): rerun after the stale-idle miscalibration fix

The base miscalibration was corrected after the zero-delta diagnosis (see the
update in `2026-05-12-switchboard-lifecycle-feedback.md`): both policies now
start from a stale idle-favoring reward memory instead of a play-favoring one
that never changed any decision. The stress suite was regenerated with the
same command (`--ticks 60 --rng-seed 20260512 --stress`).

Result summary:

```json
{
  "ticks_requested": 60,
  "scenario_count": 3,
  "dynamic_event_count": 6,
  "feedback_better_need_balance_count": 1,
  "feedback_tied_need_balance_count": 2,
  "feedback_worse_need_balance_count": 0,
  "mean_need_balance_delta": 0.026947,
  "feedback_better_survival_count": 0,
  "feedback_worse_survival_count": 0
}
```

Per-scenario deltas:

| Scenario | Need-balance delta | Survival delta | Recovery delta |
| --- | ---: | ---: | ---: |
| `attention_dropout` | 0.0 | 0 | 0 |
| `sleep_debt_then_feed_pressure` | +0.08084 | 0 | -10 |
| `overplay_grid_instability` | 0.0 | 0 | 0 |

Feedback now beats the frozen baseline in one scenario and ties in two, with
no scenario worse and no survival regression, so the suite decision moves to
`prototype_stress_feedback`. The recovery delta of -10 in the winning scenario
reflects that the frozen policy repeatedly re-enters danger zones and recovers
from them, while the feedback policy avoids entering them; recovery counts
reward oscillation, not health. The two tied scenarios keep their strongly
mooded trajectories where reward memory is decision-irrelevant, which is the
same structural cap documented in the base-lab diagnosis.

