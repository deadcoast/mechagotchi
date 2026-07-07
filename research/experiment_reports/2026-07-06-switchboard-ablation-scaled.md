# Experiment Report: Switchboard Ablation, Scaled Rerun (T19 stage 2)

Date: 2026-07-06

## Objective

The Stage 0 ablation's dead_weight verdicts were explicitly queued for a
scaled rerun before any action. This rerun scales creatures: all 8
profile-aligned seed creatures x 5 synthetic users x 6 SLIP-authored
conditions = 240 episodes, with per-user MEAN declines and variance.

## Verification

RED (grid param/scale keys absent) -> GREEN `Ran 7 tests OK`; artifacts:
`switchboard_ablation_scaled_stage0.json` (+ the single-creature
baseline regenerated under the new keep-gate keys).

## Findings

1. **The Stage 0 verdicts replicate at scale.** hidden_mood_estimator
   KEEP — its removal now costs 77-85% mean need balance across every
   user model (up from 28-30% single-creature: across morphologies it
   is even more dominant). EWMA, bandit, and mutation-risk scorer
   remain dead_weight (<5% mean decline).
2. Full-vs-rules-only headline holds across all creatures and users.
3. Standing honesty note carried forward: dead_weight at this scale
   still does not remove a thread — the census gap (interaction signals
   barely reach decisions without boredom/timing threads) is the likely
   cause for EWMA/bandit, and RUN TWO's 500-lifecycle protocol remains
   the final arbiter. What changed: the verdicts are no longer
   single-creature artifacts.

## Sources

- `labs/grid_genome/switchboard_ablation.py`, `labs/grid_genome/test_switchboard_ablation.py`
- `data/micro_learners/switchboard_ablation_scaled_stage0.json`, `data/micro_learners/switchboard_ablation_stage0.json`
- `research/experiment_reports/2026-07-05-switchboard-ablation.md`, `research/micro_learners/thread_census.md`
