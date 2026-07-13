# Experiment Report: The Repertoire Browser — Species Memory Made Visible (Cycle 16 · GAME · F13)

Date: 2026-07-12

## WHY

MVP 0.3's first element (validity §1.24: "Add mecha_darwin archive…
species niches") and the true purpose behind it: Phase E proved the
repertoire (the MAP-Elites archive at documented scale; 52 recurrent
families across ten independent runs — species memory measured), and
the era bench fills an archive every era — but the player could see
only counts. F13 makes the repertoire a PLACE.

## WHAT

**`game/src/mecha_game/repertoire.py`** (RED-first, 6 tests):
`RepertoireBrowser` pages the era archive's elites in the archive's
own deterministic niche order, era by era across the campaign. Every
display line is the elite RECORD verbatim — the descriptor's NAMED
axes (`body_mass 0  sensor_count 0  symmetry 1 …`), the fitness and
its components, the lineage generation — and every body is a real
`render_packet_v2` under the campaign's covenant. The browser never
re-derives a statistic.

**The client**: **B** opens the repertoire (companion time stands
still); **.**/**,** page niches, **[**/**]** switch eras — and **A
adopts the BROWSED elite**: the repertoire is a place the Keeper
shops for their next companion, deepening the F4 adopt-the-best path
into a real choice over the whole archive.

**Measured** (`data/game_client/repertoire_stage0.json`, status
complete, session scale, twin-equal): a two-era campaign browsed end
to end — every elite rendered a real packet whose `grid_id` matches
its record, era switching reaches the first era's archive, display
samples recorded verbatim.

## Verification

```powershell
PS> uv run python -B -m unittest discover -s game/tests -p "test_repertoire.py"
Ran 1 test ... FAILED (errors=1)   # RED: no mecha_game.repertoire
# after implementation:
Ran 6 tests ... OK
PS> uv run python -B -m unittest discover -s game/tests -p "test_*.py"
Ran 123 tests ... OK
PS> uv run python -B game/evidence.py   # repertoire_stage0: complete
PS> uv run python -B game/run_game.py --ticks 5 --keeper-dir <tmp>   # exit 0
```

## HONEST REMAINDER

1. **Ledger-sourced browsing across restarts awaits F17's resume
   rung** — the in-memory campaign's eras browse today; the ledger
   already stores the same records verbatim.
2. **A cross-era FAMILY lens is a named future rung** — E5's
   recurrent-family clustering is lab math; the client will not
   smuggle a second implementation of it.
3. **The browser draws the idle display** — per-elite clip playback
   inside the browser is polish, not contract.

## Sources

- `audits/TODO.md` (cycle 16 F13), `docs/project-research/validity-research.md` (§1.24)
- `research/experiment_reports/2026-07-09-phase-e-gate.md` (the proven repertoire), `2026-07-09-recurrent-families.md` (species memory)
- `game/src/mecha_game/{repertoire,app}.py` (+ `game/tests/test_repertoire.py`)
- `data/game_client/repertoire_stage0.json` (evidence)
