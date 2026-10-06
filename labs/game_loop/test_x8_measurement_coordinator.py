"""Guard tests only: mocked workers perform no qualification simulation."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

PATH=Path(__file__).with_name('x8_measurement_coordinator.py')
spec=importlib.util.spec_from_file_location('x8_measurement_coordinator',PATH)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value),encoding='utf-8')


class CoordinatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.budget=self.root/'budget.json'
        write(self.budget,{'format':'x8_measurement_budget_v1','total_limit_seconds':1200,
            'per_trial_limit_seconds':120,'setup_limit_seconds':120,'cohort_reservation_seconds':600,
            'native_reservation_seconds':120,'stages':[{'name':'historical_stress_01','status':'matched',
            'elapsed_seconds':18.5932752,'receipt':'historical.json'}],
            'elapsed_seconds':18.5932752,'remaining_seconds':1181.4067248})
        self.source=self.root/'source.py'
        self.source.write_text('# frozen dummy source\n')
        self.manifest=self.root/'manifest.json'
        write(self.manifest,{'format':'x8_source_manifest_v1','files':{'source.py':m.sha(self.source.read_bytes())}})
        self.inputs=self.root/'inputs.json'
        self.inputs.write_text('{}')
        self.outputs=self.root/'worker'/'trial'
        self.receipts=self.root/'control'

    def invoke(self,name='case',kind='parity',**extra):
        return m.run_one(name=name,kind=kind,command=['source.py'],source_manifest=self.manifest,
            output_dir=self.outputs,inputs=self.inputs,inputs_sha256=m.sha(b'{}'),
            budget_path=self.budget,receipt_root=self.receipts,root=self.root,**extra)

    def worker(self,action=None,code=0):
        process=unittest.mock.Mock()
        process.pid=101
        process.returncode=code
        def wait(timeout=None):
            self.outputs.mkdir(parents=True,exist_ok=True)
            (self.outputs/'result.json').write_text('{"value":1}')
            if action:action()
            return code
        process.wait.side_effect=wait
        return process

    def test_success_debits_and_binds_receipts(self):
        with patch.object(m.subprocess,'Popen',return_value=self.worker()) as spawn:
            result=self.invoke()
        self.assertEqual(result['status'],'completed')
        self.assertEqual(spawn.call_args.args[0],[m.sys.executable,'-B','source.py'])
        budget=json.loads(self.budget.read_text())
        self.assertGreater(budget['elapsed_seconds'],18.5932752)
        self.assertEqual(len(budget['stages']),2)
        self.assertTrue((self.receipts/'case'/'start.json').is_file())
        self.assertTrue((self.receipts/'case'/'terminal.json').is_file())
        self.assertFalse(self.budget.with_suffix('.lock').exists())

    def test_completed_reuse_validates_without_restarting(self):
        with patch.object(m.subprocess,'Popen',return_value=self.worker()) as spawn:
            self.invoke()
            before=json.loads(self.budget.read_text())['elapsed_seconds']
            reused=self.invoke()
        self.assertEqual(spawn.call_count,1)
        self.assertTrue(reused['reused'])
        self.assertGreater(json.loads(self.budget.read_text())['elapsed_seconds'],before)

    def test_changed_output_refuses_reuse(self):
        with patch.object(m.subprocess,'Popen',return_value=self.worker()) as spawn:
            self.invoke()
            (self.outputs/'result.json').write_text('changed')
            with self.assertRaisesRegex(ValueError,'output|integrity'):
                self.invoke()
        self.assertEqual(spawn.call_count,1)

    def test_changed_terminal_refuses_reuse(self):
        with patch.object(m.subprocess,'Popen',return_value=self.worker()):self.invoke()
        path=self.receipts/'case'/'terminal.json'
        path.write_text(path.read_text()+' ')
        with self.assertRaisesRegex(ValueError,'terminal|integrity'):self.invoke()

    def test_source_drift_before_child_has_terminal_refusal_and_debit(self):
        self.source.write_text('changed')
        with patch.object(m.subprocess,'Popen') as spawn:
            result=self.invoke()
        self.assertEqual(result['status'],'refused')
        spawn.assert_not_called()
        self.assertGreater(json.loads(self.budget.read_text())['elapsed_seconds'],18.5932752)

    def test_source_drift_after_child_refuses(self):
        with patch.object(m.subprocess,'Popen',return_value=self.worker(lambda:self.source.write_text('changed'))):
            self.assertEqual(self.invoke()['status'],'refused')

    def test_input_drift_after_child_refuses(self):
        with patch.object(m.subprocess,'Popen',return_value=self.worker(lambda:self.inputs.write_text('changed'))):
            self.assertEqual(self.invoke()['status'],'refused')

    def test_timeout_kills_child_and_preserves_failed_stage(self):
        process=self.worker()
        process.wait.side_effect=[subprocess.TimeoutExpired('worker',1),0]
        with patch.object(m.subprocess,'Popen',return_value=process), patch.object(m,'_kill',side_effect=lambda p:(p.kill(),p.wait(timeout=5))):
            result=self.invoke()
        self.assertEqual(result['status'],'timeout')
        process.kill.assert_called_once()
        self.assertEqual(process.wait.call_count,2)
        with self.assertRaisesRegex(ValueError,'failed|incomplete|refus'):
            self.invoke(name='other')

    def test_unconfirmed_tree_termination_keeps_exclusive_lock(self):
        process=self.worker()
        process.wait.side_effect=subprocess.TimeoutExpired('worker',1)
        with patch.object(m.subprocess,'Popen',return_value=process), patch.object(m,'_kill',side_effect=m.WorkerTerminationError('unconfirmed')):
            with self.assertRaisesRegex(ValueError,'termination unconfirmed'):
                self.invoke()
        self.assertTrue(self.budget.with_suffix('.lock').exists())
        self.assertEqual(json.loads((self.receipts/'case'/'terminal.json').read_text())['status'],'interrupted')

    @unittest.skipUnless(m.os.name=='nt','Windows process tree control')
    def test_windows_tree_kill_uses_bounded_taskkill(self):
        process=unittest.mock.Mock(pid=123)
        with patch.object(m.subprocess,'run',return_value=unittest.mock.Mock(returncode=0)) as kill:
            m._kill(process)
        self.assertEqual(kill.call_args.args[0],['taskkill','/PID','123','/T','/F'])
        self.assertEqual(kill.call_args.kwargs['timeout'],5)
        process.wait.assert_called_once_with(timeout=5)

    def test_child_error_never_reruns_same_name(self):
        with patch.object(m.subprocess,'Popen',return_value=self.worker(code=2)) as spawn:
            self.assertEqual(self.invoke()['status'],'error')
            with self.assertRaises(ValueError):self.invoke()
        self.assertEqual(spawn.call_count,1)

    def test_unresolved_lock_refuses_with_unknown_elapsed(self):
        self.budget.with_suffix('.lock').write_text('{}')
        with self.assertRaisesRegex(ValueError,'interrupted|unknown|active'):
            self.invoke()
        self.assertTrue(self.budget.with_suffix('.lock').exists())

    def test_reservations_protect_cohort_and_native(self):
        budget=json.loads(self.budget.read_text())
        self.assertAlmostEqual(m.available_seconds(budget,'setup'),461.4067248)
        self.assertAlmostEqual(m.available_seconds(budget,'cohort'),1061.4067248)
        self.assertAlmostEqual(m.available_seconds(budget,'native'),581.4067248)
        budget['stages'].append({'name':'cohort1','kind':'cohort','elapsed_seconds':80})
        budget['elapsed_seconds']+=80
        budget['remaining_seconds']-=80
        self.assertAlmostEqual(m.available_seconds(budget,'role'),461.4067248)

    def test_existing_worker_output_refuses_without_overwrite(self):
        self.outputs.mkdir(parents=True)
        marker=self.outputs/'partial'
        marker.write_text('keep')
        with patch.object(m.subprocess,'Popen') as spawn:
            self.assertEqual(self.invoke()['status'],'refused')
        spawn.assert_not_called()
        self.assertEqual(marker.read_text(),'keep')

    def test_invalid_input_digest_refuses_without_child(self):
        self.inputs.write_text('different')
        with patch.object(m.subprocess,'Popen') as spawn:
            self.assertEqual(self.invoke()['status'],'refused')
        spawn.assert_not_called()

    def test_budget_total_tamper_refuses(self):
        budget=json.loads(self.budget.read_text())
        budget['elapsed_seconds']=0
        write(self.budget,budget)
        with self.assertRaisesRegex(ValueError,'budget|accounting'):self.invoke()

    def test_directory_name_cannot_escape_control_root(self):
        with self.assertRaises(ValueError):self.invoke(name='../outside')

    def test_updated_manifest_cannot_rebind_between_stages(self):
        with patch.object(m.subprocess,'Popen',return_value=self.worker()) as spawn:
            self.invoke()
            self.source.write_text('changed')
            write(self.manifest,{'format':'x8_source_manifest_v1','files':{'source.py':m.sha(self.source.read_bytes())}})
            self.outputs=self.root/'worker'/'second'
            self.assertEqual(self.invoke(name='second')['status'],'refused')
        self.assertEqual(spawn.call_count,1)

    def test_input_identity_cannot_rebind_between_stages(self):
        with patch.object(m.subprocess,'Popen',return_value=self.worker()) as spawn:
            self.invoke()
            self.inputs=self.root/'different-inputs.json'
            self.inputs.write_text('{"different":true}')
            self.outputs=self.root/'worker'/'second'
            result=m.run_one(name='second',kind='parity',command=['source.py'],source_manifest=self.manifest,
                output_dir=self.outputs,inputs=self.inputs,inputs_sha256=m.sha(self.inputs.read_bytes()),
                budget_path=self.budget,receipt_root=self.receipts,root=self.root)
            self.assertEqual(result['status'],'refused')
        self.assertEqual(spawn.call_count,1)

    def test_analysis_does_not_consume_single_publication_repair(self):
        with patch.object(m.subprocess,'Popen',return_value=self.worker()):
            self.invoke(kind='analysis')
            self.outputs=self.root/'worker'/'publication'
            self.assertEqual(self.invoke(name='repair',kind='publication')['status'],'completed')

    def test_slow_reuse_does_not_return_original_success(self):
        with patch.object(m.subprocess,'Popen',return_value=self.worker()):self.invoke()
        original=m.output_snapshot
        clock=[0.0]
        def slow(output,control):
            clock[0]+=121
            return original(output,control)
        with patch.object(m.time,'perf_counter',side_effect=lambda:clock[0]), patch.object(m,'output_snapshot',side_effect=slow):
            with self.assertRaisesRegex(ValueError,'exceeded|timeout'):
                self.invoke()
        self.assertEqual(json.loads(self.budget.read_text())['validations'][-1]['status'],'timeout')

    def make_cohort(self):
        paths=[]
        with patch.object(m.subprocess,'Popen',side_effect=lambda *a,**k:self.worker()):
            for index in range(40):
                name=f'cohort-{index:02d}'
                self.outputs=self.root/'worker'/name
                m.run_one(name=name,kind='cohort',command=['source.py','case','--backend','package',
                    '--arm','ABCD'[index%4],'--seed',str(20260700+index//4),'--stage','cohort'],
                    source_manifest=self.manifest,output_dir=self.outputs,inputs=self.inputs,
                    inputs_sha256=m.sha(b'{}'),budget_path=self.budget,receipt_root=self.receipts,root=self.root)
                paths.append(self.receipts/name/'terminal.json')
        return paths

    def release(self,paths):
        return m.release_reservation(kind='cohort',completed_receipts=paths,
            budget_path=self.budget,receipt_root=self.receipts,root=self.root)

    def test_release_requires_exact_fixed_completed_cohort_and_debits_proof(self):
        paths=self.make_cohort()
        before=json.loads(self.budget.read_text())
        result=self.release(paths)
        after=json.loads(self.budget.read_text())
        self.assertEqual(result['status'],'completed')
        self.assertIn('cohort',after['reservation_releases'])
        self.assertGreater(after['elapsed_seconds'],before['elapsed_seconds'])
        self.assertGreater(m.available_seconds(after,'role'),m.available_seconds(before,'role')+500)
        self.assertEqual(after['total_limit_seconds'],1200)

    def test_release_can_use_completed_cohort_reserve_at_boundary(self):
        paths=self.make_cohort()
        budget=json.loads(self.budget.read_text())
        budget['stages'][0]['elapsed_seconds']=480
        m.retotal(budget)
        write(self.budget,budget)
        self.assertAlmostEqual(m.available_seconds(budget,'analysis'),0)
        self.assertEqual(self.release(paths)['status'],'completed')
        after=json.loads(self.budget.read_text())
        self.assertGreater(after['remaining_seconds'],120)

    def test_release_refuses_duplicate_or_missing_cohort_paths(self):
        paths=self.make_cohort()
        with self.assertRaisesRegex(ValueError,'40|unique'):
            self.release(paths[:-1]+[paths[0]])

    def test_release_refuses_corrupt_worker_outcome(self):
        paths=self.make_cohort()
        self.outputs.joinpath('result.json').write_text('changed')
        with self.assertRaisesRegex(ValueError,'output|integrity'):
            self.release(paths)
        self.assertNotIn('cohort',json.loads(self.budget.read_text()).get('reservation_releases',{}))

    def test_publication_repair_limit_is_one(self):
        with patch.object(m.subprocess,'Popen',return_value=self.worker()):self.invoke(kind='publication')
        with self.assertRaisesRegex(ValueError,'publication'):
            self.invoke(name='second',kind='publication')


if __name__=='__main__':unittest.main()
