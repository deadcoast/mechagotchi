"""Single-stage X8 instrument; only the integration owner launches measurements.

This worker never starts a second simulation, retries a failed directory, tunes
the cohort, or grants a time budget. Its foreground parent must enforce the
120-second child deadline and the shared 1,200-second experiment ledger,
including process startup, I/O, interruption and retained earlier attempts.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import math
from statistics import mean
from pathlib import Path
import sys
import time
import traceback

ROOT=Path(__file__).resolve().parents[2]
FORMAT='surviving_population_instrument_v1'
CONTRACT='docs/development/cycle-38-surviving-populations.md'
SEEDS=tuple(range(20260700,20260710))
ARMS={'A':('legacy_archive','sheltered'),'B':('legacy_archive','stress_probe'),
      'C':('generation_survivors_v1','sheltered'),'D':('generation_survivors_v1','stress_probe')}

def utc():return datetime.now(timezone.utc).isoformat()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encode(value):return (json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n').encode('utf-8')
def read(path):return json.loads(Path(path).read_bytes())
def write(path,value):
    path=Path(path)
    with path.open('xb') as stream:stream.write(encode(value))
def source_snapshot(manifest_path):
    manifest=read(manifest_path)
    if set(manifest)!={"format","files"} or manifest['format']!='x8_source_manifest_v1':
        raise ValueError('invalid shared source manifest')
    files=manifest['files']
    if not isinstance(files,dict) or not files:raise ValueError('empty source closure')
    current={}
    for name,expected in files.items():
        if not isinstance(name,str) or Path(name).is_absolute():raise ValueError('source path must be relative')
        target=(ROOT/name).resolve()
        if not target.is_relative_to(ROOT):raise ValueError('source path escapes repository')
        if not isinstance(expected,str) or len(expected)!=64:raise ValueError('invalid source digest')
        current[name]=sha(target.read_bytes())
    if current!=files:raise ValueError('registered source or original input drift')
    return current
def imports():
    for name in ('packages/mecha_engine/src','game/src','labs/runtime_integration'):
        path=str(ROOT/name)
        if path not in sys.path:sys.path.insert(0,path)

def case_plan():
    plan=[]
    for seed in (SEEDS[0],SEEDS[-1]):
        for arm in ARMS:
            for backend in ('lab','package'):
                plan.append(dict(stage='parity',backend=backend,arm=arm,seed=seed))
    for seed in SEEDS:
        for arm in ARMS:plan.append(dict(stage='cohort',backend='package',arm=arm,seed=seed))
    for arm in ARMS:plan.append(dict(stage='duplicate',backend='lab',arm=arm,seed=SEEDS[0]))
    return plan

def frozen_setup():
    imports()
    from mecha_game.campaign import load_campaign_inputs,build_weather_source
    inputs=load_campaign_inputs(ROOT/'data/seed_grids_16x16',ROOT/'data/slips/valid/slip_v2_cleanliness.json',
        ROOT/'data/readability_benchmark/adopted_readability_model.json',repair_epochs=40,rng_seed=20260707)
    if len(inputs['seed_grids'])!=50:raise ValueError('registered ordered50 corpus missing')
    weather_sources={};weather_inputs={}
    for name in ('storm','real','callback'):
        records=[];weather_sources[name]=build_weather_source(name,source_records=records);weather_inputs[name]=records
    return dict(format='surviving_population_inputs_v1',seed_grids=inputs['seed_grids'],
        slip_profile=inputs['slip_profile'],generation_model=asdict(inputs['generation_model']),
        repair_model=inputs['repair_model'],legibility_model=inputs['legibility_model'],
        readability_selection={**inputs['legibility_model'],'blend':.7},weather_sources=weather_sources,
        input_sources=inputs['input_sources'],weather_input_sources=weather_inputs,
        training_options=dict(repair_training_count=40,epochs=40,rng_seed=20260707,
            dropout_rates=[.1,.2,.3,.4],damage_instances=1,learning_rate=1.5,live_class_weight=3.,vocabulary='legacy'))

def run_case(inputs,plan):
    imports()
    from mecha_engine.generation import GenerationModel
    from mecha_engine.runtime._readability import learned_readability_score
    if plan not in case_plan():raise ValueError('case is outside the registered60-call plan')
    if plan['backend']=='lab':
        from mecha_engine_runtime_loop import run_frozen_evolution_loop as evolve
    else:
        from mecha_engine.runtime import evolve
    before=encode(inputs);local=deepcopy(inputs);evaluations=[]
    policy,regime=ARMS[plan['arm']]
    archive,report=evolve(local['seed_grids'],local['slip_profile'],GenerationModel(**local['generation_model']),
        local['repair_model'],readability_scorer=lambda grid:learned_readability_score(grid,local['legibility_model']),
        generations=6,population=16,damage_cycles=2,ticks=16,dropout_rate=.2,rng_seed=plan['seed'],
        founder_grids=[],population_policy=policy,founder_start_mode='bootstrap',survival_regime=regime,
        cubff_density_pressure=False,cubff_pressure_source=local['weather_sources']['storm'],
        readability_selection=local['readability_selection'],care_selection_policy='off',
        evaluation_callback=evaluations.append)
    result=dict(archive=archive,report=report,evaluations=evaluations,
        checks=dict(input_immutable=before==encode(inputs)==encode(local)),projection=[])
    result['checks']['observations_bound']=observations_bound(result)
    validate_result(result,plan,inputs)
    return result

def episode_consistent(episode,history,ticks):
    if episode is None:return history is None
    count=episode.get('survival_ticks')
    if type(count) is not int or not 0<=count<=ticks or not isinstance(history,list) or len(history)!=count:return False
    if type(episode.get('alive')) is not bool or (episode['death_cause'] is None)!=episode['alive']:return False
    if episode['alive'] and count!=ticks:return False
    if any(row['tick']!=i+1 or (i<len(history)-1 and row['alive'] is not True) for i,row in enumerate(history)):return False
    if history and (history[-1]['alive']!=episode['alive'] or history[-1]['death_cause']!=episode['death_cause']):return False
    if ticks and history and round(mean([row['balance'] for row in history]+[0.0]*(ticks-len(history))),6)!=episode['need_balance']:return False
    if 'history' in episode and episode['history']!=history:return False
    if history and 'final_state' in episode and episode['final_state']!=history[-1]['state']:return False
    return True

def observations_bound(result):
    from mecha_engine.runtime.care import care_grid_sha256
    report=result['report'];observations=result['evaluations']
    creatures=[(g['generation'],i,c) for g in report['generations'] for i,c in enumerate(g['creatures'])]
    if len(creatures)!=len(observations):return False
    for (generation,index,creature),row in zip(creatures,observations):
        if (row['generation_index'],row['candidate_index'],row['creature'])!=(generation,index,creature):return False
        if row['run_seed']!=report['rng_seed']+generation*100000+index:return False
        if row['candidate_grid']['grid_id']!=creature['candidate_grid_id']:return False
        if row['parent_grid']['grid_id']!=creature['parent_grid_id']:return False
        stripped=[{k:v for k,v in c.items() if k not in ('frames','damage_seed')} for c in row['cycles']]
        if stripped!=creature['cycles']:return False
        for cycle in row['cycles']:
            if cycle['damage_seed']!=row['run_seed']*10+cycle['cycle']:return False
            if len(cycle['frames']['removed_cells'])!=cycle['removed_cell_count']:return False
            episode=cycle['episode'];history=cycle['frames']['episode_history']
            if not episode_consistent(episode,history,report['ticks']):return False
        final=row['final_episode']
        if not episode_consistent(final,final['history'] if final is not None else None,report['ticks']):return False
        if 'breeding' in creature:
            b=creature['breeding']
            if b['candidate_grid_sha256']!=care_grid_sha256(row['candidate_grid']):return False
            if b['final_grid_sha256']!=care_grid_sha256(row['final_grid']):return False
            if (b['final_episode'] is None)!=(row['final_episode'] is None):return False
            if row['final_episode'] is not None:
                from mecha_engine.runtime._survival_live import _episode_digest
                if b['final_episode']!=_episode_digest(row['final_episode'],report['ticks']):return False
    return True

def execute(command,output,source_manifest_path,inputs_path=None,plan=None):
    started=time.monotonic();wall=utc();output=Path(output)
    output.mkdir(parents=True,exist_ok=False)
    # The first durable receipt precedes imports, source scanning and model I/O.
    write(output/'start.json',dict(format=FORMAT,command=command,plan=plan,started_utc=wall,
        inputs_path=str(inputs_path) if inputs_path else None,source_manifest_path=str(source_manifest_path),limit_seconds=120,
        parent_budget_authority='integration_owner_cumulative_1200_seconds'))
    outputs={};status='error';error=None;bound_source=None;input_digest=None;manifest_digest=None
    try:
        bound_source=source_snapshot(source_manifest_path)
        manifest_digest=sha(Path(source_manifest_path).read_bytes())
        if command=='setup':
            inputs=frozen_setup();inputs['source_sha256']=bound_source;inputs['source_manifest_sha256']=manifest_digest
            if source_snapshot(source_manifest_path)!=bound_source:raise ValueError('source drift during setup')
            write(output/'inputs.json',inputs);outputs['inputs.json']=sha((output/'inputs.json').read_bytes())
        else:
            raw=Path(inputs_path).read_bytes();input_digest=sha(raw);inputs=json.loads(raw)
            if inputs.get('source_sha256')!=bound_source or inputs.get('source_manifest_sha256')!=manifest_digest:
                raise ValueError('frozen source identity changed')
            write(output/'plan.json',dict(format=FORMAT,case=plan,inputs_sha256=input_digest,source_sha256=bound_source,source_manifest_sha256=manifest_digest))
            outputs['plan.json']=sha((output/'plan.json').read_bytes())
            result=run_case(inputs,plan)
            result['checks']['source_unchanged']=source_snapshot(source_manifest_path)==bound_source
            write(output/'result.json',result);outputs['result.json']=sha((output/'result.json').read_bytes())
            if not all(v is True for v in result['checks'].values()):raise ValueError('instrument invariant failure')
        if source_snapshot(source_manifest_path)!=bound_source or sha(Path(source_manifest_path).read_bytes())!=manifest_digest:
            raise ValueError('source drift before publication')
        if time.monotonic()-started>120:raise TimeoutError('measured stage exceeded120 seconds')
        status='completed'
    except BaseException as caught:
        error=f'{type(caught).__name__}: {caught}'
        (output/'error.txt').write_text(traceback.format_exc(),encoding='utf-8')
        outputs['error.txt']=sha((output/'error.txt').read_bytes())
    write(output/'terminal.json',dict(format=FORMAT,status=status,command=command,plan=plan,
        started_utc=wall,finished_utc=utc(),elapsed_seconds=time.monotonic()-started,
        inputs_sha256=input_digest,source_sha256=bound_source,source_manifest_sha256=manifest_digest,outputs=outputs,error=error))
    if status!='completed':raise RuntimeError(error)
    return read(output/'terminal.json')

def load_trial(directory,inputs_sha256,source_sha256,inputs):
    directory=Path(directory);terminal=read(directory/'terminal.json');start=read(directory/'start.json')
    if terminal['status']!='completed' or terminal['command']!='case':raise ValueError('incomplete trial cannot resume')
    if (terminal['plan'] not in case_plan() or terminal['plan']!=start['plan'] or terminal['started_utc']!=start['started_utc']
            or start['command']!='case' or start['limit_seconds']!=120):raise ValueError('start receipt differs')
    if type(terminal['elapsed_seconds']) not in (int,float) or not math.isfinite(terminal['elapsed_seconds']) or not 0<=terminal['elapsed_seconds']<=120:raise ValueError('trial exceeded measured stage budget')
    if terminal['inputs_sha256']!=inputs_sha256 or terminal['source_sha256']!=source_sha256:raise ValueError('trial identity differs')
    if set(terminal['outputs'])!={'plan.json','result.json'}:raise ValueError('unexpected completed output set')
    for name,digest in terminal['outputs'].items():
        if sha((directory/name).read_bytes())!=digest:raise ValueError('trial output digest differs')
    plan=read(directory/'plan.json')
    if (plan['case']!=terminal['plan'] or plan['inputs_sha256']!=inputs_sha256 or plan['source_sha256']!=source_sha256
            or plan['source_manifest_sha256']!=terminal['source_manifest_sha256']):
        raise ValueError('durable plan differs')
    result=read(directory/'result.json')
    if result['projection']!=[]:raise ValueError('unexpected scientific projection')
    if set(result['checks'])!={'input_immutable','observations_bound','source_unchanged'} or not all(value is True for value in result['checks'].values()):
        raise ValueError('failed trial invariant')
    imports()
    validate_result(result,terminal['plan'],inputs)
    return dict(plan=terminal['plan'],result=result,receipt=terminal)

def validate_survivor_sequence(row,slip,ticks,cycles_requested):
    """Re-derive the first terminal stop from actual frames and endpoints."""
    from mecha_engine.genome import validate_grid
    from mecha_engine.slip import is_grid_aligned
    from mecha_engine.runtime._survival_live import endpoint_qualified,endpoint_reason
    creature=row['creature'];breeding=creature['breeding'];cycles=row['cycles']
    valid=validate_grid(row['candidate_grid']).ok
    if creature['stages']['candidate_valid'] is not valid:raise ValueError('candidate validity differs')
    if not validate_grid(row['parent_grid']).ok or not is_grid_aligned(row['parent_grid'],slip).ok:
        raise ValueError('inadmissible actual parent')
    if [c['cycle'] for c in cycles]!=list(range(1,len(cycles)+1)) or len(cycles)>cycles_requested:
        raise ValueError('cycle sequence differs')
    stop=None if valid else dict(stage='candidate',cycle_index=None,reason='invalid_candidate')
    current=row['candidate_grid'];qualified=0
    for cycle in cycles:
        if stop is not None:raise ValueError('cycle recorded after a terminal stop')
        repaired=cycle['frames']['repaired_grid']
        repaired_valid=validate_grid(repaired).ok;aligned=is_grid_aligned(repaired,slip).ok
        if cycle['valid'] is not repaired_valid or cycle['aligned'] is not aligned:
            raise ValueError('repair validity or alignment differs')
        if not repaired_valid or not aligned:
            if cycle['episode'] is not None:raise ValueError('episode recorded for rejected repair')
            stop=dict(stage='repair',cycle_index=cycle['cycle'],reason='invalid_repair' if not repaired_valid else 'unaligned_repair')
        else:
            current=repaired
            if not endpoint_qualified(cycle['episode'],ticks):
                stop=dict(stage='cycle_episode',cycle_index=cycle['cycle'],reason=endpoint_reason(cycle['episode']))
            else:qualified+=1
    if row['final_grid']!=current:raise ValueError('final body differs from last accepted repair')
    if stop is not None:
        if row['final_episode'] is not None:raise ValueError('fresh final life recorded after a terminal stop')
    else:
        if len(cycles)!=cycles_requested:raise ValueError('missing requested cycles without a recorded stop')
        if row['final_episode'] is None:raise ValueError('missing actual final scoring episode')
        if not endpoint_qualified(row['final_episode'],ticks):
            stop=dict(stage='final_episode',cycle_index=None,reason=endpoint_reason(row['final_episode']))
    if breeding['stop']!=stop or breeding['cycles_qualified']!=qualified:
        raise ValueError('recorded stop or qualified cycles differ from actual sequence')
    if (creature['stages']['all_cycles_valid'] is not (valid and all(c['valid'] for c in cycles))
            or creature['stages']['all_cycles_aligned'] is not all(c['aligned'] for c in cycles)):
        raise ValueError('aggregate stage validity differs')
    scored=row['final_episode'] is not None
    if creature['stages']['scored'] is not scored or (creature['score'] is not None) is not scored:
        raise ValueError('score recorded without its actual final episode')


def validate_result(result,plan,inputs):
    """Recompute receipt consistency from factual outputs; never trust check flags."""
    if plan not in case_plan():raise ValueError('unregistered case')
    report=result['report'];policy,regime=ARMS[plan['arm']]
    expected=dict(rng_seed=plan['seed'],generations_requested=6,population=16,
                  damage_cycles=2,ticks=16,dropout_rate=.2,seed_corpus_size=50)
    if any(report.get(k)!=v for k,v in expected.items()):raise ValueError('result configuration differs from immutable trial plan')
    if len(inputs['seed_grids'])!=50 or report.get('founders')!={'admitted_ids':[],'rejected':[]} or 'care_selection' in report:
        raise ValueError('result founder/care/corpus configuration differs')
    if report.get('survival_regime','sheltered')!=regime:raise ValueError('result regime differs')
    generations=report['generations'];observed=result['evaluations'];living=report.get('living_population')
    if [g['generation'] for g in generations]!=list(range(len(generations))) or not 1<=len(generations)<=6:
        raise ValueError('noncontiguous evaluated generations')
    if any(len(g['creatures'])!=16 for g in generations):raise ValueError('requested candidate denominator differs')
    if sum(e['generation_index']==0 for e in observed)!=16:raise ValueError('matched first-generation denominator differs')
    if report['summary']['creature_count']!=len(observed):raise ValueError('evaluated candidate count differs')
    if not observations_bound(result):raise ValueError('actual observation trajectory or body contradicts report')
    from mecha_engine.runtime._survival_population import _cubff_generation_pressure
    source=inputs['weather_sources']['storm'];weather=report.get('cubff_pressure')
    expected_weather=[]
    for index in range(len(generations)):
        snapshot=source[index%len(source)];pressure,multiplier=_cubff_generation_pressure(snapshot)
        expected_weather.append(dict(snapshot_id=str(snapshot.get('snapshot_id','cubff')),
            mutation_pressure=pressure,dropout_multiplier=multiplier))
    if (weather is None or weather.get('density_pressure',False) is not False
            or weather['source_snapshot_count']!=len(source) or weather['by_generation']!=expected_weather):
        raise ValueError('frozen weather differs')
    for row in observed:
        w=expected_weather[row['generation_index']]
        if row['generation_weather']!=w or row['effective_dropout_rate']!=round(.2*w['dropout_multiplier'],6):
            raise ValueError('actual dropout differs from frozen weather')
    selection=report['readability_selection']
    for key in ('weights','reference_features','blend'):
        if selection[key]!=inputs['readability_selection'][key]:raise ValueError('readability selection inputs differ')
    if policy=='legacy_archive':
        if living is not None:raise ValueError('legacy arm mislabeled as survivor policy')
        return
    if (living is None or living['format']!=policy or living['population_policy']!=policy
            or living['founder_start_mode']!='bootstrap' or living['survival_regime']!=regime):
        raise ValueError('population policy inputs differ')
    if (living['requested_candidate_slots']!=96 or living['evaluated_candidates']!=len(observed)
            or living['unexecuted_candidate_slots']!=96-len(observed)):
        raise ValueError('living population slot accounting differs')
    from mecha_engine.runtime._survival_live import endpoint_qualified
    from mecha_engine.runtime.care import care_grid_sha256
    from mecha_engine.runtime._readability import learned_readability_score
    terminal_generation=generations[-1]['generation'];expected_breeders=[]
    for row in observed:
        validate_survivor_sequence(row,inputs['slip_profile'],16,2)
        creature=row['creature'];breeding=creature['breeding'];cycles=row['cycles']
        qualified=sum(c['valid'] and c['aligned'] and endpoint_qualified(c['episode'],16) for c in cycles)
        eligible=(creature['stages']['candidate_valid'] and len(cycles)==2 and qualified==2
                  and endpoint_qualified(row['final_episode'],16))
        if (breeding['eligible'] is not eligible or breeding['cycles_requested']!=2
                or breeding['cycles_attempted']!=len(cycles) or breeding['cycles_qualified']!=qualified):
            raise ValueError('claimed eligibility contradicts actual endpoints')
        if row['generation_index']==terminal_generation and eligible:
            expected_breeders.append(dict(generation_index=terminal_generation,candidate_index=row['candidate_index'],
                grid_id=row['final_grid']['grid_id'],grid=row['final_grid'],grid_sha256=care_grid_sha256(row['final_grid']),
                fitness=creature['score']['fitness'],learned_readability=learned_readability_score(row['final_grid'],inputs['legibility_model']),
                care_context=None,care_context_origin=None))
    if living['final_breeders']!=expected_breeders:raise ValueError('final breeder bodies/occurrences differ')
    terminal=[r for r in observed if r['generation_index']==terminal_generation]
    deaths=sum(any(c['episode'] is not None and c['episode']['alive'] is False and c['episode']['death_cause'] is not None
                   for c in r['cycles']) or (r['final_episode'] is not None and r['final_episode']['alive'] is False
                   and r['final_episode']['death_cause'] is not None) for r in terminal)
    structural=sum(r['creature']['breeding']['stop'] is not None and r['creature']['breeding']['stop']['stage'] in ('candidate','repair') for r in terminal)
    expected_termination=dict(ended=not expected_breeders,reason='requested_horizon_complete' if expected_breeders else 'no_eligible_breeders',
        generation_index=terminal_generation,lifecycle_deaths=deaths,structural_disqualifications=structural,
        genuine_lifecycle_extinction=not expected_breeders and deaths>0)
    if living['termination']!=expected_termination:raise ValueError('terminal extinction evidence differs')
    if expected_breeders and len(generations)!=6:raise ValueError('surviving cohort ended early')


def judge(trials):
    expected=case_plan()
    if len(trials)!=60 or [row['plan'] for row in trials]!=expected:
        raise ValueError('exact registered60 calls required in order')
    keyed={(r['plan']['stage'],r['plan']['backend'],r['plan']['arm'],r['plan']['seed']):r['result'] for r in trials}
    checks={}
    for seed in (SEEDS[0],SEEDS[-1]):
        for arm in ARMS:
            checks[f'parity_{arm}_{seed}']=keyed['parity','lab',arm,seed]==keyed['parity','package',arm,seed]
            checks[f'cohort_repeat_{arm}_{seed}']=keyed['parity','package',arm,seed]==keyed['cohort','package',arm,seed]
    for arm in ARMS:
        checks[f'duplicate_{arm}']=keyed['parity','lab',arm,SEEDS[0]]==keyed['duplicate','lab',arm,SEEDS[0]]
    deaths={arm:0 for arm in ARMS};missing={arm:0 for arm in ARMS};counts=[]
    survivor_seeds=[];extinct_seeds=[]
    for seed in SEEDS:
        firsts={arm:[e for e in keyed['cohort','package',arm,seed]['evaluations'] if e['generation_index']==0]
                for arm in ARMS}
        checks[f'first_generation_identity_{seed}']=all(
            [e['candidate_grid'] for e in firsts[arm]]==[e['candidate_grid'] for e in firsts['A']] for arm in ARMS)
        for arm in ARMS:
            for row in firsts[arm]:
                episode=row['final_episode'];missing[arm]+=episode is None
                deaths[arm]+=episode is not None and episode['alive'] is False and episode['death_cause'] is not None
            report=keyed['cohort','package',arm,seed]['report'];living=report.get('living_population')
            candidates=[c for g in report['generations'] for c in g['creatures']]
            eligible=sum(c.get('breeding',{}).get('eligible',False) for c in candidates) if living else None
            counts.append(dict(seed=seed,arm=arm,evaluated_candidates=len(candidates),
                requested_candidate_slots=96,unexecuted_candidate_slots=96-len(candidates),
                eligible_occurrences=eligible,requested_slot_living_yield=eligible/96 if eligible is not None else None,
                terminal_breeders=len(living['final_breeders']) if living else None,
                termination=living['termination'] if living else None,archive=report['summary']['archive']))
            if arm=='D' and living:
                if living['final_breeders']:survivor_seeds.append(seed)
                if living['termination']['genuine_lifecycle_extinction']:extinct_seeds.append(seed)
    checks['harder_matched_first_generation']=deaths['B']>deaths['A']
    checks['stress_survivors_and_genuine_extinction']=bool(survivor_seeds and extinct_seeds)
    return dict(format=FORMAT,cohort_verdict='ADOPT' if all(checks.values()) else 'REFUSE',
        product_qualification='OPEN' if all(checks.values()) else 'REFUSE',
        checks=checks,first_generation_deaths=deaths,first_generation_missing_final_episodes=missing,
        stress_survivor_seeds=survivor_seeds,genuine_extinct_seeds=extinct_seeds,
        lowest_extinct_seed=min(extinct_seeds) if extinct_seeds else None,counts=counts,
        native_journey='pending_independent_product_gate',default_changed=False)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    setup=sub.add_parser('setup');setup.add_argument('--output',type=Path,required=True)
    setup.add_argument('--source-manifest',type=Path,required=True)
    case=sub.add_parser('case');case.add_argument('--output',type=Path,required=True);case.add_argument('--inputs',type=Path,required=True)
    case.add_argument('--source-manifest',type=Path,required=True)
    case.add_argument('--backend',choices=['lab','package'],required=True);case.add_argument('--arm',choices=list(ARMS),required=True)
    case.add_argument('--seed',type=int,choices=SEEDS,required=True);case.add_argument('--stage',choices=['parity','cohort','duplicate'],required=True)
    listing=sub.add_parser('plan')
    judging=sub.add_parser('judge')
    judging.add_argument('--inputs',type=Path,required=True)
    judging.add_argument('--source-manifest',type=Path,required=True)
    judging.add_argument('--trial-index',type=Path,required=True,help='JSON ordered list of60 trial directory paths')
    judging.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.command=='plan':print(json.dumps(case_plan(),indent=2));return
    if args.command=='judge':
        started=time.monotonic();inputs=read(args.inputs);sources=source_snapshot(args.source_manifest)
        if inputs.get('source_sha256')!=sources or inputs.get('source_manifest_sha256')!=sha(args.source_manifest.read_bytes()):
            raise ValueError('judge frozen source identity differs')
        index=read(args.trial_index)
        if not isinstance(index,list) or len(index)!=60:raise ValueError('ordered60 trial directories required')
        paths=[Path(name) if Path(name).is_absolute() else args.trial_index.parent/name for name in index]
        if len({str(path.resolve()) for path in paths})!=60:raise ValueError('duplicate trial directory')
        trials=[load_trial(path,sha(args.inputs.read_bytes()),sources,inputs) for path in paths]
        result=judge(trials)
        result['trial_terminal_sha256']=[sha((path/'terminal.json').read_bytes()) for path in paths]
        result['input_sha256']=sha(args.inputs.read_bytes())
        result['source_manifest_sha256']=sha(args.source_manifest.read_bytes())
        if source_snapshot(args.source_manifest)!=sources:raise ValueError('source drift during read-only judging')
        result['judge_elapsed_seconds']=time.monotonic()-started
        write(args.output,result);print(json.dumps({'cohort_verdict':result['cohort_verdict'],'product_qualification':result['product_qualification']}));return
    plan={key:getattr(args,key) for key in ('stage','backend','arm','seed')} if args.command=='case' else None
    result=execute(args.command,args.output,args.source_manifest,getattr(args,'inputs',None),plan)
    print(json.dumps({'status':result['status'],'elapsed_seconds':result['elapsed_seconds']}))

if __name__=='__main__':main()
