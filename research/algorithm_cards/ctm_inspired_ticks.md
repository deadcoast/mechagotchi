# Algorithm Card: CTM-Inspired Internal Ticks

## Purpose

Borrow the useful CTM idea that thinking unfolds over internal time, then adapt
it into a lightweight companion switchboard mechanism.

## Mathematical Basis

Temporal processing and synchronization concepts from Continuous Thought
Machines, adapted as rule-based or micro-learner deliberation cycles.

## Inputs

- Candidate actions
- Micro-learner confidence scores
- Current companion state
- Recent interaction history
- SLIP behavior weights

## Outputs

- Action decision
- Confidence value
- Number of deliberation ticks used
- Explanation trace

## Strengths

- Can make uncertain behavior visibly deliberate
- Does not require a large model
- Aligns with the companion's tick-based life cycle

## Weaknesses

- CTM itself may be excessive for the project.
- Extra deliberation can feel like lag if exposed poorly.
- The benefit must be measured against a simpler switchboard.

## Failure Modes

- Over-engineered behavior loop
- Cosmetic "thinking" with no better decisions
- Hidden state becomes hard to debug

## Integration Risk

Medium if implemented as a concept. High if CTM code becomes a dependency.

## License Status

The CTM reference repository is Apache-2.0 licensed. First prototype should not
reuse code.

Sources:

- https://github.com/SakanaAI/continuous-thought-machines
- https://pub.sakana.ai/ctm/

## Prototype Result

Not started.

## Decision

Watch as conceptual inspiration. Do not adopt as a core dependency.

## Go/No-Go Gate

Keep only if confidence-gated ticks measurably improve action selection or user
readability over a single-pass switchboard.

