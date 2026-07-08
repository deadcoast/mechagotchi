# Development TODO — Cycle 10: ENGINE track · Phase B — the missing generation layer

**Build track: THE ENGINE** (of the two builds — engine and game — per
`docs/gap-analysis.md` §0; the engine completes before the game's
playable front end is built, and no feature in this cycle is "the
application").

Source: `docs/gap-analysis.md` (Phase B), opened by the Phase-A gate
(`research/experiment_reports/2026-07-08-phase-a-gate.md`, cycle 09).
The documents specify a hybrid generation architecture — Markov →
**WFC/constraints** → mutation → validator → MAP-Elites — proven by a
bake-off against random/Markov/constrained arms at dossier thresholds
(≥85–95% validity, ≤250 ms per candidate at 16×16). **No WFC lab has
ever existed** (`labs/wfc_grid/` was never created) and the historical
"bake-off" ran without the documented field. Phase A left one named
remainder this phase closes: the generation alphabet is still
{., B, A, E, M}, so children of rich 16×16 parents lose their
shell/limb/antenna cells — the WFC/constraint layer runs over the FULL
DR 0015 vocabulary. Third-party dependencies permitted where the
capability needs them (DR 0028), justified in the decision record;
Phase A's measurement precedent: justify from wall-clock, never assume.

- [x] **B1 · `labs/wfc_grid/` — the WFC/constraint generator.**
  Adjacency/tile extraction over the RICH token alphabet from the
  16×16 seed corpus (grid_helpers `RICH_TOKENS`); wave-function
  collapse with entropy-ordered cell selection, constraint propagation,
  bounded backtracking, and validator gating; deterministic under a
  seed (string-seeded RNG, no wall clock). Triad: algorithm card,
  experiment report, tests, `data/wfc_grid/*_stage0.json`. RED-first.
- [x] **B2 · The bake-off arms and protocol.** Arms: random baseline,
  Markov (existing lab), constrained stabilizer (existing), WFC (B1),
  and the documented hybrid (Markov proposal → WFC constraint pass →
  mutation → validator). Dossier metrics per arm: validity rate,
  connectedness, organ-presence F1, symmetry score, silhouette entropy,
  palette violation rate, generation time, descriptor novelty (archive
  bins), readability proxy (displayed as 8×8-calibrated/uncalibrated —
  honest labeling). Corpus split: the dossier's 72/24/24 over 120 seeds
  is adapted to the real 50-creature corpus (30/10/10 train/dev/
  holdout) — record the adaptation explicitly as a protocol decision;
  expanding the corpus toward 120 is a named option, not an implied
  default.
- [x] **B3 · Thresholds, verdict, adoption.** Gate the arms on the
  dossier thresholds (validity ≥85–95%, ≤250 ms per candidate at
  16×16, measured wall-clock recorded); adopt the winner into
  `mecha_engine.generation` by decision record — an additive seam,
  byte-identical when off, RED-first with parity pins; rich-alphabet
  emission closes the Phase-A remainder. If the documented hybrid does
  NOT win, the refutation is a first-class finding and the measured
  winner is adopted instead.
- [x] **B4 · Phase-B gate + report.** One consolidated experiment
  report: the bake-off table, the adoption decision, regenerated
  16×16 generated-grid corpora, and the honest remainder list.
  Gap-analysis Phase B checked off only when this gate is green.

## Standing note

`docs/gap-analysis.md` governs cycle planning until retired (Phase G
alpha). The engine-truth law (DR 0021), the identity constraint, and
the triad discipline are unchanged. CuBFF real ingest is REQUIRED
late-stage (Phase G). Apache-2.0; dependencies permitted with
justification (DR 0028). Size-parametric, never size-replacing: the
8×8 pins stay unbroken (DR 0029).

## Sources

- `docs/gap-analysis.md` (Phase B)
- `research/experiment_reports/2026-07-08-phase-a-gate.md` (the opener)
- `docs/project-research/deep-research/01/deep-research.md` (the bake-off protocol, metrics, thresholds)
- `research/decision_records/0015-dormant-vocabulary-coverage.md` (the rich alphabet), `0028`, `0029`, `0030`
- `labs/grid_genome/grid_helpers.py` (`RICH_TOKENS`), `data/seed_grids_16x16/`
