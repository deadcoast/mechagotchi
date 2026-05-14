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

from slip import is_grid_aligned
from validator import validate_grid

from standard_image_sidecar_decoder import (
    PNGDecodeError,
    decode_png_rgba,
    export_standard_png_with_sidecar,
    import_standard_png_with_sidecar,
)
from workshop_editor import compare_semantic_grid_fidelity


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
EMBEDDED_SIDECAR_KEYWORD = "mechagotchi.sidecar.v1"
REPORT_PATH = Path("data/workshop_editor/png_embedded_sidecar_writer_stage0.json")
DATA_PATH = Path("data/workshop_editor/png_embedded_sidecar_writer_data.js")


class PNGEmbeddedSidecarError(ValueError):
    def __init__(self, family: str, message: str):
        super().__init__(message)
        self.family = family
        self.message = message


def export_png_with_embedded_sidecar(grid: dict, slip_profile: dict) -> dict:
    canonical = export_standard_png_with_sidecar(grid, slip_profile)
    canonical_png_bytes = canonical["png_bytes"]
    sidecar = deepcopy(canonical["sidecar"])
    sidecar["sidecar_id"] = f"{grid['grid_id']}_embedded_png_sidecar"
    sidecar["limitations"] = [
        "Stage 0 embedded PNG proof stores Mechagotchi sidecar JSON in a PNG tEXt chunk.",
        "Asset binding hashes the canonical visual PNG without the embedded sidecar chunk to avoid self-referential hashing.",
        "PNG pixels remain the visual carrier; Mechagotchi semantics come from the embedded sidecar.",
    ]
    embedded_png_bytes = embed_sidecar_in_png_text_chunk(canonical_png_bytes, sidecar)
    return {
        "canonical_png_bytes": canonical_png_bytes,
        "embedded_png_bytes": embedded_png_bytes,
        "canonical_asset": canonical["asset"],
        "embedded_asset": _asset_from_png_bytes(
            embedded_png_bytes,
            asset_id=f"{grid['grid_id']}.embedded-sidecar.png",
            uri=f"generated://workshop/png-embedded-sidecar/{grid['grid_id']}.png",
        ),
        "sidecar": sidecar,
    }


def embed_sidecar_in_png_text_chunk(png_bytes: bytes, sidecar: dict) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    filtered_chunks = [
        chunk
        for chunk in chunks
        if not _is_embedded_sidecar_text_chunk(chunk)
    ]
    payload = {
        "metadata_model": "png_text_sidecar_v1",
        "keyword": EMBEDDED_SIDECAR_KEYWORD,
        "canonical_png_hash": _hash_bytes(png_bytes),
        "sidecar_hash": _hash_json(sidecar),
        "sidecar": sidecar,
        "hash_note": "canonical_png_hash excludes this metadata chunk to avoid self-referential hashing",
    }
    text_chunk = _chunk(
        "tEXt",
        _text_payload(EMBEDDED_SIDECAR_KEYWORD, json.dumps(payload, separators=(",", ":"), ensure_ascii=True)),
    )
    return _write_png_chunks([filtered_chunks[0], text_chunk] + filtered_chunks[1:])


def extract_embedded_sidecar_from_png(png_bytes: bytes) -> dict:
    chunks = _read_png_chunks(png_bytes)
    embedded_chunks = [
        chunk for chunk in chunks if _is_embedded_sidecar_text_chunk(chunk)
    ]
    if not embedded_chunks:
        raise PNGEmbeddedSidecarError(
            "embedded_sidecar_chunk_missing",
            "PNG does not contain a Mechagotchi embedded sidecar tEXt chunk",
        )
    if len(embedded_chunks) > 1:
        raise PNGEmbeddedSidecarError(
            "embedded_sidecar_chunk_duplicate",
            "PNG contains more than one Mechagotchi embedded sidecar tEXt chunk",
        )
    keyword, text = _decode_text_payload(embedded_chunks[0]["data"])
    try:
        metadata = json.loads(text)
    except json.JSONDecodeError as exc:
        raise PNGEmbeddedSidecarError(
            "embedded_sidecar_json_invalid",
            f"embedded sidecar JSON is invalid: {exc}",
        ) from exc

    canonical_png_bytes = remove_embedded_sidecar_chunks(png_bytes)
    if metadata.get("canonical_png_hash") != _hash_bytes(canonical_png_bytes):
        raise PNGEmbeddedSidecarError(
            "embedded_sidecar_canonical_hash_mismatch",
            "embedded sidecar canonical PNG hash does not match PNG without metadata chunk",
        )
    sidecar = metadata.get("sidecar")
    if not isinstance(sidecar, dict):
        raise PNGEmbeddedSidecarError(
            "embedded_sidecar_json_invalid",
            "embedded sidecar payload does not contain a sidecar object",
        )
    if metadata.get("sidecar_hash") != _hash_json(sidecar):
        raise PNGEmbeddedSidecarError(
            "embedded_sidecar_hash_mismatch",
            "embedded sidecar hash does not match sidecar object",
        )
    return {
        "ok": True,
        "keyword": keyword,
        "metadata": {
            key: metadata[key]
            for key in ["metadata_model", "keyword", "canonical_png_hash", "sidecar_hash", "hash_note"]
        },
        "sidecar": sidecar,
        "canonical_png_bytes": canonical_png_bytes,
        "embedded_chunk_count": len(embedded_chunks),
    }


def import_png_with_embedded_sidecar(
    png_bytes: bytes,
    source_grid: dict | None = None,
) -> dict:
    try:
        embedded_decoded = decode_png_rgba(png_bytes)
        extracted = extract_embedded_sidecar_from_png(png_bytes)
        canonical_decoded = decode_png_rgba(extracted["canonical_png_bytes"])
    except PNGDecodeError as exc:
        return _failed_import("png", exc.family, exc.message)
    except PNGEmbeddedSidecarError as exc:
        return _failed_import("embedded_sidecar", exc.family, exc.message)

    if embedded_decoded["pixels"] != canonical_decoded["pixels"]:
        return _failed_import(
            "png.pixels",
            "embedded_sidecar_pixel_mismatch",
            "embedded PNG pixels differ from canonical PNG pixels",
        )

    imported = import_standard_png_with_sidecar(
        extracted["canonical_png_bytes"],
        extracted["sidecar"],
    )
    if not imported["ok"]:
        result = _compact_import_result(imported)
        result["embedded_metadata"] = {"ok": False, "errors": imported["errors"]}
        return result

    restored = imported["restored_grid"]
    semantic_source = source_grid or restored
    diff = compare_semantic_grid_fidelity(semantic_source, restored)
    grid_validation = validate_grid(restored)
    profile = extracted["sidecar"]["slip_binding"]["profile_snapshot"]
    alignment = is_grid_aligned(restored, profile)
    return {
        "ok": grid_validation.ok and alignment.ok,
        "embedded_asset": _asset_from_png_bytes(
            png_bytes,
            asset_id=extracted["sidecar"]["asset_binding"]["asset_id"].replace(".png", ".embedded.png"),
            uri=extracted["sidecar"]["asset_binding"]["uri"].replace("standard-image", "png-embedded-sidecar"),
        ),
        "canonical_asset": imported["asset"],
        "decoded_png": _decoded_summary(embedded_decoded),
        "canonical_decoded_png": _decoded_summary(canonical_decoded),
        "embedded_metadata": {
            "ok": True,
            "keyword": extracted["keyword"],
            "metadata": extracted["metadata"],
            "embedded_chunk_count": extracted["embedded_chunk_count"],
        },
        "sidecar": extracted["sidecar"],
        "validation": imported["validation"],
        "restored_grid": restored,
        "restored_grid_validation": {
            "valid": grid_validation.ok,
            "errors": grid_validation.errors,
            "slip_aligned": alignment.ok,
            "slip_errors": alignment.errors,
        },
        "semantic_diff": diff,
        "semantic_fidelity": _semantic_fidelity(diff, semantic_source),
        "pixel_fidelity": 1.0,
        "errors": [],
        "error_families": [],
    }


def remove_embedded_sidecar_chunks(png_bytes: bytes) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    filtered_chunks = [
        chunk for chunk in chunks if not _is_embedded_sidecar_text_chunk(chunk)
    ]
    return _write_png_chunks(filtered_chunks)


def corrupt_embedded_sidecar_json_for_probe(png_bytes: bytes) -> bytes:
    return _replace_embedded_sidecar_text(
        png_bytes,
        "{not-json",
    )


def corrupt_embedded_sidecar_hash_for_probe(png_bytes: bytes) -> bytes:
    extracted = extract_embedded_sidecar_from_png(png_bytes)
    metadata = deepcopy(extracted["metadata"])
    metadata["sidecar"] = extracted["sidecar"]
    metadata["canonical_png_hash"] = "sha256:not-the-canonical-png"
    return _replace_embedded_sidecar_text(
        png_bytes,
        json.dumps(metadata, separators=(",", ":"), ensure_ascii=True),
    )


def run_png_embedded_sidecar_writer_lab(
    profile_paths: list[Path],
    generated_root: Path,
) -> dict:
    embedded_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        exported = export_png_with_embedded_sidecar(grid, profile)
        imported = import_png_with_embedded_sidecar(
            exported["embedded_png_bytes"],
            source_grid=grid,
        )
        embedded_results.append(
            {
                "profile_id": profile["profile_id"],
                "profile_path": _portable(profile_path),
                "grid_path": _portable(grid_path),
                "png_file_name": f"{profile['profile_id']}_embedded_sidecar.png",
                "sidecar_file_name": f"{profile['profile_id']}_embedded_sidecar.json",
                "embedded_png_bytes_hex": exported["embedded_png_bytes"].hex(),
                "embedded_png_byte_count": len(exported["embedded_png_bytes"]),
                "canonical_png_byte_count": len(exported["canonical_png_bytes"]),
                "canonical_asset": exported["canonical_asset"],
                "embedded_asset": exported["embedded_asset"],
                "sidecar": exported["sidecar"],
                "decoded_png": imported.get("decoded_png"),
                "canonical_decoded_png": imported.get("canonical_decoded_png"),
                "embedded_metadata": imported.get("embedded_metadata", {}),
                "import_result": _compact_import_result(imported),
                "restored_grid_validation": imported.get("restored_grid_validation", {}),
                "semantic_diff": imported.get("semantic_diff", {}),
                "semantic_fidelity": imported.get("semantic_fidelity", 0.0),
                "pixel_fidelity": imported.get("pixel_fidelity", 0.0),
            }
        )

    invalid_probe_results = _invalid_probe_results(embedded_results[0])
    success_count = sum(
        1
        for result in embedded_results
        if result["import_result"]["ok"]
        and result["restored_grid_validation"]["valid"]
        and result["restored_grid_validation"]["slip_aligned"]
        and result["semantic_fidelity"] == 1.0
        and result["pixel_fidelity"] == 1.0
    )
    invalid_rejected_count = sum(1 for result in invalid_probe_results if not result["ok"])
    return {
        "artifact_id": "png_embedded_sidecar_writer_stage0",
        "status": "research_png_embedded_sidecar_writer_no_package_code",
        "date": "2026-05-13",
        "purpose": (
            "Test a Stage 0 embedded PNG metadata writer/reader that stores "
            "Mechagotchi sidecar JSON in a PNG tEXt ancillary chunk."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "labs/workshop_editor/standard_image_sidecar_decoder.py",
            "labs/workshop_editor/png_embedded_sidecar_writer.py",
        ],
        "external_anchors": [
            {
                "source": "W3C PNG specification",
                "url": "https://www.w3.org/TR/png-3/",
                "used_for": "Ancillary text chunk ordering, safe decoder behavior, CRC validation, and editor-copy caveats.",
            }
        ],
        "profile_count": len(profile_paths),
        "embedded_roundtrip_count": len(embedded_results),
        "embedded_roundtrip_success_count": success_count,
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "metrics": {
            "embedded_roundtrip_success_rate": _ratio(success_count, len(embedded_results)),
            "mean_semantic_fidelity": round(
                sum(result["semantic_fidelity"] for result in embedded_results)
                / max(1, len(embedded_results)),
                6,
            ),
            "mean_pixel_fidelity": round(
                sum(result["pixel_fidelity"] for result in embedded_results)
                / max(1, len(embedded_results)),
                6,
            ),
            "invalid_probe_rejection_rate": _ratio(
                invalid_rejected_count,
                len(invalid_probe_results),
            ),
        },
        "embedded_results": embedded_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "embedded_png_metadata_writer_text_chunk",
            "embedded_png_metadata_reader_text_chunk",
            "embedded_png_sidecar_semantic_restore",
            "embedded_png_sidecar_hash_validation",
        ],
        "blocked_states": [
            "Adam7/APNG/full PNG conformance",
            "project-file native metadata writer",
            "full project-format coverage",
            "arbitrary atlas packing",
            "tags/layers",
            "production renderer playback",
            "package runtime lifecycle integration",
            "manual readability calibration",
            "profile-weighted evolution",
            "community profile packs",
        ],
        "decision": "prototype_png_embedded_sidecar_writer",
        "next_research_step": (
            "Keep project-file native metadata writers and full project-format "
            "coverage blocked until editor-native payload tests exist."
        ),
    }


def write_png_embedded_sidecar_writer_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "png_embedded_sidecar_writer_stage0.json", _json_report(report))
    for result in report["embedded_results"]:
        (output_dir / result["png_file_name"]).write_bytes(
            bytes.fromhex(result["embedded_png_bytes_hex"])
        )
        _write_json(output_dir / result["sidecar_file_name"], result["sidecar"])
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "png_embedded_sidecar_writer_data.js").write_text(
        "window.MECHAGOTCHI_PNG_EMBEDDED_SIDECAR_WRITER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _invalid_probe_results(reference_result: dict) -> list[dict]:
    png_bytes = bytes.fromhex(reference_result["embedded_png_bytes_hex"])
    missing_sidecar_png = remove_embedded_sidecar_chunks(png_bytes)
    corrupt_json_png = corrupt_embedded_sidecar_json_for_probe(png_bytes)
    corrupt_hash_png = corrupt_embedded_sidecar_hash_for_probe(png_bytes)
    return [
        _compact_import_result(import_png_with_embedded_sidecar(missing_sidecar_png)),
        _compact_import_result(import_png_with_embedded_sidecar(corrupt_json_png)),
        _compact_import_result(import_png_with_embedded_sidecar(corrupt_hash_png)),
    ]


def _read_png_chunks(png_bytes: bytes) -> list[dict]:
    if not png_bytes.startswith(PNG_SIGNATURE):
        raise PNGEmbeddedSidecarError("png_signature_invalid", "PNG signature is invalid")
    offset = len(PNG_SIGNATURE)
    chunks = []
    while offset < len(png_bytes):
        if offset + 12 > len(png_bytes):
            raise PNGEmbeddedSidecarError("png_chunk_truncated", "PNG chunk header is truncated")
        length = struct.unpack(">I", png_bytes[offset : offset + 4])[0]
        chunk_type_bytes = png_bytes[offset + 4 : offset + 8]
        chunk_type = chunk_type_bytes.decode("ascii", errors="strict")
        data_start = offset + 8
        data_end = data_start + length
        crc_end = data_end + 4
        if crc_end > len(png_bytes):
            raise PNGEmbeddedSidecarError("png_chunk_truncated", f"PNG chunk {chunk_type} is truncated")
        data = png_bytes[data_start:data_end]
        observed_crc = struct.unpack(">I", png_bytes[data_end:crc_end])[0]
        expected_crc = binascii.crc32(chunk_type_bytes + data) & 0xFFFFFFFF
        if observed_crc != expected_crc:
            raise PNGEmbeddedSidecarError("png_chunk_crc_mismatch", f"PNG chunk {chunk_type} CRC mismatch")
        chunks.append({"type": chunk_type, "data": data})
        offset = crc_end
        if chunk_type == "IEND":
            break
    if not chunks or chunks[0]["type"] != "IHDR":
        raise PNGEmbeddedSidecarError("png_ihdr_missing", "PNG IHDR chunk must be first")
    if chunks[-1]["type"] != "IEND":
        raise PNGEmbeddedSidecarError("png_iend_missing", "PNG IEND chunk must be last")
    return chunks


def _chunk(chunk_type: str, data: bytes) -> dict:
    if len(chunk_type) != 4:
        raise ValueError("PNG chunk type must be four characters")
    return {
        "type": chunk_type,
        "data": data,
    }


def _chunk_bytes(chunk: dict) -> bytes:
    chunk_type = chunk["type"].encode("ascii")
    data = chunk["data"]
    crc = binascii.crc32(chunk_type + data) & 0xFFFFFFFF
    return (
        struct.pack(">I", len(data))
        + chunk_type
        + data
        + struct.pack(">I", crc)
    )


def _text_payload(keyword: str, text: str) -> bytes:
    if "\x00" in keyword or len(keyword.encode("latin-1")) > 79:
        raise ValueError("PNG tEXt keyword must be 1..79 bytes without nulls")
    return keyword.encode("latin-1") + b"\x00" + text.encode("latin-1")


def _decode_text_payload(data: bytes) -> tuple[str, str]:
    if b"\x00" not in data:
        raise PNGEmbeddedSidecarError("embedded_sidecar_text_invalid", "PNG tEXt chunk lacks keyword separator")
    keyword_bytes, text_bytes = data.split(b"\x00", 1)
    return keyword_bytes.decode("latin-1"), text_bytes.decode("latin-1")


def _is_embedded_sidecar_text_chunk(chunk: dict) -> bool:
    if chunk["type"] != "tEXt" or b"\x00" not in chunk["data"]:
        return False
    keyword, _text = _decode_text_payload(chunk["data"])
    return keyword == EMBEDDED_SIDECAR_KEYWORD


def _replace_embedded_sidecar_text(png_bytes: bytes, replacement_text: str) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    replaced = False
    updated_chunks = []
    for chunk in chunks:
        if _is_embedded_sidecar_text_chunk(chunk):
            updated_chunks.append(
                _chunk("tEXt", _text_payload(EMBEDDED_SIDECAR_KEYWORD, replacement_text))
            )
            replaced = True
        else:
            updated_chunks.append(chunk)
    if not replaced:
        raise PNGEmbeddedSidecarError("embedded_sidecar_chunk_missing", "no embedded sidecar chunk to replace")
    return _write_png_chunks(updated_chunks)


def _write_png_chunks(chunks: list[dict]) -> bytes:
    payload = bytearray(PNG_SIGNATURE)
    for chunk in chunks:
        payload.extend(_chunk_bytes(chunk))
    return bytes(payload)


def _asset_from_png_bytes(png_bytes: bytes, *, asset_id: str, uri: str) -> dict:
    decoded = decode_png_rgba(png_bytes)
    return {
        "asset_id": asset_id,
        "format_id": "png",
        "media_type": "image/png",
        "uri": uri,
        "width": decoded["width"],
        "height": decoded["height"],
        "frame_count": 1,
        "content_hash": _hash_bytes(png_bytes),
        "semantic_policy": "embedded_sidecar_required",
    }


def _decoded_summary(decoded: dict) -> dict:
    return {
        "width": decoded["width"],
        "height": decoded["height"],
        "bit_depth": decoded["bit_depth"],
        "color_type": decoded["color_type"],
        "pixel_count": len(decoded["pixels"]),
        "chunks": decoded["chunks"],
    }


def _compact_import_result(result: dict) -> dict:
    return {
        "ok": result["ok"],
        "embedded_asset": result.get("embedded_asset"),
        "canonical_asset": result.get("canonical_asset"),
        "decoded_png": result.get("decoded_png"),
        "canonical_decoded_png": result.get("canonical_decoded_png"),
        "embedded_metadata": result.get("embedded_metadata"),
        "validation": result.get("validation"),
        "semantic_fidelity": result.get("semantic_fidelity", 0.0),
        "pixel_fidelity": result.get("pixel_fidelity", 0.0),
        "errors": result.get("errors", []),
        "error_families": result.get("error_families", []),
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


def _semantic_fidelity(diff: dict, source: dict) -> float:
    source_count = max(1, len(source.get("cells", [])))
    problem_count = (
        len(diff["changed_cells"])
        + len(diff["missing_cells"])
        + len(diff["added_cells"])
    )
    return round(max(0.0, 1.0 - problem_count / source_count), 6)


def _first_grid_path(profile: dict, generated_root: Path) -> Path:
    grid_paths = sorted((generated_root / profile["profile_id"]).glob("*.json"))
    if not grid_paths:
        raise ValueError(f"no generated grids found for profile: {profile['profile_id']}")
    return grid_paths[0]


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _portable(path: Path) -> str:
    return str(path).replace("\\", "/")


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def _hash_json(payload: object) -> str:
    return _hash_bytes(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8"))


def _hash_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _json_report(report: dict) -> dict:
    payload = deepcopy(report)
    for result in payload["embedded_results"]:
        result.pop("embedded_png_bytes_hex", None)
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
                "embedded_roundtrip_count",
                "embedded_roundtrip_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "embedded_summaries": [
            {
                "profile_id": result["profile_id"],
                "embedded_asset": result["embedded_asset"],
                "canonical_asset": result["canonical_asset"],
                "decoded_png": result["decoded_png"],
                "embedded_metadata": result["embedded_metadata"],
                "semantic_fidelity": result["semantic_fidelity"],
                "pixel_fidelity": result["pixel_fidelity"],
            }
            for result in json_report["embedded_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# PNG Embedded Sidecar Writer Stage 0\n\n"
        "Embedded PNG tEXt sidecar metadata writer/reader proof for "
        "Mechagotchi semantic grid metadata.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Embedded round-trip successes: {report['embedded_roundtrip_success_count']}"
        f"/{report['embedded_roundtrip_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- Mean semantic fidelity: {metrics['mean_semantic_fidelity']}\n"
        f"- Mean pixel fidelity: {metrics['mean_pixel_fidelity']}\n"
        f"- Decision: {report['decision']}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/workshop_editor/png_embedded_sidecar_writer_stage0"),
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
    report = run_png_embedded_sidecar_writer_lab(profile_paths, args.generated_root)
    write_png_embedded_sidecar_writer_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_PNG_EMBEDDED_SIDECAR_WRITER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(_json_report(report), indent=2))


if __name__ == "__main__":
    main()
