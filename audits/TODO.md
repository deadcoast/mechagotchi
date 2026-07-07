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

- [ ] **D1 · Real CuBFF weather — close the ingest gate honestly.**
  (The standing blocker `awaiting_real_cubff_snapshots`, DR 0018/0020;
  the game "upgrades to real exports with zero seam changes".) Produce
  real CuBFF `bff`/`bff_noheads` snapshot exports (or a faithfully
  reproduced fixture set the owner authorizes as real-shaped), run them
  through `labs/cubff_transducer/real_snapshot_ingest.py`, and confirm
  the ingest gate clears with the promoted `cubff_pressure_source`
  seam UNCHANGED — the weather system was designed for exactly this.
  If real exports remain unavailable, record precisely what blocks
  them and what a faithful stand-in would require (honest, not faked).
- [x] **D2 · The mortal-wound signal (C6's follow-up).** (2026-07-07:
  `_mortal_wounds` reads each report's per-creature `archive_decision`
  — no new engine number — tallying shattered-core mortal wounds
  (`skipped_invalid`) vs normal deaths, riding the era digest + the
  session `mortal_wound_toll`. Felt as "the toll" in `mechas session`
  and on the Keeper page (amber/red when the bloodline takes losses).
  Honest at zero (demo toll 0, the ~1.25% in-band rate), test-proven
  to fire non-zero under heavy damage and ALWAYS pinned to a
  recomputation of engine truth. Stale post-C3 blocked-state removed.)
- [ ] **D3 · `render` module decision record + target.** (One of the
  two remaining deferred module targets; DR 0004's list.) The render
  packet + packet-v2 selection + the workshop draw path have shipped
  as lab/workshop code for cycles; propose whether a promoted
  `mecha_engine.render` earns its target now (a real consumer beyond
  the workshop, verbatim-portable) or stays deferred with the reason
  recorded — the DR 0024 disposition method, applied to render.
- [ ] **D4 · Storm-record & harsher-forecast budget (C4's deferred
  axis).** (C4 named it deferred: `harsher_forecasts` await weather
  sources beyond the three shipped.) Once D1 lands (or its stand-in),
  the storm-record unlock axis gains real forecasts to unlock —
  harsher CuBFF sources with provenance display — closing the one
  progression axis C4 left inert. Depends on D1.
- [ ] **D5 · Campaign-scale session soak.** A longer campaign
  (many eras, real succession on measured extinction) run as a
  deterministic soak test over the promoted surfaces + storage module,
  proving the ledger, replay directory, and unlock chain hold at
  campaign scale — the C2/C3/C5 spine under sustained load. Triad.

## Standing note

The identity constraint and DR 0017 govern: the engine is the
application, the game is its showcase. The rating system is the
fallback; `.depreciated/` is the owner's archive (ignore unless
linked). `slip` remains a deferred module target alongside `render`
(D3) — each needs its own decision record before promotion.

## Sources

- `audits/complete/03/TODO.md` (cycle 03, complete)
- `research/decision_records/0017-recalibration-engine-game-duality.md`
- `research/decision_records/0018-cubff-live-lineage-pressure.md`, `research/decision_records/0020-cubff-pressure-runtime-promotion.md` (D1)
- `research/experiment_reports/2026-07-07-repair-validity-boundary.md` (D2)
- `research/decision_records/0024-grid-schema-animation-species-resolution.md` (D3's disposition method)
- `research/experiment_reports/2026-07-07-covenant-step.md` (D4 named deferred)
- `research/decision_records/0022-storage-module.md` (D5's spine)
