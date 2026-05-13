import json
import sys
import tempfile
import unittest
from pathlib import Path


GRID_GENOME_DIR = Path(__file__).resolve().parents[1] / "grid_genome"
if str(GRID_GENOME_DIR) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME_DIR))

from corpus_builder import build_seed_grids
from slip import is_grid_aligned
from validator import validate_grid

from workshop_editor import (
    apply_brush,
    build_editor_state,
    export_grid,
    import_grid,
    roundtrip_grid,
    run_workshop_multi_profile_roundtrip_suite,
    run_workshop_export_lab,
    run_workshop_roundtrip_lab,
    write_workshop_multi_profile_roundtrip_artifacts,
    write_workshop_artifacts,
    write_workshop_roundtrip_artifacts,
)


def lcd_profile() -> dict:
    return json.loads(
        Path("data/slips/valid/slip_lcd_seed.json").read_text(encoding="utf-8")
    )


class WorkshopEditorTests(unittest.TestCase):
    def test_editor_state_exposes_semantic_tools_and_slip_context(self):
        state = build_editor_state(build_seed_grids()[0], lcd_profile())

        self.assertEqual([8, 8], state["grid_size"])
        self.assertEqual("slip_lcd_seed", state["slip"]["profile_id"])
        self.assertIn("body", state["tools"])
        self.assertIn("sensor", state["tools"])
        self.assertIn("expression", state["tools"])
        self.assertIn("anchor", state["tools"])
        self.assertEqual(64, len(state["cells"]))
        self.assertTrue(any(cell["token"] == "A" for cell in state["cells"]))

    def test_apply_brush_updates_semantic_cell_state(self):
        state = build_editor_state(build_seed_grids()[0], lcd_profile())

        updated = apply_brush(state, x=7, y=7, tool="sensor")

        cell = next(cell for cell in updated["cells"] if cell["x"] == 7 and cell["y"] == 7)
        self.assertEqual("sensor", cell["role"])
        self.assertEqual("E", cell["token"])
        self.assertEqual("sensors", cell["organ"])

    def test_export_grid_returns_valid_slip_aligned_genome(self):
        state = build_editor_state(build_seed_grids()[0], lcd_profile())
        state = apply_brush(state, x=7, y=7, tool="expression")

        exported = export_grid(state, grid_id="workshop_export_test")

        self.assertTrue(validate_grid(exported).ok, validate_grid(exported).errors)
        self.assertTrue(is_grid_aligned(exported, lcd_profile()).ok)
        self.assertEqual("workshop_editor_lab", exported["metadata"]["source"])
        self.assertEqual("workshop_export_test", exported["grid_id"])

    def test_import_grid_rebuilds_editor_state_from_exported_genome(self):
        state = build_editor_state(build_seed_grids()[0], lcd_profile())
        edited = apply_brush(state, x=7, y=7, tool="sensor")
        exported = export_grid(edited, grid_id="workshop_export_test")

        imported = import_grid(exported, lcd_profile())

        self.assertEqual(exported["grid_id"], imported["grid_id"])
        self.assertEqual(64, len(imported["cells"]))
        imported_cell = next(
            cell for cell in imported["cells"] if cell["x"] == 7 and cell["y"] == 7
        )
        self.assertEqual("E", imported_cell["token"])
        self.assertEqual("sensors", imported_cell["organ"])

    def test_roundtrip_grid_reports_semantic_fidelity(self):
        grid = build_seed_grids()[0]

        result = roundtrip_grid(grid, lcd_profile(), export_grid_id="roundtrip_fixture")

        self.assertTrue(result["import_validation"]["valid"])
        self.assertTrue(result["export_validation"]["valid"])
        self.assertTrue(result["export_validation"]["slip_aligned"])
        self.assertEqual(1, result["metrics"]["roundtrip_success"])
        self.assertEqual(1.0, result["metrics"]["semantic_fidelity"])
        self.assertEqual([], result["semantic_diff"]["changed_cells"])

    def test_run_workshop_export_lab_reports_successful_authoring(self):
        report = run_workshop_export_lab(build_seed_grids()[0], lcd_profile())

        self.assertEqual("workshop_editor_stage0", report["lab_id"])
        self.assertTrue(report["export_validation"]["valid"])
        self.assertTrue(report["export_validation"]["slip_aligned"])
        self.assertEqual(1, report["metrics"]["profile_creation_success"])

    def test_run_workshop_roundtrip_lab_reports_fidelity_metrics(self):
        report = run_workshop_roundtrip_lab(build_seed_grids()[0], lcd_profile())

        self.assertEqual("workshop_roundtrip_stage0", report["lab_id"])
        self.assertEqual(1, report["metrics"]["roundtrip_success"])
        self.assertEqual(1.0, report["metrics"]["semantic_fidelity"])
        self.assertEqual(0, report["metrics"]["schema_error_rate"])

    def test_write_workshop_artifacts_creates_static_app_payload(self):
        state = build_editor_state(build_seed_grids()[0], lcd_profile())
        exported = export_grid(state, grid_id="workshop_export_test")
        report = run_workshop_export_lab(build_seed_grids()[0], lcd_profile())

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_workshop_artifacts(output_dir, state, exported, report)

            self.assertTrue((output_dir / "workshop_seed_state.json").exists())
            self.assertTrue((output_dir / "workshop_export_stage0.json").exists())
            self.assertTrue((output_dir / "workshop_editor_stage0_report.json").exists())
            app_data = (output_dir / "workshop_app_data.js").read_text(encoding="utf-8")
            self.assertIn("MECHAGOTCHI_WORKSHOP_DATA", app_data)

    def test_write_workshop_roundtrip_artifacts_creates_report_and_payload(self):
        report = run_workshop_roundtrip_lab(build_seed_grids()[0], lcd_profile())
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            write_workshop_roundtrip_artifacts(output_dir, report)

            self.assertTrue((output_dir / "workshop_roundtrip_stage0_report.json").exists())
            self.assertTrue((output_dir / "workshop_roundtrip_imported_state.json").exists())
            self.assertTrue((output_dir / "workshop_roundtrip_export.json").exists())
            app_data = (output_dir / "workshop_app_data.js").read_text(encoding="utf-8")
            self.assertIn("roundtrip", app_data)

    def test_multi_profile_roundtrip_suite_covers_generated_profile_corpora(self):
        profile_paths = [
            Path("data/slips/valid/slip_lcd_seed.json"),
            Path("data/slips/valid/slip_gray_stable.json"),
            Path("data/slips/valid/slip_amber_social.json"),
        ]

        report = run_workshop_multi_profile_roundtrip_suite(
            profile_paths,
            Path("data/slips/multi_profile_generation_stage0"),
            limit_per_profile=4,
        )

        self.assertEqual("workshop_multi_profile_roundtrip_stage0", report["lab_id"])
        self.assertEqual(3, report["totals"]["profile_count"])
        self.assertEqual(12, report["totals"]["candidate_count"])
        self.assertEqual(12, report["totals"]["roundtrip_success_count"])
        self.assertEqual(12, report["totals"]["import_valid_count"])
        self.assertEqual(12, report["totals"]["export_valid_count"])
        self.assertEqual(12, report["totals"]["slip_aligned_count"])
        self.assertEqual(1.0, report["totals"]["mean_semantic_fidelity"])
        self.assertEqual(
            ["slip_lcd_seed", "slip_gray_stable", "slip_amber_social"],
            [item["profile_id"] for item in report["profile_results"]],
        )
        self.assertNotIn("standard_image_decoder", report["blocked_states"])
        self.assertNotIn("png_variant_decoder_coverage", report["blocked_states"])
        self.assertIn("png_adam7_interlace_decoder", report["blocked_states"])
        self.assertIn("apng_decoder", report["blocked_states"])
        self.assertIn("full_png_conformance", report["blocked_states"])
        self.assertNotIn("spritesheet_decoder", report["blocked_states"])
        self.assertNotIn("spritesheet_variant_layout_coverage", report["blocked_states"])
        self.assertIn("spritesheet_packed_rotation_trim_decoder", report["blocked_states"])
        self.assertIn("runtime_animation_playback", report["blocked_states"])
        self.assertNotIn("third_party_project_decoder", report["blocked_states"])
        self.assertIn("full_project_format_coverage", report["blocked_states"])
        self.assertIn("embedded_png_metadata_writer", report["blocked_states"])
        self.assertIn("project_file_native_metadata_writer", report["blocked_states"])
        self.assertNotIn("behavior_preview", report["blocked_states"])
        self.assertNotIn("mutation_preview", report["blocked_states"])
        self.assertNotIn("external_metadata_sidecar_strategy", report["blocked_states"])

    def test_write_multi_profile_roundtrip_artifacts_creates_summary_and_profile_reports(self):
        profile_paths = [
            Path("data/slips/valid/slip_lcd_seed.json"),
            Path("data/slips/valid/slip_gray_stable.json"),
        ]
        report = run_workshop_multi_profile_roundtrip_suite(
            profile_paths,
            Path("data/slips/multi_profile_generation_stage0"),
            limit_per_profile=2,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_workshop_multi_profile_roundtrip_artifacts(output_dir, report)

            summary_path = output_dir / "workshop_multi_profile_roundtrip_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["totals"], persisted["totals"])
            for result in report["profile_results"]:
                self.assertTrue((output_dir / f"{result['profile_id']}_roundtrips.json").exists())

    def test_static_editor_shell_contains_required_surfaces(self):
        html = Path("labs/workshop_editor/index.html").read_text(encoding="utf-8")
        script = Path("labs/workshop_editor/app.js").read_text(encoding="utf-8")

        self.assertIn('data-testid="semantic-grid"', html)
        self.assertIn('data-testid="slip-authoring-panel"', html)
        self.assertIn('data-testid="profile-id-input"', html)
        self.assertIn('data-testid="body-mass-min-input"', html)
        self.assertIn('data-testid="behavior-curiosity-input"', html)
        self.assertIn('data-testid="export-json"', html)
        self.assertIn('data-testid="import-json"', html)
        self.assertIn("renderGrid", script)
        self.assertIn("renderProfileAuthoring", script)
        self.assertIn("collectProfileDraft", script)
        self.assertIn("validateProfileDraft", script)
        self.assertIn("applyProfileDraft", script)
        self.assertIn("importGenome", script)
        self.assertIn("validateExport", script)


if __name__ == "__main__":
    unittest.main()
