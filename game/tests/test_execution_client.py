"""X5 client controls: exact sources, explicit reproduction and read-only evidence."""
import base64
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for folder in ('game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT / folder))

from mecha_game import contribute
from mecha_game.app import _EraBench, run


class ExecutionClientTests(unittest.TestCase):
    def test_gather_captures_exact_ordered_bytes_without_second_read(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper = Path(directory)
            inbox = keeper / 'released'; inbox.mkdir()
            payloads = [b'{ "grid_id": "first" }\r\n', b'{"grid_id":"second"}\n']
            (inbox/'b.json').write_bytes(payloads[1]); (inbox/'a.json').write_bytes(payloads[0])
            (inbox/'a.authoring.json').write_text('{}'); (inbox/'a.bak.json').write_text('{}')
            reads = []
            original = Path.read_bytes
            def read(path):
                reads.append(path.name)
                return original(path)
            with patch.object(Path, 'read_bytes', read):
                grids, sources = contribute.gather_release_inputs(keeper, include_shared=False)
            self.assertEqual(['a.json','b.json'], reads)
            self.assertEqual(['first','second'], [g['grid_id'] for g in grids])
            self.assertEqual(payloads, [base64.b64decode(s['data_base64']) for s in sources])
            self.assertEqual(['released/a.json','released/b.json'], [s['label'] for s in sources])
            self.assertEqual([0,1], [s['source_position'] for s in sources])
            self.assertTrue(all(s['source_kind']=='workshop_release' for s in sources))
            self.assertEqual(grids, contribute.gather_releases(keeper, include_shared=False))

    def test_companion_source_keeps_actual_life_and_recorded_origin_separate(self):
        from mecha_game.session import CompanionSession, load_session_inputs
        grid, profile, model = load_session_inputs(
            ROOT / 'data/seed_grids_16x16/mg_seed16_001_beetle.json',
            ROOT / 'data/slips/valid/slip_v2_cleanliness.json')
        session = CompanionSession(grid, profile, model=model).adopt(
            grid, profile, origin='era_elite', source=dict(campaign_id='prior',era_index=4,niche_key='1,2,3'))
        session.advance('feed')
        source = contribute.companion_release_source(session)
        self.assertEqual('keeper_companion', source['source_kind'])
        self.assertEqual(session.lineage[-1]['life_id'], source['life_id'])
        self.assertEqual({'feed': 1}, source['care_context']['care_summary']['keeper_actions'])
        self.assertEqual('prior', source['campaign_id'])
        self.assertNotIn('data_base64', source)
        self.assertNotIn('label', source)

    def test_cli_reproduction_bypasses_entry_and_uses_readonly_ledger(self):
        from mecha_game import execution_readout
        with tempfile.TemporaryDirectory() as directory:
            keeper = Path(directory)/'keeper'; keeper.mkdir()
            conn = sqlite3.connect(keeper/'campaign.sqlite3'); conn.execute('CREATE TABLE preserved (value)'); conn.execute('PRAGMA user_version=1'); conn.commit();conn.close()
            before = (keeper/'campaign.sqlite3').read_bytes()
            output = Path(directory)/'comparison'
            def reproduce(conn,campaign_id,era_index,**kwargs):
                self.assertEqual(('recorded',3),(campaign_id,era_index))
                with self.assertRaises(sqlite3.OperationalError): conn.execute('INSERT INTO preserved VALUES (1)')
                return dict(status='matched',reason=None,report={'complete':True},elites=[{'complete':True}])
            with patch('mecha_game.execution.reproduce_era',side_effect=reproduce), \
                 patch('mecha_game.app._run_selected',side_effect=AssertionError('must bypass companion entry')):
                with contextlib.redirect_stdout(io.StringIO()):
                    code=run(['--keeper-dir',str(keeper),'--reproduce-era','3','--campaign-id','recorded','--output',str(output)])
            self.assertEqual(0,code)
            self.assertEqual(before,(keeper/'campaign.sqlite3').read_bytes())
            self.assertEqual({'complete':True},json.loads((output/'report.json').read_text()))
            self.assertEqual([{'complete':True}],json.loads((output/'elites.json').read_text()))
            self.assertEqual('matched',json.loads((output/'comparison.json').read_text())['status'])

    def test_output_cannot_clobber_or_enter_keeper_and_statuses_differ(self):
        from mecha_game.execution_readout import reproduce_to_directory
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory)/'keeper';keeper.mkdir()
            conn=sqlite3.connect(keeper/'campaign.sqlite3');conn.execute('CREATE TABLE preserved (value)'); conn.execute('PRAGMA user_version=1');conn.commit();conn.close()
            before={p.name:p.read_bytes() for p in keeper.iterdir()}
            for output in (keeper,keeper/'child',Path(directory)):
                with self.subTest(output=output), self.assertRaises(ValueError):
                    reproduce_to_directory(keeper,'c',0,output)
            with patch('mecha_game.execution.reproduce_era',return_value={'status':'unavailable','reason':'missing inputs'}):
                result=reproduce_to_directory(keeper,'c',0,Path(directory)/'absent')
            self.assertEqual('unavailable',result['status'])
            self.assertEqual(before,{p.name:p.read_bytes() for p in keeper.iterdir()})
            for index,status in enumerate(('mismatch','unavailable')):
                with patch('mecha_game.execution.reproduce_era',return_value={'status':status,'reason':'control'}),contextlib.redirect_stdout(io.StringIO()):
                    code=run(['--keeper-dir',str(keeper),'--reproduce-era','0','--campaign-id','c','--output',str(Path(directory)/f'out-{index}')])
                self.assertEqual(index+1,code)

    def test_descendant_edges_use_report_events_not_authored_ancestors(self):
        from mecha_game.execution_readout import descendant_lines
        evidence={'status':'available','founder_occurrences':[dict(ordinal=0,grid_id='release',admitted=True,source_kind='workshop_release')],
                  'seed_ids':['seed']}
        elite={'grid_id':'candidate_c01','grid':{'lineage':{'ancestor_ids':['forged']}}}
        report={'generations':[{'creatures':[{'parent_grid_id':'release','candidate_grid_id':'candidate',
                                            'cycles':[{'cycle':1}],'archive_decision':'inserted'}]}]}
        lines=' '.join(descendant_lines(evidence,report,elite))
        self.assertIn('occurrence 0',lines)
        self.assertIn('recorded evaluation',lines.lower())
        self.assertNotIn('forged',lines)
        absent=' '.join(descendant_lines(evidence,{'generations':[]},elite))
        self.assertIn('unavailable',absent.lower())

    def test_automatic_and_unknown_founders_are_not_presented_as_user_releases(self):
        from mecha_game.execution_readout import descendant_lines, execution_lines
        report={'generations':[{'creatures':[{'parent_grid_id':'founder','candidate_grid_id':'candidate',
                                            'cycles':[{'cycle':1}],'archive_decision':'inserted'}]}]}
        for kind,expected in (('era_elite','Recorded prior-era founder'),('in_memory','Recorded in-memory founder')):
            row=dict(ordinal=0,grid_id='founder',source_position=0,source_kind=kind,admitted=True,
                     rejection_errors=None,campaign_id='prior',era_index=2,niche_key='1,2,3')
            evidence=dict(status='available',founder_occurrences=[row],seed_ids=[])
            lines=' '.join(execution_lines(evidence))
            self.assertIn('RECORDED FOUNDER OCCURRENCES',lines)
            self.assertNotIn('RECORDED RELEASE OCCURRENCES',lines)
            links=' '.join(descendant_lines(evidence,report,{'grid_id':'candidate_c01'}))
            self.assertIn(expected,links)
            self.assertNotIn('release origin',links.lower())
            self.assertIn('occurrence 0',links)
            self.assertIn('recorded evaluation',links.lower())

    def test_seed_and_duplicate_occurrence_collisions_are_explicitly_ambiguous(self):
        from mecha_game.execution_readout import descendant_lines
        occurrence=dict(ordinal=0,grid_id='release',admitted=True,source_kind='workshop_release')
        report={'generations':[{'creatures':[{'parent_grid_id':'release','candidate_grid_id':'candidate',
                                            'cycles':[{'cycle':1}],'archive_decision':'inserted'}]}]}
        for evidence in ({'status':'available','founder_occurrences':[occurrence],'seed_ids':['release']},
                         {'status':'available','founder_occurrences':[occurrence,dict(occurrence,ordinal=1)],'seed_ids':[]}):
            lines=' '.join(descendant_lines(evidence,report,{'grid_id':'candidate_c01'}))
            self.assertIn('ambiguous',lines.lower())
            self.assertNotIn('Recorded release origin:',lines)


class ExecutionNativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from mecha_game.campaign import KeeperCampaign, TINY_ERA_CONFIG, load_campaign_inputs
        from mecha_game.session import load_session_inputs
        cls.inputs=load_campaign_inputs(ROOT/'data/seed_grids_16x16',ROOT/'data/slips/valid/slip_v2_cleanliness.json',
            ROOT/'data/readability_benchmark/adopted_readability_model.json',repair_epochs=6,seed_limit=12)
        cls.release=copy.deepcopy(cls.inputs['seed_grids'][1]);cls.release['grid_id']='x5-native-release'
        cls.campaign=KeeperCampaign(cls.inputs,era_config=TINY_ERA_CONFIG,campaign_id='x5-client')
        cls.campaign.advance_era('calm',released_grids=[cls.release],released_sources=[dict(
            role='founder',source_kind='workshop_release',source_position=0,label='released/selected.json',
            data_base64=base64.b64encode(json.dumps(cls.release,indent=1).encode()).decode())],record_original=True)
        cls.pet=load_session_inputs(ROOT/'data/seed_grids_16x16/mg_seed16_001_beetle.json',
                                  ROOT/'data/slips/valid/slip_v2_cleanliness.json')

    def setUp(self):
        from mecha_game.session import CompanionSession
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.keeper=Path(self.tmp.name)/'keeper'
        self.campaign.save(self.keeper/'campaign.sqlite3')
        self.campaign.save_state(self.keeper/'campaign_state.json')
        self.session=CompanionSession(*self.pet[:2],model=self.pet[2])
        self.session.save_checkpoint(self.keeper/'companion.json')

    def files(self):
        return {p.relative_to(self.keeper).as_posix():p.read_bytes() for p in self.keeper.rglob('*') if p.is_file()}

    def invoke(self,batches,*,on_draw=None,on_flip=None):
        import pygame
        from mecha_game.footer import FooterPager
        from mecha_game.native_ui import ActionStrip
        sequence=iter(batches);self.lines=[];self.draws=[];self.strips=[]
        original=FooterPager.layout;original_draw=ActionStrip.draw
        def events():
            batch=next(sequence,[pygame.event.Event(pygame.QUIT)])
            return batch() if callable(batch) else batch
        def capture(pager,lines,*args,**kwargs):
            self.lines.append(list(lines));return original(pager,lines,*args,**kwargs)
        def draw(strip,*args):
            result=original_draw(strip,*args)
            self.draws.append([action.id for action in strip.actions]);self.strips.append(strip)
            if on_draw:on_draw(strip)
            return result
        with patch.dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'), \
             patch('pygame.event.get',side_effect=events),patch.object(FooterPager,'layout',capture), \
             patch.object(ActionStrip,'draw',draw),patch('pygame.display.flip',side_effect=on_flip):
            return run(['--keeper-dir',str(self.keeper),'--era-scale','tiny','--scale','2','--fps','0','--tick-frames','1'])

    def test_native_explicit_action_uses_worker_readonly_connection_and_preserves_all_bytes(self):
        import pygame
        from mecha_game.session import CompanionSession
        def key(code):return pygame.event.Event(pygame.KEYDOWN,key=code,mod=0,repeat=False)
        calls=[];before=self.files()
        def reproduce(conn,campaign_id,era_index,**kwargs):
            calls.append((threading.current_thread().name,campaign_id,era_index))
            with self.assertRaises(sqlite3.OperationalError):conn.execute('CREATE TABLE forbidden (value)')
            kwargs['progress_callback'](1,1)
            return {'status':'matched','reason':None,'report':{},'elites':[]}
        def select():
            strip=self.strips[-1];enabled=[a.id for a in strip.actions if a.enabled]
            self.assertIn('reproduce',enabled)
            return [key(pygame.K_F6),key(pygame.K_HOME),*[key(pygame.K_RIGHT) for _ in range(enabled.index('reproduce'))]]
        with patch('mecha_game.execution.reproduce_era',side_effect=reproduce), \
             patch.object(CompanionSession,'advance',side_effect=AssertionError('reading/comparison must pause care')):
            code=self.invoke([[key(pygame.K_t)],select,[key(pygame.K_RETURN)]])
        self.assertEqual(0,code)
        self.assertEqual([('mechagotchi-era','x5-client',0)],calls)
        self.assertTrue(any('REPRODUCING ERA' in ' '.join(lines) for lines in self.lines))
        self.assertTrue(any('Reproduction MATCHED' in ' '.join(lines) for lines in self.lines))
        self.assertEqual(before,self.files())
        self.assertFalse(any(t.name=='mechagotchi-era' for t in threading.enumerate()))

    def test_native_cancel_and_help_join_worker_without_saving_or_queuing_input(self):
        import pygame
        from mecha_game.session import CompanionSession
        def key(code):return pygame.event.Event(pygame.KEYDOWN,key=code,mod=0,repeat=False)
        before=self.files();posted=[]
        def reproduce(conn,campaign_id,era_index,*,progress_callback):
            work=progress_callback.__self__
            work.cancel_requested.wait(3)
            progress_callback(0,1)
            raise AssertionError('Native comparison did not accept cancel')
        def draw(strip):
            if 'cancel_work' not in [a.id for a in strip.actions]:return
            if len(posted)==0:
                posted.append('help');pygame.event.post(key(pygame.K_F1))
            elif len(posted)==1:
                posted.append('cancel');pygame.event.post(key(pygame.K_ESCAPE));pygame.event.post(key(pygame.K_ESCAPE))
        with patch('mecha_game.execution.reproduce_era',side_effect=reproduce), \
             patch.object(CompanionSession,'advance',side_effect=AssertionError('comparison must pause care')):
            code=self.invoke([[key(pygame.K_t)],[key(pygame.K_d),key(pygame.K_f),key(pygame.K_d)]],on_draw=draw)
        self.assertEqual(0,code)
        self.assertEqual(['help','cancel'],posted)
        self.assertTrue(any('help; care paused' in ' '.join(lines) for lines in self.lines))
        self.assertTrue(any('Reproduction cancelled' in ' '.join(lines) for lines in self.lines))
        self.assertEqual(before,self.files())
        self.assertFalse(any(t.name=='mechagotchi-era' for t in threading.enumerate()))

    def test_reading_new_and_old_history_never_reproduces_and_keeps_public_shape(self):
        from mecha_engine.storage import campaign_history
        from mecha_game.era_review import EraReview
        from mecha_game.repertoire import RepertoireBrowser
        before=self.files()
        with patch('mecha_game.execution.reproduce_era',side_effect=AssertionError('viewing cannot simulate')):
            view=EraReview.load(self.keeper)
            browser=RepertoireBrowser.load(self.keeper)
        conn=sqlite3.connect(self.keeper/'campaign.sqlite3')
        try:self.assertEqual(campaign_history(conn,'x5-client'),view.history)
        finally:conn.close()
        self.assertEqual('available',view.execution['status'])
        self.assertNotIn('blobs',view.execution)
        self.assertIn('Occurrence 0',' '.join(view.lines()))
        self.assertIn('released/selected.json',' '.join(view.lines()))
        self.assertIn('REPRODUCTION: available',' '.join(browser.execution_lines()))
        self.assertEqual(before,self.files())
        # A genuine historical schema has no execution tables. Read-only consumers must not migrate it.
        conn=sqlite3.connect(self.keeper/'campaign.sqlite3')
        for table in ('founder_occurrences','era_executions','execution_blobs'):conn.execute('DROP TABLE '+table)
        conn.execute('PRAGMA user_version=1');conn.commit();conn.close()
        before=self.files()
        with patch('mecha_game.execution.reproduce_era',side_effect=AssertionError('old views cannot simulate')):
            old=EraReview.load(self.keeper)
            RepertoireBrowser.load(self.keeper)
        self.assertEqual(view.history,old.history)
        self.assertEqual('unavailable',old.execution['status'])
        self.assertIn('unavailable',' '.join(old.lines()).lower())
        self.assertEqual(before,self.files())

    def test_corrupt_execution_is_unavailable_without_hiding_legacy_report(self):
        from mecha_game.era_review import EraReview
        original=EraReview.load(self.keeper).history
        conn=sqlite3.connect(self.keeper/'campaign.sqlite3')
        conn.execute("UPDATE execution_blobs SET payload = ? WHERE sha256 = (SELECT sha256 FROM execution_blobs LIMIT 1)",(b'invalid retained bytes',))
        conn.commit();conn.close()
        before=self.files()
        view=EraReview.load(self.keeper)
        self.assertIsNone(view.error)
        self.assertEqual(original,view.history)
        self.assertEqual('unavailable',view.execution['status'])
        self.assertIn('cannot be verified',' '.join(view.lines()))
        self.assertEqual(before,self.files())

    def test_native_gather_and_companion_stage_retain_exact_sources_through_restart(self):
        import pygame
        from mecha_game.era_plan import EraPlan
        def key(code):return pygame.event.Event(pygame.KEYDOWN,key=code,mod=0,repeat=False)
        inbox=self.keeper/'released';inbox.mkdir()
        raw=json.dumps(self.release,indent=3).replace('\n','\r\n').encode()
        (inbox/'selected.json').write_bytes(raw)
        before=(self.keeper/'companion.json').read_bytes()
        with patch.object(_EraBench,'ensure',side_effect=AssertionError('staging must not load models')):
            self.assertEqual(0,self.invoke([[key(pygame.K_t)],[key(pygame.K_w)],[key(pygame.K_r)],[key(pygame.K_w)]]))
        plan=EraPlan(self.keeper/'era_plan.json')
        self.assertIsNone(plan.error)
        self.assertEqual(2,len(plan.releases))
        self.assertEqual(raw,base64.b64decode(plan.release_sources[0]['data_base64']))
        self.assertEqual(self.session.lineage[-1]['life_id'],plan.release_sources[1]['life_id'])
        self.assertEqual('keeper_companion',plan.release_sources[1]['source_kind'])
        self.assertEqual(before,(self.keeper/'companion.json').read_bytes())


if __name__=='__main__': unittest.main()
