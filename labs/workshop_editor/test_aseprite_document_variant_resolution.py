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

from aseprite_document_variant_resolution import (
    decode_aseprite_document_variant_project,
    export_aseprite_document_variant_bundle,
    import_aseprite_document_variant_project,
    run_aseprite_document_variant_resolution_lab,
    strip_aseprite_variant_external_file_chunks,
    tamper_aseprite_document_variant_metadata,
    tamper_aseprite_document_variant_metadata_json,
    tamper_aseprite_indexed_palette,
    tamper_aseprite_variant_color_depth,
    tamper_aseprite_variant_external_asset_hash,
    tamper_aseprite_variant_pixel_payload,
    write_aseprite_document_variant_resolution_artifacts,
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


class AsepriteDocumentVariantResolutionTests(unittest.TestCase):
    def test_export_writes_indexed_grayscale_and_rgba_document_variants_with_external_assets(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        bundle = export_aseprite_document_variant_bundle(grid, profile)
        variants = bundle["variants"]
        decoded = [
            decode_aseprite_document_variant_project(variant["project_bytes"])
            for variant in variants
        ]

        self.assertEqual(["indexed_8", "grayscale_alpha_16", "rgba_32"], [item["variant_id"] for item in variants])
        self.assertEqual([8, 16, 32], [item["color_depth_bpp"] for item in variants])
        self.assertEqual([1, 2, 4], [item["bytes_per_pixel"] for item in variants])
        self.assertEqual(3, len(bundle["external_assets"]))
        for item in decoded:
            self.assertEqual("libresprite_project", item["format_id"])
            self.assertEqual("0xa5e0", item["magic"])
            self.assertEqual("0xf1fa", item["frame_magic"])
            self.assertEqual(grid["grid_size"], item["dimensions"])
            self.assertEqual(1, item["frame_count"])
            self.assertEqual(1, item["layer_count"])
            self.assertEqual(1, item["cel_count"])
            self.assertEqual(1, item["external_files_chunk_count"])
            self.assertEqual(3, item["external_file_entry_count"])
            self.assertEqual(1, item["user_data_chunk_count"])
            self.assertTrue(item["native_mechagotchi_semantics"])
            self.assertEqual(
                bundle["metadata"]["variant_pixel_hashes"][item["variant_id"]],
                item["variant_pixel_hash"],
            )
        self.assertEqual(1, decoded[0]["palette_chunk_count"])
        self.assertEqual(len(grid["palette"]["colors"]), decoded[0]["palette_entry_count"])
        self.assertEqual(0, decoded[1]["palette_chunk_count"])
        self.assertEqual(0, decoded[2]["palette_chunk_count"])

    def test_import_restores_valid_grid_from_all_document_variants_with_resolved_external_assets(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        bundle = export_aseprite_document_variant_bundle(grid, profile)

        for variant in bundle["variants"]:
            imported = import_aseprite_document_variant_project(
                variant["project_bytes"],
                bundle["external_assets"],
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
                "aseprite_document_variant_external_asset_resolution",
                imported["project_policy"]["semantic_policy"],
            )
            self.assertEqual(3, imported["project_policy"]["document_variant_count"])
            self.assertEqual(3, imported["project_policy"]["resolved_external_asset_count"])
            self.assertTrue(imported["project_policy"]["native_mechagotchi_semantics"])
            self.assertFalse(imported["project_policy"]["live_external_editor_verified"])

    def test_import_rejects_missing_or_tampered_variant_and_resolver_semantics(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        bundle = export_aseprite_document_variant_bundle(grid, profile)
        variant = bundle["variants"][0]
        project_bytes = variant["project_bytes"]
        assets = bundle["external_assets"]

        missing_external_files = import_aseprite_document_variant_project(
            strip_aseprite_variant_external_file_chunks(project_bytes),
            assets,
            source_grid=grid,
        )
        invalid_asset_hash = import_aseprite_document_variant_project(
            project_bytes,
            tamper_aseprite_variant_external_asset_hash(assets),
            source_grid=grid,
        )
        unsupported_color_depth = import_aseprite_document_variant_project(
            tamper_aseprite_variant_color_depth(project_bytes, 24),
            assets,
            source_grid=grid,
        )
        indexed_palette_mismatch = import_aseprite_document_variant_project(
            tamper_aseprite_indexed_palette(project_bytes),
            assets,
            source_grid=grid,
        )
        pixel_payload_mismatch = import_aseprite_document_variant_project(
            tamper_aseprite_variant_pixel_payload(project_bytes),
            assets,
            source_grid=grid,
        )
        sidecar_mismatch = import_aseprite_document_variant_project(
            tamper_aseprite_document_variant_metadata(project_bytes),
            assets,
            source_grid=grid,
        )

        expected = [
            (missing_external_files, "aseprite_external_files_missing"),
            (invalid_asset_hash, "aseprite_external_asset_hash_mismatch"),
            (unsupported_color_depth, "aseprite_document_variant_color_depth_unsupported"),
            (indexed_palette_mismatch, "aseprite_indexed_palette_mismatch"),
            (pixel_payload_mismatch, "aseprite_variant_pixel_hash_mismatch"),
            (sidecar_mismatch, "aseprite_document_variant_sidecar_hash_mismatch"),
        ]
        for result, family in expected:
            self.assertFalse(result["ok"])
            self.assertIn(family, result["error_families"])
            self.assertNotIn("restored_grid", result)

    def test_import_rejects_malformed_metadata_json(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        bundle = export_aseprite_document_variant_bundle(grid, profile)

        malformed = import_aseprite_document_variant_project(
            tamper_aseprite_document_variant_metadata_json(bundle["variants"][0]["project_bytes"]),
            bundle["external_assets"],
        )

        self.assertFalse(malformed["ok"])
        self.assertIn("aseprite_document_variant_json_invalid", malformed["error_families"])

    def test_lab_report_closes_only_deterministic_document_variant_and_resolution_subset(self):
        report = run_aseprite_document_variant_resolution_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("aseprite_document_variant_resolution_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(9, report["document_variant_roundtrip_count"])
        self.assertEqual(9, report["document_variant_roundtrip_success_count"])
        self.assertEqual(7, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["document_variant_roundtrip_success_rate"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertEqual(1.0, report["metrics"]["variant_pixel_hash_preservation_rate"])
        self.assertEqual(1.0, report["metrics"]["external_asset_resolution_rate"])
        self.assertIn("aseprite_indexed_8bpp_document_subset", report["closed_states"])
        self.assertIn("aseprite_grayscale_alpha_16bpp_document_subset", report["closed_states"])
        self.assertIn("aseprite_rgba_32bpp_document_subset", report["closed_states"])
        self.assertIn("aseprite_external_asset_resolution_subset", report["closed_states"])
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])
        self.assertIn("arbitrary_aseprite_project_schema_coverage", report["blocked_states"])
        self.assertIn("arbitrary_external_asset_resolution", report["blocked_states"])
        self.assertIn("package_runtime_lifecycle_integration", report["blocked_states"])

    def test_write_artifacts_creates_variant_projects_external_assets_report_and_app_payload(self):
        report = run_aseprite_document_variant_resolution_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_aseprite_document_variant_resolution_artifacts(output_dir, report)

            summary_path = output_dir / "aseprite_document_variant_resolution_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_indexed_8.aseprite").exists())
            self.assertTrue((output_dir / "slip_lcd_seed_grayscale_alpha_16.aseprite").exists())
            self.assertTrue((output_dir / "slip_lcd_seed_rgba_32.aseprite").exists())
            self.assertTrue((output_dir / "external_assets" / "slip_lcd_seed_palette.gpl").exists())
            self.assertTrue((output_dir / "external_assets" / "slip_lcd_seed_tileset.json").exists())
            self.assertTrue((output_dir / "external_assets" / "mechagotchi_variant_resolver.json").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "aseprite_document_variant_resolution_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_ASEPRITE_DOCUMENT_VARIANT_RESOLUTION", app_data)


if __name__ == "__main__":
    unittest.main()
