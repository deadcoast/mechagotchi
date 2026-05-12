# Invalid Grid Corpus

This directory contains Stage 0 invalid counterexamples for the grid genome
validator.

Count: 200 JSON grid genomes.

Each seed grid has four invalid variants:

- duplicate coordinate
- out-of-bounds cell
- missing animation anchor
- missing organ reference

Purpose:

- Measure false accepts.
- Keep validator behavior reproducible.
- Provide negative examples before generator bake-off work starts.

The files were materialized from `labs/grid_genome/corpus_builder.py`.
