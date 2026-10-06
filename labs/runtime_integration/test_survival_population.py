"""X8 operational contracts, synthetic endpoints are not cohort evidence."""
from copy import deepcopy
import importlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"packages/mecha_engine/src"))
import survival_population as population
import survival_live as live
from mecha_engine.generation import train_generation_model

ROOT=Path(__file__).resolve().parents[2]
POLICY='generation_survivors_v1'

class PopulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid=json.loads((ROOT/'data/seed_grids/mg_seed_001.json').read_text())
        cls.slip=json.loads((ROOT/'data/slips/valid/slip_lcd_seed.json').read_text())
        cls.model=train_generation_model([cls.grid])

    def run_population(self, **options):
        args=dict(readability_scorer=lambda grid:.5, generations=2,population=2,
                  damage_cycles=0,ticks=2,population_policy=POLICY,founder_start_mode='bootstrap')
        args.update(options)
        return population.evolve([self.grid],self.slip,self.model,{},**args)

    def test_empty_continuation_never_refills(self):
        with patch.object(population,'generate_candidate',side_effect=AssertionError('refill')):
            archive,report=self.run_population(founder_start_mode='continue',founder_grids=[])
        living=report['living_population']
        self.assertEqual(living['final_breeders'],[])
        self.assertEqual(living['termination'],dict(ended=True,reason='empty_continuation',
            generation_index=None,lifecycle_deaths=0,structural_disqualifications=0,genuine_lifecycle_extinction=False))
        self.assertEqual(report['summary']['creature_count'],0)
        self.assertIsNone(report['summary']['candidate_valid_rate'])
        self.assertIsNone(report['summary']['mean_position_restoration'])
        self.assertEqual(living['unexecuted_candidate_slots'],4)
        self.assertEqual(archive['elites'],{})

    def test_explicit_start_and_density_guard(self):
        for args in [dict(founder_start_mode=None),dict(founder_start_mode='continue',founder_grids=None),
                     dict(population_policy='legacy_archive',founder_start_mode='continue'),
                     dict(cubff_density_pressure=True),dict(cubff_density_pressure=1),
                     dict(survival_regime='tiny')]:
            with self.subTest(args=args),self.assertRaises(ValueError):self.run_population(**args)

    def test_all_rejected_continuation_is_admission_not_death(self):
        bad=deepcopy(self.grid);bad['cells']=[]
        _,report=self.run_population(founder_start_mode='continue',founder_grids=[bad])
        ending=report['living_population']['termination']
        self.assertEqual(ending['reason'],'all_founders_rejected')
        self.assertFalse(ending['genuine_lifecycle_extinction'])
        self.assertEqual(len(report['founders']['rejected']),1)

    def test_zero_cycles_real_final_episode_and_niche_loser_breeds(self):
        # Reusing the identical candidate forces an archive incumbent tie.
        with patch.object(population,'generate_candidate',return_value=deepcopy(self.grid)):
            archive,report=self.run_population()
        living=report['living_population'];self.assertFalse(living['termination']['ended'])
        self.assertEqual(len(living['final_breeders']),2)
        self.assertTrue(any(c['archive_decision']=='kept_incumbent' for g in report['generations'] for c in g['creatures']))
        self.assertEqual(report['generations'][1]['parent_pool_size'],2)
        for g in report['generations']:
            for c in g['creatures']:
                b=c['breeding'];self.assertTrue(b['eligible']);self.assertTrue(b['final_episode']['alive'])
                self.assertEqual((b['cycles_requested'],b['cycles_attempted'],b['cycles_qualified']),(0,0,0))
        self.assertEqual(living['final_breeders'][0]['learned_readability'],None)
        self.assertIsNone(report['summary']['mean_token_restoration'])

    def test_final_tick_death_archived_but_not_a_breeder(self):
        actual=population.run_episode
        def death(*args,**kwargs):
            e=actual(*args,**kwargs);e['alive']=False;e['death_cause']='STARVATION';return e
        with patch.object(population,'run_episode',side_effect=death):archive,report=self.run_population()
        living=report['living_population'];self.assertTrue(archive['elites'])
        self.assertEqual(living['final_breeders'],[]);self.assertEqual(living['evaluated_candidates'],2)
        self.assertEqual(living['termination']['generation_index'],0)
        self.assertTrue(living['termination']['genuine_lifecycle_extinction'])
        for c in report['generations'][0]['creatures']:
            self.assertEqual(c['breeding']['stop'],dict(stage='final_episode',cycle_index=None,reason='lifecycle_death'))
            self.assertEqual(c['breeding']['final_episode']['survival_ticks'],2)
            self.assertIsNotNone(c['score'])

    def test_final_requested_generation_empty_still_ends(self):
        actual=population.run_episode
        def after_first(*args,**kwargs):
            e=actual(*args,**kwargs)
            if kwargs['rng_seed']>=20360512:e['alive']=False;e['death_cause']='STARVATION'
            return e
        with patch.object(population,'run_episode',side_effect=after_first):archive,report=self.run_population()
        self.assertEqual(report['summary']['generation_count'],2)
        self.assertTrue(report['living_population']['termination']['ended'])
        self.assertEqual(report['living_population']['termination']['lifecycle_deaths'],2)
        self.assertTrue(archive['elites'])

    def test_observer_is_actual_and_isolated(self):
        baseline=self.run_population();observed=[]
        def callback(row):observed.append(deepcopy(row));row['candidate_grid']['cells'].clear();row['final_episode'].clear()
        self.assertEqual(self.run_population(evaluation_callback=callback),baseline)
        self.assertEqual(len(observed),4)
        self.assertTrue(all(row['final_episode']['alive'] for row in observed))
        self.assertEqual(observed[0]['candidate_index'],0)

    def test_continue_does_not_need_aligned_seed_pool(self):
        bad=deepcopy(self.grid);bad['cells']=[]
        with patch.object(population,'is_grid_aligned',side_effect=lambda grid,slip:
                          type('V',(),{'ok':bool(grid['cells']),'errors':[] if grid['cells'] else ['empty']})()):
            archive,report=population.evolve([bad],self.slip,self.model,{},readability_scorer=lambda g:.5,
                generations=1,population=1,damage_cycles=0,ticks=2,founder_grids=[self.grid],
                population_policy=POLICY,founder_start_mode='continue')
        self.assertEqual(report['seed_pool_size'],0)
        self.assertEqual(report['living_population']['initial_parent_occurrences'][0]['kind'],'submitted_founder')

    def test_live_stops_after_terminal_death(self):
        actual=live.run_episode
        def death(*args,**kwargs):
            e=actual(*args,**kwargs);e['alive']=False;e['death_cause']='STARVATION';return e
        def repair(grid,*args,**kwargs):
            result=deepcopy(self.grid);result['metadata']['validity_guard_substitutions']=0;return result
        with patch.object(live,'repair_wound_sites',side_effect=repair),patch.object(live,'run_episode',side_effect=death) as run:
            result=live.live_cycle(self.grid,self.slip,{},damage_cycles=3,ticks=2,dropout_rate=0,
                population_policy=POLICY)
        self.assertEqual(run.call_count,1);self.assertEqual(len(result['cycles']),1)
        self.assertEqual(result['stop'],dict(stage='cycle_episode',cycle_index=1,reason='lifecycle_death'))
        self.assertEqual(result['cycles_qualified'],0)

    def test_legacy_exact_off_and_observer_parity(self):
        from mecha_engine.runtime import evolve as old_evolve
        from mecha_engine.repair import train_repair_model
        repair=train_repair_model([self.grid],epochs=2,rng_seed=1)
        args=dict(readability_scorer=lambda grid:.5,generations=2,population=2,
                  damage_cycles=1,ticks=2,dropout_rate=0,rng_seed=1122)
        baseline=old_evolve([self.grid],self.slip,self.model,repair,**args)
        observed=[]
        actual=population.evolve([self.grid],self.slip,self.model,repair,
            population_policy='legacy_archive',founder_start_mode='bootstrap',
            survival_regime='sheltered',cubff_density_pressure=False,
            evaluation_callback=lambda row:observed.append(row),**args)
        self.assertEqual(actual,baseline)
        self.assertEqual(len(observed),4)
        self.assertTrue(all(row['final_episode']['alive'] for row in observed))
        self.assertNotIn('living_population',actual[1])

    def test_invalid_repair_stops_without_fresh_episode(self):
        def repair(grid,*args,**kwargs):
            result=deepcopy(self.grid);result['cells']=[]
            result['metadata']['validity_guard_substitutions']=0;return result
        with patch.object(live,'repair_wound_sites',side_effect=repair),patch.object(live,'run_episode') as run:
            result=live.live_cycle(self.grid,self.slip,{},damage_cycles=3,ticks=2,dropout_rate=0,
                population_policy=POLICY)
        run.assert_not_called();self.assertEqual(len(result['cycles']),1)
        self.assertEqual(result['stop']['stage'],'repair')
        self.assertEqual(result['stop']['reason'],'invalid_repair')
        self.assertEqual(result['final_grid'],self.grid)

    def test_early_cycle_death_has_no_final_scoring_life(self):
        actual=live.run_episode
        def death(*args,**kwargs):
            e=actual(*args,**kwargs);e['alive']=False;e['death_cause']='STARVATION';return e
        def repair(grid,*args,**kwargs):
            result=deepcopy(self.grid);result['metadata']['validity_guard_substitutions']=0;return result
        with patch.object(live,'repair_wound_sites',side_effect=repair),patch.object(live,'run_episode',side_effect=death),\
             patch.object(population,'run_episode') as final:
            archive,report=self.run_population(damage_cycles=3)
        final.assert_not_called();self.assertEqual(archive['elites'],{})
        for c in report['generations'][0]['creatures']:
            self.assertEqual(c['archive_decision'],'skipped_dead')
            self.assertIsNone(c['breeding']['final_episode'])
            self.assertEqual(c['breeding']['cycles_attempted'],1)

    def test_duplicate_id_origins_survive_occurrence_parentage(self):
        from test_observed_care_selection import context
        contexts=[context(1),context(1)];contexts[1]['life_id']='keeper-test:life-2'
        # Distinct occurrences deliberately share a genome ID and genome bytes.
        archive,report=self.run_population(founder_grids=[self.grid,self.grid],founder_care_contexts=contexts)
        breeders=report['living_population']['final_breeders']
        self.assertEqual([b['care_context_origin']['founder_submission_index'] for b in breeders],[0,1])
        self.assertEqual([b['care_context']['life_id'] for b in breeders],[c['life_id'] for c in contexts])
        refs=[c['breeding']['parent_occurrence'] for c in report['generations'][1]['creatures']]
        self.assertEqual([r['candidate_index'] for r in refs],[0,1])
        self.assertTrue(all(r['kind']=='generation_breeder' for r in refs))

    def test_endpoint_and_ordering_contract(self):
        for episode in [None,dict(alive=True,death_cause=None,survival_ticks=1),
                        dict(alive=False,death_cause='STARVATION',survival_ticks=2),
                        dict(alive=True,death_cause='STARVATION',survival_ticks=2)]:
            self.assertFalse(live.endpoint_qualified(episode,2))
        rows=[dict(generation_index=0,candidate_index=i,fitness=f,learned_readability=l)
              for i,f,l in [(0,.9,.1),(1,.2,.9),(2,.9,.1)]]
        self.assertEqual([b['candidate_index'] for b in population._ordered_breeders(rows,'fitness_weighted',None,0)],[0,2,1])
        self.assertEqual([b['candidate_index'] for b in population._ordered_breeders(rows,None,{},1)],[1,0,2])

    def test_empty_weather_records_no_executed_generation(self):
        snapshot={"snapshot_id":"unused"}
        with patch.object(population,'_cubff_generation_pressure',side_effect=AssertionError('unused weather')):
            _,report=self.run_population(founder_start_mode='continue',founder_grids=[],cubff_pressure_source=[snapshot])
        self.assertEqual(report['cubff_pressure']['by_generation'],[])
        self.assertEqual(report['generations'],[])

    def test_lab_package_mirror_and_small_operational_parity(self):
        from mecha_engine.runtime import evolve
        self.assertEqual((ROOT/'labs/runtime_integration/survival_live.py').read_bytes(),
                         (ROOT/'packages/mecha_engine/src/mecha_engine/runtime/_survival_live.py').read_bytes())
        self.assertEqual((ROOT/'labs/runtime_integration/survival_population.py').read_text(encoding='utf-8').replace(
            'from survival_live import','from ._survival_live import'),
            (ROOT/'packages/mecha_engine/src/mecha_engine/runtime/_survival_population.py').read_text(encoding='utf-8'))
        observed=[];reference=self.run_population(evaluation_callback=observed.append)
        package_observed=[]
        actual=evolve([self.grid],self.slip,self.model,{},readability_scorer=lambda grid:.5,
            generations=2,population=2,damage_cycles=0,ticks=2,population_policy=POLICY,
            founder_start_mode='bootstrap',evaluation_callback=package_observed.append)
        self.assertEqual(reference,actual);self.assertEqual(observed,package_observed)

    def test_legacy_observer_uses_retained_algorithm(self):
        from mecha_engine.runtime import evolve
        from mecha_engine.runtime import _survival_population
        from mecha_engine.repair import train_repair_model
        repair=train_repair_model([self.grid],epochs=2,rng_seed=1)
        args=dict(readability_scorer=lambda grid:.5,generations=1,population=1,
                  damage_cycles=1,ticks=2,dropout_rate=0)
        baseline=evolve([self.grid],self.slip,self.model,repair,**args)
        observed=[]
        def observer(row):
            observed.append(deepcopy(row));row['candidate_grid']['cells'].clear();row['final_episode'].clear()
        with patch.object(_survival_population,'evolve',side_effect=AssertionError('helper cannot be the legacy control')):
            actual=evolve([self.grid],self.slip,self.model,repair,**args,founder_start_mode='bootstrap',evaluation_callback=observer)
        self.assertEqual(actual,baseline);self.assertEqual(len(observed),1)
        import survival_population_gate as gate
        self.assertTrue(gate.observations_bound(dict(archive=actual[0],report=actual[1],evaluations=observed)))

    def test_gate_rejects_a_fresh_life_after_a_dead_cycle(self):
        from mecha_engine.repair import train_repair_model
        import survival_population_gate as gate
        repair=train_repair_model([self.grid],epochs=2,rng_seed=1);observed=[]
        population.evolve([self.grid],self.slip,self.model,repair,readability_scorer=lambda grid:.5,
            generations=1,population=1,damage_cycles=2,ticks=2,dropout_rate=0,
            population_policy=POLICY,founder_start_mode='bootstrap',evaluation_callback=observed.append)
        row=observed[0]
        gate.validate_survivor_sequence(row,self.slip,2,2)
        changed=deepcopy(row);changed['cycles'][0]['episode'].update(alive=False,death_cause='STARVATION')
        with self.assertRaisesRegex(ValueError,'after a terminal stop'):
            gate.validate_survivor_sequence(changed,self.slip,2,2)
        changed['cycles']=changed['cycles'][:1]
        changed['final_grid']=changed['cycles'][0]['frames']['repaired_grid']
        with self.assertRaisesRegex(ValueError,'fresh final life'):
            gate.validate_survivor_sequence(changed,self.slip,2,2)

if __name__=='__main__':unittest.main()
