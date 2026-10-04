"""Q2's public authority, precedence and off-mode lifecycle contracts."""
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DRIVER = Path(__file__).with_name('helpers') / 'slip_mechanics_driver.py'


class SlipMechanicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        env = dict(os.environ, PYTHONPATH=str(ROOT / 'packages/mecha_engine/src'))
        result = subprocess.run([sys.executable, '-B', str(DRIVER), str(ROOT)], env=env,
                                capture_output=True, text=True, check=True)
        cls.result = json.loads(result.stdout)

    def test_package_matches_the_shared_strict_matrix(self):
        self.assertEqual([], self.result['matrix_mismatches'])

    def test_profile_only_opt_in_permits_clean_action_stream(self):
        self.assertTrue(self.result['profile_only_clean'])

    def test_explicit_empty_override_disables_profile_mechanic(self):
        self.assertTrue(self.result['explicit_disable'])

    def test_explicit_enable_wins_over_profile_false(self):
        self.assertTrue(self.result['explicit_enable'])

    def test_override_cannot_excuse_invalid_profile(self):
        self.assertTrue(self.result['invalid_profile_refused'])

    def test_every_incumbent_profile_matches_preimplementation_state_and_episodes(self):
        self.assertEqual([], self.result['incumbent_mismatches'])

    def test_inputs_are_not_mutated(self):
        self.assertTrue(self.result['inputs_preserved'])

    def test_absent_empty_and_false_profile_forms_have_identical_behavior(self):
        self.assertTrue(self.result['off_forms_identical'])


if __name__ == '__main__':
    unittest.main()
