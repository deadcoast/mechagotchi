"""X4 delivery refusals: a frozen application cannot borrow its checkout."""
from pathlib import Path
import sys
import json
import hashlib
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for folder in ("game/src", "packages/mecha_engine/src", "game"):
    sys.path.insert(0, str(ROOT / folder))
from mecha_game import packets, campaign
import build_release
from mecha_game import runtime_resources as runtime
from mecha_game.creator_bridge import CreatorBridge


class RuntimeDeliveryTests(unittest.TestCase):
    # game/ exists in a fresh source checkout; ignored .development need not.
    # The temporary bundle remains inside the checkout to expose ancestor leaks.
    def test_frozen_missing_defaults_do_not_walk_into_checkout(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "game") as folder:
            with patch.object(sys, "frozen", True, create=True), patch.object(sys, "_MEIPASS", folder, create=True):
                with self.assertRaises(FileNotFoundError):
                    packets.default_fixture_paths(start=ROOT)

    def test_frozen_missing_weather_does_not_walk_into_checkout(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "game") as folder:
            with patch.object(sys, "frozen", True, create=True), patch.object(sys, "_MEIPASS", folder, create=True):
                for load in (campaign.load_real_weather_source, campaign.load_callback_weather_source):
                    with self.subTest(loader=load.__name__), self.assertRaises(FileNotFoundError):
                        load(start=ROOT)

    def test_frozen_missing_campaign_does_not_walk_into_checkout(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "game") as folder:
            with patch.object(sys, "frozen", True, create=True), patch.object(sys, "_MEIPASS", folder, create=True):
                with self.assertRaises(FileNotFoundError):
                    campaign.default_campaign_paths(start=ROOT)

    def test_payload_declares_weather_and_creator_closure(self):
        sources = {source for source, destination in build_release.BUNDLED_DATA}
        required = {
            "data/cubff_real_ingest/real_snapshot_ingest_stage0_report.json",
            "data/cubff_real_ingest/callback_states/callback_states_compact.json",
            "workshop/server/workshop_server.py",
            "workshop/server/authoring.py", "workshop/server/drafts.py",
            "labs/workshop_editor/png_apng_sidecar_decoder.py",
            "labs/grid_genome/corpus_builder.py",
        }
        self.assertFalse(required - sources, sorted(required - sources))

    def test_source_root_is_explicit_and_installed_wheel_cannot_borrow_checkout(self):
        self.assertEqual(ROOT, runtime.source_checkout_root(ROOT / "game/tests"))
        self.assertEqual([ROOT], runtime.resource_roots())
        with patch.object(runtime, "__file__", str(ROOT / ".venv/Lib/site-packages/mecha_game/runtime_resources.py")):
            self.assertIsNone(runtime.source_checkout_root(ROOT))
            self.assertEqual([], runtime.resource_roots(ROOT))
            self.assertEqual("unsupported_install", runtime.inspect_runtime()["mode"])

    def test_frozen_without_meipass_uses_executable_internal_only(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(sys, "frozen", True, create=True), patch.object(sys, "executable", str(Path(folder) / "Mechagotchi.exe")):
                self.assertEqual(Path(folder).resolve() / "_internal", runtime.runtime_root(ROOT))
                self.assertIsNone(runtime.source_checkout_root(ROOT))

    def _manifest(self, root):
        path = root / packets.HELLO_SEED
        path.parent.mkdir(parents=True)
        path.write_bytes(b"seed")
        slip = root / packets.DEFAULT_SLIP
        slip.parent.mkdir(parents=True)
        slip.write_bytes(b"slip")
        manifest = {"format": runtime.MANIFEST_FORMAT, "target": runtime.NATIVE_TARGET,
                    "source": {"head": "fixture", "dirty": True, "files": {}},
                    "files": {item.relative_to(root).as_posix(): {"size": item.stat().st_size, "sha256": hashlib.sha256(item.read_bytes()).hexdigest()} for item in (path, slip)}}
        manifest["content_id"] = runtime.content_identity(manifest)
        (root / runtime.MANIFEST_NAME).write_text(json.dumps(manifest), encoding="utf-8")
        return manifest

    def test_manifest_distinguishes_complete_missing_and_changed_resources(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            manifest = self._manifest(root)
            with patch.object(sys, "frozen", True, create=True), patch.object(sys, "_MEIPASS", str(root), create=True):
                report = runtime.inspect_runtime()
                self.assertTrue(report["complete"])
                self.assertEqual(manifest["content_id"], report["content_id"])
                self.assertEqual((root / packets.HELLO_SEED, root / packets.DEFAULT_SLIP), packets.default_fixture_paths(ROOT))
                (root / packets.HELLO_SEED).write_bytes(b"changed")
                (root / packets.DEFAULT_SLIP).unlink()
                report = runtime.inspect_runtime()
                self.assertFalse(report["complete"])
                self.assertEqual([packets.HELLO_SEED.as_posix()], report["mismatched"])
                self.assertEqual([packets.DEFAULT_SLIP.as_posix()], report["missing"])
                with self.assertRaisesRegex(FileNotFoundError, "mismatched"):
                    runtime.validate_resource(root / packets.HELLO_SEED)

    def test_manifest_identity_and_path_escape_are_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            manifest = self._manifest(root)
            manifest["content_id"] = "f" * 64
            (root / runtime.MANIFEST_NAME).write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "identity"):
                runtime.read_manifest(root)
            manifest["files"]["../outside.json"] = {"size": 1, "sha256": "a" * 64}
            manifest["content_id"] = runtime.content_identity(manifest)
            (root / runtime.MANIFEST_NAME).write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "entry"):
                runtime.read_manifest(root)

    def test_creator_no_browser_still_serves_selected_context_and_joins(self):
        from urllib.request import urlopen
        with tempfile.TemporaryDirectory() as folder:
            bridge = CreatorBridge(Path(folder) / "missing keeper")
            try:
                with patch("mecha_game.creator_bridge.webbrowser.open") as browser:
                    url = bridge.open(open_browser=False)
                    browser.assert_not_called()
                with urlopen(url + "api/context", timeout=5) as response:
                    context = json.load(response)
                self.assertEqual("native_keeper", context["kind"])
                self.assertFalse(bridge.browser_opened)
                thread = bridge.server.workshop_thread
            finally:
                bridge.close()
            self.assertFalse(thread.is_alive())
            self.assertFalse((Path(folder) / "missing keeper").exists())

    def test_existing_build_evidence_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            (base / "dist/Mechagotchi").mkdir(parents=True)
            marker = base / "dist/Mechagotchi/owner.txt"
            marker.write_text("preserve", encoding="utf-8")
            with patch.object(sys, "platform", "win32"), patch("build_release.platform.machine", return_value="AMD64"):
                with self.assertRaises(FileExistsError):
                    build_release.build(base / "dist", base / "work")
            self.assertEqual("preserve", marker.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
