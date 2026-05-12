# Constrained WFC-Style Generator Corpus

This directory contains the constrained local-pattern generator corpus.

Count: 100 JSON grid genomes.

Generation settings:

- Source corpus: `data/seed_grids/`
- Model: learned right/down token adjacency constraints
- Stabilizer: validator-gated local resampling from valid parent grids
- RNG seed: 77
- Generator: `labs/grid_genome/constrained_generator.py`

Baseline result:

- Valid candidates: 100
- Invalid candidates: 0
- Validity rate: 1.0
- Unique signatures: 100

Purpose:

- Test the research-plan claim that WFC-style constraints should act as a
  stabilizer, not the whole creature engine.
- Provide a validity-focused comparator against random mutation and raw Markov.

Interpretation:

This is not a complete overlapping WFC implementation. It is a constrained
local-pattern stabilizer inspired by WFC's adjacency/propagation role. It proves
that learned local constraints plus validator-gated edits can clear the first
validity gate.

