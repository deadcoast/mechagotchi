"""Q2 / DR 0063: covenant authorship, with incumbent behavior as the instrument.

Preregistered in docs/development/q2-mechanics-rung.md. All contract checks
must pass; any failed check withholds authorship adoption. Scientific mechanic
parameters and DR 0059's original decision are reproduced, never retuned.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT / 'packages/mecha_engine/src', ROOT / 'game/src', ROOT / 'labs/slip_validator'):
    sys.path.insert(0, str(path))
from mecha_engine.generation import train_generation_model
from mecha_game.session import CompanionSession
from mecha_game.app import _footer_lines
from mechanics_contract import evaluate_cases
from cleanliness_mechanic_gate import build_cleanliness_mechanic_report

ARTIFACT = 'data/lifecycle/slip_mechanics_authorship_stage0.json'
BASELINE = 'data/lifecycle/slip_mechanics_incumbent_baseline.json'
REQUIRED_CHECKS = frozenset({
    'all_authorities_agree', 'package_matrix', 'profile_only_clean',
    'explicit_disable', 'explicit_enable', 'invalid_profile_refused',
    'inputs_preserved', 'incumbent_engine', 'incumbent_game',
    'dr0059_reproduced', 'game_persistence', 'player_footer', 'clean_answers',
})


def read(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def judge(checks: dict[str, bool]) -> dict:
    failed = sorted(name for name in REQUIRED_CHECKS | checks.keys() if checks.get(name) is not True)
    return {'verdict': 'withhold' if failed else 'adopt_authorship', 'failed_checks': failed,
            'rule': 'All preregistered authority, precedence, persistence, incumbent and player-readout checks must pass.'}


def build_report() -> dict:
    rows = evaluate_cases()
    driver = ROOT / 'packages/mecha_engine/tests/helpers/slip_mechanics_driver.py'
    env = dict(os.environ, PYTHONPATH=str(ROOT / 'packages/mecha_engine/src'))
    probe = json.loads(subprocess.check_output([sys.executable, '-B', str(driver), str(ROOT)], env=env, text=True))
    old_gate = build_cleanliness_mechanic_report()
    committed = read('data/lifecycle/cleanliness_mechanic_gate_stage0.json')
    old_profiles = read(BASELINE)['observations']
    game_mismatches = []
    for row in old_profiles:
        grid, profile = read(row['grid_path']), read(row['profile_path'])
        session = CompanionSession(grid, profile, model=train_generation_model([grid]))
        for action in ('feed', 'play', 'sleep'):
            session.advance(action)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'session.json'
            session.save(path)
            if digest(json.loads(path.read_text())) != row['game_save_hash'] or digest(session.snapshot()) != row['game_snapshot_hash']:
                game_mismatches.append(row['profile_path'])
    grid = read('data/seed_grids/mg_seed_001.json')
    profile = read('data/slips/valid/slip_v2_cleanliness.json')
    persistence = []
    response = None
    for override, enabled in ((None, True), ((), False)):
        session = CompanionSession(grid, profile, model=train_generation_model([grid]), mechanics=override)
        for action in ('feed', 'play', 'sleep') * 2:
            session.advance(action)
        footer = ' '.join(_footer_lines(session.snapshot(), None))
        visible = ('G clean' in footer and f"cleanliness {session.state.get('cleanliness', 0):.2f}" in footer)
        if enabled:
            before = session.state['cleanliness']
            session.advance('clean')
            response = {'before': before, 'after': session.state['cleanliness']}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'session.json'
            session.save(path)
            payload = json.loads(path.read_text())
            resumed = CompanionSession.load(path)
            same = session.snapshot() == resumed.snapshot()
            for action in ('feed', 'play', 'sleep'):
                session.advance(action)
                resumed.advance(action)
                same = same and session.snapshot() == resumed.snapshot()
            for _ in range(500):
                if not resumed.alive:
                    break
                resumed.advance()
            if resumed.alive:
                raise ValueError('Succession instrument failed to reach the incumbent bounded death.')
            resumed.succeed()
            persistence.append({'override': 'inherit' if override is None else 'explicit_empty',
                                'enabled': enabled, 'resume_matches_uninterrupted': same,
                                'save_override_preserved': ('mechanics' not in payload) if enabled else payload.get('mechanics') == [],
                                'succession_matches': ('cleanliness' in resumed.state) == enabled,
                                'player_footer_matches': visible == enabled})
    checks = {
        'all_authorities_agree': all(row['inputs_preserved'] and all(v == row['expected'] for v in row['votes'].values()) for row in rows),
        'package_matrix': not probe['matrix_mismatches'],
        'profile_only_clean': probe['profile_only_clean'], 'explicit_disable': probe['explicit_disable'],
        'explicit_enable': probe['explicit_enable'], 'invalid_profile_refused': probe['invalid_profile_refused'],
        'inputs_preserved': probe['inputs_preserved'],
        'incumbent_engine': not probe['incumbent_mismatches'] and probe['off_forms_identical'],
        'incumbent_game': not game_mismatches,
        'dr0059_reproduced': old_gate['metrics'] == committed['metrics'] and old_gate['decision'] == committed['decision'],
        'game_persistence': all(row['resume_matches_uninterrupted'] and row['save_override_preserved'] and row['succession_matches'] for row in persistence),
        'player_footer': all(row['player_footer_matches'] for row in persistence),
        'clean_answers': response['after'] > response['before'],
    }
    return {'artifact_id': 'slip_mechanics_authorship_stage0', 'status': 'q2_contract_gate', 'date': '2026-10-04',
            'purpose': 'Measure covenant authorship without changing the adopted mechanic, defaults or scientific thresholds.',
            'source_artifacts': [BASELINE, 'data/slips/mechanics_cases_stage0.json', 'data/lifecycle/cleanliness_mechanic_gate_stage0.json',
                                 'docs/development/q2-mechanics-rung.md', 'research/decision_records/0063-covenant-mechanics-authorship.md'],
            'metrics': {'authority_cases': len(rows), 'authority_votes': sum(len(row['votes']) for row in rows),
                        'incumbent_profiles': len(old_profiles), 'incumbent_engine_mismatches': probe['incumbent_mismatches'],
                        'incumbent_game_mismatches': game_mismatches, 'valid_fixtures': len(list((ROOT/'data/slips/valid').glob('*.json'))),
                        'off_forms_identical': probe['off_forms_identical'],
                        'example_profiles': len(list((ROOT/'research/slip/slip_examples').glob('*.json'))),
                        'failure_fixtures': len(list((ROOT/'data/slips/failure_cases').glob('*.json'))),
                        'checks': checks, 'clean_response': response, 'persistence': persistence,
                        'dr0059_instrument': old_gate['metrics']['instrument_check']},
            'authority_matrix': rows, 'closed_states': sorted(name for name, value in checks.items() if value),
            'blocked_states': ['native_remote_ci_unverified', 'default_covenant_adoption_requires_Q3', 'qtable_default_promotion_requires_its_separate_record'],
            'decision': judge(checks), 'next_research_step': 'Q3: preregister the default-covenant ADOPT/REFUSE measurement and exact evidence cascade.'}


def write_report(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / ARTIFACT)
    args = parser.parse_args()
    report = build_report()
    write_report(args.output, report)
    print(json.dumps({'decision': report['decision'], 'metrics': report['metrics']}, indent=2))
    raise SystemExit(0 if report['decision']['verdict'] == 'adopt_authorship' else 1)
