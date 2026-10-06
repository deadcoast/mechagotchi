"""Preregistered single-stage workload instrument, never an automatic trial loop.

Only the integrator launches workers through body_workload_coordinator. The
worker freezes actual input payloads, verifies prerequisite/source identities,
and records every started/terminal attempt. Synthetic causal fixtures are not
held-out outcome evidence. All earlier refusals remain intact.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
FORMAT = 'body_workload_instrument_v1'
INPUT_FORMAT = 'body_workload_inputs_v1'
CONTRACT = 'docs/development/cycle-38-body-workload.md'
MODEL = 'workload-v1'
EVALUATORS = ('pristine', 'archive_morphology_probe_v1')
CARE_SEEDS = (20261107, 20261117, 20261127)
FOUNDERS = tuple(range(20, 30))
PRODUCTION_SEEDS = (20261130, 20261201, 20261202)
CONFIG = dict(generations=6, population=16, damage_cycles=2, ticks=16, dropout_rate=.2)
PRODUCT_PAYLOAD_SHA256 = '4657512d4b271bbd386d786cb5fc210f475038e66b6b011ec36184e9345523ce'
PRODUCT_PATH = 'data/game_client/product_learning_gate_stage1.json'
ORIGINAL_PRODUCT_PAYLOAD_SHA256 = '05d3512573e8066536181c731ce20839748980732f2e46cb0b957c464d495737'
ORIGINAL_PRODUCT_PATH = '.development/x7/learning/manifest.json'
REPAIR_CONTRACT = 'docs/development/cycle-38-body-workload-instrument-repair.md'
PRODUCT_CORE_FIELDS = ('founders', 'covenant', 'admissions', 'source_corpus', 'hatch_seed', 'plan', 'budgets')
PRODUCTION_PATH = '.development/x8/study/setup/inputs.json'
LEGACY_INPUT_PATH = 'data/game_client/observed_care_inputs_stage0.json'
LEGACY_V1_PATH = 'data/game_client/observed_care_selection_stage0.json'
LEGACY_V2_PATH = '.development/x7-v2/care/study/regression.json'
FROZEN_PATHS = (CONTRACT, REPAIR_CONTRACT, PRODUCT_PATH, ORIGINAL_PRODUCT_PATH, PRODUCTION_PATH, LEGACY_INPUT_PATH,
                LEGACY_V1_PATH, LEGACY_V2_PATH)
PAIR_CHECKS = frozenset(('off_exact', 'absent_exact', 'empty_exact',
                        'input_immutable', 'founder_identity', 'frozen_pool_exact'))
TRIAL_CHECKS = frozenset(('package_repeat', 'lab_mirror', 'metadata_negative',
    'same_candidate_bytes', 'welfare_nonregression', 'survival_nonregression',
    'terminal_nonregression', 'live_option_selected', 'pristine_child_exact',
    'source_identity', 'trajectory_consistent', 'cold_start', 'product_receipt_loadable',
    'body_response_bound'))
CARE_CHECKS = frozenset(name+'_'+check for name in ('fed', 'neglect') for check in TRIAL_CHECKS)
SCIENTIFIC_CHECKS = frozenset(name+'_'+check+'_nonregression'
    for name in ('fed', 'neglect') for check in ('welfare', 'survival', 'terminal'))
CAUSAL_CHECKS = frozenset(('input_immutable', 'fixture_valid', 'same_initial_physiology',
    'native_play_divergence', 'native_no_play_null', 'native_repeat',
    'legacy_play_null', 'repair_position_restoration', 'repair_changed_projection',
    'repair_restored_projection_null', 'repair_consumed_projection',
    'repair_play_response_changed', 'repair_play_response_null',
    'legacy_v1_exact', 'legacy_v2_exact'))


def imports():
    for relative in ('packages/mecha_engine/src', 'game/src', 'labs/runtime_integration'):
        value = str(ROOT / relative)
        if value not in sys.path: sys.path.insert(0, value)


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode('utf-8')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                   allow_nan=False).encode('utf-8')).hexdigest()


def file_digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_bytes())
def utc(): return datetime.now(timezone.utc).isoformat()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream: stream.write(encode(value))


def all_true(checks, names):
    return isinstance(checks, dict) and set(checks) == names and all(checks[key] is True for key in names)


def care_plan():
    return [dict(pair_index=i, founder_index=founder, rng_seed=seed)
            for i, (seed, founder) in enumerate((s, f) for s in CARE_SEEDS for f in FOUNDERS)]


def production_plan():
    return [dict(era_index=i, rng_seed=seed, body_response=response)
            for i, (seed, response) in enumerate((s, r) for s in PRODUCTION_SEEDS for r in ('legacy', MODEL))]


def stage_spec(stage, index=0):
    if type(index) is not int: raise ValueError('stage index must be an integer')
    counts = {'setup':1, 'causal':1, 'care':30, 'production':6, 'reproduce':1, 'duplicate':1, 'analysis':1}
    if stage not in counts or not 0 <= index < counts[stage]:
        raise ValueError('stage outside the fixed registered plan')
    seconds = 30 if stage in ('causal', 'care') else 120 if stage in ('production', 'reproduce', 'duplicate') else 60
    return dict(stage=stage, index=index, seconds=seconds)


def source_snapshot(path):
    manifest = read(path)
    if set(manifest) != {'format', 'files'} or manifest['format'] != 'x8_source_manifest_v1':
        raise ValueError('invalid frozen source closure')
    files = manifest['files']
    required = {*FROZEN_PATHS, 'labs/game_loop/body_workload_gate.py',
                'labs/game_loop/body_workload_coordinator.py',
                'labs/game_loop/body_workload_fixtures.py',
                'labs/game_loop/body_workload_recording.py'}
    for relative in ('packages/mecha_engine/src/mecha_engine', 'game/src/mecha_game',
                     'labs/game_loop', 'labs/runtime_integration', 'labs/lifecycle_sim'):
        required.update(path.relative_to(ROOT).as_posix() for path in (ROOT/relative).rglob('*.py'))
    if not isinstance(files, dict) or not required.issubset(files):
        raise ValueError('source closure omits instrument, contract, or retained inputs')
    for name, expected in files.items():
        path = (ROOT / name).resolve()
        if Path(name).is_absolute() or not path.is_relative_to(ROOT) or file_digest(path) != expected:
            raise ValueError('frozen source or input drift: '+name)
    return files


def causal_fixture():
    imports()
    from body_workload_fixtures import causal_fixture as authored_fixture
    return authored_fixture()


def validate_product_manifest(artifact, original):
    """Pin both retained envelopes and their unchanged scientific inputs, without simulation."""
    product = artifact['input_manifest']
    if digest(product) != PRODUCT_PAYLOAD_SHA256:
        raise ValueError('retained stage1 product manifest payload differs')
    if artifact.get('input_manifest_sha256') != PRODUCT_PAYLOAD_SHA256:
        raise ValueError('declared stage1 product manifest hash differs')
    if digest(original) != ORIGINAL_PRODUCT_PAYLOAD_SHA256:
        raise ValueError('original product manifest payload differs')
    if product.get('instrument_repair', {}).get('prior_manifest_sha256') != ORIGINAL_PRODUCT_PAYLOAD_SHA256:
        raise ValueError('stage1 prior product manifest binding differs')
    if any(encode(product[field]) != encode(original[field]) for field in PRODUCT_CORE_FIELDS):
        raise ValueError('stage1 scientific core differs from original product inputs')
    return product


def freeze_inputs():
    imports()
    from mecha_engine.generation import GenerationModel, generate_candidate
    from mecha_game.session import CompanionSession
    from mecha_game.care_history import capture_care_context
    from observed_care_gate import prefix
    product = validate_product_manifest(read(ROOT / PRODUCT_PATH), read(ROOT / ORIGINAL_PRODUCT_PATH))
    if len(product['founders']) != 50 or any(row.get('founder_index') != i or row.get('status') != 'admitted'
            for i, row in enumerate(product['admissions'])) or len(product['admissions']) != 50:
        raise ValueError('complete original founder admissions required')
    founders = []
    for index in FOUNDERS:
        record = product['founders'][index]; histories = {}
        for name in ('fed', 'neglect'):
            pet = CompanionSession(record['grid'], product['covenant'],
                model=GenerationModel(**record['model']), learning_policy='incumbent', body_response=MODEL)
            for tick in range(1, 13):
                if not pet.alive: break
                pet.advance('feed' if name == 'fed' and tick % 3 == 0 else None)
            histories[name] = capture_care_context(pet)
        count = min(len(ctx['events']) for ctx in histories.values())
        contexts = {name:prefix(ctx, count) for name, ctx in histories.items()}
        if any(ctx.get('body_response') != MODEL for ctx in contexts.values()):
            raise ValueError('actual source history must bind workload-v1')
        founders.append(dict(founder_index=index, grid=record['grid'], model=record['model'],
            original_histories=histories, used_prefix_ticks=count, contexts=contexts))
    pools = []
    for spec in care_plan():
        founder = founders[spec['founder_index']-20]
        pools.append([generate_candidate(founder['grid'], GenerationModel(**founder['model']),
            product['covenant'], rng_seed=spec['rng_seed']+i) for i in range(8)])
    old = read(ROOT / LEGACY_INPUT_PATH)
    legacy = dict(founder=old['founders'][2], covenant=old['covenant'], rng_seed=20260702,
        v1=read(ROOT / LEGACY_V1_PATH)['rows'][22]['evaluators'],
        v2=read(ROOT / LEGACY_V2_PATH)['evaluators'])
    return dict(format=INPUT_FORMAT, body_response=MODEL,
        source_inputs={name:file_digest(ROOT/name) for name in FROZEN_PATHS},
        product_manifest=product, founders=founders, covenant=product['covenant'],
        pools=pools, care_plan=care_plan(), production_plan=production_plan(),
        production=read(ROOT / PRODUCTION_PATH), production_config=CONFIG,
        causal_fixture=causal_fixture(), legacy=legacy)


def validate_inputs(inputs):
    if (inputs.get('format') != INPUT_FORMAT or inputs.get('body_response') != MODEL
            or inputs.get('care_plan') != care_plan() or inputs.get('production_plan') != production_plan()
            or inputs.get('production_config') != CONFIG or len(inputs.get('founders', [])) != 10
            or len(inputs.get('pools', [])) != 30 or any(len(p) != 8 for p in inputs.get('pools', []))):
        raise ValueError('frozen study inputs differ from preregistration')
    retained_product = validate_product_manifest(read(ROOT / PRODUCT_PATH), read(ROOT / ORIGINAL_PRODUCT_PATH))
    if inputs['product_manifest'] != retained_product:
        raise ValueError('retained founder source differs')
    if inputs['production'] != read(ROOT / PRODUCTION_PATH):
        raise ValueError('production payload differs from retained X8 trained inputs')
    if inputs['source_inputs'] != {name:file_digest(ROOT/name) for name in FROZEN_PATHS}:
        raise ValueError('original source inputs changed')
    if inputs['causal_fixture'] != causal_fixture():
        raise ValueError('authored fixture changed from registered construction')
    imports()
    from observed_care_gate import prefix
    for i, row in enumerate(inputs['founders']):
        original = inputs['product_manifest']['founders'][i+20]
        if row['founder_index'] != i+20 or row['grid'] != original['grid'] or row['model'] != original['model']:
            raise ValueError('founder order or payload differs')
        if set(row['contexts']) != {'fed', 'neglect'} or any(c.get('body_response') != MODEL for c in row['contexts'].values()):
            raise ValueError('history model identity differs')
        count = min(len(ctx['events']) for ctx in row['original_histories'].values())
        if count != row['used_prefix_ticks'] or row['contexts'] != {
                name:prefix(ctx, count) for name,ctx in row['original_histories'].items()}:
            raise ValueError('matched history prefix differs from actual captured original')
        if any(ctx['grid_id'] != row['grid']['grid_id'] or ctx['grid_sha256'] != digest(row['grid'])
               for ctx in row['original_histories'].values()):
            raise ValueError('original captured history belongs to another founder body')
    if inputs['covenant'] != inputs['product_manifest']['covenant']:
        raise ValueError('care covenant differs from original product inputs')


def physiology(value):
    """Remove declared identity/body descriptors, retaining all physiological values."""
    excluded = {'grid_id', 'body_mass', 'body_response', 'body_workload', 'play_energy_cost'}
    if isinstance(value, dict): return {key:physiology(item) for key, item in value.items() if key not in excluded}
    if isinstance(value, list): return [physiology(item) for item in value]
    return value


def causal_trial(inputs):
    imports()
    from mecha_engine.lifecycle import advance_tick, initial_state, run_episode
    from mecha_engine.runtime import live_cycle
    from mecha_engine.runtime.care import CARE_POLICY, CARE_POLICY_V2, select_care_successor
    from mecha_engine.generation import GenerationModel
    from mecha_engine.genome import validate_grid
    from mecha_game.session import CompanionSession
    fixture = inputs['causal_fixture']; before = digest(inputs)
    low, high, slip = fixture['grid'], fixture['contrast_grid'], fixture['covenant']
    def native(grid, actions, response):
        pet = CompanionSession(grid, slip, model=GenerationModel(**fixture['generation_model']),
            fleet=False, learning_policy='incumbent', body_response=response)
        states = [deepcopy(pet.state)]
        for action in actions:
            if not pet.alive: break
            pet.advance(action); states.append(deepcopy(pet.state))
        return states
    traces = {name:{label:native(grid, fixture[name+'_actions'], MODEL)
                   for label, grid in (('low', low), ('high', high))}
              for name in ('play', 'no_play')}
    legacy_traces = {label:native(grid, fixture['play_actions'], 'legacy') for label, grid in (('low', low), ('high', high))}
    repair = {}; repair_direct = {}
    baseline = initial_state(low, slip, body_response=MODEL)['body_workload']
    for name, model in fixture['repair_models'].items():
        repair[name] = live_cycle(low, slip, model, damage_events=[fixture['damage_event']],
            ticks=fixture['repair_ticks'], rng_seed=fixture['rng_seed'], record_frames=True,
            population_policy='generation_survivors_v1', survival_regime='sheltered', body_response=MODEL)
        repaired = repair[name]['cycles'][0]['frames']['repaired_grid']
        projection = initial_state(repaired, slip, body_response=MODEL)['body_workload']
        direct = run_episode(repaired, slip, actions=fixture['play_actions'],
            ticks=len(fixture['play_actions']), body_response=MODEL)
        repair_direct[name] = dict(projection=projection, episode=direct)
    original_direct = run_episode(low, slip, actions=fixture['play_actions'],
        ticks=len(fixture['play_actions']), body_response=MODEL)
    def consumed(name):
        cycle = repair[name]['cycles'][0]; rows = cycle['frames']['episode_history']
        cost = repair_direct[name]['projection']['play_energy_cost']
        state = initial_state(cycle['frames']['repaired_grid'], slip, body_response=MODEL)
        replayed = []
        for row in rows or []:
            state = advance_tick(state, row['action'], row.get('deliberation'))
            replayed.append(deepcopy(state['history'][-1]))
        return rows == replayed and bool(rows) and any(row['action'] == 'play' for row in rows) and all(
            row.get('body_response') == MODEL and row.get('play_energy_cost') == cost
            and (row['action'] != 'play' or row.get('action_energy_effect') == -cost) for row in rows)
    old = inputs['legacy']; old_checks = {}
    for version, policy in (('v1', CARE_POLICY), ('v2', CARE_POLICY_V2)):
        exact = []
        for evaluator in EVALUATORS:
            for name, context in old['founder']['contexts'].items():
                result = select_care_successor(old['founder']['grid'], GenerationModel(**old['founder']['model']),
                    old['covenant'], context=context, rng_seed=old['rng_seed'], policy=policy, evaluator=evaluator)
                retained = old[version][evaluator]['trials'][name]
                exact.append(result == (retained['selected_grid'], retained['receipt']))
        old_checks['legacy_'+version+'_exact'] = all(exact)
    checks = dict(input_immutable=before == digest(inputs),
        fixture_valid=validate_grid(low).ok and validate_grid(high).ok,
        same_initial_physiology=physiology(traces['play']['low'][0]) == physiology(traces['play']['high'][0]),
        native_play_divergence=[s['energy'] for s in traces['play']['low']] != [s['energy'] for s in traces['play']['high']],
        native_no_play_null=physiology(traces['no_play']['low']) == physiology(traces['no_play']['high']),
        native_repeat=traces['play']['low'] == native(low, fixture['play_actions'], MODEL),
        legacy_play_null=physiology(legacy_traces['low']) == physiology(legacy_traces['high']),
        repair_position_restoration=all(r['cycles'][0]['position_restoration'] == 1 for r in repair.values()),
        repair_changed_projection=repair_direct['changed']['projection']['functional_capacity'] == baseline['functional_capacity']+1
            and repair_direct['changed']['projection']['occupied_mass'] == baseline['occupied_mass'],
        repair_restored_projection_null=repair_direct['null']['projection'] == baseline,
        repair_consumed_projection=all(consumed(name) for name in repair),
        repair_play_response_changed=repair_direct['changed']['projection']['play_energy_cost'] != baseline['play_energy_cost']
            and [r['state']['energy'] for r in repair_direct['changed']['episode']['history']] != [r['state']['energy'] for r in original_direct['history']],
        repair_play_response_null=physiology(repair_direct['null']['episode']) == physiology(original_direct), **old_checks)
    return dict(checks=checks, traces=traces, legacy_traces=legacy_traces, repair=repair,
                repaired_explicit_play=repair_direct, original_explicit_play=original_direct)


def complete_ranking(receipt):
    rows = receipt['candidates']
    return [r['index'] for r in sorted(rows, key=lambda r:
        (r['terminal_survival'], r['need_balance'], r['survival_ticks'], -r['index']), reverse=True)]


def measure_care(inputs, index):
    imports()
    from mecha_engine.generation import GenerationModel, generate_candidate
    from mecha_engine.runtime.care import CARE_POLICY_V2, select_care_successor, care_structure_sha256
    from mecha_game.care_history import _validate_care_v2_episode, validate_care_selection
    from observed_care_gate import altered_metadata
    from observed_care_selection import select_care_successor as lab_select
    spec = care_plan()[index]; founder = inputs['founders'][spec['founder_index']-20]
    parent, slip = founder['grid'], inputs['covenant']; model = GenerationModel(**founder['model'])
    before = digest(inputs); pool = inputs['pools'][index]; hashes = [digest(g) for g in pool]
    incumbent = generate_candidate(parent, model, slip, rng_seed=spec['rng_seed'])
    checks = {}; evaluations = {}
    empty = deepcopy(founder['contexts']['fed'])
    empty.update(events=[], events_omitted=0, last_age_ticks=0, last_session_tick=0, outcome='alive')
    empty['care_summary'] = dict(history='complete', from_age_ticks=0, ticks_observed=0,
                                 keeper_actions={}, companion_actions={}, beg_requests=0)
    for name, context, policy in (('off', founder['contexts']['fed'], 'off'),
            ('absent', None, CARE_POLICY_V2), ('empty', empty, CARE_POLICY_V2)):
        chosen, receipt = select_care_successor(parent, model, slip, context=context,
            rng_seed=spec['rng_seed'], policy=policy, body_response=MODEL)
        checks[name+'_exact'] = chosen == incumbent and receipt is None
    for evaluator in EVALUATORS:
        local = {}; trials = {}
        for name, context in founder['contexts'].items():
            kwargs = dict(context=context, rng_seed=spec['rng_seed'], policy=CARE_POLICY_V2,
                          evaluator=evaluator, body_response=MODEL)
            chosen, receipt = select_care_successor(parent, model, slip, **kwargs)
            local[name+'_package_repeat'] = (chosen, receipt) == select_care_successor(parent, model, slip, **kwargs)
            local[name+'_lab_mirror'] = (chosen, receipt) == lab_select(parent, model, slip, **kwargs)
            other, control = select_care_successor(parent, model, slip,
                **{**kwargs, 'context':altered_metadata(context)})
            local[name+'_metadata_negative'] = chosen == other and receipt['candidates'] == control['candidates']
            local[name+'_same_candidate_bytes'] = [r['grid_sha256'] for r in receipt['candidates']] == hashes
            selected, baseline = receipt['candidates'][receipt['selected_index']], receipt['candidates'][0]
            for check, field in (('welfare','need_balance'), ('survival','survival_ticks'), ('terminal','terminal_survival')):
                local[name+'_'+check+'_nonregression'] = selected[field] >= baseline[field]
            local[name+'_live_option_selected'] = selected['terminal_survival'] or not any(r['terminal_survival'] for r in receipt['candidates'])
            local[name+'_pristine_child_exact'] = chosen == pool[receipt['selected_index']] and all(
                c['stress'] == 0 and c['damage'] == 0 for c in chosen['cells'])
            local[name+'_source_identity'] = receipt['context_sha256'] == digest(context) and receipt['source_identity'] == {
                key:context[key] for key in ('keeper_id','life_id','grid_id','grid_sha256')}
            consistent = True
            try:
                for row in receipt['candidates']: _validate_care_v2_episode(row, receipt, context)
            except (ValueError, TypeError, KeyError): consistent = False
            local[name+'_trajectory_consistent'] = consistent
            local[name+'_cold_start'] = all(r['episode']['initial_state']['age_ticks'] == 0
                and not r['episode']['initial_state'].get('thread_states', {}).get('qtable_policy')
                and r['episode']['initial_state']['learning_switches']['qtable_policy'] is False for r in receipt['candidates'])
            try:
                validate_care_selection({'context':context, 'receipt':receipt}, parent_record=context, child_grid=chosen)
                local[name+'_product_receipt_loadable'] = True
            except (ValueError, TypeError, KeyError): local[name+'_product_receipt_loadable'] = False
            local[name+'_body_response_bound'] = receipt.get('body_response') == MODEL and all(
                r['episode']['initial_state'].get('body_response') == MODEL for r in receipt['candidates'])
            trials[name] = dict(selected_grid=chosen, receipt=receipt, complete_ranking=complete_ranking(receipt))
        evaluations[evaluator] = dict(trials=trials, checks=local,
            selected_structures_differ=care_structure_sha256(trials['fed']['selected_grid']) != care_structure_sha256(trials['neglect']['selected_grid']),
            complete_rankings_differ=trials['fed']['complete_ranking'] != trials['neglect']['complete_ranking'])
    checks['input_immutable'] = before == digest(inputs)
    checks['founder_identity'] = founder['founder_index'] == spec['founder_index'] and all(
        c['grid_id'] == parent['grid_id'] and c['grid_sha256'] == digest(parent) for c in founder['contexts'].values())
    checks['frozen_pool_exact'] = pool == [generate_candidate(parent, model, slip, rng_seed=spec['rng_seed']+i) for i in range(8)]
    return {**spec, 'checks':checks, 'evaluators':evaluations, 'used_prefix_ticks':founder['used_prefix_ticks']}


def judge_care(rows):
    identities = len(rows) == 30 and all(all(type(row.get(k)) is int and row[k] == v for k,v in spec.items())
        for row, spec in zip(rows, care_plan()))
    common = bool(rows) and all(all_true(row.get('checks'), PAIR_CHECKS) for row in rows)
    result = {}
    for evaluator in EVALUATORS:
        relevant = [row.get('evaluators', {}).get(evaluator, {}) for row in rows]
        changed = sum(r.get('selected_structures_differ') is True for r in relevant)
        ranked = sum(r.get('complete_rankings_differ') is True for r in relevant)
        joint = sum(r.get('selected_structures_differ') is True and r.get('complete_rankings_differ') is True for r in relevant)
        checks = dict(complete_fixed_cohort=identities, input_and_pool_invariants=common,
            all_original_nonregressions_and_controls=bool(relevant) and all(all_true(r.get('checks'), CARE_CHECKS) for r in relevant),
            care_dependent_structural_choice_and_ranking=joint >= 1)
        result[evaluator] = dict(verdict='QUALIFIED_FIXED_HOLDOUT' if all(checks.values()) else 'REFUSE',
            checks=checks, completed_pairs=len(rows), structural_different_pairs=changed,
            ranking_different_pairs=ranked, joint_different_pairs=joint)
    return result


def production_trial(inputs, index, home):
    imports()
    from mecha_engine.runtime import evolve
    from mecha_engine.runtime._readability import learned_readability_score
    from mecha_game.execution import body_arguments, population_arguments
    from survival_population_gate import observations_bound
    from body_workload_recording import prepare_record, record_result
    spec = production_plan()[index]; before = digest(inputs); rows = []; admissions = []
    bundle, data = prepare_record(home, inputs['production'], spec)
    decoded_before = digest({k:asdict(v) if k == 'generation_model' else v for k,v in data.items()})
    if data['effective_config'] != CONFIG or data['rng_seed'] != spec['rng_seed'] or data['founder_grids'] != []:
        raise ValueError('recorded production inputs changed registered protocol')
    archive, report = evolve(data['seed_grids'], data['slip_profile'], data['generation_model'],
        data['repair_model'], readability_scorer=lambda grid:learned_readability_score(grid, data['legibility_model']),
        **data['effective_config'], rng_seed=data['rng_seed'], founder_grids=data['founder_grids'],
        cubff_pressure_source=data['cubff_pressure_source'], readability_selection=data['readability_selection'],
        care_selection_policy='off', **body_arguments(bundle), **population_arguments(bundle),
        admission_callback=admissions.append, evaluation_callback=rows.append)
    record_result(home, bundle, archive, report, admissions=admissions)
    result = dict(**spec, archive=archive, report=report, evaluations=rows)
    result['checks'] = dict(input_immutable=before == digest(inputs) and decoded_before == digest({
        k:asdict(v) if k == 'generation_model' else v for k,v in data.items()}),
        observations_bound=observations_bound(result), body_response_bound=report.get('body_response','legacy') == spec['body_response'])
    result['observations'] = population_observations(result)
    return result


def reproduce_trial(original_directory, original):
    imports()
    from body_workload_recording import reproduce_record
    home = Path(original_directory)/'save'
    before = {p.relative_to(home).as_posix():file_digest(p) for p in home.rglob('*') if p.is_file()}
    replay = reproduce_record(home)
    after = {p.relative_to(home).as_posix():file_digest(p) for p in home.rglob('*') if p.is_file()}
    elites = [{'niche_key':key, **original['archive']['elites'][key]} for key in sorted(original['archive']['elites'])]
    return dict(**production_plan()[1], reproduction=replay, save_before=before, save_after=after,
        reproduction_exact=replay.get('status') == 'matched' and replay.get('report') == original['report']
            and replay.get('elites') == elites and before == after)


def population_observations(result):
    report = result['report']; population = report['living_population']; termination = population['termination']
    episodes = [episode for row in result['evaluations'] for episode in
        [*(c['episode'] for c in row['cycles']), row['final_episode']] if episode is not None]
    causes = Counter(e['death_cause'] for e in episodes if e['alive'] is False)
    terminal_generation = termination['generation_index']
    terminal_rows = [r for r in result['evaluations'] if r['generation_index'] == terminal_generation]
    terminal_deaths = sum(1 for row in terminal_rows for episode in
        [*(c['episode'] for c in row['cycles']), row['final_episode']]
        if episode is not None and episode['alive'] is False and episode['death_cause'] is not None)
    breeders = len(population['final_breeders'])
    histories = [history for row in result['evaluations'] for history in
        [*(c.get('frames', {}).get('episode_history') for c in row['cycles']),
         row['final_episode'].get('history') if row['final_episode'] else None] if history is not None]
    return dict(episodes=len(episodes), lifecycle_deaths=sum(causes.values()), death_causes=dict(causes),
        terminal_breeders=breeders, terminal_generation=terminal_generation,
        terminal_generation_lifecycle_deaths=terminal_deaths,
        qualifying_extinction=breeders == 0 and terminal_deaths > 0
            and termination['reason'] == 'no_eligible_breeders' and termination['genuine_lifecycle_extinction'] is True,
        automatic_feed_actions=sum(row['action'] == 'feed' for history in histories for row in history),
        history_ticks=sum(len(history) for history in histories))


def verify_result(directory, source_digest, input_digest):
    directory = Path(directory); terminal = read(directory/'terminal.json'); start = read(directory/'started.json')
    spec = terminal.get('spec', {})
    if spec != stage_spec(spec.get('stage'), spec.get('index')):
        raise ValueError('prior receipt stage specification changed')
    if (terminal.get('format') != FORMAT or terminal.get('status') != 'completed'
            or terminal['source_manifest_sha256'] != source_digest or terminal['inputs_sha256'] != input_digest
            or terminal['started_sha256'] != file_digest(directory/'started.json')
            or terminal['spec'] != start['spec'] or start['source_manifest_sha256'] != source_digest
            or start['inputs_sha256'] != input_digest
            or 'result.json' not in terminal.get('outputs', {})):
        raise ValueError('uncompleted or differently bound prerequisite result')
    if spec['stage'] in ('production', 'duplicate') and not {
            'save/campaign.sqlite3', 'save/prepared-inputs.json', 'save/record.json'}.issubset(terminal['outputs']):
        raise ValueError('actual saved production output is not bound to receipt')
    for name, expected in terminal['outputs'].items():
        path = (directory/name).resolve()
        if not path.is_relative_to(directory.resolve()) or file_digest(path) != expected:
            raise ValueError('prerequisite output changed')
    elapsed = terminal['elapsed_seconds']
    if type(elapsed) not in (float,int) or not math.isfinite(elapsed) or not 0 <= elapsed <= terminal['spec']['seconds']:
        raise ValueError('prior result exceeded its registered bound')
    return read(directory/'result.json')


def prerequisites(path, expected, source_digest, input_digest):
    if path is None or expected is None or file_digest(path) != expected:
        raise ValueError('exact approved prerequisite manifest required before outcomes')
    value = read(path)
    if (value.get('format') != 'body_workload_preconditions_v1'
            or value.get('source_manifest_sha256') != source_digest or value.get('inputs_sha256') != input_digest):
        raise ValueError('prerequisite source or input identity differs')
    causal = value['causal']
    directory = ROOT / causal['directory']
    if file_digest(directory/'terminal.json') != causal['terminal_sha256']:
        raise ValueError('causal receipt identity differs')
    result = verify_result(directory, source_digest, input_digest)
    if read(directory/'terminal.json')['spec'] != stage_spec('causal'):
        raise ValueError('causal receipt is another stage')
    if not all_true(result.get('checks'), CAUSAL_CHECKS): raise ValueError('causal precondition refused')
    for key in ('native', 'operational', 'independent_review'):
        evidence = value[key]; evidence_path = (ROOT/evidence['path']).resolve()
        if not evidence_path.is_relative_to(ROOT) or file_digest(evidence_path) != evidence['sha256']:
            raise ValueError(key+' evidence changed')
        item = read(evidence_path)
        if (item.get('source_manifest_sha256') != source_digest or item.get('passed') is not True):
            raise ValueError(key+' did not pass under frozen sources')
    if read(ROOT/value['independent_review']['path']).get('inputs_sha256') != input_digest:
        raise ValueError('review did not approve exact frozen inputs')
    return value


def verify_invariants(stage, result):
    """Scientific refusal is evidence; corrupted instrumentation stops work."""
    if stage == 'care':
        if not all_true(result.get('checks'), PAIR_CHECKS) or set(result.get('evaluators', {})) != set(EVALUATORS):
            raise ValueError('care pair identity or input invariant failed')
        for evaluator in EVALUATORS:
            checks = result['evaluators'][evaluator].get('checks')
            if (not isinstance(checks, dict) or set(checks) != CARE_CHECKS
                    or any(checks[name] is not True for name in CARE_CHECKS-SCIENTIFIC_CHECKS)):
                raise ValueError('care measurement integrity failed: '+evaluator)
    if stage in ('production', 'duplicate') and not all_true(result.get('checks'),
            frozenset(('input_immutable', 'observations_bound', 'body_response_bound'))):
        raise ValueError('production input or observation integrity failed')
    if stage in ('reproduce', 'duplicate') and result.get('reproduction_exact') is not True:
        raise ValueError('immutable reproduction differs')


def execute(args):
    spec = stage_spec(args.stage, args.index); begun = time.perf_counter(); output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    source_digest = file_digest(args.source_manifest)
    input_digest = file_digest(args.inputs) if args.inputs else None
    start = dict(format=FORMAT, spec=spec, started_utc=utc(), source_manifest_sha256=source_digest,
                 inputs_sha256=input_digest, prerequisites_sha256=args.prerequisites_sha256)
    write(output/'started.json', start)
    status = 'error'; error = None; outputs = {}
    try:
        sources = source_snapshot(args.source_manifest)
        if args.stage == 'setup':
            if args.inputs is not None: raise ValueError('setup has no derived inputs')
            inputs = freeze_inputs()
            write(output/'inputs.json', inputs); outputs['inputs.json'] = file_digest(output/'inputs.json')
            result = dict(checks={'frozen':True}, inputs_sha256=outputs['inputs.json'])
        else:
            if args.inputs_sha256 != input_digest: raise ValueError('input payload byte identity differs')
            inputs = read(args.inputs); validate_inputs(inputs)
            if args.stage not in ('causal', 'analysis'):
                prerequisites(args.prerequisites, args.prerequisites_sha256, source_digest, input_digest)
            if args.stage == 'causal': result = causal_trial(inputs)
            elif args.stage == 'care': result = measure_care(inputs, args.index)
            elif args.stage == 'production': result = production_trial(inputs, args.index, output/'save')
            elif args.stage in ('reproduce', 'duplicate'):
                original = verify_result(args.original, source_digest, input_digest)
                target = 1 if args.stage == 'reproduce' else 0
                if any(original.get(k) != v for k,v in production_plan()[target].items()):
                    raise ValueError('reproduction source is not the first registered arm')
                if args.stage == 'reproduce': result = reproduce_trial(args.original, original)
                else:
                    result = production_trial(inputs, target, output/'save')
                    result['reproduction_exact'] = result == original
            else:
                raise ValueError('analysis is supplied by the integration owner; no automatic study loop')
        if source_snapshot(args.source_manifest) != sources: raise ValueError('source drift during stage')
        if args.inputs and file_digest(args.inputs) != input_digest: raise ValueError('input drift during stage')
        write(output/'result.json', result); outputs['result.json'] = file_digest(output/'result.json')
        if (output/'save').exists():
            outputs.update({p.relative_to(output).as_posix():file_digest(p)
                            for p in (output/'save').rglob('*') if p.is_file()})
        verify_invariants(args.stage, result)
        if time.perf_counter()-begun > spec['seconds']:
            raise TimeoutError('worker exceeded its registered stage cap')
        status = 'completed'
    except BaseException as exc:
        error = dict(kind=type(exc).__name__, message=str(exc), traceback=traceback.format_exc())
        write(output/'failure.json', error); outputs['failure.json'] = file_digest(output/'failure.json')
    elapsed = time.perf_counter()-begun
    if elapsed > spec['seconds'] and status == 'completed':
        status = 'error'; error = dict(kind='TimeoutError', message='stage finalization exceeded registered cap')
    terminal = dict(format=FORMAT, spec=spec, status=status, error=error, started_sha256=file_digest(output/'started.json'),
        source_manifest_sha256=source_digest, inputs_sha256=input_digest, prerequisites_sha256=args.prerequisites_sha256,
        outputs=outputs, elapsed_seconds=elapsed, finished_utc=utc())
    write(output/'terminal.json', terminal)
    if status != 'completed': raise RuntimeError(error['message'])
    return terminal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', required=True); parser.add_argument('--index', type=int, default=0)
    parser.add_argument('--source-manifest', required=True, type=Path)
    parser.add_argument('--inputs', type=Path); parser.add_argument('--inputs-sha256')
    parser.add_argument('--prerequisites', type=Path); parser.add_argument('--prerequisites-sha256')
    parser.add_argument('--original', type=Path); parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); result = execute(args)
    print(json.dumps({'stage':args.stage, 'index':args.index, 'status':result['status']}, allow_nan=False))
    return 0


if __name__ == '__main__': raise SystemExit(main())
