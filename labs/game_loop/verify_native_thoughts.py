"""X7 native thought acceptance; source SDL events and processes stay distinct.

The source journeys use real app/session/replay paths with injected pygame
events. Subprocesses run unpatched native entry with bounded frames and owned
diagnostics. Neither observation is operating-system keyboard automation.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for folder in ('game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT / folder))
import pygame
from mecha_game.app import run, _EraBench
from mecha_game.footer import FooterPager
from mecha_game.packets import default_fixture_paths
from mecha_game.replay import ReplayPlayer
from mecha_game.session import CompanionSession, load_session_inputs


def key(code):
    return pygame.event.Event(pygame.KEYDOWN, key=code, mod=0, repeat=False)


def has_thought(lines):
    return any(line.startswith('Thought t') for line in lines)


def drive(home, events, output, label, *, initial_view='care', screenshot_frames=()):
    records, current = [], {}
    pending = iter(events)
    original = FooterPager.layout
    deadline = time.monotonic() + 60
    def layout(pager, lines, *args, **kwargs):
        result = original(pager, lines, *args, **kwargs)
        current.clear()
        current.update(all_lines=list(lines), drawn_lines=list(result.lines), page=result.page)
        return result
    def frame():
        assert time.monotonic() < deadline, 'native source journey exceeded 60 seconds'
        surface = pygame.display.get_surface()
        observation = dict(current, size=list(surface.get_size()), driver=pygame.display.get_driver())
        if len(records) in screenshot_frames:
            name = f'{label}-frame-{len(records):02d}.png'
            pygame.image.save(surface, str(output / name))
            observation['screenshot'] = name
        records.append(observation)
    def next_events():
        assert time.monotonic() < deadline, 'native source journey exceeded 60 seconds'
        return next(pending, [pygame.event.Event(pygame.QUIT)])
    with patch('pygame.event.get', side_effect=next_events), patch.object(FooterPager, 'layout', layout), \
            patch('pygame.display.flip', side_effect=frame):
        assert run(['--keeper-dir', str(home), '--era-scale', 'tiny', '--scale', '2', '--fps', '0',
                    '--tick-frames', '4', '--view', initial_view]) == 0
    return records


def verify(output, *, bundle=None):
    output.mkdir(parents=True, exist_ok=False)
    # Explicitly require the actual Windows display driver; never inherit dummy.
    if sys.platform == 'win32':
        os.environ['SDL_VIDEODRIVER'] = 'windows'
    else:
        os.environ.pop('SDL_VIDEODRIVER', None)
    os.environ['SDL_AUDIODRIVER'] = 'dummy'
    grid, profile, model = load_session_inputs(*default_fixture_paths())
    profile = copy.deepcopy(profile)
    profile['deliberation'] = {'max_ticks': 4, 'confidence_threshold': 1.0}
    home = output / 'source-keeper'
    session = CompanionSession(grid, profile, model=model)
    session.save_checkpoint(home / 'companion.json')
    care = drive(home, [[], [pygame.event.Event(pygame.VIDEORESIZE, w=384, h=420)],
        [key(pygame.K_F1)], [key(pygame.K_ESCAPE)], [], [key(pygame.K_f)], [], [], [],
        [pygame.event.Event(pygame.QUIT)]], output, 'care', screenshot_frames=(0, 1, 2, 4, 8))
    checks = {
        'native_windows_display': all(row['driver'] == 'windows' for row in care) if sys.platform == 'win32' else None,
        'thought_drawn_default': has_thought(care[0]['drawn_lines']),
        'thought_drawn_narrow': has_thought(care[1]['drawn_lines']) and care[1]['size'] == [384, 420],
        'help_clears': not has_thought(care[2]['all_lines']),
        'help_close_stays_clear': not has_thought(care[3]['all_lines']),
        'next_tick_restores_actual_thought': has_thought(care[4]['drawn_lines']),
        'keeper_override_clears': not has_thought(care[8]['all_lines']),
        'quit_clears': not has_thought(care[9]['all_lines']),
    }
    saved = CompanionSession.load(home / 'companion.json')
    checks['care_persisted_exact_ticks'] = saved.state['age_ticks'] == 3 and saved.state['action_counts'].get('feed') == 1
    restarted = drive(home, [[key(pygame.K_F6)], [key(pygame.K_ESCAPE)],
                            [pygame.event.Event(pygame.QUIT)]], output, 'restart', screenshot_frames=(0,))
    checks['restart_before_tick_has_no_thought'] = not any(has_thought(row['all_lines']) for row in restarted)
    checks['restart_preserves_age'] = CompanionSession.load(home / 'companion.json').state['age_ticks'] == 3
    reflex_home = output / 'reflex-control'
    reflex = CompanionSession(grid, profile, model=model)
    reflex.state['energy'] = .1
    reflex.save_checkpoint(reflex_home / 'companion.json')
    reflex_frames = drive(reflex_home, [[], [pygame.event.Event(pygame.QUIT)]], output,
                          'reflex', screenshot_frames=(0,))
    checks['configured_reflex_control_has_no_thought'] = not any(has_thought(row['all_lines']) for row in reflex_frames)

    # A real original era recording reaches the native selected-frame reader.
    replay_home = output / 'replay-keeper'
    replay_session = CompanionSession(grid, profile, model=model)
    replay_session.save_checkpoint(replay_home / 'companion.json')
    bench = _EraBench('tiny', replay_home / 'model_cache', replay_home / 'campaign_state.json',
                      replay_home / 'campaign.sqlite3', initial_profile=profile, keeper_session=replay_session)
    bench.run_era(replay_home / 'campaign.sqlite3')
    replay = bench.campaign.last_original_recording['replay']
    player = ReplayPlayer(replay)
    candidates = []
    for index in range(replay['frame_count']):
        player.index = index
        if player.thought_lines():
            candidates.append(index)
    assert candidates, 'actual original recording contains no deliberative frame'
    selected = candidates[0]
    replay_events = [[key(pygame.K_v), key(pygame.K_SPACE)], *[[key(pygame.K_PERIOD)] for _ in range(selected)],
                     [key(pygame.K_F1)], [key(pygame.K_ESCAPE)], [pygame.event.Event(pygame.QUIT)]]
    recorded = drive(replay_home, replay_events, output, 'replay', initial_view='review',
                     screenshot_frames=(selected, selected + 1))
    checks['original_replay_birth_has_no_thought'] = not any('Recorded thought' in line for line in recorded[0]['all_lines'])
    checks['original_replay_actual_thought_drawn'] = any(line.startswith('Recorded thought') for line in recorded[selected]['drawn_lines'])
    checks['replay_help_hides_recorded_thought'] = not any('Recorded thought' in line for line in recorded[selected + 1]['all_lines'])

    command = [str(bundle)] if bundle else [str(ROOT / '.venv/Scripts/python.exe'), '-B', str(ROOT / 'game/run_game.py')]
    launches = []
    process_profile = output / 'native-thought-covenant.json'
    process_profile.write_text(json.dumps(profile, indent=2) + '\n', encoding='utf-8')
    process_home = output / 'process-keeper'
    for label, flags in (('new', ['--new', '--slip', str(process_profile), '--care-selection', 'observed_care_selection_v1']),
                         ('resume', ['--view', 'archive'])):
        receipt = output / f'process-{label}.json'
        args = command + ['--keeper-dir', str(process_home), '--frames', '14' if label == 'new' else '2', '--tick-frames', '12',
                          '--fps', '8', '--scale', '2', '--launch-info', str(receipt), *flags]
        result = subprocess.run(args, cwd=output, capture_output=True, text=True, encoding='utf-8',
                                errors='replace', timeout=60)
        (output / f'process-{label}.stdout.txt').write_text(result.stdout, encoding='utf-8')
        (output / f'process-{label}.stderr.txt').write_text(result.stderr, encoding='utf-8')
        observed = json.loads(receipt.read_text(encoding='utf-8'))
        launches.append(dict(label=label, command=args, returncode=result.returncode, receipt=receipt.name,
                             driver=observed.get('display', {}).get('driver')))
        checks[f'process_{label}_clean_exit'] = result.returncode == 0 and observed.get('stopped') is True
        checks[f'process_{label}_windows_driver'] = observed.get('display', {}).get('driver') == 'windows' if sys.platform == 'win32' else None
        observations = observed.get('native_readout', [])
        checks[f'process_{label}_rendered_diagnostics'] = bool(observations)
        if label == 'new':
            checks['process_new_thought_drawn'] = any(has_thought(row['footer_lines']) for row in observations)
        else:
            checks['process_restart_reader_has_no_live_thought'] = not any(has_thought(row['footer_lines']) for row in observations)
    report = dict(format='x7_native_thought_acceptance_v1', checks=checks,
                  ok=all(value for value in checks.values() if value is not None),
                  source_flows={'care': care, 'restart': restarted, 'reflex_control': reflex_frames, 'original_replay': recorded},
                  launches=launches, operating_system_keyboard_observed=False,
                  bundle_sha256=hashlib.sha256(bundle.read_bytes()).hexdigest() if bundle else None,
                  screenshot_scope='actual SDL window buffers; source-injected pygame events',
                  frames=sum(map(len, (care, restarted, reflex_frames, recorded))))
    (output / 'result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'ok': report['ok'], 'checks': len(checks), 'frames': report['frames'],
                      'process_launches': len(launches), 'result': str(output / 'result.json')}))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True, help='new owned evidence directory')
    parser.add_argument('--bundle', type=Path, help='optional current native executable')
    args = parser.parse_args()
    raise SystemExit(0 if verify(args.output.resolve(), bundle=args.bundle.resolve() if args.bundle else None)['ok'] else 1)
