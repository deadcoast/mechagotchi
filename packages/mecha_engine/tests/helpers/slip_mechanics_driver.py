import copy
import hashlib
import json
import sys
from pathlib import Path

from mecha_engine.lifecycle import initial_state, run_episode
from mecha_engine.slip import validate_slip

root = Path(sys.argv[1])
read = lambda name: json.loads((root / name).read_text(encoding='utf-8'))
digest = lambda value: hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
base = read('data/slips/valid/slip_lcd_seed.json')
grid = read('data/seed_grids/mg_seed_001.json')
matrix = []
for case in read('data/slips/mechanics_cases_stage0.json')['cases']:
    profile = copy.deepcopy(base)
    profile.update(case['profile_patch'])
    if validate_slip(profile).ok != case['expected']:
        matrix.append(case['name'])
profile = dict(base, slip_version='0.2.0', mechanics={'cleanliness': True})
before = copy.deepcopy((grid, profile))

off = dict(base, slip_version='0.2.0')
off_forms_identical = all(
    initial_state(grid, dict(off, mechanics=block)) == initial_state(grid, off)
    and run_episode(grid, dict(off, mechanics=block), ticks=72, rng_seed=123)
    == run_episode(grid, off, ticks=72, rng_seed=123)
    for block in ({}, {'cleanliness': False})
)

def succeeds(action):
    try:
        return bool(action())
    except (ValueError, TypeError, KeyError):
        return False

def disabled():
    assert 'cleanliness' not in initial_state(grid, profile, mechanics=())
    assert 'final_cleanliness' not in run_episode(grid, profile, mechanics=[], ticks=3)
    try:
        run_episode(grid, profile, mechanics=(), actions=['clean'], ticks=1)
    except ValueError as error:
        return 'unsupported lifecycle action: clean' in str(error)
    return False

invalid_refused = True
for bad in (None, {'cleanliness': 1}, {'unknown': True}):
    for override in ((), ('cleanliness',)):
        try:
            initial_state(grid, dict(profile, mechanics=bad), mechanics=override)
            invalid_refused = False
        except ValueError:
            pass

incumbent = []
for row in read('data/lifecycle/slip_mechanics_incumbent_baseline.json')['observations']:
    old_grid, old_profile = read(row['grid_path']), read(row['profile_path'])
    if digest(old_profile) != row['profile_hash'] or digest(old_grid) != row['grid_hash']:
        incumbent.append(row['profile_path'] + ': input fixture changed')
    if digest(initial_state(old_grid, old_profile)) != row['initial_state_hash']:
        incumbent.append(row['profile_path'] + ': state')
    for policy, expected in row['episode_hashes'].items():
        if digest(run_episode(old_grid, old_profile, policy=policy, ticks=72, rng_seed=123)) != expected:
            incumbent.append(row['profile_path'] + ': ' + policy)

result = {'matrix_mismatches': matrix,
          'profile_only_clean': succeeds(lambda: 'final_cleanliness' in run_episode(grid, profile, actions=['clean'], ticks=1)),
          'explicit_disable': succeeds(disabled),
          'explicit_enable': succeeds(lambda: 'cleanliness' in initial_state(grid, dict(profile, mechanics={'cleanliness': False}), mechanics=('cleanliness',))),
          'invalid_profile_refused': invalid_refused, 'incumbent_mismatches': incumbent,
          'off_forms_identical': off_forms_identical,
          'inputs_preserved': (grid, profile) == before}
print(json.dumps(result))
