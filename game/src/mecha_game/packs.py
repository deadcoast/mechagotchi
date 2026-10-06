"""Named ``mechagotchi_pack_v1`` composition and independently gated exchange.

Packs carry exact profiles, genomes and declared provenance. Acceptance here only
stages inbox candidates; covenant compatibility and actual founder admission stay
with their existing engine gates. Canonical document digests detect changed JSON,
while the native file picker continues checking the original file's raw bytes.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
import threading

from mecha_engine.genome import validate_grid
from mecha_engine.slip import validate_slip
from mecha_game.covenant_io import read_import_file

PACK_FORMAT = 'mechagotchi_pack_v1'
# One foreground service may handle concurrent requests; identity checks and
# publication must be one operation across differently named source packs.
_IMPORT_LOCK = threading.RLock()
_ITEMS = (('slips', 'profile_id', 'covenants', validate_slip),
          ('creatures', 'grid_id', 'released', validate_grid))


def _json_value(value):
    """Reject lossy Python coercions and non-JSON numbers before copying."""
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise ValueError('JSON object keys must be strings.')
            _json_value(child)
    elif isinstance(value, list):
        for child in value:
            _json_value(child)
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError('JSON numbers must be finite.')
    elif value is not None and not isinstance(value, (str, int, bool)):
        raise ValueError('Pack values must be JSON objects, lists or scalar values.')


def _canonical_bytes(value) -> bytes:
    _json_value(value)
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


def pack_digest(pack) -> str:
    """SHA-256 of complete canonical JSON, not a signature or raw-file hash."""
    return hashlib.sha256(_canonical_bytes(pack)).hexdigest()


def _copy(value):
    return json.loads(_canonical_bytes(value))


def _encoded(value) -> bytes:
    _json_value(value)
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')


def _filename_part(value) -> bool:
    return (isinstance(value, str) and bool(value.strip()) and len(value) <= 128
            and value not in ('.', '..') and value[-1] not in '. '
            and not any(c in '<>:"/\\|?*' or ord(c) < 32 for c in value))


def _validate_header(pack):
    if not isinstance(pack, dict):
        raise ValueError('Expected a JSON object.')
    if pack.get('pack_format') != PACK_FORMAT:
        raise ValueError(f"not a {PACK_FORMAT} file: {pack.get('pack_format')!r}")
    if not _filename_part(pack.get('pack_id')):
        raise ValueError('pack_id must be a nonempty safe filename component.')
    if not isinstance(pack.get('title'), str) or not pack['title'].strip():
        raise ValueError('title must be a nonempty string.')
    if not isinstance(pack.get('provenance'), dict):
        raise ValueError('provenance must be a JSON object.')
    for field, *_ in _ITEMS:
        if not isinstance(pack.get(field), list):
            raise ValueError(f'{field} must be a list.')
    if not pack['slips'] and not pack['creatures']:
        raise ValueError('Select at least one profile or creature.')


def _summary(report):
    entries = report.get('slips', []) + report.get('creatures', [])
    accepted = sum(bool(entry['ok']) for entry in entries)
    refused = len(entries) - accepted
    report.update(accepted_count=accepted, refused_count=refused,
                  all_accepted=bool(report['ok'] and entries and not refused),
                  partial=bool(accepted and refused))
    return report


def _failure(error, *, digest=None):
    result = {'ok': False, 'violations': [str(error)], 'slips': [], 'creatures': []}
    if digest is not None:
        result['pack_digest'] = digest
    return _summary(result)


def _refuse(entry, message, status='refused'):
    entry.update(ok=False, status=status)
    entry['violations'].append(str(message))


def _inbox(keeper: Path, folder: str) -> Path:
    root = keeper.resolve()
    target = root / folder
    if not target.resolve().is_relative_to(root):
        raise ValueError(f'{folder} points outside the selected Keeper; import refused.')
    return target


def _same_existing(target: Path, value: dict) -> bool:
    if target.is_symlink():
        raise ValueError(f'{target.name} is a link; existing file preserved.')
    try:
        existing = json.loads(target.read_bytes().decode('utf-8'))
        same = _canonical_bytes(existing) == _canonical_bytes(value)
    except (ValueError, UnicodeError):
        same = False
    if not same:
        raise ValueError(f'{target.name} already exists with different content; existing file preserved.')
    return True


def _existing_item(folder: Path, target: Path, id_key: str, item: dict) -> Path | None:
    """A different filename must not hide the same identity's conflicting body."""
    found = None
    if target.exists() or target.is_symlink():
        _same_existing(target, item)
        found = target
    for path in sorted(folder.glob('*.json')):
        if path == target or path.name.endswith('.bak.json') or path.is_symlink():
            continue
        try:
            existing = json.loads(path.read_bytes().decode('utf-8'))
        except (ValueError, UnicodeError):
            continue  # An unrelated malformed candidate has no asserted identity.
        if not isinstance(existing, dict) or existing.get(id_key) != item[id_key]:
            continue
        try:
            same = _canonical_bytes(existing) == _canonical_bytes(item)
        except (ValueError, TypeError):
            same = False
        if not same:
            raise ValueError(f"{id_key} {item[id_key]!r} conflicts with {path.name}; existing file preserved.")
        if found is None:
            found = path
    return found


def preview_pack(keeper_dir: str | Path | None, pack: dict) -> dict:
    """Inspect exact values and destination conflicts without creating anything.

    ``None`` previews portable composition without a selected native Keeper.
    ``ok`` means the envelope was processed; consult ``all_accepted`` and the
    per-item results. Neither value claims covenant compatibility or admission.
    """
    digest = None
    try:
        pack = _copy(pack)
        digest = pack_digest(pack)
        _validate_header(pack)
    except (ValueError, TypeError, UnicodeError, RecursionError) as error:
        return _failure(error, digest=digest)
    report = {'ok': True, 'pack_id': pack['pack_id'], 'title': pack['title'],
              'provenance': pack['provenance'], 'pack_digest': digest,
              'violations': [], 'slips': [], 'creatures': []}
    keeper = Path(keeper_dir) if keeper_dir is not None else None
    for field, id_key, folder_name, validator in _ITEMS:
        entries = report[field]
        groups = {}
        for index, item in enumerate(pack[field]):
            identity = item.get(id_key) if isinstance(item, dict) else None
            entry = {'index': index, id_key: identity, 'ok': False,
                     'violations': [], 'status': 'refused', 'item_digest': pack_digest(item)}
            entries.append(entry)
            try:
                if not isinstance(item, dict):
                    raise ValueError('Item must be a JSON object.')
                verdict = validator(item)
                entry['violations'] = list(verdict.errors)
                if not verdict.ok:
                    continue
                if not _filename_part(identity):
                    raise ValueError(f'{id_key} cannot be used as an inbox filename.')
                name = f"pack_{pack['pack_id']}_{identity}.json"
                if len(name.encode('utf-8')) > 255:
                    raise ValueError('Combined pack and item identity is too long for an inbox filename.')
                entry.update(ok=True, status='ready', target=name)
                groups.setdefault(identity, []).append(index)
            except (ValueError, TypeError, KeyError, AttributeError) as error:
                _refuse(entry, error)
        for indexes in groups.values():
            if len({entries[index]['item_digest'] for index in indexes}) > 1:
                for index in indexes:
                    _refuse(entries[index], f'Conflicting valid duplicate {id_key}; no version selected.', 'conflicting')
                continue
            first = indexes[0]
            entry = entries[first]
            if keeper is not None:
                try:
                    folder = _inbox(keeper, folder_name)
                    existing = _existing_item(folder, folder / entry['target'], id_key, pack[field][first])
                    if existing is not None:
                        entry.update(status='already_staged', target=existing.name)
                except OSError as error:
                    _refuse(entry, error, 'io_error')
                except ValueError as error:
                    _refuse(entry, error, 'conflicting')
            for index in indexes[1:]:
                duplicate = entries[index]
                duplicate.update(ok=entry['ok'], status='duplicate' if entry['ok'] else entry['status'],
                                 target=entry['target'], duplicate_of=first,
                                 violations=list(entry['violations']))
    return _summary(report)


def _validated_export(pack: dict) -> dict:
    pack = _copy(pack)
    report = preview_pack(None, pack)
    problems = list(report.get('violations', []))
    for field, *_ in _ITEMS:
        for entry in report[field]:
            problems.extend(entry['violations'])
            if 'duplicate_of' in entry:
                problems.append(f"duplicate {field} selection at index {entry['index']}.")
    if not report['all_accepted'] or problems:
        raise ValueError('; '.join(problems) or 'Pack has no accepted items.')
    return pack


def build_pack(*, pack_id: str, title: str, provenance: dict,
               slips: list[dict], creatures: list[dict]) -> dict:
    """Build an independent, complete named composition or refuse verbatim."""
    return _validated_export({'pack_format': PACK_FORMAT, 'pack_id': pack_id,
                              'title': title, 'provenance': provenance,
                              'slips': slips, 'creatures': creatures})


def export_pack_bytes(pack: dict) -> bytes:
    """Downloadable validated JSON; preserves every selected field."""
    return _encoded(_validated_export(pack))


def write_pack(pack: dict, path: str | Path) -> Path:
    """Legacy low-level fixture/file utility; use export_pack_bytes for creation."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(pack, indent=2) + '\n', encoding='utf-8')
    return path


def load_pack(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding='utf-8'))


def _stage_item(target: Path, value: dict) -> bool:
    """Publish complete bytes exclusively; equal JSON never rewrites owner bytes.

    A hard link publishes the flushed same-directory temporary file atomically
    without replacing an existing target. Unsupported filesystems fail explicitly
    and leave the target untouched; no partial-write fallback is used.
    """
    payload = _encoded(value)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix='.pack-', suffix='.tmp', dir=target.parent,
                                         delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, target)
        except FileExistsError:
            return _same_existing(target, value)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return False


def _import_document(keeper_dir, pack, *, expected_pack_digest=None, retain_receipt=True, before_write=None):
    from mecha_game.compatibility import keeper_write_lock, require_keeper_writable
    with keeper_write_lock(keeper_dir), _IMPORT_LOCK:
        require_keeper_writable(keeper_dir)
        return _import_document_locked(keeper_dir, pack, expected_pack_digest=expected_pack_digest,
                                       retain_receipt=retain_receipt, before_write=before_write)


def _import_document_locked(keeper_dir, pack, *, expected_pack_digest=None, retain_receipt=True, before_write=None):
    try:
        pack = _copy(pack)
        digest = pack_digest(pack)
    except (ValueError, TypeError, UnicodeError, RecursionError) as error:
        return _failure(error)
    if expected_pack_digest is not None and digest != expected_pack_digest:
        return _failure('Pack changed since preview. Preview again before importing.', digest=digest)
    report = preview_pack(keeper_dir, pack)
    if not report['ok'] or not report['accepted_count']:
        return report
    keeper = Path(keeper_dir)
    from mecha_game.compatibility import require_keeper_writable
    if before_write is not None: before_write()
    require_keeper_writable(keeper)
    if retain_receipt:
        try:
            name = f'received_{digest}.json'
            already = _stage_item(_inbox(keeper, 'packs') / name, pack)
            report['receipt'] = {'file': name, 'already_retained': already, 'pack_digest': digest}
        except (OSError, ValueError) as error:
            report['ok'] = False
            report['violations'].append(f'Source pack could not be retained: {error}')
            for field, *_ in _ITEMS:
                for entry in report[field]:
                    if entry['ok']:
                        _refuse(entry, 'Source receipt unavailable; nothing staged.', 'io_error')
            return _summary(report)
    for field, id_key, folder_name, _ in _ITEMS:
        for entry in report[field]:
            if not entry['ok']:
                continue
            if 'duplicate_of' in entry:
                original = report[field][entry['duplicate_of']]
                entry.update(ok=original['ok'], violations=list(original['violations']),
                             status='duplicate' if original['ok'] else original['status'])
                if original['ok']:
                    entry.update(staged=original['staged'], already_staged=True)
                continue
            try:
                folder = _inbox(keeper, folder_name)
                item = pack[field][entry['index']]
                target = folder / entry['target']
                # Recheck after preview/receipt: an existing conflict never becomes an overwrite.
                existing = _existing_item(folder, target, id_key, item)
                if existing is not None:
                    target = existing
                already = _stage_item(target, item)
                entry.update(ok=True, status='already_staged' if already else 'staged',
                             target=target.name, staged=target.name, already_staged=already)
            except OSError as error:
                _refuse(entry, error, 'io_error')
            except (ValueError, TypeError, KeyError, AttributeError) as error:
                _refuse(entry, error, 'conflicting')
    return _summary(report)


def import_pack_document(keeper_dir: str | Path, pack: dict, *, expected_pack_digest: str, before_write=None) -> dict:
    """Import a pinned JSON document and retain its complete source receipt.

    The HTTP adapter owns selected-context identity/revision checks. This service
    only stages in the explicitly supplied Keeper; declared foreign provenance
    has no power to change its companion, campaign or association.
    """
    if not isinstance(expected_pack_digest, str) or not expected_pack_digest:
        return _failure('Preview this pack and supply its expected_pack_digest before importing.')
    return _import_document(keeper_dir, pack, expected_pack_digest=expected_pack_digest, before_write=before_write)


def import_pack(keeper_dir: str | Path, path: str | Path, *, expected_digest: str | None = None) -> dict:
    """Native picker import: expected_digest is the original file's raw SHA-256."""
    try:
        pack, source_digest = read_import_file(path, expected_digest=expected_digest)
    except (OSError, ValueError, UnicodeError) as error:
        return _failure(f'unreadable pack file: {error}')
    # A native picker source already resides in the selected inbox. External
    # files need a retained receipt too; the original raw bytes are never rewritten.
    retained = Path(path).resolve().parent == Path(keeper_dir).resolve() / 'packs'
    report = _import_document(keeper_dir, pack, retain_receipt=not retained)
    report['source_digest'] = source_digest
    return report
