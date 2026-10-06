"""X4 startup authority: real temporary files; injected I/O cases labeled separately."""
import dataclasses
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for folder in ('game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT / folder))
from mecha_game.session import CompanionSession, load_session_inputs


def authority():
    return importlib.import_module('mecha_game.startup')


def inventory(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


class StartupFixtures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_session_inputs(ROOT / 'data/seed_grids_16x16/mg_seed16_001_beetle.json',
                                        ROOT / 'data/slips/valid/slip_v2_cleanliness.json')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / 'selected keeper'
        self.path = self.home / 'companion.json'
        self.backup = self.path.with_suffix('.bak.json')

    def pair(self, policy='incumbent'):
        grid, slip, model = self.inputs
        pet = CompanionSession(grid, slip, model=model, learning_policy=policy)
        pet.save(self.path)
        pet.advance('feed')
        pet.save(self.path)
        return pet


class StartupFilesystemTests(StartupFixtures):
    def test_missing_home_inspection_never_creates_files_or_loads_assets(self):
        with patch('mecha_game.packets.default_fixture_paths', side_effect=AssertionError('no default discovery')), \
                patch('mecha_game.session.train_generation_model', side_effect=AssertionError('no training')):
            inspected = authority().inspect_home(self.home)
        self.assertEqual('missing', inspected.home_status)
        self.assertEqual(('missing', 'missing'), (inspected.primary.status, inspected.backup.status))
        self.assertEqual(('new', 'choose_directory', 'retry', 'quit'), inspected.actions)
        self.assertFalse(self.home.exists())
        with self.assertRaises(dataclasses.FrozenInstanceError): inspected.revision = 'changed'
        with self.assertRaises(dataclasses.FrozenInstanceError): inspected.primary.status = 'valid'

    def test_home_and_guard_normalize_relative_components_without_creating_them(self):
        chosen = self.root / 'uncreated parent' / '..' / 'normal home'
        inspected = authority().inspect_home(chosen)
        self.assertEqual((self.root / 'normal home').resolve(), inspected.home)
        prepared = authority().explicit_new_session(chosen / 'companion.json', *self.inputs, None, inspection=inspected)
        self.assertEqual('incumbent', prepared.learning_policy)
        self.assertEqual({}, inventory(self.root))
        self.assertFalse((self.root / 'uncreated parent').exists())

    def test_both_saved_policies_resume_without_default_assets_or_campaign(self):
        for policy in ('incumbent', 'qtable'):
            with self.subTest(policy=policy):
                pet = self.pair(policy); before = inventory(self.root)
                with patch('mecha_game.packets.default_fixture_paths', side_effect=FileNotFoundError('assets absent')), \
                        patch('mecha_game.session.train_generation_model', side_effect=AssertionError('no training')):
                    inspected = authority().inspect_home(self.home)
                    resumed = authority().resume_session(inspected)
                self.assertEqual('valid', inspected.primary.status)
                self.assertIn('resume', inspected.actions)
                self.assertEqual((pet.name, pet.keeper_id, pet.lineage[-1]['life_id'], policy, 1, 1),
                    (inspected.primary.name, inspected.primary.keeper_id, inspected.primary.life_id,
                     inspected.primary.learning_policy, inspected.primary.session_tick, inspected.primary.life_count))
                self.assertEqual(pet.state, resumed.state)
                self.assertEqual(pet.lineage, resumed.lineage)
                self.assertEqual(pet.chronicle, resumed.chronicle)
                self.assertEqual(before, inventory(self.root))
                self.assertFalse((self.home / 'campaign.sqlite3').exists())
                with self.assertRaises(ValueError):
                    authority().resume_session(inspected, learning_policy='qtable' if policy == 'incumbent' else 'incumbent')
                self.assertEqual(before, inventory(self.root))

    def test_malformed_primary_is_independent_from_valid_backup_and_restores_explicitly(self):
        for policy in ('incumbent', 'qtable'):
            with self.subTest(policy=policy):
                self.pair(policy); self.path.write_bytes(b'invalid primary retained exactly')
                primary, backup = self.path.read_bytes(), self.backup.read_bytes()
                before = inventory(self.root); inspected = authority().inspect_home(self.home)
                self.assertEqual(('invalid', 'valid'), (inspected.primary.status, inspected.backup.status))
                self.assertNotIn('resume', inspected.actions)
                self.assertIn('inspect_backup', inspected.actions)
                self.assertTrue(inspected.can_restore)
                self.assertEqual(before, inventory(self.root), 'inspection/cancel has no writes')
                with self.assertRaises(ValueError): authority().resume_session(inspected)
                self.assertEqual(before, inventory(self.root))
                restored, archive = authority().restore_session(inspected)
                self.assertEqual(primary, archive.read_bytes())
                self.assertEqual(backup, self.path.read_bytes())
                self.assertEqual(backup, self.backup.read_bytes())
                self.assertEqual(policy, restored.learning_policy)
                self.assertFalse((self.home / 'lineage.json').exists())

    def test_backup_only_stays_missing_until_confirmed_restore(self):
        self.pair('qtable'); self.path.unlink(); original = self.backup.read_bytes()
        inspected = authority().inspect_home(self.home)
        self.assertNotIn('resume', inspected.actions)
        self.assertFalse(self.path.exists())
        restored, archive = authority().restore_session(inspected)
        self.assertIsNone(archive)
        self.assertEqual('qtable', restored.learning_policy)
        self.assertEqual(original, self.path.read_bytes())
        self.assertEqual(original, self.backup.read_bytes())

    def test_excessively_nested_json_remains_an_inspectable_invalid_save(self):
        self.home.mkdir()
        raw = b'[' * 1500 + b'0' + b']' * 1500
        self.path.write_bytes(raw); self.backup.write_bytes(raw)
        before = inventory(self.root)
        inspected = authority().inspect_home(self.home)
        self.assertEqual(('invalid', 'invalid'), (inspected.primary.status, inspected.backup.status))
        self.assertNotIn('resume', inspected.actions)
        self.assertFalse(inspected.can_restore)
        self.assertIn('new', inspected.actions)
        self.assertTrue(inspected.primary.reason)
        self.assertEqual(before, inventory(self.root))

    def test_invalid_backup_has_no_restore_and_never_becomes_a_fresh_life(self):
        self.pair(); self.path.write_bytes(b'invalid primary'); self.backup.write_bytes(b'invalid backup')
        before = inventory(self.root); inspected = authority().inspect_home(self.home)
        self.assertEqual(('invalid', 'invalid'), (inspected.primary.status, inspected.backup.status))
        self.assertFalse(inspected.can_restore)
        self.assertNotIn('inspect_backup', inspected.actions)
        self.assertIn('new', inspected.actions)
        with self.assertRaises(ValueError): authority().restore_session(inspected)
        self.assertEqual(before, inventory(self.root))

    def test_file_directory_conflicts_preserve_every_entry(self):
        self.pair(); self.path.unlink(); self.path.mkdir(); (self.path / 'owner').write_bytes(b'owner')
        before = inventory(self.root); inspected = authority().inspect_home(self.home)
        self.assertEqual('directory', inspected.primary.status)
        self.assertFalse(inspected.can_restore)
        self.assertNotIn('new', inspected.actions)
        with self.assertRaises(ValueError): authority().restore_session(inspected)
        with self.assertRaises(ValueError): authority().explicit_new_session(self.path, *self.inputs, None, inspection=inspected)
        self.assertEqual(before, inventory(self.root))
        other = self.root / 'home is a file'; other.write_bytes(b'owner file')
        inspected = authority().inspect_home(other)
        self.assertEqual('file', inspected.home_status)
        self.assertEqual(('choose_directory', 'retry', 'quit'), inspected.actions)
        self.assertEqual(b'owner file', other.read_bytes())

    def test_new_with_backup_history_preserves_originals_and_both_policies(self):
        for policy in ('incumbent', 'qtable'):
            with self.subTest(policy=policy):
                old = self.pair(policy); self.path.unlink()
                original = self.backup.read_bytes(); prior = CompanionSession._from_payload(json.loads(original))
                inspected = authority().inspect_home(self.home)
                fresh = authority().explicit_new_session(self.path, *self.inputs, None, inspection=inspected)
                self.assertEqual(prior.keeper_id, fresh.keeper_id)
                self.assertEqual(policy, fresh.learning_policy)
                self.assertEqual(len(prior.lineage) + 1, len(fresh.lineage))
                self.assertEqual('unavailable', fresh.chronicle['prior_history'])
                self.assertFalse(self.path.exists(), 'new authority returns the prepared session; caller checkpoints')
                self.assertTrue(any(p.read_bytes() == original for p in self.home.glob('*.replaced-*.json')))
                fresh.save_checkpoint(self.path); fresh.advance('feed'); fresh.save_checkpoint(self.path)
                self.assertTrue(any(p.read_bytes() == original for p in self.home.glob('*.replaced-*.json')))

    def test_explicit_new_invalid_history_retains_both_originals_and_marks_gap(self):
        self.home.mkdir(); self.path.write_bytes(b'old primary'); self.backup.write_bytes(b'old backup')
        inspected = authority().inspect_home(self.home)
        fresh = authority().explicit_new_session(self.path, *self.inputs, 'qtable', inspection=inspected)
        self.assertEqual('qtable', fresh.learning_policy)
        self.assertEqual('unavailable', fresh.chronicle['prior_history'])
        originals = {p.read_bytes() for p in self.home.glob('*.replaced-*.json')}
        self.assertEqual({b'old primary', b'old backup'}, originals)
        self.assertEqual(b'old primary', self.path.read_bytes())
        self.assertEqual(b'old backup', self.backup.read_bytes())

    def test_new_invalid_assets_are_validated_before_archiving(self):
        self.pair(); inspected = authority().inspect_home(self.home); before = inventory(self.root)
        grid = dict(self.inputs[0], cells=[])
        with self.assertRaises(ValueError):
            authority().explicit_new_session(self.path, grid, self.inputs[1], self.inputs[2], None, inspection=inspected)
        self.assertEqual(before, inventory(self.root))

    def test_changed_primary_or_backup_invalidates_all_inspected_choices(self):
        for filename in ('companion.json', 'companion.bak.json'):
            with self.subTest(filename=filename):
                self.pair(); inspected = authority().inspect_home(self.home)
                changed = self.home / filename; changed.write_bytes(changed.read_bytes() + b' ')
                before = inventory(self.root)
                for action in (lambda: authority().resume_session(inspected),
                               lambda: authority().restore_session(inspected),
                               lambda: authority().explicit_new_session(self.path, *self.inputs, None, inspection=inspected)):
                    with self.assertRaisesRegex(ValueError, 'changed'): action()
                    self.assertEqual(before, inventory(self.root))

    def test_expected_absence_is_distinct_from_unguarded_legacy_recovery(self):
        self.pair(); primary = self.path.read_bytes(); backup = self.backup.read_bytes(); before = inventory(self.root)
        with self.assertRaisesRegex(ValueError, 'changed'):
            CompanionSession.recover_backup(self.path, expected_primary_digest=None, expected_backup_digest=digest(backup))
        self.assertEqual(before, inventory(self.root))
        restored, archive = CompanionSession.recover_backup(self.path)
        self.assertEqual(primary, archive.read_bytes())
        self.assertEqual(backup, self.path.read_bytes())
        self.assertEqual(0, restored.session_tick)

    def test_conflicting_preservation_archive_refuses_without_overwrite(self):
        self.pair(); primary = self.path.read_bytes()
        archive = self.home / ('companion.replaced-' + digest(primary) + '.json')
        archive.write_bytes(b'other archive owner'); before = inventory(self.root)
        with self.assertRaisesRegex(ValueError, 'conflict'):
            authority().explicit_new_session(self.path, *self.inputs, None, inspection=authority().inspect_home(self.home))
        self.assertEqual(before, inventory(self.root))


class StartupInjectedIOTests(StartupFixtures):
    """Fault injection, not an assertion about Windows ACL behavior."""
    def test_invalid_path_expansion_is_an_actionable_read_error(self):
        with patch.object(Path, 'expanduser', side_effect=RuntimeError('injected unavailable user home')):
            inspected = authority().inspect_home(self.home)
        self.assertEqual('unreadable', inspected.home_status)
        self.assertIn('unavailable user home', inspected.reason)
        self.assertEqual(('choose_directory', 'retry', 'quit'), inspected.actions)
        self.assertEqual({}, inventory(self.root))

    def test_unreadable_home_is_reported_without_write_or_fallback(self):
        self.home.mkdir(); actual = Path.stat
        def denied(path, *args, **kwargs):
            if path == self.home: raise PermissionError('injected home read denial')
            return actual(path, *args, **kwargs)
        with patch.object(Path, 'stat', denied): inspected = authority().inspect_home(self.home)
        self.assertEqual('unreadable', inspected.home_status)
        self.assertIn('denial', inspected.reason)
        self.assertEqual(('choose_directory', 'retry', 'quit'), inspected.actions)
        self.assertEqual({}, inventory(self.root))

    def test_unreadable_backup_does_not_hide_valid_primary_but_blocks_destructive_choices(self):
        original = self.pair('qtable'); before = inventory(self.root); actual = Path.read_bytes
        def denied(path):
            if path == self.backup: raise PermissionError('injected backup read denial')
            return actual(path)
        with patch.object(Path, 'read_bytes', denied):
            inspected = authority().inspect_home(self.home)
            self.assertEqual(('valid', 'unreadable'), (inspected.primary.status, inspected.backup.status))
            self.assertFalse(inspected.can_restore); self.assertNotIn('new', inspected.actions)
            resumed = authority().resume_session(inspected)
        self.assertEqual(original.state, resumed.state)
        self.assertEqual(before, inventory(self.root))

    def test_recovery_checks_exact_buffers_inside_its_read_boundary(self):
        for target in ('backup', 'primary'):
            with self.subTest(target=target):
                self.pair(); inspected = authority().inspect_home(self.home)
                original = CompanionSession.recover_backup.__func__
                actual_read = Path.read_bytes; altered = False
                def changed_read(path):
                    nonlocal altered
                    if path == self.backup and not altered:
                        altered = True
                        destination = self.backup if target == 'backup' else self.path
                        destination.write_bytes(actual_read(destination) + b' ')
                    return actual_read(path)
                def changed_boundary(cls, path, **kwargs):
                    with patch.object(Path, 'read_bytes', changed_read): return original(cls, path, **kwargs)
                with patch.object(CompanionSession, 'recover_backup', classmethod(changed_boundary)):
                    with self.assertRaisesRegex(ValueError, 'changed'): authority().restore_session(inspected)
                self.assertFalse(list(self.home.glob('*.before-recovery-*.json')))
                self.assertEqual(2, len(inventory(self.root)))

    def test_recovery_write_refusal_preserves_both_original_files(self):
        self.pair(); inspected = authority().inspect_home(self.home)
        primary, backup = self.path.read_bytes(), self.backup.read_bytes()
        with patch('mecha_game.session.os.replace', side_effect=PermissionError('injected write denial')):
            with self.assertRaises(OSError): authority().restore_session(inspected)
        self.assertEqual(primary, self.path.read_bytes()); self.assertEqual(backup, self.backup.read_bytes())
        self.assertTrue(any(p.read_bytes() == primary for p in self.home.glob('*.before-recovery-*.json')))
        self.assertFalse(list(self.home.glob('*.tmp')))

    def test_new_checkpoint_write_refusal_preserves_originals_for_visible_retry(self):
        self.pair(); primary, backup = self.path.read_bytes(), self.backup.read_bytes()
        prepared = authority().explicit_new_session(self.path, *self.inputs, None, inspection=authority().inspect_home(self.home))
        life_id = prepared.lineage[-1]['life_id']
        with patch('mecha_game.session.os.replace', side_effect=PermissionError('injected home write denial')):
            with self.assertRaises(OSError): prepared.save_checkpoint(self.path)
        self.assertEqual(primary, self.path.read_bytes()); self.assertEqual(backup, self.backup.read_bytes())
        prepared.save_checkpoint(self.path)
        self.assertEqual(life_id, CompanionSession.load(self.path).lineage[-1]['life_id'])
        originals = {p.read_bytes() for p in self.home.glob('*.replaced-*.json')}
        self.assertTrue({primary, backup}.issubset(originals))


if __name__ == '__main__':
    unittest.main()
