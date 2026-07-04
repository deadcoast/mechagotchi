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

from aseprite_external_properties_semantics import (
    decode_aseprite_external_properties_project,
    export_aseprite_external_properties_project,
    import_aseprite_external_properties_project,
    run_aseprite_external_properties_semantics_lab,
    strip_aseprite_external_file_chunks,
    strip_aseprite_user_data_properties,
    tamper_aseprite_cel_extra_precise_bounds,
    tamper_aseprite_color_profile_type,
    tamper_aseprite_extension_property_map_key,
    tamper_aseprite_external_properties_metadata,
    tamper_aseprite_external_properties_metadata_json,
    write_aseprite_external_properties_semantics_artifacts,
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


class AsepriteExternalPropertiesSemanticsTests(unittest.TestCase):
    def test_export_writes_color_profile_external_files_properties_and_cel_extra(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        exported = export_aseprite_external_properties_project(grid, profile)
        decoded = decode_aseprite_external_properties_project(exported["project_bytes"])

        self.assertEqual("libresprite_project", decoded["format_id"])
        self.assertEqual("0xa5e0", decoded["magic"])
        self.assertEqual("0xf1fa", decoded["frame_magic"])
        self.assertEqual(grid["grid_size"], decoded["dimensions"])
        self.assertEqual(2, decoded["frame_count"])
        self.assertEqual(8, decoded["chunk_count"])
        self.assertEqual(1, decoded["color_profile_chunk_count"])
        self.assertEqual(1, decoded["external_files_chunk_count"])
        self.assertEqual(3, decoded["external_file_entry_count"])
        self.assertEqual(1, decoded["layer_count"])
        self.assertEqual(2, decoded["cel_count"])
        self.assertEqual(2, decoded["cel_extra_count"])
        self.assertEqual(1, decoded["user_data_chunk_count"])
        self.assertEqual(2, decoded["property_map_count"])
        self.assertEqual(10, decoded["property_count"])
        self.assertEqual(1, decoded["color_profile"]["type"])
        self.assertEqual(1, decoded["color_profile"]["flags"])
        self.assertEqual(1.0, decoded["color_profile"]["fixed_gamma"])
        self.assertEqual([0, 1, 2], [entry["type"] for entry in decoded["external_files"]])
        self.assertEqual(
            ["palettes/slip_lcd_seed.gpl", "tilesets/slip_lcd_seed.aseprite", "mechagotchi/slip-properties"],
            [entry["name"] for entry in decoded["external_files"]],
        )
        self.assertEqual(
            [0, 303],
            [entry["map_key"] for entry in decoded["property_maps"]],
        )
        self.assertEqual(
            "aseprite_external_properties_native_semantics",
            exported["metadata"]["writer_policy"],
        )
        self.assertEqual(
            exported["metadata"]["cel_extra_semantics"],
            decoded["cel_extra_semantics"],
        )
        self.assertTrue(decoded["native_mechagotchi_semantics"])

    def test_import_restores_valid_slip_aligned_grid_from_external_properties_project(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_aseprite_external_properties_project(grid, profile)

        imported = import_aseprite_external_properties_project(
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
            "aseprite_external_properties_native_semantics",
            imported["project_policy"]["semantic_policy"],
        )
        self.assertTrue(imported["project_policy"]["native_mechagotchi_semantics"])
        self.assertFalse(imported["project_policy"]["live_external_editor_verified"])
        self.assertEqual("0x2007", imported["project_policy"]["color_profile_chunk_type"])
        self.assertEqual("0x2008", imported["project_policy"]["external_files_chunk_type"])
        self.assertEqual("0x2006", imported["project_policy"]["cel_extra_chunk_type"])
        self.assertEqual("0x2020", imported["project_policy"]["properties_user_data_chunk_type"])

    def test_import_rejects_missing_or_tampered_external_properties_semantics(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_aseprite_external_properties_project(grid, profile)

        missing_external_files = import_aseprite_external_properties_project(
            strip_aseprite_external_file_chunks(exported["project_bytes"]),
            source_grid=grid,
        )
        invalid_color_profile = import_aseprite_external_properties_project(
            tamper_aseprite_color_profile_type(exported["project_bytes"]),
            source_grid=grid,
        )
        missing_properties = import_aseprite_external_properties_project(
            strip_aseprite_user_data_properties(exported["project_bytes"]),
            source_grid=grid,
        )
        invalid_extension_key = import_aseprite_external_properties_project(
            tamper_aseprite_extension_property_map_key(exported["project_bytes"]),
            source_grid=grid,
        )
        invalid_cel_extra = import_aseprite_external_properties_project(
            tamper_aseprite_cel_extra_precise_bounds(exported["project_bytes"]),
            source_grid=grid,
        )
        tampered_metadata = import_aseprite_external_properties_project(
            tamper_aseprite_external_properties_metadata(exported["project_bytes"]),
            source_grid=grid,
        )

        self.assertFalse(missing_external_files["ok"])
        self.assertIn("aseprite_external_files_missing", missing_external_files["error_families"])
        self.assertFalse(invalid_color_profile["ok"])
        self.assertIn("aseprite_color_profile_mismatch", invalid_color_profile["error_families"])
        self.assertFalse(missing_properties["ok"])
        self.assertIn("aseprite_user_data_properties_missing", missing_properties["error_families"])
        self.assertFalse(invalid_extension_key["ok"])
        self.assertIn("aseprite_extension_property_map_missing", invalid_extension_key["error_families"])
        self.assertFalse(invalid_cel_extra["ok"])
        self.assertIn("aseprite_cel_extra_precise_bounds_mismatch", invalid_cel_extra["error_families"])
        self.assertFalse(tampered_metadata["ok"])
        self.assertIn(
            "aseprite_external_properties_sidecar_hash_mismatch",
            tampered_metadata["error_families"],
        )
        for result in [
            missing_external_files,
            invalid_color_profile,
            missing_properties,
            invalid_extension_key,
            invalid_cel_extra,
            tampered_metadata,
        ]:
            self.assertNotIn("restored_grid", result)

    def test_import_rejects_malformed_metadata_json(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_aseprite_external_properties_project(grid, profile)

        malformed = import_aseprite_external_properties_project(
            tamper_aseprite_external_properties_metadata_json(exported["project_bytes"])
        )

        self.assertFalse(malformed["ok"])
        self.assertIn("aseprite_external_properties_json_invalid", malformed["error_families"])

    def test_lab_report_closes_only_stage0_external_properties_subset(self):
        report = run_aseprite_external_properties_semantics_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("aseprite_external_properties_semantics_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(3, report["external_properties_roundtrip_count"])
        self.assertEqual(3, report["external_properties_roundtrip_success_count"])
        self.assertEqual(7, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["external_properties_roundtrip_success_rate"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertEqual(1.0, report["metrics"]["cel_visual_hash_preservation_rate"])
        self.assertEqual(1.0, report["metrics"]["property_map_preservation_rate"])
        self.assertIn("aseprite_color_profile_subset", report["closed_states"])
        self.assertIn("aseprite_external_file_reference_subset", report["closed_states"])
        self.assertIn("aseprite_user_data_properties_subset", report["closed_states"])
        self.assertIn("aseprite_cel_extra_precise_bounds_subset", report["closed_states"])
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])
        self.assertIn("arbitrary_aseprite_project_schema_coverage", report["blocked_states"])
        self.assertIn("full_project_format_coverage", report["blocked_states"])
        self.assertIn("package_runtime_lifecycle_integration", report["blocked_states"])

    def test_write_artifacts_creates_projects_report_and_app_payload(self):
        report = run_aseprite_external_properties_semantics_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_aseprite_external_properties_semantics_artifacts(output_dir, report)

            summary_path = output_dir / "aseprite_external_properties_semantics_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_external_properties.aseprite").exists())
            self.assertTrue((output_dir / "slip_gray_stable_external_properties.aseprite").exists())
            self.assertTrue((output_dir / "slip_amber_social_external_properties.aseprite").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "aseprite_external_properties_semantics_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_ASEPRITE_EXTERNAL_PROPERTIES_SEMANTICS", app_data)


if __name__ == "__main__":
    unittest.main()
