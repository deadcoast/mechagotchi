# Mecha Engine Test Fixture Manifest

Date: 2026-05-12

## Status

Research fixture manifest. This document does not create or modify
`packages/mecha_engine` and does not create package tests.

## Purpose

Inventory the concrete fixture files and metric artifacts that future
`mecha_engine` package tests must use. The contract traceability matrix defines
what package tests must assert; this manifest defines which repository fixtures
provide the evidence.

## Fixture Summary

| Fixture Group | Path | Count / Status | Package Use |
| --- | --- | ---: | --- |
| Seed grid corpus | `data/seed_grids/*.json` | 50 files | Positive `genome.validate_grid` corpus |
| Invalid grid corpus | `data/invalid_grids/*.json` | 200 files | Negative `genome.validate_grid` corpus |
| Random mutation baseline | `data/generated_grids/random_mutation_baseline/*.json` | 100 files | Generator comparator; 42 valid / 100 |
| Raw Markov corpus | `data/generated_grids/markov_local/*.json` | 100 files | Proposal-source comparator; 13 valid / 100 |
| Constrained WFC-style corpus | `data/generated_grids/constrained_wfc_style/*.json` | 100 files | Constrained generator acceptance; 100 valid / 100 |
| SLIP-constrained corpus | `data/generated_grids/slip_lcd_seed_constrained/*.json` | 50 files | SLIP generation gate; 50 valid and aligned / 50 |
| Lineage constrained corpus | `data/generated_grids/lineage_constrained/*.json` | 200 files | Lineage and archive candidate fixture pool |
| Valid SLIP profiles | `data/slips/valid/*.json` | 3 files | Positive profile validation and generation constraints |
| Invalid SLIP profiles | `data/slips/invalid/*.json` | 2 files | Negative profile validation |
| Lifecycle report | `data/lifecycle/lifecycle_stage0.json` | present | Policy comparator and bounded episode fixture |
| Archive reports | `data/archives/*.json` | 2 files | MAP-Elites coverage, fitness, QD-score fixtures |
| Provenance reports | `data/asset_provenance/*.json` | present | SPDX, hash, attribution, and CI fixtures |
| Package promotion report | `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json` | present | Promotion-gate fixture |
| Manual rating template | `data/readability/manual_rating_template.csv` | 31 lines including header | Reviewer packet fixture |
| Manual rating results | `data/readability/manual_ratings.csv` | absent | Blocked human calibration fixture |

## Required Fixture Roles

### Genome

Future `mecha_engine.genome` package tests must use:

- `data/seed_grids/*.json` as the complete positive validation corpus;
- `data/invalid_grids/*.json` as the complete negative validation corpus;
- at least one copied in-memory payload from each corpus to verify input
  immutability.

Acceptance evidence:

- seed grids: `50`;
- invalid grids: `200`.

### Generation

Future `mecha_engine.generation` package tests must use:

- `data/generated_grids/random_mutation_baseline/*.json` as the naive
  comparator;
- `data/generated_grids/markov_local/*.json` as the raw local-probability
  comparator;
- `data/generated_grids/constrained_wfc_style/*.json` as the constrained
  validity target;
- `data/generated_grids/slip_lcd_seed_constrained/*.json` as the SLIP alignment
  target;
- `data/slips/valid/slip_lcd_seed.json` as the first positive generation
  profile;
- `data/slips/invalid/*.json` as profile rejection fixtures.

Acceptance evidence:

- random mutation validity: `42 / 100`;
- raw Markov validity: `13 / 100`;
- constrained validity: `100 / 100`;
- SLIP-constrained valid and aligned: `50 / 50`.

### Lifecycle

Future `mecha_engine.lifecycle` package tests must use:

- at least one valid seed grid from `data/seed_grids`;
- at least one invalid grid from `data/invalid_grids`;
- `data/lifecycle/lifecycle_stage0.json` for the Stage 0 policy comparator.

Acceptance evidence:

- switchboard survives `72` ticks with need balance `0.789129`;
- idle dies after `11` ticks with need balance `0.121004`;
- random dies after `21` ticks with need balance `0.236001`.

### Archive

Future `mecha_engine.archive` package tests must use:

- `data/archives/map_elites_stage0.json` for the baseline 3D archive;
- `data/archives/map_elites_extended_stage0.json` for extended descriptors;
- `data/generated_grids/lineage_constrained/*.json` as the candidate fixture
  pool where package-level candidate construction needs concrete grids;
- the package genome validator for candidate-grid acceptance.

Acceptance evidence:

- baseline archive occupied niches: `24`;
- scalar top-k occupied niches: `7`;
- extended archive occupied niches: `29`;
- extended archive best fitness: `0.979592`;
- extended archive QD score: `27.773545`.

### Provenance

Future `mecha_engine.provenance` package tests must use:

- `data/asset_provenance/ledger.json`;
- `data/asset_provenance/validation_report.json`;
- `data/asset_provenance/provenance_ci_report.json`;
- `data/asset_provenance/attribution_manifest.json`;
- actual included paths from ledger entries for hash checks.

Acceptance evidence:

- provenance CI `ok`: `true`;
- asset count: `7`;
- parsed SPDX expressions: `7 / 7`;
- included assets: `3`;
- reference-only assets: `4`;
- attribution-required assets: `3`.

### Readability

The readability fixture is intentionally blocked:

- `data/readability/manual_rating_template.csv` exists and has 31 lines
  including the header;
- `data/readability/manual_ratings.csv` does not exist;
- `data/readability/manual_rating_recheck_stage0.json` records
  `ratings_collected: false`;
- `data/readability/manual_rating_collection_gate_stage0.json` records
  `ratings_collected: false`.

No package test may claim human-calibrated readability until
`data/readability/manual_ratings.csv` exists and the manual rating intake has
been rerun.

## Fixture Gaps

The current fixture set deliberately does not include:

- package scaffold files under `packages/mecha_engine`;
- package tests under `packages/mecha_engine/tests`;
- human readability ratings;
- real CuBFF snapshot artifacts;
- release license metadata;
- SBOM or repository-wide REUSE scan output.

These gaps are blockers or non-goals, not missing examples to fake.

## Verification Commands

Fixture checks used for this manifest:

```powershell
Get-ChildItem .\data\seed_grids -Filter *.json | Measure-Object
Get-ChildItem .\data\invalid_grids -Filter *.json | Measure-Object
Get-ChildItem .\data\generated_grids -Directory
Get-ChildItem .\data\slips\valid -Filter *.json
Get-ChildItem .\data\slips\invalid -Filter *.json
Test-Path .\data\readability\manual_ratings.csv
python -m json.tool .\data\architecture\mecha_engine_test_fixture_manifest_stage0.json
git diff --check
```

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
