import json
import sys
import tempfile
import unittest
from pathlib import Path


WORKSHOP_DIR = Path(__file__).resolve().parent
if str(WORKSHOP_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSHOP_DIR))

from slip_preview_gates import (
    build_behavior_preview,
    build_mutation_preview,
    run_slip_preview_gate_lab,
    validate_preview_request,
    write_slip_preview_gate_artifacts,
)


VALID_PROFILE_PATHS = [
    Path("data/slips/valid/slip_lcd_seed.json"),
    Path("data/slips/valid/slip_gray_stable.json"),
    Path("data/slips/valid/slip_amber_social.json"),
]
GENERATED_ROOT = Path("data/slips/multi_profile_generation_stage0")


def load_profile(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def first_grid_for(profile: dict) -> dict:
    grid_path = sorted((GENERATED_ROOT / profile["profile_id"]).glob("*.json"))[0]
    return json.loads(grid_path.read_text(encoding="utf-8"))


class SLIPPreviewGateTests(unittest.TestCase):
    def test_behavior_preview_reflects_profile_weight_differences(self):
        previews = {
            path.stem: build_behavior_preview(load_profile(path))
            for path in VALID_PROFILE_PATHS
        }

        self.assertEqual(
            "deterministic_profile_weight_proxy",
            previews["slip_lcd_seed"]["preview_model"],
        )
        self.assertEqual(3, previews["slip_lcd_seed"]["scenario_count"])
        self.assertGreater(
            previews["slip_amber_social"]["signals"]["social_pull"],
            previews["slip_lcd_seed"]["signals"]["social_pull"],
        )
        self.assertGreater(
            previews["slip_lcd_seed"]["signals"]["social_pull"],
            previews["slip_gray_stable"]["signals"]["social_pull"],
        )
        self.assertGreater(
            previews["slip_gray_stable"]["signals"]["rest_pull"],
            previews["slip_lcd_seed"]["signals"]["rest_pull"],
        )
        self.assertIn(
            "attention_gap",
            [scenario["scenario_id"] for scenario in previews["slip_lcd_seed"]["scenarios"]],
        )

    def test_mutation_preview_respects_profile_caps_and_palette_constraints(self):
        for path in VALID_PROFILE_PATHS:
            profile = load_profile(path)
            grid = first_grid_for(profile)

            preview = build_mutation_preview(profile, grid)

            self.assertTrue(preview["caps_respected"], profile["profile_id"])
            self.assertEqual(profile["profile_id"], preview["profile_id"])
            self.assertLessEqual(
                preview["budgets"]["cell_mutation_budget"],
                preview["budgets"]["cell_mutation_budget_cap"],
            )
            self.assertLessEqual(
                preview["budgets"]["organ_shift_budget"],
                preview["budgets"]["organ_shift_budget_cap"],
            )
            self.assertFalse(preview["palette_shift"]["allowed"])
            self.assertEqual(
                "single_allowed_palette_blocks_preview_shift",
                preview["palette_shift"]["reason"],
            )

    def test_invalid_profile_is_rejected_before_preview(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        profile["slip_version"] = "0.2.0"
        grid = first_grid_for(load_profile(VALID_PROFILE_PATHS[0]))

        result = validate_preview_request(profile, grid)

        self.assertFalse(result["ok"])
        self.assertIn("schema_version_unsupported", result["error_families"])
        self.assertEqual([], result["preview_surfaces"])

    def test_lab_report_closes_preview_gates_without_claiming_evolution(self):
        report = run_slip_preview_gate_lab(VALID_PROFILE_PATHS, GENERATED_ROOT)

        self.assertEqual("slip_behavior_mutation_preview_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(3, report["behavior_preview_count"])
        self.assertEqual(3, report["mutation_preview_count"])
        self.assertTrue(report["metrics"]["profile_weight_effects_observed"])
        self.assertTrue(report["metrics"]["mutation_caps_respected"])
        self.assertEqual(2, report["invalid_probe_rejected_count"])
        self.assertIn("behavior_preview_gate", report["closed_states"])
        self.assertIn("mutation_preview_gate", report["closed_states"])
        self.assertNotIn("behavior_preview", report["blocked_states"])
        self.assertNotIn("mutation_preview_ui", report["blocked_states"])
        self.assertIn("profile_weighted_evolution", report["blocked_states"])

    def test_write_artifacts_creates_report_profile_payloads_and_app_data(self):
        report = run_slip_preview_gate_lab(VALID_PROFILE_PATHS, GENERATED_ROOT)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_slip_preview_gate_artifacts(output_dir, report)

            summary_path = output_dir / "slip_behavior_mutation_preview_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_preview_gate.json").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "slip_preview_gate_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_SLIP_PREVIEW_GATES", app_data)

    def test_static_editor_shell_contains_preview_surfaces(self):
        html = Path("labs/workshop_editor/index.html").read_text(encoding="utf-8")
        script = Path("labs/workshop_editor/app.js").read_text(encoding="utf-8")

        self.assertIn('data-testid="behavior-preview-panel"', html)
        self.assertIn('data-testid="mutation-preview-panel"', html)
        self.assertIn('data-testid="behavior-preview-output"', html)
        self.assertIn('data-testid="mutation-preview-output"', html)
        self.assertIn("buildBehaviorPreview", script)
        self.assertIn("buildMutationPreview", script)
        self.assertIn("updatePreviewGates", script)


if __name__ == "__main__":
    unittest.main()
