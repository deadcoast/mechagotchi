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
- `../experiment_reports/2026-05-12-slip-lifecycle-archive-effects.md`
  - report proving current preview signals can be connected to measured
  lifecycle and extended archive effects while invalid or mismatched probes are
  rejected before effects start.
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
- `../experiment_reports/2026-07-04-slip-dependency-gate-env-decoupling.md`
  - report decoupling the dependency-gate tests from environment state:
  `jsonschema_available` is a recorded observation, the pinned claim is the
  dependency-manifest deferral policy (review finding H-01).
- `../experiment_reports/2026-07-04-lab-dependency-manifest-and-jsonschema-parity.md`
  - report closing the dependency-manifest decision (record 0005): pyproject
  lab dependency group declared, and lab-level runtime JSON Schema validation
  proven by corpus parity (17/18 agreements; the one divergence is the
  documented body-mass semantic gap retained by the layered checks).
- `../experiment_reports/2026-07-04-slip-lab-validator-alignment.md`
  - report aligning the grid_genome lab validator with the authoritative
  contract: exact key sets, boolean/pattern/uniqueness checks, typed
  misalignment errors, and a pinned cross-validator agreement test over the
  full corpus (review findings H-02, M-05, M-06).

## 2026-10-04: Covenant mechanics rung (DR 0063)

Only SLIP `0.2.0` accepts the optional `mechanics` object:

```json
"mechanics": {"cleanliness": true}
```

Its only supported key is `cleanliness`, a strict JSON boolean. Absence, `{}`,
or false means off. Null, unknown keys, numbers and strings are invalid.
Frozen `0.1.0` rejects the whole block, including `{}`. The engine's optional
`mechanics` keyword overrides the validated profile: None inherits, an empty
sequence disables, and `("cleanliness",)` enables. Invalid profiles are still
refused when an override is supplied.

Current fixture census: **5 valid / 15 malformed / 5 examples**. Earlier
reports retain their measured corpus sizes; this rung does not regenerate
their observations. The new matrix tests 32 cases across the authored schema,
committed generated schema, Pydantic and all three stdlib validators.
The game entry point and isolated-save example are in `game/README.md`.

## Sources

- `research/decision_records/0063-covenant-mechanics-authorship.md`
- `research/experiment_reports/2026-10-04-slip-mechanics-authorship.md`
- `data/slips/mechanics_cases_stage0.json`
- `data/slips/valid/slip_v2_cleanliness.json`
- `data/slips/failure_cases/slip_mechanics_numeric_boolean.json`
- `labs/slip_validator/mechanics_contract.py`
