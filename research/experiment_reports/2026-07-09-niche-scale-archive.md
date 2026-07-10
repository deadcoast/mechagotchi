# Experiment Report: The Archive at Documented Niche Scale (Cycle 13 · ENGINE · E1)

Date: 2026-07-09

## WHY

The gap table's evolution row is Phase E's reason to exist: the
documents specify a ~576-niche repertoire, populations ~256, 20k–50k
evaluations and the coverage/QD/family gates, while everything before
this cycle ran at population 4 over a handful of niches. E1 is the
foundation task: derive the DOCUMENTED descriptor geometry from the
calibrated descriptor surfaces, prove the archive mechanics at hundreds
of occupied niches, and measure the evaluation unit's wall-clock FIRST
(DR 0028) so E3's 20k+ loop starts from a measurement, not a hope.

The dossier's "MAP-Elites archive test" names the first-pass space
explicitly: THREE axes — symmetry, visual complexity, and neediness —
with **8×8×8 niches**. Its experiment table separately states the
coverage gate "≥ 25% on a **576-cell** repertoire after 20k
evaluations." 8×8×8 = 512, not 576. Both documented figures are carried
verbatim in the lab's `DOCUMENTED_REPERTOIRE_FIGURES`; the geometry
follows the explicit comparator spec (8 bins per axis, 512 niches) and
Phase-E coverage gates read against the geometry's own cell count. The
discrepancy is recorded, never averaged away.

## WHAT

`labs/map_elites_archive/niche_scale_archive.py` (+ tests), producing
`data/archives/niche_scale_archive_stage0.json`:

- **The scale geometry.** `symmetry` (the calibrated mirror-symmetry
  descriptor formula), `visual_complexity` (the readability feature
  extractor's `silhouette_entropy` — the dossier's own named complexity
  metric), `behavior_neediness` (the calibrated extended axis). No new
  statistics; every axis is an existing canonical surface.
- **Empirical octile bin edges.** Interior quantiles (linear
  interpolation between closest ranks) of the measured axis
  distributions over a seeded 600-candidate derivation population
  (constrained + WFC halves at 16×16), with per-axis
  degenerate-distribution diagnostics. Edges are DERIVED, never
  hand-set (the Phase-A discipline: measure, don't assume).
- **Package-parity mechanics.** The elite rule is the promoted
  archive's, verbatim: empty niche accepts the first valid candidate;
  strictly higher fitness replaces; equal fitness keeps the incumbent;
  invalid grids are blocked, never elites. A parity test rebuilds the
  package's extended-mode archive through the lab mechanics and pins
  elites and summary equal. One deliberate divergence for scale,
  documented: in-place accumulation instead of the package's per-insert
  deep copy (quadratic at 20k+ evaluations); DECISIONS are pinned
  identical.
- **Disjoint populations.** Edges derive from one rng stream; the
  archive is built from a different one (offset 1,000,003), so
  occupancy is never read off the calibration data.
- **The wall-clock pilot (FIRST).** The full Phase-E evaluation unit —
  constrained generation → validation → stress-probed lifecycle →
  descriptor → score → insert — timed at a 200-unit pilot with linear
  projections to the documented budgets.

## RESULTS

- **Occupancy at scale: 274 of 512 niches (coverage 0.535) over 3,000
  evaluated candidates** — the "hundreds of niches" claim is earned and
  pinned by a test reading the committed artifact (≥ 200). Event
  ledger: 274 first insertions, 444 elite replacements, 2,282
  kept-incumbent decisions, 0 invalid.
- **Bin spread:** symmetry 8/8, visual_complexity 8/8,
  behavior_neediness 7/8 bins reached.
- **The honest degenerate axis:** `behavior_neediness` at 16×16 is
  heavily skewed (mean 0.090, max 0.56 — the body-mass term dominates
  the calibrated formula at 16×16 masses), so its octile edges hold
  only 6 distinct values (first two duplicate at 0.0). Recorded in the
  artifact's diagnostics and blocked states — not jittered, not
  reweighted. A recalibration of the neediness formula at 16×16 is a
  candidate follow-up, but only with its own evidence.
- **Wall-clock (measured FIRST, machine-dependent, recorded in the
  artifact's `measured` section):** 6.29 ms per evaluation unit at the
  200-unit pilot (generation ≈ 4.0 ms, scoring+insert ≈ 2.3 ms).
  Projections: **125.8 s @ 20k evaluations, 314.5 s @ 50k**. Stdlib
  holds for run-once artifact builds; E3 judges its own bound against
  this measurement per DR 0028.
- The package suite (291 tests) and the full lab suite stay green; the
  parity pin proves the scale mechanics ARE the package's mechanics
  under the extended geometry.

## VERIFICATION

RED (the suite fails before the module exists):

```powershell
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_niche_scale_archive.py"
ModuleNotFoundError: No module named 'niche_scale_archive'
FAILED (errors=1)
```

GREEN (after implementation + the full-scale artifact run):

```powershell
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_*.py"
Ran 61 tests in 8.831s

OK
PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
Ran 291 tests in 14.297s

OK
```

Lab (pilot measured first, then the full-scale build):

```powershell
PS> python -B labs/map_elites_archive/niche_scale_archive.py
...
The documented 8x8x8 geometry is derivable from the calibrated descriptor surfaces with empirical octile edges, and the package-parity mechanics hold at scale: 274 of 512 niches occupied (coverage 0.535156) over 3000 evaluated candidates.
```

## BLOCKED STATES (honest remainder)

- `documented_figure_discrepancy_512_vs_576` — both dossier figures
  recorded verbatim; the geometry follows the explicit 8×8×8 comparator.
- `package_scale_geometry_seam_not_promoted` — the engine archive still
  exposes baseline/extended modes only; promoting the scale geometry is
  a package change with its own spec update and gate, consumed by E3's
  evolve run.
- `degenerate_axis_distributions` — behavior_neediness cannot support 8
  distinct octile edges on the derivation population; recorded, not
  jittered.

## Sources

- `labs/map_elites_archive/niche_scale_archive.py`
- `labs/map_elites_archive/test_niche_scale_archive.py`
- `data/archives/niche_scale_archive_stage0.json`
- `research/algorithm_cards/niche_scale_archive.md`
- `labs/map_elites_archive/extended_descriptors.py`
- `labs/readability_benchmark/learned_readability.py`
- `packages/mecha_engine/src/mecha_engine/archive/store.py`
- `docs/project-research/deep-research/01/deep-research.md` (the
  MAP-Elites archive test; the mecha_darwin experiment table)
- `docs/gap-analysis.md` (Phase E)
- `audits/TODO.md` (cycle 13 E1)
- `research/decision_records/0028-license-and-dependency-policy.md`
