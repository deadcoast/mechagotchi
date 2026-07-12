# Experiment Report: The Contribute Bridge — Workshop Releases Enter the Eras (Cycle 15 · GAME · F9)

Date: 2026-07-12

## WHY

DR 0021's Contribute step: the Keeper may craft a creature in the
workshop and RELEASE it; released creatures enter the next era as
founders "through the engine's own gates — admission or verbatim
rejection, both shown." The session lab proved the seam (E5's
`released_grids`); the workshop already writes releases
(`data/workshop/released/`); F9 bridges the two in the product,
scoping the FILE handoff — never a workshop rewrite (the workshop
keeps its ratified stack).

## WHAT

**`game/src/mecha_game/contribute.py`** (RED-first, 7 tests):
`load_released_grids` mirrors the lab's inbox rule verbatim
(deterministic file order, `.bak.json` backups skipped, a missing
inbox is simply no releases); the inboxes are the workshop's
`data/workshop/released/` (checkout or bundle) plus the player's own
`keeper/released/`; `founders_verdict` reads the engine's admission
block from the era report. **Admission is the ENGINE's verdict** —
`evolve`'s DR 0016 founders-lead rule, DR 0029 size coherence, and
SLIP alignment, recorded in `report["founders"]`
(`admitted_ids`/`rejected` with verbatim errors).

**The client**: **W** gathers every released creature into the next
era's pending pool; the era message then shows the verdict —
`founders: N admitted, M rejected (id: the engine's own error)`.

**Measured** (`data/game_client/contribute_bridge_stage0.json`,
status complete, session scale, twin-equal): the two COMMITTED
workshop releases (8×8-era pieces) entered a 16×16 era and were
**rejected verbatim on size coherence** (`founder grid is 8x8 but
the era runs at 16x16`) — an honest, documented outcome, not a
bridge failure — while an LCD-covenant-aligned 16×16 release was
**admitted and led the pool**; the era survived. A subtlety the
tests caught: covenant alignment is real — the moth seed, renamed as
a release, is honestly rejected under the LCD covenant; only some
corpus species satisfy it.

## Verification

```powershell
PS> uv run python -B -m unittest discover -s game/tests -p "test_contribute.py"
Ran 1 test ... FAILED (errors=1)   # RED: no mecha_game.contribute
# after implementation:
Ran 7 tests ... OK
PS> uv run python -B -m unittest discover -s game/tests -p "test_*.py"
Ran 106 tests ... OK
PS> uv run python -B game/evidence.py   # contribute_bridge_stage0: complete
```

## HONEST REMAINDER

1. **The committed releases are 8×8-era pieces** — a 16×16 authored
   release will admit the day the workshop saves one; the bridge
   needs no change (pinned by the aligned-release path).
2. **Release provenance display stays workshop-side** (the inspector
   browses released ancestry); the client shows the VERDICT — the
   full lineage browser is a 0.3 rung.
3. **No release curation UI** — every inbox file is submitted; a
   pick-list is authoring polish for the workshop track.

## Sources

- `audits/TODO.md` (cycle 15 F9), `research/decision_records/0021-game-loop.md` (the Contribute step)
- `labs/game_loop/session_runner.py` (`load_released_grids` — the mirrored rule), `research/decision_records/0016-evolve-founder-grids.md`, `0029` (size coherence)
- `packages/mecha_engine/src/mecha_engine/runtime/evolve.py` (the admission gates + the `founders` report block)
- `data/workshop/released/` (the committed releases), `game/src/mecha_game/{contribute,app}.py` (+ `game/tests/test_contribute.py`)
- `data/game_client/contribute_bridge_stage0.json` (evidence)
