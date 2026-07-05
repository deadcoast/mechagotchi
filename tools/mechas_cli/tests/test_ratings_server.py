import json
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mechas_cli.ratings_server import (  # noqa: E402
    CSV_HEADER,
    start_server,
)


def _post(url: str, body: str) -> tuple[int, dict]:
    request = urllib.request.Request(
        url,
        data=body.encode("utf-8"),
        headers={"Content-Type": "text/csv"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read())


class RatingsServerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        (self.directory / "tool.html").write_text("<html>ok</html>", "utf-8")
        self.ratings_path = self.directory / "ratings.csv"
        self.exports: list[tuple[int, Path, Path | None]] = []
        self.server = start_server(
            self.directory,
            self.ratings_path,
            port=0,
            on_export=lambda *args: self.exports.append(args),
        )
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}"

    def tearDown(self):
        self.server.shutdown()
        self.temp.cleanup()

    def test_serves_files_from_directory(self):
        with urllib.request.urlopen(f"{self.base}/tool.html") as response:
            self.assertEqual(200, response.status)
            self.assertIn(b"ok", response.read())

    def test_export_writes_csv_and_reports_rows(self):
        body = CSV_HEADER + "\na,b,c,me,5,4,3,2,1,\n"
        status, payload = _post(f"{self.base}/api/export", body)

        self.assertEqual(200, status)
        self.assertTrue(payload["ok"])
        self.assertEqual(1, payload["rows"])
        self.assertEqual(body, self.ratings_path.read_text(encoding="utf-8"))
        self.assertEqual(1, len(self.exports))
        rows, path, backup = self.exports[0]
        self.assertEqual(1, rows)
        self.assertEqual(self.ratings_path, path)
        self.assertIsNone(backup)

    def test_export_backs_up_existing_ratings(self):
        self.ratings_path.write_text(CSV_HEADER + "\nold,row\n", "utf-8")
        body = CSV_HEADER + "\na,b,c,me,5,4,3,2,1,\n"

        status, payload = _post(f"{self.base}/api/export", body)

        self.assertEqual(200, status)
        _, _, backup = self.exports[0]
        self.assertIsNotNone(backup)
        self.assertTrue(backup.exists())
        self.assertIn("old,row", backup.read_text(encoding="utf-8"))
        self.assertEqual(body, self.ratings_path.read_text(encoding="utf-8"))

    def test_export_rejects_wrong_header_without_writing(self):
        status, payload = _post(
            f"{self.base}/api/export", "not,a,rating,header\n1,2,3,4\n"
        )

        self.assertEqual(400, status)
        self.assertFalse(payload["ok"])
        self.assertFalse(self.ratings_path.exists())
        self.assertEqual([], self.exports)

    def test_unknown_post_endpoint_is_404(self):
        status, payload = _post(f"{self.base}/api/other", "x")
        self.assertEqual(404, status)
        self.assertFalse(payload["ok"])


if __name__ == "__main__":
    unittest.main()
