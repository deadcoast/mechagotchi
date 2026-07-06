# Algorithm Card: Animation-State Genome Projections

## Name
Animation-state projections (og vocabulary: idle/blink/sleep/beg/ill).

## Purpose
Give creatures an animation vocabulary without a second art source: a
state is a deterministic, visual-only projection of the base grid.

## Mathematical basis
Pure functions over (palette, cell role, parity): blink/sleep map
sensory/expression cells to the background color; beg maps expression to
the accent; ill applies an (x+y)-parity accent pattern to body cells;
idle is the identity. Projections preserve positions, roles, organs.

## Inputs
A validator-valid grid; a state id from the five-state vocabulary.

## Outputs
A projected grid (validator-valid, positions preserved); the
`animstate_300` dataset (60 creatures x 5 states).

## Strengths
Zero authored data; genome stays the single source of truth; trivially
deterministic; every downstream consumer (render packets, previewer,
SLIP animation_vocab) reads one vocabulary.

## Weaknesses
Expressiveness bounded by palette+role transforms (no motion/offsets yet);
five states only.

## Failure modes
Grids whose palettes collapse contrast make states visually identical
(no invariant guards this yet — readability territory).

## Integration risk
Low: additive lab surface; consumers land via T16/T3.5.

## License status
Original.

## Prototype result
300/300 projections valid across 50 seeds + 10 validator-valid generated
grids; idle identity and visual-only invariants pinned by 8 tests.

## Decision
adopt (projection semantics); render-packet selection and previewer are
the T16 follow-up.

## Go-No-Go gate
Projection validity 1.0 on the corpus — met (artifact
`data/grid_genome/animation_states_stage0.json`).
