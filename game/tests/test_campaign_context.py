"""X3 foundation: coherent history and truthful submitted-founder evidence."""
import copy
from contextlib import closing
import json
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
from mecha_game.era_plan import EraPlan, state_digest, _digest
from mecha_game.campaign_recovery import validate_ledger_state


def files(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*') if p.is_file()}


class CampaignContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_campaign_inputs(ROOT/'data/seed_grids_16x16',
            ROOT/'data/slips/valid/slip_v2_cleanliness.json',
            ROOT/'data/readability_benchmark/adopted_readability_model.json',
            repair_epochs=6, seed_limit=12)
        cls.first = KeeperCampaign(cls.inputs, campaign_id='x3_parent', era_config=TINY_ERA_CONFIG)
        cls.first.advance_era('calm')
        cls.parent = copy.deepcopy(cls.first); cls.parent.campaign['status'] = 'extinct'
        cls.child = cls.parent.successor(); cls.child.advance_era('calm')
        cls.good = copy.deepcopy(cls.inputs['seed_grids'][0]); cls.good['grid_id'] = 'x3_unique_release'
        cls.bad = copy.deepcopy(cls.good); cls.bad['grid_id'] = 'x3_refused_release'; cls.bad['cells'][0]['mutation_weight'] = -1
        cls.duplicate = copy.deepcopy(cls.good); cls.duplicate['grid_id'] = 'x3_duplicate'
        cls.submitted = [cls.good, cls.bad, cls.duplicate, cls.duplicate]
        cls.founded = copy.deepcopy(cls.first)
        cls.founded.advance_era('calm', released_grids=copy.deepcopy(cls.submitted))

    def seed(self, root, campaign):
        state, ledger = root/'campaign_state.json', root/'campaign.sqlite3'
        campaign.save(ledger); campaign.save_state(state)
        return state, ledger

    def test_successor_completion_refuses_missing_predecessor_before_any_write(self):
        for fault in ('eras', 'elites', 'slip_profiles'):
            for committed_child in (False, True):
                with self.subTest(fault=fault, committed_child=committed_child), tempfile.TemporaryDirectory() as directory:
                    root=Path(directory);state,ledger=self.seed(root,self.parent)
                    plan=EraPlan(root/'era_plan.json');plan.begin(self.child,self.child.eras[-1],state_digest(state))
                    if committed_child:self.child.save(ledger)
                    with closing(sqlite3.connect(ledger)) as conn,conn:
                        conn.execute('DELETE FROM '+fault+' WHERE campaign_id=?',(self.parent.campaign['campaign_id'],))
                    before=files(root)
                    with self.assertRaises(ValueError):plan.finish(ledger,state)
                    self.assertEqual(before,files(root))

    def test_loaded_successor_refuses_dangling_predecessor_era_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);state,ledger=self.seed(root,self.parent)
            self.child.save(ledger);self.child.save_state(state)
            with closing(sqlite3.connect(ledger)) as conn,conn:
                conn.execute('DELETE FROM eras WHERE campaign_id=?',(self.parent.campaign['campaign_id'],))
            before=files(root)
            with self.assertRaises(ValueError):validate_ledger_state(self.child.state_payload(),ledger)
            self.assertEqual(before,files(root))

    def test_snapshot_reader_is_readonly_and_keeps_one_wal_view(self):
        from mecha_game.campaign_recovery import validated_campaign_snapshot
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);state,ledger=self.seed(root,self.first)
            with closing(sqlite3.connect(ledger)) as writer:
                writer.execute('PRAGMA journal_mode=WAL')
                with validated_campaign_snapshot(self.first.state_payload(),ledger) as (reader,history):
                    self.assertTrue(reader.in_transaction)
                    self.assertEqual(self.first.campaign['campaign_id'],history['campaign_id'])
                    with self.assertRaises(sqlite3.OperationalError):reader.execute('DELETE FROM campaigns')
                    old=reader.execute('SELECT count(*) FROM campaigns').fetchone()[0]
                    with writer:writer.execute("INSERT INTO campaigns VALUES ('other','other','date',NULL,'active')")
                    self.assertEqual(old,reader.execute('SELECT count(*) FROM campaigns').fetchone()[0])
                    self.assertEqual(old+1,writer.execute('SELECT count(*) FROM campaigns').fetchone()[0])
                with self.assertRaises(sqlite3.ProgrammingError):reader.execute('SELECT 1')

    def test_founder_rows_keep_full_unique_inputs_and_actual_verdicts_without_reordering_engine(self):
        era=self.founded.eras[-1];rows=era['founder_records'];by_id={row['grid_id']:row for row in rows}
        expected_ids=[grid['grid_id'] for grid in self.submitted]+[elite['grid_id'] for elite in self.first.eras[-1]['elites']]
        self.assertEqual(expected_ids,era['founders_submitted'])
        self.assertEqual(2,era['report']['founders']['admitted_ids'].count('x3_duplicate'))
        self.assertNotIn('x3_duplicate',by_id)
        self.assertEqual(self.good,by_id['x3_unique_release']['grid'])
        self.assertEqual('workshop_release',by_id['x3_unique_release']['source'])
        self.assertTrue(by_id['x3_unique_release']['admitted'])
        self.assertEqual(self.bad,by_id['x3_refused_release']['grid'])
        self.assertFalse(by_id['x3_refused_release']['admitted'])
        rejected=next(row for row in era['report']['founders']['rejected'] if row['grid_id']=='x3_refused_release')
        self.assertEqual(rejected['errors'],by_id['x3_refused_release']['rejection_errors'])
        for grid_id,row in by_id.items():
            if grid_id not in {'x3_unique_release','x3_refused_release'}:self.assertEqual('era_elite',row['source'])

    def test_pending_founder_rows_survive_retry_exactly_once_without_evolution(self):
        from mecha_game.campaign_recovery import load_recorded_founders
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);state,ledger=self.seed(root,self.first)
            plan=EraPlan(root/'era_plan.json');plan.begin(self.founded,self.founded.eras[-1],state_digest(state))
            with patch.object(KeeperCampaign,'save_state',side_effect=PermissionError('state locked')):
                with self.assertRaises(OSError):plan.finish(ledger,state)
            expected=sorted(self.founded.eras[-1]['founder_records'],key=lambda row:row['grid_id'])
            with closing(sqlite3.connect(ledger)) as conn:
                self.assertEqual(expected,load_recorded_founders(conn,self.founded.campaign['campaign_id'],1))
            with patch('mecha_game.campaign.evolve',side_effect=AssertionError('must not repeat evolution')):
                EraPlan(plan.path).finish(ledger,state)
            self.assertIsNone(EraPlan(plan.path).pending)
            with closing(sqlite3.connect(ledger)) as conn:
                self.assertEqual(expected,load_recorded_founders(conn,self.founded.campaign['campaign_id'],1))
                self.assertEqual(2,conn.execute('SELECT count(*) FROM eras').fetchone()[0])

    def test_valid_successor_retry_preserves_parent_and_finishes_without_evolution(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);state,ledger=self.seed(root,self.parent)
            plan=EraPlan(root/'era_plan.json');plan.begin(self.child,self.child.eras[-1],state_digest(state))
            with patch.object(KeeperCampaign,'save_state',side_effect=PermissionError('state locked')):
                with self.assertRaises(OSError):plan.finish(ledger,state)
            self.assertEqual(self.parent.state_payload(),json.loads(state.read_text()))
            with patch('mecha_game.campaign.evolve',side_effect=AssertionError('must not repeat evolution')):
                EraPlan(plan.path).finish(ledger,state)
            self.assertIsNone(EraPlan(plan.path).pending)
            self.assertEqual(self.child.state_payload(),json.loads(state.read_text()))
            with closing(sqlite3.connect(ledger)) as conn:
                self.assertEqual([(self.parent.campaign['campaign_id'],1),(self.child.campaign['campaign_id'],1)],
                    conn.execute('SELECT campaign_id,count(*) FROM eras GROUP BY campaign_id ORDER BY campaign_id').fetchall())

    def test_pending_retry_refuses_changed_recorded_founder_rows_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);state,ledger=self.seed(root,self.first)
            plan=EraPlan(root/'era_plan.json');plan.begin(self.founded,self.founded.eras[-1],state_digest(state))
            with patch.object(KeeperCampaign,'save_state',side_effect=PermissionError('state locked')):
                with self.assertRaises(OSError):plan.finish(ledger,state)
            with closing(sqlite3.connect(ledger)) as conn,conn:
                conn.execute('DELETE FROM founders WHERE grid_id=?',(self.good['grid_id'],))
            before=files(root)
            with self.assertRaises(ValueError):EraPlan(plan.path).finish(ledger,state)
            self.assertEqual(before,files(root))

    def test_legacy_completed_journal_does_not_backfill_missing_founder_evidence(self):
        from mecha_game.campaign_recovery import load_recorded_founders
        legacy=copy.deepcopy(self.founded)
        for era in legacy.eras:era.pop('founder_records',None)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);state,ledger=self.seed(root,self.first)
            plan=EraPlan(root/'era_plan.json');plan.begin(legacy,legacy.eras[-1],state_digest(state))
            plan.finish(ledger,state)
            with closing(sqlite3.connect(ledger)) as conn:
                self.assertEqual([],load_recorded_founders(conn,legacy.campaign['campaign_id'],1))
            self.assertTrue(legacy.eras[-1]['report']['founders']['admitted_ids'])

    def test_checksumming_a_false_founder_verdict_does_not_authorize_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);state,ledger=self.seed(root,self.first)
            plan=EraPlan(root/'era_plan.json');plan.begin(self.founded,self.founded.eras[-1],state_digest(state))
            value=json.loads(plan.path.read_text());pending=value['pending']
            pending['era']['founder_records']=[{'grid_id':self.good['grid_id'],'source':'workshop_release',
                'grid':self.good,'admitted':False,'rejection_errors':['invented refusal']}]
            pending['sha256']=_digest({k:v for k,v in pending.items() if k!='sha256'})
            plan.path.write_text(json.dumps(value));before=files(root)
            with self.assertRaises(ValueError):EraPlan(plan.path).finish(ledger,state)
            self.assertEqual(before,files(root))


if __name__=='__main__':unittest.main()
