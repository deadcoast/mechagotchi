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

## R3: REFUSE default adoption

`data/game_client/playable_learning_gate_stage0.json` preserves all 1,500
attempted lives: 500 per arm, 100 per keeper, 200 requested ticks, seed base
20260709. Each arm admits 100 and refuses 400 due to the unchanged covenant's
palette constraint. No genome was repainted, covenant broadened or corpus
member silently filtered. Full-corpus welfare and adoption gains are null.

The admitted subset is diagnostic: follower welfare gains are +17.717% against
the actual incumbent and +18.239% against additive. These do not satisfy the
incomparable full-corpus gate. It made 2,154 recommendations and followed 1,681
autonomous decisions. Compared with incumbent, the admitted follower trials
had 132 additional beg ticks and 128 additional keeper feeds. No cleaning
behavior was invented for the inherited keepers.

Both historical Q3 controls reproduced exactly. The candidate attentive
control survives 400 ticks with 84 feeds (incumbent 79); neglect still dies
of starvation at tick 10. The complete per-life records, executed-action
counts and all mandatory checks are in the artifact.

Per-keeper admitted-subset results (each row: 20 admitted / 80 refused):

| Arm | Keeper | Diagnostic welfare | Mean survival ticks | Beg ticks | Keeper feeds | Keeper plays | Keeper cleans |
|---|---|---:|---:|---:|---:|---:|---:|
| incumbent | attentive | 0.604053 | 153.900 | 673 | 604 | 123 | 0 |
| incumbent | neglectful | 0.043754 | 10.800 | 111 | 3 | 0 | 0 |
| incumbent | erratic | 0.092056 | 23.300 | 161 | 56 | 48 | 0 |
| incumbent | punitive | 0.037652 | 9.450 | 83 | 0 | 33 | 0 |
| incumbent | exploratory | 0.040661 | 10.000 | 100 | 0 | 32 | 0 |
| additive | attentive | 0.600294 | 153.000 | 664 | 601 | 122 | 0 |
| additive | neglectful | 0.043754 | 10.800 | 111 | 3 | 0 | 0 |
| additive | erratic | 0.092201 | 23.300 | 164 | 56 | 48 | 0 |
| additive | punitive | 0.037652 | 9.450 | 83 | 0 | 33 | 0 |
| additive | exploratory | 0.040661 | 10.000 | 100 | 0 | 32 | 0 |
| follower | attentive | 0.748862 | 182.950 | 802 | 732 | 138 | 0 |
| follower | neglectful | 0.043754 | 10.800 | 111 | 3 | 0 | 0 |
| follower | erratic | 0.092201 | 23.300 | 164 | 56 | 48 | 0 |
| follower | punitive | 0.037652 | 9.450 | 83 | 0 | 33 | 0 |
| follower | exploratory | 0.040661 | 10.000 | 100 | 0 | 32 | 0 |

R3 RED/GREEN: `.venv/Scripts/python.exe -B -m unittest discover -s
labs/game_loop -p test_playable_learning_gate.py -v` first failed because the
harness did not exist, then both real-session/gate tests passed. Measurement:
`.venv/Scripts/python.exe -B labs/game_loop/playable_learning_gate.py`.
Logs: `.development/r3-red.log`, `r3-green.log`, `r3-measurement.log`.

## R4: native save-home repair and final playable release

`game/src/mecha_game/app.py::default_keeper_dir` now distinguishes a frozen
release from a checkout. Fresh native saves use the user's `.mechagotchi`.
Existing `_internal/keeper` saves continue there when the user home has no
save. When both contain lives, the user home wins and legacy bytes remain
untouched. Explicit `--keeper-dir` takes precedence. No migration or deletion
of user saves was performed.

The RED test reproduced the old bundled-data-directory selection; both save
home tests pass after repair. Actual final release verification recorded 26
process launches and 23 checks across policy, warm resume, succession,
covenants, campaigns and save homes. Artifact:
`data/game_client/product_release_stage0.json`; earlier R2/Q4 evidence and
binaries are preserved. Windows bundle:
`game/dist/r4-learning/Mechagotchi/Mechagotchi.exe` (keep `_internal` adjacent).

Commands:

```
.venv/Scripts/python.exe -B -m unittest discover -s game/tests -p test_native_save_home.py -v
.venv/Scripts/python.exe -B game/build_release.py --dist game/dist/r4-learning --work game/release_work/r4-learning
.venv/Scripts/python.exe -B labs/game_loop/verify_save_home_release.py --bundle game/dist/r4-learning/Mechagotchi --output data/game_client/native_save_home_stage0.json
.venv/Scripts/python.exe -B labs/game_loop/verify_learning_release.py --bundle game/dist/r4-learning/Mechagotchi --output .development/r4-learning-release.json
.venv/Scripts/python.exe -B labs/game_loop/verify_default_release.py --bundle game/dist/r4-learning/Mechagotchi --output .development/r4-default-continuity.json
```

## Existing pipeline repaired

`tools/mechas_cli/src/mechas_cli/development.py` now admits incoming contract
registration against a retained completed full-pass inventory. Only the new
Markdown contract and workflow registry may differ; prior contract bytes and
scope must be identical. Source/data changes, prior failures or an unfinished
phase remain blocked. Original evidence is archived and the new slice starts
with no passing verification. This fixes the observed R1 registration
failure without weakening scientific acceptance or inheriting a false pass.

RED/GREEN command: `.venv/Scripts/python.exe -B -m unittest discover -s
tools/mechas_cli/tests -p test_development.py -k registration -v`. The actual
positive admission case failed before repair; all three cases now pass,
including rejection of changed source and prior scope/contract.

Final R3/R4 full sweep passed: `20261004T162036-b03ceece`, 2,516 tests
in 24 suites, two named DR 0034 skips, 2274 JSON artifacts valid; no
source mutations. Source fingerprint `70b2a40bf2d95d40f6e5ddcec1774157c8060f5d2e20a23daed0af3192b9e86b`.
`.development/r3-r4-preservation.json` confirms all 3,303 previously inventoried
scientific files unchanged and both earlier native executables preserved.
The existing runner advanced through ENHANCE and POLISH; Cycle 28 is locally
complete. External HEAD d1ebd033 is preserved; no agent Git mutations.
Next product outcome: validated companion/model resume and explicit safe
backup recovery, with current policy clearly shown. R3 refusal remains intact.
