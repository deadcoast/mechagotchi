# Experiment Report: The WFC Lab Exists — and Pure Collapse Refutes Itself (Cycle 10 · ENGINE · B1)

Date: 2026-07-08

## WHY

The gap analysis' generation row: the documents specify Markov →
**WFC/constraints** → mutation → validator as the winning architecture,
proven by a bake-off — but `labs/wfc_grid/` was never created and the
historical bake-off ran without the documented field. Phase A left the
matching remainder: the generation alphabet was {., B, A, E, M}, so
children of rich parents lost their shells and limbs. B1 builds the
constraint layer over the FULL vocabulary.

## WHAT

`labs/wfc_grid/wfc_grid.py`: a rich-token matrix projection (every
DR 0015 role survives, anchor as its own token), the adapted 30/10/10
stratified split (the dossier's 72/24/24 over the real 50-creature
corpus — a recorded protocol decision), an overlapping-WFC model with a
position channel (per-cell observed-token candidate sets + observed
right/down adjacency), minimum-entropy collapse with arc-consistent
propagation and deterministic bounded restarts, and the documented
stabilizer finishing pass. RED-first; 10 tests.

## FINDINGS

- **Pure local collapse refutes itself as a creature generator**
  (first-class negative result): the first measured batch was 2% valid
  — 49/50 disconnected required cores — because position priors mix
  different creatures' body plans into separate blobs and local
  adjacency cannot see global connectivity. This is precisely the
  weakness the dossier's constraint-systems row flags, and its own
  recommendation ("use as validator or post-generator stabilizer") is
  the fix.
- **With the stabilizer finishing** (largest-core retention, global
  cardinality restarts at the DR 0029 floor and sensor presence, the
  promoted generator's anchor semantics): **validity 1.0** over the
  stage-0 batch — 50/50 valid, 50 unique silhouettes, all six rich
  roles emitted (antenna, decoration, effect, joint, limb, shell),
  training-copy rate 0.0, core masses 31–60 (p50 45).
- The arm stays honest: no validator-gated resampling inside — that is
  the constrained-stabilizer arm's mechanism, and keeping the arms
  mechanically distinct is what makes the B2 bake-off a comparison
  rather than five names for one pipeline.

## Verification

RED (suite before the module existed):

```powershell
PS> python -B -m unittest discover -s labs/wfc_grid -p "test_*.py"
ModuleNotFoundError: No module named 'wfc_grid'
FAILED (errors=1)
```

GREEN:

```powershell
PS> python -B -m unittest discover -s labs/wfc_grid -p "test_*.py"
Ran 10 tests in 0.744s
OK
```

Lab (artifact production):

```powershell
PS> python -B labs/wfc_grid/wfc_grid.py
"validity_rate": 1.0, "unique_signatures": 50, "rich_role_count": 6,
"training_copy_rate": 0.0, "core_mass": {"min": 31, "p50": 45, "max": 60}
```

## Sources

- `labs/wfc_grid/wfc_grid.py`, `labs/wfc_grid/test_wfc_grid.py`
- `data/wfc_grid/wfc_grid_stage0.json`
- `research/algorithm_cards/wfc_grid.md`
- `data/seed_grids_16x16/`, `labs/grid_genome/grid_helpers.py` (`RICH_TOKENS`)
- `docs/project-research/deep-research/01/deep-research.md`, `docs/gap-analysis.md` (Phase B)
- `research/experiment_reports/2026-07-08-phase-a-gate.md` (the remainder this closes)
- `audits/TODO.md` (cycle 10 B1)
