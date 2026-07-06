# Experiment Report: SLIP Schema Ladder Rung T3.3 — learning_switches

Date: 2026-07-05

## Objective

Third ladder rung (DR 0012, audit T3.3): the og "learning toggles" —
profile-authored gates over the switchboard's intelligence threads —
consumer-first per the census's design. A deliberate side effect: this
is T19's remove-one ablation harness, profile-authored instead of
code-forked.

## Design

- Field: `learning_switches: {<thread_name>: bool}` (non-empty, names
  pinned to `SWITCHBOARD_THREAD_NAMES`, 0.2.0-only, all four validation
  surfaces).
- Consumer: `run_switchboard` gains a thread registry
  (`SWITCHBOARD_THREADS`, frozen execution order) and skips threads
  switched off; absent key or `true` = on, so every v0.1 flow runs all
  four threads bit-for-bit (pinned: absent vs all-true byte-identical).
- All-off is the og "rules-only baseline": no threads, idle wins its
  0.05 base utility (pinned) — exactly the comparator T19's ablation
  needs.
- Lifecycle stashes the switches into state for v0.2 profiles only;
  the thread-name mirrors in both validators pin against the
  switchboard registry by test.
- Workshop: per-thread on/off toggles in the slip creator's ladder
  panel; only OFF entries are written (field omitted when all on).

## Verification

RED (registry/gating absent) → GREEN:

```txt
labs/grid_genome    Ran 108 tests  OK  (9 new rung tests)
labs/lifecycle_sim  Ran 13 tests   OK
labs/slip_validator Ran 18 tests   OK
workshop/tests      Ran 32 tests   OK
packages tests      Ran 235 tests  OK  (learning decide parity intact)
```

## Findings

1. Three rungs in, the pattern is stable: optional state keys + version
   gate + consumer = og scope restored at zero parity cost.
2. T19's ablation conditions are now SLIP profiles: full switchboard,
   remove-one (4 profiles), rules-only — the harness half of that task
   shipped here for free.

## Sources

- `research/decision_records/0012-slip-schema-extension-ladder.md`
- `research/micro_learners/thread_census.md`
- `labs/grid_genome/micro_switchboard.py`, `labs/grid_genome/slip.py`, `labs/grid_genome/test_slip_learning_switches.py`
- `labs/lifecycle_sim/lifecycle_sim.py`
- `labs/slip_validator/slip_validator.py`, `labs/slip_validator/pydantic_contract.py`
- `research/slip/slip.schema.json`, `research/slip/slip_pydantic_model.schema.json`
- `workshop/slip_creator/slip_creator.html`
