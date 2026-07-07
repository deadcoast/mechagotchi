# Development TODO — Cycle 04: real weather, honest signals, the render seam

Source: the seams cycle 03 recorded, the standing honest blocker, and
the two module targets still deferred. Cycle 03 is archived complete at
`audits/complete/03/` (C1–C6: readability-selection promotion, the
campaign_store lab, the storage module promotion, the Covenant step,
per-era replay, the repair-validity boundary). Governing rule
unchanged: deep integrations over breadth — the ENGINE+GAME duality
(DR 0017); hard/unique features win over easy/generic ones, said
aloud. A task is complete when developed to its description, then
marked. Development proceeds continuously through this TODO's tasks;
planning is triggered ONLY when the TODO is exhausted of its tasks and
confirmed COMPLETE — then the next cycle is planned. (Decision records
remain the design documentation for tasks that need them; they do not
pause the queue.)

- [~] **D1 · Real CuBFF weather.** CLOSED — deferred by owner decision
  (2026-07-07): the synthetic weather IS the shipped answer. The
  game's forecasts (`_stable_snapshot`/`_chaotic_snapshot`) are genuine
  Python computation producing measured effects (storm 1.17x vs calm
  0.90x damage); nothing external is required to run or ship. Ingesting
  real exports from Google's separate CuBFF simulator
  (github.com/paradigms-of-intelligence/cubff) stays an OPTIONAL
  drop-in seam — no code waits on it. The `awaiting_real_cubff_
  snapshots` marker remains an honest description of that seam's
  state, not a queued obligation.
- [x] **D2 · The mortal-wound signal (C6's follow-up).** (2026-07-07:
  `_mortal_wounds` reads each report's per-creature `archive_decision`
  — no new engine number — tallying shattered-core mortal wounds
  (`skipped_invalid`) vs normal deaths, riding the era digest + the
  session `mortal_wound_toll`. Felt as "the toll" in `mechas session`
  and on the Keeper page (amber/red when the bloodline takes losses).
  Honest at zero (demo toll 0, the ~1.25% in-band rate), test-proven
  to fire non-zero under heavy damage and ALWAYS pinned to a
  recomputation of engine truth. Stale post-C3 blocked-state removed.)
- [x] **D3 · `render` module decision record + target.** (DR 0026,
  2026-07-07: dispositioned by the DR 0024 method — the renderer-
  neutral packet contract (`render_packet_from_grid` +
  `render_packet_v2`) already SHIPS in `mecha_engine.genome`; a
  `mecha_engine.render` DRAWING module is REJECTED-until-consumer (the
  only pixel code is non-portable browser JS, no Python rasterizer
  consumer exists), with a named re-opener (a non-workshop Python
  consumer needs to rasterize — server-side PNG export / headless
  renderer / `mechas` image command). Identified a `genome` follow-up
  (`slip_profile` animation-vocab gate into `render_packet_v2`) and a
  workshop-track cleanup (three duplicated canvas draw loops → shared
  asset). `render` + `slip` remain the deferred targets.)
- [~] **D4 · Storm-record & harsher-forecast budget.** CLOSED —
  deferred by owner decision (2026-07-07), following D1. The
  storm-record unlock axis stays functional (it earns from the three
  shipped forecasts); adding harsher forecasts remains an OPTIONAL
  future polish that needs no external data — additional synthetic
  storm intensities would suffice if ever wanted. Not a queued
  obligation.
- [x] **D5 · Campaign-scale session soak.** (2026-07-07: a 12-era
  chained campaign load-verifies the C2/C3/C5 spine through the
  promoted storage module — determinism at scale, ledger blob
  round-trips, deterministic replay of EVERY stored era, replay-file
  hashes matching rows, founder-chain continuity, unlock-chain
  monotonicity; `soak_spine_holds_at_campaign_scale`, 5 tests. Two
  harness-faithfulness bugs found+fixed (the C4 earned blend must be
  replayed not defaulted; `founder_grids=None` ≠ `[]` is an
  intentional DR 0016 distinction — engine unchanged). Live extinction
  honestly unreachable at Stage-0 scale, so succession stays
  fixture-proven — recorded as a blocked state, not faked.)

## Standing note

The identity constraint and DR 0017 govern: the engine is the
application, the game is its showcase. The rating system is the
fallback; `.depreciated/` is the owner's archive (ignore unless
linked). `slip` remains a deferred module target alongside `render`
(D3/DR 0026) — each needs its own decision record before promotion.
Real-CuBFF ingest (D1/D4) is closed by owner decision: the synthetic
weather is the shipped answer and nothing external is required; the
real-export ingest stays an optional drop-in seam, not queued work.

## Sources

- `audits/complete/03/TODO.md` (cycle 03, complete)
- `research/decision_records/0017-recalibration-engine-game-duality.md`
- `research/decision_records/0018-cubff-live-lineage-pressure.md`, `research/decision_records/0020-cubff-pressure-runtime-promotion.md` (D1)
- `research/experiment_reports/2026-07-07-repair-validity-boundary.md` (D2)
- `research/decision_records/0024-grid-schema-animation-species-resolution.md` (D3's disposition method)
- `research/experiment_reports/2026-07-07-covenant-step.md` (D4 named deferred)
- `research/decision_records/0022-storage-module.md` (D5's spine)
