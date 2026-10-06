"""Body compatibility through actual selected-Keeper HTTP paths; no outcome trials."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for source in ('workshop/server', 'game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT/source))
from test_workshop_context import SelectedKeeperTests, files, snapshot
from mecha_game.session import CompanionSession
from mecha_game.campaign import KeeperCampaign
from mecha_game.packs import build_pack, pack_digest
import workshop_server
import drafts
import authoring
import mecha_game.packs as packs


class BodyCompatibilityTests(unittest.TestCase):
    setUpClass = classmethod(SelectedKeeperTests.setUpClass.__func__)
    setUp = SelectedKeeperTests.setUp
    tearDown = SelectedKeeperTests.tearDown
    start = SelectedKeeperTests.start
    request = SelectedKeeperTests.request
    context = SelectedKeeperTests.context
    pins = SelectedKeeperTests.pins

    def keeper(self, name='one', body='legacy'):
        root = self.root/name
        root.mkdir()
        pet = CompanionSession(deepcopy(self.grid), deepcopy(self.profile), model=self.model, body_response=body)
        pet.bind_campaign(name)
        pet.save(root/'companion.json')
        campaign = KeeperCampaign({'slip_profile':deepcopy(self.profile)}, campaign_id=name,
            body_response=body, era_config={'population':3, 'generations':2})
        campaign.save(root/'campaign.sqlite3')
        campaign.save_state(root/'campaign_state.json')
        return root, pet, campaign

    def switch(self, root, pet):
        changed = pet.adopt(pet.grid, pet.slip_profile,
            body_response='workload-v1' if pet.body_response=='legacy' else 'legacy')
        self.assertEqual(pet.keeper_id, changed.keeper_id)
        changed.save(root/'companion.json')
        return changed

    def test_mismatch_keeps_inspection_but_refuses_all_write_capabilities_after_restart(self):
        for body in ('legacy', 'workload-v1'):
            with self.subTest(body=body):
                root, pet, _ = self.keeper(body, body)
                self.switch(root, pet)
                before = files(root)
                for restart in range(2):
                    server = self.start(root)
                    context = self.context(server)
                    self.assertTrue(context['available'], context)
                    self.assertIn('body response', context['reason'] or '')
                    for name in ('authoring', 'release', 'pack_import'):
                        self.assertFalse(context['capabilities'][name], context)
                    code, inventory = self.request(server, '/api/context/creatures')
                    self.assertEqual(200, code, inventory)
                    self.assertTrue(inventory['creatures'])
                    code, selected = self.request(server, '/api/context/document',
                        {**self.pins(context), 'ref':inventory['creatures'][0]['ref']})
                    self.assertEqual(200, code, selected)
                    code, history = self.request(server, '/api/context/lineage')
                    self.assertEqual(200, code, history)
                    self.assertEqual(2, len(history['lives']))
                    self.assertEqual(before, files(root))

    def test_fresh_mismatch_http_writes_preserve_every_file_and_backup(self):
        paths = ('/api/save','/api/slip/save','/api/release','/api/drafts/grid','/api/packs/import','/api/metrics/flush')
        for body in ('legacy', 'workload-v1'):
            for index, path in enumerate(paths):
                with self.subTest(body=body, path=path):
                    root, pet, _ = self.keeper(f'{body}-{index}', body)
                    self.switch(root, pet)
                    server = self.start(root)
                    context = self.context(server)
                    profile = deepcopy(self.profile); profile['profile_id']='compatibility_profile'
                    pack = build_pack(pack_id='compatibility',title='Compatibility',provenance={},slips=[profile],creatures=[self.grid])
                    payload = {**self.pins(context), 'name':'unchanged', 'document':self.document,
                        'draft_revision':1, 'expected_disk_revision':None, 'expected_release_revision':None,
                        'snapshot':snapshot(self.document), 'expected_draft_revision':None,
                        'pack':pack, 'expected_pack_digest':pack_digest(pack)}
                    if path=='/api/slip/save': payload['document']={'format':'mecha_workshop_document_v1','profile':profile}
                    before = files(root)
                    for retry in range(2):
                        code, refusal = self.request(server, path, payload)
                        self.assertEqual(409, code, refusal)
                        self.assertEqual(before, files(root))

    def test_stale_context_refuses_after_supported_model_switch(self):
        root, pet, _ = self.keeper(); server = self.start(root)
        context = self.context(server); self.switch(root, pet); before=files(root)
        code, result = self.request(server, '/api/release', {**self.pins(context),
            'document':self.document, 'name':'stale', 'draft_revision':1})
        self.assertEqual(409,code,result); self.assertEqual(before,files(root))

    def test_draft_delayed_validation_refuses_before_previous_backup(self):
        root, pet, _ = self.keeper(); server = self.start(root); context=self.context(server)
        payload={**self.pins(context),'snapshot':snapshot(self.document),'expected_draft_revision':None}
        code, saved = self.request(server,'/api/drafts/grid',payload);self.assertEqual(200,code,saved)
        payload.update(snapshot=snapshot(self.document,2),expected_draft_revision=saved['draft_disk_revision'])
        validate=drafts.validate; switched=False; before=None
        def delayed(*args,**kwargs):
            nonlocal switched,before
            value=validate(*args,**kwargs)
            if not switched:
                switched=True;self.switch(root,pet);before=files(root)
            return value
        with patch.object(drafts,'validate',delayed):
            code,result=self.request(server,'/api/drafts/grid',payload)
        self.assertTrue(switched);self.assertEqual(409,code,result);self.assertEqual(before,files(root))

    def test_release_delayed_disk_inspection_refuses_before_backup(self):
        root, pet, _ = self.keeper(); server=self.start(root); context=self.context(server)
        payload={**self.pins(context),'document':self.document,'name':'delayed','draft_revision':1}
        code,saved=self.request(server,'/api/release',payload);self.assertEqual(200,code,saved)
        payload['expected_release_revision']=saved['release_revision']
        revision=authoring.disk_revision; switched=False; before=None
        def delayed(*args,**kwargs):
            nonlocal switched,before
            value=revision(*args,**kwargs)
            if not switched and args[0]==root/'released/delayed.json':
                switched=True;self.switch(root,pet);before=files(root)
            return value
        with patch.object(authoring,'disk_revision',delayed):
            code,result=self.request(server,'/api/release',payload)
        self.assertTrue(switched);self.assertEqual(409,code,result);self.assertEqual(before,files(root))

    def test_pack_delayed_preview_refuses_before_receipt_or_assets(self):
        root,pet,_=self.keeper();server=self.start(root);context=self.context(server)
        pack=build_pack(pack_id='late',title='Late',provenance={},slips=[self.profile],creatures=[self.grid])
        preview=packs.preview_pack; switched=False; before=None
        def delayed(*args,**kwargs):
            nonlocal switched,before
            value=preview(*args,**kwargs)
            if not switched:
                switched=True;self.switch(root,pet);before=files(root)
            return value
        with patch.object(packs,'preview_pack',delayed):
            code,result=self.request(server,'/api/packs/import',{**self.pins(context),'pack':pack,'expected_pack_digest':pack_digest(pack)})
        self.assertTrue(switched);self.assertEqual(409,code,result);self.assertEqual(before,files(root))

    def test_delayed_grid_profile_and_metrics_writes_refuse_current_model_change(self):
        for index,path in enumerate(('/api/save','/api/slip/save','/api/metrics/flush')):
            with self.subTest(path=path):
                root,pet,_=self.keeper(str(index));server=self.start(root);context=self.context(server)
                profile=deepcopy(self.profile);profile['profile_id']='delayed_profile'
                document=({'format':'mecha_workshop_document_v1','profile':profile}
                    if path=='/api/slip/save' else self.document)
                payload={**self.pins(context),'document':document,'name':'delayed','draft_revision':1,'expected_disk_revision':None}
                switched=False;before=None
                module=workshop_server.time if path=='/api/metrics/flush' else authoring
                attribute='strftime' if path=='/api/metrics/flush' else 'disk_revision'
                function=getattr(module,attribute)
                def delayed(*args,**kwargs):
                    nonlocal switched,before
                    value=function(*args,**kwargs)
                    if not switched:
                        switched=True;self.switch(root,pet);before=files(root)
                    return value
                with patch.object(module,attribute,delayed):
                    code,result=self.request(server,path,payload)
                self.assertTrue(switched);self.assertEqual(409,code,result);self.assertEqual(before,files(root))

    def test_interrupted_preparation_appearing_during_release_refuses_before_backup(self):
        root,_,_=self.keeper();server=self.start(root);context=self.context(server)
        revision=authoring.disk_revision;interrupted=False;before=None
        def delayed(*args,**kwargs):
            nonlocal interrupted,before
            value=revision(*args,**kwargs)
            if not interrupted and args[0]==root/'released/pending.json':
                interrupted=True;(root/'campaign_preparation.json').write_bytes(b'{interrupted')
                before=files(root)
            return value
        with patch.object(authoring,'disk_revision',delayed):
            code,result=self.request(server,'/api/release',{**self.pins(context),
                'document':self.document,'name':'pending','draft_revision':1})
        self.assertTrue(interrupted);self.assertEqual(409,code,result);self.assertEqual(before,files(root))
        current=self.context(server);self.assertFalse(current['available'])
        code,result=self.request(server,'/api/release',{**self.pins(current),
            'document':self.document,'name':'pending','draft_revision':1})
        self.assertEqual(409,code,result);self.assertEqual(before,files(root))

    def test_mismatched_keeper_can_review_and_export_saved_pack_without_writes(self):
        root,pet,_=self.keeper();self.switch(root,pet);server=self.start(root);context=self.context(server)
        composition={**self.pins(context),'pack_id':'inspection','title':'Inspection',
            'provenance':{},'slips':[self.profile],'creatures':[self.grid]}
        before=files(root)
        code,built=self.request(server,'/api/packs/build',composition)
        self.assertEqual(200,code,built)
        code,preview=self.request(server,'/api/packs/preview',{**self.pins(context),'pack':built['pack']})
        self.assertEqual(200,code,preview)
        code,exported=self.request(server,'/api/packs/export',composition)
        self.assertEqual(200,code);self.assertEqual(built['pack'],exported)
        self.assertEqual(before,files(root))

    def test_compatible_active_draft_release_and_import_repeat_without_semantic_duplication(self):
        root,_,_=self.keeper(body='workload-v1');server=self.start(root);context=self.context(server)
        draft={**self.pins(context),'snapshot':snapshot(self.document),'expected_draft_revision':None}
        code,saved=self.request(server,'/api/drafts/grid',draft);self.assertEqual(200,code,saved)
        before=files(root);draft['expected_draft_revision']=saved['draft_disk_revision']
        code,repeated=self.request(server,'/api/drafts/grid',draft);self.assertEqual(200,code,repeated);self.assertEqual(before,files(root))
        code,released=self.request(server,'/api/release',{**self.pins(context),'document':self.document,'name':'valid','draft_revision':1})
        self.assertEqual(200,code,released)
        self.assertEqual(1,released['released_document']['grid']['lineage']['mutation_events'].count('released_into_ecosystem'))
        profile=deepcopy(self.profile);profile['profile_id']='portable'
        pack=build_pack(pack_id='compatible',title='Compatible',provenance={},slips=[profile],creatures=[])
        payload={**self.pins(context),'pack':pack,'expected_pack_digest':pack_digest(pack)}
        code,result=self.request(server,'/api/packs/import',payload);self.assertEqual(200,code,result)
        before=files(root)
        code,result=self.request(server,'/api/packs/import',payload);self.assertEqual(200,code,result)
        self.assertTrue(result['receipt']['already_retained']);self.assertEqual(before,files(root))

# The imported fixture is reused without collecting its entire suite twice.
del SelectedKeeperTests

if __name__=='__main__': unittest.main()
