"""W1 actual starter-pack imports, paused source interactions and native continuity."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from unittest.mock import patch

from verify_era_review import ROOT, CompanionSession, EraReview, interact, inventory, key, pygame
from mecha_game.inbox import InboxPicker
from mecha_game.packs import write_pack


def verify(bundle, fixtures, screenshots):
    if fixtures.exists():
        raise ValueError('Use a fresh fixture directory; preserve prior observations.')
    fixtures.mkdir(parents=True)
    screenshots.mkdir(parents=True,exist_ok=True)
    executable=bundle/('Mechagotchi.exe' if os.name=='nt' else 'Mechagotchi')
    env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',PYTHONDONTWRITEBYTECODE='1')
    checks,launches,flows,observed={},[],[],{}
    example=ROOT/'data/packs/mechagotchi_starter_pack.json'
    pack=json.loads(example.read_text(encoding='utf-8'))
    profile=next(s for s in pack['slips'] if s['profile_id']=='slip_lcd_seed')

    def launch(keeper,label,*extra):
        command=[str(executable),'--keeper-dir',str(keeper),'--ticks','1','--tick-frames','1','--fps','0','--era-scale','tiny',*extra]
        result=subprocess.run(command,cwd=fixtures,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120,
            **({'creationflags':subprocess.CREATE_NO_WINDOW} if os.name=='nt' else {}))
        row=dict(label=label,command=command,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
        launches.append(row)
        if result.returncode or 'Traceback' in result.stderr:raise AssertionError(row)

    def play(keeper,label,events,*,scale=2):
        flow=interact(keeper,label,events,screenshots,scale=scale)
        flows.append(flow);return flow['pages']

    for policy in ('incumbent','qtable'):
        keeper=fixtures/policy
        launch(keeper,policy+'-new','--new','--learning-policy',policy,'--eras','1')
        history=EraReview.load(keeper).history
        (keeper/'packs').mkdir()
        shutil.copyfile(example,keeper/'packs'/'starter_choices.json')
        before=inventory(keeper)
        with patch('mecha_game.app.load_campaign_inputs',side_effect=AssertionError('browsing must not load models')):
            pages=play(keeper,policy+'-browse-cancel',[[key(pygame.K_k)],[key(pygame.K_f),key(pygame.K_e)],
                [key(pygame.K_F1)],[key(pygame.K_ESCAPE)],[key(pygame.K_ESCAPE)],
                [key(pygame.K_i)],[key(pygame.K_ESCAPE)],[pygame.event.Event(pygame.QUIT)]])
        checks[policy+'_browse_cancel_and_help_preserve_all_files']=before==inventory(keeper)
        checks[policy+'_active_inbox_help_is_specific']='F5 refresh' in ' '.join(pages[2]['visible']) and 'F feed' not in ' '.join(pages[2]['visible'])
        checks[policy+'_named_pack_and_empty_inbox_visible']=('starter_choices.json' in ' '.join(pages[0]['visible']) and
            pages[0]['all_lines']==pages[3]['all_lines'] and 'No JSON files' in ' '.join(pages[5]['visible']))
        pet=(keeper/'companion.json').read_bytes()
        pages=play(keeper,policy+'-stage-starter',[[key(pygame.K_k)],[key(pygame.K_RETURN)],
            [key(pygame.K_PAGEDOWN)],[key(pygame.K_PAGEDOWN)],[pygame.event.Event(pygame.QUIT)]])
        checks[policy+'_starter_pack_all_items_staged']=('4/4 covenants; 4/4 creatures ready.' in ' '.join(pages[1]['all_lines']) and
            len(list((keeper/'covenants').glob('*.json')))==4 and len(list((keeper/'released').glob('*.json')))==4)
        checks[policy+'_completed_import_action_is_clear']='import complete' in ' '.join(pages[1]['visible']) and 'Enter imports' not in ' '.join(pages[1]['visible'])
        picker=InboxPicker(keeper,'covenant')
        position=next(i for i,p in enumerate(picker.files) if p.name.endswith('_slip_lcd_seed.json'))
        events=[[key(pygame.K_i)]]+[[key(pygame.K_PERIOD)]]*position
        selected_at=len(events)-1
        events += [[key(pygame.K_F1)],[key(pygame.K_ESCAPE)],[key(pygame.K_RETURN)],
                   [key(pygame.K_RETURN)],[pygame.event.Event(pygame.QUIT)]]
        pages=play(keeper,policy+'-choose-covenant',events,scale=24)
        checks[policy+'_selected_named_covenant_imported']=('slip_lcd_seed' in ' '.join(pages[selected_at]['all_lines']) and
            'Covenant imported' in ' '.join(pages[selected_at+3]['visible']))
        checks[policy+'_import_and_duplicate_enter_preserve_pet']=pet==(keeper/'companion.json').read_bytes()
        state=json.loads((keeper/'campaign_state.json').read_text(encoding='utf-8'))
        checks[policy+'_import_changes_future_covenant_not_historical_era']=state['base_profile']==profile and EraReview.load(keeper).history['eras']==history['eras']
        pages=play(keeper,policy+'-prepare-restart',[[key(pygame.K_t)],[key(pygame.K_w)],
            [pygame.event.Event(pygame.QUIT)]])
        staged=json.loads((keeper/'era_plan.json').read_text(encoding='utf-8'))['releases']
        launch(keeper,policy+'-resume-next-era','--eras','1')
        after=EraReview.load(keeper).history
        checks[policy+'_native_next_era_uses_imported_covenant_and_keeps_history']=(len(after['eras'])==2 and
            after['eras'][0]==history['eras'][0] and after['eras'][1]['slip_profile']==profile)
        checks[policy+'_native_resume_keeps_policy']=CompanionSession.load(keeper/'companion.json').learning_policy==policy
        founders=after['eras'][-1]['report']['founders']
        checks[policy+'_staged_creatures_receive_real_era_verdicts']=bool(staged) and bool(founders['admitted_ids']) and bool(founders['rejected'])
        before=inventory(keeper)
        pages=play(keeper,policy+'-restarted-archive',[[key(pygame.K_t)],[key(pygame.K_b)],
            [key(pygame.K_n)],[key(pygame.K_ESCAPE)],[pygame.event.Event(pygame.QUIT)]])
        checks[policy+'_new_history_connects_to_archive_and_niche_without_writes']=('NICHE HISTORY' in ' '.join(pages[2]['visible']) and before==inventory(keeper))
        observed[policy]={'selected_file':picker.files[position].name,'imported_profile':profile['profile_id'],
            'staged_count':len(staged),'founders':founders,'era_count':len(after['eras'])}

    keeper=fixtures/'mixed-refusals';shutil.copytree(fixtures/'incumbent',keeper)
    invalid=copy.deepcopy(pack);invalid['pack_id']='mixed';invalid['slips'][0]['slip_version']='9.9.9'
    write_pack(invalid,keeper/'packs'/'aaa_mixed.json')
    pages=play(keeper,'mixed-refusals',[[key(pygame.K_k)],[key(pygame.K_RETURN)]]+
        [[key(pygame.K_PAGEDOWN)]]*5+[[pygame.event.Event(pygame.QUIT)]])
    checks['mixed_pack_retains_full_refusal_and_valid_items']=('3/4 covenants; 4/4 creatures ready.' in ' '.join(pages[1]['all_lines']) and
        any('slip_version must be one of' in ' '.join(p['visible']) for p in pages[2:]))
    keeper=fixtures/'long-invalid';shutil.copytree(fixtures/'qtable',keeper)
    long_name='a_unreadable_'*14+'.json';(keeper/'covenants'/long_name).write_bytes(b'\xff')
    before=inventory(keeper)
    pages=play(keeper,'long-invalid',[[key(pygame.K_i)],[key(pygame.K_RETURN)],
        [key(pygame.K_PAGEDOWN)],[key(pygame.K_PAGEDOWN)],[key(pygame.K_F1)],[key(pygame.K_ESCAPE)],
        [key(pygame.K_DOWN)],[key(pygame.K_HOME)],[pygame.event.Event(pygame.QUIT)]])
    checks['long_filename_keeps_unreadable_notice_on_first_page']='File unreadable' in ' '.join(pages[0]['visible']) and 'Enter imports' not in ' '.join(pages[0]['visible'])
    checks['invalid_file_has_full_name_and_recovery_without_writes']=('unreadable' in ' '.join(pages[0]['all_lines']) and
        long_name in ' '.join(pages[0]['all_lines']) and before==inventory(keeper))
    checks['all_source_flows_exit_and_fit']=all(f['returncode']==0 and all(p['fits'] for p in f['pages']) for f in flows)
    return dict(artifact_id='import_inboxes_release_stage0',date='2026-10-05',status='observed_source_and_native',
        purpose='Connect the existing starter pack, named covenant choice and durable next-era preparation.',
        source_artifacts=['data/packs/mechagotchi_starter_pack.json','game/src/mecha_game/inbox.py',
            'game/src/mecha_game/covenant_io.py','game/src/mecha_game/packs.py','labs/game_loop/verify_import_inboxes.py'],
        metrics=dict(checks=checks,launches=launches,interactive=flows,observed=observed,
            native_executable_sha256=hashlib.sha256(executable.read_bytes()).hexdigest(),
            source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ('game/src/mecha_game/app.py','game/src/mecha_game/inbox.py','game/src/mecha_game/covenant_io.py','game/src/mecha_game/packs.py')}),
        closed_states=[k for k,v in checks.items() if v],
        blocked_states=['Native keyboard/human usability unobserved: native SDL-dummy processes and source pygame events are distinct.',
            'Bounded starter-pack and long-file observations, not maximum-size import performance.',
            'Exact-published-SHA Windows/Ubuntu CI remains unverified.'],
        decision={'verdict':'verified' if all(checks.values()) else 'withhold'},
        next_research_step='Finish preservation, visual/diff review and focused/full local gates before local closure.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',type=Path,required=True);parser.add_argument('--fixtures',type=Path,required=True)
    parser.add_argument('--screenshots',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();report=verify(args.bundle.resolve(),args.fixtures.resolve(),args.screenshots.resolve())
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'checks':report['metrics']['checks'],'native_launches':len(report['metrics']['launches']),
        'source_flows':len(report['metrics']['interactive']),'frames':sum(f['rendered_frames'] for f in report['metrics']['interactive'])}))
    raise SystemExit(0 if all(report['metrics']['checks'].values()) else 1)
