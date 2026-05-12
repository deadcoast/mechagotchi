# Experiment Report: MAP-Elites Extended Descriptors

Date: 2026-05-12

## Objective

Continue the post-v0.1 research sequence by extending MAP-Elites descriptors
beyond body mass, sensor count, and symmetry.

## Source Basis

MAP-Elites stores high-performing solutions in researcher-chosen behavior-space
niches. That makes descriptor selection load-bearing: bad descriptors preserve
meaningless variation, while useful descriptors preserve distinct families. QDax
keeps the same useful architecture split between repertoire, emitter, and scoring
functions, but this lab remains CPU-first and internal.

Sources:

- https://arxiv.org/abs/1504.04909
- https://qdax.readthedocs.io/en/develop/api_documentation/core/map_elites/

## Scope

Included:

- `labs/map_elites_archive/extended_descriptors.py`
- `labs/map_elites_archive/test_extended_descriptors.py`
- retained baseline descriptor dimensions: body mass, sensor count, symmetry
- added descriptor dimensions: readability, lifecycle survival, mutation
  stability, behavior neediness
- extended fitness combining survival, readability, validity, bond, mutation
  stability, and SLIP alignment
- artifact at `data/archives/map_elites_extended_stage0.json`

Not included:

- QDax/JAX dependency
- learned descriptor discovery
- real player traces
- manual readability rating calibration
- CA/NCA repair descriptors

## Verification

RED command:

```powershell
python -B -m unittest discover -s labs\map_elites_archive -p 'test_*.py'
```

Initial result:

```txt
ModuleNotFoundError: No module named 'extended_descriptors'
```

GREEN command:

```powershell
python -B -m unittest discover -s labs\map_elites_archive -p 'test_*.py'
```

Result:

```txt
Ran 5 tests in 0.295s
OK
```

Lab command:

```powershell
python -B labs\map_elites_archive\extended_descriptors.py --output data\archives\map_elites_extended_stage0.json --count 160 --rng-seed 20260512 --lifecycle-ticks 24
```

## Descriptor Space

The extended descriptor has seven 5-bin dimensions:

```txt
(
  body_mass,
  sensor_count,
  symmetry,
  readability,
  lifecycle_survival,
  mutation_stability,
  behavior_neediness
)
```

This creates 78,125 theoretical niches. Coverage is therefore expected to be
sparse at Stage 0; the more relevant comparison is observed occupied niches
against the legacy 3D descriptor on the same candidate set.

## Fitness

The extended fitness combines:

- survival
- readability
- validity
- bond
- mutation stability
- SLIP alignment

This matches the research plan's direction:

```txt
f(x) = weighted survival + readability + bond + novelty + SLIP alignment
```

Novelty is represented indirectly in this Stage 0 lab through descriptor-space
preservation rather than a separate novelty score.

## Results

| Metric | Legacy 3D | Extended 7D |
| --- | ---: | ---: |
| Candidate count | 160 | 160 |
| Descriptor dimensions | 3 | 7 |
| Unique candidate niches | 19 | 29 |
| Occupied archive niches | 19 | 29 |
| Coverage | 0.152000 | 0.000371 |
| Best fitness | 0.910000 | 0.979592 |

Extended archive summary:

```txt
mean_elite_fitness: 0.957708
qd_score: 27.773545
```

## Findings

The extended descriptor set preserved more observed families on the same
SLIP-filtered constrained candidate set: 29 occupied niches versus 19 with the
legacy 3D descriptor. Total coverage appears lower because the extended space is
much larger, so absolute coverage is not comparable across descriptor sets.

The result supports continuing with richer descriptors, but it is not final
archive evidence. Readability is still proxy-scored, lifecycle survival is a
short synthetic probe, and behavior neediness is currently SLIP-derived when a
profile is available.

## Decision

Keep extended descriptors as `prototype`.

Use them for research comparison and future archive scoring experiments, but do
not replace the simpler baseline until manual readability ratings and broader
lifecycle tests are available.
