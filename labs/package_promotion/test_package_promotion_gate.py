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

    def test_derived_research_blocker_follows_metric_artifact_evidence(self):
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
            metrics_path = root / "data" / "fixture" / "metrics.json"
            candidate = {
                "component_id": "fixture_component",
                "target_package": "packages/mecha_engine/fixture",
                "algorithm_card": "research/algorithm_cards/fixture.md",
                "experiment_report": "research/experiment_reports/fixture.md",
                "metric_artifact": "data/fixture/metrics.json",
                "thresholds": [],
                "verification": "python -B fixture_test.py",
                "research_blockers": [
                    {
                        "blocker_id": "human_ratings_absent",
                        "cleared_when": {
                            "metric_path": ["ratings_collected"],
                            "operator": "==",
                            "value": True,
                        },
                    },
                    {"blocker_id": "lab_only_method"},
                ],
            }

            metrics_path.write_text(
                json.dumps({"ratings_collected": False}) + "\n",
                encoding="utf-8",
            )
            blocked = evaluate_candidate(root, candidate, package_root_exists=False)

            metrics_path.write_text(
                json.dumps({"ratings_collected": True}) + "\n",
                encoding="utf-8",
            )
            cleared = evaluate_candidate(root, candidate, package_root_exists=False)

        blocked_details = {
            detail["blocker_id"]: detail
            for detail in blocked["research_blocker_details"]
        }
        self.assertEqual("hold_research_only", blocked["gate_status"])
        self.assertIn("human_ratings_absent", blocked["promotion_blockers"])
        self.assertTrue(blocked_details["human_ratings_absent"]["active"])
        self.assertFalse(blocked_details["human_ratings_absent"]["static"])
        self.assertFalse(blocked_details["human_ratings_absent"]["evidence"]["ok"])
        self.assertTrue(blocked_details["lab_only_method"]["static"])
        self.assertTrue(blocked_details["lab_only_method"]["active"])
        self.assertIsNone(blocked_details["lab_only_method"]["evidence"])

        cleared_details = {
            detail["blocker_id"]: detail
            for detail in cleared["research_blocker_details"]
        }
        self.assertFalse(cleared_details["human_ratings_absent"]["active"])
        self.assertTrue(cleared_details["human_ratings_absent"]["evidence"]["ok"])
        self.assertNotIn("human_ratings_absent", cleared["promotion_blockers"])
        # The static blocker still holds the candidate in research-only state.
        self.assertEqual("hold_research_only", cleared["gate_status"])
        self.assertIn("lab_only_method", cleared["promotion_blockers"])

    def test_run_package_promotion_gate_reports_promoted_module_state(self):
        # All five initial modules carry contract tests and parity evidence
        # (2026-07-04 promotions); the repair target exists since decision
        # record 0006 (2026-07-05), so lifecycle, archive, provenance, and
        # repair report promotion_ready. Learning/evaluation targets stay
        # absent (deferred or blocked), so their candidates keep
        # target_package_absent.
        report = run_package_promotion_gate(ROOT)

        self.assertEqual("mecha_engine_package_promotion_gate_stage0", report["lab_id"])
        self.assertTrue(report["summary"]["package_root_exists"])
        self.assertGreaterEqual(report["summary"]["criteria_count"], 5)
        self.assertGreaterEqual(report["summary"]["candidate_count"], 4)
        self.assertGreater(report["summary"]["research_ready_count"], 0)
        self.assertEqual(4, report["summary"]["promotion_ready_count"])
        self.assertEqual(
            "promotion_candidates_available",
            report["decision"]["status"],
        )
        promoted = {
            "lifecycle_simulator",
            "map_elites_archive",
            "provenance_ci",
            "ca_nca_repair",
        }
        for candidate in report["candidates"]:
            self.assertNotIn("package_root_absent", candidate["promotion_blockers"])
            if candidate["component_id"] in promoted:
                self.assertNotIn(
                    "target_package_absent", candidate["promotion_blockers"]
                )
            else:
                self.assertIn(
                    "target_package_absent", candidate["promotion_blockers"]
                )

    def test_repair_candidate_blocker_derives_from_wound_site_evidence(self):
        # The trained-repair artifact records a wound-site arm that meets
        # the assisted stability bar without a target template
        # (site_aware_meets_assisted_stability_bar), so the
        # lab_only_target_template_assisted blocker must derive from that
        # key and clear. With decision record 0006 the repair package
        # target exists, so the candidate reports promotion_ready.
        report = run_package_promotion_gate(ROOT)
        repair = next(
            candidate
            for candidate in report["candidates"]
            if candidate["component_id"] == "ca_nca_repair"
        )

        details = {
            detail["blocker_id"]: detail
            for detail in repair["research_blocker_details"]
        }
        self.assertFalse(
            details["lab_only_target_template_assisted"]["active"]
        )
        self.assertNotIn(
            "lab_only_target_template_assisted",
            repair["promotion_blockers"],
        )
        self.assertNotIn("target_package_absent", repair["promotion_blockers"])
        self.assertEqual("promotion_ready", repair["gate_status"])

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
