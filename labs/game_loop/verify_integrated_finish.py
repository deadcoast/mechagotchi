"""W5 connected source demonstration; native process smoke is reported separately."""
import argparse,copy,hashlib,json,os,shutil,subprocess,sys,threading,time
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
for folder in ('game/src','packages/mecha_engine/src'):sys.path.insert(0,str(ROOT/folder))
os.environ.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
import pygame
from mecha_game.app import run,_EraBench
from mecha_game.footer import FooterPager
from mecha_game.session import CompanionSession
from mecha_game.packs import build_pack,write_pack
from mecha_game import wfc_trace
from mecha_game.era_work import EraWork
from mecha_engine.generation import explain_generation

def key(k,mod=0):return pygame.event.Event(pygame.KEYDOWN,key=k,mod=mod)
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
def inventory(root):return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}

def interact(keeper,label,batches,screenshots,*,scale=1,poll=None):
    sequence=iter(batches);pages=[];images=[];polls=[];busy=[];batch=-1;joins=[]
    original_layout,original_flip=FooterPager.layout,pygame.display.flip
    original_wfc_join,original_era_join=wfc_trace.WfcWork.join,EraWork.join
    def events():
        nonlocal batch
        batch+=1;polls.append(time.perf_counter())
        if batch>len(batches)+1:raise AssertionError('Unbounded flow')
        result=next(sequence,[pygame.event.Event(pygame.QUIT)])
        return result() if callable(result) else result
    def busy_poll():
        busy.append(time.perf_counter())
        return poll(len(busy)) if poll else pygame.event.Event(pygame.NOEVENT)
    def layout(pager,lines,measure,width,rows):
        result=original_layout(pager,lines,measure,width,rows)
        pages.append({'batch':batch,'all':list(lines),'visible':list(result.lines),'page':result.page,'pages':result.page_count,
                      'fits':len(result.lines)<=rows and all(measure(line)<=width for line in result.lines)})
        return result
    def flip():
        original_flip()
        # Capture each final outer screen plus a bounded number of busy frames.
        if not images or images[-1][0]!=batch:
            images.append((batch,pygame.display.get_surface().copy()))
        else:images[-1]=(batch,pygame.display.get_surface().copy())
    def wfc_join(work):
        original_wfc_join(work)
        joins.append({'kind':'wfc','alive':work.thread.is_alive(),'cancelled':work.cancelled,
                      'events_sha256':digest(work.events),'grid_sha256':digest(work.grid),'events':len(work.events)})
    def era_join(work):
        original_era_join(work);joins.append({'kind':'era','alive':work.thread.is_alive(),'status':work.snapshot()})
    with patch('pygame.event.get',events),patch('pygame.event.poll',busy_poll),patch.object(FooterPager,'layout',layout),patch('pygame.display.flip',flip),patch.object(wfc_trace.WfcWork,'join',wfc_join),patch.object(EraWork,'join',era_join):
        code=run(['--keeper-dir',str(keeper),'--era-scale','tiny','--scale',str(scale),'--fps','0','--tick-frames','1'])
    paths=[]
    for index,surface in images:
        path=screenshots/f'{label}-{index:02}.png';pygame.image.save(surface,str(path));paths.append(path.resolve().relative_to(ROOT).as_posix())
    return {'label':label,'scale':scale,'code':code,'pages':pages,'frames':len(pages),'screenshots':paths,'joins':joins,'busy_polls':len(busy),
            'max_busy_poll_gap_s':max((b-a for a,b in zip(busy,busy[1:])),default=0),
            'max_outer_poll_gap_s':max((b-a for a,b in zip(polls,polls[1:])),default=0)}

def verify(fixtures,screenshots,bundle):
    fixtures.mkdir(parents=True,exist_ok=False);screenshots.mkdir(parents=True,exist_ok=True)
    checks={};flows=[];launches=[]
    def play(keeper,label,batches,**kwargs):
        row=interact(keeper,label,batches,screenshots,**kwargs);flows.append(row)
        checks[label+'_exit_fit']=row['code']==0 and all(p['fits'] for p in row['pages'])
        checks[label+'_all_workers_joined']=all(not j['alive'] for j in row['joins']) and not any(t.name.startswith('mechagotchi-') for t in threading.enumerate())
        return row
    def at(row,batch):return next(p for p in reversed(row['pages']) if p['batch']==batch)
    for policy in ('incumbent','qtable'):
        keeper=fixtures/policy
        assert run(['--keeper-dir',str(keeper),'--era-scale','tiny','--eras','1','--ticks','1','--tick-frames','1','--fps','0','--scale','1','--learning-policy',policy])==0
        pet=CompanionSession.load(keeper/'companion.json');profile=copy.deepcopy(pet.slip_profile);profile['profile_id']='w5_finish'
        pack=build_pack(pack_id='w5_finish',title='Integrated finish example',provenance={'source':'existing seed and covenant; application diagnostic'},slips=[profile],creatures=[pet.grid])
        for name in ('a','z'):write_pack(pack,keeper/'packs'/f'{name}.json')
        initial=inventory(keeper);prepared={}
        def hatch():prepared.update(inventory(keeper));return [key(pygame.K_h)]
        row=play(keeper,policy+'-bridge-preview',[[key(pygame.K_k)],[key(pygame.K_END)],[key(pygame.K_RETURN)],
            [key(pygame.K_i)],[key(pygame.K_RETURN)],[key(pygame.K_k)],[key(pygame.K_ESCAPE)],hatch,
            [key(pygame.K_PAGEDOWN)],[key(pygame.K_PAGEDOWN)],[key(pygame.K_F1)],[key(pygame.K_PAGEDOWN)],[key(pygame.K_ESCAPE)],
            [key(pygame.K_TAB)],[key(pygame.K_END)],[key(pygame.K_v)],[key(pygame.K_F1)],[key(pygame.K_ESCAPE)],
            [key(pygame.K_TAB)],[key(pygame.K_ESCAPE),key(pygame.K_f)]],scale=1)
        checks[policy+'_pack_named_selection_retained']='2/2  z.json' in at(row,5)['all']
        checks[policy+'_hatch_page_restored']=at(row,9)['visible']==at(row,12)['visible'] and at(row,9)['page']==2
        checks[policy+'_imported_covenant']=json.loads((keeper/'campaign_state.json').read_text(encoding='utf-8'))['slip_profile']==profile
        checks[policy+'_preview_all_bytes_preserved']=prepared==inventory(keeper)
        checks[policy+'_import_kept_pet']=initial['companion.json']==inventory(keeper)['companion.json']
        checks[policy+'_hatch_kept_candidate']=at(row,7)['all']==at(row,18)['all']
        checks[policy+'_wfc_actual_events']=any(j['kind']=='wfc' and j['events']>0 for j in row['joins'])
        before=inventory(keeper)
        row=play(keeper,policy+'-history-small',[[key(pygame.K_t)],[key(pygame.K_PAGEDOWN)],[key(pygame.K_F1)],[key(pygame.K_ESCAPE)],
            [key(pygame.K_b)],[key(pygame.K_n)],[key(pygame.K_F1)],[key(pygame.K_ESCAPE)],[key(pygame.K_t)],
            [key(pygame.K_v)],[key(pygame.K_SPACE)],[key(pygame.K_F1)],[key(pygame.K_ESCAPE)],[key(pygame.K_v)],
            [key(pygame.K_ESCAPE),key(pygame.K_f)],[key(pygame.K_l)],[key(pygame.K_F1)],[key(pygame.K_ESCAPE)],[key(pygame.K_ESCAPE),key(pygame.K_f)]])
        checks[policy+'_history_all_bytes_preserved']=before==inventory(keeper)
        checks[policy+'_report_page_restored']=at(row,1)['visible']==at(row,3)['visible']
        checks[policy+'_history_views_reached']=all(any(title in ' '.join(p['all']) for p in row['pages']) for title in ('NICHE HISTORY HELP','REPLAY HELP','LINEAGE HELP'))
        row=play(keeper,policy+'-plan-era-adopt',[[key(pygame.K_c)],[key(pygame.K_F1)],[key(pygame.K_ESCAPE)],
            [key(pygame.K_c)],[key(pygame.K_r)],[key(pygame.K_w)],[key(pygame.K_e)],[key(pygame.K_b)],
            [key(pygame.K_a)],[key(pygame.K_o)],[key(pygame.K_F1)],[key(pygame.K_ESCAPE)]],scale=16)
        saved=CompanionSession.load(keeper/'companion.json');adopted=copy.deepcopy(saved.grid)
        checks[policy+'_era_completed']=any('ERA 1 ' in ' '.join(p['all']) for p in row['pages'])
        checks[policy+'_adopted_era_elite']=saved.lineage[-1]['origin']=='era_elite' and saved.learning_policy==policy
        checks[policy+'_preparation_consumed']=json.loads((keeper/'era_plan.json').read_text(encoding='utf-8'))['releases']==[]
        before=inventory(keeper)
        row=play(keeper,policy+'-restart-read',[[key(pygame.K_o)],[key(pygame.K_PAGEDOWN)],[key(pygame.K_F1)],[key(pygame.K_ESCAPE)],
            [key(pygame.K_ESCAPE)],[key(pygame.K_t)],[key(pygame.K_v)],[key(pygame.K_ESCAPE)],[key(pygame.K_ESCAPE)]],scale=16)
        checks[policy+'_restart_read_preserved']=before==inventory(keeper)
        native_env=os.environ.copy();native_env.pop('SDL_VIDEODRIVER',None);native_env.pop('SDL_AUDIODRIVER',None)
        for action in ('load','resume'):
            age=CompanionSession.load(keeper/'companion.json').state['age_ticks'];start=time.perf_counter()
            result=subprocess.run([str(bundle),'--keeper-dir',str(keeper),'--ticks','1','--tick-frames','1','--fps','0','--scale','1'],env=native_env,capture_output=True,text=True,timeout=90)
            current=CompanionSession.load(keeper/'companion.json')
            launches.append({'policy':policy,'action':action,'returncode':result.returncode,'seconds':time.perf_counter()-start,'age_before':age,'age_after':current.state['age_ticks'],'stdout':result.stdout,'stderr':result.stderr})
            checks[policy+'_native_'+action]=result.returncode==0 and current.grid==adopted and current.learning_policy==policy and current.state['age_ticks']==age+1
        for kind in ('wfc','era'):
            for close in (False,True):
                case=fixtures/f'{policy}-{kind}-{close}';shutil.copytree(keeper,case);before=inventory(case)
                original_capture=wfc_trace.capture_wfc;original_ensure=_EraBench.ensure
                def capture(*args,**kwargs):time.sleep(.15);return original_capture(*args,**kwargs)
                def ensure(bench,*,models=False):
                    if models:time.sleep(.15)
                    return original_ensure(bench,models=models)
                def poll(n):return (pygame.event.Event(pygame.QUIT) if close else key(pygame.K_ESCAPE)) if n==2 else pygame.event.Event(pygame.NOEVENT)
                with patch.object(wfc_trace,'capture_wfc',capture),patch.object(_EraBench,'ensure',ensure):
                    row=play(case,case.name,[[key(pygame.K_h)],[key(pygame.K_TAB)],[key(pygame.K_ESCAPE)]] if kind=='wfc' else [[key(pygame.K_e)]],poll=poll)
                after=inventory(case)
                # Model caches are derived; all saved state/preparation/history stays exact.
                checks[case.name+'_saved_bytes_preserved']=all(after.get(p)==v for p,v in before.items() if not p.startswith('model_cache/'))
                checks[case.name+'_polled_and_cancelled']=row['busy_polls']>=4 and any(j.get('cancelled') or j.get('status',{}).get('cancelling') for j in row['joins'])
    case=fixtures/'malformed-campaign';shutil.copytree(fixtures/'incumbent',case)
    state=case/'campaign_state.json';state.write_text('{}',encoding='utf-8')
    row=play(case,'malformed-campaign',[[key(pygame.K_c)],[key(pygame.K_F1)],[key(pygame.K_ESCAPE)],[key(pygame.K_c)],[key(pygame.K_x)]])
    checks['malformed_campaign_preserved']=state.read_text(encoding='utf-8')=='{}'
    checks['malformed_campaign_readable']=all(any(label in ' '.join(p['all']) for p in row['pages']) for label in ('Covenant unavailable','COVENANT HELP','Export not completed'))
    sources=['game/src/mecha_game/app.py','game/src/mecha_game/lineage.py','game/src/mecha_game/footer.py','game/src/mecha_game/inbox.py','game/src/mecha_game/generation_view.py','game/src/mecha_game/wfc_trace.py','game/tests/test_integrated_finish.py','game/tests/test_saved_archive.py','labs/game_loop/verify_integrated_finish.py']
    return {'artifact_id':'integrated_finish_release_stage0','date':'2026-10-05','checks':checks,'flows':flows,'native_launches':launches,
            'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},'native_sha256':hashlib.sha256(bundle.read_bytes()).hexdigest(),
            'boundaries':['Injected source pygame events and captured source pixels; no native keyboard automation.','Native executable load/resume checks run separately with normal SDL driver selection.','Tiny eras and deliberate 150ms worker delays are diagnostic scenarios; no scientific mechanics or acceptance thresholds changed.','Matching niche labels and campaign links do not infer ancestry.']}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('fixtures','screenshots','bundle','output'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();result=verify(args.fixtures,args.screenshots,args.bundle.resolve())
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'checks':len(result['checks']),'failed':[k for k,v in result['checks'].items() if not v],'flows':len(result['flows']),'frames':sum(f['frames'] for f in result['flows']),'native_launches':len(result['native_launches'])}))
    sys.exit(0 if all(result['checks'].values()) else 1)
