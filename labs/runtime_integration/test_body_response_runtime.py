"""Preregistered body model integration; operational probes, not care qualification."""
from copy import deepcopy
import hashlib
import importlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'packages/mecha_engine/src'))
from mecha_engine.runtime import evolve, live_cycle
from mecha_engine.runtime.care import observed_care_episode, select_care_successor, validate_care_context
from mecha_engine.lifecycle import initial_state, advance_tick
from mecha_engine.generation import train_generation_model
from mecha_engine.repair import train_repair_model
from test_observed_care_selection import context
import survival_population
import survival_live

ROOT=Path(__file__).resolve().parents[2]
MODEL='workload-v1'
class BodyResponseRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid=json.loads((ROOT/'data/seed_grids/mg_seed_001.json').read_text(encoding='utf-8'))
        cls.slip=json.loads((ROOT/'data/slips/valid/slip_lcd_seed.json').read_text(encoding='utf-8'))
        cls.model=train_generation_model([cls.grid])
        cls.repair=train_repair_model([cls.grid],epochs=1,rng_seed=7)
        cls.args=dict(readability_scorer=lambda g:.5,generations=1,population=2,damage_cycles=1,ticks=3,dropout_rate=0,rng_seed=73)

    def test_pre_seam_legacy_results_are_exact(self):
        g,s,m,r=self.grid,self.slip,self.model,self.repair
        values=dict(evolve=evolve([g],s,m,r,**self.args),survivors=evolve([g],s,m,r,**self.args,population_policy='generation_survivors_v1',founder_start_mode='bootstrap'),live=live_cycle(g,s,r,damage_cycles=1,ticks=3,dropout_rate=0,rng_seed=73),care=observed_care_episode(g,s,context(),rng_seed=73,policy='observed_care_selection_v2'),selection=select_care_successor(g,m,s,context=context(),rng_seed=73,policy='observed_care_selection_v2'))
        digest=hashlib.sha256(json.dumps(values,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        self.assertEqual('8bf9d197a1367825db218864519d6cad1ce318669411d9c233ac53f2e521ffbb',digest)
        self.assertEqual(values['evolve'],evolve([g],s,m,r,**self.args,body_response='legacy'))
        self.assertEqual(values['live'],live_cycle(g,s,r,damage_cycles=1,ticks=3,dropout_rate=0,rng_seed=73,body_response='legacy'))

    def test_active_runtime_consumes_each_actual_repaired_projection(self):
        observed=[]
        _,report=evolve([self.grid],self.slip,self.model,self.repair,**self.args,
            body_response=MODEL,population_policy='generation_survivors_v1',founder_start_mode='bootstrap',evaluation_callback=observed.append)
        self.assertEqual(MODEL,report['body_response'])
        self.assertEqual(2,len(observed))
        for row in observed:
            for cycle in row['cycles']:
                expected=initial_state(cycle['frames']['repaired_grid'],self.slip,body_response=MODEL)['body_workload']
                self.assertEqual(expected,cycle['episode']['body_workload'])
                self.assertEqual(MODEL,cycle['episode']['body_response'])
            self.assertEqual(initial_state(row['final_grid'],self.slip,body_response=MODEL)['body_workload'],row['final_episode']['body_workload'])

    def test_model_conflicts_refuse_even_when_selection_is_off(self):
        active=context();active['body_response']=MODEL
        self.assertEqual(active,validate_care_context(active))
        for bad in ('legacy','unknown',None,1):
            value={**active,'body_response':bad}
            with self.subTest(bad=bad),self.assertRaises(ValueError):validate_care_context(value)
        for chosen,ctx in ((MODEL,context()),('legacy',active)):
            with self.subTest(chosen=chosen),self.assertRaisesRegex(ValueError,'body'):
                select_care_successor(self.grid,self.model,self.slip,context=ctx,rng_seed=73,policy='off',body_response=chosen)
        with self.assertRaisesRegex(ValueError,'body'):
            evolve([self.grid],self.slip,self.model,self.repair,**self.args,founder_grids=[self.grid],founder_care_contexts=[active])

    def test_active_care_uses_shared_play_arithmetic_and_binds_receipt(self):
        ctx=context(2);ctx['body_response']=MODEL
        for e in ctx['events']:e['action']='play'
        ctx['care_summary']['keeper_actions']={'play':2}
        episode=observed_care_episode(self.grid,self.slip,ctx,rng_seed=73,evaluator='pristine',policy='observed_care_selection_v2',body_response=MODEL)
        direct=initial_state(self.grid,self.slip,body_response=MODEL)
        for _ in range(2):direct=advance_tick(direct,'play')
        self.assertEqual(direct['energy'],episode['final_state']['energy'])
        self.assertEqual(MODEL,episode['body_response'])
        _,receipt=select_care_successor(self.grid,self.model,self.slip,context=ctx,rng_seed=73,policy='observed_care_selection_v2',body_response=MODEL)
        self.assertEqual(MODEL,receipt['body_response'])
        self.assertTrue(all(r['episode']['body_response']==MODEL for r in receipt['candidates']))

    def test_active_v1_selection_also_records_each_actual_candidate_episode(self):
        ctx=context(2);ctx['body_response']=MODEL
        _,receipt=select_care_successor(self.grid,self.model,self.slip,context=ctx,rng_seed=73,policy='observed_care_selection_v1',body_response=MODEL)
        for row in receipt['candidates']:
            self.assertEqual(row['grid_id'],row['candidate_grid']['grid_id'])
            self.assertEqual(MODEL,row['episode']['body_response'])
            self.assertEqual(2,len(row['episode']['trajectory']))
            self.assertEqual(0,row['episode']['initial_state']['age_ticks'])
            self.assertEqual(row['episode']['body_workload'],row['episode']['final_state']['body_workload'])

    def test_unknown_runtime_model_refuses_before_generation(self):
        with self.assertRaisesRegex(ValueError,'body'):
            evolve([self.grid],self.slip,self.model,self.repair,**self.args,body_response='workload-v9')
        with self.assertRaisesRegex(ValueError,'body'):
            live_cycle(self.grid,self.slip,self.repair,body_response='workload-v9')

    def test_laboratory_mirrors_and_active_results_match(self):
        self.assertEqual((ROOT/'labs/runtime_integration/observed_care_selection.py').read_bytes(),(ROOT/'packages/mecha_engine/src/mecha_engine/runtime/_observed_care.py').read_bytes())
        self.assertEqual((ROOT/'labs/runtime_integration/survival_live.py').read_bytes(),(ROOT/'packages/mecha_engine/src/mecha_engine/runtime/_survival_live.py').read_bytes())
        self.assertEqual((ROOT/'labs/runtime_integration/survival_population.py').read_text(encoding='utf-8').replace('from survival_live import','from ._survival_live import'),(ROOT/'packages/mecha_engine/src/mecha_engine/runtime/_survival_population.py').read_text(encoding='utf-8'))
        options=dict(**self.args,body_response=MODEL,population_policy='generation_survivors_v1',founder_start_mode='bootstrap')
        self.assertEqual(survival_population.evolve([self.grid],self.slip,self.model,self.repair,**options),evolve([self.grid],self.slip,self.model,self.repair,**options))

if __name__=='__main__':unittest.main()
