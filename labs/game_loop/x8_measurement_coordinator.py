"""One foreground, parent-invoked X8 measurement with durable budget guards.

Workers own their output paths. This coordinator owns a separate control/name
receipt directory and the shared ledger. It never retries, batches, changes the
scientific plan, or recovers an unknown interrupted debit automatically.
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
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
KINDS = ('setup', 'parity', 'cohort', 'duplicate', 'role', 'weather', 'native', 'analysis', 'publication')
FORMAT = 'x8_parent_measurement_v1'
PUBLICATION_ALLOWANCE = 0.25
POST_WORK_ALLOWANCE = 10.0


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def utc():
    return datetime.now(timezone.utc).isoformat()


def encode(value):
    return (json.dumps(value, indent=2, allow_nan=False) + '\n').encode('utf-8')


def read(path):
    return json.loads(Path(path).read_bytes())


def exclusive_json(path, value):
    with Path(path).open('xb') as stream:
        stream.write(encode(value))
        stream.flush()
        os.fsync(stream.fileno())


def atomic_budget(path, value):
    """Only the holder of the exclusive parent lock calls this function."""
    temporary = path.with_suffix('.publishing')
    exclusive_json(temporary, value)
    os.replace(temporary, path)


def debit(entry):
    value = entry.get('elapsed_seconds')
    if type(value) not in (float, int) or not math.isfinite(value) or value < 0:
        raise ValueError('invalid budget time debit')
    return value


def check_budget(value):
    expected = dict(format='x8_measurement_budget_v1', total_limit_seconds=1200,
        per_trial_limit_seconds=120, setup_limit_seconds=120,
        cohort_reservation_seconds=600, native_reservation_seconds=120)
    if any(value.get(key) != item for key, item in expected.items()):
        raise ValueError('registered budget bounds changed')
    stages, validations = value.get('stages'), value.get('validations', [])
    if not isinstance(stages, list) or not isinstance(validations, list):
        raise ValueError('invalid budget entries')
    names = [item.get('name') for item in stages]
    if len(names) != len(set(names)):
        raise ValueError('duplicate budget stage name')
    total = sum(debit(item) for item in stages + validations)
    if (not math.isclose(total, value.get('elapsed_seconds', -1), abs_tol=1e-7)
            or not math.isclose(1200-total, value.get('remaining_seconds', -1), abs_tol=1e-7)):
        raise ValueError('budget accounting differs from retained debits')
    releases = value.get('reservation_releases', {})
    if not isinstance(releases, dict) or any(key != 'cohort' for key in releases):
        raise ValueError('invalid reservation release evidence')
    if 'cohort' in releases:
        marker = releases['cohort']
        raw = Path(marker['proof']).read_bytes()
        proof = json.loads(raw)
        if (sha(raw) != marker['proof_sha256'] or proof.get('kind') != 'cohort'
                or proof.get('total_limit_seconds') != 1200
                or len(proof.get('completed_receipts', {})) != 40
                or proof.get('source_manifest_sha256') != value.get('source_manifest_sha256')
                or proof.get('frozen_inputs_sha256') != value.get('frozen_inputs_sha256')):
            raise ValueError('reservation release integrity differs')
    return value


def retotal(budget):
    budget['elapsed_seconds'] = sum(debit(item) for item in budget['stages'] + budget.get('validations', []))
    budget['remaining_seconds'] = 1200-budget['elapsed_seconds']


def available_seconds(budget, kind):
    entries = budget['stages'] + budget.get('validations', [])
    cohort = (0 if 'cohort' in budget.get('reservation_releases', {}) else
        max(0, 600-sum(debit(item) for item in entries if item.get('kind') == 'cohort')))
    native = max(0, 120-sum(debit(item) for item in entries if item.get('kind') == 'native'))
    return budget['remaining_seconds'] - (0 if kind == 'cohort' else cohort) - (0 if kind == 'native' else native)


def sources(path, root):
    raw = path.read_bytes()
    manifest = json.loads(raw)
    if set(manifest) != {'format', 'files'} or manifest['format'] != 'x8_source_manifest_v1':
        raise ValueError('invalid source manifest')
    files = manifest['files']
    if not isinstance(files, dict) or not files:
        raise ValueError('empty frozen source closure')
    if root == ROOT and Path(__file__).resolve().relative_to(root).as_posix() not in files:
        raise ValueError('source manifest must bind this coordinator')
    for relative, expected in files.items():
        if not isinstance(relative, str) or Path(relative).is_absolute():
            raise ValueError('source path must be relative')
        path = (root/relative).resolve()
        if not path.is_relative_to(root) or not re.fullmatch('[0-9a-f]{64}', str(expected)):
            raise ValueError('invalid frozen source identity')
        if sha(path.read_bytes()) != expected:
            raise ValueError('source identity drift: ' + relative)
    return sha(raw)


def input_digest(path, expected):
    if path is None:
        if expected is not None:
            raise ValueError('input digest requires input path')
        return None
    actual = sha(path.read_bytes())
    if expected is not None and actual != expected:
        raise ValueError('frozen input byte digest mismatch')
    return actual


def output_snapshot(output, control):
    result = {}
    if output is not None and output.exists():
        paths = sorted(output.rglob('*')) if output.is_dir() else [output]
        for path in paths:
            if path.is_symlink():
                raise ValueError('output symlink is not immutable evidence')
            if path.is_file():
                name = path.relative_to(output).as_posix() if output.is_dir() else output.name
                result['worker/' + name] = sha(path.read_bytes())
    for name in ('stdout.log', 'stderr.log'):
        path = control/name
        if path.exists():
            result['parent/' + name] = sha(path.read_bytes())
    return result


class WorkerTerminationError(RuntimeError):
    pass


def _kill(process):
    # Native verifiers may start an application descendant. Kill the bounded tree.
    try:
        if os.name == 'nt':
            result = subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                capture_output=True, timeout=5, check=False)
            if result.returncode != 0:
                process.kill()
                process.wait(timeout=5)
                raise RuntimeError('taskkill did not confirm complete tree termination')
        else:
            import signal
            os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=5)
    except Exception as exc:
        raise WorkerTerminationError('process tree termination unconfirmed; preserve pending lock') from exc


def _finish(control, filename, request, start_digest, status, error, returncode,
            output, budget, entry, budget_path, started, limit):
    outputs = output_snapshot(output, control)
    measured = time.perf_counter()-started
    charged = measured+PUBLICATION_ALLOWANCE
    if charged > limit:
        status = 'timeout'
        error = 'Stage including validation/publication exceeded its reserved wall bound; ' + (error or '')
    terminal = dict(format=FORMAT, request=request, status=status, error=error,
        returncode=returncode, finished_utc=utc(), measured_before_publication_seconds=measured,
        publication_allowance_seconds=PUBLICATION_ALLOWANCE, elapsed_seconds=charged,
        limit_seconds=limit, start_sha256=start_digest, outputs=outputs)
    path = control/filename
    exclusive_json(path, terminal)
    entry.update(status=status, elapsed_seconds=charged, receipt=str(path), terminal_sha256=sha(path.read_bytes()))
    retotal(budget)
    atomic_budget(budget_path, budget)
    return terminal


def run_one(*, name, kind, command, source_manifest, output_dir=None, inputs=None,
            inputs_sha256=None, budget_path=ROOT/'.development/x8/budget.json',
            receipt_root=ROOT/'.development/x8/study/control', root=ROOT, started=None):
    """Run exactly one declared Python worker; return its parent terminal receipt.

    Completed reuse is integrity-checked and charged as a validation entry. A
    pending lock/receipt, failed prior stage or corrupt receipt refuses. Actual
    measured time plus an explicit 250ms publication allowance is debited; if
    publication exceeds it, retain the lock and stop with unknown excess time.
    No caller may clear that interruption without a prospective repair record.
    """
    started = time.perf_counter() if started is None else started
    if not isinstance(name, str) or not re.fullmatch('[A-Za-z0-9][A-Za-z0-9_.-]{0,95}', name):
        raise ValueError('stage name must be one safe unique directory name')
    if kind not in KINDS or not command or any(not isinstance(arg, str) for arg in command):
        raise ValueError('invalid declared stage kind or command')
    root, budget_path, receipt_root = Path(root).resolve(), Path(budget_path).resolve(), Path(receipt_root).resolve()
    source_manifest = Path(source_manifest).resolve()
    output = Path(output_dir).resolve() if output_dir is not None else None
    inputs = Path(inputs).resolve() if inputs is not None else None
    control = receipt_root/name
    if output is not None and (output.is_relative_to(control) or control.is_relative_to(output)):
        raise ValueError('worker output must be separate from parent receipt directory')
    request = dict(name=name, kind=kind, command=[sys.executable, '-B', *command], root=str(root),
        source_manifest=str(source_manifest), inputs=str(inputs) if inputs else None,
        inputs_sha256=inputs_sha256, output=str(output) if output else None)
    lock = budget_path.with_suffix('.lock')
    try:
        exclusive_json(lock, dict(format=FORMAT, name=name, pid=os.getpid(), started_utc=utc(),
            started_monotonic=started, control=str(control), request=request))
    except FileExistsError as error:
        raise ValueError('active or interrupted coordinator: elapsed time may be unknown; retain lock and refuse') from error
    settled = False
    try:
        budget = check_budget(read(budget_path))
        existing = next((item for item in budget['stages'] if item['name'] == name), None)
        if any(item.get('status') not in ('completed', 'matched') for item in budget['stages'] + budget.get('validations', [])):
            raise ValueError('failed or incomplete stage retained; no additional simulation without prospective repair')
        if kind == 'publication' and existing is None and any(item.get('kind') == 'publication' for item in budget['stages']):
            raise ValueError('only one prospective I/O publication repair is permitted')
        limit = min(120.0, available_seconds(budget, kind))
        if limit <= time.perf_counter()-started+POST_WORK_ALLOWANCE:
            raise ValueError('insufficient unreserved budget before next trial')
        if existing is not None:
            terminal_path = control/'terminal.json'
            if existing.get('status') != 'completed':
                raise ValueError('failed or interrupted stage cannot be rerun')
            # A reuse attempt is itself durable and debited, including failures.
            index = len(budget.get('validations', []))
            filename = f'validation-{index:04d}.json'
            entry = dict(name=name, kind=kind, status='running', elapsed_seconds=limit)
            budget.setdefault('validations', []).append(entry)
            retotal(budget)
            atomic_budget(budget_path, budget)
            status, error = 'completed', None
            try:
                raw = terminal_path.read_bytes()
                terminal = json.loads(raw)
                if sha(raw) != existing.get('terminal_sha256') or terminal['request'] != request:
                    raise ValueError('terminal receipt integrity or declared request differs')
                if sha((control/'start.json').read_bytes()) != terminal['start_sha256']:
                    raise ValueError('start receipt integrity differs')
                original = read(control/'start.json')
                if sources(source_manifest, root) != original['source_manifest_sha256']:
                    raise ValueError('source manifest changed since completed receipt')
                if input_digest(inputs, inputs_sha256) != original['actual_inputs_sha256']:
                    raise ValueError('input changed since completed receipt')
                if output_snapshot(output, control) != terminal['outputs']:
                    raise ValueError('output integrity differs from completed receipt')
                if sources(source_manifest, root) != original['source_manifest_sha256'] or input_digest(inputs, inputs_sha256) != original['actual_inputs_sha256']:
                    raise ValueError('source or input drift during reuse validation')
            except Exception as exc:
                status, error = 'refused', str(exc)
            result = _finish(control, filename, request, None, status, error, None,
                output, budget, entry, budget_path, started, limit)
            if time.perf_counter()-started > result['elapsed_seconds']:
                raise ValueError('publication allowance exceeded; unknown excess debit retained')
            settled = True
            if result['status'] != 'completed':
                raise ValueError(result['error'] or 'completed reuse validation failed')
            return dict(terminal, reused=True, validation_receipt=str(control/filename))
        if control.exists():
            raise ValueError('unreconciled interrupted receipt directory; unknown elapsed time, no rerun')
        control.mkdir(parents=True, exist_ok=False)
        # Start is durable before all source/input scans, model loading and child launch.
        start = dict(format=FORMAT, request=request, started_utc=utc(), started_monotonic=started,
            source_manifest_sha256=sha(source_manifest.read_bytes()), actual_inputs_sha256=input_digest(inputs, None),
            limit_seconds=limit)
        exclusive_json(control/'start.json', start)
        start_digest = sha((control/'start.json').read_bytes())
        entry = dict(name=name, kind=kind, status='running', elapsed_seconds=limit,
            receipt=str(control/'start.json'), reserved_upper_bound_seconds=limit)
        budget['stages'].append(entry)
        budget.setdefault('source_manifest_sha256', start['source_manifest_sha256'])
        if start['actual_inputs_sha256'] is not None:
            budget.setdefault('frozen_inputs_sha256', start['actual_inputs_sha256'])
        retotal(budget)
        atomic_budget(budget_path, budget)
        status, error, returncode, process = 'completed', None, None, None
        termination_unconfirmed = False
        try:
            if start['source_manifest_sha256'] != budget['source_manifest_sha256']:
                raise ValueError('source manifest differs from frozen cross-stage identity')
            if start['actual_inputs_sha256'] is not None and start['actual_inputs_sha256'] != budget['frozen_inputs_sha256']:
                raise ValueError('input differs from frozen cross-stage identity')
            if output is not None and output.exists():
                raise ValueError('worker output already exists; preserve interrupted evidence')
            if sources(source_manifest, root) != start['source_manifest_sha256']:
                raise ValueError('source manifest drift before worker')
            input_digest(inputs, inputs_sha256)
            remaining = limit-(time.perf_counter()-started)-POST_WORK_ALLOWANCE
            if remaining <= 0:
                raise ValueError('no remaining time after preflight')
            with (control/'stdout.log').open('xb') as stdout, (control/'stderr.log').open('xb') as stderr:
                process_options = ({'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == 'nt' else {'start_new_session': True})
                process = subprocess.Popen(request['command'], cwd=root, stdout=stdout, stderr=stderr, **process_options)
                try:
                    returncode = process.wait(timeout=max(0, limit-(time.perf_counter()-started)-POST_WORK_ALLOWANCE))
                except subprocess.TimeoutExpired:
                    _kill(process)
                    status, error = 'timeout', 'bounded worker exceeded remaining stage time'
                except BaseException:
                    _kill(process)
                    raise
                stdout.flush(); stderr.flush()
                os.fsync(stdout.fileno()); os.fsync(stderr.fileno())
            if status == 'completed' and returncode != 0:
                status, error = 'error', f'worker exited with code {returncode}'
            if sources(source_manifest, root) != start['source_manifest_sha256']:
                raise ValueError('source manifest drift after worker')
            if input_digest(inputs, inputs_sha256) != start['actual_inputs_sha256']:
                raise ValueError('input drift after worker')
        except WorkerTerminationError as exc:
            status, error = 'interrupted', str(exc)
            termination_unconfirmed = True
        except KeyboardInterrupt:
            status, error = 'interrupted', 'foreground parent interrupted; no retry'
        except ValueError as exc:
            status, error = 'refused', str(exc)
        except Exception as exc:
            status, error = 'error', f'{type(exc).__name__}: {exc}'
        result = _finish(control, 'terminal.json', request, start_digest, status, error,
            returncode, output, budget, entry, budget_path, started, limit)
        if time.perf_counter()-started > result['elapsed_seconds']:
            raise ValueError('publication allowance exceeded; unknown excess debit retained')
        if termination_unconfirmed:
            raise ValueError('process tree termination unconfirmed; lock retained, no further workers')
        settled = True
        return result
    finally:
        # Errors before a durable terminal deliberately leave an exclusive lock.
        if settled:
            lock.unlink()


def _cohort_case(request):
    command = request['command']
    def option(name):
        if command.count(name) != 1:
            raise ValueError('cohort proof requires exact registered command options')
        return command[command.index(name)+1]
    if request['kind'] != 'cohort' or option('--stage') != 'cohort' or option('--backend') != 'package':
        raise ValueError('reservation proof must be a package cohort measurement')
    return int(option('--seed')), option('--arm')


def release_reservation(*, kind, completed_receipts, budget_path=ROOT/'.development/x8/budget.json',
                        receipt_root=ROOT/'.development/x8/study/control', root=ROOT, started=None):
    """Release unused cohort reserve only against all 40 frozen registered cases.

    Parent invokes this after the declared duplicate/analysis steps. This performs
    only integrity checks, records its own debit, and never increases total time.
    Native reservation stays protected; this API does not invent its completion.
    """
    started = time.perf_counter() if started is None else started
    if kind != 'cohort':
        raise ValueError('only the fixed cohort reservation has a release protocol')
    budget_path, root, receipt_root = Path(budget_path).resolve(), Path(root).resolve(), Path(receipt_root).resolve()
    name = 'release-cohort-reservation'
    control = receipt_root/name
    lock = budget_path.with_suffix('.lock')
    try:
        exclusive_json(lock, dict(format=FORMAT, name=name, pid=os.getpid(), started_utc=utc(), started_monotonic=started))
    except FileExistsError as exc:
        raise ValueError('active or interrupted coordinator; unknown elapsed time') from exc
    settled = False
    try:
        budget = check_budget(read(budget_path))
        if kind in budget.get('reservation_releases', {}):
            raise ValueError('cohort reservation already released; preserve existing proof')
        if any(item.get('status') not in ('completed', 'matched') for item in budget['stages'] + budget.get('validations', [])):
            raise ValueError('failed or incomplete stage prevents reservation release')
        # Completed-cohort proof may consume its own still-protected reserve.
        limit = min(120.0, available_seconds(budget, 'cohort'))
        if limit <= time.perf_counter()-started+PUBLICATION_ALLOWANCE:
            raise ValueError('insufficient budget for release proof')
        control.mkdir(parents=True, exist_ok=False)
        paths = [str(Path(path).resolve()) for path in completed_receipts]
        request = dict(name=name, kind='analysis', release_kind=kind, completed_receipts=paths)
        start = dict(format=FORMAT, request=request, started_utc=utc(), started_monotonic=started, limit_seconds=limit)
        exclusive_json(control/'start.json', start)
        start_digest = sha((control/'start.json').read_bytes())
        entry = dict(name=name, kind='analysis', status='running', elapsed_seconds=limit, receipt=str(control/'start.json'))
        budget['stages'].append(entry)
        retotal(budget)
        atomic_budget(budget_path, budget)
        status, error, proofs = 'completed', None, {}
        try:
            if len(paths) != 40 or len(set(paths)) != 40:
                raise ValueError('release requires exactly 40 unique completed cohort receipts')
            registered = {str(Path(row['receipt']).resolve()): row for row in budget['stages'] if row.get('kind') == 'cohort'}
            if set(paths) != set(registered):
                raise ValueError('release proof differs from all registered cohort measurements')
            initial_request = read(paths[0])['request']
            if (sources(Path(initial_request['source_manifest']), root) != budget.get('source_manifest_sha256')
                    or input_digest(Path(initial_request['inputs']), None) != budget.get('frozen_inputs_sha256')):
                raise ValueError('source or input drift before cohort release proof')
            cases, common_identity = set(), None
            manifest_path = frozen_input_path = None
            for path_string in paths:
                if time.perf_counter()-started+PUBLICATION_ALLOWANCE >= limit:
                    raise ValueError('release proof exceeded bounded stage time')
                path = Path(path_string)
                raw = path.read_bytes()
                terminal = json.loads(raw)
                if sha(raw) != registered[path_string]['terminal_sha256'] or terminal['status'] != 'completed':
                    raise ValueError('cohort terminal integrity differs')
                worker_control = path.parent
                start_raw = (worker_control/'start.json').read_bytes()
                if sha(start_raw) != terminal['start_sha256']:
                    raise ValueError('cohort start integrity differs')
                original = json.loads(start_raw)
                request_item = terminal['request']
                if original['request'] != request_item:
                    raise ValueError('cohort start/terminal requests differ')
                case = _cohort_case(request_item)
                if case in cases:
                    raise ValueError('duplicate cohort seed/arm proof')
                cases.add(case)
                identity = (original['source_manifest_sha256'], original['actual_inputs_sha256'])
                if identity[1] is None or (common_identity is not None and identity != common_identity):
                    raise ValueError('cohort frozen source/input identities differ')
                common_identity = identity
                manifest_path = Path(request_item['source_manifest'])
                frozen_input_path = Path(request_item['inputs'])
                output = Path(request_item['output']) if request_item['output'] else None
                if output_snapshot(output, worker_control) != terminal['outputs']:
                    raise ValueError('cohort output integrity differs')
                proofs[path_string] = sha(raw)
            expected = {(seed, arm) for seed in range(20260700, 20260710) for arm in 'ABCD'}
            if cases != expected:
                raise ValueError('release does not cover the exact registered 40 seed/arm cases')
            if common_identity != (budget.get('source_manifest_sha256'), budget.get('frozen_inputs_sha256')):
                raise ValueError('cohort identities differ from pinned budget')
            if sources(manifest_path, root) != common_identity[0] or input_digest(frozen_input_path, None) != common_identity[1]:
                raise ValueError('source or input drift during cohort release')
            proof = dict(format=FORMAT, kind=kind, completed_receipts=proofs,
                source_manifest_sha256=common_identity[0], frozen_inputs_sha256=common_identity[1],
                total_limit_seconds=1200)
            exclusive_json(control/'proof.json', proof)
            # Hashing source before and after proof publication bounds that I/O too.
            if sources(manifest_path, root) != common_identity[0] or input_digest(frozen_input_path, None) != common_identity[1]:
                raise ValueError('source or input drift after cohort release proof')
        except Exception as exc:
            status, error = 'refused', str(exc)
        if status == 'completed':
            budget.setdefault('reservation_releases', {})['cohort'] = dict(
                proof=str(control/'proof.json'), proof_sha256=sha((control/'proof.json').read_bytes()))
        result = _finish(control, 'terminal.json', request, start_digest, status, error,
            None, None, budget, entry, budget_path, started, limit)
        if result['status'] != 'completed':
            budget.get('reservation_releases', {}).pop('cohort', None)
            atomic_budget(budget_path, budget)
        if time.perf_counter()-started > result['elapsed_seconds']:
            raise ValueError('publication allowance exceeded; unknown excess debit retained')
        settled = True
        if result['status'] != 'completed':
            raise ValueError(result['error'] or 'cohort release refused')
        return result
    finally:
        if settled:
            lock.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', required=True)
    parser.add_argument('--kind', choices=KINDS, required=True)
    parser.add_argument('--source-manifest', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--inputs', type=Path)
    parser.add_argument('--inputs-sha256')
    parser.add_argument('--budget', type=Path, default=ROOT/'.development/x8/budget.json')
    parser.add_argument('--receipt-root', type=Path, default=ROOT/'.development/x8/study/control')
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    try:
        result = run_one(name=args.name, kind=args.kind, command=command, source_manifest=args.source_manifest,
            output_dir=args.output_dir, inputs=args.inputs, inputs_sha256=args.inputs_sha256,
            budget_path=args.budget, receipt_root=args.receipt_root, started=_MODULE_STARTED)
    except Exception as error:
        print(json.dumps(dict(status='refused', error=str(error))), file=sys.stderr)
        return 2
    print(json.dumps(dict(status=result['status'], elapsed_seconds=result['elapsed_seconds'], reused=result.get('reused', False))))
    return 0 if result['status'] == 'completed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
