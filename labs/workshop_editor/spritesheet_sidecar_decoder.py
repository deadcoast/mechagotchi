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
from standard_image_sidecar_decoder import (
    PNGDecodeError,
    decode_png_rgba,
    encode_png_rgba,
    render_grid_rgba_pixels,
)
from workshop_editor import compare_semantic_grid_fidelity


DEFAULT_FRAME_DURATIONS_MS = [120, 160, 120]
REPORT_PATH = Path("data/workshop_editor/spritesheet_sidecar_decoder_stage0.json")
DATA_PATH = Path("data/workshop_editor/spritesheet_sidecar_decoder_data.js")


def render_spritesheet_frame_pixels(
    grid: dict,
    frame_index: int,
) -> list[tuple[int, int, int, int]]:
    pixels = render_grid_rgba_pixels(grid)
    if frame_index == 0:
        return pixels

    width, _height = grid["grid_size"]
    adjusted = list(pixels)
    cells_by_coordinate = {
        (cell["x"], cell["y"]): cell for cell in grid.get("cells", [])
    }
    if frame_index == 1:
        background = _hex_to_rgba(
            grid["palette"]["colors"][grid["palette"].get("background_index", 0)]
        )
        for cell in grid.get("cells", []):
            if cell.get("role") == "eye":
                adjusted[cell["y"] * width + cell["x"]] = background
    elif frame_index == 2:
        for cell in grid.get("cells", []):
            if cell.get("animation_anchor"):
                rgba = _hex_to_rgba(cell["visual"])
                adjusted[cell["y"] * width + cell["x"]] = _lighten_rgba(rgba)
    else:
        raise ValueError(f"unsupported Stage 0 frame index: {frame_index}")
    return adjusted


def export_spritesheet_with_sidecar(
    grid: dict,
    slip_profile: dict,
    *,
    durations_ms: list[int] | None = None,
) -> dict:
    durations = durations_ms or DEFAULT_FRAME_DURATIONS_MS
    if len(durations) != 3:
        raise ValueError("Stage 0 spritesheet proof expects exactly 3 frames")

    frame_width, frame_height = grid["grid_size"]
    frame_pixels = [
        render_spritesheet_frame_pixels(grid, frame_index)
        for frame_index in range(len(durations))
    ]
    sheet_pixels = _pack_horizontal_frames(frame_width, frame_height, frame_pixels)
    png_bytes = encode_png_rgba(frame_width * len(durations), frame_height, sheet_pixels)
    asset = _asset_from_spritesheet_png(
        png_bytes,
        asset_id=f"{grid['grid_id']}.spritesheet.png",
        uri=f"generated://workshop/spritesheet/{grid['grid_id']}.spritesheet.png",
        frame_count=len(durations),
    )
    sidecar = build_sidecar_for_grid(grid, slip_profile, asset)
    sidecar["sidecar_id"] = f"{grid['grid_id']}_spritesheet_sidecar"
    sidecar["animation_binding"] = _animation_binding(
        grid,
        frame_width,
        frame_height,
        durations,
        frame_pixels,
        sidecar["integrity"]["semantic_overlay_hash"],
    )
    sidecar["limitations"] = [
        "Stage 0 spritesheet decoder supports a horizontal strip of equal-size frames only.",
        "Frame pixels may vary visually; semantic grid metadata is restored from the sidecar.",
    ]
    return {
        "png_bytes": png_bytes,
        "asset": asset,
        "sidecar": sidecar,
        "frame_pixels": frame_pixels,
        "sheet_pixel_count": len(sheet_pixels),
    }


def extract_spritesheet_frames(decoded_png: dict, sidecar: dict) -> list[dict]:
    animation = sidecar.get("animation_binding", {})
    frame_width = animation.get("frame_width")
    frame_height = animation.get("frame_height")
    frames = []
    pixels = decoded_png["pixels"]
    sheet_width = decoded_png["width"]
    for frame in animation.get("frames", []):
        rect = frame["rect"]
        extracted = []
        for y in range(rect["y"], rect["y"] + frame_height):
            row_start = y * sheet_width + rect["x"]
            extracted.extend(pixels[row_start : row_start + frame_width])
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


def import_spritesheet_with_sidecar(
    png_bytes: bytes,
    sidecar: dict,
    source_grid: dict | None = None,
) -> dict:
    try:
        decoded = decode_png_rgba(png_bytes)
    except PNGDecodeError as exc:
        return _failed_import("png", exc.family, exc.message)

    asset = _asset_from_spritesheet_png(
        png_bytes,
        asset_id=sidecar.get("asset_binding", {}).get("asset_id", "unknown.spritesheet.png"),
        uri=sidecar.get("asset_binding", {}).get("uri", "unknown://spritesheet"),
        frame_count=sidecar.get("asset_binding", {}).get("frame_count", 0),
    )
    validation = validate_spritesheet_sidecar_binding(sidecar, asset, decoded)
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
    frames = extract_spritesheet_frames(decoded, sidecar)
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


def validate_spritesheet_sidecar_binding(
    sidecar: dict,
    asset: dict,
    decoded_png: dict,
) -> dict:
    errors = []
    binding = sidecar.get("asset_binding", {})
    animation = sidecar.get("animation_binding", {})
    grid_contract = sidecar.get("grid_contract", {})
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

    frame_width = animation.get("frame_width")
    frame_height = animation.get("frame_height")
    if grid_contract.get("grid_size") != [frame_width, frame_height]:
        errors.append(_error("animation_binding.frame_size", "frame_grid_size_mismatch"))
    if decoded_png.get("width") != frame_width * animation.get("frame_count", 0):
        errors.append(_error("animation_binding.sheet_width", "spritesheet_width_mismatch"))
    if decoded_png.get("height") != frame_height:
        errors.append(_error("animation_binding.sheet_height", "spritesheet_height_mismatch"))

    seen_indices = set()
    frames = extract_spritesheet_frames(decoded_png, sidecar) if not errors else []
    extracted_by_index = {frame["frame_index"]: frame for frame in frames}
    for frame in animation.get("frames", []):
        frame_index = frame.get("frame_index")
        if frame_index in seen_indices:
            errors.append(_error("animation_binding.frames", "duplicate_frame_index"))
        seen_indices.add(frame_index)
        rect = frame.get("rect", {})
        expected_x = frame_index * frame_width if isinstance(frame_index, int) else None
        if rect != {"x": expected_x, "y": 0, "w": frame_width, "h": frame_height}:
            errors.append(_error("animation_binding.frames.rect", "spritesheet_frame_rect_mismatch"))
        extracted = extracted_by_index.get(frame_index)
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


def run_spritesheet_sidecar_decoder_lab(
    profile_paths: list[Path],
    generated_root: Path,
) -> dict:
    spritesheet_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        exported = export_spritesheet_with_sidecar(grid, profile)
        imported = import_spritesheet_with_sidecar(
            exported["png_bytes"],
            exported["sidecar"],
            source_grid=grid,
        )
        restored = imported.get("restored_grid", {})
        grid_validation = validate_grid(restored) if restored else None
        alignment = is_grid_aligned(restored, profile) if restored else None
        spritesheet_results.append(
            {
                "profile_id": profile["profile_id"],
                "profile_path": _portable(profile_path),
                "grid_path": _portable(grid_path),
                "png_file_name": f"{profile['profile_id']}_spritesheet.png",
                "sidecar_file_name": f"{profile['profile_id']}_spritesheet_sidecar.json",
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
                "frame_pixel_fidelity": imported.get("frame_pixel_fidelity", 0.0),
                "frame_count": imported.get("frame_count", 0),
            }
        )

    invalid_probe_results = _invalid_probe_results(spritesheet_results[0])
    success_count = sum(
        1
        for result in spritesheet_results
        if result["import_result"]["ok"]
        and result["restored_grid_validation"]["valid"]
        and result["restored_grid_validation"]["slip_aligned"]
        and result["semantic_fidelity"] == 1.0
        and result["frame_pixel_fidelity"] == 1.0
    )
    invalid_rejected_count = sum(1 for result in invalid_probe_results if not result["ok"])
    return {
        "artifact_id": "spritesheet_sidecar_decoder_stage0",
        "status": "research_spritesheet_sidecar_decoder_no_package_code",
        "date": "2026-05-12",
        "purpose": (
            "Prove a fixed-grid horizontal spritesheet PNG can carry frame "
            "rectangles, durations, and pixel hashes through a Mechagotchi "
            "sidecar without losing semantic SLIP alignment."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
            "labs/workshop_editor/standard_image_sidecar_decoder.py",
            "labs/workshop_editor/spritesheet_sidecar_decoder.py",
        ],
        "external_anchors": [
            {
                "source": "W3C PNG specification",
                "url": "https://www.w3.org/TR/png-3/",
                "used_for": "PNG remains the image carrier for the horizontal spritesheet strip.",
            },
            {
                "source": "Aseprite sprite-sheet documentation",
                "url": "https://www.aseprite.org/docs/sprite-sheet/",
                "used_for": "Spritesheet export is treated as image plus external frame metadata.",
            },
            {
                "source": "Pixelorama import documentation",
                "url": "https://www.pixelorama.org/user_manual/Import/",
                "used_for": "Spritesheet import is treated as workflow context, not as Mechagotchi schema.",
            },
        ],
        "profile_count": len(spritesheet_results),
        "spritesheet_roundtrip_success_count": success_count,
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "metrics": {
            "spritesheet_roundtrip_success_rate": _ratio(success_count, len(spritesheet_results)),
            "mean_semantic_fidelity": round(
                sum(result["semantic_fidelity"] for result in spritesheet_results)
                / max(1, len(spritesheet_results)),
                6,
            ),
            "mean_frame_pixel_fidelity": round(
                sum(result["frame_pixel_fidelity"] for result in spritesheet_results)
                / max(1, len(spritesheet_results)),
                6,
            ),
            "invalid_probe_rejection_rate": _ratio(
                invalid_rejected_count,
                len(invalid_probe_results),
            ),
            "frame_count_per_profile": DEFAULT_FRAME_DURATIONS_MS.__len__(),
        },
        "spritesheet_results": spritesheet_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "spritesheet_fixed_grid_frame_metadata_decoder",
            "spritesheet_sidecar_export",
            "spritesheet_sidecar_import",
            "spritesheet_frame_rect_duration_hash_validation",
            "spritesheet_sidecar_semantic_restore",
        ],
        "blocked_states": [
            "spritesheet_packed_rotation_trim_decoder",
            "runtime_animation_playback",
            "full_project_format_coverage",
            "embedded_png_metadata_writer",
            "project_file_native_metadata_writer",
            "profile_weighted_evolution",
        ],
        "decision": "prototype_fixed_grid_spritesheet_sidecar_decoder",
        "next_research_step": (
            "Run held-out long-horizon behavior tests and manual readability "
            "calibration before profile-weighted evolution claims."
        ),
    }


def write_spritesheet_sidecar_decoder_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "spritesheet_sidecar_decoder_stage0.json", _json_report(report))
    for result in report["spritesheet_results"]:
        (output_dir / result["png_file_name"]).write_bytes(bytes.fromhex(result["png_bytes_hex"]))
        _write_json(output_dir / result["sidecar_file_name"], result["sidecar"])
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "spritesheet_sidecar_decoder_data.js").write_text(
        "window.MECHAGOTCHI_SPRITESHEET_SIDECAR_DECODER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _animation_binding(
    grid: dict,
    frame_width: int,
    frame_height: int,
    durations: list[int],
    frame_pixels: list[list[tuple[int, int, int, int]]],
    semantic_hash: str,
) -> dict:
    return {
        "animation_model": "fixed_horizontal_strip_v1",
        "frame_width": frame_width,
        "frame_height": frame_height,
        "frame_count": len(durations),
        "loop": True,
        "frames": [
            {
                "frame_index": index,
                "grid_id": grid["grid_id"],
                "rect": {"x": index * frame_width, "y": 0, "w": frame_width, "h": frame_height},
                "duration_ms": durations[index],
                "pixel_hash": _hash_pixels(frame_pixels[index]),
                "semantic_overlay_hash": semantic_hash,
                "visual_delta": _visual_delta_label(index),
            }
            for index in range(len(durations))
        ],
        "limitations": [
            "Only fixed equal-size horizontal strips are covered.",
            "Frame timing is metadata-only; no runtime animation playback is claimed.",
        ],
    }


def _pack_horizontal_frames(
    frame_width: int,
    frame_height: int,
    frame_pixels: list[list[tuple[int, int, int, int]]],
) -> list[tuple[int, int, int, int]]:
    sheet = []
    for y in range(frame_height):
        for frame in frame_pixels:
            row_start = y * frame_width
            sheet.extend(frame[row_start : row_start + frame_width])
    return sheet


def _asset_from_spritesheet_png(
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
    corrupt_png = b"not-a-png" + png_bytes[8:]
    wrong_frame_hash_sidecar = deepcopy(sidecar)
    wrong_frame_hash_sidecar["animation_binding"]["frames"][0]["pixel_hash"] = "sha256:not-the-frame"
    return [
        _compact_import_result(import_spritesheet_with_sidecar(corrupt_png, sidecar)),
        _compact_import_result(import_spritesheet_with_sidecar(png_bytes, wrong_frame_hash_sidecar)),
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


def _hex_to_rgba(value: str) -> tuple[int, int, int, int]:
    if not isinstance(value, str) or len(value) != 7 or not value.startswith("#"):
        raise ValueError(f"expected #RRGGBB color, got {value!r}")
    return (
        int(value[1:3], 16),
        int(value[3:5], 16),
        int(value[5:7], 16),
        255,
    )


def _lighten_rgba(pixel: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    return (
        min(255, pixel[0] + 32),
        min(255, pixel[1] + 32),
        min(255, pixel[2] + 32),
        pixel[3],
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
    for result in payload["spritesheet_results"]:
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
                "spritesheet_roundtrip_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "spritesheet_summaries": [
            {
                "profile_id": result["profile_id"],
                "asset": result["asset"],
                "decoded_png": result["decoded_png"],
                "frame_count": result["frame_count"],
                "semantic_fidelity": result["semantic_fidelity"],
                "frame_pixel_fidelity": result["frame_pixel_fidelity"],
            }
            for result in json_report["spritesheet_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# Spritesheet Sidecar Decoder Stage 0\n\n"
        "Fixed horizontal-strip spritesheet PNG import/export proof bound to "
        "Mechagotchi JSON sidecars.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Spritesheet round-trip successes: {report['spritesheet_roundtrip_success_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- Mean semantic fidelity: {metrics['mean_semantic_fidelity']}\n"
        f"- Mean frame pixel fidelity: {metrics['mean_frame_pixel_fidelity']}\n"
        f"- Frame count per profile: {metrics['frame_count_per_profile']}\n"
        f"- Decision: {report['decision']}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/workshop_editor/spritesheet_sidecar_decoder_stage0"),
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
    report = run_spritesheet_sidecar_decoder_lab(profile_paths, args.generated_root)
    write_spritesheet_sidecar_decoder_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_SPRITESHEET_SIDECAR_DECODER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(_json_report(report), indent=2))


if __name__ == "__main__":
    main()
