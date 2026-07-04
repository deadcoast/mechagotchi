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
from spritesheet_sidecar_decoder import render_spritesheet_frame_pixels
from standard_image_sidecar_decoder import (
    PNGDecodeError,
    decode_png_rgba,
    encode_png_rgba,
)
from workshop_editor import compare_semantic_grid_fidelity


REPORT_PATH = ROOT / "data/workshop_editor/spritesheet_arbitrary_atlas_packer_stage0.json"
DATA_PATH = ROOT / "data/workshop_editor/spritesheet_arbitrary_atlas_packer_data.js"
FRAME_DURATIONS_MS = [100, 120, 140, 160, 180]
SOURCE_FRAME_SIZE = {"w": 8, "h": 8}

ARBITRARY_ATLAS_POLICIES = [
    {
        "algorithm_id": "shelf_height_desc",
        "file_slug": "shelf",
        "basis": "height-descending shelf baseline",
        "max_width": 20,
        "padding_px": 1,
        "allow_rotation": True,
    },
    {
        "algorithm_id": "maxrects_best_short_side_fit",
        "file_slug": "maxrects",
        "basis": "MaxRects-style best-short-side-fit rectangle placement",
        "max_width": 16,
        "padding_px": 1,
        "allow_rotation": True,
    },
]


def export_arbitrary_atlas_suite_with_sidecars(
    grid: dict,
    slip_profile: dict,
) -> list[dict]:
    if grid.get("grid_size") != [8, 8]:
        raise ValueError("Stage 0 arbitrary atlas proof expects 8x8 grids")

    regions = _build_source_regions(grid)
    exports = []
    for policy in ARBITRARY_ATLAS_POLICIES:
        placed_regions = pack_arbitrary_atlas_regions(regions, policy)
        sheet_pixels = _compose_atlas_sheet(
            placed_regions["sheet_width"],
            placed_regions["sheet_height"],
            placed_regions["frames"],
        )
        png_bytes = encode_png_rgba(
            placed_regions["sheet_width"],
            placed_regions["sheet_height"],
            sheet_pixels,
        )
        slug = policy["file_slug"]
        asset = _asset_from_atlas_png(
            png_bytes,
            asset_id=f"{slip_profile['profile_id']}_{slug}_arbitrary_atlas.png",
            uri=(
                "generated://workshop/spritesheet-arbitrary-atlas/"
                f"{slip_profile['profile_id']}_{slug}_arbitrary_atlas.png"
            ),
            frame_count=len(placed_regions["frames"]),
        )
        sidecar = build_sidecar_for_grid(grid, slip_profile, asset)
        sidecar["sidecar_id"] = f"{grid['grid_id']}_{slug}_arbitrary_atlas_sidecar"
        sidecar["animation_binding"] = _animation_binding(
            grid,
            placed_regions,
            sidecar["integrity"]["semantic_overlay_hash"],
        )
        sidecar["limitations"] = [
            "Stage 0 arbitrary atlas proof supports deterministic rectangular packing only.",
            "Runtime playback is a sidecar timing model, not a production renderer.",
            "Semantic grid metadata is restored from the sidecar; atlas pixels remain visual carriers.",
        ]
        exports.append(
            {
                "policy_id": policy["algorithm_id"],
                "packing_policy": placed_regions["policy"],
                "png_bytes": png_bytes,
                "png_file_name": f"{slip_profile['profile_id']}_{slug}_arbitrary_atlas.png",
                "sidecar_file_name": f"{slip_profile['profile_id']}_{slug}_arbitrary_atlas_sidecar.json",
                "asset": asset,
                "sidecar": sidecar,
                "decoded_png": _decoded_summary(decode_png_rgba(png_bytes)),
                "frame_count": len(placed_regions["frames"]),
            }
        )
    return exports


def pack_arbitrary_atlas_regions(
    regions: list[dict],
    policy: dict,
) -> dict:
    if policy["algorithm_id"] == "shelf_height_desc":
        placed = _pack_shelf_height_desc(regions, policy)
    elif policy["algorithm_id"] == "maxrects_best_short_side_fit":
        placed = _pack_maxrects_best_short_side_fit(regions, policy)
    else:
        raise ValueError(f"unsupported atlas packing policy: {policy['algorithm_id']}")

    used_area = sum(frame["rect"]["w"] * frame["rect"]["h"] for frame in placed)
    sheet_width = max(frame["rect"]["x"] + frame["rect"]["w"] for frame in placed)
    sheet_height = max(frame["rect"]["y"] + frame["rect"]["h"] for frame in placed)
    sheet_area = sheet_width * sheet_height
    return {
        "policy": {
            "algorithm_id": policy["algorithm_id"],
            "basis": policy["basis"],
            "max_width": policy["max_width"],
            "padding_px": policy["padding_px"],
            "allow_rotation": policy["allow_rotation"],
            "used_rect_area": used_area,
            "sheet_area": sheet_area,
            "wasted_area": sheet_area - used_area,
            "occupancy_rate": _ratio(used_area, sheet_area),
            "placement_order": [frame["frame_index"] for frame in placed],
        },
        "sheet_width": sheet_width,
        "sheet_height": sheet_height,
        "frames": sorted(placed, key=lambda frame: frame["frame_index"]),
    }


def import_arbitrary_atlas_with_sidecar(
    png_bytes: bytes,
    sidecar: dict,
    source_grid: dict | None = None,
) -> dict:
    try:
        decoded = decode_png_rgba(png_bytes)
    except PNGDecodeError as exc:
        return _failed_import("png", exc.family, exc.message)

    asset = _asset_from_atlas_png(
        png_bytes,
        asset_id=sidecar.get("asset_binding", {}).get(
            "asset_id",
            "unknown.arbitrary-atlas.png",
        ),
        uri=sidecar.get("asset_binding", {}).get(
            "uri",
            "unknown://arbitrary-atlas",
        ),
        frame_count=sidecar.get("asset_binding", {}).get("frame_count", 0),
    )
    validation = validate_arbitrary_atlas_binding(sidecar, asset, decoded)
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
    reconstructed = reconstruct_arbitrary_atlas_frames(decoded, sidecar)
    playback_timeline = build_arbitrary_atlas_playback_timeline(sidecar, decoded)
    semantic_source = source_grid or restored
    diff = compare_semantic_grid_fidelity(semantic_source, restored)
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


def validate_arbitrary_atlas_binding(
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
    if animation.get("animation_model") != "arbitrary_atlas_sidecar_v1":
        errors.append(_error("animation_binding.animation_model", "animation_model_mismatch"))
    if animation.get("sheet_width") != decoded_png.get("width") or animation.get("sheet_height") != decoded_png.get("height"):
        errors.append(_error("animation_binding.sheet_size", "atlas_sheet_size_mismatch"))

    errors.extend(_atlas_frame_geometry_errors(animation, decoded_png))
    if not errors:
        reconstructed = reconstruct_arbitrary_atlas_frames(decoded_png, sidecar)
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


def reconstruct_arbitrary_atlas_frames(decoded_png: dict, sidecar: dict) -> dict:
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
            errors.append(_error("animation_binding.frames.packed_pixel_hash", "atlas_frame_hash_mismatch"))
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
            errors.append(_error("animation_binding.frames.canonical_pixel_hash", "atlas_frame_hash_mismatch"))
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


def build_arbitrary_atlas_playback_timeline(
    sidecar: dict,
    decoded_png: dict,
    sample_times_ms: list[int] | None = None,
) -> list[dict]:
    animation = sidecar["animation_binding"]
    frames = sorted(animation["frames"], key=lambda item: item["playback_order"])
    total_duration = animation["total_duration_ms"]
    if sample_times_ms is None:
        cursor = 0
        sample_times_ms = [0]
        for frame in frames[:-1]:
            cursor += frame["duration_ms"]
            sample_times_ms.append(cursor)
        sample_times_ms.append(total_duration)
    reconstructed = reconstruct_arbitrary_atlas_frames(decoded_png, sidecar)
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


def run_spritesheet_arbitrary_atlas_packer_lab(
    profile_paths: list[Path],
    generated_root: Path,
) -> dict:
    atlas_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        for exported in export_arbitrary_atlas_suite_with_sidecars(grid, profile):
            imported = import_arbitrary_atlas_with_sidecar(
                exported["png_bytes"],
                exported["sidecar"],
                source_grid=grid,
            )
            restored = imported.get("restored_grid", {})
            grid_validation = validate_grid(restored) if restored else None
            alignment = is_grid_aligned(restored, profile) if restored else None
            atlas_results.append(
                {
                    "profile_id": profile["profile_id"],
                    "profile_path": _portable(profile_path),
                    "grid_path": _portable(grid_path),
                    "policy_id": exported["policy_id"],
                    "png_file_name": exported["png_file_name"],
                    "sidecar_file_name": exported["sidecar_file_name"],
                    "png_bytes_hex": exported["png_bytes"].hex(),
                    "png_byte_count": len(exported["png_bytes"]),
                    "asset": exported["asset"],
                    "sidecar": exported["sidecar"],
                    "packing_policy": exported["packing_policy"],
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

    invalid_probe_results = _invalid_probe_results(atlas_results[0])
    success_count = sum(
        1
        for result in atlas_results
        if result["import_result"]["ok"]
        and result["restored_grid_validation"]["valid"]
        and result["restored_grid_validation"]["slip_aligned"]
        and result["semantic_fidelity"] == 1.0
        and result["reconstructed_frame_fidelity"] == 1.0
        and result["runtime_frame_fidelity"] == 1.0
    )
    invalid_rejected_count = sum(1 for result in invalid_probe_results if not result["ok"])
    policy_comparison = _policy_comparison(atlas_results)
    return {
        "artifact_id": "spritesheet_arbitrary_atlas_packer_stage0",
        "status": "research_spritesheet_arbitrary_atlas_packer_no_package_code",
        "date": "2026-05-14",
        "purpose": (
            "Extend the packed spritesheet proof from fixed sidecar-authored "
            "rectangles to deterministic arbitrary rectangle atlas packing."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
            "labs/workshop_editor/spritesheet_layout_variant_decoder.py",
            "labs/workshop_editor/spritesheet_packed_runtime_decoder.py",
            "labs/workshop_editor/spritesheet_arbitrary_atlas_packer.py",
        ],
        "external_anchors": [
            {
                "source": "Jukka Jylanki, A Thousand Ways to Pack the Bin",
                "url": "https://trszdev.github.io/maxrects-bssf-global-demo/RectangleBinPack.pdf",
                "used_for": "MaxRects and rectangle bin-packing policy anchor.",
            },
            {
                "source": "libGDX TexturePacker documentation",
                "url": "https://libgdx.com/wiki/tools/texture-packer",
                "used_for": "Texture atlas workflow, rotation, whitespace stripping, padding, and atlas metadata anchor.",
            },
            {
                "source": "W3C PNG specification",
                "url": "https://www.w3.org/TR/png-3/",
                "used_for": "PNG remains the atlas image carrier.",
            },
        ],
        "profile_count": len(profile_paths),
        "packing_policy_count": len(ARBITRARY_ATLAS_POLICIES),
        "atlas_roundtrip_count": len(atlas_results),
        "atlas_roundtrip_success_count": success_count,
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "metrics": {
            "atlas_roundtrip_success_rate": _ratio(success_count, len(atlas_results)),
            "mean_semantic_fidelity": round(
                sum(result["semantic_fidelity"] for result in atlas_results)
                / max(1, len(atlas_results)),
                6,
            ),
            "mean_reconstructed_frame_fidelity": round(
                sum(result["reconstructed_frame_fidelity"] for result in atlas_results)
                / max(1, len(atlas_results)),
                6,
            ),
            "mean_runtime_frame_fidelity": round(
                sum(result["runtime_frame_fidelity"] for result in atlas_results)
                / max(1, len(atlas_results)),
                6,
            ),
            "mean_occupancy_rate": round(
                sum(result["packing_policy"]["occupancy_rate"] for result in atlas_results)
                / max(1, len(atlas_results)),
                6,
            ),
            "invalid_probe_rejection_rate": _ratio(
                invalid_rejected_count,
                len(invalid_probe_results),
            ),
            "default_runtime_sample_count": 6,
        },
        "policy_comparison": policy_comparison,
        "atlas_results": atlas_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "arbitrary_atlas_packing_geometry",
            "maxrects_best_short_side_fit_policy",
            "shelf_height_desc_baseline_policy",
            "atlas_rotation_trim_reconstruction",
            "atlas_frame_overlap_and_bounds_rejection",
            "atlas_runtime_sidecar_playback_sampling",
            "atlas_sidecar_semantic_restore",
        ],
        "blocked_states": [
            "production renderer playback",
            "live external editor rewrite validation",
            "full project-format coverage",
            "arbitrary Aseprite project schema coverage",
            "package runtime lifecycle integration",
            "manual readability calibration",
            "profile-weighted evolution",
            "community profile packs",
        ],
        "decision": "prototype_spritesheet_arbitrary_atlas_packer",
        "next_research_step": (
            "Keep production renderer playback and live external editor validation "
            "blocked until real runtime draw calls or external editor fixtures exist."
        ),
    }


def write_spritesheet_arbitrary_atlas_packer_artifacts(
    output_dir: Path,
    report: dict,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(
        output_dir / "spritesheet_arbitrary_atlas_packer_stage0.json",
        _json_report(report),
    )
    for result in report["atlas_results"]:
        (output_dir / result["png_file_name"]).write_bytes(
            bytes.fromhex(result["png_bytes_hex"])
        )
        _write_json(output_dir / result["sidecar_file_name"], result["sidecar"])
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "spritesheet_arbitrary_atlas_packer_data.js").write_text(
        "window.MECHAGOTCHI_SPRITESHEET_ARBITRARY_ATLAS_PACKER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _build_source_regions(grid: dict) -> list[dict]:
    background = _background_rgba(grid)
    base_frames = [
        render_spritesheet_frame_pixels(grid, frame_index)
        for frame_index in range(3)
    ]
    masks = [
        {"visual_delta": "base_pose", "box": {"x": 0, "y": 0, "w": 8, "h": 8}},
        {"visual_delta": "sensor_blink_crop", "box": {"x": 1, "y": 1, "w": 6, "h": 5}},
        {"visual_delta": "left_body_sweep", "box": {"x": 0, "y": 1, "w": 5, "h": 7}},
        {"visual_delta": "upper_anchor_echo", "box": {"x": 3, "y": 0, "w": 5, "h": 5}},
        {"visual_delta": "lower_expression_pulse", "box": {"x": 2, "y": 2, "w": 6, "h": 6}},
    ]
    regions = []
    palette_pixels = _profile_pixels(grid)
    for index, mask in enumerate(masks):
        box = mask["box"]
        source_pixels = [background] * 64
        base = base_frames[index % len(base_frames)]
        for y in range(box["y"], box["y"] + box["h"]):
            for x in range(box["x"], box["x"] + box["w"]):
                pixel = base[y * 8 + x]
                if pixel == background:
                    pixel = palette_pixels[(x + y + index) % len(palette_pixels)]
                source_pixels[y * 8 + x] = pixel
        trim = _trim_bounds(source_pixels, 8, 8, background)
        crop_pixels = _extract_rect_pixels(
            source_pixels,
            8,
            trim["x"],
            trim["y"],
            trim["w"],
            trim["h"],
        )
        regions.append(
            {
                "frame_index": index,
                "grid_id": grid["grid_id"],
                "playback_order": index,
                "duration_ms": FRAME_DURATIONS_MS[index],
                "source_size": deepcopy(SOURCE_FRAME_SIZE),
                "trim": trim,
                "trimmed": trim != {"x": 0, "y": 0, "w": 8, "h": 8},
                "visual_delta": mask["visual_delta"],
                "canonical_pixels": source_pixels,
                "crop_pixels": crop_pixels,
                "canonical_pixel_hash": _hash_pixels(source_pixels),
                "crop_pixel_hash": _hash_pixels(crop_pixels),
            }
        )
    return regions


def _pack_shelf_height_desc(regions: list[dict], policy: dict) -> list[dict]:
    padding = policy["padding_px"]
    max_width = policy["max_width"]
    ordered = sorted(
        regions,
        key=lambda region: (-max(region["trim"]["w"], region["trim"]["h"]), region["frame_index"]),
    )
    placed = []
    x_cursor = 0
    y_cursor = 0
    shelf_height = 0
    for region in ordered:
        packed = _packed_region(region, policy)
        rect_w = packed["rect"]["w"]
        rect_h = packed["rect"]["h"]
        next_x = x_cursor + rect_w if x_cursor == 0 else x_cursor + padding + rect_w
        if x_cursor > 0 and next_x > max_width:
            y_cursor += shelf_height + padding
            x_cursor = 0
            shelf_height = 0
        x = x_cursor if x_cursor == 0 else x_cursor + padding
        packed["rect"]["x"] = x
        packed["rect"]["y"] = y_cursor
        placed.append(packed)
        x_cursor = x + rect_w
        shelf_height = max(shelf_height, rect_h)
    return placed


def _pack_maxrects_best_short_side_fit(regions: list[dict], policy: dict) -> list[dict]:
    max_width = policy["max_width"]
    height_limit = 64
    free_rects = [{"x": 0, "y": 0, "w": max_width, "h": height_limit}]
    ordered = sorted(
        regions,
        key=lambda region: (-(region["trim"]["w"] * region["trim"]["h"]), region["frame_index"]),
    )
    placed = []
    for region in ordered:
        best = None
        for rotation in _rotation_candidates(region, policy):
            width, height = _packed_size(region, rotation)
            for free in free_rects:
                if width <= free["w"] and height <= free["h"]:
                    leftover_x = free["w"] - width
                    leftover_y = free["h"] - height
                    candidate = {
                        "score": (
                            min(leftover_x, leftover_y),
                            max(leftover_x, leftover_y),
                            free["y"],
                            free["x"],
                            rotation,
                            region["frame_index"],
                        ),
                        "rect": {
                            "x": free["x"],
                            "y": free["y"],
                            "w": width,
                            "h": height,
                        },
                        "rotation_degrees": rotation,
                    }
                    if best is None or candidate["score"] < best["score"]:
                        best = candidate
        if best is None:
            raise ValueError(f"region cannot fit atlas width {max_width}: {region['frame_index']}")
        frame = _packed_region(region, policy, rotation_degrees=best["rotation_degrees"])
        frame["rect"] = best["rect"]
        placed.append(frame)
        free_rects = _split_free_rects(free_rects, best["rect"], policy["padding_px"])
        free_rects = _prune_contained_rects(free_rects)
    return placed


def _packed_region(
    region: dict,
    policy: dict,
    rotation_degrees: int | None = None,
) -> dict:
    rotation = rotation_degrees
    if rotation is None:
        rotation = 90 if policy["allow_rotation"] and region["trim"]["h"] > region["trim"]["w"] else 0
    crop_pixels = region["crop_pixels"]
    if rotation == 90:
        packed_pixels = _rotate_clockwise(crop_pixels, region["trim"]["w"], region["trim"]["h"])
    else:
        packed_pixels = crop_pixels
    width, height = _packed_size(region, rotation)
    return {
        "frame_index": region["frame_index"],
        "grid_id": region["grid_id"],
        "playback_order": region["playback_order"],
        "rect": {"x": 0, "y": 0, "w": width, "h": height},
        "duration_ms": region["duration_ms"],
        "source_size": deepcopy(region["source_size"]),
        "trim": deepcopy(region["trim"]),
        "trimmed": region["trimmed"],
        "rotation_degrees": rotation,
        "visual_delta": region["visual_delta"],
        "canonical_pixel_hash": region["canonical_pixel_hash"],
        "packed_pixel_hash": _hash_pixels(packed_pixels),
        "packed_pixels": packed_pixels,
    }


def _packed_size(region: dict, rotation_degrees: int) -> tuple[int, int]:
    trim = region["trim"]
    if rotation_degrees == 90:
        return trim["h"], trim["w"]
    return trim["w"], trim["h"]


def _rotation_candidates(region: dict, policy: dict) -> list[int]:
    if not policy.get("allow_rotation"):
        return [0]
    if region["trim"]["w"] == region["trim"]["h"]:
        return [0]
    return [0, 90]


def _split_free_rects(
    free_rects: list[dict],
    placed: dict,
    padding: int,
) -> list[dict]:
    padded = {
        "x": max(0, placed["x"] - padding),
        "y": max(0, placed["y"] - padding),
        "w": placed["w"] + padding,
        "h": placed["h"] + padding,
    }
    next_free = []
    for free in free_rects:
        if not _rects_overlap(free, padded):
            next_free.append(free)
            continue
        if padded["x"] > free["x"]:
            next_free.append(
                {
                    "x": free["x"],
                    "y": free["y"],
                    "w": padded["x"] - free["x"],
                    "h": free["h"],
                }
            )
        right_edge = padded["x"] + padded["w"]
        free_right = free["x"] + free["w"]
        if right_edge < free_right:
            next_free.append(
                {
                    "x": right_edge,
                    "y": free["y"],
                    "w": free_right - right_edge,
                    "h": free["h"],
                }
            )
        if padded["y"] > free["y"]:
            next_free.append(
                {
                    "x": free["x"],
                    "y": free["y"],
                    "w": free["w"],
                    "h": padded["y"] - free["y"],
                }
            )
        bottom_edge = padded["y"] + padded["h"]
        free_bottom = free["y"] + free["h"]
        if bottom_edge < free_bottom:
            next_free.append(
                {
                    "x": free["x"],
                    "y": bottom_edge,
                    "w": free["w"],
                    "h": free_bottom - bottom_edge,
                }
            )
    return [
        rect
        for rect in next_free
        if rect["w"] > 0 and rect["h"] > 0
    ]


def _prune_contained_rects(rects: list[dict]) -> list[dict]:
    pruned = []
    for index, rect in enumerate(rects):
        contained = False
        for other_index, other in enumerate(rects):
            if index == other_index:
                continue
            if _rect_contains(other, rect):
                contained = True
                break
        if not contained:
            pruned.append(rect)
    return sorted(pruned, key=lambda rect: (rect["y"], rect["x"], rect["w"], rect["h"]))


def _compose_atlas_sheet(
    sheet_width: int,
    sheet_height: int,
    frames: list[dict],
) -> list[tuple[int, int, int, int]]:
    sheet = [(0, 0, 0, 0)] * (sheet_width * sheet_height)
    for frame in frames:
        rect = frame["rect"]
        for y in range(rect["h"]):
            for x in range(rect["w"]):
                sheet_index = (rect["y"] + y) * sheet_width + rect["x"] + x
                packed_index = y * rect["w"] + x
                sheet[sheet_index] = frame["packed_pixels"][packed_index]
    return sheet


def _animation_binding(
    grid: dict,
    placed_regions: dict,
    semantic_hash: str,
) -> dict:
    frames = []
    for frame in placed_regions["frames"]:
        payload = {
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
        payload["semantic_overlay_hash"] = semantic_hash
        frames.append(payload)
    return {
        "animation_model": "arbitrary_atlas_sidecar_v1",
        "sheet_width": placed_regions["sheet_width"],
        "sheet_height": placed_regions["sheet_height"],
        "source_frame_size": deepcopy(SOURCE_FRAME_SIZE),
        "frame_count": len(frames),
        "loop": True,
        "timebase": "milliseconds",
        "total_duration_ms": sum(frame["duration_ms"] for frame in frames),
        "background_rgba": list(_background_rgba(grid)),
        "packing_policy": deepcopy(placed_regions["policy"]),
        "runtime_playback": {
            "model": "looped_frame_duration_sampler_v1",
            "sampling_rule": "time_ms modulo total_duration_ms selects first cumulative frame interval",
        },
        "frames": frames,
        "limitations": [
            "Only rectangular atlas regions are covered.",
            "Only 0 and 90-degree clockwise packing rotations are covered.",
            "Runtime playback is metadata sampling, not engine rendering.",
        ],
    }


def _atlas_frame_geometry_errors(animation: dict, decoded_png: dict) -> list[dict]:
    errors = []
    sheet_width = decoded_png.get("width", 0)
    sheet_height = decoded_png.get("height", 0)
    frames = animation.get("frames", [])
    policy = animation.get("packing_policy", {})
    supported = {policy["algorithm_id"] for policy in ARBITRARY_ATLAS_POLICIES}
    if policy.get("algorithm_id") not in supported:
        errors.append(_error("animation_binding.packing_policy.algorithm_id", "atlas_packing_algorithm_unsupported"))
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
            errors.append(_error("animation_binding.frames.rotation_degrees", "atlas_frame_rotation_unsupported"))
            continue
        if rotation == 90 and policy.get("allow_rotation") is False:
            errors.append(_error("animation_binding.frames.rotation_degrees", "atlas_frame_rotation_policy_violation"))

        rect = frame.get("rect", {})
        trim = frame.get("trim", {})
        source_size = frame.get("source_size", {})
        rect_values = [rect.get(key) for key in ["x", "y", "w", "h"]]
        trim_values = [trim.get(key) for key in ["x", "y", "w", "h"]]
        source_values = [source_size.get(key) for key in ["w", "h"]]
        if not all(type(value) is int for value in rect_values + trim_values + source_values):
            errors.append(_error("animation_binding.frames.geometry", "atlas_frame_geometry_invalid"))
            continue
        x, y, rect_width, rect_height = rect_values
        trim_x, trim_y, trim_width, trim_height = trim_values
        source_width, source_height = source_values
        if rect_width <= 0 or rect_height <= 0 or trim_width <= 0 or trim_height <= 0:
            errors.append(_error("animation_binding.frames.geometry", "atlas_frame_geometry_invalid"))
            continue
        if trim_x < 0 or trim_y < 0 or trim_x + trim_width > source_width or trim_y + trim_height > source_height:
            errors.append(_error("animation_binding.frames.trim", "atlas_frame_trim_out_of_bounds"))
            continue
        expected_rect_size = (
            {"w": trim_height, "h": trim_width}
            if rotation == 90
            else {"w": trim_width, "h": trim_height}
        )
        if {"w": rect_width, "h": rect_height} != expected_rect_size:
            errors.append(_error("animation_binding.frames.rect", "atlas_frame_rect_transform_mismatch"))
            continue
        if x < 0 or y < 0 or x + rect_width > sheet_width or y + rect_height > sheet_height:
            errors.append(_error("animation_binding.frames.rect", "atlas_frame_rect_out_of_bounds"))
            continue
        for yy in range(y, y + rect_height):
            for xx in range(x, x + rect_width):
                coordinate = (xx, yy)
                if coordinate in occupied:
                    errors.append(_error("animation_binding.frames.rect", "atlas_frame_rect_overlap"))
                    break
                occupied.add(coordinate)
            if errors and errors[-1]["family"] == "atlas_frame_rect_overlap":
                break
    if total_duration and animation.get("total_duration_ms") != total_duration:
        errors.append(_error("animation_binding.total_duration_ms", "runtime_total_duration_mismatch"))
    return errors


def _asset_from_atlas_png(
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

    overlap_sidecar = deepcopy(sidecar)
    overlap_sidecar["animation_binding"]["frames"][1]["rect"]["x"] = overlap_sidecar["animation_binding"]["frames"][0]["rect"]["x"]
    overlap_sidecar["animation_binding"]["frames"][1]["rect"]["y"] = overlap_sidecar["animation_binding"]["frames"][0]["rect"]["y"]

    out_of_bounds_sidecar = deepcopy(sidecar)
    out_of_bounds_sidecar["animation_binding"]["frames"][0]["rect"]["x"] = sidecar["animation_binding"]["sheet_width"]

    wrong_hash_sidecar = deepcopy(sidecar)
    wrong_hash_sidecar["animation_binding"]["frames"][0]["packed_pixel_hash"] = "sha256:not-the-frame"

    bad_duration_sidecar = deepcopy(sidecar)
    bad_duration_sidecar["animation_binding"]["frames"][0]["duration_ms"] = 0
    bad_duration_sidecar["animation_binding"]["total_duration_ms"] = (
        sidecar["animation_binding"]["total_duration_ms"]
        - sidecar["animation_binding"]["frames"][0]["duration_ms"]
    )

    unsupported_algorithm_sidecar = deepcopy(sidecar)
    unsupported_algorithm_sidecar["animation_binding"]["packing_policy"]["algorithm_id"] = "not_supported"

    rotation_policy_sidecar = deepcopy(sidecar)
    rotation_policy_sidecar["animation_binding"]["packing_policy"]["allow_rotation"] = False

    return [
        _compact_import_result(import_arbitrary_atlas_with_sidecar(png_bytes, overlap_sidecar)),
        _compact_import_result(import_arbitrary_atlas_with_sidecar(png_bytes, out_of_bounds_sidecar)),
        _compact_import_result(import_arbitrary_atlas_with_sidecar(png_bytes, wrong_hash_sidecar)),
        _compact_import_result(import_arbitrary_atlas_with_sidecar(png_bytes, bad_duration_sidecar)),
        _compact_import_result(import_arbitrary_atlas_with_sidecar(png_bytes, unsupported_algorithm_sidecar)),
        _compact_import_result(import_arbitrary_atlas_with_sidecar(png_bytes, rotation_policy_sidecar)),
    ]


def _policy_comparison(atlas_results: list[dict]) -> dict:
    by_policy = {}
    for result in atlas_results:
        policy = result["packing_policy"]
        by_policy.setdefault(policy["algorithm_id"], []).append(policy)
    summaries = []
    for policy_id, rows in sorted(by_policy.items()):
        summaries.append(
            {
                "algorithm_id": policy_id,
                "mean_occupancy_rate": round(
                    sum(row["occupancy_rate"] for row in rows) / len(rows),
                    6,
                ),
                "mean_sheet_area": round(
                    sum(row["sheet_area"] for row in rows) / len(rows),
                    6,
                ),
                "mean_wasted_area": round(
                    sum(row["wasted_area"] for row in rows) / len(rows),
                    6,
                ),
            }
        )
    best = sorted(
        summaries,
        key=lambda item: (-item["mean_occupancy_rate"], item["mean_sheet_area"], item["algorithm_id"]),
    )[0]
    return {
        "policies": summaries,
        "best_occupancy_policy": best["algorithm_id"],
        "selection_basis": "highest mean occupancy, then smallest mean sheet area",
    }


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


def _profile_pixels(grid: dict) -> list[tuple[int, int, int, int]]:
    palette = grid["palette"]
    background_index = palette.get("background_index", 0)
    colors = [
        _hex_to_rgba(color)
        for index, color in enumerate(palette["colors"])
        if index != background_index
    ]
    return colors or [_hex_to_rgba(palette["colors"][background_index])]


def _hex_to_rgba(value: str) -> tuple[int, int, int, int]:
    if not isinstance(value, str) or len(value) != 7 or not value.startswith("#"):
        raise ValueError(f"expected #RRGGBB color, got {value!r}")
    return (
        int(value[1:3], 16),
        int(value[3:5], 16),
        int(value[5:7], 16),
        255,
    )


def _rects_overlap(left: dict, right: dict) -> bool:
    return not (
        left["x"] + left["w"] <= right["x"]
        or right["x"] + right["w"] <= left["x"]
        or left["y"] + left["h"] <= right["y"]
        or right["y"] + right["h"] <= left["y"]
    )


def _rect_contains(outer: dict, inner: dict) -> bool:
    return (
        outer["x"] <= inner["x"]
        and outer["y"] <= inner["y"]
        and outer["x"] + outer["w"] >= inner["x"] + inner["w"]
        and outer["y"] + outer["h"] >= inner["y"] + inner["h"]
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
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def _json_report(report: dict) -> dict:
    payload = deepcopy(report)
    for result in payload["atlas_results"]:
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
                "packing_policy_count",
                "atlas_roundtrip_count",
                "atlas_roundtrip_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "policy_comparison",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "atlas_summaries": [
            {
                "profile_id": result["profile_id"],
                "policy_id": result["policy_id"],
                "asset": result["asset"],
                "decoded_png": result["decoded_png"],
                "frame_count": result["frame_count"],
                "packing_policy": result["packing_policy"],
                "semantic_fidelity": result["semantic_fidelity"],
                "reconstructed_frame_fidelity": result["reconstructed_frame_fidelity"],
                "runtime_frame_fidelity": result["runtime_frame_fidelity"],
                "runtime_playback": result["runtime_playback"],
            }
            for result in json_report["atlas_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# Spritesheet Arbitrary Atlas Packer Stage 0\n\n"
        "Deterministic arbitrary rectangle atlas packing proof with shelf and "
        "MaxRects-style policies, sidecar-described reconstruction, and "
        "looped runtime sampling.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Packing policies: {report['packing_policy_count']}\n"
        f"- Atlas round-trip successes: {report['atlas_roundtrip_success_count']}"
        f"/{report['atlas_roundtrip_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- Mean semantic fidelity: {metrics['mean_semantic_fidelity']}\n"
        f"- Mean reconstructed frame fidelity: {metrics['mean_reconstructed_frame_fidelity']}\n"
        f"- Mean runtime frame fidelity: {metrics['mean_runtime_frame_fidelity']}\n"
        f"- Mean occupancy rate: {metrics['mean_occupancy_rate']}\n"
        f"- Best occupancy policy: {report['policy_comparison']['best_occupancy_policy']}\n"
        f"- Decision: {report['decision']}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "data/workshop_editor/spritesheet_arbitrary_atlas_packer_stage0",
    )
    parser.add_argument(
        "--generated-root",
        type=Path,
        default=ROOT / "data/slips/multi_profile_generation_stage0",
    )
    parser.add_argument("--profile", type=Path, action="append")
    args = parser.parse_args()
    profile_paths = args.profile or [
        ROOT / "data/slips/valid/slip_lcd_seed.json",
        ROOT / "data/slips/valid/slip_gray_stable.json",
        ROOT / "data/slips/valid/slip_amber_social.json",
    ]
    report = run_spritesheet_arbitrary_atlas_packer_lab(profile_paths, args.generated_root)
    write_spritesheet_arbitrary_atlas_packer_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_SPRITESHEET_ARBITRARY_ATLAS_PACKER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(_json_report(report), indent=2))


if __name__ == "__main__":
    main()
