# Micro-Thread Fleet Data

Cycle 12 (ENGINE - Phase D) artifacts:

- `micro_thread_fleet_contract_stage0.json` - D1: the fleet
  contract (observe -> signal -> confidence, pure, deterministic,
  bounded) and the switchboard's additive confidence seam, proven
  on a two-arm 48-tick lifecycle replay: the frozen arm 48/48
  byte-identical lab-and-package with zero fleet appearances; the
  opted-in `hunger_forecast` pipe cleaner first speaks at tick 2,
  before the reactive hungry threshold trips at tick 4 (0 decision
  flips at LCD scale — recorded honestly; welfare impact is D5/D6's
  judgment).
- `need_predictors_stage0.json` - D2: five online predictors (hunger,
  energy, boredom, attention, interaction timing) proven one-step-
  ahead against the full replay corpus (2501 episodes / 100k ticks):
  every one beats its online baseline and passes the calibration gate
  (top-confidence quartile no worse than bottom). The first-cut
  heuristics failed both bars and were replaced — recorded in the D2
  report.
- `animation_bandit_hmm_mood_stage0.json` - D3: the contextual UCB
  clip bandit (arms from the animstate_950 catalog; beats uniform
  rotation for all three documented keepers, converges 0.74-0.92
  best-arm, deterministic under seeds) and the hidden-mood HMM (17x
  oscillation reduction on 2501 replayed episodes, next-mood Brier
  0.524 vs persistence 1.051, stable-segment agreement 0.954,
  entropy-honest confidence).

Produced by `labs/micro_threads/`.
