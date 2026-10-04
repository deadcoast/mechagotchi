"""Bounded, resumable local development evidence (DR 0062); no publication."""
from __future__ import annotations

import hashlib
import json
import os
import signal
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

PHASES = ('review', 'repair', 'enhance', 'polish')
DEPENDENCIES = ('pydantic', 'jsonschema', 'typer', 'rich', 'pygame-ce', 'pyinstaller')
PUBLICATION_GATE = {'status': 'unmet', 'requirement':
                    'Observe successful native Windows and Ubuntu CI on the exact published commit.'}


class WorkflowError(ValueError):
    """A cycle transition or evidence claim cannot be justified."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _path(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or Path(relative).is_absolute():
        raise WorkflowError(f'Path must stay inside the repository: {relative}')
    return path


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(['git', '-c', f'safe.directory={root.resolve().as_posix()}',
                             '-C', str(root), *args], capture_output=True, text=True,
                            encoding='utf-8', errors='replace', check=False)
    if result.returncode:
        raise WorkflowError(result.stderr.strip())
    return result.stdout


def _inventory(root: Path) -> dict[str, str]:
    names = _git(root, 'ls-files', '--cached', '--others', '--exclude-standard', '-z').split('\0')
    result = {}
    for name in sorted(set(filter(None, names))):
        # Exclude our own operational state even before .gitignore is committed.
        if name.startswith(('.development/', '.ci-logs/')):
            continue
        path = _path(root, name)
        result[name] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else 'MISSING'
    return result


def _verified_files(inventory: dict[str, str]) -> dict[str, str]:
    return {name: value for name, value in inventory.items()
            if not (name.endswith('.md') and not name.startswith(('data/', 'docs/development/')))}


def _fingerprint(inventory: dict[str, str]) -> str:
    return hashlib.sha256(json.dumps(_verified_files(inventory), sort_keys=True).encode()).hexdigest()


def _identity(root: Path) -> dict:
    return {'repository': str(root.resolve()), 'head': _git(root, 'rev-parse', 'HEAD').strip(),
            'branch': _git(root, 'branch', '--show-current').strip() or '(detached)',
            'git_status': _git(root, 'status', '--porcelain=v1')}


def _spec(root: Path, name: str) -> dict:
    try:
        config = json.loads(_path(root, 'docs/development/workflow.json').read_text(encoding='utf-8'))
        spec = config['slices'][name]
        assert config['schema_version'] == 1
        assert spec['suites'] and len(set(spec['suites'])) == len(spec['suites'])
        assert all(isinstance(s, str) and s for s in spec['suites'])
        assert _path(root, spec['spec']).is_file()
    except (OSError, ValueError, KeyError, TypeError, AssertionError) as error:
        raise WorkflowError(f'Unknown slice or missing/invalid preregistered specification: {name}') from error
    return spec


def _state_path(root: Path) -> Path:
    return _path(root, '.development/state.json')


def _load(root: Path) -> dict:
    try:
        state = json.loads(_state_path(root).read_text(encoding='utf-8'))
        if state['schema_version'] != 1 or state['repository'] != str(root.resolve()):
            raise WorkflowError('State belongs to a different repository or schema.')
        return state
    except (OSError, json.JSONDecodeError, KeyError) as error:
        raise WorkflowError('No readable local cycle state; start a named slice first.') from error


def _save(root: Path, state: dict) -> None:
    path = _state_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f'state-{uuid.uuid4().hex}.tmp')
    try:
        temporary.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8', newline='\n')
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _current(state: dict, fingerprint: str, mode: str | None = None) -> bool:
    results = state['verifications']
    if not results or not results[-1]['passed']:
        return False
    last_failure = max((i for i, r in enumerate(results) if not r['passed']), default=-1)
    candidates = [r for r in results[last_failure + 1:] if mode is None or r['mode'] == mode]
    return bool(candidates and candidates[-1]['passed'] and
                candidates[-1]['source_fingerprint'] == fingerprint)


def status(root: Path) -> dict:
    identity = _identity(root)
    if not _state_path(root).exists():
        return {**identity, 'started': False, 'publication_gate': dict(PUBLICATION_GATE),
                'next_action': 'Read the queue and specification; --start a named slice.'}
    state = _load(root)
    fingerprint = _fingerprint(_inventory(root))
    focused = _current(state, fingerprint)
    full = _current(state, fingerprint, 'full')
    complete = state['phase'] == 'polish' and full and not state.get('running')
    return {**state, **identity, 'started': True, 'focused_current': focused,
            'full_current': full, 'local_complete': complete,
            'publication_gate': dict(PUBLICATION_GATE),
            'next_action': ('Local slice complete; review/commit locally, then begin the next queued slice. '
                            'Remote publication still requires independent CI evidence.' if complete else
                            'Resume the recorded phase; run focused/full verification after source changes.')}


def _incoming_registration(root: Path, state: dict, name: str, spec: dict) -> list[str] | None:
    """A new contract cannot retroactively invalidate an unchanged full pass.

    This exception admits only registration metadata, never unverified source,
    changed prior contracts, failed gates or inherited success for the new slice.
    """
    if state['phase'] != 'polish' or state.get('running') or name == state['slice']:
        return None
    full = [r for r in state['verifications'] if r['mode'] == 'full']
    if not full or not _current(state, full[-1]['source_fingerprint'], 'full'):
        return None
    if (spec['spec'] == state['spec']['spec'] or
            not spec['spec'].startswith('docs/development/') or not spec['spec'].endswith('.md')):
        return None
    try:
        result = json.loads(_path(root, f".development/runs/{full[-1]['run_id']}/result.json").read_text(encoding='utf-8'))
        baseline = result['inventory']
        if not isinstance(baseline, dict) or not result['passed'] or _fingerprint(baseline) != full[-1]['source_fingerprint']:
            return None
        current = _inventory(root)
        prior_contract = state['spec']['spec']
        config = json.loads(_path(root, 'docs/development/workflow.json').read_text(encoding='utf-8'))
        if (config['slices'].get(state['slice']) != state['spec'] or
                current.get(prior_contract) != baseline.get(prior_contract)):
            return None
        before, after = _verified_files(baseline), _verified_files(current)
        changed = sorted(path for path in set(before) | set(after) if before.get(path) != after.get(path))
        allowed = {'docs/development/workflow.json', spec['spec']}
        return changed if set(changed) <= allowed else None
    except (OSError, ValueError, KeyError, TypeError):
        return None


def begin(root: Path, name: str) -> dict:
    spec = _spec(root, name)
    previous = status(root)
    registration_changes = []
    if previous['started']:
        if not previous['local_complete']:
            registration_changes = _incoming_registration(root, _load(root), name, spec)
            if registration_changes is None:
                raise WorkflowError('An unfinished slice already exists; resume with --status or --checkpoint.')
        history = _path(root, f'.development/history/{previous["cycle_id"]}.json')
        history.parent.mkdir(parents=True, exist_ok=True)
        history.write_text(json.dumps(_load(root), indent=2) + '\n', encoding='utf-8')
    state = {'schema_version': 1, **_identity(root), 'cycle_id': uuid.uuid4().hex,
             'slice': name, 'spec': spec, 'phase': 'review', 'started_at': _now(),
             'initial_inventory': _inventory(root), 'checkpoints': [], 'verifications': [],
             'registration_changes': registration_changes,
             'publication_gate': dict(PUBLICATION_GATE), 'running': None}
    _save(root, state)
    return status(root)


def checkpoint(root: Path, note: str) -> dict:
    if not note.strip():
        raise WorkflowError('A concrete checkpoint note is required.')
    state = _load(root)
    state['checkpoints'].append({'at': _now(), 'phase': state['phase'], 'note': note,
                                **_identity(root), 'source_fingerprint': _fingerprint(_inventory(root))})
    _save(root, state)
    return status(root)


def advance(root: Path, phase: str, note: str) -> dict:
    state = _load(root)
    _spec(root, state['slice'])
    if not note.strip() or phase not in PHASES:
        raise WorkflowError('A valid phase and concrete transition note are required.')
    current = PHASES.index(state['phase'])
    if PHASES.index(phase) != current + 1 and not (phase == 'repair' and current > 1):
        raise WorkflowError('Follow REVIEW -> REPAIR -> ENHANCE -> POLISH; regressions return to REPAIR.')
    if phase in ('enhance', 'polish') and not _current(state, _fingerprint(_inventory(root))):
        raise WorkflowError('Current passing verification is required for this transition.')
    state['phase'] = phase
    _save(root, state)
    return checkpoint(root, note)


def verify(root: Path, mode: str, python: str, *, timeout: float = 2100) -> dict:
    if mode not in ('focused', 'full'):
        raise WorkflowError('Verification must be focused or full.')
    state = _load(root)
    spec = _spec(root, state['slice'])
    before = _inventory(root)
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:8]
    relative = f'.development/runs/{run_id}'
    logs = _path(root, relative)
    logs.mkdir(parents=True)
    command = [python, '-B', str(root / 'tools/ci/run_sweep.py'), '--log-dir', str(logs)]
    if mode == 'focused':
        for suite in spec['suites']:
            command += ['--suite', suite]
    state['running'] = {'run_id': run_id, 'mode': mode, 'started_at': _now(), 'command': command}
    _save(root, state)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8', SDL_VIDEODRIVER='dummy')
    problems = []
    try:
        options = {'start_new_session': True} if os.name != 'nt' else {
            'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW}
        process = subprocess.Popen(command, cwd=root, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True, encoding='utf-8', errors='replace', **options)
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            returncode = process.returncode
        except (subprocess.TimeoutExpired, KeyboardInterrupt):
            # Terminate only the process tree this invocation owns.
            if os.name == 'nt':
                subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                               capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            if process.poll() is None:
                process.kill()
            stdout, stderr = process.communicate()
            returncode = None
            problems.append('Verification timed out or was interrupted; its process tree was terminated.')
    except OSError as error:
        stdout, stderr, returncode = '', str(error), None
        problems.append('Verification process could not start.')
    (logs / 'sweep.stdout.log').write_text(stdout, encoding='utf-8', newline='\n')
    (logs / 'sweep.stderr.log').write_text(stderr, encoding='utf-8', newline='\n')
    after = _inventory(root)
    changed = sorted(name for name in set(before) | set(after) if before.get(name) != after.get(name))
    if changed:
        problems.append('Verification changed source/evidence; inspect changed_files. Nothing was restored.')
    if returncode != 0:
        problems.append(f'Verification exited with {returncode}.')
    try:
        summary = json.loads((logs / 'summary.json').read_text(encoding='utf-8'))
        suites = summary['suites']
        if not (summary['complete'] and not summary.get('failures') and
                not summary.get('quick') and summary['artifacts']['ok'] and suites and
                all(s['status'] == 'passed' and s['tests_run'] > 0 for s in suites)):
            problems.append('Sweep is incomplete, empty or failed.')
        if mode == 'focused' and set(s['name'] for s in suites) != set(spec['suites']):
            problems.append('Focused suite results do not match the preregistered scope.')
        if mode == 'full':
            expected = {f'lab:{p.name}' for p in (root / 'labs').iterdir()
                        if p.is_dir() and any(p.glob('test_*.py'))}
            expected.update(('package', 'cli', 'game', 'workshop', 'ci'))
            if summary.get('selected_suites') or set(s['name'] for s in suites) != expected:
                problems.append('A filtered or incomplete suite plan cannot count as full verification.')
        if any(not summary['environment']['dependencies'].get(name) for name in DEPENDENCIES):
            problems.append('Required lab/cli/game dependencies are missing.')
    except (OSError, ValueError, KeyError, TypeError) as error:
        summary = None
        problems.append(f'No valid sweep summary: {error}')
    diff = subprocess.run(['git', '-c', f'safe.directory={root.resolve().as_posix()}', '-C', str(root),
                           'diff', '--check'], capture_output=True, text=True, encoding='utf-8', errors='replace')
    staged_diff = subprocess.run(['git', '-c', f'safe.directory={root.resolve().as_posix()}', '-C', str(root),
                                  'diff', '--cached', '--check'], capture_output=True, text=True,
                                 encoding='utf-8', errors='replace')
    (logs / 'diff-check.log').write_text(diff.stdout + diff.stderr + staged_diff.stdout + staged_diff.stderr, encoding='utf-8')
    if diff.returncode or staged_diff.returncode:
        problems.append('Git diff --check failed; see diff-check.log.')
    result = {'run_id': run_id, 'at': _now(), 'mode': mode, 'passed': not problems,
              'returncode': returncode, 'problems': problems, 'changed_files': changed,
              'source_fingerprint': _fingerprint(before), 'inventory': before,
              'head': _git(root, 'rev-parse', 'HEAD').strip(), 'command': command,
              'summary_log': f'{relative}/summary.json', 'stdout_log': f'{relative}/sweep.stdout.log',
              'stderr_log': f'{relative}/sweep.stderr.log',
              'tests_run': sum(s.get('tests_run', 0) for s in summary['suites']) if summary else 0}
    (logs / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    state['running'] = None
    state['verifications'].append({k: v for k, v in result.items() if k != 'inventory'})
    if problems:
        state['phase'] = 'repair'
    _save(root, state)
    return result
