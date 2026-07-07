# Experiment Report: `mecha_engine.storage` Promoted (C3) — The Ninth Module

Date: 2026-07-07

## WHY

DR 0022 authorized the target; C2 delivered the lab evidence (all eight
gates green over real engine output) and the promotion gate judged it
`ready_for_package_design`. C3 is the port itself, under the standing
rules every prior module obeyed: verbatim lab semantics, contract tests
through the package surface, lab-side parity pins, stdlib-only, no
`labs` imports, no `sys.path`.

## WHAT

- **The module** — `mecha_engine.storage` (`store.py` + `__init__.py`):
  the campaign-ledger surface extracted VERBATIM from
  `labs/game_loop/campaign_store.py` (the lab file was already
  package-clean by construction — pure stdlib, zero lab imports — so
  the port is a byte-level copy of the surface region).
- **Contract suite** — `tests/test_storage_contract.py` over
  `helpers/storage_contract_driver.py` (the documented subprocess
  mechanics; fixtures are synthetic interim ledgers built inside the
  driver): schema version + foreign keys, byte-identical round-trips,
  derived pins, niche-order founder pools, pointer-chain succession,
  replay-sufficient history, era atomicity with observed rollback,
  version/foreign-schema refusal, and the boundary scan.
- **Lab-side parity** — `labs/game_loop/test_package_storage_parity.py`
  pins BOTH directions: the package source contains the lab surface
  byte-for-byte (any unsynced edit fails loudly), and both stores
  ingest the real committed interim into row-for-row identical tables,
  histories, and founder pools.
- **The consumers switched** — `save_keeper_state` now derives the
  Keeper ledger as `campaign_ledger.sqlite` through the promoted
  module's `ingest_session_artifacts` on every save (the DR 0022
  migration path, exercised every time); the workshop server's session
  endpoints ride the same path. The demo JSON interim stays committed
  as evidence and as the parity fixture.
- **The bookkeeping** — `storage` left the deferred set
  (`test_package_imports.py`, the scaffold verification gate note); the
  traceability matrix gained its Storage row; the promotion gate now
  says **`promotion_ready`** for `campaign_store` (8 of 9 candidates;
  the ninth is the honestly-blocked manual-ratings gate).

## Verification

```powershell
PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
Ran 280 tests in 6.090s
OK

PS> python -B -m unittest discover -s labs/game_loop -p "test_*.py"
Ran 49 tests in 6.113s
OK

PS> python -B -m unittest discover -s workshop/tests -p "test_*.py"
OK    # the session endpoint test now reads the sqlite ledger

PS> python -B labs/package_promotion/package_promotion_gate.py
# campaign_store gate_status: promotion_ready
# summary: 9 candidates, 8 promotion_ready, 1 blocked (human ratings)
```

## Honest scope

- The Keeper's WORKING state remains `keeper_session.json` (the
  session's own format); the sqlite file is the derived DR 0022 ledger,
  rebuilt from it via the migration on every save. Making the ledger
  the primary state (reads served from SQL) is a C4+ concern once the
  Covenant step needs queryable budgets.
- The `replays` table stays empty until C5 wires per-era replay
  recording.

## Decision

Adopt — `mecha_engine` has its ninth module, gate-judged
`promotion_ready`, with the deferred set now `render` and `slip` (each
still requiring its own decision record). Next: C4 (the Covenant step).

## Sources

- `research/decision_records/0022-storage-module.md`
- `research/experiment_reports/2026-07-07-campaign-store.md` (the C2 evidence)
- `packages/mecha_engine/src/mecha_engine/storage/` (+ `store.py`)
- `packages/mecha_engine/tests/test_storage_contract.py` (+ driver)
- `labs/game_loop/test_package_storage_parity.py`
- `labs/game_loop/session_runner.py` (the switched consumer)
- `workshop/server/workshop_server.py`, `workshop/tests/test_workshop_server.py`
- `packages/mecha_engine/tests/test_package_imports.py`
- `research/package_specs/mecha_engine_scaffold_verification_gate.md`
- `research/package_specs/mecha_engine_contract_traceability_matrix.md`
- `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json`
