import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'game/src'))
sys.path.insert(0, str(ROOT/'packages/mecha_engine/src'))
import pygame
from mecha_game.footer import FooterPager, wrap_lines, HELP_LINES
from mecha_game.app import run

class FooterLayoutTests(unittest.TestCase):
    def setUp(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.font.init()
        self.font = pygame.font.Font(None, 22)

    def tearDown(self):
        pygame.quit()

    def test_font_wrapping_preserves_controls_and_long_unbroken_names(self):
        text = 'X export covenant  I import covenant  K import pack ' + 'founder_'*30
        wrapped = wrap_lines([text], lambda s: self.font.size(s)[0], 368)
        self.assertEqual(text.replace(' ', ''), ''.join(wrapped).replace(' ', ''))
        self.assertTrue(all(self.font.size(s)[0] <= 368 for s in wrapped))
        self.assertIn('K import pack', ' '.join(wrapped))

    def test_paging_reaches_every_help_line_and_clamps_at_both_ends(self):
        pager = FooterPager()
        expected = wrap_lines(HELP_LINES, lambda s: self.font.size(s)[0], 368)
        actual = []
        first = pager.layout(HELP_LINES, lambda s: self.font.size(s)[0], 368, 8)
        self.assertGreater(first.page_count, 1)
        for index in range(first.page_count):
            page = pager.layout(HELP_LINES, lambda s: self.font.size(s)[0], 368, 8)
            self.assertEqual(index, page.page)
            self.assertTrue(all(self.font.size(s)[0] <= 368 for s in page.lines))
            self.assertLessEqual(len(page.lines), 8)
            actual.extend(page.lines[:-1])
            pager.move(1)
        self.assertEqual(expected, actual)
        self.assertEqual(first.page_count-1, pager.page)
        pager.move(-999)
        self.assertEqual(0, pager.page)
        pager.move(999)
        self.assertEqual(first.page_count-1, pager.page)
        pager.reset()
        self.assertEqual(0, pager.page)

    def test_help_pauses_care_and_escape_resumes_the_same_saved_life(self):
        frames=[]
        events=iter([[pygame.event.Event(pygame.KEYDOWN,key=pygame.K_F1)],
                     [pygame.event.Event(pygame.KEYDOWN,key=pygame.K_f)],
                     [pygame.event.Event(pygame.KEYDOWN,key=pygame.K_PAGEDOWN)],
                     [pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE)], []])
        def get_events():
            return next(events,[pygame.event.Event(pygame.QUIT)])
        with tempfile.TemporaryDirectory() as directory, patch('pygame.event.get',side_effect=get_events), patch('pygame.display.flip',side_effect=lambda:frames.append(pygame.display.get_surface().copy())):
            self.assertEqual(0,run(['--new','--keeper-dir',directory,'--ticks','2','--tick-frames','1','--fps','0']))
            saved=json.loads((Path(directory)/'companion.json').read_text())
        self.assertEqual(1,saved['state']['age_ticks'])  # Only the frame after closing advances.
        self.assertNotEqual(pygame.image.tobytes(frames[1],'RGB'),pygame.image.tobytes(frames[2],'RGB'))
        self.assertEqual(0,saved['state']['action_counts'].get('feed',0))

    def test_small_lcd_scale_still_has_readable_casing(self):
        sizes=[]
        with tempfile.TemporaryDirectory() as directory,patch('pygame.event.get',return_value=[]),patch('pygame.display.flip',side_effect=lambda:sizes.append(pygame.display.get_surface().get_size())):
            self.assertEqual(0,run(['--new','--keeper-dir',directory,'--scale','2','--ticks','1','--tick-frames','1','--fps','0']))
        self.assertGreaterEqual(sizes[-1][0],384)

    def test_real_pixels_keep_long_notices_and_covenant_help_inside_the_casing(self):
        from mecha_game.app import _EraBench
        original_init,original_font=_EraBench.__init__,pygame.font.Font
        def initialize(bench,*args,**kwargs):
            original_init(bench,*args,**kwargs)
            bench.message='covenant retained '+('long_founder_id_'*20)
        for mode in ('play','covenant','help'):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as directory:
                renders=[]
                checked=[]
                class FontProbe:
                    def __init__(self,*args,**kwargs): self.font=original_font(*args,**kwargs)
                    def __getattr__(self,name): return getattr(self.font,name)
                    def render(self,text,*args,**kwargs):
                        rendered=self.font.render(text,*args,**kwargs)
                        target=pygame.Surface(rendered.get_size())
                        target.fill((16,18,16)); target.blit(rendered,(0,0))
                        renders.append((text,target))
                        return rendered
                def capture():
                    window=pygame.display.get_surface()
                    for text,target in renders:
                        w,h=target.get_size()
                        self.assertLessEqual(w,window.get_width()-16,text)
                        pixels=pygame.image.tobytes(target,'RGB')
                        self.assertTrue(any(pygame.image.tobytes(window.subsurface((8,y,w,h)),'RGB')==pixels
                                            for y in range(window.get_height()-h+1)),text)
                        checked.append(text)
                    renders.clear()
                opening=[] if mode=='play' else [pygame.event.Event(pygame.KEYDOWN,key=pygame.K_c if mode=='covenant' else pygame.K_F1)]
                events=iter([opening,[pygame.event.Event(pygame.KEYDOWN,key=pygame.K_PAGEDOWN)],
                             [pygame.event.Event(pygame.MOUSEWHEEL,y=-1)],
                             [pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE)] if mode=='help' else []])
                with patch.object(_EraBench,'__init__',initialize),patch.object(_EraBench,'budget_lines',return_value=['COVENANT palettes 123456/234567 thinking 123456/234567 population 123456 generations 234567', '1 palette 2 thinking 3 population 4 generations C close']),patch('pygame.font.Font',FontProbe),patch('pygame.event.get',side_effect=lambda:next(events,[])),patch('pygame.display.flip',side_effect=capture):
                    self.assertEqual(0,run(['--new','--keeper-dir',directory,'--ticks','4','--tick-frames','1','--fps','0']))
                self.assertTrue(checked)
                self.assertTrue(any('PgUp/PgDn' in text for text in checked))
