# Experiment Report: The Coverage/QD Gates + the GA Baseline — Three Gates Met, One Refuted (Cycle 13 · ENGINE · E4)

Date: 2026-07-09

## WHY

The dossier's MAP-Elites archive test is the documented comparison the
evolution track has owed since the gap analysis: coverage ≥25% of the
niche space, MAP-Elites ≥25% greater archive coverage than a plain GA
at the same budget, best fitness within 10% of the strongest
comparator. E4 judges all of it on E3's instrument, at the documented
protocol, with the rule pre-registered and the verdict recorded
whichever way it lands.

## WHAT

`labs/map_elites_archive/coverage_qd_gates.py` (+ tests), producing
`data/archives/coverage_qd_gates_stage0.json`:

- **MAP-Elites arm** — E3's `run_evaluation_loop`: the generational
  WFC parent path over the E1 scale geometry, 20,480 stress-probed
  lifecycle evaluations per seed.
- **Plain GA arm** — the classical control under the IDENTICAL budget,
  seed, bootstrap, variation operator (WFC retrained on selected
  parents — the dossier's shared-inputs design: every comparator
  consumes the winning generator), and evaluation unit. The only
  difference is the mechanism under test: scalar truncation selection
  (top half by fitness), full generational replacement, no archive.
  GA coverage is read over its FULL evaluation history mapped into the
  512-niche space — the GA-favorable reading, pre-registered.
- **Protocol**: the documented ten paired seeds per comparator at the
  documented 20k budget (twenty full-scale runs, 2,318 s total).
  History recorded in the artifact: a three-seed compute adaptation
  ran first and returned a near miss on the advantage gate (+22.9%);
  the escalation to the documented ten seeds was fixed in advance with
  consecutive seeds, verdict operative whichever way it landed.

## RESULTS (the ten-seed verdict)

- **Coverage gate: MET** — MAP-Elites mean coverage 0.549 vs the ≥0.25
  documented gate (2.2×). QD score and per-axis bin spread recorded
  per run.
- **Best-fitness clause: MET** — mean best fitness 0.9785, IDENTICAL
  across arms (shared bootstrap + shared operator: the peak creature
  is found either way; the archive costs nothing at the top).
- **The GA-advantage gate: REFUTED — +22.6% vs the documented ≥25%**,
  and it converged (three seeds +22.9%, ten seeds +22.6%): a real miss
  by ~2.4 points, not noise. GA history-coverage mean 0.448. The
  mechanism: WFC retrained even on scalar-selected parents is itself a
  strong illuminator, so the archive's *relative* advantage compresses
  under the shared-operator design — analysis and disposition in
  **DR 0032** (MAP-Elites remains adopted on the documented
  architecture's own terms; the refutation recorded with a named
  re-opener, the Phase-B hybrid precedent).
- Per-seed elite rosters (grid_id, descriptor, axis values, signature
  hash) are recorded in the artifact per run — E5's clustering inputs.

## VERIFICATION

RED (the suite fails before the module exists):

```powershell
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_coverage_qd_gates.py"
ModuleNotFoundError: No module named 'coverage_qd_gates'
FAILED (errors=1)
```

GREEN (after implementation + the ten-seed artifact run):

```powershell
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_coverage_qd_gates.py"
Ran 13 tests in 0.647s

OK
```

Lab (the documented ten-seed protocol):

```powershell
PS> python -B labs/map_elites_archive/coverage_qd_gates.py --seeds 20260709 20260710 ... 20260718
...
A documented gate FAILED — recorded, not fudged: MAP-Elites coverage mean 0.549414 (gate >= 0.25); advantage over the plain GA 0.226242 (gate >= 0.25, GA history-coverage mean 0.448047); best fitness 0.978472 vs strongest 0.978472 (tolerance 0.1).
```

(One artifact correction recorded: the `measured.context` label string
was baked from a pre-edit module revision — "six runs/three seeds"
against `runs: 20` — and was patched to describe the actual twenty-run
configuration; the measured wall-clock value itself was untouched.)

## BLOCKED STATES (honest remainder)

- `ga_advantage_gate_refuted` — +22.6% vs ≥25%, converged at the
  documented protocol; disposition DR 0032 with its named re-opener.
- `recurrent_families_judged_separately` — E5 (the gate's fourth
  clause).
- `package_scale_geometry_seam_not_promoted` — standing; named for the
  Phase-E gate.

## Sources

- `labs/map_elites_archive/coverage_qd_gates.py`
- `labs/map_elites_archive/test_coverage_qd_gates.py`
- `data/archives/coverage_qd_gates_stage0.json`
- `research/algorithm_cards/coverage_qd_gates.md`
- `research/decision_records/0032-map-elites-ga-gate-disposition.md`
- `research/experiment_reports/2026-07-09-evaluation-loop-scale.md` (E3)
- `docs/project-research/deep-research/01/deep-research.md`
- `audits/TODO.md` (cycle 13 E4)
