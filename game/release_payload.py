"""Audited application payload for the Windows x64 one-directory build.

The resource tree preserves the existing helper modules' ROOT contracts. These
are shipped application content, not a second editable source checkout.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "game/src"))
from mecha_game.runtime_resources import MANIFEST_FORMAT, MANIFEST_NAME, NATIVE_TARGET, content_identity

HELPER_FILES = (
    "workshop/server/workshop_server.py", "workshop/server/authoring.py", "workshop/server/drafts.py",
    "labs/workshop_editor/spritesheet_sidecar_decoder.py", "labs/workshop_editor/workshop_editor.py",
    "labs/workshop_editor/standard_image_sidecar_decoder.py", "labs/workshop_editor/png_chunk_reader.py",
    "labs/workshop_editor/external_metadata_sidecar.py", "labs/workshop_editor/slip_authoring_panel.py",
    "labs/workshop_editor/png_embedded_sidecar_writer.py", "labs/workshop_editor/png_apng_sidecar_decoder.py",
    "labs/workshop_editor/aseprite_user_data_chunk_writer.py", "labs/grid_genome/validator.py",
    "labs/grid_genome/slip.py", "labs/grid_genome/corpus_builder.py", "labs/grid_genome/invariant_scaling.py",
    "labs/grid_genome/grid_helpers.py", "labs/grid_genome/markov_grid.py", "labs/grid_genome/constrained_generator.py",
    "labs/grid_genome/micro_switchboard.py", "labs/slip_validator/slip_validator.py",
    "labs/slip_validator/schema_migration_gate.py", "labs/slip_validator/pydantic_contract.py",
    "labs/game_loop/session_runner.py", "labs/game_loop/replay_recorder.py", "labs/game_loop/companion.py",
    "labs/readability_benchmark/readability_benchmark.py", "labs/readability_benchmark/learned_readability.py",
    "labs/cellular_automata/ca_nca_growth_repair.py", "labs/lifecycle_sim/lifecycle_sim.py",
    "labs/lifecycle_sim/body_response.py",
    "labs/micro_threads/thread_fleet.py",
)
RESOURCE_FILES = (
    "packages/mecha_engine/pyproject.toml",
    "data/slips/valid/slip_lcd_seed.json", "data/slips/valid/slip_v2_cleanliness.json",
    "data/slips/valid/slip_amber_social.json", "data/slips/valid/slip_gray_stable.json",
    "data/slips/valid/slip_v2_no_shell.json",
    "data/readability_benchmark/adopted_readability_model.json",
    "data/cubff_real_ingest/real_snapshot_ingest_stage0_report.json",
    "data/cubff_real_ingest/callback_states/callback_states_compact.json",
    "data/packs/mechagotchi_starter_pack.json",
    "research/slip/slip.schema.json", "research/slip/slip_pydantic_model.schema.json", "LICENSE",
)
RESOURCE_DIRS = ("data/seed_grids_16x16", "workshop/grid_editor", "workshop/slip_creator",
                 "workshop/preview", "workshop/inspector", "workshop/packs", "workshop/shared",
                 "workshop/companion", "workshop/session", "game/notices")
BUNDLED_DATA = [(path, Path(path).parent.as_posix()) for path in RESOURCE_FILES + HELPER_FILES]
BUNDLED_DATA += [(path, path) for path in RESOURCE_DIRS]
HELPER_MODULES = tuple(Path(path).stem for path in HELPER_FILES)
HELPER_PATHS = tuple(sorted({str(ROOT / Path(path).parent) for path in HELPER_FILES}))
DEPENDENCIES = ("pygame-ce", "pydantic", "pydantic-core", "jsonschema", "jsonschema-specifications",
                "referencing", "rpds-py", "attrs", "typing-extensions", "annotated-types", "typing-inspection", "pyinstaller")


def file_record(path: Path) -> dict:
    content = path.read_bytes()
    return {"size": len(content), "sha256": hashlib.sha256(content).hexdigest()}


def source_identity() -> dict:
    # Track the runtime inputs, not test outputs/ignored build folders. Dirty
    # paths and HEAD are reported honestly even for an uncommitted local build.
    paths = set(RESOURCE_FILES + HELPER_FILES + ("game/build_release.py", "game/release_payload.py", "game/pyproject.toml", "game/PLAYER-README.txt"))
    for folder in RESOURCE_DIRS + ("game/src", "packages/mecha_engine/src"):
        paths.update(path.relative_to(ROOT).as_posix() for path in (ROOT / folder).rglob("*")
                     if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    status = subprocess.check_output(["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=ROOT, text=True)
    return {"head": head, "dirty": bool(status.strip()), "dirty_status": status.splitlines(),
            "files": {name: file_record(ROOT / name)["sha256"] for name in sorted(paths)}}


def _notices(stage: Path) -> list[dict]:
    pygame_notices = json.loads((stage / "game/notices/pygame-ce-2.5.7/sources.json").read_text(encoding="utf-8"))
    if importlib.metadata.version("pygame-ce") != pygame_notices["installed_versions"]["pygame_ce"]:
        raise RuntimeError("pygame-ce version changed; review the declared upstream notices before release")
    notice_root = stage / "game/notices/pygame-ce-2.5.7"
    for record in pygame_notices["source_files"]:
        if file_record(notice_root / record["file"]) != {key: record[key] for key in ("size", "sha256")}:
            raise RuntimeError(f"Upstream notice identity changed: {record['file']}")
    pygame_root = Path(importlib.metadata.distribution("pygame-ce").locate_file("pygame"))
    for name, expected in pygame_notices["installed_files"].items():
        if file_record(pygame_root / name)["sha256"] != expected:
            raise RuntimeError(f"Installed pygame dependency changed; review notices: {name}")
    if file_record(pygame_root / "freesansbold.ttf")["sha256"] != pygame_notices["font"]["sha256"]:
        raise RuntimeError("Installed default font changed; review its embedded notices")
    notices = stage / "notices"
    notices.mkdir()
    python_license = Path(sys.base_prefix) / "LICENSE.txt"
    if not python_license.is_file():
        python_license = Path(sys.base_prefix) / "LICENSE"
    shutil.copy2(python_license, notices / "CPython-LICENSE.txt")
    rows = [{"name": "CPython", "version": sys.version.split()[0], "license_files": ["notices/CPython-LICENSE.txt"]}]
    for name in DEPENDENCIES:
        dist = importlib.metadata.distribution(name)
        folder = notices / name
        folder.mkdir()
        metadata = dist.read_text("METADATA")
        (folder / "METADATA.txt").write_text(metadata or "", encoding="utf-8")
        license_files = []
        for item in dist.files or []:
            if any(token in part.lower() for part in item.parts for token in ("license", "copying", "notice")) and dist.locate_file(item).is_file():
                target = folder / Path(str(item)).name
                shutil.copy2(dist.locate_file(item), target)
                license_files.append(target.relative_to(stage).as_posix())
        rows.append({"name": name, "version": dist.version, "license_files": sorted(set(license_files)),
                     "metadata": f"notices/{name}/METADATA.txt"})
    rows.append({"name": "pygame-ce-upstream-notices", "version": pygame_notices["installed_versions"]["pygame_ce"],
                 "source_receipt": "game/notices/pygame-ce-2.5.7/sources.json",
                 "license_files": sorted(path.relative_to(stage).as_posix() for path in (stage / "game/notices/pygame-ce-2.5.7").glob("*.txt"))})
    (notices / "README.txt").write_text(
        "Mechagotchi Windows x64 onedir runtime notices\n"
        "Project license: ../LICENSE (Apache-2.0).\n"
        "Dependency versions, installed metadata and available license texts are retained here.\n"
        "PyInstaller is the build tool/bootloader; its exception is in its COPYING.txt.\n"
        "pygame-ce is LGPL-2.1-or-later and the runtime uses its unmodified dynamic libraries.\n"
        "Tagged pygame/SDL notices and installed DLL/font identities: ../game/notices/pygame-ce-2.5.7/sources.json.\n"
        "Runtime manifests are unsigned content receipts, not signatures or independent provenance evidence.\n",
        encoding="utf-8")
    return rows


def stage_payload(stage: Path) -> dict:
    """Create a new staging directory; never merge stale payload bytes."""
    stage.mkdir(parents=True, exist_ok=False)
    before = source_identity()
    for source, destination in BUNDLED_DATA:
        origin = ROOT / source
        target = stage / destination
        if origin.is_dir():
            shutil.copytree(origin, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            target.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origin, target / origin.name)
    notices = _notices(stage)
    manifest = {"format": MANIFEST_FORMAT, "target": NATIVE_TARGET, "source": before,
                "helper_modules": list(HELPER_MODULES), "notices": notices,
                "files": {path.relative_to(stage).as_posix(): file_record(path)
                          for path in sorted(stage.rglob("*")) if path.is_file()}}
    after = source_identity()
    if after["files"] != before["files"] or after["head"] != before["head"]:
        raise RuntimeError("Runtime sources changed during staging; freeze writers and build a fresh artifact")
    manifest["content_id"] = content_identity(manifest)
    (stage / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def write_artifact_manifest(bundle: Path, runtime_manifest: dict) -> Path:
    """Hash the complete delivered directory, including executable/dependencies."""
    target = bundle / "artifact-manifest.json"
    if target.exists():
        raise FileExistsError("Artifact identity already exists; build into a fresh directory")
    readme = bundle / "README.txt"
    if readme.exists():
        raise FileExistsError("Player README already exists; build into a fresh directory")
    shutil.copy2(ROOT / "game/PLAYER-README.txt", readme)
    if file_record(readme)["sha256"] != runtime_manifest["source"]["files"]["game/PLAYER-README.txt"]:
        raise RuntimeError("Player README changed during build; rebuild from frozen source")
    manifest = {"format": "mechagotchi_windows_artifact_v1", "target": NATIVE_TARGET,
                "runtime_content_id": runtime_manifest["content_id"], "source": runtime_manifest["source"],
                "files": {path.relative_to(bundle).as_posix(): file_record(path)
                          for path in sorted(bundle.rglob("*")) if path.is_file()}}
    manifest["content_id"] = content_identity(manifest)
    target.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target
