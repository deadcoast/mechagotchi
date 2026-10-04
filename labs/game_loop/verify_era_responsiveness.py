"""Bound real source-app cancellation/help/close flows; no native keyboard automation."""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, sys, threading, time
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
for folder in ('game/src','packages/mecha_engine/src'):sys.path.insert(0,str(ROOT/folder))
from measure_era_responsiveness import bounded

def inventory(path):
    return {p.relative_to(path).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in path.rglob('*') if p.is_file() and 'model_cache' not in p.parts}

def prepare(template,keeper,policy,cold):
    from mecha_game.session import CompanionSession,load_session_inputs
    assert not keeper.exists(),'Preserve prior observation saves'
    keeper.mkdir(parents=True)
    for p in template.iterdir():
        if p.is_file() and not p.name.startswith(('companion','lineage')):shutil.copy2(p,keeper/p.name)
    if not cold and (template/'model_cache').is_dir():shutil.copytree(template/'model_cache',keeper/'model_cache')
    grid,slip,model=load_session_inputs(ROOT/'data/seed_grids_16x16/mg_seed16_001_beetle.json',ROOT/'data/slips/valid/slip_v2_cleanliness.json')
    CompanionSession(grid,slip,model=model,learning_policy=policy).save_checkpoint(keeper/'companion.json')

def observe(case,keeper,target,screenshots,policy):
    os.environ.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
    import pygame
    from mecha_game.app import _EraBench,run
    from mecha_game.era_plan import EraPlan
    from mecha_game.era_work import EraWork
    from mecha_game.footer import FooterPager
    from mecha_game.session import CompanionSession
    before=inventory(keeper);before_state=json.loads((keeper/'campaign_state.json').read_text())
    timing={};polls=[];flips=[];pages=[];images=[];senders=[];accepted=[];current=[];captured=set();get_count=0
    original_poll=pygame.event.poll;original_flip=pygame.display.flip;original_layout=FooterPager.layout
    original_progress=EraWork.progress;original_cancel=EraWork.cancel;original_era=_EraBench.run_era;original_begin=EraPlan.begin
    def post(key=None):
        timing.setdefault('request_posted',time.perf_counter())
        event=pygame.event.Event(pygame.QUIT) if key is None else pygame.event.Event(pygame.KEYDOWN,key=key,mod=0)
        pygame.event.post(event)
    def send_sequence():
        post(pygame.K_F1);time.sleep(.12);post(pygame.K_ESCAPE);time.sleep(.12);post(pygame.K_ESCAPE)
    def era(bench,*args,**kwargs):
        timing['era_entered']=time.perf_counter()
        if case=='cancel-loading':
            def delayed():time.sleep(.1);post(pygame.K_ESCAPE)
            thread=threading.Thread(target=delayed,name='source-cancel-probe');senders.append(thread);thread.start()
        try:return original_era(bench,*args,**kwargs)
        finally:timing['era_stopped']=time.perf_counter()
    def progress(work,n,budget):
        original_progress(work,n,budget)
        if n==2 and 'request_posted' not in timing:
            if case=='cancel-evaluation':
                for key in (pygame.K_f,pygame.K_3,pygame.K_e):pygame.event.post(pygame.event.Event(pygame.KEYDOWN,key=key,mod=0))
                post(pygame.K_ESCAPE)
            elif case=='close-evaluation':post()
            elif case=='help-cancel':
                thread=threading.Thread(target=send_sequence,name='source-help-probe');senders.append(thread);thread.start()
    def cancel(work):
        value=original_cancel(work)
        if value:accepted.append(time.perf_counter())
        return value
    def begin(plan,*args,**kwargs):
        if case=='close-commit':post()
        return original_begin(plan,*args,**kwargs)
    def poll():
        polls.append(time.perf_counter());event=original_poll()
        if event.type==pygame.QUIT or (event.type==pygame.KEYDOWN and event.key in (pygame.K_F1,pygame.K_ESCAPE)):
            timing.setdefault('request_polled',time.perf_counter())
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:timing.setdefault('escape_polls',[]).append(time.perf_counter())
        return event
    def events():
        nonlocal get_count
        get_count+=1;polls.append(time.perf_counter())
        return [pygame.event.Event(pygame.KEYDOWN,key=pygame.K_e,mod=0)] if get_count==1 else [pygame.event.Event(pygame.QUIT)]
    def layout(pager,lines,measure,width,rows):
        nonlocal current
        page=original_layout(pager,lines,measure,width,rows)
        current=list(lines)
        if lines and lines[0].startswith('ERA RUNNING'):
            item=dict(lines=list(lines),visible=list(page.lines),fits=all(measure(line)<=width for line in page.lines))
            if not pages or pages[-1]!=item:pages.append(item)
        return page
    def flip():
        flips.append(time.perf_counter());original_flip()
        if current and current[0].startswith('ERA RUNNING'):
            name='help' if 'help;' in current[0] else ('cancel' if any('Cancel requested' in line for line in current) else current[1].split()[0].lower())
            if name not in captured:
                captured.add(name);path=screenshots/f'{policy}-{case}-{name}.png'
                pygame.image.save(pygame.display.get_surface(),str(path));images.append(path.relative_to(ROOT).as_posix())
    with patch('pygame.event.get',events),patch('pygame.event.poll',poll),patch('pygame.display.flip',flip),patch.object(FooterPager,'layout',layout),patch.object(EraWork,'progress',progress),patch.object(EraWork,'cancel',cancel),patch.object(_EraBench,'run_era',era),patch.object(EraPlan,'begin',begin):
        code=run(['--keeper-dir',str(keeper),'--era-scale','session','--scale','1','--fps','60','--tick-frames','1'])
    for thread in senders:thread.join(timeout=3)
    after=inventory(keeper);after_state=json.loads((keeper/'campaign_state.json').read_text())
    committed=case=='close-commit'
    latency=timing['request_polled']-timing['request_posted']
    checks=dict(source_exit=code==0,event_latency_within_half_second=latency<=.5,
                rendering_within_half_second=max((b-a for a,b in zip(flips,flips[1:])),default=0)<=.5,
                companion_unchanged=before['companion.json']==after['companion.json'],
                policy_preserved=CompanionSession.load(keeper/'companion.json').learning_policy==policy,
                no_detached_worker=not any(t.name=='mechagotchi-era' for t in threading.enumerate()),
                casing_fits=all(row['fits'] for row in pages))
    if committed:
        checks.update(completed_result_saved_once=after_state['era_count']==before_state['era_count']+1,
                      no_pending_result=json.loads((keeper/'era_plan.json').read_text())['pending'] is None,
                      commit_refuses_cancellation=not accepted)
    else:
        checks.update(cancel_preserves_every_saved_file=before==after,cancellation_accepted=bool(accepted))
    if case=='help-cancel':
        checks['first_escape_closes_help_without_cancelling']=len(timing.get('escape_polls',[]))==2 and accepted[0]>=timing['escape_polls'][1]
        checks['help_was_rendered']=any('help;' in row['lines'][0] for row in pages)
    result=dict(case=case,policy=policy,returncode=code,checks=checks,request_latency_s=latency,
                request_to_stop_s=timing['era_stopped']-timing['request_posted'],
                max_poll_gap_s=max((b-a for a,b in zip(polls,polls[1:])),default=0),
                max_frame_gap_s=max((b-a for a,b in zip(flips,flips[1:])),default=0),
                frames=len(flips),pages=pages,screenshots=images,era_count_before=before_state['era_count'],
                era_count_after=after_state['era_count'],saved_files_equal=before==after)
    target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return all(checks.values())

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--worker');p.add_argument('--keeper',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--policy',default='incumbent');p.add_argument('--screenshots',type=Path,required=True);p.add_argument('--template',type=Path);p.add_argument('--fixtures',type=Path);args=p.parse_args()
    args.screenshots=args.screenshots.resolve();args.screenshots.mkdir(parents=True,exist_ok=True)
    if args.worker:
        pid_path=args.output.with_suffix('.pid.json')
        temporary=pid_path.with_suffix('.json.tmp')
        temporary.write_text(json.dumps({'pid':os.getpid()}))
        temporary.replace(pid_path)
        raise SystemExit(0 if observe(args.worker,args.keeper,args.output,args.screenshots,args.policy) else 1)
    rows=[]
    for policy in ('incumbent','qtable'):
        for case in ('cancel-loading','cancel-evaluation','help-cancel','close-evaluation','close-commit'):
            keeper=args.fixtures/f'{policy}-{case}';prepare(args.template,keeper,policy,case=='cancel-loading')
            target=args.output.with_name(args.output.stem+f'-{policy}-{case}.json')
            row=bounded(case,keeper,target,worker_script=Path(__file__).resolve(),worker_args=['--policy',policy,'--screenshots',str(args.screenshots)])
            rows.append(row)
            print(json.dumps({k:row[k] for k in ('case','returncode','limit_hit','elapsed_s','peak_working_set_mib')}),flush=True)
            args.output.write_text(json.dumps(dict(cases=rows,passed=all(r['returncode']==0 for r in rows)),indent=2)+'\n',encoding='utf-8')
            if row['returncode']!=0:raise SystemExit(1)
