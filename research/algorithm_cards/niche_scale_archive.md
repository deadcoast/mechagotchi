# Algorithm Card: Niche-Scale Archive (the documented 8×8×8 geometry)

## Purpose

The dossier's first-pass MAP-Elites descriptor space — symmetry, visual
complexity, neediness at 8 bins per axis (512 niches; the dossier's
"576-cell repertoire" figure recorded verbatim as a documented
discrepancy) — derived empirically from the calibrated descriptor
surfaces, with the promoted archive's elite mechanics proven at
hundreds of occupied niches and the Phase-E evaluation unit's
wall-clock measured first (gap-analysis Phase E, E1).

## Mathematical basis

- MAP-Elites (Mouret & Clune, arXiv:1504.04909): a repertoire keyed by
  discretized behavior descriptors; one elite per niche; strictly
  higher fitness replaces; coverage and QD score summarize
  illumination.
- Empirical quantile binning: interior octile edges via linear
  interpolation between closest ranks over measured axis distributions
  (the calibration spirit of CVT-MAP-Elites: bins shaped by where the
  population actually lives, not by assumed ranges).
- Axis metrics: mirror-symmetry ratio; silhouette Shannon entropy over
  row/column occupancy normalized by log2(w+h) (the readability
  feature); the calibrated behavior-neediness formula.

## Inputs

- A seeded derivation population and a DISJOINT evaluation population
  (constrained + WFC halves at 16×16 from the seed corpus).
- The LCD SLIP profile; per-candidate `rng_seed + index` streams;
  24-tick stress-probed lifecycle scoring (`score_extended_candidate`).

## Outputs

- Derived per-axis octile edges + degenerate-distribution diagnostics.
- A scale archive (elites keyed by 3-axis descriptor, event ledger,
  observed-bin spread) and its coverage/QD summary.
- The `measured` wall-clock section: ms per evaluation unit and 20k/50k
  projections.

## Strengths

- Geometry is the documented spec, not an invention; every axis is an
  existing canonical surface (no new statistics).
- Edges are measured, deterministic, and honest about degenerate axes.
- Elite decisions parity-pinned byte-equal to `mecha_engine.archive`
  under the extended geometry.

## Weaknesses

- Octile edges are calibrated to the current generators' distribution;
  a very different generator (Phase-E evolve at scale) may shift the
  distributions — E3/E4 re-read coverage on the frozen edges.
- `behavior_neediness` at 16×16 is mass-dominated and supports only 6
  distinct edges — the axis discriminates weakly at this grid scale.

## Failure modes

- Degenerate axis distributions collapse bins (observed and recorded on
  neediness); guarded by per-axis diagnostics, never silent.
- In-place accumulation trades the package's persistent-value API for
  scale; misuse outside the lab loop would alias state — decisions are
  parity-pinned and the package keeps its own contract.

## Integration risk

Medium: E3's evolve loop needs the scale geometry inside the engine
archive (a `mode`-style seam with its own spec update and gate). Until
promoted, the geometry is lab-side evidence only.

## License status

Repo Apache-2.0 (DR 0028); stdlib only; MAP-Elites is method-level
prior art (paper, no code dependency).

## Prototype result

274/512 niches occupied (coverage 0.535) over 3,000 candidates on the
disjoint evaluation population; 444 elite replacements, 0 invalid;
symmetry and visual complexity reach 8/8 bins, neediness 7/8.
Evaluation unit 6.29 ms at the 200-unit pilot → 125.8 s @ 20k / 314.5 s
@ 50k evaluations (stdlib holds for run-once builds; DR 0028
measurement recorded for E3's own decision).

## Decision

**adopt** (as Phase E's descriptor geometry and mechanics evidence;
engine promotion is E3's seam with its own gate).

## Go-No-Go gate

GO for E2/E3 consumption: occupancy ≥ 200 niches pinned by test against
the committed artifact; parity pin green; wall-clock recorded. NO-GO
triggers: parity drift against the package, or E4 coverage gates
falling below the documented ≥25% under the frozen edges without a
recorded re-derivation decision.

## Sources

- `labs/map_elites_archive/niche_scale_archive.py` (+ `test_niche_scale_archive.py`)
- `data/archives/niche_scale_archive_stage0.json`
- `research/experiment_reports/2026-07-09-niche-scale-archive.md`
- `docs/project-research/deep-research/01/deep-research.md`
- `packages/mecha_engine/src/mecha_engine/archive/store.py`
