# Algorithm Card: Campaign Store (the DR 0022 SQLite ledger, lab-proven)

- **Name**: Campaign store — DR 0022 schema v1 as an executable stdlib
  `sqlite3` ledger with blob-authoritative storage and pointer-chain
  succession.
- **Purpose**: C2 — the `storage` module target's lab evidence: prove
  the campaign ledger design before any promotion (DR 0022's
  authorize-then-gate rule), with the shipped JSON interim guaranteed a
  lossless migration.
- **Mathematical basis**: storage as a pure ledger — no computation,
  only invariants: canonical-JSON idempotence
  (`canonical(parse(stored)) == stored`, byte-identical round-trips);
  derived columns as pinned projections of their blobs; era
  transactions as atomic units; unlock state as the union over the
  predecessor pointer chain (never materialized); replayability as the
  property that a stored era's `(rng_seed, profile, weather, founder
  pool)` regenerate its stored report exactly.
- **Inputs**: campaign/era records in the interim shape (verbatim
  evolve reports, six-field elite records, founder admissions, unlock
  facts) — from the session lab live or via
  `ingest_session_artifacts` over a `dr0022_v1_json_interim` ledger.
- **Outputs**: a versioned SQLite file (`PRAGMA user_version = 1`,
  foreign keys ON) plus read surfaces: `load_founder_pool` (niche-key
  order, per era or latest), `load_unlock_state` (pointer chain),
  `campaign_history` (replay-sufficient).
- **Strengths**: all eight DR 0022 gates run as tests; single-file
  transactional persistence with zero new dependencies; the store never
  computes game logic (facts in, facts out); migration exercised, not
  promised.
- **Weaknesses**: single-writer local ledger (by design — a companion
  game, not a service); the `replays` table waits on C5 to gain rows.
- **Failure modes**: a schema-version mismatch refuses to open rather
  than guessing; a bad row anywhere in an era rolls the WHOLE era back
  (atomicity pinned by test); a non-interim payload is rejected by
  schema id.
- **Integration risk**: low — pure stdlib, no engine imports at all;
  the C3 port to `mecha_engine.storage` is verbatim by construction.
- **License status**: original stdlib implementation.
- **Prototype result**: the committed demo ledger ingests to 3 eras /
  22 elites / 17 founders / 8 unlocks with every gate green; a stored
  era replays byte-for-byte into its own report through the promoted
  engine; 11/11 tests. Documented divergence from the DR draft:
  `founders.grid_json` NULLABLE (era_elite founder grids live in the
  predecessor era's elites — the single-source rule).
- **Decision**: adopt as lab evidence; C3 ports when the promotion
  gate says `promotion_ready`.
- **Go-No-Go gate**: the eight DR 0022 gates (round-trip fidelity,
  derived-column pin, chain integrity, deterministic replay, unlock
  falsifiability, extinction/succession, interim migration,
  determinism scan) plus schema-version refusal and era atomicity.

## Sources

- `research/decision_records/0022-storage-module.md`
- `research/experiment_reports/2026-07-07-campaign-store.md`
- `labs/game_loop/campaign_store.py` (+ `test_campaign_store.py`)
- `data/game_loop/campaign_store_stage0.json` (+ `campaign_store.sqlite`)
- `labs/package_promotion/package_promotion_gate.py` (the `campaign_store` candidate)
