"""X5 immutable execution and content-sensitive preparation controls."""
import base64
import copy
from contextlib import closing
import hashlib
import json
import shutil
import sqlite3
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for folder in ('game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT/folder))
from mecha_game import campaign as api


class ExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paths = api.default_campaign_paths(ROOT)
        cls.cold = api.load_campaign_inputs(**cls.paths, seed_limit=4, with_models=False)
        cls.inputs = api.prepare_campaign_models(cls.cold, repair_epochs=1)
        cls.config = dict(generations=1, population=2, damage_cycles=1, ticks=3, dropout_rate=0.2)

    def test_loader_retains_raw_sources_without_models_or_writes(self):
        self.assertTrue('input_sources' in self.cold, 'raw source provenance is absent')
        sources = self.cold['input_sources']
        self.assertEqual(4, len([s for s in sources if s['role'] == 'seed_corpus']))
        for source in sources:
            self.assertIn('data_base64', source)
            self.assertIsInstance(json.loads(base64.b64decode(source['data_base64'])), dict)
        self.assertNotIn('repair_model', self.cold)

    def test_same_ids_changed_content_misses_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = copy.deepcopy(self.cold)
            second = copy.deepcopy(first)
            second['seed_grids'][0]['cells'][0]['mutation_weight'] = 0.123
            def train(grids, **kwargs):
                return {'training': copy.deepcopy(grids), 'options': kwargs}
            with patch.object(api, 'train_repair_model', side_effect=train) as trainer:
                a = api.prepare_campaign_models(first, repair_epochs=1, cache_dir=tmp)
                b = api.prepare_campaign_models(second, repair_epochs=1, cache_dir=tmp)
                self.assertEqual(2, trainer.call_count)
                self.assertNotEqual(a['repair_model'], b['repair_model'])
                self.assertEqual(2, len(list(Path(tmp).glob('repair_model_*.json'))))

    def test_capture_reproduction_api_exists(self):
        from mecha_game.execution import capture_execution, finalize_execution, reproduce_era, inspect_execution
        self.assertTrue(all(callable(x) for x in (capture_execution, finalize_execution, reproduce_era, inspect_execution)))

    def campaign(self, name='execution-test', inputs=None):
        return api.KeeperCampaign(copy.deepcopy(inputs or self.inputs), campaign_id=name, era_config=self.config)

    def effective(self, founders=None, weather=None):
        return dict(**copy.deepcopy(self.inputs), founder_grids=founders, cubff_pressure_source=weather,
            readability_selection={**copy.deepcopy(self.inputs['legibility_model']), 'blend': 0.7},
            rng_seed=123, effective_config=self.config)

    def test_cache_hit_equals_fresh_and_corrupt_bytes_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = api.prepare_campaign_models(copy.deepcopy(self.cold), repair_epochs=1, cache_dir=tmp)
            cache = next(Path(tmp).glob('repair_model_*.json')); before = cache.read_bytes()
            with patch.object(api, 'train_repair_model', side_effect=AssertionError('cache miss')):
                second = api.prepare_campaign_models(copy.deepcopy(self.cold), repair_epochs=1, cache_dir=tmp)
            self.assertEqual(first, second)
            self.assertEqual(self.inputs['repair_model'], first['repair_model'])
            self.assertEqual(before, cache.read_bytes())
            envelope = json.loads(before); envelope['model_data_base64'] = base64.b64encode(b'{}').decode()
            corrupt = json.dumps(envelope).encode(); cache.write_bytes(corrupt)
            with patch.object(api, 'train_repair_model', side_effect=AssertionError('silent retrain')):
                with self.assertRaisesRegex(ValueError, 'preserved'):
                    api.prepare_campaign_models(copy.deepcopy(self.cold), repair_epochs=1, cache_dir=tmp)
            self.assertEqual(corrupt, cache.read_bytes())

    def test_raw_source_bytes_are_in_cache_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            changed = copy.deepcopy(self.cold)
            row = changed['input_sources'][0]
            row['data_base64'] = base64.b64encode(base64.b64decode(row['data_base64']) + b' ').decode()
            with patch.object(api, 'train_repair_model', return_value={'weights': []}) as train:
                api.prepare_campaign_models(self.cold, repair_epochs=1, cache_dir=tmp)
                api.prepare_campaign_models(changed, repair_epochs=1, cache_dir=tmp)
                self.assertEqual(2, train.call_count)

    def test_none_and_empty_inputs_remain_distinct_and_weights_order_survives_json(self):
        from mecha_game.execution import capture_execution, decode_execution_inputs
        for founders, weather in ((None, None), ([], [])):
            captured = capture_execution('test', 0, self.effective(founders, weather), [])
            transported = json.loads(json.dumps(captured, sort_keys=True))
            decoded = decode_execution_inputs(transported)
            self.assertEqual(founders, decoded['founder_grids'])
            self.assertEqual(weather, decoded['cubff_pressure_source'])
            self.assertEqual(list(self.inputs['legibility_model']['weights']), list(decoded['legibility_model']['weights']))
            self.assertEqual(list(self.inputs['legibility_model']['weights']), list(decoded['readability_selection']['weights']))

    def test_captured_objects_are_the_actual_execution_inputs(self):
        from mecha_game.execution import decode_execution_inputs
        original = api.evolve
        campaign = self.campaign()
        source_before = copy.deepcopy(campaign.inputs)
        observed = {}
        def run(seeds, profile, generation, repair, **kwargs):
            observed.update(seeds=seeds, profile=profile, generation=generation, repair=repair, kwargs=kwargs)
            # Changes to live loader objects during an era cannot change what
            # the snapshot or actual engine consumes.
            campaign.inputs['seed_grids'][0]['grid_id'] = 'changed-after-capture'
            return original(seeds, profile, generation, repair, **kwargs)
        with patch.object(api, 'evolve', side_effect=run):
            era = campaign.advance_era('calm')
        decoded = decode_execution_inputs(era['execution'])
        self.assertEqual(source_before['seed_grids'], observed['seeds'])
        self.assertEqual(decoded['seed_grids'], observed['seeds'])
        self.assertEqual(decoded['generation_model'], observed['generation'])
        self.assertEqual(decoded['repair_model'], observed['repair'])
        self.assertEqual(decoded['slip_profile'], observed['profile'])
        self.assertEqual(decoded['readability_selection'], observed['kwargs']['readability_selection'])

    def test_all_five_weather_modes_reproduce_full_results_without_input_loaders(self):
        from mecha_engine.storage import load_era_execution
        from mecha_game.execution import reproduce_era, inspect_execution
        for weather in api.WEATHER_NAMES:
            with self.subTest(weather=weather), tempfile.TemporaryDirectory() as tmp:
                campaign = self.campaign(weather)
                with patch.object(api, 'build_weather_source', wraps=api.build_weather_source) as load_weather:
                    era = campaign.advance_era(weather)
                self.assertEqual(1, load_weather.call_count)
                path = Path(tmp)/'campaign.sqlite3'; campaign.save(path)
                before = path.read_bytes()
                with closing(sqlite3.connect(path.as_uri()+'?mode=ro', uri=True)) as conn, \
                     patch.object(api, 'load_campaign_inputs', side_effect=AssertionError('input fallback')), \
                     patch.object(api, 'build_weather_source', side_effect=AssertionError('weather fallback')), \
                     patch.object(api, 'train_generation_model', side_effect=AssertionError('generation fallback')), \
                     patch.object(api, 'train_repair_model', side_effect=AssertionError('repair fallback')):
                    bundle = load_era_execution(conn, weather, 0)
                    self.assertEqual('available', inspect_execution(bundle)['status'])
                    result = reproduce_era(conn, weather, 0)
                self.assertEqual('matched', result['status'], result['reason'])
                self.assertEqual(era['report'], result['report'])
                self.assertEqual(era['elites'], result['elites'])
                self.assertEqual([], result['differing_paths'])
                self.assertEqual(before, path.read_bytes())

    def test_duplicate_ids_keep_order_payloads_verdicts_and_original_footage(self):
        from mecha_game.execution import reproduce_era, source_record, decode_execution_inputs
        from mecha_game.era_plan import EraPlan, EXECUTION_FORMAT
        from mecha_engine.storage import load_era_execution
        valid = copy.deepcopy(self.inputs['seed_grids'][0]); valid['grid_id'] = 'same-id'
        refused = copy.deepcopy(valid); refused['cells'][0]['mutation_weight'] = -1
        sources = [source_record(json.dumps(grid).encode(), role='founder', source_kind='workshop_release',
                    source_position=index, label=f'released/{index}.json') for index, grid in enumerate((valid, refused))]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); campaign = self.campaign()
            era = campaign.advance_era('calm', released_grids=[valid, refused], released_sources=sources, record_original=True)
            occurrences = era['execution']['manifest']['founder_occurrences']
            self.assertEqual([True, False], [row['admitted'] for row in occurrences])
            self.assertEqual(['same-id', 'same-id'], [row['grid_id'] for row in occurrences])
            self.assertEqual([0, 1], [row['ordinal'] for row in occurrences])
            self.assertNotEqual(occurrences[0]['grid_sha256'], occurrences[1]['grid_sha256'])
            self.assertEqual([], era['founder_records'])
            plan = EraPlan(root/'era_plan.json'); plan.begin(campaign, era, None)
            self.assertEqual(EXECUTION_FORMAT, plan.document['format'])
            reopened = EraPlan(root/'era_plan.json'); self.assertIsNone(reopened.error)
            self.assertEqual(era['execution'], reopened.pending['era']['execution'])
            decoded = decode_execution_inputs(reopened.pending['era']['execution'])
            self.assertEqual([valid, refused], decoded['founder_grids'])
            reopened.finish(root/'campaign.sqlite3', root/'campaign_state.json')
            footage = {path.name: path.read_bytes() for path in root.rglob('*') if path.is_file() and 'recording' in path.name}
            with closing(sqlite3.connect((root/'campaign.sqlite3').as_uri()+'?mode=ro', uri=True)) as conn:
                self.assertEqual(era['execution'], load_era_execution(conn, 'execution-test', 0))
                result = reproduce_era(conn, 'execution-test', 0)
            self.assertEqual('matched', result['status'])
            self.assertEqual(footage, {path.name: path.read_bytes() for path in root.rglob('*') if path.is_file() and 'recording' in path.name})

    def test_removed_original_paths_do_not_affect_reproduction(self):
        from mecha_game.execution import reproduce_era
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); corpus = root/'originals'; corpus.mkdir()
            seed_paths = sorted(Path(self.paths['seed_dir']).glob('mg_seed16_*.json'))[:4]
            for path in seed_paths:
                shutil.copy2(path, corpus/path.name)
            profile = corpus/'covenant.json'; adopted = corpus/'readability.json'
            shutil.copy2(self.paths['slip_path'], profile); shutil.copy2(self.paths['adopted_model_path'], adopted)
            inputs = api.load_campaign_inputs(corpus, profile, adopted, repair_epochs=1)
            campaign = self.campaign(inputs=inputs); era = campaign.advance_era('storm')
            ledger = root/'saved.sqlite3'; campaign.save(ledger)
            for path in corpus.iterdir():
                path.unlink()
            corpus.rmdir()
            with closing(sqlite3.connect(ledger.as_uri()+'?mode=ro', uri=True)) as conn:
                result = reproduce_era(conn, 'execution-test', 0)
            self.assertEqual('matched', result['status'])
            self.assertEqual(era['report'], result['report'])
            self.assertEqual(era['elites'], result['elites'])

    def test_source_preparation_v3_keeps_first_capture_and_legacy_remains_explicit(self):
        from mecha_game.era_plan import EraPlan, EXECUTION_FORMAT
        from mecha_game.execution import source_record
        grid = self.inputs['seed_grids'][0]
        first = source_record(b'{}', role='founder', source_kind='workshop_release', source_position=2, label='released/a.json')
        later = {**first, 'data_base64': base64.b64encode(b'{ }').decode()}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'era_plan.json'; plan = EraPlan(path)
            plan.stage([grid], [first]); plan.stage([grid], [later])
            self.assertEqual(EXECUTION_FORMAT, plan.document['format'])
            self.assertEqual([first], EraPlan(path).release_sources)
            before = path.read_bytes()
            with self.assertRaises(ValueError):
                plan.stage([grid], [])
            self.assertEqual(before, path.read_bytes())
            old = dict(format='mechagotchi_era_plan_v1', weather='calm', releases=[grid], pending=None)
            path.write_text(json.dumps(old))
            legacy = EraPlan(path)
            self.assertIsNone(legacy.error); self.assertEqual([None], legacy.release_sources)
            self.assertEqual(json.loads(path.read_bytes()), old)

    def test_tampering_and_unsupported_runtime_calibration_are_unavailable(self):
        from mecha_game.execution import inspect_execution, runtime_identity
        from mecha_engine.archive import descriptors
        bundle = self.campaign().advance_era('calm')['execution']
        corrupt = copy.deepcopy(bundle); sha = corrupt['manifest']['inputs']['seed_corpus_sha256']
        corrupt['blobs'][sha]['data_base64'] = base64.b64encode(b'[]').decode()
        self.assertIn('invalid_execution_evidence', inspect_execution(corrupt)['reason'])
        changed = copy.deepcopy(runtime_identity()); changed['engine_version'] = 'unsupported'
        with patch('mecha_game.execution.runtime_identity', return_value=changed):
            self.assertEqual('unsupported_runtime_identity', inspect_execution(bundle)['reason'])
        with patch.object(descriptors, 'MASS_REFERENCE_AREA', 999):
            self.assertEqual('unsupported_calibration_identity', inspect_execution(bundle)['reason'])
        self.assertEqual('available', inspect_execution(bundle)['status'])
        self.assertEqual('historical_inputs_not_recorded', inspect_execution(None)['reason'])

    def test_pending_retry_compares_complete_execution_and_never_reruns(self):
        from mecha_game.era_plan import EraPlan, _digest
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); campaign = self.campaign(); era = campaign.advance_era('calm', record_original=True)
            plan = EraPlan(root/'era_plan.json'); plan.begin(campaign, era, None)
            with patch.object(api.KeeperCampaign, 'save_state', side_effect=OSError('injected state failure')):
                with self.assertRaisesRegex(OSError, 'injected'):
                    plan.finish(root/'campaign.sqlite3', root/'campaign_state.json')
            pending = (root/'era_plan.json').read_bytes()
            with patch.object(api, 'evolve', side_effect=AssertionError('must not rerun')):
                plan.finish(root/'campaign.sqlite3', root/'campaign_state.json')
            self.assertIsNone(plan.pending)
            (root/'era_plan.json').write_bytes(pending)
            document = json.loads(pending)
            document['pending']['era']['execution']['manifest']['runtime_receipt']['extra'] = 'conflicting evidence'
            document['pending']['sha256'] = _digest({key: value for key, value in document['pending'].items() if key != 'sha256'})
            (root/'era_plan.json').write_text(json.dumps(document))
            before = (root/'era_plan.json').read_bytes()
            with self.assertRaisesRegex(ValueError, 'different era'):
                EraPlan(root/'era_plan.json').finish(root/'campaign.sqlite3', root/'campaign_state.json')
            self.assertEqual(before, (root/'era_plan.json').read_bytes())

    def test_resume_elite_sources_come_from_verified_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); campaign = self.campaign(); first = campaign.advance_era('calm')
            campaign.save(root/'campaign.sqlite3'); campaign.save_state(root/'campaign_state.json')
            resumed = api.KeeperCampaign.load_state(copy.deepcopy(self.inputs), root/'campaign_state.json', root/'campaign.sqlite3')
            self.assertEqual([elite['niche_key'] for elite in first['elites']], [row['niche_key'] for row in resumed.resume_founder_sources])
            era = resumed.advance_era('calm')
            for row in era['execution']['manifest']['founder_occurrences']:
                self.assertEqual('era_elite', row['source_kind'])
                self.assertEqual(0, row['era_index'])
                self.assertEqual('execution-test', row['campaign_id'])
            manual = self.campaign('manual'); manual.resume_founders = [self.inputs['seed_grids'][0]]
            occurrence = manual.advance_era('calm')['execution']['manifest']['founder_occurrences'][0]
            self.assertEqual('in_memory', occurrence['source_kind'])
            self.assertNotIn('niche_key', occurrence)

    def test_imported_base_source_survives_restart_and_spending_is_labelled(self):
        from mecha_game.covenant_io import import_covenant
        from mecha_game.execution import blob_json
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); imported = root/'chosen.json'
            profile = copy.deepcopy(self.inputs['slip_profile']); profile['name'] = 'Actual imported base'
            raw = json.dumps(profile, indent=1).encode(); imported.write_bytes(raw)
            campaign = self.campaign()
            self.assertTrue(import_covenant(campaign, imported)['ok'])
            self.assertEqual(raw, base64.b64decode(campaign.base_covenant_source['data_base64']))
            campaign.save(root/'campaign.sqlite3'); campaign.save_state(root/'campaign_state.json')
            imported.unlink()
            resumed = api.KeeperCampaign.load_state(copy.deepcopy(self.inputs), root/'campaign_state.json', root/'campaign.sqlite3')
            self.assertEqual(campaign.base_covenant_source, resumed.base_covenant_source)
            resumed.campaign['slip_profile']['name'] = 'Effective spent covenant'
            era = resumed.advance_era('calm')
            sources = [row for row in era['execution']['manifest']['sources'] if row['role'] == 'base_covenant']
            self.assertEqual(1, len(sources)); self.assertEqual('chosen.json', sources[0]['label'])
            self.assertFalse(sources[0]['matches_effective_covenant'])
            digest = sources[0]['raw_sha256']
            self.assertEqual(raw, base64.b64decode(era['execution']['blobs'][digest]['data_base64']))
            self.assertEqual(resumed.campaign['slip_profile'], blob_json(era['execution'], era['execution']['manifest']['inputs']['covenant_sha256']))
            state = campaign.state_payload(); state.pop('base_covenant_source', None)
            (root/'campaign_state.json').write_text(json.dumps(state), encoding='utf-8')
            legacy = api.KeeperCampaign.load_state(copy.deepcopy(self.inputs), root/'campaign_state.json', root/'campaign.sqlite3')
            self.assertIsNone(legacy.base_covenant_source)

    def test_loaded_function_must_match_loader_code_before_identity_is_available(self):
        import importlib
        from mecha_game.execution import runtime_identity
        module = importlib.import_module('mecha_engine.runtime.evolve')
        loader = module.__spec__.loader; path = Path(module.__file__)
        raw = path.read_bytes(); changed = raw.replace(b'return archive, report', b"return archive, {'changed': True}")
        self.assertNotEqual(raw, changed)
        get = loader.get_data
        def changed_source(name):
            if str(name).endswith('.pyc'):
                raise FileNotFoundError(name)
            return changed if Path(name) == path else get(name)
        before = module.evolve.__code__
        with patch.object(loader, 'get_data', side_effect=changed_source):
            identity = runtime_identity()
        self.assertFalse(identity['available'])
        self.assertIn('loaded', identity['reason'])
        self.assertIs(before, module.evolve.__code__)
        self.assertEqual(raw, path.read_bytes())

    def test_two_era_save_retains_each_actual_covenant_after_import(self):
        from mecha_game.covenant_io import import_covenant
        from mecha_engine.storage import campaign_history, load_era_execution
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); campaign = self.campaign()
            first = copy.deepcopy(campaign.advance_era('calm'))
            changed = copy.deepcopy(campaign.base_profile); changed['name'] = 'Imported second era'
            source = root/'new-base.json'; source.write_text(json.dumps(changed), encoding='utf-8')
            self.assertTrue(import_covenant(campaign, source)['ok'])
            second = copy.deepcopy(campaign.advance_era('calm'))
            path = root/'campaign.sqlite3'; campaign.save(path)
            with closing(sqlite3.connect(path.as_uri()+'?mode=ro', uri=True)) as conn:
                history = campaign_history(conn, 'execution-test')
                self.assertEqual(self.inputs['slip_profile'], history['eras'][0]['slip_profile'])
                self.assertEqual(changed, history['eras'][1]['slip_profile'])
                self.assertEqual(first['report'], history['eras'][0]['report'])
                self.assertEqual(second['report'], history['eras'][1]['report'])
                self.assertEqual(first['execution'], load_era_execution(conn, 'execution-test', 0))
                self.assertEqual(second['execution'], load_era_execution(conn, 'execution-test', 1))
            before = path.read_bytes(); campaign.save(path)
            self.assertEqual(before, path.read_bytes())


if __name__ == '__main__':
    unittest.main()
