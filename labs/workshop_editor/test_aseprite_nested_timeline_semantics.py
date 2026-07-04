import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


WORKSHOP_DIR = Path(__file__).resolve().parent
GRID_GENOME_DIR = WORKSHOP_DIR.parents[0] / "grid_genome"
for import_path in [WORKSHOP_DIR, GRID_GENOME_DIR]:
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

from aseprite_nested_timeline_semantics import (
    decode_aseprite_nested_timeline_project,
    export_aseprite_nested_timeline_project,
    import_aseprite_nested_timeline_project,
    run_aseprite_nested_timeline_semantics_lab,
    strip_aseprite_group_layer_chunks,
    strip_aseprite_tag_user_data_chunks,
    tamper_aseprite_nested_child_level,
    tamper_aseprite_nested_timeline_metadata,
    tamper_aseprite_nested_timeline_metadata_json,
    tamper_aseprite_tag_user_data_color,
    tamper_aseprite_timeline_loop_direction,
    write_aseprite_nested_timeline_semantics_artifacts,
)
from slip import is_grid_aligned
from validator import validate_grid
from workshop_editor import compare_semantic_grid_fidelity


VALID_PROFILE_PATHS = [
    ROOT / "data/slips/valid/slip_lcd_seed.json",
    ROOT / "data/slips/valid/slip_gray_stable.json",
    ROOT / "data/slips/valid/slip_amber_social.json",
]
GENERATED_ROOT = ROOT / "data/slips/multi_profile_generation_stage0"


def load_profile(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def first_grid_for(profile: dict) -> dict:
    grid_path = sorted((GENERATED_ROOT / profile["profile_id"]).glob("*.json"))[0]
    return json.loads(grid_path.read_text(encoding="utf-8"))


class AsepriteNestedTimelineSemanticsTests(unittest.TestCase):
    def test_export_writes_nested_groups_tag_user_data_and_timeline_variants(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        exported = export_aseprite_nested_timeline_project(grid, profile)
        decoded = decode_aseprite_nested_timeline_project(exported["project_bytes"])

        self.assertEqual("libresprite_project", decoded["format_id"])
        self.assertEqual("0xa5e0", decoded["magic"])
        self.assertEqual("0xf1fa", decoded["frame_magic"])
        self.assertEqual(grid["grid_size"], decoded["dimensions"])
        self.assertEqual(4, decoded["frame_count"])
        self.assertEqual(27, decoded["chunk_count"])
        self.assertEqual(5, decoded["layer_count"])
        self.assertEqual(2, decoded["group_layer_count"])
        self.assertEqual(3, decoded["image_layer_count"])
        self.assertEqual(2, decoded["max_child_level"])
        self.assertEqual(12, decoded["cel_count"])
        self.assertEqual(4, decoded["tag_count"])
        self.assertEqual(9, decoded["user_data_chunk_count"])
        self.assertEqual(5, decoded["layer_user_data_count"])
        self.assertEqual(4, decoded["tag_user_data_count"])
        self.assertEqual(
            [
                "Mechagotchi organs",
                "Core mass",
                "Mechagotchi affordances",
                "Sensor affordances",
                "Expression affordances",
            ],
            [layer["name"] for layer in decoded["layers"]],
        )
        self.assertEqual([1, 0, 1, 0, 0], [layer["layer_type"] for layer in decoded["layers"]])
        self.assertEqual([0, 1, 1, 2, 2], [layer["child_level"] for layer in decoded["layers"]])
        self.assertEqual([0, 1, 2, 3], [tag["direction"] for tag in decoded["tags"]])
        self.assertEqual([0, 1, 2, 3], [tag["repeat"] for tag in decoded["tags"]])
        self.assertEqual(
            [tag["name"] for tag in decoded["tags"]],
            [entry["tag_name"] for entry in decoded["tag_user_data"]],
        )
        self.assertTrue(decoded["native_mechagotchi_semantics"])
        self.assertEqual(
            "aseprite_nested_timeline_native_semantics",
            exported["metadata"]["writer_policy"],
        )
        self.assertEqual(decoded["cel_visual_hashes"], exported["metadata"]["cel_visual_hashes"])
        self.assertEqual(5, len(exported["metadata"]["layer_semantics"]))
        self.assertEqual(4, len(exported["metadata"]["tag_semantics"]))

    def test_import_restores_valid_slip_aligned_grid_from_nested_timeline_project(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_aseprite_nested_timeline_project(grid, profile)

        imported = import_aseprite_nested_timeline_project(
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
            "aseprite_nested_timeline_native_semantics",
            imported["project_policy"]["semantic_policy"],
        )
        self.assertTrue(imported["project_policy"]["native_mechagotchi_semantics"])
        self.assertFalse(imported["project_policy"]["live_external_editor_verified"])
        self.assertEqual(1, imported["project_policy"]["group_layer_type"])
        self.assertEqual(2, imported["project_policy"]["max_child_level"])
        self.assertEqual("0x2020", imported["project_policy"]["tag_user_data_chunk_type"])

    def test_import_rejects_missing_or_tampered_nested_timeline_semantics(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_aseprite_nested_timeline_project(grid, profile)

        missing_groups = import_aseprite_nested_timeline_project(
            strip_aseprite_group_layer_chunks(exported["project_bytes"]),
            source_grid=grid,
        )
        invalid_hierarchy = import_aseprite_nested_timeline_project(
            tamper_aseprite_nested_child_level(exported["project_bytes"]),
            source_grid=grid,
        )
        missing_tag_user_data = import_aseprite_nested_timeline_project(
            strip_aseprite_tag_user_data_chunks(exported["project_bytes"]),
            source_grid=grid,
        )
        invalid_direction = import_aseprite_nested_timeline_project(
            tamper_aseprite_timeline_loop_direction(exported["project_bytes"]),
            source_grid=grid,
        )
        invalid_tag_color = import_aseprite_nested_timeline_project(
            tamper_aseprite_tag_user_data_color(exported["project_bytes"]),
            source_grid=grid,
        )
        tampered_metadata = import_aseprite_nested_timeline_project(
            tamper_aseprite_nested_timeline_metadata(exported["project_bytes"]),
            source_grid=grid,
        )

        self.assertFalse(missing_groups["ok"])
        self.assertIn("aseprite_nested_group_missing", missing_groups["error_families"])
        self.assertFalse(invalid_hierarchy["ok"])
        self.assertIn("aseprite_layer_hierarchy_mismatch", invalid_hierarchy["error_families"])
        self.assertFalse(missing_tag_user_data["ok"])
        self.assertIn("aseprite_tag_user_data_missing", missing_tag_user_data["error_families"])
        self.assertFalse(invalid_direction["ok"])
        self.assertIn("aseprite_timeline_loop_direction_invalid", invalid_direction["error_families"])
        self.assertFalse(invalid_tag_color["ok"])
        self.assertIn("aseprite_tag_user_data_color_mismatch", invalid_tag_color["error_families"])
        self.assertFalse(tampered_metadata["ok"])
        self.assertIn(
            "aseprite_nested_timeline_sidecar_hash_mismatch",
            tampered_metadata["error_families"],
        )
        for result in [
            missing_groups,
            invalid_hierarchy,
            missing_tag_user_data,
            invalid_direction,
            invalid_tag_color,
            tampered_metadata,
        ]:
            self.assertNotIn("restored_grid", result)

    def test_import_rejects_malformed_metadata_json(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_aseprite_nested_timeline_project(grid, profile)

        malformed = import_aseprite_nested_timeline_project(
            tamper_aseprite_nested_timeline_metadata_json(exported["project_bytes"])
        )

        self.assertFalse(malformed["ok"])
        self.assertIn("aseprite_nested_timeline_json_invalid", malformed["error_families"])

    def test_lab_report_closes_only_stage0_nested_timeline_subset(self):
        report = run_aseprite_nested_timeline_semantics_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("aseprite_nested_timeline_semantics_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(3, report["nested_timeline_roundtrip_count"])
        self.assertEqual(3, report["nested_timeline_roundtrip_success_count"])
        self.assertEqual(7, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["nested_timeline_roundtrip_success_rate"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertEqual(1.0, report["metrics"]["cel_visual_hash_preservation_rate"])
        self.assertEqual(1.0, report["metrics"]["tag_user_data_preservation_rate"])
        self.assertIn("aseprite_nested_group_layer_subset", report["closed_states"])
        self.assertIn("aseprite_tag_user_data_subset", report["closed_states"])
        self.assertIn("aseprite_timeline_loop_direction_subset", report["closed_states"])
        self.assertNotIn(
            "advanced_tags_layers_timeline_schema_coverage",
            report["blocked_states"],
        )
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])
        self.assertIn("arbitrary_aseprite_project_schema_coverage", report["blocked_states"])
        self.assertIn("full_project_format_coverage", report["blocked_states"])
        self.assertIn("package_runtime_lifecycle_integration", report["blocked_states"])

    def test_write_artifacts_creates_projects_report_and_app_payload(self):
        report = run_aseprite_nested_timeline_semantics_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_aseprite_nested_timeline_semantics_artifacts(output_dir, report)

            summary_path = output_dir / "aseprite_nested_timeline_semantics_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_nested_timeline.aseprite").exists())
            self.assertTrue((output_dir / "slip_gray_stable_nested_timeline.aseprite").exists())
            self.assertTrue((output_dir / "slip_amber_social_nested_timeline.aseprite").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "aseprite_nested_timeline_semantics_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_ASEPRITE_NESTED_TIMELINE_SEMANTICS", app_data)


if __name__ == "__main__":
    unittest.main()
