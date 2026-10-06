"""Bounded real process journeys for qualified native learning deployment.

This verifies product integration, never reruns or replaces the scientific cohort.
Source and frozen-executable runs retain separate reports and isolated save homes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
for folder in ('game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT / folder))
from mecha_game.session import CompanionSession, load_session_inputs
from mecha_game.packets import default_fixture_paths

SOURCE_FILES = ('game/src/mecha_game/startup.py', 'game/src/mecha_game/entry.py',
    'game/src/mecha_game/session.py', 'game/src/mecha_game/native_ui.py',
    'game/src/mecha_game/app.py', 'labs/game_loop/verify_learning_rollout.py')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inventory(home):
    return {p.relative_to(home).as_posix(): digest(p) for p in home.rglob('*') if p.is_file()}


def verify(output, *, bundle=None):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    (output / 'cwd').mkdir()
    started = time.monotonic()
    source = {name: digest(ROOT / name) for name in SOURCE_FILES}
    executable = Path(bundle).resolve() / ('Mechagotchi.exe' if os.name == 'nt' else 'Mechagotchi') if bundle else None
    if executable and not executable.is_file():
        raise FileNotFoundError(executable)
    base = [str(executable)] if executable else [sys.executable, '-B', str(ROOT / 'game/run_game.py')]
    env = dict(os.environ)
    for key in ('PYTHONPATH', 'PYTHONHOME'):
        env.pop(key, None)
    env.update(PYTHONDONTWRITEBYTECODE='1', PYGAME_HIDE_SUPPORT_PROMPT='1', SDL_AUDIODRIVER='dummy')
    if os.name == 'nt':
        env['SDL_VIDEODRIVER'] = 'windows'
    else:
        env.pop('SDL_VIDEODRIVER', None)
    report = dict(format='qualified_learning_rollout_verification_v1', mode='native' if executable else 'source',
        source_sha256=source, executable_sha256=digest(executable) if executable else None,
        budgets={'per_launch_seconds': 60, 'total_seconds': 300, 'automatic_retries': 0},
        runs=[], checks={}, status='running', failure=None)

    def checkpoint():
        report['elapsed_seconds'] = time.monotonic() - started
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    def launch(label, home, *args, expected=0):
        remaining = 300 - (time.monotonic() - started)
        if remaining <= 0:
            raise TimeoutError('Learning rollout verifier exhausted total budget')
        receipt = output / f'{label}-launch.json'
        command = [*base, '--keeper-dir', str(home), '--fps', '0', '--scale', '2',
                   '--tick-frames', '1', '--launch-info', str(receipt), *args]
        begun = time.monotonic()
        result = subprocess.run(command, cwd=output / 'cwd', env=env, capture_output=True,
            text=True, encoding='utf-8', errors='replace', timeout=min(60, remaining),
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        row = dict(label=label, command=command, returncode=result.returncode, expected=expected,
                   elapsed_seconds=time.monotonic() - begun, stdout=result.stdout, stderr=result.stderr,
                   receipt=receipt.name if receipt.exists() else None)
        report['runs'].append(row)
        checkpoint()
        if result.returncode != expected:
            raise AssertionError(f'{label}: returncode {result.returncode}, expected {expected}')
        if expected == 0 and (not receipt.exists() or json.loads(receipt.read_text())['startup_outcome'] != 'ready'):
            raise AssertionError(f'{label}: no successful real startup receipt')
        path = home / 'companion.json'
        return json.loads(path.read_text(encoding='utf-8')) if path.exists() else None

    def check(name, condition):
        report['checks'][name] = bool(condition)
        checkpoint()
        if not condition:
            raise AssertionError(name)

    checkpoint()
    try:
        home = output / 'builtin'
        fresh = launch('builtin-fresh', home, '--ticks', '2')
        check('builtin_native_default_qtable', fresh.get('learning_policy') == 'qtable' and fresh['state']['age_ticks'] == 2)
        resumed = launch('builtin-resume', home, '--ticks', '2')
        check('saved_qtable_continues', resumed.get('learning_policy') == 'qtable' and resumed['state']['age_ticks'] == 4
              and resumed['chronicle']['keeper_id'] == fresh['chronicle']['keeper_id'])
        before = inventory(home)
        launch('qtable-conflict', home, '--ticks', '1', '--learning-policy', 'incumbent', expected=2)
        check('qtable_conflict_preserves_every_file', before == inventory(home))

        home = output / 'incumbent'
        incumbent = launch('explicit-incumbent', home, '--ticks', '2', '--learning-policy', 'incumbent')
        check('incumbent_opt_out', incumbent.get('learning_policy', 'incumbent') == 'incumbent'
              and 'qtable_policy' not in incumbent['state'].get('thread_states', {}))
        continued = launch('incumbent-resume', home, '--ticks', '2')
        check('saved_incumbent_continues', continued.get('learning_policy', 'incumbent') == 'incumbent' and continued['state']['age_ticks'] == 4)
        before = inventory(home)
        launch('incumbent-conflict', home, '--ticks', '1', '--learning-policy', 'qtable', expected=2)
        check('incumbent_conflict_preserves_every_file', before == inventory(home))
        renewed = launch('incumbent-new-continuity', home, '--new', '--ticks', '1')
        check('explicit_new_without_override_keeps_prior_policy', renewed.get('learning_policy', 'incumbent') == 'incumbent'
              and renewed['chronicle']['keeper_id'] == incumbent['chronicle']['keeper_id'] and len(renewed['lineage']) == 2)

        seed, slip = default_fixture_paths()
        custom = launch('custom-seed', output / 'custom', '--seed', str(seed), '--ticks', '1')
        check('custom_omitted_policy_stays_incumbent', custom.get('learning_policy', 'incumbent') == 'incumbent')
        explicit = launch('custom-explicit-qtable', output / 'custom-explicit', '--slip', str(slip), '--learning-policy', 'qtable', '--ticks', '1')
        check('custom_explicit_qtable_available', explicit.get('learning_policy') == 'qtable')

        dead = launch('real-no-care-death', output / 'neglect', '--ticks', '20')
        check('real_no_care_starvation', not dead['state']['alive'] and dead['state']['age_ticks'] == 10
              and dead['state']['death_cause'] == 'starvation' and dead['state']['action_counts'].get('feed', 0) == 0)
        child = launch('real-no-care-child', output / 'successor', '--ticks', '10', '--auto-succeed')
        check('genuine_death_cold_successor', child['state']['alive'] and child['state']['age_ticks'] == 0
              and child.get('learning_policy') == 'qtable' and len(child['lineage']) == 2
              and child['lineage'][0]['death_cause'] == 'starvation'
              and child['lineage'][1]['parent_life_id'] == child['lineage'][0]['life_id']
              and 'qtable_policy' not in child['state'].get('thread_states', {}))

        grid, profile, model = load_session_inputs(seed, slip)
        warm = CompanionSession(grid, profile, model=model, learning_policy='qtable')
        for _ in range(160):
            state = warm.state
            care = ('feed' if state['hunger'] > .55 else 'sleep' if state['energy'] < .35
                    else 'clean' if state['cleanliness'] < .6 else None)
            warm.advance(care)
        check('real_care_trains_current_life', warm.alive and bool(warm.state['thread_states']['qtable_policy']['q']))
        home = output / 'warm'
        warm.save_checkpoint(home / 'companion.json')
        samples = sum(row['n'] for row in warm.state['thread_states']['qtable_policy']['q'].values())
        expected = CompanionSession.load(home / 'companion.json')
        # Care continues in preparation by design. Compare the first real
        # resumed tick with exact continuation; do not invent a paused surface.
        expected.advance()
        after = launch('warm-active-restart', home, '--ticks', '1')
        check('restart_matches_exact_trained_continuation', after['state'] == expected.state and after['learning_policy'] == 'qtable')
        check('active_restart_continues_learning', after['state']['age_ticks'] == 161
              and sum(row['n'] for row in after['state']['thread_states']['qtable_policy']['q'].values()) == samples + 1)
        successful_receipts = [json.loads((output / row['receipt']).read_text()) for row in report['runs'] if row['returncode'] == 0]
        drivers = [receipt.get('display', {}).get('driver') for receipt in successful_receipts]
        check('real_display_observed', bool(drivers) and all(driver == 'windows' if os.name == 'nt' else driver not in (None, 'dummy') for driver in drivers))
        check('source_unchanged_during_verification', source == {name: digest(ROOT / name) for name in SOURCE_FILES})
        report['status'] = 'verified'
    except BaseException as error:
        report['status'] = 'failed'
        report['failure'] = {'type': type(error).__name__, 'detail': str(error)}
        checkpoint()
        raise
    finally:
        checkpoint()
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--bundle', type=Path)
    args = parser.parse_args()
    result = verify(args.output, bundle=args.bundle)
    print(json.dumps({'status': result['status'], 'checks': result['checks'], 'launches': len(result['runs']),
                      'elapsed_seconds': result['elapsed_seconds']}, indent=2))
