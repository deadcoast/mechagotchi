# Experiment Report: Switchboard Remove-One Ablation (T19, Stage 0)

Date: 2026-07-05

## Objective

RUN TWO's ablation, at honest Stage 0 scale: which micro-learner threads
measurably earn their place? Conditions are SLIP-authored
`learning_switches` profiles (rung T3.3's harness working as designed):
full, four remove-ones, rules-only — across the og five synthetic user
models (attentive/neglectful/erratic/punitive/exploratory, deterministic
tick patterns).

## Verification

RED (module absent) → GREEN `Ran 6 tests OK`; artifact
`data/micro_learners/switchboard_ablation_stage0.json` (30 episodes).

## Findings

1. **The og claim is now a number: the full switchboard beats
   rules-only by ~336% need balance** (347.8% under the punitive user).
   Rules-only idles into need collapse; any learning at all transforms
   wellbeing.
2. **The keep-gate (>=5% decline on removal, no survival gain) keeps
   exactly one thread: `hidden_mood_estimator`.** Removing it costs
   28-30% need balance under every user model. The EWMA, bandit, and
   mutation-risk threads each cost <5% in a single sheltered episode —
   verdict `dead_weight` AT THIS SCALE, which per the artifact's own
   limitations queues them for the scaled rerun (500-lifecycle protocol,
   variance) before any removal is considered. The mood estimator
   dominating action utility is consistent with its high-confidence,
   large-magnitude effects.
3. The near-identical deltas across user models expose a real gap the
   census predicted: the interaction stream barely reaches decisions
   (the EWMA's effects are small) — the boredom predictor and
   interaction-timing threads are where user models would start
   mattering.

## Decision

Mechanism + measured baseline delivered; no thread is removed at Stage 0
scale. Scale-up (creatures x lifecycles x variance) is the follow-up,
now cheap: every condition is a SLIP profile.

## Sources

- `labs/grid_genome/switchboard_ablation.py`, `labs/grid_genome/test_switchboard_ablation.py`
- `data/micro_learners/switchboard_ablation_stage0.json`
- `research/micro_learners/thread_census.md`, `research/decision_records/0012-slip-schema-extension-ladder.md`
- `.depreciated/02-design.md` (the ablation protocol)
