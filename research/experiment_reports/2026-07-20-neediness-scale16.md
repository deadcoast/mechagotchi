# Experiment Report: behavior_neediness at 16×16 — Measured, Recalibrated, and the Occupancy Link (Cycle 19 · SHARED · I5a)

Date: 2026-07-20

## WHY

The Phase-E gate named two standing engine remainders: **behavior_neediness
is mass-dominated at 16×16** ("a recalibration candidate with its own
evidence") and **occupancy saturation** (the WFC parent path plateaus
~55% coverage by ~generation 50). I5's charter: measure them with
honest findings — closures where the numbers close them, sharper
named remainders where they don't.

The game reason the axis matters: behavior_neediness is a niche
dimension of the archive the game's evolution surfaces consume. A
collapsed axis means fewer distinct survivors — less player-visible
variety in the living ecosystem (DR 0017's duality). And at 16×16 —
the ratified default canvas (DR 0029) — the axis WAS collapsed.

## WHAT

**The defect, measured** (`labs/map_elites_archive/neediness_scale16.py`,
both committed seed corpora, stdlib Pearson): at the 8×8 reference
canvas the sensor signal leads (r_sensors +0.870 vs r_mass −0.703);
at 16×16 under the original formula that inverts — r_mass **−0.726**
dominates r_sensors +0.530 and values hit the clamp floor (min 0.00) —
because the −0.01·mass coefficient was calibrated against 8×8 masses
and 16×16 masses are ~4× larger.

**The recalibration — the cycle 09 A4 pattern exactly** (reference-
canvas scaling, DR 0036): `mass_term = body_mass * 0.01 * (64 / area)`.
Pre-registered gates, all MET on the engine's numbers:

- `identity_8x8`: max abs diff **0.0** over the 8×8 corpus — and
  `map_elites_extended_stage0.json` regenerates BYTE-IDENTICAL (the
  identity proven at the data level).
- `mass_domination_reduced`: |−0.407| < |−0.726|.
- `sensor_signal_present`: r_sensors **+0.904** — the reference
  structure returns (sensors lead again).

Applied at BOTH parity sites (lab `_behavior_neediness` + package
`behavior_neediness`) with the application pinned; the measurement lab
freezes the ORIGINAL formula verbatim so the artifact keeps meaning
what it measured, and self-checks the live sites
(`application.lab_site_matches` / `package_site_matches` — computed,
never asserted).

**The measured occupancy link.** Regenerating the 512-niche geometry
(`niche_scale_archive_stage0.json`) under the recalibrated axis:

- distinct neediness octile edges 6 → **7**; the artifact's recorded
  "cannot support 8 distinct octile edges" degeneracy note REMOVED —
  by the lab's own honesty check, not by hand.
- coverage 274 → **319 of 512 niches (0.535 → 0.623)** over the same
  3,000 candidates: the Phase-E occupancy plateau was PARTLY the
  collapsed neediness axis wasting a descriptor dimension. One named
  remainder was feeding the other.

**The regenerated downstream evidence** (all 16×16-dependent archive
artifacts rerun under the recalibrated axis; 8×8-era artifacts
unchanged by the identity):

- `evaluation_loop_scale_stage0.json`: coverage improves at EVERY
  generation checkpoint (e.g. 0.361 → 0.396 at the first), final
  **0.619** over the 20,480-evaluation loop — the plateau moves
  without touching the parent path.
- `coverage_qd_gates_stage0.json`: the documented coverage gate stays
  MET at the higher coverage (mean 0.604); **the GA-advantage clause
  stays REFUTED — recorded, not fudged**: the recalibration narrows
  the gap (+22.6% → +24.4% vs the ≥25% documented bar) without
  flipping it. DR 0032's disposition stands; neither named re-opener
  (direction reversal, family collapse) triggers.
- `recurrent_families_stage0.json`: regenerates byte-identical (the
  families measurement does not ride the neediness axis).

## Verification

```powershell
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_neediness_scale16.py"
ImportError: cannot import name ... from 'neediness_scale16'   # RED: module absent
# after the measurement lab:
Ran 7 tests ... OK
# the application pin added, RED before the parity-site change:
Ran 8 tests ... FAILED (failures=1)   # ApplicationTests: both sites still unscaled
# after DR 0036's change at both sites:
Ran 8 tests ... OK
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_*.py"
Ran 107 tests ... OK
PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
Ran 295 tests ... OK
PS> python -B labs/map_elites_archive/neediness_scale16.py
# gates: identity_8x8 true · mass_domination_reduced true · sensor_signal_present true -> recalibrate
PS> python -B labs/map_elites_archive/niche_scale_archive.py
# 319 of 512 niches occupied (coverage 0.623047) over 3000 evaluated candidates
```

## HONEST REMAINDER

1. **Occupancy saturation is NARROWED, not closed** (I5b): coverage
   moved 0.535 → 0.623 by un-collapsing the axis, but what bounds
   coverage past ~62% stays open with the Phase-E candidates named
   (novelty pressure, re-derived edges, mutation-heavy arms) — a
   measurement with its own evidence.
2. **The correlation instrument is the seed corpora**, not archive
   run populations; the regenerated niche-scale artifact is the
   archive-population confirmation (octile edges 6 → 7).
3. **The axis fully recovers the 8-bin geometry**: 8 bins need 7
   octile edges, and the recalibrated axis derives 7 of 7 distinct
   (`supports_full_bins: true`, up from 6 of 7) — no ceiling remains
   on this axis; the correction is recorded because an earlier draft
   of this report misread 7 edges as a ceiling.

## Sources

- `audits/TODO.md` (cycle 19 I5)
- `research/decision_records/0036-neediness-scale-recalibration.md`
- `labs/map_elites_archive/neediness_scale16.py` (+ `test_neediness_scale16.py`)
- `labs/map_elites_archive/extended_descriptors.py`, `packages/mecha_engine/src/mecha_engine/archive/_metrics.py` (the parity sites)
- `data/archives/neediness_scale16_stage0.json`, `data/archives/niche_scale_archive_stage0.json`
- `research/experiment_reports/2026-07-09-phase-e-gate.md` (the named remainders)
