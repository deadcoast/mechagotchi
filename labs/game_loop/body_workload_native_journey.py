"""Bounded source SDL journey; coordinator owns its registered <=60s stage.

Injected SDL events are not OS input or a human usability claim. Only the new
output directory is written. This script performs no era/holdout outcome trial.
"""
from __future__ import annotations
import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import time
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
for folder in ('game/src','packages/mecha_engine/src'):sys.path.insert(0,str(ROOT/folder))

def run_journey(output, *, dummy=False, source_manifest_sha256=None):
    if output.exists():raise ValueError('Native journey requires a new output directory.')
    output.mkdir(parents=True)
    if dummy:
        os.environ['SDL_VIDEODRIVER']='dummy';os.environ['SDL_AUDIODRIVER']='dummy'
    import pygame
    from mecha_game.app import run
    from mecha_game.session import CompanionSession
    from mecha_game.native_ui import ActionStrip
    from mecha_game.footer import FooterPager
    home=output/'keeper';deadline=time.monotonic()+55;started=time.monotonic()
    observations=[];cold=[];screens=[];failed_saves=[];drivers=[]
    def check(condition, reason):
        if not condition:raise AssertionError(reason)
    def key(code,up=False,repeat=False):return pygame.event.Event(pygame.KEYUP if up else pygame.KEYDOWN,key=code,mod=0,repeat=repeat)
    def files():return {p.relative_to(home).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in home.rglob('*') if p.is_file()}
    original_save=CompanionSession.save
    should_fail=[False]
    def save(session,*args,**kwargs):
        if should_fail[0]:
            should_fail[0]=False;failed_saves.append(dict(tick=session.session_tick,life_id=session.lineage[-1]['life_id']))
            raise OSError('registered native interrupted checkpoint')
        if session.state['age_ticks']==0:
            cold.append(dict(life_id=session.lineage[-1]['life_id'],body_response=session.body_response,
                workload=session.state.get('body_workload'),trained_state='thread_states' in session.state))
        return original_save(session,*args,**kwargs)
    def drive(name,steps,*,startup=True):
        drawn={};all_lines=[];shown=[];position=0;phase='navigate';frames=0;pages=0
        original_draw=ActionStrip.draw;original_layout=FooterPager.layout;original_flip=pygame.display.flip
        def draw(strip,surface,font,rect):
            result=original_draw(strip,surface,font,rect)
            drawn.update(actions=tuple(strip.actions),rects=dict(strip.button_rects),focused=strip.focused_id)
            return result
        def layout(pager,lines,*args,**kwargs):
            result=original_layout(pager,lines,*args,**kwargs);all_lines[:]=list(lines);shown[:]=list(result.lines);return result
        def flip():
            nonlocal frames
            check(time.monotonic()<deadline,'Native journey exceeded 55-second internal bound')
            frames+=1;check(frames<3000,'Native driver frame cap exceeded');original_flip()
            driver=pygame.display.get_driver()
            if driver not in drivers:drivers.append(driver)
        def events():
            nonlocal position,phase,pages
            check(time.monotonic()<deadline,'Native journey exceeded 55-second internal bound')
            check(position<len(steps),'Native app did not close after explicit quit')
            if not drawn:return []
            target,method=steps[position]
            if phase=='apply_care':
                phase='navigate';return [key(pygame.K_RETURN,up=True)]
            if phase=='release':
                phase='navigate';return [key(pygame.K_RETURN,up=True),key(pygame.K_F6)]
            paging = target == '@body'
            if paging:
                if any('Play energy:' in line for line in shown):
                    screen=output/(name+'-body-'+str(len(screens))+'.png');pygame.image.save(pygame.display.get_surface(),screen)
                    screens.append(screen.name);observations.append(dict(stage=name,kind='visible_body_readout',lines=list(shown)))
                    position+=1;pages=0;return []
                target, method = 'next_page', 'keyboard'
            enabled=[a.id for a in drawn['actions'] if a.enabled]
            check(target in enabled,f'Visible action {target} unavailable: {enabled}')
            if phase=='navigate':
                phase='activate';return [key(pygame.K_F6),key(pygame.K_HOME),*[key(pygame.K_RIGHT) for _ in range(enabled.index(target))]]
            check(target in drawn['rects'] and target==drawn['focused'],'Activation must target an actually drawn control')
            observations.append(dict(stage=name,kind='action',action=target,method=method,lines=list(all_lines)))
            if paging:
                pages+=1;check(pages<25,'Body readout was not reachable through visible footer paging: '+repr(shown))
            else:position+=1
            phase='apply_care' if target in ('play','feed','sleep','clean') else 'release'
            if method=='interrupt':should_fail[0]=True
            if method=='mouse':
                point=drawn['rects'][target].center
                return [pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=point),pygame.event.Event(pygame.MOUSEBUTTONUP,button=1,pos=point)]
            return [key(pygame.K_RETURN),key(pygame.K_RETURN),key(pygame.K_RETURN,repeat=True)] if method=='repeat' else [key(pygame.K_RETURN)]
        args=['--keeper-dir',str(home),'--era-scale','tiny','--scale','2','--fps','0','--tick-frames','1']
        if startup:args+=['--startup']
        with patch('pygame.event.get',side_effect=events),patch.object(ActionStrip,'draw',draw),patch.object(FooterPager,'layout',layout),patch('pygame.display.flip',side_effect=flip),patch.object(CompanionSession,'save',save):
            check(run(args)==0,'Native journey returned nonzero')
        check(position==len(steps),'Not all explicit native steps executed')
        return frames
    first_frames=drive('new', [('new','keyboard'),('new_body','repeat'),('confirm_new','repeat'),('play','keyboard'),('feed','keyboard'),('sleep','keyboard'),('@body','page'),('lineage','keyboard'),('@body','page'),('back','keyboard'),('save','interrupt'),('save','keyboard'),('quit','mouse')])
    current=CompanionSession.load(home/'companion.json')
    check(current.body_response=='workload-v1','New life did not select active body response')
    check(len(current.lineage)==1,'Repeated confirmation created more than one life')
    check(len(failed_saves)==1,'Interrupted write was not exercised exactly once')
    check(any(row['body_response']=='workload-v1' and not row['trained_state'] for row in cold),'No actual cold active newborn checkpoint observed')
    check(current.lineage[-1]['care_summary']['keeper_actions'].get('play')==1,'Native repeated input changed actual play count')
    before=files();resume_frames=drive('resume',[('resume','keyboard'),('quit','mouse')]);check(files()==before,'Navigation-only resume changed saved bytes')
    with contextlib.redirect_stderr(io.StringIO()),contextlib.redirect_stdout(io.StringIO()):
        try:run(['--keeper-dir',str(home),'--ticks','1','--body-response','legacy'])
        except SystemExit as error:check(error.code==2,'Model conflict returned unexpected code')
        else:raise AssertionError('Conflicting model resumed')
    check(files()==before,'Conflicting model wrote save bytes')
    backup=(home/'companion.bak.json').read_bytes();primary=(home/'companion.json').read_bytes()
    restore_frames=drive('restore',[('inspect_backup','keyboard'),('confirm_restore','repeat'),('quit','mouse')])
    check((home/'companion.json').read_bytes()==backup,'Explicit native recovery did not preserve exact backup bytes')
    check(any(p.read_bytes()==primary for p in home.glob('companion.before-recovery-*.json')),'Recovery failed to retain replaced primary')
    restored=CompanionSession.load(home/'companion.json');check(restored.body_response=='workload-v1','Recovery changed model')
    report=dict(status='PASS',passed=not dummy and drivers==['windows'],classification='Actual native app with injected SDL events; no OS input or human usability claim',
        driver=drivers,dummy=dummy,source_manifest_sha256=source_manifest_sha256,elapsed_seconds=time.monotonic()-started,keeper_id=restored.keeper_id,
        life_id=restored.lineage[-1]['life_id'],body_response=restored.body_response,body_workload=restored.state['body_workload'],
        frames=dict(new=first_frames,resume=resume_frames,restore=restore_frames),observations=observations,cold_checkpoints=cold,
        interrupted_writes=failed_saves,screenshots=screens,repeat_created_one_life=True,repeat_applied_one_play=True,
        restart_bytes_preserved=True,conflict_bytes_preserved=True,recovery_exact=True,files=files())
    check(dummy or drivers==['windows'],'Registered native stage must use actual Windows SDL driver')
    (output/'native.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--dummy',action='store_true',help='operational harness test only, never native qualification')
    parser.add_argument('--source-manifest-sha256')
    args=parser.parse_args();report=run_journey(args.output,dummy=args.dummy,source_manifest_sha256=args.source_manifest_sha256)
    print(json.dumps({key:report[key] for key in ('status','driver','elapsed_seconds','frames')}))
if __name__=='__main__':main()
