import argparse
import binascii
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

from png_apng_sidecar_decoder import export_apng_with_sidecar
from png_embedded_sidecar_writer import _chunk, _write_png_chunks
from png_variant_sidecar_decoder import export_png_variant_suite_with_sidecars
from standard_image_sidecar_decoder import PNG_SIGNATURE, export_standard_png_with_sidecar


REPORT_PATH = ROOT / "data/workshop_editor/png_apng_chunk_order_conformance_stage0.json"
DATA_PATH = ROOT / "data/workshop_editor/png_apng_chunk_order_conformance_data.js"

CONFORMANCE_CASE_IDS = [
    "static_rgba_single_idat",
    "rgba_split_idat",
    "indexed_plte_trns",
    "apng_static_first_frame",
]

PNG_SOURCE_URL = "https://www.w3.org/TR/png-3/"

KNOWN_CRITICAL_CHUNKS = {"IHDR", "PLTE", "IDAT", "IEND"}


class PNGAPNGChunkOrderError(ValueError):
    def __init__(self, family: str, message: str):
        super().__init__(message)
        self.family = family
        self.message = message


def export_png_apng_chunk_order_conformance_cases(
    grid: dict,
    slip_profile: dict,
) -> list[dict]:
    standard = export_standard_png_with_sidecar(grid, slip_profile)
    static_png = standard["png_bytes"]
    split_idat_png = split_idat_chunks(static_png)

    indexed_png = _indexed_png_with_trns(grid, slip_profile)
    apng_png = export_apng_with_sidecar(grid, slip_profile)["png_bytes"]

    cases = [
        _case(
            grid,
            slip_profile,
            "static_rgba_single_idat",
            static_png,
            "Static truecolor-alpha PNG with IHDR, one IDAT, and IEND.",
            expected_animation=False,
        ),
        _case(
            grid,
            slip_profile,
            "rgba_split_idat",
            split_idat_png,
            "Static truecolor-alpha PNG with consecutive split IDAT chunks.",
            expected_animation=False,
        ),
        _case(
            grid,
            slip_profile,
            "indexed_plte_trns",
            indexed_png,
            "Indexed-color PNG with PLTE before tRNS before IDAT.",
            expected_animation=False,
        ),
        _case(
            grid,
            slip_profile,
            "apng_static_first_frame",
            apng_png,
            "APNG with acTL before IDAT, fcTL sequence 0 on the static first frame, and fdAT for the second frame.",
            expected_animation=True,
        ),
    ]

    for case in cases:
        validation = validate_png_apng_chunk_order(
            case["png_bytes"],
            expected_animation=case["expected_animation"],
        )
        case["validation"] = validation
        case["png_hash"] = _hash_bytes(case["png_bytes"])
    return cases


def validate_png_apng_chunk_order(
    png_bytes: bytes,
    *,
    expected_animation: bool | None = None,
) -> dict:
    try:
        chunks = _parse_png_chunks(png_bytes)
        _validate_chunk_order(chunks, expected_animation=expected_animation)
        ihdr = _parse_ihdr(chunks[0]["data"])
        return {
            "ok": True,
            "case_id": _classify_case(chunks, ihdr),
            "chunks": [chunk["type"] for chunk in chunks],
            "chunk_count": len(chunks),
            "idat_count": sum(1 for chunk in chunks if chunk["type"] == "IDAT"),
            "color_type": ihdr["color_type"],
            "bit_depth": ihdr["bit_depth"],
            "interlace_method": ihdr["interlace_method"],
            "apng_sequence_numbers": _apng_sequence_numbers(chunks),
            "errors": [],
            "error_families": [],
        }
    except PNGAPNGChunkOrderError as exc:
        return {
            "ok": False,
            "case_id": "invalid",
            "chunks": _safe_chunk_types(png_bytes),
            "errors": [_error("png.chunk_order", exc.family, exc.message)],
            "error_families": [exc.family],
        }


def split_idat_chunks(png_bytes: bytes) -> bytes:
    chunks = _parse_png_chunks(png_bytes)
    updated = []
    split_done = False
    for chunk in chunks:
        if chunk["type"] == "IDAT" and not split_done:
            midpoint = max(1, len(chunk["data"]) // 2)
            updated.append(_chunk("IDAT", chunk["data"][:midpoint]))
            updated.append(_chunk("IDAT", chunk["data"][midpoint:]))
            split_done = True
        else:
            updated.append(_chunk(chunk["type"], chunk["data"]))
    if not split_done:
        raise PNGAPNGChunkOrderError("png_idat_missing", "no IDAT chunk to split")
    return _write_png_chunks(updated)


def duplicate_ihdr(png_bytes: bytes) -> bytes:
    chunks = _parse_png_chunks(png_bytes)
    updated = []
    duplicated = False
    for chunk in chunks:
        updated.append(_chunk(chunk["type"], chunk["data"]))
        if chunk["type"] == "IHDR" and not duplicated:
            updated.append(_chunk("IHDR", chunk["data"]))
            duplicated = True
    return _write_png_chunks(updated)


def insert_chunk_after_iend(png_bytes: bytes) -> bytes:
    return _write_png_chunks(
        _parse_png_chunks(png_bytes)
        + [_chunk("tEXt", b"mechagotchi.after_iend\x00invalid")]
    )


def move_plte_after_idat(png_bytes: bytes) -> bytes:
    chunks = _parse_png_chunks(png_bytes)
    plte = _single_chunk(chunks, "PLTE")
    without = [chunk for chunk in chunks if chunk["type"] != "PLTE"]
    updated = []
    inserted = False
    for chunk in without:
        updated.append(_chunk(chunk["type"], chunk["data"]))
        if chunk["type"] == "IDAT" and not inserted:
            updated.append(_chunk("PLTE", plte["data"]))
            inserted = True
    return _write_png_chunks(updated)


def move_trns_before_plte(png_bytes: bytes) -> bytes:
    chunks = _parse_png_chunks(png_bytes)
    trns = _single_chunk(chunks, "tRNS")
    updated = []
    inserted = False
    for chunk in chunks:
        if chunk["type"] == "tRNS":
            continue
        if chunk["type"] == "PLTE" and not inserted:
            updated.append(_chunk("tRNS", trns["data"]))
            inserted = True
        updated.append(_chunk(chunk["type"], chunk["data"]))
    return _write_png_chunks(updated)


def insert_text_between_idats(png_bytes: bytes) -> bytes:
    chunks = _parse_png_chunks(png_bytes)
    idat_seen = 0
    updated = []
    for chunk in chunks:
        updated.append(_chunk(chunk["type"], chunk["data"]))
        if chunk["type"] == "IDAT":
            idat_seen += 1
            if idat_seen == 1:
                updated.append(_chunk("tEXt", b"mechagotchi.idat_gap\x00invalid"))
    if idat_seen < 2:
        raise PNGAPNGChunkOrderError("png_idat_split_missing", "expected split IDAT chunks")
    return _write_png_chunks(updated)


def move_actl_after_idat(png_bytes: bytes) -> bytes:
    chunks = _parse_png_chunks(png_bytes)
    actl = _single_chunk(chunks, "acTL")
    without = [chunk for chunk in chunks if chunk["type"] != "acTL"]
    updated = []
    inserted = False
    for chunk in without:
        updated.append(_chunk(chunk["type"], chunk["data"]))
        if chunk["type"] == "IDAT" and not inserted:
            updated.append(_chunk("acTL", actl["data"]))
            inserted = True
    return _write_png_chunks(updated)


def rewrite_first_fctl_sequence(png_bytes: bytes, *, sequence_number: int) -> bytes:
    chunks = _parse_png_chunks(png_bytes)
    updated = []
    rewritten = False
    for chunk in chunks:
        if chunk["type"] == "fcTL" and not rewritten:
            updated.append(_chunk("fcTL", struct.pack(">I", sequence_number) + chunk["data"][4:]))
            rewritten = True
        else:
            updated.append(_chunk(chunk["type"], chunk["data"]))
    if not rewritten:
        raise PNGAPNGChunkOrderError("apng_fctl_missing", "no fcTL chunk to rewrite")
    return _write_png_chunks(updated)


def run_png_apng_chunk_order_conformance_lab(
    profile_paths: list[Path],
    generated_root: Path,
) -> dict:
    conformance_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid = _read_json(_first_grid_path(profile, generated_root))
        for case in export_png_apng_chunk_order_conformance_cases(grid, profile):
            conformance_results.append(
                {
                    "profile_id": profile["profile_id"],
                    "grid_id": grid["grid_id"],
                    "case_id": case["case_id"],
                    "description": case["description"],
                    "expected_animation": case["expected_animation"],
                    "png_file_name": case["png_file_name"],
                    "png_hash": case["png_hash"],
                    "png_bytes_hex": case["png_bytes"].hex(),
                    "validation": case["validation"],
                }
            )

    invalid_results = _invalid_probe_results(conformance_results)
    success_count = sum(1 for result in conformance_results if result["validation"]["ok"])
    invalid_rejected_count = sum(1 for result in invalid_results if result["rejected"])

    return {
        "artifact_id": "png_apng_chunk_order_conformance_stage0",
        "status": "research_png_apng_chunk_order_conformance_no_package_code",
        "profile_count": len(profile_paths),
        "conformance_case_ids": list(CONFORMANCE_CASE_IDS),
        "conformance_case_count": len(conformance_results),
        "conformance_case_success_count": success_count,
        "invalid_probe_count": len(invalid_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "conformance_results": conformance_results,
        "invalid_probe_results": invalid_results,
        "metrics": {
            "conformance_case_success_rate": _ratio(success_count, len(conformance_results)),
            "invalid_probe_rejection_rate": _ratio(invalid_rejected_count, len(invalid_results)),
            "profile_coverage": len({result["profile_id"] for result in conformance_results}),
            "valid_case_family_count": len(CONFORMANCE_CASE_IDS),
        },
        "closed_states": [
            "png_critical_chunk_order_matrix",
            "png_palette_transparency_order_matrix",
            "png_consecutive_idat_matrix",
            "apng_control_chunk_order_matrix",
            "apng_sequence_number_matrix",
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
                "used_for": "PNG signature, chunk layout, chunk ordering, PLTE/tRNS constraints, IDAT consecutiveness, APNG acTL/fcTL/fdAT ordering, and APNG sequence numbers.",
            }
        ],
        "decision": "prototype_png_apng_chunk_order_conformance_subset",
        "notes": [
            "This lab validates deterministic chunk-order and cardinality fixtures only.",
            "It does not claim exhaustive PNG/APNG image-data conformance, live editor preservation, or final carrier selection.",
        ],
    }


def write_png_apng_chunk_order_conformance_artifacts(
    output_dir: Path,
    report: dict,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    cases_dir = output_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "png_apng_chunk_order_conformance_stage0.json", _json_report(report))
    for result in report["conformance_results"]:
        (cases_dir / result["png_file_name"]).write_bytes(
            bytes.fromhex(result["png_bytes_hex"])
        )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "png_apng_chunk_order_conformance_data.js").write_text(
        "window.MECHAGOTCHI_PNG_APNG_CHUNK_ORDER_CONFORMANCE = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _case(
    grid: dict,
    slip_profile: dict,
    case_id: str,
    png_bytes: bytes,
    description: str,
    *,
    expected_animation: bool,
) -> dict:
    return {
        "case_id": case_id,
        "png_bytes": png_bytes,
        "png_file_name": f"{slip_profile['profile_id']}_{case_id}.png",
        "grid_id": grid["grid_id"],
        "profile_id": slip_profile["profile_id"],
        "description": description,
        "expected_animation": expected_animation,
    }


def _indexed_png_with_trns(grid: dict, slip_profile: dict) -> bytes:
    exports = export_png_variant_suite_with_sidecars(grid, slip_profile)
    indexed = next(export for export in exports if export["variant_id"] == "indexed_palette_average_paeth")
    png_bytes = indexed["png_bytes"]
    chunks = _parse_png_chunks(png_bytes)
    if any(chunk["type"] == "tRNS" for chunk in chunks):
        return png_bytes
    plte = _single_chunk(chunks, "PLTE")
    alpha_payload = bytes([255] * (len(plte["data"]) // 3))
    updated = []
    inserted = False
    for chunk in chunks:
        updated.append(_chunk(chunk["type"], chunk["data"]))
        if chunk["type"] == "PLTE" and not inserted:
            updated.append(_chunk("tRNS", alpha_payload))
            inserted = True
    return _write_png_chunks(updated)


def _parse_png_chunks(png_bytes: bytes) -> list[dict]:
    if not png_bytes.startswith(PNG_SIGNATURE):
        raise PNGAPNGChunkOrderError("png_signature_invalid", "PNG signature is missing or invalid")
    chunks = []
    offset = len(PNG_SIGNATURE)
    while offset < len(png_bytes):
        if offset + 8 > len(png_bytes):
            raise PNGAPNGChunkOrderError("png_chunk_truncated", "PNG chunk header is truncated")
        length = struct.unpack(">I", png_bytes[offset : offset + 4])[0]
        chunk_type = png_bytes[offset + 4 : offset + 8]
        data_start = offset + 8
        data_end = data_start + length
        crc_end = data_end + 4
        if crc_end > len(png_bytes):
            raise PNGAPNGChunkOrderError("png_chunk_truncated", "PNG chunk payload is truncated")
        data = png_bytes[data_start:data_end]
        expected_crc = struct.unpack(">I", png_bytes[data_end:crc_end])[0]
        actual_crc = binascii.crc32(data, binascii.crc32(chunk_type)) & 0xFFFFFFFF
        if expected_crc != actual_crc:
            raise PNGAPNGChunkOrderError("png_crc_mismatch", f"CRC mismatch in {chunk_type!r}")
        try:
            chunk_name = chunk_type.decode("ascii")
        except UnicodeDecodeError as exc:
            raise PNGAPNGChunkOrderError("png_chunk_type_invalid", "chunk type must be ASCII") from exc
        chunks.append({"type": chunk_name, "data": data})
        offset = crc_end
    return chunks


def _validate_chunk_order(chunks: list[dict], *, expected_animation: bool | None) -> None:
    if not chunks:
        raise PNGAPNGChunkOrderError("png_chunk_missing", "PNG contains no chunks")
    names = [chunk["type"] for chunk in chunks]

    for chunk in chunks:
        _validate_chunk_type_bits(chunk["type"])

    if names[0] != "IHDR":
        raise PNGAPNGChunkOrderError("png_ihdr_not_first", "IHDR must be the first chunk")
    if names.count("IHDR") > 1:
        raise PNGAPNGChunkOrderError("png_ihdr_duplicate", "PNG must contain exactly one IHDR chunk")
    if names.count("IEND") != 1:
        raise PNGAPNGChunkOrderError("png_iend_missing", "PNG must contain exactly one IEND chunk")
    if names[-1] != "IEND":
        raise PNGAPNGChunkOrderError("png_iend_not_last", "IEND must be the final chunk")
    if chunks[-1]["data"] != b"":
        raise PNGAPNGChunkOrderError("png_iend_not_empty", "IEND chunk must have empty data")

    ihdr = _parse_ihdr(chunks[0]["data"])
    if names.count("PLTE") > 1:
        raise PNGAPNGChunkOrderError("png_plte_duplicate", "PNG must not contain multiple PLTE chunks")
    if names.count("tRNS") > 1:
        raise PNGAPNGChunkOrderError("png_trns_duplicate", "PNG must not contain multiple tRNS chunks")
    if "IDAT" not in names:
        raise PNGAPNGChunkOrderError("png_idat_missing", "PNG must contain at least one IDAT chunk")

    first_idat = names.index("IDAT")
    last_idat = len(names) - 1 - names[::-1].index("IDAT")
    if any(name != "IDAT" for name in names[first_idat : last_idat + 1]):
        raise PNGAPNGChunkOrderError("png_idat_not_consecutive", "multiple IDAT chunks must be consecutive")

    if "PLTE" in names and names.index("PLTE") > first_idat:
        raise PNGAPNGChunkOrderError("png_plte_after_idat", "PLTE must appear before the first IDAT")
    if ihdr["color_type"] == 3 and "PLTE" not in names:
        raise PNGAPNGChunkOrderError("png_plte_missing", "indexed-color PNG requires PLTE")
    if ihdr["color_type"] in {0, 4} and "PLTE" in names:
        raise PNGAPNGChunkOrderError("png_plte_forbidden", "PLTE shall not appear for greyscale PNG types")

    if "tRNS" in names:
        trns_index = names.index("tRNS")
        if trns_index > first_idat:
            raise PNGAPNGChunkOrderError("png_trns_after_idat", "tRNS must appear before IDAT")
        if "PLTE" in names and trns_index < names.index("PLTE"):
            raise PNGAPNGChunkOrderError("png_trns_before_plte", "tRNS must appear after PLTE when PLTE is present")
        if ihdr["color_type"] in {4, 6}:
            raise PNGAPNGChunkOrderError("png_trns_forbidden", "tRNS shall not appear for alpha color types")
        if ihdr["color_type"] == 3:
            plte_entries = len(_single_chunk(chunks, "PLTE")["data"]) // 3
            if len(_single_chunk(chunks, "tRNS")["data"]) > plte_entries:
                raise PNGAPNGChunkOrderError("png_trns_invalid", "indexed tRNS exceeds PLTE length")

    _validate_apng_chunks(chunks, first_idat, expected_animation=expected_animation)


def _validate_apng_chunks(
    chunks: list[dict],
    first_idat: int,
    *,
    expected_animation: bool | None,
) -> None:
    names = [chunk["type"] for chunk in chunks]
    actl_count = names.count("acTL")
    if expected_animation is True and actl_count == 0:
        raise PNGAPNGChunkOrderError("apng_actl_missing", "expected APNG acTL chunk")
    if expected_animation is False and actl_count > 0:
        raise PNGAPNGChunkOrderError("apng_unexpected", "static PNG case unexpectedly contains APNG chunks")
    if actl_count > 1:
        raise PNGAPNGChunkOrderError("apng_actl_duplicate", "APNG acTL chunk must be unique")
    if actl_count == 0:
        if any(name in {"fcTL", "fdAT"} for name in names):
            raise PNGAPNGChunkOrderError("apng_control_missing", "fcTL/fdAT require acTL")
        return

    actl_index = names.index("acTL")
    if actl_index > first_idat:
        raise PNGAPNGChunkOrderError("apng_actl_after_idat", "acTL must appear before the first IDAT")
    actl = chunks[actl_index]["data"]
    if len(actl) != 8:
        raise PNGAPNGChunkOrderError("apng_actl_invalid", "acTL chunk must be 8 bytes")
    frame_count, _plays = struct.unpack(">II", actl)
    if frame_count == 0:
        raise PNGAPNGChunkOrderError("apng_frame_count_invalid", "APNG frame count must be positive")

    fctl_count = 0
    expected_sequence = 0
    current_frame_has_data = False
    current_frame_uses_idat = False
    idat_seen = False
    for index, chunk in enumerate(chunks):
        name = chunk["type"]
        if name == "IDAT":
            idat_seen = True
            if current_frame_uses_idat:
                current_frame_has_data = True
            continue
        if name == "fcTL":
            if len(chunk["data"]) != 26:
                raise PNGAPNGChunkOrderError("apng_fctl_invalid", "fcTL chunk must be 26 bytes")
            if fctl_count > 0 and not current_frame_has_data:
                raise PNGAPNGChunkOrderError("apng_frame_data_missing", "previous APNG frame lacks image data")
            sequence = struct.unpack(">I", chunk["data"][:4])[0]
            if sequence != expected_sequence:
                family = "apng_sequence_number_gap" if sequence > expected_sequence else "apng_sequence_number_duplicate"
                raise PNGAPNGChunkOrderError(family, "APNG sequence numbers must ascend without gaps or duplicates")
            expected_sequence += 1
            fctl_count += 1
            current_frame_uses_idat = index < first_idat
            current_frame_has_data = False
            continue
        if name == "fdAT":
            if fctl_count == 0:
                raise PNGAPNGChunkOrderError("apng_fdat_without_fctl", "fdAT requires preceding fcTL")
            if len(chunk["data"]) < 4:
                raise PNGAPNGChunkOrderError("apng_fdat_invalid", "fdAT chunk must include a sequence number")
            if not idat_seen:
                raise PNGAPNGChunkOrderError("apng_fdat_before_idat", "fdAT must not precede the default image IDAT")
            sequence = struct.unpack(">I", chunk["data"][:4])[0]
            if sequence != expected_sequence:
                family = "apng_sequence_number_gap" if sequence > expected_sequence else "apng_sequence_number_duplicate"
                raise PNGAPNGChunkOrderError(family, "APNG sequence numbers must ascend without gaps or duplicates")
            expected_sequence += 1
            current_frame_has_data = True

    if fctl_count != frame_count:
        raise PNGAPNGChunkOrderError("apng_frame_count_mismatch", "acTL frame count does not match fcTL chunks")
    if not current_frame_has_data:
        raise PNGAPNGChunkOrderError("apng_frame_data_missing", "final APNG frame lacks image data")


def _parse_ihdr(data: bytes) -> dict:
    if len(data) != 13:
        raise PNGAPNGChunkOrderError("png_ihdr_invalid", "IHDR chunk length must be 13")
    width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(
        ">IIBBBBB",
        data,
    )
    if width == 0 or height == 0:
        raise PNGAPNGChunkOrderError("png_ihdr_invalid", "PNG width and height must be positive")
    allowed = {
        0: {1, 2, 4, 8, 16},
        2: {8, 16},
        3: {1, 2, 4, 8},
        4: {8, 16},
        6: {8, 16},
    }
    if color_type not in allowed:
        raise PNGAPNGChunkOrderError("png_color_type_invalid", "PNG color type is unsupported")
    if bit_depth not in allowed[color_type]:
        raise PNGAPNGChunkOrderError("png_bit_depth_invalid", "PNG bit depth is invalid for the color type")
    if compression != 0:
        raise PNGAPNGChunkOrderError("png_compression_invalid", "PNG compression method must be 0")
    if filter_method != 0:
        raise PNGAPNGChunkOrderError("png_filter_method_invalid", "PNG filter method must be 0")
    if interlace not in {0, 1}:
        raise PNGAPNGChunkOrderError("png_interlace_invalid", "PNG interlace method must be 0 or 1")
    return {
        "width": width,
        "height": height,
        "bit_depth": bit_depth,
        "color_type": color_type,
        "compression_method": compression,
        "filter_method": filter_method,
        "interlace_method": interlace,
    }


def _validate_chunk_type_bits(chunk_type: str) -> None:
    if len(chunk_type) != 4 or not chunk_type.isascii() or not chunk_type.isalpha():
        raise PNGAPNGChunkOrderError("png_chunk_type_invalid", "chunk type must be four ASCII letters")
    if chunk_type[2].islower():
        raise PNGAPNGChunkOrderError("png_chunk_reserved_bit_invalid", "PNG chunk reserved bit must be uppercase")
    if chunk_type[0].isupper() and chunk_type not in KNOWN_CRITICAL_CHUNKS:
        raise PNGAPNGChunkOrderError("png_unknown_critical_chunk", "unknown critical PNG chunks cannot be interpreted")


def _classify_case(chunks: list[dict], ihdr: dict) -> str:
    names = [chunk["type"] for chunk in chunks]
    if "acTL" in names:
        return "apng_static_first_frame"
    if ihdr["color_type"] == 3:
        return "indexed_plte_trns"
    if names.count("IDAT") > 1:
        return "rgba_split_idat"
    return "static_rgba_single_idat"


def _apng_sequence_numbers(chunks: list[dict]) -> list[int]:
    numbers = []
    for chunk in chunks:
        if chunk["type"] in {"fcTL", "fdAT"} and len(chunk["data"]) >= 4:
            numbers.append(struct.unpack(">I", chunk["data"][:4])[0])
    return numbers


def _single_chunk(chunks: list[dict], chunk_type: str) -> dict:
    matches = [chunk for chunk in chunks if chunk["type"] == chunk_type]
    if len(matches) != 1:
        raise PNGAPNGChunkOrderError(
            f"png_{chunk_type.lower()}_missing",
            f"expected exactly one {chunk_type} chunk",
        )
    return matches[0]


def _invalid_probe_results(conformance_results: list[dict]) -> list[dict]:
    reference_by_case = {result["case_id"]: result for result in conformance_results[:4]}
    static_png = bytes.fromhex(reference_by_case["static_rgba_single_idat"]["png_bytes_hex"])
    indexed_png = bytes.fromhex(reference_by_case["indexed_plte_trns"]["png_bytes_hex"])
    split_idat_png = bytes.fromhex(reference_by_case["rgba_split_idat"]["png_bytes_hex"])
    apng_png = bytes.fromhex(reference_by_case["apng_static_first_frame"]["png_bytes_hex"])
    probes = [
        (
            "duplicate_ihdr",
            duplicate_ihdr(static_png),
            None,
            "png_ihdr_duplicate",
        ),
        (
            "chunk_after_iend",
            insert_chunk_after_iend(static_png),
            None,
            "png_iend_not_last",
        ),
        (
            "plte_after_idat",
            move_plte_after_idat(indexed_png),
            None,
            "png_plte_after_idat",
        ),
        (
            "trns_before_plte",
            move_trns_before_plte(indexed_png),
            None,
            "png_trns_before_plte",
        ),
        (
            "idat_not_consecutive",
            insert_text_between_idats(split_idat_png),
            None,
            "png_idat_not_consecutive",
        ),
        (
            "actl_after_idat",
            move_actl_after_idat(apng_png),
            True,
            "apng_actl_after_idat",
        ),
        (
            "fctl_sequence_gap",
            rewrite_first_fctl_sequence(
                apng_png,
                sequence_number=3,
            ),
            True,
            "apng_sequence_number_gap",
        ),
    ]
    results = []
    for probe_id, png_bytes, expected_animation, expected_family in probes:
        validation = validate_png_apng_chunk_order(
            png_bytes,
            expected_animation=expected_animation,
        )
        results.append(
            {
                "probe_id": probe_id,
                "expected_family": expected_family,
                "rejected": not validation["ok"] and expected_family in validation["error_families"],
                "validation": validation,
            }
        )
    return results


def _safe_chunk_types(png_bytes: bytes) -> list[str]:
    try:
        return [chunk["type"] for chunk in _parse_png_chunks(png_bytes)]
    except PNGAPNGChunkOrderError:
        return []


def _error(path: str, family: str, message: str | None = None) -> dict:
    return {
        "path": path,
        "family": family,
        "message": message or family.replace("_", " "),
    }


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def _hash_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _first_grid_path(profile: dict, generated_root: Path) -> Path:
    grid_paths = sorted((generated_root / profile["profile_id"]).glob("*.json"))
    if not grid_paths:
        raise ValueError(f"no generated grids found for profile: {profile['profile_id']}")
    return grid_paths[0]


def _json_report(report: dict) -> dict:
    payload = deepcopy(report)
    for result in payload["conformance_results"]:
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
                "conformance_case_ids",
                "conformance_case_count",
                "conformance_case_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "conformance_summaries": [
            {
                "profile_id": result["profile_id"],
                "grid_id": result["grid_id"],
                "case_id": result["case_id"],
                "description": result["description"],
                "png_file_name": result["png_file_name"],
                "png_hash": result["png_hash"],
                "validation": result["validation"],
            }
            for result in json_report["conformance_results"]
        ],
        "invalid_probe_results": json_report["invalid_probe_results"],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# PNG/APNG Chunk Order Conformance Stage 0\n\n"
        "Bounded PNG/APNG chunk-order and cardinality conformance matrix for "
        "Mechagotchi workshop carriers.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Conformance case successes: {report['conformance_case_success_count']}"
        f"/{report['conformance_case_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- Success rate: {metrics['conformance_case_success_rate']}\n"
        f"- Invalid rejection rate: {metrics['invalid_probe_rejection_rate']}\n\n"
        "This is a deterministic chunk-order subset. It does not prove full "
        "APNG/PNG conformance, live editor rewrite preservation, or final "
        "production carrier selection.\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "data/workshop_editor/png_apng_chunk_order_conformance_stage0",
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
    report = run_png_apng_chunk_order_conformance_lab(profile_paths, args.generated_root)
    write_png_apng_chunk_order_conformance_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_PNG_APNG_CHUNK_ORDER_CONFORMANCE = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
