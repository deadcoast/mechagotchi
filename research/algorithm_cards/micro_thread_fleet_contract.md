# Algorithm Card: Micro-Thread Fleet Contract

## Purpose

The ONE interface the documented ~11-thread micro-learner fleet grows
through (gap-analysis Phase D, the owner's core ML thesis), plus the
switchboard's additive confidence seam — so every predictor D2–D4
builds plugs into the same arbitration without ever touching the
frozen, parity-pinned baseline (the phase's ablation control).

## Mathematical Basis

- A fleet thread is `(name, observe, signal)`:
  `observe: (thread_state, lifecycle_state) → thread_state'` (the
  online learning step — pure, deterministic, bounded memory);
  `signal: (thread_state, lifecycle_state) → {name, input, output,
  confidence ∈ [0,1], explanation, effects}`.
- Arbitration is the switchboard's existing additive rule, unchanged:
  `utility[a] = 0.05·[a=idle] + Σ_threads effects[a] × confidence`.
- THE OPT-IN RULE: historical threads run on `learning_switches`
  absent-or-True; fleet threads run only on explicit
  `learning_switches[name] is True` — the identity element of the
  seam, proving byte-identity on every non-opted path.
- Pipe cleaner (`hunger_forecast`): mean-delta slope over an 8-sample
  hunger window; `predicted = clamp(last + slope)`; confidence =
  fill-ratio × (0.4 + 0.6·trend-consistency); anticipatory feed
  effect `0.5 × max(0, predicted − 0.55)` — fires before the reactive
  mood thread's 0.65 threshold.

## Inputs

- The live lifecycle state (the engine's own history — never invented
  data); per-thread memory in `lifecycle_state["thread_states"][name]`
- A profile opt-in via `learning_switches`

## Outputs

- Thread dicts riding `decision["threads"]` and the utility table;
  `data/micro_threads/micro_thread_fleet_contract_stage0.json`

## Strengths

- Zero cost where nothing opts in: 48/48 frozen replay decisions
  byte-identical lab-and-package, zero fleet appearances; all 19 lab
  suites + 291 package tests green with the seam live
- Cold start is honest (confidence 0, no effects) — no invented signal
- Observe/decide division of labor preserved: `decide` stays a pure
  read; learning mechanics stay in the episode loop (DR 0009)

## Weaknesses

- One thread of ~11 — the contract is proven, the fleet is not built
- Effect magnitudes are uncalibrated: at LCD scale the anticipatory
  signal moves utilities (26/48 ticks) but never flips the decision —
  D2's calibration-on-replayed-histories assignment

## Failure Modes

- A thread emitting unbounded memory or non-JSON state breaks the
  contract — pinned by the purity/serializability/bound tests
- A future flow setting a fleet name True without understanding the
  seam changes decisions by design — that is the opt-in, not a bug

## Integration Risk

Low: the seam is one additive line in each switchboard; the package
twin is a verbatim port pinned by lab-side parity tests.

## License Status

Original stdlib-only code, Apache-2.0.

## Prototype Result

13 tests green. Frozen arm 48/48 identical, 0 fleet appearances;
opted-in arm first anticipatory signal tick 2 vs reactive threshold
tick 4, utilities moved 26/48 ticks, max confidence 0.914, 1 honest
cold-start-silent tick, 0 decision flips (recorded).

## Decision

**Adopt as the D1 contract.** Go gate for D2: each need predictor
proves itself against replayed lifecycle traces with calibrated
confidence through this exact interface.

## Sources

- `labs/micro_threads/thread_fleet.py` (+ `test_thread_fleet.py`)
- `data/micro_threads/micro_thread_fleet_contract_stage0.json`
- `research/experiment_reports/2026-07-08-micro-thread-fleet-contract.md`
- `labs/grid_genome/micro_switchboard.py`
- `packages/mecha_engine/src/mecha_engine/learning/_switchboard.py`, `threads.py`
- `research/decision_records/0009-create-mecha-engine-learning-target.md`
- `audits/TODO.md` (cycle 12 D1), `docs/gap-analysis.md` (Phase D)
