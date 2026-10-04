"""Q3: adopted defaults, campaign authorship and existing-save continuity."""
import copy
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for directory in ('game/src', 'packages/mecha_engine/src', 'game'):
    sys.path.insert(0, str(ROOT/directory))
from mecha_game.app import _EraBench, run
from mecha_game.campaign import default_campaign_paths, load_campaign_inputs
from mecha_game.packets import default_fixture_paths, HELLO_SLIP
from mecha_game.session import CompanionSession, load_session_inputs
from build_release import BUNDLED_DATA


class DefaultCovenantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_campaign_inputs(ROOT/'data/seed_grids_16x16', ROOT/HELLO_SLIP,
            ROOT/'data/readability_benchmark/adopted_readability_model.json', repair_epochs=6, seed_limit=12)

    def test_product_and_campaign_defaults_are_the_adopted_v2_covenant(self):
        seed, slip = default_fixture_paths(ROOT)
        self.assertEqual('slip_v2_cleanliness.json', slip.name)
        self.assertEqual(slip, default_campaign_paths(ROOT)['slip_path'])
        grid, profile, model = load_session_inputs(seed, slip)
        self.assertIn('cleanliness', CompanionSession(grid, profile, model=model).state)
        self.assertEqual('slip_lcd_seed.json', HELLO_SLIP.name)

    def test_release_bundles_both_current_and_incumbent_covenants(self):
        sources = {source for source, _ in BUNDLED_DATA}
        self.assertIn('data/slips/valid/slip_v2_cleanliness.json', sources)
        self.assertIn(HELLO_SLIP.as_posix(), sources)

    def test_new_bench_uses_companion_covenant_without_mutating_inputs(self):
        profile = copy.deepcopy(self.inputs['slip_profile'])
        profile.update(slip_version='0.2.0', profile_id='keeper_custom', mechanics={'cleanliness': True})
        before = copy.deepcopy(self.inputs)
        with patch('mecha_game.app.load_campaign_inputs', return_value=self.inputs):
            bench = _EraBench('tiny', initial_profile=profile)
            self.assertEqual(profile, bench.active_covenant())
        self.assertEqual(before, self.inputs)
        profile['name'] = 'caller mutation'
        self.assertNotEqual(profile['name'], bench.active_covenant()['name'])

    def test_resumed_bench_keeps_recorded_covenant_over_new_starting_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            state, ledger = Path(directory)/'campaign.json', Path(directory)/'ledger.sqlite3'
            with patch('mecha_game.app.load_campaign_inputs', return_value=self.inputs):
                first = _EraBench('tiny', state_path=state, ledger_path=ledger, initial_profile=self.inputs['slip_profile'])
                first.run_era(ledger)
                candidate = dict(self.inputs['slip_profile'], slip_version='0.2.0', mechanics={'cleanliness': True})
                resumed = _EraBench('tiny', state_path=state, ledger_path=ledger, initial_profile=candidate)
                self.assertEqual(first.active_covenant(), resumed.active_covenant())

    @unittest.skipUnless(importlib.util.find_spec('pygame'), 'game group required')
    def test_new_default_window_cleans_and_resumes_while_old_save_stays_off(self):
        import pygame
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {'SDL_VIDEODRIVER': 'dummy'}):
            events = iter([[], [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_g)]])
            args = ['--keeper-dir', directory, '--ticks', '2', '--tick-frames', '1', '--fps', '0']
            with patch('pygame.event.get', side_effect=lambda: next(events, [])):
                self.assertEqual(0, run(args))
            path = Path(directory)/'companion.json'
            saved = json.loads(path.read_text())
            self.assertEqual(1, saved['state']['action_counts'].get('clean', 0))
            with patch('pygame.event.get', return_value=[]):
                self.assertEqual(0, run(args))
            self.assertEqual(4, json.loads(path.read_text())['state']['age_ticks'])
            seed, _ = default_fixture_paths(ROOT)
            grid, profile, model = load_session_inputs(seed, ROOT/HELLO_SLIP)
            CompanionSession(grid, profile, model=model).save(path)
            with patch('pygame.event.get', return_value=[]):
                self.assertEqual(0, run(args))
            self.assertNotIn('cleanliness', json.loads(path.read_text())['state'])

    def test_explicit_covenant_cannot_silently_resume_another_save(self):
        with tempfile.TemporaryDirectory() as directory:
            seed, _ = default_fixture_paths(ROOT)
            grid, profile, model = load_session_inputs(seed, ROOT/HELLO_SLIP)
            path = Path(directory)/'companion.json'
            CompanionSession(grid, profile, model=model).save(path)
            before = path.read_bytes()
            with self.assertRaises(SystemExit) as error:
                run(['--slip', str(ROOT/'data/slips/valid/slip_v2_cleanliness.json'), '--keeper-dir', directory, '--ticks', '1'])
            self.assertEqual(2, error.exception.code)
            self.assertEqual(before, path.read_bytes())

    @unittest.skipUnless(importlib.util.find_spec('pygame'), 'game group required')
    def test_default_window_keeps_complete_campaign_notice_visible_in_both_modes(self):
        import pygame
        notice = 'campaign covenant retained'
        original_init, original_font = _EraBench.__init__, pygame.font.Font

        def initialize(bench, *args, **kwargs):
            original_init(bench, *args, **kwargs)
            bench.message = notice

        for covenant in (False, True):
            with self.subTest(covenant=covenant), tempfile.TemporaryDirectory() as directory:
                expected, frames = [], []

                class FontProbe:
                    def __init__(self, *args, **kwargs):
                        self.font = original_font(*args, **kwargs)

                    def __getattr__(self, name):
                        return getattr(self.font, name)

                    def render(self, text, *args, **kwargs):
                        rendered = self.font.render(text, *args, **kwargs)
                        if text == notice:
                            target = pygame.Surface(rendered.get_size())
                            target.fill((16, 18, 16))
                            target.blit(rendered, (0, 0))
                            expected.append((target.get_size(), pygame.image.tobytes(target, 'RGB')))
                        return rendered

                events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_c)] if covenant else []
                with patch.dict(os.environ, {'SDL_VIDEODRIVER': 'dummy'}), patch.object(_EraBench, '__init__', initialize), \
                     patch.object(_EraBench, 'budget_lines', return_value=['COVENANT budget', '1 palette  2 thinking  C close']), \
                     patch('pygame.font.Font', FontProbe), patch('pygame.event.get', return_value=events), \
                     patch('pygame.display.flip', side_effect=lambda: frames.append(pygame.display.get_surface().copy())):
                    self.assertEqual(0, run(['--new', '--keeper-dir', directory, '--ticks', '1', '--tick-frames', '1', '--fps', '0']))
                self.assertTrue(expected)
                (width, height), pixels = expected[-1]
                window = frames[-1]
                self.assertTrue(any(pygame.image.tobytes(window.subsurface((8, y, width, height)), 'RGB') == pixels
                                    for y in range(window.get_height() - height + 1)), 'Campaign notice is clipped by the real window.')
