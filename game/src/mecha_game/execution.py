"""Immutable game execution snapshots and explicit, disposable reproduction.

DR0084/X5: effective JSON bytes preserve insertion order. Canonical JSON only
hashes manifests/results; it never serializes model inputs for execution.
"""
from __future__ import annotations

import base64
import copy
from dataclasses import asdict
import hashlib
import importlib
import importlib.util
import json
import platform
import sqlite3
import sys
import tomllib
from types import CodeType, FunctionType

from mecha_engine.generation import GenerationModel
from mecha_engine.runtime import evolve, learned_readability_score
from mecha_engine.storage import canonical_json

FORMAT = 'mechagotchi_era_execution_v1'
CONTRACT_NAME = 'mechagotchi_evolve_v1'
# Fixed execution closure, including parent exports and every imported engine
# computation. Storage, rendering and examples do not affect evolve outputs.
EXECUTION_MODULES = tuple('mecha_engine.' + suffix for suffix in (
    'archive', 'archive._metrics', 'archive.descriptors', 'archive.scoring', 'archive.store',
    'generation', 'generation.generate', 'generation.model', 'generation.wfc', 'generation.explain',
    'genome', 'genome.validation', 'genome.signature', 'genome.animation', 'genome.render',
    'lifecycle', 'lifecycle._policy', 'lifecycle._body_response', 'lifecycle.simulate',
    'learning', 'learning._switchboard', 'learning.episode', 'learning.threads',
    'repair', 'repair._damage', 'repair._features', 'repair._grids', 'repair.blind', 'repair.train', 'repair.wound',
    'runtime', 'runtime._cubff', 'runtime._damage', 'runtime._grids', 'runtime._readability',
    'runtime.evolve', 'runtime.live', 'runtime.care', 'runtime._observed_care',
    'runtime._survival_population', 'runtime._survival_live', 'slip', 'slip.authority',
))
EVOLVE_DEFAULTS = dict(generations=4, population=8, damage_cycles=3, ticks=72, dropout_rate=0.2)
POLICIES = dict(generator='constrained_wfc_style_stabilizer', founder_admission='validate_align_size_v1',
    archive_descriptor='extended', archive_insertion='fitness_niche_v1',
    seed_arithmetic='era_seed_plus_generation_times_100000_plus_index',
    repair='learned_neighborhood_softmax', scorer='learned_readability_insertion_order_v1')



POPULATION_FORMAT = 'mechagotchi_era_execution_v2'
POPULATION_INPUT_FORMAT = 'survival_population_inputs_v1'
SURVIVOR_POLICY = 'generation_survivors_v1'
POPULATION_DEFAULTS = dict(population_policy='legacy_archive', founder_start_mode=None,
                           survival_regime='sheltered', cubff_density_pressure=False)


def validate_population_inputs(options):
    """Validate the declared input contract, without supplying missing history."""
    if not isinstance(options, dict) or set(options) != {'format', *POPULATION_DEFAULTS}:
        raise ValueError('Invalid population execution inputs.')
    if options['format'] != POPULATION_INPUT_FORMAT:
        raise ValueError('Unsupported population input format.')
    policy, start = options['population_policy'], options['founder_start_mode']
    if policy not in ('legacy_archive', SURVIVOR_POLICY):
        raise ValueError('Unsupported population policy.')
    if (policy == SURVIVOR_POLICY and start not in ('bootstrap', 'continue')
            or policy == 'legacy_archive' and start not in (None, 'bootstrap')):
        raise ValueError('Population policy requires an explicit supported founder start mode.')
    if options['survival_regime'] not in ('sheltered', 'stress_probe'):
        raise ValueError('Unsupported survival regime.')
    if type(options['cubff_density_pressure']) is not bool:
        raise ValueError('Density pressure must be a boolean.')


def population_arguments(bundle):
    refs = bundle['manifest']['inputs']
    digest = refs.get('population_inputs_sha256')
    if digest is None:
        if bundle['manifest']['format'] == POPULATION_FORMAT:
            raise ValueError('Versioned execution is missing its population inputs.')
        return {}
    if bundle['manifest']['format'] != POPULATION_FORMAT:
        raise ValueError('Population inputs require versioned execution.')
    options = blob_json(bundle, digest)
    validate_population_inputs(options)
    return {key: copy.deepcopy(options[key]) for key in POPULATION_DEFAULTS}


def body_arguments(bundle):
    """The absent legacy choice is never silently upgraded."""
    ref = bundle['manifest']['inputs'].get('body_response_inputs_sha256')
    if ref is None:
        return {}
    value = blob_json(bundle, ref)
    if value != {'format': 'body_response_inputs_v1', 'body_response': 'workload-v1'}:
        raise ValueError('Unsupported body response execution inputs.')
    return {'body_response': value['body_response']}


def population_ended(report, elites, policy):
    """One game authority for campaign and completed-journal status dispatch."""
    if policy == 'legacy_archive':
        if 'living_population' in report:
            raise ValueError('Legacy campaign cannot reinterpret a living-population report.')
        return len(report['generations']) < report['generations_requested'] or not elites
    if policy != SURVIVOR_POLICY:
        raise ValueError('Unsupported population policy.')
    try:
        population = report['living_population']
        termination = population['termination']
        breeders = population['final_breeders']
        reasons = ('requested_horizon_complete', 'empty_continuation', 'all_founders_rejected', 'no_eligible_breeders')
        if (population['format'] != SURVIVOR_POLICY or population['population_policy'] != policy
                or not isinstance(breeders, list) or type(termination['ended']) is not bool
                or termination['reason'] not in reasons):
            raise ValueError('Invalid living-population outcome.')
        completed = termination['reason'] == 'requested_horizon_complete'
        if (completed != bool(breeders) or termination['ended'] != (not breeders)
                or completed and len(report['generations']) != report['generations_requested']):
            raise ValueError('Living-population termination disagrees with its final cohort.')
        terminal = termination['generation_index']
        if terminal is not None and (type(terminal) is not int or terminal != len(report['generations'])-1):
            raise ValueError('Living-population terminal generation is inconsistent.')
        if terminal is None and report['generations']:
            raise ValueError('Evaluated population has no terminal generation.')
        for key in ('lifecycle_deaths', 'structural_disqualifications'):
            if type(termination[key]) is not int or termination[key] < 0 or terminal is None and termination[key] != 0:
                raise ValueError('Invalid terminal population count.')
        genuine = not breeders and termination['lifecycle_deaths'] > 0
        if type(termination['genuine_lifecycle_extinction']) is not bool or termination['genuine_lifecycle_extinction'] != genuine:
            raise ValueError('Lifecycle extinction differs from actual terminal deaths.')
        return termination['ended']
    except (KeyError, TypeError, AttributeError) as error:
        raise ValueError('Incomplete living-population outcome.') from error


def breeder_sources(report, campaign_id, era_index):
    """Copy exact survivor slots; archive membership and genome IDs are not keys."""
    result = []
    for index, breeder in enumerate(report['living_population']['final_breeders']):
        if breeder['grid_sha256'] != result_digest(breeder['grid']):
            raise ValueError('Breeder body differs from its canonical identity.')
        row = dict(source_kind='era_breeder', source_position=index, campaign_id=campaign_id,
                   era_index=era_index, generation_index=breeder['generation_index'],
                   candidate_index=breeder['candidate_index'], grid_sha256=breeder['grid_sha256'])
        if breeder['care_context'] is not None:
            row.update(care_context=copy.deepcopy(breeder['care_context']),
                       care_context_origin=copy.deepcopy(breeder['care_context_origin']))
        elif breeder['care_context_origin'] is not None:
            raise ValueError('Breeder origin has no care context.')
        result.append(row)
    return result


def validate_breeder_continuation(founders, sources, previous, campaign_id, era_index, start):
    """Bind the complete continuation tail, including an authoritative empty tail."""
    if not isinstance(founders, list) or not isinstance(sources, list) or len(founders) != len(sources):
        raise ValueError('Breeder continuation requires explicit ordered founder inputs.')
    if not isinstance(previous, list):
        raise ValueError('Previous living cohort evidence is unavailable.')
    positions = [index for index, source in enumerate(sources)
                 if source is not None and source.get('source_kind') == 'era_breeder']
    if start == 'bootstrap':
        if previous or positions:
            raise ValueError('Bootstrap cannot reuse previous breeders.')
        return
    if start != 'continue' or type(era_index) is not int or era_index < 1:
        raise ValueError('Invalid breeder continuation position.')
    offset = len(founders)-len(previous)
    if offset < 0 or positions != list(range(offset, len(founders))):
        raise ValueError('Continuation must retain the complete ordered breeder tail.')
    expected = breeder_sources({'living_population': {'final_breeders': previous}}, campaign_id, era_index-1)
    for index, (breeder, source) in enumerate(zip(previous, expected), start=offset):
        actual = sources[index]
        if (canonical_json(founders[index]) != canonical_json(breeder['grid'])
                or any(actual.get(key) != value for key, value in source.items())
                or actual.get('care_context') != breeder['care_context']
                or actual.get('care_context_origin') != breeder['care_context_origin']):
            raise ValueError('Continuation differs from the exact prior breeder occurrence.')


def ordered_json_bytes(value):
    return json.dumps(value, ensure_ascii=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def result_digest(value):
    return sha256(canonical_json(value).encode('utf-8'))


def _code_value(value):
    """Portable normalized loaded code; no source paths or address reprs."""
    if isinstance(value, CodeType):
        return {'code': value.co_code.hex(), 'consts': [_code_value(x) for x in value.co_consts],
            'names': list(value.co_names), 'varnames': list(value.co_varnames),
            'freevars': list(value.co_freevars), 'cellvars': list(value.co_cellvars),
            'flags': value.co_flags, 'argcount': value.co_argcount,
            'posonlyargcount': value.co_posonlyargcount, 'kwonlyargcount': value.co_kwonlyargcount,
            'nlocals': value.co_nlocals, 'stacksize': value.co_stacksize,
            'exceptiontable': value.co_exceptiontable.hex()}
    if isinstance(value, tuple):
        return {'tuple': [_code_value(x) for x in value]}
    if isinstance(value, frozenset):
        items = [_code_value(x) for x in value]
        return {'frozenset': sorted(items, key=canonical_json)}
    if isinstance(value, bytes):
        return {'bytes': value.hex()}
    if isinstance(value, complex):
        return {'complex': [value.real.hex(), value.imag.hex()]}
    if isinstance(value, float):
        return {'float': value.hex()}
    if value is Ellipsis:
        return {'ellipsis': True}
    if value is None or type(value) in (str, int, bool):
        return value
    raise ValueError(f'unsupported execution code constant: {type(value).__name__}')


def _declared_codes(code):
    result = {code.co_qualname: code}
    for child in code.co_consts:
        if isinstance(child, CodeType):
            result.update(_declared_codes(child))
    return result


def _live_value(value):
    if isinstance(value, dict):
        return {'dict': [[_live_value(key), _live_value(item)] for key, item in value.items()]}
    if isinstance(value, list):
        return {'list': [_live_value(item) for item in value]}
    if isinstance(value, tuple):
        return {'tuple': [_live_value(item) for item in value]}
    if isinstance(value, set):
        return {'set': sorted((_live_value(item) for item in value), key=canonical_json)}
    if isinstance(value, FunctionType):
        return {'function': value.__module__ + '.' + value.__qualname__, 'code': _code_value(value.__code__)}
    return _code_value(value)


def _loaded_functions(module):
    generated = {'__init__', '__repr__', '__eq__', '__hash__', '__setattr__', '__delattr__',
                 '__lt__', '__le__', '__gt__', '__ge__', '__getstate__', '__setstate__'}
    for name, value in vars(module).items():
        if isinstance(value, FunctionType):
            yield name, value
        elif isinstance(value, type) and value.__module__.startswith('mecha_engine'):
            for member_name, member in vars(value).items():
                # These methods are generated by the supported Python dataclass
                # implementation, rather than compiled from this module source.
                if hasattr(value, '__dataclass_fields__') and member_name in generated:
                    continue
                if isinstance(member, (classmethod, staticmethod)):
                    member = member.__func__
                if isinstance(member, FunctionType):
                    yield name + '.' + member_name, member
                elif isinstance(member, property):
                    for access in ('fget', 'fset', 'fdel'):
                        function = getattr(member, access)
                        if isinstance(function, FunctionType):
                            yield name + '.' + member_name + '.' + access, function


def runtime_identity(*, include_metadata=False):
    """Verify current source/frozen loader code; unavailable is an honest result."""
    modules = {}
    declared = {}
    loaded = {}
    try:
        from mecha_game.runtime_resources import runtime_root, validate_resource
        metadata_path = runtime_root() / 'packages/mecha_engine/pyproject.toml'
        validate_resource(metadata_path)
        metadata_bytes = metadata_path.read_bytes()
        project = tomllib.loads(metadata_bytes.decode('utf-8'))['project']
        if project['name'] != 'mecha-engine' or not isinstance(project['version'], str):
            raise ValueError('invalid declared engine project metadata')
        version = project['version']
        for name in EXECUTION_MODULES:
            spec = importlib.util.find_spec(name)
            loader = spec.loader if spec else None
            code = loader.get_code(name) if loader and hasattr(loader, 'get_code') else None
            if not isinstance(code, CodeType):
                raise ValueError(f'code loader unavailable for {name}')
            modules[name] = result_digest(_code_value(code))
            declared[name] = _declared_codes(code)
        for name in EXECUTION_MODULES:
            module = importlib.import_module(name)
            for alias, function in _loaded_functions(module):
                owner = function.__module__
                if not owner.startswith('mecha_engine'):
                    continue
                expected = declared.get(owner, {}).get(function.__code__.co_qualname)
                if expected is None or _code_value(expected) != _code_value(function.__code__):
                    raise ValueError(f'loaded code differs from declared implementation: {name}.{alias}')
                loaded[name + '.' + alias] = result_digest(dict(code=_code_value(function.__code__),
                    defaults=_live_value(function.__defaults__), kwdefaults=_live_value(function.__kwdefaults__)))
    except (ImportError, OSError, ValueError, AttributeError, KeyError, TypeError) as error:
        return {'available': False, 'reason': str(error), 'implementation': platform.python_implementation(),
                'python_major_minor': list(sys.version_info[:2])}
    result = {'available': True, 'implementation': platform.python_implementation(),
        'python_major_minor': list(sys.version_info[:2]), 'engine_version': version,
        'engine_metadata_sha256': sha256(metadata_bytes), 'optimization': sys.flags.optimize, 'module_sha256': modules,
        'implementation_sha256': result_digest(modules), 'loaded_callables_sha256': result_digest(loaded)}
    if include_metadata:
        result['engine_metadata_data_base64'] = base64.b64encode(metadata_bytes).decode('ascii')
    return result


def runtime_receipt():
    """Installation evidence is separate from portable code compatibility."""
    from mecha_game.runtime_resources import MANIFEST_NAME, read_manifest, runtime_mode, runtime_root
    mode = runtime_mode()
    if mode != 'frozen_windows_x64':
        return dict(mode=mode, manifest_sha256=None, content_id=None)
    root = runtime_root()
    manifest = read_manifest(root)
    return dict(mode=mode, manifest_sha256=sha256((root/MANIFEST_NAME).read_bytes()), content_id=manifest['content_id'])


def calibration_payload():
    from mecha_engine.archive import descriptors, scoring
    from mecha_engine.generation import model
    from mecha_engine.runtime import _cubff
    runtime = importlib.import_module('mecha_engine.runtime.evolve')
    return copy.deepcopy(dict(descriptor_mode=descriptors.EXTENDED_MODE,
        descriptor_names=descriptors.EXTENDED_DESCRIPTOR_NAMES,
        bin_thresholds=descriptors.BIN_THRESHOLDS, mass_reference_area=descriptors.MASS_REFERENCE_AREA,
        final_descriptor_thresholds_locked=descriptors.FINAL_DESCRIPTOR_THRESHOLDS_LOCKED,
        readability_calibration_status=descriptors.READABILITY_CALIBRATION_STATUS,
        fitness_weights=scoring.FITNESS_WEIGHTS, pressure_gain=runtime.CUBFF_PRESSURE_GAIN,
        pressure_multiplier_band=list(runtime.CUBFF_MULTIPLIER_BAND),
        cubff_density_weight=_cubff.CUBFF_DENSITY_WEIGHT,
        cubff_instruction_bytes=sorted(_cubff.CUBFF_INSTRUCTION_BYTES),
        cubff_organization_ceiling=_cubff.ORGANIZATION_CEILING,
        generator_strategy=model.GENERATOR_STRATEGY, proposal_source=model.PROPOSAL_SOURCE,
        policies=POLICIES))


def source_record(raw, *, role, source_position=None, label=None, source_kind='file', **facts):
    result = dict(role=role, source_kind=source_kind, source_position=source_position, **facts)
    if label is not None:
        result['label'] = label
    if raw is not None:
        result['data_base64'] = base64.b64encode(raw).decode('ascii')
    return result


def validate_source_records(records, *, count=None, grids=None):
    if not isinstance(records, list) or (count is not None and len(records) != count):
        raise ValueError('Source evidence must match the ordered inputs.')
    for index, row in enumerate(records):
        if row is None:  # old preparation with no source evidence
            continue
        if not isinstance(row, dict) or not isinstance(row.get('source_kind'), str) or not row['source_kind']:
            raise ValueError('Invalid input source evidence.')
        position = row.get('source_position', row.get('position'))
        if position is not None and (type(position) is not int or position < 0):
            raise ValueError('Invalid input source position.')
        label = row.get('label')
        if label is not None and (not isinstance(label, str) or not label or '\\' in label or ':' in label
                or label.startswith('/') or '..' in label.split('/')):
            raise ValueError('Input source labels must be relative.')
        if row.get('care_context') is not None:
            from mecha_game.care_history import validate_care_context
            context = row['care_context']
            validate_care_context(context)
            if row.get('role', 'founder') != 'founder':
                raise ValueError('Care context belongs to a founder source.')
            if row['source_kind'] == 'keeper_companion':
                if any(row.get(key) != context[key] for key in ('keeper_id', 'life_id')):
                    raise ValueError('Care context differs from the recorded Keeper life.')
                if grids is not None:
                    validate_care_context(context, grid=grids[index])
        if 'data_base64' in row:
            try:
                base64.b64decode(row['data_base64'], validate=True)
            except (ValueError, TypeError) as error:
                raise ValueError('Invalid retained input source bytes.') from error


def _add_blob(bundle, raw, media_type='application/json'):
    digest = sha256(raw)
    row = dict(media_type=media_type, data_base64=base64.b64encode(raw).decode('ascii'))
    if digest in bundle['blobs'] and bundle['blobs'][digest] != row:
        raise ValueError('Conflicting immutable execution blob.')
    bundle['blobs'][digest] = row
    return digest


def blob_json(bundle, digest):
    row = bundle['blobs'][digest]
    raw = base64.b64decode(row['data_base64'], validate=True)
    if sha256(raw) != digest:
        raise ValueError('Execution blob hash mismatch.')
    return json.loads(raw)


def capture_execution(campaign_id, era_index, effective_inputs, source_records):
    """Freeze inputs before evolve; callers execute only decoded captured bytes."""
    data = effective_inputs
    bundle = {'manifest': {}, 'blobs': {}}
    def retain(value):
        return _add_blob(bundle, ordered_json_bytes(value))
    generation = data['generation_model']
    if isinstance(generation, GenerationModel):
        generation = asdict(generation)
    inputs = dict(seed_corpus_sha256=retain(data['seed_grids']), covenant_sha256=retain(data['slip_profile']),
        generation_model_sha256=retain(generation), repair_model_sha256=retain(data['repair_model']),
        readability_model_sha256=retain(data['legibility_model']),
        readability_selection_sha256=retain(data.get('readability_selection')),
        repair_training_sha256=retain(data.get('repair_training')))
    founders, weather = data.get('founder_grids'), data.get('cubff_pressure_source')
    inputs.update(founder_mode='none' if founders is None else 'list',
        founder_sha256=[retain(grid) for grid in founders] if founders is not None else [],
        weather_mode='none' if weather is None else 'list',
        ordered_weather_sha256=None if weather is None else retain(weather))
    settings = {key: data.get(key, value) for key, value in POPULATION_DEFAULTS.items()}
    population_inputs = dict(format=POPULATION_INPUT_FORMAT, **settings)
    validate_population_inputs(population_inputs)
    extended = settings != POPULATION_DEFAULTS
    if settings['population_policy'] == SURVIVOR_POLICY and founders is None:
        raise ValueError('Survivor execution requires an explicit founder list, including empty.')
    if extended:
        inputs['population_inputs_sha256'] = retain(population_inputs)
    body_response = data.get('body_response', 'legacy')
    if body_response not in ('legacy', 'workload-v1'):
        raise ValueError('Unsupported body response.')
    if body_response != 'legacy':
        inputs['body_response_inputs_sha256'] = retain(dict(format='body_response_inputs_v1', body_response=body_response))
    care = None
    if data.get('founder_care_contexts') is not None or data.get('care_selection_policy', 'off') != 'off':
        care = dict(format='keeper_care_inputs_v1', policy=data.get('care_selection_policy', 'off'),
            evaluator=data.get('care_evaluator', 'archive_morphology_probe_v1'),
            founder_contexts=copy.deepcopy(data.get('founder_care_contexts') or [None] * len(founders or [])))
        # An explicitly empty list must never become a full null list.
        if data.get('founder_care_contexts') is not None:
            care['founder_contexts'] = copy.deepcopy(data['founder_care_contexts'])
        validate_care_inputs(care, founders or [])
        if any(context is not None and context.get("body_response", "legacy") != body_response
               for context in care["founder_contexts"]):
            raise ValueError("Founder care body response differs from captured era model.")
        inputs['care_inputs_sha256'] = retain(care)
    identity = runtime_identity(include_metadata=True)
    if not identity.get('available'):
        raise ValueError('Execution identity unavailable: ' + identity.get('reason', 'unverified runtime'))
    source_records = copy.deepcopy(source_records)
    if identity.get('available'):
        source_records.append(dict(role='engine_metadata', source_kind='declared_project', source_position=None,
            label='packages/mecha_engine/pyproject.toml', data_base64=identity.pop('engine_metadata_data_base64')))
    validate_source_records(source_records)
    if care is not None:
        by_ordinal = {}
        for row in source_records:
            if row is not None and 'founder_ordinal' in row:
                ordinal = row['founder_ordinal']
                if type(ordinal) is not int or ordinal < 0 or ordinal >= len(founders or []) or ordinal in by_ordinal:
                    raise ValueError('Duplicate or invalid care founder source ordinal.')
                by_ordinal[ordinal] = row
        for ordinal, context in enumerate(care['founder_contexts']):
            source = by_ordinal.get(ordinal)
            if source is None:
                if context is not None:
                    raise ValueError('Care context needs its recorded founder source.')
                source_records.append(dict(role='founder', source_kind='in_memory', source_position=None, founder_ordinal=ordinal, care_context=None))
            elif source.get('care_context') != context:
                raise ValueError('Care context differs from its immutable founder source.')
            elif context is not None and source.get('source_kind') == 'keeper_companion':
                from mecha_game.care_history import validate_care_context
                validate_care_context(context, keeper_id=source.get('keeper_id'), life_id=source.get('life_id'), grid=founders[ordinal])
            if source is not None:
                source['care_context'] = copy.deepcopy(context)
    sources = []
    for original in source_records:
        if original is None:
            continue
        row = copy.deepcopy(original)
        row['source_position'] = row.pop('position', row.get('source_position'))
        row.pop('media_type', None)
        if 'data_base64' in row:
            raw = base64.b64decode(row.pop('data_base64'), validate=True)
            try:
                json.loads(raw)
                media_type = 'application/json'
            except (ValueError, UnicodeError):
                media_type = 'application/octet-stream'
            row['raw_sha256'] = _add_blob(bundle, raw, media_type)
        sources.append(row)
    config = {**EVOLVE_DEFAULTS, **data.get('effective_config', {})}
    if set(config) != set(EVOLVE_DEFAULTS):
        raise ValueError('Unsupported effective evolve parameter.')
    bundle['manifest'] = dict(format=POPULATION_FORMAT if extended else FORMAT, campaign_id=campaign_id, era_index=era_index,
        rng_seed=data['rng_seed'], execution_contract=dict(name=CONTRACT_NAME, runtime=identity, policies=copy.deepcopy(POLICIES)),
        effective_config=copy.deepcopy(config), inputs=inputs, sources=sources, founder_occurrences=[],
        runtime_receipt=runtime_receipt(),
        calibration_sha256=retain(calibration_payload()), report_sha256=None, elites_sha256=None)
    return bundle


def validate_care_inputs(care, founders):
    if not isinstance(care, dict) or set(care) != {'format', 'policy', 'evaluator', 'founder_contexts'}:
        raise ValueError('Invalid care execution inputs.')
    if care['format'] != 'keeper_care_inputs_v1' or care['policy'] not in ('off', 'observed_care_selection_v1', 'observed_care_selection_v2'):
        raise ValueError('Unsupported care selection policy.')
    if care['evaluator'] not in ('pristine', 'archive_morphology_probe_v1'):
        raise ValueError('Unsupported care evaluator.')
    contexts = care['founder_contexts']
    if not isinstance(contexts, list) or len(contexts) != len(founders):
        raise ValueError('Care contexts must match founder occurrence order.')
    for context in contexts:
        if context is not None:
            from mecha_game.care_history import validate_care_context
            validate_care_context(context)


def care_arguments(bundle):
    refs = bundle['manifest']['inputs']
    if 'care_inputs_sha256' not in refs:
        return {}
    care = blob_json(bundle, refs['care_inputs_sha256'])
    founders = [blob_json(bundle, sha) for sha in refs['founder_sha256']]
    validate_care_inputs(care, founders)
    return dict(founder_care_contexts=care['founder_contexts'],
                care_selection_policy=care['policy'], care_evaluator=care['evaluator'])


def elite_care_sources(report, elites, campaign_id, era_index):
    """Retain actual prior elite slots, never infer ancestry from matching IDs."""
    sources = [dict(source_kind='era_elite', source_position=index,
        campaign_id=campaign_id, era_index=era_index, niche_key=elite['niche_key'])
        for index, elite in enumerate(elites)]
    care = report.get('care_selection')
    if care is None:
        return sources
    contexts, origins = care.get('elite_contexts'), care.get('elite_origins')
    if not isinstance(contexts, list) or not isinstance(origins, list) or len(contexts) != len(elites) or len(origins) != len(elites):
        raise ValueError('Recorded care context does not match ordered elite outputs.')
    for source, context, origin in zip(sources, contexts, origins):
        if context is not None:
            from mecha_game.care_history import validate_care_context
            validate_care_context(context)
            if not isinstance(origin, dict):
                raise ValueError('Recorded care context has no founder occurrence origin.')
            source.update(care_context=copy.deepcopy(context), care_context_origin=copy.deepcopy(origin))
        elif origin is not None:
            raise ValueError('Recorded founder occurrence origin has no care context.')
    return sources


def decode_execution_inputs(bundle):
    """Reconstruct independent, insertion-ordered objects without any path reads."""
    manifest = bundle['manifest']; refs = manifest['inputs']
    def get(key):
        return blob_json(bundle, refs[key])
    model = get('generation_model_sha256')
    return dict(seed_grids=get('seed_corpus_sha256'), slip_profile=get('covenant_sha256'),
        generation_model=GenerationModel(**model) if model is not None else None,
        repair_model=get('repair_model_sha256'), legibility_model=get('readability_model_sha256'),
        readability_selection=get('readability_selection_sha256'),
        founder_grids=None if refs['founder_mode'] == 'none' else [blob_json(bundle, ref) for ref in refs['founder_sha256']],
        cubff_pressure_source=None if refs['weather_mode'] == 'none' else get('ordered_weather_sha256'),
        rng_seed=manifest['rng_seed'], effective_config=copy.deepcopy(manifest['effective_config']),
        **care_arguments(bundle), **population_arguments(bundle), **body_arguments(bundle))


def validate_execution_outputs(bundle, report, elites):
    """Bind scientific report semantics to the captured effective arguments."""
    manifest = bundle['manifest']; refs = manifest['inputs']; config = manifest['effective_config']
    expected = {'rng_seed': manifest['rng_seed'], 'generations_requested': config['generations'],
        **{key: config[key] for key in ('population', 'damage_cycles', 'ticks', 'dropout_rate')},
        'seed_corpus_size': len(blob_json(bundle, refs['seed_corpus_sha256']))}
    if canonical_json({key: report.get(key) for key in expected}) != canonical_json(expected):
        raise ValueError('Execution configuration disagrees with the scientific report.')
    body = body_arguments(bundle).get('body_response', 'legacy')
    if report.get('body_response', 'legacy') != body or ('body_response' in report and body == 'legacy'):
        raise ValueError('Body response report differs from immutable inputs.')
    # Validate actual evaluated genomes and all saved projections using the shared engine.
    from mecha_engine.storage.store import _bind_body_report
    decoded = {sha: base64.b64decode(blob['data_base64']) for sha, blob in bundle['blobs'].items()}
    _bind_body_report(manifest, decoded, report)
    options = population_arguments(bundle)
    policy = options.get('population_policy', 'legacy_archive')
    population_ended(report, elites, policy)
    if options:
        if report.get('survival_regime', 'sheltered') != options['survival_regime']:
            raise ValueError('Survival regime report differs from immutable inputs.')
        if report.get('cubff_pressure', {}).get('density_pressure', False) != options['cubff_density_pressure']:
            raise ValueError('Density pressure report differs from immutable inputs.')
    if policy == SURVIVOR_POLICY:
        population = report['living_population']
        if any(population.get(key) != options[key] for key in ('population_policy', 'founder_start_mode', 'survival_regime')):
            raise ValueError('Living-population report differs from immutable inputs.')
        digest = manifest.get('ordered_breeders_sha256')
        if digest is None or canonical_json(blob_json(bundle, digest)) != canonical_json(population['final_breeders']):
            raise ValueError('Ordered breeder output differs from the scientific report.')
        breeder_sources(report, manifest['campaign_id'], manifest['era_index'])
    elif 'ordered_breeders_sha256' in manifest:
        raise ValueError('Historical archive execution cannot contain living breeder output.')
    care_args = care_arguments(bundle)
    care_report = report.get('care_selection')
    if care_args and any(context is not None for context in care_args['founder_care_contexts']):
        if not isinstance(care_report, dict) or any(care_report.get(key) != value for key, value in (
                ('policy', care_args['care_selection_policy']), ('evaluator', care_args['care_evaluator']),
                ('founder_contexts', care_args['founder_care_contexts']))):
            raise ValueError('Care selection report differs from immutable inputs.')
        elite_care_sources(report, elites, manifest['campaign_id'], manifest['era_index'])
    elif care_report is not None:
        raise ValueError('Care selection report has no captured care inputs.')
    rows = manifest['founder_occurrences']
    founders = dict(admitted_ids=[row['grid_id'] for row in rows if row['admitted']],
        rejected=[dict(grid_id=row['grid_id'], errors=row['rejection_errors']) for row in rows if not row['admitted']])
    if (refs['founder_mode'] == 'none' and 'founders' in report
            or refs['founder_mode'] == 'list' and canonical_json(report.get('founders')) != canonical_json(founders)):
        raise ValueError('Founder observation disagrees with the scientific report.')
    if manifest['report_sha256'] != result_digest(report) or manifest['elites_sha256'] != result_digest(elites):
        raise ValueError('Execution result digest disagrees with recorded outputs.')


def finalize_execution(bundle, admissions, report, elites):
    from mecha_engine.storage import validate_execution
    result = copy.deepcopy(bundle); manifest = result['manifest']; refs = manifest['inputs']['founder_sha256']
    if len(admissions) != len(refs):
        raise ValueError('Founder observer did not record every submitted occurrence.')
    sources = {row['founder_ordinal']: row for row in manifest['sources'] if 'founder_ordinal' in row}
    occurrences = []
    for ordinal, (digest, event) in enumerate(zip(refs, admissions)):
        grid = blob_json(result, digest)
        if event['submission_index'] != ordinal or event['grid_id'] != grid.get('grid_id'):
            raise ValueError('Founder observer order or identity disagrees with captured input.')
        source = sources.get(ordinal, dict(source_kind='in_memory', source_position=None))
        row = {key: copy.deepcopy(value) for key, value in source.items()
               if key not in ('role', 'founder_ordinal', 'raw_sha256')}
        row.update(ordinal=ordinal, grid_id=event['grid_id'], grid_sha256=digest,
            admitted=event['admitted'], rejection_errors=copy.deepcopy(event['rejection_errors']))
        occurrences.append(row)
    prior_output_digests = {manifest.get('ordered_elites_sha256'), manifest.get('ordered_breeders_sha256')}
    options = population_arguments(result)
    if options.get('population_policy') == SURVIVOR_POLICY:
        manifest['ordered_breeders_sha256'] = _add_blob(result, ordered_json_bytes(report['living_population']['final_breeders']))
    ordered_elites_digest = _add_blob(result, ordered_json_bytes(elites))
    manifest.update(founder_occurrences=occurrences, report_sha256=result_digest(report), elites_sha256=result_digest(elites),
                    ordered_elites_sha256=ordered_elites_digest)
    for prior_elites_digest in prior_output_digests - {None, manifest.get('ordered_elites_sha256'), manifest.get('ordered_breeders_sha256')}:
        # Reproduction finalizes an independent copy. Retire only this copy's
        # superseded output reference; never modify the saved bundle.
        inputs = manifest['inputs']
        other_refs = {manifest['calibration_sha256'], *inputs['founder_sha256'],
                      manifest.get('ordered_elites_sha256'), manifest.get('ordered_breeders_sha256')}
        other_refs.update(value for key, value in inputs.items() if key.endswith('_sha256') and key != 'founder_sha256' and value is not None)
        other_refs.update(row['raw_sha256'] for row in manifest['sources'] if 'raw_sha256' in row)
        if prior_elites_digest not in other_refs:
            result['blobs'].pop(prior_elites_digest, None)
    validate_execution(result)
    validate_execution_outputs(result, report, elites)
    return result


def inspect_execution(bundle):
    """Validate evidence and current compatibility; never simulate or load inputs."""
    if bundle is None:
        return dict(status='unavailable', reason='historical_inputs_not_recorded')
    try:
        from mecha_engine.storage import validate_execution
        validate_execution(bundle)
        manifest = bundle['manifest']; contract = manifest['execution_contract']
        if contract.get('name') != CONTRACT_NAME or contract.get('policies') != POLICIES:
            return dict(status='unavailable', reason='unsupported_execution_contract')
        current = runtime_identity()
        if not current['available'] or not contract.get('runtime', {}).get('available'):
            return dict(status='unavailable', reason='runtime_identity_unavailable')
        if current != contract['runtime']:
            return dict(status='unavailable', reason='unsupported_runtime_identity')
        if ordered_json_bytes(blob_json(bundle, manifest['calibration_sha256'])) != ordered_json_bytes(calibration_payload()):
            return dict(status='unavailable', reason='unsupported_calibration_identity')
        if set(manifest['effective_config']) != set(EVOLVE_DEFAULTS):
            return dict(status='unavailable', reason='unsupported_effective_config')
        decode_execution_inputs(bundle)
        return dict(status='available', reason=None)
    except (ValueError, KeyError, TypeError, AttributeError) as error:
        return dict(status='unavailable', reason=f'invalid_execution_evidence: {error}')


def _different_paths(left, right, path='$'):
    if type(left) != type(right):
        return [path]
    if isinstance(left, dict):
        paths = []
        for key in sorted(left.keys() | right.keys()):
            if key not in left or key not in right:
                paths.append(f'{path}.{key}')
            else:
                paths.extend(_different_paths(left[key], right[key], f'{path}.{key}'))
        return paths
    if isinstance(left, list):
        if len(left) != len(right):
            return [path + '.length']
        return [item for index, (a, b) in enumerate(zip(left, right)) for item in _different_paths(a, b, f'{path}[{index}]')]
    return [] if left == right else [path]


def reproduce_era(conn, campaign_id, era_index, *, progress_callback=None):
    """Run only immutable saved inputs, returning full equality without any writes."""
    from mecha_engine.storage import load_era_execution, load_era_elites
    result = dict(status='unavailable', reason=None, differing_paths=[], campaign_id=campaign_id,
                  era_index=era_index, report=None, elites=None)
    try:
        bundle = load_era_execution(conn, campaign_id, era_index)
        status = inspect_execution(bundle)
        if status['status'] != 'available':
            return {**result, 'reason': status['reason']}
        row = conn.execute('SELECT report_json FROM eras WHERE campaign_id=? AND era_index=?', (campaign_id, era_index)).fetchone()
        if row is None:
            return {**result, 'reason': 'recorded_era_missing'}
        expected_report = json.loads(row[0])
        expected_elites = load_era_elites(conn, campaign_id, era_index)
        validate_execution_outputs(bundle, expected_report, expected_elites)
        data = decode_execution_inputs(bundle)
    except (ValueError, KeyError, TypeError, sqlite3.Error) as error:
        return {**result, 'reason': f'invalid_execution_evidence: {error}'}
    admissions = []
    # Callback exceptions deliberately propagate to the existing joined worker's
    # foreground cancellation/error boundary, as in ordinary evolve.
    archive, report = evolve(data['seed_grids'], data['slip_profile'], data['generation_model'], data['repair_model'],
        readability_scorer=lambda grid: learned_readability_score(grid, data['legibility_model']),
        rng_seed=data['rng_seed'], founder_grids=data['founder_grids'], cubff_pressure_source=data['cubff_pressure_source'],
        readability_selection=data['readability_selection'], admission_callback=admissions.append,
        progress_callback=progress_callback, **data['effective_config'], **care_arguments(bundle), **population_arguments(bundle), **body_arguments(bundle))
    elites = [{'niche_key': niche, **archive['elites'][niche]} for niche in sorted(archive['elites'])]
    actual = finalize_execution(bundle, admissions, report, elites)
    paths = _different_paths(expected_report, report, '$.report') + _different_paths(expected_elites, elites, '$.elites')
    paths += _different_paths(bundle['manifest']['founder_occurrences'], actual['manifest']['founder_occurrences'], '$.founder_occurrences')
    if 'ordered_breeders_sha256' in bundle['manifest']:
        paths += _different_paths(blob_json(bundle, bundle['manifest']['ordered_breeders_sha256']),
                                  blob_json(actual, actual['manifest']['ordered_breeders_sha256']), '$.breeders')
    return {**result, 'status': 'mismatch' if paths else 'matched',
            'reason': 'recorded_results_differ' if paths else None,
            'differing_paths': paths, 'report': report, 'elites': elites}
