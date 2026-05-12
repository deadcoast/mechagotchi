# Algorithm Card: Micro-Learning Switchboard

## Purpose

Coordinate many small adaptive learners into one explainable companion action
decision.

## Mathematical Basis

EWMA, Bayesian counters, contextual bandits, HMM-like latent states,
rule-weight learners, and small logistic scorers.

## Inputs

- Visible companion state
- Hidden companion state
- User interaction events
- SLIP behavior weights
- Recent prediction errors
- Grid stability and mutation risk scores

## Outputs

- Next action
- Per-learner signal map
- Confidence
- Explanation
- Reward or correction signal

## Strengths

- Interpretable
- Testable in isolation
- Avoids one broad "pet brain"
- Fits the project plan's intelligence-thread model

## Weaknesses

- Requires a clean switchboard contract.
- Bad reward shaping can create annoying behavior.
- Too many learners can produce noisy decisions.

## Failure Modes

- Conflicting signals without arbitration
- User interaction loops optimized for engagement instead of care
- Hidden state drift
- No explanation for action changes

## Integration Risk

Medium.

## License Status

No external code selected.

## Prototype Result

First interpretable switchboard prototype completed on 2026-05-12.

```txt
scenario_count: 3
hungry_recent_attention: feed, confidence 0.829113
low_energy: sleep, confidence 0.816769
stable_curious: play, confidence 0.776111
```

Implemented micro-learners:

- recent interaction EWMA
- rule-based hidden mood estimator
- reward-average action preference bandit
- mutation risk scorer

## Decision

Keep as active prototype. Do not introduce a broad ML model. Next step is to
connect switchboard actions to lifecycle rewards and survival metrics.

## Go/No-Go Gate

Each learner must report input, output, confidence, explanation, and measurable
effect on action or survival.
