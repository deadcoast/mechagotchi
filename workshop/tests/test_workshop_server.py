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
