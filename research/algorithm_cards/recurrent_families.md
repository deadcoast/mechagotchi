# Algorithm Card: Recurrent Morphological Families

## Purpose

Measure the dossier's species-memory clause — at least five recurrent
morphological families — across independent seeded evolution runs, by
deterministic descriptor clustering over the archives' elites;
recurrence recorded as the strict intersection, never curated
(gap-analysis Phase E, E5).

## Mathematical basis

- Family = coarse cell of the E1 scale descriptor space: each 8-bin
  axis integer-divided by 2 → 4×4×4 = 64 cells over (symmetry, visual
  complexity, behavior neediness).
- Recurrence = set intersection of occupied cells across all runs.
- Characterization: per-run counts, pooled axis-value means, mean
  fitness, one exemplar per run.

## Inputs

E4's per-seed elite rosters (ten independent 20,480-evaluation runs).

## Outputs

The recurrent-family list with characterizations; per-run family
counts; the ≥5 gate verdict.

## Strengths

- Fully deterministic and curation-free; the strictest recurrence rule
  (ALL runs).
- Ten independent runs make recurrence a strong claim (not two-run
  coincidence).

## Weaknesses

- Coarse-cell families are an operationalization of "family"; human
  distinguishability (the dossier's phrasing) stays deferred with its
  material prepared.
- Descriptor clustering, not parent-chain lineage (the WFC parent path
  has no single parent — recorded in E3).

## Failure modes

- Degenerate axes could merge families (behavior_neediness spans 7 of
  8 fine bins; its coarse axis still discriminates 4 cells).
- A coarser/finer factor changes counts — the factor (2) is fixed and
  recorded; re-derivation would be its own recorded decision.

## Integration risk

None (analysis lab over committed artifacts).

## License status

Repo Apache-2.0 (DR 0028); stdlib only.

## Prototype result

52 recurrent families across all ten runs vs the documented ≥5 (met
10×); per-run occupied-family counts stable at 53–56 of 64.

> **SUPERSEDED BY REGENERATION, noted 2026-07-27** (cycle 23 M4): the
> committed artifact says **54**, per-run counts **57–58**. The figures
> above are the pre-DR-0038 vocabulary's; the artifact regenerated with
> E4's rosters at commit `f8c171b` (*"recurrent families 52 → 54"*) and
> the prose was never updated. The gate verdict is unchanged (met, by a
> wider margin). See `research/experiment_reports/2026-07-27-family-ancestry.md`.

## Decision

**adopt** (the species-memory clause is measured and MET; feeds the
Phase-E gate and DR 0032's family clause).

## Go-No-Go gate

GO: gate met at the strict intersection. NO-GO trigger: family
collapse at future scales (DR 0032's re-opener (b)).

## Sources

- `labs/map_elites_archive/recurrent_families.py` (+ `test_recurrent_families.py`)
- `data/archives/recurrent_families_stage0.json`
- `research/experiment_reports/2026-07-09-recurrent-families.md`
- `research/decision_records/0032-map-elites-ga-gate-disposition.md`
