"""X6 additive constrained evolution arm, with pre-change return-value pins."""
import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
for sub in ('labs/map_elites_archive','labs/grid_genome','labs/wfc_grid'):
    sys.path.insert(0,str(ROOT/sub))
from evaluation_loop_scale import run_evaluation_loop
from wfc_population_throughput import constrained_population
from corpus_builder import build_seed_grids_16
from mecha_engine.generation import train_generation_model

ARM='operative_permissions_v1'
PINS=[{'options': {'population': 8, 'target_evaluations': 24, 'rng_seed': 20260709, 'lifecycle_ticks': 4, 'generation': 'wfc', 'selection': 'baseline', 'slip_admission': 'none', 'collect_refusals': False, 'collect_elite_grids': False}, 'sha256': '3caa16bdbedb68b5519c357eacbdd2657c6eea1e069aa2c4350a10d6abf1ad7d'}, {'options': {'population': 8, 'target_evaluations': 24, 'rng_seed': 20260709, 'lifecycle_ticks': 4, 'generation': 'wfc', 'selection': 'novelty_first', 'slip_admission': 'insertion', 'collect_refusals': True, 'collect_elite_grids': True}, 'sha256': 'c1d57b7b1a2a525f5262205256bfd7b2ce483ee4ee3ef953c6a0efc445045aa6'}, {'options': {'population': 8, 'target_evaluations': 24, 'rng_seed': 20260709, 'lifecycle_ticks': 4, 'generation': 'constrained', 'selection': 'baseline', 'slip_admission': 'none', 'collect_refusals': False, 'collect_elite_grids': False}, 'sha256': '2aec10ebf3e6bca57dc3940b33a28d41074ea2358328c13d6df885c84ca9c476'}, {'options': {'population': 8, 'target_evaluations': 24, 'rng_seed': 20260709, 'lifecycle_ticks': 4, 'generation': 'constrained', 'selection': 'novelty_first', 'slip_admission': 'insertion', 'collect_refusals': True, 'collect_elite_grids': True}, 'sha256': 'dd4821f666671a9577aadec2fd333fbe1666738d60a70088bd1c13c8d4ced546'}, {'population': True, 'sha256': 'ba887c3b0bedf82b220c6e0ee58219ccc54e0d94a5d2124f0c9e251625c7ba64'}]

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()

class OperativeEvolutionArmTests(unittest.TestCase):
    def test_exact_prechange_full_returns_and_explicit_legacy(self):
        for row in PINS[:-1]:
            options=row['options']; actual=run_evaluation_loop(**options)
            self.assertEqual(row['sha256'],digest(actual))
            self.assertEqual(actual,run_evaluation_loop(**options,mutation_arm='legacy'))
            self.assertNotIn('mutation_arm',actual)
            self.assertNotIn('operator_observation',actual)
        seeds=build_seed_grids_16(); model=train_generation_model(seeds)
        options=dict(population=8,generation_index=1,rng_seed=20260709)
        actual=constrained_population(seeds[:4],model,**options)
        self.assertEqual(PINS[-1]['sha256'],digest(actual))
        self.assertEqual(actual,constrained_population(seeds[:4],model,mutation_arm='legacy',**options))

    def test_named_arm_is_deterministic_and_accounted_before_selection(self):
        options=dict(population=8,target_evaluations=24,rng_seed=20260709,lifecycle_ticks=4,generation='constrained',selection='novelty_first',slip_admission='insertion',collect_refusals=True,collect_elite_grids=True,mutation_arm=ARM)
        actual=run_evaluation_loop(**options)
        self.assertEqual(actual,run_evaluation_loop(**options))
        self.assertEqual(ARM,actual['mutation_arm'])
        observed=actual['operator_observation']
        self.assertEqual('complete',observed['status'])
        self.assertEqual(24,actual['evaluations_total'])
        self.assertEqual(actual['refusal_collection']['generation_attempts_total'],observed['candidate_generation_attempts'])
        self.assertEqual(observed['candidate_generation_attempts'],observed['candidate_returned']+observed['candidate_failures'])
        self.assertEqual(observed['candidate_returned'],observed['net_phenotype_changed']+observed['parent_copies'])
        self.assertEqual(observed['candidate_returned'],observed['inherited_rate_matches'])
        self.assertEqual(observed['candidate_returned'],observed['protected_payload_matches'])
        self.assertEqual(observed['proposal_attempts'],observed['accepted_operations']+observed['rejected_proposals'])
        self.assertEqual(observed['operator_opportunities'],sum(observed['outcome_counts'].values()))
        for key in ('candidate_failures','invalid_outputs','unaligned_outputs','inherited_rate_mismatches','protected_payload_mismatches','unknown_parent_outputs'):
            self.assertEqual(0,observed[key],key)

    def test_population_passes_only_explicit_arm_and_keeps_seed_order(self):
        seeds=build_seed_grids_16(); model=train_generation_model(seeds); parents=seeds[:2]
        original=copy.deepcopy(parents)
        with patch('wfc_population_throughput.generate_candidate',side_effect=lambda parent,*args,**kwargs: {'grid_id':parent['grid_id']}) as fake:
            values,failures=constrained_population(parents,model,population=4,generation_index=3,rng_seed=11,mutation_arm=ARM)
        self.assertFalse(failures); self.assertEqual(4,len(values)); self.assertEqual(original,parents)
        self.assertEqual([parents[i%2]['grid_id'] for i in range(4)],[call.args[0]['grid_id'] for call in fake.call_args_list])
        self.assertEqual([300011+i for i in range(4)],[call.kwargs['rng_seed'] for call in fake.call_args_list])
        self.assertTrue(all(call.kwargs['mutation_arm']==ARM for call in fake.call_args_list))
        with patch('wfc_population_throughput.generate_candidate',return_value={}) as fake:
            constrained_population(parents,model,population=1,generation_index=0,rng_seed=11)
        self.assertNotIn('mutation_arm',fake.call_args.kwargs)

    def test_invalid_and_incompatible_arms_refused_before_work(self):
        for arm in ('unknown',None,True):
            with self.assertRaises(ValueError): run_evaluation_loop(mutation_arm=arm)
        with self.assertRaisesRegex(ValueError,'constrained'):
            run_evaluation_loop(generation='wfc',mutation_arm=ARM)
        with self.assertRaises(ValueError):
            constrained_population([],None,population=0,generation_index=0,rng_seed=1,mutation_arm='unknown')

    def test_observation_cannot_change_archive_trajectory_or_candidate_output(self):
        options=dict(population=8,target_evaluations=24,rng_seed=20260709,lifecycle_ticks=4,
                     generation='constrained',selection='novelty_first',slip_admission='insertion',
                     collect_refusals=True,collect_elite_grids=True,mutation_arm=ARM)
        observed=run_evaluation_loop(**options)
        with patch('evaluation_loop_scale._observe_operative_population'):
            unobserved=run_evaluation_loop(**options)
        observed.pop('operator_observation'); unobserved.pop('operator_observation')
        self.assertEqual(observed,unobserved)

    def test_empty_parent_pool_stops_before_inventing_attempts(self):
        with patch('evaluation_loop_scale.build_population',return_value=([],{'constrained':0,'wfc':0})), patch('evaluation_loop_scale.constrained_population') as generation:
            result=run_evaluation_loop(population=8,target_evaluations=24,lifecycle_ticks=4,
                generation='constrained',selection='novelty_first',slip_admission='insertion',mutation_arm=ARM)
        generation.assert_not_called()
        self.assertEqual([],result['trajectory'])
        observed=result['operator_observation']
        self.assertEqual('incomplete',observed['status']); self.assertEqual('no_parents',observed['stop_reason'])
        self.assertEqual(0,observed['candidate_generation_attempts'])

    def test_failed_generation_stops_incomplete_and_retains_every_refusal(self):
        failures=[{'parent_grid_id':'rejected_parent','error':'injected generation refusal'} for _ in range(24)]
        with patch('evaluation_loop_scale.constrained_population',return_value=([],failures)):
            result=run_evaluation_loop(population=8,target_evaluations=24,rng_seed=20260709,lifecycle_ticks=4,generation='constrained',selection='novelty_first',slip_admission='insertion',collect_refusals=True,mutation_arm=ARM)
        observed=result['operator_observation']
        self.assertEqual('incomplete',observed['status']); self.assertEqual('no_candidates',observed['stop_reason'])
        self.assertEqual(8,result['evaluations_total']); self.assertEqual(1,len(result['trajectory']))
        self.assertEqual(24,observed['candidate_generation_attempts']); self.assertEqual(24,observed['candidate_failures'])
        self.assertEqual(24,len(observed['failure_records'])); self.assertEqual(24,len(result['refusal_collection']['records']))
        self.assertTrue(all(row['error']=='injected generation refusal' for row in observed['failure_records']))

if __name__=='__main__': unittest.main()
