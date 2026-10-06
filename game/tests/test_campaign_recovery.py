"""X1: campaign continuity, explicit paired recovery and journal boundaries."""
import copy
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for folder in ('game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT / folder))
from mecha_game.campaign import KeeperCampaign, TINY_ERA_CONFIG, load_campaign_inputs
from mecha_game.covenant import apply_covenant_change
from mecha_game.covenant_io import import_covenant
from mecha_game.era_plan import EraPlan, state_digest


def files(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*') if p.is_file()}


class CampaignRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_campaign_inputs(ROOT/'data/seed_grids_16x16',
            ROOT/'data/slips/valid/slip_v2_cleanliness.json',
            ROOT/'data/readability_benchmark/adopted_readability_model.json',
            repair_epochs=6, seed_limit=12)
        cls.first = KeeperCampaign(cls.inputs, campaign_id='x1_keeper', era_config=TINY_ERA_CONFIG)
        cls.first.advance_era('calm')
        cls.second = copy.deepcopy(cls.first)
        cls.second.advance_era('storm', record_original=True)

    def seed(self, root, campaign=None):
        state, ledger = root/'campaign_state.json', root/'campaign.sqlite3'
        campaign = copy.deepcopy(campaign or self.first)
        campaign.save(ledger)
        campaign.save_state(state)
        return state, ledger

    def test_malformed_supported_state_is_readable_and_never_mutates_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); state, ledger = self.seed(root)
            good = json.loads(state.read_text())
            old = copy.deepcopy(good); old.pop('base_covenant_source', None)
            state.write_text(json.dumps(old), encoding='utf-8'); old_bytes = files(root)
            self.assertIsNone(KeeperCampaign.load_state(self.inputs, state, ledger).base_covenant_source)
            self.assertEqual(old_bytes, files(root))
            variants = [[], {'state_format': KeeperCampaign.STATE_FORMAT}]
            for field in good:
                if field in ('base_parameters', 'base_covenant_source'): continue  # documented legacy optional fields
                bad = copy.deepcopy(good); bad.pop(field); variants.append(bad)
            for field, value in [('era_count', True), ('era_count', -1), ('campaign_id', ''),
                    ('base_seed', 'bad'), ('unlocks', {}), ('era_config', {}),
                    ('base_parameters', []), ('slip_profile', {}), ('status', 'lost')]:
                bad = copy.deepcopy(good); bad[field] = value; variants.append(bad)
            for bad in variants:
                with self.subTest(payload=bad):
                    state.write_text(json.dumps(bad), encoding='utf-8'); before = files(root)
                    with self.assertRaises(ValueError): KeeperCampaign.load_state(self.inputs, state, ledger)
                    self.assertEqual(before, files(root))

    def test_ledger_identity_position_and_unlock_mismatch_refuse_without_writes(self):
        sql_faults = {
            'identity': "UPDATE campaigns SET campaign_id='foreign'",
            'label': "UPDATE campaigns SET keeper_label='foreign'",
            'status': "UPDATE campaigns SET status='retired'",
            'seed': 'UPDATE eras SET rng_seed=rng_seed+1',
            'gap': 'UPDATE eras SET era_index=3',
            'unlock': "UPDATE unlocks SET metric_value='999'",
            'elite_count': 'DELETE FROM elites',
            'elite_grid': "UPDATE elites SET elite_json=json_set(elite_json, '$.grid', json_object('grid_id', grid_id))",
        }
        for fault in ('missing', 'truncated', 'ahead', 'behind', *sql_faults):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); state, ledger = self.seed(root)
                if fault == 'missing': ledger.unlink()
                elif fault == 'truncated': ledger.write_bytes(b'SQLite format')
                elif fault in ('ahead', 'behind'):
                    value = json.loads(state.read_text()); value['era_count'] += 1 if fault == 'ahead' else -1
                    state.write_text(json.dumps(value), encoding='utf-8')
                else:
                    with closing(sqlite3.connect(ledger)) as conn, conn: conn.execute(sql_faults[fault])
                before = files(root)
                with self.assertRaises(ValueError): KeeperCampaign.load_state(self.inputs, state, ledger)
                self.assertEqual(before, files(root))

    def test_imported_base_survives_successor_spend_reset_and_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); parent = copy.deepcopy(self.first)
            result = import_covenant(parent, ROOT/'data/slips/valid/slip_lcd_seed.json')
            self.assertTrue(result['ok']); new_base = copy.deepcopy(parent.base_profile)
            self.assertNotEqual(self.inputs['slip_profile'], new_base)
            budget = parent.budget()
            self.assertTrue(apply_covenant_change(parent, population=budget['population_cap'])['ok'])
            parent.campaign['status'] = 'extinct'
            state, ledger = self.seed(root, parent)
            parent = KeeperCampaign.load_state(self.inputs, state, ledger)
            successor = parent.successor()
            self.assertEqual(new_base, successor.base_profile)
            self.assertEqual(new_base, successor.campaign['slip_profile'])
            self.assertEqual(parent.base_parameters['population'], successor.era_config['population'])
            self.assertEqual(parent.unlock_state(), successor.inherited_unlocks)
            self.assertEqual([], successor.unlocks)
            self.assertEqual(parent.budget(), successor.budget())
            successor.save(ledger); successor.save_state(state)
            resumed = KeeperCampaign.load_state(self.inputs, state, ledger)
            self.assertEqual(successor.state_payload(), resumed.state_payload())
            self.assertEqual(new_base, resumed.base_profile)

    def test_legacy_base_parameter_interpretation_and_read_bytes_survive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); state, ledger = self.seed(root)
            value = json.loads(state.read_text()); value.pop('base_parameters')
            state.write_text(json.dumps(value), encoding='utf-8'); before = files(root)
            resumed = KeeperCampaign.load_state(self.inputs, state, ledger)
            self.assertEqual(value['era_config']['population'], resumed.base_parameters['population'])
            self.assertEqual(before, files(root))

    def test_pending_missing_prefix_or_altered_metadata_never_reconstructs_history(self):
        for fault in ('missing', 'gap', 'label', 'unlock'):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); state, ledger = self.seed(root)
                plan = EraPlan(root/'era_plan.json'); plan.begin(self.second, self.second.eras[-1], state_digest(state))
                if fault == 'missing': ledger.unlink()
                else:
                    sql = {'gap': 'DELETE FROM eras', 'label': "UPDATE campaigns SET keeper_label='other'",
                           'unlock': "UPDATE unlocks SET metric_value='999'"}[fault]
                    with closing(sqlite3.connect(ledger)) as conn, conn: conn.execute(sql)
                before = files(root)
                with self.assertRaises(ValueError): plan.finish(ledger, state)
                self.assertEqual(before, files(root))

    def test_snapshot_restore_is_explicit_identity_checked_and_preserves_originals(self):
        from mecha_game.campaign_recovery import save_campaign_checkpoint, inspect_campaign_backup, recover_campaign_backup
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); state, ledger = self.seed(root)
            expected = state.read_bytes(); save_campaign_checkpoint(state, ledger)
            preview = inspect_campaign_backup(state, ledger); before = files(root)
            save_campaign_checkpoint(state, ledger); self.assertEqual(before, files(root))
            state.write_bytes(b'broken primary'); ledger.write_bytes(b'broken ledger'); broken = files(root)
            with self.assertRaises(ValueError):
                recover_campaign_backup(state, ledger, expected_manifest_digest=preview['manifest_digest'], expected_campaign_id='unrelated')
            self.assertEqual(broken, files(root))
            recover_campaign_backup(state, ledger, expected_manifest_digest=preview['manifest_digest'], expected_campaign_id='x1_keeper')
            self.assertEqual(expected, state.read_bytes())
            self.assertEqual(self.first.state_payload(), KeeperCampaign.load_state(self.inputs, state, ledger).state_payload())
            recovered = list(files(root).values())
            self.assertIn(b'broken primary', recovered); self.assertIn(b'broken ledger', recovered)

    def test_snapshot_corruption_and_stale_preview_are_refused(self):
        from mecha_game.campaign_recovery import save_campaign_checkpoint, inspect_campaign_backup, recover_campaign_backup
        for fault in ('stale', 'ledger'):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); state, ledger = self.seed(root)
                save_campaign_checkpoint(state, ledger); preview = inspect_campaign_backup(state, ledger)
                if fault == 'stale':
                    marker = root/'campaign_recovery.json'; marker.write_bytes(marker.read_bytes()+b' ')
                else: Path(preview['ledger_path']).write_bytes(b'broken snapshot')
                before = files(root)
                with self.assertRaises(ValueError):
                    recover_campaign_backup(state, ledger, expected_manifest_digest=preview['manifest_digest'])
                self.assertEqual(before, files(root))

    def test_interrupted_restore_is_blocked_until_explicit_retry(self):
        from mecha_game.campaign_recovery import save_campaign_checkpoint, inspect_campaign_backup, recover_campaign_backup
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); state, ledger = self.seed(root)
            save_campaign_checkpoint(state, ledger); preview = inspect_campaign_backup(state, ledger)
            state.write_bytes(b'broken primary'); ledger.write_bytes(b'broken ledger')
            original = os.replace
            def replace(source, destination):
                if Path(destination) == state: raise PermissionError('state locked')
                return original(source, destination)
            with patch('mecha_game.session.os.replace', replace), self.assertRaises(OSError):
                recover_campaign_backup(state, ledger, expected_manifest_digest=preview['manifest_digest'])
            before = files(root)
            with self.assertRaisesRegex(ValueError, 'recovery|restore'): KeeperCampaign.load_state(self.inputs, state, ledger)
            self.assertEqual(before, files(root))
            recover_campaign_backup(state, ledger, expected_manifest_digest=preview['manifest_digest'])
            KeeperCampaign.load_state(self.inputs, state, ledger)
            self.assertIn(b'broken primary', files(root).values()); self.assertIn(b'broken ledger', files(root).values())

    def test_snapshot_failure_retries_completed_result_without_evolution_or_duplicate_rows(self):
        from mecha_game.campaign_recovery import inspect_campaign_backup
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); state, ledger = self.seed(root)
            plan = EraPlan(root/'era_plan.json'); plan.begin(self.second, self.second.eras[-1], state_digest(state))
            original = os.replace
            def replace(source, destination):
                if Path(destination).name == 'campaign_recovery.json': raise PermissionError('snapshot locked')
                return original(source, destination)
            with patch('mecha_game.session.os.replace', replace), self.assertRaises(OSError): plan.finish(ledger, state)
            self.assertIsNotNone(EraPlan(plan.path).pending)
            with patch('mecha_game.campaign.evolve', side_effect=AssertionError('must not rerun evolution')):
                EraPlan(plan.path).finish(ledger, state)
            self.assertIsNone(EraPlan(plan.path).pending)
            self.assertEqual(2, inspect_campaign_backup(state, ledger)['era_count'])
            with closing(sqlite3.connect(ledger)) as conn:
                self.assertEqual(2, conn.execute('SELECT count(*) FROM eras').fetchone()[0])
                self.assertEqual(1, conn.execute('SELECT count(*) FROM replays').fetchone()[0])
                self.assertEqual(len(self.second.unlocks), conn.execute('SELECT count(*) FROM unlocks').fetchone()[0])
            resumed = KeeperCampaign.load_state(self.inputs, state, ledger)
            self.assertEqual(self.second.unlocks, resumed.unlocks)

    def test_malformed_checksummed_completion_preserves_every_file(self):
        from mecha_game.era_plan import _digest
        for field in ('summary', 'decision', 'elite_grid', 'invalid_elite_grid', 'elite_count', 'previous_state', 'extinction'):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); path = root/'era_plan.json'
                plan = EraPlan(path); plan.begin(self.first, self.first.eras[-1], None)
                value = json.loads(path.read_text()); pending = value['pending']
                if field in ('summary', 'decision'): pending['era']['report'].pop(field)
                elif field == 'elite_grid': pending['era']['elites'][0].pop('grid')
                elif field == 'invalid_elite_grid': pending['era']['elites'][0]['grid'] = {'grid_id': pending['era']['elites'][0]['grid_id']}
                elif field == 'elite_count': pending['era']['elites'].pop()
                elif field == 'previous_state': pending['previous_state'] = 3
                else: pending['era']['derived']['went_extinct'] = True
                pending['sha256'] = _digest({key: item for key, item in pending.items() if key != 'sha256'})
                path.write_text(json.dumps(value), encoding='utf-8'); before = files(root)
                with self.assertRaises(ValueError): EraPlan(path).finish(root/'campaign.sqlite3', root/'campaign_state.json')
                self.assertEqual(before, files(root))

    def test_explicit_restore_preserves_pending_then_finishes_it_once(self):
        from mecha_game.campaign_recovery import save_campaign_checkpoint, inspect_campaign_backup, recover_campaign_backup
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); state, ledger = self.seed(root)
            save_campaign_checkpoint(state, ledger); preview = inspect_campaign_backup(state, ledger)
            plan = EraPlan(root/'era_plan.json'); plan.begin(self.second, self.second.eras[-1], state_digest(state))
            pending_bytes = plan.path.read_bytes(); ledger.unlink(); state.unlink()
            recover_campaign_backup(state, ledger, expected_manifest_digest=preview['manifest_digest'])
            self.assertEqual(pending_bytes, plan.path.read_bytes())
            with patch('mecha_game.campaign.evolve', side_effect=AssertionError('must not rerun evolution')):
                EraPlan(plan.path).finish(ledger, state)
            self.assertEqual(2, KeeperCampaign.load_state(self.inputs, state, ledger).era_offset)
            self.assertIsNone(EraPlan(plan.path).pending)

    def test_retention_keeps_two_verified_snapshots_and_unknown_files(self):
        from mecha_game.campaign_recovery import save_campaign_checkpoint, inspect_campaign_backup
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); state, ledger = self.seed(root)
            save_campaign_checkpoint(state, ledger)
            unknown = root/'.campaign-recovery'/'owner-notes.txt'; unknown.write_bytes(b'owner bytes')
            self.second.save(ledger); self.second.save_state(state); save_campaign_checkpoint(state, ledger)
            third = copy.deepcopy(self.second); third.advance_era('calm')
            third.save(ledger); third.save_state(state); save_campaign_checkpoint(state, ledger)
            self.assertEqual(3, inspect_campaign_backup(state, ledger)['era_count'])
            self.assertEqual(2, inspect_campaign_backup(state, ledger, slot='previous')['era_count'])
            self.assertEqual(2, len(list((root/'.campaign-recovery').glob('*.sqlite3'))))
            self.assertEqual(b'owner bytes', unknown.read_bytes())

    def test_missing_invalid_backup_is_explicit_and_read_only(self):
        from mecha_game.campaign_recovery import inspect_campaign_backup, has_campaign_evidence
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); state, ledger = root/'campaign_state.json', root/'campaign.sqlite3'
            self.assertFalse(has_campaign_evidence(state, ledger))
            with self.assertRaises(ValueError): inspect_campaign_backup(state, ledger)
            self.assertEqual({}, files(root))
            state.with_suffix('.bak.json').write_bytes(b'not a coherent pair')
            self.assertTrue(has_campaign_evidence(state, ledger)); before = files(root)
            with self.assertRaises(ValueError): inspect_campaign_backup(state, ledger)
            self.assertEqual(before, files(root))
            (root/'campaign_recovery.json').write_bytes(b'broken manifest'); before = files(root)
            with self.assertRaises(ValueError): inspect_campaign_backup(state, ledger)
            self.assertEqual(before, files(root))

    def test_inherited_facts_cannot_silently_disagree_with_predecessor(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); parent = copy.deepcopy(self.first); parent.campaign['status'] = 'extinct'
            state, ledger = self.seed(root, parent); child = parent.successor()
            child.save(ledger); child.save_state(state)
            value = json.loads(state.read_text()); value['inherited_unlocks'] = []
            self.assertTrue(child.inherited_unlocks)
            state.write_text(json.dumps(value), encoding='utf-8'); before = files(root)
            with self.assertRaises(ValueError): KeeperCampaign.load_state(self.inputs, state, ledger)
            self.assertEqual(before, files(root))

    def test_first_ever_completed_journal_can_still_create_its_ledger(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); plan = EraPlan(root/'era_plan.json')
            plan.begin(self.first, self.first.eras[-1], None)
            plan.finish(root/'campaign.sqlite3', root/'campaign_state.json')
            loaded = KeeperCampaign.load_state(self.inputs, root/'campaign_state.json', root/'campaign.sqlite3')
            self.assertEqual(self.first.state_payload(), loaded.state_payload())


if __name__ == '__main__': unittest.main()
