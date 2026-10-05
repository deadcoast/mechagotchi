"""U1: recording the original evaluation is observational, never another life."""
import copy
import importlib
import json
import random
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'packages/mecha_engine/src'))
import mecha_engine_runtime_loop as lab
from corpus_builder import build_seed_grids
from readability_benchmark import score_readability
from mecha_engine.generation import train_generation_model
from mecha_engine.repair import train_repair_model
from mecha_engine.runtime import evolve


class OriginalRecordingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seeds = build_seed_grids()
        cls.slip = json.loads((ROOT / 'data/slips/valid/slip_lcd_seed.json').read_text(encoding='utf-8'))
        cls.generation = train_generation_model(cls.seeds)
        cls.repair = train_repair_model(cls.seeds[:40], epochs=2, rng_seed=20260512)
        cls.config = dict(generations=2, population=2, damage_cycles=2, ticks=4,
                          dropout_rate=.2, rng_seed=20260512)

    def package(self, **kwargs):
        return evolve(self.seeds, self.slip, self.generation, self.repair,
                      readability_scorer=score_readability, **self.config, **kwargs)

    def test_lab_recording_keeps_the_complete_report_identical(self):
        records = []
        plain = lab.run_mecha_engine_evolution_loop(repair_epochs=2, **self.config)
        observed = lab.run_mecha_engine_evolution_loop(repair_epochs=2,
            recording_callback=records.append, **self.config)
        self.assertEqual(plain, observed)
        self.assertTrue(records)
        for record in records:
            self.assertEqual(record['run_seed'], self.config['rng_seed'] +
                             record['generation_index'] * 100000 + record['candidate_index'])
            self.assertEqual(record['effective_dropout_rate'], .2)
            generation = observed['generations'][record['generation_index']]
            creature = generation['creatures'][record['candidate_index']]
            self.assertEqual(creature['cycles'], [{k:v for k,v in c.items() if k != 'frames'}
                                                 for c in record['lived']['cycles']])
            for cycle in record['lived']['cycles']:
                self.assertEqual(cycle['removed_cell_count'], len(cycle['frames']['removed_cells']))
                if cycle['episode'] is not None:
                    self.assertEqual(cycle['episode']['survival_ticks'], len(cycle['frames']['episode_history']))

    def test_lab_and_package_capture_identical_original_best_evaluations(self):
        left, right = [], []
        lab.run_mecha_engine_evolution_loop(repair_epochs=2,
            recording_callback=left.append, **self.config)
        plain = self.package()
        observed = self.package(recording_callback=right.append)
        self.assertEqual(plain, observed)
        self.assertEqual(left, right)
        archive, report = observed
        niche = max(archive['elites'], key=lambda n: (archive['elites'][n]['fitness'], n))
        self.assertEqual(niche, right[-1]['niche_key'])
        self.assertEqual(archive['elites'][niche]['grid'], right[-1]['lived']['final_grid'])
        self.assertEqual(plain, self.package(recording_callback=None))

    def test_capture_uses_actual_calls_and_cannot_mutate_engine_state(self):
        module = importlib.import_module('mecha_engine.runtime.evolve')
        original_live = module.live_cycle
        actual = []
        def capture(*args, **kwargs):
            result = original_live(*args, **kwargs)
            actual.append(copy.deepcopy(result))
            return result
        inputs = copy.deepcopy((self.seeds, self.slip, self.generation, self.repair))
        plain = self.package()
        records = []
        def observer(record):
            records.append(copy.deepcopy(record))
            record['candidate_grid'].clear()
            record['lived']['cycles'].clear()
        state = random.getstate()
        with patch.object(module, 'live_cycle', side_effect=capture) as live_calls:
            observed = self.package(recording_callback=observer)
        self.assertEqual(plain, observed)
        self.assertEqual(4, live_calls.call_count)
        self.assertEqual(state, random.getstate())
        self.assertEqual(inputs, (self.seeds, self.slip, self.generation, self.repair))
        for record in records:
            self.assertEqual(actual[record['generation_index'] * 2 + record['candidate_index']], record['lived'])

    def test_recording_exception_propagates_without_input_mutation(self):
        inputs = copy.deepcopy((self.seeds, self.slip, self.generation, self.repair))
        def stop(record):
            raise RuntimeError('recording stopped')
        with self.assertRaisesRegex(RuntimeError, 'recording stopped'):
            self.package(recording_callback=stop)
        with self.assertRaisesRegex(RuntimeError, 'recording stopped'):
            lab.run_mecha_engine_evolution_loop(repair_epochs=2, recording_callback=stop, **self.config)
        self.assertEqual(inputs, (self.seeds, self.slip, self.generation, self.repair))


    def test_actual_weather_and_candidate_seeds_match_lab_and_package(self):
        from test_cubff_pressure import CHAOTIC
        left, right = [], []
        expected = self.package(cubff_pressure_source=CHAOTIC)
        actual = self.package(cubff_pressure_source=CHAOTIC, recording_callback=right.append)
        self.assertEqual(expected, actual)
        lab.run_mecha_engine_evolution_loop(repair_epochs=2, cubff_pressure_source=CHAOTIC,
            recording_callback=left.append, **self.config)
        self.assertEqual(left, right)
        self.assertTrue(right)
        for record in right:
            pressure = actual[1]['cubff_pressure']['by_generation'][record['generation_index']]
            self.assertEqual(pressure, record['generation_weather'])
            self.assertEqual(round(.2 * pressure['dropout_multiplier'], 6), record['effective_dropout_rate'])
            self.assertNotEqual(.2, record['effective_dropout_rate'])

    def test_equal_fitness_uses_existing_niche_tie_order_and_no_extra_calls(self):
        module = importlib.import_module('mecha_engine.runtime.evolve')
        original_score = module.score_candidate
        def tie(*args, **kwargs):
            score = original_score(*args, **kwargs)
            return dict(score, fitness=1.0)
        records = []
        with patch.object(module, 'score_candidate', side_effect=tie) as scoring, \
             patch.object(module, 'generate_candidate', wraps=module.generate_candidate) as generation, \
             patch.object(module, 'run_episode', wraps=module.run_episode) as episodes:
            expected = self.package()
            counts = (scoring.call_count, generation.call_count, episodes.call_count)
            scoring.reset_mock(); generation.reset_mock(); episodes.reset_mock()
            actual = self.package(recording_callback=records.append)
            self.assertEqual(counts, (scoring.call_count, generation.call_count, episodes.call_count))
        self.assertEqual(expected, actual)
        niche = max(actual[0]['elites'])
        self.assertEqual(niche, records[-1]['niche_key'])
        self.assertEqual(actual[0]['elites'][niche]['grid'], records[-1]['lived']['final_grid'])
