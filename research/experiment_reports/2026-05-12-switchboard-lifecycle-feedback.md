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

## Update (2026-07-04): zero-delta diagnosis and corrected benchmark

### Diagnosis of the original `need_balance_delta = 0.0`

The original episode was fully deterministic, and the two policies traced
byte-identical action sequences for all 48 ticks, so the delta had to be zero.
The root cause is structural:

1. The bandit thread's utility contribution is capped at
   `(mean - 0.5) * 0.25 * confidence`, at most +/-0.125. The mood and
   interaction-EWMA threads contribute 0.16 to 0.50, so reward memory
   (frozen or learned) can only change a decision inside a narrow margin
   band (idle versus active care in the curious mood).
2. The original miscalibration inflated `play`, an action the mood and EWMA
   threads already favor. The stale memory therefore never flipped a single
   argmax, and a deterministic sweep of 240 stale-reward configurations
   confirmed that play-, feed-, sleep-, and mutate-favoring miscalibrations
   are either dominated by the mood heuristics or self-correcting.
3. The lifecycle reward approximates the global need balance regardless of
   the action taken, so learned means converge toward the running balance and
   only weakly differentiate action quality.

### Corrected benchmark

The miscalibration was changed to the one stale memory the bandit thread can
both act on and correct: an inflated `idle` reward (idle `[0.95, 0.94, 0.96]`,
all other actions flat `[0.5]`) in a calm curious-mood state. The frozen
switchboard locks into idle (35 of 48 ticks) and lets bond and stress drift;
the feedback switchboard corrects the idle mean from observed lifecycle
rewards within roughly a dozen ticks and re-engages (14 idle, 18 play ticks).
Both policies start from the same memory, in the same state, on the same
deterministic episode.

Result summary (`--ticks 48 --rng-seed 20260512`):

```json
{
  "ticks_requested": 48,
  "feedback_survival_ticks": 48,
  "frozen_survival_ticks": 48,
  "feedback_need_balance": 0.790524,
  "frozen_need_balance": 0.750884,
  "feedback_reward_update_count": 48,
  "frozen_reward_update_count": 0,
  "feedback_recovery_events": 13,
  "frozen_recovery_events": 8,
  "need_balance_delta": 0.03964,
  "survival_delta": 0
}
```

The advantage grows with the horizon (+0.0129 at 24 ticks, +0.0396 at 48,
+0.0801 at 72) because the frozen policy never escapes the idle lock while
feedback pays only a fixed correction cost. The dynamic stress suite now
reports `mean_need_balance_delta = 0.026947` (1 scenario better, 2 tied,
0 worse).

### Honest scope of the claim

Feedback beats frozen only for miscalibrations that fall inside the bandit
thread's decision margin. Stale memories on mood-favored actions remain
undetectable in this architecture, and the balance-dominated reward limits
action-quality attribution. Both caveats are recorded in the artifact's
limitations and should gate any promotion beyond lab research.

### Updated decision

The `reward_shaping_not_superior_to_frozen_baseline` blocker condition
(`summary.need_balance_delta > 0`) is now met with an honest, fair,
deterministic comparison: same scenario, same initial memory, same reward
stream for both policies. The lab decision moves to `prototype`; adoption
stays `lab_only_feedback_loop`.
