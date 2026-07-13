# Experiment Report: Community Packs — the Format Rung (Cycle 16 · GAME · F16)

Date: 2026-07-12

## WHY

MVP 0.3's last named element (validity §1.24: "community profile
packs") at its FIRST honest rung: the documented community surface
needs a CARRIER before it needs infrastructure — one file a Keeper
can hand to another. Distribution (registries, sharing, moderation)
stays Phase G by the owner's staging.

## WHAT

**`game/src/mecha_game/packs.py`** (RED-first, 7 tests):
`mechagotchi_pack_v1` — SLIPs + creatures + provenance in one
importable JSON file. The engine's gates run THREE times over pack
content:

1. **Build refuses invalid content** with the validators' verbatim
   errors — an invalid pack cannot be published.
2. **Import re-judges every item** (packs travel and can be tampered
   with — pinned by a post-build tamper test) and stages ONLY
   accepted items into the existing inboxes: covenants into
   `keeper/covenants/` (I imports one), creatures into
   `keeper/released/` (W gathers them).
3. **The era admission gates judge staged creatures at run time**
   (DR 0016 founders-lead, DR 0029 size coherence, SLIP alignment).

**K** imports `keeper/packs/pack_import.json` in the client (P is
the companion's play action) with the per-item verdict summary.

**The starter pack** (`data/packs/mechagotchi_starter_pack.json`,
committed, regenerated deterministically by the evidence harness):
the four valid zoo covenants + the two committed workshop releases +
the corpus beetle, provenance declared (Apache-2.0, committed
material).

**Measured** (`data/game_client/community_pack_stage0.json`, status
complete, session scale): the starter pack built and imported with
ALL items staged (4 covenants, 3 creatures); its staged creatures
flowed into a real era where the engine judged them exactly as
documented — **the beetle admitted, the two 8×8 releases rejected
verbatim** (`founder grid is 8x8 but the era runs at 16x16`); the
era survived.

## Verification

```powershell
PS> uv run python -B -m unittest discover -s game/tests -p "test_packs.py"
Ran 1 test ... FAILED (errors=1)   # RED: no mecha_game.packs
# after implementation:
Ran 7 tests ... OK
PS> uv run python -B -m unittest discover -s game/tests -p "test_*.py"
Ran 143 tests ... OK
PS> uv run python -B game/evidence.py   # community_pack_stage0: complete
PS> python -m json.tool data/packs/mechagotchi_starter_pack.json   # valid
```

## HONEST REMAINDER

1. **Distribution is Phase G** — this rung is the carrier format
   only; registries, sharing, and moderation are the documented
   late-stage community scope.
2. **Provenance is declarative** — integrity/signature schemes belong
   with Phase G's distribution decisions, named here.
3. **The starter pack's releases are 8×8-era pieces** — they stage
   honestly and reject honestly at a 16×16 era; the day the workshop
   authors at 16×16, the same pack path carries admitting creatures.

## Sources

- `audits/TODO.md` (cycle 16 F16), `docs/project-research/validity-research.md` (§1.24)
- `game/src/mecha_game/packs.py` (+ `game/tests/test_packs.py`), `game/src/mecha_game/app.py` (the K key)
- `data/packs/mechagotchi_starter_pack.json` (the committed example), `data/game_client/community_pack_stage0.json` (evidence)
