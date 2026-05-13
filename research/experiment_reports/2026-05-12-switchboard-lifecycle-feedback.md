# Experiment Report: Switchboard Lifecycle Feedback

Date: 2026-05-12

## Objective

Continue the post-v0.2 research sequence by closing the loop between
switchboard actions, lifecycle rewards, and later action preferences.

## Source Basis

Contextual-bandit framing is relevant because it selects actions from context
and updates action choice from observed feedback. Reinforcement-learning reward
framing is relevant because lifecycle outcomes can become the action-value
signal for future decisions.

Sources:

- https://arxiv.org/abs/1003.0146
- http://incompleteideas.net/book/the-book-2nd.html

## Scope

Included:

- feedback-enabled switchboard episode
- frozen-reward switchboard baseline
- lifecycle-derived reward updates
- survival ticks, need balance, recovery count, action counts, and reward means
- artifact at `data/micro_learners/switchboard_lifecycle_feedback_stage0.json`

Not included:

- persisted online learner state
- contextual-bandit algorithm such as LinUCB
- real user reward traces
- non-annoyance or attachment ratings
- package promotion into `packages/mecha_engine`

## Method

Both policies start from the same deliberately miscalibrated action-reward
memory. Each tick runs the current switchboard, applies the selected lifecycle
action, and observes the lifecycle reward.

The `feedback_switchboard` keeps that reward in action memory. The
`frozen_switchboard` records the reward for measurement but resets action memory
to its initial values after each tick.

## Verification

RED command:

```powershell
python -B .\labs\grid_genome\test_switchboard_feedback.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'switchboard_feedback'
```

GREEN command:

```powershell
python -B .\labs\grid_genome\test_switchboard_feedback.py
```

Result:

```txt
Ran 4 tests in 0.036s
OK
```

Lab command:

```powershell
python -B .\labs\grid_genome\switchboard_feedback.py --output-dir .\data\micro_learners --ticks 48 --rng-seed 20260512
```

Result summary:

```json
{
  "ticks_requested": 48,
  "feedback_survival_ticks": 48,
  "frozen_survival_ticks": 48,
  "feedback_need_balance": 0.767384,
  "frozen_need_balance": 0.767384,
  "feedback_reward_update_count": 48,
  "frozen_reward_update_count": 0,
  "feedback_recovery_events": 9,
  "frozen_recovery_events": 9,
  "need_balance_delta": 0.0,
  "survival_delta": 0
}
```

## Findings

The feedback loop works mechanically: lifecycle rewards are captured every tick
and retained in the feedback policy's action-reward memory. The frozen baseline
observes the same rewards but does not learn from them.

The measured outcome is conservative. Feedback did not improve need balance or
survival over the frozen baseline in this synthetic scenario, but it also did
not reduce either metric. The value of this lab is the explicit closed-loop
contract and artifact, not a claim that reward shaping is solved.

## Decision

Prototype the feedback loop as lab-only switchboard research. Do not promote an
online learner into packages until reward shaping beats the frozen baseline on
need balance, recovery, or survival in a broader scenario set.
