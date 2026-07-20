# Experiment Report: The Reachability Probe — 45 Bins Won, 95 Bounded, the Emptiness Structured (Cycle 20 · SHARED · J1)

Date: 2026-07-20

## WHY

I5b named the bound: coverage is limited by the generators'
descriptor RANGE (374/512 bins at 3× volume), and whether the
unreached bins are reachable by ANY validator-passing 16×16 grid was
the next sharp question. J1 probes it under the constraint that
matters: the ENGINE'S OWN move set — the promoted generation model +
`generate_candidate` + package validation — because that is the move
set the game's evolution actually breeds with. No hand-painted
exceptions: every candidate the probe considers comes out of
`generate_candidate`.

## WHAT

`labs/map_elites_archive/reachability_probe.py` (RED first, 6 pins —
witnesses must pass the package validator AND recompute into their
claimed bin; unreached bins record the full budget and best distance;
caps are named, never silent; twin runs byte-equal): per unreached
bin, a guided descent — starting elites are the nearest valid pool
grids, children come from `generate_candidate` seeded
deterministically, the elite pool keeps the closest, and the search
stops at a witness or at budget.

**Measured at full scale** (pool 9,000 · budget 200/bin):

- Generators reach **372/512** (the I5b-level observation on this
  stream).
- The probe reached **45 more** — 417/512 now PROVEN reachable, each
  with a committed validator-passing witness whose descriptor
  recomputes into its bin.
- **95 bins stay unreached within budget** — a measured bound, not an
  impossibility proof.
- **The emptiness is structured, not scattered**: unreached bins
  concentrate at extreme symmetry (bins 6–7 hold 46 of 95) and
  extreme visual complexity (bins 0 and 7 hold 47 of 95) — the
  corners of the octile space, where a generator that cannot spell
  limbs, decorations, or fine asymmetries has nothing to reach with.

The J2 measurement (same day) supplies the named candidate cause: the
constrained path's 5-token alphabet erases the motion vocabulary in
projection. The J2 increment's "descriptor support widened" gate is
exactly where this probe's 95-bin bound gets its next test.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_reachability_probe.py"
ImportError: cannot import name ... from 'reachability_probe'   # RED: module absent
# after implementation:
Ran 6 tests ... OK
PS> python -B labs/map_elites_archive/reachability_probe.py
# generators reach 372/512; the probe reached 45 more of 140 probed bins
# under the engine's own move set; 95 stay unreached within budget 200
```

## HONEST REMAINDER

1. **95 bins bounded, not proven empty** — the budget is 200
   engine-moves per bin from nearest-neighbor starts; a
   vocabulary-complete generator (J2) re-runs this probe as its own
   gate evidence.
2. **The witnesses are evidence, not corpus members** — promoting any
   into seed/exemplar corpora is a curation decision with its own
   record.
3. **Reachable ≠ reached in play** — the evolve loop's selection
   pressure decides what players actually see; J3's novelty gate owns
   that trade.

## Sources

- `audits/TODO.md` (cycle 20 J1)
- `labs/map_elites_archive/reachability_probe.py` (+ `test_reachability_probe.py`)
- `data/archives/reachability_probe_stage0.json` (the witnesses + the axis-emptiness table)
- `research/experiment_reports/2026-07-20-occupancy-saturation.md` (I5b — the bound this probes), `2026-07-20-role-emission.md` (J2 — the named cause)
- `packages/mecha_engine/src/mecha_engine/generation/generate.py` (the move set)
