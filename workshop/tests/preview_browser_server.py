"""Bounded preview acceptance fixture; real engine, temporary native save homes only.

Commands change only the first test Keeper. No era, study, live save or historical
recording is advanced. The browser owns delayed HTTP presentation instrumentation.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
for source in ('workshop/server', 'game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT / source))
from workshop_server import start_workshop_server
from mecha_game.session import CompanionSession, load_session_inputs
from mecha_game.campaign import KeeperCampaign

scratch = Path(sys.argv[1]).resolve()
scratch.mkdir(parents=True, exist_ok=True)
grid, profile, model = load_session_inputs(
    ROOT / 'data/seed_grids_16x16/mg_seed16_001_beetle.json',
    ROOT / 'data/slips/valid/slip_v2_cleanliness.json')
keepers, pets, servers = [], [], []
for name, body in (('workload', 'workload-v1'), ('legacy', 'legacy')):
    home = scratch / name
    home.mkdir()
    pet = CompanionSession(deepcopy(grid), deepcopy(profile), model=model,
                           body_response=body, name='Preview ' + name)
    pet.bind_campaign('preview_browser_' + name)
    pet.save(home / 'companion.json')
    campaign = KeeperCampaign({'slip_profile': deepcopy(profile)},
        campaign_id='preview_browser_' + name,
        era_config={'population': 3, 'generations': 2}, body_response=body)
    campaign.save(home / 'campaign.sqlite3')
    campaign.save_state(home / 'campaign_state.json')
    incompatible = deepcopy(profile)
    incompatible['profile_id'] = 'preview_incompatible_palette'
    incompatible['grid']['allowed_palettes'] = ['gameboy_gray']
    slips = home / 'workshop/slips'
    slips.mkdir(parents=True)
    (slips / 'preview_incompatible_palette.json').write_text(json.dumps(incompatible), encoding='utf-8')
    keepers.append(home)
    pets.append(pet)
    servers.append(start_workshop_server(port=0, keeper_dir=home))
lab = scratch / 'lab'
(lab / 'slips').mkdir(parents=True)
standalone_profile = deepcopy(profile)
standalone_profile['profile_id'] = 'preview_standalone_profile'
(lab / 'slips/preview_standalone_profile.json').write_text(json.dumps(standalone_profile), encoding='utf-8')
servers.append(start_workshop_server(port=0, grids_dir=lab / 'grids',
    slips_dir=lab / 'slips', released_dir=lab / 'released',
    metrics_dir=lab / 'metrics', session_dir=lab / 'session'))


def hashes(home):
    return {str(p.relative_to(home)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(home.rglob('*')) if p.is_file()}


def status(event='ready', sequence=0):
    print(json.dumps({'port': servers[0].server_address[1],
        'legacy_port': servers[1].server_address[1],
        'lab_port': servers[2].server_address[1], 'scratch': str(scratch),
        'keepers': [str(p) for p in keepers], 'event': event, 'sequence': sequence,
        'body_response': pets[0].body_response, 'legacy_hashes': hashes(keepers[1])}), flush=True)


status()
try:
    for line in sys.stdin:
        command = json.loads(line)
        op = command['op']
        if op == 'stop':
            break
        if op == 'switch':
            # Actual supported new-life adoption, retaining campaign/history.
            pets[0] = pets[0].adopt(deepcopy(grid), deepcopy(profile),
                name='Preview ' + command['body_response'],
                body_response=command['body_response'])
            pets[0].save(keepers[0] / 'companion.json')
        elif op == 'advance':
            pets[0].advance()
            pets[0].save(keepers[0] / 'companion.json')
        elif op == 'missing':
            (keepers[0] / 'companion.json').rename(keepers[0] / 'companion.fixture-hidden')
        elif op == 'restore':
            (keepers[0] / 'companion.fixture-hidden').rename(keepers[0] / 'companion.json')
        elif op != 'inspect':
            raise ValueError('Unsupported bounded fixture command: ' + op)
        status(op, command['sequence'])
finally:
    for server in servers:
        server.shutdown()
        server.server_close()

