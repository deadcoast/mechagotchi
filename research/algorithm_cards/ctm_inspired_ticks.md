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

- [continuous-thought-machines](https://github.com/SakanaAI/continuous-thought-machines)
- [ctm-website-official](https://pub.sakana.ai/ctm/)
- [arXiv:2505.05522](https://arxiv.org/abs/2505.05522)

## Prototype Result

Implemented on 2026-05-12 as a lightweight confidence-gated wrapper around the
existing micro-switchboard.

Artifacts:

- `labs/ctm_ticks/ctm_inspired_ticks.py`
- `labs/ctm_ticks/test_ctm_inspired_ticks.py`
- `data/ctm_ticks/ctm_inspired_ticks_stage0.json`
- `research/experiment_reports/2026-05-12-ctm-inspired-internal-ticks.md`
- `research/source_notes/2026-05-12-ctm-source-review.md`

Measured result:

- Scenario count: 4
- Baseline accuracy: 1.0
- Deliberative accuracy: 1.0
- Mean baseline confidence: 0.805435
- Mean deliberative confidence: 0.824067
- Mean confidence gain: 0.018632
- Mean tick count: 1.75
- Extra-tick cases: 1

## Decision

Prototype as a small switchboard mechanism. Do not adopt CTM as a core
dependency.

## Go/No-Go Gate

Keep only if confidence-gated ticks measurably improve action selection or user
readability over a single-pass switchboard.
