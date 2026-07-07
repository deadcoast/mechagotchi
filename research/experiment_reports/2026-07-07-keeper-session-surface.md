# Experiment Report: The Keeper's Surface (G4) — Playing the Engine

Date: 2026-07-07

## WHY

DR 0021 build gate G4: "session UI on the workshop server pattern;
`mechas` gains session commands (DR 0007 charter). After G2/G3." Both
prerequisites shipped (G2 the session lab, G3=R5 the replay window), so
the Keeper gets hands: a persistent session that survives across
processes, a page to play it, and terminal commands that drive the same
lab. The first law governs the whole surface: every number shown is a
report field from a real evolve run.

## WHAT

**The lab grows the play surface** (`labs/game_loop/session_runner.py`):

- `advance_campaign` — one era at a time, extracted from `run_campaign`
  so incremental play and batch play are pinned as the SAME code path
  (`test_incremental_advances_equal_the_batch_campaign`).
- The persistent Keeper state (`keeper_session_v1`): covenant and
  engine parameters fixed at creation so every later era is reproducible
  from the state file alone; `advance_keeper_state` runs one era,
  applies unlocks, and on extinction immediately seats the successor
  bloodline (only the unlock facts carry, via the predecessor pointer —
  `apply_succession`, fixture-proven). `save_keeper_state` is
  backup-before-overwrite and refreshes the derived DR 0022 schema-v1
  ledger next to the state file on every save.
- CLI modes (`--mode new/advance/status`) — machine-readable JSON for
  supportive layers.

**The workshop server gains the session endpoints** (same pattern as
every workshop surface — the engine answers, the page asks):
`GET /session` (the Keeper page), `GET /api/session/state` (the read
model), `POST /api/session/new` (409 if one exists),
`POST /api/session/era` (one real evolve run, persisted). Play state
lives in `data/game_loop/keeper/` — gitignored, because a live game is
not evidence — so a session can never overwrite the committed stage-0
artifacts one level up.

**`mechas session`** (DR 0007's charter: new operational workflows
become mechas commands): `--open` serves the Keeper page; `--era
<forecast>` plays from the terminal through the lab's CLI mode in the
workspace interpreter; `--status`/`--new` read and start the session;
no flags = the orientation table. The workshop launch block was factored
into `launch_workshop_server` (shared, not duplicated).

## Verification

```powershell
PS> python -B -m unittest discover -s labs/game_loop -p "test_*.py"
Ran 36 tests in 2.994s
OK

PS> python -B -m unittest discover -s workshop/tests -p "test_*.py"
Ran 48 tests in 75.499s
OK

PS> python -B -m unittest discover -s tools/mechas_cli/tests -p "test_*.py"
Ran 21 tests in 3.539s
OK          # (venv run with typer installed: 21/21 OK as well)

# Terminal play, end to end (temp state dir):
PS> python -B labs/game_loop/session_runner.py --mode new --state-path ...
{"ok": true, "session_format": "keeper_session_v1", ...}
PS> python -B labs/game_loop/session_runner.py --mode advance --weather storm --state-path ...
{"ok": true, "forecast": "storm", "niches": 7, "unlocks": 5, "status": "active"}
```

The server test plays the whole loop through HTTP: no-session refusal
(409), start, duplicate-start refusal (409), one storm era with
engine-recorded snapshot provenance, persisted state + DR 0022 ledger,
unknown-forecast rejection (400).

## Findings

- **Evidence-clobbering hazard found and closed**: the first wiring
  pointed the live session's ledger at `data/game_loop/
  campaign_ledger.json` — the committed G2 evidence artifact. Play state
  now lives in its own gitignored subdirectory and the ledger is derived
  next to the state file by default.
- **Ambient-color test fragility fixed**: `FORCE_COLOR` in the ambient
  shell injected ANSI codes into captured help output and broke the CLI
  surface tests' plain-substring assertions (pre-existing; reproduced at
  HEAD). The test harness now pins its capture environment to plain
  text.

## Honest scope

- The covenant (SLIP) and engine parameters are fixed at campaign
  creation; the DR 0021 Covenant step (adjusting the SLIP within the
  unlocked budget between eras) and unlock-driven cap growth are the
  identified next slice of this surface — unlock FACTS are recorded and
  displayed, but nothing spends them yet.
- The Review step links to the preview scrubber (R5) rather than
  embedding it; per-era replay recording into the DR 0022 `replays`
  table is queued with that slice.

## Decision

Adopt — G4 developed to its description (session UI on the workshop
server pattern; `mechas` session commands per the DR 0007 charter).
Next: R6 (the dataset program), R7 (grid-schema animation/species
fields), then the covenant-budget slice above.

## Sources

- `research/decision_records/0021-game-loop.md` (G4)
- `research/decision_records/0007-mechas-companion-cli.md` (the charter)
- `research/decision_records/0022-storage-module.md` (the ledger shape)
- `labs/game_loop/session_runner.py` (+ `test_session_runner.py`)
- `workshop/server/workshop_server.py`, `workshop/session/session.html`
- `workshop/tests/test_workshop_server.py`
- `tools/mechas_cli/src/mechas_cli/workflows/session.py`
- `tools/mechas_cli/src/mechas_cli/workflows/workshop.py`
- `tools/mechas_cli/tests/test_cli_surface.py`
- `docs/cli/mechas-cli.md`
- `.gitignore` (the play-state rule)
