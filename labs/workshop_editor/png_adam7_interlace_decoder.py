import argparse
import binascii
import hashlib
import json
import struct
import sys
import zlib
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME_DIR = ROOT / "labs" / "grid_genome"
if str(GRID_GENOME_DIR) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME_DIR))

from slip import is_grid_aligned
from validator import validate_grid

from external_metadata_sidecar import (
    build_sidecar_for_grid,
    restore_grid_from_sidecar,
    validate_sidecar_binding,
)
from standard_image_sidecar_decoder import PNG_SIGNATURE, render_grid_rgba_pixels
from png_chunk_reader import PNGChunkError, bounded_decompress, read_png_chunks
from workshop_editor import compare_semantic_grid_fidelity


REPORT_PATH = ROOT / "data/workshop_editor/png_adam7_interlace_decoder_stage0.json"
DATA_PATH = ROOT / "data/workshop_editor/png_adam7_interlace_decoder_data.js"

ADAM7_PASSES = [
    {"pass_index": 1, "x_start": 0, "y_start": 0, "x_step": 8, "y_step": 8},
    {"pass_index": 2, "x_start": 4, "y_start": 0, "x_step": 8, "y_step": 8},
    {"pass_index": 3, "x_start": 0, "y_start": 4, "x_step": 4, "y_step": 8},
    {"pass_index": 4, "x_start": 2, "y_start": 0, "x_step": 4, "y_step": 4},
    {"pass_index": 5, "x_start": 0, "y_start": 2, "x_step": 2, "y_step": 4},
    {"pass_index": 6, "x_start": 1, "y_start": 0, "x_step": 2, "y_step": 2},
    {"pass_index": 7, "x_start": 0, "y_start": 1, "x_step": 1, "y_step": 2},
]


class PNGAdam7DecodeError(ValueError):
    def __init__(self, family: str, message: str):
        super().__init__(message)
        self.family = family
        self.message = message


def decode_png_adam7_rgba(png_bytes: bytes) -> dict:
    chunks = _read_png_chunks(png_bytes)
    if not chunks or chunks[0]["type"] != "IHDR":
        raise PNGAdam7DecodeError("png_ihdr_missing", "PNG IHDR chunk must be first")

    ihdr = chunks[0]["payload"]
    if len(ihdr) != 13:
        raise PNGAdam7DecodeError("png_ihdr_invalid", "PNG IHDR chunk length must be 13")
    width, height, bit_depth, color_type, compression, filter_method, interlace = (
        struct.unpack(">IIBBBBB", ihdr)
    )
    if width <= 0 or height <= 0:
        raise PNGAdam7DecodeError("png_dimensions_invalid", "PNG dimensions must be positive")
    if bit_depth != 8:
        raise PNGAdam7DecodeError("png_bit_depth_unsupported", "only 8-bit PNG is supported")
    if color_type != 6:
        raise PNGAdam7DecodeError("png_color_type_unsupported", "only 8-bit RGBA PNG is supported")
    if compression != 0 or filter_method != 0:
        raise PNGAdam7DecodeError(
            "png_method_unsupported",
            "only PNG compression method 0 and filter method 0 are supported",
        )
    if interlace != 1:
        raise PNGAdam7DecodeError(
            "png_adam7_interlace_required",
            "this Stage 0 decoder requires Adam7 interlace method 1",
        )

    idat = b"".join(chunk["payload"] for chunk in chunks if chunk["type"] == "IDAT")
    if not idat:
        raise PNGAdam7DecodeError("png_idat_missing", "PNG IDAT chunk is required")
    if not any(chunk["type"] == "IEND" for chunk in chunks):
        raise PNGAdam7DecodeError("png_iend_missing", "PNG IEND chunk is required")
    expected_length = sum(
        _pass_size(height, pass_spec["y_start"], pass_spec["y_step"])
        * (1 + _pass_size(width, pass_spec["x_start"], pass_spec["x_step"]) * 4)
        for pass_spec in ADAM7_PASSES
    )
    try:
        raw = bounded_decompress(idat, expected_length)
    except PNGChunkError as exc:
        raise PNGAdam7DecodeError("png_idat_decompression_failed", exc.message) from exc

    pixels: list[tuple[int, int, int, int]] = [(0, 0, 0, 0)] * (width * height)
    assigned = [False] * (width * height)
    offset = 0
    filter_types_seen = []
    pass_summaries = []

    for pass_spec in ADAM7_PASSES:
        pass_width = _pass_size(width, pass_spec["x_start"], pass_spec["x_step"])
        pass_height = _pass_size(height, pass_spec["y_start"], pass_spec["y_step"])
        pass_filters = []
        previous = None
        for row_index in range(pass_height):
            row_length = pass_width * 4
            if offset + 1 + row_length > len(raw):
                raise PNGAdam7DecodeError(
                    "png_adam7_scanline_length_mismatch",
                    "Adam7 reduced-image scanline data ended early",
                )
            filter_type = raw[offset]
            offset += 1
            if filter_type > 4:
                raise PNGAdam7DecodeError(
                    "png_filter_type_unsupported",
                    "PNG filter type must be in 0..4 for filter method 0",
                )
            row = raw[offset : offset + row_length]
            offset += row_length
            unfiltered = _unfilter_row(row, previous, 4, filter_type)
            previous = unfiltered
            if filter_type not in pass_filters:
                pass_filters.append(filter_type)
            if filter_type not in filter_types_seen:
                filter_types_seen.append(filter_type)
            for pass_x in range(pass_width):
                x = pass_spec["x_start"] + pass_x * pass_spec["x_step"]
                y = pass_spec["y_start"] + row_index * pass_spec["y_step"]
                pixel_offset = pass_x * 4
                pixel = tuple(unfiltered[pixel_offset : pixel_offset + 4])
                pixel_index = y * width + x
                pixels[pixel_index] = pixel
                assigned[pixel_index] = True
        pass_summaries.append(
            {
                "pass_index": pass_spec["pass_index"],
                "x_start": pass_spec["x_start"],
                "y_start": pass_spec["y_start"],
                "x_step": pass_spec["x_step"],
                "y_step": pass_spec["y_step"],
                "width": pass_width,
                "height": pass_height,
                "scanline_count": pass_height,
                "pixel_count": pass_width * pass_height,
                "filter_types_seen": pass_filters,
            }
        )

    if offset != len(raw):
        raise PNGAdam7DecodeError(
            "png_adam7_scanline_length_mismatch",
            "Adam7 reduced-image scanline data has trailing bytes",
        )
    if not all(assigned):
        raise PNGAdam7DecodeError(
            "png_adam7_pixel_coverage_incomplete",
            "Adam7 pass coverage did not assign every output pixel",
        )

    return {
        "width": width,
        "height": height,
        "bit_depth": bit_depth,
        "color_type": color_type,
        "interlace_method": interlace,
        "pixels": pixels,
        "pixel_count": len(pixels),
        "pass_order": [pass_spec["pass_index"] for pass_spec in ADAM7_PASSES],
        "pass_summaries": pass_summaries,
        "non_empty_pass_count": sum(1 for item in pass_summaries if item["pixel_count"] > 0),
        "filter_types_seen": filter_types_seen,
        "chunks": [chunk["type"] for chunk in chunks],
    }


def encode_png_adam7_rgba(
    width: int,
    height: int,
    pixels: list[tuple[int, int, int, int]],
    filter_types: list[int] | None = None,
) -> bytes:
    if width <= 0 or height <= 0:
        raise ValueError("PNG dimensions must be positive")
    if len(pixels) != width * height:
        raise ValueError("pixel count does not match PNG dimensions")
    filters = filter_types or [0, 1, 2, 3, 4]
    if not filters or any(filter_type < 0 or filter_type > 4 for filter_type in filters):
        raise ValueError("filter types must be in 0..4")

    raw = bytearray()
    filter_cursor = 0
    for pass_spec in ADAM7_PASSES:
        pass_width = _pass_size(width, pass_spec["x_start"], pass_spec["x_step"])
        pass_height = _pass_size(height, pass_spec["y_start"], pass_spec["y_step"])
        previous = None
        for row_index in range(pass_height):
            row = bytearray()
            for pass_x in range(pass_width):
                x = pass_spec["x_start"] + pass_x * pass_spec["x_step"]
                y = pass_spec["y_start"] + row_index * pass_spec["y_step"]
                pixel = pixels[y * width + x]
                _validate_rgba_pixel(pixel)
                row.extend(pixel)
            row_bytes = bytes(row)
            filter_type = filters[filter_cursor % len(filters)]
            filter_cursor += 1
            raw.append(filter_type)
            raw.extend(_filter_row(row_bytes, previous, 4, filter_type))
            previous = row_bytes

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 1)
    return (
        PNG_SIGNATURE
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", zlib.compress(bytes(raw)))
        + _png_chunk(b"IEND", b"")
    )


def export_png_adam7_with_sidecar(grid: dict, slip_profile: dict) -> dict:
    width, height = grid["grid_size"]
    source_pixels = render_grid_rgba_pixels(grid)
    png_bytes = encode_png_adam7_rgba(width, height, source_pixels)
    decoded = decode_png_adam7_rgba(png_bytes)
    asset = _asset_from_decoded(
        png_bytes,
        decoded,
        asset_id=f"{slip_profile['profile_id']}_adam7_rgba.png",
        uri=f"generated://workshop/png-adam7/{slip_profile['profile_id']}_adam7_rgba.png",
    )
    sidecar = build_sidecar_for_grid(grid, slip_profile, asset)
    sidecar["sidecar_id"] = f"{grid['grid_id']}_adam7_rgba_sidecar"
    sidecar["adam7_binding"] = {
        "variant_id": "adam7_rgba",
        "color_type": 6,
        "bit_depth": 8,
        "compression_method": 0,
        "filter_method": 0,
        "interlace_method": 1,
        "pass_order": decoded["pass_order"],
        "pass_summaries": decoded["pass_summaries"],
        "non_empty_pass_count": decoded["non_empty_pass_count"],
        "filter_types": decoded["filter_types_seen"],
        "source_render_pixel_hash": _hash_pixels(source_pixels),
        "visual_carrier_pixel_hash": _hash_pixels(decoded["pixels"]),
    }
    sidecar["limitations"] = [
        "Stage 0 Adam7 decoder supports 8-bit RGBA PNG only.",
        "APNG, 16-bit channels, grayscale-alpha, and full PNG conformance are not claimed.",
        "Semantic metadata is restored from the Mechagotchi sidecar, not inferred from pixels.",
    ]
    return {
        "variant_id": "adam7_rgba",
        "png_bytes": png_bytes,
        "png_file_name": f"{slip_profile['profile_id']}_adam7_rgba.png",
        "sidecar_file_name": f"{slip_profile['profile_id']}_adam7_rgba_sidecar.json",
        "asset": asset,
        "sidecar": sidecar,
        "decoded_png": _decoded_summary(decoded),
        "visual_carrier_pixel_hash": _hash_pixels(decoded["pixels"]),
    }


def import_png_adam7_with_sidecar(png_bytes: bytes, sidecar: dict) -> dict:
    try:
        decoded = decode_png_adam7_rgba(png_bytes)
    except PNGAdam7DecodeError as exc:
        return _failed_import("png", exc.family, exc.message)

    binding = sidecar.get("asset_binding", {})
    asset = _asset_from_decoded(
        png_bytes,
        decoded,
        asset_id=binding.get("asset_id", "unknown.png"),
        uri=binding.get("uri", "unknown://png"),
    )
    validation = validate_sidecar_binding(sidecar, asset)
    if not validation["ok"]:
        return {
            "ok": False,
            "asset": asset,
            "decoded_png": _decoded_summary(decoded),
            "validation": validation,
            "errors": validation["errors"],
            "error_families": validation["error_families"],
        }

    adam7_validation = _validate_adam7_binding(sidecar, decoded)
    if not adam7_validation["ok"]:
        return {
            "ok": False,
            "asset": asset,
            "decoded_png": _decoded_summary(decoded),
            "validation": validation,
            "errors": adam7_validation["errors"],
            "error_families": adam7_validation["error_families"],
        }

    restored = restore_grid_from_sidecar(sidecar, asset)
    expected_pixels = render_grid_rgba_pixels(restored)
    if decoded["pixels"] != expected_pixels:
        error = _error(
            "png.pixels",
            "png_adam7_sidecar_pixel_mismatch",
            "decoded Adam7 pixels do not match the sidecar semantic overlay",
        )
        return {
            "ok": False,
            "asset": asset,
            "decoded_png": _decoded_summary(decoded),
            "validation": validation,
            "errors": [error],
            "error_families": [error["family"]],
        }

    source_grid = restore_grid_from_sidecar(sidecar, asset, validate=False)
    diff = compare_semantic_grid_fidelity(source_grid, restored)
    fidelity = _semantic_fidelity(diff, source_grid)
    return {
        "ok": True,
        "asset": asset,
        "decoded_png": _decoded_summary(decoded),
        "validation": validation,
        "restored_grid": restored,
        "semantic_diff": diff,
        "semantic_fidelity": fidelity,
        "pixel_fidelity": 1.0,
        "errors": [],
        "error_families": [],
    }


def run_png_adam7_interlace_decoder_lab(
    profile_paths: list[Path],
    generated_root: Path,
) -> dict:
    png_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        exported = export_png_adam7_with_sidecar(grid, profile)
        imported = import_png_adam7_with_sidecar(
            exported["png_bytes"],
            exported["sidecar"],
        )
        restored = imported.get("restored_grid", {})
        grid_validation = validate_grid(restored) if restored else None
        alignment = is_grid_aligned(restored, profile) if restored else None
        png_results.append(
            {
                "profile_id": profile["profile_id"],
                "profile_path": _portable(profile_path),
                "grid_path": _portable(grid_path),
                "variant_id": exported["variant_id"],
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
                "pixel_fidelity": imported.get("pixel_fidelity", 0.0),
                "pass_summaries": exported["decoded_png"]["pass_summaries"],
            }
        )

    invalid_probe_results = _invalid_probe_results(png_results[0]) if png_results else []
    success_count = sum(1 for result in png_results if result["import_result"]["ok"])
    invalid_rejected = sum(1 for result in invalid_probe_results if not result["ok"])
    return {
        "artifact_id": "png_adam7_interlace_decoder_stage0",
        "status": "research_png_adam7_interlace_decoder_no_package_code",
        "date": "2026-05-14",
        "purpose": (
            "Close the bounded Adam7 interlace decoder gap for 8-bit RGBA PNG "
            "sidecar carriers without claiming APNG or full PNG conformance."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
            "labs/workshop_editor/png_variant_sidecar_decoder.py",
            "labs/workshop_editor/png_adam7_interlace_decoder.py",
        ],
        "external_anchors": [
            {
                "source": "W3C PNG specification",
                "url": "https://www.w3.org/TR/png-3/",
                "used_for": (
                    "IHDR interlace method values, Adam7 pass extraction order, "
                    "filter method 0, IDAT zlib stream, and PNG chunk validation."
                ),
            }
        ],
        "profile_count": len(profile_paths),
        "png_roundtrip_count": len(png_results),
        "png_roundtrip_success_count": success_count,
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected,
        "metrics": {
            "png_roundtrip_success_rate": _ratio(success_count, len(png_results)),
            "mean_semantic_fidelity": _mean(result["semantic_fidelity"] for result in png_results),
            "mean_pixel_fidelity": _mean(result["pixel_fidelity"] for result in png_results),
            "mean_non_empty_pass_count": _mean(
                result["decoded_png"]["non_empty_pass_count"] for result in png_results
            ),
            "invalid_probe_rejection_rate": _ratio(invalid_rejected, len(invalid_probe_results)),
        },
        "adam7_policy": {
            "color_type": 6,
            "bit_depth": 8,
            "interlace_method": 1,
            "pass_count": len(ADAM7_PASSES),
            "passes": deepcopy(ADAM7_PASSES),
            "filter_types": [0, 1, 2, 3, 4],
        },
        "png_results": png_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "png_adam7_interlace_decoder",
            "png_adam7_pass_manifest",
            "png_adam7_filter_type_0_to_4_decoder",
            "png_adam7_sidecar_semantic_restore",
            "png_adam7_invalid_probe_rejection",
        ],
        "blocked_states": [
            "apng_decoder",
            "full_png_conformance",
            "png_16bit_channel_decoder",
            "png_color_type_4_grayscale_alpha_decoder",
            "live_external_editor_rewrite_validation",
            "final_png_production_carrier_selection",
            "package_runtime_lifecycle_integration",
            "manual_readability_calibration",
            "profile_weighted_evolution",
        ],
        "decision": "prototype_png_adam7_interlace_decoder",
        "next_research_step": (
            "Keep APNG, deeper bit-depth/color-type coverage, live external "
            "editor rewrite validation, and final production carrier selection "
            "blocked until direct fixture evidence exists."
        ),
    }


def write_png_adam7_interlace_decoder_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "png_adam7_interlace_decoder_stage0.json", _json_report(report))
    for result in report["png_results"]:
        (output_dir / result["png_file_name"]).write_bytes(
            bytes.fromhex(result["png_bytes_hex"])
        )
        _write_json(output_dir / result["sidecar_file_name"], result["sidecar"])
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "png_adam7_interlace_decoder_data.js").write_text(
        "window.MECHAGOTCHI_PNG_ADAM7_INTERLACE_DECODER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _validate_adam7_binding(sidecar: dict, decoded: dict) -> dict:
    errors = []
    binding = sidecar.get("adam7_binding")
    if not binding:
        errors.append(_error("adam7_binding", "png_adam7_binding_missing"))
    else:
        if binding.get("color_type") != decoded["color_type"]:
            errors.append(_error("adam7_binding.color_type", "png_adam7_color_type_mismatch"))
        if binding.get("bit_depth") != decoded["bit_depth"]:
            errors.append(_error("adam7_binding.bit_depth", "png_adam7_bit_depth_mismatch"))
        if binding.get("interlace_method") != decoded["interlace_method"]:
            errors.append(_error("adam7_binding.interlace_method", "png_adam7_interlace_mismatch"))
        if binding.get("pass_order") != decoded["pass_order"]:
            errors.append(_error("adam7_binding.pass_order", "png_adam7_pass_manifest_mismatch"))
        if binding.get("pass_summaries") != decoded["pass_summaries"]:
            errors.append(_error("adam7_binding.pass_summaries", "png_adam7_pass_manifest_mismatch"))
        expected_filters = sorted(set(binding.get("filter_types", [])))
        actual_filters = sorted(set(decoded["filter_types_seen"]))
        if expected_filters != actual_filters:
            errors.append(_error("adam7_binding.filter_types", "png_adam7_filter_mismatch"))
        if binding.get("visual_carrier_pixel_hash") != _hash_pixels(decoded["pixels"]):
            errors.append(_error("adam7_binding.visual_carrier_pixel_hash", "png_adam7_pixel_hash_mismatch"))
    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "error_families": sorted({error["family"] for error in errors}),
    }


def _invalid_probe_results(reference_result: dict) -> list[dict]:
    png_bytes = bytes.fromhex(reference_result["png_bytes_hex"])
    sidecar = reference_result["sidecar"]
    raw = _idat_raw(png_bytes)

    non_adam7_png = _replace_ihdr_interlace(png_bytes, 0)
    short_scanline_png = _replace_idat_raw(png_bytes, raw[:-1])
    bad_filter_raw = bytearray(raw)
    bad_filter_raw[0] = 5
    bad_filter_png = _replace_idat_raw(png_bytes, bytes(bad_filter_raw))

    wrong_pass_sidecar = deepcopy(sidecar)
    wrong_pass_sidecar["adam7_binding"]["pass_summaries"][0]["pixel_count"] += 1
    wrong_pixel_hash_sidecar = deepcopy(sidecar)
    wrong_pixel_hash_sidecar["adam7_binding"]["visual_carrier_pixel_hash"] = "sha256:not-the-visual-carrier"
    wrong_asset_hash_sidecar = deepcopy(sidecar)
    wrong_asset_hash_sidecar["asset_binding"]["content_hash"] = "sha256:not-the-png"

    return [
        _compact_import_result(import_png_adam7_with_sidecar(non_adam7_png, sidecar)),
        _compact_import_result(import_png_adam7_with_sidecar(short_scanline_png, sidecar)),
        _compact_import_result(import_png_adam7_with_sidecar(bad_filter_png, sidecar)),
        _compact_import_result(import_png_adam7_with_sidecar(png_bytes, wrong_pass_sidecar)),
        _compact_import_result(import_png_adam7_with_sidecar(png_bytes, wrong_pixel_hash_sidecar)),
        _compact_import_result(import_png_adam7_with_sidecar(png_bytes, wrong_asset_hash_sidecar)),
    ]


def _pass_size(size: int, start: int, step: int) -> int:
    if size <= start:
        return 0
    return ((size - start - 1) // step) + 1


def _filter_row(row: bytes, previous: bytes | None, bpp: int, filter_type: int) -> bytes:
    if filter_type == 0:
        return row
    filtered = bytearray()
    for i, value in enumerate(row):
        left = row[i - bpp] if i >= bpp else 0
        up = previous[i] if previous is not None else 0
        upper_left = previous[i - bpp] if previous is not None and i >= bpp else 0
        if filter_type == 1:
            prediction = left
        elif filter_type == 2:
            prediction = up
        elif filter_type == 3:
            prediction = (left + up) // 2
        elif filter_type == 4:
            prediction = _paeth(left, up, upper_left)
        else:
            raise ValueError("filter type must be in 0..4")
        filtered.append((value - prediction) & 0xFF)
    return bytes(filtered)


def _unfilter_row(row: bytes, previous: bytes | None, bpp: int, filter_type: int) -> bytes:
    if filter_type == 0:
        return row
    reconstructed = bytearray()
    for i, value in enumerate(row):
        left = reconstructed[i - bpp] if i >= bpp else 0
        up = previous[i] if previous is not None else 0
        upper_left = previous[i - bpp] if previous is not None and i >= bpp else 0
        if filter_type == 1:
            prediction = left
        elif filter_type == 2:
            prediction = up
        elif filter_type == 3:
            prediction = (left + up) // 2
        elif filter_type == 4:
            prediction = _paeth(left, up, upper_left)
        else:
            raise PNGAdam7DecodeError("png_filter_type_unsupported", "filter type must be in 0..4")
        reconstructed.append((value + prediction) & 0xFF)
    return bytes(reconstructed)


def _paeth(left: int, up: int, upper_left: int) -> int:
    estimate = left + up - upper_left
    distance_left = abs(estimate - left)
    distance_up = abs(estimate - up)
    distance_upper_left = abs(estimate - upper_left)
    if distance_left <= distance_up and distance_left <= distance_upper_left:
        return left
    if distance_up <= distance_upper_left:
        return up
    return upper_left


def _read_png_chunks(png_bytes: bytes) -> list[dict]:
    try:
        return read_png_chunks(png_bytes)
    except PNGChunkError as exc:
        raise PNGAdam7DecodeError(exc.family, exc.message) from exc


def _png_chunk(chunk_type: bytes, payload: bytes) -> bytes:
    crc = binascii.crc32(payload, binascii.crc32(chunk_type)) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + chunk_type + payload + struct.pack(">I", crc)


def _idat_raw(png_bytes: bytes) -> bytes:
    idat = b"".join(chunk["payload"] for chunk in _read_png_chunks(png_bytes) if chunk["type"] == "IDAT")
    return zlib.decompress(idat)


def _replace_idat_raw(png_bytes: bytes, raw: bytes) -> bytes:
    output = [PNG_SIGNATURE]
    replaced = False
    for chunk in _read_png_chunks(png_bytes):
        if chunk["type"] == "IDAT":
            if not replaced:
                output.append(_png_chunk(b"IDAT", zlib.compress(raw)))
                replaced = True
            continue
        output.append(_png_chunk(chunk["type"].encode("ascii"), chunk["payload"]))
    return b"".join(output)


def _replace_ihdr_interlace(png_bytes: bytes, interlace_method: int) -> bytes:
    output = [PNG_SIGNATURE]
    for chunk in _read_png_chunks(png_bytes):
        payload = chunk["payload"]
        if chunk["type"] == "IHDR":
            payload = payload[:12] + bytes([interlace_method])
        output.append(_png_chunk(chunk["type"].encode("ascii"), payload))
    return b"".join(output)


def _asset_from_decoded(
    png_bytes: bytes,
    decoded: dict,
    *,
    asset_id: str,
    uri: str,
) -> dict:
    return {
        "asset_id": asset_id,
        "format_id": "png",
        "media_type": "image/png",
        "uri": uri,
        "width": decoded["width"],
        "height": decoded["height"],
        "frame_count": 1,
        "content_hash": _hash_bytes(png_bytes),
        "semantic_policy": "sidecar_required",
    }


def _compact_import_result(result: dict) -> dict:
    return {
        "ok": result["ok"],
        "asset": result.get("asset"),
        "decoded_png": result.get("decoded_png"),
        "validation": result.get("validation"),
        "semantic_fidelity": result.get("semantic_fidelity", 0.0),
        "pixel_fidelity": result.get("pixel_fidelity", 0.0),
        "errors": result.get("errors", []),
        "error_families": result.get("error_families", []),
    }


def _decoded_summary(decoded: dict) -> dict:
    return {
        "width": decoded["width"],
        "height": decoded["height"],
        "bit_depth": decoded["bit_depth"],
        "color_type": decoded["color_type"],
        "interlace_method": decoded["interlace_method"],
        "pixel_count": decoded["pixel_count"],
        "pass_order": decoded["pass_order"],
        "pass_summaries": decoded["pass_summaries"],
        "non_empty_pass_count": decoded["non_empty_pass_count"],
        "filter_types_seen": decoded["filter_types_seen"],
        "chunks": decoded["chunks"],
    }


def _validate_rgba_pixel(pixel: tuple[int, int, int, int]) -> None:
    if len(pixel) != 4 or any(channel < 0 or channel > 255 for channel in pixel):
        raise ValueError("RGBA pixel channels must be in [0, 255]")


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


def _hash_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _hash_pixels(pixels: list[tuple[int, int, int, int]]) -> str:
    payload = b"".join(bytes(pixel) for pixel in pixels)
    return _hash_bytes(payload)


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


def _mean(values) -> float:
    items = list(values)
    if not items:
        return 0.0
    return round(sum(items) / len(items), 6)


def _json_report(report: dict) -> dict:
    payload = deepcopy(report)
    for result in payload["png_results"]:
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
                "png_roundtrip_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "png_summaries": [
            {
                "profile_id": result["profile_id"],
                "variant_id": result["variant_id"],
                "asset": result["asset"],
                "decoded_png": result["decoded_png"],
                "semantic_fidelity": result["semantic_fidelity"],
                "pixel_fidelity": result["pixel_fidelity"],
            }
            for result in json_report["png_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# PNG Adam7 Interlace Decoder Stage 0\n\n"
        "8-bit RGBA Adam7 interlaced PNG import/export proof bound to "
        "Mechagotchi JSON sidecars.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- PNG round-trip successes: {report['png_roundtrip_success_count']}"
        f"/{report['png_roundtrip_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- Mean semantic fidelity: {metrics['mean_semantic_fidelity']}\n"
        f"- Mean pixel fidelity: {metrics['mean_pixel_fidelity']}\n"
        f"- Mean non-empty Adam7 pass count: {metrics['mean_non_empty_pass_count']}\n"
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
        default=ROOT / "data/workshop_editor/png_adam7_interlace_decoder_stage0",
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
    report = run_png_adam7_interlace_decoder_lab(profile_paths, args.generated_root)
    write_png_adam7_interlace_decoder_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_PNG_ADAM7_INTERLACE_DECODER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(_json_report(report), indent=2))


if __name__ == "__main__":
    main()
