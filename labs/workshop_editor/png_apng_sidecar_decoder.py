import argparse
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
from png_embedded_sidecar_writer import (
    _chunk,
    _compact_import_result,
    _decoded_summary,
    _hash_bytes,
    _hash_json,
    _portable,
    _ratio,
    _read_json,
    _read_png_chunks,
    _semantic_fidelity,
    _write_json,
    _write_png_chunks,
)
from standard_image_sidecar_decoder import render_grid_rgba_pixels
from png_chunk_reader import PNGChunkError, bounded_decompress
from workshop_editor import compare_semantic_grid_fidelity


REPORT_PATH = Path("data/workshop_editor/apng_sidecar_decoder_stage0.json")
DATA_PATH = Path("data/workshop_editor/apng_sidecar_decoder_data.js")
APNG_FRAME_POLICY = "bounded_full_canvas_source_frames"


class APNGDecodeError(ValueError):
    def __init__(self, family: str, message: str):
        super().__init__(message)
        self.family = family
        self.message = message


def export_apng_with_sidecar(grid: dict, slip_profile: dict) -> dict:
    width, height = grid["grid_size"]
    base_pixels = render_grid_rgba_pixels(grid)
    frames = [
        {
            "frame_id": "base",
            "pixels": base_pixels,
            "delay_num": 1,
            "delay_den": 5,
        },
        {
            "frame_id": "pulse",
            "pixels": _pulse_pixels(base_pixels),
            "delay_num": 1,
            "delay_den": 5,
        },
    ]
    png_bytes = _encode_bounded_apng(width, height, frames)
    decoded = decode_apng_frames(png_bytes)
    asset = _asset_from_apng_bytes(
        png_bytes,
        asset_id=f"{grid['grid_id']}.apng.png",
        uri=f"generated://workshop/apng-sidecar-decoder/{grid['grid_id']}.png",
    )
    sidecar = build_sidecar_for_grid(grid, slip_profile, asset)
    sidecar["sidecar_id"] = f"{grid['grid_id']}_apng_sidecar"
    sidecar["apng_binding"] = {
        "binding_model": "apng_sidecar_decoder_v1",
        "frame_policy": APNG_FRAME_POLICY,
        "frame_count": decoded["frame_count"],
        "num_plays": decoded["animation_control"]["num_plays"],
        "sequence_numbers": decoded["sequence_numbers"],
        "frames": [
            {
                "frame_index": frame["frame_index"],
                "frame_id": frames[frame["frame_index"]]["frame_id"],
                "width": frame["width"],
                "height": frame["height"],
                "x_offset": frame["x_offset"],
                "y_offset": frame["y_offset"],
                "delay_ms": frame["delay_ms"],
                "dispose_op": frame["dispose_op"],
                "blend_op": frame["blend_op"],
                "pixel_hash": frame["pixel_hash"],
            }
            for frame in decoded["frames"]
        ],
    }
    sidecar["limitations"] = [
        "Stage 0 APNG decoder supports two full-canvas 8-bit RGBA source frames only.",
        "Frame semantics remain sidecar-bound; APNG pixels do not encode Mechagotchi organs.",
        "Blend-over, partial-frame offsets, disposal variants, APNG text/private metadata, and full APNG/PNG conformance are not claimed.",
        "Live external editor open-save preservation is not verified by this lab.",
    ]
    return {
        "png_bytes": png_bytes,
        "asset": asset,
        "sidecar": sidecar,
        "decoded_apng": _decoded_apng_summary(decoded),
    }


def decode_apng_frames(png_bytes: bytes) -> dict:
    chunks = _read_png_chunks(png_bytes)
    if not chunks or chunks[0]["type"] != "IHDR":
        raise APNGDecodeError("png_ihdr_missing", "PNG IHDR chunk must be first")
    ihdr = chunks[0]["data"]
    if len(ihdr) != 13:
        raise APNGDecodeError("png_ihdr_invalid", "PNG IHDR chunk length must be 13")
    width, height, bit_depth, color_type, compression, filter_method, interlace = (
        struct.unpack(">IIBBBBB", ihdr)
    )
    if bit_depth != 8 or color_type != 6:
        raise APNGDecodeError(
            "apng_color_model_unsupported",
            "Stage 0 APNG supports only 8-bit RGBA frames",
        )
    if compression != 0 or filter_method != 0 or interlace != 0:
        raise APNGDecodeError(
            "apng_method_unsupported",
            "Stage 0 APNG supports only compression 0, filter method 0, and no interlace",
        )

    actl_chunks = [chunk for chunk in chunks if chunk["type"] == "acTL"]
    if not actl_chunks:
        raise APNGDecodeError("apng_control_missing", "APNG acTL chunk is required")
    if len(actl_chunks) != 1 or len(actl_chunks[0]["data"]) != 8:
        raise APNGDecodeError("apng_control_invalid", "APNG acTL chunk must be unique and 8 bytes")
    num_frames, num_plays = struct.unpack(">II", actl_chunks[0]["data"])
    if num_frames != 2:
        raise APNGDecodeError(
            "apng_frame_count_unsupported",
            "Stage 0 APNG supports exactly two frames",
        )

    expected_sequence = 0
    sequence_numbers = []
    animation_chunk_order = []
    frames = []
    current = None
    idat_seen = False

    def finalize_current() -> None:
        nonlocal current
        if current is None:
            return
        if not current["data"]:
            raise APNGDecodeError(
                "apng_frame_data_missing",
                "APNG frame control lacks matching image data",
            )
        frames.append(_decode_frame(current, len(frames), width, height))
        current = None

    for chunk in chunks[1:]:
        chunk_type = chunk["type"]
        if chunk_type == "fcTL":
            finalize_current()
            control = _decode_fctl(chunk["data"])
            if control["sequence_number"] != expected_sequence:
                raise APNGDecodeError(
                    "apng_sequence_number_invalid",
                    "APNG fcTL sequence numbers must be consecutive",
                )
            sequence_numbers.append(control["sequence_number"])
            expected_sequence += 1
            current = {**control, "data": bytearray(), "data_source": None}
            animation_chunk_order.append("fcTL")
        elif chunk_type == "IDAT":
            if current is None:
                raise APNGDecodeError(
                    "apng_default_frame_control_missing",
                    "Stage 0 APNG requires fcTL before IDAT default image data",
                )
            if idat_seen and current["data_source"] != "IDAT":
                raise APNGDecodeError("apng_idat_order_invalid", "IDAT order is invalid")
            current["data"].extend(chunk["data"])
            current["data_source"] = "IDAT"
            idat_seen = True
            animation_chunk_order.append("IDAT")
        elif chunk_type == "fdAT":
            if current is None:
                raise APNGDecodeError(
                    "apng_frame_control_missing",
                    "fdAT chunk requires preceding fcTL",
                )
            if len(chunk["data"]) < 4:
                raise APNGDecodeError("apng_fdat_invalid", "fdAT chunk lacks sequence number")
            sequence_number = struct.unpack(">I", chunk["data"][:4])[0]
            if sequence_number != expected_sequence:
                raise APNGDecodeError(
                    "apng_sequence_number_invalid",
                    "APNG fdAT sequence numbers must be consecutive",
                )
            sequence_numbers.append(sequence_number)
            expected_sequence += 1
            current["data"].extend(chunk["data"][4:])
            current["data_source"] = "fdAT"
            animation_chunk_order.append("fdAT")
        elif chunk_type == "IEND":
            finalize_current()
            break

    if len(frames) != num_frames:
        raise APNGDecodeError(
            "apng_frame_count_mismatch",
            "APNG decoded frame count does not match acTL",
        )
    return {
        "width": width,
        "height": height,
        "bit_depth": bit_depth,
        "color_type": color_type,
        "chunks": [chunk["type"] for chunk in chunks],
        "animation_control": {
            "num_frames": num_frames,
            "num_plays": num_plays,
        },
        "frame_count": len(frames),
        "sequence_numbers": sequence_numbers,
        "animation_chunk_order": animation_chunk_order,
        "frames": frames,
    }


def import_apng_with_sidecar(
    png_bytes: bytes,
    sidecar: dict,
    source_grid: dict | None = None,
) -> dict:
    try:
        decoded = decode_apng_frames(png_bytes)
    except APNGDecodeError as exc:
        return _failed_import("apng", exc.family, exc.message)
    except Exception as exc:
        family = getattr(exc, "family", "apng_decode_failed")
        message = getattr(exc, "message", str(exc))
        return _failed_import("apng", family, message)

    asset = _asset_from_apng_bytes(
        png_bytes,
        asset_id=sidecar.get("asset_binding", {}).get("asset_id", "unknown.apng.png"),
        uri=sidecar.get("asset_binding", {}).get("uri", "unknown://apng"),
    )
    validation = validate_sidecar_binding(sidecar, asset)
    if not validation["ok"]:
        return {
            "ok": False,
            "asset": asset,
            "decoded_apng": _decoded_apng_summary(decoded),
            "validation": validation,
            "errors": validation["errors"],
            "error_families": validation["error_families"],
        }

    binding_result = _validate_apng_binding(sidecar.get("apng_binding"), decoded)
    if not binding_result["ok"]:
        return {
            "ok": False,
            "asset": asset,
            "decoded_apng": _decoded_apng_summary(decoded),
            "validation": validation,
            "errors": binding_result["errors"],
            "error_families": binding_result["error_families"],
        }

    restored = restore_grid_from_sidecar(sidecar, asset)
    profile = sidecar["slip_binding"]["profile_snapshot"]
    grid_validation = validate_grid(restored)
    alignment = is_grid_aligned(restored, profile)
    semantic_source = source_grid or restore_grid_from_sidecar(sidecar, asset, validate=False)
    diff = compare_semantic_grid_fidelity(semantic_source, restored)
    fidelity = _semantic_fidelity(diff, semantic_source)
    errors = []
    if not grid_validation.ok:
        errors.extend(_error("$", "restored_grid_invalid", message) for message in grid_validation.errors)
    if not alignment.ok:
        errors.extend(_error("$", "restored_grid_not_slip_aligned", message) for message in alignment.errors)
    return {
        "ok": len(errors) == 0,
        "asset": asset,
        "decoded_apng": _decoded_apng_summary(decoded),
        "validation": validation,
        "apng_policy": {
            "frame_policy": sidecar["apng_binding"]["frame_policy"],
            "frame_count": decoded["frame_count"],
            "full_canvas_only": all(frame["full_canvas"] for frame in decoded["frames"]),
            "source_blend_only": all(frame["blend_op"] == 0 for frame in decoded["frames"]),
            "dispose_none_only": all(frame["dispose_op"] == 0 for frame in decoded["frames"]),
            "live_external_editor_verified": False,
        },
        "restored_grid": restored,
        "restored_grid_validation": {
            "valid": grid_validation.ok,
            "errors": grid_validation.errors,
            "slip_aligned": alignment.ok,
            "slip_errors": alignment.errors,
        },
        "semantic_diff": diff,
        "semantic_fidelity": fidelity,
        "frame_pixel_fidelity": 1.0,
        "errors": errors,
        "error_families": sorted({error["family"] for error in errors}),
    }


def remove_apng_control_chunk(png_bytes: bytes) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    return _write_png_chunks([chunk for chunk in chunks if chunk["type"] != "acTL"])


def tamper_apng_sequence_number(png_bytes: bytes) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    updated = []
    tampered = False
    for chunk in chunks:
        if chunk["type"] == "fdAT" and not tampered:
            updated.append(_chunk("fdAT", struct.pack(">I", 99) + chunk["data"][4:]))
            tampered = True
        else:
            updated.append(chunk)
    if not tampered:
        raise APNGDecodeError("apng_fdat_missing", "no fdAT chunk to tamper")
    return _write_png_chunks(updated)


def tamper_apng_blend_op(png_bytes: bytes) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    updated = []
    tampered = False
    for chunk in chunks:
        if chunk["type"] == "fcTL" and not tampered:
            data = bytearray(chunk["data"])
            data[-1] = 1
            updated.append(_chunk("fcTL", bytes(data)))
            tampered = True
        else:
            updated.append(chunk)
    if not tampered:
        raise APNGDecodeError("apng_fctl_missing", "no fcTL chunk to tamper")
    return _write_png_chunks(updated)


def run_apng_sidecar_decoder_lab(
    profile_paths: list[Path],
    generated_root: Path,
) -> dict:
    apng_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        bundle = export_apng_with_sidecar(grid, profile)
        imported = import_apng_with_sidecar(
            bundle["png_bytes"],
            bundle["sidecar"],
            source_grid=grid,
        )
        apng_results.append(
            {
                "profile_id": profile["profile_id"],
                "profile_path": _portable(profile_path),
                "grid_path": _portable(grid_path),
                "png_file_name": f"{profile['profile_id']}_apng_sidecar.png",
                "sidecar_file_name": f"{profile['profile_id']}_apng_sidecar.json",
                "png_bytes_hex": bundle["png_bytes"].hex(),
                "png_byte_count": len(bundle["png_bytes"]),
                "asset": bundle["asset"],
                "sidecar": bundle["sidecar"],
                "decoded_apng": bundle["decoded_apng"],
                "import_result": _compact_apng_import_result(imported),
                "restored_grid_validation": imported.get("restored_grid_validation", {}),
                "semantic_diff": imported.get("semantic_diff", {}),
                "semantic_fidelity": imported.get("semantic_fidelity", 0.0),
                "frame_pixel_fidelity": imported.get("frame_pixel_fidelity", 0.0),
            }
        )

    invalid_probe_results = _invalid_probe_results(apng_results[0])
    success_count = sum(
        1
        for result in apng_results
        if result["import_result"]["ok"]
        and result["semantic_fidelity"] == 1.0
        and result["frame_pixel_fidelity"] == 1.0
    )
    invalid_rejected_count = sum(
        1 for result in invalid_probe_results if not result["ok"]
    )
    return {
        "artifact_id": "apng_sidecar_decoder_stage0",
        "status": "research_apng_sidecar_decoder_no_package_code",
        "date": "2026-05-14",
        "purpose": (
            "Prove a bounded APNG sidecar decoder for two full-canvas 8-bit "
            "RGBA source frames without claiming full APNG or PNG conformance."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
            "labs/workshop_editor/png_apng_sidecar_decoder.py",
        ],
        "external_sources": [
            {
                "name": "W3C Portable Network Graphics (PNG) Specification, Third Edition",
                "url": "https://www.w3.org/TR/png-3/",
                "used_for": "APNG acTL, fcTL, fdAT chunk structure, sequence numbers, dispose, and blend semantics.",
            }
        ],
        "profile_count": len(profile_paths),
        "apng_roundtrip_count": len(apng_results),
        "apng_roundtrip_success_count": success_count,
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "metrics": {
            "apng_roundtrip_success_rate": _ratio(success_count, len(apng_results)),
            "mean_semantic_fidelity": _mean(
                result["semantic_fidelity"] for result in apng_results
            ),
            "mean_frame_pixel_fidelity": _mean(
                result["frame_pixel_fidelity"] for result in apng_results
            ),
            "invalid_probe_rejection_rate": _ratio(
                invalid_rejected_count,
                len(invalid_probe_results),
            ),
        },
        "apng_results": apng_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "apng_full_canvas_source_frame_decoder",
            "apng_actl_fctl_fdat_sequence_validation",
            "apng_sidecar_semantic_restore",
            "apng_frame_hash_validation",
            "apng_invalid_probe_rejection",
        ],
        "blocked_states": [
            "full_apng_png_conformance",
            "partial_frame_blend_over_disposal_variants",
            "APNG_textual_private_metadata_carrier_cross_product",
            "live_external_editor_rewrite_validation",
            "final_png_production_carrier_selection",
            "package_runtime_lifecycle_integration",
            "manual_readability_calibration",
            "profile_weighted_evolution",
        ],
        "decision": "prototype_bounded_apng_sidecar_decoder",
        "next_research_step": (
            "Keep full APNG/PNG conformance, APNG metadata-carrier "
            "cross-products, live external editor validation, and final PNG "
            "carrier selection blocked until direct fixture evidence exists."
        ),
    }


def write_apng_sidecar_decoder_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "apng_sidecar_decoder_stage0.json", _json_report(report))
    for result in report["apng_results"]:
        (output_dir / result["png_file_name"]).write_bytes(
            bytes.fromhex(result["png_bytes_hex"])
        )
        _write_json(output_dir / result["sidecar_file_name"], result["sidecar"])
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "apng_sidecar_decoder_data.js").write_text(
        "window.MECHAGOTCHI_APNG_SIDECAR_DECODER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _encode_bounded_apng(width: int, height: int, frames: list[dict]) -> bytes:
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    chunks = [_chunk("IHDR", ihdr), _chunk("acTL", struct.pack(">II", len(frames), 0))]
    sequence_number = 0
    for index, frame in enumerate(frames):
        chunks.append(
            _chunk(
                "fcTL",
                struct.pack(
                    ">IIIIIHHBB",
                    sequence_number,
                    width,
                    height,
                    0,
                    0,
                    frame["delay_num"],
                    frame["delay_den"],
                    0,
                    0,
                ),
            )
        )
        sequence_number += 1
        compressed = zlib.compress(_rgba_scanlines(width, height, frame["pixels"]))
        if index == 0:
            chunks.append(_chunk("IDAT", compressed))
        else:
            chunks.append(_chunk("fdAT", struct.pack(">I", sequence_number) + compressed))
            sequence_number += 1
    chunks.append(_chunk("IEND", b""))
    return _write_png_chunks(chunks)


def _decode_fctl(data: bytes) -> dict:
    if len(data) != 26:
        raise APNGDecodeError("apng_fctl_invalid", "APNG fcTL chunk length must be 26")
    (
        sequence_number,
        width,
        height,
        x_offset,
        y_offset,
        delay_num,
        delay_den,
        dispose_op,
        blend_op,
    ) = struct.unpack(">IIIIIHHBB", data)
    return {
        "sequence_number": sequence_number,
        "width": width,
        "height": height,
        "x_offset": x_offset,
        "y_offset": y_offset,
        "delay_num": delay_num,
        "delay_den": delay_den,
        "dispose_op": dispose_op,
        "blend_op": blend_op,
    }


def _decode_frame(frame: dict, frame_index: int, canvas_width: int, canvas_height: int) -> dict:
    if (
        frame["width"] != canvas_width
        or frame["height"] != canvas_height
        or frame["x_offset"] != 0
        or frame["y_offset"] != 0
        or frame["dispose_op"] != 0
        or frame["blend_op"] != 0
    ):
        raise APNGDecodeError(
            "apng_frame_control_unsupported",
            "Stage 0 APNG supports only full-canvas dispose-none source-blend frames",
        )
    try:
        raw = bounded_decompress(bytes(frame["data"]), (canvas_width * 4 + 1) * canvas_height)
    except PNGChunkError as exc:
        raise APNGDecodeError("apng_frame_decompression_failed", exc.message) from exc
    pixels = _decode_rgba_scanlines(canvas_width, canvas_height, raw)
    delay_den = frame["delay_den"] or 100
    delay_ms = round((frame["delay_num"] / delay_den) * 1000)
    return {
        "frame_index": frame_index,
        "width": frame["width"],
        "height": frame["height"],
        "x_offset": frame["x_offset"],
        "y_offset": frame["y_offset"],
        "delay_num": frame["delay_num"],
        "delay_den": frame["delay_den"],
        "delay_ms": delay_ms,
        "dispose_op": frame["dispose_op"],
        "blend_op": frame["blend_op"],
        "data_source": frame["data_source"],
        "full_canvas": True,
        "pixel_hash": _pixel_hash(pixels),
        "pixels": pixels,
    }


def _rgba_scanlines(
    width: int,
    height: int,
    pixels: list[tuple[int, int, int, int]],
) -> bytes:
    if len(pixels) != width * height:
        raise ValueError("pixel count does not match APNG dimensions")
    payload = bytearray()
    for y in range(height):
        payload.append(0)
        for pixel in pixels[y * width : (y + 1) * width]:
            payload.extend(pixel)
    return bytes(payload)


def _decode_rgba_scanlines(width: int, height: int, raw: bytes) -> list[tuple[int, int, int, int]]:
    stride = width * 4
    expected = (stride + 1) * height
    if len(raw) != expected:
        raise APNGDecodeError(
            "apng_scanline_length_mismatch",
            "APNG frame scanline length does not match dimensions",
        )
    pixels = []
    offset = 0
    for _y in range(height):
        filter_type = raw[offset]
        offset += 1
        if filter_type != 0:
            raise APNGDecodeError(
                "apng_filter_unsupported",
                "Stage 0 APNG supports only filter type 0",
            )
        row = raw[offset : offset + stride]
        offset += stride
        for x in range(width):
            index = x * 4
            pixels.append(tuple(row[index : index + 4]))
    return pixels


def _pulse_pixels(pixels: list[tuple[int, int, int, int]]) -> list[tuple[int, int, int, int]]:
    pulsed = []
    for index, (red, green, blue, alpha) in enumerate(pixels):
        if index % 3 == 0:
            pulsed.append((min(255, red + 18), min(255, green + 18), min(255, blue + 18), alpha))
        else:
            pulsed.append((max(0, red - 10), max(0, green - 10), max(0, blue - 10), alpha))
    return pulsed


def _validate_apng_binding(binding: object, decoded: dict) -> dict:
    errors = []
    if not isinstance(binding, dict):
        errors.append(_error("apng_binding", "apng_binding_missing", "APNG binding is required"))
        return _validation_result(errors)
    if binding.get("binding_model") != "apng_sidecar_decoder_v1":
        errors.append(_error("apng_binding.binding_model", "apng_binding_model_unsupported", "unsupported APNG binding model"))
    if binding.get("frame_policy") != APNG_FRAME_POLICY:
        errors.append(_error("apng_binding.frame_policy", "apng_frame_policy_mismatch", "APNG frame policy mismatch"))
    if binding.get("frame_count") != decoded["frame_count"]:
        errors.append(_error("apng_binding.frame_count", "apng_frame_count_mismatch", "APNG frame count mismatch"))
    if binding.get("sequence_numbers") != decoded["sequence_numbers"]:
        errors.append(_error("apng_binding.sequence_numbers", "apng_sequence_number_invalid", "APNG sequence numbers mismatch binding"))
    frames = binding.get("frames", [])
    if len(frames) != decoded["frame_count"]:
        errors.append(_error("apng_binding.frames", "apng_frame_count_mismatch", "APNG binding frame list mismatch"))
    else:
        for expected, observed in zip(frames, decoded["frames"]):
            if expected.get("pixel_hash") != observed["pixel_hash"]:
                errors.append(_error("apng_binding.frames.pixel_hash", "apng_frame_hash_mismatch", "APNG frame pixel hash mismatch"))
            for key in ["width", "height", "x_offset", "y_offset", "delay_ms", "dispose_op", "blend_op"]:
                if expected.get(key) != observed[key]:
                    errors.append(_error(f"apng_binding.frames.{key}", "apng_frame_manifest_mismatch", f"APNG frame {key} mismatch"))
    return _validation_result(errors)


def _invalid_probe_results(reference_result: dict) -> list[dict]:
    png_bytes = bytes.fromhex(reference_result["png_bytes_hex"])
    sidecar = reference_result["sidecar"]
    bad_frame_sidecar = deepcopy(sidecar)
    bad_frame_sidecar["apng_binding"]["frames"][1]["pixel_hash"] = "sha256:not-the-frame"
    bad_asset_sidecar = deepcopy(sidecar)
    bad_asset_sidecar["asset_binding"]["content_hash"] = "sha256:not-the-apng"
    probes = [
        ("missing_control", remove_apng_control_chunk(png_bytes), sidecar),
        ("sequence_number", tamper_apng_sequence_number(png_bytes), sidecar),
        ("blend_op", tamper_apng_blend_op(png_bytes), sidecar),
        ("frame_hash", png_bytes, bad_frame_sidecar),
        ("asset_hash", png_bytes, bad_asset_sidecar),
    ]
    return [
        {
            "probe_id": probe_id,
            **_compact_apng_import_result(import_apng_with_sidecar(probe_png, probe_sidecar)),
        }
        for probe_id, probe_png, probe_sidecar in probes
    ]


def _asset_from_apng_bytes(png_bytes: bytes, *, asset_id: str, uri: str) -> dict:
    decoded = decode_apng_frames(png_bytes)
    return {
        "asset_id": asset_id,
        "format_id": "png",
        "media_type": "image/apng",
        "uri": uri,
        "width": decoded["width"],
        "height": decoded["height"],
        "frame_count": decoded["frame_count"],
        "content_hash": _hash_bytes(png_bytes),
        "semantic_policy": "sidecar_required",
    }


def _pixel_hash(pixels: list[tuple[int, int, int, int]]) -> str:
    return _hash_json([list(pixel) for pixel in pixels])


def _decoded_apng_summary(decoded: dict) -> dict:
    return {
        "width": decoded["width"],
        "height": decoded["height"],
        "bit_depth": decoded["bit_depth"],
        "color_type": decoded["color_type"],
        "chunks": decoded["chunks"],
        "animation_control": decoded["animation_control"],
        "frame_count": decoded["frame_count"],
        "sequence_numbers": decoded["sequence_numbers"],
        "animation_chunk_order": decoded["animation_chunk_order"],
        "frames": [
            {
                key: frame[key]
                for key in [
                    "frame_index",
                    "width",
                    "height",
                    "x_offset",
                    "y_offset",
                    "delay_ms",
                    "dispose_op",
                    "blend_op",
                    "data_source",
                    "full_canvas",
                    "pixel_hash",
                ]
            }
            for frame in decoded["frames"]
        ],
    }


def _compact_apng_import_result(result: dict) -> dict:
    return {
        "ok": result["ok"],
        "asset": result.get("asset"),
        "decoded_apng": result.get("decoded_apng"),
        "validation": result.get("validation"),
        "apng_policy": result.get("apng_policy"),
        "semantic_fidelity": result.get("semantic_fidelity", 0.0),
        "frame_pixel_fidelity": result.get("frame_pixel_fidelity", 0.0),
        "errors": result.get("errors", []),
        "error_families": result.get("error_families", []),
    }


def _validation_result(errors: list[dict]) -> dict:
    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "error_families": sorted({error["family"] for error in errors}),
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


def _mean(values) -> float:
    values = list(values)
    if not values:
        return 0.0
    return round(sum(values) / len(values), 6)


def _first_grid_path(profile: dict, generated_root: Path) -> Path:
    grid_paths = sorted((generated_root / profile["profile_id"]).glob("*.json"))
    if not grid_paths:
        raise ValueError(f"no generated grids found for profile: {profile['profile_id']}")
    return grid_paths[0]


def _json_report(report: dict) -> dict:
    payload = deepcopy(report)
    for result in payload["apng_results"]:
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
                "apng_roundtrip_count",
                "apng_roundtrip_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "apng_summaries": [
            {
                "profile_id": result["profile_id"],
                "asset": result["asset"],
                "decoded_apng": result["decoded_apng"],
                "semantic_fidelity": result["semantic_fidelity"],
                "frame_pixel_fidelity": result["frame_pixel_fidelity"],
            }
            for result in json_report["apng_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# APNG Sidecar Decoder Stage 0\n\n"
        "Bounded APNG sidecar decoder for two full-canvas 8-bit RGBA source "
        "frames.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- APNG round-trip successes: {report['apng_roundtrip_success_count']}"
        f"/{report['apng_roundtrip_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- Mean semantic fidelity: {metrics['mean_semantic_fidelity']}\n"
        f"- Mean frame-pixel fidelity: {metrics['mean_frame_pixel_fidelity']}\n"
        f"- Decision: {report['decision']}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/workshop_editor/apng_sidecar_decoder_stage0"),
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
    report = run_apng_sidecar_decoder_lab(profile_paths, args.generated_root)
    write_apng_sidecar_decoder_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_APNG_SIDECAR_DECODER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
