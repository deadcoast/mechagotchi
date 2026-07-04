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


REPORT_PATH = ROOT / "data/workshop_editor/spritesheet_multi_page_atlas_stage0.json"
DATA_PATH = ROOT / "data/workshop_editor/spritesheet_multi_page_atlas_data.js"
FRAME_DURATIONS_MS = [90, 110, 130, 150, 170, 190, 210]
SOURCE_FRAME_SIZE = {"w": 8, "h": 8}
MULTI_PAGE_ATLAS_POLICY = {
    "algorithm_id": "multi_page_first_fit_shelf_scan",
    "basis": "first-fit page selection with scanline shelf placement and 0/90-degree rotation candidates",
    "max_page_width": 12,
    "max_page_height": 12,
    "padding_px": 1,
    "allow_rotation": True,
}


def export_multi_page_atlas_bundle(
    grid: dict,
    slip_profile: dict,
) -> dict:
    if grid.get("grid_size") != [8, 8]:
        raise ValueError("Stage 0 multi-page atlas proof expects 8x8 grids")

    source_regions = _build_multi_page_source_regions(grid)
    packed = pack_multi_page_regions(source_regions, MULTI_PAGE_ATLAS_POLICY)
    page_payloads = _page_payloads(slip_profile, packed)
    aggregate_asset = _aggregate_asset(
        slip_profile,
        page_payloads,
        frame_count=len(packed["frames"]),
    )
    sidecar = build_sidecar_for_grid(grid, slip_profile, aggregate_asset)
    sidecar["sidecar_id"] = f"{grid['grid_id']}_multi_page_atlas_sidecar"
    sidecar["asset_binding"] = deepcopy(aggregate_asset)
    sidecar["animation_binding"] = _animation_binding(
        grid,
        packed,
        page_payloads,
        sidecar["integrity"]["semantic_overlay_hash"],
    )
    sidecar["limitations"] = [
        "Stage 0 multi-page atlas proof supports generated page fixtures only.",
        "Runtime playback is a sidecar timing model, not a production renderer.",
        "Live external editor-authored atlas fixtures remain separate evidence.",
    ]
    return {
        "pages": page_payloads,
        "asset": aggregate_asset,
        "sidecar": sidecar,
        "page_count": len(page_payloads),
        "frame_count": len(packed["frames"]),
    }


def pack_multi_page_regions(
    regions: list[dict],
    policy: dict,
) -> dict:
    pages = []
    placed_frames = []
    for region in sorted(regions, key=lambda item: item["playback_order"]):
        placement = _find_first_fit(region, pages, policy)
        if placement is None:
            pages.append({"page_index": len(pages), "frames": []})
            placement = _find_first_fit(region, pages[-1:], policy, page_offset=len(pages) - 1)
        if placement is None:
            raise ValueError(f"region cannot fit multi-page atlas: {region['frame_index']}")
        frame = _packed_region(region, placement["rotation_degrees"])
        frame["page_index"] = placement["page_index"]
        frame["rect"]["x"] = placement["x"]
        frame["rect"]["y"] = placement["y"]
        pages[placement["page_index"]]["frames"].append(frame)
        placed_frames.append(frame)

    page_summaries = []
    for page in pages:
        page_width = max(frame["rect"]["x"] + frame["rect"]["w"] for frame in page["frames"])
        page_height = max(frame["rect"]["y"] + frame["rect"]["h"] for frame in page["frames"])
        used_area = sum(frame["rect"]["w"] * frame["rect"]["h"] for frame in page["frames"])
        page_summaries.append(
            {
                "page_index": page["page_index"],
                "width": page_width,
                "height": page_height,
                "frame_indices": [frame["frame_index"] for frame in page["frames"]],
                "used_rect_area": used_area,
                "page_area": page_width * page_height,
                "occupancy_rate": _ratio(used_area, page_width * page_height),
            }
        )
    return {
        "policy": {
            **deepcopy(policy),
            "page_count": len(pages),
            "frame_count": len(placed_frames),
            "mean_page_occupancy_rate": round(
                sum(page["occupancy_rate"] for page in page_summaries)
                / max(1, len(page_summaries)),
                6,
            ),
        },
        "pages": pages,
        "page_summaries": page_summaries,
        "frames": sorted(placed_frames, key=lambda frame: frame["frame_index"]),
    }


def import_multi_page_atlas_bundle(
    pages: list[dict],
    sidecar: dict,
    source_grid: dict | None = None,
) -> dict:
    decoded_pages, page_errors = _decode_pages(pages)
    aggregate_asset = _aggregate_asset_from_pages(sidecar, pages, decoded_pages)
    if page_errors:
        return _failed_import(page_errors)

    validation = validate_multi_page_atlas_binding(decoded_pages, sidecar, aggregate_asset)
    if not validation["ok"]:
        return {
            "ok": False,
            "asset": aggregate_asset,
            "decoded_pages": _decoded_page_summaries(decoded_pages),
            "validation": validation,
            "errors": validation["errors"],
            "error_families": validation["error_families"],
        }

    restored = restore_grid_from_sidecar(sidecar, aggregate_asset, validate=False)
    profile = sidecar["slip_binding"]["profile_snapshot"]
    grid_validation = validate_grid(restored)
    alignment = is_grid_aligned(restored, profile)
    reconstructed = reconstruct_multi_page_atlas_frames(decoded_pages, sidecar)
    playback_timeline = build_multi_page_atlas_playback_timeline(sidecar, decoded_pages)
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
        "asset": aggregate_asset,
        "decoded_pages": _decoded_page_summaries(decoded_pages),
        "validation": validation,
        "restored_grid": restored,
        "frame_count": len(reconstructed["frames"]),
        "page_count": len(decoded_pages),
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


def validate_multi_page_atlas_binding(
    decoded_pages: dict[int, dict],
    sidecar: dict,
    aggregate_asset: dict,
) -> dict:
    errors = []
    binding = sidecar.get("asset_binding", {})
    animation = sidecar.get("animation_binding", {})
    if binding.get("asset_id") != aggregate_asset.get("asset_id"):
        errors.append(_error("asset_binding.asset_id", "asset_id_mismatch"))
    if binding.get("format_id") != "spritesheet_atlas_pages":
        errors.append(_error("asset_binding.format_id", "asset_format_mismatch"))
    if binding.get("content_hash") != aggregate_asset.get("content_hash"):
        errors.append(_error("asset_binding.content_hash", "asset_hash_mismatch"))
    if binding.get("page_count") != len(decoded_pages):
        errors.append(_error("asset_binding.page_count", "atlas_page_count_mismatch"))
    if binding.get("frame_count") != animation.get("frame_count"):
        errors.append(_error("asset_binding.frame_count", "asset_frame_count_mismatch"))
    if animation.get("animation_model") != "multi_page_atlas_sidecar_v1":
        errors.append(_error("animation_binding.animation_model", "animation_model_mismatch"))

    manifest_pages = {page.get("page_index"): page for page in animation.get("pages", [])}
    for page_index, manifest in manifest_pages.items():
        decoded = decoded_pages.get(page_index)
        if decoded is None:
            errors.append(_error("animation_binding.pages", "atlas_page_missing"))
            continue
        if manifest.get("content_hash") != decoded["content_hash"]:
            errors.append(_error("animation_binding.pages.content_hash", "atlas_page_hash_mismatch"))
        if manifest.get("width") != decoded["width"] or manifest.get("height") != decoded["height"]:
            errors.append(_error("animation_binding.pages.dimensions", "atlas_page_dimension_mismatch"))

    errors.extend(_frame_geometry_errors(animation, decoded_pages, manifest_pages))
    if not errors:
        reconstructed = reconstruct_multi_page_atlas_frames(decoded_pages, sidecar)
        errors.extend(reconstructed["errors"])

    profile = sidecar.get("slip_binding", {}).get("profile_snapshot", {})
    restored = restore_grid_from_sidecar(sidecar, aggregate_asset, validate=False) if profile else {}
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


def reconstruct_multi_page_atlas_frames(
    decoded_pages: dict[int, dict],
    sidecar: dict,
) -> dict:
    animation = sidecar.get("animation_binding", {})
    background = tuple(animation.get("background_rgba", [0, 0, 0, 0]))
    reconstructed_frames = []
    errors = []
    for frame in animation.get("frames", []):
        decoded = decoded_pages.get(frame.get("page_index"))
        if decoded is None:
            errors.append(_error("animation_binding.frames.page_index", "atlas_frame_page_unknown"))
            continue
        rect = frame["rect"]
        trim = frame["trim"]
        source_size = frame["source_size"]
        packed_pixels = _extract_rect_pixels(
            decoded["pixels"],
            decoded["width"],
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
                "page_index": frame["page_index"],
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


def build_multi_page_atlas_playback_timeline(
    sidecar: dict,
    decoded_pages: dict[int, dict],
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
    reconstructed = reconstruct_multi_page_atlas_frames(decoded_pages, sidecar)
    hashes_by_index = {
        frame["frame_index"]: frame["canonical_pixel_hash"]
        for frame in reconstructed["frames"]
    }
    page_hashes = {index: page["content_hash"] for index, page in decoded_pages.items()}
    timeline = []
    for sample_time in sample_times_ms:
        effective_time = sample_time % total_duration if animation.get("loop") else min(sample_time, total_duration - 1)
        frame = _frame_at_time(frames, effective_time)
        canonical_hash = hashes_by_index.get(frame["frame_index"])
        page_hash = page_hashes.get(frame["page_index"])
        timeline.append(
            {
                "time_ms": sample_time,
                "effective_time_ms": effective_time,
                "frame_index": frame["frame_index"],
                "page_index": frame["page_index"],
                "duration_ms": frame["duration_ms"],
                "visual_delta": frame["visual_delta"],
                "page_content_hash": page_hash,
                "expected_page_content_hash": frame["page_content_hash"],
                "page_hash_match": page_hash == frame["page_content_hash"],
                "canonical_pixel_hash": canonical_hash,
                "expected_canonical_pixel_hash": frame["canonical_pixel_hash"],
                "canonical_hash_match": canonical_hash == frame["canonical_pixel_hash"],
            }
        )
    return timeline


def run_spritesheet_multi_page_atlas_lab(
    profile_paths: list[Path],
    generated_root: Path,
) -> dict:
    bundle_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        exported = export_multi_page_atlas_bundle(grid, profile)
        imported = import_multi_page_atlas_bundle(
            exported["pages"],
            exported["sidecar"],
            source_grid=grid,
        )
        restored = imported.get("restored_grid", {})
        grid_validation = validate_grid(restored) if restored else None
        alignment = is_grid_aligned(restored, profile) if restored else None
        bundle_results.append(
            {
                "profile_id": profile["profile_id"],
                "profile_path": _portable(profile_path),
                "grid_path": _portable(grid_path),
                "sidecar_file_name": f"{profile['profile_id']}_multi_page_atlas_sidecar.json",
                "asset": exported["asset"],
                "sidecar": exported["sidecar"],
                "pages": _persistable_pages(exported["pages"]),
                "decoded_pages": imported.get("decoded_pages", []),
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
                "page_count": imported.get("page_count", 0),
                "frame_count": imported.get("frame_count", 0),
            }
        )

    invalid_probe_results = _invalid_probe_results(bundle_results[0])
    success_count = sum(
        1
        for result in bundle_results
        if result["import_result"]["ok"]
        and result["restored_grid_validation"]["valid"]
        and result["restored_grid_validation"]["slip_aligned"]
        and result["semantic_fidelity"] == 1.0
        and result["reconstructed_frame_fidelity"] == 1.0
        and result["runtime_frame_fidelity"] == 1.0
    )
    invalid_rejected_count = sum(1 for result in invalid_probe_results if not result["ok"])
    return {
        "artifact_id": "spritesheet_multi_page_atlas_stage0",
        "status": "research_spritesheet_multi_page_atlas_no_package_code",
        "date": "2026-05-14",
        "purpose": (
            "Extend arbitrary atlas research to generated multi-page atlas "
            "fixtures with page manifests and frame-to-page bindings."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
            "labs/workshop_editor/spritesheet_arbitrary_atlas_packer.py",
            "labs/workshop_editor/spritesheet_multi_page_atlas.py",
        ],
        "external_anchors": [
            {
                "source": "libGDX TexturePacker documentation",
                "url": "https://libgdx.com/wiki/tools/texture-packer",
                "used_for": "Multiple atlas pages, texture bind/page grouping, rotation, whitespace stripping, padding, and atlas metadata context.",
            },
            {
                "source": "W3C PNG specification",
                "url": "https://www.w3.org/TR/png-3/",
                "used_for": "PNG remains the page image carrier.",
            },
        ],
        "profile_count": len(profile_paths),
        "bundle_roundtrip_count": len(bundle_results),
        "bundle_roundtrip_success_count": success_count,
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "metrics": {
            "bundle_roundtrip_success_rate": _ratio(success_count, len(bundle_results)),
            "mean_semantic_fidelity": round(
                sum(result["semantic_fidelity"] for result in bundle_results)
                / max(1, len(bundle_results)),
                6,
            ),
            "mean_reconstructed_frame_fidelity": round(
                sum(result["reconstructed_frame_fidelity"] for result in bundle_results)
                / max(1, len(bundle_results)),
                6,
            ),
            "mean_runtime_frame_fidelity": round(
                sum(result["runtime_frame_fidelity"] for result in bundle_results)
                / max(1, len(bundle_results)),
                6,
            ),
            "mean_page_count": round(
                sum(result["page_count"] for result in bundle_results)
                / max(1, len(bundle_results)),
                6,
            ),
            "mean_frame_count": round(
                sum(result["frame_count"] for result in bundle_results)
                / max(1, len(bundle_results)),
                6,
            ),
            "invalid_probe_rejection_rate": _ratio(
                invalid_rejected_count,
                len(invalid_probe_results),
            ),
        },
        "page_policy": deepcopy(MULTI_PAGE_ATLAS_POLICY),
        "bundle_results": bundle_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "multi_page_atlas_page_manifest",
            "multi_page_atlas_frame_page_binding",
            "multi_page_atlas_page_hash_validation",
            "multi_page_atlas_runtime_page_switch_sampling",
            "multi_page_atlas_sidecar_semantic_restore",
            "multi_page_atlas_invalid_probe_rejection",
        ],
        "blocked_states": [
            "editor-authored atlas fixtures",
            "production renderer playback",
            "live external editor rewrite validation",
            "full project-format coverage",
            "arbitrary Aseprite project schema coverage",
            "package runtime lifecycle integration",
            "manual readability calibration",
            "profile-weighted evolution",
        ],
        "decision": "prototype_spritesheet_multi_page_atlas",
        "next_research_step": (
            "Keep editor-authored atlas fixtures, production renderer playback, "
            "and live external editor validation blocked until direct fixtures "
            "or runtime draw-call evidence exists."
        ),
    }


def write_spritesheet_multi_page_atlas_artifacts(
    output_dir: Path,
    report: dict,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "spritesheet_multi_page_atlas_stage0.json", _json_report(report))
    for result in report["bundle_results"]:
        _write_json(output_dir / result["sidecar_file_name"], result["sidecar"])
        for page in result["pages"]:
            (output_dir / page["png_file_name"]).write_bytes(bytes.fromhex(page["png_bytes_hex"]))
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "spritesheet_multi_page_atlas_data.js").write_text(
        "window.MECHAGOTCHI_SPRITESHEET_MULTI_PAGE_ATLAS = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _build_multi_page_source_regions(grid: dict) -> list[dict]:
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
        {"visual_delta": "right_sensor_stride", "box": {"x": 4, "y": 1, "w": 4, "h": 7}},
        {"visual_delta": "core_idle_glow", "box": {"x": 1, "y": 3, "w": 7, "h": 4}},
    ]
    palette_pixels = _profile_pixels(grid)
    regions = []
    for index, mask in enumerate(masks):
        box = mask["box"]
        source_pixels = [background] * 64
        base = base_frames[index % len(base_frames)]
        for y in range(box["y"], box["y"] + box["h"]):
            for x in range(box["x"], box["x"] + box["w"]):
                pixel = base[y * 8 + x]
                if pixel == background:
                    pixel = palette_pixels[(x * 3 + y + index) % len(palette_pixels)]
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


def _find_first_fit(
    region: dict,
    pages: list[dict],
    policy: dict,
    page_offset: int = 0,
) -> dict | None:
    for local_page_index, page in enumerate(pages):
        page_index = page.get("page_index", page_offset + local_page_index)
        for rotation in _rotation_candidates(region, policy):
            width, height = _packed_size(region, rotation)
            for y in range(0, policy["max_page_height"] - height + 1):
                for x in range(0, policy["max_page_width"] - width + 1):
                    rect = {"x": x, "y": y, "w": width, "h": height}
                    if _rect_fits_page(rect, page["frames"], policy["padding_px"]):
                        return {
                            "page_index": page_index,
                            "x": x,
                            "y": y,
                            "rotation_degrees": rotation,
                        }
    return None


def _rect_fits_page(rect: dict, frames: list[dict], padding: int) -> bool:
    padded = {
        "x": rect["x"] - padding,
        "y": rect["y"] - padding,
        "w": rect["w"] + padding * 2,
        "h": rect["h"] + padding * 2,
    }
    for frame in frames:
        if _rects_overlap(padded, frame["rect"]):
            return False
    return True


def _packed_region(region: dict, rotation_degrees: int) -> dict:
    crop_pixels = region["crop_pixels"]
    if rotation_degrees == 90:
        packed_pixels = _rotate_clockwise(crop_pixels, region["trim"]["w"], region["trim"]["h"])
    else:
        packed_pixels = crop_pixels
    width, height = _packed_size(region, rotation_degrees)
    return {
        "frame_index": region["frame_index"],
        "grid_id": region["grid_id"],
        "playback_order": region["playback_order"],
        "rect": {"x": 0, "y": 0, "w": width, "h": height},
        "duration_ms": region["duration_ms"],
        "source_size": deepcopy(region["source_size"]),
        "trim": deepcopy(region["trim"]),
        "trimmed": region["trimmed"],
        "rotation_degrees": rotation_degrees,
        "visual_delta": region["visual_delta"],
        "canonical_pixel_hash": region["canonical_pixel_hash"],
        "packed_pixel_hash": _hash_pixels(packed_pixels),
        "packed_pixels": packed_pixels,
    }


def _page_payloads(slip_profile: dict, packed: dict) -> list[dict]:
    payloads = []
    for page in packed["pages"]:
        summary = next(item for item in packed["page_summaries"] if item["page_index"] == page["page_index"])
        pixels = _compose_page(summary["width"], summary["height"], page["frames"])
        png_bytes = encode_png_rgba(summary["width"], summary["height"], pixels)
        asset = _page_asset(
            png_bytes,
            slip_profile["profile_id"],
            page["page_index"],
            len(page["frames"]),
        )
        for frame in page["frames"]:
            frame["page_content_hash"] = asset["content_hash"]
        payloads.append(
            {
                "page_index": page["page_index"],
                "png_bytes": png_bytes,
                "png_file_name": f"{slip_profile['profile_id']}_multi_page_atlas_page_{page['page_index']}.png",
                "asset": asset,
                "decoded_png": _decoded_summary(decode_png_rgba(png_bytes)),
            }
        )
    return payloads


def _compose_page(
    page_width: int,
    page_height: int,
    frames: list[dict],
) -> list[tuple[int, int, int, int]]:
    pixels = [(0, 0, 0, 0)] * (page_width * page_height)
    for frame in frames:
        rect = frame["rect"]
        for y in range(rect["h"]):
            for x in range(rect["w"]):
                page_index = (rect["y"] + y) * page_width + rect["x"] + x
                packed_index = y * rect["w"] + x
                pixels[page_index] = frame["packed_pixels"][packed_index]
    return pixels


def _animation_binding(
    grid: dict,
    packed: dict,
    page_payloads: list[dict],
    semantic_hash: str,
) -> dict:
    page_manifest = []
    for page in page_payloads:
        asset = page["asset"]
        page_manifest.append(
            {
                "page_index": page["page_index"],
                "asset_id": asset["asset_id"],
                "width": asset["width"],
                "height": asset["height"],
                "frame_count": asset["frame_count"],
                "content_hash": asset["content_hash"],
            }
        )
    frames = []
    page_hashes = {page["page_index"]: page["asset"]["content_hash"] for page in page_payloads}
    for frame in packed["frames"]:
        payload = {
            key: deepcopy(frame[key])
            for key in [
                "frame_index",
                "grid_id",
                "playback_order",
                "page_index",
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
        payload["page_content_hash"] = page_hashes[frame["page_index"]]
        payload["semantic_overlay_hash"] = semantic_hash
        frames.append(payload)
    return {
        "animation_model": "multi_page_atlas_sidecar_v1",
        "page_policy": deepcopy(packed["policy"]),
        "source_frame_size": deepcopy(SOURCE_FRAME_SIZE),
        "page_count": len(page_payloads),
        "frame_count": len(frames),
        "loop": True,
        "timebase": "milliseconds",
        "total_duration_ms": sum(frame["duration_ms"] for frame in frames),
        "background_rgba": list(_background_rgba(grid)),
        "pages": page_manifest,
        "frames": frames,
        "runtime_playback": {
            "model": "looped_multi_page_duration_sampler_v1",
            "sampling_rule": "time_ms modulo total_duration_ms selects frame interval and then that frame's page binding",
        },
        "limitations": [
            "Only generated multi-page atlas fixtures are covered.",
            "Only rectangular regions and 0/90-degree rotations are covered.",
            "Production renderer texture binding is not claimed.",
        ],
    }


def _frame_geometry_errors(
    animation: dict,
    decoded_pages: dict[int, dict],
    manifest_pages: dict[int, dict],
) -> list[dict]:
    errors = []
    frames = animation.get("frames", [])
    seen_indices = set()
    seen_orders = set()
    total_duration = 0
    occupied_by_page: dict[int, set[tuple[int, int]]] = {}
    policy = animation.get("page_policy", {})
    for frame in frames:
        frame_index = frame.get("frame_index")
        playback_order = frame.get("playback_order")
        if frame_index in seen_indices:
            errors.append(_error("animation_binding.frames", "duplicate_frame_index"))
        seen_indices.add(frame_index)
        if playback_order in seen_orders or type(playback_order) is not int:
            errors.append(_error("animation_binding.frames.playback_order", "runtime_frame_order_invalid"))
        seen_orders.add(playback_order)
        duration = frame.get("duration_ms")
        if type(duration) is not int or duration <= 0:
            errors.append(_error("animation_binding.frames.duration_ms", "runtime_frame_duration_invalid"))
        else:
            total_duration += duration
        page_index = frame.get("page_index")
        decoded = decoded_pages.get(page_index)
        if decoded is None or page_index not in manifest_pages:
            errors.append(_error("animation_binding.frames.page_index", "atlas_frame_page_unknown"))
            continue
        if frame.get("page_content_hash") != decoded.get("content_hash"):
            errors.append(_error("animation_binding.frames.page_content_hash", "atlas_page_hash_mismatch"))
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
        if trim_x < 0 or trim_y < 0 or trim_x + trim_width > source_width or trim_y + trim_height > source_height:
            errors.append(_error("animation_binding.frames.trim", "atlas_frame_trim_out_of_bounds"))
            continue
        expected = (
            {"w": trim_height, "h": trim_width}
            if rotation == 90
            else {"w": trim_width, "h": trim_height}
        )
        if {"w": rect_width, "h": rect_height} != expected:
            errors.append(_error("animation_binding.frames.rect", "atlas_frame_rect_transform_mismatch"))
            continue
        if x < 0 or y < 0 or x + rect_width > decoded["width"] or y + rect_height > decoded["height"]:
            errors.append(_error("animation_binding.frames.rect", "atlas_frame_rect_out_of_bounds"))
            continue
        occupied = occupied_by_page.setdefault(page_index, set())
        for yy in range(y, y + rect_height):
            for xx in range(x, x + rect_width):
                coordinate = (xx, yy)
                if coordinate in occupied:
                    errors.append(_error("animation_binding.frames.rect", "atlas_frame_rect_overlap"))
                    break
                occupied.add(coordinate)
            if errors and errors[-1]["family"] == "atlas_frame_rect_overlap":
                break
    expected_orders = set(range(len(frames)))
    if seen_orders != expected_orders:
        errors.append(_error("animation_binding.frames.playback_order", "runtime_frame_order_invalid"))
    if total_duration and animation.get("total_duration_ms") != total_duration:
        errors.append(_error("animation_binding.total_duration_ms", "runtime_total_duration_mismatch"))
    return errors


def _decode_pages(pages: list[dict]) -> tuple[dict[int, dict], list[dict]]:
    decoded = {}
    errors = []
    for page in pages:
        page_index = page.get("page_index")
        try:
            decoded_png = decode_png_rgba(page["png_bytes"])
        except (KeyError, PNGDecodeError) as exc:
            errors.append(_error("pages", "atlas_page_decode_failed", str(exc)))
            continue
        decoded_png["page_index"] = page_index
        decoded_png["content_hash"] = _hash_bytes(page["png_bytes"])
        decoded_png["asset_id"] = page.get("asset", {}).get("asset_id", f"page_{page_index}.png")
        decoded[page_index] = decoded_png
    return decoded, errors


def _aggregate_asset(
    slip_profile: dict,
    pages: list[dict],
    frame_count: int,
) -> dict:
    manifest = [
        {
            "page_index": page["page_index"],
            "asset_id": page["asset"]["asset_id"],
            "width": page["asset"]["width"],
            "height": page["asset"]["height"],
            "frame_count": page["asset"]["frame_count"],
            "content_hash": page["asset"]["content_hash"],
        }
        for page in pages
    ]
    return {
        "asset_id": f"{slip_profile['profile_id']}_multi_page_atlas.bundle",
        "format_id": "spritesheet_atlas_pages",
        "media_type": "application/vnd.mechagotchi.atlas-pages+json",
        "uri": f"generated://workshop/spritesheet-multi-page-atlas/{slip_profile['profile_id']}.bundle",
        "width": max(page["width"] for page in manifest),
        "height": max(page["height"] for page in manifest),
        "frame_count": frame_count,
        "page_count": len(pages),
        "pages": manifest,
        "content_hash": _hash_payload(manifest),
        "semantic_policy": "sidecar_required",
    }


def _aggregate_asset_from_pages(
    sidecar: dict,
    pages: list[dict],
    decoded_pages: dict[int, dict],
) -> dict:
    manifest = []
    for page in pages:
        page_index = page.get("page_index")
        decoded = decoded_pages.get(page_index)
        if decoded is None:
            continue
        manifest.append(
            {
                "page_index": page_index,
                "asset_id": page.get("asset", {}).get("asset_id", f"page_{page_index}.png"),
                "width": decoded["width"],
                "height": decoded["height"],
                "frame_count": page.get("asset", {}).get("frame_count", 0),
                "content_hash": decoded["content_hash"],
            }
        )
    binding = sidecar.get("asset_binding", {})
    return {
        "asset_id": binding.get("asset_id", "unknown_multi_page_atlas.bundle"),
        "format_id": "spritesheet_atlas_pages",
        "media_type": "application/vnd.mechagotchi.atlas-pages+json",
        "uri": binding.get("uri", "unknown://multi-page-atlas"),
        "width": max((page["width"] for page in manifest), default=0),
        "height": max((page["height"] for page in manifest), default=0),
        "frame_count": binding.get("frame_count", 0),
        "page_count": len(manifest),
        "pages": manifest,
        "content_hash": _hash_payload(manifest),
        "semantic_policy": "sidecar_required",
    }


def _page_asset(
    png_bytes: bytes,
    profile_id: str,
    page_index: int,
    frame_count: int,
) -> dict:
    decoded = decode_png_rgba(png_bytes)
    return {
        "asset_id": f"{profile_id}_multi_page_atlas_page_{page_index}.png",
        "format_id": "spritesheet_png",
        "media_type": "image/png",
        "uri": (
            "generated://workshop/spritesheet-multi-page-atlas/"
            f"{profile_id}_page_{page_index}.png"
        ),
        "width": decoded["width"],
        "height": decoded["height"],
        "frame_count": frame_count,
        "content_hash": _hash_bytes(png_bytes),
        "semantic_policy": "sidecar_required",
    }


def _invalid_probe_results(reference_result: dict) -> list[dict]:
    pages = _pages_from_persisted(reference_result["pages"])
    sidecar = reference_result["sidecar"]

    missing_page_pages = deepcopy(pages[:-1])

    page_hash_sidecar = deepcopy(sidecar)
    page_hash_sidecar["animation_binding"]["pages"][0]["content_hash"] = "sha256:not-the-page"

    unknown_page_sidecar = deepcopy(sidecar)
    unknown_page_sidecar["animation_binding"]["frames"][0]["page_index"] = 999

    out_of_bounds_sidecar = deepcopy(sidecar)
    out_of_bounds_sidecar["animation_binding"]["frames"][1]["rect"]["x"] = (
        out_of_bounds_sidecar["animation_binding"]["pages"][0]["width"]
    )

    wrong_hash_sidecar = deepcopy(sidecar)
    wrong_hash_sidecar["animation_binding"]["frames"][2]["packed_pixel_hash"] = "sha256:not-the-frame"

    bad_order_sidecar = deepcopy(sidecar)
    bad_order_sidecar["animation_binding"]["frames"][3]["playback_order"] = 2

    return [
        _compact_import_result(import_multi_page_atlas_bundle(missing_page_pages, sidecar)),
        _compact_import_result(import_multi_page_atlas_bundle(pages, page_hash_sidecar)),
        _compact_import_result(import_multi_page_atlas_bundle(pages, unknown_page_sidecar)),
        _compact_import_result(import_multi_page_atlas_bundle(pages, out_of_bounds_sidecar)),
        _compact_import_result(import_multi_page_atlas_bundle(pages, wrong_hash_sidecar)),
        _compact_import_result(import_multi_page_atlas_bundle(pages, bad_order_sidecar)),
    ]


def _persistable_pages(pages: list[dict]) -> list[dict]:
    return [
        {
            "page_index": page["page_index"],
            "png_file_name": page["png_file_name"],
            "png_bytes_hex": page["png_bytes"].hex(),
            "asset": page["asset"],
            "decoded_png": page["decoded_png"],
        }
        for page in pages
    ]


def _pages_from_persisted(pages: list[dict]) -> list[dict]:
    return [
        {
            "page_index": page["page_index"],
            "png_bytes": bytes.fromhex(page["png_bytes_hex"]),
            "asset": page["asset"],
        }
        for page in pages
    ]


def _packed_size(region: dict, rotation_degrees: int) -> tuple[int, int]:
    trim = region["trim"]
    if rotation_degrees == 90:
        return trim["h"], trim["w"]
    return trim["w"], trim["h"]


def _rotation_candidates(region: dict, policy: dict) -> list[int]:
    if not policy.get("allow_rotation"):
        return [0]
    trim = region["trim"]
    if trim["w"] == trim["h"]:
        return [0]
    if trim["h"] > trim["w"]:
        return [90, 0]
    return [0, 90]


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
    matches = sum(
        1
        for event in timeline
        if event["canonical_hash_match"] and event["page_hash_match"]
    )
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
        "page_index": frame["page_index"],
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


def _decoded_page_summaries(decoded_pages: dict[int, dict]) -> list[dict]:
    return [
        {
            "page_index": page_index,
            "asset_id": decoded.get("asset_id"),
            "content_hash": decoded["content_hash"],
            **_decoded_summary(decoded),
        }
        for page_index, decoded in sorted(decoded_pages.items())
    ]


def _compact_import_result(result: dict) -> dict:
    return {
        "ok": result["ok"],
        "asset": result.get("asset"),
        "decoded_pages": result.get("decoded_pages"),
        "validation": result.get("validation"),
        "semantic_fidelity": result.get("semantic_fidelity", 0.0),
        "reconstructed_frame_fidelity": result.get("reconstructed_frame_fidelity", 0.0),
        "runtime_frame_fidelity": result.get("runtime_frame_fidelity", 0.0),
        "errors": result.get("errors", []),
        "error_families": result.get("error_families", []),
    }


def _failed_import(errors: list[dict]) -> dict:
    return {
        "ok": False,
        "errors": errors,
        "error_families": sorted({error["family"] for error in errors}),
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


def _hash_payload(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _hash_bytes(encoded)


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
    for result in payload["bundle_results"]:
        for page in result["pages"]:
            page.pop("png_bytes_hex", None)
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
                "bundle_roundtrip_count",
                "bundle_roundtrip_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "page_policy",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "bundle_summaries": [
            {
                "profile_id": result["profile_id"],
                "asset": result["asset"],
                "page_count": result["page_count"],
                "frame_count": result["frame_count"],
                "decoded_pages": result["decoded_pages"],
                "semantic_fidelity": result["semantic_fidelity"],
                "reconstructed_frame_fidelity": result["reconstructed_frame_fidelity"],
                "runtime_frame_fidelity": result["runtime_frame_fidelity"],
                "runtime_playback": result["runtime_playback"],
            }
            for result in json_report["bundle_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# Spritesheet Multi-Page Atlas Stage 0\n\n"
        "Generated multi-page atlas proof with page manifests, per-page hashes, "
        "frame-to-page binding, canonical frame reconstruction, and looped "
        "runtime page-switch sampling.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Bundle round-trip successes: {report['bundle_roundtrip_success_count']}"
        f"/{report['bundle_roundtrip_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- Mean semantic fidelity: {metrics['mean_semantic_fidelity']}\n"
        f"- Mean reconstructed frame fidelity: {metrics['mean_reconstructed_frame_fidelity']}\n"
        f"- Mean runtime frame fidelity: {metrics['mean_runtime_frame_fidelity']}\n"
        f"- Mean page count: {metrics['mean_page_count']}\n"
        f"- Decision: {report['decision']}\n"
    )


def _first_grid_path(profile: dict, generated_root: Path) -> Path:
    grid_paths = sorted((generated_root / profile["profile_id"]).glob("*.json"))
    if not grid_paths:
        raise ValueError(f"no generated grids found for profile: {profile['profile_id']}")
    return grid_paths[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "data/workshop_editor/spritesheet_multi_page_atlas_stage0",
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
    report = run_spritesheet_multi_page_atlas_lab(profile_paths, args.generated_root)
    write_spritesheet_multi_page_atlas_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_SPRITESHEET_MULTI_PAGE_ATLAS = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(_json_report(report), indent=2))


if __name__ == "__main__":
    main()
