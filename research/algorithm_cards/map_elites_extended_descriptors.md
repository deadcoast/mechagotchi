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
- Behavior neediness is currently SLIP-derived when available.

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

## Decision

Keep as active prototype. Use extended descriptors for research comparison, but
do not replace the simpler baseline until manual readability ratings and broader
lifecycle tests are available.

## Go/No-Go Gate

Promote extended descriptors only if they preserve more meaningful families than
the 3D baseline while maintaining fitness and matching manual readability
ratings.
