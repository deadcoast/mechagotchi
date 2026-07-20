# Algorithm Card: MAP-Elites Extended Descriptors

## Purpose

Expand `mecha_darwin` archive niches beyond body mass, sensor count, and
symmetry so the archive can preserve families that differ in readability,
lifecycle survival, mutation stability, and behavior tendency.

## Mathematical Basis

Quality-diversity search with a researcher-defined behavior descriptor space.
The Stage 0 extension keeps the original MAP-Elites dimensions and adds four
new bins:

- readability
- lifecycle survival
- mutation stability
- behavior neediness

## Inputs

- Candidate grid genomes
- SLIP profile
- Proxy readability score
- Short lifecycle simulation result
- Mutation-rate vector

## Outputs

- Extended descriptor vector
- Elite archive keyed by seven-dimensional niche
- Fitness components
- Legacy-vs-extended comparison
- Coverage, best fitness, mean elite fitness, and QD score

## Strengths

- Keeps the baseline descriptor dimensions for direct comparison.
- Brings post-v0.1 lifecycle and readability metrics into archive selection.
- Separates observed niche diversity from total theoretical coverage.
- Keeps QDax/JAX as a future acceleration path, not a dependency.

## Weaknesses

- Lifecycle probes are synthetic and short.
- Readability is still proxy-scored until manual ratings are collected.
- Seven 5-bin dimensions create a large sparse space.
- Lifecycle dynamics are bistable under the switchboard policy (stress load
  ≤ 0.94 stabilizes forever; ≥ 0.95 collapses at tick 12–14), so the
  morphology-derived stress probe yields survival spread 2, not a continuum;
  intermediate survival bins await a harsher lifecycle model.
- `mutation_stability` is cap-normalized (`1 − mean(rate/cap)`): the raw-mean
  form mathematically could not leave the top bin under LCD caps.

## Failure Modes

- Descriptor sparsity can make coverage look low even when observed diversity improves.
- Proxy readability can overvalue valid but bland creatures.
- Synthetic survival may overfit to switchboard behavior.
- Bad bin thresholds can split or merge species families arbitrarily.

## Integration Risk

Medium.

## License Status

No external code selected.

## Prototype Result

First descriptor-extended archive completed on 2026-05-12.

```txt
candidate_count: 160
legacy_descriptor_dimensions: 3
extended_descriptor_dimensions: 7
legacy_occupied_niches: 19
extended_occupied_niches: 29
extended_best_fitness: 0.979592
extended_mean_elite_fitness: 0.957708
extended_qd_score: 27.773545
```

Behavior-neediness descriptor fix regenerated on 2026-07-04 (review finding
H-03): the axis was SLIP-derived and therefore constant per archive run; it
is now grid-derived with the profile neediness as a prior shift, and the
archive reports per-axis `descriptor_bin_spread`.

```txt
candidate_count: 160
legacy_occupied_niches: 19
extended_occupied_niches: 33
extended_best_fitness: 0.979592
extended_mean_elite_fitness: 0.958156
extended_qd_score: 31.619138
descriptor_bin_spread: body_mass 3, sensor_count 4, symmetry 4,
  readability 3, lifecycle_survival 1, mutation_stability 1,
  behavior_neediness 2
```

Descriptor-axis calibration regenerated on 2026-07-04 (review finding
L-12): per-candidate mutation-temperature jitter within SLIP caps in the
constrained generator, cap-normalized mutation stability, and a
morphology-derived lifecycle stress probe.

```txt
candidate_count: 160
extended_occupied_niches: 83
extended_best_fitness: 0.972366
extended_qd_score: 72.069987
descriptor_bin_spread: body_mass 3, sensor_count 4, symmetry 4,
  readability 3, lifecycle_survival 2, mutation_stability 5,
  behavior_neediness 2
```

Behavior-neediness reference-canvas recalibration on 2026-07-20
(cycle 19 I5a, DR 0036): the mass term scales by `64 / area` — an
EXACT identity at 8×8 (`map_elites_extended_stage0.json` regenerates
byte-identical; every number above is unchanged), and at 16×16 the
sensor signal leads again (r +0.904 vs mass −0.407; the axis derives
7 of 7 distinct octile edges in the niche-scale geometry). Evidence:
`labs/map_elites_archive/neediness_scale16.py` +
`data/archives/neediness_scale16_stage0.json`.

SLIP lifecycle/archive bridge completed on 2026-05-12.

```txt
profile_count: 3
archive_effect_count: 3
distinct_archive_fingerprints: 3
mean_archive_qd_score: 7.671145
```

SLIP runtime selection policy completed on 2026-05-13.

```txt
selection_success_count: 3
selected_elite_count: 3
distinct_selected_archive_niches: 3
mean_selected_selection_score: 0.955828
```

SLIP offspring lineage gate completed on 2026-05-13.

```txt
offspring_gate_success_count: 3
lineage_decision_count: 3
add_archive_niche_count: 1
hold_parent_count: 2
mean_selected_offspring_score: 0.928194
```

## Decision

Keep as active prototype. Use extended descriptors for research comparison,
profile-effect probes, Stage 0 runtime elite selection, and the follow-on
long-horizon behavior gate, but do not promote profile-weighted evolution until
manual readability ratings and package-level contracts are available. The
Stage 0 multigeneration runner now covers lab-only lineage depth.

## Go/No-Go Gate

Promote extended descriptors only if they preserve more meaningful families than
the 3D baseline while maintaining fitness and matching manual readability
ratings.
