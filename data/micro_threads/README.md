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

Produced by `labs/micro_threads/`.
