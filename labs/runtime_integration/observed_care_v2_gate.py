"""Versioned terminal-survival correction: bounded regression and fresh holdouts.

The contract is frozen before execution. Failed attempts never auto-retry.
Explicit resume only continues a clean completed boundary under the same inputs,
source and cumulative budget. Scientific refusals remain evaluator-local.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
for relative in ('packages/mecha_engine/src','game/src','labs/runtime_integration'):
    path=str(ROOT/relative)
    if path not in sys.path:sys.path.insert(0,path)
from mecha_engine.generation import GenerationModel, generate_candidate
from mecha_engine.runtime.care import (CARE_POLICY, CARE_POLICY_V2, CARE_EVALUATORS,
    care_grid_sha256 as digest, care_structure_sha256, care_context_sha256, select_care_successor)
from mecha_game.session import CompanionSession
from mecha_game.care_history import capture_care_context, _validate_care_v2_episode, validate_care_selection
from observed_care_selection import select_care_successor as prototype_select
from observed_care_gate import prefix, altered_metadata

FORMAT='care_v2_terminal_survival_gate_v1'
PRODUCT_PAYLOAD_SHA256='05d3512573e8066536181c731ce20839748980732f2e46cb0b957c464d495737'
SEEDS=(20261007,20261017,20261027)
FOUNDERS=tuple(range(10,20))
PAIR_COUNT=30
PAIR_LIMIT=30
TOTAL_LIMIT=300
CONTRACT='docs/development/cycle-38-terminal-survival-care.md'
COMMON_CHECKS=frozenset(('off_exact','absent_exact','empty_exact','input_immutable','source_unchanged','founder_identity'))
TRIAL_CHECKS=frozenset(('package_repeat','lab_mirror','metadata_negative','same_candidate_bytes',
    'welfare_nonregression','survival_nonregression','terminal_nonregression','live_option_selected',
    'pristine_child_exact','source_identity','trajectory_consistent','cold_start','product_receipt_loadable'))
REQUIRED_CHECKS=frozenset(name+'_'+check for name in ('fed','neglect') for check in TRIAL_CHECKS)
QUALIFICATION_CHECKS=frozenset(name+'_'+check for name in ('fed','neglect') for check in
    ('welfare_nonregression','survival_nonregression','terminal_nonregression'))
SOURCE_FILES=(CONTRACT,'labs/runtime_integration/observed_care_selection.py',
    'labs/runtime_integration/observed_care_gate.py','labs/runtime_integration/observed_care_v2_gate.py',
    'game/src/mecha_game/session.py','game/src/mecha_game/chronicle.py',
    'game/src/mecha_game/care_history.py','game/src/mecha_game/health.py','game/src/mecha_game/happiness.py')
PACKAGE_ROOT=ROOT/'packages/mecha_engine/src/mecha_engine'

def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def sources():
    paths=[ROOT/p for p in SOURCE_FILES]
    paths += sorted(PACKAGE_ROOT.rglob('*.py'))
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
def all_true(checks,names):
    return isinstance(checks,dict) and set(checks)==names and all(checks[key] is True for key in names)
def utc():return datetime.now(timezone.utc).isoformat()
def relative(path):return Path(path).resolve().relative_to(ROOT).as_posix()

def validate_product(product,retained):
    if digest(product)!=PRODUCT_PAYLOAD_SHA256:
        raise ValueError('original registered product manifest identity differs')
    if any(product.get(key)!=retained.get(key) for key in ('founders','covenant','admissions')):
        raise ValueError('founders models covenant or admissions differ from retained product evidence')
    admissions=product.get('admissions',[])
    if len(admissions)!=50 or any(type(row.get('founder_index')) is not int or row['founder_index']!=index
            or row.get('status')!='admitted' for index,row in enumerate(admissions)):
        raise ValueError('original ordered admission identities required')

def freeze(product_path):
    before=sources(); product=read(product_path)
    retained_path=ROOT/'data/game_client/product_learning_gate_stage1.json'
    retained=read(retained_path)['input_manifest']
    validate_product(product,retained)
    if product.get('hatch_seed')!=20261006 or len(product.get('founders',[]))!=50:
        raise ValueError('registered50 product founder cohort missing')
    admissions=product.get('admissions',[])
    if len(admissions)!=50 or any(row.get('status')!='admitted' for row in admissions):
        raise ValueError('all50 original admissions required')
    old=read(ROOT/'data/game_client/observed_care_inputs_stage0.json')
    historical=read(ROOT/'data/game_client/observed_care_selection_stage0.json')['rows'][22]
    founders=[]
    for index in FOUNDERS:
        record=product['founders'][index];histories={}
        for name in ('fed','neglect'):
            pet=CompanionSession(record['grid'],product['covenant'],model=GenerationModel(**record['model']),learning_policy='incumbent')
            for tick in range(1,13):
                if not pet.alive:break
                pet.advance('feed' if name=='fed' and tick%3==0 else None)
            histories[name]=capture_care_context(pet)
        count=min(len(ctx['events']) for ctx in histories.values())
        founders.append({'founder_index':index,'grid':record['grid'],'model':record['model'],
            'original_histories':histories,'used_prefix_ticks':count,
            'contexts':{name:prefix(ctx,count) for name,ctx in histories.items()}})
    if before!=sources():raise ValueError('source changed during freeze')
    return {'format':FORMAT,'policy':CARE_POLICY_V2,'source_sha256':before,
        'product_manifest_sha256':hashlib.sha256(Path(product_path).read_bytes()).hexdigest(),
        'product_payload_sha256':digest(product),
        'retained_product_evidence_sha256':hashlib.sha256(retained_path.read_bytes()).hexdigest(),
        'historical_input_file_sha256':hashlib.sha256((ROOT/'data/game_client/observed_care_inputs_stage0.json').read_bytes()).hexdigest(),
        'historical_result_file_sha256':hashlib.sha256((ROOT/'data/game_client/observed_care_selection_stage0.json').read_bytes()).hexdigest(),
        'source_admissions':admissions,'source_admissions_sha256':digest(admissions),
        'founders':founders,'covenant':product['covenant'],'covenant_sha256':digest(product['covenant']),
        'founder_payload_sha256':digest(founders),'regression_founder':old['founders'][2],
        'regression_v1':historical,'regression_covenant':old['covenant'],
        'plan':[{'founder_index':index,'rng_seed':seed} for seed in SEEDS for index in FOUNDERS],
        'protocol':{'evaluators':list(CARE_EVALUATORS),'pool_size':8,'seeds':list(SEEDS),
            'requested_observed_ticks':12,'keeper_feeds_at':[3,6,9,12],
            'setup_limit_seconds':PAIR_LIMIT,'pair_limit_seconds':PAIR_LIMIT,'total_limit_seconds':TOTAL_LIMIT}}

def trajectory_consistent(row,context,receipt):
    # Same strict stored-evidence validator used by the actual product loader;
    # includes cold state, source-tape mapping, action mediation, need continuity,
    # counters, final state, zero dead tail and no postdeath trajectory ticks.
    try:
        _validate_care_v2_episode(row,receipt,context)
    except (ValueError,TypeError,KeyError,AttributeError,OverflowError):
        return False
    return True


def measure(manifest,index,active,regression=False):
    if manifest['source_sha256']!=sources():raise ValueError('frozen source changed')
    if regression:
        spec={'founder_index':2,'rng_seed':20260702};founder=manifest['regression_founder'];slip=manifest['regression_covenant']
    else:
        spec=manifest['plan'][index];founder=manifest['founders'][spec['founder_index']-10];slip=manifest['covenant']
    parent=founder['grid'];model=GenerationModel(**founder['model']);before=digest((parent,slip,founder))
    old=generate_candidate(parent,model,slip,rng_seed=spec['rng_seed']);checks={}
    empty=deepcopy(founder['contexts']['fed']);empty.update(events=[],events_omitted=0,last_age_ticks=0,last_session_tick=0,outcome='alive')
    empty['care_summary']={'history':'complete','from_age_ticks':0,'ticks_observed':0,'keeper_actions':{},'companion_actions':{},'beg_requests':0}
    for mode,ctx,policy in [('off',founder['contexts']['fed'],'off'),('absent',None,CARE_POLICY_V2),('empty',empty,CARE_POLICY_V2)]:
        selected,receipt=select_care_successor(parent,model,slip,context=ctx,rng_seed=spec['rng_seed'],policy=policy)
        checks[mode+'_exact']=selected==old and receipt is None
    pool=[generate_candidate(parent,model,slip,rng_seed=spec['rng_seed']+i) for i in range(8)]
    pool_hashes=[digest(g) for g in pool];rows={};v1_exact={}
    for evaluator in active:
        trials={};local={}
        for name,ctx in founder['contexts'].items():
            args=dict(context=ctx,rng_seed=spec['rng_seed'],policy=CARE_POLICY_V2,evaluator=evaluator)
            selected,receipt=select_care_successor(parent,model,slip,**args)
            local[name+'_package_repeat']=(selected,receipt)==select_care_successor(parent,model,slip,**args)
            local[name+'_lab_mirror']=(selected,receipt)==prototype_select(parent,model,slip,**args)
            control,control_receipt=select_care_successor(parent,model,slip,**{**args,'context':altered_metadata(ctx)})
            local[name+'_metadata_negative']=selected==control and receipt['candidates']==control_receipt['candidates']
            local[name+'_same_candidate_bytes']=[r['grid_sha256'] for r in receipt['candidates']]==pool_hashes
            chosen=receipt['candidates'][receipt['selected_index']];baseline=receipt['candidates'][0]
            local[name+'_welfare_nonregression']=chosen['need_balance']>=baseline['need_balance']
            local[name+'_survival_nonregression']=chosen['survival_ticks']>=baseline['survival_ticks']
            local[name+'_terminal_nonregression']=chosen['terminal_survival']>=baseline['terminal_survival']
            local[name+'_live_option_selected']=chosen['terminal_survival'] or not any(r['terminal_survival'] for r in receipt['candidates'])
            local[name+'_pristine_child_exact']=selected==pool[receipt['selected_index']] and all(c['stress']==0 and c['damage']==0 for c in selected['cells'])
            local[name+'_source_identity']=(receipt['source_identity']=={key:ctx[key] for key in ('keeper_id','life_id','grid_id','grid_sha256')}
                and receipt['context_sha256']==care_context_sha256(ctx))
            local[name+'_trajectory_consistent']=all(trajectory_consistent(r,ctx,receipt) for r in receipt['candidates'])
            local[name+'_cold_start']=all(r['episode']['initial_state']['age_ticks']==0
                and not r['episode']['initial_state'].get('thread_states',{}).get('qtable_policy')
                and r['episode']['initial_state']['learning_switches']['qtable_policy'] is False for r in receipt['candidates'])
            try:
                validate_care_selection({'context':ctx,'receipt':receipt},parent_record=ctx,child_grid=selected)
                local[name+'_product_receipt_loadable']=True
            except (ValueError,TypeError,KeyError):local[name+'_product_receipt_loadable']=False
            trials[name]={'selected_grid':selected,'receipt':receipt}
            if regression:
                historical=manifest['regression_v1']['evaluators'][evaluator]['trials'][name]
                v1_exact[evaluator+'_'+name]=(historical['selected_grid'],historical['receipt'])==select_care_successor(parent,model,slip,**{**args,'policy':CARE_POLICY})
        rows[evaluator]={'trials':trials,'checks':local,'selected_structures_differ':
            care_structure_sha256(trials['fed']['selected_grid'])!=care_structure_sha256(trials['neglect']['selected_grid'])}
    checks['input_immutable']=before==digest((parent,slip,founder))
    checks['source_unchanged']=manifest['source_sha256']==sources()
    checks['founder_identity']=(founder['founder_index']==spec['founder_index'] and all(
        ctx['grid_id']==parent['grid_id'] and ctx['grid_sha256']==digest(parent) for ctx in founder['contexts'].values()))
    result={'pair_index':index,**spec,'evaluators':rows,'checks':checks,'used_prefix_ticks':founder['used_prefix_ticks']}
    if regression:
        result['v1_exact']=v1_exact
        probe=rows['archive_morphology_probe_v1']['trials']['neglect']['receipt']
        result['terminal_correction']=probe['selected_index']==0 and probe['candidates'][0]['terminal_survival'] is True
    return result

def judge(rows,regression,complete,source_unchanged,*,elapsed_seconds=0.0,setup_elapsed_seconds=0.0,failure=None):
    identities=(len(rows)==PAIR_COUNT and all(row.get('pair_index')==i and row.get('founder_index')==FOUNDERS[i%10]
        and row.get('rng_seed')==SEEDS[i//10]
        and all(type(row.get(key)) is int for key in ('pair_index','founder_index','rng_seed')) for i,row in enumerate(rows)))
    common=bool(rows) and all(all_true(r.get('checks'),COMMON_CHECKS) for r in rows)
    regression_ok=(isinstance(regression,dict) and all_true(regression.get('checks'),COMMON_CHECKS)
        and all_true(regression.get('v1_exact'),frozenset(e+'_'+n for e in CARE_EVALUATORS for n in ('fed','neglect')))
        and regression.get('terminal_correction') is True
        and set(regression.get('evaluators',{}))==set(CARE_EVALUATORS))
    runtime=(type(elapsed_seconds) in (int,float) and 0<=elapsed_seconds<=TOTAL_LIMIT
        and type(setup_elapsed_seconds) in (int,float) and 0<=setup_elapsed_seconds<=PAIR_LIMIT
        and all(type(r.get('elapsed_seconds')) in (int,float) and 0<=r['elapsed_seconds']<=PAIR_LIMIT
            for r in [*rows,*([regression] if isinstance(regression,dict) else [])]))
    result={}
    for evaluator in CARE_EVALUATORS:
        relevant=[r['evaluators'][evaluator] for r in rows if evaluator in r.get('evaluators',{})]
        different=sum(r.get('selected_structures_differ') is True for r in relevant)
        gates={'complete_cohort':complete and identities and len(relevant)==PAIR_COUNT,
            'registered_runtime':runtime,'no_operational_failure':failure is None,'source_unchanged':source_unchanged,
            'regression_fixed_without_v1_drift':regression_ok and all_true(
                regression['evaluators'][evaluator].get('checks'),REQUIRED_CHECKS),'all_invariants':common and bool(relevant)
                and all(all_true(r.get('checks'),REQUIRED_CHECKS) for r in relevant),
            'structural_descendant_effect':different>=1}
        failed=[k for k,v in gates.items() if v is not True]
        result[evaluator]={'verdict':'REFUSE' if failed else 'ADOPT','checks':gates,'failed_checks':failed,
            'completed_pairs':len(relevant),'structural_different_pairs':different}
    return result

def derive_evaluator_state(regression,rows):
    active=list(CARE_EVALUATORS);refused={}
    if (not all_true(regression.get('checks'),COMMON_CHECKS)
            or not all_true(regression.get('v1_exact'),frozenset(e+'_'+n for e in CARE_EVALUATORS for n in ('fed','neglect')))
            or regression.get('terminal_correction') is not True):
        raise ValueError('resume regression invariants fail')
    for phase,row in [('regression',regression),*((index,value) for index,value in enumerate(rows))]:
        if set(row.get('evaluators',{}))!=set(active) or not all_true(row.get('checks'),COMMON_CHECKS):
            raise ValueError('resume evaluator history differs from completed receipts')
        for evaluator in list(active):
            checks=row['evaluators'][evaluator].get('checks',{})
            if set(checks)!=REQUIRED_CHECKS or any(checks[k] is not True for k in REQUIRED_CHECKS-QUALIFICATION_CHECKS):
                raise ValueError('resume measurement invariants fail')
            failures=[key for key,value in checks.items() if value is not True]
            if failures:
                refused[evaluator]=({'phase':'regression'} if phase=='regression' else {'pair_index':phase}) | {'failed_checks':failures}
                active.remove(evaluator)
    return active,refused

def validate_resume(directory,manifest,checkpoint):
    if checkpoint.get('status')!='boundary' or checkpoint.get('failure') is not None:
        raise ValueError('only a clean completed-pair boundary can resume; retain interrupted or failed attempts')
    if checkpoint.get('manifest_sha256')!=digest(manifest) or manifest['source_sha256']!=sources():
        raise ValueError('resume inputs or source changed')
    if not 0<=checkpoint.get('consumed_seconds',TOTAL_LIMIT)<TOTAL_LIMIT:raise ValueError('no remaining cumulative budget')
    if (directory/'regression.started.json').exists() and not (directory/'regression.json').exists():
        raise ValueError('unfinished regression cannot resume')
    if list(directory.glob('rows/*.started.json'))!=[]:
        completed={p.name.replace('.json','') for p in directory.glob('rows/pair-*.json') if '.started.' not in p.name and '.payload.' not in p.name}
        if any(p.name.replace('.started.json','') not in completed for p in directory.glob('rows/*.started.json')):
            raise ValueError('unfinished started trial cannot resume')

def run(directory,product_path,artifact,*,resume=False):
    start=time.monotonic()
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    cp_path=directory/'checkpoint.json';manifest_path=directory/'manifest.json'
    rows=[];regression=None;manifest=None;failure=None;refused={};active=list(CARE_EVALUATORS);prior=0.0;setup_elapsed_seconds=0.0
    if cp_path.exists():
        if not resume:raise ValueError('existing bounded study retained; explicit safe-boundary resume required')
        cp=read(cp_path);manifest=read(manifest_path);validate_resume(directory,manifest,cp)
        prior=cp['consumed_seconds'];setup=read(directory/'setup.json');saved=setup.pop('receipt_sha256')
        if digest(setup)!=saved or setup.get('manifest_sha256')!=digest(manifest):raise ValueError('resume setup binding changed')
        setup_elapsed_seconds=setup['elapsed_seconds']
        if setup_elapsed_seconds>PAIR_LIMIT:raise ValueError('setup exceeded registered bound')
        active=cp['active_evaluators'];refused=cp['refused_evaluators']
        regression=read(directory/'regression.json')
        saved=regression.pop('receipt_sha256')
        if regression.get('manifest_sha256')!=digest(manifest) or digest(regression)!=saved:raise ValueError('resume regression binding changed')
        regression['receipt_sha256']=saved
        count=cp.get('completed_pairs')
        if type(count) is not int or not 0<=count<=PAIR_COUNT:raise ValueError('invalid completed pair count')
        expected={f'pair-{i:02d}.json' for i in range(count)}
        if {p.name for p in (directory/'rows').glob('pair-[0-9][0-9].json')}!=expected:
            raise ValueError('resume skips or invents a completed receipt')
        for index in range(cp['completed_pairs']):
            row=read(directory/'rows'/f'pair-{index:02d}.json');saved=row.pop('receipt_sha256')
            if row.get('manifest_sha256')!=digest(manifest) or digest(row)!=saved:raise ValueError('resume receipt binding changed')
            if row.get('pair_index')!=index or row.get('founder_index')!=FOUNDERS[index%10] or row.get('rng_seed')!=SEEDS[index//10]:
                raise ValueError('resume pair identity changed')
            row['receipt_sha256']=saved;rows.append(row)
        if prior<setup_elapsed_seconds+sum(r['elapsed_seconds'] for r in [regression,*rows]):raise ValueError('resume cumulative debit lost')
        expected_active,expected_refused=derive_evaluator_state(regression,rows)
        if active!=expected_active or refused!=expected_refused:raise ValueError('resume checkpoint resurrects or skips an evaluator')
    elif resume:raise ValueError('no existing study to resume')
    status='incomplete'
    def elapsed():return prior+time.monotonic()-start
    def checkpoint(state,**extra):
        write(cp_path,{'format':FORMAT,'at':utc(),'status':state,'failure':failure,'completed_pairs':len(rows),
            'consumed_seconds':elapsed(),'setup_elapsed_seconds':setup_elapsed_seconds,'manifest_sha256':digest(manifest) if manifest else None,
            'active_evaluators':active,'refused_evaluators':refused,**extra})
    def worker(index,is_regression=False):
        base=directory/'regression' if is_regression else directory/'rows'/f'pair-{index:02d}'
        payload=Path(str(base)+'.payload.json');final=Path(str(base)+'.json');started=Path(str(base)+'.started.json')
        write(started,{'at':utc(),'pair_index':index,'regression':is_regression,'active_evaluators':active,
            'manifest_sha256':digest(manifest),'consumed_seconds_before':elapsed()})
        checkpoint('running',active_pair='regression' if is_regression else index)
        remaining=TOTAL_LIMIT-elapsed()
        if remaining<=0:raise TimeoutError('cumulative budget exhausted')
        command=[sys.executable,'-B',__file__,'--worker',str(manifest_path),'--pair',str(index),
            '--evaluators',','.join(active),'--output',str(payload)]
        if is_regression:command.append('--regression')
        began=time.monotonic()
        subprocess.run(command,check=True,capture_output=True,text=True,timeout=min(PAIR_LIMIT,remaining))
        row=read(payload);row['elapsed_seconds']=time.monotonic()-began;row['manifest_sha256']=digest(manifest)
        row['receipt_sha256']=digest(row);write(final,row)
        if row['elapsed_seconds']>PAIR_LIMIT:raise TimeoutError('pair runtime bound exceeded')
        if not all_true(row['checks'],COMMON_CHECKS):raise ValueError('global instrument invariant failed')
        for evaluator,result in row['evaluators'].items():
            checks=result['checks']
            if set(checks)!=REQUIRED_CHECKS or any(checks[k] is not True for k in REQUIRED_CHECKS-QUALIFICATION_CHECKS):
                raise ValueError('global measurement/parity/trajectory invariant failed: '+evaluator)
        return row
    try:
        if manifest is None:
            checkpoint('setup')
            began=time.monotonic()
            try:
                subprocess.run([sys.executable,'-B',__file__,'--freeze',str(product_path),'--output',str(manifest_path)],
                    check=True,capture_output=True,text=True,timeout=min(PAIR_LIMIT,TOTAL_LIMIT-elapsed()))
                manifest=read(manifest_path)
            finally:
                setup_elapsed_seconds=time.monotonic()-began
                setup={'elapsed_seconds':setup_elapsed_seconds,'manifest_sha256':digest(manifest) if manifest else None}
                setup['receipt_sha256']=digest(setup);write(directory/'setup.json',setup)
            if setup_elapsed_seconds>PAIR_LIMIT:raise TimeoutError('measured setup bound exceeded')
        if regression is None:
            regression=worker(-1,True)
            if not regression.get('terminal_correction') or not all(regression['v1_exact'].values()):
                raise ValueError('regression does not fix terminal defect or v1 changed')
            for evaluator in list(active):
                failures=[k for k,v in regression['evaluators'][evaluator]['checks'].items() if v is not True]
                if failures:refused[evaluator]={'phase':'regression','failed_checks':failures};active.remove(evaluator)
            checkpoint('boundary')
        for index in range(len(rows),PAIR_COUNT):
            if not active:break
            row=worker(index);rows.append(row)
            for evaluator in list(active):
                failures=[k for k,v in row['evaluators'][evaluator]['checks'].items() if v is not True]
                if failures:refused[evaluator]={'pair_index':index,'failed_checks':failures};active.remove(evaluator)
            checkpoint('boundary')
            print(json.dumps({'completed_pairs':len(rows),'active_evaluators':active,'elapsed_seconds':round(elapsed(),3)}),flush=True)
        status='complete' if len(rows)==PAIR_COUNT else 'refused'
    except (subprocess.TimeoutExpired,TimeoutError) as error:failure={'kind':'registered_runtime_limit','detail':str(error)}
    except subprocess.CalledProcessError as error:failure={'kind':'worker_error','detail':error.stderr or error.stdout}
    except (ValueError,KeyError,OSError) as error:failure={'kind':'invalid_inputs_sources_or_instrument','detail':str(error)}
    unchanged=manifest is not None and manifest['source_sha256']==sources()
    duration=elapsed()
    if duration>TOTAL_LIMIT:failure={'kind':'registered_runtime_limit','detail':'cumulative bound exceeded'};status='incomplete'
    result={'artifact_id':'care_v2_terminal_survival_stage0','date':'2026-10-06','status':status,
        'purpose':'Alive-at-horizon correction and separately held-out care-dependent structural descendant qualification.',
        'source_artifacts':[CONTRACT,relative(manifest_path),'data/game_client/observed_care_selection_stage0.json'],
        'manifest_sha256':digest(manifest) if manifest else None,'manifest':manifest,'completed_pairs':len(rows),
        'planned_pairs':PAIR_COUNT,'elapsed_seconds':duration,'setup_elapsed_seconds':setup_elapsed_seconds,'failure':failure,'refused_evaluators':refused,
        'decision':judge(rows,regression,status=='complete',unchanged,elapsed_seconds=duration,setup_elapsed_seconds=setup_elapsed_seconds,failure=failure),
        'regression':regression,'rows':rows,'default':'off',
        'limitations':['Fixed synthetic care windows and legacy pools; no biological or personality claims.',
            'Species covenant priors remain distinct from morphology probe loads.',
            'Known pair22 is a regression, never new holdout evidence.',
            'Product persistence, founder propagation and native verification are separate gates.'],
        'next_research_step':'Honor each measured refusal; do not weaken old thresholds or seed-hunt.'}
    write(artifact,result);checkpoint(status,artifact=relative(artifact),failure=failure)
    print(json.dumps({'status':status,'decision':result['decision'],'failure':failure},indent=2))
    return 0 if failure is None else 2

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',type=Path);parser.add_argument('--resume',action='store_true')
    parser.add_argument('--product-manifest',type=Path,default=ROOT/'.development/x7/learning/manifest.json')
    parser.add_argument('--artifact',type=Path,default=ROOT/'data/game_client/care_v2_terminal_survival_stage0.json')
    parser.add_argument('--freeze',type=Path);parser.add_argument('--worker',type=Path);parser.add_argument('--pair',type=int)
    parser.add_argument('--evaluators',default=','.join(CARE_EVALUATORS));parser.add_argument('--regression',action='store_true');parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.freeze:write(args.output,freeze(args.freeze));return 0
    if args.worker:
        active=args.evaluators.split(',')
        if not active or any(e not in CARE_EVALUATORS for e in active):raise ValueError('unregistered evaluator')
        write(args.output,measure(read(args.worker),args.pair,active,args.regression));return 0
    return run(args.run,args.product_manifest,args.artifact,resume=args.resume)
if __name__=='__main__':raise SystemExit(main())
