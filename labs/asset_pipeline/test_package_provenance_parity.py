"""Parity pin: lab provenance ledger vs promoted mecha_engine.provenance.

Runs the Stage 0 lab provenance CI (flat imports, the authoritative
research behavior: the Stage 0 ledger builder, SPDX expression subset with
case-sensitive uppercase operators, ledger policy validation, sha256 /
sha256-tree included-path hashing, CI report, and attribution manifest)
and the promoted package provenance surface (mecha_engine.provenance
through the package src layout) over the same committed Stage 0 artifacts
and fault-injected derivations, and asserts identical results — including
byte-identical re-derivations of the committed
``data/asset_provenance/{validation_report,provenance_ci_report,
attribution_manifest}.json`` artifacts and the committed included-asset
hashes recorded in ``data/asset_provenance/ledger.json``.

Documented equivalence scope: the package function ``build_ci_report`` is
the contract-gate name for the lab-only ``build_provenance_ci_report``
(package callers do not inherit lab file names); ledger *authoring*
(``build_stage0_ledger``) and Stage 0 artifact *writing*
(``write_stage0_artifacts``) stay lab-only, so the package is fed the
committed ledger and the lab-built ledger as inputs. Everything the two
surfaces both expose is compared verbatim — same dict shapes, same error
and warning strings, same hashes. All ``data/asset_provenance`` artifacts
are read-only fixtures here: nothing in this suite regenerates them.

Direction note: labs may import the package for regression evidence; the
reverse (package importing labs) stays forbidden by the provenance
contract gate, and this file lives on the lab side precisely so the
package tree keeps zero lab references.
"""

import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
PACKAGE_SRC = REPO_ROOT / "packages" / "mecha_engine" / "src"
for path in [LAB_DIR, PACKAGE_SRC]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from provenance_ledger import (  # noqa: E402
    build_provenance_ci_report,
    build_stage0_ledger,
    generate_attribution_manifest as lab_generate_attribution_manifest,
    hash_included_path as lab_hash_included_path,
    parse_spdx_expression as lab_parse_spdx_expression,
    validate_ledger as lab_validate_ledger,
)

from mecha_engine.provenance import (  # noqa: E402
    build_ci_report,
    generate_attribution_manifest,
    hash_included_path,
    parse_spdx_expression,
    validate_ledger,
)


ASSET_PROVENANCE = REPO_ROOT / "data" / "asset_provenance"

# Shared SPDX parity corpus: the accepted Stage 0 subset plus the
# single-token mutations and operator-case faults from the property and
# negative test strategy (P6).
SPDX_PARITY_EXPRESSIONS = [
    "MIT",
    "Apache-2.0",
    "Apache-2.0+",
    "CC0-1.0",
    "CC-BY-SA-4.0",
    "GPL-2.0-only",
    "LicenseRef-Mechagotchi-Internal-Research",
    "LicenseRef-Reference-Only",
    "DocumentRef-vendor:LicenseRef-pack",
    "MIT OR Apache-2.0",
    "MIT AND Apache-2.0",
    "GPL-2.0-or-later WITH Autoconf-exception-3.0",
    "(MIT OR Apache-2.0) AND (GPL-2.0-or-later WITH Autoconf-exception-3.0)"
    " AND LicenseRef-Mechagotchi-Internal-Research",
    # Rejections must match error-for-error.
    "MadeUp-1.0",
    "MIT WITH Fake-exception-1.0",
    "MIT or Apache-2.0",
    "MIT and Apache-2.0",
    "MIT with Autoconf-exception-3.0",
    "(MIT",
    "MIT)",
    "MIT OR",
    "AND MIT",
    "",
    "MIT && Apache-2.0",
    "(MIT OR Apache-2.0) WITH Autoconf-exception-3.0",
]


def load_committed(name: str) -> dict:
    return json.loads((ASSET_PROVENANCE / name).read_text(encoding="utf-8"))


def fault_ledgers(ledger: dict) -> dict:
    """Single-fault derivations applied identically to both surfaces."""
    faults: dict[str, dict] = {}

    def derive(name: str, mutate) -> None:
        variant = deepcopy(ledger)
        mutate(variant)
        faults[name] = variant

    derive("wrong_ledger_version", lambda l: l.update(ledger_version="0.2.0"))
    derive("empty_assets", lambda l: l.update(assets=[]))
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
    derive("included_missing_hash", lambda l: l["assets"][1].update(hash=""))
    derive("stale_included_hash", lambda l: l["assets"][1].update(hash="0" * 64))
    derive(
        "hash_algorithm_mismatch",
        lambda l: l["assets"][1].update(hash_algorithm="sha256-tree"),
    )
    derive(
        "included_path_absent",
        lambda l: l["assets"][0].update(
            included_path="data/asset_provenance/absent_fixture.json"
        ),
    )
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
    derive(
        "excluded_with_hash_warns", lambda l: l["assets"][3].update(hash="a" * 64)
    )
    return faults


class PackageProvenanceParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.committed_ledger = load_committed("ledger.json")
        cls.lab_ledger = build_stage0_ledger(REPO_ROOT)

    def test_lab_stage0_ledger_matches_the_committed_fixture(self):
        # Fixture-freshness precondition: the committed ledger is exactly
        # what the lab builder derives from the committed included paths.
        self.assertEqual(self.committed_ledger, self.lab_ledger)

    def test_validation_parity_and_committed_artifact_rederivation(self):
        package_result = validate_ledger(self.committed_ledger, REPO_ROOT)
        lab_result = lab_validate_ledger(self.committed_ledger, REPO_ROOT)
        self.assertEqual(lab_result, package_result)
        self.assertEqual(load_committed("validation_report.json"), package_result)
        # Byte-identical re-derivation of the committed artifact.
        self.assertEqual(
            (ASSET_PROVENANCE / "validation_report.json").read_text(encoding="utf-8"),
            json.dumps(package_result, indent=2) + "\n",
        )

    def test_ci_report_parity_and_committed_artifact_rederivation(self):
        package_report = build_ci_report(self.committed_ledger, REPO_ROOT)
        lab_report = build_provenance_ci_report(self.committed_ledger, REPO_ROOT)
        self.assertEqual(lab_report, package_report)
        self.assertEqual(load_committed("provenance_ci_report.json"), package_report)
        self.assertEqual(
            (ASSET_PROVENANCE / "provenance_ci_report.json").read_text(
                encoding="utf-8"
            ),
            json.dumps(package_report, indent=2) + "\n",
        )

    def test_attribution_manifest_parity_and_committed_artifact_rederivation(self):
        package_manifest = generate_attribution_manifest(self.committed_ledger)
        lab_manifest = lab_generate_attribution_manifest(self.committed_ledger)
        self.assertEqual(lab_manifest, package_manifest)
        self.assertEqual(load_committed("attribution_manifest.json"), package_manifest)
        self.assertEqual(
            (ASSET_PROVENANCE / "attribution_manifest.json").read_text(
                encoding="utf-8"
            ),
            json.dumps(package_manifest, indent=2) + "\n",
        )

    def test_included_path_hash_parity_with_committed_ledger_hashes(self):
        included = [
            entry
            for entry in self.committed_ledger["assets"]
            if entry["included_in_repo"] is True
        ]
        self.assertEqual(3, len(included))
        for entry in included:
            with self.subTest(asset_id=entry["asset_id"]):
                path = REPO_ROOT / entry["included_path"]
                package_hash = hash_included_path(path)
                self.assertEqual(lab_hash_included_path(path), package_hash)
                self.assertEqual(
                    {
                        "hash_algorithm": entry["hash_algorithm"],
                        "hash": entry["hash"],
                    },
                    package_hash,
                )

    def test_spdx_expression_parity_across_the_ledger_expressions(self):
        for entry in self.committed_ledger["assets"]:
            with self.subTest(asset_id=entry["asset_id"]):
                self.assertEqual(
                    lab_parse_spdx_expression(entry["spdx_expression"]),
                    parse_spdx_expression(entry["spdx_expression"]),
                )

    def test_spdx_expression_parity_across_the_mutation_corpus(self):
        for expression in SPDX_PARITY_EXPRESSIONS:
            with self.subTest(expression=expression):
                self.assertEqual(
                    lab_parse_spdx_expression(expression),
                    parse_spdx_expression(expression),
                )

    def test_fault_injected_validation_parity(self):
        for name, variant in fault_ledgers(self.committed_ledger).items():
            with self.subTest(fault=name):
                self.assertEqual(
                    lab_validate_ledger(deepcopy(variant), REPO_ROOT),
                    validate_ledger(deepcopy(variant), REPO_ROOT),
                )

    def test_fault_injected_ci_report_parity(self):
        for name in [
            "stale_included_hash",
            "included_copyleft_without_decision_record",
            "lowercase_operator_expression",
        ]:
            variant = fault_ledgers(self.committed_ledger)[name]
            with self.subTest(fault=name):
                package_report = build_ci_report(deepcopy(variant), REPO_ROOT)
                lab_report = build_provenance_ci_report(deepcopy(variant), REPO_ROOT)
                self.assertEqual(lab_report, package_report)
                self.assertFalse(package_report["ok"])


if __name__ == "__main__":
    unittest.main()
