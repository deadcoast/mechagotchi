"""X8 preparation source/UI guards; synthetic facts never qualify earned play."""
import copy
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[2]
for folder in ('game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT/folder))
from mecha_game.app import _EraBench, build_parser
from mecha_game.campaign import KeeperCampaign
from mecha_game.covenant import STARTER_ORGAN_ROLES, starter_role_covenant
from mecha_game.preparation_readout import role_progress_lines, next_era_line, covenant_change_summary, preparation_notice


class EarnedPreparationReadoutTests(unittest.TestCase):
    def campaign(self):
        profile=json.loads((ROOT/'data/slips/valid/slip_v2_cleanliness.json').read_text())
        return KeeperCampaign({'slip_profile':starter_role_covenant(profile)}, campaign_id='guard')

    def test_role_readout_reports_unchanged_threshold_and_actual_earned_budget(self):
        campaign=self.campaign()
        lines=' '.join(role_progress_lines(campaign))
        self.assertIn('ornament',lines); self.assertIn('locked',lines); self.assertIn('16 niches',lines)
        campaign.campaign['unlocks']=[dict(axis='niche_mastery',tier=1)]
        lines=' '.join(role_progress_lines(campaign))
        self.assertIn('ready',lines); self.assertIn('ornament',lines)
        campaign.campaign['slip_profile']['grid']['allowed_organ_roles'].append('ornament')
        lines=' '.join(role_progress_lines(campaign))
        self.assertIn('effect',lines); self.assertIn('locked',lines); self.assertIn('26 niches',lines)

    def test_unrestricted_and_fully_spent_roles_are_distinct(self):
        campaign=self.campaign()
        campaign.base_profile['grid'].pop('allowed_organ_roles')
        campaign.campaign['slip_profile']['grid'].pop('allowed_organ_roles')
        self.assertIn('unrestricted',' '.join(role_progress_lines(campaign)))
        campaign=self.campaign()
        campaign.campaign['slip_profile']['grid']['allowed_organ_roles'] += ['ornament','effect']
        self.assertIn('All supported roles',' '.join(role_progress_lines(campaign)))

    def test_next_era_readout_keeps_prefix_and_shows_every_effective_choice(self):
        line=next_era_line('storm',2,population_policy='generation_survivors_v1',
            survival_regime='stress_probe',density=True)
        for text in ('NEXT ERA [storm]: 2 staged','living generations','stress probe','density on'):
            self.assertIn(text,line)
        self.assertIn('archive continuity',next_era_line('calm',0,population_policy='legacy_archive',
            survival_regime='sheltered',density=False))

    def test_spend_summary_names_actual_change_and_does_not_claim_earning(self):
        campaign=self.campaign();before=copy.deepcopy(campaign.state_payload())
        campaign.campaign['slip_profile']['grid']['allowed_organ_roles'].append('ornament')
        summary=covenant_change_summary(before,campaign.state_payload())
        self.assertIn('ornament',summary);self.assertIn('added',summary)
        self.assertNotIn('earned',summary)
        self.assertIn('unchanged',covenant_change_summary(before,before))

    def test_pending_notice_never_repeats_the_completed_spend_claim(self):
        pending=SimpleNamespace(error=None,pending={'summary':'Covenant saved: role ornament added.'})
        line=preparation_notice(pending)
        self.assertIn('awaiting finish',line);self.assertIn('ornament',line)
        self.assertNotIn('Covenant saved',line);self.assertIn('no era runs',line)

    def test_finish_parser_is_explicit_and_omitted_by_default(self):
        self.assertFalse(build_parser().parse_args([]).finish_preparation)
        self.assertTrue(build_parser().parse_args(['--finish-preparation']).finish_preparation)

    def test_preparation_policy_label_reads_saved_state_without_materializing_campaign(self):
        with tempfile.TemporaryDirectory() as directory:
            home=Path(directory);state=home/'campaign_state.json';ledger=home/'campaign.sqlite3'
            campaign=self.campaign();campaign.save(ledger);campaign.save_state(state)
            before=(state.read_bytes(),ledger.read_bytes())
            bench=_EraBench('session',state_path=state,ledger_path=ledger)
            with patch.object(bench,'ensure',side_effect=AssertionError('display loaded campaign')):
                self.assertIn('archive continuity',bench.preparation_line())
            self.assertIsNone(bench.campaign)
            self.assertEqual(before,(state.read_bytes(),ledger.read_bytes()))

    def test_pending_preparation_blocks_era_before_training_or_evaluation(self):
        with tempfile.TemporaryDirectory() as directory:
            home=Path(directory)
            bench=_EraBench('session',state_path=home/'campaign_state.json',ledger_path=home/'campaign.sqlite3')
            with patch.object(bench.preparation_commit,'require_ready',side_effect=ValueError('pending preparation')):
                with patch.object(bench,'ensure',side_effect=AssertionError('era work started')):
                    with self.assertRaisesRegex(ValueError,'pending preparation'):
                        bench.run_era(bench.ledger_path)


class EarnedPreparationApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from mecha_game.session import load_session_inputs
        from mecha_game.packets import default_fixture_paths
        cls.inputs=load_session_inputs(*default_fixture_paths())

    def setUp(self):
        from mecha_game.session import CompanionSession
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.home=Path(self.temp.name)
        grid,profile,model=self.inputs
        self.pet=CompanionSession(grid,profile,model=model,learning_policy='qtable')
        self.pet.save_checkpoint(self.home/'companion.json')
        self.env=patch.dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
        self.env.start();self.addCleanup(self.env.stop)
        self.draws=[]

    def key(self,code,*,up=False,repeat=False):
        import pygame
        return pygame.event.Event(pygame.KEYUP if up else pygame.KEYDOWN,key=code,mod=0,repeat=repeat)

    def invoke(self,batches,extra=()):
        import pygame
        from mecha_game.app import run
        from mecha_game.native_ui import ActionStrip
        original=ActionStrip.draw;rows=iter(batches)
        def draw(strip,surface,font,rect):
            result=original(strip,surface,font,rect)
            self.draws.append([(a.id,a.enabled) for a in strip.actions])
            return result
        def events():
            batch=next(rows,[pygame.event.Event(pygame.QUIT)])
            return batch() if callable(batch) else batch
        with patch('pygame.event.get',side_effect=events),patch.object(ActionStrip,'draw',draw):
            return run(['--keeper-dir',str(self.home),'--fps','0','--scale','2','--tick-frames','100000',*extra])

    def test_raw_held_and_repeat_events_spend_once_until_release(self):
        import pygame
        with patch.object(_EraBench,'spend') as spend:
            self.assertEqual(0,self.invoke([[self.key(pygame.K_c)],
                [self.key(pygame.K_5),self.key(pygame.K_5),self.key(pygame.K_5,repeat=True)],
                [self.key(pygame.K_5,up=True),self.key(pygame.K_5)]]))
        self.assertEqual([((4,),{}),((4,),{})],spend.call_args_list)

    def test_native_real_role_spend_names_change_and_preserves_learning(self):
        import pygame
        from mecha_game.session import CompanionSession
        original=KeeperCampaign.budget
        def budget(campaign):
            result=original(campaign)
            if result['allowed_organ_roles'] is not None:
                result['allowed_organ_roles']=[*STARTER_ORGAN_ROLES,'ornament','effect']
            return result
        original_spend=_EraBench.spend;states=[]
        def spend(bench,index):
            before=copy.deepcopy(bench.keeper_session.state)
            result=original_spend(bench,index)
            states.append((before,copy.deepcopy(bench.keeper_session.state)))
            return result
        # Synthetic permission tests the real controller/save path, never earned play.
        with patch.object(KeeperCampaign,'budget',budget),patch.object(_EraBench,'spend',spend):
            self.assertEqual(0,self.invoke([[self.key(pygame.K_c)],[self.key(pygame.K_9)],
                [self.key(pygame.K_5),self.key(pygame.K_5,repeat=True)]]))
        state=json.loads((self.home/'campaign_state.json').read_text())
        self.assertEqual([*STARTER_ORGAN_ROLES,'ornament'],state['slip_profile']['grid']['allowed_organ_roles'])
        loaded=CompanionSession.load(self.home/'companion.json')
        self.assertEqual(self.pet.learning_policy,loaded.learning_policy)
        self.assertEqual(1,len(states));self.assertEqual(states[0][0],states[0][1])
        self.assertEqual(states[0][1],loaded.state)
        self.assertEqual(0,state['era_count'])


    def import_fixture(self):
        bench=_EraBench('session',state_path=self.home/'campaign_state.json',ledger_path=self.home/'campaign.sqlite3',
            initial_profile=self.pet.slip_profile,keeper_session=self.pet)
        bench.choose_new_campaign('legacy_archive');bench.bind_current_campaign()
        self.pet.save_checkpoint(self.home/'companion.json')
        profile=json.loads((ROOT/'data/slips/valid/slip_lcd_seed.json').read_text())
        (self.home/'covenants').mkdir();(self.home/'covenants'/'chosen.json').write_text(json.dumps(profile))
        return bench,profile

    def test_import_retry_finishes_own_captured_target_once_without_reimport_or_pet_change(self):
        import pygame
        from mecha_game import app
        bench,profile=self.import_fixture();before=(self.home/'companion.json').read_bytes()
        original=os.replace;fail=[True];attempts=[]
        def replace(source,destination):
            if Path(destination)==bench.state_path:
                attempts.append(1)
                if fail[0]: raise PermissionError('injected state lock')
            return original(source,destination)
        def retry():
            self.assertEqual(1,len(attempts),'Same-frame duplicate Enter must not retry a captured save')
            fail[0]=False;return [self.key(pygame.K_RETURN)]
        with patch('mecha_game.session.os.replace',replace),patch.object(app,'import_covenant',wraps=app.import_covenant) as imported:
            self.assertEqual(0,self.invoke([[self.key(pygame.K_i)],
                [self.key(pygame.K_RETURN),self.key(pygame.K_RETURN)],retry]))
        self.assertEqual(1,imported.call_count)
        self.assertEqual(profile,json.loads(bench.state_path.read_text())['slip_profile'])
        self.assertFalse(bench.preparation_commit.path.exists())
        self.assertEqual(before,(self.home/'companion.json').read_bytes())

    def test_import_retry_refuses_changed_selection_or_preview_without_applying_either(self):
        import pygame
        from mecha_game import app
        for change in ('selection','preview'):
            with self.subTest(change=change),tempfile.TemporaryDirectory() as directory:
                self.home=Path(directory);self.pet.save_checkpoint(self.home/'companion.json')
                bench,profile=self.import_fixture();before=bench.state_path.read_bytes()
                if change == 'selection':
                    (self.home/'covenants'/'second.json').write_text(json.dumps(profile))
                original=os.replace;fail=[True];captured=[]
                def replace(source,destination):
                    if Path(destination)==bench.state_path and fail[0]:raise PermissionError('injected state lock')
                    return original(source,destination)
                def retry():
                    fail[0]=False;captured.append(bench.preparation_commit.path.read_bytes())
                    if change == 'preview':
                        (self.home/'covenants'/'chosen.json').write_text(json.dumps(profile,indent=4))
                        return [self.key(pygame.K_F5),self.key(pygame.K_RETURN)]
                    return [self.key(pygame.K_PERIOD),self.key(pygame.K_RETURN)]
                with patch('mecha_game.session.os.replace',replace),patch.object(app,'import_covenant',wraps=app.import_covenant) as imported:
                    self.assertEqual(0,self.invoke([[self.key(pygame.K_i)],[self.key(pygame.K_RETURN)],retry]))
                self.assertEqual(1,imported.call_count)
                self.assertEqual(before,bench.state_path.read_bytes())
                self.assertEqual(captured[0],bench.preparation_commit.path.read_bytes())

    def test_import_retry_refuses_a_replaced_journal_without_reimport(self):
        import pygame
        from mecha_game import app
        bench,_=self.import_fixture();state=bench.state_path.read_bytes();original=os.replace;fail=[True]
        changed=b'external replacement preparation journal'
        def replace(source,destination):
            if Path(destination)==bench.state_path and fail[0]: raise PermissionError('injected state lock')
            return original(source,destination)
        def retry():
            fail[0]=False;bench.preparation_commit.path.write_bytes(changed)
            return [self.key(pygame.K_RETURN)]
        with patch('mecha_game.session.os.replace',replace),patch.object(app,'import_covenant',wraps=app.import_covenant) as imported:
            self.assertEqual(0,self.invoke([[self.key(pygame.K_i)],[self.key(pygame.K_RETURN)],retry]))
        self.assertEqual(1,imported.call_count)
        self.assertEqual(state,bench.state_path.read_bytes())
        self.assertEqual(changed,bench.preparation_commit.path.read_bytes())

    def prepare_pending(self):
        bench=_EraBench('session',state_path=self.home/'campaign_state.json',ledger_path=self.home/'campaign.sqlite3',
            initial_profile=self.pet.slip_profile,keeper_session=self.pet)
        bench.choose_new_campaign('generation_survivors_v1',starter_roles=True)
        bench.bind_current_campaign();self.pet.save_checkpoint(self.home/'companion.json')
        current=bench.ensure();candidate=copy.deepcopy(current)
        candidate.campaign['slip_profile']['grid']['allowed_organ_roles'].append('ornament')
        bench.preparation_commit.begin(candidate,kind='covenant',source_campaign_id=current.campaign['campaign_id'],
            summary='Add role ornament',expected_state_digest=bench._loaded_state_digest,
            expected_ledger_digest=bench._loaded_ledger_digest)
        return bench,candidate

    def test_covenant_finish_is_visible_idempotent_and_never_starts_an_era(self):
        import pygame
        bench,candidate=self.prepare_pending()
        with patch.object(KeeperCampaign,'advance_era',side_effect=AssertionError('era started')), \
             patch.object(_EraBench,'spend',side_effect=AssertionError('spend repeated')):
            self.assertEqual(0,self.invoke([[],[self.key(pygame.K_e),self.key(pygame.K_e),
                self.key(pygame.K_e,repeat=True)],
                [self.key(pygame.K_e,up=True),self.key(pygame.K_e)]],['--view','preparation']))
        self.assertTrue(any(('finish_preparation',True) in row for row in self.draws))
        self.assertEqual(candidate.state_payload(),json.loads(bench.state_path.read_text()))
        self.assertFalse(bench.preparation_commit.path.exists())

    def test_main_era_refuses_pending_preparation_without_finishing_it(self):
        import pygame
        bench,candidate=self.prepare_pending();journal=bench.preparation_commit.path.read_bytes()
        before=bench.state_path.read_bytes()
        with patch.object(KeeperCampaign,'advance_era',side_effect=AssertionError('era started')):
            self.assertEqual(0,self.invoke([[self.key(pygame.K_e)],[]]))
        self.assertEqual(before,bench.state_path.read_bytes())
        self.assertEqual(journal,bench.preparation_commit.path.read_bytes())

    def test_cli_finishes_only_the_captured_target_and_repeated_finish_is_safe(self):
        from mecha_game.app import run
        bench,candidate=self.prepare_pending()
        with patch.object(KeeperCampaign,'advance_era',side_effect=AssertionError('era started')):
            for repeat in range(2):
                self.assertEqual(0,self.invoke([],['--finish-preparation']))
        self.assertEqual(candidate.state_payload(),json.loads(bench.state_path.read_text()))
        with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit) as raised:
            run(['--finish-preparation','--eras','1'])
        self.assertEqual(2,raised.exception.code)

    def test_incompatible_finish_flags_refuse_before_any_app_or_file_write(self):
        from mecha_game.app import run
        bench,_=self.prepare_pending()
        before={p.relative_to(self.home).as_posix():p.read_bytes() for p in self.home.rglob('*') if p.is_file()}
        cases=[['--eras','1'],['--create-successor'],['--new'],['--recover-backup'],
            ['--creator'],['--example','care-to-era'],['--reproduce-era','0'],
            ['--seed','unused.json'],['--slip','unused.json'],['--learning-policy','qtable'],
            ['--care-selection','off'],['--care-evaluator','pristine'],
            ['--population-policy','generation_survivors_v1'],['--campaign-seed','1'],['--starter-roles'],
            ['--prepare-weather','storm'],['--prepare-survival-regime','sheltered'],['--prepare-density-pressure','off']]
        for flags in cases:
            with self.subTest(flags=flags),contextlib.redirect_stderr(io.StringIO()), \
                 patch('mecha_game.app._run_selected',side_effect=AssertionError('app entered before rejection')):
                with self.assertRaises(SystemExit) as raised:
                    run(['--keeper-dir',str(self.home),'--finish-preparation',*flags])
                self.assertEqual(2,raised.exception.code)
        self.assertEqual(before,{p.relative_to(self.home).as_posix():p.read_bytes() for p in self.home.rglob('*') if p.is_file()})

    def test_pending_refusal_wording_never_claims_no_writes(self):
        bench,_=self.prepare_pending()
        notice=bench.preparation_failed(OSError('checkpoint locked'))
        self.assertIn('awaiting finish',notice)
        self.assertNotIn('not changed',notice)
        self.assertNotIn('unchanged',notice)

    def test_late_checkpoint_failure_keeps_target_and_native_restart_finishes_without_spend(self):
        import pygame
        from mecha_game import preparation_commit as persistence
        bench,candidate=self.prepare_pending();original=persistence._write_bytes_atomic
        def write(path,raw):
            if Path(path)==self.home/'campaign_recovery.json':
                raise OSError('injected late checkpoint failure')
            return original(path,raw)
        with patch.object(persistence,'_write_bytes_atomic',write):
            with self.assertRaisesRegex(OSError,'checkpoint'):
                bench.finish_preparation()
        self.assertEqual(candidate.state_payload(),json.loads(bench.state_path.read_text()))
        self.assertTrue(bench.preparation_commit.path.exists())
        self.assertIn('awaiting finish',bench.preparation_failed(OSError('late failure')))
        with patch.object(_EraBench,'spend',side_effect=AssertionError('spend reran')), \
             patch.object(KeeperCampaign,'advance_era',side_effect=AssertionError('era reran')):
            self.assertEqual(0,self.invoke([[],[self.key(pygame.K_e)]],['--view','preparation']))
        self.assertFalse(bench.preparation_commit.path.exists())
        self.assertEqual(candidate.state_payload(),json.loads(bench.state_path.read_text()))

    def test_native_checkpoint_recovery_archives_malformed_preparation_and_unblocks(self):
        import pygame
        bench,_=self.prepare_pending();before=bench.state_path.read_bytes()
        malformed=b'owner malformed preparation evidence'
        bench.preparation_commit.path.write_bytes(malformed)
        self.assertEqual(0,self.invoke([[],[self.key(pygame.K_u)],[],[self.key(pygame.K_u)]],
                                      ['--view','preparation']))
        self.assertEqual(before,bench.state_path.read_bytes())
        self.assertFalse(bench.preparation_commit.path.exists())
        archived=list((self.home/'.campaign-preparation'/'recovered').glob('*.json'))
        self.assertEqual([malformed],[path.read_bytes() for path in archived])
        restarted=_EraBench('session',state_path=bench.state_path,ledger_path=bench.ledger_path)
        restarted.require_preparation()

    def test_recovery_refuses_journal_changed_after_preview(self):
        bench,_=self.prepare_pending();bench.inspect_recovery()
        changed=b'external replacement journal';bench.preparation_commit.path.write_bytes(changed)
        before=(bench.state_path.read_bytes(),bench.ledger_path.read_bytes())
        with self.assertRaisesRegex(ValueError,'changed'):
            bench.restore_recovery()
        self.assertEqual(before,(bench.state_path.read_bytes(),bench.ledger_path.read_bytes()))
        self.assertEqual(changed,bench.preparation_commit.path.read_bytes())


if __name__ == '__main__': unittest.main()
