import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


WORKSHOP_DIR = Path(__file__).resolve().parent
if str(WORKSHOP_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSHOP_DIR))

from slip_multigeneration_lineage_runner import (
    run_profile_multigeneration_lineage_probe,
    run_slip_multigeneration_lineage_runner_lab,
    write_slip_multigeneration_lineage_runner_artifacts,
)


VALID_PROFILE_PATHS = [
    ROOT / "data/slips/valid/slip_lcd_seed.json",
    ROOT / "data/slips/valid/slip_gray_stable.json",
    ROOT / "data/slips/valid/slip_amber_social.json",
]
GENERATED_ROOT = ROOT / "data/slips/multi_profile_generation_stage0"


class SLIPMultigenerationLineageRunnerTests(unittest.TestCase):
    def test_profile_probe_runs_generation_chain_with_lineage_graph_continuity(self):
        probe = run_profile_multigeneration_lineage_probe(
            VALID_PROFILE_PATHS[0],
            GENERATED_ROOT,
            generations=3,
            candidate_limit=8,
            lifecycle_ticks=12,
            rng_seed=101,
        )

        self.assertTrue(probe["validation"]["ok"])
        self.assertTrue(probe["runner_started"])
        self.assertEqual("multigeneration_lineage_runner_v0", probe["policy"]["policy_id"])
        self.assertEqual(3, probe["generation_count"])
        self.assertEqual(3, len(probe["generation_records"]))
        self.assertEqual(9, probe["lineage_graph"]["summary"]["candidate_count"])
        self.assertEqual(0, probe["lineage_graph"]["summary"]["orphan_count"])
        self.assertGreaterEqual(probe["lineage_graph"]["summary"]["max_generation"], 4)
        self.assertTrue(probe["metrics"]["lineage_continuity_verified"])
        self.assertTrue(probe["metrics"]["all_selected_offspring_valid"])
        self.assertTrue(probe["metrics"]["all_selected_offspring_aligned"])
        self.assertGreaterEqual(probe["metrics"]["continued_child_count"], 3)
        for record in probe["generation_records"]:
            self.assertEqual(3, record["offspring_candidate_count"])
            self.assertIn(record["lineage_decision"]["action"], {"replace_parent", "add_archive_niche", "hold_parent"})
            self.assertIn("archive_update", record)
            self.assertIn("continuation_parent_grid_id", record)

    def test_lab_report_closes_lab_multigeneration_without_claiming_runtime_evolution(self):
        report = run_slip_multigeneration_lineage_runner_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
            generations=3,
            candidate_limit=8,
            lifecycle_ticks=12,
            rng_seed=20260513,
        )

        self.assertEqual("slip_multigeneration_lineage_runner_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(3, report["multigeneration_success_count"])
        self.assertEqual(9, report["total_generation_records"])
        self.assertEqual(2, report["invalid_probe_rejected_count"])
        self.assertTrue(report["metrics"]["persistent_multigeneration_lineage_runner_specified"])
        self.assertGreaterEqual(report["metrics"]["max_generation_reached"], 4)
        self.assertIn("persistent_multigeneration_lineage_runner", report["closed_states"])
        self.assertIn("manual_readability_calibration", report["blocked_states"])
        self.assertIn("profile_weighted_evolution", report["blocked_states"])
        self.assertIn("package_runtime_lifecycle_integration", report["blocked_states"])
        self.assertNotIn("persistent_multigeneration_lineage_runner", report["blocked_states"])

    def test_invalid_profile_and_mismatched_candidate_corpus_stop_before_runner(self):
        report = run_slip_multigeneration_lineage_runner_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
            generations=2,
            candidate_limit=4,
            lifecycle_ticks=8,
            rng_seed=77,
        )

        invalids = report["invalid_probe_results"]
        self.assertEqual(2, len(invalids))
        for result in invalids:
            self.assertFalse(result["validation"]["ok"], result["probe_id"])
            self.assertFalse(result["runner_started"], result["probe_id"])

        families = {
            family
            for result in invalids
            for family in result["validation"]["error_families"]
        }
        self.assertIn("schema_version_unsupported", families)
        self.assertIn("slip_alignment", families)

    def test_write_artifacts_creates_summary_profile_payloads_and_app_data(self):
        report = run_slip_multigeneration_lineage_runner_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
            generations=2,
            candidate_limit=4,
            lifecycle_ticks=8,
            rng_seed=91,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_slip_multigeneration_lineage_runner_artifacts(output_dir, report)

            summary_path = output_dir / "slip_multigeneration_lineage_runner_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue(
                (
                    output_dir
                    / "slip_lcd_seed_multigeneration_lineage_runner.json"
                ).exists()
            )
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (
                output_dir / "slip_multigeneration_lineage_runner_data.js"
            ).read_text(encoding="utf-8")
            self.assertIn("MECHAGOTCHI_SLIP_MULTIGENERATION_LINEAGE_RUNNER", app_data)


if __name__ == "__main__":
    unittest.main()
