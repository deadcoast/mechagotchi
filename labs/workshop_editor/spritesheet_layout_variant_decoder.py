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


REPORT_PATH = Path("data/workshop_editor/spritesheet_layout_variant_decoder_stage0.json")
DATA_PATH = Path("data/workshop_editor/spritesheet_layout_variant_decoder_data.js")


def export_spritesheet_layout_variant_suite_with_sidecars(
    grid: dict,
    slip_profile: dict,
) -> list[dict]:
    frame_width, frame_height = grid["grid_size"]
    frame_pixels = [
        render_spritesheet_frame_pixels(grid, frame_index)
        for frame_index in range(len(DEFAULT_FRAME_DURATIONS_MS))
    ]
    exports = []
    for layout in _layout_specs(frame_width, frame_height):
        sheet_pixels = _compose_sheet_pixels(
            layout["sheet_width"],
            layout["sheet_height"],
            layout["rects"],
            frame_pixels,
        )
        png_bytes = encode_png_rgba(
            layout["sheet_width"],
            layout["sheet_height"],
            sheet_pixels,
        )
        asset = _asset_from_layout_png(
            png_bytes,
            asset_id=f"{slip_profile['profile_id']}_{layout['layout_id']}.spritesheet.png",
            uri=(
                "generated://workshop/spritesheet-layout/"
                f"{slip_profile['profile_id']}_{layout['layout_id']}.spritesheet.png"
            ),
            frame_count=len(frame_pixels),
        )
        sidecar = build_sidecar_for_grid(grid, slip_profile, asset)
        sidecar["sidecar_id"] = f"{grid['grid_id']}_{layout['layout_id']}_spritesheet_sidecar"
        sidecar["animation_binding"] = _animation_binding(
            grid,
            layout,
            frame_pixels,
            sidecar["integrity"]["semantic_overlay_hash"],
        )
        sidecar["limitations"] = [
            "Stage 0 layout variants support unrotated full-frame rectangles only.",
            "Frame pixels may vary visually; semantic grid metadata is restored from the sidecar.",
            "Packed rotation, trimming, nested tags, layers, and runtime playback are not claimed.",
        ]
        exports.append(
            {
                "layout_id": layout["layout_id"],
                "png_bytes": png_bytes,
                "png_file_name": f"{slip_profile['profile_id']}_{layout['layout_id']}_spritesheet.png",
                "sidecar_file_name": f"{slip_profile['profile_id']}_{layout['layout_id']}_sidecar.json",
                "asset": asset,
                "sidecar": sidecar,
                "decoded_png": _decoded_summary(decode_png_rgba(png_bytes)),
            }
        )
    return exports


def import_spritesheet_layout_variant_with_sidecar(
    png_bytes: bytes,
    sidecar: dict,
    source_grid: dict | None = None,
) -> dict:
    try:
        decoded = decode_png_rgba(png_bytes)
    except PNGDecodeError as exc:
        return _failed_import("png", exc.family, exc.message)

    asset = _asset_from_layout_png(
        png_bytes,
        asset_id=sidecar.get("asset_binding", {}).get("asset_id", "unknown.spritesheet.png"),
        uri=sidecar.get("asset_binding", {}).get("uri", "unknown://spritesheet-layout"),
        frame_count=sidecar.get("asset_binding", {}).get("frame_count", 0),
    )
    validation = validate_layout_variant_sidecar_binding(sidecar, asset, decoded)
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
    frames = extract_layout_variant_frames(decoded, sidecar)
    semantic_source = source_grid or restored
    diff = compare_semantic_grid_fidelity(semantic_source, restored)
    frame_fidelity = _frame_pixel_fidelity(frames, sidecar)
    return {
        "ok": grid_validation.ok and alignment.ok and frame_fidelity == 1.0,
        "asset": asset,
        "decoded_png": _decoded_summary(decoded),
        "validation": validation,
        "restored_grid": restored,
        "frame_count": len(frames),
        "frame_summaries": [_frame_summary(frame) for frame in frames],
        "semantic_diff": diff,
        "semantic_fidelity": _semantic_fidelity(diff, semantic_source),
        "frame_pixel_fidelity": frame_fidelity,
        "errors": [],
        "error_families": [],
    }


def validate_layout_variant_sidecar_binding(
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
    if animation.get("sheet_width") != decoded_png.get("width") or animation.get("sheet_height") != decoded_png.get("height"):
        errors.append(_error("animation_binding.sheet_size", "spritesheet_sheet_size_mismatch"))

    rect_errors = _frame_rect_errors(animation, decoded_png)
    errors.extend(rect_errors)
    frames = extract_layout_variant_frames(decoded_png, sidecar) if not errors else []
    extracted_by_index = {frame["frame_index"]: frame for frame in frames}
    for frame in animation.get("frames", []):
        extracted = extracted_by_index.get(frame.get("frame_index"))
        if extracted and frame.get("pixel_hash") != extracted["pixel_hash"]:
            errors.append(_error("animation_binding.frames.pixel_hash", "spritesheet_frame_hash_mismatch"))

    profile = sidecar.get("slip_binding", {}).get("profile_snapshot", {})
    restored = restore_grid_from_sidecar(sidecar, asset, validate=False) if profile else {}
    if restored:
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


def extract_layout_variant_frames(decoded_png: dict, sidecar: dict) -> list[dict]:
    pixels = decoded_png["pixels"]
    sheet_width = decoded_png["width"]
    frames = []
    for frame in sidecar.get("animation_binding", {}).get("frames", []):
        rect = frame["rect"]
        extracted = []
        for y in range(rect["y"], rect["y"] + rect["h"]):
            row_start = y * sheet_width + rect["x"]
            extracted.extend(pixels[row_start : row_start + rect["w"]])
        frames.append(
            {
                "frame_index": frame["frame_index"],
                "rect": deepcopy(rect),
                "duration_ms": frame["duration_ms"],
                "pixels": extracted,
                "pixel_hash": _hash_pixels(extracted),
            }
        )
    return frames


def run_spritesheet_layout_variant_decoder_lab(
    profile_paths: list[Path],
    generated_root: Path,
) -> dict:
    layout_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        for exported in export_spritesheet_layout_variant_suite_with_sidecars(grid, profile):
            imported = import_spritesheet_layout_variant_with_sidecar(
                exported["png_bytes"],
                exported["sidecar"],
                source_grid=grid,
            )
            restored = imported.get("restored_grid", {})
            grid_validation = validate_grid(restored) if restored else None
            alignment = is_grid_aligned(restored, profile) if restored else None
            layout_results.append(
                {
                    "profile_id": profile["profile_id"],
                    "profile_path": _portable(profile_path),
                    "grid_path": _portable(grid_path),
                    "layout_id": exported["layout_id"],
                    "png_file_name": exported["png_file_name"],
                    "sidecar_file_name": exported["sidecar_file_name"],
                    "png_bytes_hex": exported["png_bytes"].hex(),
                    "png_byte_count": len(exported["png_bytes"]),
                    "asset": exported["asset"],
                    "sidecar": exported["sidecar"],
                    "decoded_png": exported["decoded_png"],
                    "import_result": _compact_import_result(imported),
                    "restored_grid_validation": {
                        "valid": bool(grid_validation and grid_validation.ok),
                        "errors": grid_validation.errors if grid_validation else [],
                        "slip_aligned": bool(alignment and alignment.ok),
                        "slip_errors": alignment.errors if alignment else [],
                    },
                    "semantic_diff": imported.get("semantic_diff", {}),
                    "semantic_fidelity": imported.get("semantic_fidelity", 0.0),
                    "frame_pixel_fidelity": imported.get("frame_pixel_fidelity", 0.0),
                    "frame_count": imported.get("frame_count", 0),
                }
            )

    invalid_probe_results = _invalid_probe_results(layout_results[0])
    success_count = sum(
        1
        for result in layout_results
        if result["import_result"]["ok"]
        and result["restored_grid_validation"]["valid"]
        and result["restored_grid_validation"]["slip_aligned"]
        and result["semantic_fidelity"] == 1.0
        and result["frame_pixel_fidelity"] == 1.0
    )
    invalid_rejected_count = sum(1 for result in invalid_probe_results if not result["ok"])
    return {
        "artifact_id": "spritesheet_layout_variant_decoder_stage0",
        "status": "research_spritesheet_layout_variant_decoder_no_package_code",
        "date": "2026-05-13",
        "purpose": (
            "Broaden the fixed-horizontal-strip spritesheet proof to explicit "
            "layout variants while preserving Mechagotchi semantics through "
            "sidecar metadata."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
            "labs/workshop_editor/spritesheet_sidecar_decoder.py",
            "labs/workshop_editor/spritesheet_layout_variant_decoder.py",
        ],
        "external_anchors": [
            {
                "source": "Aseprite sprite-sheet documentation",
                "url": "https://www.aseprite.org/docs/sprite-sheet/",
                "used_for": "Horizontal, vertical, matrix, padding, and sheet-type workflow boundaries.",
            },
            {
                "source": "Aseprite CLI documentation",
                "url": "https://aseprite.com/docs/cli/",
                "used_for": "Rows, columns, packed sheet type, sheet width/height, and JSON data export context.",
            },
            {
                "source": "Pixelorama import documentation",
                "url": "https://pixelorama.org/user_manual/Import/",
                "used_for": "Spritesheet import workflow context; Pixelorama metadata is not treated as Mechagotchi schema.",
            },
            {
                "source": "W3C PNG specification",
                "url": "https://www.w3.org/TR/png-3/",
                "used_for": "PNG remains the image carrier for layout-variant spritesheets.",
            },
        ],
        "profile_count": len(profile_paths),
        "layout_count_per_profile": len(_layout_specs(8, 8)),
        "layout_roundtrip_count": len(layout_results),
        "layout_roundtrip_success_count": success_count,
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "metrics": {
            "layout_roundtrip_success_rate": _ratio(success_count, len(layout_results)),
            "mean_semantic_fidelity": round(
                sum(result["semantic_fidelity"] for result in layout_results)
                / max(1, len(layout_results)),
                6,
            ),
            "mean_frame_pixel_fidelity": round(
                sum(result["frame_pixel_fidelity"] for result in layout_results)
                / max(1, len(layout_results)),
                6,
            ),
            "invalid_probe_rejection_rate": _ratio(
                invalid_rejected_count,
                len(invalid_probe_results),
            ),
        },
        "layout_results": layout_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "spritesheet_vertical_matrix_padded_sparse_layout_decoder",
            "spritesheet_layout_variant_sidecar_export",
            "spritesheet_layout_variant_sidecar_import",
            "spritesheet_layout_rect_duration_hash_validation",
            "spritesheet_layout_sidecar_semantic_restore",
        ],
        "blocked_states": [
            "spritesheet_packed_rotation_trim_decoder",
            "runtime_animation_playback",
            "full_project_format_coverage",
            "embedded_png_metadata_writer",
            "project_file_native_metadata_writer",
            "profile_weighted_evolution",
        ],
        "decision": "prototype_spritesheet_layout_variant_decoder",
        "next_research_step": (
            "Specify runtime lifecycle/archive selection integration before "
            "profile-weighted evolution claims."
        ),
    }


def write_spritesheet_layout_variant_decoder_artifacts(
    output_dir: Path,
    report: dict,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(
        output_dir / "spritesheet_layout_variant_decoder_stage0.json",
        _json_report(report),
    )
    for result in report["layout_results"]:
        (output_dir / result["png_file_name"]).write_bytes(
            bytes.fromhex(result["png_bytes_hex"])
        )
        _write_json(output_dir / result["sidecar_file_name"], result["sidecar"])
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "spritesheet_layout_variant_decoder_data.js").write_text(
        "window.MECHAGOTCHI_SPRITESHEET_LAYOUT_VARIANTS = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _layout_specs(frame_width: int, frame_height: int) -> list[dict]:
    return [
        {
            "layout_id": "vertical_strip",
            "layout_model": "vertical_strip_equal_frames_v1",
            "sheet_width": frame_width,
            "sheet_height": frame_height * 3,
            "rects": [
                {"x": 0, "y": index * frame_height, "w": frame_width, "h": frame_height}
                for index in range(3)
            ],
            "order": "top_to_bottom",
        },
        {
            "layout_id": "row_major_matrix",
            "layout_model": "row_major_matrix_equal_frames_v1",
            "sheet_width": frame_width * 2,
            "sheet_height": frame_height * 2,
            "rects": [
                {"x": 0, "y": 0, "w": frame_width, "h": frame_height},
                {"x": frame_width, "y": 0, "w": frame_width, "h": frame_height},
                {"x": 0, "y": frame_height, "w": frame_width, "h": frame_height},
            ],
            "order": "row_major",
        },
        {
            "layout_id": "padded_grid",
            "layout_model": "padded_grid_equal_frames_v1",
            "sheet_width": frame_width * 3 + 4,
            "sheet_height": frame_height + 2,
            "rects": [
                {"x": 1 + index * (frame_width + 1), "y": 1, "w": frame_width, "h": frame_height}
                for index in range(3)
            ],
            "order": "left_to_right_with_margin_and_gutter",
        },
        {
            "layout_id": "sparse_atlas",
            "layout_model": "sparse_atlas_unrotated_rects_v1",
            "sheet_width": frame_width + 11,
            "sheet_height": frame_height + 13,
            "rects": [
                {"x": 0, "y": 0, "w": frame_width, "h": frame_height},
                {"x": frame_width + 3, "y": 1, "w": frame_width, "h": frame_height},
                {"x": 1, "y": frame_height + 5, "w": frame_width, "h": frame_height},
            ],
            "order": "explicit_frame_rects",
        },
    ]


def _compose_sheet_pixels(
    sheet_width: int,
    sheet_height: int,
    rects: list[dict],
    frame_pixels: list[list[tuple[int, int, int, int]]],
) -> list[tuple[int, int, int, int]]:
    sheet = [(0, 0, 0, 0)] * (sheet_width * sheet_height)
    for rect, pixels in zip(rects, frame_pixels, strict=True):
        for y in range(rect["h"]):
            for x in range(rect["w"]):
                sheet_index = (rect["y"] + y) * sheet_width + rect["x"] + x
                frame_index = y * rect["w"] + x
                sheet[sheet_index] = pixels[frame_index]
    return sheet


def _animation_binding(
    grid: dict,
    layout: dict,
    frame_pixels: list[list[tuple[int, int, int, int]]],
    semantic_hash: str,
) -> dict:
    return {
        "animation_model": "layout_variant_sidecar_v1",
        "layout_id": layout["layout_id"],
        "layout_model": layout["layout_model"],
        "layout_order": layout["order"],
        "sheet_width": layout["sheet_width"],
        "sheet_height": layout["sheet_height"],
        "frame_width": grid["grid_size"][0],
        "frame_height": grid["grid_size"][1],
        "frame_count": len(frame_pixels),
        "loop": True,
        "frames": [
            {
                "frame_index": index,
                "grid_id": grid["grid_id"],
                "rect": deepcopy(layout["rects"][index]),
                "duration_ms": DEFAULT_FRAME_DURATIONS_MS[index],
                "pixel_hash": _hash_pixels(frame_pixels[index]),
                "semantic_overlay_hash": semantic_hash,
                "visual_delta": _visual_delta_label(index),
                "rotation": 0,
                "trimmed": False,
            }
            for index in range(len(frame_pixels))
        ],
        "limitations": [
            "Only unrotated, untrimmed full-frame rectangles are covered.",
            "Frame timing is metadata-only; no runtime animation playback is claimed.",
        ],
    }


def _frame_rect_errors(animation: dict, decoded_png: dict) -> list[dict]:
    errors = []
    sheet_width = decoded_png.get("width", 0)
    sheet_height = decoded_png.get("height", 0)
    expected_frame_count = animation.get("frame_count", 0)
    frames = animation.get("frames", [])
    if len(frames) != expected_frame_count:
        errors.append(_error("animation_binding.frames", "asset_frame_count_mismatch"))
    occupied = set()
    seen_indices = set()
    for frame in frames:
        frame_index = frame.get("frame_index")
        if frame_index in seen_indices:
            errors.append(_error("animation_binding.frames", "duplicate_frame_index"))
        seen_indices.add(frame_index)
        rect = frame.get("rect", {})
        fields = [rect.get(key) for key in ["x", "y", "w", "h"]]
        if not all(isinstance(value, int) for value in fields):
            errors.append(_error("animation_binding.frames.rect", "spritesheet_frame_rect_invalid"))
            continue
        x, y, width, height = fields
        if width <= 0 or height <= 0:
            errors.append(_error("animation_binding.frames.rect", "spritesheet_frame_rect_invalid"))
            continue
        if x < 0 or y < 0 or x + width > sheet_width or y + height > sheet_height:
            errors.append(_error("animation_binding.frames.rect", "spritesheet_frame_rect_out_of_bounds"))
            continue
        if frame.get("rotation", 0) != 0:
            errors.append(_error("animation_binding.frames.rotation", "spritesheet_frame_rotation_unsupported"))
        if frame.get("trimmed") is True:
            errors.append(_error("animation_binding.frames.trimmed", "spritesheet_frame_trim_unsupported"))
        for yy in range(y, y + height):
            for xx in range(x, x + width):
                coordinate = (xx, yy)
                if coordinate in occupied:
                    errors.append(_error("animation_binding.frames.rect", "spritesheet_frame_rect_overlap"))
                    break
                occupied.add(coordinate)
            if errors and errors[-1]["family"] == "spritesheet_frame_rect_overlap":
                break
    return errors


def _asset_from_layout_png(
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
    out_of_bounds_sidecar = deepcopy(sidecar)
    out_of_bounds_sidecar["animation_binding"]["frames"][0]["rect"]["x"] = (
        sidecar["animation_binding"]["sheet_width"] - 1
    )
    overlapping_sidecar = deepcopy(sidecar)
    overlapping_sidecar["animation_binding"]["frames"][1]["rect"] = deepcopy(
        overlapping_sidecar["animation_binding"]["frames"][0]["rect"]
    )
    wrong_hash_sidecar = deepcopy(sidecar)
    wrong_hash_sidecar["animation_binding"]["frames"][0]["pixel_hash"] = "sha256:not-the-frame"
    return [
        _compact_import_result(
            import_spritesheet_layout_variant_with_sidecar(png_bytes, out_of_bounds_sidecar)
        ),
        _compact_import_result(
            import_spritesheet_layout_variant_with_sidecar(png_bytes, overlapping_sidecar)
        ),
        _compact_import_result(
            import_spritesheet_layout_variant_with_sidecar(png_bytes, wrong_hash_sidecar)
        ),
    ]


def _frame_pixel_fidelity(frames: list[dict], sidecar: dict) -> float:
    expected = {
        frame["frame_index"]: frame["pixel_hash"]
        for frame in sidecar["animation_binding"]["frames"]
    }
    if not frames:
        return 0.0
    matches = sum(
        1 for frame in frames if expected.get(frame["frame_index"]) == frame["pixel_hash"]
    )
    return _ratio(matches, len(frames))


def _frame_summary(frame: dict) -> dict:
    return {
        "frame_index": frame["frame_index"],
        "rect": frame["rect"],
        "duration_ms": frame["duration_ms"],
        "pixel_hash": frame["pixel_hash"],
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
        "frame_pixel_fidelity": result.get("frame_pixel_fidelity", 0.0),
        "errors": result.get("errors", []),
        "error_families": result.get("error_families", []),
    }


def _visual_delta_label(frame_index: int) -> str:
    return ["base_pose", "sensor_blink", "anchor_pulse"][frame_index]


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
    for result in payload["layout_results"]:
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
                "layout_count_per_profile",
                "layout_roundtrip_count",
                "layout_roundtrip_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "layout_summaries": [
            {
                "profile_id": result["profile_id"],
                "layout_id": result["layout_id"],
                "asset": result["asset"],
                "decoded_png": result["decoded_png"],
                "frame_count": result["frame_count"],
                "semantic_fidelity": result["semantic_fidelity"],
                "frame_pixel_fidelity": result["frame_pixel_fidelity"],
            }
            for result in json_report["layout_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# Spritesheet Layout Variant Decoder Stage 0\n\n"
        "Vertical, matrix, padded-grid, and sparse-atlas spritesheet PNG "
        "layout proof bound to Mechagotchi JSON sidecars.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Layouts per profile: {report['layout_count_per_profile']}\n"
        f"- Layout round-trip successes: {report['layout_roundtrip_success_count']}"
        f"/{report['layout_roundtrip_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- Mean semantic fidelity: {metrics['mean_semantic_fidelity']}\n"
        f"- Mean frame pixel fidelity: {metrics['mean_frame_pixel_fidelity']}\n"
        f"- Decision: {report['decision']}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/workshop_editor/spritesheet_layout_variant_decoder_stage0"),
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
    report = run_spritesheet_layout_variant_decoder_lab(profile_paths, args.generated_root)
    write_spritesheet_layout_variant_decoder_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_SPRITESHEET_LAYOUT_VARIANTS = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(_json_report(report), indent=2))


if __name__ == "__main__":
    main()
