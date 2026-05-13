# SLIP Schema Migration and Dependency Gate

Date: 2026-05-12

Status: `research_slip_schema_migration_dependency_gate_no_package_code`

## Purpose

Define the Stage 0 schema migration policy and runtime dependency decision for
SLIP profiles before minimal profile-authoring panel work continues.

This gate does not create package code, package tests, package dependencies, or
a package root.

## Source Anchors

Current documentation anchors:

- JSON Schema Draft 2020-12 remains the machine-readable schema dialect.
- Python `jsonschema` exposes `Draft202012Validator.check_schema()` and
  `iter_errors()` for runtime schema validation, but the package is not
  installed or declared here.
- Pydantic v2 remains the lab Python model path and can emit JSON Schema through
  `model_json_schema()`.

Local environment evidence:

```txt
Pydantic: available, version 2.12.5
jsonschema: missing
repository dependency manifest: absent
packages/: absent
```

## Artifacts

- `labs/slip_validator/schema_migration_gate.py`
- `labs/slip_validator/test_schema_migration_gate.py`
- `data/slips/slip_schema_migration_dependency_gate_stage0.json`

## Result

Schema-surface comparison between the authored schema and generated Pydantic
schema found no core mismatches for:

- required top-level fields;
- palette enum values;
- organ-role enum values;
- required mutation keys;
- required behavior keys;
- required survival-weight keys;
- extra-property rejection.

Migration policy:

```txt
0.1.0 profile -> accept current, no migration
missing version -> reject before validation
non-string version -> reject before validation
unknown version -> reject before validation
implicit upgrade -> forbidden
implicit downgrade -> forbidden
lossy migration -> forbidden
```

Future migration requires a new schema id, explicit source and target versions,
source/target fixture corpora, a loss report, and validator parity evidence.

## Decision

Close the Stage 0 schema migration policy for the current `0.1.0` corpus.

Keep runtime JSON Schema validation blocked until the repository has an
explicit dependency manifest and package import-surface policy. Continue using
the dependency-free checker and Pydantic lab contract for research-stage
profile validation.

## Verification

```powershell
python -B -m unittest discover -s .\labs\slip_validator -p "test_schema_migration_gate.py"
python -B .\labs\slip_validator\schema_migration_gate.py
python -m json.tool .\data\slips\slip_schema_migration_dependency_gate_stage0.json
```

## References

- `docs/02-research_plan.md`
- `research/slip/slip.schema.json`
- `research/slip/slip_pydantic_model.schema.json`
- `research/slip/pydantic_contract.md`
- `data/slips/slip_pydantic_contract_stage0.json`
- JSON Schema Draft 2020-12: https://json-schema.org/draft/2020-12
- Python jsonschema validation docs: https://python-jsonschema.readthedocs.io/en/v4.22.0/validate/
- Pydantic JSON Schema docs: https://docs.pydantic.dev/latest/concepts/json_schema/
