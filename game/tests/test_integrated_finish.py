"""W5: connected readers preserve care, selection and all recorded facts."""
import copy,json,os,shutil,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
for folder in ('game/src','packages/mecha_engine/src'):sys.path.insert(0,str(ROOT/folder))
import pygame
from mecha_game.app import run,_EraBench
from mecha_game.footer import FooterPager
from mecha_game.session import CompanionSession
from mecha_game.lineage import LineageBrowser
from mecha_game.packs import build_pack,write_pack

def key(k,mod=0):return pygame.event.Event(pygame.KEYDOWN,key=k,mod=mod)
def files(root):return {p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob('*') if p.is_file()}

class IntegratedFinishTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.temporary.cleanup)
        cls.seed=Path(cls.temporary.name)/'seed'
        with patch.dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'):
            assert run(['--keeper-dir',str(cls.seed),'--era-scale','tiny','--eras','1','--ticks','1','--tick-frames','1','--fps','0','--scale','1'])==0
        profile=json.loads((ROOT/'data/slips/valid/slip_lcd_seed.json').read_text(encoding='utf-8'))
        (cls.seed/'covenants').mkdir(exist_ok=True)
        for name in ('a','z'):(cls.seed/'covenants'/f'{name}.json').write_text(json.dumps(dict(profile,profile_id=name)),encoding='utf-8')
        pack=build_pack(pack_id='finish_test',title='Finish test',provenance={'source':'diagnostic'},slips=[profile],creatures=[])
        for name in ('a','z'):write_pack(pack,cls.seed/'packs'/f'{name}.json')

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.keeper=Path(self.temp.name)/'keeper';shutil.copytree(self.seed,self.keeper)

    def observe(self,batches):
        sequence=iter(batches);pages=[];original=FooterPager.layout
        def poll():
            batch=next(sequence,[pygame.event.Event(pygame.QUIT)])
            return batch() if callable(batch) else batch
        def capture(pager,lines,measure,width,rows):
            page=original(pager,lines,measure,width,rows)
            pages.append({'all':list(lines),'visible':list(page.lines),'page':page.page,'pages':page.page_count})
            self.assertTrue(all(measure(line)<=width for line in page.lines))
            self.assertLessEqual(len(page.lines),rows)
            return page
        with patch.dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'),patch('pygame.event.get',side_effect=poll),patch.object(FooterPager,'layout',capture):
            self.assertEqual(0,run(['--keeper-dir',str(self.keeper),'--era-scale','tiny','--scale','1','--fps','0','--tick-frames','1']))
        return pages

    def test_all_readers_close_without_care_or_command_leak(self):
        for opening,closing in ((pygame.K_F1,pygame.K_F1),(pygame.K_t,pygame.K_t),(pygame.K_b,pygame.K_b),(pygame.K_v,pygame.K_v),(pygame.K_l,pygame.K_l),(pygame.K_h,pygame.K_h),(pygame.K_i,pygame.K_i)):
            for close in (closing,pygame.K_ESCAPE):
                with self.subTest(opening=opening,close=close):
                    before=files(self.keeper)
                    self.observe([[key(opening)],[key(close),key(pygame.K_f),key(pygame.K_5)]])
                    self.assertEqual(before,files(self.keeper))

    def test_open_and_close_in_one_batch_also_stays_paused(self):
        for opening in (pygame.K_F1,pygame.K_t,pygame.K_b,pygame.K_l,pygame.K_i):
            with self.subTest(opening=opening):
                before=files(self.keeper)
                self.observe([[key(opening),key(pygame.K_ESCAPE),key(pygame.K_f)]])
                self.assertEqual(before,files(self.keeper))

    def test_close_resumes_next_frame_and_drops_queued_feed(self):
        before=CompanionSession.load(self.keeper/'companion.json')
        expected=copy.deepcopy(before);expected.advance(player_action=None,displayed_clip=None)
        self.observe([[key(pygame.K_t)],[key(pygame.K_ESCAPE),key(pygame.K_f)],[]])
        actual=CompanionSession.load(self.keeper/'companion.json')
        self.assertEqual(before.state['age_ticks']+1,actual.state['age_ticks'])
        self.assertEqual(expected.state,actual.state)

    def test_help_restores_hatch_page_and_selection(self):
        before=files(self.keeper)
        pages=self.observe([[key(pygame.K_h)],[key(pygame.K_PAGEDOWN)],[key(pygame.K_PAGEDOWN)],[key(pygame.K_F1)],[key(pygame.K_PAGEDOWN)],[key(pygame.K_ESCAPE)]])
        self.assertEqual(2,pages[2]['page']);self.assertEqual(0,pages[3]['page'])
        self.assertEqual(pages[2]['visible'],pages[5]['visible'])
        self.assertEqual(before,files(self.keeper))

    def test_picker_selection_survives_switch_and_close_reopen(self):
        before=files(self.keeper)
        pages=self.observe([[key(pygame.K_k)],[key(pygame.K_END)],[key(pygame.K_i)],[key(pygame.K_k)],[key(pygame.K_ESCAPE)],[key(pygame.K_k)]])
        for index in (1,3,5):self.assertIn('2/2  z.json',pages[index]['all'])
        self.assertEqual(before,files(self.keeper))

    def test_picker_reopen_refreshes_removed_selection(self):
        def remove_selected():
            (self.keeper/'packs/z.json').unlink()
            return [key(pygame.K_k)]
        pages=self.observe([[key(pygame.K_k)],[key(pygame.K_END)],[key(pygame.K_i)],remove_selected])
        self.assertIn('1/1  a.json',pages[3]['all'])

    def test_covenant_help_matches_live_controls_and_five_does_not_change_weather(self):
        pages=self.observe([[key(pygame.K_c)],[key(pygame.K_5)],[key(pygame.K_F1)]])
        joined=' '.join(pages[2]['all'])
        self.assertIn('1 palette',joined);self.assertIn('Care continues',joined)
        self.assertIn('5 has no action',joined)
        self.assertEqual('calm',json.loads((self.keeper/'era_plan.json').read_text(encoding='utf-8'))['weather'])

    def test_weather_still_works_after_covenant_closes(self):
        self.observe([[key(pygame.K_c)],[key(pygame.K_c)],[key(pygame.K_5)]])
        self.assertEqual('callback',json.loads((self.keeper/'era_plan.json').read_text(encoding='utf-8'))['weather'])

    def test_corrupt_campaign_is_readable_and_preserved(self):
        state=self.keeper/'campaign_state.json';state.write_text('{}',encoding='utf-8')
        pages=self.observe([[key(pygame.K_c)],[key(pygame.K_F1)],[key(pygame.K_ESCAPE)],[key(pygame.K_c)]])
        self.assertIn('Covenant unavailable',' '.join(pages[0]['all']))
        self.assertEqual('{}',state.read_text(encoding='utf-8'))

    def test_corrupt_campaign_export_and_adoption_do_not_crash_or_replace_it(self):
        state=self.keeper/'campaign_state.json';valid=state.read_bytes()
        state.write_text('{}',encoding='utf-8')
        pages=self.observe([[key(pygame.K_x)]])
        self.assertIn('Export not completed',' '.join(pages[-1]['all']))
        self.assertEqual('{}',state.read_text(encoding='utf-8'))
        self.assertFalse((self.keeper/'covenants/covenant_export.json').exists())
        # The archive correctly refuses an already corrupt state. Change it
        # after a valid archive opens to exercise adoption's loading boundary.
        state.write_bytes(valid)
        before=(self.keeper/'companion.json').read_bytes()
        def corrupt_then_adopt():
            state.write_text('{}',encoding='utf-8')
            return [key(pygame.K_a)]
        pages=self.observe([[key(pygame.K_b)],corrupt_then_adopt])
        self.assertIn('Adoption refused',' '.join(pages[-1]['all']))
        self.assertEqual('{}',state.read_text(encoding='utf-8'))
        self.assertEqual(before,(self.keeper/'companion.json').read_bytes())

    def test_older_reader_help_is_contextual(self):
        for opening,label in ((pygame.K_t,'REPORT HELP'),(pygame.K_b,'ARCHIVE HELP'),(pygame.K_v,'REPLAY HELP'),(pygame.K_l,'LINEAGE HELP')):
            with self.subTest(label=label):
                before=files(self.keeper)
                pages=self.observe([[key(opening)],[key(pygame.K_F1)]])
                self.assertIn(label,pages[1]['all'][0]);self.assertEqual(before,files(self.keeper))

    def test_archive_first_page_keeps_back_and_help_after_long_era_notice(self):
        original=_EraBench.__init__
        def initialize(bench,*args,**kwargs):
            original(bench,*args,**kwargs)
            bench.message='Previous era completed; admissions and rejections. '*12
        with patch.object(_EraBench,'__init__',initialize):
            pages=self.observe([[key(pygame.K_b)],[key(pygame.K_n)]])
        for page in pages[:2]:
            visible=' '.join(page['visible'])
            self.assertIn('B/Escape',visible);self.assertIn('F1 help',visible)
            self.assertNotIn('Previous era completed',visible)

    def test_lineage_exposes_every_recorded_ancestor_and_event_field(self):
        events=['first_event',{'kind':'later_event','payload':'important_'*20}]
        ancestors=[f'ancestor_{i}' for i in range(9)]
        record={'grid_id':'probe','lineage':{'generation':9,'ancestor_ids':ancestors,'mutation_events':events}}
        original=copy.deepcopy(record);joined=' '.join(LineageBrowser([record]).detail_lines())
        for value in (*ancestors,events[0],events[1]['kind'],events[1]['payload']):self.assertIn(value,joined)
        self.assertEqual(original,record)

if __name__=='__main__':unittest.main()
