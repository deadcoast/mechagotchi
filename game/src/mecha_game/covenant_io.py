"""SLIP import/export — the covenant is shareable (F15, MVP 0.3).

Export writes the ACTIVE covenant VERBATIM: it is already an
authority-validated SLIP (spends included), shareable as-is — the
zoo's file convention, no wrapper invented. Import passes two engine
gates before anything applies: the authority's validation
(`mecha_engine.slip.validate_slip`, refusals verbatim) and corpus
compatibility (`evolve`'s own rule — "no seed grid satisfies the SLIP
profile" — checked with the engine's `is_grid_aligned`); a refused
import applies NOTHING. An accepted import becomes the campaign's
NEW BASE covenant: a fresh species contract whose spend budget
recomputes from the Keeper's earned facts (spends re-apply by
choice, never silently).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from mecha_engine.slip import is_grid_aligned, validate_slip


def export_covenant(keeper_campaign, path: str | Path) -> Path:
    """Write the active covenant verbatim (backup-before-overwrite)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.with_suffix(".bak.json").write_text(
            path.read_text(encoding="utf-8"), encoding="utf-8"
        )
    path.write_text(
        json.dumps(keeper_campaign.campaign["slip_profile"], indent=2)
        + "\n",
        encoding="utf-8",
    )
    return path


def read_import_file(path: str | Path, *, expected_digest: str | None = None, with_bytes=False) -> tuple[dict, str] | tuple[dict, str, bytes]:
    """Read exactly the bytes previewed by a picker, never silently a replacement."""
    raw = Path(path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if expected_digest is not None and digest != expected_digest:
        raise ValueError("File changed since preview. F5 refresh before importing.")
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object.")
    return (value, digest, raw) if with_bytes else (value, digest)


def import_covenant(keeper_campaign, path: str | Path, *, expected_digest: str | None = None) -> dict:
    """Import a covenant through the engine's gates.

    Returns ``{"ok": True, "covenant": …, "aligned_seeds": n}`` or
    ``{"ok": False, "violations": […]}`` with nothing applied."""
    try:
        profile, _, raw = read_import_file(path, expected_digest=expected_digest, with_bytes=True)
    except (OSError, ValueError, UnicodeError) as error:
        return {
            "ok": False,
            "violations": [f"unreadable covenant file: {error}"],
        }
    try:
        verdict = validate_slip(profile)
    except (TypeError, ValueError, KeyError, AttributeError) as error:
        return {'ok': False, 'violations': [f'the authority could not read the covenant: {error}']}
    if not verdict.ok:
        return {
            "ok": False,
            "violations": [
                f"the authority rejects the covenant: {error}"
                for error in verdict.errors
            ],
        }
    aligned = sum(
        1
        for seed in keeper_campaign.inputs["seed_grids"]
        if is_grid_aligned(seed, profile).ok
    )
    if aligned == 0:
        return {
            "ok": False,
            "violations": [
                "no seed grid satisfies the SLIP profile — an era "
                "under this covenant could not begin (the engine's "
                "own rule)"
            ],
        }
    # The new species contract: base AND active covenant; the earned
    # budget recomputes from it, spends re-apply by choice.
    from mecha_game.execution import source_record
    keeper_campaign.base_covenant_source = source_record(raw, role='base_covenant',
        source_kind='imported_file', label=Path(path).name)
    keeper_campaign.base_profile = json.loads(json.dumps(profile))
    keeper_campaign.campaign["slip_profile"] = json.loads(
        json.dumps(profile)
    )
    return {"ok": True, "covenant": profile, "aligned_seeds": aligned}
