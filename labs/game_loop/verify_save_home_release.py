"""R4 native default save-home observations; no real user home is touched."""
import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path


def verify(bundle):
    executable=bundle/"Mechagotchi.exe"
    legacy=bundle/"_internal/keeper"
    if legacy.exists():
        raise ValueError("Use a fresh verification bundle; an existing legacy directory must be preserved.")
    checks={};runs=[]
    def inventory(path):
        return {str(p.relative_to(path)):hashlib.sha256(p.read_bytes()).hexdigest() for p in path.rglob('*') if p.is_file()}
    try:
        with tempfile.TemporaryDirectory(prefix='mechagotchi-native-home-') as temporary:
            root=Path(temporary)
            home=root/'user'
            home.mkdir()
            def launch(label,profile,*args):
                # Windows Path.home resolves USERPROFILE. This only affects the
                # observed child, not the operator's environment or configuration.
                env=dict(os.environ,USERPROFILE=str(profile),SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
                command=[str(executable),'--tick-frames','1','--fps','0','--scale','2',*args]
                result=subprocess.run(command,cwd=root,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',
                    timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
                runs.append(dict(label=label,returncode=result.returncode,command=command,stderr=result.stderr))
                if result.returncode: raise AssertionError(runs[-1])
            def saved(path): return json.loads((path/'companion.json').read_text(encoding='utf-8'))
            launch('fresh-user-home',home,'--ticks','2','--learning-policy','qtable')
            destination=home/'.mechagotchi'
            fresh=saved(destination)
            checks['new_native_save_uses_user_home']=fresh['state']['age_ticks']==2 and not legacy.exists()
            launch('resume-user-home',home,'--ticks','1')
            checks['user_home_resume']=saved(destination)['state']['age_ticks']==3 and saved(destination)['learning_policy']=='qtable'
            old_user=root/'legacy-user'
            old_user.mkdir()
            launch('create-isolated-legacy-fixture',old_user,'--keeper-dir',str(legacy),'--ticks','2')
            launch('resume-legacy-default',old_user,'--ticks','1')
            checks['legacy_continues_in_place']=saved(legacy)['state']['age_ticks']==3 and not (old_user/'.mechagotchi').exists()
            before=inventory(legacy)
            launch('both-save-homes',home,'--ticks','1')
            checks['existing_user_home_wins_without_touching_legacy']=saved(destination)['state']['age_ticks']==4 and before==inventory(legacy)
            home_before=inventory(destination)
            explicit=root/'explicit'
            launch('explicit-directory',home,'--keeper-dir',str(explicit),'--ticks','2')
            checks['explicit_directory_wins']=saved(explicit)['state']['age_ticks']==2 and home_before==inventory(destination) and before==inventory(legacy)
    finally:
        # Only remove the fixture files we created under this new bundle.
        # Unknown concurrent files are preserved, never recursively deleted.
        if legacy.exists():
            if not legacy.resolve().is_relative_to(bundle.resolve()):
                raise ValueError('Legacy fixture escaped the verified bundle')
            for name in ('companion.json','companion.bak.json','lineage.json','lineage.bak.json'):
                (legacy/name).unlink(missing_ok=True)
            if not any(legacy.iterdir()): legacy.rmdir()
    return dict(artifact_id='native_save_home_stage0',date='2026-10-04',status='native_windows_observed',
        purpose='New frozen saves belong to the user; existing bundled companions continue without migration.',
        source_artifacts=['game/src/mecha_game/app.py','labs/game_loop/verify_save_home_release.py'],
        metrics=dict(checks=checks,runs=runs,native_executable_sha256=hashlib.sha256(executable.read_bytes()).hexdigest()),
        closed_states=[key for key,value in checks.items() if value],blocked_states=['remote CI/signing unverified'],
        decision=dict(verdict='verified' if all(checks.values()) else 'withhold'),
        next_research_step='Consolidate Cycle 28, retain incumbent default and experimental opt-in.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    report=verify(args.bundle.resolve())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report['metrics']['checks'],indent=2))
    raise SystemExit(0 if report['decision']['verdict']=='verified' else 1)
