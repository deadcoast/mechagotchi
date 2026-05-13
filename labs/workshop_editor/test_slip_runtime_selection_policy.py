import json
import sys
import tempfile
import unittest
from pathlib import Path


WORKSHOP_DIR = Path(__file__).resolve().parent
if str(WORKSHOP_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSHOP_DIR))

from slip_runtime_selection_policy import (
    run_profile_runtime_selection_probe,
    run_slip_runtime_selection_policy_lab,
    write_slip_runtime_selection_policy_artifacts,
)


VALID_PROFILE_PATHS = [
    Path("data/slips/valid/slip_lcd_seed.json"),
    Path("data/slips/valid/slip_gray_stable.json"),
    Path("data/slips/valid/slip_amber_social.json"),
]
GENERATED_ROOT = Path("data/slips/multi_profile_generation_stage0")


class SLIPRuntimeSelectionPolicyTests(unittest.TestCase):
    def test_profile_probe_selects_archive_elite_from_runtime_lifecycle_metrics(self):
        probe = run_profile_runtime_selection_probe(
            VALID_PROFILE_PATHS[0],
            GENERATED_ROOT,
            candidate_limit=8,
            lifecycle_ticks=12,
            rng_seed=31,
        )

        self.assertTrue(probe["validation"]["ok"])
        self.assertTrue(probe["selection_started"])
        self.assertEqual("slip_lcd_seed", probe["profile_id"])
        self.assertEqual("profile_weighted_archive_elite_v0", probe["policy"]["policy_id"])
        self.assertEqual("switchboard", probe["policy"]["runtime_lifecycle_policy"])
        self.assertGreater(probe["archive_summary"]["occupied_niches"], 0)
        self.assertIn(probe["selected"]["grid_id"], probe["archive_summary"]["elite_grid_ids"])
        self.assertGreater(probe["selected"]["selection_score"], 0)
        self.assertIn("need_balance", probe["selected"]["components"])
        self.assertIn("archive_niche_rarity", probe["selected"]["components"])
        self.assertIn("profile_weighted_score", probe["selection_trace"])
        self.assertIn("survival_weights", probe["selection_trace"]["profile_weights"])
        self.assertEqual("switchboard", probe["selected"]["runtime_episode"]["policy"])

    def test_lab_report_selects_one_profile_elite_without_claiming_evolution(self):
        report = run_slip_runtime_selection_policy_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
            candidate_limit=8,
            lifecycle_ticks=12,
            rng_seed=20260513,
        )

        self.assertEqual("slip_runtime_selection_policy_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(3, report["selection_success_count"])
        self.assertEqual(3, report["selected_elite_count"])
        self.assertEqual(2, report["invalid_probe_rejected_count"])
        self.assertGreaterEqual(report["metrics"]["distinct_selected_grid_ids"], 2)
        self.assertGreater(report["metrics"]["mean_selected_selection_score"], 0)
        self.assertTrue(report["metrics"]["runtime_lifecycle_archive_selection_specified"])
        self.assertIn(
            "runtime_lifecycle_archive_selection_policy",
            report["closed_states"],
        )
        self.assertIn(
            "profile_weighted_archive_elite_selection_trace",
            report["closed_states"],
        )
        self.assertIn("profile_weighted_evolution", report["blocked_states"])
        self.assertNotIn("offspring_mutation_selection", report["blocked_states"])
        self.assertNotIn("lineage_replacement_policy", report["blocked_states"])
        self.assertNotIn("archive_selection_policy_integration", report["blocked_states"])
        self.assertNotEqual("profile_weighted_evolution", report["decision"])

    def test_invalid_profile_and_mismatched_candidate_corpus_stop_before_selection(self):
        report = run_slip_runtime_selection_policy_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
            candidate_limit=4,
            lifecycle_ticks=8,
            rng_seed=11,
        )

        invalids = report["invalid_probe_results"]
        self.assertEqual(2, len(invalids))
        for result in invalids:
            self.assertFalse(result["validation"]["ok"], result["probe_id"])
            self.assertFalse(result["selection_started"], result["probe_id"])

        families = {
            family
            for result in invalids
            for family in result["validation"]["error_families"]
        }
        self.assertIn("schema_version_unsupported", families)
        self.assertIn("slip_alignment", families)

    def test_write_artifacts_creates_summary_profile_payloads_and_app_data(self):
        report = run_slip_runtime_selection_policy_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
            candidate_limit=4,
            lifecycle_ticks=8,
            rng_seed=19,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_slip_runtime_selection_policy_artifacts(output_dir, report)

            summary_path = output_dir / "slip_runtime_selection_policy_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue(
                (output_dir / "slip_lcd_seed_runtime_selection_policy.json").exists()
            )
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (
                output_dir / "slip_runtime_selection_policy_data.js"
            ).read_text(encoding="utf-8")
            self.assertIn("MECHAGOTCHI_SLIP_RUNTIME_SELECTION_POLICY", app_data)


if __name__ == "__main__":
    unittest.main()
