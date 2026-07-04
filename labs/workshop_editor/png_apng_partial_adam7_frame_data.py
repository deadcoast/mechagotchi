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

from standard_image_sidecar_decoder import PNG_SIGNATURE, render_grid_rgba_pixels

from png_adam7_deep_color_cross_product import (
    PNGAdam7DeepColorDecodeError,
    decode_png_adam7_deep_color,
)
from png_adam7_interlace_decoder import ADAM7_PASSES
from png_apng_adam7_frame_data import (
    _adapt_adam7_pixels,
    _adam7_frame_raw,
    _split_segments,
)
from png_apng_bit_depth_frame_data import (
    FILTER_TYPES,
    PNG_SOURCE_URL,
    _alternate_pixels,
    _decode_fctl,
    _first_grid_path,
    _pack_fctl,
    _parse_plte,
    _parse_trns,
    _portable,
)
from png_apng_partial_sample_frame_data import _alpha_over
from png_deep_color_sidecar_decoder import (
    _filter_bpp,
    _hash_bytes,
    _hash_pixels,
    _png_chunk,
    _read_json,
    _read_png_chunks,
    _ratio,
    _scanline_byte_length,
    _sorted_unique,
    _write_json,
)


REPORT_PATH = ROOT / "data/workshop_editor/apng_partial_adam7_frame_data_stage0.json"
DATA_PATH = ROOT / "data/workshop_editor/apng_partial_adam7_frame_data.js"
ARTIFACT_DIR = ROOT / "data/workshop_editor/apng_partial_adam7_frame_data_stage0"
DEFAULT_GENERATED_ROOT = ROOT / "data/slips/multi_profile_generation_stage0"
DEFAULT_PROFILE_PATHS = [
    ROOT / "data/slips/valid/slip_lcd_seed.json",
    ROOT / "data/slips/valid/slip_gray_stable.json",
    ROOT / "data/slips/valid/slip_amber_social.json",
]
TRANSPARENT_BLACK = (0, 0, 0, 0)
PATCH_WIDTH = 6
PATCH_HEIGHT = 6
PATCH_X = 1
PATCH_Y = 1

SUPPORTED_BIT_DEPTHS_BY_COLOR_TYPE = {
    0: {1},
    2: {16},
    3: {4},
    4: {16},
    6: {8, 16},
}

APNG_PARTIAL_ADAM7_CASE_SPECS = [
    {
        "case_id": "rgba8_adam7_source_patch",
        "color_type": 6,
        "bit_depth": 8,
        "blend_op": 0,
        "description": "8-bit truecolor-alpha partial APNG frame data with Adam7 pass reconstruction.",
    },
    {
        "case_id": "grayscale1_adam7_source_patch",
        "color_type": 0,
        "bit_depth": 1,
        "blend_op": 0,
        "description": "1-bit packed greyscale partial APNG frame data with Adam7 pass reconstruction.",
    },
    {
        "case_id": "indexed4_adam7_trns_source_patch",
        "color_type": 3,
        "bit_depth": 4,
        "blend_op": 0,
        "description": "4-bit indexed-color partial APNG frame data with PLTE/tRNS and Adam7 pass reconstruction.",
    },
    {
        "case_id": "truecolor16_adam7_source_patch",
        "color_type": 2,
        "bit_depth": 16,
        "blend_op": 0,
        "description": "16-bit truecolor partial APNG frame data with Adam7 pass reconstruction.",
    },
    {
        "case_id": "grayscale_alpha16_adam7_over_patch",
        "color_type": 4,
        "bit_depth": 16,
        "blend_op": 1,
        "description": "16-bit greyscale-alpha partial APNG frame data with Adam7 pass reconstruction and over blend.",
    },
    {
        "case_id": "truecolor_alpha16_adam7_over_patch",
        "color_type": 6,
        "bit_depth": 16,
        "blend_op": 1,
        "description": "16-bit truecolor-alpha partial APNG frame data with Adam7 pass reconstruction and over blend.",
    },
]

APNG_PARTIAL_ADAM7_CASE_IDS = [
    spec["case_id"] for spec in APNG_PARTIAL_ADAM7_CASE_SPECS
]


class APNGPartialAdam7FrameDataError(ValueError):
    def __init__(self, family: str, message: str):
        super().__init__(message)
        self.family = family
        self.message = message


def export_apng_partial_adam7_frame_data_cases(grid: dict, slip_profile: dict) -> list[dict]:
    width, height = grid["grid_size"]
    source = render_grid_rgba_pixels(grid)
    alternate = _alternate_pixels(source, width, height, slip_profile["profile_id"])
    patch = _extract_patch_pixels(alternate, width, PATCH_X, PATCH_Y, PATCH_WIDTH, PATCH_HEIGHT)
    cases = []
    for spec in APNG_PARTIAL_ADAM7_CASE_SPECS:
        frames = [
            _frame("base", width, height, 0, 0, spec, source, 1, 5, 0),
            _frame(
                "adam7_patch",
                PATCH_WIDTH,
                PATCH_HEIGHT,
                PATCH_X,
                PATCH_Y,
                spec,
                patch,
                1,
                10,
                spec["blend_op"],
            ),
        ]
        png_bytes = _encode_apng_partial_adam7_frame_data(width, height, spec, frames)
        expected = _simulate_playback(width, height, frames)
        decoded = decode_apng_partial_adam7_frame_data(png_bytes)
        cases.append(
            {
                "case_id": spec["case_id"],
                "description": spec["description"],
                "profile_id": slip_profile["profile_id"],
                "grid_id": grid["grid_id"],
                "color_type": spec["color_type"],
                "bit_depth": spec["bit_depth"],
                "blend_op": spec["blend_op"],
                "interlace_method": 1,
                "patch_width": PATCH_WIDTH,
                "patch_height": PATCH_HEIGHT,
                "x_offset": PATCH_X,
                "y_offset": PATCH_Y,
                "filter_types": list(FILTER_TYPES),
                "png_file_name": f"{slip_profile['profile_id']}_{spec['case_id']}.png",
                "png_bytes": png_bytes,
                "png_hash": _hash_bytes(png_bytes),
                "expected_frame_hashes": [_hash_pixels(frame["rgba_pixels"]) for frame in frames],
                "expected_display_hashes": expected["display_hashes"],
                "expected_final_hash": expected["final_canvas_hash"],
                "expected_pass_order": [pass_spec["pass_index"] for pass_spec in ADAM7_PASSES],
                "decoded": decoded,
            }
        )
    return cases


def decode_apng_partial_adam7_frame_data(png_bytes: bytes) -> dict:
    try:
        decoded = _decode_apng_partial_adam7_frame_data(png_bytes)
        decoded["ok"] = True
        decoded["errors"] = []
        decoded["error_families"] = []
        return decoded
    except APNGPartialAdam7FrameDataError as exc:
        return _failed_decode(exc.family, exc.message)
    except PNGAdam7DeepColorDecodeError as exc:
        return _failed_decode(_map_adam7_error_family(exc.family), exc.message)


def make_non_adam7_interlace_probe(png_bytes: bytes) -> bytes:
    return _rewrite_ihdr(png_bytes, interlace=0)


def make_out_of_bounds_probe(png_bytes: bytes) -> bytes:
    return _rewrite_fctl(
        png_bytes,
        frame_number=2,
        mutate=lambda frame, canvas: {
            **frame,
            "x_offset": canvas["width"],
        },
    )


def make_invalid_bit_depth_color_type_probe(png_bytes: bytes) -> bytes:
    return _rewrite_ihdr(png_bytes, bit_depth=4, color_type=2)


def make_truncated_partial_adam7_scanline_probe(png_bytes: bytes) -> bytes:
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
                raise APNGPartialAdam7FrameDataError("apng_fdat_invalid", "fdAT chunk is too short")
            sequence_number = struct.unpack(">I", payload[:4])[0] + 3
            payload = struct.pack(">I", sequence_number) + payload[4:]
            mutated = True
        rewritten.append(_png_chunk(chunk["type"].encode("ascii"), payload))
    if not mutated:
        raise APNGPartialAdam7FrameDataError("apng_fdat_missing", "expected fdAT chunk")
    return b"".join(rewritten)


def run_apng_partial_adam7_frame_data_lab(
    profile_paths: list[Path] | None = None,
    generated_root: Path = DEFAULT_GENERATED_ROOT,
) -> dict:
    profile_paths = profile_paths or DEFAULT_PROFILE_PATHS
    case_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        for case in export_apng_partial_adam7_frame_data_cases(grid, profile):
            decoded = case["decoded"]
            success = (
                decoded["ok"]
                and decoded["frame_pixel_hashes"] == case["expected_frame_hashes"]
                and decoded["display_hashes"] == case["expected_display_hashes"]
                and decoded["final_canvas_hash"] == case["expected_final_hash"]
                and decoded["color_type"] == case["color_type"]
                and decoded["bit_depth"] == case["bit_depth"]
                and decoded["interlace_method"] == 1
                and decoded["pass_order"] == case["expected_pass_order"]
            )
            case_results.append(
                {
                    "profile_id": profile["profile_id"],
                    "profile_path": _portable(profile_path),
                    "grid_id": grid["grid_id"],
                    "grid_path": _portable(grid_path),
                    "case_id": case["case_id"],
                    "description": case["description"],
                    "color_type": case["color_type"],
                    "bit_depth": case["bit_depth"],
                    "blend_op": case["blend_op"],
                    "interlace_method": case["interlace_method"],
                    "patch_width": case["patch_width"],
                    "patch_height": case["patch_height"],
                    "x_offset": case["x_offset"],
                    "y_offset": case["y_offset"],
                    "filter_types": case["filter_types"],
                    "png_file_name": case["png_file_name"],
                    "png_hash": case["png_hash"],
                    "png_bytes_hex": case["png_bytes"].hex(),
                    "expected_frame_hashes": case["expected_frame_hashes"],
                    "expected_display_hashes": case["expected_display_hashes"],
                    "expected_final_hash": case["expected_final_hash"],
                    "expected_pass_order": case["expected_pass_order"],
                    "decoded": _compact_decoded(decoded),
                    "success": success,
                }
            )

    invalid_results = _invalid_probe_results(case_results)
    success_count = sum(1 for result in case_results if result["success"])
    invalid_rejected_count = sum(1 for result in invalid_results if result["rejected"])
    return {
        "artifact_id": "apng_partial_adam7_frame_data_stage0",
        "status": "research_apng_partial_adam7_frame_data_no_package_code",
        "date": "2026-05-14",
        "purpose": (
            "Close a bounded APNG image-data gap for Adam7-interlaced partial "
            "frame regions with non-zero offsets without claiming full APNG/PNG conformance."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
            "labs/workshop_editor/png_apng_partial_sample_frame_data.py",
            "labs/workshop_editor/png_apng_adam7_frame_data.py",
            "labs/workshop_editor/png_apng_partial_adam7_frame_data.py",
        ],
        "external_anchors": [
            {
                "source": "W3C PNG specification",
                "url": PNG_SOURCE_URL,
                "used_for": (
                    "APNG frame offsets and source/over blend behavior, fcTL/fdAT "
                    "sequence numbering, frame-data inheritance, Adam7 pass "
                    "reconstruction, PNG filter method 0 reconstruction, and "
                    "selected packed/indexed/8-bit/16-bit sample decoding."
                ),
            }
        ],
        "profile_count": len(profile_paths),
        "case_ids": list(APNG_PARTIAL_ADAM7_CASE_IDS),
        "case_count": len(case_results),
        "case_success_count": success_count,
        "invalid_probe_count": len(invalid_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "case_results": case_results,
        "invalid_probe_results": invalid_results,
        "metrics": {
            "case_success_ratio": _ratio(success_count, len(case_results)),
            "invalid_probe_rejection_ratio": _ratio(invalid_rejected_count, len(invalid_results)),
            "profile_coverage": len({result["profile_id"] for result in case_results}),
            "case_family_count": len(APNG_PARTIAL_ADAM7_CASE_IDS),
            "supported_color_types": _sorted_unique(
                result["color_type"] for result in case_results
            ),
            "supported_bit_depths": _sorted_unique(
                result["bit_depth"] for result in case_results
            ),
            "supported_filter_types": list(FILTER_TYPES),
            "supported_interlace_methods": [1],
            "adam7_pass_count": len(ADAM7_PASSES),
            "partial_adam7_frame_count": sum(
                1
                for result in case_results
                for frame in result["decoded"].get("frames", [])
                if not frame.get("full_canvas", True)
            ),
            "split_fdat_frame_count": sum(
                1
                for result in case_results
                for frame in result["decoded"].get("frames", [])
                if frame.get("fdat_chunk_count") == 2
            ),
            "over_blend_case_count": sum(1 for result in case_results if result["blend_op"] == 1),
            "live_external_editor_verified": False,
        },
        "closed_states": [
            "apng_partial_adam7_offset_reconstruction",
            "apng_partial_adam7_pass_manifest_reconstruction",
            "apng_partial_adam7_deep_sample_reconstruction",
            "apng_partial_adam7_split_fdat_reconstruction",
            "apng_partial_adam7_invalid_probe_rejection",
        ],
        "blocked_states": [
            "full_apng_png_conformance",
            "live_external_editor_rewrite_validation",
            "production_import_export_carrier_selection_final_decision",
            "manual_readability_calibration",
            "package_runtime_lifecycle_integration",
        ],
        "decision": "prototype_apng_partial_adam7_frame_data_subset",
        "notes": [
            "This lab validates deterministic APNG partial frame data where the PNG image stream uses Adam7 interlace method 1.",
            "It covers a non-zero 6x6 patch offset so every Adam7 pass is non-empty for the second frame.",
            "It does not claim full APNG/PNG conformance, live editor preservation, or final production carrier selection.",
        ],
        "next_research_step": (
            "Keep remaining APNG/PNG work scoped to explicit image-data fixtures, "
            "live external editor preservation, or final carrier selection evidence "
            "before claiming full conformance."
        ),
    }


def write_apng_partial_adam7_frame_data_artifacts(
    output_root: Path = ROOT / "data/workshop_editor",
    report: dict | None = None,
) -> dict:
    report = report or run_apng_partial_adam7_frame_data_lab()
    output_root.mkdir(parents=True, exist_ok=True)
    artifact_dir = output_root / "apng_partial_adam7_frame_data_stage0"
    cases_dir = artifact_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)

    summary_json = output_root / "apng_partial_adam7_frame_data_stage0.json"
    app_js = output_root / "apng_partial_adam7_frame_data.js"
    artifact_summary_json = artifact_dir / "apng_partial_adam7_frame_data_stage0.json"
    artifact_app_js = artifact_dir / "apng_partial_adam7_frame_data.js"
    readme_path = artifact_dir / "README.md"

    json_payload = _json_report(report)
    _write_json(summary_json, json_payload)
    _write_json(artifact_summary_json, json_payload)
    app_payload = (
        "window.MECHAGOTCHI_APNG_PARTIAL_ADAM7_FRAME_DATA = "
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


def _decode_apng_partial_adam7_frame_data(png_bytes: bytes) -> dict:
    chunks = _read_png_chunks(png_bytes)
    if not chunks or chunks[0]["type"] != "IHDR":
        raise APNGPartialAdam7FrameDataError("png_ihdr_missing", "PNG IHDR chunk must be first")
    ihdr = _decode_ihdr(chunks[0]["payload"])
    plte = _parse_plte(chunks)
    trns = _parse_trns(chunks, ihdr["color_type"], ihdr["bit_depth"], plte)
    names = [chunk["type"] for chunk in chunks]
    actl_chunks = [chunk for chunk in chunks if chunk["type"] == "acTL"]
    if len(actl_chunks) != 1 or len(actl_chunks[0]["payload"]) != 8:
        raise APNGPartialAdam7FrameDataError(
            "apng_control_invalid",
            "APNG acTL chunk must be present, unique, and 8 bytes",
        )
    if "IDAT" not in names:
        raise APNGPartialAdam7FrameDataError("apng_idat_missing", "APNG default IDAT chunk must be present")
    if names.index("acTL") > names.index("IDAT"):
        raise APNGPartialAdam7FrameDataError("apng_actl_after_idat", "APNG acTL must appear before IDAT")
    expected_frame_count, num_plays = struct.unpack(">II", actl_chunks[0]["payload"])
    if expected_frame_count <= 0:
        raise APNGPartialAdam7FrameDataError("apng_frame_count_invalid", "APNG frame count must be positive")

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
                raise APNGPartialAdam7FrameDataError(
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
                raise APNGPartialAdam7FrameDataError(
                    "apng_default_frame_control_missing",
                    "APNG default IDAT requires preceding fcTL",
                )
            if current["data_source"] not in {None, "IDAT"}:
                raise APNGPartialAdam7FrameDataError("apng_idat_order_invalid", "IDAT order is invalid")
            current["data"].extend(payload)
            current["data_source"] = "IDAT"
            idat_seen = True
            animation_chunk_order.append("IDAT")
        elif chunk_type == "fdAT":
            if current is None:
                raise APNGPartialAdam7FrameDataError("apng_fdat_without_fctl", "fdAT requires preceding fcTL")
            if not idat_seen:
                raise APNGPartialAdam7FrameDataError("apng_fdat_before_idat", "fdAT must not precede IDAT")
            if len(payload) < 4:
                raise APNGPartialAdam7FrameDataError("apng_fdat_invalid", "fdAT chunk must include a sequence number")
            sequence_number = struct.unpack(">I", payload[:4])[0]
            if sequence_number != expected_sequence:
                raise APNGPartialAdam7FrameDataError(
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
        raise APNGPartialAdam7FrameDataError(
            "apng_frame_count_mismatch",
            "acTL frame count does not match fcTL chunks",
        )

    playback = _simulate_playback(ihdr["width"], ihdr["height"], frames)
    pass_order = [pass_spec["pass_index"] for pass_spec in ADAM7_PASSES]
    filter_types_seen = []
    for frame in frames:
        for filter_type in frame["filter_types_seen"]:
            if filter_type not in filter_types_seen:
                filter_types_seen.append(filter_type)
    return {
        "ihdr": dict(ihdr),
        "canvas_width": ihdr["width"],
        "canvas_height": ihdr["height"],
        "bit_depth": ihdr["bit_depth"],
        "color_type": ihdr["color_type"],
        "interlace_method": ihdr["interlace"],
        "bytes_per_pixel": _filter_bpp(ihdr["color_type"], ihdr["bit_depth"]),
        "scanline_byte_length": _scanline_byte_length(
            ihdr["width"],
            ihdr["color_type"],
            ihdr["bit_depth"],
        ),
        "filter_bpp": _filter_bpp(ihdr["color_type"], ihdr["bit_depth"]),
        "pass_order": pass_order,
        "filter_types_seen": filter_types_seen,
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
        raise APNGPartialAdam7FrameDataError("apng_frame_data_missing", "APNG frame has no image data")
    frame_ihdr = struct.pack(
        ">IIBBBBB",
        frame["width"],
        frame["height"],
        ihdr["bit_depth"],
        ihdr["color_type"],
        ihdr["compression"],
        ihdr["filter_method"],
        ihdr["interlace"],
    )
    chunks = [PNG_SIGNATURE, _png_chunk(b"IHDR", frame_ihdr)]
    if ihdr["color_type"] == 3:
        chunks.append(_png_chunk(b"PLTE", b"".join(bytes(rgb) for rgb in plte)))
        if trns:
            chunks.append(_png_chunk(b"tRNS", trns))
    chunks.extend(
        [
            _png_chunk(b"IDAT", bytes(frame["data"])),
            _png_chunk(b"IEND", b""),
        ]
    )
    try:
        decoded = decode_png_adam7_deep_color(b"".join(chunks))
    except PNGAdam7DeepColorDecodeError as exc:
        raise APNGPartialAdam7FrameDataError(
            _map_adam7_error_family(exc.family),
            exc.message,
        ) from exc
    frame["rgba_pixels"] = decoded["pixels"]
    frame["filter_types_seen"] = decoded["filter_types_seen"]
    frame["pass_order"] = decoded["pass_order"]
    frame["pass_summaries"] = decoded["pass_summaries"]
    frame["non_empty_pass_count"] = decoded["non_empty_pass_count"]
    frames.append(frame)


def _encode_apng_partial_adam7_frame_data(
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
                1,
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
        compressed = zlib.compress(_adam7_frame_raw(frame, spec))
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
    pixels: list[tuple[int, int, int, int]],
    delay_num: int,
    delay_den: int,
    blend_op: int,
) -> dict:
    adapted = _adapt_adam7_pixels(pixels, spec, width, height)
    return {
        "frame_id": frame_id,
        "width": width,
        "height": height,
        "x_offset": x_offset,
        "y_offset": y_offset,
        "color_type": spec["color_type"],
        "bit_depth": spec["bit_depth"],
        "prepared_pixels": adapted["prepared_pixels"],
        "rgba_pixels": adapted["rgba_pixels"],
        "plte": adapted["plte"],
        "trns": adapted["trns"],
        "delay_num": delay_num,
        "delay_den": delay_den,
        "dispose_op": 0,
        "blend_op": blend_op,
    }


def _decode_ihdr(data: bytes) -> dict:
    if len(data) != 13:
        raise APNGPartialAdam7FrameDataError("png_ihdr_invalid", "PNG IHDR chunk length must be 13")
    width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(">IIBBBBB", data)
    if width <= 0 or height <= 0:
        raise APNGPartialAdam7FrameDataError("png_ihdr_invalid", "PNG dimensions must be positive")
    if color_type not in SUPPORTED_BIT_DEPTHS_BY_COLOR_TYPE:
        raise APNGPartialAdam7FrameDataError(
            "png_color_type_unsupported",
            "PNG color type must be one of 0, 2, 3, 4, or 6",
        )
    if bit_depth not in SUPPORTED_BIT_DEPTHS_BY_COLOR_TYPE[color_type]:
        raise APNGPartialAdam7FrameDataError(
            "png_bit_depth_color_type_invalid",
            "PNG bit depth is not allowed for this APNG partial Adam7 lab color type",
        )
    if compression != 0 or filter_method != 0:
        raise APNGPartialAdam7FrameDataError(
            "png_method_unsupported",
            "Stage 0 APNG partial Adam7 matrix supports compression 0 and filter method 0 only",
        )
    if interlace != 1:
        raise APNGPartialAdam7FrameDataError(
            "apng_adam7_interlace_required",
            "Stage 0 APNG partial Adam7 frame-data matrix requires interlace method 1",
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
        raise APNGPartialAdam7FrameDataError(
            "apng_frame_dimensions_invalid",
            "APNG frame dimensions must be positive",
        )
    if (
        frame["x_offset"] + frame["width"] > ihdr["width"]
        or frame["y_offset"] + frame["height"] > ihdr["height"]
    ):
        raise APNGPartialAdam7FrameDataError(
            "apng_frame_bounds_invalid",
            "APNG frame bounds exceed the canvas",
        )
    if frame["dispose_op"] not in {0, 1, 2}:
        raise APNGPartialAdam7FrameDataError("apng_dispose_op_invalid", "APNG dispose_op must be 0, 1, or 2")
    if frame["blend_op"] not in {0, 1}:
        raise APNGPartialAdam7FrameDataError("apng_blend_op_invalid", "APNG blend_op must be 0 or 1")
    if default_frame and (
        frame["x_offset"] != 0
        or frame["y_offset"] != 0
        or frame["width"] != ihdr["width"]
        or frame["height"] != ihdr["height"]
        or frame["blend_op"] != 0
    ):
        raise APNGPartialAdam7FrameDataError(
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


def _extract_patch_pixels(
    pixels: list[tuple[int, int, int, int]],
    canvas_width: int,
    x_offset: int,
    y_offset: int,
    width: int,
    height: int,
) -> list[tuple[int, int, int, int]]:
    patch = []
    for y in range(height):
        start = (y_offset + y) * canvas_width + x_offset
        patch.extend(pixels[start : start + width])
    return patch


def _rewrite_ihdr(
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


def _rewrite_fctl(png_bytes: bytes, *, frame_number: int, mutate) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    ihdr = _decode_ihdr(chunks[0]["payload"])
    canvas = {"width": ihdr["width"], "height": ihdr["height"]}
    rewritten = [PNG_SIGNATURE]
    seen = 0
    for chunk in chunks:
        payload = chunk["payload"]
        if chunk["type"] == "fcTL":
            seen += 1
            if seen == frame_number:
                payload = _pack_fctl(mutate(_decode_fctl(payload), canvas))
        rewritten.append(_png_chunk(chunk["type"].encode("ascii"), payload))
    if seen < frame_number:
        raise APNGPartialAdam7FrameDataError("apng_fctl_missing", "requested fcTL chunk is missing")
    return b"".join(rewritten)


def _rewrite_second_frame_fdat_raw(png_bytes: bytes, mutate) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    fdat_chunks = [chunk for chunk in chunks if chunk["type"] == "fdAT"]
    if not fdat_chunks:
        raise APNGPartialAdam7FrameDataError("apng_fdat_missing", "expected fdAT chunk")
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


def _invalid_probe_results(case_results: list[dict]) -> list[dict]:
    by_case = {result["case_id"]: bytes.fromhex(result["png_bytes_hex"]) for result in case_results}
    probes = [
        (
            "non_adam7_interlace",
            make_non_adam7_interlace_probe(by_case["rgba8_adam7_source_patch"]),
            "apng_adam7_interlace_required",
        ),
        (
            "out_of_bounds_partial_adam7_frame",
            make_out_of_bounds_probe(by_case["grayscale1_adam7_source_patch"]),
            "apng_frame_bounds_invalid",
        ),
        (
            "invalid_bit_depth_color_type",
            make_invalid_bit_depth_color_type_probe(by_case["truecolor16_adam7_source_patch"]),
            "png_bit_depth_color_type_invalid",
        ),
        (
            "truncated_partial_adam7_scanline",
            make_truncated_partial_adam7_scanline_probe(by_case["grayscale1_adam7_source_patch"]),
            "apng_partial_adam7_scanline_length_mismatch",
        ),
        (
            "invalid_filter_type",
            make_invalid_filter_probe(by_case["grayscale_alpha16_adam7_over_patch"]),
            "png_filter_type_unsupported",
        ),
        (
            "fdat_sequence_gap",
            make_sequence_gap_probe(by_case["truecolor_alpha16_adam7_over_patch"]),
            "apng_sequence_number_invalid",
        ),
    ]
    results = []
    for probe_id, png_bytes, expected_family in probes:
        decoded = decode_apng_partial_adam7_frame_data(png_bytes)
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
        "pass_order": frame.get("pass_order", [pass_spec["pass_index"] for pass_spec in ADAM7_PASSES]),
        "pass_summaries": frame.get("pass_summaries", []),
        "non_empty_pass_count": frame.get("non_empty_pass_count", 0),
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
            "interlace_method",
            "bytes_per_pixel",
            "scanline_byte_length",
            "filter_bpp",
            "pass_order",
            "filter_types_seen",
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
                "bit_depth": result["bit_depth"],
                "blend_op": result["blend_op"],
                "interlace_method": result["interlace_method"],
                "x_offset": result["x_offset"],
                "y_offset": result["y_offset"],
                "patch_width": result["patch_width"],
                "patch_height": result["patch_height"],
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
        "# APNG Partial Adam7 Frame Data Stage 0\n\n"
        "Bounded APNG partial-frame Adam7 matrix for Mechagotchi workshop carriers.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Case successes: {report['case_success_count']}/{report['case_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- Supported color types: {metrics['supported_color_types']}\n"
        f"- Supported bit depths: {metrics['supported_bit_depths']}\n"
        f"- Partial Adam7 frames: {metrics['partial_adam7_frame_count']}\n"
        f"- Split fdAT frames: {metrics['split_fdat_frame_count']}\n"
        f"- Adam7 pass count: {metrics['adam7_pass_count']}\n"
        f"- Success ratio: {metrics['case_success_ratio']}\n"
        f"- Invalid rejection ratio: {metrics['invalid_probe_rejection_ratio']}\n\n"
        "This is a deterministic APNG partial Adam7 frame-data subset. It does "
        "not prove full APNG/PNG conformance, live editor rewrite preservation, "
        "or final production carrier selection.\n"
    )


def _map_adam7_error_family(family: str) -> str:
    return {
        "png_adam7_deep_color_interlace_required": "apng_adam7_interlace_required",
        "png_adam7_deep_color_scanline_length_mismatch": "apng_partial_adam7_scanline_length_mismatch",
        "png_adam7_deep_color_pixel_coverage_incomplete": "apng_partial_adam7_pixel_coverage_incomplete",
    }.get(family, family)


def _failed_decode(family: str, message: str) -> dict:
    return {
        "ok": False,
        "errors": [_error("apng.partial_adam7_frame_data", family, message)],
        "error_families": [family],
        "error_family": family,
    }


def _error(path: str, family: str, message: str | None = None) -> dict:
    return {
        "path": path,
        "family": family,
        "message": message or family.replace("_", " "),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ROOT / "data/workshop_editor",
    )
    parser.add_argument(
        "--generated-root",
        type=Path,
        default=DEFAULT_GENERATED_ROOT,
    )
    parser.add_argument("--profile", type=Path, action="append")
    args = parser.parse_args()
    report = run_apng_partial_adam7_frame_data_lab(
        args.profile or list(DEFAULT_PROFILE_PATHS),
        args.generated_root,
    )
    write_apng_partial_adam7_frame_data_artifacts(args.output_root, report)


if __name__ == "__main__":
    main()
