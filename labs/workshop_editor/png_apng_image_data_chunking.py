import argparse
import hashlib
import json
import struct
import sys
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME_DIR = ROOT / "labs" / "grid_genome"
if str(GRID_GENOME_DIR) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME_DIR))

from png_apng_filtered_frame_data import (
    decode_apng_filtered_frame_data,
    export_apng_filtered_frame_data_cases,
)
from png_deep_color_sidecar_decoder import (
    PNGDeepColorDecodeError,
    _encode_png_deep_color,
    _hash_pixels,
    _png_chunk,
    _read_json,
    _read_png_chunks,
    _ratio,
    _write_json,
    decode_png_deep_color,
)
from standard_image_sidecar_decoder import PNG_SIGNATURE, render_grid_rgba_pixels


REPORT_PATH = Path("data/workshop_editor/png_apng_image_data_chunking_stage0.json")
DATA_PATH = Path("data/workshop_editor/png_apng_image_data_chunking.js")
ARTIFACT_DIR = Path("data/workshop_editor/png_apng_image_data_chunking_stage0")
PNG_SOURCE_URL = "https://www.w3.org/TR/png-3/"
PNG_APNG_IMAGE_DATA_CHUNKING_CASE_IDS = [
    "png_idat_leading_empty_chunk",
    "png_idat_zlib_header_split",
    "png_idat_adler32_split",
    "apng_fdat_leading_empty_frame_data",
    "apng_fdat_zlib_header_split",
    "apng_fdat_adler32_split",
]


class PNGAPNGImageDataChunkingError(ValueError):
    def __init__(self, family: str, message: str):
        super().__init__(message)
        self.family = family
        self.message = message


def export_png_apng_image_data_chunking_cases(grid: dict, slip_profile: dict) -> list[dict]:
    width, height = grid["grid_size"]
    source_pixels = render_grid_rgba_pixels(grid)
    png_spec = {"color_type": 6, "bit_depth": 8, "filter_types": [0, 1, 2, 3, 4]}
    static_png = _encode_png_deep_color(width, height, source_pixels, png_spec)
    apng_source_cases = {
        case["case_id"]: case
        for case in export_apng_filtered_frame_data_cases(grid, slip_profile)
    }

    case_specs = [
        {
            "case_id": "png_idat_leading_empty_chunk",
            "carrier_family": "png",
            "split_target": "leading_empty",
            "source_png": static_png,
            "segments": _split_image_datastream(_combined_idat_data(static_png), "leading_empty"),
            "description": "Static PNG with an empty IDAT data field before the compressed image datastream.",
        },
        {
            "case_id": "png_idat_zlib_header_split",
            "carrier_family": "png",
            "split_target": "zlib_header",
            "source_png": static_png,
            "segments": _split_image_datastream(_combined_idat_data(static_png), "zlib_header"),
            "description": "Static PNG with the zlib header split across IDAT chunk boundaries.",
        },
        {
            "case_id": "png_idat_adler32_split",
            "carrier_family": "png",
            "split_target": "adler32",
            "source_png": static_png,
            "segments": _split_image_datastream(_combined_idat_data(static_png), "adler32"),
            "description": "Static PNG with the compressed stream and Adler-32 trailer split across five IDAT chunks.",
        },
        {
            "case_id": "apng_fdat_leading_empty_frame_data",
            "carrier_family": "apng",
            "split_target": "leading_empty",
            "source_png": apng_source_cases["filter_none_split_fdat"]["png_bytes"],
            "segments": _split_image_datastream(
                _combined_fdat_frame_data(apng_source_cases["filter_none_split_fdat"]["png_bytes"]),
                "leading_empty",
            ),
            "description": "APNG with an empty fdAT frame_data field before the compressed frame datastream.",
        },
        {
            "case_id": "apng_fdat_zlib_header_split",
            "carrier_family": "apng",
            "split_target": "zlib_header",
            "source_png": apng_source_cases["filter_sub_split_fdat"]["png_bytes"],
            "segments": _split_image_datastream(
                _combined_fdat_frame_data(apng_source_cases["filter_sub_split_fdat"]["png_bytes"]),
                "zlib_header",
            ),
            "description": "APNG with the zlib header split across fdAT frame_data chunk boundaries.",
        },
        {
            "case_id": "apng_fdat_adler32_split",
            "carrier_family": "apng",
            "split_target": "adler32",
            "source_png": apng_source_cases["filter_paeth_split_fdat"]["png_bytes"],
            "segments": _split_image_datastream(
                _combined_fdat_frame_data(apng_source_cases["filter_paeth_split_fdat"]["png_bytes"]),
                "adler32",
            ),
            "description": "APNG with the compressed frame stream and Adler-32 trailer split across five fdAT chunks.",
        },
    ]

    cases = []
    for spec in case_specs:
        if spec["carrier_family"] == "png":
            png_bytes = _replace_idat_chunks(spec["source_png"], spec["segments"])
        else:
            png_bytes = _replace_fdat_chunks(spec["source_png"], spec["segments"])
        decoded = decode_png_apng_image_data_chunking(png_bytes)
        if not decoded["ok"]:
            raise PNGAPNGImageDataChunkingError(
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
                "split_target": spec["split_target"],
                "png_file_name": f"{slip_profile['profile_id']}_{spec['case_id']}.png",
                "png_bytes": png_bytes,
                "png_hash": _hash_bytes(png_bytes),
                "expected_pixel_hash": decoded["pixel_hash"],
                "expected_idat_data_lengths": decoded["idat_data_lengths"],
                "expected_fdat_frame_data_lengths": decoded["fdat_frame_data_lengths"],
                "expected_data_chunk_count": decoded["data_chunk_count"],
                "decoded": decoded,
            }
        )
    return cases


def decode_png_apng_image_data_chunking(png_bytes: bytes) -> dict:
    try:
        decoded = _decode_png_apng_image_data_chunking(png_bytes)
        decoded["ok"] = True
        decoded["errors"] = []
        decoded["error_families"] = []
        return decoded
    except PNGAPNGImageDataChunkingError as exc:
        return {
            "ok": False,
            "errors": [_error("png_apng.image_data_chunking", exc.family, exc.message)],
            "error_families": [exc.family],
            "error_family": exc.family,
        }


def make_idat_nonconsecutive_probe(png_bytes: bytes) -> bytes:
    chunks = _read_chunks(png_bytes)
    rewritten = [PNG_SIGNATURE]
    inserted = False
    for chunk in chunks:
        rewritten.append(_png_chunk(chunk["type"].encode("ascii"), chunk["payload"]))
        if chunk["type"] == "IDAT" and not inserted:
            rewritten.append(_png_chunk(b"tEXt", b"mechagotchi\x00nonconsecutive-idat"))
            inserted = True
    if not inserted:
        raise PNGAPNGImageDataChunkingError("png_idat_missing", "expected IDAT chunk")
    return b"".join(rewritten)


def make_corrupt_idat_probe(png_bytes: bytes) -> bytes:
    return _mutate_first_data_chunk_byte(png_bytes, "IDAT", data_offset=0)


def make_missing_idat_probe(png_bytes: bytes) -> bytes:
    return _remove_chunks(png_bytes, {"IDAT"})


def make_missing_fdat_probe(png_bytes: bytes) -> bytes:
    return _remove_chunks(png_bytes, {"fdAT"})


def make_sequence_gap_probe(png_bytes: bytes) -> bytes:
    chunks = _read_chunks(png_bytes)
    rewritten = [PNG_SIGNATURE]
    mutated = False
    for chunk in chunks:
        payload = chunk["payload"]
        if chunk["type"] == "fdAT" and not mutated:
            if len(payload) < 4:
                raise PNGAPNGImageDataChunkingError("apng_fdat_invalid", "fdAT chunk is too short")
            sequence_number = struct.unpack(">I", payload[:4])[0] + 1
            payload = struct.pack(">I", sequence_number) + payload[4:]
            mutated = True
        rewritten.append(_png_chunk(chunk["type"].encode("ascii"), payload))
    if not mutated:
        raise PNGAPNGImageDataChunkingError("apng_fdat_missing", "expected fdAT chunk")
    return b"".join(rewritten)


def make_corrupt_fdat_probe(png_bytes: bytes) -> bytes:
    return _mutate_first_data_chunk_byte(png_bytes, "fdAT", data_offset=4)


def run_png_apng_image_data_chunking_lab(
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
        cases = export_png_apng_image_data_chunking_cases(grid, profile)
        if first_profile_cases is None:
            first_profile_cases = cases
        for case in cases:
            decoded = case["decoded"]
            success = (
                decoded["ok"]
                and decoded["pixel_hash"] == case["expected_pixel_hash"]
                and decoded["idat_data_lengths"] == case["expected_idat_data_lengths"]
                and decoded["fdat_frame_data_lengths"] == case["expected_fdat_frame_data_lengths"]
                and decoded["data_chunk_count"] == case["expected_data_chunk_count"]
            )
            case_results.append(
                {
                    "profile_id": profile["profile_id"],
                    "grid_id": grid["grid_id"],
                    "case_id": case["case_id"],
                    "description": case["description"],
                    "carrier_family": case["carrier_family"],
                    "split_target": case["split_target"],
                    "png_file_name": case["png_file_name"],
                    "png_hash": case["png_hash"],
                    "png_bytes_hex": case["png_bytes"].hex(),
                    "expected_pixel_hash": case["expected_pixel_hash"],
                    "expected_idat_data_lengths": case["expected_idat_data_lengths"],
                    "expected_fdat_frame_data_lengths": case["expected_fdat_frame_data_lengths"],
                    "decoded": _compact_decoded(decoded),
                    "success": success,
                }
            )

    invalid_results = _invalid_probe_results(first_profile_cases or [])
    success_count = sum(1 for result in case_results if result["success"])
    invalid_rejected_count = sum(1 for result in invalid_results if result["rejected"])
    return {
        "artifact_id": "png_apng_image_data_chunking_stage0",
        "status": "research_png_apng_image_data_chunking_no_package_code",
        "date": "2026-05-14",
        "purpose": (
            "Close a bounded PNG/APNG image-data gap by proving that selected "
            "static PNG IDAT and APNG fdAT chunk boundaries do not change "
            "decoded pixels or frame playback when the concatenated zlib "
            "datastream is unchanged."
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
        ],
        "external_anchors": [
            {
                "source": "W3C PNG specification",
                "url": PNG_SOURCE_URL,
                "used_for": (
                    "PNG IDAT image-data concatenation, APNG fdAT frame_data "
                    "concatenation in sequence-number order, zero-length "
                    "fdAT frame_data fields, zlib compression method 0, and "
                    "filter-byte scanline payload boundaries."
                ),
            }
        ],
        "profile_count": len(profile_paths),
        "case_ids": list(PNG_APNG_IMAGE_DATA_CHUNKING_CASE_IDS),
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
            "case_family_count": len(PNG_APNG_IMAGE_DATA_CHUNKING_CASE_IDS),
            "png_case_count": sum(1 for result in case_results if result["carrier_family"] == "png"),
            "apng_case_count": sum(1 for result in case_results if result["carrier_family"] == "apng"),
            "zero_length_data_chunk_case_count": sum(
                1
                for result in case_results
                if 0 in result["expected_idat_data_lengths"]
                or 0 in result["expected_fdat_frame_data_lengths"]
            ),
            "zlib_header_split_case_count": sum(
                1 for result in case_results if result["split_target"] == "zlib_header"
            ),
            "adler32_split_case_count": sum(
                1 for result in case_results if result["split_target"] == "adler32"
            ),
            "max_data_chunk_count": max(
                result["decoded"]["data_chunk_count"] for result in case_results
            ),
            "live_external_editor_verified": False,
        },
        "closed_states": [
            "png_idat_arbitrary_boundary_reconstruction",
            "png_idat_zero_length_data_field_reconstruction",
            "apng_fdat_arbitrary_boundary_reconstruction",
            "apng_fdat_zero_length_frame_data_reconstruction",
            "png_apng_image_data_chunking_invalid_probe_rejection",
        ],
        "blocked_states": [
            "full_apng_png_conformance",
            "live_external_editor_rewrite_validation",
            "production_import_export_carrier_selection_final_decision",
            "manual_readability_calibration",
            "package_runtime_lifecycle_integration",
        ],
        "decision": "prototype_png_apng_image_data_chunking_subset",
        "notes": [
            "This lab validates selected chunk-boundary variants only; it does not broaden color, bit-depth, interlace, or playback semantics beyond the source decoders.",
            "The static PNG cases reuse the existing 8-bit RGBA/deep-color decoder path and split only the compressed IDAT byte stream.",
            "The APNG cases reuse the existing filtered frame-data decoder path and split only the second-frame fdAT frame_data byte stream.",
        ],
        "next_research_step": (
            "Continue remaining APNG/PNG coverage through explicit image-data "
            "fixtures, live external editor preservation, or final carrier "
            "selection evidence before claiming full conformance."
        ),
    }


def write_png_apng_image_data_chunking_artifacts(
    output_root: Path = Path("data/workshop_editor"),
    report: dict | None = None,
) -> dict:
    report = report or run_png_apng_image_data_chunking_lab()
    output_root.mkdir(parents=True, exist_ok=True)
    artifact_dir = output_root / "png_apng_image_data_chunking_stage0"
    cases_dir = artifact_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)

    summary_json = output_root / "png_apng_image_data_chunking_stage0.json"
    app_js = output_root / "png_apng_image_data_chunking.js"
    artifact_summary_json = artifact_dir / "png_apng_image_data_chunking_stage0.json"
    artifact_app_js = artifact_dir / "png_apng_image_data_chunking.js"
    readme = artifact_dir / "README.md"

    _write_json(summary_json, _json_report(report))
    _write_json(artifact_summary_json, _json_report(report))
    for result in report["case_results"]:
        (cases_dir / result["png_file_name"]).write_bytes(
            bytes.fromhex(result["png_bytes_hex"])
        )
    payload = (
        "window.MECHAGOTCHI_PNG_APNG_IMAGE_DATA_CHUNKING = "
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


def _decode_png_apng_image_data_chunking(png_bytes: bytes) -> dict:
    chunks = _read_chunks(png_bytes)
    _validate_idat_consecutiveness(chunks)
    names = [chunk["type"] for chunk in chunks]
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
            raise PNGAPNGImageDataChunkingError(family, family.replace("_", " "))
        return {
            "carrier_family": "apng",
            "canvas_width": decoded["canvas_width"],
            "canvas_height": decoded["canvas_height"],
            "frame_count": decoded["frame_count"],
            "animation_control": decoded["animation_control"],
            "pixel_hash": decoded["final_output_hash"],
            "display_hashes": decoded["display_hashes"],
            "final_output_hash": decoded["final_output_hash"],
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
        raise PNGAPNGImageDataChunkingError(_map_png_error_family(exc.family), exc.message) from exc
    return {
        "carrier_family": "png",
        "width": decoded["width"],
        "height": decoded["height"],
        "pixel_hash": _hash_pixels(decoded["pixels"]),
        "idat_data_lengths": idat_data_lengths,
        "fdat_frame_data_lengths": [],
        "idat_chunk_count": len(idat_data_lengths),
        "fdat_chunk_count": 0,
        "data_chunk_count": len(idat_data_lengths),
        "chunks": names,
        "filter_types_seen": decoded["filter_types_seen"],
    }


def _read_chunks(png_bytes: bytes) -> list[dict]:
    try:
        chunks = _read_png_chunks(png_bytes)
    except PNGDeepColorDecodeError as exc:
        raise PNGAPNGImageDataChunkingError(_map_png_error_family(exc.family), exc.message) from exc
    return [{"type": chunk["type"], "payload": chunk["payload"]} for chunk in chunks]


def _validate_idat_consecutiveness(chunks: list[dict]) -> None:
    names = [chunk["type"] for chunk in chunks]
    if "IDAT" not in names:
        raise PNGAPNGImageDataChunkingError("png_idat_missing", "PNG image data requires IDAT")
    first = names.index("IDAT")
    last = len(names) - 1 - names[::-1].index("IDAT")
    if any(name != "IDAT" for name in names[first : last + 1]):
        raise PNGAPNGImageDataChunkingError(
            "png_idat_not_consecutive",
            "IDAT chunks must be consecutive in this image-data chunking lab",
        )


def _split_image_datastream(payload: bytes, split_target: str) -> list[bytes]:
    if len(payload) < 8:
        raise PNGAPNGImageDataChunkingError(
            "png_image_data_too_short",
            "compressed datastream is too short for chunking cases",
        )
    if split_target == "leading_empty":
        return [b"", payload]
    if split_target == "zlib_header":
        return [payload[:1], payload[1:]]
    if split_target == "adler32":
        return [payload[:1], payload[1:2], payload[2:-4], payload[-4:-2], payload[-2:]]
    raise ValueError(f"unknown split target: {split_target}")


def _combined_idat_data(png_bytes: bytes) -> bytes:
    chunks = _read_chunks(png_bytes)
    return b"".join(chunk["payload"] for chunk in chunks if chunk["type"] == "IDAT")


def _combined_fdat_frame_data(png_bytes: bytes) -> bytes:
    chunks = _read_chunks(png_bytes)
    return b"".join(chunk["payload"][4:] for chunk in chunks if chunk["type"] == "fdAT")


def _replace_idat_chunks(png_bytes: bytes, segments: list[bytes]) -> bytes:
    chunks = _read_chunks(png_bytes)
    rewritten = [PNG_SIGNATURE]
    wrote = False
    for chunk in chunks:
        if chunk["type"] == "IDAT":
            if not wrote:
                for segment in segments:
                    rewritten.append(_png_chunk(b"IDAT", segment))
                wrote = True
            continue
        rewritten.append(_png_chunk(chunk["type"].encode("ascii"), chunk["payload"]))
    if not wrote:
        raise PNGAPNGImageDataChunkingError("png_idat_missing", "expected IDAT chunk")
    return b"".join(rewritten)


def _replace_fdat_chunks(png_bytes: bytes, segments: list[bytes]) -> bytes:
    chunks = _read_chunks(png_bytes)
    original_fdat = [chunk for chunk in chunks if chunk["type"] == "fdAT"]
    if not original_fdat:
        raise PNGAPNGImageDataChunkingError("apng_fdat_missing", "expected fdAT chunks")
    first_sequence = struct.unpack(">I", original_fdat[0]["payload"][:4])[0]
    rewritten = [PNG_SIGNATURE]
    wrote = False
    for chunk in chunks:
        if chunk["type"] == "fdAT":
            if not wrote:
                for offset, segment in enumerate(segments):
                    payload = struct.pack(">I", first_sequence + offset) + segment
                    rewritten.append(_png_chunk(b"fdAT", payload))
                wrote = True
            continue
        rewritten.append(_png_chunk(chunk["type"].encode("ascii"), chunk["payload"]))
    return b"".join(rewritten)


def _remove_chunks(png_bytes: bytes, chunk_types: set[str]) -> bytes:
    chunks = _read_chunks(png_bytes)
    rewritten = [PNG_SIGNATURE]
    for chunk in chunks:
        if chunk["type"] in chunk_types:
            continue
        rewritten.append(_png_chunk(chunk["type"].encode("ascii"), chunk["payload"]))
    return b"".join(rewritten)


def _mutate_first_data_chunk_byte(png_bytes: bytes, chunk_type: str, *, data_offset: int) -> bytes:
    chunks = _read_chunks(png_bytes)
    rewritten = [PNG_SIGNATURE]
    mutated = False
    for chunk in chunks:
        payload = chunk["payload"]
        if chunk["type"] == chunk_type and not mutated:
            if len(payload) <= data_offset:
                raise PNGAPNGImageDataChunkingError(
                    "png_image_data_too_short",
                    f"{chunk_type} payload is too short to corrupt",
                )
            mutable = bytearray(payload)
            mutable[data_offset] ^= 0xFF
            payload = bytes(mutable)
            mutated = True
        rewritten.append(_png_chunk(chunk["type"].encode("ascii"), payload))
    if not mutated:
        raise PNGAPNGImageDataChunkingError(
            f"{chunk_type.lower()}_missing",
            f"expected {chunk_type} chunk",
        )
    return b"".join(rewritten)


def _invalid_probe_results(cases: list[dict]) -> list[dict]:
    by_case = {case["case_id"]: case["png_bytes"] for case in cases}
    probes = [
        (
            "idat_nonconsecutive",
            make_idat_nonconsecutive_probe(by_case["png_idat_zlib_header_split"]),
            "png_idat_not_consecutive",
        ),
        (
            "corrupt_idat",
            make_corrupt_idat_probe(by_case["png_idat_adler32_split"]),
            "png_image_data_decompression_failed",
        ),
        (
            "missing_idat",
            make_missing_idat_probe(by_case["png_idat_leading_empty_chunk"]),
            "png_idat_missing",
        ),
        (
            "missing_fdat",
            make_missing_fdat_probe(by_case["apng_fdat_leading_empty_frame_data"]),
            "apng_frame_data_missing",
        ),
        (
            "sequence_gap",
            make_sequence_gap_probe(by_case["apng_fdat_zlib_header_split"]),
            "apng_sequence_number_invalid",
        ),
        (
            "corrupt_fdat",
            make_corrupt_fdat_probe(by_case["apng_fdat_adler32_split"]),
            "apng_frame_decompression_failed",
        ),
    ]
    results = []
    for probe_id, png_bytes, expected_family in probes:
        decoded = decode_png_apng_image_data_chunking(png_bytes)
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
        "pixel_hash",
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
                "split_target": result["split_target"],
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
        "# PNG/APNG Image Data Chunking Stage 0\n\n"
        "Bounded PNG IDAT and APNG fdAT datastream chunk-boundary matrix for "
        "Mechagotchi workshop carriers.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Case successes: {report['case_success_count']}/{report['case_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- PNG cases: {metrics['png_case_count']}\n"
        f"- APNG cases: {metrics['apng_case_count']}\n"
        f"- Zero-length data chunk cases: {metrics['zero_length_data_chunk_case_count']}\n\n"
        "This is a deterministic IDAT/fdAT chunk-boundary subset. It does not "
        "prove full APNG/PNG conformance, live editor rewrite preservation, "
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
        description="Generate PNG/APNG image-data chunking Stage 0 research artifacts."
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("data/workshop_editor"),
    )
    args = parser.parse_args()
    report = run_png_apng_image_data_chunking_lab()
    write_png_apng_image_data_chunking_artifacts(args.output_root, report)


if __name__ == "__main__":
    main()
