"""W3: real constrained explanation, explicit adoption and paused source UI."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
for folder in ('game/src','packages/mecha_engine/src'):
    sys.path.insert(0,str(ROOT/folder))
import pygame
from mecha_game.app import run, _EraBench
from mecha_game.campaign import KeeperCampaign,TINY_ERA_CONFIG,load_campaign_inputs
from mecha_game.session import CompanionSession,load_session_inputs
from mecha_game.footer import FooterPager
from mecha_game.hatchery import hatch_founders
from mecha_engine.generation import explain_generation
from mecha_engine.genome import render_packet_v2

def key(k,mod=0,repeat=False):
    return pygame.event.Event(pygame.KEYDOWN,key=k,mod=mod,repeat=repeat)
def files(root):
    return {p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob('*') if p.is_file()}

class HatchPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs=load_campaign_inputs(ROOT/'data/seed_grids_16x16',ROOT/'data/slips/valid/slip_v2_cleanliness.json',ROOT/'data/readability_benchmark/adopted_readability_model.json',seed_limit=12,with_models=False)
        cls.pet=load_session_inputs(ROOT/'data/seed_grids_16x16/mg_seed16_001_beetle.json',ROOT/'data/slips/valid/slip_v2_cleanliness.json')
        cls.profile=json.loads((ROOT/'data/slips/valid/slip_lcd_seed.json').read_text())
        cls.hatched=hatch_founders(cls.inputs['seed_grids'],cls.pet[1],rng_seed=20260714)[0]

    def seed(self,keeper,policy='incumbent',hatched=False):
        campaign=KeeperCampaign(copy.deepcopy(self.inputs),era_config=TINY_ERA_CONFIG,campaign_id='preview_test')
        campaign.save(keeper/'campaign.sqlite3');campaign.save_state(keeper/'campaign_state.json')
        grid,slip,model=self.pet
        session = CompanionSession(self.hatched['grid'] if hatched else grid,slip,model=model,learning_policy=policy)
        session.bind_campaign(campaign.campaign['campaign_id'])
        session.save_checkpoint(keeper/'companion.json')

    def observe(self,keeper,batches):
        events=iter(batches);pages=[];original=FooterPager.layout
        def poll():
            batch=next(events,[pygame.event.Event(pygame.QUIT)])
            return batch() if callable(batch) else batch
        def capture(pager,lines,measure,width,rows):
            result=original(pager,lines,measure,width,rows)
            pages.append({'all':list(lines),'visible':list(result.lines),'page':result.page,'pages':result.page_count})
            return result
        with patch.dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'),patch('pygame.event.get',side_effect=poll),patch.object(FooterPager,'layout',capture),patch('mecha_game.app.load_campaign_inputs',return_value=copy.deepcopy(self.inputs)):
            result=run(['--keeper-dir',str(keeper),'--era-scale','tiny','--scale','1','--fps','0','--tick-frames','1'])
        self.assertEqual(0,result)
        return pages

    def test_hatch_open_cancel_help_and_closing_batch_are_read_only(self):
        for policy in ('incumbent','qtable'):
            with self.subTest(policy=policy),tempfile.TemporaryDirectory() as d:
                keeper=Path(d);self.seed(keeper,policy);before=files(keeper)
                pages=self.observe(keeper,[[key(pygame.K_h)],[key(pygame.K_f),key(pygame.K_e)],[key(pygame.K_F1)],[key(pygame.K_ESCAPE)],[key(pygame.K_ESCAPE),key(pygame.K_f),key(pygame.K_RETURN)]])
                self.assertIn('HATCH PREVIEW',' '.join(pages[0]['visible']))
                self.assertEqual(before,files(keeper))

    def test_origin_reopens_verbatim_without_writes(self):
        with tempfile.TemporaryDirectory() as d:
            keeper=Path(d);self.seed(keeper,hatched=True);before=files(keeper)
            pages=self.observe(keeper,[[key(pygame.K_o)],[key(pygame.K_RETURN)],[key(pygame.K_PAGEDOWN)],[key(pygame.K_ESCAPE)]])
            self.assertIn('ORIGIN TRACE',' '.join(pages[0]['visible']))
            self.assertIn('generator_strategy',' '.join(pages[0]['all']))
            self.assertGreater(pages[2]['page'],0)
            self.assertEqual(before,files(keeper))

    def test_missing_trace_is_honest_and_read_only(self):
        with tempfile.TemporaryDirectory() as d:
            keeper=Path(d);self.seed(keeper);before=files(keeper)
            pages=self.observe(keeper,[[key(pygame.K_o)],[key(pygame.K_n)],[key(pygame.K_RETURN)]])
            self.assertIn('unavailable',' '.join(pages[0]['all']).lower())
            self.assertEqual(before,files(keeper))

    def test_named_import_preview_adopt_and_restart_retains_actual_trace_and_policy(self):
        for policy in ('incumbent','qtable'):
            with self.subTest(policy=policy),tempfile.TemporaryDirectory() as d:
                keeper=Path(d);self.seed(keeper,policy);(keeper/'covenants').mkdir();(keeper/'covenants/chosen.json').write_text(json.dumps(self.profile))
                before=(keeper/'companion.json').read_bytes()
                def adopt():
                    self.assertEqual(before,(keeper/'companion.json').read_bytes())
                    return [key(pygame.K_RETURN),key(pygame.K_RETURN),key(pygame.K_f)]
                self.observe(keeper,[[key(pygame.K_i)],[key(pygame.K_RETURN)],[key(pygame.K_ESCAPE)],[key(pygame.K_h)],adopt])
                pet=CompanionSession.load(keeper/'companion.json')
                self.assertEqual(self.profile,pet.slip_profile);self.assertEqual(policy,pet.learning_policy)
                self.assertEqual(0,pet.state['age_ticks']);self.assertEqual(20260714,explain_generation(pet.grid)['rng_seed'])
                saved=files(keeper);pages=self.observe(keeper,[[key(pygame.K_o)]])
                self.assertIn(pet.grid['grid_id'],' '.join(pages[0]['all']));self.assertEqual(saved,files(keeper))

    def test_generation_failure_can_retry_without_adopting(self):
        with tempfile.TemporaryDirectory() as d:
            keeper=Path(d);self.seed(keeper);before=files(keeper)
            with patch.object(_EraBench,'hatch',side_effect=[ValueError('no aligned seed'),self.hatched]):
                pages=self.observe(keeper,[[key(pygame.K_h)],[key(pygame.K_n)]])
            self.assertIn('no aligned seed',' '.join(pages[0]['all']))
            self.assertIn(self.hatched['grid']['grid_id'],' '.join(pages[1]['all']))
            self.assertEqual(before,files(keeper))

    def test_external_campaign_change_refuses_adoption(self):
        with tempfile.TemporaryDirectory() as d:
            keeper=Path(d);self.seed(keeper);before=(keeper/'companion.json').read_bytes();changed=None
            def conflict():
                nonlocal changed
                p=keeper/'campaign_state.json';changed=p.read_bytes()+b' ';p.write_bytes(changed)
                return [key(pygame.K_RETURN)]
            pages=self.observe(keeper,[[key(pygame.K_h)],conflict])
            self.assertIn('changed',' '.join(pages[1]['all']))
            self.assertEqual(before,(keeper/'companion.json').read_bytes());self.assertEqual(changed,(keeper/'campaign_state.json').read_bytes())

    def test_view_uses_complete_exact_explanation_and_engine_packet(self):
        from mecha_game.generation_view import GenerationView
        original=copy.deepcopy(self.hatched['grid']);profile=copy.deepcopy(self.pet[1])
        view=GenerationView(original,profile,adoptable=True)
        self.assertEqual(explain_generation(original),view.explanation)
        self.assertEqual(render_packet_v2(original,None,slip_profile=profile,clip='idle',frame_index=0),view.packet())
        for field,value in view.explanation.items():
            self.assertIn(field+': '+json.dumps(value,ensure_ascii=True,sort_keys=True),'\n'.join(view.lines()))
        original['grid_id']='external edit';profile['profile_id']='external edit'
        self.assertEqual(self.hatched['grid'],view.grid);self.assertEqual(self.pet[1],view.profile)

    def test_animation_respects_engine_vocabulary_and_keeps_trace_paging(self):
        from mecha_game.generation_view import GenerationView
        view=GenerationView(self.hatched['grid'],self.pet[1])
        before=copy.deepcopy(view.explanation)
        for _ in range(8):
            view.move_clip(1)
            for _ in range(7):
                view.step(1);packet=view.packet()
                self.assertIn(packet['animation']['clip'],packet['animation_vocabulary'])
                self.assertLess(packet['animation']['frame_index'],packet['animation']['frame_count'])
        self.assertEqual(before,view.explanation)
        with tempfile.TemporaryDirectory() as d:
            keeper=Path(d);self.seed(keeper);saved=files(keeper)
            pages=self.observe(keeper,[[key(pygame.K_h)],[key(pygame.K_SPACE)],[key(pygame.K_PAGEDOWN)],[],[],[key(pygame.K_F1)],[key(pygame.K_ESCAPE)],[key(pygame.K_ESCAPE)]])
            self.assertEqual(pages[2]['page'],pages[4]['page']);self.assertEqual(saved,files(keeper))

    def test_save_failure_before_adoption_retains_preview_and_old_pet_for_retry(self):
        with tempfile.TemporaryDirectory() as d:
            keeper=Path(d);self.seed(keeper);before=(keeper/'companion.json').read_bytes()
            original=CompanionSession.save_checkpoint;locked=[True]
            def save(session,path):
                if locked[0]:raise PermissionError('old save lock')
                return original(session,path)
            def retry():
                self.assertEqual(before,(keeper/'companion.json').read_bytes());locked[0]=False
                return [key(pygame.K_s,pygame.KMOD_CTRL)]
            with patch.object(CompanionSession,'save_checkpoint',save):
                pages=self.observe(keeper,[[key(pygame.K_h)],[key(pygame.K_RETURN)],retry,[key(pygame.K_RETURN)]])
            self.assertIn('Save failed',' '.join(pages[1]['visible']))
            self.assertIn('HATCH PREVIEW',' '.join(pages[2]['all']))
            self.assertEqual(self.hatched['grid'],CompanionSession.load(keeper/'companion.json').grid)

    def test_save_failure_after_adoption_retains_previous_primary_until_retry(self):
        with tempfile.TemporaryDirectory() as d:
            keeper=Path(d);self.seed(keeper);before=(keeper/'companion.json').read_bytes()
            original=CompanionSession.save_checkpoint;locked=[True]
            def save(session,path):
                if locked[0] and session.grid['grid_id']==self.hatched['grid']['grid_id']:
                    raise PermissionError('new save lock')
                return original(session,path)
            def retry():
                self.assertEqual(before,(keeper/'companion.json').read_bytes());locked[0]=False
                return [key(pygame.K_s,pygame.KMOD_CTRL),pygame.event.Event(pygame.QUIT)]
            with patch.object(CompanionSession,'save_checkpoint',save):
                pages=self.observe(keeper,[[key(pygame.K_h)],[key(pygame.K_RETURN)],[key(pygame.K_f),key(pygame.K_h)],retry])
            self.assertIn('Save failed',' '.join(pages[1]['all']))
            pet=CompanionSession.load(keeper/'companion.json');self.assertEqual(self.hatched['grid'],pet.grid)
            self.assertEqual(0,pet.state['age_ticks'])

    def test_adoption_gate_failure_keeps_candidate_and_old_save(self):
        from mecha_game import session as api
        original=api.initial_state
        def gate(grid,*args,**kwargs):
            if grid['grid_id']==self.hatched['grid']['grid_id']:raise ValueError('engine adoption gate refused')
            return original(grid,*args,**kwargs)
        with tempfile.TemporaryDirectory() as d:
            keeper=Path(d);self.seed(keeper);before=files(keeper)
            with patch.object(api,'initial_state',gate):
                pages=self.observe(keeper,[[key(pygame.K_h)],[key(pygame.K_RETURN)]])
            self.assertIn('Adoption refused: engine adoption gate refused',' '.join(pages[1]['all']))
            self.assertEqual(before,files(keeper))

    def test_next_candidate_repeat_enter_and_render_do_not_change_generation_output(self):
        expected=hatch_founders(self.inputs['seed_grids'],self.pet[1],rng_seed=20260715)[0]
        with tempfile.TemporaryDirectory() as d:
            keeper=Path(d);self.seed(keeper);before=(keeper/'companion.json').read_bytes()
            def adopt():
                self.assertEqual(before,(keeper/'companion.json').read_bytes())
                return [key(pygame.K_RETURN)]
            self.observe(keeper,[[key(pygame.K_h)],[key(pygame.K_n)],[key(pygame.K_n,repeat=True)],
                [key(pygame.K_RETURN,repeat=True)],[key(pygame.K_SPACE)],[key(pygame.K_RIGHTBRACKET)],adopt])
            pet=CompanionSession.load(keeper/'companion.json')
            self.assertEqual(expected['grid'],pet.grid);self.assertEqual(expected['explanation'],explain_generation(pet.grid))

    def test_help_keeps_animation_position_and_every_trace_field_reachable(self):
        from mecha_game.generation_view import GenerationView
        original=GenerationView.packet;seen=[]
        def packet(view):
            result=original(view);seen.append((view.frame_index,view.playing));return result
        with tempfile.TemporaryDirectory() as d:
            keeper=Path(d);self.seed(keeper)
            with patch.object(GenerationView,'packet',packet):
                pages=self.observe(keeper,[[key(pygame.K_h)],[key(pygame.K_PERIOD)],[key(pygame.K_F1)],[],[key(pygame.K_ESCAPE)]]+
                    [[key(pygame.K_PAGEDOWN)] for _ in range(80)])
            self.assertEqual(pages[1]['all'],pages[4]['all'])
            self.assertEqual(pages[-1]['page'],pages[-1]['pages']-1)
            self.assertIn('model:', ' '.join(line for page in pages for line in page['visible']))

if __name__=='__main__':unittest.main()

