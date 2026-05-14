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

from slip import is_grid_aligned
from spritesheet_packed_runtime_decoder import (
    build_runtime_playback_timeline,
    export_packed_runtime_spritesheet_with_sidecar,
    import_packed_runtime_spritesheet_with_sidecar,
    run_spritesheet_packed_runtime_decoder_lab,
    write_spritesheet_packed_runtime_decoder_artifacts,
)
from standard_image_sidecar_decoder import decode_png_rgba
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


class SpritesheetPackedRuntimeDecoderTests(unittest.TestCase):
    def test_exports_packed_trimmed_and_rotated_atlas_frames(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        exported = export_packed_runtime_spritesheet_with_sidecar(grid, profile)
        decoded = decode_png_rgba(exported["png_bytes"])
        frames = exported["sidecar"]["animation_binding"]["frames"]
        rotated_frames = [frame for frame in frames if frame["rotation_degrees"] == 90]
        trimmed_frames = [frame for frame in frames if frame["trimmed"]]

        self.assertEqual("packed_runtime_sidecar_v1", exported["sidecar"]["animation_binding"]["animation_model"])
        self.assertEqual(3, len(frames))
        self.assertGreater(decoded["width"], 8)
        self.assertGreater(decoded["height"], 8)
        self.assertLess(decoded["width"] * decoded["height"], 8 * 8 * 3)
        self.assertEqual(1, len(rotated_frames))
        self.assertGreaterEqual(len(trimmed_frames), 2)
        for frame in frames:
            trim = frame["trim"]
            rect = frame["rect"]
            if frame["rotation_degrees"] == 90:
                self.assertEqual(trim["h"], rect["w"])
                self.assertEqual(trim["w"], rect["h"])
            else:
                self.assertEqual(trim["w"], rect["w"])
                self.assertEqual(trim["h"], rect["h"])
            self.assertEqual({"w": 8, "h": 8}, frame["source_size"])
            self.assertTrue(frame["canonical_pixel_hash"].startswith("sha256:"))
            self.assertTrue(frame["packed_pixel_hash"].startswith("sha256:"))

    def test_import_reconstructs_canonical_frames_and_runtime_playback(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_packed_runtime_spritesheet_with_sidecar(grid, profile)

        imported = import_packed_runtime_spritesheet_with_sidecar(
            exported["png_bytes"],
            exported["sidecar"],
            source_grid=grid,
        )
        restored = imported["restored_grid"]
        diff = compare_semantic_grid_fidelity(grid, restored)
        timeline = imported["runtime_playback"]["timeline"]

        self.assertTrue(imported["ok"], imported["errors"])
        self.assertTrue(validate_grid(restored).ok, validate_grid(restored).errors)
        self.assertTrue(is_grid_aligned(restored, profile).ok)
        self.assertEqual(3, imported["frame_count"])
        self.assertEqual(1.0, imported["semantic_fidelity"])
        self.assertEqual(1.0, imported["reconstructed_frame_fidelity"])
        self.assertEqual(1.0, imported["runtime_frame_fidelity"])
        self.assertEqual([], diff["changed_cells"])
        self.assertEqual([], diff["missing_cells"])
        self.assertEqual([], diff["added_cells"])
        self.assertEqual([0, 1, 2, 0, 1], [event["frame_index"] for event in timeline])
        self.assertTrue(all(event["canonical_hash_match"] for event in timeline))

    def test_playback_timeline_loops_by_duration_boundaries(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_packed_runtime_spritesheet_with_sidecar(grid, profile)
        decoded = decode_png_rgba(exported["png_bytes"])

        timeline = build_runtime_playback_timeline(
            exported["sidecar"],
            decoded,
            sample_times_ms=[0, 119, 120, 279, 280, 399, 400, 520],
        )

        self.assertEqual([0, 0, 1, 1, 2, 2, 0, 1], [event["frame_index"] for event in timeline])
        self.assertEqual([0, 119, 120, 279, 280, 399, 0, 120], [event["effective_time_ms"] for event in timeline])
        self.assertTrue(all(event["canonical_hash_match"] for event in timeline))

    def test_import_rejects_unsupported_rotation_bad_trim_hash_and_duration(self):
        report = run_spritesheet_packed_runtime_decoder_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )
        families = {
            family
            for result in report["invalid_probe_results"]
            for family in result["error_families"]
        }

        self.assertIn("spritesheet_frame_rotation_unsupported", families)
        self.assertIn("spritesheet_frame_trim_out_of_bounds", families)
        self.assertIn("spritesheet_frame_hash_mismatch", families)
        self.assertIn("runtime_frame_duration_invalid", families)

    def test_lab_report_closes_packed_runtime_without_metadata_or_package_claims(self):
        report = run_spritesheet_packed_runtime_decoder_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("spritesheet_packed_runtime_decoder_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(3, report["packed_roundtrip_success_count"])
        self.assertEqual(4, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertEqual(1.0, report["metrics"]["mean_reconstructed_frame_fidelity"])
        self.assertEqual(1.0, report["metrics"]["mean_runtime_frame_fidelity"])
        self.assertIn("spritesheet_packed_rotation_trim_decoder", report["closed_states"])
        self.assertIn("runtime_animation_playback_sidecar_model", report["closed_states"])
        self.assertNotIn("packed rotation/trim atlas handling", report["blocked_states"])
        self.assertNotIn("runtime animation playback", report["blocked_states"])
        self.assertIn("Adam7/APNG/full PNG conformance", report["blocked_states"])
        self.assertIn("full project-format coverage", report["blocked_states"])
        self.assertIn("arbitrary Aseprite project schema coverage", report["blocked_states"])
        self.assertIn("live external editor rewrite validation", report["blocked_states"])
        self.assertIn("package runtime lifecycle integration", report["blocked_states"])
        self.assertIn("profile-weighted evolution", report["blocked_states"])

    def test_write_artifacts_creates_packed_pngs_sidecars_report_and_app_payload(self):
        report = run_spritesheet_packed_runtime_decoder_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_spritesheet_packed_runtime_decoder_artifacts(output_dir, report)

            summary_path = output_dir / "spritesheet_packed_runtime_decoder_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_packed_runtime_spritesheet.png").exists())
            self.assertTrue((output_dir / "slip_lcd_seed_packed_runtime_sidecar.json").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "spritesheet_packed_runtime_decoder_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_SPRITESHEET_PACKED_RUNTIME_DECODER", app_data)


if __name__ == "__main__":
    unittest.main()
