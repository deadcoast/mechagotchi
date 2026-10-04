# S2 durable play checkpoints and save-failure recovery

Date: 2026-10-04. Authoritative repo, `phase-l-gate`, owner HEAD
`d1ebd033d13938f2a3732282cc6fe6b8ad8255c5`, existing Python 3.13.9.
Status: locally complete; the single pending full gate passed on 2026-10-04.
S1's complete result was reviewed without rerunning its unchanged full sweep.
No agent Git mutation, alternate checkout, environment or persistent service.

## Real failure and product repair

Actual app fault injection (`.development/s2-review.json`) showed two defects:
a failed companion replacement preserved the old pet at age 1 but exported two
lineage records against its one; a failed export raised before the writable
companion could record current progress. The browser reads embedded lineage.

`CompanionSession.save_checkpoint` commits the complete pet first. Missing or
stale standalone exports are repaired from that validated save before play;
old export bytes are backed up. Export failure warns while preserving the new
primary. This single authority resolves resume ambiguity without a multi-file
transaction. S1 backup recovery derives lineage from the restored pet, retaining
its policy, learned state, primary archive and earlier progress exactly.

Ctrl+S saves immediately instead of queuing sleep. Death, succession and adoption
checkpoint. Failed primary writes pause care, hold the current pet in memory,
and show retry/discard controls. A failed interactive quit stays open; Ctrl+S
retries and completes that quit, while Ctrl+Q explicitly discards unsaved state.
Bounded runs exit 1 without tracebacks. A quit request does not advance another
care tick. Repeated identical checkpoints preserve the previous useful backup.

The first rendered error included long OS paths. Final casing keeps the concise
reason and retry/discard instructions; detailed primary diagnostics remain in
stderr. Final screenshots under `.development/s2-ui/` were visually inspected.

## Actual verification

Preregistered `docs/development/cycle-29-safe-checkpoints.md` before RED, then
started `s2-safe-checkpoints` through the existing workflow with fresh evidence.

```powershell
.venv/Scripts/python.exe -B -m unittest discover -s game/tests -p test_checkpoints.py -v
.venv/Scripts/python.exe -B -m unittest discover -s game/tests -p 'test_*.py' -v
.venv/Scripts/python.exe -B game/build_release.py --dist game/dist/s2-safe-checkpoints --work game/release_work/s2-safe-checkpoints
.venv/Scripts/python.exe -B labs/game_loop/verify_checkpoints_release.py --bundle game/dist/s2-safe-checkpoints/Mechagotchi --output data/game_client/safe_checkpoints_release_stage0.json
$env:PYTHONPATH = (Resolve-Path tools/mechas_cli/src).Path
.venv/Scripts/python.exe -B -m mechas_cli.app develop --verify focused
```

RED `.development/s2-red-final.log`: 9 tests, 2 failures / 7 errors. GREEN
`.development/s2-green.log`: 9 passed. Whole-game iteration: 287 tests passed
(`.development/s2-game-iteration.log`); final focused gate recorded below.

Final artifact `data/game_client/safe_checkpoints_release_stage0.json` records
48 actual source/CLI/native process launches and 48 passing checks, including
invalid-model/policy refusal, blocked export without lost progress, blocked
primary with coherent old state, exact retry progress, and recovery of the
prior policy/state/lineage. Four actual interactive app flows (both policies x
retry/discard) passed: care paused, retry saved age 1, discard retained original
age-0 bytes. Native filesystem-fault fixtures were private temporary directories;
no real user save home was touched. Three final rendered pages were inspected.

Native candidate: `game/dist/s2-safe-checkpoints/Mechagotchi/Mechagotchi.exe`,
retain adjacent `_internal`. SHA256: `f4179c2dda5a86943f6eb397d42adb3e015f57c6d3a23c467f9e6492440c0582`.
Preservation `.development/s2-preservation.json`: 3330 existing scientific
files and 77 engine files unchanged against S1's full inventory; Q4/R2/R4/S1
executables retain their previous hashes. All new observations are separate.

## Implemented checkpoint and exact next gate

Final focused run `20261004T173506-cd1787fd` passed at `2026-10-04T17:35:59.280401+00:00`:
**655 tests** (game 287 / package 324 / CLI 44), no skips,
2276 JSON artifacts valid, no source mutations, no sweep problems and
`git diff --check` passed. Source fingerprint:
`947f0743723b932a9dd8f32cc2fb2d6bc6c3da8d60c1749564114702b52c8172`.

The single pending full run `20261004T173915-19f22122` passed at
`2026-10-04T17:51:03.775927+00:00`: **2,537 tests across 24 suites**,
two documented DR 0034 zlib skips, 2276 JSON artifacts valid, no source
mutations and no gate problems. Source fingerprint remains
`947f0743723b932a9dd8f32cc2fb2d6bc6c3da8d60c1749564114702b52c8172`. No repair or rerun was necessary.

The existing workflow closed S2 in POLISH with `full_current=true`,
`local_complete=true`, `running=null`. The prior focused/native observations
remain valid; no unchanged S1 verification was repeated. S2 is reviewed and
archived in Cycle 29 before beginning the next player-facing increment.
No commit, sync or push was performed.

Limits: standalone exports may be stale until resume after abrupt interruption;
the companion's embedded state is authoritative. A still-unwritable primary
cannot persist new progress; interactive memory remains until explicit discard.
Ctrl+Q intentionally loses unsaved progress. There is no cross-file transaction
or periodic unattended saving. Remote published-SHA Windows/Ubuntu CI, signing
and human usability remain unverified; Q-table default adoption remains refused.
