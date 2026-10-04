"""T3: actual native launches and source pygame saved-replay observations."""
import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from verify_era_review import ROOT, CompanionSession, EraReview, interact, inventory, key, pygame


def verify(bundle, screenshots):
    executable = bundle / ('Mechagotchi.exe' if os.name == 'nt' else 'Mechagotchi')
    env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy', PYTHONDONTWRITEBYTECODE='1')
    screenshots.mkdir(parents=True, exist_ok=True)
    checks, launches, flows = {}, [], []
    with tempfile.TemporaryDirectory(prefix='mechagotchi-saved-replays-') as directory:
        root = Path(directory)
        for policy in ('incumbent', 'qtable'):
            keeper = root / policy
            def launch(label, *extra, expected=0):
                command = [str(executable), '--keeper-dir', str(keeper), '--ticks', '1', '--tick-frames', '1',
                           '--fps', '0', '--era-scale', 'tiny', *extra]
                result = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True,
                    encoding='utf-8', errors='replace', timeout=120,
                    **({'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {}))
                launches.append(dict(label=policy + '-' + label, command=command, returncode=result.returncode,
                                     stdout=result.stdout, stderr=result.stderr))
                if result.returncode != expected or 'Traceback' in result.stderr:
                    raise AssertionError(launches[-1])
            def play(label, events):
                flow = interact(keeper, policy + '-' + label, events, screenshots, scale=2)
                flows.append(flow)
                return flow['pages']
            launch('create', '--new', '--eras', '1', '--learning-policy', policy)
            age = CompanionSession.load(keeper / 'companion.json').state['age_ticks']
            pages = play('record-two-eras', [[key(pygame.K_e)], [key(pygame.K_v)], [key(pygame.K_SPACE)],
                [key(pygame.K_PERIOD)], [key(pygame.K_F1)], [key(pygame.K_F1)], [key(pygame.K_v)],
                [key(pygame.K_e)], [key(pygame.K_v)], [key(pygame.K_COMMA)] * 200,
                [key(pygame.K_v)], [key(pygame.K_LEFTBRACKET)], [key(pygame.K_v)],
                [key(pygame.K_t)], [pygame.event.Event(pygame.QUIT)]])
            checks[policy + '_current_run_records_and_reopens_selected_era'] = (
                pages[1]['all_lines'][0].startswith('REVIEW ERA 1') and
                pages[8]['all_lines'][0].startswith('REVIEW ERA 2') and
                pages[12]['all_lines'][0].startswith('REVIEW ERA 1') and
                len(list((keeper / 'replays').glob('*.json'))) == 2 and
                CompanionSession.load(keeper / 'companion.json').state['age_ticks'] == age)
            checks[policy + '_honest_post_era_label_retained'] = all(
                'post-era' in ' '.join(pages[index]['all_lines']) for index in (1, 8, 12))
            ledger = (keeper / 'campaign.sqlite3').read_bytes()
            recordings = inventory(keeper / 'replays')
            launch('native-resume')
            checks[policy + '_native_resume_preserves_recordings_ledger_and_policy'] = (
                ledger == (keeper / 'campaign.sqlite3').read_bytes() and recordings == inventory(keeper / 'replays') and
                CompanionSession.load(keeper / 'companion.json').learning_policy == policy and
                CompanionSession.load(keeper / 'companion.json').state['age_ticks'] == age + 1)
            before = inventory(keeper)
            pages = play('restart-playback', [[key(pygame.K_v)], [key(pygame.K_F1)], [], [key(pygame.K_F1)],
                [key(pygame.K_SPACE)], [], [key(pygame.K_PERIOD)] * 200, [key(pygame.K_COMMA)] * 200,
                [key(pygame.K_f), key(pygame.K_e), key(pygame.K_a), key(pygame.K_b), key(pygame.K_c)],
                [key(pygame.K_t)], [key(pygame.K_LEFTBRACKET)], [key(pygame.K_v)],
                [key(pygame.K_ESCAPE)], [pygame.event.Event(pygame.QUIT)]])
            replay = json.loads((keeper / 'replays' / next(p.name for p in (keeper / 'replays').glob('*era2.json'))).read_text())
            last = replay['frame_count'] - 1
            checks[policy + '_restart_latest_selected_help_pause_and_clamped_scrub'] = (
                pages[0]['all_lines'][0].startswith('REVIEW ERA 2') and
                pages[0]['all_lines'][1] == pages[3]['all_lines'][1] and
                pages[4]['all_lines'][1] == pages[5]['all_lines'][1] and
                f'frame {last}/{last}' in pages[6]['all_lines'][1] and 'frame 0/' in pages[7]['all_lines'][1] and
                pages[11]['all_lines'][0].startswith('REVIEW ERA 1') and pages[12]['all_lines'][0].startswith('ERA 1 ['))
            checks[policy + '_playback_ignores_care_planning_and_preserves_all_bytes'] = before == inventory(keeper)
            pages = play('unrecorded-era', [[key(pygame.K_t)], [key(pygame.K_LEFTBRACKET)] * 2,
                [key(pygame.K_v)], [pygame.event.Event(pygame.QUIT)]])
            checks[policy + '_unrecorded_older_era_is_explicit_and_not_rebuilt'] = (
                'No recording was saved for this era' in ' '.join(pages[2]['all_lines']) and before == inventory(keeper))
            launch('incompatible-policy', '--learning-policy', 'qtable' if policy == 'incumbent' else 'incumbent', expected=2)
            checks[policy + '_incompatible_policy_preserves_recordings_and_pet'] = before == inventory(keeper)
            corrupt = next((keeper / 'replays').glob('*era2.json'))
            corrupt.write_text('{}', encoding='utf-8')
            before = inventory(keeper)
            pages = play('tampered-recording', [[key(pygame.K_v)], [key(pygame.K_v)], [pygame.event.Event(pygame.QUIT)]])
            checks[policy + '_tamper_refused_without_replacement_or_care_ticks'] = (
                'SHA256' in ' '.join(pages[0]['all_lines']) and before == inventory(keeper))
    checks['all_source_flows_exit_and_render_within_page_width'] = all(
        flow['returncode'] == 0 and all(page['fits'] for page in flow['pages']) for flow in flows)
    return dict(artifact_id='saved_replays_release_stage0', date='2026-10-04', status='observed_native_and_source',
        purpose='Reopen real recorded post-era lives after restart without reconstructing missing history.',
        source_artifacts=['game/src/mecha_game/recorded_review.py', 'game/src/mecha_game/app.py', 'labs/game_loop/verify_saved_replays.py'],
        metrics=dict(checks=checks, launches=launches, interactive=flows,
                     native_executable_sha256=hashlib.sha256(executable.read_bytes()).hexdigest()),
        closed_states=[name for name, ok in checks.items() if ok],
        blocked_states=['Native keyboard runtime remains unavailable; source pygame events are distinct observations.',
                        'Recordings are post-era lives, not captures of original in-era evaluations.',
                        'Full local closure and exact-published-SHA native Windows/Ubuntu CI remain separate gates.'],
        decision=dict(verdict='verified' if all(checks.values()) else 'withhold'),
        next_research_step='Run the full gate once after focused/artifact/preservation review; preserve earlier evidence.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--screenshots', type=Path, default=ROOT / '.development/t3-ui')
    args = parser.parse_args()
    report = verify(args.bundle.resolve(), args.screenshots.resolve())
    report['artifact_id'] = args.output.stem
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(checks=report['metrics']['checks'], launches=len(report['metrics']['launches']),
                         flows=len(report['metrics']['interactive'])), indent=2))
    raise SystemExit(0 if report['decision']['verdict'] == 'verified' else 1)
