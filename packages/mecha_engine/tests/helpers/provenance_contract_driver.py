"""Provenance contract probe driver executed against the package surface.

Traceability: research/package_specs/mecha_engine_provenance_contract_gate.md
("Required Public Surface", "Ledger Acceptance", "SPDX Expression
Acceptance", "Hash Acceptance", "CI Report Acceptance", "Attribution
Manifest Acceptance", "Negative Checks"),
research/package_specs/mecha_engine_contract_traceability_matrix.md
("Provenance Test Obligations"), and
research/package_specs/mecha_engine_property_negative_test_strategy.md (P6
provenance and license strictness, P8 boundary hygiene, and the lowercase
SPDX operator metamorphic check).
``tests/test_provenance_contract.py`` launches this script in a subprocess
whose PYTHONPATH points at the package ``src`` directory (the same
documented import mechanics as ``tests/test_package_imports.py``), so every
probe exercises ``mecha_engine.provenance`` — never repository-root or
research lab modules — and the test module itself never mutates the
interpreter module search path.

The driver prints a single JSON report on stdout; the unittest module
asserts on it. Fixtures are the frozen Stage 0 provenance artifacts fixed
by the test fixture manifest and P6: ``data/asset_provenance/ledger.json``
(plus the committed ``validation_report.json``,
``provenance_ci_report.json``, and ``attribution_manifest.json`` oracles)
and the committed included paths the ledger references
(``data/seed_grids``, ``data/cubff_transducer/synthetic_snapshots.json``,
``data/workshop_editor/workshop_export_stage0.json``). Fault-injected
ledgers are deep-copied single-fault derivations; hash property probes use
``tempfile`` trees. Every fixture read is read-only: the driver snapshots
``data/`` and the package tree and re-digests the five committed
``data/asset_provenance`` artifacts to prove no probe wrote anything.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

import mecha_engine.provenance as provenance_module
from mecha_engine.provenance import (
    build_ci_report,
    generate_attribution_manifest,
    hash_included_path,
    parse_spdx_expression,
    validate_ledger,
)


EXPECTED_PUBLIC_SURFACE = [
    "build_ci_report",
    "generate_attribution_manifest",
    "hash_included_path",
    "parse_spdx_expression",
    "validate_ledger",
]
# Lab-only names the package surface must not inherit (contract gate,
# "Required Public Surface" and "Negative Checks").
LAB_ONLY_NAMES = [
    "build_provenance_ci_report",
    "build_stage0_ledger",
    "write_stage0_artifacts",
]

ACCEPTED_EXPRESSIONS = [
    "MIT",
    "Apache-2.0+",
    "CC-BY-SA-4.0",
    "LicenseRef-Custom-Asset",
    "DocumentRef-vendor:LicenseRef-pack",
    "MIT OR Apache-2.0",
    "MIT AND Apache-2.0",
    "GPL-2.0-or-later WITH Autoconf-exception-3.0",
    "(MIT OR Apache-2.0) AND (GPL-2.0-or-later WITH Autoconf-exception-3.0)"
    " AND LicenseRef-Mechagotchi-Internal-Research",
]
REJECTED_EXPRESSIONS = {
    "unknown_license_id": "MadeUp-1.0",
    "unknown_exception_id": "MIT WITH Fake-exception-1.0",
    "lowercase_or": "MIT or Apache-2.0",
    "lowercase_and": "MIT and Apache-2.0",
    "lowercase_with": "MIT with Autoconf-exception-3.0",
    "missing_closing_parenthesis": "(MIT",
    "unbalanced_closing_parenthesis": "MIT)",
    "dangling_operator": "MIT OR",
    "leading_operator": "AND MIT",
    "empty_expression": "",
    "whitespace_expression": "   ",
    "invalid_characters": "MIT && Apache-2.0",
    "compound_with_left_operand": "(MIT OR Apache-2.0) WITH Autoconf-exception-3.0",
}
COPYLEFT_IDS = [
    "CC-BY-SA-4.0",
    "GPL-2.0-only",
    "GPL-2.0-or-later",
    "GPL-3.0-or-later",
]
NON_COPYLEFT_IDS = ["MIT", "Apache-2.0", "CC0-1.0", "LicenseRef-Reference-Only"]

SHA256_OF_NOTHING = hashlib.sha256().hexdigest()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _json_roundtrip(payload) -> bool:
    try:
        return json.loads(json.dumps(payload)) == payload
    except (TypeError, ValueError):
        return False


def _asset_by_id(ledger: dict, asset_id: str) -> dict:
    return next(
        entry for entry in ledger["assets"] if entry["asset_id"] == asset_id
    )


def _snapshot_files(directory: Path) -> set[str]:
    if not directory.exists():
        return set()
    return {
        path.relative_to(directory).as_posix()
        for path in directory.rglob("*")
        if path.is_file()
    }


def _digest_directory_files(directory: Path) -> dict:
    return {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.iterdir())
        if path.is_file()
    }


# -- Contracted formula oracle (restated from the contract gate) -------------


def _oracle_tree_hash(directory: Path) -> str:
    """Restated sha256-tree contract, built independently as one byte stream:
    for each child file, its POSIX path relative to the hashed directory and
    its sha256 content digest, NUL-separated. Child order restates the
    corrected contract's case-sensitive relative POSIX-string order
    (DR 0061); the lab also pins an independently enumerated mixed-case corpus."""
    stream = bytearray()
    for child in sorted(
        (item for item in directory.rglob("*") if item.is_file()),
        key=lambda item: item.relative_to(directory).as_posix(),
    ):
        stream += child.relative_to(directory).as_posix().encode("utf-8")
        stream += b"\0"
        stream += hashlib.sha256(child.read_bytes()).hexdigest().encode("ascii")
        stream += b"\0"
    return hashlib.sha256(bytes(stream)).hexdigest()


# -- Probes ------------------------------------------------------------------


def probe_surface() -> dict:
    public_names = sorted(
        name for name in dir(provenance_module) if not name.startswith("_")
    )
    return {
        "public_all": sorted(provenance_module.__all__),
        "lab_only_names_present": [
            name for name in LAB_ONLY_NAMES if hasattr(provenance_module, name)
        ],
        "callable_surface": [
            name
            for name in EXPECTED_PUBLIC_SURFACE
            if callable(getattr(provenance_module, name, None))
        ],
        "public_names": public_names,
    }


def probe_spdx() -> dict:
    accepted = {}
    sorted_outputs = True
    for expression in ACCEPTED_EXPRESSIONS:
        parsed = parse_spdx_expression(expression)
        accepted[expression] = {
            "ok": parsed["ok"],
            "license_ids": parsed["license_ids"],
            "exception_ids": parsed["exception_ids"],
            "operators": parsed["operators"],
            "contains_copyleft": parsed["contains_copyleft"],
            "errors": parsed["errors"],
        }
        for key in ["license_ids", "exception_ids", "operators"]:
            if parsed[key] != sorted(parsed[key]):
                sorted_outputs = False

    rejected = {
        name: {
            "expression": expression,
            "ok": parse_spdx_expression(expression)["ok"],
            "errors": parse_spdx_expression(expression)["errors"],
        }
        for name, expression in REJECTED_EXPRESSIONS.items()
    }
    non_string = parse_spdx_expression(None)  # type: ignore[arg-type]

    sample = parse_spdx_expression(ACCEPTED_EXPRESSIONS[-1])
    return {
        "accepted": accepted,
        "rejected": rejected,
        "sorted_outputs": sorted_outputs,
        "result_keys": sorted(sample),
        "deterministic": sample == parse_spdx_expression(ACCEPTED_EXPRESSIONS[-1]),
        "json_roundtrip": _json_roundtrip(sample),
        "non_string_rejected": {
            "ok": non_string["ok"],
            "errors": non_string["errors"],
        },
        "copyleft_flags": {
            identifier: parse_spdx_expression(identifier)["contains_copyleft"]
            for identifier in COPYLEFT_IDS + NON_COPYLEFT_IDS
        },
    }


def probe_hashes(repo_root: Path, ledger: dict) -> dict:
    file_asset = _asset_by_id(ledger, "workshop_editor_stage0_export")
    second_file_asset = _asset_by_id(ledger, "cubff_synthetic_snapshot_corpus_stage0")
    directory_asset = _asset_by_id(ledger, "internal_seed_grid_corpus_v1")

    file_path = repo_root / file_asset["included_path"]
    file_hash = hash_included_path(file_path)
    file_oracle = hashlib.sha256(file_path.read_bytes()).hexdigest()
    directory_path = repo_root / directory_asset["included_path"]
    directory_hash = hash_included_path(directory_path)

    with tempfile.TemporaryDirectory() as temp_dir:
        scratch = Path(temp_dir)
        (scratch / "base").mkdir()
        (scratch / "base" / "b.txt").write_bytes(b"beta")
        (scratch / "base" / "a.txt").write_bytes(b"alpha")
        base_hash = hash_included_path(scratch / "base")["hash"]

        # Same file bytes under a different relative name.
        (scratch / "renamed").mkdir()
        (scratch / "renamed" / "b.txt").write_bytes(b"beta")
        (scratch / "renamed" / "c.txt").write_bytes(b"alpha")
        renamed_hash = hash_included_path(scratch / "renamed")["hash"]

        # Same relative names, one changed byte payload.
        (scratch / "edited").mkdir()
        (scratch / "edited" / "b.txt").write_bytes(b"beta")
        (scratch / "edited" / "a.txt").write_bytes(b"ALPHA")
        edited_hash = hash_included_path(scratch / "edited")["hash"]

        # Same file bytes nested one directory deeper.
        (scratch / "nested").mkdir()
        (scratch / "nested" / "b.txt").write_bytes(b"beta")
        (scratch / "nested" / "sub").mkdir()
        (scratch / "nested" / "sub" / "a.txt").write_bytes(b"alpha")
        nested_hash = hash_included_path(scratch / "nested")["hash"]

        # Same tree written in the opposite creation order.
        (scratch / "reordered").mkdir()
        (scratch / "reordered" / "a.txt").write_bytes(b"alpha")
        (scratch / "reordered" / "b.txt").write_bytes(b"beta")
        reordered_hash = hash_included_path(scratch / "reordered")["hash"]

        (scratch / "empty").mkdir()
        empty_hash = hash_included_path(scratch / "empty")

        try:
            hash_included_path(scratch / "absent.json")
            missing_exception = None
        except Exception as error:
            missing_exception = type(error).__name__

    return {
        "file": {
            "hash_algorithm": file_hash["hash_algorithm"],
            "hash_is_64_hex": len(file_hash["hash"]) == 64
            and all(char in "0123456789abcdef" for char in file_hash["hash"]),
            "matches_sha256_oracle": file_hash["hash"] == file_oracle,
            "matches_committed_ledger_hash": file_hash == {
                "hash_algorithm": file_asset["hash_algorithm"],
                "hash": file_asset["hash"],
            },
            "second_file_matches_committed_ledger_hash": hash_included_path(
                repo_root / second_file_asset["included_path"]
            )
            == {
                "hash_algorithm": second_file_asset["hash_algorithm"],
                "hash": second_file_asset["hash"],
            },
            "str_and_path_equal": hash_included_path(str(file_path)) == file_hash,
            "repeat_equal": hash_included_path(file_path) == file_hash,
        },
        "directory": {
            "hash_algorithm": directory_hash["hash_algorithm"],
            "hash_is_64_hex": len(directory_hash["hash"]) == 64
            and all(char in "0123456789abcdef" for char in directory_hash["hash"]),
            "matches_committed_ledger_hash": directory_hash == {
                "hash_algorithm": directory_asset["hash_algorithm"],
                "hash": directory_asset["hash"],
            },
            "matches_tree_oracle": directory_hash["hash"]
            == _oracle_tree_hash(directory_path),
            "repeat_equal": hash_included_path(directory_path) == directory_hash,
        },
        "properties": {
            "rename_changes_hash": renamed_hash != base_hash,
            "content_changes_hash": edited_hash != base_hash,
            "nesting_changes_hash": nested_hash != base_hash,
            "creation_order_independent": reordered_hash == base_hash,
            "empty_directory_algorithm": empty_hash["hash_algorithm"],
            "empty_directory_hash_is_sha256_of_nothing": empty_hash["hash"]
            == SHA256_OF_NOTHING,
        },
        "missing_path_exception": missing_exception,
    }


def probe_ledger_valid(repo_root: Path, ledger: dict) -> dict:
    committed_validation = _load(
        repo_root / "data" / "asset_provenance" / "validation_report.json"
    )
    pristine = deepcopy(ledger)
    result = validate_ledger(ledger, repo_root)
    repeat = validate_ledger(ledger, repo_root)
    via_str_root = validate_ledger(ledger, str(repo_root))
    return {
        "ok": result["ok"],
        "errors": result["errors"],
        "warnings": result["warnings"],
        "summary": result["summary"],
        "result_keys": sorted(result),
        "matches_committed_validation_report": result == committed_validation,
        "deterministic": result == repeat,
        "repo_root_str_equivalent": result == via_str_root,
        "json_roundtrip": _json_roundtrip(result),
        "input_mutated": ledger != pristine,
    }


def _fault_ledgers(repo_root: Path, ledger: dict) -> dict:
    """Single-fault ledger derivations (P6): one policy violation each."""
    faults: dict[str, dict] = {}

    def derive(name: str, mutate) -> None:
        variant = deepcopy(ledger)
        mutate(variant)
        faults[name] = variant

    derive("wrong_ledger_version", lambda l: l.update(ledger_version="0.2.0"))
    derive("empty_assets", lambda l: l.update(assets=[]))
    derive("assets_not_a_list", lambda l: l.update(assets="not-a-list"))
    derive("missing_required_field", lambda l: l["assets"][0].pop("notes"))
    derive(
        "duplicate_asset_id",
        lambda l: l["assets"].append(deepcopy(l["assets"][0])),
    )
    derive(
        "invalid_review_status",
        lambda l: l["assets"][0].update(review_status="looks_fine"),
    )
    derive(
        "unknown_spdx_id",
        lambda l: l["assets"][3].update(
            spdx_id="MadeUp-1.0", spdx_expression="MadeUp-1.0"
        ),
    )
    derive(
        "spdx_id_not_in_expression",
        lambda l: l["assets"][3].update(spdx_expression="MIT"),
    )
    derive(
        "lowercase_operator_expression",
        lambda l: l["assets"][3].update(spdx_expression="Apache-2.0 or MIT"),
    )
    derive(
        "included_missing_path", lambda l: l["assets"][0].update(included_path="")
    )
    derive(
        "included_path_absent",
        lambda l: l["assets"][0].update(
            included_path="data/asset_provenance/absent_fixture.json"
        ),
    )
    derive(
        "hash_algorithm_mismatch",
        lambda l: l["assets"][1].update(hash_algorithm="sha256-tree"),
    )
    derive("included_missing_hash", lambda l: l["assets"][1].update(hash=""))
    derive(
        "stale_included_hash", lambda l: l["assets"][1].update(hash="0" * 64)
    )
    derive(
        "included_unreviewed",
        lambda l: l["assets"][0].update(review_status="unreviewed"),
    )
    derive(
        "excluded_with_included_path",
        lambda l: l["assets"][3].update(included_path="data/seed_grids"),
    )
    derive(
        "excluded_with_hash_warns", lambda l: l["assets"][3].update(hash="a" * 64)
    )
    derive(
        "excluded_not_reference_only_warns",
        lambda l: l["assets"][3].update(review_status="approved"),
    )
    derive("noncommercial_core", lambda l: l["assets"][0].update(
        commercial_allowed=False, shipping_scope="core"
    ))
    derive(
        "included_copyleft_without_decision_record",
        lambda l: l["assets"][2].update(
            spdx_id="CC-BY-SA-4.0", spdx_expression="CC-BY-SA-4.0"
        ),
    )
    derive(
        "share_alike_core",
        lambda l: l["assets"][0].update(
            share_alike_required=True, shipping_scope="core"
        ),
    )
    derive(
        "attribution_text_missing",
        lambda l: l["assets"][3].update(attribution_text=""),
    )
    derive("non_object_asset", lambda l: l["assets"].append("not-an-asset"))

    included_external = deepcopy(ledger)
    entry = included_external["assets"][3]
    entry.update(
        included_in_repo=True,
        included_path="data/workshop_editor/workshop_export_stage0.json",
        shipping_scope="research",
        **hash_included_path(
            repo_root / "data/workshop_editor/workshop_export_stage0.json"
        ),
        review_status="needs_legal_review",
    )
    faults["included_external_not_approved"] = included_external
    return faults


def probe_ledger_faults(repo_root: Path, ledger: dict) -> dict:
    results = {}
    for name, variant in _fault_ledgers(repo_root, ledger).items():
        pristine = deepcopy(variant)
        outcome = validate_ledger(variant, repo_root)
        results[name] = {
            "ok": outcome["ok"],
            "errors": outcome["errors"],
            "warnings": outcome["warnings"],
            "input_mutated": variant != pristine,
        }

    # Positive controls: the same policy shapes pass once the required
    # metadata exists.
    with_decision_record = deepcopy(ledger)
    with_decision_record["assets"][2].update(
        spdx_id="CC-BY-SA-4.0",
        spdx_expression="CC-BY-SA-4.0",
        share_alike_required=True,
        decision_record="research/decision_records/0004-mecha-engine-package-scaffold.md",
    )
    decision_outcome = validate_ledger(with_decision_record, repo_root)

    approved_external = deepcopy(ledger)
    entry = approved_external["assets"][3]
    entry.update(
        included_in_repo=True,
        included_path="data/workshop_editor/workshop_export_stage0.json",
        shipping_scope="research",
        **hash_included_path(
            repo_root / "data/workshop_editor/workshop_export_stage0.json"
        ),
        review_status="approved",
    )
    approved_outcome = validate_ledger(approved_external, repo_root)

    results["positive_controls"] = {
        "decision_record_clears_gate": (
            decision_outcome["ok"]
            and not any(
                "requires decision_record" in error
                for error in decision_outcome["errors"]
            )
        ),
        "approved_external_included_ok": approved_outcome["ok"],
    }
    return results


def probe_ci_report(repo_root: Path, ledger: dict) -> dict:
    committed_report = _load(
        repo_root / "data" / "asset_provenance" / "provenance_ci_report.json"
    )
    pristine = deepcopy(ledger)
    report = build_ci_report(ledger, repo_root)
    repeat = build_ci_report(ledger, repo_root)

    faults = _fault_ledgers(repo_root, ledger)
    stale = build_ci_report(faults["stale_included_hash"], repo_root)
    missing_record = build_ci_report(
        faults["included_copyleft_without_decision_record"], repo_root
    )
    lowercase = build_ci_report(faults["lowercase_operator_expression"], repo_root)

    no_expression = deepcopy(ledger)
    del no_expression["assets"][4]["spdx_expression"]
    fallback = build_ci_report(no_expression, repo_root)
    fallback_result = fallback["spdx_results"][4]

    return {
        "report_keys": sorted(report),
        "checks_keys": sorted(report["checks"]),
        "spdx_summary_keys": sorted(report["spdx_summary"]),
        "report_version": report["report_version"],
        "generated_date_echoes_ledger": report["generated_date"]
        == ledger["generated_date"],
        "clean_ok": report["ok"],
        "clean_checks": report["checks"],
        "spdx_summary": report["spdx_summary"],
        "matches_committed_report": report == committed_report,
        "spdx_results_align_with_assets": [
            result["asset_id"] for result in report["spdx_results"]
        ]
        == [entry["asset_id"] for entry in ledger["assets"]],
        "stale_hash_report": {
            "ok": stale["ok"],
            "checks": stale["checks"],
            "hash_error_present": any(
                "hash mismatch" in error for error in stale["errors"]
            ),
        },
        "missing_decision_record_report": {
            "ok": missing_record["ok"],
            "checks": missing_record["checks"],
        },
        "lowercase_operator_report": {
            "ok": lowercase["ok"],
            "checks": lowercase["checks"],
            "expression_error_prefixed_with_asset_id": any(
                error.startswith("piskel_reference_only: ")
                for error in lowercase["errors"]
            ),
            "parsed_expression_count": lowercase["spdx_summary"][
                "parsed_expression_count"
            ],
            "expression_count": lowercase["spdx_summary"]["expression_count"],
        },
        "missing_expression_falls_back_to_spdx_id": (
            fallback_result["expression"] == no_expression["assets"][4]["spdx_id"]
            and fallback_result["ok"]
        ),
        "deterministic": report == repeat,
        "json_roundtrip": _json_roundtrip(report),
        "input_mutated": ledger != pristine,
    }


def probe_attribution(repo_root: Path, ledger: dict) -> dict:
    committed_manifest = _load(
        repo_root / "data" / "asset_provenance" / "attribution_manifest.json"
    )
    pristine = deepcopy(ledger)
    manifest = generate_attribution_manifest(ledger)
    repeat = generate_attribution_manifest(ledger)

    required_ids = sorted(
        entry["asset_id"]
        for entry in ledger["assets"]
        if entry.get("attribution_required") is True
    )
    not_required_ids = {
        entry["asset_id"]
        for entry in ledger["assets"]
        if entry.get("attribution_required") is not True
    }
    manifest_ids = sorted(entry["asset_id"] for entry in manifest["attributions"])

    flipped = deepcopy(ledger)
    flipped["assets"][0]["attribution_required"] = True
    flipped["assets"][0]["attribution_text"] = "Driver attribution probe"
    flipped_manifest = generate_attribution_manifest(flipped)

    return {
        "manifest_keys": sorted(manifest),
        "manifest_version": manifest["manifest_version"],
        "generated_date_echoes_ledger": manifest["generated_date"]
        == ledger["generated_date"],
        "matches_committed_manifest": manifest == committed_manifest,
        "asset_ids": manifest_ids,
        "only_attribution_required": manifest_ids == required_ids,
        "internal_assets_excluded": not (set(manifest_ids) & not_required_ids),
        "entry_keys": sorted(manifest["attributions"][0])
        if manifest["attributions"]
        else [],
        "attribution_texts_nonempty": all(
            entry["attribution_text"] for entry in manifest["attributions"]
        ),
        "reference_only_entries_have_no_included_path": all(
            entry["included_path"] == ""
            for entry in manifest["attributions"]
            if entry["included_in_repo"] is False
        ),
        "flipped_asset_included": any(
            entry["asset_id"] == flipped["assets"][0]["asset_id"]
            for entry in flipped_manifest["attributions"]
        ),
        "deterministic": manifest == repeat,
        "json_roundtrip": _json_roundtrip(manifest),
        "input_mutated": ledger != pristine,
    }


def probe_loaded_lab_modules() -> list[str]:
    lab_root = "la" "bs"
    return sorted(
        name
        for name in sys.modules
        if name == lab_root or name.startswith(lab_root + ".")
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()

    provenance_dir = repo_root / "data" / "asset_provenance"
    data_before = _snapshot_files(repo_root / "data")
    package_before = _snapshot_files(repo_root / "packages")
    artifacts_before = _digest_directory_files(provenance_dir)

    ledger = _load(provenance_dir / "ledger.json")
    ledger_pristine = deepcopy(ledger)

    report = {
        "surface": probe_surface(),
        "spdx": probe_spdx(),
        "hashes": probe_hashes(repo_root, ledger),
        "ledger_valid": probe_ledger_valid(repo_root, ledger),
        "ledger_faults": probe_ledger_faults(repo_root, ledger),
        "ci_report": probe_ci_report(repo_root, ledger),
        "attribution": probe_attribution(repo_root, ledger),
        "fixtures_mutated": ledger != ledger_pristine,
        "lab_modules_loaded": probe_loaded_lab_modules(),
    }
    report["no_writes"] = {
        "new_data_files": sorted(_snapshot_files(repo_root / "data") - data_before),
        "new_package_files": sorted(
            _snapshot_files(repo_root / "packages") - package_before
        ),
        "asset_provenance_artifacts_unchanged": (
            _digest_directory_files(provenance_dir) == artifacts_before
        ),
    }
    json.dump(report, sys.stdout)


if __name__ == "__main__":
    main()
