"""T2: complete stored elites are blob-authoritative, scoped, ordered reads."""
import copy
import importlib
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
for path in (ROOT/'labs/game_loop',ROOT/'packages/mecha_engine/src'):
    sys.path.insert(0,str(path))
import campaign_store as lab
package=importlib.import_module('mecha_engine.storage')
INTERIM=json.loads((ROOT/'data/game_loop/campaign_ledger.json').read_text(encoding='utf-8'))

class SavedEliteQueryTests(unittest.TestCase):
    def test_records_match_each_campaign_and_era_in_niche_order(self):
        for store in (lab,package):
            with self.subTest(store=store.__name__):
                conn=store.open_ledger(':memory:')
                try:
                    store.ingest_session_artifacts(conn,INTERIM)
                    for era in INTERIM['eras']:
                        expected=[{'niche_key':row['niche_key'],**row['elite']} for row in sorted(
                            [r for r in INTERIM['elites'] if r['campaign_id']==era['campaign_id'] and r['era_index']==era['era_index']],key=lambda row:row['niche_key'])]
                        self.assertEqual(expected,store.load_era_elites(conn,era['campaign_id'],era['era_index']))
                finally:conn.close()

    def test_unknown_campaign_or_era_is_empty(self):
        for store in (lab,package):
            with self.subTest(store=store.__name__):
                conn=store.open_ledger(':memory:')
                try:
                    store.ingest_session_artifacts(conn,INTERIM)
                    self.assertEqual([],store.load_era_elites(conn,'not_a_campaign',0))
                    self.assertEqual([],store.load_era_elites(conn,INTERIM['campaigns'][0]['campaign_id'],99999))
                finally:conn.close()

    def test_derived_scalar_columns_do_not_replace_blob_values(self):
        for store in (lab,package):
            with self.subTest(store=store.__name__):
                conn=store.open_ledger(':memory:')
                try:
                    store.ingest_session_artifacts(conn,INTERIM)
                    row=INTERIM['elites'][0]
                    conn.execute('UPDATE elites SET fitness=-999, grid_id=?',('derived_decoy',))
                    values=store.load_era_elites(conn,row['campaign_id'],row['era_index'])
                    actual=next(v for v in values if v['niche_key']==row['niche_key'])
                    self.assertEqual(row['elite'],{k:v for k,v in actual.items() if k!='niche_key'})
                finally:conn.close()

    def test_read_only_queries_leave_ledger_and_founder_pool_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'campaign.sqlite3'
            conn=lab.open_ledger(path)
            lab.ingest_session_artifacts(conn,INTERIM)
            campaign=INTERIM['campaigns'][0]['campaign_id']
            expected=lab.load_founder_pool(conn,campaign)
            conn.close()
            before=path.read_bytes()
            conn=sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True)
            try:
                for store in (lab,package):
                    with self.subTest(store=store.__name__):
                        for era in INTERIM['eras']:
                            store.load_era_elites(conn,era['campaign_id'],era['era_index'])
                        self.assertEqual(expected,store.load_founder_pool(conn,campaign))
            finally:conn.close()
            self.assertEqual(before,path.read_bytes())

if __name__=='__main__':unittest.main()
