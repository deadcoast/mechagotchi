# Mecha Engine Archive Contract Gate

Date: 2026-05-12

## Status

Research acceptance gate. This document does not create or modify
`packages/mecha_engine`.

## Purpose

Define the package-level contract for the future `mecha_engine.archive` module
before MAP-Elites archive code is moved out of `labs/`.

## Source Evidence

The Stage 0 archive labs already prove:

- Baseline MAP-Elites archive: 24 occupied niches from 200 candidates.
- Baseline MAP-Elites coverage: `0.192` over a 125-niche 3D descriptor space.
- Baseline MAP-Elites best fitness: `0.898214`.
- Scalar top-k baseline: 7 occupied niches and `0.056` coverage with the same
  best fitness.
- Extended descriptor archive: 29 occupied niches from 160 candidates.
- Extended descriptor dimensions: 7.
- Extended best fitness: `0.979592`.
- Extended QD score: `27.773545`.

The package archive may adopt the archive mechanics and extended metric shape.
It must not lock final descriptor thresholds until manual readability ratings
and broader lifecycle calibration exist.

## Mathematical Contract

The archive is a quality-diversity repertoire:

```txt
descriptor = phi(candidate, metrics)
fitness = f(candidate, metrics)
niche = discretize(descriptor)
archive[niche] = argmax_fitness(candidate in niche)
```

The package contract must preserve the distinction between:

- descriptor-space diversity;
- scalar candidate fitness;
- elite replacement;
- summary metrics such as coverage, QD score, best fitness, and mean elite
  fitness.

Scalar top-k selection is a comparator, not an archive replacement.

## Required Public Surface

```python
from mecha_engine.archive import (
    archive_summary,
    build_archive,
    descriptor_for_candidate,
    insert_candidate,
    score_candidate,
)
```

Required contracts:

- `descriptor_for_candidate(candidate: dict, metrics: dict) -> tuple[int, ...]`
- `score_candidate(candidate: dict, metrics: dict) -> dict`
- `insert_candidate(archive: dict, candidate: dict, score: dict, descriptor: tuple[int, ...]) -> dict`
- `build_archive(candidates: list[dict], metrics_by_grid_id: dict) -> dict`
- `archive_summary(archive: dict) -> dict`

## Candidate Acceptance

Archive candidates must contain:

- `grid`
- `descriptor`
- `fitness`
- `fitness_components`
- `validation`
- `provenance`

Candidate grids must pass `mecha_engine.genome.validate_grid` before archive
insertion. Invalid candidates may be scored as failures for reports, but they
must not become elites.

## Descriptor Acceptance

The package must preserve a baseline 3D descriptor option:

- body mass;
- sensor count;
- symmetry.

The package must also support the current extended descriptor dimensions:

- body mass;
- sensor count;
- symmetry;
- readability;
- lifecycle survival;
- mutation stability;
- behavior neediness.

Descriptor functions must:

- return deterministic integer tuples;
- expose descriptor names and cardinalities in archive metadata;
- reject or explicitly mark missing metric inputs;
- distinguish observed occupied niches from theoretical total coverage;
- keep manual readability calibration status visible.

Manual readability ratings must be incorporated before final descriptor
thresholds are locked.

## Fitness Acceptance

`score_candidate` must return a JSON-serializable result containing:

- `fitness`
- `components`
- `validation`
- `readability`
- `lifecycle`
- `slip_alignment`
- `provenance`

The current extended fitness components are:

- survival;
- readability;
- validity;
- bond;
- mutation stability;
- SLIP alignment.

Every component and the aggregate fitness must remain inside `[0, 1]`.

## Insertion Acceptance

`insert_candidate` must:

- derive the niche key from the descriptor;
- insert a candidate when a niche is empty;
- replace an existing elite only when the new candidate has higher fitness;
- use deterministic tie handling;
- preserve the previous archive when a candidate does not win its niche;
- record enough information to audit why insertion or replacement happened.

## Summary Acceptance

`archive_summary` must report at least:

- descriptor names;
- descriptor dimensions;
- descriptor cardinalities;
- total possible niches;
- occupied niches;
- coverage;
- best fitness;
- mean elite fitness;
- QD score;
- candidate count;
- blocked or skipped candidate counts;
- readability calibration status.

The implementation-stage package gate must reproduce or intentionally update
these Stage 0 metrics with a new decision record:

| Metric | Required Stage 0 Evidence |
| --- | ---: |
| Baseline occupied niches | 24 |
| Baseline coverage | 0.192 |
| Scalar top-k occupied niches | 7 |
| Extended occupied niches | 29 |
| Extended descriptor dimensions | 7 |
| Extended best fitness | 0.979592 |
| Extended QD score | 27.773545 |

## Negative Checks

The archive package gate fails if:

- `packages/mecha_engine/src/mecha_engine/archive` imports `labs`;
- package tests import `labs`;
- package tests mutate `sys.path` to reach `labs`;
- scalar top-k replaces MAP-Elites archive mechanics;
- invalid grids can become elites;
- descriptor metadata is absent;
- theoretical coverage is compared directly across different descriptor
  dimensionalities without observed-niche context;
- proxy readability is presented as human-calibrated readability;
- final descriptor thresholds are locked before manual readability ratings are
  collected.

## Future Verification Commands

Run these after the scaffold and `archive` implementation exist:

```powershell
python -B .\labs\grid_genome\test_darwin_archive.py
python -B -m unittest discover -s .\labs\map_elites_archive -p "test_*.py"
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
python -c "from mecha_engine.archive import descriptor_for_candidate, score_candidate, insert_candidate, build_archive, archive_summary"
rg -n "from labs|import labs|labs/|labs\\|sys\\.path" .\packages\mecha_engine
python -B .\labs\package_promotion\package_promotion_gate.py --root . --output-dir .\data\package_promotion
git diff --check
```

Expected implementation-stage result:

- Lab archive tests still pass.
- Package archive tests pass through `mecha_engine.archive`.
- Package archive candidates validate through `mecha_engine.genome`.
- Package archive summaries preserve coverage, QD score, best fitness, and mean
  elite fitness.
- Scalar top-k remains a comparator only.
- Manual readability remains an explicit calibration gate.
- The package contains no runtime or test imports from `labs`.
- Package-promotion gate is rerun after package archive tests exist.

## Non-Goals

- No package creation in this research step.
- No archive implementation migration.
- No QDax/JAX dependency.
- No learned descriptor discovery.
- No final descriptor threshold lock.
- No real-player trace model.
- No frontend archive browser.

## Sources

- `research/package_specs/mecha_engine_module_interfaces.md`
- `research/algorithm_cards/map_elites.md`
- `research/algorithm_cards/map_elites_extended_descriptors.md`
- `research/experiment_reports/2026-05-12-map-elites-archive-baseline.md`
- `research/experiment_reports/2026-05-12-map-elites-extended-descriptors.md`
- `data/archives/map_elites_stage0.json`
- `data/archives/map_elites_extended_stage0.json`
- `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json`
- MAP-Elites paper:
  https://arxiv.org/abs/1504.04909
- QDax overview:
  https://qdax.readthedocs.io/en/latest/overview/
- QDax repository:
  https://github.com/adaptive-intelligent-robotics/QDax
