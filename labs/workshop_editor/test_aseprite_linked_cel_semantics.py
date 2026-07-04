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

from aseprite_linked_cel_semantics import (
    decode_aseprite_linked_cel_project,
    export_aseprite_linked_cel_project,
    import_aseprite_linked_cel_project,
    run_aseprite_linked_cel_semantics_lab,
    strip_aseprite_linked_cel_chunks,
    strip_aseprite_linked_cel_target,
    tamper_aseprite_linked_cel_metadata,
    tamper_aseprite_linked_cel_metadata_json,
    tamper_aseprite_linked_cel_source_visual,
    tamper_aseprite_linked_cel_target,
    write_aseprite_linked_cel_semantics_artifacts,
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


class AsepriteLinkedCelSemanticsTests(unittest.TestCase):
    def test_export_writes_linked_cel_targets_and_resolved_visual_hashes(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        exported = export_aseprite_linked_cel_project(grid, profile)
        decoded = decode_aseprite_linked_cel_project(exported["project_bytes"])

        self.assertEqual("libresprite_project", decoded["format_id"])
        self.assertEqual("0xa5e0", decoded["magic"])
        self.assertEqual("0xf1fa", decoded["frame_magic"])
        self.assertEqual(grid["grid_size"], decoded["dimensions"])
        self.assertEqual(3, decoded["frame_count"])
        self.assertEqual(20, decoded["chunk_count"])
        self.assertEqual(3, decoded["layer_count"])
        self.assertEqual(9, decoded["cel_count"])
        self.assertEqual(5, decoded["compressed_cel_count"])
        self.assertEqual(4, decoded["linked_cel_count"])
        self.assertEqual(4, decoded["linked_cel_target_count"])
        self.assertEqual(3, decoded["tag_count"])
        self.assertEqual(3, decoded["user_data_chunk_count"])
        self.assertEqual(1, decoded["palette_chunk_count"])
        self.assertEqual(3, decoded["slice_count"])
        self.assertTrue(decoded["native_mechagotchi_semantics"])
        self.assertEqual(
            "aseprite_linked_cel_native_semantics",
            exported["metadata"]["writer_policy"],
        )
        self.assertEqual(
            [
                {"frame_index": 1, "layer_index": 0, "linked_to_frame": 0},
                {"frame_index": 1, "layer_index": 2, "linked_to_frame": 0},
                {"frame_index": 2, "layer_index": 0, "linked_to_frame": 0},
                {"frame_index": 2, "layer_index": 1, "linked_to_frame": 0},
            ],
            [
                {
                    "frame_index": entry["frame_index"],
                    "layer_index": entry["layer_index"],
                    "linked_to_frame": entry["linked_to_frame"],
                }
                for entry in decoded["linked_cel_semantics"]
            ],
        )
        self.assertEqual(
            decoded["cel_visual_hashes"]["frame_0_layer_0"],
            decoded["cel_visual_hashes"]["frame_1_layer_0"],
        )
        self.assertEqual(
            decoded["cel_visual_hashes"]["frame_0_layer_2"],
            decoded["cel_visual_hashes"]["frame_1_layer_2"],
        )
        self.assertEqual(
            decoded["cel_visual_hashes"]["frame_0_layer_0"],
            decoded["cel_visual_hashes"]["frame_2_layer_0"],
        )
        self.assertEqual(
            decoded["cel_visual_hashes"]["frame_0_layer_1"],
            decoded["cel_visual_hashes"]["frame_2_layer_1"],
        )
        self.assertNotEqual(
            decoded["cel_visual_hashes"]["frame_0_layer_1"],
            decoded["cel_visual_hashes"]["frame_1_layer_1"],
        )
        self.assertNotEqual(
            decoded["cel_visual_hashes"]["frame_0_layer_2"],
            decoded["cel_visual_hashes"]["frame_2_layer_2"],
        )

    def test_import_restores_valid_slip_aligned_grid_from_linked_cel_project(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_aseprite_linked_cel_project(grid, profile)

        imported = import_aseprite_linked_cel_project(
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
            "aseprite_linked_cel_native_semantics",
            imported["project_policy"]["semantic_policy"],
        )
        self.assertTrue(imported["project_policy"]["native_mechagotchi_semantics"])
        self.assertFalse(imported["project_policy"]["live_external_editor_verified"])
        self.assertEqual("0x2005", imported["project_policy"]["linked_cel_chunk_type"])
        self.assertEqual(4, imported["decoded_project"]["linked_cel_count"])
        self.assertEqual(5, imported["decoded_project"]["compressed_cel_count"])

    def test_import_rejects_missing_invalid_or_tampered_linked_cel_semantics(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_aseprite_linked_cel_project(grid, profile)

        missing_linked = import_aseprite_linked_cel_project(
            strip_aseprite_linked_cel_chunks(exported["project_bytes"]),
            source_grid=grid,
        )
        invalid_target = import_aseprite_linked_cel_project(
            tamper_aseprite_linked_cel_target(exported["project_bytes"]),
            source_grid=grid,
        )
        missing_target = import_aseprite_linked_cel_project(
            strip_aseprite_linked_cel_target(exported["project_bytes"]),
            source_grid=grid,
        )
        tampered_visual = import_aseprite_linked_cel_project(
            tamper_aseprite_linked_cel_source_visual(exported["project_bytes"]),
            source_grid=grid,
        )
        tampered_metadata = import_aseprite_linked_cel_project(
            tamper_aseprite_linked_cel_metadata(exported["project_bytes"]),
            source_grid=grid,
        )

        self.assertFalse(missing_linked["ok"])
        self.assertIn("aseprite_linked_cels_missing", missing_linked["error_families"])
        self.assertFalse(invalid_target["ok"])
        self.assertIn("aseprite_linked_cel_target_invalid", invalid_target["error_families"])
        self.assertFalse(missing_target["ok"])
        self.assertIn("aseprite_linked_cel_target_missing", missing_target["error_families"])
        self.assertFalse(tampered_visual["ok"])
        self.assertIn(
            "aseprite_linked_cel_visual_hash_mismatch",
            tampered_visual["error_families"],
        )
        self.assertFalse(tampered_metadata["ok"])
        self.assertIn(
            "aseprite_linked_cel_sidecar_hash_mismatch",
            tampered_metadata["error_families"],
        )
        for result in [
            missing_linked,
            invalid_target,
            missing_target,
            tampered_visual,
            tampered_metadata,
        ]:
            self.assertNotIn("restored_grid", result)

    def test_import_rejects_malformed_metadata_json(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_aseprite_linked_cel_project(grid, profile)

        malformed = import_aseprite_linked_cel_project(
            tamper_aseprite_linked_cel_metadata_json(exported["project_bytes"])
        )

        self.assertFalse(malformed["ok"])
        self.assertIn("aseprite_linked_cel_json_invalid", malformed["error_families"])

    def test_lab_report_closes_only_stage0_linked_cel_subset(self):
        report = run_aseprite_linked_cel_semantics_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("aseprite_linked_cel_semantics_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(3, report["linked_cel_roundtrip_count"])
        self.assertEqual(3, report["linked_cel_roundtrip_success_count"])
        self.assertEqual(6, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["linked_cel_roundtrip_success_rate"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertEqual(1.0, report["metrics"]["cel_visual_hash_preservation_rate"])
        self.assertIn(
            "aseprite_linked_cel_target_resolution",
            report["closed_states"],
        )
        self.assertIn(
            "aseprite_linked_cel_visual_hash_validation",
            report["closed_states"],
        )
        self.assertNotIn(
            "aseprite_linked_cel_schema_coverage",
            report["blocked_states"],
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
        report = run_aseprite_linked_cel_semantics_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_aseprite_linked_cel_semantics_artifacts(output_dir, report)

            summary_path = output_dir / "aseprite_linked_cel_semantics_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_linked_cel.aseprite").exists())
            self.assertTrue((output_dir / "slip_gray_stable_linked_cel.aseprite").exists())
            self.assertTrue((output_dir / "slip_amber_social_linked_cel.aseprite").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "aseprite_linked_cel_semantics_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_ASEPRITE_LINKED_CEL_SEMANTICS", app_data)


if __name__ == "__main__":
    unittest.main()
