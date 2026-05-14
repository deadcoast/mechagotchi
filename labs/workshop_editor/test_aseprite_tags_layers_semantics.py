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

from aseprite_tags_layers_semantics import (
    decode_aseprite_tags_layers_project,
    export_aseprite_tags_layers_project,
    import_aseprite_tags_layers_project,
    run_aseprite_tags_layers_semantics_lab,
    strip_aseprite_tags_chunk,
    tamper_aseprite_layer_user_data,
    tamper_aseprite_layer_visual_payload,
    tamper_aseprite_tag_range,
    write_aseprite_tags_layers_semantics_artifacts,
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


class AsepriteTagsLayersSemanticsTests(unittest.TestCase):
    def test_export_writes_multiframe_layers_tags_and_layer_user_data(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        exported = export_aseprite_tags_layers_project(grid, profile)
        decoded = decode_aseprite_tags_layers_project(exported["project_bytes"])

        self.assertEqual("libresprite_project", decoded["format_id"])
        self.assertEqual("0xa5e0", decoded["magic"])
        self.assertEqual("0xf1fa", decoded["frame_magic"])
        self.assertEqual(grid["grid_size"], decoded["dimensions"])
        self.assertEqual(3, decoded["frame_count"])
        self.assertEqual(16, decoded["chunk_count"])
        self.assertEqual(3, decoded["layer_count"])
        self.assertEqual(9, decoded["cel_count"])
        self.assertEqual(3, decoded["tag_count"])
        self.assertEqual(3, decoded["user_data_chunk_count"])
        self.assertEqual(
            ["Mechagotchi body", "Mechagotchi sensors", "Mechagotchi expression"],
            [layer["name"] for layer in decoded["layers"]],
        )
        self.assertEqual(
            ["body_core", "sensor", "expression"],
            [entry["semantic_role"] for entry in decoded["layer_user_data"]],
        )
        self.assertEqual(
            ["idle_loop", "sensor_blink", "expression_pulse"],
            [tag["name"] for tag in decoded["tags"]],
        )
        self.assertEqual(
            [[0, 2], [0, 1], [1, 2]],
            [[tag["from_frame"], tag["to_frame"]] for tag in decoded["tags"]],
        )
        self.assertTrue(decoded["native_mechagotchi_semantics"])
        self.assertEqual(
            "aseprite_tags_layers_native_semantics",
            exported["metadata"]["writer_policy"],
        )
        self.assertEqual(9, len(exported["metadata"]["cel_visual_hashes"]))
        self.assertEqual(3, len(exported["metadata"]["layer_semantics"]))
        self.assertEqual(3, len(exported["metadata"]["tag_semantics"]))

    def test_import_restores_valid_slip_aligned_grid_from_layer_user_data(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_aseprite_tags_layers_project(grid, profile)

        imported = import_aseprite_tags_layers_project(
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
            "aseprite_tags_layers_native_semantics",
            imported["project_policy"]["semantic_policy"],
        )
        self.assertTrue(imported["project_policy"]["native_mechagotchi_semantics"])
        self.assertFalse(imported["project_policy"]["live_external_editor_verified"])
        self.assertEqual(3, imported["decoded_project"]["layer_count"])
        self.assertEqual(3, imported["decoded_project"]["tag_count"])

    def test_import_rejects_missing_tags_invalid_ranges_tampered_metadata_and_visuals(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_aseprite_tags_layers_project(grid, profile)

        missing_tags = import_aseprite_tags_layers_project(
            strip_aseprite_tags_chunk(exported["project_bytes"]),
            source_grid=grid,
        )
        invalid_tag_range = import_aseprite_tags_layers_project(
            tamper_aseprite_tag_range(exported["project_bytes"]),
            source_grid=grid,
        )
        tampered_metadata = import_aseprite_tags_layers_project(
            tamper_aseprite_layer_user_data(exported["project_bytes"]),
            source_grid=grid,
        )
        tampered_visual = import_aseprite_tags_layers_project(
            tamper_aseprite_layer_visual_payload(exported["project_bytes"]),
            source_grid=grid,
        )

        self.assertFalse(missing_tags["ok"])
        self.assertIn("aseprite_tags_missing", missing_tags["error_families"])
        self.assertFalse(invalid_tag_range["ok"])
        self.assertIn("aseprite_tag_range_invalid", invalid_tag_range["error_families"])
        self.assertFalse(tampered_metadata["ok"])
        self.assertIn(
            "aseprite_tags_layers_sidecar_hash_mismatch",
            tampered_metadata["error_families"],
        )
        self.assertFalse(tampered_visual["ok"])
        self.assertIn(
            "aseprite_tags_layers_visual_hash_mismatch",
            tampered_visual["error_families"],
        )
        for result in [missing_tags, invalid_tag_range, tampered_metadata, tampered_visual]:
            self.assertNotIn("restored_grid", result)

    def test_lab_report_closes_only_stage0_tags_layers_subset(self):
        report = run_aseprite_tags_layers_semantics_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("aseprite_tags_layers_semantics_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(3, report["tags_layers_roundtrip_count"])
        self.assertEqual(3, report["tags_layers_roundtrip_success_count"])
        self.assertEqual(4, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["tags_layers_roundtrip_success_rate"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertEqual(1.0, report["metrics"]["cel_visual_hash_preservation_rate"])
        self.assertIn(
            "aseprite_tags_layers_native_semantics_subset",
            report["closed_states"],
        )
        self.assertIn(
            "aseprite_frame_tags_semantic_ranges",
            report["closed_states"],
        )
        self.assertNotIn(
            "tags_layers" + "_native_project_semantics",
            report["blocked_states"],
        )
        self.assertIn(
            "advanced_tags_layers_timeline_schema_coverage",
            report["blocked_states"],
        )
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])
        self.assertIn("arbitrary_aseprite_project_schema_coverage", report["blocked_states"])
        self.assertIn("full_project_format_coverage", report["blocked_states"])
        self.assertIn("package_runtime_lifecycle_integration", report["blocked_states"])

    def test_write_artifacts_creates_projects_report_and_app_payload(self):
        report = run_aseprite_tags_layers_semantics_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_aseprite_tags_layers_semantics_artifacts(output_dir, report)

            summary_path = output_dir / "aseprite_tags_layers_semantics_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_tags_layers.aseprite").exists())
            self.assertTrue((output_dir / "slip_gray_stable_tags_layers.aseprite").exists())
            self.assertTrue((output_dir / "slip_amber_social_tags_layers.aseprite").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "aseprite_tags_layers_semantics_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_ASEPRITE_TAGS_LAYERS_SEMANTICS", app_data)


if __name__ == "__main__":
    unittest.main()
