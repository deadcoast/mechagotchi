# Random Mutation Baseline Corpus

This directory contains the first generated grid corpus for Mechagotchi.

Count: 100 JSON grid genomes.

Generation settings:

- Source corpus: `data/seed_grids/`
- Per seed: 2 children
- RNG seed: 90210
- Generator: `labs/grid_genome/random_mutation.py`

Baseline result:

- Valid candidates: 42
- Invalid candidates: 58
- Validity rate: 0.42

Purpose:

- Establish a naive baseline before Markov and WFC experiments.
- Provide the first generated test grid corpus required by the research plan.
- Expose common mutation failure modes for validator and generator design.

