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

## Sources

- docs/development/cycle-33-import-inboxes.md
- research/decision_records/0076-connected-import-inboxes.md
- game/tests/test_import_inboxes.py
