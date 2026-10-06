"""Bounded X7 care selection gate, registered before execution.

First10 actual product founders, seeds20260700..20260702, pool8; exact observed
12-tick feed-every-third versus neglect tapes (common actual prefix if needed).
Both pristine and archive_morphology_probe_v1 share candidate bytes. Gate must
complete30 pairs; no welfare/survival loss against pool index0 and at least one
paired structural selected difference, with all invariant controls. Zero effect
REFUSES; no inferred phenotype, trained Q inheritance or stress inheritance.
Foreground supervisor caps each pair30s and total300s including setup. Failed
or source-changed work is never retried. Every completed pair is a bound receipt.
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

ROOT = Path(__file__).resolve().parents[2]
for relative in ('packages/mecha_engine/src','game/src','labs/runtime_integration'):
    path = str(ROOT / relative)
    if path not in sys.path: sys.path.insert(0,path)

from mecha_engine.generation import GenerationModel, generate_candidate
from mecha_engine.runtime.care import (CARE_EVALUATORS, CARE_POLICY, care_context_sha256,
    care_grid_sha256, care_structure_sha256, select_care_successor, validate_care_context)
from mecha_game.session import CompanionSession
from mecha_game.care_history import capture_care_context
from observed_care_selection import select_care_successor as prototype_select

SEEDS = (20260700,20260701,20260702)
PAIR_LIMIT = 30
TOTAL_LIMIT = 300
PAIR_COUNT = 30
FORMAT = 'observed_care_selection_gate_v1'
REQUIRED_CHECKS = frozenset(('off_exact', 'absent_exact', 'input_immutable', 'source_unchanged')) | frozenset(
    evaluator + '_' + care + '_' + suffix
    for evaluator in CARE_EVALUATORS for care in ('fed', 'neglect')
    for suffix in ('repeat_and_mirror', 'metadata_negative', 'same_candidate_bytes',
                   'welfare_nonregression', 'survival_nonregression', 'pristine_child'))
SOURCE_FILES = ('labs/runtime_integration/observed_care_selection.py',
    'labs/runtime_integration/observed_care_gate.py','game/src/mecha_game/session.py',
    'game/src/mecha_game/chronicle.py','game/src/mecha_game/care_history.py')
SOURCE_DIRS = ('packages/mecha_engine/src/mecha_engine/generation',
    'packages/mecha_engine/src/mecha_engine/genome','packages/mecha_engine/src/mecha_engine/lifecycle',
    'packages/mecha_engine/src/mecha_engine/learning','packages/mecha_engine/src/mecha_engine/archive',
    'packages/mecha_engine/src/mecha_engine/runtime')


def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def digest(value): return care_grid_sha256(value)
def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def sources():
    paths = [ROOT/relative for relative in SOURCE_FILES]
    paths += [path for relative in SOURCE_DIRS for path in sorted((ROOT/relative).glob('*.py'))]
    return {path.relative_to(ROOT).as_posix():hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def prefix(context, count):
    """An actually observed fresh-life prefix, with no invented missing ticks."""
    if context['events_omitted'] or context['care_summary']['from_age_ticks']:
        raise ValueError('registered care source must begin at its observed birth')
    events=deepcopy(context['events'][:count])
    if len(events)!=count or not events: raise ValueError('no common observed prefix')
    out=deepcopy(context)
    out['events']=events
    out['last_age_ticks']=events[-1]['tick']
    out['last_session_tick']=events[-1]['session_tick']
    out['outcome']='alive' if events[-1]['alive'] else 'dead'
    out['care_summary']={'history':'complete','from_age_ticks':0,'ticks_observed':count,
        'keeper_actions':dict(Counter(e['action'] for e in events if e['actor']=='keeper')),
        'companion_actions':dict(Counter(e['action'] for e in events if e['actor']=='companion')),
        'beg_requests':sum(int(e['begging']) for e in events)}
    return validate_care_context(out)


def freeze(learning_manifest):
    before_sources=sources()
    product=read(learning_manifest)
    if product.get('hatch_seed')!=20261006 or len(product.get('founders',[]))!=50:
        raise ValueError('registered full50 product hatch cohort missing')
    admissions=product.get('admissions',[])
    if len(admissions)!=50 or any(row.get('status')!='admitted' for row in admissions):
        raise ValueError('incomplete or refused product founder admission')
    slip=product['covenant']
    founders=[]
    for index,record in enumerate(product['founders'][:10]):
        model=GenerationModel(**record['model'])
        histories={}
        for care in ('fed','neglect'):
            pet=CompanionSession(record['grid'],slip,model=model,learning_policy='incumbent')
            for tick in range(1,13):
                if not pet.alive: break
                pet.advance('feed' if care=='fed' and tick%3==0 else None)
            histories[care]=capture_care_context(pet)
        count=min(len(ctx['events']) for ctx in histories.values())
        founders.append({'founder_index':index,'grid':record['grid'],'model':record['model'],
            'original_histories':histories,'used_prefix_ticks':count,
            'contexts':{name:prefix(ctx,count) for name,ctx in histories.items()}})
    if before_sources != sources(): raise ValueError('source changed during observed history freeze')
    return {'format':FORMAT,'learning_manifest_sha256':hashlib.sha256(Path(learning_manifest).read_bytes()).hexdigest(),
        'source_sha256':before_sources,'source_admissions':admissions,'founders':founders,'covenant':slip,
        'plan':[{'founder_index':index,'rng_seed':seed} for seed in SEEDS for index in range(10)],
        'protocol':{'evaluators':list(CARE_EVALUATORS),'pool_size':8,'seeds':list(SEEDS),
                    'requested_observed_ticks':12,'keeper_feeds_at':[3,6,9,12],
                    'pair_limit_seconds':PAIR_LIMIT,'total_limit_seconds':TOTAL_LIMIT}}


def altered_metadata(context):
    """Deliberately synthetic negative-control labels/counters, never lived data."""
    out=deepcopy(context)
    out['keeper_id']='negative-control'
    out['life_id']='negative-control:life-77'
    out['grid_id']='metadata-control'
    out['grid_sha256']='b'*64
    for key in ('last_age_ticks','last_session_tick'): out[key]+=10
    for event in out['events']:
        event['tick']+=10
        event['session_tick']+=10
    out['events_omitted']+=10
    out['care_summary']['ticks_observed']+=10
    counts=out['care_summary']['keeper_actions']
    counts['idle']=counts.get('idle',0)+10
    return validate_care_context(out)


def measure(manifest, pair_index):
    spec=manifest['plan'][pair_index]
    founder=manifest['founders'][spec['founder_index']]
    parent=founder['grid']; model=GenerationModel(**founder['model']); slip=manifest['covenant']
    before=digest((parent,slip,founder['contexts']))
    rows={}; checks={}
    pool_hashes=None
    old=generate_candidate(parent,model,slip,rng_seed=spec['rng_seed'])
    for mode in ('off','absent'):
        selected,receipt=select_care_successor(parent,model,slip,
            context=founder['contexts']['fed'] if mode=='off' else None,
            rng_seed=spec['rng_seed'],policy='off' if mode=='off' else CARE_POLICY)
        checks[mode+'_exact']=selected==old and receipt is None
    for evaluator in CARE_EVALUATORS:
        trials={}
        for name,context in founder['contexts'].items():
            args=dict(context=context,rng_seed=spec['rng_seed'],policy=CARE_POLICY,evaluator=evaluator)
            selected,receipt=select_care_successor(parent,model,slip,**args)
            repeated=prototype_select(parent,model,slip,**args)
            checks[evaluator+'_'+name+'_repeat_and_mirror']=(selected,receipt)==repeated
            control,control_receipt=select_care_successor(parent,model,slip,
                **{**args,'context':altered_metadata(context)})
            checks[evaluator+'_'+name+'_metadata_negative']=selected==control and receipt['candidates']==control_receipt['candidates']
            pool=[row['grid_sha256'] for row in receipt['candidates']]
            if pool_hashes is None: pool_hashes=pool
            checks[evaluator+'_'+name+'_same_candidate_bytes']=pool==pool_hashes
            chosen=receipt['candidates'][receipt['selected_index']]
            baseline=receipt['candidates'][0]
            checks[evaluator+'_'+name+'_welfare_nonregression']=chosen['need_balance']>=baseline['need_balance']
            checks[evaluator+'_'+name+'_survival_nonregression']=chosen['survival_ticks']>=baseline['survival_ticks']
            checks[evaluator+'_'+name+'_pristine_child']=all(cell['stress']==0 and cell['damage']==0 for cell in selected['cells'])
            trials[name]={'selected_grid':selected,'receipt':receipt}
        rows[evaluator]={'trials':trials,'selected_structures_differ':
            care_structure_sha256(trials['fed']['selected_grid'])!=care_structure_sha256(trials['neglect']['selected_grid'])}
    checks['input_immutable']=before==digest((parent,slip,founder['contexts']))
    checks['source_unchanged']=manifest['source_sha256']==sources()
    return {'pair_index':pair_index,**spec,'evaluators':rows,'checks':checks,
            'used_prefix_ticks':founder['used_prefix_ticks']}


def judge(rows, complete, source_unchanged, *, elapsed_seconds=0.0, failure=None):
    output={}
    identities_ok = len(rows) == PAIR_COUNT and all(
        isinstance(row, dict) and type(row.get('pair_index')) is int and row['pair_index'] == index
        and type(row.get('founder_index')) is int and row['founder_index'] == index % 10
        and type(row.get('rng_seed')) is int and row['rng_seed'] == SEEDS[index // 10]
        for index, row in enumerate(rows))
    controls_ok = bool(rows) and all(isinstance(row.get('checks'), dict)
        and set(row['checks']) == REQUIRED_CHECKS
        and all(row['checks'][key] is True for key in REQUIRED_CHECKS) for row in rows)
    for evaluator in CARE_EVALUATORS:
        relevant=[row for row in rows if evaluator in row.get('evaluators',{})]
        differences=sum(row['evaluators'][evaluator].get('selected_structures_differ') is True for row in relevant)
        runtime_ok = (type(elapsed_seconds) in (int, float) and 0 <= elapsed_seconds <= TOTAL_LIMIT
            and all(type(row.get('elapsed_seconds')) in (int, float)
                    and 0 <= row['elapsed_seconds'] <= PAIR_LIMIT for row in rows))
        gates={'complete_cohort':complete and len(relevant)==PAIR_COUNT and identities_ok,
               'registered_runtime':runtime_ok, 'no_operational_failure':failure is None,
               'source_unchanged':source_unchanged,
               'all_invariants':controls_ok,
               'structural_descendant_effect':differences>=1}
        failed=[name for name,value in gates.items() if value is not True]
        output[evaluator]={'verdict':'REFUSE' if failed else 'ADOPT','checks':gates,
                           'failed_checks':failed,'structural_different_pairs':differences}
    return output


def report(manifest, rows, status, failure, elapsed):
    unchanged=manifest is not None and manifest['source_sha256']==sources()
    return {'artifact_id':'observed_care_selection_stage0','date':'2026-10-06','status':status,
        'purpose':'Observed action-window contextual successor selection; no inherited physiology or learned state.',
        'manifest_sha256':digest(manifest) if manifest is not None else None,
        'source_artifacts':['docs/development/cycle-38-lived-care-and-thought.md',
                            '.development/x7/care/manifest.json'],
        'completed_pairs':len(rows),'planned_pairs':PAIR_COUNT,'elapsed_seconds':elapsed,
        'failure':failure,'decision':judge(rows,status=='complete',unchanged,
            elapsed_seconds=elapsed,failure=failure),'rows':rows,
        'external_product_gates':'Persistence, reproduction and native evidence are separate root integration gates.',
        'limitations':['The stress evaluator is the existing archive morphology probe on a copy.',
                       'Observed prefix evaluation restarts cold; it is not source-life replay.',
                       'Boundary seeds have overlapping candidate-seed ranges, not independent uncertainty.'],
        'next_research_step':'Keep refused paths opt-in; do not infer unmeasured product benefits.'}


def run(directory, learning_manifest, artifact):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    checkpoint_path=directory/'checkpoint.json'; manifest_path=directory/'manifest.json'
    if checkpoint_path.exists():
        raise ValueError('existing bounded study retained; no automatic retry or overwrite')
    start=time.monotonic(); rows=[];manifest=None; failure=None;status='incomplete'
    write(checkpoint_path,{'format':FORMAT,'status':'setup','at':datetime.now(timezone.utc).isoformat(),
                           'remaining_pairs':list(range(PAIR_COUNT)),'consumed_seconds':0})
    try:
        command=[sys.executable,'-B',__file__,'--freeze',str(learning_manifest),'--output',str(manifest_path)]
        subprocess.run(command,check=True,capture_output=True,text=True,timeout=min(PAIR_LIMIT,TOTAL_LIMIT))
        manifest=read(manifest_path)
        for index in range(PAIR_COUNT):
            remaining=TOTAL_LIMIT-(time.monotonic()-start)
            if remaining<=0: raise TimeoutError('registered cumulative300-second budget exhausted')
            row_path=directory/'rows'/f'pair-{index:02d}.json'
            write(checkpoint_path,{'format':FORMAT,'status':'running','active_pair':index,
                'manifest_sha256':digest(manifest),'completed_pairs':len(rows),
                'remaining_pairs':list(range(index,PAIR_COUNT)),'consumed_seconds':time.monotonic()-start})
            command=[sys.executable,'-B',__file__,'--worker',str(manifest_path),'--pair',str(index),'--output',str(row_path)]
            began=time.monotonic()
            subprocess.run(command,check=True,capture_output=True,text=True,timeout=min(PAIR_LIMIT,remaining))
            row=read(row_path)
            row['elapsed_seconds']=time.monotonic()-began
            row['manifest_sha256']=digest(manifest)
            row['receipt_sha256']=digest(row)
            write(row_path,row)
            rows.append(row)
            if row['elapsed_seconds'] > PAIR_LIMIT:
                raise TimeoutError('measured pair elapsed exceeds registered30-second bound')
            print(json.dumps({'completed_pair':index+1,'of':PAIR_COUNT,'elapsed_seconds':round(time.monotonic()-start,3)}),flush=True)
            if set(row['checks']) != REQUIRED_CHECKS or any(row['checks'][key] is not True for key in REQUIRED_CHECKS):
                failure={'kind':'hard_invariant','pair_index':index,'failed_checks':[key for key,value in row['checks'].items() if not value]}
                break
        else: status='complete'
    except (subprocess.TimeoutExpired,TimeoutError) as error:
        failure={'kind':'registered_runtime_limit','detail':str(error)}
    except subprocess.CalledProcessError as error:
        failure={'kind':'worker_error','detail':error.stderr or error.stdout}
    except (ValueError,OSError,KeyError) as error:
        failure={'kind':'invalid_inputs_or_sources','detail':str(error)}
    elapsed=time.monotonic()-start
    if elapsed > TOTAL_LIMIT:
        status='incomplete'
        failure={'kind':'registered_runtime_limit','detail':'measured elapsed exceeds cumulative300-second bound'}
    result=report(manifest,rows,status,failure,elapsed)
    write(artifact,result)
    write(checkpoint_path,{'format':FORMAT,'status':status,'failure':failure,'completed_pairs':len(rows),
        'remaining_pairs':list(range(len(rows),PAIR_COUNT)),'consumed_seconds':elapsed,
        'artifact':str(Path(artifact).relative_to(ROOT).as_posix()),
        'next_action':'Review retained decision; do not auto-resume failed candidate.'})
    print(json.dumps({'status':status,'decisions':result['decision'],'failure':failure},indent=2))
    return 0 if status=='complete' else 2


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run',type=Path)
    parser.add_argument('--learning-manifest',type=Path,default=ROOT/'.development/x7/learning/manifest.json')
    parser.add_argument('--artifact',type=Path,default=ROOT/'data/game_client/observed_care_selection_stage0.json')
    parser.add_argument('--freeze',type=Path);parser.add_argument('--worker',type=Path)
    parser.add_argument('--pair',type=int);parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.freeze:
        write(args.output,freeze(args.freeze));return 0
    if args.worker:
        manifest=read(args.worker)
        if manifest['source_sha256']!=sources(): raise ValueError('frozen source changed')
        write(args.output,measure(manifest,args.pair));return 0
    return run(args.run,args.learning_manifest,args.artifact)

if __name__=='__main__':raise SystemExit(main())
