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

from png_apng_filtered_frame_data import decode_apng_filtered_frame_data
from png_apng_image_data_chunking import (
    _combined_fdat_frame_data,
    _combined_idat_data,
    _read_chunks,
    _replace_fdat_chunks,
    _replace_idat_chunks,
)
from png_apng_zlib_compression_matrix import (
    _full_canvas_apng_source,
    _map_png_error_family,
    _split_payload,
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


REPORT_PATH = Path("data/workshop_editor/png_apng_zlib_header_policy_stage0.json")
DATA_PATH = Path("data/workshop_editor/png_apng_zlib_header_policy.js")
ARTIFACT_DIR = Path("data/workshop_editor/png_apng_zlib_header_policy_stage0")
PNG_SOURCE_URL = "https://www.w3.org/TR/png-3/"
ZLIB_SOURCE_URL = "https://www.rfc-editor.org/rfc/rfc1950"
DEFLATE_SOURCE_URL = "https://www.rfc-editor.org/rfc/rfc1951"

PNG_APNG_ZLIB_HEADER_POLICY_CASE_IDS = [
    "png_zlib_window_512",
    "png_zlib_window_4096",
    "png_zlib_window_32768",
    "apng_fdat_zlib_window_512",
    "apng_fdat_zlib_window_4096",
    "apng_fdat_zlib_window_32768",
]

WINDOW_SPECS = {
    "window_512": {
        "wbits": 9,
        "expected_cinfo": 1,
        "window_size_bytes": 512,
        "description": "zlib CMF CINFO=1, indicating a 512-byte LZ77 window.",
    },
    "window_4096": {
        "wbits": 12,
        "expected_cinfo": 4,
        "window_size_bytes": 4096,
        "description": "zlib CMF CINFO=4, indicating a 4096-byte LZ77 window.",
    },
    "window_32768": {
        "wbits": 15,
        "expected_cinfo": 7,
        "window_size_bytes": 32768,
        "description": "zlib CMF CINFO=7, indicating the maximum 32768-byte LZ77 window.",
    },
}


class PNGAPNGZlibHeaderPolicyError(ValueError):
    def __init__(self, family: str, message: str):
        super().__init__(message)
        self.family = family
        self.message = message


def export_png_apng_zlib_header_policy_cases(grid: dict, slip_profile: dict) -> list[dict]:
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
            "png_zlib_window_512",
            "png",
            "window_512",
            static_png,
            static_raw,
            "Static PNG IDAT encoded with a valid 512-byte zlib window header.",
        ),
        _case_spec(
            "png_zlib_window_4096",
            "png",
            "window_4096",
            static_png,
            static_raw,
            "Static PNG IDAT encoded with a valid 4096-byte zlib window header.",
        ),
        _case_spec(
            "png_zlib_window_32768",
            "png",
            "window_32768",
            static_png,
            static_raw,
            "Static PNG IDAT encoded with a valid 32768-byte zlib window header.",
        ),
        _case_spec(
            "apng_fdat_zlib_window_512",
            "apng",
            "window_512",
            apng_source,
            apng_raw,
            "APNG second-frame fdAT encoded with a valid 512-byte zlib window header.",
        ),
        _case_spec(
            "apng_fdat_zlib_window_4096",
            "apng",
            "window_4096",
            apng_source,
            apng_raw,
            "APNG second-frame fdAT encoded with a valid 4096-byte zlib window header.",
        ),
        _case_spec(
            "apng_fdat_zlib_window_32768",
            "apng",
            "window_32768",
            apng_source,
            apng_raw,
            "APNG second-frame fdAT encoded with a valid 32768-byte zlib window header.",
        ),
    ]

    cases = []
    for spec in case_specs:
        if spec["carrier_family"] == "png":
            png_bytes = _replace_idat_chunks(spec["source_png"], [spec["compressed"]])
        else:
            png_bytes = _replace_fdat_chunks(spec["source_png"], _split_payload(spec["compressed"], 2))
        decoded = decode_png_apng_zlib_header_policy(png_bytes)
        if not decoded["ok"]:
            raise PNGAPNGZlibHeaderPolicyError(
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
                "window_policy_id": spec["window_policy_id"],
                "zlib_wbits": spec["zlib_wbits"],
                "window_size_bytes": spec["window_size_bytes"],
                "png_file_name": f"{slip_profile['profile_id']}_{spec['case_id']}.png",
                "png_bytes": png_bytes,
                "png_hash": _hash_bytes(png_bytes),
                "expected_pixel_hash": decoded["pixel_hash"],
                "expected_raw_image_data_hash": decoded["raw_image_data_hash"],
                "expected_compressed_data_hash": decoded["compressed_data_hash"],
                "expected_zlib_header": decoded["zlib_header"],
                "expected_data_chunk_count": decoded["data_chunk_count"],
                "expected_idat_chunk_count": decoded["idat_chunk_count"],
                "expected_fdat_chunk_count": decoded["fdat_chunk_count"],
                "decoded": decoded,
            }
        )
    return cases


def decode_png_apng_zlib_header_policy(png_bytes: bytes) -> dict:
    try:
        decoded = _decode_png_apng_zlib_header_policy(png_bytes)
        decoded["ok"] = True
        decoded["errors"] = []
        decoded["error_families"] = []
        return decoded
    except PNGAPNGZlibHeaderPolicyError as exc:
        return {
            "ok": False,
            "errors": [_error("png_apng.zlib_header_policy", exc.family, exc.message)],
            "error_families": [exc.family],
            "error_family": exc.family,
        }


def make_png_fdict_probe(png_bytes: bytes) -> bytes:
    raw = _decompress_stream(_combined_idat_data(png_bytes), "png_image_data_decompression_failed")
    payload = _compress_zlib(raw, wbits=15, zdict=_dictionary_seed())
    return _replace_idat_chunks(png_bytes, [payload])


def make_png_cmf_flg_check_probe(png_bytes: bytes) -> bytes:
    return _replace_png_compressed_stream(
        png_bytes,
        _mutate_cmf_flg_check(_combined_idat_data(png_bytes)),
    )


def make_png_reserved_cm_probe(png_bytes: bytes) -> bytes:
    payload = _combined_idat_data(png_bytes)
    return _replace_png_compressed_stream(
        png_bytes,
        _replace_zlib_header(payload, cmf=0x7F, fdict=False, flevel=2),
    )


def make_apng_fdict_probe(png_bytes: bytes) -> bytes:
    raw = _decompress_stream(_combined_fdat_frame_data(png_bytes), "apng_frame_decompression_failed")
    payload = _compress_zlib(raw, wbits=15, zdict=_dictionary_seed())
    return _replace_apng_compressed_stream(png_bytes, payload)


def make_apng_cmf_flg_check_probe(png_bytes: bytes) -> bytes:
    return _replace_apng_compressed_stream(
        png_bytes,
        _mutate_cmf_flg_check(_combined_fdat_frame_data(png_bytes)),
    )


def make_apng_cinfo_too_large_probe(png_bytes: bytes) -> bytes:
    payload = _combined_fdat_frame_data(png_bytes)
    return _replace_apng_compressed_stream(
        png_bytes,
        _replace_zlib_header(payload, cmf=0x88, fdict=False, flevel=2),
    )


def run_png_apng_zlib_header_policy_lab(
    profile_paths: list[Path] | None = None,
    generated_root: Path | None = None,
) -> dict:
    profile_paths = profile_paths or [
        Path("data/slips/valid/slip_lcd_seed.json"),
        Path("data/slips/valid/slip_gray_stable.json"),
        Path("data/slips/valid/slip_amber_social.json"),
    ]
    generated_root = generated_root or Path("data/slips/multi_profile_generation_stage0")

    case_results = []
    first_profile_cases = None
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid = _read_json(_first_grid_path(profile, generated_root))
        cases = export_png_apng_zlib_header_policy_cases(grid, profile)
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
                and not decoded["zlib_header"]["fdict"]
                and decoded["zlib_header"]["cmf_flg_check_passed"]
                and decoded["zlib_header"]["compression_info"]
                == case["expected_zlib_header"]["compression_info"]
            )
            case_results.append(
                {
                    "profile_id": profile["profile_id"],
                    "grid_id": grid["grid_id"],
                    "case_id": case["case_id"],
                    "description": case["description"],
                    "carrier_family": case["carrier_family"],
                    "window_policy_id": case["window_policy_id"],
                    "zlib_wbits": case["zlib_wbits"],
                    "window_size_bytes": case["window_size_bytes"],
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
    cinfo_values = sorted({result["decoded"]["zlib_header"]["compression_info"] for result in case_results})
    return {
        "artifact_id": "png_apng_zlib_header_policy_stage0",
        "status": "research_png_apng_zlib_header_policy_no_package_code",
        "date": "2026-05-14",
        "purpose": (
            "Close a bounded PNG/APNG image-data gap by proving selected valid "
            "zlib CMF/FLG header window values for static PNG IDAT and APNG "
            "fdAT streams, while rejecting preset-dictionary and malformed "
            "zlib header streams before semantic restore."
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
            "labs/workshop_editor/png_apng_zlib_header_policy.py",
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
                    "zlib CMF/FLG header structure, CM=8 deflate method, "
                    "CINFO window-size field, FCHECK divisibility, FDICT "
                    "preset-dictionary flag, and Adler-32 validation."
                ),
            },
            {
                "source": "RFC 1951 DEFLATE compressed data format",
                "url": DEFLATE_SOURCE_URL,
                "used_for": (
                    "Deflate payload interpretation under valid zlib method-8 "
                    "headers and rejection context for malformed zlib wrappers."
                ),
            },
        ],
        "profile_count": len(profile_paths),
        "case_ids": list(PNG_APNG_ZLIB_HEADER_POLICY_CASE_IDS),
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
            "case_family_count": len(PNG_APNG_ZLIB_HEADER_POLICY_CASE_IDS),
            "png_case_count": sum(1 for result in case_results if result["carrier_family"] == "png"),
            "apng_case_count": sum(1 for result in case_results if result["carrier_family"] == "apng"),
            "zlib_cinfo_values_covered": cinfo_values,
            "zlib_window_sizes_covered": sorted({result["window_size_bytes"] for result in case_results}),
            "ihdr_compression_method_0_count": sum(
                1 for result in case_results if result["decoded"]["ihdr_compression_method"] == 0
            ),
            "zlib_cm8_case_count": sum(
                1
                for result in case_results
                if result["decoded"]["zlib_header"]["compression_method"] == 8
            ),
            "fdict_false_case_count": sum(
                1 for result in case_results if not result["decoded"]["zlib_header"]["fdict"]
            ),
            "cmf_flg_check_passed_case_count": sum(
                1
                for result in case_results
                if result["decoded"]["zlib_header"]["cmf_flg_check_passed"]
            ),
            "split_fdat_case_count": sum(
                1
                for result in case_results
                if result["carrier_family"] == "apng" and result["decoded"]["fdat_chunk_count"] == 2
            ),
            "live_external_editor_verified": False,
        },
        "closed_states": [
            "png_zlib_window_header_reconstruction",
            "apng_fdat_zlib_window_header_reconstruction",
            "png_apng_fdict_rejection",
            "png_apng_zlib_cmf_flg_error_rejection",
            "png_apng_zlib_header_policy_invalid_probe_rejection",
        ],
        "blocked_states": [
            "full_apng_png_conformance",
            "live_external_editor_rewrite_validation",
            "production_import_export_carrier_selection_final_decision",
            "manual_readability_calibration",
            "package_runtime_lifecycle_integration",
        ],
        "decision": "prototype_png_apng_zlib_header_policy_subset",
        "notes": [
            "This lab validates selected zlib header-window values only; it does not enumerate every possible CINFO/FLEVEL combination.",
            "The FDICT probes use real zlib preset-dictionary streams and prove they are rejected by the current decoder path before semantic restore.",
            "The malformed CMF/FLG probes prove decompressor rejection for invalid header checksum, reserved compression method, and too-large CINFO.",
        ],
        "next_research_step": (
            "Continue remaining APNG/PNG coverage through additional explicit "
            "image-data conformance fixtures such as CRC/error taxonomy, "
            "larger color/interlace/header cross-products, live external "
            "editor preservation, or final carrier selection evidence before "
            "claiming full conformance."
        ),
    }


def write_png_apng_zlib_header_policy_artifacts(
    output_root: Path = Path("data/workshop_editor"),
    report: dict | None = None,
) -> dict:
    report = report or run_png_apng_zlib_header_policy_lab()
    output_root.mkdir(parents=True, exist_ok=True)
    artifact_dir = output_root / "png_apng_zlib_header_policy_stage0"
    cases_dir = artifact_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)

    summary_json = output_root / "png_apng_zlib_header_policy_stage0.json"
    app_js = output_root / "png_apng_zlib_header_policy.js"
    artifact_summary_json = artifact_dir / "png_apng_zlib_header_policy_stage0.json"
    artifact_app_js = artifact_dir / "png_apng_zlib_header_policy.js"
    readme = artifact_dir / "README.md"

    _write_json(summary_json, _json_report(report))
    _write_json(artifact_summary_json, _json_report(report))
    for result in report["case_results"]:
        (cases_dir / result["png_file_name"]).write_bytes(
            bytes.fromhex(result["png_bytes_hex"])
        )
    payload = (
        "window.MECHAGOTCHI_PNG_APNG_ZLIB_HEADER_POLICY = "
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


def _decode_png_apng_zlib_header_policy(png_bytes: bytes) -> dict:
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
            raise PNGAPNGZlibHeaderPolicyError(family, family.replace("_", " "))
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
        raise PNGAPNGZlibHeaderPolicyError(_map_png_error_family(exc.family), exc.message) from exc
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
    window_policy_id: str,
    source_png: bytes,
    raw: bytes,
    description: str,
) -> dict:
    window = WINDOW_SPECS[window_policy_id]
    return {
        "case_id": case_id,
        "carrier_family": carrier_family,
        "window_policy_id": window_policy_id,
        "zlib_wbits": window["wbits"],
        "window_size_bytes": window["window_size_bytes"],
        "source_png": source_png,
        "compressed": _compress_zlib(raw, wbits=window["wbits"]),
        "description": description,
    }


def _compress_zlib(raw: bytes, *, wbits: int, zdict: bytes | None = None) -> bytes:
    kwargs = {
        "level": 6,
        "method": zlib.DEFLATED,
        "wbits": wbits,
        "memLevel": 8,
        "strategy": zlib.Z_DEFAULT_STRATEGY,
    }
    if zdict is not None:
        kwargs["zdict"] = zdict
    compressor = zlib.compressobj(**kwargs)
    return compressor.compress(raw) + compressor.flush()


def _safe_read_chunks(png_bytes: bytes) -> list[dict]:
    try:
        return _read_chunks(png_bytes)
    except Exception as exc:
        family = getattr(exc, "family", "png_chunk_parse_failed")
        message = getattr(exc, "message", str(exc))
        raise PNGAPNGZlibHeaderPolicyError(family, message) from exc


def _ihdr_summary(chunks: list[dict]) -> dict:
    ihdr_chunks = [chunk for chunk in chunks if chunk["type"] == "IHDR"]
    if len(ihdr_chunks) != 1:
        raise PNGAPNGZlibHeaderPolicyError("png_ihdr_missing", "PNG IHDR chunk must be present exactly once")
    payload = ihdr_chunks[0]["payload"]
    if len(payload) != 13:
        raise PNGAPNGZlibHeaderPolicyError("png_ihdr_invalid", "PNG IHDR chunk length must be 13")
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
        raise PNGAPNGZlibHeaderPolicyError(
            "zlib_header_truncated",
            "zlib stream must contain CMF and FLG bytes",
        )
    cmf = payload[0]
    flg = payload[1]
    compression_info = cmf >> 4
    return {
        "cmf": cmf,
        "flg": flg,
        "compression_method": cmf & 0x0F,
        "compression_info": compression_info,
        "window_size_bytes": 1 << (compression_info + 8),
        "fdict": bool(flg & 0x20),
        "flevel": flg >> 6,
        "cmf_flg_check_passed": ((cmf * 256 + flg) % 31) == 0,
    }


def _decompress_stream(payload: bytes, family: str) -> bytes:
    try:
        return zlib.decompress(payload)
    except zlib.error as exc:
        raise PNGAPNGZlibHeaderPolicyError(family, str(exc)) from exc


def _replace_png_compressed_stream(png_bytes: bytes, payload: bytes) -> bytes:
    return _replace_idat_chunks(png_bytes, [payload])


def _replace_apng_compressed_stream(png_bytes: bytes, payload: bytes) -> bytes:
    return _replace_fdat_chunks(png_bytes, _split_payload(payload, 2))


def _mutate_cmf_flg_check(payload: bytes) -> bytes:
    if len(payload) < 2:
        raise PNGAPNGZlibHeaderPolicyError("zlib_header_truncated", "zlib stream header is truncated")
    mutable = bytearray(payload)
    mutable[1] ^= 0x01
    return bytes(mutable)


def _replace_zlib_header(payload: bytes, *, cmf: int, fdict: bool, flevel: int) -> bytes:
    if len(payload) < 2:
        raise PNGAPNGZlibHeaderPolicyError("zlib_header_truncated", "zlib stream header is truncated")
    flg = _valid_flg_for(cmf, fdict=fdict, flevel=flevel)
    return bytes([cmf, flg]) + payload[2:]


def _valid_flg_for(cmf: int, *, fdict: bool, flevel: int) -> int:
    base = ((flevel & 0x03) << 6) | (0x20 if fdict else 0)
    for fcheck in range(32):
        flg = base | fcheck
        if (cmf * 256 + flg) % 31 == 0:
            return flg
    raise PNGAPNGZlibHeaderPolicyError("zlib_header_invalid", "could not construct a valid FLG byte")


def _dictionary_seed() -> bytes:
    return b"mechagotchi-stage0-zlib-dictionary"


def _invalid_probe_results(cases: list[dict]) -> list[dict]:
    by_case = {case["case_id"]: case["png_bytes"] for case in cases}
    probes = [
        (
            "png_fdict",
            make_png_fdict_probe(by_case["png_zlib_window_512"]),
            "png_image_data_decompression_failed",
        ),
        (
            "png_cmf_flg_check",
            make_png_cmf_flg_check_probe(by_case["png_zlib_window_4096"]),
            "png_image_data_decompression_failed",
        ),
        (
            "png_reserved_cm",
            make_png_reserved_cm_probe(by_case["png_zlib_window_32768"]),
            "png_image_data_decompression_failed",
        ),
        (
            "apng_fdict",
            make_apng_fdict_probe(by_case["apng_fdat_zlib_window_512"]),
            "apng_frame_decompression_failed",
        ),
        (
            "apng_cmf_flg_check",
            make_apng_cmf_flg_check_probe(by_case["apng_fdat_zlib_window_4096"]),
            "apng_frame_decompression_failed",
        ),
        (
            "apng_cinfo_too_large",
            make_apng_cinfo_too_large_probe(by_case["apng_fdat_zlib_window_32768"]),
            "apng_frame_decompression_failed",
        ),
    ]
    results = []
    for probe_id, png_bytes, expected_family in probes:
        decoded = decode_png_apng_zlib_header_policy(png_bytes)
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
                "window_policy_id": result["window_policy_id"],
                "window_size_bytes": result["window_size_bytes"],
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
        "# PNG/APNG Zlib Header Policy Stage 0\n\n"
        "Bounded PNG IDAT and APNG fdAT zlib header policy matrix for "
        "Mechagotchi workshop carriers.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Case successes: {report['case_success_count']}/{report['case_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- PNG cases: {metrics['png_case_count']}\n"
        f"- APNG cases: {metrics['apng_case_count']}\n"
        f"- Zlib CINFO values covered: {metrics['zlib_cinfo_values_covered']}\n"
        f"- FDICT=false valid cases: {metrics['fdict_false_case_count']}\n\n"
        "This is a deterministic zlib header-policy subset. It does not prove "
        "full APNG/PNG conformance, live editor rewrite preservation, or final "
        "production carrier selection.\n"
    )


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
        description="Generate PNG/APNG zlib header policy Stage 0 research artifacts."
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("data/workshop_editor"),
    )
    args = parser.parse_args()
    report = run_png_apng_zlib_header_policy_lab()
    write_png_apng_zlib_header_policy_artifacts(args.output_root, report)


if __name__ == "__main__":
    main()
