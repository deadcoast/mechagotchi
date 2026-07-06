# Experiment Report: SLIP Schema Ladder Rung T3.2 — risk_tolerances

Date: 2026-07-05

## Objective

Second ladder rung (DR 0012, audit T3.2), consumer-first per the ladder
law and the thread census's design: a v0.2 profile's mutation risk
tolerance measurably changes switchboard behavior.

## Design

- Field: `risk_tolerances: {mutation: 0..1}` (0.2.0-only, all four
  validation surfaces).
- Consumer chain: lab lifecycle stashes `state["risk_tolerance_mutation"]`
  for v0.2 profiles (v0.1 states byte-identical; `advance_tick`'s
  deepcopy propagates it) → `mutation_risk_scorer` uses the tolerance as
  the risk level where mutation utility flips negative — the historical
  constant 0.35 IS the baseline tolerance, so absent ⇒ bit-for-bit
  frozen behavior, and explicit 0.35 is utility-identical (pinned).
- Semantics, measured by test: mutate utility is monotone in tolerance
  under a stressed state (0.1 < 0.35 < 0.9) — risk-tolerant species
  keep mutating under stress, risk-averse species freeze; the thread's
  explanation surfaces the tolerance when set.
- Workshop: a tolerance slider (off ⇒ field omitted ⇒ v0.1) in the
  slip creator's ladder panel.

## Verification

RED: unknown ladder key / missing consumer (8 tests). GREEN:

```txt
labs/grid_genome    Ran 99 tests   OK  (8 new rung tests; census alias)
labs/lifecycle_sim  Ran 13 tests   OK  (v0.1 state untouched)
labs/slip_validator Ran 18 tests   OK  (all four surfaces agree)
workshop/tests      Ran 32 tests   OK
packages tests      Ran 235 tests  OK  (learning decide parity intact)
```

## Findings

1. The census-designed consumer pattern works and generalizes: optional
   state keys the frozen flows never set give ladder fields real
   engine semantics at zero parity cost. T3.3 `learning_switches` uses
   the same pattern (thread gating).
2. The v2 showcase fixture (`slip_v2_no_shell`) now carries both ladder
   fields — corpus counts unchanged, cross-validator agreement green.

## Sources

- `research/decision_records/0012-slip-schema-extension-ladder.md`
- `research/micro_learners/thread_census.md`
- `labs/grid_genome/slip.py`, `labs/grid_genome/micro_switchboard.py`, `labs/grid_genome/test_slip_risk_tolerances.py`
- `labs/lifecycle_sim/lifecycle_sim.py`
- `labs/slip_validator/slip_validator.py`, `labs/slip_validator/pydantic_contract.py`
- `research/slip/slip.schema.json`, `research/slip/slip_pydantic_model.schema.json`
- `workshop/slip_creator/slip_creator.html`
