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
from png_adam7_interlace_decoder import ADAM7_PASSES
from png_deep_color_sidecar_decoder import (
    ALLOWED_BIT_DEPTHS_BY_COLOR_TYPE,
    DEEP_COLOR_VARIANT_SPECS,
    PNGDeepColorDecodeError,
    _filter_bpp,
    _filter_row,
    _parse_plte,
    _parse_trns,
    _read_png_chunks,
    _rows_to_rgba_pixels,
    _scanline_byte_length,
    _unfilter_row,
    _variant_rows,
)
from standard_image_sidecar_decoder import PNG_SIGNATURE, render_grid_rgba_pixels
from png_chunk_reader import PNGChunkError, bounded_decompress
from workshop_editor import compare_semantic_grid_fidelity


REPORT_PATH = Path("data/workshop_editor/png_adam7_deep_color_cross_product_stage0.json")
DATA_PATH = Path("data/workshop_editor/png_adam7_deep_color_cross_product_data.js")

ADAM7_DEEP_COLOR_VARIANT_SPECS = [
    {
        **spec,
        "variant_id": f"adam7_{spec['variant_id']}",
        "base_variant_id": spec["variant_id"],
        "description": f"Adam7 interlaced {spec['description']}",
    }
    for spec in DEEP_COLOR_VARIANT_SPECS
]


class PNGAdam7DeepColorDecodeError(ValueError):
    def __init__(self, family: str, message: str):
        super().__init__(message)
        self.family = family
        self.message = message


def decode_png_adam7_deep_color(png_bytes: bytes) -> dict:
    try:
        chunks = _read_png_chunks(png_bytes)
    except PNGDeepColorDecodeError as exc:
        raise PNGAdam7DeepColorDecodeError(exc.family, exc.message) from exc
    if not chunks or chunks[0]["type"] != "IHDR":
        raise PNGAdam7DeepColorDecodeError("png_ihdr_missing", "PNG IHDR chunk must be first")

    ihdr = chunks[0]["payload"]
    if len(ihdr) != 13:
        raise PNGAdam7DeepColorDecodeError("png_ihdr_invalid", "PNG IHDR chunk length must be 13")
    width, height, bit_depth, color_type, compression, filter_method, interlace = (
        struct.unpack(">IIBBBBB", ihdr)
    )
    if width <= 0 or height <= 0:
        raise PNGAdam7DeepColorDecodeError("png_dimensions_invalid", "PNG dimensions must be positive")
    if color_type not in ALLOWED_BIT_DEPTHS_BY_COLOR_TYPE:
        raise PNGAdam7DeepColorDecodeError(
            "png_color_type_unsupported",
            "Stage 0 Adam7/deep-color decoder supports color types 0, 2, 3, 4, and 6 only",
        )
    if bit_depth not in ALLOWED_BIT_DEPTHS_BY_COLOR_TYPE[color_type]:
        raise PNGAdam7DeepColorDecodeError(
            "png_bit_depth_color_type_invalid",
            "PNG bit depth is not allowed for this color type",
        )
    if compression != 0 or filter_method != 0:
        raise PNGAdam7DeepColorDecodeError(
            "png_method_unsupported",
            "only PNG compression method 0 and filter method 0 are supported",
        )
    if interlace != 1:
        raise PNGAdam7DeepColorDecodeError(
            "png_adam7_deep_color_interlace_required",
            "this Stage 0 cross-product decoder requires Adam7 interlace method 1",
        )

    try:
        plte = _parse_plte(chunks)
        trns = _parse_trns(chunks)
    except PNGDeepColorDecodeError as exc:
        raise PNGAdam7DeepColorDecodeError(exc.family, exc.message) from exc
    if color_type == 3 and not plte:
        raise PNGAdam7DeepColorDecodeError("png_plte_missing", "indexed-color PNG requires PLTE")
    if color_type == 3 and len(plte) > 2**bit_depth:
        raise PNGAdam7DeepColorDecodeError(
            "png_plte_bit_depth_mismatch",
            "PLTE entry count exceeds the range representable by the bit depth",
        )
    if trns and color_type != 3:
        raise PNGAdam7DeepColorDecodeError(
            "png_trns_unsupported",
            "Stage 0 Adam7/deep-color decoder only supports tRNS for indexed-color PNG",
        )
    if trns and len(trns) > len(plte):
        raise PNGAdam7DeepColorDecodeError("png_trns_invalid", "indexed-color tRNS exceeds PLTE length")

    idat = b"".join(chunk["payload"] for chunk in chunks if chunk["type"] == "IDAT")
    if not idat:
        raise PNGAdam7DeepColorDecodeError("png_idat_missing", "PNG IDAT chunk is required")
    if not any(chunk["type"] == "IEND" for chunk in chunks):
        raise PNGAdam7DeepColorDecodeError("png_iend_missing", "PNG IEND chunk is required")
    expected_length = sum(
        _pass_size(height, pass_spec["y_start"], pass_spec["y_step"])
        * (
            1
            + _scanline_byte_length(
                _pass_size(width, pass_spec["x_start"], pass_spec["x_step"]),
                color_type,
                bit_depth,
            )
        )
        for pass_spec in ADAM7_PASSES
    )
    try:
        raw = bounded_decompress(idat, expected_length)
    except PNGChunkError as exc:
        raise PNGAdam7DeepColorDecodeError("png_idat_decompression_failed", exc.message) from exc

    pixels: list[tuple[int, int, int, int]] = [(0, 0, 0, 0)] * (width * height)
    assigned = [False] * (width * height)
    offset = 0
    filter_types_seen = []
    pass_summaries = []

    for pass_spec in ADAM7_PASSES:
        pass_width = _pass_size(width, pass_spec["x_start"], pass_spec["x_step"])
        pass_height = _pass_size(height, pass_spec["y_start"], pass_spec["y_step"])
        scanline_length = _scanline_byte_length(pass_width, color_type, bit_depth)
        filter_bpp = _filter_bpp(color_type, bit_depth)
        pass_filters = []
        pass_rows = []
        previous = None
        for _row_index in range(pass_height):
            if offset + 1 + scanline_length > len(raw):
                raise PNGAdam7DeepColorDecodeError(
                    "png_adam7_deep_color_scanline_length_mismatch",
                    "Adam7 reduced-image scanline data ended early",
                )
            filter_type = raw[offset]
            offset += 1
            if filter_type > 4:
                raise PNGAdam7DeepColorDecodeError(
                    "png_filter_type_unsupported",
                    "PNG filter type must be in 0..4 for filter method 0",
                )
            row = raw[offset : offset + scanline_length]
            offset += scanline_length
            try:
                unfiltered = _unfilter_row(row, previous, filter_bpp, filter_type)
            except PNGDeepColorDecodeError as exc:
                raise PNGAdam7DeepColorDecodeError(exc.family, exc.message) from exc
            pass_rows.append(unfiltered)
            previous = unfiltered
            if filter_type not in pass_filters:
                pass_filters.append(filter_type)
            if filter_type not in filter_types_seen:
                filter_types_seen.append(filter_type)

        try:
            pass_pixels = _rows_to_rgba_pixels(
                pass_rows,
                width=pass_width,
                color_type=color_type,
                bit_depth=bit_depth,
                plte=plte,
                trns=trns,
            )
        except PNGDeepColorDecodeError as exc:
            raise PNGAdam7DeepColorDecodeError(exc.family, exc.message) from exc
        for row_index in range(pass_height):
            for pass_x in range(pass_width):
                x = pass_spec["x_start"] + pass_x * pass_spec["x_step"]
                y = pass_spec["y_start"] + row_index * pass_spec["y_step"]
                pixel_index = y * width + x
                pixels[pixel_index] = pass_pixels[row_index * pass_width + pass_x]
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
                "scanline_byte_length": scanline_length,
                "filter_bpp": filter_bpp,
                "filter_types_seen": pass_filters,
            }
        )

    if offset != len(raw):
        raise PNGAdam7DeepColorDecodeError(
            "png_adam7_deep_color_scanline_length_mismatch",
            "Adam7 reduced-image scanline data has trailing bytes",
        )
    if not all(assigned):
        raise PNGAdam7DeepColorDecodeError(
            "png_adam7_deep_color_pixel_coverage_incomplete",
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
        "has_plte": bool(plte),
        "has_trns": bool(trns),
    }


def export_png_adam7_deep_color_suite_with_sidecars(
    grid: dict, slip_profile: dict
) -> list[dict]:
    width, height = grid["grid_size"]
    source_pixels = render_grid_rgba_pixels(grid)
    source_hash = _hash_pixels(source_pixels)
    exports = []
    for spec in ADAM7_DEEP_COLOR_VARIANT_SPECS:
        png_bytes = encode_png_adam7_deep_color(width, height, source_pixels, spec)
        decoded = decode_png_adam7_deep_color(png_bytes)
        visual_hash = _hash_pixels(decoded["pixels"])
        delta_count = _pixel_delta_count(source_pixels, decoded["pixels"])
        asset = _asset_from_decoded(
            png_bytes,
            decoded,
            asset_id=f"{slip_profile['profile_id']}_{spec['variant_id']}.png",
            uri=(
                "generated://workshop/png-adam7-deep-color/"
                f"{slip_profile['profile_id']}_{spec['variant_id']}.png"
            ),
        )
        sidecar = build_sidecar_for_grid(grid, slip_profile, asset)
        sidecar["sidecar_id"] = f"{grid['grid_id']}_{spec['variant_id']}_sidecar"
        sidecar["adam7_deep_color_binding"] = {
            "variant_id": spec["variant_id"],
            "base_variant_id": spec["base_variant_id"],
            "color_type": spec["color_type"],
            "bit_depth": spec["bit_depth"],
            "compression_method": 0,
            "filter_method": 0,
            "interlace_method": 1,
            "pass_order": decoded["pass_order"],
            "pass_summaries": decoded["pass_summaries"],
            "non_empty_pass_count": decoded["non_empty_pass_count"],
            "filter_types": decoded["filter_types_seen"],
            "source_render_pixel_hash": source_hash,
            "visual_carrier_pixel_hash": visual_hash,
            "source_visual_delta_count": delta_count,
            "description": spec["description"],
        }
        sidecar["limitations"] = [
            "Stage 0 cross-product decoder supports bounded Adam7 interlaced PNG only.",
            "Supported deep-color variants mirror the non-interlaced deep-color lab.",
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


def import_png_adam7_deep_color_with_sidecar(png_bytes: bytes, sidecar: dict) -> dict:
    try:
        decoded = decode_png_adam7_deep_color(png_bytes)
    except PNGAdam7DeepColorDecodeError as exc:
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

    cross_product_validation = _validate_adam7_deep_color_binding(sidecar, decoded)
    if not cross_product_validation["ok"]:
        return {
            "ok": False,
            "asset": asset,
            "decoded_png": _decoded_summary(decoded),
            "validation": validation,
            "errors": cross_product_validation["errors"],
            "error_families": cross_product_validation["error_families"],
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


def run_png_adam7_deep_color_cross_product_lab(
    profile_paths: list[Path], generated_root: Path
) -> dict:
    variant_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        for exported in export_png_adam7_deep_color_suite_with_sidecars(grid, profile):
            imported = import_png_adam7_deep_color_with_sidecar(
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
        "artifact_id": "png_adam7_deep_color_cross_product_stage0",
        "status": "research_png_adam7_deep_color_cross_product_no_package_code",
        "date": "2026-05-14",
        "purpose": (
            "Close the bounded Stage 0 cross-product between Adam7 interlace "
            "and the previously proven deep-color PNG sidecar decoder subset."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
            "labs/workshop_editor/external_metadata_sidecar.py",
            "labs/workshop_editor/png_adam7_interlace_decoder.py",
            "labs/workshop_editor/png_deep_color_sidecar_decoder.py",
            "labs/workshop_editor/png_adam7_deep_color_cross_product.py",
        ],
        "external_anchors": [
            {
                "source": "W3C PNG specification",
                "url": "https://www.w3.org/TR/png-3/",
                "used_for": "PNG Adam7 pass schedule, color type and bit depth matrix, packed reduced-image scanline sizing, filter method 0, PLTE, IDAT, and CRC semantics.",
            }
        ],
        "profile_count": len(profile_paths),
        "variant_count_per_profile": len(ADAM7_DEEP_COLOR_VARIANT_SPECS),
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
                spec["color_type"] for spec in ADAM7_DEEP_COLOR_VARIANT_SPECS
            ),
            "supported_bit_depths": _sorted_unique(
                spec["bit_depth"] for spec in ADAM7_DEEP_COLOR_VARIANT_SPECS
            ),
            "supported_filter_types": [0, 1, 2, 3, 4],
            "mean_non_empty_pass_count": _mean(
                result["decoded_png"]["non_empty_pass_count"]
                for result in variant_results
            ),
            "quantized_visual_variant_count": sum(
                1
                for result in variant_results
                if result["source_visual_delta_count"] > 0
            ),
        },
        "variant_specs": deepcopy(ADAM7_DEEP_COLOR_VARIANT_SPECS),
        "variant_results": variant_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "png_adam7_deep_color_cross_product_decoder",
            "png_adam7_deep_color_low_bit_decoder",
            "png_adam7_deep_color_16bit_decoder",
            "png_adam7_deep_color_grayscale_alpha_decoder",
            "png_adam7_deep_color_pass_manifest",
            "png_adam7_deep_color_sidecar_semantic_restore",
            "png_adam7_deep_color_invalid_probe_rejection",
        ],
        "blocked_states": [
            "apng_decoder",
            "full_png_conformance",
            "live_external_editor_rewrite_validation",
            "private_chunk_editor_preservation_matrix",
            "final_png_production_carrier_selection",
            "package_runtime_integration",
            "manual_readability_calibration",
            "profile_weighted_evolution",
        ],
        "decision": "prototype_png_adam7_deep_color_cross_product",
        "next_research_step": (
            "Move remaining PNG work to APNG/full-conformance fixtures or live "
            "external editor rewrite validation before final carrier selection."
        ),
    }


def write_png_adam7_deep_color_cross_product_artifacts(
    output_dir: Path, report: dict
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "png_adam7_deep_color_cross_product_stage0.json", _json_report(report))
    for result in report["variant_results"]:
        (output_dir / result["png_file_name"]).write_bytes(
            bytes.fromhex(result["png_bytes_hex"])
        )
        _write_json(output_dir / result["sidecar_file_name"], result["sidecar"])
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "png_adam7_deep_color_cross_product_data.js").write_text(
        "window.MECHAGOTCHI_PNG_ADAM7_DEEP_COLOR_CROSS_PRODUCT = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def encode_png_adam7_deep_color(
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

    raw = bytearray()
    filter_cursor = 0
    plte = []
    trns = []
    filter_bpp = _filter_bpp(color_type, bit_depth)
    for pass_spec in ADAM7_PASSES:
        pass_width = _pass_size(width, pass_spec["x_start"], pass_spec["x_step"])
        pass_height = _pass_size(height, pass_spec["y_start"], pass_spec["y_step"])
        if pass_width == 0 or pass_height == 0:
            continue
        pass_pixels = []
        for row_index in range(pass_height):
            y = pass_spec["y_start"] + row_index * pass_spec["y_step"]
            for pass_x in range(pass_width):
                x = pass_spec["x_start"] + pass_x * pass_spec["x_step"]
                pass_pixels.append(pixels[y * width + x])
        rows, pass_plte, pass_trns = _variant_rows(
            pass_width,
            pass_height,
            pass_pixels,
            color_type,
            bit_depth,
        )
        if color_type == 3 and not plte:
            plte = pass_plte
            trns = pass_trns
        previous = None
        for row in rows:
            filter_type = filter_types[filter_cursor % len(filter_types)]
            filter_cursor += 1
            raw.append(filter_type)
            raw.extend(_filter_row(row, previous, filter_bpp, filter_type))
            previous = row

    ihdr = struct.pack(">IIBBBBB", width, height, bit_depth, color_type, 0, 0, 1)
    chunks = [PNG_SIGNATURE, _png_chunk(b"IHDR", ihdr)]
    if color_type == 3:
        chunks.append(_png_chunk(b"PLTE", b"".join(bytes(rgb) for rgb in plte)))
        if any(alpha < 255 for alpha in trns):
            chunks.append(_png_chunk(b"tRNS", bytes(trns)))
    chunks.extend(
        [
            _png_chunk(b"IDAT", zlib.compress(bytes(raw))),
            _png_chunk(b"IEND", b""),
        ]
    )
    return b"".join(chunks)


def _validate_adam7_deep_color_binding(sidecar: dict, decoded: dict) -> dict:
    errors = []
    binding = sidecar.get("adam7_deep_color_binding", {})
    if not binding:
        errors.append(_error("adam7_deep_color_binding", "png_adam7_deep_color_binding_missing"))
    else:
        if binding.get("color_type") != decoded["color_type"]:
            errors.append(_error("adam7_deep_color_binding.color_type", "png_adam7_deep_color_color_type_mismatch"))
        if binding.get("bit_depth") != decoded["bit_depth"]:
            errors.append(_error("adam7_deep_color_binding.bit_depth", "png_adam7_deep_color_bit_depth_mismatch"))
        if binding.get("interlace_method") != decoded["interlace_method"]:
            errors.append(_error("adam7_deep_color_binding.interlace_method", "png_adam7_deep_color_interlace_mismatch"))
        if binding.get("pass_order") != decoded["pass_order"]:
            errors.append(_error("adam7_deep_color_binding.pass_order", "png_adam7_deep_color_pass_manifest_mismatch"))
        if binding.get("pass_summaries") != decoded["pass_summaries"]:
            errors.append(_error("adam7_deep_color_binding.pass_summaries", "png_adam7_deep_color_pass_manifest_mismatch"))
        if binding.get("non_empty_pass_count") != decoded["non_empty_pass_count"]:
            errors.append(_error("adam7_deep_color_binding.non_empty_pass_count", "png_adam7_deep_color_pass_manifest_mismatch"))
        expected_filters = sorted(set(binding.get("filter_types", [])))
        actual_filters = sorted(set(decoded["filter_types_seen"]))
        if expected_filters != actual_filters:
            errors.append(_error("adam7_deep_color_binding.filter_types", "png_adam7_deep_color_filter_mismatch"))
        expected_hash = binding.get("visual_carrier_pixel_hash")
        if expected_hash != _hash_pixels(decoded["pixels"]):
            errors.append(_error("adam7_deep_color_binding.visual_carrier_pixel_hash", "png_adam7_deep_color_pixel_hash_mismatch"))
    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "error_families": sorted({error["family"] for error in errors}),
    }


def _invalid_probe_results(reference_result: dict) -> list[dict]:
    sidecar = reference_result["sidecar"]
    png_bytes = bytes.fromhex(reference_result["png_bytes_hex"])

    non_interlaced_png = _replace_ihdr_interlace(png_bytes, 0)
    truncated_scanline = _replace_idat_raw(png_bytes, _idat_raw(png_bytes)[:-1])
    raw_with_bad_filter = bytearray(_idat_raw(png_bytes))
    raw_with_bad_filter[0] = 5
    bad_filter_png = _replace_idat_raw(png_bytes, bytes(raw_with_bad_filter))

    wrong_pass_sidecar = deepcopy(sidecar)
    wrong_pass_sidecar["adam7_deep_color_binding"]["pass_summaries"][0]["pixel_count"] += 1

    wrong_bit_depth_sidecar = deepcopy(sidecar)
    wrong_bit_depth_sidecar["adam7_deep_color_binding"]["bit_depth"] = 16

    wrong_pixel_sidecar = deepcopy(sidecar)
    wrong_pixel_sidecar["adam7_deep_color_binding"]["visual_carrier_pixel_hash"] = (
        "sha256:not-the-visual-carrier"
    )

    wrong_asset_sidecar = deepcopy(sidecar)
    wrong_asset_sidecar["asset_binding"]["content_hash"] = "sha256:not-the-png"

    return [
        _compact_import_result(import_png_adam7_deep_color_with_sidecar(non_interlaced_png, sidecar)),
        _compact_import_result(import_png_adam7_deep_color_with_sidecar(truncated_scanline, sidecar)),
        _compact_import_result(import_png_adam7_deep_color_with_sidecar(bad_filter_png, sidecar)),
        _compact_import_result(import_png_adam7_deep_color_with_sidecar(png_bytes, wrong_pass_sidecar)),
        _compact_import_result(import_png_adam7_deep_color_with_sidecar(png_bytes, wrong_bit_depth_sidecar)),
        _compact_import_result(import_png_adam7_deep_color_with_sidecar(png_bytes, wrong_pixel_sidecar)),
        _compact_import_result(import_png_adam7_deep_color_with_sidecar(png_bytes, wrong_asset_sidecar)),
    ]


def _idat_raw(png_bytes: bytes) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    idat = b"".join(chunk["payload"] for chunk in chunks if chunk["type"] == "IDAT")
    return zlib.decompress(idat)


def _replace_idat_raw(png_bytes: bytes, raw: bytes) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    new_idat = zlib.compress(raw)
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


def _replace_ihdr_interlace(png_bytes: bytes, interlace_method: int) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    rewritten = [PNG_SIGNATURE]
    for index, chunk in enumerate(chunks):
        payload = chunk["payload"]
        if index == 0 and chunk["type"] == "IHDR":
            width, height, bit_depth, color_type, compression, filter_method, _interlace = (
                struct.unpack(">IIBBBBB", payload)
            )
            payload = struct.pack(
                ">IIBBBBB",
                width,
                height,
                bit_depth,
                color_type,
                compression,
                filter_method,
                interlace_method,
            )
        rewritten.append(_png_chunk(chunk["type"].encode("ascii"), payload))
    return b"".join(rewritten)


def _png_chunk(chunk_type: bytes, payload: bytes) -> bytes:
    crc = binascii.crc32(payload, binascii.crc32(chunk_type)) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + chunk_type + payload + struct.pack(">I", crc)


def _asset_from_decoded(png_bytes: bytes, decoded: dict, *, asset_id: str, uri: str) -> dict:
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


def _pass_size(size: int, start: int, step: int) -> int:
    if size <= start:
        return 0
    return (size - start + step - 1) // step


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
        "has_plte": decoded["has_plte"],
        "has_trns": decoded["has_trns"],
    }


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
    return str(path).replace("\\", "/")


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def _mean(values) -> float:
    values = list(values)
    if not values:
        return 0.0
    return round(sum(values) / len(values), 6)


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
        "# PNG Adam7 Deep Color Cross Product Stage 0\n\n"
        "Bounded Adam7 interlace plus deep-color PNG import/export proof bound "
        "to Mechagotchi JSON sidecars.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Variants per profile: {report['variant_count_per_profile']}\n"
        f"- Variant round-trip successes: {report['variant_roundtrip_success_count']}"
        f"/{report['variant_roundtrip_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- Supported color types: {metrics['supported_color_types']}\n"
        f"- Supported bit depths: {metrics['supported_bit_depths']}\n"
        f"- Mean non-empty Adam7 passes: {metrics['mean_non_empty_pass_count']}\n"
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
        default=Path("data/workshop_editor/png_adam7_deep_color_cross_product_stage0"),
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
    report = run_png_adam7_deep_color_cross_product_lab(profile_paths, args.generated_root)
    write_png_adam7_deep_color_cross_product_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_PNG_ADAM7_DEEP_COLOR_CROSS_PRODUCT = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(_json_report(report), indent=2))


if __name__ == "__main__":
    main()
