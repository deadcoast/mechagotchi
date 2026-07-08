# Development TODO — Cycle 13: ENGINE track · Phase E — evolution at documented scale

**Build track: THE ENGINE** (of the two builds — engine and game — per
`docs/gap-analysis.md` §0; the engine completes before the game's
playable front end is built, and no feature in this cycle is "the
application").

Source: `docs/gap-analysis.md` (Phase E), opened by the Phase-D gate
(`research/experiment_reports/2026-07-08-phase-d-gate.md`, cycle 12).
The gap table's evolution row: the documents specify 8×8×8 ≈ 576
niches, populations ~256, 20k–50k evaluations, coverage ≥25%, ≥5
recurrent families, and MAP-Elites ≥25% coverage over a GA baseline —
what exists ran at population 4, 3 generations, a handful of niches:
~3 orders of magnitude below the documented regime. Standing seams
this cycle consumes: the promoted `archive` (calibrated 7D
descriptors, elite rules), `generation` (WFC adopted, DR 0031),
`runtime.evolve`, the kept fleet threads (D6 verdicts: hunger/energy
forecasts, interaction timing, animation bandit, HMM mood), and the
D5/D6 harness discipline (wall-clock FIRST — 20k+ stress-probed
lifecycle evaluations are the strongest NumPy trigger yet, DR 0028).

- [ ] **E1 · The archive at documented niche scale.** The descriptor
  binning that yields the documented ~576-niche space from the
  calibrated descriptors; archive mechanics proven at hundreds of
  niches (insertion, elite replacement, coverage/QD summaries);
  wall-clock pilot for the evaluation unit measured FIRST. RED-first;
  triad.
- [ ] **E2 · Generation throughput at population scale.** WFC
  candidate generation at populations in the hundreds per generation
  (parents from archive elites per the promoted evolve semantics);
  validity and uniqueness rates recorded at scale; throughput
  measured against the dossier's ≤250 ms bar.
- [ ] **E3 · The evaluation loop at 20k+ evaluations.** The full
  evolve loop at documented scale (20k–50k stress-probed lifecycle
  evaluations); wall-clock measured FIRST at pilot scale — if stdlib
  cannot hold, the NumPy decision record cites the measurement
  (DR 0028); determinism pinned under seeds.
- [ ] **E4 · The coverage/QD gates + the GA baseline.** The
  documented gates: coverage ≥25% of the niche space; QD score and
  per-axis spread recorded; MAP-Elites ≥25% coverage over a plain GA
  baseline run under identical budgets (the documented comparison).
- [ ] **E5 · The recurrent families.** ≥5 recurrent morphological
  families identified across independent seeded runs (lineage/
  descriptor clustering over the archive's elites); family
  recurrence recorded, not curated.
- [ ] **E6 · The Phase-E gate.** One consolidated gate report with
  the honest remainder list; gap-analysis Phase E checked off only
  when green; cycle 13 archived; cycle 14 opens Phase F — the
  playable game (the GAME track begins).

## Standing note

`docs/gap-analysis.md` governs cycle planning until retired (Phase G
alpha). The engine-truth law (DR 0021), the identity constraint, and
the triad discipline are unchanged. CuBFF real ingest is REQUIRED
late-stage (Phase G). Apache-2.0; dependencies permitted with
justification (DR 0028). Size-parametric, never size-replacing (DR
0029). Named remainders standing: evolve's inner loop on WFC (this
cycle may finally provide its evidence — E2/E3 measure the constrained
vs WFC parent path where the loop demands it); the hybrid re-opener;
limb/joint per-role motion; live clip driving; clip-frame exports;
the fleet's decision-seam welfare (~0 over frozen rules — its value
cashes out at the game's consumers, Phase F); dropped threads stay out
of default profiles (D6).

## Sources

- `docs/gap-analysis.md` (Phase E)
- `research/experiment_reports/2026-07-08-phase-d-gate.md` (the opener)
- `docs/project-research/deep-research/01/deep-research.md` (the evolution regime, coverage/QD/family gates)
- `packages/mecha_engine/src/mecha_engine/{archive,generation,runtime}/` (the promoted surfaces)
- `data/micro_threads/ablation_gates_stage0.json` (the kept fleet)
- `research/decision_records/0028`, `0029`, `0031`
