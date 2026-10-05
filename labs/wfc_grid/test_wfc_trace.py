"""W4 observational trace: frozen pre-edit RNG/output/error and lab/package parity."""
import copy
import hashlib
import json
from pathlib import Path
import random
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'labs/wfc_grid'),str(ROOT/'labs/grid_genome'),str(ROOT/'packages/mecha_engine/src')]
import wfc_grid as lab

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
BASE=json.loads((ROOT/'data/game_client/wfc_trace_before_stage0.json').read_text())

def observe(module,case,enabled=True):
    seen=[];events=[];original=random.Random
    class RecordingRandom(original):
        def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);seen.append(self)
    kwargs={k:case[k] for k in ('grid_id','rng_seed','max_restarts')}
    if enabled:kwargs['trace']=events
    with patch.object(module.random,'Random',RecordingRandom):
        try:grid=module.generate_wfc_grid(BASE['models'][case['model']],**kwargs);outcome={'grid_sha256':digest(grid)}
        except (ValueError,KeyError) as error:outcome={'error_type':type(error).__name__,'error':str(error)};grid=None
    return {**outcome,'rng_state_sha256':digest(seen[0].getstate())},events,grid

class WfcTraceLabTests(unittest.TestCase):
    def test_all_pre_edit_results_errors_and_rng_end_states_unchanged(self):
        for case in BASE['cases']:
            expected={k:case[k] for k in ('grid_sha256','error_type','error','rng_state_sha256') if k in case}
            for enabled in (False,True):
                with self.subTest(model=case['model'],seed=case['rng_seed'],trace=enabled):
                    self.assertEqual(expected,observe(lab,case,enabled)[0])

    def test_real_finish_restarts_and_exhaustion_retained(self):
        traces=[observe(lab,c)[1] for c in BASE['cases'] if c['model']=='finish_retry']
        self.assertTrue(any(any(e['event']=='attempt_rejected' for e in t) and t[-1]['event']=='generated' for t in traces))
        case=next(c for c in BASE['cases'] if c['model']=='contradiction' and c['max_restarts']==8)
        result,trace,grid=observe(lab,case)
        self.assertIsNone(grid);self.assertEqual('exhausted',trace[-1]['event'])
        self.assertEqual(8,sum(e['event']=='attempt_started' for e in trace))
        rejected=[e for e in trace if e['event']=='contradiction']
        self.assertEqual(8,len(rejected));self.assertTrue(all(e['remaining']=={} for e in rejected))
        self.assertEqual('wave contradiction',trace[-1]['reason'])

    def test_trace_decisions_are_observed_and_detached(self):
        case=BASE['cases'][0];model=BASE['models'][case['model']];before=copy.deepcopy(model)
        _,trace,grid=observe(lab,case)
        self.assertEqual('wfc_trace_v1',trace[0]['trace_format'])
        self.assertEqual(before,model);self.assertNotIn('wfc_trace',grid['metadata'])
        waves=[e for e in trace if e['event']=='wave_started'];self.assertTrue(waves)
        self.assertEqual(model['position_candidates'],waves[0]['cells'])
        choices=[e for e in trace if e['event']=='cell_collapsed'];self.assertTrue(choices)
        self.assertTrue(all(e['token'] in e['choices'] for e in choices))
        finished=next(e for e in trace if e['event']=='finished')
        self.assertEqual(finished['matrix'],[''.join(row) for row in lab.rich_matrix_from_grid(grid)])
        waves[0]['cells']['0,0']['external']=100
        self.assertEqual(before,model)
        self.assertEqual(trace,json.loads(json.dumps(trace)))

    def test_zero_attempt_error_has_no_invented_wave(self):
        case=next(c for c in BASE['cases'] if c['max_restarts']==0)
        _,trace,_=observe(lab,case)
        self.assertEqual(['generation_started','exhausted'],[e['event'] for e in trace])

class WfcTraceParityTests(unittest.TestCase):
    def test_package_matches_lab_events_and_frozen_behavior(self):
        from mecha_engine.generation import wfc as package
        for case in BASE['cases']:
            with self.subTest(model=case['model'],seed=case['rng_seed']):
                self.assertEqual(observe(lab,case),observe(package,case))

if __name__=='__main__':unittest.main()
