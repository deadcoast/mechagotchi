import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from mecha_engine_runtime_boundary_gate import (  # noqa: E402
    ARTIFACT_ID,
    build_runtime_boundary_contracts,
    evaluate_runtime_boundary_gate,
    write_runtime_boundary_gate_artifacts,
)


class MechaEngineRuntimeBoundaryGateTests(unittest.TestCase):
    def test_contracts_cover_runtime_lifecycle_and_slip_boundaries(self):
        contracts = build_runtime_boundary_contracts(ROOT)
        contract_ids = {contract["contract_id"] for contract in contracts}

        self.assertIn("package_import_boundary", contract_ids)
        self.assertIn("lifecycle_runtime_boundary", contract_ids)
        self.assertIn("slip_profile_runtime_validation_boundary", contract_ids)
        self.assertIn("archive_readability_boundary", contract_ids)
        self.assertIn("lineage_runtime_state_boundary", contract_ids)

        for contract in contracts:
            self.assertIn("package_target", contract)
            self.assertIn("forbidden_dependencies", contract)
            self.assertIn("blocked_until", contract)
            self.assertIn("labs", contract["forbidden_dependencies"])

    def test_gate_keeps_package_runtime_integration_blocked_without_package_root(self):
        report = evaluate_runtime_boundary_gate(ROOT)

        self.assertEqual(ARTIFACT_ID, report["artifact_id"])
        self.assertFalse(report["package_root_exists"])
        self.assertFalse(report["package_runtime_integration_ready"])
        self.assertFalse(report["profile_weighted_evolution_ready"])
        self.assertFalse(report["manual_readability_calibration_ready"])
        self.assertEqual(0, report["metrics"]["promotion_ready_contracts"])
        self.assertIn("package_runtime_lifecycle_integration", report["blocked_states"])
        self.assertIn("manual_readability_calibration", report["blocked_states"])
        self.assertIn("profile_weighted_evolution", report["blocked_states"])

    def test_negative_probes_reject_lab_imports_and_premature_evolution_claims(self):
        report = evaluate_runtime_boundary_gate(ROOT)
        probes_by_id = {probe["probe_id"]: probe for probe in report["negative_probes"]}

        self.assertFalse(probes_by_id["package_runtime_imports_labs"]["accepted"])
        self.assertEqual("rejected", probes_by_id["package_runtime_imports_labs"]["result"])
        self.assertIn("forbidden_lab_dependency", probes_by_id["package_runtime_imports_labs"]["reasons"])

        self.assertFalse(probes_by_id["claim_profile_weighted_evolution"]["accepted"])
        self.assertIn(
            "manual_readability_calibration_absent",
            probes_by_id["claim_profile_weighted_evolution"]["reasons"],
        )
        self.assertIn(
            "package_runtime_lifecycle_integration_absent",
            probes_by_id["claim_profile_weighted_evolution"]["reasons"],
        )

    def test_write_artifacts_creates_json_report_and_readme(self):
        report = evaluate_runtime_boundary_gate(ROOT)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_runtime_boundary_gate_artifacts(output_dir, report)

            report_path = output_dir / f"{ARTIFACT_ID}.json"
            readme_path = output_dir / "README.md"
            self.assertTrue(report_path.exists())
            self.assertTrue(readme_path.exists())
            loaded = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], loaded["metrics"])
            self.assertIn(
                "not package runtime integration",
                readme_path.read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
