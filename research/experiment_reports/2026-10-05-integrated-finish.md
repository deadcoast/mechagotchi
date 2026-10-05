# W5 - integrated application finish

2026-10-05. Cycle 37, DR0080. Authoritative source at owner HEAD
64bea16f10c8b09639837024935ffc5a5ba1fdf9 on phase-l-gate; existing Python 3.13.9.
No agent commit, synchronization, push, source mirror or environment change.

## Source findings and delivered behavior

Actual source observations reproduced six gaps: F1/T/B/V/L exit consumed a
care tick and leaked same-batch F; help lost hatch page 3; K End I K reset the
chosen filename; covenant help mislabeled spending as weather and 5 silently
changed weather; malformed campaign state crashed C/export; lineage omitted
earlier ancestors and object-event payloads. W1/W3 closing behavior provided
the existing consistent model. The baseline artifact retains those failures.

Paused readers now consume their closing frame/batch and clear queued care.
The next ordinary frame resumes unchanged care scheduling. Help restores the
underlying page, while its own text starts at page 1. Each inbox retains its
selected filename within the session and refreshes on reopen, including safe
clamping when the file disappears. Existing stale-digest import checks remain.

Report/archive/niche/replay/lineage/covenant help is contextual. Covenant mode
still runs care, explicitly says so, and only 1-4 spends existing unlocks;
5 has no action there. Outside covenant mode, all weather keys still work.
Malformed campaign display/export/adoption loads show recoverable messages
and leave source bytes intact; no automatic repair or replacement occurs.
Lineage pages contain every recorded ancestor and mutation field, with controls
before details. No inferred ancestry or E5/niche conflation is introduced.

Visual review of the first demonstration found a long prior-era notice burying
archive controls. A further preregistered RED test reproduced it. Archive entry
now clears that stale transient notice, preserves the saved era report, and
puts Back/Help beside archive/history navigation. Fresh failure notices remain.

## RED/GREEN and test reconciliation

```powershell
& .\.venv\Scripts\python.exe -B -m unittest discover -s game/tests -p test_integrated_finish.py -v
```

Initial RED: 12 tests / 14.282s, 25 subcase failures and two errors.
First GREEN attempt: 12 / 4.937s with one diagnostic setup failure: an archive
already refuses corrupt state, so adoption had no elite to load. The test now
corrupts the fixture after a valid archive opens, exercising the intended
adoption boundary and asserting unchanged companion/state. GREEN: 12 / 5.091s.
Visual RED: 13 / 5.216s, one first-page navigation failure. Final targeted
GREEN: 13 / 5.463s. Logs remain in .development/w5-{red,green-*,visual-red}.log.

Initial focused run 20261005T142510-a91fd384 ran 897 tests: package, CLI and
game-loop passed; game failed three legacy closing-tick assertions, with no
source mutations and 2,301 valid JSON artifacts. Five existing tests total
are reconciled to the stronger pause contract: two archive checks now require
age 0 on close, help counts only its ordinary post-close frame, and report/
replay tests insert an ordinary frame before retaining their original age/
action assertions. New tests independently require byte-exact preservation
through closes and exact next-frame state without a queued feed. No scientific
test, threshold or control has been loosened.

## Connected application demonstration

```powershell
& .\.venv\Scripts\python.exe -B game/build_release.py --dist game/dist/w5-integrated-finish-release --work .development/w5-release-build-work --windowed
& .\.venv\Scripts\python.exe -B labs/game_loop/verify_integrated_finish.py --fixtures .development/w5-release-demo --screenshots .development/w5-release-ui --bundle game/dist/w5-integrated-finish-release/Mechagotchi/Mechagotchi.exe --output .development/w5-observed-release.json
```

Final result: 84 checks, 17 source flows, 239 rendered frames and four native
load/resume launches, all passed. Both policies traverse pack -> covenant ->
H -> WFC -> unchanged H, help/paging, T/B/N/V/L, live C preparation, an actual
tiny era, explicit archive adoption, O and restart. Both workers are exercised
with deliberate 150ms diagnostic delays for cancellation and window close;
all join and preserve saved data. Malformed campaign controls remain readable.

Scales 1 and 16 were rendered through the actual app; measured rows/widths
fit, and selected screenshots were inspected. Native processes separately use
normal SDL driver selection, load/resume the adopted genome and policy, and
advance exactly one tick per launch. Source key injection is not native keyboard
automation. The initial candidate/235-frame observation remains retained; the
four-frame release difference is real worker-poll timing, not changed work.

Candidate: game/dist/w5-integrated-finish-release/Mechagotchi/Mechagotchi.exe
with adjacent _internal. Its hash and source hashes are in the release artifact.
Historical generator/trace artifacts and all engine/lab scientific files remain
unchanged. Constrained remains default, R3 refuses Q-table promotion, and
existing saves are not migrated.

## Closing gates and next action

Closing gates passed as recorded below. Exact restart is
.development/w5-live-handoff.json. This bounded integrated pass found no
additional source-backed application blocker after the recorded fixes; it does
not establish human usability or maximal-scale performance. Native keyboard,
remote execution and exact-published-SHA Windows/Ubuntu CI remain unobserved.
Owner/parent controls Git publication, remote setup and single-writer handoff.

## Actual local closure

Final focused `20261005T143622-632ee1df`: **898 tests**, 2,302 valid JSON,
no source mutations. Full `20261005T143932-8940eb33` passed **2,707 tests / 24 suites**, 2 documented DR0034 zlib skips and **2302 JSON artifacts valid**, with no source mutations.

```powershell
$env:PYTHONPATH = (Resolve-Path tools/mechas_cli/src).Path
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --verify focused
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --verify full
& .\.venv\Scripts\python.exe -B .development/w5-audit.py
git diff --check
```

Preservation audit covers 4,180 baseline source files: all 2,982 prior data
files, 370 prior lab files, 77 engine files, 40 other game-test files, 25 prior
native executables and two live-save files are unchanged. W4's report/card/
decision and W1/W3/W4 standalone UI modules are exact. Only the listed W5
client, tests, registry and current guidance changed; eight new source files
carry contract/tests/harness/artifacts/card/decision/report. Full source/native
hashes match the release observations. Git diff check passes and owner HEAD
is unchanged.

Release executable SHA256: `e74eb49177642937ae3532a94ebdf5cc444dc1d7ee9b800f10f97dcb08b2c808`.
Runner closes in polish with full_current/local_complete true and running null.
The source-local handoff contains all 51 dirty-file identities and hashes;
all existing owner work remains uncommitted and preserved. No further local
UI scope is registered. Review this result before any next delegated scope;
do not repeat unchanged gates. No remote executor or published CI is claimed.
