# Development TODO — Cycle 12: ENGINE track · Phase D — the intelligence threads

**Build track: THE ENGINE** (of the two builds — engine and game — per
`docs/gap-analysis.md` §0; the engine completes before the game's
playable front end is built, and no feature in this cycle is "the
application").

Source: `docs/gap-analysis.md` (Phase D), opened by the Phase-C gate
(`research/experiment_reports/2026-07-08-phase-c-gate.md`, cycle 11).
The gap table's micro-learner row is the owner's core ML thesis: ~11
named threads (hunger/sleep/boredom/attention predictors, the
animation-preference bandit, interaction timing, HMM mood, mutation
stability, readability, SLIP compat, lineage survival) each streaming
confidence into the switchboard; 5 synthetic user models; a
100k-tick × 500-lifecycle benchmark; ablation gates (≥15% welfare over
the frozen baseline; drop any learner whose removal costs <5%). What
exists: the frozen rule switchboard, one feedback learner, and the
7-weight legibility ranker — ~2 threads of 11. Standing seams this
cycle consumes: `animstate_950` (C3, the bandit's dataset), the adopted
readability model (F3), the mutation-stability descriptor, the SLIP
authority, and lineage records. Dependencies permitted where measured
wall-clock demands (DR 0028; Phase A/B precedent: measure first — the
100k-tick harness is the likeliest genuine NumPy trigger yet).

- [x] **D1 · The thread contract + the switchboard confidence seam.**
  One common interface for every micro-learner (observe → predict →
  confidence in [0,1], deterministic, per-companion state, JSON-
  serializable); the switchboard gains an ADDITIVE confidence-weighted
  arbitration seam (byte-identical when no threads are attached — the
  frozen switchboard stays the promoted baseline and the ablation
  control). RED-first; triad.
- [x] **D2 · The need predictors + interaction timing.** Online
  per-companion threads: hunger, sleep(energy), boredom(novelty),
  attention, and interaction-timing predictors — each proven in the
  lab against replayed lifecycle traces (the engine's own histories,
  never invented data), each streaming calibrated confidence.
- [x] **D3 · The animation-preference bandit + HMM mood.** The
  documented bandit over clips consuming `animstate_950` + interaction
  feedback; the hidden-mood HMM thread (states grounded in the T16
  mood vocabulary) with honest uncertainty. Both deterministic under
  seeds.
- [x] **D4 · The evidence threads.** Mutation stability, readability
  (the F3 adopted model wrapped as a thread — primary signal, survey
  stays fallback), SLIP compatibility, and lineage survival — wired
  from the engine's existing artifacts/records through the D1
  contract; no new statistics invented.
- [ ] **D5 · The synthetic keepers + the scale harness.** The 5
  documented synthetic user models (distinct interaction policies over
  the companion surface); the 100k-tick × 500-lifecycle benchmark
  measuring welfare with/without threads — wall-clock measured FIRST
  at a pilot scale; if stdlib cannot hold, the NumPy decision record
  cites the measurement (DR 0028).
- [ ] **D6 · The ablation gates + Phase-D gate.** The documented
  gates: ≥15% welfare improvement over the frozen baseline; any
  thread whose removal costs <5% is DROPPED (recorded, not kept for
  sentiment). One consolidated Phase-D gate report with the honest
  remainder list. Gap-analysis Phase D checked off only when green.

## Standing note

`docs/gap-analysis.md` governs cycle planning until retired (Phase G
alpha). The engine-truth law (DR 0021), the identity constraint, and
the triad discipline are unchanged. CuBFF real ingest is REQUIRED
late-stage (Phase G). Apache-2.0; dependencies permitted with
justification (DR 0028). Size-parametric, never size-replacing (DR
0029). Named remainders from Phases B/C (evolve's inner loop on WFC;
the hybrid re-opener; limb/joint per-role motion; live clip driving;
clip-frame exports) wait for their own evidence or their owning phase
— do not smuggle them into this cycle.

## Sources

- `docs/gap-analysis.md` (Phase D)
- `research/experiment_reports/2026-07-08-phase-c-gate.md` (the opener)
- `docs/project-research/deep-research/01/deep-research.md` (the thread fleet, user models, benchmark, ablation gates)
- `data/animation_system/animstate_950.json` (D3's dataset), `data/readability_benchmark/adopted_readability_model.json` (D4's model)
- `packages/mecha_engine/src/mecha_engine/learning/` (the frozen switchboard + feedback learner)
- `research/decision_records/0019` (learned readability primary), `0028`, `0029`
