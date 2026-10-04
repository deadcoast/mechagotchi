"""Read existing DR 0022/0023 recordings without resuming a live campaign."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

from mecha_engine.storage import SCHEMA_VERSION, load_replay_rows
from mecha_game.rasterize import rasterize_cells
from mecha_game.replay import REPLAY_FORMAT, ReplayPlayer, overlay_wounds


def _validate(replay, expected_seed):
    """Validate what the existing player consumes; retain every stored value."""
    if replay['replay_format'] != REPLAY_FORMAT:
        raise ValueError('Unsupported replay format.')
    frames = replay['frames']
    if not isinstance(frames, list) or not frames or replay['frame_count'] != len(frames):
        raise ValueError('The recording has an invalid frame count.')
    if replay['parameters']['rng_seed'] != expected_seed:
        raise ValueError('The recording seed does not match the selected era.')
    if not isinstance(replay['creature']['grid_id'], str):
        raise ValueError('The recording has no valid creature identity.')
    if 'honest_label' in replay and not isinstance(replay['honest_label'], str):
        raise ValueError('The recording has an invalid provenance label.')
    player = ReplayPlayer(replay)
    for index, frame in enumerate(frames):
        if frame['frame'] != index or frame['phase'] not in ('birth', 'wound', 'repair', 'episode_tick'):
            raise ValueError('The recording has an invalid frame sequence.')
        if type(frame['cycle']) is not int or frame['cycle'] < 0:
            raise ValueError('The recording has an invalid cycle.')
        if frame['phase'] in ('birth', 'repair'):
            packet = frame['packet']
            if packet is None:
                if not frame['validation_errors'] or not all(isinstance(x, str) for x in frame['validation_errors']):
                    raise ValueError('An unavailable body must retain its validator errors.')
            else:
                width, height = packet['grid_size']
                if any(type(v) is not int or v <= 0 for v in (width, height)):
                    raise ValueError('The recorded body has invalid dimensions.')
                if any(type(c['x']) is not int or type(c['y']) is not int or
                       not 0 <= c['x'] < width or not 0 <= c['y'] < height for c in packet['cells']):
                    raise ValueError('The recorded body has invalid cell coordinates.')
                rasterize_cells(packet)
        if frame['phase'] == 'wound':
            if frame['removed_cell_count'] != len(frame['removed_cells']):
                raise ValueError('The recorded wound count is inconsistent.')
            overlay_wounds((), frame['removed_cells'])
        if frame['phase'] == 'episode_tick' and (type(frame['tick']) is not int or not isinstance(frame['entry'], dict)):
            raise ValueError('The recording has an invalid episode tick.')
        player.index = index
        player.caption()
    if frames[0]['phase'] != 'birth':
        raise ValueError('The recording is missing its birth frame.')


def load_saved_replay(keeper_dir, campaign_id, era_index, *, expected_seed):
    """Return the exact indexed recording, None if none exists, or an explicit error.

    Hash normalized UTF-8 text as the existing writer/loader do. In particular,
    older Windows recordings have CRLF bytes but their ledger SHA covers LF text.
    """
    keeper = Path(keeper_dir)
    ledger = keeper / 'campaign.sqlite3'
    if not ledger.is_file():
        return None
    try:
        conn = sqlite3.connect(ledger.resolve().as_uri() + '?mode=ro', uri=True)
        try:
            if conn.execute('PRAGMA user_version').fetchone()[0] != SCHEMA_VERSION:
                raise ValueError('Unsupported campaign-ledger schema version.')
            rows = [row for row in load_replay_rows(conn, campaign_id) if row['era_index'] == era_index]
        finally:
            conn.close()
        if not rows:
            return None
        if len(rows) != 1:
            raise ValueError('The era has multiple replay pointers; selection is ambiguous.')
        row = rows[0]
        directory = (keeper / 'replays').resolve()
        relative = Path(row['artifact_path'])
        path = (directory / relative).resolve()
        if relative.is_absolute() or '..' in relative.parts or not path.is_relative_to(directory):
            raise ValueError('The replay pointer leaves its recordings directory.')
        payload = path.read_text(encoding='utf-8')
        if hashlib.sha256(payload.encode('utf-8')).hexdigest() != row['artifact_sha256']:
            raise ValueError('The saved recording fails its recorded SHA256; it was not replaced.')
        replay = json.loads(payload)
        _validate(replay, expected_seed)
        return replay
    except (OSError, sqlite3.Error, KeyError, TypeError, AttributeError, IndexError, UnicodeError) as error:
        raise ValueError('The saved recording cannot be read or displayed.') from error


def fit_recorded_panel(raster, width, height, scale):
    """Nearest-neighbor fit with letterboxing; packets keep their own dimensions."""
    source_h, source_w = len(raster), len(raster[0])
    target_w, target_h = width * scale, height * scale
    ratio = min(target_w / source_w, target_h / source_h)
    fitted_w, fitted_h = max(1, int(source_w * ratio)), max(1, int(source_h * ratio))
    left, top = (target_w - fitted_w) // 2, (target_h - fitted_h) // 2
    return tuple(tuple(raster[min(source_h - 1, int((y - top) / ratio))]
                             [min(source_w - 1, int((x - left) / ratio))]
                       if left <= x < left + fitted_w and top <= y < top + fitted_h else (16, 18, 16)
                       for x in range(target_w)) for y in range(target_h))
