"""X7 immutable care inputs and occurrence-preserving continuation."""
import copy
import json
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
for folder in ('game/src','packages/mecha_engine/src'):
    sys.path.insert(0,str(ROOT/folder))
from mecha_game import campaign as api
from mecha_game.execution import capture_execution, decode_execution_inputs

class CareExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cold=api.load_campaign_inputs(**api.default_campaign_paths(ROOT),seed_limit=4,with_models=False)
        cls.inputs=api.prepare_campaign_models(cold,repair_epochs=1)
    def effective(self):
        return dict(**copy.deepcopy(self.inputs),founder_grids=[self.inputs['seed_grids'][0]],
            founder_care_contexts=[None],care_selection_policy='off',care_evaluator='pristine',
            cubff_pressure_source=None,rng_seed=123,effective_config=dict(generations=1,population=2,damage_cycles=1,ticks=3,dropout_rate=.2))
    def test_capture_retains_versioned_ordered_care_inputs(self):
        data=self.effective()
        bundle=capture_execution('care-test',0,data,[])
        self.assertIn('care_inputs_sha256',bundle['manifest']['inputs'])
        restored=decode_execution_inputs(json.loads(json.dumps(bundle,sort_keys=True)))
        self.assertEqual([None],restored['founder_care_contexts'])
        self.assertEqual('off',restored['care_selection_policy'])
        self.assertEqual('pristine',restored['care_evaluator'])
    def test_misaligned_context_count_refused_before_execution(self):
        data=self.effective(); data['founder_care_contexts']=[]
        with self.assertRaisesRegex(ValueError,'care|Care|context'):
            capture_execution('care-test',0,data,[])
    def test_unknown_care_policy_refused(self):
        data=self.effective(); data['care_selection_policy']='pretend_personality'
        with self.assertRaisesRegex(ValueError,'care|Care|policy'):
            capture_execution('care-test',0,data,[])
    def test_old_missing_care_inputs_decode_off(self):
        data=self.effective()
        for key in ('founder_care_contexts','care_selection_policy','care_evaluator'): data.pop(key)
        bundle=capture_execution('old',0,data,[])
        self.assertNotIn('care_inputs_sha256',bundle['manifest']['inputs'])
        self.assertEqual('off',decode_execution_inputs(bundle).get('care_selection_policy','off'))
    def session(self):
        from mecha_game.session import CompanionSession
        return CompanionSession(self.inputs['seed_grids'][0],self.inputs['slip_profile'],model=self.inputs['generation_model'])
    def test_direct_source_wrong_body_or_duplicate_ordinal_refused_before_run(self):
        from mecha_game.contribute import companion_release_source
        session=self.session();session.advance('feed')
        source=companion_release_source(session);source['founder_ordinal']=0
        data=self.effective();data['founder_grids']=[copy.deepcopy(session.grid)]
        data['founder_care_contexts']=[copy.deepcopy(source['care_context'])]
        data['founder_grids'][0]['cells'][0]['mutation_weight']=.12345
        with self.assertRaisesRegex(ValueError,'genome'):
            capture_execution('bad',0,data,[source])
        data['founder_grids']=[session.grid]
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            capture_execution('bad',0,data,[source,source])
    def test_real_care_persists_through_era_resume_continuation_and_reproduction(self):
        import sqlite3,tempfile
        from contextlib import closing
        from mecha_game.contribute import companion_release_source
        from mecha_game.era_plan import EraPlan
        from mecha_game.execution import reproduce_era
        session=self.session(); session.advance('feed');session.advance('sleep')
        source=companion_release_source(session)
        campaign=api.KeeperCampaign(copy.deepcopy(self.inputs),campaign_id='care-live',era_config=self.effective()['effective_config'])
        era=campaign.advance_era('calm',released_grids=[session.grid],released_sources=[source],
            care_selection_policy='observed_care_selection_v1',care_evaluator='pristine')
        context=source['care_context']
        self.assertEqual(context,decode_execution_inputs(era['execution'])['founder_care_contexts'][0])
        self.assertTrue(any(c is not None for c in era['report']['care_selection']['elite_contexts']))
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);ledger=folder/'campaign.sqlite3';state=folder/'campaign_state.json'
            plan=EraPlan(folder/'era_plan.json');plan.begin(campaign,era,None);plan.finish(ledger,state)
            loaded=api.KeeperCampaign.load_state(copy.deepcopy(self.inputs),state,ledger)
            carried=[s['care_context'] for s in loaded.resume_founder_sources if 'care_context' in s]
            self.assertTrue(carried);self.assertTrue(all(c==context for c in carried))
            uninterrupted=campaign.advance_era('calm')
            resumed=loaded.advance_era('calm')
            self.assertEqual(uninterrupted['report'],resumed['report'])
            self.assertEqual(uninterrupted['elites'],resumed['elites'])
            before=ledger.read_bytes()
            with closing(sqlite3.connect(ledger.as_uri()+'?mode=ro',uri=True)) as conn:
                result=reproduce_era(conn,'care-live',0)
            self.assertEqual('matched',result['status'],result)
            self.assertEqual(before,ledger.read_bytes())
    def test_equal_grid_ids_keep_distinct_life_occurrences(self):
        from mecha_game.contribute import companion_release_source
        a=self.session();b=self.session();a.advance('feed');b.advance('sleep')
        sources=[companion_release_source(pet) for pet in (a,b)]
        campaign=api.KeeperCampaign(copy.deepcopy(self.inputs),campaign_id='duplicate-care',era_config=self.effective()['effective_config'])
        era=campaign.advance_era('calm',released_grids=[a.grid,b.grid],released_sources=sources)
        self.assertEqual(a.grid,b.grid)
        inputs=decode_execution_inputs(era['execution'])
        self.assertEqual([source['care_context'] for source in sources],inputs['founder_care_contexts'])
        rows=era['execution']['manifest']['founder_occurrences']
        self.assertEqual([0,1],[row['ordinal'] for row in rows])
        self.assertEqual([a.lineage[-1]['life_id'],b.lineage[-1]['life_id']],[row['care_context']['life_id'] for row in rows])

    def test_staging_rejects_care_from_a_different_body_before_writing(self):
        from mecha_game.contribute import companion_release_source
        from mecha_game.era_plan import EraPlan
        session=self.session();session.advance('feed')
        changed=copy.deepcopy(session.grid);changed['cells'][0]['mutation_weight']=.12345
        plan=EraPlan(None)
        with self.assertRaisesRegex(ValueError,'genome'):
            plan.stage([changed],[companion_release_source(session)])
        self.assertEqual([],plan.releases)

if __name__=='__main__': unittest.main()
