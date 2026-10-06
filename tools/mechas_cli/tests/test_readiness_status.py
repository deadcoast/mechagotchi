"""Product evidence and research calibration remain distinct."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/mechas_cli/src'))

class ReadinessStatusTests(unittest.TestCase):
    def test_no_artifact_never_claims_delivery_or_remote_success(self):
        from mechas_cli.workflows.status import readiness
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            with patch('mechas_cli.development.status',return_value={
                    'local_complete':True,'full_current':True,
                    'publication_gate':{'status':'unmet'}}):
                value=readiness(root)
            self.assertTrue(value['local']['full_current'])
            self.assertEqual('unverified',value['packaged']['status'])
            self.assertEqual('unmet',value['cloud']['status'])
            self.assertFalse(value['research']['blocks_application'])
if __name__=='__main__':unittest.main()
