# Body-model compatibility before mutation

2026-10-06. Approved integration repair of X1/X3/X5/X8. Runtime checks now refuse incompatible campaign writes before mutation while supporting intentional new-life model selection in the same Keeper and read-only historical inspection. Final local gates are recorded in `.development/body-compatibility/closing.json`; an absent closing record means verification is still in progress.

## Reproduced problem
Normal campaign loading checked the current companion body response, but recovery,
captured preparation finish, pending era finish and completed-worker retries could
write old-model state first. Workshop validated Keeper identity alone, then enabled
authoring/release/import on a refreshed incompatible context. A stale native save
could overwrite the supported new-life choice; a stale derived lineage export could
also replace the current chronicle while leaving the new companion intact.

Native RED command: `.venv/Scripts/python.exe -B -m unittest discover -s game/tests -p test_body_compatibility.py -v`.
`native-red-corrected.log` records eight methods with 11 failing subcases before production changes. The first `native-red.log` also exposed an invalid test covenant provenance; its correction did not alter product validators or acceptance assertions. Workshop equivalent discovery under `workshop/tests` reproduced 17 failing subcases in `workshop-red.log`; 16 imported fixture tests were subsequently removed from duplicate discovery, not from their original suite.

## Repair and limits
One current Keeper/campaign compatibility rule checks both the selected native session
and the actual companion file at mutation time. A reentrant Windows/Unix publication
lock is shared by native and Workshop writers; its transient lock file is outside
the Keeper directory. Locks cover short persistence work, not era simulation.

Campaign save/checkpoint/initialization, paired recovery, captured preparation and
journal reconciliation, completed-era journals, deferred workers, ancillary planning
and native/Workshop pack imports use the boundary before backups, receipts or durable
writes. Workshop validates again after delayed draft/authoring/pack work. Supported
native save and adoption use expected-byte authority, so a previous session or sibling
candidate cannot overwrite a newer life. Parent final checkpoint can authorize its
already prepared child exactly once. Derived lineage writes use the same authority.

A coherent model mismatch keeps Workshop history and source documents inspectable,
with write capabilities disabled and a visible reason. Immutable reproduction and
read-only pack preview/export remain available. Existing interrupted-journal readiness
rules remain; neither models nor campaign histories are silently migrated.

An interim broader game run was stopped after a newly introduced adoption-order
regression was independently reproduced. Its partial log is `game-check-01.log`.
The fix and tests retain the supported parent-checkpoint-before-child flow while
refusing stale parent/sibling writes. Targeted `native-regressions.log` ran 123 tests,
with one changed refusal-message ordering assertion; preserving the original identity
error priority fixed it. Final `native-green-final.log` passed 24 tests (13 new native
boundary tests and 11 existing continuity tests). Workshop `workshop-green-verified.log`
passed 10 new HTTP tests; 16 existing context tests and one frontend contract also passed.
Independent Windows two-process locking and source review are separately retained.

## Aggregate feedback and final freeze
The first complete sweep `20261006T145657-e97d844a` ran 3,652 tests across 24 suites,
with two errors in game fixtures that placed opaque placeholder bytes in canonical
companion/campaign saves. All other suites and 2,322 JSON artifacts passed, and source
bytes stayed unchanged during the run. Its failed result remains retained.
Independent review approved replacing those success fixtures with valid, independent
Keepers while retaining every receipt, provenance, preservation and retry assertion.
Separate malformed-save cases verify refusal and whole-tree byte preservation.

The review also reproduced a companion-only malformed home accepting a direct pack
import. `companion-only-red.log` ran 21 tests with that one failing subcase. The shared
ancillary guard now validates any present companion even before a campaign exists;
missing-companion standalone folders and valid pre-campaign imports remain supported.
`fixture-authority-green.log` passed all 43 affected tests. Exact command:
`PYTHONPATH=game/tests;game/src;packages/mecha_engine/src .venv/Scripts/python.exe -B -m unittest test_campaign_initialization test_pack_authoring test_body_compatibility -v`
(PowerShell sets PYTHONPATH separately.) Final source review and aggregate repeat are
recorded separately; the failed aggregate is never relabeled as successful.

An external commit advanced HEAD from `d4b4337d0dacbdfa816d990297c03a5da2d0cdca` to
`c15bdff771959a5a45ca470429e7327be979dd01` while the first sweep ran. It changed no
frozen runtime bytes. This task performed no Git mutation and preserved that commit.
The first additive artifact, both retained instrumentation failures, 45 baseline checks
and 58 native/Workshop boundary checks remain intact. That artifact remains bound to
its original recorded HEAD. The final four-line runtime follow-up requires a fresh
`game/dist/body-compatibility-02/Mechagotchi/Mechagotchi.exe` and repeated delivery,
whose actual status and identities are recorded in the closing evidence.

## Scientific disposition and preservation
No engine equation, survival criterion, food access, repair, episode reset, automatic
feeding, death threshold, sampling policy, seed or scientific outcome trial changed.
Pristine workload care remains narrowly qualified at 9/30; morphology 4/30 fails pair28
welfare. Overall care REFUSE and population extinction OPEN remain authoritative.
There is no denominator artifact to repair and no permission to relax nonregression.

Entry source is frozen in `.development/body-compatibility/entry-source.zip`, with
4,457 source identities and 13,872 protected identities in `entry.json`. Both live saves,
all prior data and complete builds are included. No commits, sync, push, checkout,
environment replacement or unattended work was performed. Exact-published-SHA Windows
and Ubuntu CI remains unobserved.

## Closing evidence and next boundary
The final full run `20261006T152001-a6afeffb` passed 3,655 tests across
24 suites, with 2 documented DR0034 zlib skips,
2322 JSON artifacts valid, and zero source mutations during verification.
Command: `.venv/Scripts/python.exe -B tools/ci/run_sweep.py --log-dir
.development/runs/20261006T152001-a6afeffb` through the actual `development.verify(root, 'full', repo_python)` runner.
Final independent source review is `PASS_FINAL_SOURCE`; its 18-file union manifest
and separate 43-test repeat are in `independent-final-source-review.json`.

The final player is `game/dist/body-compatibility-02/Mechagotchi/Mechagotchi.exe`.
This exact artifact passed all 45 baseline checks and all 58 compatibility checks;
the original workload era reproduced `MATCHED`. Native model switches, repeated
preparation/era refusals, compatible exactly-once finishes and real Workshop HTTP
inspection/write-refusal routes were exercised. All owned process trees closed.
No OS keyboard, human usability or remote CI result is inferred from these checks.
EXE SHA-256: `da4a4bb2cd9b7d605c986579abeb24f3b77eb9e2d313ef2ae824bcc52b8774cd`.
Runtime content identity: `1de8bbacf47972749396e70dc5ad6162503dfd1d9baf4a53156b466a071acb14`.
The build binds current HEAD `c15bdff771959a5a45ca470429e7327be979dd01` plus its exact uncommitted runtime hashes.
It does not claim that HEAD alone contains the uncommitted repair or passed cloud CI.

The original artifact and failed instrumentation attempts remain intact. The
instrument correction selected paused review mode for repeated finish checks;
ordinary care/preparation mode advances live ticks and cannot support a whole-tree
no-change assertion. No acceptance criterion was relaxed. All final evidence,
13,872-file preservation audit, source backups, runner status and next action are
indexed by `.development/body-compatibility/closing.json` and `resume.json`.

The remaining approved TODO was reviewed independently. X6 product exposure remains
blocked by its measured runtime refusal; X7 broad care and X8 genuine extinction need
qualified evidence, not extra trials or fabricated empty populations. A concrete next
bounded integration repair is selected-Keeper Workshop live/replay previews.
`next-preview-boundary.json` records actual HTTP dispatch from a valid compatible
workload Keeper: both routes returned 200 and called their engine function once,
omitting `body_response`; both engine defaults are `legacy`. The context also omits
the model. Engine results were substituted to inspect dispatch without simulating
any outcome; the whole Keeper remained byte-identical. This establishes a dispatch
gap, not a measured physiology difference. Preregister model-consistent selected
Keeper previews, honest model metadata and preserved standalone/inspection behavior
before the next RED/repair. No preview or scientific scope was added to this slice.
