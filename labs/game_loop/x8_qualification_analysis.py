"""Read-only X8 aggregates, executed under the shared measurement coordinator."""
from pathlib import Path
import argparse, hashlib, json, sys, time
ROOT=Path(__file__).resolve().parents[2]
for relative in ('labs/runtime_integration','labs/cubff_transducer'):
    sys.path.insert(0,str(ROOT/relative))
import survival_population_gate as population
import x8_role_weather_qualification as effects

def read(path):return json.loads(path.read_bytes())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def trial_path(study,index,plan):
    return study/'trials'/f"{index:02d}-{plan['stage']}-{plan['backend']}-{plan['arm']}-{plan['seed']}"
def load_effect(study,kind,index,source_manifest,inputs_digest):
    path=study/kind/f'{index:02d}'
    start=read(path/'worker-start.json');terminal=read(path/'worker-finish.json')
    if (start['kind']!=kind or start['case_index']!=index or start['inputs_sha256']!=inputs_digest
            or start['source_manifest_sha256']!=sha(source_manifest)
            or terminal['source_manifest_sha256']!=sha(source_manifest)
            or terminal['status']!='completed' or not 0<=terminal['elapsed_seconds']<=120
            or terminal['result_sha256']!=sha(path/'result.json')):
        raise ValueError('effect receipt does not bind requested case')
    return read(path/'result.json')

def analyze(stage,study):
    manifest=study/'source-manifest.json';input_path=study/'setup/inputs.json'
    sources=population.source_snapshot(manifest);inputs=read(input_path);inputs_digest=sha(input_path)
    if inputs['source_sha256']!=sources or inputs['source_manifest_sha256']!=sha(manifest):
        raise ValueError('frozen input/source mismatch')
    if stage in ('parity','cohort'):
        plans=population.case_plan()[:16] if stage=='parity' else population.case_plan()
        trials=[population.load_trial(trial_path(study,i,p),inputs_digest,sources,inputs) for i,p in enumerate(plans)]
        if [trial['plan'] for trial in trials]!=plans:
            raise ValueError('ordered loaded trial plans differ from requested stage')
        if stage=='parity':
            checks={f"{trials[i]['plan']['arm']}-{trials[i]['plan']['seed']}":trials[i]['result']==trials[i+1]['result'] for i in range(0,16,2)}
            result=dict(format='x8_parity_judgment_v1',checks=checks,verdict='MATCH' if all(checks.values()) else 'REFUSE',projection=[])
        else:
            result=population.judge(trials)
        result['trial_terminal_sha256']=[sha(trial_path(study,i,p)/'terminal.json') for i,p in enumerate(plans)]
    elif stage=='roles':
        results=[load_effect(study,'role',i,manifest,inputs_digest) for i in range(31)]
        result=effects.summarize_roles(results,inputs)
    else:
        results=[load_effect(study,'weather',i,manifest,inputs_digest) for i in range(21)]
        result=effects.summarize_weather(results,inputs)
        reference=load_effect(study,'density-reference',0,manifest,inputs_digest)
        result['density_reference_verdict']=reference['verdict']
        if reference['verdict']!='MATCH':result['verdict']='REFUSE'
    if population.source_snapshot(manifest)!=sources or sha(input_path)!=inputs_digest:
        raise ValueError('source/input drift during aggregate')
    result['inputs_sha256']=inputs_digest;result['source_manifest_sha256']=sha(manifest)
    return result

def main():
    started=time.perf_counter();parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage',required=True,choices=('parity','cohort','roles','weather'))
    parser.add_argument('--study',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    result=analyze(args.stage,args.study);result['elapsed_seconds']=time.perf_counter()-started
    (args.output/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k in ('verdict','cohort_verdict','product_qualification','elapsed_seconds')}))
    if args.stage=='parity' and result['verdict']!='MATCH':return 1
    return 0
if __name__=='__main__':raise SystemExit(main())
