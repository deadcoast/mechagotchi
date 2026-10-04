"""Q3 / DR 0064: measure ADOPT/REFUSE before changing the product default.

The six conjunction gates and budgets are preregistered in
docs/development/q3-default-covenant.md. A false or missing check REFUSES.
Historical studies remain explicitly bound to HELLO_SLIP, never relabelled.
"""
import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for directory in ('game', 'game/src', 'packages/mecha_engine/src', 'labs/lifecycle_sim'):
    sys.path.insert(0, str(ROOT/directory))
from evidence import build_companion_loop_report
from cleanliness_mechanic_gate import build_cleanliness_mechanic_report
from mecha_engine.lifecycle.simulate import CLEANLINESS_CLEAN_RESTORE
from mecha_game.packets import HELLO_SEED, HELLO_SLIP
from mecha_game.session import CompanionSession, load_session_inputs
from mecha_game.app import _footer_lines, run

CANDIDATE = 'data/slips/valid/slip_v2_cleanliness.json'
REQUIRED = frozenset(('instrument_reproduced', 'attentive_survives', 'neglect_unchanged',
                      'scripted_care_survives', 'clean_answers', 'window_contract'))


def read(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))


def decide(checks):
    failed = sorted(name for name in REQUIRED | checks.keys() if checks.get(name) is not True)
    return {'verdict': 'REFUSE' if failed else 'ADOPT', 'failed_checks': failed,
            'rule': 'Every preregistered candidate acceptance check must pass; no metric or threshold is retuned.'}


def session(profile=CANDIDATE):
    grid, slip, model = load_session_inputs(ROOT/HELLO_SEED, ROOT/profile)
    return CompanionSession(grid, slip, model=model)


def keeper_arm(attentive):
    pet = session()
    feeds = 0
    for _ in range(400):
        if not pet.alive:
            break
        action = 'feed' if attentive and pet.begging else None
        feeds += int(action == 'feed')
        pet.advance(action)
    return {'alive': pet.alive, 'age_ticks': pet.state['age_ticks'],
            'death_cause': pet.death_cause, 'keeper_feeds': feeds,
            'final_cleanliness': pet.state['cleanliness'], 'final_stress': pet.state['stress']}


def scripted_care():
    pet = session()
    clean_events = []
    for _ in range(72):
        if not pet.alive:
            break
        before = pet.state['cleanliness']
        word = pet.snapshot()['health']['binding_word']
        action = ('clean' if before <= 1 - CLEANLINESS_CLEAN_RESTORE else
                  {'hungry': 'feed', 'tired': 'sleep', 'lonely': 'play', 'stressed': 'play'}.get(word, 'sleep'))
        pet.advance(action)
        if action == 'clean':
            clean_events.append({'tick': pet.state['age_ticks'], 'before': before,
                                 'after': pet.state['cleanliness'], 'health_binding_before': word})
    return {'alive': pet.alive, 'age_ticks': pet.state['age_ticks'],
            'clean_count': len(clean_events), 'clean_events': clean_events,
            'clean_threshold': 1 - CLEANLINESS_CLEAN_RESTORE,
            'final_health': pet.snapshot()['health'], 'final_cleanliness': pet.state['cleanliness']}


def window_probe(capture_dir=None):
    os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
    import pygame
    frames = []
    with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {'SDL_VIDEODRIVER': 'dummy', 'SDL_AUDIODRIVER': 'dummy'}):
        events = iter([[], [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_g)]])

        def capture():
            surface = pygame.display.get_surface()
            frames.append(surface.get_size())
            if capture_dir is not None:
                Path(capture_dir).mkdir(parents=True, exist_ok=True)
                pygame.image.save(surface, str(Path(capture_dir)/'q3-candidate-window.png'))

        args = ['--keeper-dir', directory, '--ticks', '2', '--tick-frames', '1', '--fps', '0']
        with patch('pygame.event.get', side_effect=lambda: next(events, [])), patch('pygame.display.flip', side_effect=capture):
            fresh = run(['--new', '--slip', str(ROOT/CANDIDATE), *args])
        path = Path(directory)/'companion.json'
        before = CompanionSession.load(path)
        lines = _footer_lines(before.snapshot(), None)
        clean_lines = [line for line in lines if 'G clean' in line]
        pygame.font.init()
        font = pygame.font.Font(None, 22)
        widths = [font.size(line)[0] for line in clean_lines]
        pygame.font.quit()
        with patch('pygame.event.get', return_value=[]):
            resumed = run(args)
        after = CompanionSession.load(path)
        return {'fresh_exit': fresh, 'resume_exit': resumed, 'fresh_age': before.state['age_ticks'],
                'resumed_age': after.state['age_ticks'], 'clean_count': before.state['action_counts'].get('clean', 0),
                'clean_lines': clean_lines, 'clean_line_widths': widths, 'window_size': frames[-1],
                'engine_value_shown': any(f"cleanliness {before.state['cleanliness']:.2f}" in line for line in clean_lines),
                'same_profile': before.slip_profile == after.slip_profile,
                'clean_control_fits': bool(widths) and max(widths) <= frames[-1][0] - 16}


def build_report(capture_dir=None):
    incumbent = build_companion_loop_report()
    committed = read('data/game_client/companion_loop_stage0.json')
    mechanic = build_cleanliness_mechanic_report()
    mechanic_pin = read('data/lifecycle/cleanliness_mechanic_gate_stage0.json')
    instrument = (incumbent['metrics'] == committed['metrics'] and
                  mechanic['metrics'] == mechanic_pin['metrics'] and mechanic['decision'] == mechanic_pin['decision'])
    attentive, neglect, care = keeper_arm(True), keeper_arm(False), scripted_care()
    window = window_probe(capture_dir)
    old_neglect = committed['metrics']['neglect_arm']
    checks = {
        'instrument_reproduced': instrument,
        'attentive_survives': attentive['alive'] and attentive['age_ticks'] == 400,
        'neglect_unchanged': neglect['age_ticks'] == old_neglect['age_ticks'] and neglect['death_cause'] == old_neglect['death_cause'],
        'scripted_care_survives': care['alive'] and care['age_ticks'] == 72,
        'clean_answers': care['clean_count'] > 0 and all(row['after'] > row['before'] for row in care['clean_events']),
        'window_contract': window['fresh_exit'] == window['resume_exit'] == 0 and window['fresh_age'] == 2
                           and window['resumed_age'] == 4 and window['clean_count'] == 1
                           and window['same_profile'] and window['engine_value_shown'] and window['clean_control_fits'],
    }
    return {'artifact_id': 'default_covenant_gate_stage0', 'date': '2026-10-04', 'status': 'candidate_measured_before_default_flip',
            'purpose': 'Price and judge default cleanliness under unchanged scientific definitions and preserved historical inputs.',
            'source_artifacts': [CANDIDATE, HELLO_SEED.as_posix(), HELLO_SLIP.as_posix(), 'data/game_client/companion_loop_stage0.json',
                                 'data/lifecycle/cleanliness_mechanic_gate_stage0.json', 'docs/development/q3-default-covenant.md'],
            'metrics': {'instrument_reproduced': instrument, 'candidate_attentive': attentive, 'candidate_neglect': neglect,
                        'scripted_care': care, 'window': window, 'checks': checks},
            'artifact_plan': {'regenerated_historical_artifacts': [],
                              'new_current_default_artifact': 'data/game_client/default_covenant_gate_stage0.json',
                              'new_release_observation': 'data/game_client/default_covenant_release_stage0.json',
                              'frozen_bindings': ['game/evidence.py::_new_session -> HELLO_SLIP', 'game/evidence.py::_campaign_inputs -> HELLO_SLIP',
                                                  'game/evidence.py::build_front_end_skeleton_report -> HELLO_SLIP',
                                                  'labs/game_loop/session_runner.py -> slip_lcd_seed.json',
                                                  'labs/game_loop/replay_recorder.py -> slip_lcd_seed.json']},
            'closed_states': sorted(name for name, value in checks.items() if value),
            'blocked_states': ['human_usability_unmeasured', 'native_remote_ci_unverified', 'qtable_default_not_promoted'],
            'decision': decide(checks), 'next_research_step': 'Land only if ADOPT, verify session/campaign/bundle continuity, then Q4 hidden-axis source survey.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--capture-dir', type=Path)
    args = parser.parse_args()
    report = build_report(args.capture_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'decision': report['decision'], 'metrics': report['metrics']}, indent=2))
    raise SystemExit(0 if report['decision']['verdict'] == 'ADOPT' else 1)
