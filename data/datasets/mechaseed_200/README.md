# mechaseed_200

`mechaseed_200@2026-07-07` — the og broader body-plan
training/eval set: the 50 hand-authored `mechaseed_50` seeds
(`data/seed_grids/`) plus 150 engine-generated variants, curated
by the corpus bar itself: every variant passes `validate_grid`
and `grid_signature` dedup guarantees novelty. Deterministic —
each variant records the parent and rng seed that reproduce it
through `mecha_engine.generation.generate_candidate`.

Regenerate: `python -B labs/datasets/dataset_program.py`
