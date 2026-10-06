"""mecha_engine.storage — the campaign ledger (decision record 0022).

The ninth promoted module: DR 0022's SQLite schema v2 (with unchanged v1 tables) as a deterministic,
transactional store of engine truth. Contract sources:

- research/decision_records/0022-storage-module.md (the design and the
  eight gates)
- labs/game_loop/campaign_store.py (the verbatim behavior source, pinned
  by the lab-side parity test
  ``labs/game_loop/test_package_storage_parity.py``)
- research/experiment_reports/2026-07-07-campaign-store.md (the lab
  evidence the promotion gate judged)

Storage never computes game logic: unlock facts, era reports, elite
records, and founder admissions are stored VERBATIM (canonical JSON,
blob-authoritative; derived scalar columns exist purely for query and
are pinned equal to their blobs), one era commits atomically or not at
all, and succession resolves unlock state through the predecessor
pointer at read time — rows are never copied. Stdlib ``sqlite3`` only;
ids, dates, and seeds are caller-supplied (no wall clock, no os
randomness).
"""

from mecha_engine.storage.store import (
    INTERIM_SCHEMA,
    SCHEMA_VERSION,
    SUPPORTED_READ_SCHEMA_VERSIONS,
    load_era_execution,
    validate_execution,
    campaign_history,
    canonical_json,
    ingest_session_artifacts,
    load_era_elites,
    load_era_breeders,
    load_founder_pool,
    load_replay_rows,
    load_unlock_state,
    open_ledger,
    record_campaign,
    record_era,
    record_replay,
)

__all__ = [
    "INTERIM_SCHEMA",
    "SCHEMA_VERSION",
    "SUPPORTED_READ_SCHEMA_VERSIONS",
    "load_era_execution",
    "validate_execution",
    "campaign_history",
    "canonical_json",
    "ingest_session_artifacts",
    "load_era_elites",
    "load_era_breeders",
    "load_founder_pool",
    "load_replay_rows",
    "load_unlock_state",
    "open_ledger",
    "record_campaign",
    "record_era",
    "record_replay",
]
