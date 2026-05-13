# Experiment Report: Mecha Engine Archive Contract Gate

Date: 2026-05-12

## Objective

Define the acceptance contract for the future `mecha_engine.archive` package
module before moving MAP-Elites archive code out of `labs/`.

## Method

1. Re-read the research plan's quality-diversity and `mecha_darwin` archive
   sections.
2. Re-read the `mecha_engine` module interface spec.
3. Re-read the MAP-Elites baseline and extended descriptor reports.
4. Re-read the archive lab source and tests.
5. Checked current public references for MAP-Elites and QDax architecture.
6. Wrote a prose gate and a machine-readable architecture artifact.

## Outputs

- `research/package_specs/mecha_engine_archive_contract_gate.md`
- `data/architecture/mecha_engine_archive_contract_gate_stage0.json`

## Findings

The archive package boundary is mathematically specific: it must preserve a
quality-diversity repertoire, not a scalar winner list.

```txt
descriptor = phi(candidate, metrics)
fitness = f(candidate, metrics)
niche = discretize(descriptor)
archive[niche] = argmax_fitness(candidate in niche)
```

The baseline archive showed the intended difference from scalar top-k:

| Metric | MAP-Elites | Scalar top-k |
| --- | ---: | ---: |
| occupied niches | 24 | 7 |
| coverage | 0.192 | 0.056 |
| best fitness | 0.898214 | 0.898214 |

The extended descriptor lab improved observed family preservation on the same
candidate set:

| Metric | Legacy 3D | Extended 7D |
| --- | ---: | ---: |
| occupied niches | 19 | 29 |
| best fitness | 0.910000 | 0.979592 |
| QD score | n/a | 27.773545 |

The package promotion gate already marks `map_elites_archive` as
`ready_for_package_design`, with blockers only for the absent package root and
target package. That does not mean final descriptor thresholds are solved:
manual readability ratings and broader lifecycle tests are still required
before descriptor bins and fitness weights can be locked.

Supersession note: SLIP runtime selection now chooses profile-weighted archive
elites from the extended archive in
`research/experiment_reports/2026-05-13-slip-runtime-selection-policy.md`.
This still does not define offspring mutation or lineage replacement.

The required public surface is:

```python
from mecha_engine.archive import (
    archive_summary,
    build_archive,
    descriptor_for_candidate,
    insert_candidate,
    score_candidate,
)
```

## Decision

Adopt the archive contract gate as the package acceptance checklist for the
future `mecha_engine.archive` module. Do not create `packages/mecha_engine` in
this research step.

Status: `research_archive_contract_gate_no_package_code`

## Verification Targets

These checks are valid after package implementation begins:

```powershell
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
python -c "from mecha_engine.archive import descriptor_for_candidate, score_candidate, insert_candidate, build_archive, archive_summary"
rg -n "from labs|import labs|labs/|labs\\|sys\\.path" .\packages\mecha_engine
python -B .\labs\package_promotion\package_promotion_gate.py --root . --output-dir .\data\package_promotion
```

This research step only verifies the new gate artifacts and existing archive
lab evidence.

## Sources

- `research/package_specs/mecha_engine_module_interfaces.md`
- `research/algorithm_cards/map_elites.md`
- `research/algorithm_cards/map_elites_extended_descriptors.md`
- `research/experiment_reports/2026-05-12-map-elites-archive-baseline.md`
- `research/experiment_reports/2026-05-12-map-elites-extended-descriptors.md`
- `research/experiment_reports/2026-05-13-slip-runtime-selection-policy.md`
- `data/archives/map_elites_stage0.json`
- `data/archives/map_elites_extended_stage0.json`
- `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json`
- MAP-Elites paper:
  https://arxiv.org/abs/1504.04909
- QDax overview:
  https://qdax.readthedocs.io/en/latest/overview/
- QDax repository:
  https://github.com/adaptive-intelligent-robotics/QDax
