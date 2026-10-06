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
The additive Windows artifact, exact runtime identities, detached native/Workshop
checks, full sweep and final preservation audit will be summarized by `closing.json`
and the additive metric `data/game_client/body_compatibility_stage0.json`.

The remaining approved TODO was reviewed independently. X6 product exposure remains
blocked by its measured runtime refusal; X7 broad care and X8 genuine extinction need
qualified evidence, not extra trials or fabricated empty populations. A concrete next
bounded source review is selected-Keeper Workshop live/replay previews: current calls
to `live_cycle`/`build_replay` omit the selected body response. Reproduce whether a
compatible workload Keeper is shown legacy physiology and establish the intended
preview contract before a separate preregistered repair. No preview or scientific
scope was added to this mutation-boundary slice.
