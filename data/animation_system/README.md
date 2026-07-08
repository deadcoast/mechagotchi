# Animation System Data

Cycle 11 (ENGINE - Phase C) artifacts:

- `clip_model_stage0.json` - C1: the clip model gates over the
  16x16 corpus (950 frames; in-bounds/palette-clean/genome-
  untouched all 1.0) and the intra-clip delta table.
- `transition_graph_stage0.json` - C2: the hub-and-spoke
  transition graph measured at 0.9877 validity against the
  dossier's >=0.80 bar (pre-registered metric).
- `animstate_950.json` - C3: the documented animstate dataset
  regenerated at clip-frame resolution (950 labeled samples;
  supersedes the og 8x8 `animstate_300`, which stays in
  `data/grid_genome/` as history). Consumers: Phase D's
  animation-preference learner.
- `animstate_dataset_stage0.json` - C3's gates.

Produced by `labs/animation_system/`.
