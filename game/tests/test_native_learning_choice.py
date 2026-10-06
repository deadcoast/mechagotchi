"""Prospective X7 new-life choice; source events, not OS keyboard evidence."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'game/src'))
sys.path.insert(0,str(ROOT/'packages/mecha_engine/src'))
import pygame
from mecha_game.native_ui import StartupView
from test_native_ui import inspection, key

class NewLearningChoiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env=patch.dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
        cls.env.start(); pygame.init(); cls.font=pygame.font.Font(None,22)
    @classmethod
    def tearDownClass(cls):
        pygame.quit(); cls.env.stop()
    def view(self, policy='qtable'):
        view=StartupView(inspection(primary='missing',backup='missing'),new_learning_policy=policy)
        view._transition('new')
        return view
    def activate(self, view, action, width=640):
        view.draw(pygame.Surface((width,620)),self.font)
        view.strip.focus(action)
        view.draw(pygame.Surface((width,620)),self.font)
        view.handle(key(pygame.K_RETURN,up=True))
        return view.handle(key(pygame.K_RETURN))
    def test_untouched_confirmation_preserves_omitted_choice(self):
        view=self.view()
        self.assertIsNone(self.activate(view,'confirm_new').learning_policy)
        self.assertIn('Q-table',' '.join(view.lines))
        self.assertIn('within this life',' '.join(view.lines))
    def test_terminal_free_incumbent_opt_out_is_explicit_and_keyboard_reachable(self):
        for width in (384,640,1024):
            with self.subTest(width=width):
                view=self.view()
                self.assertIsNone(self.activate(view,'new_policy',width).action)
                result=self.activate(view,'confirm_new',width)
                self.assertEqual('incumbent',result.learning_policy)
                self.assertEqual('confirm_new',result.action)
                self.assertEqual(view.inspection.revision,result.inspection_revision)
    def test_toggle_to_qtable_and_cancel_does_not_change_next_new_default(self):
        view=self.view('incumbent')
        self.activate(view,'new_policy')
        self.assertEqual('qtable',self.activate(view,'confirm_new').learning_policy)
        self.activate(view,'cancel')
        self.activate(view,'new')
        self.assertIsNone(self.activate(view,'confirm_new').learning_policy)
        self.assertIn('incumbent',' '.join(view.lines))
    def test_inspection_reset_drops_explicit_choice(self):
        view=self.view(); self.activate(view,'new_policy')
        view.set_inspection(inspection(primary='valid'),new_learning_policy='incumbent')
        self.activate(view,'new')
        self.assertIsNone(self.activate(view,'confirm_new').learning_policy)
        self.assertIn('incumbent',' '.join(view.lines))
    def test_product_parser_keeps_saved_policy_sentinel_and_explicit_care_v2(self):
        from mecha_game.app import build_parser
        parser=build_parser()
        self.assertIsNone(parser.parse_args([]).learning_policy)
        self.assertIn('built-in',parser.format_help())
        self.assertEqual('observed_care_selection_v2',parser.parse_args(
            ['--care-selection','observed_care_selection_v2']).care_selection)
    def test_qtable_display_identifies_per_life_learning(self):
        from test_learning_policy import companion
        from mecha_game.app import _footer_lines
        self.assertIn('within this life',' '.join(_footer_lines(companion(learning_policy='qtable').snapshot(),None)))
    def test_invalid_policy_refused(self):
        with self.assertRaises(ValueError): self.view('invented')

if __name__=='__main__': unittest.main()
