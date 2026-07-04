# Lab Dependency Manifest and JSON Schema Runtime Parity

Date: 2026-07-04

Status: `research_lab_dependency_manifest_jsonschema_parity_no_package_code`

## Purpose

Close the M-15 remainder from `docs/03-code_review/2026-07-04-code_review.md`
— the deliberately-deferred dependency-manifest decision — via decision
record `research/decision_records/0005-declare-lab-dependency-manifest.md`,
and unblock lab-level runtime JSON Schema validation with executable parity
evidence.

## What changed

1. **`pyproject.toml`** (new, repo root) — a PEP 735 `[dependency-groups]`
   `lab` group declaring `pydantic>=2.12` and `jsonschema>=4.26`. No
   `[project]` dependencies, no build system: the *package* dependency policy
   remains a separate blocked decision until a `packages/` import-surface
   gate exists. Provision with `uv sync --group lab`.
2. **`labs/slip_validator/jsonschema_runtime_parity.py`** (new) + test — runs
   `Draft202012Validator` over the full Stage 0 corpus and compares against
   the dependency-free validator. Result: **17/18 agreements; the single
   divergence is the documented semantic gap**
   (`slip_body_mass_bounds_reversed.json` — body-mass ordering is a semantic
   check JSON Schema cannot express), and layered validation (schema layer +
   semantic checks) yields the full correct outcome: 3/3 valid, 3/3 examples
   accepted, 12/12 failures rejected. Tests skip with a provisioning hint if
   jsonschema is absent — asserting the policy, never the environment
   (H-01 decision stands).
3. **Gate updates** — `schema_migration_gate.py` dependency decisions become
   "declared in the lab group"; `declared_dependency_manifest` and
   `lab_runtime_jsonschema_validation` move to closed;
   `package_runtime_jsonschema_validation` stays blocked.
   `slip_validator.py` derives `jsonschema_dependency_available` per run
   (was hardcoded `False`) and re-scopes its blocked states to package level.
   `pydantic_contract.py` blocked list and dependency-policy text updated.
4. **Architecture gate** — `declare_runtime_schema_validation_ready` derives
   from real `pyproject.toml` inspection (`tomllib`): the lab dependency
   group does **not** satisfy the package dependency policy, so the
   package-level claim keeps rejecting, now with evidence
   (`manifest_state: {pyproject_exists, lab_dependency_group_declared,
   package_dependencies_declared}`) instead of a hardcoded constant. Its
   `runtime_jsonschema_validation` blocked state renamed to
   `package_runtime_jsonschema_validation` for scope clarity.
5. **Stale-blocker retirement** — seven workshop SLIP gate modules dropped
   `declared_dependency_manifest` from their blocked lists (their artifact
   regeneration is deferred to the descriptor-calibration batch, which
   rebuilds the same artifacts).

## Result

```powershell
python -B -m unittest discover -s labs/slip_validator -p "test_*.py"
# Ran 18 tests - OK  (was 15; +3 parity tests)
python -B -m unittest discover -s labs/architecture -p "test_*.py"
# Ran 6 tests - OK
python -B -m unittest discover -s labs/workshop_editor -p "test_slip_*.py"
# Ran 33 tests - OK
```

Artifacts regenerated and validated: the three slip_validator stage0
artifacts, the new `data/slips/slip_jsonschema_runtime_parity_stage0.json`,
and the architecture runtime-boundary gate artifact.

## Decision

Adopt layered runtime schema validation for labs: `Draft202012Validator` as
the schema layer, the dependency-free validator's semantic checks retained on
top, `layered_ok` as the decision surface. The package dependency policy
remains explicitly blocked and is now *measured* (pyproject inspection)
rather than assumed.

## Verification

```powershell
python -B -m unittest discover -s labs/slip_validator -p "test_*.py"
python -B labs/slip_validator/jsonschema_runtime_parity.py
python -m json.tool data/slips/slip_jsonschema_runtime_parity_stage0.json
python -B labs/architecture/mecha_engine_runtime_boundary_gate.py
```

## Sources

- `docs/03-code_review/2026-07-04-code_review.md`
- `research/decision_records/0005-declare-lab-dependency-manifest.md`
- `pyproject.toml`
- `labs/slip_validator/jsonschema_runtime_parity.py`
- `labs/slip_validator/schema_migration_gate.py`
- `labs/slip_validator/slip_validator.py`
- `labs/slip_validator/pydantic_contract.py`
- `labs/architecture/mecha_engine_runtime_boundary_gate.py`
- `data/slips/slip_jsonschema_runtime_parity_stage0.json`
- `research/slip/schema_migration_dependency_gate.md`
- `research/slip/pydantic_contract.md`
