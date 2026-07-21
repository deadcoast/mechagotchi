# Experiment Report: The Vocabulary-Complete Generation Alphabet — Five Gates Met, a Second Blindness Cured (Cycle 20 · SHARED · J2, implementation)

Date: 2026-07-20

## WHY

DR 0038 chartered the change with five pre-registered gates: the
constrained generation path — including the promoted
`generate_batch`, the surface the game's evolution breeds through —
projected every grid onto the 5-token alphabet and emitted the
DR 0011/0015 motion trio at exactly 0.0 against a training corpus
carrying it at 0.48. The implementation is judged by the gates, never
assumed.

## WHAT — the generation alphabet (DR 0038)

The ratified tables the seed corpus was AUTHORED with
(`RICH_TOKENS`/`RICH_ORGAN_ROLES`, one token per role) now drive the
generator paths at both parity sites: projection (every role its own
token; the standalone anchor role normalizes to "A"), statistics over
the full alphabet, and table-driven reconstruction whose canonical
organ order keeps legacy-only matrices byte-identical. The
resample-temperature knob rides as chartered (keyword-only, `None`
byte-identical, capped (0, 2], mirrored).

**The five gates, measured:**

| Gate | Bar | Measured | Verdict |
| --- | --- | --- | --- |
| 1 Emission | ≥ 0.24 | **0.512** (constrained AND promoted batch; corpus itself 0.48) | MET |
| 2 Validity | 1.0 | 300/300 at both sites (+ the batch's internal hard-fail) | MET |
| 3 Support widened | probe > 417/512 | **495 generator-reached; 503/512 proven** (9 remain, budget-bounded) | MET |
| 4 Additivity | legacy byte-identical | all three 8×8 generator artifacts regenerate with ZERO diffs | MET |
| 5 Parity | verbatim | lab 226 + package 295 green, incl. rich-corpus + temperature pins | MET |

## WHAT — the second blindness (DR 0039)

With generation cured, the game's era went EXTINCT (generation 0,
zero elites): the REPAIR stack (promoted module, its runtime twin,
the CA lab authority) was also 5-token, and its projection coerced
every rich cell to BODY — each damage/repair cycle rebuilt a rich
creature as a legacy blob (restoration 0.53, slip mass blown, nothing
admitted). The cure, mirrored at all three sites: vocabulary-
preserving projection/reconstruction (surviving cells keep their
roles verbatim), recorded perception coarsening by palette family
(the 5-class regrowth head stays; the 11-class retrain is a named
record), and the guard's ISLAND DRAIN — a structural, template-free
stall pass for the refilled-core-island defect single-flip
hill-climbing can never fix.

**Measured consequences:** the diagnostic era now runs with 12 elites
whose cells span the ENTIRE ratified vocabulary (antenna, body,
decoration, effect, eye, joint, limb, mouth, sensor, shell) — the
game breeds creatures it could never spell. The repair boundary
receded: session-band failures 0.0; only harshest-regime mortal
wounds fail (8.75%, cause anchor loss — the disconnected-core mode is
GONE), and the truncated-life replay fixture now rides that measured
residual boundary. The 16×16 generation bake-off verdict FLIPPED:
the constrained path, once ineligible on the very emission gap this
change cured, now WINS by the same pre-registered rule — recorded as
measured evidence; WFC's adoption (DR 0031) stands until its own
record revisits it.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/grid_genome -p "test_vocabulary_alphabet.py"
ImportError ... FAILED (failures=29, errors=7)      # RED: the alphabet absent
# after the lab implementation: Ran 10 tests ... OK
PS> python -B -m unittest discover -s labs/grid_genome -p "test_package_generation_parity.py"
FAILED (failures=25, errors=1)                      # RED: package unmirrored
# after the verbatim mirror: Ran 5 tests ... OK
PS> python -B labs/grid_genome/role_emission.py
# constrained 0.512333, wfc 0.800667, promoted_generate_batch 0.512333
PS> python -B labs/map_elites_archive/reachability_probe.py
# generators reach 495/512; the probe reached 8 more; 9 stay unreached
PS> git status --short data/   # after regenerating all three 8x8 generator labs
# (empty — byte-identical)
# the repair arc, RED first (test_repair_vocabulary_preservation):
# FAILED (failures=53, errors=1) -> after DR 0039 at all three sites -> OK
PS> python -B tools/ci/run_sweep.py
SWEEP GREEN                                          # all suites, workshop included
```

## HONEST REMAINDER

1. **The 11-class regrowth head** (DR 0039's named record): repair
   preserves but cannot regrow the rich vocabulary — wounded limbs
   return as legacy classes.
2. **9 descriptor bins remain unreached** within the probe budget —
   the octile corners narrowed from 95; geometric emptiness remains a
   hypothesis, not a conclusion.
3. **The bake-off flip is DR 0031 evidence, not an adoption change** —
   the generation-layer revisit is its own record (J-phase material).
4. **Downstream artifacts regenerate under the new stream** — the
   16×16 archive/game evidence chain re-runs with this change; the
   deltas are recorded in the regenerated artifacts themselves.

## Sources

- `audits/TODO.md` (cycle 20 J2), `research/decision_records/0038-vocabulary-complete-generation-alphabet.md`, `0039-repair-vocabulary-preservation.md`
- `labs/grid_genome/{grid_helpers,markov_grid,constrained_generator}.py` (+ `test_vocabulary_alphabet.py`, `test_package_generation_parity.py`)
- `packages/mecha_engine/src/mecha_engine/generation/{model,generate}.py`
- `labs/cellular_automata/ca_nca_growth_repair.py` (+ `test_repair_vocabulary_preservation.py`), `packages/mecha_engine/src/mecha_engine/repair/`, `packages/mecha_engine/src/mecha_engine/runtime/_grids.py`
- `data/grid_genome/role_emission_stage0.json`, `data/archives/reachability_probe_stage0.json`, `data/repair_boundary/repair_validity_boundary_stage0.json`, `data/wfc_grid/generation_bakeoff16_stage0.json`
- `research/experiment_reports/2026-07-20-role-emission.md` (the measurement this implements)
