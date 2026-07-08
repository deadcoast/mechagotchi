# Algorithm Card: Need Predictors + Interaction Timing

## Purpose

The documented need-predictor threads (hunger, sleep/energy,
boredom/novelty, attention) and the interaction-timing thread —
five online per-companion micro-learners through the D1 fleet
contract, each proven one-step-ahead against the engine's own
replayed lifecycle histories with calibrated confidence
(gap-analysis Phase D, D2).

## Mathematical Basis

- **Conditional-delta forecast** (hunger, energy):
  `predicted = clamp(v + E_decay[Δ | bucket(v)])` — a decayed mean of
  observed next-tick deltas per need-level bucket (10 bins), learning
  the policy-coupled dynamics (feeds cluster at high hunger, sleeps at
  low energy); median-delta trend fallback for unseen buckets.
  Confidence = window fill × max(0, 1 − 4·bucket_error_EWMA) — skill
  self-assessed per bucket against realized outcomes.
- **Hazard model** (attention):
  `P(interaction | s = ticks since last)` from decayed per-bucket
  counts, hierarchically smoothed toward the thread's own global
  decayed rate (`(h + 2·rate)/(t + 2)`) — a strict generalization of
  the running-rate baseline.
- **Repeat propensity** (boredom): per-action decayed repeat counts,
  same smoothing; `boredom = 1 − window novelty` drives the play
  effect.
- **Gap rhythm** (timing): EWMA (α=0.3) over completed interaction
  gaps; `remaining = max(0, mean_gap − ticks_since)`.
- **Binary confidence = sharpness**: a calibrated predictor's expected
  Brier error is p(1−p), so confidence = max(0, 1 − 4·p(1−p)) ×
  observation ramp.
- All decayed counts bound memory at 1/(1−0.98) = 50; every thread
  state is a small JSON dict; everything is deterministic.

## Inputs

- The live lifecycle state per tick (need values, recent_interactions,
  action_counts — the engine's own history, nothing invented)
- Per-thread memory in `lifecycle_state["thread_states"][name]`

## Outputs

- D1-contract thread dicts (prediction in `output`, confidence,
  additive effects); `data/micro_threads/need_predictors_stage0.json`

## Strengths

- Every predictor beats its documented online baseline on the FULL
  replay corpus (2501 episodes / 100k ticks): hunger MAE 0.0638 vs
  0.1027, energy 0.0492 vs 0.1064, boredom Brier 0.1625 vs 0.1704,
  attention 0.1811 vs 0.1854, timing gap-MAE 0.587 vs 0.689
- Calibration is structural, not tuned: top-confidence quartile errs
  no worse than bottom for all five (hunger bins 0.144→0.028)

## Weaknesses

- Attention's margin over base rate is thin — hazard structure only
  exists where the interaction stream has rhythm
- One-step-ahead skill only; multi-horizon forecasts unproven
- Effect magnitudes are not welfare-proven — D5's benchmark and D6's
  ablation gates judge them

## Failure Modes

- A regime shift faster than the decay window (50 trials) lags — the
  self-assessed error EWMA honestly drops confidence while it relearns
- The first-cut heuristics FAILED both bars (three of five lost to
  baselines; trend-consistency confidence was anti-calibrated) —
  recorded in the D2 report as the canonical warning against proxy
  confidence

## Integration Risk

Low: pure fleet threads behind the D1 opt-in rule; frozen paths stay
byte-identical (all 19 lab suites + 291 package tests green).

## License Status

Original stdlib-only code, Apache-2.0.

## Prototype Result

36 lab tests green; full-dataset evaluation `status: complete` — all
five beat baselines, all five calibrated.

## Decision

**Adopt into the fleet.** Go gate for D3: the animation-preference
bandit (over `animstate_950`) and the HMM mood thread, deterministic
under seeds, through this same contract.

## Sources

- `labs/micro_threads/need_predictors.py` (+ `test_need_predictors.py`)
- `labs/micro_threads/thread_fleet.py` (+ `test_thread_fleet.py`)
- `data/micro_threads/need_predictors_stage0.json`
- `data/datasets/replay_100k_ticks/`
- `research/experiment_reports/2026-07-08-need-predictors.md`
- `research/algorithm_cards/micro_thread_fleet_contract.md` (D1)
- `audits/TODO.md` (cycle 12 D2), `docs/gap-analysis.md` (Phase D)
