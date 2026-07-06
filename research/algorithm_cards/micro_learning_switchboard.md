# Algorithm Card: Micro-Learning Switchboard

## Purpose

Coordinate many small adaptive learners into one explainable companion action
decision.

## Mathematical Basis

EWMA, Bayesian counters, contextual bandits, HMM-like latent states,
rule-weight learners, and small logistic scorers.

## Inputs

- Visible companion state
- Hidden companion state
- User interaction events
- SLIP behavior weights
- Recent prediction errors
- Grid stability and mutation risk scores

## Outputs

- Next action
- Per-learner signal map
- Confidence
- Explanation
- Reward or correction signal

## Strengths

- Interpretable
- Testable in isolation
- Avoids one broad "pet brain"
- Fits the project plan's intelligence-thread model

## Weaknesses

- Requires a clean switchboard contract.
- Bad reward shaping can create annoying behavior.
- Too many learners can produce noisy decisions.

## Failure Modes

- Conflicting signals without arbitration
- User interaction loops optimized for engagement instead of care
- Hidden state drift
- No explanation for action changes

## Integration Risk

Medium.

## License Status

No external code selected.

## Prototype Result

First interpretable switchboard prototype completed on 2026-05-12.

```txt
scenario_count: 3
hungry_recent_attention: feed, confidence 0.829113
low_energy: sleep, confidence 0.816769
stable_curious: play, confidence 0.776111
```

Implemented micro-learners:

- recent interaction EWMA
- rule-based hidden mood estimator
- reward-average action preference bandit
- mutation risk scorer

Lifecycle feedback follow-up completed on 2026-05-12.

Artifacts:

- `labs/grid_genome/switchboard_feedback.py`
- `labs/grid_genome/test_switchboard_feedback.py`
- `data/micro_learners/switchboard_lifecycle_feedback_stage0.json`
- `research/experiment_reports/2026-05-12-switchboard-lifecycle-feedback.md`
- `research/source_notes/2026-05-12-switchboard-feedback-source-review.md`

Measured feedback result:

- Feedback survival ticks: 48
- Frozen baseline survival ticks: 48
- Feedback need balance: 0.767384
- Frozen baseline need balance: 0.767384
- Feedback reward updates: 48
- Frozen reward updates: 0
- Need balance delta: 0.0

Dynamic stress follow-up completed on 2026-05-12.

Artifacts:

- `data/micro_learners/switchboard_feedback_dynamic_stress_stage0.json`
- `research/experiment_reports/2026-05-12-switchboard-feedback-dynamic-stress.md`

Measured dynamic stress result:

- Scenario count: 3
- Dynamic events: 6
- Feedback better need-balance count: 0
- Feedback worse need-balance count: 1
- Mean need-balance delta: -0.002226

SLIP lifecycle/archive bridge completed on 2026-05-12.

Artifacts:

- `labs/workshop_editor/slip_lifecycle_archive_effects.py`
- `data/workshop_editor/slip_lifecycle_archive_effects_stage0.json`
- `research/experiment_reports/2026-05-12-slip-lifecycle-archive-effects.md`

Measured bridge result:

- Current valid profiles covered: 3
- Lifecycle effects measured: 3
- Distinct lifecycle fingerprints: 3
- Mean lifecycle need balance: 0.793865

SLIP runtime selection policy completed on 2026-05-13.

Artifacts:

- `labs/workshop_editor/slip_runtime_selection_policy.py`
- `data/workshop_editor/slip_runtime_selection_policy_stage0.json`
- `research/experiment_reports/2026-05-13-slip-runtime-selection-policy.md`

Measured selector result:

- Selection successes: 3
- Selected archive elites: 3
- Mean selected need balance: 0.793865
- Mean selected survival ratio: 1.0

## Decision

Keep as active prototype. Do not introduce a broad ML model. The lifecycle
feedback loop and profile-specific lifecycle effect bridge are explicit and
measured, and switchboard lifecycle metrics now feed a lab-only archive elite
selector. Reward shaping must still beat the frozen baseline under dynamic
stress before any online learner is promoted into packages.

## Go/No-Go Gate

Each learner must report input, output, confidence, explanation, and measurable
effect on action or survival.

## Stress Benchmark Result (2026-07-05)

24 generated morphologies on the contracted stress probe, 72-tick
episodes, feedback vs frozen switchboard (only difference: online reward
updates):

- Survival: policy-independent — both arms 1.0; zero saved/lost
  (`feedback_beats_frozen_survival = false`, recorded). Survival is
  decided by morphology load (lifecycle bistability).
- Wellbeing: mean need-balance delta **+0.080069** under stress
  (vs +0.03964 sheltered) at zero survival cost.

Decision update: promoted as `mecha_engine.learning` under decision
record 0009 with the bounded claim — need-balance improvement only, no
survival claim permitted without new evidence.

## Ablation Result (2026-07-05, audit T19 Stage 0)

SLIP-authored remove-one ablation (T3.3 switches), five synthetic
user models: full switchboard beats rules-only by ~336% need balance
(the og claim, measured). Keep-gate (>=5% decline, no survival gain):
hidden_mood_estimator KEEP (28-30% decline when removed); EWMA,
bandit, mutation-risk scorer dead_weight at single-episode scale —
queued for the scaled rerun, not removed. The flat deltas across
user models confirm the census gap: interaction signals barely reach
decisions until boredom/timing threads exist.
