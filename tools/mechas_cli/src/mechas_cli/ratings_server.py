"""Local server behind `mechas rate --creatures`.

Serves the generated rating tool from ``data/readability`` and accepts the
finished ratings back on ``POST /api/export``, writing them straight into
the project (backing up any existing file first) so nobody ever moves a
CSV by hand — the workflow error this CLI exists to remove.

Stdlib-only on purpose: the server is testable without the CLI's
dependencies, and it inherits the project's determinism habits everywhere
except backup filenames (wall-clock timestamped, which is fine for
user-facing safety copies).
"""

from __future__ import annotations

import functools
import json
import threading
import time
from collections.abc import Callable
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


CSV_HEADER = (
    "sample_id,grid_id,source,reviewer_id,silhouette,organ_clarity,"
    "palette_contrast,animation_readiness,companion_appeal,notes"
)
RATINGS_FILENAME = "slip_readability_calibration_ratings.csv"


class RatingsServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(
        self,
        address: tuple[str, int],
        directory: Path,
        ratings_path: Path,
        on_export: Callable[[int, Path, Path | None], None] | None = None,
    ) -> None:
        self.directory = directory
        self.ratings_path = ratings_path
        self.on_export = on_export
        handler = functools.partial(_Handler, directory=str(directory))
        super().__init__(address, handler)


class _Handler(SimpleHTTPRequestHandler):
    server: RatingsServer

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        pass  # the CLI narrates; raw request logs would be noise

    def _respond_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802 (http.server API)
        if self.path.split("?")[0] != "/api/export":
            self._respond_json(404, {"ok": False, "error": "unknown endpoint"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        csv_text = self.rfile.read(length).decode("utf-8")
        lines = [line for line in csv_text.splitlines() if line.strip()]
        if not lines or lines[0] != CSV_HEADER:
            self._respond_json(
                400,
                {
                    "ok": False,
                    "error": "CSV header does not match the rating template",
                },
            )
            return

        ratings_path = self.server.ratings_path
        backup_path: Path | None = None
        if ratings_path.exists():
            stamp = time.strftime("%Y%m%d-%H%M%S")
            backup_path = ratings_path.with_name(
                f"{ratings_path.stem}.{stamp}.bak.csv"
            )
            backup_path.write_bytes(ratings_path.read_bytes())
        ratings_path.parent.mkdir(parents=True, exist_ok=True)
        ratings_path.write_text(csv_text, encoding="utf-8")

        rows = len(lines) - 1
        # Notify BEFORE responding: when the browser sees success, the
        # export (file + callback) is fully complete — no ordering race.
        if self.server.on_export is not None:
            try:
                self.server.on_export(rows, ratings_path, backup_path)
            except Exception:
                pass  # a narration failure must never fail the export
        self._respond_json(
            200,
            {
                "ok": True,
                "rows": rows,
                "saved_to": ratings_path.name,
            },
        )


def start_server(
    directory: Path,
    ratings_path: Path,
    *,
    port: int = 0,
    on_export: Callable[[int, Path, Path | None], None] | None = None,
) -> RatingsServer:
    """Start the ratings server on a background thread; caller shuts down."""
    server = RatingsServer(
        ("127.0.0.1", port), directory, ratings_path, on_export
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server
