"""The Contribute step — workshop releases enter the eras (F9).

DR 0021 step 3, as a FILE bridge (the workshop keeps its own stack):
released creatures are JSON grids in a release inbox — the workshop's
committed `data/workshop/released/` in a checkout, plus the player's
own `keeper/released/` — loaded in the lab's deterministic file order
(backups skipped, a missing inbox is simply no releases) and fed into
the era seam. ADMISSION IS THE ENGINE'S VERDICT: `evolve`'s DR 0016/
DR 0029 gates admit a release to LEAD the pool or reject it with
verbatim errors — both recorded in the era report's `founders` block
and both shown to the Keeper, never smoothed.
"""

from __future__ import annotations

import base64
import copy
import json
from pathlib import Path

from mecha_game.packets import data_search_origins


def load_released_grids(released_dir: str | Path | None) -> list[dict]:
    """The lab's rule verbatim: deterministic file order, `.bak.json`
    backups skipped, a missing/None inbox is no releases."""
    if released_dir is None:
        return []
    released_dir = Path(released_dir)
    if not released_dir.exists():
        return []
    grids = []
    for file in sorted(released_dir.glob("*.json")):
        if file.name.endswith((".bak.json", ".authoring.json", ".layers.json")):
            continue
        grids.append(json.loads(file.read_text(encoding="utf-8")))
    return grids


def default_release_inboxes(
    keeper_dir: str | Path, start: Path | None = None, *, include_shared: bool = True
) -> list[Path]:
    """The inboxes, in read order: the workshop's release directory
    (when a checkout or bundle carries one) then the player's own."""
    inboxes: list[Path] = []
    for origin in data_search_origins(start) if include_shared else ():
        for base in (origin, *origin.parents):
            workshop = base / "data" / "workshop" / "released"
            if workshop.is_dir():
                inboxes.append(workshop)
                break
        if inboxes:
            break
    inboxes.append(Path(keeper_dir) / "released")
    return inboxes


def gather_releases(
    keeper_dir: str | Path, start: Path | None = None, *, include_shared: bool = True
) -> list[dict]:
    """Read chosen inboxes; native selected-Keeper callers disable shared data."""
    grids: list[dict] = []
    for inbox in default_release_inboxes(keeper_dir, start=start, include_shared=include_shared):
        grids.extend(load_released_grids(inbox))
    return grids


def gather_release_inputs(
    keeper_dir: str | Path, start: Path | None = None, *, include_shared: bool = True
) -> tuple[list[dict], list[dict]]:
    """Capture each selected file once; parse the same bytes retained as evidence."""
    grids, sources = [], []
    own_inbox = (Path(keeper_dir) / "released").resolve()
    for inbox in default_release_inboxes(keeper_dir, start=start, include_shared=include_shared):
        if not inbox.is_dir():
            continue
        for file in sorted(inbox.glob("*.json")):
            if file.name.endswith((".bak.json", ".authoring.json", ".layers.json")):
                continue
            payload = file.read_bytes()
            grid = json.loads(payload.decode("utf-8"))
            label_root = "released" if inbox.resolve() == own_inbox else "shared_released"
            sources.append(dict(role="founder", source_kind="workshop_release",
                source_position=len(grids), label=f"{label_root}/{file.name}",
                data_base64=base64.b64encode(payload).decode("ascii")))
            grids.append(grid)
    return grids, sources


def companion_release_source(session) -> dict:
    """Record the actual staged life, keeping its earlier origin a separate fact."""
    from .care_history import capture_care_context
    context = capture_care_context(session)
    life = session.lineage[-1]
    source = dict(role="founder", source_kind="keeper_companion", source_position=0,
                  keeper_id=session.keeper_id, life_id=life["life_id"], origin=life["origin"],
                  care_context=context)
    recorded = life.get("source") or {}
    for key in ("campaign_id", "era_index", "niche_key"):
        if key in recorded:
            source[key] = copy.deepcopy(recorded[key])
    return source


def founders_verdict(era_record: dict) -> dict | None:
    """The engine's own admission verdict for an era's submissions
    (``None`` when the era ran without founders)."""
    return era_record["report"].get("founders")
