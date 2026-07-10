# Experiment Report: The Evaluation Loop at Documented Scale — Stdlib Holds at 20k (Cycle 13 · ENGINE · E3)

Date: 2026-07-09

## WHY

The dossier's MAP-Elites archive test budgets 50,000 evaluations per
run; the gap table demands 20k–50k stress-probed lifecycle evaluations
where everything before this cycle ran at population 4 × 3 generations.
E3 is the scale proof: the full generational loop at the documented
budget, with the wall-clock measured FIRST against a bound
pre-registered before the run (DR 0028 — the TODO named this "the
strongest NumPy trigger yet"), and determinism pinned under seeds.

## WHAT

`labs/map_elites_archive/evaluation_loop_scale.py` (+ tests), producing
`data/archives/evaluation_loop_scale_stage0.json`:

- **The loop.** Bootstrap population (constrained + WFC halves, E1's
  mixed composition) → generations of [parents = archive elites in the
  promoted evolve ordering → WFC model retrained on the elite pool →
  population generated → 24-tick stress-probed lifecycle scoring
  (calibrated Stage 0 fitness) → elite insertion through E1's
  package-parity mechanics under the frozen empirical edges] until the
  budget is reached.
- **The parent path is WFC** — E2's measured evidence, cited in the
  protocol. SLIP alignment stays out of scope (the standing E2 note).
- **DR 0028, in order:** pilot measured first; the bound
  pre-registered in code before the run (`PRE_REGISTERED_BOUND_S =
  600`, the D5 precedent); the full run's wall-clock recorded against
  it in the artifact's `measured` section.
- **Determinism pinned:** identical seeds reproduce the trajectory and
  every elite byte-for-byte (test-pinned); the protocol records
  everything needed to replay.
- **Elite records for E5:** descriptor, axis values, and a morphology
  signature hash per elite — family clustering inputs without shipping
  grids.

## RESULTS

Full scale: population 256, 79 generations, **20,480 stress-probed
lifecycle evaluations**, zero WFC collapse failures.

- **Stdlib HOLDS: 174.12 s measured against the pre-registered 600 s
  bound** (pilot 6.8 ms/evaluation → projections 129 s @ 20k /
  323 s @ 50k — even the 50k budget fits the bound). The NumPy trigger
  did not fire; DR 0028 requires no dependency record.
- **Final archive: 281 of 512 niches (coverage 0.549)**, QD score
  222.1, best fitness 0.9836, 682 elite replacements over the run.
  Formal gate judgment (≥25% coverage, the GA baseline) is E4's; the
  raw coverage sits at ~2.2× the documented figure.
- **The honest saturation observation:** occupancy plateaus at ~281
  niches well before the budget ends (it reaches 281 around generation
  ~50 of 79); late generations contribute fitness refinements
  (replacements: 4–5 per 256-candidate generation by the end) rather
  than new niches. The WFC parent path converges toward its elite
  pool's distribution — coverage growth beyond ~55% will need
  something the current loop does not have (novelty pressure, edge
  re-derivation, or mutation-heavy arms). Recorded for E4/E5's
  reading, not smoothed over.
- behavior_neediness still reaches only 7 of 8 bins (the E1 degenerate
  axis carries through, as expected).

## VERIFICATION

RED (the suite fails before the module exists):

```powershell
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_evaluation_loop_scale.py"
ModuleNotFoundError: No module named 'evaluation_loop_scale'
FAILED (errors=1)
```

GREEN (after implementation + the full-scale artifact run):

```powershell
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_*.py"
Ran 74 tests in 7.793s

OK
```

Lab (pilot first, the pre-registered bound, the measured full run):

```powershell
PS> python -B labs/map_elites_archive/evaluation_loop_scale.py
...
{
  "wall_clock_s": 174.12,
  "meets_bound": true,
  "bound_s": 600.0
}
The loop ran 20480 stress-probed lifecycle evaluations over 79 generations of population 256: 281 of 512 niches occupied (coverage 0.548828), QD score 222.079495, best fitness 0.983616 — deterministic under seed 20260709.
```

## BLOCKED STATES (honest remainder)

- `coverage_qd_gates_not_judged_here` — E4 runs the documented gates
  including the plain-GA baseline under identical budgets.
- `package_scale_geometry_seam_not_promoted` — still lab-side; named
  for the Phase-E gate.
- `slip_alignment_not_enforced_in_this_harness` — the standing E2
  scope note.

## Sources

- `labs/map_elites_archive/evaluation_loop_scale.py`
- `labs/map_elites_archive/test_evaluation_loop_scale.py`
- `data/archives/evaluation_loop_scale_stage0.json`
- `research/algorithm_cards/evaluation_loop_scale.md`
- `research/experiment_reports/2026-07-09-niche-scale-archive.md` (E1)
- `research/experiment_reports/2026-07-09-wfc-population-throughput.md` (E2)
- `packages/mecha_engine/src/mecha_engine/generation/`
- `research/decision_records/0028-license-and-dependency-policy.md`
- `docs/project-research/deep-research/01/deep-research.md`
- `audits/TODO.md` (cycle 13 E3)
