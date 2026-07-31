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

## Ablation Conditions E/F/G (2026-07-28, cycle 24 N3 — DR 0051)

The dossier's micro-learner ablation names eight conditions; Phase D's
eleven-thread fleet contained **no Q-table, no decision tree and no
Bayesian counter**, so **E/F/G were documented and unmet from cycle 12
until now**. All three built and run through the D6 gates **verbatim**
(`ablation_gates` imported, never re-implemented), at the same 5% bar:

| condition | learner | decision | welfare | skill |
| --- | --- | --- | --- | --- |
| **E** | `qtable_policy` (3×3 hunger/energy buckets) | **KEEP** | 0.795% | **+55.459%** regret reduction vs uniform random |
| **F** | `tiny_tree_router` (depth 2, ≤4 leaves) | **DROP** | 0.615% | **−1.776%** vs a depth-1 stump |
| **G** | `bayes_keeper_counter` (Beta-Bernoulli) | **DROP** | 1.194% | **+2.756%** Brier reduction vs the running rate |

**Both drops confirm this card's own "Mathematical Basis" entries in the
harsh direction, with numbers attached.** F: splitting on energy *after*
hunger returns 0.799976 against the stump's 0.814443 — the second split
is **decoration**, and the failure is dilution (thin leaves) rather than
overfitting. G: a Beta-Bernoulli posterior is barely distinguishable
from a running mean on this question (Brier 0.190317 vs 0.195712) — the
uncertainty it carries buys 2.756%, **under half the bar**, and nothing
in the switchboard consumes the uncertainty itself.

Every candidate's welfare removal cost is **under 1.2%**, reproducing
D6's saturated decision seam: the frozen reactive rules sit near the
autonomous-behavior welfare optimum, so learners are decided on skill.
The **kept-five roster is unchanged** — all eleven incumbents re-judged
on the new baseline land between 0.000% and 0.359%, and their skill
metrics are properties of each thread's own prediction task rather than
of fleet composition.

**Nothing is promoted**: `FLEET_THREADS` is untouched and the committed
D6 artifact regenerates **byte-identical** (SHA-256
`75640475cc9c9fc4cab5f4c4955121e8a2a118672169e5c64acdc5bf17e66f44`),
proven by regeneration rather than asserted. Honest limits: E's uniform
random baseline is weak (the `animation_bandit` precedent's shape, not a
test against the incumbent reactive rule), and F's stump baseline is
given a full-sample oracle while the tree is scored online — an
asymmetry that runs against the tree.
