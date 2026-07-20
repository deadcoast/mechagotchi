# Experiment Report: Occupancy Saturation — the Bound Measured and Named (Cycle 19 · SHARED · I5b)

Date: 2026-07-20

## WHY

Phase E named occupancy saturation (~55% plateau) with three candidate
levers; DR 0036 narrowed it (the collapsed neediness axis was wasting
a dimension — coverage moved to ~0.62) without answering what bounds
coverage PAST that. I5b instruments the question with pre-registered
readings: the support ceiling (the hard bound on any selection), the
in-sample edge lever (calibration's maximum), and the novelty-first
pool lever at the SAME scored budget.

The game stake: archive coverage is creature variety — the distinct
survivors the player's ecosystem can ever surface.

## WHAT

`labs/map_elites_archive/occupancy_saturation.py` (RED first, 6 pins
at test scale; the full-scale artifact
`data/archives/occupancy_saturation_stage0.json`), everything on the
niche-scale lab's own surfaces:

| Instrument | Measured |
| --- | --- |
| Baseline (3,000 candidates, derived edges) | **334/512 = 0.652** |
| Support ceiling (distinct descriptors in that population) | **334** |
| **Support utilization** | **1.0** |
| In-sample edges lever | +0.0117 (< the 0.02 bar) |
| Novelty-first from a 3× pool, same 3,000 scored | **374/512 = 0.730 (+0.078)** |
| Pool support (9,000 candidates) | 374 |

**The findings, judged by the lab's own rules:**

1. **Selection is NOT the bound — at all.** The baseline archive
   fills 100% of the descriptor bins its population produces
   (334 of 334). Nothing about elite competition wastes coverage.
2. **Calibration is not the lever** (+0.0117, under the
   pre-registered 0.02 bar) — and in-sample edges would be
   methodologically degenerate as practice anyway; measured only to
   size the lever.
3. **Generation diversity IS the lever**: novelty-first selection
   from a 3× generation pool captures EVERY descriptor the pool
   reaches (374 of 374) at the same scored budget — coverage 0.730.
   Generation is cheap; evaluation is the budget; the trade is
   explicit.
4. **The trade is recorded, not hidden**: the novelty arm's QD score
   is LOWER (223.85 vs 235.84) — niches filled by first-reachers
   trade mean elite fitness. Adopting novelty-first is a
   coverage-vs-QD decision for the evolution surface's own record.
5. **The deeper bound, named sharply**: even 9,000 candidates reach
   only **374 of 512** bins. The generators' descriptor RANGE — not
   selection, not calibration, not volume alone — is the remaining
   ceiling (138 bins unreached at 3× volume).

## Verification

```powershell
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_occupancy_saturation.py"
ImportError: cannot import name ... from 'occupancy_saturation'   # RED: module absent
# after implementation:
Ran 6 tests ... OK
PS> python -B labs/map_elites_archive/occupancy_saturation.py
# {"in_sample_edges": 0.011718, "novelty_pool": 0.078125}
# support_utilization 1.0
# measured_levers_move_the_plateau: novelty_pool
```

## HONEST REMAINDER

1. **The mutation-heavy arm stays named-not-run** — the constrained
   generator exposes no temperature knob; adding one is a generator
   change with its own record (and finding 5 predicts where its value
   would have to come from: reaching NEW bins, not re-rolling old
   ones).
2. **Novelty-first adoption is not decided here** — it moves coverage
   at a measured QD cost; the evolution surface (E3's loop, the
   game's repertoire) owns that trade with its own gate.
3. **The 138 unreached bins are uncharacterized** — whether they are
   reachable by ANY validator-passing 16×16 grid (vs geometrically
   empty corners of the octile space) is the next sharp question; a
   descriptor-targeted generation probe would answer it.

## Sources

- `audits/TODO.md` (cycle 19 I5b)
- `research/experiment_reports/2026-07-20-neediness-scale16.md` (I5a — the narrowing)
- `research/experiment_reports/2026-07-09-phase-e-gate.md` (the named remainder and its candidate levers)
- `labs/map_elites_archive/occupancy_saturation.py` (+ `test_occupancy_saturation.py`)
- `data/archives/occupancy_saturation_stage0.json`
- `research/decision_records/0036-neediness-scale-recalibration.md`, `0032-map-elites-ga-gate-disposition.md`
