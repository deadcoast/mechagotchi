"""S2 saves commit the pet first; UI failures retain progress for an explicit retry."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for relative in ("game/src", "packages/mecha_engine/src"):
    sys.path.insert(0, str(ROOT / relative))
import pygame
from mecha_game.app import run
from mecha_game.session import CompanionSession, load_session_inputs


def pet():
    grid, slip, model = load_session_inputs(ROOT / "data/seed_grids_16x16/mg_seed16_001_beetle.json",
                                           ROOT / "data/slips/valid/slip_v2_cleanliness.json")
    return CompanionSession(grid, slip, model=model, learning_policy="qtable")


def child(session):
    while session.alive:
        session.advance()
    session.succeed()


def key(value, ctrl=False):
    return pygame.event.Event(pygame.KEYDOWN, key=value, mod=pygame.KMOD_CTRL if ctrl else 0)


class CheckpointTests(unittest.TestCase):
    def test_primary_failure_leaves_export_at_last_committed_lineage(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "companion.json"
            lineage = path.with_name("lineage.json")
            session = pet()
            session.save_checkpoint(path)
            old_primary, old_export = path.read_bytes(), lineage.read_bytes()
            child(session)
            replace = os.replace
            def fail_primary(source, destination):
                if Path(destination) == path:
                    raise PermissionError("locked companion")
                return replace(source, destination)
            with patch("mecha_game.session.os.replace", side_effect=fail_primary):
                with self.assertRaises(OSError):
                    session.save_checkpoint(path)
            self.assertEqual(old_primary, path.read_bytes())
            self.assertEqual(old_export, lineage.read_bytes())
            self.assertEqual(2, len(session.lineage))

    def test_repeated_checkpoint_keeps_the_previous_save_recoverable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "companion.json"
            session = pet()
            session.save_checkpoint(path)
            previous = path.read_bytes()
            session.advance("feed")
            session.save_checkpoint(path)
            current = path.read_bytes()
            session.save_checkpoint(path)
            self.assertEqual(current, path.read_bytes())
            self.assertEqual(previous, path.with_suffix(".bak.json").read_bytes())

    def test_export_failure_commits_pet_and_reconciliation_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "companion.json"
            lineage = path.with_name("lineage.json")
            session = pet()
            session.save_checkpoint(path)
            previous = lineage.read_bytes()
            child(session)
            replace = os.replace
            def fail_export(source, destination):
                if Path(destination) == lineage:
                    raise PermissionError("locked export")
                return replace(source, destination)
            with patch("mecha_game.session.os.replace", side_effect=fail_export):
                warning = session.save_checkpoint(path)
            self.assertIn("lineage", warning.lower())
            loaded = CompanionSession.load(path)
            self.assertEqual(session.state, loaded.state)
            self.assertEqual(session.lineage, loaded.lineage)
            self.assertEqual(previous, lineage.read_bytes())
            self.assertTrue(loaded.sync_lineage_export(lineage))
            self.assertEqual(previous, lineage.with_suffix(".bak.json").read_bytes())
            before = {p.name:p.read_bytes() for p in Path(directory).iterdir()}
            self.assertFalse(loaded.sync_lineage_export(lineage))
            self.assertEqual(before, {p.name:p.read_bytes() for p in Path(directory).iterdir()})

    def test_backup_recovery_reconciles_earlier_lineage_and_learning(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "companion.json"
            lineage = path.with_name("lineage.json")
            session = pet()
            session.advance("feed")
            session.save_checkpoint(path)
            previous = path.read_bytes()
            child(session)
            session.save_checkpoint(path)
            later, later_export = path.read_bytes(), lineage.read_bytes()
            recovered, archive = CompanionSession.recover_backup(path)
            self.assertEqual(later, archive.read_bytes())
            self.assertEqual(previous, path.read_bytes())
            recovered.sync_lineage_export(lineage)
            self.assertEqual(json.loads(previous)["lineage"], json.loads(lineage.read_text())["records"])
            self.assertEqual(later_export, lineage.with_suffix(".bak.json").read_bytes())
            self.assertEqual(json.loads(previous)["state"], recovered.state)
            self.assertEqual("qtable", recovered.learning_policy)

    def run_events(self, directory, events, *, fail_count=0, frame_probe=None):
        frames, failures = 0, 0
        sequence = iter(events)
        replace = os.replace
        def next_events():
            nonlocal frames
            frames += 1
            if frames > 12:
                raise AssertionError("interactive save flow did not finish")
            if frame_probe:
                frame_probe(frames)
            return next(sequence, [pygame.event.Event(pygame.QUIT)])
        def replace_primary(source, destination):
            nonlocal failures
            if Path(destination).name == "companion.json" and failures < fail_count:
                failures += 1
                raise PermissionError("simulated locked companion")
            return replace(source, destination)
        with patch.dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy"), \
             patch("pygame.event.get", side_effect=next_events), \
             patch("mecha_game.session.os.replace", side_effect=replace_primary), \
             contextlib.redirect_stderr(io.StringIO()):
            code = run(["--keeper-dir", directory, "--tick-frames", "1", "--fps", "0", "--scale", "2"])
        return code, frames

    def test_failed_quit_pauses_care_and_retry_saves_that_exact_life(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "companion.json"
            session = pet()
            session.save(path)
            old = path.read_bytes()
            observations = []
            def probe(frame):
                if frame == 4:
                    observations.append(path.read_bytes() == old)
            code, frames = self.run_events(directory, [[], [pygame.event.Event(pygame.QUIT)],
                [key(pygame.K_f), key(pygame.K_s)], [key(pygame.K_s, ctrl=True)]], fail_count=1, frame_probe=probe)
            self.assertEqual(0, code)
            self.assertEqual(4, frames)
            self.assertEqual([True], observations)
            self.assertEqual(1, CompanionSession.load(path).state["age_ticks"])

    def test_explicit_discard_after_failed_quit_preserves_saved_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "companion.json"
            pet().save(path)
            old = path.read_bytes()
            code, frames = self.run_events(directory, [[], [pygame.event.Event(pygame.QUIT)],
                [key(pygame.K_f)], [key(pygame.K_q, ctrl=True)]], fail_count=99)
            self.assertEqual(1, code)
            self.assertEqual(4, frames)
            self.assertEqual(old, path.read_bytes())

    def test_manual_checkpoint_is_immediate_and_does_not_queue_sleep(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "companion.json"
            pet().save(path)
            observed = []
            def probe(frame):
                if frame == 3:
                    saved = CompanionSession.load(path)
                    observed.append(saved.state["age_ticks"])
            actions = []
            advance = CompanionSession.advance
            def track(session, *args, **kwargs):
                actions.append(kwargs.get("player_action"))
                return advance(session, *args, **kwargs)
            with patch.object(CompanionSession, "advance", track):
                code, _ = self.run_events(directory, [[], [key(pygame.K_s, ctrl=True)],
                    [pygame.event.Event(pygame.QUIT)]], frame_probe=probe)
            self.assertEqual(0, code)
            self.assertEqual([1], observed)
            self.assertEqual([None, None], actions)

    def test_bounded_primary_failure_returns_nonzero_without_export_ahead(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "companion.json"
            session = pet()
            session.save(path)
            session.save_lineage(path.with_name("lineage.json"))
            old = path.read_bytes()
            replace = os.replace
            def fail(source, destination):
                if Path(destination) == path:
                    raise PermissionError("locked companion")
                return replace(source, destination)
            with patch.dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy"), \
                 patch("mecha_game.session.os.replace", side_effect=fail), contextlib.redirect_stderr(io.StringIO()) as errors:
                code = run(["--keeper-dir", directory, "--ticks", "14", "--auto-succeed", "--tick-frames", "1", "--fps", "0"])
            self.assertEqual(1, code)
            self.assertNotIn("Traceback", errors.getvalue())
            self.assertEqual(old, path.read_bytes())
            self.assertEqual(json.loads(old)["lineage"], json.loads(path.with_name("lineage.json").read_text())["records"])

    def test_successor_is_checkpointed_before_next_frame(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "companion.json"
            session = pet()
            while session.alive:
                session.advance()
            session.save(path)
            observed = []
            def probe(frame):
                if frame == 2:
                    observed.append(len(CompanionSession.load(path).lineage))
            code, _ = self.run_events(directory, [[key(pygame.K_RETURN)],
                [pygame.event.Event(pygame.QUIT)]], frame_probe=probe)
            self.assertEqual(0, code)
            self.assertEqual([2], observed)
            self.assertEqual("qtable", CompanionSession.load(path).learning_policy)


if __name__ == "__main__":
    unittest.main()
