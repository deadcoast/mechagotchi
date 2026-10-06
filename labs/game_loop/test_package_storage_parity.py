"""Lab-side parity pin: ``mecha_engine.storage`` mirrors the lab store
verbatim (C3, decision record 0022 — the promotion's drift guard).

Two pins: (1) SOURCE — the package's storage surface is byte-for-byte
the lab file's surface region, so any edit to either side without a
resync fails loudly; (2) BEHAVIOR — both stores ingest the same real
committed interim ledger and every table dumps identically."""

import importlib
import sys
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
for path in [LAB_DIR, PACKAGE_SRC]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import campaign_store as lab_store  # noqa: E402

package_store = importlib.import_module("mecha_engine.storage.store")

INTERIM_PATH = ROOT / "data" / "game_loop" / "campaign_ledger.json"
TABLES = (
    "campaigns",
    "slip_profiles",
    "eras",
    "elites",
    "founders",
    "unlocks",
    "replays",
    "execution_blobs",
    "era_executions",
    "founder_occurrences",
)


def _dump(conn) -> dict:
    dump = {}
    for table in TABLES:
        dump[table] = conn.execute(
            f"SELECT * FROM {table} ORDER BY rowid"  # noqa: S608 — fixed names
        ).fetchall()
    return dump


class StorageSourceParityTests(unittest.TestCase):
    def test_package_surface_is_the_lab_surface_verbatim(self):
        lab_source = (LAB_DIR / "campaign_store.py").read_text(
            encoding="utf-8"
        )
        surface = lab_source[
            lab_source.index("SCHEMA_VERSION =") : lab_source.index(
                "def _sha256"
            )
        ].rstrip()
        package_source = (
            PACKAGE_SRC / "mecha_engine" / "storage" / "store.py"
        ).read_text(encoding="utf-8")
        self.assertIn(surface, package_source)


class StorageBehaviorParityTests(unittest.TestCase):
    def test_execution_rows_and_loaded_bundles_match_exactly(self):
        from test_execution_store import probes
        campaign, profile, era, bundle = probes.fixture()
        connections = [store.open_ledger(":memory:") for store in (lab_store, package_store)]
        try:
            for store, conn in zip((lab_store, package_store), connections, strict=True):
                store.record_campaign(conn, campaign)
                store.record_era(conn, campaign["campaign_id"], era, profile, execution=bundle)
                self.assertEqual(bundle, store.load_era_execution(conn, campaign["campaign_id"], 0))
            self.assertEqual(_dump(connections[0]), _dump(connections[1]))
        finally:
            for conn in connections:
                conn.close()

    def test_living_cohort_and_complete_continuation_match_exactly(self):
        from test_population_store import probes
        campaign, profile, era, bundle = probes.fixture(cared=True)
        later, continuation = probes.continuation(era, bundle, cared=True)
        connections = [store.open_ledger(":memory:") for store in (lab_store, package_store)]
        try:
            for store, conn in zip((lab_store, package_store), connections, strict=True):
                store.record_campaign(conn, campaign)
                store.record_era(conn, campaign["campaign_id"], era, profile, execution=bundle)
                store.record_era(conn, campaign["campaign_id"], later, profile, execution=continuation)
                self.assertEqual(later["report"]["living_population"]["final_breeders"],
                    store.load_era_breeders(conn, campaign["campaign_id"], 1))
                self.assertEqual(continuation, store.load_era_execution(conn, campaign["campaign_id"], 1))
            self.assertEqual(_dump(connections[0]), _dump(connections[1]))
        finally:
            for conn in connections:
                conn.close()

    def test_both_stores_ingest_the_real_interim_identically(self):
        lab_conn = lab_store.open_ledger(":memory:")
        package_conn = package_store.open_ledger(":memory:")
        try:
            lab_counts = lab_store.ingest_session_artifacts(
                lab_conn, INTERIM_PATH
            )
            package_counts = package_store.ingest_session_artifacts(
                package_conn, INTERIM_PATH
            )
            self.assertEqual(lab_counts, package_counts)
            self.assertEqual(_dump(lab_conn), _dump(package_conn))
            campaign_id = lab_conn.execute(
                "SELECT campaign_id FROM campaigns"
            ).fetchone()[0]
            self.assertEqual(
                lab_store.campaign_history(lab_conn, campaign_id),
                package_store.campaign_history(package_conn, campaign_id),
            )
            self.assertEqual(
                lab_store.load_founder_pool(lab_conn, campaign_id),
                package_store.load_founder_pool(package_conn, campaign_id),
            )
        finally:
            lab_conn.close()
            package_conn.close()


if __name__ == "__main__":
    unittest.main()
