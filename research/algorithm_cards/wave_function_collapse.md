# Algorithm Card: Wave Function Collapse

## Purpose

Use example-derived local constraints to stabilize grid bodies and preserve
pixel-level coherence.

## Mathematical Basis

Constraint propagation over local NxN patterns. The reference implementation
uses an observation-propagation cycle and can be interpreted as local pattern
constraint solving.

## Inputs

- Seed bitmap or semantic grid corpus
- Pattern size
- Symmetry policy
- Allowed adjacency relationships
- Optional pre-constraints from SLIP

## Outputs

- Candidate grid
- Contradiction status
- Pattern provenance

## Strengths

- Strong local visual coherence
- Good fit for tile and pixel constraints
- Supports constrained synthesis
- Useful as a repair or stabilizer after another generator proposes a body

## Weaknesses

- Can overfit to sample grids.
- Contradictions are possible.
- It does not understand companion survival or behavior by itself.

## Failure Modes

- No solution under strict constraints
- Repetitive bodies
- Local correctness without global body meaning
- Too much similarity to seed examples

## Integration Risk

Medium.

## License Status

Reference repo is MIT licensed, but provided image samples and tiles are called
out separately in the license file. Treat code and sample assets separately.

Source: https://github.com/mxgmn/WaveFunctionCollapse

## Prototype Result

First constrained WFC-style stabilizer completed on 2026-05-12.

```txt
candidate_count: 100
valid_count: 100
invalid_count: 0
validity_rate: 1.0
unique_signatures: 100
```

This is not a complete overlapping WFC implementation. It uses learned
right/down token adjacency rules and validator-gated local resampling from
valid seed parents.

## Decision

Adopt constrained local-pattern stabilization as the next generator direction.
Do not claim full WFC adoption yet, and do not make WFC the whole generation
engine.

## Go/No-Go Gate

Adopt only if it improves local visual coherence over Markov alone without
reducing novelty beyond the accepted threshold.
