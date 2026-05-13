# Switchboard Feedback Source Review - 2026-05-12

## Primary Sources

- https://arxiv.org/abs/1003.0146
- http://incompleteideas.net/book/the-book-2nd.html

## Confirmed Facts

- Contextual-bandit systems select actions from context and update selection
  strategy from observed feedback.
- Reinforcement-learning framing treats reward as the signal used to evaluate
  selected actions over time.
- Mechagotchi does not need a broad neural model to test this idea; the current
  switchboard already has action-reward lists that can be updated by lifecycle
  outcomes.

## Mechagotchi Interpretation

The next useful research step is not a larger learner. It is proving that the
existing micro-switchboard can close the loop from action to lifecycle outcome
to future action preference.

The Stage 0 feedback lab therefore compares two policies:

- `feedback_switchboard`: keeps lifecycle reward updates in action memory.
- `frozen_switchboard`: observes the same rewards but resets action memory to
  its initial values after each tick.

This keeps the experiment inspectable and avoids prematurely promoting a
package-level online learner.
