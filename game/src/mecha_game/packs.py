"""Community profile packs — the FORMAT rung (F16, MVP 0.3).

`mechagotchi_pack_v1`: SLIPs + creatures + provenance in ONE
importable file — the documented community surface at its first
honest rung (distribution infrastructure stays Phase G; this is the
carrier). The gates are the engine's, twice over:

- **the BUILDER refuses invalid content** with the validators'
  verbatim errors — an invalid pack cannot be published;
- **IMPORT judges every item again** (packs travel and can be
  tampered with) and stages ONLY accepted items into the existing
  inboxes — covenants into `keeper/covenants/` (candidates the
  Keeper imports with I), creatures into `keeper/released/` (where
  the era admission gates judge them a third time at run time, DR
  0016/0029) — per-item verdicts, nothing smoothed.
"""

from __future__ import annotations

import json
from pathlib import Path

from mecha_engine.genome import validate_grid
from mecha_engine.slip import validate_slip
from mecha_game.covenant_io import read_import_file

PACK_FORMAT = "mechagotchi_pack_v1"


def build_pack(
    *,
    pack_id: str,
    title: str,
    provenance: dict,
    slips: list[dict],
    creatures: list[dict],
) -> dict:
    """Assemble a pack, refusing invalid content verbatim."""
    for slip in slips:
        verdict = validate_slip(slip)
        if not verdict.ok:
            raise ValueError(
                f"pack slip {slip.get('profile_id')!r} is invalid: "
                + "; ".join(verdict.errors)
            )
    for creature in creatures:
        verdict = validate_grid(creature)
        if not verdict.ok:
            raise ValueError(
                f"pack creature {creature.get('grid_id')!r} is "
                "invalid: " + "; ".join(verdict.errors)
            )
    return {
        "pack_format": PACK_FORMAT,
        "pack_id": pack_id,
        "title": title,
        "provenance": dict(provenance),
        "slips": json.loads(json.dumps(slips)),
        "creatures": json.loads(json.dumps(creatures)),
    }


def write_pack(pack: dict, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(pack, indent=2) + "\n", encoding="utf-8"
    )
    return path


def load_pack(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _filename_part(value) -> bool:
    return (isinstance(value, str) and bool(value.strip()) and value not in ('.', '..')
            and not any(c in '<>:"/\\|?*' or ord(c) < 32 for c in value))


def _stage_item(target: Path, value: dict) -> bool:
    """Create once; equal JSON is a no-op, existing bytes always stay untouched."""
    payload = (json.dumps(value, indent=2) + '\n').encode('utf-8')
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with target.open('xb') as stream:
            try:
                stream.write(payload)
            except OSError:
                stream.close()
                target.unlink()  # Only this call's exclusive, incomplete creation.
                raise
    except FileExistsError:
        existing = target.read_bytes()
        same = existing == payload
        if not same:
            try:
                same = json.dumps(json.loads(existing.decode('utf-8')), sort_keys=True) == json.dumps(value, sort_keys=True)
            except (ValueError, UnicodeError):
                pass
        if not same:
            raise ValueError(f'{target.name} already exists with different content; existing file preserved.')
        return True
    return False


def import_pack(keeper_dir: str | Path, path: str | Path, *, expected_digest: str | None = None) -> dict:
    """Judge/stage items independently and retain explicit retryable verdicts."""
    keeper_dir = Path(keeper_dir)
    try:
        pack, _ = read_import_file(path, expected_digest=expected_digest)
        if pack.get('pack_format') != PACK_FORMAT:
            raise ValueError(f"not a {PACK_FORMAT} file: {pack.get('pack_format')!r}")
        if not _filename_part(pack.get('pack_id')):
            raise ValueError('pack_id must be a nonempty filename component without path separators.')
        for field in ('slips', 'creatures'):
            if not isinstance(pack.get(field, []), list):
                raise ValueError(f'{field} must be a list.')
    except (OSError, ValueError, UnicodeError) as error:
        return {'ok': False, 'violations': [f'unreadable pack file: {error}']}

    report = {'ok': True, 'pack_id': pack['pack_id'], 'title': pack.get('title'),
              'provenance': pack.get('provenance'), 'slips': [], 'creatures': []}
    for field, id_key, folder, validator in (
        ('slips', 'profile_id', 'covenants', validate_slip),
        ('creatures', 'grid_id', 'released', validate_grid),
    ):
        for index, item in enumerate(pack.get(field, [])):
            identity = item.get(id_key) if isinstance(item, dict) else None
            entry = {id_key: identity, 'ok': False, 'violations': []}
            try:
                if not isinstance(item, dict):
                    raise ValueError('Item must be a JSON object.')
                verdict = validator(item)
                entry['violations'] = list(verdict.errors)
                if verdict.ok:
                    name = identity or f'slip_{index}'
                    if not _filename_part(name):
                        raise ValueError(f'{id_key} cannot be used as an inbox filename.')
                    target = keeper_dir / folder / f"pack_{pack['pack_id']}_{name}.json"
                    already = _stage_item(target, item)
                    entry.update(ok=True, staged=target.name, already_staged=already)
            except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
                entry['violations'].append(str(error))
            report[field].append(entry)
    return report
