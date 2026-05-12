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
    run_workshop_export_lab,
    write_workshop_artifacts,
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

    def test_run_workshop_export_lab_reports_successful_authoring(self):
        report = run_workshop_export_lab(build_seed_grids()[0], lcd_profile())

        self.assertEqual("workshop_editor_stage0", report["lab_id"])
        self.assertTrue(report["export_validation"]["valid"])
        self.assertTrue(report["export_validation"]["slip_aligned"])
        self.assertEqual(1, report["metrics"]["profile_creation_success"])

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

    def test_static_editor_shell_contains_required_surfaces(self):
        html = Path("labs/workshop_editor/index.html").read_text(encoding="utf-8")
        script = Path("labs/workshop_editor/app.js").read_text(encoding="utf-8")

        self.assertIn('data-testid="semantic-grid"', html)
        self.assertIn('data-testid="export-json"', html)
        self.assertIn("renderGrid", script)
        self.assertIn("validateExport", script)


if __name__ == "__main__":
    unittest.main()
