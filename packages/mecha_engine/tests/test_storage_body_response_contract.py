"""Body response ledger contract in an isolated package process."""
import os,subprocess,sys,unittest
from pathlib import Path
class StorageBodyResponseContractTests(unittest.TestCase):
    def test_body_response_storage_contract(self):
        root=Path(__file__).resolve().parents[1];env=os.environ.copy();env['PYTHONPATH']=str(root/'src')
        result=subprocess.run([sys.executable,'-B',str(root/'tests/helpers/storage_body_response_contract_driver.py'),'-v'],cwd=root,env=env,capture_output=True,text=True,timeout=30)
        self.assertEqual(0,result.returncode,result.stdout+result.stderr)
        self.assertIn('Ran 6 tests',result.stderr)
