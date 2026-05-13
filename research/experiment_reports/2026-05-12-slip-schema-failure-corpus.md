# Experiment Report: SLIP Schema Failure Corpus

Date: 2026-05-12

## Objective

Continue the research plan's SLIP track by authoring the versioned Stage 0
machine-readable profile schema, expanding the negative profile corpus, and
recording validation evidence before any profile-authoring panel or package
code is created.

## Method

1. Re-read the SLIP section of `docs/02-research_plan.md` and the current
   compatibility matrix in `research/slip/profile_compatibility_tests.md`.
2. Inspected the current profile fixtures and the lab validator under
   `labs/grid_genome/`.
3. Checked the runtime environment for a `jsonschema` dependency. It is not
   installed, so the lab gate uses a dependency-free structural validator.
4. Used the official JSON Schema Draft 2020-12 dialect as the schema anchor and
   Pydantic v2 JSON Schema documentation as the future Python-model anchor.
5. Wrote failing tests for schema metadata, valid profile acceptance, expanded
   failure rejection, and boolean numeric rejection.
6. Implemented the minimal Stage 0 schema validator and generated the validation
   report.

## Outputs

- `research/slip/slip.schema.json`
- `research/slip/slip_examples/`
- `research/slip/slip_failure_cases.md`
- `labs/slip_validator/slip_validator.py`
- `labs/slip_validator/test_slip_validator.py`
- `data/slips/failure_cases/*.json`
- `data/slips/slip_schema_validation_stage0.json`

## Result

```txt
valid profiles accepted: 3/3
research examples accepted: 3/3
failure cases rejected: 12/12
unexpected rejections: 0
unexpected acceptances: 0
```

The failure corpus covers required fields, type errors, enum errors, range
errors, minimum item counts, additional properties, reversed body-mass bounds,
and boolean-as-numeric mistakes.

## Interpretation

The Stage 0 schema and failure corpus are now authored and executable. This
closes the prior "schema/failure corpus" gap in the profile compatibility
matrix.

This does not close the larger SLIP gate. Runtime JSON Schema validation,
behavior preview, mutation preview, and profile-weighted evolution remain
unproven. Supersession note: Pydantic-backed model generation, schema
migration, and the minimal profile-authoring panel now have separate Stage 0
reports.

## Verification

```powershell
python -B -m unittest discover -s .\labs\slip_validator -p "test_*.py"
python -B .\labs\slip_validator\slip_validator.py --valid-dir .\data\slips\valid --failure-dir .\data\slips\failure_cases --examples-dir .\research\slip\slip_examples --output .\data\slips\slip_schema_validation_stage0.json
```

## Decision

Adopt the Stage 0 schema and failure corpus as the active SLIP profile file
contract. Keep the validator under `labs/` until a runtime schema dependency,
Pydantic model boundary, and package import-surface gate are selected.

Status: `research_slip_schema_failure_corpus_no_package_code`

## References

- `docs/02-research_plan.md`
- `research/slip/profile_compatibility_tests.md`
- `research/slip/slip.schema.json`
- `research/slip/slip_examples/`
- `research/slip/slip_failure_cases.md`
- `data/slips/slip_schema_validation_stage0.json`
- JSON Schema Draft 2020-12: https://json-schema.org/draft/2020-12
- Pydantic JSON Schema docs: https://docs.pydantic.dev/latest/concepts/json_schema/
