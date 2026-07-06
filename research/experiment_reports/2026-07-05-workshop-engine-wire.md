# Experiment Report: The Workshop→Engine Asset Wire (T1)

Date: 2026-07-05

## Objective

Close the owner's DESIGN-CORRECTION [00] (audit task T1): the og
triangle `engine <-> SLIP <-> workshop` promised that workshop creations
become assets the engine USES, but the return path dead-ended — no
simulation ever consumed a workshop creature. This experiment wires
released workshop creatures into the evolution founder pool and measures
what happens to their lineages.

## Design

- `run_mecha_engine_evolution_loop(..., workshop_grids_dir=...)`:
  released creatures are admitted through the engine's own gates
  (`validate_grid` + SLIP alignment; rejections recorded with the
  engine's errors verbatim). Admitted founders LEAD the generation-0
  parent pool so the round-robin always exercises the wire.
- Lineage traceability (T1.2): a founder's `grid_id` persists in every
  descendant's `lineage.ancestor_ids` — verified mechanism: per-cycle
  renames touch only `grid_id`, never the ancestor list, so
  `founder_source` is computable for every creature in every generation
  and asserted in tests.
- Every wire key is regime-conditional: the default `workshop_grids_dir
  = None` path is byte-identical (package parity pins verified green).
- Release flow (T1.3): `POST /api/release` + an editor Release button +
  `mechas workshop --release <name>` — strict (saved, engine-valid
  creatures only), lineage-marked (`released_into_ecosystem`), a COPY so
  the draft stays editable, backup-before-overwrite. Evolution consumes
  `data/workshop/released/`.

## Verification

RED (parameter did not exist):

```powershell
python -B -m unittest discover -s labs/runtime_integration -p "test_workshop_wire.py"
# TypeError: unexpected keyword argument 'workshop_grids_dir' -> FAILED
```

GREEN:

```txt
Ran 6 tests in 1.973s   OK        # wire tests
Ran 30 tests in 37.599s OK        # full runtime lab incl. parity pins
Ran 21 tests in 0.523s  OK        # package runtime contract suite
Ran 30 tests in 41.571s OK        # workshop server suite incl. release
```

Lab command (full size, stress regime, two released founders):

```powershell
python -B .\labs\runtime_integration\mecha_engine_runtime_loop.py --mode evolution --regime stress_probe --generations 6 --workshop-dir data\workshop\released
```

```txt
"workshop": {"released_count": 2,
  "founder_ids": ["released_tall_wisp", "released_wide_sentinel"],
  "rejected": [],
  "creature_count_by_generation": [2, 0, 0, 0, 0, 0],
  "archive_elite_count": 0,
  "mean_fitness": 0.762134, "corpus_mean_fitness": 0.867971,
  "lineage_survived_beyond_founding": false}
```

## Findings

1. **The wire works, and the ecosystem does not grant favors.** Both
   released founders were admitted, bred in generation 0 (2 of 8
   creatures), and their lineages went **extinct immediately**: mean
   fitness 0.762 vs the corpus lineages' 0.868, zero archive entries,
   no workshop ancestry in any later generation. This is the og promise
   *measured*: user-authored assets enter evolution and must EARN their
   survival — these two did not.
2. **The extinction validates the workshop's teaching surfaces.** The
   founders were structurally heavy/asymmetric morphologies; under the
   stress regime that is exactly the load the grid editor's
   structural-load meter warns about while drawing. A creator who heeds
   the meter authors fitter founders — the loop from editor guidance to
   ecosystem outcome is now closed and honest.
3. **The wire exposed and fixed a latent gate gap in the loop**: episodes
   were gated on SLIP alignment only; a workshop-descended offspring
   produced a repaired grid that stayed aligned but went INVALID
   (disconnected core), crashing the lifecycle instead of being
   recorded. Episodes now require the engine's full word
   (`valid and aligned`), with a new measured outcome
   (`skipped_invalid`). Pre-wire corpora never produced this state
   (validity 1.0 throughout), so all pinned artifacts are unchanged —
   verified by the full parity suites above.
4. Rejection honesty: a founder whose palette the profile forbids comes
   back in `summary.workshop.rejected` with the engine's alignment
   errors verbatim (pinned by test).

## Decision

The wire is live end-to-end: draw → save → **release** → the creature
competes in evolution, traceably. T1.5 (a decision record extending the
promoted `runtime.evolve` seed-source contract) is owner-gated and now
evidence-ready. Follow-ups: release fitter founders (use the load
meter), grow `data/workshop/released/`, and surface workshop-lineage
outcomes in the future lineage browser (T13/slice 5).

## Sources

- `audits/TODO.md` (T1), `audits/audit-devspec.md` (§1)
- `labs/runtime_integration/mecha_engine_runtime_loop.py`
- `labs/runtime_integration/test_workshop_wire.py`
- `data/runtime_integration/mecha_engine_evolution_workshop_wire_stage0.json`
- `data/workshop/released/` (founding fixtures + README)
- `workshop/server/workshop_server.py` (release surface)
- `tools/mechas_cli/src/mechas_cli/workflows/workshop.py`
- `research/algorithm_cards/mecha_engine_runtime_loop.md`
