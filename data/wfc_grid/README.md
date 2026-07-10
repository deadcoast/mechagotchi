# WFC Grid Artifacts

Measured generation evidence produced by `labs/wfc_grid/`.

- `wfc_grid_stage0.json` - B1: the WFC constraint generator over the
  full rich alphabet at 16x16 (position priors + adjacency, bounded
  restarts).
- `generation_bakeoff16_stage0.json` - B2: the documented five-arm
  bake-off (random/markov/constrained/wfc/hybrid) at 16x16; WFC won by
  the pre-registered rule; the hybrid refutation recorded.
- `wfc_population_throughput_stage0.json` - E2: the promoted surfaces
  at population scale (256 x 3 generations, parents from archive
  elites per the promoted evolve semantics). Validity 1.0 both arms;
  WFC 7.04 ms/candidate with retraining vs the 250 ms bar; archive
  171 -> 233 niches under the WFC parent path; the DR 0031 standing
  remainder's evidence.
