"""X5 storage acceptance over synthetic records; no engine or game imports."""

import base64
import copy
import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import mecha_engine.storage as package_store
import mecha_engine.storage.store as package_impl


def digest(value):
    return hashlib.sha256(package_store.canonical_json(value).encode('utf-8')).hexdigest()


def fixture():
    campaign = dict(campaign_id='execution_test', keeper_label='keeper',
                    created_date='2026-10-06', predecessor_campaign_id=None, status='active')
    profile = {'profile_id': 'fixture', 'slip_version': '0.1.0'}
    grids = [{'grid_id': 'duplicate', 'cells': [{'x': index}]} for index in range(2)]
    report = {'decision': {'status': 'fixture'}, 'summary': {
        'archive': {'filled_niches': 1, 'coverage': 0.1, 'qd_score': 0.5},
        'max_lineage_generation': 0}, 'founders': {'admitted_ids': ['duplicate'],
        'rejected': [{'grid_id': 'duplicate', 'errors': ['actual rejection']}]}}
    elite = dict(niche_key='n0', grid_id='duplicate', grid=grids[0], fitness=0.5)
    era = dict(era_index=0, rng_seed=19, weather=None, report=report,
               elites=[elite], went_extinct=False)
    blobs = {}

    def blob(value, raw=False):
        data = value if raw else json.dumps(value, separators=(',', ':')).encode('utf-8')
        sha = hashlib.sha256(data).hexdigest()
        blobs[sha] = dict(media_type='application/octet-stream' if raw else 'application/json',
                          data_base64=base64.b64encode(data).decode('ascii'))
        return sha

    refs = [blob(grid) for grid in grids]
    manifest = dict(format='mechagotchi_era_execution_v1', campaign_id=campaign['campaign_id'],
        era_index=0, rng_seed=19, execution_contract=dict(name='mechagotchi_evolve_v1',
            runtime={'implementation': 'fixture'}, policies={}), effective_config={'ticks': 3},
        inputs=dict(seed_corpus_sha256=blob(grids), covenant_sha256=blob(profile),
            generation_model_sha256=blob(None), repair_model_sha256=blob({'weights': {'z': 1, 'a': 2}}),
            readability_model_sha256=blob(None), readability_selection_sha256=blob(None),
            founder_mode='list', founder_sha256=refs, weather_mode='none', ordered_weather_sha256=None),
        sources=[dict(role='founder', source_position=0, source_kind='workshop_release',
                      label='releases/source.json', raw_sha256=blob(b'{ "source": 1 }\n', raw=True))],
        founder_occurrences=[dict(ordinal=i, grid_id='duplicate', grid_sha256=ref,
            source_kind='workshop_release', source_position=i, admitted=(i == 0),
            rejection_errors=None if i == 0 else ['actual rejection']) for i, ref in enumerate(refs)],
        calibration_sha256=blob({'descriptor': ['actual', 'ordered']}),
        report_sha256=digest(report), elites_sha256=digest(era['elites']))
    return campaign, profile, era, dict(manifest=manifest, blobs=blobs)


OLD_TABLES = ('campaigns', 'slip_profiles', 'eras', 'elites', 'founders', 'unlocks', 'replays')
NEW_TABLES = ('execution_blobs', 'era_executions', 'founder_occurrences')


def dump(conn, tables=OLD_TABLES):
    return {table: conn.execute(f'SELECT * FROM {table} ORDER BY rowid').fetchall() for table in tables}


class StorageExecutionTests(unittest.TestCase):
    store = package_store
    impl = package_impl

    def setUp(self):
        self.campaign, self.profile, self.era, self.bundle = fixture()
        self.conn = self.store.open_ledger(':memory:')
        self.addCleanup(self.conn.close)
        self.store.record_campaign(self.conn, self.campaign)

    def record(self, bundle=None):
        self.store.record_era(self.conn, self.campaign['campaign_id'], self.era,
                              self.profile, execution=self.bundle if bundle is None else bundle)

    def load(self):
        return self.store.load_era_execution(self.conn, self.campaign['campaign_id'], 0)

    def test_public_version_and_pure_validation(self):
        self.assertEqual(2, self.store.SCHEMA_VERSION)
        self.assertEqual((1, 2), self.store.SUPPORTED_READ_SCHEMA_VERSIONS)
        before = copy.deepcopy(self.bundle)
        with patch.object(Path, 'open', side_effect=AssertionError('unexpected file I/O')):
            self.assertIsNone(self.store.validate_execution(self.bundle))
        self.assertEqual(before, self.bundle)

    def test_restart_exact_bytes_duplicate_occurrences_and_independent_copies(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'ledger.sqlite'
            conn = self.store.open_ledger(path)
            self.store.record_campaign(conn, self.campaign)
            self.store.record_era(conn, self.campaign['campaign_id'], self.era, self.profile, execution=self.bundle)
            conn.close()
            conn = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)
            try:
                loaded = self.store.load_era_execution(conn, self.campaign['campaign_id'], 0)
                self.assertEqual(self.bundle, loaded)
                self.assertEqual(2, conn.execute('SELECT count(*) FROM founder_occurrences').fetchone()[0])
                for sha, record in self.bundle['blobs'].items():
                    self.assertEqual(base64.b64decode(record['data_base64']), conn.execute(
                        'SELECT payload FROM execution_blobs WHERE sha256=?', (sha,)).fetchone()[0])
                loaded['manifest']['founder_occurrences'][0]['admitted'] = False
                self.assertEqual(self.bundle, self.store.load_era_execution(conn, self.campaign['campaign_id'], 0))
            finally:
                conn.close()

    def test_old_api_shapes_and_missing_evidence_remain_unchanged(self):
        self.store.record_era(self.conn, self.campaign['campaign_id'], self.era, self.profile)
        self.assertIsNone(self.load())
        self.assertIsNone(self.store.load_era_execution(self.conn, 'missing', 0))
        history = self.store.campaign_history(self.conn, self.campaign['campaign_id'])
        self.assertNotIn('execution', history['eras'][0])
        self.assertEqual(self.era['elites'], self.store.load_era_elites(self.conn, self.campaign['campaign_id'], 0))

    def test_none_and_empty_lists_remain_distinct(self):
        for founder_mode in ('none', 'list'):
            for weather_mode in ('none', 'list'):
                with self.subTest(founder_mode=founder_mode, weather_mode=weather_mode):
                    bundle = copy.deepcopy(self.bundle)
                    inputs = bundle['manifest']['inputs']
                    inputs.update(founder_mode=founder_mode, founder_sha256=[], weather_mode=weather_mode)
                    bundle['manifest']['founder_occurrences'] = []
                    if weather_mode == 'list':
                        sha = hashlib.sha256(b'[]').hexdigest()
                        bundle['blobs'][sha] = dict(media_type='application/json', data_base64='W10=')
                        inputs['ordered_weather_sha256'] = sha
                    refs = {bundle['manifest']['calibration_sha256'],
                            *[value for key, value in inputs.items()
                              if key.endswith('_sha256') and key != 'founder_sha256' and value is not None],
                            *[item['raw_sha256'] for item in bundle['manifest']['sources']]}
                    bundle['blobs'] = {sha: blob for sha, blob in bundle['blobs'].items() if sha in refs}
                    self.store.validate_execution(bundle)

    def test_structural_hash_reference_and_ordinal_corruption_refuses(self):
        changes = [
            lambda b: b['manifest'].update(format='future'),
            lambda b: b['manifest'].update(era_index=True),
            lambda b: b['manifest'].update(rng_seed=True),
            lambda b: b['manifest'].update(effective_config=[]),
            lambda b: b['manifest'].update(execution_contract='unstructured'),
            lambda b: b['manifest'].update(report_sha256='bad'),
            lambda b: b['manifest'].update(calibration_sha256='0' * 64),
            lambda b: b['manifest']['inputs'].update(covenant_sha256='0' * 64),
            lambda b: b['manifest']['inputs'].update(founder_mode='none'),
            lambda b: b['manifest']['inputs'].update(founder_sha256=list(reversed(b['manifest']['inputs']['founder_sha256']))),
            lambda b: b['manifest']['inputs'].update(weather_mode='list'),
            lambda b: b['manifest']['founder_occurrences'][1].update(ordinal=0),
            lambda b: b['manifest']['founder_occurrences'][1].update(grid_id='different'),
            lambda b: b['manifest']['founder_occurrences'][0].update(admitted=1),
            lambda b: b['manifest']['founder_occurrences'][0].update(rejection_errors=['invented']),
            lambda b: b['manifest']['sources'][0].update(raw_sha256='0' * 64),
            lambda b: b['manifest']['sources'][0].update(label='C:/absolute.json'),
            lambda b: b['blobs'][next(iter(b['blobs']))].update(data_base64='not base64'),
            lambda b: b['blobs'][next(iter(b['blobs']))].update(data_base64='e30='),
        ]
        for index, change in enumerate(changes):
            with self.subTest(index=index):
                bundle = copy.deepcopy(self.bundle)
                change(bundle)
                with self.assertRaises(ValueError):
                    self.store.validate_execution(bundle)

    def test_writer_binds_identity_covenant_report_and_complete_elites(self):
        changes = [lambda b: b['manifest'].update(campaign_id='wrong'),
                   lambda b: b['manifest'].update(era_index=1),
                   lambda b: b['manifest'].update(rng_seed=20),
                   lambda b: b['manifest'].update(report_sha256='0' * 64),
                   lambda b: b['manifest'].update(elites_sha256='0' * 64),
                   lambda b: b['manifest']['inputs'].update(covenant_sha256=b['manifest']['inputs']['repair_model_sha256'])]
        before = dump(self.conn, OLD_TABLES + NEW_TABLES)
        for index, change in enumerate(changes):
            with self.subTest(index=index):
                bundle = copy.deepcopy(self.bundle)
                change(bundle)
                with self.assertRaises(ValueError):
                    self.record(bundle)
                self.assertEqual(before, dump(self.conn, OLD_TABLES + NEW_TABLES))

    def test_conflicting_blob_media_or_bytes_rolls_back_all_era_rows(self):
        sha, blob = next(iter(self.bundle['blobs'].items()))
        for media, payload in [('wrong', base64.b64decode(blob['data_base64'])),
                               (blob['media_type'], b'conflict')]:
            with self.subTest(media=media):
                self.conn.execute('INSERT INTO execution_blobs VALUES (?, ?, ?)', (sha, media, payload))
                self.conn.commit()
                before = dump(self.conn, OLD_TABLES + NEW_TABLES)
                with self.assertRaises(ValueError):
                    self.record()
                self.assertEqual(before, dump(self.conn, OLD_TABLES + NEW_TABLES))
                self.conn.execute('DELETE FROM execution_blobs')
                self.conn.commit()

    def test_late_sql_failure_rolls_back_execution_and_all_era_rows(self):
        self.conn.execute("CREATE TRIGGER refuse_occurrence BEFORE INSERT ON founder_occurrences BEGIN SELECT RAISE(ABORT, 'injected occurrence failure'); END")
        before = dump(self.conn, OLD_TABLES + NEW_TABLES)
        with self.assertRaises(sqlite3.IntegrityError):
            self.record()
        self.assertEqual(before, dump(self.conn, OLD_TABLES + NEW_TABLES))

    def test_execution_is_immutable_and_blob_deduplication_is_exact(self):
        self.record()
        before = dump(self.conn, OLD_TABLES + NEW_TABLES)
        with self.assertRaises(sqlite3.IntegrityError):
            self.record()
        self.assertEqual(before, dump(self.conn, OLD_TABLES + NEW_TABLES))
        other = copy.deepcopy(self.bundle)
        other['manifest']['era_index'] = 1
        self.store.record_era(self.conn, self.campaign['campaign_id'], {**self.era, 'era_index': 1}, self.profile, execution=other)
        self.assertEqual(len(self.bundle['blobs']), self.conn.execute('SELECT count(*) FROM execution_blobs').fetchone()[0])

    def test_read_verifies_manifest_projection_blobs_and_bound_results(self):
        changes = ["UPDATE era_executions SET manifest_sha256='bad'",
                   "UPDATE execution_blobs SET payload=X'00'",
                   "DELETE FROM execution_blobs",
                   "UPDATE founder_occurrences SET occurrence_json='{}'",
                   "DELETE FROM founder_occurrences",
                   "UPDATE eras SET report_json='{}'",
                   "UPDATE slip_profiles SET profile_json='{}'",
                   "UPDATE elites SET elite_json='{}'"]
        self.record()
        for sql in changes:
            with self.subTest(sql=sql):
                self.conn.execute('SAVEPOINT corruption')
                self.conn.execute(sql)
                with self.assertRaises(ValueError):
                    self.load()
                self.conn.execute('ROLLBACK TO corruption')
                self.conn.execute('RELEASE corruption')

    def test_admissions_bind_to_report_on_write_and_verified_read(self):
        before = dump(self.conn, OLD_TABLES + NEW_TABLES)
        changes = [lambda b: b['manifest']['founder_occurrences'][0].update(
                        admitted=False, rejection_errors=['contradictory review probe']),
                   lambda b: b['manifest']['founder_occurrences'][1].update(
                        rejection_errors=['different rejection'])]
        for index, change in enumerate(changes):
            with self.subTest(index=index):
                bundle = copy.deepcopy(self.bundle)
                change(bundle)
                with self.assertRaisesRegex(ValueError, 'founder|admission'):
                    self.record(bundle)
                self.assertEqual(before, dump(self.conn, OLD_TABLES + NEW_TABLES))
        self.record()
        for index, change in enumerate(changes):
            with self.subTest(read_index=index):
                self.conn.execute('SAVEPOINT contradictory_projection')
                bundle = copy.deepcopy(self.bundle)
                change(bundle)
                manifest = bundle['manifest']
                self.conn.execute('UPDATE era_executions SET manifest_json=?, manifest_sha256=?',
                                  (self.store.canonical_json(manifest), digest(manifest)))
                for item in manifest['founder_occurrences']:
                    self.conn.execute('UPDATE founder_occurrences SET occurrence_json=? WHERE ordinal=?',
                                      (self.store.canonical_json(item), item['ordinal']))
                with self.assertRaisesRegex(ValueError, 'founder|admission'):
                    self.load()
                self.conn.execute('ROLLBACK TO contradictory_projection')
                self.conn.execute('RELEASE contradictory_projection')

    def test_founder_none_and_empty_list_bind_report_presence(self):
        for mode in ('none', 'list'):
            for report_present in (False, True):
                with self.subTest(mode=mode, report_present=report_present):
                    bundle, era = copy.deepcopy(self.bundle), copy.deepcopy(self.era)
                    manifest = bundle['manifest']
                    manifest['inputs'].update(founder_mode=mode, founder_sha256=[])
                    manifest['founder_occurrences'] = []
                    manifest['sources'] = []
                    refs = {manifest['calibration_sha256'], *[value for key, value in manifest['inputs'].items()
                            if key.endswith('_sha256') and key != 'founder_sha256' and value is not None]}
                    bundle['blobs'] = {sha: item for sha, item in bundle['blobs'].items() if sha in refs}
                    if report_present:
                        era['report']['founders'] = dict(admitted_ids=[], rejected=[])
                    else:
                        del era['report']['founders']
                    manifest['report_sha256'] = digest(era['report'])
                    conn = self.store.open_ledger(':memory:')
                    try:
                        self.store.record_campaign(conn, self.campaign)
                        if (mode == 'list') == report_present:
                            self.store.record_era(conn, self.campaign['campaign_id'], era, self.profile, execution=bundle)
                            self.assertEqual(bundle, self.store.load_era_execution(conn, self.campaign['campaign_id'], 0))
                        else:
                            with self.assertRaisesRegex(ValueError, 'founder|admission'):
                                self.store.record_era(conn, self.campaign['campaign_id'], era, self.profile, execution=bundle)
                    finally:
                        conn.close()

    def test_admission_sequences_keep_order_and_verbatim_duplicate_rejections(self):
        for index, item in enumerate(self.bundle['manifest']['founder_occurrences']):
            item.update(admitted=False, rejection_errors=[f'rejection {index}'])
        self.era['report']['founders'] = dict(admitted_ids=[], rejected=[
            dict(grid_id='duplicate', errors=[f'rejection {index}']) for index in range(2)])
        self.bundle['manifest']['report_sha256'] = digest(self.era['report'])
        self.record()
        self.assertEqual(self.bundle, self.load())
        self.era['era_index'] = 1
        self.bundle['manifest']['era_index'] = 1
        self.era['report']['founders']['rejected'].reverse()
        self.bundle['manifest']['report_sha256'] = digest(self.era['report'])
        with self.assertRaisesRegex(ValueError, 'founder|admission'):
            self.record()

    def add_ordered_elites(self, elites):
        payload = json.dumps(elites, separators=(',', ':')).encode('utf-8')
        sha = hashlib.sha256(payload).hexdigest()
        self.bundle['manifest']['ordered_elites_sha256'] = sha
        self.bundle['blobs'][sha] = dict(media_type='application/json', data_base64=base64.b64encode(payload).decode('ascii'))
        return sha, payload

    def test_ordered_elite_output_bytes_survive_canonical_legacy_rows(self):
        sha, payload = self.add_ordered_elites(self.era['elites'])
        self.record()
        loaded = self.load()
        self.assertEqual(self.bundle, loaded)
        self.assertEqual(payload, base64.b64decode(loaded['blobs'][sha]['data_base64']))
        self.assertEqual(list(self.era['elites'][0]), list(json.loads(payload)[0]))
        self.assertNotEqual(list(self.era['elites'][0]), list(self.store.load_era_elites(self.conn, self.campaign['campaign_id'], 0)[0]))

    def test_optional_ordered_elites_reference_and_result_binding_refuse_tampering(self):
        sha, _ = self.add_ordered_elites(self.era['elites'])
        self.store.validate_execution(self.bundle)
        bundle = copy.deepcopy(self.bundle)
        bundle['manifest']['ordered_elites_sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            self.store.validate_execution(bundle)
        bundle = copy.deepcopy(self.bundle)
        other = [{**self.era['elites'][0], 'fitness': 0.9}]
        payload = json.dumps(other, separators=(',', ':')).encode('utf-8')
        new_sha = hashlib.sha256(payload).hexdigest()
        del bundle['blobs'][sha]
        bundle['manifest']['ordered_elites_sha256'] = new_sha
        bundle['blobs'][new_sha] = dict(media_type='application/json', data_base64=base64.b64encode(payload).decode('ascii'))
        self.store.validate_execution(bundle)
        with self.assertRaisesRegex(ValueError, 'elite'):
            self.record(bundle)

    def replace_json_blob(self, bundle, old_sha, value):
        payload = json.dumps(value, separators=(',', ':')).encode('utf-8')
        sha = hashlib.sha256(payload).hexdigest()
        del bundle['blobs'][old_sha]
        bundle['blobs'][sha] = dict(media_type='application/json', data_base64=base64.b64encode(payload).decode('ascii'))
        return sha, payload

    def test_ordered_elite_json_types_bound_on_write_and_verified_read(self):
        original_sha, _ = self.add_ordered_elites(self.era['elites'])
        before = dump(self.conn, OLD_TABLES + NEW_TABLES)
        for value in (False, 0.0):
            with self.subTest(writer_type=type(value).__name__):
                bundle = copy.deepcopy(self.bundle)
                typed = copy.deepcopy(self.era['elites'])
                typed[0]['grid']['cells'][0]['x'] = value
                sha, _ = self.replace_json_blob(bundle, original_sha, typed)
                bundle['manifest']['ordered_elites_sha256'] = sha
                with self.assertRaisesRegex(ValueError, 'elite'):
                    self.record(bundle)
                self.assertEqual(before, dump(self.conn, OLD_TABLES + NEW_TABLES))
        self.record()
        for value in (False, 0.0):
            with self.subTest(reader_type=type(value).__name__):
                self.conn.execute('SAVEPOINT typed_output')
                bundle = copy.deepcopy(self.bundle)
                typed = copy.deepcopy(self.era['elites'])
                typed[0]['grid']['cells'][0]['x'] = value
                sha, payload = self.replace_json_blob(bundle, original_sha, typed)
                bundle['manifest']['ordered_elites_sha256'] = sha
                self.conn.execute('INSERT INTO execution_blobs VALUES (?, ?, ?)', (sha, 'application/json', payload))
                self.conn.execute('UPDATE era_executions SET manifest_json=?, manifest_sha256=?',
                    (self.store.canonical_json(bundle['manifest']), digest(bundle['manifest'])))
                with self.assertRaisesRegex(ValueError, 'elite'):
                    self.load()
                self.conn.execute('ROLLBACK TO typed_output')
                self.conn.execute('RELEASE typed_output')

    def test_covenant_json_types_bound_on_write_and_verified_read(self):
        self.profile['numeric_fixture'] = 0
        old_sha = self.bundle['manifest']['inputs']['covenant_sha256']
        original_sha, _ = self.replace_json_blob(self.bundle, old_sha, self.profile)
        self.bundle['manifest']['inputs']['covenant_sha256'] = original_sha
        before = dump(self.conn, OLD_TABLES + NEW_TABLES)
        for value in (False, 0.0):
            with self.subTest(writer_type=type(value).__name__):
                bundle = copy.deepcopy(self.bundle)
                sha, _ = self.replace_json_blob(bundle, original_sha, {**self.profile, 'numeric_fixture': value})
                bundle['manifest']['inputs']['covenant_sha256'] = sha
                with self.assertRaisesRegex(ValueError, 'covenant'):
                    self.record(bundle)
                self.assertEqual(before, dump(self.conn, OLD_TABLES + NEW_TABLES))
        self.record()
        for value in (False, 0.0):
            with self.subTest(reader_type=type(value).__name__):
                self.conn.execute('SAVEPOINT typed_covenant')
                bundle = copy.deepcopy(self.bundle)
                sha, payload = self.replace_json_blob(bundle, original_sha, {**self.profile, 'numeric_fixture': value})
                bundle['manifest']['inputs']['covenant_sha256'] = sha
                self.conn.execute('INSERT INTO execution_blobs VALUES (?, ?, ?)', (sha, 'application/json', payload))
                self.conn.execute('UPDATE era_executions SET manifest_json=?, manifest_sha256=?',
                    (self.store.canonical_json(bundle['manifest']), digest(bundle['manifest'])))
                with self.assertRaisesRegex(ValueError, 'covenant'):
                    self.load()
                self.conn.execute('ROLLBACK TO typed_covenant')
                self.conn.execute('RELEASE typed_covenant')

    def typed_rejected_founder(self, bundle, grid_id):
        occurrence = bundle['manifest']['founder_occurrences'][0]
        old_sha = occurrence['grid_sha256']
        genome = json.loads(base64.b64decode(bundle['blobs'][old_sha]['data_base64']))
        genome['grid_id'] = grid_id
        sha, _ = self.replace_json_blob(bundle, old_sha, genome)
        bundle['manifest']['inputs']['founder_sha256'][0] = sha
        occurrence.update(grid_sha256=sha, grid_id=grid_id, admitted=False, rejection_errors=['invalid identity'])

    def test_rejected_founder_grid_identity_preserves_json_types(self):
        for value in (False, 0.0):
            with self.subTest(type=type(value).__name__):
                bundle = copy.deepcopy(self.bundle)
                self.typed_rejected_founder(bundle, 0)
                bundle['manifest']['founder_occurrences'][0]['grid_id'] = value
                with self.assertRaisesRegex(ValueError, 'identity'):
                    self.store.validate_execution(bundle)

    def test_report_admission_grid_identity_preserves_json_types(self):
        self.typed_rejected_founder(self.bundle, 0)
        original_report = copy.deepcopy(self.era['report'])
        original_report['founders'] = dict(admitted_ids=[], rejected=[
            dict(grid_id=0, errors=['invalid identity']), dict(grid_id='duplicate', errors=['actual rejection'])])
        before = dump(self.conn, OLD_TABLES + NEW_TABLES)
        for value in (False, 0.0):
            with self.subTest(type=type(value).__name__):
                self.era['report'] = copy.deepcopy(original_report)
                self.era['report']['founders']['rejected'][0]['grid_id'] = value
                self.bundle['manifest']['report_sha256'] = digest(self.era['report'])
                with self.assertRaisesRegex(ValueError, 'admission'):
                    self.record()
                self.assertEqual(before, dump(self.conn, OLD_TABLES + NEW_TABLES))

    def make_v1(self, path):
        conn = sqlite3.connect(path)
        conn.executescript(self.impl.SCHEMA)
        conn.execute('PRAGMA user_version = 1')
        self.store.record_campaign(conn, self.campaign)
        self.store.record_era(conn, self.campaign['campaign_id'], self.era, self.profile)
        self.store.record_replay(conn, self.campaign['campaign_id'], 0, 'original.json', 'a' * 64)
        conn.execute('UPDATE slip_profiles SET profile_json=?', ('{ "slip_version": "0.1.0", "profile_id": "fixture" }\n',))
        conn.commit()
        return conn

    def test_populated_v1_migration_preserves_every_old_row_and_text_byte(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'legacy.sqlite'
            conn = self.make_v1(path)
            before = dump(conn)
            conn.close()
            raw_before = path.read_bytes()
            conn = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)
            self.assertIsNone(self.store.load_era_execution(conn, self.campaign['campaign_id'], 0))
            conn.close()
            self.assertEqual(raw_before, path.read_bytes())
            conn = self.store.open_ledger(path)
            try:
                self.assertEqual(2, conn.execute('PRAGMA user_version').fetchone()[0])
                self.assertEqual(before, dump(conn))
                self.assertIsNone(self.store.load_era_execution(conn, self.campaign['campaign_id'], 0))
            finally:
                conn.close()

    def test_migration_failure_rolls_back_all_ddl_and_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'legacy.sqlite'
            conn = self.make_v1(path)
            before = dump(conn)
            conn.close()
            original_connect = sqlite3.connect

            def connected(*args, **kwargs):
                value = original_connect(*args, **kwargs)
                value.set_authorizer(lambda operation, arg1, *rest:
                    sqlite3.SQLITE_DENY if operation == sqlite3.SQLITE_CREATE_TABLE and arg1 == 'era_executions'
                    else sqlite3.SQLITE_OK)
                return value

            with patch.object(self.impl.sqlite3, 'connect', side_effect=connected):
                with self.assertRaises(sqlite3.DatabaseError):
                    self.store.open_ledger(path)
            conn = original_connect(path)
            try:
                self.assertEqual(1, conn.execute('PRAGMA user_version').fetchone()[0])
                self.assertEqual(before, dump(conn))
                self.assertEqual(set(OLD_TABLES), {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")})
            finally:
                conn.close()

    def test_future_read_schema_refuses(self):
        self.conn.execute('PRAGMA user_version = 99')
        with self.assertRaises(ValueError):
            self.load()


if __name__ == '__main__':
    unittest.main()
