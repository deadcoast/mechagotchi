"""Qualified native default; low-level and existing-life authority stay explicit."""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for directory in ('game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT / directory))
from mecha_game import startup
from mecha_game.app import build_parser
from mecha_game.entry import choose_entry
from mecha_game.packets import default_fixture_paths
from mecha_game.session import CompanionSession, load_session_inputs


def inventory(home):
    return {p.relative_to(home).as_posix(): p.read_bytes() for p in home.rglob('*') if p.is_file()}


class LearningRolloutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paths = default_fixture_paths()
        cls.inputs = load_session_inputs(*cls.paths)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name) / 'keeper'
        self.path = self.home / 'companion.json'

    def saved(self, policy='incumbent'):
        pet = CompanionSession(self.inputs[0], self.inputs[1], model=self.inputs[2], learning_policy=policy)
        pet.save_checkpoint(self.path)
        return pet

    def resolve(self, requested=None, built_in=True):
        return startup.resolve_new_learning_policy(startup.inspect_home(self.home),
            requested_policy=requested, built_in_inputs=built_in)

    def enter(self, *options):
        args = build_parser().parse_args(['--keeper-dir', str(self.home), '--ticks', '1', *options])
        selected, code = choose_entry(args, default_home=lambda: self.home,
            default_paths=lambda: self.paths, new_session=startup.explicit_new_session, receipt={})
        self.assertEqual(0, code)
        return selected.session

    def test_only_native_builtin_fresh_choice_defaults_to_qtable(self):
        self.assertEqual('qtable', self.resolve())
        self.assertEqual('incumbent', self.resolve(built_in=False))
        self.assertEqual('qtable', self.enter().learning_policy)
        self.assertFalse(self.home.exists(), 'creation prepares; inspection and entry do not checkpoint')

    def test_custom_seed_or_covenant_does_not_borrow_the_default_claim(self):
        for option, value in (('--seed', self.paths[0]), ('--slip', self.paths[1])):
            with self.subTest(option=option):
                self.assertEqual('incumbent', self.enter(option, str(value)).learning_policy)
                self.assertEqual('qtable', self.enter(option, str(value), '--learning-policy', 'qtable').learning_policy)

    def test_explicit_new_policy_wins_for_both_input_choices(self):
        for built_in in (False, True):
            for policy in ('incumbent', 'qtable'):
                self.assertEqual(policy, self.resolve(policy, built_in))
        self.assertEqual('incumbent', self.enter('--learning-policy', 'incumbent').learning_policy)

    def test_invalid_policy_refuses_before_creating_files(self):
        for policy in ('bad', True, 1, {}, []):
            with self.subTest(policy=policy), self.assertRaises(ValueError):
                self.resolve(policy)
        self.assertFalse(self.home.exists())

    def test_historical_constructor_and_helper_defaults_remain_incumbent(self):
        pet = CompanionSession(self.inputs[0], self.inputs[1], model=self.inputs[2])
        helper = startup.explicit_new_session(self.path, *self.inputs, None,
                                              inspection=startup.inspect_home(self.home))
        self.assertEqual(('incumbent', 'incumbent'), (pet.learning_policy, helper.learning_policy))
        self.assertFalse(self.home.exists())

    def test_existing_primary_new_without_override_preserves_both_policies(self):
        for policy in ('incumbent', 'qtable'):
            with self.subTest(policy=policy):
                self.home = Path(self.temporary.name) / policy; self.path = self.home / 'companion.json'
                prior = self.saved(policy); before = self.path.read_bytes()
                self.assertIsNone(self.resolve())
                fresh = self.enter('--new')
                self.assertEqual(policy, fresh.learning_policy)
                self.assertEqual(prior.keeper_id, fresh.keeper_id)
                self.assertEqual(prior.lineage[-1]['life_id'], fresh.lineage[-1]['previous_life_id'])
                self.assertNotIn('qtable_policy', fresh.state.get('thread_states', {}))
                self.assertEqual(before, self.path.read_bytes())
                self.assertIn(before, inventory(self.home).values())

    def test_valid_backup_new_without_override_preserves_recorded_policy(self):
        for policy in ('incumbent', 'qtable'):
            with self.subTest(policy=policy):
                self.home = Path(self.temporary.name) / policy; self.path = self.home / 'companion.json'
                old = self.saved(policy); old.advance('feed'); old.save_checkpoint(self.path)
                backup = self.path.with_suffix('.bak.json'); original = backup.read_bytes()
                self.path.write_bytes(b'preserve invalid primary')
                self.assertIsNone(self.resolve())
                fresh = self.enter('--new')
                self.assertEqual(policy, fresh.learning_policy)
                self.assertEqual(old.keeper_id, fresh.keeper_id)
                self.assertEqual('unavailable', fresh.chronicle['prior_history'])
                self.assertIn(original, inventory(self.home).values())
                self.assertIn(b'preserve invalid primary', inventory(self.home).values())

    def test_invalid_prior_explicit_new_uses_default_and_preserves_originals(self):
        self.home.mkdir(); self.path.write_bytes(b'primary evidence')
        self.path.with_suffix('.bak.json').write_bytes(b'backup evidence')
        fresh = self.enter('--new')
        self.assertEqual('qtable', fresh.learning_policy)
        self.assertEqual('unavailable', fresh.chronicle['prior_history'])
        self.assertIn(b'primary evidence', inventory(self.home).values())
        self.assertIn(b'backup evidence', inventory(self.home).values())

    def test_existing_new_can_explicitly_choose_a_cold_different_policy(self):
        old = self.saved('qtable'); before = self.path.read_bytes()
        fresh = self.enter('--new', '--learning-policy', 'incumbent')
        self.assertEqual('incumbent', fresh.learning_policy)
        self.assertEqual(old.keeper_id, fresh.keeper_id)
        self.assertNotIn('qtable_policy', fresh.state.get('thread_states', {}))
        self.assertEqual(before, self.path.read_bytes())

    def test_warm_native_default_restarts_with_exact_table_and_continuation(self):
        pet = self.enter()
        for _ in range(160):
            state = pet.state
            action = ('feed' if state['hunger'] > .55 else 'sleep' if state['energy'] < .35
                      else 'clean' if state['cleanliness'] < .6 else None)
            pet.advance(action)
        self.assertTrue(pet.alive)
        self.assertTrue(pet.state['thread_states']['qtable_policy']['q'])
        pet.save_checkpoint(self.path); before = self.path.read_bytes()
        resumed = self.enter()
        self.assertEqual(pet.state, resumed.state)
        self.assertEqual(before, self.path.read_bytes())
        for _ in range(8):
            self.assertEqual(pet.advance('feed'), resumed.advance('feed'))

    def test_both_saved_policy_conflicts_refuse_without_writes(self):
        for policy, conflict in (('incumbent', 'qtable'), ('qtable', 'incumbent')):
            with self.subTest(policy=policy):
                self.home = Path(self.temporary.name) / policy; self.path = self.home / 'companion.json'
                self.saved(policy); before = inventory(self.home)
                with self.assertRaisesRegex(ValueError, 'conflict'):
                    self.enter('--learning-policy', conflict)
                self.assertEqual(before, inventory(self.home))

    def test_no_care_really_dies_and_child_retains_policy_with_cold_learning(self):
        for policy in ('incumbent', 'qtable'):
            with self.subTest(policy=policy):
                pet = self.enter('--learning-policy', policy)
                for _ in range(20):
                    if not pet.alive: break
                    pet.advance()
                self.assertFalse(pet.alive)
                self.assertEqual((10, 'starvation'), (pet.state['age_ticks'], pet.death_cause))
                self.assertEqual(0, pet.state['action_counts'].get('feed', 0))
                parent_life = pet.lineage[-1]['life_id']; pet.succeed()
                self.assertTrue(pet.alive)
                self.assertEqual(policy, pet.learning_policy)
                self.assertEqual(0, pet.state['age_ticks'])
                self.assertEqual(parent_life, pet.lineage[-1]['parent_life_id'])
                self.assertNotIn('qtable_policy', pet.state.get('thread_states', {}))

    def test_hatch_and_elite_adoption_keep_policy_and_start_cold(self):
        for policy in ('incumbent', 'qtable'):
            for origin in ('hatched', 'era_elite'):
                with self.subTest(policy=policy, origin=origin):
                    pet = self.enter('--learning-policy', policy); pet.advance('feed'); pet.advance()
                    adopted = pet.adopt(self.inputs[0], self.inputs[1], model=self.inputs[2], origin=origin)
                    self.assertEqual(policy, adopted.learning_policy)
                    self.assertEqual(pet.keeper_id, adopted.keeper_id)
                    self.assertEqual('replaced_alive', adopted.lineage[-2]['outcome'])
                    self.assertEqual(0, adopted.state['age_ticks'])
                    self.assertNotIn('qtable_policy', adopted.state.get('thread_states', {}))

    def test_native_new_confirmation_consumes_toggle_without_migrating_prior_life(self):
        import pygame
        def key(code, up=False):
            return pygame.event.Event(pygame.KEYUP if up else pygame.KEYDOWN,
                                      key=code, mod=0, repeat=False)
        for existing in (False, True):
            for toggle in (False, True):
                with self.subTest(existing=existing, toggle=toggle):
                    self.home = Path(self.temporary.name) / f'native-{existing}-{toggle}'
                    self.path = self.home / 'companion.json'
                    prior = self.saved('incumbent') if existing else None
                    original = self.path.read_bytes() if existing else None
                    # Real view/entry/new/save authority, injected keyboard events.
                    # Existing homes focus Resume first; empty homes focus New.
                    first = ([key(pygame.K_RIGHT)] if existing else []) + [key(pygame.K_RETURN)]
                    if toggle:
                        batches = [first, [key(pygame.K_RETURN, True), key(pygame.K_RIGHT), key(pygame.K_RETURN)],
                            [key(pygame.K_RETURN, True), key(pygame.K_END), key(pygame.K_RETURN)]]
                    else:
                        batches = [first, [key(pygame.K_RETURN, True), key(pygame.K_END), key(pygame.K_RETURN)]]
                    pending = iter(batches)
                    args = build_parser().parse_args(['--keeper-dir', str(self.home), '--startup', '--fps', '0', '--frames', '8'])
                    receipt = {}
                    with patch.dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy'), \
                            patch('pygame.event.get', side_effect=lambda: next(pending, [pygame.event.Event(pygame.QUIT)])):
                        selection, code = choose_entry(args, default_home=lambda: self.home,
                            default_paths=lambda: self.paths, new_session=startup.explicit_new_session, receipt=receipt)
                    self.assertEqual(0, code)
                    self.assertIsNotNone(selection)
                    expected = 'incumbent' if existing != toggle else 'qtable'
                    loaded = CompanionSession.load(self.path)
                    self.assertEqual(expected, loaded.learning_policy)
                    self.assertEqual(0, loaded.state['age_ticks'])
                    self.assertNotIn('qtable_policy', loaded.state.get('thread_states', {}))
                    self.assertEqual('ready', receipt['startup_outcome'])
                    if prior:
                        self.assertEqual(prior.keeper_id, loaded.keeper_id)
                        self.assertEqual('incumbent', loaded.lineage[-2].get('learning_policy', 'incumbent'))
                        self.assertIn(original, inventory(self.home).values())


    def test_stale_inspection_refresh_displays_the_new_saved_policy_before_new(self):
        import pygame
        from mecha_game.native_ui import StartupView
        def key(code, up=False):
            return pygame.event.Event(pygame.KEYUP if up else pygame.KEYDOWN,
                                      key=code, mod=0, repeat=False)
        original_draw = StartupView.draw
        for original_policy, external_policy in (('qtable', 'incumbent'), ('incumbent', 'qtable')):
            with self.subTest(original=original_policy, external=external_policy):
                self.home = Path(self.temporary.name) / ('refresh-' + original_policy)
                self.path = self.home / 'companion.json'
                self.saved(original_policy)
                displayed, external_files = [], {}
                step = 0
                def draw(view, *args, **kwargs):
                    result = original_draw(view, *args, **kwargs)
                    if view.mode == 'new':
                        displayed.append(view.new_learning_policy)
                    return result
                def events():
                    nonlocal step, external_files
                    current = step; step += 1
                    if current in (0, 2):
                        if current == 2:
                            self.assertEqual(external_files, inventory(self.home),
                                             'stale confirmation must preserve external save bytes')
                        moves = startup.inspect_home(self.home).actions.index('new')
                        return [key(pygame.K_RETURN, True), key(pygame.K_HOME),
                                *[key(pygame.K_RIGHT) for _ in range(moves)], key(pygame.K_RETURN)]
                    if current == 1:
                        self.saved(external_policy)
                        external_files = inventory(self.home)
                    if current in (1, 3):
                        return [key(pygame.K_RETURN, True), key(pygame.K_END), key(pygame.K_RETURN)]
                    return [pygame.event.Event(pygame.QUIT)]
                args = build_parser().parse_args(['--keeper-dir', str(self.home), '--startup', '--fps', '0', '--frames', '8'])
                receipt = {}
                with patch.dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy'), \
                        patch.object(StartupView, 'draw', draw), patch('pygame.event.get', side_effect=events):
                    selection, code = choose_entry(args, default_home=lambda: self.home,
                        default_paths=lambda: self.paths, new_session=startup.explicit_new_session, receipt=receipt)
                self.assertEqual(0, code)
                self.assertIsNotNone(selection)
                self.assertEqual([original_policy, external_policy], displayed)
                self.assertEqual(external_policy, CompanionSession.load(self.path).learning_policy)
                self.assertEqual('ready', receipt['startup_outcome'])


if __name__ == '__main__':
    unittest.main()
