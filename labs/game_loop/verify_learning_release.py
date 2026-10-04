"""R2 real source/CLI/native launches with isolated saves, including a warm life."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
for relative in ("game/src","packages/mecha_engine/src"):
    sys.path.insert(0,str(ROOT/relative))
from mecha_game.session import CompanionSession, load_session_inputs


def verify(bundle):
    executable=bundle/('Mechagotchi.exe' if os.name=='nt' else 'Mechagotchi')
    if not executable.is_file(): raise FileNotFoundError(executable)
    env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',PYTHONDONTWRITEBYTECODE='1',
        PYTHONPATH=os.pathsep.join(str(ROOT/p) for p in ('tools/mechas_cli/src','game/src','packages/mecha_engine/src')))
    runs=[]
    checks={}
    with tempfile.TemporaryDirectory(prefix='mechagotchi-learning-') as directory:
        temporary=Path(directory)
        def launch(label,base,keeper,*args,expected=0):
            command=[*base,'--keeper-dir',str(keeper),*args]
            result=subprocess.run(command,cwd=temporary,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',
                timeout=120,**({'creationflags':subprocess.CREATE_NO_WINDOW} if os.name=='nt' else {}))
            runs.append(dict(label=label,returncode=result.returncode,expected=expected,command=command,stderr=result.stderr))
            if result.returncode != expected: raise AssertionError(runs[-1])
            path=keeper/'companion.json'
            return json.loads(path.read_text(encoding='utf-8')) if path.exists() else None
        def inventory(keeper):
            return {str(p.relative_to(keeper)):hashlib.sha256(p.read_bytes()).hexdigest() for p in keeper.rglob('*') if p.is_file()}
        fast=['--tick-frames','1','--fps','0','--scale','2']
        paths=(('source',[sys.executable,'-B',str(ROOT/'game/run_game.py'),*fast]),
               ('cli',[sys.executable,'-B','-m','mechas_cli.app','game','--play']),
               ('native',[str(executable),*fast]))
        for label,base in paths:
            keeper=temporary/label
            fresh=launch(label+'-new',base,keeper,'--new','--learning-policy','qtable','--ticks','2')
            resumed=launch(label+'-resume',base,keeper,'--ticks','2')
            checks[label+'_new_and_resume']=(fresh['learning_policy']==resumed['learning_policy']=='qtable'
                and fresh['state']['age_ticks']==2 and resumed['state']['age_ticks']==4
                and fresh['grid']['grid_id']==resumed['grid']['grid_id'] and bool(resumed['state']['thread_states']['qtable_policy']['q']))
            before=inventory(keeper)
            launch(label+'-conflict',base,keeper,'--learning-policy','incumbent','--ticks','1',expected=2)
            checks[label+'_conflict_preserves_all_save_bytes']=before==inventory(keeper)
            launch(label+'-invalid',base,keeper,'--learning-policy','unknown','--ticks','1',expected=2)
            checks[label+'_invalid_preserves_all_save_bytes']=before==inventory(keeper)
        keeper=temporary/'native'
        native=paths[-1][1]
        fresh=launch('native-incumbent',native,keeper,'--new','--learning-policy','incumbent','--ticks','2')
        checks['incumbent_default_shape']='learning_policy' not in fresh and 'qtable_policy' not in fresh['state']['thread_states']
        child=launch('native-succession',native,keeper,'--new','--learning-policy','qtable','--auto-succeed','--ticks','14')
        checks['native_succession']=len(child['lineage'])>=2 and all(r.get('learning_policy')=='qtable' for r in child['lineage']) and child['state']['age_ticks']<14
        grid,slip,model=load_session_inputs(ROOT/'data/seed_grids_16x16/mg_seed16_001_beetle.json',ROOT/'data/slips/valid/slip_v2_cleanliness.json')
        warm=CompanionSession(grid,slip,model=model,learning_policy='qtable')
        for _ in range(160):
            state=warm.state
            care='feed' if state['hunger']>.55 else 'sleep' if state['energy']<.35 else 'clean' if state['cleanliness']<.6 else None
            warm.advance(care)
        keeper=temporary/'warm'
        warm.save(keeper/'companion.json')
        samples=sum(row['n'] for row in warm.state['thread_states']['qtable_policy']['q'].values())
        continued=launch('native-warm-resume',native,keeper,'--ticks','1')
        checks['warm_state_survives_native_resume']=(continued['state']['age_ticks']==161 and continued['learning_policy']=='qtable'
            and sum(row['n'] for row in continued['state']['thread_states']['qtable_policy']['q'].values())==samples+1)
        payload=dict(continued,learning_policy='broken')
        (keeper/'companion.json').write_text(json.dumps(payload),encoding='utf-8')
        before=inventory(keeper)
        launch('native-corrupt-save',native,keeper,'--ticks','1',expected=2)
        checks['corrupt_save_refused_without_writes']=before==inventory(keeper)
    return {'artifact_id':'playable_learning_release_stage0','date':'2026-10-04','status':'observed_native_windows_and_source',
        'purpose':'Observe the implemented opt-in through actual launchers, warm save continuity and native succession.',
        'source_artifacts':['game/src/mecha_game/app.py','game/src/mecha_game/session.py','labs/game_loop/verify_learning_release.py'],
        'metrics':{'checks':checks,'runs':runs,'native_executable_sha256':hashlib.sha256(executable.read_bytes()).hexdigest()},
        'closed_states':[key for key,value in checks.items() if value],
        'blocked_states':['default adoption awaits R3','remote CI and signing unverified'],
        'decision':{'verdict':'verified' if all(checks.values()) else 'withhold'},
        'next_research_step':'R3 actual-game paired default adoption comparison.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    report=verify(args.bundle.resolve())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'checks':report['metrics']['checks'],'launches':len(report['metrics']['runs'])},indent=2))
    raise SystemExit(0 if report['decision']['verdict']=='verified' else 1)
