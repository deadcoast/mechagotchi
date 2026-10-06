"""Detached delivery guard tests; no production outcomes or game imports."""
import ast
from contextlib import closing
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch


class BodyWorkloadDeliveryTests(unittest.TestCase):
    def module(self):
        import verify_body_workload_delivery as m
        return m

    def test_verifier_never_imports_application_or_engine(self):
        m = self.module()
        tree = ast.parse(Path(m.__file__).read_text())
        modules = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import): modules.extend(alias.name for alias in node.names)
            if isinstance(node, ast.ImportFrom): modules.append(node.module or '')
        self.assertFalse(any(name.startswith(('mecha_game', 'mecha_engine', 'labs.')) for name in modules))

    def test_source_binding_requires_exact_frozen_application_hashes(self):
        m = self.module()
        source = {'files': {'game/src/mecha_game/session.py': 'a'*64,
                            'packages/mecha_engine/src/mecha_engine/lifecycle/workload.py': 'b'*64,
                            'labs/unit.py': 'c'*64}}
        runtime = {'source': {'head': 'head', 'files': dict(source['files'])}}
        self.assertEqual(2, m.validate_source_binding(runtime, source, 'head'))
        changed = copy.deepcopy(runtime)
        changed['source']['files']['game/src/mecha_game/session.py'] = 'd'*64
        with self.assertRaises(ValueError): m.validate_source_binding(changed, source, 'head')
        with self.assertRaises(ValueError): m.validate_source_binding(runtime, source, 'other')
        with self.assertRaises(ValueError): m.validate_source_binding(runtime, {'files': {}}, 'head')
        added = copy.deepcopy(runtime)
        added['source']['files']['game/src/mecha_game/late.py'] = 'e'*64
        with self.assertRaises(ValueError): m.validate_source_binding(added, source, 'head')

    def test_restart_and_recovery_identity_use_persisted_lineage_schema(self):
        m = self.module()
        saved = {'chronicle': {'chronicle_format': 'keeper_chronicle_v1', 'keeper_id': 'keeper-one',
                 'identity_origin': 'new_keeper', 'prior_history': 'none', 'campaign_id': None, 'campaign_links': []},
                 'grid': {'grid_id': 'body-a'},
                 'lineage': [{'grid_id': 'body-a', 'life_id': 'keeper-one:life-a'}]}
        restarted = copy.deepcopy(saved)
        restarted['lineage'][-1]['last_session_tick'] = 2
        self.assertEqual('keeper-one:life-a', m.current_life_identity(saved))
        self.assertEqual(m.current_life_identity(saved), m.current_life_identity(restarted))
        restored = copy.deepcopy(restarted)
        restored['lineage'][-1]['last_session_tick'] = 3
        self.assertEqual(m.current_life_identity(saved), m.current_life_identity(restored))
        successor = copy.deepcopy(saved)
        successor['grid']['grid_id'] = 'body-b'
        successor['lineage'].append({'grid_id': 'body-b', 'life_id': 'keeper-one:life-b'})
        self.assertNotEqual(m.current_life_identity(saved), m.current_life_identity(successor))

    def test_current_life_identity_refuses_malformed_or_foreign_lineage(self):
        m = self.module()
        saved = {'chronicle': {'keeper_id': 'keeper-one'}, 'grid': {'grid_id': 'body-a'},
                 'lineage': [{'grid_id': 'body-a', 'life_id': 'keeper-one:life-a'}]}
        for mutate in (lambda p: p.pop('chronicle'),
                       lambda p: p['chronicle'].update(keeper_id=None),
                       lambda p: p['chronicle'].update(keeper_id=' '),
                       lambda p: p.pop('lineage'),
                       lambda p: p.update(lineage=[]),
                       lambda p: p.update(lineage={'life_id': 'keeper-one:life-a'}),
                       lambda p: p.update(lineage=[None]),
                       lambda p: p['lineage'][-1].pop('life_id'),
                       lambda p: p['lineage'][-1].update(life_id=5),
                       lambda p: p['lineage'][-1].update(life_id='keeper-one:life-'),
                       lambda p: p['lineage'][-1].update(life_id='keeper-other:life-a'),
                       lambda p: p['lineage'].append(copy.deepcopy(p['lineage'][-1])),
                       lambda p: p['lineage'][-1].update(grid_id='body-other'),
                       lambda p: p.pop('grid')):
            invalid = copy.deepcopy(saved); mutate(invalid)
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                m.current_life_identity(invalid)

    def test_active_identity_and_projection_are_bound_to_actual_body(self):
        m = self.module()
        payload = {'body_response': 'workload-v1', 'grid': {
            'cells': [{'x': 0, 'y': 0, 'role': 'body', 'material': 'soft', 'damage': .25},
                      {'x': 1, 'y': 0, 'role': 'decoration', 'material': 'soft', 'damage': 0}],
            'organs': {'renamed': {'role': 'body_core', 'cells': [[0, 0], [0, 0]]}}},
            'state': {'body_response': 'workload-v1', 'body_workload': {
                'occupied_mass': 2, 'functional_capacity': .75, 'capacity_floor': 1., 'play_energy_cost': .14}},
            'lineage': [{'body_response': 'workload-v1'}]}
        payload['lineage'][-1]['body_workload'] = copy.deepcopy(payload['state']['body_workload'])
        self.assertEqual(.14, m.validate_active_session(payload)['play_energy_cost'])
        for mutate in (lambda p: p.pop('body_response'),
                       lambda p: p['state'].update(body_response='legacy'),
                       lambda p: p['state']['body_workload'].update(play_energy_cost=.07),
                       lambda p: p['state']['body_workload'].update(capacity_floor=True),
                       lambda p: p['lineage'][-1]['body_workload'].update(play_energy_cost=.07),
                       lambda p: p['grid']['cells'][0].update(damage=float('nan')),
                       lambda p: p['lineage'][-1].update(body_response='legacy')):
            bad = copy.deepcopy(payload); mutate(bad)
            with self.assertRaises(ValueError): m.validate_active_session(bad)

    def test_cold_successor_requires_newborn_no_inherited_learning(self):
        m = self.module()
        child = {'learning_policy': 'qtable', 'state': {'alive': True, 'age_ticks': 0, 'thread_states': {}},
                 'lineage': [{'grid_id': 'p'}, {'grid_id': 'c', 'parent_grid_id': 'p'}],
                 'grid': {'grid_id': 'c', 'parent_grid_id': 'p'}}
        self.assertTrue(m.cold_successor(child, 'p'))
        for mutate in (lambda p: p['state'].update(age_ticks=1),
                       lambda p: p['state']['thread_states'].update(qtable_policy={'q': {}}),
                       lambda p: p['grid'].update(parent_grid_id='other'),
                       lambda p: p.update(learning_policy='incumbent')):
            bad = copy.deepcopy(child); mutate(bad)
            self.assertFalse(m.cold_successor(bad, 'p'))

    def test_bounded_process_timeout_kills_owned_tree_and_retains_logs(self):
        m = self.module()
        # The former .2s cap reserved half for cleanup, leaving under .1s for
        # Python startup. A killed interpreter is not required to have printed.
        # This 2s synthetic fixture changes no production deadline.
        cap = 2.0
        real_popen = subprocess.Popen
        children = []
        def observe_child(*args, **kwargs):
            child = real_popen(*args, **kwargs)
            children.append(child)
            return child
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            started = time.perf_counter()
            with patch.object(m.subprocess, 'Popen', side_effect=observe_child):
                with self.assertRaises(subprocess.TimeoutExpired) as caught:
                    m.run_bounded([sys.executable, '-c', 'import time; time.sleep(30)'],
                                  root, dict(__import__('os').environ), root/'run', cap)
            self.assertTrue(caught.exception.cleanup_confirmed)
            self.assertLessEqual(time.perf_counter()-started, cap+1.0)
            self.assertEqual(1, len(children))
            self.assertIsNotNone(children[0].returncode)
            self.assertIsNotNone(children[0].poll())
            for suffix in ('.stdout.log', '.stderr.log'):
                log = (root/'run').with_suffix(suffix)
                self.assertTrue(log.is_file())
                self.assertIsInstance(log.read_text(), str)

    def test_successful_launcher_and_interpreter_retain_stdout_and_stderr(self):
        m = self.module()
        # Exercise both the repository launcher and the verified current image.
        # Successful logging must be strict across both real process paths.
        executable = sys._base_executable if sys.platform == 'win32' else sys.executable
        self.assertTrue(Path(executable).is_file())
        if sys.platform == 'win32':
            import ctypes
            image = ctypes.create_unicode_buffer(32768)
            self.assertGreater(ctypes.windll.kernel32.GetModuleFileNameW(None, image, len(image)), 0)
            self.assertEqual(Path(image.value).resolve(), Path(executable).resolve())
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name, selected in (('repo-launcher', sys.executable), ('current-image', executable)):
                with self.subTest(executable=selected):
                    code = m.run_bounded([selected, '-B', '-I', '-c',
                        'import sys; print("stdout marker",flush=True); print("stderr marker",file=sys.stderr,flush=True)'],
                        root, dict(__import__('os').environ), root/name, 10.0)
                    self.assertEqual(0, code)
                    self.assertEqual('stdout marker\n', (root/(name+'.stdout.log')).read_text())
                    self.assertEqual('stderr marker\n', (root/(name+'.stderr.log')).read_text())

    def test_owned_tree_transient_completion_uses_one_work_deadline(self):
        m = self.module()
        clock = [4.0]; sleeps = []; counts = iter([2, 1, 0])
        class Tree:
            def reap(self): pass
            def active(self): return next(counts)
        def sleep(delay): sleeps.append(delay); clock[0] += delay
        self.assertTrue(m._drain_owned_tree(Tree(), 4.025, clock=lambda: clock[0], sleeper=sleep))
        self.assertAlmostEqual(4.02, clock[0])
        self.assertAlmostEqual(.02, sum(sleeps))

    def test_persistent_tree_exhausts_work_without_consuming_cleanup_reserve(self):
        m = self.module()
        clock = [4.0]; sleeps = []
        class Tree:
            def reap(self): pass
            def active(self): return 1
        def sleep(delay): sleeps.append(delay); clock[0] += delay
        work_deadline, total_deadline = 4.025, 4.1
        self.assertFalse(m._drain_owned_tree(Tree(), work_deadline, clock=lambda: clock[0], sleeper=sleep))
        self.assertEqual(work_deadline, clock[0])
        self.assertAlmostEqual(.075, total_deadline-clock[0])
        self.assertTrue(all(0 < delay <= .01 for delay in sleeps))

    def test_owned_tree_zero_first_observed_after_work_expiry_refuses(self):
        m = self.module()
        for operation in ('reap', 'active'):
            for observed_at in (4.025, 4.03):
                with self.subTest(operation=operation, observed_at=observed_at):
                    clock = [4.0]
                    class Tree:
                        def reap(self):
                            if operation == 'reap': clock[0] = observed_at
                        def active(self):
                            if operation == 'active': clock[0] = observed_at
                            return 0
                    self.assertFalse(m._drain_owned_tree(Tree(), 4.025,
                        clock=lambda: clock[0], sleeper=lambda _: self.fail('No time remains to sleep')))
        class ExpiredTree:
            def reap(self): raise AssertionError('Expired work must not obtain a new completion observation')
        self.assertFalse(m._drain_owned_tree(ExpiredTree(), 4., clock=lambda: 4., sleeper=lambda _: None))

    def test_owned_tree_query_uncertainty_never_passes(self):
        m = self.module()
        for operation in ('reap', 'active'):
            with self.subTest(operation=operation):
                class Tree:
                    def reap(self):
                        if operation == 'reap': raise OSError('unknown process state')
                    def active(self):
                        if operation == 'active': raise OSError('unknown process state')
                        return 0
                with self.assertRaises(OSError):
                    m._drain_owned_tree(Tree(), 4.1, clock=lambda: 4., sleeper=lambda _: None)
        for invalid in (None, True, -1):
            class Tree:
                def reap(self): pass
                def active(self): return invalid
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                m._drain_owned_tree(Tree(), 4.1, clock=lambda: 4., sleeper=lambda _: None)

    def test_delivery_format_records_prospective_owned_tree_semantics(self):
        self.assertEqual('mechagotchi_body_workload_delivery_v2', self.module().FORMAT)

    def test_short_lived_owned_descendant_completes_and_retains_logs(self):
        m = self.module()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            command = [sys.executable, '-B', '-I', '-c',
                'import subprocess,sys; print("parent completed",flush=True); subprocess.Popen([sys.executable,"-B","-I","-c",'
                '\'import time,sys;time.sleep(.1);print("child completed",flush=True);print("child stderr",file=sys.stderr,flush=True)\']);'
                '']
            code = m.run_bounded(command, root, dict(__import__('os').environ), root/'short', 10.)
            self.assertEqual(0, code)
            self.assertEqual(['parent completed', 'child completed'], (root/'short.stdout.log').read_text().splitlines())
            self.assertEqual('child stderr\n', (root/'short.stderr.log').read_text())

    def test_finished_parent_cannot_leave_descendant_running(self):
        m = self.module()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            command = [sys.executable, '-c', 'import subprocess,sys; p=subprocess.Popen([sys.executable,"-c","import time; time.sleep(30)"]); print(p.pid,flush=True)']
            with self.assertRaisesRegex(RuntimeError, 'descendant') as caught:
                m.run_bounded(command, root, dict(__import__('os').environ), root/'orphan', 3)
            self.assertTrue(caught.exception.cleanup_confirmed)

    def test_missing_receipt_fails_success_but_allows_explicit_parser_refusal(self):
        m = self.module()
        with self.assertRaises(ValueError): m.require_launch_receipt(None, 0)
        with self.assertRaises(ValueError): m.require_launch_receipt(None, 2)
        m.require_launch_receipt(None, 2, allow_parser_refusal=True)
        with self.assertRaises(ValueError): m.require_launch_receipt(None, 0, allow_parser_refusal=True)
        m.require_launch_receipt({'stopped': True, 'exit_code': 0}, 0)
        with self.assertRaises(ValueError): m.require_launch_receipt({'stopped': False, 'exit_code': 0}, 0)

    def test_era_evidence_requires_active_hash_bound_input_blob(self):
        m = self.module()
        import sqlite3
        with tempfile.TemporaryDirectory() as folder:
            ledger = Path(folder)/'campaign.sqlite3'
            blob = json.dumps({'format': 'body_response_inputs_v1', 'body_response': 'workload-v1'}).encode()
            digest = hashlib.sha256(blob).hexdigest()
            report = {'body_response': 'workload-v1', 'generations': []}
            canonical = lambda x: json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()
            manifest = {'campaign_id': 'fixture', 'era_index': 0, 'inputs': {'body_response_inputs_sha256': digest},
                        'report_sha256': hashlib.sha256(canonical(report)).hexdigest()}
            with closing(sqlite3.connect(ledger)) as conn, conn:
                conn.executescript('CREATE TABLE era_executions(campaign_id,era_index,manifest_json,manifest_sha256); CREATE TABLE execution_blobs(sha256,media_type,payload); CREATE TABLE eras(campaign_id,era_index,report_json);')
                conn.execute('INSERT INTO era_executions VALUES(?,?,?,?)', ('fixture',0,json.dumps(manifest),hashlib.sha256(canonical(manifest)).hexdigest()))
                conn.execute('INSERT INTO execution_blobs VALUES(?,?,?)', (digest,'application/json',blob))
                conn.execute('INSERT INTO eras VALUES(?,?,?)', ('fixture',0,json.dumps(report)))
            before = ledger.read_bytes()
            evidence = m.read_active_era(ledger, 'fixture', 0)
            self.assertEqual(report, evidence['report'])
            self.assertEqual(before, ledger.read_bytes())
            with closing(sqlite3.connect(ledger)) as conn, conn:
                conn.execute('UPDATE execution_blobs SET payload=?', (b'{}',))
            with self.assertRaises(ValueError): m.read_active_era(ledger, 'fixture', 0)


if __name__ == '__main__': unittest.main()
