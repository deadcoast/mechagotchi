"""Community profile packs — the FORMAT rung (F16, MVP 0.3).

`mechagotchi_pack_v1`: SLIPs + creatures + provenance in ONE
importable file — the documented community surface at its first
honest rung (distribution infrastructure stays Phase G; this is the
carrier). The gates are the engine's, twice over:

- **the BUILDER refuses invalid content** with the validators'
  verbatim errors — an invalid pack cannot be published;
- **IMPORT judges every item again** (packs travel and can be
  tampered with) and stages ONLY accepted items into the existing
  inboxes — covenants into `keeper/covenants/` (candidates the
  Keeper imports with I), creatures into `keeper/released/` (where
  the era admission gates judge them a third time at run time, DR
  0016/0029) — per-item verdicts, nothing smoothed.
"""

from __future__ import annotations

import json
from pathlib import Path

from mecha_engine.genome import validate_grid
from mecha_engine.slip import validate_slip

PACK_FORMAT = "mechagotchi_pack_v1"


def build_pack(
    *,
    pack_id: str,
    title: str,
    provenance: dict,
    slips: list[dict],
    creatures: list[dict],
) -> dict:
    """Assemble a pack, refusing invalid content verbatim."""
    for slip in slips:
        verdict = validate_slip(slip)
        if not verdict.ok:
            raise ValueError(
                f"pack slip {slip.get('profile_id')!r} is invalid: "
                + "; ".join(verdict.errors)
            )
    for creature in creatures:
        verdict = validate_grid(creature)
        if not verdict.ok:
            raise ValueError(
                f"pack creature {creature.get('grid_id')!r} is "
                "invalid: " + "; ".join(verdict.errors)
            )
    return {
        "pack_format": PACK_FORMAT,
        "pack_id": pack_id,
        "title": title,
        "provenance": dict(provenance),
        "slips": json.loads(json.dumps(slips)),
        "creatures": json.loads(json.dumps(creatures)),
    }


def write_pack(pack: dict, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(pack, indent=2) + "\n", encoding="utf-8"
    )
    return path


def load_pack(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def import_pack(keeper_dir: str | Path, path: str | Path) -> dict:
    """Judge and stage a pack's contents (per-item verdicts)."""
    keeper_dir = Path(keeper_dir)
    try:
        pack = load_pack(path)
    except (OSError, json.JSONDecodeError) as error:
        return {
            "ok": False,
            "violations": [f"unreadable pack file: {error}"],
        }
    if pack.get("pack_format") != PACK_FORMAT:
        return {
            "ok": False,
            "violations": [
                f"not a {PACK_FORMAT} file: "
                f"{pack.get('pack_format')!r}"
            ],
        }

    slip_reports: list[dict] = []
    for index, slip in enumerate(pack.get("slips") or []):
        verdict = validate_slip(slip)
        entry = {
            "profile_id": slip.get("profile_id"),
            "ok": verdict.ok,
            "violations": list(verdict.errors),
        }
        if verdict.ok:
            name = slip.get("profile_id") or f"slip_{index}"
            target = (
                keeper_dir / "covenants" / f"pack_{pack['pack_id']}_{name}.json"
            )
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                json.dumps(slip, indent=2) + "\n", encoding="utf-8"
            )
            entry["staged"] = target.name
        slip_reports.append(entry)

    creature_reports: list[dict] = []
    for creature in pack.get("creatures") or []:
        verdict = validate_grid(creature)
        entry = {
            "grid_id": creature.get("grid_id"),
            "ok": verdict.ok,
            "violations": list(verdict.errors),
        }
        if verdict.ok:
            target = (
                keeper_dir
                / "released"
                / f"pack_{pack['pack_id']}_{creature['grid_id']}.json"
            )
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                json.dumps(creature, indent=2) + "\n",
                encoding="utf-8",
            )
            entry["staged"] = target.name
        creature_reports.append(entry)

    return {
        "ok": True,
        "pack_id": pack["pack_id"],
        "title": pack.get("title"),
        "provenance": pack.get("provenance"),
        "slips": slip_reports,
        "creatures": creature_reports,
    }
