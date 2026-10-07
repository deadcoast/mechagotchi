"""Cycle38 preview identity/provenance and immutable saved-footage regressions."""
import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for folder in ('game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT / folder))

from mecha_engine.repair import train_repair_model
from mecha_engine.runtime import live_cycle
from mecha_engine.storage import load_replay_rows, open_ledger
from mecha_game.replay import ReplayPlayer, build_replay, replay_from_lived


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


class PreviewReplayIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid = json.loads((ROOT / 'data/seed_grids/mg_seed_001.json').read_text())
        cls.profile = json.loads((ROOT / 'data/slips/valid/slip_lcd_seed.json').read_text())
        cls.model = train_repair_model([cls.grid], epochs=1)
        cls.options = dict(damage_cycles=1, ticks=24, dropout_rate=0.0, rng_seed=20260707)

    def replay(self, body_response='legacy', **options):
        return build_replay(self.grid, self.profile, self.model,
                            **{**self.options, **options}, body_response=body_response)

    def test_recomputed_identity_versions_and_separates_models(self):
        legacy, workload = self.replay(), self.replay('workload-v1')
        self.assertNotEqual(legacy['replay_id'], workload['replay_id'])
        for model, replay in (('legacy', legacy), ('workload-v1', workload)):
            identity = replay['replay_identity']
            self.assertEqual('mechagotchi_recomputed_replay_v2', identity['format'])
            self.assertEqual('recomputed_preview', identity['kind'])
            self.assertEqual(model, identity['body_response'])
            self.assertEqual('preview-v2-' + identity['inputs_sha256'], replay['replay_id'])
            self.assertEqual(64, len(identity['inputs_sha256']))
            self.assertEqual('mechagotchi_replay_v1', replay['replay_format'])

    def test_identity_binds_full_inputs_and_simulation_options(self):
        baseline = self.replay()
        variants = []
        for index in range(3):
            inputs = copy.deepcopy([self.grid, self.profile, self.model])
            if index == 0: inputs[index]['metadata']['identity_probe'] = True
            elif index == 1: inputs[index]['behavior']['curiosity'] = 0.61
            else: inputs[index]['weights'][0][0] += 0.01
            variants.append(build_replay(*inputs, **self.options))
        for options in ({'damage_cycles': 0}, {'ticks': 12}, {'dropout_rate': 0.01}, {'rng_seed': 20260708}):
            variants.append(self.replay(**options))
        self.assertEqual(len(variants) + 1, len({baseline['replay_id'], *(v['replay_id'] for v in variants)}))

    def test_repeated_and_reordered_input_identity_is_stable_and_inputs_untouched(self):
        original = canonical([self.grid, self.profile, self.model])
        first = self.replay('workload-v1')
        second = build_replay(dict(reversed(list(self.grid.items()))), self.profile, self.model,
                              **self.options, body_response='workload-v1')
        self.assertEqual(canonical(first), canonical(second))
        self.assertEqual(original, canonical([self.grid, self.profile, self.model]))

    def test_omitted_body_model_remains_explicit_legacy_recomputation(self):
        default = build_replay(self.grid, self.profile, self.model, **self.options)
        self.assertEqual(canonical(default), canonical(self.replay('legacy')))
        self.assertEqual('legacy', default['replay_identity']['body_response'])
        self.assertNotIn('body_response', default['parameters'])

    def test_malformed_models_fail_before_simulation(self):
        for model in (None, False, [], {}, 'future', 1):
            with self.subTest(model=model), patch('mecha_game.replay.live_cycle') as simulate:
                with self.assertRaises(ValueError): self.replay(model)
                simulate.assert_not_called()

    def test_actual_live_and_replay_frames_and_physiology_match_for_both_models(self):
        trajectories = {}
        for model in ('legacy', 'workload-v1'):
            lived = live_cycle(self.grid, self.profile, self.model, **self.options,
                               body_response=model, record_frames=True)
            replay = self.replay(model)
            expected = replay_from_lived(self.grid, self.profile, lived, **self.options)
            self.assertEqual(expected['frames'], replay['frames'])
            self.assertEqual(expected['live'], replay['live'])
            self.assertEqual(expected['parameters'], replay['parameters'])
            entries = [f['entry'] for f in replay['frames'] if f['phase'] == 'episode_tick']
            self.assertTrue(any(e['action'] == 'play' for e in entries), 'fixed fixture must exercise the action seam')
            trajectories[model] = [e['state']['energy'] for e in entries]
            if model == 'legacy': self.assertNotIn('body_response', replay['parameters'])
            else: self.assertEqual(model, replay['parameters']['body_response'])
        self.assertNotEqual(trajectories['legacy'], trajectories['workload-v1'])

    def test_historical_formatter_retains_lab_bytes_and_identity(self):
        spec = importlib.util.spec_from_file_location('historical_replay_recorder', ROOT / 'labs/game_loop/replay_recorder.py')
        historical = importlib.util.module_from_spec(spec); spec.loader.exec_module(historical)
        expected = historical.build_replay(self.grid, self.profile, self.model, **self.options)
        lived = live_cycle(self.grid, self.profile, self.model, **self.options, record_frames=True)
        actual = replay_from_lived(self.grid, self.profile, lived, **self.options)
        self.assertEqual(canonical(expected), canonical(actual))
        self.assertEqual(f"{self.grid['grid_id']}_seed{self.options['rng_seed']}", actual['replay_id'])
        self.assertNotIn('replay_identity', actual)

    def test_historical_sample_scrubs_without_rewriting_and_labels_recorded_default(self):
        path = ROOT / 'data/game_loop/replay_sample.json'
        before = path.read_bytes(); replay = json.loads(before)
        original = canonical(replay); player = ReplayPlayer(replay)
        with patch('mecha_game.replay.live_cycle', side_effect=AssertionError('recorded frames cannot resimulate')):
            for index in range(replay['frame_count']):
                player.index = index; player.caption(); player.body_packet(); player.thought_lines()
            labels = ' '.join(player.provenance_lines())
        self.assertIn('Recorded body response: legacy', labels)
        self.assertNotIn('Recomputed preview', labels)
        self.assertEqual(original, canonical(replay)); self.assertEqual(before, path.read_bytes())

    def test_provenance_uses_recorded_model_and_distinguishes_recomputation(self):
        replay = self.replay('workload-v1'); original = canonical(replay)
        lines = ' '.join(ReplayPlayer(replay).provenance_lines())
        self.assertIn('Recomputed preview', lines); self.assertIn('workload-v1', lines)
        self.assertIn('not original Keeper footage', lines)
        historical = copy.deepcopy(replay); historical.pop('replay_identity', None)
        historical['evaluation'] = {'kind': 'mechagotchi_original_evaluation_v1'}
        self.assertIn('Original recorded evaluation', ' '.join(ReplayPlayer(historical).provenance_lines()))
        self.assertEqual(original, canonical(replay))


class PreviewReplayPersistenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_saved_replays import SavedReplayTests
        SavedReplayTests.setUpClass()
        cls.fixture = SavedReplayTests

    def seed(self, keeper):
        self.fixture.seed(self.fixture(), keeper)
        return self.fixture.campaign, copy.deepcopy(self.fixture.recordings[1]), keeper / 'replays/saved_replay_era1.json'

    @staticmethod
    def inventory(keeper):
        return {p.relative_to(keeper).as_posix(): p.read_bytes() for p in keeper.rglob('*') if p.is_file()}

    def test_different_recomputed_payload_cannot_overwrite_saved_footage_or_pointer(self):
        for mutation in ('model', 'identity', 'frame'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                keeper = Path(directory); campaign, replay, path = self.seed(keeper)
                if mutation == 'model': replay['parameters']['body_response'] = 'workload-v1'
                elif mutation == 'identity': replay['replay_id'] += '-different'
                else: replay['frames'][0]['validation_errors'] = ['different']
                before = self.inventory(keeper)
                with self.assertRaisesRegex(ValueError, 'recording|replay'):
                    campaign.save_review_replay(replay, keeper, keeper / 'campaign.sqlite3')
                self.assertEqual(before, self.inventory(keeper))

    def test_identical_retry_preserves_historical_windows_bytes_and_single_pointer(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper = Path(directory); campaign, replay, path = self.seed(keeper)
            path.write_bytes(path.read_text().replace('\n', '\r\n').encode())
            before = self.inventory(keeper)
            for _ in range(3): campaign.save_review_replay(replay, keeper, keeper / 'campaign.sqlite3')
            self.assertEqual(before, self.inventory(keeper))
            with closing(open_ledger(keeper / 'campaign.sqlite3')) as conn:
                self.assertEqual(2, len(load_replay_rows(conn, 'saved_replay')))

    def test_pointer_conflict_preserves_file_before_any_write(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper = Path(directory); campaign, replay, path = self.seed(keeper)
            with closing(open_ledger(keeper / 'campaign.sqlite3')) as conn, conn:
                conn.execute("UPDATE replays SET artifact_sha256=? WHERE era_index=1", ('a' * 64,))
            before = self.inventory(keeper)
            with self.assertRaisesRegex(ValueError, 'recording|replay'):
                campaign.save_review_replay(replay, keeper, keeper / 'campaign.sqlite3')
            self.assertEqual(before, self.inventory(keeper))

    def test_pointer_interruption_retries_same_complete_bytes_without_resimulation(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper = Path(directory); campaign, replay, path = self.seed(keeper)
            with closing(open_ledger(keeper / 'campaign.sqlite3')) as conn, conn:
                conn.execute('DELETE FROM replays WHERE era_index=1')
            path.unlink()
            with patch('mecha_engine.storage.record_replay', side_effect=OSError('pointer interruption')):
                with self.assertRaises(OSError): campaign.save_review_replay(replay, keeper, keeper / 'campaign.sqlite3')
            payload = path.read_bytes()
            with patch('mecha_game.replay.live_cycle', side_effect=AssertionError('retry cannot simulate')):
                for _ in range(2): campaign.save_review_replay(replay, keeper, keeper / 'campaign.sqlite3')
            self.assertEqual(payload, path.read_bytes())
            self.assertEqual(replay, campaign.load_review_replay(keeper, keeper / 'campaign.sqlite3', 1))

    def test_interrupted_file_publication_leaves_no_partial_footage_and_retry_succeeds(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper = Path(directory); campaign, replay, path = self.seed(keeper)
            with closing(open_ledger(keeper / 'campaign.sqlite3')) as conn, conn:
                conn.execute('DELETE FROM replays WHERE era_index=1')
            path.unlink(); before = self.inventory(keeper)
            with patch('os.link', side_effect=OSError('publication interruption')):
                with self.assertRaises(OSError): campaign.save_review_replay(replay, keeper, keeper / 'campaign.sqlite3')
            self.assertEqual(before, self.inventory(keeper))
            campaign.save_review_replay(replay, keeper, keeper / 'campaign.sqlite3')
            self.assertEqual(replay, campaign.load_review_replay(keeper, keeper / 'campaign.sqlite3', 1))

    def test_competing_models_publish_one_complete_recording_and_preserve_its_pointer(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        with tempfile.TemporaryDirectory() as directory:
            keeper = Path(directory); campaign, replay, path = self.seed(keeper)
            with closing(open_ledger(keeper / 'campaign.sqlite3')) as conn, conn:
                conn.execute('DELETE FROM replays WHERE era_index=1')
            path.unlink(); second = copy.deepcopy(replay)
            second['parameters']['body_response'] = 'workload-v1'
            second['replay_id'] += '-different-model'
            ready = Barrier(2)
            def save(value):
                ready.wait(timeout=5)
                try:
                    campaign.save_review_replay(value, keeper, keeper / 'campaign.sqlite3')
                    return True
                except ValueError:
                    return False
            with ThreadPoolExecutor(max_workers=2) as executor:
                results = list(executor.map(save, [replay, second]))
            self.assertEqual([False, True], sorted(results))
            winner = replay if results[0] else second
            self.assertEqual(winner, campaign.load_review_replay(keeper, keeper / 'campaign.sqlite3', 1))
            self.assertEqual(winner, json.loads(path.read_bytes()))
            self.assertFalse(list(path.parent.glob('.replay-*.tmp')))

    def test_native_recorded_model_is_not_relabelled_by_changed_current_keeper(self):
        import pygame
        from test_saved_replays import SavedReplayTests, key
        from mecha_game.session import CompanionSession
        with tempfile.TemporaryDirectory() as directory:
            keeper = Path(directory); campaign, replay, path = self.seed(keeper)
            replay.pop('replay_identity', None)
            replay['replay_id'] = f"{replay['creature']['grid_id']}_seed{replay['parameters']['rng_seed']}"
            SavedReplayTests.replace_recording(self.fixture(), keeper, replay)
            grid, slip, model = self.fixture.pet
            CompanionSession(grid, slip, model=model, body_response='workload-v1').save_checkpoint(keeper / 'companion.json')
            before = self.inventory(keeper)
            with patch('mecha_game.replay.live_cycle', side_effect=AssertionError('native review cannot simulate')):
                pages = SavedReplayTests.events(self, keeper, [[key(pygame.K_v)], [key(pygame.K_v)], [pygame.event.Event(pygame.QUIT)]])
            self.assertTrue(pages[0][0].startswith('REVIEW ERA 1'))
            self.assertIn('Recorded body response: legacy', ' '.join(pages[0]))
            self.assertNotIn('Recorded body response: workload-v1', ' '.join(pages[0]))
            self.assertEqual(before, self.inventory(keeper))


if __name__ == '__main__':
    unittest.main()
