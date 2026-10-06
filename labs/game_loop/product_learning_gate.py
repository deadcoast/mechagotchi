"""X7: bounded, source-bound comparison of the three actual product policies.

The pre-RED contract is docs/development/cycle-38-lived-care-and-thought.md.
Never changes a product default or regenerates a historical experiment.
"""
from __future__ import annotations
import argparse
import copy
import dataclasses
from decimal import Decimal, InvalidOperation
import hashlib
import io
import json
import math
import os
from pathlib import Path
import random
import subprocess
import sys
import time
import unittest
from collections import Counter
from statistics import mean
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
for relative in ('labs/game_loop','labs/micro_threads','labs/grid_genome','game/src','packages/mecha_engine/src'):
    sys.path.insert(0,str(ROOT/relative))
from playable_learning_gate import (
    ARMS, COVENANT, KEEP_THRESHOLD_PCT, KEEPER_IDS, FULL_TICKS,
    FULL_LIFECYCLES_PER_KEEPER, SEED_BASE, load_inputs,
    q3_candidate, summarize as original_summary,
)
from default_covenant_gate import keeper_arm
from ablation_gates import keeper_respond
from test_package_qtable_parity import PackageQtableParityTests
from mecha_engine.generation import GenerationModel, train_generation_model
from mecha_engine.learning import decide
from mecha_engine.lifecycle import DANGER_THRESHOLDS
from mecha_game.hatchery import hatch_founders
from mecha_game.session import CompanionSession

REPAIR_APPENDIX='docs/development/cycle-38-learning-instrument-repair.md'
GATE_SOURCE='labs/game_loop/product_learning_gate.py'
FORMAT='product_learning_cohort_v1'
HATCH_SEED=20261006
SETUP_LIMIT=120.0
TRIAL_LIMIT=20.0
TOTAL_LIMIT=1200.0
SETUP_CHECKS=frozenset(('instruments','parity','attentive_survives','neglect_unchanged'))
REQUIRED=frozenset(('instruments','parity','complete_budget','corpus_comparable',
    'consumer_fires','gain_vs_incumbent','gain_vs_additive','attentive_survives',
    'neglect_unchanged','runtime','source_binding','cold_learning','voluntary_feeding'))
SOURCES=(
    REPAIR_APPENDIX,
    'docs/development/cycle-38-lived-care-and-thought.md',
    'labs/game_loop/product_learning_gate.py','labs/game_loop/playable_learning_gate.py',
    'labs/game_loop/default_covenant_gate.py','labs/micro_threads/ablation_gates.py',
    'labs/micro_threads/synthetic_keepers.py','labs/micro_threads/test_package_qtable_parity.py',
    'labs/micro_threads/thread_fleet.py','labs/grid_genome/micro_switchboard.py',
    'labs/grid_genome/corpus_builder.py',
    'data/micro_threads/qtable_consumer_gate_stage0.json',
    'data/micro_threads/package_qtable_parity_stage0.json',
    'data/game_client/playable_learning_gate_stage0.json',
    'data/game_client/default_covenant_gate_stage0.json',COVENANT,
)


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def encoded(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def write_json(path,value,*,exclusive=False):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    content=json.dumps(value,indent=2,allow_nan=False)+'\n'
    if exclusive:
        with path.open('x',encoding='utf-8',newline='\n') as stream:stream.write(content)
    else:
        temporary=path.with_suffix(path.suffix+'.tmp')
        temporary.write_text(content,encoding='utf-8',newline='\n')
        # Windows readers may briefly deny delete sharing while the supervisor
        # reads progress. Retry publication only; no simulation is replayed.
        for attempt in range(20):
            try:
                os.replace(temporary,path)
                break
            except PermissionError as error:
                if getattr(error,'winerror',None) not in (5,32) or attempt==19:
                    raise
                time.sleep(.01)


def snapshot_sources():
    paths={ROOT/name for name in SOURCES}
    # Include complete package/game source closures; a resumed measurement cannot
    # silently mix versions when an indirectly imported helper changes.
    for directory in ('packages/mecha_engine/src/mecha_engine','game/src/mecha_game'):
        paths.update((ROOT/directory).rglob('*.py'))
    # Capture loaded research helper modules as well as the complete product
    # trees. Parity imports occur at module load so the set stays stable.
    for module in tuple(sys.modules.values()):
        filename=getattr(module,'__file__',None)
        if filename:
            path=Path(filename).resolve()
            if path.suffix=='.py' and path.is_relative_to(ROOT/'labs'):
                paths.add(path)
    paths.update((ROOT/'data/seed_grids_16x16').glob('mg_seed16_*.json'))
    return {path.relative_to(ROOT).as_posix():hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(paths)}


def gain_at_least(candidate,baseline):
    if candidate is None or baseline is None:return False
    try:
        left,right=Decimal(str(candidate)),Decimal(str(baseline))
        return (left.is_finite() and right.is_finite() and right>0 and
                (left-right)*100 >= Decimal(str(KEEP_THRESHOLD_PCT))*right)
    except (InvalidOperation,ValueError):return False


def gain(candidate,baseline):
    if candidate is None or baseline is None or baseline<=0:return None
    return float((Decimal(str(candidate))-Decimal(str(baseline)))*100/Decimal(str(baseline)))


def gain_rows_at_least(candidate_rows,baseline_rows):
    """Compare exact sums of registered six-decimal rows, never rounded means."""
    if not candidate_rows or not baseline_rows:return False
    if any(row.get('status')!='admitted' for row in candidate_rows+baseline_rows):return False
    left=sum((Decimal(str(row['welfare'])) for row in candidate_rows),Decimal(0))
    right=sum((Decimal(str(row['welfare'])) for row in baseline_rows),Decimal(0))
    if not left.is_finite() or not right.is_finite() or right<=0:return False
    lhs=left*len(baseline_rows);rhs=right*len(candidate_rows)
    return (lhs-rhs)*100>=Decimal(str(KEEP_THRESHOLD_PCT))*rhs


def exact_comparison(candidate_rows,baseline_rows):
    if not candidate_rows or not baseline_rows or any(row.get('status')!='admitted' for row in candidate_rows+baseline_rows):return None
    left=sum((Decimal(str(row['welfare'])) for row in candidate_rows),Decimal(0))
    right=sum((Decimal(str(row['welfare'])) for row in baseline_rows),Decimal(0))
    numerator=(left*len(baseline_rows)-right*len(candidate_rows))*100
    denominator=right*len(candidate_rows)
    return dict(candidate_welfare_sum=str(left),baseline_welfare_sum=str(right),
        candidate_count=len(candidate_rows),baseline_count=len(baseline_rows),
        percent_numerator=str(numerator),percent_denominator=str(denominator),
        gain_pct=float(numerator/denominator) if denominator>0 else None)


def judge(checks):
    failed=sorted(name for name in REQUIRED if checks.get(name) is not True)
    return {'verdict':'REFUSE' if failed else 'ADOPT','failed_checks':failed,
        'rule':'Complete source-bound product cohort, exact >=5% welfare against BOTH comparators, preserved controls and bounded runtime.'}


def build_plan():
    return [dict(keeper_id=keeper,life_index=index,founder_index=index%50,arm=arm,
                 rng_seed=SEED_BASE+keeper_index*100000+index,ticks_requested=FULL_TICKS)
        for keeper_index,keeper in enumerate(KEEPER_IDS)
        for index in range(FULL_LIFECYCLES_PER_KEEPER) for arm in ARMS]


def run_trial(grid,slip,model,keeper,arm,ticks,seed):
    if arm not in ARMS:raise ValueError('Unknown preregistered learning arm')
    row=dict(grid_id=grid['grid_id'],keeper_id=keeper,arm=arm,rng_seed=seed,ticks_requested=ticks)
    try:pet=CompanionSession(grid,slip,model=model,learning_policy='incumbent' if arm=='incumbent' else 'qtable')
    except ValueError as error:return dict(row,status='refused',reason=str(error))
    if arm=='additive':pet.state['learning_switches']['qtable_consumer']=False
    initial_entries=len((pet.state.get('thread_states',{}).get('qtable_policy') or {}).get('q',{}))
    rng=random.Random(seed);total=0.0;begs=0;recommendations=0;followed=0
    executed=Counter();care=Counter();danger=Counter();trajectory=hashlib.sha256()
    def observed_decide(state):
        nonlocal recommendations
        result=decide(state);recommendations+=int('qtable_consumer' in result)
        return result
    with patch('mecha_game.session.decide',side_effect=observed_decide):
        for _ in range(ticks):
            if not pet.alive:break
            pet.advance(keeper_respond(keeper,pet.state,pet.begging,rng))
            entry=pet.log[-1];total+=pet.state['history'][-1]['balance']
            begs+=int(entry['begging']);executed[entry['action']]+=1
            if entry['actor']=='keeper':care[entry['action']]+=1
            followed+=int('qtable_consumer' in (entry.get('thought') or {}))
            for axis,threshold in DANGER_THRESHOLDS.items():
                danger[axis]+=int(pet.state[axis]>=threshold if axis in ('hunger','stress') else pet.state[axis]<=threshold)
            trajectory.update(encoded(dict(tick=pet.state['age_ticks'],actor=entry['actor'],
                action=entry['action'],begging=entry['begging'],alive=pet.alive,
                needs={key:pet.state[key] for key in (*DANGER_THRESHOLDS,'cleanliness')})))
    return dict(row,status='admitted',survival_ticks=pet.state['age_ticks'],alive=pet.alive,
        death_cause=pet.death_cause,welfare=round(total/ticks,6),beg_ticks=begs,
        consumer_recommendations=recommendations,consumer_executed_ticks=followed,
        executed_actions={key:executed[key] for key in ('feed','play','sleep','idle','mutate','clean')},
        keeper_actions={key:care[key] for key in ('feed','play','sleep','clean')},
        final_cleanliness=pet.state['cleanliness'],danger_ticks=dict(danger),
        initial_qtable_entries=initial_entries,trajectory_sha256=trajectory.hexdigest())


def summarize(rows):
    summary=original_summary(rows);accepted=[row for row in rows if row['status']=='admitted']
    danger=Counter();deaths=Counter()
    for row in accepted:
        danger.update(row['danger_ticks'])
        if not row['alive']:deaths[row['death_cause']]+=1
    summary.update(deaths_before_horizon=sum(not row['alive'] for row in accepted),
        death_causes=dict(deaths),danger_ticks=dict(danger),
        unique_trajectories=len({row['trajectory_sha256'] for row in accepted}))
    return summary


def make_receipt(index,row,manifest_sha,previous,elapsed):
    result=dict(index=index,row=row,manifest_sha256=manifest_sha,
                previous_receipt_sha256=previous,elapsed_seconds=elapsed)
    result['receipt_sha256']=digest(result)
    return result


def check_receipts(receipts,manifest_sha,plan):
    previous=None;rows=[]
    for index,receipt in enumerate(receipts):
        body={key:value for key,value in receipt.items() if key!='receipt_sha256'}
        if (index>=len(plan) or receipt.get('index')!=index or receipt.get('manifest_sha256')!=manifest_sha
                or receipt.get('previous_receipt_sha256')!=previous or digest(body)!=receipt.get('receipt_sha256')
                or any(receipt.get('row',{}).get(key)!=value for key,value in plan[index].items())):
            raise ValueError('Learning receipt chain or paired input identity is invalid')
        elapsed=receipt.get('elapsed_seconds')
        if type(elapsed) not in (int,float) or not math.isfinite(elapsed) or elapsed<0:
            raise ValueError('Learning receipt runtime must be finite and nonnegative')
        rows.append(receipt['row']);previous=receipt['receipt_sha256']
    return rows


def instrument_controls():
    original=read_json(ROOT/'data/game_client/playable_learning_gate_stage0.json')
    seeds,slip,models=load_inputs();comparisons=[]
    # Exactly 15 complete historical rows plus all three fixed palette refusals.
    for keeper in KEEPER_IDS:
        for arm in ARMS:
            expected=next(row for row in original['metrics']['trials'] if row['keeper_id']==keeper
                and row['arm']==arm and row['rng_seed']==SEED_BASE+KEEPER_IDS.index(keeper)*100000)
            actual=run_trial(seeds[0],slip,models[0],keeper,arm,FULL_TICKS,expected['rng_seed'])
            comparisons.append(dict(keeper=keeper,arm=arm,match=expected=={key:actual.get(key) for key in expected},
                                    expected=expected,actual={key:actual.get(key) for key in expected}))
            if not comparisons[-1]['match']:
                return dict(checks={'instruments':False},historical_rows=comparisons,historical_refusals=[],
                            stopped_at='historical_row_mismatch')
    refusals=[]
    for arm in ARMS:
        expected=next(row for row in original['metrics']['trials'] if row['keeper_id']=='attentive'
            and row['arm']==arm and row['rng_seed']==SEED_BASE+1)
        actual=run_trial(seeds[1],slip,models[1],'attentive',arm,FULL_TICKS,SEED_BASE+1)
        refusals.append(dict(arm=arm,match=expected==actual,expected=expected,actual=actual))
        if not refusals[-1]['match']:
            return dict(checks={'instruments':False},historical_rows=comparisons,historical_refusals=refusals,
                        stopped_at='historical_refusal_mismatch')
    output=io.StringIO();test_result=unittest.TextTestRunner(stream=output,verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(PackageQtableParityTests))
    prior=read_json(ROOT/'data/micro_threads/package_qtable_parity_stage0.json')['metrics']
    q1_hash=hashlib.sha256((ROOT/'data/micro_threads/qtable_consumer_gate_stage0.json').read_bytes()).hexdigest()
    if not (test_result.wasSuccessful() and test_result.testsRun==5
            and prior['complete_q1_record_reproduced'] is True and prior['original_q1_sha256']==q1_hash):
        return dict(checks={'instruments':False,'parity':test_result.wasSuccessful() and test_result.testsRun==5},
                    historical_rows=comparisons,historical_refusals=refusals,parity_output=output.getvalue(),
                    stopped_at='parity_or_q1_binding')
    q3=read_json(ROOT/'data/game_client/default_covenant_gate_stage0.json')['metrics']
    incumbent={'attentive':keeper_arm(True),'neglect':keeper_arm(False)}
    if incumbent['attentive']!=q3['candidate_attentive'] or incumbent['neglect']!=q3['candidate_neglect']:
        return dict(checks={'instruments':False,'parity':True},historical_rows=comparisons,
                    historical_refusals=refusals,incumbent_controls=incumbent,stopped_at='q3_incumbent_mismatch')
    candidate={'attentive':q3_candidate(True),'neglect':q3_candidate(False)}
    checks=dict(instruments=all(row['match'] for row in comparisons+refusals)
            and prior['complete_q1_record_reproduced'] is True and prior['original_q1_sha256']==q1_hash
            and incumbent['attentive']==q3['candidate_attentive'] and incumbent['neglect']==q3['candidate_neglect'],
        parity=test_result.wasSuccessful() and test_result.testsRun==5,
        attentive_survives=candidate['attentive']['alive'] and candidate['attentive']['age_ticks']==400,
        neglect_unchanged=candidate['neglect']['age_ticks']==q3['candidate_neglect']['age_ticks']
            and candidate['neglect']['death_cause']==q3['candidate_neglect']['death_cause'])
    return dict(checks=checks,historical_rows=comparisons,historical_refusals=refusals,
        parity_output=output.getvalue(),parity_tests=test_result.testsRun,q1_sha256=q1_hash,
        incumbent_controls=incumbent,candidate_controls=candidate)


def create_manifest():
    source=snapshot_sources()
    corpus=[read_json(path) for path in sorted((ROOT/'data/seed_grids_16x16').glob('mg_seed16_*.json'))]
    if len(corpus)!=50:raise ValueError('The registered hatchery corpus must contain all50 shipped founders')
    slip=read_json(ROOT/COVENANT)
    founders=hatch_founders(corpus,slip,count=50,rng_seed=HATCH_SEED)
    for founder in founders:founder['model']=dataclasses.asdict(train_generation_model([founder['grid']]))
    controls=instrument_controls()
    # Test all generated outputs, keeping every actual admission/refusal.
    admissions=[]
    for index,founder in enumerate(founders) if all(controls['checks'].get(key) is True for key in SETUP_CHECKS) else []:
        try:
            CompanionSession(founder['grid'],slip,model=GenerationModel(**founder['model']))
            admissions.append(dict(founder_index=index,status='admitted'))
        except ValueError as error:
            admissions.append(dict(founder_index=index,status='refused',reason=str(error)))
            break
    return dict(format=FORMAT,source_sha256=source,source_unchanged=source==snapshot_sources(),
        hatch_seed=HATCH_SEED,founders=founders,source_corpus=corpus,covenant=slip,
        controls=controls,admissions=admissions,plan=build_plan(),
        budgets=dict(setup_seconds=SETUP_LIMIT,trial_seconds=TRIAL_LIMIT,total_seconds=TOTAL_LIMIT))


def validate_manifest(manifest):
    """Structural study identity is checked independently of self-hashed receipts."""
    if (not isinstance(manifest,dict) or manifest.get('format')!=FORMAT
            or manifest.get('hatch_seed')!=HATCH_SEED or manifest.get('plan')!=build_plan()
            or manifest.get('budgets')!=dict(setup_seconds=SETUP_LIMIT,trial_seconds=TRIAL_LIMIT,total_seconds=TOTAL_LIMIT)
            or manifest.get('covenant')!=read_json(ROOT/COVENANT)):
        raise ValueError('Learning manifest differs from the preregistered study')
    source_corpus=[read_json(path) for path in sorted((ROOT/'data/seed_grids_16x16').glob('mg_seed16_*.json'))]
    if len(source_corpus)!=50 or manifest.get('source_corpus')!=source_corpus:
        raise ValueError('Learning manifest source corpus differs from all50 ordered shipped genomes')
    founders=manifest.get('founders')
    if not isinstance(founders,list) or len(founders)!=50:
        raise ValueError('Learning manifest must retain exactly50 generated founders')
    for founder in founders:
        if not isinstance(founder,dict) or set(founder)!={'grid','explanation','model'}:
            raise ValueError('Learning manifest founder fields are invalid')
        GenerationModel(**founder['model']).validate_for(founder['grid']['grid_size'])
    admissions=manifest.get('admissions')
    if (not isinstance(admissions,list) or len(admissions)>50
            or any(row.get('founder_index')!=index or row.get('status') not in ('admitted','refused')
                   for index,row in enumerate(admissions))):
        raise ValueError('Learning manifest founder admissions are not ordered occurrences')
    if not isinstance(manifest.get('controls'),dict) or not isinstance(manifest['controls'].get('checks'),dict):
        raise ValueError('Learning manifest controls are missing')
    return manifest


def prepare_instrument_repair(prior_directory):
    """Only the recorded sharing-error instrument failure permits this attempt."""
    prior_directory=Path(prior_directory)
    manifest=read_json(prior_directory/'manifest.json')
    report=read_json(prior_directory/'report.json')
    budget=read_json(prior_directory/'budget.json')
    failure=read_json(prior_directory/'failure.json')
    stderr=(prior_directory/'worker.stderr.log').read_text(encoding='utf-8')
    validate_manifest(manifest)
    receipts=[read_json(path) for path in sorted((prior_directory/'rows').glob('*.json'))]
    rows=check_receipts(receipts,digest(manifest),manifest['plan'])
    current=snapshot_sources();prior=manifest['source_sha256']
    if (manifest.get('instrument_repair') is not None or budget.get('state')!='refused'
            or failure!={'reason':'worker_error','exit_code':1}
            or 'PermissionError: [WinError 5]' not in stderr or 'progress.json' not in stderr
            or report.get('decision',{}).get('verdict')!='REFUSE'
            or set(report['decision'].get('failed_checks',[]))!={'complete_budget','runtime'}
            or report.get('input_manifest')!=manifest or report.get('input_manifest_sha256')!=digest(manifest)
            or report.get('metrics',{}).get('trials')!=rows
            or report['metrics'].get('budget')!=budget or report['metrics'].get('failure')!=failure
            or report.get('last_receipt_sha256')!=(receipts[-1]['receipt_sha256'] if receipts else None)
            or not rows or len(rows)>=len(build_plan())
            or any(receipt['elapsed_seconds']>TRIAL_LIMIT for receipt in receipts)
            or not all(manifest['controls']['checks'].get(key) is True for key in SETUP_CHECKS)):
        raise ValueError('Only the retained Windows publication instrument failure qualifies for the one repair attempt')
    if set(current)-set(prior)!={REPAIR_APPENDIX} or set(prior)-set(current):
        raise ValueError('Instrument repair source membership changed beyond the registered appendix')
    changed={name for name,value in prior.items() if current.get(name)!=value}
    if not changed<= {GATE_SOURCE}:
        raise ValueError('Instrument repair changed product or research sources beyond the reviewed harness')
    debit=budget.get('consumed_seconds')
    if type(debit) not in (int,float) or not math.isfinite(debit) or not 0<=debit<SETUP_LIMIT:
        raise ValueError('Instrument repair has no remaining conservative setup budget')
    result=copy.deepcopy(manifest)
    result['source_sha256']=current;result['source_unchanged']=True
    result['instrument_repair']=dict(
        rule=REPAIR_APPENDIX,prior_manifest_sha256=digest(manifest),
        prior_report_sha256=hashlib.sha256((prior_directory/'report.json').read_bytes()).hexdigest(),
        prior_worker_error=stderr,
        prior_completed_rows=rows,prior_last_receipt_sha256=receipts[-1]['receipt_sha256'],
        debited_seconds=debit,allowed_source_changes=sorted(changed),
        remaining_total_seconds=TOTAL_LIMIT-debit,remaining_setup_seconds=SETUP_LIMIT-debit,
        publication_retry_recomputes_trials=False,
        new_attempt_repeats_registered_cohort=True,
        prior_rows_reproduction_required=len(rows),
        automatic_trial_retries=False,
        reason='One explicitly preregistered new instrument attempt; no automatic terminal resume.')
    return result


def verify_repaired_prefix(row,index,manifest):
    prior=(manifest.get('instrument_repair') or {}).get('prior_completed_rows',[])
    if index<len(prior) and row!=prior[index]:
        raise ValueError('Repaired instrument did not exactly reproduce the retained prior row')


def worker(directory):
    directory=Path(directory);manifest_path=directory/'manifest.json'
    if manifest_path.exists():manifest=read_json(manifest_path)
    elif (directory/'repair-input.json').exists():
        manifest=read_json(directory/'repair-input.json')
        controls=instrument_controls()
        manifest['controls']=controls
        manifest['source_unchanged']=manifest['source_sha256']==snapshot_sources()
        write_json(manifest_path,manifest,exclusive=True)
    else:
        write_json(directory/'progress.json',dict(phase='setup',started=time.monotonic()))
        manifest=create_manifest();write_json(manifest_path,manifest,exclusive=True)
    validate_manifest(manifest)
    if manifest['source_sha256']!=snapshot_sources() or not manifest['source_unchanged']:
        raise ValueError('Source inputs changed; refuse to mix measurements')
    if not all(manifest['controls']['checks'].get(key) is True for key in SETUP_CHECKS):
        write_json(directory/'failure.json',dict(reason='mandatory_instrument_or_care_control'));return 2
    if len(manifest['admissions'])!=50 or any(row['status']!='admitted' for row in manifest['admissions']):
        write_json(directory/'failure.json',dict(reason='corpus_admission'));return 2
    manifest_sha=digest(manifest);plan=manifest['plan']
    receipts=[read_json(path) for path in sorted((directory/'rows').glob('*.json'))]
    rows=check_receipts(receipts,manifest_sha,plan)
    previous=receipts[-1]['receipt_sha256'] if receipts else None
    for index in range(len(rows),len(plan)):
        item=plan[index];started=time.monotonic()
        write_json(directory/'progress.json',dict(phase='trial',index=index,started=started))
        founder=manifest['founders'][item['founder_index']]
        row=run_trial(founder['grid'],manifest['covenant'],GenerationModel(**founder['model']),
            item['keeper_id'],item['arm'],item['ticks_requested'],item['rng_seed'])
        row.update(item);elapsed=time.monotonic()-started
        try:verify_repaired_prefix(row,index,manifest)
        except ValueError as error:
            write_json(directory/'failure.json',dict(reason='prior_row_mismatch',index=index,detail=str(error),actual_row=row));return 2
        receipt=make_receipt(index,row,manifest_sha,previous,elapsed)
        write_json(directory/'rows'/f'{index:04d}.json',receipt,exclusive=True)
        previous=receipt['receipt_sha256']
        if row['status']!='admitted' or elapsed>TRIAL_LIMIT:
            write_json(directory/'failure.json',dict(reason='trial_admission_or_runtime',index=index));return 2
    write_json(directory/'progress.json',dict(phase='complete',started=time.monotonic(),rows=len(plan)))
    return 0


def build_report(directory):
    directory=Path(directory);manifest=read_json(directory/'manifest.json') if (directory/'manifest.json').exists() else None
    if manifest is not None:validate_manifest(manifest)
    budget=read_json(directory/'budget.json')
    failure=read_json(directory/'failure.json') if (directory/'failure.json').exists() else None
    receipts=[read_json(path) for path in sorted((directory/'rows').glob('*.json'))]
    rows=check_receipts(receipts,digest(manifest),manifest['plan']) if manifest else []
    arm_rows={arm:[row for row in rows if row['arm']==arm] for arm in ARMS}
    arms={arm:summarize(arm_rows[arm]) for arm in ARMS}
    by_keeper={arm:{keeper:summarize([row for row in rows if row['arm']==arm and row['keeper_id']==keeper])
        for keeper in KEEPER_IDS} for arm in ARMS}
    checks=dict(manifest['controls']['checks']) if manifest else {}
    repaired_prefix=(manifest.get('instrument_repair') or {}).get('prior_completed_rows',[]) if manifest else []
    prefix_verified=len(rows)>=len(repaired_prefix) and rows[:len(repaired_prefix)]==repaired_prefix
    checks.update(complete_budget=len(rows)==len(build_plan()),
        corpus_comparable=bool(manifest) and len(manifest['admissions'])==50
            and all(row['status']=='admitted' for row in manifest['admissions'])
            and all(row['status']=='admitted' for row in rows),
        consumer_fires=arms['follower']['consumer_executed_ticks']>0,
        gain_vs_incumbent=gain_rows_at_least(arm_rows['follower'],arm_rows['incumbent']),
        gain_vs_additive=gain_rows_at_least(arm_rows['follower'],arm_rows['additive']),
        runtime=type(budget['consumed_seconds']) in (int,float) and math.isfinite(budget['consumed_seconds'])
            and 0<=budget['consumed_seconds']<=TOTAL_LIMIT and budget['state']=='complete' and failure is None
            and all(receipt['elapsed_seconds']<=TRIAL_LIMIT for receipt in receipts),
        source_binding=bool(manifest) and manifest['source_unchanged'] and manifest['source_sha256']==snapshot_sources() and prefix_verified,
        cold_learning=bool(rows) and all(row.get('initial_qtable_entries')==0 for row in rows),
        voluntary_feeding=bool(rows) and all(row.get('status')=='admitted' and
            row['executed_actions']['feed']==row['keeper_actions']['feed'] for row in rows))
    return dict(artifact_id='product_learning_gate_stage1' if manifest and manifest.get('instrument_repair') else 'product_learning_gate_stage0',date='2026-10-06',
        status='complete' if checks['complete_budget'] else 'incomplete',
        purpose='A separate product-compatible comparison; historical R3 REFUSE is preserved.',
        source_artifacts=list(SOURCES),parameters=dict(arms=list(ARMS),keepers=list(KEEPER_IDS),
            founder_count=50,hatch_seed=HATCH_SEED,lifecycles_per_keeper=FULL_LIFECYCLES_PER_KEEPER,
            ticks=FULL_TICKS,seed_base=SEED_BASE,threshold_pct=KEEP_THRESHOLD_PCT,
            keeper_mapping='Unchanged keeper_respond using previous displayed beg; no additional cleaning.',
            budgets=dict(setup=SETUP_LIMIT,trial=TRIAL_LIMIT,total=TOTAL_LIMIT)),
        metrics=dict(arms=arms,by_keeper=by_keeper,trials=rows,checks=checks,
            unique_founder_structures=len({digest({key:founder['grid'][key] for key in ('grid_size','cells','organs','palette')})
                for founder in manifest['founders']}) if manifest else None,
            structural_diagnostic='Counts distinct stored body/organ/palette structures; no personality or effectiveness claim.',
            exact_comparisons={arm:exact_comparison(arm_rows['follower'],arm_rows[arm]) for arm in ('incumbent','additive')},
            display_gain_pct={arm:gain(arms['follower']['welfare'],arms[arm]['welfare']) for arm in ('incumbent','additive')},
            repaired_prior_prefix_verified=prefix_verified,
            repaired_prior_rows=len(repaired_prefix),
            controls=manifest['controls'] if manifest else None,
            admissions=manifest['admissions'] if manifest else [],budget=budget,failure=failure),
        input_manifest=manifest,
        input_manifest_sha256=digest(manifest) if manifest else None,
        source_sha256=manifest['source_sha256'] if manifest else {},
        last_receipt_sha256=receipts[-1]['receipt_sha256'] if receipts else None,
        closed_states=sorted(key for key,value in checks.items() if value),
        blocked_states=sorted(key for key,value in checks.items() if not value),
        decision=judge(checks),deployment=dict(default='incumbent',changed=False,
            verdict='REFUSE',reason='Independent integrated native/save evidence required; this harness never changes product policy.'),
        next_research_step='Interpret this complete or incomplete registered cohort; do not resume a terminal failure or retune criteria.')


def supervise(directory,*,resume=False,instrument_repair_from=None):
    entered=time.monotonic()
    directory=Path(directory)
    if instrument_repair_from is not None and resume:raise ValueError('Instrument repair is a new attempt, never a resume')
    repair_input=None
    if instrument_repair_from is not None:
        if (directory.resolve()!=ROOT/'.development/x7/learning-instrument-repair-01'
                or Path(instrument_repair_from).resolve()!=ROOT/'.development/x7/learning'):
            raise ValueError('Only the one preregistered repair attempt location is authorized')
        repair_input=prepare_instrument_repair(instrument_repair_from)
    if directory.exists() and not resume:raise ValueError('Run directory exists; use explicit resume only for an interrupted run')
    directory.mkdir(parents=True,exist_ok=True)
    budget_path=directory/'budget.json';consumed=0.0;setup_debit=0.0
    if repair_input is not None:
        consumed=setup_debit=repair_input['instrument_repair']['debited_seconds']
        write_json(directory/'repair-input.json',repair_input,exclusive=True)
    if resume:
        budget=read_json(budget_path)
        if budget['state']!='interrupted':raise ValueError('Only an interrupted study may resume; terminal failures do not retry')
        consumed=budget['consumed_seconds']
        if type(consumed) not in (int,float) or not math.isfinite(consumed) or consumed<0:
            raise ValueError('Resume cumulative runtime must be finite and nonnegative')
        manifest=read_json(directory/'manifest.json')
        if manifest['source_sha256']!=snapshot_sources():raise ValueError('Resume source inputs differ')
        validate_manifest(manifest)
        setup_debit=(manifest.get('instrument_repair') or {}).get('debited_seconds',0.0)
        if (directory/'failure.json').exists():raise ValueError('A mandatory failure cannot resume')
        check_receipts([read_json(path) for path in sorted((directory/'rows').glob('*.json'))],digest(manifest),manifest['plan'])
    if consumed>=TOTAL_LIMIT:raise ValueError('Registered cumulative runtime budget is exhausted')
    started=entered;state='running';reason=None;process=None;last_source_check=started
    def save_budget():
        write_json(budget_path,dict(format=FORMAT,state=state,consumed_seconds=consumed+time.monotonic()-started,
            limit_seconds=TOTAL_LIMIT,reason=reason,worker_pid=process.pid if process else None,
            previous_attempt_debit_seconds=setup_debit,remaining_setup_seconds=SETUP_LIMIT-setup_debit))
    save_budget()
    # A resumed worker gets a new validation/setup phase; a previous trial's
    # monotonic timestamp must never trigger a false watchdog before startup.
    write_json(directory/'progress.json',dict(phase='setup',started=started))
    try:
        with (directory/'worker.stdout.log').open('a',encoding='utf-8') as stdout, (directory/'worker.stderr.log').open('a',encoding='utf-8') as stderr:
            process=subprocess.Popen([sys.executable,'-B',str(Path(__file__).resolve()),'--worker',str(directory)],
                cwd=ROOT,stdout=stdout,stderr=stderr,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            while process.poll() is None:
                now=time.monotonic();active=read_json(directory/'progress.json') if (directory/'progress.json').exists() else {}
                phase=active.get('phase','setup');phase_started=active.get('started',started)
                if now-last_source_check>=1 and (directory/'manifest.json').exists():
                    manifest=read_json(directory/'manifest.json')
                    if manifest['source_sha256']!=snapshot_sources():reason='source_changed_during_run'
                    last_source_check=now
                if reason is None and consumed+now-started>=TOTAL_LIMIT:reason='cumulative_runtime_limit'
                elif phase=='setup' and now-started>=SETUP_LIMIT-setup_debit:reason='setup_runtime_limit'
                elif phase=='trial' and now-phase_started>=TRIAL_LIMIT:reason='trial_runtime_limit'
                if reason:
                    process.terminate();process.wait(timeout=10);state='refused'
                    write_json(directory/'failure.json',dict(reason=reason,active=active));break
                save_budget();time.sleep(.2)
            if reason is None:state='complete' if process.returncode==0 else 'refused'
            if state=='refused' and not (directory/'failure.json').exists():
                write_json(directory/'failure.json',dict(reason='worker_error',exit_code=process.returncode))
    except KeyboardInterrupt:
        state='interrupted';reason='foreground_interruption'
    finally:
        if process is not None and process.poll() is None:
            process.terminate();process.wait(timeout=10)
        save_budget()
    report=build_report(directory);write_json(directory/'report.json',report)
    return report


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir',type=Path)
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--instrument-repair-from',type=Path)
    parser.add_argument('--worker',type=Path,help=argparse.SUPPRESS)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(argv)
    if args.worker:return worker(args.worker)
    if args.run_dir is None:parser.error('--run-dir is required')
    report=supervise(args.run_dir.resolve(),resume=args.resume,instrument_repair_from=args.instrument_repair_from)
    if args.output:write_json(args.output,report,exclusive=True)
    print(json.dumps(dict(status=report['status'],decision=report['decision'],metrics=report['metrics']['arms']),indent=2))
    return 0 if report['status']=='complete' else 2

if __name__=='__main__':raise SystemExit(main())
