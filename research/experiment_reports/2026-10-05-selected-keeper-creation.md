# Cycle 38 X3: selected Keeper creation and exchange

Started 2026-10-05; locally closed 2026-10-06 UTC after the full closing gates.
Repository C:\Users\ryanf\github\_shelved\mechagotchi, branch phase-l-gate,
owner HEAD d4b4337d0dacbdfa816d990297c03a5da2d0cdca. Existing Python 3.13.9.
No Git mutations. Preregistered contract:
docs/development/cycle-38-selected-keeper-creation.md, runner slice
x3-selected-keeper-creation. Baseline .development/x3/baseline.json accounts for
4220 source files and verifies all 57 incoming dirty identities.

## Acceptance review, including negative findings

The prior X1/X2 full run 20261005T230645-abc7203e remains a valid historical
2778-test result; independent criterion review found five untested gaps:
pending successor completion accepted missing predecessor eras; explicit --new
could discard backup-only history; direct A omitted a known era index; layer
edits dropped accepted extra siblings; and localStorage drafts were stranded
after an ordinary different-port server restart. Maps, actual source hashes,
API/browser probes and screenshots are retained under .development/x3/review-x1
and review-x2. Earlier closure prose is superseded for these five criteria.

Repairs preserve valid backup histories and exact old bytes, label missing
intervals, carry known direct-A provenance, validate predecessor history before
completion writes, preserve full layers, and persist bounded per-context server
drafts separately from validated engine output. Undo/local browser recovery remain.

## Implemented consumer and authorities

Explicit --keeper-dir selects a native Keeper; absent selection remains the
visibly separate browser lab. Native J checkpoints and opens that Keeper's creator
while care pauses. J/Escape returns; the owned loopback server closes with the
game. Native W gathers only that Keeper's releases. CLI --packs opens composition.

The read-only adapter validates companion/state and a coherent SQLite transaction,
then rechecks JSON identities. It displays the actual base covenant/earned budget
and recorded histories; no training, care advance or reconstruction occurs.
Context revision and per-file/source revision checks serve different purposes.
Native write requests require fresh context pins; legacy browser care/session
mutations remain separate. Release saves the exact selected document plus its
explicit ecosystem transform and full authoring sidecar. It is staging, not
admission. Subsequent actual engine verdicts and unique full founder source records
survive journal retry and restart using the existing table. Ambiguous duplicate
IDs stay in engine order and do not acquire invented source mappings.

Named mechagotchi_pack_v1 composition/export/import keeps exact profiles/genomes
and declared provenance. Reviewed document digests are distinct from original
file-byte digests. Imports preserve conflicts, retain source receipts and show
independent item outcomes. No signing, registry, hosting or receiving-Keeper
identity rebinding is introduced.

## Integration findings and repairs

Independent main review found browser-launch/startup cleanup holes, repeated-J
care leakage, and interrupted first-creator genesis with no recoverable pair.
The native/CLI controls now ignore repeated close/open keys, supervise browser
launch errors and terminate/wait for owned startup failures. New campaign creation
uses the existing paired checkpoint authority before either primary is installed;
unpublished failure cleanup is limited to this attempt's verified owned artifacts.
Existing evidence is never initialization permission.

Actual native creator startup exposed eager unused 8x8 model training:
8.0756387 seconds before, 0.0171300 seconds after native-only lazy preparation.
The deferred full-corpus 8x8 models compare exactly with the unchanged browser-lab
arm. This is a bounded startup observation, not a broad performance claim.

Independent pack review passed 46 focused tests and additional overlapping-import,
post-scan target-appearance and exact Unicode source receipt probes. It found
Windows-reserved download basenames; exports now use a fixed safe prefix without
changing pack identities. Browser/API integration also found top-level refused
imports returned a success HTTP status and composition incorrectly applied its
source Keeper's destination conflicts. Those adapter corrections passed the final API/browser demonstration and full sweep.

## Actual verification and current gates

Focused RED/GREEN commands and unmodified output are in:
- .development/x3/campaign/result.json and initialization evidence.
- .development/x3/packs/README.md and handoff.json.
- .development/x3/backend/result.json and notes.md.
- .development/x3/frontend (JavaScript and real browser evidence).
- .development/x3/main (entry, CLI, actual owned bridge and integration logs).

The main test commands use .venv/Scripts/python.exe -B -m unittest discover
with -s game/tests -p test_selected_keeper_entry.py, -p test_creator_bridge.py,
or -s tools/mechas_cli/tests -p test_workshop_context.py. Existing CLI surface,
campaign, EraPlan, pack and Workshop controls are retained.
Initial direct-A test setup errors (saved campaign instead of a current in-memory
era, then wrong state key) are retained in logs; the independent pre-edit actual
direct-A probe supplied the correct reproduction under both policies.
No failed/inconclusive evidence is relabeled as a pass.

The first integrated demonstration passed 27/29 checks. One harness fixture
mistakenly expected covenant rejection for an 8x8 creature that was covenant-aligned
but incompatible with the era's 16x16 cohort; actual engine refusal was correct.
The corrected fixture uses an actually disallowed palette too. The other failure
exposed the refused-import HTTP/UI outcome defect above. Initial evidence remains
at .development/x3/demo-01/result.json.

Full closing run `20261006T002342-6c33bff8` passed **2,842 tests / 24 suites**, 2 documented DR0034 skips, 2304 JSON artifacts valid.
Exact command: `.venv/Scripts/python.exe -B -m mechas_cli.app develop --verify full`,
with `PYTHONPATH=tools/mechas_cli/src` and UTF-8 output. Logs and inventory are in
`.development/runs/20261006T002342-6c33bff8/`. The runner observed zero source mutations,
no failed suites/artifact checks, and a clean `git diff --check`. Its current full
pass supports the ENHANCE and POLISH transitions without a duplicate unchanged run.

The first closing full run `20261006T000649-c30cd634` failed one of 527 game
tests: niche-history adoption. An isolated reproduction captured the explicit
refusal `Recorded predecessor is not extinct; succession is unavailable.` Its
synthetic fixture linked older/middle/current campaigns while leaving both
predecessors active. The correction marks those archived predecessors extinct
before making the next link, keeping deterministic era inputs and every adoption,
covenant-refusal and byte-preservation assertion unchanged. No runtime validator
or acceptance threshold was weakened. The failed full and isolated RED, followed
by focused GREEN, remain in the run directory and `.development/x3/review-main/`.

The final application artifact `data/game_client/selected_keeper_creation_stage0.json`
records **33/33 checks**, three source-event flows and two actual native SDL
launch/resume processes. The release is staged, then genuinely admitted or refused
by an era in a second Keeper; the chosen covenant, full submitted genomes, actual
verdicts and recorded elites survive restart. The other Keeper stays unchanged.
This demonstrates saved genetic declarations and actual admissions, not a claim
that every final elite descended from the edited release. Source demo evidence is
`.development/x3/demo-02/result.json`; the native process log/result is under main/.

The final real-browser harness passed **11/11 flows**, with seven screenshots and
no page exceptions, including live/replay/offspring previews, a real file download,
and import of that download into a second selected Keeper. Two additional initial
disconnect/reconnect flows passed with zero blank server writes. Commands:
`node workshop/tests/context_browser_check.js` and
`node workshop/tests/context_browser_check.js .development/x3/frontend/startup-reconnect --startup-only`.
The final browser result is `.development/x3/frontend/browser-20261006000235024/result.json`;
startup evidence is `.development/x3/frontend/startup-reconnect/result.json`.
The actual exported pack is retained byte-for-byte under `.development/x3/examples/`.
`node --test workshop/tests/authoring_frontend.test.js` passed 18/18, and the
unchanged legacy consumer checks passed. Backend final focused coverage passed
41 tests (16 X3, 25 X2); pack coverage passed 46; campaign coverage passed 46.
These counts describe overlapping focused evidence, not additional full-suite tests.

Independent final source-event review made 75 assertions across four real app
runs with the real bridge/server: fresh creator genesis, exact restart identity,
interrupted primary publication, explicit C/U recovery, care pause, repeat keys,
server reuse and owned shutdown. Its command and result are
`.venv/Scripts/python.exe -B .development/x3/review-main/probe.py` and
`.development/x3/review-main/result.json`. This is not OS keyboard automation.
Context and pack race/authority reviews are separately retained in review-context
and review-packs. All negative and corrected-fixture runs remain available.

The built native candidate is `game/dist/x3-selected-keeper/Mechagotchi/Mechagotchi.exe`
(requires its adjacent `_internal` directory), SHA256
`aad51e51a146c1e5203c7c8ac80f57c904d402d26339a64a42a8f68d2d578b68`.
Command: `.venv/Scripts/python.exe -B game/build_release.py --dist game/dist/x3-selected-keeper --work game/release_work/x3-selected-keeper --windowed`.
All 79 source hashes recorded by the native/integration artifact still match.
Its care/resume launch coverage does not close packaged creator or detached delivery.

The preservation audit accounts for all **4220 incoming source files**, with
25 authorized baseline files changed and no missing or unexpected changes. Both
live Keeper save hashes and the owner HEAD remain unchanged. All 57 initial dirty
identities were verified before X3; final exact dirty identities/hashes and source
inventory are in `.development/x3/final-source-state.json`. Audit evidence is
`.development/x3/preservation-final.json`; runner status is `.development/x3/final-status.json`.
No commit, synchronization, push or publication was performed.

Two preserved/refused edge cases remain explicit: an abrupt process kill before
the genesis manifest can leave an unknown unreferenced snapshot, so automatic retry
refuses instead of adopting it; a malformed server draft without a valid previous
copy is preserved and has no destructive reset UI. Ordinary caught genesis failures
are retryable, and interruption after manifest publication uses existing recovery.

X3 is locally complete. Next: preregister the existing X4 delivery milestone from
`.development/x3/next-x4-app.json` after verifying this exact handoff. It must package
Workshop's actual imports and both real/callback weather resources, fix startup
inspection before default-resource resolution, expose connected native actions,
and prove the actual relocated artifact outside repository ancestry. The current
bundle does not contain that complete payload. X5's immutable ordered replay input
and cache work remains queued. `.development/x3/resume.json` is the exact restart.

## Boundaries and sources

R3 default adoption stays refused; incumbent remains default, optional Q-table
available. Scientific thresholds, negative results and historical corpora stay
unchanged. Niche history, genetic ancestry, Keeper lives and E5 historical
families remain distinct. X4 owns detached delivery, all weather/resource paths
and packaged creator resources. X5 owns ordered immutable replay input manifests
and content-based cache identity. Existing unordered unique founder rows do not
close X5. Native OS keyboard automation and human usability remain unobserved;
source events, real browser interaction and native process launches are separate.
Remote execution is parent-owned and no registered remote is claimed.

Sources: sunsetted/TODO.md X1-X5; Cycle38 contracts; docs/development/local-cycle.md;
docs/mecha-workshop/mecha-workshop-design.md; DESIGN.md; DR0017/0021/0022/0035/0081;
the source-backed product checkpoint and retained X3 evidence.
