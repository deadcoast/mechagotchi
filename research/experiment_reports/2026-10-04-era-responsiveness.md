# Era responsiveness (Cycle 30 T5)

2026-10-04. Authoritative repository `C:/Users/ryanf/github/_shelved/mechagotchi`,
branch `phase-l-gate`, HEAD `d1ebd033d13938f2a3732282cc6fe6b8ad8255c5`.
Existing Python 3.13.9 .venv; owner edits preserved; no Git mutations.
T4 full 20261004T202052-aaa63dd1 was closed before this explicit delegation.

## REVIEW: actual defect

Normal session configuration: 6 x 16 candidates, two damage cycles, 16 ticks.
The larger fixture used 12 x 32 through the real covenant budget earned by the
normal era, without fabricated unlocks. Each process was bounded at 90 seconds
and a 512 MiB working-set stop threshold, sampled every 50ms. No limit was hit.

| Case | Evaluations | Era call | Event gap | Frame gap | Help delay | Peak MiB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Normal | 96 | 9.313s | 9.327s | 9.337s | 9.221s | 64.555 |
| Earned larger | 384 | 11.845s | 11.866s | 11.875s | 11.760s | 75.043 |

Both source runs saved consecutive era seeds (20260707, 21260707), complete
reports and no pending journal. The defect is event/render starvation, not
observed save loss. Help was posted through actual pygame events during the
computation and received only after it returned. Native keyboard was not used.
The first probe sampled the Windows venv launcher for memory; it is retained
as preliminary evidence only. Corrected probes use the worker's own PID and
terminate that owned worker on a bound breach.

```powershell
& .\.venv\Scripts\python.exe -B labs/game_loop/measure_era_responsiveness.py --keeper .development/t5-baseline-keeper --output .development/t5-baseline.json
& .\.venv\Scripts\python.exe -B labs/game_loop/measure_era_responsiveness.py --keeper .development/t5-bounded-baseline-keeper --output .development/t5-bounded-baseline.json
```

Frozen artifact: `data/game_client/era_responsiveness_review_stage0.json`.
Detailed original results: `.development/t5-bounded-baseline-normal.json` and
`-larger.json`. Canonical report hashes are f64fd5671f0ade11fe384b79b29c84b1788939120c5244b61e851f15e64e1116
and 20d513416fa8c7ea463691785a6b806e7c8c6331f374e3bb54bc9c5cbf4cf474.

## Current state

Locally complete. Full `20261004T214405-8fe7b9f8` passed 2,606 tests / 24 suites,
two documented DR 0034 skips and 2,288 JSON artifacts with no mutations.
Engine observer RED: four tests/four
errors (missing progress keyword); lab-only GREEN proved exact complete report
equality, counts and exception propagation before package promotion. Promoted
observer GREEN: four tests in 0.494s, including lab/package parity and early
extinction. Application RED: six tests/six errors (missing worker). Initial
GREEN: six tests in 2.134s. Expanded ownership, close and rendering-fault coverage
passed nine tests in 3.275s. Visual first-paint RED: one failure; correction and
ten checks passed in 3.736s. Same-batch Escape/close RED: one test/two failures;
same-batch application GREEN: **11 tests in 4.398s**. No scientific algorithm changed.

The prior game regression first ran 342 tests in 48.638s with eight failures:
old observation helpers indexed intermediate paints as completed key actions.
Their timing now records the final casing per input batch, retaining separate
busy-frame evidence. Every existing `test_*` function in the three affected
files is AST-identical (`.development/t5-test-preservation.json`). The unchanged
assertions passed: 342 tests in 49.384s. Later new checks are included in the
final focused/full gates. No acceptance threshold was lowered.

Actual targeted commands:

```powershell
& .\.venv\Scripts\python.exe -B -m unittest discover -s labs/runtime_integration -p test_evolution_progress.py -v
& .\.venv\Scripts\python.exe -B -m unittest discover -s game/tests -p test_era_responsiveness.py -v
& .\.venv\Scripts\python.exe -B -m unittest discover -s game/tests -p test_era_responsiveness.py -k immediate -v
& .\.venv\Scripts\python.exe -B -m unittest discover -s game/tests -p test_era_responsiveness.py -k already_batched -v
& .\.venv\Scripts\python.exe -B -m unittest discover -s game/tests -p 'test_*.py'
```

Logs: `.development/t5-red-engine.log`, `t5-red-game.log`,
`t5-lab-seam-green.log`, `t5-green-engine.log`, `t5-green-game-batched.log`,
`t5-red-first-paint.log`, `t5-red-batched-cancel.log`,
`t5-game-regression.log` and `t5-game-regression-green.log`.

The application owns the single non-daemon thread and always joins it, even on
render/event exceptions. Pygame stays on the main thread. Real model-loading,
evaluation and saving phases plus completed-candidate counters replace the
previous frozen window; no elapsed-time percentage or simulated animation is
shown. Existing care/report/archive/replay controls resume after the request.
Queued Escape/close/F1 controls retain order; conflicting game inputs are never
replayed after the era. A first-event E paints the actual held companion first.

Final bounded observations, native build and preservation/diff review passed.
Focused verification and the single full closing gate passed.
Read the local closure below before resuming. Do not repeat completed gates.


## Final application and preservation observations

Release-candidate commands, executed sequentially for the measured workloads:

```powershell
& .\.venv\Scripts\python.exe -B labs/game_loop/measure_era_responsiveness.py --keeper .development/t5-release-measure-keeper --output .development/t5-release-measure.json
& .\.venv\Scripts\python.exe -B labs/game_loop/verify_era_responsiveness.py --template .development/t5-bounded-baseline-keeper --fixtures .development/t5-release-safety-fixtures --screenshots .development/t5-release-safety-ui --output .development/t5-release-safety.json
& .\.venv\Scripts\python.exe -B game/build_release.py --dist game/dist/t5-responsive-eras --work game/release_work/t5-responsive-eras
& .\.venv\Scripts\python.exe -B labs/game_loop/verify_keeper_loop.py --bundle game/dist/t5-responsive-eras/Mechagotchi --output .development/t5-connected.json --screenshots .development/t5-connected-ui
```

| Final case | Evaluations | Era call | Event gap | Frame gap | Help delay | Peak MiB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Normal | 96 | 8.068s | 0.043s | 0.043s | 0.037s | 66.605 |
| Earned larger | 384 | 10.087s | 0.047s | 0.047s | 0.039s | 75.609 |

Both **complete reports equal their original baseline**, including the hashes
above. The observation seam changes no scientific computation; total wall times
are machine observations, not a speedup claim. Rendered counts are monotone and
finish at the actual 96/384 evaluations. All resource bounds held.

Ten further actual source flows cover both policies: cold-load cancellation,
cancellation during evaluation, Help/Escape ordering, close during evaluation,
and close after saving starts. All checks passed. Accepted cancellation left
every saved file unchanged (model-cache files excluded); companion bytes and
policies remained exact in all flows. No worker remained alive after return.
Active evaluation cancellation stopped within **0.052s** of the request; cold
loading stopped within **4.887s**, with event/frame service continuing below
0.041s. Closing during commit saved exactly one result, cleared its journal and
preserved the companion. The 25 connected-loop checks also passed: **ten actual
native launches**, including policy refusal and recovery of an interrupted real
era, plus nine source flows through reports, archive/adoption and replay.

Visual inspection covered final progress at 192/384, cancellation during loading,
Help paging and 96/96 saving. Casing text fits the 384-pixel window, including an
E received before the first ordinary frame. Source-only screenshots remain under
`.development/t5-release-measure-*-ui/` and `.development/t5-release-safety-ui/`.
This is not native keyboard or human-usability evidence.

Instrumentation corrections are retained, not erased: preliminary memory sampled
the venv launcher; one safety reader assumed an incorrect companion JSON shape;
one screenshot path was relative to an absolute provenance root; and a PID read
caught an in-progress write. The final harness uses the validated companion
loader, resolved screenshot paths and atomic PID records. Failed/preliminary
logs and fixtures remain under the earlier `.development/t5-*` prefixes. Final
passing commands/results are named above. The first repaired measurement ran
alongside game regression; final measurements above ran sequentially without it.

Preservation audit `.development/t5-preservation.json` passed: **3,325 prior
lab/data files**, **46 other engine source files**, **20 other game modules** and
**ten prior native executables** unchanged; no unexpected existing-file changes.
With only the optional observer stripped, the lab evolution loop, package evolve
and campaign advance_era scientific functions are AST-identical to the prior
algorithm. All existing test methods in the three timing-adapted helpers remain
AST-identical. No artifact, comparator, refusal, default policy or threshold was
weakened. The native executable requires its adjacent `_internal` directory.

Native SHA256: `751a30c6e2713f7b2309f09bea01d82f9b2dfb06aceefe44a241b3d84f79622d`. Consolidated artifact:
`data/game_client/era_responsiveness_release_stage0.json` (**21 source flows / 1343 rendered frames**, plus ten native launches).

## Preserved parent-requested checkpoint

At the earlier bounded checkpoint, focused `20261004T213006-5d5985a6` had passed
at `2026-10-04T21:32:58.246471+00:00`: 784 tests (runtime lab 69, package 324,
CLI 44, game 347), 2,288 valid JSON artifacts, no skips, problems or mutations.
Its fingerprint was
`1e01abb79d0e9e230965f86d554d153b4e1ce98fa7069d7064995c5c1db72031`.
ENHANCE/POLISH transitions and the pause before full verification are retained
in `.development/t5-enhance.json`, `t5-polish.json`, `t5-checkpoint.json` and
runner history. That was a checkpoint, not closure; the subsequent explicit
request resumed the one full gate recorded below. No measured workload or
unchanged T4 gate was repeated.

## Closing concurrency review

The worker exclusively owns the era bench until the main thread joins it;
pygame and companion care remain on the main thread, with care paused. Existing
checks already cover duplicate E in the same batch and while busy, cancellation
winning before the commit lock, commit winning before cancellation, exact saved
bytes after cancellation for both policies, rendering failure cleanup, and T4
journal recovery after a real state-save failure without another evolution.
The actual source cold-load cancellation and close-during-evaluation observations
remain the workload evidence; they are not repeated.

One uncovered composition received a bounded synchronization check: closing
while loading is still blocked. Both learning policies paint twice on the main
thread, accept close/cancel before the loader returns, then join at the cooperative
boundary with all saved bytes unchanged, no accepted era and no surviving worker.
The existing implementation passes; no runtime or engine change was needed.
This is an additional regression check, not a fabricated failing RED or timing
benchmark. Preregistered in the T5 contract before execution.

```powershell
& .\.venv\Scripts\python.exe -B -m unittest discover -s game/tests -p test_era_responsiveness.py -k close_during_blocked -v
```

GREEN: one test (both policy subcases), 1.773s, no failures;
`.development/t5-close-loading.log`. The additional test/contract changes stale
the earlier focused fingerprint. The existing workflow permits the final full
pass to satisfy focused evidence too. No scientific outputs or native source
changed, so the already verified native bundle remains applicable.


## Local closure and operational pipeline

Single full run **20261004T214405-8fe7b9f8**, completed **2026-10-04T21:54:53.083627+00:00**:
**2,606 tests / 24 suites**, **two documented DR 0034 zlib skips**,
**2,288 valid JSON artifacts**; no failed suites, problems or source mutations.
The game suite includes all **348 tests**, including the 12 T5 tests. Fingerprint:
`9303296cc4fd3134a1e70e976842844e07fee28425907fff32144bd64433df85`.
Result and per-suite logs: `.development/runs/20261004T214405-8fe7b9f8/`.

Actual closing command (existing source front door and repository .venv):

```powershell
$env:PYTHONPATH = (Resolve-Path tools/mechas_cli/src).Path
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --verify full
```

The existing REVIEW -> REPAIR -> ENHANCE -> POLISH workflow executed in this
repository: measured defect and preregistered contract, retained RED/GREEN,
lab/package promotion and actual source/native evidence, then full verification.
The final full pass also satisfies current focused evidence after the additional
closing check. No competing workflow, source mirror or environment was created.
Scoped repository writes used the runtime's supported approval path; its effective
sandbox still excludes this repository from default writable roots. No security
configuration was changed, denial bypassed, or credentials/service installed.

The earlier preservation audit remains valid: this closing review changed only
the cold-close test, its contract and report before verification. The native
executable and engine/application source remained byte-identical to the measured
candidate. Final diff review and source inventory are retained in
`.development/t5-closing-preservation.json` and `.development/t5-live-handoff.json`.
The full run completed and its foreground session exited; no workload remains.

## Consolidated playable checkpoint and established remaining scope

The current locally verified alpha is
`game/dist/t5-responsive-eras/Mechagotchi/Mechagotchi.exe` with adjacent `_internal`.
Q5 reconciled launch paths and evidence. Cycle 28 provides persisted explicit
Q-table opt-in, with default adoption REFUSED and incumbent unchanged. Cycle 29
provides validated resume, backup recovery and authoritative companion checkpoint
retry/discard. Cycle 30 connects saved reports, archive/current-covenant adoption,
honestly labelled post-era replay, durable preparation and once-only completed-era
persistence. T5 keeps explicit era requests responsive, with truthful progress,
ordered Help/cancel/close and unchanged deterministic scientific results.
All accepted current contracts are locally closed; no next RED has started.

| Established scope | Concrete next design work and source |
| --- | --- |
| Original in-era recording | `game/src/mecha_game/campaign.py:636` explicitly names the missing engine recording seam. Preregister which original evaluations/frames to retain and a bounded recording/storage contract, then prove unchanged seeded results through lab/package parity. Current V replay is a newly recorded post-era life, not that original evaluation. |
| Cross-era morphological family view | Named in `research/experiment_reports/2026-07-12-repertoire-browser.md`. Specify/promote a measured family metric before building its consumer. `2026-07-27-family-ancestry.md` distinguishes descriptor-family recurrence from ancestry and supersedes the old WFC rationale; existing lineage is not a substitute. |
| Hosted sharing/signing | DR 0035 (`0035-pack-distribution-at-alpha.md`) requires a product decision with the owner. Validated file packs are the accepted alpha path; no hosted registry is implied. |
| Optional browser clip playback | The repertoire report calls this polish outside its accepted contract. It is not a blocker for the delivered connected loop. |

Offline simulation is not an unfinished task: notice 5 of
`2026-07-07-five-notices-audit.md` explicitly resolves the old metaphor as eras
requested by the Keeper and says no background simulation should exist. Retired
roadmap phases and completed contracts are not a new queue.

Measured responsiveness covers 96 and 384 evaluations, with final event/frame
gaps below 0.047s and identical complete baseline reports. The standard three-tier
maximum (48x128=6,144) and custom saves were not benchmarked. Cold-load cancellation
waited up to 4.887s while events/rendering continued; active-evaluation cancellation
stopped within 0.052s. These are bounded observations, not universal timing claims.
Native subprocess launches and source pygame events/rendering were verified;
native keyboard/human usability remain unobserved because the required runtime
is unavailable. Signing and exact-published-SHA Windows/Ubuntu Actions remain
unmet. No publication or Git mutation is part of local completion.

Exact next action: read this report and run `develop --status` with the same
source PYTHONPATH and .venv. Confirm `phase=polish`, `full_current=true`,
`local_complete=true`, `running=null`; do not repeat the unchanged passing gate.
Any later substantive development should preregister a bounded contract from
the established scope above. Commits, sync and pushes remain reserved to the user.
