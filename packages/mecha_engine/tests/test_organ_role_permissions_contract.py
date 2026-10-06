"""X8 optional role permissions on the isolated package surface."""
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACKAGE_ROOT.parents[1]
DRIVER = Path(__file__).resolve().parent / 'helpers/organ_role_permissions_driver.py'

class OrganRolePermissionsContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        env = dict(os.environ, PYTHONPATH=str(PACKAGE_ROOT / 'src'))
        result = subprocess.run([sys.executable, '-B', str(DRIVER), '--repo-root', str(REPO_ROOT)],
                                env=env, cwd=PACKAGE_ROOT, text=True, capture_output=True, timeout=30)
        if result.returncode:
            raise AssertionError(result.stderr)
        cls.report = json.loads(result.stdout)

    def test_supported_role_sets_are_accepted(self):
        self.assertEqual(4, len(self.report['valid']))
        self.assertTrue(all(self.report['valid']))

    def test_malformed_version_and_required_role_contradictions_refuse(self):
        self.assertEqual(13, len(self.report['invalid']))
        self.assertTrue(all(self.report['invalid']))

    def test_actual_corpus_roles_control_admission(self):
        self.assertEqual(200, len(self.report['alignment']))
        self.assertTrue(all(self.report['alignment']))

    def test_all_allowed_roles_matches_legacy_alignment(self):
        self.assertEqual(50, len(self.report['absence']))
        self.assertTrue(all(self.report['absence']))

    def test_malformed_mixed_type_roles_are_rejected_without_crashing(self):
        self.assertEqual(5, len(self.report['malformed_roles']))
        self.assertTrue(all(self.report['malformed_roles']))

    def test_inputs_are_unchanged(self):
        self.assertTrue(all(self.report['pure']))

if __name__ == '__main__': unittest.main()
