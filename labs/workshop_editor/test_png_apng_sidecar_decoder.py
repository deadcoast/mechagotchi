import binascii
import json
import struct
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


WORKSHOP_DIR = Path(__file__).resolve().parent
GRID_GENOME_DIR = WORKSHOP_DIR.parents[0] / "grid_genome"
for import_path in [WORKSHOP_DIR, GRID_GENOME_DIR]:
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

from png_apng_sidecar_decoder import (
    decode_apng_frames,
    export_apng_with_sidecar,
    import_apng_with_sidecar,
    remove_apng_control_chunk,
    run_apng_sidecar_decoder_lab,
    tamper_apng_blend_op,
    tamper_apng_sequence_number,
    write_apng_sidecar_decoder_artifacts,
)
from slip import is_grid_aligned
from validator import validate_grid


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


class APNGSidecarDecoderTests(unittest.TestCase):
    def test_export_writes_bounded_apng_control_frame_and_fdat_chunks(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        bundle = export_apng_with_sidecar(grid, profile)
        decoded = decode_apng_frames(bundle["png_bytes"])

        self.assertIn("acTL", decoded["chunks"])
        self.assertEqual(2, decoded["animation_control"]["num_frames"])
        self.assertEqual(0, decoded["animation_control"]["num_plays"])
        self.assertEqual(2, decoded["frame_count"])
        self.assertEqual([0, 1, 2], decoded["sequence_numbers"])
        self.assertEqual(["fcTL", "IDAT", "fcTL", "fdAT"], decoded["animation_chunk_order"])
        self.assertEqual([200, 200], [frame["delay_ms"] for frame in decoded["frames"]])
        self.assertTrue(all(frame["full_canvas"] for frame in decoded["frames"]))

    def test_import_restores_slip_aligned_grid_and_validates_frame_hashes(self):
        profile = load_profile(VALID_PROFILE_PATHS[1])
        grid = first_grid_for(profile)
        bundle = export_apng_with_sidecar(grid, profile)

        imported = import_apng_with_sidecar(
            bundle["png_bytes"],
            bundle["sidecar"],
            source_grid=grid,
        )
        restored = imported["restored_grid"]

        self.assertTrue(imported["ok"], imported["errors"])
        self.assertTrue(validate_grid(restored).ok)
        self.assertTrue(is_grid_aligned(restored, profile).ok)
        self.assertEqual(1.0, imported["semantic_fidelity"])
        self.assertEqual(1.0, imported["frame_pixel_fidelity"])
        self.assertEqual(2, imported["decoded_apng"]["frame_count"])
        self.assertEqual("bounded_full_canvas_source_frames", imported["apng_policy"]["frame_policy"])

    def test_import_rejects_invalid_apng_control_sequence_blend_frame_and_asset_hashes(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        bundle = export_apng_with_sidecar(grid, profile)
        bad_frame_sidecar = deepcopy(bundle["sidecar"])
        bad_frame_sidecar["apng_binding"]["frames"][1]["pixel_hash"] = "sha256:not-the-frame"
        bad_asset_sidecar = deepcopy(bundle["sidecar"])
        bad_asset_sidecar["asset_binding"]["content_hash"] = "sha256:not-the-apng"

        probes = [
            (
                remove_apng_control_chunk(bundle["png_bytes"]),
                bundle["sidecar"],
                "apng_control_missing",
            ),
            (
                tamper_apng_sequence_number(bundle["png_bytes"]),
                bundle["sidecar"],
                "apng_sequence_number_invalid",
            ),
            (
                tamper_apng_blend_op(bundle["png_bytes"]),
                bundle["sidecar"],
                "apng_frame_control_unsupported",
            ),
            (
                bundle["png_bytes"],
                bad_frame_sidecar,
                "apng_frame_hash_mismatch",
            ),
            (
                bundle["png_bytes"],
                bad_asset_sidecar,
                "asset_hash_mismatch",
            ),
        ]

        for png_bytes, sidecar, family in probes:
            imported = import_apng_with_sidecar(png_bytes, sidecar, source_grid=grid)
            self.assertFalse(imported["ok"])
            self.assertIn(family, imported["error_families"])

    def test_import_rejects_trailing_bytes_and_non_ascii_chunk_type(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        bundle = export_apng_with_sidecar(grid, profile)
        png_bytes = bundle["png_bytes"]

        trailing = import_apng_with_sidecar(
            png_bytes + b"trailing-garbage",
            bundle["sidecar"],
            source_grid=grid,
        )

        chunk_type = b"t\xffXt"
        data = b"probe"
        bad_chunk = (
            struct.pack(">I", len(data))
            + chunk_type
            + data
            + struct.pack(">I", binascii.crc32(chunk_type + data) & 0xFFFFFFFF)
        )
        non_ascii = import_apng_with_sidecar(
            png_bytes[:-12] + bad_chunk + png_bytes[-12:],
            bundle["sidecar"],
            source_grid=grid,
        )

        self.assertFalse(trailing["ok"])
        self.assertIn("png_trailing_bytes", trailing["error_families"])
        self.assertFalse(non_ascii["ok"])
        self.assertIn("png_chunk_type_invalid", non_ascii["error_families"])

    def test_lab_report_closes_bounded_apng_subset_without_full_conformance_claim(self):
        report = run_apng_sidecar_decoder_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("apng_sidecar_decoder_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(3, report["apng_roundtrip_count"])
        self.assertEqual(3, report["apng_roundtrip_success_count"])
        self.assertEqual(5, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["apng_roundtrip_success_rate"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertEqual(1.0, report["metrics"]["mean_frame_pixel_fidelity"])
        self.assertIn("apng_full_canvas_source_frame_decoder", report["closed_states"])
        self.assertIn("full_apng_png_conformance", report["blocked_states"])
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])
        self.assertNotIn("apng_decoder", report["blocked_states"])

    def test_write_artifacts_creates_apngs_report_and_app_payload(self):
        report = run_apng_sidecar_decoder_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_apng_sidecar_decoder_artifacts(output_dir, report)

            summary_path = output_dir / "apng_sidecar_decoder_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_apng_sidecar.png").exists())
            self.assertTrue((output_dir / "slip_lcd_seed_apng_sidecar.json").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "apng_sidecar_decoder_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_APNG_SIDECAR_DECODER", app_data)


if __name__ == "__main__":
    unittest.main()
