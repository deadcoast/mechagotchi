"""X6 conditional evolution qualification, preregistered before RED/run.

Fixed six FRESH runs: legacy/operative_permissions_v1 at DR0052 seeds
20260709,21260712,22260715; population256, 20,480 scored evaluations,
24 lifecycle ticks, novelty_first, pool_factor3, constrained generation,
explicit insertion admission. The first legacy run MUST reproduce the
DR0056 adopted headline451/.880859/411.738214, zero refusals/illegal elites,
before any operative run. No historical evidence is overwritten.

AND gates: exact completed budget on EVERY run; zero candidate failures,
refusals and illegal elites on EVERY seed; current unchanged source hashes;
actual operative counter consistency; elapsed <= existing1200s/run bound.
Mean coverage and QD costs may not exceed the corresponding fresh legacy
three-seed max-min spread. Costs and spreads are rounded6dp BEFORE judgment,
as the published DR0052 comparison; zero spread permits zero cost only.
No seed, threshold, refusal classification or workload changes after outcomes.
A failure REFUSES the product route; no rescue or survivor-only comparison.

This independent necessary gate runs before the runtime permission carrier by
integration authorization. Passing it DOES NOT qualify damage/repair inheritance,
Workshop/hatch/campaign exposure or change the legacy default. Actual pre-selection
attempts, refusals, accepted operation deltas and net phenotype copies are distinct.
"""

# PRE-MEASUREMENT CORRECTION, 2026-10-06 (initial draft retained above):
# The initial rounded-before-judgment sentence was incorrect. DR0052 compares
# unrounded mean cost to its control. X6's exact zero allowance is authoritative.
# Compare Decimal sums of published per-seed metrics to 3 * Decimal spread;
# division/rounding occurs only for display. A one-seed 1e-6 cost cannot disappear.
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal
import gzip
import hashlib
import importlib
import json
import math
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
for relative in ('labs/map_elites_archive','labs/grid_genome','labs/readability_benchmark',
                 'labs/lifecycle_sim','labs/wfc_grid','packages/mecha_engine/src'):
    path = str(ROOT/relative)
    if path not in sys.path: sys.path.insert(0,path)

from evaluation_loop_scale import run_evaluation_loop, PRE_REGISTERED_BOUND_S, _load_default_slip
from mecha_engine.genome import validate_grid
from mecha_engine.slip import is_grid_aligned
importlib.import_module('mecha_engine.generation._operative_permissions')

ARM = 'operative_permissions_v1'
SEEDS = (20260709,21260712,22260715)
PROTOCOL = dict(population=256,target_evaluations=20480,lifecycle_ticks=24,
                selection='novelty_first',pool_factor=3,generation='constrained',slip_admission='insertion')
ARTIFACT_ID = 'operative_evolution_stage0'
STAGE0 = 'data/grid_genome/operative_mutation_stage0.json'
BASELINE = 'data/archives/adopted_default_restatement_stage0.json'
DEFAULT_STUDY = 'data/archives/slip_admission_default_stage0.json'
INPUT_FILES = (STAGE0,BASELINE,DEFAULT_STUDY,'data/archives/niche_scale_archive_stage0.json',
               'data/slips/valid/slip_lcd_seed.json')
RULE = ('Exact Decimal mean costs <= fresh legacy three-seed spread; compare sums against3*spread, '
        'round display only. Exact zero structural failures, identical completed20480budget per run, '
        'unchanged source/input hashes and <=1200seconds per run. AND gates; no product promotion.')
CORRECTION = dict(date='2026-10-06',before_any_measurement=True,
    initial_draft='Costs and spreads rounded6dp before judgment, incorrectly attributed to DR0052.',
    corrected='Exact Decimal sum comparisons on published per-seed metrics; only display values round. '
              'One-seed1e-6 loss under zero spread REFUSES. No threshold or seed changed.')


def encoded(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def digest(value): return hashlib.sha256(encoded(value)).hexdigest()


def file_hash(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path): return json.loads(path.read_text(encoding='utf-8'))


def write_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def source_hashes():
    # Conservative inventory: every relevant lab/package source, including lazy
    # corpus_builder -> invariant_scaling imports, is bound before execution.
    paths = {Path(__file__).resolve(),*(ROOT/name for name in INPUT_FILES)}
    for directory in ('labs', 'packages/mecha_engine/src'):
        paths.update(path for path in (ROOT/directory).rglob('*.py')
                     if not path.name.startswith('test_'))
    return {path.relative_to(ROOT).as_posix():file_hash(path) for path in sorted(paths) if path.is_file()}


def rehash(paths): return {name:file_hash(ROOT/name) for name in paths}


def stage0_qualification():
    artifact=read_json(ROOT/STAGE0)
    checks=artifact['metrics']['checks']
    receipt=artifact['metrics']['g1']
    reviewed=receipt['evidence']['source_sha256']
    matches={name:(ROOT/name).is_file() and file_hash(ROOT/name)==expected for name,expected in reviewed.items()}
    return dict(passed=artifact['decision']['verdict']=='STAGED_PASS' and all(value is True for value in checks.values())
                and receipt['binding']['passed'] and all(matches.values()),source=STAGE0,sha256=file_hash(ROOT/STAGE0),
                source_review_matches=matches,checks=checks,
                limitation='Candidate gates only; permission carrier and product consumers remain unqualified.')


def reproduce_headline(actual,expected):
    fields=dict(rng_seed=expected['rng_seed'],occupied_niches=expected['adopted_occupied'],
                coverage=expected['adopted_coverage'],qd_score=expected['adopted_qd'],
                refusals=expected['adopted_refusals'],slip_illegal_elites=expected['adopted_illegal_elites'])
    differences={name:dict(expected=value,actual=actual.get(name)) for name,value in fields.items() if actual.get(name)!=value}
    complete=(actual.get('arm')=='legacy' and actual.get('status')=='returned' and actual.get('sources_unchanged') is True
              and actual.get('configuration')==PROTOCOL and actual.get('evaluations_total')==PROTOCOL['target_evaluations']
              and actual.get('candidate_failures')==0 and actual.get('invalid_elites')==0)
    return dict(passed=not differences and complete,expected=fields,actual={name:actual.get(name) for name in fields},
                different_metrics=differences,complete_valid_source_stable=complete)


def operator_observation_qualified(observed,attempts,refusals):
    if not isinstance(observed,dict): return False
    zero=('candidate_failures','inherited_rate_mismatches','protected_payload_mismatches','unknown_parent_outputs',
          'invalid_outputs','unaligned_outputs','missing_operator_trace','trace_counter_mismatches')
    try:
        returned=observed['candidate_returned']
        return (observed['status']=='complete' and observed['stop_reason'] is None
            and all(observed[name]==0 for name in zero)
            and observed['candidate_generation_attempts']==attempts
            and returned+observed['candidate_failures']==attempts
            and len(observed['failure_records'])==refusals==observed['candidate_failures']
            and observed['net_phenotype_changed']+observed['parent_copies']==returned
            and observed['inherited_rate_matches']==observed['protected_payload_matches']==returned
            and observed['accepted_operations']+observed['rejected_proposals']==observed['proposal_attempts']
            and observed['proposal_attempts']<=observed['operator_opportunities']
            and sum(observed['operation_counts'].values())==observed['accepted_operations']
            and sum(observed['outcome_counts'].values())==observed['operator_opportunities'])
    except (KeyError,TypeError): return False


def summarize_run(result,*,arm,seed,elapsed):
    summary=result['archive_summary']
    elites=result['elite_grid_collection']['elites']
    profile=_load_default_slip()
    refusals=result['refusal_collection']
    observed=deepcopy(result.get('operator_observation'))
    attempts=refusals['generation_attempts_total']
    failure_count=sum(row['collapse_failures'] for row in result['trajectory'])
    return dict(arm=arm,rng_seed=seed,status='returned',configuration=deepcopy(PROTOCOL),
        occupied_niches=summary['occupied_niches'],coverage=summary['coverage'],qd_score=summary['qd_score'],
        best_fitness=summary['best_fitness'],evaluations_total=result['evaluations_total'],
        generations_run=len(result['trajectory']),candidate_generation_attempts=attempts,
        candidate_failures=failure_count,refusals=len(refusals['records']),
        refusal_records=deepcopy(refusals['records']),
        slip_illegal_elites=sum(not is_grid_aligned(row['grid'],profile).ok for row in elites),
        invalid_elites=sum(not validate_grid(row['grid']).ok for row in elites),
        elite_origin_counts={name:sum(row['origin']==name for row in elites) for name in ('bootstrap','loop_offspring')},
        elapsed_seconds=elapsed,operator_observation=observed,
        operator_counters_qualified=(operator_observation_qualified(observed,attempts,len(refusals['records'])) if arm==ARM else failure_count==len(refusals['records'])),
        full_result_sha256=digest(result),
        phenotype_measurement='loop _operative_phenotype: cell/organ/palette/grid_size excluding rates,locks,weights,identity,lineage,trace; stress/damage remain actual payload')


def _finite(value): return type(value) in (float,int) and math.isfinite(value)


def judge_evolution(runs,*,instrument,current_sources):
    expected={(arm,seed) for arm in ('legacy',ARM) for seed in SEEDS}
    pairs=[(row.get('arm'),row.get('rng_seed')) for row in runs]
    complete=len(pairs)==len(expected) and set(pairs)==expected
    checks=dict(instrument_reproduced=instrument.get('passed') is True,
        declared_six_runs=complete,
        exact_protocol=complete and all(row.get('configuration')==PROTOCOL for row in runs),
        all_returned=complete and all(row.get('status')=='returned' for row in runs),
        complete_budget=complete and all(row.get('evaluations_total')==PROTOCOL['target_evaluations'] for row in runs),
        zero_candidate_failures=complete and all(row.get('candidate_failures')==0 and row.get('refusals')==0 for row in runs),
        legal_valid_elites=complete and all(row.get('slip_illegal_elites')==0 and row.get('invalid_elites')==0 for row in runs),
        source_stable=complete and bool(current_sources) and all(
            row.get('sources_unchanged') is True and row.get('source_sha256_before')==current_sources
            and row.get('source_sha256_after')==current_sources for row in runs),
        within_existing_runtime_bound=complete and all(_finite(row.get('elapsed_seconds')) and row['elapsed_seconds']<=PRE_REGISTERED_BOUND_S for row in runs),
        operative_counters=complete and all(row.get('operator_counters_qualified') is True for row in runs))
    controls={}
    for metric,label in (('coverage','coverage'),('qd_score','quality')):
        valid=complete and all(_finite(row.get(metric)) for row in runs)
        if valid:
            legacy=[Decimal(str(row[metric])) for row in runs if row['arm']=='legacy']
            operative=[Decimal(str(row[metric])) for row in runs if row['arm']==ARM]
            spread=max(legacy)-min(legacy)
            cost_total=max(Decimal(0),sum(legacy)-sum(operative))
            passes=cost_total<=spread*len(SEEDS)
            controls.update({label+'_cost':round(float(cost_total/len(SEEDS)),6),label+'_spread':round(float(spread),6),
                label+'_cost_exact_numerator':str(cost_total),label+'_cost_exact_denominator':len(SEEDS),
                label+'_spread_exact':str(spread),label+'_legacy_mean':round(float(sum(legacy)/len(SEEDS)),6),
                label+'_operative_mean':round(float(sum(operative)/len(SEEDS)),6)})
        else:
            controls.update({label+'_cost':None,label+'_spread':None})
            passes=False
        checks[label+'_preserved']=passes
    failed=sorted(name for name,passed in checks.items() if not passed)
    return dict(verdict='REFUSE' if failed else 'STAGED_PASS',checks=checks,failed_checks=failed,controls=controls,
                rule=RULE,consumer_promotion=False,legacy_default_unchanged=True)


def run_one(arm,seed,directory,*,expected_sources=None):
    label=f'{arm}-{seed}'
    path=directory/(label+'.json')
    if path.exists(): raise ValueError(f'Refusing to overwrite retained run {path.name}')
    before=source_hashes()
    if expected_sources is not None and before!=expected_sources:
        raise ValueError('Source/input snapshot changed between runs; refusing mixed-source comparison.')
    write_json(directory/'active.json',dict(arm=arm,seed=seed,status='running',started=datetime.now(timezone.utc).isoformat(),source_sha256=before))
    print(f'RUN {arm} {seed}: population256 target20480 ticks24 insertion',flush=True)
    started=time.perf_counter()
    try:
        raw=run_evaluation_loop(**PROTOCOL,rng_seed=seed,mutation_arm=arm,collect_refusals=True,collect_elite_grids=True)
        elapsed=time.perf_counter()-started
        row=summarize_run(raw,arm=arm,seed=seed,elapsed=elapsed)
        raw_bytes=encoded(raw)
        raw_path=directory/(label+'.result.json.gz')
        raw_path.write_bytes(gzip.compress(raw_bytes,mtime=0))
        row['raw_result']=dict(path=raw_path.relative_to(ROOT).as_posix(),sha256=file_hash(raw_path),
            uncompressed_sha256=hashlib.sha256(raw_bytes).hexdigest(),uncompressed_bytes=len(raw_bytes),compressed_bytes=raw_path.stat().st_size)
    except Exception as error:
        row=dict(arm=arm,rng_seed=seed,status='exception',configuration=deepcopy(PROTOCOL),
                 elapsed_seconds=time.perf_counter()-started,exception_type=type(error).__name__,error=str(error))
    after=source_hashes()
    row.update(source_sha256_before=before,source_sha256_after=after,sources_unchanged=before==after)
    write_json(path,row)
    write_json(directory/'active.json',dict(status='completed',last_run=path.relative_to(ROOT).as_posix(),active_process=False))
    print(json.dumps({key:row.get(key) for key in ('arm','rng_seed','status','coverage','qd_score','evaluations_total',
        'candidate_failures','refusals','slip_illegal_elites','elapsed_seconds','sources_unchanged')},sort_keys=True),flush=True)
    return row


def load_run(path):
    row=read_json(path)
    if row['source_sha256_before']!=row['source_sha256_after'] or source_hashes()!=row['source_sha256_after']:
        raise ValueError(f'Saved run source differs: {path.name}')
    if row.get('raw_result'):
        raw=row['raw_result'];data=(ROOT/raw['path']).read_bytes()
        if hashlib.sha256(data).hexdigest()!=raw['sha256'] or hashlib.sha256(gzip.decompress(data)).hexdigest()!=raw['uncompressed_sha256']:
            raise ValueError(f'Saved raw run differs: {path.name}')
    return row


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--instrument-only',action='store_true')
    parser.add_argument('--finish',action='store_true')
    parser.add_argument('--directory',type=Path,default=ROOT/'.development/x6/evolution-science/runs')
    parser.add_argument('--output',type=Path,default=ROOT/'data/archives/operative_evolution_stage0.json')
    args=parser.parse_args()
    if args.instrument_only==args.finish: raise ValueError('Choose exactly one of --instrument-only or --finish.')
    prerequisite=stage0_qualification()
    if not prerequisite['passed']: raise ValueError('G0-G3 candidate qualification is missing or stale.')
    parameters=read_json(ROOT/DEFAULT_STUDY)['parameters']
    if (tuple(parameters['seeds'])!=SEEDS or any(parameters[name]!=PROTOCOL[name] for name in ('population','target_evaluations','lifecycle_ticks'))):
        raise ValueError('DR0052 protocol source disagrees with preregistered fixed protocol.')
    args.directory.mkdir(parents=True,exist_ok=True)
    head=read_json(ROOT/BASELINE)['metrics']['headline']
    first_path=args.directory/f'legacy-{SEEDS[0]}.json'
    if args.instrument_only:
        first=run_one('legacy',SEEDS[0],args.directory)
        instrument=reproduce_headline(first,head)
        instrument.update(source=BASELINE,source_sha256=file_hash(ROOT/BASELINE),prerequisite=prerequisite)
        write_json(args.directory.parent/'instrument.json',instrument)
        print(json.dumps(instrument,indent=2),flush=True)
        return 0 if instrument['passed'] else 1
    instrument_path=args.directory.parent/'instrument.json'
    instrument=read_json(instrument_path)
    first=load_run(first_path)
    if not instrument['passed'] or not reproduce_headline(first,head)['passed']:
        raise ValueError('First legacy instrument did not reproduce; challengers are not authorized.')
    runs=[first]
    for arm in ('legacy',ARM):
        for seed in SEEDS:
            if arm=='legacy' and seed==SEEDS[0]: continue
            path=args.directory/f'{arm}-{seed}.json'
            runs.append(load_run(path) if path.exists() else run_one(arm,seed,args.directory,
                expected_sources=first['source_sha256_before']))
    final_sources=source_hashes()
    verdict=judge_evolution(runs,instrument=instrument,current_sources=final_sources)
    report=dict(artifact_id=ARTIFACT_ID,date='2026-10-06',status='measured',
        purpose='Conditional paired evolution qualification for explicit operative permissions; legacy default and historical evidence retained.',
        source_artifacts=list(INPUT_FILES),parameters={**PROTOCOL,'seeds':list(SEEDS),'arms':['legacy',ARM],
            'existing_bound_seconds_per_run':PRE_REGISTERED_BOUND_S,'fresh_runs':6,
            'measurement_order':'first legacy instrument, remaining legacy seeds, then three operative seeds',
            'runtime_carrier_gate_order':'independent evolution condition measured first by integration authorization; carrier remains unqualified'},
        pre_measurement_correction=CORRECTION,prerequisite=prerequisite,
        metrics=dict(instrument=instrument,runs=runs,judgment=verdict,
            final_source_sha256=final_sources,
            source_inventory_policy='all non-test Python in labs and packages/mecha_engine/src plus declared data inputs; full inventory before/after each run and at final judgment'),
        closed_states=[name for name,value in verdict['checks'].items() if value],
        blocked_states=verdict['failed_checks']+['runtime_damage_repair_permission_carrier_unqualified','product_consumers_unqualified','full_local_sweep_pending'],
        decision=verdict,next_research_step=('Retain REFUSE; no product promotion or rescue run. A new preregistered operator study is the reopener.'
                                           if verdict['verdict']=='REFUSE' else 'Qualify inherited permission carrier through actual damage/repair before any product exposure.'))
    write_json(args.output,report)
    print(json.dumps(verdict,indent=2),flush=True)
    return 0


if __name__=='__main__': raise SystemExit(main())
