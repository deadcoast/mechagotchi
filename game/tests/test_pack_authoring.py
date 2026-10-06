"""X3: complete named packs, read-only preview and isolated retryable import."""
import copy
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import threading
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for folder in ('game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT / folder))
from mecha_game import packs


def files(root):
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob('*') if p.is_file()}


def composition():
    profile = json.loads((ROOT/'data/slips/valid/slip_lcd_seed.json').read_text(encoding='utf-8'))
    creature = json.loads((ROOT/'data/seed_grids_16x16/mg_seed16_002_wisp.json').read_text(encoding='utf-8'))
    creature.setdefault('metadata', {})['workshop'] = {'notes': ['exact', {'origin': 'saved elite'}]}
    return dict(pack_id='named_pack', title='Moon garden', provenance={
        'author': 'Keeper', 'source': {'keeper_id': 'foreign_declared_identity',
                                     'campaign_id': 'foreign_campaign', 'era_index': 4},
        'notes': ['Full payloads', {'unicode': '\u6708'}]}, slips=[profile], creatures=[creature])


def sample():
    return packs.build_pack(**composition())


class PackAuthoringTests(unittest.TestCase):
    def test_named_builder_validates_metadata_types_and_filename_identity(self):
        invalid = [('pack_id', '../escape'), ('pack_id', ''), ('pack_id', 'ending.'),
                   ('title', ''), ('title', 4), ('provenance', []), ('slips', {}),
                   ('creatures', None), ('provenance', {'non_json': float('nan')})]
        for field, value in invalid:
            with self.subTest(field=field, value=value):
                args = composition(); args[field] = value
                with self.assertRaises(ValueError):
                    packs.build_pack(**args)
        args = composition(); args.update(slips=[], creatures=[])
        with self.assertRaises(ValueError):
            packs.build_pack(**args)

    def test_builder_copies_nested_provenance_and_complete_selected_fields(self):
        args = composition(); expected = copy.deepcopy(args)
        pack = packs.build_pack(**args)
        args['provenance']['notes'][1]['unicode'] = 'changed'
        args['slips'][0]['grid']['allowed_palettes'].append('changed')
        args['creatures'][0]['cells'][0]['visual'] = 'changed'
        for key in expected:
            self.assertEqual(expected[key], pack[key])

    def test_builder_refuses_duplicate_selection_identities(self):
        for field in ('slips', 'creatures'):
            with self.subTest(field=field):
                args = composition(); args[field].append(copy.deepcopy(args[field][0]))
                with self.assertRaisesRegex(ValueError, 'duplicate'):
                    packs.build_pack(**args)

    def test_export_roundtrips_every_field_and_uses_canonical_semantic_digest(self):
        pack = sample(); pack['extension'] = {'caller_field': ['preserved']}
        raw = packs.export_pack_bytes(pack)
        self.assertEqual(pack, json.loads(raw))
        expected = hashlib.sha256(json.dumps(pack, sort_keys=True, separators=(',', ':'),
                                             ensure_ascii=False, allow_nan=False).encode()).hexdigest()
        self.assertEqual(expected, packs.pack_digest(pack))
        reordered = dict(reversed(list(pack.items())))
        self.assertEqual(expected, packs.pack_digest(reordered))
        pack['slips'][0]['slip_version'] = '9.9.9'
        with self.assertRaisesRegex(ValueError, 'slip_version'):
            packs.export_pack_bytes(pack)

    def test_preview_is_read_only_even_when_destination_does_not_exist(self):
        pack = sample()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); keeper = root/'not_created'
            before = files(root)
            report = packs.preview_pack(keeper, pack)
            self.assertTrue(report['ok']); self.assertTrue(report['all_accepted'])
            self.assertFalse(report['partial']); self.assertEqual(2, report['accepted_count'])
            self.assertEqual('ready', report['slips'][0]['status'])
            self.assertEqual('ready', report['creatures'][0]['status'])
            self.assertEqual(before, files(root)); self.assertFalse(keeper.exists())
            self.assertTrue(packs.preview_pack(None, pack)['all_accepted'])

    def test_source_receipt_is_exact_and_receiving_keeper_remains_independent(self):
        pack = sample()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); first = root/'first'; second = root/'second'
            first.mkdir(); second.mkdir()
            (first/'companion.json').write_bytes(b'first Keeper own history')
            (second/'companion.json').write_bytes(b'second Keeper own history')
            (second/'campaign_state.json').write_bytes(b'second campaign own state')
            protected = files(root)
            result = packs.import_pack_document(second, pack, expected_pack_digest=packs.pack_digest(pack))
            self.assertTrue(result['all_accepted']); self.assertEqual(2, result['accepted_count'])
            self.assertFalse(result['receipt']['already_retained'])
            self.assertEqual(pack, json.loads((second/'packs'/result['receipt']['file']).read_bytes()))
            self.assertEqual(pack['slips'][0], json.loads((second/'covenants'/result['slips'][0]['staged']).read_bytes()))
            self.assertEqual(pack['creatures'][0], json.loads((second/'released'/result['creatures'][0]['staged']).read_bytes()))
            for name, raw in protected.items(): self.assertEqual(raw, (root/name).read_bytes())
            self.assertEqual({'companion.json': b'first Keeper own history'}, files(first))
            before = files(root)
            again = packs.import_pack_document(second, pack, expected_pack_digest=packs.pack_digest(pack))
            self.assertTrue(again['receipt']['already_retained'])
            self.assertTrue(again['slips'][0]['already_staged'])
            self.assertTrue(again['creatures'][0]['already_staged'])
            self.assertEqual(before, files(root))

    def test_tampering_after_preview_refuses_every_write(self):
        pack = sample(); digest = packs.pack_digest(pack)
        pack['provenance']['notes'].append('changed after preview')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); before = files(root)
            result = packs.import_pack_document(root, pack, expected_pack_digest=digest)
            self.assertFalse(result['ok']); self.assertIn('changed', ' '.join(result['violations']))
            self.assertEqual(before, files(root))

    def test_partial_invalid_duplicate_preserves_valid_item_and_full_verdict(self):
        pack = sample(); bad = copy.deepcopy(pack['slips'][0]); bad['slip_version'] = '9.9.9'
        pack['slips'].insert(0, bad)
        with tempfile.TemporaryDirectory() as directory:
            keeper = Path(directory)
            result = packs.import_pack_document(keeper, pack, expected_pack_digest=packs.pack_digest(pack))
            self.assertTrue(result['ok']); self.assertTrue(result['partial']); self.assertFalse(result['all_accepted'])
            self.assertEqual((2, 1), (result['accepted_count'], result['refused_count']))
            self.assertFalse(result['slips'][0]['ok']); self.assertTrue(result['slips'][1]['ok'])
            self.assertIn('slip_version', ' '.join(result['slips'][0]['violations']))
            self.assertTrue(result['creatures'][0]['ok'])
            self.assertEqual(pack, json.loads((keeper/'packs'/result['receipt']['file']).read_bytes()))

    def test_conflicting_valid_duplicate_identities_are_order_independent(self):
        for reverse in (False, True):
            with self.subTest(reverse=reverse), tempfile.TemporaryDirectory() as directory:
                pack = sample(); changed = copy.deepcopy(pack['creatures'][0])
                changed['metadata']['workshop']['notes'].append('different body record')
                pack['creatures'].append(changed)
                if reverse: pack['creatures'].reverse()
                root = Path(directory)
                result = packs.import_pack_document(root, pack, expected_pack_digest=packs.pack_digest(pack))
                self.assertTrue(result['slips'][0]['ok'])
                self.assertTrue(all(not row['ok'] and row['status'] == 'conflicting' for row in result['creatures']))
                self.assertEqual([], list((root/'released').glob('*.json')))

    def test_identical_import_duplicates_have_one_output_and_explicit_relationship(self):
        pack = sample(); pack['creatures'].append(copy.deepcopy(pack['creatures'][0]))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            preview = packs.preview_pack(root, pack)
            self.assertEqual('duplicate', preview['creatures'][1]['status'])
            self.assertEqual(0, preview['creatures'][1]['duplicate_of'])
            result = packs.import_pack_document(root, pack, expected_pack_digest=packs.pack_digest(pack))
            self.assertTrue(result['all_accepted'])
            self.assertEqual(1, len(list((root/'released').glob('*.json'))))
            self.assertEqual('duplicate', result['creatures'][1]['status'])

    def test_cross_pack_identity_conflict_preserves_inbox_without_silent_merge(self):
        pack = sample()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packs.import_pack_document(root, pack, expected_pack_digest=packs.pack_digest(pack))
            changed = copy.deepcopy(pack); changed['pack_id'] = 'other_named_pack'
            changed['slips'] = []; changed['creatures'][0]['metadata']['workshop']['notes'].append('conflict')
            before = files(root)
            preview = packs.preview_pack(root, changed)
            self.assertEqual('conflicting', preview['creatures'][0]['status'])
            result = packs.import_pack_document(root, changed, expected_pack_digest=packs.pack_digest(changed))
            self.assertFalse(result['all_accepted']); self.assertFalse(result['creatures'][0]['ok'])
            self.assertNotIn('receipt', result); self.assertEqual(before, files(root))

    def test_identical_existing_named_release_is_recognized_without_rewrite(self):
        pack = sample(); pack['slips'] = []
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root/'released').mkdir()
            target = root/'released'/'owner_selected_name.json'
            target.write_text(json.dumps(pack['creatures'][0], indent=4), encoding='utf-8')
            before = target.read_bytes()
            result = packs.import_pack_document(root, pack, expected_pack_digest=packs.pack_digest(pack))
            self.assertTrue(result['creatures'][0]['already_staged'])
            self.assertEqual(target.name, result['creatures'][0]['staged'])
            self.assertEqual(before, target.read_bytes())
            self.assertEqual(1, len(list((root/'released').glob('*.json'))))

    def test_receipt_conflict_or_io_failure_never_stages_items(self):
        pack = sample(); digest = packs.pack_digest(pack)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root/'packs').mkdir()
            receipt = root/'packs'/f'received_{digest}.json'; receipt.write_bytes(b'owner evidence')
            before = files(root)
            result = packs.import_pack_document(root, pack, expected_pack_digest=digest)
            self.assertFalse(result['ok']); self.assertEqual(before, files(root))
            receipt.unlink()
            original = packs._stage_item
            def denied(target, value):
                if target.parent.name == 'packs': raise PermissionError('receipt locked')
                return original(target, value)
            with patch.object(packs, '_stage_item', side_effect=denied):
                result = packs.import_pack_document(root, pack, expected_pack_digest=digest)
            self.assertFalse(result['ok']); self.assertEqual({}, files(root))

    def test_partial_io_failure_retries_without_rewriting_successful_items(self):
        pack = sample(); digest = packs.pack_digest(pack)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); original = packs._stage_item
            def denied(target, value):
                if target.parent.name == 'covenants': raise PermissionError('covenant locked')
                return original(target, value)
            with patch.object(packs, '_stage_item', side_effect=denied):
                result = packs.import_pack_document(root, pack, expected_pack_digest=digest)
            self.assertTrue(result['partial']); self.assertEqual('io_error', result['slips'][0]['status'])
            self.assertTrue(result['creatures'][0]['ok'])
            existing = files(root)
            again = packs.import_pack_document(root, pack, expected_pack_digest=digest)
            self.assertTrue(again['all_accepted']); self.assertTrue(again['receipt']['already_retained'])
            for name, raw in existing.items(): self.assertEqual(raw, (root/name).read_bytes())

    def test_atomic_staging_failure_leaves_no_partial_target_and_retry_succeeds(self):
        pack = sample(); item = pack['creatures'][0]
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)/'released'/'item.json'
            with patch('mecha_game.packs.os.link', side_effect=PermissionError('publish locked')):
                with self.assertRaises(PermissionError): packs._stage_item(target, item)
            self.assertFalse(target.exists()); self.assertEqual({}, files(Path(directory)))
            self.assertFalse(packs._stage_item(target, item)); self.assertEqual(item, json.loads(target.read_bytes()))

    def test_file_picker_raw_digest_remains_distinct_from_document_digest(self):
        pack = sample()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = packs.write_pack(pack, root/'source.json')
            raw = source.read_bytes(); raw_digest = hashlib.sha256(raw).hexdigest()
            self.assertNotEqual(raw_digest, packs.pack_digest(pack))
            refused = packs.import_pack(root/'wrong', source, expected_digest=packs.pack_digest(pack))
            self.assertFalse(refused['ok']); self.assertFalse((root/'wrong').exists())
            accepted = packs.import_pack(root/'right', source, expected_digest=raw_digest)
            self.assertTrue(accepted['all_accepted']); self.assertEqual(raw, source.read_bytes())
            self.assertEqual(raw_digest, accepted['source_digest'])

    def test_overlapping_imports_cannot_publish_conflicting_bodies_for_one_identity(self):
        first = sample(); first['slips'] = []
        second = copy.deepcopy(first); second['pack_id'] = 'second_pack'
        second['creatures'][0]['metadata']['workshop']['notes'].append('another record')
        entered = threading.Event(); release = threading.Event()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); original = packs._stage_item
            def pause_first(target, value):
                if target.parent.name == 'released' and target.name.startswith('pack_named_pack_'):
                    entered.set()
                    if not release.wait(3): raise AssertionError('test failed to release staging')
                return original(target, value)
            with patch.object(packs, '_stage_item', side_effect=pause_first), ThreadPoolExecutor(max_workers=2) as pool:
                one = pool.submit(packs.import_pack_document, root, first, expected_pack_digest=packs.pack_digest(first))
                self.assertTrue(entered.wait(2))
                two = pool.submit(packs.import_pack_document, root, second, expected_pack_digest=packs.pack_digest(second))
                try:
                    two.result(timeout=0.15)
                except TimeoutError:
                    pass
                finally:
                    release.set()
                results = [one.result(timeout=3), two.result(timeout=3)]
            self.assertEqual(1, sum(result['creatures'][0]['ok'] for result in results))
            self.assertEqual(1, len(list((root/'released').glob('*.json'))))

    def test_external_file_import_retains_source_in_selected_pack_inbox(self):
        pack = sample()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = packs.write_pack(pack, root/'download.json')
            raw = source.read_bytes(); keeper = root/'selected'
            result = packs.import_pack(keeper, source, expected_digest=hashlib.sha256(raw).hexdigest())
            self.assertTrue(result['all_accepted'])
            receipts = list((keeper/'packs').glob('*.json'))
            self.assertEqual(1, len(receipts)); self.assertEqual(pack, json.loads(receipts[0].read_bytes()))
            self.assertEqual(raw, source.read_bytes())

    def test_malformed_or_all_refused_documents_write_nothing(self):
        for broken in (None, [], {}, dict(sample(), provenance=[]),
                       dict(sample(), slips=[None], creatures=[[]])):
            with self.subTest(broken=type(broken).__name__), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); preview = packs.preview_pack(root, broken)
                result = packs.import_pack_document(root, broken, expected_pack_digest=packs.pack_digest(broken))
                self.assertFalse(result['all_accepted']); self.assertEqual({}, files(root))
                self.assertEqual(preview['ok'], result['ok'])


if __name__ == '__main__':
    unittest.main()
