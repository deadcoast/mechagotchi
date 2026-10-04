"""T5: observational progress and interruption preserve the engine's science."""
import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'packages/mecha_engine/src'))
import mecha_engine_runtime_loop as lab
from corpus_builder import build_seed_grids
from readability_benchmark import score_readability
from mecha_engine.generation import train_generation_model
from mecha_engine.repair import train_repair_model
from mecha_engine.runtime import evolve

class EvolutionProgressTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import json
        cls.seeds=build_seed_grids()
        cls.slip=json.loads((ROOT/'data/slips/valid/slip_lcd_seed.json').read_text())
        cls.generation=train_generation_model(cls.seeds)
        cls.repair=train_repair_model(cls.seeds[:40],epochs=2,rng_seed=20260512)
        cls.config=dict(generations=2,population=2,damage_cycles=1,ticks=4,dropout_rate=.2,rng_seed=20260512)
    def package(self,**kwargs):
        return evolve(self.seeds,self.slip,self.generation,self.repair,readability_scorer=score_readability,**self.config,**kwargs)
    def test_observer_none_and_counts_are_identical_to_unobserved_complete_results(self):
        before=copy.deepcopy((self.seeds,self.slip,self.generation,self.repair))
        rows=[];plain=self.package();observed=self.package(progress_callback=lambda n,total:rows.append((n,total)))
        self.assertEqual(plain,observed)
        self.assertEqual(plain,self.package(progress_callback=None))
        self.assertEqual([(i,4) for i in range(5)],rows)
        self.assertEqual(before,(self.seeds,self.slip,self.generation,self.repair))
    def test_lab_package_observer_and_scientific_records_match(self):
        left=[];right=[]
        plain=lab.run_mecha_engine_evolution_loop(repair_epochs=2,**self.config)
        observed=lab.run_mecha_engine_evolution_loop(repair_epochs=2,progress_callback=lambda n,total:left.append((n,total)),**self.config)
        _,package=self.package(progress_callback=lambda n,total:right.append((n,total)))
        self.assertEqual(plain,observed)
        self.assertEqual(left,right)
        for key in ('generations','summary'):
            self.assertEqual(observed[key],package[key])
        self.assertEqual(observed['decision']['status'],package['decision']['status'])
    def test_callback_exception_stops_without_mutating_caller_inputs(self):
        class Stop(Exception):pass
        def cancel(n,total):
            if n==1:raise Stop('cancel after one completed candidate')
        before=copy.deepcopy((self.seeds,self.slip,self.generation,self.repair))
        with self.assertRaises(Stop):self.package(progress_callback=cancel)
        with self.assertRaises(Stop):lab.run_mecha_engine_evolution_loop(repair_epochs=2,progress_callback=cancel,**self.config)
        self.assertEqual(before,(self.seeds,self.slip,self.generation,self.repair))
    def test_extinction_counts_actual_completed_work_not_requested_budget(self):
        import importlib
        module=importlib.import_module('mecha_engine.runtime.evolve')
        rows=[]
        with patch.object(module,'insert_candidate',side_effect=lambda archive,*args:archive):
            _,report=self.package(progress_callback=lambda n,total:rows.append((n,total)))
        self.assertEqual([(0,4),(1,4),(2,4)],rows)
        self.assertEqual(1,len(report['generations']))
