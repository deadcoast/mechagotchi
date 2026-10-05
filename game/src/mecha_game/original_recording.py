"""Bounded original best-evaluation capture and idempotent artifact persistence."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from mecha_game.replay import replay_from_lived, packet_or_errors

FORMAT = 'mechagotchi_original_evaluation_v1'
MAX_REPLAY_FRAMES = 2048
MAX_REPLAY_BYTES = 8 * 1024 * 1024


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode('utf-8')


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


class BestEvaluationRecording:
    def __init__(self, campaign_id, era_index, era_seed, covenant, weather, config):
        self.covenant = copy.deepcopy(covenant)
        self.weather = weather
        self.document = dict(recording_format=FORMAT, campaign_id=campaign_id,
                             era_index=era_index, era_seed=era_seed,
                             status='unavailable', reason='No final elite evaluation was recorded.', replay=None)
        self.enabled = 1 + config['damage_cycles'] * (2 + config['ticks']) <= MAX_REPLAY_FRAMES
        if not self.enabled:
            self.document['reason'] = f'Original recording exceeds the {MAX_REPLAY_FRAMES}-frame limit.'

    def capture(self, record):
        replay = replay_from_lived(record['candidate_grid'], self.covenant, record['lived'],
            damage_cycles=record['damage_cycles'], ticks=record['ticks'],
            dropout_rate=record['effective_dropout_rate'], rng_seed=record['run_seed'])
        replay['engine_surface'] = 'mecha_engine.runtime.evolve: original live_cycle evaluation'
        replay['honest_label'] = 'Original era evaluation: actual damage, repair and lifecycle ticks; final best elite.'
        replay['evaluation'] = {
            'kind': FORMAT, 'campaign_id': self.document['campaign_id'],
            'era_index': self.document['era_index'], 'era_seed': self.document['era_seed'],
            'generation_index': record['generation_index'], 'candidate_index': record['candidate_index'],
            'niche_key': record['niche_key'], 'fitness': record['fitness'],
            'weather': self.weather, 'generation_weather': record['generation_weather'],
            'covenant_sha256': digest(self.covenant),
            'original_grid': record['candidate_grid'], 'final_grid': record['lived']['final_grid'],
            'original_grid_sha256': digest(record['candidate_grid']),
            'final_grid_sha256': digest(record['lived']['final_grid']),
        }
        candidate = dict(self.document, status='recorded', reason=None, replay=replay)
        if len(replay['frames']) > MAX_REPLAY_FRAMES or len(encoded(candidate)) > MAX_REPLAY_BYTES:
            self.document.update(status='unavailable', reason='Original recording exceeds the frame/byte limit.', replay=None)
        else:
            self.document = candidate

    def finish(self, era):
        validate_recording(self.document, self.document['campaign_id'], era, self.covenant)
        return copy.deepcopy(self.document)


def validate_recording(document, campaign_id, era, covenant):
    """Bind captured footage to the actual stored scientific report and best elite."""
    if (document['recording_format'] != FORMAT or document['campaign_id'] != campaign_id or
        document['era_index'] != era['era_index'] or document['era_seed'] != era['rng_seed']):
        raise ValueError('Original recording does not match its campaign/era.')
    if document['status'] == 'unavailable':
        if document['replay'] is not None or not isinstance(document['reason'], str) or not document['reason']:
            raise ValueError('Invalid unavailable recording status.')
        return
    if document['status'] != 'recorded' or document['reason'] is not None:
        raise ValueError('Invalid original recording status.')
    replay = document['replay']; origin = replay['evaluation']; params = replay['parameters']
    if (origin['kind'] != FORMAT or origin['campaign_id'] != campaign_id or
        origin['era_index'] != era['era_index'] or origin['era_seed'] != era['rng_seed'] or
        origin['covenant_sha256'] != digest(covenant)):
        raise ValueError('Original recording provenance does not match this era.')
    generation, index = origin['generation_index'], origin['candidate_index']
    if type(generation) is not int or type(index) is not int or generation < 0 or index < 0:
        raise ValueError('Invalid original evaluation position.')
    report = era['report']
    try: creature = report['generations'][generation]['creatures'][index]
    except IndexError as error: raise ValueError('Original evaluation is outside the saved report.') from error
    best = max(era['elites'], key=lambda item: (item['fitness'], item['niche_key']))
    if (origin['final_grid'] != best['grid'] or origin['niche_key'] != best['niche_key'] or
        origin['fitness'] != best['fitness'] or origin['original_grid']['grid_id'] != creature['candidate_grid_id'] or
        origin['original_grid_sha256'] != digest(origin['original_grid']) or
        origin['final_grid_sha256'] != digest(origin['final_grid'])):
        raise ValueError('Original recording does not belong to the selected best elite.')
    weather = (report.get('cubff_pressure') or {}).get('by_generation', [])
    pressure = weather[generation] if weather else None
    dropout = round(report['dropout_rate'] * pressure['dropout_multiplier'], 6) if pressure else report['dropout_rate']
    if (params['rng_seed'] != era['rng_seed'] + generation * 100000 + index or
        params['ticks'] != report['ticks'] or params['damage_cycles'] != report['damage_cycles'] or
        params['dropout_rate'] != dropout or origin['generation_weather'] != pressure or
        origin['weather'] != era['weather']['forecast'] or replay['live']['cycles'] != creature['cycles']):
        raise ValueError('Original recording seed, weather or cycle evidence does not match the report.')
    if replay['creature']['grid_id'] != origin['original_grid']['grid_id']:
        raise ValueError('Original recording birth identity does not match.')
    birth, errors = packet_or_errors(origin['original_grid'])
    if replay['frames'][0]['packet'] != birth or replay['frames'][0]['validation_errors'] != errors:
        raise ValueError('Original recording birth packet does not match its captured grid.')
    repairs = [frame for frame in replay['frames'] if frame['phase'] == 'repair']
    final_packet, errors = packet_or_errors(origin['final_grid'])
    if not repairs or repairs[-1]['packet'] != final_packet:
        raise ValueError('Original recording final body does not match its saved elite.')
    if replay['frame_count'] > MAX_REPLAY_FRAMES or len(encoded(document)) > MAX_REPLAY_BYTES:
        raise ValueError('Original recording exceeds its storage limit.')


def save_original_recording(document, keeper_dir, ledger_path):
    """Finish the journaled bytes and pointer once; preserve any conflicting file."""
    from mecha_engine.storage import open_ledger, load_replay_rows, record_replay
    from mecha_game.session import _write_bytes_atomic
    keeper = Path(keeper_dir)
    directory = (keeper / 'replays').resolve()
    path = directory / f"{document['campaign_id']}_era{document['era_index']}.json"
    if not path.resolve().is_relative_to(directory):
        raise ValueError('Original recording name leaves its recordings directory.')
    payload = encoded(document); sha = hashlib.sha256(payload).hexdigest()
    conn = open_ledger(ledger_path)
    try:
        rows = [row for row in load_replay_rows(conn, document['campaign_id']) if row['era_index'] == document['era_index']]
        if rows and (len(rows) != 1 or rows[0]['artifact_path'] != path.name or rows[0]['artifact_sha256'] != sha):
            raise ValueError('Conflicting recording pointer preserved; completed result remains pending.')
        if path.exists() and path.read_bytes() != payload:
            raise ValueError('Conflicting recording file preserved; completed result remains pending.')
        if not path.exists():
            directory.mkdir(parents=True, exist_ok=True)
            _write_bytes_atomic(path, payload)
        if not rows:
            record_replay(conn, document['campaign_id'], document['era_index'], path.name, sha)
    finally:
        conn.close()
