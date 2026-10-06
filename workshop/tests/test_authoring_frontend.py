"""Run actual shared authoring JavaScript when an installed Node is available.

Browser DOM/keyboard acceptance is separately recorded; this is not a browser test.
"""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class AuthoringJavaScriptTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "installed Node unavailable; frontend JavaScript checks not observed")
    def test_actual_authoring_state_and_revision_contract(self):
        result = subprocess.run(
            [shutil.which("node"), "--test", str(ROOT / "workshop/tests/authoring_frontend.test.js")],
            cwd=ROOT, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

if __name__ == "__main__":
    unittest.main()
