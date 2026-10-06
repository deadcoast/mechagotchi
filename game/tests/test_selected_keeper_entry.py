"""X3 source-event and preservation regressions; live saves are never fixtures."""
import copy
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for folder in ("game/src", "packages/mecha_engine/src"):
    sys.path.insert(0, str(ROOT / folder))
import pygame
from mecha_game.app import run
from mecha_game.session import CompanionSession
from mecha_game.contribute import gather_releases


def key(value):
    return pygame.event.Event(pygame.KEYDOWN, key=value, mod=0)


class SelectedKeeperEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.fixture.cleanup)
        cls.seed = Path(cls.fixture.name) / "seed"
        with patch.dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy"):
            assert run(["--keeper-dir", str(cls.seed), "--era-scale", "tiny",
                        "--eras", "1", "--ticks", "1", "--tick-frames", "1",
                        "--fps", "0", "--scale", "1"]) == 0

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.keeper = Path(self.temp.name) / "keeper"
        shutil.copytree(self.seed, self.keeper)

    def observe(self, batches, extra=()):
        sequence = iter(batches)
        def poll():
            return next(sequence, [pygame.event.Event(pygame.QUIT)])
        with patch.dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy"), \
                patch("pygame.event.get", side_effect=poll):
            self.assertEqual(0, run(["--keeper-dir", str(self.keeper), "--era-scale", "tiny",
                                    "--scale", "1", "--fps", "0", "--tick-frames", "1", *extra]))

    def test_explicit_new_preserves_backup_history_after_missing_or_invalid_primary(self):
        for state in ("missing", "invalid"):
            with self.subTest(state=state):
                path = self.keeper / "companion.json"
                session = CompanionSession.load(self.seed / "companion.json")
                session = session.adopt(session.grid, session.slip_profile, origin="new_companion")
                session.save(path.with_suffix(".bak.json"))
                backup_bytes = path.with_suffix(".bak.json").read_bytes()
                old_id = session.keeper_id
                old_lives = copy.deepcopy(session.lineage)
                if state == "missing":
                    path.unlink(missing_ok=True)
                else:
                    path.write_bytes(b"invalid primary to retain")
                self.observe([[key(pygame.K_F1)]], ("--new",))
                new = CompanionSession.load(path)
                self.assertEqual(old_id, new.keeper_id)
                self.assertEqual(len(old_lives) + 1, len(new.lineage))
                self.assertEqual(old_lives[0], new.lineage[0])
                self.assertEqual("unavailable", new.chronicle["prior_history"])
                self.assertTrue(any(p.read_bytes() == backup_bytes for p in self.keeper.glob("companion*.json")))
                if state == "invalid":
                    self.assertTrue(any(p.read_bytes() == b"invalid primary to retain" for p in self.keeper.glob("companion*.json")))
                # A subsequent changed checkpoint must not erase preserved bytes.
                new.advance(player_action="feed")
                new.save_checkpoint(path)
                self.assertTrue(any(p.read_bytes() == backup_bytes for p in self.keeper.glob("companion*.json")))

    def test_explicit_new_preserves_invalid_backup_and_marks_unknown_history(self):
        path = self.keeper / "companion.json"
        path.unlink()
        backup = path.with_suffix(".bak.json")
        raw = b"unreadable old backup"
        backup.write_bytes(raw)
        self.observe([[key(pygame.K_F1)]], ("--new",))
        new = CompanionSession.load(path)
        self.assertEqual("unavailable", new.chronicle["prior_history"])
        new.advance(player_action="feed")
        new.save_checkpoint(path)
        self.assertTrue(any(p.read_bytes() == raw for p in self.keeper.glob("companion*.json")))

    def test_direct_adoption_records_known_era_under_both_policies(self):
        for policy in ("incumbent", "qtable"):
            with self.subTest(policy=policy):
                self.keeper = Path(self.temp.name) / ("direct-" + policy)
                self.observe([[key(pygame.K_a)], [key(pygame.K_F1)]],
                             ("--eras", "1", "--ticks", "2", "--learning-policy", policy))
                state = json.loads((self.keeper / "campaign_state.json").read_text(encoding="utf-8"))
                current = CompanionSession.load(self.keeper / "companion.json")
                source = current.lineage[-1]["source"]
                self.assertEqual(state["campaign_id"], source["campaign_id"])
                self.assertEqual(0, source.get("era_index"))
                self.assertEqual(policy, current.learning_policy)

    def test_creator_entry_pauses_care_and_closes_owned_server_on_exit(self):
        before = CompanionSession.load(self.keeper / "companion.json").session_tick
        with patch("mecha_game.app.CreatorBridge") as bridge:
            bridge.return_value.open.return_value = "http://127.0.0.1:1234/"
            self.observe([[key(pygame.K_j)], [key(pygame.K_f), key(pygame.K_e)],
                          [key(pygame.K_j), key(pygame.K_f)]])
        after = CompanionSession.load(self.keeper / "companion.json")
        self.assertEqual(before, after.session_tick)
        bridge.assert_called_once_with(self.keeper)
        bridge.return_value.open.assert_called_once()
        bridge.return_value.close.assert_called_once()

    def test_creator_repeat_does_not_resume_care_or_open_extra_tabs(self):
        before = CompanionSession.load(self.keeper / "companion.json").session_tick
        repeated_j = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_j, mod=0, repeat=True)
        repeated_enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, repeat=True)
        with patch("mecha_game.app.CreatorBridge") as bridge:
            bridge.return_value.open.return_value = "http://127.0.0.1:1234/"
            self.observe([[key(pygame.K_j)], [repeated_j], [repeated_enter], [],
                          [key(pygame.K_F1)]])
        self.assertEqual(before, CompanionSession.load(self.keeper / "companion.json").session_tick)
        bridge.return_value.open.assert_called_once()
        bridge.return_value.close.assert_called_once()

    def test_selected_native_gather_excludes_shared_workshop_inbox(self):
        release = self.keeper / "released"
        release.mkdir(exist_ok=True)
        grid = CompanionSession.load(self.keeper / "companion.json").grid
        (release / "selected.json").write_text(json.dumps(grid), encoding="utf-8")
        (release / "selected.authoring.json").write_text(json.dumps({"document": {"grid": grid}}), encoding="utf-8")
        (release / "selected.layers.json").write_text(json.dumps({"layers": []}), encoding="utf-8")
        self.assertEqual([grid], gather_releases(self.keeper, start=ROOT, include_shared=False))


if __name__ == "__main__":
    unittest.main()
