# Experiment Report: The Installable Release — Install, Launch, Play, Quit, Resume (Cycle 14 · GAME · F5)

Date: 2026-07-12

## WHY

MVP 0.1 is a PRODUCT rung: "installable, launchable, with save
files" (the gap analysis's Phase-F charter; the F5 sentence in the
TODO: *a player can install, launch, play, quit, and resume from a
save file*). DR 0033 named PyInstaller and deferred the decision to
this rung, with evidence.

## WHAT

**Save/resume first (RED-first):** `CompanionSession.save/load`
(`keeper_session_v1`) — state, log, lineage, and the succession
`GenerationModel` serialized VERBATIM (a plain dataclass; nothing
retrained, nothing guessed), the W1 backup-before-overwrite pattern.
The fixed RNG is recreated fresh on load — the switchboard path never
draws from it, so **a resumed life continues byte-identically with a
never-saved twin (pinned by test)**. The window auto-resumes from
`keeper/companion.json` unless `--new`; saves land on quit and on
death. A real bug this exposed: bounded runs counted the SESSION's
ticks, which continue across resume — `--ticks` now counts this run's.

**The build (PyInstaller 6.21, decided here):** `game/build_release.py`
produces a one-directory bundle (console entry `Mechagotchi`)
carrying the data the client needs — the 16×16 seed corpus, the LCD
covenant, the adopted readability model — and the client's walk-up
data resolution gained the frozen-bundle origins (`sys._MEIPASS`, the
executable's home) with the dev-checkout path unchanged. Outside a
checkout, saves default to the player's own `~/.mechagotchi`.
`dist/`/`release_work/` are gitignored: installers are built, never
committed.

**Measured** (`data/game_client/installable_release_stage0.json`,
status complete — generated only against a real build, never
fabricated): the built executable (41 MB bundle, ~12 s build on this
machine — observations, not pins) **launched fresh (exit 0, played 4
ticks, wrote the save), then launched again and RESUMED THE SAME LIFE
(exit 0, age 4 → 7)**, with the bundled corpus present. The same
sequence was run windowed by hand on the dev machine.

## Verification

```powershell
PS> uv run python -B -m unittest discover -s game/tests -p "test_*.py"
Ran 83 tests ... OK      # incl. RED-first save/resume + quit-and-resume launch
PS> uv run python -B game/build_release.py
Build complete! ... built ...\game\dist\Mechagotchi
PS> .\game\dist\Mechagotchi\Mechagotchi.exe --ticks 4 --keeper-dir <home>   # exit 0
PS> .\game\dist\Mechagotchi\Mechagotchi.exe --ticks 3 --keeper-dir <home>   # exit 0, age 4 -> 7
PS> uv run python -B game/evidence.py    # six artifacts, statuses complete
```

## HONEST REMAINDER

1. **CI packaging, signing, and multi-platform matrices are Phase G**
   (the documented delivery scope) — this build is verified on this
   machine, by hand and by the evidence harness.
2. **The bundle is console-mode** (diagnostics visible) — windowed-only
   polish and an icon are release-candidate concerns for the 0.2/0.3
   rungs.
3. **The campaign ledger saves/resumes with the keeper dir**, but the
   era bench retrains its models per process (~6 s lazy) — model
   caching is a noted 0.2 polish, not a correctness gap.

## Sources

- `audits/TODO.md` (cycle 14 F5), `research/decision_records/0033-game-front-end-technology.md` (PyInstaller named)
- `labs/game_loop/companion.py` (the W1 save/load pattern mirrored)
- `game/build_release.py`, `game/src/mecha_game/{session,app,packets,campaign}.py` (+ tests)
- `data/game_client/installable_release_stage0.json` (evidence)
