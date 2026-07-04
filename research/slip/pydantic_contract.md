# SLIP Pydantic Contract Gate

Date: 2026-05-12

Updated: 2026-07-04 (environment decoupling, review finding H-01)

Status: `research_slip_pydantic_contract_no_package_code`

## Purpose

Define the Stage 0 Python model boundary for SLIP profile payloads using
Pydantic v2, without creating package code or making Pydantic a package
dependency gate.

## Source Anchors

Current documentation anchors:

- Pydantic v2 supports `BaseModel.model_validate()`,
  `BaseModel.model_validate_json()`, `BaseModel.model_json_schema()`,
  `ConfigDict(extra="forbid")`, and bounded `Field` constraints.
- Python `jsonschema` supports Draft 2020-12 validation through
  `Draft202012Validator.check_schema()` and `iter_errors()`, but the
  repository defers that dependency until a dependency manifest exists.

Local environment evidence (an observation recorded per run, not a pinned
claim — `jsonschema_available` in the stage 0 artifact reflects whatever the
executing environment provides):

```txt
Pydantic: available, version 2.12.5
jsonschema: environment-dependent (missing on 2026-05-12; 4.26.0 observed 2026-07-04)
repository dependency manifest: absent
```

## Artifacts

- `labs/slip_validator/pydantic_contract.py`
- `labs/slip_validator/test_pydantic_contract.py`
- `research/slip/slip_pydantic_model.schema.json`
- `data/slips/slip_pydantic_contract_stage0.json`

## Result

```txt
valid profiles accepted: 3/3
research examples accepted: 3/3
failure cases rejected: 12/12
unexpected valid rejections: 0
unexpected example rejections: 0
unexpected failure acceptances: 0
```

Observed error families:

- `schema_additional_properties`
- `schema_enum`
- `schema_min_items`
- `schema_range`
- `schema_required`
- `schema_type`
- `semantic_body_mass_bounds`
- `semantic_numeric_bool`

The model also rejects numeric-string coercion before Pydantic can convert it,
so JSON values such as `"0.6"` do not silently pass as numbers.

## Decision

Adopt the Pydantic model as the current Stage 0 Python authoring contract. Do
not promote it into `packages/` or make it a required package dependency until a
repository dependency manifest and package import-surface gate exist.

Lab-level runtime JSON Schema validation is now unblocked: `jsonschema` is
declared in the pyproject `lab` dependency group (decision record 0005) and
`labs/slip_validator/jsonschema_runtime_parity.py` proves corpus parity with
the dependency-free validator. Package-level runtime validation stays
blocked on the package import-surface policy. Lab tests assert the
dependency policy, not the environment observation (review finding H-01).
Schema migration policy is handled separately in
`research/slip/schema_migration_dependency_gate.md`.

## Verification

```powershell
python -B -m unittest discover -s .\labs\slip_validator -p "test_pydantic_contract.py"
python -B .\labs\slip_validator\pydantic_contract.py
python -m json.tool .\research\slip\slip_pydantic_model.schema.json
python -m json.tool .\data\slips\slip_pydantic_contract_stage0.json
```

## References

- `docs/02-research_plan.md`
- `research/slip/slip.schema.json`
- `research/slip/slip_failure_cases.md`
- `data/slips/slip_schema_validation_stage0.json`
- Pydantic JSON Schema docs: https://docs.pydantic.dev/latest/concepts/json_schema/
- Pydantic models docs: https://docs.pydantic.dev/latest/concepts/models/
- Python jsonschema validation docs: https://python-jsonschema.readthedocs.io/en/v4.22.0/validate/
