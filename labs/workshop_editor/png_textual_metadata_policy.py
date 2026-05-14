import argparse
import json
import sys
import zlib
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME_DIR = ROOT / "labs" / "grid_genome"
if str(GRID_GENOME_DIR) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME_DIR))

from slip import is_grid_aligned
from validator import validate_grid

from png_embedded_sidecar_writer import (
    PNGEmbeddedSidecarError,
    _asset_from_png_bytes,
    _chunk,
    _compact_import_result,
    _decoded_summary,
    _error,
    _failed_import,
    _first_grid_path,
    _hash_bytes,
    _hash_json,
    _portable,
    _ratio,
    _read_json,
    _read_png_chunks,
    _semantic_fidelity,
    _write_json,
    _write_png_chunks,
)
from standard_image_sidecar_decoder import (
    PNGDecodeError,
    decode_png_rgba,
    export_standard_png_with_sidecar,
    import_standard_png_with_sidecar,
)
from workshop_editor import compare_semantic_grid_fidelity


TEXTUAL_METADATA_KEYWORD = "mechagotchi.sidecar.v1"
REPORT_PATH = Path("data/workshop_editor/png_textual_metadata_policy_stage0.json")
DATA_PATH = Path("data/workshop_editor/png_textual_metadata_policy_data.js")
METADATA_MODEL = "png_textual_metadata_policy_v1"
ASCII_PROBE = "cafe ascii metadata"
UNICODE_PROBE = "caf\u00e9 \u0394 metadata"


class PNGTextualMetadataPolicyError(ValueError):
    def __init__(self, family: str, message: str):
        super().__init__(message)
        self.family = family
        self.message = message


VARIANT_POLICIES = [
    {
        "variant_id": "text_ascii",
        "chunk_type": "tEXt",
        "compressed": False,
        "encoding_policy": "ascii_json_in_latin1_text_chunk",
        "ensure_ascii": True,
    },
    {
        "variant_id": "ztxt_ascii",
        "chunk_type": "zTXt",
        "compressed": True,
        "encoding_policy": "ascii_json_in_latin1_ztxt_chunk",
        "ensure_ascii": True,
    },
    {
        "variant_id": "itxt_utf8",
        "chunk_type": "iTXt",
        "compressed": False,
        "encoding_policy": "utf8_json_in_itxt_chunk",
        "ensure_ascii": False,
    },
    {
        "variant_id": "itxt_utf8_compressed",
        "chunk_type": "iTXt",
        "compressed": True,
        "encoding_policy": "utf8_json_in_itxt_chunk",
        "ensure_ascii": False,
    },
]


def export_png_textual_metadata_bundle(grid: dict, slip_profile: dict) -> dict:
    canonical = export_standard_png_with_sidecar(grid, slip_profile)
    canonical_png_bytes = canonical["png_bytes"]
    sidecar = deepcopy(canonical["sidecar"])
    sidecar["sidecar_id"] = f"{grid['grid_id']}_png_textual_metadata_policy_sidecar"
    sidecar["limitations"] = [
        "Stage 0 PNG textual metadata proof covers tEXt, zTXt, and iTXt metadata carriers only.",
        "Asset binding hashes the canonical visual PNG without the textual metadata chunk to avoid self-referential hashing.",
        "Live external editor open-save preservation is not verified by this lab.",
    ]

    metadata_base = {
        "metadata_model": METADATA_MODEL,
        "keyword": TEXTUAL_METADATA_KEYWORD,
        "canonical_png_hash": _hash_bytes(canonical_png_bytes),
        "sidecar_hash": _hash_json(sidecar),
        "ascii_probe": ASCII_PROBE,
        "unicode_probe": UNICODE_PROBE,
        "sidecar": sidecar,
        "hash_note": "canonical_png_hash excludes Mechagotchi textual metadata chunks",
    }
    variants = [
        _build_variant(canonical_png_bytes, metadata_base, policy, grid, slip_profile)
        for policy in VARIANT_POLICIES
    ]
    return {
        "canonical_png_bytes": canonical_png_bytes,
        "canonical_asset": canonical["asset"],
        "sidecar": sidecar,
        "metadata": {
            "metadata_model": METADATA_MODEL,
            "keyword": TEXTUAL_METADATA_KEYWORD,
            "canonical_png_hash": metadata_base["canonical_png_hash"],
            "sidecar_hash": metadata_base["sidecar_hash"],
            "ascii_probe": ASCII_PROBE,
            "unicode_probe": UNICODE_PROBE,
            "variant_ids": [variant["variant_id"] for variant in variants],
        },
        "variants": variants,
    }


def import_png_textual_metadata(
    png_bytes: bytes,
    source_grid: dict | None = None,
) -> dict:
    try:
        embedded_decoded = decode_png_rgba(png_bytes)
        extracted = _extract_textual_metadata(png_bytes)
        canonical_decoded = decode_png_rgba(extracted["canonical_png_bytes"])
    except PNGDecodeError as exc:
        return _failed_import("png", exc.family, exc.message)
    except (PNGEmbeddedSidecarError, PNGTextualMetadataPolicyError) as exc:
        return _failed_import("png.textual_metadata", exc.family, exc.message)

    if embedded_decoded["pixels"] != canonical_decoded["pixels"]:
        return _failed_import(
            "png.pixels",
            "png_textual_metadata_pixel_mismatch",
            "PNG pixels differ after textual metadata removal",
        )

    imported = import_standard_png_with_sidecar(
        extracted["canonical_png_bytes"],
        extracted["sidecar"],
    )
    if not imported["ok"]:
        result = _compact_import_result(imported)
        result["metadata_policy"] = {"ok": False, "errors": imported["errors"]}
        return result

    restored = imported["restored_grid"]
    semantic_source = source_grid or restored
    diff = compare_semantic_grid_fidelity(semantic_source, restored)
    grid_validation = validate_grid(restored)
    profile = extracted["sidecar"]["slip_binding"]["profile_snapshot"]
    alignment = is_grid_aligned(restored, profile)
    return {
        "ok": grid_validation.ok and alignment.ok,
        "textual_metadata_asset": _asset_from_png_bytes(
            png_bytes,
            asset_id=extracted["sidecar"]["asset_binding"]["asset_id"].replace(
                ".png", f".{extracted['metadata']['variant_id']}.png"
            ),
            uri=extracted["sidecar"]["asset_binding"]["uri"].replace(
                "standard-image", "png-textual-metadata-policy"
            ),
        ),
        "canonical_asset": imported["asset"],
        "decoded_png": _decoded_summary(embedded_decoded),
        "canonical_decoded_png": _decoded_summary(canonical_decoded),
        "metadata_policy": {
            "ok": True,
            "keyword": extracted["keyword"],
            "variant_id": extracted["metadata"]["variant_id"],
            "chunk_type": extracted["chunk_type"],
            "encoding_policy": extracted["encoding_policy"],
            "compressed": extracted["compressed"],
            "metadata_model": extracted["metadata"]["metadata_model"],
            "textual_chunk_count": extracted["textual_chunk_count"],
            "unicode_metadata_supported": extracted["chunk_type"] == "iTXt",
            "live_external_editor_verified": False,
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


def remove_png_textual_metadata_chunks(png_bytes: bytes) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    return _write_png_chunks([chunk for chunk in chunks if not _is_policy_chunk(chunk)])


def duplicate_png_textual_metadata_chunk(png_bytes: bytes) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    updated = []
    duplicated = False
    for chunk in chunks:
        updated.append(chunk)
        if _is_policy_chunk(chunk) and not duplicated:
            updated.append(deepcopy(chunk))
            duplicated = True
    if not duplicated:
        raise PNGTextualMetadataPolicyError(
            "png_textual_metadata_chunk_missing",
            "no textual metadata chunk to duplicate",
        )
    return _write_png_chunks(updated)


def tamper_png_textual_metadata_non_ascii_text_policy(png_bytes: bytes) -> bytes:
    extracted = _extract_textual_metadata(png_bytes)
    metadata = deepcopy(extracted["metadata"])
    metadata["unicode_probe"] = "caf\u00e9"
    replacement_text = json.dumps(metadata, separators=(",", ":"), ensure_ascii=False)
    return _replace_policy_chunk(
        png_bytes,
        "tEXt",
        _text_chunk_data(TEXTUAL_METADATA_KEYWORD, replacement_text),
    )


def tamper_png_textual_metadata_ztxt_method(png_bytes: bytes) -> bytes:
    chunk = _single_policy_chunk(png_bytes)
    if chunk["type"] != "zTXt":
        raise PNGTextualMetadataPolicyError(
            "png_textual_metadata_wrong_probe_variant",
            "zTXt compression method probe requires a zTXt policy chunk",
        )
    data = bytearray(chunk["data"])
    separator_index = data.index(0)
    data[separator_index + 1] = 1
    return _replace_policy_chunk(png_bytes, "zTXt", bytes(data))


def corrupt_png_textual_metadata_ztxt_stream(png_bytes: bytes) -> bytes:
    chunk = _single_policy_chunk(png_bytes)
    if chunk["type"] != "zTXt":
        raise PNGTextualMetadataPolicyError(
            "png_textual_metadata_wrong_probe_variant",
            "zTXt decompression probe requires a zTXt policy chunk",
        )
    data = bytearray(chunk["data"])
    separator_index = data.index(0)
    data[separator_index + 2 :] = b"not-a-zlib-stream"
    return _replace_policy_chunk(png_bytes, "zTXt", bytes(data))


def corrupt_png_textual_metadata_itxt_utf8(png_bytes: bytes) -> bytes:
    chunk = _single_policy_chunk(png_bytes)
    if chunk["type"] != "iTXt":
        raise PNGTextualMetadataPolicyError(
            "png_textual_metadata_wrong_probe_variant",
            "iTXt UTF-8 probe requires an iTXt policy chunk",
        )
    prefix, _text = _itxt_prefix_and_text_bytes(chunk["data"])
    return _replace_policy_chunk(png_bytes, "iTXt", prefix + b"\xff\xfe\xfa")


def corrupt_png_textual_metadata_canonical_hash(png_bytes: bytes) -> bytes:
    extracted = _extract_textual_metadata(png_bytes)
    metadata = deepcopy(extracted["metadata"])
    metadata["canonical_png_hash"] = "sha256:not-the-canonical-png"
    policy = _policy_for_variant(metadata["variant_id"])
    data = _encode_metadata_chunk(metadata, policy)
    return _replace_policy_chunk(png_bytes, policy["chunk_type"], data)


def run_png_textual_metadata_policy_lab(
    profile_paths: list[Path],
    generated_root: Path,
) -> dict:
    textual_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        bundle = export_png_textual_metadata_bundle(grid, profile)
        for variant in bundle["variants"]:
            imported = import_png_textual_metadata(
                variant["png_bytes"],
                source_grid=grid,
            )
            textual_results.append(
                {
                    "profile_id": profile["profile_id"],
                    "profile_path": _portable(profile_path),
                    "grid_path": _portable(grid_path),
                    "variant_id": variant["variant_id"],
                    "chunk_type": variant["chunk_type"],
                    "encoding_policy": variant["encoding_policy"],
                    "compressed": variant["compressed"],
                    "png_file_name": variant["png_file_name"],
                    "png_bytes_hex": variant["png_bytes"].hex(),
                    "png_byte_count": len(variant["png_bytes"]),
                    "canonical_png_byte_count": len(variant["canonical_png_bytes"]),
                    "metadata": _metadata_summary(variant["metadata"]),
                    "decoded_png": imported.get("decoded_png"),
                    "canonical_decoded_png": imported.get("canonical_decoded_png"),
                    "metadata_policy": imported.get("metadata_policy"),
                    "import_result": _compact_textual_import_result(imported),
                    "semantic_fidelity": imported.get("semantic_fidelity", 0.0),
                    "pixel_fidelity": imported.get("pixel_fidelity", 0.0),
                    "ok": imported["ok"],
                }
            )

    invalid_probe_results = _invalid_probe_results_for_report(textual_results)
    roundtrip_count = len(textual_results)
    roundtrip_success_count = sum(1 for result in textual_results if result["ok"])
    invalid_probe_count = len(invalid_probe_results)
    invalid_probe_rejected_count = sum(
        1 for result in invalid_probe_results if not result["ok"]
    )
    return {
        "artifact_id": "png_textual_metadata_policy_stage0",
        "status": "research_png_textual_metadata_policy_no_package_code",
        "profile_count": len(profile_paths),
        "textual_metadata_roundtrip_count": roundtrip_count,
        "textual_metadata_roundtrip_success_count": roundtrip_success_count,
        "invalid_probe_count": invalid_probe_count,
        "invalid_probe_rejected_count": invalid_probe_rejected_count,
        "variant_policies": [
            {
                key: policy[key]
                for key in ["variant_id", "chunk_type", "compressed", "encoding_policy"]
            }
            for policy in VARIANT_POLICIES
        ],
        "textual_metadata_results": textual_results,
        "invalid_probe_results": invalid_probe_results,
        "metrics": {
            "textual_metadata_roundtrip_success_rate": _ratio(
                roundtrip_success_count, roundtrip_count
            ),
            "mean_semantic_fidelity": _mean(
                result["semantic_fidelity"] for result in textual_results
            ),
            "mean_pixel_fidelity": _mean(
                result["pixel_fidelity"] for result in textual_results
            ),
            "invalid_probe_rejection_rate": _ratio(
                invalid_probe_rejected_count, invalid_probe_count
            ),
        },
        "closed_states": [
            "png_textual_metadata_text_ascii_policy",
            "png_textual_metadata_ztxt_compressed_policy",
            "png_textual_metadata_itxt_utf8_policy",
            "png_textual_metadata_hash_validation",
            "png_textual_metadata_invalid_probe_rejection",
        ],
        "blocked_states": [
            "live_external_editor_rewrite_validation",
            "Adam7/APNG/full PNG conformance",
            "arbitrary Aseprite project schema coverage",
            "full project-format coverage",
            "package_runtime_lifecycle_integration",
            "manual readability calibration",
            "profile_weighted_evolution",
            "community profile packs",
        ],
        "external_sources": [
            {
                "name": "W3C Portable Network Graphics (PNG) Specification, Third Edition",
                "url": "https://www.w3.org/TR/png-3/",
                "used_for": "tEXt, zTXt, and iTXt textual chunk structure and encoding policy anchors",
            }
        ],
        "decision": "prototype_png_textual_metadata_policy",
        "next_research_step": (
            "Keep live external editor rewrite validation, Adam7/APNG/full PNG "
            "conformance, and package runtime lifecycle integration blocked "
            "until each has explicit fixtures and authorization."
        ),
    }


def write_png_textual_metadata_policy_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(
        output_dir / "png_textual_metadata_policy_stage0.json",
        _json_report(report),
    )
    for result in report["textual_metadata_results"]:
        (output_dir / result["png_file_name"]).write_bytes(
            bytes.fromhex(result["png_bytes_hex"])
        )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "png_textual_metadata_policy_data.js").write_text(
        "window.MECHAGOTCHI_PNG_TEXTUAL_METADATA_POLICY = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _build_variant(
    canonical_png_bytes: bytes,
    metadata_base: dict,
    policy: dict,
    grid: dict,
    slip_profile: dict,
) -> dict:
    metadata = deepcopy(metadata_base)
    metadata.update(
        {
            "variant_id": policy["variant_id"],
            "chunk_type": policy["chunk_type"],
            "encoding_policy": policy["encoding_policy"],
            "compressed": policy["compressed"],
        }
    )
    data = _encode_metadata_chunk(metadata, policy)
    png_bytes = _insert_policy_chunk(canonical_png_bytes, policy["chunk_type"], data)
    return {
        "variant_id": policy["variant_id"],
        "chunk_type": policy["chunk_type"],
        "compressed": policy["compressed"],
        "encoding_policy": policy["encoding_policy"],
        "png_bytes": png_bytes,
        "canonical_png_bytes": canonical_png_bytes,
        "metadata": metadata,
        "png_file_name": f"{slip_profile['profile_id']}_{policy['variant_id']}.png",
        "grid_id": grid["grid_id"],
        "profile_id": slip_profile["profile_id"],
    }


def _extract_textual_metadata(png_bytes: bytes) -> dict:
    chunks = _read_png_chunks(png_bytes)
    policy_chunks = [chunk for chunk in chunks if _is_policy_chunk(chunk)]
    if not policy_chunks:
        raise PNGTextualMetadataPolicyError(
            "png_textual_metadata_chunk_missing",
            "PNG does not contain a Mechagotchi textual metadata chunk",
        )
    if len(policy_chunks) > 1:
        raise PNGTextualMetadataPolicyError(
            "png_textual_metadata_chunk_duplicate",
            "PNG contains more than one Mechagotchi textual metadata chunk",
        )

    decoded = _decode_policy_chunk(policy_chunks[0])
    try:
        metadata = json.loads(decoded["text"])
    except json.JSONDecodeError as exc:
        raise PNGTextualMetadataPolicyError(
            "png_textual_metadata_json_invalid",
            f"PNG textual metadata JSON is invalid: {exc}",
        ) from exc

    _validate_metadata_shape(metadata)
    if metadata.get("keyword") != TEXTUAL_METADATA_KEYWORD:
        raise PNGTextualMetadataPolicyError(
            "png_textual_metadata_keyword_mismatch",
            "PNG textual metadata keyword does not match policy keyword",
        )
    if metadata.get("chunk_type") != decoded["chunk_type"]:
        raise PNGTextualMetadataPolicyError(
            "png_textual_metadata_chunk_type_mismatch",
            "PNG textual metadata chunk type does not match metadata",
        )
    if metadata.get("compressed") != decoded["compressed"]:
        raise PNGTextualMetadataPolicyError(
            "png_textual_metadata_compression_mismatch",
            "PNG textual metadata compression flag does not match metadata",
        )
    if metadata.get("encoding_policy") != decoded["encoding_policy"]:
        raise PNGTextualMetadataPolicyError(
            "png_textual_metadata_encoding_policy_mismatch",
            "PNG textual metadata encoding policy does not match chunk",
        )

    canonical_png_bytes = remove_png_textual_metadata_chunks(png_bytes)
    if metadata["canonical_png_hash"] != _hash_bytes(canonical_png_bytes):
        raise PNGTextualMetadataPolicyError(
            "png_textual_metadata_canonical_hash_mismatch",
            "PNG textual metadata canonical PNG hash does not match PNG without metadata chunks",
        )
    sidecar = metadata.get("sidecar")
    if metadata["sidecar_hash"] != _hash_json(sidecar):
        raise PNGTextualMetadataPolicyError(
            "png_textual_metadata_sidecar_hash_mismatch",
            "PNG textual metadata sidecar hash does not match sidecar object",
        )
    return {
        "ok": True,
        "keyword": decoded["keyword"],
        "chunk_type": decoded["chunk_type"],
        "encoding_policy": decoded["encoding_policy"],
        "compressed": decoded["compressed"],
        "metadata": metadata,
        "sidecar": sidecar,
        "canonical_png_bytes": canonical_png_bytes,
        "textual_chunk_count": len(policy_chunks),
    }


def _decode_policy_chunk(chunk: dict) -> dict:
    if chunk["type"] == "tEXt":
        keyword, text_bytes = _split_keyword_payload(
            chunk["data"],
            "png_textual_metadata_text_invalid",
        )
        _require_ascii_text_policy(text_bytes)
        text = text_bytes.decode("latin-1")
        return {
            "keyword": keyword,
            "text": text,
            "chunk_type": "tEXt",
            "compressed": False,
            "encoding_policy": "ascii_json_in_latin1_text_chunk",
        }

    if chunk["type"] == "zTXt":
        keyword, payload = _split_keyword_payload(
            chunk["data"],
            "png_textual_metadata_ztxt_invalid",
        )
        if len(payload) < 1:
            raise PNGTextualMetadataPolicyError(
                "png_textual_metadata_ztxt_invalid",
                "zTXt chunk lacks compression method byte",
            )
        method = payload[0]
        if method != 0:
            raise PNGTextualMetadataPolicyError(
                "png_ztxt_compression_method_unsupported",
                "zTXt compression method must be 0",
            )
        try:
            text_bytes = zlib.decompress(payload[1:])
        except zlib.error as exc:
            raise PNGTextualMetadataPolicyError(
                "png_ztxt_decompression_failed",
                str(exc),
            ) from exc
        _require_ascii_text_policy(text_bytes)
        text = text_bytes.decode("latin-1")
        return {
            "keyword": keyword,
            "text": text,
            "chunk_type": "zTXt",
            "compressed": True,
            "encoding_policy": "ascii_json_in_latin1_ztxt_chunk",
        }

    if chunk["type"] == "iTXt":
        keyword, compressed, text_bytes = _decode_itxt_data(chunk["data"])
        try:
            text = text_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise PNGTextualMetadataPolicyError(
                "png_itxt_utf8_invalid",
                "iTXt text field is not valid UTF-8",
            ) from exc
        return {
            "keyword": keyword,
            "text": text,
            "chunk_type": "iTXt",
            "compressed": compressed,
            "encoding_policy": "utf8_json_in_itxt_chunk",
        }

    raise PNGTextualMetadataPolicyError(
        "png_textual_metadata_chunk_type_unsupported",
        f"unsupported textual metadata chunk type: {chunk['type']}",
    )


def _decode_itxt_data(data: bytes) -> tuple[str, bool, bytes]:
    keyword, payload = _split_keyword_payload(
        data,
        "png_textual_metadata_itxt_invalid",
    )
    if len(payload) < 2:
        raise PNGTextualMetadataPolicyError(
            "png_textual_metadata_itxt_invalid",
            "iTXt chunk lacks compression flag and method",
        )
    compression_flag = payload[0]
    compression_method = payload[1]
    if compression_flag not in (0, 1):
        raise PNGTextualMetadataPolicyError(
            "png_itxt_compression_flag_unsupported",
            "iTXt compression flag must be 0 or 1",
        )
    if compression_method != 0:
        raise PNGTextualMetadataPolicyError(
            "png_itxt_compression_method_unsupported",
            "iTXt compression method must be 0",
        )
    try:
        language_tag, translated_keyword, text_bytes = payload[2:].split(b"\x00", 2)
    except ValueError as exc:
        raise PNGTextualMetadataPolicyError(
            "png_textual_metadata_itxt_invalid",
            "iTXt chunk lacks language or translated keyword separators",
        ) from exc
    try:
        language_tag.decode("ascii")
        translated_keyword.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PNGTextualMetadataPolicyError(
            "png_textual_metadata_itxt_invalid",
            "iTXt language tag or translated keyword encoding is invalid",
        ) from exc
    if compression_flag == 1:
        try:
            text_bytes = zlib.decompress(text_bytes)
        except zlib.error as exc:
            raise PNGTextualMetadataPolicyError(
                "png_itxt_decompression_failed",
                str(exc),
            ) from exc
    return keyword, compression_flag == 1, text_bytes


def _insert_policy_chunk(png_bytes: bytes, chunk_type: str, data: bytes) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    filtered = [chunk for chunk in chunks if not _is_policy_chunk(chunk)]
    return _write_png_chunks([filtered[0], _chunk(chunk_type, data)] + filtered[1:])


def _replace_policy_chunk(png_bytes: bytes, chunk_type: str, data: bytes) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    updated = []
    replaced = False
    for chunk in chunks:
        if _is_policy_chunk(chunk):
            updated.append(_chunk(chunk_type, data))
            replaced = True
        else:
            updated.append(chunk)
    if not replaced:
        raise PNGTextualMetadataPolicyError(
            "png_textual_metadata_chunk_missing",
            "no textual metadata chunk to replace",
        )
    return _write_png_chunks(updated)


def _single_policy_chunk(png_bytes: bytes) -> dict:
    chunks = _read_png_chunks(png_bytes)
    matches = [chunk for chunk in chunks if _is_policy_chunk(chunk)]
    if len(matches) != 1:
        raise PNGTextualMetadataPolicyError(
            "png_textual_metadata_chunk_missing",
            "expected exactly one textual metadata chunk",
        )
    return matches[0]


def _is_policy_chunk(chunk: dict) -> bool:
    if chunk["type"] not in {"tEXt", "zTXt", "iTXt"}:
        return False
    data = chunk["data"]
    if b"\x00" not in data:
        return False
    keyword_bytes = data.split(b"\x00", 1)[0]
    try:
        keyword = keyword_bytes.decode("latin-1")
    except UnicodeDecodeError:
        return False
    return keyword == TEXTUAL_METADATA_KEYWORD


def _encode_metadata_chunk(metadata: dict, policy: dict) -> bytes:
    text = json.dumps(
        metadata,
        separators=(",", ":"),
        sort_keys=True,
        ensure_ascii=policy["ensure_ascii"],
    )
    if policy["chunk_type"] == "tEXt":
        return _text_chunk_data(TEXTUAL_METADATA_KEYWORD, text)
    if policy["chunk_type"] == "zTXt":
        return _ztxt_chunk_data(TEXTUAL_METADATA_KEYWORD, text)
    if policy["chunk_type"] == "iTXt":
        return _itxt_chunk_data(
            TEXTUAL_METADATA_KEYWORD,
            text,
            compressed=policy["compressed"],
        )
    raise ValueError(f"unsupported policy chunk type: {policy['chunk_type']}")


def _text_chunk_data(keyword: str, text: str) -> bytes:
    keyword_bytes = _keyword_bytes(keyword)
    return keyword_bytes + b"\x00" + text.encode("latin-1")


def _ztxt_chunk_data(keyword: str, text: str) -> bytes:
    keyword_bytes = _keyword_bytes(keyword)
    return keyword_bytes + b"\x00\x00" + zlib.compress(text.encode("latin-1"))


def _itxt_chunk_data(keyword: str, text: str, *, compressed: bool) -> bytes:
    keyword_bytes = _keyword_bytes(keyword)
    flag = b"\x01" if compressed else b"\x00"
    method = b"\x00"
    language_tag = b"en-US"
    translated_keyword = b"Mechagotchi sidecar"
    text_bytes = text.encode("utf-8")
    if compressed:
        text_bytes = zlib.compress(text_bytes)
    return (
        keyword_bytes
        + b"\x00"
        + flag
        + method
        + language_tag
        + b"\x00"
        + translated_keyword
        + b"\x00"
        + text_bytes
    )


def _keyword_bytes(keyword: str) -> bytes:
    if "\x00" in keyword:
        raise ValueError("PNG text keyword cannot contain nulls")
    keyword_bytes = keyword.encode("latin-1")
    if not 1 <= len(keyword_bytes) <= 79:
        raise ValueError("PNG text keyword must be 1..79 bytes")
    return keyword_bytes


def _split_keyword_payload(data: bytes, family: str) -> tuple[str, bytes]:
    if b"\x00" not in data:
        raise PNGTextualMetadataPolicyError(
            family,
            "PNG textual metadata chunk lacks keyword separator",
        )
    keyword_bytes, payload = data.split(b"\x00", 1)
    try:
        keyword = keyword_bytes.decode("latin-1")
    except UnicodeDecodeError as exc:
        raise PNGTextualMetadataPolicyError(
            family,
            "PNG textual metadata keyword is not Latin-1",
        ) from exc
    return keyword, payload


def _require_ascii_text_policy(text_bytes: bytes) -> None:
    if any(byte > 0x7F for byte in text_bytes):
        raise PNGTextualMetadataPolicyError(
            "png_textual_metadata_non_ascii_text_policy_violation",
            "tEXt and zTXt metadata JSON must stay ASCII in this policy lab",
        )


def _itxt_prefix_and_text_bytes(data: bytes) -> tuple[bytes, bytes]:
    first_separator = data.index(b"\x00")
    payload_start = first_separator + 1
    after_flags = payload_start + 2
    first_tail_separator = data.index(b"\x00", after_flags)
    second_tail_separator = data.index(b"\x00", first_tail_separator + 1)
    text_start = second_tail_separator + 1
    return data[:text_start], data[text_start:]


def _validate_metadata_shape(metadata: object) -> None:
    if not isinstance(metadata, dict):
        raise PNGTextualMetadataPolicyError(
            "png_textual_metadata_json_invalid",
            "PNG textual metadata root must be an object",
        )
    required = {
        "metadata_model",
        "keyword",
        "variant_id",
        "chunk_type",
        "encoding_policy",
        "compressed",
        "canonical_png_hash",
        "sidecar_hash",
        "sidecar",
    }
    missing = sorted(required - set(metadata))
    if missing:
        raise PNGTextualMetadataPolicyError(
            "png_textual_metadata_json_invalid",
            f"PNG textual metadata is missing required keys: {missing}",
        )
    if metadata["metadata_model"] != METADATA_MODEL:
        raise PNGTextualMetadataPolicyError(
            "png_textual_metadata_model_unsupported",
            "PNG textual metadata model is unsupported",
        )
    if not isinstance(metadata.get("sidecar"), dict):
        raise PNGTextualMetadataPolicyError(
            "png_textual_metadata_json_invalid",
            "PNG textual metadata sidecar must be an object",
        )


def _policy_for_variant(variant_id: str) -> dict:
    for policy in VARIANT_POLICIES:
        if policy["variant_id"] == variant_id:
            return policy
    raise PNGTextualMetadataPolicyError(
        "png_textual_metadata_variant_unsupported",
        f"unsupported textual metadata variant: {variant_id}",
    )


def _metadata_summary(metadata: dict) -> dict:
    return {
        key: metadata[key]
        for key in [
            "metadata_model",
            "keyword",
            "variant_id",
            "chunk_type",
            "encoding_policy",
            "compressed",
            "canonical_png_hash",
            "sidecar_hash",
            "ascii_probe",
            "unicode_probe",
            "hash_note",
        ]
    }


def _compact_textual_import_result(result: dict) -> dict:
    return {
        "ok": result["ok"],
        "textual_metadata_asset": result.get("textual_metadata_asset"),
        "canonical_asset": result.get("canonical_asset"),
        "decoded_png": result.get("decoded_png"),
        "canonical_decoded_png": result.get("canonical_decoded_png"),
        "metadata_policy": result.get("metadata_policy"),
        "validation": result.get("validation"),
        "semantic_fidelity": result.get("semantic_fidelity", 0.0),
        "pixel_fidelity": result.get("pixel_fidelity", 0.0),
        "errors": result.get("errors", []),
        "error_families": result.get("error_families", []),
    }


def _invalid_probe_results_for_report(textual_results: list[dict]) -> list[dict]:
    profile_id = textual_results[0]["profile_id"]
    bundle_variants = {
        result["variant_id"]: bytes.fromhex(result["png_bytes_hex"])
        for result in textual_results
        if result["profile_id"] == profile_id
    }
    probes = [
        (
            "missing_textual_metadata",
            remove_png_textual_metadata_chunks(bundle_variants["text_ascii"]),
        ),
        (
            "duplicate_textual_metadata",
            duplicate_png_textual_metadata_chunk(bundle_variants["text_ascii"]),
        ),
        (
            "non_ascii_text_policy",
            tamper_png_textual_metadata_non_ascii_text_policy(
                bundle_variants["text_ascii"]
            ),
        ),
        (
            "ztxt_method",
            tamper_png_textual_metadata_ztxt_method(bundle_variants["ztxt_ascii"]),
        ),
        (
            "ztxt_stream",
            corrupt_png_textual_metadata_ztxt_stream(bundle_variants["ztxt_ascii"]),
        ),
        (
            "itxt_utf8",
            corrupt_png_textual_metadata_itxt_utf8(bundle_variants["itxt_utf8"]),
        ),
        (
            "canonical_hash",
            corrupt_png_textual_metadata_canonical_hash(
                bundle_variants["itxt_utf8_compressed"]
            ),
        ),
    ]
    return [
        {
            "probe_id": probe_id,
            **_compact_textual_import_result(import_png_textual_metadata(probe_png)),
        }
        for probe_id, probe_png in probes
    ]

def _mean(values) -> float:
    values = list(values)
    if not values:
        return 0.0
    return round(sum(values) / len(values), 6)


def _json_report(report: dict) -> dict:
    payload = deepcopy(report)
    for result in payload["textual_metadata_results"]:
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
                "textual_metadata_roundtrip_count",
                "textual_metadata_roundtrip_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "variant_policies": json_report["variant_policies"],
        "textual_metadata_summaries": [
            {
                "profile_id": result["profile_id"],
                "variant_id": result["variant_id"],
                "chunk_type": result["chunk_type"],
                "encoding_policy": result["encoding_policy"],
                "compressed": result["compressed"],
                "png_file_name": result["png_file_name"],
                "metadata": result["metadata"],
                "decoded_png": result["decoded_png"],
                "metadata_policy": result["metadata_policy"],
                "semantic_fidelity": result["semantic_fidelity"],
                "pixel_fidelity": result["pixel_fidelity"],
            }
            for result in json_report["textual_metadata_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# PNG Textual Metadata Policy Stage 0\n\n"
        "Bounded tEXt, zTXt, and iTXt metadata-carrier policy proof for "
        "Mechagotchi semantic sidecars.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        "- Textual metadata round-trip successes: "
        f"{report['textual_metadata_roundtrip_success_count']}"
        f"/{report['textual_metadata_roundtrip_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        "- Textual metadata round-trip success rate: "
        f"{metrics['textual_metadata_roundtrip_success_rate']}\n"
        f"- Mean semantic fidelity: {metrics['mean_semantic_fidelity']}\n"
        f"- Mean pixel fidelity: {metrics['mean_pixel_fidelity']}\n"
        f"- Decision: {report['decision']}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/workshop_editor/png_textual_metadata_policy_stage0"),
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
    report = run_png_textual_metadata_policy_lab(profile_paths, args.generated_root)
    write_png_textual_metadata_policy_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_PNG_TEXTUAL_METADATA_POLICY = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
