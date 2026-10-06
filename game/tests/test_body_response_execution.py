"""Immutable body model capture and reproduction boundaries."""
import copy,json,sys,unittest,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'game/src'),str(ROOT/'packages/mecha_engine/src')]
from mecha_game import execution
class BodyResponseExecutionTests(unittest.TestCase):
    def effective(self,**extra):
        return dict(seed_grids=[],slip_profile={},generation_model=None,repair_model=None,legibility_model=None,rng_seed=7,**extra)
    def test_legacy_explicit_is_same_captured_input_shape(self):
        left=execution.capture_execution('body',0,self.effective(),[])
        right=execution.capture_execution('body',0,self.effective(body_response='legacy'),[])
        self.assertEqual(left['manifest']['inputs'],right['manifest']['inputs'])
        self.assertNotIn('body_response',execution.decode_execution_inputs(left))
    def test_active_captures_and_decodes_immutable_model(self):
        bundle=execution.capture_execution('body',0,self.effective(body_response='workload-v1'),[])
        self.assertEqual({'body_response':'workload-v1'},execution.body_arguments(bundle))
        self.assertEqual('workload-v1',execution.decode_execution_inputs(bundle)['body_response'])
        digest=bundle['manifest']['inputs']['body_response_inputs_sha256']
        self.assertEqual(dict(format='body_response_inputs_v1',body_response='workload-v1'),execution.blob_json(bundle,digest))
    def test_unknown_body_model_and_context_model_conflict_refuse(self):
        with self.assertRaisesRegex(ValueError,'body'):
            execution.capture_execution('body',0,self.effective(body_response='workload-v2'),[])
    def test_new_body_module_is_in_runtime_closure(self):
        self.assertIn('mecha_engine.lifecycle._body_response',execution.EXECUTION_MODULES)

    def test_actual_active_result_records_and_reproduces_readonly(self):
        from mecha_engine.generation import train_generation_model
        from mecha_engine.repair import train_repair_model
        from mecha_engine.runtime import evolve, learned_readability_score
        from mecha_engine.storage import load_era_execution
        from contextlib import closing
        import importlib.util,sqlite3
        module_spec=importlib.util.spec_from_file_location('body_recording_operational',ROOT/'labs/game_loop/body_workload_recording.py')
        recording=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(recording)
        grid=json.loads((ROOT/'data/seed_grids/mg_seed_001.json').read_text())
        slip=json.loads((ROOT/'data/slips/valid/slip_lcd_seed.json').read_text())
        inputs=dict(seed_grids=[grid],slip_profile=slip,generation_model=train_generation_model([grid]),
            repair_model=train_repair_model([grid],epochs=1,rng_seed=7),legibility_model={'weights':{},'reference_features':{}},
            readability_selection=None,weather_sources={'storm':[{'snapshot_id':'operational'}]})
        spec=dict(body_response='workload-v1',rng_seed=73,config=dict(generations=1,population=1,damage_cycles=1,ticks=3,dropout_rate=0))
        with tempfile.TemporaryDirectory() as tmp:
            home=Path(tmp)/'record'
            bundle,data=recording.prepare_record(home,inputs,spec)
            admissions=[]
            archive,report=evolve(data['seed_grids'],data['slip_profile'],data['generation_model'],data['repair_model'],
                readability_scorer=lambda g:learned_readability_score(g,data['legibility_model']),
                rng_seed=data['rng_seed'],founder_grids=data['founder_grids'],cubff_pressure_source=data['cubff_pressure_source'],
                readability_selection=data['readability_selection'],admission_callback=admissions.append,
                **data['effective_config'],**execution.body_arguments(bundle),**execution.population_arguments(bundle))
            receipt=recording.record_result(home,bundle,archive,report,admissions)
            from mecha_game.campaign import KeeperCampaign
            resumed=KeeperCampaign.load_state(data,home/'campaign_state.json',home/'campaign.sqlite3')
            self.assertEqual('workload-v1',resumed.body_response)
            self.assertEqual(1,resumed.era_offset)
            self.assertEqual(report['living_population']['final_breeders'],resumed.resume_breeders)
            before=(home/'campaign.sqlite3').read_bytes()
            result=recording.reproduce_record(home)
            self.assertEqual('matched',result['status'],result['reason'])
            self.assertEqual(before,(home/'campaign.sqlite3').read_bytes())
            with self.assertRaisesRegex(ValueError,'already exists'):recording.record_result(home,bundle,archive,report,admissions)
            # A self-consistent forged F/cost still disagrees with the actual body.
            forged=copy.deepcopy(report);endpoint=forged['generations'][0]['creatures'][0]['cycles'][0]['episode']
            workload=endpoint['body_workload'];workload['functional_capacity']=0
            workload['play_energy_cost']=round(.07*workload['occupied_mass']/workload['capacity_floor'],6)
            elites=[{'niche_key':niche,**archive['elites'][niche]} for niche in sorted(archive['elites'])]
            with self.assertRaisesRegex(ValueError,'actual evaluated body'):
                execution.finalize_execution(bundle,admissions,forged,elites)
            # Swapping both evaluated body and cost must also fail against
            # the independently captured final breeder body.
            swapped=copy.deepcopy(report)
            endpoint=swapped['generations'][0]['creatures'][0]['breeding']['final_episode']
            endpoint['evaluated_grid']['grid_id']='foreign-evaluated-body'
            with self.assertRaisesRegex(ValueError,'actual recorded body'):
                execution.finalize_execution(bundle,admissions,swapped,elites)
            with closing(sqlite3.connect(home/'campaign.sqlite3')) as conn:
                persisted=load_era_execution(conn,receipt['campaign_id'],0)
            self.assertEqual('workload-v1',execution.body_arguments(persisted)['body_response'])
