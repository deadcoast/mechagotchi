"""W3 real source interaction, complete trace parity and separate native launches."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
for folder in ('game/src','packages/mecha_engine/src'):
    sys.path.insert(0,str(ROOT/folder))
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import pygame
from mecha_game.app import run, _EraBench
from mecha_game.campaign import KeeperCampaign, default_campaign_paths, load_campaign_inputs
from mecha_game.session import CompanionSession,load_session_inputs
from mecha_game.footer import FooterPager
from mecha_game.generation_view import GenerationView
from mecha_game.hatchery import hatch_founders
from mecha_engine.generation import explain_generation

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def inventory(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
def key(k,mod=0):
    return pygame.event.Event(pygame.KEYDOWN,key=k,mod=mod)

def interact(keeper,label,batches,screenshots):
    polls=[];frames=[];pages=[];sequence=iter(batches);packets=[];images=[]
    original_layout,original_flip,original_packet=FooterPager.layout,pygame.display.flip,GenerationView.packet
    def events():
        polls.append(time.perf_counter())
        if len(polls)>len(batches)+2:raise AssertionError('Unbounded interaction')
        batch=next(sequence,[pygame.event.Event(pygame.QUIT)])
        return batch() if callable(batch) else batch
    def layout(self,lines,measure,width,rows):
        page=original_layout(self,lines,measure,width,rows)
        pages.append({'all':list(lines),'visible':list(page.lines),'page':page.page,'pages':page.page_count,
                      'fits':all(measure(s)<=width for s in page.lines)})
        return page
    def flip():
        frames.append(time.perf_counter());original_flip()
        # Keep pixels out of timing's file-I/O path. Capture only useful pages.
        if len(pages)<=10 or pages[-1]['page']==pages[-1]['pages']-1:
            images.append((len(pages)-1,pygame.display.get_surface().copy()))
    def packet(self):
        result=original_packet(self)
        if result is not None:packets.append({'grid':digest(self.grid),'trace':digest(self.explanation),'animation':result['animation']})
        return result
    with patch('pygame.event.get',events),patch('pygame.display.flip',flip),patch.object(FooterPager,'layout',layout),patch.object(GenerationView,'packet',packet):
        code=run(['--keeper-dir',str(keeper),'--era-scale','session','--scale','16','--fps','0','--tick-frames','1'])
    paths=[]
    for index,surface in images:
        path=screenshots/f'{label}-{index:02}.png';pygame.image.save(surface,str(path));paths.append(path.resolve().relative_to(ROOT).as_posix())
    return {'label':label,'code':code,'frames':len(frames),'pages':pages,'packets':packets,'screenshots':paths,
            'max_poll_gap_s':max((b-a for a,b in zip(polls,polls[1:])),default=0),
            'max_frame_gap_s':max((b-a for a,b in zip(frames,frames[1:])),default=0)}

def verify(fixtures,screenshots,bundle):
    fixtures.mkdir(parents=True,exist_ok=False);screenshots.mkdir(parents=True,exist_ok=True)
    inputs=load_campaign_inputs(**default_campaign_paths(ROOT),with_models=False)
    pet=load_session_inputs(ROOT/'data/seed_grids_16x16/mg_seed16_001_beetle.json',ROOT/'data/slips/valid/slip_v2_cleanliness.json')
    profile=json.loads((ROOT/'data/slips/valid/slip_lcd_seed.json').read_text())
    flows=[];checks={};launches=[];adopted={}
    def seed(label,policy):
        keeper=fixtures/label;keeper.mkdir()
        campaign=KeeperCampaign(inputs);campaign.save(keeper/'campaign.sqlite3');campaign.save_state(keeper/'campaign_state.json')
        CompanionSession(pet[0],pet[1],model=pet[2],learning_policy=policy).save_checkpoint(keeper/'companion.json')
        return keeper
    def play(keeper,label,batches):
        row=interact(keeper,label,batches,screenshots);flows.append(row)
        checks[label+'_renders_and_exits']=row['code']==0 and all(p['fits'] for p in row['pages'])
        return row
    for policy in ('incumbent','qtable'):
        label=policy+'-cancel';keeper=seed(label,policy);before=inventory(keeper)
        row=play(keeper,label,[[key(pygame.K_h)],[key(pygame.K_SPACE)],[],[key(pygame.K_RIGHTBRACKET)],
             [key(pygame.K_F1)],[],[key(pygame.K_ESCAPE)],[key(pygame.K_PAGEDOWN)],[key(pygame.K_ESCAPE),key(pygame.K_f),key(pygame.K_RETURN)]])
        checks[label+'_all_bytes_unchanged']=before==inventory(keeper)
        checks[label+'_real_animation']=len({digest(p['animation']) for p in row['packets']})>1
        checks[label+'_one_candidate_trace']=len({p['trace'] for p in row['packets']})==1
        checks[label+'_cold_gap_under_half_second']=row['max_poll_gap_s']<=.5

        label=policy+'-import-adopt';keeper=seed(label,policy);(keeper/'covenants').mkdir();selected=keeper/'covenants'/'chosen.json';selected.write_text(json.dumps(profile))
        before=inventory(keeper);unchanged=[]
        def adopt():
            unchanged.append(inventory(keeper)['companion.json']==before['companion.json'])
            return [key(pygame.K_RETURN),key(pygame.K_RETURN),key(pygame.K_f)]
        row=play(keeper,label,[[key(pygame.K_i)],[key(pygame.K_RETURN)],[key(pygame.K_ESCAPE)],[key(pygame.K_h)],
             [key(pygame.K_PERIOD)],[key(pygame.K_PAGEDOWN)],[key(pygame.K_PAGEDOWN)],adopt])
        saved=CompanionSession.load(keeper/'companion.json');expected=hatch_founders(inputs['seed_grids'],profile,rng_seed=20260714)[0]
        checks[label+'_adoption_explicit']=all(unchanged) and saved.state['age_ticks']==0
        checks[label+'_engine_grid_trace_exact']=saved.grid==expected['grid'] and explain_generation(saved.grid)==expected['explanation']
        checks[label+'_policy_and_imported_covenant']=saved.learning_policy==policy and saved.slip_profile==profile
        checks[label+'_inbox_unchanged']=inventory(keeper)['covenants/chosen.json']==before['covenants/chosen.json']
        checks[label+'_no_evolution_cache']=not (keeper/'model_cache').exists()
        adopted[policy]={'grid_sha256':digest(saved.grid),'trace_sha256':digest(explain_generation(saved.grid))}
        before=inventory(keeper);view=GenerationView(saved.grid,saved.slip_profile)
        row=play(keeper,policy+'-reopen-origin',[[key(pygame.K_o)],[key(pygame.K_RETURN)],[key(pygame.K_n)]]+
                 [[key(pygame.K_PAGEDOWN)] for _ in range(70)]+[[key(pygame.K_ESCAPE)]])
        checks[policy+'_origin_all_bytes_unchanged']=before==inventory(keeper)
        checks[policy+'_origin_complete_fields']=all(line in row['pages'][0]['all'] for line in view._trace_lines)
        checks[policy+'_origin_last_page_reached']=any(p['page']==p['pages']-1 for p in row['pages'][:-1])
        checks[policy+'_origin_exact_trace']=all(p['trace']==adopted[policy]['trace_sha256'] for p in row['packets'])
        for action in ('load','resume'):
            command=[str(bundle),'--keeper-dir',str(keeper),'--ticks','1','--tick-frames','1','--fps','0','--scale','1']
            start=time.perf_counter();result=subprocess.run(command,capture_output=True,text=True,timeout=90)
            current=CompanionSession.load(keeper/'companion.json')
            launches.append({'policy':policy,'action':action,'returncode':result.returncode,'seconds':time.perf_counter()-start,
                            'stdout':result.stdout,'stderr':result.stderr,'age_ticks':current.state['age_ticks']})
            checks[policy+'_native_'+action]=result.returncode==0 and current.grid==expected['grid'] and current.learning_policy==policy and explain_generation(current.grid)==expected['explanation']

        label=policy+'-missing-origin';keeper=seed(label,policy);before=inventory(keeper)
        row=play(keeper,label,[[key(pygame.K_o)],[key(pygame.K_RETURN)],[key(pygame.K_n)],[key(pygame.K_ESCAPE)]])
        checks[label+'_honest_read_only']='unavailable' in ' '.join(row['pages'][0]['all']) and before==inventory(keeper)

        label=policy+'-save-retry';keeper=seed(label,policy);before=inventory(keeper);locked=[True];observed=[];original=CompanionSession.save_checkpoint
        def save(session,path):
            if locked[0] and session.grid['grid_id'].startswith('mg_constrained'):raise PermissionError('demonstration checkpoint lock')
            return original(session,path)
        def retry():
            observed.append(inventory(keeper)['companion.json']==before['companion.json']);locked[0]=False
            return [key(pygame.K_s,pygame.KMOD_CTRL),key(pygame.K_o)]
        with patch.object(CompanionSession,'save_checkpoint',save):
            row=play(keeper,label,[[key(pygame.K_h)],[key(pygame.K_RETURN)],[key(pygame.K_f)],retry])
        checks[label+'_previous_primary_retained']=all(observed)
        checks[label+'_failure_then_origin']='Save failed' in ' '.join(row['pages'][1]['all']) and 'ORIGIN TRACE' in ' '.join(row['pages'][3]['all'])
        checks[label+'_no_time_leak']=CompanionSession.load(keeper/'companion.json').state['age_ticks']==0
    sources=['game/src/mecha_game/app.py','game/src/mecha_game/generation_view.py','game/src/mecha_game/footer.py','game/tests/test_hatch_preview.py', 'labs/game_loop/verify_hatch_preview.py']
    return {'artifact_id':'hatch_preview_release_stage0','date':'2026-10-05','checks':checks,'flows':flows,'native_launches':launches,'adopted':adopted,
            'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},'native_sha256':hashlib.sha256(bundle.read_bytes()).hexdigest(),
            'boundaries':['Source pygame keys/rendering observed; native process launches separately observed; native keyboard unobserved.',
                'No WFC collapse/restart events are available. Existing constrained trace is consumed verbatim.',
                'No remote executor configured; published-SHA Windows/Ubuntu CI unmet.']}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixtures',type=Path,required=True);parser.add_argument('--screenshots',type=Path,required=True)
    parser.add_argument('--bundle',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=verify(args.fixtures,args.screenshots,args.bundle.resolve())
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'checks':len(result['checks']),'failed':[k for k,v in result['checks'].items() if not v],
                      'source_flows':len(result['flows']),'frames':sum(f['frames'] for f in result['flows']),'native_launches':len(result['native_launches']),
                      'max_poll_gap_s':max(f['max_poll_gap_s'] for f in result['flows'])}))
    sys.exit(0 if all(result['checks'].values()) else 1)
