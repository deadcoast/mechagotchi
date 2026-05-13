# Experiment Report: Mecha Engine Contract Traceability Matrix

Date: 2026-05-12

## Objective

Continue the package-contract research sequence by translating the scaffold and
module contract gates into future package test obligations without creating
`packages/mecha_engine`.

## Method

1. Re-read the v0.5 package-contract handoff report.
2. Re-read the scaffold, genome, generation, lifecycle, archive, and
   provenance contract gates.
3. Extracted each gate's implementation-stage assertions and negative checks.
4. Grouped assertions into future package test files.
5. Wrote a prose traceability matrix and a machine-readable architecture
   artifact.

## Outputs

- `research/package_specs/mecha_engine_contract_traceability_matrix.md`
- `data/architecture/mecha_engine_contract_traceability_matrix_stage0.json`

## Findings

The next package implementation step cannot be treated as a single generic
"make package tests pass" task. The gates imply an ordered test stack:

1. scaffold imports;
2. genome validation;
3. generation through the package genome API;
4. lifecycle simulation after package genome validation;
5. archive insertion after package candidate validation;
6. provenance CI independent of lab imports;
7. package-promotion gate rerun.

This ordering prevents the package from copying lab behavior without proving
the import boundary and prevents later modules from bypassing `genome` as the
core validation authority.

## Decision

Adopt the traceability matrix as the package test checklist for future
implementation work. Do not create `packages/mecha_engine` in this research
step.

Status: `research_traceability_matrix_no_package_code`

## Verification Targets

These checks are valid after package implementation begins:

```powershell
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
python -c "import mecha_engine, mecha_engine.genome, mecha_engine.generation, mecha_engine.lifecycle, mecha_engine.archive, mecha_engine.provenance"
rg -n "from labs|import labs|labs/|labs\\|sys\\.path" .\packages\mecha_engine
python -B .\labs\package_promotion\package_promotion_gate.py --root . --output-dir .\data\package_promotion
```

This research step only verifies the new matrix artifacts and the continued
absence of package code.

## Sources

- `research/reports/mechagotchi_research_report_v0_5.md`
- `research/package_specs/mecha_engine_scaffold_verification_gate.md`
- `research/package_specs/mecha_engine_genome_contract_gate.md`
- `research/package_specs/mecha_engine_generation_contract_gate.md`
- `research/package_specs/mecha_engine_lifecycle_contract_gate.md`
- `research/package_specs/mecha_engine_archive_contract_gate.md`
- `research/package_specs/mecha_engine_provenance_contract_gate.md`
- `data/architecture/mecha_engine_scaffold_verification_gate_stage0.json`
- `data/architecture/mecha_engine_genome_contract_gate_stage0.json`
- `data/architecture/mecha_engine_generation_contract_gate_stage0.json`
- `data/architecture/mecha_engine_lifecycle_contract_gate_stage0.json`
- `data/architecture/mecha_engine_archive_contract_gate_stage0.json`
- `data/architecture/mecha_engine_provenance_contract_gate_stage0.json`
