"""T5: foreground ownership, cancellation, real progress and T4 recovery."""
import copy
import importlib
import json
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
for folder in ('game/src','packages/mecha_engine/src'):sys.path.insert(0,str(ROOT/folder))
from mecha_game.app import _EraBench,run
from mecha_game.campaign import KeeperCampaign,TINY_ERA_CONFIG,load_campaign_inputs
from mecha_game.session import CompanionSession,load_session_inputs

def saved(path):
    return {p.relative_to(path).as_posix():p.read_bytes() for p in path.rglob('*') if p.is_file() and 'model_cache' not in p.parts}

class EraResponsivenessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs=load_campaign_inputs(ROOT/'data/seed_grids_16x16',ROOT/'data/slips/valid/slip_v2_cleanliness.json',ROOT/'data/readability_benchmark/adopted_readability_model.json',repair_epochs=6,seed_limit=12)
        cls.campaign=KeeperCampaign(cls.inputs,era_config=TINY_ERA_CONFIG,campaign_id='responsive_test')
        cls.campaign.advance_era('calm')
        cls.pet=load_session_inputs(ROOT/'data/seed_grids_16x16/mg_seed16_001_beetle.json',ROOT/'data/slips/valid/slip_v2_cleanliness.json')
    def fixture(self,path,policy='incumbent'):
        self.campaign.save(path/'campaign.sqlite3');self.campaign.save_state(path/'campaign_state.json')
        grid,slip,model=self.pet
        CompanionSession(grid,slip,model=model,learning_policy=policy).save_checkpoint(path/'companion.json')
        bench=_EraBench('tiny',path/'model_cache',path/'campaign_state.json',path/'campaign.sqlite3')
        bench.campaign=copy.deepcopy(self.campaign);bench.stage_releases([grid]);bench.choose_weather(2)
        return bench
    def api(self):return importlib.import_module('mecha_game.era_work')
    def test_observed_era_matches_synchronous_result_and_progress(self):
        api=self.api()
        with tempfile.TemporaryDirectory() as name:
            path=Path(name);bench=self.fixture(path);expected=copy.deepcopy(bench.campaign)
            expected_era=expected.advance_era('storm',released_grids=bench.plan.releases)
            work=api.EraWork(lambda observer:bench.run_era(path/'campaign.sqlite3',work=observer));work.start()
            self.assertEqual(expected_era,work.result())
            status=work.snapshot()
            self.assertEqual((12,12),(status['completed'],status['budget']))
            self.assertFalse(work.thread.is_alive());self.assertFalse(work.thread.daemon)
            self.assertIsNone(bench.plan.pending);self.assertEqual([],bench.plan.releases)
    def test_cancel_before_commit_preserves_all_saved_inputs_and_seed(self):
        api=self.api()
        for policy in ('incumbent','qtable'):
            with self.subTest(policy=policy),tempfile.TemporaryDirectory() as name:
                path=Path(name);bench=self.fixture(path,policy);before=saved(path)
                work=api.EraWork(lambda observer:bench.run_era(path/'campaign.sqlite3',work=observer))
                original=work.progress
                def cancel(completed,budget):
                    original(completed,budget)
                    if completed==1:work.cancel()
                work.progress=cancel;work.start()
                with self.assertRaises(api.EraCancelled):work.result()
                self.assertEqual(before,saved(path));self.assertEqual(self.campaign.eras,bench.campaign.eras)
                self.assertIsNone(bench._completed_work);self.assertFalse(work.thread.is_alive())
    def test_cancellation_wins_before_atomic_commit_boundary(self):
        api=self.api();entered=threading.Event();release=threading.Event()
        def operation(work):
            work.phase('Loading models');entered.set();release.wait(2);work.begin_commit();return 'saved'
        work=api.EraWork(operation);work.start();self.assertTrue(entered.wait(2))
        self.assertTrue(work.cancel());release.set()
        with self.assertRaises(api.EraCancelled):work.result()
        self.assertFalse(work.thread.is_alive())
    def test_commit_wins_and_close_cannot_discard_completed_result(self):
        api=self.api();entered=threading.Event();release=threading.Event()
        def operation(work):
            work.begin_commit();entered.set();release.wait(2);return 'saved'
        work=api.EraWork(operation);work.start();self.assertTrue(entered.wait(2))
        self.assertFalse(work.cancel());release.set();self.assertEqual('saved',work.result())
    def test_worker_failure_retains_t4_journal_and_retry_does_not_evolve(self):
        api=self.api()
        with tempfile.TemporaryDirectory() as name:
            path=Path(name);bench=self.fixture(path)
            with patch.object(KeeperCampaign,'save_state',side_effect=PermissionError('state locked')):
                work=api.EraWork(lambda observer:bench.run_era(path/'campaign.sqlite3',work=observer));work.start()
                with self.assertRaises(PermissionError):work.result()
            self.assertIsNotNone(bench.plan.pending);before=copy.deepcopy(bench.plan.pending['era'])
            with patch.object(KeeperCampaign,'advance_era',side_effect=AssertionError('must not rerun')):
                self.assertEqual(before,bench.run_era(path/'campaign.sqlite3'))
    def test_pygame_busy_events_cancel_without_care_or_extra_era(self):
        api=self.api()
        import pygame
        for policy in ('incumbent','qtable'):
            with self.subTest(policy=policy),tempfile.TemporaryDirectory() as name:
                path=Path(name);bench=self.fixture(path,policy);before=saved(path);pages=[]
                original=api.EraWork.progress;posted=threading.Event()
                def progress(work,n,total):
                    original(work,n,total)
                    if n==0 and not posted.is_set():
                        posted.set()
                        for key in (pygame.K_e,pygame.K_3,pygame.K_f,pygame.K_ESCAPE):
                            pygame.event.post(pygame.event.Event(pygame.KEYDOWN,key=key,mod=0))
                        work.cancel_requested.wait(2)
                        original(work,n,total)
                rows=iter([[pygame.event.Event(pygame.KEYDOWN,key=pygame.K_e,mod=0)],[pygame.event.Event(pygame.QUIT)]])
                with patch.dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'),patch('pygame.event.get',side_effect=lambda:next(rows,[pygame.event.Event(pygame.QUIT)])),patch('mecha_game.app._EraBench',return_value=bench),patch.object(api.EraWork,'progress',progress):
                    self.assertEqual(0,run(['--keeper-dir',str(path),'--era-scale','tiny','--scale','1','--fps','0','--tick-frames','1']))
                self.assertTrue(posted.is_set());self.assertEqual(before,saved(path))
                self.assertFalse(any(t.name=='mechagotchi-era' for t in threading.enumerate()))

    def test_window_close_joins_worker_and_preserves_both_companions(self):
        api=self.api()
        import pygame
        for policy in ('incumbent','qtable'):
            with self.subTest(policy=policy),tempfile.TemporaryDirectory() as name:
                path=Path(name);bench=self.fixture(path,policy);before=saved(path)
                original=api.EraWork.progress
                def progress(work,n,total):
                    original(work,n,total)
                    if n==0:
                        pygame.event.post(pygame.event.Event(pygame.QUIT))
                        work.cancel_requested.wait(2)
                        original(work,n,total)
                event=pygame.event.Event(pygame.KEYDOWN,key=pygame.K_e,mod=0)
                with patch.dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'),patch('pygame.event.get',return_value=[event]),patch('mecha_game.app._EraBench',return_value=bench),patch.object(api.EraWork,'progress',progress):
                    self.assertEqual(0,run(['--keeper-dir',str(path),'--scale','1','--fps','0','--tick-frames','1']))
                self.assertEqual(before,saved(path))
                self.assertFalse(any(t.name=='mechagotchi-era' for t in threading.enumerate()))

    def test_render_failure_cancels_and_joins_without_saved_mutation(self):
        api=self.api()
        import pygame
        from mecha_game.footer import FooterPager
        with tempfile.TemporaryDirectory() as name:
            path=Path(name);bench=self.fixture(path);before=saved(path)
            original=api.EraWork.progress
            def progress(work,n,total):
                original(work,n,total)
                if n==0:
                    work.cancel_requested.wait(2)
                    original(work,n,total)
            def broken_layout(*args):raise RuntimeError('observed rendering fault')
            event=pygame.event.Event(pygame.KEYDOWN,key=pygame.K_e,mod=0)
            with patch.dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'),patch('pygame.event.get',return_value=[event]),patch('mecha_game.app._EraBench',return_value=bench),patch.object(api.EraWork,'progress',progress),patch.object(FooterPager,'layout',broken_layout):
                with self.assertRaisesRegex(RuntimeError,'rendering fault'):
                    run(['--keeper-dir',str(path),'--scale','1','--fps','0','--tick-frames','1'])
            self.assertEqual(before,saved(path))
            self.assertFalse(any(t.name=='mechagotchi-era' for t in threading.enumerate()))

    def test_repeated_era_in_one_input_batch_does_not_run_twice(self):
        self.api()
        import pygame
        with tempfile.TemporaryDirectory() as name:
            path=Path(name);bench=self.fixture(path);old_count=bench.campaign.era_offset+len(bench.campaign.eras)
            companion=(path/'companion.json').read_bytes()
            rows=iter([[pygame.event.Event(pygame.KEYDOWN,key=k,mod=0) for k in (pygame.K_e,pygame.K_e,pygame.K_f,pygame.K_3)],[pygame.event.Event(pygame.QUIT)]])
            with patch.dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'),patch('pygame.event.get',side_effect=lambda:next(rows,[pygame.event.Event(pygame.QUIT)])),patch('mecha_game.app._EraBench',return_value=bench):
                self.assertEqual(0,run(['--keeper-dir',str(path),'--scale','1','--fps','0','--tick-frames','1']))
            self.assertEqual(old_count+1,json.loads((path/'campaign_state.json').read_text())['era_count'])
            self.assertEqual(companion,(path/'companion.json').read_bytes())

    def test_immediate_era_paints_the_held_companion_without_a_tick(self):
        api=self.api()
        import pygame
        with tempfile.TemporaryDirectory() as name:
            path=Path(name);bench=self.fixture(path);before=saved(path)
            rendered=threading.Event();colors=[];original=api.EraWork.progress;flip=pygame.display.flip
            def progress(work,n,total):
                original(work,n,total)
                if n==0:rendered.wait(2)
            def capture():
                flip()
                if not rendered.is_set():
                    surface=pygame.display.get_surface();left=(surface.get_width()-16)//2
                    colors.extend(surface.get_at((x,y))[:3] for x in range(left,left+16) for y in range(16))
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE,mod=0));rendered.set()
            rows=iter([[pygame.event.Event(pygame.KEYDOWN,key=pygame.K_e,mod=0)],[pygame.event.Event(pygame.QUIT)]])
            with patch.dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'),patch('pygame.event.get',side_effect=lambda:next(rows,[pygame.event.Event(pygame.QUIT)])),patch('mecha_game.app._EraBench',return_value=bench),patch.object(api.EraWork,'progress',progress),patch('pygame.display.flip',capture):
                self.assertEqual(0,run(['--keeper-dir',str(path),'--scale','1','--fps','0','--tick-frames','1']))
            self.assertTrue(any(g>80 for r,g,b in colors),'E before the first ordinary paint must not leave the companion panel blank')
            self.assertEqual(before,saved(path))

    def test_escape_and_close_already_batched_after_era_are_not_lost(self):
        api=self.api()
        import pygame
        for request in ('escape','close'):
            with self.subTest(request=request),tempfile.TemporaryDirectory() as name:
                path=Path(name);bench=self.fixture(path);before=saved(path)
                original=api.EraWork.progress
                def progress(work,n,total):
                    original(work,n,total)
                    if n==0:
                        work.cancel_requested.wait(2)
                        original(work,n,total)
                event=pygame.event.Event(pygame.QUIT) if request=='close' else pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE,mod=0)
                rows=iter([[pygame.event.Event(pygame.KEYDOWN,key=pygame.K_e,mod=0),event],[pygame.event.Event(pygame.QUIT)]])
                with patch.dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'),patch('pygame.event.get',side_effect=lambda:next(rows,[pygame.event.Event(pygame.QUIT)])),patch('mecha_game.app._EraBench',return_value=bench),patch.object(api.EraWork,'progress',progress):
                    self.assertEqual(0,run(['--keeper-dir',str(path),'--scale','1','--fps','0','--tick-frames','1']))
                self.assertEqual(before,saved(path))

    def test_close_during_blocked_loading_keeps_painting_and_preserves_saves(self):
        api = self.api()
        import pygame
        for policy in ('incumbent', 'qtable'):
            with self.subTest(policy=policy), tempfile.TemporaryDirectory() as name:
                path = Path(name)
                bench = self.fixture(path, policy)
                bench.campaign = None
                before = saved(path)
                loading = threading.Event()
                release = threading.Event()
                accepted = []
                frames = []
                main_thread = threading.get_ident()
                cancel = api.EraWork.cancel
                flip = pygame.display.flip

                def load(*args, **kwargs):
                    self.assertNotEqual(main_thread, threading.get_ident())
                    loading.set()
                    self.assertTrue(release.wait(3), 'main thread did not service close during loading')
                    return self.inputs

                def request_cancel(work):
                    result = cancel(work)
                    if loading.is_set() and not release.is_set():
                        accepted.append(result)
                    return result

                def paint():
                    flip()
                    if loading.is_set() and not release.is_set():
                        self.assertEqual(main_thread, threading.get_ident())
                        frames.append(True)
                        if len(frames) == 1:
                            pygame.event.post(pygame.event.Event(pygame.QUIT))
                        elif len(frames) == 2:
                            release.set()

                event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e, mod=0)
                with patch.dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy'), \
                     patch('pygame.event.get', return_value=[event]), \
                     patch('mecha_game.app._EraBench', return_value=bench), \
                     patch('mecha_game.app.load_campaign_inputs', side_effect=load), \
                     patch.object(api.EraWork, 'cancel', request_cancel), \
                     patch('pygame.display.flip', paint):
                    self.assertEqual(0, run(['--keeper-dir', str(path), '--scale', '1', '--fps', '0', '--tick-frames', '1']))
                self.assertEqual([True], accepted)
                self.assertEqual(2, len(frames))
                self.assertEqual(before, saved(path))
                self.assertIsNone(bench._completed_work)
                self.assertFalse(any(t.name == 'mechagotchi-era' for t in threading.enumerate()))
