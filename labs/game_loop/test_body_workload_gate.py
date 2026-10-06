"""Synthetic instrument checks; never executes the held-out outcomes."""
from copy import deepcopy
from contextlib import ExitStack
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

import body_workload_gate as gate


def passing_pair(index):
    spec = gate.care_plan()[index]
    return {**spec, 'checks': {key: True for key in gate.PAIR_CHECKS},
        'evaluators': {name: {'checks': {key: True for key in gate.CARE_CHECKS},
            'selected_structures_differ': index == 0,
            'complete_rankings_differ': index == 0}
            for name in gate.EVALUATORS}}


class RetainedProductIdentityTests(unittest.TestCase):
    """Reads retained inputs only; never collects histories or evaluates candidates."""
    def setUp(self):
        self.artifact = gate.read(gate.ROOT/'data/game_client/product_learning_gate_stage1.json')
        self.original = gate.read(gate.ROOT/'.development/x7/learning/manifest.json')

    def test_retained_stage1_identity_validates_without_simulation(self):
        before = gate.digest([self.artifact, self.original])
        self.assertEqual(gate.digest(self.artifact['input_manifest']),
            '4657512d4b271bbd386d786cb5fc210f475038e66b6b011ec36184e9345523ce')
        self.assertEqual(gate.digest(self.original),
            '05d3512573e8066536181c731ce20839748980732f2e46cb0b957c464d495737')
        with patch.object(gate, 'imports', side_effect=AssertionError('simulation import forbidden')):
            self.assertIs(gate.validate_product_manifest(self.artifact, self.original),
                          self.artifact['input_manifest'])
        self.assertEqual(gate.digest([self.artifact, self.original]), before)

    def test_original_manifest_cannot_substitute_for_repaired_stage1(self):
        self.artifact['input_manifest'] = self.original
        with self.assertRaisesRegex(ValueError, 'stage1'):
            gate.validate_product_manifest(self.artifact, self.original)

    def test_declared_current_hash_must_match_known_stage1(self):
        self.artifact['input_manifest_sha256'] = gate.digest(self.original)
        with self.assertRaisesRegex(ValueError, 'declared'):
            gate.validate_product_manifest(self.artifact, self.original)

    def test_original_manifest_tamper_refuses(self):
        self.original['hatch_seed'] += 1
        with self.assertRaisesRegex(ValueError, 'original'):
            gate.validate_product_manifest(self.artifact, self.original)

    def test_stage1_scientific_core_tamper_refuses(self):
        for field in ('founders', 'covenant', 'admissions', 'source_corpus', 'hatch_seed', 'plan', 'budgets'):
            with self.subTest(field=field):
                artifact = deepcopy(self.artifact)
                artifact['input_manifest'][field] = {'tampered': True}
                with self.assertRaisesRegex(ValueError, 'stage1'):
                    gate.validate_product_manifest(artifact, self.original)

    def test_prior_binding_is_independently_required(self):
        self.artifact['input_manifest']['instrument_repair']['prior_manifest_sha256'] = '0'*64
        changed_hash = gate.digest(self.artifact['input_manifest'])
        self.artifact['input_manifest_sha256'] = changed_hash
        with patch.object(gate, 'PRODUCT_PAYLOAD_SHA256', changed_hash), \
                self.assertRaisesRegex(ValueError, 'prior'):
            gate.validate_product_manifest(self.artifact, self.original)

    def test_core_identity_is_independently_required(self):
        for field in ('founders', 'covenant', 'admissions', 'source_corpus', 'hatch_seed', 'plan', 'budgets'):
            with self.subTest(field=field):
                artifact = deepcopy(self.artifact)
                artifact['input_manifest'][field] = {'tampered': True}
                changed_hash = gate.digest(artifact['input_manifest'])
                artifact['input_manifest_sha256'] = changed_hash
                with patch.object(gate, 'PRODUCT_PAYLOAD_SHA256', changed_hash), \
                        self.assertRaisesRegex(ValueError, 'scientific core'):
                    gate.validate_product_manifest(artifact, self.original)

    def test_source_closure_requires_original_and_repair_contract(self):
        self.assertIn('.development/x7/learning/manifest.json', gate.FROZEN_PATHS)
        self.assertIn('docs/development/cycle-38-body-workload-instrument-repair.md', gate.FROZEN_PATHS)


class BodyWorkloadGateTests(unittest.TestCase):
    def synthetic_inputs(self):
        product = dict(covenant={'synthetic':True}, founders=[dict(grid={'grid_id':f'grid-{i}'}, model={}) for i in range(50)])
        founders = []
        for index in range(20,30):
            grid = product['founders'][index]['grid']
            ctx = dict(format='keeper_care_context_v1', keeper_id='keeper', life_id='keeper:life-1',
                grid_id=grid['grid_id'], grid_sha256=gate.digest(grid), body_response='workload-v1',
                care_summary=dict(history='complete', from_age_ticks=0, ticks_observed=1,
                    keeper_actions={'play':1}, companion_actions={}, beg_requests=0),
                events=[dict(tick=1,session_tick=1,actor='keeper',action='play',begging=False,alive=True,death_cause=None)],
                events_omitted=0,last_age_ticks=1,last_session_tick=1,outcome='alive')
            histories = {name:deepcopy(ctx) for name in ('fed','neglect')}
            founders.append(dict(founder_index=index,grid=grid,model={},used_prefix_ticks=1,
                original_histories=histories,contexts=deepcopy(histories)))
        return dict(format=gate.INPUT_FORMAT,body_response='workload-v1',care_plan=gate.care_plan(),
            production_plan=gate.production_plan(),production_config=gate.CONFIG,
            product_manifest=product,founders=founders,pools=[[{}]*8 for _ in range(30)],
            source_inputs={name:'c'*64 for name in gate.FROZEN_PATHS},production={},causal_fixture={},covenant=product['covenant'])

    def validate_synthetic(self, inputs):
        with ExitStack() as stack:
            stack.enter_context(patch.object(gate,'validate_product_manifest',return_value=inputs['product_manifest']))
            stack.enter_context(patch.object(gate,'read',return_value={}))
            stack.enter_context(patch.object(gate,'file_digest',return_value='c'*64))
            stack.enter_context(patch.object(gate,'causal_fixture',return_value={}))
            gate.validate_inputs(inputs)

    def test_fixed_plan_contains_only_fresh_preregistered_ids(self):
        pairs = gate.care_plan()
        self.assertEqual(len(pairs), 30)
        self.assertEqual(pairs[0], dict(pair_index=0, founder_index=20, rng_seed=20261107))
        self.assertEqual(pairs[-1], dict(pair_index=29, founder_index=29, rng_seed=20261127))
        self.assertEqual(gate.production_plan(), [dict(era_index=i,
            rng_seed=(20261130, 20261201, 20261202)[i // 2],
            body_response=('legacy', 'workload-v1')[i % 2]) for i in range(6)])

    def test_stage_spec_rejects_bool_unknown_and_extra_trials(self):
        for stage, index in [('care', True), ('care', 30), ('production', 6),
                             ('reproduce', 1), ('setup', 1), ('mystery', 0)]:
            with self.subTest(stage=stage, index=index), self.assertRaises(ValueError):
                gate.stage_spec(stage, index)
        self.assertEqual(gate.stage_spec('care', 0)['seconds'], 30)
        self.assertEqual(gate.stage_spec('setup', 0)['seconds'], 60)
        self.assertEqual(gate.stage_spec('production', 0)['seconds'], 120)

    def test_complete_rank_uses_terminal_before_welfare_elapsed_and_index(self):
        rows = [dict(index=0, terminal_survival=False, need_balance=1., survival_ticks=10),
                dict(index=1, terminal_survival=True, need_balance=.4, survival_ticks=9),
                dict(index=2, terminal_survival=True, need_balance=.4, survival_ticks=10),
                dict(index=3, terminal_survival=True, need_balance=.4, survival_ticks=10)]
        self.assertEqual(gate.complete_ranking({'candidates': rows}), [2, 3, 1, 0])

    def test_judgment_requires_structure_and_ranking_in_same_pair(self):
        rows = [passing_pair(i) for i in range(30)]
        self.assertEqual(gate.judge_care(rows)['pristine']['verdict'], 'QUALIFIED_FIXED_HOLDOUT')
        rows[0]['evaluators']['pristine']['complete_rankings_differ'] = False
        rows[1]['evaluators']['pristine']['complete_rankings_differ'] = True
        result = gate.judge_care(rows)
        self.assertEqual(result['pristine']['verdict'], 'REFUSE')
        self.assertEqual(result[gate.EVALUATORS[1]]['verdict'], 'QUALIFIED_FIXED_HOLDOUT')

    def test_judgment_cannot_pass_incomplete_or_reordered_cohort(self):
        rows = [passing_pair(i) for i in range(30)]
        for bad in (rows[:-1], list(reversed(rows)), rows + [rows[0]]):
            self.assertTrue(all(v['verdict'] == 'REFUSE' for v in gate.judge_care(bad).values()))

    def test_all_original_nonregressions_remain_required(self):
        for name in ('fed_welfare_nonregression', 'fed_survival_nonregression',
                     'neglect_terminal_nonregression'):
            rows = [passing_pair(i) for i in range(30)]
            rows[3]['evaluators']['pristine']['checks'][name] = False
            self.assertEqual(gate.judge_care(rows)['pristine']['verdict'], 'REFUSE')

    def test_missing_or_nonboolean_checks_fail_closed(self):
        for value in (1, 'true', None):
            rows = [passing_pair(i) for i in range(30)]
            rows[2]['checks']['input_immutable'] = value
            self.assertTrue(all(v['verdict'] == 'REFUSE' for v in gate.judge_care(rows).values()))
        rows = [passing_pair(i) for i in range(30)]
        rows[0]['evaluators']['pristine']['checks']['invented'] = True
        self.assertEqual(gate.judge_care(rows)['pristine']['verdict'], 'REFUSE')

    def test_unchanged_synthetic_inputs_validate_without_outcome(self):
        self.validate_synthetic(self.synthetic_inputs())

    def test_changed_covenant_refuses_before_outcome(self):
        inputs=self.synthetic_inputs();inputs['covenant']={'forged':True}
        with self.assertRaisesRegex(ValueError,'covenant'):self.validate_synthetic(inputs)

    def test_changed_history_prefix_refuses_before_outcome(self):
        inputs=self.synthetic_inputs();inputs['founders'][0]['used_prefix_ticks']=2
        with self.assertRaisesRegex(ValueError,'prefix'):self.validate_synthetic(inputs)

    def test_context_cannot_be_bound_to_another_founder(self):
        inputs=self.synthetic_inputs()
        for key in ('original_histories','contexts'):
            inputs['founders'][0][key]['fed']['grid_id']='other-body'
        with self.assertRaisesRegex(ValueError,'another founder'):self.validate_synthetic(inputs)

    def test_scientific_care_refusal_does_not_block_independent_production(self):
        row=passing_pair(0)
        row['evaluators']['pristine']['checks']['fed_welfare_nonregression']=False
        gate.verify_invariants('care',row)
        row['evaluators']['pristine']['checks']['fed_trajectory_consistent']=False
        with self.assertRaisesRegex(ValueError,'integrity'):gate.verify_invariants('care',row)

    def test_missing_original_instrument_check_is_integrity_failure(self):
        row=passing_pair(0);del row['checks']['off_exact']
        with self.assertRaisesRegex(ValueError,'invariant'):gate.verify_invariants('care',row)

    def test_refused_immutable_reproduction_stops_following_work(self):
        with self.assertRaisesRegex(ValueError,'reproduction'):
            gate.verify_invariants('reproduce',{'reproduction_exact':False})

    def make_receipt(self, directory, result=None):
        directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
        start=dict(format=gate.FORMAT,spec=gate.stage_spec('causal'),source_manifest_sha256='a'*64,
                   inputs_sha256='b'*64)
        gate.write(directory/'started.json',start)
        gate.write(directory/'result.json',result or {'checks':{name:True for name in gate.CAUSAL_CHECKS}})
        terminal={**start,'status':'completed','elapsed_seconds':.1,
            'started_sha256':gate.file_digest(directory/'started.json'),
            'outputs':{'result.json':gate.file_digest(directory/'result.json')}}
        gate.write(directory/'terminal.json',terminal)
        return terminal

    def test_verified_receipt_checks_bound_result_and_stage_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            terminal=self.make_receipt(directory)
            self.assertTrue(gate.verify_result(directory,'a'*64,'b'*64)['checks']['native_play_divergence'])
            terminal['outputs']={}
            Path(directory,'terminal.json').write_bytes(gate.encode(terminal))
            with self.assertRaises(ValueError):gate.verify_result(directory,'a'*64,'b'*64)

    def test_forged_receipt_stage_cap_refuses(self):
        with tempfile.TemporaryDirectory() as directory:
            terminal=self.make_receipt(directory)
            terminal['spec']['seconds']=120
            Path(directory,'terminal.json').write_bytes(gate.encode(terminal))
            with self.assertRaisesRegex(ValueError,'specification'):
                gate.verify_result(directory,'a'*64,'b'*64)

    def test_over_budget_receipt_refuses(self):
        with tempfile.TemporaryDirectory() as directory:
            terminal=self.make_receipt(directory);terminal['elapsed_seconds']=30.001
            Path(directory,'terminal.json').write_bytes(gate.encode(terminal))
            with self.assertRaisesRegex(ValueError,'bound'):gate.verify_result(directory,'a'*64,'b'*64)

    def test_prerequisites_bind_causal_native_operational_review_and_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.make_receipt(root/'causal')
            prerequisite=dict(format='body_workload_preconditions_v1',source_manifest_sha256='a'*64,
                inputs_sha256='b'*64,causal=dict(directory='causal',terminal_sha256=gate.file_digest(root/'causal/terminal.json')))
            for key in ('native','operational','independent_review'):
                gate.write(root/(key+'.json'),dict(passed=True,source_manifest_sha256='a'*64,inputs_sha256='b'*64))
                prerequisite[key]=dict(path=key+'.json',sha256=gate.file_digest(root/(key+'.json')))
            gate.write(root/'preconditions.json',prerequisite)
            with patch.object(gate,'ROOT',root):
                gate.prerequisites(root/'preconditions.json',gate.file_digest(root/'preconditions.json'),'a'*64,'b'*64)
                # Even a newly hashed review file cannot certify a different input.
                review=root/'independent_review.json'
                review.write_bytes(gate.encode(dict(passed=True,source_manifest_sha256='a'*64,inputs_sha256='c'*64)))
                prerequisite['independent_review']['sha256']=gate.file_digest(review)
                (root/'preconditions.json').write_bytes(gate.encode(prerequisite))
                with self.assertRaisesRegex(ValueError,'exact frozen inputs'):
                    gate.prerequisites(root/'preconditions.json',gate.file_digest(root/'preconditions.json'),'a'*64,'b'*64)

    def test_no_prerequisite_means_no_outcome(self):
        with self.assertRaisesRegex(ValueError,'required'):
            gate.prerequisites(None,None,'a'*64,'b'*64)

    def test_worker_cannot_complete_after_its_own_stage_cap(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);gate.write(root/'source.json',{});gate.write(root/'inputs.json',{})
            args=SimpleNamespace(stage='causal',index=0,output=root/'out',source_manifest=root/'source.json',
                inputs=root/'inputs.json',inputs_sha256=gate.file_digest(root/'inputs.json'),
                prerequisites=None,prerequisites_sha256=None)
            with patch.object(gate,'source_snapshot',return_value={}), patch.object(gate,'validate_inputs'), \
                    patch.object(gate,'causal_trial',return_value={}), patch.object(gate.time,'perf_counter',side_effect=[0,31,32]):
                with self.assertRaisesRegex(RuntimeError,'stage cap'):gate.execute(args)
            terminal=gate.read(root/'out/terminal.json')
            self.assertEqual(terminal['status'],'error')
            self.assertEqual(terminal['error']['kind'],'TimeoutError')
            self.assertTrue((root/'out/result.json').exists())

    def test_source_manifest_cannot_omit_current_module_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            required=(*gate.FROZEN_PATHS,'labs/game_loop/body_workload_gate.py',
                'labs/game_loop/body_workload_coordinator.py','labs/game_loop/body_workload_fixtures.py',
                'labs/game_loop/body_workload_recording.py')
            for name in required:
                path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('retained')
            omitted=root/'packages/mecha_engine/src/mecha_engine/lifecycle/new.py'
            omitted.parent.mkdir(parents=True);omitted.write_text('must freeze')
            manifest={'format':'x8_source_manifest_v1','files':{name:gate.file_digest(root/name) for name in required}}
            gate.write(root/'source.json',manifest)
            with patch.object(gate,'ROOT',root), self.assertRaisesRegex(ValueError,'omits'):
                gate.source_snapshot(root/'source.json')

    def test_exclusive_evidence_write_preserves_prior_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'result.json'
            gate.write(path, {'first': True})
            original = path.read_bytes()
            with self.assertRaises(FileExistsError): gate.write(path, {})
            self.assertEqual(path.read_bytes(), original)

    def test_fixture_is_authored_not_selected_from_holdout(self):
        fixture = gate.causal_fixture()
        self.assertEqual(fixture['grid']['grid_size'], [8, 8])
        self.assertEqual(len(fixture['grid']['cells']), 6)
        self.assertEqual(fixture['damage_event'], {'removed_cells': [[4, 3]]})
        self.assertEqual(set(fixture['repair_models']), {'changed', 'null'})
        self.assertEqual(fixture['play_actions'], ['play', 'sleep', 'feed'] * 3)
        self.assertNotIn('founder_index', fixture)
        for name, token in [('changed', 'B'), ('null', 'D')]:
            model = fixture['repair_models'][name]
            chosen = model['class_tokens'].index(token)
            self.assertEqual(model['weights'][chosen][-1], 8.)
            self.assertEqual(sum(x != 0 for row in model['weights'] for x in row), 1)

    def test_projection_view_excludes_metadata_only(self):
        row = dict(grid_id='a', body_response='workload-v1', body_workload={},
                   play_energy_cost=.12, hunger=.4, energy=.7, age_ticks=1,
                   alive=True, death_cause=None, action_energy_effect=0)
        self.assertEqual(gate.physiology(row), dict(hunger=.4, energy=.7, age_ticks=1,
                        alive=True, death_cause=None, action_energy_effect=0))

    def test_production_summary_counts_real_deaths_and_terminal_breeders(self):
        row = dict(generation_index=0, cycles=[dict(episode=dict(alive=False, death_cause='stress_collapse'))],
                   final_episode=None)
        report = dict(living_population=dict(final_breeders=[], termination=dict(generation_index=0, reason='no_eligible_breeders', genuine_lifecycle_extinction=True)),
                      generations=[dict(generation=0, creatures=[])])
        result = gate.population_observations(dict(report=report, evaluations=[row]))
        self.assertEqual(result['lifecycle_deaths'], 1)
        self.assertEqual(result['death_causes'], {'stress_collapse': 1})
        self.assertEqual(result['terminal_breeders'], 0)

    def test_zero_breeders_without_terminal_lifecycle_death_never_qualifies(self):
        result = gate.population_observations(dict(report=dict(
            living_population=dict(final_breeders=[], termination=dict(generation_index=0, reason='no_eligible_breeders', genuine_lifecycle_extinction=False)),
            generations=[dict(generation=0, creatures=[])]), evaluations=[]))
        self.assertFalse(result['qualifying_extinction'])


if __name__ == '__main__': unittest.main()
