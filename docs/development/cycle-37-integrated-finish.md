# Cycle 37 W5 - Integrated reader and preparation finish

2026-10-05, preregistered before RED following completed W4. Direct delegation
requests demonstrated usability corrections across existing screens, not new
panels or scientific mechanics. Same source tree and .venv; no Git mutation.

## Observed defects and repair contract

Actual source app at scale 1 reproduced in .development/w5-review.json:
F1/T/B/V/L close consumes care on the closing frame and allows F from the same
event batch; H/I already prevent it. Apply one explicit reading-close barrier
to readers, including open/close within one batch. Subsequent care/preparation
keys from that closing batch are ignored, queued care is cleared, and normal
care resumes next frame. Explicit adoption behavior is unchanged. Two older
archive tests incidentally expect age 1 after close; strengthen to age 0 and
add next-frame resume assertions, without weakening scientific thresholds.

Help resets page 3 of a hatch explanation to page 1. Preserve the underlying
page and selection/event/frame when help opens/closes; help starts at page 1.
Use contextual help for covenant, reports, archive/history, replay and lineage,
keeping current controls and honest provenance. Covenant mode remains live;
say so. Keys 1-4 spend unlocks there; ignore the unadvertised 5 weather action.
Weather keys still work outside covenant mode. No changes to spending gates.

K End I K loses z.json selection. Keep a per-session picker for each kind,
refresh on reopen, preserve selected filename when still present, revalidate
digests on import, and clamp safely if removed. No new persistence schema.

Malformed campaign_state.json crashes C. Show a recoverable unavailable
message with working close/help, preserve corrupt bytes, and handle the same
existing campaign-loading failure at export/adoption command boundaries.
No automatic repair, replacement or fallback to a different campaign.

Lineage hides earlier ancestors and all but the last event despite the existing
paged footer. Make every recorded ancestor/event field reachable verbatim,
with controls first and plain direction labels. No inferred ancestry, E5
family conflation, niche reinterpretation or generated missing provenance.

## Verification and closure

Formal RED/GREEN reproduces these failures and tests closing-batch isolation,
next-frame resume, page bookmark, selection refresh, malformed campaign paths,
and complete lineage fields. Preserve W1-W4 controls, saves, traces, outputs,
scientific lab/package files and historical artifacts. Review actual small
and normal layouts. Demonstrate connected pack/covenant, H/WFC/O, care,
era/report/archive/niche/replay, cancellation, close and restart source flows.
Native process smoke remains distinct from unavailable native keyboard input.
Keep report/card/DR0080/artifacts/ledger together, run full sweep/artifact/diff
checks and preservation audit. Do not repeat unchanged gates or create a new
backlog if this bounded finish closes the demonstrated local gaps. Remote
execution and exact-published-SHA CI remain unobserved and parent/owner owned.

Focused reconciliation: three additional older tests pinned the previous
closing tick. Report/replay tests now include an ordinary frame after closing
and retain their age/action assertions; the help test expects only its existing
post-close frame to advance. The new W5 tests independently assert exact byte
preservation through every close and correct next-frame state with no feed.

Visual finish finding: the integrated post-era archive screenshot shows the
previous long era notice pushing archive navigation off page 1. On archive
entry discard that stale transient notice (the report stays saved), put Back
and Help beside archive/history navigation, and retain campaign identity and
fresh command failures. Verify at the smallest supported casing before close.
