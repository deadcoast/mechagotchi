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

from aseprite_tilemap_tileset_semantics import (
    decode_aseprite_tilemap_tileset_project,
    export_aseprite_tilemap_tileset_project,
    import_aseprite_tilemap_tileset_project,
    run_aseprite_tilemap_tileset_semantics_lab,
    strip_aseprite_tilemap_cel_chunks,
    strip_aseprite_tileset_chunks,
    tamper_aseprite_tilemap_metadata,
    tamper_aseprite_tilemap_tile_id,
    tamper_aseprite_tileset_image,
    write_aseprite_tilemap_tileset_semantics_artifacts,
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


def organ_counts(grid: dict) -> dict:
    counts = {"core": 0, "sensors": 0, "expression": 0}
    for cell in grid["cells"]:
        if cell.get("organ") in counts:
            counts[cell["organ"]] += 1
    return counts


class AsepriteTilemapTilesetSemanticsTests(unittest.TestCase):
    def test_export_writes_tilemap_layer_tileset_and_compressed_tilemap_cels(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        exported = export_aseprite_tilemap_tileset_project(grid, profile)
        decoded = decode_aseprite_tilemap_tileset_project(exported["project_bytes"])

        self.assertEqual("libresprite_project", decoded["format_id"])
        self.assertEqual("0xa5e0", decoded["magic"])
        self.assertEqual("0xf1fa", decoded["frame_magic"])
        self.assertEqual(grid["grid_size"], decoded["dimensions"])
        self.assertEqual(3, decoded["frame_count"])
        self.assertEqual(11, decoded["chunk_count"])
        self.assertEqual(1, decoded["layer_count"])
        self.assertEqual(1, decoded["tilemap_layer_count"])
        self.assertEqual(1, decoded["tileset_chunk_count"])
        self.assertEqual(4, decoded["tileset_tile_count"])
        self.assertEqual([1, 1], decoded["tilesets"][0]["tile_size"])
        self.assertEqual(3, decoded["cel_count"])
        self.assertEqual(3, decoded["tilemap_cel_count"])
        self.assertEqual(0, decoded["compressed_cel_count"])
        self.assertEqual(3, decoded["tag_count"])
        self.assertEqual(1, decoded["user_data_chunk_count"])
        self.assertEqual(1, decoded["palette_chunk_count"])
        self.assertEqual(3, decoded["slice_count"])
        self.assertTrue(decoded["native_mechagotchi_semantics"])
        self.assertEqual(
            "aseprite_tilemap_tileset_native_semantics",
            exported["metadata"]["writer_policy"],
        )
        self.assertEqual(
            organ_counts(grid),
            decoded["tilemap_semantics"]["organ_tile_counts"],
        )
        self.assertEqual(
            {"empty": 0, "core": 1, "sensors": 2, "expression": 3},
            decoded["tilemap_semantics"]["tile_ids_by_semantic"],
        )
        self.assertEqual(
            decoded["tilemap_hashes"],
            exported["metadata"]["tilemap_hashes"],
        )

    def test_import_restores_valid_slip_aligned_grid_from_tilemap_tileset_project(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_aseprite_tilemap_tileset_project(grid, profile)

        imported = import_aseprite_tilemap_tileset_project(
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
            "aseprite_tilemap_tileset_native_semantics",
            imported["project_policy"]["semantic_policy"],
        )
        self.assertTrue(imported["project_policy"]["native_mechagotchi_semantics"])
        self.assertFalse(imported["project_policy"]["live_external_editor_verified"])
        self.assertEqual("0x2023", imported["project_policy"]["tileset_chunk_type"])
        self.assertEqual("0x2005", imported["project_policy"]["tilemap_cel_chunk_type"])
        self.assertEqual(3, imported["decoded_project"]["tilemap_cel_count"])

    def test_import_rejects_missing_or_tampered_tilemap_tileset_semantics(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_aseprite_tilemap_tileset_project(grid, profile)

        missing_tileset = import_aseprite_tilemap_tileset_project(
            strip_aseprite_tileset_chunks(exported["project_bytes"]),
            source_grid=grid,
        )
        missing_tilemap = import_aseprite_tilemap_tileset_project(
            strip_aseprite_tilemap_cel_chunks(exported["project_bytes"]),
            source_grid=grid,
        )
        tampered_tileset = import_aseprite_tilemap_tileset_project(
            tamper_aseprite_tileset_image(exported["project_bytes"]),
            source_grid=grid,
        )
        tampered_tile_id = import_aseprite_tilemap_tileset_project(
            tamper_aseprite_tilemap_tile_id(exported["project_bytes"]),
            source_grid=grid,
        )
        tampered_metadata = import_aseprite_tilemap_tileset_project(
            tamper_aseprite_tilemap_metadata(exported["project_bytes"]),
            source_grid=grid,
        )

        self.assertFalse(missing_tileset["ok"])
        self.assertIn("aseprite_tileset_missing", missing_tileset["error_families"])
        self.assertFalse(missing_tilemap["ok"])
        self.assertIn("aseprite_tilemap_cels_missing", missing_tilemap["error_families"])
        self.assertFalse(tampered_tileset["ok"])
        self.assertIn("aseprite_tileset_image_hash_mismatch", tampered_tileset["error_families"])
        self.assertFalse(tampered_tile_id["ok"])
        self.assertIn("aseprite_tilemap_tile_ids_mismatch", tampered_tile_id["error_families"])
        self.assertFalse(tampered_metadata["ok"])
        self.assertIn(
            "aseprite_tilemap_tileset_sidecar_hash_mismatch",
            tampered_metadata["error_families"],
        )
        for result in [
            missing_tileset,
            missing_tilemap,
            tampered_tileset,
            tampered_tile_id,
            tampered_metadata,
        ]:
            self.assertNotIn("restored_grid", result)

    def test_lab_report_closes_only_stage0_tilemap_tileset_subset(self):
        report = run_aseprite_tilemap_tileset_semantics_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("aseprite_tilemap_tileset_semantics_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(3, report["tilemap_tileset_roundtrip_count"])
        self.assertEqual(3, report["tilemap_tileset_roundtrip_success_count"])
        self.assertEqual(5, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["tilemap_tileset_roundtrip_success_rate"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertEqual(1.0, report["metrics"]["tilemap_hash_preservation_rate"])
        self.assertIn(
            "aseprite_tileset_chunk_subset",
            report["closed_states"],
        )
        self.assertIn(
            "aseprite_tilemap_cel_chunk_subset",
            report["closed_states"],
        )
        self.assertNotIn(
            "aseprite_tilemap_tileset_schema_coverage",
            report["blocked_states"],
        )
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])
        self.assertIn("arbitrary_aseprite_project_schema_coverage", report["blocked_states"])
        self.assertIn("advanced_tags_layers_timeline_schema_coverage", report["blocked_states"])
        self.assertIn("full_project_format_coverage", report["blocked_states"])
        self.assertIn("package_runtime_lifecycle_integration", report["blocked_states"])

    def test_write_artifacts_creates_projects_report_and_app_payload(self):
        report = run_aseprite_tilemap_tileset_semantics_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_aseprite_tilemap_tileset_semantics_artifacts(output_dir, report)

            summary_path = output_dir / "aseprite_tilemap_tileset_semantics_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_tilemap_tileset.aseprite").exists())
            self.assertTrue((output_dir / "slip_gray_stable_tilemap_tileset.aseprite").exists())
            self.assertTrue((output_dir / "slip_amber_social_tilemap_tileset.aseprite").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "aseprite_tilemap_tileset_semantics_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_ASEPRITE_TILEMAP_TILESET_SEMANTICS", app_data)


if __name__ == "__main__":
    unittest.main()
