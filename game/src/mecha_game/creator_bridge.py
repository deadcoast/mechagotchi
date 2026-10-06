"""Owned local Workshop bridge; no detached service or inferred save home."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import webbrowser


def workshop_resource_root() -> Path:
    from mecha_game.runtime_resources import runtime_root
    return runtime_root()


def _server_module():
    path = workshop_resource_root() / "workshop/server/workshop_server.py"
    if not path.is_file():
        raise ValueError("Workshop resources are unavailable in this installation. Open Workshop from the source installation with --keeper-dir pointing to this save.")
    from mecha_game.runtime_resources import validate_resource
    for relative in ("workshop", "labs", "data/slips/valid", "research/slip"):
        validate_resource(workshop_resource_root() / relative)
    import hashlib
    name = "_mechagotchi_owned_workshop_" + hashlib.sha256(str(path.resolve()).encode("utf-8")).hexdigest()[:16]
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError("Workshop server could not be loaded from this installation.")
    module = importlib.util.module_from_spec(spec)
    folder = str(path.parent)
    added = folder not in sys.path
    if added:
        sys.path.insert(0, folder)
    try:
        spec.loader.exec_module(module)
    finally:
        if added:
            sys.path.remove(folder)
    sys.modules[name] = module
    return module


class CreatorBridge:
    """One server owned by the active native application, reused while it lives."""

    def __init__(self, keeper_dir: Path):
        self.keeper_dir = Path(keeper_dir).resolve()
        self.server = None
        self.url = None
        self.browser_opened = False

    def open(self, *, open_browser: bool = True) -> str:
        if self.server is None:
            self.server = _server_module().start_workshop_server(port=0, keeper_dir=self.keeper_dir)
            self.url = f"http://127.0.0.1:{self.server.server_address[1]}/"
        if not open_browser:
            self.browser_opened = False
            return self.url
        try:
            self.browser_opened = bool(webbrowser.open(self.url))
        except (OSError, webbrowser.Error):
            self.browser_opened = False
        return self.url

    def close(self) -> None:
        if self.server is not None:
            server, self.server = self.server, None
            self.url = None
            server.close_workshop()
