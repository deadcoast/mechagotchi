"""X2 contract: full semantic documents and revision-bound authoring operations."""
import base64
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'workshop' / 'server'))
from workshop_server import (
    _build_grid, _apply_cell_overrides, start_workshop_server,
    render_packet_v2, clip_frame_count, validate_grid,
)

MATRIX = [list(row) for row in (
    '.E..E...', '..BB....', '.BABB...', '..BB.M..', '...BB...',
    '........', '........', '........',
)]
FORMAT = 'mecha_workshop_document_v1'


def rich_document():
    grid = _build_grid(MATRIX, 'lcd_green', 'x2_rich_original')
    _apply_cell_overrides(grid, {'1,0': {'role': 'antenna', 'mutation_weight': .91}})
    grid['parent_grid_id'] = 'actual_parent'
    grid['lineage'] = {'generation': 4, 'ancestor_ids': ['actual_parent'],
                       'mutation_events': ['recorded_origin']}
    grid['metadata'] = {'source': 'retained_creator', 'note': 'do not reconstruct'}
    grid['cells'][0]['locked'] = True
    grid['organs']['core']['mutation_weight'] = .73
    profile = json.loads((ROOT / 'data/slips/valid/slip_v2_cleanliness.json').read_text())
    profile['profile_id'] = 'x2_authored_cleanliness'
    layers = [{'name': name, 'matrix': deepcopy(MATRIX) if name == 'body' else
               [['.'] * 8 for _ in range(8)]}
              for name in ('body', 'organs', 'decoration', 'effects')]
    layers[0]['matrix'][0][1] = 'N'
    return {'format': FORMAT, 'grid': grid, 'profile': profile, 'layers': layers}


class AuthoringFidelityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.server = start_workshop_server(port=0, grids_dir=cls.root/'grids',
            slips_dir=cls.root/'slips', released_dir=cls.root/'released',
            metrics_dir=cls.root/'metrics', session_dir=cls.root/'keeper')
        cls.base = f'http://127.0.0.1:{cls.server.server_address[1]}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.temp.cleanup()

    def request(self, path, payload=None, raw=None, revision=None):
        data = raw if raw is not None else (json.dumps(payload).encode() if payload is not None else None)
        req = urllib.request.Request(self.base+path, data=data,
            headers={'Content-Type': 'application/json' if raw is None else 'application/octet-stream',
                     **({'X-Workshop-Draft-Revision': str(revision)} if revision is not None else {})})
        try:
            response = urllib.request.urlopen(req, timeout=20)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            body = response.read()
            headers = response.headers
            if 'application/json' in headers.get('Content-Type', ''):
                body = json.loads(body)
            return response.code, body, headers

    def post(self, path, payload):
        return self.request(path, payload)[:2]

    def save(self, name, document, **kw):
        return self.post('/api/save', {'name': name, 'document': document,
            'draft_revision': 7, 'expected_disk_revision': None, **kw})

    def test_rich_load_and_untouched_resave_preserve_every_field(self):
        document = rich_document()
        folder = self.root/'grids'
        folder.mkdir(exist_ok=True)
        target = folder/'loaded_rich.json'
        target.write_text(json.dumps(document['grid']))
        status, loaded, _ = self.request('/api/grids/loaded_rich')
        self.assertEqual(200, status)
        self.assertEqual(document['grid'], loaded.get('document', {}).get('grid'))
        status, saved = self.save('loaded_rich', loaded['document'], expected_disk_revision=loaded['disk_revision'])
        self.assertEqual(200, status, saved)
        self.assertEqual(document['grid'], json.loads(target.read_text()))
        self.assertNotEqual(loaded['disk_revision'], saved['disk_revision'])

    def test_rich_antenna_token_is_accepted_by_legacy_matrix_gate(self):
        matrix = deepcopy(MATRIX)
        matrix[0][1] = 'N'
        status, result = self.post('/api/validate', {'matrix': matrix, 'palette_id': 'lcd_green'})
        self.assertEqual(200, status, result)
        self.assertTrue(result['valid'])

    def test_catalogs_exclude_sidecars_and_non_creatures(self):
        self.post('/api/save', {'name': 'catalogued', 'matrix': MATRIX, 'palette_id': 'lcd_green'})
        folder = self.root/'grids'
        (folder/'catalogued.layers.json').write_text(json.dumps({'layers': []}))
        (folder/'not_a_creature.json').write_text(json.dumps({'unrelated': True}))
        for endpoint, key in (('/api/grids', 'grids'), ('/api/preview/creatures', 'creatures')):
            status, body, _ = self.request(endpoint)
            self.assertEqual(200, status)
            names = [row['name'] for row in body[key]]
            self.assertIn('catalogued', names)
            self.assertNotIn('catalogued.layers', names)
            self.assertNotIn('not_a_creature', names)

    def test_validation_echoes_exact_document_and_revision_even_when_invalid(self):
        document = rich_document()
        for cell in document['grid']['cells']:
            cell['animation_anchor'] = False
        document.pop('layers')
        status, body = self.post('/api/validate', {'document': document, 'draft_revision': 18})
        self.assertEqual(200, status, body)
        self.assertFalse(body['valid'])
        self.assertEqual(document, body['document'])
        self.assertEqual(18, body['draft_revision'])
        self.assertEqual(64, len(body['document_digest']))
        self.assertEqual(validate_grid(document['grid']).errors, body['errors'])

    def test_save_preserves_document_profile_layers_and_conflicts_without_writing(self):
        document = rich_document()
        status, first = self.save('saved_document', document)
        self.assertEqual(200, status, first)
        status, loaded, _ = self.request('/api/grids/saved_document')
        self.assertEqual(document, loaded['document'])
        before = {p.name: p.read_bytes() for p in (self.root/'grids').glob('saved_document*')}
        changed = deepcopy(document)
        changed['grid']['cells'][0]['mutation_weight'] = .25
        status, conflict = self.save('saved_document', changed)
        self.assertEqual(409, status, conflict)
        self.assertEqual(first['disk_revision'], conflict['current_revision'])
        self.assertEqual(before, {p.name: p.read_bytes() for p in (self.root/'grids').glob('saved_document*')})
        status, second = self.save('saved_document', changed, expected_disk_revision=first['disk_revision'])
        self.assertEqual(200, status, second)
        self.assertIsNotNone(second['backup'])
        self.assertEqual(document['grid'], json.loads((self.root/'grids'/second['backup']).read_text()))

    def test_sidecar_changes_are_part_of_disk_conflict_identity(self):
        status, saved = self.save('sidecar_conflict', rich_document())
        self.assertEqual(200, status, saved)
        sidecar = self.root/'grids/sidecar_conflict.layers.json'
        sidecar.write_bytes(sidecar.read_bytes()+b' ')
        status, conflict = self.save('sidecar_conflict', rich_document(), expected_disk_revision=saved['disk_revision'])
        self.assertEqual(409, status, conflict)

    def test_concurrent_writers_cannot_both_overwrite_same_revision(self):
        doc = rich_document()
        status, saved = self.save('concurrent', doc)
        self.assertEqual(200, status, saved)
        def update(weight):
            changed = deepcopy(doc)
            changed['grid']['cells'][0]['mutation_weight'] = weight
            return self.save('concurrent', changed, expected_disk_revision=saved['disk_revision'])[0]
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual([200, 409], sorted(pool.map(update, [.2, .3])))

    def test_repeated_overwrite_backups_are_unique_and_preserved(self):
        document = rich_document()
        status, saved = self.save('backup_unique', document)
        self.assertEqual(200, status, saved)
        backups = []
        for weight in [.25, .5, .75]:
            document['grid']['cells'][0]['mutation_weight'] = weight
            status, saved = self.save('backup_unique', document, expected_disk_revision=saved['disk_revision'])
            self.assertEqual(200, status, saved)
            backups.append(saved['backup'])
        self.assertEqual(3, len(set(backups)))
        self.assertEqual([.91, .25, .5], [json.loads((self.root/'grids'/name).read_text())['cells'][0]['mutation_weight'] for name in backups])

    def test_release_uses_selected_inline_draft_and_explicit_copy_transform(self):
        document = rich_document()
        status, saved = self.save('release_selected', document)
        self.assertEqual(200, status, saved)
        document['grid']['cells'][0]['mutation_weight'] = .33
        payload = {'name': 'release_selected', 'document': document, 'draft_revision': 29}
        status, released = self.post('/api/release', payload)
        self.assertEqual(200, status, released)
        self.assertEqual(29, released['draft_revision'])
        self.assertEqual(document, released['document'])
        self.assertEqual('released_into_ecosystem', released['transform'])
        actual = json.loads((self.root/'released/release_selected.json').read_text())
        self.assertEqual(.33, actual['cells'][0]['mutation_weight'])
        self.assertEqual(actual, released['released_document']['grid'])
        self.assertEqual(.91, json.loads((self.root/'grids/release_selected.json').read_text())['cells'][0]['mutation_weight'])
        status, conflict = self.post('/api/release', payload)
        self.assertEqual(409, status, conflict)
        payload['expected_release_revision'] = conflict['current_revision']
        status, retry = self.post('/api/release', payload)
        self.assertEqual(200, status, retry)
        self.assertIsNotNone(retry['backup'])

    def test_clip_packets_derive_from_the_same_document_and_inline_profile(self):
        document = rich_document()
        status, result = self.post('/api/preview/clip', {'document': document, 'draft_revision': 42, 'clip': 'idle'})
        self.assertEqual(200, status, result)
        self.assertEqual(42, result['draft_revision'])
        expected = [render_packet_v2(document['grid'], None, clip='idle', frame_index=i,
            slip_profile=document['profile']) for i in range(clip_frame_count('idle'))]
        self.assertEqual(expected, result['frames'])
        self.assertEqual(document, result['document'])

    def test_all_four_carriers_roundtrip_complete_document(self):
        document = rich_document()
        for kind in ('png', 'apng', 'aseprite', 'spritesheet'):
            with self.subTest(kind=kind):
                status, output, headers = self.request('/api/export/'+kind,
                    {'document': document, 'draft_revision': 51, 'name': 'full_fidelity'})
                self.assertEqual(200, status, output)
                if kind == 'spritesheet':
                    status, imported = self.post('/api/import/spritesheet', output)
                else:
                    self.assertEqual('51', headers.get('X-Workshop-Draft-Revision'))
                    status, imported, _ = self.request('/api/import/'+('aseprite' if kind == 'aseprite' else 'png'), raw=output)
                self.assertEqual(200, status, imported)
                self.assertEqual(document, imported['document'])

    def test_conflicting_carrier_snapshot_is_refused(self):
        status, exported = self.post('/api/export/spritesheet', {'document': rich_document(), 'draft_revision': 1})
        self.assertEqual(200, status, exported)
        exported['sidecar']['authoring_document']['grid']['cells'][0]['mutation_weight'] = .05
        status, refused = self.post('/api/import/spritesheet', exported)
        self.assertEqual(400, status, refused)
        self.assertTrue(refused['errors'])

    def test_profile_only_document_preserves_mechanics_and_requires_disk_revision(self):
        document = {'format': FORMAT, 'profile': rich_document()['profile']}
        status, verdict = self.post('/api/slip/validate', {'document': document, 'draft_revision': 9})
        self.assertEqual(200, status, verdict)
        self.assertTrue(verdict['valid'])
        self.assertEqual(document, verdict['document'])
        status, saved = self.post('/api/slip/save', {'document': document, 'draft_revision': 9, 'expected_disk_revision': None})
        self.assertEqual(200, status, saved)
        status, loaded, _ = self.request('/api/slips/'+document['profile']['profile_id'])
        self.assertEqual(document, loaded['document'])
        self.assertEqual(saved['disk_revision'], loaded['disk_revision'])
        document['profile']['name'] = 'An explicit edit'
        status, refused = self.post('/api/slip/save', {'document': document, 'draft_revision': 10})
        self.assertEqual(409, status, refused)

    def test_lying_layers_are_refused_for_every_document_operation(self):
        document = rich_document()
        document['layers'][0]['matrix'][7][7] = 'B'
        for endpoint in ('/api/validate', '/api/save', '/api/preview/clip', '/api/export/png', '/api/release'):
            with self.subTest(endpoint=endpoint):
                status, result = self.post(endpoint, {'document': document, 'name': 'lying', 'draft_revision': 1})
                self.assertEqual(400, status, result)
                self.assertIn('layers', str(result))

    def test_legacy_export_honors_cell_overrides(self):
        status, png, _ = self.request('/api/export/png', {'matrix': MATRIX, 'palette_id': 'lcd_green',
            'profile_id': 'slip_lcd_seed', 'cell_overrides': {'1,0': {'mutation_weight': .91}}})
        self.assertEqual(200, status)
        from png_embedded_sidecar_writer import import_png_with_embedded_sidecar
        imported = import_png_with_embedded_sidecar(png)
        self.assertEqual(.91, imported['restored_grid']['cells'][0]['mutation_weight'])


    def test_mid_save_io_failure_preserves_original_pair_and_backups(self):
        import authoring
        document = rich_document()
        status, saved = self.save('io_rollback', document)
        self.assertEqual(200, status, saved)
        target = self.root/'grids/io_rollback.json'
        sidecar = self.root/'grids/io_rollback.layers.json'
        before = (target.read_bytes(), sidecar.read_bytes())
        document['grid']['cells'][0]['mutation_weight'] = .17
        real_write = authoring.atomic_bytes
        def fail_sidecar(path, data):
            if path == sidecar:
                raise OSError('injected sidecar failure')
            real_write(path, data)
        with patch.object(authoring, 'atomic_bytes', side_effect=fail_sidecar):
            status, refused = self.save('io_rollback', document, expected_disk_revision=saved['disk_revision'])
        self.assertEqual(500, status, refused)
        self.assertEqual(before, (target.read_bytes(), sidecar.read_bytes()))
        self.assertEqual(document, refused['document'])
        self.assertEqual(2, len(list((self.root/'grids').glob('io_rollback*.bak.json'))))

    def test_saved_document_reopens_after_server_restart(self):
        document = rich_document()
        status, saved = self.save('restart', document)
        self.assertEqual(200, status, saved)
        other = start_workshop_server(port=0, grids_dir=self.root/'grids', slips_dir=self.root/'slips',
            released_dir=self.root/'released', metrics_dir=self.root/'metrics', session_dir=self.root/'keeper')
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{other.server_address[1]}/api/grids/restart') as response:
                loaded = json.load(response)
            self.assertEqual(document, loaded['document'])
            self.assertEqual(saved['disk_revision'], loaded['disk_revision'])
        finally:
            other.shutdown()
            other.server_close()

    def test_rectangular_valid_genome_can_save_and_export_without_reconstruction(self):
        document = rich_document()
        document.pop('layers')
        document['grid']['grid_size'] = [8, 9]
        self.assertTrue(validate_grid(document['grid']).ok)
        status, saved = self.save('rectangular', document)
        self.assertEqual(200, status, saved)
        status, png, _ = self.request('/api/export/png', {'document': document, 'draft_revision': 7})
        self.assertEqual(200, status, png)
        status, restored, _ = self.request('/api/import/png', raw=png)
        self.assertEqual(200, status, restored)
        self.assertEqual(document, restored['document'])

    def test_malformed_documents_return_errors_without_server_disconnect(self):
        for grid in ({'cells': 'bad'}, {'grid_size': [8, 8], 'cells': [{'x': 1, 'y': 1, 'role': []}]}):
            document = {'format': FORMAT, 'grid': grid}
            status, verdict = self.post('/api/validate', {'document': document, 'draft_revision': 1})
            self.assertEqual(200, status, verdict)
            self.assertFalse(verdict['valid'])
            self.assertTrue(verdict['errors'])
            status, refused = self.save('malformed', document)
            self.assertEqual(400, status, refused)
            self.assertFalse((self.root/'grids/malformed.json').exists())

    def test_tampered_snapshot_metadata_and_profile_are_refused(self):
        import authoring
        for kind in ('metadata', 'profile', 'overlay'):
            status, exported = self.post('/api/export/spritesheet', {'document': rich_document(), 'draft_revision': 1})
            self.assertEqual(200, status, exported)
            sidecar = exported['sidecar']
            if kind == 'metadata':
                sidecar['authoring_document']['grid']['parent_grid_id'] = 'invented_parent'
            elif kind == 'profile':
                sidecar['authoring_document']['profile']['mechanics']['cleanliness'] = 'not_boolean'
                sidecar['slip_binding']['profile_snapshot']['mechanics']['cleanliness'] = 'not_boolean'
                sidecar['authoring_document_digest'] = authoring.digest(sidecar['authoring_document'])
            else:
                sidecar['authoring_document']['grid']['cells'][0]['mutation_weight'] = .09
                sidecar['authoring_document_digest'] = authoring.digest(sidecar['authoring_document'])
            status, refused = self.post('/api/import/spritesheet', exported)
            self.assertEqual(400, status, refused)
            self.assertTrue(refused['errors'])

    def test_projected_animated_carriers_reimport_the_same_draft(self):
        document = rich_document()
        for kind in ('apng', 'spritesheet'):
            status, output, _ = self.request('/api/export/'+kind,
                {'document': document, 'draft_revision': 2, 'clip': 'ill'})
            self.assertEqual(200, status, output)
            if kind == 'apng':
                from png_embedded_sidecar_writer import extract_embedded_sidecar_from_png
                sidecar = extract_embedded_sidecar_from_png(output)['sidecar']
                binding = sidecar['apng_binding']
                status, restored, _ = self.request('/api/import/png', raw=output)
            else:
                binding = output['sidecar']['animation_binding']
                status, restored = self.post('/api/import/spritesheet', output)
            self.assertEqual(200, status, restored)
            self.assertEqual(document, restored['document'])
            self.assertEqual({'kind': 'clip_frames', 'clip': 'ill'}, binding['frame_source'])
            expected = [render_packet_v2(document['grid'], None, clip='ill', frame_index=i,
                slip_profile=document['profile'])['animation'] for i in range(clip_frame_count('ill'))]
            self.assertEqual(expected, [frame['animation'] for frame in binding['frames']])

    def test_imports_echo_request_revision_without_changing_carried_document(self):
        document = rich_document()
        for kind in ('png', 'aseprite', 'spritesheet'):
            status, output, _ = self.request('/api/export/'+kind, {'document': document, 'draft_revision': 12})
            self.assertEqual(200, status, output)
            if kind == 'spritesheet':
                output['draft_revision'] = 88
                status, imported = self.post('/api/import/spritesheet', output)
            else:
                status, imported, _ = self.request('/api/import/'+kind, raw=output, revision=88)
            self.assertEqual(200, status, imported)
            self.assertEqual(88, imported['draft_revision'])
            self.assertEqual(document, imported['document'])

    def test_inconsistent_saved_sidecar_refuses_load_without_discarding_bytes(self):
        status, saved = self.save('sidecar_inconsistent', rich_document())
        self.assertEqual(200, status, saved)
        sidecar = self.root/'grids/sidecar_inconsistent.layers.json'
        original = sidecar.read_bytes()
        for value in ({'unknown': True}, []):
            sidecar.write_text(json.dumps(value))
            before = sidecar.read_bytes()
            status, refused, _ = self.request('/api/grids/sidecar_inconsistent')
            self.assertEqual(409, status, refused)
            self.assertEqual(before, sidecar.read_bytes())
        sidecar.write_bytes(original)
        payload = json.loads(original)
        payload['layers'][0]['matrix'][7][7] = 'B'
        sidecar.write_text(json.dumps(payload))
        before = sidecar.read_bytes()
        status, refused, _ = self.request('/api/grids/sidecar_inconsistent')
        self.assertEqual(409, status, refused)
        self.assertEqual(before, sidecar.read_bytes())

    def test_review_profile_read_revision_cannot_authorize_stale_overwrite(self):
        document = {'format': FORMAT, 'profile': rich_document()['profile']}
        document['profile']['profile_id'] = 'review_atomic_profile'
        status, first = self.post('/api/slip/save', {'document': document,
            'draft_revision': 1, 'expected_disk_revision': None})
        self.assertEqual(200, status, first)
        changed = deepcopy(document)
        changed['profile']['name'] = 'The concurrently saved profile'
        reader_ready = threading.Event()
        writer_entered = threading.Event()
        writer_blocked = threading.Event()
        writer_done = threading.Event()
        reader_ident = [None]
        real_lock = self.server.authoring_lock
        real_profiles = self.server.all_profiles

        class ObservedLock:
            # Expose writer admission without sleeps. This retains the real
            # mutual exclusion and observes the actual two HTTP operations.
            def __enter__(self):
                if reader_ready.is_set() and threading.get_ident() != reader_ident[0]:
                    acquired = real_lock.acquire(blocking=False)
                    if not acquired:
                        writer_blocked.set()
                    writer_entered.set()
                    if not acquired:
                        real_lock.acquire()
                else:
                    real_lock.acquire()
                return self

            def __exit__(self, *args):
                real_lock.release()

        def pause_loaded_profile():
            profiles = real_profiles()
            reader_ident[0] = threading.get_ident()
            reader_ready.set()
            if not writer_entered.wait(5):
                raise AssertionError('concurrent writer never reached its save boundary')
            # Before the repair the writer can finish while this GET has
            # already read its old profile. With the repair it must wait.
            if not writer_blocked.is_set() and not writer_done.wait(5):
                raise AssertionError('admitted concurrent writer did not complete')
            return profiles

        def concurrent_save():
            try:
                return self.post('/api/slip/save', {'document': changed,
                    'draft_revision': 2, 'expected_disk_revision': first['disk_revision']})
            finally:
                writer_done.set()

        with patch.object(self.server, 'authoring_lock', ObservedLock()), patch.object(
                self.server, 'all_profiles', side_effect=pause_loaded_profile):
            with ThreadPoolExecutor(max_workers=2) as pool:
                reading = pool.submit(self.request, '/api/slips/review_atomic_profile')
                self.assertTrue(reader_ready.wait(5), 'GET did not read its profile')
                writing = pool.submit(concurrent_save)
                status, loaded, _ = reading.result(timeout=10)
                writer_status, saved = writing.result(timeout=10)
        self.assertEqual(200, status, loaded)
        self.assertEqual(200, writer_status, saved)
        self.assertEqual(document, loaded['document'])
        target = self.root/'slips/review_atomic_profile.json'
        before = target.read_bytes()
        stale = deepcopy(loaded['document'])
        stale['profile']['name'] = 'An edit based on the older profile'
        status, refused = self.post('/api/slip/save', {'document': stale,
            'draft_revision': 3, 'expected_disk_revision': loaded['disk_revision']})
        self.assertEqual(409, status, refused)
        self.assertEqual(first['disk_revision'], loaded['disk_revision'])
        self.assertEqual(before, target.read_bytes())

    def test_review_partial_modern_carriers_cannot_fall_back_to_lossy_legacy(self):
        for mutation in ('null_document', 'missing_document', 'missing_digest', 'null_digest'):
            with self.subTest(mutation=mutation):
                status, exported = self.post('/api/export/spritesheet',
                    {'document': rich_document(), 'draft_revision': 1})
                self.assertEqual(200, status, exported)
                sidecar = exported['sidecar']
                if mutation == 'null_document':
                    sidecar['authoring_document'] = None
                elif mutation == 'missing_document':
                    del sidecar['authoring_document']
                elif mutation == 'missing_digest':
                    del sidecar['authoring_document_digest']
                else:
                    sidecar['authoring_document_digest'] = None
                status, refused = self.post('/api/import/spritesheet', exported)
                self.assertEqual(400, status, refused)
                self.assertTrue(refused['errors'])

if __name__ == '__main__':
    unittest.main()
