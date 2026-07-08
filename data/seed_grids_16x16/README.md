# 16×16 Seed Grid Corpus

Fifty hand-authored creatures at the ratified default scale (DR 0029;
cycle 09 A2). Seeds 001–010 are the invariant-scaling pilot exemplars
under corpus identity; 011–050 are authored in
`labs/grid_genome/corpus_builder.py` (`BLUEPRINTS_16`) — ten creatures
per palette, rich-token DR 0015 vocabulary (shell, joint, limb, antenna,
sensor, decoration, effect), real morphological variety, NOT upscaled
8×8 blobs. Every seed passes the promoted validator, carries a sensor
pair and exactly one animation anchor, and clears the ratified 18-cell
core floor. Gates pinned by `labs/grid_genome/test_corpus_builder.py`
(`Corpus16Tests`). Counterexamples: `data/invalid_grids_16x16/`.
