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


REPORT_PATH = Path("data/workshop_editor/png_variant_sidecar_decoder_stage0.json")
DATA_PATH = Path("data/workshop_editor/png_variant_sidecar_decoder_data.js")

CHANNELS_BY_COLOR_TYPE = {
    0: 1,
    2: 3,
    3: 1,
    6: 4,
}

VARIANT_SPECS = [
    {
        "variant_id": "rgba_filter_none",
        "color_type": 6,
        "filter_types": [0],
        "description": "8-bit RGBA truecolor with alpha and filter type 0.",
    },
    {
        "variant_id": "rgba_filter_cycle",
        "color_type": 6,
        "filter_types": [0, 1, 2, 3, 4],
        "description": "8-bit RGBA truecolor with alpha cycling filters 0 through 4.",
    },
    {
        "variant_id": "rgb_truecolor_sub",
        "color_type": 2,
        "filter_types": [1],
        "description": "8-bit RGB truecolor using Sub filtering.",
    },
    {
        "variant_id": "grayscale_up",
        "color_type": 0,
        "filter_types": [2],
        "description": "8-bit grayscale visual carrier using Up filtering.",
    },
    {
        "variant_id": "indexed_palette_average_paeth",
        "color_type": 3,
        "filter_types": [3, 4],
        "description": "8-bit indexed-color carrier with PLTE and Average/Paeth filtering.",
    },
]


class PNGVariantDecodeError(ValueError):
    def __init__(self, family: str, message: str):
        super().__init__(message)
        self.family = family
        self.message = message


def decode_png_variant(png_bytes: bytes) -> dict:
    chunks = _read_png_chunks(png_bytes)
    if not chunks or chunks[0]["type"] != "IHDR":
        raise PNGVariantDecodeError("png_ihdr_missing", "PNG IHDR chunk must be first")

    ihdr = chunks[0]["payload"]
    if len(ihdr) != 13:
        raise PNGVariantDecodeError("png_ihdr_invalid", "PNG IHDR chunk length must be 13")
    width, height, bit_depth, color_type, compression, filter_method, interlace = (
        struct.unpack(">IIBBBBB", ihdr)
    )
    if width <= 0 or height <= 0:
        raise PNGVariantDecodeError("png_dimensions_invalid", "PNG dimensions must be positive")
    if bit_depth != 8:
        raise PNGVariantDecodeError("png_bit_depth_unsupported", "only 8-bit PNG is supported")
    if color_type not in CHANNELS_BY_COLOR_TYPE:
        raise PNGVariantDecodeError(
            "png_color_type_unsupported",
            "Stage 0 variant decoder supports color types 0, 2, 3, and 6 only",
        )
    if compression != 0 or filter_method != 0:
        raise PNGVariantDecodeError(
            "png_method_unsupported",
            "only PNG compression method 0 and filter method 0 are supported",
        )
    if interlace != 0:
        raise PNGVariantDecodeError(
            "png_interlace_unsupported",
            "Adam7 interlaced PNG is outside this Stage 0 variant decoder",
        )

    plte = _parse_plte(chunks)
    trns = _parse_trns(chunks)
    if color_type == 3 and not plte:
        raise PNGVariantDecodeError("png_plte_missing", "indexed-color PNG requires PLTE")
    if trns and color_type != 3:
        raise PNGVariantDecodeError(
            "png_trns_unsupported",
            "Stage 0 variant decoder only supports tRNS for indexed-color PNG",
        )
    if trns and len(trns) > len(plte):
        raise PNGVariantDecodeError("png_trns_invalid", "indexed-color tRNS exceeds PLTE length")

    idat = b"".join(chunk["payload"] for chunk in chunks if chunk["type"] == "IDAT")
    if not idat:
        raise PNGVariantDecodeError("png_idat_missing", "PNG IDAT chunk is required")
    if not any(chunk["type"] == "IEND" for chunk in chunks):
        raise PNGVariantDecodeError("png_iend_missing", "PNG IEND chunk is required")
    channels = CHANNELS_BY_COLOR_TYPE[color_type]
    stride = width * channels
    expected_length = (stride + 1) * height
    try:
        raw = bounded_decompress(idat, expected_length)
    except PNGChunkError as exc:
        raise PNGVariantDecodeError("png_idat_decompression_failed", exc.message) from exc

    if len(raw) != expected_length:
        raise PNGVariantDecodeError(
            "png_scanline_length_mismatch",
            "decoded scanline length does not match IHDR dimensions",
        )

    rows = []
    filter_types_seen = []
    offset = 0
    previous = None
    for _y in range(height):
        filter_type = raw[offset]
        offset += 1
        if filter_type > 4:
            raise PNGVariantDecodeError(
                "png_filter_type_unsupported",
                "PNG filter type must be in 0..4 for filter method 0",
            )
        row = raw[offset : offset + stride]
        offset += stride
        unfiltered = _unfilter_row(row, previous, channels, filter_type)
        rows.append(unfiltered)
        previous = unfiltered
        if filter_type not in filter_types_seen:
            filter_types_seen.append(filter_type)

    pixels = _rows_to_rgba_pixels(
        rows,
        width=width,
        color_type=color_type,
        plte=plte,
        trns=trns,
    )
    return {
        "width": width,
        "height": height,
        "bit_depth": bit_depth,
        "color_type": color_type,
        "interlace_method": interlace,
        "pixels": pixels,
        "pixel_count": len(pixels),
        "filter_types_seen": filter_types_seen,
        "chunks": [chunk["type"] for chunk in chunks],
        "has_plte": bool(plte),
        "has_trns": bool(trns),
    }


def export_png_variant_suite_with_sidecars(grid: dict, slip_profile: dict) -> list[dict]:
    width, height = grid["grid_size"]
    source_pixels = render_grid_rgba_pixels(grid)
    exports = []
    for spec in VARIANT_SPECS:
        png_bytes = _encode_png_variant(
            width,
            height,
            source_pixels,
            color_type=spec["color_type"],
            filter_types=spec["filter_types"],
        )
        decoded = decode_png_variant(png_bytes)
        asset = _asset_from_png_bytes(
            png_bytes,
            asset_id=f"{slip_profile['profile_id']}_{spec['variant_id']}.png",
            uri=(
                "generated://workshop/png-variant/"
                f"{slip_profile['profile_id']}_{spec['variant_id']}.png"
            ),
        )
        sidecar = build_sidecar_for_grid(grid, slip_profile, asset)
        sidecar["sidecar_id"] = f"{grid['grid_id']}_{spec['variant_id']}_sidecar"
        sidecar["variant_binding"] = {
            "variant_id": spec["variant_id"],
            "color_type": spec["color_type"],
            "bit_depth": 8,
            "interlace_method": 0,
            "filter_types": list(spec["filter_types"]),
            "source_render_pixel_hash": _hash_pixels(source_pixels),
            "visual_carrier_pixel_hash": _hash_pixels(decoded["pixels"]),
            "description": spec["description"],
        }
        sidecar["limitations"] = [
            "Stage 0 variant decoder supports 8-bit non-interlaced PNG only.",
            "Supported color types are grayscale, truecolor, indexed color, and truecolor with alpha.",
            "Semantic metadata is restored from the Mechagotchi sidecar, not inferred from pixels.",
            "Adam7 interlace, APNG, 16-bit channels, and grayscale-alpha are not claimed.",
        ]
        exports.append(
            {
                "variant_id": spec["variant_id"],
                "png_bytes": png_bytes,
                "png_file_name": f"{slip_profile['profile_id']}_{spec['variant_id']}.png",
                "sidecar_file_name": f"{slip_profile['profile_id']}_{spec['variant_id']}_sidecar.json",
                "asset": asset,
                "sidecar": sidecar,
                "decoded_png": _decoded_summary(decoded),
                "visual_carrier_pixel_hash": _hash_pixels(decoded["pixels"]),
            }
        )
    return exports


def import_png_variant_with_sidecar(png_bytes: bytes, sidecar: dict) -> dict:
    try:
        decoded = decode_png_variant(png_bytes)
    except PNGVariantDecodeError as exc:
        return _failed_import("png", exc.family, exc.message)

    binding = sidecar.get("asset_binding", {})
    asset = _asset_from_png_bytes(
        png_bytes,
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

    variant_validation = _validate_variant_binding(sidecar, decoded)
    if not variant_validation["ok"]:
        return {
            "ok": False,
            "asset": asset,
            "decoded_png": _decoded_summary(decoded),
            "validation": validation,
            "errors": variant_validation["errors"],
            "error_families": variant_validation["error_families"],
        }

    restored = restore_grid_from_sidecar(sidecar, asset)
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


def run_png_variant_sidecar_decoder_lab(
    profile_paths: list[Path], generated_root: Path
) -> dict:
    variant_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        for exported in export_png_variant_suite_with_sidecars(grid, profile):
            imported = import_png_variant_with_sidecar(
                exported["png_bytes"],
                exported["sidecar"],
            )
            restored = imported.get("restored_grid", {})
            grid_validation = validate_grid(restored) if restored else None
            alignment = is_grid_aligned(restored, profile) if restored else None
            variant_results.append(
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
                }
            )

    invalid_probe_results = _invalid_probe_results(variant_results[0])
    success_count = sum(
        1
        for result in variant_results
        if result["import_result"]["ok"]
        and result["restored_grid_validation"]["valid"]
        and result["restored_grid_validation"]["slip_aligned"]
        and result["semantic_fidelity"] == 1.0
        and result["pixel_fidelity"] == 1.0
    )
    invalid_rejected_count = sum(
        1 for result in invalid_probe_results if not result["ok"]
    )
    mean_semantic_fidelity = round(
        sum(result["semantic_fidelity"] for result in variant_results)
        / max(1, len(variant_results)),
        6,
    )
    mean_pixel_fidelity = round(
        sum(result["pixel_fidelity"] for result in variant_results)
        / max(1, len(variant_results)),
        6,
    )
    return {
        "artifact_id": "png_variant_sidecar_decoder_stage0",
        "status": "research_png_variant_sidecar_decoder_no_package_code",
        "date": "2026-05-13",
        "purpose": (
            "Broaden the Stage 0 standard-image proof from static RGBA filter-0 "
            "PNG to an explicit 8-bit non-interlaced PNG variant suite while "
            "keeping Mechagotchi semantics sidecar-bound."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
            "labs/workshop_editor/external_metadata_sidecar.py",
            "labs/workshop_editor/standard_image_sidecar_decoder.py",
            "labs/workshop_editor/png_variant_sidecar_decoder.py",
        ],
        "external_anchors": [
            {
                "source": "W3C PNG specification",
                "url": "https://www.w3.org/TR/png-3/",
                "used_for": "PNG color type, bit depth, filter method, filter type, PLTE, IDAT, CRC, and Adam7 boundary semantics.",
            }
        ],
        "profile_count": len(profile_paths),
        "variant_count_per_profile": len(VARIANT_SPECS),
        "variant_roundtrip_count": len(variant_results),
        "variant_roundtrip_success_count": success_count,
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "metrics": {
            "variant_roundtrip_success_rate": _ratio(success_count, len(variant_results)),
            "mean_semantic_fidelity": mean_semantic_fidelity,
            "mean_pixel_fidelity": mean_pixel_fidelity,
            "invalid_probe_rejection_rate": _ratio(
                invalid_rejected_count,
                len(invalid_probe_results),
            ),
            "supported_color_types": [0, 2, 3, 6],
            "supported_filter_types": [0, 1, 2, 3, 4],
        },
        "variant_specs": deepcopy(VARIANT_SPECS),
        "variant_results": variant_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "png_color_type_0_2_3_6_8bit_decoder",
            "png_filter_types_0_to_4_decoder",
            "png_plte_indexed_color_decoder",
            "png_variant_sidecar_export",
            "png_variant_sidecar_import",
            "png_variant_sidecar_semantic_restore",
        ],
        "blocked_states": [
            "png_adam7_interlace_decoder",
            "apng_decoder",
            "png_color_type_4_grayscale_alpha_decoder",
            "png_bit_depth_1_2_4_16_decoder",
            "full_png_conformance",
            "spritesheet_packed_rotation_trim_decoder",
            "runtime_animation_playback",
            "full_project_format_coverage",
            "embedded_png_metadata_writer",
            "project_file_native_metadata_writer",
            "profile_weighted_evolution",
        ],
        "decision": "prototype_png_variant_sidecar_decoder",
        "next_research_step": (
            "Run held-out long-horizon behavior tests and manual readability "
            "calibration before profile-weighted evolution claims."
        ),
    }


def write_png_variant_sidecar_decoder_artifacts(
    output_dir: Path, report: dict
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "png_variant_sidecar_decoder_stage0.json", _json_report(report))
    for result in report["variant_results"]:
        (output_dir / result["png_file_name"]).write_bytes(
            bytes.fromhex(result["png_bytes_hex"])
        )
        _write_json(output_dir / result["sidecar_file_name"], result["sidecar"])
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "png_variant_sidecar_decoder_data.js").write_text(
        "window.MECHAGOTCHI_PNG_VARIANT_SIDECAR_DECODER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _encode_png_variant(
    width: int,
    height: int,
    pixels: list[tuple[int, int, int, int]],
    *,
    color_type: int,
    filter_types: list[int],
    include_plte: bool = True,
    interlace: int = 0,
) -> bytes:
    if color_type not in CHANNELS_BY_COLOR_TYPE:
        raise ValueError(f"unsupported color type for Stage 0 encoder: {color_type}")
    if width <= 0 or height <= 0:
        raise ValueError("PNG dimensions must be positive")
    if len(pixels) != width * height:
        raise ValueError("pixel count does not match PNG dimensions")
    if not filter_types:
        raise ValueError("at least one filter type is required")
    if any(filter_type < 0 or filter_type > 4 for filter_type in filter_types):
        raise ValueError("filter types must be in 0..4")

    rows, plte, trns = _variant_rows(width, height, pixels, color_type)
    channels = CHANNELS_BY_COLOR_TYPE[color_type]
    scanlines = bytearray()
    previous = None
    for y, row in enumerate(rows):
        filter_type = filter_types[y % len(filter_types)]
        scanlines.append(filter_type)
        scanlines.extend(_filter_row(row, previous, channels, filter_type))
        previous = row

    ihdr = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, interlace)
    chunks = [PNG_SIGNATURE, _png_chunk(b"IHDR", ihdr)]
    if color_type == 3 and include_plte:
        chunks.append(_png_chunk(b"PLTE", b"".join(bytes(rgb) for rgb in plte)))
        if any(alpha < 255 for alpha in trns):
            chunks.append(_png_chunk(b"tRNS", bytes(trns)))
    chunks.extend(
        [
            _png_chunk(b"IDAT", zlib.compress(bytes(scanlines))),
            _png_chunk(b"IEND", b""),
        ]
    )
    return b"".join(chunks)


def _variant_rows(
    width: int,
    height: int,
    pixels: list[tuple[int, int, int, int]],
    color_type: int,
) -> tuple[list[bytes], list[tuple[int, int, int]], list[int]]:
    rows = []
    plte = []
    trns = []
    index_by_color = {}
    if color_type == 3:
        for pixel in pixels:
            key = tuple(pixel)
            if key not in index_by_color:
                if len(index_by_color) >= 256:
                    raise ValueError("indexed-color PNG cannot encode more than 256 colors")
                index_by_color[key] = len(index_by_color)
                plte.append(tuple(pixel[:3]))
                trns.append(pixel[3])

    for y in range(height):
        row = bytearray()
        for pixel in pixels[y * width : (y + 1) * width]:
            _validate_rgba_pixel(pixel)
            if color_type == 0:
                row.append(_luminance(pixel))
            elif color_type == 2:
                row.extend(pixel[:3])
            elif color_type == 3:
                row.append(index_by_color[tuple(pixel)])
            elif color_type == 6:
                row.extend(pixel)
        rows.append(bytes(row))
    return rows, plte, trns


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
            raise PNGVariantDecodeError("png_filter_type_unsupported", "filter type must be in 0..4")
        reconstructed.append((value + prediction) & 0xFF)
    return bytes(reconstructed)


def _rows_to_rgba_pixels(
    rows: list[bytes],
    *,
    width: int,
    color_type: int,
    plte: list[tuple[int, int, int]],
    trns: bytes,
) -> list[tuple[int, int, int, int]]:
    pixels = []
    for row in rows:
        if color_type == 0:
            for gray in row:
                pixels.append((gray, gray, gray, 255))
        elif color_type == 2:
            for offset in range(0, len(row), 3):
                r, g, b = row[offset : offset + 3]
                pixels.append((r, g, b, 255))
        elif color_type == 3:
            for index in row:
                if index >= len(plte):
                    raise PNGVariantDecodeError(
                        "png_palette_index_out_of_range",
                        "indexed-color pixel references a missing PLTE entry",
                    )
                r, g, b = plte[index]
                alpha = trns[index] if index < len(trns) else 255
                pixels.append((r, g, b, alpha))
        elif color_type == 6:
            for offset in range(0, len(row), 4):
                pixels.append(tuple(row[offset : offset + 4]))
    if len(pixels) != width * len(rows):
        raise PNGVariantDecodeError("png_pixel_count_mismatch", "decoded pixel count is invalid")
    return pixels


def _parse_plte(chunks: list[dict]) -> list[tuple[int, int, int]]:
    plte_payloads = [chunk["payload"] for chunk in chunks if chunk["type"] == "PLTE"]
    if not plte_payloads:
        return []
    if len(plte_payloads) > 1:
        raise PNGVariantDecodeError("png_plte_duplicate", "PNG must not contain multiple PLTE chunks")
    payload = plte_payloads[0]
    if len(payload) == 0 or len(payload) % 3 != 0 or len(payload) > 768:
        raise PNGVariantDecodeError("png_plte_invalid", "PLTE length must be 1..256 RGB entries")
    return [
        tuple(payload[offset : offset + 3])
        for offset in range(0, len(payload), 3)
    ]


def _parse_trns(chunks: list[dict]) -> bytes:
    trns_payloads = [chunk["payload"] for chunk in chunks if chunk["type"] == "tRNS"]
    if not trns_payloads:
        return b""
    if len(trns_payloads) > 1:
        raise PNGVariantDecodeError("png_trns_duplicate", "PNG must not contain multiple tRNS chunks")
    return trns_payloads[0]


def _read_png_chunks(png_bytes: bytes) -> list[dict]:
    try:
        return read_png_chunks(png_bytes)
    except PNGChunkError as exc:
        raise PNGVariantDecodeError(exc.family, exc.message) from exc


def _png_chunk(chunk_type: bytes, payload: bytes) -> bytes:
    crc = binascii.crc32(payload, binascii.crc32(chunk_type)) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + chunk_type + payload + struct.pack(">I", crc)


def _asset_from_png_bytes(png_bytes: bytes, *, asset_id: str, uri: str) -> dict:
    decoded = decode_png_variant(png_bytes)
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


def _validate_variant_binding(sidecar: dict, decoded: dict) -> dict:
    errors = []
    binding = sidecar.get("variant_binding", {})
    if binding:
        if binding.get("color_type") != decoded["color_type"]:
            errors.append(_error("variant_binding.color_type", "png_variant_color_type_mismatch"))
        if binding.get("bit_depth") != decoded["bit_depth"]:
            errors.append(_error("variant_binding.bit_depth", "png_variant_bit_depth_mismatch"))
        if binding.get("interlace_method") != decoded["interlace_method"]:
            errors.append(_error("variant_binding.interlace_method", "png_variant_interlace_mismatch"))
        expected_filters = sorted(set(binding.get("filter_types", [])))
        actual_filters = sorted(set(decoded["filter_types_seen"]))
        if expected_filters != actual_filters:
            errors.append(_error("variant_binding.filter_types", "png_variant_filter_mismatch"))
        expected_hash = binding.get("visual_carrier_pixel_hash")
        if expected_hash != _hash_pixels(decoded["pixels"]):
            errors.append(_error("variant_binding.visual_carrier_pixel_hash", "png_variant_pixel_hash_mismatch"))
    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "error_families": sorted({error["family"] for error in errors}),
    }


def _invalid_probe_results(reference_result: dict) -> list[dict]:
    sidecar = reference_result["sidecar"]
    width = reference_result["asset"]["width"]
    height = reference_result["asset"]["height"]
    pixels = decode_png_variant(bytes.fromhex(reference_result["png_bytes_hex"]))["pixels"]
    interlaced_png = _encode_png_variant(
        width,
        height,
        pixels,
        color_type=6,
        filter_types=[0],
        interlace=1,
    )
    indexed_without_plte = _encode_png_variant(
        width,
        height,
        pixels,
        color_type=3,
        filter_types=[0],
        include_plte=False,
    )
    wrong_variant_sidecar = deepcopy(sidecar)
    wrong_variant_sidecar["variant_binding"]["visual_carrier_pixel_hash"] = "sha256:not-the-visual-carrier"
    return [
        _compact_import_result(import_png_variant_with_sidecar(interlaced_png, sidecar)),
        _compact_import_result(import_png_variant_with_sidecar(indexed_without_plte, sidecar)),
        _compact_import_result(
            import_png_variant_with_sidecar(
                bytes.fromhex(reference_result["png_bytes_hex"]),
                wrong_variant_sidecar,
            )
        ),
    ]


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
        "filter_types_seen": decoded["filter_types_seen"],
        "chunks": decoded["chunks"],
        "has_plte": decoded["has_plte"],
        "has_trns": decoded["has_trns"],
    }


def _validate_rgba_pixel(pixel: tuple[int, int, int, int]) -> None:
    if len(pixel) != 4 or any(channel < 0 or channel > 255 for channel in pixel):
        raise ValueError("RGBA pixel channels must be in [0, 255]")


def _luminance(pixel: tuple[int, int, int, int]) -> int:
    return (pixel[0] * 299 + pixel[1] * 587 + pixel[2] * 114) // 1000


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
    return str(path).replace("\\", "/")


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def _json_report(report: dict) -> dict:
    payload = deepcopy(report)
    for result in payload["variant_results"]:
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
                "variant_count_per_profile",
                "variant_roundtrip_count",
                "variant_roundtrip_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "variant_summaries": [
            {
                "profile_id": result["profile_id"],
                "variant_id": result["variant_id"],
                "asset": result["asset"],
                "decoded_png": result["decoded_png"],
                "semantic_fidelity": result["semantic_fidelity"],
                "pixel_fidelity": result["pixel_fidelity"],
            }
            for result in json_report["variant_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# PNG Variant Sidecar Decoder Stage 0\n\n"
        "8-bit non-interlaced PNG variant import/export proof bound to "
        "Mechagotchi JSON sidecars.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Variants per profile: {report['variant_count_per_profile']}\n"
        f"- Variant round-trip successes: {report['variant_roundtrip_success_count']}"
        f"/{report['variant_roundtrip_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- Mean semantic fidelity: {metrics['mean_semantic_fidelity']}\n"
        f"- Mean pixel fidelity: {metrics['mean_pixel_fidelity']}\n"
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
        default=Path("data/workshop_editor/png_variant_sidecar_decoder_stage0"),
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
    report = run_png_variant_sidecar_decoder_lab(profile_paths, args.generated_root)
    write_png_variant_sidecar_decoder_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_PNG_VARIANT_SIDECAR_DECODER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(_json_report(report), indent=2))


if __name__ == "__main__":
    main()
