"""V1 actual saved-history browsing, native continuity and explicit historic limits."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import time
from contextlib import closing
from unittest.mock import patch

from verify_era_review import ROOT, CompanionSession, interact, inventory, key, pygame
from mecha_game.campaign import KeeperCampaign, TINY_ERA_CONFIG, load_campaign_inputs
from mecha_game.session import load_session_inputs
from mecha_game.original_recording import save_original_recording
from mecha_game.repertoire import RepertoireBrowser
from mecha_game.niche_history import CampaignStory, NicheHistory


def ctrl(value):
    return pygame.event.Event(pygame.KEYDOWN,key=value,mod=pygame.KMOD_CTRL)


def verify(bundle, fixtures, screenshots):
    if fixtures.exists():
        raise ValueError('Use a fresh fixture directory; prior observations are preserved.')
    fixtures.mkdir(parents=True)
    screenshots.mkdir(parents=True,exist_ok=True)
    executable=bundle/('Mechagotchi.exe' if os.name=='nt' else 'Mechagotchi')
    env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',PYTHONDONTWRITEBYTECODE='1')
    checks,launches,flows,observed={},[],[],{}
    inputs=load_campaign_inputs(ROOT/'data/seed_grids_16x16',ROOT/'data/slips/valid/slip_v2_cleanliness.json',
        ROOT/'data/readability_benchmark/adopted_readability_model.json',repair_epochs=6,seed_limit=12)
    grid,slip,model=load_session_inputs(ROOT/'data/seed_grids_16x16/mg_seed16_001_beetle.json',ROOT/'data/slips/valid/slip_v2_cleanliness.json')
    template=fixtures/'template';template.mkdir()
    predecessor=None; campaign_counts=[]
    for number in range(1,4):
        campaign=KeeperCampaign(inputs,campaign_id=f'campaign-{number:02d}',predecessor_campaign_id=predecessor,
            keeper_label=f'Saved Keeper {number}',era_config=TINY_ERA_CONFIG)
        recordings=[]
        for index in range(8):
            campaign.advance_era('calm' if index%2==0 else 'storm',record_original=True)
            recordings.append(campaign.last_original_recording)
        campaign.save(template/'campaign.sqlite3')
        for recording in recordings:save_original_recording(recording,template,template/'campaign.sqlite3')
        campaign_counts.append(dict(campaign_id=campaign.campaign['campaign_id'],predecessor=predecessor,
            eras=len(campaign.eras),elites=sum(len(e['elites']) for e in campaign.eras)))
        predecessor=campaign.campaign['campaign_id']
    campaign.save_state(template/'campaign_state.json')
    observed['fixture']=dict(campaigns=campaign_counts,scope='24 actual tiny eras, three explicit saved campaign links; deterministic seeds repeat by campaign, not an independent recurrence experiment.')

    def launch(keeper,label):
        command=[str(executable),'--keeper-dir',str(keeper),'--ticks','1','--tick-frames','1','--fps','0']
        result=subprocess.run(command,cwd=fixtures,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90,
            **({'creationflags':subprocess.CREATE_NO_WINDOW} if os.name=='nt' else {}))
        row=dict(label=label,command=command,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
        launches.append(row)
        if result.returncode or 'Traceback' in result.stderr:raise AssertionError(row)

    def play(keeper,label,events):
        with patch('mecha_game.campaign.evolve',side_effect=AssertionError('history must not evolve')), \
             patch('mecha_game.replay.live_cycle',side_effect=AssertionError('history must not reconstruct footage')):
            flow=interact(keeper,label,events,screenshots,scale=2)
        flows.append(flow);return flow['pages']

    for policy in ('incumbent','qtable'):
        keeper=fixtures/policy;shutil.copytree(template,keeper)
        CompanionSession(grid,slip,model=model,learning_policy=policy).save_checkpoint(keeper/'companion.json')
        ledger=(keeper/'campaign.sqlite3').read_bytes();state=(keeper/'campaign_state.json').read_bytes()
        launch(keeper,policy+'-resume-24-eras')
        checks[policy+'_native_resume_keeps_all_campaigns']=(ledger==(keeper/'campaign.sqlite3').read_bytes() and state==(keeper/'campaign_state.json').read_bytes())
        before=inventory(keeper)
        origin=RepertoireBrowser.load(keeper,campaign_id='campaign-02')
        started=time.perf_counter();history=NicheHistory.load(keeper,origin);elapsed=time.perf_counter()-started
        history.back();expected_campaign=history.campaign_id;expected_era=history.selected_era['era_index']
        pages=play(keeper,policy+'-story-and-niche',[[key(pygame.K_l)],[key(pygame.K_f)],
            [key(pygame.K_t)],[ctrl(pygame.K_LEFTBRACKET)],[key(pygame.K_b)],[key(pygame.K_n)],
            [key(pygame.K_COMMA)],[key(pygame.K_t)],[key(pygame.K_b)],[pygame.event.Event(pygame.QUIT)]])
        texts=[' '.join(p['all_lines']) for p in pages]
        checks[policy+'_story_archive_niche_report_connect']=(
            'campaign-02' in texts[3] and 'campaign-02' in texts[4] and 'NICHE HISTORY' in texts[5] and
            expected_campaign in texts[6] and f'ERA {expected_era} ' in texts[7] and expected_campaign in texts[7] and
            'REPERTOIRE' in texts[8] and expected_campaign in texts[8])
        checks[policy+'_story_and_history_preserve_all_saved_bytes']=before==inventory(keeper)
        checks[policy+'_history_labels_limits_and_occurrences']=('historical calibration is not recorded' in texts[5] and
            len(history.eras)>=3 and all(e['elites'][0]['descriptor']['values']==list(history.niche) for e in history.eras))
        observed[policy+'_history']=dict(occurrences=len(history.eras),load_seconds=elapsed,selected_niche=list(history.niche),
            selected_campaign=expected_campaign,selected_era=expected_era)

        browser=RepertoireBrowser.load(keeper)
        best=max(browser.elites,key=lambda e:(e['fitness'],e['niche_key']));position=browser.elites.index(best)
        events=[[key(pygame.K_b)]]+[[key(pygame.K_PERIOD)]]*position
        at=len(events)
        events += [[key(pygame.K_n)],[key(pygame.K_v)],[key(pygame.K_F1)],[key(pygame.K_ESCAPE)],
                   [key(pygame.K_v)],[key(pygame.K_n)],[pygame.event.Event(pygame.QUIT)]]
        pages=play(keeper,policy+'-history-playback',events)
        checks[policy+'_original_replay_and_return_from_history']=(
            pages[at]['all_lines'][0].startswith('NICHE HISTORY') and 'Original era evaluation' in ' '.join(pages[at+1]['all_lines']) and
            pages[at+4]['all_lines']==pages[at]['all_lines'] and pages[at+5]['all_lines'][0].startswith('REPERTOIRE') and
            best['grid_id'] in ' '.join(pages[at+5]['all_lines']))
        checks[policy+'_playback_preserves_all_saved_bytes']=before==inventory(keeper)

        selected=NicheHistory.load(keeper,RepertoireBrowser.load(keeper));selected.back();expected=selected.current()['grid']
        pages=play(keeper,policy+'-history-adoption',[[key(pygame.K_b)],[key(pygame.K_n)],[key(pygame.K_COMMA)],
            [key(pygame.K_a)],[pygame.event.Event(pygame.QUIT)]])
        pet=CompanionSession.load(keeper/'companion.json')
        checks[policy+'_historical_adoption_keeps_active_campaign_and_policy']=(pet.grid==expected and pet.learning_policy==policy and
            pet.lineage[-1]['origin']=='era_elite' and ledger==(keeper/'campaign.sqlite3').read_bytes() and state==(keeper/'campaign_state.json').read_bytes())
        launch(keeper,policy+'-resume-adopted-history')
        pet=CompanionSession.load(keeper/'companion.json')
        checks[policy+'_native_resumes_historical_adoption']=pet.grid==expected and pet.learning_policy==policy

    keeper=fixtures/'incomplete-history';shutil.copytree(fixtures/'incumbent',keeper)
    with closing(sqlite3.connect(keeper/'campaign.sqlite3')) as conn:
        conn.execute('UPDATE campaigns SET predecessor_campaign_id=? WHERE campaign_id=?',('missing-campaign','campaign-01'))
        conn.execute('DELETE FROM elites WHERE campaign_id=? AND era_index=0',('campaign-02',))
        for era,niche,blob in conn.execute('SELECT era_index,niche_key,elite_json FROM elites WHERE campaign_id=?',('campaign-01',)).fetchall():
            row=json.loads(blob);row['descriptor']['names']=['incompatible-historic-axes']
            conn.execute('UPDATE elites SET elite_json=? WHERE campaign_id=? AND era_index=? AND niche_key=?',(json.dumps(row),'campaign-01',era,niche))
        conn.commit()
    before=inventory(keeper)
    pages=play(keeper,'incomplete-history',[[key(pygame.K_b)],[key(pygame.K_n)],[key(pygame.K_PAGEDOWN)],
        [key(pygame.K_PAGEDOWN)],[key(pygame.K_t)],[ctrl(pygame.K_LEFTBRACKET)],
        [ctrl(pygame.K_LEFTBRACKET)],[ctrl(pygame.K_LEFTBRACKET)],[key(pygame.K_PAGEDOWN)],[ctrl(pygame.K_RIGHTBRACKET)],
        [pygame.event.Event(pygame.QUIT)]])
    texts=[' '.join(p['all_lines']) for p in pages]
    checks['incomplete_records_visible_while_valid_occurrences_remain']=all(s in texts[1].lower() for s in ['incompatible','missing','campaign-01','campaign-02']) and 'NICHE HISTORY' in texts[1]
    checks['missing_campaign_link_visible_and_returnable']='missing-campaign' in texts[7] and 'unavailable' in texts[7].lower() and 'ERA ' in texts[9] and 'Recorded predecessor: not recorded' in texts[7]
    checks['unavailable_campaign_details_can_be_paged']='Recorded predecessor: not recorded' in ' '.join(pages[8]['visible'])
    checks['incomplete_history_never_rewritten']=before==inventory(keeper)
    checks['all_source_flows_exit_and_fit']=all(f['returncode']==0 and all(p['fits'] for p in f['pages']) for f in flows)
    return dict(artifact_id='recorded_niche_history_release_stage0',date='2026-10-04',status='observed_source_and_native',
        purpose='Exact saved seven-axis niche history and recorded predecessor-campaign navigation, without family or ancestry inference.',
        source_artifacts=['game/src/mecha_game/niche_history.py','game/src/mecha_game/app.py','labs/game_loop/verify_niche_history.py'],
        metrics=dict(checks=checks,launches=launches,interactive=flows,observed=observed,native_executable_sha256=hashlib.sha256(executable.read_bytes()).hexdigest()),
        closed_states=[k for k,v in checks.items() if v],
        blocked_states=['Native keyboard/human usability unobserved; native subprocesses use SDL dummy and source pygame consumes actual events.',
            'Matching bin labels do not establish unrecorded historical calibration equivalence or biological relationships.',
            'Only the active campaign and recorded predecessor chain are searched; unlinked campaigns are not inferred.',
            '24 tiny eras across three linked campaigns tested, not arbitrary/maximal histories.',
            'Full local gate and exact-published-SHA CI are separate; hosted sharing/signing excluded.'],
        decision=dict(verdict='verified' if all(checks.values()) else 'withhold'))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('bundle','fixtures','screenshots','output'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();report=verify(args.bundle.resolve(),args.fixtures.resolve(),args.screenshots.resolve())
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(checks=report['metrics']['checks'],launches=len(report['metrics']['launches']),flows=len(report['metrics']['interactive'])),indent=2))
    raise SystemExit(0 if report['decision']['verdict']=='verified' else 1)
