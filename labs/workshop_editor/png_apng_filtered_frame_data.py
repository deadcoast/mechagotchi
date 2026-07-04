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

from png_chunk_reader import PNGChunkError, bounded_decompress, read_png_chunks
from standard_image_sidecar_decoder import PNG_SIGNATURE, render_grid_rgba_pixels


REPORT_PATH = ROOT / "data/workshop_editor/apng_filtered_frame_data_stage0.json"
DATA_PATH = ROOT / "data/workshop_editor/apng_filtered_frame_data.js"

FILTER_FDAT_CASE_IDS = [
    "filter_none_split_fdat",
    "filter_sub_split_fdat",
    "filter_up_split_fdat",
    "filter_average_split_fdat",
    "filter_paeth_split_fdat",
]

PNG_SOURCE_URL = "https://www.w3.org/TR/png-3/"
TRANSPARENT_BLACK = (0, 0, 0, 0)
BYTES_PER_PIXEL = 4


class APNGFilteredFrameDataError(ValueError):
    def __init__(self, family: str, message: str):
        super().__init__(message)
        self.family = family
        self.message = message


def export_apng_filtered_frame_data_cases(grid: dict, slip_profile: dict) -> list[dict]:
    width, height = grid["grid_size"]
    base_pixels = render_grid_rgba_pixels(grid)
    patch_width = min(5, max(1, width - 2))
    patch_height = min(4, max(1, height - 2))
    cases = []
    for filter_type, case_id in enumerate(FILTER_FDAT_CASE_IDS):
        patch_pixels = _patch_pixels(
            patch_width,
            patch_height,
            seed=f"{slip_profile['profile_id']}:{case_id}",
            alpha=255,
        )
        frames = [
            _frame("base", width, height, 0, 0, base_pixels, [0], 1, 5, 0, 0, 0),
            _frame(
                case_id,
                patch_width,
                patch_height,
                1,
                1,
                patch_pixels,
                [filter_type],
                1,
                10,
                0,
                0,
                2,
            ),
        ]
        png_bytes = _encode_apng(width, height, frames)
        expected = _simulate_source_playback(width, height, frames)
        decoded = decode_apng_filtered_frame_data(png_bytes)
        cases.append(
            {
                "case_id": case_id,
                "description": (
                    f"APNG partial frame with PNG filter type {filter_type} "
                    "and two fdAT chunks."
                ),
                "profile_id": slip_profile["profile_id"],
                "grid_id": grid["grid_id"],
                "filter_type": filter_type,
                "png_file_name": f"{slip_profile['profile_id']}_{case_id}.png",
                "png_bytes": png_bytes,
                "png_hash": _hash_bytes(png_bytes),
                "expected_patch_hash": _hash_pixels(patch_pixels),
                "expected_display_hashes": expected["display_hashes"],
                "expected_final_hash": expected["final_output_hash"],
                "decoded": decoded,
            }
        )
    return cases


def decode_apng_filtered_frame_data(png_bytes: bytes) -> dict:
    try:
        decoded = _decode_apng_filtered_frame_data(png_bytes)
        decoded["ok"] = True
        decoded["errors"] = []
        decoded["error_families"] = []
        return decoded
    except APNGFilteredFrameDataError as exc:
        return {
            "ok": False,
            "errors": [_error("apng.filtered_frame_data", exc.family, exc.message)],
            "error_families": [exc.family],
        }


def make_invalid_filter_probe(png_bytes: bytes) -> bytes:
    return _replace_fdat_raw(png_bytes, frame_number=1, mutate=lambda raw: bytes([5]) + raw[1:])


def make_truncated_scanline_probe(png_bytes: bytes) -> bytes:
    return _replace_fdat_raw(png_bytes, frame_number=1, mutate=lambda raw: raw[:-1])


def make_fdat_sequence_gap_probe(png_bytes: bytes) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    seen = 0
    updated = []
    for chunk in chunks:
        if chunk["type"] == "fdAT":
            seen += 1
            if seen == 2:
                sequence_number = struct.unpack(">I", chunk["data"][:4])[0]
                chunk = _chunk(
                    "fdAT",
                    struct.pack(">I", sequence_number + 1) + chunk["data"][4:],
                )
        updated.append(chunk)
    if seen < 2:
        raise APNGFilteredFrameDataError(
            "apng_fdat_missing",
            "expected at least two fdAT chunks",
        )
    return _write_png_chunks(updated)


def make_missing_fdat_continuation_probe(png_bytes: bytes) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    seen = 0
    updated = []
    for chunk in chunks:
        if chunk["type"] == "fdAT":
            seen += 1
            if seen == 2:
                continue
        updated.append(chunk)
    if seen < 2:
        raise APNGFilteredFrameDataError(
            "apng_fdat_missing",
            "expected at least two fdAT chunks",
        )
    return _write_png_chunks(updated)


def run_apng_filtered_frame_data_lab(
    profile_paths: list[Path],
    generated_root: Path,
) -> dict:
    case_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid = _read_json(_first_grid_path(profile, generated_root))
        for case in export_apng_filtered_frame_data_cases(grid, profile):
            decoded = case["decoded"]
            success = (
                decoded["ok"]
                and decoded["display_hashes"] == case["expected_display_hashes"]
                and decoded["final_output_hash"] == case["expected_final_hash"]
                and decoded["frames"][1]["pixel_hash"] == case["expected_patch_hash"]
                and decoded["frames"][1]["fdat_chunk_count"] == 2
                and decoded["frames"][1]["filter_types_seen"] == [case["filter_type"]]
            )
            case_results.append(
                {
                    "profile_id": profile["profile_id"],
                    "grid_id": grid["grid_id"],
                    "case_id": case["case_id"],
                    "description": case["description"],
                    "filter_type": case["filter_type"],
                    "png_file_name": case["png_file_name"],
                    "png_hash": case["png_hash"],
                    "png_bytes_hex": case["png_bytes"].hex(),
                    "expected_patch_hash": case["expected_patch_hash"],
                    "expected_display_hashes": case["expected_display_hashes"],
                    "expected_final_hash": case["expected_final_hash"],
                    "decoded": _compact_decoded(decoded),
                    "success": success,
                }
            )

    invalid_results = _invalid_probe_results(case_results)
    success_count = sum(1 for result in case_results if result["success"])
    invalid_rejected_count = sum(1 for result in invalid_results if result["rejected"])
    return {
        "artifact_id": "apng_filtered_frame_data_stage0",
        "status": "research_apng_filtered_frame_data_no_package_code",
        "profile_count": len(profile_paths),
        "case_ids": list(FILTER_FDAT_CASE_IDS),
        "case_count": len(case_results),
        "case_success_count": success_count,
        "invalid_probe_count": len(invalid_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "case_results": case_results,
        "invalid_probe_results": invalid_results,
        "metrics": {
            "case_success_rate": _ratio(success_count, len(case_results)),
            "invalid_probe_rejection_rate": _ratio(
                invalid_rejected_count,
                len(invalid_results),
            ),
            "profile_coverage": len({result["profile_id"] for result in case_results}),
            "filter_family_count": len(FILTER_FDAT_CASE_IDS),
            "split_fdat_frames": sum(
                1 for result in case_results if result["decoded"]["frames"][1]["fdat_chunk_count"] == 2
            ),
        },
        "closed_states": [
            "apng_filter_method_0_frame_reconstruction",
            "apng_split_fdat_frame_data_reconstruction",
            "apng_filtered_partial_frame_source_playback",
            "apng_filtered_frame_invalid_data_rejection",
        ],
        "blocked_states": [
            "full_apng_png_conformance",
            "live_external_editor_rewrite_validation",
            "production_import_export_carrier_selection_final_decision",
            "manual_readability_calibration",
            "package_runtime_lifecycle_integration",
        ],
        "spec_sources": [
            {
                "name": "Portable Network Graphics (PNG) Specification, Third Edition",
                "url": PNG_SOURCE_URL,
                "used_for": (
                    "PNG filter method 0 filter functions, zlib image-data streams, "
                    "fdAT frame-data concatenation, and APNG frame-data inheritance."
                ),
            }
        ],
        "decision": "prototype_apng_filtered_frame_data_subset",
        "notes": [
            "This lab validates deterministic 8-bit RGBA non-interlaced APNG frames only.",
            "It covers filter method 0 filter types 0..4 on split-fdAT APNG frames.",
            "It does not claim full APNG/PNG conformance, live editor preservation, or final production carrier selection.",
        ],
    }


def write_apng_filtered_frame_data_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    cases_dir = output_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "apng_filtered_frame_data_stage0.json", _json_report(report))
    for result in report["case_results"]:
        (cases_dir / result["png_file_name"]).write_bytes(
            bytes.fromhex(result["png_bytes_hex"])
        )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "apng_filtered_frame_data.js").write_text(
        "window.MECHAGOTCHI_APNG_FILTERED_FRAME_DATA = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _decode_apng_filtered_frame_data(png_bytes: bytes) -> dict:
    chunks = _read_png_chunks(png_bytes)
    if not chunks or chunks[0]["type"] != "IHDR":
        raise APNGFilteredFrameDataError("png_ihdr_missing", "PNG IHDR chunk must be first")
    canvas = _decode_ihdr(chunks[0]["data"])
    names = [chunk["type"] for chunk in chunks]
    actl_chunks = [chunk for chunk in chunks if chunk["type"] == "acTL"]
    if len(actl_chunks) != 1:
        raise APNGFilteredFrameDataError("apng_control_missing", "APNG acTL chunk must be present and unique")
    if "IDAT" not in names:
        raise APNGFilteredFrameDataError("apng_idat_missing", "APNG default IDAT chunk must be present")
    if names.index("acTL") > names.index("IDAT"):
        raise APNGFilteredFrameDataError("apng_actl_after_idat", "APNG acTL must appear before IDAT")
    if len(actl_chunks[0]["data"]) != 8:
        raise APNGFilteredFrameDataError("apng_actl_invalid", "APNG acTL chunk must be 8 bytes")
    expected_frame_count, num_plays = struct.unpack(">II", actl_chunks[0]["data"])
    if expected_frame_count <= 0:
        raise APNGFilteredFrameDataError("apng_frame_count_invalid", "APNG frame count must be positive")

    frames = []
    current = None
    expected_sequence = 0
    idat_seen = False
    animation_chunk_order = []
    sequence_numbers = []
    for chunk in chunks[1:]:
        chunk_type = chunk["type"]
        if chunk_type == "fcTL":
            if current is not None:
                _append_frame(frames, current)
            control = _decode_fctl(chunk["data"])
            if control["sequence_number"] != expected_sequence:
                raise APNGFilteredFrameDataError(
                    "apng_sequence_number_invalid",
                    "APNG sequence numbers must be consecutive",
                )
            sequence_numbers.append(control["sequence_number"])
            expected_sequence += 1
            _validate_frame_control(control, canvas, default_frame=not idat_seen)
            current = {
                **control,
                "data": bytearray(),
                "data_source": None,
                "fdat_chunk_count": 0,
            }
            animation_chunk_order.append("fcTL")
        elif chunk_type == "IDAT":
            if current is None:
                raise APNGFilteredFrameDataError(
                    "apng_default_frame_unsupported",
                    "Stage 0 filtered frame data requires fcTL before default IDAT",
                )
            if current["data_source"] not in {None, "IDAT"}:
                raise APNGFilteredFrameDataError("apng_idat_order_invalid", "IDAT order is invalid")
            current["data"].extend(chunk["data"])
            current["data_source"] = "IDAT"
            idat_seen = True
            animation_chunk_order.append("IDAT")
        elif chunk_type == "fdAT":
            if current is None:
                raise APNGFilteredFrameDataError("apng_fdat_without_fctl", "fdAT requires preceding fcTL")
            if not idat_seen:
                raise APNGFilteredFrameDataError("apng_fdat_before_idat", "fdAT must not precede IDAT")
            if len(chunk["data"]) < 4:
                raise APNGFilteredFrameDataError("apng_fdat_invalid", "fdAT chunk must include a sequence number")
            sequence_number = struct.unpack(">I", chunk["data"][:4])[0]
            if sequence_number != expected_sequence:
                raise APNGFilteredFrameDataError(
                    "apng_sequence_number_invalid",
                    "APNG sequence numbers must be consecutive",
                )
            sequence_numbers.append(sequence_number)
            expected_sequence += 1
            current["data"].extend(chunk["data"][4:])
            current["data_source"] = "fdAT"
            current["fdat_chunk_count"] += 1
            animation_chunk_order.append("fdAT")
        elif chunk_type == "IEND":
            break

    if current is not None:
        _append_frame(frames, current)
    if len(frames) != expected_frame_count:
        raise APNGFilteredFrameDataError("apng_frame_count_mismatch", "acTL frame count does not match fcTL chunks")

    playback = _simulate_source_playback(canvas["width"], canvas["height"], frames)
    return {
        "canvas_width": canvas["width"],
        "canvas_height": canvas["height"],
        "animation_control": {
            "num_frames": expected_frame_count,
            "num_plays": num_plays,
        },
        "frame_count": len(frames),
        "sequence_numbers": sequence_numbers,
        "frames": [
            _frame_summary(frame, index, canvas["width"], canvas["height"])
            for index, frame in enumerate(frames)
        ],
        "chunks": names,
        "animation_chunk_order": animation_chunk_order,
        **playback,
    }


def _append_frame(frames: list[dict], frame: dict) -> None:
    if not frame["data"]:
        raise APNGFilteredFrameDataError("apng_frame_data_missing", "APNG frame has no image data")
    try:
        raw = bounded_decompress(bytes(frame["data"]), (frame["width"] * 4 + 1) * frame["height"])
    except PNGChunkError as exc:
        raise APNGFilteredFrameDataError("apng_frame_decompression_failed", exc.message) from exc
    decoded = _decode_filtered_rgba_scanlines(frame["width"], frame["height"], raw)
    frame["pixels"] = decoded["pixels"]
    frame["filter_types_seen"] = decoded["filter_types_seen"]
    frames.append(frame)


def _validate_frame_control(frame: dict, canvas: dict, *, default_frame: bool) -> None:
    if frame["width"] <= 0 or frame["height"] <= 0:
        raise APNGFilteredFrameDataError("apng_frame_dimensions_invalid", "APNG frame dimensions must be positive")
    if frame["x_offset"] + frame["width"] > canvas["width"] or frame["y_offset"] + frame["height"] > canvas["height"]:
        raise APNGFilteredFrameDataError("apng_frame_bounds_invalid", "APNG frame bounds exceed the canvas")
    if frame["dispose_op"] not in {0, 1, 2}:
        raise APNGFilteredFrameDataError("apng_dispose_op_invalid", "APNG dispose_op must be 0, 1, or 2")
    if frame["blend_op"] not in {0, 1}:
        raise APNGFilteredFrameDataError("apng_blend_op_invalid", "APNG blend_op must be 0 or 1")
    if frame["dispose_op"] != 0:
        # _simulate_source_playback implements source playback only; letting
        # dispose background/previous frames through would silently produce
        # spec-incorrect display hashes instead of a typed rejection.
        raise APNGFilteredFrameDataError(
            "apng_dispose_op_unsupported",
            "Stage 0 filtered frame data plays back dispose_op none only",
        )
    if frame["blend_op"] != 0:
        raise APNGFilteredFrameDataError(
            "apng_blend_op_unsupported",
            "Stage 0 filtered frame data plays back blend_op source only",
        )
    if default_frame and (
        frame["x_offset"] != 0
        or frame["y_offset"] != 0
        or frame["width"] != canvas["width"]
        or frame["height"] != canvas["height"]
    ):
        raise APNGFilteredFrameDataError(
            "apng_default_frame_control_invalid",
            "APNG default image frame must cover the full canvas",
        )


def _simulate_source_playback(width: int, height: int, frames: list[dict]) -> dict:
    output = [TRANSPARENT_BLACK for _ in range(width * height)]
    display_hashes = []
    for frame in frames:
        for y in range(frame["height"]):
            for x in range(frame["width"]):
                source = frame["pixels"][y * frame["width"] + x]
                destination_index = (frame["y_offset"] + y) * width + frame["x_offset"] + x
                output[destination_index] = source
        display_hashes.append(_hash_pixels(output))
    return {
        "display_hashes": display_hashes,
        "final_output_hash": display_hashes[-1] if display_hashes else _hash_pixels(output),
    }


def _encode_apng(width: int, height: int, frames: list[dict]) -> bytes:
    chunks = [
        _chunk("IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)),
        _chunk("acTL", struct.pack(">II", len(frames), 0)),
    ]
    sequence_number = 0
    for index, frame in enumerate(frames):
        chunks.append(_chunk("fcTL", _pack_fctl({**frame, "sequence_number": sequence_number})))
        sequence_number += 1
        raw = _filtered_rgba_scanlines(frame["width"], frame["height"], frame["pixels"], frame["filter_types"])
        compressed = zlib.compress(raw)
        if index == 0:
            chunks.append(_chunk("IDAT", compressed))
        else:
            for part in _split_payload(compressed, frame["fdat_split_count"]):
                chunks.append(_chunk("fdAT", struct.pack(">I", sequence_number) + part))
                sequence_number += 1
    chunks.append(_chunk("IEND", b""))
    return _write_png_chunks(chunks)


def _frame(
    frame_id: str,
    width: int,
    height: int,
    x_offset: int,
    y_offset: int,
    pixels: list[tuple[int, int, int, int]],
    filter_types: list[int],
    delay_num: int,
    delay_den: int,
    dispose_op: int,
    blend_op: int,
    fdat_split_count: int,
) -> dict:
    return {
        "frame_id": frame_id,
        "width": width,
        "height": height,
        "x_offset": x_offset,
        "y_offset": y_offset,
        "pixels": pixels,
        "filter_types": filter_types,
        "delay_num": delay_num,
        "delay_den": delay_den,
        "dispose_op": dispose_op,
        "blend_op": blend_op,
        "fdat_split_count": fdat_split_count,
    }


def _patch_pixels(width: int, height: int, *, seed: str, alpha: int) -> list[tuple[int, int, int, int]]:
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    pixels = []
    for index in range(width * height):
        red = (digest[index % len(digest)] + index * 29) % 256
        green = (digest[(index + 5) % len(digest)] + index * 31) % 256
        blue = (digest[(index + 11) % len(digest)] + index * 37) % 256
        pixels.append((red, green, blue, alpha))
    return pixels


def _filtered_rgba_scanlines(
    width: int,
    height: int,
    pixels: list[tuple[int, int, int, int]],
    filter_types: list[int],
) -> bytes:
    if len(pixels) != width * height:
        raise ValueError("pixel count does not match APNG frame dimensions")
    payload = bytearray()
    previous = None
    for y in range(height):
        filter_type = filter_types[y % len(filter_types)]
        row = bytes(channel for pixel in pixels[y * width : (y + 1) * width] for channel in pixel)
        payload.append(filter_type)
        payload.extend(_filter_row(row, previous, filter_type))
        previous = row
    return bytes(payload)


def _filter_row(row: bytes, previous: bytes | None, filter_type: int) -> bytes:
    filtered = bytearray()
    for index, value in enumerate(row):
        left = row[index - BYTES_PER_PIXEL] if index >= BYTES_PER_PIXEL else 0
        up = previous[index] if previous is not None else 0
        upper_left = previous[index - BYTES_PER_PIXEL] if previous is not None and index >= BYTES_PER_PIXEL else 0
        if filter_type == 0:
            predictor = 0
        elif filter_type == 1:
            predictor = left
        elif filter_type == 2:
            predictor = up
        elif filter_type == 3:
            predictor = (left + up) // 2
        elif filter_type == 4:
            predictor = _paeth_predictor(left, up, upper_left)
        else:
            raise ValueError(f"unsupported filter type: {filter_type}")
        filtered.append((value - predictor) % 256)
    return bytes(filtered)


def _decode_filtered_rgba_scanlines(width: int, height: int, raw: bytes) -> dict:
    stride = width * BYTES_PER_PIXEL
    expected = (stride + 1) * height
    if len(raw) != expected:
        raise APNGFilteredFrameDataError("apng_scanline_length_mismatch", "APNG frame scanline length does not match dimensions")
    pixels = []
    filter_types_seen = []
    offset = 0
    previous = None
    for _y in range(height):
        filter_type = raw[offset]
        offset += 1
        if filter_type > 4:
            raise APNGFilteredFrameDataError("apng_filter_type_invalid", "PNG filter method 0 supports filter types 0..4")
        row = raw[offset : offset + stride]
        offset += stride
        reconstructed = _unfilter_row(row, previous, filter_type)
        previous = reconstructed
        if filter_type not in filter_types_seen:
            filter_types_seen.append(filter_type)
        for x in range(width):
            index = x * BYTES_PER_PIXEL
            pixels.append(tuple(reconstructed[index : index + BYTES_PER_PIXEL]))
    return {"pixels": pixels, "filter_types_seen": filter_types_seen}


def _unfilter_row(row: bytes, previous: bytes | None, filter_type: int) -> bytes:
    reconstructed = bytearray()
    for index, value in enumerate(row):
        left = reconstructed[index - BYTES_PER_PIXEL] if index >= BYTES_PER_PIXEL else 0
        up = previous[index] if previous is not None else 0
        upper_left = previous[index - BYTES_PER_PIXEL] if previous is not None and index >= BYTES_PER_PIXEL else 0
        if filter_type == 0:
            predictor = 0
        elif filter_type == 1:
            predictor = left
        elif filter_type == 2:
            predictor = up
        elif filter_type == 3:
            predictor = (left + up) // 2
        else:
            predictor = _paeth_predictor(left, up, upper_left)
        reconstructed.append((value + predictor) % 256)
    return bytes(reconstructed)


def _paeth_predictor(left: int, up: int, upper_left: int) -> int:
    estimate = left + up - upper_left
    distance_left = abs(estimate - left)
    distance_up = abs(estimate - up)
    distance_upper_left = abs(estimate - upper_left)
    if distance_left <= distance_up and distance_left <= distance_upper_left:
        return left
    if distance_up <= distance_upper_left:
        return up
    return upper_left


def _replace_fdat_raw(png_bytes: bytes, *, frame_number: int, mutate) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    target_indexes = _fdat_indexes_for_frame(chunks, frame_number)
    compressed = b"".join(chunks[index]["data"][4:] for index in target_indexes)
    try:
        raw = zlib.decompress(compressed)
    except zlib.error as exc:
        raise APNGFilteredFrameDataError("apng_frame_decompression_failed", str(exc)) from exc
    replacement = zlib.compress(mutate(raw))
    parts = _split_payload(replacement, len(target_indexes))
    updated = list(chunks)
    for chunk_index, part in zip(target_indexes, parts):
        sequence_number = updated[chunk_index]["data"][:4]
        updated[chunk_index] = _chunk("fdAT", sequence_number + part)
    return _write_png_chunks(updated)


def _fdat_indexes_for_frame(chunks: list[dict], frame_number: int) -> list[int]:
    current_frame = -1
    indexes = []
    for index, chunk in enumerate(chunks):
        if chunk["type"] == "fcTL":
            current_frame += 1
        elif chunk["type"] == "fdAT" and current_frame == frame_number:
            indexes.append(index)
    if not indexes:
        raise APNGFilteredFrameDataError("apng_fdat_missing", "target frame has no fdAT chunks")
    return indexes


def _decode_ihdr(data: bytes) -> dict:
    if len(data) != 13:
        raise APNGFilteredFrameDataError("png_ihdr_invalid", "PNG IHDR chunk length must be 13")
    width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(">IIBBBBB", data)
    if width <= 0 or height <= 0:
        raise APNGFilteredFrameDataError("png_ihdr_invalid", "PNG dimensions must be positive")
    if bit_depth != 8 or color_type != 6 or compression != 0 or filter_method != 0 or interlace != 0:
        raise APNGFilteredFrameDataError(
            "apng_color_model_unsupported",
            "Stage 0 filtered frame data supports non-interlaced 8-bit RGBA APNG only",
        )
    return {"width": width, "height": height}


def _decode_fctl(data: bytes) -> dict:
    if len(data) != 26:
        raise APNGFilteredFrameDataError("apng_fctl_invalid", "APNG fcTL chunk length must be 26")
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


def _pack_fctl(frame: dict) -> bytes:
    return struct.pack(
        ">IIIIIHHBB",
        frame["sequence_number"],
        frame["width"],
        frame["height"],
        frame["x_offset"],
        frame["y_offset"],
        frame["delay_num"],
        frame["delay_den"],
        frame["dispose_op"],
        frame["blend_op"],
    )


def _read_png_chunks(png_bytes: bytes) -> list[dict]:
    try:
        parsed = read_png_chunks(png_bytes)
    except PNGChunkError as exc:
        raise APNGFilteredFrameDataError(exc.family, exc.message) from exc
    return [{"type": chunk["type"], "data": chunk["payload"]} for chunk in parsed]


def _chunk(chunk_type: str, data: bytes) -> dict:
    return {"type": chunk_type, "data": data}


def _write_png_chunks(chunks: list[dict]) -> bytes:
    payload = bytearray(PNG_SIGNATURE)
    for chunk in chunks:
        chunk_type = chunk["type"].encode("ascii")
        data = chunk["data"]
        crc = binascii.crc32(data, binascii.crc32(chunk_type)) & 0xFFFFFFFF
        payload.extend(struct.pack(">I", len(data)))
        payload.extend(chunk_type)
        payload.extend(data)
        payload.extend(struct.pack(">I", crc))
    return bytes(payload)


def _invalid_probe_results(case_results: list[dict]) -> list[dict]:
    reference = bytes.fromhex(case_results[0]["png_bytes_hex"])
    probes = [
        ("invalid_filter", make_invalid_filter_probe(reference), "apng_filter_type_invalid"),
        ("truncated_scanline", make_truncated_scanline_probe(reference), "apng_scanline_length_mismatch"),
        ("fdat_sequence_gap", make_fdat_sequence_gap_probe(reference), "apng_sequence_number_invalid"),
        ("missing_fdat_continuation", make_missing_fdat_continuation_probe(reference), "apng_frame_decompression_failed"),
    ]
    results = []
    for probe_id, png_bytes, expected_family in probes:
        decoded = decode_apng_filtered_frame_data(png_bytes)
        results.append(
            {
                "probe_id": probe_id,
                "expected_family": expected_family,
                "rejected": not decoded["ok"] and expected_family in decoded["error_families"],
                "decoded": _compact_decoded(decoded),
            }
        )
    return results


def _frame_summary(frame: dict, index: int, canvas_width: int, canvas_height: int) -> dict:
    delay_den = frame["delay_den"] or 100
    return {
        "frame_index": index,
        "width": frame["width"],
        "height": frame["height"],
        "x_offset": frame["x_offset"],
        "y_offset": frame["y_offset"],
        "delay_num": frame["delay_num"],
        "delay_den": frame["delay_den"],
        "delay_ms": round((frame["delay_num"] / delay_den) * 1000),
        "dispose_op": frame["dispose_op"],
        "blend_op": frame["blend_op"],
        "data_source": frame["data_source"],
        "fdat_chunk_count": frame["fdat_chunk_count"],
        "filter_types_seen": frame["filter_types_seen"],
        "full_canvas": (
            frame["x_offset"] == 0
            and frame["y_offset"] == 0
            and frame["width"] == canvas_width
            and frame["height"] == canvas_height
        ),
        "pixel_hash": _hash_pixels(frame["pixels"]),
    }


def _compact_decoded(decoded: dict) -> dict:
    if not decoded.get("ok"):
        return {
            "ok": False,
            "errors": decoded.get("errors", []),
            "error_families": decoded.get("error_families", []),
        }
    return {
        key: decoded[key]
        for key in [
            "ok",
            "canvas_width",
            "canvas_height",
            "animation_control",
            "frame_count",
            "sequence_numbers",
            "frames",
            "animation_chunk_order",
            "display_hashes",
            "final_output_hash",
        ]
    }


def _json_report(report: dict) -> dict:
    payload = deepcopy(report)
    for result in payload["case_results"]:
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
                "case_ids",
                "case_count",
                "case_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "case_summaries": [
            {
                "profile_id": result["profile_id"],
                "grid_id": result["grid_id"],
                "case_id": result["case_id"],
                "filter_type": result["filter_type"],
                "png_file_name": result["png_file_name"],
                "png_hash": result["png_hash"],
                "decoded": result["decoded"],
                "success": result["success"],
            }
            for result in json_report["case_results"]
        ],
        "invalid_probe_results": json_report["invalid_probe_results"],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# APNG Filtered Frame Data Stage 0\n\n"
        "Bounded APNG filter-method-0 and split-fdAT frame-data matrix for "
        "Mechagotchi workshop carriers.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Case successes: {report['case_success_count']}/{report['case_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- Success rate: {metrics['case_success_rate']}\n"
        f"- Invalid rejection rate: {metrics['invalid_probe_rejection_rate']}\n\n"
        "This is a deterministic 8-bit RGBA non-interlaced APNG subset. It "
        "does not prove full APNG/PNG conformance, live editor rewrite "
        "preservation, or final production carrier selection.\n"
    )


def _split_payload(payload: bytes, count: int) -> list[bytes]:
    if count <= 1:
        return [payload]
    midpoint = max(1, len(payload) // 2)
    return [payload[:midpoint], payload[midpoint:]]


def _error(path: str, family: str, message: str | None = None) -> dict:
    return {
        "path": path,
        "family": family,
        "message": message or family.replace("_", " "),
    }


def _hash_pixels(pixels: list[tuple[int, int, int, int]]) -> str:
    return _hash_bytes(bytes(channel for pixel in pixels for channel in pixel))


def _hash_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _first_grid_path(profile: dict, generated_root: Path) -> Path:
    grid_paths = sorted((generated_root / profile["profile_id"]).glob("*.json"))
    if not grid_paths:
        raise ValueError(f"no generated grids found for profile: {profile['profile_id']}")
    return grid_paths[0]


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "data/workshop_editor/apng_filtered_frame_data_stage0",
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
    report = run_apng_filtered_frame_data_lab(profile_paths, args.generated_root)
    write_apng_filtered_frame_data_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_APNG_FILTERED_FRAME_DATA = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
