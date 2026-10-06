"""Promoted X5 storage contract executes all lab-proven cases via public package API."""
import os
import subprocess
import sys
import unittest
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DRIVER = Path(__file__).resolve().parent / "helpers/storage_execution_contract_driver.py"


class StorageExecutionContractTests(unittest.TestCase):
    def test_all_execution_contract_probes_pass(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(PACKAGE_ROOT / "src")
        result = subprocess.run([sys.executable, "-B", str(DRIVER), "-v"],
                                cwd=PACKAGE_ROOT, env=env, capture_output=True,
                                text=True, timeout=60)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Ran 22 tests", result.stderr)
