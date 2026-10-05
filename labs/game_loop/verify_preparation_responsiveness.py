"""W2 bounded real source imports, saved-byte checks and eager/deferred parity."""
import argparse
import copy
import dataclasses
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for folder in ('game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT/folder))
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import pygame
from mecha_game.app import run, _EraBench
from mecha_game import campaign as api
from mecha_game.covenant import apply_covenant_change
from mecha_game.footer import FooterPager
from mecha_game.session import CompanionSession, load_session_inputs


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
        default=dataclasses.asdict).encode()).hexdigest()


def inventory(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and 'model_cache' not in p.parts}


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k, mod=0)


def interact(keeper, label, batches, screenshots):
    polls, flips, pages, spans, images, received = [], [], [], [], [], []
    original_flip, original_layout = pygame.display.flip, FooterPager.layout
    original_change = _EraBench.change_covenant
    original_poll = pygame.event.poll
    sequence = iter(batches)
    outer_count = 0
    def events():
        nonlocal outer_count
        outer_count += 1
        polls.append(time.perf_counter())
        if outer_count > len(batches)+2: raise AssertionError('Unbounded source flow')
        batch = next(sequence, [pygame.event.Event(pygame.QUIT)])
        return batch() if callable(batch) else batch
    def busy_poll():
        polls.append(time.perf_counter());event=original_poll()
        if event.type in (pygame.QUIT,pygame.KEYDOWN):received.append({'at':time.perf_counter(),'type':event.type,'key':getattr(event,'key',None)})
        return event
    def layout(self, lines, measure, width, rows):
        page = original_layout(self, lines, measure, width, rows)
        pages.append({'all':list(lines), 'visible':list(page.lines),
                      'fits':all(measure(s)<=width for s in page.lines)})
        return page
    def flip():
        flips.append(time.perf_counter()); original_flip()
        # Retain every state transition without an image-write delay in the measured gap.
        images.append(pygame.display.get_surface().copy())
    def change(self, operation):
        start=time.perf_counter()
        try:return original_change(self, operation)
        finally:spans.append(time.perf_counter()-start)
    with patch('pygame.event.get',events), patch('pygame.event.poll',busy_poll), patch('pygame.display.flip',flip), \
         patch.object(FooterPager,'layout',layout), patch.object(_EraBench,'change_covenant',change):
        code=run(['--keeper-dir',str(keeper),'--era-scale','session','--scale','1','--fps','0','--tick-frames','1'])
    paths=[]
    for index, surface in enumerate(images):
        path=screenshots/f'{label}-{index:02}.png';pygame.image.save(surface,str(path));paths.append(path.relative_to(ROOT).as_posix())
    return dict(label=label,code=code,pages=pages,frames=len(flips),screenshots=paths,import_s=spans,received=received,
        max_poll_gap_s=max((b-a for a,b in zip(polls,polls[1:])),default=0),
        max_frame_gap_s=max((b-a for a,b in zip(flips,flips[1:])),default=0))


def verify(fixtures, screenshots, eager_reference, bundle):
    fixtures.mkdir(parents=True,exist_ok=False);screenshots.mkdir(parents=True,exist_ok=True)
    paths=api.default_campaign_paths(ROOT)
    inputs=api.load_campaign_inputs(**paths,with_models=False)
    pet=load_session_inputs(ROOT/'data/seed_grids_16x16/mg_seed16_001_beetle.json',ROOT/'data/slips/valid/slip_v2_cleanliness.json')
    profile=json.loads((ROOT/'data/slips/valid/slip_lcd_seed.json').read_text())
    pack=json.loads((ROOT/'data/packs/mechagotchi_starter_pack.json').read_text())
    flows=[];checks={};launches=[];parity={};failed_writes=[]
    def seed(label,policy):
        keeper=fixtures/label;keeper.mkdir()
        c=api.KeeperCampaign(inputs);c.save(keeper/'campaign.sqlite3');c.save_state(keeper/'campaign_state.json')
        CompanionSession(pet[0],pet[1],model=pet[2],learning_policy=policy).save_checkpoint(keeper/'companion.json')
        return keeper
    def play(keeper,label,batches):
        row=interact(keeper,label,batches,screenshots);flows.append(row)
        checks[label+'_responsive']=row['max_poll_gap_s']<=.5 and row['max_frame_gap_s']<=.5
        checks[label+'_renders_and_exits']=row['code']==0 and all(p['fits'] for p in row['pages'])
        return row['pages']
    for policy in ('incumbent','qtable'):
        for count in (1,256):
            label=f'{policy}-import-{count}';keeper=seed(label,policy);inbox=keeper/'covenants';inbox.mkdir()
            for i in range(count):(inbox/f'choice_{i:03}.json').write_text(json.dumps(dict(profile,profile_id=f'choice_{i:03}')))
            before=inventory(keeper)
            pages=play(keeper,label,[[key(pygame.K_i)],[key(pygame.K_END)],[key(pygame.K_RETURN)],
                [key(pygame.K_RETURN),key(pygame.K_RETURN)],[key(pygame.K_ESCAPE),key(pygame.K_f)],
                [key(pygame.K_i)],[key(pygame.K_END)],[key(pygame.K_RETURN)],[key(pygame.K_ESCAPE)]])
            after=inventory(keeper);state=json.loads((keeper/'campaign_state.json').read_text())
            checks[label+'_chosen_and_reopened']=state['slip_profile']['profile_id']==f'choice_{count-1:03}' and 'Covenant imported' in ' '.join(pages[7]['all'])
            checks[label+'_pet_inbox_preserved']=all(before[p]==after[p] for p in before if p.startswith(('companion','lineage','covenants/')))
            checks[label+'_no_evolution_cache']=not (keeper/'model_cache').exists()
        label=policy+'-stale-invalid-retry';keeper=seed(label,policy);(keeper/'covenants').mkdir();selected=keeper/'covenants'/'choice.json'
        selected.write_text(json.dumps(profile));before=inventory(keeper)
        def stale():selected.write_text('{}');return [key(pygame.K_RETURN)]
        def valid():selected.write_text(json.dumps(profile));return [key(pygame.K_F5)]
        pages=play(keeper,label,[[key(pygame.K_i)],stale,[key(pygame.K_F5)],[key(pygame.K_RETURN)],
            valid,[key(pygame.K_RETURN)],[key(pygame.K_ESCAPE)]])
        checks[label+'_truthful_verdicts']=('changed since preview' in ' '.join(pages[1]['all']) and
            'authority rejects' in ' '.join(pages[3]['all']) and 'Covenant imported' in ' '.join(pages[5]['all']))
        checks[label+'_pet_preserved']=before['companion.json']==inventory(keeper)['companion.json']
        checks[label+'_no_evolution_cache']=not (keeper/'model_cache').exists()
        label=policy+'-write-retry';keeper=seed(label,policy);(keeper/'covenants').mkdir();selected=keeper/'covenants'/'choice.json';selected.write_text(json.dumps(profile))
        before=inventory(keeper);original_replace=os.replace;locked=[True];unchanged=[]
        def replace(source,destination):
            if Path(destination)==keeper/'campaign_state.json' and locked[0]:raise PermissionError('observed state write lock')
            return original_replace(source,destination)
        def retry():
            at_failure=inventory(keeper)
            changed=[p for p in before if at_failure.get(p)!=before[p]]
            added=sorted(set(at_failure)-set(before))
            backup_only=(added==['campaign_state.bak.json'] and at_failure['campaign_state.bak.json']==before['campaign_state.json'])
            failed_writes.append(dict(label=label,changed_existing=changed,added=added,backup_matches_prior_state=backup_only))
            unchanged.append(not changed and (not added or backup_only))
            locked[0]=False;return [key(pygame.K_RETURN)]
        with patch('mecha_game.session.os.replace',replace):
            pages=play(keeper,label,[[key(pygame.K_i)],[key(pygame.K_RETURN)],retry,[key(pygame.K_ESCAPE)]])
        checks[label+'_failed_then_retry']=all(unchanged) and 'Import not completed' in ' '.join(pages[1]['all']) and 'Covenant imported' in ' '.join(pages[2]['all'])
        checks[label+'_pet_preserved']=before['companion.json']==inventory(keeper)['companion.json']
        label=policy+'-pack-retry';keeper=seed(label,policy);(keeper/'packs').mkdir();(keeper/'packs'/'starter.json').write_text(json.dumps(pack))
        (keeper/'covenants').mkdir();conflict=keeper/'covenants'/f"pack_{pack['pack_id']}_{pack['slips'][0]['profile_id']}.json";conflict.write_text('{"owner":"keep"}')
        before=inventory(keeper);staged=[]
        def again():staged.append(inventory(keeper));return [key(pygame.K_RETURN)]
        pages=play(keeper,label,[[key(pygame.K_k)],[key(pygame.K_RETURN)],again,[key(pygame.K_ESCAPE)]])
        after=inventory(keeper)
        checks[label+'_conflict_and_repeat']=after==staged[0] and after[str(conflict.relative_to(keeper)).replace('\\','/')]==before[str(conflict.relative_to(keeper)).replace('\\','/')] and 'different content' in ' '.join(pages[1]['all']) and 'already staged' in ' '.join(pages[2]['all'])

        for close in (False,True):
            label=policy+('-cold-close' if close else '-cold-cancel');keeper=seed(label,policy)
            (keeper/'covenants').mkdir();(keeper/'covenants'/'choice.json').write_text(json.dumps(profile))
            before_work=[];posted=[];senders=[]
            import mecha_game.app as app
            original_prepare=app.prepare_campaign_models
            def prepare(*a,**kw):
                def request():
                    time.sleep(.1);posted.append(time.perf_counter())
                    pygame.event.post(pygame.event.Event(pygame.QUIT) if close else key(pygame.K_ESCAPE))
                sender=threading.Thread(target=request,name='bounded-preparation-probe');senders.append(sender);sender.start()
                return original_prepare(*a,**kw)
            def era():before_work.append(inventory(keeper));return [key(pygame.K_e)]
            with patch.object(app,'prepare_campaign_models',prepare):
                pages=play(keeper,label,[[key(pygame.K_i)],[key(pygame.K_RETURN)],[key(pygame.K_ESCAPE)],era])
            for sender in senders:sender.join()
            row=flows[-1];observed=[r['at'] for r in row['received'] if r['type']==pygame.QUIT or r['key']==pygame.K_ESCAPE]
            row['request_latency_s']=observed[0]-posted[0] if observed and posted else None
            checks[label+'_polled_cancel_promptly']=row['request_latency_s'] is not None and 0<=row['request_latency_s']<=.5
            checks[label+'_saved_inputs_unchanged']=before_work[0]==inventory(keeper)
            checks[label+'_loading_visible']=any('Loading models' in p['all'] for p in pages)
            checks[label+'_joined']=not any(t.name=='mechagotchi-era' for t in threading.enumerate())

    reference=json.loads(eager_reference.read_text())
    for scale,config in [('tiny',api.TINY_ERA_CONFIG),('session',api.ERA_CONFIG)]:
        options=dict(repair_epochs=6 if scale=='tiny' else 40,seed_limit=12 if scale=='tiny' else None)
        lightweight=api.load_campaign_inputs(**paths,**options,with_models=False)
        ready=api.prepare_campaign_models(lightweight,repair_epochs=options['repair_epochs'])
        campaign=api.KeeperCampaign(ready,era_config=config);era=campaign.advance_era('calm',record_original=True)
        row=dict(model_digests={k:digest(v) for k,v in ready.items()},era_sha256=digest(era),recording_sha256=digest(campaign.last_original_recording))
        checks[scale+'_matches_prechange_eager']=all(row[k]==reference[scale][k] for k in row)
        parity[scale]=row
        if scale=='session':
            verdict=apply_covenant_change(campaign,population=32,generations=12)
            checks['larger_budget_genuinely_earned']=verdict['ok']
            twin=copy.deepcopy(campaign);twin.inputs=api.load_campaign_inputs(**paths)
            large=campaign.advance_era('calm',record_original=True)
            other=twin.advance_era('calm',record_original=True)
            checks['earned_larger_eager_deferred_equal']=large==other and campaign.last_original_recording==twin.last_original_recording
            parity['larger']=dict(config=campaign.era_config,earned_budget=campaign.budget(),era_sha256=digest(large),recording_sha256=digest(campaign.last_original_recording))
    if bundle:
        exe=bundle/'Mechagotchi.exe';env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
        for policy in ('incumbent','qtable'):
            keeper=fixtures/('native-'+policy)
            for name,extra in [('new',['--new','--learning-policy',policy]),('resume-next-era',['--eras','1'])]:
                command=[str(exe),'--keeper-dir',str(keeper),'--era-scale','session','--ticks','1','--tick-frames','1','--fps','0',*extra]
                result=subprocess.run(command,cwd=fixtures,env=env,capture_output=True,text=True,timeout=180,**({'creationflags':subprocess.CREATE_NO_WINDOW} if os.name=='nt' else {}))
                launches.append(dict(policy=policy,label=name,command=command,returncode=result.returncode,stderr=result.stderr))
                checks['native_'+policy+'_'+name]=result.returncode==0 and CompanionSession.load(keeper/'companion.json').learning_policy==policy
        native_sha256=hashlib.sha256(exe.read_bytes()).hexdigest()
    else:native_sha256=None
    return dict(artifact_id='responsive_preparation_release_stage0',date='2026-10-05',checks=checks,flows=flows,parity=parity,
        native_launches=launches,native_sha256=native_sha256,failed_writes=failed_writes,source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ('game/src/mecha_game/app.py','game/src/mecha_game/campaign.py')},
        blocked_states=['Source pygame events and native process launches are separate; native keyboard/human usability unobserved.',
        'Bounded one/256-file and earned 32x12 observations; maximum scale unmeasured.','Published-SHA Windows/Ubuntu CI and remote executor setup remain separate.'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fixtures',type=Path,required=True);p.add_argument('--screenshots',type=Path,required=True)
    p.add_argument('--eager-reference',type=Path,required=True);p.add_argument('--bundle',type=Path);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    result=verify(args.fixtures.resolve(),args.screenshots.resolve(),args.eager_reference.resolve(),args.bundle.resolve() if args.bundle else None)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':all(result['checks'].values()),'checks':result['checks'],'flows':len(result['flows']),'frames':sum(r['frames'] for r in result['flows'])}))
    raise SystemExit(0 if all(result['checks'].values()) else 1)
