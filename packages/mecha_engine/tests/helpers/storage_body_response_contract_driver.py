"""Passive immutable body model integrity; no outcome qualification."""
import base64,copy,importlib.util,json,unittest
from pathlib import Path
import mecha_engine.storage as package_store
spec=importlib.util.spec_from_file_location('body_storage_old',Path(__file__).with_name('storage_execution_contract_driver.py'))
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)

def active_fixture():
    campaign,profile,era,bundle=old.fixture()
    payload=dict(format='body_response_inputs_v1',body_response='workload-v1')
    put_model(bundle,payload)
    era['report']['body_response']='workload-v1'
    bundle['manifest']['report_sha256']=old.digest(era['report'])
    return campaign,profile,era,bundle

def put_model(bundle,payload):
    key='body_response_inputs_sha256';refs=bundle['manifest']['inputs']
    previous=refs.get(key)
    if previous:bundle['blobs'].pop(previous)
    data=json.dumps(payload,separators=(',',':')).encode()
    import hashlib
    sha=hashlib.sha256(data).hexdigest();refs[key]=sha
    bundle['blobs'][sha]=dict(media_type='application/json',data_base64=base64.b64encode(data).decode())

class StorageBodyResponseTests(unittest.TestCase):
    store=package_store
    def setUp(self):
        self.campaign,self.profile,self.era,self.bundle=active_fixture()
        self.conn=self.store.open_ledger(':memory:');self.addCleanup(self.conn.close)
        self.store.record_campaign(self.conn,self.campaign)
    def record(self):
        self.store.record_era(self.conn,self.campaign['campaign_id'],self.era,self.profile,execution=self.bundle)
    def test_roundtrip_retains_exact_opt_in_payload(self):
        self.record();self.assertEqual(self.bundle,self.store.load_era_execution(self.conn,self.campaign['campaign_id'],0))
    def test_unknown_model_and_malformed_payload_refuse(self):
        for value in (dict(format='body_response_inputs_v1',body_response='workload-v2'),dict(format='body_response_inputs_v1',body_response='legacy'),dict(format='body_response_inputs_v9',body_response='workload-v1'),dict(format='body_response_inputs_v1',body_response='workload-v1',extra=True)):
            with self.subTest(value=value):
                put_model(self.bundle,value)
                with self.assertRaisesRegex(ValueError,'body'):self.store.validate_execution(self.bundle)
    def test_report_model_must_equal_captured_model(self):
        del self.era['report']['body_response'];self.bundle['manifest']['report_sha256']=old.digest(self.era['report'])
        with self.assertRaisesRegex(ValueError,'body'):self.record()
    def test_active_report_requires_immutable_inputs(self):
        with self.assertRaisesRegex(ValueError,'body'):
            self.store.record_era(self.conn,self.campaign['campaign_id'],self.era,self.profile)
        ref=self.bundle['manifest']['inputs'].pop('body_response_inputs_sha256');self.bundle['blobs'].pop(ref)
        with self.assertRaisesRegex(ValueError,'body'):self.record()
    def test_missing_execution_for_active_era_refuses(self):
        self.record()
        self.conn.execute('DELETE FROM founder_occurrences')
        self.conn.execute('DELETE FROM era_executions')
        with self.assertRaisesRegex(ValueError,'body response execution evidence is missing'):
            self.store.load_era_execution(self.conn,self.campaign['campaign_id'],0)
    def test_continuation_cannot_change_model(self):
        self.record()
        self.era['era_index']=1;self.bundle['manifest']['era_index']=1
        ref=self.bundle['manifest']['inputs'].pop('body_response_inputs_sha256');self.bundle['blobs'].pop(ref)
        del self.era['report']['body_response'];self.bundle['manifest']['report_sha256']=old.digest(self.era['report'])
        with self.assertRaisesRegex(ValueError,'body'):self.record()

if __name__=='__main__':unittest.main()
