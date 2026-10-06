"""X8 package storage population contract in an isolated import process."""
import os
from pathlib import Path
import subprocess
import sys
import unittest
class StoragePopulationContractTests(unittest.TestCase):
    def test_all_population_storage_contract_probes_pass(self):
        root=Path(__file__).resolve().parents[1]
        env=os.environ.copy();env['PYTHONPATH']=str(root/'src')
        result=subprocess.run([sys.executable,'-B',str(root/'tests/helpers/storage_population_contract_driver.py'),'-v'],
            cwd=root,env=env,capture_output=True,text=True,timeout=30)
        self.assertEqual(0,result.returncode,result.stdout+result.stderr)
        self.assertIn('Ran 23 tests',result.stderr)
