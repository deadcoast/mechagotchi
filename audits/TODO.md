# Development TODO — Cycle 03: deepening the loop

Source: the seams cycle 02 identified and recorded (each task cites the
document that named it). Cycle 02 is archived complete at
`audits/complete/02/` (all nine tasks: R1–R4, G1–G4 interleaved, R5–R7).
Governing rule unchanged: deep integrations over breadth — the
ENGINE+GAME duality (DR 0017); hard/unique features win over
easy/generic ones, said aloud. A task is complete when developed to its
description, then marked. Development proceeds continuously through
this TODO's tasks; planning is triggered ONLY when the TODO is
exhausted of its tasks and confirmed COMPLETE — then the next cycle is
planned. (Decision records remain the design documentation for tasks
that need them; they do not pause the queue.)

- [x] **C1 · Promote R3 readability-selection into `runtime.evolve`.**
  (DR 0025, 2026-07-07: `readability_selection` keyword on the
  promoted `evolve` — verbatim `_readability.py` scorer mirror + drift
  guard, record-for-record lab parity incl. the precedence pin, the
  R3 A/B directional claim held on the promoted surface, contract
  probe, defaults byte-identical (every frozen pin unmodified). The
  session steers every era at blend 0.7: legibility tiers 1+2 earned
  live (elite mean 0.401 vs 0.244; 8 unlock facts vs 6) — and the
  live currency immediately measured legibility drifting DOWN across
  chained eras (0.401 → 0.182 → 0.014; bodies fragment 0.875 → 0.567
  inverse-component, symmetry 0.337 → 0.191) — recorded, not tuned
  away; a measured target for C4/C6.)
- [x] **C2 · The `campaign_store` lab (DR 0022's schema, proven).**
  (2026-07-07: schema v1 executable — all eight DR 0022 gates green as
  tests over a real chained campaign: byte-identical blob round-trips,
  derived-column pins, atomic one-transaction eras (rollback observed),
  founder-chain integrity, DETERMINISTIC REPLAY of a stored era into
  its own report, pointer-chain succession with zero copied rows,
  lossless `dr0022_v1_json_interim` migration, determinism scan; 11
  tests. Documented divergence: `founders.grid_json` nullable (the
  single-source rule — era_elite grids live in the predecessor's
  elites). Promotion-gate candidate registered; verdict
  `ready_for_package_design` — the status that precedes every port
  (the gate flips to promotion_ready when C3's package tests exist,
  per the seven prior modules' history).)
- [x] **C3 · Promote `mecha_engine.storage` (the ninth module).**
  (2026-07-07: verbatim byte-level port of the lab surface (the lab
  file was package-clean by construction); contract suite via the
  documented subprocess driver (10 tests incl. observed atomic
  rollback + boundary scan); lab-side parity pins BOTH directions
  (source byte-identity + row-for-row behavior over the real
  interim); the Keeper session and workshop server now derive
  `campaign_ledger.sqlite` through `ingest_session_artifacts` on
  every save — the migration path exercised every time. `storage`
  left the deferred set (imports test, scaffold gate note, matrix
  row); the promotion gate says PROMOTION_READY — 8 of 9 candidates,
  the ninth being the honestly-blocked manual-ratings gate. Deferred
  set is now `render` + `slip`.)
- [x] **C4 · The Covenant step — unlocks SPEND.** (2026-07-07:
  `covenant_budget` maps the DR 0021 table to spendable budget as a
  pure function of earned facts (palettes per niche tier; deliberation
  on the authority's REAL floor of 2 — found by the validator, not
  imagined; caps double per QD tier against the snapshotted base;
  blend +0.05/legibility tier, and the earned blend flows through
  `advance_campaign` so batch == incremental stays pinned);
  `apply_covenant_change` enforces budget + authority with named
  violations and atomicity; `POST /api/session/covenant` + the Keeper
  page's covenant panel. Deferred axes NAMED in the budget payload.
  Regenerated session: eras 1–2 run at the EARNED blend 0.8 —
  progression mechanically changes engine behavior mid-bloodline.)
- [x] **C5 · Per-era replay into the ledger.** (2026-07-07: every era
  records its best elite's life via the DR 0023 recorder at the era's
  own seed (honest label: a real recorded life, replayed post-era —
  threading record_frames through evolve is a noted future seam);
  ledger `replays` rows are pure functions of state (fixed path
  convention + sha256 over canonical JSON, file hash == row hash
  pinned); both stores ingest the rows (demo SQLite: replays 3);
  `GET /api/session/replay` + the Keeper page's per-era "▶ replay"
  in-page scrubber. The Review step consumes recorded engine truth.)
- [ ] **C6 · The repair-validity boundary study.** (Found during G2:
  aligned-but-invalid repairs exist; the crash is fixed, the QUESTION
  is not.) Measure the boundary honestly — frequency of
  lifecycle-invalid repairs across dropout regimes and cycle depths —
  and decide with evidence whether wound-site repair should guarantee
  a connected core (an engine contract evolution, lab-first with
  parity implications named) or the skip is the correct biology
  (creatures CAN be mortally wounded). Either verdict is a triad.

## Standing note

The identity constraint and DR 0017 govern: the engine is the
application, the game is its showcase. Real CuBFF weather remains
honestly blocked on the ingest gate (`awaiting_real_cubff_snapshots`) —
it unblocks with no code change when real exports are ingested (DR
0020), and is not a task. The rating system is the fallback;
`.depreciated/` is the owner's archive (ignore unless linked).

## Sources

- `audits/complete/02/TODO.md` (cycle 02, complete)
- `research/decision_records/0017-recalibration-engine-game-duality.md`
- `research/decision_records/0021-game-loop.md` (the loop C4/C5 deepen)
- `research/decision_records/0022-storage-module.md` (C2/C3's contract)
- `research/experiment_reports/2026-07-07-game-loop-session-runner.md` (C1, C6 named)
- `research/experiment_reports/2026-07-07-keeper-session-surface.md` (C4 named)
- `research/experiment_reports/2026-07-07-replay-recorder.md` (C5 named)
