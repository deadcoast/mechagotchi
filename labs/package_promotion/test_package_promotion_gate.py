import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from package_promotion_gate import (  # noqa: E402
    build_promotion_criteria,
    evaluate_candidate,
    run_package_promotion_gate,
    write_package_promotion_artifacts,
)


class PackagePromotionGateTests(unittest.TestCase):
    def test_build_promotion_criteria_defines_required_gate_ids(self):
        criteria = build_promotion_criteria()
        criterion_ids = {criterion["criterion_id"] for criterion in criteria}

        self.assertIn("research_artifacts_complete", criterion_ids)
        self.assertIn("metric_thresholds_met", criterion_ids)
        self.assertIn("package_boundary_defined", criterion_ids)
        self.assertIn("verification_surface_defined", criterion_ids)
        self.assertIn("provenance_gate_clean", criterion_ids)

    def test_evaluate_candidate_distinguishes_research_ready_from_package_ready(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "research" / "algorithm_cards").mkdir(parents=True)
            (root / "research" / "experiment_reports").mkdir(parents=True)
            (root / "data" / "fixture").mkdir(parents=True)
            (root / "research" / "algorithm_cards" / "fixture.md").write_text(
                "# Fixture\n",
                encoding="utf-8",
            )
            (root / "research" / "experiment_reports" / "fixture.md").write_text(
                "# Fixture Report\n",
                encoding="utf-8",
            )
            (root / "data" / "fixture" / "metrics.json").write_text(
                json.dumps({"summary": {"validity_rate": 1.0}}) + "\n",
                encoding="utf-8",
            )
            candidate = {
                "component_id": "fixture_component",
                "target_package": "packages/mecha_engine/fixture",
                "algorithm_card": "research/algorithm_cards/fixture.md",
                "experiment_report": "research/experiment_reports/fixture.md",
                "metric_artifact": "data/fixture/metrics.json",
                "thresholds": [
                    {
                        "metric_path": ["summary", "validity_rate"],
                        "operator": ">=",
                        "value": 0.9,
                    }
                ],
                "verification": "python -B fixture_test.py",
            }

            result = evaluate_candidate(root, candidate, package_root_exists=False)

            self.assertTrue(result["research_evidence_complete"])
            self.assertTrue(result["thresholds_met"])
            self.assertEqual("ready_for_package_design", result["gate_status"])
            self.assertIn("package_root_absent", result["promotion_blockers"])

    def test_run_package_promotion_gate_reports_no_actual_promotion_without_package_dir(self):
        report = run_package_promotion_gate(ROOT)

        self.assertEqual("mecha_engine_package_promotion_gate_stage0", report["lab_id"])
        self.assertFalse(report["summary"]["package_root_exists"])
        self.assertGreaterEqual(report["summary"]["criteria_count"], 5)
        self.assertGreaterEqual(report["summary"]["candidate_count"], 4)
        self.assertGreater(report["summary"]["research_ready_count"], 0)
        self.assertEqual(0, report["summary"]["promotion_ready_count"])
        self.assertEqual(
            "criteria_defined_no_package_promotion",
            report["decision"]["status"],
        )

    def test_write_package_promotion_artifacts_creates_report_and_criteria_doc(self):
        report = run_package_promotion_gate(ROOT)
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            write_package_promotion_artifacts(output_dir, report)

            report_path = output_dir / "mecha_engine_package_promotion_gate_stage0.json"
            criteria_path = output_dir / "mecha_engine_package_promotion_criteria.md"
            self.assertTrue(report_path.exists())
            self.assertTrue(criteria_path.exists())
            loaded = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["lab_id"], loaded["lab_id"])


if __name__ == "__main__":
    unittest.main()
