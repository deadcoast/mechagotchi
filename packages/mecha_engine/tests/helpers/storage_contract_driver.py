"""Storage contract probe driver executed against the package surface.

Traceability: research/decision_records/0022-storage-module.md (the
schema and the eight gates) and
research/experiment_reports/2026-07-07-campaign-store.md.
``tests/test_storage_contract.py`` launches this script in a subprocess
whose PYTHONPATH points at the package ``src`` directory (the same
documented import mechanics as every other contract suite), so every
probe exercises ``mecha_engine.storage`` only — never repository-root
or research lab modules.

Fixtures are SYNTHETIC interim ledgers built right here (the contract
is the store's behavior over the ``dr0022_v1_json_interim`` shape; the
real-engine-output evidence is the lab suite and the lab-side parity
pin). The driver prints a single JSON report on stdout.
"""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
from pathlib import Path

from mecha_engine.storage import (
    SCHEMA_VERSION,
    campaign_history,
    canonical_json,
    ingest_session_artifacts,
    load_founder_pool,
    load_unlock_state,
    open_ledger,
    record_campaign,
    record_era,
)


def _report(era_index: int, niches: int) -> dict:
    return {
        "lab_id": "fixture",
        "rng_seed": 100 + era_index,
        "generations_requested": 2,
        "generations": [],
        "summary": {
            "max_lineage_generation": era_index + 1,
            "archive": {
                "filled_niches": niches,
                "coverage": round(niches / 100.0, 6),
                "qd_score": round(niches * 1.5, 6),
            },
        },
        "decision": {"status": "fixture_ok"},
    }


def _elite(era_index: int, index: int) -> dict:
    grid = {
        "grid_id": f"e{era_index}_{index}",
        "cells": [{"x": index, "y": era_index, "role": "body"}],
    }
    return {
        "campaign_id": "fixture_campaign",
        "era_index": era_index,
        "niche_key": f"n{index:02d}",
        "grid_id": grid["grid_id"],
        "fitness": round(0.5 + index / 10.0, 6),
        "elite": {
            "grid_id": grid["grid_id"],
            "grid": grid,
            "descriptor": {"key": f"n{index:02d}"},
            "fitness": round(0.5 + index / 10.0, 6),
            "fitness_components": {},
            "validation": {"ok": True},
            "provenance": {"provided": False, "record": None},
        },
    }


def build_fixture_interim() -> dict:
    return {
        "ledger_id": "fixture",
        "schema": "dr0022_v1_json_interim",
        "campaigns": [
            {
                "campaign_id": "fixture_campaign",
                "keeper_label": "keeper",
                "created_date": "2026-07-07",
                "predecessor_campaign_id": None,
                "status": "active",
            }
        ],
        "eras": [
            {
                "campaign_id": "fixture_campaign",
                "era_index": index,
                "rng_seed": 100 + index,
                "slip_profile": {
                    "profile_id": "fixture_profile",
                    "slip_version": "0.1.0",
                },
                "weather": {"forecast": "calm", "snapshot_ids": []},
                "report": _report(index, niches=4 + index),
                "went_extinct": False,
            }
            for index in (0, 1)
        ],
        "elites": [
            _elite(era_index, index)
            for era_index in (0, 1)
            for index in (0, 1, 2)
        ],
        "founders": [
            {
                "campaign_id": "fixture_campaign",
                "era_index": 1,
                "grid_id": f"e0_{index}",
                "source": "era_elite",
                "admitted": True,
                "rejection_errors": None,
            }
            for index in (0, 1, 2)
        ],
        "unlocks": [
            {
                "campaign_id": "fixture_campaign",
                "axis": "niche_mastery",
                "tier": 1,
                "earned_era_index": 0,
                "metric_path": "report.summary.archive.filled_niches",
                "metric_value": 4,
                "threshold": 4,
            }
        ],
    }


def main() -> None:
    interim = build_fixture_interim()
    conn = open_ledger(":memory:")
    counts = ingest_session_artifacts(conn, interim)

    # Round-trip fidelity.
    stored_report = conn.execute(
        "SELECT report_json FROM eras WHERE era_index = 0"
    ).fetchone()[0]
    round_trip = (
        stored_report == canonical_json(interim["eras"][0]["report"])
        and canonical_json(json.loads(stored_report)) == stored_report
    )

    # Derived pins.
    derived_ok = all(
        row[1] == json.loads(row[0])["summary"]["archive"]["filled_niches"]
        for row in conn.execute("SELECT report_json, filled_niches FROM eras")
    )

    # Founder pool ordering.
    pool = load_founder_pool(conn, "fixture_campaign", era_index=1)
    pool_ok = [grid["grid_id"] for grid in pool] == ["e0_0", "e0_1", "e0_2"]

    # Succession chain.
    record_campaign(
        conn,
        {
            "campaign_id": "heir",
            "keeper_label": "keeper",
            "created_date": "2026-07-07",
            "predecessor_campaign_id": "fixture_campaign",
            "status": "active",
        },
    )
    heir_state = load_unlock_state(conn, "heir")
    chain_ok = len(heir_state) == 1 and heir_state[0][
        "campaign_id"
    ] == "fixture_campaign"

    # History replay-sufficiency.
    history = campaign_history(conn, "fixture_campaign")
    history_ok = (
        len(history["eras"]) == 2
        and history["eras"][1]["report"] == interim["eras"][1]["report"]
        and history["eras"][0]["slip_profile"]
        == interim["eras"][0]["slip_profile"]
    )

    # Atomicity: a bad unlock rolls the whole era back.
    atomic_conn = open_ledger(":memory:")
    record_campaign(atomic_conn, interim["campaigns"][0])
    atomic_raised = False
    try:
        record_era(
            atomic_conn,
            "fixture_campaign",
            {
                "era_index": 0,
                "rng_seed": 1,
                "weather": None,
                "report": _report(0, 4),
                "went_extinct": False,
                "elites": [],
            },
            {"profile_id": "p", "slip_version": "0.1.0"},
            unlocks=[
                {
                    "axis": "not_an_axis",
                    "tier": 1,
                    "earned_era_index": 0,
                    "metric_path": "x",
                    "metric_value": 1,
                    "threshold": 1,
                }
            ],
        )
    except sqlite3.IntegrityError:
        atomic_raised = True
    atomic_ok = atomic_raised and all(
        atomic_conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]  # noqa: S608
        == 0
        for table in ("eras", "slip_profiles", "unlocks")
    )

    # Version handling.
    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "bad.sqlite"
        raw = sqlite3.connect(str(bad))
        raw.execute("PRAGMA user_version = 99")
        raw.close()
        try:
            open_ledger(bad)
            version_refused = False
        except ValueError:
            version_refused = True

    # Foreign schemas refused.
    try:
        ingest_session_artifacts(open_ledger(":memory:"), {"schema": "x"})
        foreign_refused = False
    except ValueError:
        foreign_refused = True

    json.dump(
        {
            "schema_version": SCHEMA_VERSION,
            "counts": counts,
            "round_trip_byte_identical": round_trip,
            "derived_columns_pinned": derived_ok,
            "founder_pool_niche_order": pool_ok,
            "succession_chain_resolves": chain_ok,
            "history_replay_sufficient": history_ok,
            "era_atomicity_holds": atomic_ok,
            "bad_version_refused": version_refused,
            "foreign_schema_refused": foreign_refused,
        },
        sys.stdout,
    )


if __name__ == "__main__":
    main()
