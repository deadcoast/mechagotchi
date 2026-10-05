# Connected import inboxes - W1

2026-10-05. Implementation in progress; no completion claim.

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
