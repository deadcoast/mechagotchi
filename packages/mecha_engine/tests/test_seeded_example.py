"""The public toy example runs from an installed/src package, with isolated output."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class SeededExampleTests(unittest.TestCase):
    def invoke(self, output, cwd):
        env = dict(os.environ, PYTHONPATH=str(ROOT/'src'), PYTHONDONTWRITEBYTECODE='1')
        return subprocess.run([sys.executable, '-B', '-m', 'mecha_engine.runtime.examples.seeded',
            '--output', str(output), '--rng-seed', '123'], cwd=cwd, env=env,
            capture_output=True, text=True, timeout=60)

    def test_reproducible_public_run_and_existing_output_refusal(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ('one','two'):
                result = self.invoke(root/name, root)
                self.assertEqual(0, result.returncode, result.stderr)
            first = {p.name:p.read_bytes() for p in (root/'one').iterdir()}
            second = {p.name:p.read_bytes() for p in (root/'two').iterdir()}
            self.assertEqual(first, second)
            report = json.loads(first['report.json'])
            self.assertTrue(report['ok'])
            self.assertFalse(report['scientific_evidence'])
            self.assertEqual('constant_uncalibrated',report['readability']['kind'])
            self.assertGreater(report['engine_report']['generations_requested'],0)
            self.assertTrue(report['checks']['seed_valid'])
            self.assertTrue(report['checks']['seed_aligned'])
            self.assertNotEqual(0,self.invoke(root/'one',root).returncode)
            self.assertEqual(first,{p.name:p.read_bytes() for p in (root/'one').iterdir()})

if __name__ == '__main__': unittest.main()
