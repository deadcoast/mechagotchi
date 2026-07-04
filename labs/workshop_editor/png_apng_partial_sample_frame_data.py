import argparse
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

from png_chunk_reader import PNGChunkError, bounded_decompress
from standard_image_sidecar_decoder import PNG_SIGNATURE, render_grid_rgba_pixels

from png_apng_bit_depth_frame_data import (
    APNGBitDepthFrameDataError,
    FILTER_TYPES,
    PNG_SOURCE_URL,
    SUPPORTED_BIT_DEPTHS_BY_COLOR_TYPE,
    _adapt_pixels,
    _decode_frame_pixels,
    _decode_fctl,
    _filtered_frame_scanlines,
    _first_grid_path,
    _hash_bytes,
    _hash_pixels,
    _pack_fctl,
    _parse_plte,
    _parse_trns,
    _portable,
    _ratio,
    _read_json,
    _sorted_unique,
    _write_json,
)
from png_deep_color_sidecar_decoder import (
    PNGDeepColorDecodeError,
    _filter_bpp,
    _png_chunk,
    _read_png_chunks,
    _scanline_byte_length,
)


REPORT_PATH = Path("data/workshop_editor/apng_partial_sample_frame_data_stage0.json")
DATA_PATH = Path("data/workshop_editor/apng_partial_sample_frame_data.js")
ARTIFACT_DIR = Path("data/workshop_editor/apng_partial_sample_frame_data_stage0")
DEFAULT_GENERATED_ROOT = Path("data/slips/multi_profile_generation_stage0")
DEFAULT_PROFILE_PATHS = [
    Path("data/slips/valid/slip_lcd_seed.json"),
    Path("data/slips/valid/slip_gray_stable.json"),
    Path("data/slips/valid/slip_amber_social.json"),
]
DEFAULT_PROFILE_IDS = ["slip_lcd_seed", "slip_gray_stable", "slip_amber_social"]
TRANSPARENT_BLACK = (0, 0, 0, 0)

PARTIAL_SAMPLE_CASE_SPECS = [
    {
        "case_family_id": "grayscale1_source_patch",
        "color_type": 0,
        "bit_depth": 1,
        "blend_op": 0,
        "description": "1-bit packed greyscale partial source-blend APNG frame region.",
    },
    {
        "case_family_id": "indexed4_trns_source_patch",
        "color_type": 3,
        "bit_depth": 4,
        "blend_op": 0,
        "description": "4-bit indexed-color partial source-blend APNG frame region with PLTE/tRNS.",
    },
    {
        "case_family_id": "truecolor16_source_patch",
        "color_type": 2,
        "bit_depth": 16,
        "blend_op": 0,
        "description": "16-bit truecolor partial source-blend APNG frame region.",
    },
    {
        "case_family_id": "grayscale_alpha16_over_patch",
        "color_type": 4,
        "bit_depth": 16,
        "blend_op": 1,
        "description": "16-bit greyscale-alpha partial alpha-over APNG frame region.",
    },
    {
        "case_family_id": "truecolor_alpha16_over_patch",
        "color_type": 6,
        "bit_depth": 16,
        "blend_op": 1,
        "description": "16-bit truecolor-alpha partial alpha-over APNG frame region.",
    },
]

PARTIAL_SAMPLE_CASE_FAMILY_IDS = [
    spec["case_family_id"] for spec in PARTIAL_SAMPLE_CASE_SPECS
]
PARTIAL_SAMPLE_CASE_IDS = [
    f"{profile_id}_{case_family_id}"
    for profile_id in DEFAULT_PROFILE_IDS
    for case_family_id in PARTIAL_SAMPLE_CASE_FAMILY_IDS
]


class APNGPartialSampleFrameDataError(ValueError):
    def __init__(self, family: str, message: str):
        super().__init__(message)
        self.family = family
        self.message = message


def export_apng_partial_sample_frame_data_cases(
    grid: dict,
    slip_profile: dict | str,
) -> list[dict]:
    profile_id = _profile_id(slip_profile)
    width, height = grid["grid_size"]
    base_pixels = render_grid_rgba_pixels(grid)
    patch_width = min(4, max(1, width - 2))
    patch_height = min(5, max(1, height - 2))
    x_offset = min(2, max(0, width - patch_width))
    y_offset = min(1, max(0, height - patch_height))

    cases = []
    for spec in PARTIAL_SAMPLE_CASE_SPECS:
        base_adapted = _adapt_pixels(base_pixels, spec, width, height)
        patch_pixels = _patch_pixels(
            patch_width,
            patch_height,
            seed=f"{profile_id}:{spec['case_family_id']}",
            alpha=160 if spec["blend_op"] else 255,
        )
        patch_adapted = _adapt_pixels(patch_pixels, spec, patch_width, patch_height)
        frames = [
            _frame(
                "default_canvas",
                width,
                height,
                0,
                0,
                spec,
                base_adapted,
                1,
                5,
                0,
                0,
            ),
            _frame(
                "partial_patch",
                patch_width,
                patch_height,
                x_offset,
                y_offset,
                spec,
                patch_adapted,
                1,
                10,
                0,
                spec["blend_op"],
            ),
        ]
        png_bytes = _encode_apng_partial_sample_frame_data(width, height, spec, frames)
        expected = _simulate_playback(width, height, frames)
        decoded = decode_apng_partial_sample_frame_data(png_bytes)
        case_id = f"{profile_id}_{spec['case_family_id']}"
        cases.append(
            {
                "case_id": case_id,
                "case_family_id": spec["case_family_id"],
                "description": spec["description"],
                "profile_id": profile_id,
                "grid_id": grid["grid_id"],
                "color_type": spec["color_type"],
                "bit_depth": spec["bit_depth"],
                "blend_op": spec["blend_op"],
                "filter_types": list(FILTER_TYPES),
                "patch_width": patch_width,
                "patch_height": patch_height,
                "x_offset": x_offset,
                "y_offset": y_offset,
                "png_file_name": f"{case_id}.png",
                "png_bytes": png_bytes,
                "png_hash": _hash_bytes(png_bytes),
                "expected_frame_hashes": [_hash_pixels(frame["rgba_pixels"]) for frame in frames],
                "expected_display_hashes": expected["display_hashes"],
                "expected_after_dispose_hashes": expected["after_dispose_hashes"],
                "expected_final_hash": expected["final_canvas_hash"],
                "expected_patch_scanline_byte_length": _scanline_byte_length(
                    patch_width,
                    spec["color_type"],
                    spec["bit_depth"],
                ),
                "decoded": decoded,
            }
        )
    return cases


def decode_apng_partial_sample_frame_data(png_bytes: bytes) -> dict:
    try:
        decoded = _decode_apng_partial_sample_frame_data(png_bytes)
        decoded["ok"] = True
        decoded["errors"] = []
        decoded["error_families"] = []
        return decoded
    except APNGPartialSampleFrameDataError as exc:
        return _failed_decode(exc.family, exc.message)
    except APNGBitDepthFrameDataError as exc:
        return _failed_decode(exc.family, exc.message)
    except PNGDeepColorDecodeError as exc:
        return _failed_decode(exc.family, exc.message)


def make_out_of_bounds_probe(png_bytes: bytes) -> bytes:
    def mutate(frame: dict, canvas: dict) -> dict:
        return {**frame, "x_offset": canvas["width"]}

    return _rewrite_fctl(png_bytes, frame_number=1, mutate=mutate)


def make_invalid_bit_depth_color_type_probe(png_bytes: bytes) -> bytes:
    return _rewrite_ihdr(png_bytes, bit_depth=4, color_type=2)


def make_truncated_partial_scanline_probe(png_bytes: bytes) -> bytes:
    return _rewrite_second_frame_fdat_raw(png_bytes, lambda raw: raw[:-1])


def make_invalid_filter_probe(png_bytes: bytes) -> bytes:
    return _rewrite_second_frame_fdat_raw(png_bytes, lambda raw: bytes([5]) + raw[1:])


def make_sequence_gap_probe(png_bytes: bytes) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    rewritten = [PNG_SIGNATURE]
    mutated = False
    for chunk in chunks:
        payload = chunk["payload"]
        if chunk["type"] == "fdAT" and not mutated:
            if len(payload) < 4:
                raise APNGPartialSampleFrameDataError("apng_fdat_invalid", "fdAT chunk is too short")
            sequence_number = struct.unpack(">I", payload[:4])[0] + 3
            payload = struct.pack(">I", sequence_number) + payload[4:]
            mutated = True
        rewritten.append(_png_chunk(chunk["type"].encode("ascii"), payload))
    if not mutated:
        raise APNGPartialSampleFrameDataError("apng_fdat_missing", "expected fdAT chunk")
    return b"".join(rewritten)


def run_apng_partial_sample_frame_data_lab(
    profile_paths: list[Path] | None = None,
    generated_root: Path = DEFAULT_GENERATED_ROOT,
) -> dict:
    profile_paths = profile_paths or list(DEFAULT_PROFILE_PATHS)
    case_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        for case in export_apng_partial_sample_frame_data_cases(grid, profile):
            decoded = case["decoded"]
            success = (
                decoded["ok"]
                and decoded["frame_pixel_hashes"] == case["expected_frame_hashes"]
                and decoded["display_hashes"] == case["expected_display_hashes"]
                and decoded["after_dispose_hashes"] == case["expected_after_dispose_hashes"]
                and decoded["final_canvas_hash"] == case["expected_final_hash"]
                and decoded["color_type"] == case["color_type"]
                and decoded["bit_depth"] == case["bit_depth"]
            )
            case_results.append(
                {
                    "profile_id": profile["profile_id"],
                    "profile_path": _portable(profile_path),
                    "grid_id": grid["grid_id"],
                    "grid_path": _portable(grid_path),
                    "case_id": case["case_id"],
                    "case_family_id": case["case_family_id"],
                    "description": case["description"],
                    "color_type": case["color_type"],
                    "bit_depth": case["bit_depth"],
                    "blend_op": case["blend_op"],
                    "filter_types": case["filter_types"],
                    "patch_width": case["patch_width"],
                    "patch_height": case["patch_height"],
                    "x_offset": case["x_offset"],
                    "y_offset": case["y_offset"],
                    "png_file_name": case["png_file_name"],
                    "png_hash": case["png_hash"],
                    "png_bytes_hex": case["png_bytes"].hex(),
                    "expected_frame_hashes": case["expected_frame_hashes"],
                    "expected_display_hashes": case["expected_display_hashes"],
                    "expected_after_dispose_hashes": case["expected_after_dispose_hashes"],
                    "expected_final_hash": case["expected_final_hash"],
                    "expected_patch_scanline_byte_length": case[
                        "expected_patch_scanline_byte_length"
                    ],
                    "decoded": _compact_decoded(decoded),
                    "success": success,
                }
            )

    invalid_results = _invalid_probe_results(case_results)
    success_count = sum(1 for result in case_results if result["success"])
    invalid_rejected_count = sum(1 for result in invalid_results if result["rejected"])
    return {
        "artifact_id": "apng_partial_sample_frame_data_stage0",
        "status": "research_apng_partial_sample_frame_data_no_package_code",
        "date": "2026-05-14",
        "purpose": (
            "Close a bounded APNG image-data gap where partial frame offsets "
            "intersect packed low-bit, indexed, and 16-bit PNG sample encodings."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
            "labs/workshop_editor/png_apng_partial_frame_playback.py",
            "labs/workshop_editor/png_apng_bit_depth_frame_data.py",
            "labs/workshop_editor/png_apng_partial_sample_frame_data.py",
        ],
        "external_anchors": [
            {
                "source": "W3C PNG specification",
                "url": PNG_SOURCE_URL,
                "used_for": (
                    "APNG frame offsets, fdAT sequence inheritance, source/over "
                    "blend behavior, packed sample scanline sizing, filter method "
                    "0 reconstruction, and PLTE/tRNS indexed-color transparency."
                ),
            }
        ],
        "profile_count": len(profile_paths),
        "case_family_ids": list(PARTIAL_SAMPLE_CASE_FAMILY_IDS),
        "case_ids": [result["case_id"] for result in case_results],
        "case_count": len(case_results),
        "case_success_count": success_count,
        "invalid_probe_count": len(invalid_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "case_results": case_results,
        "invalid_probe_results": invalid_results,
        "supported_color_types": _sorted_unique(result["color_type"] for result in case_results),
        "supported_bit_depths": _sorted_unique(result["bit_depth"] for result in case_results),
        "metrics": {
            "case_success_ratio": _ratio(success_count, len(case_results)),
            "invalid_probe_rejection_ratio": _ratio(
                invalid_rejected_count,
                len(invalid_results),
            ),
            "profile_coverage": len({result["profile_id"] for result in case_results}),
            "case_family_count": len(PARTIAL_SAMPLE_CASE_FAMILY_IDS),
            "supported_color_types": _sorted_unique(
                result["color_type"] for result in case_results
            ),
            "supported_bit_depths": _sorted_unique(
                result["bit_depth"] for result in case_results
            ),
            "supported_filter_types": list(FILTER_TYPES),
            "partial_frame_case_count": sum(
                1
                for result in case_results
                if result["x_offset"] > 0 or result["y_offset"] > 0
            ),
            "over_blend_case_count": sum(
                1 for result in case_results if result["blend_op"] == 1
            ),
            "split_fdat_frame_count": sum(
                1
                for result in case_results
                for frame in result["decoded"].get("frames", [])
                if frame.get("fdat_chunk_count") == 2
            ),
        },
        "closed_states": [
            "apng_partial_sample_offset_reconstruction",
            "apng_partial_low_bit_region_reconstruction",
            "apng_partial_16bit_region_reconstruction",
            "apng_partial_alpha_over_sample_reconstruction",
            "apng_partial_sample_invalid_probe_rejection",
        ],
        "blocked_states": [
            "full_apng_png_conformance",
            "live_external_editor_rewrite_validation",
            "production_import_export_carrier_selection_final_decision",
            "manual_readability_calibration",
            "package_runtime_lifecycle_integration",
        ],
        "decision": "prototype_apng_partial_sample_frame_data_subset",
        "notes": [
            "This lab validates deterministic non-interlaced APNG partial-frame sample reconstruction only.",
            "It intersects partial frame offsets with packed 1-bit greyscale, 4-bit indexed PLTE/tRNS, and 16-bit truecolor/alpha sample models.",
            "It does not claim full APNG/PNG conformance, live editor preservation, or final production carrier selection.",
        ],
        "next_research_step": (
            "Keep remaining APNG/PNG work scoped to explicit image-data "
            "fixtures, live external editor preservation, or final carrier "
            "selection evidence before claiming full conformance."
        ),
    }


def write_apng_partial_sample_frame_data_artifacts(
    output_root: Path = Path("data/workshop_editor"),
    report: dict | None = None,
) -> dict:
    report = report or run_apng_partial_sample_frame_data_lab()
    output_root.mkdir(parents=True, exist_ok=True)
    artifact_dir = output_root / "apng_partial_sample_frame_data_stage0"
    cases_dir = artifact_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)

    summary_json = output_root / "apng_partial_sample_frame_data_stage0.json"
    app_js = output_root / "apng_partial_sample_frame_data.js"
    artifact_summary_json = artifact_dir / "apng_partial_sample_frame_data_stage0.json"
    artifact_app_js = artifact_dir / "apng_partial_sample_frame_data.js"
    readme_path = artifact_dir / "README.md"

    json_payload = _json_report(report)
    _write_json(summary_json, json_payload)
    _write_json(artifact_summary_json, json_payload)
    app_payload = (
        "window.MECHAGOTCHI_APNG_PARTIAL_SAMPLE_FRAME_DATA = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n"
    )
    app_js.write_text(app_payload, encoding="utf-8")
    artifact_app_js.write_text(app_payload, encoding="utf-8")
    readme_path.write_text(_readme_text(report), encoding="utf-8")
    for result in report["case_results"]:
        (cases_dir / result["png_file_name"]).write_bytes(
            bytes.fromhex(result["png_bytes_hex"])
        )

    return {
        "summary_json": summary_json,
        "app_js": app_js,
        "artifact_dir": artifact_dir,
        "artifact_summary_json": artifact_summary_json,
        "artifact_app_js": artifact_app_js,
        "readme": readme_path,
        "cases_dir": cases_dir,
    }


def _decode_apng_partial_sample_frame_data(png_bytes: bytes) -> dict:
    chunks = _read_png_chunks(png_bytes)
    if not chunks or chunks[0]["type"] != "IHDR":
        raise APNGPartialSampleFrameDataError("png_ihdr_missing", "PNG IHDR chunk must be first")
    ihdr = _decode_ihdr(chunks[0]["payload"])
    plte = _parse_plte(chunks)
    trns = _parse_trns(chunks, ihdr["color_type"], ihdr["bit_depth"], plte)
    names = [chunk["type"] for chunk in chunks]
    actl_chunks = [chunk for chunk in chunks if chunk["type"] == "acTL"]
    if len(actl_chunks) != 1 or len(actl_chunks[0]["payload"]) != 8:
        raise APNGPartialSampleFrameDataError(
            "apng_control_invalid",
            "APNG acTL chunk must be present, unique, and 8 bytes",
        )
    if "IDAT" not in names:
        raise APNGPartialSampleFrameDataError("apng_idat_missing", "APNG default IDAT chunk must be present")
    if names.index("acTL") > names.index("IDAT"):
        raise APNGPartialSampleFrameDataError("apng_actl_after_idat", "APNG acTL must appear before IDAT")
    expected_frame_count, num_plays = struct.unpack(">II", actl_chunks[0]["payload"])
    if expected_frame_count <= 0:
        raise APNGPartialSampleFrameDataError("apng_frame_count_invalid", "APNG frame count must be positive")

    frames = []
    current = None
    expected_sequence = 0
    idat_seen = False
    sequence_numbers = []
    animation_chunk_order = []
    for chunk in chunks[1:]:
        chunk_type = chunk["type"]
        payload = chunk["payload"]
        if chunk_type == "fcTL":
            if current is not None:
                _append_frame(frames, current, ihdr, plte, trns)
            control = _decode_fctl(payload)
            if control["sequence_number"] != expected_sequence:
                raise APNGPartialSampleFrameDataError(
                    "apng_sequence_number_invalid",
                    "APNG sequence numbers must be consecutive",
                )
            sequence_numbers.append(control["sequence_number"])
            expected_sequence += 1
            _validate_frame_control(control, ihdr, default_frame=not idat_seen)
            current = {
                **control,
                "data": bytearray(),
                "data_source": None,
                "fdat_chunk_count": 0,
            }
            animation_chunk_order.append("fcTL")
        elif chunk_type == "IDAT":
            if current is None:
                raise APNGPartialSampleFrameDataError(
                    "apng_default_frame_control_missing",
                    "APNG default IDAT requires preceding fcTL",
                )
            if current["data_source"] not in {None, "IDAT"}:
                raise APNGPartialSampleFrameDataError("apng_idat_order_invalid", "IDAT order is invalid")
            current["data"].extend(payload)
            current["data_source"] = "IDAT"
            idat_seen = True
            animation_chunk_order.append("IDAT")
        elif chunk_type == "fdAT":
            if current is None:
                raise APNGPartialSampleFrameDataError("apng_fdat_without_fctl", "fdAT requires preceding fcTL")
            if not idat_seen:
                raise APNGPartialSampleFrameDataError("apng_fdat_before_idat", "fdAT must not precede IDAT")
            if len(payload) < 4:
                raise APNGPartialSampleFrameDataError("apng_fdat_invalid", "fdAT chunk must include a sequence number")
            sequence_number = struct.unpack(">I", payload[:4])[0]
            if sequence_number != expected_sequence:
                raise APNGPartialSampleFrameDataError(
                    "apng_sequence_number_invalid",
                    "APNG sequence numbers must be consecutive",
                )
            sequence_numbers.append(sequence_number)
            expected_sequence += 1
            current["data"].extend(payload[4:])
            current["data_source"] = "fdAT"
            current["fdat_chunk_count"] += 1
            animation_chunk_order.append("fdAT")
        elif chunk_type == "IEND":
            break

    if current is not None:
        _append_frame(frames, current, ihdr, plte, trns)
    if len(frames) != expected_frame_count:
        raise APNGPartialSampleFrameDataError(
            "apng_frame_count_mismatch",
            "acTL frame count does not match fcTL chunks",
        )

    playback = _simulate_playback(ihdr["width"], ihdr["height"], frames)
    return {
        "ihdr": dict(ihdr),
        "canvas_width": ihdr["width"],
        "canvas_height": ihdr["height"],
        "bit_depth": ihdr["bit_depth"],
        "color_type": ihdr["color_type"],
        "bytes_per_pixel": _filter_bpp(ihdr["color_type"], ihdr["bit_depth"]),
        "scanline_byte_length": _scanline_byte_length(
            ihdr["width"],
            ihdr["color_type"],
            ihdr["bit_depth"],
        ),
        "filter_bpp": _filter_bpp(ihdr["color_type"], ihdr["bit_depth"]),
        "palette": {"present": bool(plte), "entry_count": len(plte)},
        "transparency": {"present": bool(trns), "entry_count": len(trns)},
        "animation_control": {
            "num_frames": expected_frame_count,
            "num_plays": num_plays,
        },
        "frame_count": len(frames),
        "sequence_numbers": sequence_numbers,
        "frames": [
            _frame_summary(frame, index, ihdr["width"], ihdr["height"])
            for index, frame in enumerate(frames)
        ],
        "frame_pixel_hashes": [_hash_pixels(frame["rgba_pixels"]) for frame in frames],
        "chunks": names,
        "animation_chunk_order": animation_chunk_order,
        **playback,
    }


def _append_frame(
    frames: list[dict],
    frame: dict,
    ihdr: dict,
    plte: list[tuple[int, int, int]],
    trns: bytes,
) -> None:
    if not frame["data"]:
        raise APNGPartialSampleFrameDataError("apng_frame_data_missing", "APNG frame has no image data")
    try:
        raw = bounded_decompress(
            bytes(frame["data"]),
            (_scanline_byte_length(frame["width"], ihdr["color_type"], ihdr["bit_depth"]) + 1) * frame["height"],
        )
    except PNGChunkError as exc:
        raise APNGPartialSampleFrameDataError("apng_frame_decompression_failed", exc.message) from exc
    try:
        decoded = _decode_frame_pixels(frame["width"], frame["height"], raw, ihdr, plte, trns)
    except APNGBitDepthFrameDataError as exc:
        raise APNGPartialSampleFrameDataError(exc.family, exc.message) from exc
    except PNGDeepColorDecodeError as exc:
        raise APNGPartialSampleFrameDataError(exc.family, exc.message) from exc
    frame["rgba_pixels"] = decoded["pixels"]
    frame["filter_types_seen"] = decoded["filter_types_seen"]
    frame["scanline_byte_length"] = decoded["scanline_byte_length"]
    frames.append(frame)


def _encode_apng_partial_sample_frame_data(
    width: int,
    height: int,
    spec: dict,
    frames: list[dict],
) -> bytes:
    chunks = [
        PNG_SIGNATURE,
        _png_chunk(
            b"IHDR",
            struct.pack(
                ">IIBBBBB",
                width,
                height,
                spec["bit_depth"],
                spec["color_type"],
                0,
                0,
                0,
            ),
        ),
    ]
    if spec["color_type"] == 3:
        chunks.append(_png_chunk(b"PLTE", b"".join(bytes(rgb) for rgb in frames[0]["plte"])))
        if frames[0]["trns"]:
            chunks.append(_png_chunk(b"tRNS", frames[0]["trns"]))
    chunks.append(_png_chunk(b"acTL", struct.pack(">II", len(frames), 0)))
    sequence_number = 0
    for index, frame in enumerate(frames):
        chunks.append(_png_chunk(b"fcTL", _pack_fctl({**frame, "sequence_number": sequence_number})))
        sequence_number += 1
        compressed = zlib.compress(_filtered_frame_scanlines(frame, spec))
        if index == 0:
            chunks.append(_png_chunk(b"IDAT", compressed))
        else:
            midpoint = max(1, len(compressed) // 2)
            for segment in [compressed[:midpoint], compressed[midpoint:]]:
                chunks.append(_png_chunk(b"fdAT", struct.pack(">I", sequence_number) + segment))
                sequence_number += 1
    chunks.append(_png_chunk(b"IEND", b""))
    return b"".join(chunks)


def _frame(
    frame_id: str,
    width: int,
    height: int,
    x_offset: int,
    y_offset: int,
    spec: dict,
    adapted: dict,
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
        "color_type": spec["color_type"],
        "bit_depth": spec["bit_depth"],
        "encoded_rows": adapted["encoded_rows"],
        "rgba_pixels": adapted["rgba_pixels"],
        "plte": adapted["plte"],
        "trns": adapted["trns"],
        "delay_num": delay_num,
        "delay_den": delay_den,
        "dispose_op": dispose_op,
        "blend_op": blend_op,
    }


def _patch_pixels(
    width: int,
    height: int,
    *,
    seed: str,
    alpha: int,
) -> list[tuple[int, int, int, int]]:
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
        raise APNGPartialSampleFrameDataError("png_ihdr_invalid", "PNG IHDR chunk length must be 13")
    width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(">IIBBBBB", data)
    if width <= 0 or height <= 0:
        raise APNGPartialSampleFrameDataError("png_ihdr_invalid", "PNG dimensions must be positive")
    if color_type not in SUPPORTED_BIT_DEPTHS_BY_COLOR_TYPE:
        raise APNGPartialSampleFrameDataError(
            "png_color_type_unsupported",
            "PNG color type must be one of 0, 2, 3, 4, or 6",
        )
    if bit_depth not in SUPPORTED_BIT_DEPTHS_BY_COLOR_TYPE[color_type]:
        raise APNGPartialSampleFrameDataError(
            "png_bit_depth_color_type_invalid",
            "PNG bit depth is not allowed for this APNG partial-sample lab color type",
        )
    if compression != 0 or filter_method != 0 or interlace != 0:
        raise APNGPartialSampleFrameDataError(
            "png_method_unsupported",
            "Stage 0 APNG partial-sample matrix supports compression 0, filter method 0, and no interlace only",
        )
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
    if frame["width"] <= 0 or frame["height"] <= 0:
        raise APNGPartialSampleFrameDataError(
            "apng_frame_dimensions_invalid",
            "APNG frame dimensions must be positive",
        )
    if (
        frame["x_offset"] + frame["width"] > ihdr["width"]
        or frame["y_offset"] + frame["height"] > ihdr["height"]
    ):
        raise APNGPartialSampleFrameDataError(
            "apng_frame_bounds_invalid",
            "APNG frame bounds exceed the canvas",
        )
    if frame["dispose_op"] not in {0, 1, 2}:
        raise APNGPartialSampleFrameDataError("apng_dispose_op_invalid", "APNG dispose_op must be 0, 1, or 2")
    if frame["blend_op"] not in {0, 1}:
        raise APNGPartialSampleFrameDataError("apng_blend_op_invalid", "APNG blend_op must be 0 or 1")
    if default_frame and (
        frame["x_offset"] != 0
        or frame["y_offset"] != 0
        or frame["width"] != ihdr["width"]
        or frame["height"] != ihdr["height"]
        or frame["blend_op"] != 0
    ):
        raise APNGPartialSampleFrameDataError(
            "apng_default_frame_control_invalid",
            "APNG default image frame must cover the full canvas and use source blend in this lab",
        )


def _simulate_playback(width: int, height: int, frames: list[dict]) -> dict:
    output = [TRANSPARENT_BLACK for _ in range(width * height)]
    display_hashes = []
    after_dispose_hashes = []
    for index, frame in enumerate(frames):
        before = list(output)
        for y in range(frame["height"]):
            for x in range(frame["width"]):
                source = frame["rgba_pixels"][y * frame["width"] + x]
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
    final_hash = after_dispose_hashes[-1] if after_dispose_hashes else _hash_pixels(output)
    return {
        "display_hashes": display_hashes,
        "after_dispose_hashes": after_dispose_hashes,
        "final_canvas_hash": final_hash,
        "final_output_hash": final_hash,
    }


def _alpha_over(
    source: tuple[int, int, int, int],
    destination: tuple[int, int, int, int],
) -> tuple[int, int, int, int]:
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


def _rewrite_ihdr(
    png_bytes: bytes,
    *,
    bit_depth: int | None = None,
    color_type: int | None = None,
) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    rewritten = [PNG_SIGNATURE]
    for index, chunk in enumerate(chunks):
        payload = chunk["payload"]
        if index == 0 and chunk["type"] == "IHDR":
            width, height, old_bit_depth, old_color_type, compression, filter_method, interlace = (
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
                interlace,
            )
        rewritten.append(_png_chunk(chunk["type"].encode("ascii"), payload))
    return b"".join(rewritten)


def _rewrite_fctl(png_bytes: bytes, *, frame_number: int, mutate) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    canvas = _decode_ihdr(chunks[0]["payload"])
    rewritten = [PNG_SIGNATURE]
    seen = -1
    for chunk in chunks:
        payload = chunk["payload"]
        if chunk["type"] == "fcTL":
            seen += 1
            if seen == frame_number:
                payload = _pack_fctl(mutate(_decode_fctl(payload), canvas))
        rewritten.append(_png_chunk(chunk["type"].encode("ascii"), payload))
    if seen < frame_number:
        raise APNGPartialSampleFrameDataError("apng_fctl_missing", "requested fcTL chunk is missing")
    return b"".join(rewritten)


def _rewrite_second_frame_fdat_raw(png_bytes: bytes, mutate) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    fdat_chunks = [chunk for chunk in chunks if chunk["type"] == "fdAT"]
    if not fdat_chunks:
        raise APNGPartialSampleFrameDataError("apng_fdat_missing", "expected fdAT chunk")
    compressed = b"".join(chunk["payload"][4:] for chunk in fdat_chunks)
    raw = zlib.decompress(compressed)
    mutated_raw = mutate(raw)
    new_compressed = zlib.compress(mutated_raw)
    segments = _split_segments(new_compressed, len(fdat_chunks))

    rewritten = [PNG_SIGNATURE]
    fdat_index = 0
    for chunk in chunks:
        payload = chunk["payload"]
        if chunk["type"] == "fdAT":
            payload = payload[:4] + segments[fdat_index]
            fdat_index += 1
        rewritten.append(_png_chunk(chunk["type"].encode("ascii"), payload))
    return b"".join(rewritten)


def _split_segments(payload: bytes, count: int) -> list[bytes]:
    if count <= 1:
        return [payload]
    segments = []
    start = 0
    for index in range(count):
        remaining_segments = count - index
        remaining_bytes = len(payload) - start
        size = max(1, remaining_bytes // remaining_segments)
        if index == count - 1:
            size = remaining_bytes
        segments.append(payload[start : start + size])
        start += size
    return segments


def _invalid_probe_results(case_results: list[dict]) -> list[dict]:
    by_family = {
        result["case_family_id"]: bytes.fromhex(result["png_bytes_hex"])
        for result in case_results
    }
    probes = [
        (
            "out_of_bounds_partial_frame",
            make_out_of_bounds_probe(by_family["grayscale1_source_patch"]),
            "apng_frame_bounds_invalid",
        ),
        (
            "invalid_bit_depth_color_type",
            make_invalid_bit_depth_color_type_probe(by_family["truecolor16_source_patch"]),
            "png_bit_depth_color_type_invalid",
        ),
        (
            "truncated_partial_scanline",
            make_truncated_partial_scanline_probe(by_family["grayscale1_source_patch"]),
            "apng_scanline_length_mismatch",
        ),
        (
            "invalid_filter_type",
            make_invalid_filter_probe(by_family["grayscale_alpha16_over_patch"]),
            "png_filter_type_unsupported",
        ),
        (
            "fdat_sequence_gap",
            make_sequence_gap_probe(by_family["truecolor_alpha16_over_patch"]),
            "apng_sequence_number_invalid",
        ),
    ]
    results = []
    for probe_id, png_bytes, expected_family in probes:
        decoded = decode_apng_partial_sample_frame_data(png_bytes)
        results.append(
            {
                "probe_id": probe_id,
                "expected_family": expected_family,
                "rejected": not decoded["ok"] and expected_family in decoded["error_families"],
                "decoded": _compact_decoded(decoded),
            }
        )
    return results


def _frame_summary(
    frame: dict,
    index: int,
    canvas_width: int,
    canvas_height: int,
) -> dict:
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
        "filter_types_seen": frame.get("filter_types_seen", FILTER_TYPES),
        "scanline_byte_length": frame.get("scanline_byte_length", 0),
        "pixel_count": len(frame["rgba_pixels"]),
        "transparent_pixel_count": transparent,
        "partial_alpha_pixel_count": partial_alpha,
        "full_canvas": (
            frame["x_offset"] == 0
            and frame["y_offset"] == 0
            and frame["width"] == canvas_width
            and frame["height"] == canvas_height
        ),
        "pixel_hash": _hash_pixels(frame["rgba_pixels"]),
    }


def _compact_decoded(decoded: dict) -> dict:
    if not decoded.get("ok"):
        return {
            "ok": False,
            "errors": decoded.get("errors", []),
            "error_families": decoded.get("error_families", []),
            "error_family": decoded.get("error_family"),
        }
    return {
        key: decoded[key]
        for key in [
            "ok",
            "ihdr",
            "canvas_width",
            "canvas_height",
            "bit_depth",
            "color_type",
            "bytes_per_pixel",
            "scanline_byte_length",
            "filter_bpp",
            "palette",
            "transparency",
            "animation_control",
            "frame_count",
            "sequence_numbers",
            "frames",
            "frame_pixel_hashes",
            "animation_chunk_order",
            "display_hashes",
            "after_dispose_hashes",
            "final_canvas_hash",
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
                "case_family_ids",
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
                "case_family_id": result["case_family_id"],
                "color_type": result["color_type"],
                "bit_depth": result["bit_depth"],
                "blend_op": result["blend_op"],
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
        "# APNG Partial Sample Frame Data Stage 0\n\n"
        "Bounded APNG partial-frame matrix for packed low-bit, indexed, and 16-bit "
        "PNG sample reconstruction in Mechagotchi workshop carriers.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Case successes: {report['case_success_count']}/{report['case_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- Supported color types: {metrics['supported_color_types']}\n"
        f"- Supported bit depths: {metrics['supported_bit_depths']}\n"
        f"- Partial frame cases: {metrics['partial_frame_case_count']}\n"
        f"- Over-blend cases: {metrics['over_blend_case_count']}\n"
        f"- Success ratio: {metrics['case_success_ratio']}\n"
        f"- Invalid rejection ratio: {metrics['invalid_probe_rejection_ratio']}\n\n"
        "This is a deterministic non-interlaced APNG partial-sample subset. "
        "It does not prove full APNG/PNG conformance, live editor rewrite "
        "preservation, or final production carrier selection.\n"
    )


def _failed_decode(family: str, message: str) -> dict:
    return {
        "ok": False,
        "errors": [_error("apng.partial_sample_frame_data", family, message)],
        "error_families": [family],
        "error_family": family,
    }


def _error(path: str, family: str, message: str | None = None) -> dict:
    return {
        "path": path,
        "family": family,
        "message": message or family.replace("_", " "),
    }


def _profile_id(slip_profile: dict | str) -> str:
    if isinstance(slip_profile, str):
        return slip_profile
    return slip_profile["profile_id"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("data/workshop_editor"),
    )
    parser.add_argument(
        "--generated-root",
        type=Path,
        default=DEFAULT_GENERATED_ROOT,
    )
    parser.add_argument("--profile", type=Path, action="append")
    args = parser.parse_args()
    report = run_apng_partial_sample_frame_data_lab(
        args.profile or list(DEFAULT_PROFILE_PATHS),
        args.generated_root,
    )
    paths = write_apng_partial_sample_frame_data_artifacts(args.output_root, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if paths["summary_json"] != REPORT_PATH:
        _write_json(REPORT_PATH, _json_report(report))
    if paths["app_js"] != DATA_PATH:
        DATA_PATH.write_text(
            "window.MECHAGOTCHI_APNG_PARTIAL_SAMPLE_FRAME_DATA = "
            + json.dumps(_app_payload(report), indent=2)
            + ";\n",
            encoding="utf-8",
        )
    if paths["artifact_dir"] != ARTIFACT_DIR:
        write_apng_partial_sample_frame_data_artifacts(Path("data/workshop_editor"), report)
    print(json.dumps(_json_report(report), indent=2))


if __name__ == "__main__":
    main()
