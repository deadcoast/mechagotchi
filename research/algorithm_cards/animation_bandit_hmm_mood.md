# Algorithm Card: Animation Bandit + HMM Mood

## Purpose

The dossier's behavior-layer pair as fleet threads (gap-analysis
Phase D, D3): a contextual UCB bandit personalizing clip choice per
mood from interaction feedback (consuming `animstate_950`, C3's named
consumer seam), and a hidden-mood HMM over the T16 vocabulary giving
the engine a smoothed, uncertainty-honest latent mood.

## Mathematical Basis

- **Bandit**: per-(mood, clip) means with UCB index
  `mean + sqrt(0.3·ln N_mood / n)` — exploration constant 0.3, tuned
  for the documented short-lifecycle horizon (classic 2.0 never
  converges inside a companion lifetime with 0.2-gap preferences);
  unplayed arms first in vocabulary order; plain counts capped at 500;
  pending show→reward attribution one tick later. Context = the frozen
  T16 threshold mood; arms = the animstate_950 clip catalog ∩ the
  packet's `animation_vocabulary`. Confidence = pulls ramp × top-two
  mean gap. Effects: EMPTY (clip preference is packet-side).
- **HMM**: forward filtering, 4 states [curious, hungry, stressed,
  tired], sticky transitions (0.85 diagonal), soft emissions from the
  frozen thresholds (sigmoid slope 40) with lexicographic priority
  masking (tired > hungry > stressed); dwell hysteresis on the MAP
  readout (challenger must lead by 0.15; the distribution itself is
  reported unsmoothed). Confidence = ramp × (1 − normalized entropy).
  Effects = the frozen reactive mood table's posterior expectation.
- Both deterministic; seeds appear only in the lab keepers' draws.

## Inputs

- Bandit: lifecycle needs (context), `last_animation`,
  `recent_interactions`, `animation_vocabulary`
- HMM: hunger/energy/stress per tick

## Outputs

- Bandit: `recommended_clip` + per-clip means (packet-side consumer)
- HMM: `map_mood` + full `mood_distribution`, entropy-honest
  confidence, expectation-weighted mood effects;
  `data/micro_threads/animation_bandit_hmm_mood_stage0.json`

## Strengths

- Bandit beats uniform rotation for every documented keeper model
  (best case 48.8 vs 192.0 regret) and converges (best-arm rate 0.74–
  0.92 in the final quarter)
- HMM: 17× oscillation reduction (0.0298 vs 0.525 switch rate) on all
  2501 replayed episodes, next-mood Brier 0.524 vs persistence 1.051,
  stable-segment agreement 0.954, confidence lower exactly at
  disagreements (0.622 vs 0.876)

## Weaknesses

- The bandit's live feed (`last_animation` on lifecycle state) does
  not exist yet — live clip driving is Phase F's consumption; until
  then the thread runs only where a loop provides the key
- Overall raw-label agreement is 0.736, capped by design: the flicker
  ticks are the filter's job to disagree with
- Keeper models are D3's three; the five documented user models are
  D5's build

## Failure Modes

- Non-stationary keeper preferences beyond the capped counts' reach
  relearn slowly — the cap trades adaptivity for bounded state
- A mood regime shorter than the dwell margin's threshold is smoothed
  away — that is the documented trade, measured by the stable-segment
  bar

## Integration Risk

Low: both behind the D1 opt-in rule; frozen paths byte-identical (19
lab suites + 291 package tests green).

## License Status

Original stdlib-only code, Apache-2.0.

## Prototype Result

55 lab tests green; full-dataset report `status: complete` — every
bandit and HMM bar met; two honest failures on the way (reward
misattribution in the first harness; UCB1's classic constant too
exploratory) recorded in the report.

## Decision

**Adopt into the fleet.** Go gate for D4: the evidence threads wired
from existing artifacts through this same contract, no new statistics
invented.

## Sources

- `labs/micro_threads/animation_bandit_hmm_mood.py` (+ test file)
- `labs/micro_threads/thread_fleet.py` (+ `test_thread_fleet.py`)
- `data/micro_threads/animation_bandit_hmm_mood_stage0.json`
- `data/animation_system/animstate_950.json`
- `data/datasets/replay_100k_ticks/`
- `research/experiment_reports/2026-07-08-animation-bandit-hmm-mood.md`
- `audits/TODO.md` (cycle 12 D3), `docs/gap-analysis.md` (Phase D)
