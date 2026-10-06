"""Subprocess-owned package-only X7 care contracts."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
class CareContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        env=os.environ.copy()
        env['PYTHONPATH']=str(ROOT/'packages/mecha_engine/src')
        result=subprocess.run([sys.executable,'-B',str(Path(__file__).parent/'helpers/care_contract_driver.py')],
                              capture_output=True,text=True,env=env,timeout=90)
        if result.returncode: raise AssertionError(result.stdout+result.stderr)
        cls.checks=json.loads(result.stdout)
    def test_absent_and_off_scientific_parity(self):
        for name in ('null_exact','off_archive_exact','off_science_exact','successor_off_exact'):
            with self.subTest(name=name): self.assertTrue(self.checks[name])
    def test_actual_founder_occurrences_and_parentage(self):
        for name in ('duplicate_occurrences_distinct','source_free_no_selection','enabled_receipts',
                     'elite_context_order','later_actual_parent_occurrence'):
            with self.subTest(name=name): self.assertTrue(self.checks[name])
    def test_inputs_immutable_and_bad_ordinal_refused(self):
        self.assertTrue(self.checks['source_immutable'])
        self.assertTrue(self.checks['ordinal_length_refuses'])

    def test_v2_preserves_founder_occurrence_and_terminal_contract(self):
        for name in ('v2_absent_exact','v2_duplicate_occurrences_distinct','v2_source_identity_bound',
                     'v2_terminal_selection_order','v2_later_actual_parent_occurrence','v2_source_immutable'):
            with self.subTest(name=name): self.assertTrue(self.checks[name])
