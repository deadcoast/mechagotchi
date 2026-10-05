"""W2: cold preparation avoids evolution training without changing scientific outputs."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for folder in ('game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT / folder))
from mecha_game import campaign as api
from mecha_game.app import _EraBench, run
from mecha_game.covenant_io import import_covenant
from mecha_game.era_work import EraWork, EraCancelled
from mecha_game.session import CompanionSession, load_session_inputs


def saved(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*') if p.is_file() and 'model_cache' not in p.parts}


class ResponsivePreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paths = api.default_campaign_paths(ROOT)
        cls.eager = api.load_campaign_inputs(**cls.paths, repair_epochs=6, seed_limit=12)
        cls.profile = json.loads((ROOT/'data/slips/valid/slip_lcd_seed.json').read_text())
        cls.pet = load_session_inputs(ROOT/'data/seed_grids_16x16/mg_seed16_001_beetle.json', ROOT/'data/slips/valid/slip_v2_cleanliness.json')

    def fixture(self, root, policy='incumbent'):
        campaign = api.KeeperCampaign(self.eager, era_config=api.TINY_ERA_CONFIG)
        campaign.save(root/'campaign.sqlite3'); campaign.save_state(root/'campaign_state.json')
        CompanionSession(self.pet[0],self.pet[1],model=self.pet[2],learning_policy=policy).save_checkpoint(root/'companion.json')
        return _EraBench('tiny', root/'model_cache', root/'campaign_state.json', root/'campaign.sqlite3')

    def cold(self, **kwargs):
        return api.load_campaign_inputs(**self.paths, repair_epochs=6, seed_limit=12, with_models=False, **kwargs)

    def test_deferred_corpus_has_no_training_cache_or_placeholder_models(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(api,'train_generation_model',side_effect=AssertionError('unneeded generation training')), \
             patch.object(api,'train_repair_model',side_effect=AssertionError('unneeded repair training')):
            root=Path(directory); inputs=self.cold(cache_dir=root/'cache')
            self.assertEqual({'seed_grids','slip_profile','legibility_model'},set(inputs))
            self.assertEqual({k:self.eager[k] for k in inputs},inputs)
            self.assertEqual({},saved(root))

    def test_deferred_models_and_complete_era_match_eager(self):
        deferred=api.prepare_campaign_models(self.cold(),repair_epochs=6)
        self.assertEqual(self.eager,deferred)
        eager=api.KeeperCampaign(copy.deepcopy(self.eager),era_config=api.TINY_ERA_CONFIG)
        lazy=api.KeeperCampaign(deferred,era_config=api.TINY_ERA_CONFIG)
        self.assertEqual(eager.advance_era('calm',record_original=True),lazy.advance_era('calm',record_original=True))
        self.assertEqual(eager.last_original_recording,lazy.last_original_recording)

    def test_failed_preparation_publishes_no_partial_models_and_can_retry(self):
        inputs=self.cold(); before=copy.deepcopy(inputs)
        with patch.object(api,'train_repair_model',side_effect=OSError('training interrupted')):
            with self.assertRaisesRegex(OSError,'interrupted'):
                api.prepare_campaign_models(inputs,repair_epochs=6)
        self.assertEqual(before,inputs)
        self.assertEqual(self.eager,api.prepare_campaign_models(inputs,repair_epochs=6))

    def test_budget_hatch_and_cold_import_do_not_train_era_models(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);bench=self.fixture(root);before=saved(root)
            selected=root/'choice.json';selected.write_text(json.dumps(self.profile))
            with patch.object(api,'train_generation_model',side_effect=AssertionError('unneeded generation training')), \
                 patch.object(api,'train_repair_model',side_effect=AssertionError('unneeded repair training')):
                self.assertTrue(bench.budget_lines());self.assertTrue(bench.hatch(123)['explanation'])
                result=bench.change_covenant(lambda c:import_covenant(c,selected))
            self.assertTrue(result['ok']);self.assertEqual(self.profile,bench.active_covenant())
            self.assertEqual(before['companion.json'],(root/'companion.json').read_bytes())
            self.assertFalse((root/'model_cache').exists())

    def test_invalid_and_stale_imports_refuse_without_training_or_save_changes(self):
        for stale in (False,True):
            with self.subTest(stale=stale),tempfile.TemporaryDirectory() as directory:
                root=Path(directory);bench=self.fixture(root);selected=root/'choice.json'
                selected.write_text(json.dumps(self.profile if stale else {}));before=saved(root)
                with patch.object(api,'train_generation_model',side_effect=AssertionError('unneeded training')):
                    result=bench.change_covenant(lambda c:import_covenant(c,selected,expected_digest='old' if stale else None))
                self.assertFalse(result['ok']);self.assertEqual(before,saved(root));self.assertFalse((root/'model_cache').exists())

    def test_repeated_model_demand_reuses_the_same_models(self):
        with tempfile.TemporaryDirectory() as directory:
            bench=self.fixture(Path(directory));before=bench.ensure().state_payload()
            ready=bench.ensure(models=True)
            with patch.object(api,'train_generation_model',side_effect=AssertionError('duplicate training')):
                self.assertIs(ready,bench.ensure(models=True))
            self.assertEqual(before,ready.state_payload())
            self.assertEqual(self.eager['repair_model'],ready.inputs['repair_model'])

    def test_saved_larger_config_and_unlock_facts_survive_model_demand(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);bench=self.fixture(root)
            current=bench.ensure();current.era_config.update(population=32,generations=12)
            current.campaign['unlocks']=[{'axis':'niche_mastery','tier':3,'earned_era_index':0}]
            before=copy.deepcopy(current.state_payload())
            bench.ensure(models=True)
            self.assertEqual(before,current.state_payload())

    def test_external_state_change_after_light_preparation_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);bench=self.fixture(root);bench.ensure()
            state=root/'campaign_state.json';payload=json.loads(state.read_text());payload['keeper_label']='external owner'
            state.write_text(json.dumps(payload));before=saved(root)
            with self.assertRaisesRegex(ValueError,'changed outside'):
                bench.change_covenant(lambda c:{'ok':True})
            self.assertEqual(before,saved(root))

    def test_training_after_preparation_is_owned_by_era_worker_and_cancel_preserves(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);bench=self.fixture(root);bench.ensure();before=saved(root);threads=[]
            original=api.train_repair_model
            def train(*args,**kwargs):threads.append(threading.get_ident());return original(*args,**kwargs)
            work=EraWork(lambda w:bench.run_era(root/'campaign.sqlite3',work=w))
            original_progress=work.progress
            def cancel_before_evaluation(n,total):work.cancel();original_progress(n,total)
            with patch.object(api,'train_repair_model',train),patch.object(work,'progress',cancel_before_evaluation):
                work.start()
                with self.assertRaises(EraCancelled):work.result()
            self.assertTrue(threads);self.assertNotIn(threading.get_ident(),threads)
            self.assertFalse(work.thread.is_alive());self.assertEqual(before,saved(root))

    def test_source_cold_import_and_cancel_preserve_both_policy_companions(self):
        import pygame
        for policy in ('incumbent','qtable'):
            with self.subTest(policy=policy),tempfile.TemporaryDirectory() as directory:
                root=Path(directory);self.fixture(root,policy);(root/'covenants').mkdir()
                (root/'covenants'/'choice.json').write_text(json.dumps(self.profile));pet=(root/'companion.json').read_bytes()
                key=lambda k:pygame.event.Event(pygame.KEYDOWN,key=k,mod=0)
                events=iter([[key(pygame.K_i)],[key(pygame.K_RETURN)],[key(pygame.K_ESCAPE)],[pygame.event.Event(pygame.QUIT)]])
                with patch.dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'), \
                     patch('pygame.event.get',side_effect=lambda:next(events,[pygame.event.Event(pygame.QUIT)])), \
                     patch.object(api,'train_generation_model',side_effect=AssertionError('unneeded training')):
                    self.assertEqual(0,run(['--keeper-dir',str(root),'--era-scale','tiny','--fps','0','--scale','1','--tick-frames','1']))
                self.assertEqual(pet,(root/'companion.json').read_bytes())
                self.assertEqual(self.profile,json.loads((root/'campaign_state.json').read_text())['slip_profile'])
                self.assertFalse((root/'model_cache').exists())


if __name__=='__main__':unittest.main()
