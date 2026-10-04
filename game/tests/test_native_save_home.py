"""R4: frozen bundles must not accidentally choose their data directory."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
for relative in ("game/src","packages/mecha_engine/src"):
    sys.path.insert(0,str(ROOT/relative))
from mecha_game.app import default_keeper_dir


class NativeSaveHomeTests(unittest.TestCase):
    def test_frozen_new_release_uses_user_home_and_preserves_legacy(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            bundle=root/"release/_internal"
            (bundle/"data/seed_grids_16x16").mkdir(parents=True)
            home=root/"user/.mechagotchi"
            legacy=bundle/"keeper"
            with patch.object(sys,"frozen",True,create=True),patch.object(sys,"_MEIPASS",str(bundle),create=True),patch.object(Path,"home",return_value=root/"user"):
                self.assertEqual(home,default_keeper_dir(bundle/"mecha_game/app.py"))
                self.assertFalse(home.exists())
                for name in ("companion.json","campaign_state.json","campaign.sqlite3","lineage.json"):
                    legacy.mkdir(exist_ok=True)
                    save=legacy/name
                    save.write_bytes(b"preserved legacy bytes")
                    self.assertEqual(legacy,default_keeper_dir())
                    self.assertEqual(b"preserved legacy bytes",save.read_bytes())
                    save.unlink()
                (legacy/"companion.json").write_bytes(b"legacy")
                home.mkdir(parents=True)
                (home/"companion.json").write_bytes(b"home")
                self.assertEqual(home,default_keeper_dir())
                self.assertEqual(b"legacy",(legacy/"companion.json").read_bytes())
                self.assertEqual(b"home",(home/"companion.json").read_bytes())

    def test_source_checkout_keeps_its_repository_save_home(self):
        with patch.object(sys,"frozen",False,create=True):
            self.assertEqual(ROOT/"keeper",default_keeper_dir(ROOT/"game/src/mecha_game/app.py"))


if __name__=="__main__": unittest.main()
