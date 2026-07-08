# Experiment Report: The Need Predictors Beat Their Baselines, Calibrated (Cycle 12 · ENGINE · D2)

Date: 2026-07-08

## WHY

The documented fleet names hunger/sleep/boredom/attention predictors
and an interaction-timing thread, "each proven in the lab against
replayed lifecycle traces (the engine's own histories, never invented
data), each streaming calibrated confidence." D1 gave the fleet its
contract; D2 is the first real learning through it.

## WHAT

Five online per-companion threads in `labs/micro_threads/thread_fleet.py`
(RED-first; the lab is now 36 tests) and the evaluation harness
`need_predictors.py`:

- **`hunger_forecast` / `energy_forecast`** — bucket-conditional delta
  learners: at the current need level's bucket (10 bins), the decayed
  mean of the engine's own observed next-tick deltas — which LEARNS
  that high hunger attracts feeds and low energy attracts sleeps —
  with a median-delta trend fallback for unseen buckets. Confidence is
  per-bucket SELF-ASSESSED skill (1 − 4×the bucket's realized-error
  EWMA): spiky regimes keep honestly low confidence.
- **`boredom_novelty`** — per-action repeat propensity (decayed
  counts, hierarchically smoothed toward the thread's own global
  repeat rate), the novelty-decay signal; boredom = 1 − window novelty
  seeks play.
- **`attention_forecast`** — an online hazard model:
  P(interaction | ticks since the last one), decayed counts per bucket,
  smoothed toward the thread's own global rate — a strict
  generalization of the base-rate baseline.
- **`interaction_timing`** — gap-EWMA rhythm over completed
  interaction gaps (unchanged from its first cut: it passed both bars
  immediately).
- Binary-thread confidence is Bernoulli SHARPNESS (1 − 4·p(1−p)): a
  calibrated predictor's expected Brier error *is* p(1−p), so
  sharpness is the honest confidence statement.

**The harness** replays all 2501 episodes of `replay_100k_ticks`
(switchboard/idle/random policies, 100k ticks), reconstructing each
tick's lifecycle state verbatim (recorded snapshots + the exact
5-window `recent_interactions` / `action_counts` rules
`advance_tick` applies), and scores every one-step-ahead prediction
against the recorded next tick. Bars, both pre-registered in the
harness: (1) every predictor beats its documented online baseline;
(2) every predictor's top-confidence quartile errs no worse than its
bottom quartile.

## FINDINGS (2501 episodes · 100,004 rows · full dataset)

| Predictor | Metric | Predictor | Baseline | Beats | Calibrated |
| --- | --- | --- | --- | --- | --- |
| hunger_forecast | MAE | **0.0638** | 0.1027 (persistence) | yes | yes (0.144→0.028 across bins) |
| energy_forecast | MAE | **0.0492** | 0.1064 (persistence) | yes | yes (0.079→0.016) |
| boredom_novelty | Brier | **0.1625** | 0.1704 (running repeat rate) | yes | yes (0.229→0.045) |
| attention_forecast | Brier | **0.1811** | 0.1854 (running interaction rate) | yes | yes (0.222→0.199) |
| interaction_timing | gap MAE | **0.587** | 0.689 (last-gap persistence) | yes | yes |

- **The first cut FAILED — recorded, then fixed.** The initial
  heuristics (mean-delta trend, flat interaction EWMA, modal-share
  repeat, trend-consistency confidence) lost to their baselines on
  three of five threads, and trend-consistency confidence was
  ANTI-calibrated: it peaks during long drift streaks, exactly where
  the policy's next feed/sleep spike lands, so the top-confidence bin
  had the WORST error (0.178 vs 0.075). The replacements are learners
  of the engine's actual dynamics, and the calibration fix is
  structural (self-assessed per-bucket error; sharpness), not tuned.
- Energy is the strongest forecast (less than half of persistence
  error): sleep spikes concentrate in low-energy buckets and the
  conditional model captures them.
- Attention's margin is the thinnest (0.1811 vs 0.1854) — honest: the
  hazard structure only pays off in the switchboard arm's periodic
  regimes; in the random arm it converges to the base rate by design.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/micro_threads -p "test_*.py"   # RED
ImportError: cannot import name 'build_need_predictor_report' from 'need_predictors'
FAILED (errors=2)
PS> python -B -m unittest discover -s labs/micro_threads -p "test_*.py"   # GREEN
Ran 36 tests in 4.438s
OK
PS> python -B labs/micro_threads/need_predictors.py
All five predictors beat their baselines with calibrated confidence on
the engine's own replayed histories.
PS> python -B labs/micro_threads/thread_fleet.py   # D1 gates re-verified post-upgrade
The contract and the seam hold: 48/48 frozen decisions byte-identical
lab-and-package with zero fleet appearances; the opted-in pipe cleaner
moved utilities on 24 ticks and first spoke at tick 2 (reactive
threshold trips at 4).
```

## Sources

- `labs/micro_threads/need_predictors.py` (+ `test_need_predictors.py`)
- `labs/micro_threads/thread_fleet.py` (+ `test_thread_fleet.py`)
- `data/micro_threads/need_predictors_stage0.json`
- `data/datasets/replay_100k_ticks/` (the replayed histories)
- `packages/mecha_engine/src/mecha_engine/learning/threads.py` (the twin)
- `research/algorithm_cards/need_predictors.md`
- `research/experiment_reports/2026-07-08-micro-thread-fleet-contract.md` (D1)
- `audits/TODO.md` (cycle 12 D2), `docs/gap-analysis.md` (Phase D)
