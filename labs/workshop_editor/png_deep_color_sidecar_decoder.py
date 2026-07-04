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


REPORT_PATH = ROOT / "data/workshop_editor/png_deep_color_sidecar_decoder_stage0.json"
DATA_PATH = ROOT / "data/workshop_editor/png_deep_color_sidecar_decoder_data.js"

CHANNELS_BY_COLOR_TYPE = {
    0: 1,
    2: 3,
    3: 1,
    4: 2,
    6: 4,
}

ALLOWED_BIT_DEPTHS_BY_COLOR_TYPE = {
    0: {1, 2, 4, 8, 16},
    2: {8, 16},
    3: {1, 2, 4, 8},
    4: {8, 16},
    6: {8, 16},
}

DEEP_COLOR_VARIANT_SPECS = [
    {
        "variant_id": "grayscale_1bit",
        "color_type": 0,
        "bit_depth": 1,
        "filter_types": [0, 1, 2, 3, 4],
        "description": "PNG color type 0, 1-bit packed greyscale samples.",
    },
    {
        "variant_id": "grayscale_2bit",
        "color_type": 0,
        "bit_depth": 2,
        "filter_types": [0, 1, 2, 3, 4],
        "description": "PNG color type 0, 2-bit packed greyscale samples.",
    },
    {
        "variant_id": "grayscale_4bit",
        "color_type": 0,
        "bit_depth": 4,
        "filter_types": [0, 1, 2, 3, 4],
        "description": "PNG color type 0, 4-bit packed greyscale samples.",
    },
    {
        "variant_id": "grayscale_16bit",
        "color_type": 0,
        "bit_depth": 16,
        "filter_types": [0, 1, 2, 3, 4],
        "description": "PNG color type 0, 16-bit greyscale samples.",
    },
    {
        "variant_id": "indexed_1bit",
        "color_type": 3,
        "bit_depth": 1,
        "filter_types": [0, 1, 2, 3, 4],
        "description": "PNG color type 3, 1-bit packed palette indices with PLTE.",
    },
    {
        "variant_id": "indexed_2bit",
        "color_type": 3,
        "bit_depth": 2,
        "filter_types": [0, 1, 2, 3, 4],
        "description": "PNG color type 3, 2-bit packed palette indices with PLTE.",
    },
    {
        "variant_id": "indexed_4bit",
        "color_type": 3,
        "bit_depth": 4,
        "filter_types": [0, 1, 2, 3, 4],
        "description": "PNG color type 3, 4-bit packed palette indices with PLTE.",
    },
    {
        "variant_id": "truecolor_16bit",
        "color_type": 2,
        "bit_depth": 16,
        "filter_types": [0, 1, 2, 3, 4],
        "description": "PNG color type 2, 16-bit RGB truecolor samples.",
    },
    {
        "variant_id": "grayscale_alpha_8bit",
        "color_type": 4,
        "bit_depth": 8,
        "filter_types": [0, 1, 2, 3, 4],
        "description": "PNG color type 4, 8-bit greyscale plus alpha samples.",
    },
    {
        "variant_id": "grayscale_alpha_16bit",
        "color_type": 4,
        "bit_depth": 16,
        "filter_types": [0, 1, 2, 3, 4],
        "description": "PNG color type 4, 16-bit greyscale plus alpha samples.",
    },
    {
        "variant_id": "rgba_16bit",
        "color_type": 6,
        "bit_depth": 16,
        "filter_types": [0, 1, 2, 3, 4],
        "description": "PNG color type 6, 16-bit RGBA truecolor with alpha samples.",
    },
]


class PNGDeepColorDecodeError(ValueError):
    def __init__(self, family: str, message: str):
        super().__init__(message)
        self.family = family
        self.message = message


def decode_png_deep_color(png_bytes: bytes) -> dict:
    chunks = _read_png_chunks(png_bytes)
    if not chunks or chunks[0]["type"] != "IHDR":
        raise PNGDeepColorDecodeError("png_ihdr_missing", "PNG IHDR chunk must be first")

    ihdr = chunks[0]["payload"]
    if len(ihdr) != 13:
        raise PNGDeepColorDecodeError("png_ihdr_invalid", "PNG IHDR chunk length must be 13")
    width, height, bit_depth, color_type, compression, filter_method, interlace = (
        struct.unpack(">IIBBBBB", ihdr)
    )
    if width <= 0 or height <= 0:
        raise PNGDeepColorDecodeError("png_dimensions_invalid", "PNG dimensions must be positive")
    if color_type not in ALLOWED_BIT_DEPTHS_BY_COLOR_TYPE:
        raise PNGDeepColorDecodeError(
            "png_color_type_unsupported",
            "Stage 0 deep-color decoder supports color types 0, 2, 3, 4, and 6 only",
        )
    if bit_depth not in ALLOWED_BIT_DEPTHS_BY_COLOR_TYPE[color_type]:
        raise PNGDeepColorDecodeError(
            "png_bit_depth_color_type_invalid",
            "PNG bit depth is not allowed for this color type",
        )
    if compression != 0 or filter_method != 0:
        raise PNGDeepColorDecodeError(
            "png_method_unsupported",
            "only PNG compression method 0 and filter method 0 are supported",
        )
    if interlace != 0:
        raise PNGDeepColorDecodeError(
            "png_interlace_unsupported",
            "deep-color Stage 0 proof is non-interlaced; Adam7 is covered by a separate lab",
        )

    plte = _parse_plte(chunks)
    trns = _parse_trns(chunks)
    if color_type == 3 and not plte:
        raise PNGDeepColorDecodeError("png_plte_missing", "indexed-color PNG requires PLTE")
    if color_type == 3 and len(plte) > 2**bit_depth:
        raise PNGDeepColorDecodeError(
            "png_plte_bit_depth_mismatch",
            "PLTE entry count exceeds the range representable by the bit depth",
        )
    if color_type in {0, 4} and plte:
        raise PNGDeepColorDecodeError(
            "png_plte_forbidden",
            "PLTE shall not appear for greyscale or greyscale-alpha PNG",
        )
    if trns and color_type != 3:
        raise PNGDeepColorDecodeError(
            "png_trns_unsupported",
            "Stage 0 deep-color decoder only supports tRNS for indexed-color PNG",
        )
    if trns and len(trns) > len(plte):
        raise PNGDeepColorDecodeError("png_trns_invalid", "indexed-color tRNS exceeds PLTE length")

    idat = b"".join(chunk["payload"] for chunk in chunks if chunk["type"] == "IDAT")
    if not idat:
        raise PNGDeepColorDecodeError("png_idat_missing", "PNG IDAT chunk is required")
    if not any(chunk["type"] == "IEND" for chunk in chunks):
        raise PNGDeepColorDecodeError("png_iend_missing", "PNG IEND chunk is required")
    scanline_byte_length = _scanline_byte_length(width, color_type, bit_depth)
    expected_length = (scanline_byte_length + 1) * height
    try:
        raw = bounded_decompress(idat, expected_length)
    except PNGChunkError as exc:
        raise PNGDeepColorDecodeError("png_idat_decompression_failed", exc.message) from exc

    if len(raw) != expected_length:
        raise PNGDeepColorDecodeError(
            "png_scanline_length_mismatch",
            "decoded scanline length does not match IHDR dimensions and bit depth",
        )

    rows = []
    filter_types_seen = []
    offset = 0
    previous = None
    filter_bpp = _filter_bpp(color_type, bit_depth)
    for _y in range(height):
        filter_type = raw[offset]
        offset += 1
        if filter_type > 4:
            raise PNGDeepColorDecodeError(
                "png_filter_type_unsupported",
                "PNG filter type must be in 0..4 for filter method 0",
            )
        row = raw[offset : offset + scanline_byte_length]
        offset += scanline_byte_length
        unfiltered = _unfilter_row(row, previous, filter_bpp, filter_type)
        rows.append(unfiltered)
        previous = unfiltered
        if filter_type not in filter_types_seen:
            filter_types_seen.append(filter_type)

    pixels = _rows_to_rgba_pixels(
        rows,
        width=width,
        color_type=color_type,
        bit_depth=bit_depth,
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
        "scanline_byte_length": scanline_byte_length,
        "filter_bpp": filter_bpp,
        "filter_types_seen": filter_types_seen,
        "chunks": [chunk["type"] for chunk in chunks],
        "has_plte": bool(plte),
        "has_trns": bool(trns),
    }


def export_png_deep_color_suite_with_sidecars(grid: dict, slip_profile: dict) -> list[dict]:
    width, height = grid["grid_size"]
    source_pixels = render_grid_rgba_pixels(grid)
    source_hash = _hash_pixels(source_pixels)
    exports = []
    for spec in DEEP_COLOR_VARIANT_SPECS:
        png_bytes = _encode_png_deep_color(width, height, source_pixels, spec)
        decoded = decode_png_deep_color(png_bytes)
        visual_hash = _hash_pixels(decoded["pixels"])
        delta_count = _pixel_delta_count(source_pixels, decoded["pixels"])
        asset = _asset_from_png_bytes(
            png_bytes,
            asset_id=f"{slip_profile['profile_id']}_{spec['variant_id']}.png",
            uri=(
                "generated://workshop/png-deep-color/"
                f"{slip_profile['profile_id']}_{spec['variant_id']}.png"
            ),
        )
        sidecar = build_sidecar_for_grid(grid, slip_profile, asset)
        sidecar["sidecar_id"] = f"{grid['grid_id']}_{spec['variant_id']}_sidecar"
        sidecar["deep_color_binding"] = {
            "variant_id": spec["variant_id"],
            "color_type": spec["color_type"],
            "bit_depth": spec["bit_depth"],
            "interlace_method": 0,
            "filter_types": list(spec["filter_types"]),
            "scanline_byte_length": decoded["scanline_byte_length"],
            "filter_bpp": decoded["filter_bpp"],
            "source_render_pixel_hash": source_hash,
            "visual_carrier_pixel_hash": visual_hash,
            "source_visual_delta_count": delta_count,
            "description": spec["description"],
        }
        sidecar["limitations"] = [
            "Stage 0 deep-color decoder supports bounded non-interlaced PNG only.",
            "Supported color types are greyscale, truecolor, indexed color, greyscale-alpha, and truecolor-alpha.",
            "Low-bit and greyscale carriers can be visually quantized; semantic metadata is restored from the Mechagotchi sidecar.",
            "APNG, full PNG conformance, live editor rewrite behavior, and final production carrier selection are not claimed.",
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
                "visual_carrier_pixel_hash": visual_hash,
                "source_visual_delta_count": delta_count,
            }
        )
    return exports


def import_png_deep_color_with_sidecar(png_bytes: bytes, sidecar: dict) -> dict:
    try:
        decoded = decode_png_deep_color(png_bytes)
    except PNGDeepColorDecodeError as exc:
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

    deep_color_validation = _validate_deep_color_binding(sidecar, decoded)
    if not deep_color_validation["ok"]:
        return {
            "ok": False,
            "asset": asset,
            "decoded_png": _decoded_summary(decoded),
            "validation": validation,
            "errors": deep_color_validation["errors"],
            "error_families": deep_color_validation["error_families"],
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


def run_png_deep_color_sidecar_decoder_lab(
    profile_paths: list[Path], generated_root: Path
) -> dict:
    variant_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        for exported in export_png_deep_color_suite_with_sidecars(grid, profile):
            imported = import_png_deep_color_with_sidecar(
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
                    "source_visual_delta_count": exported["source_visual_delta_count"],
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
        "artifact_id": "png_deep_color_sidecar_decoder_stage0",
        "status": "research_png_deep_color_sidecar_decoder_no_package_code",
        "date": "2026-05-14",
        "purpose": (
            "Close the bounded Stage 0 PNG low-bit, 16-bit sample, and "
            "greyscale-alpha sidecar decoder gap without claiming APNG, live "
            "editor, package runtime, or full PNG conformance."
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
            "labs/workshop_editor/png_adam7_interlace_decoder.py",
            "labs/workshop_editor/png_deep_color_sidecar_decoder.py",
        ],
        "external_anchors": [
            {
                "source": "W3C PNG specification",
                "url": "https://www.w3.org/TR/png-3/",
                "used_for": "PNG color type and bit depth matrix, packed scanline sizing, filter method 0, PLTE, IDAT, and CRC semantics.",
            }
        ],
        "profile_count": len(profile_paths),
        "variant_count_per_profile": len(DEEP_COLOR_VARIANT_SPECS),
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
            "supported_color_types": _sorted_unique(
                spec["color_type"] for spec in DEEP_COLOR_VARIANT_SPECS
            ),
            "supported_bit_depths": _sorted_unique(
                spec["bit_depth"] for spec in DEEP_COLOR_VARIANT_SPECS
            ),
            "supported_filter_types": [0, 1, 2, 3, 4],
            "quantized_visual_variant_count": sum(
                1
                for result in variant_results
                if result["source_visual_delta_count"] > 0
            ),
        },
        "variant_specs": deepcopy(DEEP_COLOR_VARIANT_SPECS),
        "variant_results": variant_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "png_grayscale_low_bit_depth_decoder",
            "png_indexed_low_bit_depth_decoder",
            "png_16bit_sample_decoder",
            "png_color_type_4_grayscale_alpha_decoder",
            "png_deep_color_sidecar_export",
            "png_deep_color_sidecar_import",
            "png_deep_color_sidecar_semantic_restore",
            "png_deep_color_invalid_probe_rejection",
        ],
        "blocked_states": [
            "apng_decoder",
            "full_png_conformance",
            "adam7_deep_color_cross_product_decoder",
            "live_external_editor_rewrite_validation",
            "private_chunk_editor_preservation_matrix",
            "final_png_production_carrier_selection",
            "package_runtime_integration",
            "manual_readability_calibration",
            "profile_weighted_evolution",
        ],
        "decision": "prototype_png_deep_color_sidecar_decoder",
        "next_research_step": (
            "Move remaining PNG work to APNG/full-conformance fixtures or live "
            "external editor rewrite validation before final carrier selection."
        ),
    }


def write_png_deep_color_sidecar_decoder_artifacts(
    output_dir: Path, report: dict
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "png_deep_color_sidecar_decoder_stage0.json", _json_report(report))
    for result in report["variant_results"]:
        (output_dir / result["png_file_name"]).write_bytes(
            bytes.fromhex(result["png_bytes_hex"])
        )
        _write_json(output_dir / result["sidecar_file_name"], result["sidecar"])
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "png_deep_color_sidecar_decoder_data.js").write_text(
        "window.MECHAGOTCHI_PNG_DEEP_COLOR_SIDECAR_DECODER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _encode_png_deep_color(
    width: int,
    height: int,
    pixels: list[tuple[int, int, int, int]],
    spec: dict,
) -> bytes:
    color_type = spec["color_type"]
    bit_depth = spec["bit_depth"]
    filter_types = spec["filter_types"]
    if color_type not in ALLOWED_BIT_DEPTHS_BY_COLOR_TYPE:
        raise ValueError(f"unsupported color type for Stage 0 encoder: {color_type}")
    if bit_depth not in ALLOWED_BIT_DEPTHS_BY_COLOR_TYPE[color_type]:
        raise ValueError("bit depth is not allowed for this color type")
    if width <= 0 or height <= 0:
        raise ValueError("PNG dimensions must be positive")
    if len(pixels) != width * height:
        raise ValueError("pixel count does not match PNG dimensions")
    if not filter_types:
        raise ValueError("at least one filter type is required")
    if any(filter_type < 0 or filter_type > 4 for filter_type in filter_types):
        raise ValueError("filter types must be in 0..4")

    rows, plte, trns = _variant_rows(width, height, pixels, color_type, bit_depth)
    filter_bpp = _filter_bpp(color_type, bit_depth)
    scanlines = bytearray()
    previous = None
    for y, row in enumerate(rows):
        filter_type = filter_types[y % len(filter_types)]
        scanlines.append(filter_type)
        scanlines.extend(_filter_row(row, previous, filter_bpp, filter_type))
        previous = row

    ihdr = struct.pack(">IIBBBBB", width, height, bit_depth, color_type, 0, 0, 0)
    chunks = [PNG_SIGNATURE, _png_chunk(b"IHDR", ihdr)]
    if color_type == 3:
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
    bit_depth: int,
) -> tuple[list[bytes], list[tuple[int, int, int]], list[int]]:
    rows = []
    plte = _ramp_palette(bit_depth) if color_type == 3 else []
    trns = [255 for _ in plte]

    for y in range(height):
        row = bytearray()
        packed_samples = []
        for pixel in pixels[y * width : (y + 1) * width]:
            _validate_rgba_pixel(pixel)
            if color_type == 0:
                gray = _luminance(pixel)
                if bit_depth < 8:
                    packed_samples.append(_byte_to_sample(gray, bit_depth))
                elif bit_depth == 8:
                    row.append(gray)
                else:
                    row.extend(_uint16(gray * 257))
            elif color_type == 2:
                if bit_depth == 8:
                    row.extend(pixel[:3])
                else:
                    row.extend(_uint16(pixel[0] * 257))
                    row.extend(_uint16(pixel[1] * 257))
                    row.extend(_uint16(pixel[2] * 257))
            elif color_type == 3:
                index = _byte_to_sample(_luminance(pixel), bit_depth)
                packed_samples.append(index)
            elif color_type == 4:
                gray = _luminance(pixel)
                if bit_depth == 8:
                    row.extend([gray, pixel[3]])
                else:
                    row.extend(_uint16(gray * 257))
                    row.extend(_uint16(pixel[3] * 257))
            elif color_type == 6:
                if bit_depth == 8:
                    row.extend(pixel)
                else:
                    for channel in pixel:
                        row.extend(_uint16(channel * 257))
            else:
                raise ValueError(f"unsupported color type: {color_type}")
        if bit_depth < 8:
            row = bytearray(_pack_low_bit_samples(packed_samples, bit_depth))
        rows.append(bytes(row))
    return rows, plte, trns


def _rows_to_rgba_pixels(
    rows: list[bytes],
    *,
    width: int,
    color_type: int,
    bit_depth: int,
    plte: list[tuple[int, int, int]],
    trns: bytes,
) -> list[tuple[int, int, int, int]]:
    pixels = []
    for row in rows:
        if color_type == 0:
            if bit_depth < 8:
                for sample in _unpack_low_bit_samples(row, bit_depth, width):
                    gray = _sample_to_byte(sample, bit_depth)
                    pixels.append((gray, gray, gray, 255))
            elif bit_depth == 8:
                for gray in row:
                    pixels.append((gray, gray, gray, 255))
            else:
                for offset in range(0, len(row), 2):
                    gray = _sample16_to_byte(row[offset : offset + 2])
                    pixels.append((gray, gray, gray, 255))
        elif color_type == 2:
            sample_bytes = bit_depth // 8
            pixel_bytes = 3 * sample_bytes
            for offset in range(0, len(row), pixel_bytes):
                r = _sample_to_rgba_byte(row[offset : offset + sample_bytes], bit_depth)
                g = _sample_to_rgba_byte(row[offset + sample_bytes : offset + 2 * sample_bytes], bit_depth)
                b = _sample_to_rgba_byte(row[offset + 2 * sample_bytes : offset + 3 * sample_bytes], bit_depth)
                pixels.append((r, g, b, 255))
        elif color_type == 3:
            for index in _unpack_low_bit_samples(row, bit_depth, width):
                if index >= len(plte):
                    raise PNGDeepColorDecodeError(
                        "png_palette_index_out_of_range",
                        "indexed-color pixel references a missing PLTE entry",
                    )
                r, g, b = plte[index]
                alpha = trns[index] if index < len(trns) else 255
                pixels.append((r, g, b, alpha))
        elif color_type == 4:
            sample_bytes = bit_depth // 8
            pixel_bytes = 2 * sample_bytes
            for offset in range(0, len(row), pixel_bytes):
                gray = _sample_to_rgba_byte(row[offset : offset + sample_bytes], bit_depth)
                alpha = _sample_to_rgba_byte(row[offset + sample_bytes : offset + 2 * sample_bytes], bit_depth)
                pixels.append((gray, gray, gray, alpha))
        elif color_type == 6:
            sample_bytes = bit_depth // 8
            pixel_bytes = 4 * sample_bytes
            for offset in range(0, len(row), pixel_bytes):
                r = _sample_to_rgba_byte(row[offset : offset + sample_bytes], bit_depth)
                g = _sample_to_rgba_byte(row[offset + sample_bytes : offset + 2 * sample_bytes], bit_depth)
                b = _sample_to_rgba_byte(row[offset + 2 * sample_bytes : offset + 3 * sample_bytes], bit_depth)
                a = _sample_to_rgba_byte(row[offset + 3 * sample_bytes : offset + 4 * sample_bytes], bit_depth)
                pixels.append((r, g, b, a))
    if len(pixels) != width * len(rows):
        raise PNGDeepColorDecodeError("png_pixel_count_mismatch", "decoded pixel count is invalid")
    return pixels


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
            raise PNGDeepColorDecodeError("png_filter_type_unsupported", "filter type must be in 0..4")
        reconstructed.append((value + prediction) & 0xFF)
    return bytes(reconstructed)


def _parse_plte(chunks: list[dict]) -> list[tuple[int, int, int]]:
    plte_payloads = [chunk["payload"] for chunk in chunks if chunk["type"] == "PLTE"]
    if not plte_payloads:
        return []
    if len(plte_payloads) > 1:
        raise PNGDeepColorDecodeError("png_plte_duplicate", "PNG must not contain multiple PLTE chunks")
    payload = plte_payloads[0]
    if len(payload) == 0 or len(payload) % 3 != 0 or len(payload) > 768:
        raise PNGDeepColorDecodeError("png_plte_invalid", "PLTE length must be 1..256 RGB entries")
    return [
        tuple(payload[offset : offset + 3])
        for offset in range(0, len(payload), 3)
    ]


def _parse_trns(chunks: list[dict]) -> bytes:
    trns_payloads = [chunk["payload"] for chunk in chunks if chunk["type"] == "tRNS"]
    if not trns_payloads:
        return b""
    if len(trns_payloads) > 1:
        raise PNGDeepColorDecodeError("png_trns_duplicate", "PNG must not contain multiple tRNS chunks")
    return trns_payloads[0]


def _read_png_chunks(png_bytes: bytes) -> list[dict]:
    try:
        return read_png_chunks(png_bytes)
    except PNGChunkError as exc:
        raise PNGDeepColorDecodeError(exc.family, exc.message) from exc


def _png_chunk(chunk_type: bytes, payload: bytes) -> bytes:
    crc = binascii.crc32(payload, binascii.crc32(chunk_type)) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + chunk_type + payload + struct.pack(">I", crc)


def _asset_from_png_bytes(png_bytes: bytes, *, asset_id: str, uri: str) -> dict:
    decoded = decode_png_deep_color(png_bytes)
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


def _validate_deep_color_binding(sidecar: dict, decoded: dict) -> dict:
    errors = []
    binding = sidecar.get("deep_color_binding", {})
    if not binding:
        errors.append(_error("deep_color_binding", "png_deep_color_binding_missing"))
    else:
        if binding.get("color_type") != decoded["color_type"]:
            errors.append(_error("deep_color_binding.color_type", "png_deep_color_color_type_mismatch"))
        if binding.get("bit_depth") != decoded["bit_depth"]:
            errors.append(_error("deep_color_binding.bit_depth", "png_deep_color_bit_depth_mismatch"))
        if binding.get("interlace_method") != decoded["interlace_method"]:
            errors.append(_error("deep_color_binding.interlace_method", "png_deep_color_interlace_mismatch"))
        if binding.get("scanline_byte_length") != decoded["scanline_byte_length"]:
            errors.append(_error("deep_color_binding.scanline_byte_length", "png_deep_color_scanline_mismatch"))
        expected_filters = sorted(set(binding.get("filter_types", [])))
        actual_filters = sorted(set(decoded["filter_types_seen"]))
        if expected_filters != actual_filters:
            errors.append(_error("deep_color_binding.filter_types", "png_deep_color_filter_mismatch"))
        expected_hash = binding.get("visual_carrier_pixel_hash")
        if expected_hash != _hash_pixels(decoded["pixels"]):
            errors.append(_error("deep_color_binding.visual_carrier_pixel_hash", "png_deep_color_pixel_hash_mismatch"))
    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "error_families": sorted({error["family"] for error in errors}),
    }


def _invalid_probe_results(reference_result: dict) -> list[dict]:
    sidecar = reference_result["sidecar"]
    png_bytes = bytes.fromhex(reference_result["png_bytes_hex"])

    invalid_bit_depth = _rewrite_ihdr_fields(png_bytes, bit_depth=4, color_type=2)
    truncated_scanline = _rewrite_idat_raw(png_bytes, lambda raw: raw[:-1])
    invalid_filter = _rewrite_idat_raw(png_bytes, lambda raw: bytes([5]) + raw[1:])

    wrong_bit_depth_sidecar = deepcopy(sidecar)
    wrong_bit_depth_sidecar["deep_color_binding"]["bit_depth"] = 16

    wrong_pixel_sidecar = deepcopy(sidecar)
    wrong_pixel_sidecar["deep_color_binding"]["visual_carrier_pixel_hash"] = (
        "sha256:not-the-visual-carrier"
    )

    wrong_asset_sidecar = deepcopy(sidecar)
    wrong_asset_sidecar["asset_binding"]["content_hash"] = "sha256:not-the-png"

    return [
        _compact_import_result(import_png_deep_color_with_sidecar(invalid_bit_depth, sidecar)),
        _compact_import_result(import_png_deep_color_with_sidecar(truncated_scanline, sidecar)),
        _compact_import_result(import_png_deep_color_with_sidecar(invalid_filter, sidecar)),
        _compact_import_result(import_png_deep_color_with_sidecar(png_bytes, wrong_bit_depth_sidecar)),
        _compact_import_result(import_png_deep_color_with_sidecar(png_bytes, wrong_pixel_sidecar)),
        _compact_import_result(import_png_deep_color_with_sidecar(png_bytes, wrong_asset_sidecar)),
    ]


def _rewrite_ihdr_fields(
    png_bytes: bytes,
    *,
    bit_depth: int | None = None,
    color_type: int | None = None,
    interlace: int | None = None,
) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    rewritten = [PNG_SIGNATURE]
    for index, chunk in enumerate(chunks):
        payload = chunk["payload"]
        if index == 0 and chunk["type"] == "IHDR":
            width, height, old_bit_depth, old_color_type, compression, filter_method, old_interlace = (
                struct.unpack(">IIBBBBB", payload)
            )
            payload = struct.pack(
                ">IIBBBBB",
                width,
                height,
                old_bit_depth if bit_depth is None else bit_depth,
                old_color_type if color_type is None else color_type,
                compression,
                filter_method,
                old_interlace if interlace is None else interlace,
            )
        rewritten.append(_png_chunk(chunk["type"].encode("ascii"), payload))
    return b"".join(rewritten)


def _rewrite_idat_raw(png_bytes: bytes, mutate) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    idat = b"".join(chunk["payload"] for chunk in chunks if chunk["type"] == "IDAT")
    raw = zlib.decompress(idat)
    new_idat = zlib.compress(mutate(raw))
    rewritten = [PNG_SIGNATURE]
    wrote_idat = False
    for chunk in chunks:
        if chunk["type"] == "IDAT":
            if not wrote_idat:
                rewritten.append(_png_chunk(b"IDAT", new_idat))
                wrote_idat = True
            continue
        rewritten.append(_png_chunk(chunk["type"].encode("ascii"), chunk["payload"]))
    return b"".join(rewritten)


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
        "scanline_byte_length": decoded["scanline_byte_length"],
        "filter_bpp": decoded["filter_bpp"],
        "filter_types_seen": decoded["filter_types_seen"],
        "chunks": decoded["chunks"],
        "has_plte": decoded["has_plte"],
        "has_trns": decoded["has_trns"],
    }


def _scanline_byte_length(width: int, color_type: int, bit_depth: int) -> int:
    channels = CHANNELS_BY_COLOR_TYPE[color_type]
    return (width * channels * bit_depth + 7) // 8


def _filter_bpp(color_type: int, bit_depth: int) -> int:
    channels = CHANNELS_BY_COLOR_TYPE[color_type]
    return max(1, (channels * bit_depth + 7) // 8)


def _pack_low_bit_samples(samples: list[int], bit_depth: int) -> bytes:
    if bit_depth not in {1, 2, 4}:
        raise ValueError("packed samples require bit depth 1, 2, or 4")
    max_sample = (1 << bit_depth) - 1
    per_byte = 8 // bit_depth
    packed = bytearray()
    current = 0
    sample_index = 0
    for sample in samples:
        if sample < 0 or sample > max_sample:
            raise ValueError("sample exceeds bit depth")
        shift = 8 - bit_depth - (sample_index % per_byte) * bit_depth
        current |= sample << shift
        sample_index += 1
        if sample_index % per_byte == 0:
            packed.append(current)
            current = 0
    if sample_index % per_byte:
        packed.append(current)
    return bytes(packed)


def _unpack_low_bit_samples(row: bytes, bit_depth: int, expected_count: int) -> list[int]:
    if bit_depth not in {1, 2, 4}:
        raise PNGDeepColorDecodeError("png_bit_depth_invalid", "packed samples require bit depth 1, 2, or 4")
    mask = (1 << bit_depth) - 1
    samples = []
    for byte in row:
        for shift in range(8 - bit_depth, -1, -bit_depth):
            samples.append((byte >> shift) & mask)
            if len(samples) == expected_count:
                return samples
    if len(samples) != expected_count:
        raise PNGDeepColorDecodeError("png_scanline_length_mismatch", "packed scanline ended early")
    return samples


def _ramp_palette(bit_depth: int) -> list[tuple[int, int, int]]:
    if bit_depth not in {1, 2, 4}:
        raise ValueError("indexed low-bit palette requires bit depth 1, 2, or 4")
    return [
        (value := _sample_to_byte(index, bit_depth), value, value)
        for index in range(2**bit_depth)
    ]


def _sample_to_rgba_byte(sample: bytes, bit_depth: int) -> int:
    if bit_depth == 8:
        return sample[0]
    if bit_depth == 16:
        return _sample16_to_byte(sample)
    raise PNGDeepColorDecodeError("png_bit_depth_invalid", "sample must be 8 or 16 bits")


def _sample16_to_byte(sample: bytes) -> int:
    if len(sample) != 2:
        raise PNGDeepColorDecodeError("png_sample_length_invalid", "16-bit sample must be two bytes")
    value = struct.unpack(">H", sample)[0]
    return (value * 255 + 32767) // 65535


def _byte_to_sample(value: int, bit_depth: int) -> int:
    max_sample = (1 << bit_depth) - 1
    return (value * max_sample + 127) // 255


def _sample_to_byte(sample: int, bit_depth: int) -> int:
    max_sample = (1 << bit_depth) - 1
    return (sample * 255 + max_sample // 2) // max_sample


def _uint16(value: int) -> bytes:
    if value < 0 or value > 65535:
        raise ValueError("16-bit sample must be in [0, 65535]")
    return struct.pack(">H", value)


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


def _pixel_delta_count(
    source: list[tuple[int, int, int, int]],
    visual: list[tuple[int, int, int, int]],
) -> int:
    return sum(1 for source_pixel, visual_pixel in zip(source, visual) if source_pixel != visual_pixel)


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


def _sorted_unique(values) -> list[int]:
    return sorted({int(value) for value in values})


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
                "source_visual_delta_count": result["source_visual_delta_count"],
                "semantic_fidelity": result["semantic_fidelity"],
                "pixel_fidelity": result["pixel_fidelity"],
            }
            for result in json_report["variant_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# PNG Deep Color Sidecar Decoder Stage 0\n\n"
        "Bounded low-bit, 16-bit sample, and greyscale-alpha PNG import/export "
        "proof bound to Mechagotchi JSON sidecars.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Variants per profile: {report['variant_count_per_profile']}\n"
        f"- Variant round-trip successes: {report['variant_roundtrip_success_count']}"
        f"/{report['variant_roundtrip_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- Supported color types: {metrics['supported_color_types']}\n"
        f"- Supported bit depths: {metrics['supported_bit_depths']}\n"
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
        default=ROOT / "data/workshop_editor/png_deep_color_sidecar_decoder_stage0",
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
    report = run_png_deep_color_sidecar_decoder_lab(profile_paths, args.generated_root)
    write_png_deep_color_sidecar_decoder_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_PNG_DEEP_COLOR_SIDECAR_DECODER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(_json_report(report), indent=2))


if __name__ == "__main__":
    main()
