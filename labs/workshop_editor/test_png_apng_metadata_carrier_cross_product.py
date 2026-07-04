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

from png_apng_metadata_carrier_cross_product import (
    APNG_METADATA_CARRIER_POLICIES,
    export_apng_metadata_carrier_bundle,
    import_apng_metadata_carrier,
    run_apng_metadata_carrier_cross_product_lab,
    write_apng_metadata_carrier_cross_product_artifacts,
)
from png_apng_sidecar_decoder import decode_apng_frames
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


class APNGMetadataCarrierCrossProductTests(unittest.TestCase):
    def test_export_writes_textual_and_private_carriers_without_changing_apng_frames(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        bundle = export_apng_metadata_carrier_bundle(grid, profile)
        variants = bundle["variants"]

        self.assertEqual(
            ["text_ascii", "ztxt_ascii", "itxt_utf8", "itxt_utf8_compressed", "private_mgot"],
            [variant["variant_id"] for variant in variants],
        )
        self.assertEqual(len(APNG_METADATA_CARRIER_POLICIES), len(variants))
        canonical = decode_apng_frames(bundle["canonical_apng_bytes"])
        canonical_hashes = [frame["pixel_hash"] for frame in canonical["frames"]]
        for variant in variants:
            decoded = decode_apng_frames(variant["png_bytes"])
            self.assertEqual(canonical_hashes, [frame["pixel_hash"] for frame in decoded["frames"]])
            self.assertEqual(
                bundle["metadata"]["canonical_apng_hash"],
                variant["metadata"]["canonical_png_hash"],
            )
            self.assertEqual(
                bundle["metadata"]["sidecar_hash"],
                variant["metadata"]["sidecar_hash"],
            )
            self.assertIn(variant["carrier_family"], {"textual", "private"})
        self.assertEqual(["tEXt", "zTXt", "iTXt", "iTXt", "mgOT"], [variant["chunk_type"] for variant in variants])

    def test_import_restores_valid_grid_from_each_apng_metadata_carrier(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        bundle = export_apng_metadata_carrier_bundle(grid, profile)

        for variant in bundle["variants"]:
            imported = import_apng_metadata_carrier(variant["png_bytes"], source_grid=grid)
            restored = imported["restored_grid"]
            diff = compare_semantic_grid_fidelity(grid, restored)

            self.assertTrue(imported["ok"], imported["errors"])
            self.assertTrue(validate_grid(restored).ok, validate_grid(restored).errors)
            self.assertTrue(is_grid_aligned(restored, profile).ok)
            self.assertEqual([], diff["changed_cells"])
            self.assertEqual([], diff["missing_cells"])
            self.assertEqual([], diff["added_cells"])
            self.assertEqual(1.0, imported["semantic_fidelity"])
            self.assertEqual(1.0, imported["frame_pixel_fidelity"])
            self.assertEqual(2, imported["decoded_apng"]["frame_count"])
            self.assertEqual(variant["variant_id"], imported["metadata_carrier_policy"]["variant_id"])
            self.assertFalse(imported["metadata_carrier_policy"]["live_external_editor_verified"])

    def test_lab_report_closes_only_apng_metadata_carrier_cross_product_subset(self):
        report = run_apng_metadata_carrier_cross_product_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("apng_metadata_carrier_cross_product_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(15, report["metadata_carrier_roundtrip_count"])
        self.assertEqual(15, report["metadata_carrier_roundtrip_success_count"])
        self.assertEqual(6, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["metadata_carrier_roundtrip_success_rate"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertEqual(1.0, report["metrics"]["mean_frame_pixel_fidelity"])
        self.assertIn("apng_textual_metadata_carrier_cross_product", report["closed_states"])
        self.assertIn("apng_private_metadata_carrier_cross_product", report["closed_states"])
        self.assertIn("full_apng_png_conformance", report["blocked_states"])
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])
        self.assertIn("final_png_production_carrier_selection", report["blocked_states"])
        self.assertIn("package_runtime_lifecycle_integration", report["blocked_states"])

    def test_write_artifacts_creates_carrier_pngs_report_and_app_payload(self):
        report = run_apng_metadata_carrier_cross_product_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_apng_metadata_carrier_cross_product_artifacts(output_dir, report)

            summary_path = output_dir / "apng_metadata_carrier_cross_product_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_text_ascii_apng_carrier.png").exists())
            self.assertTrue((output_dir / "slip_lcd_seed_private_mgot_apng_carrier.png").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "apng_metadata_carrier_cross_product_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_APNG_METADATA_CARRIER_CROSS_PRODUCT", app_data)


if __name__ == "__main__":
    unittest.main()
