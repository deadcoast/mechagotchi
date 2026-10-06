# Cycle 38 X3: selected Keeper creation and exchange

Preregistered 2026-10-05 after the X1/X2 acceptance review. Authority: current
user delegation, TODO X3, DR0017/0021/0022/0035, existing X1 identity/recovery
and X2 complete authoring documents. All implementation uses this source tree
and its existing Python 3.13.9 environment. No Git mutations, mirrors, publishing,
remote executor claims or scientific/default adoption changes.

## Review evidence and prerequisite repairs

Prior full run 20261005T230645-abc7203e passed 2778 tests/24 suites/two documented
DR0034 skips/2303 JSON. That measured result remains historical evidence, not
proof of every acceptance criterion. The independent X1 criterion map and
reproductions are under .development/x3/review-x1; X2 under review-x2. Preserve
all 57 initial dirty identities, owner HEAD d4b4337d0dacbdfa816d990297c03a5da2d0cdca,
and the 4220-file baseline in .development/x3/baseline.json.

Before integrating selected-context writes, repair these reproduced gaps:
1. Pending successor completion must validate its recorded predecessor state and
   ledger prefix before any mutation. Missing parent eras refuse; journal and
   original files remain intact. Valid exactly-once recovery remains supported.
2. Explicit --new with missing/invalid primary must preserve any existing backup
   bytes and available real life history. Never describe unavailable history as
   none or overwrite the last available evidence during the next checkpoint.
3. Direct native A adoption includes its known current era index under both
   policies, while unknown source facts stay unknown.
4. Editor visibility, paint and other edits preserve accepted layer siblings and
   full semantic data. Destructive ambiguity is explicitly refused or reversible.
5. Draft recovery survives a real Workshop server restart on a different port,
   not merely page reload. Drafts remain separate from validated engine exports.

## Context and resource ownership

An explicit --keeper-dir selects a native Keeper at server startup. Absence means
the existing browser_lab project, visibly labeled and never silently merged.
Native server directories are selected Keeper/workshop/{grids,slips,metrics,drafts}
and its existing released/, covenants/ and packs/. No second save-home resolver,
new environment, source mirror or hidden persistent service. CLI passes explicit
selection and offers pack composition. Native J opens the creator for its current
Keeper through an owned foreground-lifetime server, pauses care while its creator
view is active, and shuts down its owned server on application exit. Unsupported
or missing resources give an actionable result. X4 remains responsible for fully
detached packaged resources/install journeys; X3 source launch is not that gate.

A narrow read-only Keeper adapter uses existing companion, campaign and ledger
validators. Return stable context identity, semantic revision, actual active
profile/budget, availability reasons and recorded identities. Read ledger through
a coherent read-only transaction and check JSON identities across it; do not use
raw SQLite file hashes as WAL snapshot identity. No care ticks, training or
automatic reconstruction in inspection. Legacy identity labels are explicit.

Native writes require selected context_id and expected_context_revision and
revalidate immediately before writing. Stale selection refuses with 409, preserving
draft and files. All authoring save/release/pack/draft paths obey this boundary;
legacy lab session/companion mutation APIs are unavailable in native mode.
No request may retarget the server to a different Keeper. Native W gathers only
that Keeper's release inbox; historical shared-inbox helper behavior stays available
for its existing explicit consumers and scientific controls.

## Complete creation, release and provenance

Context APIs list/resolve saved companion, selected releases and exact saved
elite references (campaign_id, era_index, niche_key) as full X2 documents.
Show selected Keeper/path/campaign/profile and actual earned caps in creator,
preview and inspector. Authoring and preview remain engine-authoritative.
Release validates the exact selected draft and target disk revision, identifies
the saved output digest and explicit release transform, and distinguishes staging
from actual later engine admission. Store declared source/context provenance
without pretending it proves genetic descent.

Inspect actual saved campaign/predecessor history, recorded genotype relations
and verbatim era report founder admission/refusal after restart. For new eras,
use the existing founders table for full uniquely identifiable submitted genomes,
source kind and actual verdict, carried through completed-result recovery.
The existing table cannot express ordered duplicate IDs: do not deduplicate,
reorder or change evolution to fit it. Omit ambiguous rows and show unavailable/
ambiguous coverage honestly. Historical missing records stay missing.
X5 still owns immutable ordered execution manifests, full replay inputs and cache
identity; no competing ledger/schema or causal inference is introduced here.

## Durable recoverable authoring

Server-backed per-context grid/slip drafts persist a bounded complete snapshot/
history with optimistic draft revision, atomic writes and recoverable prior bytes.
They are unvalidated work, separate from engine-ready files. Restore/New is explicit.
A startup blank cannot overwrite recoverable work. Keep local fallback and a
download route when persistence fails. Different Keepers have distinct namespaces;
stale or conflicting requests preserve both sides without silent merging.
A restart with a new origin must offer the exact recoverable draft.

Retain the existing LCD/workbench design and canonical shared authoring behavior.
Context errors, stale selections and unavailable provenance are readable and
actionable. All file-provided labels/provenance use escaped text. Native controls,
keyboard focus/return, narrow layouts and existing undo/revision behavior survive.

## Named pack composition and exchange

Use mechagotchi_pack_v1 and existing engine validators. Provide supported UI for
naming a pack, choosing complete creatures/profiles, previewing contents, downloading
validated bytes and importing into a second explicitly selected Keeper. No Python
or manual JSON is required. Deep-copy exact rich payloads and declarative provenance.
Validate composition metadata/types/IDs and reject ambiguous conflicting valid
duplicate identities without arbitrary first-wins; malformed duplicates must not
block otherwise valid items. Preserve legacy low-level fixture writer behavior.

Shared service offers preview_pack, import_pack_document and export_pack_bytes.
Keep file import exact raw-byte expected_digest distinct from canonical pack_digest.
Retain source pack/receipt in selected packs/ without clobbering unrelated files.
Per-item outcomes distinguish accepted, already present, refused, conflicting and
I/O failures; ok means processed, with explicit partial/all_accepted summaries.
Format validity does not imply active-covenant compatibility or engine admission.
Foreign provenance never rebinds the receiving Keeper. No hosting/signing/registry.

## Falsifiable checks and completion

Record exact RED and GREEN commands per owner before/after repairs. Targeted
regressions cover all five prerequisite gaps, context missing/foreign/stale,
actual budget from non-default/imported covenant and earned unlocks, full semantic
release, isolated write paths, safe inspector text, draft port restart, pack
tamper/conflict/partial/retry and two-Keeper isolation. No relaxed acceptance,
new scientific mechanics or regenerated historical baselines.

Demonstrate selected Keeper -> full author/preview -> exact release -> engine
admission/refusal -> era -> restart -> supported descendant inspection. Demonstrate
named UI pack export/import into second save, covenant selection/preparation and
founder gathering/run. Real browser DOM/keyboard evidence uses supported installed
Chrome/CDP with temporary profile; no security bypass. Source pygame event tests
and actual native process launches remain separate; native OS keyboard was unavailable.

Disjoint owners: campaign/recovery foundation; server/context/draft API; pack service;
frontend surfaces; main native/CLI/contribution and integration. One runner owner,
no full sweep while source writers are active. Close only after independent review,
real demonstrations, full sweep/artifact checks, preservation audit and diff review.
Keep this contract, code, report, card, metric artifact, decision and research ledger
together. Checkpoint exact HEAD/dirty identities, tests and next action under
.development/x3. Keep remote setup and publication with parent/owner. If bounded
context requires handoff, mark unfinished criteria explicitly rather than claim closure.

## Sources

- sunsetted/TODO.md, X1-X5 acceptance and dependencies.
- docs/development/cycle-38-keeper-and-authoring.md.
- docs/development/local-cycle.md.
- docs/mecha-workshop/mecha-workshop-design.md and DESIGN.md.
- research/reports/2026-10-05-product-design-implementation-checkpoint.md.
- research/decision_records/0017*; 0021*; 0022*; 0035*; 0081*.
- .development/x3/review-x1 and review-x2 measured acceptance evidence.

## Integration clarification: recoverable creator genesis

Independent source-event review reproduced a first-J state-write interruption:
the new ledger survived without state or a recovery snapshot. Preregistered repair
uses existing paired recovery authority: prepare a new campaign in an owned
temporary directory, validate it, publish its immutable snapshot and existing
manifest at the selected Keeper before either primary, then explicitly materialize
that pinned pair. Only absence of all prior campaign evidence permits initialization.
Recheck for external evidence before publication. An interruption after publication
must leave the existing C/U recovery route usable; an earlier failure leaves both
primaries unchanged. No new persistent journal schema or reconstruction fallback.

Repeated J/Enter key events must not close the paused creator or open repeated
browser tabs. A browser launch failure retains a supervised URL path and still
closes the owned server/process on exit.
