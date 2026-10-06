"""Verify only a relocated Windows x64 onedir artifact, with no source imports.

The harness uses stdlib process/HTTP/file readers. It never imports game, engine
or Workshop modules. Native process/API evidence is not OS keyboard, browser
interaction or human usability evidence.
"""
from __future__ import annotations
import argparse
import copy
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT=Path(__file__).resolve().parents[2]
WEATHER=('calm','stable_soup','storm','real','callback')


def isolated_environment(home: Path) -> dict:
    env=dict(os.environ)
    for key in ('PYTHONPATH','PYTHONHOME','PYTHONSTARTUP','PYTHONUSERBASE'):
        env.pop(key,None)
    env.update(USERPROFILE=str(home),HOME=str(home),PYTHONNOUSERSITE='1',
        PYTHONDONTWRITEBYTECODE='1',PYINSTALLER_RESET_ENVIRONMENT='1',
        SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
    return env


def relocate_bundle(source: Path, destination: Path, repository: Path=ROOT) -> Path:
    source=Path(source).resolve();destination=Path(destination).resolve();repository=repository.resolve()
    if destination==repository or destination.is_relative_to(repository) or repository.is_relative_to(destination):
        raise ValueError('Detached destination must be outside repository ancestry.')
    if destination.exists():
        raise ValueError('Detached destination already exists.')
    if not (source/'Mechagotchi.exe').is_file():
        raise ValueError('Provide the built Mechagotchi onedir directory.')
    if source.is_relative_to(destination) or destination.is_relative_to(source):
        raise ValueError('Artifact source and destination must be disjoint.')
    # An artifact may contain no links into a source checkout or external home.
    if any(path.is_symlink() or getattr(path,'is_junction',lambda:False)() for path in source.rglob('*')):
        raise ValueError('Artifact contains a link; detached verification refuses external content.')
    shutil.copytree(source,destination)
    return destination


def json_read(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def inventory(root):
    root=Path(root)
    if root.is_file():return {'.':sha(root)}
    return {path.relative_to(root).as_posix():sha(path) for path in root.rglob('*') if path.is_file()}



def validate_artifact_manifest(bundle: Path) -> dict:
    manifest=json_read(bundle/'artifact-manifest.json')
    body={key:value for key,value in manifest.items() if key!='content_id'}
    digest=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
    if (manifest.get('format')!='mechagotchi_windows_artifact_v1'
            or manifest.get('target')!='windows_x64_onedir' or manifest.get('content_id')!=digest):
        raise ValueError('Artifact manifest identity is invalid.')
    records=manifest.get('files')
    if not isinstance(records,dict) or not records:
        raise ValueError('Artifact manifest has no files.')
    actual={path.relative_to(bundle).as_posix() for path in bundle.rglob('*')
            if path.is_file() and path!=bundle/'artifact-manifest.json'}
    if actual!=set(records):raise ValueError('Artifact manifest file inventory differs.')
    for name,record in records.items():
        relative=PurePosixPath(name)
        if relative.is_absolute() or '..' in relative.parts or name!=relative.as_posix() or ':' in name or chr(92) in name:
            raise ValueError('Artifact manifest contains an unsafe path.')
        path=bundle/name
        if path.stat().st_size!=record['size'] or sha(path)!=record['sha256']:
            raise ValueError('Artifact bytes differ from manifest: '+name)
    return manifest

def request(url,path,payload=None):
    req=urllib.request.Request(url.rstrip('/')+path,
        data=json.dumps(payload).encode('utf-8') if payload is not None else None,
        headers={'Content-Type':'application/json'})
    try:response=urllib.request.urlopen(req,timeout=40)
    except urllib.error.HTTPError as error:response=error
    with response:
        raw=response.read();headers=dict(response.headers)
        body=json.loads(raw) if 'application/json' in headers.get('Content-Type','') else raw
        return response.status,body,headers


def require_request(url,path,payload=None):
    status,body,headers=request(url,path,payload)
    if status!=200:raise ValueError(f'{path}: HTTP {status}: {body!r}')
    return body,headers



def startup_window_evidence(info, exit_code: int) -> bool:
    if not isinstance(info,dict):return False
    outcome=info.get('startup_outcome')
    display=info.get('display') or {}
    size=display.get('size')
    expected={'cancelled':0,'refused':2}.get(outcome)
    return (expected is not None and exit_code==expected and info.get('exit_code')==exit_code
        and info.get('stopped') is True and info.get('view')=='startup'
        and info.get('startup',{}).get('entered_play') is False
        and bool(display.get('driver')) and isinstance(size,list) and len(size)==2
        and all(type(value) is int and value>0 for value in size)
        and type(info.get('startup_rendered_frames')) is int
        and info['startup_rendered_frames']>=1)

def draft_snapshot(document,revision=1):
    return {'format':'mecha_workshop_draft_v1','draft_revision':revision,
        'document':copy.deepcopy(document),'editor_state':{'name':'detached'},
        'history':{'version':1,'history':[{'document':copy.deepcopy(document),'name':'detached'}],
                   'index':0,'saved':None}}



@contextmanager
def isolated_workspace(output: Path):
    with tempfile.TemporaryDirectory(prefix='mechagotchi-detached-') as folder:
        detached=Path(folder)
        runs=detached/'runs';runs.mkdir()
        try:
            yield detached,runs
        finally:
            # Retain only generated run evidence, never a second source tree or
            # another copy of the native artifact.
            shutil.copytree(runs,output/'isolated-runs')

def verify(bundle: Path, output: Path, expected_head: str | None=None) -> dict:
    bundle=Path(bundle).resolve();output=Path(output)
    if output.exists() or output.is_symlink():raise ValueError('Output already exists; choose a new directory.')
    output=output.resolve()
    if output.is_relative_to(bundle) or bundle.is_relative_to(output):
        raise ValueError('Output must be disjoint from the built artifact.')
    output.mkdir(parents=True,exist_ok=False)
    report={'format':'mechagotchi_detached_release_v1','ok':False,
        'scope':{'native_process':True,'http_api':True,'source_event_injection':False,
                 'browser_interaction':False,'os_keyboard':False,'human_usability':False},
        'artifact':{'source_bundle':str(bundle),'exe_sha256':sha(bundle/'Mechagotchi.exe')},
        'checks':{},'commands':[],'weather':{},'creator':{},'startup':{},
        'environment':{'platform':os.name,'python_source_paths_removed':True},
        'retained_run_files':'isolated-runs'}
    baseline=inventory(bundle)
    def record(name,condition):
        report['checks'][name]=bool(condition)
        if not condition:raise ValueError(f'Check failed: {name}')
    def save():
        (output/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    try:
        with isolated_workspace(output) as (detached,runs):
            copy_bundle=relocate_bundle(bundle,detached/'Mechagotchi')
            exe=copy_bundle/'Mechagotchi.exe';runtime_root=copy_bundle/'_internal'
            cwd=detached/'unrelated';cwd.mkdir()
            home=detached/'user';home.mkdir();env=isolated_environment(home)
            report['artifact']['relocated_bundle']=str(copy_bundle)
            report['artifact']['artifact_manifest_sha256']=sha(copy_bundle/'artifact-manifest.json')
            artifact_manifest=validate_artifact_manifest(copy_bundle)
            record('complete_artifact_bytes_verified',True)
            manifest=json_read(runtime_root/'runtime-manifest.json')
            record('artifact_runtime_identity_matches',artifact_manifest['runtime_content_id']==manifest['content_id'])
            report['artifact']['content_id']=manifest.get('content_id')
            report['artifact']['source']=manifest.get('source')
            record('relocated_outside_repository',not copy_bundle.is_relative_to(ROOT) and not ROOT.is_relative_to(copy_bundle))
            record('unrelated_working_directory',cwd!=copy_bundle and not cwd.is_relative_to(ROOT))
            record('save_and_output_homes_detached',not runs.is_relative_to(ROOT) and not ROOT.is_relative_to(runs))

            def check_runtime(info,label,complete=True):
                runtime=info['runtime']
                record(label+'_runtime_root',Path(runtime['root']).resolve()==runtime_root.resolve())
                record(label+'_frozen_target',runtime['mode']=='frozen_windows_x64' and runtime['target']=='windows_x64_onedir')
                record(label+'_manifest_identity',runtime['content_id']==manifest['content_id'])
                if complete:record(label+'_payload_complete',runtime['complete'])
                modules=runtime['loaded_modules']
                record(label+'_loaded_application',any(name.startswith('mecha_game.') for name in modules))
                record(label+'_no_source_imports',all(not Path(path).resolve().is_relative_to(ROOT) for path in modules.values()))
                if expected_head:
                    record(label+'_published_source_head',runtime['source']['head']==expected_head)
                    record(label+'_published_source_clean',runtime['source']['dirty'] is False)

            def run(name,args,timeout=600):
                receipt=runs/(name+'-launch.json')
                command=[str(exe),*args,'--launch-info',str(receipt)]
                result=subprocess.run(command,cwd=cwd,env=env,capture_output=True,text=True,
                    encoding='utf-8',errors='replace',timeout=timeout,
                    creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                (output/(name+'.stdout.log')).write_text(result.stdout or '',encoding='utf-8')
                (output/(name+'.stderr.log')).write_text(result.stderr or '',encoding='utf-8')
                info=json_read(receipt) if receipt.is_file() else None
                report['commands'].append({'name':name,'command':command,'exit_code':result.returncode,'launch_info':info})
                return result.returncode,info

            # The packaged public example launches its own ordinary preparation,
            # era, review, archive and resume processes. No source module is used.
            for weather in WEATHER:
                directory=runs/('example-'+weather)
                command=[str(exe),'--example','care-to-era','--output',str(directory),
                         '--prepare-weather',weather,'--era-scale','tiny']
                result=subprocess.run(command,cwd=cwd,env=env,capture_output=True,text=True,
                    encoding='utf-8',errors='replace',timeout=900,
                    creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                (output/(weather+'.stdout.log')).write_text(result.stdout or '',encoding='utf-8')
                (output/(weather+'.stderr.log')).write_text(result.stderr or '',encoding='utf-8')
                report['commands'].append({'name':'example-'+weather,'command':command,'exit_code':result.returncode})
                example=json_read(directory/'report.json') if (directory/'report.json').is_file() else {}
                report['weather'][weather]=example
                record(weather+'_actual_example',result.returncode==0 and example.get('ok') is True)
                for step in example['steps']:check_runtime(step['launch_info'],weather+'_'+step['name'])
                saved=json_read(directory/'saved-eras.json')[0]
                ids=saved['weather']['snapshot_ids']
                pressure=saved['report'].get('cubff_pressure',{}).get('by_generation',[])
                record(weather+'_source_ids_match_report',ids==[item['snapshot_id'] for item in pressure])
                if weather=='calm':
                    record('calm_no_pressure_source','cubff_pressure' not in saved['report'] and ids==[])
                else:
                    if weather in ('real','callback'):
                        relative=('data/cubff_real_ingest/real_snapshot_ingest_stage0_report.json'
                          if weather=='real' else 'data/cubff_real_ingest/callback_states/callback_states_compact.json')
                        payload=json_read(runtime_root/relative)
                        records=payload['ingested_snapshots'] if weather=='real' else payload['records']
                        source_ids=[item['snapshot_id'] for item in sorted(records,key=lambda item:item['epoch'])]
                        record(weather+'_original_source_bytes',sha(runtime_root/relative)==manifest['source']['files'][relative])
                    else:
                        prefix='weather_stable_' if weather=='stable_soup' else 'weather_storm_'
                        source_ids=[prefix+f'{index:03d}' for index in range(6)]
                    expected=[source_ids[index%len(source_ids)] for index in range(len(pressure))]
                    record(weather+'_actual_ordered_source_ids',bool(ids) and ids==expected)
                    record(weather+'_full_source_count',saved['report']['cubff_pressure']['source_snapshot_count']==len(source_ids))
                save()

            keeper=runs/'example-calm/keeper'
            remembered={}
            # Owned creator process is bounded even though care is paused.
            for attempt in (1,2):
                name=f'creator-{attempt}';receipt=runs/(name+'-launch.json')
                command=[str(exe),'--keeper-dir',str(keeper),'--creator','--no-browser',
                         '--frames','1200','--fps','30','--scale','2','--launch-info',str(receipt)]
                report['commands'].append({'name':name,'command':command})
                stdout=(output/(name+'.stdout.log')).open('w',encoding='utf-8')
                stderr=(output/(name+'.stderr.log')).open('w',encoding='utf-8')
                process=subprocess.Popen(command,cwd=cwd,env=env,stdout=stdout,stderr=stderr,
                    creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                url=None
                try:
                    deadline=time.monotonic()+45
                    info={}
                    while time.monotonic()<deadline and process.poll() is None:
                        try:info=json_read(receipt)
                        except (OSError,ValueError):pass
                        url=info.get('creator_url')
                        if url:break
                        time.sleep(.1)
                    record(name+'_ready',bool(url))
                    context,_=require_request(url,'/api/context')
                    record(name+'_selected_keeper',context['kind']=='native_keeper' and context['available'] and Path(context['keeper_dir'])==keeper)
                    pins={'context_id':context['context_id'],'expected_context_revision':context['context_revision']}
                    if attempt==1:
                        for page in ('/','/slip','/preview','/inspector','/packs','/shared/authoring.js','/shared/authoring.css'):
                            raw,_=require_request(url,page);record('packaged_asset_'+page,bool(raw))
                        rows,_=require_request(url,'/api/context/creatures')
                        selected=next(row for row in rows['creatures'] if row['source']=='companion')
                        chosen,_=require_request(url,'/api/context/document',{**pins,'ref':selected['ref']})
                        doc=chosen['document'];doc['grid']['metadata']['detached_probe']={'preserve':[1,'exact']}
                        snapshot=draft_snapshot(doc)
                        saved,_=require_request(url,'/api/drafts/grid',{**pins,'snapshot':snapshot,'expected_draft_revision':None})
                        record('complete_draft_saved',saved['snapshot']==snapshot)
                        status,_,_=request(url,'/api/drafts/grid',{**pins,'snapshot':snapshot,'expected_draft_revision':None})
                        record('draft_cas_refuses_stale',status==409)
                        saved_grid,_=require_request(url,'/api/save',{**pins,'document':doc,'name':'detached',
                            'draft_revision':1,'expected_disk_revision':None})
                        loaded,_=require_request(url,'/api/grids/detached')
                        record('full_document_save_load',loaded['document']==doc)
                        preview,_=require_request(url,'/api/preview/clip',{'document':doc,'draft_revision':1,'clip':'idle'})
                        record('packaged_clip_route',bool(preview.get('frames')) and preview.get('document')==doc)
                        # Curated IDs are protected by the real authoring route.
                        # A deliberate named copy keeps every other semantic field.
                        authored_profile=copy.deepcopy(doc['profile'])
                        authored_profile['profile_id']='detached_profile'
                        slipdoc={'format':'mecha_workshop_document_v1','profile':authored_profile}
                        reviewed_slip,_=require_request(url,'/api/slip/validate',{'document':slipdoc,'draft_revision':1})
                        record('packaged_slip_authority',reviewed_slip['valid'])
                        record('packaged_slip_advisory_available',reviewed_slip['authoring_review']['available'])
                        require_request(url,'/api/slip/save',{**pins,'document':slipdoc,'name':'detached_profile',
                            'draft_revision':1,'expected_disk_revision':None})
                        reloaded_slip,_=require_request(url,'/api/slips/detached_profile')
                        record('full_profile_save_load',reloaded_slip['document']==slipdoc)
                        released,_=require_request(url,'/api/release',{**pins,'document':doc,'name':'detached',
                            'draft_revision':1,'expected_release_revision':None})
                        record('release_bound_to_selected_keeper',released['release_provenance']['keeper_id']==context['keeper_id'])
                        record('release_preserves_semantic_document',released['released_document']['grid']['metadata']['detached_probe']=={'preserve':[1,'exact']})
                        pack_grid=copy.deepcopy(doc['grid']);pack_grid['grid_id']='detached_pack_candidate'
                        composition={**pins,'pack_id':'detached_demo','title':'Detached packaged example',
                            'provenance':{'purpose':'explicit isolated delivery check'},
                            'slips':[doc['profile']],'creatures':[pack_grid],'draft_revision':2}
                        built,_=require_request(url,'/api/packs/build',composition)
                        exported,_=require_request(url,'/api/packs/export',composition)
                        if isinstance(exported,bytes):exported=json.loads(exported)
                        record('pack_export_exact',exported==built['pack'])
                        reviewed,_=require_request(url,'/api/packs/preview',{**pins,'pack':built['pack']})
                        record('pack_item_review',reviewed['all_accepted'])
                        refused,_,_=request(url,'/api/packs/import',{**pins,'pack':built['pack'],'expected_pack_digest':'0'*64})
                        record('pack_stale_preview_refused',refused==409)
                        imported,_=require_request(url,'/api/packs/import',{**pins,'pack':built['pack'],
                            'expected_pack_digest':built['pack_digest']})
                        record('pack_import_items_staged',imported['all_accepted'])
                        record('pack_receipt_exact',json_read(keeper/'packs'/imported['receipt']['file'])==built['pack'])
                        remembered={'snapshot':snapshot,'context_id':context['context_id'],'released':released,
                                    'pack':built,'draft_revision':saved['draft_disk_revision']}
                    else:
                        recovered,_=require_request(url,'/api/drafts/grid')
                        record('creator_restart_context_identity',context['context_id']==remembered['context_id'])
                        record('creator_restart_complete_draft',recovered['snapshot']==remembered['snapshot']
                               and recovered['draft_disk_revision']==remembered['draft_revision'])
                        rows,_=require_request(url,'/api/context/creatures')
                        selected=next(row for row in rows['creatures'] if row['source']=='released' and row['label']=='detached')
                        chosen,_=require_request(url,'/api/context/document',{**pins,'ref':selected['ref']})
                        record('creator_restart_release_lineage',chosen['document']==remembered['released']['released_document'])
                    report['creator'][name]={'context':context,'url':url}
                finally:
                    try:process.wait(timeout=75)
                    except subprocess.TimeoutExpired:
                        process.kill();process.wait();report['checks'][name+'_bounded_exit']=False
                    stdout.close();stderr.close()
                    if receipt.is_file():
                        final=json_read(receipt)
                        report['creator'].setdefault(name,{})['launch_info']=final
                        check_runtime(final,name)
                        record(name+'_owned_shutdown',final.get('stopped') and process.returncode==0)
                    if url:
                        port=urllib.parse.urlparse(url).port
                        with socket.socket() as probe:
                            record(name+'_port_closed',probe.connect_ex(('127.0.0.1',port))!=0)
                save()

            valid=(keeper/'companion.json').read_bytes()
            cases={
                'malformed_primary':{'companion.json':b'{broken'},
                'malformed_with_valid_backup':{'companion.json':b'{broken primary retained','companion.bak.json':valid},
                'backup_only':{'companion.bak.json':valid},
                'invalid_backup':{'companion.json':b'{broken','companion.bak.json':b'{also broken'},
                'valid_primary_bad_backup':{'companion.json':valid,'companion.bak.json':b'{broken'},
            }
            for name,files in cases.items():
                target=runs/('startup-'+name);target.mkdir()
                for filename,raw in files.items():(target/filename).write_bytes(raw)
                before=inventory(target)
                code,info=run('startup-'+name,['--keeper-dir',str(target),'--startup','--frames','2','--fps','0'])
                report['startup'][name]={'exit_code':code,'launch_info':info}
                record(name+'_cancel_preserves_bytes',inventory(target)==before)
                record(name+'_windowed_outcome',startup_window_evidence(info,code))
            recovery_home=runs/'startup-malformed_with_valid_backup'
            rejected_primary=(recovery_home/'companion.json').read_bytes()
            code,info=run('explicit_backup_restore',['--keeper-dir',str(recovery_home),'--recover-backup',
                '--ticks','1','--tick-frames','1','--fps','0'])
            recovered=json_read(recovery_home/'companion.json')
            record('explicit_backup_restore_ready',code==0 and info['startup_outcome']=='ready')
            record('explicit_backup_restore_identity',recovered['chronicle']['keeper_id']==json.loads(valid)['chronicle']['keeper_id'])
            record('explicit_backup_preserves_original',any(path.read_bytes()==rejected_primary
                for path in recovery_home.iterdir() if path.is_file() and path.name!='companion.json'))
            qtable_home=runs/'qtable-self-contained'
            code,info=run('qtable_fixture',['--keeper-dir',str(qtable_home),'--learning-policy','qtable',
                '--ticks','1','--tick-frames','1','--fps','0'])
            record('qtable_saved_fixture',code==0 and info['learning_policy']=='qtable')
            target=runs/'startup-path-file';target.write_bytes(b'not a directory')
            before=inventory(target)
            code,info=run('startup-path-file',['--keeper-dir',str(target),'--startup','--frames','2','--fps','0'])
            record('path_conflict_actionable',startup_window_evidence(info,code))
            record('path_conflict_preserved',inventory(target)==before)

            # Only the relocated copy is altered, and its payload is restored.
            seeds=runtime_root/'data/seed_grids_16x16';hidden=runtime_root/'data/x4_hidden_seed_payload'
            seeds.rename(hidden)
            try:
                before=json_read(keeper/'companion.json')
                code,info=run('self_contained_saved_care',['--keeper-dir',str(keeper),'--ticks','1','--tick-frames','1','--fps','0'])
                after=json_read(keeper/'companion.json')
                record('saved_care_without_default_assets',code==0 and info['startup_outcome']=='ready'
                       and before['chronicle']['keeper_id']==after['chronicle']['keeper_id'])
                before_qtable=json_read(qtable_home/'companion.json')
                code,info=run('self_contained_qtable_care',['--keeper-dir',str(qtable_home),
                    '--ticks','1','--tick-frames','1','--fps','0'])
                after_qtable=json_read(qtable_home/'companion.json')
                record('qtable_care_without_default_assets',code==0 and info['startup_outcome']=='ready'
                    and info['learning_policy']=='qtable'
                    and before_qtable['chronicle']['keeper_id']==after_qtable['chronicle']['keeper_id']
                    and after_qtable['session_tick']==before_qtable['session_tick']+1)
                missing_home=runs/'missing-assets-home'
                code,info=run('missing_new_assets',['--keeper-dir',str(missing_home),'--new','--frames','2','--fps','0'])
                record('missing_new_assets_actionable',startup_window_evidence(info,code) and info['startup_outcome']=='refused')
                record('missing_new_assets_no_companion',not (missing_home/'companion.json').exists())
            finally:hidden.rename(seeds)
    except (OSError,ValueError,KeyError,TypeError,AttributeError,StopIteration,subprocess.TimeoutExpired) as error:
        report['error']=str(error)
    finally:
        report['checks']['original_artifact_preserved']=inventory(bundle)==baseline
        report['ok']=bool(report['checks']) and all(report['checks'].values()) and 'error' not in report
        save()
    return report


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--expected-head')
    args=parser.parse_args(argv)
    try:report=verify(args.bundle,args.output,args.expected_head)
    except (OSError,ValueError) as error:parser.exit(2,str(error)+'\n')
    print(json.dumps({'ok':report['ok'],'checks':len(report['checks']),'error':report.get('error'),
                      'report':str(args.output/'report.json')}))
    return 0 if report['ok'] else 1

if __name__=='__main__':raise SystemExit(main())
