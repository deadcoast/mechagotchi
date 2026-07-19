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

from slip import is_grid_aligned
from spritesheet_sidecar_decoder import (
    DEFAULT_FRAME_DURATIONS_MS,
    export_spritesheet_with_sidecar,
    extract_spritesheet_frames,
    import_spritesheet_with_sidecar,
    render_spritesheet_frame_pixels,
    run_spritesheet_sidecar_decoder_lab,
    write_spritesheet_sidecar_decoder_artifacts,
)
from standard_image_sidecar_decoder import PNG_SIGNATURE, decode_png_rgba
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


class SpritesheetSidecarDecoderTests(unittest.TestCase):
    def test_export_writes_horizontal_spritesheet_with_frame_metadata(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        exported = export_spritesheet_with_sidecar(grid, profile)
        decoded = decode_png_rgba(exported["png_bytes"])
        frames = extract_spritesheet_frames(decoded, exported["sidecar"])
        animation = exported["sidecar"]["animation_binding"]

        self.assertTrue(exported["png_bytes"].startswith(PNG_SIGNATURE))
        self.assertEqual("spritesheet_png", exported["asset"]["format_id"])
        self.assertEqual(3, animation["frame_count"])
        self.assertEqual(DEFAULT_FRAME_DURATIONS_MS, [frame["duration_ms"] for frame in animation["frames"]])
        self.assertEqual(grid["grid_size"][0] * 3, decoded["width"])
        self.assertEqual(grid["grid_size"][1], decoded["height"])
        self.assertEqual([0, 8, 16], [frame["rect"]["x"] for frame in animation["frames"]])
        self.assertEqual(render_spritesheet_frame_pixels(grid, 0), frames[0]["pixels"])
        self.assertEqual(render_spritesheet_frame_pixels(grid, 1), frames[1]["pixels"])
        self.assertNotEqual(frames[0]["pixel_hash"], frames[1]["pixel_hash"])

    def test_import_spritesheet_with_sidecar_restores_valid_slip_aligned_grid(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_spritesheet_with_sidecar(grid, profile)

        imported = import_spritesheet_with_sidecar(
            exported["png_bytes"],
            exported["sidecar"],
        )
        restored = imported["restored_grid"]
        diff = compare_semantic_grid_fidelity(grid, restored)

        self.assertTrue(imported["ok"], imported["errors"])
        self.assertTrue(validate_grid(restored).ok, validate_grid(restored).errors)
        self.assertTrue(is_grid_aligned(restored, profile).ok)
        self.assertEqual(3, imported["frame_count"])
        self.assertEqual(1.0, imported["semantic_fidelity"])
        self.assertEqual(1.0, imported["frame_pixel_fidelity"])
        self.assertEqual([], diff["changed_cells"])
        self.assertEqual([], diff["missing_cells"])
        self.assertEqual([], diff["added_cells"])

    def test_import_scores_semantic_fidelity_against_source_grid_when_available(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_spritesheet_with_sidecar(grid, profile)
        tampered_sidecar = json.loads(json.dumps(exported["sidecar"]))
        tampered_sidecar["semantic_overlay"]["cells"][0]["material"] = "soft"

        imported = import_spritesheet_with_sidecar(
            exported["png_bytes"],
            tampered_sidecar,
            source_grid=grid,
        )

        self.assertTrue(imported["ok"], imported["errors"])
        self.assertLess(imported["semantic_fidelity"], 1.0)
        self.assertNotEqual([], imported["semantic_diff"]["changed_cells"])

    def test_import_rejects_corrupt_png_and_frame_hash_mismatch(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_spritesheet_with_sidecar(grid, profile)
        corrupt_png = b"not-a-png" + exported["png_bytes"][8:]
        wrong_frame_hash_sidecar = json.loads(json.dumps(exported["sidecar"]))
        wrong_frame_hash_sidecar["animation_binding"]["frames"][0]["pixel_hash"] = "sha256:not-the-frame"

        corrupt_result = import_spritesheet_with_sidecar(
            corrupt_png,
            exported["sidecar"],
        )
        wrong_hash_result = import_spritesheet_with_sidecar(
            exported["png_bytes"],
            wrong_frame_hash_sidecar,
        )

        self.assertFalse(corrupt_result["ok"])
        self.assertIn("png_signature_invalid", corrupt_result["error_families"])
        self.assertFalse(wrong_hash_result["ok"])
        self.assertIn("spritesheet_frame_hash_mismatch", wrong_hash_result["error_families"])

    def test_lab_report_closes_fixed_grid_spritesheet_metadata_only(self):
        report = run_spritesheet_sidecar_decoder_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("spritesheet_sidecar_decoder_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(3, report["spritesheet_roundtrip_success_count"])
        self.assertEqual(2, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertIn("spritesheet_fixed_grid_frame_metadata_decoder", report["closed_states"])
        self.assertNotIn("spritesheet_decoder", report["blocked_states"])
        self.assertNotIn("spritesheet_variant_layout_coverage", report["blocked_states"])
        self.assertIn("spritesheet_packed_rotation_trim_decoder", report["blocked_states"])
        self.assertIn("runtime_animation_playback", report["blocked_states"])
        self.assertNotIn("third_party_project_decoder", report["blocked_states"])
        self.assertIn("full_project_format_coverage", report["blocked_states"])

    def test_write_artifacts_creates_spritesheets_sidecars_report_and_app_payload(self):
        report = run_spritesheet_sidecar_decoder_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_spritesheet_sidecar_decoder_artifacts(output_dir, report)

            summary_path = output_dir / "spritesheet_sidecar_decoder_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_spritesheet.png").exists())
            self.assertTrue((output_dir / "slip_lcd_seed_spritesheet_sidecar.json").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "spritesheet_sidecar_decoder_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_SPRITESHEET_SIDECAR_DECODER", app_data)


def synthetic_clip_frames(grid: dict, count: int = 4, clip: str = "ill") -> dict:
    """Codec-level clip frames (cell lists + animation blocks); the
    workshop server test pins the REAL engine clip frames end-to-end."""
    from copy import deepcopy

    frames = []
    for index in range(count):
        cells = deepcopy(grid["cells"])
        for cell in cells[:index]:
            cell["visual"] = "#00{:02x}40".format(64 + index * 8)
        frames.append(
            {
                "cells": cells,
                "animation": {
                    "clip": clip,
                    "frame_index": index,
                    "frame_count": count,
                    "anchors": [
                        [cell["x"], cell["y"]]
                        for cell in cells
                        if cell.get("animation_anchor")
                    ],
                },
            }
        )
    return {"clip": clip, "frames": frames}


class ClipFrameSpritesheetTests(unittest.TestCase):
    """H3 (cycle 18): the spritesheet strip gains clip frames as an
    additive keyword — no clip_frames, no change to the 3-frame proof."""

    def test_export_with_clip_frames_packs_every_frame(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        bundle = export_spritesheet_with_sidecar(
            grid, profile, clip_frames=synthetic_clip_frames(grid)
        )
        frame_width, frame_height = grid["grid_size"]
        decoded = decode_png_rgba(bundle["png_bytes"])
        self.assertEqual(frame_width * 4, decoded["width"])
        binding = bundle["sidecar"]["animation_binding"]
        self.assertEqual(4, binding["frame_count"])
        self.assertEqual(
            {"kind": "clip_frames", "clip": "ill"}, binding["frame_source"]
        )
        for index, frame in enumerate(binding["frames"]):
            self.assertEqual(index, frame["animation"]["frame_index"])
            self.assertEqual("ill", frame["animation"]["clip"])
            self.assertEqual(f"ill_frame_{index}", frame["visual_delta"])

    def test_clip_frame_export_round_trips_the_semantic_grid(self):
        profile = load_profile(VALID_PROFILE_PATHS[1])
        grid = first_grid_for(profile)
        bundle = export_spritesheet_with_sidecar(
            grid, profile, clip_frames=synthetic_clip_frames(grid)
        )
        imported = import_spritesheet_with_sidecar(
            bundle["png_bytes"], bundle["sidecar"], source_grid=grid
        )
        self.assertTrue(imported["ok"], imported.get("errors"))
        self.assertEqual(1.0, imported["semantic_fidelity"])

    def test_three_frame_proof_is_untouched_without_clip_frames(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        bundle = export_spritesheet_with_sidecar(grid, profile)
        binding = bundle["sidecar"]["animation_binding"]
        self.assertEqual(3, binding["frame_count"])
        self.assertNotIn("frame_source", binding)


if __name__ == "__main__":
    unittest.main()
