"""One bounded X8 native journey stage; qualification is parent-coordinated.

This tool does not select a new seed, train a model, retry a stage, run a second
era, claim OS keyboard input, or grant an experiment budget. Source mode uses
injected SDL events in a real Windows SDL process. Detached EXE mode uses the
corresponding existing CLI action. Their evidence labels remain distinct.

The parent must invoke each stage separately, debit its full outer elapsed time
against the shared 1,200-second ledger and 120-second native reservation, enforce
the outer process-tree deadline, and authorize the once-only fallback. A worker
receipt cannot prove global budget accounting or human usability.
"""
from __future__ import annotations

import argparse
import base64
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
FORMAT = 'survival_population_native_stage_v1'
POLICY = 'generation_survivors_v1'
SEEDS = tuple(range(20260700, 20260710))
ACTIONS = ('startup', 'direct-era', 'fallback-sheltered-era', 'fallback-stress-era', 'restart',
           'review', 'create-successor', 'successor-era', 'finish-pending', 'reproduce')
ERA_ACTIONS = ('direct-era', 'fallback-sheltered-era', 'fallback-stress-era', 'successor-era')
CONFIG = dict(generations=6, population=16, damage_cycles=2, ticks=16, dropout_rate=.2)
TRAINING = dict(dropout_rates=[.1, .2, .3, .4], damage_instances=1, epochs=40,
                learning_rate=1.5, live_class_weight=3., rng_seed=20260707, vocabulary='legacy')


def read(path): return json.loads(Path(path).read_bytes())
def digest(raw): return hashlib.sha256(raw).hexdigest()
def file_digest(path): return digest(Path(path).read_bytes())
def utc(): return datetime.now(timezone.utc).isoformat()
def encoded(value): return json.dumps(value, ensure_ascii=True, separators=(',', ':'), allow_nan=False).encode()
def write(path, value):
    with Path(path).open('xb') as stream:
        stream.write(encoded(value) + b'\n')


def imports():
    for name in ('', 'game/src', 'packages/mecha_engine/src'):
        value = str(ROOT/name)
        if value not in sys.path: sys.path.insert(0, value)


def checked_source(path):
    value = read(path)
    if value.get('format') != 'x8_source_manifest_v1' or not isinstance(value.get('files'), dict) or not value['files']:
        raise ValueError('A nonempty frozen X8 source manifest is required.')
    for name, expected in value['files'].items():
        target = (ROOT/name).resolve()
        if Path(name).is_absolute() or not target.is_relative_to(ROOT) or file_digest(target) != expected:
            raise ValueError('Frozen source drift: ' + str(name))
    own = 'labs/game_loop/verify_survival_population.py'
    if own not in value['files']:
        raise ValueError('The native instrument must be inside the frozen source closure.')
    return value['files']


def verified_receipt(directory):
    directory = Path(directory).resolve()
    receipt = read(directory/'terminal.json')
    if receipt.get('status') != 'completed' or any(value is not True for value in receipt.get('checks', {}).values()):
        raise ValueError('A prior failed/interrupted stage is not reusable.')
    for name, expected in receipt.get('outputs', {}).items():
        path = (directory/name).resolve()
        if not path.is_relative_to(directory) or file_digest(path) != expected:
            raise ValueError('Prior receipt output changed: ' + name)
    return receipt


def select_qualified_seed(judgment):
    if (judgment.get('cohort_verdict') != 'ADOPT' or not judgment.get('checks')
            or any(value is not True for value in judgment['checks'].values())):
        raise ValueError('Native scientific journey requires the qualified fixed cohort.')
    seeds = judgment.get('genuine_extinct_seeds')
    if not isinstance(seeds, list) or not seeds or any(type(seed) is not int or seed not in SEEDS for seed in seeds):
        raise ValueError('No registered D genuine-extinction seed is available.')
    selected = min(seeds)
    if judgment.get('lowest_extinct_seed') != selected:
        raise ValueError('The journey must use the lowest qualified D extinction seed.')
    rows = [row for row in judgment.get('counts', []) if row.get('seed') == selected and row.get('arm') == 'D']
    if len(rows) != 1 or rows[0].get('termination', {}).get('genuine_lifecycle_extinction') is not True:
        raise ValueError('Selected cohort row does not record genuine lifecycle extinction.')
    return selected


def frozen_reference(trial, seed, inputs, input_sha, source, arm='D'):
    receipt = verified_receipt(trial)
    expected = dict(stage='cohort', backend='package', arm=arm, seed=seed)
    if (receipt.get('plan') != expected or receipt.get('inputs_sha256') != input_sha
            or receipt.get('source_sha256') != source):
        raise ValueError('Reference trial differs from the selected frozen cohort inputs.')
    result = read(Path(trial)/'result.json')
    if not result.get('checks') or any(value is not True for value in result['checks'].values()):
        raise ValueError('Reference trial did not pass its instrument invariants.')
    imports()
    from labs.runtime_integration.survival_population_gate import validate_result
    validate_result(result, expected, inputs)
    return result


def inventory(home):
    home = Path(home)
    return {p.relative_to(home).as_posix(): file_digest(p) for p in home.rglob('*') if p.is_file()} if home.exists() else {}


def inspect_home(home):
    """Read actual saved facts without inventing missing state or running a model."""
    home = Path(home)
    state = read(home/'campaign_state.json') if (home/'campaign_state.json').is_file() else None
    pet = read(home/'companion.json') if (home/'companion.json').is_file() else None
    archives = {}; eras = {}; counts = {}
    ledger = home/'campaign.sqlite3'
    if ledger.exists():
        with closing(sqlite3.connect(ledger.resolve().as_uri()+'?mode=ro', uri=True)) as conn:
            for campaign, era, raw in conn.execute('SELECT campaign_id,era_index,report_json FROM eras ORDER BY campaign_id,era_index'):
                eras[f'{campaign}/{era}'] = digest(raw.encode())
            for campaign, era, niche, raw in conn.execute('SELECT campaign_id,era_index,niche_key,elite_json FROM elites ORDER BY campaign_id,era_index,niche_key'):
                archives[f'{campaign}/{era}/{niche}'] = digest(raw.encode())
            for campaign, count in conn.execute('SELECT campaign_id,count(*) FROM eras GROUP BY campaign_id'):
                counts[campaign] = count
    return dict(state=state, keeper_id=(pet or {}).get('chronicle', {}).get('keeper_id'),
                companion_life_id=(pet or {}).get('chronicle', {}).get('current_life_id'),
                era_counts=counts, historical_era_sha256=eras, historical_elite_sha256=archives,
                files=inventory(home))


def validate_frozen_inputs(inputs):
    if (inputs.get('format') != 'surviving_population_inputs_v1' or len(inputs.get('seed_grids', [])) != 50
            or inputs.get('training_options') != dict(repair_training_count=40, **TRAINING)
            or inputs.get('readability_selection') != {**inputs.get('legibility_model', {}), 'blend': .7}
            or len(inputs.get('weather_sources', {}).get('storm', [])) != 6):
        raise ValueError('Native inputs differ from the registered production corpus/model/configuration.')


def cache_envelope(inputs, runtime):
    """Use the existing cache contract and frozen model bytes, never retrain."""
    validate_frozen_inputs(inputs)
    grids = inputs['seed_grids'][:40]
    identities = [dict(source_position=row.get('source_position'),
                       raw_sha256=digest(base64.b64decode(row['data_base64'], validate=True)))
                  for row in inputs['input_sources'] if row.get('role') == 'seed_corpus'
                  and type(row.get('source_position')) is int and row['source_position'] < 40
                  and 'data_base64' in row]
    material = dict(contract='mechagotchi_repair_training_v2', ordered_training_sha256=digest(encoded(grids)),
                    source_identities=identities, trainer_options=TRAINING, runtime=runtime)
    key = digest(encoded(material)); model = encoded(inputs['repair_model'])
    return f'repair_model_v2_{key}.json', dict(format='mechagotchi_repair_cache_v2', key=key,
        key_material=material, model_sha256=digest(model), model_data_base64=base64.b64encode(model).decode())


def install_frozen_cache(home, inputs):
    imports()
    from mecha_game.execution import runtime_identity
    identity = runtime_identity()
    if not identity.get('available'): raise ValueError('Native cache runtime identity is unavailable.')
    name, envelope = cache_envelope(inputs, identity)
    directory = Path(home)/'model_cache'; directory.mkdir(parents=True, exist_ok=True)
    path = directory/name; raw = encoded(envelope)+b'\n'
    if path.exists():
        if path.read_bytes() != raw: raise ValueError('Existing cache differs; bytes preserved.')
    else:
        with path.open('xb') as stream: stream.write(raw)
    return dict(path=name, sha256=file_digest(path), model_sha256=envelope['model_sha256'], runtime=identity)


def validate_stage(action, before, seed, previous=None, direct=None, home=None):
    state = before['state']
    if action in ('startup', 'direct-era', 'fallback-sheltered-era'):
        if state is not None or any(not name.startswith('model_cache/') for name in before['files']):
            raise ValueError('Fresh journey requires a separate empty save home.')
    else:
        if (state is None or state.get('population_policy') != POLICY or state.get('era_config') != CONFIG):
            raise ValueError('Stage needs the exact recorded production survivor campaign.')
        if (previous is None or previous.get('format') != FORMAT or previous.get('save_home') != str(Path(home).resolve())
                or previous.get('selected_seed') != seed):
            raise ValueError('Existing journey requires its completed previous stage receipt.')
        if previous.get('after', {}).get('files') != before['files']:
            raise ValueError('Save home changed since the preceding stage.')
    if action == 'fallback-sheltered-era':
        if (direct is None or direct.get('action') != 'direct-era' or direct.get('selected_seed') != seed
                or direct.get('after', {}).get('state', {}).get('unlocks') != []
                or direct.get('save_home') == str(Path(home).resolve())):
            raise ValueError('The once-only separate fallback requires the direct extinction with no earned facts.')
    if action == 'fallback-stress-era':
        if state['base_seed'] != seed or state['era_count'] != 1 or state['status'] != 'active':
            raise ValueError('Fallback stress is only the declared second era at the selected seed.')
        if previous.get('action') != 'fallback-sheltered-era':
            raise ValueError('Fallback cannot add eras or change order.')
    if action == 'create-successor' and state['status'] != 'extinct':
        raise ValueError('Only the actual ended population can create its successor.')
    if action == 'successor-era':
        if (state['status'] != 'active' or state['era_count'] != 0 or state['base_seed'] != seed+50_000_000
                or state.get('predecessor_campaign_id') is None):
            raise ValueError('Only the fresh declared successor may run this sheltered bootstrap.')
    if action == 'finish-pending':
        path = Path(home)/'era_plan.json'
        if not path.is_file() or read(path).get('pending') is None:
            raise ValueError('No completed journal exists; refusing to launch another era.')


def launch_arguments(action, home, output, seed, before, *, source=False):
    args = ['--keeper-dir', str(home), '--era-scale', 'session', '--fps', '0', '--scale', '10',
            '--tick-frames', '1', '--launch-info', str(output/'launch.json')]
    if action == 'reproduce':
        state = before['state']
        if state['era_count'] < 1: raise ValueError('There is no recorded era to reproduce.')
        return args+['--reproduce-era', str(state['era_count']-1), '--campaign-id', state['campaign_id'],
                     '--output', str(output/'comparison')]
    if action in ('direct-era', 'fallback-sheltered-era'):
        args += ['--population-policy', POLICY, '--campaign-seed', str(seed)]
    if action in ERA_ACTIONS:
        regime = 'stress_probe' if action in ('direct-era', 'fallback-stress-era') else 'sheltered'
        args += ['--prepare-weather', 'storm', '--prepare-survival-regime', regime, '--prepare-density-pressure', 'off']
    if action == 'create-successor' and not source: args += ['--create-successor']
    if not source and action in (*ERA_ACTIONS, 'finish-pending'): args += ['--eras', '1']
    return args+['--view', 'archive' if action == 'review' else 'preparation', '--frames', '12' if source else '2']


def source_worker(payload_path):
    """Exactly one app entry; UI instrumentation observes and injects keys only."""
    payload = read(payload_path)
    if os.name != 'nt': raise ValueError('Qualification requires a Windows SDL source process.')
    os.environ.update(SDL_VIDEODRIVER='windows', SDL_AUDIODRIVER='dummy', PYGAME_HIDE_SUPPORT_PROMPT='1')
    imports()
    import pygame
    from unittest.mock import patch
    from mecha_game.app import run
    from mecha_game.footer import FooterPager
    from mecha_game.era_work import EraWork
    output = Path(payload['output']); action = payload['action']
    key = (pygame.K_e if action in (*ERA_ACTIONS, 'finish-pending') else pygame.K_n if action == 'create-successor' else None)
    batches = [[], [pygame.event.Event(pygame.KEYDOWN, key=key, mod=0)] if key is not None else [], [],
               [pygame.event.Event(pygame.QUIT)]]
    iterator = iter(batches); pages=[]; screenshots=[]; joins=[]; poll_count=0; batch=-1
    flip = pygame.display.flip; layout = FooterPager.layout; join = EraWork.join
    def events():
        nonlocal batch
        batch += 1
        return next(iterator, [pygame.event.Event(pygame.QUIT)])
    def poll():
        nonlocal poll_count
        poll_count += 1
        return pygame.event.Event(pygame.NOEVENT)
    def render():
        flip()
        # One first/final frame per outer event batch; no unbounded busy-frame IO.
        if batch >= 0 and batch not in [item['batch'] for item in screenshots]:
            path=output/f'screen-{batch:02}.png'; pygame.image.save(pygame.display.get_surface(), str(path))
            screenshots.append(dict(batch=batch,path=path.name,sha256=file_digest(path)))
    def record_layout(pager, lines, measure, width, rows):
        result=layout(pager,lines,measure,width,rows)
        if len(pages)<60:
            pages.append(dict(batch=batch,all=list(lines),visible=list(result.lines),
                              fits=len(result.lines)<=rows and all(measure(line)<=width for line in result.lines)))
        return result
    def record_join(work):
        join(work); joins.append(dict(alive=work.thread.is_alive(),status=work.snapshot()))
    with patch('pygame.event.get',events), patch('pygame.event.poll',poll), patch('pygame.display.flip',render), \
            patch.object(FooterPager,'layout',record_layout), patch.object(EraWork,'join',record_join):
        code=run(payload['arguments'])
    write(output/'source-events.json',dict(returncode=code,pages=pages,screenshots=screenshots,joins=joins,
        busy_poll_count=poll_count,event_label='injected SDL keys in actual Windows source window; no OS keyboard automation'))
    return code


def effective_action_checks(decoded, action, selected_seed, before, inputs):
    """Bind later journey settings even where no first-era reference applies."""
    if action not in ERA_ACTIONS: raise ValueError('An era action is required.')
    continuing=action=='fallback-stress-era'
    offset=1_000_000 if continuing else 50_000_000 if action=='successor-era' else 0
    state=before.get('state') or {}
    facts=state.get('inherited_unlocks',[])+state.get('unlocks',[])
    tier=max((fact['tier'] for fact in facts if fact['axis']=='legibility'),default=0)
    blend=round(min(.9,.7+.05*tier),6)
    return dict(action_rng_seed=decoded.get('rng_seed')==selected_seed+offset,
        action_population_policy=decoded.get('population_policy')==POLICY,
        action_start_mode=decoded.get('founder_start_mode')==('continue' if continuing else 'bootstrap'),
        action_survival_regime=decoded.get('survival_regime')==('stress_probe' if action in ('direct-era','fallback-stress-era') else 'sheltered'),
        action_density_disabled=decoded.get('cubff_density_pressure') is False,
        action_readability_selection=decoded.get('readability_selection')=={**inputs['legibility_model'],'blend':blend},
        action_care_disabled=decoded.get('care_selection_policy','off')=='off' and decoded.get('care_evaluator','pristine')=='pristine'
            and all(context is None for context in decoded.get('founder_care_contexts') or []),
        action_founder_transport=isinstance(decoded.get('founder_grids'),list) if continuing else decoded.get('founder_grids')==[])


def audit_era(home, before, after, inputs, expected=None, *, action, selected_seed):
    imports()
    from mecha_engine.storage import load_era_execution, load_era_elites
    from mecha_game.execution import decode_execution_inputs, population_arguments, blob_json
    state=after['state']; index=state['era_count']-1; campaign=state['campaign_id']
    ledger=Path(home)/'campaign.sqlite3'
    with closing(sqlite3.connect(ledger.resolve().as_uri()+'?mode=ro',uri=True)) as conn:
        bundle=load_era_execution(conn,campaign,index)
        report=json.loads(conn.execute('SELECT report_json FROM eras WHERE campaign_id=? AND era_index=?',(campaign,index)).fetchone()[0])
        elites=load_era_elites(conn,campaign,index)
    decoded=decode_execution_inputs(bundle)
    from dataclasses import asdict
    checks=dict(corpus_exact=decoded['seed_grids']==inputs['seed_grids'], covenant_exact=decoded['slip_profile']==inputs['slip_profile'],
        generation_model_exact=asdict(decoded['generation_model'])==inputs['generation_model'], repair_model_exact=decoded['repair_model']==inputs['repair_model'],
        readability_model_exact=decoded['legibility_model']==inputs['legibility_model'], configuration_exact=decoded['effective_config']==CONFIG,
        weather_exact=decoded['cubff_pressure_source']==inputs['weather_sources']['storm'],
        breeders_exact=blob_json(bundle,bundle['manifest']['ordered_breeders_sha256'])==report['living_population']['final_breeders'])
    checks['one_era_only']=sum(after['era_counts'].values())-sum(before['era_counts'].values())==1
    checks.update(effective_action_checks(decoded,action,selected_seed,before,inputs))
    if expected is not None:
        ordered=[{'niche_key':niche,**expected['archive']['elites'][niche]} for niche in sorted(expected['archive']['elites'])]
        checks.update(exact_reference_report=report==expected['report'],exact_reference_elites=elites==ordered,
                      exact_reference_breeders=report['living_population']['final_breeders']==expected['report']['living_population']['final_breeders'])
    return dict(checks=checks,report=report,elites=elites,population_inputs=population_arguments(bundle),
                execution_manifest_sha256=digest(encoded(bundle['manifest'])))


def hold_for_outer_cleanup(process, output, error):
    """Keep the parent-child link until positive reap or coordinator tree kill.

    The externally enforced deadline bounds this fail-closed state. Exiting an
    ordinary error path here would orphan a still-running application and hide
    it from the coordinator's taskkill /T rooted at this wrapper.
    """
    try:
        write(output/'cleanup-unconfirmed.json',dict(child_pid=process.pid,error=repr(error),
            required_action='outer coordinator process-tree termination or confirmed child reap'))
    except OSError:
        pass  # Even an unwritable receipt must not permit an orphaning exit.
    while True:
        try:
            process.wait(timeout=1)
            return
        except BaseException:
            try:
                time.sleep(.1)
            except BaseException:
                pass


def supervise(command, output, env, remaining):
    """Join/kill the one child, reserving ten seconds before the outer deadline.

    This is direct-child cleanup, not an assertion of process-tree termination.
    The supported source child contains its era thread in the same process;
    no action enables a browser, launcher, service, or further process.
    """
    allowance=min(110,remaining-10)
    if allowance<=0: raise TimeoutError('No child allowance remains after cleanup reservation.')
    process=None
    with (output/'stdout.log').open('xb') as stdout,(output/'stderr.log').open('xb') as stderr:
        try:
            process=subprocess.Popen(command,cwd=output,env=env,stdout=stdout,stderr=stderr,
                creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            return process.wait(timeout=allowance)
        finally:
            if process is not None and process.poll() is None:
                try:
                    process.kill()
                    process.wait(timeout=3)
                except BaseException as error:
                    hold_for_outer_cleanup(process,output,error)


def execute(args):
    started=time.monotonic();wall=utc();output=args.output_dir.resolve();home=args.save_home.resolve()
    output.mkdir(parents=True,exist_ok=False)
    write(output/'start.json',dict(format=FORMAT,action=args.action,started_utc=wall,save_home=str(home),
        mode='detached_exe_cli' if args.executable else 'source_injected_sdl',remaining_seconds=args.remaining_seconds,
        stage_deadline_seconds=min(120,args.remaining_seconds),parent_budget_authority='shared1200_seconds_including_all_retained_attempts'))
    outputs={};checks={};status='error';error=None;before=None;after=None;selected=None;cache=None;source=None;command=None;input_sha=None
    def retain(name,value):
        write(output/name,value);outputs[name]=file_digest(output/name)
    try:
        if os.name!='nt': raise ValueError('Native qualification requires Windows; no dummy-SDL fallback.')
        if not 0<args.remaining_seconds<=1200: raise ValueError('Parent remaining budget must be positive and <=1200 seconds.')
        if output.is_relative_to(home) or home.is_relative_to(output): raise ValueError('Stage output and save home must be disjoint.')
        source=checked_source(args.source_manifest);inputs=None;reference=None
        if args.action!='startup':
            input_sha=file_digest(args.inputs);inputs=read(args.inputs)
            validate_frozen_inputs(inputs)
            if inputs.get('source_sha256')!=source or inputs.get('source_manifest_sha256')!=file_digest(args.source_manifest):
                raise ValueError('Frozen input/source identity mismatch.')
            selected=select_qualified_seed(read(args.cohort_judgment))
            reference=frozen_reference(args.expected_trial,selected,inputs,input_sha,source)
        previous=verified_receipt(args.previous_stage) if args.previous_stage else None
        direct=verified_receipt(args.direct_stage) if args.direct_stage else None
        for prior in (previous,direct):
            if prior is not None and (prior.get('source_sha256')!=source or prior.get('inputs_sha256')!=input_sha
                    or prior.get('mode')!=('detached_exe_cli' if args.executable else 'source_injected_sdl')):
                raise ValueError('Prior stage source/input/runtime mode differs from this journey.')
        before=inspect_home(home)
        validate_stage(args.action,before,selected,previous,direct,home)
        if args.action=='fallback-sheltered-era':
            if args.sheltered_trial is None: raise ValueError('Fallback needs its matching selected C cohort reference.')
            reference=frozen_reference(args.sheltered_trial,selected,inputs,input_sha,source,arm='C')
        elif args.action!='direct-era': reference=None
        cache=install_frozen_cache(home,inputs) if args.action in ERA_ACTIONS else None
        native=Path(args.executable).resolve() if args.executable else None
        if native is not None:
            if native.is_relative_to(ROOT): raise ValueError('Native artifact must be relocated outside repository ancestry.')
            imports()
            from labs.game_loop.verify_detached_release import validate_artifact_manifest
            validate_artifact_manifest(native.parent)
        arguments=launch_arguments(args.action,home,output,selected,before,source=native is None)
        if native is None and args.action!='reproduce':
            retain('source-worker.json',dict(action=args.action,arguments=arguments,output=str(output)))
            command=[sys.executable,'-B',str(Path(__file__).resolve()),'--source-worker',str(output/'source-worker.json')]
        else:
            command=[str(native)] if native else [sys.executable,'-B',str(ROOT/'game/run_game.py')]
            command+=arguments
        retain('plan.json',dict(action=args.action,selected_seed=selected,command=command,source_sha256=source,
            input_sha256=input_sha,source_manifest_sha256=file_digest(args.source_manifest),
            cohort_judgment_sha256=file_digest(args.cohort_judgment) if args.cohort_judgment else None,
            expected_trial=str(args.expected_trial.resolve()) if args.expected_trial else None,
            previous_stage=str(args.previous_stage.resolve()) if args.previous_stage else None,
            direct_stage=str(args.direct_stage.resolve()) if args.direct_stage else None,cache=cache,
            executable_sha256=file_digest(native) if native else None,
            scientific_boundary='Only actual saved endpoints and earned facts qualify; injected terminal fixtures are forbidden.'))
        remaining=min(120,args.remaining_seconds)-(time.monotonic()-started)
        if remaining<=0: raise TimeoutError('No remaining parent-authorized stage budget before launch.')
        env=dict(os.environ)
        for key in ('PYTHONPATH','PYTHONHOME'): env.pop(key,None)
        env.update(PYTHONDONTWRITEBYTECODE='1',PYGAME_HIDE_SUPPORT_PROMPT='1',SDL_VIDEODRIVER='windows',SDL_AUDIODRIVER='dummy')
        returncode=supervise(command,output,env,remaining)
        checks['process_exit_zero']=returncode==0
        if returncode: raise ValueError(f'Native stage exited {returncode}; no retry authorized.')
        after=inspect_home(home)
        checks['historical_eras_preserved']=all(after['historical_era_sha256'].get(k)==v for k,v in before['historical_era_sha256'].items())
        checks['historical_archives_preserved']=all(after['historical_elite_sha256'].get(k)==v for k,v in before['historical_elite_sha256'].items())
        if before['keeper_id'] is not None: checks['keeper_identity_preserved']=before['keeper_id']==after['keeper_id']
        if args.action=='startup':
            checks['no_era_ran']=not after['era_counts']
            checks['real_startup_ready']=read(output/'launch.json').get('startup_outcome')=='ready'
        elif args.action in ERA_ACTIONS:
            audit=audit_era(home,before,after,inputs,reference,action=args.action,selected_seed=selected);retain('era-audit.json',audit);checks.update(audit['checks'])
            checks['frozen_cache_retained']=file_digest(home/'model_cache'/cache['path'])==cache['sha256']
            checks['no_extra_training_cache']=not any(name.startswith('model_cache/') and name not in before['files']
                and name!='model_cache/'+cache['path'] for name in after['files'])
            if args.action=='direct-era':
                checks['genuine_extinction_matches']=audit['report']['living_population']['termination']['genuine_lifecycle_extinction'] is True and after['state']['status']=='extinct'
            if args.action=='fallback-stress-era':
                checks['fallback_genuine_extinction']=audit['report']['living_population']['termination']['genuine_lifecycle_extinction'] is True
                checks['actual_earned_fact']=bool(after['state']['unlocks'])
        elif args.action=='create-successor':
            prior,current=before['state'],after['state']
            checks.update(new_successor_identity=current['campaign_id']!=prior['campaign_id'] and current['predecessor_campaign_id']==prior['campaign_id'],
                successor_bootstrap=current['population_continuation']['founder_start_mode']=='bootstrap' and current['era_count']==0,
                inherited_facts_exact=current['inherited_unlocks']==prior['inherited_unlocks']+prior['unlocks'],
                base_covenant_exact=current['base_profile']==prior['base_profile'] and current['slip_profile']==prior['base_profile'],
                no_era_ran=before['era_counts']==after['era_counts'])
        elif args.action in ('restart','review','reproduce'):
            checks['save_bytes_preserved']=before['files']==after['files']
            if args.action=='reproduce': checks['full_reproduction_matched']=read(output/'comparison/comparison.json')['status']=='matched'
        elif args.action=='finish-pending':
            checks['journal_finished']=read(home/'era_plan.json').get('pending') is None
            checks['at_most_one_recorded_result']=0<=sum(after['era_counts'].values())-sum(before['era_counts'].values())<=1
        if native is None and args.action!='reproduce':
            observed=read(output/'source-events.json')
            checks['source_frames_captured']=bool(observed['screenshots'])
            checks['source_layout_fits']=all(row['fits'] for row in observed['pages'])
            checks['source_workers_joined']=all(not row['alive'] for row in observed['joins'])
            if args.action=='create-successor':
                checks['visible_successor_action']=any('successor' in ' '.join(row['all']).lower() for row in observed['pages'])
        checks['source_unchanged']=checked_source(args.source_manifest)==source
        if args.inputs is not None: checks['input_unchanged']=file_digest(args.inputs)==input_sha
        if time.monotonic()-started>min(120,args.remaining_seconds): raise TimeoutError('Stage exceeded its bounded allowance.')
        if not all(checks.values()): raise ValueError('Native stage checks failed: '+','.join(k for k,v in checks.items() if not v))
        status='completed'
    except BaseException as caught:
        status='timeout' if isinstance(caught,(TimeoutError,subprocess.TimeoutExpired)) else 'refused' if isinstance(caught,ValueError) else 'error'
        error=f'{type(caught).__name__}: {caught}'
        (output/'error.txt').write_text(traceback.format_exc(),encoding='utf-8')
    for path in output.rglob('*'):
        if path.is_file() and path.name not in ('terminal.json',): outputs[path.relative_to(output).as_posix()]=file_digest(path)
    terminal=dict(format=FORMAT,status=status,action=args.action,save_home=str(home),selected_seed=selected,
        mode='detached_exe_cli' if args.executable else 'source_injected_sdl',started_utc=wall,finished_utc=utc(),
        elapsed_seconds=time.monotonic()-started,source_sha256=source,inputs_sha256=input_sha,command=command,before=before,after=after,
        qualification_scope='startup_only_no_era' if args.action=='startup' else 'single_registered_journey_stage',
        checks=checks,outputs=outputs,error=error,actual_earned_facts=(after or {}).get('state',{}).get('unlocks') if (after or {}).get('state') else None,
        limitations=['Parent coordinator owns cumulative budget and once-only fallback authorization.',
                     'Source injected SDL and EXE CLI evidence are distinct; neither proves OS keyboard or human usability.',
                     'Direct-child watchdog <=110 seconds reserves cleanup before outer120; it does not claim a general process-tree kill.',
                     'No actual earned facts means inherited-unlock qualification remains OPEN.',
                     'This stage does not manufacture a pending journal or adopt a companion; those journeys require separately reviewed parent actions.'])
    write(output/'terminal.json',terminal)
    return terminal


def parser():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-worker',type=Path,help=argparse.SUPPRESS)
    p.add_argument('--action',choices=ACTIONS)
    for key in ('save-home','output-dir','inputs','source-manifest','cohort-judgment','expected-trial',
                'previous-stage','direct-stage','sheltered-trial','executable'):
        p.add_argument('--'+key,type=Path)
    p.add_argument('--remaining-seconds',type=float)
    return p


def main():
    p=parser();args=p.parse_args()
    if args.source_worker is not None: return source_worker(args.source_worker)
    required=['action','save_home','output_dir','source_manifest','remaining_seconds']
    if args.action!='startup':required+=['inputs','cohort_judgment','expected_trial']
    for key in required:
        if getattr(args,key) is None: p.error('--'+key.replace('_','-')+' is required')
    result=execute(args)
    print(json.dumps({key:result[key] for key in ('status','action','selected_seed','elapsed_seconds','checks','error')}))
    return 0 if result['status']=='completed' else 1


if __name__=='__main__': raise SystemExit(main())
