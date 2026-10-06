"""One foreground-owned X8 earned-preparation qualification stage.

The coordinator alone freezes/trains, copies density fork homes, enforces the
process-tree deadline and debits every attempt against the shared 1,200 seconds.
This worker never chooses another seed, repeats an era, changes source, creates a
successor, trains repair models or qualifies food access. Unit tests are synthetic.

CLI::
  python -B labs/game_loop/x8_earned_preparation_gate.py \
    --stage role-era --index 0 --home NEW_HOME --output NEW_OUTPUT \
    --inputs FROZEN_INPUTS --source-manifest FROZEN_SOURCE --remaining-seconds 1200

Stages: role-era indices 0..2; density-earn index 0; density-off/on index 1;
restart, reproduce, density-duplicate select an existing index. Continuing calls
need --previous COMPLETED_STAGE_DIRECTORY. Density fork bytes must equal the
density-earn terminal's after.files exactly. For a duplicate after another read
stage, --reference may name the original density-off stage. No implicit resume.

Frozen inputs format x8_earned_preparation_inputs_v1: seed_grids (50 ordered),
slip_profile, input_sources (raw source records), generation_model (dataclass
fields), repair_model, repair_training, legibility_model, training_options, weather_sources
(storm and real), role_exemplars (ornament/effect -> exact grid_id). The source
manifest has format x8_earned_source_manifest_v1 or x8_source_manifest_v1 and a
nonempty files mapping covering this worker and all effective runtime inputs.

Outputs: start.json before application work; source-events.json/screenshots for
native stages; evaluations.json contains ORIGINAL read-only callback records;
result.json contains verified saved outputs; terminal.json binds every output,
before/after inventories, invariants, actual duration and explicit failure.
"""
from __future__ import annotations

import argparse
import base64
from contextlib import closing
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import sqlite3
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
FORMAT = 'x8_earned_preparation_stage_v1'
INPUT_FORMAT = 'x8_earned_preparation_inputs_v1'
POLICY = 'generation_survivors_v1'
CONFIG = dict(generations=6, population=16, damage_cycles=2, ticks=16, dropout_rate=.2)
TRAINING = dict(repair_training_count=40, dropout_rates=[.1,.2,.3,.4], damage_instances=1,
                epochs=40, learning_rate=1.5, live_class_weight=3., rng_seed=20260707, vocabulary='legacy')
STARTER_ROLES = ('body_core', 'sensor', 'expression', 'locomotion')
ROLES = ('ornament', 'effect')
ERA_STAGES = ('role-era', 'density-earn', 'density-off', 'density-on')
STAGES = (*ERA_STAGES, 'restart', 'reproduce', 'density-duplicate')


def encoded(value):
    return json.dumps(value, ensure_ascii=True, separators=(',', ':'), allow_nan=False).encode()


def digest(raw): return hashlib.sha256(raw).hexdigest()
def file_digest(path): return digest(Path(path).read_bytes())
def read(path): return json.loads(Path(path).read_bytes())
def utc(): return datetime.now(timezone.utc).isoformat()


def write(path, value):
    with Path(path).open('xb') as stream:
        stream.write(encoded(value) + b'\n')


def imports():
    for relative in ('', 'game/src', 'packages/mecha_engine/src'):
        value = str(ROOT / relative)
        if value not in sys.path: sys.path.insert(0, value)


def stage_spec(stage, index):
    if stage not in STAGES or type(index) is not int or not 0 <= index <= 2:
        raise ValueError('Unsupported fixed stage/index.')
    if stage == 'density-earn' and index != 0 or stage in ('density-off','density-on','density-duplicate') and index != 1:
        raise ValueError('Density protocol has exactly earn index0 and comparison index1.')
    seed = 20261030 if stage == 'role-era' else 20261031 if stage.startswith('density-') else None
    return dict(seed=seed, index=index, era=stage in ERA_STAGES,
                seconds=60 if stage == 'restart' else 120)


def verified_receipt(directory):
    directory = Path(directory).resolve()
    receipt = read(directory / 'terminal.json')
    if (receipt.get('format') != FORMAT or receipt.get('status') != 'completed'
            or not receipt.get('checks') or any(v is not True for v in receipt['checks'].values())
            or not receipt.get('outputs')):
        raise ValueError('Prior stage is incomplete, failed or has no verified output closure.')
    stage_spec(receipt.get('stage'),receipt.get('index'))
    required={'start.json','result.json','evaluations.json'}
    if receipt['stage'] in (*ERA_STAGES,'restart'):required.update(('source-events.json','launch.json'))
    actual={p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file() and p!=directory/'terminal.json'}
    if not required.issubset(receipt['outputs']) or set(receipt['outputs'])!=actual:
        raise ValueError('Prior receipt does not bind the exact output closure.')
    if not required_checks(receipt['stage']).issubset(receipt['checks']):
        raise ValueError('Prior receipt is missing required stage invariants.')
    for name, expected in receipt['outputs'].items():
        target = (directory / name).resolve()
        if Path(name).is_absolute() or not target.is_relative_to(directory) or file_digest(target) != expected:
            raise ValueError('Prior output changed: ' + name)
    start=read(directory/'start.json')
    for key in ('format','stage','index','home','source_manifest_sha256','inputs_sha256'):
        if key not in receipt or start.get(key)!=receipt[key]:raise ValueError('Prior terminal/start binding differs: '+key)
    for key in ('source_manifest_sha256','inputs_sha256'):
        value=receipt[key]
        if not isinstance(value,str) or len(value)!=64 or any(c not in '0123456789abcdef' for c in value):
            raise ValueError('Invalid prior frozen digest.')
    return receipt


def required_checks(stage):
    common={'source_unchanged','inputs_unchanged','within_stage_budget'}
    if stage in ERA_STAGES:
        return common|{'one_era','full_corpus','covenant','generation_model','repair_model','repair_training',
            'readability_model','configuration','readability_selection','fixed_seed','weather','population','start',
            'sheltered','density','care_off','all_actual_evaluations','breeders_exact'}
    if stage=='restart':return common|{'restart_state_unchanged','restart_ledger_unchanged','restart_plan_unchanged'}
    return common|{'immutable_reproduction','read_only'}|({'duplicate_observations_exact','duplicate_report_exact','duplicate_elites_exact'} if stage=='density-duplicate' else set())


def checked_source(path):
    manifest = read(path)
    if manifest.get('format') not in ('x8_source_manifest_v1','x8_earned_source_manifest_v1') or not manifest.get('files'):
        raise ValueError('Nonempty frozen source manifest required.')
    files = manifest['files']
    if not isinstance(files, dict) or 'labs/game_loop/x8_earned_preparation_gate.py' not in files:
        raise ValueError('Instrument missing from source closure.')
    for name, expected in files.items():
        path = (ROOT / name).resolve()
        if Path(name).is_absolute() or not path.is_relative_to(ROOT) or file_digest(path) != expected:
            raise ValueError('Frozen source drift: ' + name)
    return files


def inventory(home):
    home = Path(home)
    return {p.relative_to(home).as_posix():file_digest(p) for p in sorted(home.rglob('*')) if p.is_file()} if home.exists() else {}


def inspect_home(home):
    imports()
    from labs.game_loop.verify_survival_population import inspect_home as inspect
    result = inspect(home)
    if result['state'] is not None:
        from mecha_game.campaign_recovery import validate_ledger_state
        validate_ledger_state(result['state'], Path(home)/'campaign.sqlite3')
    return result


def has_fact(state, axis, tier, threshold):
    return any(fact.get('axis') == axis and type(fact.get('tier')) is int and fact['tier'] >= tier
               and isinstance(fact.get('metric_value'), (int,float)) and not isinstance(fact['metric_value'],bool)
               and math.isfinite(fact['metric_value']) and fact['metric_value'] >= threshold
               and isinstance(fact.get('threshold'), (int,float)) and fact['threshold'] >= threshold
               for fact in state.get('unlocks', []))


def validate_transition(stage, index, before, previous):
    spec = stage_spec(stage, index); state = before['state']
    if stage in ('role-era','density-earn') and index == 0:
        if state is not None or any(not key.startswith('model_cache/') for key in before['files']):
            raise ValueError('First era requires an isolated empty home except frozen cache.')
        if previous is not None: raise ValueError('First era cannot reuse a previous stage.')
        return
    if (state is None or state.get('population_policy') != POLICY or state.get('era_config') != CONFIG
            or previous is None or previous.get('status') != 'completed'
            or previous.get('after', {}).get('files') != before['files']):
        raise ValueError('Existing stage needs exact completed prior save bytes and production configuration.')
    if spec['era']:
        if state.get('status') != 'active' or state.get('era_count') != index or state.get('base_seed') != spec['seed']:
            raise ValueError('Wrong campaign seed, era boundary or ended population.')
        wanted = 'role-era' if stage == 'role-era' else 'density-earn'
        if previous.get('stage') != wanted or previous.get('index') != index-1:
            raise ValueError('The fixed protocol does not authorize this next era.')
    elif state.get('base_seed') not in (20261030,20261031) or index >= state.get('era_count',0):
        raise ValueError('Read/reproduction stage has no recorded selected era.')
    if stage in ('density-off','density-on','density-duplicate'):
        if state.get('base_seed') != 20261031 or not has_fact(state,'storm_record',1,1.1):
            raise ValueError('Density requires the actual fixed earned storm fact.')


def role_decision(state):
    current = state['slip_profile']['grid'].get('allowed_organ_roles')
    if current is None or not set(STARTER_ROLES).issubset(current) or set(current)-set((*STARTER_ROLES,*ROLES)):
        raise ValueError('Role journey requires its explicit starter-derived covenant.')
    next_role = next((role for role in ROLES if role not in current), None)
    threshold = None if next_role is None else 16 if next_role == 'ornament' else 26
    earned = next_role is not None and has_fact(state,'niche_mastery',ROLES.index(next_role)+1,threshold)
    return dict(active_roles=list(current), next_role=next_role, threshold=threshold,
                spend=next_role if earned else None, disposition='earned' if earned else 'locked' if next_role else 'complete')


def prepare_release(home, inputs, role):
    """Keep old consumed examples, but W stages only this newly allowed body."""
    home=Path(home).resolve();directory=home/'released'
    if not directory.resolve().is_relative_to(home):raise ValueError('Release inbox escapes the selected home.')
    directory.mkdir(exist_ok=True)
    expected={grid['grid_id']:grid for grid in inputs['seed_grids'] if grid['grid_id'] in inputs['role_exemplars'].values()}
    moves=[]
    for path in sorted(directory.glob('*.json')):
        if path.stem not in expected or read(path)!=expected[path.stem]:
            raise ValueError('Unexpected release inbox bytes; preserve them rather than changing the fixed journey.')
        archived=directory/'consumed'/path.name
        if not path.resolve().is_relative_to(home) or not archived.resolve().is_relative_to(home):
            raise ValueError('Consumed-release source/target escapes the selected home.')
        if archived.exists():raise ValueError('Consumed release already exists; no repeated spend/staging.')
        moves.append(dict(source=path.relative_to(home).as_posix(),target=archived.relative_to(home).as_posix(),sha256=file_digest(path)))
    for move in moves:
        path=home/move['source'];archived=home/move['target']
        archived.parent.mkdir(exist_ok=True);path.rename(archived)
        if file_digest(archived)!=move['sha256']:raise ValueError('Consumed release bytes changed.')
    grid=expected[inputs['role_exemplars'][role]]
    write(directory/(grid['grid_id']+'.json'),grid)
    return dict(grid_id=grid['grid_id'],moves=moves,new_release=dict(path='released/'+grid['grid_id']+'.json',sha256=file_digest(directory/(grid['grid_id']+'.json'))))


def validate_inputs(inputs):
    if (inputs.get('format') != INPUT_FORMAT or len(inputs.get('seed_grids',[])) != 50
            or inputs.get('training_options') != TRAINING or not isinstance(inputs.get('generation_model'),dict)
            or not isinstance(inputs.get('repair_model'),dict) or not isinstance(inputs.get('input_sources'),list)
            or not isinstance(inputs.get('repair_training'),dict)
            or len(inputs.get('weather_sources',{}).get('storm',[])) != 6
            or not inputs.get('weather_sources',{}).get('real') or set(inputs.get('role_exemplars',{})) != set(ROLES)):
        raise ValueError('Frozen inputs do not match registered product setup.')
    imports()
    from mecha_game.covenant import starter_role_covenant
    from mecha_game.campaign import build_weather_source
    from mecha_engine.slip import is_grid_aligned
    paths=sorted((ROOT/'data/seed_grids_16x16').glob('mg_seed16_*.json'))
    sources=[row for row in inputs['input_sources'] if row.get('role')=='seed_corpus']
    if len(paths)!=50 or len(sources)!=50 or [row.get('source_position') for row in sources]!=list(range(50)):
        raise ValueError('Frozen corpus is not the full sorted product source list.')
    for index,(path,source) in enumerate(zip(paths,sources)):
        raw=path.read_bytes()
        if base64.b64decode(source['data_base64'],validate=True)!=raw or inputs['seed_grids'][index]!=json.loads(raw):
            raise ValueError('Frozen corpus grid/raw source differs: '+path.name)
    if inputs['slip_profile']!=read(ROOT/'data/slips/valid/slip_v2_cleanliness.json'):
        raise ValueError('The protocol requires its existing cleanliness base covenant.')
    if any(inputs['weather_sources'][name]!=build_weather_source(name) for name in ('storm','real')):
        raise ValueError('Frozen weather is not the original product forecast order.')
    if inputs['repair_training'] != expected_training(inputs):
        raise ValueError('Repair training provenance differs from frozen first40 raw sources/options.')
    profile = starter_role_covenant(inputs['slip_profile'])
    for role in ROLES:
        after = deepcopy(profile); after['grid']['allowed_organ_roles'].append(role)
        eligible = [grid for grid in inputs['seed_grids'] if not is_grid_aligned(grid,profile).ok and is_grid_aligned(grid,after).ok]
        if not eligible or eligible[0]['grid_id'] != inputs['role_exemplars'][role]:
            raise ValueError('Role exemplar is not the first sorted newly admissible frozen body: '+role)
        profile = after


def expected_training(inputs):
    grids=inputs['seed_grids'][:40]
    sources=[dict(source_position=row.get('source_position'),raw_sha256=digest(base64.b64decode(row['data_base64'],validate=True)))
             for row in inputs['input_sources'] if row.get('role')=='seed_corpus'
             and type(row.get('source_position')) is int and row['source_position']<40 and 'data_base64' in row]
    if [row['source_position'] for row in sources] != list(range(40)):
        raise ValueError('Frozen first40 training source occurrences are missing or reordered.')
    return dict(training_contract='mechagotchi_repair_training_v2',
        trainer_options={key:value for key,value in TRAINING.items() if key!='repair_training_count'},
        ordered_training_sha256=digest(encoded(grids)),training_grids=grids,source_identities=sources)


def install_cache(home, inputs):
    imports()
    from mecha_game.execution import runtime_identity
    training=expected_training(inputs);identity=runtime_identity()
    if not identity.get('available'):raise ValueError('Cache runtime identity unavailable.')
    material=dict(contract=training['training_contract'],ordered_training_sha256=training['ordered_training_sha256'],
        source_identities=training['source_identities'],trainer_options=training['trainer_options'],runtime=identity)
    key=digest(encoded(material));raw_model=encoded(inputs['repair_model'])
    envelope=dict(format='mechagotchi_repair_cache_v2',key=key,key_material=material,
        model_sha256=digest(raw_model),model_data_base64=base64.b64encode(raw_model).decode('ascii'))
    directory=Path(home)/'model_cache';directory.mkdir(parents=True,exist_ok=True)
    path=directory/f'repair_model_v2_{key}.json';raw=encoded(envelope)+b'\n'
    if path.exists():
        if path.read_bytes()!=raw:raise ValueError('Existing frozen cache differs; preserve it.')
    else:
        with path.open('xb') as stream:stream.write(raw)
    return dict(path=path.name,sha256=file_digest(path),model_sha256=envelope['model_sha256'])


def observer_adapter(original, captured):
    """Only add the existing deep-copy observation seam, once per invocation."""
    called = False
    def wrapped(*args, **kwargs):
        nonlocal called
        if called: raise ValueError('Instrument refuses an additional engine computation.')
        if kwargs.get('evaluation_callback') is not None: raise ValueError('Existing observer cannot be replaced.')
        called = True
        return original(*args, **{**kwargs, 'evaluation_callback':lambda item:captured.append(deepcopy(item))})
    return wrapped


def compare_density(off, on):
    """Judge original first-cycle observations; unmatched later generations stay visible."""
    def indexed(rows):
        found = {}
        for row in rows:
            key = (row['generation_index'],row['candidate_index'])
            if key in found: raise ValueError('Duplicate candidate occurrence in density observations.')
            found[key] = row
        return found
    left, right = indexed(off), indexed(on); generations=[]
    for generation in sorted({key[0] for key in left}|{key[0] for key in right}):
        keys = sorted(key for key in left if key[0] == generation)
        equal_keys = keys == sorted(key for key in right if key[0] == generation)
        comparable = bool(keys) and equal_keys
        difference=0;positive=False;nonnegative=True
        for key in keys if equal_keys else []:
            a,b=left[key],right[key]; ac=a.get('cycles',[]);bc=b.get('cycles',[])
            identity=(digest(encoded(a['candidate_grid']))==digest(encoded(b['candidate_grid'])) and a['run_seed']==b['run_seed'])
            cycles=bool(ac and bc) and ac[0]['cycle']==bc[0]['cycle']==1 and ac[0]['damage_seed']==bc[0]['damage_seed']
            comparable = comparable and identity and cycles
            delta=b['effective_dropout_rate']-a['effective_dropout_rate'];positive=positive or delta>0;nonnegative=nonnegative and delta>=0
            if cycles:difference += bc[0]['removed_cell_count']-ac[0]['removed_cell_count']
        generations.append(dict(generation=generation,comparable=comparable,candidates=len(keys),
            first_cycle_difference=difference if comparable else None,positive_dropout_delta=positive if comparable else None,
            nonnegative_dropout_deltas=nonnegative if comparable else None))
    comparable=[row for row in generations if row['comparable']]
    total=sum(row['first_cycle_difference'] for row in comparable)
    qualified=bool(comparable) and all(row['nonnegative_dropout_deltas'] and row['first_cycle_difference']>=0 for row in comparable) and any(row['positive_dropout_delta'] and row['first_cycle_difference']>0 for row in comparable)
    return dict(format='x8_production_density_comparison_v1',generations=generations,
        comparable_first_cycle_difference=total,verdict='QUALIFIED_CONSEQUENCE' if qualified else 'REFUSE',
        claim='Matched production damage consequence only; no survival benefit, difficulty or food claim.')


def observations_match(report, rows):
    """Require every observed occurrence to equal its authoritative saved report."""
    imports()
    from mecha_engine.runtime.care import care_grid_sha256
    expected={(generation['generation'],index):creature
              for generation in report['generations'] for index,creature in enumerate(generation['creatures'])}
    if len(rows)!=len(expected):return False
    seen=set()
    for row in rows:
        key=(row['generation_index'],row['candidate_index'])
        if key in seen or key not in expected or row['creature']!=expected[key]:return False
        seen.add(key)
        if row['run_seed']!=report['rng_seed']+key[0]*100000+key[1]:return False
        breeding=row['creature']['breeding']
        if (care_grid_sha256(row['candidate_grid'])!=breeding['candidate_grid_sha256']
                or care_grid_sha256(row['final_grid'])!=breeding['final_grid_sha256']):return False
        cycles=[{k:v for k,v in cycle.items() if k not in ('frames','damage_seed')} for cycle in row['cycles']]
        if cycles!=row['creature']['cycles']:return False
        if any(cycle['damage_seed']!=row['run_seed']*10+cycle['cycle'] for cycle in row['cycles']):return False
    return seen==set(expected)


def saved_era(home, index):
    imports()
    from mecha_engine.storage import load_era_execution,load_era_elites
    from mecha_game.execution import decode_execution_inputs,validate_execution_outputs
    state=read(Path(home)/'campaign_state.json');campaign=state['campaign_id']
    with closing(sqlite3.connect((Path(home)/'campaign.sqlite3').resolve().as_uri()+'?mode=ro',uri=True)) as conn:
        bundle=load_era_execution(conn,campaign,index)
        row=conn.execute('SELECT report_json FROM eras WHERE campaign_id=? AND era_index=?',(campaign,index)).fetchone()
        if row is None:raise ValueError('Requested saved era does not exist.')
        report=json.loads(row[0]);elites=load_era_elites(conn,campaign,index)
    validate_execution_outputs(bundle,report,elites)
    return bundle,decode_execution_inputs(bundle),report,elites


def verify_fact(home,state,axis):
    """Authenticate used facts against their actual immutable saved era metrics."""
    facts=[f for f in state.get('unlocks',[]) if f['axis']==axis]
    for fact in facts:
        _,_,report,_=saved_era(home,fact['earned_era_index'])
        if axis=='niche_mastery':
            value=report['summary']['archive']['filled_niches'];threshold=(16,26,36)[fact['tier']-1]
            path='report.summary.archive.filled_niches'
        else:
            if report['living_population']['termination']['ended']:raise ValueError('Ended era cannot earn survived-storm fact.')
            value=max(row['dropout_multiplier'] for row in report['cubff_pressure']['by_generation'])
            threshold=(1.1,1.4)[fact['tier']-1];path='derived.max_dropout_multiplier_survived'
        if fact.get('metric_value')!=value or fact.get('threshold')!=threshold or fact.get('metric_path')!=path or value<threshold:
            raise ValueError('Earned fact disagrees with its real saved era.')
    return facts


def native_run(args, before, inputs, output, evaluations, role):
    if os.name!='nt':raise ValueError('Native qualification requires Windows SDL; no dummy fallback.')
    os.environ.update(SDL_VIDEODRIVER='windows',SDL_AUDIODRIVER='dummy',PYGAME_HIDE_SUPPORT_PROMPT='1')
    imports()
    import pygame
    from unittest.mock import patch
    import mecha_game.campaign as campaign_module
    from mecha_game.app import run
    from mecha_game.footer import FooterPager
    from mecha_game.era_work import EraWork
    launch=['--keeper-dir',str(args.home),'--era-scale','session','--fps','0','--tick-frames','1000',
            '--view','preparation','--frames','30','--launch-info',str(output/'launch.json')]
    if args.stage in ('role-era','density-earn') and args.index==0:
        launch += ['--population-policy',POLICY,'--campaign-seed',str(stage_spec(args.stage,args.index)['seed']),
                   '--care-selection','off','--prepare-survival-regime','sheltered','--prepare-density-pressure','off']
        if args.stage=='role-era':launch.append('--starter-roles')
    keys=[]
    if args.stage=='role-era' and role and role['spend']:keys.append(pygame.K_5)
    if args.stage in ERA_STAGES:
        keys.append(pygame.K_c) # leave covenant view for weather controls
        keys.append(pygame.K_4 if args.stage in ('density-off','density-on') else pygame.K_3)
        if args.stage=='density-on': keys += [pygame.K_c,pygame.K_6,pygame.K_c]
        if args.stage=='role-era' and role and role['spend']:keys.append(pygame.K_w)
        keys.append(pygame.K_e)
    batches=[[]]+[[pygame.event.Event(pygame.KEYDOWN,key=key,mod=0,repeat=False),pygame.event.Event(pygame.KEYUP,key=key,mod=0)] for key in keys]+[[],[pygame.event.Event(pygame.QUIT)]]
    iterator=iter(batches);batch=-1;pages=[];screens=[];joins=[];polls=0
    flip=pygame.display.flip;layout=FooterPager.layout;join=EraWork.join
    def events():
        nonlocal batch
        batch+=1;return next(iterator,[pygame.event.Event(pygame.QUIT)])
    def poll():
        nonlocal polls
        polls+=1;return pygame.event.Event(pygame.NOEVENT)
    def render():
        flip()
        if batch>=0 and batch not in [row['batch'] for row in screens]:
            path=output/f'screen-{batch:02}.png';pygame.image.save(pygame.display.get_surface(),str(path))
            screens.append(dict(batch=batch,file=path.name,sha256=file_digest(path),driver=pygame.display.get_driver()))
    def record_layout(pager,lines,measure,width,rows):
        result=layout(pager,lines,measure,width,rows)
        if len(pages)<100:pages.append(dict(batch=batch,all=list(lines),visible=list(result.lines),fits=len(result.lines)<=rows and all(measure(line)<=width for line in result.lines)))
        return result
    def record_join(work):
        join(work);joins.append(dict(alive=work.thread.is_alive(),status=work.snapshot()))
    code=None
    try:
        with patch('pygame.event.get',events),patch('pygame.event.poll',poll),patch('pygame.display.flip',render),\
                patch.object(FooterPager,'layout',record_layout),patch.object(EraWork,'join',record_join),\
                patch.object(campaign_module,'evolve',observer_adapter(campaign_module.evolve,evaluations)):
            code=run(launch)
    finally:
        result=dict(returncode=code,arguments=launch,pages=pages,screenshots=screens,joins=joins,busy_poll_count=polls,
            key_names=[pygame.key.name(key) for key in keys],method='Injected SDL source events in a Windows window; not OS keyboard/human usability.')
        write(output/'source-events.json',result)
    if code!=0 or not screens or any(row['driver']!='windows' for row in screens) or any(not row['fits'] for row in pages):
        raise ValueError('Native process/driver/layout invariant failed.')
    return result


def audit_native_era(args, before, after, inputs, evaluations, role):
    imports()
    from mecha_game.covenant import starter_role_covenant
    from mecha_game.execution import population_arguments,blob_json
    from mecha_game.campaign import legibility_blend_for
    bundle,data,report,elites=saved_era(args.home,args.index)
    profile=deepcopy(before['state']['slip_profile'] if before['state'] else inputs['slip_profile'])
    if args.stage=='role-era' and args.index==0:profile=starter_role_covenant(profile)
    if role and role['spend']:profile['grid']['allowed_organ_roles'].append(role['spend'])
    expected_weather=inputs['weather_sources']['real' if args.stage in ('density-off','density-on') else 'storm']
    settings=population_arguments(bundle)
    prior_state=before['state'] or {}
    facts=prior_state.get('inherited_unlocks',[])+prior_state.get('unlocks',[])
    checks=dict(one_era=sum(after['era_counts'].values())-sum(before['era_counts'].values())==1,
        full_corpus=data['seed_grids']==inputs['seed_grids'],covenant=data['slip_profile']==profile,
        generation_model=asdict(data['generation_model'])==inputs['generation_model'],repair_model=data['repair_model']==inputs['repair_model'],
        repair_training=blob_json(bundle,bundle['manifest']['inputs']['repair_training_sha256'])==inputs['repair_training'],
        readability_model=data['legibility_model']==inputs['legibility_model'],configuration=data['effective_config']==CONFIG,
        readability_selection=data['readability_selection']=={**inputs['legibility_model'],'blend':legibility_blend_for(facts)},
        fixed_seed=data['rng_seed']==stage_spec(args.stage,args.index)['seed']+args.index*1_000_000,
        weather=data['cubff_pressure_source']==expected_weather,population=settings.get('population_policy')==POLICY,
        start=settings.get('founder_start_mode')==('bootstrap' if args.index==0 else 'continue'),
        sheltered=settings.get('survival_regime')=='sheltered',density=settings.get('cubff_density_pressure')==(args.stage=='density-on'),
        care_off=data.get('care_selection_policy','off')=='off',
        all_actual_evaluations=observations_match(report,evaluations),
        breeders_exact=blob_json(bundle,bundle['manifest']['ordered_breeders_sha256'])==report['living_population']['final_breeders'])
    if before['state']:
        checks['prior_history_preserved']=all(after['historical_era_sha256'].get(k)==v for k,v in before['historical_era_sha256'].items())
        checks['prior_elites_preserved']=all(after['historical_elite_sha256'].get(k)==v for k,v in before['historical_elite_sha256'].items())
    role_effect=None
    if role and role['spend']:
        grid_id=inputs['role_exemplars'][role['spend']]
        occurrences=bundle['manifest']['founder_occurrences']
        admitted=[row for row in occurrences if row.get('grid_id')==grid_id]
        descendants=[row for row in evaluations if row['generation_index']==0 and row['parent_grid']['grid_id']==grid_id]
        checks['role_saved']=after['state']['slip_profile']==profile
        checks['role_admitted']=bool(admitted) and any(row.get('admitted') is True for row in admitted)
        checks['role_evaluated']=bool(descendants)
        from mecha_engine.runtime.care import care_grid_sha256
        admitted_slots={row['ordinal'] for row in admitted if row.get('admitted') is True}
        checks['role_parent_bound']=bool(descendants) and all(
            row['creature']['breeding']['parent_occurrence'].get('kind')=='submitted_founder'
            and row['creature']['breeding']['parent_occurrence'].get('submission_index') in admitted_slots
            and row['creature']['breeding']['parent_occurrence'].get('grid_sha256')==care_grid_sha256(row['parent_grid'])
            for row in descendants)
        role_effect=dict(role=role['spend'],grid_id=grid_id,admissions=admitted,
                         evaluated_occurrences=[row['creature']['breeding']['occurrence'] for row in descendants])
    result=dict(report=report,elites=elites,manifest=bundle['manifest'],population_inputs=settings,
        input_summary=dict(rng_seed=data['rng_seed'],founder_grids=data['founder_grids'],weather=data['cubff_pressure_source'],covenant=data['slip_profile'],effective_config=data['effective_config']),
        role=role,role_effect=role_effect,checks=checks)
    return result


def reproduce(args,evaluations):
    imports()
    from unittest.mock import patch
    import mecha_game.execution as execution
    state=read(args.home/'campaign_state.json')
    with closing(sqlite3.connect((args.home/'campaign.sqlite3').resolve().as_uri()+'?mode=ro',uri=True)) as conn,\
            patch.object(execution,'evolve',observer_adapter(execution.evolve,evaluations)):
        result=execution.reproduce_era(conn,state['campaign_id'],args.index)
    if result['status']!='matched' or result['differing_paths']:raise ValueError('Immutable reproduction did not MATCH.')
    return result


def execute(args):
    started=time.monotonic();wall=utc();args.home=args.home.resolve();output=args.output.resolve()
    spec=stage_spec(args.stage,args.index)
    if not math.isfinite(args.remaining_seconds) or not 0<args.remaining_seconds<=1200:raise ValueError('Invalid parent budget.')
    if output.is_relative_to(args.home) or args.home.is_relative_to(output):raise ValueError('Evidence output and save home must be disjoint.')
    output.mkdir(parents=True,exist_ok=False)
    initial_source_sha=file_digest(args.source_manifest) if args.source_manifest.is_file() else None
    initial_input_sha=file_digest(args.inputs) if args.inputs.is_file() else None
    write(output/'start.json',dict(format=FORMAT,stage=args.stage,index=args.index,home=str(args.home),started_utc=wall,
        source_manifest_sha256=initial_source_sha,inputs_sha256=initial_input_sha,
        command=sys.argv,stage_deadline_seconds=min(spec['seconds'],args.remaining_seconds),
        parent_budget_authority='Coordinator owns global budget and process-tree watchdog; no worker-granted extension.'))
    checks={};before=after=None;error=None;source_sha=input_sha=None;status='error';result=None;evaluations=[]
    try:
        source=checked_source(args.source_manifest);source_sha=file_digest(args.source_manifest)
        inputs=read(args.inputs);input_sha=file_digest(args.inputs)
        if source_sha!=initial_source_sha or input_sha!=initial_input_sha:raise ValueError('Frozen bytes changed after stage start.')
        validate_inputs(inputs)
        before=inspect_home(args.home)
        previous=verified_receipt(args.previous) if args.previous else None
        if previous and (previous.get('source_manifest_sha256')!=source_sha or previous.get('inputs_sha256')!=input_sha):
            raise ValueError('Previous stage used different frozen source or inputs.')
        validate_transition(args.stage,args.index,before,previous)
        role=None
        if args.stage=='role-era' and before['state']:
            verify_fact(args.home,before['state'],'niche_mastery');role=role_decision(before['state'])
            if role['spend']:
                imports();from mecha_engine.slip import is_grid_aligned
                exemplar=next(grid for grid in inputs['seed_grids'] if grid['grid_id']==inputs['role_exemplars'][role['spend']])
                if is_grid_aligned(exemplar,before['state']['slip_profile']).ok:raise ValueError('Role exemplar was not blocked before spending.')
                write(output/'release-preparation.json',prepare_release(args.home,inputs,role['spend']))
        if args.stage in ('density-off','density-on','density-duplicate'):
            verify_fact(args.home,before['state'],'storm_record')
        if args.stage in ERA_STAGES:
            install_cache(args.home,inputs)
        if args.stage in (*ERA_STAGES,'restart'):
            native_run(args,before,inputs,output,evaluations,role)
            after=inspect_home(args.home)
            if args.stage in ERA_STAGES:
                result=audit_native_era(args,before,after,inputs,evaluations,role);checks.update(result['checks'])
            else:
                checks['restart_state_unchanged']=before['state']==after['state']
                checks['restart_ledger_unchanged']=before['files'].get('campaign.sqlite3')==after['files'].get('campaign.sqlite3')
                checks['restart_plan_unchanged']=before['files'].get('era_plan.json')==after['files'].get('era_plan.json')
                result=dict(checks=checks,claim='Native restart/persistence only; no era executed.')
        else:
            result=reproduce(args,evaluations);after=inspect_home(args.home)
            checks.update(immutable_reproduction=result['status']=='matched',read_only=before['files']==after['files'])
            if args.stage=='density-duplicate':
                directory=args.reference or args.previous;reference=verified_receipt(directory)
                if reference.get('stage')!='density-off' or reference.get('index')!=1:raise ValueError('Duplicate requires the exact density OFF receipt.')
                expected=read(Path(directory)/'evaluations.json');checks['duplicate_observations_exact']=evaluations==expected
                recorded=read(Path(directory)/'result.json');checks['duplicate_report_exact']=result['report']==recorded['report'];checks['duplicate_elites_exact']=result['elites']==recorded['elites']
        write(output/'evaluations.json',evaluations);write(output/'result.json',result)
        checks['source_unchanged']=checked_source(args.source_manifest)==source and file_digest(args.source_manifest)==source_sha
        checks['inputs_unchanged']=file_digest(args.inputs)==input_sha
        checks['within_stage_budget']=time.monotonic()-started<=min(spec['seconds'],args.remaining_seconds)
        if not checks or not all(value is True for value in checks.values()):raise ValueError('Qualification invariant failed: '+', '.join(k for k,v in checks.items() if v is not True))
        status='completed'
    except BaseException as exc:
        error=repr(exc)
        with (output/'error.txt').open('x',encoding='utf-8') as stream:stream.write(traceback.format_exc())
        if not (output/'evaluations.json').exists():write(output/'evaluations.json',evaluations)
        if result is not None and not (output/'result.json').exists():write(output/'result.json',result)
    finally:
        outputs={p.relative_to(output).as_posix():file_digest(p) for p in sorted(output.rglob('*')) if p.is_file()}
        terminal=dict(format=FORMAT,stage=args.stage,index=args.index,home=str(args.home),status=status,error=error,
            started_utc=wall,finished_utc=utc(),elapsed_seconds=time.monotonic()-started,checks=checks,outputs=outputs,
            before=before,after=after,source_manifest_sha256=source_sha,inputs_sha256=input_sha)
        write(output/'terminal.json',terminal)
    return terminal


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage',choices=STAGES,required=True);parser.add_argument('--index','--era-index',dest='index',type=int,required=True)
    for name in ('home','output','inputs','source-manifest'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--previous',type=Path);parser.add_argument('--reference',type=Path)
    parser.add_argument('--remaining-seconds',type=float,required=True)
    result=execute(parser.parse_args(argv));print(json.dumps({key:result[key] for key in ('stage','index','status','elapsed_seconds','error')}))
    return 0 if result['status']=='completed' else 1


if __name__=='__main__':raise SystemExit(main())
