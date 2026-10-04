"""T2: saved bodies, truthful historical display and explicit current-covenant adoption."""
import copy
import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
for folder in ('game/src','packages/mecha_engine/src'):
    sys.path.insert(0,str(ROOT/folder))
import pygame
from mecha_engine.genome import render_packet_v2
from mecha_game.app import _EraBench,run
from mecha_game.campaign import KeeperCampaign,TINY_ERA_CONFIG,load_campaign_inputs
from mecha_game.footer import FooterPager
from mecha_game.repertoire import RepertoireBrowser
from mecha_game.session import CompanionSession,load_session_inputs

def key(value):return pygame.event.Event(pygame.KEYDOWN,key=value,mod=0)
def inventory(path):return {p.relative_to(path).as_posix():p.read_bytes() for p in path.rglob('*') if p.is_file()}

class SavedArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs=load_campaign_inputs(ROOT/'data/seed_grids_16x16',ROOT/'data/slips/valid/slip_v2_cleanliness.json',ROOT/'data/readability_benchmark/adopted_readability_model.json',repair_epochs=6,seed_limit=12)
        cls.campaign=KeeperCampaign(cls.inputs,era_config=TINY_ERA_CONFIG,campaign_id='saved_archive')
        cls.campaign.advance_era('calm')
        cls.campaign.advance_era('storm')
        cls.pet=load_session_inputs(ROOT/'data/seed_grids_16x16/mg_seed16_001_beetle.json',ROOT/'data/slips/valid/slip_v2_cleanliness.json')

    def seed(self,keeper,*,campaign=True):
        grid,slip,model=self.pet
        CompanionSession(grid,slip,model=model,learning_policy='qtable').save_checkpoint(keeper/'companion.json')
        if campaign:
            self.campaign.save(keeper/'campaign.sqlite3')
            self.campaign.save_state(keeper/'campaign_state.json')

    def events(self,keeper,rows):
        sequence=iter(rows)
        pages=[]
        batch=-1
        def poll():
            nonlocal batch
            batch+=1
            return next(sequence,[pygame.event.Event(pygame.QUIT)])
        layout=FooterPager.layout
        def capture(pager,lines,measure,width,height):
            page=layout(pager,lines,measure,width,height)
            # Final casing per input batch; progress frames are separate observations.
            value={'all':list(lines),'visible':list(page.lines)}
            if len(pages)<=batch:pages.append(value)
            else:pages[batch]=value
            return page
        with patch.dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'),patch('pygame.event.get',side_effect=poll),patch.object(FooterPager,'layout',capture):
            code=run(['--keeper-dir',str(keeper),'--era-scale','tiny','--scale','1','--fps','0','--tick-frames','1'])
        return code,pages

    def test_saved_records_match_and_do_not_hydrate_live_campaign(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper)
            before=inventory(keeper)
            browser=RepertoireBrowser.load(keeper)
            self.assertEqual(self.campaign.eras[-1]['elites'],browser.elites)
            browser.previous_era()
            self.assertEqual(self.campaign.eras[0]['elites'],browser.elites)
            self.assertEqual(before,inventory(keeper))
            resumed=KeeperCampaign.load_state(self.inputs,keeper/'campaign_state.json',keeper/'campaign.sqlite3')
            self.assertEqual([],resumed.eras)
            self.assertEqual(2,resumed.era_offset)

    def test_selected_era_uses_its_recorded_covenant_for_packet(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper)
            state=keeper/'campaign_state.json'
            payload=json.loads(state.read_text(encoding='utf-8'))
            payload['slip_profile']['grid']['allowed_palettes']=['not_the_saved_palette']
            state.write_text(json.dumps(payload),encoding='utf-8')
            browser=RepertoireBrowser.load(keeper,era_index=0)
            expected=render_packet_v2(self.campaign.eras[0]['elites'][0]['grid'],None,slip_profile=self.campaign.campaign['slip_profile'])
            self.assertEqual(expected,browser.packet())
            self.assertIn('era 0',browser.caption())

    def test_empty_saved_era_is_safe_and_navigation_clamps(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper)
            conn=sqlite3.connect(keeper/'campaign.sqlite3')
            report=copy.deepcopy(self.campaign.eras[-1]['report']);report['summary']['archive']['filled_niches']=0
            conn.execute('DELETE FROM elites WHERE era_index=1')
            conn.execute('UPDATE eras SET report_json=? WHERE era_index=1',(json.dumps(report),))
            conn.commit();conn.close()
            browser=RepertoireBrowser.load(keeper)
            self.assertEqual(0,browser.count)
            self.assertIsNone(browser.current());self.assertIsNone(browser.packet())
            self.assertEqual(0,browser.step());self.assertEqual(0,browser.back())
            self.assertIn('0 elites',browser.caption())
            browser.previous_era();self.assertGreater(browser.count,0)
            browser.next_era();browser.next_era();self.assertEqual(1,browser.era_index)
            self.assertEqual(0,self.events(keeper,[[key(pygame.K_b)],[pygame.event.Event(pygame.QUIT)]])[0])

    def test_corrupt_elite_is_explicit_without_writes_or_crash(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper)
            conn=sqlite3.connect(keeper/'campaign.sqlite3')
            conn.execute("UPDATE elites SET elite_json='[]' WHERE era_index=1")
            conn.commit();conn.close()
            before=inventory(keeper)
            with self.assertRaises(ValueError):RepertoireBrowser.load(keeper)
            code,pages=self.events(keeper,[[key(pygame.K_b)],[key(pygame.K_e),key(pygame.K_c),key(pygame.K_a)],[pygame.event.Event(pygame.QUIT)]])
            self.assertEqual(0,code)
            self.assertIn('unavailable',' '.join(pages[0]['all']).lower())
            self.assertEqual(before,inventory(keeper))

    def test_saved_browser_pauses_ignores_care_and_does_not_train(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper)
            before=inventory(keeper)
            with patch.object(_EraBench,'ensure',side_effect=AssertionError('reading archive must not train')):
                code,pages=self.events(keeper,[[key(pygame.K_b)],[key(pygame.K_f),key(pygame.K_s)],[key(pygame.K_PERIOD)],[key(pygame.K_F1)],[key(pygame.K_ESCAPE)],[pygame.event.Event(pygame.QUIT)]])
            self.assertEqual(0,code)
            self.assertIn('REPERTOIRE',' '.join(pages[0]['all']))
            self.assertEqual(before,inventory(keeper))

    def test_report_selected_era_browser_and_escape_return(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper)
            code,pages=self.events(keeper,[[key(pygame.K_t)],[key(pygame.K_LEFTBRACKET)],[key(pygame.K_b)],[key(pygame.K_PERIOD)],[key(pygame.K_ESCAPE)],[key(pygame.K_ESCAPE)],[pygame.event.Event(pygame.QUIT)]])
            self.assertEqual(0,code)
            self.assertIn('REPERTOIRE  era 0',' '.join(pages[2]['all']))
            self.assertTrue(pages[4]['all'][0].startswith('ERA 0 '))
            self.assertEqual(1,CompanionSession.load(keeper/'companion.json').state['age_ticks'])

    def test_browser_t_opens_its_selected_report(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper)
            code,pages=self.events(keeper,[[key(pygame.K_b)],[key(pygame.K_LEFTBRACKET)],[key(pygame.K_t)],[pygame.event.Event(pygame.QUIT)]])
            self.assertEqual(0,code)
            self.assertTrue(pages[2]['all'][0].startswith('ERA 0 '))
            self.assertEqual(0,CompanionSession.load(keeper/'companion.json').state['age_ticks'])

    def test_restart_adoption_uses_selected_grid_and_preserves_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper)
            old=(keeper/'campaign.sqlite3').read_bytes()
            code,pages=self.events(keeper,[[key(pygame.K_b)],[key(pygame.K_PERIOD)],[key(pygame.K_a)],[pygame.event.Event(pygame.QUIT)]])
            self.assertEqual(0,code)
            pet=CompanionSession.load(keeper/'companion.json')
            self.assertEqual(self.campaign.eras[-1]['elites'][1]['grid'],pet.grid)
            self.assertEqual('qtable',pet.learning_policy)
            self.assertEqual('era_elite',pet.lineage[-1]['origin'])
            self.assertEqual(old,(keeper/'campaign.sqlite3').read_bytes())
            self.assertNotIn('REPERTOIRE',' '.join(pages[2]['all']))

    def test_refused_adoption_keeps_pet_and_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper)
            path=keeper/'campaign_state.json'
            payload=json.loads(path.read_text(encoding='utf-8'))
            payload['slip_profile']['grid']['allowed_palettes']=['not_the_saved_palette']
            path.write_text(json.dumps(payload),encoding='utf-8')
            pet=(keeper/'companion.json').read_bytes();ledger=(keeper/'campaign.sqlite3').read_bytes()
            code,pages=self.events(keeper,[[key(pygame.K_b)],[key(pygame.K_a)],[pygame.event.Event(pygame.QUIT)]])
            self.assertEqual(0,code)
            self.assertIn('refused',' '.join(pages[1]['all']).lower())
            self.assertEqual(pet,(keeper/'companion.json').read_bytes())
            self.assertEqual(ledger,(keeper/'campaign.sqlite3').read_bytes())

    def test_empty_history_browser_pauses_and_covenant_controls_are_first(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper,campaign=False)
            code,pages=self.events(keeper,[[key(pygame.K_b)],[key(pygame.K_s)],[key(pygame.K_ESCAPE)],[pygame.event.Event(pygame.QUIT)]])
            self.assertEqual(0,code)
            self.assertIn('No recorded eras',' '.join(pages[0]['all']))
            self.assertEqual(1,CompanionSession.load(keeper/'companion.json').state['age_ticks'])
            self.assertFalse((keeper/'campaign.sqlite3').exists())
            code,pages=self.events(keeper,[[key(pygame.K_c)],[pygame.event.Event(pygame.QUIT)]])
            lines=pages[0]['all']
            self.assertLess(next(i for i,x in enumerate(lines) if 'COVENANT' in x),next(i for i,x in enumerate(lines) if x.startswith('health ')))

    def test_empty_archive_can_run_first_era_without_care_tick(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper,campaign=False)
            code,pages=self.events(keeper,[[key(pygame.K_b)],[key(pygame.K_e)],[pygame.event.Event(pygame.QUIT)]])
            self.assertEqual(0,code)
            self.assertTrue(pages[1]['all'][0].startswith('ERA 0 '))
            self.assertEqual(0,CompanionSession.load(keeper/'companion.json').state['age_ticks'])

if __name__=='__main__':unittest.main()
