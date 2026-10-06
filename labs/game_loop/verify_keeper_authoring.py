"""X1 connected life/recovery observations; native launches remain separate."""
import argparse, copy, hashlib, json, os, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from labs.game_loop.verify_integrated_finish import interact, key, run, CompanionSession, pygame

def verify(fixtures, screenshots, bundle):
    fixtures.mkdir(parents=True, exist_ok=False)
    screenshots.mkdir(parents=True, exist_ok=True)
    checks, flows, launches = {}, [], []
    def play(keeper, label, batches):
        row = interact(keeper, label, batches, screenshots, scale=16)
        flows.append(row)
        checks[label + '_exit_and_fit'] = row['code'] == 0 and all(p['fits'] for p in row['pages'])
        return row
    for policy in ('incumbent', 'qtable'):
        keeper = fixtures / policy
        assert run(['--keeper-dir', str(keeper), '--era-scale', 'tiny', '--eras', '1',
                    '--ticks', '1', '--tick-frames', '1', '--fps', '0', '--scale', '1',
                    '--learning-policy', policy]) == 0
        pet = CompanionSession.load(keeper / 'companion.json')
        for _ in range(100):
            if not pet.alive: break
            pet.advance(player_action='idle')
        checks[policy + '_actual_death'] = not pet.alive
        death = copy.deepcopy(pet.lineage[0])
        pet.succeed()
        pet.save_checkpoint(keeper / 'companion.json')
        play(keeper, policy + '-adoptions', [[key(pygame.K_h)], [key(pygame.K_RETURN)],
            [key(pygame.K_b)], [key(pygame.K_a)], [key(pygame.K_l)],
            [key(pygame.K_COMMA)], [key(pygame.K_COMMA)], [key(pygame.K_COMMA)]])
        pet = CompanionSession.load(keeper / 'companion.json')
        checks[policy + '_four_actual_lives'] = len(pet.lineage) == 4
        checks[policy + '_earlier_death_preserved'] = pet.lineage[0]['death_cause'] == death['death_cause']
        checks[policy + '_replacement_not_death'] = all('death_cause' not in row for row in pet.lineage[1:3])
        checks[policy + '_policy_preserved'] = pet.learning_policy == policy
        original_companion = (keeper / 'companion.json').read_bytes()
        play(keeper, policy + '-restart-history', [[key(pygame.K_l)], [key(pygame.K_COMMA)],
            [key(pygame.K_COMMA)], [key(pygame.K_COMMA)], [key(pygame.K_F1)]])
        checks[policy + '_restart_read_unchanged'] = original_companion == (keeper / 'companion.json').read_bytes()
        state, ledger = keeper / 'campaign_state.json', keeper / 'campaign.sqlite3'
        original_state, original_ledger = state.read_bytes(), ledger.read_bytes()
        broken = b'X1 source demonstration: deliberately broken temporary campaign primary'
        state.write_bytes(broken)
        play(keeper, policy + '-recovery-cancel', [[key(pygame.K_c), key(pygame.K_u), key(pygame.K_u)],
            [key(pygame.K_f)], [key(pygame.K_c), key(pygame.K_f)], [key(pygame.K_F1)]])
        checks[policy + '_cancel_preserves_pair'] = state.read_bytes() == broken and ledger.read_bytes() == original_ledger
        checks[policy + '_inspection_pauses_care'] = original_companion == (keeper / 'companion.json').read_bytes()
        play(keeper, policy + '-recovery-confirm', [[key(pygame.K_c), key(pygame.K_u)],
            [key(pygame.K_u)], [key(pygame.K_F1)]])
        checks[policy + '_explicit_pair_restored'] = json.loads(state.read_bytes()) == json.loads(original_state)
        checks[policy + '_corrupt_bytes_retained'] = any(p.is_file() and p.read_bytes() == broken for p in keeper.rglob('*'))
        checks[policy + '_no_extra_era'] = json.loads(state.read_bytes())['era_count'] == 1
        native_env = os.environ.copy()
        native_env.pop('SDL_VIDEODRIVER', None)
        native_env.pop('SDL_AUDIODRIVER', None)
        for label in ('load', 'resume'):
            before = CompanionSession.load(keeper / 'companion.json')
            start = time.perf_counter()
            result = subprocess.run([str(bundle.resolve()), '--keeper-dir', str(keeper.resolve()),
                '--ticks', '1', '--tick-frames', '1', '--fps', '0', '--scale', '16'],
                cwd=ROOT, env=native_env, timeout=60, capture_output=True)
            after = CompanionSession.load(keeper / 'companion.json')
            passed = result.returncode == 0 and after.state['age_ticks'] == before.state['age_ticks'] + 1 and after.keeper_id == before.keeper_id and len(after.lineage) == 4 and after.learning_policy == policy
            checks[policy + '_native_' + label] = passed
            launches.append({'policy': policy, 'action': label, 'returncode': result.returncode,
                             'seconds': time.perf_counter() - start, 'passed': passed})
    hashes = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in (
        'game/src/mecha_game/app.py', 'game/src/mecha_game/session.py', 'game/src/mecha_game/chronicle.py',
        'game/src/mecha_game/campaign.py', 'game/src/mecha_game/campaign_recovery.py', 'game/src/mecha_game/era_plan.py')}
    return {'schema_version': 1, 'scope': 'Cycle 38 X1 source interaction and native process smoke',
        'checks': checks, 'passed': all(checks.values()), 'flows': flows, 'native_launches': launches,
        'source_hashes': hashes, 'bundle': str(bundle), 'bundle_sha256': hashlib.sha256(bundle.read_bytes()).hexdigest(),
        'limits': ['Source events are injected, not native keyboard automation.', 'Native processes use normal SDL drivers.',
                   'Temporary tiny eras and observed care do not measure full-scale performance or human usability.']}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixtures', type=Path, required=True)
    parser.add_argument('--screenshots', type=Path, required=True)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.fixtures, args.screenshots, args.bundle)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': result['passed'], 'checks': len(result['checks']),
                      'flows': len(result['flows']), 'native_launches': len(result['native_launches'])}))
    raise SystemExit(0 if result['passed'] else 1)
