# SLIP Dependency Gate Environment Decoupling

Date: 2026-07-04

Status: `research_slip_dependency_gate_env_decoupled_no_package_code`

## Purpose

Fix review findings H-01 and M-15 from
`docs/03-code_review/2026-07-04-code_review.md`: two slip_validator gate tests
pinned an environment observation (`jsonschema_available == False`) instead of
the dependency policy, so the suite failed in any environment where
`jsonschema` is importable. The user site-packages installation of
`jsonschema 4.26.0` (visible to every local interpreter) surfaced the
coupling.

This change does not create package code and does not alter the Stage 0
dependency decision: runtime `jsonschema` validation remains deferred until a
repository dependency manifest exists.

## What changed

1. `labs/slip_validator/test_pydantic_contract.py` and
   `labs/slip_validator/test_schema_migration_gate.py` now assert
   `jsonschema_available` is a recorded boolean observation instead of pinning
   it `False`. The stable assertions remain: `pydantic_available` is true (the
   module imports pydantic), `dependency_manifest_present` is false (repo
   state, an intended tripwire), and the `dependency_decision` strings are
   unchanged.
2. `_module_version()` in `pydantic_contract.py` and
   `schema_migration_gate.py` now uses `importlib.metadata.version()` instead
   of the deprecated `module.__version__` access, removing a
   `DeprecationWarning` under jsonschema 4.26.0.
3. `research/slip/pydantic_contract.md`,
   `research/slip/schema_migration_dependency_gate.md`, and
   `research/slip/slip_failure_cases.md` now anchor the blocked state to the
   missing dependency manifest rather than to package absence, and mark the
   environment evidence blocks as per-run observations.

## Result

RED (before, commit `977e1d2`):

```powershell
python -B -m unittest discover -s labs/slip_validator -p "test_*.py"
# FAILED (failures=2)
# test_pydantic_contract.py:49  AssertionError: True is not false
# test_schema_migration_gate.py:24  AssertionError: True is not false
```

GREEN (after):

```powershell
python -B -m unittest discover -s labs/slip_validator -p "test_*.py"
# Ran 15 tests in 0.058s
# OK
```

Artifact regeneration (both byte-stable against the committed state, no
deprecation warnings):

```powershell
python -B labs/slip_validator/schema_migration_gate.py
python -B labs/slip_validator/pydantic_contract.py
python -m json.tool data/slips/slip_schema_migration_dependency_gate_stage0.json
python -m json.tool data/slips/slip_pydantic_contract_stage0.json
```

## Decision

Keep the Stage 0 dependency deferral policy. Gate tests assert the policy
(dependency decision strings, manifest absence) and the report shape;
environment availability fields are recorded observations that may vary by
machine. The remaining M-15 surface — authoring a dependency manifest — stays
an explicit open decision tracked in the code review TODO; it is deliberately
not made here because a manifest flips `dependency_manifest_present` and
triggers the gate revisit the migration policy defines.

## Verification

```powershell
python -B -m unittest discover -s labs/slip_validator -p "test_*.py"
python -B labs/slip_validator/schema_migration_gate.py
python -B labs/slip_validator/pydantic_contract.py
python -m json.tool data/slips/slip_schema_migration_dependency_gate_stage0.json
python -m json.tool data/slips/slip_pydantic_contract_stage0.json
```

## Sources

- `docs/03-code_review/2026-07-04-code_review.md`
- `labs/slip_validator/pydantic_contract.py`
- `labs/slip_validator/test_pydantic_contract.py`
- `labs/slip_validator/schema_migration_gate.py`
- `labs/slip_validator/test_schema_migration_gate.py`
- `data/slips/slip_pydantic_contract_stage0.json`
- `data/slips/slip_schema_migration_dependency_gate_stage0.json`
- `research/slip/pydantic_contract.md`
- `research/slip/schema_migration_dependency_gate.md`
- `research/slip/slip_failure_cases.md`
