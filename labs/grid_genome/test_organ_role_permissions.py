"""X8 preregistered allowed-organ-role authority contract; no cohort measurement."""
import copy
import json
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
for directory in (ROOT / 'labs/grid_genome', ROOT / 'labs/slip_validator'):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))
import slip
from slip_validator import validate_profile
from pydantic_contract import SLIPProfile, _generated_schema
from pydantic import ValidationError
from jsonschema import Draft202012Validator

ALL = ['body_core', 'sensor', 'expression', 'locomotion', 'ornament', 'effect']
START = ALL[:4]

def profile():
    return json.loads((ROOT / 'data/slips/valid/slip_v2_cleanliness.json').read_text())

def votes(value):
    authored = json.loads((ROOT / 'research/slip/slip.schema.json').read_text())
    try:
        SLIPProfile.model_validate(value)
        pydantic = True
    except ValidationError:
        pydantic = False
    return {'lab': slip.validate_slip(value).ok,
            'validator': validate_profile(value)['ok'], 'pydantic': pydantic,
            'authored_schema': Draft202012Validator(authored).is_valid(value),
            'generated_schema': Draft202012Validator(_generated_schema()).is_valid(value)}

class OrganRolePermissionsTests(unittest.TestCase):
    def assert_votes(self, value, expected):
        original = copy.deepcopy(value)
        for authority, verdict in votes(value).items():
            with self.subTest(authority=authority, value=value.get('grid')):
                self.assertEqual(expected, verdict)
        self.assertEqual(original, value)

    def test_absence_retains_existing_v1_and_v2_contracts(self):
        for path in sorted((ROOT / 'data/slips/valid').glob('*.json')):
            self.assert_votes(json.loads(path.read_text()), True)

    def test_optional_six_role_vocabulary_accepts_supported_subsets(self):
        for allowed in (START, ALL, ['body_core', 'sensor', 'expression']):
            p = profile(); p['grid']['allowed_organ_roles'] = allowed
            self.assert_votes(p, True)

    def test_bad_field_values_refuse_at_every_authority(self):
        for allowed in (None, [], 'sensor', {}, ['unknown'], [True], [['sensor']],
                        START + ['sensor'], ['body_core', 'sensor']):
            with self.subTest(allowed=allowed):
                p = profile(); p['grid']['allowed_organ_roles'] = allowed
                self.assert_votes(p, False)

    def test_v1_does_not_accept_the_new_optional_field(self):
        p = json.loads((ROOT / 'data/slips/valid/slip_lcd_seed.json').read_text())
        p['grid']['allowed_organ_roles'] = ALL
        self.assert_votes(p, False)

    def test_required_role_vocabulary_remains_three(self):
        for role in ('locomotion', 'ornament', 'effect'):
            p = profile(); p['grid']['allowed_organ_roles'] = ALL
            p['grid']['required_organ_roles'] = [role]
            self.assert_votes(p, False)

    def test_unknown_grid_key_remains_rejected(self):
        p = profile(); p['grid']['allowed_organ_roles'] = ALL
        p['grid']['allowed_organ_role'] = ALL
        self.assert_votes(p, False)

    def test_role_alignment_uses_actual_organ_roles(self):
        p = profile(); p['grid']['allowed_organ_roles'] = START
        for path in sorted((ROOT / 'data/seed_grids_16x16').glob('*.json')):
            grid = json.loads(path.read_text()); before = copy.deepcopy(grid)
            legacy = slip.is_grid_aligned(grid, profile())
            present = {organ['role'] for organ in grid['organs'].values()}
            result = slip.is_grid_aligned(grid, p)
            with self.subTest(grid=grid['grid_id']):
                self.assertEqual(legacy.ok and present <= set(START), result.ok)
                for forbidden in sorted(present - set(START)):
                    self.assertIn('organ role not allowed by SLIP: ' + forbidden, result.errors)
            self.assertEqual(before, grid)

    def test_all_roles_retains_legacy_alignment_and_errors(self):
        p = profile(); p['grid']['allowed_organ_roles'] = ALL
        for path in sorted((ROOT / 'data/seed_grids_16x16').glob('*.json')):
            grid = json.loads(path.read_text())
            self.assertEqual(slip.is_grid_aligned(grid, profile()), slip.is_grid_aligned(grid, p))

    def test_malformed_roles_refuse_instead_of_crashing_permission_admission(self):
        p = profile(); p['grid']['allowed_organ_roles'] = START
        original = json.loads((ROOT / 'data/seed_grids_16x16/mg_seed16_001_beetle.json').read_text())
        for bad in (None, True, 42, [], {}):
            grid = copy.deepcopy(original)
            grid['organs']['bad'] = {'role': bad}
            grid['organs']['forbidden'] = {'role': 'effect'}
            with self.subTest(bad=bad):
                result = slip.is_grid_aligned(grid, p)
                self.assertFalse(result.ok)
                self.assertIn('organ role not allowed by SLIP: effect', result.errors)
                self.assertTrue(any('organ role must be a string for SLIP:' in error for error in result.errors))

    def test_frozen_v1_projection_removes_only_optional_v2_role_permission(self):
        p = profile(); original = copy.deepcopy(p)
        expected = copy.deepcopy(slip.v01_projection(p))
        p['grid']['allowed_organ_roles'] = START
        projected = slip.v01_projection(p)
        self.assertEqual(expected, projected)
        self.assertTrue(slip.validate_slip(projected).ok)
        self.assertEqual(START, p['grid']['allowed_organ_roles'])
        self.assertEqual(original['grid'], projected['grid'])
        self.assertIs(projected, slip.v01_projection(projected))

    def test_saved_pydantic_schema_matches_generation(self):
        saved = json.loads((ROOT / 'research/slip/slip_pydantic_model.schema.json').read_text())
        self.assertEqual(_generated_schema(), saved)

if __name__ == '__main__': unittest.main()
