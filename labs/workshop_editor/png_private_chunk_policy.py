import argparse
import json
import sys
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


PRIVATE_METADATA_CHUNK_TYPE = "mgOT"
PRIVATE_METADATA_MAGIC = "mechagotchi.private_chunk.v1"
PRIVATE_METADATA_MODEL = "png_private_chunk_policy_v1"
PRIVATE_CHUNK_POLICY = "ancillary_private_unsafe_to_copy_with_magic_prefix"
REPORT_PATH = Path("data/workshop_editor/png_private_chunk_policy_stage0.json")
DATA_PATH = Path("data/workshop_editor/png_private_chunk_policy_data.js")


class PNGPrivateChunkPolicyError(ValueError):
    def __init__(self, family: str, message: str):
        super().__init__(message)
        self.family = family
        self.message = message


def export_png_private_chunk_bundle(grid: dict, slip_profile: dict) -> dict:
    canonical = export_standard_png_with_sidecar(grid, slip_profile)
    canonical_png_bytes = canonical["png_bytes"]
    sidecar = deepcopy(canonical["sidecar"])
    sidecar["sidecar_id"] = f"{grid['grid_id']}_png_private_chunk_policy_sidecar"
    sidecar["limitations"] = [
        "Stage 0 PNG private chunk proof covers one app-private ancillary metadata chunk type only.",
        "Asset binding hashes the canonical visual PNG without the private chunk to avoid self-referential hashing.",
        "The private chunk is unsafe-to-copy because the metadata is bound to the canonical PNG image data.",
        "Live external editor open-save preservation is not verified by this lab.",
    ]
    metadata = {
        "metadata_model": PRIVATE_METADATA_MODEL,
        "chunk_type": PRIVATE_METADATA_CHUNK_TYPE,
        "chunk_type_properties": _chunk_type_properties(PRIVATE_METADATA_CHUNK_TYPE),
        "magic": PRIVATE_METADATA_MAGIC,
        "private_chunk_policy": PRIVATE_CHUNK_POLICY,
        "canonical_png_hash": _hash_bytes(canonical_png_bytes),
        "sidecar_hash": _hash_json(sidecar),
        "sidecar": sidecar,
        "hash_note": "canonical_png_hash excludes Mechagotchi private metadata chunks",
        "copy_note": "unsafe-to-copy private chunk because metadata is bound to image bytes",
    }
    png_bytes = _insert_private_chunk(canonical_png_bytes, _encode_private_chunk_data(metadata))
    return {
        "canonical_png_bytes": canonical_png_bytes,
        "png_bytes": png_bytes,
        "canonical_asset": canonical["asset"],
        "private_chunk_asset": _asset_from_png_bytes(
            png_bytes,
            asset_id=f"{grid['grid_id']}.private-chunk.png",
            uri=f"generated://workshop/png-private-chunk-policy/{grid['grid_id']}.png",
        ),
        "sidecar": sidecar,
        "metadata": _metadata_summary(metadata),
    }


def import_png_private_chunk(
    png_bytes: bytes,
    source_grid: dict | None = None,
) -> dict:
    try:
        private_decoded = decode_png_rgba(png_bytes)
        extracted = _extract_private_chunk(png_bytes)
        canonical_decoded = decode_png_rgba(extracted["canonical_png_bytes"])
    except PNGDecodeError as exc:
        return _failed_import("png", exc.family, exc.message)
    except (PNGEmbeddedSidecarError, PNGPrivateChunkPolicyError) as exc:
        return _failed_import("png.private_chunk", exc.family, exc.message)

    if private_decoded["pixels"] != canonical_decoded["pixels"]:
        return _failed_import(
            "png.pixels",
            "png_private_chunk_pixel_mismatch",
            "PNG pixels differ after private chunk removal",
        )

    imported = import_standard_png_with_sidecar(
        extracted["canonical_png_bytes"],
        extracted["sidecar"],
    )
    if not imported["ok"]:
        result = _compact_import_result(imported)
        result["private_chunk_policy"] = {"ok": False, "errors": imported["errors"]}
        return result

    restored = imported["restored_grid"]
    semantic_source = source_grid or restored
    diff = compare_semantic_grid_fidelity(semantic_source, restored)
    grid_validation = validate_grid(restored)
    profile = extracted["sidecar"]["slip_binding"]["profile_snapshot"]
    alignment = is_grid_aligned(restored, profile)
    properties = extracted["metadata"]["chunk_type_properties"]
    return {
        "ok": grid_validation.ok and alignment.ok,
        "private_chunk_asset": _asset_from_png_bytes(
            png_bytes,
            asset_id=extracted["sidecar"]["asset_binding"]["asset_id"].replace(
                ".png", ".private-chunk.png"
            ),
            uri=extracted["sidecar"]["asset_binding"]["uri"].replace(
                "standard-image", "png-private-chunk-policy"
            ),
        ),
        "canonical_asset": imported["asset"],
        "decoded_png": _decoded_summary(private_decoded),
        "canonical_decoded_png": _decoded_summary(canonical_decoded),
        "private_chunk_policy": {
            "ok": True,
            "chunk_type": extracted["chunk_type"],
            "magic": extracted["metadata"]["magic"],
            "private_chunk_policy": extracted["metadata"]["private_chunk_policy"],
            "ancillary": properties["ancillary"],
            "private": properties["private"],
            "reserved_bit_valid": properties["reserved_bit_valid"],
            "safe_to_copy": properties["safe_to_copy"],
            "private_chunk_count": extracted["private_chunk_count"],
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


def remove_png_private_chunks(png_bytes: bytes) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    return _write_png_chunks(
        [chunk for chunk in chunks if not _is_private_chunk_candidate(chunk)]
    )


def duplicate_png_private_chunk(png_bytes: bytes) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    updated = []
    duplicated = False
    for chunk in chunks:
        updated.append(chunk)
        if _is_private_chunk_candidate(chunk) and not duplicated:
            updated.append(deepcopy(chunk))
            duplicated = True
    if not duplicated:
        raise PNGPrivateChunkPolicyError(
            "png_private_chunk_missing",
            "no private metadata chunk to duplicate",
        )
    return _write_png_chunks(updated)


def tamper_png_private_chunk_safe_to_copy_type(png_bytes: bytes) -> bytes:
    chunk = _single_private_chunk(png_bytes)
    return _replace_private_chunk(png_bytes, "mgOt", chunk["data"])


def tamper_png_private_chunk_magic(png_bytes: bytes) -> bytes:
    metadata = _extract_private_chunk(png_bytes)["metadata"]
    data = b"not.mechagotchi.private\x00" + json.dumps(
        metadata,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return _replace_private_chunk(png_bytes, PRIVATE_METADATA_CHUNK_TYPE, data)


def corrupt_png_private_chunk_json(png_bytes: bytes) -> bytes:
    data = PRIVATE_METADATA_MAGIC.encode("ascii") + b"\x00{not-json"
    return _replace_private_chunk(png_bytes, PRIVATE_METADATA_CHUNK_TYPE, data)


def tamper_png_private_chunk_canonical_hash(png_bytes: bytes) -> bytes:
    extracted = _extract_private_chunk(png_bytes)
    metadata = deepcopy(extracted["metadata"])
    metadata["canonical_png_hash"] = "sha256:not-the-canonical-png"
    return _replace_private_chunk(
        png_bytes,
        PRIVATE_METADATA_CHUNK_TYPE,
        _encode_private_chunk_data(metadata),
    )


def tamper_png_private_chunk_sidecar_hash(png_bytes: bytes) -> bytes:
    extracted = _extract_private_chunk(png_bytes)
    metadata = deepcopy(extracted["metadata"])
    metadata["sidecar_hash"] = "sha256:not-the-sidecar"
    return _replace_private_chunk(
        png_bytes,
        PRIVATE_METADATA_CHUNK_TYPE,
        _encode_private_chunk_data(metadata),
    )


def run_png_private_chunk_policy_lab(
    profile_paths: list[Path],
    generated_root: Path,
) -> dict:
    private_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        bundle = export_png_private_chunk_bundle(grid, profile)
        imported = import_png_private_chunk(bundle["png_bytes"], source_grid=grid)
        private_results.append(
            {
                "profile_id": profile["profile_id"],
                "profile_path": _portable(profile_path),
                "grid_path": _portable(grid_path),
                "png_file_name": f"{profile['profile_id']}_private_chunk.png",
                "png_bytes_hex": bundle["png_bytes"].hex(),
                "png_byte_count": len(bundle["png_bytes"]),
                "canonical_png_byte_count": len(bundle["canonical_png_bytes"]),
                "private_chunk_asset": bundle["private_chunk_asset"],
                "canonical_asset": bundle["canonical_asset"],
                "metadata": bundle["metadata"],
                "decoded_png": imported.get("decoded_png"),
                "canonical_decoded_png": imported.get("canonical_decoded_png"),
                "private_chunk_policy": imported.get("private_chunk_policy"),
                "import_result": _compact_private_import_result(imported),
                "semantic_fidelity": imported.get("semantic_fidelity", 0.0),
                "pixel_fidelity": imported.get("pixel_fidelity", 0.0),
                "ok": imported["ok"],
            }
        )

    invalid_probe_results = _invalid_probe_results(private_results[0])
    roundtrip_count = len(private_results)
    roundtrip_success_count = sum(1 for result in private_results if result["ok"])
    invalid_probe_count = len(invalid_probe_results)
    invalid_probe_rejected_count = sum(
        1 for result in invalid_probe_results if not result["ok"]
    )
    return {
        "artifact_id": "png_private_chunk_policy_stage0",
        "status": "research_png_private_chunk_policy_no_package_code",
        "profile_count": len(profile_paths),
        "private_chunk_roundtrip_count": roundtrip_count,
        "private_chunk_roundtrip_success_count": roundtrip_success_count,
        "invalid_probe_count": invalid_probe_count,
        "invalid_probe_rejected_count": invalid_probe_rejected_count,
        "chunk_type": PRIVATE_METADATA_CHUNK_TYPE,
        "chunk_type_properties": _chunk_type_properties(PRIVATE_METADATA_CHUNK_TYPE),
        "private_chunk_results": private_results,
        "invalid_probe_results": invalid_probe_results,
        "carrier_selection_inputs": _carrier_selection_inputs(),
        "metrics": {
            "private_chunk_roundtrip_success_rate": _ratio(
                roundtrip_success_count, roundtrip_count
            ),
            "mean_semantic_fidelity": _mean(
                result["semantic_fidelity"] for result in private_results
            ),
            "mean_pixel_fidelity": _mean(
                result["pixel_fidelity"] for result in private_results
            ),
            "invalid_probe_rejection_rate": _ratio(
                invalid_probe_rejected_count, invalid_probe_count
            ),
        },
        "closed_states": [
            "png_private_chunk_type_bits_policy",
            "png_private_chunk_magic_prefix_policy",
            "png_private_chunk_hash_validation",
            "png_private_chunk_invalid_probe_rejection",
            "png_metadata_carrier_selection_inputs",
        ],
        "blocked_states": [
            "production_import_export_carrier_selection_final_decision",
            "live_external_editor_rewrite_validation",
            "Adam7/APNG/full PNG conformance",
            "private_chunk_editor_preservation_matrix",
            "package_runtime_lifecycle_integration",
            "manual readability calibration",
            "profile_weighted_evolution",
        ],
        "external_sources": [
            {
                "name": "W3C Portable Network Graphics (PNG) Specification, Third Edition",
                "url": "https://www.w3.org/TR/png-3/",
                "used_for": "private chunk naming, safe-to-copy bit policy, and private chunk identifying data guidance",
            }
        ],
        "decision": "prototype_png_private_chunk_policy",
        "next_research_step": (
            "Collect live editor preservation fixtures before using private "
            "chunks as a production import/export carrier."
        ),
    }


def write_png_private_chunk_policy_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "png_private_chunk_policy_stage0.json", _json_report(report))
    for result in report["private_chunk_results"]:
        (output_dir / result["png_file_name"]).write_bytes(
            bytes.fromhex(result["png_bytes_hex"])
        )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "png_private_chunk_policy_data.js").write_text(
        "window.MECHAGOTCHI_PNG_PRIVATE_CHUNK_POLICY = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _extract_private_chunk(png_bytes: bytes) -> dict:
    chunks = _read_png_chunks(png_bytes)
    candidates = [chunk for chunk in chunks if _is_private_chunk_candidate(chunk)]
    if not candidates:
        raise PNGPrivateChunkPolicyError(
            "png_private_chunk_missing",
            "PNG does not contain a Mechagotchi private metadata chunk",
        )
    if len(candidates) > 1:
        raise PNGPrivateChunkPolicyError(
            "png_private_chunk_duplicate",
            "PNG contains more than one Mechagotchi private metadata chunk",
        )
    chunk = candidates[0]
    _validate_chunk_type_policy(chunk["type"])
    metadata = _decode_private_chunk_data(chunk["data"])
    _validate_metadata_shape(metadata)

    canonical_png_bytes = remove_png_private_chunks(png_bytes)
    if metadata["canonical_png_hash"] != _hash_bytes(canonical_png_bytes):
        raise PNGPrivateChunkPolicyError(
            "png_private_chunk_canonical_hash_mismatch",
            "PNG private chunk canonical PNG hash does not match PNG without private metadata chunks",
        )
    sidecar = metadata["sidecar"]
    if metadata["sidecar_hash"] != _hash_json(sidecar):
        raise PNGPrivateChunkPolicyError(
            "png_private_chunk_sidecar_hash_mismatch",
            "PNG private chunk sidecar hash does not match sidecar object",
        )
    return {
        "ok": True,
        "chunk_type": chunk["type"],
        "metadata": metadata,
        "sidecar": sidecar,
        "canonical_png_bytes": canonical_png_bytes,
        "private_chunk_count": len(candidates),
    }


def _insert_private_chunk(png_bytes: bytes, data: bytes) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    filtered = [chunk for chunk in chunks if not _is_private_chunk_candidate(chunk)]
    return _write_png_chunks(
        [filtered[0], _chunk(PRIVATE_METADATA_CHUNK_TYPE, data)] + filtered[1:]
    )


def _replace_private_chunk(png_bytes: bytes, chunk_type: str, data: bytes) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    updated = []
    replaced = False
    for chunk in chunks:
        if _is_private_chunk_candidate(chunk):
            updated.append(_chunk(chunk_type, data))
            replaced = True
        else:
            updated.append(chunk)
    if not replaced:
        raise PNGPrivateChunkPolicyError(
            "png_private_chunk_missing",
            "no private metadata chunk to replace",
        )
    return _write_png_chunks(updated)


def _single_private_chunk(png_bytes: bytes) -> dict:
    chunks = _read_png_chunks(png_bytes)
    matches = [chunk for chunk in chunks if _is_private_chunk_candidate(chunk)]
    if len(matches) != 1:
        raise PNGPrivateChunkPolicyError(
            "png_private_chunk_missing",
            "expected exactly one private metadata chunk",
        )
    return matches[0]


def _is_private_chunk_candidate(chunk: dict) -> bool:
    return chunk["type"] == PRIVATE_METADATA_CHUNK_TYPE or chunk["data"].startswith(
        PRIVATE_METADATA_MAGIC.encode("ascii") + b"\x00"
    )


def _encode_private_chunk_data(metadata: dict) -> bytes:
    return (
        PRIVATE_METADATA_MAGIC.encode("ascii")
        + b"\x00"
        + json.dumps(metadata, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


def _decode_private_chunk_data(data: bytes) -> dict:
    prefix = PRIVATE_METADATA_MAGIC.encode("ascii") + b"\x00"
    if not data.startswith(prefix):
        raise PNGPrivateChunkPolicyError(
            "png_private_chunk_magic_mismatch",
            "PNG private chunk payload does not start with the Mechagotchi magic prefix",
        )
    try:
        metadata = json.loads(data[len(prefix) :].decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise PNGPrivateChunkPolicyError(
            "png_private_chunk_utf8_invalid",
            "PNG private chunk JSON payload is not valid UTF-8",
        ) from exc
    except json.JSONDecodeError as exc:
        raise PNGPrivateChunkPolicyError(
            "png_private_chunk_json_invalid",
            f"PNG private chunk JSON payload is invalid: {exc}",
        ) from exc
    return metadata


def _validate_metadata_shape(metadata: object) -> None:
    if not isinstance(metadata, dict):
        raise PNGPrivateChunkPolicyError(
            "png_private_chunk_json_invalid",
            "PNG private chunk metadata root must be an object",
        )
    required = {
        "metadata_model",
        "chunk_type",
        "chunk_type_properties",
        "magic",
        "private_chunk_policy",
        "canonical_png_hash",
        "sidecar_hash",
        "sidecar",
    }
    missing = sorted(required - set(metadata))
    if missing:
        raise PNGPrivateChunkPolicyError(
            "png_private_chunk_json_invalid",
            f"PNG private chunk metadata is missing required keys: {missing}",
        )
    if metadata["metadata_model"] != PRIVATE_METADATA_MODEL:
        raise PNGPrivateChunkPolicyError(
            "png_private_chunk_model_unsupported",
            "PNG private chunk metadata model is unsupported",
        )
    if metadata["chunk_type"] != PRIVATE_METADATA_CHUNK_TYPE:
        raise PNGPrivateChunkPolicyError(
            "png_private_chunk_type_policy_violation",
            "PNG private chunk metadata names an unsupported chunk type",
        )
    if metadata["magic"] != PRIVATE_METADATA_MAGIC:
        raise PNGPrivateChunkPolicyError(
            "png_private_chunk_magic_mismatch",
            "PNG private chunk metadata magic does not match policy",
        )
    if metadata["private_chunk_policy"] != PRIVATE_CHUNK_POLICY:
        raise PNGPrivateChunkPolicyError(
            "png_private_chunk_policy_mismatch",
            "PNG private chunk policy marker does not match expected policy",
        )
    if not isinstance(metadata["sidecar"], dict):
        raise PNGPrivateChunkPolicyError(
            "png_private_chunk_json_invalid",
            "PNG private chunk sidecar must be an object",
        )
    if metadata["chunk_type_properties"] != _chunk_type_properties(PRIVATE_METADATA_CHUNK_TYPE):
        raise PNGPrivateChunkPolicyError(
            "png_private_chunk_type_policy_violation",
            "PNG private chunk type properties do not match policy",
        )


def _validate_chunk_type_policy(chunk_type: str) -> None:
    if chunk_type != PRIVATE_METADATA_CHUNK_TYPE:
        raise PNGPrivateChunkPolicyError(
            "png_private_chunk_type_policy_violation",
            "PNG private metadata chunk type does not match the Stage 0 policy",
        )
    properties = _chunk_type_properties(chunk_type)
    if not (
        properties["ancillary"]
        and properties["private"]
        and properties["reserved_bit_valid"]
        and not properties["safe_to_copy"]
    ):
        raise PNGPrivateChunkPolicyError(
            "png_private_chunk_type_policy_violation",
            "PNG private metadata chunk must be ancillary, private, reserved-bit-valid, and unsafe-to-copy",
        )


def _chunk_type_properties(chunk_type: str) -> dict:
    if len(chunk_type) != 4 or not chunk_type.isalpha() or not chunk_type.isascii():
        raise PNGPrivateChunkPolicyError(
            "png_private_chunk_type_invalid",
            "PNG chunk type must contain four ASCII letters",
        )
    return {
        "ancillary": chunk_type[0].islower(),
        "private": chunk_type[1].islower(),
        "reserved_bit_valid": chunk_type[2].isupper(),
        "safe_to_copy": chunk_type[3].islower(),
    }


def _metadata_summary(metadata: dict) -> dict:
    return {
        key: metadata[key]
        for key in [
            "metadata_model",
            "chunk_type",
            "chunk_type_properties",
            "magic",
            "private_chunk_policy",
            "canonical_png_hash",
            "sidecar_hash",
            "hash_note",
            "copy_note",
        ]
    }


def _invalid_probe_results(reference_result: dict) -> list[dict]:
    png_bytes = bytes.fromhex(reference_result["png_bytes_hex"])
    probes = [
        ("missing_private_chunk", remove_png_private_chunks(png_bytes)),
        ("duplicate_private_chunk", duplicate_png_private_chunk(png_bytes)),
        ("safe_to_copy_type", tamper_png_private_chunk_safe_to_copy_type(png_bytes)),
        ("magic_mismatch", tamper_png_private_chunk_magic(png_bytes)),
        ("invalid_json", corrupt_png_private_chunk_json(png_bytes)),
        ("canonical_hash", tamper_png_private_chunk_canonical_hash(png_bytes)),
        ("sidecar_hash", tamper_png_private_chunk_sidecar_hash(png_bytes)),
    ]
    return [
        {
            "probe_id": probe_id,
            **_compact_private_import_result(import_png_private_chunk(probe_png)),
        }
        for probe_id, probe_png in probes
    ]


def _carrier_selection_inputs() -> dict:
    return {
        "external_sidecar": {
            "current_status": "proven_stage0_strategy",
            "strength": "highest compatibility with editors that strip unknown PNG metadata",
            "risk": "metadata can be separated from the visual asset",
        },
        "textual_png_chunks": {
            "current_status": "proven_stage0_text_ztxt_itxt_policy",
            "strength": "standard textual metadata carriers with UTF-8 path through iTXt",
            "risk": "editor preservation still unmeasured",
        },
        "private_png_chunk": {
            "current_status": "proven_stage0_private_chunk_policy",
            "strength": "application-native binary metadata carrier with explicit magic prefix",
            "risk": "spec guidance says text-specific metadata should not be stored only in private chunks; editor preservation still unmeasured",
        },
        "provisional_recommendation": "textual_or_external_sidecar_preferred_until_editor_fixtures",
        "final_decision_blocked_by": [
            "live_external_editor_rewrite_validation",
            "production_import_export_carrier_selection_final_decision",
        ],
    }


def _compact_private_import_result(result: dict) -> dict:
    return {
        "ok": result["ok"],
        "private_chunk_asset": result.get("private_chunk_asset"),
        "canonical_asset": result.get("canonical_asset"),
        "decoded_png": result.get("decoded_png"),
        "canonical_decoded_png": result.get("canonical_decoded_png"),
        "private_chunk_policy": result.get("private_chunk_policy"),
        "validation": result.get("validation"),
        "semantic_fidelity": result.get("semantic_fidelity", 0.0),
        "pixel_fidelity": result.get("pixel_fidelity", 0.0),
        "errors": result.get("errors", []),
        "error_families": result.get("error_families", []),
    }


def _mean(values) -> float:
    values = list(values)
    if not values:
        return 0.0
    return round(sum(values) / len(values), 6)


def _json_report(report: dict) -> dict:
    payload = deepcopy(report)
    for result in payload["private_chunk_results"]:
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
                "private_chunk_roundtrip_count",
                "private_chunk_roundtrip_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "chunk_type": json_report["chunk_type"],
        "chunk_type_properties": json_report["chunk_type_properties"],
        "carrier_selection_inputs": json_report["carrier_selection_inputs"],
        "private_chunk_summaries": [
            {
                "profile_id": result["profile_id"],
                "png_file_name": result["png_file_name"],
                "private_chunk_asset": result["private_chunk_asset"],
                "canonical_asset": result["canonical_asset"],
                "metadata": result["metadata"],
                "decoded_png": result["decoded_png"],
                "private_chunk_policy": result["private_chunk_policy"],
                "semantic_fidelity": result["semantic_fidelity"],
                "pixel_fidelity": result["pixel_fidelity"],
            }
            for result in json_report["private_chunk_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# PNG Private Chunk Policy Stage 0\n\n"
        "Bounded app-private PNG ancillary chunk policy proof for Mechagotchi "
        "semantic sidecars.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Private chunk round-trip successes: {report['private_chunk_roundtrip_success_count']}"
        f"/{report['private_chunk_roundtrip_count']}\n"
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
        default=Path("data/workshop_editor/png_private_chunk_policy_stage0"),
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
    report = run_png_private_chunk_policy_lab(profile_paths, args.generated_root)
    write_png_private_chunk_policy_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_PNG_PRIVATE_CHUNK_POLICY = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
