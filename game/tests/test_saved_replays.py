"""T3: recorded lives survive restart without inventing history or advancing care."""
import copy
from contextlib import closing
import hashlib
import importlib
import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for folder in ('game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT / folder))
import pygame
from mecha_game.app import _EraBench, run
from mecha_game.campaign import KeeperCampaign, TINY_ERA_CONFIG, load_campaign_inputs
from mecha_game.footer import FooterPager
from mecha_game.session import CompanionSession, load_session_inputs


def key(value):
    return pygame.event.Event(pygame.KEYDOWN, key=value, mod=0)


def inventory(path):
    return {p.relative_to(path).as_posix(): p.read_bytes() for p in path.rglob('*') if p.is_file()}


class SavedReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        inputs = load_campaign_inputs(ROOT / 'data/seed_grids_16x16',
            ROOT / 'data/slips/valid/slip_v2_cleanliness.json',
            ROOT / 'data/readability_benchmark/adopted_readability_model.json', repair_epochs=6, seed_limit=12)
        cls.campaign = KeeperCampaign(inputs, era_config=TINY_ERA_CONFIG, campaign_id='saved_replay')
        cls.campaign.advance_era('calm')
        cls.campaign.advance_era('storm')
        cls.recordings = [cls.campaign.record_review_replay(i) for i in range(2)]
        cls.pet = load_session_inputs(ROOT / 'data/seed_grids_16x16/mg_seed16_001_beetle.json',
                                     ROOT / 'data/slips/valid/slip_v2_cleanliness.json')

    def seed(self, keeper, *, recordings=True, policy='qtable'):
        grid, slip, model = self.pet
        CompanionSession(grid, slip, model=model, learning_policy=policy).save_checkpoint(keeper / 'companion.json')
        self.campaign.save(keeper / 'campaign.sqlite3')
        self.campaign.save_state(keeper / 'campaign_state.json')
        if recordings:
            for replay in self.recordings:
                self.campaign.save_review_replay(replay, keeper, keeper / 'campaign.sqlite3')

    def load(self, keeper, era=1):
        module = importlib.import_module('mecha_game.recorded_review')
        return module.load_saved_replay(keeper, 'saved_replay', era,
                                       expected_seed=self.campaign.eras[era]['rng_seed'])

    def replace_recording(self, keeper, replay, era=1):
        path = keeper / 'replays' / f'saved_replay_era{era}.json'
        payload = json.dumps(replay) + '\n'
        path.write_text(payload, encoding='utf-8')
        with closing(sqlite3.connect(keeper / 'campaign.sqlite3')) as conn, conn:
            conn.execute('UPDATE replays SET artifact_sha256=? WHERE era_index=?',
                         (hashlib.sha256(payload.encode()).hexdigest(), era))

    def events(self, keeper, rows, *, read_only=True):
        sequence = iter(rows)
        pages = []
        batch = -1
        def poll():
            nonlocal batch
            batch += 1
            return next(sequence, [pygame.event.Event(pygame.QUIT)])
        layout = FooterPager.layout
        def capture(pager, lines, measure, width, height):
            page = layout(pager, lines, measure, width, height)
            # Final casing after each scripted input, including completed E.
            if len(pages) <= batch: pages.append(list(lines))
            else: pages[batch] = list(lines)
            return page
        with patch.dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy'), \
             patch('pygame.event.get', side_effect=poll), \
             patch.object(FooterPager, 'layout', capture):
            if read_only:
                with patch.object(_EraBench, 'ensure', side_effect=AssertionError('view must not train or resume campaign')):
                    code = run(['--keeper-dir', str(keeper), '--era-scale', 'tiny', '--scale', '1', '--fps', '0', '--tick-frames', '1'])
            else:
                code = run(['--keeper-dir', str(keeper), '--era-scale', 'tiny', '--scale', '1', '--fps', '0', '--tick-frames', '1'])
        self.assertEqual(0, code)
        return pages

    def test_reader_matches_real_artifacts_and_windows_text_hash_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper = Path(directory); self.seed(keeper)
            for era in range(2):
                path = keeper / 'replays' / f'saved_replay_era{era}.json'
                path.write_bytes(path.read_text(encoding='utf-8').replace('\n', '\r\n').encode())
            before = inventory(keeper)
            for era in range(2):
                self.assertEqual(self.recordings[era], self.load(keeper, era))
            self.assertEqual(before, inventory(keeper))

    def test_reader_missing_rows_never_creates_database_or_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper = Path(directory)
            self.assertIsNone(self.load(keeper))
            self.assertEqual({}, inventory(keeper))
            self.seed(keeper, recordings=False)
            before = inventory(keeper)
            self.assertIsNone(self.load(keeper))
            self.assertEqual(before, inventory(keeper))

    def test_reader_refuses_missing_tampered_and_escaping_pointers(self):
        for problem in ('missing', 'tampered', 'escape'):
            with self.subTest(problem=problem), tempfile.TemporaryDirectory() as directory:
                keeper = Path(directory); self.seed(keeper)
                path = keeper / 'replays/saved_replay_era1.json'
                if problem == 'missing': path.unlink()
                elif problem == 'tampered': path.write_text('{}', encoding='utf-8')
                else:
                    with closing(sqlite3.connect(keeper / 'campaign.sqlite3')) as conn, conn:
                        conn.execute("UPDATE replays SET artifact_path='../companion.json' WHERE era_index=1")
                before = inventory(keeper)
                with self.assertRaises(ValueError): self.load(keeper)
                self.assertEqual(before, inventory(keeper))

    def test_reader_refuses_valid_hash_with_invalid_consumed_fields_or_wrong_seed(self):
        for problem in ('empty', 'count', 'phase', 'packet', 'seed'):
            with self.subTest(problem=problem), tempfile.TemporaryDirectory() as directory:
                keeper = Path(directory); self.seed(keeper)
                replay = copy.deepcopy(self.recordings[1])
                if problem == 'empty': replay['frames'] = []
                elif problem == 'count': replay['frame_count'] += 1
                elif problem == 'phase': replay['frames'][0]['phase'] = 'made_up'
                elif problem == 'packet': replay['frames'][0]['packet']['grid_size'] = [0, 0]
                else: replay['parameters']['rng_seed'] += 1
                self.replace_recording(keeper, replay)
                before = inventory(keeper)
                with self.assertRaises(ValueError): self.load(keeper)
                self.assertEqual(before, inventory(keeper))

    def test_restart_latest_playback_is_read_only_and_ignores_care_planning_inputs(self):
        for policy in ('incumbent', 'qtable'):
            with self.subTest(policy=policy), tempfile.TemporaryDirectory() as directory:
                keeper = Path(directory); self.seed(keeper, policy=policy)
                before = inventory(keeper)
                pages = self.events(keeper, [[key(pygame.K_v)],
                    [key(pygame.K_f), key(pygame.K_e), key(pygame.K_a), key(pygame.K_b), key(pygame.K_c)],
                    [pygame.event.Event(pygame.QUIT)]])
                self.assertTrue(pages[0][0].startswith('REVIEW ERA 1'))
                self.assertIn(self.recordings[1]['honest_label'], pages[0])
                self.assertEqual(before, inventory(keeper))

    def test_selected_report_playback_help_pause_clamps_and_returns(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper = Path(directory); self.seed(keeper)
            before = inventory(keeper)
            pages = self.events(keeper, [[key(pygame.K_t)], [key(pygame.K_LEFTBRACKET)],
                [key(pygame.K_v)], [key(pygame.K_F1)], [], [], [key(pygame.K_F1)],
                [key(pygame.K_COMMA)] * 200, [key(pygame.K_PERIOD)] * 200,
                [key(pygame.K_v)], [pygame.event.Event(pygame.QUIT)]])
            self.assertTrue(pages[2][0].startswith('REVIEW ERA 0'))
            self.assertEqual(pages[2][1], pages[6][1], 'help must not advance autoplay')
            self.assertIn('frame 0/', pages[7][1])
            last = self.recordings[0]['frame_count'] - 1
            self.assertIn(f'frame {last}/{last}', pages[8][1])
            self.assertTrue(pages[9][0].startswith('ERA 0 ['))
            self.assertEqual(before, inventory(keeper))

    def test_t_returns_selected_report_and_escape_from_care_replay_leaves_no_queued_action(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper = Path(directory); self.seed(keeper)
            pages = self.events(keeper, [[key(pygame.K_t)], [key(pygame.K_LEFTBRACKET)],
                [key(pygame.K_v)], [key(pygame.K_t)], [key(pygame.K_v)],
                [key(pygame.K_ESCAPE)], [pygame.event.Event(pygame.QUIT)]])
            self.assertTrue(pages[3][0].startswith('ERA 0 ['))
            self.assertTrue(pages[5][0].startswith('ERA 0 ['))
            self.events(keeper, [[key(pygame.K_v)], [key(pygame.K_f)], [key(pygame.K_ESCAPE)], [pygame.event.Event(pygame.QUIT)]])
            pet = CompanionSession.load(keeper / 'companion.json')
            self.assertEqual(1, pet.state['age_ticks'])
            self.assertEqual('companion', pet.log[-1]['actor'])

    def test_unrecorded_or_corrupt_history_shows_paused_notice_and_never_regenerates(self):
        for problem in ('unrecorded', 'corrupt'):
            with self.subTest(problem=problem), tempfile.TemporaryDirectory() as directory:
                keeper = Path(directory); self.seed(keeper, recordings=problem == 'corrupt')
                if problem == 'corrupt': (keeper / 'replays/saved_replay_era1.json').write_text('{}', encoding='utf-8')
                before = inventory(keeper)
                pages = self.events(keeper, [[key(pygame.K_v)], [key(pygame.K_v)], [pygame.event.Event(pygame.QUIT)]])
                self.assertIn('Replay unavailable:', ' '.join(pages[0]))
                self.assertEqual(before, inventory(keeper))

    def test_new_era_records_once_through_existing_producer(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper = Path(directory); self.seed(keeper, recordings=False)
            original = KeeperCampaign.record_review_replay
            calls = []
            def record(campaign, era_index=-1):
                calls.append(era_index)
                return original(campaign, era_index)
            with patch.object(KeeperCampaign, 'record_review_replay', record):
                pages = self.events(keeper, [[key(pygame.K_e)], [key(pygame.K_v)],
                    [key(pygame.K_v)], [key(pygame.K_v)], [pygame.event.Event(pygame.QUIT)]], read_only=False)
            self.assertEqual([0], calls)
            self.assertTrue(pages[1][0].startswith('REVIEW ERA 2'))
            before = inventory(keeper)
            self.events(keeper, [[key(pygame.K_v)], [pygame.event.Event(pygame.QUIT)]])
            self.assertEqual(before, inventory(keeper))

    def test_current_run_refuses_changed_parameters_and_unindexed_file(self):
        for problem in ('parameters', 'unindexed'):
            with self.subTest(problem=problem), tempfile.TemporaryDirectory() as directory:
                keeper = Path(directory); self.seed(keeper, recordings=False)
                original = _EraBench.run_era
                existing = keeper / 'replays/saved_replay_era2.json'
                def run_era(bench, *args, **kwargs):
                    result = original(bench, *args, **kwargs)
                    if problem == 'parameters':
                        bench.campaign.era_config['ticks'] += 1
                    else:
                        existing.parent.mkdir(exist_ok=True)
                        existing.write_bytes(b'preserve unindexed recording')
                    return result
                with patch.object(_EraBench, 'run_era', run_era), \
                     patch.object(KeeperCampaign, 'record_review_replay', side_effect=AssertionError('refusal must not record')):
                    pages = self.events(keeper, [[key(pygame.K_e)], [key(pygame.K_v)], [pygame.event.Event(pygame.QUIT)]], read_only=False)
                self.assertIn('Replay unavailable:', ' '.join(pages[1]))
                if problem == 'unindexed':
                    self.assertEqual(b'preserve unindexed recording', existing.read_bytes())

    def test_reader_rejects_unsupported_schema_without_migration(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper = Path(directory); self.seed(keeper)
            with closing(sqlite3.connect(keeper / 'campaign.sqlite3')) as conn, conn:
                conn.execute('PRAGMA user_version=999')
            before = inventory(keeper)
            with self.assertRaisesRegex(ValueError, 'schema'):
                self.load(keeper)
            self.assertEqual(before, inventory(keeper))

    def test_save_failure_and_retry_remain_available_during_playback(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper = Path(directory); self.seed(keeper)
            before = inventory(keeper)
            original = os.replace
            failures = []
            def replace(source, destination):
                if Path(destination) == keeper / 'companion.json' and not failures:
                    failures.append(True)
                    raise PermissionError('test replay checkpoint lock')
                return original(source, destination)
            save = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_s, mod=pygame.KMOD_CTRL)
            with patch('mecha_game.session.os.replace', replace):
                pages = self.events(keeper, [[], [key(pygame.K_v)], [save], [key(pygame.K_f)], [save], [pygame.event.Event(pygame.QUIT)]])
            self.assertEqual([True], failures)
            self.assertIn('Save failed.', pages[2][0])
            self.assertTrue(pages[4][0].startswith('REVIEW ERA 1'))
            after = inventory(keeper)
            for name in before:
                if name.startswith('replays/') or name.startswith('campaign'):
                    self.assertEqual(before[name], after[name])
            pet = CompanionSession.load(keeper / 'companion.json')
            self.assertEqual(1, pet.state['age_ticks'])
            self.assertEqual('companion', pet.log[-1]['actor'])
            self.assertEqual('qtable', pet.learning_policy)

    def test_recorded_dimensions_do_not_depend_on_current_pet(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper = Path(directory); self.seed(keeper)
            replay = copy.deepcopy(self.recordings[1])
            for frame in replay['frames']:
                if frame.get('packet'): frame['packet']['grid_size'] = [32, 24]
            self.replace_recording(keeper, replay)
            before = inventory(keeper)
            pages = self.events(keeper, [[key(pygame.K_v)], [key(pygame.K_PERIOD)] * 200, [pygame.event.Event(pygame.QUIT)]])
            self.assertTrue(pages[0][0].startswith('REVIEW ERA 1'))
            self.assertEqual(before, inventory(keeper))


if __name__ == '__main__':
    unittest.main()
