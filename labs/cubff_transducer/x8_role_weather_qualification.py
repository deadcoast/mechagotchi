"""Bounded single-case X8 role/weather instrument; only the owner launches it.

Contract: docs/development/cycle-38-surviving-populations.md. No training,
automatic retry, seed search, or aggregate publication occurs here. The parent
watchdog owns the 120-second child limit and the shared 1,200-second budget.
Imports/model loading and all work below occur inside that measured child.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
SEEDS = tuple(range(20260700, 20260710))
ROLES = ('body_core', 'sensor', 'expression', 'locomotion', 'ornament', 'effect')
PARENT_ID = 'mg_seed16_001_beetle'
REFERENCE = 'data/game_client/density_pressure_stage0.json'
REAL_SOURCE = 'data/cubff_real_ingest/real_snapshot_ingest_stage0_report.json'
CALLBACK_SOURCE = 'data/cubff_real_ingest/callback_states/callback_states_compact.json'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def file_digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def role_plan():
    cases = [dict(seed=seed, level=level, duplicate_of=None)
             for seed in SEEDS for level in range(3)]
    return cases + [dict(seed=SEEDS[0], level=0, duplicate_of=0)]


def weather_plan():
    cases = [dict(seed=seed, density=density, rotation=ordinal, duplicate_of=None)
             for ordinal, seed in enumerate(SEEDS) for density in (False, True)]
    return cases + [dict(seed=SEEDS[0], density=False, rotation=0, duplicate_of=0)]


def selected_case(plan, index):
    if type(index) is not int or not 0 <= index < len(plan):
        raise ValueError('case index is outside the frozen plan')
    return copy.deepcopy(plan[index])


def _engine():
    source = str(ROOT / 'packages/mecha_engine/src')
    if source not in sys.path:
        sys.path.insert(0, source)
    from mecha_engine.generation import GenerationModel, generate_candidate
    from mecha_engine.genome import validate_grid
    from mecha_engine.slip import validate_slip, is_grid_aligned
    from mecha_engine.repair import repair_wound_sites
    from mecha_engine.repair._damage import apply_stochastic_damage
    from mecha_engine.runtime import evolve
    from mecha_engine.runtime._readability import learned_readability_score
    from mecha_engine.runtime._cubff import extract_cubff_features
    from mecha_engine.runtime.evolve import _cubff_generation_pressure
    return SimpleNamespace(**locals())


def _roles_profile(base, level):
    profile = copy.deepcopy(base)
    profile['grid']['allowed_organ_roles'] = list(ROLES[:4 + level])
    return profile


def _judgment(engine, grid, profile):
    validity = engine.validate_grid(grid)
    alignment = engine.is_grid_aligned(grid, profile)
    return dict(valid=validity.ok, aligned=alignment.ok,
                accepted=validity.ok and alignment.ok,
                validity_errors=validity.errors, alignment_errors=alignment.errors,
                organ_roles=sorted({organ['role'] for organ in grid['organs'].values()}),
                grid_sha256=digest(grid))


def role_case(inputs, case_index):
    """One frozen generation and (if admitted) one actual wound repair."""
    case = selected_case(role_plan(), case_index)
    original = digest(inputs)
    engine = _engine()
    grids = inputs['seed_grids']
    if len(grids) != 50 or 'allowed_organ_roles' in inputs['slip_profile']['grid']:
        raise ValueError('role probe requires the frozen 50-grid unrestricted cohort')
    parents = [grid for grid in grids if grid['grid_id'] == PARENT_ID]
    if len(parents) != 1:
        raise ValueError('the registered beetle parent must occur exactly once')
    parent = parents[0]
    profiles = [_roles_profile(inputs['slip_profile'], level) for level in range(3)]
    inventory = []
    for level, profile in enumerate(profiles):
        if not engine.validate_slip(profile).ok or not _judgment(engine, parent, profile)['accepted']:
            raise ValueError('registered parent/profile preflight refused; no fallback parent')
        inventory.append(dict(level=level, allowed_roles=list(ROLES[:4 + level]),
                              rows=[dict(grid_id=grid['grid_id'], **_judgment(engine, grid, profile))
                                    for grid in grids]))
    profile = profiles[case['level']]
    result = dict(format='x8_role_trial_v1', case_index=case_index, case=case,
                  inputs_sha256=original, parent_grid=copy.deepcopy(parent),
                  profile=profile, inventory=inventory, generation=None, repair=None)
    try:
        candidate = engine.generate_candidate(copy.deepcopy(parent),
                    engine.GenerationModel(**copy.deepcopy(inputs['generation_model'])),
                    profile, rng_seed=case['seed'], mutation_arm='legacy')
    except ValueError as error:
        result['generation'] = dict(accepted=False, error_type=type(error).__name__, error=str(error))
    else:
        result['generation'] = dict(grid=candidate, **_judgment(engine, candidate, profile))
        if result['generation']['accepted']:
            damage_seed = case['seed'] * 10 + 1
            damaged = engine.apply_stochastic_damage(candidate, dropout_rate=.2,
                                                     rng_seed=damage_seed, event_index=1)
            repaired = engine.repair_wound_sites(damaged, copy.deepcopy(inputs['repair_model']),
                                                 validity_guard=True, slip_profile=profile)
            result['repair'] = dict(damage_seed=damage_seed, dropout_rate=.2,
                                   damaged_grid=damaged, grid=repaired,
                                   **_judgment(engine, repaired, profile))
    if digest(inputs) != original:
        raise RuntimeError('role trial mutated its frozen inputs')
    return result


def weather_case(inputs, case_index):
    """One fixed real-source exposure; no unregistered seed/rotation overrides."""
    case = selected_case(weather_plan(), case_index)
    original = digest(inputs)
    engine = _engine()
    records = inputs['weather_sources']['real']
    if not records:
        raise ValueError('real weather must be nonempty')
    offset = case['rotation'] % len(records)
    rotated = copy.deepcopy(records[offset:] + records[:offset])
    observations = []
    config = dict(generations=1, population=16, damage_cycles=2, ticks=16,
                  dropout_rate=.2, rng_seed=case['seed'], founder_grids=None,
                  cubff_density_pressure=case['density'], population_policy='legacy_archive',
                  founder_start_mode='bootstrap', survival_regime='sheltered', care_selection_policy='off')
    archive, report = engine.evolve(
        copy.deepcopy(inputs['seed_grids']), copy.deepcopy(inputs['slip_profile']),
        engine.GenerationModel(**copy.deepcopy(inputs['generation_model'])),
        copy.deepcopy(inputs['repair_model']),
        readability_scorer=lambda grid: engine.learned_readability_score(grid, inputs['legibility_model']),
        readability_selection=copy.deepcopy(inputs['readability_selection']),
        cubff_pressure_source=rotated, **config,
        evaluation_callback=observations.append)
    if digest(inputs) != original:
        raise RuntimeError('weather trial mutated its frozen inputs')
    return dict(format='x8_weather_trial_v1', protocol='real_rotation_probe_v1',
                case_index=case_index, case=case, inputs_sha256=original, effective_config=config,
                ordered_weather_sha256=digest(rotated), archive=archive, report=report,
                observations=observations)


def _phase_means(rows, suffix):
    return {phase: round(sum(row['dropout_multiplier_' + suffix] for row in rows
                             if row['phase'] == phase) /
                         sum(row['phase'] == phase for row in rows), 6)
            for phase in ('early_phase', 'post_takeover')}


def density_reference(inputs):
    """Reproduce DR0045 on original sources; a mismatch stays a refusal."""
    original = digest(inputs)
    engine = _engine()
    reference = json.loads((ROOT / REFERENCE).read_bytes())
    real = sorted(json.loads((ROOT / REAL_SOURCE).read_bytes())['ingested_snapshots'],
                  key=lambda row: row['epoch'])
    callback = sorted(json.loads((ROOT / CALLBACK_SOURCE).read_bytes())['records'],
                      key=lambda row: row['epoch'])
    if real != inputs['weather_sources']['real'] or callback != inputs['weather_sources']['callback']:
        raise ValueError('frozen weather differs from original committed records')
    source_hashes = {path: file_digest(ROOT / path) for path in (REFERENCE, REAL_SOURCE, CALLBACK_SOURCE)}
    rows_by_source = {}
    observations = []
    for source_name, records in (('checkpoint', real), ('callback', callback)):
        rows = []
        for record in records:
            off = engine._cubff_generation_pressure(record)
            explicit_off = engine._cubff_generation_pressure(record, density_pressure=False)
            duplicate_off = engine._cubff_generation_pressure(record, density_pressure=False)
            on = engine._cubff_generation_pressure(record, density_pressure=True)
            features_off = engine.extract_cubff_features(record)
            features_on = engine.extract_cubff_features(record, include_density=True)
            rows.append(dict(snapshot_id=record['snapshot_id'], epoch=record['epoch'], phase=record['phase'],
                instruction_density=features_on['instruction_density'],
                organization_ratio=features_on['organization_ratio'],
                organization_signal=features_on['organization_signal'],
                mutation_pressure_off=off[0], mutation_pressure_on=on[0],
                dropout_multiplier_off=off[1], dropout_multiplier_on=on[1]))
            observations.append(dict(source=source_name, snapshot_id=record['snapshot_id'],
                snapshot_sha256=digest(record), off_matches_omitted=off == explicit_off,
                duplicate_identical=explicit_off == duplicate_off,
                existing_features_unchanged=features_off == {key: features_on[key] for key in features_off},
                absent_replication_unchanged=bool(record.get('replication_scores')) or
                    features_off['replication_rate'] == features_on['replication_rate'] == 0,
                absent_lineage_unchanged=bool(record.get('lineage_events')) or
                    features_off['lineage_churn'] == features_on['lineage_churn'] == 0,
                effective_dropout_off=round(.2 * off[1], 6),
                effective_dropout_on=round(.2 * on[1], 6)))
        rows_by_source[source_name] = rows
    metrics = dict(checkpoint_per_snapshot=rows_by_source['checkpoint'], callback_per_snapshot=rows_by_source['callback'])
    for key, source, suffix in (('checkpoint_phase_means_off', 'checkpoint', 'off'),
                                ('checkpoint_phase_means_on', 'checkpoint', 'on'),
                                ('callback_phase_means_off', 'callback', 'off')):
        metrics[key] = _phase_means(rows_by_source[source], suffix)
    for suffix in ('off', 'on'):
        means = metrics['checkpoint_phase_means_' + suffix]
        metrics['inversion_' + suffix] = round(means['post_takeover'] - means['early_phase'], 6)
    callback_means = metrics['callback_phase_means_off']
    metrics['callback_ground_truth_direction'] = ('post_takeover_harsher'
        if callback_means['post_takeover'] > callback_means['early_phase'] else 'post_takeover_not_harsher')
    all_rows = rows_by_source['checkpoint'] + rows_by_source['callback']
    gates = dict(g1_inversion_corrected=metrics['inversion_on'] > 0,
                 g2_agrees_with_callback_ground_truth=metrics['inversion_on'] > 0 and
                    callback_means['post_takeover'] > callback_means['early_phase'],
                 g3_off_and_duplicate_parity=all(row['off_matches_omitted'] and row['duplicate_identical']
                                                 for row in observations),
                 g4_no_silent_channel_synthesis=all(row['absent_replication_unchanged'] and
                    row['absent_lineage_unchanged'] and row['existing_features_unchanged'] for row in observations),
                 g5_within_documented_band=all(.5 <= row['dropout_multiplier_' + suffix] <= 1.6
                                              for row in all_rows for suffix in ('off', 'on')))
    historical_decisions_match = all(gates[key] == reference['decision'][key]
        for key in ('g1_inversion_corrected', 'g2_agrees_with_callback_ground_truth', 'g5_within_documented_band'))
    directional = all(row['dropout_multiplier_on'] >= row['dropout_multiplier_off'] for row in all_rows)
    positive = any(row['effective_dropout_on'] > row['effective_dropout_off'] for row in observations)
    unchanged = source_hashes == {path: file_digest(ROOT / path) for path in source_hashes} and digest(inputs) == original
    matched = metrics == reference['metrics'] and historical_decisions_match
    return dict(format='x8_density_reference_v1', metrics=metrics, gates=gates, observations=observations,
                source_hashes=source_hashes, inputs_sha256=original, historical_metrics_exact=matched,
                source_inputs_unchanged=unchanged, nonnegative_multiplier_deltas=directional,
                positive_effective_dropout_delta=positive,
                verdict='MATCH' if matched and unchanged and directional and positive and all(gates.values()) else 'REFUSE')


def _first_cycle(observation):
    cycle = observation['cycles'][0]
    sites = cycle['frames']['removed_cells']
    if cycle['cycle'] != 1 or cycle['damage_seed'] != observation['run_seed'] * 10 + 1:
        raise ValueError('first-cycle observation has inconsistent seed or ordinal')
    if cycle['removed_cell_count'] != len(sites):
        raise ValueError('actual removed-site count differs from cycle count')
    return dict(generation_index=observation['generation_index'], candidate_index=observation['candidate_index'],
                run_seed=observation['run_seed'], candidate_grid=observation['candidate_grid'],
                damage_seed=cycle['damage_seed']), len(sites)


def _weather_plan_binding(result, inputs):
    case = result['case']
    config = dict(generations=1, population=16, damage_cycles=2, ticks=16,
                  dropout_rate=.2, rng_seed=case['seed'], founder_grids=None,
                  cubff_density_pressure=case['density'], population_policy='legacy_archive',
                  founder_start_mode='bootstrap', survival_regime='sheltered', care_selection_policy='off')
    if result.get('effective_config') != config or result['inputs_sha256'] != digest(inputs):
        raise ValueError('weather result does not bind the frozen execution inputs')
    report = result['report']
    for report_key, config_key in (('rng_seed', 'rng_seed'), ('generations_requested', 'generations'),
                                    ('population', 'population'), ('damage_cycles', 'damage_cycles'),
                                    ('ticks', 'ticks'), ('dropout_rate', 'dropout_rate')):
        if report.get(report_key) != config[config_key]:
            raise ValueError('weather report differs from planned ' + report_key)
    if ('living_population' in report or report.get('survival_regime', 'sheltered') != 'sheltered'
            or 'care_selection' in report):
        raise ValueError('weather report uses an unregistered policy/regime/care path')
    weather = inputs['weather_sources']['real']
    offset = case['rotation'] % len(weather)
    ordered = weather[offset:] + weather[:offset]
    pressure = report['cubff_pressure']
    if (result['ordered_weather_sha256'] != digest(ordered) or
            pressure.get('density_pressure', False) is not case['density'] or
            pressure['source_snapshot_count'] != len(weather) or
            len(pressure['by_generation']) != 1 or
            pressure['by_generation'][0]['snapshot_id'] != ordered[0]['snapshot_id']):
        raise ValueError('weather report differs from planned density or ordered source')
    generations = report['generations']
    if len(generations) != 1 or generations[0]['generation'] != 0 or len(generations[0]['creatures']) != 16:
        raise ValueError('weather report must contain the complete one-generation exposure')
    for index, observation in enumerate(result['observations']):
        if (observation['creature'] != generations[0]['creatures'][index] or
                observation['generation_weather'] != pressure['by_generation'][0] or
                observation['effective_dropout_rate'] != round(.2 * pressure['by_generation'][0]['dropout_multiplier'], 6)):
            raise ValueError('weather observation differs from its actual report')


def summarize_weather(results, inputs):
    """Pure aggregate; missing cases and nonzero duplicates cannot qualify."""
    plan = weather_plan()
    if len(results) != len(plan) or any(row['case_index'] != index or row['case'] != plan[index]
                                      for index, row in enumerate(results)):
        raise ValueError('weather aggregate requires all 21 cases in registered order')
    if len({row['inputs_sha256'] for row in results}) != 1:
        raise ValueError('weather cases differ in frozen inputs')
    for result in results:
        _weather_plan_binding(result, inputs)
    fields = ('archive', 'report', 'observations', 'ordered_weather_sha256')
    duplicate_exact = all(results[0][key] == results[-1][key] for key in fields)
    pairs = []
    for ordinal, seed in enumerate(SEEDS):
        off, on = results[ordinal * 2:ordinal * 2 + 2]
        off_rows, on_rows = off['observations'], on['observations']
        complete = len(off_rows) == len(on_rows) == 16
        comparable = complete
        off_removed = on_removed = 0
        for candidate_index, (left, right) in enumerate(zip(off_rows, on_rows)):
            left_identity, left_removed = _first_cycle(left)
            right_identity, right_removed = _first_cycle(right)
            comparable &= left_identity == right_identity
            comparable &= (left_identity['generation_index'] == 0 and
                           left_identity['candidate_index'] == candidate_index and
                           left_identity['run_seed'] == seed + candidate_index)
            off_removed += left_removed
            on_removed += right_removed
        pairs.append(dict(seed=seed, complete=complete, candidate_bodies_and_seeds_equal=comparable,
                          first_cycle_removed_off=off_removed, first_cycle_removed_on=on_removed,
                          difference=on_removed - off_removed))
    comparable = all(row['candidate_bodies_and_seeds_equal'] for row in pairs)
    total_difference = sum(row['difference'] for row in pairs)
    qualified = duplicate_exact and comparable and total_difference > 0
    return dict(format='x8_weather_summary_v1', pairs=pairs, duplicate_exact=duplicate_exact,
                candidate_bodies_and_seeds_equal=comparable, total_first_cycle_difference=total_difference,
                no_aggregate_reduction=total_difference >= 0, at_least_one_extra_removed_cell=total_difference > 0,
                verdict='QUALIFIED_MECHANISM' if qualified else 'REFUSE',
                claim='Modeled first-cycle damage directionality; no survival-benefit claim.')


def _role_plan_binding(result, inputs, engine):
    case = result['case']
    profiles = [_roles_profile(inputs['slip_profile'], level) for level in range(3)]
    if result['inputs_sha256'] != digest(inputs) or result['profile'] != profiles[case['level']]:
        raise ValueError('role result differs from the frozen profile/inputs')
    parents = [grid for grid in inputs['seed_grids'] if grid['grid_id'] == PARENT_ID]
    if len(parents) != 1 or result['parent_grid'] != parents[0]:
        raise ValueError('role result differs from the registered parent')
    expected_inventory = [dict(level=level, allowed_roles=list(ROLES[:4 + level]),
        rows=[dict(grid_id=grid['grid_id'], **_judgment(engine, grid, profile)) for grid in inputs['seed_grids']])
        for level, profile in enumerate(profiles)]
    if result['inventory'] != expected_inventory:
        raise ValueError('role inventory differs from actual frozen corpus judgments')
    for stage in ('generation', 'repair'):
        output = result[stage]
        if output is None:
            if stage == 'generation' or result['generation']['accepted']:
                raise ValueError('role result omits a required attempted stage')
            continue
        if 'grid' not in output:
            if (stage != 'generation' or output.get('accepted') is not False or
                    output.get('error_type') != 'ValueError' or not isinstance(output.get('error'), str)):
                raise ValueError('role output lacks the body or an explicit generation refusal')
            continue
        judgment = _judgment(engine, output['grid'], profiles[case['level']])
        if any(output.get(key) != value for key, value in judgment.items()):
            raise ValueError('role output judgment differs from its actual genome')
        if stage == 'repair' and (output.get('damage_seed') != case['seed'] * 10 + 1 or
                                  output.get('dropout_rate') != .2 or 'damaged_grid' not in output):
            raise ValueError('role repair differs from registered exposure')


def summarize_roles(results, inputs):
    """Authority/output gate only; earned native permissions remain separate."""
    plan = role_plan()
    if len(results) != len(plan) or any(row['case_index'] != index or row['case'] != plan[index]
                                      for index, row in enumerate(results)):
        raise ValueError('role aggregate requires all 31 cases in registered order')
    if len({row['inputs_sha256'] for row in results}) != 1:
        raise ValueError('role cases differ in frozen inputs')
    engine = _engine()
    for result in results:
        _role_plan_binding(result, inputs, engine)
    fields = ('parent_grid', 'profile', 'inventory', 'generation', 'repair')
    duplicate_exact = all(results[0][key] == results[-1][key] for key in fields)
    inventory = results[0]['inventory']
    if len(inventory) != 3 or any(len(stage['rows']) != 50 for stage in inventory):
        raise ValueError('role inventory must retain all 50 rows at every stage')
    inventory_identical = all(row['inventory'] == inventory for row in results)
    admitted = [{row['grid_id'] for row in stage['rows'] if row['accepted']} for stage in inventory]
    new_ids = [sorted(admitted[level] - admitted[level - 1]) for level in (1, 2)]
    permissions_hold = all(not row['accepted'] or set(row['organ_roles']) <= set(ROLES[:4 + level])
        for level, stage in enumerate(inventory) for row in stage['rows'])
    permissions_hold &= all(output is None or not output['accepted'] or
        set(output['organ_roles']) <= set(ROLES[:4 + trial['case']['level']])
        for trial in results for output in (trial['generation'], trial['repair']))
    trials = results[:-1]
    generations = sum(row['generation']['accepted'] for row in trials)
    repairs = [row['repair'] for row in trials if row['repair'] is not None]
    qualified = (duplicate_exact and inventory_identical and permissions_hold and
                 all(admitted) and all(new_ids))
    return dict(format='x8_role_summary_v1', duplicate_exact=duplicate_exact,
                inventory_identical=inventory_identical, permissions_hold=permissions_hold,
                viable_admissions_by_stage=[len(value) for value in admitted],
                newly_admitted_ornament=new_ids[0], newly_admitted_effect=new_ids[1],
                generation_attempts=30, generations_accepted=generations,
                generation_rejections=30 - generations, repair_attempts=len(repairs),
                repairs_accepted=sum(row['accepted'] for row in repairs),
                repair_rejections=sum(not row['accepted'] for row in repairs),
                verdict='QUALIFIED_AUTHORITY' if qualified else 'REFUSE',
                native_earned_permission_gate='NOT_EVALUATED',
                claim='Modeled role admissibility; no survival or biological adaptation claim.')


def verify_sources(manifest):
    files = manifest.get('files')
    if not isinstance(files, dict) or not files:
        raise ValueError('source manifest requires a nonempty files mapping')
    if Path(__file__).resolve().relative_to(ROOT).as_posix() not in files:
        raise ValueError('source manifest must bind this instrument')
    for relative, expected in files.items():
        path = (ROOT / relative).resolve()
        if not path.is_relative_to(ROOT) or file_digest(path) != expected:
            raise ValueError('source identity mismatch: ' + relative)


def _exclusive_json(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def main(argv=None):
    started = time.perf_counter()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--inputs-sha256', required=True)
    parser.add_argument('--source-manifest', type=Path, required=True)
    parser.add_argument('--kind', choices=('role', 'weather', 'density-reference'), required=True)
    parser.add_argument('--case-index', type=int, default=0)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest_identity = file_digest(args.source_manifest)
    _exclusive_json(args.output_dir / 'worker-start.json', dict(format='x8_role_weather_worker_v1',
        started_utc=datetime.now(timezone.utc).isoformat(), monotonic_started=started,
        kind=args.kind, case_index=args.case_index, inputs=str(args.inputs),
        inputs_sha256=args.inputs_sha256, source_manifest=str(args.source_manifest),
        source_manifest_sha256=manifest_identity,
        parent_enforced_trial_bound_seconds=120, parent_enforced_global_bound_seconds=1200))
    try:
        manifest_raw = args.source_manifest.read_bytes()
        if hashlib.sha256(manifest_raw).hexdigest() != manifest_identity:
            raise ValueError('source manifest changed after worker start')
        manifest = json.loads(manifest_raw)
        verify_sources(manifest)
        raw = args.inputs.read_bytes()
        if hashlib.sha256(raw).hexdigest() != args.inputs_sha256:
            raise ValueError('frozen input byte digest mismatch')
        inputs = json.loads(raw)
        if args.kind == 'density-reference':
            if args.case_index != 0:
                raise ValueError('density reference has exactly one registered case')
            result = density_reference(inputs)
        else:
            result = (role_case if args.kind == 'role' else weather_case)(inputs, args.case_index)
        verify_sources(manifest)
        if args.source_manifest.read_bytes() != manifest_raw or args.inputs.read_bytes() != raw:
            raise ValueError('input or manifest changed during trial')
        _exclusive_json(args.output_dir / 'result.json', result)
        _exclusive_json(args.output_dir / 'worker-finish.json', dict(status='completed',
            elapsed_seconds=time.perf_counter() - started,
            source_manifest_sha256=hashlib.sha256(manifest_raw).hexdigest(),
            result_sha256=file_digest(args.output_dir / 'result.json')))
    except Exception as error:
        _exclusive_json(args.output_dir / 'worker-error.json', dict(status='error',
            elapsed_seconds=time.perf_counter() - started, error_type=type(error).__name__,
            error=str(error), traceback=traceback.format_exc()))
        raise


if __name__ == '__main__':
    main()
