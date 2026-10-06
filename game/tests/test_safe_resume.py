"""S1: malformed models fail before play; recovery preserves every companion."""
import dataclasses
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
for relative in ("game/src","packages/mecha_engine/src"):
    sys.path.insert(0,str(ROOT/relative))
from mecha_engine.generation import GenerationModel, generate_candidate
from mecha_game.session import CompanionSession, load_session_inputs
from mecha_game.app import _footer_lines, build_parser, default_keeper_dir, run


def pet(policy="incumbent"):
    grid,slip,model=load_session_inputs(ROOT/"data/seed_grids_16x16/mg_seed16_001_beetle.json",ROOT/"data/slips/valid/slip_v2_cleanliness.json")
    return CompanionSession(grid,slip,model=model,learning_policy=policy)


class SafeResumeTests(unittest.TestCase):
    def test_loaded_model_validation_precedes_any_save_change(self):
        mutations=(lambda p:p.pop("generation_model"),
                   lambda p:p["generation_model"].update(width=0),
                   lambda p:p["generation_model"].update(width="16"),
                   lambda p:p["generation_model"].update(width=8),
                   lambda p:p["generation_model"].update(adjacency=[]),
                   lambda p:p["generation_model"]["token_counts"].update(B=-1),
                   lambda p:p["generation_model"]["token_counts"].update(B="bad"),
                   lambda p:p["generation_model"]["token_counts"].update(unknown=3),
                   lambda p:p["generation_model"]["metadata"].update(strategy="unsupported"),
                   lambda p:p["generation_model"].update(total_pairs=1))
        for index,mutate in enumerate(mutations):
            with self.subTest(index=index),tempfile.TemporaryDirectory() as directory:
                path=Path(directory)/"companion.json"
                pet("qtable").save(path)
                document=json.loads(path.read_text())
                mutate(document)
                path.write_text(json.dumps(document))
                backup=path.with_suffix(".bak.json")
                backup.write_bytes(b"preserve previous backup")
                before=(path.read_bytes(),backup.read_bytes())
                with self.assertRaises(ValueError): CompanionSession.load(path)
                self.assertEqual(before,(path.read_bytes(),backup.read_bytes()))

    def test_bad_save_roots_and_required_types_are_clear_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"companion.json"
            pet().save(path)
            good=json.loads(path.read_text())
            for payload in ([],None,{},dict(good,fleet="off"),dict(good,log={}),dict(good,state=None)):
                path.write_text(json.dumps(payload))
                before=path.read_bytes()
                with self.assertRaises(ValueError): CompanionSession.load(path)
                self.assertEqual(before,path.read_bytes())

    def test_engine_refuses_malformed_model_and_wrong_parent_size(self):
        session=pet()
        fields=dataclasses.asdict(session.model)
        fields["width"]=0
        with self.assertRaises(ValueError): GenerationModel(**fields)
        fields=dataclasses.asdict(session.model)
        fields["width"]=8
        # Structurally valid model metadata still must match its target grid.
        with self.assertRaisesRegex(ValueError,"model"):
            generate_candidate(session.grid,GenerationModel(**fields),session.slip_profile,1)

    def test_explicit_backup_recovery_retains_primary_and_learning(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"companion.json"
            session=pet("qtable")
            session.advance("feed")
            session.save(path)
            previous=path.read_bytes()
            session.advance("sleep")
            session.save(path)
            primary=path.read_bytes()
            restored,archive=CompanionSession.recover_backup(path)
            self.assertEqual(primary,archive.read_bytes())
            self.assertEqual(previous,path.read_bytes())
            self.assertEqual(previous,path.with_suffix(".bak.json").read_bytes())
            self.assertEqual("qtable",restored.learning_policy)
            self.assertEqual(1,restored.state["age_ticks"])
            self.assertEqual(json.loads(previous)["state"],restored.state)
            restored.advance("sleep")
            self.assertEqual(session.state,restored.state)

    def test_bad_or_conflicting_backup_is_refused_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"companion.json"
            session=pet("qtable")
            session.save(path);session.advance();session.save(path)
            def inventory(): return {p.name:p.read_bytes() for p in Path(directory).iterdir() if p.is_file()}
            before=inventory()
            with self.assertRaises(ValueError): CompanionSession.recover_backup(path,learning_policy="incumbent")
            self.assertEqual(before,inventory())
            path.with_suffix(".bak.json").write_text("broken")
            before=inventory()
            with self.assertRaises(ValueError): CompanionSession.recover_backup(path)
            self.assertEqual(before,inventory())

    def test_save_and_recovery_write_failures_preserve_primary(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"companion.json"
            session=pet();session.save(path);session.advance();session.save(path)
            before=path.read_bytes();backup=path.with_suffix(".bak.json").read_bytes()
            with patch("mecha_game.session.os.replace",side_effect=OSError("simulated write failure")):
                with self.assertRaises(OSError): session.save(path)
                self.assertEqual(before,path.read_bytes())
                self.assertEqual(backup,path.with_suffix(".bak.json").read_bytes())
                with self.assertRaises(OSError): CompanionSession.recover_backup(path)
                self.assertEqual(before,path.read_bytes())
                self.assertEqual(backup,path.with_suffix(".bak.json").read_bytes())
            self.assertFalse(list(Path(directory).glob("*.tmp")))

    def test_primary_replace_failure_keeps_previous_primary_readable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "companion.json"
            session = pet("qtable")
            session.save(path)
            session.advance("feed")
            session.save(path)
            previous = path.read_bytes()
            session.advance("sleep")
            real_replace = os.replace
            def fail_primary(source, destination):
                if Path(destination) == path:
                    raise OSError("simulated primary replace failure")
                return real_replace(source, destination)
            with patch("mecha_game.session.os.replace", side_effect=fail_primary):
                with self.assertRaises(OSError):
                    session.save(path)
            self.assertEqual(previous, path.read_bytes())
            self.assertEqual(previous, path.with_suffix(".bak.json").read_bytes())
            self.assertEqual(1, CompanionSession.load(path).state["age_ticks"])
            self.assertFalse(list(Path(directory).glob("*.tmp")))

    def test_frozen_save_discovery_keeps_backup_only_homes_reachable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home, bundle = root / "user", root / "bundle"
            legacy = bundle / "keeper"
            legacy.mkdir(parents=True)
            (legacy / "companion.bak.json").write_text("retained")
            with patch("sys.frozen", True, create=True), patch("sys._MEIPASS", str(bundle), create=True), patch("pathlib.Path.home", return_value=home):
                self.assertEqual(legacy, default_keeper_dir())
                (home / ".mechagotchi").mkdir(parents=True)
                (home / ".mechagotchi/companion.bak.json").write_text("retained home")
                self.assertEqual(home / ".mechagotchi", default_keeper_dir())

    def test_missing_primary_requires_explicit_recovery_or_new_life(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"companion.json"
            session=pet("qtable");session.save(path);session.advance();session.save(path)
            path.unlink()
            before=path.with_suffix(".bak.json").read_bytes()
            with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit) as error:
                run(["--keeper-dir",directory,"--ticks","1"])
            self.assertEqual(2,error.exception.code)
            self.assertFalse(path.exists())
            self.assertEqual(before,path.with_suffix(".bak.json").read_bytes())
            recovered,archive=CompanionSession.recover_backup(path)
            self.assertIsNone(archive)
            self.assertEqual("qtable",recovered.learning_policy)
            self.assertEqual(before,path.read_bytes())

    def test_policy_is_visible_for_both_modes_and_recovery_is_explicit(self):
        self.assertIn("incumbent"," ".join(_footer_lines(pet().snapshot(),None)))
        self.assertIn("q-table"," ".join(_footer_lines(pet("qtable").snapshot(),None)).lower())
        for policy, label in (("incumbent", "incumbent"), ("qtable", "q-table")):
            snapshot = pet(policy).snapshot()
            snapshot.update(alive=False, death_cause="starvation")
            self.assertIn(label, " ".join(_footer_lines(snapshot, None)).lower())
        self.assertTrue(build_parser().parse_args(["--recover-backup"]).recover_backup)
        self.assertFalse(build_parser().parse_args([]).recover_backup)


if __name__=="__main__": unittest.main()
