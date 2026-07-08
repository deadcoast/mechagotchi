# Experiment Report: Validator Floor and Generation at 16×16 (Cycle 09 · ENGINE · A3, first slice)

Date: 2026-07-08

## WHY

A1 ratified the size-parametric core floor (DR 0029) and A2 delivered
the 16×16 corpus, but the engine still enforced the 8×8 constant at
every size and the generation model hard-pinned `width=8, height=8`.
A3's charter: re-prove the promoted pipeline at 16×16, size-parametric
and never size-replacing, RED-first, with every 8×8 pin unbroken.

## WHAT — this slice

1. **The validator floor** (lab `validator.py` + promoted
   `mecha_engine.genome.validation`, identical text): a new
   `body_core_min_cells(width, height) = max(4, 18·w·h // 256)` applied
   in `validate_grid`. At 8×8 it reproduces the constant 4 and the
   exact historical error string; malformed sizes fall back to the 8×8
   floor, preserving the historical error path. The lab evidence
   function (`invariant_scaling.body_core_min_cells`) now DELEGATES to
   the validator's law, so evidence and enforcement cannot drift.
2. **The parity pin widened**: the 16×16 corpora (50 seeds + 200
   invalid) joined `test_package_genome_parity` — lab and package
   validators must agree file-for-file (error strings included) over
   all 500 corpus files at both ratified scales.
3. **Generation size-parametric**: `train_generation_model` (package)
   and `train_constraints` (lab) derive their dimensions from the
   training corpus — an 8×8 corpus trains the byte-identical historical
   model; a mixed-size corpus fails loudly ("seed corpus must share a
   single grid size") instead of silently training wrong-position
   statistics. The stabilizer, matrix projections, and grid builders
   were already size-generic (they read `grid_size`), so candidate
   emission at 16×16 needed no further change.
4. **The 16×16 generation gate**: contract probe `scale_16` (package
   driver) and the lab twin — model dimensions 16×16, a 25-candidate
   batch all valid at [16,16], every candidate's required core over the
   ratified floor 18, unique ids, mixed-size rejection.

## FINDINGS

- Both validators agree over all 500 corpus files at both scales; the
  8×8 outcomes are byte-identical to the pre-change validator (the 205-
  and 290/291-test suites passed unmodified apart from the new tests).
- Constrained generation at 16×16 emits 100% valid candidates over the
  ratified floor with no changes to the proposal loop — the
  validator-gated stabilizer design carried the scale change.
- **Honest generation limitation** (recorded for Phase B): the token
  alphabet is still {., B, A, E, M}, so candidates bred from rich
  16×16 parents (shell/limb/antenna creatures) keep the core, eyes,
  and mouth but lose the rich-vocabulary cells. The WFC/constraint
  layer with the full vocabulary is exactly Phase B's charter.
- **The stress-probe renormalization is NOT in this slice, on
  evidence**: DR 0014 anticipated a `mass/(w·h/4)`-family denominator,
  but the A1/A2 measurements show the 16×16 corpus median core
  FRACTION is higher than 8×8's (51.5/256 = 0.201 vs 10/64 = 0.156), so
  `mass/64` would shift the load distribution upward and saturate heavy
  or asymmetric creatures (e.g. mole's 68-cell core → 1.06 on the mass
  term alone). Renormalizing by fiat would repeat the exact mistake DR
  0014 warned against; the denominator needs its own lab measurement
  (load distribution + survival-bin spread at 16×16), which is the next
  A3 increment together with repair retraining, lifecycle re-derivation,
  and size-relative SLIP bounds.

  *Correction (same day, after the measurement ran):* the implied
  prediction that `mass/64` would fail its gates was **wrong**. The
  stress_probe_scaling lab measured it: 18% of the corpus saturates,
  but the survival axis stays alive (bins {2,4}, matching the 8×8
  baseline) and every gate passes — while the untouched `/16` measured
  as a TOTAL collapse at 16×16 (98% saturation, one bin). `mass/(w·h/4)`
  was adopted. See
  `research/experiment_reports/2026-07-08-stress-probe-scaling.md`.

## Verification

RED (floor tests before the law existed):

```powershell
PS> python -B -m unittest test_validator
ImportError: cannot import name 'body_core_min_cells' from 'validator'
FAILED (errors=1)
```

RED (generation contract before size derivation):

```powershell
PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_generation_contract.py"
AssertionError: 16 != 8   (scale_16.model_width)
FAILED (failures=1)
```

GREEN (both suites after the port; +4 lab validator/parity tests,
+1 lab generation gate, +1 package contract test):

```powershell
PS> python -B -m unittest discover -s labs/grid_genome -p "test_*.py"
Ran 206 tests in 7.357s
OK
PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
Ran 291 tests in 8.478s
OK
```

Full sweep after the engine change (16 labs green, workshop 58, CLI 21,
promotion gate steady at nine promotion-ready):

```powershell
PS> # every labs/* suite
architecture 14 OK · asset_pipeline 22 OK · cellular_automata 32 OK ·
ctm_ticks 4 OK · cubff_transducer 17 OK · datasets 22 OK · game_loop 81 OK ·
grid_genome 206 OK · lifecycle_sim 24 OK · map_elites_archive 24 OK ·
package_promotion 6 OK · readability_benchmark 42 OK · repair_boundary 4 OK ·
runtime_integration 65 OK · slip_validator 24 OK · workshop_editor 307 OK
```

## Sources

- `labs/grid_genome/validator.py`, `labs/grid_genome/test_validator.py`
- `packages/mecha_engine/src/mecha_engine/genome/validation.py`
- `labs/grid_genome/test_package_genome_parity.py`
- `packages/mecha_engine/src/mecha_engine/generation/model.py`
- `labs/grid_genome/constrained_generator.py` (+ `test_constrained_generator.py`)
- `packages/mecha_engine/tests/test_generation_contract.py` (+ `helpers/generation_contract_driver.py`)
- `research/decision_records/0029-16x16-default-grid-scale.md`
- `research/decision_records/0014-grid-size-commitment.md` (the /16 warning this slice honors)
- `data/seed_grids_16x16/`, `data/invalid_grids_16x16/`
- `audits/TODO.md` (cycle 09 A3), `docs/gap-analysis.md` (Phase A)
