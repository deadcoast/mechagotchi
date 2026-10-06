"""Package-only X8 role authority probe; no scientific simulation."""
import argparse
import copy
import json
from pathlib import Path
from mecha_engine.slip import validate_slip, is_grid_aligned

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo-root', type=Path, required=True)
    root = parser.parse_args().repo_root
    base = json.loads((root / 'data/slips/valid/slip_v2_cleanliness.json').read_text())
    roles = ['body_core', 'sensor', 'expression', 'locomotion', 'ornament', 'effect']
    report = {'valid': [], 'invalid': [], 'alignment': [], 'absence': [], 'pure': []}
    for allowed in (roles[:3], roles[:4], roles[:5], roles):
        profile = copy.deepcopy(base); profile['grid']['allowed_organ_roles'] = allowed
        before = copy.deepcopy(profile)
        report['valid'].append(validate_slip(profile).ok)
        for path in sorted((root / 'data/seed_grids_16x16').glob('*.json')):
            grid = json.loads(path.read_text()); original = copy.deepcopy(grid)
            legacy = is_grid_aligned(grid, base)
            actual = is_grid_aligned(grid, profile)
            present = {organ['role'] for organ in grid['organs'].values()}
            expected = legacy.ok and present <= set(allowed)
            report['alignment'].append(actual.ok == expected)
            if allowed == roles:
                report['absence'].append(actual == legacy)
            report['pure'].append(grid == original)
        report['pure'].append(profile == before)
    for allowed in (None, [], {}, 'sensor', ['unknown'], [True], [['sensor']],
                    roles + ['sensor'], ['sensor']):
        profile = copy.deepcopy(base); profile['grid']['allowed_organ_roles'] = allowed
        report['invalid'].append(not validate_slip(profile).ok)
    profile = json.loads((root / 'data/slips/valid/slip_lcd_seed.json').read_text())
    profile['grid']['allowed_organ_roles'] = roles
    report['invalid'].append(not validate_slip(profile).ok)
    for role in roles[3:]:
        profile = copy.deepcopy(base); profile['grid']['required_organ_roles'] = [role]
        profile['grid']['allowed_organ_roles'] = roles
        report['invalid'].append(not validate_slip(profile).ok)
    report['malformed_roles'] = []
    profile = copy.deepcopy(base); profile['grid']['allowed_organ_roles'] = roles[:4]
    original = json.loads((root / 'data/seed_grids_16x16/mg_seed16_001_beetle.json').read_text())
    for bad in (None, True, 42, [], {}):
        grid = copy.deepcopy(original)
        grid['organs']['bad'] = {'role': bad}
        grid['organs']['forbidden'] = {'role': 'effect'}
        result = is_grid_aligned(grid, profile)
        report['malformed_roles'].append(not result.ok and
            'organ role not allowed by SLIP: effect' in result.errors and
            any('organ role must be a string for SLIP:' in error for error in result.errors))
    print(json.dumps(report))

if __name__ == '__main__': main()
