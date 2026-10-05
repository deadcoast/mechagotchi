"""W4 paused WFC diagnostics and foreground-owned cancellation."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'game/src'),str(ROOT/'packages/mecha_engine/src')]
import pygame
from mecha_game.app import run
from mecha_game.footer import FooterPager
from mecha_game.campaign import load_campaign_inputs,KeeperCampaign,TINY_ERA_CONFIG
from mecha_game.session import CompanionSession,load_session_inputs
from mecha_engine.generation import generate_wfc_grid
BASE=json.loads((ROOT/'data/game_client/wfc_trace_before_stage0.json').read_text())
def key(k):return pygame.event.Event(pygame.KEYDOWN,key=k,mod=0)
def files(root):return {p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob('*') if p.is_file()}

class WfcTraceViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs=load_campaign_inputs(ROOT/'data/seed_grids_16x16',ROOT/'data/slips/valid/slip_v2_cleanliness.json',ROOT/'data/readability_benchmark/adopted_readability_model.json',with_models=False)
        cls.pet=load_session_inputs(ROOT/'data/seed_grids_16x16/mg_seed16_001_beetle.json',ROOT/'data/slips/valid/slip_v2_cleanliness.json')
    def seed(self,keeper,policy='incumbent'):
        campaign=KeeperCampaign(copy.deepcopy(self.inputs),era_config=TINY_ERA_CONFIG,campaign_id='wfc_view_test');campaign.save(keeper/'campaign.sqlite3');campaign.save_state(keeper/'campaign_state.json')
        g,s,m=self.pet;CompanionSession(g,s,model=m,learning_policy=policy).save_checkpoint(keeper/'companion.json')
    def observe(self,keeper,batches,busy=None):
        events=iter(batches);pages=[];original=FooterPager.layout
        def poll():
            batch=next(events,[pygame.event.Event(pygame.QUIT)])
            return batch() if callable(batch) else batch
        def layout(self,lines,measure,width,rows):
            page=original(self,lines,measure,width,rows);pages.append({'all':list(lines),'visible':list(page.lines),'page':page.page});return page
        with patch.dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'),patch('pygame.event.get',side_effect=poll),patch.object(FooterPager,'layout',layout),patch('mecha_game.app.load_campaign_inputs',return_value=copy.deepcopy(self.inputs)),patch('pygame.event.poll',side_effect=busy or (lambda:pygame.event.Event(pygame.NOEVENT))):
            result=run(['--keeper-dir',str(keeper),'--era-scale','tiny','--scale','1','--fps','0','--tick-frames','1'])
        self.assertEqual(0,result);return pages
    def test_open_step_help_final_back_and_close_preserve_all_saves_both_policies(self):
        for policy in ('incumbent','qtable'):
            with self.subTest(policy=policy),tempfile.TemporaryDirectory() as d:
                keeper=Path(d);self.seed(keeper,policy);before=files(keeper)
                pages=self.observe(keeper,[[key(pygame.K_h)],[key(pygame.K_TAB)],[key(pygame.K_SPACE)],[],[key(pygame.K_F1)],[key(pygame.K_ESCAPE)],
                  [key(pygame.K_END)],[key(pygame.K_v)],[key(pygame.K_RIGHTBRACKET)],[key(pygame.K_PERIOD)],[key(pygame.K_RETURN)],
                  [key(pygame.K_TAB)],[key(pygame.K_ESCAPE),key(pygame.K_f)]])
                self.assertTrue(any('WFC TRACE' in ' '.join(p['all']) for p in pages));self.assertTrue(any('WFC FINAL BODY' in ' '.join(p['all']) for p in pages))
                self.assertEqual(before,files(keeper))
    def test_wave_reconstructs_actual_choices_and_finished_matrix(self):
        from mecha_game.wfc_trace import WfcTraceView
        trace=[];grid=generate_wfc_grid(BASE['models']['finish_retry'],grid_id='view',rng_seed=3,trace=trace)
        view=WfcTraceView(grid,trace)
        for i,event in enumerate(trace):
            view.index=i;wave=view.wave()
            if event['event']=='wave_started':self.assertEqual(event['cells'],wave)
            if event['event']=='cell_collapsed':self.assertEqual({event['token']:1},wave[','.join(map(str,event['position']))])
            if event['event']=='propagated':self.assertEqual(event['remaining'],wave[','.join(map(str,event['target']))])
            if event['event']=='finished':
                self.assertEqual(event['matrix'],[''.join(next(iter(wave[f'{x},{y}'])) for x in range(4)) for y in range(4)])
        saved=copy.deepcopy(trace);view.step(-1);view.move_attempt(-1);view.move_attempt(1);self.assertEqual(saved,trace)
    def test_genuine_failure_keeps_events_and_disallows_final_body(self):
        from mecha_game.wfc_trace import WfcTraceView
        trace=[]
        try:generate_wfc_grid(BASE['models']['contradiction'],grid_id='failed',rng_seed=0,trace=trace)
        except ValueError as error:reason=str(error)
        view=WfcTraceView(None,trace,error=reason);view.index=len(trace)-1;view.toggle_final()
        self.assertFalse(view.final);self.assertIn('exhausted',' '.join(view.lines()));self.assertIn(reason,' '.join(view.lines()))
        self.assertEqual(8,len(view.attempts))
    def test_worker_joins_after_cancellation_without_changing_engine_outcome(self):
        from mecha_game.wfc_trace import WfcWork
        def operation(events):
            time.sleep(.04)
            return generate_wfc_grid(BASE['models']['finish_retry'],grid_id='join',rng_seed=4,trace=events)
        work=WfcWork(operation);work.start();work.cancel();work.join()
        self.assertFalse(work.thread.is_alive());self.assertTrue(work.cancelled)
        self.assertEqual(generate_wfc_grid(BASE['models']['finish_retry'],grid_id='join',rng_seed=4),work.grid)
    def test_slow_cancel_and_window_close_keep_polling_and_join(self):
        from mecha_game import wfc_trace
        original=wfc_trace.capture_wfc
        def slow(*args,**kwargs):time.sleep(.08);return original(*args,**kwargs)
        for closing in (False,True):
            with self.subTest(closing=closing),tempfile.TemporaryDirectory() as d:
                keeper=Path(d);self.seed(keeper);before=files(keeper);count=[0]
                def busy():
                    count[0]+=1
                    return pygame.event.Event(pygame.QUIT) if closing and count[0]==2 else key(pygame.K_ESCAPE) if count[0]==2 else pygame.event.Event(pygame.NOEVENT)
                with patch.object(wfc_trace,'capture_wfc',slow):
                    self.observe(keeper,[[key(pygame.K_h)],[key(pygame.K_TAB)],[key(pygame.K_ESCAPE)]],busy)
                self.assertGreater(count[0],2);self.assertEqual(before,files(keeper))
                self.assertFalse(any(t.name=='mechagotchi-wfc' for t in threading.enumerate()))
    def test_failed_capture_retry_and_reopened_capture_are_explicit(self):
        from mecha_game import wfc_trace
        original=wfc_trace.capture_wfc;calls=[]
        def capture(seeds,grid_id,rng_seed,events):
            calls.append(rng_seed)
            if len(calls)==1:return generate_wfc_grid(BASE['models']['contradiction'],grid_id=grid_id,rng_seed=rng_seed,trace=events)
            return original(seeds,grid_id,rng_seed,events)
        with tempfile.TemporaryDirectory() as d:
            keeper=Path(d);self.seed(keeper);before=files(keeper)
            with patch.object(wfc_trace,'capture_wfc',capture):
                pages=self.observe(keeper,[[key(pygame.K_h)],[key(pygame.K_TAB)],[key(pygame.K_END)],[key(pygame.K_n)],[key(pygame.K_END)]])
            self.assertTrue(any('wave contradiction' in ' '.join(p['all']) for p in pages))
            self.assertTrue(any('generated' in ' '.join(p['all']) for p in pages))
            self.assertNotEqual(calls[0],calls[1]);self.assertEqual(before,files(keeper))
            pages=self.observe(keeper,[[key(pygame.K_h)],[key(pygame.K_TAB)]])
            self.assertTrue(any('Fresh capture; session-only' in ' '.join(p['all']) for p in pages));self.assertEqual(before,files(keeper))

    def test_empty_capture_error_is_inspectable_and_can_retry(self):
        from mecha_game.wfc_trace import WfcTraceView
        view=WfcTraceView(None,[],error='corpus unavailable')
        self.assertEqual({},view.wave());self.assertTrue(view.pixels(1));view.step(1);view.move_attempt(-1);view.toggle_final()
        self.assertIn('corpus unavailable',' '.join(view.lines()))
        from mecha_game import wfc_trace
        original=wfc_trace.capture_wfc;calls=[0]
        def capture(*args,**kwargs):
            calls[0]+=1
            if calls[0]==1:raise ValueError('corpus unavailable')
            return original(*args,**kwargs)
        with tempfile.TemporaryDirectory() as d:
            keeper=Path(d);self.seed(keeper);before=files(keeper)
            with patch.object(wfc_trace,'capture_wfc',capture):
                pages=self.observe(keeper,[[key(pygame.K_h)],[key(pygame.K_TAB)],[key(pygame.K_n)]])
            self.assertTrue(any('corpus unavailable' in ' '.join(p['all']) for p in pages));self.assertEqual(before,files(keeper))

    def test_initial_wave_is_visible_with_earlier_metadata_still_reachable(self):
        from mecha_game.wfc_trace import WfcTraceView
        events=[];grid=generate_wfc_grid(BASE['models']['finish_retry'],grid_id='visible',rng_seed=3,trace=events)
        view=WfcTraceView(grid,events)
        self.assertEqual('wave_started',view.event['event']);self.assertTrue(view.wave())
        view.index=0;self.assertEqual('generation_started',view.event['event'])

    def test_origin_view_does_not_open_an_unadvertised_fresh_generator(self):
        from mecha_game import wfc_trace
        with tempfile.TemporaryDirectory() as d:
            keeper=Path(d);self.seed(keeper);before=files(keeper)
            with patch.object(wfc_trace,'capture_wfc',side_effect=AssertionError('origin is read-only')) as capture:
                self.observe(keeper,[[key(pygame.K_o)],[key(pygame.K_TAB)]])
            capture.assert_not_called();self.assertEqual(before,files(keeper))

    def test_wfc_close_batch_cannot_adopt_or_advance_original_hatch(self):
        with tempfile.TemporaryDirectory() as d:
            keeper=Path(d);self.seed(keeper);before=files(keeper)
            pages=self.observe(keeper,[[key(pygame.K_h)],[key(pygame.K_TAB)],[key(pygame.K_ESCAPE),key(pygame.K_RETURN),key(pygame.K_f)]])
            visible=[p for p in pages if p['all'] and p['all'][0].startswith('HATCH PREVIEW')]
            self.assertEqual(visible[0]['all'],visible[-1]['all']);self.assertEqual(before,files(keeper))

if __name__=='__main__':unittest.main()

