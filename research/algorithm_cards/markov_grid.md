# Algorithm Card: Markov Grid Generator

## Purpose

Generate probable companion body structures from seed grids, parent lineages,
and SLIP constraints.

## Mathematical Basis

Markov chains, higher-order Markov models, n-grams, and optional Bayesian
transition estimates.

## Inputs

- Seed grid corpus
- Parent grid genome
- SLIP constraints
- Neighborhood topology
- Optional mood or animation state

## Outputs

- Candidate child grid genome
- Transition explanation
- Probability trace for sampled local structures

## Strengths

- Small data requirement
- Easy to debug
- Natural fit for ancestor-to-child transitions
- Good baseline against random mutation

## Weaknesses

- Local coherence can still produce global nonsense.
- Higher-order variants can explode the state space.
- Hard constraints need a validator or repair pass.

## Failure Modes

- Disconnected bodies
- Missing required organs
- Over-copying seed grids
- Locally plausible but unreadable silhouettes
- High novelty with low survival value

## Integration Risk

Low to medium.

## License Status

No external code selected. Build the first implementation internally.

## Prototype Result

First raw local Markov prototype completed on 2026-05-12.

```txt
candidate_count: 100
valid_count: 13
invalid_count: 87
validity_rate: 0.13
```

This underperformed the random mutation baseline, which reached 0.42 validity.
The dominant failures were missing animation anchors, disconnected body cores,
and body mass below the minimum.

## Decision

Keep as prototype only. Do not adopt raw local Markov as the body generator.
Use it next as a proposal source for repair, grammar constraints, or WFC-style
stabilization.

## Go/No-Go Gate

Keep if it beats random mutation on valid grid rate, organ placement, ancestor
resemblance, visual coherence, and SLIP compliance.
