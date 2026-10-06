"""V1: exact stored niche occurrences and recorded campaign links, not ancestry."""
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
for sub in ('game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT / sub))
import pygame
from mecha_game.app import run
from mecha_game.campaign import KeeperCampaign, TINY_ERA_CONFIG, load_campaign_inputs
from mecha_game.footer import FooterPager
from mecha_game.repertoire import RepertoireBrowser
from mecha_game.session import CompanionSession, load_session_inputs
from mecha_game.original_recording import save_original_recording


def inventory(path):
    return {p.relative_to(path).as_posix(): p.read_bytes() for p in path.rglob('*')
            if p.is_file() and 'model_cache' not in p.parts}


def key(value, ctrl=False):
    return pygame.event.Event(pygame.KEYDOWN, key=value, mod=pygame.KMOD_CTRL if ctrl else 0)


class NicheHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_campaign_inputs(ROOT/'data/seed_grids_16x16', ROOT/'data/slips/valid/slip_v2_cleanliness.json',
            ROOT/'data/readability_benchmark/adopted_readability_model.json', repair_epochs=6, seed_limit=12)
        cls.campaigns = []
        cls.recordings = []
        for name, predecessor in [('older', None), ('middle', 'older'), ('current', 'middle')]:
            # Synthetic history links follow closed prior bloodlines.
            if predecessor is not None:
                cls.campaigns[-1].campaign['status'] = 'extinct'
            # The recorded predecessor link carries its actual earned facts.
            inherited = cls.campaigns[-1].unlock_state() if predecessor is not None else []
            campaign = KeeperCampaign(cls.inputs, campaign_id=name, predecessor_campaign_id=predecessor,
                                      era_config=TINY_ERA_CONFIG, inherited_unlocks=inherited)
            records = []
            for weather in ('calm', 'storm'):
                campaign.advance_era(weather, record_original=True)
                records.append(copy.deepcopy(campaign.last_original_recording))
            cls.campaigns.append(campaign); cls.recordings.append(records)
        cls.pet = load_session_inputs(ROOT/'data/seed_grids_16x16/mg_seed16_001_beetle.json', ROOT/'data/slips/valid/slip_v2_cleanliness.json')

    def seed(self, keeper, policy='incumbent'):
        for campaign, recordings in zip(self.campaigns, self.recordings):
            campaign.save(keeper/'campaign.sqlite3')
            for recording in recordings:
                save_original_recording(recording, keeper, keeper/'campaign.sqlite3')
        self.campaigns[-1].save_state(keeper/'campaign_state.json')
        grid, slip, model = self.pet
        CompanionSession(grid, slip, model=model, learning_policy=policy).save_checkpoint(keeper/'companion.json')

    def observe(self, keeper, batches):
        events = iter(batches); pages=[]; original=FooterPager.layout
        def capture(pager, lines, measure, width, height):
            page=original(pager, lines, measure, width, height)
            pages.append({'all':list(lines),'visible':list(page.lines)})
            return page
        with patch.dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy'), \
             patch('pygame.event.get', side_effect=lambda: next(events,[pygame.event.Event(pygame.QUIT)])), \
             patch.object(FooterPager,'layout',capture), \
             patch('mecha_game.campaign.evolve',side_effect=AssertionError('browsing must not evolve')):
            code=run(['--keeper-dir',str(keeper),'--scale','1','--fps','0','--tick-frames','1'])
        return code,pages

    def test_chain_uses_recorded_links_and_preserves_records(self):
        from mecha_game.niche_history import CampaignStory
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory); self.seed(keeper); before=inventory(keeper)
            story=CampaignStory.load(keeper)
            self.assertEqual(['older','middle','current'],[v.history['campaign_id'] for v in story.views])
            self.assertEqual('current',story.current.history['campaign_id'])
            story.move(-1); self.assertEqual('middle',story.current.history['campaign_id'])
            story.select('older'); self.assertEqual(self.campaigns[0].eras[-1]['report'],story.current.current['report'])
            self.assertEqual(before,inventory(keeper))

    def test_niche_history_exact_matches_have_original_provenance(self):
        from mecha_game.niche_history import NicheHistory
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory); self.seed(keeper); before=inventory(keeper)
            browser=RepertoireBrowser.load(keeper); selected=copy.deepcopy(browser.current())
            history=NicheHistory.load(keeper,browser)
            expected=[(c.campaign['campaign_id'],e['era_index'],r) for c in self.campaigns for e in c.eras
                      for r in e['elites'] if r['descriptor']['values']==selected['descriptor']['values']]
            actual=[(e['campaign_id'],e['era_index'],e['elites'][0]) for e in history.eras]
            self.assertEqual(expected,actual)
            self.assertGreaterEqual(len(actual),3)
            self.assertIs(browser,history.origin)
            self.assertEqual('current',history.campaign_id)
            history.back(); self.assertEqual(selected['descriptor']['values'],history.current()['descriptor']['values'])
            self.assertIn('not recorded', ' '.join(history.history_lines()).lower())
            self.assertEqual(before,inventory(keeper))

    def test_missing_and_cyclic_predecessors_are_visible_and_bounded(self):
        from mecha_game.niche_history import CampaignStory
        for predecessor,word in [('missing','unavailable'),('current','cycle')]:
            with self.subTest(predecessor=predecessor), tempfile.TemporaryDirectory() as directory:
                keeper=Path(directory);self.seed(keeper)
                with closing(sqlite3.connect(keeper/'campaign.sqlite3')) as conn:
                    conn.execute('UPDATE campaigns SET predecessor_campaign_id=? WHERE campaign_id=?',(predecessor,'older'));conn.commit()
                before=inventory(keeper); story=CampaignStory.load(keeper)
                self.assertEqual('current',story.current.history['campaign_id'])
                self.assertIn(word,' '.join(v.error or '' for v in story.views).lower())
                self.assertLessEqual(len(story.views),4)
                self.assertEqual(before,inventory(keeper))

    def test_incompatible_and_missing_era_archives_remain_explicit(self):
        from mecha_game.niche_history import NicheHistory
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper)
            with closing(sqlite3.connect(keeper/'campaign.sqlite3')) as conn:
                records=conn.execute('SELECT niche_key,elite_json FROM elites WHERE campaign_id=? AND era_index=1',('older',)).fetchall()
                for niche,blob in records:
                    record=json.loads(blob);record['descriptor']['names']=['E5']
                    conn.execute('UPDATE elites SET elite_json=? WHERE campaign_id=? AND era_index=1 AND niche_key=?',(json.dumps(record),'older',niche))
                conn.execute('DELETE FROM elites WHERE campaign_id=? AND era_index=0',('middle',));conn.commit()
            before=inventory(keeper);history=NicheHistory.load(keeper,RepertoireBrowser.load(keeper))
            warnings=' '.join(history.history_lines()).lower()
            self.assertIn('older',warnings);self.assertIn('incompatible',warnings)
            self.assertIn('middle',warnings);self.assertIn('missing',warnings)
            self.assertTrue(history.eras); self.assertEqual(before,inventory(keeper))

    def test_unsupported_selected_axes_are_not_reinterpreted(self):
        from mecha_game.niche_history import NicheHistory
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper);browser=RepertoireBrowser.load(keeper)
            browser.current()['descriptor']['names']=['symmetry','visual_complexity','behavior_neediness']
            with self.assertRaisesRegex(ValueError,'seven-axis'):
                NicheHistory.load(keeper,browser)

    def test_source_navigates_campaign_archive_history_and_report_read_only(self):
        for policy in ('incumbent','qtable'):
            with self.subTest(policy=policy),tempfile.TemporaryDirectory() as directory:
                keeper=Path(directory);self.seed(keeper,policy);before=inventory(keeper)
                code,pages=self.observe(keeper,[[key(pygame.K_l)],[key(pygame.K_t)],
                    [key(pygame.K_LEFTBRACKET,True)],[key(pygame.K_b)],[key(pygame.K_n)],
                    [key(pygame.K_COMMA)],[key(pygame.K_t)],[pygame.event.Event(pygame.QUIT)]])
                texts=[' '.join(p['all']) for p in pages]
                self.assertEqual(0,code)
                self.assertIn('middle',texts[2]); self.assertIn('middle',texts[3])
                self.assertIn('NICHE HISTORY',texts[4]);self.assertIn('older',texts[5]);self.assertIn('older',texts[6])
                self.assertEqual(before,inventory(keeper))

    def test_history_replay_return_and_archive_return_preserve_selected_occurrence(self):
        for policy in ('incumbent','qtable'):
            with self.subTest(policy=policy),tempfile.TemporaryDirectory() as directory:
                keeper=Path(directory);self.seed(keeper,policy)
                era=self.campaigns[-1].eras[-1]
                best=max(era['elites'],key=lambda e:(e['fitness'],e['niche_key']))
                position=era['elites'].index(best)
                batches=[[key(pygame.K_b)]]+[[key(pygame.K_PERIOD)]]*position
                start=len(batches)
                batches += [[key(pygame.K_n)],[key(pygame.K_COMMA)],[key(pygame.K_v)],
                            [key(pygame.K_F1)],[key(pygame.K_ESCAPE)],[key(pygame.K_v)],
                            [key(pygame.K_n)],[pygame.event.Event(pygame.QUIT)]]
                before=inventory(keeper)
                with patch('mecha_game.replay.live_cycle',side_effect=AssertionError('no reconstruction')):
                    code,pages=self.observe(keeper,batches)
                texts=[' '.join(p['all']) for p in pages]
                self.assertEqual(0,code);self.assertIn('NICHE HISTORY',texts[start])
                self.assertIn('Original era evaluation',texts[start+2])
                self.assertEqual(texts[start+1],texts[start+5])
                self.assertIn('REPERTOIRE',texts[start+6]);self.assertIn(best['grid_id'],texts[start+6])
                self.assertEqual(before,inventory(keeper))

    def test_history_adoption_uses_active_covenant_and_preserves_campaign(self):
        for allowed in (True,False):
            with self.subTest(allowed=allowed),tempfile.TemporaryDirectory() as directory:
                keeper=Path(directory);self.seed(keeper,'qtable')
                if not allowed:
                    state=json.loads((keeper/'campaign_state.json').read_text(encoding='utf-8'))
                    state['slip_profile']['grid']['allowed_palettes']=['not_the_saved_palette']
                    (keeper/'campaign_state.json').write_text(json.dumps(state),encoding='utf-8')
                before=inventory(keeper);expected=self.campaigns[-1].eras[-1]['elites'][0]['grid']
                code,pages=self.observe(keeper,[[key(pygame.K_b)],[key(pygame.K_n)],[key(pygame.K_COMMA)],
                    [key(pygame.K_a)],[pygame.event.Event(pygame.QUIT)]])
                self.assertEqual(0,code)
                after=inventory(keeper)
                for name,value in before.items():
                    if not name.startswith(('companion','lineage')):self.assertEqual(value,after[name],name)
                if allowed:
                    pet=CompanionSession.load(keeper/'companion.json')
                    self.assertEqual(expected,pet.grid);self.assertEqual('qtable',pet.learning_policy)
                    self.assertEqual('era_elite',pet.lineage[-1]['origin'])
                else:
                    self.assertIn('refused',' '.join(pages[3]['all']).lower())
                    self.assertEqual(before,after)

    def test_lineage_pause_ignores_care_and_does_not_queue_it_on_return(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper);before=inventory(keeper)
            code,pages=self.observe(keeper,[[key(pygame.K_l)],[key(pygame.K_f),key(pygame.K_s)],
                [key(pygame.K_F1)],[key(pygame.K_ESCAPE)],[pygame.event.Event(pygame.QUIT)]])
            self.assertEqual(0,code);self.assertEqual(before,inventory(keeper))

    def test_empty_campaign_and_missing_body_are_explicit_without_fallback(self):
        from mecha_game.niche_history import NicheHistory,CampaignStory
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper)
            with closing(sqlite3.connect(keeper/'campaign.sqlite3')) as conn:
                conn.execute('DELETE FROM eras WHERE campaign_id=?',('middle',))
                for niche,blob in conn.execute('SELECT niche_key,elite_json FROM elites WHERE campaign_id=?',('older',)).fetchall():
                    record=json.loads(blob);record.pop('grid',None)
                    conn.execute('UPDATE elites SET elite_json=? WHERE campaign_id=? AND niche_key=?',(json.dumps(record),'older',niche))
                conn.commit()
            before=inventory(keeper);history=NicheHistory.load(keeper,RepertoireBrowser.load(keeper))
            notices=' '.join(history.history_lines())
            self.assertIn('middle: no eras recorded',notices);self.assertIn('matching body unavailable',notices)
            story=CampaignStory.load(keeper);story.select('middle');self.assertIsNone(story.current.current)
            self.assertEqual(before,inventory(keeper))

    def test_missing_campaign_does_not_claim_no_predecessor(self):
        from mecha_game.niche_history import CampaignStory
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper)
            with closing(sqlite3.connect(keeper/'campaign.sqlite3')) as conn:
                conn.execute('UPDATE campaigns SET predecessor_campaign_id=? WHERE campaign_id=?',('missing','older'));conn.commit()
            story=CampaignStory.load(keeper);story.select('missing')
            self.assertIn('Recorded predecessor: not recorded',story.lines())

    def test_unavailable_campaign_can_page_details_and_return_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper)
            with closing(sqlite3.connect(keeper/'campaign.sqlite3')) as conn:
                conn.execute('UPDATE campaigns SET predecessor_campaign_id=? WHERE campaign_id=?',('missing','older'));conn.commit()
            before=inventory(keeper)
            code,pages=self.observe(keeper,[[key(pygame.K_t)],[key(pygame.K_LEFTBRACKET,True)],
                [key(pygame.K_LEFTBRACKET,True)],[key(pygame.K_LEFTBRACKET,True)],
                [key(pygame.K_PAGEDOWN)],[key(pygame.K_RIGHTBRACKET,True)],[pygame.event.Event(pygame.QUIT)]])
            self.assertEqual(0,code)
            self.assertIn('Recorded predecessor: not recorded',' '.join(pages[4]['visible']))
            self.assertIn('older',' '.join(pages[5]['all']))
            self.assertEqual(before,inventory(keeper))
