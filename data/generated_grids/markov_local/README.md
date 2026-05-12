# Markov Local Generator Corpus

This directory contains the first raw Markov grid generator corpus.

Count: 100 JSON grid genomes.

Generation settings:

- Source corpus: `data/seed_grids/`
- Model: first-order local condition `(left token, up token) -> token`
- RNG seed: 4242
- Generator: `labs/grid_genome/markov_grid.py`

Baseline result:

- Valid candidates: 13
- Invalid candidates: 87
- Validity rate: 0.13

Purpose:

- Test whether local token probability alone can generate valid semantic grid
  bodies.
- Provide a raw Markov comparator before repair, constraints, or WFC are added.

Interpretation:

The raw Markov generator does not beat the random mutation baseline. Its main
failures are missing animation anchors, disconnected body cores, and low body
mass. This supports the research plan's claim that Markov needs constraints or
repair to be useful for body generation.

