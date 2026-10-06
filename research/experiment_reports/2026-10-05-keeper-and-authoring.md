# Cycle 38 X1/X2: Keeper continuity and faithful authoring

2026-10-05. Requested source: C:/Users/ryanf/github/_shelved/mechagotchi.
Branch phase-l-gate, owner HEAD d4b4337d0dacbdfa816d990297c03a5da2d0cdca.
Only the existing Python 3.13.9 environment is used. No Git mutation or source mirror.

## Outcome and scope

The native client retains earlier actual lives through death, succession, hatch,
archive adoption, explicit new companion and restart. L exposes factual care,
outcomes and campaign links independently of genome ancestry. Missing/malformed
campaign pieces refuse replacement. C then U inspects latest recovery; Y inspects
prior; a later U restores the displayed coherent pair, preserving primary bytes.
Inspection pauses care and C cancels without leaking care/preparation actions.

Workshop Grid/SLIP editing preserves the full selected document, including rich
roles, metadata, parents, mechanics and valid unknown siblings. Bounded undo/redo,
explicit browser draft recovery, keyboard canvas tools and spatial validation help
retain work. Request/disk revisions protect async feedback and overwrite/release;
release uses the selected draft. Four modern carriers round-trip the complete
snapshot; original codec arms remain unchanged.

X3-X8 remain queued. No new mutation, learning, survival or offline-time mechanism
is claimed. E5, ancestry and seven-axis niche histories remain distinct; R3/DR0066
refuses default Q-table adoption and child learning starts cold.

## Contract and actual RED/GREEN

Before edits, 16 incoming review files matched their handoff. Baseline inventory
records 4,200 source files and two live saves in .development/x1-x2/baseline.json.
The supported baseline refresh full run 20261005T222720-12b0da67 passed 2,707 tests
in 24 suites (two documented skips). The contract and workflow slice were then
registered before RED: docs/development/cycle-38-keeper-and-authoring.md and
.development/x1-x2/registration.json. Four disjoint owners implemented X1/X2;
the integration owner controls app/docs/runner. An independent read-only review
found six additional real edge cases, all repaired with retained regressions.

Actual new regression commands (PowerShell, repository root):

```powershell
& .\.venv\Scripts\python.exe -B -m unittest discover -s game/tests -p test_keeper_chronicle.py
& .\.venv\Scripts\python.exe -B -m unittest discover -s game/tests -p test_campaign_recovery.py
& .\.venv\Scripts\python.exe -B -m unittest discover -s game/tests -p test_keeper_continuity_app.py
& .\.venv\Scripts\python.exe -B -m unittest discover -s workshop/tests -p test_workshop_fidelity.py
& .\.venv\Scripts\python.exe -B -m unittest discover -s workshop/tests -p test_authoring_frontend.py
```

Chronicle first RED: 13 tests/17 errors; final 18 new tests plus 70 existing tests
pass. Initial campaign RED: 10 tests, 23 failing subtests/19 errors; final targeted
aggregate 64 tests pass, including incomplete journals and missing elite survivors.
App first RED: five tests with five failures/one error; recovery RED subsequently
confirmed care leakage and foreign pending persistence; ten pre-integration app tests pass; the added first-binding regression brings the final app file to eleven.
The first recovery test attempt used a nonexistent observation property; the
corrected age-field RED is separately retained, not represented as a product failure.
The first prior-snapshot fixture tried to mutate immutable metadata and was correctly
refused; the final test creates an actual second era before choosing the prior pair.

Workshop first backend RED: 15 tests/22 failing assertions or subtests; the initial expanded 23 new
checks pass (25 after independent review below). Existing server 86 tests and codec lab 314 tests pass, with the two old
DR0034 skips. Frontend wrapper first failed for missing shared module; final node
tests and browser observations are recorded in the frontend evidence. All exact
owner commands/results are under .development/x1-x2/{chronicle,campaign,backend,frontend}.
App logs use .development/x1-x2/app-*.log. The initial app RED shell printed its log
after running tests and exited zero; its retained unittest output is the RED result.
Subsequent runs propagate the test exit code.

## Controls and review

Chronicle committed-baseline parity passes 220 lifecycle ticks and 16 child outputs
across both policies and fleet modes. Independent life IDs do not alter RNG seeds.
Eight legacy carrier byte/sidecar hashes match before/after; no old artifacts were
regenerated. Imported-base succession and inherited/earned unlock semantics stay
explicit. Strict validation rejects missing elites, malformed genome journals,
foreign pending campaign commits and conflicting backup associations before write.
Known successor recovery preserves both replaced primaries and binds only explicitly.

Tiny-fixture paired checkpoint observations: first 16.384ms, repeated 11.309ms,
second 17.720ms and restore 27.085ms. Two retained ledger snapshots total 606,208
bytes; manifest 6,676 bytes. Single small observations do not establish scale limits.
The layer uses per-file atomic replacements and retry markers, not a multi-file OS
transaction; Workshop serialization does not coordinate other processes.

## Application demonstrations and closing gates

The integrated full gate and preservation audit passed as recorded below. Source
events, browser interaction and native process launches are recorded separately.
The authoritative restart checkpoint is .development/x1-x2/resume.json. Native keyboard automation, remote execution and exact-published-SHA Windows/Ubuntu
CI remain unobserved; local completion comes from the new full run below.


Actual connected demonstration commands:

```powershell
& .\.venv\Scripts\python.exe -B game/build_release.py --dist game/dist/x1-x2-keeper-authoring --work .development/x1-x2/build-work --windowed
& .\.venv\Scripts\python.exe -B labs/game_loop/verify_keeper_authoring.py --fixtures .development/x1-x2/native-demo --screenshots .development/x1-x2/native-ui --bundle game/dist/x1-x2-keeper-authoring/Mechagotchi/Mechagotchi.exe --output .development/x1-x2/native-observed.json
```

All **34 checks / eight source flows / 48 rendered frames / four native launches**
passed. Both policies traverse actual care/death/child, hatch and archive adoption,
restart/L, recovery inspection/cancel with no leaked care, and explicit restore
retaining damaged bytes with no extra era. The native executable separately loads
and resumes each selected companion for exactly one tick per launch under normal
SDL driver selection; this does not exercise native keyboard input. Representative
recovery and chronology screenshots were inspected at scale16 and controls fit the
paged footer. Source and bundle hashes are in data/game_client/keeper_authoring_stage0.json.

Native candidate: game/dist/x1-x2-keeper-authoring/Mechagotchi/Mechagotchi.exe with
adjacent _internal; SHA256 e23a4edd0b41c38686178df1ab50d8b7d524387fc8d689cfbfe89c271e4c1801.
This candidate does not close the detached-delivery gaps reserved for X4.


Actual Chrome/CDP browser observation passes **17 flows**, no browser exceptions:
rich document load/save, native profile selection, keyboard rich-role paint and
undo/redo, exact validation-cell focus, stale validation/clip rejection, network
retry, selected clip, PNG download and real file-input reimport, reversible clear/
resize/crop with focus return, unsaved selected release and conflict cancel, both
editor restart recoveries, retained mechanics/256-cell mass, and narrow/dark/
reduced-motion controls. Five screenshots are retained and inspected under
.development/x1-x2/frontend/browser-20261005230046342. Built-in Node/CDP drove a
dedicated bounded headless Chrome with temporary profile and loopback server; no
dependency installation or native desktop input workaround was used. Early browser
attempts exposed harness selector/timing/modifier errors, retained separately from
product defects. Shared JavaScript passes ten Node tests via one unittest wrapper.

First integrated game run: **481 tests, 13 failures and one error**, retained in
.development/x1-x2/game-integration.log. These exposed fixture assumptions about a
global campaign ID, unbound saved identities and discarded inherited facts, plus
the historical save hash's newly added metadata. Established fixtures now explicitly
bind the known campaign while byte-preservation assertions remain exact. The new
first-import test verifies association is the only saved change and care stays at
zero. Launch resolves the actual Keeper campaign ID. Niche-history inheritance now
uses real predecessor facts; its 12 tests pass. The historical digest projection
and negative controls keep every prior engine/state/profile/learning field and all
committed scientific hashes. Final targeted app compatibility: **59 tests passed**.

Independent X2 review also repaired profile-content/token read interleaving and
partial modern-carrier downgrade. Complete modern carriers still restore exact
documents; missing/null snapshot bindings refuse instead of losing parent/layers.
The profile snapshot and revision share the write lock. Genuine absent legacy arms
retain their prior interpretation and bytes.


## Actual local closure

Full `20261005T230645-abc7203e` passed **2,778 tests / 24 suites**, 2 documented DR0034 skips, with no source mutations.

The final full run provides the current passing verification for both ENHANCE and
POLISH transitions, as explicitly allowed by the local-cycle contract; it was not
repeated unchanged. All owners were frozen during verification. Runner status is
polish / full_current=true / local_complete=true / running=null. Exact artifacts
and logs are retained in its run directory; artifact counts are read from its
summary/stdout rather than inferred from test totals.

```powershell
$env:PYTHONPATH = (Resolve-Path tools/mechas_cli/src).Path
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --verify full
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --advance enhance --note "Integrated current full pass covers X1/X2 enhancement and repaired regressions."
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --advance polish --note "Current full pass, independent review, application/browser/native evidence and preservation audit close X1/X2 locally."
git diff --check
```

Final strict historical checks: seven game tests and five gate tests pass, including
a new guard that refuses unknown metadata or altered current facts. The gate's
negative controls and every committed baseline hash remain unchanged. Workshop's
final independent-review aggregate is 25 tests passing; its earlier 23-test result
above is retained as an earlier observation.

Preservation audit: all 4,200 baseline source files exist; exactly 25 existing files
changed within assigned source, fixture and current-guidance scope. All prior data,
engine files, live saves and review/archive evidence are exact. Every final owner
fingerprint and observed native-source/bundle fingerprint matches. No commit, sync,
push, source mirror, new environment or security-setting change occurred.

X1 and X2 close locally. X3-X8 remain in the accepted queue. The next action is to
read X3's existing selected-Keeper/pack-composition acceptance, preregister that
integrated scope and reproduce its source-backed failures. No commit sequencing
stop applies; Git mutations stay reserved to the owner. Remote executor setup and
single-writer coordination remain with the parent; no remote environment is claimed.
Exact restart and all dirty-file identities: .development/x1-x2/resume.json.

The closing summary confirms **2,303 JSON artifacts valid**, no suite failures,
and no source side effects. Final game suite: 483 tests; Workshop suite: 118 tests.
All 57 dirty-file identities are retained in the final source-local handoff.

## Subsequent acceptance review (2026-10-05)

The X3 prerequisite review reproduced five missed acceptance cases: missing
predecessor history during successor completion, backup-only history during --new,
known direct-A era provenance, unknown layer siblings, and different-port draft
recovery. The earlier full run remains its measured observation; it did not prove
those cases. See the selected-Keeper creation report and .development/x3/review-x1
and review-x2 for exact probes and the additive repairs. Historical artifacts stay
byte-exact; no prior negative finding or threshold is removed.
