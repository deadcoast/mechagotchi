# Cycle 30 T1: make the recorded era-review loop playable

Preregistered 2026-10-04 after S2 full closure/review and before T1 RED.
Authority: DR 0021 core loop (Review, Collect and metric-derived progression),
DR 0022 blob-authoritative campaign history, and the retired gap analysis's
instruction to plan from still-unmet product documentation when a queue ends.

Source gap: `_EraBench.run_era` shows a brief completion message; there is no
player browser for full outcomes/unlock reasons. On restart, `load_state` keeps
an era offset and founders but an empty current-run eras list, so existing
in-memory views do not expose recorded history. Stored era reports and unlock
facts already provide the data; do not alter campaign evolution/resume state.

Implement a T-key era-review mode in the established pygame casing. It reads
current campaign history through the engine storage API using a read-only
SQLite connection, without creating a ledger, training models or running an era.
Open latest; [/] or comma/period browse recorded eras; paged/wrapped details show
stored outcomes, niches/coverage/QD, generations/depth, earned unlock facts and
weather provenance. No fabricated zero for absent fields or new stat definition.
Inherited unlocks must not be attributed to an era of the current campaign.

The companion remains visible and explicitly paused during review. Ignore care
inputs while reviewing; T/Escape closes, F1 help returns to review, Ctrl+S keeps
S2 behavior, C opens the current covenant and E runs the next era. Interactive E
opens the completed era's report; bounded --ticks/--eras entry points retain
their existing automation behavior. Keep older replay/archive mechanics intact;
do not promise historical replays or archive bodies in this report-only scope.

RED pins: stored metrics/facts exact and source records unchanged; history
survives restart independently of current-run eras; inherited-fact filtering;
empty/missing/corrupt history is honest and creates no files; read-only browsing
does not write campaign state or alter the next era's seeds/founders; clamped
navigation; real T/help/close inputs pause/resume the same pet without queued
care; report interactions preserve S2 retry/discard. Render small/long-report
pages and verify every source line remains reachable. Observe actual native
campaign creation/restart and source pygame interactions using those records.

Keep current default/covenants, generator/training math, research thresholds and
all prior artifacts/bundles unchanged. Focused game/package/CLI checks plus native
observations define an implemented checkpoint; full sweep/preservation/diff gates
remain required before T1 local closure. No Git mutations or new workflow.
