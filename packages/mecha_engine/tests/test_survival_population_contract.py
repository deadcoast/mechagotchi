"""Isolated package-only X8 runtime contract checks."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
ROOT=Path(__file__).resolve().parents[3]
class SurvivalPopulationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        env=os.environ.copy();env['PYTHONPATH']=str(ROOT/'packages/mecha_engine/src')
        result=subprocess.run([sys.executable,'-B',str(Path(__file__).parent/'helpers/survival_population_contract_driver.py')],
                              capture_output=True,text=True,env=env,timeout=30)
        if result.returncode:raise AssertionError(result.stdout+result.stderr)
        cls.checks=json.loads(result.stdout)
    def test_legacy_observation_and_input_contract(self):
        for key in ('legacy_exact','actual_observer','damage_observer','inputs_immutable','explicit_guards'):
            with self.subTest(key=key):self.assertTrue(self.checks[key])
    def test_living_population_endpoint_contract(self):
        for key in ('survivor_api','full_endpoint_evidence','repeat_exact','empty_explicit',
                    'empty_not_death','archive_is_history','terminal_death'):
            with self.subTest(key=key):self.assertTrue(self.checks[key])
