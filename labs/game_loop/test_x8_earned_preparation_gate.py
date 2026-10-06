"""Synthetic instrument controls only; these tests never run qualification eras."""
from __future__ import annotations

import copy
import base64
import json
from pathlib import Path
import tempfile
import unittest

import x8_earned_preparation_gate as gate


def state(seed=20261030, count=1, roles=None):
    return dict(base_seed=seed, era_count=count, status='active', population_policy=gate.POLICY,
                era_config=gate.CONFIG, campaign_id='synthetic', inherited_unlocks=[], unlocks=[],
                slip_profile={'grid': {'allowed_organ_roles': roles or list(gate.STARTER_ROLES)}})


def observation(generation, index, removed, identity='same', dropout=.2):
    return dict(generation_index=generation, candidate_index=index, run_seed=100+index,
                candidate_grid={'grid_id': identity, 'cells': []}, effective_dropout_rate=dropout,
                cycles=[dict(cycle=1, damage_seed=1000+index, removed_cell_count=removed)])


def completed_receipt(path):
    base=dict(format=gate.FORMAT,stage='reproduce',index=0,home='synthetic',source_manifest_sha256='a'*64,inputs_sha256='b'*64)
    for name,value in [('start.json',base),('result.json',{}),('evaluations.json',[])]:gate.write(path/name,value)
    record={**base,'status':'completed','checks':{name:True for name in gate.required_checks('reproduce')},
            'outputs':{name:gate.file_digest(path/name) for name in ('start.json','result.json','evaluations.json')}}
    gate.write(path/'terminal.json',record)
    return record


class EarnedPreparationInstrumentTests(unittest.TestCase):
    def test_fixed_stage_limits_and_seed_identity(self):
        self.assertEqual(gate.stage_spec('role-era', 2), dict(seed=20261030, index=2, era=True, seconds=120))
        self.assertEqual(gate.stage_spec('density-on', 1)['seed'], 20261031)
        for stage, index in [('role-era', 3), ('density-earn', 1), ('density-off', 0), ('food', 0)]:
            with self.subTest(stage=stage, index=index), self.assertRaises(ValueError):
                gate.stage_spec(stage, index)

    def test_new_role_era_needs_fresh_home(self):
        gate.validate_transition('role-era', 0, {'state': None, 'files': {}}, None)
        with self.assertRaises(ValueError):
            gate.validate_transition('role-era', 0, {'state': state(), 'files': {}}, None)

    def test_continuation_requires_exact_completed_predecessor(self):
        before = dict(state=state(), files={'campaign_state.json': 'one'})
        prior = dict(stage='role-era', index=0, status='completed', after=copy.deepcopy(before))
        gate.validate_transition('role-era', 1, before, prior)
        changed = copy.deepcopy(before); changed['files']['campaign_state.json'] = 'two'
        with self.assertRaises(ValueError): gate.validate_transition('role-era', 1, changed, prior)
        for field, value in [('era_count', 2), ('base_seed', 1), ('status', 'extinct')]:
            bad = copy.deepcopy(before); bad['state'][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                gate.validate_transition('role-era', 1, bad, prior)

    def test_density_fork_requires_real_earned_fact_and_earn_predecessor(self):
        before = dict(state=state(20261031), files={'campaign_state.json': 'one'})
        prior = dict(stage='density-earn', index=0, status='completed', after=copy.deepcopy(before))
        with self.assertRaises(ValueError): gate.validate_transition('density-on', 1, before, prior)
        before['state']['unlocks'] = [dict(axis='storm_record', tier=1, threshold=1.1, metric_value=1.170205, earned_era_index=0)]
        prior['after'] = copy.deepcopy(before)
        gate.validate_transition('density-on', 1, before, prior)
        prior['stage'] = 'role-era'
        with self.assertRaises(ValueError): gate.validate_transition('density-on', 1, before, prior)

    def test_role_decision_requires_threshold_and_offers_one_role(self):
        current = state()
        self.assertIsNone(gate.role_decision(current)['spend'])
        current['unlocks'] = [dict(axis='niche_mastery', tier=2, threshold=26, metric_value=30, earned_era_index=0)]
        self.assertEqual(gate.role_decision(current)['spend'], 'ornament')
        current['slip_profile']['grid']['allowed_organ_roles'].append('ornament')
        self.assertEqual(gate.role_decision(current)['spend'], 'effect')
        current['unlocks'][0]['metric_value'] = 25
        self.assertIsNone(gate.role_decision(current)['spend'])

    def test_observer_adapter_preserves_arguments_result_and_capture_copy(self):
        captured=[]; calls=[]; payload={'value': [1]}; result=({'original': True}, {'report': True})
        def original(*args, **kwargs):
            observer=kwargs.pop('evaluation_callback'); calls.append((args, kwargs)); observer(payload); return result
        wrapped=gate.observer_adapter(original, captured)
        scientific={'rng_seed': 3, 'population': 16, 'founder_grids': []}
        self.assertIs(wrapped('seed', **scientific), result)
        self.assertEqual(calls, [(('seed',), scientific)])
        payload['value'].append(2)
        self.assertEqual(captured, [{'value': [1]}])
        with self.assertRaises(ValueError): wrapped('seed', **scientific)

    def test_observer_rejects_existing_callback_instead_of_replacing_it(self):
        with self.assertRaises(ValueError):
            gate.observer_adapter(lambda: None, [])(evaluation_callback=lambda value: None)

    def test_density_judgment_requires_paired_candidate_and_damage_seeds(self):
        off=[observation(0,0,2), observation(0,1,3)]
        on=[observation(0,0,3,dropout=.21), observation(0,1,3,dropout=.21)]
        self.assertEqual(gate.compare_density(off,on)['verdict'], 'QUALIFIED_CONSEQUENCE')
        on[0]['candidate_grid']['grid_id']='different'
        self.assertEqual(gate.compare_density(off,on)['verdict'], 'REFUSE')
        on[0]['candidate_grid']['grid_id']='same'; on[0]['cycles'][0]['damage_seed']=999
        self.assertEqual(gate.compare_density(off,on)['verdict'], 'REFUSE')

    def test_density_judgment_never_counts_later_unmatched_damage(self):
        off=[observation(0,0,2),observation(1,0,2)]
        on=[observation(0,0,2,dropout=.21),observation(1,0,50,identity='diverged',dropout=.21)]
        verdict=gate.compare_density(off,on)
        self.assertEqual(verdict['verdict'],'REFUSE')
        self.assertEqual(verdict['comparable_first_cycle_difference'],0)
        self.assertFalse(verdict['generations'][1]['comparable'])

    def test_density_judgment_rejects_duplicate_occurrences(self):
        rows=[observation(0,0,2),observation(0,0,2)]
        with self.assertRaises(ValueError): gate.compare_density(rows,rows)

    def test_receipt_requires_complete_check_and_exact_output_closure(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);record=completed_receipt(p)
            self.assertEqual(gate.verified_receipt(p),record)
            (p/'result.json').write_text('{"changed":true}')
            with self.assertRaises(ValueError): gate.verified_receipt(p)

    def test_receipt_rejects_dropped_outputs_unknown_checks_and_start_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);record=completed_receipt(p)
            bad=copy.deepcopy(record);del bad['outputs']['evaluations.json']
            (p/'terminal.json').write_text(json.dumps(bad))
            with self.assertRaises(ValueError):gate.verified_receipt(p)
            bad=copy.deepcopy(record);bad['checks']={'invented':True}
            (p/'terminal.json').write_text(json.dumps(bad))
            with self.assertRaises(ValueError):gate.verified_receipt(p)
            bad=copy.deepcopy(record);bad['inputs_sha256']='c'*64
            (p/'terminal.json').write_text(json.dumps(bad))
            with self.assertRaises(ValueError):gate.verified_receipt(p)
            record['outputs']={}; (p/'terminal.json').write_text(json.dumps(record))
            with self.assertRaises(ValueError): gate.verified_receipt(p)

    def test_receipt_rejects_traversal_failed_empty_checks(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)
            for record in [dict(status='error',checks={'a':True},outputs={'x':'a'}),dict(status='completed',checks={},outputs={'x':'a'}),dict(status='completed',checks={'a':True},outputs={'../foreign':'a'})]:
                (p/'terminal.json').write_text(json.dumps({'format':gate.FORMAT,**record}))
                with self.subTest(record=record),self.assertRaises(ValueError):gate.verified_receipt(p)

    def test_exclusive_output_writer_preserves_original(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'evidence.json';gate.write(p,{'original':True});raw=p.read_bytes()
            with self.assertRaises(FileExistsError):gate.write(p,{'original':False})
            self.assertEqual(p.read_bytes(),raw)

    def test_training_provenance_binds_ordered_first40_raw_sources(self):
        grids=[{'grid_id':str(i)} for i in range(50)]
        inputs=dict(seed_grids=grids,input_sources=[dict(role='seed_corpus',source_position=i,
            data_base64=base64.b64encode(gate.encoded(grid)).decode()) for i,grid in enumerate(grids)])
        training=gate.expected_training(inputs)
        self.assertEqual(training['training_grids'],grids[:40])
        self.assertEqual(training['trainer_options']['rng_seed'],20260707)
        self.assertEqual(training['ordered_training_sha256'],gate.digest(gate.encoded(grids[:40])))
        inputs['input_sources'][0],inputs['input_sources'][1]=inputs['input_sources'][1],inputs['input_sources'][0]
        with self.assertRaises(ValueError):gate.expected_training(inputs)

    def test_release_inbox_keeps_consumed_bytes_and_refuses_foreign_files(self):
        inputs=dict(seed_grids=[{'grid_id':'snail'},{'grid_id':'wisp'}],role_exemplars={'ornament':'snail','effect':'wisp'})
        with tempfile.TemporaryDirectory() as temp:
            home=Path(temp)
            gate.prepare_release(home,inputs,'ornament');raw=(home/'released/snail.json').read_bytes()
            gate.prepare_release(home,inputs,'effect')
            self.assertEqual((home/'released/consumed/snail.json').read_bytes(),raw)
            self.assertEqual([p.name for p in (home/'released').glob('*.json')],['wisp.json'])
            gate.write(home/'released/foreign.json',{'foreign':True})
            with self.assertRaises(ValueError):gate.prepare_release(home,inputs,'ornament')
            self.assertTrue((home/'released/foreign.json').exists())


if __name__ == '__main__': unittest.main()
