"""X3 first-creator genesis publishes recovery before any primary file."""
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
for folder in ('game/src','packages/mecha_engine/src'):sys.path.insert(0,str(ROOT/folder))
from mecha_game.campaign import KeeperCampaign,TINY_ERA_CONFIG
from mecha_game import campaign_recovery as recovery


def files(root):
    return {str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file()}


class CampaignInitializationTests(unittest.TestCase):
    def campaign(self):
        profile=json.loads((ROOT/'data/slips/valid/slip_v2_cleanliness.json').read_text())
        return KeeperCampaign({'slip_profile':profile},campaign_id='new_keeper',era_config=TINY_ERA_CONFIG)

    def test_new_campaign_materializes_verified_zero_era_pair_without_other_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);state=root/'campaign_state.json';ledger=root/'campaign.sqlite3'
            unrelated=root/'companion.json';unrelated.write_bytes(b'owner companion bytes')
            campaign=self.campaign()
            result=recovery.initialize_campaign_checkpoint(campaign,state,ledger)
            self.assertEqual('new_keeper',result['campaign_id'])
            self.assertEqual(campaign.state_payload(),json.loads(state.read_text()))
            self.assertEqual(0,recovery.inspect_campaign_backup(state,ledger)['era_count'])
            self.assertFalse((root/'campaign_restore.json').exists())
            self.assertEqual(b'owner companion bytes',unrelated.read_bytes())
            self.assertFalse(list(root.glob('.campaign-init-*')))
            with closing(sqlite3.connect(ledger)) as conn:self.assertEqual(0,conn.execute('SELECT count(*) FROM eras').fetchone()[0])

    def test_each_genesis_failure_leaves_primaries_untouched_or_verified_recovery(self):
        for fault in ('prepare_ledger','prepare_state','snapshot','manifest','ledger','state'):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory() as directory:
                root=Path(directory);state=root/'campaign_state.json';ledger=root/'campaign.sqlite3'
                original=os.replace
                def replace(source,destination):
                    destination=Path(destination)
                    if ((fault=='snapshot' and destination.parent==root/'.campaign-recovery') or
                        (fault=='manifest' and destination==root/'campaign_recovery.json') or
                        (fault=='ledger' and destination==ledger) or
                        (fault=='state' and destination==state)):
                        raise PermissionError('injected '+fault)
                    return original(source,destination)
                target={'prepare_ledger':'save','prepare_state':'save_state'}.get(fault)
                with patch('mecha_game.session.os.replace',replace):
                    if target:
                        with patch.object(KeeperCampaign,target,side_effect=PermissionError('preparation locked')):
                            with self.assertRaises(OSError):recovery.initialize_campaign_checkpoint(self.campaign(),state,ledger)
                    else:
                        with self.assertRaises(OSError):recovery.initialize_campaign_checkpoint(self.campaign(),state,ledger)
                if (root/'campaign_recovery.json').exists():
                    preview=recovery.inspect_campaign_backup(state,ledger)
                    recovery.recover_campaign_backup(state,ledger,expected_manifest_digest=preview['manifest_digest'],expected_campaign_id='new_keeper')
                    self.assertEqual(self.campaign().state_payload(),json.loads(state.read_text()))
                    recovery.validate_ledger_state(json.loads(state.read_text()),ledger)
                else:
                    self.assertFalse(state.exists());self.assertFalse(ledger.exists())
                    recovery.initialize_campaign_checkpoint(self.campaign(),state,ledger)
                    recovery.validate_ledger_state(json.loads(state.read_text()),ledger)
                self.assertFalse(list(root.glob('.campaign-init-*')))

    def test_existing_campaign_evidence_is_never_replaced(self):
        for name in ('campaign_state.json','campaign_state.bak.json','campaign.sqlite3','campaign.sqlite3-wal',
                     'campaign.sqlite3-journal','campaign.sqlite3-shm','campaign_recovery.json','campaign_restore.json',
                     '.campaign-recovery/owner-snapshot.sqlite3','era_plan.json'):
            with self.subTest(name=name),tempfile.TemporaryDirectory() as directory:
                root=Path(directory);target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b'owner evidence')
                before=files(root)
                with self.assertRaises(ValueError):recovery.initialize_campaign_checkpoint(self.campaign(),root/'campaign_state.json',root/'campaign.sqlite3')
                self.assertEqual(before,files(root))

    def test_campaign_appearing_during_preparation_is_preserved_before_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);state=root/'campaign_state.json';ledger=root/'campaign.sqlite3'
            original=recovery.save_campaign_checkpoint
            def concurrent(*args,**kwargs):
                result=original(*args,**kwargs);state.write_bytes(b'external campaign');return result
            with patch.object(recovery,'save_campaign_checkpoint',concurrent):
                with self.assertRaises(ValueError):recovery.initialize_campaign_checkpoint(self.campaign(),state,ledger)
            self.assertEqual({'campaign_state.json':b'external campaign'},files(root))

    def test_external_state_after_snapshot_is_not_overwritten_or_hidden(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);state=root/'campaign_state.json';ledger=root/'campaign.sqlite3'
            original=recovery._write_bytes_atomic
            def concurrent(path,data):
                original(path,data)
                if Path(path).parent==root/'.campaign-recovery':state.write_bytes(b'external campaign')
            with patch.object(recovery,'_write_bytes_atomic',concurrent):
                with self.assertRaises(ValueError):recovery.initialize_campaign_checkpoint(self.campaign(),state,ledger)
            self.assertEqual(b'external campaign',state.read_bytes())
            self.assertFalse(ledger.exists());self.assertFalse((root/'campaign_recovery.json').exists())


    def test_failed_unpublished_attempt_preserves_changed_or_additional_snapshot_evidence(self):
        for mutation in ('changed','additional'):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as directory:
                root=Path(directory);state=root/'campaign_state.json';ledger=root/'campaign.sqlite3'
                original=recovery._write_bytes_atomic
                foreign=None
                def concurrent(path,data):
                    nonlocal foreign
                    original(path,data)
                    if Path(path).parent==root/'.campaign-recovery':
                        foreign=Path(path) if mutation=='changed' else Path(path).parent/'external.sqlite3'
                        foreign.write_bytes(b'external evidence')
                        raise PermissionError('injected after external change')
                with patch.object(recovery,'_write_bytes_atomic',concurrent):
                    with self.assertRaises(OSError):recovery.initialize_campaign_checkpoint(self.campaign(),state,ledger)
                self.assertEqual({str(foreign.relative_to(root)):b'external evidence'},files(root))
                with self.assertRaises(ValueError):recovery.initialize_campaign_checkpoint(self.campaign(),state,ledger)
                self.assertEqual(b'external evidence',foreign.read_bytes())

    def test_external_state_after_manifest_is_preserved_before_materialization(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);state=root/'campaign_state.json';ledger=root/'campaign.sqlite3'
            original=recovery._write_bytes_atomic
            def concurrent(path,data):
                original(path,data)
                if Path(path)==root/'campaign_recovery.json':state.write_bytes(b'external campaign')
            with patch.object(recovery,'_write_bytes_atomic',concurrent):
                with self.assertRaises(ValueError):recovery.initialize_campaign_checkpoint(self.campaign(),state,ledger)
            self.assertEqual(b'external campaign',state.read_bytes());self.assertFalse(ledger.exists())
            self.assertEqual('new_keeper',recovery.inspect_campaign_backup(state,ledger)['campaign_id'])

    def test_valid_empty_preparation_survives_but_non_genesis_campaign_is_refused(self):
        from mecha_game.era_plan import EraPlan
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);plan=EraPlan(root/'era_plan.json');plan.select_weather('storm')
            original=plan.path.read_bytes()
            recovery.initialize_campaign_checkpoint(self.campaign(),root/'campaign_state.json',root/'campaign.sqlite3')
            self.assertEqual(original,plan.path.read_bytes())
        for fault in ('eras','predecessor','status'):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory() as directory:
                root=Path(directory);campaign=self.campaign()
                if fault=='eras':campaign.era_offset=1
                elif fault=='predecessor':campaign.campaign['predecessor_campaign_id']='parent'
                else:campaign.campaign['status']='extinct'
                with self.assertRaises(ValueError):recovery.initialize_campaign_checkpoint(campaign,root/'campaign_state.json',root/'campaign.sqlite3')
                self.assertEqual({},files(root))


if __name__=='__main__':unittest.main()
