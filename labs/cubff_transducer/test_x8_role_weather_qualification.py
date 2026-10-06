"""Instrument wiring tests use synthetic records/mocks, never qualification runs."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import x8_role_weather_qualification as instrument


def inputs():
    grid = dict(grid_id=instrument.PARENT_ID, organs={'core': {'role': 'body_core'}}, cells=[])
    return dict(seed_grids=[grid] + [dict(grid, grid_id=str(index)) for index in range(49)],
                slip_profile={'grid': {}}, generation_model={}, repair_model={},
                legibility_model={}, readability_selection={},
                weather_sources={'real': [{'snapshot_id': str(index)} for index in range(14)]})


def fake_engine():
    candidate = copy.deepcopy(inputs()['seed_grids'][0])
    return SimpleNamespace(validate_grid=Mock(return_value=SimpleNamespace(ok=True, errors=[])),
        is_grid_aligned=Mock(return_value=SimpleNamespace(ok=True, errors=[])),
        validate_slip=Mock(return_value=SimpleNamespace(ok=True, errors=[])),
        GenerationModel=lambda **kwargs: kwargs,
        generate_candidate=Mock(return_value=copy.deepcopy(candidate)),
        apply_stochastic_damage=Mock(return_value=copy.deepcopy(candidate)),
        repair_wound_sites=Mock(return_value=copy.deepcopy(candidate)),
        learned_readability_score=Mock(return_value=.5), evolve=Mock(return_value=({}, {})))


def observed(seed, index, removed):
    return dict(generation_index=0, candidate_index=index, run_seed=seed + index,
                candidate_grid={'grid_id': str(index)}, cycles=[dict(cycle=1,
                    damage_seed=(seed + index) * 10 + 1, removed_cell_count=removed,
                    frames={'removed_cells': [[cell, 0] for cell in range(removed)]})])


def weather_results(extra=0):
    results = []
    source = inputs()
    for index, case in enumerate(instrument.weather_plan()):
        weather = source['weather_sources']['real']; offset = case['rotation']
        pressure = dict(snapshot_id=str(offset), dropout_multiplier=1)
        creatures = [{'grid_id': str(candidate)} for candidate in range(16)]
        observations = [dict(observed(case['seed'], candidate,
                            1 + (extra if case['density'] and candidate == 0 else 0)),
                            creature=creatures[candidate], generation_weather=pressure, effective_dropout_rate=.2)
                        for candidate in range(16)]
        config = dict(generations=1, population=16, damage_cycles=2, ticks=16, dropout_rate=.2,
                      rng_seed=case['seed'], founder_grids=None, cubff_density_pressure=case['density'],
                      population_policy='legacy_archive', founder_start_mode='bootstrap',
                      survival_regime='sheltered', care_selection_policy='off')
        report = dict(rng_seed=case['seed'], generations_requested=1, population=16,
                      damage_cycles=2, ticks=16, dropout_rate=.2,
                      generations=[dict(generation=0, creatures=creatures)],
                      cubff_pressure=dict(density_pressure=case['density'], source_snapshot_count=14,
                                          by_generation=[pressure]))
        results.append(dict(case_index=index, case=case, inputs_sha256=instrument.digest(source),
                            archive={}, report=report, effective_config=config,
                            ordered_weather_sha256=instrument.digest(weather[offset:] + weather[:offset]),
                            observations=observations))
    return results


class RoleWeatherInstrumentTests(unittest.TestCase):
    def test_fixed_plans_cover_thirty_roles_twenty_weather_and_declared_duplicates(self):
        roles, weather = instrument.role_plan(), instrument.weather_plan()
        self.assertEqual(31, len(roles)); self.assertEqual(21, len(weather))
        self.assertEqual([(seed, level) for seed in range(20260700, 20260710) for level in range(3)],
                         [(row['seed'], row['level']) for row in roles[:-1]])
        self.assertEqual([(seed, value) for seed in range(20260700, 20260710) for value in (False, True)],
                         [(row['seed'], row['density']) for row in weather[:-1]])
        self.assertEqual(dict(roles[0], duplicate_of=0), roles[-1])
        self.assertEqual(dict(weather[0], duplicate_of=0), weather[-1])
        for bad in (-1, 31, True, .5):
            with self.assertRaises(ValueError): instrument.selected_case(roles, bad)

    def test_role_probe_uses_fixed_parent_actual_repair_seed_and_three_inventory_levels(self):
        engine = fake_engine(); source = inputs(); original = copy.deepcopy(source)
        with patch.object(instrument, '_engine', return_value=engine):
            result = instrument.role_case(source, 5)
        self.assertEqual(original, source)
        self.assertEqual([50, 50, 50], [len(row['rows']) for row in result['inventory']])
        self.assertEqual(instrument.PARENT_ID, engine.generate_candidate.call_args.args[0]['grid_id'])
        self.assertEqual(20260701, engine.generate_candidate.call_args.kwargs['rng_seed'])
        self.assertEqual(202607011, engine.apply_stochastic_damage.call_args.kwargs['rng_seed'])
        self.assertEqual(.2, engine.apply_stochastic_damage.call_args.kwargs['dropout_rate'])
        self.assertTrue(engine.repair_wound_sites.call_args.kwargs['validity_guard'])
        self.assertEqual(list(instrument.ROLES), result['profile']['grid']['allowed_organ_roles'])

    def test_role_parent_refusal_cannot_select_another_parent(self):
        engine = fake_engine()
        engine.is_grid_aligned.return_value = SimpleNamespace(ok=False, errors=['blocked'])
        with patch.object(instrument, '_engine', return_value=engine), self.assertRaises(ValueError):
            instrument.role_case(inputs(), 0)
        engine.generate_candidate.assert_not_called()

    def test_generation_rejection_is_retained_without_repair_or_fallback(self):
        engine = fake_engine(); engine.generate_candidate.side_effect = ValueError('guard refusal')
        with patch.object(instrument, '_engine', return_value=engine):
            result = instrument.role_case(inputs(), 0)
        self.assertEqual('guard refusal', result['generation']['error'])
        self.assertIsNone(result['repair']); engine.repair_wound_sites.assert_not_called()
        self.assertEqual(1, engine.generate_candidate.call_count)

    def test_failed_repair_is_reported_without_replacement(self):
        engine = fake_engine()
        engine.repair_wound_sites.return_value['grid_id'] = 'invalid-repair'
        engine.validate_grid.side_effect = lambda grid: SimpleNamespace(
            ok=grid['grid_id'] != 'invalid-repair', errors=['disconnected'] if grid['grid_id'] == 'invalid-repair' else [])
        with patch.object(instrument, '_engine', return_value=engine):
            result = instrument.role_case(inputs(), 0)
        self.assertFalse(result['repair']['accepted'])
        self.assertEqual(['disconnected'], result['repair']['validity_errors'])
        self.assertEqual(1, engine.repair_wound_sites.call_count)

    def test_weather_uses_fixed_rotation_settings_and_one_observed_runtime_call(self):
        engine = fake_engine(); source = inputs()
        with patch.object(instrument, '_engine', return_value=engine):
            result = instrument.weather_case(source, 5)
        kwargs = engine.evolve.call_args.kwargs
        self.assertEqual(1, engine.evolve.call_count)
        self.assertEqual((1, 16, 2, 16, .2, 20260702), tuple(kwargs[key] for key in
            ('generations', 'population', 'damage_cycles', 'ticks', 'dropout_rate', 'rng_seed')))
        self.assertEqual('2', kwargs['cubff_pressure_source'][0]['snapshot_id'])
        self.assertTrue(kwargs['cubff_density_pressure'])
        self.assertEqual('off', kwargs['care_selection_policy'])
        self.assertEqual('legacy_archive', kwargs['population_policy'])
        self.assertEqual('sheltered', kwargs['survival_regime'])
        self.assertEqual('real_rotation_probe_v1', result['protocol'])

    def test_weather_requires_actual_extra_damage_and_exact_duplicate(self):
        self.assertEqual('REFUSE', instrument.summarize_weather(weather_results(), inputs())['verdict'])
        good = weather_results(extra=1)
        result = instrument.summarize_weather(good, inputs())
        self.assertEqual('QUALIFIED_MECHANISM', result['verdict'])
        self.assertEqual(10, result['total_first_cycle_difference'])
        good[-1]['report']['drift'] = True
        self.assertEqual('REFUSE', instrument.summarize_weather(good, inputs())['verdict'])

    def test_weather_refuses_different_bodies_and_missing_or_reordered_cases(self):
        rows = weather_results(extra=1)
        rows[1]['observations'][0]['candidate_grid']['grid_id'] = 'changed'
        self.assertEqual('REFUSE', instrument.summarize_weather(rows, inputs())['verdict'])
        for bad in (rows[:-1], rows[::-1]):
            with self.assertRaises(ValueError): instrument.summarize_weather(bad, inputs())

    def test_weather_rejects_synthetic_seed_or_removed_count_inconsistency(self):
        for field in ('damage_seed', 'removed_cell_count'):
            rows = weather_results(extra=1)
            rows[1]['observations'][0]['cycles'][0][field] += 1
            with self.assertRaises(ValueError): instrument.summarize_weather(rows, inputs())

    def test_weather_aggregate_refuses_relabelled_payload_config_density_and_rotation(self):
        def report_seed(row): row['report']['rng_seed'] += 1
        def config(row): row['report']['ticks'] = 8
        def density(row): row['report']['cubff_pressure']['density_pressure'] = True
        def rotation(row): row['ordered_weather_sha256'] = 'wrong'
        def observation_seed(row):
            row['observations'][0]['run_seed'] += 1
            row['observations'][0]['cycles'][0]['damage_seed'] += 10
        for change in (report_seed, config, density, rotation):
            rows = weather_results(extra=1); change(rows[0])
            with self.subTest(change=change.__name__), self.assertRaises(ValueError):
                instrument.summarize_weather(rows, inputs())
        rows = weather_results(extra=1)
        observation_seed(rows[0]); observation_seed(rows[1])
        self.assertEqual('REFUSE', instrument.summarize_weather(rows, inputs())['verdict'])

    def test_source_manifest_detects_drift_and_requires_instrument_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); path = root / 'instrument.py'; path.write_text('first')
            with patch.object(instrument, 'ROOT', root), patch.object(instrument, '__file__', str(path)):
                manifest = {'files': {'instrument.py': instrument.file_digest(path)}}
                instrument.verify_sources(manifest)
                path.write_text('second')
                with self.assertRaises(ValueError): instrument.verify_sources(manifest)
                with self.assertRaises(ValueError): instrument.verify_sources({'files': {'other': 'x'}})

    def test_receipts_are_exclusive(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'receipt.json'
            instrument._exclusive_json(path, {'first': True})
            with self.assertRaises(FileExistsError): instrument._exclusive_json(path, {'replacement': True})
            self.assertEqual({'first': True}, json.loads(path.read_text()))

    def test_wrong_frozen_input_hash_keeps_failure_receipt_without_simulation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root / 'inputs.json'; source.write_text('{}')
            manifest = root / 'source.json'
            relative = Path(instrument.__file__).resolve().relative_to(instrument.ROOT).as_posix()
            manifest.write_text(json.dumps({'files': {relative: instrument.file_digest(Path(instrument.__file__))}}))
            output = root / 'trial'
            with patch.object(instrument, '_engine') as engine, self.assertRaises(ValueError):
                instrument.main(['--inputs', str(source), '--inputs-sha256', 'wrong',
                    '--source-manifest', str(manifest), '--kind', 'role', '--output-dir', str(output)])
            engine.assert_not_called()
            self.assertTrue((output / 'worker-start.json').is_file())
            self.assertTrue((output / 'worker-error.json').is_file())
            self.assertFalse((output / 'result.json').exists())

    def test_role_aggregate_retains_failures_and_requires_new_admission_and_zero_duplicate_noise(self):
        engine, source, results = self.role_results()
        with patch.object(instrument, '_engine', return_value=engine):
            result = instrument.summarize_roles(results, source)
            self.assertEqual('QUALIFIED_AUTHORITY', result['verdict'])
            self.assertEqual('NOT_EVALUATED', result['native_earned_permission_gate'])
            self.assertEqual(30, result['generation_rejections'])
            self.assertEqual(['0'], result['newly_admitted_ornament'])
            self.assertEqual(48, len(result['newly_admitted_effect']))
            results[-1]['generation'] = {'accepted': False, 'error_type': 'ValueError', 'error': 'changed'}
            self.assertEqual('REFUSE', instrument.summarize_roles(results, source)['verdict'])

    def role_results(self):
        source = inputs(); engine = fake_engine()
        for index, grid in enumerate(source['seed_grids']):
            grid['organs'] = {'part': {'role': ('locomotion', 'ornament', 'effect')[min(index, 2)]}}
        engine.is_grid_aligned.side_effect = lambda grid, profile: SimpleNamespace(
            ok={organ['role'] for organ in grid['organs'].values()} <= set(profile['grid']['allowed_organ_roles']), errors=[])
        profiles = [instrument._roles_profile(source['slip_profile'], level) for level in range(3)]
        inventory = [dict(level=level, allowed_roles=list(instrument.ROLES[:4 + level]),
                         rows=[dict(grid_id=grid['grid_id'], **instrument._judgment(engine, grid, profile))
                               for grid in source['seed_grids']]) for level, profile in enumerate(profiles)]
        results = [dict(case_index=index, case=case, inputs_sha256=instrument.digest(source),
                        parent_grid=source['seed_grids'][0], profile=profiles[case['level']], inventory=copy.deepcopy(inventory),
                        generation={'accepted': False, 'error_type': 'ValueError', 'error': 'retained'}, repair=None)
                   for index, case in enumerate(instrument.role_plan())]
        return engine, source, results

    def test_role_aggregate_derives_permissions_from_actual_bodies_and_frozen_corpus(self):
        engine, source, results = self.role_results()
        candidate = copy.deepcopy(source['seed_grids'][0])
        output = dict(grid=candidate, **instrument._judgment(engine, candidate, results[0]['profile']))
        output['grid']['organs']['forbidden'] = {'role': 'effect'}
        results[0]['generation'] = output
        with patch.object(instrument, '_engine', return_value=engine), self.assertRaises(ValueError):
            instrument.summarize_roles(results, source)
        engine, source, results = self.role_results()
        results[0]['inventory'][0]['rows'][0]['grid_sha256'] = 'wrong'
        with patch.object(instrument, '_engine', return_value=engine), self.assertRaises(ValueError):
            instrument.summarize_roles(results, source)

    def test_historical_density_mismatch_is_retained_without_rewriting_reference(self):
        def record(identity, phase, off, on):
            return dict(snapshot_id=identity, epoch=1, phase=phase, off=off, on=on,
                        replication_scores=[], lineage_events=[])
        real = [record('early', 'early_phase', [.1, .5], [.2, .6]),
                record('late', 'post_takeover', [.1, .5], [.5, 1.0])]
        callback = [record('early-cb', 'early_phase', [.2, .6], [.3, .7]),
                    record('late-cb', 'post_takeover', [.6, 1.1], [.7, 1.2])]
        def features(snapshot, include_density=False):
            value = dict(replication_rate=0, lineage_churn=0)
            if include_density:
                value.update(instruction_density=9, organization_ratio=3.6, organization_signal=.1)
            return value
        engine = SimpleNamespace(extract_cubff_features=features,
            _cubff_generation_pressure=lambda row, density_pressure=False:
                row['on' if density_pressure else 'off'])
        historical = dict(metrics={'preserved_mismatch': True}, decision=dict(
            g1_inversion_corrected=True, g2_agrees_with_callback_ground_truth=True,
            g5_within_documented_band=True))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative, value in ((instrument.REFERENCE, historical),
                                    (instrument.REAL_SOURCE, {'ingested_snapshots': real}),
                                    (instrument.CALLBACK_SOURCE, {'records': callback})):
                path = root / relative; path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(value))
            source = {'weather_sources': {'real': real, 'callback': callback}}
            before = (root / instrument.REFERENCE).read_bytes()
            with patch.object(instrument, 'ROOT', root), patch.object(instrument, '_engine', return_value=engine):
                result = instrument.density_reference(source)
            self.assertEqual('REFUSE', result['verdict'])
            self.assertFalse(result['historical_metrics_exact'])
            self.assertEqual(.4, result['metrics']['inversion_on'])
            self.assertTrue(all(result['gates'].values()))
            self.assertEqual(before, (root / instrument.REFERENCE).read_bytes())


if __name__ == '__main__': unittest.main()
