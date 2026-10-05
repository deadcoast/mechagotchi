"""W4 observed source wave inspector, genuine failures, joined cancellation and native smoke."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
from unittest.mock import patch
from verify_hatch_preview import ROOT, interact, inventory, key, digest
import pygame
from mecha_game.campaign import KeeperCampaign, load_campaign_inputs, default_campaign_paths
from mecha_game.session import CompanionSession, load_session_inputs
from mecha_game import wfc_trace
from mecha_engine.generation import generate_wfc_grid, train_wfc_model

def verify(fixtures,screenshots,bundle):
    fixtures.mkdir(parents=True,exist_ok=False);screenshots.mkdir(parents=True,exist_ok=True)
    inputs=load_campaign_inputs(**default_campaign_paths(ROOT),with_models=False)
    pet=load_session_inputs(ROOT/'data/seed_grids_16x16/mg_seed16_001_beetle.json',ROOT/'data/slips/valid/slip_v2_cleanliness.json')
    profile=json.loads((ROOT/'data/slips/valid/slip_lcd_seed.json').read_text())
    baseline=json.loads((ROOT/'data/game_client/wfc_trace_before_stage0.json').read_text())
    flows=[];checks={};launches=[];examples={}
    original_join=wfc_trace.WfcWork.join;original_capture=wfc_trace.capture_wfc
    def seed(label,policy):
        keeper=fixtures/label;keeper.mkdir();campaign=KeeperCampaign(inputs)
        campaign.save(keeper/'campaign.sqlite3');campaign.save_state(keeper/'campaign_state.json')
        CompanionSession(pet[0],pet[1],model=pet[2],learning_policy=policy).save_checkpoint(keeper/'companion.json')
        return keeper
    def play(keeper,label,batches,*,poll=None):
        captures=[];busy=[]
        def joined(work):
            original_join(work)
            row={'event_count':len(work.events),'events_sha256':digest(work.events),'grid_sha256':digest(work.grid),
                 'error':str(work.error) if work.error is not None else None,'cancelled':work.cancelled,'alive_after_join':work.thread.is_alive(),
                 'attempts':sum(e['event']=='attempt_started' for e in work.events)}
            captures.append(row)
            if work.events and 'normal' not in examples and work.grid is not None:
                examples['normal']={'grid':copy.deepcopy(work.grid),'events':copy.deepcopy(work.events)}
            if work.events and work.error is not None:
                examples.setdefault('failed',{'error':str(work.error),'events':copy.deepcopy(work.events)})
        def busy_poll():
            busy.append(time.perf_counter())
            return poll(len(busy)) if poll else pygame.event.Event(pygame.NOEVENT)
        with patch.object(wfc_trace.WfcWork,'join',joined),patch('pygame.event.poll',side_effect=busy_poll):
            row=interact(keeper,label,batches,screenshots)
        row['captures']=captures;row['busy_polls']=len(busy)
        row['max_busy_poll_gap_s']=max((b-a for a,b in zip(busy,busy[1:])),default=0)
        flows.append(row)
        checks[label+'_rendered_and_exit']=row['code']==0 and all(p['fits'] for p in row['pages'])
        checks[label+'_joined']=all(not c['alive_after_join'] for c in captures) and not any(t.name=='mechagotchi-wfc' for t in threading.enumerate())
        checks[label+'_bounded_outer_poll_gap']=row['max_poll_gap_s']<.5
        return row
    for policy in ('incumbent','qtable'):
        label=policy+'-import-inspect';keeper=seed(label,policy);(keeper/'covenants').mkdir();(keeper/'covenants/chosen.json').write_text(json.dumps(profile))
        before=inventory(keeper);prepared={}
        def hatch():prepared.update(inventory(keeper));return [key(pygame.K_h)]
        row=play(keeper,label,[[key(pygame.K_i)],[key(pygame.K_RETURN)],[key(pygame.K_ESCAPE)],hatch,
            [key(pygame.K_TAB)],[key(pygame.K_PERIOD)],[key(pygame.K_SPACE)],[],[],[key(pygame.K_F1)],[key(pygame.K_ESCAPE)],
            [key(pygame.K_PAGEDOWN)],[key(pygame.K_END)],[key(pygame.K_v)],[key(pygame.K_RIGHTBRACKET)],[key(pygame.K_PERIOD)],
            [key(pygame.K_v)],[key(pygame.K_HOME)],[key(pygame.K_TAB)],[key(pygame.K_ESCAPE),key(pygame.K_f)]])
        expected_events=[];expected=generate_wfc_grid(train_wfc_model(inputs['seed_grids']),grid_id='mg_wfc_preview_001',rng_seed=20261006,trace=expected_events)
        checks[label+'_direct_engine_grid_events_exact']=row['captures'][0]['grid_sha256']==digest(expected) and row['captures'][0]['events_sha256']==digest(expected_events)
        checks[label+'_post_import_all_bytes_unchanged']=prepared==inventory(keeper)
        checks[label+'_companion_unchanged']=before['companion.json']==inventory(keeper)['companion.json']
        headers=[' '.join(p['all']) for p in row['pages']]
        checks[label+'_trace_final_help_visible']=all(any(title in text for text in headers) for title in ('WFC TRACE','WFC FINAL BODY','WFC HELP'))
        hatch_pages=[p['all'] for p in row['pages'] if p['all'][0].startswith('HATCH PREVIEW')]
        checks[label+'_original_candidate_retained']=hatch_pages[0]==hatch_pages[-1]
        before=inventory(keeper)
        row=play(keeper,policy+'-restart',[[key(pygame.K_h)],[key(pygame.K_TAB)],[key(pygame.K_END)],[key(pygame.K_TAB)],[key(pygame.K_ESCAPE)]])
        checks[policy+'_restart_fresh_deterministic']=row['captures'][0]['events_sha256']==digest(expected_events) and before==inventory(keeper)
        for action in ('load','resume'):
            result=subprocess.run([str(bundle),'--keeper-dir',str(keeper),'--ticks','1','--tick-frames','1','--fps','0','--scale','1'],capture_output=True,text=True,timeout=90)
            current=CompanionSession.load(keeper/'companion.json')
            launches.append({'policy':policy,'action':action,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'age':current.state['age_ticks']})
            checks[policy+'_native_'+action]=result.returncode==0 and current.grid==pet[0] and current.learning_policy==policy
        for failure in ('failed','empty'):
            label=policy+'-'+failure+'-retry';keeper=seed(label,policy);before=inventory(keeper);calls=[0]
            def capture(seeds,grid_id,rng_seed,events):
                calls[0]+=1
                if calls[0]==1:
                    if failure=='empty':raise ValueError('observed unavailable corpus')
                    return generate_wfc_grid(baseline['models']['contradiction'],grid_id=grid_id,rng_seed=rng_seed,trace=events)
                return original_capture(seeds,grid_id,rng_seed,events)
            with patch.object(wfc_trace,'capture_wfc',capture):
                row=play(keeper,label,[[key(pygame.K_h)],[key(pygame.K_TAB)],[key(pygame.K_END)],[key(pygame.K_LEFTBRACKET)],
                    [key(pygame.K_PAGEDOWN)],[key(pygame.K_n)],[key(pygame.K_END)]])
            checks[label+'_retained_failure_then_success']=row['captures'][0]['error'] is not None and row['captures'][1]['error'] is None
            checks[label+'_actual_attempt_count']=row['captures'][0]['attempts']==(8 if failure=='failed' else 0)
            checks[label+'_all_bytes_unchanged']=before==inventory(keeper)
        for close in (False,True):
            label=policy+('-close' if close else '-cancel');keeper=seed(label,policy);before=inventory(keeper)
            def slow(*args,**kwargs):time.sleep(.15);return original_capture(*args,**kwargs)
            def poll(n):return (pygame.event.Event(pygame.QUIT) if close else key(pygame.K_ESCAPE)) if n==2 else pygame.event.Event(pygame.NOEVENT)
            with patch.object(wfc_trace,'capture_wfc',slow):
                row=play(keeper,label,[[key(pygame.K_h)],[key(pygame.K_TAB)],[key(pygame.K_ESCAPE)]],poll=poll)
            checks[label+'_cancelled_discarded']=row['captures'][0]['cancelled'] and not any(p['all'][0].startswith('WFC TRACE') for p in row['pages'])
            checks[label+'_engine_still_exact']=row['captures'][0]['grid_sha256']==digest(expected) and row['captures'][0]['events_sha256']==digest(expected_events)
            checks[label+'_polled_during_call']=row['busy_polls']>4
            checks[label+'_all_bytes_unchanged']=before==inventory(keeper)
    sources=['game/src/mecha_game/app.py','game/src/mecha_game/wfc_trace.py','game/src/mecha_game/generation_view.py','game/src/mecha_game/footer.py',
       'packages/mecha_engine/src/mecha_engine/generation/wfc.py','packages/mecha_engine/src/mecha_engine/generation/__init__.py','labs/wfc_grid/wfc_grid.py',
       'labs/wfc_grid/test_wfc_trace.py','game/tests/test_wfc_trace_view.py','labs/game_loop/verify_wfc_trace.py']
    return {'artifact_id':'wfc_trace_release_stage0','date':'2026-10-05','checks':checks,'flows':flows,'examples':examples,'native_launches':launches,
       'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},'native_sha256':hashlib.sha256(bundle.read_bytes()).hexdigest(),
       'boundaries':['WFC remains a distinct optional arm; constrained is the DR0042 evolution default.','Source pygame keys/rendering observed; native launch/resume smoke separately observed; native WFC keyboard unobserved.',
        'Wave rendering depicts observed choices; final body uses engine packets. No adoption or save writes.','Cancel discards after joined bounded call; engine decisions still finish unchanged.','Traces session-only; restart explicitly captures anew.']}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('fixtures','screenshots','bundle','output'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();result=verify(args.fixtures,args.screenshots,args.bundle.resolve())
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'checks':len(result['checks']),'failed':[k for k,v in result['checks'].items() if not v],
       'flows':len(result['flows']),'frames':sum(f['frames'] for f in result['flows']),'native_launches':len(result['native_launches']),
       'max_outer_poll_gap_s':max(f['max_poll_gap_s'] for f in result['flows'])}))
    sys.exit(0 if all(result['checks'].values()) else 1)
