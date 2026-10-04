"""Observe Q3's actual built executable using isolated saves and an external cwd."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def verify_bundle(bundle: Path) -> dict:
    executable = bundle / ('Mechagotchi.exe' if sys.platform == 'win32' else 'Mechagotchi')
    if not executable.is_file():
        raise FileNotFoundError(f'Build the executable before verifying: {executable}')
    data = bundle/'_internal/data/slips/valid'
    old = data/'slip_lcd_seed.json'
    current = data/'slip_v2_cleanliness.json'
    if not old.is_file() or not current.is_file():
        raise FileNotFoundError('The release must include both current and incumbent covenants.')
    exits = []
    with tempfile.TemporaryDirectory() as directory:
        keeper = Path(directory)/'keeper'
        base = [str(executable), '--keeper-dir', str(keeper), '--tick-frames', '1', '--fps', '0', '--scale', '2']
        env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy')

        def launch(*args):
            options = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {}
            result = subprocess.run(base + list(args), cwd=directory, env=env, capture_output=True,
                                    text=True, encoding='utf-8', errors='replace', timeout=300, **options)
            exits.append(result.returncode)
            if result.returncode:
                raise RuntimeError(f'Built client failed ({result.returncode}): {result.stderr}')
            return json.loads((keeper/'companion.json').read_text(encoding='utf-8'))

        fresh = launch('--ticks', '4')
        resumed = launch('--ticks', '3')
        explicit_old = launch('--new', '--slip', str(old), '--eras', '1', '--era-scale', 'tiny', '--ticks', '1')
        campaign = json.loads((keeper/'campaign_state.json').read_text(encoding='utf-8'))
        old_resumed = launch('--eras', '1', '--era-scale', 'tiny', '--ticks', '1')
        resumed_campaign = json.loads((keeper/'campaign_state.json').read_text(encoding='utf-8'))
    checks = {
        'fresh_default_enabled': fresh['slip_profile'] == json.loads(current.read_text()) and 'cleanliness' in fresh['state'],
        'same_life_resumed': fresh['state']['age_ticks'] == 4 and resumed['state']['age_ticks'] == 7
                             and fresh['grid']['grid_id'] == resumed['grid']['grid_id'],
        'explicit_old_profile_stays_off': 'cleanliness' not in explicit_old['state'] and 'cleanliness' not in old_resumed['state'],
        'new_campaign_uses_selected_profile': campaign['slip_profile'] == explicit_old['slip_profile'],
        'campaign_resume_keeps_profile': resumed_campaign['slip_profile'] == campaign['slip_profile']
                                         and resumed_campaign['era_count'] == campaign['era_count'] + 1,
    }
    return {'artifact_id': 'default_covenant_release_stage0', 'date': '2026-10-04', 'status': 'observed_native_windows_bundle' if os.name == 'nt' else 'observed_native_bundle',
            'purpose': 'Verify the actual built current-default client, old save compatibility and campaign covenant continuity outside the repository cwd.',
            'source_artifacts': ['game/build_release.py', 'game/src/mecha_game/app.py', 'labs/game_loop/verify_default_release.py',
                                 'data/game_client/default_covenant_gate_stage0.json'],
            'metrics': {'launch_exit_codes': exits, 'fresh_age': fresh['state']['age_ticks'], 'resumed_age': resumed['state']['age_ticks'],
                        'campaign_eras': [campaign['era_count'], resumed_campaign['era_count']], 'checks': checks,
                        'executable_sha256': hashlib.sha256(executable.read_bytes()).hexdigest(), 'executable_bytes': executable.stat().st_size},
            'closed_states': sorted(name for name, value in checks.items() if value),
            'blocked_states': ['native_remote_ci_unverified', 'signing_and_other_platform_builds_not_observed', 'human_usability_unmeasured'],
            'decision': {'verdict': 'local_release_verified' if all(checks.values()) else 'withhold',
                         'failed_checks': sorted(name for name, value in checks.items() if not value)},
            'next_research_step': 'Q4 hidden-axis source survey; independent exact-SHA native remote CI when publication is allowed.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = verify_bundle(args.bundle.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(report['metrics'], indent=2))
    raise SystemExit(0 if report['decision']['verdict'] == 'local_release_verified' else 1)
