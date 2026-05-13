# Experiment Report: SLIP Schema Migration and Dependency Gate

Date: 2026-05-12

## Objective

Continue the SLIP research plan by resolving the schema migration policy and
runtime dependency decision that remained after the schema and Pydantic contract
gates.

## Method

1. Re-read `docs/02-research_plan.md`,
   `research/slip/profile_compatibility_tests.md`, and current SLIP gate
   reports.
2. Refreshed primary documentation anchors for JSON Schema Draft 2020-12,
   Python `jsonschema`, and Pydantic v2.
3. Measured local runtime state: Pydantic is available, `jsonschema` is missing,
   no dependency manifest exists, and `packages/` is absent.
4. Wrote failing migration/dependency tests before implementation.
5. Added a lab-only gate that compares authored and Pydantic schema surfaces,
   evaluates version migration requests, records dependency policy, and writes a
   machine-readable report.

## Outputs

- `labs/slip_validator/schema_migration_gate.py`
- `labs/slip_validator/test_schema_migration_gate.py`
- `research/slip/schema_migration_dependency_gate.md`
- `data/slips/slip_schema_migration_dependency_gate_stage0.json`

## Result

```txt
schema surface mismatches: 0
current version accepted: 0.1.0 -> 0.1.0, no migration
missing version: rejected before validation
non-string version: rejected before validation
unknown version: rejected before validation
Pydantic available: yes, 2.12.5
jsonschema available: no
dependency manifest: absent
packages/: absent
```

## Interpretation

The Stage 0 migration policy is now explicit and conservative: no implicit
upgrade, no implicit downgrade, and no lossy migration. Since only `0.1.0`
exists, the only valid action is accepting current profiles with no conversion.

Runtime JSON Schema validation remains blocked. The correct package-level
decision cannot be made without an explicit dependency manifest and package
import-surface policy.

## Decision

Adopt the Stage 0 schema migration policy and defer Python `jsonschema` as a
runtime dependency until dependency declaration work exists.

Status: `research_slip_schema_migration_dependency_gate_no_package_code`

## Verification

```powershell
python -B -m unittest discover -s .\labs\slip_validator -p "test_schema_migration_gate.py"
python -B .\labs\slip_validator\schema_migration_gate.py
```

## References

- `docs/02-research_plan.md`
- `research/slip/profile_compatibility_tests.md`
- `research/slip/schema_migration_dependency_gate.md`
- `data/slips/slip_schema_migration_dependency_gate_stage0.json`
- JSON Schema Draft 2020-12: https://json-schema.org/draft/2020-12
- Python jsonschema validation docs: https://python-jsonschema.readthedocs.io/en/v4.22.0/validate/
- Pydantic JSON Schema docs: https://docs.pydantic.dev/latest/concepts/json_schema/
