"""X4 actual native app entry and preserved-save integration."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for folder in ('game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT / folder))
import pygame
from mecha_game.app import run
from mecha_game.packets import default_fixture_paths
from mecha_game.session import CompanionSession, load_session_inputs


def inventory(home):
    return {p.relative_to(home).as_posix(): p.read_bytes() for p in home.rglob('*') if p.is_file()}


class NativeEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_session_inputs(*default_fixture_paths())

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / 'keeper'
        self.env = patch.dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy')
        self.env.start(); self.addCleanup(self.env.stop)

    def seed(self, policy='incumbent'):
        grid, profile, model = self.inputs
        pet = CompanionSession(grid, profile, model=model, learning_policy=policy)
        pet.save(self.home / 'companion.json')
        return pet

    def invoke(self, extra, events=None):
        with patch('pygame.event.get', side_effect=events or (lambda: [])):
            return run(['--keeper-dir', str(self.home), '--fps', '0', '--scale', '2', *extra])

    def test_valid_saved_companion_does_not_resolve_unrelated_default_assets(self):
        for policy in ('incumbent', 'qtable'):
            with self.subTest(policy=policy):
                self.home = self.root / policy
                original = self.seed(policy)
                with patch('mecha_game.app.default_fixture_paths', side_effect=FileNotFoundError('unavailable defaults')):
                    self.assertEqual(0, self.invoke(['--ticks', '1', '--tick-frames', '1']))
                loaded = CompanionSession.load(self.home / 'companion.json')
                self.assertEqual(original.keeper_id, loaded.keeper_id)
                self.assertEqual(policy, loaded.learning_policy)
                self.assertEqual(original.grid, loaded.grid)

    def test_windowed_bad_primary_cancel_has_a_real_window_and_changes_no_save(self):
        self.seed()
        (self.home / 'companion.json').write_bytes(b'malformed owner save')
        before = inventory(self.home)
        info = self.root / 'cancel.json'
        with patch('pygame.display.set_mode', wraps=pygame.display.set_mode) as shown:
            self.assertEqual(0, self.invoke(['--startup', '--frames', '2', '--launch-info', str(info)],
                             events=lambda: [pygame.event.Event(pygame.QUIT)]))
        self.assertTrue(shown.called, 'an invalid companion must not prevent the entry window')
        self.assertEqual(before, inventory(self.home))
        receipt = json.loads(info.read_text(encoding='utf-8'))
        self.assertEqual('cancelled', receipt['startup_outcome'])
        self.assertTrue(receipt['stopped'])
        self.assertEqual('invalid', receipt['startup']['primary_status'])
        self.assertFalse(receipt['startup']['entered_play'])

    def test_valid_startup_cancel_does_not_export_or_checkpoint(self):
        self.seed('qtable')
        before = inventory(self.home)
        with patch('mecha_game.app.default_fixture_paths', side_effect=AssertionError('inspection cannot resolve defaults')):
            self.assertEqual(0, self.invoke(['--startup', '--frames', '2'],
                             events=lambda: [pygame.event.Event(pygame.QUIT)]))
        self.assertEqual(before, inventory(self.home))
        self.assertFalse((self.home / 'lineage.json').exists())

    def test_process_surface_prepares_actual_weather_and_reads_saved_report(self):
        self.assertEqual(0, self.invoke(['--prepare-weather', 'storm', '--eras', '1',
                          '--era-scale', 'tiny', '--ticks', '1', '--tick-frames', '1']))
        before = inventory(self.home)
        info = self.root / 'review.json'
        self.assertEqual(0, self.invoke(['--view', 'review', '--frames', '2', '--launch-info', str(info)]))
        receipt = json.loads(info.read_text(encoding='utf-8'))
        self.assertEqual('ready', receipt['startup_outcome'])
        self.assertEqual('review', receipt['view'])
        self.assertEqual('storm', receipt['review']['weather']['forecast'])
        self.assertTrue(receipt['review']['lines'])
        self.assertEqual(1, receipt['review']['era_count'])
        self.assertTrue(receipt['stopped'])
        self.assertEqual(before, inventory(self.home))


if __name__ == '__main__':
    unittest.main()
