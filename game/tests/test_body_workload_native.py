"""Registered workload-v1 operational coverage; no holdout qualification."""
import copy
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
import uuid
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
for folder in ('game/src','packages/mecha_engine/src'):sys.path.insert(0,str(ROOT/folder))
from mecha_engine.lifecycle import initial_state,advance_tick
from mecha_game.session import CompanionSession,load_session_inputs
from mecha_game.care_history import capture_care_context,validate_care_selection
from mecha_game.app import _footer_lines,build_parser
from mecha_game.lineage import LineageBrowser
from mecha_game import campaign as api
from mecha_game.era_plan import EraPlan
from mecha_game.execution import decode_execution_inputs,reproduce_era
ACTIVE='workload-v1'
def pet(**kwargs):
    grid,profile,model=load_session_inputs(ROOT/'data/seed_grids_16x16/mg_seed16_001_beetle.json',ROOT/'data/slips/valid/slip_v2_cleanliness.json')
    return CompanionSession(grid,profile,model=model,**kwargs)
class BodyWorkloadNativeTests(unittest.TestCase):
    def test_prechange_off_bundle_hashes(self):
        expected={'incumbent':'e37b9adac73df443fdd0de0a79c7ac024002f756343e8aafa60762126a974ff6','qtable':'7091d224cd52f45458bc753a929edc9d7fc538f0baad77738c0cdb8d625d1031'}
        for policy,digest in expected.items():
            with self.subTest(policy=policy),patch('mecha_game.chronicle.uuid.uuid4',side_effect=[uuid.UUID(int=x) for x in range(1,10)]):
                s=pet(learning_policy=policy)
                for action in ['play','feed',None,'sleep','mutate','idle']*8:s.advance(action)
                value=dict(grid=s.grid,state=s.state,lineage=s.lineage,chronicle=s.chronicle,snapshot=s.snapshot(),care_context=capture_care_context(s),footer=_footer_lines(s.snapshot(),None),history=LineageBrowser(s.lineage,chronicle=s.chronicle).detail_lines())
                raw=json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
                self.assertEqual(digest,hashlib.sha256(raw).hexdigest())
    def test_active_native_calls_shared_lifecycle_and_exposes_cost(self):
        s=pet(body_response=ACTIVE,fleet=False);expected=initial_state(s.grid,s.slip_profile,body_response=ACTIVE)
        for action in ('play','feed','sleep','idle','mutate'):
            expected=advance_tick(expected,action);s.advance(action);self.assertEqual(expected,s.state)
        self.assertEqual(ACTIVE,s.snapshot()['body_response'])
        self.assertIn('Play energy',' '.join(_footer_lines(s.snapshot(),None)))
        self.assertIn('workload-v1',' '.join(LineageBrowser(s.lineage).detail_lines()))
    def test_restart_conflicts_tampered_projection_and_backup_preservation(self):
        s=pet(body_response=ACTIVE,learning_policy='qtable')
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'companion.json';s.save(path);s.advance('play');s.save(path)
            before={p.name:p.read_bytes() for p in Path(tmp).glob('*')}
            with self.assertRaises(ValueError):CompanionSession.load(path,body_response='legacy')
            with self.assertRaises(ValueError):CompanionSession.recover_backup(path,body_response='legacy')
            self.assertEqual(before,{p.name:p.read_bytes() for p in Path(tmp).glob('*')})
            loaded=CompanionSession.load(path);self.assertEqual(s.state,loaded.state)
            for action in ('feed','play','sleep'):s.advance(action);loaded.advance(action)
            self.assertEqual(s.state,loaded.state)
            payload=json.loads(path.read_text());payload['state']['body_workload']['play_energy_cost']=.123
            with self.assertRaises(ValueError):CompanionSession._from_payload(payload)
            restored,archive=CompanionSession.recover_backup(path)
            self.assertEqual(ACTIVE,restored.body_response);self.assertEqual(0,restored.state['age_ticks'])
            self.assertEqual(before['companion.json'],archive.read_bytes())
    def test_actual_death_and_successor_keep_model_but_start_cold(self):
        s=pet(body_response=ACTIVE,learning_policy='qtable',care_selection_policy='observed_care_selection_v2');s.advance('play')
        for _ in range(400):
            if not s.alive:break
            s.advance()
        self.assertFalse(s.alive);parent=copy.deepcopy(s.lineage[-1]);s.succeed()
        self.assertEqual(ACTIVE,s.body_response);self.assertNotIn('thread_states',s.state);self.assertEqual(0,s.state['age_ticks'])
        self.assertEqual(initial_state(s.grid,s.slip_profile,body_response=ACTIVE)['body_workload'],s.state['body_workload'])
        self.assertEqual(ACTIVE,s.lineage[-1]['care_selection']['context']['body_response'])
        validate_care_selection(s.lineage[-1]['care_selection'],parent_record=parent,child_grid=s.grid,child_record=s.lineage[-1])
        legacy=s.adopt(s.grid,s.slip_profile,body_response='legacy')
        self.assertNotIn('body_response',legacy.state);self.assertEqual(ACTIVE,legacy.lineage[-2]['body_response'])
    def test_active_model_and_context_cannot_be_relabelled(self):
        for model in ('invented',None,False):
            with self.subTest(model=model),self.assertRaises(ValueError):pet(body_response=model)
        s=pet(body_response=ACTIVE);s.advance('play');self.assertEqual(ACTIVE,capture_care_context(s)['body_response'])
        with tempfile.TemporaryDirectory() as tmp:
            p=s.save(Path(tmp)/'pet.json');payload=json.loads(p.read_text());payload.pop('body_response')
            with self.assertRaises(ValueError):CompanionSession._from_payload(payload)
    def test_active_v1_v2_cost_labels_cannot_hide_forged_energy_trajectory(self):
        from mecha_engine.runtime.care import select_care_successor
        for policy in ('observed_care_selection_v1','observed_care_selection_v2'):
            with self.subTest(policy=policy):
                s=pet(body_response=ACTIVE);s.advance('play');s.advance('feed')
                child,receipt=select_care_successor(s.grid,s.model,s.slip_profile,context=capture_care_context(s),rng_seed=8181,policy=policy,body_response=ACTIVE)
                selected=dict(context=capture_care_context(s),receipt=receipt)
                row=selected['receipt']['candidates'][0];episode=row['episode']
                for result in (episode['history'][-1],episode['trajectory'][-1]['result'],episode['final_state']['history'][-1]):result['state']['energy']=.123
                episode['final_state']['energy']=.123
                with self.assertRaisesRegex(ValueError,'energy transition'):validate_care_selection(selected,parent_record=s.lineage[-1],child_grid=child)
    def test_active_v1_selection_and_all_ranked_body_evidence_roundtrip(self):
        s=pet(body_response=ACTIVE,care_selection_policy='observed_care_selection_v1');s.advance('play')
        while s.alive:s.advance()
        parent=copy.deepcopy(s.lineage[-1]);s.succeed()
        selected=s.lineage[-1]['care_selection']
        validate_care_selection(selected,parent_record=parent,child_grid=s.grid)
        bad=copy.deepcopy(selected);row=bad['receipt']['candidates'][(bad['receipt']['selected_index']+1)%8]
        row['candidate_grid']['cells'][0]['damage']=.5
        with self.assertRaises(ValueError):validate_care_selection(bad,parent_record=parent,child_grid=s.grid)
        with tempfile.TemporaryDirectory() as tmp:
            path=s.save(Path(tmp)/'pet.json');self.assertEqual(s.lineage,CompanionSession.load(path).lineage)
    def test_native_parser_preserves_saved_model_sentinel(self):
        self.assertIsNone(build_parser().parse_args([]).body_response)
        self.assertEqual(ACTIVE,build_parser().parse_args(['--body-response',ACTIVE]).body_response)
    def test_campaign_captures_and_recovers_immutable_model(self):
        inputs=api.load_campaign_inputs(**api.default_campaign_paths(ROOT),seed_limit=4,repair_epochs=1)
        campaign=api.KeeperCampaign(copy.deepcopy(inputs),campaign_id='workload-operational',population_policy='generation_survivors_v1',body_response=ACTIVE,era_config=dict(generations=1,population=2,damage_cycles=1,ticks=3,dropout_rate=.2))
        with self.assertRaises(AttributeError):campaign.body_response='legacy'
        era=campaign.advance_era('calm',record_original=True)
        self.assertEqual(ACTIVE,decode_execution_inputs(era['execution'])['body_response']);self.assertEqual(ACTIVE,campaign.state_payload()['body_response'])
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);ledger=root/'campaign.sqlite3';state=root/'campaign_state.json';plan=EraPlan(root/'era_plan.json');plan.begin(campaign,era,None)
            with patch.object(api.KeeperCampaign,'save_state',side_effect=OSError('injected interruption')):
                with self.assertRaises(OSError):plan.finish(ledger,state)
            reopened=EraPlan(plan.path);reopened.finish(ledger,state)
            restored=api.KeeperCampaign.load_state(copy.deepcopy(inputs),state,ledger);self.assertEqual(ACTIVE,restored.body_response)
            with closing(sqlite3.connect(ledger.as_uri()+'?mode=ro',uri=True)) as conn:self.assertEqual('matched',reproduce_era(conn,'workload-operational',0)['status'])
            bad=json.loads(state.read_text());bad.pop('body_response');state.write_text(json.dumps(bad))
            with self.assertRaises(ValueError):api.KeeperCampaign.load_state(copy.deepcopy(inputs),state,ledger)

class BodyWorkloadNativeUiTests(unittest.TestCase):
    def setUp(self):
        import os
        import pygame
        self.env=patch.dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy');self.env.start()
        self.addCleanup(self.env.stop);pygame.init();self.addCleanup(pygame.quit)
        self.font=pygame.font.Font(None,22)
    def test_new_body_toggle_is_visible_repeat_safe_and_cancel_resets(self):
        import pygame
        from mecha_game.native_ui import StartupView
        from test_native_ui import inspection,key
        for width in (384,640,1024):
            view=StartupView(inspection(primary='missing',backup='missing'))
            view._transition('new');surface=pygame.Surface((width,620))
            view.draw(surface,self.font);view.strip.focus('new_body');view.draw(surface,self.font)
            self.assertIn('new_body',view.button_rects)
            view.handle(key(pygame.K_RETURN));self.assertEqual(ACTIVE,view.new_body_response)
            for _ in range(5):view.handle(key(pygame.K_RETURN))
            self.assertEqual(ACTIVE,view.new_body_response)
            view.draw(surface,self.font);view.strip.focus('confirm_new');view.draw(surface,self.font)
            view.handle(key(pygame.K_RETURN,up=True));result=view.handle(key(pygame.K_RETURN))
            self.assertEqual('confirm_new',result.action);self.assertEqual(ACTIVE,result.body_response)
            view._transition('home');view._transition('new');self.assertEqual('legacy',view.new_body_response)
    def test_native_process_new_restart_conflict_and_explicit_new_switch(self):
        import contextlib,io
        from mecha_game.app import run
        with tempfile.TemporaryDirectory() as tmp:
            home=Path(tmp)
            def launch(*flags):return run(['--keeper-dir',str(home),'--ticks','1','--tick-frames','1','--fps','0',*flags])
            self.assertEqual(0,launch('--new','--body-response',ACTIVE))
            prior=CompanionSession.load(home/'companion.json');self.assertEqual(ACTIVE,prior.body_response)
            self.assertEqual(0,launch());resumed=CompanionSession.load(home/'companion.json')
            self.assertEqual(ACTIVE,resumed.body_response);self.assertEqual(2,resumed.session_tick)
            before={p.name:p.read_bytes() for p in home.glob('companion*.json')}
            with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):launch('--body-response','legacy')
            self.assertEqual(before,{p.name:p.read_bytes() for p in home.glob('companion*.json')})
            self.assertEqual(0,launch('--new','--body-response','legacy'))
            fresh=CompanionSession.load(home/'companion.json');self.assertEqual('legacy',fresh.body_response)
            self.assertEqual(ACTIVE,fresh.lineage[-2]['body_response']);self.assertEqual(prior.keeper_id,fresh.keeper_id)
    def test_inspection_refresh_omission_keeps_existing_body_default(self):
        from mecha_game.native_ui import StartupView
        from test_native_ui import inspection
        view=StartupView(inspection(),new_body_response=ACTIVE)
        view.set_inspection(inspection())
        self.assertEqual(ACTIVE,view.new_body_response)
        view.set_inspection(inspection(),new_learning_policy='incumbent')
        self.assertEqual(ACTIVE,view.new_body_response)
    def test_existing_campaign_model_conflict_blocks_before_era(self):
        from mecha_game.app import _EraBench
        s=pet(body_response=ACTIVE)
        bench=_EraBench(era_scale='tiny',keeper_session=s)
        bench.campaign=api.KeeperCampaign({'slip_profile':s.slip_profile})
        with self.assertRaisesRegex(ValueError,'different body response'):bench.ensure()
    def test_saved_self_consistent_false_capacity_and_past_body_tampering_refuse(self):
        s=pet(body_response=ACTIVE)
        with self.assertRaises(AttributeError):s.body_response='legacy'
        with tempfile.TemporaryDirectory() as tmp:
            path=s.save(Path(tmp)/'pet.json');payload=json.loads(path.read_text())
            bad=copy.deepcopy(payload);value=bad['state']['body_workload'];value['functional_capacity']=value['occupied_mass'];value['play_energy_cost']=.07
            bad['lineage'][-1]['body_workload']=copy.deepcopy(value)
            with self.assertRaises(ValueError):CompanionSession._from_payload(bad)
            adopted=s.adopt(s.grid,s.slip_profile);adopted.save(path);bad=json.loads(path.read_text());bad['lineage'][0]['body_grid']['cells'][0]['damage']=.5
            with self.assertRaises(ValueError):CompanionSession._from_payload(bad)

if __name__=='__main__':unittest.main()

