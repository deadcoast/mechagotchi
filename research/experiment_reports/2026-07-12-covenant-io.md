# Experiment Report: SLIP Import/Export — Covenants Travel (Cycle 16 · GAME · F15)

Date: 2026-07-12

## WHY

MVP 0.3's import/export element (validity §1.24) and the founding
vision's community shape: "users author species via SLIP" and share
them. The covenant was already the progression surface (F7); F15
makes it a FILE that travels.

## WHAT

**`game/src/mecha_game/covenant_io.py`** (RED-first, 5 tests):

- **Export writes the ACTIVE covenant VERBATIM** (spends included) —
  it is already an authority-validated SLIP, shareable as-is; the
  zoo's file convention, no wrapper invented. Backup-before-overwrite.
- **Import passes TWO engine gates before anything applies**: the
  authority's validation (`validate_slip`, refusals verbatim) and
  corpus compatibility — `evolve`'s own "no seed grid satisfies the
  SLIP profile" rule, checked with the engine's `is_grid_aligned` so
  an accepted covenant can actually begin an era. A refused import
  applies NOTHING.
- **An accepted import is a NEW SPECIES CONTRACT**: it replaces both
  the base and the active covenant; the earned budget recomputes from
  it; spends re-apply by the Keeper's choice, never silently. A live
  companion's covenant never swaps under it — imports govern future
  adoptions, hatches, and eras.

**The client**: **X** exports to `keeper/covenants/
covenant_export.json`; **I** imports `keeper/covenants/
covenant_import.json` (the F9 file-bridge pattern) with the verdict —
including the aligned-seed count — in the footer.

**Measured** (`data/game_client/covenant_io_stage0.json`, status
complete, session scale): a SPENT covenant (earned thinking applied)
exported verbatim and round-tripped to identity; the zoo's
`slip_gray_stable` imported (8 corpus seeds satisfy it) and **its era
ran, filling 22 niches under the imported contract**; the
bad-version fixture refused with the authority's verbatim error
(`slip_version must be one of 0.1.0, 0.2.0`); an authority-valid but
impossible covenant (body-mass floor 200) refused with the engine's
named rule.

## Verification

```powershell
PS> uv run python -B -m unittest discover -s game/tests -p "test_covenant_io.py"
Ran 1 test ... FAILED (errors=1)   # RED: no mecha_game.covenant_io
# after implementation:
Ran 5 tests ... OK
PS> uv run python -B -m unittest discover -s game/tests -p "test_*.py"
Ran 136 tests ... OK
PS> uv run python -B game/evidence.py   # covenant_io_stage0: complete
PS> uv run python -B game/run_game.py --ticks 5 --keeper-dir <tmp>   # exit 0
```

## HONEST REMAINDER

1. **Spends do not migrate with an import** — the new contract's
   budget recomputes from the earned facts and the Keeper re-spends;
   silent re-application would hide authority checks.
2. **The import inbox is one fixed filename** — a pick-list is
   authoring polish; F16's pack format is the multi-file carrier.
3. **Corpus compatibility is judged against the SHIPPED corpus** —
   a pack carrying its own creatures (F16) widens what a covenant
   can satisfy.

## Sources

- `audits/TODO.md` (cycle 16 F15), `docs/project-research/validity-research.md` (§1.24)
- `research/decision_records/0012-slip-schema-extension-ladder.md`, `data/slips/` (the zoo + failure cases)
- `packages/mecha_engine/src/mecha_engine/slip/__init__.py` (the authority), `runtime/evolve.py` (the compatibility rule)
- `game/src/mecha_game/{covenant_io,app}.py` (+ `game/tests/test_covenant_io.py`)
- `data/game_client/covenant_io_stage0.json` (evidence)
