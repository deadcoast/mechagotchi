"""Hermetic artifact-verifier boundaries; actual EXE proof is a separate run."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

class DetachedReleaseTests(unittest.TestCase):
    def test_environment_removes_source_python_settings(self):
        from verify_detached_release import isolated_environment
        with tempfile.TemporaryDirectory() as folder:
            with patch.dict(os.environ,{'PYTHONPATH':'source','PYTHONHOME':'source',
                    'PYTHONSTARTUP':'source','PYTHONUSERBASE':'source'}):
                env=isolated_environment(Path(folder))
            for key in ('PYTHONPATH','PYTHONHOME','PYTHONSTARTUP','PYTHONUSERBASE'):
                self.assertNotIn(key,env)
            self.assertEqual('1',env['PYTHONNOUSERSITE'])
            self.assertEqual(str(Path(folder)),env['USERPROFILE'])

    def test_relocation_refuses_existing_destination_and_repo_ancestry(self):
        from verify_detached_release import relocate_bundle
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); repo=root/'repo'; repo.mkdir()
            source=repo/'dist';source.mkdir();(source/'Mechagotchi.exe').write_bytes(b'fixture')
            with self.assertRaises(ValueError):relocate_bundle(source,repo/'copy',repo)
            existing=root/'existing';existing.mkdir();(existing/'owner').write_bytes(b'keep')
            with self.assertRaises(ValueError):relocate_bundle(source,existing,repo)
            self.assertEqual(b'keep',(existing/'owner').read_bytes())
            destination=root/'detached'
            relocate_bundle(source,destination,repo)
            self.assertEqual(b'fixture',(destination/'Mechagotchi.exe').read_bytes())

    def test_artifact_manifest_binds_all_files_and_refuses_tampering(self):
        from verify_detached_release import validate_artifact_manifest
        import hashlib,json
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'Mechagotchi.exe').write_bytes(b'executable')
            manifest={'format':'mechagotchi_windows_artifact_v1','target':'windows_x64_onedir',
                'files':{'Mechagotchi.exe':{'size':10,'sha256':hashlib.sha256(b'executable').hexdigest()}}}
            manifest['content_id']=hashlib.sha256(json.dumps(manifest,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
            (root/'artifact-manifest.json').write_text(json.dumps(manifest))
            self.assertEqual(manifest,validate_artifact_manifest(root))
            (root/'Mechagotchi.exe').write_bytes(b'tampered')
            with self.assertRaises(ValueError):validate_artifact_manifest(root)

    def test_pre_window_refusal_or_unfinished_exit_cannot_pass_window_gate(self):
        from verify_detached_release import startup_window_evidence
        partial={'view':'startup','startup_outcome':'refused','stopped':True,'exit_code':2,
                 'startup':{'entered_play':False}}
        self.assertFalse(startup_window_evidence(partial,2))
        complete={**partial,'display':{'driver':'dummy','size':[640,480],'resizable':True},
                  'startup_rendered_frames':1}
        self.assertTrue(startup_window_evidence(complete,2))
        self.assertFalse(startup_window_evidence({**complete,'stopped':False},2))
        self.assertFalse(startup_window_evidence(complete,1))
        self.assertFalse(startup_window_evidence({**complete,'startup':{'entered_play':True}},2))
        self.assertFalse(startup_window_evidence({**complete,'startup_rendered_frames':0},2))

if __name__=='__main__':unittest.main()
