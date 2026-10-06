"""Foreground Keeper preparation and recoverable completed-era persistence.

The journal holds an actual engine result, never a job to run unattended.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path

from mecha_engine.genome import validate_grid
from mecha_game.campaign import ERA_SEED_STRIDE, WEATHER_NAMES, KeeperCampaign
from mecha_game.session import _document_bytes, _write_bytes_atomic
from mecha_game.campaign_recovery import require_no_restore, save_campaign_checkpoint, validate_era_elites, validate_founder_records, validate_ledger_state

FORMAT = 'mechagotchi_era_plan_v1'
RECORDING_FORMAT = 'mechagotchi_era_plan_v2'
EXECUTION_FORMAT = 'mechagotchi_era_plan_v3'
POPULATION_FORMAT = 'mechagotchi_era_plan_v4'


def _digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def state_digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path is not None and path.exists() else None


def _validate_completed_era(pending):
    """Check all writer/continuation fields before any durable result is touched."""
    try:
        state, era = pending['state'], pending['era']
        previous = pending['previous_state']
        if previous is not None and (not isinstance(previous, str) or len(previous) != 64 or
                                      any(c not in '0123456789abcdef' for c in previous)):
            raise ValueError('Invalid previous-state identity in completed-era journal.')
        if type(era['rng_seed']) is not int:
            raise ValueError('Invalid completed-era seed.')
        report = era['report']; summary = report['summary']; archive = summary['archive']
        if not isinstance(report['decision']['status'], str):
            raise ValueError('Invalid completed-era decision.')
        for value in (archive['filled_niches'], summary['max_lineage_generation'], report['generations_requested']):
            if type(value) is not int or value < 0:
                raise ValueError('Invalid completed-era count.')
        for value in (archive['coverage'], archive['qd_score']):
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError('Invalid completed-era archive metric.')
        if not isinstance(report['generations'], list):
            raise ValueError('Invalid completed-era generations.')
        from mecha_game.execution import population_ended, population_arguments, body_arguments
        policy = state.get('population_policy', 'legacy_archive')
        extinct = population_ended(report, era['elites'], policy)
        if extinct != era['derived']['went_extinct'] or state['status'] != ('extinct' if extinct else 'active'):
            raise ValueError('Completed-era outcome disagrees with its recorded result.')
        weather = era['weather']
        if weather['forecast'] not in WEATHER_NAMES or not isinstance(weather['snapshot_ids'], list):
            raise ValueError('Invalid completed-era weather.')
        validate_era_elites(era['elites'], report)
        validate_founder_records(era)
        if era.get('execution') is not None:
            from mecha_engine.storage import validate_execution
            from mecha_game.execution import blob_json, result_digest, validate_execution_outputs
            bundle = era['execution']
            validate_execution(bundle)
            validate_execution_outputs(bundle, report, era['elites'])
            manifest = bundle['manifest']
            if body_arguments(bundle).get('body_response', 'legacy') != state.get('body_response', 'legacy'):
                raise ValueError('Completed-era body response differs from its campaign state.')
            if population_arguments(bundle).get('population_policy', 'legacy_archive') != policy:
                raise ValueError('Completed-era population policy differs from its campaign state.')
            if policy == 'generation_survivors_v1' and state['population_continuation'] != dict(
                    founder_start_mode='continue', era_index=era['era_index'],
                    ordered_breeders_sha256=manifest.get('ordered_breeders_sha256')):
                raise ValueError('Completed-era living continuation differs from its output.')
            if (manifest['campaign_id'] != state['campaign_id'] or manifest['era_index'] != era['era_index']
                    or manifest['rng_seed'] != era['rng_seed'] or manifest['report_sha256'] != result_digest(report)
                    or manifest['elites_sha256'] != result_digest(era['elites'])
                    or result_digest(blob_json(bundle, manifest['inputs']['covenant_sha256'])) != result_digest(state['slip_profile'])):
                raise ValueError('Completed-era execution evidence disagrees with its recorded result.')
    except (KeyError, TypeError, AttributeError) as error:
        raise ValueError('Incomplete completed-era journal; existing files preserved.') from error


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
    def survival_regime(self): return self.document.get('survival_regime', 'sheltered')
    @property
    def cubff_density_pressure(self): return self.document.get('cubff_density_pressure', False)
    @property
    def releases(self): return copy.deepcopy(self.document['releases'])
    @property
    def release_sources(self):
        return copy.deepcopy(self.document.get('release_sources', [None] * len(self.document['releases'])))
    @property
    def pending(self): return copy.deepcopy(self.document['pending'])

    @staticmethod
    def _validate(payload):
        if payload['format'] not in (FORMAT, RECORDING_FORMAT, EXECUTION_FORMAT, POPULATION_FORMAT) or payload['weather'] not in WEATHER_NAMES:
            raise ValueError('unsupported preparation format or weather')
        if payload['format'] == POPULATION_FORMAT:
            if payload.get('survival_regime') not in ('sheltered', 'stress_probe') or type(payload.get('cubff_density_pressure')) is not bool:
                raise ValueError('Invalid versioned era preparation inputs')
        elif 'survival_regime' in payload or 'cubff_density_pressure' in payload:
            raise ValueError('Extended preparation inputs require their versioned format')
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
        if payload['format'] in (EXECUTION_FORMAT, POPULATION_FORMAT):
            from mecha_game.execution import validate_source_records
            validate_source_records(payload['release_sources'], count=len(payload['releases']), grids=payload['releases'])
        elif 'release_sources' in payload:
            raise ValueError('Source-bearing preparation requires the current format.')
        pending = payload['pending']
        if payload['format'] in (EXECUTION_FORMAT, POPULATION_FORMAT) and pending is not None and not pending.get('era', {}).get('execution'):
            raise ValueError('Execution-bearing journal is missing its immutable execution evidence.')
        if payload['format'] not in (EXECUTION_FORMAT, POPULATION_FORMAT) and pending is not None and pending.get('era', {}).get('execution') is not None:
            raise ValueError('Execution evidence requires the current journal format.')
        if payload['format'] == RECORDING_FORMAT and (not isinstance(pending, dict) or pending.get('recording') is None):
            raise ValueError('Recording-bearing journal is missing its completed footage status.')
        if pending is not None:
            body = {k:v for k,v in pending.items() if k != 'sha256'}
            if _digest(body) != pending['sha256']:
                raise ValueError('completed-era journal hash mismatch')
            state,era = pending['state'],pending['era']
            KeeperCampaign.validate_state_payload(state)
            if (state['era_count'] != era['era_index'] + 1 or
                era['rng_seed'] != state['base_seed'] + era['era_index'] * ERA_SEED_STRIDE or
                type(era['era_index']) is not int or era['era_index'] < 0 or
                not isinstance(era['report'],dict) or not isinstance(era['elites'],list) or
                not isinstance(era.get('derived'),dict) or type(era['derived'].get('went_extinct')) is not bool):
                raise ValueError('inconsistent completed-era journal')
            _validate_completed_era(pending)
            if payload['format'] == POPULATION_FORMAT:
                from mecha_game.execution import population_arguments
                options = population_arguments(era['execution'])
                if (options.get('survival_regime', 'sheltered') != payload['survival_regime'] or
                        options.get('cubff_density_pressure', False) != payload['cubff_density_pressure']):
                    raise ValueError('Completed result differs from its prepared survival inputs')
            elif state['state_format'] == KeeperCampaign.POPULATION_STATE_FORMAT:
                raise ValueError('Living-population recovery requires the versioned journal')
            if pending.get('recording') is not None:
                from mecha_game.original_recording import validate_recording
                validate_recording(pending['recording'], state['campaign_id'], era, state['slip_profile'])

    def require_ready(self, *, allow_pending=False):
        if self.error: raise ValueError(self.error)
        if self.pending is not None and not allow_pending:
            raise ValueError('E finishes saving the completed era before another preparation change.')

    def _write(self, payload):
        from mecha_game.compatibility import keeper_write_lock, require_keeper_writable, require_campaign_compatibility
        with keeper_write_lock(self.path.parent if self.path is not None else None):
            if self.path is not None:
                require_keeper_writable(self.path.parent, allow_pending=True)
                if payload.get('pending') is not None:
                    require_campaign_compatibility(payload['pending']['state'], state_path=self.path)
            return self._write_compatible(payload)

    def _write_compatible(self, payload):
        self._validate(payload)
        if payload == self.document: return
        if self.path is not None:
            _write_bytes_atomic(self.path,_document_bytes(payload))
        self.document = copy.deepcopy(payload)

    def select_weather(self, weather):
        self.require_ready()
        self._write({**self.document,'weather':weather})

    def select_survival_regime(self, value):
        self.require_ready()
        self._write({**self.document, 'format': POPULATION_FORMAT, 'release_sources': self.release_sources,
                     'survival_regime': value, 'cubff_density_pressure': self.cubff_density_pressure})

    def select_density_pressure(self, enabled):
        self.require_ready()
        self._write({**self.document, 'format': POPULATION_FORMAT, 'release_sources': self.release_sources,
                     'survival_regime': self.survival_regime, 'cubff_density_pressure': enabled})

    def stage(self, grids, sources=None):
        self.require_ready()
        from mecha_game.execution import validate_source_records
        grids = list(grids)
        sources = [None] * len(grids) if sources is None else sources
        validate_source_records(sources, count=len(grids), grids=grids)
        staged = self.releases
        staged_sources = self.release_sources
        for grid, source in zip(grids, sources):
            if not isinstance(grid,dict) or not isinstance(grid.get('grid_id'),str) or not grid['grid_id']:
                raise ValueError('A contribution needs a grid identity; no staged creatures changed.')
            prior = next((item for item in staged if item['grid_id']==grid['grid_id']),None)
            if prior is not None and prior != grid:
                raise ValueError(f"A different creature named {grid['grid_id']} is already staged.")
            if prior is None:
                staged.append(copy.deepcopy(grid))
                staged_sources.append(copy.deepcopy(source))
        added = len(staged)-len(self.document['releases'])
        self._write({**self.document,'format':POPULATION_FORMAT if self.document['format'] == POPULATION_FORMAT else EXECUTION_FORMAT,'releases':staged,'release_sources':staged_sources})
        return added

    def unstage_all(self):
        self.require_ready()
        self._write({**self.document,'releases':[],'release_sources':[], 'format':POPULATION_FORMAT if self.document['format'] == POPULATION_FORMAT else EXECUTION_FORMAT})

    def begin(self, campaign, era, previous_state):
        self.require_ready()
        pending = dict(state=campaign.state_payload(),era=era,previous_state=previous_state)
        if campaign.last_original_recording is not None:
            pending['recording'] = copy.deepcopy(campaign.last_original_recording)
        pending['sha256'] = _digest(pending)
        format_name = EXECUTION_FORMAT if era.get('execution') is not None else RECORDING_FORMAT if pending.get('recording') is not None else FORMAT
        if (self.document['format'] == POPULATION_FORMAT or campaign.population_policy == 'generation_survivors_v1'
                or era.get('execution', {}).get('manifest', {}).get('format') == 'mechagotchi_era_execution_v2'):
            format_name = POPULATION_FORMAT
        document = {key: value for key, value in self.document.items() if key != 'release_sources'}
        if format_name == POPULATION_FORMAT:
            document.update(survival_regime=self.survival_regime, cubff_density_pressure=self.cubff_density_pressure)
        if format_name in (EXECUTION_FORMAT, POPULATION_FORMAT):
            document['release_sources'] = self.release_sources
        self._write({**document,'format':format_name,'pending':pending})

    def finish(self, ledger_path, state_path):
        from mecha_game.compatibility import keeper_write_lock, require_campaign_compatibility
        with keeper_write_lock(Path(ledger_path).parent):
            if self.pending is not None:
                require_campaign_compatibility(self.pending['state'], state_path=state_path or ledger_path)
            return self._finish_compatible(ledger_path, state_path)

    def _finish_compatible(self, ledger_path, state_path):
        """Commit an already recorded result; never train, evolve or infer history."""
        self.require_ready(allow_pending=True)
        require_no_restore(state_path)
        state_path = Path(state_path) if state_path is not None else None
        pending = self.pending
        if pending is None: raise ValueError('No completed era awaits saving.')
        state,era = pending['state'],pending['era']
        if state_path is not None and state_digest(state_path) != pending['previous_state']:
            try: same = json.loads(state_path.read_text(encoding='utf-8')) == state
            except (OSError,ValueError): same = False
            if not same:
                raise ValueError('Campaign state changed outside this preparation; existing state preserved.')
        predecessor_state = None
        if state_path is not None and state_path.exists():
            # The previous state may be this campaign or its extinct predecessor,
            # never a coincident byte digest used to join unrelated campaigns.
            prior = json.loads(state_path.read_text(encoding='utf-8'))
            KeeperCampaign.validate_state_payload(prior)
            if prior != state:
                same_campaign = prior['campaign_id'] == state['campaign_id']
                if same_campaign:
                    valid = (prior['era_count'] == era['era_index'] and prior['status'] == 'active'
                             and prior.get('population_policy', 'legacy_archive') == state.get('population_policy', 'legacy_archive')
                             and prior.get('body_response', 'legacy') == state.get('body_response', 'legacy'))
                else:
                    valid = (prior['campaign_id'] == state['predecessor_campaign_id'] and
                             prior['status'] == 'extinct' and era['era_index'] == 0
                             and prior.get('body_response', 'legacy') == state.get('body_response', 'legacy'))
                    predecessor_state = prior
                if not valid:
                    raise ValueError('Previous campaign state does not match this completed era; existing files preserved.')
        ledger_path = Path(ledger_path)
        if ledger_path.exists():
            validate_ledger_state(state, ledger_path, pending_era=era, predecessor_state=predecessor_state)
        elif era['era_index'] != 0 or pending['previous_state'] is not None or state['predecessor_campaign_id'] is not None:
            raise ValueError('Campaign ledger is missing earlier history; completed result preserved for recovery.')
        # Restore only the exact recorded state needed by the existing writers.
        # No live simulation model or fabricated current-run history is created.
        saved = KeeperCampaign({'slip_profile':state['base_profile']},
            campaign_id=state['campaign_id'],keeper_label=state['keeper_label'],created_date=state['created_date'],
            predecessor_campaign_id=state['predecessor_campaign_id'],base_seed=state['base_seed'],
            era_config=state['era_config'],inherited_unlocks=state['inherited_unlocks'],
            population_policy=state.get('population_policy', 'legacy_archive'),
            body_response=state.get('body_response', 'legacy'))
        if saved.population_policy == 'generation_survivors_v1':
            saved._population_continuation = copy.deepcopy(state['population_continuation'])
        saved.base_profile = state['base_profile']
        saved.base_covenant_source = copy.deepcopy(state.get('base_covenant_source'))
        saved.base_parameters = state.get('base_parameters',saved.base_parameters)
        saved.campaign.update(status=state['status'],slip_profile=state['slip_profile'],unlocks=state['unlocks'],eras=[era])
        saved.era_offset = era['era_index']
        saved.save(ledger_path)
        if pending.get('recording') is not None:
            from mecha_game.original_recording import save_original_recording
            save_original_recording(pending['recording'], Path(ledger_path).parent, ledger_path)
        if state_path is not None:
            saved.save_state(state_path)
            save_campaign_checkpoint(state_path, ledger_path)
        reset = dict(format=FORMAT, weather=self.weather, pending=None, releases=[])
        if self.document['format'] == POPULATION_FORMAT:
            reset.update(format=POPULATION_FORMAT, release_sources=[], survival_regime=self.survival_regime,
                         cubff_density_pressure=self.cubff_density_pressure)
        self._write(reset)
        return era
