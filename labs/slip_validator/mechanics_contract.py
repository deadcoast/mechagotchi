"""Q2's shared adversarial mechanics matrix across the SLIP authorities."""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT / 'packages/mecha_engine/src', ROOT / 'labs/grid_genome'):
    sys.path.insert(0, str(path))

import jsonschema
from pydantic import ValidationError
from pydantic_contract import SLIPProfile
from slip import validate_slip as lab_validate
from slip_validator import validate_profile
from mecha_engine.slip import validate_slip as package_validate


def evaluate_cases() -> list[dict]:
    base = json.loads((ROOT / 'data/slips/valid/slip_lcd_seed.json').read_text(encoding='utf-8'))
    cases = json.loads((ROOT / 'data/slips/mechanics_cases_stage0.json').read_text(encoding='utf-8'))['cases']
    authored = jsonschema.Draft202012Validator(json.loads((ROOT / 'research/slip/slip.schema.json').read_text(encoding='utf-8')))
    generated = jsonschema.Draft202012Validator(json.loads((ROOT / 'research/slip/slip_pydantic_model.schema.json').read_text(encoding='utf-8')))
    rows = []
    for case in cases:
        profile = copy.deepcopy(base)
        profile.update(case['profile_patch'])
        before = copy.deepcopy(profile)
        try:
            SLIPProfile.model_validate(profile)
            model_ok = True
        except ValidationError:
            model_ok = False
        votes = {'authored_schema': authored.is_valid(profile), 'generated_schema': generated.is_valid(profile),
                 'pydantic': model_ok, 'package': package_validate(profile).ok,
                 'grid_lab': lab_validate(profile).ok, 'standalone_lab': validate_profile(profile)['ok']}
        rows.append({'case': case['name'], 'expected': case['expected'], 'votes': votes,
                     'inputs_preserved': profile == before})
    return rows
