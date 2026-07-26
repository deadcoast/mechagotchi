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
- `coverage_qd_gates_stage0.json` - cycle 13 E4: the documented gate
  at the documented ten-seed protocol (20 full-scale runs). Coverage
  MET 0.549 vs >=0.25; best fitness identical across arms; the
  GA-advantage gate REFUTED (+22.6% vs >=25%, converged) - recorded,
  dispositioned by DR 0032 (MAP-Elites stays adopted; named
  re-openers). Carries per-seed elite rosters for E5.
- `recurrent_families_stage0.json` - cycle 13 E5: 52 recurrent
  morphological families across ALL TEN independent seeded runs vs
  the documented >=5 (strict intersection over 4x4x4 coarse
  descriptor cells; nothing curated). Species memory, measured.
- `generation_refusal_causes_stage0.json` - cycle 22 L1: the
  refusal-cause histogram over the adopted loop, and the instrument
  that CORRECTED DR 0042's reading of its own number. The count
  reproduces exactly (4,435, matching the committed K2 artifact and
  the loop's own independent counter), but the rate is 7.2% not ~22%
  (the old figure divided by the scored budget, 20,480, where
  novelty-first REQUESTS 61,440 attempts), and the promoted path
  refused ZERO invalid candidates: 100% of the refusals are
  `parent grid cannot satisfy SLIP constraints` - the profile
  rejecting the PARENT before a candidate exists. Reasons: palette
  4,411, required organ role 613 (5,024 reasons over 4,435 refusals).
  Origin measured by membership, not inferred: 100% bootstrap, 0 loop
  offspring - as `_acceptable` guarantees, since it requires SLIP
  alignment to emit. The curve is structural: generation 1 refuses
  73.8% of its 768 requests, then decays to exactly 38 per generation
  unbroken for the last 40 generations - SLIP-illegal bootstrap
  elites holding niches permanently. An INSTRUMENT: no generation
  behaviour changed; the fix (and its coverage trade) is its own
  record.
- `lineage_dominance_stage0.json` - cycle 22 L2: the documented
  MAP-Elites gate's SECOND clause, judged for the first time in the
  project's history - "no single lineage > 40% of occupied cells"
  (deep-research.md:205), the quantitative form of Evolution Q1.
  Rule pre-registered before the run (a lineage is a founder line,
  `lineage.ancestor_ids[0]`, oldest-first per the promoted generator;
  pass if max share <= 0.40, and exactly 40% is not a violation per
  the documented wording). VERDICT: PASS at 0.2848 (131 of 460
  occupied cells) across 38 founder lines. Reported beside the
  verdict and deliberately OUTSIDE it, because the clause asks about
  one lineage and cannot see a cartel: FOUR founder lines hold half
  the archive, and the two largest (39.4% between them) are founded
  by WFC *bootstrap* creatures even though the adopted generation
  layer is `constrained` - generation layer and founder stock are
  independent facts. Elite lineage depth spans 0-18; exactly one
  elite has no recorded ancestry. The documented 576-cell repertoire
  vs this archive's proven 512-cell geometry (DR 0029/E1) is
  DECLARED in the artifact, never silently substituted.
