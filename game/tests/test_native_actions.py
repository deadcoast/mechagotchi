"""X4 actual app action/resize events, separate from native OS input evidence."""
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
for folder in ('game/src','packages/mecha_engine/src'):
    sys.path.insert(0,str(ROOT/folder))
import pygame
from mecha_game.app import run, default_keeper_dir
from mecha_game.native_ui import ActionStrip, fit_native_layout
from mecha_game.packets import default_fixture_paths
from mecha_game.session import CompanionSession, load_session_inputs


def key(code,up=False,mod=0):
    return pygame.event.Event(pygame.KEYUP if up else pygame.KEYDOWN,key=code,mod=mod)


class NativeActionApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs=load_session_inputs(*default_fixture_paths())

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.home=Path(self.temp.name)/'keeper'
        grid,profile,model=self.inputs
        self.pet=CompanionSession(grid,profile,model=model)
        self.pet.save_checkpoint(self.home/'companion.json')
        self.env=patch.dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
        self.env.start();self.addCleanup(self.env.stop)
        self.draws=[];self.strips=[];self.frames=[]

    def invoke(self,batches,extra=()):
        rows=iter(batches)
        original=ActionStrip.draw
        def draw(strip,surface,font,rect):
            result=original(strip,surface,font,rect)
            self.strips.append(strip)
            self.draws.append({'ids':[a.id for a in strip.actions], 'rects':dict(strip.button_rects),
                               'size':surface.get_size(),'rect':pygame.Rect(rect),'focus':strip.focus_active})
            return result
        def events():
            batch=next(rows,[pygame.event.Event(pygame.QUIT)])
            return batch() if callable(batch) else batch
        def paint():
            self.frames.append(pygame.display.get_surface().copy())
            if hasattr(self, 'on_frame'):
                self.on_frame()
        with patch('pygame.event.get',side_effect=events),patch.object(ActionStrip,'draw',draw), \
             patch('pygame.display.flip',side_effect=paint):
            result=run(['--keeper-dir',str(self.home),'--scale','2','--tick-frames','1','--fps','0',*extra])
        self.assertEqual(0,result)
        return CompanionSession.load(self.home/'companion.json')

    def select(self,action):
        self.assertTrue(self.strips,'Actual app must draw a visible native action strip')
        strip=self.strips[-1]
        self.assertIn(action,[a.id for a in strip.actions])
        enabled=[a.id for a in strip.actions if a.enabled]
        self.assertIn(action,enabled)
        # Actual app receives keyboard events; the fixture never changes focus.
        return [key(pygame.K_F6),key(pygame.K_HOME),
                *[key(pygame.K_RIGHT) for _ in range(enabled.index(action))]]

    def click(self,action):
        self.assertTrue(self.draws,'Actual app must draw a visible native action strip')
        pos=self.draws[-1]['rects'][action].center
        return [pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=pos),
                pygame.event.Event(pygame.MOUSEBUTTONUP,button=1,pos=pos)]

    def test_keyboard_navigation_and_its_closing_frame_pause_care(self):
        loaded=self.invoke([[key(pygame.K_F6)],[],[key(pygame.K_ESCAPE),key(pygame.K_f)],[]])
        self.assertEqual(1,loaded.state['age_ticks'])
        self.assertEqual(0,loaded.state['action_counts'].get('feed',0))
        self.assertTrue(self.draws)
        self.assertFalse(self.strips[-1].allow_tab)

    def test_mouse_feed_uses_existing_care_once_on_following_frame(self):
        loaded=self.invoke([[],lambda:self.click('feed'),[]])
        self.assertEqual(1,loaded.state['action_counts'].get('feed',0))
        self.assertEqual(2,loaded.state['age_ticks'])
        self.assertFalse(self.strips[-1].focus_active)

    def test_contextual_help_back_and_inbox_actions_use_existing_views(self):
        self.invoke([[],lambda:self.select('help'),[key(pygame.K_RETURN)],
            [key(pygame.K_RETURN,up=True)],lambda:self.select('back'),[key(pygame.K_RETURN)],
            [key(pygame.K_RETURN,up=True)],lambda:self.select('pack_inbox'),[key(pygame.K_RETURN)],
            [key(pygame.K_RETURN,up=True)]])
        contexts=[row['ids'] for row in self.draws]
        self.assertTrue(any('back' in ids and 'next_page' in ids for ids in contexts))
        self.assertTrue(any('import_selected' in ids and 'refresh' in ids for ids in contexts))

    def test_resize_reflows_actual_pixels_and_controls_inside_window(self):
        modes=[];original=pygame.display.set_mode
        def mode(size,flags=0,*args,**kwargs):
            modes.append((size,flags));return original(size,flags,*args,**kwargs)
        with patch('pygame.display.set_mode',side_effect=mode):
            self.invoke([[key(pygame.K_F6)],
                [pygame.event.Event(pygame.VIDEORESIZE,w=384,h=480,size=(384,480))],
                [pygame.event.Event(pygame.VIDEORESIZE,w=1024,h=768,size=(1024,768))]])
        self.assertTrue(modes[0][1]&pygame.RESIZABLE)
        self.assertIn((384,480),[row['size'] for row in self.draws])
        self.assertIn((1024,768),[row['size'] for row in self.draws])
        for row in self.draws:
            bounds=pygame.Rect((0,0),row['size'])
            self.assertTrue(bounds.contains(row['rect']))
            self.assertTrue(all(bounds.contains(rect) for rect in row['rects'].values()))

    def test_era_worker_resize_and_mouse_cancel_stay_responsive_and_join(self):
        before=(self.home/'companion.json').read_bytes()
        observed=[]
        def operation(bench,ledger,*,work=None):
            work.phase('Blocked source fixture')
            work.cancel_requested.wait(3)
            work.phase('Checking cancellation')
            raise AssertionError('Visible cancel was not routed to worker')
        def paint():
            if len(self.frames)==1:
                from mecha_game.rasterize import compose_frame
                from mecha_game.app import _frame_bytes
                layout=fit_native_layout(self.frames[-1].get_size(),(16,22),pygame.font.Font(None,22).get_height(),preferred_scale=2)
                expected=compose_frame(self.pet.packet_for(self.pet.desired_clip(),0),previous_ghost=None,cell_px=2).pixels
                body=self.frames[-1].subsurface((layout.lcd_rect.x,layout.lcd_rect.y,32,32))
                self.assertEqual(_frame_bytes(expected),pygame.image.tobytes(body,'RGB'),
                                 'Held creature pixels remain exact at the actual LCD rectangle')
                pygame.event.post(pygame.event.Event(pygame.VIDEORESIZE,w=384,h=480,size=(384,480)))
            elif len(self.frames)==2:
                rows=[row for row in self.draws if 'cancel_work' in row['rects']]
                if rows:
                    observed.append(rows[-1])
                    pos=rows[-1]['rects']['cancel_work'].center
                    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=pos))
                    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP,button=1,pos=pos))
                else:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
        self.on_frame=paint
        with patch('mecha_game.app._EraBench.run_era',operation):
            self.invoke([[key(pygame.K_e)]])
        self.assertTrue(observed,'Era worker must render the actual visible cancel control')
        self.assertEqual((384,480),observed[-1]['size'])
        self.assertEqual(before,(self.home/'companion.json').read_bytes())
        self.assertFalse(any(t.name=='mechagotchi-era' for t in threading.enumerate()))

    def test_bounded_frame_save_failure_exits_once_without_touching_primary(self):
        before=(self.home/'companion.json').read_bytes()
        polls=[]
        def events():
            polls.append(True)
            if len(polls)>3:
                raise AssertionError('Bounded --frames continued after failed final save')
            return []
        with patch('pygame.event.get',side_effect=events), \
                patch.object(CompanionSession,'save_checkpoint',side_effect=PermissionError('injected write refusal')) as save:
            result=run(['--keeper-dir',str(self.home),'--scale','2','--frames','1','--fps','0'])
        self.assertEqual(1,result)
        self.assertEqual(1,save.call_count)
        self.assertEqual(1,len(polls))
        self.assertEqual(before,(self.home/'companion.json').read_bytes())

    def test_old_weather_button_cannot_spend_after_raw_covenant_key_in_same_batch(self):
        def stale_click():
            return [key(pygame.K_c),*self.click('weather_stable_soup')]
        with patch('mecha_game.app._EraBench.spend') as spend, \
                patch('mecha_game.app._EraBench.budget_lines',return_value=['COVENANT source fixture']):
            self.invoke([[],lambda:self.select('weather_stable_soup'),[key(pygame.K_ESCAPE)],stale_click])
        spend.assert_not_called()

    def test_existing_raw_covenant_shortcut_sequence_keeps_its_meaning(self):
        with patch('mecha_game.app._EraBench.spend') as spend, \
                patch('mecha_game.app._EraBench.budget_lines',return_value=['COVENANT source fixture']):
            self.invoke([[key(pygame.K_c),key(pygame.K_2)]])
        spend.assert_called_once_with(1)

    def test_enter_release_inside_worker_reaches_parent_navigation_on_return(self):
        posted=[]
        def operation(bench,ledger,*,work=None):
            work.phase('Waiting for source UI cancel')
            work.cancel_requested.wait(3)
            work.phase('Cancelled')
            raise AssertionError('Source worker did not receive cancel')
        def paint():
            if not posted and self.draws and 'cancel_work' in self.draws[-1]['ids']:
                posted.append(True)
                pygame.event.post(key(pygame.K_RETURN,up=True))
                pygame.event.post(key(pygame.K_ESCAPE))
        self.on_frame=paint
        with patch('mecha_game.app._EraBench.run_era',operation):
            self.invoke([[key(pygame.K_F6)],lambda:self.select('run_era'),[key(pygame.K_RETURN)],
                         lambda:self.select('help'),[key(pygame.K_RETURN)],[key(pygame.K_RETURN,up=True)]])
        self.assertTrue(posted)
        self.assertTrue(any(row['ids']==['back','previous_page','next_page'] for row in self.draws),
                        'First released Enter after worker return must open the selected help action')

    def test_explicit_source_identity_does_not_borrow_external_ancestor(self):
        outside=Path(self.temp.name)/'fake_checkout'
        (outside/'data/seed_grids_16x16').mkdir(parents=True)
        with patch.object(Path,'home',return_value=Path(self.temp.name)/'user'):
            self.assertEqual(Path(self.temp.name)/'user/.mechagotchi',default_keeper_dir(outside/'app.py'))


if __name__=='__main__':unittest.main()
