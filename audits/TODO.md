# Development TODO — Cycle 02: the DR 0017 R-queue

Source: `research/decision_records/0017-recalibration-engine-game-duality.md`
(owner FEEDBACK 2026-07-06). Cycle 01 is archived complete at
`audits/complete/01/` (T7/T8/T11/T12 carried here as R7/R1/R6/R5).
Governing rule: deep integrations over breadth — the ENGINE+GAME duality;
hard/unique features win over easy/generic ones, said aloud. A task is
complete when developed to its description, then marked. Development
proceeds continuously through this TODO's tasks; planning is triggered
ONLY when the TODO is exhausted of its tasks and confirmed COMPLETE —
then the next cycle is planned. (Decision records remain the design
documentation for tasks that need them; they do not pause the queue.)

- [x] **R1 (=T8) · CTM deliberation into the runtime switchboard.**
  (DR 0017 R1, shipped 2026-07-06 commit 837ca3d: `deliberation` SLIP
  field, ctm_ticks semantics pinned verbatim, both package mirrors
  synced; measured 64 observable thinking events across 8 episodes,
  wellbeing delta 0.0 in sheltered episodes — verdict recorded:
  adopt-as-expressiveness / watch-for-utility. The creature visibly
  thinks.)
- [x] **R2 · CuBFF live lineage pressure.** (DR 0018, 2026-07-06: Pipeline C wired into the evolution loop — chaotic soup 1.17x damage/111 cells vs stable 0.90x/88 at the same seed, provenance per generation, semantic-compiler rule held; runtime.evolve promotion queued as R2.5.)
- [x] **R2.5 · Promote the CuBFF pressure seam into `runtime.evolve`.**
  (DR 0020, 2026-07-07: `cubff_pressure_source` keyword on the
  promoted `evolve`; verbatim `_cubff.py` mirror + lab-side parity
  drift guard; contract green, promoted-surface directional effect
  1.17x vs 0.90x. Real-snapshot clause NOT claimed — recorded blocked
  on the ingest gate's `awaiting_real_cubff_snapshots`; unblocks with
  no code change when real exports are ingested.)
- [x] **R3 · Learned readability — TRUE ML as the primary path.**
  (DR 0019, 2026-07-06: physics-supervised pairwise ranker — heldout
  1.0, leave-one-family-out 1.0 on all four degradation families,
  auditable learned weights; LIVE consumer: readability-aware parent
  selection in the evolution loop, A/B at the same seed 0.361 vs
  0.270 post-founder mean, gen-3 0.498 vs 0.199. The manual rating
  system stays exactly as built as the FALLBACK and calibration
  check — never a blocker.)
- [x] **R4 · The game loop decision record.** (DR 0021, 2026-07-07:
  "Eras of the Soup" — Keeper fantasy; era = one `runtime.evolve`
  run, campaign = era chain persisted via `founder_grids` (the DR
  0016 spine); CuBFF pressure sources as weather; progression
  currencies verbatim from report metrics; extinction stakes from
  the measured empty-archive behavior; five player-NOTICES each
  mapped to a shipped mechanism (R1/R2/R3/T1/persistence). Unblocks
  the `storage` module DR. First law: everything shown is engine
  truth.)
- [ ] **G1 · `storage` module decision record.** (Unblocked by DR
  0021.) Schema for campaigns, eras, unlocks, lineage; SQLite per DR
  0011's ratified pointer; stdlib `sqlite3` keeps the package
  dependency policy intact.
- [ ] **G2 · Session-runner lab (`labs/game_loop/`).** One full
  session over promoted surfaces: era-chaining via founders, weather
  selection, unlock evaluation from report metrics, extinction and
  succession. Deterministic, triad convention. JSON-artifact
  persistence interim until G1 lands.
- [ ] **G4 · The Keeper's surface.** Session UI on the workshop
  server pattern; `mechas` gains session commands (DR 0007 charter).
  After G2/G3.
- [ ] **R5 (=T12) · Replay recorder + workshop scrubber.** Per-tick
  render packets from live_cycle/episodes into a replay artifact; the
  preview gains a scrubber (engine truth, recorded). The player's window.
- [ ] **R6 (=T11) · Dataset program completion.** `mechaseed_200`,
  `mutationbench_5000`, `replay_100k_ticks` (feeds R5) — each with a
  README + ledger entry. The ML tracks' fuel.
- [ ] **R7 (=T7) · Grid-schema animation/species fields.** Implement per
  the og starter schema, or record the T4 projection design as the
  superseding decision — either way, developed then marked.

## Standing note

The identity constraint and DR 0017 govern: the engine is the
application, the game is its showcase, and every task above serves the
duality. The rating system is the fallback; `.depreciated/` is the
owner's archive (ignore unless linked).

## Sources

- `research/decision_records/0017-recalibration-engine-game-duality.md`
- `audits/complete/01/` (cycle 01, complete)
