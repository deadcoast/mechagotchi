# Cycle 28: playable learning integration

Source: authoritative repository, branch phase-l-gate, HEAD
8145b4aa35a4968e45c60b00121a740129183f47, Python 3.13.9. No Git mutations.
Q5 edits are preserved. The user explicitly waived commit sequencing after
reviewing the conflict; no scientific threshold or publication gate was waived.

## Implemented R1/R2

Public bounded Q-table producer/follower, complete lab decision/state parity,
cold deliberation helper repair, explicit session policy, exact learned-state
resume, cold succession with parent policy provenance, keeper-mediated feeds,
app casing provenance and source/CLI/native launch options. The incumbent and
old save format stay unchanged. The experimental evaluator honors engine
reflexes before learning; it is explicitly selected by the game.

Actual RED/GREEN commands (repository interpreter throughout):

```
.venv/Scripts/python.exe -B -m unittest discover -s labs/micro_threads -p test_package_qtable_parity.py -v
.venv/Scripts/python.exe -B -m unittest discover -s game/tests -p test_learning_policy.py -v
.venv/Scripts/python.exe -B -m unittest discover -s tools/mechas_cli/tests -p test_game_launch_options.py -v
.venv/Scripts/python.exe -B tools/ci/run_sweep.py --suite lab:micro_threads --suite lab:grid_genome --suite package --suite game --suite cli --log-dir .development/r1-r2-focused
.venv/Scripts/python.exe -B labs/micro_threads/package_qtable_parity.py
.venv/Scripts/python.exe -B game/build_release.py --dist game/dist/r2-learning --work game/release_work/r2-learning
.venv/Scripts/python.exe -B labs/game_loop/verify_learning_release.py --bundle game/dist/r2-learning/Mechagotchi --output data/game_client/playable_learning_release_stage0.json
```

RED: package 87 failing subcases exposed absent producer/follower; game 15
errors exposed the absent policy interface. Intermediate parity exposed missing
CTM helpers and a test fixture's false assumption that every warm additive
choice disagreed. Complete equality assertions remain; a separate known
conflicting vector pins the override. GREEN: 5 parity tests, 9 policy tests,
4 launcher tests; focused sweep passed 1,020 tests across five suites.
Logs: `.development/r1-qtable-red.log`, `r1-qtable-green.log`,
`r2-policy-red.log`, `r2-policy-green.log`, `r2-launcher-green.log`, and
`.development/r1-r2-focused/summary.json`.

New artifacts (historical Q1/Q3 evidence untouched):
- `data/micro_threads/package_qtable_parity_stage0.json`: complete original Q1
  record reproduced, excluding only wall-clock duration; package parity passed.
- `data/game_client/playable_learning_release_stage0.json`: 16 actual launches,
  13 checks passed, including source/CLI/native new/resume, byte-preserving
  conflicts, invalid input, native succession and a 160-tick warm life resumed
  by the executable. Isolated saves and external cwd; no user's save touched.

## Pipeline continuity

The existing runner refused starting the newly registered scope because its
registration itself invalidated Q5's current fingerprint. No result was
fabricated and no gate was bypassed. Existing state retains the failed start
and an explicit R1/R2 checkpoint. This continuation uses the same runner and
full sweep before starting the already preregistered R3/R4 slice. Q5's prior
full evidence remains intact. The next scope is registered before this full
sweep so the same admission problem does not recur.

## Remaining gates

R1/R2 full sweep passed: `.development/runs/20261004T155004-f33ec4a2/result.json`,
2,509 tests across 24 suites, two documented DR 0034 skips, 2,271 valid JSON
artifacts, no file mutations. Preservation audit checked 3,298 existing
scientific files unchanged and retained the original Q4 executable hash.
Actual app screenshots in `.development/r2-ui/` show a tick-22 followed feed
where the additive choice was play; wrapping and paging were inspected.
Four additional native launches preserved covenant/campaign continuity
(`.development/r2-default-continuity.json`). An external owner commit
`03ec951269984be95f94254aba6b0ae8a313c0b9` appeared during the sweep and
contains the unchanged verified bytes; the agent performed no Git mutations.
The runner advanced REPAIR -> ENHANCE -> POLISH and successfully started
`r3-r4-product-release` from the preregistered scope.
R3 preregistration records a real corpus incompatibility: the current covenant
rejects forty of Q1's fifty palette variants. Preserve that finding; do not
repaint or filter the corpus to manufacture adoption. R4 repairs frozen-release
save-home selection while preserving legacy saves. Remote CI/signing and human
usability remain separate and unverified.
