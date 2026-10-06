"""Falsifiable v2 cohort, endpoint and bounded-resume contracts."""
from copy import deepcopy
from contextlib import redirect_stdout
from io import StringIO
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import observed_care_v2_gate as gate

class CareV2GateTests(unittest.TestCase):
    def regression(self):
        return {'checks':dict.fromkeys(gate.COMMON_CHECKS,True),'terminal_correction':True,
            'v1_exact':{e+'_'+n:True for e in gate.CARE_EVALUATORS for n in ('fed','neglect')},
            'evaluators':{e:{'checks':dict.fromkeys(gate.REQUIRED_CHECKS,True)} for e in gate.CARE_EVALUATORS},
            'elapsed_seconds':1.0}
    def rows(self,different=True):
        return [{'pair_index':i,'founder_index':gate.FOUNDERS[i%10],'rng_seed':gate.SEEDS[i//10],
            'checks':dict.fromkeys(gate.COMMON_CHECKS,True),'elapsed_seconds':1.0,
            'evaluators':{e:{'checks':dict.fromkeys(gate.REQUIRED_CHECKS,True),'selected_structures_differ':different}
                for e in gate.CARE_EVALUATORS}} for i in range(gate.PAIR_COUNT)]
    def judge(self,rows=None,regression=None,**kwargs):
        return gate.judge(self.rows() if rows is None else rows,self.regression() if regression is None else regression,True,True,**kwargs)
    def test_positive_gate_and_null_refusal(self):
        self.assertTrue(all(d['verdict']=='ADOPT' for d in self.judge().values()))
        self.assertTrue(all(d['verdict']=='REFUSE' and d['failed_checks']==['structural_descendant_effect']
            for d in self.judge(self.rows(False)).values()))
    def test_known_regression_never_counts_as_holdout_effect(self):
        regression=self.regression()
        for row in regression['evaluators'].values():row['selected_structures_differ']=True
        self.assertTrue(all(d['verdict']=='REFUSE' for d in self.judge(self.rows(False),regression).values()))
    def test_each_check_missing_false_or_nonboolean_refuses(self):
        for key in gate.COMMON_CHECKS:
            for value in (False,None,1):
                rows=self.rows();rows[0]['checks'][key]=value
                self.assertTrue(all(d['verdict']=='REFUSE' for d in self.judge(rows).values()))
            rows=self.rows();rows[0]['checks'].pop(key)
            self.assertTrue(all(d['verdict']=='REFUSE' for d in self.judge(rows).values()))
        for evaluator in gate.CARE_EVALUATORS:
            for key in gate.REQUIRED_CHECKS:
                for value in (False,None,1):
                    rows=self.rows();rows[0]['evaluators'][evaluator]['checks'][key]=value
                    self.assertEqual(self.judge(rows)[evaluator]['verdict'],'REFUSE')
                rows=self.rows();rows[0]['evaluators'][evaluator]['checks'].pop(key)
                self.assertEqual(self.judge(rows)[evaluator]['verdict'],'REFUSE')
    def test_welfare_tradeoff_is_refusal_even_when_survival_improves(self):
        rows=self.rows();e=gate.CARE_EVALUATORS[1]
        rows[0]['evaluators'][e]['checks']['neglect_welfare_nonregression']=False
        result=self.judge(rows)
        self.assertEqual(result[e]['verdict'],'REFUSE')
        self.assertEqual(result[gate.CARE_EVALUATORS[0]]['verdict'],'ADOPT')
    def test_missing_duplicate_or_misidentified_holdout_refuses(self):
        for key,value in [('pair_index',1),('founder_index',0),('rng_seed',20260702),('pair_index',False)]:
            rows=self.rows();rows[0][key]=value
            self.assertTrue(all(d['verdict']=='REFUSE' for d in self.judge(rows).values()))
        rows=self.rows();rows[1]=deepcopy(rows[0])
        self.assertTrue(all(d['verdict']=='REFUSE' for d in self.judge(rows).values()))
        self.assertTrue(all(d['verdict']=='REFUSE' for d in self.judge(self.rows()[:-1]).values()))
    def test_regression_failure_and_source_or_runtime_failure_refuse(self):
        regression=self.regression();regression['terminal_correction']=False
        self.assertTrue(all(d['verdict']=='REFUSE' for d in self.judge(regression=regression).values()))
        regression=self.regression();regression['v1_exact'][next(iter(regression['v1_exact']))]=False
        self.assertTrue(all(d['verdict']=='REFUSE' for d in self.judge(regression=regression).values()))
        self.assertTrue(all(d['verdict']=='REFUSE' for d in self.judge(elapsed_seconds=300.001).values()))
        self.assertTrue(all(d['verdict']=='REFUSE' for d in self.judge(setup_elapsed_seconds=30.001).values()))
        rows=self.rows();rows[0]['elapsed_seconds']=30.001
        self.assertTrue(all(d['verdict']=='REFUSE' for d in self.judge(rows).values()))
        self.assertTrue(all(d['verdict']=='REFUSE' for d in self.judge(failure={'kind':'timeout'}).values()))
        self.assertTrue(all(d['verdict']=='REFUSE' for d in gate.judge(self.rows(),self.regression(),True,False).values()))
    def test_safe_resume_requires_boundary_same_source_and_no_inflight(self):
        manifest={'source_sha256':{'test':'source'}}
        cp={'status':'boundary','failure':None,'manifest_sha256':gate.digest(manifest),'consumed_seconds':2}
        with tempfile.TemporaryDirectory() as tmp,patch.object(gate,'sources',return_value=manifest['source_sha256']):
            folder=Path(tmp);gate.validate_resume(folder,manifest,cp)
            for patch_values in ({'status':'running'},{'failure':{}},{'consumed_seconds':300},{'manifest_sha256':'changed'}):
                with self.assertRaises(ValueError):gate.validate_resume(folder,manifest,{**cp,**patch_values})
            gate.write(folder/'rows/pair-00.started.json',{})
            with self.assertRaises(ValueError):gate.validate_resume(folder,manifest,cp)
    def test_watchdog_retains_failed_setup_and_refuses_retry(self):
        import subprocess
        with redirect_stdout(StringIO()),tempfile.TemporaryDirectory() as tmp,patch.object(gate,'relative',return_value='.development/test'),patch.object(gate.subprocess,'run',side_effect=subprocess.TimeoutExpired('freeze',30)) as child:
            folder=Path(tmp)/'run';artifact=Path(tmp)/'artifact.json'
            self.assertEqual(gate.run(folder,Path(tmp)/'unused',artifact),2)
            self.assertLessEqual(child.call_args.kwargs['timeout'],30)
            result=gate.read(artifact)
            self.assertEqual(result['failure']['kind'],'registered_runtime_limit')
            self.assertTrue(all(d['verdict']=='REFUSE' for d in result['decision'].values()))
            with self.assertRaises(ValueError):gate.run(folder,Path(tmp)/'unused',artifact)
    def test_regression_nonregression_is_evaluator_local(self):
        regression=self.regression();e=gate.CARE_EVALUATORS[1]
        regression['evaluators'][e]['checks']['neglect_welfare_nonregression']=False
        result=self.judge(regression=regression)
        self.assertEqual(result[e]['verdict'],'REFUSE')
        self.assertEqual(result[gate.CARE_EVALUATORS[0]]['verdict'],'ADOPT')
    def test_registered_cohort_cannot_be_substituted(self):
        product=gate.read(gate.ROOT/'data/game_client/product_learning_gate_stage0.json')['input_manifest']
        retained=gate.read(gate.ROOT/'data/game_client/product_learning_gate_stage1.json')['input_manifest']
        gate.validate_product(product,retained)
        wrong=deepcopy(product);wrong['admissions'][0]['founder_index']=1
        with self.assertRaises(ValueError):gate.validate_product(wrong,retained)
        with self.assertRaises(ValueError):gate.validate_product({},retained)
    def test_refused_evaluator_cannot_reappear_in_later_receipts(self):
        regression=self.regression();rows=self.rows()[:2];e=gate.CARE_EVALUATORS[1]
        rows[0]['evaluators'][e]['checks']['neglect_welfare_nonregression']=False
        with self.assertRaises(ValueError):gate.derive_evaluator_state(regression,rows)
        rows[1]['evaluators'].pop(e)
        active,refused=gate.derive_evaluator_state(regression,rows)
        self.assertNotIn(e,active);self.assertEqual(refused[e]['pair_index'],0)
    def test_source_closure_and_frozen_inputs(self):
        paths=gate.sources()
        for name in ('game/src/mecha_game/health.py','game/src/mecha_game/happiness.py',gate.CONTRACT,
                     'packages/mecha_engine/src/mecha_engine/slip/__init__.py',
                     'packages/mecha_engine/src/mecha_engine/repair/__init__.py'):self.assertIn(name,paths)

if __name__=='__main__':unittest.main()
