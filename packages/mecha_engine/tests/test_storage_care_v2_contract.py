"""X7 v2 package passive care storage contract in an isolated import process."""
import os
from pathlib import Path
import subprocess
import sys
import unittest


class StorageCareV2ContractTests(unittest.TestCase):
    def test_all_v2_storage_contract_probes_pass(self):
        root = Path(__file__).resolve().parents[1]
        env = os.environ.copy(); env['PYTHONPATH'] = str(root / 'src')
        result = subprocess.run([sys.executable, '-B', str(root / 'tests/helpers/storage_care_v2_contract_driver.py'), '-v'],
            cwd=root, env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn('Ran 17 tests', result.stderr)
