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
- POST /api/validate        {matrix, palette_id, grid_id?,
                            cell_overrides?} -> verdict, per-profile
                            alignment, morphology stats, grid_cells
                            (T9 trait editor: per-cell material /
                            mutation_weight / full-vocabulary role
                            overrides, engine-validated)
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
- GET  /preview             the preview page
- GET  /api/preview/creatures  seed + workshop creatures to preview
- POST /api/preview/render  {source, name} -> the engine's render packet
- POST /api/preview/live    {source, name, profile_id, cycles, ticks} ->
                            runtime.live_cycle: damage/repair/episode
                            truth plus before/after packets
- POST /api/preview/offspring  {source, name, profile_id, count} ->
                            engine-generated children (or the engine's
                            alignment errors when the parent cannot
                            breed under the profile)
- POST /api/export/png      {matrix, palette_id, profile_id} -> a
                            self-contained PNG (embedded sidecar) via
                            the proven lab codec; strict on validity
                            and profile alignment
- POST /api/export/apng     same input -> the lab's animated APNG
                            (base + pulse frames); visual artifact
- POST /api/import/png      raw PNG bytes -> restored editable matrix,
                            or the codec's own failure families
- POST /api/export/aseprite same input -> a self-contained LibreSprite/
                            Aseprite project (semantics in user-data
                            chunks); strict like every export
- POST /api/import/aseprite raw project bytes -> restored matrix
- POST /api/export/spritesheet  same input -> the lab pair as JSON:
                            {png_base64, sidecar} (external-sidecar
                            strategy: the sheet and its sidecar travel
                            together)
- POST /api/import/spritesheet  {png_base64, sidecar} -> restored
                            matrix through the codec's binding checks
- POST /api/release         {name} -> release a SAVED, engine-valid
                            creature into the ecosystem (T1 wire): a
                            lineage-marked copy lands in the released
                            directory that evolution runs consume
- GET  /api/released        creatures currently released
- GET  /inspect             the genome inspector + lineage browser
- GET  /api/inspect?source=&name=  the engine-judged genome record
- GET  /api/lineage         released ancestry + evolution-run traces

Launched by `mechas workshop --editor` with the workspace interpreter.
"""

import argparse
import base64
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
    ROOT / "labs" / "workshop_editor",
]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from ca_nca_growth_repair import (  # noqa: E402
    grid_from_matrix,
    matrix_from_grid,
)
from corpus_builder import PALETTES, build_seed_grids  # noqa: E402
from animation_states import build_render_packet_v2  # noqa: E402
from slip import is_grid_aligned, validate_slip  # noqa: E402

from mecha_engine.generation import (  # noqa: E402
    generate_candidate,
    train_generation_model,
)
from mecha_engine.genome import (  # noqa: E402
    render_packet_from_grid,
    validate_grid,
)
from mecha_engine.repair import train_repair_model  # noqa: E402
from aseprite_user_data_chunk_writer import (  # noqa: E402
    export_aseprite_user_data_project,
    import_aseprite_user_data_project,
)
from png_apng_sidecar_decoder import export_apng_with_sidecar  # noqa: E402
from spritesheet_sidecar_decoder import (  # noqa: E402
    export_spritesheet_with_sidecar,
    import_spritesheet_with_sidecar,
)
from png_embedded_sidecar_writer import (  # noqa: E402
    export_png_with_embedded_sidecar,
    import_png_with_embedded_sidecar,
)
from mecha_engine.runtime import live_cycle  # noqa: E402


WORKSHOP_DIR = ROOT / "workshop"
DEFAULT_GRIDS_DIR = ROOT / "data" / "workshop" / "grids"
DEFAULT_SLIPS_DIR = ROOT / "data" / "workshop" / "slips"
DEFAULT_RELEASED_DIR = ROOT / "data" / "workshop" / "released"
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


# T9 trait editor (DR 0015 vocabulary): role -> (organ_id, organ_role).
ROLE_ORGANS = {
    "body": ("core", "body_core"),
    "anchor": ("core", "body_core"),
    "shell": ("carapace", "body_core"),
    "joint": ("joints", "locomotion"),
    "limb": ("limbs", "locomotion"),
    "eye": ("sensors", "sensor"),
    "sensor": ("antennae", "sensor"),
    "antenna": ("antennae", "sensor"),
    "mouth": ("expression", "expression"),
    "decoration": ("trim", "ornament"),
    "effect": ("aura", "effect"),
}
TRAIT_MATERIALS = {"soft", "hard", "glass", "joint", "light", "signal"}


def _apply_cell_overrides(grid: dict, overrides: dict) -> list[str]:
    """Apply per-cell trait overrides; returns problems (empty = ok).

    Presentation-side plumbing only: the ENGINE'S validator and
    alignment remain the judges of the resulting grid.
    """
    problems: list[str] = []
    cells = {(cell["x"], cell["y"]): cell for cell in grid.get("cells", [])}
    for key, patch in overrides.items():
        try:
            x, y = (int(part) for part in str(key).split(","))
        except ValueError:
            problems.append(f"bad cell key: {key}")
            continue
        cell = cells.get((x, y))
        if cell is None:
            problems.append(f"no creature cell at {x},{y}")
            continue
        if not isinstance(patch, dict):
            problems.append(f"override for {x},{y} must be an object")
            continue
        for field, value in patch.items():
            if field == "material":
                if value not in TRAIT_MATERIALS:
                    problems.append(f"unknown material at {x},{y}: {value}")
                else:
                    cell["material"] = value
            elif field == "mutation_weight":
                if (
                    isinstance(value, bool)
                    or not isinstance(value, int | float)
                    or not 0.0 <= value <= 1.0
                ):
                    problems.append(
                        f"mutation_weight at {x},{y} must be 0..1: {value}"
                    )
                else:
                    cell["mutation_weight"] = value
            elif field == "role":
                if value not in ROLE_ORGANS:
                    problems.append(f"unknown role at {x},{y}: {value}")
                else:
                    cell["role"] = value
                    cell["organ"] = ROLE_ORGANS[value][0]
                    if value != "anchor":
                        cell["animation_anchor"] = False
            else:
                problems.append(f"unknown trait field at {x},{y}: {field}")
    if problems:
        return problems
    # Rebuild the organ map from the (possibly re-roled) cells.
    organs: dict[str, dict] = {}
    for cell in grid.get("cells", []):
        organ_id = cell.get("organ")
        role = cell.get("role")
        organ_role = ROLE_ORGANS.get(role, ("core", "body_core"))[1]
        entry = organs.setdefault(
            organ_id, {"role": organ_role, "cells": [], "required": False}
        )
        entry["cells"].append([cell["x"], cell["y"]])
    if "core" in organs:
        organs["core"]["required"] = True
    if "sensors" in organs:
        organs["sensors"]["required"] = True
    grid["organs"] = organs
    return []


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
        released_dir: Path,
    ) -> None:
        self.grids_dir = grids_dir
        self.slips_dir = slips_dir
        self.released_dir = released_dir
        self.curated_profiles = _load_profiles()
        self.seed_grids = build_seed_grids()
        self.repair_model = train_repair_model(self.seed_grids)
        self.generation_model = train_generation_model(self.seed_grids)
        handler = functools.partial(_Handler, directory=str(WORKSHOP_DIR))
        super().__init__(address, handler)

    def resolve_creature(self, source: str, name: str) -> dict | None:
        if source == "seed":
            for seed in self.seed_grids:
                if seed.get("grid_id") == name:
                    return json.loads(json.dumps(seed))
            return None
        if source == "workshop":
            file = self.grids_dir / (_safe_name(name) + ".json")
            if file.exists():
                return json.loads(file.read_text(encoding="utf-8"))
        return None

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

    def _read_bytes(self) -> bytes:
        length = int(self.headers.get("Content-Length", "0"))
        return self.rfile.read(length)

    def _file(self, data: bytes, filename: str, media_type: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", media_type)
        self.send_header(
            "Content-Disposition", 'attachment; filename="' + filename + '"'
        )
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _png(self, data: bytes, filename: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.send_header(
            "Content-Disposition", 'attachment; filename="' + filename + '"'
        )
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # ------------------------------------------------------------- GET
    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?")[0]
        if path == "/":
            self.path = "/grid_editor/grid_editor.html"
            return super().do_GET()
        if path == "/inspect":
            self.path = "/inspector/inspector.html"
            return super().do_GET()
        if path.startswith("/api/inspect"):
            from urllib.parse import parse_qs, urlparse

            query = parse_qs(urlparse(self.path).query)
            source = (query.get("source") or [""])[0]
            name = (query.get("name") or [""])[0]
            grid = self.server.resolve_creature(source, name)
            if grid is None and source == "released":
                file = self.server.released_dir / (_safe_name(name) + ".json")
                if file.exists():
                    grid = json.loads(file.read_text(encoding="utf-8"))
            if grid is None:
                self._json(404, {"ok": False, "error": "no such creature"})
                return
            validation = validate_grid(grid)
            organs = {
                organ_id: {
                    "role": organ.get("role"),
                    "cell_count": len(organ.get("cells", [])),
                    "required": organ.get("required", False),
                }
                for organ_id, organ in grid.get("organs", {}).items()
            }
            self._json(
                200,
                {
                    "ok": True,
                    "grid_id": grid.get("grid_id"),
                    "palette": grid.get("palette"),
                    "validation": {
                        "ok": validation.ok,
                        "errors": list(validation.errors),
                    },
                    "stats": _morphology_stats(grid),
                    "organs": organs,
                    "lineage": grid.get("lineage", {}),
                    "mutation": grid.get("mutation", {}),
                    "metadata": grid.get("metadata", {}),
                    "cells": grid.get("cells", []),
                },
            )
            return
        if path == "/api/lineage":
            released = []
            if self.server.released_dir.exists():
                for file in sorted(self.server.released_dir.glob("*.json")):
                    if file.name.endswith(".bak.json"):
                        continue
                    grid = json.loads(file.read_text(encoding="utf-8"))
                    released.append(
                        {
                            "name": file.stem,
                            "grid_id": grid.get("grid_id"),
                            "lineage": grid.get("lineage", {}),
                        }
                    )
            evolution_runs = []
            runs_dir = ROOT / "data" / "runtime_integration"
            if runs_dir.exists():
                for file in sorted(runs_dir.glob("mecha_engine_evolution_*_stage0.json")):
                    payload = json.loads(file.read_text(encoding="utf-8"))
                    workshop = payload.get("summary", {}).get("workshop")
                    entry = {
                        "lab_id": payload.get("lab_id"),
                        "generations": payload.get("generations_requested"),
                        "archive": payload.get("summary", {}).get("archive", {}),
                    }
                    if workshop:
                        entry.update(
                            {
                                "founder_ids": workshop.get("founder_ids", []),
                                "creature_count_by_generation": workshop.get(
                                    "creature_count_by_generation", []
                                ),
                                "lineage_survived_beyond_founding": workshop.get(
                                    "lineage_survived_beyond_founding"
                                ),
                                "mean_fitness": workshop.get("mean_fitness"),
                                "corpus_mean_fitness": workshop.get(
                                    "corpus_mean_fitness"
                                ),
                            }
                        )
                    evolution_runs.append(entry)
            self._json(
                200,
                {"released": released, "evolution_runs": evolution_runs},
            )
            return
        if path == "/preview":
            self.path = "/preview/preview.html"
            return super().do_GET()
        if path == "/api/preview/creatures":
            creatures = []
            if self.server.grids_dir.exists():
                for file in sorted(self.server.grids_dir.glob("*.json")):
                    if file.name.endswith(".bak.json"):
                        continue
                    creatures.append(
                        {"source": "workshop", "name": file.stem}
                    )
            for seed in self.server.seed_grids[:12]:
                creatures.append({"source": "seed", "name": seed["grid_id"]})
            self._json(200, {"creatures": creatures})
            return
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
        if path == "/api/released":
            released = []
            if self.server.released_dir.exists():
                for file in sorted(self.server.released_dir.glob("*.json")):
                    if file.name.endswith(".bak.json"):
                        continue
                    payload = json.loads(file.read_text(encoding="utf-8"))
                    released.append(
                        {
                            "name": file.stem,
                            "grid_id": payload.get("grid_id"),
                            "palette_id": payload.get("palette", {}).get(
                                "palette_id"
                            ),
                        }
                    )
            self._json(200, {"released": released})
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
            "/api/preview/render",
            "/api/preview/live",
            "/api/preview/offspring",
            "/api/export/png",
            "/api/export/apng",
            "/api/import/png",
            "/api/export/aseprite",
            "/api/import/aseprite",
            "/api/export/spritesheet",
            "/api/import/spritesheet",
            "/api/release",
        ):
            self._json(404, {"ok": False, "error": "unknown endpoint"})
            return
        if path == "/api/import/png":
            self._import_png(self._read_bytes())
            return
        if path == "/api/import/aseprite":
            self._import_result(
                import_aseprite_user_data_project(self._read_bytes())
            )
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
        if path.startswith("/api/preview/"):
            self._preview(path.rsplit("/", 1)[-1], payload)
            return
        if path == "/api/import/spritesheet":
            self._import_spritesheet(payload)
            return
        if path == "/api/release":
            status, result = release_creature(
                self.server.grids_dir,
                self.server.released_dir,
                str(payload.get("name", "")),
            )
            self._json(status, result)
            return
        if path.startswith("/api/export/"):
            self._export(path.rsplit("/", 1)[-1], payload)
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
            overrides = payload.get("cell_overrides") or {}
            if overrides:
                problems = _apply_cell_overrides(grid, overrides)
                if problems:
                    self._json(400, {"ok": False, "errors": problems})
                    return
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
                    "grid_cells": grid.get("cells", []),
                },
            )
            return

        # /api/save — strict per the charter's 4-W pillar: the workshop
        # never writes a grid the engine would reject.
        name = _safe_name(payload.get("name", ""))
        grid = _build_grid(matrix, palette_id, f"workshop_{name}")
        overrides = payload.get("cell_overrides") or {}
        if overrides:
            problems = _apply_cell_overrides(grid, overrides)
            if problems:
                self._json(400, {"ok": False, "errors": problems})
                return
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

    def _preview(self, kind: str, payload: dict) -> None:
        grid = self.server.resolve_creature(
            str(payload.get("source", "")), str(payload.get("name", ""))
        )
        if grid is None:
            self._json(404, {"ok": False, "error": "no such creature"})
            return

        if kind == "render":
            # T16: packet v2 — the requested animation state's projected
            # visuals ride the packet (lab builder; engine validation).
            animation = payload.get("animation")
            try:
                packet = build_render_packet_v2(grid, None, animation=animation)
            except ValueError as error:
                self._json(400, {"ok": False, "error": str(error)})
                return
            self._json(200, {"ok": True, "packet": packet})
            return

        profiles = self.server.all_profiles()
        profile = profiles.get(str(payload.get("profile_id", "")))
        if profile is None:
            self._json(404, {"ok": False, "error": "no such profile"})
            return
        # Previews are the engine's answers: when the creature cannot
        # live/breed under the profile, the engine's own alignment errors
        # ARE the preview.
        alignment = is_grid_aligned(grid, profile)
        if not alignment.ok:
            self._json(
                200,
                {
                    "ok": False,
                    "errors": list(alignment.errors),
                    "reason": "this creature does not belong to that "
                    "profile, so the engine will not run it there",
                },
            )
            return

        if kind == "live":
            cycles = max(1, min(5, int(payload.get("cycles", 3))))
            ticks = max(8, min(96, int(payload.get("ticks", 48))))
            report = live_cycle(
                grid,
                profile,
                self.server.repair_model,
                damage_cycles=cycles,
                ticks=ticks,
                rng_seed=int(payload.get("rng_seed", 20260512)),
            )
            self._json(
                200,
                {
                    "ok": True,
                    "report": report,
                    "before": {"packet": render_packet_from_grid(grid)},
                    "after": {
                        "packet": render_packet_from_grid(
                            report["final_grid"]
                        )
                    },
                },
            )
            return

        if kind == "offspring":
            count = max(1, min(8, int(payload.get("count", 4))))
            rng_seed = int(payload.get("rng_seed", 20260512))
            children = []
            for index in range(count):
                child = generate_candidate(
                    grid,
                    self.server.generation_model,
                    profile,
                    rng_seed=rng_seed + index,
                )
                children.append(
                    {
                        "grid_id": child["grid_id"],
                        "valid": validate_grid(child).ok,
                        "aligned": is_grid_aligned(child, profile).ok,
                        "packet": render_packet_from_grid(child),
                    }
                )
            self._json(200, {"ok": True, "children": children})
            return

        self._json(404, {"ok": False, "error": "unknown preview"})

    def _export(self, kind: str, payload: dict) -> None:
        """Strict per the 4-W pillar: exports carry the engine's word."""
        matrix = payload.get("matrix")
        problem = _check_matrix(matrix)
        if problem:
            self._json(400, {"ok": False, "errors": [problem]})
            return
        palette_id = payload.get("palette_id", "lcd_green")
        if palette_id not in PALETTES:
            self._json(400, {"ok": False, "errors": ["unknown palette"]})
            return
        profile = self.server.all_profiles().get(
            str(payload.get("profile_id", ""))
        )
        if profile is None:
            self._json(400, {"ok": False, "errors": ["no such profile"]})
            return
        grid_id = _safe_name(payload.get("name") or "workshop_export")
        grid = _build_grid(matrix, palette_id, "workshop_" + grid_id)
        validation = validate_grid(grid)
        if not validation.ok:
            self._json(400, {"ok": False, "errors": list(validation.errors)})
            return
        alignment = is_grid_aligned(grid, profile)
        if not alignment.ok:
            self._json(400, {"ok": False, "errors": list(alignment.errors)})
            return
        if kind == "png":
            exported = export_png_with_embedded_sidecar(grid, profile)
            self._png(exported["embedded_png_bytes"], grid_id + ".png")
            return
        if kind == "apng":
            exported = export_apng_with_sidecar(grid, profile)
            self._png(exported["png_bytes"], grid_id + ".apng.png")
            return
        if kind == "aseprite":
            exported = export_aseprite_user_data_project(grid, profile)
            self._file(
                exported["project_bytes"],
                grid_id + ".aseprite",
                "application/octet-stream",
            )
            return
        if kind == "spritesheet":
            exported = export_spritesheet_with_sidecar(grid, profile)
            self._json(
                200,
                {
                    "ok": True,
                    "png_base64": base64.b64encode(
                        exported["png_bytes"]
                    ).decode("ascii"),
                    "sidecar": exported["sidecar"],
                    "filename": grid_id + ".spritesheet.png",
                    "sidecar_filename": grid_id + ".spritesheet.sidecar.json",
                },
            )
            return
        self._json(404, {"ok": False, "errors": ["unknown export"]})

    def _import_png(self, data: bytes) -> None:
        self._import_result(import_png_with_embedded_sidecar(data))

    def _import_spritesheet(self, payload: dict) -> None:
        sidecar = payload.get("sidecar")
        try:
            png_bytes = base64.b64decode(str(payload.get("png_base64", "")))
        except Exception:
            png_bytes = b""
        if not png_bytes or not isinstance(sidecar, dict):
            self._json(
                400,
                {
                    "ok": False,
                    "errors": [
                        "a spritesheet travels as a pair: the sheet PNG "
                        "and its sidecar JSON are both required"
                    ],
                },
            )
            return
        self._import_result(
            import_spritesheet_with_sidecar(png_bytes, sidecar)
        )

    def _import_result(self, result: dict) -> None:
        """Permissive on import: the codec's own failure families come
        back verbatim; nothing is written."""
        if not result.get("ok"):
            errors = result.get("errors") or [
                str(result.get("error", "the codec rejected this file"))
            ]
            self._json(
                400,
                {
                    "ok": False,
                    "errors": [str(error) for error in errors],
                    "families": result.get("error_families", []),
                },
            )
            return
        restored = result["restored_grid"]
        self._json(
            200,
            {
                "ok": True,
                "matrix": matrix_from_grid(restored),
                "palette_id": restored.get("palette", {}).get("palette_id"),
                "grid_id": restored.get("grid_id"),
                "engine_valid": validate_grid(restored).ok,
            },
        )


def release_creature(
    grids_dir: Path, released_dir: Path, name: str
) -> tuple[int, dict]:
    """Release a saved creature into the ecosystem (T1 wire).

    Strict per the 4-W pillar: the creature must exist as a saved draft
    and pass the engine's validator again at release time. The release
    is a lineage-marked COPY (`released_into_ecosystem` mutation event) —
    the draft stays editable; the released copy is what evolution runs
    consume. Backup-before-overwrite on re-release.
    """
    source = grids_dir / (_safe_name(name) + ".json")
    if not source.exists():
        return 404, {
            "ok": False,
            "error": "no saved creature by that name — save it first",
        }
    grid = json.loads(source.read_text(encoding="utf-8"))
    validation = validate_grid(grid)
    if not validation.ok:
        return 400, {
            "ok": False,
            "error": "the engine rejects this creature; fix it first",
            "errors": list(validation.errors),
        }
    events = grid.setdefault("lineage", {}).setdefault(
        "mutation_events", []
    )
    if "released_into_ecosystem" not in events:
        events.append("released_into_ecosystem")
    released_dir.mkdir(parents=True, exist_ok=True)
    target = released_dir / source.name
    backup = None
    if target.exists():
        stamp = time.strftime("%Y%m%d-%H%M%S")
        backup = target.with_name(f"{target.stem}.{stamp}.bak.json")
        backup.write_bytes(target.read_bytes())
    target.write_text(json.dumps(grid, indent=2) + "\n", encoding="utf-8")
    return 200, {
        "ok": True,
        "file": target.name,
        "backup": backup.name if backup else None,
    }


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
    released_dir: Path = DEFAULT_RELEASED_DIR,
) -> WorkshopServer:
    server = WorkshopServer(
        ("127.0.0.1", port), grids_dir, slips_dir, released_dir
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def main() -> None:
    parser = argparse.ArgumentParser(description="mecha_workshop server")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--grids-dir", type=Path, default=DEFAULT_GRIDS_DIR)
    parser.add_argument(
        "--release",
        type=str,
        default=None,
        help="One-shot: release a saved creature into the ecosystem, "
        "print the JSON result, exit.",
    )
    args = parser.parse_args()
    if args.release is not None:
        status, result = release_creature(
            args.grids_dir, DEFAULT_RELEASED_DIR, args.release
        )
        print(json.dumps(result))
        raise SystemExit(0 if status == 200 else 1)
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
