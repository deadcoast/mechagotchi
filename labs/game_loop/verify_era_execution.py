"""X5 connected source and relocated native reproduction acceptance.

Creates only new diagnostic fixtures. Source SDL events and actual native
processes are measured separately; neither claims OS keyboard automation.
"""
from __future__ import annotations
import argparse
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for folder in ('', 'game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT / folder))


def read(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def inventory(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in Path(root).rglob('*') if p.is_file()}
def write(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=True, indent=2, allow_nan=False)
        stream.write('\n')
def relative(path): return Path(path).resolve().relative_to(ROOT).as_posix()


def source_acceptance(output):
    from mecha_game.campaign import KeeperCampaign, TINY_ERA_CONFIG, load_campaign_inputs
    from mecha_game.contribute import gather_release_inputs
    from mecha_game.era_plan import EraPlan
    from mecha_game.execution import reproduce_era
    from mecha_game.execution_readout import load_execution_summary, descendant_lines
    from mecha_game.session import CompanionSession, load_session_inputs
    from labs.game_loop.verify_integrated_finish import interact, key, pygame
    output.mkdir(parents=True, exist_ok=False)
    screenshots=output/'screenshots'; screenshots.mkdir()
    originals=output/'original-inputs'; originals.mkdir()
    seed_dir=originals/'seeds'; seed_dir.mkdir()
    for source in sorted((ROOT/'data/seed_grids_16x16').glob('mg_seed16_*.json'))[:12]:
        shutil.copy2(source, seed_dir/source.name)
    slip=originals/'covenant.json'; model=originals/'readability.json'
    shutil.copy2(ROOT/'data/slips/valid/slip_v2_cleanliness.json', slip)
    shutil.copy2(ROOT/'data/readability_benchmark/adopted_readability_model.json', model)
    inputs=load_campaign_inputs(seed_dir, slip, model, repair_epochs=6)
    keeper=output/'keeper'; keeper.mkdir()
    release_dir=keeper/'released'; release_dir.mkdir()
    release=copy.deepcopy(inputs['seed_grids'][0]); release['grid_id']='x5_connected_release'
    small=read(ROOT/'data/seed_grids/mg_seed_002.json');small['grid_id']='x5_size_refusal'
    raw=[json.dumps(release,indent=2).replace('\n','\r\n').encode(), json.dumps(small,indent=1).encode()]
    for name, content in zip(('a-release.json','b-incompatible.json'), raw): (release_dir/name).write_bytes(content)
    gathered, sources=gather_release_inputs(keeper, include_shared=False)
    plan=EraPlan(keeper/'era_plan.json');plan.stage(gathered,sources=sources)
    # Reload before execution to demonstrate the preparation journal boundary.
    plan=EraPlan(keeper/'era_plan.json')
    campaign=KeeperCampaign(inputs, campaign_id='x5-connected',era_config=TINY_ERA_CONFIG)
    era=campaign.advance_era('real',released_grids=plan.releases,released_sources=plan.release_sources,record_original=True)
    plan.begin(campaign,era,None);plan=EraPlan(keeper/'era_plan.json')
    plan.finish(keeper/'campaign.sqlite3',keeper/'campaign_state.json')
    pet=load_session_inputs(seed_dir/sorted(seed_dir.iterdir())[0].name, slip)
    CompanionSession(*pet[:2],model=pet[2]).save_checkpoint(keeper/'companion.json')
    checks={};details={}
    conn=sqlite3.connect((keeper/'campaign.sqlite3').resolve().as_uri()+'?mode=ro',uri=True)
    try:
        evidence=load_execution_summary(conn,'x5-connected',0)
        occurrences=evidence.get('founder_occurrences',[])
        checks['ordered_actual_admission_and_size_refusal']=[r['admitted'] for r in occurrences]==[True,False]
        checks['raw_release_bytes_retained']=all(base64.b64decode(era['execution']['blobs'][row['raw_sha256']]['data_base64'])==raw[row['source_position']]
            for row in era['execution']['manifest']['sources'] if row.get('role')=='founder')
        links=[descendant_lines(evidence,era['report'],elite) for elite in era['elites']]
        checks['actual_release_descendant_visible']=any('Recorded release origin:' in ' '.join(lines) for lines in links)
        details['descendant_links']=links
    finally:conn.close()
    # Move only our own source fixtures. Retained immutable bytes must stand alone.
    originals.rename(output/'original-inputs-moved')
    release_dir.rename(output/'released-inputs-moved')
    before=inventory(keeper)
    conn=sqlite3.connect((keeper/'campaign.sqlite3').resolve().as_uri()+'?mode=ro',uri=True)
    try:
        with patch('mecha_game.campaign.load_campaign_inputs',side_effect=AssertionError('live loader used')),\
             patch('mecha_game.campaign.build_weather_source',side_effect=AssertionError('weather loader used')),\
             patch('mecha_game.campaign.train_repair_model',side_effect=AssertionError('trainer used')):
            result=reproduce_era(conn,'x5-connected',0)
    finally:conn.close()
    checks['source_reproduction_after_original_paths_moved']=result['status']=='matched'
    checks['complete_report_and_every_elite_equal']=result.get('report')==era['report'] and result.get('elites')==era['elites']
    write(output/'source-comparison.json',result)
    flows=[]
    for label,batches in (
        ('restart-provenance',[[key(pygame.K_t)],[key(pygame.K_PAGEDOWN)],[key(pygame.K_b)],[key(pygame.K_END)]]),
        ('explicit-reproduction',[[key(pygame.K_t)],[key(pygame.K_d)]]),
    ):
        flow=interact(keeper,label,batches,screenshots,scale=16);flows.append(flow)
        checks[label+'_exit_and_fit']=flow['code']==0 and all(p['fits'] for p in flow['pages'])
        checks[label+'_worker_joined']=all(not row['alive'] for row in flow['joins'])
    checks['native_source_reproduction_notice']=any('Reproduction MATCHED' in ' '.join(p['all']) for f in flows for p in f['pages'])
    checks['read_and_reproduction_preserve_all_keeper_bytes']=before==inventory(keeper)
    checks['no_worker_left_alive']=not any(t.name.startswith('mechagotchi-') for t in threading.enumerate())
    from mecha_game.recorded_review import load_saved_replay
    recorded=load_saved_replay(keeper,'x5-connected',0,expected_seed=era['rng_seed'])
    checks['original_footage_present']=recorded is not None and any(name.startswith('replays/') for name in before)
    details['occurrences']=occurrences
    return dict(format='mechagotchi_x5_source_acceptance_v1',passed=all(checks.values()),checks=checks,
        keeper=relative(keeper),campaign_id='x5-connected',era_index=0,keeper_sha256=inventory(keeper),flows=flows,details=details,
        boundaries=['Injected source SDL events, not OS keyboard interaction.','Tiny diagnostic era; scientific adoption criteria unchanged.'])


def native_acceptance(output, source_output, bundle):
    from labs.game_loop.verify_detached_release import relocate_bundle, isolated_environment, validate_artifact_manifest
    output.mkdir(parents=True,exist_ok=False)
    source_report=read(source_output/'report.json')
    if not source_report['passed']: raise ValueError('Source acceptance has not passed')
    temp=Path(tempfile.mkdtemp(prefix='mecha-x5-native-'))
    artifact=relocate_bundle(bundle,temp/'player'); validate_artifact_manifest(artifact)
    home=temp/'home';home.mkdir();env=isolated_environment(home)
    executable=artifact/'Mechagotchi.exe';checks={};commands=[]
    def launch(label,args,*,windows=False):
        current=dict(env)
        if windows:
            current.pop('SDL_VIDEODRIVER',None);current.pop('SDL_AUDIODRIVER',None)
        start=time.perf_counter()
        result=subprocess.run([str(executable),*map(str,args)],cwd=temp,env=current,capture_output=True,timeout=180)
        (output/(label+'.stdout.log')).write_bytes(result.stdout)
        (output/(label+'.stderr.log')).write_bytes(result.stderr)
        commands.append(dict(label=label,args=list(map(str,args)),returncode=result.returncode,
            seconds=time.perf_counter()-start,actual_windows_sdl=windows))
        return result.returncode
    source_keeper=ROOT/source_report['keeper'];before=inventory(source_keeper)
    cross=output/'source-era-reproduced-by-native'
    code=launch('cross-runtime',['--keeper-dir',source_keeper,'--reproduce-era','0','--campaign-id','x5-connected','--output',cross])
    checks['source_inputs_reproduced_by_relocated_native']=code==0 and read(cross/'comparison.json')['status']=='matched'
    checks['source_keeper_bytes_preserved']=before==inventory(source_keeper)
    modes=('calm','stable_soup','storm','real','callback')
    for mode in modes:
        keeper=output/('native-'+mode)
        code=launch(mode+'-record',['--keeper-dir',keeper,'--era-scale','tiny','--prepare-weather',mode,'--eras','1',
            '--ticks','1','--tick-frames','1','--fps','0','--scale','1'],windows=mode=='calm')
        checks[mode+'_recorded_by_native']=code==0
        before=inventory(keeper)
        state=read(keeper/'campaign_state.json');comparison=output/(mode+'-comparison')
        code=launch(mode+'-reproduce',['--keeper-dir',keeper,'--reproduce-era','0','--campaign-id',state['campaign_id'],'--output',comparison])
        result=read(comparison/'comparison.json')
        checks[mode+'_full_reproduction_matched']=code==0 and result['status']=='matched' and result['report'] is not None and result['elites'] is not None
        checks[mode+'_keeper_all_bytes_preserved']=before==inventory(keeper)
    keeper=output/'native-calm';before=inventory(keeper)
    code=launch('native-review',['--keeper-dir',keeper,'--view','review','--frames','2','--scale','16'],windows=True)
    checks['actual_windows_review_launch']=code==0
    checks['review_preserved_all_keeper_bytes']=before==inventory(keeper)
    validate_artifact_manifest(artifact)
    checks['relocated_artifact_preserved']=True
    return dict(format='mechagotchi_x5_native_acceptance_v1',passed=all(checks.values()),checks=checks,commands=commands,
        exe_sha256=sha(executable),source_acceptance=relative(source_output/'report.json'),
        detached_artifact=str(artifact),native_processes=len(commands),actual_windows_sdl_launches=sum(c['actual_windows_sdl'] for c in commands),
        boundaries=['Actual process invocation from relocated built artifact.','CLI reproduction does not claim OS keyboard automation.','Temporary native artifact retained for inspection; no source mirror.'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase',choices=('source','native'));parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--source-output',type=Path);parser.add_argument('--bundle',type=Path)
    args=parser.parse_args()
    if args.phase=='native' and (args.bundle is None or args.source_output is None): parser.error('native requires --source-output and --bundle')
    result=source_acceptance(args.output.resolve()) if args.phase=='source' else native_acceptance(args.output.resolve(),args.source_output.resolve(),args.bundle.resolve())
    write(args.output/'report.json',result)
    print(json.dumps({'passed':result['passed'],'checks':len(result['checks']),'failed':[k for k,v in result['checks'].items() if not v]}))
    sys.exit(0 if result['passed'] else 1)
