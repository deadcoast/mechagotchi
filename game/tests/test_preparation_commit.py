"""Captured preparation is persistence evidence, never earned/extinction evidence."""
import copy
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for folder in ('game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT/folder))
from mecha_game.campaign import KeeperCampaign, TINY_ERA_CONFIG
from mecha_game.campaign_recovery import (initialize_campaign_checkpoint, inspect_campaign_backup,
    recover_campaign_backup, validate_ledger_state)
from mecha_game.era_plan import EraPlan, state_digest
from mecha_game.preparation_commit import PreparationCommit


def files(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*') if p.is_file()}


class PreparationCommitTests(unittest.TestCase):
    def campaign(self):
        profile = json.loads((ROOT/'data/slips/valid/slip_v2_cleanliness.json').read_text())
        return KeeperCampaign({'slip_profile': profile}, campaign_id='preparation_keeper', era_config=TINY_ERA_CONFIG)

    def setup_pair(self, root, *, extinct=False):
        campaign = self.campaign()
        state, ledger = root/'campaign_state.json', root/'campaign.sqlite3'
        if extinct:
            # Explicit synthetic zero-era extinct fixture tests only persistence guards.
            campaign.campaign['status'] = 'extinct'
            campaign.save(ledger); campaign.save_state(state)
            from mecha_game.campaign_recovery import save_campaign_checkpoint
            save_campaign_checkpoint(state, ledger)
        else:
            initialize_campaign_checkpoint(campaign, state, ledger)
        return campaign, state, ledger

    def target(self, source):
        target = copy.deepcopy(source)
        target.base_profile['name'] = 'Explicitly imported covenant'
        target.campaign['slip_profile'] = copy.deepcopy(target.base_profile)
        return target

    def begin(self, state, ledger, target, *, kind='covenant', source_campaign_id='preparation_keeper'):
        transaction = PreparationCommit(state, ledger)
        transaction.begin(target, kind=kind, source_campaign_id=source_campaign_id,
            expected_state_digest=state_digest(state), expected_ledger_digest=state_digest(ledger),
            summary='Imported covenant' if kind == 'covenant' else 'Created successor')
        return transaction

    def finish(self, transaction):
        return transaction.finish(expected_journal_digest=transaction.journal_digest,
                                  expected_campaign_id='preparation_keeper')

    def test_begin_captures_target_without_touching_primaries_or_checkpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); campaign, state, ledger = self.setup_pair(root)
            self.assertEqual({'state', 'state_bytes', 'ledger_path', 'ledger_bytes', 'campaign_id',
                'era_count', 'manifest_digest', 'slot'}, set(inspect_campaign_backup(state, ledger)))
            original = files(root); target = self.target(campaign)
            transaction = self.begin(state, ledger, target)
            for name, raw in original.items(): self.assertEqual(raw, (root/name).read_bytes(), name)
            self.assertEqual('covenant', transaction.pending['kind'])
            self.assertEqual('Imported covenant', transaction.pending['summary'])
            with self.assertRaisesRegex(ValueError, 'preparation'): transaction.require_ready()
            target.base_profile['name'] = 'later in-memory edit'
            completed = self.finish(transaction)
            self.assertEqual('Explicitly imported covenant', completed['base_profile']['name'])
            self.assertIsNone(self.finish(transaction))
            self.assertIsNone(transaction.pending)
            validate_ledger_state(completed, ledger)
            current = inspect_campaign_backup(state, ledger)
            previous = inspect_campaign_backup(state, ledger, slot='previous')
            self.assertEqual(completed, current['state'])
            self.assertEqual(json.loads(original[state.name]), previous['state'])
            for name, raw in original.items():
                if name not in (state.name, ledger.name, 'campaign_recovery.json'):
                    self.assertEqual(raw, (root/name).read_bytes(), name)
            self.assertTrue(any(p.read_bytes() == original[state.name] for p in transaction.directory.rglob('*') if p.is_file()))
            self.assertTrue(any(p.read_bytes() == original[ledger.name] for p in transaction.directory.rglob('*') if p.is_file()))

    def test_interruption_at_every_finish_boundary_retries_exact_target(self):
        for boundary in ('snapshot', 'ledger', 'state', 'checkpoint', 'archive', 'clear'):
            with self.subTest(boundary=boundary), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); campaign, state, ledger = self.setup_pair(root, extinct=True)
                target = campaign.successor(); transaction = self.begin(state, ledger, target, kind='successor')
                original_replace = os.replace; original_unlink = Path.unlink
                hit = []
                def replace(source, destination):
                    destination = Path(destination)
                    match = ((boundary == 'snapshot' and destination.parent == root/'.campaign-recovery') or
                        (boundary == 'ledger' and destination == ledger) or (boundary == 'state' and destination == state) or
                        (boundary == 'checkpoint' and destination == root/'campaign_recovery.json') or
                        (boundary == 'archive' and destination.parent == transaction.directory/'completed'))
                    if match: hit.append(boundary); raise PermissionError('injected '+boundary)
                    return original_replace(source, destination)
                def unlink(path, *args, **kwargs):
                    if boundary == 'clear' and path == transaction.path:
                        hit.append(boundary); raise PermissionError('injected clear')
                    return original_unlink(path, *args, **kwargs)
                with patch('mecha_game.session.os.replace', replace), patch.object(Path, 'unlink', unlink):
                    with self.assertRaises(OSError): self.finish(transaction)
                self.assertTrue(hit)
                restart = PreparationCommit(state, ledger)
                self.assertIsNone(restart.error); self.assertIsNotNone(restart.pending)
                with (patch.object(KeeperCampaign, 'save', side_effect=AssertionError('retry reran writer')),
                     patch.object(KeeperCampaign, 'successor', side_effect=AssertionError('retry created another successor'))):
                    result = self.finish(restart)
                self.assertEqual(target.state_payload(), result)
                self.assertEqual(result, KeeperCampaign.load_state(campaign.inputs, state, ledger).state_payload())
                with closing(sqlite3.connect(ledger)) as conn:
                    self.assertEqual(2, conn.execute('SELECT count(*) FROM campaigns').fetchone()[0])
                self.assertIsNone(self.finish(restart))

    def test_begin_capture_failure_never_changes_existing_pair(self):
        for boundary in ('target', 'blob', 'journal'):
            with self.subTest(boundary=boundary), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); campaign, state, ledger = self.setup_pair(root)
                original = files(root); original_replace = os.replace
                def replace(source, destination):
                    destination = Path(destination)
                    if ((boundary == 'blob' and destination.parent.name == 'blobs') or
                        (boundary == 'journal' and destination == root/'campaign_preparation.json')):
                        raise PermissionError('injected '+boundary)
                    return original_replace(source, destination)
                with patch('mecha_game.session.os.replace', replace):
                    if boundary == 'target':
                        with patch.object(KeeperCampaign, 'save', side_effect=PermissionError('target locked')):
                            with self.assertRaises(OSError): self.begin(state, ledger, self.target(campaign))
                    else:
                        with self.assertRaises(OSError): self.begin(state, ledger, self.target(campaign))
                for name, raw in original.items(): self.assertEqual(raw, (root/name).read_bytes(), name)
                self.assertFalse((root/'campaign_preparation.json').exists())

    def test_first_covenant_with_absent_primaries_is_captured_and_explicitly_finished(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); state = root/'campaign_state.json'; ledger = root/'campaign.sqlite3'
            transaction = self.begin(state, ledger, self.target(self.campaign()))
            self.assertFalse(state.exists()); self.assertFalse(ledger.exists())
            self.finish(transaction)
            self.assertEqual('Explicitly imported covenant', KeeperCampaign.load_state(self.campaign().inputs, state, ledger).base_profile['name'])

    def test_external_primary_and_checkpoint_conflicts_refuse_before_any_write(self):
        for name in ('campaign_state.json', 'campaign.sqlite3', 'campaign_recovery.json'):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); campaign, state, ledger = self.setup_pair(root)
                transaction = self.begin(state, ledger, self.target(campaign))
                (root/name).write_bytes(b'external owner bytes'); before = files(root)
                with self.assertRaisesRegex(ValueError, 'changed|conflict'): self.finish(transaction)
                self.assertEqual(before, files(root))

    def test_all_sqlite_sidecars_refuse_without_mutation(self):
        for suffix in ('-wal', '-journal', '-shm'):
            for phase in ('begin', 'finish'):
                with self.subTest(suffix=suffix, phase=phase), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory); campaign, state, ledger = self.setup_pair(root)
                    if phase == 'finish': transaction = self.begin(state, ledger, self.target(campaign))
                    ledger.with_name(ledger.name+suffix).write_bytes(b'active writer'); before = files(root)
                    with self.assertRaisesRegex(ValueError, 'SQLite'):
                        if phase == 'begin': self.begin(state, ledger, self.target(campaign))
                        else: self.finish(transaction)
                    self.assertEqual(before, files(root))

    def test_identity_stale_preview_and_changed_journal_are_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); campaign, state, ledger = self.setup_pair(root)
            transaction = PreparationCommit(state, ledger); before = files(root)
            with self.assertRaisesRegex(ValueError, 'identity|Keeper'):
                transaction.begin(self.target(campaign), kind='covenant', source_campaign_id='foreign',
                    expected_state_digest=state_digest(state), expected_ledger_digest=state_digest(ledger))
            self.assertEqual(before, files(root))
            transaction = self.begin(state, ledger, self.target(campaign)); before = files(root)
            for kwargs in ({'expected_journal_digest': '0'*64, 'expected_campaign_id': 'preparation_keeper'},
                           {'expected_journal_digest': transaction.journal_digest, 'expected_campaign_id': 'foreign'}):
                with self.assertRaises(ValueError): transaction.finish(**kwargs)
                self.assertEqual(before, files(root))
            transaction.path.write_bytes(b'{malformed'); changed = files(root); transaction.refresh()
            self.assertEqual(hashlib.sha256(b'{malformed').hexdigest(), transaction.journal_digest)
            self.assertIsNotNone(transaction.error)
            with self.assertRaises(ValueError): self.finish(transaction)
            self.assertEqual(changed, files(root))

    def test_corrupt_captured_bytes_refuse_without_overwriting_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); campaign, state, ledger = self.setup_pair(root)
            transaction = self.begin(state, ledger, self.target(campaign))
            blob = next((transaction.directory/'blobs').iterdir()); blob.write_bytes(b'corrupt capture')
            before = files(root); transaction.refresh()
            self.assertIsNotNone(transaction.error)
            with self.assertRaises(ValueError): self.finish(transaction)
            self.assertEqual(before, files(root))

    def test_pending_preparation_blocks_normal_load_new_checkpoint_and_era_finish(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); campaign, state, ledger = self.setup_pair(root)
            self.begin(state, ledger, self.target(campaign)); before = files(root)
            from mecha_game.campaign_recovery import save_campaign_checkpoint
            for operation in (lambda: KeeperCampaign.load_state(campaign.inputs, state, ledger),
                              lambda: save_campaign_checkpoint(state, ledger)):
                with self.assertRaisesRegex(ValueError, 'preparation'): operation()
            self.assertEqual(before, files(root))

    def test_explicit_paired_recovery_preserves_and_supersedes_even_malformed_journal(self):
        for malformed in (False, True):
            with self.subTest(malformed=malformed), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); campaign, state, ledger = self.setup_pair(root)
                transaction = self.begin(state, ledger, self.target(campaign))
                if malformed: transaction.path.write_bytes(b'{malformed')
                transaction.refresh(); raw = transaction.path.read_bytes(); digest = transaction.journal_digest
                preview = inspect_campaign_backup(state, ledger)
                recover_campaign_backup(state, ledger, expected_manifest_digest=preview['manifest_digest'],
                                        expected_campaign_id='preparation_keeper')
                transaction.resolve_after_recovery(expected_journal_digest=digest,
                    restored_state_digest=state_digest(state), restored_ledger_digest=state_digest(ledger))
                self.assertIsNone(transaction.pending); self.assertIsNone(transaction.error)
                self.assertEqual(campaign.state_payload(), KeeperCampaign.load_state(campaign.inputs, state, ledger).state_payload())
                self.assertTrue(any(path.read_bytes() == raw for path in transaction.directory.rglob('*') if path.is_file()))

    def test_resolution_requires_verified_paired_checkpoint_and_exact_primary_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); campaign, state, ledger = self.setup_pair(root)
            transaction = self.begin(state, ledger, self.target(campaign)); before = files(root)
            with self.assertRaises(ValueError):
                transaction.resolve_after_recovery(expected_journal_digest=transaction.journal_digest,
                    restored_state_digest='0'*64, restored_ledger_digest=state_digest(ledger))
            self.assertEqual(before, files(root))

    def test_fresh_python_process_finishes_without_original_operation_or_models(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); campaign, state, ledger = self.setup_pair(root)
            transaction = self.begin(state, ledger, self.target(campaign)); digest = transaction.journal_digest
            script = ('from pathlib import Path; from mecha_game.preparation_commit import PreparationCommit; '
                'import sys,json; t=PreparationCommit(Path(sys.argv[1]),Path(sys.argv[2])); '
                "r=t.finish(expected_journal_digest=sys.argv[3],expected_campaign_id='preparation_keeper'); "
                "print(json.dumps({'campaign_id':r['campaign_id'],'name':r['base_profile']['name']}))")
            env = os.environ.copy(); env['PYTHONPATH'] = os.pathsep.join([str(ROOT/'game/src'),
                str(ROOT/'packages/mecha_engine/src'), env.get('PYTHONPATH', '')])
            result = subprocess.run([sys.executable, '-B', '-c', script, str(state), str(ledger), digest],
                env=env, capture_output=True, text=True, timeout=20)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual('Explicitly imported covenant', json.loads(result.stdout)['name'])


    def test_current_and_prior_checkpoint_snapshots_survive_successor_rotation(self):
        from mecha_game.campaign_recovery import save_campaign_checkpoint, _record_bytes
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); campaign, state, ledger = self.setup_pair(root)
            campaign.campaign['status'] = 'extinct'  # synthetic persistence fixture only
            campaign.save(ledger); campaign.save_state(state); save_campaign_checkpoint(state, ledger)
            old_manifest = (root/'campaign_recovery.json').read_bytes()
            old = json.loads(old_manifest)
            self.assertNotEqual(old['current']['ledger_sha256'], old['previous']['ledger_sha256'])
            old_snapshots = {p.name: p.read_bytes() for p in (root/'.campaign-recovery').glob('*.sqlite3')}
            transaction = self.begin(state, ledger, campaign.successor(), kind='successor')
            self.finish(transaction)
            for name, raw in old_snapshots.items(): self.assertEqual(raw, (root/'.campaign-recovery'/name).read_bytes())
            for record in (old['current'], old['previous']): _record_bytes(record, root/'.campaign-recovery')
            self.assertTrue(any(p.read_bytes() == old_manifest for p in transaction.directory.rglob('*') if p.is_file()))

    def test_integrated_recovery_interruption_keeps_exact_retry_marker(self):
        for boundary in ('archive_preparation', 'clear_preparation', 'clear_recovery'):
            with self.subTest(boundary=boundary), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); campaign, state, ledger = self.setup_pair(root)
                transaction = self.begin(state, ledger, self.target(campaign))
                transaction.path.write_bytes(b'{malformed preserved preparation')
                transaction.refresh(); digest = transaction.journal_digest
                preview = inspect_campaign_backup(state, ledger)
                self.assertEqual(digest, preview['preparation_digest'])
                original_replace, original_unlink = os.replace, Path.unlink
                def replace(source, destination):
                    if boundary == 'archive_preparation' and Path(destination).parent == transaction.directory/'recovered':
                        raise PermissionError('injected recovered archive')
                    return original_replace(source, destination)
                def unlink(path, *args, **kwargs):
                    if ((boundary == 'clear_preparation' and path == transaction.path) or
                        (boundary == 'clear_recovery' and path == root/'campaign_restore.json')):
                        raise PermissionError('injected marker clear')
                    return original_unlink(path, *args, **kwargs)
                with patch('mecha_game.session.os.replace', replace), patch.object(Path, 'unlink', unlink):
                    with self.assertRaises(OSError):
                        recover_campaign_backup(state, ledger, expected_manifest_digest=preview['manifest_digest'],
                            expected_campaign_id='preparation_keeper', expected_preparation_digest=digest)
                self.assertTrue((root/'campaign_restore.json').exists())
                restart = inspect_campaign_backup(state, ledger)
                self.assertEqual(digest, restart['preparation_digest'])
                recover_campaign_backup(state, ledger, expected_manifest_digest=restart['manifest_digest'],
                    expected_campaign_id='preparation_keeper', expected_preparation_digest=restart['preparation_digest'])
                self.assertFalse(transaction.path.exists()); self.assertFalse((root/'campaign_restore.json').exists())
                self.assertEqual(campaign.state_payload(), KeeperCampaign.load_state(campaign.inputs, state, ledger).state_payload())

    def test_recovery_rejects_changed_preparation_pin_before_primary_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); campaign, state, ledger = self.setup_pair(root)
            transaction = self.begin(state, ledger, self.target(campaign))
            preview = inspect_campaign_backup(state, ledger)
            transaction.path.write_bytes(b'changed owner journal'); before = files(root)
            with self.assertRaisesRegex(ValueError, 'changed'):
                recover_campaign_backup(state, ledger, expected_manifest_digest=preview['manifest_digest'],
                    expected_preparation_digest=preview['preparation_digest'])
            self.assertEqual(before, files(root))

    def test_absent_primaries_with_existing_legacy_backup_are_never_fresh(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); state = root/'campaign_state.json'; ledger = root/'campaign.sqlite3'
            state.with_suffix('.bak.json').write_bytes(b'owner saved backup'); before = files(root)
            with self.assertRaisesRegex(ValueError, 'evidence'):
                self.begin(state, ledger, self.target(self.campaign()))
            self.assertEqual(before, files(root))

    def test_external_change_during_begin_capture_and_finish_is_preserved(self):
        for phase in ('begin', 'finish'):
            with self.subTest(phase=phase), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); campaign, state, ledger = self.setup_pair(root)
                from mecha_game import preparation_commit
                original = preparation_commit._write_bytes_atomic
                if phase == 'finish': transaction = self.begin(state, ledger, self.target(campaign))
                injected = []
                def concurrent(path, raw):
                    original(path, raw)
                    if ((phase == 'begin' and path.parent.name == 'blobs') or
                        (phase == 'finish' and path == state)) and not injected:
                        injected.append(True); ledger.write_bytes(b'owner changed ledger')
                with patch.object(preparation_commit, '_write_bytes_atomic', concurrent):
                    with self.assertRaisesRegex(ValueError, 'changed'):
                        if phase == 'begin': self.begin(state, ledger, self.target(campaign))
                        else: self.finish(transaction)
                self.assertEqual(b'owner changed ledger', ledger.read_bytes())
                if phase == 'begin': self.assertFalse((root/'campaign_preparation.json').exists())
                else: self.assertTrue(transaction.path.exists())

    def test_unrelated_candidate_and_completed_era_preparation_are_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); campaign, state, ledger = self.setup_pair(root)
            for change in ('identity', 'era_count', 'population_policy'):
                candidate = self.target(campaign)
                if change == 'identity': candidate.campaign['campaign_id'] = 'foreign'
                elif change == 'era_count': candidate.era_offset = 1
                else: candidate._population_policy = 'generation_survivors_v1'
                before = files(root)
                with self.assertRaises(ValueError): self.begin(state, ledger, candidate)
                self.assertEqual(before, files(root))
            plan = root/'era_plan.json'; plan.write_bytes(b'{malformed old era journal'); before = files(root)
            with self.assertRaisesRegex(ValueError, 'preparation'): self.begin(state, ledger, self.target(campaign))
            self.assertEqual(before, files(root))


    def test_valid_foreign_or_forged_checkpoint_family_refuses_before_capture(self):
        from mecha_game.campaign_recovery import save_campaign_checkpoint
        for forgery in ('foreign', 'predecessor_label', 'seed'):
            with self.subTest(forgery=forgery), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); campaign, state, ledger = self.setup_pair(root)
                foreign_root = root/'foreign'; foreign_root.mkdir()
                foreign = self.campaign()
                if forgery == 'foreign': foreign.campaign['campaign_id'] = 'unrelated_keeper'
                elif forgery == 'predecessor_label': foreign.campaign['keeper_label'] = 'forged predecessor'
                else: foreign.campaign['base_seed'] += 1
                foreign.campaign['status'] = 'extinct'  # synthetic relationship guard only
                foreign_state, foreign_ledger = foreign_root/state.name, foreign_root/ledger.name
                foreign.save(foreign_ledger); foreign.save_state(foreign_state)
                if forgery == 'predecessor_label':
                    foreign = foreign.successor(); foreign.save(foreign_ledger); foreign.save_state(foreign_state)
                save_campaign_checkpoint(foreign_state, foreign_ledger)
                (root/'campaign_recovery.json').write_bytes((foreign_root/'campaign_recovery.json').read_bytes())
                for snapshot in (foreign_root/'.campaign-recovery').glob('*.sqlite3'):
                    (root/'.campaign-recovery'/snapshot.name).write_bytes(snapshot.read_bytes())
                before = files(root)
                with self.assertRaisesRegex(ValueError, 'checkpoint'):
                    self.begin(state, ledger, self.target(campaign))
                self.assertEqual(before, files(root))

    def test_prior_predecessor_recovery_allows_later_preparation_with_successor_checkpoint_retained(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); campaign, state, ledger = self.setup_pair(root, extinct=True)
            transaction = self.begin(state, ledger, campaign.successor(), kind='successor')
            self.finish(transaction)
            preview = inspect_campaign_backup(state, ledger, slot='previous')
            recover_campaign_backup(state, ledger, expected_manifest_digest=preview['manifest_digest'], slot='previous')
            restored = KeeperCampaign.load_state(campaign.inputs, state, ledger)
            transaction = self.begin(state, ledger, self.target(restored))
            self.finish(transaction)
            self.assertEqual('Explicitly imported covenant', KeeperCampaign.load_state(campaign.inputs, state, ledger).base_profile['name'])
            self.assertEqual('preparation_keeper_successor', inspect_campaign_backup(state, ledger, slot='previous')['campaign_id'])


    def test_pair_paths_and_stale_source_digests_refuse_before_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); campaign, state, ledger = self.setup_pair(root)
            before = files(root)
            for pair in ((state, state), (state, root/'other'/ledger.name),
                         (root/'campaign_restore.json', ledger), (state, root/'era_plan.json')):
                with self.assertRaises(ValueError): PreparationCommit(*pair)
                self.assertEqual(before, files(root))
            transaction = PreparationCommit(state, ledger)
            with self.assertRaisesRegex(ValueError, 'changed'):
                transaction.begin(self.target(campaign), kind='covenant', source_campaign_id='preparation_keeper',
                    expected_state_digest='0'*64, expected_ledger_digest=state_digest(ledger))
            self.assertEqual(before, files(root))


if __name__ == '__main__': unittest.main()
