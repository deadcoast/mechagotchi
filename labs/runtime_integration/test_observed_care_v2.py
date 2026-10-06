"""Terminal-survival v2 contracts; v1 remains a byte-exact historical control."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import observed_care_selection as care
from mecha_engine.generation import GenerationModel, generate_candidate, train_generation_model
from test_observed_care_selection import context

ROOT = Path(__file__).resolve().parents[2]
V2 = 'observed_care_selection_v2'

class TerminalCareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid = json.loads((ROOT/'data/seed_grids/mg_seed_001.json').read_text())
        cls.slip = json.loads((ROOT/'data/slips/valid/slip_lcd_seed.json').read_text())
        cls.model = train_generation_model([cls.grid])

    def test_public_version_and_mirror(self):
        from mecha_engine.runtime.care import CARE_POLICY_V2
        self.assertEqual(CARE_POLICY_V2, V2)
        self.assertEqual((ROOT/'labs/runtime_integration/observed_care_selection.py').read_bytes(),
                        (ROOT/'packages/mecha_engine/src/mecha_engine/runtime/_observed_care.py').read_bytes())

    def test_disabled_absent_empty_exact(self):
        baseline = generate_candidate(self.grid,self.model,self.slip,rng_seed=333)
        for policy,ctx in [('off',context()), (V2,None), (V2,context(0))]:
            selected,receipt=care.select_care_successor(self.grid,self.model,self.slip,
                context=ctx,rng_seed=333,policy=policy)
            self.assertEqual(selected,baseline)
            self.assertIsNone(receipt)

    def test_terminal_alive_dominates_and_all_dead_preserves_welfare_order(self):
        episode = dict(need_balance=.9,survival_ticks=12,alive=False,death_cause='starvation',
                       terminal_survival=False,trajectory=[],history=[],initial_state={},final_state={})
        scores=[deepcopy(episode) for _ in range(8)]
        scores[5].update(need_balance=.1,alive=True,death_cause=None,terminal_survival=True)
        with patch.object(care,'observed_care_episode',side_effect=scores):
            _,receipt=care.select_care_successor(self.grid,self.model,self.slip,
                context=context(),rng_seed=333,policy=V2)
        self.assertEqual(receipt['selected_index'],5)
        self.assertEqual(receipt['selection_order'],['terminal_survival','need_balance','survival_ticks','earliest_index'])
        scores[5].update(need_balance=.95,alive=False,death_cause='starvation',terminal_survival=False)
        with patch.object(care,'observed_care_episode',side_effect=scores):
            _,receipt=care.select_care_successor(self.grid,self.model,self.slip,
                context=context(),rng_seed=333,policy=V2)
        self.assertEqual(receipt['selected_index'],5)

    def test_retained_pair22_exact_v1_and_terminal_correction(self):
        manifest=json.loads((ROOT/'data/game_client/observed_care_inputs_stage0.json').read_text())
        historical=json.loads((ROOT/'data/game_client/observed_care_selection_stage0.json').read_text())['rows'][22]
        founder=manifest['founders'][2]
        args=(founder['grid'],GenerationModel(**founder['model']),manifest['covenant'])
        before=deepcopy(args[0:1]+(args[2],founder['contexts']))
        for evaluator in care.CARE_EVALUATORS:
            for name,ctx in founder['contexts'].items():
                selected,receipt=care.select_care_successor(*args,context=ctx,rng_seed=20260702,
                    policy=care.CARE_POLICY,evaluator=evaluator)
                previous=historical['evaluators'][evaluator]['trials'][name]
                self.assertEqual((selected,receipt),(previous['selected_grid'],previous['receipt']))
        selected,receipt=care.select_care_successor(*args,context=founder['contexts']['neglect'],
            rng_seed=20260702,policy=V2,evaluator='archive_morphology_probe_v1')
        self.assertEqual(receipt['selected_index'],0)
        rows=receipt['candidates'];chosen=rows[0]
        self.assertTrue(chosen['terminal_survival'])
        self.assertEqual(chosen['survival_ticks'],10)
        self.assertFalse(rows[4]['terminal_survival'])
        self.assertEqual(rows[4]['survival_ticks'],10)
        self.assertEqual(receipt['source_identity'],{key:founder['contexts']['neglect'][key]
            for key in ('keeper_id','life_id','grid_id','grid_sha256')})
        self.assertTrue(all(cell['stress']==0 and cell['damage']==0 for cell in selected['cells']))
        for row in rows:
            episode=row['episode'];trace=episode['trajectory']
            self.assertEqual(len(trace),row['survival_ticks'])
            self.assertEqual(episode['initial_state']['age_ticks'],0)
            self.assertNotIn('qtable_policy',episode['initial_state'].get('thread_states',{}))
            self.assertEqual(trace[-1]['result']['alive'],row['alive'])
            self.assertEqual(trace[-1]['result']['death_cause'],row['death_cause'])
            self.assertEqual(episode['history'],[tick['result'] for tick in trace])
            self.assertEqual(row['need_balance'],round(sum(t['result']['balance'] for t in trace)/10,6))
            self.assertTrue(all(t['applied_action']!='feed' or t['source_actor']=='keeper' for t in trace))
        self.assertEqual(before,args[0:1]+(args[2],founder['contexts']))

    def test_newborn_state_and_metadata_control(self):
        from observed_care_gate import altered_metadata
        ctx=context();renamed=altered_metadata(ctx)
        args=(self.grid,self.model,self.slip)
        a,ra=care.select_care_successor(*args,context=ctx,rng_seed=333,policy=V2)
        b,rb=care.select_care_successor(*args,context=renamed,rng_seed=333,policy=V2)
        self.assertEqual((a,ra['candidates']),(b,rb['candidates']))
        self.assertNotEqual(ra['context_sha256'],rb['context_sha256'])
        self.assertNotEqual(ra['source_identity'],rb['source_identity'])

if __name__=='__main__':unittest.main()
