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

from png_apng_filtered_frame_data import (
    decode_apng_filtered_frame_data,
    _encode_apng,
    _frame,
)
from png_apng_image_data_chunking import (
    _combined_fdat_frame_data,
    _combined_idat_data,
    _read_chunks,
    _replace_fdat_chunks,
    _replace_idat_chunks,
)
from png_deep_color_sidecar_decoder import (
    PNGDeepColorDecodeError,
    _encode_png_deep_color,
    _hash_pixels,
    _png_chunk,
    _read_json,
    _ratio,
    _write_json,
    decode_png_deep_color,
)
from standard_image_sidecar_decoder import PNG_SIGNATURE, render_grid_rgba_pixels


REPORT_PATH = ROOT / "data/workshop_editor/png_apng_zlib_compression_stage0.json"
DATA_PATH = ROOT / "data/workshop_editor/png_apng_zlib_compression.js"
ARTIFACT_DIR = ROOT / "data/workshop_editor/png_apng_zlib_compression_stage0"
PNG_SOURCE_URL = "https://www.w3.org/TR/png-3/"
ZLIB_SOURCE_URL = "https://www.rfc-editor.org/rfc/rfc1950"
DEFLATE_SOURCE_URL = "https://www.rfc-editor.org/rfc/rfc1951"

PNG_APNG_ZLIB_COMPRESSION_CASE_IDS = [
    "png_zlib_stored_blocks",
    "png_zlib_fixed_huffman",
    "png_zlib_filtered_strategy",
    "apng_fdat_zlib_stored_blocks",
    "apng_fdat_zlib_fixed_huffman",
    "apng_fdat_zlib_rle_strategy",
]

ZLIB_STRATEGY_SPECS = {
    "stored_blocks": {
        "level": 0,
        "strategy": zlib.Z_DEFAULT_STRATEGY,
        "zlib_strategy_name": "Z_DEFAULT_STRATEGY",
        "deflate_block_family": "stored_blocks",
        "description": "level-0 zlib stream using non-compressed DEFLATE blocks",
    },
    "fixed_huffman": {
        "level": 9,
        "strategy": zlib.Z_FIXED,
        "zlib_strategy_name": "Z_FIXED",
        "deflate_block_family": "fixed_huffman",
        "description": "zlib stream constrained to fixed Huffman DEFLATE coding",
    },
    "filtered_strategy": {
        "level": 9,
        "strategy": zlib.Z_FILTERED,
        "zlib_strategy_name": "Z_FILTERED",
        "deflate_block_family": "filtered_strategy",
        "description": "zlib stream compressed with the PNG-oriented filtered strategy",
    },
    "rle_strategy": {
        "level": 9,
        "strategy": zlib.Z_RLE,
        "zlib_strategy_name": "Z_RLE",
        "deflate_block_family": "rle_strategy",
        "description": "zlib stream compressed with run-length-biased strategy",
    },
}


class PNGAPNGZlibCompressionError(ValueError):
    def __init__(self, family: str, message: str):
        super().__init__(message)
        self.family = family
        self.message = message


def export_png_apng_zlib_compression_cases(grid: dict, slip_profile: dict) -> list[dict]:
    width, height = grid["grid_size"]
    source_pixels = render_grid_rgba_pixels(grid)
    static_png = _encode_png_deep_color(
        width,
        height,
        source_pixels,
        {"color_type": 6, "bit_depth": 8, "filter_types": [0, 1, 2, 3, 4]},
    )
    static_raw = zlib.decompress(_combined_idat_data(static_png))
    apng_source = _full_canvas_apng_source(width, height, source_pixels)
    apng_raw = zlib.decompress(_combined_fdat_frame_data(apng_source))

    case_specs = [
        _case_spec(
            "png_zlib_stored_blocks",
            "png",
            "stored_blocks",
            static_png,
            static_raw,
            "Static PNG IDAT recompressed as a zlib level-0 stored-block datastream.",
        ),
        _case_spec(
            "png_zlib_fixed_huffman",
            "png",
            "fixed_huffman",
            static_png,
            static_raw,
            "Static PNG IDAT recompressed with fixed Huffman DEFLATE coding.",
        ),
        _case_spec(
            "png_zlib_filtered_strategy",
            "png",
            "filtered_strategy",
            static_png,
            static_raw,
            "Static PNG IDAT recompressed with the zlib filtered strategy.",
        ),
        _case_spec(
            "apng_fdat_zlib_stored_blocks",
            "apng",
            "stored_blocks",
            apng_source,
            apng_raw,
            "APNG second-frame fdAT frame_data recompressed as a zlib level-0 stored-block datastream.",
        ),
        _case_spec(
            "apng_fdat_zlib_fixed_huffman",
            "apng",
            "fixed_huffman",
            apng_source,
            apng_raw,
            "APNG second-frame fdAT frame_data recompressed with fixed Huffman DEFLATE coding.",
        ),
        _case_spec(
            "apng_fdat_zlib_rle_strategy",
            "apng",
            "rle_strategy",
            apng_source,
            apng_raw,
            "APNG second-frame fdAT frame_data recompressed with the zlib RLE strategy.",
        ),
    ]

    cases = []
    for spec in case_specs:
        if spec["carrier_family"] == "png":
            png_bytes = _replace_idat_chunks(spec["source_png"], [spec["compressed"]])
        else:
            png_bytes = _replace_fdat_chunks(
                spec["source_png"],
                _split_payload(spec["compressed"], 2),
            )
        decoded = decode_png_apng_zlib_compression(png_bytes)
        if not decoded["ok"]:
            raise PNGAPNGZlibCompressionError(
                decoded["error_family"],
                f"generated case {spec['case_id']} failed to decode",
            )
        cases.append(
            {
                "case_id": spec["case_id"],
                "description": spec["description"],
                "profile_id": slip_profile["profile_id"],
                "grid_id": grid["grid_id"],
                "carrier_family": spec["carrier_family"],
                "compression_strategy_id": spec["compression_strategy_id"],
                "zlib_level": spec["zlib_level"],
                "zlib_strategy_name": spec["zlib_strategy_name"],
                "deflate_block_family": spec["deflate_block_family"],
                "png_file_name": f"{slip_profile['profile_id']}_{spec['case_id']}.png",
                "png_bytes": png_bytes,
                "png_hash": _hash_bytes(png_bytes),
                "expected_pixel_hash": decoded["pixel_hash"],
                "expected_raw_image_data_hash": decoded["raw_image_data_hash"],
                "expected_compressed_data_hash": decoded["compressed_data_hash"],
                "expected_data_chunk_count": decoded["data_chunk_count"],
                "expected_idat_chunk_count": decoded["idat_chunk_count"],
                "expected_fdat_chunk_count": decoded["fdat_chunk_count"],
                "expected_zlib_header": decoded["zlib_header"],
                "decoded": decoded,
            }
        )
    return cases


def decode_png_apng_zlib_compression(png_bytes: bytes) -> dict:
    try:
        decoded = _decode_png_apng_zlib_compression(png_bytes)
        decoded["ok"] = True
        decoded["errors"] = []
        decoded["error_families"] = []
        return decoded
    except PNGAPNGZlibCompressionError as exc:
        return {
            "ok": False,
            "errors": [_error("png_apng.zlib_compression", exc.family, exc.message)],
            "error_families": [exc.family],
            "error_family": exc.family,
        }


def make_invalid_compression_method_probe(png_bytes: bytes) -> bytes:
    chunks = _safe_read_chunks(png_bytes)
    rewritten = [PNG_SIGNATURE]
    mutated = False
    for chunk in chunks:
        payload = chunk["payload"]
        if chunk["type"] == "IHDR" and not mutated:
            if len(payload) != 13:
                raise PNGAPNGZlibCompressionError("png_ihdr_invalid", "IHDR payload must be 13 bytes")
            mutable = bytearray(payload)
            mutable[10] = 1
            payload = bytes(mutable)
            mutated = True
        rewritten.append(_png_chunk(chunk["type"].encode("ascii"), payload))
    if not mutated:
        raise PNGAPNGZlibCompressionError("png_ihdr_missing", "expected IHDR chunk")
    return b"".join(rewritten)


def make_corrupt_idat_zlib_header_probe(png_bytes: bytes) -> bytes:
    return _mutate_data_chunk_byte(png_bytes, "IDAT", payload_offset=0, from_end=False)


def make_truncated_idat_probe(png_bytes: bytes) -> bytes:
    return _truncate_data_chunk(png_bytes, "IDAT", data_offset=0)


def make_truncated_fdat_probe(png_bytes: bytes) -> bytes:
    return _truncate_data_chunk(png_bytes, "fdAT", data_offset=4)


def make_corrupt_fdat_adler_probe(png_bytes: bytes) -> bytes:
    return _mutate_data_chunk_byte(png_bytes, "fdAT", payload_offset=0, from_end=True)


def make_sequence_gap_probe(png_bytes: bytes) -> bytes:
    chunks = _safe_read_chunks(png_bytes)
    rewritten = [PNG_SIGNATURE]
    mutated = False
    for chunk in chunks:
        payload = chunk["payload"]
        if chunk["type"] == "fdAT" and not mutated:
            if len(payload) < 4:
                raise PNGAPNGZlibCompressionError("apng_fdat_invalid", "fdAT chunk is too short")
            sequence_number = struct.unpack(">I", payload[:4])[0] + 1
            payload = struct.pack(">I", sequence_number) + payload[4:]
            mutated = True
        rewritten.append(_png_chunk(chunk["type"].encode("ascii"), payload))
    if not mutated:
        raise PNGAPNGZlibCompressionError("apng_fdat_missing", "expected fdAT chunk")
    return b"".join(rewritten)


def run_png_apng_zlib_compression_lab(
    profile_paths: list[Path] | None = None,
    generated_root: Path | None = None,
) -> dict:
    profile_paths = profile_paths or [
        ROOT / "data/slips/valid/slip_lcd_seed.json",
        ROOT / "data/slips/valid/slip_gray_stable.json",
        ROOT / "data/slips/valid/slip_amber_social.json",
    ]
    generated_root = generated_root or ROOT / "data/slips/multi_profile_generation_stage0"

    case_results = []
    first_profile_cases = None
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid = _read_json(_first_grid_path(profile, generated_root))
        cases = export_png_apng_zlib_compression_cases(grid, profile)
        if first_profile_cases is None:
            first_profile_cases = cases
        for case in cases:
            decoded = case["decoded"]
            success = (
                decoded["ok"]
                and decoded["pixel_hash"] == case["expected_pixel_hash"]
                and decoded["raw_image_data_hash"] == case["expected_raw_image_data_hash"]
                and decoded["compressed_data_hash"] == case["expected_compressed_data_hash"]
                and decoded["ihdr_compression_method"] == 0
                and decoded["zlib_header"]["compression_method"] == 8
                and decoded["zlib_header"]["cmf_flg_check_passed"]
            )
            case_results.append(
                {
                    "profile_id": profile["profile_id"],
                    "grid_id": grid["grid_id"],
                    "case_id": case["case_id"],
                    "description": case["description"],
                    "carrier_family": case["carrier_family"],
                    "compression_strategy_id": case["compression_strategy_id"],
                    "zlib_level": case["zlib_level"],
                    "zlib_strategy_name": case["zlib_strategy_name"],
                    "deflate_block_family": case["deflate_block_family"],
                    "png_file_name": case["png_file_name"],
                    "png_hash": case["png_hash"],
                    "png_bytes_hex": case["png_bytes"].hex(),
                    "expected_pixel_hash": case["expected_pixel_hash"],
                    "expected_raw_image_data_hash": case["expected_raw_image_data_hash"],
                    "expected_compressed_data_hash": case["expected_compressed_data_hash"],
                    "expected_zlib_header": case["expected_zlib_header"],
                    "decoded": _compact_decoded(decoded),
                    "success": success,
                }
            )

    invalid_results = _invalid_probe_results(first_profile_cases or [])
    success_count = sum(1 for result in case_results if result["success"])
    invalid_rejected_count = sum(1 for result in invalid_results if result["rejected"])
    return {
        "artifact_id": "png_apng_zlib_compression_stage0",
        "status": "research_png_apng_zlib_compression_no_package_code",
        "date": "2026-05-14",
        "purpose": (
            "Close a bounded PNG/APNG image-data gap by proving that selected "
            "valid zlib-wrapped DEFLATE variants preserve static PNG IDAT and "
            "APNG fdAT decoded pixels when the uncompressed scanline payload is "
            "unchanged."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
            "labs/workshop_editor/png_deep_color_sidecar_decoder.py",
            "labs/workshop_editor/png_apng_filtered_frame_data.py",
            "labs/workshop_editor/png_apng_image_data_chunking.py",
            "labs/workshop_editor/png_apng_zlib_compression_matrix.py",
        ],
        "external_anchors": [
            {
                "source": "W3C PNG specification",
                "url": PNG_SOURCE_URL,
                "used_for": (
                    "PNG compression method 0, IDAT image-data storage, APNG "
                    "fdAT frame_data inheritance from IDAT, and APNG sequence "
                    "number validation."
                ),
            },
            {
                "source": "RFC 1950 zlib compressed data format",
                "url": ZLIB_SOURCE_URL,
                "used_for": (
                    "zlib stream header/trailer structure, CM=8 deflate method, "
                    "Adler-32 validation, and decompressor error expectations."
                ),
            },
            {
                "source": "RFC 1951 DEFLATE compressed data format",
                "url": DEFLATE_SOURCE_URL,
                "used_for": (
                    "DEFLATE block families covering non-compressed blocks, "
                    "fixed Huffman coding, and dynamic/strategy-dependent streams."
                ),
            },
        ],
        "profile_count": len(profile_paths),
        "case_ids": list(PNG_APNG_ZLIB_COMPRESSION_CASE_IDS),
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
            "case_family_count": len(PNG_APNG_ZLIB_COMPRESSION_CASE_IDS),
            "png_case_count": sum(1 for result in case_results if result["carrier_family"] == "png"),
            "apng_case_count": sum(1 for result in case_results if result["carrier_family"] == "apng"),
            "zlib_strategy_family_count": len(
                {result["compression_strategy_id"] for result in case_results}
            ),
            "ihdr_compression_method_0_count": sum(
                1 for result in case_results if result["decoded"]["ihdr_compression_method"] == 0
            ),
            "zlib_cm8_case_count": sum(
                1
                for result in case_results
                if result["decoded"]["zlib_header"]["compression_method"] == 8
            ),
            "split_fdat_case_count": sum(
                1
                for result in case_results
                if result["carrier_family"] == "apng" and result["decoded"]["fdat_chunk_count"] == 2
            ),
            "stored_block_case_count": sum(
                1 for result in case_results if result["deflate_block_family"] == "stored_blocks"
            ),
            "fixed_huffman_case_count": sum(
                1 for result in case_results if result["deflate_block_family"] == "fixed_huffman"
            ),
            "live_external_editor_verified": False,
        },
        "closed_states": [
            "png_idat_zlib_deflate_variant_reconstruction",
            "apng_fdat_zlib_deflate_variant_reconstruction",
            "png_apng_zlib_header_and_adler_error_rejection",
            "png_apng_zlib_compression_invalid_probe_rejection",
        ],
        "blocked_states": [
            "full_apng_png_conformance",
            "live_external_editor_rewrite_validation",
            "production_import_export_carrier_selection_final_decision",
            "manual_readability_calibration",
            "package_runtime_lifecycle_integration",
        ],
        "decision": "prototype_png_apng_zlib_compression_subset",
        "notes": [
            "This lab validates selected zlib-wrapped DEFLATE variants only; it does not inspect every possible DEFLATE block graph.",
            "The static PNG cases keep the same uncompressed RGBA scanline payload and replace only the IDAT zlib stream.",
            "The APNG cases keep the same second-frame uncompressed RGBA scanline payload and replace only split fdAT frame_data.",
            "The strategy labels record the compressor configuration used to produce the stream; PNG decoders are required to decode the resulting zlib/deflate stream, not recover the encoder strategy.",
        ],
        "next_research_step": (
            "Continue remaining APNG/PNG coverage through additional explicit "
            "image-data conformance fixtures such as preset-dictionary "
            "rejection, wider color/interlace cross-products, live external "
            "editor preservation, or final carrier selection evidence before "
            "claiming full conformance."
        ),
    }


def write_png_apng_zlib_compression_artifacts(
    output_root: Path = ROOT / "data/workshop_editor",
    report: dict | None = None,
) -> dict:
    report = report or run_png_apng_zlib_compression_lab()
    output_root.mkdir(parents=True, exist_ok=True)
    artifact_dir = output_root / "png_apng_zlib_compression_stage0"
    cases_dir = artifact_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)

    summary_json = output_root / "png_apng_zlib_compression_stage0.json"
    app_js = output_root / "png_apng_zlib_compression.js"
    artifact_summary_json = artifact_dir / "png_apng_zlib_compression_stage0.json"
    artifact_app_js = artifact_dir / "png_apng_zlib_compression.js"
    readme = artifact_dir / "README.md"

    _write_json(summary_json, _json_report(report))
    _write_json(artifact_summary_json, _json_report(report))
    for result in report["case_results"]:
        (cases_dir / result["png_file_name"]).write_bytes(
            bytes.fromhex(result["png_bytes_hex"])
        )
    payload = (
        "window.MECHAGOTCHI_PNG_APNG_ZLIB_COMPRESSION = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n"
    )
    app_js.write_text(payload, encoding="utf-8")
    artifact_app_js.write_text(payload, encoding="utf-8")
    readme.write_text(_readme_text(report), encoding="utf-8")
    return {
        "summary_json": summary_json,
        "app_js": app_js,
        "artifact_dir": artifact_dir,
        "artifact_summary_json": artifact_summary_json,
        "artifact_app_js": artifact_app_js,
        "readme": readme,
    }


def _decode_png_apng_zlib_compression(png_bytes: bytes) -> dict:
    chunks = _safe_read_chunks(png_bytes)
    names = [chunk["type"] for chunk in chunks]
    ihdr = _ihdr_summary(chunks)
    idat_data_lengths = [len(chunk["payload"]) for chunk in chunks if chunk["type"] == "IDAT"]
    fdat_frame_data_lengths = [
        max(0, len(chunk["payload"]) - 4)
        for chunk in chunks
        if chunk["type"] == "fdAT"
    ]
    is_apng = "acTL" in names

    if is_apng:
        decoded = decode_apng_filtered_frame_data(png_bytes)
        if not decoded["ok"]:
            family = decoded["error_families"][0] if decoded.get("error_families") else "apng_decode_failed"
            raise PNGAPNGZlibCompressionError(family, family.replace("_", " "))
        compressed = _combined_fdat_frame_data(png_bytes)
        raw = _decompress_stream(compressed, "apng_frame_decompression_failed")
        return {
            "carrier_family": "apng",
            "ihdr_compression_method": ihdr["compression_method"],
            "canvas_width": decoded["canvas_width"],
            "canvas_height": decoded["canvas_height"],
            "frame_count": decoded["frame_count"],
            "animation_control": decoded["animation_control"],
            "pixel_hash": decoded["final_output_hash"],
            "display_hashes": decoded["display_hashes"],
            "final_output_hash": decoded["final_output_hash"],
            "raw_image_data_hash": _hash_bytes(raw),
            "raw_image_data_length": len(raw),
            "compressed_data_hash": _hash_bytes(compressed),
            "compressed_data_length": len(compressed),
            "zlib_header": _zlib_header_summary(compressed),
            "idat_data_lengths": idat_data_lengths,
            "fdat_frame_data_lengths": fdat_frame_data_lengths,
            "idat_chunk_count": len(idat_data_lengths),
            "fdat_chunk_count": len(fdat_frame_data_lengths),
            "data_chunk_count": len(idat_data_lengths) + len(fdat_frame_data_lengths),
            "chunks": names,
            "animation_chunk_order": decoded["animation_chunk_order"],
        }

    try:
        decoded = decode_png_deep_color(png_bytes)
    except PNGDeepColorDecodeError as exc:
        raise PNGAPNGZlibCompressionError(_map_png_error_family(exc.family), exc.message) from exc
    compressed = _combined_idat_data(png_bytes)
    raw = _decompress_stream(compressed, "png_image_data_decompression_failed")
    return {
        "carrier_family": "png",
        "ihdr_compression_method": ihdr["compression_method"],
        "width": decoded["width"],
        "height": decoded["height"],
        "pixel_hash": _hash_pixels(decoded["pixels"]),
        "raw_image_data_hash": _hash_bytes(raw),
        "raw_image_data_length": len(raw),
        "compressed_data_hash": _hash_bytes(compressed),
        "compressed_data_length": len(compressed),
        "zlib_header": _zlib_header_summary(compressed),
        "idat_data_lengths": idat_data_lengths,
        "fdat_frame_data_lengths": [],
        "idat_chunk_count": len(idat_data_lengths),
        "fdat_chunk_count": 0,
        "data_chunk_count": len(idat_data_lengths),
        "chunks": names,
        "filter_types_seen": decoded["filter_types_seen"],
    }


def _case_spec(
    case_id: str,
    carrier_family: str,
    strategy_id: str,
    source_png: bytes,
    raw: bytes,
    description: str,
) -> dict:
    strategy = ZLIB_STRATEGY_SPECS[strategy_id]
    return {
        "case_id": case_id,
        "carrier_family": carrier_family,
        "compression_strategy_id": strategy_id,
        "zlib_level": strategy["level"],
        "zlib_strategy_name": strategy["zlib_strategy_name"],
        "deflate_block_family": strategy["deflate_block_family"],
        "source_png": source_png,
        "compressed": _compress_zlib(raw, strategy["level"], strategy["strategy"]),
        "description": description,
    }


def _full_canvas_apng_source(
    width: int,
    height: int,
    source_pixels: list[tuple[int, int, int, int]],
) -> bytes:
    frames = [
        _frame(
            "base",
            width,
            height,
            0,
            0,
            source_pixels,
            [0, 1, 2, 3, 4],
            1,
            5,
            0,
            0,
            0,
        ),
        _frame(
            "zlib_matrix",
            width,
            height,
            0,
            0,
            source_pixels,
            [0, 1, 2, 3, 4],
            1,
            10,
            0,
            0,
            2,
        ),
    ]
    return _encode_apng(width, height, frames)


def _compress_zlib(raw: bytes, level: int, strategy: int) -> bytes:
    compressor = zlib.compressobj(
        level=level,
        method=zlib.DEFLATED,
        wbits=15,
        memLevel=8,
        strategy=strategy,
    )
    return compressor.compress(raw) + compressor.flush()


def _split_payload(payload: bytes, count: int) -> list[bytes]:
    if count <= 1:
        return [payload]
    if len(payload) < count:
        raise PNGAPNGZlibCompressionError(
            "zlib_stream_too_short",
            "compressed stream is too short for requested split",
        )
    parts = []
    start = 0
    for index in range(count - 1):
        remaining = len(payload) - start
        size = max(1, remaining // (count - index))
        parts.append(payload[start : start + size])
        start += size
    parts.append(payload[start:])
    return parts


def _safe_read_chunks(png_bytes: bytes) -> list[dict]:
    try:
        return _read_chunks(png_bytes)
    except Exception as exc:
        family = getattr(exc, "family", "png_chunk_parse_failed")
        message = getattr(exc, "message", str(exc))
        raise PNGAPNGZlibCompressionError(family, message) from exc


def _ihdr_summary(chunks: list[dict]) -> dict:
    ihdr_chunks = [chunk for chunk in chunks if chunk["type"] == "IHDR"]
    if len(ihdr_chunks) != 1:
        raise PNGAPNGZlibCompressionError("png_ihdr_missing", "PNG IHDR chunk must be present exactly once")
    payload = ihdr_chunks[0]["payload"]
    if len(payload) != 13:
        raise PNGAPNGZlibCompressionError("png_ihdr_invalid", "PNG IHDR chunk length must be 13")
    width, height, bit_depth, color_type, compression_method, filter_method, interlace_method = struct.unpack(
        ">IIBBBBB",
        payload,
    )
    return {
        "width": width,
        "height": height,
        "bit_depth": bit_depth,
        "color_type": color_type,
        "compression_method": compression_method,
        "filter_method": filter_method,
        "interlace_method": interlace_method,
    }


def _zlib_header_summary(payload: bytes) -> dict:
    if len(payload) < 2:
        raise PNGAPNGZlibCompressionError(
            "zlib_header_truncated",
            "zlib stream must contain CMF and FLG bytes",
        )
    cmf = payload[0]
    flg = payload[1]
    return {
        "cmf": cmf,
        "flg": flg,
        "compression_method": cmf & 0x0F,
        "compression_info": cmf >> 4,
        "fdict": bool(flg & 0x20),
        "flevel": flg >> 6,
        "cmf_flg_check_passed": ((cmf * 256 + flg) % 31) == 0,
    }


def _decompress_stream(payload: bytes, family: str) -> bytes:
    try:
        return zlib.decompress(payload)
    except zlib.error as exc:
        raise PNGAPNGZlibCompressionError(family, str(exc)) from exc


def _mutate_data_chunk_byte(
    png_bytes: bytes,
    chunk_type: str,
    *,
    payload_offset: int,
    from_end: bool,
) -> bytes:
    chunks = _safe_read_chunks(png_bytes)
    rewritten = [PNG_SIGNATURE]
    candidates = [
        index
        for index, chunk in enumerate(chunks)
        if chunk["type"] == chunk_type and len(chunk["payload"]) > payload_offset
    ]
    if not candidates:
        raise PNGAPNGZlibCompressionError(
            f"{chunk_type.lower()}_missing",
            f"expected {chunk_type} chunk with enough data",
        )
    target = candidates[-1] if from_end else candidates[0]
    for index, chunk in enumerate(chunks):
        payload = chunk["payload"]
        if index == target:
            mutable = bytearray(payload)
            target_offset = len(mutable) - 1 - payload_offset if from_end else payload_offset
            mutable[target_offset] ^= 0xFF
            payload = bytes(mutable)
        rewritten.append(_png_chunk(chunk["type"].encode("ascii"), payload))
    return b"".join(rewritten)


def _truncate_data_chunk(png_bytes: bytes, chunk_type: str, *, data_offset: int) -> bytes:
    chunks = _safe_read_chunks(png_bytes)
    rewritten = [PNG_SIGNATURE]
    candidates = [
        index
        for index, chunk in enumerate(chunks)
        if chunk["type"] == chunk_type and len(chunk["payload"]) > data_offset
    ]
    if not candidates:
        raise PNGAPNGZlibCompressionError(
            f"{chunk_type.lower()}_missing",
            f"expected {chunk_type} chunk with enough data",
        )
    target = candidates[-1]
    for index, chunk in enumerate(chunks):
        payload = chunk["payload"]
        if index == target:
            payload = payload[:-1]
        rewritten.append(_png_chunk(chunk["type"].encode("ascii"), payload))
    return b"".join(rewritten)


def _invalid_probe_results(cases: list[dict]) -> list[dict]:
    by_case = {case["case_id"]: case["png_bytes"] for case in cases}
    probes = [
        (
            "invalid_compression_method",
            make_invalid_compression_method_probe(by_case["png_zlib_stored_blocks"]),
            "png_method_unsupported",
        ),
        (
            "corrupt_idat_zlib_header",
            make_corrupt_idat_zlib_header_probe(by_case["png_zlib_fixed_huffman"]),
            "png_image_data_decompression_failed",
        ),
        (
            "truncated_idat",
            make_truncated_idat_probe(by_case["png_zlib_filtered_strategy"]),
            "png_image_data_decompression_failed",
        ),
        (
            "truncated_fdat",
            make_truncated_fdat_probe(by_case["apng_fdat_zlib_stored_blocks"]),
            "apng_frame_decompression_failed",
        ),
        (
            "corrupt_fdat_adler",
            make_corrupt_fdat_adler_probe(by_case["apng_fdat_zlib_fixed_huffman"]),
            "apng_frame_decompression_failed",
        ),
        (
            "sequence_gap",
            make_sequence_gap_probe(by_case["apng_fdat_zlib_rle_strategy"]),
            "apng_sequence_number_invalid",
        ),
    ]
    results = []
    for probe_id, png_bytes, expected_family in probes:
        decoded = decode_png_apng_zlib_compression(png_bytes)
        results.append(
            {
                "probe_id": probe_id,
                "expected_family": expected_family,
                "ok": decoded["ok"],
                "error_families": decoded.get("error_families", []),
                "error_family": decoded.get("error_family"),
                "rejected": not decoded["ok"] and decoded.get("error_family") == expected_family,
            }
        )
    return results


def _compact_decoded(decoded: dict) -> dict:
    if not decoded.get("ok"):
        return {
            "ok": False,
            "errors": decoded.get("errors", []),
            "error_families": decoded.get("error_families", []),
        }
    keys = [
        "ok",
        "carrier_family",
        "ihdr_compression_method",
        "pixel_hash",
        "raw_image_data_hash",
        "raw_image_data_length",
        "compressed_data_hash",
        "compressed_data_length",
        "zlib_header",
        "idat_data_lengths",
        "fdat_frame_data_lengths",
        "idat_chunk_count",
        "fdat_chunk_count",
        "data_chunk_count",
        "chunks",
    ]
    if decoded["carrier_family"] == "apng":
        keys.extend(["frame_count", "display_hashes", "final_output_hash", "animation_chunk_order"])
    else:
        keys.extend(["width", "height", "filter_types_seen"])
    return {key: decoded[key] for key in keys}


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
                "date",
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
                "carrier_family": result["carrier_family"],
                "compression_strategy_id": result["compression_strategy_id"],
                "zlib_strategy_name": result["zlib_strategy_name"],
                "deflate_block_family": result["deflate_block_family"],
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
        "# PNG/APNG Zlib Compression Stage 0\n\n"
        "Bounded PNG IDAT and APNG fdAT zlib/DEFLATE compression matrix for "
        "Mechagotchi workshop carriers.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Case successes: {report['case_success_count']}/{report['case_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- PNG cases: {metrics['png_case_count']}\n"
        f"- APNG cases: {metrics['apng_case_count']}\n"
        f"- Zlib CM=8 cases: {metrics['zlib_cm8_case_count']}\n\n"
        "This is a deterministic zlib compression-method-0 subset. It does "
        "not prove full APNG/PNG conformance, live editor rewrite preservation, "
        "or final production carrier selection.\n"
    )


def _map_png_error_family(family: str) -> str:
    if family == "png_idat_decompression_failed":
        return "png_image_data_decompression_failed"
    return family


def _error(path: str, family: str, message: str | None = None) -> dict:
    return {
        "path": path,
        "family": family,
        "message": message or family.replace("_", " "),
    }


def _hash_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _first_grid_path(profile: dict, generated_root: Path) -> Path:
    grid_paths = sorted((generated_root / profile["profile_id"]).glob("*.json"))
    if not grid_paths:
        raise ValueError(f"no generated grids found for profile: {profile['profile_id']}")
    return grid_paths[0]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate PNG/APNG zlib compression Stage 0 research artifacts."
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ROOT / "data/workshop_editor",
    )
    args = parser.parse_args()
    report = run_png_apng_zlib_compression_lab()
    write_png_apng_zlib_compression_artifacts(args.output_root, report)


if __name__ == "__main__":
    main()
