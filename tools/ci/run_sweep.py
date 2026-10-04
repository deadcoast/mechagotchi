"""Full verification sweep with retained diagnostics (DR 0034 / DR 0061).

Use the current interpreter with all lab/cli/game dependencies provisioned.
--quick skips workshop for local diagnosis only; CI runs every suite.
Logs and partial summaries survive failures under .ci-logs (gitignored).
"""
from __future__ import annotations
import argparse
import importlib.metadata
import json
import os
import platform
import re
import subprocess
import sys
import time
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUITES: list[tuple[str, Path]] = [
    ('package', ROOT / 'packages/mecha_engine/tests'),
    ('cli', ROOT / 'tools/mechas_cli/tests'),
    ('game', ROOT / 'game/tests'),
    ('workshop', ROOT / 'workshop/tests'),
    ('ci', ROOT / 'tools/ci/tests'),
]


def run_suite(name: str, directory: Path, log_dir: Path, *, timeout: float = 900) -> dict:
    env = dict(os.environ)
    env.setdefault('SDL_VIDEODRIVER', 'dummy')
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['PYTHONIOENCODING'] = 'utf-8'
    log_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    command = [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', str(directory), '-p', 'test_*.py', '-v']
    try:
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8',
                                errors='replace', cwd=ROOT, env=env, timeout=timeout)
        stdout, stderr, returncode = result.stdout, result.stderr, result.returncode
        status = 'passed' if returncode == 0 else 'failed'
    except subprocess.TimeoutExpired as error:
        def decoded(value):
            return value.decode('utf-8', errors='replace') if isinstance(value, bytes) else (value or '')
        stdout, stderr = decoded(error.stdout), decoded(error.stderr)
        stderr += f'\nSUITE TIMEOUT after {timeout:g} seconds\n'
        returncode, status = None, 'timeout'
    except OSError as error:
        stdout, stderr, returncode, status = '', str(error), None, 'failed'
    count = re.search(r'Ran (\d+) tests?', stderr)
    skipped = re.search(r'skipped=(\d+)', stderr)
    tests_run = int(count.group(1)) if count else 0
    if status == 'passed' and not tests_run:
        status = 'failed'
        stderr += '\nNo tests discovered; empty verification cannot pass.\n'
    stem = re.sub(r'[^A-Za-z0-9_.-]', '_', name)
    for stream, value in [('stdout', stdout), ('stderr', stderr)]:
        (log_dir / f'{stem}.{stream}.log').write_text(value, encoding='utf-8', newline='\n')
    return {'name': name, 'status': status, 'returncode': returncode,
            'tests_run': tests_run, 'skipped': int(skipped.group(1)) if skipped else 0,
            'seconds': round(time.monotonic() - started, 3),
            'stdout_log': f'{stem}.stdout.log', 'stderr_log': f'{stem}.stderr.log'}


def validate_artifacts() -> tuple[bool, str]:
    checked = 0
    for path in sorted((ROOT / 'data').rglob('*.json')):
        try:
            json.loads(path.read_text(encoding='utf-8'))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            return False, f'{path.relative_to(ROOT).as_posix()}: {error}'
        checked += 1
    return True, f'{checked} JSON artifacts valid'


def environment_report() -> dict:
    dependencies = {}
    for name in ('pydantic', 'jsonschema', 'typer', 'rich', 'pygame-ce', 'pyinstaller'):
        try:
            dependencies[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            dependencies[name] = None
    return {'python': sys.version, 'executable': sys.executable,
            'platform': platform.platform(), 'zlib': zlib.ZLIB_RUNTIME_VERSION,
            'dependencies': dependencies}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quick', action='store_true', help='skip workshop (local diagnosis only)')
    parser.add_argument('--log-dir', type=Path, default=ROOT / '.ci-logs')
    parser.add_argument('--suite-timeout', type=float, default=900,
                        help='seconds per suite (more than twice the measured slowest CI suite)')
    args = parser.parse_args()
    if args.suite_timeout <= 0:
        parser.error('--suite-timeout must be positive')
    args.log_dir.mkdir(parents=True, exist_ok=True)
    plan = [(f'lab:{lab.name}', lab) for lab in sorted((ROOT / 'labs').iterdir())
            if lab.is_dir() and any(lab.glob('test_*.py'))]
    plan += [(name, path) for name, path in SUITES if not (args.quick and name == 'workshop')]
    summary = {'environment': environment_report(), 'quick': args.quick, 'suites': [], 'complete': False}
    def persist():
        (args.log_dir / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8', newline='\n')
    persist()
    failures = []
    for name, directory in plan:
        print(f'{name:32} RUNNING', flush=True)
        result = run_suite(name, directory, args.log_dir, timeout=args.suite_timeout)
        summary['suites'].append(result)
        persist()
        print(f"{name:32} {result['status'].upper()} {result['tests_run']} tests, "
              f"{result['skipped']} skipped [{result['seconds']:.1f}s]", flush=True)
        if result['status'] != 'passed':
            failures.append(name)
            if os.environ.get('GITHUB_ACTIONS'):
                print(f'::group::{name} failure diagnostics', flush=True)
            for key in ('stdout_log', 'stderr_log'):
                print((args.log_dir / result[key]).read_text(encoding='utf-8'), flush=True)
            if os.environ.get('GITHUB_ACTIONS'):
                print('::endgroup::', flush=True)
    ok, detail = validate_artifacts()
    print(f"{'data artifacts':32} {'OK' if ok else 'FAIL'} {detail}", flush=True)
    if not ok:
        failures.append('data artifacts')
    summary.update(complete=True, failures=failures, artifacts={'ok': ok, 'detail': detail})
    persist()
    print('\nSWEEP FAILED: ' + ', '.join(failures) if failures else '\nSWEEP GREEN', flush=True)
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
