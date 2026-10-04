# Keeper preparation and era completion (Cycle 30 T4)

2026-10-04. Authoritative repo `C:\Users\ryanf\github\_shelved\mechagotchi`,
branch `phase-l-gate`, HEAD `d1ebd033d13938f2a3732282cc6fe6b8ad8255c5`.
Same `.venv/Scripts/python.exe` (3.13.9); existing changes preserved; no Git.
T3 full `20261004T192757-866fdf0f` was reviewed before this bounded milestone.

## Current code-and-queue handoff

**Locally complete.** Canonical runner: `t4-durable-era-plan`, POLISH.
The existing full run `20261004T202052-aaa63dd1` completed at
`2026-10-04T20:31:54.994205+00:00`: **2,590 tests / 24 suites**, two documented
DR 0034 zlib skips, **2,286 valid JSON artifacts**, no failures or source
mutations. It was resumed and inspected, not restarted. Source fingerprint:
`39c1da540cd5f8461bc76a6aab70f71f83e2f2b4cb60510ed84a8ef42c4be842`.

Final focused run `20261004T201806-79255b52` passed **704 tests**
(package 324, CLI 44, game 336) and 2,286 JSON artifacts at
`2026-10-04T20:19:32.992532+00:00`, no skips, problems or mutations.
REVIEW, REPAIR, ENHANCE and POLISH ran through the existing source CLI.
Visual, preservation and diff review are complete. Closure is retained in
`.development/t4-closed.json`; the full summary and result remain under
`.development/runs/20261004T202052-aaa63dd1/`. No following scope is started.

- Contract: `docs/development/cycle-30-durable-era-plan.md`; checked T4 live queue.
- `game/src/mecha_game/era_plan.py`: atomic explicit weather/staging, dedup and
  conflicting-id refusal, public genome validation, reversible unstaging, sealed
  completed-era journal, conflict checks and idempotent persistence completion.
- `game/src/mecha_game/app.py`: prepared E execution from a copy; retry retains
  completed results; successful covenant changes persist immediately. R/W and
  weather also work from paused reports. Backspace unstages source-preserving
  copies. Current preparation appears in existing care/report/covenant casing.
- `game/src/mecha_game/campaign.py`: shared state_payload, atomic/no-op state
  checkpoints through the unchanged S2 file writer, persisted base_parameters.
  Newly written state cannot compound spent budget caps on restart. Legacy
  states lacking base_parameters retain their established load behavior; no
  historical base values are guessed or migrated.
- `era_review.py` shows exact admitted founder IDs alongside prior verbatim
  rejections; `footer.py` explains the existing-loop controls.
- `game/tests/test_era_plan.py`: 14 tests including four persistence fault points,
  unbroken/resumed engine-result equality, next seed continuity, both policies,
  paused report preparation, archive/adoption and replay, invalid/duplicate
  staging and state conflicts. No engine/math/default-policy changes.

## Why this milestone

DR 0021's session is Review -> Covenant -> Contribute -> Weather -> Run ->
Collect; DR 0022/F17 preserve its state. The actual T3 app staged the cared-for
genome, selected storm and saved/quit, but after restart ran calm without that
genome. Preserve `data/game_client/keeper_loop_review_stage0.json`; it contains
one bounded native create and three actual source pygame observations before
repair. Its palette-spend attempt was refused (no unspent palette), so that
observation makes no successful-spend claim. Source and RED separately expose
successful covenant spending remaining only in memory until another era.

The change joins existing decisions and outcomes, with no new panel, simulated
mechanic or automated evolution. A persisted journal contains an actual completed
engine result. Only explicit E runs or finishes saving; reading never runs it.
Compatibility still receives the engine's real admission/refusal. No default
adoption of the experimental Q-table occurred.

## Actual RED/GREEN to this checkpoint

```powershell
& .\.venv\Scripts\python.exe -B -m unittest discover -s game/tests -p test_era_plan.py -v
& .\.venv\Scripts\python.exe -B -m unittest discover -s game/tests -p 'test_*.py'
```

Initial and expanded RED: 8 tests, three failures/nine errors
(`.development/t4-red.log`, `t4-red-expanded.log`). Initial GREEN: 8 tests in
4.646s. Added preregistered unstaging/malformed-genome RED: 10 tests, one failure
and one error (`t4-red-unstage.log`). Expanded GREEN: 10 tests in 4.987s.
The existing game suite passed **332 tests in 44.367s** (`t4-game.log`).
No acceptance threshold or existing test was weakened.

## Application and preservation evidence

Expanded targeted GREEN passed 12 tests in 5.368s. Actual stage0 application
checks passed, but visual inspection found metrics below the first page and
prompts for disabled preparation during recovery. Added preregistered RED:
14 tests, two failures (`t4-red-visual.log`). Final GREEN: **14 tests in 6.355s**
(`t4-green-visual.log`). Existing assertions remain intact.

Actual build/observation commands (stage0 was run before the visual polish;
its artifact and entire native bundle are retained):

```powershell
& .\.venv\Scripts\python.exe -B game/build_release.py --dist game/dist/t4-keeper-loop --work game/release_work/t4-keeper-loop
& .\.venv\Scripts\python.exe -B labs/game_loop/verify_keeper_loop.py --bundle game/dist/t4-keeper-loop/Mechagotchi --output data/game_client/keeper_loop_release_stage0.json --screenshots .development/t4-ui
& .\.venv\Scripts\python.exe -B labs/game_loop/verify_keeper_loop.py --bundle game/dist/t4-keeper-loop/Mechagotchi --output data/game_client/keeper_loop_release_stage1.json --screenshots .development/t4-ui-final
```

Final stage1 passed **25 checks / ten native launches / nine actual source pygame
flows / 71 rendered frames**, using `--era-scale tiny`. Native subprocesses used SDL dummy video/audio;
source events exercised actual game/render logic. Both policies preserve storm,
one staged cared-for genome despite repeated R, and population spending (6 -> 12
under the real earned cap, base remains 6). Native resume keeps them. The next
source era admits that genome, exposes the exact verdict, records an honestly
labelled post-era life, browses the archive and adopts an elite with policy intact.
That adopted genome is staged for a later native era. Prior reports stay exact,
read-only reviews preserve keeper bytes, unstaging preserves source creatures,
and incompatible-policy native launches return 2 without writes.

A real computed-era/state-save interruption was observed with a private-fixture
file lock. Its journal and staged inputs survive exit. A native restart with one
requested era finishes that exact saved result; it produces no additional era.
Unit instrumentation separately proves no second evolve call at each journal,
ledger, state or final-clear fault. Simulation failures leave preparation intact.
Conflicting saved state/ledger and corrupt journals are refused without writes.

Inspected final 384-pixel screenshots under `.development/t4-ui-final/` show
outcome/niches/QD on page one, the persisted storm/count, and recovery's E retry
without unavailable preparation prompts. This is source rendering evidence;
it is not native keyboard or human-usability evidence.

Locally verified build `game/dist/t4-keeper-loop/Mechagotchi/Mechagotchi.exe`, retain
adjacent `_internal`. SHA256:
`30224d39b3ea83af356362e4a09fc6c42bcb834ddc65c99ab73522d074097de2`.
The initial candidate was preserved by a checked same-repository move to
`game/dist/t4-keeper-loop-stage0/Mechagotchi/Mechagotchi.exe`; its hash remains
`3102b1aed370cc657960fcac400672abafb8f2e6b8ff6b38b36eee14ef79884d`.

`.development/t4-preservation.json` verifies **3,324 prior lab/data files**, **77
engine files**, six prior game-core modules and eight preceding native builds
unchanged, plus the initial T4 candidate. The campaign's **15 non-persistence
methods are AST-identical** to its verified prior source; load_state only adds
optional base_parameters restoration. Persistence changes are the shared state
payload and atomic/idempotent file writes through the unchanged S2 writer.
No existing scientific artifact, refusal, comparator, engine function or default
policy changed. Diff reviewed; `git diff --check` passed (existing Git newline
notices are informational). Current HEAD remains d1ebd033, with no Git mutations.

## Closing commands and restart

Actual final workflow commands, after the targeted and application commands above:

```powershell
$env:PYTHONPATH = (Resolve-Path tools/mechas_cli/src).Path
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --verify focused
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --advance enhance --note "Final T4 focused 20261004T201806-79255b52 passed 704 tests and 2286 JSON with no mutations. Fourteen targeted pins and 25 application checks/ten native launches/nine source flows passed; final visual and preservation review complete."
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --advance polish --note "Integrated Keeper milestone source/evidence finalized. 3324 prior lab/data files, 77 engine files, six core modules and nine retained builds unchanged; 15 campaign calculation methods identical. Run the one full closing gate. No Git or further scope."
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --verify full
```

The original transition records are in
`.development/t4-enhance.json`, `.development/t4-polish.json` and runner state.
To resume, read the report and `sunsetted/TODO.md`, then run only the read-only
source command `develop --status` with the same PYTHONPATH/interpreter. Confirm
`phase=polish`, `full_current=true`, `local_complete=true`, `running=null`.
Do not repeat unchanged passing gates or start a replacement workflow.

Native keyboard remains unavailable (required node_repl/@oai/sky is unexposed);
do not investigate alternate control routes. Native subprocess and source pygame
observations are distinct. Era computation remains synchronous. Old saves without
recorded base_parameters retain their established legacy interpretation. Human
usability, signing and published-SHA Windows/Ubuntu CI remain separate. No new
feature list, source mirror, environment, background service or Git mutation.

## Consolidated product checkpoint and established remainder review

Q5's source/CLI/native launch reconciliation is closed and reviewed
(`2026-10-04-phase-q-gate.md`); Cycle 28 retains an explicit experimental
Q-table option and the refused default adoption; Cycle 29 protects companion
resume and interrupted checkpoints. Cycle 30 now connects saved reports,
archive/adoption, recorded replay and durable preparation/completion. The four
accepted Cycle 30 contracts are met. This does not declare the entire research
or product vision finished, and it does not turn historical future work into
new accepted tasks.

Reviewed the live queue, DR 0021/0022/0033, the retired gap analysis and the
Phase F/G remainder reports against current source. The concrete distinctions:

| Documented item | Current disposition and source |
| --- | --- |
| Saved archive, replay and spent covenant continuity | Implemented and verified through T2-T4. The actual connected tiny-era observations above cover restart, admission, adoption, replay and later contribution. |
| Original in-era evaluation recordings | Still absent. `game/src/mecha_game/campaign.py:634` explicitly records a new post-era elite life; T3 never relabels it as the original evaluation. A future engine contract must choose which evaluation histories to retain and bound recording cost before promotion. This is a genuine engine extension, not a missing replay-view control. |
| Cross-era morphological family view | Named future rung in `2026-07-12-repertoire-browser.md`, separate from saved archive browsing. Current `repertoire.py` shows recorded niches/elites and `lineage.py` shows life/ancestry records. The family definitions remain research; `2026-07-27-family-ancestry.md` distinguishes morphology from ancestry and supersedes the old WFC rationale. A consumer must use a promoted, specified metric rather than recompute lab science in the UI. |
| Offline simulation | Not an unfinished requirement. `2026-07-07-five-notices-audit.md`, notice 5, explicitly resolves DR 0021's metaphor: eras run when the Keeper requests them; no background simulation should run. Current explicit E/CLI-era behavior matches that disposition. |
| Per-elite clip playback | The repertoire report explicitly calls it optional polish, outside its contract. Idle bodies are the present browser behavior; it does not block the delivered connected loop. |
| Hosted community and signing | DR 0035 explicitly defers registry/hosting to a product decision with the owner; files and validation gates are the accepted alpha delivery. No hosting or Git work was undertaken. |

The July MVP roadmap is retired and its named phases are historically closed;
its checked tasks are not a new backlog. No additional acceptance-defined,
high-impact application item remains in the current queue. No speculative next
panel or process phase was added. No design decision blocks the delivered loop.
An original-evaluation replay or family consumer would need a new bounded engine
contract; hosted distribution needs the explicit DR 0035 owner decision.

Scale and observation limits remain material: the T4 connected-loop evidence is
**tiny-era** evidence. Era computation still runs synchronously in the foreground;
these checks do not establish responsive interaction during large-era evaluation.
Native keyboard and human usability remain unobserved here. Missing historical
recordings and unknown old budget bases remain explicit rather than fabricated.
No published-SHA Windows/Ubuntu CI result is claimed.

Exact final dirty paths and SHA256 values are retained in the ignored
`.development/t4-product-handoff.json` and `.development/t4-final-dirty.txt`.
These include pre-existing/external changes, not just this milestone's work.
Source identity remains `phase-l-gate` at `d1ebd033d13938f2a3732282cc6fe6b8ad8255c5`.
No files were staged, committed, synchronized or pushed. The exact next action
is to read this checkpoint and `develop --status`; a future active development
request should name or preregister a substantive contract from the remainders
above, without replaying completed gates or installing unattended execution.
