"""Read-only native entry inspection and explicitly chosen companion operations.

A saved companion is self-contained. Inspection never discovers runtime assets,
trains a model, creates a home, exports lineage or writes a checkpoint. The window
owns navigation/confirmation and checkpoints a chosen new life before care.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path
import stat

from mecha_game.session import CompanionSession

COMPANION_FILENAME = 'companion.json'
_READABLE = ('missing', 'valid', 'invalid')


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class SaveInspection:
    status: str
    reason: str | None = None
    name: str | None = None
    keeper_id: str | None = None
    life_id: str | None = None
    learning_policy: str | None = None
    body_response: str | None = None
    alive: bool | None = None
    session_tick: int | None = None
    life_count: int | None = None
    digest: str | None = None
    _raw: bytes | None = field(default=None, repr=False, compare=False)


@dataclass(frozen=True)
class HomeInspection:
    home: Path
    revision: str
    home_status: str
    reason: str | None
    primary: SaveInspection
    backup: SaveInspection
    actions: tuple[str, ...]
    notices: tuple[str, ...] = ()

    @property
    def can_restore(self) -> bool:
        return (self.home_status == 'directory' and self.backup.status == 'valid'
                and self.primary.status in _READABLE)


def _read_save(path: Path) -> SaveInspection:
    try:
        # lstat distinguishes an absent file from a broken link, which is existing
        # evidence and cannot be silently treated as an empty save slot.
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode):
            info = path.stat()
        if stat.S_ISDIR(info.st_mode):
            return SaveInspection('directory', f'{path.name} is a directory; choose another save home or repair this path.')
        if not stat.S_ISREG(info.st_mode):
            return SaveInspection('unreadable', f'{path.name} is not a regular save file.')
        raw = path.read_bytes()
    except FileNotFoundError as error:
        # An existing dangling link is not an absent save.
        if path.is_symlink():
            return SaveInspection('unreadable', str(error))
        return SaveInspection('missing')
    except OSError as error:
        return SaveInspection('unreadable', str(error))
    token = _digest(raw)
    try:
        session = CompanionSession._from_payload(json.loads(raw.decode('utf-8')))
    except (ValueError, TypeError, KeyError, AttributeError, OverflowError) as error:
        return SaveInspection('invalid', str(error), digest=token, _raw=raw)
    return SaveInspection('valid', name=session.name, keeper_id=session.keeper_id,
        life_id=session.lineage[-1]['life_id'], learning_policy=session.learning_policy, body_response=session.body_response,
        alive=session.alive, session_tick=session.session_tick, life_count=len(session.lineage),
        digest=token, _raw=raw)


def inspect_home(home: str | Path) -> HomeInspection:
    """Describe the selected home and exact companion snapshots without writes.

    A read does not establish writability. Actual write failures are handled by
    the explicitly requested operation; inspection never uses a probe file.
    """
    requested = Path(home)
    resolved = requested.absolute()
    reason = None
    try:
        resolved = requested.expanduser().resolve()
        info = resolved.stat()
        home_status = 'directory' if stat.S_ISDIR(info.st_mode) else 'file'
        if home_status == 'file':
            reason = 'The selected save home is a file, not a directory. Choose another directory.'
    except FileNotFoundError:
        home_status = 'missing'
    except (OSError, ValueError, RuntimeError) as error:
        home_status, reason = 'unreadable', str(error)
    if home_status in ('directory', 'missing'):
        primary = _read_save(resolved / COMPANION_FILENAME)
        backup = _read_save((resolved / COMPANION_FILENAME).with_suffix('.bak.json'))
    else:
        primary = backup = SaveInspection('unreadable', reason)
    facts = [os.path.normcase(str(resolved)), home_status, reason,
             [primary.status, primary.digest, primary.reason],
             [backup.status, backup.digest, backup.reason]]
    revision = _digest(json.dumps(facts, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
    actions = []
    if home_status in ('directory', 'missing'):
        if primary.status == 'valid':
            actions.append('resume')
        if backup.status == 'valid':
            actions.append('inspect_backup')
        if primary.status in _READABLE and backup.status in _READABLE:
            actions.append('new')
    actions.extend(('choose_directory', 'retry', 'quit'))
    notices = []
    if primary.status == 'missing' and backup.status != 'missing':
        notices.append('Primary companion is missing. Backup inspection never restores it automatically.')
    if primary.status == 'invalid':
        notices.append('Primary companion cannot be resumed. Its exact bytes remain untouched.')
    if backup.status == 'invalid':
        notices.append('Backup is invalid and cannot be restored. Its exact bytes remain untouched.')
    return HomeInspection(resolved, revision, home_status, reason, primary, backup,
                          tuple(actions), tuple(notices))


def _require_current(inspection: HomeInspection) -> HomeInspection:
    current = inspect_home(inspection.home)
    if current.revision != inspection.revision:
        raise ValueError('Selected companion files changed since inspection. Retry and inspect them again before choosing.')
    return current


def resume_session(inspection: HomeInspection, *, learning_policy: str | None = None,
                   care_selection_policy: str | None = None, care_evaluator: str | None = None, body_response: str | None = None) -> CompanionSession:
    """Resume the inspected primary without touching assets or any save file."""
    current = _require_current(inspection)
    if current.primary.status != 'valid':
        raise ValueError(current.primary.reason or 'No valid primary companion is available to resume.')
    session = CompanionSession._from_payload(json.loads(current.primary._raw.decode('utf-8')),
                                          learning_policy=learning_policy,
                                          care_selection_policy=care_selection_policy, care_evaluator=care_evaluator, body_response=body_response)
    session._save_authorities[str((current.home / COMPANION_FILENAME).resolve())] = current.primary._raw
    return session


def restore_session(inspection: HomeInspection, *, learning_policy: str | None = None,
                    care_selection_policy: str | None = None, care_evaluator: str | None = None, body_response: str | None = None):
    """Explicit confirmation restores only the inspected backup and primary pair."""
    current = _require_current(inspection)
    if not current.can_restore:
        raise ValueError(current.backup.reason or current.primary.reason or
                         'No valid backup can be safely restored in this selected home.')
    return CompanionSession.recover_backup(current.home / COMPANION_FILENAME,
        learning_policy=learning_policy, care_selection_policy=care_selection_policy,
        care_evaluator=care_evaluator, body_response=body_response, expected_primary_digest=current.primary.digest,
        expected_backup_digest=current.backup.digest)


def resolve_new_learning_policy(inspection: HomeInspection, *, requested_policy: str | None,
                                built_in_inputs: bool) -> str | None:
    """Resolve only native New: qualified fresh default or prior-life continuity.

    None deliberately asks explicit_new_session to retain valid primary/backup
    policy. Low-level constructor/helper callers keep their historical default.
    Custom input choices do not borrow the standard product cohort's claim.
    """
    if requested_policy is not None:
        if not isinstance(requested_policy, str) or requested_policy not in ('incumbent', 'qtable'):
            raise ValueError('learning policy must be incumbent or qtable')
        return requested_policy
    if inspection.primary.status == 'valid' or inspection.backup.status == 'valid':
        return None
    return 'qtable' if built_in_inputs else 'incumbent'


def explicit_new_session(companion_path, grid, slip_profile, model, learning_policy, *,
                         inspection: HomeInspection | None = None,
                         care_selection_policy: str | None = None,
                         care_evaluator: str | None = None, body_response: str | None = None) -> CompanionSession:
    """Prepare an explicitly selected new life, preserving exact prior snapshots.

    This retains the former app helper's contract: original files are archived,
    and the caller checkpoints the returned session. With an inspection, only its
    selected home and unchanged snapshots authorize preservation. New inputs must
    already have been explicitly selected/resolved by the caller.
    """
    companion_path = Path(companion_path)
    snapshots = []
    if inspection is not None:
        if (companion_path.parent.expanduser().resolve() != inspection.home or
                companion_path.name != COMPANION_FILENAME):
            raise ValueError('New companion path differs from the inspected save home.')
        current = _require_current(inspection)
        companion_path = current.home / COMPANION_FILENAME
        if 'new' not in current.actions:
            raise ValueError(current.reason or current.primary.reason or current.backup.reason or
                             'Existing companion files cannot be preserved safely.')
        for path, saved in ((companion_path, current.primary),
                            (companion_path.with_suffix('.bak.json'), current.backup)):
            if saved._raw is not None:
                prior = (CompanionSession._from_payload(json.loads(saved._raw.decode('utf-8')))
                         if saved.status == 'valid' else None)
                snapshots.append((path, saved._raw, prior))
    else:
        # Keep the explicit CLI helper's unguarded behavior for existing callers.
        for path in (companion_path, companion_path.with_suffix('.bak.json')):
            if path.exists():
                if not path.is_file():
                    raise ValueError(f'{path.name} is not a file')
                raw = path.read_bytes()
                try:
                    prior = CompanionSession._from_payload(json.loads(raw.decode('utf-8')))
                except (ValueError, UnicodeError):
                    prior = None
                snapshots.append((path, raw, prior))
    previous = next(((path, prior) for path, _, prior in snapshots if prior is not None), None)
    # Validate the requested life before archiving, so invalid New inputs cannot
    # produce preservation files or consume the player's current companion.
    if previous is not None:
        path, prior = previous
        session = prior.adopt(grid, slip_profile, model=model, origin='new_companion',
                              learning_policy=learning_policy, source={'history_snapshot': path.name},
                              care_selection_policy=care_selection_policy, care_evaluator=care_evaluator, body_response=body_response)
        if path != companion_path:
            reason = ('Previous primary was missing or invalid. Available backup history is retained; '
                      'events after that snapshot are unavailable. Exact prior files were preserved.')
            session.chronicle['prior_history'] = 'unavailable'
            session.chronicle['prior_history_reason'] = reason
            session.lineage[-1]['prior_history_unavailable'] = reason
    else:
        session = CompanionSession(grid, slip_profile, model=model,
                                   learning_policy=learning_policy or 'incumbent',
                                   care_selection_policy=care_selection_policy or 'off',
                                   care_evaluator=care_evaluator or 'archive_morphology_probe_v1',
                                   body_response='legacy' if body_response is None else body_response)
        session.model.validate_for(session.grid['grid_size'])
        if snapshots:
            session.mark_history_unavailable(
                'Previous companion files were invalid; their exact bytes were preserved before explicit new companion.')
    if inspection is not None:
        _require_current(inspection)
    for path, raw, _ in snapshots:
        archive = path.with_name(path.stem + '.replaced-' + _digest(raw) + '.json')
        try:
            with archive.open('xb') as output:
                output.write(raw)
        except FileExistsError:
            if archive.read_bytes() != raw:
                raise ValueError('Preservation archive conflicts; existing companion unchanged.')
    session._save_authorities[str(companion_path.resolve())] = next(
        (raw for path, raw, _ in snapshots if path == companion_path), None)
    return session
