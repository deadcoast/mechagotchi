"""The mecha_workshop local server — the engine answers, the page asks.

Serves the grid editor and exposes the local API the charter's 4-W pillar
requires: validation is the ENGINE'S verdict (`mecha_engine.genome
.validate_grid`), SLIP judgment is the PROMOTED authority
(`mecha_engine.slip.is_grid_aligned`/`validate_slip` — the switch this
docstring long promised, fulfilled by DR 0027/F2 when the tenth module
landed), grid construction is the
canonical matrix->grid builder the research proved, and the structural
load shown to creators is the archive's contracted stress-probe formula.
The workshop layer may import both the package and the labs (it is
application content, not package code); nothing here reimplements a
validator that could drift.

X2 authoring requests may instead carry a complete
``document={format: "mecha_workshop_document_v1", grid, profile?, layers?}``
and ``draft_revision``. The same document drives validation, preview, save,
export and inline release. JSON responses identify the document and revision;
binary exports carry equivalent headers. Modern saves compare
``expected_disk_revision`` against the grid plus authoring-sidecar bytes;
releases compare ``expected_release_revision`` before a preserved overwrite.
Legacy requests and absent-arm codec outputs remain supported.

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
- POST /api/preview/clip    {source, name, clip, profile_id?} -> every
                            frame of the clip through the promoted
                            packet rung (C4: the documented animation
                            block clip/frame_index/frame_count/anchors).
                            H3: also accepts an inline UNSAVED draft —
                            {matrix, palette_id?, cell_overrides?, clip}
                            — judged by the engine before any frame
- POST /api/preview/live    {source, name, profile_id, cycles, ticks} ->
                            runtime.live_cycle: damage/repair/episode
                            truth plus before/after packets
- POST /api/preview/offspring  {source, name, profile_id, count} ->
                            engine-generated children (or the engine's
                            alignment errors when the parent cannot
                            breed under the profile)
- POST /api/preview/replay  {source, name, profile_id, cycles, ticks,
                            rng_seed?} -> a replay artifact (R5, DR
                            0023): the creature's whole live_cycle as
                            recorded engine truth — birth/wound/repair
                            packets plus every episode tick — for the
                            scrubber. Engine truth, recorded.
- POST /api/export/png      {matrix, palette_id, profile_id} -> a
                            self-contained PNG (embedded sidecar) via
                            the proven lab codec; strict on validity
                            and profile alignment
- POST /api/export/apng     same input -> the lab's animated APNG
                            (base + pulse frames); visual artifact.
                            H3: + optional clip -> the engine's clip
                            frames instead of the pulse (additive rung;
                            spritesheet takes clip the same way)
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
- GET  /session             the Keeper's session page (G4, DR 0021)
- GET  /api/session/state   the persistent keeper session's read model
- GET  /api/covenant/budget the active campaign's earned covenant caps
  (K5, DR 0044: read-only, the session lab's own read model; an absent
  session answers available:false honestly — advisory, never authority)
                            (campaign digests, unlock state, forecasts)
- POST /api/session/new     {campaign_id?, base_seed?} -> start a
                            keeper session (409 if one exists)
- POST /api/session/era     {weather} -> advance the active campaign by
                            one era (the promoted evolve run), persist
                            state + DR 0022 ledger, return the turn
- POST /api/session/covenant  {allowed_palettes?, deliberation_max_
                            ticks?, population?, generations?} ->
                            the Covenant step (C4): adjust within the
                            EARNED budget, authority-validated;
                            over-budget = named violations (400)
- GET  /api/session/replay?campaign=&era=  a stored era replay (C5):
                            the era's best elite's RECORDED life, served
                            from the ledger's replays directory
- GET  /inspect             the genome inspector + lineage browser
- GET  /api/inspect?source=&name=  the engine-judged genome record
- GET  /api/lineage         released ancestry + evolution-run traces
- GET  /api/metrics         T10 session instrumentation (og workshop
                            metrics: validations, invalid verdicts,
                            per-error counts, saves/releases/exports/
                            imports; authoring-time proxy via
                            timestamps). Instrumented pipeline only —
                            human-study DATA comes from humans.
- POST /api/metrics/flush   persist the session record

Launched by `mechas workshop --editor` with the workspace interpreter.
"""

import argparse
from copy import deepcopy
from contextlib import contextmanager, nullcontext
import base64
import functools
import json
import re
import socket
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import authoring as authoring_docs
import drafts as draft_store


ROOT = Path(__file__).resolve().parents[2]
import sys  # noqa: E402

for path in [
    ROOT / "packages" / "mecha_engine" / "src",
    ROOT / "game" / "src",
    ROOT / "labs" / "grid_genome",
    ROOT / "labs" / "cellular_automata",
    ROOT / "labs" / "workshop_editor",
    ROOT / "labs" / "game_loop",
]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from ca_nca_growth_repair import (  # noqa: E402
    grid_from_matrix,
    matrix_from_grid,
)
from corpus_builder import (  # noqa: E402
    PALETTES,
    build_seed_grids,
    build_seed_grids_16,
)

from mecha_engine.generation import (  # noqa: E402
    generate_candidate,
    train_generation_model,
)
from mecha_engine.genome import (  # noqa: E402
    clip_frame_count,
    clip_names,
    render_packet_from_grid,
    render_packet_v2,
    validate_grid,
)
from mecha_engine.repair import train_repair_model  # noqa: E402
from mecha_engine.slip import is_grid_aligned, validate_slip  # noqa: E402
from aseprite_user_data_chunk_writer import (  # noqa: E402
    export_aseprite_user_data_project,
    import_aseprite_user_data_project,
    extract_aseprite_user_data_sidecar,
)
from png_apng_sidecar_decoder import (  # noqa: E402
    export_apng_with_sidecar,
    import_apng_with_sidecar,
)
from spritesheet_sidecar_decoder import (  # noqa: E402
    export_spritesheet_with_sidecar,
    import_spritesheet_with_sidecar,
)
from png_embedded_sidecar_writer import (  # noqa: E402
    export_png_with_embedded_sidecar,
    import_png_with_embedded_sidecar,
    extract_embedded_sidecar_from_png,
    embed_sidecar_in_png_text_chunk,
)
from mecha_engine.runtime import live_cycle  # noqa: E402
from mecha_game.replay import build_replay  # noqa: E402
from companion import (  # noqa: E402
    adopt_companion,
    autonomous_tick,
    companion_snapshot,
    load_companion,
    player_act,
    save_companion,
)
from session_runner import (  # noqa: E402
    WEATHER_NAMES,
    advance_keeper_state,
    apply_covenant_change,
    keeper_state_summary,
    load_keeper_state,
    new_keeper_state,
    save_keeper_state,
    session_scale,
    state_covenant_budget,
    train_legibility_model,
)


WORKSHOP_DIR = ROOT / "workshop"
DEFAULT_GRIDS_DIR = ROOT / "data" / "workshop" / "grids"
DEFAULT_SLIPS_DIR = ROOT / "data" / "workshop" / "slips"
DEFAULT_RELEASED_DIR = ROOT / "data" / "workshop" / "released"
DEFAULT_METRICS_DIR = ROOT / "data" / "workshop" / "metrics"
# Keeper play state lives in its own subdirectory so a live session
# never overwrites the committed game_loop stage-0 evidence artifacts.
DEFAULT_SESSION_DIR = ROOT / "data" / "game_loop" / "keeper"
SLIP_VALID_DIR = ROOT / "data" / "slips" / "valid"
TOKENS = authoring_docs.TOKENS
# DR 0029 (cycle 09 A2): the canvas is size-parametric across the two
# ratified scales — 8x8 (Stage 0) and 16x16 (the proven default target).
ALLOWED_GRID_SIZES = (8, 16)


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
        or len(matrix) not in ALLOWED_GRID_SIZES
        or any(
            not isinstance(row, list) or len(row) != len(matrix)
            for row in matrix
        )
    ):
        allowed = " or ".join(f"{size}x{size}" for size in ALLOWED_GRID_SIZES)
        return f"matrix must be {allowed}"
    bad = sorted({str(token) for row in matrix for token in row
                  if not isinstance(token, str) or token not in TOKENS})
    if bad:
        return f"unknown tokens: {', '.join(map(str, bad))}"
    return None


def _morphology_stats(grid: dict) -> dict:
    """Morphology stats incl. the archive's contracted stress-probe load.

    Formula mirrored verbatim from
    ``mecha_engine.archive._metrics.lifecycle_probe_grid``:
    load = clamp(body_mass/(w*h/4) + (1 - symmetry) * 0.65
    - sensors * 0.08). The mass denominator is size-parametric since
    cycle 09 A3 (16 at 8x8, 64 at 16x16 — measured in the
    stress_probe_scaling lab; the shipped /16 measured as a total
    survival-axis collapse at 16x16). ``collapse_risk`` marks the
    lifecycle's documented bistability boundary (stress >= 0.95
    collapses around tick 12-14).
    """
    cells = grid.get("cells", [])
    body_mass = sum(1 for cell in cells if cell.get("organ") == "core")
    sensors = grid.get("organs", {}).get("sensors", {}).get("cells", [])
    sensor_count = len(sensors) if isinstance(sensors, list) else 0
    grid_size = grid.get("grid_size", [8, 8])
    width = grid_size[0] if isinstance(grid_size, list) and grid_size else 8
    occupied = {
        (cell["x"], cell["y"], cell.get("role")) for cell in cells
    }
    symmetry = (
        sum(
            1
            for x, y, role in occupied
            if (width - 1 - x, y, role) in occupied
        )
        / len(occupied)
        if occupied
        else 0.0
    )
    height = grid_size[1] if isinstance(grid_size, list) and len(grid_size) > 1 else 8
    mass_denominator = max(1, (width * height) // 4)
    load = max(
        0.0,
        min(
            1.0,
            body_mass / mass_denominator
            + (1 - symmetry) * 0.65
            - sensor_count * 0.08,
        ),
    )
    return {
        "body_mass": body_mass,
        "sensor_count": sensor_count,
        "symmetry": round(symmetry, 6),
        "stress_load": round(load, 6),
        "collapse_risk": load >= 0.95,
        "cell_count": len(cells),
    }


# H2 (cycle 18): the semantic strata, in merge-precedence order. The
# layer model is AUTHORING STATE riding a sidecar; the saved grid
# stays the engine's single source of truth, and the server verifies
# the honesty claim — the layers must MERGE to the posted matrix.
LAYER_STRATA = ("body", "organs", "decoration", "effects")


def _merge_layers(layers: list[dict]) -> tuple[list[list[str]] | None, str | None]:
    """Merge the four strata (last non-empty token wins) or name the
    shape problem."""
    try:
        return authoring_docs.merge_layers(layers), None
    except ValueError as error:
        return None, str(error)


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


class _ContextRefused(Exception):
    """The HTTP refusal has already been sent; stop before publication."""


class WorkshopServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False

    def __init__(
        self,
        address: tuple[str, int],
        grids_dir: Path,
        slips_dir: Path,
        released_dir: Path,
        metrics_dir: Path,
        session_dir: Path | None = None,
        keeper_dir: Path | None = None,
    ) -> None:
        self.keeper_dir = Path(keeper_dir).resolve() if keeper_dir is not None else None
        if self.keeper_dir is not None:
            project = self.keeper_dir / "workshop"
            grids_dir, slips_dir, metrics_dir = project/"grids", project/"slips", project/"metrics"
            released_dir = self.keeper_dir/"released"
        self.drafts_dir = Path(grids_dir).parent/"drafts"
        self.grids_dir = grids_dir
        self.authoring_lock = threading.RLock()
        self.slips_dir = slips_dir
        self.released_dir = released_dir
        self.metrics_dir = metrics_dir
        # G4 (DR 0021): the Keeper's persistent session (JSON interim).
        session_dir = session_dir or DEFAULT_SESSION_DIR
        self.session_state_path = session_dir / "keeper_session.json"
        # C3 (DR 0022): the derived ledger is the promoted storage
        # module's SQLite file.
        self.session_ledger_path = session_dir / "campaign_ledger.sqlite"
        # W1: the living companion's play state.
        self.companion_path = session_dir / "companion.json"
        self._legibility_model: dict | None = None
        self._session_repair_models: dict[tuple[int, int], dict] = {}
        self.session_metrics = {
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "validations": 0,
            "invalid_verdicts": 0,
            "validator_error_counts": {},
            "saves": 0,
            "releases": 0,
            "exports": 0,
            "imports": 0,
            "first_valid_at": None,
        }
        self.curated_profiles = _load_profiles()
        # Both ratified corpora (DR 0029): 8x8 keeps every historical
        # surface; 16x16 is the default scale for new sessions. Models
        # are per-scale (generation and repair both derive their layout
        # from their corpus since A3). Browser-lab 8x8 stays eager; native
        # context and 16x16 train only when a model-backed preview needs them.
        self.seed_grids = build_seed_grids()
        self.seed_grids_16 = build_seed_grids_16()
        self._models_lock = threading.RLock()
        self._models_by_scale: dict[int, tuple] = {}
        self.repair_model = self.generation_model = None
        if self.keeper_dir is None:
            # Preserve the established browser-lab eager models exactly. Native
            # context inspection does not need training before its window opens.
            self.repair_model = train_repair_model(self.seed_grids)
            self.generation_model = train_generation_model(self.seed_grids)
            self._models_by_scale[8] = (self.generation_model,self.repair_model)
        handler = functools.partial(_Handler, directory=str(WORKSHOP_DIR))
        super().__init__(address, handler)

    @contextmanager
    def mutation_lock(self):
        from mecha_game.compatibility import keeper_write_lock
        with self.authoring_lock:
            with keeper_write_lock(self.keeper_dir) if self.keeper_dir is not None else nullcontext():
                yield

    def selected_context(self):
        from mecha_game.keeper_context import context_id, read_keeper
        if self.keeper_dir is not None:
            result=read_keeper(self.keeper_dir)
            if result['context']['available']:
                for file, grid in authoring_docs.grid_files(self.grids_dir):
                    try: doc,revision=authoring_docs.load_document(file)
                    except (OSError,ValueError): continue
                    result['creatures'].append(dict(ref=dict(source='workshop',name=file.stem,disk_revision=revision),label=file.stem,
                        source='workshop',grid_id=grid['grid_id'],document=doc,document_digest=authoring_docs.digest(doc),disk_revision=revision))
            return result
        identity = context_id(self.grids_dir.parent, 'browser_lab')
        result = {'context': dict(kind='browser_lab',context_id=identity,context_revision=identity,
            available=True,reason='Browser lab history is separate from native Keeper saves.',
            keeper_dir=None,keeper_id=None,campaign_id=None,covenant=None,budget=None,
            body_response='legacy',body_response_source='standalone_legacy',
            capabilities=dict(authoring=True,release=True,pack_import=False,lab_session=True)),
            'creatures':[], 'lineage':{'campaigns':[],'lives':[]}}
        for grid in [*self.seed_grids_16,*self.seed_grids]:
            doc=dict(format=authoring_docs.FORMAT,grid=deepcopy(grid))
            result['creatures'].append(dict(ref=dict(source='seed',grid_id=grid['grid_id']),label=grid['grid_id'],source='seed',
                grid_id=grid['grid_id'],document=doc,document_digest=authoring_docs.digest(doc)))
        for source,folder in (('workshop',self.grids_dir),('released',self.released_dir)):
            for file,grid in authoring_docs.grid_files(folder):
                try: doc,revision=authoring_docs.load_document(file)
                except (OSError,ValueError): continue
                result['creatures'].append(dict(ref=dict(source=source,name=file.stem,disk_revision=revision),label=file.stem,source=source,
                    grid_id=grid['grid_id'],document=doc,document_digest=authoring_docs.digest(doc),disk_revision=revision))
        return result

    def close_workshop(self):
        """Owned foreground lifetime; compatible with shutdown/server_close callers."""
        self.shutdown()
        self.server_close()
        thread = getattr(self, 'workshop_thread', None)
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=5)

    def seeds_for_scale(self, scale: int) -> list[dict]:
        return self.seed_grids if scale == 8 else self.seed_grids_16

    def models_for(self, grid: dict) -> tuple:
        """(generation_model, repair_model) matching the grid's scale."""
        grid_size = grid.get("grid_size", [8, 8])
        scale = grid_size[0] if isinstance(grid_size, list) and grid_size else 8
        with self._models_lock:
            if scale not in self._models_by_scale:
                seeds = self.seeds_for_scale(scale)
                # The historical 8x8 eager arm uses the complete corpus. Keep
                # that input and the 16x16 first-40 policy unchanged when lazy.
                if scale == 8:
                    repair = train_repair_model(seeds)
                    generation = train_generation_model(seeds)
                else:
                    generation = train_generation_model(seeds)
                    repair = train_repair_model(seeds[:40])
                self._models_by_scale[scale] = (generation,repair)
                if scale == 8:
                    self.generation_model,self.repair_model = generation,repair
            return self._models_by_scale[scale]

    def legibility_model(self) -> dict:
        if self._legibility_model is None:
            self._legibility_model = train_legibility_model()
        return self._legibility_model

    def session_repair_model(
        self, epochs: int, rng_seed: int, scale: int = 16
    ) -> dict:
        key = (epochs, rng_seed, scale)
        if key not in self._session_repair_models:
            self._session_repair_models[key] = train_repair_model(
                self.seeds_for_scale(scale)[:40],
                epochs=epochs,
                rng_seed=rng_seed,
            )
        return self._session_repair_models[key]

    def resolve_creature(self, source: str, name: str) -> dict | None:
        if source == "seed":
            for seed in [*self.seed_grids_16, *self.seed_grids]:
                if seed.get("grid_id") == name:
                    return json.loads(json.dumps(seed))
            return None
        if source == "workshop":
            file = self.grids_dir / (_safe_name(name) + ".json")
            for candidate, grid in authoring_docs.grid_files(self.grids_dir):
                if candidate == file:
                    return grid
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
        payload = {**getattr(self, '_response_context', {}), **payload}
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
        self._revision_headers()
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _png(self, data: bytes, filename: str) -> None:
        self._file(data, filename, 'image/png')

    def _revision_headers(self) -> None:
        context = getattr(self, '_response_context', {})
        if context.get('draft_revision') is not None:
            self.send_header('X-Workshop-Draft-Revision', str(context['draft_revision']))
        if context.get('pack_digest'):
            self.send_header('X-Workshop-Pack-Digest', context['pack_digest'])
        if context.get('document_digest'):
            self.send_header('X-Workshop-Document-Digest', context['document_digest'])

    def _bind_document(self, document: dict, payload: dict | None = None) -> dict:
        revision = getattr(self, '_response_context', {}).get('draft_revision')
        self._response_context = {'document': document,
            'document_digest': authoring_docs.digest(document)}
        if payload is not None and 'draft_revision' in payload:
            revision = payload['draft_revision']
        if revision is not None:
            self._response_context['draft_revision'] = revision
        return document

    def _request_document(self, payload: dict, *, grid_id: str = 'workshop_draft',
                          profile_only: bool = False) -> dict | None:
        try:
            if 'document' in payload:
                doc = authoring_docs.document(payload['document'],
                    require_grid=not profile_only, require_profile=profile_only)
            elif profile_only:
                doc = authoring_docs.document({'format': authoring_docs.FORMAT,
                    'profile': payload.get('profile')}, require_profile=True)
            else:
                matrix = payload.get('matrix')
                problem = _check_matrix(matrix)
                if problem:
                    raise ValueError(problem)
                palette_id = payload.get('palette_id', 'lcd_green')
                if palette_id not in PALETTES:
                    raise ValueError('unknown palette')
                grid = _build_grid(matrix, palette_id, grid_id)
                overrides = payload.get('cell_overrides') or {}
                if not isinstance(overrides, dict):
                    raise ValueError('cell_overrides must be an object')
                if overrides:
                    errors = _apply_cell_overrides(grid, overrides)
                    if errors:
                        raise ValueError('; '.join(errors))
                doc = {'format': authoring_docs.FORMAT, 'grid': grid}
                if payload.get('layers') is not None:
                    # Legacy layers describe the posted token canvas. Rich
                    # trait changes are projected only in the modern document.
                    layers = payload['layers']
                    if authoring_docs.merge_layers(layers) != matrix:
                        raise ValueError('layers do not merge to the posted matrix - the sidecar may not lie about the grid')
                    doc['layers'] = deepcopy(layers)
            return self._bind_document(doc, payload)
        except (ValueError, TypeError) as error:
            self._json(400, {'ok': False, 'error': str(error), 'errors': [str(error)]})
            return None

    def _profile_for(self, payload: dict, doc: dict | None = None) -> dict | None:
        if doc is not None and 'profile' in doc:
            return doc['profile']
        return self.server.all_profiles().get(str(payload.get('profile_id', '')))

    def _profile_errors(self, doc: dict) -> list[str]:
        if 'profile' not in doc:
            return []
        try:
            return list(validate_slip(doc['profile']).errors)
        except (TypeError, ValueError, KeyError, AttributeError) as error:
            return ['malformed profile: ' + str(error)]

    def _grid_errors(self, doc: dict) -> list[str]:
        try:
            errors = list(validate_grid(doc['grid']).errors)
            errors.extend(self._profile_errors(doc))
            return errors
        except (TypeError, ValueError, KeyError, AttributeError) as error:
            return ['malformed semantic document: ' + str(error)]

    def _conflict(self, payload: dict, key: str, current: str | None) -> bool:
        if ((current is not None and key not in payload) or
                (key in payload and payload[key] != current)):
            self._json(409, {'ok': False, 'error': 'file changed or already exists; review it before replacing',
                             'current_revision': current})
            return True
        return False

    # ------------------------------------------------------------- GET
    def _context_guard(self, payload, capability='authoring'):
        context = self.server.selected_context()['context']
        if self.server.keeper_dir is None:
            self._response_context.update(context_id=context['context_id'],context_revision=context['context_revision'])
            return context
        if (payload.get('context_id') != context['context_id'] or
                payload.get('expected_context_revision') != context['context_revision']):
            self._json(409,dict(ok=False,error='Selected Keeper context changed; refresh before writing.',
                error_code='context_changed',context=context,current_context_revision=context['context_revision']))
            return None
        if not (context['available'] if capability=='inspection' else context['capabilities'].get(capability)):
            self._json(409,dict(ok=False,error=context['reason'] or 'Selected Keeper context is unavailable.',
                error_code='context_unavailable',context=context,current_context_revision=context['context_revision']))
            return None
        if capability!='inspection':
            from mecha_game.compatibility import require_keeper_writable
            try: require_keeper_writable(self.server.keeper_dir)
            except ValueError as error:
                self._json(409,dict(ok=False,error=str(error),error_code='context_unavailable',context=context,
                    current_context_revision=context['context_revision']))
                return None
        self._response_context.update(context_id=context['context_id'],context_revision=context['context_revision'])
        return context

    def _require_write_context(self,payload,capability='authoring'):
        if self._context_guard(payload,capability) is None:
            raise _ContextRefused()

    def _x3_get(self, path):
        from urllib.parse import parse_qs, urlparse
        if path == '/packs':
            self.path='/packs/packs.html'; super().do_GET(); return True
        if self.server.keeper_dir is not None and path in ('/api/session/state','/api/session/replay','/api/companion'):
            self._json(403,dict(ok=False,error='Lab history is separate. Use the native Keeper application for care and eras.')); return True
        relevant = path.startswith('/api/context') or path.startswith('/api/drafts/') or (
            self.server.keeper_dir is not None and path in ('/api/covenant/budget','/api/lineage'))
        if not relevant: return False
        with self.server.authoring_lock:
            selected=self.server.selected_context(); context=selected['context']
            self._response_context.update(context_id=context['context_id'],context_revision=context['context_revision'])
            if path == '/api/context': self._json(200,dict(ok=True,**context))
            elif path == '/api/covenant/budget':
                self._json(200,dict(ok=True,**context,active_campaign_id=context['campaign_id']))
            elif path == '/api/context/creatures':
                self._json(200,dict(ok=True,available=context['available'],reason=context['reason'],
                    creatures=[{key:value for key,value in row.items() if key!='document'} for row in selected['creatures']],
                    release_errors=selected.get('release_errors',[])))
            elif path in ('/api/context/lineage','/api/lineage'):
                self._json(200,dict(ok=True,available=context['available'],reason=context['reason'],**selected['lineage']))
            elif path.startswith('/api/drafts/'):
                slot=parse_qs(urlparse(self.path).query).get('slot',['current'])[0]
                try: body=draft_store.read(self.server.drafts_dir,path.rsplit('/',1)[-1],context['context_id'],slot=slot)
                except draft_store.DraftError as error: self._json(error.status,error.body)
                else: self._json(200,body)
            else: self._json(404,dict(ok=False,error='Unknown context endpoint.'))
        return True

    def _x3_post(self,path,payload):
        if path == '/api/context/document':
            with self.server.authoring_lock:
                context=self._context_guard(payload,'inspection')
                if context is None: return
                selected=self.server.selected_context()
                if selected['context']['context_revision']!=context['context_revision']:
                    self._context_guard(payload,'inspection'); return
                row=next((row for row in selected['creatures'] if row['ref']==payload.get('ref')),None)
                if row is None: self._json(404,dict(ok=False,error='This selected creature is no longer available. Refresh the context.'))
                else: self._json(200,dict(ok=True,**row))
            return
        if path.startswith('/api/drafts/'):
            with self.server.mutation_lock():
                context=self._context_guard(payload)
                if context is None: return
                try: result=draft_store.write(self.server.drafts_dir,path.rsplit('/',1)[-1],context['context_id'],payload,
                    before_write=lambda:self._require_write_context(payload))
                except draft_store.DraftError as error: self._json(error.status,error.body)
                else: self._json(200,result)
            return
        from mecha_game.packs import build_pack, preview_pack, export_pack_bytes, import_pack_document, pack_digest
        action=path.rsplit('/',1)[-1]
        with self.server.mutation_lock() if action=='import' else self.server.authoring_lock:
            context=self._context_guard(payload, 'pack_import' if action=='import' else 'inspection')
            if context is None: return
            if action=='import' and self.server.keeper_dir is None:
                self._json(403,dict(ok=False,error='Select a native Keeper explicitly before importing a pack.')); return
            if action in ('build','export'):
                pack=build_pack(**{key:payload[key] for key in ('pack_id','title','provenance','slips','creatures')})
            else: pack=payload['pack']
            if action=='export':
                data=export_pack_bytes(pack)
                self._response_context['pack_digest']=pack_digest(pack)
                self._file(data,'mechagotchi-pack_'+_safe_name(pack['pack_id'])+'.json','application/json')
                return
            if action=='import':
                report=import_pack_document(self.server.keeper_dir,pack,expected_pack_digest=payload.get('expected_pack_digest'),
                    before_write=lambda:self._require_write_context(payload,'pack_import'))
            else: report=preview_pack(None if action=='build' else self.server.keeper_dir,pack)
            if not report.get('ok'):
                status=409 if action=='import' and payload.get('expected_pack_digest')!=report.get('pack_digest') else 400
                self._json(status,dict(report,error='; '.join(report.get('violations',[])) or 'Pack request refused.',error_code='pack_refused'))
                return
            if context.get('covenant') is not None:
                for entry in report.get('creatures',[]):
                    if entry.get('ok'):
                        item=pack['creatures'][entry['index']]
                        verdict=is_grid_aligned(item,context['covenant'])
                        entry['compatibility']=dict(scope='active_covenant_alignment',ok=verdict.ok,errors=list(verdict.errors),
                            notice='Staging is not admission; the native era engine makes the final decision.')
            self._json(200,dict(report,**({'pack':pack} if action=='build' else {})))

    def do_GET(self) -> None:  # noqa: N802
        self._response_context = {}
        path = self.path.split("?")[0]
        try:
            if self._x3_get(path): return
        except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
            self._json(400,dict(ok=False,error=str(error))); return
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
        if path == "/api/metrics":
            self._json(200, {"session": self.server.session_metrics})
            return
        if path == "/api/lineage":
            released = []
            if self.server.released_dir.exists():
                for file, grid in authoring_docs.grid_files(self.server.released_dir):
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
                for file, _grid in authoring_docs.grid_files(self.server.grids_dir):
                    creatures.append(
                        {"source": "workshop", "name": file.stem}
                    )
            # The ratified 16x16 corpus leads (DR 0029); a slice of the
            # 8x8 Stage 0 seeds stays offered.
            for seed in self.server.seed_grids_16[:12]:
                creatures.append({"source": "seed", "name": seed["grid_id"]})
            for seed in self.server.seed_grids[:12]:
                creatures.append({"source": "seed", "name": seed["grid_id"]})
            self._json(200, {"creatures": creatures})
            return
        if path == "/slip":
            self.path = "/slip_creator/slip_creator.html"
            return super().do_GET()
        if path == "/session":
            self.path = "/session/session.html"
            return super().do_GET()
        if path == "/companion":
            self.path = "/companion/companion.html"
            return super().do_GET()
        if path == "/api/companion":
            companion = load_companion(self.server.companion_path)
            if companion is None:
                self._json(200, {"ok": True, "exists": False})
                return
            self._json(
                200,
                {"ok": True, "exists": True, **companion_snapshot(companion)},
            )
            return
        if path == "/api/session/replay":
            # C5: serve a stored era replay (recorded engine truth) from
            # the ledger's replays directory.
            from urllib.parse import parse_qs, urlparse

            query = parse_qs(urlparse(self.path).query)
            campaign = _safe_name(str(query.get("campaign", [""])[0]))
            try:
                era_index = int(query.get("era", ["-1"])[0])
            except ValueError:
                era_index = -1
            replay_path = (
                self.server.session_ledger_path.parent
                / "replays"
                / f"{campaign}_era{era_index:03d}.json"
            )
            if era_index < 0 or not replay_path.exists():
                self._json(404, {"ok": False, "error": "no such replay"})
                return
            self._json(
                200,
                {
                    "ok": True,
                    "replay": json.loads(
                        replay_path.read_text(encoding="utf-8")
                    ),
                },
            )
            return
        if path == "/api/covenant/budget":
            # K5 (DR 0044): the earned budget's authoring-face read —
            # READ-ONLY, the session lab's own read model verbatim; an
            # absent session answers honestly, never fabricates.
            state = load_keeper_state(self.server.session_state_path)
            if state is None:
                self._json(
                    200,
                    {
                        "ok": True,
                        "available": False,
                        "reason": (
                            "no keeper session near this project — "
                            "the advisory shows earned caps only when "
                            "a campaign exists"
                        ),
                    },
                )
                return
            self._json(
                200,
                {
                    "ok": True,
                    "available": True,
                    "active_campaign_id": state["active_campaign_id"],
                    "budget": state_covenant_budget(state),
                },
            )
            return
        if path == "/api/session/state":
            state = load_keeper_state(self.server.session_state_path)
            if state is None:
                self._json(
                    200,
                    {
                        "ok": True,
                        "exists": False,
                        "weather_names": list(WEATHER_NAMES),
                    },
                )
                return
            self._json(
                200,
                {"ok": True, "exists": True, **keeper_state_summary(state)},
            )
            return
        if path == "/api/palettes":
            self._json(200, {"palettes": PALETTES})
            return
        if path == "/api/grids":
            grids = []
            for file, payload in authoring_docs.grid_files(self.server.grids_dir):
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
                for file, payload in authoring_docs.grid_files(self.server.released_dir):
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
            # The semantic snapshot and its CAS token are one read. A
            # concurrent save must not pair an older profile with a new token.
            with self.server.authoring_lock:
                profiles = self.server.all_profiles()
                if wanted not in profiles:
                    self._json(404, {"ok": False, "error": "no such profile"})
                    return
                target = self.server.slips_dir / (_safe_name(wanted) + '.json')
                doc = {'format': authoring_docs.FORMAT, 'profile': profiles[wanted]}
                revision = authoring_docs.disk_revision(target)
            self._bind_document(doc)
            self._json(200, {'ok': True, 'profile': profiles[wanted],
                'disk_revision': revision})
            return
        if path.startswith("/api/grids/"):
            name = _safe_name(path.rsplit("/", 1)[-1])
            file = self.server.grids_dir / f"{name}.json"
            if not file.exists():
                self._json(404, {"ok": False, "error": "no such grid"})
                return
            try:
                with self.server.authoring_lock:
                    doc, revision = authoring_docs.load_document(file)
                grid = doc['grid']
                response = {'ok': True, 'name': name,
                    'matrix': authoring_docs.project_grid(grid),
                    'palette_id': grid.get('palette', {}).get('palette_id'),
                    'grid_id': grid.get('grid_id'), 'disk_revision': revision}
                if 'layers' in doc:
                    response['layers'] = doc['layers']
                self._bind_document(doc)
            except (OSError, ValueError, TypeError) as error:
                self._json(409, {'ok': False, 'error': str(error)})
                return
            self._json(200, response)
            return
        return super().do_GET()

    # ------------------------------------------------------------ POST
    def do_POST(self) -> None:  # noqa: N802
        self._response_context = {}
        try:
            self._post_request()
        except _ContextRefused:
            return
        except OSError as error:
            self._json(500, {'ok': False, 'error': 'local file operation failed; retain the draft and retry: ' + str(error)})
        except (TypeError, ValueError, KeyError, AttributeError) as error:
            self._json(400, {'ok': False, 'error': 'invalid request or carrier: ' + str(error), 'errors': [str(error)]})

    def _post_request(self) -> None:
        raw_revision = self.headers.get('X-Workshop-Draft-Revision')
        if raw_revision is not None:
            try:
                revision = json.loads(raw_revision)
            except ValueError:
                revision = raw_revision
            if (type(revision) not in (str, int) or len(str(revision)) > 120
                    or not str(revision).isascii()
                    or any(c in str(revision) for c in '\r\n')):
                self._json(400, {'ok': False, 'error': 'invalid draft revision header'})
                return
            self._response_context['draft_revision'] = revision
        path = self.path.split("?")[0]
        if self.server.keeper_dir is not None and path.startswith(("/api/session/", "/api/companion/")):
            self._json(403,dict(ok=False,error="Lab mutation APIs are unavailable for a native Keeper. Use the native application.")); return
        if path not in (
            "/api/context/document",
            "/api/drafts/grid", "/api/drafts/slip",
            "/api/packs/build", "/api/packs/preview", "/api/packs/export", "/api/packs/import",
            "/api/validate",
            "/api/save",
            "/api/slip/validate",
            "/api/slip/save",
            "/api/preview/render",
            "/api/preview/clip",
            "/api/preview/live",
            "/api/preview/offspring",
            "/api/preview/replay",
            "/api/export/png",
            "/api/export/apng",
            "/api/import/png",
            "/api/export/aseprite",
            "/api/import/aseprite",
            "/api/export/spritesheet",
            "/api/import/spritesheet",
            "/api/release",
            "/api/metrics/flush",
            "/api/session/new",
            "/api/session/era",
            "/api/session/covenant",
            "/api/companion/adopt",
            "/api/companion/act",
            "/api/companion/tick",
        ):
            self._json(404, {"ok": False, "error": "unknown endpoint"})
            return
        if path == "/api/import/png":
            self.server.session_metrics["imports"] += 1
            self._import_png(self._read_bytes())
            return
        if path == "/api/import/aseprite":
            data = self._read_bytes()
            result = import_aseprite_user_data_project(data)
            sidecar = extract_aseprite_user_data_sidecar(data)['sidecar'] if result.get('ok') else None
            self._import_result(result, sidecar)
            return
        try:
            payload = self._read_json()
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json(400, {"ok": False, "error": "invalid JSON"})
            return
        if not isinstance(payload, dict):
            self._json(400, {'ok': False, 'error': 'request must be an object'})
            return
        revision = payload.get('draft_revision')
        if revision is not None and (type(revision) not in (str, int) or
                len(str(revision)) > 120 or not str(revision).isascii() or any(c in str(revision) for c in '\r\n')):
            self._json(400, {'ok': False, 'error': 'draft_revision must be a short string or integer'})
            return
        if revision is not None:
            self._response_context['draft_revision'] = revision

        if path.startswith(("/api/context/", "/api/drafts/", "/api/packs/")):
            self._x3_post(path,payload); return
        if path in ("/api/save","/api/slip/save","/api/release","/api/metrics/flush"):
            if self._context_guard(payload) is None: return
        if path == "/api/slip/validate":
            self._slip_validate(payload)
            return
        if path == "/api/slip/save":
            self._slip_save(payload)
            return
        if path.startswith("/api/preview/"):
            self._preview(path.rsplit("/", 1)[-1], payload)
            return
        if path.startswith("/api/session/"):
            self._session(path.rsplit("/", 1)[-1], payload)
            return
        if path.startswith("/api/companion/"):
            self._companion(path.rsplit("/", 1)[-1], payload)
            return
        if path == "/api/import/spritesheet":
            self._import_spritesheet(payload)
            return
        if path == "/api/metrics/flush":
            stamp = time.strftime("%Y%m%d-%H%M%S")
            record = dict(self.server.session_metrics)
            record["provenance"] = "instrumented_pipeline_no_human_study_data"
            target = self.server.metrics_dir / f"session_{stamp}.json"
            data = (json.dumps(record, indent=2) + "\n").encode("utf-8")
            with self.server.mutation_lock():
                self._require_write_context(payload)
                authoring_docs.atomic_bytes(target,data)
            self._json(200, {"ok": True, "file": target.name})
            return
        if path == "/api/release":
            if self.server.keeper_dir is not None and "document" not in payload:
                self._json(400,dict(ok=False,error="Native release requires the complete selected authoring document.")); return
            self.server.session_metrics["releases"] += 1
            if 'document' in payload:
                self._release_document(payload)
                return
            with self.server.authoring_lock:
                source = self.server.grids_dir / (_safe_name(str(payload.get('name', ''))) + '.json')
                if 'expected_disk_revision' in payload and self._conflict(payload, 'expected_disk_revision',
                        authoring_docs.disk_revision(source, source.with_name(source.stem + '.layers.json'))):
                    return
                status, result = release_creature(self.server.grids_dir,
                    self.server.released_dir, str(payload.get('name', '')))
            self._json(status, result)
            return
        if path.startswith("/api/export/"):
            self.server.session_metrics["exports"] += 1
            self._export(path.rsplit("/", 1)[-1], payload)
            return
        name = _safe_name(str(payload.get('name', '')))
        doc = self._request_document(payload, grid_id=(f'workshop_{name}' if path == '/api/save'
                    else payload.get('grid_id') or 'workshop_draft'))
        if doc is None:
            return
        grid = doc['grid']
        errors = self._grid_errors(doc)
        if path == '/api/validate':
            metrics = self.server.session_metrics
            metrics['validations'] += 1
            if errors:
                metrics['invalid_verdicts'] += 1
                for error in errors:
                    metrics['validator_error_counts'][error] = metrics['validator_error_counts'].get(error, 0) + 1
            elif metrics['first_valid_at'] is None:
                metrics['first_valid_at'] = time.strftime('%Y-%m-%dT%H:%M:%S')
            # Invalid structures still get the authority's errors; derived
            # statistics are unavailable when their inputs cannot be read.
            try:
                stats = _morphology_stats(grid)
                alignment = {profile_id: {'ok': (result := is_grid_aligned(grid, profile)).ok,
                    'errors': list(result.errors)} for profile_id, profile in self.server.all_profiles().items()}
            except (TypeError, ValueError, KeyError, AttributeError):
                stats, alignment = None, {}
            self._json(200, {'ok': True, 'valid': not errors, 'errors': errors,
                'alignment': alignment, 'stats': stats, 'grid_cells': grid.get('cells', []),
                'selected_profile_valid': (not self._profile_errors(doc)) if 'profile' in doc else None,
                'selected_profile_errors': self._profile_errors(doc)})
            return
        if errors:
            self._json(400, {'ok': False, 'error': 'the engine rejects this grid or profile; fix it first', 'errors': errors})
            return
        target = self.server.grids_dir / (name + '.json')
        sidecar = self.server.grids_dir / (name + '.layers.json')
        with self.server.mutation_lock():
            if self._context_guard(payload) is None: return
            if 'document' in payload and self._conflict(payload, 'expected_disk_revision',
                    authoring_docs.disk_revision(target, sidecar)):
                return
            extra = {'document': doc, **({'layers': doc['layers']} if 'layers' in doc else {})} if 'document' in payload else (
                    {'layers': doc['layers']} if 'layers' in doc else None)
            try:
                backups = authoring_docs.preserved_write([(target, authoring_docs.json_bytes(grid)),
                    (sidecar, authoring_docs.json_bytes(extra) if extra is not None else None)],
                    before_write=lambda:self._require_write_context(payload))
            except OSError as error:
                self._json(500, {'ok': False, 'error': 'save failed; draft retained: ' + str(error)})
                return
            revision = authoring_docs.disk_revision(target, sidecar)
        self.server.session_metrics['saves'] += 1
        self._json(200, {'ok': True, 'file': target.name, 'backup': backups.get(target.name),
            'backups': backups, 'disk_revision': revision})

    def _release_document(self, payload: dict) -> None:
        doc = self._request_document(payload)
        if doc is None:
            return
        errors = self._grid_errors(doc)
        if errors:
            self._json(400, {'ok': False, 'error': 'the engine rejects this creature; fix it first', 'errors': errors})
            return
        released = deepcopy(doc)
        grid = released['grid']
        events = grid.setdefault('lineage', {}).setdefault('mutation_events', [])
        if 'released_into_ecosystem' not in events:
            events.append('released_into_ecosystem')
        grid.setdefault('metadata', {})['workshop_source_document_digest'] = authoring_docs.digest(doc)
        target = self.server.released_dir / (_safe_name(str(payload.get('name', ''))) + '.json')
        sidecar=target.with_name(target.stem+'.authoring.json') if self.server.keeper_dir is not None else None
        with self.server.mutation_lock():
            context=self._context_guard(payload, 'release')
            if context is None: return
            if self.server.keeper_dir is not None:
                grid['metadata']['workshop_release_context'] = {key:context[key] for key in ('keeper_id','campaign_id','context_id','context_revision')}
            if self._conflict(payload, 'expected_release_revision', authoring_docs.disk_revision(target,sidecar)):
                return
            try:
                changes=[(target,authoring_docs.json_bytes(grid))]
                if sidecar is not None: changes.append((sidecar,authoring_docs.json_bytes({'document':released})))
                backups = authoring_docs.preserved_write(changes,before_write=lambda:self._require_write_context(payload,'release'))
            except OSError as error:
                self._json(500, {'ok': False, 'error': 'release failed; draft retained: ' + str(error)})
                return
            revision = authoring_docs.disk_revision(target,sidecar)
        self._json(200, {'ok': True, 'file': target.name, 'backup': backups.get(target.name),
            'release_revision': revision, 'backups':backups, 'source_document_digest': authoring_docs.digest(doc),
            'released_document': released, 'released_document_digest': authoring_docs.digest(released),
            'transform': 'released_into_ecosystem', 'status':'staged',
            'released_grid_digest':authoring_docs.digest(grid),
            'release_provenance':grid.get('metadata',{}).get('workshop_release_context'),
            'admission':'The selected native era engine will judge this candidate when gathered and run.'})

    def _slip_validate(self, payload: dict) -> None:
        doc = self._request_document(payload, profile_only=True)
        if doc is None:
            return
        profile = doc['profile']
        verdict = validate_slip(profile)
        aligned = 0
        aligned_16 = 0
        if verdict.ok:
            for seed in self.server.seed_grids:
                if is_grid_aligned(seed, profile).ok:
                    aligned += 1
            for seed in self.server.seed_grids_16:
                if is_grid_aligned(seed, profile).ok:
                    aligned_16 += 1
        workshop_grids = []
        if verdict.ok and self.server.grids_dir.exists():
            for file, grid in authoring_docs.grid_files(self.server.grids_dir):
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
                    "seed_corpus_16": {
                        "aligned": aligned_16,
                        "total": len(self.server.seed_grids_16),
                    },
                    "workshop_grids": workshop_grids,
                },
            },
        )

    def _slip_save(self, payload: dict) -> None:
        doc = self._request_document(payload, profile_only=True)
        if doc is None:
            return
        if set(doc) != {'format', 'profile'}:
            self._json(400, {'ok': False, 'error': 'save the complete creature document through the grid editor; profile-only save cannot discard its grid or layers'})
            return
        profile = doc['profile']
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
        target = self.server.slips_dir / (_safe_name(profile_id) + '.json')
        with self.server.mutation_lock():
            if self._context_guard(payload) is None: return
            if 'document' in payload and self._conflict(payload, 'expected_disk_revision', authoring_docs.disk_revision(target)):
                return
            try:
                backups = authoring_docs.preserved_write([(target, authoring_docs.json_bytes(profile))],
                    before_write=lambda:self._require_write_context(payload))
            except OSError as error:
                self._json(500, {'ok': False, 'error': 'save failed; draft retained: ' + str(error)})
                return
            revision = authoring_docs.disk_revision(target)
        self._json(200, {'ok': True, 'file': target.name, 'backup': backups.get(target.name), 'disk_revision': revision})

    def _preview_context(self, payload, *, require_pins=False):
        """Fresh read authority for recomputation; request models are assertions."""
        from mecha_game.body_response import validate_body_response
        context = self.server.selected_context()['context']
        pinned = require_pins or 'context_id' in payload or 'expected_context_revision' in payload
        if pinned and (payload.get('context_id') != context['context_id'] or
                payload.get('expected_context_revision') != context['context_revision']):
            self._json(409, dict(ok=False, error='Selected Keeper context changed; refresh before previewing.',
                error_code='context_changed', context=context, current_context_revision=context['context_revision']))
            return None
        if not context['available']:
            self._json(409, dict(ok=False, error=context['reason'] or 'Selected Keeper context is unavailable.',
                error_code='context_unavailable', context=context, current_context_revision=context['context_revision']))
            return None
        model = validate_body_response(context['body_response'])
        if 'body_response' in payload and validate_body_response(payload['body_response']) != model:
            self._json(409, dict(ok=False, error='Body response differs from the selected context; refresh before previewing.',
                error_code='body_response_changed', context=context, current_context_revision=context['context_revision']))
            return None
        self._response_context.update(context_id=context['context_id'], context_revision=context['context_revision'],
            body_response=model, body_response_source=context['body_response_source'])
        return context

    def _living_preview_response(self, context, kind, document, profile, repair_model, parameters, result):
        # Capture effective inputs, never caller-supplied identity/model metadata.
        inputs = dict(kind=kind, document=document, profile=profile, parameters=parameters,
            repair_model_sha256=authoring_docs.digest(repair_model))
        identity = dict(format='mechagotchi_workshop_preview_v1', body_response=context['body_response'],
            context_id=context['context_id'], context_revision=context['context_revision'],
            inputs_sha256=authoring_docs.digest(inputs))
        # A native life may change while simulation or lazy model training runs.
        # Hold the shared publication lock only for the final read and response;
        # the engine evaluation itself never blocks a new-life writer.
        with self.server.mutation_lock():
            current = self._preview_context(dict(context_id=context['context_id'],
                expected_context_revision=context['context_revision'], body_response=context['body_response']))
            if current is None:
                return
            self._json(200, dict(ok=True, preview_identity=identity,
                preview_id=authoring_docs.digest(identity), **result))

    def _preview(self, kind: str, payload: dict) -> None:
        doc = None
        if 'document' in payload or payload.get('matrix') is not None:
            doc = self._request_document(payload, grid_id='workshop_draft_preview')
            if doc is None:
                return
            grid = doc['grid']
            errors = self._grid_errors(doc)
            if errors:
                self._json(400, {'ok': False, 'errors': errors})
                return
        else:
            grid = self.server.resolve_creature(str(payload.get('source', '')), str(payload.get('name', '')))
            if grid is None:
                self._json(404, {'ok': False, 'error': 'no such creature'})
                return

        context = None
        if kind in ('live', 'replay') or 'context_id' in payload or 'expected_context_revision' in payload:
            # Document binding above deliberately precedes response-context pins.
            context = self._preview_context(payload,
                require_pins=self.server.keeper_dir is not None and kind in ('live', 'replay'))
            if context is None:
                return

        if kind == "render":
            # T16: packet v2 — the requested animation state's projected
            # visuals ride the packet. E1 (cycle 05): the PROMOTED
            # mecha_engine.genome.render_packet_v2 now carries the SLIP
            # visual-grammar gate, so the workshop no longer depends on
            # the lab builder here. The species' profile bounds the
            # portrait vocabulary and honestly idles unsupported states.
            animation = payload.get("animation")
            profile = self._profile_for(payload, doc)
            try:
                packet = render_packet_v2(
                    grid, None, animation=animation, slip_profile=profile
                )
            except ValueError as error:
                self._json(400, {"ok": False, "error": str(error)})
                return
            self._json(200, {"ok": True, "packet": packet})
            return

        if kind == "clip":
            # C4 (cycle 11): the documented clip contract, scrubbed
            # end-to-end through the PROMOTED packet rung — every frame
            # is a render_packet_v2 whose animation field is the
            # dossier's block (clip/frame_index/frame_count/anchors).
            clip = str(payload.get("clip", "idle"))
            profile = self._profile_for(payload, doc)
            try:
                count = clip_frame_count(clip)
                frames = [
                    render_packet_v2(
                        grid,
                        None,
                        clip=clip,
                        frame_index=index,
                        slip_profile=profile,
                    )
                    for index in range(count)
                ]
            except ValueError as error:
                self._json(400, {"ok": False, "error": str(error)})
                return
            self._json(
                200,
                {
                    "ok": True,
                    "clip": clip,
                    "frame_count": count,
                    "frames": frames,
                    "clips": clip_names(),
                },
            )
            return

        profile = self._profile_for(payload, doc)
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

        if kind in ('live', 'replay'):
            cycles = max(1, min(5, int(payload.get("cycles", 3))))
            ticks = max(8, min(96, int(payload.get("ticks", 48))))
            seed = int(payload.get("rng_seed", 20260512))
            _, repair_model = self.server.models_for(grid)
            parameters = dict(damage_cycles=cycles, ticks=ticks, dropout_rate=0.2, rng_seed=seed)
            if kind == 'live':
                report = live_cycle(grid, profile, repair_model,
                    **parameters, body_response=context['body_response'])
                result = dict(report=report,
                    before=dict(packet=render_packet_from_grid(grid)),
                    after=dict(packet=render_packet_from_grid(report['final_grid'])))
            else:
                # A newly recomputed preview uses current physiology. Stored era
                # footage remains on its separate read-only route, byte for byte.
                result = dict(replay=build_replay(grid, profile, repair_model,
                    **parameters, body_response=context['body_response']))
            self._living_preview_response(context, kind,
                doc or dict(format=authoring_docs.FORMAT, grid=grid), profile,
                repair_model, parameters, result)
            return

        if kind == "offspring":
            count = max(1, min(8, int(payload.get("count", 4))))
            rng_seed = int(payload.get("rng_seed", 20260512))
            offspring_generation_model, _ = self.server.models_for(grid)
            children = []
            for index in range(count):
                child = generate_candidate(
                    grid,
                    offspring_generation_model,
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

    def _companion(self, kind: str, payload: dict) -> None:
        """W1: the living companion. Every beat is the engine's own
        machinery (adoption = `initial_state`'s gate, tending =
        `advance_tick`, idle life = the frozen switchboard, frames =
        packet v2); the server only resolves, persists, and serves."""
        if kind == "adopt":
            source = str(payload.get("source", "seed"))
            name = str(payload.get("name", ""))
            grid = None
            if source in ("seed", "workshop"):
                grid = self.server.resolve_creature(source, name)
            elif source == "campaign":
                state = load_keeper_state(self.server.session_state_path)
                eras = (
                    state["campaigns"][-1]["eras"]
                    if state is not None and state["campaigns"]
                    else []
                )
                elites = eras[-1]["elites"] if eras else []
                if not elites:
                    self._json(
                        409,
                        {
                            "ok": False,
                            "error": "nothing to adopt from the campaign "
                            "yet — run an era on the session page first",
                        },
                    )
                    return
                if name in ("", "best"):
                    grid = json.loads(
                        json.dumps(
                            max(elites, key=lambda e: e["score"])["grid"]
                        )
                    )
                else:
                    for elite in elites:
                        if elite["grid_id"] == name:
                            grid = json.loads(json.dumps(elite["grid"]))
                            break
            else:
                self._json(
                    400,
                    {"ok": False, "error": f"unknown adoption source: {source}"},
                )
                return
            if grid is None:
                self._json(
                    404,
                    {
                        "ok": False,
                        "error": f"no creature named {name!r} in "
                        f"source {source!r}",
                    },
                )
                return
            profile_id = str(payload.get("profile_id", "slip_lcd_seed"))
            profile = self.server.all_profiles().get(profile_id)
            if profile is None:
                self._json(
                    404,
                    {"ok": False, "error": f"unknown SLIP profile: {profile_id}"},
                )
                return
            try:
                companion = adopt_companion(
                    grid,
                    profile,
                    source={
                        "kind": source,
                        "name": name or grid.get("grid_id", ""),
                    },
                    name=str(payload["companion_name"])
                    if payload.get("companion_name")
                    else None,
                )
            except ValueError as error:
                # The ENGINE's verdict, verbatim: an invalid body or a
                # covenant mismatch refuses the adoption.
                self._json(400, {"ok": False, "error": str(error)})
                return
            save_companion(companion, self.server.companion_path)
            self._json(
                200, {"ok": True, "exists": True, **companion_snapshot(companion)}
            )
            return

        companion = load_companion(self.server.companion_path)
        if companion is None:
            self._json(
                409, {"ok": False, "error": "no companion yet — adopt one"}
            )
            return
        if not companion["state"]["alive"]:
            self._json(
                409,
                {
                    "ok": False,
                    "error": (
                        "the companion died of "
                        f"{companion['state']['death_cause']} at tick "
                        f"{companion['state']['age_ticks']} — adopt a "
                        "successor"
                    ),
                    "alive": False,
                    "death_cause": companion["state"]["death_cause"],
                },
            )
            return
        thought = None
        try:
            if kind == "act":
                player_act(companion, str(payload.get("action", "")))
            elif kind == "tick":
                _, _, thought = autonomous_tick(companion)
            else:
                self._json(
                    404,
                    {"ok": False, "error": f"unknown companion endpoint: {kind}"},
                )
                return
        except ValueError as error:
            self._json(400, {"ok": False, "error": str(error)})
            return
        save_companion(companion, self.server.companion_path)
        snapshot = companion_snapshot(companion)
        if thought is not None:
            snapshot["thought"] = thought
        self._json(200, {"ok": True, "exists": True, **snapshot})

    def _session(self, kind: str, payload: dict) -> None:
        """G4 (DR 0021): the Keeper's session — persistent, engine-run.

        Every number the page shows comes from the session lab's own
        read model over verbatim engine reports; the server never
        recomputes game logic."""
        if kind == "new":
            if self.server.session_state_path.exists():
                self._json(
                    409,
                    {
                        "ok": False,
                        "error": "a keeper session already exists — "
                        "advance it, or move the state file aside to "
                        "start over",
                    },
                )
                return
            state = new_keeper_state(
                campaign_id=str(
                    payload.get("campaign_id", "keeper_campaign_001")
                ),
                base_seed=int(payload.get("base_seed", 20260707)),
            )
            save_keeper_state(
                state,
                self.server.session_state_path,
                self.server.session_ledger_path,
            )
            self._json(
                200,
                {"ok": True, "exists": True, **keeper_state_summary(state)},
            )
            return

        if kind == "covenant":
            # C4 (DR 0021's Covenant step): adjust the covenant within
            # the EARNED budget; the authority validates, over-budget
            # requests come back with named violations.
            state = load_keeper_state(self.server.session_state_path)
            if state is None:
                self._json(
                    409,
                    {
                        "ok": False,
                        "error": "no keeper session yet — start one first",
                    },
                )
                return
            changes = {}
            if "allowed_palettes" in payload:
                changes["allowed_palettes"] = [
                    str(p) for p in payload["allowed_palettes"]
                ]
            if "deliberation_max_ticks" in payload:
                changes["deliberation_max_ticks"] = int(
                    payload["deliberation_max_ticks"]
                )
            if "population" in payload:
                changes["population"] = int(payload["population"])
            if "generations" in payload:
                changes["generations"] = int(payload["generations"])
            verdict = apply_covenant_change(state, **changes)
            if not verdict["ok"]:
                self._json(
                    400,
                    {
                        "ok": False,
                        "violations": verdict["violations"],
                        "budget": verdict["budget"],
                    },
                )
                return
            save_keeper_state(
                state,
                self.server.session_state_path,
                self.server.session_ledger_path,
            )
            self._json(
                200,
                {"ok": True, "exists": True, **keeper_state_summary(state)},
            )
            return

        if kind == "era":
            weather = str(payload.get("weather", "calm"))
            if weather not in WEATHER_NAMES:
                self._json(
                    400, {"ok": False, "error": f"unknown forecast: {weather}"}
                )
                return
            state = load_keeper_state(self.server.session_state_path)
            if state is None:
                self._json(
                    409,
                    {
                        "ok": False,
                        "error": "no keeper session yet — start one first",
                    },
                )
                return
            params = state["engine_parameters"]
            active = next(
                campaign
                for campaign in state["campaigns"]
                if campaign["campaign_id"] == state["active_campaign_id"]
            )
            # A4: the corpus and models follow the active campaign's own
            # recorded scale — pre-A4 8x8 bloodlines keep their machinery;
            # fresh campaigns run at the ratified 16x16 default.
            scale = session_scale(state)
            scale_generation_model, _ = self.server.models_for(
                {"grid_size": [scale, scale]}
            )
            turn = advance_keeper_state(
                state,
                weather,
                seed_grids=self.server.seeds_for_scale(scale),
                generation_model=scale_generation_model,
                repair_model=self.server.session_repair_model(
                    params["repair_epochs"], active["base_seed"], scale
                ),
                legibility_model=self.server.legibility_model(),
                # E5 (DR 0021's Contribute step): the Keeper's released
                # creatures enter this era as founders through the
                # engine's own gates.
                released_dir=self.server.released_dir,
            )
            save_keeper_state(
                state,
                self.server.session_state_path,
                self.server.session_ledger_path,
            )
            self._json(
                200,
                {
                    "ok": True,
                    "turn": turn,
                    **keeper_state_summary(state),
                },
            )
            return

        self._json(404, {"ok": False, "error": "unknown session endpoint"})

    def _export(self, kind: str, payload: dict) -> None:
        """Strict per the 4-W pillar: exports carry the engine's word."""
        grid_id = _safe_name(str(payload.get('name') or 'workshop_export'))
        doc = self._request_document(payload, grid_id='workshop_' + grid_id)
        if doc is None:
            return
        profile = self._profile_for(payload, doc)
        if profile is None:
            self._json(400, {'ok': False, 'errors': ['no such profile']})
            return
        grid = doc['grid']
        errors = self._grid_errors(doc)
        if 'profile' not in doc:
            errors.extend(self._profile_errors({'profile': profile}))
        if errors:
            self._json(400, {'ok': False, 'errors': errors})
            return
        modern = 'document' in payload
        if modern and 'profile' not in doc:
            doc = self._bind_document({**doc, 'profile': deepcopy(profile)}, payload)
        carrier = {'authoring_document': doc} if modern else {}
        alignment = is_grid_aligned(grid, profile)
        if not alignment.ok:
            self._json(400, {"ok": False, "errors": list(alignment.errors)})
            return
        # H3 (cycle 18): a named clip means the export carries the
        # engine's projected clip frames, not the historical pulse —
        # the DR 0013 additive-rung shape (no clip, no change). The
        # frames are presentation; the sidecar's semantic grid stays
        # the single truth.
        clip = payload.get("clip")
        clip_frames = None
        if clip is not None:
            if kind not in ("apng", "spritesheet"):
                self._json(
                    400,
                    {
                        "ok": False,
                        "errors": [
                            "clip frames export as APNG or spritesheet "
                            "only; a single-frame export has no clip"
                        ],
                    },
                )
                return
            try:
                packets = [
                    render_packet_v2(
                        grid,
                        None,
                        clip=str(clip),
                        frame_index=index,
                        slip_profile=profile,
                    )
                    for index in range(clip_frame_count(str(clip)))
                ]
            except ValueError as error:
                self._json(400, {"ok": False, "errors": [str(error)]})
                return
            clip_frames = {
                "clip": str(clip),
                "frames": [
                    {
                        "cells": packet["cells"],
                        "animation": packet["animation"],
                    }
                    for packet in packets
                ],
            }
        if kind == "png":
            exported = export_png_with_embedded_sidecar(grid, profile, **carrier)
            self._png(exported["embedded_png_bytes"], grid_id + ".png")
            return
        if kind == "apng":
            exported = export_apng_with_sidecar(
                grid, profile, clip_frames=clip_frames, **carrier
            )
            data = exported['png_bytes']
            if modern:
                data = embed_sidecar_in_png_text_chunk(data, exported['sidecar'])
            self._png(data, grid_id + '.apng.png')
            return
        if kind == "aseprite":
            exported = export_aseprite_user_data_project(grid, profile, **carrier)
            self._file(
                exported["project_bytes"],
                grid_id + ".aseprite",
                "application/octet-stream",
            )
            return
        if kind == "spritesheet":
            exported = export_spritesheet_with_sidecar(
                grid, profile, clip_frames=clip_frames, **carrier
            )
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
        try:
            extracted = extract_embedded_sidecar_from_png(data)
        except (ValueError, TypeError, KeyError):
            self._import_result(import_png_with_embedded_sidecar(data))
            return
        sidecar = extracted['sidecar']
        if 'apng_binding' in sidecar:
            result = import_apng_with_sidecar(extracted['canonical_png_bytes'], sidecar)
        else:
            result = import_png_with_embedded_sidecar(data)
        self._import_result(result, sidecar)

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
            import_spritesheet_with_sidecar(png_bytes, sidecar), sidecar
        )

    def _import_result(self, result: dict, sidecar: dict | None = None) -> None:
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
        restored = result['restored_grid']
        sidecar = sidecar or result.get('sidecar')
        try:
            doc = authoring_docs.carrier_document(sidecar) if sidecar else None
            if doc is None:
                doc = {'format': authoring_docs.FORMAT, 'grid': restored}
                if sidecar and isinstance(sidecar.get('slip_binding', {}).get('profile_snapshot'), dict):
                    doc['profile'] = deepcopy(sidecar['slip_binding']['profile_snapshot'])
            errors = self._grid_errors(doc)
            if errors:
                raise ValueError('; '.join(errors))
            self._bind_document(doc)
            restored = doc['grid']
            response = {'ok': True, 'matrix': authoring_docs.project_grid(restored),
                'palette_id': restored.get('palette', {}).get('palette_id'),
                'grid_id': restored.get('grid_id'), 'engine_valid': True}
            if 'layers' in doc:
                response['layers'] = doc['layers']
            self._json(200, response)
        except (ValueError, TypeError, KeyError) as error:
            self._json(400, {'ok': False, 'errors': [str(error)], 'families': ['authoring_document_conflict']})



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
    target = released_dir / source.name
    try:
        backups = authoring_docs.preserved_write([(target, authoring_docs.json_bytes(grid))])
    except OSError as error:
        return 500, {'ok': False, 'error': 'release failed: ' + str(error)}
    return 200, {'ok': True, 'file': target.name, 'backup': backups.get(target.name)}



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
    metrics_dir: Path = DEFAULT_METRICS_DIR,
    session_dir: Path | None = None,
    keeper_dir: Path | None = None,
) -> WorkshopServer:
    server = WorkshopServer(
        ("127.0.0.1", port),
        grids_dir,
        slips_dir,
        released_dir,
        metrics_dir,
        session_dir=session_dir,
        keeper_dir=keeper_dir,
    )
    thread = threading.Thread(target=server.serve_forever, name="Workshop foreground server")
    server.workshop_thread = thread
    thread.start()
    return server


def main() -> None:
    parser = argparse.ArgumentParser(description="mecha_workshop server")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--grids-dir", type=Path, default=DEFAULT_GRIDS_DIR)
    parser.add_argument("--keeper-dir", type=Path, default=None)
    parser.add_argument(
        "--release",
        type=str,
        default=None,
        help="One-shot: release a saved creature into the ecosystem, "
        "print the JSON result, exit.",
    )
    args = parser.parse_args()
    if args.release is not None and args.keeper_dir is not None:
        import urllib.request
        import urllib.error
        server=start_workshop_server(keeper_dir=args.keeper_dir)
        try:
            context=server.selected_context()['context']
            if not context['available']: raise ValueError(context['reason'])
            doc,_=authoring_docs.load_document(server.grids_dir/(_safe_name(args.release)+'.json'))
            request=urllib.request.Request(f'http://127.0.0.1:{server.server_address[1]}/api/release',
                data=json.dumps(dict(document=doc,name=args.release,draft_revision='cli-selected',
                    context_id=context['context_id'],expected_context_revision=context['context_revision'])).encode(),
                headers={'Content-Type':'application/json'})
            try: response=urllib.request.urlopen(request,timeout=30)
            except urllib.error.HTTPError as error: response=error
            with response: status,result=response.status,json.loads(response.read())
        except (OSError,ValueError) as error: status,result=400,dict(ok=False,error=str(error))
        finally: server.close_workshop()
        print(json.dumps(result)); raise SystemExit(0 if status==200 else 1)
    if args.release is not None:
        status, result = release_creature(
            args.grids_dir, DEFAULT_RELEASED_DIR, args.release
        )
        print(json.dumps(result))
        raise SystemExit(0 if status == 200 else 1)
    server = start_workshop_server(port=args.port, grids_dir=args.grids_dir, keeper_dir=args.keeper_dir)
    print(
        f"workshop serving on http://127.0.0.1:{server.server_address[1]}/",
        flush=True,
    )
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        server.close_workshop()


if __name__ == "__main__":
    main()
