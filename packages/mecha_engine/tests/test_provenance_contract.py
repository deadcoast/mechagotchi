"""Provenance contract tests for the mecha_engine package surface.

Traceability: research/package_specs/mecha_engine_provenance_contract_gate.md
("Required Public Surface", "Ledger Acceptance", "SPDX Expression
Acceptance", "Hash Acceptance", "CI Report Acceptance", "Attribution
Manifest Acceptance", "Negative Checks"),
research/package_specs/mecha_engine_contract_traceability_matrix.md
("Provenance Test Obligations"), and
research/package_specs/mecha_engine_property_negative_test_strategy.md (P6
provenance and license strictness, single-token SPDX mutations, altered
included hashes, P8 boundary hygiene, and the lowercase-operator
metamorphic check).

Import mechanics match ``tests/test_package_imports.py``,
``tests/test_genome_contract.py``, ``tests/test_generation_contract.py``,
``tests/test_lifecycle_contract.py``, and ``tests/test_archive_contract.py``:
the probes run in one ``python -B`` subprocess whose PYTHONPATH points at
this package's own ``src`` directory (standard src-layout semantics; an
installed package satisfies the same probe), executed by
``tests/helpers/provenance_contract_driver.py`` through
``mecha_engine.provenance`` only — provenance carries no dependency on any
other mecha_engine module. This module never mutates the interpreter
module search path and never points the subprocess at research lab
directories. Fixtures are the frozen Stage 0 provenance artifacts (P6):
``data/asset_provenance/ledger.json`` plus the committed validation
report, CI report, and attribution manifest as oracles, and the committed
included paths the ledger references. The lab-vs-package artifact parity
pin runs lab-side, in the asset_pipeline research lab's package parity
test, because it re-derives the Stage 0 ledger through the lab builder.
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACKAGE_ROOT.parents[1]
SRC_DIR = PACKAGE_ROOT / "src"
DRIVER = Path(__file__).resolve().parent / "helpers" / "provenance_contract_driver.py"

REQUIRED_PUBLIC_SURFACE = [
    "build_ci_report",
    "generate_attribution_manifest",
    "hash_included_path",
    "parse_spdx_expression",
    "validate_ledger",
]
REQUIRED_PARSE_RESULT_FIELDS = [
    "contains_copyleft",
    "errors",
    "exception_ids",
    "expression",
    "license_ids",
    "ok",
    "operators",
]
REQUIRED_VALIDATION_FIELDS = ["errors", "ok", "summary", "warnings"]
REQUIRED_REPORT_FIELDS = [
    "checks",
    "errors",
    "generated_date",
    "ok",
    "report_version",
    "spdx_results",
    "spdx_summary",
    "validation",
    "warnings",
]
REQUIRED_CHECKS = [
    "decision_record_gate_ok",
    "included_hashes_ok",
    "ledger_validation_ok",
    "spdx_expressions_ok",
]
REQUIRED_SPDX_SUMMARY_FIELDS = [
    "exception_ids",
    "expression_count",
    "license_ids",
    "operators",
    "parsed_expression_count",
]
REQUIRED_MANIFEST_ENTRY_FIELDS = [
    "asset_id",
    "attribution_text",
    "creator",
    "included_in_repo",
    "included_path",
    "license",
    "source_url",
    "spdx_expression",
    "spdx_id",
    "title",
]

# Stage 0 baseline (contract gate, "CI Report Acceptance" table).
STAGE0_SUMMARY = {
    "asset_count": 7,
    "included_count": 3,
    "reference_only_count": 4,
    "attribution_required_count": 3,
}
STAGE0_LICENSE_IDS = [
    "Apache-2.0",
    "GPL-2.0-only",
    "LicenseRef-Mechagotchi-Internal-Research",
    "LicenseRef-Reference-Only",
    "MIT",
]

# SPDX acceptance oracle (contract gate, "SPDX Expression Acceptance").
EXPECTED_ACCEPTED = {
    "MIT": {
        "license_ids": ["MIT"],
        "exception_ids": [],
        "operators": [],
        "contains_copyleft": False,
    },
    "Apache-2.0+": {
        "license_ids": ["Apache-2.0"],
        "exception_ids": [],
        "operators": [],
        "contains_copyleft": False,
    },
    "CC-BY-SA-4.0": {
        "license_ids": ["CC-BY-SA-4.0"],
        "exception_ids": [],
        "operators": [],
        "contains_copyleft": True,
    },
    "LicenseRef-Custom-Asset": {
        "license_ids": ["LicenseRef-Custom-Asset"],
        "exception_ids": [],
        "operators": [],
        "contains_copyleft": False,
    },
    "DocumentRef-vendor:LicenseRef-pack": {
        "license_ids": ["DocumentRef-vendor:LicenseRef-pack"],
        "exception_ids": [],
        "operators": [],
        "contains_copyleft": False,
    },
    "MIT OR Apache-2.0": {
        "license_ids": ["Apache-2.0", "MIT"],
        "exception_ids": [],
        "operators": ["OR"],
        "contains_copyleft": False,
    },
    "MIT AND Apache-2.0": {
        "license_ids": ["Apache-2.0", "MIT"],
        "exception_ids": [],
        "operators": ["AND"],
        "contains_copyleft": False,
    },
    "GPL-2.0-or-later WITH Autoconf-exception-3.0": {
        "license_ids": ["GPL-2.0-or-later"],
        "exception_ids": ["Autoconf-exception-3.0"],
        "operators": ["WITH"],
        "contains_copyleft": True,
    },
    "(MIT OR Apache-2.0) AND (GPL-2.0-or-later WITH Autoconf-exception-3.0)"
    " AND LicenseRef-Mechagotchi-Internal-Research": {
        "license_ids": [
            "Apache-2.0",
            "GPL-2.0-or-later",
            "LicenseRef-Mechagotchi-Internal-Research",
            "MIT",
        ],
        "exception_ids": ["Autoconf-exception-3.0"],
        "operators": ["AND", "OR", "WITH"],
        "contains_copyleft": True,
    },
}
EXPECTED_REJECTED_NEEDLES = {
    "unknown_license_id": "unknown SPDX license identifier MadeUp-1.0",
    "unknown_exception_id": "unknown SPDX exception identifier Fake-exception-1.0",
    "lowercase_or": "unexpected token or",
    "lowercase_and": "unexpected token and",
    "lowercase_with": "unexpected token with",
    "missing_closing_parenthesis": "missing closing parenthesis",
    "unbalanced_closing_parenthesis": "unexpected token )",
    "dangling_operator": "unexpected end of SPDX expression",
    "leading_operator": "unexpected token AND",
    "empty_expression": "SPDX expression is empty",
    "whitespace_expression": "SPDX expression is empty",
    "invalid_characters": "SPDX expression contains invalid characters or spacing",
    "compound_with_left_operand": "WITH left operand must be a simple license expression",
}

# Single-fault ledger oracle (P6): fault name -> expected error family.
EXPECTED_FAULT_ERROR_NEEDLES = {
    "wrong_ledger_version": "ledger_version must be 0.1.0",
    "empty_assets": "assets must be a non-empty array",
    "assets_not_a_list": "assets must be a non-empty array",
    "missing_required_field": "missing required field notes",
    "duplicate_asset_id": "duplicate asset_id",
    "invalid_review_status": "invalid review_status looks_fine",
    "unknown_spdx_id": "unknown or unsupported SPDX identifier MadeUp-1.0",
    "spdx_id_not_in_expression": "spdx_id must appear in spdx_expression",
    "lowercase_operator_expression": "unexpected token or",
    "included_missing_path": "included asset missing included_path",
    "included_path_absent": (
        "included path does not exist: data/asset_provenance/absent_fixture.json"
    ),
    "hash_algorithm_mismatch": "included asset hash algorithm mismatch",
    "included_missing_hash": "included asset missing hash",
    "stale_included_hash": "included asset hash mismatch",
    "included_unreviewed": "included asset must be approved or needs_legal_review",
    "excluded_with_included_path": "excluded asset must not have included_path",
    "included_external_not_approved": "included external asset must be approved",
    "noncommercial_core": "noncommercial asset cannot be core",
    "included_copyleft_without_decision_record": (
        "share-alike or copyleft asset requires decision_record"
    ),
    "share_alike_core": "share-alike asset cannot be core without decision record",
    "attribution_text_missing": "attribution required but attribution_text is empty",
    "non_object_asset": "asset[7] must be an object",
}
EXPECTED_FAULT_WARNING_NEEDLES = {
    "excluded_with_hash_warns": "excluded asset hash is ignored",
    "excluded_not_reference_only_warns": "excluded asset is not marked reference_only",
}


def _run_driver() -> dict:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(SRC_DIR) + (os.pathsep + existing if existing else "")
    result = subprocess.run(
        [sys.executable, "-B", str(DRIVER), "--repo-root", str(REPO_ROOT)],
        capture_output=True,
        text=True,
        env=env,
        cwd=PACKAGE_ROOT,
        timeout=300,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"provenance contract driver failed ({result.returncode}): {result.stderr}"
        )
    return json.loads(result.stdout)


class MechaEngineProvenanceContractTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = _run_driver()

    # -- Public surface -----------------------------------------------------

    def test_public_surface_is_the_contracted_five_functions(self):
        surface = self.report["surface"]
        self.assertEqual(REQUIRED_PUBLIC_SURFACE, surface["public_all"])
        self.assertEqual(REQUIRED_PUBLIC_SURFACE, surface["callable_surface"])

    def test_lab_only_names_are_not_inherited(self):
        # build_ci_report intentionally hides the lab-only name
        # build_provenance_ci_report; ledger authoring and artifact writing
        # stay lab-only surfaces.
        self.assertEqual([], self.report["surface"]["lab_only_names_present"])

    def test_provenance_surface_loads_no_lab_modules(self):
        self.assertEqual([], self.report["lab_modules_loaded"])

    # -- SPDX expression acceptance ------------------------------------------

    def test_supported_spdx_subset_is_accepted(self):
        for expression, expected in EXPECTED_ACCEPTED.items():
            with self.subTest(expression=expression):
                parsed = self.report["spdx"]["accepted"][expression]
                self.assertTrue(parsed["ok"], parsed["errors"])
                self.assertEqual([], parsed["errors"])
                self.assertEqual(expected["license_ids"], parsed["license_ids"])
                self.assertEqual(expected["exception_ids"], parsed["exception_ids"])
                self.assertEqual(expected["operators"], parsed["operators"])
                self.assertEqual(
                    expected["contains_copyleft"], parsed["contains_copyleft"]
                )

    def test_parse_result_reports_the_contracted_fields(self):
        self.assertEqual(REQUIRED_PARSE_RESULT_FIELDS, self.report["spdx"]["result_keys"])
        self.assertTrue(self.report["spdx"]["json_roundtrip"])

    def test_parse_outputs_are_sorted_and_deterministic(self):
        self.assertTrue(self.report["spdx"]["sorted_outputs"])
        self.assertTrue(self.report["spdx"]["deterministic"])

    def test_malformed_and_unknown_expressions_are_rejected(self):
        for name, needle in EXPECTED_REJECTED_NEEDLES.items():
            with self.subTest(fault=name):
                rejected = self.report["spdx"]["rejected"][name]
                self.assertFalse(rejected["ok"])
                self.assertIn(needle, "\n".join(rejected["errors"]))

    def test_lowercase_operators_stay_rejected_under_stage0_policy(self):
        # Metamorphic check pinned by the test strategy: lowercasing an SPDX
        # operator must reject until an explicit schema revision.
        for name in ["lowercase_or", "lowercase_and", "lowercase_with"]:
            with self.subTest(fault=name):
                self.assertFalse(self.report["spdx"]["rejected"][name]["ok"])

    def test_non_string_expression_is_rejected_not_thrown(self):
        non_string = self.report["spdx"]["non_string_rejected"]
        self.assertFalse(non_string["ok"])
        self.assertIn("SPDX expression is empty", "\n".join(non_string["errors"]))

    def test_copyleft_flag_tracks_the_known_copyleft_identifiers(self):
        flags = self.report["spdx"]["copyleft_flags"]
        for identifier in [
            "CC-BY-SA-4.0",
            "GPL-2.0-only",
            "GPL-2.0-or-later",
            "GPL-3.0-or-later",
        ]:
            self.assertTrue(flags[identifier], identifier)
        for identifier in ["MIT", "Apache-2.0", "CC0-1.0", "LicenseRef-Reference-Only"]:
            self.assertFalse(flags[identifier], identifier)

    # -- Hash acceptance -----------------------------------------------------

    def test_file_hashes_use_sha256_and_match_committed_stage0_hashes(self):
        file_report = self.report["hashes"]["file"]
        self.assertEqual("sha256", file_report["hash_algorithm"])
        self.assertTrue(file_report["hash_is_64_hex"])
        self.assertTrue(file_report["matches_sha256_oracle"])
        self.assertTrue(file_report["matches_committed_ledger_hash"])
        self.assertTrue(file_report["second_file_matches_committed_ledger_hash"])

    def test_directory_hashes_use_deterministic_sha256_tree(self):
        directory = self.report["hashes"]["directory"]
        self.assertEqual("sha256-tree", directory["hash_algorithm"])
        self.assertTrue(directory["hash_is_64_hex"])
        self.assertTrue(directory["matches_tree_oracle"])
        self.assertTrue(directory["repeat_equal"])

    def test_seed_grid_corpus_tree_hash_matches_the_committed_ledger(self):
        self.assertTrue(
            self.report["hashes"]["directory"]["matches_committed_ledger_hash"]
        )

    def test_tree_hash_covers_relative_names_and_child_digests(self):
        properties = self.report["hashes"]["properties"]
        self.assertTrue(properties["rename_changes_hash"])
        self.assertTrue(properties["content_changes_hash"])
        self.assertTrue(properties["nesting_changes_hash"])

    def test_tree_hash_is_independent_of_file_creation_order(self):
        properties = self.report["hashes"]["properties"]
        self.assertTrue(properties["creation_order_independent"])
        self.assertEqual("sha256-tree", properties["empty_directory_algorithm"])
        self.assertTrue(properties["empty_directory_hash_is_sha256_of_nothing"])

    def test_absent_paths_raise_file_not_found(self):
        self.assertEqual(
            "FileNotFoundError", self.report["hashes"]["missing_path_exception"]
        )

    def test_hash_accepts_str_and_path_equivalently(self):
        self.assertTrue(self.report["hashes"]["file"]["str_and_path_equal"])
        self.assertTrue(self.report["hashes"]["file"]["repeat_equal"])

    # -- Ledger acceptance ---------------------------------------------------

    def test_committed_stage0_ledger_validates_clean(self):
        valid = self.report["ledger_valid"]
        self.assertTrue(valid["ok"], valid["errors"])
        self.assertEqual([], valid["errors"])
        self.assertEqual([], valid["warnings"])
        self.assertEqual(STAGE0_SUMMARY, valid["summary"])

    def test_validation_result_reports_the_contracted_fields(self):
        valid = self.report["ledger_valid"]
        self.assertEqual(REQUIRED_VALIDATION_FIELDS, valid["result_keys"])
        self.assertTrue(valid["json_roundtrip"])

    def test_validation_reproduces_the_committed_validation_report(self):
        self.assertTrue(self.report["ledger_valid"]["matches_committed_validation_report"])

    def test_validation_is_deterministic_and_accepts_str_repo_root(self):
        valid = self.report["ledger_valid"]
        self.assertTrue(valid["deterministic"])
        self.assertTrue(valid["repo_root_str_equivalent"])

    def test_validation_never_mutates_the_ledger(self):
        self.assertFalse(self.report["ledger_valid"]["input_mutated"])
        self.assertFalse(self.report["fixtures_mutated"])
        for name, fault in self.report["ledger_faults"].items():
            if name == "positive_controls":
                continue
            with self.subTest(fault=name):
                self.assertFalse(fault["input_mutated"])

    def test_single_fault_ledgers_fail_for_the_intended_reason(self):
        for name, needle in EXPECTED_FAULT_ERROR_NEEDLES.items():
            with self.subTest(fault=name):
                fault = self.report["ledger_faults"][name]
                self.assertFalse(fault["ok"])
                self.assertIn(needle, "\n".join(fault["errors"]))

    def test_excluded_asset_anomalies_warn_without_failing(self):
        for name, needle in EXPECTED_FAULT_WARNING_NEEDLES.items():
            with self.subTest(fault=name):
                fault = self.report["ledger_faults"][name]
                self.assertTrue(fault["ok"], fault["errors"])
                self.assertIn(needle, "\n".join(fault["warnings"]))

    def test_decision_record_metadata_clears_the_share_alike_gate(self):
        controls = self.report["ledger_faults"]["positive_controls"]
        self.assertTrue(controls["decision_record_clears_gate"])
        self.assertTrue(controls["approved_external_included_ok"])

    # -- CI report acceptance --------------------------------------------------

    def test_ci_report_reports_the_contracted_fields_and_checks(self):
        ci_report = self.report["ci_report"]
        self.assertEqual(REQUIRED_REPORT_FIELDS, ci_report["report_keys"])
        self.assertEqual(REQUIRED_CHECKS, ci_report["checks_keys"])
        self.assertEqual(
            REQUIRED_SPDX_SUMMARY_FIELDS, ci_report["spdx_summary_keys"]
        )
        self.assertEqual("0.1.0", ci_report["report_version"])
        self.assertTrue(ci_report["generated_date_echoes_ledger"])

    def test_ci_report_reproduces_the_stage0_clean_checks(self):
        ci_report = self.report["ci_report"]
        self.assertTrue(ci_report["clean_ok"])
        self.assertEqual(
            {
                "ledger_validation_ok": True,
                "spdx_expressions_ok": True,
                "included_hashes_ok": True,
                "decision_record_gate_ok": True,
            },
            ci_report["clean_checks"],
        )
        self.assertEqual(
            {
                "expression_count": 7,
                "parsed_expression_count": 7,
                "license_ids": STAGE0_LICENSE_IDS,
                "exception_ids": [],
                "operators": [],
            },
            ci_report["spdx_summary"],
        )

    def test_ci_report_reproduces_the_committed_stage0_artifact(self):
        self.assertTrue(self.report["ci_report"]["matches_committed_report"])

    def test_spdx_results_align_with_ledger_assets(self):
        ci_report = self.report["ci_report"]
        self.assertTrue(ci_report["spdx_results_align_with_assets"])
        self.assertTrue(ci_report["missing_expression_falls_back_to_spdx_id"])

    def test_stale_included_hash_fails_the_hash_check(self):
        stale = self.report["ci_report"]["stale_hash_report"]
        self.assertFalse(stale["ok"])
        self.assertTrue(stale["hash_error_present"])
        self.assertEqual(
            {
                "ledger_validation_ok": False,
                "spdx_expressions_ok": True,
                "included_hashes_ok": False,
                "decision_record_gate_ok": True,
            },
            stale["checks"],
        )

    def test_missing_decision_record_fails_the_decision_record_gate(self):
        report = self.report["ci_report"]["missing_decision_record_report"]
        self.assertFalse(report["ok"])
        self.assertEqual(
            {
                "ledger_validation_ok": False,
                "spdx_expressions_ok": True,
                "included_hashes_ok": True,
                "decision_record_gate_ok": False,
            },
            report["checks"],
        )

    def test_lowercase_operator_expression_fails_the_spdx_check(self):
        report = self.report["ci_report"]["lowercase_operator_report"]
        self.assertFalse(report["ok"])
        self.assertFalse(report["checks"]["spdx_expressions_ok"])
        self.assertTrue(report["expression_error_prefixed_with_asset_id"])
        self.assertEqual(7, report["expression_count"])
        self.assertEqual(6, report["parsed_expression_count"])

    def test_ci_report_is_deterministic_and_pure(self):
        ci_report = self.report["ci_report"]
        self.assertTrue(ci_report["deterministic"])
        self.assertTrue(ci_report["json_roundtrip"])
        self.assertFalse(ci_report["input_mutated"])

    # -- Attribution manifest acceptance ---------------------------------------

    def test_manifest_contains_only_attribution_required_assets(self):
        attribution = self.report["attribution"]
        self.assertTrue(attribution["only_attribution_required"])
        self.assertTrue(attribution["internal_assets_excluded"])
        self.assertEqual(
            [
                "libresprite_reference_only",
                "piskel_reference_only",
                "pixelorama_reference_only",
            ],
            attribution["asset_ids"],
        )
        self.assertTrue(attribution["flipped_asset_included"])

    def test_manifest_preserves_the_contracted_attribution_fields(self):
        attribution = self.report["attribution"]
        self.assertEqual(
            ["attributions", "generated_date", "manifest_version"],
            attribution["manifest_keys"],
        )
        self.assertEqual(REQUIRED_MANIFEST_ENTRY_FIELDS, attribution["entry_keys"])
        self.assertTrue(attribution["attribution_texts_nonempty"])

    def test_reference_only_assets_stay_excluded_from_shipped_paths(self):
        # Reference-only external sources carry attribution but never an
        # included path: they are not shipped assets.
        self.assertTrue(
            self.report["attribution"]["reference_only_entries_have_no_included_path"]
        )

    def test_manifest_version_stays_pinned_until_a_migration_gate(self):
        attribution = self.report["attribution"]
        self.assertEqual("0.1.0", attribution["manifest_version"])
        self.assertTrue(attribution["generated_date_echoes_ledger"])

    def test_manifest_reproduces_the_committed_stage0_artifact(self):
        self.assertTrue(self.report["attribution"]["matches_committed_manifest"])

    def test_manifest_is_deterministic_and_pure(self):
        attribution = self.report["attribution"]
        self.assertTrue(attribution["deterministic"])
        self.assertTrue(attribution["json_roundtrip"])
        self.assertFalse(attribution["input_mutated"])

    # -- Negative checks ---------------------------------------------------------

    def test_no_probe_wrote_any_repository_file(self):
        no_writes = self.report["no_writes"]
        self.assertEqual([], no_writes["new_data_files"])
        self.assertEqual([], no_writes["new_package_files"])
        self.assertTrue(no_writes["asset_provenance_artifacts_unchanged"])


if __name__ == "__main__":
    unittest.main()
