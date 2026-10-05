"""W1: connected paused inboxes and preservation of existing file-bridge data."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for folder in ('game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT / folder))
import pygame
from mecha_game.app import run
from mecha_game.campaign import KeeperCampaign, TINY_ERA_CONFIG, load_campaign_inputs
from mecha_game.covenant_io import import_covenant
from mecha_game.footer import FooterPager
from mecha_game.packs import build_pack, import_pack, write_pack
from mecha_game.session import CompanionSession, load_session_inputs


def key(value):
    return pygame.event.Event(pygame.KEYDOWN, key=value, mod=0)


def files(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*')
            if p.is_file() and 'model_cache' not in p.parts}


class ImportInboxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_campaign_inputs(ROOT/'data/seed_grids_16x16', ROOT/'data/slips/valid/slip_v2_cleanliness.json',
            ROOT/'data/readability_benchmark/adopted_readability_model.json', repair_epochs=6, seed_limit=12)
        cls.campaign = KeeperCampaign(cls.inputs, era_config=TINY_ERA_CONFIG, campaign_id='inbox_test')
        cls.pet = load_session_inputs(ROOT/'data/seed_grids_16x16/mg_seed16_001_beetle.json', ROOT/'data/slips/valid/slip_v2_cleanliness.json')
        cls.profile = json.loads((ROOT/'data/slips/valid/slip_lcd_seed.json').read_text(encoding='utf-8'))
        cls.pack = build_pack(pack_id='inbox', title='Keeper choices', provenance={'source':'test'},
            slips=[cls.profile], creatures=[cls.inputs['seed_grids'][0]])

    def seed(self, keeper, policy='incumbent'):
        self.campaign.save(keeper/'campaign.sqlite3')
        self.campaign.save_state(keeper/'campaign_state.json')
        grid, slip, model = self.pet
        CompanionSession(grid, slip, model=model, learning_policy=policy).save_checkpoint(keeper/'companion.json')

    def observe(self, keeper, batches, *, no_training=False):
        events=iter(batches); pages=[]; original=FooterPager.layout
        def capture(pager, lines, measure, width, rows):
            result=original(pager,lines,measure,width,rows)
            pages.append({'all':list(lines),'visible':list(result.lines)})
            return result
        def poll():
            batch=next(events,[pygame.event.Event(pygame.QUIT)])
            return batch() if callable(batch) else batch
        def inputs(*args, **kwargs):
            if no_training: raise AssertionError('browsing must not load campaign models')
            return self.inputs
        with patch.dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'), \
             patch('pygame.event.get',side_effect=poll), \
             patch.object(FooterPager,'layout',capture),patch('mecha_game.app.load_campaign_inputs',side_effect=inputs):
            code=run(['--keeper-dir',str(keeper),'--era-scale','tiny','--scale','1','--fps','0','--tick-frames','1'])
        self.assertEqual(0,code)
        return pages

    def test_picker_reads_sorted_named_files_without_writes_and_refreshes(self):
        from mecha_game.inbox import InboxPicker
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory); inbox=keeper/'covenants';inbox.mkdir()
            for name in ['z.json','a.json','a.bak.json']:
                (inbox/name).write_text(json.dumps(self.profile),encoding='utf-8')
            before=files(keeper); picker=InboxPicker(keeper,'covenant')
            self.assertEqual(['a.json','z.json'],[p.name for p in picker.files])
            self.assertEqual('a.json',picker.selected.name)
            picker.move(1);picker.refresh();self.assertEqual('z.json',picker.selected.name)
            self.assertIn(self.profile['profile_id'],' '.join(picker.lines()))
            self.assertEqual(before,files(keeper))
            (inbox/'z.json').unlink();picker.refresh();self.assertEqual('a.json',picker.selected.name)

    def test_empty_invalid_and_long_names_remain_browsable(self):
        from mecha_game.inbox import InboxPicker
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);picker=InboxPicker(keeper,'pack')
            self.assertIn('No JSON files',' '.join(picker.lines()));self.assertEqual({},files(keeper))
            (keeper/'packs').mkdir();name='long_'*30+'.json';(keeper/'packs'/name).write_bytes(b'\xff')
            picker.refresh();self.assertIn('unreadable',' '.join(picker.lines()).lower())
            self.assertIn(name,' '.join(picker.lines()));self.assertIn(str(keeper/'packs'),' '.join(picker.lines()))

    def test_open_help_select_cancel_is_read_only_on_both_policies(self):
        for policy in ('incumbent','qtable'):
            with self.subTest(policy=policy),tempfile.TemporaryDirectory() as directory:
                keeper=Path(directory);self.seed(keeper,policy)
                write_pack(self.pack,keeper/'packs'/'named.json');before=files(keeper)
                pages=self.observe(keeper,[[key(pygame.K_k)],[key(pygame.K_f),key(pygame.K_e)],
                    [key(pygame.K_F1)],[key(pygame.K_ESCAPE)],[key(pygame.K_ESCAPE)],
                    [key(pygame.K_i)],[key(pygame.K_ESCAPE)]],no_training=True)
                self.assertIn('PACK INBOX',' '.join(pages[0]['visible']))
                self.assertIn('named.json',' '.join(pages[3]['all']))
                self.assertEqual(before,files(keeper))

    def test_pack_then_named_covenant_import_persists_without_changing_pet(self):
        for policy in ('incumbent','qtable'):
            with self.subTest(policy=policy),tempfile.TemporaryDirectory() as directory:
                keeper=Path(directory);self.seed(keeper,policy)
                write_pack(self.pack,keeper/'packs'/'named.json');pet=(keeper/'companion.json').read_bytes()
                pages=self.observe(keeper,[[key(pygame.K_k)],[key(pygame.K_RETURN)],
                    [key(pygame.K_i)],[key(pygame.K_RETURN)]])
                self.assertIn('pack_inbox_', ' '.join(pages[2]['all']))
                self.assertIn('Covenant imported', ' '.join(pages[3]['all']))
                restored=KeeperCampaign.load_state(self.inputs,keeper/'campaign_state.json',keeper/'campaign.sqlite3')
                self.assertEqual(self.profile,restored.base_profile)
                self.assertEqual(pet,(keeper/'companion.json').read_bytes())
                self.assertEqual(policy,CompanionSession.load(keeper/'companion.json').learning_policy)

    def test_refused_covenant_preserves_files_and_displays_engine_reason(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper);(keeper/'covenants').mkdir()
            invalid=copy.deepcopy(self.profile);invalid['grid']['body_mass_min']=200;invalid['grid']['body_mass_max']=256
            (keeper/'covenants'/'impossible.json').write_text(json.dumps(invalid),encoding='utf-8');before=files(keeper)
            pages=self.observe(keeper,[[key(pygame.K_i)],[key(pygame.K_RETURN)]])
            self.assertIn('no seed grid satisfies',' '.join(pages[-1]['all']))
            self.assertEqual(before,files(keeper))

    def test_changed_selection_requires_refresh_before_import(self):
        from mecha_game.inbox import InboxPicker
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper);(keeper/'covenants').mkdir();p=keeper/'covenants'/'a.json'
            p.write_text(json.dumps(self.profile),encoding='utf-8');picker=InboxPicker(keeper,'covenant')
            changed=copy.deepcopy(self.profile);changed['profile_id']='changed';p.write_text(json.dumps(changed),encoding='utf-8')
            campaign=copy.deepcopy(self.campaign);before=copy.deepcopy(campaign.base_profile)
            result=import_covenant(campaign,p,expected_digest=picker.digest)
            self.assertFalse(result['ok']);self.assertIn('changed',' '.join(result['violations']))
            self.assertEqual(before,campaign.base_profile)
            picker.refresh();self.assertTrue(import_covenant(campaign,p,expected_digest=picker.digest)['ok'])

    def test_malformed_covenants_refuse_without_crashing(self):
        for raw in (b'[]',b'null',b'"text"',b'\xff'):
            with self.subTest(raw=raw),tempfile.TemporaryDirectory() as directory:
                p=Path(directory)/'bad.json';p.write_bytes(raw)
                self.assertFalse(import_covenant(copy.deepcopy(self.campaign),p)['ok'])

    def test_malformed_packs_refuse_without_crashing_or_writes(self):
        for value in ([],None,{'pack_format':'mechagotchi_pack_v1'},
                      dict(self.pack,slips='oops'),dict(self.pack,slips=[None],creatures=[[]])):
            with self.subTest(value=value),tempfile.TemporaryDirectory() as directory:
                keeper=Path(directory);p=keeper/'bad.json';p.write_text(json.dumps(value),encoding='utf-8');before=files(keeper)
                result=import_pack(keeper,p)
                self.assertFalse(result['ok'] and any(e['ok'] for e in result.get('slips',[])))
                self.assertEqual(before,files(keeper))

    def test_pack_conflicts_preserve_bytes_and_identical_repeats_are_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);p=write_pack(self.pack,keeper/'pack.json');first=import_pack(keeper,p)
            before=files(keeper);again=import_pack(keeper,p)
            self.assertTrue(again['slips'][0]['already_staged']);self.assertEqual(before,files(keeper))
            staged=keeper/'covenants'/first['slips'][0]['staged'];staged.write_bytes(b'owner edit')
            before=files(keeper);conflict=import_pack(keeper,p)
            self.assertFalse(conflict['slips'][0]['ok']);self.assertIn('exists',' '.join(conflict['slips'][0]['violations']))
            self.assertEqual(before,files(keeper))

    def test_pack_ids_cannot_escape_inbox(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory)/'keeper';keeper.mkdir();outside=Path(directory)/'owner.json';outside.write_bytes(b'owner')
            p=write_pack(dict(self.pack,pack_id='../escape'),keeper/'pack.json');before=files(Path(directory))
            result=import_pack(keeper,p);self.assertFalse(result['ok']);self.assertEqual(before,files(Path(directory)))

    def test_bad_item_keeps_full_verdict_and_other_items_can_stage(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);pack=copy.deepcopy(self.pack);bad=copy.deepcopy(self.profile);bad['slip_version']='9.9.9';pack['slips'].append(bad)
            p=write_pack(pack,keeper/'pack.json');result=import_pack(keeper,p)
            self.assertTrue(result['slips'][0]['ok']);self.assertFalse(result['slips'][1]['ok'])
            self.assertIn('slip_version',' '.join(result['slips'][1]['violations']))
            self.assertTrue(result['creatures'][0]['ok'])

    def test_source_stale_selection_can_refresh_and_apply_the_new_preview(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper);(keeper/'covenants').mkdir();p=keeper/'covenants'/'chosen.json'
            p.write_text(json.dumps(self.profile),encoding='utf-8');before=(keeper/'campaign_state.json').read_bytes()
            changed=copy.deepcopy(self.profile);changed['profile_id']='refreshed_choice'
            def replace_file():
                p.write_text(json.dumps(changed),encoding='utf-8')
                return [key(pygame.K_RETURN)]
            def refresh():
                self.assertEqual(before,(keeper/'campaign_state.json').read_bytes())
                return [key(pygame.K_F5)]
            pages=self.observe(keeper,[[key(pygame.K_i)],replace_file,refresh,[key(pygame.K_RETURN)]])
            self.assertIn('changed since preview',' '.join(pages[1]['all']))
            self.assertIn('refreshed_choice',' '.join(pages[2]['all']))
            self.assertIn('Covenant imported',' '.join(pages[3]['all']))

    def test_source_keeps_selection_and_refusal_details_through_help_and_paging(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper);(keeper/'covenants').mkdir()
            (keeper/'covenants'/'a.json').write_text(json.dumps(self.profile),encoding='utf-8')
            name='chosen_'*22+'.json';(keeper/'covenants'/name).write_text('{}',encoding='utf-8')
            pages=self.observe(keeper,[[key(pygame.K_i)],[key(pygame.K_END)],[key(pygame.K_F1)],
                [key(pygame.K_ESCAPE)],[key(pygame.K_RETURN)],[key(pygame.K_PAGEDOWN)],
                [key(pygame.K_PAGEDOWN)],[key(pygame.K_HOME)]])
            self.assertEqual(pages[1]['all'],pages[3]['all'])
            self.assertIn('authority rejects',' '.join(pages[5]['visible']+pages[6]['visible']))
            self.assertIn('a.json',' '.join(pages[7]['visible']))

    def test_pack_partial_io_failure_retries_without_rewriting_successes(self):
        from mecha_game import packs
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);p=write_pack(self.pack,keeper/'pack.json');original=packs._stage_item
            def deny_covenant(path,value):
                if path.parent.name=='covenants': raise PermissionError('observed staging lock')
                return original(path,value)
            with patch.object(packs,'_stage_item',side_effect=deny_covenant):
                first=import_pack(keeper,p)
            self.assertFalse(first['slips'][0]['ok']);self.assertTrue(first['creatures'][0]['ok'])
            saved={p:p.read_bytes() for p in (keeper/'released').glob('*.json')}
            again=import_pack(keeper,p)
            self.assertTrue(again['slips'][0]['ok']);self.assertTrue(again['creatures'][0]['already_staged'])
            self.assertTrue(all(p.read_bytes()==raw for p,raw in saved.items()))

    def test_covenant_state_write_failure_is_visible_and_retries_without_changing_pet(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper);(keeper/'covenants').mkdir()
            (keeper/'covenants'/'chosen.json').write_text(json.dumps(self.profile),encoding='utf-8')
            state=(keeper/'campaign_state.json').read_bytes();pet=(keeper/'companion.json').read_bytes()
            original=os.replace;fail=[True]
            def locked(source,destination):
                if Path(destination)==keeper/'campaign_state.json' and fail[0]:raise PermissionError('observed state lock')
                return original(source,destination)
            def retry():
                self.assertEqual(state,(keeper/'campaign_state.json').read_bytes());fail[0]=False
                return [key(pygame.K_RETURN)]
            with patch('mecha_game.session.os.replace',side_effect=locked):
                pages=self.observe(keeper,[[key(pygame.K_i)],[key(pygame.K_RETURN)],retry])
            self.assertIn('Import not completed',' '.join(pages[1]['visible']))
            self.assertIn('Covenant imported',' '.join(pages[2]['visible']))
            self.assertEqual(pet,(keeper/'companion.json').read_bytes())

    def test_duplicate_enter_applies_once_and_return_resumes_care_next_frame(self):
        from mecha_game.app import _EraBench
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper);(keeper/'covenants').mkdir()
            (keeper/'covenants'/'chosen.json').write_text(json.dumps(self.profile),encoding='utf-8')
            age=CompanionSession.load(keeper/'companion.json').state['age_ticks'];calls=[];original=_EraBench.change_covenant
            def counted(bench,operation):
                calls.append(1);return original(bench,operation)
            with patch.object(_EraBench,'change_covenant',counted):
                self.observe(keeper,[[key(pygame.K_i)],[key(pygame.K_RETURN),key(pygame.K_RETURN)],
                    [key(pygame.K_RETURN)],[key(pygame.K_ESCAPE),key(pygame.K_f)],[]])
            pet=CompanionSession.load(keeper/'companion.json')
            self.assertEqual(1,len(calls));self.assertEqual(age+1,pet.state['age_ticks'])
            self.assertEqual(0,pet.state['action_counts'].get('feed',0))

    def test_legacy_formatted_staged_items_are_recognized_without_rewriting(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);p=write_pack(self.pack,keeper/'pack.json');first=import_pack(keeper,p)
            target=keeper/'covenants'/first['slips'][0]['staged']
            target.write_text(json.dumps(self.profile,indent=4),encoding='utf-8');before=target.read_bytes()
            again=import_pack(keeper,p)
            self.assertTrue(again['slips'][0]['ok']);self.assertTrue(again['slips'][0]['already_staged'])
            self.assertEqual(before,target.read_bytes())

    def test_malformed_nested_covenant_refuses_without_changing_campaign(self):
        for field,value in [('slip_version',[]),('grid',{'allowed_palettes':[[]]}),('mutation',[]),('mechanics',None)]:
            with self.subTest(field=field),tempfile.TemporaryDirectory() as directory:
                profile=copy.deepcopy(self.profile);profile[field]=value
                p=Path(directory)/'bad.json';p.write_text(json.dumps(profile),encoding='utf-8')
                campaign=copy.deepcopy(self.campaign);before=copy.deepcopy(campaign.campaign)
                result=import_covenant(campaign,p)
                self.assertFalse(result['ok']);self.assertTrue(result['violations']);self.assertEqual(before,campaign.campaign)

    def test_first_page_explains_disabled_import_before_a_long_filename(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper);(keeper/'covenants').mkdir()
            (keeper/'covenants'/('unreadable_'*17+'.json')).write_bytes(b'\xff')
            before=files(keeper)
            pages=self.observe(keeper,[[key(pygame.K_i)],[key(pygame.K_F1)],[key(pygame.K_ESCAPE)],
                [key(pygame.K_RETURN)]],no_training=True)
            self.assertIn('File unreadable',' '.join(pages[0]['visible']))
            self.assertNotIn('Enter imports',' '.join(pages[0]['visible']))
            self.assertIn('F5 refresh',' '.join(pages[1]['visible']))
            self.assertNotIn('F feed',' '.join(pages[1]['visible']))
            self.assertEqual(before,files(keeper))

    def test_completed_import_no_longer_offers_the_disabled_enter_action(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper=Path(directory);self.seed(keeper);write_pack(self.pack,keeper/'packs'/'named.json')
            pages=self.observe(keeper,[[key(pygame.K_k)],[key(pygame.K_RETURN)]])
            self.assertIn('import complete',' '.join(pages[1]['visible']))
            self.assertNotIn('Enter imports',' '.join(pages[1]['visible']))


if __name__ == '__main__':
    unittest.main()
