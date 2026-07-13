# Experiment Report: The Lineage Browser — the Keeper's Whole Story (Cycle 16 · GAME · F14)

Date: 2026-07-12

## WHY

MVP 0.3's lineage-browser element (validity §1.24), and the founding
loop's own promise: the creature "saves a lineage file" and its
descendants grow "more complex over time based on the survival of its
ancestors" — the file existed since F2; F14 makes it a readable STORY.

## WHAT

**One additive session fact first**: lineage records gain `origin` —
how each life began (founder / hatched / era_elite / succession) — a
Keeper fact the engine does not own, recorded ALONGSIDE the engine's
verbatim lineage block, riding the save file; old saves without it
stay loadable (pinned). The client's adoption paths record their
origins (H → hatched, A → era_elite, death's door → succession).

**`game/src/mecha_game/lineage.py`** (RED-first, 8 tests):
`LineageBrowser` pages the lives newest-first-on-open; every line is
a record field verbatim — the identity, the origin, the engine's own
death cause and age, the parent, and the grid schema's lineage block
(generation, the ancestor chain, mutation events — string or object
events shown as the schema wrote them; a shape difference the tests
caught). **L** pages the story in the client (`.`/`,`), companion
time pausing like every browsing mode.

**Measured** (`data/game_client/lineage_story_stage0.json`, status
complete, twin-equal): a real three-life story — founder → starvation
→ succession → starvation → succession — with origins
`[founder, succession, succession]` verbatim, both death causes the
engine's own (`starvation`), and **the ancestor chain growing 0 → 1 →
2** — `generate_candidate`'s own `ancestor_ids` accumulating across
successions, exactly the founding sentence made visible. The story
rides the save file byte-for-byte.

## Verification

```powershell
PS> uv run python -B -m unittest discover -s game/tests -p "test_lineage.py"
Ran 1 test ... FAILED (errors=1)   # RED: no mecha_game.lineage
# after implementation (and the string-event shape fix):
Ran 8 tests ... OK
PS> uv run python -B -m unittest discover -s game/tests -p "test_*.py"
Ran 131 tests ... OK
PS> uv run python -B game/evidence.py   # lineage_story_stage0: complete
PS> uv run python -B game/run_game.py --ticks 5 --keeper-dir <tmp>   # exit 0
```

## HONEST REMAINDER

1. **The cross-campaign timeline is F17's material** — the session's
   lineage browses today; weaving the ledger's era chain into one
   story lands with campaign resume.
2. **No body thumbnails for past lives** — lineage records are
   id+metadata by design (dead bodies are not stored; the repertoire
   browses the archive's stored bodies instead).
3. **Origin is a Keeper fact, not an engine field** — recorded
   additively next to the engine's block, never inside it.

## Sources

- `audits/TODO.md` (cycle 16 F14), `docs/project-research/validity-research.md` (§1.24)
- `research/grid_genome/grid_genome.schema.json` (the lineage block — the verbatim source)
- `game/src/mecha_game/{lineage,session,app}.py` (+ `game/tests/test_lineage.py`)
- `data/game_client/lineage_story_stage0.json` (evidence)
