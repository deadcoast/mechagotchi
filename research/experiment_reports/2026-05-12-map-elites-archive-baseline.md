# Experiment Report: MAP-Elites Archive Baseline

Date: 2026-05-12

## Objective

Continue the research plan into Stage 3 by building the first CPU-only
`mecha_darwin` archive and comparing repertoire coverage against a scalar
top-fitness selector.

## Source Basis

The MAP-Elites paper frames the algorithm as a way to map high-performing
solutions across researcher-chosen dimensions of variation instead of returning
one best solution. QDax uses the same conceptual split that is useful for
Mechagotchi architecture: container, emitter, and scoring function.

Sources:

- https://arxiv.org/abs/1504.04909
- https://qdax.readthedocs.io/en/latest/overview/

## Scope

Included:

- CPU archive implementation under `labs/grid_genome/darwin_archive.py`
- descriptors for body mass, sensor count, and symmetry
- bounded fitness score for validation, mass, sensors, symmetry, animation
  anchor, and optional SLIP alignment
- scalar top-k comparator
- archive artifact at `data/archives/map_elites_stage0.json`

Not included:

- life simulation
- mutation emitter loop
- lineage reproduction
- QDax/JAX dependency
- user interaction or bond signals
- behavior descriptors from companion simulation

## Descriptor Space

The first archive uses a 5 x 5 x 5 descriptor grid:

```txt
descriptor = (
  body_mass_bin,
  sensor_count_bin,
  symmetry_bin
)
```

This gives 125 possible niches. The descriptor set is intentionally primitive;
it tests archive mechanics before behavior simulation exists.

## Fitness

The first bounded fitness score combines:

- validator pass
- body mass near target
- sensor count
- symmetry
- animation anchor presence
- optional SLIP alignment

This is not the final `mecha_darwin` fitness model. It is only the first
measurable archive baseline.

## Verification

Command:

```powershell
python -m unittest discover -s labs\grid_genome -p 'test_*.py'
```

Result:

```txt
Ran 28 tests in 0.337s
OK
```

Archive command:

```powershell
python labs\grid_genome\darwin_archive.py --count 200 --rng-seed 818 --top-k 20 --output data\archives\map_elites_stage0.json
```

## Metrics

```json
{
  "candidate_count": 200,
  "map_elites_occupied_niches": 24,
  "map_elites_coverage": 0.192,
  "map_elites_best_fitness": 0.898214,
  "map_elites_mean_elite_fitness": 0.821066,
  "scalar_top_occupied_niches": 7,
  "scalar_top_coverage": 0.056,
  "scalar_top_best_fitness": 0.898214
}
```

## Findings

The first CPU MAP-Elites archive preserved more descriptor diversity than a
single scalar top-k selector while retaining the same best observed fitness.
That is exactly the behavior the research plan wants from `mecha_darwin`:
preserve useful families, not only the highest-scoring individual.

The current result is still a mechanics proof. Because there is no life
simulation yet, the descriptors are visual/structural rather than behavioral.
The next archive step needs a simple lifecycle simulation so archive niches can
include survival, energy stability, or interaction response.

## Decision

Keep MAP-Elites as the active `mecha_darwin` archive direction. Keep the
implementation CPU-first and internal until descriptor and fitness definitions
stabilize. QDax remains a later acceleration candidate, not a dependency.

