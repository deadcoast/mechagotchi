# Decision Record 0009: Create the Mecha Engine Learning Package Target

Date: 2026-07-05

## Status

**Accepted** (owner: "propose 0009 --go", 2026-07-05 — proposal and go
authorized together). Authorizes creating
`packages/mecha_engine/src/mecha_engine/learning` and promoting the
micro-switchboard learning surface under the same rules as the previous
seven modules, with the promotion claim bounded by the evidence below.

## Context — and what the evidence actually supports

Decision record 0004 deferred `learning`. The prerequisite work landed
first, in order: the composed runtime (DR 0008), then the stress survival
regime that broke the saturation which had made every learning claim
unfalsifiable.

The stress learning benchmark
(`data/runtime_integration/stress_learning_benchmark_stage0.json`, 24
generated morphologies on the contracted stress probe, 72-tick episodes,
feedback vs frozen switchboard differing ONLY in whether observed rewards
update the action histories) then **falsified the survival framing
itself**:

- Survival is policy-independent under this regime: both arms 1.0; zero
  morphologies saved or lost by feedback. Survival is decided by the
  morphology's structural load (the lifecycle's documented bistability),
  not by action policy. `feedback_beats_frozen_survival = false`,
  recorded as first-class evidence.
- The learning benefit is **wellbeing**: mean need-balance delta
  **+0.080069** under stress — double the sheltered measurement
  (+0.03964, `switchboard_lifecycle_feedback_stage0`) — at zero survival
  risk (`lost_by_feedback_count = 0`).

## Decision

Create the eighth package module target, `mecha_engine.learning`, porting
the micro-switchboard and its feedback loop with the promotion claim
stated exactly:

> Online reward feedback improves companion need balance (measured
> +0.080069 under stress, +0.03964 sheltered) at zero survival cost.
> **No survival-improvement claim is made or permitted** — survival is
> morphology-decided under the current regime, and any future survival
> claim requires new evidence.

Rules as for every promotion: verbatim lab semantics
(`labs/grid_genome/micro_switchboard.py` + the feedback episode
mechanics), contract tests through the package `src` surface, lab-side
parity pins (including the need-balance delta pins), stdlib-only, no
`labs` imports, no `sys.path`; gates re-derived test-first. The lifecycle
module's "reward shaping stays out of package state" contract is
preserved: the learner lives in `learning`, driving lifecycle only
through its public surface.

## Consequences

- `mecha_engine` gains its eighth module; `render`, `storage`, `slip`
  remain deferred with their own future decision records.
- The engine's behavior story becomes honest and layered: morphology
  decides survival (evolution's domain), policy decides wellbeing
  (learning's domain) — measured, not assumed.
- A future survival-relevant learning claim has a ready-made falsifiable
  harness: the stress learning benchmark.

## Evidence

- `data/runtime_integration/stress_learning_benchmark_stage0.json`
- `research/experiment_reports/2026-07-05-stress-learning-benchmark.md`
- `data/micro_learners/switchboard_lifecycle_feedback_stage0.json`
- `research/experiment_reports/2026-07-05-stress-regime-evolution.md`
- `research/algorithm_cards/micro_learning_switchboard.md`
- `research/package_specs/mecha_engine_learning_interface_spec.md`
- `research/decision_records/0008-propose-mecha-engine-runtime-target.md`
  (the promotion pattern)
