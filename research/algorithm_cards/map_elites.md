# Algorithm Card: MAP-Elites Archive

## Purpose

Preserve many high-performing companion families instead of converging toward
one best creature.

## Mathematical Basis

Quality-diversity search. MAP-Elites stores elites in niches defined by
behavior descriptors selected by the researcher.

## Inputs

- Candidate grid genome
- Life simulation result
- Fitness vector
- Behavior descriptor vector
- SLIP alignment score
- Lineage history

## Outputs

- Updated archive
- Niche assignment
- Elite replacement decision
- Coverage and QD-score metrics

## Strengths

- Direct fit for "many species, not one optimum"
- Makes diversity measurable
- Supports lineage and family browsing
- QDax offers a later modular acceleration path using container, emitter, and
  scoring-function concepts

## Weaknesses

- Descriptor choice is load-bearing.
- Bad descriptors create meaningless diversity.
- Needs a working simulator and generator before results mean anything.

## Failure Modes

- One lineage dominates archive cells
- Archive covers visually different but behaviorally identical variants
- Fitness rewards exploit validation gaps
- Niches encode style rather than useful behavior

## Integration Risk

Medium.

## License Status

No code selected for first prototype. QDax is a strong future study target, but
the first archive should be CPU-first and internal.

Sources:

- https://arxiv.org/abs/1504.04909
- https://qdax.readthedocs.io/en/latest/overview/
- https://arxiv.org/abs/2308.03665

## Prototype Result

First CPU archive prototype completed on 2026-05-12.

```txt
candidate_count: 200
map_elites_occupied_niches: 24
map_elites_coverage: 0.192
map_elites_best_fitness: 0.898214
map_elites_mean_elite_fitness: 0.821066
scalar_top_occupied_niches: 7
scalar_top_coverage: 0.056
scalar_top_best_fitness: 0.898214
```

## Decision

Keep as active `mecha_darwin` archive direction. Keep CPU-first and internal
until descriptors and fitness stabilize. QDax remains a later acceleration
candidate, not a dependency.

## Go/No-Go Gate

Keep MAP-Elites if archive coverage beats a simple GA baseline while preserving
best-fitness within the accepted tolerance and producing visibly distinct
families.
