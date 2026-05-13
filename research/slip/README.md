# SLIP Research

This folder holds research-stage SLIP profile compatibility artifacts.

`SLIP` is the user-authored constraint and prior layer. Research here must
prove that profiles can guide generation, lifecycle behavior, archive
descriptors, and workshop authoring without replacing the autonomous engine.

Published artifacts:

- `slip.schema.json` - Stage 0 Draft 2020-12 SLIP profile schema for current
  valid fixtures and negative profile cases.
- `slip_examples/` - research-facing examples for the three current valid
  Stage 0 profiles.
- `slip_failure_cases.md` - failure-corpus explanation, observed error
  families, and blocked runtime/schema-model states.
- `pydantic_contract.md` - Stage 0 Pydantic model gate for the current SLIP
  profile corpus, generated schema, and dependency policy.
- `schema_migration_dependency_gate.md` - Stage 0 migration policy and runtime
  dependency decision for current SLIP schemas.
- `profile_compatibility_tests.md` - Stage 0 compatibility matrix for current
  SLIP fixtures, lab validator behavior, known proven surfaces, and blocked
  future compatibility tests.
- `../experiment_reports/2026-05-12-slip-authoring-panel.md` - report proving
  the current minimal workshop profile-authoring panel can draft current
  `0.1.0` profiles through the dependency-free validator, Pydantic contract,
  and migration gate.
- `../experiment_reports/2026-05-12-slip-behavior-mutation-preview-gate.md`
  - report proving current valid profiles can drive deterministic behavior
  previews and bounded mutation previews while invalid preview probes are
  rejected before activation.
- `../experiment_reports/2026-05-12-slip-schema-failure-corpus.md` - report
  proving 3 valid profiles accepted and 12 authored failure cases rejected by
  the dependency-free Stage 0 schema validator.
- `../experiment_reports/2026-05-12-slip-pydantic-contract-gate.md` - report
  proving the current Pydantic v2 lab model accepts the valid/example corpus,
  rejects the failure corpus, and emits a JSON Schema mirror.
- `../experiment_reports/2026-05-12-slip-schema-migration-dependency-gate.md`
  - report closing the Stage 0 migration policy and deferring runtime
  `jsonschema` until dependency declaration exists.
- `../experiment_reports/2026-05-12-slip-multi-profile-generation-benchmark.md`
  - benchmark proving the current constrained generator can produce valid,
  aligned corpora for all current valid Stage 0 profiles.
