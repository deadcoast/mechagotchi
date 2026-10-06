"""Connected X4 journey through drawn native controls, not OS-input automation.

The robot observes rendered ActionStrip controls and injects SDL key/mouse events.
It never calls an app handler or replaces engine/campaign/adoption operations.
"""
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
for folder in ('game/src','packages/mecha_engine/src'):
    sys.path.insert(0,str(ROOT/folder))
import pygame
from mecha_game.app import run
from mecha_game.era_review import EraReview
from mecha_game.footer import FooterPager
from mecha_game.native_ui import ActionStrip
from mecha_game.packets import default_fixture_paths
from mecha_game.repertoire import RepertoireBrowser
from mecha_game.session import CompanionSession, load_session_inputs


def key(code, *, up=False):
    return pygame.event.Event(pygame.KEYUP if up else pygame.KEYDOWN,key=code,mod=0,repeat=False)


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


class NativeConnectedJourneyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs=load_session_inputs(*default_fixture_paths())

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='mecha-native-journey-')
        self.addCleanup(self.temp.cleanup)
        self.home=Path(self.temp.name)/'selected-keeper'
        self.env=patch.dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
        self.env.start();self.addCleanup(self.env.stop)
        self.evidence={}
        self.images={}

    def drive(self, steps, *, startup=False):
        drawn={}
        records=[]
        footer_lines=[]
        contexts=[]
        frame_count=0
        current=0
        phase='navigate'
        deadline=time.monotonic()+90
        original_draw=ActionStrip.draw
        original_footer=FooterPager.layout
        def draw(strip,surface,font,rect):
            result=original_draw(strip,surface,font,rect)
            drawn.clear()
            drawn.update(actions=tuple(strip.actions),rects=dict(strip.button_rects),
                         focused=strip.focused_id,size=surface.get_size())
            return result
        def footer(pager,lines,*args,**kwargs):
            footer_lines[:] = list(lines)
            return original_footer(pager,lines,*args,**kwargs)
        def paint():
            nonlocal frame_count
            frame_count+=1
            self.assertLess(time.monotonic(),deadline,'Bounded native journey exceeded 90 seconds')
            ids=[a.id for a in drawn.get('actions',())]
            context=('startup' if 'resume' in ids else 'worker' if 'cancel_work' in ids else
                     'archive' if 'adopt' in ids else 'report' if 'previous_campaign' in ids else
                     'covenant' if 'palette' in ids else 'care')
            contexts.append(context)
            if getattr(self,'capture_images',False) and context not in self.images:
                self.images[context]=pygame.display.get_surface().copy()
        def events():
            nonlocal current,phase
            self.assertLess(time.monotonic(),deadline,'Bounded native journey exceeded 90 seconds')
            if not drawn:
                return [key(pygame.K_F6)]
            self.assertLess(current,len(steps),'App did not stop after visible Save and quit')
            action_id,method=steps[current]
            if phase=='release':
                phase='navigate'
                # Release the previous activation and enter navigation before a
                # fresh care frame. This is actual input, not direct focus mutation.
                return [key(pygame.K_RETURN,up=True),key(pygame.K_F6)]
            enabled=[a.id for a in drawn['actions'] if a.enabled]
            self.assertIn(action_id,enabled,f'{action_id} unavailable in drawn controls: {enabled}')
            if phase=='navigate':
                phase='activate'
                return [key(pygame.K_F6),key(pygame.K_HOME),
                        *[key(pygame.K_RIGHT) for _ in range(enabled.index(action_id))]]
            self.assertIn(action_id,drawn['rects'],'Control must actually be visible before activation')
            self.assertEqual(action_id,drawn['focused'])
            if action_id=='adopt':
                selected=RepertoireBrowser.load(self.home).current()
                self.assertIsNotNone(selected)
                self.evidence['selected_archive_grid']=selected['grid']
            control=next(a for a in drawn['actions'] if a.id==action_id)
            records.append({'action':action_id,'label':control.label,'input':method,
                            'window':drawn['size'],'footer':list(footer_lines)})
            current+=1
            phase='release'
            if method=='mouse':
                pos=drawn['rects'][action_id].center
                return [pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=pos),
                        pygame.event.Event(pygame.MOUSEBUTTONUP,button=1,pos=pos)]
            return [key(pygame.K_RETURN)]
        args=['--keeper-dir',str(self.home),'--era-scale','tiny','--scale','2','--fps','0','--tick-frames','1']
        if startup:
            args.append('--startup')
        with patch('pygame.event.get',side_effect=events),patch.object(ActionStrip,'draw',draw), \
                patch.object(FooterPager,'layout',footer),patch('pygame.display.flip',side_effect=paint):
            self.assertEqual(0,run(args))
        self.assertEqual(len(steps),len(records))
        return {'actions':records,'frames':frame_count,'contexts':contexts}

    def test_visible_preparation_era_archive_adoption_quit_and_resume(self):
        grid,profile,model=self.inputs
        initial=CompanionSession(grid,profile,model=model,learning_policy='qtable')
        initial.save_checkpoint(self.home/'companion.json')
        steps=[('preparation','keyboard'),('back','mouse'),('weather_storm','keyboard'),
               ('stage_pet','mouse'),('run_era','keyboard'),('archive','mouse'),
               ('adopt','keyboard'),('quit','mouse')]
        first=self.drive(steps)
        self.assertIn('covenant',first['contexts'])
        self.assertIn('worker',first['contexts'])
        self.assertIn('report',first['contexts'])
        self.assertIn('archive',first['contexts'])
        report=EraReview.load(self.home)
        self.assertIsNone(report.error)
        self.assertEqual(1,len(report.history['eras']))
        self.assertEqual('storm',report.current['weather']['forecast'])
        self.assertIn(initial.grid['grid_id'],report.current['report']['founders']['admitted_ids'])
        selected=self.evidence.pop('selected_archive_grid')
        adopted=CompanionSession.load(self.home/'companion.json')
        self.assertEqual(selected,adopted.grid)
        self.assertEqual(initial.keeper_id,adopted.keeper_id)
        self.assertEqual('qtable',adopted.learning_policy)
        self.assertEqual(2,len(adopted.lineage))
        self.assertEqual('replaced_alive',adopted.lineage[0]['outcome'])
        self.assertEqual('era_elite',adopted.lineage[-1]['origin'])
        self.assertEqual({'campaign_id':report.history['campaign_id'],'era_index':0},adopted.lineage[-1]['source'])
        self.assertEqual(report.history['campaign_id'],adopted.campaign_id)
        identity=(adopted.keeper_id,adopted.lineage[-1]['life_id'],adopted.campaign_id,
                  adopted.learning_policy,adopted.grid,adopted.lineage)
        checkpoint={p.relative_to(self.home).as_posix():p.read_bytes() for p in self.home.rglob('*') if p.is_file()}
        restart=self.drive([('resume','keyboard'),('quit','mouse')],startup=True)
        resumed=CompanionSession.load(self.home/'companion.json')
        self.assertEqual(identity,(resumed.keeper_id,resumed.lineage[-1]['life_id'],resumed.campaign_id,
                                  resumed.learning_policy,resumed.grid,resumed.lineage))
        self.assertEqual(checkpoint,{p.relative_to(self.home).as_posix():p.read_bytes()
                                   for p in self.home.rglob('*') if p.is_file()},
                         'Navigation-only restart/quit must preserve all saved bytes')
        self.evidence.update(classification='Actual app source SDL events; dummy driver, no OS input claim',
            first=first,restart=restart,keeper_id=adopted.keeper_id,campaign_id=adopted.campaign_id,
            life_id=adopted.lineage[-1]['life_id'],policy=adopted.learning_policy,
            selected_grid_id=selected['grid_id'],selected_grid_digest=digest(selected),
            report_digest=digest(report.current),weather=report.current['weather']['forecast'],
            recorded_eras=len(report.history['eras']),recorded_lives=len(adopted.lineage),
            adoption_source=adopted.lineage[-1]['source'],restart_bytes_preserved=True,
            writes='Only the disposable TemporaryDirectory Keeper fixture')


if __name__=='__main__':
    unittest.main()
