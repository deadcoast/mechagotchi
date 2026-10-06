"""Read-only campaign consistency and explicit, paired checkpoint recovery.

The state and ledger remain separate authorities for preparation and history.
A published checkpoint pairs their verified bytes; it never reconstructs eras.
"""
from __future__ import annotations

from collections import Counter
from contextlib import closing, contextmanager
import copy
import hashlib
import json
import math
from pathlib import Path
import sqlite3
import tempfile

from mecha_engine.storage import SUPPORTED_READ_SCHEMA_VERSIONS, canonical_json, campaign_history, load_era_elites, load_founder_pool, load_era_execution
from mecha_engine.genome import validate_grid
from mecha_game.campaign import ERA_SEED_STRIDE, KeeperCampaign
from mecha_game.session import _document_bytes, _write_bytes_atomic

FORMAT = 'keeper_campaign_recovery_v1'
RESTORE_FORMAT = 'keeper_campaign_restore_v1'
FACT_FIELDS = ('axis', 'tier', 'earned_era_index', 'metric_path', 'metric_value', 'threshold')


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _paths(state_path):
    directory = Path(state_path).parent
    return directory/'campaign_recovery.json', directory/'.campaign-recovery', directory/'campaign_restore.json'


def _campaign_evidence_paths(state_path, ledger_path):
    paths = []
    if ledger_path is not None:
        ledger = Path(ledger_path)
        paths.extend((ledger, *(ledger.with_name(ledger.name+suffix) for suffix in ('-wal', '-journal', '-shm'))))
    if state_path is not None:
        state = Path(state_path)
        paths.extend((state, state.with_suffix('.bak.json'), state.parent/'campaign_preparation.json', *_paths(state)))
    return paths


def has_campaign_evidence(state_path, ledger_path):
    """Any established pair, SQLite sidecar or recovery evidence prevents fallback."""
    return any(path.exists() for path in _campaign_evidence_paths(state_path, ledger_path))


def require_no_restore(state_path):
    if state_path is not None and (Path(state_path).parent/'campaign_preparation.json').exists():
        raise ValueError('Captured campaign preparation awaits explicit finish or inspected checkpoint recovery.')
    if state_path is not None and _paths(state_path)[2].exists():
        raise ValueError('Campaign recovery was interrupted. Explicitly retry the same recovery checkpoint.')


def _open_readonly(ledger_path):
    path = Path(ledger_path)
    if not path.is_file():
        raise ValueError('Campaign ledger is missing. Existing state preserved; use a verified recovery checkpoint.')
    conn = sqlite3.connect(path.resolve().as_uri()+'?mode=ro', uri=True)
    try:
        if conn.execute('PRAGMA user_version').fetchone()[0] not in SUPPORTED_READ_SCHEMA_VERSIONS:
            raise ValueError('Unsupported campaign-ledger schema; existing ledger preserved.')
    except Exception:
        conn.close()
        raise
    return conn


def _facts(rows):
    # Campaign IDs are ledger pointer provenance; old state facts have no such key.
    return sorted(json.dumps({key: fact[key] for key in FACT_FIELDS}, sort_keys=True) for fact in rows)



def validate_era_elites(elites, report):
    """Missing or malformed survivors must never become a fresh founder pool."""
    try:
        expected = report['summary']['archive']['filled_niches']
        if type(expected) is not int or expected < 0 or not isinstance(elites, list) or len(elites) != expected:
            raise ValueError('Recorded era elite count disagrees with its report; survivors cannot be reconstructed.')
        ids = set()
        for elite in elites:
            if (not isinstance(elite, dict) or not isinstance(elite['niche_key'], str) or
                elite['niche_key'] in ids or not isinstance(elite['grid_id'], str) or
                not isinstance(elite['grid'], dict) or elite['grid'].get('grid_id') != elite['grid_id'] or
                type(elite['fitness']) not in (int, float) or not math.isfinite(elite['fitness'])):
                raise ValueError('Invalid recorded elite identity or fitness.')
            verdict = validate_grid(elite['grid'])
            if not verdict.ok:
                raise ValueError('Invalid recorded elite genome: ' + '; '.join(verdict.errors))
            ids.add(elite['niche_key'])
    except (KeyError, TypeError, AttributeError) as error:
        raise ValueError('Incomplete recorded elite genome; existing files preserved.') from error


def load_recorded_founders(conn, campaign_id, era_index):
    """Read existing founder facts; ordering is by ID, never execution order.

    An empty/partial result means evidence is unavailable. It does not mean no
    input was submitted; inspect the verbatim era report for admission/refusal.
    """
    result = []
    for grid_id, source, admitted, errors, grid in conn.execute(
            'SELECT grid_id, source, admitted, rejection_errors_json, grid_json FROM founders '
            'WHERE campaign_id=? AND era_index=? ORDER BY grid_id', (campaign_id, era_index)):
        if admitted not in (0, 1) or source not in ('workshop_release', 'era_elite'):
            raise ValueError('Invalid recorded founder source or verdict.')
        result.append(dict(grid_id=grid_id, source=source, admitted=bool(admitted),
            rejection_errors=json.loads(errors) if errors is not None else None,
            grid=json.loads(grid) if grid is not None else None))
    return result


def validate_founder_records(era):
    """New journal evidence must agree with its verbatim engine outcomes.

    Older journals have no founder_records; missing historical evidence remains
    missing instead of being guessed from a present-day release directory.
    """
    if 'founder_records' not in era:
        return
    rows = era['founder_records']
    submitted = Counter(era['founders_submitted'])
    outcomes = {}
    for grid_id in era['report'].get('founders', {}).get('admitted_ids', []):
        outcomes.setdefault(grid_id, []).append((True, None))
    for row in era['report'].get('founders', {}).get('rejected', []):
        outcomes.setdefault(row['grid_id'], []).append((False, row['errors']))
    expected = {grid_id for grid_id, count in submitted.items()
                if isinstance(grid_id, str) and grid_id and count == 1 and len(outcomes.get(grid_id, [])) == 1}
    bundle = era.get('execution')
    if bundle is not None:
        from mecha_game.execution import population_arguments, blob_json
        if population_arguments(bundle).get('population_policy') == 'generation_survivors_v1':
            occurrences = bundle['manifest']['founder_occurrences']
            projected = [dict(grid_id=row['grid_id'], source='workshop_release', admitted=row['admitted'],
                              rejection_errors=row['rejection_errors'], grid=blob_json(bundle, row['grid_sha256']))
                         for row in occurrences if row['source_kind'] != 'era_breeder' and row['grid_id'] in expected]
            if (not isinstance(rows, list) or canonical_json(sorted(rows, key=lambda row: row['grid_id'])) !=
                    canonical_json(sorted(projected, key=lambda row: row['grid_id']))):
                raise ValueError('Living-population founder projection differs from exact execution occurrences.')
            return
    if not isinstance(rows, list) or len(rows) != len(expected):
        raise ValueError('Completed-era founder evidence is incomplete or ambiguous.')
    seen = set()
    for row in rows:
        grid_id = row['grid_id']
        if (grid_id not in expected or grid_id in seen or
                row['source'] not in ('workshop_release', 'era_elite') or
                type(row['admitted']) is not bool or not isinstance(row['grid'], dict) or
                row['grid'].get('grid_id') != grid_id or
                (row['admitted'], row['rejection_errors']) != outcomes[grid_id][0]):
            raise ValueError('Completed-era founder evidence disagrees with its actual input or verdict.')
        if row['admitted'] and not validate_grid(row['grid']).ok:
            raise ValueError('An admitted founder record has an invalid genome.')
        seen.add(grid_id)



def _validate_population_tail(conn, bundle):
    """Game-side recovery checks the full immutable continuation, not elite IDs."""
    from mecha_game.execution import population_arguments, blob_json, validate_breeder_continuation
    options = population_arguments(bundle)
    if options.get('population_policy') != 'generation_survivors_v1':
        return
    manifest = bundle['manifest']; era_index = manifest['era_index']
    start = options['founder_start_mode']
    if start != ('bootstrap' if era_index == 0 else 'continue'):
        raise ValueError('Population start mode differs from its campaign era position.')
    refs = manifest['inputs']
    if refs['founder_mode'] != 'list':
        raise ValueError('Living continuation must retain an explicit founder list.')
    if era_index:
        prior = conn.execute('SELECT went_extinct FROM eras WHERE campaign_id=? AND era_index=?',
                             (manifest['campaign_id'], era_index-1)).fetchone()
        if prior is None or prior[0]:
            raise ValueError('Missing or ended predecessor cannot supply living continuation.')
        from mecha_engine.storage import load_era_breeders
        previous = load_era_breeders(conn, manifest['campaign_id'], era_index-1)
    else:
        previous = []
    by_ordinal = {row['founder_ordinal']: row for row in manifest['sources'] if 'founder_ordinal' in row}
    founders = [blob_json(bundle, digest) for digest in refs['founder_sha256']]
    sources = [by_ordinal.get(index) for index in range(len(founders))]
    validate_breeder_continuation(founders, sources, previous, manifest['campaign_id'], era_index, start)


def _validate_recorded_campaign(conn, history):
    """Check available predecessor evidence without fabricating missing eras."""
    campaign_id = history['campaign_id']; rows = history['eras']
    count = conn.execute('SELECT count(*) FROM eras WHERE campaign_id=?', (campaign_id,)).fetchone()[0]
    if count != len(rows) or [row['era_index'] for row in rows] != list(range(count)):
        raise ValueError('Campaign history is missing an era or its recorded profile.')
    tables = ['slip_profiles', 'elites', 'founders', 'replays']
    if conn.execute('PRAGMA user_version').fetchone()[0] >= 2:
        tables += ['era_executions', 'founder_occurrences']
    for table in tables:
        orphan = conn.execute(f'SELECT 1 FROM {table} r LEFT JOIN eras e '
            'ON e.campaign_id=r.campaign_id AND e.era_index=r.era_index '
            'WHERE r.campaign_id=? AND e.era_index IS NULL LIMIT 1', (campaign_id,)).fetchone()
        if orphan:
            raise ValueError('Campaign history has evidence whose recorded era is missing.')
    for fact in history['unlocks']:
        if fact['campaign_id'] == campaign_id and (type(fact['earned_era_index']) is not int or
                not 0 <= fact['earned_era_index'] < count):
            raise ValueError('Campaign unlock references missing predecessor history.')
    for row in rows:
        validate_era_elites(load_era_elites(conn, campaign_id, row['era_index']), row['report'])
        bundle = load_era_execution(conn, campaign_id, row['era_index'])
        if bundle is not None:
            _validate_population_tail(conn, bundle)
            from mecha_game.execution import population_arguments, population_ended
            policy = population_arguments(bundle).get('population_policy', 'legacy_archive')
            if policy == 'generation_survivors_v1':
                ended = population_ended(row['report'], load_era_elites(conn, campaign_id, row['era_index']), policy)
                if ended != row['went_extinct']:
                    raise ValueError('Recorded population termination disagrees with the era status.')
        if row['rng_seed'] != rows[0]['rng_seed'] + row['era_index'] * ERA_SEED_STRIDE:
            raise ValueError('Recorded campaign era seeds are inconsistent.')


def _validated_history(conn, state, pending_era=None):
    campaign_id = state['campaign_id']
    try:
        history = campaign_history(conn, campaign_id)
    except KeyError:
        if pending_era is None or pending_era['era_index'] != 0:
            raise ValueError('Saved campaign identity is absent from this ledger.') from None
        predecessor = state['predecessor_campaign_id']
        if predecessor is None:
            if conn.execute('SELECT count(*) FROM campaigns').fetchone()[0]:
                raise ValueError('A different campaign occupies this ledger; existing history preserved.')
            inherited = []
        else:
            try: prior = campaign_history(conn, predecessor)
            except KeyError:
                raise ValueError('The recorded predecessor is missing; existing history preserved.') from None
            if prior['status'] != 'extinct':
                raise ValueError('The recorded predecessor is not extinct; succession is unavailable.')
            inherited = prior['unlocks']
        history = {**{key: state[key] for key in ('campaign_id', 'keeper_label', 'created_date', 'predecessor_campaign_id')},
                   'status': state['status'], 'eras': [], 'unlocks': inherited}
    for key in ('campaign_id', 'keeper_label', 'created_date', 'predecessor_campaign_id'):
        if history[key] != state[key]:
            raise ValueError(f'Campaign state and ledger disagree on {key}; existing files preserved.')
    # Verify the whole predecessor chain without accepting dangling or cyclic links.
    seen = {campaign_id}; predecessor = history['predecessor_campaign_id']
    while predecessor is not None:
        if predecessor in seen:
            raise ValueError('Campaign ledger contains a predecessor cycle.')
        seen.add(predecessor)
        try: prior = campaign_history(conn, predecessor)
        except KeyError: raise ValueError('Campaign predecessor history is missing.') from None
        if prior['status'] != 'extinct':
            raise ValueError('Recorded predecessor is not extinct; succession is unavailable.')
        _validate_recorded_campaign(conn, prior)
        predecessor = prior['predecessor_campaign_id']
    _validate_recorded_campaign(conn, history)
    rows = history['eras']; count = len(rows)
    expected_count = state['era_count']
    allowed = {expected_count} if pending_era is None else {expected_count-1, expected_count}
    if count not in allowed or [row['era_index'] for row in rows] != list(range(count)):
        raise ValueError('Campaign state and ledger era positions disagree; missing history cannot be reconstructed.')
    for row in rows:
        if row['rng_seed'] != state['base_seed'] + row['era_index'] * ERA_SEED_STRIDE:
            raise ValueError('Campaign state and ledger era seeds disagree; existing history preserved.')
    allowed_status = {state['status']}
    if pending_era is not None and count == expected_count-1:
        # record_campaign and record_era use separate transactions. Either old active
        # status or this journal's final status can be visible in that crash window.
        allowed_status.add('active')
    if history['status'] not in allowed_status:
        raise ValueError('Campaign state and ledger status disagree; existing history preserved.')
    own = [fact for fact in history['unlocks'] if fact['campaign_id'] == campaign_id]
    inherited = [fact for fact in history['unlocks'] if fact['campaign_id'] != campaign_id]
    expected_own = [fact for fact in state['unlocks'] if fact['earned_era_index'] < count]
    if _facts(own) != _facts(expected_own) or _facts(inherited) != _facts(state['inherited_unlocks']):
        raise ValueError('Campaign state and ledger unlock facts disagree; existing facts preserved.')
    if pending_era is not None and count == expected_count:
        row = rows[-1]
        same = all(row[key] == pending_era[key] for key in ('report', 'weather', 'rng_seed'))
        same = same and row['slip_profile'] == state['slip_profile']
        same = same and row['went_extinct'] == pending_era['derived']['went_extinct']
        same = same and load_era_elites(conn, campaign_id, pending_era['era_index']) == pending_era['elites']
        if 'founder_records' in pending_era:
            same = same and load_recorded_founders(conn, campaign_id, pending_era['era_index']) == sorted(
                pending_era['founder_records'], key=lambda item: item['grid_id'])
        same = same and canonical_json(load_era_execution(conn, campaign_id, pending_era['era_index'])) == canonical_json(pending_era.get('execution'))
        if not same:
            raise ValueError('A different era occupies this position; existing history preserved.')
    policy = state.get('population_policy', 'legacy_archive')
    from mecha_game.execution import population_arguments, body_arguments
    for row in rows:
        bundle = load_era_execution(conn, campaign_id, row['era_index'])
        recorded_model = body_arguments(bundle).get('body_response', 'legacy') if bundle is not None else 'legacy'
        if recorded_model != state.get('body_response', 'legacy'):
            raise ValueError('Saved campaign cannot migrate its recorded body response.')
        recorded_policy = population_arguments(bundle).get('population_policy', 'legacy_archive') if bundle is not None else 'legacy_archive'
        if recorded_policy != policy:
            raise ValueError('Saved campaign cannot migrate its recorded population policy.')
    if policy == 'generation_survivors_v1':
        from mecha_engine.storage import load_era_breeders
        from mecha_game.execution import breeder_sources, population_ended
        continuation = state['population_continuation']
        latest = pending_era['execution'] if pending_era is not None else load_era_execution(conn, campaign_id, count-1) if count else None
        if latest is not None:
            _validate_population_tail(conn, latest)
            if (population_arguments(latest).get('population_policy') != policy or
                    continuation['era_index'] != latest['manifest']['era_index'] or
                    continuation['ordered_breeders_sha256'] != latest['manifest'].get('ordered_breeders_sha256')):
                raise ValueError('Saved living continuation differs from the exact breeder output.')
            last_report = pending_era['report'] if pending_era is not None else rows[-1]['report']
            ended = population_ended(last_report, [], policy)
            if (ended and state['status'] != 'extinct' or not ended and state['status'] == 'extinct'):
                raise ValueError('Saved population status differs from its actual living result.')
        breeders = load_era_breeders(conn, campaign_id, count-1) if count else []
        if breeders is None:
            raise ValueError('Living continuation evidence is missing; historical elites cannot replace it.')
        history['resume_breeders'] = breeders
        history['resume_founders'] = [copy.deepcopy(row['grid']) for row in breeders]
        history['resume_founder_sources'] = breeder_sources(rows[-1]['report'], campaign_id, count-1) if count else []
        return history
    history['resume_founders'] = load_founder_pool(conn, campaign_id, era_index=count)
    previous_execution = load_era_execution(conn, campaign_id, count-1) if count else None
    if previous_execution is not None and 'ordered_elites_sha256' in previous_execution['manifest']:
        from mecha_game.execution import blob_json
        ordered_elites = blob_json(previous_execution, previous_execution['manifest']['ordered_elites_sha256'])
        history['resume_founders'] = [elite['grid'] for elite in ordered_elites]
    from mecha_game.execution import elite_care_sources
    prior_elites = (ordered_elites if previous_execution is not None and 'ordered_elites_sha256' in previous_execution['manifest']
                    else load_era_elites(conn, campaign_id, count-1)) if count else []
    history['resume_founder_sources'] = elite_care_sources(rows[-1]['report'], prior_elites, campaign_id, count-1) if count else []
    return history


@contextmanager
def validated_campaign_snapshot(state, ledger_path, *, pending_era=None, predecessor_state=None):
    """Yield one verified read-only transaction for coherent context queries.

    JSON bytes/selection identity stay caller-owned. The connection is closed on
    exit and cannot authorize writes, even while another WAL writer commits.
    """
    KeeperCampaign.validate_state_payload(state)
    if predecessor_state is not None:
        KeeperCampaign.validate_state_payload(predecessor_state)
        if predecessor_state['campaign_id'] != state['predecessor_campaign_id']:
            raise ValueError("Previous state is not this campaign's recorded predecessor.")
    try:
        with closing(_open_readonly(ledger_path)) as conn:
            conn.execute('BEGIN')
            if predecessor_state is not None:
                _validated_history(conn, predecessor_state)
            history = _validated_history(conn, state, pending_era)
            yield conn, history
    except (sqlite3.Error, KeyError, TypeError, AttributeError) as error:
        raise ValueError(f'Campaign ledger is unreadable or inconsistent: {error}. Existing files preserved.') from error


def validate_ledger_state(state, ledger_path, *, pending_era=None, predecessor_state=None):
    """Read existing ledger facts; a pending result permits only its exact prefix."""
    with validated_campaign_snapshot(state, ledger_path, pending_era=pending_era,
            predecessor_state=predecessor_state) as (_, history):
        return history


def _manifest(path):
    try:
        raw = path.read_bytes(); value = json.loads(raw)
        if not isinstance(value, dict) or value.get('format') != FORMAT or not isinstance(value.get('current'), dict):
            raise ValueError('Unsupported paired campaign checkpoint.')
        if value.get('previous') is not None and not isinstance(value['previous'], dict):
            raise ValueError('Invalid previous paired campaign checkpoint.')
        return value, raw
    except (ValueError, TypeError, UnicodeError) as error:
        raise ValueError('Campaign recovery manifest is unreadable; existing files preserved.') from error


def _record_bytes(record, directory):
    try:
        state_bytes = record['state_text'].encode('utf-8')
        digest = record['ledger_sha256']
        if (not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest)
                or _sha(state_bytes) != record['state_sha256']):
            raise ValueError('Paired campaign checkpoint identity mismatch.')
        ledger_path = directory/f'{digest}.sqlite3'
        ledger_bytes = ledger_path.read_bytes()
        if _sha(ledger_bytes) != digest:
            raise ValueError('Paired campaign ledger checksum mismatch.')
        state = json.loads(state_bytes)
        validate_ledger_state(state, ledger_path)
        return state, state_bytes, ledger_path, ledger_bytes
    except (KeyError, TypeError, AttributeError, UnicodeError) as error:
        raise ValueError('Incomplete paired campaign checkpoint; existing files preserved.') from error


def inspect_campaign_backup(state_path, ledger_path, *, slot='current'):
    """Inspect exactly one selected slot without automatic fallback or file writes."""
    if slot not in ('current', 'previous'): raise ValueError('Unknown campaign checkpoint selection.')
    manifest_path, directory, _ = _paths(state_path)
    try:
        manifest, raw = _manifest(manifest_path)
        record = manifest.get(slot)
        if record is None: raise ValueError('No previous paired campaign checkpoint is available.')
        state, state_bytes, snapshot, ledger_bytes = _record_bytes(record, directory)
    except OSError as error:
        raise ValueError(f'Paired campaign checkpoint unavailable: {error}. Existing files preserved.') from error
    preparation_path = Path(state_path).parent/'campaign_preparation.json'
    preparation_digest = _sha(preparation_path.read_bytes()) if preparation_path.exists() else None
    restore_path = _paths(state_path)[2]
    if preparation_digest is None and restore_path.exists():
        try:
            restore = json.loads(restore_path.read_bytes())
            preparation_digest = restore.get('preparation_sha256')
            if preparation_digest is not None and (not isinstance(preparation_digest, str) or
                    len(preparation_digest) != 64 or any(c not in '0123456789abcdef' for c in preparation_digest)):
                raise ValueError('Invalid preparation recovery identity.')
        except (ValueError, TypeError, AttributeError) as error:
            raise ValueError('Interrupted campaign recovery marker is unreadable; existing files preserved.') from error
    result = dict(state=state, state_bytes=state_bytes, ledger_path=snapshot, ledger_bytes=ledger_bytes,
                  campaign_id=state['campaign_id'], era_count=state['era_count'],
                  manifest_digest=_sha(raw), slot=slot)
    if preparation_digest is not None: result['preparation_digest'] = preparation_digest
    return result


def save_campaign_checkpoint(state_path, ledger_path):
    from mecha_game.compatibility import keeper_write_lock, require_campaign_compatibility
    with keeper_write_lock(Path(state_path).parent):
        require_campaign_compatibility(json.loads(Path(state_path).read_bytes()), state_path=state_path)
        return _save_compatible_checkpoint(state_path, ledger_path)

def _save_compatible_checkpoint(state_path, ledger_path):
    """Publish a complete, verified pair last; retain current and previous snapshots."""
    require_no_restore(state_path)
    state_path = Path(state_path)
    raw = state_path.read_bytes(); state = json.loads(raw)
    KeeperCampaign.validate_state_payload(state)
    manifest_path, directory, _ = _paths(state_path)
    previous = None
    if manifest_path.exists():
        previous, _ = _manifest(manifest_path)
        # Never replace a broken pointer and thereby conceal the only known backup.
        _record_bytes(previous['current'], directory)
    try:
        with closing(_open_readonly(ledger_path)) as source, closing(sqlite3.connect(':memory:')) as target:
            source.execute('BEGIN')
            _validated_history(source, state)
            source.backup(target)
            ledger_bytes = target.serialize()
    except (sqlite3.Error, KeyError, TypeError) as error:
        raise ValueError(f'Campaign checkpoint could not validate the ledger: {error}.') from error
    if state_path.read_bytes() != raw:
        raise ValueError('Campaign state changed during checkpoint; previous checkpoint preserved.')
    record = dict(state_text=raw.decode('utf-8'), state_sha256=_sha(raw), ledger_sha256=_sha(ledger_bytes))
    if previous is not None and previous['current'] == record:
        return manifest_path
    snapshot = directory/f"{record['ledger_sha256']}.sqlite3"
    if snapshot.exists():
        if snapshot.read_bytes() != ledger_bytes: raise ValueError('Conflicting immutable recovery snapshot preserved.')
    else: _write_bytes_atomic(snapshot, ledger_bytes)
    published = dict(format=FORMAT, current=record, previous=previous['current'] if previous else None)
    _write_bytes_atomic(manifest_path, _document_bytes(published))
    # Only a previously referenced, content-verified file can be retired. Unknown
    # files, archives of replaced primaries and interrupted orphan copies survive.
    retired = previous.get('previous') if previous else None
    retained = {record['ledger_sha256'], previous['current']['ledger_sha256'] if previous else None}
    if isinstance(retired, dict) and retired.get('ledger_sha256') not in retained:
        digest = retired.get('ledger_sha256')
        if isinstance(digest, str) and len(digest) == 64 and all(c in '0123456789abcdef' for c in digest):
            path = directory/f'{digest}.sqlite3'
            if path.is_file() and _sha(path.read_bytes()) == digest:
                try: path.unlink()
                except OSError: pass  # A locked old snapshot never invalidates the published pair.
    return manifest_path


def _require_new_campaign_destination(state_path, ledger_path, *, snapshot=None, snapshot_bytes=None,
                                      manifest_bytes=None):
    """Accept only absence or the exact recovery files this initializer published."""
    manifest, directory, _ = _paths(state_path)
    for path in _campaign_evidence_paths(state_path, ledger_path):
        if not path.exists():
            continue
        if path == directory and snapshot is not None:
            if set(directory.iterdir()) == {snapshot} and snapshot.read_bytes() == snapshot_bytes:
                continue
        if path == manifest and manifest_bytes is not None and path.read_bytes() == manifest_bytes:
            continue
        raise ValueError('Existing campaign evidence appeared; initialization refused and files preserved.')
    plan_path = Path(state_path).parent/'era_plan.json'
    if plan_path.exists():
        from mecha_game.era_plan import EraPlan
        EraPlan(plan_path).require_ready()


def initialize_campaign_checkpoint(campaign, state_path, ledger_path):
    from mecha_game.compatibility import keeper_write_lock, require_campaign_compatibility
    with keeper_write_lock(Path(state_path).parent):
        require_campaign_compatibility(campaign.state_payload(), state_path=state_path)
        return _initialize_compatible(campaign, state_path, ledger_path)

def _initialize_compatible(campaign, state_path, ledger_path):
    """Publish a verified genesis checkpoint before installing either primary.

    This is only for an absent campaign and an explicit new-campaign action.
    Existing evidence always refuses. After manifest publication any interrupted
    materialization is the ordinary pinned C/U recovery operation, never a new
    schema, journal or simulated reconstruction. Per-file replacement is atomic;
    the separate state and ledger are not a multi-file atomic transaction.
    """
    state_path, ledger_path = Path(state_path).resolve(), Path(ledger_path).resolve()
    if state_path.parent != ledger_path.parent or state_path == ledger_path:
        raise ValueError('New campaign primaries must be distinct files in the selected Keeper directory.')
    state = campaign.state_payload()
    KeeperCampaign.validate_state_payload(state)
    if state['era_count'] != 0 or state['predecessor_campaign_id'] is not None or state['status'] != 'active':
        raise ValueError('Only a fresh zero-era campaign can be initialized without prior evidence.')
    _require_new_campaign_destination(state_path, ledger_path)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.campaign-init-', dir=state_path.parent) as staging:
        staging = Path(staging).resolve()
        if staging.parent != state_path.parent:
            raise ValueError('Campaign preparation directory escaped the selected Keeper.')
        prepared_state, prepared_ledger = staging/state_path.name, staging/ledger_path.name
        campaign.save(prepared_ledger)
        campaign.save_state(prepared_state)
        prepared_manifest = save_campaign_checkpoint(prepared_state, prepared_ledger)
        selected = inspect_campaign_backup(prepared_state, prepared_ledger)
        manifest_bytes = prepared_manifest.read_bytes()
        _require_new_campaign_destination(state_path, ledger_path)
        manifest, directory, marker = _paths(state_path)
        snapshot = directory/(selected['ledger_path'].name)
        # Reserve this attempt's directory exclusively. An external directory
        # appearing after the absence check must never become ours to clean.
        directory.mkdir(exist_ok=False)
        directory_identity = directory.stat()
        try:
            _write_bytes_atomic(snapshot, selected['ledger_bytes'])
            _require_new_campaign_destination(state_path, ledger_path,
                snapshot=snapshot, snapshot_bytes=selected['ledger_bytes'])
            _write_bytes_atomic(manifest, manifest_bytes)
            _require_new_campaign_destination(state_path, ledger_path,
                snapshot=snapshot, snapshot_bytes=selected['ledger_bytes'], manifest_bytes=manifest_bytes)
            return recover_campaign_backup(state_path, ledger_path,
                expected_manifest_digest=_sha(manifest_bytes), expected_campaign_id=state['campaign_id'])
        except Exception:
            # An ordinary pre-publication I/O failure must remain retryable.
            # Published recovery authority and any changed/foreign files survive.
            # A hard process interruption can still leave an unpublished copy;
            # never adopt an unreferenced copy automatically on a later call.
            try:
                if (not manifest.exists() and not marker.exists()
                        and directory.resolve() == directory
                        and directory.stat().st_ino == directory_identity.st_ino
                        and directory.stat().st_dev == directory_identity.st_dev):
                    if snapshot.is_file() and snapshot.read_bytes() == selected['ledger_bytes']:
                        snapshot.unlink()
                    if not any(directory.iterdir()):
                        directory.rmdir()
            except OSError:
                pass  # Preserve leftovers if cleanup is locked; retain the original error.
            raise


def _preserve(path, directory):
    if not path.exists(): return None
    raw = path.read_bytes()
    archive = directory/'originals'/f'{path.name}.{_sha(raw)}.preserved'
    if archive.exists():
        if archive.read_bytes() != raw: raise ValueError('Conflicting original recovery archive preserved.')
    else: _write_bytes_atomic(archive, raw)
    return archive


def recover_campaign_backup(state_path, ledger_path, **kwargs):
    from mecha_game.compatibility import keeper_write_lock, require_campaign_compatibility
    with keeper_write_lock(Path(state_path).parent):
        selected = inspect_campaign_backup(state_path, ledger_path, slot=kwargs.get('slot', 'current'))
        require_campaign_compatibility(selected['state'], state_path=state_path)
        return _recover_compatible(state_path, ledger_path, **kwargs)

def _recover_compatible(state_path, ledger_path, *, expected_manifest_digest,
                            expected_campaign_id=None, slot='current', expected_preparation_digest=None):
    """Explicitly restore a previewed pair, preserving both replaced originals.

    Replacement is atomic per file. A durable marker blocks normal load/commit
    until this exact recovery finishes; a failure is explicitly retryable.
    The completed-era journal and all replay artifacts are left intact.
    """
    state_path, ledger_path = Path(state_path), Path(ledger_path)
    selected = inspect_campaign_backup(state_path, ledger_path, slot=slot)
    if selected['manifest_digest'] != expected_manifest_digest:
        raise ValueError('Campaign checkpoint changed since preview; inspect it again before recovery.')
    if expected_campaign_id is not None and selected['campaign_id'] != expected_campaign_id:
        raise ValueError('Campaign checkpoint belongs to a different Keeper campaign; existing files preserved.')
    preparation = None
    if expected_preparation_digest is not None:
        from mecha_game.preparation_commit import PreparationCommit
        preparation = PreparationCommit(state_path, ledger_path)
        preparation._require_recovery_pin(expected_preparation_digest)
    _, directory, marker = _paths(state_path)
    intent = dict(format=RESTORE_FORMAT, manifest_digest=expected_manifest_digest, slot=slot,
                  campaign_id=selected['campaign_id'])
    if preparation is not None: intent['preparation_sha256'] = expected_preparation_digest
    if marker.exists():
        try: old = json.loads(marker.read_bytes())
        except (ValueError, UnicodeError) as error:
            raise ValueError('Interrupted campaign recovery marker is unreadable; existing files preserved.') from error
        if old != intent: raise ValueError('A different interrupted campaign recovery must be resolved first.')
    for suffix in ('-wal', '-journal', '-shm'):
        if ledger_path.with_name(ledger_path.name+suffix).exists():
            raise ValueError('Campaign ledger has an active SQLite journal. Close its writer before recovery.')
    # Archive both originals before replacing either; never rotate the legacy backup.
    preserved = [path for path in (_preserve(state_path, directory), _preserve(ledger_path, directory)) if path is not None]
    if not marker.exists(): _write_bytes_atomic(marker, _document_bytes(intent))
    if not ledger_path.exists() or ledger_path.read_bytes() != selected['ledger_bytes']:
        _write_bytes_atomic(ledger_path, selected['ledger_bytes'])
    if not state_path.exists() or state_path.read_bytes() != selected['state_bytes']:
        _write_bytes_atomic(state_path, selected['state_bytes'])
    validate_ledger_state(selected['state'], ledger_path)
    if state_path.read_bytes() != selected['state_bytes']:
        raise ValueError('Campaign state changed during recovery; explicit retry required.')
    if preparation is not None:
        preparation.resolve_after_recovery(expected_journal_digest=expected_preparation_digest,
            restored_state_digest=_sha(selected['state_bytes']), restored_ledger_digest=_sha(selected['ledger_bytes']))
    marker.unlink()
    return dict(campaign_id=selected['campaign_id'], era_count=selected['era_count'], preserved=preserved)
