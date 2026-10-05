# Responsive covenant preparation - W2

2026-10-05. Locally complete. Full closure follows the measured implementation record.

## Review and measured defect

W1 was reviewed at owner HEAD 0fda2dc646ea in the actual source tree, retaining
all eight closure edits. Real pygame source events with the session corpus and
40 repair epochs showed cold imports blocking polling/rendering for 4.20-4.41s,
including invalid/stale refusals. Each needlessly created an evolution repair
cache. The companion remained unchanged. One-file and 256-file inboxes use the
same actual corpus; file count is not an evolution population measurement.

W2 preregistered the repair in `docs/development/cycle-34-responsive-preparation.md`
before RED. Ten new tests initially failed (six failures, five errors across
subcases, 1.808s); GREEN passed all ten in 2.509s. Unchanged W1 tests passed
20/2.436s and era-responsiveness tests 12/4.107s. Exact targeted commands:

```powershell
& .\.venv\Scripts\python.exe -B -m unittest discover -s game/tests -p test_responsive_preparation.py -v
& .\.venv\Scripts\python.exe -B -m unittest discover -s game/tests -p test_import_inboxes.py -v
& .\.venv\Scripts\python.exe -B -m unittest discover -s game/tests -p test_era_responsiveness.py -v
```

## Implementation and result

`load_campaign_inputs` retains its eager default. Its explicit `with_models=False`
path reads the same corpus/covenant/adopted readability artifact. The bench uses
that path for covenant/import/export/adoption and constrained hatch consumers.
`prepare_campaign_models` builds both evolution models before publishing them;
it leaves the caller unchanged on failure. E requests models inside its existing
joined worker, reuses complete models and preserves the original trainer, cache
key, inputs, seeds and scientific definitions. No package or historical test changed.

Seconds, same four source event scripts before/after:

| Case | Import before | Import after | Poll gap after |
| --- | ---: | ---: | ---: |
| valid-normal | 4.1943 | 0.0314 | 0.0344 |
| valid-larger | 4.4007 | 0.0379 | 0.0407 |
| invalid-cold | 4.3797 | 0.0233 | 0.0271 |
| stale-cold | 4.4044 | 0.0249 | 0.0280 |

The connected final observation passed **76 checks**, **14 source flows /
560 rendered frames**, on both policies, plus **4 native session-scale launches**.
Largest measured source poll gap: 0.0488s. Cold-load cancel/close request
latency: at most 0.0115s; work still finishes its current model-load boundary
before joining, and no save/preparation bytes change on cancellation. Selection,
reopened/repeated imports, stale refresh, authority refusal, conflict/repeat
pack staging and state-write retry all retain explicit outcomes and paused care.

Tiny and normal model/era/original-recording hashes exactly match eager hashes
retained before the edit. A real normal era earned the larger 32-population /
12-generation budget; eager and deferred next-era reports and original recordings
match exactly. These are equality controls, not new biological measurements.

## Instrument correction and retained limits

The first connected observation reported two failed write-retry inventory checks.
Inspection identified the intended new recovery copy `campaign_state.bak.json`.
Stage1 retains the same existing-file preservation rule and additionally requires
that the only added file is this backup with the exact prior primary hash. Both
policies pass: zero changed existing files. The initial negative observation
survives in stage0; the app's established backup or scientific thresholds were
not changed to make a check pass. State/ledger writes retain their established
separate-write behavior; this is not a new cross-file transaction guarantee.

Native binary: `game/dist/w2-responsive-preparation/Mechagotchi/Mechagotchi.exe`,
adjacent `_internal` required. SHA256: `26e8e2e1cdfe233286b0fc1de5588611ce6e418055bb0e040fea5948362623c3`.
Source keyboard/render evidence and native process coverage remain distinct.
Native keyboard/human usability, maximum inbox/history scale and exact-published-SHA
Windows/Ubuntu Actions remain unverified. No remote executor is configured.

```powershell
& .\.venv\Scripts\python.exe -B game/build_release.py --dist game/dist/w2-responsive-preparation --work game/release_work/w2-responsive-preparation
& .\.venv\Scripts\python.exe -B labs/game_loop/verify_preparation_responsiveness.py --fixtures .development/w2-final-keepers --screenshots .development/w2-final-ui --eager-reference .development/w2-eager-baseline.json --bundle game/dist/w2-responsive-preparation/Mechagotchi --output .development/w2-observed-final.json
```

The before-stage0 artifact includes the eager reference for portable reproduction;
extract its `eager_reference` value to a fresh JSON file for `--eager-reference`.
Raw pre/post measurement logs and the first failed observation remain under
`.development/w2-*`; never overwrite an existing observation's fixture directory.

The owner/external commit 64bea16f10c8b09639837024935ffc5a5ba1fdf9 recorded the
W1 closure and W2 implementation during this work. The agent made no Git mutation
and preserves that commit. The current source and candidate hashes are recorded
by the final observation; the closing runner/preservation checks are recorded below.

## Next source-backed scope

F8 explicitly distinguishes constrained hatch explanations from era-side WFC.
A WFC hatchery explanation still needs the separately named engine trace seam;
do not manufacture a trace in the UI. The existing constrained hatch path already
carries a real explanation but H immediately adopts and only shows its summary.
Review its full recorded trace and the established preview design before selecting
a further review/preview consumer. This report does not preregister that work.

## Local closure

Focused `20261005T123134-92894aa5` passed 862 tests (game 402, package 324,
CLI 44, game-loop lab 92). Full `20261005T123344-a9435c5a` passed **2,666 tests /
24 suites**, two documented DR 0034 zlib skips and **2,297 valid JSON artifacts**.
No source files changed during either verification. Both used the existing
repository Python 3.13.9 environment, without dependency/security changes.

```powershell
$env:PYTHONPATH = (Resolve-Path tools/mechas_cli/src).Path
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --verify focused
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --verify full
& .\.venv\Scripts\python.exe -B .development/w2-audit.py
git diff --check
```

Preservation audit: all 3,342 prior lab/data files, 77 engine files, 41 existing
game tests, 19 prior native executables and two live keeper files retain their
baseline hashes. W1's completed report/card/decision are unchanged. New evidence
retains the original stall and first negative instrument result. The source
diff preserves eager defaults, exact trainer/cache parameters and import/save
authority; screenshots cover loading/cancel, import completion and retry. Final
observed source/native hashes remain exact and `git diff --check` passes.

Evidence: `.development/w2-full.json`, `.development/w2-preservation.json`,
`.development/w2-closed.json`, and `.development/w2-live-handoff.json`.
The latter records current HEAD, dirty-file identities and no active worker.
Next: read-only source `develop --status`, review W2, then investigate the
existing hatch trace/preview seam described above before any further contract.
Do not rerun unchanged gates. Native keyboard, maximum scale and published-SHA
CI remain outside this local result; no remote executor or agent Git mutation.

## Sources

- docs/development/cycle-34-responsive-preparation.md
- research/decision_records/0077-responsive-covenant-preparation.md
- research/algorithm_cards/responsive_preparation.md
- game/src/mecha_game/{app,campaign,era_work,hatchery}.py
- game/tests/test_responsive_preparation.py
- labs/game_loop/verify_preparation_responsiveness.py
- data/game_client/responsive_preparation_before_stage0.json
- data/game_client/responsive_preparation_release_stage0.json
- data/game_client/responsive_preparation_release_stage1.json
- research/experiment_reports/2026-07-12-hatchery.md
