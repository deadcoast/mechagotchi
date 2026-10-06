"""Current native Keeper authority at mutation time; inspection remains read-only.

The short publication lock is shared by native and Workshop writers. It lives
outside the Keeper tree so a refusal creates no save, backup or journal bytes.
It is not held while an era is simulated.
"""
from contextlib import contextmanager
from functools import wraps
import hashlib
import json
import os
from pathlib import Path
import tempfile
import threading

from .body_response import saved_body_response

_locks = {}
_locks_guard = threading.Lock()
_held = threading.local()

@contextmanager
def keeper_write_lock(directory):
    if directory is None:
        yield
        return
    key = os.path.normcase(str(Path(directory).resolve()))
    with _locks_guard:
        lock = _locks.setdefault(key, threading.RLock())
    with lock:
        held = getattr(_held, 'roots', set())
        if key in held:
            yield
            return
        name = 'mechagotchi-write-' + hashlib.sha256(key.encode()).hexdigest() + '.lock'
        with (Path(tempfile.gettempdir()) / name).open('a+b') as stream:
            stream.seek(0, 2)
            if stream.tell() == 0:
                stream.write(b'0'); stream.flush()
            stream.seek(0)
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            _held.roots = held | {key}
            try:
                yield
            finally:
                _held.roots = held
                stream.seek(0)
                if os.name == 'nt': msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
                else: fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

def require_campaign_compatibility(state, *, keeper_session=None, state_path=None):
    """Check target against both cached native and current persisted companion."""
    model = saved_body_response(state)
    if keeper_session is not None and keeper_session.campaign_id is not None and keeper_session.campaign_id not in (
            state['campaign_id'], state.get('predecessor_campaign_id')):
        raise ValueError('Campaign belongs to a different recorded Keeper history; files preserved.')
    sessions = [] if keeper_session is None else [keeper_session]
    if state_path is not None:
        companion = Path(state_path).parent / 'companion.json'
        if companion.exists():
            from .session import CompanionSession
            current = CompanionSession.load(companion)
            if keeper_session is not None and (current.keeper_id != keeper_session.keeper_id or
                    current.body_response != keeper_session.body_response or
                    current.lineage[-1]['life_id'] != keeper_session.lineage[-1]['life_id']):
                raise ValueError('Keeper companion changed outside this session; refresh before writing. Files preserved.')
            sessions.append(current)
    for session in sessions:
        if model != session.body_response:
            raise ValueError('This campaign keeps a different body response from the current companion. '
                             'Recorded history remains available for inspection; files preserved.')
        if session.campaign_id is not None and session.campaign_id not in (
                state['campaign_id'], state.get('predecessor_campaign_id')):
            raise ValueError('Campaign belongs to a different recorded Keeper history; files preserved.')

def require_keeper_writable(directory, *, allow_pending=False):
    """Guard ancillary native/Workshop writes without loading simulation models."""
    root = Path(directory)
    state_path = root / 'campaign_state.json'
    if state_path.exists():
        from .campaign import KeeperCampaign
        state = json.loads(state_path.read_bytes())
        KeeperCampaign.validate_state_payload(state)
        require_campaign_compatibility(state, state_path=state_path)
    for name in ('era_plan.json', 'campaign_preparation.json'):
        path = root / name
        if not path.exists(): continue
        if name == 'era_plan.json':
            from .era_plan import EraPlan
            plan = EraPlan(path)
            if plan.error: raise ValueError(plan.error)
            pending = plan.pending
        else:
            from .preparation_commit import PreparationCommit
            preparation = PreparationCommit(state_path, root / 'campaign.sqlite3')
            if preparation.error: raise ValueError(preparation.error)
            pending = preparation.pending
        if pending is not None:
            require_campaign_compatibility(pending['state'], state_path=state_path)
            if not allow_pending:
                raise ValueError('Captured preparation or completed era awaits explicit native finish; files preserved.')
    if not allow_pending:
        from .campaign_recovery import require_no_restore
        require_no_restore(state_path)

def campaign_writer(method):
    """Guard existing campaign save methods, including direct service callers."""
    @wraps(method)
    def guarded(self, path, *args, **kwargs):
        with keeper_write_lock(Path(path).parent):
            require_campaign_compatibility(self.state_payload(), state_path=path)
            return method(self, path, *args, **kwargs)
    return guarded
