"""T4: preparation reaches one durable era, then review/adoption/replay."""
import copy
import importlib
import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[2]
for folder in ('game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT / folder))
import pygame
from mecha_game.app import _EraBench, run
from mecha_game.campaign import KeeperCampaign, TINY_ERA_CONFIG, load_campaign_inputs
from mecha_game.era_review import EraReview
from mecha_game.footer import FooterPager
from mecha_game.session import CompanionSession, load_session_inputs


def key(value):
    return pygame.event.Event(pygame.KEYDOWN, key=value, mod=0)


def files(path):
    return {p.relative_to(path).as_posix():p.read_bytes() for p in path.rglob('*') if p.is_file()}


class EraPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_campaign_inputs(ROOT/'data/seed_grids_16x16', ROOT/'data/slips/valid/slip_v2_cleanliness.json',
            ROOT/'data/readability_benchmark/adopted_readability_model.json', repair_epochs=6, seed_limit=12)
        cls.campaign = KeeperCampaign(cls.inputs, era_config=TINY_ERA_CONFIG, campaign_id='era_plan_test')
        cls.campaign.advance_era('calm')
        cls.pet = load_session_inputs(ROOT/'data/seed_grids_16x16/mg_seed16_001_beetle.json', ROOT/'data/slips/valid/slip_v2_cleanliness.json')
        cls.release = copy.deepcopy(cls.inputs['seed_grids'][1]); cls.release['grid_id'] = 'keeper_contribution'

    def seed(self, keeper, policy='qtable'):
        self.campaign.save(keeper/'campaign.sqlite3')
        self.campaign.save_state(keeper/'campaign_state.json')
        grid,slip,model = self.pet
        CompanionSession(grid,slip,model=model,learning_policy=policy).save_checkpoint(keeper/'companion.json')

    def bench(self, keeper, *, live=True):
        b = _EraBench('tiny', cache_dir=keeper/'model_cache', state_path=keeper/'campaign_state.json', ledger_path=keeper/'campaign.sqlite3')
        if live: b.campaign = copy.deepcopy(self.campaign)
        return b

    def plan(self, keeper):
        return importlib.import_module('mecha_game.era_plan').EraPlan(keeper/'era_plan.json')

    def events(self, keeper, rows, *, visible=None):
        pages=[]; sequence=iter(rows); original=FooterPager.layout
        batch=-1
        def poll():
            nonlocal batch
            batch+=1
            return next(sequence,[pygame.event.Event(pygame.QUIT)])
        def capture(pager,lines,measure,width,height):
            # Retain the final casing after each scripted event batch. T5 also
            # renders intermediate progress within the same E operation.
            if len(pages)<=batch:pages.append(list(lines))
            else:pages[batch]=list(lines)
            page=original(pager,lines,measure,width,height)
            if visible is not None:
                if len(visible)<=batch:visible.append(list(page.lines))
                else:visible[batch]=list(page.lines)
            return page
        with patch.dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'), \
             patch('pygame.event.get',side_effect=poll),patch.object(FooterPager,'layout',capture):
            code=run(['--keeper-dir',str(keeper),'--era-scale','tiny','--scale','1','--fps','0','--tick-frames','1'])
        self.assertEqual(0,code)
        return pages

    def test_preparation_round_trip_order_dedup_conflict_and_lazy_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);plan=self.plan(keeper)
            self.assertEqual({},files(keeper))
            second=copy.deepcopy(self.release);second['grid_id']='second'
            plan.stage([self.release,second,self.release]);plan.select_weather('storm')
            self.assertEqual([self.release,second],self.plan(keeper).releases)
            self.assertEqual('storm',self.plan(keeper).weather)
            before=files(keeper);plan.stage([second,self.release]);self.assertEqual(before,files(keeper))
            changed=copy.deepcopy(self.release);changed['grid_size']=[0,0]
            with self.assertRaises(ValueError):plan.stage([changed])
            with self.assertRaises(ValueError):plan.stage([None])
            self.assertEqual(before,files(keeper))

    def test_unstage_preserves_source_creature_and_cannot_discard_pending_result(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper);b=self.bench(keeper)
            b.plan.stage([self.release]);before=(keeper/'companion.json').read_bytes()
            b.plan.unstage_all();self.assertEqual([],b.plan.releases)
            self.assertEqual(before,(keeper/'companion.json').read_bytes())
            b.plan.stage([self.release])
            with patch.object(KeeperCampaign,'save',side_effect=PermissionError('ledger locked')):
                with self.assertRaises(OSError):b.run_era(keeper/'campaign.sqlite3')
            before=files(keeper)
            with self.assertRaises(ValueError):b.plan.unstage_all()
            self.assertEqual(before,files(keeper))

    def test_malformed_genome_is_refused_with_authority_errors_before_staging(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);plan=self.plan(keeper)
            with self.assertRaises(ValueError):plan.stage([{'grid_id':'incomplete'}])
            self.assertEqual([],plan.releases);self.assertEqual({},files(keeper))

    def test_staging_atomic_failure_keeps_prior_plan_and_memory(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);plan=self.plan(keeper);plan.stage([self.release]);before=files(keeper)
            with patch('mecha_game.session.os.replace',side_effect=PermissionError('plan locked')):
                with self.assertRaises(OSError):plan.select_weather('storm')
            self.assertEqual('calm',plan.weather);self.assertEqual(before,files(keeper))

    def test_covenant_spend_survives_restart_and_failed_save_does_not_apply(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper);b=self.bench(keeper)
            b.spend(2)
            stored=json.loads((keeper/'campaign_state.json').read_text())
            self.assertEqual(b.campaign.era_config['population'],stored['era_config']['population'])
            self.assertGreater(stored['era_config']['population'],TINY_ERA_CONFIG['population'])
            resumed=KeeperCampaign.load_state(self.inputs,keeper/'campaign_state.json',keeper/'campaign.sqlite3')
            self.assertEqual(b.campaign.base_parameters,resumed.base_parameters)
            self.assertEqual(b.campaign.budget(),resumed.budget())
            before=(keeper/'campaign_state.json').read_bytes();config=copy.deepcopy(b.campaign.era_config)
            original=os.replace
            def fail(source,destination):
                if Path(destination)==keeper/'campaign_state.json':raise PermissionError('state locked')
                return original(source,destination)
            with patch('mecha_game.session.os.replace',fail):
                with self.assertRaises(OSError):b.spend(3)
            self.assertEqual(config,b.campaign.era_config);self.assertEqual(before,(keeper/'campaign_state.json').read_bytes())

    def test_simulation_failure_keeps_preparation_and_campaign(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper);b=self.bench(keeper)
            b.plan.stage([self.release]);b.choose_weather(2);before=files(keeper)
            with patch.object(KeeperCampaign,'advance_era',side_effect=ValueError('weather unavailable')):
                with self.assertRaises(ValueError):b.run_era(keeper/'campaign.sqlite3')
            self.assertEqual(before,files(keeper));self.assertEqual(self.campaign.eras,b.campaign.eras)

    def test_each_persistence_fault_retries_without_repeating_evolution(self):
        for fault in ('journal','ledger','state','clear'):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory() as directory:
                keeper=Path(directory);self.seed(keeper);b=self.bench(keeper)
                b.plan.stage([self.release]);b.choose_weather(2)
                evolve=KeeperCampaign.advance_era;calls=[];original=os.replace
                def advance(campaign,*args,**kwargs):
                    calls.append(1);return evolve(campaign,*args,**kwargs)
                def replace(source,destination):
                    destination=Path(destination)
                    if fault=='state' and destination==keeper/'campaign_state.json':raise PermissionError('state locked')
                    if destination==keeper/'era_plan.json':
                        payload=json.loads(Path(source).read_text())
                        if (fault=='journal' and payload['pending'] is not None) or (fault=='clear' and payload['pending'] is None):
                            raise PermissionError('plan locked')
                    return original(source,destination)
                with patch.object(KeeperCampaign,'advance_era',advance):
                    if fault=='ledger':
                        with patch.object(KeeperCampaign,'save',side_effect=PermissionError('ledger locked')):
                            with self.assertRaises(OSError):b.run_era(keeper/'campaign.sqlite3')
                    else:
                        with patch('mecha_game.session.os.replace',replace):
                            with self.assertRaises(OSError):b.run_era(keeper/'campaign.sqlite3')
                    if fault!='journal':b=self.bench(keeper,live=False)
                    result=b.run_era(keeper/'campaign.sqlite3')
                self.assertEqual([1],calls)
                self.assertEqual(1,result['era_index']);self.assertEqual('storm',result['weather']['forecast'])
                self.assertEqual([],self.plan(keeper).releases);self.assertIsNone(self.plan(keeper).pending)
                history=EraReview.load(keeper).history
                self.assertEqual([0,1],[e['era_index'] for e in history['eras']])
                self.assertEqual(2,json.loads((keeper/'campaign_state.json').read_text())['era_count'])
                self.assertEqual(self.campaign.eras[0]['report'],history['eras'][0]['report'])

    def test_completed_result_matches_unbroken_engine_and_next_seed(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper);b=self.bench(keeper)
            b.plan.stage([self.release]);b.choose_weather(2)
            expected=copy.deepcopy(self.campaign)
            first=expected.advance_era('storm',released_grids=[self.release])
            self.assertEqual(first,b.run_era(keeper/'campaign.sqlite3'))
            b=self.bench(keeper,live=False)
            second=expected.advance_era('storm')
            actual=b.run_era(keeper/'campaign.sqlite3')
            self.assertEqual(second,actual)

    def test_corrupt_plan_and_external_state_conflict_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper);b=self.bench(keeper)
            b.plan.stage([self.release])
            with patch.object(KeeperCampaign,'save',side_effect=PermissionError('ledger locked')):
                with self.assertRaises(OSError):b.run_era(keeper/'campaign.sqlite3')
            state=json.loads((keeper/'campaign_state.json').read_text());state['keeper_label']='external edit'
            (keeper/'campaign_state.json').write_text(json.dumps(state),encoding='utf-8');before=files(keeper)
            with self.assertRaises(ValueError):self.bench(keeper,live=False).run_era(keeper/'campaign.sqlite3')
            self.assertEqual(before,files(keeper))
            (keeper/'era_plan.json').write_text('broken',encoding='utf-8');before=files(keeper)
            pages=self.events(keeper,[[key(pygame.K_t)],[key(pygame.K_e)],[key(pygame.K_r)],[pygame.event.Event(pygame.QUIT)]])
            self.assertIn('preparation unavailable',' '.join(pages[1]).lower())
            self.assertEqual(before,files(keeper))

    def test_journal_tamper_and_ledger_conflict_do_not_overwrite_evidence(self):
        from contextlib import closing
        for fault in ('journal','ledger'):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory() as directory:
                keeper=Path(directory);self.seed(keeper);b=self.bench(keeper)
                b.plan.stage([self.release])
                original=os.replace
                def fail(source,destination):
                    if Path(destination)==keeper/'campaign_state.json':raise PermissionError('state locked')
                    return original(source,destination)
                with patch('mecha_game.session.os.replace',fail):
                    with self.assertRaises(OSError):b.run_era(keeper/'campaign.sqlite3')
                if fault=='journal':
                    path=keeper/'era_plan.json';payload=json.loads(path.read_text())
                    payload['pending']['state']['keeper_label']='tampered'
                    path.write_text(json.dumps(payload),encoding='utf-8')
                else:
                    with closing(sqlite3.connect(keeper/'campaign.sqlite3')) as conn,conn:
                        conn.execute("UPDATE eras SET rng_seed=rng_seed+1 WHERE era_index=1")
                before=files(keeper)
                with patch.object(KeeperCampaign,'advance_era',side_effect=AssertionError('must not resimulate')):
                    with self.assertRaises(ValueError):self.bench(keeper,live=False).run_era(keeper/'campaign.sqlite3')
                self.assertEqual(before,files(keeper))

    def test_imported_covenant_persists_without_changing_the_pet_and_legacy_state_loads(self):
        from mecha_game.covenant_io import import_covenant
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper);b=self.bench(keeper)
            before=(keeper/'companion.json').read_bytes()
            imported=b.change_covenant(lambda c:import_covenant(c,ROOT/'data/slips/valid/slip_lcd_seed.json'))
            self.assertTrue(imported['ok'])
            restored=KeeperCampaign.load_state(self.inputs,keeper/'campaign_state.json',keeper/'campaign.sqlite3')
            self.assertEqual(imported['covenant'],restored.campaign['slip_profile'])
            self.assertEqual(imported['covenant'],restored.base_profile)
            self.assertEqual(before,(keeper/'companion.json').read_bytes())
            state=json.loads((keeper/'campaign_state.json').read_text());state.pop('base_parameters')
            (keeper/'campaign_state.json').write_text(json.dumps(state),encoding='utf-8')
            before=(keeper/'campaign_state.json').read_bytes()
            old=KeeperCampaign.load_state(self.inputs,keeper/'campaign_state.json',keeper/'campaign.sqlite3')
            self.assertEqual(state['era_config']['population'],old.base_parameters['population'])
            self.assertEqual(before,(keeper/'campaign_state.json').read_bytes())

    def test_existing_outcome_metrics_stay_on_first_report_page(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper);visible=[]
            self.events(keeper,[[key(pygame.K_t)],[pygame.event.Event(pygame.QUIT)]],visible=visible)
            page=' '.join(visible[0])
            self.assertIn('bloodline continued',page)
            self.assertIn('Niches',page)
            self.assertIn('QD',page)

    def test_pending_completion_does_not_advertise_disabled_preparation_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper)
            with patch.object(KeeperCampaign,'save',side_effect=PermissionError('ledger locked')):
                pages=self.events(keeper,[[key(pygame.K_t)],[key(pygame.K_e)],[pygame.event.Event(pygame.QUIT)]])
            self.assertIn('E retry',' '.join(pages[1]))
            self.assertNotIn('1-5 weather',' '.join(pages[1]))

    def test_report_preparation_pauses_care_and_restart_uses_it(self):
        for policy in ('incumbent','qtable'):
            with self.subTest(policy=policy),tempfile.TemporaryDirectory() as directory:
                keeper=Path(directory);self.seed(keeper,policy)
                pet_before=(keeper/'companion.json').read_bytes()
                pages=self.events(keeper,[[key(pygame.K_t)],[key(pygame.K_r)],[key(pygame.K_r)],
                    [key(pygame.K_3)],[pygame.event.Event(pygame.QUIT)]])
                self.assertIn('NEXT ERA [storm]: 1 staged',' '.join(pages[3]))
                self.assertEqual(pet_before,(keeper/'companion.json').read_bytes())
                pages=self.events(keeper,[[key(pygame.K_t)],[key(pygame.K_e)],[key(pygame.K_b)],
                    [key(pygame.K_t)],[key(pygame.K_v)],[key(pygame.K_v)],[key(pygame.K_b)],
                    [key(pygame.K_a)],[pygame.event.Event(pygame.QUIT)]])
                era=EraReview.load(keeper).current
                self.assertEqual('storm',era['weather']['forecast'])
                admitted=era['report']['founders']['admitted_ids']
                self.assertIn(self.pet[0]['grid_id'],admitted)
                self.assertIn('ADMITTED: '+self.pet[0]['grid_id'],' '.join(pages[1]))
                self.assertTrue(pages[4][0].startswith('REVIEW ERA 1'))
                self.assertEqual(policy,CompanionSession.load(keeper/'companion.json').learning_policy)
                self.assertEqual([],self.plan(keeper).releases)


if __name__=='__main__':unittest.main()
