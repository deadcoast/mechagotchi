"""Bound actual source pygame era work; retain pre-repair results and event latency."""
from __future__ import annotations
import argparse, ctypes, hashlib, json, os, subprocess, sys, threading, time
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
for folder in ('game/src','packages/mecha_engine/src'):
    sys.path.insert(0,str(ROOT/folder))

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def observe(case,keeper,target):
    os.environ.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
    import pygame
    from mecha_game.app import _EraBench,run
    from mecha_game.era_review import EraReview
    from mecha_game.covenant import apply_covenant_change
    from mecha_game.footer import FooterPager
    setup={}
    if case=='larger':
        bench=_EraBench('session',keeper/'model_cache',keeper/'campaign_state.json',keeper/'campaign.sqlite3')
        campaign=bench.ensure()
        setup={'earned_budget':campaign.budget(),'earned_unlocks':campaign.unlock_state()}
        result=bench.change_covenant(lambda c:apply_covenant_change(c,population=32,generations=12))
        if not result['ok']:raise ValueError(f'No genuine earned larger configuration: {result}')
    polls=[];flips=[];timing={};threads=[];busy=[];outer_polls=0;current=[];images=[];captured=set()
    screenshots=target.with_name(target.stem+'-ui').resolve();screenshots.mkdir(parents=True,exist_ok=True)
    original_get=pygame.event.get;original_poll=pygame.event.poll;original_flip=pygame.display.flip;original_era=_EraBench.run_era
    original_layout=FooterPager.layout
    def era(bench,*args,**kwargs):
        timing['era_entered']=time.perf_counter()
        def post():
            time.sleep(.1)
            timing['help_posted']=time.perf_counter()
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_F1,mod=0))
            time.sleep(.2)
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_F1,mod=0))
        thread=threading.Thread(target=post,name='bounded-source-input-probe')
        threads.append(thread);thread.start()
        result=original_era(bench,*args,**kwargs)
        timing['era_returned']=time.perf_counter()
        return result
    def busy_poll():
        polls.append(time.perf_counter());event=original_poll()
        if event.type==pygame.KEYDOWN and event.key==pygame.K_F1:timing.setdefault('help_polled',time.perf_counter())
        return event
    def layout(pager,lines,measure,width,height):
        nonlocal current
        current=list(lines)
        page=original_layout(pager,lines,measure,width,height)
        if lines and lines[0].startswith('ERA RUNNING'):
            row=dict(lines=list(lines),visible=list(page.lines),fits=all(measure(line)<=width for line in page.lines))
            if not busy or busy[-1]!=row:busy.append(row)
        return page
    def events():
        nonlocal outer_polls
        outer_polls+=1;polls.append(time.perf_counter())
        if outer_polls==1:return []
        if outer_polls==2:return [pygame.event.Event(pygame.KEYDOWN,key=pygame.K_e,mod=0)]
        rows=original_get()
        if any(e.type==pygame.KEYDOWN and e.key==pygame.K_F1 for e in rows):
            timing['help_polled']=time.perf_counter()
        return rows+[pygame.event.Event(pygame.QUIT)]
    def flip():
        flips.append(time.perf_counter());original_flip()
        if current and current[0].startswith('ERA RUNNING'):
            marker='help' if 'help;' in current[0] else current[1].split()[0].lower()
            count=next((line.split()[1] for line in current if line.startswith('Evaluations ')),None)
            if count:
                done,budget=map(int,count.split('/'));marker+=f'-{4*done//budget}'
            if marker not in captured:
                captured.add(marker);path=screenshots/f'{case}-{marker}.png'
                pygame.image.save(pygame.display.get_surface(),str(path));images.append(path.relative_to(ROOT).as_posix())
    started=time.perf_counter()
    with patch.object(_EraBench,'run_era',era),patch('pygame.event.get',events),patch('pygame.event.poll',busy_poll),patch.object(FooterPager,'layout',layout),patch('pygame.display.flip',flip):
        code=run(['--keeper-dir',str(keeper),'--era-scale','session','--scale','1','--fps','60','--tick-frames','1000000']+(['--new'] if case=='normal' else []))
    for thread in threads:thread.join(timeout=1)
    history=EraReview.load(keeper).history
    current=history['eras'][-1]
    report=current['report']
    evaluations=sum(len(g.get('creatures',[])) for g in report['generations'])
    result=dict(case=case,returncode=code,setup=setup,elapsed_s=time.perf_counter()-started,
        era_call_s=timing['era_returned']-timing['era_entered'],max_poll_gap_s=max(b-a for a,b in zip(polls,polls[1:])),
        max_frame_gap_s=max(b-a for a,b in zip(flips,flips[1:])),
        help_input_latency_s=timing.get('help_polled',timing['era_returned'])-timing['help_posted'],
        polls=len(polls),frames=len(flips),busy_pages=busy,screenshots=images,era_count=len(history['eras']),era_index=current['era_index'],rng_seed=current['rng_seed'],
        config=json.loads((keeper/'campaign_state.json').read_text())['era_config'],actual_evaluations=evaluations,
        report_sha256=digest(report),report=report,state=json.loads((keeper/'campaign_state.json').read_text()),
        pending=json.loads((keeper/'era_plan.json').read_text())['pending'],
        companion=json.loads((keeper/'companion.json').read_text()),keyboard_scope='source pygame events, SDL dummy; no native keyboard')
    target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')

def working_set(process):
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[(name,ctypes.c_size_t) for name in ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage')]
    counters=Counters();counters.cb=ctypes.sizeof(counters)
    func=ctypes.WinDLL('psapi').GetProcessMemoryInfo
    func.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD];func.restype=wintypes.BOOL
    if not func(wintypes.HANDLE(int(process._handle)),ctypes.byref(counters),counters.cb):
        raise ctypes.WinError()
    return counters.WorkingSetSize

def bounded(case,keeper,target,seconds=90,memory_mib=512,worker_script=None,worker_args=()):
    command=[sys.executable,'-B',str(worker_script or Path(__file__).resolve()),'--worker',case,'--keeper',str(keeper),'--output',str(target),*worker_args]
    started=time.monotonic();peak=0;reason=None;worker_handle=None
    pid_file=target.with_suffix('.pid.json')
    assert not pid_file.exists(), 'Preserve existing observation process record'
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong];kernel.OpenProcess.restype=ctypes.c_void_p
    kernel.TerminateProcess.argtypes=[ctypes.c_void_p,ctypes.c_uint]
    kernel.CloseHandle.argtypes=[ctypes.c_void_p]
    with target.with_suffix('.stdout.log').open('w',encoding='utf-8') as stdout,target.with_suffix('.stderr.log').open('w',encoding='utf-8') as stderr:
        proc=subprocess.Popen(command,cwd=ROOT,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        try:
            while proc.poll() is None:
                if worker_handle is None and pid_file.is_file():
                    worker_pid=json.loads(pid_file.read_text())['pid']
                    worker_handle=kernel.OpenProcess(0x0400|0x0010|0x0001,False,worker_pid)
                    if not worker_handle:raise ctypes.WinError()
                if worker_handle is not None:
                    from types import SimpleNamespace
                    try:peak=max(peak,working_set(SimpleNamespace(_handle=worker_handle)))
                    except OSError:
                        if proc.poll() is None:time.sleep(.05)
                if peak>memory_mib*1024**2:reason='working-set limit';break
                if time.monotonic()-started>seconds:reason='elapsed-time limit';break
                time.sleep(.05)
        finally:
            if proc.poll() is None:
                if worker_handle is not None:kernel.TerminateProcess(worker_handle,124)
                try:proc.wait(timeout=3)
                except subprocess.TimeoutExpired:proc.kill()
            proc.wait(timeout=10)
            if worker_handle is not None:kernel.CloseHandle(worker_handle)
    result=dict(case=case,command=command,returncode=proc.returncode,limit_hit=reason,elapsed_limit_s=seconds,
                working_set_limit_mib=memory_mib,memory_scope='actual Python worker; venv launcher excluded; sampled every 50ms',peak_working_set_mib=round(peak/1024**2,3),elapsed_s=time.monotonic()-started)
    if proc.returncode==0:
        value=json.loads(target.read_text(encoding='utf-8'))
        result['observation']={k:v for k,v in value.items() if k not in ('report','companion','state','setup')}
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--worker',choices=['normal','larger']);p.add_argument('--keeper',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.worker:
        pid_path=args.output.with_suffix('.pid.json')
        temporary=pid_path.with_suffix('.json.tmp')
        temporary.write_text(json.dumps({'pid':os.getpid()}))
        temporary.replace(pid_path)
        observe(args.worker,args.keeper,args.output)
    else:
        assert not args.keeper.exists(),'Preserve prior baseline; select a fresh private fixture.'
        args.keeper.mkdir(parents=True);args.output.parent.mkdir(parents=True,exist_ok=True)
        rows=[]
        for case in ('normal','larger'):
            row=bounded(case,args.keeper,args.output.with_name(args.output.stem+'-'+case+'.json'));rows.append(row)
            print(json.dumps(row),flush=True)
            args.output.write_text(json.dumps({'cases':rows,'limits':'90 seconds and 512 MiB per source process; <=384 candidate evaluations per era'},indent=2)+'\n',encoding='utf-8')
            if row['returncode']!=0:break
        raise SystemExit(0 if len(rows)==2 and all(r['returncode']==0 for r in rows) else 1)
