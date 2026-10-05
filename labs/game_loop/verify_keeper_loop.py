"""T4: actual connected Keeper preparation, execution, collection and recovery."""
import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch
from verify_era_review import ROOT, CompanionSession, EraReview, interact, inventory, key, pygame
from mecha_game.campaign import ERA_SEED_STRIDE
from mecha_game.recorded_review import load_saved_replay
from mecha_game.repertoire import RepertoireBrowser


def verify(bundle, screenshots, legacy_bundle=None):
    executable=bundle/('Mechagotchi.exe' if os.name=='nt' else 'Mechagotchi')
    env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',PYTHONDONTWRITEBYTECODE='1')
    screenshots.mkdir(parents=True,exist_ok=True)
    checks,launches,flows,observed={},{},[],{}
    with tempfile.TemporaryDirectory(prefix='mechagotchi-keeper-loop-') as directory:
        root=Path(directory)
        def launch(keeper,label,*extra,expected=0):
            command=[str(executable),'--keeper-dir',str(keeper),'--ticks','1','--tick-frames','1','--fps','0','--era-scale','tiny',*extra]
            result=subprocess.run(command,cwd=root,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90,
                **({'creationflags':subprocess.CREATE_NO_WINDOW} if os.name=='nt' else {}))
            launches[label]=dict(command=command,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
            if result.returncode!=expected or 'Traceback' in result.stderr:raise AssertionError(launches[label])
        def play(keeper,label,events):
            flow=interact(keeper,label,events,screenshots,scale=2);flows.append(flow);return flow['pages']
        for policy in ('incumbent','qtable'):
            keeper=root/policy
            launch(keeper,policy+'-create','--new','--eras','1','--learning-policy',policy)
            pet=CompanionSession.load(keeper/'companion.json');original_id=pet.grid['grid_id']
            first=EraReview.load(keeper).current
            pages=play(keeper,policy+'-prepare',[[key(pygame.K_t)],[key(pygame.K_r)],[key(pygame.K_r)],
                [key(pygame.K_3)],[key(pygame.K_c)],[key(pygame.K_3)],[key(pygame.K_t)],[pygame.event.Event(pygame.QUIT)]])
            plan=json.loads((keeper/'era_plan.json').read_text());state=json.loads((keeper/'campaign_state.json').read_text())
            checks[policy+'_weather_and_single_contribution_persist_from_report']=(plan['weather']=='storm' and
                [g['grid_id'] for g in plan['releases']]==[original_id] and 'NEXT ERA [storm]: 1 staged' in ' '.join(pages[3]['all_lines']))
            checks[policy+'_earned_covenant_spend_persisted_with_original_base']=(state['era_config']['population']==12 and state['base_parameters']['population']==6)
            before_plan=(keeper/'era_plan.json').read_bytes();before_state=(keeper/'campaign_state.json').read_bytes()
            launch(keeper,policy+'-resume')
            checks[policy+'_native_resume_keeps_preparation_and_covenant']=(before_plan==(keeper/'era_plan.json').read_bytes() and before_state==(keeper/'campaign_state.json').read_bytes())
            pages=play(keeper,policy+'-connected-loop',[[key(pygame.K_t)],[key(pygame.K_e)],[key(pygame.K_v)],
                [key(pygame.K_SPACE)],[key(pygame.K_PERIOD)],[key(pygame.K_t)],[key(pygame.K_b)],
                [key(pygame.K_a)],[key(pygame.K_r)],[key(pygame.K_t)],[key(pygame.K_1)],[pygame.event.Event(pygame.QUIT)]])
            history=EraReview.load(keeper).history;era=history['eras'][-1]
            adopted=CompanionSession.load(keeper/'companion.json')
            checks[policy+'_prepared_storm_runs_once_and_shows_real_admission']=(len(history['eras'])==2 and era['weather']['forecast']=='storm' and
                original_id in era['report']['founders']['admitted_ids'] and 'ADMITTED: '+original_id in ' '.join(pages[1]['all_lines']))
            checks[policy+'_report_replay_archive_adoption_and_next_contribution_connect']=(pages[2]['all_lines'][0].startswith('REVIEW ERA 1') and
                adopted.lineage[-1]['origin']=='era_elite' and adopted.learning_policy==policy and
                json.loads((keeper/'era_plan.json').read_text())['releases'][0]==adopted.grid)
            checks[policy+'_recording_is_original_era_evaluation']='Original era evaluation' in ' '.join(pages[2]['all_lines'])
            launch(keeper,policy+'-run-prepared-next','--eras','1')
            after=EraReview.load(keeper).history;last=after['eras'][-1]
            checks[policy+'_adopted_creature_enters_next_native_era_without_repeating_prior_release']=(len(after['eras'])==3 and last['weather']['forecast']=='calm' and
                adopted.grid['grid_id'] in last['report']['founders']['admitted_ids'] and last['rng_seed']==first['rng_seed']+2*ERA_SEED_STRIDE and
                json.loads((keeper/'era_plan.json').read_text())['releases']==[])
            checks[policy+'_previous_recorded_reports_preserved']=after['eras'][0]['report']==first['report'] and after['eras'][1]==era
            before=inventory(keeper)
            pages=play(keeper,policy+'-review-after-restart',[[key(pygame.K_t)],[key(pygame.K_LEFTBRACKET)],[key(pygame.K_v)],
                [key(pygame.K_F1)],[key(pygame.K_F1)],[key(pygame.K_t)],[key(pygame.K_b)],[key(pygame.K_ESCAPE)],
                [pygame.event.Event(pygame.QUIT)]])
            checks[policy+'_history_archive_replay_stay_read_only_after_native_execution']=before==inventory(keeper) and pages[2]['all_lines'][0].startswith('REVIEW ERA 1')
            browser = RepertoireBrowser.load(keeper)
            best = max(browser.elites, key=lambda e: (e['fitness'], e['niche_key']))
            replay = load_saved_replay(keeper, after['campaign_id'], last['era_index'], expected_seed=last['rng_seed'], selected_elite=best)
            origin = replay['evaluation']
            creature = last['report']['generations'][origin['generation_index']]['creatures'][origin['candidate_index']]
            checks[policy+'_native_capture_preserves_actual_candidate_seed_weather_and_cycles'] = (
                origin['final_grid'] == best['grid'] and origin['original_grid']['grid_id'] == creature['candidate_grid_id'] and
                replay['live']['cycles'] == creature['cycles'] and
                replay['parameters']['rng_seed'] == last['rng_seed'] + origin['generation_index'] * 100000 + origin['candidate_index'])
            position = browser.elites.index(best)
            events = [[key(pygame.K_b)]] + [[key(pygame.K_PERIOD)]] * position
            opened = len(events)
            pages = play(keeper, policy+'-original-archive-playback', events + [[key(pygame.K_v)], [key(pygame.K_SPACE)],
                [key(pygame.K_PERIOD)], [key(pygame.K_F1)], [key(pygame.K_ESCAPE)], [key(pygame.K_v)], [pygame.event.Event(pygame.QUIT)]])
            checks[policy+'_selected_original_replay_returns_to_archive_without_writes'] = (
                pages[opened]['all_lines'][0].startswith('REVIEW ERA 2') and
                'Original era evaluation' in ' '.join(pages[opened]['all_lines']) and
                pages[opened+5]['all_lines'][0].startswith('REPERTOIRE') and before == inventory(keeper))
            other = 1 if position == 0 else 0
            assert len(browser.elites) > 1, 'fixture must exercise a non-best selection'
            events = [[key(pygame.K_b)]] + [[key(pygame.K_PERIOD)]] * other
            pages = play(keeper, policy+'-other-elite-not-recorded', events + [[key(pygame.K_v)], [pygame.event.Event(pygame.QUIT)]])
            checks[policy+'_other_selected_elite_explicitly_not_recorded_without_writes'] = (
                'not recorded' in ' '.join(pages[-2]['all_lines']) and before == inventory(keeper))
            pages=play(keeper,policy+'-undo-staging',[[key(pygame.K_t)],[key(pygame.K_r)],[key(pygame.K_BACKSPACE)],[pygame.event.Event(pygame.QUIT)]])
            checks[policy+'_unstage_preserves_all_original_creature_and_campaign_bytes']=before==inventory(keeper)
            launch(keeper,policy+'-incompatible-policy','--learning-policy','qtable' if policy=='incumbent' else 'incumbent',expected=2)
            checks[policy+'_incompatible_policy_refused_without_writes']=before==inventory(keeper)
            observed[policy]=dict(initial_grid=original_id,adopted_grid=adopted.grid['grid_id'],completed_eras=[dict(era_index=e['era_index'],rng_seed=e['rng_seed'],weather=e['weather'],founders=e['report'].get('founders')) for e in after['eras']])
        keeper=root/'interrupted-save'
        launch(keeper,'recovery-create','--new','--eras','1')
        original=os.replace
        def fail_state(source,destination):
            if Path(destination)==keeper/'campaign_state.json':raise PermissionError('observed campaign state lock')
            return original(source,destination)
        with patch('mecha_game.session.os.replace',fail_state):
            pages=play(keeper,'interrupted-save',[[key(pygame.K_t)],[key(pygame.K_r)],[key(pygame.K_3)],
                [key(pygame.K_e)],[pygame.event.Event(pygame.QUIT)]])
        pending=json.loads((keeper/'era_plan.json').read_text())['pending']
        checks['interrupted_state_write_keeps_completed_result_and_staged_inputs']=(pending is not None and
            json.loads((keeper/'campaign_state.json').read_text())['era_count']==1 and 'Era not completed' in ' '.join(pages[3]['all_lines']))
        expected_recording = pending['recording']['replay']
        if legacy_bundle is not None:
            old_executable = legacy_bundle / ('Mechagotchi.exe' if os.name == 'nt' else 'Mechagotchi')
            before_legacy = inventory(keeper)
            command = [str(old_executable), '--keeper-dir', str(keeper), '--eras', '1', '--ticks', '1', '--era-scale', 'tiny', '--fps', '0']
            result = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True, encoding='utf-8',
                errors='replace', timeout=90, **({'creationflags':subprocess.CREATE_NO_WINDOW} if os.name=='nt' else {}))
            launches['legacy-refuses-recording-journal'] = dict(command=command, returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)
            checks['legacy_native_refuses_pending_original_journal_without_writes'] = (
                result.returncode == 2 and 'unsupported preparation format' in result.stderr and before_legacy == inventory(keeper))
        launch(keeper,'recovery-finish-only','--eras','1')
        recovered=EraReview.load(keeper).history
        checks['native_restart_finishes_recorded_era_without_an_extra_era']=(len(recovered['eras'])==2 and
            recovered['eras'][-1]['report']==pending['era']['report'] and recovered['eras'][-1]['rng_seed']==pending['era']['rng_seed'] and
            json.loads((keeper/'campaign_state.json').read_text())['era_count']==2 and json.loads((keeper/'era_plan.json').read_text())['pending'] is None)
        actual_recording = load_saved_replay(keeper, recovered['campaign_id'], pending['era']['era_index'], expected_seed=pending['era']['rng_seed'])
        checks['native_restart_finishes_the_exact_journaled_original_recording'] = actual_recording == expected_recording
    checks['all_actual_source_flows_exit_and_fit']=all(f['returncode']==0 and all(p['fits'] for p in f['pages']) for f in flows)
    return dict(artifact_id='keeper_loop_release_stage0',date='2026-10-04',status='observed_native_and_source',
        purpose='Keep one connected care/preparation/era/collection/adoption/replay loop durable across restart and interrupted persistence.',
        source_artifacts=['game/src/mecha_game/era_plan.py','game/src/mecha_game/app.py','game/src/mecha_game/campaign.py','game/src/mecha_game/original_recording.py','labs/game_loop/verify_keeper_loop.py'],
        metrics=dict(checks=checks,launches=launches,interactive=flows,observed=observed,native_executable_sha256=hashlib.sha256(executable.read_bytes()).hexdigest()),
        closed_states=[k for k,v in checks.items() if v],
        blocked_states=['Native subprocesses used SDL dummy video/audio; keyboard interactions were observed in source pygame only.',
                        'Older saves without base_parameters keep their established legacy interpretation; no historical bases are inferred.',
                        'Era responsiveness is measured separately; this harness verifies connected play and persistence. No offline simulation or service.',
                        'Full local verification and published-SHA Windows/Ubuntu CI are separate gates.'],
        decision=dict(verdict='verified' if all(checks.values()) else 'withhold'),next_research_step='Complete final visual/preservation/diff review and final focused/full gates; preserve the pre-repair observation.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--screenshots',type=Path,default=ROOT/'.development/t4-ui')
    parser.add_argument('--legacy-bundle',type=Path)
    args=parser.parse_args();report=verify(args.bundle.resolve(),args.screenshots.resolve(),args.legacy_bundle.resolve() if args.legacy_bundle else None);report['artifact_id']=args.output.stem
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(checks=report['metrics']['checks'],launches=len(report['metrics']['launches']),flows=len(report['metrics']['interactive'])),indent=2))
    raise SystemExit(0 if report['decision']['verdict']=='verified' else 1)
