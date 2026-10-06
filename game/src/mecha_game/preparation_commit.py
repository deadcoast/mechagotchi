"""Explicit, exactly captured covenant/successor persistence across file failures.

This journal contains completed preparation, never a request to spend again,
create a successor again, simulate an era, or run without a foreground caller.
"""
from __future__ import annotations

import copy
from contextlib import closing
import hashlib
import json
from pathlib import Path
import tempfile

from mecha_game.campaign import KeeperCampaign, SUCCESSOR_SEED_OFFSET
from mecha_game.session import _document_bytes, _write_bytes_atomic

FORMAT = 'keeper_preparation_commit_v1'


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _raw(path):
    return path.read_bytes() if path.exists() else None


def _digest(raw):
    return _sha(raw) if raw is not None else None


def _json(raw):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value: raise ValueError('Duplicate preparation journal key.')
            value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=unique)


def _body_digest(document):
    body = {key: value for key, value in document.items() if key != 'sha256'}
    return _sha(json.dumps(body, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8'))


def _valid_digest(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def _immutable(path, raw):
    if path.exists():
        if path.read_bytes() != raw:
            raise ValueError('Conflicting immutable preparation evidence; existing bytes preserved.')
    else:
        _write_bytes_atomic(path, raw)


def _transition(source, target, kind, source_campaign_id):
    KeeperCampaign.validate_state_payload(target)
    if source is None:
        if (kind != 'covenant' or target['campaign_id'] != source_campaign_id or
            target['era_count'] != 0 or target['status'] != 'active' or
            target['predecessor_campaign_id'] is not None):
            raise ValueError('Absent campaign primaries permit only a fresh Keeper covenant preparation.')
        return
    KeeperCampaign.validate_state_payload(source)
    if source['campaign_id'] != source_campaign_id:
        raise ValueError('Preparation source Keeper identity differs from the saved campaign.')
    if kind == 'covenant':
        # Only the existing covenant/import choices can differ. History, living
        # continuation, earned facts and campaign identity are not preparation.
        baseline = copy.deepcopy(source)
        baseline.setdefault('base_covenant_source', None)
        baseline.setdefault('base_parameters', {key: source['era_config'][key] for key in ('population', 'generations')})
        mutable = {'base_profile', 'base_covenant_source', 'slip_profile', 'era_config'}
        if ({key: value for key, value in baseline.items() if key not in mutable} !=
            {key: value for key, value in target.items() if key not in mutable}):
            raise ValueError('Covenant preparation cannot change campaign identity, history or earned facts.')
    elif kind == 'successor':
        if source['status'] != 'extinct':
            raise ValueError('Only a recorded extinct campaign may prepare its explicit successor.')
        base = source.get('base_parameters', {key: source['era_config'][key] for key in ('population', 'generations')})
        expected = KeeperCampaign({'slip_profile': source['base_profile']},
            campaign_id=source['campaign_id']+'_successor', keeper_label=source['keeper_label'],
            created_date=source['created_date'], predecessor_campaign_id=source['campaign_id'],
            base_seed=source['base_seed']+SUCCESSOR_SEED_OFFSET, era_config={**source['era_config'], **base},
            inherited_unlocks=source['inherited_unlocks']+source['unlocks'],
            population_policy=source.get('population_policy', 'legacy_archive'),
            body_response=source.get('body_response', 'legacy')).state_payload()
        expected['base_covenant_source'] = copy.deepcopy(source.get('base_covenant_source'))
        if target != expected:
            raise ValueError('Captured successor differs from the explicit inherited/base reset contract.')
    else:
        raise ValueError('Unsupported preparation operation.')


def _compatible_checkpoint(source_state, source_ledger, checkpoint_state, checkpoint_ledger):
    """Retained rollback/ancestor pairs are allowed; unrelated history is not."""
    from mecha_game.campaign_recovery import _open_readonly, load_recorded_founders
    from mecha_engine.storage import campaign_history, load_era_elites, load_era_execution
    def chain(conn, identity):
        result = {}
        while identity is not None:
            if identity in result: raise ValueError('Checkpoint predecessor cycle.')
            history = campaign_history(conn, identity)
            result[identity] = history
            identity = history['predecessor_campaign_id']
        return result
    with closing(_open_readonly(source_ledger)) as source, closing(_open_readonly(checkpoint_ledger)) as checkpoint:
        left = chain(source, source_state['campaign_id'])
        right = chain(checkpoint, checkpoint_state['campaign_id'])
        if source_state['campaign_id'] in right:
            distance = list(right).index(source_state['campaign_id'])
            seed_ok = checkpoint_state['base_seed'] == source_state['base_seed'] + distance*SUCCESSOR_SEED_OFFSET
        elif checkpoint_state['campaign_id'] in left:
            distance = list(left).index(checkpoint_state['campaign_id'])
            seed_ok = source_state['base_seed'] == checkpoint_state['base_seed'] + distance*SUCCESSOR_SEED_OFFSET
        else:
            raise ValueError('Paired checkpoint belongs to unrelated Keeper campaign history.')
        if source_state.get('body_response', 'legacy') != checkpoint_state.get('body_response', 'legacy'):
            raise ValueError('Paired checkpoint campaign body response differs.')
        if not seed_ok or source_state.get('population_policy', 'legacy_archive') != checkpoint_state.get('population_policy', 'legacy_archive'):
            raise ValueError('Paired checkpoint campaign lineage seed or population policy differs.')
        for identity in left.keys() & right.keys():
            a, b = left[identity], right[identity]
            fields = ('campaign_id', 'keeper_label', 'created_date', 'predecessor_campaign_id')
            if any(a[field] != b[field] for field in fields):
                raise ValueError('Paired checkpoint predecessor identity differs from saved history.')
            count = min(len(a['eras']), len(b['eras']))
            if a['eras'][:count] != b['eras'][:count]:
                raise ValueError('Paired checkpoint immutable era history differs.')
            def facts(history):
                return sorted(json.dumps(fact, sort_keys=True) for fact in history['unlocks']
                    if fact['campaign_id'] != identity or fact['earned_era_index'] < count)
            if facts(a) != facts(b):
                raise ValueError('Paired checkpoint inherited or earned facts differ.')
            for index in range(count):
                for loader in (load_era_elites, load_recorded_founders, load_era_execution):
                    if loader(source, identity, index) != loader(checkpoint, identity, index):
                        raise ValueError('Paired checkpoint immutable era evidence differs.')


class PreparationCommit:
    """Cached read status; explicit mutations reread every captured authority."""
    def __init__(self, state_path, ledger_path):
        self.state_path, self.ledger_path = Path(state_path).resolve(), Path(ledger_path).resolve()
        if self.state_path.parent != self.ledger_path.parent or self.state_path == self.ledger_path:
            raise ValueError('Preparation primaries must be distinct files in the selected Keeper directory.')
        self.path = self.state_path.parent/'campaign_preparation.json'
        self.directory = self.state_path.parent/'.campaign-preparation'
        self.checkpoint_path = self.state_path.parent/'campaign_recovery.json'
        reserved = {self.path, self.checkpoint_path, self.state_path.parent/'campaign_restore.json',
                    self.state_path.parent/'era_plan.json'}
        if self.state_path in reserved or self.ledger_path in reserved:
            raise ValueError('Preparation primaries cannot replace journal/checkpoint authorities.')
        self.pending = None
        self.error = None
        self.journal_digest = None
        self._document = None
        self._verified_digest = None
        self._verified_state = None
        self._verified_blobs = ()
        self.refresh()

    def _blob_path(self, digest):
        if not _valid_digest(digest): raise ValueError('Invalid captured preparation digest.')
        return self.directory/'blobs'/digest

    def _blob(self, digest):
        if digest is None: return None
        raw = self._blob_path(digest).read_bytes()
        if _sha(raw) != digest: raise ValueError('Captured preparation checksum mismatch.')
        return raw

    def _capture(self, raw):
        if raw is None: return None
        digest = _sha(raw)
        _immutable(self._blob_path(digest), raw)
        return digest

    def _validate(self, document):
        from mecha_game.campaign_recovery import FORMAT as CHECKPOINT_FORMAT, validate_ledger_state
        expected = {'format', 'state_name', 'ledger_name', 'kind', 'summary', 'source_campaign_id',
                    'target_campaign_id', 'source', 'target', 'checkpoint_ledgers', 'sha256'}
        if (not isinstance(document, dict) or set(document) != expected or document['format'] != FORMAT or
            document['state_name'] != self.state_path.name or document['ledger_name'] != self.ledger_path.name or
            document['kind'] not in ('covenant', 'successor') or
            any(not isinstance(document[key], str) or not document[key].strip()
                for key in ('summary', 'source_campaign_id', 'target_campaign_id')) or
            document['sha256'] != _body_digest(document)):
            raise ValueError('Unsupported, incomplete or changed preparation journal.')
        states = {}
        for label in ('source', 'target'):
            record = document[label]
            if not isinstance(record, dict) or set(record) != {'state', 'ledger', 'checkpoint'}:
                raise ValueError('Incomplete captured preparation pair.')
            raw = {key: self._blob(value) for key, value in record.items()}
            if (raw['state'] is None) != (raw['ledger'] is None):
                raise ValueError('Incomplete captured campaign primaries.')
            if label == 'target' and any(value is None for value in raw.values()):
                raise ValueError('Incomplete captured preparation target.')
            states[label] = _json(raw['state']) if raw['state'] is not None else None
            if states[label] is not None:
                validate_ledger_state(states[label], self._blob_path(record['ledger']))
            if raw['checkpoint'] is not None:
                manifest = _json(raw['checkpoint'])
                if (not isinstance(manifest, dict) or set(manifest) != {'format', 'current', 'previous'} or
                    manifest['format'] != CHECKPOINT_FORMAT):
                    raise ValueError('Invalid captured paired checkpoint.')
                for slot in ('current', 'previous'):
                    checkpoint = manifest[slot]
                    if checkpoint is None and slot == 'previous': continue
                    if (not isinstance(checkpoint, dict) or set(checkpoint) != {'state_text', 'state_sha256', 'ledger_sha256'} or
                        not isinstance(checkpoint['state_text'], str)):
                        raise ValueError('Invalid captured checkpoint record.')
                    checkpoint_state = checkpoint['state_text'].encode('utf-8')
                    if _sha(checkpoint_state) != checkpoint['state_sha256']:
                        raise ValueError('Captured checkpoint state checksum mismatch.')
                    self._blob(checkpoint['ledger_sha256'])
                    validate_ledger_state(_json(checkpoint_state), self._blob_path(checkpoint['ledger_sha256']))
                    if label == 'source':
                        if states['source'] is None: raise ValueError('Absent source has a checkpoint authority.')
                        _compatible_checkpoint(states['source'], self._blob_path(document['source']['ledger']),
                            _json(checkpoint_state), self._blob_path(checkpoint['ledger_sha256']))
        _transition(states['source'], states['target'], document['kind'], document['source_campaign_id'])
        if states['target']['campaign_id'] != document['target_campaign_id']:
            raise ValueError('Preparation target Keeper identity mismatch.')
        manifest = _json(self._blob(document['target']['checkpoint']))
        target_record = dict(state_text=self._blob(document['target']['state']).decode('utf-8'),
                             state_sha256=document['target']['state'], ledger_sha256=document['target']['ledger'])
        previous = _json(self._blob(document['source']['checkpoint'])) if document['source']['checkpoint'] else None
        if manifest['current'] != target_record or manifest['previous'] != (previous['current'] if previous else None):
            raise ValueError('Preparation target checkpoint differs from the captured pair.')
        required = {document['target']['ledger']}
        if previous:
            required.update(record['ledger_sha256'] for record in (previous['current'], previous['previous']) if record)
        if (not isinstance(document['checkpoint_ledgers'], list) or
            document['checkpoint_ledgers'] != sorted(required)):
            raise ValueError('Incomplete captured prior checkpoint snapshots.')
        return states['target']

    def refresh(self):
        self.pending = None; self.error = None; self._document = None; self.journal_digest = None
        try:
            raw = _raw(self.path)
            if raw is None: return self
            self.journal_digest = _sha(raw)
            document = _json(raw)
            if self.journal_digest == self._verified_digest:
                # Hash every authority again; identical bytes need no repeated SQLite parse.
                for digest in self._verified_blobs: self._blob(digest)
                state = copy.deepcopy(self._verified_state)
            else:
                state = self._validate(document)
                self._verified_digest = self.journal_digest
                self._verified_state = copy.deepcopy(state)
                self._verified_blobs = tuple(sorted({digest for label in ('source', 'target')
                    for digest in document[label].values() if digest is not None} | set(document['checkpoint_ledgers'])))
            self._document = document
            self.pending = {key: copy.deepcopy(document[key]) for key in
                ('kind', 'summary', 'source_campaign_id', 'target_campaign_id')}
            self.pending['state'] = copy.deepcopy(state)
        except (OSError, ValueError, KeyError, TypeError, AttributeError, UnicodeError) as error:
            self.error = f'Campaign preparation unavailable: {error}. Captured and primary bytes preserved.'
        return self

    def require_ready(self):
        self.refresh()
        if self.error: raise ValueError(self.error)
        if self.pending is not None:
            raise ValueError('Captured preparation awaits explicit finish or inspected checkpoint recovery.')

    def _no_sidecars(self):
        for suffix in ('-wal', '-journal', '-shm'):
            if self.ledger_path.with_name(self.ledger_path.name+suffix).exists():
                raise ValueError('Campaign ledger has an active SQLite sidecar. Close its writer before preparation.')

    def _no_other_work(self):
        if (self.state_path.parent/'campaign_restore.json').exists():
            raise ValueError('Campaign recovery was interrupted; explicitly retry that recovery first.')
        from mecha_game.era_plan import EraPlan
        EraPlan(self.state_path.parent/'era_plan.json').require_ready()
        self._no_sidecars()

    def _current(self):
        self._no_sidecars()
        return dict(state=_digest(_raw(self.state_path)), ledger=_digest(_raw(self.ledger_path)),
                    checkpoint=_digest(_raw(self.checkpoint_path)))

    def begin(self, candidate, **kwargs):
        from mecha_game.compatibility import keeper_write_lock, require_campaign_compatibility
        with keeper_write_lock(self.state_path.parent):
            require_campaign_compatibility(candidate.state_payload(), state_path=self.state_path)
            return self._begin_compatible(candidate, **kwargs)

    def _begin_compatible(self, candidate, *, kind, source_campaign_id, expected_state_digest,
              expected_ledger_digest, summary=None):
        """Capture a complete validated target before changing any primary bytes."""
        from mecha_game.campaign_recovery import _manifest, _record_bytes, _paths, validate_ledger_state, has_campaign_evidence, FORMAT as CHECKPOINT_FORMAT
        self.require_ready(); self._no_other_work()
        current = self._current()
        if current['state'] != expected_state_digest or current['ledger'] != expected_ledger_digest:
            raise ValueError('Campaign primaries changed since preparation; existing files preserved.')
        source_raw = dict(state=_raw(self.state_path), ledger=_raw(self.ledger_path), checkpoint=_raw(self.checkpoint_path))
        if (source_raw['state'] is None) != (source_raw['ledger'] is None):
            raise ValueError('Both campaign primaries must exist, or both must be absent before first preparation.')
        source_state = _json(source_raw['state']) if source_raw['state'] is not None else None
        target_state = copy.deepcopy(candidate.state_payload())
        _transition(source_state, target_state, kind, source_campaign_id)
        if source_state is not None: validate_ledger_state(source_state, self.ledger_path)
        elif has_campaign_evidence(self.state_path, self.ledger_path):
            raise ValueError('Existing campaign recovery evidence prevents fresh preparation.')
        prior = None; checkpoint_blobs = {}
        if source_raw['checkpoint'] is not None:
            prior, raw = _manifest(self.checkpoint_path)
            if raw != source_raw['checkpoint']: raise ValueError('Campaign checkpoint changed during preparation.')
            for record in (prior['current'], prior.get('previous')):
                if record is not None:
                    checkpoint_state, _, checkpoint_ledger, raw = _record_bytes(record, _paths(self.state_path)[1])
                    _compatible_checkpoint(source_state, self.ledger_path, checkpoint_state, checkpoint_ledger)
                    checkpoint_blobs[record['ledger_sha256']] = raw
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with tempfile.TemporaryDirectory(prefix='.preparation-stage-', dir=self.state_path.parent) as temporary:
                staging = Path(temporary)
                staged_state, staged_ledger = staging/self.state_path.name, staging/self.ledger_path.name
                if source_raw['ledger'] is not None: staged_ledger.write_bytes(source_raw['ledger'])
                candidate.save(staged_ledger)
                staged_state.write_bytes(_document_bytes(target_state))
                validate_ledger_state(target_state, staged_ledger)
                target_raw = dict(state=staged_state.read_bytes(), ledger=staged_ledger.read_bytes())
            record = dict(state_text=target_raw['state'].decode('utf-8'), state_sha256=_sha(target_raw['state']),
                          ledger_sha256=_sha(target_raw['ledger']))
            target_raw['checkpoint'] = _document_bytes(dict(format=CHECKPOINT_FORMAT, current=record,
                                                           previous=prior['current'] if prior else None))
            checkpoint_blobs[record['ledger_sha256']] = target_raw['ledger']
            if self._current() != current: raise ValueError('Campaign primaries or checkpoint changed during preparation.')
            from mecha_game.compatibility import require_campaign_compatibility
            require_campaign_compatibility(target_state, state_path=self.state_path)
            document = dict(format=FORMAT, state_name=self.state_path.name, ledger_name=self.ledger_path.name,
                kind=kind, summary=summary or ('Create successor' if kind == 'successor' else 'Change covenant'),
                source_campaign_id=source_campaign_id, target_campaign_id=target_state['campaign_id'],
                source={key: self._capture(raw) for key, raw in source_raw.items()},
                target={key: self._capture(raw) for key, raw in target_raw.items()},
                checkpoint_ledgers=sorted(checkpoint_blobs))
            for raw in checkpoint_blobs.values(): self._capture(raw)
            document['sha256'] = _body_digest(document)
            self._validate(document)
            self.require_ready(); self._no_other_work()
            if self._current() != current: raise ValueError('Campaign primaries or checkpoint changed during capture.')
            _write_bytes_atomic(self.path, _document_bytes(document))
        finally:
            self.refresh()
        if self.error: raise ValueError(self.error)
        return copy.deepcopy(self.pending)

    def _check_finish(self, digest):
        self.refresh()
        if self.journal_digest != digest: raise ValueError('Captured preparation changed since preview; inspect it again.')
        if self.error: raise ValueError(self.error)
        self._no_other_work()
        document = self._document
        from mecha_game.compatibility import require_campaign_compatibility
        require_campaign_compatibility(self.pending['state'], state_path=self.state_path)
        current = self._current()
        for key, value in current.items():
            if value not in (document['source'][key], document['target'][key]):
                raise ValueError('Campaign '+key+' changed outside captured preparation; existing bytes preserved.')
        return document

    def finish(self, **kwargs):
        from mecha_game.compatibility import keeper_write_lock, require_campaign_compatibility
        with keeper_write_lock(self.state_path.parent):
            self.refresh()
            if self.pending is not None:
                require_campaign_compatibility(self.pending['state'], state_path=self.state_path)
            return self._finish_compatible(**kwargs)

    def _finish_compatible(self, *, expected_journal_digest, expected_campaign_id=None):
        """Explicitly install captured bytes; no candidate/operation is rerun."""
        self.refresh()
        if self.journal_digest is None and self.error is None: return None
        document = self._check_finish(expected_journal_digest)
        if expected_campaign_id is not None and expected_campaign_id not in (
                document['source_campaign_id'], document['target_campaign_id']):
            raise ValueError('Captured preparation belongs to a different Keeper campaign identity.')
        target_state = copy.deepcopy(self.pending['state'])
        journal_raw = self.path.read_bytes()
        try:
            # Preserve every previous snapshot; this path never retires checkpoints.
            for digest in document['checkpoint_ledgers']:
                self._check_finish(expected_journal_digest)
                _immutable(self.state_path.parent/'.campaign-recovery'/f'{digest}.sqlite3', self._blob(digest))
            for key, path in (('ledger', self.ledger_path), ('state', self.state_path), ('checkpoint', self.checkpoint_path)):
                self._check_finish(expected_journal_digest)
                raw = self._blob(document['target'][key])
                if _raw(path) != raw: _write_bytes_atomic(path, raw)
            self._check_finish(expected_journal_digest)
            if self._current() != document['target']:
                raise ValueError('Preparation target changed before completion; explicit retry required.')
            _immutable(self.directory/'completed'/f'{expected_journal_digest}.json', journal_raw)
            self._check_finish(expected_journal_digest)
            self.path.unlink()
        finally:
            self.refresh()
        return target_state

    def _require_recovery_pin(self, digest):
        if not _valid_digest(digest): raise ValueError('Inspect captured preparation before checkpoint recovery.')
        raw = _raw(self.path)
        if raw is None:
            raw = _raw(self.directory/'recovered'/f'{digest}.json')
            if raw is None: raise ValueError('Preparation recovery pin has no matching preserved journal.')
        if _sha(raw) != digest:
            raise ValueError('Captured preparation changed since recovery inspection; existing bytes preserved.')
        return raw

    def resolve_after_recovery(self, **kwargs):
        from mecha_game.compatibility import keeper_write_lock, require_campaign_compatibility
        with keeper_write_lock(self.state_path.parent):
            require_campaign_compatibility(_json(self.state_path.read_bytes()), state_path=self.state_path)
            return self._resolve_compatible(**kwargs)

    def _resolve_compatible(self, *, expected_journal_digest, restored_state_digest, restored_ledger_digest):
        """Archive a pinned journal only after explicit exact paired restoration."""
        from mecha_game.campaign_recovery import inspect_campaign_backup, validate_ledger_state
        raw = self._require_recovery_pin(expected_journal_digest)
        self._no_sidecars()
        if (_digest(_raw(self.state_path)) != restored_state_digest or
            _digest(_raw(self.ledger_path)) != restored_ledger_digest):
            raise ValueError('Recovered campaign primaries changed; preparation evidence preserved.')
        matched = False
        for slot in ('current', 'previous'):
            try: selected = inspect_campaign_backup(self.state_path, self.ledger_path, slot=slot)
            except ValueError: continue
            if _sha(selected['state_bytes']) == restored_state_digest and _sha(selected['ledger_bytes']) == restored_ledger_digest:
                matched = True; break
        if not matched: raise ValueError('Preparation can resolve only after an exact verified paired checkpoint recovery.')
        validate_ledger_state(_json(self.state_path.read_bytes()), self.ledger_path)
        _immutable(self.directory/'recovered'/f'{expected_journal_digest}.json', raw)
        self._require_recovery_pin(expected_journal_digest)
        if (_digest(_raw(self.state_path)) != restored_state_digest or
            _digest(_raw(self.ledger_path)) != restored_ledger_digest):
            raise ValueError('Recovered campaign changed before preparation resolution.')
        if self.path.exists(): self.path.unlink()
        self.refresh()
