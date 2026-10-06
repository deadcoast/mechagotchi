"""Lossless Workshop document projection and local revision-safe persistence.

X2 preregistration: cycle-38-keeper-and-authoring.md. This adapter never
reconstructs a supplied genome. Engine validators remain the authority;
canvas matrices are a projection, while legacy matrix construction stays at
its existing call site. Carrier snapshots must agree with the codec overlay.
"""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import uuid

FORMAT = 'mecha_workshop_document_v1'
STRATA = ('body', 'organs', 'decoration', 'effects')
ROLE_TOKENS = {'body': 'B', 'anchor': 'A', 'shell': 'S', 'joint': 'J',
               'limb': 'L', 'eye': 'E', 'mouth': 'M', 'antenna': 'N',
               'sensor': 'P', 'decoration': 'D', 'effect': 'F', 'empty': '.'}
TOKENS = frozenset(ROLE_TOKENS.values())


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
        ensure_ascii=False, allow_nan=False).encode('utf-8')).hexdigest()


def project_grid(grid: dict) -> list[list[str]]:
    size = grid.get('grid_size')
    if (not isinstance(size, list) or len(size) != 2 or
        any(type(n) is not int or not 1 <= n <= 64 for n in size)):
        raise ValueError('grid_size must contain two dimensions within 1..64 for projection')
    width, height = size
    matrix = [['.'] * width for _ in range(height)]
    cells = grid.get('cells', [])
    if not isinstance(cells, list):
        raise ValueError('cells must be an array')
    for cell in cells:
        if not isinstance(cell, dict):
            raise ValueError('cell entry must be an object')
        x, y = cell.get('x'), cell.get('y')
        if type(x) is not int or type(y) is not int or not 0 <= x < width or not 0 <= y < height:
            continue  # authoritative validator reports malformed coordinates
        matrix[y][x] = ('A' if cell.get('animation_anchor') is True
                         else ROLE_TOKENS.get(cell.get('role'), 'B'))
    return matrix


def merge_layers(layers: object) -> list[list[str]]:
    if (not isinstance(layers, list) or len(layers) != len(STRATA) or
        any(not isinstance(layer, dict) for layer in layers) or
        [layer.get('name') for layer in layers] != list(STRATA)):
        raise ValueError('layers must be exactly the four semantic strata in order: ' + ', '.join(STRATA))
    matrices = [layer.get('matrix') for layer in layers]
    first = matrices[0]
    if not isinstance(first, list) or not first or not isinstance(first[0], list) or not first[0]:
        raise ValueError('layer matrices must be non-empty grids')
    height, width = len(first), len(first[0])
    for matrix in matrices:
        if (not isinstance(matrix, list) or len(matrix) != height or
            any(not isinstance(row, list) or len(row) != width for row in matrix)):
            raise ValueError('layer matrices must share one canvas size')
        if any(not isinstance(token, str) or token not in TOKENS for row in matrix for token in row):
            raise ValueError('layers contain unknown tokens')
    merged = [['.'] * width for _ in range(height)]
    for matrix in matrices:
        for y, row in enumerate(matrix):
            for x, token in enumerate(row):
                if token != '.':
                    merged[y][x] = token
    return merged


def document(value: object, *, require_grid: bool = False, require_profile: bool = False) -> dict:
    if not isinstance(value, dict) or value.get('format') != FORMAT:
        raise ValueError('document must use format ' + FORMAT)
    unknown = set(value) - {'format', 'grid', 'profile', 'layers'}
    if unknown:
        raise ValueError('unsupported document fields must be preserved outside this format: ' + ', '.join(sorted(unknown)))
    if require_grid and not isinstance(value.get('grid'), dict):
        raise ValueError('document.grid must be an object')
    if require_profile and not isinstance(value.get('profile'), dict):
        raise ValueError('document.profile must be an object')
    for key in ('grid', 'profile'):
        if key in value and not isinstance(value[key], dict):
            raise ValueError('document.' + key + ' must be an object')
    if not any(key in value for key in ('grid', 'profile')):
        raise ValueError('document needs a grid or profile')
    if 'layers' in value:
        if not isinstance(value.get('grid'), dict):
            raise ValueError('layers require a semantic grid')
        if merge_layers(value['layers']) != project_grid(value['grid']):
            raise ValueError('layers do not merge to the semantic grid - the sidecar may not lie about the grid')
    digest(value)  # reject NaN/infinite/non-JSON values before any mutation
    return deepcopy(value)


def _bytes_revision(values: list[bytes | None]) -> str | None:
    """The existing revision encoding, applied to one captured set of bytes."""
    if all(data is None for data in values):
        return None
    state = hashlib.sha256()
    for data in values:
        if data is not None:
            state.update(b'present\0' + str(len(data)).encode() + b'\0' + data)
        else:
            state.update(b'absent\0')
    return state.hexdigest()


def disk_revision(target: Path, sidecar: Path | None = None) -> str | None:
    paths = [target] + ([sidecar] if sidecar else [])
    return _bytes_revision([path.read_bytes() if path.exists() else None for path in paths])


def atomic_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix='.' + path.name + '.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'wb') as output:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def preserved_write(changes: list[tuple[Path, bytes | None]], *, before_write=None) -> dict[str, str]:
    """Keep unique originals, replace each file atomically, roll back I/O errors.

    The handler owns the in-process lock. This is not a cross-process file
    transaction; an interrupted multi-file change remains detectable on load.
    Backups survive both successful replacements and a failed attempt.
    """
    originals = {path: path.read_bytes() if path.exists() else None for path, _ in changes}
    if before_write is not None:
        before_write()  # Revalidate after all inspection, before even a backup.
    backups = {}
    for path, original in originals.items():
        if original is not None:
            backup = path.with_name(path.stem + '.' + uuid.uuid4().hex + '.bak.json')
            atomic_bytes(backup, original)
            backups[path.name] = backup.name
    completed = []
    try:
        for path, data in changes:
            if data is None:
                path.unlink(missing_ok=True)
            else:
                atomic_bytes(path, data)
            completed.append(path)
    except OSError:
        for path in reversed(completed):
            original = originals[path]
            if original is None:
                path.unlink(missing_ok=True)
            else:
                atomic_bytes(path, original)
        raise
    return backups


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')


def grid_files(folder: Path):
    for path in sorted(folder.glob('*.json')):
        if path.name.endswith(('.bak.json', '.layers.json', '.authoring.json')):
            continue
        try:
            grid = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            continue
        if isinstance(grid, dict) and isinstance(grid.get('grid_id'), str) and isinstance(grid.get('cells'), list) and isinstance(grid.get('grid_size'), list):
            yield path, grid


def load_document(target: Path) -> tuple[dict, str | None]:
    sidecar = target.with_name(target.stem + '.layers.json')
    grid_bytes = target.read_bytes()
    sidecar_bytes = sidecar.read_bytes() if sidecar.exists() else None
    grid = json.loads(grid_bytes.decode('utf-8'))
    result = {'format': FORMAT, 'grid': grid}
    if sidecar_bytes is not None:
        extra = json.loads(sidecar_bytes.decode('utf-8'))
        if not isinstance(extra, dict) or not any(key in extra for key in ('document', 'layers')):
            raise ValueError('unrecognized authoring sidecar; preserve it and restore the intended draft')
        if 'document' in extra:
            result = document(extra['document'], require_grid=True)
            if result['grid'] != grid or ('layers' in extra and extra['layers'] != result.get('layers')):
                raise ValueError('authoring sidecar differs from saved grid or layers; preserve both files and restore the intended draft')
        elif 'layers' in extra:
            result['layers'] = extra['layers']
    result = document(result, require_grid=True)
    if (target.read_bytes() != grid_bytes or
            (sidecar.read_bytes() if sidecar.exists() else None) != sidecar_bytes):
        raise ValueError('saved creature changed during inspection; refresh before selecting its revision')
    return result, _bytes_revision([grid_bytes, sidecar_bytes])


def carrier_document(sidecar: dict) -> dict | None:
    markers = ('authoring_document', 'authoring_document_digest')
    if not any(key in sidecar for key in markers):
        return None  # only a genuinely absent modern arm is a legacy carrier
    snapshot = sidecar.get('authoring_document')
    if (not all(key in sidecar for key in markers) or not isinstance(snapshot, dict)
            or not isinstance(sidecar['authoring_document_digest'], str)):
        raise ValueError('incomplete authoring document binding; refusing legacy fallback')
    result = document(snapshot, require_grid=True, require_profile=True)
    if digest(result) != sidecar.get('authoring_document_digest'):
        raise ValueError('authoring snapshot digest mismatch')
    grid = result['grid']
    contract = sidecar.get('grid_contract', {})
    overlay = sidecar.get('semantic_overlay', {})
    for key in ('grid_id', 'schema_version', 'grid_size'):
        if grid.get(key) != contract.get(key):
            raise ValueError('authoring snapshot conflicts with carrier grid_contract.' + key)
    for key in ('cells', 'organs', 'palette', 'mutation', 'lineage', 'metadata'):
        if grid.get(key, [] if key == 'cells' else {}) != overlay.get(key):
            raise ValueError('authoring snapshot conflicts with carrier semantic_overlay.' + key)
    if result['profile'] != sidecar.get('slip_binding', {}).get('profile_snapshot'):
        raise ValueError('authoring snapshot conflicts with carrier profile')
    return result
