# SLIP LCD Seed Constrained Corpus

This directory contains the first SLIP-constrained generated corpus.

Count: 50 JSON grid genomes.

Generation settings:

- Source corpus: `data/seed_grids/`
- Generator: `labs/grid_genome/constrained_generator.py`
- SLIP profile: `data/slips/valid/slip_lcd_seed.json`
- RNG seed: 313

Result:

- Valid candidates: 50
- SLIP-aligned candidates: 50
- Invalid candidates: 0
- Alignment failures: 0

Purpose:

- Prove that a SLIP profile can constrain palette, body mass, organ roles, and
  mutation-rate limits during generation.
- Establish the first profile compatibility test before workshop work begins.

