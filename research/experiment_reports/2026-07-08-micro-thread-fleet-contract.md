# Experiment Report: The Thread Contract + The Confidence Seam (Cycle 12 · ENGINE · D1)

Date: 2026-07-08

## WHY

The gap table's micro-learner row is the owner's core ML thesis: ~11
named threads each streaming confidence into the switchboard, and ~2
exist. Before any predictor can be built (D2–D4), the fleet needs ONE
contract to grow through and the switchboard needs a seam that accepts
confidence-weighted signals WITHOUT disturbing the frozen baseline —
the promoted switchboard is the parity-pinned ablation control for the
whole phase, so the seam must cost exactly zero on every existing path.

## WHAT

`labs/micro_threads/thread_fleet.py` (RED-first; 13 tests) — the fleet
contract and the first thread as the end-to-end pipe cleaner:

- **The contract.** A fleet thread is `(name, observe, signal)`:
  `observe(thread_state, lifecycle_state) → new thread_state` is the
  online learning step (pure, deterministic, JSON-serializable, BOUNDED
  memory, called by the episode loop per tick — never by the
  switchboard, whose `decide` stays a pure read); `signal(...)` emits
  the same `{name, input, output, confidence, explanation, effects}`
  shape the historical threads emit, additively combined as
  `effects × confidence`. Thread memory lives in
  `lifecycle_state["thread_states"][name]`.
- **THE OPT-IN RULE (load-bearing).** Historical threads run on
  `learning_switches` absent-or-True; fleet threads run ONLY on an
  explicit `learning_switches[name] is True`. No existing flow sets a
  fleet name, so every frozen path is byte-identical until a profile
  opts in.
- **The seam.** `run_switchboard` (lab) and `decide` (package) gain one
  additive line: `threads.extend(fleet_signals(state))`. The package
  twin `mecha_engine/learning/threads.py` is pinned by the lab-side
  tests (lab decision == package decision, with and without opt-in).
- **The pipe cleaner.** `hunger_forecast` — an online forecaster over
  the companion's own hunger history. It anticipates: feed utility
  rises when *predicted* hunger crosses 0.55, before the reactive mood
  thread's 0.65 threshold trips. Cold start is honest: confidence 0,
  no effects, no invented signal. (D2 upgraded its internals to the
  bucket-conditional delta learner and re-verified every D1 gate; the
  numbers below are the re-measured ones — see the D2 report.)

## FINDINGS (two-arm 48-tick deterministic replay, LCD seed subject)

- **The frozen arm: 48/48 decisions byte-identical** lab-and-package,
  zero fleet appearances — the seam costs exactly nothing where no one
  opts in. The full lab sweep (19 suites) plus the package suite (291
  tests) stayed green, every parity pin intact.
- **The opted-in arm: the thread rides the decision.** 48/48 lab ==
  package with the fleet attached; the anticipatory signal first
  speaks at **tick 2**, before the reactive hungry threshold trips at
  **tick 4**; utilities move on 24 of 48 ticks; max confidence 1.0;
  exactly 1 cold-start-silent tick.
- **Honest remainder: 0 decision flips at LCD scale.** The anticipatory
  boost (≤ ~0.05 × confidence) moves the feed utility but never
  outranks the frozen argmax on this subject. Effect calibration
  against replayed histories is exactly D2's assignment — recorded in
  `blocked_states`, not fudged.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/micro_threads -p "test_*.py"   # RED
ImportError: cannot import name 'build_thread_fleet_report' from 'thread_fleet'
FAILED (errors=1)
PS> python -B -m unittest discover -s labs/micro_threads -p "test_*.py"   # GREEN
Ran 13 tests in 0.064s
OK
PS> python -B labs/micro_threads/thread_fleet.py
The contract and the seam hold: 48/48 frozen decisions byte-identical
lab-and-package with zero fleet appearances; the opted-in pipe cleaner
moved utilities on 24 ticks and first spoke at tick 2 (reactive
threshold trips at 4).
PS> python -B -m unittest discover -s labs/grid_genome -p "test_*.py"
Ran 209 tests in 10.402s
OK
PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
Ran 291 tests in 8.194s
OK
```

## Sources

- `labs/micro_threads/thread_fleet.py` (+ `test_thread_fleet.py`)
- `data/micro_threads/micro_thread_fleet_contract_stage0.json`
- `labs/grid_genome/micro_switchboard.py` (the lab seam)
- `packages/mecha_engine/src/mecha_engine/learning/_switchboard.py`, `threads.py` (the package seam + twin)
- `research/algorithm_cards/micro_thread_fleet_contract.md`
- `docs/project-research/deep-research/01/deep-research.md` (the thread fleet)
- `audits/TODO.md` (cycle 12 D1), `docs/gap-analysis.md` (Phase D)
- `research/decision_records/0009-create-mecha-engine-learning-target.md` (the frozen baseline's bounded claim)
