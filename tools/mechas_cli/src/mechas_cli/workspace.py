"""Locate the Mechagotchi workspace the CLI operates on.

Resolution order:

1. ``MECHAGOTCHI_ROOT`` environment variable (explicit override).
2. The editable-install source location (this file lives inside the repo
   at ``tools/mechas_cli/src/mechas_cli/``, so four parents up is the
   workspace — the same ROOT-anchoring convention the labs use).
3. Walking up from the current directory looking for the workspace
   markers.

Stdlib-only so the module is testable without the CLI dependencies.
"""

from __future__ import annotations

import os
from pathlib import Path


_MARKERS = ("data/readability", "labs", "research")


class WorkspaceNotFoundError(RuntimeError):
    """Raised when no Mechagotchi workspace can be located."""


def _looks_like_workspace(candidate: Path) -> bool:
    return all((candidate / marker).exists() for marker in _MARKERS)


def find_workspace_root(start: Path | None = None) -> Path:
    env_override = os.environ.get("MECHAGOTCHI_ROOT")
    if env_override:
        candidate = Path(env_override).resolve()
        if _looks_like_workspace(candidate):
            return candidate
        raise WorkspaceNotFoundError(
            f"MECHAGOTCHI_ROOT is set to {candidate}, but that folder does "
            "not look like a Mechagotchi workspace (missing "
            f"{', '.join(_MARKERS)})."
        )

    anchored = Path(__file__).resolve().parents[4]
    if _looks_like_workspace(anchored):
        return anchored

    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if _looks_like_workspace(candidate):
            return candidate

    raise WorkspaceNotFoundError(
        "Could not find the Mechagotchi workspace. Run `mechas` from inside "
        "the repository, or set MECHAGOTCHI_ROOT to its folder."
    )
