"""X7 package storage care contract, isolated from game dependencies."""
import os
import subprocess
import sys
import unittest
from pathlib import Path


class StorageCareContractTests(unittest.TestCase):
    def test_all_care_storage_contract_probes_pass(self):
        root = Path(__file__).resolve().parents[1]
        env = os.environ.copy(); env['PYTHONPATH'] = str(root / 'src')
        result = subprocess.run([sys.executable, '-B', str(root / 'tests/helpers/storage_care_contract_driver.py'), '-v'],
            cwd=root, env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn('Ran 16 tests', result.stderr)
