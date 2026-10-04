"""Foreground Keeper preparation and recoverable completed-era persistence.

The journal holds an actual engine result, never a job to run unattended.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sqlite3
from pathlib import Path

from mecha_engine.storage import SCHEMA_VERSION, campaign_history, load_era_elites
from mecha_engine.genome import validate_grid
from mecha_game.campaign import ERA_SEED_STRIDE, WEATHER_NAMES, KeeperCampaign
from mecha_game.session import _document_bytes, _write_bytes_atomic

FORMAT = 'mechagotchi_era_plan_v1'


def _digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def state_digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path is not None and path.exists() else None


class EraPlan:
    def __init__(self, path):
        self.path = Path(path) if path is not None else None
        self.error = None
        self.document = dict(format=FORMAT,weather='calm',releases=[],pending=None)
        if self.path is not None and self.path.exists():
            try:
                payload = json.loads(self.path.read_text(encoding='utf-8'))
                self._validate(payload)
                self.document = payload
            except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
                self.error = f'Era preparation unavailable: {error}. Existing file preserved.'

    @property
    def weather(self): return self.document['weather']
    @property
    def releases(self): return copy.deepcopy(self.document['releases'])
    @property
    def pending(self): return copy.deepcopy(self.document['pending'])

    @staticmethod
    def _validate(payload):
        if payload['format'] != FORMAT or payload['weather'] not in WEATHER_NAMES:
            raise ValueError('unsupported preparation format or weather')
        if not isinstance(payload['releases'],list):
            raise ValueError('staged contributions are not a list')
        ids = set()
        for grid in payload['releases']:
            if not isinstance(grid,dict) or not isinstance(grid.get('grid_id'),str) or not grid['grid_id'] or grid['grid_id'] in ids:
                raise ValueError('invalid or duplicate contribution identity')
            verdict = validate_grid(grid)
            if not verdict.ok:
                raise ValueError('Invalid staged genome: ' + '; '.join(verdict.errors))
            ids.add(grid['grid_id'])
        pending = payload['pending']
        if pending is not None:
            body = {k:v for k,v in pending.items() if k != 'sha256'}
            if _digest(body) != pending['sha256']:
                raise ValueError('completed-era journal hash mismatch')
            state,era = pending['state'],pending['era']
            if (state['state_format'] != KeeperCampaign.STATE_FORMAT or
                state['era_count'] != era['era_index'] + 1 or
                era['rng_seed'] != state['base_seed'] + era['era_index'] * ERA_SEED_STRIDE or
                not isinstance(era['report'],dict) or not isinstance(era['elites'],list)):
                raise ValueError('inconsistent completed-era journal')

    def require_ready(self, *, allow_pending=False):
        if self.error: raise ValueError(self.error)
        if self.pending is not None and not allow_pending:
            raise ValueError('E finishes saving the completed era before another preparation change.')

    def _write(self, payload):
        self._validate(payload)
        if payload == self.document: return
        if self.path is not None:
            _write_bytes_atomic(self.path,_document_bytes(payload))
        self.document = copy.deepcopy(payload)

    def select_weather(self, weather):
        self.require_ready()
        self._write({**self.document,'weather':weather})

    def stage(self, grids):
        self.require_ready()
        staged = self.releases
        for grid in grids:
            if not isinstance(grid,dict) or not isinstance(grid.get('grid_id'),str) or not grid['grid_id']:
                raise ValueError('A contribution needs a grid identity; no staged creatures changed.')
            prior = next((item for item in staged if item['grid_id']==grid['grid_id']),None)
            if prior is not None and prior != grid:
                raise ValueError(f"A different creature named {grid['grid_id']} is already staged.")
            if prior is None: staged.append(copy.deepcopy(grid))
        added = len(staged)-len(self.document['releases'])
        self._write({**self.document,'releases':staged})
        return added

    def unstage_all(self):
        self.require_ready()
        self._write({**self.document,'releases':[]})

    def begin(self, campaign, era, previous_state):
        self.require_ready()
        pending = dict(state=campaign.state_payload(),era=era,previous_state=previous_state)
        pending['sha256'] = _digest(pending)
        self._write({**self.document,'pending':pending})

    def finish(self, ledger_path, state_path):
        """Commit an already recorded result; never train, evolve or infer history."""
        self.require_ready(allow_pending=True)
        pending = self.pending
        if pending is None: raise ValueError('No completed era awaits saving.')
        state,era = pending['state'],pending['era']
        if state_path is not None and state_digest(state_path) != pending['previous_state']:
            try: same = json.loads(state_path.read_text(encoding='utf-8')) == state
            except (OSError,ValueError): same = False
            if not same:
                raise ValueError('Campaign state changed outside this preparation; existing state preserved.')
        ledger_path = Path(ledger_path)
        if ledger_path.exists():
            conn = sqlite3.connect(ledger_path.resolve().as_uri()+'?mode=ro',uri=True)
            try:
                if conn.execute('PRAGMA user_version').fetchone()[0] != SCHEMA_VERSION:
                    raise ValueError('Unsupported campaign-ledger schema; existing ledger preserved.')
                try: history = campaign_history(conn,state['campaign_id'])
                except KeyError: history = {'eras':[]}
                if any(row['era_index'] > era['era_index'] for row in history['eras']):
                    raise ValueError('Campaign advanced outside this preparation; existing history preserved.')
                for row in history['eras']:
                    if row['era_index'] == era['era_index']:
                        same = all(row[k] == era[k] for k in ('report','weather','rng_seed'))
                        same = same and row['slip_profile'] == state['slip_profile']
                        same = same and load_era_elites(conn,state['campaign_id'],era['era_index']) == era['elites']
                        if not same:
                            raise ValueError('A different era occupies this position; existing history preserved.')
            finally: conn.close()
        # Restore only the exact recorded state needed by the existing writers.
        # No live simulation model or fabricated current-run history is created.
        saved = KeeperCampaign({'slip_profile':state['base_profile']},
            campaign_id=state['campaign_id'],keeper_label=state['keeper_label'],created_date=state['created_date'],
            predecessor_campaign_id=state['predecessor_campaign_id'],base_seed=state['base_seed'],
            era_config=state['era_config'],inherited_unlocks=state['inherited_unlocks'])
        saved.base_profile = state['base_profile']
        saved.base_parameters = state.get('base_parameters',saved.base_parameters)
        saved.campaign.update(status=state['status'],slip_profile=state['slip_profile'],unlocks=state['unlocks'],eras=[era])
        saved.era_offset = era['era_index']
        saved.save(ledger_path)
        if state_path is not None: saved.save_state(state_path)
        self._write({**self.document,'pending':None,'releases':[]})
        return era
