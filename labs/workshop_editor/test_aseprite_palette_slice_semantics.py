import json
import sys
import tempfile
import unittest
from pathlib import Path


WORKSHOP_DIR = Path(__file__).resolve().parent
GRID_GENOME_DIR = WORKSHOP_DIR.parents[0] / "grid_genome"
for import_path in [WORKSHOP_DIR, GRID_GENOME_DIR]:
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

from aseprite_palette_slice_semantics import (
    decode_aseprite_palette_slice_project,
    export_aseprite_palette_slice_project,
    import_aseprite_palette_slice_project,
    run_aseprite_palette_slice_semantics_lab,
    strip_aseprite_palette_chunk,
    strip_aseprite_slice_chunks,
    tamper_aseprite_palette_entry,
    tamper_aseprite_palette_slice_metadata,
    tamper_aseprite_slice_bounds,
    write_aseprite_palette_slice_semantics_artifacts,
)
from slip import is_grid_aligned
from validator import validate_grid
from workshop_editor import compare_semantic_grid_fidelity


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


def organ_bounds(grid: dict) -> dict:
    bounds = {}
    for organ in ["core", "sensors", "expression"]:
        cells = [cell for cell in grid["cells"] if cell.get("organ") == organ]
        xs = [cell["x"] for cell in cells]
        ys = [cell["y"] for cell in cells]
        bounds[organ] = {
            "x": min(xs),
            "y": min(ys),
            "width": max(xs) - min(xs) + 1,
            "height": max(ys) - min(ys) + 1,
        }
    return bounds


class AsepritePaletteSliceSemanticsTests(unittest.TestCase):
    def test_export_writes_palette_entries_and_semantic_slice_bounds(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        exported = export_aseprite_palette_slice_project(grid, profile)
        decoded = decode_aseprite_palette_slice_project(exported["project_bytes"])

        self.assertEqual("libresprite_project", decoded["format_id"])
        self.assertEqual("0xa5e0", decoded["magic"])
        self.assertEqual("0xf1fa", decoded["frame_magic"])
        self.assertEqual(grid["grid_size"], decoded["dimensions"])
        self.assertEqual(3, decoded["frame_count"])
        self.assertEqual(20, decoded["chunk_count"])
        self.assertEqual(3, decoded["layer_count"])
        self.assertEqual(9, decoded["cel_count"])
        self.assertEqual(3, decoded["tag_count"])
        self.assertEqual(3, decoded["user_data_chunk_count"])
        self.assertEqual(1, decoded["palette_chunk_count"])
        self.assertEqual(len(grid["palette"]["colors"]), decoded["palette_entry_count"])
        self.assertEqual(grid["palette"]["colors"], decoded["palette"]["colors_hex"])
        self.assertEqual(3, decoded["slice_count"])
        self.assertEqual(3, decoded["slice_key_count"])
        self.assertEqual(
            ["organ_core_bounds", "organ_sensors_bounds", "organ_expression_bounds"],
            [entry["name"] for entry in decoded["slices"]],
        )
        self.assertEqual(organ_bounds(grid), exported["metadata"]["slice_bounds_by_organ"])
        self.assertTrue(decoded["native_mechagotchi_semantics"])
        self.assertEqual(
            "aseprite_palette_slice_native_semantics",
            exported["metadata"]["writer_policy"],
        )
        self.assertEqual(3, len(exported["metadata"]["palette_semantics"]))
        self.assertEqual(3, len(exported["metadata"]["slice_semantics"]))

    def test_import_restores_valid_slip_aligned_grid_from_palette_slice_project(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_aseprite_palette_slice_project(grid, profile)

        imported = import_aseprite_palette_slice_project(
            exported["project_bytes"],
            source_grid=grid,
        )
        restored = imported["restored_grid"]
        diff = compare_semantic_grid_fidelity(grid, restored)

        self.assertTrue(imported["ok"], imported["errors"])
        self.assertTrue(validate_grid(restored).ok, validate_grid(restored).errors)
        self.assertTrue(is_grid_aligned(restored, profile).ok)
        self.assertEqual([], diff["changed_cells"])
        self.assertEqual([], diff["missing_cells"])
        self.assertEqual([], diff["added_cells"])
        self.assertEqual(1.0, imported["semantic_fidelity"])
        self.assertEqual(
            "aseprite_palette_slice_native_semantics",
            imported["project_policy"]["semantic_policy"],
        )
        self.assertTrue(imported["project_policy"]["native_mechagotchi_semantics"])
        self.assertFalse(imported["project_policy"]["live_external_editor_verified"])
        self.assertEqual("0x2019", imported["project_policy"]["palette_chunk_type"])
        self.assertEqual("0x2022", imported["project_policy"]["slice_chunk_type"])
        self.assertEqual(3, imported["decoded_project"]["slice_count"])
        self.assertEqual(3, imported["decoded_project"]["palette_entry_count"])

    def test_import_rejects_missing_or_tampered_palette_slice_semantics(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_aseprite_palette_slice_project(grid, profile)

        missing_palette = import_aseprite_palette_slice_project(
            strip_aseprite_palette_chunk(exported["project_bytes"]),
            source_grid=grid,
        )
        tampered_palette = import_aseprite_palette_slice_project(
            tamper_aseprite_palette_entry(exported["project_bytes"]),
            source_grid=grid,
        )
        missing_slices = import_aseprite_palette_slice_project(
            strip_aseprite_slice_chunks(exported["project_bytes"]),
            source_grid=grid,
        )
        invalid_slice_bounds = import_aseprite_palette_slice_project(
            tamper_aseprite_slice_bounds(exported["project_bytes"]),
            source_grid=grid,
        )
        tampered_metadata = import_aseprite_palette_slice_project(
            tamper_aseprite_palette_slice_metadata(exported["project_bytes"]),
            source_grid=grid,
        )

        self.assertFalse(missing_palette["ok"])
        self.assertIn("aseprite_palette_missing", missing_palette["error_families"])
        self.assertFalse(tampered_palette["ok"])
        self.assertIn("aseprite_palette_semantics_mismatch", tampered_palette["error_families"])
        self.assertFalse(missing_slices["ok"])
        self.assertIn("aseprite_slices_missing", missing_slices["error_families"])
        self.assertFalse(invalid_slice_bounds["ok"])
        self.assertIn("aseprite_slice_bounds_invalid", invalid_slice_bounds["error_families"])
        self.assertFalse(tampered_metadata["ok"])
        self.assertIn(
            "aseprite_palette_slice_sidecar_hash_mismatch",
            tampered_metadata["error_families"],
        )
        for result in [
            missing_palette,
            tampered_palette,
            missing_slices,
            invalid_slice_bounds,
            tampered_metadata,
        ]:
            self.assertNotIn("restored_grid", result)

    def test_lab_report_closes_only_stage0_palette_slice_subset(self):
        report = run_aseprite_palette_slice_semantics_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("aseprite_palette_slice_semantics_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(3, report["palette_slice_roundtrip_count"])
        self.assertEqual(3, report["palette_slice_roundtrip_success_count"])
        self.assertEqual(5, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["palette_slice_roundtrip_success_rate"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertEqual(1.0, report["metrics"]["cel_visual_hash_preservation_rate"])
        self.assertIn(
            "aseprite_palette_chunk_slip_colors_subset",
            report["closed_states"],
        )
        self.assertIn(
            "aseprite_slice_chunk_semantic_bounds_subset",
            report["closed_states"],
        )
        self.assertIn(
            "aseprite_tilemap_tileset_schema_coverage",
            report["blocked_states"],
        )
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])
        self.assertIn("arbitrary_aseprite_project_schema_coverage", report["blocked_states"])
        self.assertIn("advanced_tags_layers_timeline_schema_coverage", report["blocked_states"])
        self.assertIn("full_project_format_coverage", report["blocked_states"])
        self.assertIn("package_runtime_lifecycle_integration", report["blocked_states"])

    def test_write_artifacts_creates_projects_report_and_app_payload(self):
        report = run_aseprite_palette_slice_semantics_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_aseprite_palette_slice_semantics_artifacts(output_dir, report)

            summary_path = output_dir / "aseprite_palette_slice_semantics_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_palette_slice.aseprite").exists())
            self.assertTrue((output_dir / "slip_gray_stable_palette_slice.aseprite").exists())
            self.assertTrue((output_dir / "slip_amber_social_palette_slice.aseprite").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "aseprite_palette_slice_semantics_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_ASEPRITE_PALETTE_SLICE_SEMANTICS", app_data)


if __name__ == "__main__":
    unittest.main()
