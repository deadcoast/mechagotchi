import argparse
import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME_DIR = ROOT / "labs" / "grid_genome"
if str(GRID_GENOME_DIR) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME_DIR))

from slip import is_grid_aligned
from validator import validate_grid

from external_metadata_sidecar import build_sidecar_for_grid, restore_grid_from_sidecar
from spritesheet_sidecar_decoder import (
    DEFAULT_FRAME_DURATIONS_MS,
    render_spritesheet_frame_pixels,
)
from standard_image_sidecar_decoder import (
    PNGDecodeError,
    decode_png_rgba,
    encode_png_rgba,
)
from workshop_editor import compare_semantic_grid_fidelity


REPORT_PATH = Path("data/workshop_editor/spritesheet_packed_runtime_decoder_stage0.json")
DATA_PATH = Path("data/workshop_editor/spritesheet_packed_runtime_decoder_data.js")


def export_packed_runtime_spritesheet_with_sidecar(
    grid: dict,
    slip_profile: dict,
) -> dict:
    frame_width, frame_height = grid["grid_size"]
    if [frame_width, frame_height] != [8, 8]:
        raise ValueError("Stage 0 packed runtime proof expects 8x8 grids")

    background = _background_rgba(grid)
    frame_pixels = [
        render_spritesheet_frame_pixels(grid, frame_index)
        for frame_index in range(len(DEFAULT_FRAME_DURATIONS_MS))
    ]
    packed_frames = _packed_frame_specs(
        grid,
        frame_pixels,
        background,
    )
    sheet_width = sum(frame["rect"]["w"] for frame in packed_frames) + len(packed_frames) - 1
    sheet_height = max(frame["rect"]["h"] for frame in packed_frames) + 1
    x_cursor = 0
    for frame in packed_frames:
        frame["rect"]["x"] = x_cursor
        frame["rect"]["y"] = 0
        x_cursor += frame["rect"]["w"] + 1

    sheet_pixels = _compose_packed_sheet(sheet_width, sheet_height, packed_frames)
    png_bytes = encode_png_rgba(sheet_width, sheet_height, sheet_pixels)
    asset = _asset_from_packed_png(
        png_bytes,
        asset_id=f"{slip_profile['profile_id']}_packed_runtime.spritesheet.png",
        uri=(
            "generated://workshop/spritesheet-packed-runtime/"
            f"{slip_profile['profile_id']}_packed_runtime.spritesheet.png"
        ),
        frame_count=len(frame_pixels),
    )
    sidecar = build_sidecar_for_grid(grid, slip_profile, asset)
    sidecar["sidecar_id"] = f"{grid['grid_id']}_packed_runtime_spritesheet_sidecar"
    sidecar["animation_binding"] = _animation_binding(
        grid,
        sheet_width,
        sheet_height,
        packed_frames,
        background,
        sidecar["integrity"]["semantic_overlay_hash"],
    )
    sidecar["limitations"] = [
        "Stage 0 packed runtime decoder supports sidecar-described trim and 90-degree rotation only.",
        "Runtime playback is a deterministic metadata playback model, not a production renderer.",
        "Semantic grid metadata is restored from the sidecar; PNG pixels remain a visual carrier.",
    ]
    return {
        "png_bytes": png_bytes,
        "asset": asset,
        "sidecar": sidecar,
        "frame_pixels": frame_pixels,
        "sheet_pixel_count": len(sheet_pixels),
    }


def import_packed_runtime_spritesheet_with_sidecar(
    png_bytes: bytes,
    sidecar: dict,
    source_grid: dict | None = None,
) -> dict:
    try:
        decoded = decode_png_rgba(png_bytes)
    except PNGDecodeError as exc:
        return _failed_import("png", exc.family, exc.message)

    asset = _asset_from_packed_png(
        png_bytes,
        asset_id=sidecar.get("asset_binding", {}).get(
            "asset_id",
            "unknown.packed-runtime.spritesheet.png",
        ),
        uri=sidecar.get("asset_binding", {}).get(
            "uri",
            "unknown://packed-runtime-spritesheet",
        ),
        frame_count=sidecar.get("asset_binding", {}).get("frame_count", 0),
    )
    validation = validate_packed_runtime_sidecar_binding(sidecar, asset, decoded)
    if not validation["ok"]:
        return {
            "ok": False,
            "asset": asset,
            "decoded_png": _decoded_summary(decoded),
            "validation": validation,
            "errors": validation["errors"],
            "error_families": validation["error_families"],
        }

    restored = restore_grid_from_sidecar(sidecar, asset, validate=False)
    profile = sidecar["slip_binding"]["profile_snapshot"]
    grid_validation = validate_grid(restored)
    alignment = is_grid_aligned(restored, profile)
    semantic_source = source_grid or restored
    diff = compare_semantic_grid_fidelity(semantic_source, restored)
    reconstructed = reconstruct_packed_runtime_frames(decoded, sidecar)
    playback_timeline = build_runtime_playback_timeline(sidecar, decoded)
    reconstructed_fidelity = _reconstructed_frame_fidelity(reconstructed["frames"])
    runtime_fidelity = _runtime_frame_fidelity(playback_timeline)
    return {
        "ok": (
            grid_validation.ok
            and alignment.ok
            and reconstructed["ok"]
            and reconstructed_fidelity == 1.0
            and runtime_fidelity == 1.0
        ),
        "asset": asset,
        "decoded_png": _decoded_summary(decoded),
        "validation": validation,
        "restored_grid": restored,
        "frame_count": len(reconstructed["frames"]),
        "frame_summaries": [_frame_summary(frame) for frame in reconstructed["frames"]],
        "runtime_playback": {
            "timeline": playback_timeline,
            "sample_count": len(playback_timeline),
            "loop": bool(sidecar["animation_binding"].get("loop")),
            "total_duration_ms": sidecar["animation_binding"]["total_duration_ms"],
        },
        "semantic_diff": diff,
        "semantic_fidelity": _semantic_fidelity(diff, semantic_source),
        "reconstructed_frame_fidelity": reconstructed_fidelity,
        "runtime_frame_fidelity": runtime_fidelity,
        "errors": [],
        "error_families": [],
    }


def validate_packed_runtime_sidecar_binding(
    sidecar: dict,
    asset: dict,
    decoded_png: dict,
) -> dict:
    errors = []
    binding = sidecar.get("asset_binding", {})
    animation = sidecar.get("animation_binding", {})
    if binding.get("asset_id") != asset.get("asset_id"):
        errors.append(_error("asset_binding.asset_id", "asset_id_mismatch"))
    if binding.get("format_id") != "spritesheet_png":
        errors.append(_error("asset_binding.format_id", "asset_format_mismatch"))
    if binding.get("content_hash") != asset.get("content_hash"):
        errors.append(_error("asset_binding.content_hash", "asset_hash_mismatch"))
    if binding.get("width") != decoded_png.get("width") or binding.get("height") != decoded_png.get("height"):
        errors.append(_error("asset_binding.dimensions", "asset_dimension_mismatch"))
    if binding.get("frame_count") != animation.get("frame_count"):
        errors.append(_error("asset_binding.frame_count", "asset_frame_count_mismatch"))
    if animation.get("animation_model") != "packed_runtime_sidecar_v1":
        errors.append(_error("animation_binding.animation_model", "animation_model_mismatch"))
    if animation.get("sheet_width") != decoded_png.get("width") or animation.get("sheet_height") != decoded_png.get("height"):
        errors.append(_error("animation_binding.sheet_size", "spritesheet_sheet_size_mismatch"))

    errors.extend(_packed_frame_geometry_errors(animation, decoded_png))
    if not errors:
        reconstructed = reconstruct_packed_runtime_frames(decoded_png, sidecar)
        errors.extend(reconstructed["errors"])

    profile = sidecar.get("slip_binding", {}).get("profile_snapshot", {})
    restored = restore_grid_from_sidecar(sidecar, asset, validate=False) if profile else {}
    if restored and not errors:
        grid_validation = validate_grid(restored)
        if not grid_validation.ok:
            errors.extend(_error("$", "restored_grid_invalid", message) for message in grid_validation.errors)
        alignment = is_grid_aligned(restored, profile)
        if not alignment.ok:
            errors.extend(_error("$", "restored_grid_not_slip_aligned", message) for message in alignment.errors)

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "error_families": sorted({error["family"] for error in errors}),
    }


def reconstruct_packed_runtime_frames(decoded_png: dict, sidecar: dict) -> dict:
    animation = sidecar.get("animation_binding", {})
    background = tuple(animation.get("background_rgba", [0, 0, 0, 0]))
    pixels = decoded_png["pixels"]
    sheet_width = decoded_png["width"]
    reconstructed_frames = []
    errors = []
    for frame in animation.get("frames", []):
        rect = frame["rect"]
        trim = frame["trim"]
        source_size = frame["source_size"]
        packed_pixels = _extract_rect_pixels(
            pixels,
            sheet_width,
            rect["x"],
            rect["y"],
            rect["w"],
            rect["h"],
        )
        packed_hash = _hash_pixels(packed_pixels)
        if packed_hash != frame.get("packed_pixel_hash"):
            errors.append(_error("animation_binding.frames.packed_pixel_hash", "spritesheet_frame_hash_mismatch"))
        if frame["rotation_degrees"] == 90:
            crop_pixels = _rotate_counterclockwise(packed_pixels, rect["w"], rect["h"])
        else:
            crop_pixels = packed_pixels
        canvas = [background] * (source_size["w"] * source_size["h"])
        for y in range(trim["h"]):
            for x in range(trim["w"]):
                canvas_index = (trim["y"] + y) * source_size["w"] + trim["x"] + x
                crop_index = y * trim["w"] + x
                canvas[canvas_index] = crop_pixels[crop_index]
        canonical_hash = _hash_pixels(canvas)
        canonical_match = canonical_hash == frame.get("canonical_pixel_hash")
        if not canonical_match:
            errors.append(_error("animation_binding.frames.canonical_pixel_hash", "spritesheet_frame_hash_mismatch"))
        reconstructed_frames.append(
            {
                "frame_index": frame["frame_index"],
                "rect": deepcopy(rect),
                "duration_ms": frame["duration_ms"],
                "rotation_degrees": frame["rotation_degrees"],
                "trim": deepcopy(trim),
                "pixels": canvas,
                "packed_pixel_hash": packed_hash,
                "canonical_pixel_hash": canonical_hash,
                "packed_hash_match": packed_hash == frame.get("packed_pixel_hash"),
                "canonical_hash_match": canonical_match,
            }
        )
    return {
        "ok": len(errors) == 0,
        "frames": reconstructed_frames,
        "errors": errors,
        "error_families": sorted({error["family"] for error in errors}),
    }


def build_runtime_playback_timeline(
    sidecar: dict,
    decoded_png: dict,
    sample_times_ms: list[int] | None = None,
) -> list[dict]:
    animation = sidecar["animation_binding"]
    frames = sorted(animation["frames"], key=lambda item: item["playback_order"])
    total_duration = animation["total_duration_ms"]
    if sample_times_ms is None:
        sample_times_ms = [
            0,
            frames[0]["duration_ms"],
            frames[0]["duration_ms"] + frames[1]["duration_ms"],
            total_duration,
            total_duration + frames[0]["duration_ms"],
        ]
    reconstructed = reconstruct_packed_runtime_frames(decoded_png, sidecar)
    hashes_by_index = {
        frame["frame_index"]: frame["canonical_pixel_hash"]
        for frame in reconstructed["frames"]
    }
    timeline = []
    for sample_time in sample_times_ms:
        effective_time = sample_time % total_duration if animation.get("loop") else min(sample_time, total_duration - 1)
        frame = _frame_at_time(frames, effective_time)
        canonical_hash = hashes_by_index.get(frame["frame_index"])
        timeline.append(
            {
                "time_ms": sample_time,
                "effective_time_ms": effective_time,
                "frame_index": frame["frame_index"],
                "duration_ms": frame["duration_ms"],
                "visual_delta": frame["visual_delta"],
                "canonical_pixel_hash": canonical_hash,
                "expected_canonical_pixel_hash": frame["canonical_pixel_hash"],
                "canonical_hash_match": canonical_hash == frame["canonical_pixel_hash"],
            }
        )
    return timeline


def run_spritesheet_packed_runtime_decoder_lab(
    profile_paths: list[Path],
    generated_root: Path,
) -> dict:
    packed_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        exported = export_packed_runtime_spritesheet_with_sidecar(grid, profile)
        imported = import_packed_runtime_spritesheet_with_sidecar(
            exported["png_bytes"],
            exported["sidecar"],
            source_grid=grid,
        )
        restored = imported.get("restored_grid", {})
        grid_validation = validate_grid(restored) if restored else None
        alignment = is_grid_aligned(restored, profile) if restored else None
        packed_results.append(
            {
                "profile_id": profile["profile_id"],
                "profile_path": _portable(profile_path),
                "grid_path": _portable(grid_path),
                "png_file_name": f"{profile['profile_id']}_packed_runtime_spritesheet.png",
                "sidecar_file_name": f"{profile['profile_id']}_packed_runtime_sidecar.json",
                "png_bytes_hex": exported["png_bytes"].hex(),
                "png_byte_count": len(exported["png_bytes"]),
                "asset": exported["asset"],
                "sidecar": exported["sidecar"],
                "decoded_png": imported.get("decoded_png"),
                "import_result": _compact_import_result(imported),
                "restored_grid_validation": {
                    "valid": bool(grid_validation and grid_validation.ok),
                    "errors": grid_validation.errors if grid_validation else [],
                    "slip_aligned": bool(alignment and alignment.ok),
                    "slip_errors": alignment.errors if alignment else [],
                },
                "semantic_diff": imported.get("semantic_diff", {}),
                "semantic_fidelity": imported.get("semantic_fidelity", 0.0),
                "reconstructed_frame_fidelity": imported.get("reconstructed_frame_fidelity", 0.0),
                "runtime_frame_fidelity": imported.get("runtime_frame_fidelity", 0.0),
                "runtime_playback": imported.get("runtime_playback", {}),
                "frame_count": imported.get("frame_count", 0),
            }
        )

    invalid_probe_results = _invalid_probe_results(packed_results[0])
    success_count = sum(
        1
        for result in packed_results
        if result["import_result"]["ok"]
        and result["restored_grid_validation"]["valid"]
        and result["restored_grid_validation"]["slip_aligned"]
        and result["semantic_fidelity"] == 1.0
        and result["reconstructed_frame_fidelity"] == 1.0
        and result["runtime_frame_fidelity"] == 1.0
    )
    invalid_rejected_count = sum(1 for result in invalid_probe_results if not result["ok"])
    return {
        "artifact_id": "spritesheet_packed_runtime_decoder_stage0",
        "status": "research_spritesheet_packed_runtime_decoder_no_package_code",
        "date": "2026-05-13",
        "purpose": (
            "Extend the spritesheet sidecar proof to packed trim/rotation atlas "
            "frames and a deterministic looped runtime playback model."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
            "labs/workshop_editor/spritesheet_sidecar_decoder.py",
            "labs/workshop_editor/spritesheet_layout_variant_decoder.py",
            "labs/workshop_editor/spritesheet_packed_runtime_decoder.py",
        ],
        "external_anchors": [
            {
                "source": "Aseprite sprite-sheet documentation",
                "url": "https://www.aseprite.org/docs/sprite-sheet/",
                "used_for": "Packed spritesheet workflow and frame metadata boundary.",
            },
            {
                "source": "Aseprite CLI documentation",
                "url": "https://aseprite.com/docs/cli/",
                "used_for": "Packed sheet type, trimming, sheet size, and JSON data export context.",
            },
            {
                "source": "W3C PNG specification",
                "url": "https://www.w3.org/TR/png-3/",
                "used_for": "PNG remains the visual carrier for packed atlas spritesheets.",
            },
        ],
        "profile_count": len(profile_paths),
        "packed_roundtrip_count": len(packed_results),
        "packed_roundtrip_success_count": success_count,
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "metrics": {
            "packed_roundtrip_success_rate": _ratio(success_count, len(packed_results)),
            "mean_semantic_fidelity": round(
                sum(result["semantic_fidelity"] for result in packed_results)
                / max(1, len(packed_results)),
                6,
            ),
            "mean_reconstructed_frame_fidelity": round(
                sum(result["reconstructed_frame_fidelity"] for result in packed_results)
                / max(1, len(packed_results)),
                6,
            ),
            "mean_runtime_frame_fidelity": round(
                sum(result["runtime_frame_fidelity"] for result in packed_results)
                / max(1, len(packed_results)),
                6,
            ),
            "invalid_probe_rejection_rate": _ratio(
                invalid_rejected_count,
                len(invalid_probe_results),
            ),
            "default_runtime_sample_count": 5,
        },
        "packed_results": packed_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "spritesheet_packed_rotation_trim_decoder",
            "runtime_animation_playback_sidecar_model",
            "spritesheet_packed_runtime_sidecar_export",
            "spritesheet_packed_runtime_sidecar_import",
            "spritesheet_packed_frame_hash_validation",
            "spritesheet_packed_sidecar_semantic_restore",
        ],
        "blocked_states": [
            "Adam7/APNG/full PNG conformance",
            "full project-format coverage",
            "arbitrary Aseprite project schema coverage",
            "live external editor rewrite validation",
            "package runtime lifecycle integration",
            "manual readability calibration",
            "profile-weighted evolution",
            "community profile packs",
        ],
        "decision": "prototype_spritesheet_packed_runtime_decoder",
        "next_research_step": (
            "Keep workshop metadata writer and full editor project coverage "
            "blocked until live external editor rewrite validation, "
            "arbitrary Aseprite project schema coverage, and full project format "
            "tests exist."
        ),
    }


def write_spritesheet_packed_runtime_decoder_artifacts(
    output_dir: Path,
    report: dict,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(
        output_dir / "spritesheet_packed_runtime_decoder_stage0.json",
        _json_report(report),
    )
    for result in report["packed_results"]:
        (output_dir / result["png_file_name"]).write_bytes(
            bytes.fromhex(result["png_bytes_hex"])
        )
        _write_json(output_dir / result["sidecar_file_name"], result["sidecar"])
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "spritesheet_packed_runtime_decoder_data.js").write_text(
        "window.MECHAGOTCHI_SPRITESHEET_PACKED_RUNTIME_DECODER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _packed_frame_specs(
    grid: dict,
    frame_pixels: list[list[tuple[int, int, int, int]]],
    background: tuple[int, int, int, int],
) -> list[dict]:
    specs = []
    transforms = [
        {"visual_delta": "base_pose", "trim": False, "rotation_degrees": 0},
        {"visual_delta": "sensor_blink", "trim": True, "rotation_degrees": 90},
        {"visual_delta": "anchor_pulse", "trim": True, "rotation_degrees": 0},
    ]
    source_width, source_height = grid["grid_size"]
    for index, transform in enumerate(transforms):
        source_pixels = frame_pixels[index]
        if transform["trim"]:
            trim = _trim_bounds(source_pixels, source_width, source_height, background)
        else:
            trim = {"x": 0, "y": 0, "w": source_width, "h": source_height}
        crop_pixels = _extract_rect_pixels(
            source_pixels,
            source_width,
            trim["x"],
            trim["y"],
            trim["w"],
            trim["h"],
        )
        if transform["rotation_degrees"] == 90:
            packed_pixels = _rotate_clockwise(crop_pixels, trim["w"], trim["h"])
            rect_width = trim["h"]
            rect_height = trim["w"]
        else:
            packed_pixels = crop_pixels
            rect_width = trim["w"]
            rect_height = trim["h"]
        specs.append(
            {
                "frame_index": index,
                "grid_id": grid["grid_id"],
                "playback_order": index,
                "rect": {"x": 0, "y": 0, "w": rect_width, "h": rect_height},
                "duration_ms": DEFAULT_FRAME_DURATIONS_MS[index],
                "source_size": {"w": source_width, "h": source_height},
                "trim": trim,
                "trimmed": trim != {"x": 0, "y": 0, "w": source_width, "h": source_height},
                "rotation_degrees": transform["rotation_degrees"],
                "visual_delta": transform["visual_delta"],
                "canonical_pixel_hash": _hash_pixels(source_pixels),
                "packed_pixel_hash": _hash_pixels(packed_pixels),
                "packed_pixels": packed_pixels,
            }
        )
    return specs


def _compose_packed_sheet(
    sheet_width: int,
    sheet_height: int,
    packed_frames: list[dict],
) -> list[tuple[int, int, int, int]]:
    sheet = [(0, 0, 0, 0)] * (sheet_width * sheet_height)
    for frame in packed_frames:
        rect = frame["rect"]
        for y in range(rect["h"]):
            for x in range(rect["w"]):
                sheet_index = (rect["y"] + y) * sheet_width + rect["x"] + x
                packed_index = y * rect["w"] + x
                sheet[sheet_index] = frame["packed_pixels"][packed_index]
    return sheet


def _animation_binding(
    grid: dict,
    sheet_width: int,
    sheet_height: int,
    packed_frames: list[dict],
    background: tuple[int, int, int, int],
    semantic_hash: str,
) -> dict:
    frames = []
    for frame in packed_frames:
        frame_payload = {
            key: deepcopy(frame[key])
            for key in [
                "frame_index",
                "grid_id",
                "playback_order",
                "rect",
                "duration_ms",
                "source_size",
                "trim",
                "trimmed",
                "rotation_degrees",
                "visual_delta",
                "canonical_pixel_hash",
                "packed_pixel_hash",
            ]
        }
        frame_payload["semantic_overlay_hash"] = semantic_hash
        frames.append(frame_payload)
    return {
        "animation_model": "packed_runtime_sidecar_v1",
        "sheet_width": sheet_width,
        "sheet_height": sheet_height,
        "frame_width": grid["grid_size"][0],
        "frame_height": grid["grid_size"][1],
        "frame_count": len(frames),
        "loop": True,
        "timebase": "milliseconds",
        "total_duration_ms": sum(frame["duration_ms"] for frame in frames),
        "background_rgba": list(background),
        "runtime_playback": {
            "model": "looped_frame_duration_sampler_v1",
            "sampling_rule": "time_ms modulo total_duration_ms selects first cumulative frame interval",
        },
        "frames": frames,
        "limitations": [
            "Only 0 and 90-degree clockwise packed rotations are covered.",
            "Only transparent-free source grids reconstructed over the profile background are covered.",
            "Runtime playback is validated as sidecar timing metadata, not as browser or engine rendering.",
        ],
    }


def _packed_frame_geometry_errors(animation: dict, decoded_png: dict) -> list[dict]:
    errors = []
    sheet_width = decoded_png.get("width", 0)
    sheet_height = decoded_png.get("height", 0)
    frames = animation.get("frames", [])
    if len(frames) != animation.get("frame_count"):
        errors.append(_error("animation_binding.frames", "asset_frame_count_mismatch"))

    occupied = set()
    seen_indices = set()
    total_duration = 0
    for frame in frames:
        frame_index = frame.get("frame_index")
        if frame_index in seen_indices:
            errors.append(_error("animation_binding.frames", "duplicate_frame_index"))
        seen_indices.add(frame_index)
        duration = frame.get("duration_ms")
        if type(duration) is not int or duration <= 0:
            errors.append(_error("animation_binding.frames.duration_ms", "runtime_frame_duration_invalid"))
        else:
            total_duration += duration
        rotation = frame.get("rotation_degrees")
        if rotation not in {0, 90}:
            errors.append(_error("animation_binding.frames.rotation_degrees", "spritesheet_frame_rotation_unsupported"))
            continue

        rect = frame.get("rect", {})
        trim = frame.get("trim", {})
        source_size = frame.get("source_size", {})
        rect_values = [rect.get(key) for key in ["x", "y", "w", "h"]]
        trim_values = [trim.get(key) for key in ["x", "y", "w", "h"]]
        source_values = [source_size.get(key) for key in ["w", "h"]]
        if not all(type(value) is int for value in rect_values + trim_values + source_values):
            errors.append(_error("animation_binding.frames.geometry", "spritesheet_frame_geometry_invalid"))
            continue
        x, y, rect_width, rect_height = rect_values
        trim_x, trim_y, trim_width, trim_height = trim_values
        source_width, source_height = source_values
        if rect_width <= 0 or rect_height <= 0 or trim_width <= 0 or trim_height <= 0:
            errors.append(_error("animation_binding.frames.geometry", "spritesheet_frame_geometry_invalid"))
            continue
        if trim_x < 0 or trim_y < 0 or trim_x + trim_width > source_width or trim_y + trim_height > source_height:
            errors.append(_error("animation_binding.frames.trim", "spritesheet_frame_trim_out_of_bounds"))
            continue
        expected_rect_size = (
            {"w": trim_height, "h": trim_width}
            if rotation == 90
            else {"w": trim_width, "h": trim_height}
        )
        if {"w": rect_width, "h": rect_height} != expected_rect_size:
            errors.append(_error("animation_binding.frames.rect", "spritesheet_frame_rect_transform_mismatch"))
            continue
        if x < 0 or y < 0 or x + rect_width > sheet_width or y + rect_height > sheet_height:
            errors.append(_error("animation_binding.frames.rect", "spritesheet_frame_rect_out_of_bounds"))
            continue
        for yy in range(y, y + rect_height):
            for xx in range(x, x + rect_width):
                coordinate = (xx, yy)
                if coordinate in occupied:
                    errors.append(_error("animation_binding.frames.rect", "spritesheet_frame_rect_overlap"))
                    break
                occupied.add(coordinate)
            if errors and errors[-1]["family"] == "spritesheet_frame_rect_overlap":
                break
    if total_duration and animation.get("total_duration_ms") != total_duration:
        errors.append(_error("animation_binding.total_duration_ms", "runtime_total_duration_mismatch"))
    return errors


def _asset_from_packed_png(
    png_bytes: bytes,
    *,
    asset_id: str,
    uri: str,
    frame_count: int,
) -> dict:
    decoded = decode_png_rgba(png_bytes)
    return {
        "asset_id": asset_id,
        "format_id": "spritesheet_png",
        "media_type": "image/png",
        "uri": uri,
        "width": decoded["width"],
        "height": decoded["height"],
        "frame_count": frame_count,
        "content_hash": _hash_bytes(png_bytes),
        "semantic_policy": "sidecar_required",
    }


def _invalid_probe_results(reference_result: dict) -> list[dict]:
    png_bytes = bytes.fromhex(reference_result["png_bytes_hex"])
    sidecar = reference_result["sidecar"]

    unsupported_rotation_sidecar = deepcopy(sidecar)
    unsupported_rotation_sidecar["animation_binding"]["frames"][1]["rotation_degrees"] = 45

    bad_trim_sidecar = deepcopy(sidecar)
    bad_trim_sidecar["animation_binding"]["frames"][2]["trim"]["x"] = 8

    wrong_hash_sidecar = deepcopy(sidecar)
    wrong_hash_sidecar["animation_binding"]["frames"][0]["canonical_pixel_hash"] = "sha256:not-the-frame"

    bad_duration_sidecar = deepcopy(sidecar)
    bad_duration_sidecar["animation_binding"]["frames"][0]["duration_ms"] = 0
    bad_duration_sidecar["animation_binding"]["total_duration_ms"] = (
        sidecar["animation_binding"]["total_duration_ms"]
        - sidecar["animation_binding"]["frames"][0]["duration_ms"]
    )

    return [
        _compact_import_result(
            import_packed_runtime_spritesheet_with_sidecar(png_bytes, unsupported_rotation_sidecar)
        ),
        _compact_import_result(
            import_packed_runtime_spritesheet_with_sidecar(png_bytes, bad_trim_sidecar)
        ),
        _compact_import_result(
            import_packed_runtime_spritesheet_with_sidecar(png_bytes, wrong_hash_sidecar)
        ),
        _compact_import_result(
            import_packed_runtime_spritesheet_with_sidecar(png_bytes, bad_duration_sidecar)
        ),
    ]


def _frame_at_time(frames: list[dict], effective_time: int) -> dict:
    cursor = 0
    for frame in frames:
        cursor += frame["duration_ms"]
        if effective_time < cursor:
            return frame
    return frames[-1]


def _reconstructed_frame_fidelity(frames: list[dict]) -> float:
    if not frames:
        return 0.0
    matches = sum(1 for frame in frames if frame["canonical_hash_match"])
    return _ratio(matches, len(frames))


def _runtime_frame_fidelity(timeline: list[dict]) -> float:
    if not timeline:
        return 0.0
    matches = sum(1 for event in timeline if event["canonical_hash_match"])
    return _ratio(matches, len(timeline))


def _trim_bounds(
    pixels: list[tuple[int, int, int, int]],
    width: int,
    height: int,
    background: tuple[int, int, int, int],
) -> dict:
    coordinates = [
        (x, y)
        for y in range(height)
        for x in range(width)
        if pixels[y * width + x] != background
    ]
    if not coordinates:
        return {"x": 0, "y": 0, "w": width, "h": height}
    min_x = min(x for x, _y in coordinates)
    max_x = max(x for x, _y in coordinates)
    min_y = min(y for _x, y in coordinates)
    max_y = max(y for _x, y in coordinates)
    return {
        "x": min_x,
        "y": min_y,
        "w": max_x - min_x + 1,
        "h": max_y - min_y + 1,
    }


def _extract_rect_pixels(
    pixels: list[tuple[int, int, int, int]],
    sheet_width: int,
    x: int,
    y: int,
    width: int,
    height: int,
) -> list[tuple[int, int, int, int]]:
    extracted = []
    for yy in range(y, y + height):
        row_start = yy * sheet_width + x
        extracted.extend(pixels[row_start : row_start + width])
    return extracted


def _rotate_clockwise(
    pixels: list[tuple[int, int, int, int]],
    width: int,
    height: int,
) -> list[tuple[int, int, int, int]]:
    rotated = [(0, 0, 0, 0)] * (width * height)
    rotated_width = height
    for y in range(height):
        for x in range(width):
            dest_x = height - 1 - y
            dest_y = x
            rotated[dest_y * rotated_width + dest_x] = pixels[y * width + x]
    return rotated


def _rotate_counterclockwise(
    pixels: list[tuple[int, int, int, int]],
    width: int,
    height: int,
) -> list[tuple[int, int, int, int]]:
    rotated = [(0, 0, 0, 0)] * (width * height)
    rotated_width = height
    for y in range(height):
        for x in range(width):
            dest_x = y
            dest_y = width - 1 - x
            rotated[dest_y * rotated_width + dest_x] = pixels[y * width + x]
    return rotated


def _background_rgba(grid: dict) -> tuple[int, int, int, int]:
    palette = grid["palette"]
    background_index = palette.get("background_index", 0)
    return _hex_to_rgba(palette["colors"][background_index])


def _hex_to_rgba(value: str) -> tuple[int, int, int, int]:
    if not isinstance(value, str) or len(value) != 7 or not value.startswith("#"):
        raise ValueError(f"expected #RRGGBB color, got {value!r}")
    return (
        int(value[1:3], 16),
        int(value[3:5], 16),
        int(value[5:7], 16),
        255,
    )


def _first_grid_path(profile: dict, generated_root: Path) -> Path:
    grid_paths = sorted((generated_root / profile["profile_id"]).glob("*.json"))
    if not grid_paths:
        raise ValueError(f"no generated grids found for profile: {profile['profile_id']}")
    return grid_paths[0]


def _semantic_fidelity(diff: dict, source: dict) -> float:
    source_count = max(1, len(source.get("cells", [])))
    problem_count = (
        len(diff["changed_cells"])
        + len(diff["missing_cells"])
        + len(diff["added_cells"])
    )
    return round(max(0.0, 1.0 - problem_count / source_count), 6)


def _frame_summary(frame: dict) -> dict:
    return {
        "frame_index": frame["frame_index"],
        "rect": frame["rect"],
        "duration_ms": frame["duration_ms"],
        "rotation_degrees": frame["rotation_degrees"],
        "trim": frame["trim"],
        "packed_pixel_hash": frame["packed_pixel_hash"],
        "canonical_pixel_hash": frame["canonical_pixel_hash"],
        "canonical_hash_match": frame["canonical_hash_match"],
    }


def _decoded_summary(decoded: dict) -> dict:
    return {
        "width": decoded["width"],
        "height": decoded["height"],
        "bit_depth": decoded["bit_depth"],
        "color_type": decoded["color_type"],
        "pixel_count": len(decoded["pixels"]),
        "chunks": decoded["chunks"],
    }


def _compact_import_result(result: dict) -> dict:
    return {
        "ok": result["ok"],
        "asset": result.get("asset"),
        "decoded_png": result.get("decoded_png"),
        "validation": result.get("validation"),
        "semantic_fidelity": result.get("semantic_fidelity", 0.0),
        "reconstructed_frame_fidelity": result.get("reconstructed_frame_fidelity", 0.0),
        "runtime_frame_fidelity": result.get("runtime_frame_fidelity", 0.0),
        "errors": result.get("errors", []),
        "error_families": result.get("error_families", []),
    }


def _failed_import(path: str, family: str, message: str) -> dict:
    error = _error(path, family, message)
    return {
        "ok": False,
        "errors": [error],
        "error_families": [family],
    }


def _error(path: str, family: str, message: str | None = None) -> dict:
    return {
        "path": path,
        "family": family,
        "message": message or family.replace("_", " "),
    }


def _hash_pixels(pixels: list[tuple[int, int, int, int]]) -> str:
    raw = bytearray()
    for pixel in pixels:
        raw.extend(pixel)
    return _hash_bytes(bytes(raw))


def _hash_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _portable(path: Path) -> str:
    return str(path).replace("\\", "/")


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def _json_report(report: dict) -> dict:
    payload = deepcopy(report)
    for result in payload["packed_results"]:
        result.pop("png_bytes_hex", None)
    return payload


def _app_payload(report: dict) -> dict:
    json_report = _json_report(report)
    return {
        "report": {
            key: json_report[key]
            for key in [
                "artifact_id",
                "status",
                "profile_count",
                "packed_roundtrip_count",
                "packed_roundtrip_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "packed_summaries": [
            {
                "profile_id": result["profile_id"],
                "asset": result["asset"],
                "decoded_png": result["decoded_png"],
                "frame_count": result["frame_count"],
                "semantic_fidelity": result["semantic_fidelity"],
                "reconstructed_frame_fidelity": result["reconstructed_frame_fidelity"],
                "runtime_frame_fidelity": result["runtime_frame_fidelity"],
                "runtime_playback": result["runtime_playback"],
            }
            for result in json_report["packed_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# Spritesheet Packed Runtime Decoder Stage 0\n\n"
        "Packed trim/rotation spritesheet PNG proof with sidecar-described "
        "frame reconstruction and deterministic runtime playback sampling.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Packed round-trip successes: {report['packed_roundtrip_success_count']}"
        f"/{report['packed_roundtrip_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- Mean semantic fidelity: {metrics['mean_semantic_fidelity']}\n"
        f"- Mean reconstructed frame fidelity: {metrics['mean_reconstructed_frame_fidelity']}\n"
        f"- Mean runtime frame fidelity: {metrics['mean_runtime_frame_fidelity']}\n"
        f"- Decision: {report['decision']}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/workshop_editor/spritesheet_packed_runtime_decoder_stage0"),
    )
    parser.add_argument(
        "--generated-root",
        type=Path,
        default=Path("data/slips/multi_profile_generation_stage0"),
    )
    parser.add_argument("--profile", type=Path, action="append")
    args = parser.parse_args()
    profile_paths = args.profile or [
        Path("data/slips/valid/slip_lcd_seed.json"),
        Path("data/slips/valid/slip_gray_stable.json"),
        Path("data/slips/valid/slip_amber_social.json"),
    ]
    report = run_spritesheet_packed_runtime_decoder_lab(profile_paths, args.generated_root)
    write_spritesheet_packed_runtime_decoder_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_SPRITESHEET_PACKED_RUNTIME_DECODER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(_json_report(report), indent=2))


if __name__ == "__main__":
    main()
