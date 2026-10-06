"""An isolated executable care -> saved preparation -> era -> review -> restart example.

No simulation is reimplemented here. Every action runs the actual application.
The tiny era is a verification configuration, not a scientific performance claim.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sqlite3
import subprocess

WEATHER=('calm','stable_soup','storm','real','callback')


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def run_example(executable_command: list[str], output: Path, weather: str='calm',
                era_scale: str='tiny') -> dict:
    if (not isinstance(executable_command,list) or not executable_command or
            any(not isinstance(value,str) or not value for value in executable_command)):
        raise ValueError('Provide a nonempty executable command.')
    if weather not in WEATHER or era_scale not in ('tiny','session'):
        raise ValueError('Unsupported weather or era scale.')
    output=Path(output)
    if output.exists() or output.is_symlink():
        raise ValueError(f'Output already exists; choose a new directory: {output}')
    output=output.resolve()
    try: output.mkdir(parents=True,exist_ok=False)
    except FileExistsError as error:
        raise ValueError(f'Output already exists; choose a new directory: {output}') from error
    keeper=output/'keeper'
    report={'format':'mechagotchi_care_to_era_example_v1','ok':False,
        'keeper_dir':str(keeper),'weather':weather,'era_scale':era_scale,
        'scientific_evidence':False,
        'verification_scope':'Actual application processes; no OS keyboard or human usability claim.',
        'steps':[],'checks':{},'report_file':str(output/'report.json')}
    common=['--keeper-dir',str(keeper),'--era-scale',era_scale,
            '--tick-frames','1','--fps','0','--scale','2']
    steps=[
        ('care',['--ticks','2']),
        ('era',['--prepare-weather',weather,'--eras','1','--ticks','1']),
        ('review',['--view','review','--frames','2']),
        ('archive',['--view','archive','--frames','2']),
        ('restart',['--ticks','1']),
    ]
    first=None; after_era=None; era_state=None
    try:
        for name,args in steps:
            receipt=output/(name+'-launch.json')
            command=[*executable_command,*common,*args,'--launch-info',str(receipt)]
            result=subprocess.run(command,cwd=output,env=dict(os.environ,PYINSTALLER_RESET_ENVIRONMENT="1"),capture_output=True,text=True,
                encoding='utf-8',errors='replace',timeout=600,
                creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            (output/(name+'.stdout.log')).write_text(result.stdout or '',encoding='utf-8')
            (output/(name+'.stderr.log')).write_text(result.stderr or '',encoding='utf-8')
            info=read_json(receipt) if receipt.is_file() else None
            report['steps'].append({'name':name,'command':command,'exit_code':result.returncode,
                                    'launch_info':info})
            if result.returncode or info is None or not info.get('stopped'):
                raise ValueError(f'{name} did not complete; inspect its launch receipt and logs.')
            if info.get('startup_outcome')!='ready':
                raise ValueError(f'{name} did not enter a ready application.')
            current=read_json(keeper/'companion.json')
            if name=='care': first=current
            if name=='era':
                after_era=current;era_state=read_json(keeper/'campaign_state.json')
            if name in ('review','archive'):
                if info.get('view')!=name or info.get(name) is None:
                    raise ValueError(f'{name} did not expose its actual saved reader.')
                if current!=after_era:
                    raise ValueError(f'{name} changed the saved companion while reading.')
        final=read_json(keeper/'companion.json');state=read_json(keeper/'campaign_state.json')
        plan=read_json(keeper/'era_plan.json')
        conn=sqlite3.connect((keeper/'campaign.sqlite3').as_uri()+'?mode=ro',uri=True)
        try:
            rows=conn.execute('SELECT campaign_id,era_index,weather_json,report_json FROM eras ORDER BY era_index').fetchall()
        finally:conn.close()
        saved=[{'campaign_id':row[0],'era_index':row[1],'weather':json.loads(row[2]),
                'report':json.loads(row[3])} for row in rows]
        (output/'saved-eras.json').write_text(json.dumps(saved,indent=2)+'\n',encoding='utf-8')
        checks=report['checks']
        checks['keeper_identity_survives']=first['chronicle']['keeper_id']==final['chronicle']['keeper_id']
        checks['care_resumes']=final['session_tick']==after_era['session_tick']+1
        checks['campaign_survives']=era_state==state
        checks['actual_single_saved_era']=len(saved)==1 and state['era_count']==1
        checks['saved_preparation']=plan['weather']==weather and plan['pending'] is None
        checks['actual_weather']=bool(saved) and saved[0]['weather']['forecast']==weather
        checks['actual_source_ids']=bool(saved) and (
            saved[0]['weather']['snapshot_ids']==[] if weather=='calm'
            else bool(saved[0]['weather']['snapshot_ids']))
        checks['actual_report']=bool(saved) and isinstance(saved[0]['report'].get('summary'),dict)
        review=next(step['launch_info']['review'] for step in report['steps'] if step['name']=='review')
        archive=next(step['launch_info']['archive'] for step in report['steps'] if step['name']=='archive')
        checks['saved_review_and_archive']=(review['campaign_id']==state['campaign_id']
            and review['era_count']==1 and review['current_era_index']==0
            and review['weather']==saved[0]['weather'] and bool(review['lines'])
            and archive['campaign_id']==state['campaign_id'] and archive['era_index']==0
            and archive.get('error') is None
            and archive['entry_count']==saved[0]['report']['summary']['archive']['filled_niches'])
        report['ok']=all(checks.values())
    except (OSError,ValueError,KeyError,sqlite3.Error,subprocess.TimeoutExpired) as error:
        report['error']=str(error)
    with (output/'report.json').open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(json.dumps(report,indent=2,allow_nan=False)+'\n')
    return report


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executable',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--weather',choices=WEATHER,default='calm')
    parser.add_argument('--era-scale',choices=('tiny','session'),default='tiny')
    args=parser.parse_args(argv)
    try: report=run_example([str(args.executable.resolve())],args.output,args.weather,args.era_scale)
    except (OSError,ValueError) as error: parser.exit(2,str(error)+'\n')
    print(report['report_file'])
    return 0 if report['ok'] else 1

if __name__=='__main__':raise SystemExit(main())
