"""Storage contract tests for the mecha_engine package surface.

Traceability: research/decision_records/0022-storage-module.md (schema
v1 and the eight gates) and
research/experiment_reports/2026-07-07-campaign-store.md. Import
mechanics match every other contract suite: the probes run in one
``python -B`` subprocess whose PYTHONPATH points at this package's own
``src`` directory, executed by
``tests/helpers/storage_contract_driver.py`` through
``mecha_engine.storage`` only. Fixtures are synthetic interim ledgers
built inside the driver — the real-engine-output evidence is the lab
suite (``labs/game_loop/test_campaign_store.py``) and the lab-side
parity pin (``labs/game_loop/test_package_storage_parity.py``).
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACKAGE_ROOT.parents[1]
SRC_DIR = PACKAGE_ROOT / "src"
DRIVER = Path(__file__).resolve().parent / "helpers" / "storage_contract_driver.py"


def _run_driver() -> dict:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(SRC_DIR) + (os.pathsep + existing if existing else "")
    result = subprocess.run(
        [sys.executable, "-B", str(DRIVER)],
        capture_output=True,
        text=True,
        env=env,
        cwd=PACKAGE_ROOT,
        timeout=300,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"storage contract driver failed ({result.returncode}):\n"
            f"{result.stderr}"
        )
    return json.loads(result.stdout)


class MechaEngineStorageContractTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = _run_driver()

    def test_schema_version_is_one(self):
        self.assertEqual(1, self.report["schema_version"])

    def test_interim_migration_counts(self):
        self.assertEqual(
            {
                "campaigns": 1,
                "slip_profiles": 2,
                "eras": 2,
                "elites": 6,
                "founders": 3,
                "unlocks": 1,
                "replays": 0,
            },
            self.report["counts"],
        )

    def test_blobs_round_trip_byte_identically(self):
        self.assertTrue(self.report["round_trip_byte_identical"])

    def test_derived_columns_equal_their_blobs(self):
        self.assertTrue(self.report["derived_columns_pinned"])

    def test_founder_pool_is_the_prior_eras_elites_in_niche_order(self):
        self.assertTrue(self.report["founder_pool_niche_order"])

    def test_succession_resolves_through_the_predecessor_pointer(self):
        self.assertTrue(self.report["succession_chain_resolves"])

    def test_history_is_replay_sufficient(self):
        self.assertTrue(self.report["history_replay_sufficient"])

    def test_era_transactions_are_atomic(self):
        self.assertTrue(self.report["era_atomicity_holds"])

    def test_unsupported_versions_and_foreign_schemas_are_refused(self):
        self.assertTrue(self.report["bad_version_refused"])
        self.assertTrue(self.report["foreign_schema_refused"])

    def test_storage_source_keeps_the_package_boundary(self):
        source_dir = SRC_DIR / "mecha_engine" / "storage"
        for path in source_dir.glob("*.py"):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("import labs", text, path.name)
            self.assertNotIn("from labs", text, path.name)
            # The boundary scan's hard rule: no interpreter-path text
            # anywhere in the package tree.
            self.assertNotIn("sys" + ".path", text, path.name)


if __name__ == "__main__":
    unittest.main()
