"""T2 observed saved-archive play on native-created histories, with isolated pets."""
import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
for folder in ('game/src','packages/mecha_engine/src','labs/game_loop'):
    sys.path.insert(0,str(ROOT/folder))
import pygame
from verify_era_review import interact, inventory, key
from mecha_game.era_review import EraReview
from mecha_game.repertoire import RepertoireBrowser
from mecha_game.session import CompanionSession


def verify(bundle,screenshots):
    executable=bundle/('Mechagotchi.exe' if os.name=='nt' else 'Mechagotchi')
    env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',PYTHONDONTWRITEBYTECODE='1')
    screenshots.mkdir(parents=True,exist_ok=True)
    checks,launches,flows,selections={},[],[],[]
    with tempfile.TemporaryDirectory(prefix='mechagotchi-saved-archive-') as directory:
        root=Path(directory)
        def launch(label,keeper,*args):
            command=[str(executable),'--keeper-dir',str(keeper),'--ticks','1','--tick-frames','1','--fps','0','--era-scale','tiny',*args]
            result=subprocess.run(command,cwd=root,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=180,
                                  **({'creationflags':subprocess.CREATE_NO_WINDOW} if os.name=='nt' else {}))
            launches.append(dict(label=label,command=command,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr))
            if result.returncode or 'Traceback' in result.stderr:raise AssertionError(launches[-1])
        for policy in ('incumbent','qtable'):
            keeper=root/policy
            launch(policy+'_new_24_eras',keeper,'--new','--learning-policy',policy,'--eras','24')
            history=EraReview.load(keeper)
            checks[policy+'_native_long_history']=len(history.history['eras'])==24
            ledger=(keeper/'campaign.sqlite3').read_bytes()
            launch(policy+'_restart',keeper)
            checks[policy+'_native_restart_keeps_archive']=ledger==(keeper/'campaign.sqlite3').read_bytes()
            before=inventory(keeper)
            flow=interact(keeper,policy+'-archive-navigation',[[key(pygame.K_b)],[key(pygame.K_f),key(pygame.K_s)],
                [key(pygame.K_PAGEDOWN)],[key(pygame.K_LEFTBRACKET)]*30,[key(pygame.K_PERIOD)],
                [key(pygame.K_F1)],[key(pygame.K_ESCAPE)],[key(pygame.K_t)],[key(pygame.K_b)],
                [key(pygame.K_ESCAPE)],[pygame.event.Event(pygame.QUIT)]],screenshots,scale=1)
            flows.append(flow)
            pages=flow['pages']
            checks[policy+'_read_only_paused_archive_preserves_all_bytes']=before==inventory(keeper)
            checks[policy+'_long_navigation_help_and_report_return']=(
                'REPERTOIRE  era 23' in ' '.join(pages[0]['all_lines']) and
                'REPERTOIRE  era 0' in ' '.join(pages[3]['all_lines']) and
                pages[5]['all_lines'][0].startswith('HELP') and
                pages[7]['all_lines'][0].startswith('ERA 0 ') and pages[9]['all_lines'][0].startswith('ERA 0 '))
            view=RepertoireBrowser.load(keeper)
            view.step()
            expected=view.current()
            selections.append(dict(policy=policy,era_index=view.selected_era['era_index'],niche_key=expected['niche_key'],
                                   grid_id=expected['grid_id'],fitness=expected['fitness'],descriptor=expected['descriptor']))
            flow=interact(keeper,policy+'-adopt-selected',[[key(pygame.K_b)],[key(pygame.K_PERIOD)],
                [key(pygame.K_a)],[pygame.event.Event(pygame.QUIT)]],screenshots,scale=10)
            flows.append(flow)
            pet=CompanionSession.load(keeper/'companion.json')
            checks[policy+'_selected_adoption_and_policy_resume']=(pet.grid==expected['grid'] and pet.learning_policy==policy and
                pet.lineage[-1]['origin']=='era_elite' and 'REPERTOIRE' not in ' '.join(flow['pages'][2]['all_lines']))
            checks[policy+'_adoption_keeps_campaign_records']=ledger==(keeper/'campaign.sqlite3').read_bytes()
            flow=interact(keeper,policy+'-covenant-controls',[[key(pygame.K_t)],[key(pygame.K_c)],
                [pygame.event.Event(pygame.QUIT)]],screenshots,scale=1)
            flows.append(flow)
            visible=' '.join(flow['pages'][1]['visible'])
            checks[policy+'_covenant_actions_visible_on_first_page']='COVENANT' in visible and '1 palette' in visible
            # Current-covenant refusal is a deliberately invalid private fixture.
            state=keeper/'campaign_state.json'
            state_bytes=state.read_bytes()
            payload=json.loads(state_bytes)
            payload['slip_profile']['grid']['allowed_palettes']=['not_the_saved_palette']
            state.write_text(json.dumps(payload),encoding='utf-8')
            pet_bytes=(keeper/'companion.json').read_bytes()
            flow=interact(keeper,policy+'-adoption-refused',[[key(pygame.K_b)],[key(pygame.K_a)],
                [pygame.event.Event(pygame.QUIT)]],screenshots,scale=1)
            flows.append(flow)
            checks[policy+'_refusal_keeps_pet_and_archive']=(pet_bytes==(keeper/'companion.json').read_bytes() and
                ledger==(keeper/'campaign.sqlite3').read_bytes() and 'Adoption refused' in ' '.join(flow['pages'][1]['all_lines']))
            state.write_bytes(state_bytes)  # this isolated fixture only
            before_history=EraReview.load(keeper).history['eras']
            age=CompanionSession.load(keeper/'companion.json').state['age_ticks']
            flow=interact(keeper,policy+'-next-era',[[key(pygame.K_b)],[key(pygame.K_e)],
                [pygame.event.Event(pygame.QUIT)]],screenshots,scale=1)
            flows.append(flow)
            after=EraReview.load(keeper).history['eras']
            checks[policy+'_next_era_after_browsing_preserves_history_and_pauses_care']=(len(after)==25 and
                after[:24]==before_history and CompanionSession.load(keeper/'companion.json').state['age_ticks']==age and
                flow['pages'][1]['all_lines'][0].startswith('ERA 24 '))
        empty=root/'empty'
        CompanionSession.load(keeper/'companion.json').save_checkpoint(empty/'companion.json')
        before=inventory(empty)
        flow=interact(empty,'empty-archive',[[key(pygame.K_b)],[pygame.event.Event(pygame.QUIT)]],screenshots,scale=1)
        flows.append(flow)
        checks['empty_archive_is_explicit_paused_and_creates_nothing']=(before==inventory(empty) and
            'No recorded eras' in ' '.join(flow['pages'][0]['all_lines']))
        age=CompanionSession.load(empty/'companion.json').state['age_ticks']
        flow=interact(empty,'empty-first-era',[[key(pygame.K_b)],[key(pygame.K_e)],[pygame.event.Event(pygame.QUIT)]],screenshots,scale=1)
        flows.append(flow)
        checks['empty_archive_can_run_first_era_without_care_tick']=(len(EraReview.load(empty).history['eras'])==1 and
            CompanionSession.load(empty/'companion.json').state['age_ticks']==age and flow['pages'][1]['all_lines'][0].startswith('ERA 0 '))
        conn=sqlite3.connect(keeper/'campaign.sqlite3')
        conn.execute("UPDATE elites SET elite_json='[]' WHERE era_index=24")
        conn.commit();conn.close()
        before=inventory(keeper)
        flow=interact(keeper,'corrupt-archive',[[key(pygame.K_b)],[key(pygame.K_e),key(pygame.K_c),key(pygame.K_a)],[pygame.event.Event(pygame.QUIT)]],screenshots,scale=1)
        flows.append(flow)
        checks['corrupt_archive_is_explicit_paused_and_preserved']=(before==inventory(keeper) and
            'unavailable' in ' '.join(flow['pages'][0]['all_lines']).lower())
    checks['all_flows_exit_cleanly_and_fit']=all(f['returncode']==0 and all(p['fits'] for p in f['pages']) for f in flows)
    return dict(artifact_id='saved_archive_release_stage0',date='2026-10-04',status='observed_native_and_source',
        purpose='Make saved creatures browsable and explicitly adoptable after restart without changing engine mechanics.',
        source_artifacts=['labs/game_loop/campaign_store.py','packages/mecha_engine/src/mecha_engine/storage/store.py',
                          'game/src/mecha_game/repertoire.py','game/src/mecha_game/app.py','labs/game_loop/verify_saved_archive.py'],
        metrics=dict(checks=checks,launches=launches,interactive=flows,selected_elites=selections,
                     native_executable_sha256=hashlib.sha256(executable.read_bytes()).hexdigest()),
        closed_states=[name for name,ok in checks.items() if ok],
        blocked_states=['Native keyboard unavailable: required node_repl/@oai/sky runtime not exposed; no substitute automation used.',
                        'Full T2 gate, human usability, signing and published-SHA Windows/Ubuntu CI remain separate gates.'],
        decision=dict(verdict='verified' if all(checks.values()) else 'withhold'),
        next_research_step='Complete focused/full local gates before local closure; preserve prior observations and engine controls.')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--screenshots',type=Path,default=ROOT/'.development/t2-ui')
    args=parser.parse_args()
    report=verify(args.bundle.resolve(),args.screenshots.resolve())
    report['artifact_id']=args.output.stem
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(checks=report['metrics']['checks'],launches=len(report['metrics']['launches']),
                         flows=len(report['metrics']['interactive']),frames=sum(len(f['pages']) for f in report['metrics']['interactive'])),indent=2))
    raise SystemExit(0 if report['decision']['verdict']=='verified' else 1)
