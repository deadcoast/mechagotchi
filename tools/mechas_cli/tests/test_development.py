"""Exercise the local cycle with real Git and verification subprocesses."""
import json
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from mechas_cli import development as cycle


class DevelopmentCycleTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.write('.gitignore', '.development/\n')
        self.write('docs/development/workflow.json', json.dumps({'schema_version': 1, 'slices': {
            'first': {'spec': 'docs/first.md', 'purpose': 'test slice', 'suites': ['cli', 'ci']},
            'second': {'spec': 'docs/second.md', 'purpose': 'next slice', 'suites': ['cli']}}}))
        self.write('docs/first.md', 'Preregistered contract\n')
        self.write('docs/second.md', 'Second contract\n')
        self.write('source.py', 'VALUE = 1\n')
        (self.root / 'labs').mkdir()
        self.write('tools/ci/run_sweep.py', '''import json, pathlib, sys
args = sys.argv[1:]
logs = pathlib.Path(args[args.index('--log-dir') + 1]); logs.mkdir(parents=True, exist_ok=True)
suites = [args[i+1] for i, a in enumerate(args) if a == '--suite'] or ['cli', 'ci', 'package', 'game', 'workshop']
summary = {'complete': True, 'failures': [], 'quick': False,
 'environment': {'dependencies': dict.fromkeys(['pydantic','jsonschema','typer','rich','pygame-ce','pyinstaller'], 'installed')},
 'suites': [{'name': s, 'status': 'passed', 'tests_run': 1} for s in suites],
 'artifacts': {'ok': True}}
(logs/'summary.json').write_text(json.dumps(summary))
print('real-subprocess-evidence')
''')
        self.git('init', '-q')
        self.git('add', '.')
        self.git('-c', 'user.name=Workflow Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'fixture')

    def write(self, name, text):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], stderr=subprocess.STDOUT)

    def start(self):
        cycle.begin(self.root, 'first')
        cycle.advance(self.root, 'repair', 'Recorded baseline and RED plan.')

    def test_resume_and_local_completion_keep_publication_unmet(self):
        self.start()
        with self.assertRaises(cycle.WorkflowError):
            cycle.advance(self.root, 'enhance', 'No verification yet')
        result = cycle.verify(self.root, 'focused', sys.executable)
        self.assertTrue(result['passed'])
        self.assertIn('real-subprocess-evidence', (self.root / result['stdout_log']).read_text())
        cycle.advance(self.root, 'enhance', 'Baseline repaired.')
        cycle.advance(self.root, 'polish', 'Contract and implementation reviewed.')
        self.assertFalse(cycle.status(self.root)['local_complete'])
        self.assertTrue(cycle.verify(self.root, 'full', sys.executable)['passed'])
        cycle.checkpoint(self.root, 'Next: independent native CI, currently blocked.')
        resumed = cycle.status(self.root)
        self.assertTrue(resumed['local_complete'])
        self.assertEqual('polish', resumed['phase'])
        self.assertEqual('unmet', resumed['publication_gate']['status'])
        self.assertIn('native CI', resumed['checkpoints'][-1]['note'])
        cycle.begin(self.root, 'second')
        self.assertEqual('review', cycle.status(self.root)['phase'])
        self.assertEqual(1, len(list((self.root / '.development/history').glob('*.json'))))

    def test_source_edits_invalidate_but_report_markdown_can_record_results(self):
        self.start()
        self.assertTrue(cycle.verify(self.root, 'focused', sys.executable)['passed'])
        self.write('docs/result.md', 'Measured result\n')
        self.assertTrue(cycle.status(self.root)['focused_current'])
        self.write('source.py', 'VALUE = 2\n')
        self.assertFalse(cycle.status(self.root)['focused_current'])
        with self.assertRaises(cycle.WorkflowError):
            cycle.advance(self.root, 'enhance', 'Stale evidence cannot pass.')

    def test_test_mutation_fails_without_restoring_the_changed_file(self):
        self.start()
        runner = self.root / 'tools/ci/run_sweep.py'
        runner.write_text(runner.read_text() + "\npathlib.Path('source.py').write_text('changed by test')\n")
        result = cycle.verify(self.root, 'focused', sys.executable)
        self.assertFalse(result['passed'])
        self.assertIn('source.py', result['changed_files'])
        self.assertEqual('changed by test', (self.root / 'source.py').read_text())
        self.assertEqual('repair', cycle.status(self.root)['phase'])

    def test_failure_revoke_success_and_preserves_stderr(self):
        self.start()
        self.assertTrue(cycle.verify(self.root, 'focused', sys.executable)['passed'])
        runner = self.root / 'tools/ci/run_sweep.py'
        runner.write_text(runner.read_text() + "\nprint('actual-failure', file=sys.stderr)\nraise SystemExit(7)\n")
        result = cycle.verify(self.root, 'focused', sys.executable)
        self.assertFalse(result['passed'])
        self.assertEqual(7, result['returncode'])
        self.assertIn('actual-failure', (self.root / result['stderr_log']).read_text())
        self.assertFalse(cycle.status(self.root)['focused_current'])

    def test_invalid_sweep_results_cannot_pass(self):
        self.start()
        runner = self.root / 'tools/ci/run_sweep.py'
        original = runner.read_text()
        for change in ["summary['complete'] = False", "summary['suites'] = []",
                       "summary['suites'][0]['tests_run'] = 0",
                       "summary['suites'][0]['name'] = 'wrong-suite'",
                       "summary['environment']['dependencies']['typer'] = None"]:
            with self.subTest(change=change):
                runner.write_text(original + '\n' + change + "\n(logs/'summary.json').write_text(json.dumps(summary))\n")
                self.assertFalse(cycle.verify(self.root, 'focused', sys.executable)['passed'])

    def test_unfinished_replacement_missing_spec_and_invalid_phase_are_refused(self):
        cycle.begin(self.root, 'first')
        with self.assertRaises(cycle.WorkflowError):
            cycle.begin(self.root, 'second')
        with self.assertRaises(cycle.WorkflowError):
            cycle.advance(self.root, 'polish', 'Skip the gates')
        with self.assertRaises(cycle.WorkflowError):
            cycle.advance(self.root, 'repair', '')
        (self.root / 'docs/first.md').unlink()
        with self.assertRaises(cycle.WorkflowError):
            cycle.verify(self.root, 'focused', sys.executable)

    def test_read_only_status_and_path_escape_rejection(self):
        self.assertFalse(cycle.status(self.root)['started'])
        self.assertFalse((self.root / '.development').exists())
        config = json.loads((self.root / 'docs/development/workflow.json').read_text())
        config['slices']['first']['spec'] = '../outside.md'
        self.write('docs/development/workflow.json', json.dumps(config))
        with self.assertRaises(cycle.WorkflowError):
            cycle.begin(self.root, 'first')


    @unittest.skipUnless(importlib.util.find_spec('typer'), 'CLI dependencies not installed')
    def test_cli_status_uses_actual_root_and_rejects_conflicting_actions(self):
        from typer.testing import CliRunner
        from mechas_cli.app import app
        runner = CliRunner()
        with patch('mechas_cli.workflows.develop.find_workspace_root', return_value=self.root):
            response = runner.invoke(app, ['develop', '--status'])
            self.assertEqual(0, response.exit_code, response.output)
            self.assertEqual(str(self.root.resolve()), json.loads(response.output)['repository'])
            response = runner.invoke(app, ['develop', '--status', '--start', 'first'])
            self.assertEqual(2, response.exit_code)
            self.assertFalse((self.root / '.development').exists())

    def test_full_verification_rejects_incomplete_suite_plan(self):
        self.start()
        runner = self.root / 'tools/ci/run_sweep.py'
        runner.write_text(runner.read_text() + "\nsummary['suites'] = summary['suites'][:1]\n(logs/'summary.json').write_text(json.dumps(summary))\n")
        self.assertFalse(cycle.verify(self.root, 'full', sys.executable)['passed'])



    def test_failure_revokes_earlier_full_result_even_after_focused_recovery(self):
        self.start()
        self.assertTrue(cycle.verify(self.root, 'full', sys.executable)['passed'])
        runner = self.root / 'tools/ci/run_sweep.py'
        original = runner.read_text()
        runner.write_text(original + '\nraise SystemExit(1)\n')
        self.assertFalse(cycle.verify(self.root, 'focused', sys.executable)['passed'])
        runner.write_text(original)
        self.assertTrue(cycle.verify(self.root, 'focused', sys.executable)['passed'])
        self.assertFalse(cycle.status(self.root)['full_current'])



    def test_timeout_retains_partial_output_and_fails(self):
        self.start()
        self.write('tools/ci/run_sweep.py', "import time\nprint('before-timeout', flush=True)\ntime.sleep(30)\n")
        result = cycle.verify(self.root, 'focused', sys.executable, timeout=3)
        self.assertFalse(result['passed'])
        self.assertIsNone(result['returncode'])
        self.assertIn('before-timeout', (self.root / result['stdout_log']).read_text())
        self.assertIsNone(cycle.status(self.root)['running'])


if __name__ == '__main__':
    unittest.main()
