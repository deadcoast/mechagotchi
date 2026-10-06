"""Compatibility refusal is operational; tiny fixtures are not outcome trials."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
for folder in ('game/src','packages/mecha_engine/src'): sys.path.insert(0,str(ROOT/folder))
from mecha_game.app import _EraBench
from mecha_game.campaign import KeeperCampaign,load_campaign_inputs,default_campaign_paths
from mecha_game.campaign_recovery import initialize_campaign_checkpoint,inspect_campaign_backup,recover_campaign_backup
from mecha_game.session import CompanionSession,load_session_inputs
from mecha_game.era_plan import EraPlan,state_digest
from mecha_game.preparation_commit import PreparationCommit

def files(root):
    return {p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob('*') if p.is_file()}

class BodyCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs=load_campaign_inputs(**default_campaign_paths(ROOT),seed_limit=4,repair_epochs=1)
        cls.pet_inputs=load_session_inputs(ROOT/'data/seed_grids_16x16/mg_seed16_001_beetle.json',ROOT/'data/slips/valid/slip_v2_cleanliness.json')
        cls.campaign=KeeperCampaign(copy.deepcopy(cls.inputs),campaign_id='compatibility',era_config=dict(generations=1,population=2,damage_cycles=1,ticks=3,dropout_rate=.2))
        cls.completed=copy.deepcopy(cls.campaign)
        cls.completed.advance_era('calm',record_original=True)

    def setup_pair(self,root):
        s=CompanionSession(*self.pet_inputs[:2],model=self.pet_inputs[2]);s.bind_campaign('compatibility');s.save(root/'companion.json')
        c=copy.deepcopy(self.campaign);state=root/'campaign_state.json';ledger=root/'campaign.sqlite3'
        initialize_campaign_checkpoint(c,state,ledger)
        return s,c,state,ledger

    def switch(self,root,s):
        changed=s.adopt(s.grid,s.slip_profile,body_response='workload-v1',origin='new_companion')
        changed.save(root/'companion.json');return changed

    def bench(self,state,ledger,s):
        return _EraBench('tiny',state_path=state,ledger_path=ledger,keeper_session=s)

    def preparation(self,state,ledger,c):
        candidate=copy.deepcopy(c);candidate.base_profile['name']='Captured import';candidate.base_covenant_source=None;candidate.campaign['slip_profile']=copy.deepcopy(candidate.base_profile)
        journal=PreparationCommit(state,ledger)
        journal.begin(candidate,kind='covenant',source_campaign_id='compatibility',expected_state_digest=state_digest(state),expected_ledger_digest=state_digest(ledger))
        return journal

    def refuses_unchanged(self,root,operation):
        before=files(root)
        for _ in range(2):
            with self.assertRaisesRegex(ValueError,'body response|companion.*changed|Keeper.*changed'):
                operation()
            self.assertEqual(before,files(root))

    def test_native_recovery_refuses_before_preservation_or_restore_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);s,c,state,ledger=self.setup_pair(root)
            b=self.bench(state,ledger,s);b.inspect_recovery()
            self.switch(root,s)
            self.refuses_unchanged(root,b.restore_recovery)

    def test_direct_recovery_refuses_on_restart_before_journal_reconciliation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);s,c,state,ledger=self.setup_pair(root);j=self.preparation(state,ledger,c)
            offer=inspect_campaign_backup(state,ledger);self.switch(root,s)
            self.refuses_unchanged(root,lambda:recover_campaign_backup(state,ledger,expected_manifest_digest=offer['manifest_digest'],expected_preparation_digest=j.journal_digest))

    def test_native_and_direct_captured_preparation_refuse_before_writes(self):
        for native in (True,False):
            with self.subTest(native=native),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);s,c,state,ledger=self.setup_pair(root);j=self.preparation(state,ledger,c)
                changed=self.switch(root,s);b=self.bench(state,ledger,changed)
                operation=b.finish_preparation if native else lambda:j.finish(expected_journal_digest=j.journal_digest)
                self.refuses_unchanged(root,operation)

    def test_pending_era_native_and_direct_finish_refuse(self):
        for native in (True,False):
            with self.subTest(native=native),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);s,c,state,ledger=self.setup_pair(root);plan=EraPlan(root/'era_plan.json')
                plan.begin(self.completed,self.completed.eras[-1],state_digest(state));changed=self.switch(root,s)
                b=self.bench(state,ledger,changed)
                self.refuses_unchanged(root,lambda:b.run_era(ledger) if native else EraPlan(plan.path).finish(ledger,state))

    def test_delayed_worker_refuses_before_creating_completed_journal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);s,c,state,ledger=self.setup_pair(root);b=self.bench(state,ledger,s)
            b._completed_work=copy.deepcopy(self.completed);b._completed_previous_state=state_digest(state)
            self.switch(root,s)
            self.refuses_unchanged(root,lambda:b.run_era(ledger))

    def test_preparation_choice_and_capture_refuse_for_stale_session(self):
        for action in ('weather','stage','begin'):
            with self.subTest(action=action),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);s,c,state,ledger=self.setup_pair(root);b=self.bench(state,ledger,s)
                self.switch(root,s)
                operation={'weather':lambda:b.choose_weather(1),'stage':lambda:b.stage_releases([s.grid]),'begin':lambda:self.preparation(state,ledger,c)}[action]
                self.refuses_unchanged(root,operation)

    def test_stale_care_checkpoint_cannot_revert_supported_new_life(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);s,c,state,ledger=self.setup_pair(root);stale=CompanionSession.load(root/'companion.json')
            changed=self.switch(root,s);stale.advance('feed')
            self.refuses_unchanged(root,lambda:stale.save_checkpoint(root/'companion.json'))
            self.assertEqual(changed.keeper_id,CompanionSession.load(root/'companion.json').keeper_id)

    def test_compatible_pending_era_and_preparation_finish_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);s,c,state,ledger=self.setup_pair(root);j=self.preparation(state,ledger,c)
            target=j.finish(expected_journal_digest=j.journal_digest);before=files(root)
            self.assertIsNone(j.finish(expected_journal_digest=None));self.assertEqual(before,files(root))
            self.assertEqual('Captured import',target['slip_profile']['name'])
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);s,c,state,ledger=self.setup_pair(root);plan=EraPlan(root/'era_plan.json');plan.begin(self.completed,self.completed.eras[-1],state_digest(state))
            plan.finish(ledger,state);before=files(root)
            with self.assertRaisesRegex(ValueError,'No completed era'):EraPlan(plan.path).finish(ledger,state)
            self.assertEqual(before,files(root))

    def test_parent_checkpoint_authorizes_adoption_once_not_stale_parent_or_sibling(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);s,c,state,ledger=self.setup_pair(root);path=root/'companion.json'
            s.advance('feed');first=s.adopt(s.grid,s.slip_profile);sibling=s.adopt(s.grid,s.slip_profile)
            s.save_checkpoint(path);first.save_checkpoint(path)
            self.assertEqual(first.lineage,CompanionSession.load(path).lineage)
            self.refuses_unchanged(root,lambda:s.save_checkpoint(path))
            self.refuses_unchanged(root,lambda:sibling.save_checkpoint(path))

    def test_interrupted_preparation_switch_refuses_then_compatible_retry_once(self):
        from mecha_game import session as session_api
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);s,c,state,ledger=self.setup_pair(root);j=self.preparation(state,ledger,c)
            original=session_api.os.replace
            def interrupt(source,destination):
                if Path(destination)==state:raise OSError('injected state interruption')
                return original(source,destination)
            with patch('mecha_game.session.os.replace',interrupt),self.assertRaises(OSError):
                j.finish(expected_journal_digest=j.journal_digest)
            changed=self.switch(root,s);restart=PreparationCommit(state,ledger)
            self.refuses_unchanged(root,lambda:restart.finish(expected_journal_digest=restart.journal_digest))
            restored=changed.adopt(changed.grid,changed.slip_profile,body_response='legacy');restored.save(root/'companion.json')
            target=restart.finish(expected_journal_digest=restart.journal_digest)
            before=files(root);self.assertIsNone(restart.finish(expected_journal_digest=None));self.assertEqual(before,files(root))
            self.assertEqual('Captured import',target['slip_profile']['name'])

    def test_inverse_model_recovery_inspects_but_refuses_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);s=CompanionSession(*self.pet_inputs[:2],model=self.pet_inputs[2],body_response='workload-v1')
            s.bind_campaign('compatibility');s.save(root/'companion.json')
            c=KeeperCampaign(copy.deepcopy(self.inputs),campaign_id='compatibility',body_response='workload-v1',era_config=self.campaign.era_config)
            state=root/'campaign_state.json';ledger=root/'campaign.sqlite3';initialize_campaign_checkpoint(c,state,ledger)
            changed=s.adopt(s.grid,s.slip_profile,body_response='legacy');changed.save(root/'companion.json')
            b=self.bench(state,ledger,changed);before=files(root);b.inspect_recovery();self.assertEqual(before,files(root))
            self.refuses_unchanged(root,b.restore_recovery)

    def test_stale_derived_lineage_export_preserves_current_life_and_backups(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);s,c,state,ledger=self.setup_pair(root);s.save_checkpoint(root/'companion.json')
            changed=self.switch(root,s);changed.save_checkpoint(root/'companion.json')
            self.refuses_unchanged(root,lambda:s.sync_lineage_export(root/'lineage.json'))
            self.assertEqual(2,len(json.loads((root/'lineage.json').read_bytes())['records']))

    def test_native_startup_stale_lineage_is_actionable_refusal(self):
        import contextlib,io,os
        from mecha_game.app import run
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);s,c,state,ledger=self.setup_pair(root);before=files(root)
            with (patch.dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'),
                  patch.object(CompanionSession,'sync_lineage_export',side_effect=ValueError('Keeper companion changed before lineage export; files preserved.')),
                  contextlib.redirect_stderr(io.StringIO()) as error,self.assertRaises(SystemExit) as exit):
                run(['--keeper-dir',str(root),'--ticks','1','--fps','0'])
            self.assertEqual(2,exit.exception.code);self.assertIn('Cannot resume companion',error.getvalue())
            self.assertEqual(before,files(root))

if __name__=='__main__':unittest.main()
