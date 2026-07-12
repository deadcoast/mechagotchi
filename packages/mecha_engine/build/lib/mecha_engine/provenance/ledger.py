"""Provenance-ledger validation for the mecha_engine package surface.

Contract sources:

- research/package_specs/mecha_engine_provenance_contract_gate.md
  ("Ledger Acceptance", "Compliance Model")
- research/asset_provenance/ledger.schema.md (required fields and field
  rules)
- research/package_specs/mecha_engine_module_interfaces.md ("provenance")

Verbatim semantic port of the Stage 0 research ledger validator (the
asset_pipeline lab): the same required-field roster, review-status set,
SPDX policy, included-path existence and hash-match checks, inclusion and
review-status policy, the noncommercial-core rejection, the share-alike /
copyleft decision-record gate, and the attribution-text requirement —
with identical error and warning message strings. Validation never
mutates the ledger, performs no writes, and returns a JSON-serializable
``ok`` / ``errors`` / ``warnings`` / ``summary`` result.

This is a deterministic policy gate for research and package promotion,
not legal review and not repository-wide REUSE compliance (contract gate,
"Compliance Model").
"""

from __future__ import annotations

from pathlib import Path

from .hashing import hash_included_path
from .spdx import KNOWN_SPDX_IDS, parse_spdx_expression

# research/asset_provenance/ledger.schema.md, "Required Fields".
REQUIRED_FIELDS: tuple[str, ...] = (
    "asset_id",
    "title",
    "asset_type",
    "creator",
    "source",
    "source_url",
    "download_date",
    "license",
    "spdx_id",
    "spdx_expression",
    "license_url",
    "derivative_of",
    "modifications",
    "hash_algorithm",
    "hash",
    "included_in_repo",
    "included_path",
    "shipping_scope",
    "commercial_allowed",
    "redistribution_allowed",
    "share_alike_required",
    "attribution_required",
    "attribution_text",
    "review_status",
    "reviewer",
    "decision_record",
    "notes",
)

REVIEW_STATUSES: frozenset[str] = frozenset(
    {
        "unreviewed",
        "approved",
        "rejected",
        "reference_only",
        "needs_legal_review",
    }
)

# Ledger schema version pinned until a schema migration gate exists.
LEDGER_VERSION = "0.1.0"


def validate_ledger(ledger: dict, repo_root: str | Path) -> dict:
    """Validate a provenance ledger against the Stage 0 policy gate.

    ``repo_root`` anchors the ledger's repo-relative ``included_path``
    strings for existence and hash verification.
    """
    repo_root = Path(repo_root)
    errors: list[str] = []
    warnings: list[str] = []
    assets = ledger.get("assets", [])
    if ledger.get("ledger_version") != LEDGER_VERSION:
        errors.append("ledger_version must be 0.1.0")
    if not isinstance(assets, list) or not assets:
        errors.append("assets must be a non-empty array")
        assets = []

    seen_ids: set[str] = set()
    for index, entry in enumerate(assets):
        prefix = f"asset[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix} must be an object")
            continue
        _validate_entry(entry, repo_root, seen_ids, errors, warnings)

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "asset_count": len(assets),
            "included_count": sum(
                1 for entry in assets if isinstance(entry, dict) and entry.get("included_in_repo") is True
            ),
            "reference_only_count": sum(
                1 for entry in assets if isinstance(entry, dict) and entry.get("review_status") == "reference_only"
            ),
            "attribution_required_count": sum(
                1 for entry in assets if isinstance(entry, dict) and entry.get("attribution_required") is True
            ),
        },
    }


def _validate_entry(
    entry: dict,
    repo_root: Path,
    seen_ids: set[str],
    errors: list[str],
    warnings: list[str],
) -> None:
    asset_id = entry.get("asset_id", "<missing>")
    for field in REQUIRED_FIELDS:
        if field not in entry:
            errors.append(f"{asset_id}: missing required field {field}")

    if asset_id in seen_ids:
        errors.append(f"{asset_id}: duplicate asset_id")
    seen_ids.add(asset_id)

    if entry.get("review_status") not in REVIEW_STATUSES:
        errors.append(f"{asset_id}: invalid review_status {entry.get('review_status')}")

    if entry.get("spdx_id") not in KNOWN_SPDX_IDS:
        errors.append(f"{asset_id}: unknown or unsupported SPDX identifier {entry.get('spdx_id')}")
    expression = str(entry.get("spdx_expression", entry.get("spdx_id", "")))
    parsed_expression = parse_spdx_expression(expression)
    if not parsed_expression["ok"]:
        for error in parsed_expression["errors"]:
            errors.append(f"{asset_id}: {error}")
    if parsed_expression["ok"] and entry.get("spdx_id") not in parsed_expression["license_ids"]:
        errors.append(f"{asset_id}: spdx_id must appear in spdx_expression")

    included = entry.get("included_in_repo") is True
    if included:
        included_path = entry.get("included_path", "")
        if not included_path:
            errors.append(f"{asset_id}: included asset missing included_path")
        else:
            path = repo_root / included_path
            if not path.exists():
                errors.append(f"{asset_id}: included path does not exist: {included_path}")
            else:
                actual = hash_included_path(path)
                if entry.get("hash_algorithm") != actual["hash_algorithm"]:
                    errors.append(f"{asset_id}: included asset hash algorithm mismatch")
                if not entry.get("hash"):
                    errors.append(f"{asset_id}: included asset missing hash")
                elif entry.get("hash") != actual["hash"]:
                    errors.append(f"{asset_id}: included asset hash mismatch")
        if entry.get("review_status") not in {"approved", "needs_legal_review"}:
            errors.append(f"{asset_id}: included asset must be approved or needs_legal_review")
    else:
        if entry.get("included_path"):
            errors.append(f"{asset_id}: excluded asset must not have included_path")
        if entry.get("hash"):
            warnings.append(f"{asset_id}: excluded asset hash is ignored")
        if entry.get("review_status") != "reference_only":
            warnings.append(f"{asset_id}: excluded asset is not marked reference_only")

    if entry.get("source") == "external" and included and entry.get("review_status") != "approved":
        errors.append(f"{asset_id}: included external asset must be approved")

    if entry.get("commercial_allowed") is False and entry.get("shipping_scope") == "core":
        errors.append(f"{asset_id}: noncommercial asset cannot be core")

    expression_is_copyleft = parsed_expression["contains_copyleft"]
    needs_decision_record = (
        entry.get("included_in_repo") is True
        and (entry.get("share_alike_required") is True or expression_is_copyleft)
    )
    if needs_decision_record and not entry.get("decision_record"):
        errors.append(f"{asset_id}: share-alike or copyleft asset requires decision_record")

    if entry.get("share_alike_required") is True and entry.get("shipping_scope") == "core":
        errors.append(f"{asset_id}: share-alike asset cannot be core without decision record")

    if entry.get("attribution_required") is True and not entry.get("attribution_text"):
        errors.append(f"{asset_id}: attribution required but attribution_text is empty")
