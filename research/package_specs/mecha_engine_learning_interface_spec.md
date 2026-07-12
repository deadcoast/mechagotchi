# Mecha Engine Learning Module Interface Spec

Date: 2026-07-05

## Status

Contract reference for `mecha_engine.learning` (decision record 0009,
accepted 2026-07-05). Evidence basis: the stress learning benchmark and
the original switchboard feedback lab.

## The bounded claim (load-bearing)

This module's contract claim is **wellbeing, not survival**: online
reward feedback improves need balance (+0.080069 measured under the
stress regime; +0.03964 sheltered) at zero survival cost
(`lost_by_feedback_count = 0`). Survival is morphology-decided under the
current lifecycle bistability — `feedback_beats_frozen_survival = false`
is recorded evidence, and no surface, docstring, or report of this module
may claim survival improvement without new evidence.

## Proposed public surface

- `decide(state) -> dict` — the micro-switchboard decision: verbatim port
  of `labs/grid_genome/micro_switchboard.run_switchboard` (action,
  confidence, per-learner signals, explanation) over a lifecycle state
  from `mecha_engine.lifecycle.initial_state`/`advance_tick`.
- `ACTIONS` — the supported action set, identical to the lab's.
- `run_feedback_episode(grid, slip_profile, *, ticks=48,
  feedback_enabled=True, miscalibrate=True) -> dict` — one deterministic
  episode driving `mecha_engine.lifecycle` publics with switchboard
  decisions; `feedback_enabled=False` resets action-reward histories
  every tick (the frozen comparator); `miscalibrate=True` applies the
  labs' deliberate reward miscalibration (the learnable-gap premise both
  measurements share). Episode report mirrors the lab shape (survival,
  need_balance, recovery events, reward update count, per-tick history).

### The fleet surface (additive, cycle 14 F3b)

The cycle-12 D1 contract's fleet entry points — already promoted into
`learning.threads` (verbatim port of `labs/micro_threads/
thread_fleet.py`) and consumed internally by `decide`'s additive
seam — are exported for the consumer the Phase-D gate names (the
GAME: beg timing, clip choice, mood display). Export only; zero
behavior change:

- `observe_fleet(lifecycle_state) -> dict` — one observe step for
  every opted-in fleet thread; returns the new `thread_states`
  mapping (the caller stores it back); never mutates its input.
- `fleet_signals(lifecycle_state) -> list[dict]` — the opted-in
  threads' `{name, input, output, confidence, explanation, effects}`
  signals (the D1 shape).
- `FLEET_THREAD_NAMES` — the eleven documented thread names in the
  registry's fixed execution order.

THE OPT-IN RULE is unchanged and load-bearing: fleet threads run only
on an explicit `learning_switches[name] is True`, so both surfaces
are silent on every frozen path (pinned by
`tests/test_learning_fleet_surface.py`). The D6 ablation verdicts
stand: dropped threads stay out of default profiles; a consumer
enabling threads cites the kept list
(`data/micro_threads/ablation_gates_stage0.json`).

## Hard gates for the port

- Lab-side parity pins: `decide` byte-identical to the lab
  `run_switchboard` over episode-generated states; `run_feedback_episode`
  reproduces the original feedback lab's episode records (48 ticks,
  seed grid, feedback on and off) AND the stress learning benchmark's
  per-candidate episode results for both arms — including the
  need-balance delta pins (+0.03964 sheltered, +0.080069 stress mean).
- The lifecycle boundary holds: `learning` drives lifecycle only through
  its public surface; reward shaping state lives in the episode loop,
  never inside lifecycle.
- Deterministic; no input mutation; stdlib-only; imports only
  `mecha_engine.*`; no `labs`, no `sys.path`.
- The bounded claim appears in the module docstring; no survival claim
  anywhere.

## Non-goals

- No contextual bandits / deeper learners (future candidates need their
  own evidence and decision records).
- No survival-improvement claim (see the bounded claim).
- No persistence of learned state across episodes (single-episode
  learning only, matching the evidence).

## Sources

- `research/decision_records/0009-create-mecha-engine-learning-target.md`
- `labs/grid_genome/micro_switchboard.py`
- `labs/grid_genome/switchboard_feedback.py`
- `labs/runtime_integration/stress_learning_benchmark.py`
- `data/runtime_integration/stress_learning_benchmark_stage0.json`
- `data/micro_learners/switchboard_lifecycle_feedback_stage0.json`
- `research/algorithm_cards/micro_learning_switchboard.md`
