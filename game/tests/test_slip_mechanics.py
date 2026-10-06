"""Covenant mechanics survive real game saves, resumption and succession."""
import hashlib
import importlib.util
import os
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT / 'packages/mecha_engine/src', ROOT / 'game/src', ROOT / 'labs/lifecycle_sim'):
    sys.path.insert(0, str(path))
from mecha_engine.generation import train_generation_model
from mecha_game.session import CompanionSession
from slip_mechanics_gate import legacy_game_save_projection, legacy_game_snapshot_projection


def read(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


class CovenantMechanicsTests(unittest.TestCase):
    def session(self, mechanics=None):
        grid = read('data/seed_grids/mg_seed_001.json')
        profile = dict(read('data/slips/valid/slip_lcd_seed.json'), slip_version='0.2.0', mechanics={'cleanliness': True})
        return CompanionSession(grid, profile, model=train_generation_model([grid]), mechanics=mechanics)

    def test_covenant_only_session_offers_readout_and_clean_action(self):
        session = self.session()
        self.assertIn('clean', session.snapshot()['actions'])
        self.assertIn('cleanliness', session.snapshot()['needs'])
        session.advance('play')
        before = session.state['cleanliness']
        session.advance('clean')
        self.assertGreater(session.state['cleanliness'], before)

    def test_save_resume_and_succession_preserve_inheritance_and_explicit_disable(self):
        for override, enabled in ((None, True), ((), False)):
            with self.subTest(override=override), tempfile.TemporaryDirectory() as directory:
                session = self.session(override)
                session.advance('feed')
                path = Path(directory) / 'session.json'
                session.save(path)
                payload = json.loads(path.read_text())
                if override == ():
                    self.assertEqual([], payload['mechanics'])
                else:
                    self.assertNotIn('mechanics', payload)
                resumed = CompanionSession.load(path)
                self.assertEqual(session.snapshot(), resumed.snapshot())
                for action in ('play', 'sleep', 'feed'):
                    self.assertEqual(session.advance(action), resumed.advance(action))
                for _ in range(500):
                    if not resumed.alive:
                        break
                    resumed.advance()
                self.assertFalse(resumed.alive)
                resumed.succeed()
                self.assertEqual(enabled, 'cleanliness' in resumed.state)
                self.assertEqual(enabled, 'clean' in resumed.snapshot()['actions'])

    def test_incumbent_profiles_preserve_game_snapshot_and_save_payload(self):
        baseline = read('data/lifecycle/slip_mechanics_incumbent_baseline.json')
        for row in baseline['observations']:
            with self.subTest(profile=row['profile_path']), tempfile.TemporaryDirectory() as directory:
                grid, profile = read(row['grid_path']), read(row['profile_path'])
                session = CompanionSession(grid, profile, model=train_generation_model([grid]))
                for action in baseline['game_actions']:
                    session.advance(action)
                self.assertEqual(row['game_snapshot_hash'], digest(legacy_game_snapshot_projection(session.snapshot())))
                path = Path(directory) / 'save.json'
                session.save(path)
                legacy = legacy_game_save_projection(json.loads(path.read_text()))
                self.assertEqual(row['game_save_hash'], digest(legacy))

    def test_explicit_empty_on_incumbent_profile_keeps_old_save_shape(self):
        grid = read('data/seed_grids/mg_seed_001.json')
        profile = read('data/slips/valid/slip_lcd_seed.json')
        model = train_generation_model([grid])
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory) / 'a.json', Path(directory) / 'b.json'
            CompanionSession(grid, profile, model=model).save(a)
            CompanionSession(grid, profile, model=model, mechanics=()).save(b)
            first, second = json.loads(a.read_text()), json.loads(b.read_text())
            self.assertNotEqual(first['chronicle']['keeper_id'], second['chronicle']['keeper_id'])
            self.assertNotEqual(first['lineage'][0]['life_id'], second['lineage'][0]['life_id'])
            self.assertEqual(legacy_game_save_projection(first), legacy_game_save_projection(second))
    def test_historical_projection_rejects_unregistered_metadata_and_false_care(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'session.json'
            self.session().save(path)
            original = json.loads(path.read_text())
            for mutate in (
                lambda payload: payload.update(unregistered=True),
                lambda payload: payload['lineage'][0].update(unregistered=True),
                lambda payload: payload['chronicle'].update(unregistered=True),
                lambda payload: payload['lineage'][0]['care_summary'].update(ticks_observed=1),
            ):
                payload = json.loads(json.dumps(original))
                mutate(payload)
                with self.subTest(mutate=mutate), self.assertRaises(ValueError):
                    legacy_game_save_projection(payload)

    def test_historical_projection_validates_x7_body_and_event_identities(self):
        session = self.session()
        session.advance('feed')
        snapshot = session.snapshot()
        for mutate in (lambda s: s.update(unregistered=True),
                       lambda s: s.update(life_id='invented'),
                       lambda s: s['log'][0].update(life_id='other-life')):
            corrupt = json.loads(json.dumps(snapshot))
            mutate(corrupt)
            with self.assertRaises(ValueError):
                legacy_game_snapshot_projection(corrupt)
        with tempfile.TemporaryDirectory() as directory:
            path = session.save(Path(directory) / 'session.json')
            payload = json.loads(path.read_text())
            for field in ('grid_sha256', 'grid_structure_sha256'):
                corrupt = json.loads(json.dumps(payload))
                corrupt['lineage'][0][field] = '0' * 64
                with self.assertRaises(ValueError):
                    legacy_game_save_projection(corrupt)

    def test_footer_exposes_engine_cleanliness_only_when_opted_in(self):
        from mecha_game.app import _footer_lines
        session = self.session()
        session.advance('play')
        footer = ' '.join(_footer_lines(session.snapshot(), None))
        self.assertIn(f"cleanliness {session.state['cleanliness']:.2f}", footer)
        self.assertIn('G clean', footer)
        off_footer = ' '.join(_footer_lines(self.session(()).snapshot(), None))
        self.assertNotIn('cleanliness', off_footer)
        self.assertNotIn('G clean', off_footer)

    @unittest.skipUnless(importlib.util.find_spec('pygame'), 'game dependency group not installed')
    def test_real_window_key_event_cleans_only_opted_in_companion(self):
        import pygame
        from mecha_game.app import run
        for filename, enabled in [('slip_v2_cleanliness.json', True), ('slip_lcd_seed.json', False)]:
            with self.subTest(profile=filename), tempfile.TemporaryDirectory() as directory:
                events = iter([[], [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_g)]])
                with patch.dict(os.environ, {'SDL_VIDEODRIVER': 'dummy'}), patch('pygame.event.get', side_effect=lambda: next(events, [])):
                    self.assertEqual(0, run(['--new', '--slip', str(ROOT/'data/slips/valid'/filename),
                                             '--keeper-dir', directory, '--ticks', '2', '--tick-frames', '1', '--fps', '0']))
                saved = json.loads((Path(directory)/'companion.json').read_text())
                self.assertEqual(int(enabled), saved['state']['action_counts'].get('clean', 0))


if __name__ == '__main__':
    unittest.main()
