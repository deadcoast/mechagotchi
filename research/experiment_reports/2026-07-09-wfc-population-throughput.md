# Experiment Report: WFC Generation Throughput at Population Scale (Cycle 13 · ENGINE · E2)

Date: 2026-07-09

## WHY

The gap table's evolution row demands populations ~256 per generation;
the dossier's generation gate demands ≤250 ms per 16×16 candidate. The
standing remainder from cycle 10 (DR 0031) left `runtime.evolve`'s
inner loop on the constrained path *pending its own evidence* — the
bake-off proved WFC as a batch generator, never as the evolve loop's
parent path. E2 produces that evidence: both paths measured at the
documented population scale, from the SAME parents, drawn from archive
elites per the promoted evolve semantics.

## WHAT

`labs/wfc_grid/wfc_population_throughput.py` (+ tests), producing
`data/wfc_grid/wfc_population_throughput_stage0.json`:

- **The engine's own surfaces.** Both arms run
  `mecha_engine.generation` (the promoted package), not lab twins:
  `generate_candidate` (the evolve inner loop, verbatim — round-robin
  `parents[index % len(parents)]`, per-candidate seed
  `rng_seed + generation × 100000 + index`) vs `train_wfc_model` +
  `generate_wfc_grid` (the adopted WFC layer as a parent path: the
  model retrained on the current elite pool each generation).
- **Parents per the promoted semantics.** `runtime.evolve`'s default
  branch, pinned by test: elites' grids in `sorted(niche)` order, from
  an E1-mechanics archive bootstrapped over a 400-candidate mixed
  population (171 elites), binned with E1's FROZEN empirical edges.
- **Archive refresh by the path under test.** The WFC arm's candidates
  are scored (calibrated Stage 0 fitness, 24-tick stress-probed
  lifecycle) and inserted between generations; the constrained arm is
  the measured comparator from the same parents, never inserted.
- **Failures recorded.** WFC wave contradictions and constrained
  generation rejections are counted per generation, never hidden.
- SLIP alignment is deliberately NOT enforced (generation measured
  without profile constraints; E3's full loop owns the alignment
  gates) — recorded in protocol and blocked states.

## RESULTS

Full scale: population 256 × 3 generations from 171-elite parents
(1,168 total archive candidates including the bootstrap).

- **Throughput (measured FIRST, machine-dependent, in the artifact's
  `measured` section): WFC 7.04 ms per candidate — WITH its
  per-generation model retraining counted (6.3 ms per generation) —
  constrained 2.51 ms. Both meet the documented 250 ms bar with ~35×
  and ~100× headroom respectively.**
- **Validity at scale: 1.0 for BOTH arms** across all three generations
  (the dossier's ≥0.85–0.95 bars cleared at the top).
- **Uniqueness: WFC 1.0 unique-signature rate** (768/768 distinct
  bodies), constrained 0.996 (3 duplicate signatures across 768). WFC
  candidates never copy a parent (parent_copy_rate 0.0); the
  constrained arm's copy rate is also ~0.
- **Descriptor spread:** constrained reaches slightly more unique scale
  descriptors (299 vs 281 summed per-generation) — the arms are
  comparable illuminators; neither dominates novelty.
- **The archive grew 171 → 233 occupied niches (coverage 0.455)** under
  the WFC parent path, with 234 elite replacements — the parent path
  sustains quality-diversity growth at population scale.
- **The DR 0031 remainder's evidence:** WFC as the parent path is
  viable at documented scale — equal validity, strictly higher
  uniqueness, ~35× time headroom including retraining, and healthy
  archive growth. The inner-loop adoption itself remains a package
  change for E3/a decision record; the promoted evolve is untouched
  here.

## VERIFICATION

RED (the suite fails before the module exists):

```powershell
PS> python -B -m unittest discover -s labs/wfc_grid -p "test_wfc_population_throughput.py"
ModuleNotFoundError: No module named 'wfc_population_throughput'
FAILED (errors=1)
```

GREEN (after implementation + the full-scale artifact run):

```powershell
PS> python -B -m unittest discover -s labs/wfc_grid -p "test_*.py"
Ran 36 tests in 6.715s

OK
```

Lab (throughput measured first, then the full-scale build):

```powershell
PS> python -B labs/wfc_grid/wfc_population_throughput.py
...
Measured at population 256 x 3 generations from 171-elite parents: WFC validity 1.0, unique-signature rate 1.0 vs constrained validity 1.0, unique-signature rate 0.996094; the archive grew from 171 to 233 occupied niches under the WFC parent path.
```

## BLOCKED STATES (honest remainder)

- `throughput_gate_judged_on_the_measured_section` — machine-dependent;
  tests assert shape and arithmetic, never values.
- `slip_alignment_not_enforced_in_this_harness` — E3's full loop owns
  the alignment gates.
- `evolve_inner_loop_adoption_pending` — the evidence is recorded; the
  package change is E3's/a decision record's.

## Sources

- `labs/wfc_grid/wfc_population_throughput.py`
- `labs/wfc_grid/test_wfc_population_throughput.py`
- `data/wfc_grid/wfc_population_throughput_stage0.json`
- `research/algorithm_cards/wfc_population_throughput.md`
- `labs/map_elites_archive/niche_scale_archive.py`
- `data/archives/niche_scale_archive_stage0.json` (the frozen edges)
- `packages/mecha_engine/src/mecha_engine/generation/`
- `packages/mecha_engine/src/mecha_engine/runtime/evolve.py`
- `research/decision_records/0031-wfc-generation-adoption.md`
- `docs/project-research/deep-research/01/deep-research.md`
- `audits/TODO.md` (cycle 13 E2)
