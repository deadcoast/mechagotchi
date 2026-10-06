"""Synthetic coordinator safety checks; no models or qualification trials."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    'x8_earned_coordinator', Path(__file__).with_name('x8_earned_coordinator.py'))
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class CoordinatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.worker = self.root / 'worker.py'
        self.worker.write_text('from pathlib import Path\nimport sys\np=Path(sys.argv[1]); p.mkdir(); (p/"result").write_text("retained")\n')
        self.manifest = self.root / 'source.json'
        self.freeze()
        self.inputs = self.root / 'inputs.json'
        self.inputs.write_text('{}')
        self.budget = self.root / 'budget.json'
        self.budget.write_bytes(m.encode(m.initial_budget(m.sha(self.manifest.read_bytes()))))
        self.receipts = self.root / 'receipts'
        self.output = self.root / 'output'

    def freeze(self):
        self.manifest.write_bytes(m.encode({'format': 'x8_source_manifest_v1',
            'files': {'worker.py': m.sha(self.worker.read_bytes())}}))

    def invoke(self, name='setup', kind='setup', **changes):
        args = dict(name=name, kind=kind,
            command=[sys.executable, '-B', str(self.worker), str(self.output)],
            source_manifest=self.manifest, inputs=self.inputs,
            inputs_sha256=m.sha(self.inputs.read_bytes()), output_dir=self.output,
            budget_path=self.budget, receipt_root=self.receipts, root=self.root)
        args.update(changes)
        return m.run_one(**args)

    def test_success_is_durable_hashed_and_debited(self):
        result = self.invoke()
        self.assertEqual(result['status'], 'completed')
        self.assertTrue(result['cleanup_confirmed'])
        self.assertEqual(result['outputs']['worker/result'], m.sha(b'retained'))
        start = self.receipts / 'setup' / 'started.json'
        self.assertEqual(result['started_sha256'], m.sha(start.read_bytes()))
        budget = json.loads(self.budget.read_bytes())
        self.assertGreater(budget['elapsed_seconds'], 0)
        self.assertAlmostEqual(budget['elapsed_seconds'] + budget['remaining_seconds'], 1200)
        self.assertFalse(self.budget.with_suffix('.lock').exists())

    def test_worker_observes_started_receipt_and_running_debit(self):
        self.worker.write_text('from pathlib import Path\nimport json,sys\nr=Path(sys.argv[1]).parent\nassert (r/"receipts/setup/started.json").exists()\nassert json.loads((r/"budget.json").read_bytes())["stages"][0]["status"]=="running"\np=Path(sys.argv[1]);p.mkdir();(p/"result").write_text("retained")\n')
        self.freeze()
        self.budget.write_bytes(m.encode(m.initial_budget(m.sha(self.manifest.read_bytes()))))
        self.assertEqual(self.invoke()['status'], 'completed')

    def test_existing_stage_never_reuses_or_reruns(self):
        self.invoke()
        with patch.object(m, '_launch') as launch:
            with self.assertRaisesRegex(ValueError, 'repeat|existing|already'):
                self.invoke()
        launch.assert_not_called()

    def test_existing_output_is_preserved_and_terminal_refused(self):
        self.output.mkdir()
        (self.output / 'result').write_text('original')
        with patch.object(m, '_launch') as launch:
            self.assertEqual(self.invoke()['status'], 'refused')
        launch.assert_not_called()
        self.assertEqual((self.output / 'result').read_text(), 'original')

    def test_bad_input_hash_refuses_before_worker(self):
        with patch.object(m, '_launch') as launch:
            result = self.invoke(inputs_sha256='0' * 64)
        self.assertEqual(result['status'], 'refused')
        launch.assert_not_called()

    def test_input_path_requires_digest(self):
        with self.assertRaisesRegex(ValueError, 'digest|sha256'):
            self.invoke(inputs_sha256=None)

    def test_source_drift_before_worker_refuses(self):
        self.worker.write_text('raise RuntimeError("never run")')
        with patch.object(m, '_launch') as launch:
            self.assertEqual(self.invoke()['status'], 'refused')
        launch.assert_not_called()

    def test_source_drift_after_worker_refuses(self):
        self.worker.write_text('from pathlib import Path\nPath(__file__).write_text("changed")\n')
        self.freeze()
        self.budget.write_bytes(m.encode(m.initial_budget(m.sha(self.manifest.read_bytes()))))
        result = self.invoke()
        self.assertEqual(result['status'], 'refused')
        self.assertIn('drift', result['error'])

    def test_failed_worker_blocks_every_following_stage(self):
        result = self.invoke(command=[sys.executable, '-B', '-c', 'raise SystemExit(7)'])
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['returncode'], 7)
        with self.assertRaisesRegex(ValueError, 'failed|incomplete'):
            self.invoke(name='independent', kind='analysis', output_dir=self.root / 'other')

    def test_interrupted_lock_is_not_removed(self):
        lock = self.budget.with_suffix('.lock')
        lock.write_bytes(b'preserve')
        with self.assertRaisesRegex(ValueError, 'active|interrupted'):
            self.invoke()
        self.assertEqual(lock.read_bytes(), b'preserve')

    def test_partial_receipts_are_never_restarted(self):
        (self.receipts / 'setup').mkdir(parents=True)
        (self.receipts / 'setup' / 'started.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'partial|existing|interrupted'):
            self.invoke()

    def test_modified_prior_output_refuses_next_stage(self):
        self.invoke()
        (self.output / 'result').write_text('tampered')
        result = self.invoke(name='era-1', kind='era', output_dir=self.root / 'second')
        self.assertEqual(result['status'], 'refused')
        self.assertIn('output', result['error'])

    def test_new_derived_inputs_are_bound_per_stage(self):
        self.invoke()
        self.inputs = self.root / 'derived.json'
        self.inputs.write_text('{"from_previous":true}')
        self.output = self.root / 'second'
        result = self.invoke(name='era-1', kind='era')
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['inputs_sha256'], m.sha(self.inputs.read_bytes()))

    def test_cross_stage_source_rebinding_refuses(self):
        self.invoke()
        self.worker.write_text('# changed')
        self.freeze()
        result = self.invoke(name='era-1', kind='era', output_dir=self.root / 'second')
        self.assertEqual(result['status'], 'refused')

    def test_budget_accounting_tamper_refuses(self):
        value = json.loads(self.budget.read_bytes())
        value['remaining_seconds'] -= 1
        self.budget.write_bytes(m.encode(value))
        with self.assertRaisesRegex(ValueError, 'accounting'):
            self.invoke()

    def test_fixed_caps_and_safe_stage_names(self):
        self.assertEqual(m.KIND_LIMITS, {'setup':120, 'era':120, 'reproduction':120, 'native':60, 'analysis':120})
        with self.assertRaises(ValueError):
            self.invoke(name='../escape')
        with self.assertRaises(ValueError):
            self.invoke(kind='cohort')

    def test_setup_cannot_be_repeated_under_different_name(self):
        self.invoke()
        with self.assertRaisesRegex(ValueError, 'slot|setup'):
            self.invoke(name='another-setup', output_dir=self.root / 'other')

    def test_actual_timeout_kills_and_reaps_worker(self):
        # Earlier start consumes a native stage's time without waiting 60s.
        result = self.invoke(kind='native', command=[sys.executable, '-B', '-c',
            'import time;time.sleep(30)'], started=m.time.perf_counter()-
            (60-m.CLEANUP_ALLOWANCE-m.PUBLICATION_ALLOWANCE-0.3))
        self.assertEqual(result['status'], 'timeout')
        self.assertTrue(result['cleanup_confirmed'])
        self.assertFalse(self.budget.with_suffix('.lock').exists())

    def test_finished_parent_cannot_leave_descendant_running(self):
        result = self.invoke(command=[sys.executable, '-B', '-c',
            'import subprocess,sys; subprocess.Popen([sys.executable,"-B","-c","import time;time.sleep(30)"])'])
        self.assertEqual(result['status'], 'error')
        self.assertIn('descendant', result['error'])
        self.assertTrue(result['cleanup_confirmed'])

    def test_cli_preserves_full_worker_argv(self):
        args = m.parser().parse_args(['--name','a','--kind','analysis',
            '--source-manifest',str(self.manifest),'--output-dir',str(self.output),
            '--budget',str(self.budget),'--receipt-root',str(self.receipts),
            '--',sys.executable,'-B','-c','print(1)'])
        self.assertEqual(args.command[1:], [sys.executable,'-B','-c','print(1)'])

    def test_mutated_input_after_worker_is_refused(self):
        result = self.invoke(command=[sys.executable, '-B', '-c',
            'from pathlib import Path; Path("inputs.json").write_text("changed")'])
        self.assertEqual(result['status'], 'refused')
        self.assertIn('input', result['error'])

    def test_keyboard_interrupt_reaps_then_records_interruption(self):
        original = m._launch
        def launch(*args):
            process, tree = original(*args)
            wait = process.wait
            first = [True]
            def interrupted(timeout=None):
                if first.pop() if first else False:
                    raise KeyboardInterrupt()
                return wait(timeout=timeout)
            process.wait = interrupted
            return process, tree
        with patch.object(m, '_launch', side_effect=launch):
            result = self.invoke(command=[sys.executable, '-B', '-c', 'import time;time.sleep(30)'])
        self.assertEqual(result['status'], 'interrupted')
        self.assertTrue(result['cleanup_confirmed'])
        self.assertFalse(self.budget.with_suffix('.lock').exists())

    def test_unconfirmed_cleanup_keeps_lock_and_terminal(self):
        original = m._cleanup
        def unconfirmed(*args, **kwargs):
            original(*args, **kwargs)
            raise m.WorkerTerminationError('synthetic unconfirmed cleanup')
        with patch.object(m, '_cleanup', side_effect=unconfirmed):
            with self.assertRaises(m.WorkerTerminationError):
                self.invoke()
        self.assertTrue(self.budget.with_suffix('.lock').exists())
        result = json.loads((self.receipts / 'setup' / 'terminal.json').read_bytes())
        self.assertEqual(result['status'], 'interrupted')
        self.assertFalse(result['cleanup_confirmed'])

    def test_late_budget_failure_keeps_durable_terminal_and_lock(self):
        original = m._publish_budget
        calls = []
        def fail_terminal(*args):
            calls.append(True)
            if len(calls) == 2:
                raise OSError('synthetic late publication failure')
            return original(*args)
        with patch.object(m, '_publish_budget', side_effect=fail_terminal):
            with self.assertRaises(OSError):
                self.invoke()
        self.assertTrue((self.receipts / 'setup' / 'terminal.json').exists())
        self.assertTrue(self.budget.with_suffix('.lock').exists())
        self.assertEqual(json.loads(self.budget.read_bytes())['stages'][0]['status'], 'running')

    def test_slow_publication_is_not_returned_as_success(self):
        original = m._publish_budget
        calls = []
        def delayed(*args):
            calls.append(True)
            original(*args)
            if len(calls) == 2:
                m.time.sleep(m.PUBLICATION_ALLOWANCE + 0.05)
        with patch.object(m, '_publish_budget', side_effect=delayed):
            with self.assertRaisesRegex(ValueError, 'publication allowance'):
                self.invoke()
        self.assertTrue(self.budget.with_suffix('.lock').exists())
        self.assertEqual(json.loads(self.budget.read_bytes())['stages'][0]['status'], 'interrupted')
        self.assertEqual(json.loads((self.receipts / 'setup' / 'publication-failure.json').read_bytes())['status'], 'interrupted')

    def test_scanning_outputs_consumes_stage_budget(self):
        original = m.output_snapshot
        def exhausted(*args, **kwargs):
            raise TimeoutError('synthetic bounded output validation timeout')
        with patch.object(m, 'output_snapshot', side_effect=exhausted):
            result = self.invoke()
        self.assertEqual(result['status'], 'timeout')
        self.assertIn('output validation', result['error'])

    def test_publication_artifact_cannot_be_overwritten(self):
        leftover = self.budget.with_suffix('.publishing')
        leftover.write_bytes(b'preserve')
        with self.assertRaises(FileExistsError):
            self.invoke()
        self.assertEqual(leftover.read_bytes(), b'preserve')
        self.assertTrue(self.budget.with_suffix('.lock').exists())

    def test_fixed_era_and_reproduction_slots_are_enforced(self):
        for kind, maximum in (('era', 6), ('reproduction', 4)):
            with self.subTest(kind=kind):
                # Reinitialize only this synthetic temporary fixture, not a study.
                self.budget.write_bytes(m.encode(m.initial_budget(m.sha(self.manifest.read_bytes()))))
                for index in range(maximum):
                    self.output = self.root / f'{kind}-output-{index}'
                    self.assertEqual(self.invoke(name=f'{kind}-{index}', kind=kind)['status'], 'completed')
                with self.assertRaisesRegex(ValueError, 'slots exhausted'):
                    self.invoke(name=f'{kind}-extra', kind=kind, output_dir=self.root / f'{kind}-extra')

    def test_low_cumulative_budget_refuses_before_launch(self):
        value = m.initial_budget(m.sha(self.manifest.read_bytes()))
        value['stages'] = [dict(name='retained', kind='analysis', status='completed', elapsed_seconds=1195)]
        value['elapsed_seconds'] = 1195
        value['remaining_seconds'] = 5
        self.budget.write_bytes(m.encode(value))
        with patch.object(m, '_launch') as launch:
            with self.assertRaisesRegex(ValueError, 'budget'):
                self.invoke()
        launch.assert_not_called()

    def test_cli_runs_the_full_command_in_fresh_process(self):
        # The real coordinator runs from its repository root; temp inputs/outputs
        # stay disposable while the manifest includes coordinator and dummy worker.
        closure = m.ROOT / 'labs/game_loop/x8_earned_coordinator.py'
        self.manifest.write_bytes(m.encode({'format':'x8_source_manifest_v1',
            'files':{'labs/game_loop/x8_earned_coordinator.py':m.sha(closure.read_bytes())}}))
        self.budget.write_bytes(m.encode(m.initial_budget(m.sha(self.manifest.read_bytes()))))
        result = subprocess.run([sys.executable, '-B', str(closure), '--name','cli',
            '--kind','analysis','--source-manifest',str(self.manifest),
            '--output-dir',str(self.output),'--budget',str(self.budget),
            '--receipt-root',str(self.receipts),'--',sys.executable,'-B',str(self.worker),str(self.output)],
            capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        terminal = json.loads(result.stdout)
        self.assertEqual(terminal['status'], 'completed')
        self.assertEqual(terminal['request']['command'], [sys.executable,'-B',str(self.worker),str(self.output)])

    def test_prior_kind_relabel_cannot_bypass_reserved_slots(self):
        for kind in ('setup', 'era', 'reproduction'):
            with self.subTest(kind=kind):
                self.budget.write_bytes(m.encode(m.initial_budget(m.sha(self.manifest.read_bytes()))))
                self.output = self.root / f'relabel-output-{kind}'
                self.invoke(name=f'original-{kind}', kind=kind)
                budget = json.loads(self.budget.read_bytes())
                budget['stages'][0]['kind'] = 'native'
                self.budget.write_bytes(m.encode(budget))
                with patch.object(m, '_launch') as launch:
                    result = self.invoke(name=f'after-{kind}', kind='analysis', output_dir=self.root / f'after-output-{kind}')
                self.assertEqual(result['status'], 'refused')
                self.assertIn('identities', result['error'])
                launch.assert_not_called()

    def test_terminal_request_must_match_hashed_started_request(self):
        self.invoke()
        budget = json.loads(self.budget.read_bytes())
        terminal_path = self.receipts / 'setup' / 'terminal.json'
        terminal = json.loads(terminal_path.read_bytes())
        terminal['request']['command'] = ['changed-command']
        terminal_path.write_bytes(m.encode(terminal))
        budget['stages'][0]['terminal_sha256'] = m.sha(terminal_path.read_bytes())
        self.budget.write_bytes(m.encode(budget))
        with patch.object(m, '_launch') as launch:
            result = self.invoke(name='after', kind='analysis', output_dir=self.root / 'after')
        self.assertEqual(result['status'], 'refused')
        self.assertIn('identities', result['error'])
        launch.assert_not_called()

    def test_unknown_kind_and_missing_status_refuse_budget(self):
        for change in ({'kind': 'unregistered'}, {'status': None}):
            value = m.initial_budget(m.sha(self.manifest.read_bytes()))
            value['stages'] = [dict(name='invalid', kind='native', status='completed', elapsed_seconds=0, **{})]
            value['stages'][0].update(change)
            with self.assertRaisesRegex(ValueError, 'kind|status'):
                m.check_budget(value)


if __name__ == '__main__':
    unittest.main()
