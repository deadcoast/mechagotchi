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

from png_textual_metadata_policy import (
    TEXTUAL_METADATA_KEYWORD,
    corrupt_png_textual_metadata_canonical_hash,
    corrupt_png_textual_metadata_itxt_utf8,
    corrupt_png_textual_metadata_ztxt_stream,
    duplicate_png_textual_metadata_chunk,
    export_png_textual_metadata_bundle,
    import_png_textual_metadata,
    remove_png_textual_metadata_chunks,
    run_png_textual_metadata_policy_lab,
    tamper_png_textual_metadata_non_ascii_text_policy,
    tamper_png_textual_metadata_ztxt_method,
    write_png_textual_metadata_policy_artifacts,
)
from slip import is_grid_aligned
from standard_image_sidecar_decoder import decode_png_rgba
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


class PNGTextualMetadataPolicyTests(unittest.TestCase):
    def test_export_writes_text_ztxt_and_itxt_policy_variants_without_changing_pixels(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        bundle = export_png_textual_metadata_bundle(grid, profile)
        variants = bundle["variants"]

        self.assertEqual(
            ["text_ascii", "ztxt_ascii", "itxt_utf8", "itxt_utf8_compressed"],
            [variant["variant_id"] for variant in variants],
        )
        self.assertEqual(["tEXt", "zTXt", "iTXt", "iTXt"], [variant["chunk_type"] for variant in variants])
        self.assertEqual(TEXTUAL_METADATA_KEYWORD, bundle["metadata"]["keyword"])
        self.assertIn("cafe", bundle["metadata"]["ascii_probe"])
        self.assertIn("café", bundle["metadata"]["unicode_probe"])
        for variant in variants:
            decoded = decode_png_rgba(variant["png_bytes"])
            canonical_decoded = decode_png_rgba(variant["canonical_png_bytes"])
            self.assertIn(variant["chunk_type"], decoded["chunks"])
            self.assertEqual(canonical_decoded["pixels"], decoded["pixels"])
            self.assertEqual(bundle["metadata"]["canonical_png_hash"], variant["metadata"]["canonical_png_hash"])
            self.assertEqual(bundle["metadata"]["sidecar_hash"], variant["metadata"]["sidecar_hash"])
        self.assertFalse(variants[0]["compressed"])
        self.assertTrue(variants[1]["compressed"])
        self.assertFalse(variants[2]["compressed"])
        self.assertTrue(variants[3]["compressed"])
        self.assertEqual("ascii_json_in_latin1_text_chunk", variants[0]["encoding_policy"])
        self.assertEqual("utf8_json_in_itxt_chunk", variants[2]["encoding_policy"])

    def test_import_restores_valid_grid_from_each_textual_metadata_variant(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        bundle = export_png_textual_metadata_bundle(grid, profile)

        for variant in bundle["variants"]:
            imported = import_png_textual_metadata(
                variant["png_bytes"],
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
            self.assertEqual(1.0, imported["pixel_fidelity"])
            self.assertEqual(variant["chunk_type"], imported["metadata_policy"]["chunk_type"])
            self.assertEqual(variant["variant_id"], imported["metadata_policy"]["variant_id"])
            self.assertFalse(imported["metadata_policy"]["live_external_editor_verified"])

    def test_import_rejects_invalid_textual_metadata_policy_cases(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        bundle = export_png_textual_metadata_bundle(grid, profile)
        by_id = {variant["variant_id"]: variant for variant in bundle["variants"]}

        probes = [
            (
                remove_png_textual_metadata_chunks(by_id["text_ascii"]["png_bytes"]),
                "png_textual_metadata_chunk_missing",
            ),
            (
                duplicate_png_textual_metadata_chunk(by_id["text_ascii"]["png_bytes"]),
                "png_textual_metadata_chunk_duplicate",
            ),
            (
                tamper_png_textual_metadata_non_ascii_text_policy(by_id["text_ascii"]["png_bytes"]),
                "png_textual_metadata_non_ascii_text_policy_violation",
            ),
            (
                tamper_png_textual_metadata_ztxt_method(by_id["ztxt_ascii"]["png_bytes"]),
                "png_ztxt_compression_method_unsupported",
            ),
            (
                corrupt_png_textual_metadata_ztxt_stream(by_id["ztxt_ascii"]["png_bytes"]),
                "png_ztxt_decompression_failed",
            ),
            (
                corrupt_png_textual_metadata_itxt_utf8(by_id["itxt_utf8"]["png_bytes"]),
                "png_itxt_utf8_invalid",
            ),
            (
                corrupt_png_textual_metadata_canonical_hash(by_id["itxt_utf8_compressed"]["png_bytes"]),
                "png_textual_metadata_canonical_hash_mismatch",
            ),
        ]

        for png_bytes, family in probes:
            imported = import_png_textual_metadata(png_bytes, source_grid=grid)
            self.assertFalse(imported["ok"])
            self.assertIn(family, imported["error_families"])
            self.assertNotIn("restored_grid", imported)

    def test_lab_report_closes_only_textual_metadata_policy_subset(self):
        report = run_png_textual_metadata_policy_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("png_textual_metadata_policy_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(12, report["textual_metadata_roundtrip_count"])
        self.assertEqual(12, report["textual_metadata_roundtrip_success_count"])
        self.assertEqual(7, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["textual_metadata_roundtrip_success_rate"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertEqual(1.0, report["metrics"]["mean_pixel_fidelity"])
        self.assertIn("png_textual_metadata_text_ascii_policy", report["closed_states"])
        self.assertIn("png_textual_metadata_ztxt_compressed_policy", report["closed_states"])
        self.assertIn("png_textual_metadata_itxt_utf8_policy", report["closed_states"])
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])
        self.assertIn("Adam7/APNG/full PNG conformance", report["blocked_states"])
        self.assertIn("package_runtime_lifecycle_integration", report["blocked_states"])
        self.assertIn("profile_weighted_evolution", report["blocked_states"])

    def test_write_artifacts_creates_variant_pngs_report_and_app_payload(self):
        report = run_png_textual_metadata_policy_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_png_textual_metadata_policy_artifacts(output_dir, report)

            summary_path = output_dir / "png_textual_metadata_policy_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_text_ascii.png").exists())
            self.assertTrue((output_dir / "slip_lcd_seed_ztxt_ascii.png").exists())
            self.assertTrue((output_dir / "slip_lcd_seed_itxt_utf8.png").exists())
            self.assertTrue((output_dir / "slip_lcd_seed_itxt_utf8_compressed.png").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "png_textual_metadata_policy_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_PNG_TEXTUAL_METADATA_POLICY", app_data)


if __name__ == "__main__":
    unittest.main()
