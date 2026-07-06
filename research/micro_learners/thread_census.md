# Micro-Learner Thread Census

Date: 2026-07-05. Audit task T5: map every og-specified predictor
(01-formatted, Layer 6) to its implementation status with evidence
paths. This census is the design input for the remaining SLIP ladder
rungs (T3.2 `risk_tolerances`, T3.3 `learning_switches` — DR 0012's
enforced-or-consumed law needs these threads as consumers) and for the
T19 remove-one ablation.

The implemented switchboard (`labs/grid_genome/micro_switchboard.py`)
runs four threads over `ACTIONS = [feed, play, sleep, idle, mutate]`,
each returning the og proof shape (input, output, confidence,
explanation, effects on actions); `run_switchboard` sums
confidence-weighted effects into action utilities. The promoted
`mecha_engine.learning` module carries the feedback loop over this
switchboard with its measured bounded claim (wellbeing, not survival —
DR 0009).

## The census

| # | og predictor | Status | Evidence / gap |
| --- | --- | --- | --- |
| 1 | Hunger predictor | **PARTIAL** | `estimate_hidden_mood` reads `hunger` and raises feed utility when high — reactive inference, not the og's forward *predictor* (no hunger-trajectory forecast). |
| 2 | Sleep predictor | **PARTIAL** | Same thread: `energy < 0.2 → tired → sleep effect`. Reactive, not predictive. |
| 3 | Boredom predictor | **MISSING** | No boredom concept anywhere. Closest signal is `recent_interaction_ewma`'s low-attention branch, which measures the user, not the creature's boredom state. |
| 4 | Attention predictor | **IMPLEMENTED** | `recent_interaction_ewma`: EWMA (α=0.45) over `recent_interactions`, confidence from sample count, play/idle effects. |
| 5 | Animation preference learner | **MISSING (blocked on T4)** | No animation vocabulary exists to prefer among. Unblocks when T4 lands; `action_preference_bandit` is the ready-made mechanism (bandit over animation ids instead of actions). |
| 6 | Interaction timing learner | **MISSING** | Needs an interaction-event stream. The honest path is T19's synthetic user models (attentive/neglectful/erratic/punitive/exploratory) — real user data is owner-gated. |
| 7 | Mood transition model | **PARTIAL** | `estimate_hidden_mood` is a rule-based static classifier (tired/hungry/stressed/curious), not the og's transition model (HMM-ish, `P(mood_t+1 | mood_t, …)`). The lifecycle history stream exists to train one. |
| 8 | Mutation stability learner | **IMPLEMENTED** | `mutation_risk_scorer`: `risk = 0.65·stress + 0.35·(1−grid_stability)`; suppresses `mutate`, nudges `idle`. |
| 9 | Visual readability learner | **COVERED ELSEWHERE** | Not a switchboard thread: the readability proxy (`labs/readability_benchmark`) scores creatures into archive fitness, visibly uncalibrated until the owner's manual ratings. A *learned* readability model is gated on that same human data. |
| 10 | SLIP compatibility scorer | **COVERED ELSEWHERE** | Contractual, not learned: `is_grid_aligned` (authority + package mirrors) plus alignment-retention metrics through repair/runtime. The og imagined a soft scorer; the shipped system made it a hard gate — stronger, and a deliberate divergence worth keeping. |
| 11 | Lineage survival predictor | **MISSING** | Evolution runs *measure* lineage survival (stress regime, T1 wire) but nothing *predicts* offspring survival from lineage features. Candidate lab: train on the accumulated evolution artifacts' (ancestor features → survival) pairs. |
| + | Action preference bandit | **IMPLEMENTED (beyond the og list)** | `action_preference_bandit`: reward-mean bandit over actions; the surface `mecha_engine.learning`'s feedback loop updates. |

Totals: 3 implemented, 3 partial, 3 missing (one blocked on T4), 2
covered elsewhere by stronger mechanisms.

## Consumer designs for the next ladder rungs (T3.2 / T3.3)

Both designs are parity-safe by construction: the switchboard reads new
OPTIONAL state keys that no v0.1 flow ever sets, so every pinned
trajectory (including `mecha_engine.learning`'s byte-for-byte `decide`
parity) is untouched.

- **T3.2 `risk_tolerances`** → consumed by `mutation_risk_scorer` (and
  the stress branch of `estimate_hidden_mood`): the lab lifecycle stashes
  the profile's tolerance into state (e.g. `state["risk_tolerance"]`),
  and the scorer scales its mutation-suppression effect — risk-tolerant
  species keep mutating under stress, risk-averse species freeze.
  Absent key ⇒ current behavior, bit-for-bit. The rung's experiment:
  two profiles differing only in tolerance produce measurably different
  action mixes and mutation counts (the og go/no-go: one measurable
  outcome, no destabilization).
- **T3.3 `learning_switches`** → gates which threads run
  (`state["learning_switches"]`, default all-on): the og "learning
  toggles". Doubles as the harness T19's remove-one ablation needs —
  the ablation conditions become profile-authored instead of
  code-forked.

## Gap plan (each missing thread, og proof shape required)

Every future thread must ship with: input, output, confidence,
explanation, effect on action, effect on survival/experience — and the
go/no-go: it improves one measurable outcome without destabilizing the
companion (measured via T19's harness once built).

1. Boredom predictor — EWMA/counter over action monotony + interaction
   gaps; effects raise `play`. Buildable now.
2. Mood transition model — count-based transition matrix from lifecycle
   `history` streams; replaces the static classifier only if it beats it
   in the T19 harness.
3. Interaction timing learner — after T19's synthetic users exist.
4. Animation preference learner — after T4's vocabulary exists.
5. Lineage survival predictor — train/evaluate on accumulated evolution
   artifacts; feeds archive parenting (pairs with T3.4
   `lineage_preferences`).

## Sources

- `.depreciated/01-formatted.md` (Layer 6), `audits/TODO.md` (T5, T19)
- `labs/grid_genome/micro_switchboard.py`
- `labs/grid_genome/switchboard_feedback.py`
- `packages/mecha_engine/src/mecha_engine/learning/`
- `research/decision_records/0009-create-mecha-engine-learning-target.md`
- `research/decision_records/0012-slip-schema-extension-ladder.md`
- `labs/readability_benchmark/`, `labs/grid_genome/slip.py`
