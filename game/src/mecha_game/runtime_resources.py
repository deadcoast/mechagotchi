"""Explicit source/native resource authority; a bundle never borrows a checkout."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import sys

MANIFEST_NAME = "runtime-manifest.json"
MANIFEST_FORMAT = "mechagotchi_runtime_manifest_v1"
NATIVE_TARGET = "windows_x64_onedir"


def source_checkout_root(start: Path | None = None) -> Path | None:
    """Recognize this module's actual source tree, never an installed ancestor."""
    if getattr(sys, "frozen", False):
        return None
    module = Path(__file__).resolve()
    if len(module.parents) < 4:
        return None
    root = module.parents[3]
    if module != root / "game/src/mecha_game/runtime_resources.py":
        return None
    if not (root / "AGENTS.md").is_file() or not (root / "packages/mecha_engine/src/mecha_engine").is_dir():
        return None
    if start is not None and not Path(start).resolve().is_relative_to(root):
        return None
    return root


def runtime_mode() -> str:
    if getattr(sys, "frozen", False):
        return "frozen_windows_x64"
    return "source_checkout" if source_checkout_root() else "unsupported_install"


def runtime_root(start: Path | None = None) -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent / "_internal")).resolve()
    return source_checkout_root(start) or Path(__file__).resolve().parent


def resource_roots(start: Path | None = None) -> list[Path]:
    if getattr(sys, "frozen", False):
        return [runtime_root()]
    root = source_checkout_root(start)
    return [root] if root else []


def content_identity(manifest: dict) -> str:
    """Unsigned deterministic integrity receipt, not a trust/signature claim."""
    body = {key: value for key, value in manifest.items() if key != "content_id"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")).hexdigest()


def read_manifest(root: Path) -> dict:
    path = root / MANIFEST_NAME
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"Runtime manifest unavailable: {exc}") from exc
    if not isinstance(manifest, dict) or manifest.get("format") != MANIFEST_FORMAT:
        raise ValueError("Runtime manifest format is invalid")
    if manifest.get("target") != NATIVE_TARGET or manifest.get("content_id") != content_identity(manifest):
        raise ValueError("Runtime manifest identity is invalid")
    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise ValueError("Runtime manifest has no declared files")
    for name, record in files.items():
        relative = PurePosixPath(name)
        if (relative.is_absolute() or ".." in relative.parts or "\\" in name or ":" in name
                or name != relative.as_posix() or not isinstance(record, dict)
                or not isinstance(record.get("size"), int) or record["size"] < 0
                or not isinstance(record.get("sha256"), str) or len(record["sha256"]) != 64):
            raise ValueError(f"Runtime manifest file entry is invalid: {name}")
    return manifest


def _file_problem(root: Path, name: str, record: dict) -> str | None:
    path = root / name
    try:
        if not path.resolve().is_relative_to(root.resolve()):
            return "outside_root"
        content = path.read_bytes()
    except OSError:
        return "missing"
    return None if len(content) == record["size"] and hashlib.sha256(content).hexdigest() == record["sha256"] else "mismatched"


def validate_resource(path: Path) -> None:
    """Check a requested native feature before consuming its bundled bytes."""
    if not getattr(sys, "frozen", False):
        return
    root = runtime_root()
    try:
        relative = path.resolve().relative_to(root).as_posix()
    except ValueError as exc:
        raise FileNotFoundError(f"Runtime resource is outside this bundle: {path}") from exc
    try:
        manifest = read_manifest(root)
    except ValueError as exc:
        raise FileNotFoundError(str(exc)) from exc
    names = [name for name in manifest["files"] if name == relative or name.startswith(relative + "/")]
    if not names:
        raise FileNotFoundError(f"Runtime resource is not declared: {relative}")
    for name in names:
        problem = _file_problem(root, name, manifest["files"][name])
        if problem:
            raise FileNotFoundError(f"Runtime resource {problem}: {name}")


def inspect_runtime() -> dict:
    """JSON-native diagnostics; reading resources never writes to a save home."""
    root = runtime_root()
    mode = runtime_mode()
    result = dict(mode=mode, root=str(root), target=NATIVE_TARGET,
                  supported=mode != "unsupported_install", manifest_path=str(root / MANIFEST_NAME),
                  content_id=None, source=None, complete=False, missing=[], mismatched=[], errors=[])
    manifest = None
    if mode == "frozen_windows_x64":
        try:
            manifest = read_manifest(root)
            result.update(content_id=manifest["content_id"], source=manifest.get("source"),
                          manifest_format=manifest["format"], file_count=len(manifest["files"]))
            for name, record in manifest["files"].items():
                problem = _file_problem(root, name, record)
                if problem:
                    result["missing" if problem == "missing" else "mismatched"].append(name)
            result["complete"] = not result["missing"] and not result["mismatched"]
        except ValueError as exc:
            result["errors"].append(str(exc))
    elif mode == "source_checkout":
        result["source"] = {"root": str(root), "form": "developer_checkout"}
        result["complete"] = None  # source is not a built artifact certificate
    else:
        result["errors"].append("Standalone wheel is not a complete player installation; use the Windows onedir release or the source checkout.")
    helpers = set(manifest.get("helper_modules", [])) if manifest else set()
    result["loaded_modules"] = {
        name: str(Path(module.__file__).resolve())
        for name, module in sorted(list(sys.modules.items()))
        if getattr(module, "__file__", None) and (
            name == "mecha_game" or name.startswith("mecha_game.")
            or name == "mecha_engine" or name.startswith("mecha_engine.")
            or name in helpers or name.startswith("_mechagotchi_owned_workshop")
            or "/labs/" in str(module.__file__).replace("\\", "/")
            or "/workshop/server/" in str(module.__file__).replace("\\", "/"))
    }
    return result
