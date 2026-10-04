# Saved creatures reach the returning Keeper (Cycle 30 T2)

Date: 2026-10-04. GAME/SHARED track. Authoritative repository:
`C:/Users/ryanf/github/_shelved/mechagotchi`, `phase-l-gate`,
HEAD `d1ebd033d13938f2a3732282cc6fe6b8ad8255c5`, repository Python 3.13.9.
Existing/owner changes remain; no Git mutations or new environment.

## Why this increment and what changed

T1 closed once at full run `20261004T181855-269f5dbc`: 2,548 tests / 24 suites,
two documented skips, 2,279 valid JSON artifacts and no mutations. Its expanded
navigation observation passed nine checks with 24 real eras. The source-backed
next gap was explicit in repertoire.py: ledger browsing promised at F17 still
required current-run eras. DR 0021 Review/Collect and DR 0022 stored elite blobs
already define the product behavior and data authority. Contract
`docs/development/cycle-30-saved-archive.md` preceded T2 RED; decision DR 0070.

The lab/package storage surface adds load_era_elites, returning complete stored
blobs plus niche keys in deterministic order. It changes no schema, founder pool,
engine math, threshold or saved record. Read-only browsing never trains, runs an
era or hydrates the live campaign's eras. Historical bodies render under the
recorded era covenant; current-covenant adoption remains the engine's decision.

B opens saved archives after restart or from a selected T report. Comma/period
select creatures, brackets select eras, paging wraps details, and care pauses
with care inputs ignored. Help retains selection. B/Escape goes back; T opens
the selected report. A explicitly adopts through the current gate and S2
checkpoints, keeps the chosen policy and returns to care. Refusal retains the
current pet. Empty/corrupt views remain explicit; unavailable records cannot
launch planning actions. An empty history can run its first era.

Actual T1 screenshots showed C controls below care status; the existing budget
and spending keys now appear first. Existing covenant-mode timing is unchanged.
No replay reconstruction, new simulation mechanic or default-policy adoption.

## Actual RED/GREEN and observations

```powershell
& .\.venv\Scripts\python.exe -B -m unittest discover -s labs/game_loop -p test_saved_elite_query.py -v
& .\.venv\Scripts\python.exe -B -m unittest discover -s labs/game_loop -p test_package_storage_parity.py -v
& .\.venv\Scripts\python.exe -B -m unittest discover -s game/tests -p test_saved_archive.py -v
& .\.venv\Scripts\python.exe -B -m unittest discover -s game/tests -p 'test_*.py'
& .\.venv\Scripts\python.exe -B game/build_release.py --dist game/dist/t2-saved-archive --work game/release_work/t2-saved-archive
& .\.venv\Scripts\python.exe -B labs/game_loop/verify_saved_archive.py --bundle game/dist/t2-saved-archive/Mechagotchi --output data/game_client/saved_archive_release_stage2.json --screenshots .development/t2-ui-final
```

Storage RED: four tests / eight missing-API subtest errors. Lab implementation
passed its four cases while the package still failed four; only then was the
exact query ported. Four query tests and both existing source/behavior parity
pins passed. They prove full record equality/order/scope, empty unknown queries,
blob authority despite corrupted scalar columns, and read-only byte preservation.

Game RED: ten tests, six failures/four errors from absent saved loading and
inaccessible paused/navigation/adoption behavior. Initial GREEN ten passed;
whole game suite passed 308. An additional corruption-action RED then reproduced
a TypeError when E attempted to resume malformed elite data. The unavailable
view now blocks C/E while an empty view can still start its first era. The
expanded targeted GREEN passed 11 tests in 4.343 seconds; focused evidence follows below.

Initial observation `data/game_client/saved_archive_release_stage0.json` passed
21 checks, four native launches and twelve source pygame flows (52 frames),
including both policies, 24-era histories, adoption/refusal and subsequent eras.
That observation is preserved. Stage1 passed 22 checks including unavailable
actions and empty-to-first-era. Final stage2 also passed **22 checks**, **four
native launches**, **13 actual source pygame flows / 56 rendered frames**, on
the final candidate after removing inapplicable controls from empty/error views.
Each policy has 24 native-created eras, read-only browse/quit, help/report return,
selected adoption, current-covenant refusal and exact append to era 24 without
changing the first 24 records or advancing care. Prior stage artifacts remain.

Screenshots under `.development/t2-ui-final/` show real stored bodies and the
adopted companion, C budget/actions on page one, and concise empty/corrupt views
with only applicable controls. Small windows are 384 pixels wide; long histories
were real engine results, not fabricated report rows.

Native candidate: `game/dist/t2-saved-archive/Mechagotchi/Mechagotchi.exe`, retain
adjacent `_internal`. SHA256:
`34689304d1d0d519d808eca355d9e45fea17365ec12501697ebe493b0a5e91ad`.
Preservation `.development/t2-preservation.json` checks 3,336 prior scientific
files and 77 engine files against T1. Only the lab query and two package
query/export files changed in those sets. Removing those exact additions
reconstructs their prior bytes; original LF formats were restored with identical
compiled code. Every prior data artifact, engine math/control, S2 session file
and all six older native executables remain unchanged. Diff reviewed and
`git diff --check` passed.

## Checkpoint, preservation and limits

Focused run `20261004T185147-cb5b0431` passed at
`2026-10-04T11:53:28.041944-07:00`: **769 tests** (lab game_loop 92,
package 324, CLI 44, game 309), no skips, **2,282 valid JSON artifacts**, no
source mutations and no gate problems. Source fingerprint:
`81c671dfe6599cca4b344a629a601236cce58d46d6eb562f6ebf89930255a679`.
Exact command:

```powershell
$env:PYTHONPATH = (Resolve-Path tools/mechas_cli/src).Path
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --verify focused
```

Full run `20261004T185738-2f3b4168` passed at
`2026-10-04T12:09:31.759042-07:00`: **2,563 tests / 24 suites**, two
previously documented DR 0034 zlib skips, **2,282 valid JSON artifacts**, no
failures, gate problems or source mutations. The source fingerprint matches
the focused pass above. Actual command: `develop --verify full` through the
same source invocation. T2 is locally complete and reviewed; canonical status
and `.development/t2-closed.json` preserve its full-current/polish closure.

Additional adoption review `.development/t2-adoption-review.json` passed all
**12 checks / six native launches / six source pygame flows**. Both policies
survive repeated and clamped selections, explicit repeated adoption, native
save/restart and conflicting-policy refusal. An invalid private-fixture grid
is refused without changing the covenant. Covenant/campaign bytes and ledger
remain unchanged by adoption. Each repeated explicit adoption begins a new
life as the existing mechanic specifies. No covenant was weakened for admission.

T3's next substantive scope is the previously documented saved replay consumer:
reopen an existing recording after restart/from a selected era, preserve its
provenance, and state missing history without fabricating or rerunning it.

Native keyboard interaction remains unavailable. The installed computer-use
SKILL.md requires node_repl/@oai/sky, which tool discovery did not expose; no
custom helper, alternate protocol or PowerShell UI automation was used. Actual
native subprocess launches and actual source pygame input/render observations
are separate claims. Human usability, signing, historical replay rendering and
published-SHA Windows/Ubuntu CI remain outside this checkpoint. Runtime scoped
escalation works; no security settings or user save homes were changed.
