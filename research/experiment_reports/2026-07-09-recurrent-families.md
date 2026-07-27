# Experiment Report: The Recurrent Families — 52 Across All Ten Runs (Cycle 13 · ENGINE · E5)

Date: 2026-07-09

## WHY

The dossier's MAP-Elites gate ends on the species-memory clause: the
archive must be diverse enough that "at least five recurrent families"
can be distinguished. The gap table demands they be identified "across
independent seeded runs (lineage/descriptor clustering over the
archive's elites); family recurrence recorded, not curated." E5 is the
measurement — and the thesis stake is real: if independent evolution
runs do NOT rediscover the same morphological families, "species
memory" is a story, not a property.

## WHAT

`labs/map_elites_archive/recurrent_families.py` (+ tests), producing
`data/archives/recurrent_families_stage0.json`:

- **Family** = a coarse cell of the E1 scale descriptor space — each
  8-bin axis halved (factor 2), 4×4×4 = 64 morphological cells over
  (symmetry, visual complexity, behavior neediness).
- **Recurrent** = occupied by at least one elite in EVERY independent
  seeded run. The family list is the deterministic intersection —
  nothing curated, no manual selection anywhere.
- **Input**: E4's committed artifact — ten independent 20,480-
  evaluation runs, each recording its full elite roster (grid_id,
  descriptor, axis values, morphology signature hash).
- Descriptor clustering, not parent-chain lineage: the WFC parent path
  retrains on the whole elite pool, so children carry no single parent
  (recorded since E3).
- Per-family characterization recorded for the deferred human check:
  per-run counts, pooled axis-value means, mean fitness, one exemplar
  grid id per run.

## RESULTS

- **52 recurrent families across ALL TEN independent seeded runs — the
  documented ≥5 gate is met tenfold.** This is the strict intersection
  (a family missing from even one run is excluded).
- Per-run family counts are remarkably stable: 53–56 coarse cells
  occupied per run, of which 52 are common to all ten. Independent
  evolution runs rediscover essentially the same morphological
  structure — the species-memory property, measured.

> **SUPERSEDED BY REGENERATION, noted 2026-07-27** (cycle 23 M4 —
> `2026-07-27-family-ancestry.md`). **The committed artifact now says
> 54, not 52, and per-run counts 57–58, not 53–56.** The numbers above
> are what this study measured under the *pre-DR-0038* vocabulary; when
> the DR 0038/0039 vocabulary landed, E4's elite rosters regenerated and
> this artifact regenerated with them — commit `f8c171b`'s own message
> records *"recurrent families 52 → 54 (gate MET)"*. **The regeneration
> was recorded; the prose was not updated**, so `52` propagated into the
> Phase-E gate, DR 0032, the repertoire-browser report, L2, the Phase-L
> gate, `audits/TODO.md` and `docs/gap-analysis.md`. Nothing above is
> retracted: it stays true of the vocabulary it was measured under, and
> the gate's verdict is unchanged (met, by an even wider margin). M4
> reads the count from the artifact rather than from prose, which is how
> it surfaced.
- With E4, the dossier's four-clause MAP-Elites gate now reads:
  coverage MET (2.2×), best-fitness MET (identical), families MET
  (10×), GA-advantage REFUTED (+22.6% vs ≥25%, DR 0032's disposition).

## VERIFICATION

RED (the suite fails before the module exists):

```powershell
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_recurrent_families.py"
ModuleNotFoundError: No module named 'recurrent_families'
FAILED (errors=1)
```

GREEN (after implementation + the artifact over E4's ten rosters):

```powershell
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_recurrent_families.py"
Ran 12 tests in 0.013s

OK
```

Lab:

```powershell
PS> python -B labs/map_elites_archive/recurrent_families.py
{
  "family_gate": 5,
  "recurrent_family_count": 52,
  "gate_met": true
}
[56, 53, 55, 55, 55, 54, 55, 54, 55, 55]
52 recurrent families across 10 independent seeded runs against the documented >= 5 gate — the gate is MET.
```

## BLOCKED STATES (honest remainder)

- `human_distinguishability_not_collected` — the dossier's "reliably
  distinguish" reading is owner-deferred survey territory, never a
  blocker; the per-family axis means and exemplars are its prepared
  material.

## Sources

- `labs/map_elites_archive/recurrent_families.py`
- `labs/map_elites_archive/test_recurrent_families.py`
- `data/archives/recurrent_families_stage0.json`
- `research/algorithm_cards/recurrent_families.md`
- `data/archives/coverage_qd_gates_stage0.json` (the ten rosters)
- `research/decision_records/0032-map-elites-ga-gate-disposition.md`
- `docs/project-research/deep-research/01/deep-research.md`
- `audits/TODO.md` (cycle 13 E5)
