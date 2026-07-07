"""C2: the eight DR 0022 gates, executable. Each test names its gate."""

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from campaign_store import (  # noqa: E402
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
from session_runner import (  # noqa: E402
    build_campaign_ledger,
    build_seed_grids,
    evaluate_unlocks,
    run_campaign,
    run_era,
    train_legibility_model,
    train_session_models,
)

BASE_SEED = 20260707
CAMPAIGN_KW = dict(
    weather_schedule=("calm", "storm"),
    base_seed=BASE_SEED,
    generations=2,
    population=3,
    damage_cycles=1,
    ticks=8,
)


class CampaignStoreGateTests(unittest.TestCase):
    """The DR 0022 gates over a REAL campaign (two chained eras through
    the promoted engine), stored via the lossless interim migration."""

    seeds: list[dict]

    @classmethod
    def setUpClass(cls):
        cls.seeds = build_seed_grids()
        cls.generation_model, cls.repair_model = train_session_models(
            cls.seeds, repair_epochs=20, rng_seed=BASE_SEED
        )
        cls.legibility_model = train_legibility_model()
        cls.models = dict(
            seed_grids=cls.seeds,
            generation_model=cls.generation_model,
            repair_model=cls.repair_model,
            legibility_model=cls.legibility_model,
        )
        cls.campaign = run_campaign(
            campaign_id="store_test", **cls.models, **CAMPAIGN_KW
        )
        cls.interim = build_campaign_ledger({"campaigns": [cls.campaign]})
        cls.conn = open_ledger(":memory:")
        cls.counts = ingest_session_artifacts(cls.conn, cls.interim)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    # -- schema ----------------------------------------------------------

    def test_schema_version_and_foreign_keys(self):
        self.assertEqual(
            SCHEMA_VERSION,
            self.conn.execute("PRAGMA user_version").fetchone()[0],
        )
        self.assertEqual(
            1, self.conn.execute("PRAGMA foreign_keys").fetchone()[0]
        )
        with self.assertRaises(sqlite3.IntegrityError):
            with self.conn:
                self.conn.execute(
                    "INSERT INTO eras (campaign_id, era_index, rng_seed,"
                    " slip_profile_id, report_json, decision_status,"
                    " filled_niches, coverage, qd_score,"
                    " max_lineage_generation, went_extinct)"
                    " VALUES ('ghost', 0, 1, 999, '{}', 'x', 0, 0, 0, 0, 0)"
                )

    # -- gate 1: round-trip fidelity ----------------------------------------

    def test_gate_1_blobs_round_trip_byte_identically(self):
        for era in self.campaign["eras"]:
            stored = self.conn.execute(
                "SELECT report_json FROM eras WHERE campaign_id = ? AND"
                " era_index = ?",
                (self.campaign["campaign_id"], era["era_index"]),
            ).fetchone()[0]
            self.assertEqual(canonical_json(era["report"]), stored)
            self.assertEqual(era["report"], json.loads(stored))
            self.assertEqual(
                canonical_json(json.loads(stored)), stored
            )  # re-canonicalization is byte-identical

    # -- gate 2: derived-column pin --------------------------------------------

    def test_gate_2_derived_columns_equal_their_blob_fields(self):
        for row in self.conn.execute(
            "SELECT report_json, decision_status, filled_niches, coverage,"
            " qd_score, max_lineage_generation FROM eras"
        ):
            report = json.loads(row[0])
            self.assertEqual(report["decision"]["status"], row[1])
            self.assertEqual(
                report["summary"]["archive"]["filled_niches"], row[2]
            )
            self.assertEqual(report["summary"]["archive"]["coverage"], row[3])
            self.assertEqual(report["summary"]["archive"]["qd_score"], row[4])
            self.assertEqual(
                report["summary"]["max_lineage_generation"], row[5]
            )
        for row in self.conn.execute(
            "SELECT grid_id, fitness, elite_json FROM elites"
        ):
            elite = json.loads(row[2])
            self.assertEqual(elite["grid_id"], row[0])
            self.assertEqual(elite["fitness"], row[1])

    # -- gate 3: chain integrity ---------------------------------------------

    def test_gate_3_founder_pool_equals_prior_elites_in_niche_order(self):
        pool = load_founder_pool(
            self.conn, self.campaign["campaign_id"], era_index=1
        )
        expected = [
            elite["grid"] for elite in self.campaign["eras"][0]["elites"]
        ]
        self.assertEqual(expected, pool)
        # And the stored admissions mirror the engine's verbatim.
        admitted = [
            row[0]
            for row in self.conn.execute(
                "SELECT grid_id FROM founders WHERE era_index = 1 AND"
                " admitted = 1 ORDER BY rowid"
            )
        ]
        self.assertEqual(
            self.campaign["eras"][1]["report"]["founders"]["admitted_ids"],
            admitted,
        )

    # -- gate 4: deterministic replay ---------------------------------------

    def test_gate_4_a_stored_era_replays_into_its_own_report(self):
        history = campaign_history(self.conn, self.campaign["campaign_id"])
        stored = history["eras"][1]
        replayed = run_era(
            era_index=1,
            weather=stored["weather"]["forecast"],
            seed_grids=self.seeds,
            slip_profile=stored["slip_profile"],
            generation_model=self.generation_model,
            repair_model=self.repair_model,
            legibility_model=self.legibility_model,
            founder_grids=load_founder_pool(
                self.conn, self.campaign["campaign_id"], era_index=1
            ),
            rng_seed=stored["rng_seed"],
            generations=2,
            population=3,
            damage_cycles=1,
            ticks=8,
            dropout_rate=0.2,
        )
        self.assertEqual(stored["report"], replayed["report"])

    # -- gate 5: unlock falsifiability ---------------------------------------

    def test_gate_5_stored_facts_resolve_and_fixtures_stay_falsifiable(self):
        from session_runner import _resolve_metric

        eras = {era["era_index"]: era for era in self.campaign["eras"]}
        state = load_unlock_state(self.conn, self.campaign["campaign_id"])
        self.assertTrue(state)
        for fact in state:
            value = _resolve_metric(
                eras[fact["earned_era_index"]], fact["metric_path"]
            )
            self.assertEqual(fact["metric_value"], value)
        # Fixture direction (met must unlock / unmet must not) stays
        # pinned by the session suite; here the STORED rows carry it.
        fixture = {
            "era_index": 9,
            "report": {
                "summary": {
                    "archive": {
                        "filled_niches": 3,
                        "coverage": 0.0,
                        "qd_score": 1.0,
                    },
                    "max_lineage_generation": 1,
                }
            },
            "derived": {
                "max_dropout_multiplier_survived": None,
                "elite_mean_learned_readability": 0.1,
            },
        }
        self.assertEqual([], evaluate_unlocks(fixture, []))

    # -- gate 6: extinction and succession ------------------------------------

    def test_gate_6_succession_resolves_without_copying(self):
        conn = open_ledger(":memory:")
        try:
            record_campaign(
                conn,
                {
                    "campaign_id": "doomed",
                    "keeper_label": "keeper",
                    "created_date": "2026-07-07",
                    "predecessor_campaign_id": None,
                    "status": "extinct",
                },
            )
            record_campaign(
                conn,
                {
                    "campaign_id": "heir",
                    "keeper_label": "keeper",
                    "created_date": "2026-07-07",
                    "predecessor_campaign_id": "doomed",
                    "status": "active",
                },
            )
            era = dict(self.interim["eras"][0])
            era["went_extinct"] = True
            era["elites"] = []
            record_era(
                conn,
                "doomed",
                era,
                self.campaign["slip_profile"],
                unlocks=[
                    {
                        "axis": "niche_mastery",
                        "tier": 1,
                        "earned_era_index": 0,
                        "metric_path": "report.summary.archive.filled_niches",
                        "metric_value": 5,
                        "threshold": 4,
                    }
                ],
            )
            stored_flag = conn.execute(
                "SELECT went_extinct FROM eras WHERE campaign_id = 'doomed'"
            ).fetchone()[0]
            self.assertEqual(1, stored_flag)
            heir_state = load_unlock_state(conn, "heir")
            self.assertEqual(1, len(heir_state))
            self.assertEqual("doomed", heir_state[0]["campaign_id"])
            self.assertEqual(
                0,
                conn.execute(
                    "SELECT COUNT(*) FROM unlocks WHERE campaign_id = 'heir'"
                ).fetchone()[0],
            )  # never copied
        finally:
            conn.close()

    # -- gate 7: interim migration ---------------------------------------------

    def test_gate_7_interim_migration_is_lossless(self):
        self.assertEqual(
            {
                "campaigns": 1,
                "slip_profiles": 2,
                "eras": 2,
                "elites": sum(
                    len(era["elites"]) for era in self.campaign["eras"]
                ),
                "founders": len(
                    self.campaign["eras"][1]["report"]["founders"][
                        "admitted_ids"
                    ]
                ),
                "unlocks": len(self.campaign["unlocks"]),
                "replays": 0,
            },
            self.counts,
        )
        history = campaign_history(self.conn, self.campaign["campaign_id"])
        for stored, live in zip(
            history["eras"], self.campaign["eras"], strict=True
        ):
            self.assertEqual(live["report"], stored["report"])
            self.assertEqual(live["weather"], stored["weather"])
            self.assertEqual(live["rng_seed"], stored["rng_seed"])
        self.assertEqual(
            self.campaign["slip_profile"],
            history["eras"][0]["slip_profile"],
        )
        with self.assertRaises(ValueError):
            ingest_session_artifacts(
                open_ledger(":memory:"), {"schema": "something_else"}
            )

    # -- gate 8: determinism scan -----------------------------------------------

    def test_gate_8_no_wall_clock_no_randomness_no_absolute_paths(self):
        source = (LAB_DIR / "campaign_store.py").read_text(encoding="utf-8")
        for forbidden in (
            "datetime.now",
            "time.time(",
            "time.strftime",
            "os.urandom",
            "random.",
            "uuid",
        ):
            self.assertNotIn(forbidden, source)
        # Stored strings carry no absolute paths (the L-08 rule): scan
        # every TEXT cell of the ingested ledger.
        for table, column in (
            ("eras", "report_json"),
            ("elites", "elite_json"),
            ("slip_profiles", "profile_json"),
        ):
            for row in self.conn.execute(
                f"SELECT {column} FROM {table}"  # noqa: S608 — fixed names
            ):
                self.assertNotIn("C:\\\\", row[0])
                self.assertNotIn("/Users/", row[0])

    # -- API safety ---------------------------------------------------------------

    def test_unsupported_schema_versions_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.sqlite"
            conn = sqlite3.connect(str(path))
            conn.execute("PRAGMA user_version = 99")
            conn.close()
            with self.assertRaises(ValueError):
                open_ledger(path)

    def test_era_transactions_are_atomic(self):
        conn = open_ledger(":memory:")
        try:
            record_campaign(
                conn,
                {
                    "campaign_id": "atomic",
                    "keeper_label": "keeper",
                    "created_date": "2026-07-07",
                    "predecessor_campaign_id": None,
                    "status": "active",
                },
            )
            era = dict(self.interim["eras"][0])
            era["elites"] = []
            bad_unlock = [{"axis": "not_an_axis", "tier": 1,
                           "earned_era_index": 0, "metric_path": "x",
                           "metric_value": 1, "threshold": 1}]
            with self.assertRaises(sqlite3.IntegrityError):
                record_era(
                    conn,
                    "atomic",
                    era,
                    self.campaign["slip_profile"],
                    unlocks=bad_unlock,
                )
            # The whole era rolled back — not a half-written ledger.
            for table in ("eras", "elites", "slip_profiles", "unlocks"):
                self.assertEqual(
                    0,
                    conn.execute(
                        f"SELECT COUNT(*) FROM {table}"  # noqa: S608
                    ).fetchone()[0],
                )
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
