# Q3: New lives can be cleaned; covenants stay attached to their lives

Date: 2026-10-04. Decision: DR 0064. Predecessor: Q2 commit `7c82e85`.

## Why and design

Q3 prices DR 0059's default flip. Source review also found a real product gap:
the window selected a --slip companion but independently created its evolution
bench with the built-in covenant. A new campaign now inherits the companion's
validated profile, while an existing campaign resumes its recorded covenant.
The launcher now exposes authored profiles and isolated save directories.

The acceptance criteria were recorded before tests and measurement in
`docs/development/q3-default-covenant.md`. The candidate gate ran before the
default constant changed. Its six checks all passed, so the product landing
followed the recorded ADOPT rule. No metric or threshold was weakened.

## Findings

The instrument reproduces the complete committed companion-loop metrics and
DR 0059's complete metrics/decision. Candidate attentive keeping survives
400 ticks with 79 feeds; neglect still ends at tick 10 by starvation.
The scripted health-word keeper survives 72 ticks, cleaning at ticks 27/53
for +0.3076 each, and ends with health 0.976 and cleanliness 0.7472.
The derived cleaning threshold is 1 - 0.32 (floating representation
0.6799999999999999), recorded as computed rather than retuned or rounded in
the decision. The no-clean attentive arm reaches cleanliness 0 with stress 0:
this is optional care, not a requirement to keep an attentive pet alive.

The initial candidate's real 384x668 pygame window displays the engine value and G clean in a
181-pixel line within 368 usable pixels. G records one clean, and the saved
age-2 life resumes to age 4 with the same covenant. Actual pixels were inspected.
Final landing review found that a campaign notification could be vertically
clipped after adding the clean row. A pixel regression failed in both normal
and covenant modes. Increasing the footer from 140 to 184 pixels fixes that
loss; the final window is 384x712, with the complete notification raster
verified in both modes. The original candidate artifact retains its original
668-pixel observation. Human usability remains unmeasured. The legacy long
era-help and budget lines still clip horizontally; this known layout limit
is unchanged and does not hide the clean control.

The native Windows windowed executable was rebuilt after the footer fix,
then launched four times from an
external temporary cwd with isolated saves. Default fresh/resume ages are 4/7;
the explicit incumbent covenant remains off; a new campaign uses that selected
covenant; resume advances the same campaign from era 1 to era 2. Every process
exits 0. Both profile assets are present in the bundle. The executable hash
and size are observations in the release artifact, never acceptance constants.

## Exact source and artifact price

| Surface | Result |
| --- | --- |
| `packets.DEFAULT_SLIP`, `default_fixture_paths` | New product lives use `slip_v2_cleanliness.json` |
| `campaign._campaign_paths_under` | New default campaigns resolve the same covenant |
| `app._EraBench` | A new campaign uses its companion's profile; persisted campaigns win on resume |
| `build_release.BUNDLED_DATA` | Add the v0.2 covenant; keep the incumbent asset |
| `game/evidence.py` session/campaign/front-end builders | Retain explicit `HELLO_SLIP` historical bindings |
| `labs/game_loop/session_runner.py`, `replay_recorder.py` | Retain explicit LCD fixture paths |
| Existing `data/` artifacts and profile fixtures | No regeneration or modification |
| `default_covenant_gate_stage0.json` | New current-candidate observation and artifact plan |
| `default_covenant_release_stage0.json` | New actual native bundle observation |

The historical regeneration set is exactly **empty**. DR 0059 predicted a
blanket session-artifact cascade; inspection showed those experiments already
name their original covenant. Preserving those explicit bindings follows
DR 0053 rather than changing what the studies mean. This is a dated correction
beside the old prediction, not a rewrite of its evidence.

## Verification

All work and verification target the actual local repository on phase-l-gate.
Native CPython 3.14.3 and the unchanged lock's lab/CLI/game groups were used.
RED, before the landing:

```powershell
$python = 'C:/Users/ryanf/Documents/Codex/2026-10-03/task-3/repair/.venv/Scripts/python.exe'
& $python -B -m unittest discover -s game/tests -p test_default_covenant.py
# Ran 6 tests; FAILED (failures=4, errors=2).
& $python -B -m unittest discover -s tools/mechas_cli/tests -p test_game_launch_options.py
# Ran 2 tests; FAILED (failures=4), including subcases.
& $python -B -m unittest discover -s labs/game_loop -p test_default_covenant_gate.py
# Ran 1 test; FAILED (errors=1), missing instrument module.
```

The same commands now pass 7, 2 and 2 tests respectively. The seventh game
test checks the full rendered notification pixels in both display modes;
it first failed in both subcases before the footer fix. The instrument was
measured before the implementation script accepted its ADOPT artifact:

```powershell
& $python -B labs/game_loop/default_covenant_gate.py --output <isolated-candidate-report.json>
# ADOPT; six checks true; frozen instruments reproduced.
& $python -B game/build_release.py --windowed --dist <isolated-dist> --work <isolated-build-work>
& $python -B labs/game_loop/verify_default_release.py --bundle <isolated-dist>/Mechagotchi --output <isolated-release-report.json>
# four zero exits; ages 4/7; campaign eras 1/2; five landing checks true.
mechas develop --verify full --python $python
```

Closing full sweep `20261004T090122-7b250a41`: **2485 tests across
24 suites, zero skips**, every suite passed, and no source/evidence files
changed during verification. Artifact validation: 2267 JSON artifacts valid.
The complete summary and command are retained
in `.development/runs/20261004T090122-7b250a41/`.

The earlier run `20261004T085216-5c09fa5f` was deliberately stopped when
footer review found the clipping bug. It remains recorded as failed/incomplete
(1310 tests observed), rather than counted as a pass. The final full sweep
ran after the fix and after the final native release artifact was recorded.

The preservation audit confirms all **2947 incumbent data files** and
**25 incumbent SLIP fixture/example JSON files** remain byte-identical, with
no unexpected or concurrent owner changes. Only the explicit Q3 manifest
was staged. Runtime RED logs, screenshots, release build log and preservation
audit are retained under `.development/q3-evidence/`. The final native bundle
is `q3-windowed-final-20261004/Mechagotchi/` in the execution workspace; keep
the executable with its adjacent `_internal` folder. Its observed SHA-256 is
`e664e70c34c9c5be6c35fbb5a31163ab34a7f3ff61e9a04facc4a67ed751bbfc`.

The Q3 declaration was registered atomically after verifying Q2's clean,
committed, current full pass, then a new unverified REVIEW state was created.
The current CLI otherwise requires registering a new slice before starting it,
which invalidates the predecessor fingerprint. Q2's history was preserved; no
verification was carried into Q3 and no completion gate was skipped.

## Limits and continuation

Q4's hidden-axis survey and Q5's consolidation remain planned. No Q-table
promotion, reward changes, new danger thresholds or autonomous cleaning.
Existing pets and campaigns are not migrated. Native remote CI, signing,
other-platform builds and human usability remain unverified. Publication stays
blocked; no remote retry or alternate route was attempted.

## Sources

- `docs/development/q3-default-covenant.md`, `sunsetted/TODO.md`
- `research/decision_records/0059-cleanliness-mechanic-opt-in.md`, `0063-covenant-mechanics-authorship.md`, `0064-default-covenant-cleanliness.md`
- `research/algorithm_cards/default_covenant_gate.md`
- `labs/game_loop/default_covenant_gate.py`, `test_default_covenant_gate.py`, `verify_default_release.py`
- `game/tests/test_default_covenant.py`, `tools/mechas_cli/tests/test_game_launch_options.py`
- `data/game_client/default_covenant_gate_stage0.json`, `default_covenant_release_stage0.json`
