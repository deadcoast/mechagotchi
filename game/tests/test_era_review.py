"""T1: era reports are recorded truth, readable after restart, and pause care."""
import contextlib
import copy
import io
import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for relative in ("game/src", "packages/mecha_engine/src"):
    sys.path.insert(0, str(ROOT / relative))
import pygame
from mecha_engine.storage import campaign_history, open_ledger
from mecha_game.app import _EraBench, run
from mecha_game.campaign import KeeperCampaign, TINY_ERA_CONFIG, load_campaign_inputs
from mecha_game.era_review import EraReview
from mecha_game.footer import FooterPager, wrap_lines
from mecha_game.session import CompanionSession, load_session_inputs


def key(value, ctrl=False):
    return pygame.event.Event(pygame.KEYDOWN, key=value, mod=pygame.KMOD_CTRL if ctrl else 0)


class EraReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_campaign_inputs(ROOT / "data/seed_grids_16x16",
            ROOT / "data/slips/valid/slip_v2_cleanliness.json",
            ROOT / "data/readability_benchmark/adopted_readability_model.json", repair_epochs=6, seed_limit=12)
        cls.campaign = KeeperCampaign(cls.inputs, era_config=TINY_ERA_CONFIG, campaign_id="era_review_test")
        cls.campaign.advance_era("calm")
        cls.campaign.advance_era("storm")

    def seed_keeper(self, directory):
        keeper = Path(directory)
        self.campaign.save(keeper / "campaign.sqlite3")
        self.campaign.save_state(keeper / "campaign_state.json")
        grid, slip, model = load_session_inputs(ROOT / "data/seed_grids_16x16/mg_seed16_001_beetle.json",
                                               ROOT / "data/slips/valid/slip_v2_cleanliness.json")
        session = CompanionSession(grid, slip, model=model, learning_policy="qtable")
        session.save_checkpoint(keeper / "companion.json")
        return session

    def test_restart_history_matches_public_storage_and_does_not_write(self):
        with tempfile.TemporaryDirectory() as directory:
            self.seed_keeper(directory)
            keeper = Path(directory)
            before = {p.name:p.read_bytes() for p in keeper.iterdir()}
            view = EraReview.load(keeper)
            conn = open_ledger(keeper / "campaign.sqlite3")
            try:
                history = campaign_history(conn, "era_review_test")
            finally:
                conn.close()
            self.assertEqual(history, view.history)
            self.assertEqual(history["eras"][-1], view.current)
            self.assertEqual(1, view.index)
            self.assertEqual(before, {p.name:p.read_bytes() for p in keeper.iterdir()})
            resumed = KeeperCampaign.load_state(self.inputs, keeper / "campaign_state.json", keeper / "campaign.sqlite3")
            self.assertEqual([], resumed.eras)
            self.assertEqual(2, len(view.history["eras"]))
            self.assertEqual(2, resumed.era_offset)

    def test_lines_show_stored_metrics_weather_and_unlock_values(self):
        with tempfile.TemporaryDirectory() as directory:
            self.seed_keeper(directory)
            view = EraReview.load(Path(directory))
            before = copy.deepcopy(view.history)
            era = view.current
            lines = " ".join(view.lines())
            self.assertIn("storm", lines)
            self.assertIn(str(era["report"]["summary"]["archive"]["coverage"]), lines)
            self.assertIn(f"QD {era['report']['summary']['archive']['qd_score']}", lines)
            self.assertIn(str(era['report']['summary']['max_lineage_generation']), lines)
            for row in era['report']['cubff_pressure']['by_generation']:
                self.assertIn(row['snapshot_id'], lines)
                self.assertIn(str(row['dropout_multiplier']), lines)
            for fact in view.earned():
                self.assertIn(str(fact['metric_value']), lines)
                self.assertIn(str(fact['threshold']), lines)
            self.assertEqual(before, view.history)

    def test_inherited_facts_are_not_new_unlocks_for_same_numbered_era(self):
        current = {'campaign_id':'current','axis':'bloodline_depth','tier':1,
                   'earned_era_index':0,'metric_value':2,'threshold':2}
        inherited = dict(current, campaign_id='parent', axis='niche_mastery')
        view = EraReview({'campaign_id':'current','eras':[{'era_index':0}], 'unlocks':[inherited,current]})
        self.assertEqual([current], view.earned())

    def test_navigation_clamps_and_long_details_remain_reachable(self):
        with tempfile.TemporaryDirectory() as directory:
            self.seed_keeper(directory)
            view = EraReview.load(Path(directory))
            self.assertEqual(0, view.move(-99))
            self.assertEqual(1, view.move(99))
            for row in view.current['report']['cubff_pressure']['by_generation']:
                row['snapshot_id'] = 'long_snapshot_' * 40
            pygame.font.init()
            try:
                font = pygame.font.Font(None, 22)
                measure = lambda text:font.size(text)[0]
                expected = wrap_lines(view.lines(), measure, 368)
                pager, actual = FooterPager(), []
                first = pager.layout(view.lines(), measure, 368, 8)
                self.assertGreater(first.page_count, 1)
                for _ in range(first.page_count):
                    page = pager.layout(view.lines(), measure, 368, 8)
                    self.assertTrue(all(measure(line) <= 368 for line in page.lines))
                    actual.extend(page.lines[:-1])
                    pager.move(1)
                self.assertEqual(expected, actual)
            finally:
                pygame.quit()

    def test_empty_history_creates_nothing_and_names_the_next_player_action(self):
        with tempfile.TemporaryDirectory() as directory:
            view = EraReview.load(Path(directory))
            self.assertIsNone(view.current)
            self.assertIn("E run", " ".join(view.lines()))
            self.assertIn("paused", " ".join(view.lines()).lower())
            self.assertEqual([], list(Path(directory).iterdir()))

    def test_corrupt_or_unknown_schema_is_refused_without_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper = Path(directory)
            state = keeper / 'campaign_state.json'
            state.write_text('broken', encoding='utf-8')
            with self.assertRaises(ValueError):
                EraReview.load(keeper)
            self.assertEqual('broken', state.read_text())
            state.write_text(json.dumps({'state_format':KeeperCampaign.STATE_FORMAT,'campaign_id':'x'}))
            ledger = keeper / 'campaign.sqlite3'
            conn = sqlite3.connect(ledger)
            conn.execute('PRAGMA user_version=999');conn.close()
            before = ledger.read_bytes()
            with self.assertRaisesRegex(ValueError, 'schema'):
                EraReview.load(keeper)
            self.assertEqual(before, ledger.read_bytes())

    def test_malformed_report_blob_is_unavailable_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            self.seed_keeper(directory)
            keeper = Path(directory)
            ledger = keeper / 'campaign.sqlite3'
            conn = sqlite3.connect(ledger)
            conn.execute("UPDATE eras SET report_json = ? WHERE era_index = 0",
                         (json.dumps({'summary':'malformed saved summary'}),))
            conn.commit()
            conn.close()
            before = {p.name:p.read_bytes() for p in keeper.iterdir()}
            with self.assertRaisesRegex(ValueError, 'invalid era report'):
                EraReview.load(keeper)
            self.assertEqual(before, {p.name:p.read_bytes() for p in keeper.iterdir()})

    def run_events(self, directory, rows, **patches):
        sequence = iter(rows)
        frames = 0
        def events():
            nonlocal frames
            frames += 1
            if frames > 15: raise AssertionError('era-review flow did not exit')
            return next(sequence, [pygame.event.Event(pygame.QUIT)])
        with patch.dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy'), \
             patch('pygame.event.get', side_effect=events):
            return run(['--keeper-dir',directory,'--tick-frames','1','--fps','0','--scale','2'])

    def test_real_review_help_and_close_preserve_care_time_and_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            self.seed_keeper(directory)
            keeper = Path(directory)
            ledger = (keeper/'campaign.sqlite3').read_bytes()
            advances = []
            original = CompanionSession.advance
            def advance(session, *args, **kwargs):
                advances.append(kwargs.get('player_action'))
                return original(session,*args,**kwargs)
            with patch.object(_EraBench,'ensure',side_effect=AssertionError('review must not train/run a campaign')), \
                 patch.object(CompanionSession,'advance',advance):
                code = self.run_events(directory, [[key(pygame.K_t)],[key(pygame.K_f),key(pygame.K_s),key(pygame.K_g)],
                    [key(pygame.K_LEFTBRACKET)],[key(pygame.K_F1)],[key(pygame.K_PAGEDOWN)],
                    [key(pygame.K_ESCAPE)],[key(pygame.K_t)],[],[pygame.event.Event(pygame.QUIT)]])
            self.assertEqual(0,code)
            self.assertEqual([None],advances)
            resumed=CompanionSession.load(keeper/'companion.json')
            self.assertEqual(1,resumed.state['age_ticks'])
            self.assertEqual('qtable',resumed.learning_policy)
            self.assertEqual(ledger,(keeper/'campaign.sqlite3').read_bytes())

    def test_quit_inside_review_does_not_touch_companion_or_campaign_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            self.seed_keeper(directory)
            keeper=Path(directory)
            before={p.name:p.read_bytes() for p in keeper.iterdir()}
            self.assertEqual(0,self.run_events(directory,[[key(pygame.K_t)],[pygame.event.Event(pygame.QUIT)]]))
            self.assertEqual(before,{p.name:p.read_bytes() for p in keeper.iterdir()})

    def test_save_failure_in_review_keeps_s2_discard_available(self):
        with tempfile.TemporaryDirectory() as directory:
            self.seed_keeper(directory)
            keeper=Path(directory)
            old=(keeper/'companion.json').read_bytes()
            (keeper/'companion.bak.json').mkdir()
            with contextlib.redirect_stderr(io.StringIO()) as errors:
                code=self.run_events(directory,[[],[key(pygame.K_t)],[key(pygame.K_s,True)],[key(pygame.K_q,True)]])
            self.assertEqual(1,code)
            self.assertIn('Save failed. Care paused.',errors.getvalue())
            self.assertEqual(old,(keeper/'companion.json').read_bytes())

    def test_interactive_era_completion_opens_review_before_care_advances(self):
        with tempfile.TemporaryDirectory() as directory:
            grid,slip,model=load_session_inputs(ROOT/'data/seed_grids_16x16/mg_seed16_001_beetle.json',
                                               ROOT/'data/slips/valid/slip_v2_cleanliness.json')
            CompanionSession(grid,slip,model=model).save_checkpoint(Path(directory)/'companion.json')
            with patch('mecha_game.app.load_campaign_inputs',return_value=self.inputs):
                code=self.run_events(directory,[[key(pygame.K_e)],[pygame.event.Event(pygame.QUIT)]])
            self.assertEqual(0,code)
            self.assertEqual(0,CompanionSession.load(Path(directory)/'companion.json').state['age_ticks'])
            self.assertIsNotNone(EraReview.load(Path(directory)).current)


if __name__=='__main__':unittest.main()
