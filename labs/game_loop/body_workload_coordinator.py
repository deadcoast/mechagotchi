"""Bound one foreground body-workload worker; never retry a stage.

The frozen orchestrator binds stage names/commands and prerequisites. This guard
enforces the shared 1,200s ledger, kind caps, single worker and immutable receipts.
Publication is charged a conservative 250ms allowance; exceeding it retains the
lock and refuses further work. A started debit reserves the whole stage bound
until terminal publication, so an interrupted coordinator cannot resume silently.
"""
from __future__ import annotations

import time
_MODULE_STARTED = time.perf_counter()
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
FORMAT = 'body_workload_measurement_v1'
BUDGET_FORMAT = 'body_workload_measurement_budget_v1'
CONTINUATION_BUDGET_FORMAT = 'body_workload_measurement_budget_v2'
KIND_LIMITS = {'setup':60, 'causal':30, 'care':30, 'era':120, 'reproduction':120, 'native':60, 'analysis':60, 'conditional-era':120}
SLOT_LIMITS = {'setup':1, 'causal':1, 'care':30, 'era':6, 'reproduction':2, 'native':3, 'analysis':1, 'conditional-era':1}
CONTINUATION_KIND_LIMITS = {'recovery':60, 'era':120, 'reproduction':120,
    'native':60, 'analysis':60, 'conditional-era':120}
CONTINUATION_SLOT_LIMITS = {'recovery':1, 'era':4, 'reproduction':2,
    'native':1, 'analysis':1, 'conditional-era':1}
_PRIOR_DEBIT_FIELDS = {'budget_path', 'budget_sha256', 'terminal_path',
    'terminal_sha256', 'elapsed_seconds'}
PUBLICATION_ALLOWANCE = 0.25
CLEANUP_ALLOWANCE = 10.0


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, indent=2, allow_nan=False) + '\n').encode('utf-8')


def utc():
    return datetime.now(timezone.utc).isoformat()


def _digest(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def initial_budget(source_manifest_sha256, *, prior_debit=None, root=ROOT):
    """Fresh v1, or explicitly bound v2 recovery; never rewrites prior evidence."""
    if not _digest(source_manifest_sha256):
        raise ValueError('source manifest sha256 is required')
    value = dict(format=BUDGET_FORMAT, total_limit_seconds=1200,
        kind_limits_seconds=dict(KIND_LIMITS), source_manifest_sha256=source_manifest_sha256,
        stages=[], elapsed_seconds=0.0, remaining_seconds=1200.0)
    if prior_debit is not None:
        if not isinstance(prior_debit, dict):
            raise ValueError('prior debit must be a typed reference mapping')
        value.update(format=CONTINUATION_BUDGET_FORMAT,
            kind_limits_seconds=dict(CONTINUATION_KIND_LIMITS), prior_debit=dict(prior_debit))
        _prior_debit(value, Path(root).resolve())
        _retotal(value)
    return value


def _limits(budget):
    if budget.get('format') == BUDGET_FORMAT:
        return KIND_LIMITS, SLOT_LIMITS
    if budget.get('format') == CONTINUATION_BUDGET_FORMAT:
        return CONTINUATION_KIND_LIMITS, CONTINUATION_SLOT_LIMITS
    raise ValueError('unknown measurement budget version')


def _prior_debit(budget, root=ROOT, deadline=None):
    """Recheck immutable v1 debit and its settled terminal, including old error.

    This is accounting evidence, not approval of that failed measurement. An
    independent recovery attestation and fixed continuation launcher still gate
    outcomes. Failed v2 recovery cannot be chained into another continuation.
    """
    if budget.get('format') == BUDGET_FORMAT:
        return None
    if budget.get('format') != CONTINUATION_BUDGET_FORMAT:
        raise ValueError('unknown measurement budget version')
    reference = budget.get('prior_debit')
    if not isinstance(reference, dict) or set(reference) != _PRIOR_DEBIT_FIELDS:
        raise ValueError('invalid prior debit reference fields')
    amount = reference['elapsed_seconds']
    if (type(amount) not in (int, float) or not 0 <= amount <= 1200 or
            not math.isfinite(amount) or not all(_digest(reference[key])
                for key in ('budget_sha256', 'terminal_sha256'))):
        raise ValueError('invalid prior debit amount or hashes')
    root = Path(root).resolve()
    paths = {}
    for key in ('budget_path', 'terminal_path'):
        relative = reference[key]
        if (not isinstance(relative, str) or not relative or '\\' in relative or
                Path(relative).is_absolute() or ':' in relative or
                any(part in ('', '.', '..') for part in relative.split('/'))):
            raise ValueError('prior debit requires normalized relative JSON paths')
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            raise ValueError('prior debit path leaves the evidence root')
        paths[key] = path
    for path_key, hash_key in (('budget_path', 'budget_sha256'), ('terminal_path', 'terminal_sha256')):
        if _hash_file(paths[path_key], deadline) != reference[hash_key]:
            raise ValueError('prior debit evidence drift: ' + path_key)
    prior = json.loads(paths['budget_path'].read_bytes())
    if prior.get('format') != BUDGET_FORMAT:
        raise ValueError('prior debit must reference the retained v1 budget')
    check_budget(prior, root=root)
    rows = prior['stages']
    if (prior['elapsed_seconds'] != amount or not rows or
            any(row['status'] != 'completed' for row in rows[:-1])):
        raise ValueError('prior debit differs from retained elapsed or completed prefix')
    last = rows[-1]
    terminal = json.loads(paths['terminal_path'].read_bytes())
    if (last['status'] not in ('completed', 'error', 'refused', 'timeout') or
            _resolve(last.get('receipt', ''), root) != paths['terminal_path'] or
            last.get('terminal_sha256') != reference['terminal_sha256'] or
            terminal.get('format') != FORMAT or terminal.get('status') != last['status'] or
            terminal.get('elapsed_seconds') != last['elapsed_seconds'] or
            terminal.get('source_manifest_sha256') != prior['source_manifest_sha256'] or
            terminal.get('cleanup_confirmed') is not True or
            terminal.get('request', {}).get('name') != last['name'] or
            terminal.get('request', {}).get('kind') != last['kind']):
        raise ValueError('prior debit terminal binding or cleanup is invalid')
    return prior


def exclusive_json(path, value):
    with Path(path).open('xb') as stream:
        stream.write(encode(value))
        stream.flush()
        os.fsync(stream.fileno())


def _publish_budget(path, budget):
    temporary = path.with_suffix('.publishing')
    exclusive_json(temporary, budget)
    os.replace(temporary, path)


def _retotal(budget):
    prior = budget['prior_debit']['elapsed_seconds'] if budget.get('format') == CONTINUATION_BUDGET_FORMAT else 0
    budget['elapsed_seconds'] = prior + sum(row['elapsed_seconds'] for row in budget['stages'])
    budget['remaining_seconds'] = 1200-budget['elapsed_seconds']


def check_budget(budget, *, root=ROOT):
    limits, slots = _limits(budget)
    prior = _prior_debit(budget, root)
    if (budget.get('total_limit_seconds') != 1200
            or budget.get('kind_limits_seconds') != limits
            or not _digest(budget.get('source_manifest_sha256'))):
        raise ValueError('registered budget bounds or source binding changed')
    stages = budget.get('stages')
    if not isinstance(stages, list):
        raise ValueError('invalid budget stages')
    names = []
    for row in stages:
        if not isinstance(row, dict) or not isinstance(row.get('name'), str):
            raise ValueError('invalid budget stage')
        if (row.get('kind') not in limits or row.get('status') not in
                ('running', 'completed', 'refused', 'error', 'timeout', 'interrupted')):
            raise ValueError('invalid budget kind or status')
        amount = row.get('elapsed_seconds')
        if type(amount) not in (float, int) or not math.isfinite(amount) or amount < 0:
            raise ValueError('invalid budget debit')
        names.append(row['name'])
    if len(names) != len(set(names)):
        raise ValueError('duplicate budget stage')
    if prior is not None:
        if stages and stages[0]['kind'] != 'recovery':
            raise ValueError('continuation must begin with explicit recovery')
        if any(sum(row['kind'] == kind for row in stages) > maximum for kind, maximum in slots.items()):
            raise ValueError('continuation stage slots exceeded')
        if set(names) & {row['name'] for row in prior['stages']}:
            raise ValueError('prior stage names cannot be repeated')
    total = (prior['elapsed_seconds'] if prior is not None else 0) + sum(row['elapsed_seconds'] for row in stages)
    for field, expected in (('elapsed_seconds', total), ('remaining_seconds', 1200-total)):
        actual = budget.get(field)
        if (type(actual) not in (int, float) or not math.isfinite(actual)
                or not math.isclose(actual, expected, rel_tol=0, abs_tol=1e-7)):
            raise ValueError('budget accounting differs from retained debits')
    return budget


def _path(path, root):
    return path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)


def _resolve(path, root):
    return (root / path).resolve()


def _hash_file(path, deadline=None):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        while chunk := stream.read(1024 * 1024):
            if deadline is not None and time.perf_counter() >= deadline:
                raise TimeoutError('validation exceeded remaining stage time')
            digest.update(chunk)
    return digest.hexdigest()


def _sources(path, root, expected, deadline):
    raw = path.read_bytes()
    if sha(raw) != expected:
        raise ValueError('source manifest drift from frozen study identity')
    manifest = json.loads(raw)
    if (set(manifest) != {'format', 'files'} or manifest['format'] != 'x8_source_manifest_v1'
            or not isinstance(manifest['files'], dict) or not manifest['files']):
        raise ValueError('invalid source manifest')
    files = manifest['files']
    if root == ROOT and Path(__file__).resolve().relative_to(root).as_posix() not in files:
        raise ValueError('source manifest must bind this coordinator')
    for relative, digest in files.items():
        if not isinstance(relative, str) or Path(relative).is_absolute() or not _digest(digest):
            raise ValueError('invalid frozen source identity')
        target = (root / relative).resolve()
        if not target.is_relative_to(root) or _hash_file(target, deadline) != digest:
            raise ValueError('source identity drift: ' + relative)


def _inputs(path, digest, deadline):
    if path is not None and _hash_file(path, deadline) != digest:
        raise ValueError('input byte digest mismatch or drift')


def output_snapshot(output, control, deadline=None):
    result = {}
    if output.exists():
        if output.is_symlink() or not output.is_dir():
            raise ValueError('worker output must be a real directory')
        for path in sorted(output.rglob('*')):
            if path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction()):
                raise ValueError('output links are not immutable evidence')
            if path.is_file():
                result['worker/' + path.relative_to(output).as_posix()] = _hash_file(path, deadline)
    for name in ('stdout.log', 'stderr.log'):
        path = control / name
        if path.exists():
            result['parent/' + name] = _hash_file(path, deadline)
    return result


def _prior_receipts(budget, root, deadline):
    limits, _ = _limits(budget)
    for entry in budget['stages']:
        if entry['status'] == 'running':
            continue  # only the just-persisted current stage can be running
        path = _resolve(entry['receipt'], root)
        raw = path.read_bytes()
        if sha(raw) != entry.get('terminal_sha256'):
            raise ValueError('prior terminal receipt integrity differs')
        receipt = json.loads(raw)
        if (receipt.get('format') != FORMAT or receipt['status'] != 'completed'
                or receipt['elapsed_seconds'] != entry['elapsed_seconds']):
            raise ValueError('prior completed debit differs')
        control = path.parent
        started_raw = (control / 'started.json').read_bytes()
        if sha(started_raw) != receipt['started_sha256']:
            raise ValueError('prior started receipt integrity differs')
        started = json.loads(started_raw)
        request = receipt['request']
        if (started.get('format') != FORMAT or started['request'] != request
                or entry['name'] != request['name'] or entry['kind'] != request['kind']
                or control.name != entry['name']
                or started['source_manifest_sha256'] != receipt['source_manifest_sha256']
                or receipt['source_manifest_sha256'] != budget['source_manifest_sha256']
                or started['inputs_sha256'] != receipt['inputs_sha256']
                or request['inputs_sha256'] != receipt['inputs_sha256']
                or started['limit_seconds'] != receipt['limit_seconds']
                or receipt['limit_seconds'] != entry['reserved_upper_bound_seconds']
                or receipt['limit_seconds'] > limits[entry['kind']]
                or not receipt['cleanup_confirmed']):
            raise ValueError('prior budget, terminal and started identities differ')
        if budget['format'] == CONTINUATION_BUDGET_FORMAT and (
                receipt.get('prior_debit') != budget['prior_debit'] or
                started.get('prior_debit') != budget['prior_debit']):
            raise ValueError('continuation prior debit receipt identities differ')
        if output_snapshot(_resolve(request['output'], root), control, deadline) != receipt['outputs']:
            raise ValueError('prior output integrity differs')
        if request['inputs'] is not None:
            _inputs(_resolve(request['inputs'], root), receipt['inputs_sha256'], deadline)


class WorkerTerminationError(RuntimeError):
    pass


class _WindowsTree:
    """Assign a suspended worker to a kill-on-close job before it can spawn."""
    def __init__(self):
        import ctypes as c
        from ctypes import wintypes as w
        self.c = c
        self.k = c.WinDLL('kernel32', use_last_error=True)
        class Basic(c.Structure):
            _fields_ = [('per_process', c.c_int64), ('per_job', c.c_int64),
                ('flags', w.DWORD), ('minimum', c.c_size_t), ('maximum', c.c_size_t),
                ('active_limit', w.DWORD), ('affinity', c.c_size_t),
                ('priority', w.DWORD), ('scheduling', w.DWORD)]
        class IO(c.Structure):
            _fields_ = [(name, c.c_uint64) for name in ('read_ops', 'write_ops', 'other_ops',
                'read_bytes', 'write_bytes', 'other_bytes')]
        class Extended(c.Structure):
            _fields_ = [('basic', Basic), ('io', IO), ('process_memory', c.c_size_t),
                ('job_memory', c.c_size_t), ('peak_process', c.c_size_t), ('peak_job', c.c_size_t)]
        class Accounting(c.Structure):
            _fields_ = [(name, c.c_int64) for name in ('user', 'kernel', 'period_user', 'period_kernel')] + [
                (name, w.DWORD) for name in ('faults', 'total', 'active', 'terminated')]
        self.accounting = Accounting
        self.k.CreateJobObjectW.argtypes = [c.c_void_p, w.LPCWSTR]
        self.k.CreateJobObjectW.restype = w.HANDLE
        for name, args in (
            ('SetInformationJobObject', [w.HANDLE, c.c_int, c.c_void_p, w.DWORD]),
            ('AssignProcessToJobObject', [w.HANDLE, w.HANDLE]),
            ('QueryInformationJobObject', [w.HANDLE, c.c_int, c.c_void_p, w.DWORD, c.c_void_p]),
            ('TerminateJobObject', [w.HANDLE, w.UINT]), ('CloseHandle', [w.HANDLE])):
            getattr(self.k, name).argtypes = args
            getattr(self.k, name).restype = w.BOOL
        self.handle = self.k.CreateJobObjectW(None, None)
        if not self.handle:
            raise c.WinError(c.get_last_error())
        info = Extended()
        info.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.k.SetInformationJobObject(self.handle, 9, c.byref(info), c.sizeof(info)):
            self.close()
            raise c.WinError(c.get_last_error())

    def attach(self, process):
        if not self.k.AssignProcessToJobObject(self.handle, int(process._handle)):
            raise self.c.WinError(self.c.get_last_error())
        nt = self.c.WinDLL('ntdll')
        nt.NtResumeProcess.argtypes = [self.c.c_void_p]
        nt.NtResumeProcess.restype = self.c.c_long
        if nt.NtResumeProcess(int(process._handle)) != 0:
            raise OSError('could not resume owned suspended worker')

    def active(self):
        info = self.accounting()
        if not self.k.QueryInformationJobObject(self.handle, 1, self.c.byref(info), self.c.sizeof(info), None):
            raise self.c.WinError(self.c.get_last_error())
        return info.active

    def terminate(self):
        if not self.k.TerminateJobObject(self.handle, 1):
            raise self.c.WinError(self.c.get_last_error())

    def reap(self):
        pass  # Job accounting includes descendant exit; root is reaped by Popen.

    def close(self):
        if self.handle:
            self.k.CloseHandle(self.handle)
            self.handle = None


class _PosixTree:
    def __init__(self):
        self.pid = None
        self.subreaper = None
        if sys.platform.startswith('linux'):
            # Adopt orphaned descendants so the foreground parent can reap them.
            # Without this, a killed grandchild can remain a zombie under PID 1.
            import ctypes
            libc = ctypes.CDLL(None, use_errno=True)
            previous = ctypes.c_int()
            if libc.prctl(37, ctypes.byref(previous), 0, 0, 0) != 0:
                raise OSError(ctypes.get_errno(), 'cannot inspect child subreaper')
            if libc.prctl(36, 1, 0, 0, 0) != 0:
                raise OSError(ctypes.get_errno(), 'cannot own descendant cleanup')
            self.subreaper = libc, previous.value

    def active(self):
        try:
            os.killpg(self.pid, 0)
            return 1
        except ProcessLookupError:
            return 0

    def terminate(self):
        try:
            os.killpg(self.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

    def close(self):
        if self.subreaper is not None:
            libc, previous = self.subreaper
            if libc.prctl(36, previous, 0, 0, 0) != 0:
                raise WorkerTerminationError('could not restore foreground subreaper state')
            self.subreaper = None

    def reap(self):
        # Call only after Popen.wait has reaped the root. Negative PID restricts
        # this to the owned group, leaving unrelated subprocesses untouched.
        while True:
            try:
                pid, _ = os.waitpid(-self.pid, os.WNOHANG)
            except ChildProcessError:
                return
            if pid == 0:
                return


def _launch(command, root, stdout, stderr):
    if os.name != 'nt':
        tree = _PosixTree()
        try:
            process = subprocess.Popen(command, cwd=root, stdout=stdout, stderr=stderr, start_new_session=True)
            tree.pid = process.pid
            return process, tree
        except BaseException:
            tree.close()
            raise
    tree = _WindowsTree()
    process = None
    try:
        process = subprocess.Popen(command, cwd=root, stdout=stdout, stderr=stderr,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | 0x4)  # CREATE_SUSPENDED
        tree.attach(process)
        return process, tree
    except BaseException:
        try:
            if process is not None:
                tree.terminate()
                process.kill()
                process.wait(timeout=5)
        except BaseException as exc:
            raise WorkerTerminationError('launch cleanup unconfirmed') from exc
        finally:
            tree.close()
        raise


def _cleanup(process, tree, deadline, force=False):
    """Reap the root and confirm zero owned descendants; never silently orphan."""
    try:
        leftovers = bool(tree.active())
        if force or leftovers:
            tree.terminate()
        process.wait(timeout=max(0.001, deadline-time.perf_counter()))
        while True:
            tree.reap()
            if not tree.active():
                break
            if time.perf_counter() >= deadline:
                raise TimeoutError('owned process tree did not empty')
            time.sleep(0.01)
        tree.close()
        return leftovers
    except BaseException as exc:
        tree.close()  # Windows kill-on-close remains a final fail-safe.
        raise WorkerTerminationError('process tree cleanup unconfirmed; retain lock') from exc


def run_one(*, name, kind, command, source_manifest, output_dir, inputs=None,
            inputs_sha256=None, budget_path=ROOT / '.development/body-workload/budget.json',
            receipt_root=ROOT / '.development/body-workload/coordinator/receipts', root=ROOT, started=None):
    started = time.perf_counter() if started is None else started
    if not isinstance(name, str) or not re.fullmatch('[A-Za-z0-9][A-Za-z0-9_.-]{0,95}', name):
        raise ValueError('stage name must be a safe unique directory name')
    if kind not in (KIND_LIMITS.keys() | CONTINUATION_KIND_LIMITS.keys()) or not command or any(not isinstance(arg, str) for arg in command):
        raise ValueError('invalid stage kind or full worker command')
    if (inputs is None) != (inputs_sha256 is None) or (inputs is not None and not _digest(inputs_sha256)):
        raise ValueError('input path requires its exact sha256 digest')
    root = Path(root).resolve()
    source_manifest, output, budget_path, receipt_root = [Path(path).resolve()
        for path in (source_manifest, output_dir, budget_path, receipt_root)]
    inputs = Path(inputs).resolve() if inputs is not None else None
    control = receipt_root / name
    if (output.is_relative_to(receipt_root) or receipt_root.is_relative_to(output)
            or budget_path.is_relative_to(output) or source_manifest.is_relative_to(output)
            or (inputs is not None and inputs.is_relative_to(output))):
        raise ValueError('worker output must be separate from control and frozen inputs')
    request = dict(name=name, kind=kind, command=list(command),
        source_manifest=_path(source_manifest, root), inputs=_path(inputs, root) if inputs else None,
        inputs_sha256=inputs_sha256, output=_path(output, root))
    lock = budget_path.with_suffix('.lock')
    try:
        exclusive_json(lock, dict(format=FORMAT, pid=os.getpid(), request=request,
            started_utc=utc(), started_monotonic=started))
    except FileExistsError as exc:
        raise ValueError('active or interrupted coordinator; retain lock, no automatic resume') from exc
    stage_started = settled = False
    try:
        budget = check_budget(json.loads(budget_path.read_bytes()), root=root)
        limits, slots = _limits(budget)
        prior = _prior_debit(budget, root)
        if kind not in limits:
            raise ValueError('stage kind is not authorized for this budget version')
        if prior is not None:
            if not budget['stages'] and kind != 'recovery':
                raise ValueError('explicit recovery must precede continuation')
            if name in {row['name'] for row in prior['stages']}:
                raise ValueError('prior stage cannot be repeated under a continuation ledger')
        prior_binding = {'prior_debit': dict(budget['prior_debit'])} if prior is not None else {}
        if any(row.get('status') != 'completed' for row in budget['stages']):
            raise ValueError('failed or incomplete prior stage stops the study')
        if any(row['name'] == name for row in budget['stages']):
            raise ValueError('existing stage cannot be repeated or reused')
        if control.exists():
            raise ValueError('partial or existing receipt directory; no automatic resume')
        if kind in slots and sum(row.get('kind') == kind for row in budget['stages']) >= slots[kind]:
            raise ValueError('registered ' + kind + ' slots exhausted')
        limit = min(limits[kind], budget['remaining_seconds'])
        if limit <= time.perf_counter()-started+CLEANUP_ALLOWANCE+PUBLICATION_ALLOWANCE:
            raise ValueError('insufficient remaining cumulative or stage budget')
        deadline = started+limit-PUBLICATION_ALLOWANCE
        control.mkdir(parents=True, exist_ok=False)
        stage_started = True
        start = dict(format=FORMAT, request=request, started_utc=utc(),
            started_monotonic=started, limit_seconds=limit,
            source_manifest_sha256=budget['source_manifest_sha256'], inputs_sha256=inputs_sha256, **prior_binding)
        exclusive_json(control / 'started.json', start)
        start_digest = sha((control / 'started.json').read_bytes())
        entry = dict(name=name, kind=kind, status='running', elapsed_seconds=limit,
            reserved_upper_bound_seconds=limit, receipt=_path(control / 'started.json', root))
        budget['stages'].append(entry)
        _retotal(budget)
        _publish_budget(budget_path, budget)
        status, error, returncode, cleanup_confirmed = 'completed', None, None, True
        try:
            if output.exists():
                raise ValueError('worker output already exists; preserve its bytes')
            _prior_debit(budget, root, deadline)
            _prior_receipts(budget, root, deadline)
            _sources(source_manifest, root, budget['source_manifest_sha256'], deadline)
            _inputs(inputs, inputs_sha256, deadline)
            if time.perf_counter()+CLEANUP_ALLOWANCE >= deadline:
                raise TimeoutError('preflight exhausted worker time')
            with (control / 'stdout.log').open('xb') as stdout, (control / 'stderr.log').open('xb') as stderr:
                process, tree = _launch(command, root, stdout, stderr)
                cleanup_confirmed = False
                try:
                    returncode = process.wait(timeout=max(0, deadline-CLEANUP_ALLOWANCE-time.perf_counter()))
                except BaseException:
                    _cleanup(process, tree, deadline, force=True)
                    cleanup_confirmed = True
                    raise
                leftovers = _cleanup(process, tree, deadline)
                cleanup_confirmed = True
                stdout.flush()
                stderr.flush()
                os.fsync(stdout.fileno())
                os.fsync(stderr.fileno())
            if leftovers:
                status, error = 'error', 'worker exited with a live descendant; owned tree terminated'
            elif returncode != 0:
                status, error = 'error', f'worker exited with code {returncode}'
            _sources(source_manifest, root, budget['source_manifest_sha256'], deadline)
            _inputs(inputs, inputs_sha256, deadline)
            _prior_debit(budget, root, deadline)
        except WorkerTerminationError as exc:
            status, error, cleanup_confirmed = 'interrupted', str(exc), False
        except (TimeoutError, subprocess.TimeoutExpired) as exc:
            status, error = 'timeout', str(exc)
        except KeyboardInterrupt:
            status, error = 'interrupted', 'foreground parent interrupted; no automatic retry'
        except ValueError as exc:
            status, error = 'refused', str(exc)
        except Exception as exc:
            status, error = 'error', f'{type(exc).__name__}: {exc}'
        outputs = {}
        try:
            outputs = output_snapshot(output, control, deadline)
        except Exception as exc:
            status = 'timeout' if isinstance(exc, TimeoutError) else 'error'
            error = (error + '; ' if error else '') + 'output validation: ' + str(exc)
        measured = time.perf_counter()-started
        charged = measured+PUBLICATION_ALLOWANCE
        if charged > limit:
            status, error = 'timeout', 'stage validation/publication bound exceeded; ' + (error or '')
        terminal = dict(format=FORMAT, request=request, status=status, error=error,
            returncode=returncode, cleanup_confirmed=cleanup_confirmed, finished_utc=utc(),
            started_sha256=start_digest, source_manifest_sha256=budget['source_manifest_sha256'],
            inputs_sha256=inputs_sha256, outputs=outputs, limit_seconds=limit,
            measured_before_publication_seconds=measured,
            publication_allowance_seconds=PUBLICATION_ALLOWANCE, elapsed_seconds=charged, **prior_binding)
        terminal_path = control / 'terminal.json'
        exclusive_json(terminal_path, terminal)
        entry.update(status=status, elapsed_seconds=charged,
            receipt=_path(terminal_path, root), terminal_sha256=sha(terminal_path.read_bytes()))
        _retotal(budget)
        _publish_budget(budget_path, budget)
        if not cleanup_confirmed:
            raise WorkerTerminationError('cleanup unconfirmed; terminal retained and lock retained')
        if time.perf_counter()-started > charged:
            # Preserve the original terminal as a completed computation attempt,
            # but publish a distinct failure so it cannot imply a settled stage.
            failure_path = control / 'publication-failure.json'
            failure = dict(format=FORMAT, request=request, status='interrupted',
                error='publication allowance exceeded; unknown excess time; lock retained',
                prior_terminal_sha256=entry['terminal_sha256'], cleanup_confirmed=True,
                measured_elapsed_seconds=time.perf_counter()-started)
            exclusive_json(failure_path, failure)
            entry.update(status='interrupted', elapsed_seconds=time.perf_counter()-started+PUBLICATION_ALLOWANCE,
                receipt=_path(failure_path, root), terminal_sha256=sha(failure_path.read_bytes()))
            _retotal(budget)
            _publish_budget(budget_path, budget)
            raise ValueError('publication allowance exceeded; lock retained for unknown excess time')
        settled = True
        return terminal
    finally:
        if settled or not stage_started:
            lock.unlink()


def parser():
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument('--name', required=True)
    value.add_argument('--kind', required=True, choices=tuple(dict.fromkeys((*KIND_LIMITS, *CONTINUATION_KIND_LIMITS))))
    value.add_argument('--source-manifest', required=True, type=Path)
    value.add_argument('--inputs', type=Path)
    value.add_argument('--inputs-sha256')
    value.add_argument('--output-dir', required=True, type=Path)
    value.add_argument('--budget', type=Path, default=ROOT / '.development/body-workload/budget.json')
    value.add_argument('--receipt-root', type=Path, default=ROOT / '.development/body-workload/coordinator/receipts')
    value.add_argument('command', nargs=argparse.REMAINDER)
    return value


def main():
    args = parser().parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    try:
        result = run_one(name=args.name, kind=args.kind, command=command,
            source_manifest=args.source_manifest, output_dir=args.output_dir,
            inputs=args.inputs, inputs_sha256=args.inputs_sha256, budget_path=args.budget,
            receipt_root=args.receipt_root, started=_MODULE_STARTED)
    except Exception as exc:
        print(f'Coordinator refused: {type(exc).__name__}: {exc}', file=sys.stderr)
        return 2
    print(json.dumps(result, allow_nan=False))
    return 0 if result['status'] == 'completed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
