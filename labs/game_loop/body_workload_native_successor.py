"""Conditional native successor over an actual qualified frozen population result.

No evolve call and no fabricated death/unlock. The cold companion is a native
bridge for the recorded campaign, never an inherited biological companion.
The coordinator selects the first qualifying registered active outcome.
"""
from __future__ import annotations
import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import sys
import time
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
for folder in ('game/src','packages/mecha_engine/src'):sys.path.insert(0,str(ROOT/folder))

def qualified_terminal_extinction(report):
    """Require actual dead episode endpoints in the recorded terminal generation."""
    try:
        population=report['living_population'];terminal=population['termination'];generations=report['generations']
        index=terminal['generation_index']
        if (population['final_breeders'] or terminal['ended'] is not True
                or terminal['reason']!='no_eligible_breeders' or terminal['genuine_lifecycle_extinction'] is not True
                or type(index) is not int or not generations or generations[-1]['generation']!=index):return False
        rows=generations[-1]['creatures']
        episodes=[episode for row in rows for episode in
            [*(cycle.get('episode') for cycle in row['cycles']),row['breeding'].get('final_episode')]
            if episode is not None]
        return terminal['lifecycle_deaths']>0 and any(
            episode.get('alive') is False and isinstance(episode.get('death_cause'),str) and bool(episode['death_cause'])
            for episode in episodes)
    except (KeyError,TypeError,IndexError,AttributeError):return False

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--keeper-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--source-manifest-sha256',required=True)
    args=parser.parse_args();source=args.keeper_dir.resolve();output=args.output.resolve()
    if output.exists() or source==output or source in output.parents:raise ValueError('Conditional output must be a new separate evidence directory.')
    from mecha_engine.storage import load_era_execution,load_era_elites
    from mecha_game.execution import decode_execution_inputs,validate_execution_outputs,result_digest
    from mecha_game.campaign import KeeperCampaign
    from mecha_game.session import CompanionSession
    from mecha_game.app import run
    from mecha_game.native_ui import ActionStrip
    from mecha_game.footer import FooterPager
    def hashes(home):return {p.relative_to(home).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in home.rglob('*') if p.is_file()}
    before=hashes(source);record=json.loads((source/'record.json').read_text())
    identity=record['campaign_id']
    with closing(sqlite3.connect((source/'campaign.sqlite3').as_uri()+'?mode=ro',uri=True)) as conn:
        bundle=load_era_execution(conn,identity,0);elites=load_era_elites(conn,identity,0)
        row=conn.execute('SELECT report_json FROM eras WHERE campaign_id=? AND era_index=0',(identity,)).fetchone()
        if row is None:raise ValueError('Recorded actual outcome is missing.')
        report=json.loads(row[0]);validate_execution_outputs(bundle,report,elites)
    expected=dict(generations=6,population=16,damage_cycles=2,ticks=16,dropout_rate=.2)
    data=decode_execution_inputs(bundle)
    terminal=report['living_population']['termination']
    if (record['report_sha256']!=result_digest(report) or record['elites_sha256']!=result_digest(elites)
            or record['execution_manifest_sha256']!=result_digest(bundle['manifest'])
            or report.get('body_response')!='workload-v1' or data['effective_config']!=expected
            or data['rng_seed'] not in (20261130,20261201,20261202)
            or data.get('population_policy')!='generation_survivors_v1' or data.get('survival_regime')!='stress_probe'
            or data.get('cubff_density_pressure') is not False or report['living_population']['final_breeders']
            or not qualified_terminal_extinction(report)):
        raise ValueError('Conditional successor requires an actual registered active outcome with terminal lifecycle deaths and zero breeders.')
    actual=KeeperCampaign.load_state(data,source/'campaign_state.json',source/'campaign.sqlite3')
    if actual.status!='extinct' or actual.body_response!='workload-v1':raise ValueError('Recorded population is not eligible for successor.')
    inherited=actual.unlock_state();output.mkdir(parents=True);keeper=output/'keeper';shutil.copytree(source,keeper)
    # Pure bridge state for driving the existing campaign UI. This newborn is
    # explicitly not claimed to descend genetically from the extinct cohort.
    pet=CompanionSession(data['seed_grids'][0],actual.campaign['slip_profile'],model=data['generation_model'],body_response='workload-v1',learning_policy='incumbent')
    pet.bind_campaign(identity);pet.save_checkpoint(keeper/'companion.json')
    bridge=dict(body_response=pet.body_response,life_id=pet.lineage[-1]['life_id'],age_ticks=0,trained_state='thread_states' in pet.state,
        role='Cold native campaign bridge; no inherited biological companion claim')
    import pygame
    drawn={};lines=[];observations=[];index=0;phase='navigate';frames=0;deadline=time.monotonic()+55;driver=None
    steps=['preparation','campaign_successor','quit']
    original_draw=ActionStrip.draw;original_layout=FooterPager.layout;original_flip=pygame.display.flip
    def key(code,up=False,repeat=False):return pygame.event.Event(pygame.KEYUP if up else pygame.KEYDOWN,key=code,mod=0,repeat=repeat)
    def draw(strip,surface,font,rect):
        value=original_draw(strip,surface,font,rect);drawn.update(actions=strip.actions,rects=strip.button_rects,focus=strip.focused_id);return value
    def layout(pager,text,*a,**kw):
        lines[:]=text;return original_layout(pager,text,*a,**kw)
    def flip():
        nonlocal frames,driver
        if time.monotonic()>=deadline:raise TimeoutError('Conditional native successor exceeded55seconds.')
        frames+=1;original_flip();driver=pygame.display.get_driver()
        if 'Successor created with inherited unlocks' in ' '.join(lines):pygame.image.save(pygame.display.get_surface(),output/'successor.png')
    def events():
        nonlocal index,phase
        if not drawn:return []
        if index>=len(steps):raise AssertionError('Native successor did not quit after explicit Save and quit.')
        if phase=='release':phase='navigate';return [key(pygame.K_RETURN,up=True),key(pygame.K_F6)]
        target=steps[index];enabled=[row.id for row in drawn['actions'] if row.enabled]
        if target not in enabled:raise AssertionError('Actual native successor action unavailable: '+target)
        if phase=='navigate':phase='activate';return [key(pygame.K_F6),key(pygame.K_HOME),*[key(pygame.K_RIGHT) for _ in range(enabled.index(target))]]
        if drawn['focus']!=target or target not in drawn['rects']:raise AssertionError('Target action was not drawn before activation.')
        observations.append(dict(action=target,lines=list(lines)));index+=1;phase='release'
        return [key(pygame.K_RETURN),key(pygame.K_RETURN),key(pygame.K_RETURN,repeat=True)]
    with patch('pygame.event.get',side_effect=events),patch.object(ActionStrip,'draw',draw),patch.object(FooterPager,'layout',layout),patch('pygame.display.flip',side_effect=flip):
        code=run(['--keeper-dir',str(keeper),'--fps','0','--scale','2','--tick-frames','1'])
    child=KeeperCampaign.load_state(data,keeper/'campaign_state.json',keeper/'campaign.sqlite3')
    if (code!=0 or driver!='windows' or index!=len(steps) or child.status!='active' or child.era_offset!=0
            or child.campaign['predecessor_campaign_id']!=identity or child.inherited_unlocks!=inherited
            or child.base_profile!=actual.base_profile or child.body_response!='workload-v1' or hashes(source)!=before):
        raise AssertionError('Conditional native successor failed exact inherited/base/model/source preservation.')
    result=dict(passed=True,status='PASS',source_manifest_sha256=args.source_manifest_sha256,driver=driver,frames=frames,
        source_keeper=str(source),keeper_dir=str(keeper),source_report_sha256=result_digest(report),predecessor_campaign_id=identity,
        successor_campaign_id=child.campaign['campaign_id'],body_response=child.body_response,bridge=bridge,
        inherited_unlocks=inherited,observations=observations,source_preserved=True,
        next_era=['--keeper-dir',str(keeper),'--body-response','workload-v1','--eras','1'])
    (output/'native.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({'passed':True,'keeper_dir':str(keeper)}))
if __name__=='__main__':main()
