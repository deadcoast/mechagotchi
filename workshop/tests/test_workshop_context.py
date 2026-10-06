"""X3 selected native authority, draft recovery and pack API regressions."""
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from unittest.mock import patch
import json
from pathlib import Path
import sys
import tempfile
import unittest
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
for source in ('workshop/server', 'game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT/source))
from workshop_server import start_workshop_server
from mecha_game.session import CompanionSession, load_session_inputs
from mecha_game.campaign import KeeperCampaign


def snapshot(document, revision=1):
    state = {'document': deepcopy(document), 'name': 'unfinished'}
    return {'format':'mecha_workshop_draft_v1', 'draft_revision':revision,
        'document':deepcopy(document), 'editor_state':{'name':'unfinished'},
        'history':{'version':1,'history':[state],'index':0,'saved':None}}


def files(root):
    return {p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob('*') if p.is_file()}


class SelectedKeeperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid, cls.profile, cls.model = load_session_inputs(
            ROOT/'data/seed_grids_16x16/mg_seed16_001_beetle.json',
            ROOT/'data/slips/valid/slip_v2_cleanliness.json')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.servers = []
        self.document = {'format':'mecha_workshop_document_v1','grid':deepcopy(self.grid), 'profile':deepcopy(self.profile)}

    def tearDown(self):
        for server in self.servers:
            server.shutdown(); server.server_close()
        self.temp.cleanup()

    def keeper(self, name='one'):
        root = self.root/name
        pet = CompanionSession(deepcopy(self.grid),deepcopy(self.profile),model=self.model)
        pet.bind_campaign(name)
        root.mkdir()
        pet.save(root/'companion.json')
        campaign = KeeperCampaign({'slip_profile':deepcopy(self.profile)},campaign_id=name,
            era_config={'population':3,'generations':2})
        campaign.save(root/'campaign.sqlite3'); campaign.save_state(root/'campaign_state.json')
        return root, pet, campaign

    def start(self, keeper=None, project=None):
        project = project or self.root/'project'
        options = dict(grids_dir=project/'grids', slips_dir=project/'slips',
            released_dir=project/'released',metrics_dir=project/'metrics',session_dir=project/'lab')
        if keeper is not None: options['keeper_dir']=keeper
        server = start_workshop_server(**options)
        self.servers.append(server)
        return server

    def request(self, server, path, payload=None):
        req = urllib.request.Request(f'http://127.0.0.1:{server.server_address[1]}'+path,
            data=json.dumps(payload).encode() if payload is not None else None,
            headers={'Content-Type':'application/json'})
        try: response=urllib.request.urlopen(req,timeout=20)
        except urllib.error.HTTPError as error: response=error
        with response:
            raw=response.read()
            return response.status, json.loads(raw) if 'application/json' in response.headers.get('Content-Type','') else raw

    def context(self, server):
        code,result=self.request(server,'/api/context'); self.assertEqual(200,code,result)
        return result

    def pins(self, context):
        return dict(context_id=context['context_id'],expected_context_revision=context['context_revision'])

    def test_native_context_uses_actual_files_budget_and_no_mutation(self):
        keeper,pet,_=self.keeper(); before=files(keeper); server=self.start(keeper)
        ctx=self.context(server)
        self.assertEqual('native_keeper',ctx['kind']); self.assertTrue(ctx['available'],ctx)
        self.assertEqual(pet.keeper_id,ctx['keeper_id']); self.assertEqual(self.profile,ctx['covenant'])
        self.assertEqual(3,ctx['budget']['population_cap']); self.assertEqual(2,ctx['budget']['generation_cap'])
        self.assertEqual(before,files(keeper))
        code, inventory=self.request(server,'/api/context/creatures')
        self.assertEqual(200,code,inventory)
        code,selected=self.request(server,'/api/context/document',{**self.pins(ctx),'ref':inventory['creatures'][0]['ref']})
        self.assertEqual(200,code,selected); self.assertEqual(self.document,selected['document'])

    def test_missing_or_wrong_native_context_never_falls_back_to_lab(self):
        server=self.start(self.root/'missing'); ctx=self.context(server)
        self.assertEqual('native_keeper',ctx['kind']); self.assertFalse(ctx['available']); self.assertIsNone(ctx['budget'])
        self.assertFalse((self.root/'missing').exists())
        keeper,pet,_=self.keeper(); payload=json.loads((keeper/'companion.json').read_text())
        payload['chronicle']['campaign_id']='foreign'
        (keeper/'companion.json').write_text(json.dumps(payload))
        other=self.start(keeper); self.assertFalse(self.context(other)['available'])

    def test_native_writes_require_fresh_context_and_isolate_selected_inboxes(self):
        keeper,_,campaign=self.keeper(); untouched,_,_=self.keeper('two'); before=files(untouched)
        server=self.start(keeper); ctx=self.context(server)
        write={'name':'selected','document':self.document,'draft_revision':4,'expected_disk_revision':None}
        self.assertEqual(409,self.request(server,'/api/save',write)[0])
        code,saved=self.request(server,'/api/save',{**write,**self.pins(ctx)})
        self.assertEqual(200,code,saved); self.assertTrue((keeper/'workshop/grids/selected.json').is_file())
        campaign.campaign['slip_profile']['name']='changed active covenant'; campaign.save_state(keeper/'campaign_state.json')
        code,refusal=self.request(server,'/api/release',{**write,**self.pins(ctx)})
        self.assertEqual(409,code,refusal); self.assertEqual('context_changed',refusal['error_code'])
        self.assertNotIn('current_revision',refusal)
        ctx=self.context(server)
        code,released=self.request(server,'/api/release',{**write,**self.pins(ctx)})
        self.assertEqual(200,code,released)
        self.assertTrue((keeper/'released/selected.json').is_file()); self.assertEqual(before,files(untouched))
        self.assertEqual('staged',released['status']); self.assertEqual(ctx['keeper_id'],released['release_provenance']['keeper_id'])
        for path in ('/api/session/new','/api/session/era','/api/companion/adopt','/api/companion/act'):
            self.assertEqual(403,self.request(server,path,{})[0],path)

    def test_draft_survives_new_port_and_initial_blank_conflicts(self):
        server=self.start(); ctx=self.context(server)
        broken=deepcopy(self.document); broken['grid']['cells']=[]
        draft=snapshot(broken)
        code,first=self.request(server,'/api/drafts/grid',dict(snapshot=draft,expected_draft_revision=None))
        self.assertEqual(200,code,first)
        server.shutdown();server.server_close();self.servers.remove(server)
        other=self.start(); self.assertEqual(ctx['context_id'],self.context(other)['context_id'])
        code,loaded=self.request(other,'/api/drafts/grid'); self.assertEqual(200,code,loaded)
        self.assertEqual(draft,loaded['snapshot'])
        self.assertEqual(409,self.request(other,'/api/drafts/grid',dict(snapshot=snapshot(self.document),expected_draft_revision=None))[0])
        code,current=self.request(other,'/api/drafts/grid');self.assertEqual(draft,current['snapshot'])

    def test_draft_bounds_consistency_and_prior_recovery_preserve_bytes(self):
        server=self.start(); draft=snapshot(self.document)
        code,first=self.request(server,'/api/drafts/grid',dict(snapshot=draft,expected_draft_revision=None))
        self.assertEqual(200,code,first)
        changed=snapshot(self.document,2)
        code,second=self.request(server,'/api/drafts/grid',dict(snapshot=changed,expected_draft_revision=first['draft_disk_revision']))
        self.assertEqual(200,code,second)
        code,prior=self.request(server,'/api/drafts/grid?slot=previous');self.assertEqual(draft,prior['snapshot'])
        invalid=deepcopy(changed);invalid['editor_state']['name']='not in active history'
        self.assertEqual(400,self.request(server,'/api/drafts/grid',dict(snapshot=invalid,expected_draft_revision=second['draft_disk_revision']))[0])
        path=self.root/'project/drafts/grid.json';path.write_bytes(b'{broken')
        code,bad=self.request(server,'/api/drafts/grid'); self.assertEqual(409,code,bad);self.assertTrue(bad['recovery_available'])
        code,prior=self.request(server,'/api/drafts/grid?slot=previous')
        code,recovered=self.request(server,'/api/drafts/grid',dict(snapshot=prior['snapshot'],expected_draft_revision=prior['draft_disk_revision'],archive_previous=True))
        self.assertEqual(200,code,recovered); self.assertEqual(b'{broken',(path.parent/recovered['archive']).read_bytes())

    def test_pack_export_import_roundtrip_and_receipt_stay_selected(self):
        keeper,_,_=self.keeper(); server=self.start(keeper);ctx=self.context(server)
        composition=dict(pack_id='named',title='Named pack',provenance={'author':'Keeper'},slips=[self.profile],creatures=[self.grid],draft_revision=9)
        code,built=self.request(server,'/api/packs/build',{**composition,**self.pins(ctx)})
        self.assertEqual(200,code,built);self.assertEqual(self.grid,built['pack']['creatures'][0])
        code,report=self.request(server,'/api/packs/import',{**self.pins(ctx),'pack':built['pack'],'expected_pack_digest':built['pack_digest']})
        self.assertEqual(200,code,report);self.assertTrue(report['all_accepted']);self.assertTrue((keeper/'packs'/report['receipt']['file']).exists())
        self.assertEqual(self.grid,json.loads((keeper/'released'/report['creatures'][0]['staged']).read_text()))


    def test_all_native_write_routes_refuse_old_context_and_pending_recovery(self):
        keeper,_,_=self.keeper(); server=self.start(keeper); ctx=self.context(server)
        payload={**self.pins(ctx),'document':self.document,'name':'isolated','draft_revision':1}
        (keeper/'campaign_restore.json').write_text('{}')
        before=files(keeper)
        for endpoint in ('/api/save','/api/slip/save','/api/release','/api/metrics/flush','/api/drafts/grid','/api/packs/import'):
            code,result=self.request(server,endpoint,payload)
            self.assertEqual(409,code,(endpoint,result))
        self.assertEqual(before,files(keeper)); self.assertFalse(self.context(server)['available'])
        (keeper/'campaign_restore.json').unlink()
        (keeper/'era_plan.json').write_text('{broken')
        unavailable=self.context(server); self.assertFalse(unavailable['available'])
        self.assertEqual(409,self.request(server,'/api/save',{**payload,**self.pins(unavailable)})[0])

    def test_context_detects_marker_appearing_during_readonly_snapshot(self):
        keeper,_,_=self.keeper()
        from mecha_game.keeper_context import read_keeper
        from mecha_game.campaign_recovery import validated_campaign_snapshot
        @contextmanager
        def interrupted(*args,**kwargs):
            with validated_campaign_snapshot(*args,**kwargs) as result:
                (keeper/'campaign_restore.json').write_text('{}')
                yield result
        with patch('mecha_game.campaign_recovery.validated_campaign_snapshot',interrupted):
            result=read_keeper(keeper)
        self.assertFalse(result['context']['available']);self.assertIn('changed',result['context']['reason'])

    def test_draft_concurrent_cas_bounds_and_native_namespaces(self):
        one,_,_=self.keeper();two,_,_=self.keeper('two');a=self.start(one);b=self.start(two)
        ac=self.context(a);bc=self.context(b);self.assertNotEqual(ac['context_id'],bc['context_id'])
        draft=snapshot(self.document)
        code,first=self.request(a,'/api/drafts/grid',{**self.pins(ac),'snapshot':draft,'expected_draft_revision':None})
        self.assertEqual(200,code,first)
        def save(revision):
            return self.request(a,'/api/drafts/grid',{**self.pins(ac),'snapshot':snapshot(self.document,revision),
                'expected_draft_revision':first['draft_disk_revision']})[0]
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual([200,409],sorted(pool.map(save,[3,4])))
        self.assertFalse(self.request(b,'/api/drafts/grid')[1]['exists'])
        current=self.request(a,'/api/drafts/grid')[1]
        for bad in ('history','bytes'):
            changed=deepcopy(draft)
            if bad=='history': changed['history']['history']*=41
            else: changed['editor_state']['note']='x'*(2*1024*1024);changed['history']['history'][0]['note']=changed['editor_state']['note']
            code,result=self.request(a,'/api/drafts/grid',{**self.pins(ac),'snapshot':changed,'expected_draft_revision':current['draft_disk_revision']})
            self.assertEqual(400,code,result)
        self.assertEqual(current['snapshot'],self.request(a,'/api/drafts/grid')[1]['snapshot'])

    def test_recorded_era_admission_and_full_elite_survive_restart_inspection(self):
        from mecha_game.campaign import load_campaign_inputs, TINY_ERA_CONFIG
        keeper,pet,_=self.keeper()
        inputs=load_campaign_inputs(ROOT/'data/seed_grids_16x16',ROOT/'data/slips/valid/slip_v2_cleanliness.json',
            ROOT/'data/readability_benchmark/adopted_readability_model.json',repair_epochs=6,seed_limit=12)
        campaign=KeeperCampaign(inputs,campaign_id='one',era_config=TINY_ERA_CONFIG)
        release=deepcopy(inputs['seed_grids'][1]);release['grid_id']='selected_author_release'
        era=campaign.advance_era('calm',released_grids=[release])
        campaign.save(keeper/'campaign.sqlite3');campaign.save_state(keeper/'campaign_state.json')
        server=self.start(keeper);ctx=self.context(server);self.assertTrue(ctx['available'],ctx)
        code,lineage=self.request(server,'/api/context/lineage');self.assertEqual(200,code,lineage)
        recorded=lineage['campaigns'][0]['eras'][0]
        self.assertEqual(era['report']['founders'],recorded['report']['founders'])
        self.assertEqual(release,recorded['founder_records'][0]['grid'])
        self.assertTrue(recorded['founder_provenance']['available'])
        entries=self.request(server,'/api/context/creatures')[1]['creatures']
        chosen=next(row for row in entries if row['source']=='era_elite')
        code,document=self.request(server,'/api/context/document',{**self.pins(ctx),'ref':chosen['ref']})
        expected=next(row['grid'] for row in era['elites'] if row['niche_key']==chosen['ref']['niche_key'])
        self.assertEqual(expected,document['document']['grid'])
        self.assertEqual(self.profile,document['document']['profile'])


    def test_released_full_document_remix_and_sidecar_tamper_are_explicit(self):
        import authoring
        keeper,_,_=self.keeper(); server=self.start(keeper);ctx=self.context(server)
        doc=deepcopy(self.document);doc['profile']['name']='Selected authored covenant, not active covenant'
        matrix=authoring.project_grid(doc['grid'])
        doc['layers']=[dict(name=name,matrix=matrix if name=='body' else [['.']*16 for _ in range(16)],
            creator_note='preserve hidden layer sibling') for name in ('body','organs','decoration','effects')]
        code,released=self.request(server,'/api/release',{**self.pins(ctx),'document':doc,'draft_revision':3,'name':'faithful'})
        self.assertEqual(200,code,released)
        inventory=self.request(server,'/api/context/creatures')[1]['creatures']
        chosen=next(row for row in inventory if row['source']=='released')
        code,remix=self.request(server,'/api/context/document',{**self.pins(ctx),'ref':chosen['ref']})
        self.assertEqual(200,code,remix);self.assertEqual(released['released_document'],remix['document'])
        sidecar=keeper/'released/faithful.authoring.json'
        stored=json.loads(sidecar.read_text());stored['document']['grid']['cells'][0]['mutation_weight']=.77
        sidecar.write_text(json.dumps(stored))
        result=self.request(server,'/api/context/creatures')[1]
        self.assertTrue(result['release_errors']);self.assertFalse(any(row['source']=='released' for row in result['creatures']))
        code,conflict=self.request(server,'/api/release',{**self.pins(ctx),'document':doc,'draft_revision':4,'name':'faithful',
            'expected_release_revision':released['release_revision']})
        self.assertEqual(409,code,conflict)


    def test_missing_primary_does_not_allow_blank_to_hide_previous_recovery(self):
        import drafts
        folder=self.root/'drafts'; draft=snapshot(self.document)
        first=drafts.write(folder,'grid','context',dict(snapshot=draft,expected_draft_revision=None))
        second=drafts.write(folder,'grid','context',dict(snapshot=snapshot(self.document,2),expected_draft_revision=first['draft_disk_revision']))
        (folder/'grid.json').unlink(); before=files(folder)
        with self.assertRaises(drafts.DraftError):
            drafts.write(folder,'grid','context',dict(snapshot=snapshot(self.document,0),expected_draft_revision=None))
        self.assertEqual(before,files(folder))


    def test_native_start_defers_unused_models_and_preserves_first_preview_output(self):
        import time
        import workshop_server as module
        keeper,_,_=self.keeper()
        with patch.object(module,'train_repair_model',wraps=module.train_repair_model) as repair, patch.object(module,'train_generation_model',wraps=module.train_generation_model) as generation:
            started=time.perf_counter(); server=self.start(keeper);elapsed=time.perf_counter()-started
            print(json.dumps(dict(native_start_seconds=elapsed,repair_calls=repair.call_count,generation_calls=generation.call_count)),flush=True)
            self.assertEqual(0,repair.call_count);self.assertEqual(0,generation.call_count)
            self.context(server);self.assertEqual(0,repair.call_count)
            models=server.models_for(server.seed_grids[0])
            self.assertEqual(1,repair.call_count);self.assertEqual(1,generation.call_count)
            self.assertEqual(server.seed_grids,repair.call_args.args[0])
            self.assertIs(models,server.models_for(server.seed_grids[0]))
        legacy=self.start(project=self.root/'legacy')
        self.assertEqual(legacy.models_for(legacy.seed_grids[0]),models)


    def test_pack_digest_refusal_has_error_status_while_partial_processing_stays_visible(self):
        from mecha_game.packs import build_pack,pack_digest
        keeper,_,_=self.keeper();server=self.start(keeper);ctx=self.context(server)
        pack=build_pack(pack_id='partial',title='Partial pack',provenance={},slips=[self.profile],creatures=[self.grid])
        before=files(keeper)
        code,refusal=self.request(server,'/api/packs/import',{**self.pins(ctx),'pack':pack,'expected_pack_digest':'0'*64})
        self.assertEqual(409,code,refusal);self.assertIn('changed',refusal['error'].lower());self.assertEqual(before,files(keeper))
        pack['slips'].append({})
        code,partial=self.request(server,'/api/packs/import',{**self.pins(ctx),'pack':pack,'expected_pack_digest':pack_digest(pack)})
        self.assertEqual(200,code,partial);self.assertTrue(partial['ok']);self.assertTrue(partial['partial'])
        self.assertFalse(partial['slips'][1]['ok']);self.assertTrue(partial['slips'][1]['violations'])

    def test_pack_composition_does_not_claim_to_import_into_its_source_keeper(self):
        keeper,_,_=self.keeper();server=self.start(keeper);ctx=self.context(server)
        code,released=self.request(server,'/api/release',{**self.pins(ctx),'name':'same_identity','document':self.document,'draft_revision':1})
        self.assertEqual(200,code,released)
        composition=dict(pack_id='portable',title='Portable original',provenance={},slips=[self.profile],creatures=[self.grid],draft_revision=2)
        code,built=self.request(server,'/api/packs/build',{**self.pins(ctx),**composition})
        self.assertEqual(200,code,built);self.assertTrue(built['all_accepted'],built)
        code,destination=self.request(server,'/api/packs/preview',{**self.pins(ctx),'pack':built['pack']})
        self.assertEqual(200,code,destination);self.assertEqual('conflicting',destination['creatures'][0]['status'])


    def test_source_document_and_revision_cannot_mix_external_file_generations(self):
        import authoring
        keeper,_,_=self.keeper();server=self.start(keeper);ctx=self.context(server)
        code,saved=self.request(server,'/api/save',{**self.pins(ctx),'name':'source','document':self.document,'draft_revision':1,'expected_disk_revision':None})
        self.assertEqual(200,code,saved)
        original=self.request(server,'/api/context/creatures')[1]
        ref=next(row['ref'] for row in original['creatures'] if row['source']=='workshop')
        target=keeper/'workshop/grids/source.json';sidecar=target.with_name('source.layers.json')
        changed=deepcopy(self.document);changed['grid']['cells'][0]['mutation_weight']=.31
        newer_grid=authoring.json_bytes(changed['grid']);newer_sidecar=authoring.json_bytes({'document':changed})
        old_revision=authoring.disk_revision(target,sidecar)
        read=Path.read_bytes; raced=False
        def external_writer(path):
            nonlocal raced
            result=read(path)
            if path==target and not raced:
                raced=True;target.write_bytes(newer_grid);sidecar.write_bytes(newer_sidecar)
            return result
        with patch.object(Path,'read_bytes',external_writer):
            try: loaded,revision=authoring.load_document(target)
            except ValueError: loaded=revision=None  # Explicitly refused incoherent read is safe.
        self.assertTrue(raced)
        if loaded is not None:
            if loaded==self.document: self.assertEqual(old_revision,revision)
            else: self.assertEqual(changed,loaded);self.assertEqual(authoring.disk_revision(target,sidecar),revision)
        code,result=self.request(server,'/api/context/document',{**self.pins(ctx),'ref':ref})
        self.assertEqual(404,code,result)


if __name__=='__main__': unittest.main()
