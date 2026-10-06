"""Actual native entry source events and labeled I/O injection; no OS keyboard claim."""
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
from mecha_game.native_ui import StartupView
from mecha_game.session import CompanionSession, load_session_inputs


def inventory(home):
    return {p.relative_to(home).as_posix(): p.read_bytes() for p in home.rglob('*') if p.is_file()}


def key(code, *, up=False, repeat=False, mod=0):
    return pygame.event.Event(pygame.KEYUP if up else pygame.KEYDOWN, key=code, mod=mod, repeat=repeat)


def click(view, action):
    pos = view.button_rects[action].center
    return [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos),
            pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=pos)]


class NativeStartupErrorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_session_inputs(ROOT / 'data/seed_grids_16x16/mg_seed16_001_beetle.json',
                                        ROOT / 'data/slips/valid/slip_v2_cleanliness.json')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / 'selected keeper'
        self.frames = []
        self.receipt_index = 0
        self.env = patch.dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy')
        self.env.start(); self.addCleanup(self.env.stop)

    def seed_pair(self, policy='incumbent', *, bad_primary=False):
        grid, profile, model = self.inputs
        pet = CompanionSession(grid, profile, model=model, learning_policy=policy)
        path = self.home / 'companion.json'
        pet.save(path); pet.advance('feed'); pet.save(path)
        if bad_primary: path.write_bytes(b'malformed original primary')
        return pet

    def invoke(self, steps, *, extra=()):
        self.receipt_index += 1
        info = self.root / ('receipt-' + str(self.receipt_index) + '.json')
        iterator = iter(steps); current = {}; original = StartupView.draw
        def draw(view, surface, font):
            original(view, surface, font)
            current['view'] = view
            self.frames.append(dict(mode=view.mode, lines=list(view.lines), home=str(view.inspection.home),
                                    focused=view.focused_id, error=view.error))
            evidence = os.environ.get('MECHA_STARTUP_TEST_EVIDENCE')
            if evidence and (view.error or view.mode in ('backup', 'new', 'directory')):
                folder = Path(evidence); folder.mkdir(parents=True, exist_ok=True)
                name = f'{self._testMethodName}-{self.receipt_index}-{len(self.frames)}.png'
                pygame.image.save(surface, str(folder / name))
        def poll():
            step = next(iterator, None)
            return [pygame.event.Event(pygame.QUIT)] if step is None else step(current.get('view'))
        with patch.object(StartupView, 'draw', draw), patch('pygame.event.get', side_effect=poll):
            code = run(['--keeper-dir', str(self.home), '--startup', '--frames', '15',
                        '--fps', '0', '--scale', '1', '--launch-info', str(info), *extra])
        return code, json.loads(info.read_text(encoding='utf-8'))

    def test_source_missing_new_assets_stays_visible_and_preserves_all_existing_bytes(self):
        self.seed_pair('qtable', bad_primary=True); before = inventory(self.home)
        with patch('mecha_game.app.default_fixture_paths', side_effect=FileNotFoundError('injected missing new-life assets')), \
                patch.object(CompanionSession, 'advance', side_effect=AssertionError('care cannot start')):
            code, receipt = self.invoke([lambda v: click(v, 'new'), lambda v: click(v, 'confirm_new'), lambda v: []])
        self.assertEqual(0, code)
        self.assertFalse(receipt['startup']['entered_play'])
        self.assertTrue(any('missing new-life assets' in ' '.join(f['lines']) for f in self.frames))
        self.assertEqual(before, inventory(self.home))

    def test_injected_initial_checkpoint_denial_stays_in_entry_without_lost_prior_saves(self):
        for policy in ('incumbent', 'qtable'):
            with self.subTest(policy=policy):
                self.home = self.root / policy; self.seed_pair(policy)
                path = self.home / 'companion.json'; backup = path.with_suffix('.bak.json')
                primary_bytes, backup_bytes = path.read_bytes(), backup.read_bytes()
                original = os.replace
                def denied(source, destination):
                    if Path(destination) in (path, backup): raise PermissionError('injected selected-home save denial')
                    return original(source, destination)
                with patch('mecha_game.session.os.replace', denied), \
                        patch.object(CompanionSession, 'advance', side_effect=AssertionError('care cannot start')):
                    code, receipt = self.invoke([lambda v: click(v, 'new'), lambda v: click(v, 'confirm_new'), lambda v: []])
                self.assertEqual(0, code)
                self.assertFalse(receipt['startup']['entered_play'])
                self.assertTrue(any('selected-home save denial' in ' '.join(f['lines']) for f in self.frames))
                self.assertEqual(primary_bytes, path.read_bytes()); self.assertEqual(backup_bytes, backup.read_bytes())
                originals = {p.read_bytes() for p in self.home.glob('*.replaced-*.json')}
                self.assertTrue({primary_bytes, backup_bytes}.issubset(originals))

    def test_source_changed_backup_after_drawn_preview_refuses_before_any_archive(self):
        self.seed_pair('qtable', bad_primary=True)
        path = self.home / 'companion.json'; backup = path.with_suffix('.bak.json'); expected = {}
        def changed(view):
            self.assertEqual('backup', view.mode)
            backup.write_bytes(backup.read_bytes() + b' ')
            expected.update(inventory(self.home))
            return click(view, 'confirm_restore')
        with patch.object(CompanionSession, 'advance', side_effect=AssertionError('care cannot start')):
            code, receipt = self.invoke([lambda v: click(v, 'inspect_backup'), changed, lambda v: []])
        self.assertEqual(0, code)
        self.assertFalse(receipt['startup']['entered_play'])
        self.assertTrue(any('changed' in ' '.join(f['lines']) for f in self.frames))
        self.assertEqual(expected, inventory(self.home))
        self.assertFalse(list(self.home.glob('*.before-recovery-*.json')))

    def test_source_same_batch_and_held_enter_cannot_confirm_backup(self):
        for policy in ('incumbent', 'qtable'):
            with self.subTest(policy=policy):
                self.home = self.root / policy; self.seed_pair(policy, bad_primary=True)
                before = inventory(self.home)
                def open_and_try(view):
                    self.assertEqual('inspect_backup', view.focused_id)
                    return [key(pygame.K_RETURN), key(pygame.K_RIGHT), key(pygame.K_RETURN)]
                def held(view):
                    self.assertEqual('backup', view.mode)
                    self.assertEqual(before, inventory(self.home))
                    return [key(pygame.K_RETURN, repeat=True)]
                def still_held(view):
                    self.assertEqual(before, inventory(self.home))
                    return [key(pygame.K_RETURN)]
                def cancel(view):
                    self.assertEqual(before, inventory(self.home))
                    return [key(pygame.K_RETURN, up=True), key(pygame.K_ESCAPE)]
                with patch.object(CompanionSession, 'advance', side_effect=AssertionError('care cannot start')):
                    code, receipt = self.invoke([open_and_try, held, still_held, cancel])
                self.assertEqual(0, code)
                self.assertFalse(receipt['startup']['entered_play'])
                self.assertEqual(before, inventory(self.home))

    def test_source_cancelled_directory_text_keeps_original_selection_and_files(self):
        self.seed_pair('qtable'); before = inventory(self.home); other = self.root / 'unused new home'
        def type_and_cancel(view):
            self.assertEqual('directory', view.mode)
            return [key(pygame.K_a, mod=pygame.KMOD_CTRL), pygame.event.Event(pygame.TEXTINPUT, text=str(other)),
                    key(pygame.K_ESCAPE)]
        def inspect_original(view):
            self.assertEqual(self.home, view.inspection.home)
            self.assertEqual('home', view.mode)
            return []
        with patch('mecha_game.app.default_fixture_paths', side_effect=AssertionError('no assets on cancel')):
            code, receipt = self.invoke([lambda v: click(v, 'choose_directory'), type_and_cancel, inspect_original])
        self.assertEqual(0, code); self.assertFalse(receipt['startup']['entered_play'])
        self.assertEqual(str(self.home), receipt['keeper_dir'])
        self.assertEqual(before, inventory(self.home)); self.assertFalse(other.exists())

    def test_source_deliberate_backup_confirmation_preserves_both_saved_policies_and_old_primary(self):
        for policy in ('incumbent', 'qtable'):
            with self.subTest(policy=policy):
                self.home = self.root / policy; original = self.seed_pair(policy, bad_primary=True)
                path = self.home / 'companion.json'; backup = path.with_suffix('.bak.json')
                primary_bytes, backup_bytes = path.read_bytes(), backup.read_bytes()
                with patch('mecha_game.app.default_fixture_paths', side_effect=AssertionError('restore needs no defaults')):
                    code, receipt = self.invoke([lambda v: click(v, 'inspect_backup'), lambda v: click(v, 'confirm_restore')])
                self.assertEqual(0, code); self.assertTrue(receipt['startup']['entered_play'])
                restored = CompanionSession.load(path)
                self.assertEqual(policy, restored.learning_policy)
                self.assertEqual(original.keeper_id, restored.keeper_id)
                self.assertEqual(0, restored.session_tick)
                self.assertEqual(backup_bytes, path.read_bytes())
                self.assertTrue(any(p.read_bytes() == primary_bytes for p in self.home.glob('*.before-recovery-*.json')))

    def test_injected_directory_apply_resolution_failure_keeps_original_bytes_and_window(self):
        self.seed_pair('qtable'); before = inventory(self.home)
        selected = self.root / 'unresolvable selected home'; original = Path.expanduser
        def denied(path):
            if path == selected: raise RuntimeError('injected applied path expansion unavailable')
            return original(path)
        def type_path(view):
            return [key(pygame.K_a, mod=pygame.KMOD_CTRL),
                    pygame.event.Event(pygame.TEXTINPUT, text=str(selected))]
        with patch.object(Path, 'expanduser', denied):
            code, receipt = self.invoke([lambda v: click(v, 'choose_directory'), type_path,
                                         lambda v: click(v, 'apply_directory'), lambda v: []])
        self.assertEqual(0, code); self.assertFalse(receipt['startup']['entered_play'])
        self.assertEqual(before, inventory(self.home)); self.assertFalse(selected.exists())
        self.assertTrue(any('applied path expansion unavailable' in ' '.join(f['lines']) for f in self.frames))

    def test_injected_selected_path_resolution_failure_still_opens_actionable_window(self):
        original = Path.expanduser
        def denied(path):
            if path == self.home: raise RuntimeError('injected selected path expansion unavailable')
            return original(path)
        with patch.object(Path, 'expanduser', denied), \
                patch('pygame.display.set_mode', wraps=pygame.display.set_mode) as shown:
            code, receipt = self.invoke([lambda v: []])
        self.assertEqual(0, code)
        self.assertTrue(shown.called)
        self.assertFalse(receipt['startup']['entered_play'])
        self.assertTrue(any('selected path expansion unavailable' in ' '.join(f['lines']) for f in self.frames))
        self.assertFalse(self.home.exists())


if __name__ == '__main__':
    unittest.main()
