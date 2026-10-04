# Recorded era review reaches the player (Cycle 30 T1)

Date: 2026-10-04. GAME track. Authoritative source:
`C:/Users/ryanf/github/_shelved/mechagotchi`, branch `phase-l-gate`,
HEAD `d1ebd033d13938f2a3732282cc6fe6b8ad8255c5`, repository Python 3.13.9.
Owner/existing changes preserved; no commit, sync or push. Runtime remains
workspace-write; scoped repository edits/builds/tests use supported escalation.

## Source-backed scope and behavior

S2 was reviewed after its single full run `20261004T173915-19f22122` passed
2,537 tests / 24 suites, two documented skips and 2,276 valid JSON artifacts,
without source mutations. Cycle 29 is archived; its gate was not repeated.

DR 0021's core loop specifies review and collection of metric-derived progress.
`_EraBench.run_era` only exposed a brief completion notice. A resumed campaign
has an era offset/founders but no current-run eras; the existing in-memory views
therefore did not expose saved reports. DR 0022 already provides history and
verbatim unlock facts. Contract `docs/development/cycle-30-era-review.md` was
registered before RED; decision DR 0069 keeps evolution/resume state untouched.

`game/src/mecha_game/era_review.py` reads public history through SQLite mode=ro
without creating a ledger, training, advancing or writing campaign state. T
opens latest; [ ] / comma / period browse; PgUp/PgDn/wheel page the established
casing. The real companion stays visible with care paused and care inputs ignored.
T/Escape closes, F1 returns to review, C opens current covenant, interactive E
opens its completed report. Bounded --ticks/--eras behavior and S2 Ctrl+S / retry /
discard stay intact. Empty/corrupt histories are explicit and preserve bytes.

Stored outcomes, coverage/QD, generation/depth, unlock values/thresholds, weather
snapshots/multipliers and founder verdicts are shown. Inherited facts are not
misattributed to a same-numbered current era. No new metric, threshold, training,
engine-storage schema or default adoption was introduced.

## Actual RED, GREEN and application observations

```powershell
& .\.venv\Scripts\python.exe -B -m unittest discover -s game/tests -p test_era_review.py -v
& .\.venv\Scripts\python.exe -B -m unittest discover -s game/tests -p 'test_*.py'
& .\.venv\Scripts\python.exe -B game/build_release.py --dist game/dist/t1-era-review --work game/release_work/t1-era-review
& .\.venv\Scripts\python.exe -B labs/game_loop/verify_era_review.py --bundle game/dist/t1-era-review/Mechagotchi --output data/game_client/era_review_release_stage2.json --screenshots .development/t1-ui-verified
$env:PYTHONPATH = (Resolve-Path tools/mechas_cli/src).Path
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --verify focused
```

Initial RED `.development/t1-red.log`: missing era_review module. Initial ten
checks passed; the whole game suite then passed 297 tests. Additional RED
`.development/t1-malformed-red.log`: malformed older report blob was accepted;
it now yields an unavailable view before navigation can crash. Visual review
caught small nonzero coverage rounded to zero; `.development/t1-coverage-red.log`
pinned that failure. The display now uses stored precision for coverage and QD.
Final targeted GREEN: 11 tests passed in 4.806 seconds (`.development/t1-green.log`).

The first observation (`era_review_release_stage0.json`) retains three failed
checks caused by the harness omitting --eras 1 from its next-era launch; this
was not a product continuation defect. Corrected stage1 passed all 13 checks,
three native launches and six source pygame flows using native-created records.
Stage2 passed all 14 checks: three actual native launches and six real source
pygame flows (28 rendered frames). Native-created histories survive restart and
append distinct era seeds; browsing/quit preserves every keeper byte, care
inputs are ignored while reading, help returns to the same era, closing advances
one care tick, C opens the current covenant, and E records a storm era then
pauses on its new report. Empty/corrupt views preserve their files. The inherited
fact filter, long-line paging and S2 failure controls have separate test pins.
Earlier observations remain unchanged.

Four final screenshots were inspected in `.development/t1-ui-verified/`:
`saved-history-01.png` shows coverage 0.000102, `saved-history-06.png` shows
actual earned depth 2 / threshold 2 and QD 9.014228 / threshold 9.0,
`next-era-02.png` shows recorded storm era 3, and `unavailable-history-01.png`
shows readable unavailable text. Wrapped text fits the 384-pixel casing.

Native candidate: `game/dist/t1-era-review/Mechagotchi/Mechagotchi.exe`, retain
adjacent `_internal`. SHA256:
`83e70ea02fc980d6144ad15232657d741a79ca8d35badd6d0b8d4fe9f1c8dd1b`.
Preservation `.development/t1-preservation.json`: 3332 existing scientific
files and 77 engine files unchanged against S2; S2 session implementation and
Q4/R2/R4/S1/S2 executable bytes remain unchanged. T1 diff reviewed; `git diff
--check` passes.

## Closing evidence and restart

Focused run `20261004T181301-70fcba95` passed at
`2026-10-04T18:14:13.762208+00:00`: **666 tests** (game 298, package 324,
CLI 44), no skips, **2,279 JSON artifacts valid**, no source mutations,
no gate problems, and `git diff --check` passed. Source fingerprint:
`6cb6bd50fda009017d38cced408700c64dfbd08c53e09a2a9d4d70e72f354d29`.

The subsequent single full run `20261004T181855-269f5dbc` passed at
`2026-10-04T11:29:30.715143-07:00`: **2,548 tests / 24 suites**, two documented
DR 0034 zlib skips, **2,279 valid JSON artifacts**, no source mutations and no
problems. The fingerprint is unchanged from the focused pass. Exact command:

```powershell
$env:PYTHONPATH = (Resolve-Path tools/mechas_cli/src).Path
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --verify full
```

Additional actual source-pygame navigation observation
`.development/t1-navigation-check.py` / `.development/t1-navigation.json` passed
nine checks across five flows / 39 rendered frames: 24 real saved eras, clamped
navigation, six open/close cycles with exactly six unqueued care ticks, restart,
empty-to-first-era, T/C/E transitions and 384-pixel small windows. Three additional
screenshots were inspected. No keeper bytes changed while reading/quitting.
Covenant navigation works, but C currently puts budget controls after care status;
that observed usability issue belongs in the next archive/navigation increment.

T1 is locally complete and reviewed in POLISH, with a current full pass and no
running verification. Preservation and diff review passed. The next source-backed
gap is the F13/F17 remainder explicitly named in `repertoire.py`: B browsing
saved elite records after restart. Do not rerun unchanged T1 gates.

Native keyboard automation remains unavailable: the installed computer-use skill
requires node_repl with @oai/sky, neither exposed in this execution runtime.
No custom helper/protocol or PowerShell UI automation was substituted. Native
subprocess launches verify packaged creation/resume/continuation; actual source
pygame inputs verify interaction/rendering. Runtime scoped escalation works and
security settings are unchanged. No Git mutations occurred. Historical replay
rendering, human usability, signing and published-SHA Windows/Ubuntu CI remain
separate limitations.
