"""Staged resource/import proof; this is explicitly not native artifact proof."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "game"))
from release_payload import stage_payload, HELPER_FILES, write_artifact_manifest, file_record


@unittest.skipUnless(sys.platform == "win32", "Windows x64 release staging is the declared delivery target")
class PayloadStagingTests(unittest.TestCase):
    def test_staged_bytes_manifest_and_actual_helper_imports(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            stage = base / "runtime"
            manifest = stage_payload(stage)
            self.assertTrue(manifest["source"]["head"])
            self.assertIn("game/PLAYER-README.txt", manifest["source"]["files"])
            bundle = base / "bundle"
            bundle.mkdir()
            artifact = json.loads(write_artifact_manifest(bundle, manifest).read_text(encoding="utf-8"))
            self.assertEqual((ROOT / "game/PLAYER-README.txt").read_bytes(), (bundle / "README.txt").read_bytes())
            self.assertEqual(file_record(bundle / "README.txt"), artifact["files"]["README.txt"])
            self.assertEqual(32, len(HELPER_FILES))
            self.assertIn("labs/lifecycle_sim/body_response.py", HELPER_FILES)
            for relative in HELPER_FILES:
                self.assertEqual((ROOT / relative).read_bytes(), (stage / relative).read_bytes())
            script = r'''
import json, sys
from pathlib import Path
from urllib.request import Request, urlopen
stage, checkout = map(Path, sys.argv[1:])
# Source application/engine code only. Every dynamic Workshop helper/resource
# must come from the staged payload; final native proof is a separate gate.
sys.path[:0] = [str(checkout / "game/src"), str(checkout / "packages/mecha_engine/src")]
sys.frozen = True
sys._MEIPASS = str(stage)
from mecha_game.runtime_resources import inspect_runtime
from mecha_game.campaign import WEATHER_NAMES, build_weather_source, default_campaign_paths
from mecha_game.creator_bridge import CreatorBridge
from mecha_game.packets import default_fixture_paths
initial = inspect_runtime()
assert initial["complete"], initial
default_fixture_paths(checkout)
default_campaign_paths(checkout)
counts = {name: len(build_weather_source(name) or []) for name in WEATHER_NAMES}
assert counts["calm"] == 0 and counts["stable_soup"] == 6 and counts["storm"] == 6
assert counts["real"] > 0 and counts["callback"] > 0
bridge = CreatorBridge(stage.parent / "missing keeper")
try:
    url = bridge.open(open_browser=False)
    routes = ["", "slip", "preview", "inspect", "packs", "shared/authoring.js", "shared/authoring.css", "api/context", "api/slips", "api/preview/creatures"]
    checks = {}
    for route in routes:
        with urlopen(url + route, timeout=10) as response:
            body = response.read()
            assert body, route
            checks[route] = response.status
    profile = json.loads((stage / "data/slips/valid/slip_v2_cleanliness.json").read_text(encoding="utf-8"))
    request = Request(url + "api/slip/validate", data=json.dumps({"profile": profile}).encode(), headers={"Content-Type":"application/json"})
    with urlopen(request, timeout=10) as response:
        verdict = json.load(response)
    report = inspect_runtime()
    for name in json.loads((stage / "runtime-manifest.json").read_text(encoding="utf-8"))["helper_modules"]:
        if name in report["loaded_modules"]:
            assert Path(report["loaded_modules"][name]).is_relative_to(stage), (name, report["loaded_modules"][name])
    thread = bridge.server.workshop_thread
finally:
    bridge.close()
assert not thread.is_alive()
assert not (stage.parent / "missing keeper").exists()
print(json.dumps({"proof_kind":"staged_source_helpers_not_frozen_artifact", "weather_records":counts, "routes":checks, "slip_verdict":verdict, "runtime":report, "owned_server_joined":True}))
'''
            environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1")
            environment.pop("PYTHONPATH", None)
            result = subprocess.run([sys.executable, "-B", "-I", "-c", script, str(stage), str(ROOT)],
                                    cwd=base, env=environment, capture_output=True, text=True, encoding="utf-8", timeout=45)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            report = json.loads(result.stdout.strip().splitlines()[-1])
            evidence = os.environ.get("MECHA_X4_STAGING_REPORT")
            if evidence:
                Path(evidence).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            self.assertTrue(report["owned_server_joined"])
            self.assertTrue(report["runtime"]["complete"])
            self.assertGreater(len(report["runtime"]["loaded_modules"]), 15)
            # Available advisory dependencies must load from the installed
            # environment here, then from the frozen bundle in detached proof.
            self.assertTrue(report["slip_verdict"]["authoring_review"]["available"], report["slip_verdict"])


if __name__ == "__main__":
    unittest.main()
