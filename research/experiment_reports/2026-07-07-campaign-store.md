# Experiment Report: The Campaign Store (C2) — DR 0022's Schema, Executable

Date: 2026-07-07

## WHY

DR 0022 authorized the `mecha_engine.storage` target and fixed its
design, but the repo's law is lab-first: the module lands only when its
lab evidence exists and the promotion gate says `promotion_ready`. C2
is that evidence — the SQLite campaign ledger proven over REAL engine
output, with the shipped JSON interim guaranteed a lossless migration
so nothing G2/G4 recorded is stranded.

## WHAT

`labs/game_loop/campaign_store.py` (+ `test_campaign_store.py`, 11
tests): schema v1 verbatim from DR 0022 (`PRAGMA user_version = 1`,
foreign keys ON), `canonical_json` as the blob-authoritative encoding,
`record_campaign` / `record_era` (one era = one transaction: profile,
era row, elites, founder admissions, unlock facts — atomic or nothing),
`load_founder_pool` (niche-key order, per-era or latest),
`load_unlock_state` (predecessor pointer chain, never copied),
`campaign_history` (replay-sufficient), and `ingest_session_artifacts`
(the `dr0022_v1_json_interim` migration). Registered as a
promotion-gate candidate (`campaign_store` →
`packages/mecha_engine/src/mecha_engine/storage`).

**Documented divergence** (the spec-wins-with-documented-divergence
rule): `founders.grid_json` is NULLABLE where the DR draft said NOT
NULL — the shipped interim records founder ADMISSIONS, and an
`era_elite` founder's grid already lives in the predecessor era's
`elites` rows; duplicating it would break the single-source rule the
blob-authoritative design exists for. `workshop_release` founders
(whose grids exist nowhere else) carry `grid_json`.

## The eight DR 0022 gates — all green

| # | Gate | Pinned by |
| --- | --- | --- |
| 1 | Round-trip fidelity | stored `report_json` equals `canonical_json(report)` and re-canonicalizes byte-identically |
| 2 | Derived-column pin | every era/elite scalar column equals its blob field on real evolve output |
| 3 | Chain integrity | `load_founder_pool(era 1)` equals era 0's elites in niche order; stored admissions equal the engine's verbatim |
| 4 | Deterministic replay | a stored era's `(rng_seed, profile, weather, founder pool)` re-run through `run_era` reproduces its stored report EXACTLY |
| 5 | Unlock falsifiability | every stored fact's `metric_path` resolves in its cited era to `metric_value`; below-threshold fixtures earn nothing |
| 6 | Extinction & succession | `went_extinct` stored; an heir resolves the predecessor's facts through the pointer with ZERO copied rows |
| 7 | Interim migration | the live campaign's ledger ingests losslessly (reports, weather, seeds, profiles equal; row counts exact); foreign schemas refused |
| 8 | Determinism scan | no wall clock / randomness / uuid in the source; no absolute paths in any stored TEXT cell |

Plus: schema-version mismatches refuse to open; a bad unlock row rolls
back the WHOLE era (atomicity observed, not assumed).

## Verification

```powershell
PS> python -B -m unittest discover -s labs/game_loop -p "test_campaign_store.py"
Ran 11 tests in 2.152s
OK

PS> python -B labs/game_loop/campaign_store.py
{
  "artifact_id": "game_loop_campaign_store_stage0",
  "decision": "campaign_store_gates_green",
  "row_counts": {"campaigns": 1, "slip_profiles": 3, "eras": 3,
                 "elites": 22, "founders": 17, "unlocks": 8, "replays": 0}
}
```

## Decision

`campaign_store_gates_green` / adopt as lab evidence (C2 developed to
its description). C3 ports to `mecha_engine.storage` when the
promotion gate says `promotion_ready` over this artifact; the session
lab and workshop server then switch from the JSON interim through the
exercised migration path.

## Sources

- `research/decision_records/0022-storage-module.md`
- `research/algorithm_cards/campaign_store.md`
- `labs/game_loop/campaign_store.py`
- `labs/game_loop/test_campaign_store.py`
- `data/game_loop/campaign_store_stage0.json`
- `data/game_loop/campaign_store.sqlite`
- `data/game_loop/campaign_ledger.json` (the migrated interim)
- `labs/package_promotion/package_promotion_gate.py`
