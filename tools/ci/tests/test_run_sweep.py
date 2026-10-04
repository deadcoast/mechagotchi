"""The CI instrument must preserve failures, including a stalled suite."""
import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('run_sweep', Path(__file__).resolve().parents[1] / 'run_sweep.py')
sweep = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sweep)


class SweepTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.suite = self.root / 'suite'
        self.suite.mkdir()
        self.logs = self.root / 'logs'

    def fixture(self, body):
        (self.suite / 'test_fixture.py').write_text('import unittest, time\nclass TestFixture(unittest.TestCase):\n    def test_fixture(self):\n' + body, encoding='utf-8')

    def test_failure_retains_both_streams_and_fails_the_sweep(self):
        self.fixture("        print('stdout-evidence', flush=True)\n        self.fail('traceback-evidence')\n")
        with patch.object(sweep, 'ROOT', self.root), patch.object(sweep, 'SUITES', [('fixture', self.suite)]), patch.object(sys, 'argv', ['sweep', '--log-dir', str(self.logs)]), contextlib.redirect_stdout(io.StringIO()) as output:
            (self.root / 'labs').mkdir()
            (self.root / 'data').mkdir()
            self.assertEqual(1, sweep.main())
        self.assertIn('traceback-evidence', output.getvalue())
        summary = json.loads((self.logs / 'summary.json').read_text())
        result = summary['suites'][0]
        self.assertEqual('failed', result['status'])
        self.assertEqual(1, result['tests_run'])
        self.assertIn('stdout-evidence', (self.logs / result['stdout_log']).read_text())
        self.assertIn('traceback-evidence', (self.logs / result['stderr_log']).read_text())

    def test_timeout_retains_partial_output(self):
        self.fixture("        print('before-stall', flush=True)\n        time.sleep(30)\n")
        result = sweep.run_suite('stall', self.suite, self.logs, timeout=3)
        self.assertEqual('timeout', result['status'])
        self.assertIn('before-stall', (self.logs / result['stdout_log']).read_text())

    def test_empty_discovery_cannot_pass(self):
        result = sweep.run_suite('empty', self.suite, self.logs)
        self.assertEqual('failed', result['status'])
        self.assertEqual(0, result['tests_run'])


if __name__ == '__main__':
    unittest.main()
