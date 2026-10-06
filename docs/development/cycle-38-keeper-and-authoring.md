# Cycle 38 X1-X2 - Keeper continuity and faithful authoring

Date: 2026-10-05. Build track: SHARED (game persistence and Workshop/codec consumers).
Preregistered before new RED tests or implementation under the user's explicit
instruction to delegate the approved TODO and begin development. Baseline HEAD:
`d4b4337d0dacbdfa816d990297c03a5da2d0cdca`, phase-l-gate. Preserve the 16 prior
review files, all scientific history and the exact existing source tree/.venv.

## Authority, scope and one integration owner

Implement the complete X1 and X2 outcomes in `sunsetted/TODO.md`, grounded in
`research/reports/2026-10-05-product-design-implementation-checkpoint.md` and its
retained reproductions. DR0021/0022, DR0067/0068/0072 govern Keeper truth and
persistence; the Workshop design charter, DR0024/H3 projected animation and
DR0063 covenant mechanics govern authoring. No scientific defaults, mutation
operators, promotion bars or inherited learning policy change in this slice.
R3/DR0066 default REFUSE remains. X3-X8 are separate pending outcomes.

The main agent owns integration, app.py, source-event acceptance, shared docs,
DESIGN.md, registry and the runner. One agent owns session.py/lineage.py/chronicle.py
and chronicle tests; one owns campaign.py/covenant_io.py/era_plan.py, optional
campaign_recovery.py and campaign tests; one owns Workshop server/authoring adapter
and backend tests plus the four declared carrier exporter modules; one owns grid
and SLIP HTML, shared authoring.js/authoring.css and frontend tests. No overlapping file edits.
Agents must report any needed ownership expansion before editing it. All actual
changes stay in this repository; no Git mutation, mirror or environment is allowed.

## X1: durable factual lives, independent identities

The observed H/Enter and B/A paths discard accessible earlier lives by replacing
CompanionSession. Use a non-mutating `session.adopt(grid, profile, model=...,
name=..., origin=..., source=...)` candidate API. Carry the Keeper chronicle and
session clock into the candidate, then checkpoint before replacing the displayed
session. Invalid candidate or failed prior checkpoint cannot replace the active
life. Checkpoint failure after adoption keeps the existing retry/discard behavior.
Explicit CLI --new also retains available valid prior Keeper history, while
allowing its already-supported explicit policy choice on that fresh life. If
the old primary is invalid, retain its bytes and explicitly mark missing history;
do not pretend a corrupt record was recovered or invent earlier life facts.

Persist a Keeper identity independent of genetic grid IDs and campaign identity.
Each actual life has a unique life identity even if the same genome is adopted
twice. Record real birth/death/succession/adoption/replacement events, explicit
source campaign/era facts when known, bounded recent events and complete counters
for observed keeper actions, autonomous actions and begs. Living replacement is
`replaced_alive`, never an invented death or genetic parent. Genetic ancestry
remains the engine's recorded data. Existing unknown history is explicitly
unavailable or partial; no reconstruction from a truncated log or archive label.

Expose all factual life summaries/transitions in the existing L browser and
derived lineage export. Maintain legacy save readability and unchanged legacy
file bytes during reads. Validate new chronicle identities, counters and active
life consistency before accepting a save. Explicit backup recovery preserves
replaced bytes and recovers the recorded snapshot, not a fabricated merged story.

Preserve fresh-life learning semantics: keep selected policy/configuration,
but never inherit trained Q-tables. Use a saved per-adoption-line succession
index (legacy defaults to previous lineage length) so retaining unrelated adopted
lives does not alter generation seeds or incumbent child output. No life ID is
injected into engine state or scientific tick logs.

`bind_campaign(id, predecessor_campaign_id=...)` may establish an unknown legacy
association after validated load, no-op for the same ID, or record an explicit
known successor relation. It must not silently replace a known unrelated identity.
New application campaigns use the current Keeper identity rather than a shared
demo identity. Legacy coincident IDs cannot prove cross-home association; do not
claim otherwise or invent lost identity metadata.

## X1: campaign loading, imported base and coherent recovery

Any established state/ledger/recovery evidence prevents the new-campaign fallback.
Strictly validate payload shape/types, configuration/profile, campaign identity,
status, contiguous era count/seed sequence and recorded unlock facts using a
read-only existing ledger connection. Missing, truncated, foreign or mismatched
state/ledger must refuse with preserved bytes and readable app recovery guidance,
not KeyError or a new default campaign. A current/spent/imported covenant need
not equal the last immutable era's covenant. Legacy missing base_parameters keeps
its documented interpretation.

Successor uses the currently imported base, resets spent settings according to
the existing base contract, and preserves exact inherited unlock facts. Existing
own-versus-inherited earning semantics and past era profiles are not redefined.

Publish a recoverable state+ledger snapshot only after the complete pair validates.
Capture the ledger through SQLite backup, keep exact state bytes and content
identities, and publish its manifest last. Repeated unchanged checkpoint is a
no-op. Recovery is explicit, identifies the selected campaign/checkpoint and pins
the previewed manifest digest. Preserve existing primary bytes before restoration;
refuse a known unrelated Keeper association. Per-file atomic replacement is not
multi-file atomicity: an interrupted restore remains blocked and explicitly
retryable through an explicit restoration marker that blocks normal loading until
the pair validates. Retention applies only to specifically owned recovery snapshots, never
historical reports, replays, external saves or unknown files.

The unavailable covenant view offers U to inspect/explicitly restore the known
coherent checkpoint; other care and read-only history stay available. Broader X4
startup/product routing is not implied. No backup means truthful unavailable,
not reconstruction. A recovery does not silently clear pending completed work.

Only the completed-result journal may settle its exact recorded prior-state
digest or exact completed state and contiguous ledger prefix. Missing prior eras
must refuse. A genuinely first-ever era with no prior state/predecessor can still
recover a new ledger. Save snapshot after state persistence and before clearing
pending completion. Retry after ledger/state/snapshot interruption commits the
same output once, with no new evolve call, duplicate own unlock, or replay row.

## X2: one faithful authoring document and explicit revisions

Introduce an additive envelope `mecha_workshop_document_v1` containing the full
semantic grid and optional profile/layers. One shared backend adapter owns document
validation/projection, and one shared browser authoring state owns history,
recovery and async revisions. Preserve existing legacy requests and codec bytes.

Modern load/save/validation/preview/export/import/release operate on this complete
document, preserving rich cells, materials, mutation weights, organs, anchors,
lineage, metadata, valid unknown fields and SLIP mechanics. Only explicit edits
change fields. Rich alphabet projection must be accepted on reload; never list
layer/profile sidecars as creatures. Ambiguous/destructive transforms are explicit
and undoable or refused. No new mutation/lock science is introduced.

Modern requests carry draft_revision; responses echo it and return canonical
document_digest. The client applies feedback only to the originating revision.
Writes carry expected_disk_revision for optimistic comparison, including related sidecar
bytes; conflicts preserve files and the unsaved draft. Server writes serialize
related operations, replace files atomically, and retain unique overwrite backups.
Release receives the exact selected inline document, validates it, identifies its
revision and checks a release-target conflict token. The response separately names
released_document/digest and its explicit released_into_ecosystem transform.
A saved filename cannot stand
in for a visibly different draft. Existing legacy release calls remain compatible.

The SLIP editor retains its complete loaded JSON and patches only changed known
controls, including preserving mechanics, versions and unknown valid siblings.
Mass limits support actual 16x16 authoring. Engine validators remain authoritative.

## X2: reversible work and accessible interaction

The shared browser state owns bounded undo/redo and persistent local draft history.
Recovery is explicit Restore/New, distinct from saved/released engine inputs.
Clear/load/import/resize and crop are reversible; destructive crop is explained.
Storage failure is visible and allows downloading the draft. Server/network failure
retains the exact draft, offers retry, and never produces a false saved/released
state. Async validation/preview responses cannot overwrite a newer revision.

Retain the existing LCD/workbench palette, typography and native form controls.
Make the canvas focusable with visible cell focus; arrows select cells,
Space/Enter applies the chosen tool, and current tool shortcuts remain available
without hijacking text entry. Validation issues retain verbatim authority text and
offer spatial cell navigation when coordinates are known; no invented location.
Use native buttons/dialog behavior with keyboard focus/return and concise visible
feedback. DESIGN.md records canonical owners, not a separate simulation/UI kit.

## X2: carrier fidelity without erasing historical codecs

The backend agent may add optional authoring_document to the four existing
`labs/workshop_editor` carrier writer/export modules:
png_embedded_sidecar_writer.py, png_apng_sidecar_decoder.py,
aseprite_user_data_chunk_writer.py and spritesheet_sidecar_decoder.py.
Absent this optional arm, original bytes and old recorded semantics remain pinned.
Modern carriers bind the complete authoring snapshot into existing sidecar/image
validation. Import validates both binding and semantic overlay, refusing tampered
or conflicting document snapshots. Exact metadata and parent IDs survive the
modern round trip; original legacy reconstruction remains reproducible.

Modern APNG must carry the sidecar needed for reimport and use APNG-specific binding
validation. Projected clip packets derive from the selected semantic draft.
No historical artifacts are regenerated under the new arm or relabeled.

## Falsifiable verification and closure

Each owner first records a failing regression against the preregistered outcomes,
then the same checks passing, with exact commands and retained output. Baseline
refresh is the required workflow gate, not a new product result. Focused checks
are for iteration. No full runner verification while another agent edits source.

X1: test malformed new/legacy payloads; same-genome distinct lives; paired legacy
succession output; actual care→death→child→hatch→archive adoption→restart under both
policies; missing/truncated/foreign state/ledger; imported base and inherited
unlocks; interruption/retry at ledger/state/snapshot boundaries without recompute;
explicit paired recovery preserving originals and pending work. Main must also
exercise real source pygame event flows through H/Enter, B/A, L, C/U and restart.

X2: test semantic load/save/reload, rich antenna, mechanics, safe sidecar catalogs,
all four modern carrier roundtrips and tampered binding refusal; legacy parity;
selected draft release, stale disk conflict and retained backups. Meaningful
JavaScript tests cover undo/redo, revision arbitration and recovery; their unittest
wrapper explicitly skips if Node is absent. Real browser DOM/keyboard flows must
exercise editing, errors, stale responses, draft recovery, release and resizing.
A dedicated installed headless browser/CDP with temporary profile and loopback
endpoint is allowed if supported; no browser security bypass or owner profile.
Native keyboard remains unavailable and is never conflated with browser coverage.

Close only after independent integration review, realistic product demonstrations,
full sweep/artifact validation, preservation audit and diff review. Keep report,
card, DR0081, new measured artifact and research ledger together; mark any unmet
criterion explicitly. Preserve all live save hashes and earlier reviewed evidence.
No Git action or cloud/native-keyboard success claim is authorized by local passing.

## Sources

- `sunsetted/TODO.md` (X1-X2 complete acceptance)
- `research/reports/2026-10-05-product-design-implementation-checkpoint.md`
- `research/decision_records/0021-game-loop.md`
- `research/decision_records/0022-storage-module.md`
- `research/decision_records/0024-grid-schema-animation-species-resolution.md`
- `research/decision_records/0066-playable-qtable-opt-in.md`
- `research/decision_records/0067-safe-companion-resume.md`
- `research/decision_records/0068-durable-play-checkpoints.md`
- `research/decision_records/0072-durable-keeper-loop.md`
- `docs/mecha-workshop/mecha-workshop-design.md`
- `docs/development/local-cycle.md`

## Implementation clarification, 2026-10-05

The modern carrier arm also needs external_metadata_sidecar.py to validate
authoring_document profiles with the promoted validator. Its absent legacy arm
keeps the former migration/advisory gate and byte output. This fifth adapter is
necessary for the existing v0.2 cleanliness covenant, not a scientific threshold
change. Backend owner was explicitly assigned this path before its edit.

The native recovery surface exposes U for latest and Y for prior managed paired
checkpoints. Inspection pauses care, U on a later frame confirms the displayed
identity, and C cancels. Binding accepts a verified successor of a known campaign;
pending completion checks the same association before any persistence. Selected
snapshot and primary digests remain pinned, and a retry never discards pending work.


Integrated compatibility clarification, 2026-10-05: new identity/chronicle metadata
necessarily extends saved bytes. The original Q2 save-hash instrument in
labs/lifecycle_sim/slip_mechanics_gate.py and its game test retain the exact old
digest over a strictly validated legacy projection, removing only this explicitly
new metadata. They also validate the complete new schema; old baseline hashes and
adoption thresholds remain untouched. Fixtures that describe an established Keeper
now record their known campaign association before byte-preservation checks.
The new app regression independently verifies first binding changes only chronicle
association, with all other persisted fields equal and no care tick. The niche
history fixture inherits actual predecessor unlock_state facts; every acceptance
assertion remains. No saved scientific evidence is regenerated.
