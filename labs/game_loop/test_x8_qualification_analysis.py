"""Receipt tampering controls; no simulations."""
import unittest
from unittest.mock import patch
from pathlib import Path
import x8_qualification_analysis as target

class AnalysisBindingTests(unittest.TestCase):
    def test_parity_rejects_valid_receipts_from_wrong_planned_directories(self):
        first=target.population.case_plan()[0]
        rows=[dict(plan=first,result={}) for _ in range(16)]
        with patch.object(target.population,'source_snapshot',return_value={'source':'digest'}), \
             patch.object(target,'read',return_value={'source_sha256':{'source':'digest'},'source_manifest_sha256':'digest'}), \
             patch.object(target,'sha',return_value='digest'), \
             patch.object(target.population,'load_trial',side_effect=rows):
            with self.assertRaisesRegex(ValueError,'ordered'):
                target.analyze('parity',Path('unused'))
