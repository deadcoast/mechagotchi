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


REPORT_PATH = ROOT / "data/workshop_editor/apng_color_type_frame_data_stage0.json"
DATA_PATH = ROOT / "data/workshop_editor/apng_color_type_frame_data.js"

COLOR_TYPE_CASE_IDS = [
    "grayscale8_fdat",
    "truecolor8_fdat",
    "indexed8_trns_fdat",
    "grayscale_alpha8_fdat",
    "truecolor_alpha8_fdat",
]

PNG_SOURCE_URL = "https://www.w3.org/TR/png-3/"
TRANSPARENT_BLACK = (0, 0, 0, 0)


COLOR_TYPE_CHANNELS = {
    0: 1,
    2: 3,
    3: 1,
    4: 2,
    6: 4,
}


CASE_SPECS = [
    {
        "case_id": "grayscale8_fdat",
        "color_type": 0,
        "description": "8-bit greyscale APNG frame data.",
    },
    {
        "case_id": "truecolor8_fdat",
        "color_type": 2,
        "description": "8-bit truecolor APNG frame data.",
    },
    {
        "case_id": "indexed8_trns_fdat",
        "color_type": 3,
        "description": "8-bit indexed-color APNG frame data with PLTE and tRNS.",
    },
    {
        "case_id": "grayscale_alpha8_fdat",
        "color_type": 4,
        "description": "8-bit greyscale-with-alpha APNG frame data.",
    },
    {
        "case_id": "truecolor_alpha8_fdat",
        "color_type": 6,
        "description": "8-bit truecolor-with-alpha APNG frame data.",
    },
]


class APNGColorTypeFrameDataError(ValueError):
    def __init__(self, family: str, message: str):
        super().__init__(message)
        self.family = family
        self.message = message


def export_apng_color_type_frame_data_cases(grid: dict, slip_profile: dict) -> list[dict]:
    width, height = grid["grid_size"]
    source = render_grid_rgba_pixels(grid)
    alternate = _alternate_pixels(source, width, height, slip_profile["profile_id"])
    cases = []
    for spec in CASE_SPECS:
        frames = [
            _frame("base", width, height, _adapt_pixels(source, spec["color_type"], width), 1, 5),
            _frame("pulse", width, height, _adapt_pixels(alternate, spec["color_type"], width), 1, 10),
        ]
        png_bytes = _encode_apng_color_type(width, height, spec["color_type"], frames)
        expected = _expected_playback(width, height, frames)
        decoded = decode_apng_color_type_frame_data(png_bytes)
        cases.append(
            {
                "case_id": spec["case_id"],
                "description": spec["description"],
                "profile_id": slip_profile["profile_id"],
                "grid_id": grid["grid_id"],
                "color_type": spec["color_type"],
                "bit_depth": 8,
                "png_file_name": f"{slip_profile['profile_id']}_{spec['case_id']}.png",
                "png_bytes": png_bytes,
                "png_hash": _hash_bytes(png_bytes),
                "expected_frame_hashes": [_hash_pixels(frame["rgba_pixels"]) for frame in frames],
                "expected_display_hashes": expected["display_hashes"],
                "expected_final_hash": expected["final_output_hash"],
                "decoded": decoded,
            }
        )
    return cases


def decode_apng_color_type_frame_data(png_bytes: bytes) -> dict:
    try:
        decoded = _decode_apng_color_type_frame_data(png_bytes)
        decoded["ok"] = True
        decoded["errors"] = []
        decoded["error_families"] = []
        return decoded
    except APNGColorTypeFrameDataError as exc:
        return {
            "ok": False,
            "errors": [_error("apng.color_type_frame_data", exc.family, exc.message)],
            "error_families": [exc.family],
        }


def make_missing_plte_probe(png_bytes: bytes) -> bytes:
    chunks = [chunk for chunk in _read_png_chunks(png_bytes) if chunk["type"] != "PLTE"]
    return _write_png_chunks(chunks)


def make_invalid_trns_probe(png_bytes: bytes) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    plte = _parse_plte(chunks)
    updated = []
    replaced = False
    for chunk in chunks:
        if chunk["type"] == "tRNS":
            updated.append(_chunk("tRNS", bytes([255]) * (len(plte) + 1)))
            replaced = True
        else:
            updated.append(chunk)
    if not replaced:
        raise APNGColorTypeFrameDataError("png_trns_missing", "expected tRNS chunk")
    return _write_png_chunks(updated)


def make_unsupported_color_type_probe(png_bytes: bytes) -> bytes:
    return _rewrite_ihdr(png_bytes, lambda ihdr: {**ihdr, "color_type": 5})


def make_alpha_trns_conflict_probe(png_bytes: bytes) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    updated = []
    inserted = False
    for chunk in chunks:
        if chunk["type"] == "acTL" and not inserted:
            updated.append(_chunk("tRNS", b"\x00\x00\x00\x00\x00\x00"))
            inserted = True
        updated.append(chunk)
    if not inserted:
        raise APNGColorTypeFrameDataError("apng_control_missing", "expected acTL chunk")
    return _write_png_chunks(updated)


def run_apng_color_type_frame_data_lab(
    profile_paths: list[Path],
    generated_root: Path,
) -> dict:
    case_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid = _read_json(_first_grid_path(profile, generated_root))
        for case in export_apng_color_type_frame_data_cases(grid, profile):
            decoded = case["decoded"]
            success = (
                decoded["ok"]
                and decoded["frame_pixel_hashes"] == case["expected_frame_hashes"]
                and decoded["display_hashes"] == case["expected_display_hashes"]
                and decoded["final_output_hash"] == case["expected_final_hash"]
                and decoded["color_type"] == case["color_type"]
            )
            case_results.append(
                {
                    "profile_id": profile["profile_id"],
                    "grid_id": grid["grid_id"],
                    "case_id": case["case_id"],
                    "description": case["description"],
                    "color_type": case["color_type"],
                    "png_file_name": case["png_file_name"],
                    "png_hash": case["png_hash"],
                    "png_bytes_hex": case["png_bytes"].hex(),
                    "expected_frame_hashes": case["expected_frame_hashes"],
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
        "artifact_id": "apng_color_type_frame_data_stage0",
        "status": "research_apng_color_type_frame_data_no_package_code",
        "profile_count": len(profile_paths),
        "case_ids": list(COLOR_TYPE_CASE_IDS),
        "case_count": len(case_results),
        "case_success_count": success_count,
        "invalid_probe_count": len(invalid_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "case_results": case_results,
        "invalid_probe_results": invalid_results,
        "metrics": {
            "case_success_rate": _ratio(success_count, len(case_results)),
            "invalid_probe_rejection_rate": _ratio(invalid_rejected_count, len(invalid_results)),
            "profile_coverage": len({result["profile_id"] for result in case_results}),
            "color_type_family_count": len(COLOR_TYPE_CASE_IDS),
            "color_types_covered": sorted({result["color_type"] for result in case_results}),
        },
        "closed_states": [
            "apng_color_type_frame_reconstruction",
            "apng_palette_trns_frame_reconstruction",
            "apng_alpha_channel_frame_reconstruction",
            "apng_color_type_invalid_metadata_rejection",
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
                    "PNG color types, bit-depth restrictions, PLTE/tRNS rules, "
                    "filter method 0, IDAT image data, and APNG fdAT frame-data inheritance."
                ),
            }
        ],
        "decision": "prototype_apng_color_type_frame_data_subset",
        "notes": [
            "This lab validates deterministic 8-bit non-interlaced APNG frame color types only.",
            "It covers color types 0, 2, 3, 4, and 6 with full-canvas source frames.",
            "It does not claim full APNG/PNG conformance, live editor preservation, or final production carrier selection.",
        ],
    }


def write_apng_color_type_frame_data_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    cases_dir = output_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "apng_color_type_frame_data_stage0.json", _json_report(report))
    for result in report["case_results"]:
        (cases_dir / result["png_file_name"]).write_bytes(
            bytes.fromhex(result["png_bytes_hex"])
        )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "apng_color_type_frame_data.js").write_text(
        "window.MECHAGOTCHI_APNG_COLOR_TYPE_FRAME_DATA = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _decode_apng_color_type_frame_data(png_bytes: bytes) -> dict:
    chunks = _read_png_chunks(png_bytes)
    if not chunks or chunks[0]["type"] != "IHDR":
        raise APNGColorTypeFrameDataError("png_ihdr_missing", "PNG IHDR chunk must be first")
    ihdr = _decode_ihdr(chunks[0]["data"])
    plte = _parse_plte(chunks)
    trns = _parse_trns(chunks, ihdr["color_type"], plte)
    names = [chunk["type"] for chunk in chunks]
    actl_chunks = [chunk for chunk in chunks if chunk["type"] == "acTL"]
    if len(actl_chunks) != 1 or len(actl_chunks[0]["data"]) != 8:
        raise APNGColorTypeFrameDataError("apng_control_invalid", "APNG acTL chunk must be present, unique, and 8 bytes")
    if "IDAT" not in names:
        raise APNGColorTypeFrameDataError("apng_idat_missing", "APNG default IDAT chunk must be present")
    if names.index("acTL") > names.index("IDAT"):
        raise APNGColorTypeFrameDataError("apng_actl_after_idat", "APNG acTL must appear before IDAT")
    expected_frame_count, num_plays = struct.unpack(">II", actl_chunks[0]["data"])

    frames = []
    current = None
    expected_sequence = 0
    idat_seen = False
    sequence_numbers = []
    animation_chunk_order = []
    for chunk in chunks[1:]:
        chunk_type = chunk["type"]
        if chunk_type == "fcTL":
            if current is not None:
                _append_frame(frames, current, ihdr, plte, trns)
            control = _decode_fctl(chunk["data"])
            if control["sequence_number"] != expected_sequence:
                raise APNGColorTypeFrameDataError("apng_sequence_number_invalid", "APNG sequence numbers must be consecutive")
            sequence_numbers.append(control["sequence_number"])
            expected_sequence += 1
            _validate_frame_control(control, ihdr, default_frame=not idat_seen)
            current = {**control, "data": bytearray(), "data_source": None, "fdat_chunk_count": 0}
            animation_chunk_order.append("fcTL")
        elif chunk_type == "IDAT":
            if current is None:
                raise APNGColorTypeFrameDataError("apng_default_frame_control_missing", "APNG default IDAT requires preceding fcTL")
            if current["data_source"] not in {None, "IDAT"}:
                raise APNGColorTypeFrameDataError("apng_idat_order_invalid", "IDAT order is invalid")
            current["data"].extend(chunk["data"])
            current["data_source"] = "IDAT"
            idat_seen = True
            animation_chunk_order.append("IDAT")
        elif chunk_type == "fdAT":
            if current is None:
                raise APNGColorTypeFrameDataError("apng_fdat_without_fctl", "fdAT requires preceding fcTL")
            if len(chunk["data"]) < 4:
                raise APNGColorTypeFrameDataError("apng_fdat_invalid", "fdAT chunk must include a sequence number")
            sequence_number = struct.unpack(">I", chunk["data"][:4])[0]
            if sequence_number != expected_sequence:
                raise APNGColorTypeFrameDataError("apng_sequence_number_invalid", "APNG sequence numbers must be consecutive")
            sequence_numbers.append(sequence_number)
            expected_sequence += 1
            current["data"].extend(chunk["data"][4:])
            current["data_source"] = "fdAT"
            current["fdat_chunk_count"] += 1
            animation_chunk_order.append("fdAT")
        elif chunk_type == "IEND":
            break

    if current is not None:
        _append_frame(frames, current, ihdr, plte, trns)
    if len(frames) != expected_frame_count:
        raise APNGColorTypeFrameDataError("apng_frame_count_mismatch", "acTL frame count does not match fcTL chunks")

    playback = _expected_playback(ihdr["width"], ihdr["height"], frames)
    return {
        "canvas_width": ihdr["width"],
        "canvas_height": ihdr["height"],
        "bit_depth": ihdr["bit_depth"],
        "color_type": ihdr["color_type"],
        "bytes_per_pixel": COLOR_TYPE_CHANNELS[ihdr["color_type"]],
        "has_plte": bool(plte),
        "has_trns": bool(trns),
        "animation_control": {
            "num_frames": expected_frame_count,
            "num_plays": num_plays,
        },
        "frame_count": len(frames),
        "sequence_numbers": sequence_numbers,
        "frames": [_frame_summary(frame, index) for index, frame in enumerate(frames)],
        "frame_pixel_hashes": [_hash_pixels(frame["rgba_pixels"]) for frame in frames],
        "chunks": names,
        "animation_chunk_order": animation_chunk_order,
        **playback,
    }


def _append_frame(
    frames: list[dict],
    frame: dict,
    ihdr: dict,
    plte: list[tuple[int, int, int]] | None,
    trns: bytes,
) -> None:
    if not frame["data"]:
        raise APNGColorTypeFrameDataError("apng_frame_data_missing", "APNG frame has no image data")
    try:
        raw = bounded_decompress(
            bytes(frame["data"]),
            (frame["width"] * COLOR_TYPE_CHANNELS[ihdr["color_type"]] + 1) * frame["height"],
        )
    except PNGChunkError as exc:
        raise APNGColorTypeFrameDataError("apng_frame_decompression_failed", exc.message) from exc
    frame["rgba_pixels"] = _decode_frame_pixels(frame["width"], frame["height"], raw, ihdr, plte, trns)
    frames.append(frame)


def _decode_frame_pixels(
    width: int,
    height: int,
    raw: bytes,
    ihdr: dict,
    plte: list[tuple[int, int, int]] | None,
    trns: bytes,
) -> list[tuple[int, int, int, int]]:
    channels = COLOR_TYPE_CHANNELS[ihdr["color_type"]]
    stride = width * channels
    expected = (stride + 1) * height
    if len(raw) != expected:
        raise APNGColorTypeFrameDataError("apng_scanline_length_mismatch", "APNG scanline length does not match frame dimensions")
    pixels = []
    offset = 0
    for _y in range(height):
        filter_type = raw[offset]
        offset += 1
        if filter_type != 0:
            raise APNGColorTypeFrameDataError("apng_filter_unsupported", "Stage 0 color-type APNG supports filter type 0 only")
        row = raw[offset : offset + stride]
        offset += stride
        pixels.extend(_row_to_rgba(row, ihdr["color_type"], plte, trns))
    return pixels


def _row_to_rgba(
    row: bytes,
    color_type: int,
    plte: list[tuple[int, int, int]] | None,
    trns: bytes,
) -> list[tuple[int, int, int, int]]:
    pixels = []
    if color_type == 0:
        transparent = struct.unpack(">H", trns)[0] & 0xFF if trns else None
        for grey in row:
            alpha = 0 if transparent is not None and grey == transparent else 255
            pixels.append((grey, grey, grey, alpha))
    elif color_type == 2:
        transparent = struct.unpack(">HHH", trns) if trns else None
        for index in range(0, len(row), 3):
            red, green, blue = row[index : index + 3]
            alpha = 0 if transparent == (red, green, blue) else 255
            pixels.append((red, green, blue, alpha))
    elif color_type == 3:
        if plte is None:
            raise APNGColorTypeFrameDataError("png_plte_missing", "indexed-color APNG requires PLTE")
        for palette_index in row:
            if palette_index >= len(plte):
                raise APNGColorTypeFrameDataError("png_palette_index_invalid", "indexed-color frame references a missing PLTE entry")
            red, green, blue = plte[palette_index]
            alpha = trns[palette_index] if palette_index < len(trns) else 255
            pixels.append((red, green, blue, alpha))
    elif color_type == 4:
        for index in range(0, len(row), 2):
            grey, alpha = row[index : index + 2]
            pixels.append((grey, grey, grey, alpha))
    elif color_type == 6:
        for index in range(0, len(row), 4):
            pixels.append(tuple(row[index : index + 4]))
    return pixels


def _encode_apng_color_type(width: int, height: int, color_type: int, frames: list[dict]) -> bytes:
    chunks = [_chunk("IHDR", struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0))]
    if color_type == 3:
        chunks.append(_chunk("PLTE", _palette_bytes()))
        chunks.append(_chunk("tRNS", _palette_trns()))
    chunks.append(_chunk("acTL", struct.pack(">II", len(frames), 0)))
    sequence_number = 0
    for index, frame in enumerate(frames):
        chunks.append(_chunk("fcTL", _pack_fctl({**frame, "sequence_number": sequence_number})))
        sequence_number += 1
        raw = _frame_scanlines(frame["encoded_rows"])
        compressed = zlib.compress(raw)
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
    adapted: dict,
    delay_num: int,
    delay_den: int,
) -> dict:
    return {
        "frame_id": frame_id,
        "width": width,
        "height": height,
        "x_offset": 0,
        "y_offset": 0,
        "encoded_rows": adapted["encoded_rows"],
        "rgba_pixels": adapted["rgba_pixels"],
        "delay_num": delay_num,
        "delay_den": delay_den,
        "dispose_op": 0,
        "blend_op": 0,
    }


def _adapt_pixels(pixels: list[tuple[int, int, int, int]], color_type: int, width: int) -> dict:
    rows = []
    rgba = []
    for start in range(0, len(pixels), width):
        row_pixels = pixels[start : start + width]
        encoded = bytearray()
        for index, pixel in enumerate(row_pixels, start=start):
            red, green, blue, alpha = pixel
            grey = _luma(red, green, blue)
            if color_type == 0:
                encoded.append(grey)
                rgba.append((grey, grey, grey, 255))
            elif color_type == 2:
                encoded.extend([red, green, blue])
                rgba.append((red, green, blue, 255))
            elif color_type == 3:
                palette_index = 0 if alpha == 0 or index % 11 == 0 else (index % 3) + 1
                encoded.append(palette_index)
                pr, pg, pb = _palette()[palette_index]
                pa = _palette_trns()[palette_index] if palette_index < len(_palette_trns()) else 255
                rgba.append((pr, pg, pb, pa))
            elif color_type == 4:
                adjusted_alpha = _alpha_pattern(index, alpha)
                encoded.extend([grey, adjusted_alpha])
                rgba.append((grey, grey, grey, adjusted_alpha))
            elif color_type == 6:
                adjusted_alpha = _alpha_pattern(index, alpha)
                encoded.extend([red, green, blue, adjusted_alpha])
                rgba.append((red, green, blue, adjusted_alpha))
        rows.append(bytes(encoded))
    return {"encoded_rows": rows, "rgba_pixels": rgba}


def _alternate_pixels(
    pixels: list[tuple[int, int, int, int]],
    width: int,
    height: int,
    seed: str,
) -> list[tuple[int, int, int, int]]:
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    alternate = []
    for index, (red, green, blue, alpha) in enumerate(pixels):
        alternate.append(
            (
                (red + digest[index % len(digest)] + 17) % 256,
                (green + digest[(index + 7) % len(digest)] + 29) % 256,
                (blue + digest[(index + 13) % len(digest)] + 43) % 256,
                alpha if alpha else (0 if (index + width + height) % 7 == 0 else 255),
            )
        )
    return alternate


def _alpha_pattern(index: int, alpha: int) -> int:
    if index % 13 == 0:
        return 0
    if index % 7 == 0:
        return 128
    return alpha if alpha else 255


def _luma(red: int, green: int, blue: int) -> int:
    return (77 * red + 150 * green + 29 * blue) // 256


def _frame_scanlines(rows: list[bytes]) -> bytes:
    payload = bytearray()
    for row in rows:
        payload.append(0)
        payload.extend(row)
    return bytes(payload)


def _expected_playback(width: int, height: int, frames: list[dict]) -> dict:
    output = [TRANSPARENT_BLACK for _ in range(width * height)]
    display_hashes = []
    for frame in frames:
        output = list(frame["rgba_pixels"])
        display_hashes.append(_hash_pixels(output))
    return {
        "display_hashes": display_hashes,
        "final_output_hash": display_hashes[-1] if display_hashes else _hash_pixels(output),
    }


def _decode_ihdr(data: bytes) -> dict:
    if len(data) != 13:
        raise APNGColorTypeFrameDataError("png_ihdr_invalid", "PNG IHDR chunk length must be 13")
    width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(">IIBBBBB", data)
    if width <= 0 or height <= 0:
        raise APNGColorTypeFrameDataError("png_ihdr_invalid", "PNG dimensions must be positive")
    if bit_depth != 8:
        raise APNGColorTypeFrameDataError("png_bit_depth_unsupported", "Stage 0 APNG color-type matrix supports 8-bit samples only")
    if color_type not in COLOR_TYPE_CHANNELS:
        raise APNGColorTypeFrameDataError("png_color_type_unsupported", "PNG color type must be one of 0, 2, 3, 4, or 6")
    if compression != 0 or filter_method != 0 or interlace != 0:
        raise APNGColorTypeFrameDataError("png_method_unsupported", "Stage 0 APNG color-type matrix supports compression 0, filter method 0, and no interlace only")
    return {
        "width": width,
        "height": height,
        "bit_depth": bit_depth,
        "color_type": color_type,
        "compression": compression,
        "filter_method": filter_method,
        "interlace": interlace,
    }


def _validate_frame_control(frame: dict, ihdr: dict, *, default_frame: bool) -> None:
    if frame["width"] != ihdr["width"] or frame["height"] != ihdr["height"]:
        raise APNGColorTypeFrameDataError("apng_frame_dimensions_unsupported", "Stage 0 color-type APNG frames must be full canvas")
    if frame["x_offset"] != 0 or frame["y_offset"] != 0:
        raise APNGColorTypeFrameDataError("apng_frame_offset_unsupported", "Stage 0 color-type APNG frames must start at origin")
    if frame["dispose_op"] not in {0, 1, 2}:
        raise APNGColorTypeFrameDataError("apng_dispose_op_invalid", "APNG dispose_op must be 0, 1, or 2")
    if frame["blend_op"] not in {0, 1}:
        raise APNGColorTypeFrameDataError("apng_blend_op_invalid", "APNG blend_op must be 0 or 1")
    if default_frame and frame["blend_op"] != 0:
        raise APNGColorTypeFrameDataError("apng_default_blend_invalid", "APNG default image frame must use source blend in this lab")


def _decode_fctl(data: bytes) -> dict:
    if len(data) != 26:
        raise APNGColorTypeFrameDataError("apng_fctl_invalid", "APNG fcTL chunk length must be 26")
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


def _parse_plte(chunks: list[dict]) -> list[tuple[int, int, int]] | None:
    plte_chunks = [chunk for chunk in chunks if chunk["type"] == "PLTE"]
    if not plte_chunks:
        return None
    if len(plte_chunks) != 1 or len(plte_chunks[0]["data"]) % 3 != 0:
        raise APNGColorTypeFrameDataError("png_plte_invalid", "PLTE must be unique and divisible into RGB triples")
    payload = plte_chunks[0]["data"]
    return [tuple(payload[index : index + 3]) for index in range(0, len(payload), 3)]


def _parse_trns(
    chunks: list[dict],
    color_type: int,
    plte: list[tuple[int, int, int]] | None,
) -> bytes:
    trns_chunks = [chunk for chunk in chunks if chunk["type"] == "tRNS"]
    if not trns_chunks:
        if color_type == 3 and plte is None:
            raise APNGColorTypeFrameDataError("png_plte_missing", "indexed-color APNG requires PLTE")
        return b""
    if len(trns_chunks) != 1:
        raise APNGColorTypeFrameDataError("png_trns_invalid", "tRNS must be unique")
    payload = trns_chunks[0]["data"]
    if color_type in {4, 6}:
        raise APNGColorTypeFrameDataError("png_trns_forbidden", "tRNS is forbidden when alpha is already present")
    if color_type == 3:
        if plte is None:
            raise APNGColorTypeFrameDataError("png_plte_missing", "indexed-color APNG requires PLTE")
        if len(payload) > len(plte):
            raise APNGColorTypeFrameDataError("png_trns_invalid", "indexed-color tRNS cannot exceed PLTE length")
    elif color_type == 0 and len(payload) != 2:
        raise APNGColorTypeFrameDataError("png_trns_invalid", "greyscale tRNS must be 2 bytes")
    elif color_type == 2 and len(payload) != 6:
        raise APNGColorTypeFrameDataError("png_trns_invalid", "truecolor tRNS must be 6 bytes")
    return payload


def _rewrite_ihdr(png_bytes: bytes, mutate) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    updated = []
    for chunk in chunks:
        if chunk["type"] == "IHDR":
            width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(">IIBBBBB", chunk["data"])
            ihdr = mutate(
                {
                    "width": width,
                    "height": height,
                    "bit_depth": bit_depth,
                    "color_type": color_type,
                    "compression": compression,
                    "filter_method": filter_method,
                    "interlace": interlace,
                }
            )
            updated.append(
                _chunk(
                    "IHDR",
                    struct.pack(
                        ">IIBBBBB",
                        ihdr["width"],
                        ihdr["height"],
                        ihdr["bit_depth"],
                        ihdr["color_type"],
                        ihdr["compression"],
                        ihdr["filter_method"],
                        ihdr["interlace"],
                    ),
                )
            )
        else:
            updated.append(chunk)
    return _write_png_chunks(updated)


def _read_png_chunks(png_bytes: bytes) -> list[dict]:
    try:
        parsed = read_png_chunks(png_bytes)
    except PNGChunkError as exc:
        raise APNGColorTypeFrameDataError(exc.family, exc.message) from exc
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
    by_case = {result["case_id"]: bytes.fromhex(result["png_bytes_hex"]) for result in case_results}
    probes = [
        ("missing_plte", make_missing_plte_probe(by_case["indexed8_trns_fdat"]), "png_plte_missing"),
        ("invalid_trns", make_invalid_trns_probe(by_case["indexed8_trns_fdat"]), "png_trns_invalid"),
        ("unsupported_color_type", make_unsupported_color_type_probe(by_case["truecolor8_fdat"]), "png_color_type_unsupported"),
        ("alpha_trns_conflict", make_alpha_trns_conflict_probe(by_case["truecolor_alpha8_fdat"]), "png_trns_forbidden"),
    ]
    results = []
    for probe_id, png_bytes, expected_family in probes:
        decoded = decode_apng_color_type_frame_data(png_bytes)
        results.append(
            {
                "probe_id": probe_id,
                "expected_family": expected_family,
                "rejected": not decoded["ok"] and expected_family in decoded["error_families"],
                "decoded": _compact_decoded(decoded),
            }
        )
    return results


def _frame_summary(frame: dict, index: int) -> dict:
    delay_den = frame["delay_den"] or 100
    transparent = sum(1 for pixel in frame["rgba_pixels"] if pixel[3] == 0)
    partial_alpha = sum(1 for pixel in frame["rgba_pixels"] if 0 < pixel[3] < 255)
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
        "transparent_pixel_count": transparent,
        "partial_alpha_pixel_count": partial_alpha,
        "pixel_hash": _hash_pixels(frame["rgba_pixels"]),
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
            "bit_depth",
            "color_type",
            "bytes_per_pixel",
            "has_plte",
            "has_trns",
            "animation_control",
            "frame_count",
            "sequence_numbers",
            "frames",
            "frame_pixel_hashes",
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
                "color_type": result["color_type"],
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
        "# APNG Color Type Frame Data Stage 0\n\n"
        "Bounded APNG color-type frame-data matrix for Mechagotchi workshop carriers.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Case successes: {report['case_success_count']}/{report['case_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- Success rate: {metrics['case_success_rate']}\n"
        f"- Invalid rejection rate: {metrics['invalid_probe_rejection_rate']}\n\n"
        "This is a deterministic 8-bit non-interlaced APNG color-type subset. "
        "It does not prove full APNG/PNG conformance, live editor rewrite "
        "preservation, or final production carrier selection.\n"
    )


def _palette() -> list[tuple[int, int, int]]:
    return [
        (0, 0, 0),
        (52, 92, 64),
        (176, 136, 48),
        (220, 84, 72),
    ]


def _palette_bytes() -> bytes:
    return bytes(channel for entry in _palette() for channel in entry)


def _palette_trns() -> bytes:
    return b"\x00\xff\xcc\xff"


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
        default=ROOT / "data/workshop_editor/apng_color_type_frame_data_stage0",
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
    report = run_apng_color_type_frame_data_lab(profile_paths, args.generated_root)
    write_apng_color_type_frame_data_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_APNG_COLOR_TYPE_FRAME_DATA = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
