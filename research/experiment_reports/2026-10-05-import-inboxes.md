# Connected import inboxes - W1

2026-10-05. Locally complete. Full closing evidence follows the chronological implementation record.

REVIEW: V1 full_current verified at c12df2ab4d39 with preserved owner work.
F16 pack staging creates named covenant files unreachable through the fixed I
path. W1 preregisters the shared paused selector, engine validation and durable
application, plus explicit malformed/stale/conflicting input handling. Baseline
hashes cover 4,144 source files, 16 native executables and two live keeper files.

## Verification

Command for every targeted run:

```powershell
& .\.venv\Scripts\python.exe -B -m unittest discover -s game/tests -p test_import_inboxes.py -v
```

Initial RED (`.development/w1-red.log`): 11 tests in 1.280s, five failures and
11 errors across cases. Initial GREEN: 11 tests in 1.280s. Refinement RED:
17 tests in 2.061s, one failure for equivalent legacy-formatted staged JSON.
Nested-input RED: 18 tests in 2.034s, that failure plus an unhandled TypeError
for list-valued slip_version. Existing validator semantics are preserved; the
file consumer reports malformed-input exceptions as refusals. Equal parsed
JSON now keeps its original file bytes and reports already staged.
Application observations and final gates remain pending.

## Initial application observation and visual repair

The first native candidate, `game/dist/w1-import-inboxes/Mechagotchi/Mechagotchi.exe`,
passed 23 checks, four native launches, twelve source flows and 75 rendered frames.
The committed starter pack stages four covenants and four creatures; I selects
slip_lcd_seed without renaming. Both policies persist, the companion stays exact
during import, and the native next era uses the imported covenant while preserving
its predecessor. Real founder admission/refusal reasons survive. Raw observation:
`.development/w1-observed.json`; frozen `data/game_client/import_inboxes_release_stage0.json`.

Screenshot review found the unreadable notice below a long filename and an Enter
instruction remaining visible after successful import disabled that action.
Visual RED: 20 tests in 2.872s, two failures (`w1-red-visual.log`). The picker now
states unavailable/complete before long details, and F1 describes its own workflow.
GREEN: 20 tests in 2.828s (`w1-green-polished.log`). A fresh final native candidate
will preserve the first build; no historical artifacts or thresholds are changed.

## Final application candidate

Polished observations: **28 checks passed, four native launches, twelve source
pygame flows, 75 rendered frames**, both policies. Native new/resume and next-era
execution are separate from source keyboard/render observations. The native
candidate is `game/dist/w1-import-inboxes-final/Mechagotchi/Mechagotchi.exe` with
adjacent `_internal`. Source hashes in the observation match current source.
Raw evidence: `.development/w1-observed-final.json`, screenshots:
`.development/w1-final-ui/`; frozen `data/game_client/import_inboxes_release_stage1.json`.

```powershell
& .\.venv\Scripts\python.exe -B game/build_release.py --dist game/dist/w1-import-inboxes-final --work game/release_work/w1-import-inboxes-final
& .\.venv\Scripts\python.exe -B labs/game_loop/verify_import_inboxes.py --bundle game/dist/w1-import-inboxes-final/Mechagotchi --fixtures .development/w1-final-keepers --screenshots .development/w1-final-ui --output .development/w1-observed-final.json
```

The frontend-design skill's strict static audit reported zero findings in the
explicit native-game source scope (`.development/w1-premium-audit.json`). Its
scanner has no Python/SDL coverage; it is not accessibility or behavior proof.
The project-owned source event, save-byte, failure and screenshot checks above
provide that bounded evidence. Existing visual and UX sources govern this SDL
surface; no new theme, font, web layer or dependency was introduced.

During this work the owner/external tooling committed `0c4e5c065e16d5532835f48d5e0d1b6de2d5fc1b`.
The agent performed no Git mutation. Reconciliation found only the expected W1
byte changes from the c12df2 baseline; final observed source stayed exact. The
committed stage0 observation is preserved unchanged; stage1 paths are portable.
Full local gates are pending at this point in the chronological record.

## Sources

- docs/development/cycle-33-import-inboxes.md
- research/decision_records/0076-connected-import-inboxes.md
- game/tests/test_import_inboxes.py
- labs/game_loop/verify_import_inboxes.py
- research/algorithm_cards/import_inboxes.md
- data/game_client/import_inboxes_release_stage0.json
- data/game_client/import_inboxes_release_stage1.json

## Local closure

Focused `20261005T115442-0a47b5d7` passed **760 tests** (package 324, CLI 44,
game 392). Full `20261005T115738-611ddb0c` passed **2,656 tests / 24 suites**,
the two named DR 0034 zlib skips, and **2,294 valid JSON artifacts**. All suites
passed; no tracked or untracked source file changed during either run.
The existing Python 3.13.9 interpreter ran both checks. Exact commands:

```powershell
$env:PYTHONPATH = (Resolve-Path tools/mechas_cli/src).Path
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --verify focused
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --verify full
& .\.venv\Scripts\python.exe -B .development/w1-audit.py
git diff --check
```

The final executable SHA256 is
`c3bfd5dc748eca391d0b01539af0201ed609bfbd867e711df1ef4cd67cf9ab7b`.
Its 28 application checks, four native launches, twelve source flows and 75
rendered frames are distinct from the full regression sweep. Full results:
`.development/w1-full.json` and its run directory; preservation:
`.development/w1-preservation.json`. The preservation audit compares 4,144
baseline source files and confirms all 3,339 prior lab/data files, 77 engine
files, 40 existing game test files, 16 prior native builds and two live keeper
files retain their original hashes. New tests add coverage; no existing test
or scientific threshold was changed. Final source diff review covers picker
event routing, digest-bound validation, exclusive per-item staging, error/help
states and connected application evidence. `git diff --check` passes.

The full run started at `0c4e5c065e16d5532835f48d5e0d1b6de2d5fc1b`.
An additional owner/external commit, `0fda2dc646eaa87c9a13b1c6c935126791e01a33`,
recorded the remaining implementation and observation bytes. Read-only runner
status confirms the exact verified source fingerprint remains current at this
HEAD; no repeat of unchanged tests is warranted. The agent made neither commit.

Closure is `.development/w1-closed.json`; `.development/w1-live-handoff.json`
records exact HEAD, dirty-file hashes, candidate identity and runner state.
Restart with the existing source CLI's read-only `develop --status`, then review
this result and actual source before preregistering another cohesive slice.
Do not rerun unchanged gates. The completed F15/F16 import connection creates
no new scientific scope. Ordinary covenant application still uses the existing
synchronous model-loading path; its cold-load responsiveness is not measured
here. Native keyboard/human usability and maximum inbox scale remain unobserved.
Windows/Ubuntu Actions on an exact published SHA remain unmet. No remote
executor is configured or claimed. No agent commit, synchronization, push,
service or credential installation occurred; Git operations remain the user's.
