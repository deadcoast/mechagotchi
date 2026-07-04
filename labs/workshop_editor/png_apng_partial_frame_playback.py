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


REPORT_PATH = Path("data/workshop_editor/apng_partial_frame_playback_stage0.json")
DATA_PATH = Path("data/workshop_editor/apng_partial_frame_playback_data.js")

PLAYBACK_SCENARIO_IDS = [
    "source_patch_dispose_none",
    "over_patch_dispose_none",
    "background_disposal",
    "previous_disposal",
]

PNG_SOURCE_URL = "https://www.w3.org/TR/png-3/"
TRANSPARENT_BLACK = (0, 0, 0, 0)


class APNGPartialFramePlaybackError(ValueError):
    def __init__(self, family: str, message: str):
        super().__init__(message)
        self.family = family
        self.message = message


def export_apng_partial_frame_playback_cases(grid: dict, slip_profile: dict) -> list[dict]:
    width, height = grid["grid_size"]
    base_pixels = render_grid_rgba_pixels(grid)
    patch_width = min(3, max(1, width - 2))
    patch_height = min(3, max(1, height - 2))
    secondary_x = min(width - patch_width, 3)
    secondary_y = min(height - patch_height, 3)
    patch_a = _patch_pixels(
        patch_width,
        patch_height,
        seed=slip_profile["profile_id"] + ":a",
        alpha=255,
    )
    patch_a_over = _patch_pixels(
        patch_width,
        patch_height,
        seed=slip_profile["profile_id"] + ":over",
        alpha=128,
    )
    patch_b = _patch_pixels(
        patch_width,
        patch_height,
        seed=slip_profile["profile_id"] + ":b",
        alpha=230,
    )

    scenarios = [
        (
            "source_patch_dispose_none",
            "Partial source-blend patch with dispose none.",
            [
                _frame("base", width, height, 0, 0, base_pixels, 1, 5, 0, 0),
                _frame("source_patch", patch_width, patch_height, 1, 1, patch_a, 1, 10, 0, 0),
            ],
        ),
        (
            "over_patch_dispose_none",
            "Partial alpha-over patch with dispose none.",
            [
                _frame("base", width, height, 0, 0, base_pixels, 1, 5, 0, 0),
                _frame("over_patch", patch_width, patch_height, 1, 1, patch_a_over, 1, 10, 0, 1),
            ],
        ),
        (
            "background_disposal",
            "Partial patch clears its region to transparent black before the next frame.",
            [
                _frame("base", width, height, 0, 0, base_pixels, 1, 5, 0, 0),
                _frame("clear_after_patch", patch_width, patch_height, 1, 1, patch_a, 1, 10, 1, 0),
                _frame("post_clear_patch", patch_width, patch_height, secondary_x, secondary_y, patch_b, 1, 10, 0, 0),
            ],
        ),
        (
            "previous_disposal",
            "Partial patch restores the previous output buffer before the next frame.",
            [
                _frame("base", width, height, 0, 0, base_pixels, 1, 5, 0, 0),
                _frame("restore_after_patch", patch_width, patch_height, 1, 1, patch_a, 1, 10, 2, 0),
                _frame("post_restore_patch", patch_width, patch_height, secondary_x, secondary_y, patch_b, 1, 10, 0, 0),
            ],
        ),
    ]

    cases = []
    for scenario_id, description, frames in scenarios:
        png_bytes = _encode_apng(width, height, frames)
        expected = _simulate_playback(width, height, frames)
        decoded = decode_apng_partial_frame_playback(png_bytes)
        cases.append(
            {
                "scenario_id": scenario_id,
                "description": description,
                "profile_id": slip_profile["profile_id"],
                "grid_id": grid["grid_id"],
                "png_file_name": f"{slip_profile['profile_id']}_{scenario_id}.png",
                "png_bytes": png_bytes,
                "png_hash": _hash_bytes(png_bytes),
                "expected_display_hashes": expected["display_hashes"],
                "expected_after_dispose_hashes": expected["after_dispose_hashes"],
                "expected_final_hash": expected["final_output_hash"],
                "decoded": decoded,
            }
        )
    return cases


def decode_apng_partial_frame_playback(png_bytes: bytes) -> dict:
    try:
        decoded = _decode_apng_partial_frame_playback(png_bytes)
        decoded["ok"] = True
        decoded["errors"] = []
        decoded["error_families"] = []
        return decoded
    except APNGPartialFramePlaybackError as exc:
        return {
            "ok": False,
            "errors": [_error("apng.partial_frame", exc.family, exc.message)],
            "error_families": [exc.family],
        }


def make_out_of_bounds_probe(png_bytes: bytes) -> bytes:
    def mutate(frame: dict, canvas: dict) -> dict:
        frame["x_offset"] = canvas["width"]
        return frame

    return _rewrite_fctl(png_bytes, frame_number=1, mutate=mutate)


def make_invalid_dispose_probe(png_bytes: bytes) -> bytes:
    return _rewrite_fctl(
        png_bytes,
        frame_number=1,
        mutate=lambda frame, _canvas: {**frame, "dispose_op": 3},
    )


def make_invalid_blend_probe(png_bytes: bytes) -> bytes:
    return _rewrite_fctl(
        png_bytes,
        frame_number=1,
        mutate=lambda frame, _canvas: {**frame, "blend_op": 2},
    )


def make_missing_default_idat_probe(png_bytes: bytes) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    removed = False
    updated = []
    for chunk in chunks:
        if chunk["type"] == "IDAT" and not removed:
            removed = True
            continue
        updated.append(chunk)
    if not removed:
        raise APNGPartialFramePlaybackError("apng_idat_missing", "no IDAT chunk to remove")
    return _write_png_chunks(updated)


def make_missing_frame_data_probe(png_bytes: bytes) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    removed = False
    updated = []
    for chunk in chunks:
        if chunk["type"] == "fdAT" and not removed:
            removed = True
            continue
        updated.append(chunk)
    if not removed:
        raise APNGPartialFramePlaybackError("apng_fdat_missing", "no fdAT chunk to remove")
    return _write_png_chunks(updated)


def run_apng_partial_frame_playback_lab(
    profile_paths: list[Path],
    generated_root: Path,
) -> dict:
    playback_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid = _read_json(_first_grid_path(profile, generated_root))
        for case in export_apng_partial_frame_playback_cases(grid, profile):
            decoded = case["decoded"]
            success = (
                decoded["ok"]
                and decoded["display_hashes"] == case["expected_display_hashes"]
                and decoded["after_dispose_hashes"] == case["expected_after_dispose_hashes"]
                and decoded["final_output_hash"] == case["expected_final_hash"]
            )
            playback_results.append(
                {
                    "profile_id": profile["profile_id"],
                    "grid_id": grid["grid_id"],
                    "scenario_id": case["scenario_id"],
                    "description": case["description"],
                    "png_file_name": case["png_file_name"],
                    "png_hash": case["png_hash"],
                    "png_bytes_hex": case["png_bytes"].hex(),
                    "expected_display_hashes": case["expected_display_hashes"],
                    "expected_after_dispose_hashes": case["expected_after_dispose_hashes"],
                    "expected_final_hash": case["expected_final_hash"],
                    "decoded": _compact_decoded(decoded),
                    "success": success,
                }
            )

    invalid_results = _invalid_probe_results(playback_results)
    success_count = sum(1 for result in playback_results if result["success"])
    invalid_rejected_count = sum(1 for result in invalid_results if result["rejected"])
    return {
        "artifact_id": "apng_partial_frame_playback_stage0",
        "status": "research_apng_partial_frame_playback_no_package_code",
        "profile_count": len(profile_paths),
        "playback_scenario_ids": list(PLAYBACK_SCENARIO_IDS),
        "playback_case_count": len(playback_results),
        "playback_case_success_count": success_count,
        "invalid_probe_count": len(invalid_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "playback_results": playback_results,
        "invalid_probe_results": invalid_results,
        "metrics": {
            "playback_case_success_rate": _ratio(success_count, len(playback_results)),
            "invalid_probe_rejection_rate": _ratio(invalid_rejected_count, len(invalid_results)),
            "profile_coverage": len({result["profile_id"] for result in playback_results}),
            "scenario_family_count": len(PLAYBACK_SCENARIO_IDS),
        },
        "closed_states": [
            "apng_partial_frame_offset_playback",
            "apng_blend_source_over_playback",
            "apng_dispose_background_previous_playback",
            "apng_partial_frame_invalid_control_rejection",
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
                "used_for": "APNG output buffer, frame offsets, source/over blend operations, dispose none/background/previous behavior, and frame-control validation.",
            }
        ],
        "decision": "prototype_apng_partial_frame_playback_subset",
        "notes": [
            "This lab validates deterministic 8-bit RGBA partial-frame playback only.",
            "It does not claim full APNG/PNG conformance, live editor rewrite preservation, or final production carrier selection.",
        ],
    }


def write_apng_partial_frame_playback_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    cases_dir = output_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "apng_partial_frame_playback_stage0.json", _json_report(report))
    for result in report["playback_results"]:
        (cases_dir / result["png_file_name"]).write_bytes(
            bytes.fromhex(result["png_bytes_hex"])
        )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "apng_partial_frame_playback_data.js").write_text(
        "window.MECHAGOTCHI_APNG_PARTIAL_FRAME_PLAYBACK = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _decode_apng_partial_frame_playback(png_bytes: bytes) -> dict:
    chunks = _read_png_chunks(png_bytes)
    if not chunks or chunks[0]["type"] != "IHDR":
        raise APNGPartialFramePlaybackError("png_ihdr_missing", "PNG IHDR chunk must be first")
    canvas = _decode_ihdr(chunks[0]["data"])
    names = [chunk["type"] for chunk in chunks]
    actl_chunks = [chunk for chunk in chunks if chunk["type"] == "acTL"]
    if len(actl_chunks) != 1:
        raise APNGPartialFramePlaybackError("apng_control_missing", "APNG acTL chunk must be present and unique")
    if "IDAT" not in names:
        raise APNGPartialFramePlaybackError("apng_idat_missing", "APNG default IDAT chunk must be present")
    if names.index("acTL") > names.index("IDAT"):
        raise APNGPartialFramePlaybackError("apng_actl_after_idat", "APNG acTL must appear before IDAT")
    if len(actl_chunks[0]["data"]) != 8:
        raise APNGPartialFramePlaybackError("apng_actl_invalid", "APNG acTL chunk must be 8 bytes")
    expected_frame_count, num_plays = struct.unpack(">II", actl_chunks[0]["data"])
    if expected_frame_count <= 0:
        raise APNGPartialFramePlaybackError("apng_frame_count_invalid", "APNG frame count must be positive")

    frames = []
    current = None
    expected_sequence = 0
    idat_seen = False
    animation_chunk_order = []
    for chunk in chunks[1:]:
        chunk_type = chunk["type"]
        if chunk_type == "fcTL":
            if current is not None:
                _append_frame(frames, current)
            control = _decode_fctl(chunk["data"])
            if control["sequence_number"] != expected_sequence:
                raise APNGPartialFramePlaybackError(
                    "apng_sequence_number_invalid",
                    "APNG sequence numbers must be consecutive",
                )
            expected_sequence += 1
            _validate_frame_control(control, canvas, default_frame=not idat_seen)
            current = {**control, "data": bytearray(), "data_source": None}
            animation_chunk_order.append("fcTL")
        elif chunk_type == "IDAT":
            if current is None:
                raise APNGPartialFramePlaybackError(
                    "apng_default_frame_unsupported",
                    "Stage 0 partial playback requires fcTL before default IDAT",
                )
            if current["data_source"] not in {None, "IDAT"}:
                raise APNGPartialFramePlaybackError("apng_idat_order_invalid", "IDAT order is invalid")
            current["data"].extend(chunk["data"])
            current["data_source"] = "IDAT"
            idat_seen = True
            animation_chunk_order.append("IDAT")
        elif chunk_type == "fdAT":
            if current is None:
                raise APNGPartialFramePlaybackError("apng_fdat_without_fctl", "fdAT requires preceding fcTL")
            if not idat_seen:
                raise APNGPartialFramePlaybackError("apng_fdat_before_idat", "fdAT must not precede IDAT")
            if len(chunk["data"]) < 4:
                raise APNGPartialFramePlaybackError("apng_fdat_invalid", "fdAT chunk must include a sequence number")
            sequence_number = struct.unpack(">I", chunk["data"][:4])[0]
            if sequence_number != expected_sequence:
                raise APNGPartialFramePlaybackError(
                    "apng_sequence_number_invalid",
                    "APNG sequence numbers must be consecutive",
                )
            expected_sequence += 1
            current["data"].extend(chunk["data"][4:])
            current["data_source"] = "fdAT"
            animation_chunk_order.append("fdAT")
        elif chunk_type == "IEND":
            break

    if current is not None:
        _append_frame(frames, current)
    if len(frames) != expected_frame_count:
        raise APNGPartialFramePlaybackError("apng_frame_count_mismatch", "acTL frame count does not match fcTL chunks")

    playback = _simulate_playback(canvas["width"], canvas["height"], frames)
    return {
        "canvas_width": canvas["width"],
        "canvas_height": canvas["height"],
        "animation_control": {
            "num_frames": expected_frame_count,
            "num_plays": num_plays,
        },
        "frame_count": len(frames),
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
        raise APNGPartialFramePlaybackError("apng_frame_data_missing", "APNG frame has no image data")
    try:
        raw = bounded_decompress(bytes(frame["data"]), (frame["width"] * 4 + 1) * frame["height"])
    except PNGChunkError as exc:
        raise APNGPartialFramePlaybackError("apng_frame_decompression_failed", exc.message) from exc
    frame["pixels"] = _decode_rgba_scanlines(frame["width"], frame["height"], raw)
    frames.append(frame)


def _validate_frame_control(frame: dict, canvas: dict, *, default_frame: bool) -> None:
    if frame["width"] <= 0 or frame["height"] <= 0:
        raise APNGPartialFramePlaybackError("apng_frame_dimensions_invalid", "APNG frame dimensions must be positive")
    if frame["x_offset"] + frame["width"] > canvas["width"] or frame["y_offset"] + frame["height"] > canvas["height"]:
        raise APNGPartialFramePlaybackError("apng_frame_bounds_invalid", "APNG frame bounds exceed the canvas")
    if frame["dispose_op"] not in {0, 1, 2}:
        raise APNGPartialFramePlaybackError("apng_dispose_op_invalid", "APNG dispose_op must be 0, 1, or 2")
    if frame["blend_op"] not in {0, 1}:
        raise APNGPartialFramePlaybackError("apng_blend_op_invalid", "APNG blend_op must be 0 or 1")
    if default_frame and (
        frame["x_offset"] != 0
        or frame["y_offset"] != 0
        or frame["width"] != canvas["width"]
        or frame["height"] != canvas["height"]
    ):
        raise APNGPartialFramePlaybackError(
            "apng_default_frame_control_invalid",
            "APNG default image frame must cover the full canvas",
        )


def _simulate_playback(width: int, height: int, frames: list[dict]) -> dict:
    output = [TRANSPARENT_BLACK for _ in range(width * height)]
    display_hashes = []
    after_dispose_hashes = []
    for index, frame in enumerate(frames):
        before = list(output)
        for y in range(frame["height"]):
            for x in range(frame["width"]):
                source = frame["pixels"][y * frame["width"] + x]
                destination_index = (frame["y_offset"] + y) * width + frame["x_offset"] + x
                if frame["blend_op"] == 0:
                    output[destination_index] = source
                else:
                    output[destination_index] = _alpha_over(source, output[destination_index])
        display_hashes.append(_hash_pixels(output))

        if frame["dispose_op"] == 1 or (frame["dispose_op"] == 2 and index == 0):
            for y in range(frame["height"]):
                for x in range(frame["width"]):
                    destination_index = (frame["y_offset"] + y) * width + frame["x_offset"] + x
                    output[destination_index] = TRANSPARENT_BLACK
        elif frame["dispose_op"] == 2:
            output = before
        after_dispose_hashes.append(_hash_pixels(output))
    return {
        "display_hashes": display_hashes,
        "after_dispose_hashes": after_dispose_hashes,
        "final_output_hash": after_dispose_hashes[-1] if after_dispose_hashes else _hash_pixels(output),
    }


def _alpha_over(source: tuple[int, int, int, int], destination: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    source_alpha = source[3] / 255
    dest_alpha = destination[3] / 255
    out_alpha = source_alpha + dest_alpha * (1 - source_alpha)
    if out_alpha <= 0:
        return TRANSPARENT_BLACK
    channels = []
    for index in range(3):
        value = (
            source[index] * source_alpha
            + destination[index] * dest_alpha * (1 - source_alpha)
        ) / out_alpha
        channels.append(round(value))
    channels.append(round(out_alpha * 255))
    return tuple(channels)


def _encode_apng(width: int, height: int, frames: list[dict]) -> bytes:
    chunks = [
        _chunk("IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)),
        _chunk("acTL", struct.pack(">II", len(frames), 0)),
    ]
    sequence_number = 0
    for index, frame in enumerate(frames):
        chunks.append(_chunk("fcTL", _pack_fctl({**frame, "sequence_number": sequence_number})))
        sequence_number += 1
        compressed = zlib.compress(_rgba_scanlines(frame["width"], frame["height"], frame["pixels"]))
        if index == 0:
            chunks.append(_chunk("IDAT", compressed))
        else:
            chunks.append(_chunk("fdAT", struct.pack(">I", sequence_number) + compressed))
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
    delay_num: int,
    delay_den: int,
    dispose_op: int,
    blend_op: int,
) -> dict:
    return {
        "frame_id": frame_id,
        "width": width,
        "height": height,
        "x_offset": x_offset,
        "y_offset": y_offset,
        "pixels": pixels,
        "delay_num": delay_num,
        "delay_den": delay_den,
        "dispose_op": dispose_op,
        "blend_op": blend_op,
    }


def _patch_pixels(width: int, height: int, *, seed: str, alpha: int) -> list[tuple[int, int, int, int]]:
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    pixels = []
    for index in range(width * height):
        red = (digest[index % len(digest)] + index * 17) % 256
        green = (digest[(index + 7) % len(digest)] + index * 23) % 256
        blue = (digest[(index + 13) % len(digest)] + index * 31) % 256
        pixels.append((red, green, blue, alpha))
    return pixels


def _decode_ihdr(data: bytes) -> dict:
    if len(data) != 13:
        raise APNGPartialFramePlaybackError("png_ihdr_invalid", "PNG IHDR chunk length must be 13")
    width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(">IIBBBBB", data)
    if width <= 0 or height <= 0:
        raise APNGPartialFramePlaybackError("png_ihdr_invalid", "PNG dimensions must be positive")
    if bit_depth != 8 or color_type != 6 or compression != 0 or filter_method != 0 or interlace != 0:
        raise APNGPartialFramePlaybackError(
            "apng_color_model_unsupported",
            "Stage 0 partial-frame playback supports non-interlaced 8-bit RGBA APNG only",
        )
    return {"width": width, "height": height}


def _decode_fctl(data: bytes) -> dict:
    if len(data) != 26:
        raise APNGPartialFramePlaybackError("apng_fctl_invalid", "APNG fcTL chunk length must be 26")
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


def _rgba_scanlines(width: int, height: int, pixels: list[tuple[int, int, int, int]]) -> bytes:
    if len(pixels) != width * height:
        raise ValueError("pixel count does not match APNG frame dimensions")
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
        raise APNGPartialFramePlaybackError("apng_scanline_length_mismatch", "APNG frame scanline length does not match dimensions")
    pixels = []
    offset = 0
    for _y in range(height):
        filter_type = raw[offset]
        offset += 1
        if filter_type != 0:
            raise APNGPartialFramePlaybackError("apng_filter_unsupported", "Stage 0 partial-frame playback supports filter type 0 only")
        row = raw[offset : offset + stride]
        offset += stride
        for x in range(width):
            index = x * 4
            pixels.append(tuple(row[index : index + 4]))
    return pixels


def _rewrite_fctl(png_bytes: bytes, *, frame_number: int, mutate) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    canvas = _decode_ihdr(chunks[0]["data"])
    seen = -1
    updated = []
    for chunk in chunks:
        if chunk["type"] == "fcTL":
            seen += 1
            if seen == frame_number:
                frame = _decode_fctl(chunk["data"])
                chunk = _chunk("fcTL", _pack_fctl(mutate(frame, canvas)))
        updated.append(chunk)
    if seen < frame_number:
        raise APNGPartialFramePlaybackError("apng_fctl_missing", "requested fcTL chunk is missing")
    return _write_png_chunks(updated)


def _read_png_chunks(png_bytes: bytes) -> list[dict]:
    try:
        parsed = read_png_chunks(png_bytes)
    except PNGChunkError as exc:
        raise APNGPartialFramePlaybackError(exc.family, exc.message) from exc
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


def _invalid_probe_results(playback_results: list[dict]) -> list[dict]:
    reference = bytes.fromhex(playback_results[0]["png_bytes_hex"])
    probes = [
        ("out_of_bounds", make_out_of_bounds_probe(reference), "apng_frame_bounds_invalid"),
        ("invalid_dispose", make_invalid_dispose_probe(reference), "apng_dispose_op_invalid"),
        ("invalid_blend", make_invalid_blend_probe(reference), "apng_blend_op_invalid"),
        ("missing_default_idat", make_missing_default_idat_probe(reference), "apng_idat_missing"),
        ("missing_frame_data", make_missing_frame_data_probe(reference), "apng_frame_data_missing"),
    ]
    results = []
    for probe_id, png_bytes, expected_family in probes:
        decoded = decode_apng_partial_frame_playback(png_bytes)
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
            "frames",
            "animation_chunk_order",
            "display_hashes",
            "after_dispose_hashes",
            "final_output_hash",
        ]
    }


def _json_report(report: dict) -> dict:
    payload = deepcopy(report)
    for result in payload["playback_results"]:
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
                "playback_scenario_ids",
                "playback_case_count",
                "playback_case_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "playback_summaries": [
            {
                "profile_id": result["profile_id"],
                "grid_id": result["grid_id"],
                "scenario_id": result["scenario_id"],
                "png_file_name": result["png_file_name"],
                "png_hash": result["png_hash"],
                "decoded": result["decoded"],
                "success": result["success"],
            }
            for result in json_report["playback_results"]
        ],
        "invalid_probe_results": json_report["invalid_probe_results"],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# APNG Partial Frame Playback Stage 0\n\n"
        "Bounded APNG partial-frame playback matrix for Mechagotchi workshop "
        "carriers.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Playback successes: {report['playback_case_success_count']}"
        f"/{report['playback_case_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- Success rate: {metrics['playback_case_success_rate']}\n"
        f"- Invalid rejection rate: {metrics['invalid_probe_rejection_rate']}\n\n"
        "This is a deterministic 8-bit RGBA partial-frame playback subset. It "
        "does not prove full APNG/PNG conformance, live editor rewrite "
        "preservation, or final production carrier selection.\n"
    )


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
        default=Path("data/workshop_editor/apng_partial_frame_playback_stage0"),
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
    report = run_apng_partial_frame_playback_lab(profile_paths, args.generated_root)
    write_apng_partial_frame_playback_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_APNG_PARTIAL_FRAME_PLAYBACK = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
