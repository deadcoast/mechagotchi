"""The mecha_workshop local server — the engine answers, the page asks.

Serves the grid editor and exposes the local API the charter's 4-W pillar
requires: validation is the ENGINE'S verdict (`mecha_engine.genome
.validate_grid`), SLIP alignment is the Stage 0 authority
(`labs/grid_genome/slip.is_grid_aligned` — switches to a promoted
`mecha_engine.slip` surface when one exists), grid construction is the
canonical matrix->grid builder the research proved, and the structural
load shown to creators is the archive's contracted stress-probe formula.
The workshop layer may import both the package and the labs (it is
application content, not package code); nothing here reimplements a
validator that could drift.

Endpoints:

- GET  /                    the grid editor page
- GET  /api/palettes        engine palettes
- POST /api/validate        {matrix, palette_id, grid_id?} -> verdict,
                            per-profile alignment, morphology stats
- POST /api/save            strict: only validator-valid grids are
                            written (backup-before-overwrite)
- GET  /api/grids           saved workshop grids
- GET  /api/grids/<name>    one saved grid as an editable matrix
- GET  /slip                the SLIP profile creator page
- POST /api/slip/validate   {profile} -> Stage 0 authority verdict,
                            optional authoring review, live grid compat
- POST /api/slip/save       strict: only validate_slip-clean profiles
- GET  /api/slips           curated + workshop-authored profiles
- GET  /api/slips/<id>      one profile for editing

Launched by `mechas workshop --editor` with the workspace interpreter.
"""

import argparse
import functools
import json
import re
import socket
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
import sys  # noqa: E402

for path in [
    ROOT / "packages" / "mecha_engine" / "src",
    ROOT / "labs" / "grid_genome",
    ROOT / "labs" / "cellular_automata",
]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from ca_nca_growth_repair import (  # noqa: E402
    grid_from_matrix,
    matrix_from_grid,
)
from corpus_builder import PALETTES, build_seed_grids  # noqa: E402
from slip import is_grid_aligned, validate_slip  # noqa: E402

from mecha_engine.genome import validate_grid  # noqa: E402


WORKSHOP_DIR = ROOT / "workshop"
DEFAULT_GRIDS_DIR = ROOT / "data" / "workshop" / "grids"
DEFAULT_SLIPS_DIR = ROOT / "data" / "workshop" / "slips"
SLIP_VALID_DIR = ROOT / "data" / "slips" / "valid"
TOKENS = {".", "B", "A", "E", "M"}
GRID_SIZE = 8


def _load_profiles() -> dict[str, dict]:
    profiles = {}
    if SLIP_VALID_DIR.exists():
        for path in sorted(SLIP_VALID_DIR.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            profiles[payload.get("profile_id", path.stem)] = payload
    return profiles


def _check_matrix(matrix: object) -> str | None:
    if (
        not isinstance(matrix, list)
        or len(matrix) != GRID_SIZE
        or any(
            not isinstance(row, list) or len(row) != GRID_SIZE
            for row in matrix
        )
    ):
        return f"matrix must be {GRID_SIZE}x{GRID_SIZE}"
    bad = sorted(
        {token for row in matrix for token in row if token not in TOKENS}
    )
    if bad:
        return f"unknown tokens: {', '.join(map(str, bad))}"
    return None


def _morphology_stats(grid: dict) -> dict:
    """Morphology stats incl. the archive's contracted stress-probe load.

    Formula mirrored verbatim from
    ``mecha_engine.archive._metrics.lifecycle_probe_grid``:
    load = clamp(body_mass/16 + (1 - symmetry) * 0.65 - sensors * 0.08).
    ``collapse_risk`` marks the lifecycle's documented bistability
    boundary (stress >= 0.95 collapses around tick 12-14).
    """
    cells = grid.get("cells", [])
    body_mass = sum(1 for cell in cells if cell.get("organ") == "core")
    sensors = grid.get("organs", {}).get("sensors", {}).get("cells", [])
    sensor_count = len(sensors) if isinstance(sensors, list) else 0
    occupied = {
        (cell["x"], cell["y"], cell.get("role")) for cell in cells
    }
    symmetry = (
        sum(
            1
            for x, y, role in occupied
            if (GRID_SIZE - 1 - x, y, role) in occupied
        )
        / len(occupied)
        if occupied
        else 0.0
    )
    load = max(
        0.0,
        min(1.0, body_mass / 16 + (1 - symmetry) * 0.65 - sensor_count * 0.08),
    )
    return {
        "body_mass": body_mass,
        "sensor_count": sensor_count,
        "symmetry": round(symmetry, 6),
        "stress_load": round(load, 6),
        "collapse_risk": load >= 0.95,
        "cell_count": len(cells),
    }


def _build_grid(matrix: list[list[str]], palette_id: str, grid_id: str) -> dict:
    palette = {
        "palette_id": palette_id,
        "colors": PALETTES.get(palette_id, PALETTES["lcd_green"]),
        "background_index": 0,
    }
    return grid_from_matrix(
        grid_id=grid_id,
        matrix=matrix,
        palette=palette,
        parent_grid_id=None,
        source="workshop_grid_editor",
        mutation_events=["workshop_grid_editor_draft"],
        generation_delta=0,
    )


def _safe_name(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", str(name).lower()).strip("_")
    return slug[:48] or "unnamed"


class WorkshopServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False

    def __init__(
        self,
        address: tuple[str, int],
        grids_dir: Path,
        slips_dir: Path,
    ) -> None:
        self.grids_dir = grids_dir
        self.slips_dir = slips_dir
        self.curated_profiles = _load_profiles()
        self.seed_grids = build_seed_grids()
        handler = functools.partial(_Handler, directory=str(WORKSHOP_DIR))
        super().__init__(address, handler)

    def all_profiles(self) -> dict[str, dict]:
        """Curated fixtures plus workshop-authored profiles (read fresh)."""
        profiles = dict(self.curated_profiles)
        if self.slips_dir.exists():
            for path in sorted(self.slips_dir.glob("*.json")):
                if path.name.endswith(".bak.json"):
                    continue
                payload = json.loads(path.read_text(encoding="utf-8"))
                profiles[payload.get("profile_id", path.stem)] = payload
        return profiles

    def server_bind(self) -> None:
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1
            )
        super().server_bind()


class _Handler(SimpleHTTPRequestHandler):
    server: WorkshopServer

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        pass

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length).decode("utf-8"))

    # ------------------------------------------------------------- GET
    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?")[0]
        if path == "/":
            self.path = "/grid_editor/grid_editor.html"
            return super().do_GET()
        if path == "/slip":
            self.path = "/slip_creator/slip_creator.html"
            return super().do_GET()
        if path == "/api/palettes":
            self._json(200, {"palettes": PALETTES})
            return
        if path == "/api/grids":
            grids = []
            for file in sorted(self.server.grids_dir.glob("*.json")):
                if file.name.endswith(".bak.json"):
                    continue
                payload = json.loads(file.read_text(encoding="utf-8"))
                grids.append(
                    {
                        "name": file.stem,
                        "grid_id": payload.get("grid_id"),
                        "palette_id": payload.get("palette", {}).get(
                            "palette_id"
                        ),
                    }
                )
            self._json(200, {"grids": grids})
            return
        if path == "/api/slips":
            slips = []
            for profile_id, profile in sorted(
                self.server.curated_profiles.items()
            ):
                slips.append(
                    {
                        "profile_id": profile_id,
                        "name": profile.get("name"),
                        "source": "curated",
                    }
                )
            if self.server.slips_dir.exists():
                for file in sorted(self.server.slips_dir.glob("*.json")):
                    if file.name.endswith(".bak.json"):
                        continue
                    payload = json.loads(file.read_text(encoding="utf-8"))
                    slips.append(
                        {
                            "profile_id": payload.get("profile_id", file.stem),
                            "name": payload.get("name"),
                            "source": "workshop",
                        }
                    )
            self._json(200, {"slips": slips})
            return
        if path.startswith("/api/slips/"):
            wanted = path.rsplit("/", 1)[-1]
            profiles = self.server.all_profiles()
            if wanted not in profiles:
                self._json(404, {"ok": False, "error": "no such profile"})
                return
            self._json(200, {"ok": True, "profile": profiles[wanted]})
            return
        if path.startswith("/api/grids/"):
            name = _safe_name(path.rsplit("/", 1)[-1])
            file = self.server.grids_dir / f"{name}.json"
            if not file.exists():
                self._json(404, {"ok": False, "error": "no such grid"})
                return
            grid = json.loads(file.read_text(encoding="utf-8"))
            self._json(
                200,
                {
                    "ok": True,
                    "name": name,
                    "matrix": matrix_from_grid(grid),
                    "palette_id": grid.get("palette", {}).get("palette_id"),
                    "grid_id": grid.get("grid_id"),
                },
            )
            return
        return super().do_GET()

    # ------------------------------------------------------------ POST
    def do_POST(self) -> None:  # noqa: N802
        path = self.path.split("?")[0]
        if path not in (
            "/api/validate",
            "/api/save",
            "/api/slip/validate",
            "/api/slip/save",
        ):
            self._json(404, {"ok": False, "error": "unknown endpoint"})
            return
        try:
            payload = self._read_json()
        except json.JSONDecodeError:
            self._json(400, {"ok": False, "error": "invalid JSON"})
            return

        if path == "/api/slip/validate":
            self._slip_validate(payload)
            return
        if path == "/api/slip/save":
            self._slip_save(payload)
            return
        matrix = payload.get("matrix")
        problem = _check_matrix(matrix)
        if problem:
            self._json(400, {"ok": False, "error": problem})
            return
        palette_id = payload.get("palette_id", "lcd_green")
        if palette_id not in PALETTES:
            self._json(400, {"ok": False, "error": "unknown palette"})
            return

        if path == "/api/validate":
            grid = _build_grid(
                matrix, palette_id, payload.get("grid_id") or "workshop_draft"
            )
            validation = validate_grid(grid)
            alignment = {
                profile_id: {
                    "ok": (result := is_grid_aligned(grid, profile)).ok,
                    "errors": list(result.errors),
                }
                for profile_id, profile in self.server.all_profiles().items()
            }
            self._json(
                200,
                {
                    "ok": True,
                    "valid": validation.ok,
                    "errors": list(validation.errors),
                    "alignment": alignment,
                    "stats": _morphology_stats(grid),
                },
            )
            return

        # /api/save — strict per the charter's 4-W pillar: the workshop
        # never writes a grid the engine would reject.
        name = _safe_name(payload.get("name", ""))
        grid = _build_grid(matrix, palette_id, f"workshop_{name}")
        validation = validate_grid(grid)
        if not validation.ok:
            self._json(
                400,
                {
                    "ok": False,
                    "error": "the engine rejects this grid; fix it first",
                    "errors": list(validation.errors),
                },
            )
            return
        self.server.grids_dir.mkdir(parents=True, exist_ok=True)
        target = self.server.grids_dir / f"{name}.json"
        backup = None
        if target.exists():
            stamp = time.strftime("%Y%m%d-%H%M%S")
            backup = target.with_name(f"{name}.{stamp}.bak.json")
            backup.write_bytes(target.read_bytes())
        target.write_text(
            json.dumps(grid, indent=2) + "\n", encoding="utf-8"
        )
        self._json(
            200,
            {
                "ok": True,
                "file": target.name,
                "backup": backup.name if backup else None,
            },
        )

    def _slip_validate(self, payload: dict) -> None:
        profile = payload.get("profile")
        if not isinstance(profile, dict):
            self._json(400, {"ok": False, "error": "profile must be an object"})
            return
        verdict = validate_slip(profile)
        aligned = 0
        if verdict.ok:
            for seed in self.server.seed_grids:
                if is_grid_aligned(seed, profile).ok:
                    aligned += 1
        workshop_grids = []
        if verdict.ok and self.server.grids_dir.exists():
            for file in sorted(self.server.grids_dir.glob("*.json")):
                if file.name.endswith(".bak.json"):
                    continue
                grid = json.loads(file.read_text(encoding="utf-8"))
                result = is_grid_aligned(grid, profile)
                workshop_grids.append(
                    {
                        "name": file.stem,
                        "ok": result.ok,
                        "errors": list(result.errors),
                    }
                )
        self._json(
            200,
            {
                "ok": True,
                "valid": verdict.ok,
                "errors": list(verdict.errors),
                "authoring_review": _authoring_review(profile)
                if verdict.ok
                else {
                    "available": False,
                    "reason": "fix authority errors first",
                },
                "grid_compat": {
                    "seed_corpus": {
                        "aligned": aligned,
                        "total": len(self.server.seed_grids),
                    },
                    "workshop_grids": workshop_grids,
                },
            },
        )

    def _slip_save(self, payload: dict) -> None:
        profile = payload.get("profile")
        if not isinstance(profile, dict):
            self._json(400, {"ok": False, "error": "profile must be an object"})
            return
        verdict = validate_slip(profile)
        if not verdict.ok:
            self._json(
                400,
                {
                    "ok": False,
                    "error": "the Stage 0 authority rejects this profile; "
                    "fix it first",
                    "errors": list(verdict.errors),
                },
            )
            return
        profile_id = profile["profile_id"]
        if profile_id in self.server.curated_profiles:
            self._json(
                400,
                {
                    "ok": False,
                    "error": "profile_id " + repr(profile_id) + " belongs "
                    "to a curated fixture profile - choose your own id",
                },
            )
            return
        self.server.slips_dir.mkdir(parents=True, exist_ok=True)
        target = self.server.slips_dir / (_safe_name(profile_id) + ".json")
        backup = None
        if target.exists():
            stamp = time.strftime("%Y%m%d-%H%M%S")
            backup = target.with_name(target.stem + "." + stamp + ".bak.json")
            backup.write_bytes(target.read_bytes())
        target.write_text(
            json.dumps(profile, indent=2) + "\n", encoding="utf-8"
        )
        self._json(
            200,
            {
                "ok": True,
                "file": target.name,
                "backup": backup.name if backup else None,
            },
        )


def _authoring_review(profile: dict) -> dict:
    """The workshop_editor authoring panel, when its dependencies exist.

    The panel adds pydantic/migration review on top of the Stage 0
    authority. Availability is recorded per-run (H-01 style), never
    assumed: environments without the lab dependency group simply report
    it unavailable.
    """
    try:
        panel_dir = ROOT / "labs" / "workshop_editor"
        if str(panel_dir) not in sys.path:
            sys.path.insert(0, str(panel_dir))
        from slip_authoring_panel import validate_authoring_draft

        review = validate_authoring_draft(profile)
        errors = review["errors"]
        if errors and isinstance(errors[0], dict):
            errors = [error.get("message", str(error)) for error in errors]
        return {
            "available": True,
            "ok": review["ok"],
            "error_families": review["error_families"],
            "errors": errors,
        }
    except Exception as error:  # dependency or import shape drift
        return {"available": False, "reason": str(error)[:200]}


def start_workshop_server(
    *,
    port: int = 0,
    grids_dir: Path = DEFAULT_GRIDS_DIR,
    slips_dir: Path = DEFAULT_SLIPS_DIR,
) -> WorkshopServer:
    server = WorkshopServer(("127.0.0.1", port), grids_dir, slips_dir)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def main() -> None:
    parser = argparse.ArgumentParser(description="mecha_workshop server")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--grids-dir", type=Path, default=DEFAULT_GRIDS_DIR)
    args = parser.parse_args()
    server = start_workshop_server(port=args.port, grids_dir=args.grids_dir)
    print(
        f"workshop serving on http://127.0.0.1:{server.server_address[1]}/",
        flush=True,
    )
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
