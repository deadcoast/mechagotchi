# Experiment Report: Per-Era Replay into the Ledger (C5) — The Review Step Closes

Date: 2026-07-07

## WHY

DR 0021's core loop OPENS with Review ("the last era's report and
replay"), and both the R5 and G2 reports named the wiring gap: the
recorder existed, the ledger's `replays` table existed, but no era ever
recorded a replay. C5 closes the loop.

## WHAT

- **Recording** — every era records its best elite's life through the
  DR 0023 recorder (`record_frames=True`) at the ERA'S OWN seed; the
  replay rides the era record. Honest label: this is a real recorded
  life of a real era creature, replayed post-era — the in-era
  per-creature lives ran without frame recording, and threading
  `record_frames` through `evolve` is a NOTED future seam, not silently
  skipped.
- **Ledger rows as pure functions of state** — `build_campaign_ledger`
  emits one `replays` row per era with a fixed path convention
  (`replays/<campaign>_era<NNN>.json`) and a sha256 over the replay's
  CANONICAL JSON; `write_replay_files` writes the artifacts to match,
  and the gate test pins file hash == row hash. Both stores (lab +
  promoted `mecha_engine.storage`, verbatim re-port) gained
  `record_replay`/`load_replay_rows` and ingest the rows — the demo
  SQLite now carries `replays: 3`.
- **The Review surface** — `GET /api/session/replay?campaign=&era=`
  serves stored replays from the ledger's directory; the Keeper page's
  era cards gain "▶ replay" and an in-page scrubber (slider,
  play/pause, wound overlays, tick readout) over the RECORDED frames.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/game_loop -p "test_*.py"
Ran 51 tests in 6.259s
OK    # incl. replay-per-era pins, file-hash == row-hash, gate-7 counts

PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
Ran 280 tests in 6.024s
OK

PS> python -B -m unittest discover -s workshop/tests -p "test_*.py"
OK    # the session flow now fetches era 0's stored replay end to end

PS> python -B labs/game_loop/campaign_store.py
{... "row_counts": {..., "replays": 3}}
```

## Decision

Adopt — C5 developed to its description: eras record, the ledger
points with content hashes, the Keeper reviews. Remaining in cycle 03:
C4 (the Covenant step) and C6 (the repair-validity boundary study).

## Sources

- `research/decision_records/0021-game-loop.md` (the Review step)
- `research/decision_records/0022-storage-module.md` (the replays table)
- `research/decision_records/0023-replay-recording.md` (the recorder)
- `labs/game_loop/session_runner.py`, `labs/game_loop/campaign_store.py`
- `packages/mecha_engine/src/mecha_engine/storage/store.py`
- `workshop/server/workshop_server.py`, `workshop/session/session.html`
- `data/game_loop/replays/` + `data/game_loop/campaign_ledger.json` + `data/game_loop/campaign_store.sqlite`
