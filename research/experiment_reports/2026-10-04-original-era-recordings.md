# Original best-elite recordings (Cycle 31 U1)

2026-10-04, phase-l-gate at d1ebd033d13938f2a3732282cc6fe6b8ad8255c5,
C:/Users/ryanf/github/_shelved/mechagotchi, existing Python 3.13.9 .venv.
T5 full 20261004T214405-8fe7b9f8 is closed/reviewed. No Git mutations.

REVIEW found the current producer records a NEW post-era life at the era seed.
The parent chose original final-best-elite only, not every archive elite.
Actual candidate seed/weather and original/final identities are necessary;
legacy seed-derived indexing and the reader's era-seed equality cannot be reused
for original evaluations. DR0022 permits artifact pointers without schema change.
Preregistered contract/DR0074 precede RED. Preserve legacy files and labels;
other selected elites must explicitly say not recorded. Original captures must
travel with T4's completed-result journal and T5's cancellation ownership.

Source-backed inspection checkpoint: `.development/original-recordings-review.json`.
Capture, journal and playback are locally complete. The actual closing gates and
restart instructions are recorded below; original failed observations remain intact.


The owner advanced HEAD externally to c12df2ab4d39dd019f65f61d4a583c6450702ed3
during registration; the existing runner captured it as U1's starting HEAD.
No Git mutation was performed by this development agent.

Engine RED: four tests/four missing-keyword errors, 0.335s
(.development/u1-red-engine.log). Lab-only GREEN before package editing:
one complete-report/capture test passed, 0.423s (.development/u1-lab-seam-green.log).
Actual commands use the same .venv:

```powershell
& .\.venv\Scripts\python.exe -B -m unittest discover -s labs/runtime_integration -p test_original_recording.py -v
& .\.venv\Scripts\python.exe -B -m unittest discover -s labs/runtime_integration -p test_original_recording.py -k test_lab_recording -v
```


Promoted engine GREEN: four tests, 0.992s, complete lab/package records equal,
exact off/None/on scientific outputs, actual-call identity and caller isolation
(.development/u1-green-engine.log). Game RED: six tests, one failure/four errors
(3.321s; pre-existing cancellation already passed). Core GREEN: six, 3.365s.
Archive playback RED: two tests/three policy-case failures, 2.280s; GREEN with
source pygame read-only navigation: eight tests, 5.196s. Logs use u1-red-game,
u1-green-game-core, u1-red-playback, u1-green-game-playback prefixes.

First full game regression: 356 tests, 56.156s, two failures
(.development/u1-game-regression.log). Both asserted the superseded current-run
post-era producer semantics: one expected an extra demonstration call; one
refused playback after current parameters changed. U1 now requires zero such
calls and playback of already recorded original data despite later parameter
changes. The two tests are updated to assert those stronger original-footage
contracts. The tampered-file refusal, hash/read-only checks and every scientific
threshold remain. This is an intentional contract change, not an acceptance
threshold relaxation. No other regression appeared in that run.


The added fault suite first ran ten tests in 7.303s with one Windows temporary
fixture cleanup error: the new tamper test used sqlite3's transaction context
without closing its connection. This was test-harness resource ownership, not
a game save defect; it now uses contextlib.closing. Original log retained at
.development/u1-green-game-faults.log. No saved artifact or threshold changed.


Corrected fault tests: ten passed in 7.455s. A repeated game regression already
in flight still used the old test-module connection cleanup and reported that
one error (358 tests, 58.157s); do not call its green-named log a pass. Final
focused/full gates will exercise the fixed source. Engine weather/tie/call-count
checks passed six tests in 0.800s. No extra generation/scoring/final-episode call
was observed, and complete lab/package original capture records match.

Initial native/source demonstration: 32 checks, ten native launches, 13 source
flows / 138 rendered frames passed (.development/u1-connected.json). Visual
inspection saw the original wound timeline and the other-elite 'not recorded'
notice fitting the 384-pixel casing. This is source rendering, not native keyboard.

Normal/larger observations (.development/u1-measure.json), 90s/512MiB bounds:
96/384 actual evaluations; era calls 7.881s/9.848s, peak worker 65.891/76.316MiB,
maximum event/frame gap 0.045361s/0.041137s, Help 0.033650s/0.028046s. Each original
recording has 37 frames, 36,928/36,245 encoded bytes. Both complete report hashes
match the preserved T5 baseline exactly. These machine observations are not
speedup or maximum-scale claims. The measurement preceded only a journal-format
guard and legacy-recorder docstring correction; capture/evaluation is unchanged.

Recovery review found old v1 clients could ignore new pending recording fields.
Additional RED (one failure, 0.707s) pins a recording-bearing v2 journal. GREEN:
11 tests, 7.841s (.development/u1-green-versioned-journal.log). U1 still reads v1
journals and clears back to v1 idle preparation only after completion. The final
native verification adds preserved T5 executable refusal followed by U1 recovery.


Final application observations passed: 33 connected checks / eleven native
launches / thirteen source flows, including read-only refusal by the preserved
T5 executable and exact U1 completion of the versioned pending recording.
Ten additional bounded source safety flows passed on incumbent/qtable: accepted
cancel preserves all saved bytes; close during commit finishes exactly one
recorded result; help ordering, paused care, policy and joined cleanup survive.
Cold-load cancellation stopped within 4.832s while events/rendering continued;
active-evaluation cancellation within 0.038s. No resource limit was hit.
Raw evidence: .development/u1-connected-final.json and .development/u1-safety.json.

Immutable observations: `data/game_client/original_recordings_release_stage0.json`
(25 source flows / 1,365 rendered frames plus eleven native launches), with the
actual 37-frame sample `data/game_client/original_evaluation_sample_stage0.json`.
Final native SHA256: cbefbc232231229be5e4dde58864ee62d53f4ed2f56516c76c4fee839297e41c.
The initial candidate remains at game/dist/u1-original-recordings-stage0;
current candidate is game/dist/u1-original-recordings/Mechagotchi/Mechagotchi.exe,
with adjacent _internal. No native keyboard/human-usability claim.

Preservation .development/u1-preservation.json passed: 3,330 prior lab/data files,
46 other engine source files, 18 other game modules and twelve retained prior
native builds unchanged, including the U1 initial candidate. The lab loop,
package evolve and campaign advance_era are AST-identical to baseline after
removing only original-recording observation. No unexpected existing changes;
git diff --check passed. The original T5 native and data artifacts remain intact.

Actual observation and preservation commands (same repository .venv):

```powershell
& .\.venv\Scripts\python.exe -B game/build_release.py --dist game/dist/u1-original-recordings --work game/release_work/u1-original-recordings-final
& .\.venv\Scripts\python.exe -B labs/game_loop/verify_keeper_loop.py --bundle game/dist/u1-original-recordings/Mechagotchi --legacy-bundle game/dist/t5-responsive-eras/Mechagotchi --output .development/u1-connected-final.json --screenshots .development/u1-connected-final-ui
& .\.venv\Scripts\python.exe -B labs/game_loop/measure_era_responsiveness.py --keeper .development/u1-measure-keeper --output .development/u1-measure.json
& .\.venv\Scripts\python.exe -B labs/game_loop/verify_era_responsiveness.py --template .development/t5-bounded-baseline-keeper --fixtures .development/u1-safety-fixtures --screenshots .development/u1-safety-ui --output .development/u1-safety.json
& .\.venv\Scripts\python.exe -B .development/u1-audit.py
```

Focused run **20261004T224313-a113b1ed** passed **895 tests** across the five
selected suites, including the complete 360-test game suite and the durable
unavailable-status case. No gate problems or source mutations occurred.

## Local closure and operational pipeline

Single full run **20261004T224746-6ccc82b0**, completed
**2026-10-04T22:57:42.469646+00:00**: **2,624 tests / 24 suites**,
**two documented DR 0034 zlib skips**, **2,290 valid JSON artifacts**.
All suites passed; no problems or source mutations. The complete game suite
passed all **360 tests**. The focused and full source fingerprint is
`f3a1fdb26b8e2fdb421e332c1ffaa2d57f8f6e3a2d06ea77a5d40df1b8d1ef2f`.
Per-suite logs and exact commands are in
`.development/runs/20261004T224746-6ccc82b0/` and `.development/u1-full.json`.

Actual canonical closing commands:

```powershell
$env:PYTHONPATH = (Resolve-Path tools/mechas_cli/src).Path
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --verify focused
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --verify full
```

The targeted game RED/GREEN logs above cover the evolving
`test_original_recordings.py` module. Its reproducible focused command is:

```powershell
& .\.venv\Scripts\python.exe -B -m unittest discover -s game/tests -p test_original_recordings.py -v
```

The existing REVIEW -> REPAIR -> ENHANCE -> POLISH workflow executed in the
requested repository and its original .venv. Registration preceded RED;
lab-first capture was promoted after parity, source/native observations and
preservation review passed, then current focused evidence admitted ENHANCE and
POLISH and the full sweep closed the slice. No source mirror, replacement
environment, service or competing workflow was created. Scoped writes used the
runtime's supported approval path: its effective workspace-write sandbox still
excludes this repository from default writable roots. No security configuration
was changed and no approval denial was bypassed.

Closure updates only narrative reports, queue and launch guides outside the
verified executable fingerprint. The source, tests, contracts, native build and
immutable observation artifacts remain the tested versions. The stage-0 metric
artifact deliberately retains its observation-time full-gate-pending verdict;
this full result is the later closing evidence, not a rewrite of that snapshot.
Restart context: `.development/u1-live-handoff.json`; runner closure:
`.development/u1-closed.json`. No active workload or Git mutation remains.

## Playable checkpoint and remaining scope

Current local native build:
`game/dist/u1-original-recordings/Mechagotchi/Mechagotchi.exe`, with adjacent
`_internal`. New eras record the original final-best evaluation; V from care/T
or the matching B selection reads saved footage only. Other elites and missing
history explicitly say not recorded. Actual candidate seed, generation, weather,
covenant and original/final identities are retained. Legacy post-era footage
keeps its provenance. Interrupted completion retains the actual result and
recording; accepted pre-commit cancellation preserves saved bytes.

Normal/earned-larger observations cover 96/384 evaluations, not the 6,144
standard maximum or arbitrary custom saves. Retention is bounded per era, not
across a campaign's lifetime. Native SDL-dummy launches and real source pygame
navigation/rendering were observed; native keyboard/human usability remain
unobserved because the required runtime is unavailable. Exact-published-SHA
Windows and Ubuntu Actions and hosted signing remain unmet. Incumbent/default
policy, R3's adoption refusal and old saves remain unchanged.

Original recording is now completed scope. The next independent product scope
is the cross-era morphological-family consumer: specify/promote its measured
metric from `2026-07-12-repertoire-browser.md` and
`2026-07-27-family-ancestry.md` before implementation. Descriptor families and
ancestry are distinct. Hosted sharing/signing still requires DR 0035's owner
product decision; per-elite browser clip playback remains optional polish.
Offline simulation was explicitly rejected by notice 5 of
`2026-07-07-five-notices-audit.md`; it is not unfinished scope. No next RED starts.

Exact next action: read this report, then run the same source front door with
`develop --status`. Confirm `phase=polish`, `full_current=true`,
`local_complete=true`, `running=null`; do not repeat an unchanged passing gate.
Commits, sync and pushes remain reserved to the user.
