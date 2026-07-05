import json
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SERVER_DIR = ROOT / "workshop" / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

from workshop_server import start_workshop_server  # noqa: E402


VALID_MATRIX = [
    [".", "E", ".", ".", "E", ".", ".", "."],
    [".", ".", "B", "B", ".", ".", ".", "."],
    [".", "B", "A", "B", "B", ".", ".", "."],
    [".", ".", "B", "B", ".", "M", ".", "."],
    [".", ".", ".", "B", "B", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
]
BROKEN_MATRIX = [row[:] for row in VALID_MATRIX]
BROKEN_MATRIX[2][2] = "."  # no anchor anywhere


def _post(url: str, payload: dict) -> tuple[int, dict]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read())


def _get(url: str) -> tuple[int, dict]:
    with urllib.request.urlopen(url) as response:
        return response.status, json.loads(response.read())


class WorkshopServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.grids_dir = Path(cls.temp.name)
        cls.server = start_workshop_server(
            port=0, grids_dir=cls.grids_dir
        )
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.temp.cleanup()

    def test_serves_the_editor_page_at_root(self):
        with urllib.request.urlopen(f"{self.base}/") as response:
            body = response.read().decode("utf-8")
        self.assertEqual(200, response.status)
        self.assertIn("mecha_workshop", body)
        self.assertIn("/api/validate", body)

    def test_palettes_endpoint_lists_engine_palettes(self):
        status, payload = _get(f"{self.base}/api/palettes")
        self.assertEqual(200, status)
        self.assertIn("lcd_green", payload["palettes"])
        self.assertEqual(3, len(payload["palettes"]["lcd_green"]))

    def test_validate_returns_the_engine_verdict_and_stats(self):
        status, payload = _post(
            f"{self.base}/api/validate",
            {"matrix": VALID_MATRIX, "palette_id": "lcd_green"},
        )
        self.assertEqual(200, status)
        self.assertTrue(payload["valid"])
        self.assertEqual([], payload["errors"])
        stats = payload["stats"]
        self.assertGreater(stats["body_mass"], 0)
        self.assertEqual(2, stats["sensor_count"])
        self.assertGreaterEqual(stats["stress_load"], 0.0)
        self.assertLessEqual(stats["stress_load"], 1.0)
        self.assertIn("collapse_risk", stats)
        # SLIP alignment per available profile, from the Stage 0 authority.
        self.assertIn("slip_lcd_seed", payload["alignment"])
        self.assertTrue(payload["alignment"]["slip_lcd_seed"]["ok"])

    def test_validate_reports_engine_errors_verbatim(self):
        status, payload = _post(
            f"{self.base}/api/validate",
            {"matrix": BROKEN_MATRIX, "palette_id": "lcd_green"},
        )
        self.assertEqual(200, status)
        self.assertFalse(payload["valid"])
        self.assertGreater(len(payload["errors"]), 0)

    def test_save_is_strict_per_the_compatibility_pillar(self):
        status, payload = _post(
            f"{self.base}/api/save",
            {
                "name": "broken creature",
                "matrix": BROKEN_MATRIX,
                "palette_id": "lcd_green",
            },
        )
        self.assertEqual(400, status)
        self.assertFalse(payload["ok"])
        self.assertGreater(len(payload["errors"]), 0)
        self.assertEqual([], list(self.grids_dir.glob("broken_creature*.json")))

    def test_save_and_reload_a_valid_grid_with_backup(self):
        status, payload = _post(
            f"{self.base}/api/save",
            {
                "name": "First Creature!",
                "matrix": VALID_MATRIX,
                "palette_id": "lcd_green",
            },
        )
        self.assertEqual(200, status)
        self.assertTrue(payload["ok"])
        saved = self.grids_dir / payload["file"]
        self.assertTrue(saved.exists())
        grid = json.loads(saved.read_text(encoding="utf-8"))
        self.assertEqual("workshop_grid_editor", grid["metadata"]["source"])

        # Overwrite backs up the previous file.
        status, payload = _post(
            f"{self.base}/api/save",
            {
                "name": "First Creature!",
                "matrix": VALID_MATRIX,
                "palette_id": "amber_terminal",
            },
        )
        self.assertEqual(200, status)
        self.assertTrue(payload["backup"])
        self.assertTrue(any(self.grids_dir.glob("*.bak.json")))

        status, listing = _get(f"{self.base}/api/grids")
        self.assertEqual(200, status)
        names = [entry["name"] for entry in listing["grids"]]
        self.assertIn("first_creature", names)

        status, loaded = _get(f"{self.base}/api/grids/first_creature")
        self.assertEqual(200, status)
        self.assertEqual(VALID_MATRIX, loaded["matrix"])
        self.assertEqual("amber_terminal", loaded["palette_id"])

    def test_malformed_matrix_fails_loudly(self):
        status, payload = _post(
            f"{self.base}/api/validate",
            {"matrix": [["Z"]], "palette_id": "lcd_green"},
        )
        self.assertEqual(400, status)
        self.assertFalse(payload["ok"])


if __name__ == "__main__":
    unittest.main()


VALID_PROFILE = {
    "slip_version": "0.1.0",
    "profile_id": "workshop_test_profile",
    "name": "Workshop Test Profile",
    "grid": {
        "allowed_palettes": ["lcd_green", "amber_terminal"],
        "body_mass_min": 4,
        "body_mass_max": 24,
        "required_organ_roles": ["sensor", "expression"],
    },
    "mutation": {
        "cell_mutation_rate_max": 0.15,
        "organ_shift_rate_max": 0.05,
        "palette_shift_rate_max": 0.05,
        "symmetry_break_rate_max": 0.05,
    },
    "behavior": {"curiosity": 0.6, "neediness": 0.4, "sleepiness": 0.5},
    "survival_weights": {"stability": 0.5, "novelty": 0.25, "bond": 0.25},
}


class SlipCreatorEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        base = Path(cls.temp.name)
        cls.grids_dir = base / "grids"
        cls.slips_dir = base / "slips"
        cls.server = start_workshop_server(
            port=0, grids_dir=cls.grids_dir, slips_dir=cls.slips_dir
        )
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.temp.cleanup()

    def test_serves_the_slip_creator_page(self):
        with urllib.request.urlopen(f"{self.base}/slip") as response:
            body = response.read().decode("utf-8")
        self.assertEqual(200, response.status)
        self.assertIn("slip creator", body)
        self.assertIn("/api/slip/validate", body)

    def test_validate_profile_returns_authority_verdict_and_grid_compat(self):
        status, payload = _post(
            f"{self.base}/api/slip/validate", {"profile": VALID_PROFILE}
        )
        self.assertEqual(200, status)
        self.assertTrue(payload["valid"])
        self.assertEqual([], payload["errors"])
        # Grid compatibility: the seed corpus summary is always present.
        compat = payload["grid_compat"]
        self.assertEqual(50, compat["seed_corpus"]["total"])
        self.assertGreaterEqual(compat["seed_corpus"]["aligned"], 1)
        # The authoring review records availability honestly (H-01 style).
        self.assertIn("available", payload["authoring_review"])

    def test_validate_profile_reports_authority_errors_verbatim(self):
        broken = dict(VALID_PROFILE)
        broken = json.loads(json.dumps(VALID_PROFILE))
        broken["grid"]["allowed_palettes"] = ["neon_pink"]
        status, payload = _post(
            f"{self.base}/api/slip/validate", {"profile": broken}
        )
        self.assertEqual(200, status)
        self.assertFalse(payload["valid"])
        self.assertGreater(len(payload["errors"]), 0)

    def test_slip_save_is_strict_and_roundtrips(self):
        broken = json.loads(json.dumps(VALID_PROFILE))
        broken["slip_version"] = "9.9.9"
        files_before = sorted(self.slips_dir.glob("*.json")) if self.slips_dir.exists() else []
        status, payload = _post(
            f"{self.base}/api/slip/save", {"profile": broken}
        )
        self.assertEqual(400, status)
        self.assertFalse(payload["ok"])
        self.assertGreater(len(payload["errors"]), 0)
        files_after = sorted(self.slips_dir.glob("*.json")) if self.slips_dir.exists() else []
        self.assertEqual(files_before, files_after)

        status, payload = _post(
            f"{self.base}/api/slip/save", {"profile": VALID_PROFILE}
        )
        self.assertEqual(200, status)
        self.assertTrue(payload["ok"])
        self.assertTrue((self.slips_dir / payload["file"]).exists())

        status, listing = _get(f"{self.base}/api/slips")
        self.assertEqual(200, status)
        entries = {e["profile_id"]: e["source"] for e in listing["slips"]}
        self.assertEqual("workshop", entries["workshop_test_profile"])
        self.assertEqual("curated", entries.get("slip_lcd_seed", "curated"))

        status, loaded = _get(f"{self.base}/api/slips/workshop_test_profile")
        self.assertEqual(200, status)
        self.assertEqual(VALID_PROFILE, loaded["profile"])

    def test_authored_profiles_join_grid_editor_alignment(self):
        _post(f"{self.base}/api/slip/save", {"profile": VALID_PROFILE})
        status, payload = _post(
            f"{self.base}/api/validate",
            {"matrix": VALID_MATRIX, "palette_id": "lcd_green"},
        )
        self.assertEqual(200, status)
        self.assertIn("workshop_test_profile", payload["alignment"])
        self.assertTrue(payload["alignment"]["workshop_test_profile"]["ok"])
