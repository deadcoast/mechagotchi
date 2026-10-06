"""Instrument tests use synthetic results; they run no qualification simulation."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import survival_population_gate as gate

class InstrumentTests(unittest.TestCase):
    def test_declared_sixty_case_plan_and_order(self):
        plan=gate.case_plan()
        self.assertEqual(len(plan),60)
        self.assertEqual(sum(p['stage']=='parity' for p in plan),16)
        self.assertEqual(sum(p['stage']=='cohort' for p in plan),40)
        self.assertEqual(sum(p['stage']=='duplicate' for p in plan),4)
        self.assertEqual(len({tuple(p.items()) for p in plan}),60)
        self.assertTrue(all(p['backend']=='package' for p in plan[16:56]))

    def test_single_case_receipts_and_verified_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            temp=Path(tmp);manifest=temp/'manifest.json';source={gate.CONTRACT:gate.sha((gate.ROOT/gate.CONTRACT).read_bytes())}
            gate.write(manifest,dict(format='x8_source_manifest_v1',files=source))
            inputs=temp/'inputs.json';gate.write(inputs,dict(source_sha256=source,source_manifest_sha256=gate.sha(manifest.read_bytes())))
            result=dict(archive={},report={},evaluations=[],projection=[],checks=dict(input_immutable=True,observations_bound=True))
            plan=gate.case_plan()[0]
            with patch.object(gate,'run_case',return_value=result) as run:
                receipt=gate.execute('case',temp/'trial',manifest,inputs,plan)
                self.assertEqual(run.call_count,1)
            with patch.object(gate,'validate_result') as validator:
                loaded=gate.load_trial(temp/'trial',gate.sha(inputs.read_bytes()),source,gate.read(inputs))
                validator.assert_called_once()
            self.assertEqual(loaded['receipt'],receipt)
            with self.assertRaises(FileExistsError):gate.execute('case',temp/'trial',manifest,inputs,plan)
            (temp/'trial/result.json').write_text('{}')
            with self.assertRaises(ValueError):gate.load_trial(temp/'trial',gate.sha(inputs.read_bytes()),source,gate.read(inputs))

    def test_input_source_mismatch_refuses_before_simulation_and_retains_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            temp=Path(tmp);manifest=temp/'manifest.json'
            gate.write(manifest,dict(format='x8_source_manifest_v1',files={gate.CONTRACT:'0'*64}))
            with patch.object(gate,'run_case') as run,self.assertRaises(RuntimeError):
                gate.execute('case',temp/'trial',manifest,temp/'absent.json',gate.case_plan()[0])
            run.assert_not_called()
            self.assertEqual(gate.read(temp/'trial/terminal.json')['status'],'error')
            self.assertTrue((temp/'trial/start.json').exists())

    def test_endpoint_tick_count_is_not_alive(self):
        history=[dict(tick=1,balance=.7,alive=True,death_cause=None,state={}),
                 dict(tick=2,balance=.5,alive=False,death_cause='STARVATION',state={})]
        episode=dict(survival_ticks=2,alive=False,death_cause='STARVATION',need_balance=.6)
        self.assertTrue(gate.episode_consistent(episode,history,2))
        changed=deepcopy(history);changed[0]['alive']=False
        self.assertFalse(gate.episode_consistent(episode,changed,2))
        episode['alive']=True
        self.assertFalse(gate.episode_consistent(episode,history,2))

    def test_source_manifest_requires_repository_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'manifest.json'
            gate.write(path,dict(format='x8_source_manifest_v1',files={'../outside.py':'0'*64}))
            with self.assertRaises(ValueError):gate.source_snapshot(path)

    def test_wrong_seed_or_case_refuses_even_with_asserted_checks(self):
        report=dict(rng_seed=20260701,generations_requested=6,population=16,damage_cycles=2,ticks=16,
                    dropout_rate=.2,seed_corpus_size=50)
        with self.assertRaisesRegex(ValueError,'configuration'):
            gate.validate_result(dict(report=report),gate.case_plan()[0],{})
        with self.assertRaisesRegex(ValueError,'unregistered'):
            gate.validate_result({},dict(stage='cohort',backend='lab',arm='A',seed=20260700),{})

    def test_cohort_adoption_does_not_claim_native_qualification(self):
        trials=[]
        for plan in gate.case_plan():
            arm=plan['arm'];seed=plan['seed'];extinct=arm=='D' and seed==gate.SEEDS[0]
            rows=[dict(generation_index=0,candidate_grid={'grid_id':str(i)},
                       final_episode=dict(alive=not(arm=='B' and i==0),death_cause='STARVATION' if arm=='B' and i==0 else None))
                  for i in range(16)]
            report=dict(generations=[dict(creatures=[{}]*16)],summary={'archive':{}})
            if arm in 'CD':report['living_population']=dict(final_breeders=[] if extinct else [{}],
                termination={'genuine_lifecycle_extinction':extinct})
            trials.append(dict(plan=plan,result=dict(report=report,evaluations=rows)))
        result=gate.judge(trials)
        self.assertEqual(result['cohort_verdict'],'ADOPT')
        self.assertEqual(result['product_qualification'],'OPEN')
        self.assertEqual(result['lowest_extinct_seed'],gate.SEEDS[0])
        self.assertFalse(result['default_changed'])
        for row in trials:
            if row['plan']['arm']=='D':row['result']['report']['living_population']['termination']['genuine_lifecycle_extinction']=False
        self.assertEqual(gate.judge(trials)['cohort_verdict'],'REFUSE')
