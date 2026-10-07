# DR 0093: authoritative model for newly recomputed previews

Date: 2026-10-06. Status: locally qualified software repair; publication unobserved.

## Context

The selected compatible workload Keeper was omitted from both Workshop preview
dispatches, which therefore used legacy physiology. Preview acceptance pinned only
local document revision; recomputed replay IDs bound grid ID and seed alone.

## Decision

Expose the validated current Keeper model, freshly bind live/replay dispatch and
post-simulation checks to context pins, and refuse client attempts to override
authority. Standalone Workshop remains legacy. Current-model recomputation remains
read-only, including supported new-life/current campaign mismatch. Old footage
stays bound to its recorded model and original identity. Version identity only
for new recomputed previews and bind all simulation inputs and effective options.

Shared browser context owns latest-refresh-wins, immediate invalidation, request
pins and final fresh-context checks before displaying results. Existing previews,
animation timers and selected context inventory invalidate together. The current
body model and saved-footage distinction are visible without changing UI design.
Native saved preview publication must preserve an existing recording on repeated
or interrupted operations; retry may finish the same exact payload only.

## Boundaries

No equations, food access, thresholds, studies, cohorts, seed searches, era hunts
or defaults change. Overall care REFUSE, extinction OPEN. No scientific outcome
claim follows from deterministic software regression fixtures. Owner retains
commits/sync/push; exact-published-SHA Windows/Ubuntu CI is unobserved.

## Verification

Preregistered contract and actual RED/GREEN logs live under
`.development/preview-consistency`. Full sweep passed 3682 tests / 24 suites, with 2 documented skips.
Actual browser15, independent source53, additive Windows identity/functional checks
and final preservation/closing review are recorded in closing.json.

## Sources

- docs/development/cycle-38-preview-consistency.md
- game/src/mecha_game/keeper_context.py
- workshop/server/workshop_server.py
- workshop/shared/authoring.js
- workshop/preview/preview.html
- game/src/mecha_game/replay.py
- game/src/mecha_game/campaign.py
- .development/preview-consistency/registration.json
- .development/preview-consistency/entry.json
- .development/body-compatibility/next-preview-boundary.json
