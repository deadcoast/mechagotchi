# 0005 - Declare the Lab Dependency Manifest

Date: 2026-07-04

Status: accepted

## Context

Stage 0 policy deferred all dependency declaration
("defer_python_jsonschema_until_dependency_manifest_exists" in
`labs/slip_validator/schema_migration_gate.py`). The 2026-07-04 code review
(`docs/03-code_review/2026-07-04-code_review.md`, findings H-01 and M-15)
showed the environment had moved underneath that deferral: pydantic was
already a de-facto lab dependency (`pydantic_contract.py` hard-imports it),
and a user site-packages installation of jsonschema flipped recorded gate
outcomes on machines the policy never anticipated. Batch 1 made the gates
record availability as an observation instead of pinning it, but the
underlying question — declare or keep deferring — remained open.

## Decision

Declare a **lab** dependency manifest: `pyproject.toml` with a PEP 735
`[dependency-groups]` `lab` group (`pydantic>=2.12`, `jsonschema>=4.26`) and
no `[project]` dependencies and no build system.

Scope boundaries, deliberately:

1. The lab group declares what some labs import. Stdlib-only remains the
   default convention for lab code.
2. The **package** dependency policy stays blocked: `[project]` carries no
   dependencies, and the architecture runtime-boundary gate now derives its
   `declare_runtime_schema_validation_ready` probe from real pyproject
   inspection — it keeps rejecting the package-level claim until a
   `packages/` import-surface gate exists.
3. Runtime JSON Schema validation is unblocked at the **lab** level only,
   with executable evidence: `labs/slip_validator/jsonschema_runtime_parity.py`
   proves `Draft202012Validator` agrees with the dependency-free Stage 0
   validator over the full corpus, and records the known semantic gap
   (body-mass ordering is a semantic check the JSON Schema cannot express, so
   the layered semantic checks stay on top).

## Consequences

- `dependency_manifest_present` flips to true in the schema-migration gate;
  its dependency decisions become "declared in the lab group" and
  `declared_dependency_manifest` / `runtime_jsonschema_validation` move from
  blocked to closed at lab scope.
- The stale `declared_dependency_manifest` blocked entries across the
  workshop SLIP gate reports are retired.
- Environment-availability fields (`jsonschema_available` etc.) remain
  per-run observations; tests assert the policy, never the environment
  (decision from finding H-01 stands).
- Package-scoped blocked states (`declared_pydantic_package_dependency`,
  package runtime schema validation) remain blocked until `packages/`
  exists.

## Sources

- `docs/03-code_review/2026-07-04-code_review.md`
- `pyproject.toml`
- `labs/slip_validator/schema_migration_gate.py`
- `labs/slip_validator/jsonschema_runtime_parity.py`
- `research/experiment_reports/2026-07-04-slip-dependency-gate-env-decoupling.md`
- `research/slip/schema_migration_dependency_gate.md`
