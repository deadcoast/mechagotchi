"""Verify workload delivery using only stdlib and a relocated Windows artifact.

This is operational delivery evidence. No source game/engine imports, injected
SDL events, OS keyboard automation, care holdouts or new production eras occur.
The optional reproduction consumes one existing immutable source-era record.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import tempfile
import time

from x8_earned_coordinator import _WindowsTree, _PosixTree, _cleanup, WorkerTerminationError

from verify_detached_release import (inventory, isolated_environment, json_read,
    relocate_bundle, sha, validate_artifact_manifest)

MODEL = 'workload-v1'
FORMAT = 'mechagotchi_body_workload_delivery_v2'


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode()


def digest(raw): return hashlib.sha256(raw).hexdigest()


def validate_source_binding(runtime, frozen, expected_head):
    """Bind every shipped game/engine source file, including unexpected additions."""
    def relevant(name):
        return name.startswith(('game/src/', 'packages/mecha_engine/src/')) and name.endswith('.py')
    recorded = runtime.get('source', {})
    expected = {name: value for name, value in frozen.get('files', {}).items() if relevant(name)}
    actual = {name: value for name, value in recorded.get('files', {}).items() if relevant(name)}
    if not expected or not any(name.startswith('game/src/') for name in expected) or not any(name.startswith('packages/mecha_engine/src/') for name in expected):
        raise ValueError('Frozen source must contain the complete application and engine closure.')
    if recorded.get('head') != expected_head or expected != actual:
        raise ValueError('Built artifact differs from the frozen application/engine source or expected HEAD.')
    return len(expected)



def current_life_identity(payload):
    """Read the actual save schema; current life is the final lineage record."""
    if not isinstance(payload, dict):
        raise ValueError('Saved companion must be an object.')
    chronicle = payload.get('chronicle')
    records = payload.get('lineage')
    grid = payload.get('grid')
    keeper = chronicle.get('keeper_id') if isinstance(chronicle, dict) else None
    if not isinstance(keeper, str) or not keeper.strip():
        raise ValueError('Saved Keeper identity is missing or malformed.')
    if not isinstance(records, list) or not records or any(not isinstance(row, dict) for row in records):
        raise ValueError('Saved lineage must contain life records.')
    identities = [row.get('life_id') for row in records]
    prefix = keeper + ':life-'
    if (any(not isinstance(value, str) or not value.startswith(prefix) or len(value) == len(prefix)
            for value in identities) or len(set(identities)) != len(identities)):
        raise ValueError('Saved lineage has missing, duplicate or foreign life identities.')
    if (not isinstance(grid, dict) or not isinstance(grid.get('grid_id'), str) or not grid['grid_id'].strip()
            or records[-1].get('grid_id') != grid['grid_id']):
        raise ValueError('Current lineage body differs from the saved companion.')
    return identities[-1]


def validate_active_session(payload):
    """Independently read and recompute the registered projection from saved cells."""
    try:
        state = payload['state']; grid = payload['grid']
        if payload['body_response'] != MODEL or state['body_response'] != MODEL or payload['lineage'][-1]['body_response'] != MODEL:
            raise ValueError('Saved model identity is not workload-v1 at every active boundary.')
        occupied = {(cell['x'], cell['y']): cell for cell in grid['cells']
                    if cell.get('role') != 'empty' and cell.get('material') != 'void'}
        if not occupied: raise ValueError('Active body has no occupied mass.')
        for cell in grid['cells']:
            damage = cell.get('damage', 0)
            if type(damage) not in (int, float) or not math.isfinite(damage) or not 0 <= damage <= 1:
                raise ValueError('Invalid saved body integrity.')
        supporting = {tuple(pos) for organ in grid.get('organs', {}).values()
                      if organ.get('role') in ('body_core', 'locomotion') for pos in organ.get('cells', [])}
        mass = len(occupied)
        capacity = math.fsum(1 - occupied[pos].get('damage', 0) for pos in sorted(supporting & occupied.keys()))
        floor = max(1., mass * .07 / .34)
        expected = dict(occupied_mass=mass, functional_capacity=capacity, capacity_floor=floor,
                        play_energy_cost=round(.07 * mass / max(capacity, floor), 6))
        workload = state['body_workload']
        if (not isinstance(workload, dict) or set(workload) != set(expected)
                or type(workload['occupied_mass']) is not int
                or any(type(workload[key]) not in (int, float) or not math.isfinite(workload[key])
                       for key in expected if key != 'occupied_mass')
                or workload != expected or payload['lineage'][-1].get('body_workload') != expected):
            raise ValueError('Saved workload projection differs from its actual body.')
        return expected
    except (KeyError, TypeError, AttributeError) as error:
        raise ValueError('Incomplete active model save.') from error


def cold_successor(payload, parent_id):
    state = payload.get('state', {})
    grid = payload.get('grid', {})
    lineage = payload.get('lineage', [])
    return (payload.get('learning_policy') == 'qtable' and state.get('alive') is True
            and state.get('age_ticks') == 0 and 'qtable_policy' not in state.get('thread_states', {})
            and grid.get('grid_id') != parent_id and grid.get('parent_grid_id') == parent_id
            and len(lineage) >= 2 and lineage[-2].get('grid_id') == parent_id
            and lineage[-1].get('grid_id') == grid.get('grid_id')
            and lineage[-1].get('parent_grid_id') == parent_id)


def read_active_era(ledger, campaign_id, era_index):
    """Read a source receipt without loading any simulation module or writing SQL."""
    ledger = Path(ledger).resolve()
    if not ledger.is_file(): raise ValueError('Source era ledger is missing.')
    with closing(sqlite3.connect(ledger.as_uri() + '?mode=ro', uri=True)) as conn:
        row = conn.execute('SELECT manifest_json,manifest_sha256 FROM era_executions WHERE campaign_id=? AND era_index=?', (campaign_id, era_index)).fetchone()
        if row is None: raise ValueError('Source immutable era is missing.')
        manifest = json.loads(row[0])
        if digest(canonical(manifest)) != row[1]: raise ValueError('Source execution manifest digest mismatch.')
        ref = manifest.get('inputs', {}).get('body_response_inputs_sha256')
        if not ref: raise ValueError('Source era has no active immutable model input.')
        blob = conn.execute('SELECT payload FROM execution_blobs WHERE sha256=?', (ref,)).fetchone()
        if blob is None or digest(blob[0]) != ref: raise ValueError('Source model input bytes changed.')
        options = json.loads(blob[0])
        if options != {'format': 'body_response_inputs_v1', 'body_response': MODEL}:
            raise ValueError('Source era does not declare the supported active model.')
        row = conn.execute('SELECT report_json FROM eras WHERE campaign_id=? AND era_index=?', (campaign_id, era_index)).fetchone()
        if row is None: raise ValueError('Source era report is missing.')
        report = json.loads(row[0])
        if report.get('body_response') != MODEL or digest(canonical(report)) != manifest.get('report_sha256'):
            raise ValueError('Source era report is not bound to the active input.')
        return dict(manifest=manifest, report=report, model_inputs=options, ledger_sha256=sha(ledger))


def require_launch_receipt(info, exit_code, *, allow_parser_refusal=False):
    if info is None and allow_parser_refusal and exit_code == 2:
        return
    if not isinstance(info, dict) or info.get('stopped') is not True or info.get('exit_code') != exit_code:
        raise ValueError('Required launch receipt is absent, incomplete or has a conflicting exit code.')



def _drain_owned_tree(tree, work_deadline, *, clock=None, sleeper=None):
    """Observe an empty owned tree within the original work allocation."""
    clock = time.perf_counter if clock is None else clock
    sleeper = time.sleep if sleeper is None else sleeper
    while clock() < work_deadline:
        tree.reap()
        active = tree.active()
        if type(active) is not int or active < 0:
            raise ValueError('Owned process count is unknown or invalid.')
        # A slow reap/query cannot turn a late observation into timely success.
        remaining = work_deadline - clock()
        if remaining <= 0:
            return False
        if active == 0:
            return True
        sleeper(min(.01, remaining))
    return False


def _wait_log_handles_released(log_prefix, deadline):
    """Windows job accounting may reach zero just before inherited IO closes."""
    if os.name != 'nt': return
    import ctypes as c
    from ctypes import wintypes as w
    kernel = c.WinDLL('kernel32', use_last_error=True)
    kernel.CreateFileW.argtypes = [w.LPCWSTR, w.DWORD, w.DWORD, c.c_void_p, w.DWORD, w.DWORD, w.HANDLE]
    kernel.CreateFileW.restype = w.HANDLE
    kernel.CloseHandle.argtypes = [w.HANDLE]
    kernel.CloseHandle.restype = w.BOOL
    invalid = c.c_void_p(-1).value
    for path in (log_prefix.with_suffix('.stdout.log'), log_prefix.with_suffix('.stderr.log')):
        if not path.exists(): continue
        while True:
            if time.perf_counter() >= deadline:
                raise WorkerTerminationError('Log closure was not confirmed within the delivery deadline.')
            handle = kernel.CreateFileW(str(path), 0x80000000, 0, None, 3, 0x80, None)
            if handle != invalid:
                if not kernel.CloseHandle(handle) or time.perf_counter() >= deadline:
                    raise WorkerTerminationError('Log closure was not confirmed within the delivery deadline.')
                break
            code = c.get_last_error()
            if code not in (32, 33) or time.perf_counter() >= deadline:
                raise WorkerTerminationError('Owned process log handles remain open: ' + str(path))
            time.sleep(min(.01, max(0., deadline-time.perf_counter())))


def run_bounded(command, cwd, env, log_prefix, timeout):
    """Own the complete tree even when its root exits; cleanup is inside the cap."""
    if timeout <= 0: raise ValueError('Delivery runtime budget is exhausted.')
    deadline = time.perf_counter() + timeout
    cleanup_allowance = min(10., timeout / 2)
    work_deadline = deadline - cleanup_allowance
    log_prefix = Path(log_prefix)
    tree = _WindowsTree() if os.name == 'nt' else _PosixTree()
    process = None
    cleanup_confirmed = False
    cleanup_attempted = False
    try:
        with log_prefix.with_suffix('.stdout.log').open('x', encoding='utf-8') as stdout, log_prefix.with_suffix('.stderr.log').open('x', encoding='utf-8') as stderr:
            options = ({'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW | 0x4}
                       if os.name == 'nt' else {'start_new_session': True})
            process = subprocess.Popen(command, cwd=cwd, env=env, stdout=stdout, stderr=stderr, **options)
            if os.name == 'nt': tree.attach(process)
            else: tree.pid = process.pid
            remaining = work_deadline - time.perf_counter()
            if remaining <= 0:
                raise subprocess.TimeoutExpired(command, timeout-cleanup_allowance)
            code = process.wait(timeout=remaining)
            drained = _drain_owned_tree(tree, work_deadline)
            cleanup_attempted = True
            leftovers = _cleanup(process, tree, deadline, force=not drained)
            if time.perf_counter() >= deadline:
                raise WorkerTerminationError('Process tree cleanup exceeded the delivery deadline.')
            cleanup_confirmed = True
            if not drained or leftovers:
                raise RuntimeError('Owned descendant completion was not confirmed within the work deadline; tree terminated.')
            return code
    except BaseException as error:
        if process is not None and not cleanup_attempted:
            cleanup_attempted = True
            try:
                # Assignment failures still leave a suspended root owned by Popen.
                if process.poll() is None: process.kill()
                _cleanup(process, tree, deadline, force=True)
                if time.perf_counter() >= deadline:
                    raise WorkerTerminationError('Process tree cleanup exceeded the delivery deadline.')
                cleanup_confirmed = True
            except BaseException as cleanup_error:
                error = WorkerTerminationError('Process tree cleanup unconfirmed: ' + str(cleanup_error))
        error.cleanup_confirmed = cleanup_confirmed
        raise error
    finally:
        try:
            tree.close()
            _wait_log_handles_released(log_prefix, deadline)
            if time.perf_counter() >= deadline:
                raise WorkerTerminationError('Final cleanup exceeded the delivery deadline.')
        except BaseException as error:
            error.cleanup_confirmed = False
            raise


def verify(bundle, output, frozen_source, expected_head, *, source_keeper=None, campaign_id=None, era_index=None):
    started = time.monotonic()
    bundle = Path(bundle).resolve(); output = Path(output).resolve()
    if os.name != 'nt': raise ValueError('Actual delivery verification requires Windows.')
    if output.exists() or output.is_relative_to(bundle) or bundle.is_relative_to(output):
        raise ValueError('Use a new output directory disjoint from the artifact.')
    if source_keeper is not None and (not campaign_id or type(era_index) is not int or era_index < 0):
        raise ValueError('Source reproduction requires a campaign identity and nonnegative era index.')
    output.mkdir(parents=True)
    initial = inventory(bundle)
    source_before = inventory(source_keeper) if source_keeper is not None else None
    report = dict(format=FORMAT, ok=False, delivery_complete=False, checks={}, stages=[],
                  scope=dict(operational_only=True, native_process=True, native_window_driver='windows',
                             application_source_imports=False, sdl_event_injection=False, os_keyboard=False,
                             human_usability=False, new_production_eras=0),
                  source_manifest_sha256=sha(frozen_source), expected_head=expected_head,
                  source_reproduction='NOT_RUN' if source_keeper is None else 'PENDING')
    deadline = started + 480
    def save():
        report['elapsed_seconds'] = time.monotonic() - started
        (output/'report.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    def check(name, condition):
        report['checks'][name] = bool(condition); save()
        if not condition: raise ValueError('Delivery check failed: ' + name)
    with tempfile.TemporaryDirectory(prefix='mecha-workload-delivery-') as directory:
        root = Path(directory); runs = root/'runs'; runs.mkdir()
        try:
            relocated = relocate_bundle(bundle, root/'Mechagotchi')
            artifact = validate_artifact_manifest(relocated)
            runtime = json_read(relocated/'_internal/runtime-manifest.json')
            count = validate_source_binding(runtime, json_read(frozen_source), expected_head)
            check('artifact_runtime_identity', artifact.get('runtime_content_id') == runtime.get('content_id'))
            report['artifact'] = dict(bundle=str(bundle), exe_sha256=sha(bundle/'Mechagotchi.exe'),
                manifest_sha256=sha(bundle/'artifact-manifest.json'), content_id=artifact['content_id'],
                runtime_content_id=runtime['content_id'], frozen_application_files=count)
            cwd = root/'unrelated'; cwd.mkdir(); home = root/'user'; home.mkdir()
            env = isolated_environment(home); env['SDL_VIDEODRIVER'] = 'windows'
            exe = relocated/'Mechagotchi.exe'
            def launch(name, args, *, receipt=True, allow_parser_refusal=False, cap=60):
                launch_path = runs/(name+'-launch.json')
                command = [str(exe), *args, *(['--launch-info', str(launch_path)] if receipt else [])]
                stage = dict(name=name, command=command, status='started', cap_seconds=cap)
                report['stages'].append(stage); save(); at=time.monotonic()
                try:
                    code = run_bounded(command, cwd, env, output/name, min(cap, deadline-time.monotonic()-5))
                except BaseException as error:
                    stage.update(status='failed', error=str(error), cleanup_confirmed=getattr(error, 'cleanup_confirmed', False), elapsed_seconds=time.monotonic()-at); save(); raise
                stage.update(status='completed', exit_code=code, cleanup_confirmed=True, elapsed_seconds=time.monotonic()-at)
                info = json_read(launch_path) if launch_path.exists() else None
                if receipt:
                    require_launch_receipt(info, code, allow_parser_refusal=allow_parser_refusal)
                if info is not None:
                    check(name+'_receipt_completed', info.get('stopped') is True and info.get('exit_code') == code)
                    observed = info.get('runtime', {})
                    check(name+'_detached_runtime', observed.get('mode') == 'frozen_windows_x64' and observed.get('complete') is True
                          and observed.get('content_id') == runtime['content_id'])
                    loaded = observed.get('loaded_modules', {})
                    check(name+'_module_locations', bool(loaded) and all(Path(path).resolve().is_relative_to(relocated) for path in loaded.values()))
                save(); return code, info
            common = ['--fps', '0', '--tick-frames', '1', '--scale', '2']
            keeper = runs/'active'
            code, info = launch('active-new', ['--keeper-dir', str(keeper), '--new', '--body-response', MODEL,
                                 '--learning-policy', 'qtable', '--ticks', '1', *common])
            check('new_ready', code == 0 and info is not None and info.get('body_response') == MODEL)
            first = json_read(keeper/'companion.json'); validate_active_session(first)
            check('actual_windows_sdl', info.get('display', {}).get('driver') == 'windows')
            code, info = launch('active-restart', ['--keeper-dir', str(keeper), '--ticks', '1', *common])
            second = json_read(keeper/'companion.json'); validate_active_session(second)
            check('restart_same_life_and_model', code == 0 and second['session_tick'] == first['session_tick']+1
                  and current_life_identity(second) == current_life_identity(first))
            twin = runs/'successor'; shutil.copytree(keeper, twin)
            for name, choice in [('legacy-conflict', 'legacy'), ('unknown-version', 'workload-v999')]:
                before = inventory(keeper)
                code, _ = launch(name, ['--keeper-dir', str(keeper), '--body-response', choice, '--ticks', '1', *common], allow_parser_refusal=choice == 'workload-v999')
                check(name+'_refused_and_preserved', code == 2 and inventory(keeper) == before)
            code, _ = launch('natural-death', ['--keeper-dir', str(keeper), '--ticks', '120', *common])
            dead = json_read(keeper/'companion.json'); validate_active_session(dead)
            remaining = dead['session_tick']-second['session_tick']
            check('operational_natural_death', code == 0 and dead['state'].get('alive') is False and 0 < remaining <= 120)
            check('parent_learning_is_present', bool(dead['state'].get('thread_states', {}).get('qtable_policy', {}).get('q')))
            code, _ = launch('cold-successor', ['--keeper-dir', str(twin), '--auto-succeed', '--ticks', str(remaining), *common])
            child = json_read(twin/'companion.json'); validate_active_session(child)
            check('successor_model_and_cold_learning', code == 0 and cold_successor(child, second['grid']['grid_id']))
            check('successor_same_keeper', child['chronicle']['keeper_id'] == second['chronicle']['keeper_id'])
            recovery = runs/'recovery'; recovery.mkdir()
            original = b'{deliberately interrupted operational primary'
            (recovery/'companion.json').write_bytes(original)
            backup = (twin/'companion.json').read_bytes(); (recovery/'companion.bak.json').write_bytes(backup)
            before = inventory(recovery)
            code, _ = launch('recovery-conflict', ['--keeper-dir', str(recovery), '--recover-backup', '--body-response', 'legacy', '--ticks', '1', *common])
            check('recovery_conflict_preserves_both_files', code == 2 and inventory(recovery) == before)
            code, _ = launch('explicit-recovery', ['--keeper-dir', str(recovery), '--recover-backup', '--body-response', MODEL,
                                                 '--ticks', '1', *common])
            restored = json_read(recovery/'companion.json'); validate_active_session(restored)
            check('explicit_backup_restores_recorded_life', code == 0
                  and current_life_identity(restored) == current_life_identity(child)
                  and restored['session_tick'] == child['session_tick']+1 and restored['state']['age_ticks'] == 1)
            check('recovery_retains_exact_restored_checkpoint', (recovery/'companion.bak.json').read_bytes() == backup)
            check('recovery_preserves_rejected_primary', any(p.is_file() and p.read_bytes() == original for p in recovery.iterdir()))
            legacy = runs/'legacy'
            code, _ = launch('legacy-new', ['--keeper-dir', str(legacy), '--ticks', '1', *common])
            old = json_read(legacy/'companion.json')
            check('legacy_remains_absent', code == 0 and 'body_response' not in old and 'body_response' not in old['state'] and 'body_workload' not in old['state'])
            if source_keeper is not None:
                evidence = read_active_era(Path(source_keeper)/'campaign.sqlite3', campaign_id, era_index)
                report['source_era'] = dict(keeper=str(Path(source_keeper).resolve()), campaign_id=campaign_id, era_index=era_index,
                                           ledger_sha256=evidence['ledger_sha256'], report_sha256=evidence['manifest']['report_sha256'])
                source_copy = runs/'source-era'; shutil.copytree(source_keeper, source_copy)
                baseline = inventory(source_copy)
                comparison = runs/'reproduction'
                code, _ = launch('source-era-reproduce', ['--keeper-dir', str(source_copy), '--campaign-id', campaign_id,
                    '--reproduce-era', str(era_index), '--output', str(comparison)], receipt=False, cap=120)
                result = json_read(comparison/'comparison.json')
                check('source_era_full_report_and_elites_match', code == 0 and result.get('status') == 'matched'
                      and result.get('differing_paths') == [] and result.get('report') == evidence['report'])
                check('source_era_copy_is_immutable', inventory(source_copy) == baseline)
                report['source_reproduction'] = 'MATCHED'
        except (OSError, ValueError, KeyError, TypeError, AttributeError, sqlite3.Error, subprocess.SubprocessError, RuntimeError) as error:
            report['error'] = str(error)
        finally:
            shutil.copytree(runs, output/'isolated-runs')
            report['checks']['original_artifact_preserved'] = inventory(bundle) == initial
            if source_keeper is not None:
                report['checks']['original_source_keeper_preserved'] = inventory(source_keeper) == source_before
            report['checks']['wall_budget_met'] = time.monotonic() <= deadline
            report['checks']['all_process_trees_closed'] = all(stage.get('cleanup_confirmed') is True for stage in report['stages'])
            report['ok'] = bool(report['checks']) and all(report['checks'].values()) and 'error' not in report
            report['delivery_complete'] = report['ok'] and report['source_reproduction'] == 'MATCHED'
            save()
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--source-manifest', type=Path, required=True)
    parser.add_argument('--expected-head', required=True)
    parser.add_argument('--source-keeper', type=Path)
    parser.add_argument('--campaign-id')
    parser.add_argument('--era-index', type=int)
    args = parser.parse_args(argv)
    try:
        report = verify(args.bundle, args.output, args.source_manifest, args.expected_head,
                        source_keeper=args.source_keeper, campaign_id=args.campaign_id, era_index=args.era_index)
    except (OSError, ValueError) as error: parser.exit(2, str(error)+'\n')
    print(json.dumps({key: report.get(key) for key in ('ok', 'delivery_complete', 'source_reproduction', 'error')}))
    return 0 if report['ok'] else 1


if __name__ == '__main__': raise SystemExit(main())
