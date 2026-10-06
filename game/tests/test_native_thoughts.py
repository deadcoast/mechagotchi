"""X7 real, tick-bound native thought; SDL injection is not OS keyboard QA."""
import copy
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
from mecha_game.footer import FooterPager
from mecha_game.packets import default_fixture_paths
from mecha_game.replay import ReplayPlayer
from mecha_game.session import CompanionSession, load_session_inputs
from mecha_game.thought_view import LiveThoughtView, current_thought, thought_lines


def key(code):
    return pygame.event.Event(pygame.KEYDOWN, key=code, mod=0, repeat=False)


class ThoughtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_session_inputs(*default_fixture_paths())

    def companion(self, depth=4):
        grid, profile, model = self.inputs
        profile = copy.deepcopy(profile)
        profile['deliberation'] = {'max_ticks': depth, 'confidence_threshold': 1.0}
        return CompanionSession(grid, profile, model=model)

    def thought_snapshot(self):
        session = self.companion()
        session.advance()
        return session, session.snapshot()

    def test_actual_recorded_depth_changes_the_readout_without_engine_mutation(self):
        for depth in (2, 4):
            session = self.companion(depth)
            session.advance()
            before = copy.deepcopy(session.state)
            view = LiveThoughtView()
            view.observe(session.snapshot())
            lines = view.lines(session.snapshot())
            self.assertIn(f'{depth}/{depth} internal steps', ' '.join(lines))
            self.assertEqual(depth, current_thought(session.snapshot())['thought']['tick_count'])
            self.assertEqual(before, session.state)
            self.assertNotIn('confidence', ' '.join(lines).lower())

    def test_reflex_and_manual_override_clear_the_previous_thought(self):
        for change, action in (({'energy': .1}, None), ({}, 'feed')):
            session, snapshot = self.thought_snapshot()
            view = LiveThoughtView()
            view.observe(snapshot)
            self.assertTrue(view.lines(snapshot))
            session.state.update(change)
            session.advance(action)
            view.observe(session.snapshot())
            self.assertIsNone(current_thought(session.snapshot()))
            self.assertEqual([], view.lines(session.snapshot()))

    def test_life_tick_identity_and_companion_actor_are_required(self):
        _, snapshot = self.thought_snapshot()
        self.assertIsNotNone(current_thought(snapshot))
        for changes in ({'age_ticks': 0}, {'age_ticks': 99}, {'session_tick': 99},
                        {'alive': False}, {'life_id': 'another-life'}):
            with self.subTest(changes=changes):
                altered = copy.deepcopy(snapshot)
                altered.update(changes)
                self.assertIsNone(current_thought(altered))
        snapshot['log'][-1]['actor'] = 'keeper'
        self.assertIsNone(current_thought(snapshot))

    def test_early_confidence_exit_shows_one_of_four_actual_steps(self):
        grid, profile, model = self.inputs
        profile = copy.deepcopy(profile)
        profile['deliberation'] = {'max_ticks': 4, 'confidence_threshold': .5}
        session = CompanionSession(grid, profile, model=model)
        session.advance()
        view = LiveThoughtView()
        view.observe(session.snapshot())
        self.assertIn('1/4 internal steps', ' '.join(view.lines(session.snapshot())))

    def test_contradictory_saved_event_is_not_current_thought(self):
        _, snapshot = self.thought_snapshot()
        for changes in ({'alive': False}, {'death_cause': 'starvation'}, {'begging': 'yes'}):
            altered = copy.deepcopy(snapshot)
            altered['log'][-1].update(changes)
            self.assertIsNone(current_thought(altered))

    def test_legacy_entry_needs_exact_clocks_after_current_birth(self):
        _, snapshot = self.thought_snapshot()
        snapshot['log'][-1].pop('life_id', None)
        self.assertIsNotNone(current_thought(snapshot))
        snapshot['born_session_tick'] = snapshot['session_tick']
        self.assertIsNone(current_thought(snapshot))

    def test_malformed_saved_log_or_trace_is_safe_and_never_invents_depth(self):
        _, snapshot = self.thought_snapshot()
        for bad in (None, {}, 'not-a-log', [], [None], ['bad'], [42], [{}]):
            altered = copy.deepcopy(snapshot)
            altered['log'] = bad
            self.assertIsNone(current_thought(altered))
        for bad in (None, 'bad', [], {'tick_count': True, 'max_ticks': 4},
                    {'tick_count': 0, 'max_ticks': 4}, {'tick_count': 5, 'max_ticks': 4},
                    {'tick_count': 1}, {'tick_count': 1, 'max_ticks': '4'}):
            self.assertEqual([], thought_lines(bad, tick=1, action='idle'))

    def test_transient_view_starts_empty_and_clear_requires_a_new_observation(self):
        _, snapshot = self.thought_snapshot()
        view = LiveThoughtView()
        self.assertEqual([], view.lines(snapshot))
        view.observe(snapshot)
        self.assertTrue(view.lines(snapshot))
        view.clear()
        self.assertEqual([], view.lines(snapshot))
        view.observe(snapshot)
        altered = copy.deepcopy(snapshot)
        altered['session_tick'] += 1
        self.assertEqual([], view.lines(altered))
        self.assertEqual([], view.lines(snapshot))

    def test_beg_and_executed_action_remain_distinct(self):
        lines = thought_lines({'tick_count': 2, 'max_ticks': 4}, tick=7,
                              action='idle', begging=True)
        text = ' '.join(lines)
        self.assertIn('asked for food', text)
        self.assertIn('idle', text)
        self.assertNotIn('chose idle', text)

    def test_adoption_birth_and_restart_do_not_resurrect_prior_life_thought(self):
        session, snapshot = self.thought_snapshot()
        view = LiveThoughtView()
        view.observe(snapshot)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'companion.json'
            session.save_checkpoint(path)
            resumed = CompanionSession.load(path)
            self.assertEqual([], LiveThoughtView().lines(resumed.snapshot()))
            adopted = resumed.adopt(resumed.grid, resumed.slip_profile)
            self.assertTrue(adopted.log)
            self.assertEqual([], view.lines(adopted.snapshot()))
            self.assertIsNone(current_thought(adopted.snapshot()))

    def test_replay_only_uses_the_selected_episode_frame(self):
        trace = {'tick_count': 3, 'max_ticks': 4}
        frames = [
            {'frame': 0, 'phase': 'birth', 'cycle': 0},
            {'frame': 1, 'phase': 'episode_tick', 'cycle': 0, 'tick': 1,
             'entry': {'tick': 1, 'action': 'play', 'deliberation': trace}},
            {'frame': 2, 'phase': 'episode_tick', 'cycle': 0, 'tick': 2,
             'entry': {'tick': 2, 'action': 'sleep'}},
            {'frame': 3, 'phase': 'wound', 'cycle': 1, 'removed_cell_count': 0},
        ]
        player = ReplayPlayer({'frame_count': len(frames), 'frames': frames})
        self.assertEqual([], player.thought_lines())
        player.step()
        self.assertIn('Recorded thought t1: 3/4 internal steps', ' '.join(player.thought_lines()))
        player.step()
        self.assertEqual([], player.thought_lines())
        player.step()
        self.assertEqual([], player.thought_lines())
        player.back(); player.back()
        frames[1]['entry']['tick'] = 9
        self.assertEqual([], player.thought_lines())


class NativeThoughtJourneyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_session_inputs(*default_fixture_paths())

    companion = ThoughtTests.companion

    def setUp(self):
        self.env = patch.dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy')
        self.env.start()
        self.addCleanup(self.env.stop)

    def drive(self, home, events, *, tick_frames=3, capture=None):
        records = []
        current_lines = []
        pending = iter(events)
        layout = FooterPager.layout
        def record(pager, lines, *args, **kwargs):
            current_lines[:] = lines
            return layout(pager, lines, *args, **kwargs)
        def paint():
            records.append(list(current_lines))
            if capture is not None:
                capture.append(pygame.display.get_surface().copy())
        with patch('pygame.event.get', side_effect=lambda: next(pending, [pygame.event.Event(pygame.QUIT)])), \
                patch.object(FooterPager, 'layout', record), patch('pygame.display.flip', side_effect=paint):
            self.assertEqual(0, run(['--keeper-dir', str(home), '--scale', '2', '--fps', '0',
                                     '--tick-frames', str(tick_frames)]))
        return records

    def test_actual_native_care_help_override_quit_and_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            self.companion().save_checkpoint(home / 'companion.json')
            frames = self.drive(home, [[], [key(pygame.K_F1)], [key(pygame.K_ESCAPE)], [],
                                       [key(pygame.K_f)], [], [], [pygame.event.Event(pygame.QUIT)]])
            has_thought = lambda lines: any(line.startswith('Thought t') for line in lines)
            self.assertTrue(has_thought(frames[0]))
            self.assertFalse(has_thought(frames[1]))
            self.assertFalse(has_thought(frames[2]))
            self.assertTrue(has_thought(frames[3]))
            self.assertFalse(has_thought(frames[6]))
            self.assertFalse(has_thought(frames[7]))
            saved = CompanionSession.load(home / 'companion.json')
            self.assertEqual(3, saved.state['age_ticks'])
            self.assertEqual(1, saved.state['action_counts'].get('feed'))
            restarted = self.drive(home, [[key(pygame.K_F6)], [key(pygame.K_ESCAPE)],
                                          [pygame.event.Event(pygame.QUIT)]], tick_frames=100)
            self.assertFalse(any(has_thought(lines) for lines in restarted))
            self.assertEqual(3, CompanionSession.load(home / 'companion.json').state['age_ticks'])

    def test_actual_native_reflex_has_no_thought(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            session = self.companion()
            session.state['energy'] = .1
            session.save_checkpoint(home / 'companion.json')
            frames = self.drive(home, [[], [pygame.event.Event(pygame.QUIT)]])
            self.assertFalse(any(line.startswith('Thought t') for lines in frames for line in lines))
            saved = CompanionSession.load(home / 'companion.json')
            self.assertEqual('sleep', saved.log[-1]['action'])


if __name__ == '__main__':
    unittest.main()
