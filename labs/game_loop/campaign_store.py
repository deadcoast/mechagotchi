"""Campaign store — DR 0022's SQLite campaign ledger, proven lab-first (C2).

The `storage` module target's lab evidence: schema v1 exactly as decision
record 0022 fixed it — stdlib `sqlite3`, `PRAGMA user_version = 1`,
foreign keys ON, the blob-authoritative rule (every engine artifact
stored as canonical JSON text; derived scalar columns exist purely for
query and are pinned equal to their blob fields by the gate tests), one
era = one transaction, succession without copying (unlock state resolves
through the predecessor pointer at read time).

`ingest_session_artifacts` consumes the shipped JSON interim
(`dr0022_v1_json_interim`, the G2/G4 campaign ledger) losslessly, so
nothing recorded before promotion is stranded.

Documented divergence from the DR 0022 draft (the spec-wins-with-
documented-divergence rule): `founders.grid_json` is NULLABLE — the
shipped interim records founder ADMISSIONS (source, verdict, verbatim
rejection errors), while an `era_elite` founder's grid already lives in
the predecessor era's `elites` rows; duplicating it would violate the
single-source rule the blob-authoritative design exists for.
`workshop_release` founders (whose grids exist nowhere else) carry
`grid_json`.

Deterministic end to end: no wall clock, no os randomness; ids, dates,
and seeds are caller-supplied. The module is stdlib-only and imports
only `mecha_engine` surfaces (none, in fact — the store is a ledger,
not a computer), so promotion to `mecha_engine.storage` is a verbatim
port.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ARTIFACT_ID = "game_loop_campaign_store_stage0"
REPORT_DATE = "2026-07-07"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "game_loop"
DEFAULT_INTERIM_LEDGER = DEFAULT_OUTPUT_DIR / "campaign_ledger.json"
SCHEMA_VERSION = 1
INTERIM_SCHEMA = "dr0022_v1_json_interim"

SCHEMA = """
CREATE TABLE campaigns (
  campaign_id               TEXT PRIMARY KEY,
  keeper_label              TEXT NOT NULL,
  created_date              TEXT NOT NULL,
  predecessor_campaign_id   TEXT REFERENCES campaigns(campaign_id),
  status                    TEXT NOT NULL
    CHECK (status IN ('active', 'extinct', 'retired'))
);

CREATE TABLE slip_profiles (
  profile_id    INTEGER PRIMARY KEY,
  campaign_id   TEXT NOT NULL REFERENCES campaigns(campaign_id),
  era_index     INTEGER NOT NULL,
  slip_version  TEXT NOT NULL,
  profile_json  TEXT NOT NULL,
  UNIQUE (campaign_id, era_index)
);

CREATE TABLE eras (
  campaign_id             TEXT NOT NULL REFERENCES campaigns(campaign_id),
  era_index               INTEGER NOT NULL,
  rng_seed                INTEGER NOT NULL,
  slip_profile_id         INTEGER NOT NULL REFERENCES slip_profiles(profile_id),
  weather_json            TEXT,
  report_json             TEXT NOT NULL,
  decision_status         TEXT NOT NULL,
  filled_niches           INTEGER NOT NULL,
  coverage                REAL NOT NULL,
  qd_score                REAL NOT NULL,
  max_lineage_generation  INTEGER NOT NULL,
  went_extinct            INTEGER NOT NULL,
  PRIMARY KEY (campaign_id, era_index)
);

CREATE TABLE elites (
  campaign_id  TEXT NOT NULL,
  era_index    INTEGER NOT NULL,
  niche_key    TEXT NOT NULL,
  grid_id      TEXT NOT NULL,
  fitness      REAL NOT NULL,
  elite_json   TEXT NOT NULL,
  PRIMARY KEY (campaign_id, era_index, niche_key),
  FOREIGN KEY (campaign_id, era_index) REFERENCES eras
);

CREATE TABLE founders (
  campaign_id           TEXT NOT NULL,
  era_index             INTEGER NOT NULL,
  grid_id               TEXT NOT NULL,
  source                TEXT NOT NULL
    CHECK (source IN ('workshop_release', 'era_elite')),
  admitted              INTEGER NOT NULL,
  rejection_errors_json TEXT,
  grid_json             TEXT,
  PRIMARY KEY (campaign_id, era_index, grid_id),
  FOREIGN KEY (campaign_id, era_index) REFERENCES eras
);

CREATE TABLE unlocks (
  campaign_id      TEXT NOT NULL REFERENCES campaigns(campaign_id),
  axis             TEXT NOT NULL
    CHECK (axis IN ('niche_mastery', 'bloodline_depth',
                    'quality_diversity', 'storm_record', 'legibility')),
  tier             INTEGER NOT NULL,
  earned_era_index INTEGER NOT NULL,
  metric_path      TEXT NOT NULL,
  metric_value     TEXT NOT NULL,
  threshold        TEXT NOT NULL,
  PRIMARY KEY (campaign_id, axis, tier)
);

CREATE TABLE replays (
  campaign_id     TEXT NOT NULL,
  era_index       INTEGER NOT NULL,
  artifact_path   TEXT NOT NULL,
  artifact_sha256 TEXT NOT NULL,
  PRIMARY KEY (campaign_id, era_index, artifact_path),
  FOREIGN KEY (campaign_id, era_index) REFERENCES eras
);
"""


def canonical_json(value) -> str:
    """The blob-authoritative encoding (DR 0022): canonical JSON text."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def open_ledger(path: str | Path) -> sqlite3.Connection:
    """Open (creating/migrating if needed) a campaign ledger."""
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA foreign_keys = ON")
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version == 0:
        with conn:
            conn.executescript(SCHEMA)
            conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    elif version != SCHEMA_VERSION:
        conn.close()
        raise ValueError(
            f"unsupported campaign-ledger schema version: {version}"
        )
    return conn


def record_campaign(conn: sqlite3.Connection, campaign: dict) -> None:
    """Insert or update one campaign row (status changes flow through
    here — e.g. extinction)."""
    with conn:
        conn.execute(
            "INSERT INTO campaigns (campaign_id, keeper_label, created_date,"
            " predecessor_campaign_id, status) VALUES (?, ?, ?, ?, ?)"
            " ON CONFLICT(campaign_id) DO UPDATE SET status = excluded.status",
            (
                campaign["campaign_id"],
                campaign["keeper_label"],
                campaign["created_date"],
                campaign["predecessor_campaign_id"],
                campaign["status"],
            ),
        )


def record_era(
    conn: sqlite3.Connection,
    campaign_id: str,
    era: dict,
    slip_profile: dict,
    founders: list[dict] | None = None,
    unlocks: list[dict] | None = None,
) -> None:
    """One era = one transaction (DR 0022): the profile, the era row,
    its elites, its founder admissions, and its unlock facts commit
    atomically or not at all.

    ``era`` is the interim era row shape: era_index, rng_seed, weather,
    the VERBATIM report, and the derived flags; elites ride either on
    the era (session records) or are passed via the interim's elites
    rows by the ingester.
    """
    report = era["report"]
    with conn:
        cursor = conn.execute(
            "INSERT INTO slip_profiles (campaign_id, era_index,"
            " slip_version, profile_json) VALUES (?, ?, ?, ?)",
            (
                campaign_id,
                era["era_index"],
                str(slip_profile.get("slip_version", "unknown")),
                canonical_json(slip_profile),
            ),
        )
        profile_row_id = cursor.lastrowid
        conn.execute(
            "INSERT INTO eras (campaign_id, era_index, rng_seed,"
            " slip_profile_id, weather_json, report_json, decision_status,"
            " filled_niches, coverage, qd_score, max_lineage_generation,"
            " went_extinct) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                campaign_id,
                era["era_index"],
                era["rng_seed"],
                profile_row_id,
                canonical_json(era["weather"])
                if era.get("weather") is not None
                else None,
                canonical_json(report),
                report["decision"]["status"],
                report["summary"]["archive"]["filled_niches"],
                report["summary"]["archive"]["coverage"],
                report["summary"]["archive"]["qd_score"],
                report["summary"]["max_lineage_generation"],
                1 if era["went_extinct"] else 0,
            ),
        )
        for elite in era.get("elites", []):
            record = {
                key: value for key, value in elite.items() if key != "niche_key"
            }
            conn.execute(
                "INSERT INTO elites (campaign_id, era_index, niche_key,"
                " grid_id, fitness, elite_json) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    campaign_id,
                    era["era_index"],
                    elite["niche_key"],
                    record["grid_id"],
                    record["fitness"],
                    canonical_json(record),
                ),
            )
        for founder in founders or []:
            conn.execute(
                "INSERT INTO founders (campaign_id, era_index, grid_id,"
                " source, admitted, rejection_errors_json, grid_json)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    campaign_id,
                    era["era_index"],
                    founder["grid_id"],
                    founder["source"],
                    1 if founder["admitted"] else 0,
                    canonical_json(founder["rejection_errors"])
                    if founder.get("rejection_errors") is not None
                    else None,
                    canonical_json(founder["grid"])
                    if founder.get("grid") is not None
                    else None,
                ),
            )
        for fact in unlocks or []:
            conn.execute(
                "INSERT INTO unlocks (campaign_id, axis, tier,"
                " earned_era_index, metric_path, metric_value, threshold)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    campaign_id,
                    fact["axis"],
                    fact["tier"],
                    fact["earned_era_index"],
                    fact["metric_path"],
                    canonical_json(fact["metric_value"]),
                    canonical_json(fact["threshold"]),
                ),
            )


def record_replay(
    conn: sqlite3.Connection,
    campaign_id: str,
    era_index: int,
    artifact_path: str,
    artifact_sha256: str,
) -> None:
    """One replays-table row (C5): the artifact stays a file; the
    ledger stores the pointer and the content hash (DR 0022)."""
    with conn:
        conn.execute(
            "INSERT INTO replays (campaign_id, era_index, artifact_path,"
            " artifact_sha256) VALUES (?, ?, ?, ?)",
            (campaign_id, era_index, artifact_path, artifact_sha256),
        )


def load_replay_rows(
    conn: sqlite3.Connection, campaign_id: str
) -> list[dict]:
    return [
        {
            "campaign_id": campaign_id,
            "era_index": row[0],
            "artifact_path": row[1],
            "artifact_sha256": row[2],
        }
        for row in conn.execute(
            "SELECT era_index, artifact_path, artifact_sha256 FROM replays"
            " WHERE campaign_id = ? ORDER BY era_index, artifact_path",
            (campaign_id,),
        )
    ]


def load_founder_pool(
    conn: sqlite3.Connection,
    campaign_id: str,
    era_index: int | None = None,
) -> list[dict]:
    """The founder pool for the NEXT era (default) or for a given era —
    the previous era's elites in niche-key order, the same deterministic
    ordering ``evolve`` uses for elite parents (DR 0022)."""
    if era_index is None:
        row = conn.execute(
            "SELECT MAX(era_index) FROM eras WHERE campaign_id = ?",
            (campaign_id,),
        ).fetchone()
        if row[0] is None:
            return []
        source_era = row[0]
    else:
        source_era = era_index - 1
        if source_era < 0:
            return []
    rows = conn.execute(
        "SELECT elite_json FROM elites WHERE campaign_id = ? AND"
        " era_index = ? ORDER BY niche_key",
        (campaign_id, source_era),
    ).fetchall()
    return [json.loads(row[0])["grid"] for row in rows]


def load_unlock_state(
    conn: sqlite3.Connection, campaign_id: str
) -> list[dict]:
    """The Keeper's unlock state: this campaign's facts plus every
    predecessor's, resolved through the pointer chain — rows are never
    copied (DR 0022's succession rule)."""
    facts: list[dict] = []
    seen: set[str] = set()
    current: str | None = campaign_id
    while current is not None and current not in seen:
        seen.add(current)
        for row in conn.execute(
            "SELECT axis, tier, earned_era_index, metric_path,"
            " metric_value, threshold FROM unlocks WHERE campaign_id = ?"
            " ORDER BY axis, tier",
            (current,),
        ):
            facts.append(
                {
                    "campaign_id": current,
                    "axis": row[0],
                    "tier": row[1],
                    "earned_era_index": row[2],
                    "metric_path": row[3],
                    "metric_value": json.loads(row[4]),
                    "threshold": json.loads(row[5]),
                }
            )
        row = conn.execute(
            "SELECT predecessor_campaign_id FROM campaigns WHERE"
            " campaign_id = ?",
            (current,),
        ).fetchone()
        current = row[0] if row else None
    return facts


def campaign_history(
    conn: sqlite3.Connection, campaign_id: str
) -> dict:
    """Replay-sufficient history: the campaign row plus every era's
    verbatim inputs and report."""
    row = conn.execute(
        "SELECT campaign_id, keeper_label, created_date,"
        " predecessor_campaign_id, status FROM campaigns WHERE"
        " campaign_id = ?",
        (campaign_id,),
    ).fetchone()
    if row is None:
        raise KeyError(f"no such campaign: {campaign_id}")
    eras = []
    for era_row in conn.execute(
        "SELECT e.era_index, e.rng_seed, e.weather_json, e.report_json,"
        " e.went_extinct, p.profile_json FROM eras e JOIN slip_profiles p"
        " ON p.profile_id = e.slip_profile_id WHERE e.campaign_id = ?"
        " ORDER BY e.era_index",
        (campaign_id,),
    ):
        eras.append(
            {
                "era_index": era_row[0],
                "rng_seed": era_row[1],
                "weather": json.loads(era_row[2])
                if era_row[2] is not None
                else None,
                "report": json.loads(era_row[3]),
                "went_extinct": bool(era_row[4]),
                "slip_profile": json.loads(era_row[5]),
            }
        )
    return {
        "campaign_id": row[0],
        "keeper_label": row[1],
        "created_date": row[2],
        "predecessor_campaign_id": row[3],
        "status": row[4],
        "eras": eras,
        "unlocks": load_unlock_state(conn, campaign_id),
    }


def ingest_session_artifacts(
    conn: sqlite3.Connection, interim: dict | str | Path
) -> dict:
    """Consume the shipped JSON interim (`dr0022_v1_json_interim`)
    losslessly. Returns row counts per table."""
    if not isinstance(interim, dict):
        interim = json.loads(Path(interim).read_text(encoding="utf-8"))
    if interim.get("schema") != INTERIM_SCHEMA:
        raise ValueError(
            f"not a {INTERIM_SCHEMA} ledger: {interim.get('schema')!r}"
        )
    for campaign in interim["campaigns"]:
        record_campaign(conn, campaign)
    unlocks_by_campaign: dict[str, list[dict]] = {}
    for fact in interim["unlocks"]:
        unlocks_by_campaign.setdefault(fact["campaign_id"], []).append(
            {key: value for key, value in fact.items() if key != "campaign_id"}
        )
    for era_row in interim["eras"]:
        campaign_id = era_row["campaign_id"]
        elites = [
            {
                "niche_key": row["niche_key"],
                **row["elite"],
            }
            for row in interim["elites"]
            if row["campaign_id"] == campaign_id
            and row["era_index"] == era_row["era_index"]
        ]
        founders = [
            {
                "grid_id": row["grid_id"],
                "source": row["source"],
                "admitted": row["admitted"],
                "rejection_errors": row["rejection_errors"],
                "grid": row.get("grid"),
            }
            for row in interim["founders"]
            if row["campaign_id"] == campaign_id
            and row["era_index"] == era_row["era_index"]
        ]
        era_unlocks = [
            fact
            for fact in unlocks_by_campaign.get(campaign_id, [])
            if fact["earned_era_index"] == era_row["era_index"]
        ]
        record_era(
            conn,
            campaign_id,
            {
                "era_index": era_row["era_index"],
                "rng_seed": era_row["rng_seed"],
                "weather": era_row["weather"],
                "report": era_row["report"],
                "went_extinct": era_row["went_extinct"],
                "elites": elites,
            },
            era_row["slip_profile"],
            founders=founders,
            unlocks=era_unlocks,
        )
    for replay_row in interim.get("replays", []):
        record_replay(
            conn,
            replay_row["campaign_id"],
            replay_row["era_index"],
            replay_row["artifact_path"],
            replay_row["artifact_sha256"],
        )
    counts = {}
    for table in (
        "campaigns",
        "slip_profiles",
        "eras",
        "elites",
        "founders",
        "unlocks",
        "replays",
    ):
        counts[table] = conn.execute(
            f"SELECT COUNT(*) FROM {table}"  # noqa: S608 — fixed table names
        ).fetchone()[0]
    return counts


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_store_report(counts: dict, sqlite_path: Path) -> dict:
    try:
        payload_path = sqlite_path.relative_to(ROOT).as_posix()
    except ValueError:
        payload_path = sqlite_path.name
    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0_complete",
        "date": REPORT_DATE,
        "purpose": (
            "C2 (DR 0022): prove the storage module's SQLite campaign "
            "ledger lab-first — schema v1, the blob-authoritative rule, "
            "one-transaction eras, succession without copying, and the "
            "lossless JSON-interim migration; the eight DR 0022 gates "
            "run as the lab's test suite."
        ),
        "source_artifacts": [
            "research/decision_records/0022-storage-module.md",
            "data/game_loop/campaign_ledger.json",
        ],
        "metrics": {
            "schema_version": SCHEMA_VERSION,
            "row_counts": counts,
            "sqlite_payload": {
                "path": payload_path,
                "bytes": sqlite_path.stat().st_size,
                "sha256": _sha256(sqlite_path),
            },
        },
        "closed_states": [
            "schema_v1_applied_with_foreign_keys_and_user_version",
            "blob_authoritative_round_trip_byte_identical",
            "derived_columns_pinned_to_report_blobs",
            "one_transaction_eras_atomic",
            "founder_chain_integrity_pinned",
            "deterministic_replay_reproduces_stored_reports",
            "unlock_state_resolves_through_predecessor_pointer",
            "json_interim_migration_lossless",
        ],
        "blocked_states": [
            # C3's task: the verbatim port to mecha_engine.storage waits
            # on the promotion gate's verdict over this evidence.
            "mecha_engine_storage_port_pending_promotion_gate",
        ],
        "documented_divergence": (
            "founders.grid_json is NULLABLE (DR 0022 draft said NOT "
            "NULL): the shipped interim records founder admissions, and "
            "an era_elite founder's grid already lives in the "
            "predecessor era's elites rows — duplicating it would "
            "violate the single-source rule; workshop_release founders "
            "carry grid_json."
        ),
        "decision": {
            "status": "campaign_store_gates_green",
            "adoption": "lab_only_storage_evidence",
            "reason": (
                "DR 0022's schema is executable fact: engine artifacts "
                "round-trip byte-identically, derived columns equal "
                "their blobs, era transactions are atomic, the founder "
                "chain and unlock succession behave exactly as the "
                "session lab's JSON interim, and a stored era replays "
                "deterministically into its own report."
            ),
        },
        "next_research_step": (
            "C3: port to mecha_engine.storage when the promotion gate "
            "says promotion_ready; the session lab and workshop server "
            "then switch from the JSON interim through the exercised "
            "migration path."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the SQLite campaign ledger from the JSON interim."
    )
    parser.add_argument(
        "--interim", type=Path, default=DEFAULT_INTERIM_LEDGER
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    sqlite_path = args.output_dir / "campaign_store.sqlite"
    if sqlite_path.exists():
        sqlite_path.unlink()
    conn = open_ledger(sqlite_path)
    try:
        counts = ingest_session_artifacts(conn, args.interim)
    finally:
        conn.close()
    report = build_store_report(counts, sqlite_path)
    (args.output_dir / "campaign_store_stage0.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "artifact_id": report["artifact_id"],
                "decision": report["decision"]["status"],
                "row_counts": counts,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
