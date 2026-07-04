import base64
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


WORKSHOP_DIR = Path(__file__).resolve().parent
GRID_GENOME_DIR = WORKSHOP_DIR.parents[0] / "grid_genome"
for import_path in [WORKSHOP_DIR, GRID_GENOME_DIR]:
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

from slip import is_grid_aligned
from third_party_project_decoder import (
    PXO_MEMBER_SIZE_CAP,
    ProjectDecodeError,
    decode_aseprite_header,
    decode_piskel_project,
    decode_pixelorama_pxo,
    export_project_with_sidecar,
    import_project_with_sidecar,
    run_third_party_project_decoder_lab,
    write_third_party_project_decoder_artifacts,
)
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


class ThirdPartyProjectDecoderTests(unittest.TestCase):
    def test_export_project_payloads_match_source_format_boundaries(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        piskel = export_project_with_sidecar(grid, profile, "piskel_project")
        pixelorama = export_project_with_sidecar(grid, profile, "pixelorama_pxo")
        aseprite = export_project_with_sidecar(grid, profile, "libresprite_project")

        decoded_piskel = decode_piskel_project(piskel["project_bytes"])
        decoded_pixelorama = decode_pixelorama_pxo(pixelorama["project_bytes"])
        decoded_aseprite = decode_aseprite_header(aseprite["project_bytes"])

        self.assertEqual("piskel_project", decoded_piskel["format_id"])
        self.assertEqual(2, decoded_piskel["model_version"])
        self.assertEqual(grid["grid_size"], decoded_piskel["dimensions"])
        self.assertEqual(1, decoded_piskel["layer_count"])
        self.assertEqual(1, decoded_piskel["frame_count"])
        self.assertEqual("pixelorama_pxo", decoded_pixelorama["format_id"])
        self.assertTrue(decoded_pixelorama["is_zip"])
        self.assertIn("data.json", decoded_pixelorama["members"])
        self.assertEqual(grid["grid_size"], decoded_pixelorama["dimensions"])
        self.assertEqual("libresprite_project", decoded_aseprite["format_id"])
        self.assertEqual("0xa5e0", decoded_aseprite["magic"])
        self.assertEqual(grid["grid_size"], decoded_aseprite["dimensions"])
        self.assertEqual(32, decoded_aseprite["color_depth_bpp"])

    def test_import_project_with_sidecar_restores_valid_slip_aligned_grid(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        exported = export_project_with_sidecar(grid, profile, "pixelorama_pxo")
        imported = import_project_with_sidecar(
            exported["project_bytes"],
            exported["sidecar"],
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
        self.assertEqual("sidecar_required", imported["project_policy"]["semantic_policy"])
        self.assertFalse(imported["project_policy"]["native_mechagotchi_semantics"])

    def test_import_rejects_corrupt_project_and_sidecar_binding_mismatch(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_project_with_sidecar(grid, profile, "piskel_project")
        wrong_hash_sidecar = json.loads(json.dumps(exported["sidecar"]))
        wrong_hash_sidecar["asset_binding"]["content_hash"] = "sha256:not-the-project"
        corrupt_chunk_payload = json.loads(exported["project_bytes"].decode("utf-8"))
        corrupt_layer = json.loads(corrupt_chunk_payload["piskel"]["layers"][0])
        corrupt_layer["chunks"][0]["base64PNG"] = (
            "data:image/png;base64,"
            + base64.b64encode(b"not-a-png").decode("ascii")
        )
        corrupt_chunk_payload["piskel"]["layers"][0] = json.dumps(
            corrupt_layer,
            separators=(",", ":"),
        )
        corrupt_chunk_bytes = json.dumps(
            corrupt_chunk_payload,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")

        corrupt_result = import_project_with_sidecar(
            b"{not-json",
            exported["sidecar"],
        )
        corrupt_chunk_result = import_project_with_sidecar(
            corrupt_chunk_bytes,
            exported["sidecar"],
        )
        wrong_hash_result = import_project_with_sidecar(
            exported["project_bytes"],
            wrong_hash_sidecar,
        )

        self.assertFalse(corrupt_result["ok"])
        self.assertIn("project_json_invalid", corrupt_result["error_families"])
        self.assertFalse(corrupt_chunk_result["ok"])
        self.assertIn("piskel_chunk_png_invalid", corrupt_chunk_result["error_families"])
        self.assertFalse(wrong_hash_result["ok"])
        self.assertIn("asset_hash_mismatch", wrong_hash_result["error_families"])
        self.assertNotIn("restored_grid", corrupt_result)
        self.assertNotIn("restored_grid", corrupt_chunk_result)
        self.assertNotIn("restored_grid", wrong_hash_result)

    def test_decode_pixelorama_pxo_rejects_missing_and_oversized_cel_members(self):
        def build_pxo(cel_payload: bytes | None) -> bytes:
            data = {
                "name": "member_probe",
                "size": {"width": 2, "height": 2},
                "fps": 12,
                "frames": [{"index": 0, "duration_ms": 120}],
                "layers": [{"name": "probe layer", "type": "pixel"}],
                "cels": [
                    {
                        "frame": 0,
                        "layer": 0,
                        "path": "image_data/frames/0/cel_0.png",
                    }
                ],
            }
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("data.json", json.dumps(data))
                if cel_payload is not None:
                    archive.writestr("image_data/frames/0/cel_0.png", cel_payload)
            return buffer.getvalue()

        with self.assertRaises(ProjectDecodeError) as missing:
            decode_pixelorama_pxo(build_pxo(None))
        with self.assertRaises(ProjectDecodeError) as oversized:
            decode_pixelorama_pxo(build_pxo(b"\x00" * (PXO_MEMBER_SIZE_CAP + 1)))

        self.assertEqual("pxo_member_missing", missing.exception.family)
        self.assertEqual("pxo_member_too_large", oversized.exception.family)

    def test_lab_report_closes_decoder_boundary_without_native_writer_claims(self):
        report = run_third_party_project_decoder_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("third_party_project_decoder_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(3, report["project_decoder_success_count"])
        self.assertEqual(3, report["sidecar_restore_success_count"])
        self.assertEqual(3, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertIn("third_party_project_decoder_boundary", report["closed_states"])
        self.assertIn("project_file_sidecar_binding_integrity", report["closed_states"])
        self.assertNotIn("third_party_project_decoder", report["blocked_states"])
        self.assertIn("full_project_format_coverage", report["blocked_states"])
        self.assertIn("embedded_png_metadata_writer", report["blocked_states"])
        self.assertIn("project_file_native_metadata_writer", report["blocked_states"])
        self.assertIn("profile_weighted_evolution", report["blocked_states"])

    def test_write_artifacts_creates_projects_sidecars_summary_and_app_payload(self):
        report = run_third_party_project_decoder_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_third_party_project_decoder_artifacts(output_dir, report)

            summary_path = output_dir / "third_party_project_decoder_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed.piskel").exists())
            self.assertTrue((output_dir / "slip_gray_stable.pxo").exists())
            self.assertTrue((output_dir / "slip_amber_social.aseprite").exists())
            self.assertTrue((output_dir / "slip_lcd_seed_project_sidecar.json").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "third_party_project_decoder_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_THIRD_PARTY_PROJECT_DECODER", app_data)


if __name__ == "__main__":
    unittest.main()
