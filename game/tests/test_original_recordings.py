"""U1: actual best evaluation, bounded retention, journal recovery and saved playback."""
import copy
from contextlib import closing
import importlib
import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for folder in ('game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT / folder))
from mecha_game.app import _EraBench
from mecha_game.campaign import KeeperCampaign, TINY_ERA_CONFIG, load_campaign_inputs
from mecha_game.era_work import EraWork, EraCancelled
from mecha_game.recorded_review import load_saved_replay


def inventory(path):
    return {p.relative_to(path).as_posix(): p.read_bytes() for p in path.rglob('*')
            if p.is_file() and 'model_cache' not in p.parts}


class OriginalRecordingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_campaign_inputs(ROOT / 'data/seed_grids_16x16',
            ROOT / 'data/slips/valid/slip_v2_cleanliness.json',
            ROOT / 'data/readability_benchmark/adopted_readability_model.json', repair_epochs=6, seed_limit=12)

    def campaign(self):
        return KeeperCampaign(self.inputs, era_config=TINY_ERA_CONFIG, campaign_id='original_test')

    def fixture(self, path):
        campaign = self.campaign()
        campaign.advance_era('calm')
        campaign.save(path / 'campaign.sqlite3')
        campaign.save_state(path / 'campaign_state.json')
        bench = _EraBench('tiny', path / 'model_cache', path / 'campaign_state.json', path / 'campaign.sqlite3')
        bench.campaign = campaign
        bench.choose_weather(2)
        return bench

    def test_original_capture_matches_unobserved_era_and_actual_candidate(self):
        plain, captured = self.campaign(), self.campaign()
        expected = plain.advance_era('storm')
        with patch('mecha_game.replay.live_cycle', side_effect=AssertionError('no demonstration simulation')):
            actual = captured.advance_era('storm', record_original=True)
        self.assertEqual(expected, actual)
        envelope = captured.last_original_recording
        self.assertEqual('recorded', envelope['status'])
        replay = envelope['replay']
        origin = replay['evaluation']
        best = max(actual['elites'], key=lambda e: (e['fitness'], e['niche_key']))
        self.assertEqual(best['grid'], origin['final_grid'])
        self.assertEqual(best['niche_key'], origin['niche_key'])
        creature = actual['report']['generations'][origin['generation_index']]['creatures'][origin['candidate_index']]
        self.assertEqual(creature['candidate_grid_id'], origin['original_grid']['grid_id'])
        self.assertEqual(creature['cycles'], replay['live']['cycles'])
        self.assertEqual(actual['rng_seed'] + origin['generation_index'] * 100000 + origin['candidate_index'], replay['parameters']['rng_seed'])
        self.assertIn('Original era evaluation', replay['honest_label'])

    def test_frame_and_byte_limits_preserve_real_era_without_fake_recording(self):
        module = importlib.import_module('mecha_game.original_recording')
        expected = self.campaign().advance_era('calm')
        for limit in ('MAX_REPLAY_FRAMES', 'MAX_REPLAY_BYTES'):
            with self.subTest(limit=limit), patch.object(module, limit, 1):
                campaign = self.campaign()
                self.assertEqual(expected, campaign.advance_era('calm', record_original=True))
                record = campaign.last_original_recording
                self.assertEqual('unavailable', record['status'])
                self.assertIsNone(record['replay'])
                self.assertIn('limit', record['reason'])

    def test_completed_journal_retains_capture_and_restart_never_resimulates(self):
        with tempfile.TemporaryDirectory() as name:
            path = Path(name); bench = self.fixture(path)
            with patch.object(KeeperCampaign, 'save_state', side_effect=PermissionError('state locked')):
                with self.assertRaises(PermissionError): bench.run_era(path / 'campaign.sqlite3')
            pending = bench.plan.pending
            self.assertEqual('recorded', pending['recording']['status'])
            expected = copy.deepcopy(pending['recording']['replay'])
            resumed = _EraBench('tiny', path / 'model_cache', path / 'campaign_state.json', path / 'campaign.sqlite3')
            with patch.object(KeeperCampaign, 'advance_era', side_effect=AssertionError('no rerun')), \
                 patch('mecha_game.replay.live_cycle', side_effect=AssertionError('no reconstruction')):
                era = resumed.run_era(path / 'campaign.sqlite3')
                before = inventory(path)
                actual = load_saved_replay(path, 'original_test', era['era_index'], expected_seed=era['rng_seed'])
            self.assertEqual(expected, actual)
            self.assertEqual(before, inventory(path))
            self.assertIsNone(resumed.plan.pending)

    def test_cancel_discards_original_capture_and_all_saved_inputs(self):
        with tempfile.TemporaryDirectory() as name:
            path = Path(name); bench = self.fixture(path); before = inventory(path)
            work = EraWork(lambda observer: bench.run_era(path / 'campaign.sqlite3', work=observer))
            original = work.progress
            def progress(completed, budget):
                original(completed, budget)
                if completed == 1: work.cancel()
            work.progress = progress; work.start()
            with self.assertRaises(EraCancelled): work.result()
            self.assertEqual(before, inventory(path))
            self.assertIsNone(bench._completed_work)
            self.assertFalse(work.thread.is_alive())

    def test_conflicting_artifact_is_preserved_and_pending_capture_remains(self):
        with tempfile.TemporaryDirectory() as name:
            path = Path(name); bench = self.fixture(path)
            target = path / 'replays' / 'original_test_era1.json'
            target.parent.mkdir(); target.write_bytes(b'preserve foreign recording')
            with self.assertRaisesRegex(ValueError, 'recording'):
                bench.run_era(path / 'campaign.sqlite3')
            self.assertEqual(b'preserve foreign recording', target.read_bytes())
            self.assertEqual('recorded', bench.plan.pending['recording']['status'])

    def test_other_selected_elite_explicitly_has_no_original_recording(self):
        with tempfile.TemporaryDirectory() as name:
            path = Path(name); bench = self.fixture(path)
            era = bench.run_era(path / 'campaign.sqlite3')
            best = max(era['elites'], key=lambda e: (e['fitness'], e['niche_key']))
            before = inventory(path)
            with self.assertRaisesRegex(ValueError, 'not recorded'):
                load_saved_replay(path, 'original_test', era['era_index'], expected_seed=era['rng_seed'],
                                  selected_elite={'grid_id':'a_different_selection', 'grid':{}, 'niche_key':'different'})
            replay = load_saved_replay(path, 'original_test', era['era_index'], expected_seed=era['rng_seed'], selected_elite=best)
            self.assertEqual(best['grid_id'], replay['evaluation']['final_grid']['grid_id'])
            self.assertEqual(before, inventory(path))


    def test_original_playback_from_archive_returns_without_simulation_or_care(self):
        import pygame
        from test_saved_replays import SavedReplayTests, key
        from mecha_game.session import CompanionSession, load_session_inputs
        pet = load_session_inputs(ROOT / 'data/seed_grids_16x16/mg_seed16_001_beetle.json',
                                  ROOT / 'data/slips/valid/slip_v2_cleanliness.json')
        for policy in ('incumbent', 'qtable'):
            with self.subTest(policy=policy), tempfile.TemporaryDirectory() as name:
                path = Path(name); bench = self.fixture(path)
                era = bench.run_era(path / 'campaign.sqlite3')
                grid, slip, model = pet
                CompanionSession(grid, slip, model=model, learning_policy=policy).save_checkpoint(path / 'companion.json')
                before = inventory(path)
                best = max(era['elites'], key=lambda e: (e['fitness'], e['niche_key']))
                position = era['elites'].index(best)
                rows = [[key(pygame.K_b)]] + [[key(pygame.K_PERIOD)]] * position
                review_at = len(rows)
                rows += [[key(pygame.K_v)], [key(pygame.K_F1)], [key(pygame.K_ESCAPE)],
                         [key(pygame.K_v)], [key(pygame.K_t)], [key(pygame.K_v)],
                         [key(pygame.K_ESCAPE)], [pygame.event.Event(pygame.QUIT)]]
                with patch('mecha_game.replay.live_cycle', side_effect=AssertionError('playback cannot simulate')), \
                     patch.object(KeeperCampaign, 'advance_era', side_effect=AssertionError('playback cannot evolve')):
                    pages = SavedReplayTests.events(self, path, rows)
                self.assertTrue(pages[review_at][0].startswith('REVIEW ERA 1'))
                self.assertIn('Original era evaluation', ' '.join(pages[review_at]))
                self.assertTrue(pages[review_at + 3][0].startswith('REPERTOIRE'))
                self.assertTrue(pages[review_at + 4][0].startswith('ERA 1'))
                self.assertEqual(before, inventory(path))

    def test_archive_other_selection_shows_not_recorded_and_stays_in_archive(self):
        import pygame
        from test_saved_replays import SavedReplayTests, key
        from mecha_game.session import CompanionSession, load_session_inputs
        with tempfile.TemporaryDirectory() as name:
            path = Path(name); bench = self.fixture(path); era = bench.run_era(path / 'campaign.sqlite3')
            self.assertGreater(len(era['elites']), 1)
            grid, slip, model = load_session_inputs(ROOT / 'data/seed_grids_16x16/mg_seed16_001_beetle.json',
                                                   ROOT / 'data/slips/valid/slip_v2_cleanliness.json')
            CompanionSession(grid, slip, model=model).save_checkpoint(path / 'companion.json')
            best = max(era['elites'], key=lambda e: (e['fitness'], e['niche_key']))
            other = 1 if era['elites'].index(best) == 0 else 0
            rows = [[key(pygame.K_b)]] + [[key(pygame.K_PERIOD)]] * other
            at = len(rows); rows += [[key(pygame.K_v)], [pygame.event.Event(pygame.QUIT)]]
            before = inventory(path)
            pages = SavedReplayTests.events(self, path, rows)
            self.assertIn('not recorded', ' '.join(pages[at]))
            self.assertTrue(any(line.startswith('REPERTOIRE') for line in pages[at]))
            self.assertEqual(before, inventory(path))


    def test_rehashed_wrong_provenance_is_refused_before_playback(self):
        import hashlib
        import sqlite3
        with tempfile.TemporaryDirectory() as name:
            path = Path(name); bench = self.fixture(path); era = bench.run_era(path / 'campaign.sqlite3')
            target = path / 'replays' / 'original_test_era1.json'
            original = json.loads(target.read_text(encoding='utf-8'))
            def seed(doc): doc['replay']['parameters']['rng_seed'] += 1
            def weather(doc): doc['replay']['parameters']['dropout_rate'] += .1
            def generation(doc): doc['replay']['evaluation']['generation_index'] += 1
            def identity(doc): doc['replay']['evaluation']['final_grid']['grid_id'] = 'wrong_elite'
            def campaign(doc): doc['campaign_id'] = 'wrong_campaign'
            def frames(doc): doc['replay']['frames'][1]['frame'] = 77
            for mutate in (seed, weather, generation, identity, campaign, frames):
                with self.subTest(mutation=mutate.__name__):
                    document = copy.deepcopy(original); mutate(document)
                    payload = json.dumps(document) + '\n'; target.write_text(payload, encoding='utf-8')
                    with closing(sqlite3.connect(path / 'campaign.sqlite3')) as conn, conn:
                        conn.execute('UPDATE replays SET artifact_sha256=? WHERE era_index=1',
                                     (hashlib.sha256(payload.encode('utf-8')).hexdigest(),))
                    before = inventory(path)
                    with self.assertRaises(ValueError):
                        load_saved_replay(path, 'original_test', 1, expected_seed=era['rng_seed'])
                    self.assertEqual(before, inventory(path))

    def test_interrupted_recording_and_pointer_writes_retry_the_same_capture(self):
        from mecha_game.original_recording import encoded
        for stage in ('artifact', 'pointer', 'journal_clear'):
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as name:
                path = Path(name); bench = self.fixture(path)
                if stage == 'artifact':
                    import mecha_game.session as session
                    original = session._write_bytes_atomic
                    def fail(target, payload):
                        if Path(target).parent.name == 'replays': raise PermissionError('recording locked')
                        return original(target, payload)
                    blocker = patch.object(session, '_write_bytes_atomic', side_effect=fail)
                elif stage == 'pointer':
                    blocker = patch('mecha_engine.storage.record_replay', side_effect=PermissionError('pointer locked'))
                else:
                    from mecha_game.era_plan import EraPlan
                    original = EraPlan._write
                    def fail(plan, payload):
                        if plan.pending is not None and payload['pending'] is None:
                            raise PermissionError('journal clear locked')
                        return original(plan, payload)
                    blocker = patch.object(EraPlan, '_write', fail)
                with blocker:
                    with self.assertRaises(PermissionError): bench.run_era(path / 'campaign.sqlite3')
                pending = bench.plan.pending
                expected = copy.deepcopy(pending['recording'])
                resumed = _EraBench('tiny', path / 'model_cache', path / 'campaign_state.json', path / 'campaign.sqlite3')
                with patch.object(KeeperCampaign, 'advance_era', side_effect=AssertionError('must not evolve again')):
                    resumed.run_era(path / 'campaign.sqlite3')
                self.assertEqual(encoded(expected), (path / 'replays' / 'original_test_era1.json').read_bytes())
                self.assertIsNone(resumed.plan.pending)
                replay = load_saved_replay(path, 'original_test', 1, expected_seed=pending['era']['rng_seed'])
                self.assertEqual(expected['replay'], replay)


    def test_pending_original_journal_is_versioned_against_legacy_data_loss(self):
        with tempfile.TemporaryDirectory() as name:
            path = Path(name); bench = self.fixture(path)
            with patch('mecha_game.original_recording.save_original_recording', side_effect=PermissionError('recording locked')):
                with self.assertRaises(PermissionError): bench.run_era(path / 'campaign.sqlite3')
            pending = json.loads((path / 'era_plan.json').read_text(encoding='utf-8'))
            self.assertEqual('mechagotchi_era_plan_v2', pending['format'])
            self.assertEqual('recorded', pending['pending']['recording']['status'])
            resumed = _EraBench('tiny', path / 'model_cache', path / 'campaign_state.json', path / 'campaign.sqlite3')
            with patch.object(KeeperCampaign, 'advance_era', side_effect=AssertionError('no resimulation')):
                resumed.run_era(path / 'campaign.sqlite3')
            idle = json.loads((path / 'era_plan.json').read_text(encoding='utf-8'))
            self.assertEqual('mechagotchi_era_plan_v1', idle['format'])
            self.assertIsNone(idle['pending'])


    def test_unavailable_limit_status_is_durable_without_footage_reconstruction(self):
        from mecha_game import original_recording
        with tempfile.TemporaryDirectory() as name:
            path = Path(name); bench = self.fixture(path)
            with patch.object(original_recording, 'MAX_REPLAY_FRAMES', 1):
                era = bench.run_era(path / 'campaign.sqlite3')
            before = inventory(path)
            with patch('mecha_game.replay.live_cycle', side_effect=AssertionError('must not reconstruct')):
                with self.assertRaisesRegex(ValueError, 'not recorded.*limit'):
                    load_saved_replay(path, 'original_test', 1, expected_seed=era['rng_seed'])
            self.assertEqual(before, inventory(path))
            self.assertIsNone(bench.plan.pending)
            self.assertEqual(2, json.loads((path / 'campaign_state.json').read_text(encoding='utf-8'))['era_count'])
