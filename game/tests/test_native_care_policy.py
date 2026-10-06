"""X7 explicit native care-selection entry and saved-policy safety."""
import contextlib
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
for folder in ('game/src','packages/mecha_engine/src'):
    sys.path.insert(0,str(ROOT/folder))
from mecha_game.app import _footer_lines, build_parser, run
from mecha_game.session import CompanionSession, load_session_inputs
from mecha_game.packets import default_fixture_paths

POLICY='observed_care_selection_v1'


class NativeCarePolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs=load_session_inputs(*default_fixture_paths())

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='mecha-x7-policy-')
        self.addCleanup(self.temp.cleanup)
        self.home=Path(self.temp.name)
        self.env=patch.dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
        self.env.start();self.addCleanup(self.env.stop)

    def start(self,*flags):
        return run(['--keeper-dir',str(self.home),'--ticks','1','--tick-frames','1','--fps','0',*flags])

    def test_new_choice_is_explicit_and_restart_keeps_it(self):
        self.assertIsNone(build_parser().parse_args([]).care_selection)
        self.assertEqual(0,self.start('--new','--care-selection',POLICY,'--care-evaluator','pristine'))
        first=CompanionSession.load(self.home/'companion.json')
        self.assertEqual(POLICY,first.care_selection_policy)
        self.assertEqual('pristine',first.care_evaluator)
        self.assertIn('experimental',' '.join(_footer_lines(first.snapshot(),None)).lower())
        self.assertEqual(0,self.start())
        resumed=CompanionSession.load(self.home/'companion.json')
        self.assertEqual(POLICY,resumed.care_selection_policy)
        self.assertEqual('pristine',resumed.care_evaluator)

    def test_conflicting_resume_preserves_primary_and_backup_bytes(self):
        self.assertEqual(0,self.start('--new','--care-selection',POLICY))
        before={p.name:p.read_bytes() for p in self.home.glob('companion*.json')}
        with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit) as raised:
            self.start('--care-selection','off')
        self.assertEqual(2,raised.exception.code)
        self.assertEqual(before,{p.name:p.read_bytes() for p in self.home.glob('companion*.json')})

    def test_explicit_new_can_disable_without_losing_prior_life(self):
        self.assertEqual(0,self.start('--new','--care-selection',POLICY))
        first=CompanionSession.load(self.home/'companion.json')
        self.assertEqual(0,self.start('--new','--care-selection','off'))
        second=CompanionSession.load(self.home/'companion.json')
        self.assertEqual('off',second.care_selection_policy)
        self.assertEqual(first.keeper_id,second.keeper_id)
        self.assertEqual(first.lineage[-1]['life_id'],second.lineage[0]['life_id'])
        self.assertEqual(2,len(second.lineage))

    def test_conflicting_backup_restore_does_not_replace_either_save(self):
        grid,profile,model=self.inputs
        session=CompanionSession(grid,profile,model=model,care_selection_policy=POLICY)
        session.save_checkpoint(self.home/'companion.json')
        session.advance('feed')
        session.save_checkpoint(self.home/'companion.json')
        before={p.name:p.read_bytes() for p in self.home.glob('companion*.json')}
        with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):
            self.start('--recover-backup','--care-selection','off')
        self.assertEqual(before,{p.name:p.read_bytes() for p in self.home.glob('companion*.json')})


if __name__=='__main__':
    unittest.main()
