# Experiment Report: Mecha Engine Test Fixture Manifest

Date: 2026-05-12

## Objective

Continue the package-contract research sequence by inventorying the concrete
fixtures that future `mecha_engine` package tests must use.

## Method

1. Re-read the contract traceability matrix.
2. Counted seed grids, invalid grids, generated-grid corpora, and SLIP
   profiles from the repository.
3. Re-read the lifecycle, archive, provenance, readability, and package
   promotion metric artifacts.
4. Recorded available fixtures and blocked fixture gaps in prose and JSON.

## Outputs

- `research/package_specs/mecha_engine_test_fixture_manifest.md`
- `data/architecture/mecha_engine_test_fixture_manifest_stage0.json`

## Findings

The future package tests have enough repository fixtures for the core engine
surfaces:

| Fixture | Count / Status |
| --- | ---: |
| Seed grids | 50 |
| Invalid grids | 200 |
| Random mutation candidates | 100 |
| Raw Markov candidates | 100 |
| Constrained WFC-style candidates | 100 |
| SLIP-constrained candidates | 50 |
| Lineage constrained candidates | 200 |
| Valid SLIP profiles | 3 |
| Invalid SLIP profiles | 2 |
| Provenance CI assets | 7 |
| Parsed SPDX expressions | 7 / 7 |

The critical blocked fixture remains human readability:

- `data/readability/manual_rating_template.csv` exists and has 31 lines
  including the header.
- `data/readability/manual_ratings.csv` does not exist.
- The manual rating recheck and collection gate both record
  `ratings_collected: false`.

## Decision

Adopt the fixture manifest as the package-test data inventory. Do not create
`packages/mecha_engine` or package tests in this research step.

Status: `research_fixture_manifest_no_package_code`

## Verification Targets

These checks are valid after package implementation begins:

```powershell
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
rg -n "from labs|import labs|labs/|labs\\|sys\\.path" .\packages\mecha_engine
python -B .\labs\package_promotion\package_promotion_gate.py --root . --output-dir .\data\package_promotion
```

This research step verifies fixture counts, JSON validity, and package absence.

## Sources

- `research/package_specs/mecha_engine_contract_traceability_matrix.md`
- `data/architecture/mecha_engine_contract_traceability_matrix_stage0.json`
- `data/seed_grids`
- `data/invalid_grids`
- `data/generated_grids`
- `data/slips`
- `data/lifecycle/lifecycle_stage0.json`
- `data/archives/map_elites_stage0.json`
- `data/archives/map_elites_extended_stage0.json`
- `data/asset_provenance/provenance_ci_report.json`
- `data/readability/manual_rating_recheck_stage0.json`
- `data/readability/manual_rating_collection_gate_stage0.json`
- `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json`
