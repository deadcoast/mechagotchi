# Saved replay review (Cycle 30 T3)

Date: 2026-10-04. Authoritative source:
`C:\Users\ryanf\github\_shelved\mechagotchi`, branch `phase-l-gate`,
HEAD `d1ebd033d13938f2a3732282cc6fe6b8ad8255c5`; existing owner/external
changes preserved. Repository `.venv/Scripts/python.exe` is Python 3.13.9.
No alternate source, environment, Git mutation or security setting change.

**Locally complete and reviewed.** Full `20261004T192757-866fdf0f` passed
2,576 tests / 24 suites, two documented skips and 2,283 valid JSON artifacts
without mutations. The existing REVIEW -> REPAIR -> ENHANCE -> POLISH workflow
executed through actual tests, application observations and preservation gates.
Final runner snapshot: `.development/t3-closed.json`; canonical state:
`.development/state.json`. No process or next scope remains active.

T2 closed and was reviewed before this scope: full run
`20261004T185738-2f3b4168`, 2,563 tests / 24 suites, two documented DR 0034
zlib skips, 2,282 valid JSON artifacts and no source mutations. Additional
archive adoption review passed 12 checks / six native launches / six source
flows with covenant unchanged and both policies preserved through restart.

## Concrete behavior and source

The existing V handler required current-run campaign eras, so indexed recordings
could not be reopened after restart or from T's selected historical era.
`game/src/mecha_game/recorded_review.py` now reads the existing public
load_replay_rows query through read-only SQLite, checking schema, pointer
containment, normalized UTF-8 text SHA256, era seed and consumed frame fields.
It retains every stored value. The text hash preserves the existing Windows
CRLF-file/LF-payload convention; hashing raw bytes would reject old recordings.

`game/src/mecha_game/app.py` opens the latest or T-selected saved replay without
training/resuming a campaign. Care pauses; care/planning inputs are ignored.
Space plays/pauses; comma/period clamps at the saved frame bounds; F1 pauses and
returns to the same frame; V/Escape returns to the entry report or care; T opens
the selected report. S2 checkpoint/retry remains available. Recorded dimensions
are fitted with nearest-neighbor letterboxing, independent of the current pet.
`era_review.py` supplies explicit unavailable notices; `footer.py` explains keys.

The unchanged current-run producer remains available only for an era whose
recorded covenant/parameters still match. It records one real post-era life at
the era seed, and reopening consumes that artifact. It does not claim to capture
the original in-era evaluation or reconstruct historical weather. An older era
without a recording stays unavailable. Bad hashes, missing files, malformed
frames, ambiguous/escaping pointers and pre-existing unindexed files are never
silently replaced or reconstructed. Existing campaign/engine math is unchanged.

## Actual RED/GREEN and application evidence

Contract `docs/development/cycle-30-saved-replays.md` and runner registration
preceded RED. Actual commands, from the repository root:

```powershell
& .\.venv\Scripts\python.exe -B -m unittest discover -s game/tests -p test_saved_replays.py -v
& .\.venv\Scripts\python.exe -B -m unittest discover -s game/tests -p 'test_*.py'
& .\.venv\Scripts\python.exe -B game/build_release.py --dist game/dist/t3-saved-replays --work game/release_work/t3-saved-replays
& .\.venv\Scripts\python.exe -B labs/game_loop/verify_saved_replays.py --bundle game/dist/t3-saved-replays/Mechagotchi --output data/game_client/saved_replays_release_stage0.json --screenshots .development/t3-ui
```

Initial RED: 10 tests, eight failures and ten errors, preserved in
`.development/t3-red.log`. Initial implementation exposed test-fixture mistakes:
SQLite transaction context managers do not close their connections on Windows,
and snapshot has no action field. Explicit closing and the persisted log actor
pin now test the intended behavior without changing acceptance. Ten GREEN tests
passed in 4.392s; the initial whole game suite passed 319 tests in 45.834s.
Expanded refusal/schema checks passed 12. The final save-retry pin first found
that an unchanged checkpoint performs no write; its fixture now includes real
unsaved care progress before simulating a locked primary. Final targeted GREEN:
**13 tests in 5.757s**, `.development/t3-green-final-retry.log`.

`data/game_client/saved_replays_release_stage0.json` passed **17 checks / six
native launches / eight source pygame flows / 72 rendered frames**. These were
bounded native subprocess launches with SDL dummy video/audio, and source
pygame flows with supplied events and observed rendered output. Both
incumbent and Q-table policies create real eras and two post-era recordings,
resume natively, reopen latest/selected recordings, pause through help, scrub
to boundaries and ignore care/planning keys. Playback preserves all keeper
bytes. Missing earlier recordings are explicit; altered hashes are refused
without replacement; conflicting policy launches return 2 without mutation.
The supplied source events exercise actual app/render behavior. Inspected
screenshots show birth/end frames, visible honest provenance and readable
unrecorded/tampered notices in 384-pixel windows (`.development/t3-ui/`).

Native candidate: `game/dist/t3-saved-replays/Mechagotchi/Mechagotchi.exe`;
retain adjacent `_internal`. SHA256:
`0e3b9cc48662b73ff2893b0b1c5a3b974d98139d1d64287eb72234f83f3ee4d6`.

## Preservation, workflow and restart

`.development/t3-preservation.json` checks **3,322 prior lab/data files** and
**77 engine files** against T3 admission after T2 full closure: none changed.
Prior session, campaign, replay producer and archive modules are byte-identical;
all seven prior native executables retain their recorded hashes. Earlier
negative findings/default-policy refusal and controls are preserved. Diff review
and `git diff --check` pass; Git's existing LF/CRLF notices are informational.

The runner correctly refused an early REPAIR-to-ENHANCE advance before a current
passing verification; no bypass was used. Focused `20261004T192539-c157294c`
passed at `2026-10-04T19:27:06.095677+00:00`: **690 tests** (game 322,
package 324, CLI 44), no skips, **2,283 valid JSON artifacts**, no gate problems
or source mutations. The runner then advanced to ENHANCE at 19:27:46 UTC and
POLISH at 19:27:52 UTC with evidence/preservation notes in its checkpoints.

The single full gate `20261004T192757-866fdf0f` passed at
`2026-10-04T19:38:47.116282+00:00`: **2,576 tests / 24 suites**, two unchanged
DR 0034 zlib skips, **2,283 valid JSON artifacts**, no failures, gate problems
or source mutations. Both runs have source fingerprint:
`92389ad1aa9e97646358d784e39929c97948d4d9f118fd54d2ef7fab727dd868`.
Actual verification commands:

```powershell
$env:PYTHONPATH = (Resolve-Path tools/mechas_cli/src).Path
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --verify focused
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --verify full
```

The next active operator should read this report and the live queue, then inspect
current source before selecting further existing scope. Exact restart command:

```powershell
$env:PYTHONPATH = (Resolve-Path tools/mechas_cli/src).Path
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --status
```

Expected closure: slice t3-saved-replays, phase polish, focused_current true,
full_current true, local_complete true, running null. The task has no remaining
local implementation or verification gate. T1/T2/T3 are checked in the live
queue; no subsequent RED or new backlog item has been started.

Do not rerun unchanged completed slices. No new gameplay backlog is invented here. Native keyboard
interaction remains unavailable because the required node_repl/@oai/sky runtime
is unexposed; no alternate control route was used or sought. Human usability,
signing and published-SHA Windows/Ubuntu CI remain separate. Scoped runtime
write escalation worked without rejection or security changes. No publication
or remote-green claim is made.
