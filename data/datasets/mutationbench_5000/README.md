# mutationbench_5000

`mutationbench_5000@2026-07-07` — mutation-operator
evaluation: 5,000 offspring cases (50 parents x 100 fixed rng
seeds under `slip_lcd_seed`) as JSONL rows. Each row carries the
case config, outcome measurements (validity, alignment, lineage
generation, cell-level diffs), and the candidate's
`grid_signature`: the candidate grid itself is deterministically
reproducible from `(parent_grid_id, rng_seed, profile)` through
`generate_candidate`, and the signature verifies any
regeneration byte-for-byte — 5,000 grids of truth without
5,000 stored grids.

Regenerate: `python -B labs/datasets/dataset_program.py`
