"""Pure, additive validation recovery for the retained production-01 result.

Never runs a life, advances a tick, evolves a population, or alters old evidence.
The original failed observation check and worker status remain authoritative
historical facts. This attestation establishes corrected observation binding only.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
FORMAT='body_workload_observation_recovery_v1'
CONTRACT='docs/development/cycle-38-body-workload-observation-repair.md'
ATTEMPT='.development/body-workload/attempt-02'
ORIGINAL_OUTPUT=ATTEMPT+'/study/production-01/output'
ORIGINAL_CONTROL=ATTEMPT+'/coordinator/receipts/production-01'
OLD_SOURCE_SHA='43e8d9e9de2b337889abe1a6502e48ab450deb4a06f6dc983f6f10460ec85ca0'
OLD_INPUT_SHA='d2e7e0ee5518f734632499370f54529abe2db2a9c4474dae8969eeec984374bf'
OLD_PREREQUISITE_SHA='ef58cd3001c3fa2b1f35460088a8d68f3885cf6723ab87e3916e54466eac426c'
OLD_RESULT_SHA='3bed87dc3de5f0ee2b02b889d24f461478f6286e86219439ad43d0c85c35eac0'
PINNED_FILES={
    ATTEMPT+'/source-manifest.json':OLD_SOURCE_SHA,
    ATTEMPT+'/study/setup/output/inputs.json':OLD_INPUT_SHA,
    ATTEMPT+'/prerequisites.json':OLD_PREREQUISITE_SHA,
    ATTEMPT+'/budget.json':'a5913a271cc1c49c1af91b8bfa4e742b98b4a70c810011d86b8a06af9d78c24a',
    ORIGINAL_OUTPUT+'/result.json':OLD_RESULT_SHA,
    ORIGINAL_OUTPUT+'/started.json':'26d2e9cd2899fce7483138336f7a7eba25737cc69f30a98c5271660d5b3d537c',
    ORIGINAL_OUTPUT+'/terminal.json':'a59431a5b926804d4ba8fc7736ee961553549627bc10cade08f53fdd64d6ca3a',
    ORIGINAL_CONTROL+'/started.json':'65ff0ccc0c3ac8ad790140a1460c0a5b2fdfeba8b2932a94fa5a4f8150cf4117',
    ORIGINAL_CONTROL+'/terminal.json':'86d5f42234ba136f189cef749c7e3e9a858529795cefa198d5af59742ab3a7c1',
}
ALLOWED_ORIGINAL_INSTRUMENT_CHANGES=frozenset((
    'labs/game_loop/body_workload_coordinator.py', 'labs/game_loop/test_body_workload_coordinator.py',
    'labs/game_loop/verify_body_workload_delivery.py', 'labs/game_loop/test_verify_body_workload_delivery.py'))
CHECK_NAMES=frozenset(('well_formed','row_count','row_identity','run_seed','candidate_id','parent_id',
    'cycle_report','damage_seed','removed_count','cycle_episode_consistent','final_episode_consistent',
    'candidate_hash','final_hash','final_presence','final_digest_bound','model_identity',
    'cycle_body_binding','final_body_binding','score_body_binding'))


def imports():
    for name in ('packages/mecha_engine/src','labs/runtime_integration','labs/game_loop'):
        path=str(ROOT/name)
        if path not in sys.path:sys.path.insert(0,path)


def read(path):return json.loads(Path(path).read_bytes())
def file_digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def encode(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as stream:stream.write(encode(value))


def _body_bound(value,grid,history,slip_profile,model,*,require_grid):
    if value is None:return history is None
    if value.get('body_response','legacy')!=model:return False
    active_fields=('body_response','body_workload','evaluated_grid')
    if model=='legacy':
        return not any(k in value for k in active_fields) and not any(
            any(k in row for k in ('body_response','play_energy_cost','action_energy_effect')) for row in (history or []))
    from mecha_engine.lifecycle import initial_state
    from mecha_engine.lifecycle.simulate import ACTION_EFFECTS
    expected=initial_state(grid,slip_profile,body_response=model)['body_workload']
    if value.get('body_workload')!=expected:return False
    if (require_grid or 'evaluated_grid' in value) and value.get('evaluated_grid')!=grid:return False
    for row in history or []:
        action=row['action']
        if action=='play':effect=-expected['play_energy_cost']
        elif action in ACTION_EFFECTS:effect=ACTION_EFFECTS[action]['energy']
        elif action=='clean' and slip_profile.get('mechanics',{}).get('cleanliness') is True:effect=0.0
        else:return False
        if (row.get('body_response')!=model or row.get('play_energy_cost')!=expected['play_energy_cost']
                or row.get('action_energy_effect')!=effect):return False
    return True


def observation_checks(result,slip_profile):
    """Preserve every original predicate and bind active bodies, without replay."""
    imports()
    from survival_population_gate import episode_consistent
    from mecha_engine.runtime.care import care_grid_sha256
    from mecha_engine.runtime._survival_live import _episode_digest,evaluation_grid
    checks={name:True for name in CHECK_NAMES};counts=Counter()
    def check(name,value):
        checks[name]=checks[name] and bool(value);counts[name]+=1
    try:
        report=result['report'];observations=result['evaluations'];ticks=report['ticks']
        model=report.get('body_response','legacy');regime=report['survival_regime']
        check('model_identity',model in ('legacy','workload-v1') and not (model=='legacy' and 'body_response' in report))
        if not checks['model_identity'] or regime not in ('sheltered','stress_probe'):raise ValueError('unsupported model/regime')
        creatures=[(g['generation'],i,c) for g in report['generations'] for i,c in enumerate(g['creatures'])]
        check('row_count',len(creatures)==len(observations))
        for (generation,index,creature),row in zip(creatures,observations):
            check('row_identity',(row['generation_index'],row['candidate_index'],row['creature'])==(generation,index,creature))
            check('run_seed',row['run_seed']==report['rng_seed']+generation*100000+index)
            check('candidate_id',row['candidate_grid']['grid_id']==creature['candidate_grid_id'])
            check('parent_id',row['parent_grid']['grid_id']==creature['parent_grid_id'])
            stripped=[{k:v for k,v in c.items() if k not in ('frames','damage_seed')} for c in row['cycles']]
            check('cycle_report',stripped==creature['cycles'])
            for cycle in row['cycles']:
                check('damage_seed',cycle['damage_seed']==row['run_seed']*10+cycle['cycle'])
                check('removed_count',len(cycle['frames']['removed_cells'])==cycle['removed_cell_count'])
                episode=cycle['episode'];history=cycle['frames']['episode_history']
                check('cycle_episode_consistent',episode_consistent(episode,history,ticks))
                grid,_=evaluation_grid(cycle['frames']['repaired_grid'],regime)
                check('cycle_body_binding',_body_bound(episode,grid,history,slip_profile,model,require_grid=True))
            final=row['final_episode'];history=final['history'] if final is not None else None
            check('final_episode_consistent',episode_consistent(final,history,ticks))
            grid,_=evaluation_grid(row['final_grid'],regime)
            check('final_body_binding',_body_bound(final,grid,history,slip_profile,model,require_grid=False))
            if 'breeding' in creature:
                b=creature['breeding']
                check('candidate_hash',b['candidate_grid_sha256']==care_grid_sha256(row['candidate_grid']))
                check('final_hash',b['final_grid_sha256']==care_grid_sha256(row['final_grid']))
                check('final_presence',(b['final_episode'] is None)==(final is None))
                if final is not None:
                    check('final_digest_bound',b['final_episode']==_episode_digest(final,ticks,evaluated_grid=grid))
                    check('final_body_binding',_body_bound(b['final_episode'],grid,history,slip_profile,model,require_grid=True))
            score=creature.get('score')
            if score is not None and 'final_episode' in score:
                check('score_body_binding',_body_bound(score['final_episode'],grid,history,slip_profile,model,require_grid=True))
    except (KeyError,TypeError,ValueError,AttributeError,IndexError,OverflowError):
        checks['well_formed']=False
    return {'checks':checks,'counts':dict(counts)}


def observations_bound(result,slip_profile):
    return all(value is True for value in observation_checks(result,slip_profile)['checks'].values())


def unchanged_original_source(old,current):
    return all(current.get('files',{}).get(name)==digest for name,digest in old['files'].items()
               if name not in ALLOWED_ORIGINAL_INSTRUMENT_CHANGES)


def _relative(path):
    path=Path(path).resolve()
    if not path.is_relative_to(ROOT):raise ValueError('recovery path must remain inside repository')
    return path.relative_to(ROOT).as_posix()


def _bound(path):
    path=(ROOT/path).resolve()
    if not path.is_relative_to(ROOT) or path.is_symlink():raise ValueError('invalid evidence path')
    return path


def _original_evidence():
    """Verify the exact failed attempt and its complete output closure."""
    bound=dict(PINNED_FILES)
    for name,expected in bound.items():
        if file_digest(_bound(name))!=expected:raise ValueError('retained evidence changed: '+name)
    worker=read(ROOT/ORIGINAL_OUTPUT/'terminal.json');start=read(ROOT/ORIGINAL_OUTPUT/'started.json')
    control=read(ROOT/ORIGINAL_CONTROL/'terminal.json');control_start=read(ROOT/ORIGINAL_CONTROL/'started.json')
    if (worker['status']!='error' or worker['error']['message']!='production input or observation integrity failed'
            or worker['spec']!={'stage':'production','index':1,'seconds':120}
            or worker['started_sha256']!=bound[ORIGINAL_OUTPUT+'/started.json']
            or worker['spec']!=start['spec'] or worker['elapsed_seconds']>120
            or control['status']!='error' or control['cleanup_confirmed'] is not True
            or control['returncode']!=1 or control['elapsed_seconds']>120
            or control['started_sha256']!=bound[ORIGINAL_CONTROL+'/started.json']
            or control['request']!=control_start['request']):raise ValueError('original failure receipt differs')
    for receipt in (worker,start,control,control_start):
        if receipt['source_manifest_sha256']!=OLD_SOURCE_SHA or receipt['inputs_sha256']!=OLD_INPUT_SHA:
            raise ValueError('original source/input identity differs')
    if worker['prerequisites_sha256']!=OLD_PREREQUISITE_SHA or start['prerequisites_sha256']!=OLD_PREREQUISITE_SHA:
        raise ValueError('original prerequisite identity differs')
    expected_worker={ORIGINAL_OUTPUT+'/'+name:digest for name,digest in worker['outputs'].items()}
    for name,digest in control['outputs'].items():
        if name.startswith('worker/'):target=ORIGINAL_OUTPUT+'/'+name.removeprefix('worker/')
        elif name.startswith('parent/'):target=ORIGINAL_CONTROL+'/'+name.removeprefix('parent/')
        else:raise ValueError('unknown output namespace')
        if target in bound and bound[target]!=digest:raise ValueError('output digest contradiction')
        bound[target]=digest
    if not all(bound.get(name)==digest for name,digest in expected_worker.items()):raise ValueError('worker output closure differs')
    actual={_relative(path) for path in (ROOT/ORIGINAL_OUTPUT).rglob('*') if path.is_file()}
    if actual!={name for name in bound if name.startswith(ORIGINAL_OUTPUT+'/')}:
        raise ValueError('saved output inventory changed')
    for name,expected in bound.items():
        if file_digest(_bound(name))!=expected:raise ValueError('retained output changed: '+name)
    result=read(ROOT/ORIGINAL_OUTPUT/'result.json')
    if (result['checks']!={'input_immutable':True,'observations_bound':False,'body_response_bound':True}
            or {k:result[k] for k in ('era_index','rng_seed','body_response')}
                !={'era_index':1,'rng_seed':20261130,'body_response':'workload-v1'}):raise ValueError('retained original result differs')
    return bound,result


def _build_attestation(source_manifest):
    imports()
    from body_workload_gate import population_observations,source_snapshot
    source_manifest=_bound(_relative(source_manifest));current=read(source_manifest)
    files=source_snapshot(source_manifest)
    required=(CONTRACT,'labs/game_loop/body_workload_observation_recovery.py',
              'labs/game_loop/test_body_workload_observation_recovery.py')
    if not all(name in files for name in required):raise ValueError('corrected source closure incomplete')
    old=read(ROOT/ATTEMPT/'source-manifest.json')
    if not unchanged_original_source(old,current):raise ValueError('original non-allowlisted source changed')
    bound,result=_original_evidence()
    inputs=read(ROOT/ATTEMPT/'study/setup/output/inputs.json')
    validation=observation_checks(result,inputs['production']['slip_profile'])
    if not all(value is True for value in validation['checks'].values()):raise ValueError('corrected observation binding refused')
    observations=population_observations(result)
    if observations!=result['observations']:raise ValueError('recorded observation totals differ')
    # Rehash after validation to exclude changed evidence during the read.
    if any(file_digest(_bound(name))!=digest for name,digest in bound.items()):raise ValueError('evidence changed during validation')
    if source_snapshot(source_manifest)!=files:raise ValueError('source changed during validation')
    attestation=dict(format=FORMAT,status='validated_retained_observation',original_worker_status='error',
        original_observations_bound=False,original_source_manifest_sha256=OLD_SOURCE_SHA,
        original_inputs_sha256=OLD_INPUT_SHA,original_prerequisites_sha256=OLD_PREREQUISITE_SHA,
        original_result_sha256=OLD_RESULT_SHA,source_manifest=_relative(source_manifest),
        source_manifest_sha256=file_digest(source_manifest),
        corrected_validator_sha256=files['labs/game_loop/body_workload_observation_recovery.py'],
        bound_files=bound,validation=validation,observations=observations,
        original_runtime_source_unchanged=True,simulation_executed=False)
    return attestation,result


def recover(output_path,new_source_manifest):
    """Publish a new attestation once, after the integrator freezes the new source."""
    output_path=_bound(_relative(output_path))
    if output_path.is_relative_to(ROOT/ATTEMPT):raise ValueError('cannot publish into retained attempt')
    attestation,_=_build_attestation(new_source_manifest)
    write(output_path,attestation)
    return attestation


def validate_recovery(attestation_path,expected_sha256,new_source_manifest_sha256):
    """Return the original result only after exact attestation/evidence revalidation."""
    if file_digest(attestation_path)!=expected_sha256:raise ValueError('recovery attestation digest differs')
    saved=read(attestation_path)
    if saved.get('source_manifest_sha256')!=new_source_manifest_sha256:raise ValueError('recovery source identity differs')
    expected,result=_build_attestation(_bound(saved['source_manifest']))
    if saved!=expected:raise ValueError('recovery attestation payload differs')
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-manifest',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();recover(args.output,args.source_manifest)


if __name__=='__main__':main()
