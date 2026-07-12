"""Provenance CI report and attribution manifest for mecha_engine.

Contract sources:

- research/package_specs/mecha_engine_provenance_contract_gate.md
  ("CI Report Acceptance", "Attribution Manifest Acceptance",
  "Required Public Surface")
- research/package_specs/mecha_engine_module_interfaces.md ("provenance")

``build_ci_report`` is the package-facing name for the Stage 0 lab
report builder (the lab-only name ``build_provenance_ci_report`` is
intentionally hidden: package callers must not inherit lab file names,
per the contract gate). Both functions are verbatim semantic ports of
the asset_pipeline lab: identical report/manifest shapes, identical
check derivations, identical field preservation. They are pure — no
writes, no input mutation — and their outputs are JSON-serializable.
Version strings stay pinned until a schema migration gate exists.
"""

from __future__ import annotations

from pathlib import Path

from .ledger import validate_ledger
from .spdx import parse_spdx_expression

# Pinned until a schema migration gate exists (contract gate acceptance).
REPORT_VERSION = "0.1.0"
MANIFEST_VERSION = "0.1.0"
# Stage 0 fallback date used when a ledger carries no generated_date
# (verbatim lab semantics; the committed Stage 0 ledger always carries one).
_STAGE0_GENERATED_DATE = "2026-05-12"


def build_ci_report(ledger: dict, repo_root: str | Path) -> dict:
    """Return the package-facing provenance CI report for a ledger.

    Combines ledger validation with per-asset SPDX expression parsing and
    exposes the four contracted checks: ``ledger_validation_ok``,
    ``spdx_expressions_ok``, ``included_hashes_ok``, and
    ``decision_record_gate_ok``.
    """
    validation = validate_ledger(ledger, repo_root)
    spdx_results: list[dict] = []
    expression_errors: list[str] = []
    license_ids: set[str] = set()
    exception_ids: set[str] = set()
    operators: set[str] = set()

    for index, entry in enumerate(ledger.get("assets", [])):
        if not isinstance(entry, dict):
            continue
        asset_id = entry.get("asset_id", f"asset[{index}]")
        expression = entry.get("spdx_expression", entry.get("spdx_id", ""))
        parsed = parse_spdx_expression(expression)
        spdx_results.append(
            {
                "asset_id": asset_id,
                "expression": expression,
                "ok": parsed["ok"],
                "license_ids": parsed["license_ids"],
                "exception_ids": parsed["exception_ids"],
                "operators": parsed["operators"],
                "contains_copyleft": parsed["contains_copyleft"],
                "errors": parsed["errors"],
            }
        )
        if not parsed["ok"]:
            for error in parsed["errors"]:
                expression_errors.append(f"{asset_id}: {error}")
        license_ids.update(parsed["license_ids"])
        exception_ids.update(parsed["exception_ids"])
        operators.update(parsed["operators"])

    # REUSE convention (audit T21): every license id covering an
    # INCLUDED asset must resolve to LICENSES/<id>.txt.
    included_license_ids: set[str] = set()
    for entry in ledger.get("assets", []):
        if isinstance(entry, dict) and entry.get("included_in_repo"):
            expression = entry.get("spdx_expression", entry.get("spdx_id", ""))
            included_license_ids.update(
                parse_spdx_expression(expression)["license_ids"]
            )
    reuse_errors = [
        f"REUSE: missing LICENSES/{license_id}.txt"
        for license_id in sorted(included_license_ids)
        if not (repo_root / "LICENSES" / f"{license_id}.txt").is_file()
    ]

    errors = list(validation["errors"]) + expression_errors + reuse_errors
    return {
        "report_version": REPORT_VERSION,
        "generated_date": ledger.get("generated_date", _STAGE0_GENERATED_DATE),
        "ok": not errors,
        "checks": {
            "ledger_validation_ok": validation["ok"],
            "spdx_expressions_ok": not expression_errors,
            "reuse_licenses_ok": not reuse_errors,
            "included_hashes_ok": not any("hash" in error for error in validation["errors"]),
            "decision_record_gate_ok": not any(
                "requires decision_record" in error for error in validation["errors"]
            ),
        },
        "errors": errors,
        "warnings": validation["warnings"],
        "validation": validation,
        "spdx_summary": {
            "expression_count": len(spdx_results),
            "parsed_expression_count": sum(1 for result in spdx_results if result["ok"]),
            "license_ids": sorted(license_ids),
            "exception_ids": sorted(exception_ids),
            "operators": sorted(operators),
        },
        "spdx_results": spdx_results,
    }


def generate_attribution_manifest(ledger: dict) -> dict:
    """Return the attribution manifest for a ledger.

    Includes only assets where ``attribution_required`` is true and
    preserves the contracted fields; internal assets that require no
    attribution stay excluded.
    """
    attributions: list[dict] = []
    for entry in ledger.get("assets", []):
        if entry.get("attribution_required") is True:
            attributions.append(
                {
                    "asset_id": entry["asset_id"],
                    "title": entry["title"],
                    "creator": entry["creator"],
                    "license": entry["license"],
                    "spdx_id": entry["spdx_id"],
                    "spdx_expression": entry["spdx_expression"],
                    "source_url": entry["source_url"],
                    "attribution_text": entry["attribution_text"],
                    "included_in_repo": entry["included_in_repo"],
                    "included_path": entry["included_path"],
                }
            )
    return {
        "manifest_version": MANIFEST_VERSION,
        "generated_date": ledger.get("generated_date", _STAGE0_GENERATED_DATE),
        "attributions": attributions,
    }
