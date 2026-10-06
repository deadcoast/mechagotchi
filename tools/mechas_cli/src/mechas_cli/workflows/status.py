"""Observed application evidence, separate from historical research findings."""
from __future__ import annotations
import json
from pathlib import Path
from mechas_cli import development,theme


def readiness(root: Path, artifact_report: Path | None=None) -> dict:
    local=development.status(root)
    result={'application':{'form':'source_checkout','root':str(root),
                          'entry':'mechas game --play'},
        'local':{key:local.get(key,False) for key in ('full_current','local_complete')},
        'packaged':{'status':'unverified','reason':'No detached artifact report selected.'},
        'cloud':dict(local.get('publication_gate',{'status':'unmet'})),
        'research':{'blocks_application':False}}
    calibration=root/'data/readability/slip_readability_calibration_gate_stage0.json'
    if calibration.is_file():
        try:
            gate=json.loads(calibration.read_text(encoding='utf-8'))
            result['research']['manual_readability_calibration_ready']=bool(gate.get('manual_readability_calibration_ready'))
        except (OSError,ValueError) as error: result['research']['error']=str(error)
    if artifact_report is not None:
        try:
            report=json.loads(artifact_report.read_text(encoding='utf-8'))
            valid=(report.get('format')=='mechagotchi_detached_release_v1'
                   and report.get('ok') is True and bool(report.get('checks'))
                   and all(value is True for value in report['checks'].values()))
            result['packaged']={'status':'observed_pass' if valid else 'failed_or_incomplete',
                'report':str(artifact_report),'artifact':report.get('artifact'),
                'reason':'Recorded local artifact evidence; not a new verification or a cloud result.'}
        except (OSError,ValueError,TypeError) as error:
            result['packaged']={'status':'unavailable','reason':str(error)}
    return result


def show_status(root: Path, artifact_report: Path | None=None) -> dict:
    result=readiness(root,artifact_report)
    console=theme.console()
    console.print(theme.banner('status - application and evidence'))
    rows=[
        ('application',f"Source checkout: {root}\nPlay: mechas game --play",'mechas.ok'),
        ('local full sweep','Current source passed' if result['local']['full_current'] else
          'Not current; use mechas develop --status for exact gates','mechas.ok' if result['local']['full_current'] else 'mechas.warn'),
        ('Windows x64 artifact',result['packaged']['status']+' - '+result['packaged']['reason'],
          'mechas.ok' if result['packaged']['status']=='observed_pass' else 'mechas.warn'),
        ('published CI',result['cloud'].get('status','unmet')+'; exact published SHA requires separate Windows and Ubuntu evidence','mechas.warn'),
        ('research calibration','Historical manual readability calibration: '+
           ('ready' if result['research'].get('manual_readability_calibration_ready') else 'not ready / not recorded')+
           '. Separate research finding; does not block playing the application.','mechas.dim')]
    console.print(theme.kv_table(rows))
    return result
