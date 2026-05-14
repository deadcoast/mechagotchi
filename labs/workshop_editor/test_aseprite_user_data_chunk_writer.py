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

from aseprite_user_data_chunk_writer import (
    decode_aseprite_user_data_project,
    export_aseprite_user_data_project,
    extract_aseprite_user_data_sidecar,
    import_aseprite_user_data_project,
    run_aseprite_user_data_chunk_writer_lab,
    strip_aseprite_user_data_chunks,
    tamper_aseprite_user_data_sidecar,
    tamper_aseprite_visual_payload,
    write_aseprite_user_data_chunk_writer_artifacts,
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


class AsepriteUserDataChunkWriterTests(unittest.TestCase):
    def test_export_writes_aseprite_chunk_model_with_layer_user_data(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        exported = export_aseprite_user_data_project(grid, profile)
        decoded = decode_aseprite_user_data_project(exported["project_bytes"])
        extracted = extract_aseprite_user_data_sidecar(exported["project_bytes"])

        self.assertEqual("libresprite_project", decoded["format_id"])
        self.assertEqual("0xa5e0", decoded["magic"])
        self.assertEqual("0xf1fa", decoded["frame_magic"])
        self.assertEqual(grid["grid_size"], decoded["dimensions"])
        self.assertEqual(1, decoded["frame_count"])
        self.assertEqual(3, decoded["chunk_count"])
        self.assertEqual(1, decoded["layer_count"])
        self.assertEqual(1, decoded["cel_count"])
        self.assertEqual(1, decoded["user_data_chunk_count"])
        self.assertEqual("0x2020", decoded["user_data_chunks"][0]["chunk_type"])
        self.assertEqual("layer", decoded["user_data_chunks"][0]["target_type"])
        self.assertEqual("Mechagotchi semantic layer", decoded["layers"][0]["name"])
        self.assertTrue(decoded["native_mechagotchi_semantics"])
        self.assertEqual("aseprite_user_data_chunk", extracted["metadata"]["writer_policy"])
        self.assertEqual("libresprite_project", extracted["sidecar"]["asset_binding"]["format_id"])
        self.assertEqual(
            "aseprite_user_data_chunk",
            extracted["sidecar"]["asset_binding"]["semantic_policy"],
        )
        self.assertEqual(
            decoded["cel_visual_hash"],
            extracted["metadata"]["cel_visual_hash"],
        )

    def test_import_restores_valid_slip_aligned_grid_from_user_data_sidecar(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_aseprite_user_data_project(grid, profile)

        imported = import_aseprite_user_data_project(
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
            "aseprite_user_data_chunk",
            imported["project_policy"]["semantic_policy"],
        )
        self.assertTrue(imported["project_policy"]["native_mechagotchi_semantics"])
        self.assertFalse(imported["project_policy"]["live_external_editor_verified"])

    def test_import_rejects_missing_tampered_or_visually_changed_user_data(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_aseprite_user_data_project(grid, profile)

        missing = import_aseprite_user_data_project(
            strip_aseprite_user_data_chunks(exported["project_bytes"]),
            source_grid=grid,
        )
        tampered_sidecar = import_aseprite_user_data_project(
            tamper_aseprite_user_data_sidecar(exported["project_bytes"]),
            source_grid=grid,
        )
        tampered_visual = import_aseprite_user_data_project(
            tamper_aseprite_visual_payload(exported["project_bytes"]),
            source_grid=grid,
        )

        self.assertFalse(missing["ok"])
        self.assertIn("aseprite_user_data_missing", missing["error_families"])
        self.assertFalse(tampered_sidecar["ok"])
        self.assertIn(
            "aseprite_user_data_sidecar_hash_mismatch",
            tampered_sidecar["error_families"],
        )
        self.assertFalse(tampered_visual["ok"])
        self.assertIn(
            "aseprite_user_data_visual_hash_mismatch",
            tampered_visual["error_families"],
        )
        self.assertNotIn("restored_grid", missing)
        self.assertNotIn("restored_grid", tampered_sidecar)
        self.assertNotIn("restored_grid", tampered_visual)

    def test_lab_report_closes_only_stage0_user_data_chunk_subset(self):
        report = run_aseprite_user_data_chunk_writer_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("aseprite_user_data_chunk_writer_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(3, report["user_data_roundtrip_count"])
        self.assertEqual(3, report["user_data_roundtrip_success_count"])
        self.assertEqual(3, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["user_data_roundtrip_success_rate"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertEqual(1.0, report["metrics"]["cel_visual_hash_preservation_rate"])
        self.assertIn("aseprite_libresprite_user_data_chunk_writer", report["closed_states"])
        self.assertIn("aseprite_user_data_sidecar_semantic_restore", report["closed_states"])
        self.assertNotIn("aseprite_libresprite_user_data_chunk_writer", report["blocked_states"])
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])
        self.assertIn("full_project_format_coverage", report["blocked_states"])
        self.assertIn("advanced_tags_layers_timeline_schema_coverage", report["blocked_states"])
        self.assertIn("package_runtime_lifecycle_integration", report["blocked_states"])

    def test_write_artifacts_creates_aseprite_projects_report_and_app_payload(self):
        report = run_aseprite_user_data_chunk_writer_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_aseprite_user_data_chunk_writer_artifacts(output_dir, report)

            summary_path = output_dir / "aseprite_user_data_chunk_writer_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_user_data.aseprite").exists())
            self.assertTrue((output_dir / "slip_gray_stable_user_data.aseprite").exists())
            self.assertTrue((output_dir / "slip_amber_social_user_data.aseprite").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "aseprite_user_data_chunk_writer_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_ASEPRITE_USER_DATA_CHUNK_WRITER", app_data)


if __name__ == "__main__":
    unittest.main()
