# Experiment Report: The Phase-D Gate — The Intelligence Threads Exist (Cycle 12 · ENGINE · D1–D6)

Date: 2026-07-08

## WHY

The gap table's micro-learner row was the owner's core ML thesis and
the deepest engine gap: ~11 named threads specified, ~2 in existence.
Phase D (gap-analysis) closes when the fleet, the user models, the
scale benchmark, and the documented ablation gates all exist with
honest verdicts.

## THE GATE, TASK BY TASK

- **D1 — the contract + the seam.** One interface for every
  micro-learner (observe → signal → confidence ∈ [0,1], pure,
  deterministic, bounded, JSON-serializable) and the switchboard's
  additive confidence seam under THE OPT-IN RULE: 48/48 frozen replay
  decisions byte-identical lab-and-package with zero fleet
  appearances. The frozen switchboard remains the parity-pinned
  ablation control.
- **D2 — the need predictors + interaction timing.** Five online
  per-companion learners proven one-step-ahead on the engine's own
  replayed histories (2501 episodes / 100k ticks): every predictor
  beats its documented baseline (energy MAE 0.049 vs 0.106
  persistence) with calibrated confidence (top-quartile error ≤
  bottom). The first-cut heuristics FAILED both bars and were
  replaced — recorded.
- **D3 — the animation bandit + HMM mood.** The contextual UCB bandit
  over the `animstate_950` catalog beats uniform rotation for all
  three documented keeper models (best-arm 0.74–0.92), deterministic
  under seeds; the HMM smooths the T16 mood 17× with next-mood Brier
  0.524 vs 1.051 and entropy-honest confidence (0.62 at
  disagreements vs 0.88).
- **D4 — the evidence threads.** Mutation stability, readability (the
  F3 ADOPTED model, DR 0019 primary), SLIP compatibility, lineage
  survival — wired from existing artifacts under the input-bundle
  factoring; THE WIRING PIN holds 50/50 byte-equal on all four. The
  documented fleet reached 11 of ~11.
- **D5 — the keepers + the scale harness.** The five documented user
  models; the 100k-tick × 500-lifecycle two-arm benchmark; wall-clock
  measured FIRST: **stdlib holds** (17.9 s measured vs the 600 s
  bound — the likeliest NumPy trigger yet did not fire, DR 0028). THE
  HONEST ZERO: the sheltered environment is welfare-saturated, which
  forced D6's keeper-dependent redesign.
- **D6 — the ablation gates.** In the beg-mediated keeper-dependent
  mode: **full fleet beats rules_only by 292.6%** (the dossier's ≥15%
  gate MET; T19 precedent); **fleet-vs-frozen −0.05% recorded
  honestly**; the <5% drop rule applied without sentiment — **5
  threads kept on their documented skill metrics, 6 dropped**
  (boredom_novelty 4.6%, attention_forecast 2.3%, and the four
  evidence conduits from the decision seam).

## THE GATE VERDICT: GREEN

Every Phase-D surface named by `docs/gap-analysis.md` exists with a
machine-readable artifact and honest verdicts: the fleet (11/11
through one contract), the five user models, the 100k-tick ×
500-lifecycle harness, and the documented ablation gates run at full
scale. All 19 lab suites plus the 291-test package suite are green;
every frozen path is byte-identical.

## THE HONEST REMAINDER LIST

1. **Decision-seam welfare of the fleet is ~0 over the frozen rules**
   — measured across three environments and a gain sweep. The frozen
   reactive switchboard already sits near the autonomous-behavior
   welfare optimum; remaining welfare belongs to the keeper. The
   fleet's proven value is prediction skill, personalization, and
   interpretability — the GAME's consumers (Phase F) are where those
   signals cash out (ui_hints, beg timing, clip choice, mood display).
2. **Dropped threads** stay parity-pinned with verdicts recorded;
   default profiles must not opt them in (T19 precedent).
3. **Live-loop wiring** of `evidence` bundles and `last_animation`
   into lifecycle state waits for its consumer (Phase F's live clip
   driving and packet loop).
4. **Keeper models are lab operationalizations**; real player
   telemetry is a GAME-track concern.
5. Named remainders from B/C stand unchanged (evolve's inner loop on
   WFC; the hybrid re-opener; limb/joint motion; live clip driving;
   clip-frame exports).

## Verification

```powershell
PS> python -B -m unittest discover -s labs/micro_threads -p "test_*.py"
Ran 85 tests in 8.359s
OK
PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
Ran 291 tests
OK
# Full lab sweep: 19/19 suites OK (see the D1–D6 reports for each RED/GREEN)
```

## Sources

- `research/experiment_reports/2026-07-08-micro-thread-fleet-contract.md` (D1)
- `research/experiment_reports/2026-07-08-need-predictors.md` (D2)
- `research/experiment_reports/2026-07-08-animation-bandit-hmm-mood.md` (D3)
- `research/experiment_reports/2026-07-08-evidence-threads.md` (D4)
- `research/experiment_reports/2026-07-08-synthetic-keepers.md` (D5)
- `research/experiment_reports/2026-07-08-ablation-gates.md` (D6)
- `data/micro_threads/` (the six stage0 artifacts)
- `docs/gap-analysis.md` (Phase D), `audits/TODO.md` (cycle 12)
