# S1 safe companion resume and explicit recovery

Date: 2026-10-04. Source: authoritative repository, branch `phase-l-gate`,
external owner HEAD `d1ebd033d13938f2a3732282cc6fe6b8ad8255c5`, Python 3.13.9.
Status: locally complete; full gate and actual source/CLI/native observations passed.
No agent Git mutations. Cycle 28 is complete and reviewed; no old sweep rerun.

## Problem and change

Saved GenerationModel JSON was reconstructed without structural validation;
malformed counts, unsupported strategies or wrong dimensions could survive load
and fail later during generation. The app had no explicit recovery option for
its existing backup. Required save structures are now checked before play;
engine-owned model validation preserves valid counts, metadata and output.

`--recover-backup` validates the exact backup snapshot and policy, retains any
previous primary byte-for-byte in `companion.before-recovery-<digest>.json`, and
atomically restores the primary. Invalid/conflicting backups are refused before
writes. A backup-only save home remains discoverable; a missing primary cannot
silently start a replacement life. Atomic normal saves prevent partial-primary
truncation; injected failures before both backup and primary replacement retain
readable prior bytes. Companion/lineage remain separate file writes.

Incumbent and experimental policy status are visible in live/dead casing pages.
The recorded per-life choice, learned state, valid legacy saves and deterministic
continuation remain unchanged. No training algorithm or adoption threshold changed.

## Reproduction and observed checks

Preregistered `docs/development/cycle-29-safe-resume.md` before RED. The existing
runner started `s1-safe-resume` after Cycle 28 closure, with fresh verification
state. Actual RED command:

```powershell
.venv/Scripts/python.exe -B -m unittest discover -s game/tests -p test_safe_resume.py -v
```

Initial `.development/s1-red.log`: 7 tests, 11 failures / 5 errors from missing
validation/recovery behavior. The backup-only discovery follow-up RED is
`.development/s1-home-red.log`: 10 tests, one failure. Same command GREEN:
`.development/s1-green.log`, 10 passed. CLI forwarding/conflict coverage adds two
tests in `tools/mechas_cli/tests/test_game_launch_options.py`.

```powershell
$env:PYTHONPATH = (Resolve-Path tools/mechas_cli/src).Path
.venv/Scripts/python.exe -B -m mechas_cli.app develop --verify focused
.venv/Scripts/python.exe -B game/build_release.py --dist game/dist/s1-safe-resume --work game/release_work/s1-safe-resume
.venv/Scripts/python.exe -B labs/game_loop/verify_safe_resume_release.py --bundle game/dist/s1-safe-resume/Mechagotchi --output data/game_client/safe_resume_release_stage0.json
.venv/Scripts/python.exe -B -m mechas_cli.app develop --verify full
```

Focused run `20261004T165128-d92d2f5f`: 645 tests in package/game/CLI, 2,274 JSON
artifacts, no source mutations. This preceded the one-test discovery follow-up
and final observation harness; it is iteration evidence, not final closure.

The final native bundle and real source/CLI launchers passed 48 process launches
and 48 checks, covering both policies: malformed-model refusal; policy and
new-life conflicts; exact backup/primary preservation on recovery; deterministic
continued state; backup-only recovery; bad-backup refusal. No actual keeper
home was touched. Four rendered pages were visually inspected, including the
recovery archive notice and both policy labels. Screenshots are retained under
`.development/s1-ui/`; the artifact lists all captures and actual commands.

Native executable: `game/dist/s1-safe-resume/Mechagotchi/Mechagotchi.exe`, keep
`_internal` beside it. SHA256: `f4f89b5513c1a56fc29bb4321292160ba2868698afcbcfea2db5f7ee788211b1`.
Preservation audit `.development/s1-preservation.json` compares 3328 existing
scientific files against the completed R3/R4 inventory: none changed. Q4, R2 and
R4 executable hashes are unchanged. The new harness/artifact are separate files.

## Closing gate and restart

Full run `20261004T170013-413498d4` passed at
`2026-10-04T17:11:50.871058+00:00`: **2,528 tests across 24 suites**,
two named DR 0034 zlib skips, 2275 JSON artifacts valid; no source
mutations, no sweep problems, and `git diff --check` passed. Source fingerprint:
`90ba750fdde942642881801d41222c8c982b3979e2309b852a75a4a9ee7522de`.

The existing runner progressed REVIEW -> REPAIR -> ENHANCE -> POLISH using this
current full pass, with actual RED/GREEN logs, launch observations and retained
restart notes. `.development/state.json` is the operational resume point;
`full_current=true`, `local_complete=true`, `running=null` is the closing state.
No duplicate sweep is needed for unchanged source. Read this completed result
and the live queue before preregistering another slice. No new task's RED has
started; commits, sync and pushes remain the user's.

Remaining limits: recovery rolls back to the prior save, not the most recent
unsaved progress; no multi-file transaction or automatic recovery; corrupted
backup bytes are refused, not reconstructed. Remote native Windows/Ubuntu CI on
the published SHA, signing and human usability remain unverified. R3's Q-table
default-adoption refusal is unchanged.
