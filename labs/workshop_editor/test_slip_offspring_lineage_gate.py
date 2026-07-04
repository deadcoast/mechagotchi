import json
import sys
import tempfile
import unittest
from pathlib import Path


WORKSHOP_DIR = Path(__file__).resolve().parent
if str(WORKSHOP_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSHOP_DIR))

from slip_offspring_lineage_gate import (
    _offspring_grid_id,
    run_profile_offspring_lineage_probe,
    run_slip_offspring_lineage_gate_lab,
    write_slip_offspring_lineage_gate_artifacts,
)


VALID_PROFILE_PATHS = [
    Path("data/slips/valid/slip_lcd_seed.json"),
    Path("data/slips/valid/slip_gray_stable.json"),
    Path("data/slips/valid/slip_amber_social.json"),
]
GENERATED_ROOT = Path("data/slips/multi_profile_generation_stage0")


class SLIPOffspringLineageGateTests(unittest.TestCase):
    def test_offspring_grid_id_stays_within_schema_pattern_across_generations(self):
        # Regression: compounded "_offspring_<variant>" ids exceeded the
        # schema's 64-char grid_id limit at generation 2+ once the grid
        # validator began enforcing the pattern.
        import re

        pattern = re.compile(r"^[a-z0-9][a-z0-9_-]{2,63}$")
        grid_id = "mg_seed_001"
        for generation in range(1, 6):
            grid_id = _offspring_grid_id(grid_id, "social_recolor")
            with self.subTest(generation=generation):
                self.assertLessEqual(len(grid_id), 64)
                self.assertRegex(grid_id, pattern)
        # Deterministic: same inputs, same compressed id.
        long_parent = "mg_seed_001" + "_offspring_social_recolor" * 3
        self.assertEqual(
            _offspring_grid_id(long_parent, "x"), _offspring_grid_id(long_parent, "x")
        )

    def test_profile_probe_selects_valid_offspring_from_runtime_parent(self):
        probe = run_profile_offspring_lineage_probe(
            VALID_PROFILE_PATHS[0],
            GENERATED_ROOT,
            candidate_limit=8,
            lifecycle_ticks=12,
            rng_seed=41,
        )

        self.assertTrue(probe["validation"]["ok"])
        self.assertTrue(probe["gate_started"])
        self.assertEqual("offspring_lineage_gate_v0", probe["policy"]["policy_id"])
        self.assertEqual(
            probe["runtime_parent"]["grid_id"],
            probe["selected_offspring"]["parent_grid_id"],
        )
        self.assertGreater(probe["offspring_candidate_count"], 0)
        self.assertTrue(probe["mutation_gate"]["caps_respected"])
        self.assertTrue(probe["mutation_gate"]["selected_offspring_valid"])
        self.assertTrue(probe["mutation_gate"]["selected_offspring_aligned"])
        self.assertGreaterEqual(
            probe["selected_offspring"]["lineage"]["generation"],
            probe["runtime_parent"]["lineage"]["generation"] + 1,
        )
        self.assertIn(
            probe["lineage_decision"]["action"],
            {"replace_parent", "add_archive_niche", "hold_parent"},
        )
        self.assertIn("archive_niche", probe["selected_offspring"])
        self.assertIn("runtime_episode", probe["selected_offspring"])

    def test_lab_report_closes_offspring_and_lineage_without_claiming_evolution(self):
        report = run_slip_offspring_lineage_gate_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
            candidate_limit=8,
            lifecycle_ticks=12,
            rng_seed=20260513,
        )

        self.assertEqual("slip_offspring_lineage_gate_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(3, report["offspring_gate_success_count"])
        self.assertEqual(3, report["lineage_decision_count"])
        self.assertEqual(2, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["offspring_gate_success_rate"])
        self.assertEqual(1.0, report["metrics"]["invalid_probe_rejection_rate"])
        self.assertTrue(report["metrics"]["offspring_mutation_selection_specified"])
        self.assertTrue(report["metrics"]["lineage_replacement_policy_specified"])
        self.assertGreater(report["metrics"]["mean_selected_offspring_score"], 0)
        self.assertIn("offspring_mutation_selection", report["closed_states"])
        self.assertIn("lineage_replacement_policy", report["closed_states"])
        self.assertNotIn("offspring_mutation_selection", report["blocked_states"])
        self.assertNotIn("lineage_replacement_policy", report["blocked_states"])
        self.assertIn("profile_weighted_evolution", report["blocked_states"])
        self.assertNotEqual("profile_weighted_evolution", report["decision"])

    def test_invalid_profile_and_mismatched_candidate_corpus_stop_before_gate(self):
        report = run_slip_offspring_lineage_gate_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
            candidate_limit=4,
            lifecycle_ticks=8,
            rng_seed=17,
        )

        invalids = report["invalid_probe_results"]
        self.assertEqual(2, len(invalids))
        for result in invalids:
            self.assertFalse(result["validation"]["ok"], result["probe_id"])
            self.assertFalse(result["gate_started"], result["probe_id"])

        families = {
            family
            for result in invalids
            for family in result["validation"]["error_families"]
        }
        self.assertIn("schema_version_unsupported", families)
        self.assertIn("slip_alignment", families)

    def test_write_artifacts_creates_summary_profile_payloads_and_app_data(self):
        report = run_slip_offspring_lineage_gate_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
            candidate_limit=4,
            lifecycle_ticks=8,
            rng_seed=29,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_slip_offspring_lineage_gate_artifacts(output_dir, report)

            summary_path = output_dir / "slip_offspring_lineage_gate_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue(
                (output_dir / "slip_lcd_seed_offspring_lineage_gate.json").exists()
            )
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (
                output_dir / "slip_offspring_lineage_gate_data.js"
            ).read_text(encoding="utf-8")
            self.assertIn("MECHAGOTCHI_SLIP_OFFSPRING_LINEAGE_GATE", app_data)


if __name__ == "__main__":
    unittest.main()
