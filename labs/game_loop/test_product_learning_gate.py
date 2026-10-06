"""X7 product learning gates: real sessions, exact thresholds and bound evidence."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent))
from product_learning_gate import (
    ARMS, REQUIRED, SOURCES, build_plan, check_receipts, gain_at_least,
    judge, make_receipt, read_json, run_trial, snapshot_sources, summarize, supervise, write_json,
    gain_rows_at_least, validate_manifest, prepare_instrument_repair, verify_repaired_prefix,
)
from playable_learning_gate import load_inputs, run_trial as historical_trial


class ProductLearningGateTests(unittest.TestCase):
    def test_every_scientific_gate_binds(self):
        checks = {name: True for name in REQUIRED}
        self.assertEqual('ADOPT', judge(checks)['verdict'])
        for name in REQUIRED:
            for value in (False, None, 1):
                self.assertEqual('REFUSE', judge(dict(checks, **{name:value}))['verdict'])
            missing = dict(checks); missing.pop(name)
            self.assertEqual('REFUSE', judge(missing)['verdict'])

    def test_both_exact_thresholds_do_not_round_into_adoption(self):
        self.assertTrue(gain_at_least(.105, .1))
        self.assertFalse(gain_at_least(.1049996, .1))
        for candidate, baseline in ((None,.1),(.2,None),(.2,0),(.2,-1)):
            self.assertFalse(gain_at_least(candidate,baseline))

    def test_complete_paired_plan_has_registered_mapping(self):
        plan=build_plan()
        self.assertEqual(1500,len(plan))
        for offset in range(0,len(plan),3):
            triple=plan[offset:offset+3]
            self.assertEqual(list(ARMS),[row['arm'] for row in triple])
            self.assertEqual(1,len({(row['keeper_id'],row['rng_seed'],row['founder_index']) for row in triple}))
        self.assertEqual(0,plan[0]['founder_index'])
        self.assertEqual(49,plan[-1]['founder_index'])
        self.assertEqual(20260709+400000+99,plan[-1]['rng_seed'])

    def test_receipt_chain_rejects_tampering_reordering_and_source_mix(self):
        plan=build_plan()
        first=make_receipt(0,dict(plan[0],status='admitted'), 'manifest-a', None, .1)
        second=make_receipt(1,dict(plan[1],status='admitted'), 'manifest-a',first['receipt_sha256'],.2)
        self.assertEqual(2,len(check_receipts([first,second],'manifest-a',plan)))
        variants=[]
        changed=copy.deepcopy(first);changed['row']['rng_seed']+=1;variants.append([changed])
        variants.extend(([second,first],[first,first]))
        for rows in variants:
            with self.assertRaises(ValueError):check_receipts(rows,'manifest-a',plan)
        with self.assertRaises(ValueError):check_receipts([first],'manifest-b',plan)

    def test_real_session_projection_matches_original_instrument(self):
        seeds,slip,models=load_inputs()
        for arm in ARMS:
            expected=historical_trial(seeds[0],slip,models[0],'attentive',arm,20,20260709)
            actual=run_trial(seeds[0],slip,models[0],'attentive',arm,20,20260709)
            self.assertEqual(expected,{key:actual[key] for key in expected})
            self.assertEqual(0,actual['initial_qtable_entries'])
            self.assertEqual(actual['executed_actions']['feed'],actual['keeper_actions']['feed'])
            self.assertEqual(64,len(actual['trajectory_sha256']))
            self.assertEqual(actual,run_trial(seeds[0],slip,models[0],'attentive',arm,20,20260709))
        refused=run_trial(seeds[1],slip,models[1],'attentive','follower',20,20260710)
        self.assertEqual('refused',refused['status'])
        self.assertNotIn('welfare',refused)
        self.assertIsNone(summarize([actual,refused])['welfare'])

    def test_death_keeps_requested_horizon_and_failure_diagnostics(self):
        seeds,slip,models=load_inputs()
        row=run_trial(seeds[0],slip,models[0],'punitive','follower',200,20260709)
        self.assertFalse(row['alive'])
        self.assertLess(row['survival_ticks'],200)
        self.assertTrue(row['death_cause'])
        self.assertGreater(sum(row['danger_ticks'].values()),0)
        summary=summarize([row])
        self.assertEqual(1,summary['deaths_before_horizon'])
        self.assertEqual(1,summary['death_causes'][row['death_cause']])
        self.assertEqual(row['welfare'],summary['welfare'])

    def test_terminal_refusal_and_source_change_cannot_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            write_json(root/'budget.json',dict(state='refused',consumed_seconds=1))
            with self.assertRaisesRegex(ValueError,'Only an interrupted'):
                supervise(root,resume=True)
            write_json(root/'budget.json',dict(state='interrupted',consumed_seconds=1))
            write_json(root/'manifest.json',dict(source_sha256={'stale':'source'}))
            with self.assertRaisesRegex(ValueError,'source inputs differ'):
                supervise(root,resume=True)

    def test_foreground_watchdog_terminates_and_records_timeout(self):
        class Worker:
            pid=12345
            returncode=None
            terminated=False
            def poll(self):return self.returncode
            def terminate(self):self.terminated=True;self.returncode=-1
            def wait(self,timeout):return self.returncode
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'study';worker=Worker()
            clock=iter([0,0,0,121,121,121,121,121])
            with patch('product_learning_gate.subprocess.Popen',return_value=worker), \
                 patch('product_learning_gate.time.monotonic',side_effect=lambda:next(clock)), \
                 patch('product_learning_gate.time.sleep'), \
                 patch('product_learning_gate.build_report',return_value={'status':'incomplete'}):
                supervise(output)
            self.assertTrue(worker.terminated)
            self.assertEqual('setup_runtime_limit',read_json(output/'failure.json')['reason'])
            self.assertEqual('refused',read_json(output/'budget.json')['state'])

    def test_trial_and_total_watchdogs_bind_independently(self):
        class Worker:
            pid=12345
            returncode=None
            def poll(self):return self.returncode
            def terminate(self):self.returncode=-1
            def wait(self,timeout):return self.returncode
        for elapsed,reason in ((21,'trial_runtime_limit'),(1201,'cumulative_runtime_limit')):
            with self.subTest(reason=reason), tempfile.TemporaryDirectory() as directory:
                output=Path(directory)/'study';worker=Worker()
                def launch(*args,**kwargs):
                    write_json(output/'progress.json',dict(phase='trial',index=0,started=0))
                    return worker
                clock=iter([0,0,elapsed,elapsed,elapsed,elapsed,elapsed])
                with patch('product_learning_gate.subprocess.Popen',side_effect=launch), \
                     patch('product_learning_gate.time.monotonic',side_effect=lambda:next(clock)), \
                     patch('product_learning_gate.time.sleep'), \
                     patch('product_learning_gate.build_report',return_value={'status':'incomplete'}):
                    supervise(output)
                self.assertEqual(reason,read_json(output/'failure.json')['reason'])
                self.assertEqual(-1,worker.returncode)

    def test_aggregate_mean_cannot_round_up_to_five_percent(self):
        baseline=[dict(status='admitted',welfare=.1)]*5
        below=[dict(status='admitted',welfare=value) for value in (.105,.105,.105,.105,.104998)]
        exact=[dict(status='admitted',welfare=.105)]*5
        self.assertEqual(.105,round(sum(row['welfare'] for row in below)/5,6))
        self.assertFalse(gain_rows_at_least(below,baseline))
        self.assertTrue(gain_rows_at_least(exact,baseline))

    def test_mutable_plan_cannot_redefine_the_registered_cohort(self):
        import product_learning_gate as gate
        good=dict(format=gate.FORMAT,hatch_seed=gate.HATCH_SEED,plan=build_plan(),
            budgets=dict(setup_seconds=120.,trial_seconds=20.,total_seconds=1200.),
            covenant=read_json(gate.ROOT/gate.COVENANT))
        changed=copy.deepcopy(good);changed['plan']=[changed['plan'][0]]*1500
        with self.assertRaisesRegex(ValueError,'preregistered study'):validate_manifest(changed)
        for field,value in (('hatch_seed',1),('budgets',{}),('covenant',{})):
            changed=copy.deepcopy(good);changed[field]=value
            with self.assertRaisesRegex(ValueError,'preregistered study'):validate_manifest(changed)

    def test_receipts_reject_nonfinite_or_negative_runtime(self):
        plan=build_plan()
        for value in (-1,float('nan'),float('inf'),True):
            if value in (-1,True):
                receipt=make_receipt(0,dict(plan[0],status='admitted'),'m',None,value)
                with self.assertRaisesRegex(ValueError,'runtime'):check_receipts([receipt],'m',plan)
            else:
                with self.assertRaises(ValueError):make_receipt(0,dict(plan[0],status='admitted'),'m',None,value)

    def test_windows_atomic_publication_retries_only_bounded_sharing_errors(self):
        import product_learning_gate as gate
        error=PermissionError('sharing violation');error.winerror=5
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'progress.json'
            with patch('product_learning_gate.os.replace',side_effect=[error,None]) as replace, \
                 patch('product_learning_gate.time.sleep') as sleep:
                write_json(path,{'phase':'trial'})
            self.assertEqual(2,replace.call_count)
            sleep.assert_called_once_with(.01)
            with patch('product_learning_gate.os.replace',side_effect=error) as replace, \
                 patch('product_learning_gate.time.sleep') as sleep:
                with self.assertRaises(PermissionError):write_json(path,{'phase':'trial'})
            self.assertEqual(20,replace.call_count)
            self.assertEqual(19,sleep.call_count)
            other=PermissionError('not a sharing race');other.winerror=13
            with patch('product_learning_gate.os.replace',side_effect=other) as replace, \
                 patch('product_learning_gate.time.sleep') as sleep:
                with self.assertRaises(PermissionError):write_json(path,{'phase':'trial'})
            self.assertEqual(1,replace.call_count);sleep.assert_not_called()

    def test_repair_reuses_recorded_inputs_and_refuses_unrelated_source_changes(self):
        import product_learning_gate as gate
        # The failed attempt is durable data; tests never depend on ignored
        # .development directories existing in a fresh checkout.
        report=read_json(gate.ROOT/'data/game_client/product_learning_gate_stage0.json')
        original=report['input_manifest']
        source=dict(original['source_sha256'])
        source[gate.REPAIR_APPENDIX]='new-appendix';source[gate.GATE_SOURCE]='reviewed-repair'
        with tempfile.TemporaryDirectory() as directory:
            prior_path=Path(directory)
            for name,value in (('manifest',original),('budget',report['metrics']['budget']),('failure',report['metrics']['failure'])):
                write_json(prior_path/(name+'.json'),value)
            (prior_path/'worker.stderr.log').write_text('PermissionError: [WinError 5] progress.json',encoding='utf-8')
            previous=None
            for index,row in enumerate(report['metrics']['trials']):
                receipt=make_receipt(index,row,gate.digest(original),previous,.1)
                write_json(prior_path/'rows'/f'{index:04d}.json',receipt)
                previous=receipt['receipt_sha256']
            report['last_receipt_sha256']=previous
            write_json(prior_path/'report.json',report)
            with patch('product_learning_gate.snapshot_sources',return_value=source):
                repaired=prepare_instrument_repair(prior_path)
            for key in ('founders','source_corpus','covenant','plan'):
                self.assertEqual(original[key],repaired[key])
            prior=repaired['instrument_repair']
            self.assertEqual(56,len(prior['prior_completed_rows']))
            self.assertEqual(15.608391000074334,prior['debited_seconds'])
            self.assertAlmostEqual(104.39160899992567,prior['remaining_setup_seconds'])
            self.assertAlmostEqual(1184.3916089999257,prior['remaining_total_seconds'])
            source['game/src/mecha_game/session.py']='unrelated-change'
            with patch('product_learning_gate.snapshot_sources',return_value=source):
                with self.assertRaisesRegex(ValueError,'beyond the reviewed harness'):
                    prepare_instrument_repair(prior_path)

    def test_repair_prefix_mismatch_is_a_hard_failure(self):
        row={'welfare':.1,'rng_seed':20260709}
        manifest={'instrument_repair':{'prior_completed_rows':[row]}}
        verify_repaired_prefix(dict(row),0,manifest)
        with self.assertRaisesRegex(ValueError,'exactly reproduce'):
            verify_repaired_prefix(dict(row,welfare=.2),0,manifest)

    def test_repair_supervisor_debits_prior_runtime_from_setup_and_total(self):
        import product_learning_gate as gate
        class Worker:
            pid=12345
            returncode=None
            def poll(self):return self.returncode
            def terminate(self):self.returncode=-1
            def wait(self,timeout):return self.returncode
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);output=root/'.development/x7/learning-instrument-repair-01'
            clock=iter([0,0,105,105,105,105,105])
            with patch('product_learning_gate.ROOT',root), \
                 patch('product_learning_gate.prepare_instrument_repair',return_value={'instrument_repair':{'debited_seconds':15.608391000074334}}), \
                 patch('product_learning_gate.subprocess.Popen',return_value=Worker()), \
                 patch('product_learning_gate.time.monotonic',side_effect=lambda:next(clock)), \
                 patch('product_learning_gate.time.sleep'), \
                 patch('product_learning_gate.build_report',return_value={'status':'incomplete'}):
                supervise(output,instrument_repair_from=root/'.development/x7/learning')
            budget=read_json(output/'budget.json')
            self.assertAlmostEqual(120.60839100007433,budget['consumed_seconds'])
            self.assertAlmostEqual(104.39160899992567,budget['remaining_setup_seconds'])
            self.assertEqual('setup_runtime_limit',read_json(output/'failure.json')['reason'])

    def test_repair_provenance_preparation_is_inside_the_runtime_budget(self):
        class Worker:
            pid=12345
            returncode=0
            def poll(self):return self.returncode
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);output=root/'.development/x7/learning-instrument-repair-01'
            clock=[0.0]
            def prepare(*args):
                clock[0]+=10
                return {'instrument_repair':{'debited_seconds':15.608391000074334}}
            with patch('product_learning_gate.ROOT',root), \
                 patch('product_learning_gate.prepare_instrument_repair',side_effect=prepare), \
                 patch('product_learning_gate.subprocess.Popen',return_value=Worker()), \
                 patch('product_learning_gate.time.monotonic',side_effect=lambda:clock[0]), \
                 patch('product_learning_gate.build_report',return_value={'status':'incomplete'}):
                supervise(output,instrument_repair_from=root/'.development/x7/learning')
            self.assertAlmostEqual(25.608391000074334,read_json(output/'budget.json')['consumed_seconds'])

if __name__=='__main__':unittest.main()
