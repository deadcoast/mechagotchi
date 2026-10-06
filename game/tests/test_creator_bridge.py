"""The source creator server belongs to the active native app."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.request import urlopen
from urllib.error import URLError

ROOT = Path(__file__).resolve().parents[2]
for folder in ("game/src", "packages/mecha_engine/src"):
    sys.path.insert(0, str(ROOT / folder))
from mecha_game.creator_bridge import CreatorBridge


class CreatorBridgeTests(unittest.TestCase):
    def test_actual_loopback_server_has_selected_context_and_joins(self):
        with tempfile.TemporaryDirectory() as directory:
            keeper = Path(directory) / "missing selected save"
            bridge = CreatorBridge(keeper)
            try:
                with patch("mecha_game.creator_bridge.webbrowser.open", side_effect=OSError("no browser")):
                    url = bridge.open()
                self.assertFalse(bridge.browser_opened)
                with urlopen(url + "api/context", timeout=5) as response:
                    context = json.load(response)
                self.assertEqual("native_keeper", context["kind"])
                self.assertEqual(str(keeper.resolve()), context["keeper_dir"])
                self.assertFalse(context["available"])
                self.assertFalse(keeper.exists(), "Inspection must not create a missing save")
                thread = bridge.server.workshop_thread
                self.assertTrue(thread.is_alive())
            finally:
                bridge.close()
            self.assertFalse(thread.is_alive())
            bridge.close()
            with self.assertRaises((URLError, OSError)):
                urlopen(url + "api/context", timeout=1)

    def test_missing_install_resources_refuse_without_other_checkout_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("mecha_game.creator_bridge.workshop_resource_root", return_value=Path(directory)):
                with self.assertRaisesRegex(ValueError, "Workshop resources"):
                    CreatorBridge(Path(directory) / "keeper").open()


if __name__ == "__main__":
    unittest.main()
