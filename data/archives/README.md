# MAP-Elites Archive Artifacts

Measured archive evidence produced by `labs/map_elites_archive/`.

- `map_elites_stage0.json` - the legacy 3-axis baseline archive
  (body mass, sensor count, symmetry).
- `map_elites_extended_stage0.json` - the calibrated 7-axis extended
  archive (adds readability, lifecycle survival, mutation stability,
  behavior neediness); the package parity pins read its numbers.
- `archive_comparators_stage0.json` - scalar/novelty comparators kept
  OUTSIDE the archive (the repertoire is never a leaderboard).
- `stress_probe_scaling_stage0.json` - the size-parametric lifecycle
  stress-probe denominator evidence (cycle 09 A3).
- `generator_evolution_ab_stage0.json` - the generator-vs-evolution
  A/B evidence.
- `niche_scale_archive_stage0.json` - cycle 13 E1: the documented
  first-pass 8x8x8 geometry (symmetry, silhouette-entropy visual
  complexity, behavior neediness) with empirically derived octile
  edges; 274/512 niches occupied over a disjoint 3000-candidate
  evaluation population; the evaluation-unit wall-clock pilot
  (6.29 ms -> 125.8 s @ 20k) in its `measured` section.
- `evaluation_loop_scale_stage0.json` - cycle 13 E3: the full
  generational loop at the documented budget - 20,480 stress-probed
  lifecycle evaluations over 79 generations of population 256 (WFC
  parent path per E2). 281/512 niches (coverage 0.549), QD 222.1,
  zero collapse failures; measured 174.12 s vs the pre-registered
  600 s bound - stdlib holds. The honest saturation observation:
  occupancy plateaus ~gen 50; late generations refine fitness.
