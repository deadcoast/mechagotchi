"""Bounded, unvalidated Workshop draft recovery, separate from engine exports."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import uuid
import authoring

FORMAT='mecha_workshop_draft_v1'
LIMIT=2*1024*1024


class DraftError(ValueError):
    def __init__(self,status,body):
        super().__init__(body['error']); self.status=status; self.body=body


def token(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def validate(snapshot,kind):
    raw=authoring.json_bytes(snapshot)
    if len(raw)>LIMIT: raise ValueError('Draft exceeds the 2 MiB recovery limit; download it before continuing.')
    if not isinstance(snapshot,dict) or snapshot.get('format')!=FORMAT:
        raise ValueError('Unsupported draft snapshot.')
    revision=snapshot.get('draft_revision')
    if type(revision) not in (str,int) or len(str(revision))>120: raise ValueError('Invalid draft revision.')
    history=snapshot.get('history')
    if not isinstance(history,dict) or history.get('version')!=1: raise ValueError('Unsupported draft history.')
    entries=history.get('history'); index=history.get('index')
    if not isinstance(entries,list) or not 1<=len(entries)<=40 or type(index) is not int or not 0<=index<len(entries):
        raise ValueError('Draft history needs 1..40 snapshots and a valid active index.')
    for entry in [*entries,*([history['saved']] if history.get('saved') is not None else [])]:
        if not isinstance(entry,dict) or not isinstance(entry.get('document'),dict): raise ValueError('Incomplete draft history snapshot.')
        doc=entry['document']
        if doc.get('format')!=authoring.FORMAT or not isinstance(doc.get('grid' if kind=='grid' else 'profile'),dict):
            raise ValueError('Draft history does not contain a complete document for this editor.')
    if not isinstance(snapshot.get('editor_state'),dict) or 'document' in snapshot['editor_state']:
        raise ValueError('Invalid draft editor state.')
    if entries[index] != dict(snapshot['editor_state'],document=snapshot.get('document')):
        raise ValueError('Current draft differs from its active history snapshot.')
    return deepcopy(snapshot)


def _load(path,context_id,kind):
    payload=json.loads(path.read_bytes())
    if not isinstance(payload,dict) or payload.get('context_id')!=context_id: raise ValueError('Draft belongs to a different context.')
    return validate(payload.get('snapshot'),kind)


def read(directory,kind,context_id,*,slot='current'):
    if kind not in ('grid','slip') or slot not in ('current','previous'): raise ValueError('Unknown draft kind or slot.')
    path=Path(directory)/f'{kind}.json'; previous=path.with_name(f'{kind}.previous.json')
    current=token(path); selected=path if slot=='current' else previous
    body=dict(ok=True,exists=False,slot=slot,draft_disk_revision=current,context_id=context_id)
    if not selected.exists() and not (slot=='current' and previous.exists()): return body
    try:
        snapshot=_load(selected,context_id,kind)
    except (OSError,ValueError,TypeError,KeyError) as error:
        try: _load(previous,context_id,kind); recoverable=True
        except (OSError,ValueError,TypeError,KeyError): recoverable=False
        raise DraftError(409,dict(ok=False,error='Draft recovery file is unreadable; existing bytes preserved: '+str(error),
            error_code='draft_unreadable',current_revision=current,recovery_available=recoverable)) from error
    return dict(body,exists=True,snapshot=snapshot,selected_draft_revision=token(selected))


def write(directory,kind,context_id,payload,*,before_write=None):
    if kind not in ('grid','slip'): raise ValueError('Unknown draft kind.')
    snapshot=validate(payload.get('snapshot'),kind)
    path=Path(directory)/f'{kind}.json'; previous=path.with_name(f'{kind}.previous.json')
    current=token(path)
    if 'expected_draft_revision' not in payload or payload['expected_draft_revision']!=current:
        raise DraftError(409,dict(ok=False,error='A different draft is on disk; restore or explicitly replace it.',
            error_code='draft_conflict',current_revision=current))
    if not path.exists() and previous.exists() and payload.get('archive_previous') is not True:
        raise DraftError(409,dict(ok=False,error='A previous draft survives without its primary. Inspect and explicitly restore it before starting new.',
            error_code='draft_unreadable',current_revision=None,recovery_available=True))
    raw=authoring.json_bytes(dict(context_id=context_id,snapshot=snapshot)); archive=None
    if path.exists():
        old=path.read_bytes()
        if old==raw: return dict(ok=True,draft_disk_revision=current,snapshot=snapshot,archive=None)
        try: _load(path,context_id,kind); valid=True
        except (ValueError,TypeError,KeyError): valid=False
        if not valid and payload.get('archive_previous') is not True:
            raise DraftError(409,dict(ok=False,error='Unreadable draft must be explicitly preserved before recovery.',error_code='draft_unreadable',current_revision=current,recovery_available=previous.exists()))
        if before_write is not None: before_write()
        if payload.get('archive_previous') is True:
            archive=f'{kind}.preserved-{uuid.uuid4().hex}.json'
            authoring.atomic_bytes(path.parent/archive,old)
        if valid: authoring.atomic_bytes(previous,old)
    elif before_write is not None:
        before_write()
    authoring.atomic_bytes(path,raw)
    return dict(ok=True,draft_disk_revision=token(path),snapshot=snapshot,archive=archive)
