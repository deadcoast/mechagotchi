import json
import tempfile
import unittest
from pathlib import Path

from slip_authoring_panel import (
    apply_authoring_patch,
    build_authoring_state,
    run_slip_authoring_panel_lab,
    write_slip_authoring_panel_artifacts,
)


VALID_PROFILE_PATHS = [
    Path("data/slips/valid/slip_lcd_seed.json"),
    Path("data/slips/valid/slip_gray_stable.json"),
    Path("data/slips/valid/slip_amber_social.json"),
]


def load_profile(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class SLIPAuthoringPanelTests(unittest.TestCase):
    def test_authoring_state_exposes_schema_constraints_and_migration_gate(self):
        state = build_authoring_state(load_profile(VALID_PROFILE_PATHS[0]))

        self.assertEqual("slip_authoring_panel_stage0", state["panel_id"])
        self.assertEqual("slip_lcd_seed", state["profile"]["profile_id"])
        self.assertEqual(["0.1.0"], state["migration_gate"]["supported_versions"])
        self.assertEqual("accept_current_no_migration", state["migration_gate"]["current_version_action"])
        self.assertIn("lcd_green", state["schema_constraints"]["palette_values"])
        self.assertIn("sensor", state["schema_constraints"]["organ_roles"])
        self.assertEqual(
            ["curiosity", "neediness", "sleepiness"],
            state["schema_constraints"]["behavior_required"],
        )
        self.assertIn("profile_metadata_form", state["surfaces"])
        self.assertIn("schema_validation_panel", state["surfaces"])

    def test_valid_patch_passes_dependency_free_pydantic_and_migration_gates(self):
        state = build_authoring_state(load_profile(VALID_PROFILE_PATHS[0]))

        result = apply_authoring_patch(
            state,
            {
                "name": "LCD Seed Companion Revised",
                "behavior.curiosity": 0.75,
                "grid.allowed_palettes": ["lcd_green", "crt_blue"],
            },
        )

        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual("LCD Seed Companion Revised", result["draft"]["name"])
        self.assertEqual(0.75, result["draft"]["behavior"]["curiosity"])
        self.assertTrue(result["validation"]["dependency_free"]["ok"])
        self.assertTrue(result["validation"]["pydantic"]["ok"])
        self.assertTrue(result["validation"]["migration"]["ok"])
        self.assertEqual([], result["errors"])

    def test_invalid_patch_is_rejected_before_profile_activation(self):
        state = build_authoring_state(load_profile(VALID_PROFILE_PATHS[0]))

        result = apply_authoring_patch(
            state,
            {
                "slip_version": "0.2.0",
                "grid.allowed_palettes": ["unknown_palette"],
                "mutation.cell_mutation_rate_max": 1.4,
            },
        )

        self.assertFalse(result["ok"])
        self.assertEqual("slip_lcd_seed", state["profile"]["profile_id"])
        self.assertEqual("0.1.0", state["profile"]["slip_version"])
        families = {error["family"] for error in result["errors"]}
        self.assertIn("schema_version_unsupported", families)
        self.assertIn("schema_enum", families)
        self.assertIn("schema_range", families)

    def test_lab_report_covers_current_profiles_and_invalid_probes(self):
        report = run_slip_authoring_panel_lab(VALID_PROFILE_PATHS)

        self.assertEqual("slip_authoring_panel_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(3, report["valid_draft_count"])
        self.assertEqual(3, report["invalid_probe_count"])
        self.assertEqual(3, report["invalid_probe_rejected_count"])
        self.assertIn("minimal_profile_authoring_panel", report["closed_states"])
        self.assertNotIn("profile_authoring_ui", report["blocked_states"])
        self.assertIn("behavior_preview", report["blocked_states"])

    def test_write_artifacts_creates_report_states_and_app_payload(self):
        report = run_slip_authoring_panel_lab(VALID_PROFILE_PATHS)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_slip_authoring_panel_artifacts(output_dir, report)

            summary_path = output_dir / "slip_authoring_panel_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_authoring_state.json").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "slip_authoring_panel_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_SLIP_AUTHORING_PANEL", app_data)


if __name__ == "__main__":
    unittest.main()
