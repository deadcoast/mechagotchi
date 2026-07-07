# Decision Record 0019: Learned Readability (R3) — Plan

Date: 2026-07-06

## Status

**Accepted as the R3 plan** (DR 0017 R-queue). R3 is one task of the
cycle-02 TODO; development continues through that TODO's tasks until it
is exhausted and confirmed complete.

## The purpose (TRUE ML as the primary path)

The owner's requirement (DR 0017 a.4): TRUE Machine Learning where
applicable, never framed as blocked on human labels. Today readability
is a hand-designed heuristic (`score_readability` — fixed weights the
author chose) plus a manual rating pipeline that waits for human data.
The manual system is the FALLBACK and future calibration check — it
stays exactly as built. R3 delivers the primary path: **a model that
LEARNS readability from engine-derived signals**, with no human in the
training loop.

## The design

### The training signal: physics-supervised pairwise learning

Human labels are unavailable; engine physics is not. For any valid grid
the engine can manufacture a *provably less readable* counterpart:

- **contrast collapse** — recolor toward a low-contrast palette ramp
  (WCAG relative-luminance physics guarantees the ordering);
- **organ scatter** — fragment an organ's cells into disconnected
  islands (detectability physics: more components, less legible);
- **silhouette noise** — flip body/void cells at the boundary (raises
  silhouette entropy);
- **anchor erosion** — strip animation-anchor coverage.

Each (original, degraded) pair is a ground-truth comparison labeled by
physics, not by a person. The model trains on these pairs with a
Bradley-Terry/logistic pairwise objective — `P(a preferred over b) =
sigmoid(w · (f(a) − f(b)))` — learning weights `w` by gradient ascent
(stdlib math only). Features `f` are raw measurables (component counts,
contrast ratios, entropies, symmetry, coverage, mass, organ stats) —
NOT the heuristic's hand-mixed score. The weights are LEARNED, never
copied.

### The honest gates

- **It actually learns**: heldout pair accuracy well above chance, and
  trained weights measurably different from initialization.
- **It generalizes**: hold out one entire degradation family from
  training; the model must still rank unseen-family pairs correctly —
  the test that separates learning from memorizing.
- **Determinism**: fixed seed ⇒ identical trained weights and report.
- **Fallback intact**: the manual intake, Bradley-Terry human scorer,
  and calibration gate stay byte-identical; when human data arrives it
  calibrates/audits the learned model (the fallback's real job).

### The live consumer (no new exhibits)

DR 0017 forbids proving a track and leaving it on a shelf. R3 wires the
learned model into the running engine: an optional
**readability-aware parent selection** arm in the evolution loop —
elite parents ranked by a blend of archive fitness and LEARNED
readability. Measured A/B at the same seed: mean readability of the
evolved population must rise versus the fitness-only baseline without
collapsing fitness. That is the player-noticeable claim: **creatures
evolve to be easier to read because the engine learned what readable
means.** Absent the option, the loop stays byte-identical (the same
discipline as R2).

### Scope boundaries

- Model class is a linear pairwise ranker — small, stdlib, inspectable
  (learned weights are reported per feature, so the model's "opinion"
  is auditable). Nonlinear models are a later record if the linear
  ceiling is measured and found wanting.
- The heuristic `score_readability` stays for comparison (report the
  rank agreement) but no longer holds the primary title.
- Lab-first: promotion of learned readability into the package is a
  separate later record.

## Deliverables (the triad + wiring)

1. `labs/readability_benchmark/learned_readability.py` — degradation
   pair factory, feature extractor, pairwise trainer, evaluation,
   artifact writer (+ `test_learned_readability.py`, RED first).
2. Evolution-loop arm: optional learned-readability blend in parent
   selection (`labs/runtime_integration`), A/B measured, absent =
   frozen.
3. Experiment report `2026-07-06-learned-readability.md` (RED/GREEN +
   measured generalization + A/B), algorithm card
   `learned_readability.md`, ledger entry, TODO check-off.

## Consequences

- Readability becomes a learned engine capability; the manual system is
  demoted to its true role (fallback + calibration) permanently.
- The `runtime.evolve` promotion of the R2 CuBFF seam (DR 0018's
  recorded next step) is logged in the cycle-02 TODO as R2.5 so it is
  developed, not forgotten.

## Sources

- `research/decision_records/0017-recalibration-engine-game-duality.md` (R3)
- `labs/readability_benchmark/readability_benchmark.py` (features/heuristic)
- `labs/readability_benchmark/bradley_terry.py` (the human-data scorer, fallback)
- `research/human_studies_protocol.md` (human DATA comes only from humans)
- `labs/runtime_integration/mecha_engine_runtime_loop.py` (parent-selection seam)
