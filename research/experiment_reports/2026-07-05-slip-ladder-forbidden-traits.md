# Experiment Report: SLIP Schema Ladder Rung T3.1 — forbidden_traits

Date: 2026-07-05

## Objective

Execute the first rung of the SLIP schema extension ladder (decision
record 0012, audit task T3.1): the og "forbidden traits" field, fully
enforced, across all four validation surfaces, without touching the
frozen v0.1.0 baseline the promoted modules consume.

## Design

- Dual-version authority: `slip_version` enum {0.1.0, 0.2.0};
  `forbidden_traits` ({roles?, materials?}, at least one, vocabulary
  mirrored from the grid genome schema minus empty/void and pinned by
  test) is legal only under 0.2.0.
- Enforcement in `is_grid_aligned`: forbidden roles/materials present in
  a grid fail alignment with the offending values named. Live everywhere
  the lab authority runs: workshop chips, slip-creator fit counts, the
  T1 wire's founder admission.
- Contradiction guard: forbidding the cell role a required organ role
  implies is a validation error (all four surfaces agree).
- Package boundary (DR 0012 rule 4): v0.2 profiles are deliberately
  rejected by `mecha_engine.generation`/`lifecycle` until a port DR.

## Verification

RED: `test_slip_forbidden_traits.py` — ImportError (FORBIDDABLE_ROLES),
then fixture failures. GREEN, all surfaces:

```txt
labs/grid_genome      Ran 91 tests  OK   (incl. 13 new rung tests + corpus pins 14 failure / 4 valid / 4 example)
labs/slip_validator   Ran 18 tests  OK   (duplicate validator + pydantic mirror + jsonschema parity)
workshop/tests        Ran 32 tests  OK   (2 new ladder endpoint tests; v2 profile validates + binds)
packages tests        Ran 235 tests OK   (the v0.1 boundary intact)
```

## Findings

1. The ladder mechanism works: additive optional fields under a version
   gate cost the frozen baseline nothing (all pinned artifacts and
   parity suites unchanged).
2. The ladder legalized one old failure fixture's "bad version" (0.2.0)
   — updated to 9.9.9, preserving the fixture's intent. Honest ripple,
   recorded.
3. The required/forbidden contradiction is a semantic check JSON Schema
   cannot express — registered as the second known semantic-gap case in
   the jsonschema parity lab (with body-mass ordering).
4. The workshop slip creator authors the field with role/material
   toggles and writes `slip_version` automatically (0.1.0 when unused —
   maximum compatibility; 0.2.0 otherwise).

## Decision

Rung T3.1 complete. Next rungs per DR 0012: T3.2 `risk_tolerances`
(lifecycle/switchboard consumers) onward; the package port DR unlocks
v0.2 profiles for simulations when the ladder stabilizes.

## Sources

- `research/decision_records/0012-slip-schema-extension-ladder.md`
- `labs/grid_genome/slip.py`, `labs/grid_genome/test_slip_forbidden_traits.py`
- `labs/slip_validator/slip_validator.py`, `labs/slip_validator/pydantic_contract.py`, `labs/slip_validator/jsonschema_runtime_parity.py`
- `research/slip/slip.schema.json`, `research/slip/slip_pydantic_model.schema.json`
- `data/slips/valid/slip_v2_no_shell.json`, `data/slips/failure_cases/slip_v1_with_forbidden_traits.json`, `data/slips/failure_cases/slip_v2_forbids_required.json`
- `workshop/slip_creator/slip_creator.html`, `workshop/tests/test_workshop_server.py`
