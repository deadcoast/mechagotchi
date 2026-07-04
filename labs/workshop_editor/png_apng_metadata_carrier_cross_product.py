import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME_DIR = ROOT / "labs" / "grid_genome"
if str(GRID_GENOME_DIR) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME_DIR))

from png_apng_sidecar_decoder import (
    APNGDecodeError,
    decode_apng_frames,
    export_apng_with_sidecar,
    import_apng_with_sidecar,
    tamper_apng_sequence_number,
    _asset_from_apng_bytes,
    _compact_apng_import_result,
    _decoded_apng_summary,
)
from png_embedded_sidecar_writer import (
    _failed_import,
    _hash_bytes,
    _hash_json,
    _portable,
    _ratio,
    _read_json,
    _read_png_chunks,
    _write_json,
)
from png_private_chunk_policy import (
    PRIVATE_METADATA_CHUNK_TYPE,
    PRIVATE_METADATA_MAGIC,
    PRIVATE_METADATA_MODEL,
    PRIVATE_CHUNK_POLICY,
    PNGPrivateChunkPolicyError,
    _chunk_type_properties,
    _encode_private_chunk_data,
    _extract_private_chunk,
    _insert_private_chunk,
    remove_png_private_chunks,
    tamper_png_private_chunk_canonical_hash,
)
from png_textual_metadata_policy import (
    ASCII_PROBE,
    METADATA_MODEL as TEXTUAL_METADATA_MODEL,
    TEXTUAL_METADATA_KEYWORD,
    UNICODE_PROBE,
    VARIANT_POLICIES as TEXTUAL_VARIANT_POLICIES,
    PNGTextualMetadataPolicyError,
    _encode_metadata_chunk,
    _extract_textual_metadata,
    _insert_policy_chunk,
    corrupt_png_textual_metadata_ztxt_stream,
    duplicate_png_textual_metadata_chunk,
    remove_png_textual_metadata_chunks,
)


REPORT_PATH = ROOT / "data/workshop_editor/apng_metadata_carrier_cross_product_stage0.json"
DATA_PATH = ROOT / "data/workshop_editor/apng_metadata_carrier_cross_product_data.js"
METADATA_CARRIER_MODEL = "apng_metadata_carrier_cross_product_v1"


APNG_METADATA_CARRIER_POLICIES = [
    {
        "variant_id": policy["variant_id"],
        "carrier_family": "textual",
        "chunk_type": policy["chunk_type"],
        "compressed": policy["compressed"],
        "encoding_policy": policy["encoding_policy"],
    }
    for policy in TEXTUAL_VARIANT_POLICIES
] + [
    {
        "variant_id": "private_mgot",
        "carrier_family": "private",
        "chunk_type": PRIVATE_METADATA_CHUNK_TYPE,
        "compressed": False,
        "encoding_policy": "magic_prefixed_utf8_json_private_chunk",
    }
]


def export_apng_metadata_carrier_bundle(grid: dict, slip_profile: dict) -> dict:
    canonical = export_apng_with_sidecar(grid, slip_profile)
    canonical_apng_bytes = canonical["png_bytes"]
    sidecar = deepcopy(canonical["sidecar"])
    sidecar["sidecar_id"] = f"{grid['grid_id']}_apng_metadata_carrier_sidecar"
    sidecar["limitations"] = [
        "Stage 0 APNG metadata-carrier proof stores sidecar JSON in APNG textual or private PNG chunks.",
        "Asset binding hashes canonical APNG bytes with Mechagotchi carrier chunks removed.",
        "This proof inherits the bounded two-frame full-canvas 8-bit RGBA APNG decoder limits.",
        "Live external editor open-save preservation is not verified by this lab.",
    ]
    metadata_base = {
        "carrier_model": METADATA_CARRIER_MODEL,
        "canonical_png_hash": _hash_bytes(canonical_apng_bytes),
        "sidecar_hash": _hash_json(sidecar),
        "sidecar": sidecar,
        "hash_note": "canonical_png_hash names APNG bytes with Mechagotchi carrier chunks removed",
    }
    variants = []
    for policy in TEXTUAL_VARIANT_POLICIES:
        variants.append(
            _build_textual_variant(
                canonical_apng_bytes,
                metadata_base,
                policy,
                grid,
                slip_profile,
            )
        )
    variants.append(
        _build_private_variant(
            canonical_apng_bytes,
            metadata_base,
            grid,
            slip_profile,
        )
    )
    return {
        "canonical_apng_bytes": canonical_apng_bytes,
        "canonical_asset": canonical["asset"],
        "canonical_decoded_apng": canonical["decoded_apng"],
        "sidecar": sidecar,
        "metadata": {
            "carrier_model": METADATA_CARRIER_MODEL,
            "canonical_apng_hash": metadata_base["canonical_png_hash"],
            "sidecar_hash": metadata_base["sidecar_hash"],
            "variant_ids": [variant["variant_id"] for variant in variants],
        },
        "variants": variants,
    }


def import_apng_metadata_carrier(
    png_bytes: bytes,
    source_grid: dict | None = None,
) -> dict:
    try:
        embedded_decoded = decode_apng_frames(png_bytes)
        extracted = _extract_metadata_carrier(png_bytes)
        canonical_decoded = decode_apng_frames(extracted["canonical_png_bytes"])
    except APNGDecodeError as exc:
        return _failed_import("apng", exc.family, exc.message)
    except (PNGTextualMetadataPolicyError, PNGPrivateChunkPolicyError) as exc:
        return _failed_import("apng.metadata_carrier", exc.family, exc.message)

    embedded_frame_hashes = [frame["pixel_hash"] for frame in embedded_decoded["frames"]]
    canonical_frame_hashes = [frame["pixel_hash"] for frame in canonical_decoded["frames"]]
    if embedded_frame_hashes != canonical_frame_hashes:
        return _failed_import(
            "apng.frames",
            "apng_metadata_carrier_frame_hash_mismatch",
            "APNG frame hashes differ after metadata carrier removal",
        )

    imported = import_apng_with_sidecar(
        extracted["canonical_png_bytes"],
        extracted["sidecar"],
        source_grid=source_grid,
    )
    if not imported["ok"]:
        result = _compact_apng_import_result(imported)
        result["metadata_carrier_policy"] = {
            "ok": False,
            "carrier_family": extracted["carrier_family"],
            "variant_id": extracted["metadata"].get("variant_id"),
            "errors": imported["errors"],
        }
        return result

    metadata_carrier_asset = _asset_from_apng_bytes(
        png_bytes,
        asset_id=extracted["sidecar"]["asset_binding"]["asset_id"].replace(
            ".apng.png", f".{extracted['variant_id']}.apng.png"
        ),
        uri=extracted["sidecar"]["asset_binding"]["uri"].replace(
            "apng-sidecar-decoder", "apng-metadata-carrier-cross-product"
        ),
    )
    return {
        "ok": True,
        "asset": metadata_carrier_asset,
        "metadata_carrier_asset": metadata_carrier_asset,
        "canonical_asset": imported["asset"],
        "decoded_apng": _decoded_apng_summary(embedded_decoded),
        "canonical_decoded_apng": _decoded_apng_summary(canonical_decoded),
        "metadata_carrier_policy": _carrier_policy_summary(extracted),
        "sidecar": extracted["sidecar"],
        "validation": imported["validation"],
        "apng_policy": imported["apng_policy"],
        "restored_grid": imported["restored_grid"],
        "restored_grid_validation": imported["restored_grid_validation"],
        "semantic_diff": imported["semantic_diff"],
        "semantic_fidelity": imported["semantic_fidelity"],
        "frame_pixel_fidelity": 1.0,
        "errors": [],
        "error_families": [],
    }


def run_apng_metadata_carrier_cross_product_lab(
    profile_paths: list[Path],
    generated_root: Path,
) -> dict:
    carrier_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        bundle = export_apng_metadata_carrier_bundle(grid, profile)
        for variant in bundle["variants"]:
            imported = import_apng_metadata_carrier(
                variant["png_bytes"],
                source_grid=grid,
            )
            carrier_results.append(
                {
                    "profile_id": profile["profile_id"],
                    "profile_path": _portable(profile_path),
                    "grid_path": _portable(grid_path),
                    "variant_id": variant["variant_id"],
                    "carrier_family": variant["carrier_family"],
                    "chunk_type": variant["chunk_type"],
                    "encoding_policy": variant["encoding_policy"],
                    "compressed": variant["compressed"],
                    "png_file_name": variant["png_file_name"],
                    "png_bytes_hex": variant["png_bytes"].hex(),
                    "png_byte_count": len(variant["png_bytes"]),
                    "canonical_apng_byte_count": len(variant["canonical_apng_bytes"]),
                    "metadata": _metadata_summary(variant["metadata"]),
                    "decoded_apng": imported.get("decoded_apng"),
                    "canonical_decoded_apng": imported.get("canonical_decoded_apng"),
                    "metadata_carrier_policy": imported.get("metadata_carrier_policy"),
                    "import_result": _compact_apng_import_result(imported),
                    "semantic_fidelity": imported.get("semantic_fidelity", 0.0),
                    "frame_pixel_fidelity": imported.get("frame_pixel_fidelity", 0.0),
                    "ok": imported["ok"],
                }
            )

    invalid_probe_results = _invalid_probe_results(carrier_results[0:5])
    roundtrip_count = len(carrier_results)
    roundtrip_success_count = sum(1 for result in carrier_results if result["ok"])
    invalid_probe_count = len(invalid_probe_results)
    invalid_probe_rejected_count = sum(
        1 for result in invalid_probe_results if not result["ok"]
    )
    return {
        "artifact_id": "apng_metadata_carrier_cross_product_stage0",
        "status": "research_apng_metadata_carrier_cross_product_no_package_code",
        "date": "2026-05-14",
        "purpose": (
            "Prove that bounded APNG sidecar semantics can round-trip through "
            "existing PNG textual and private metadata carrier policies without "
            "claiming full APNG/PNG conformance."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "labs/workshop_editor/png_apng_sidecar_decoder.py",
            "labs/workshop_editor/png_textual_metadata_policy.py",
            "labs/workshop_editor/png_private_chunk_policy.py",
            "data/slips/multi_profile_generation_stage0/",
        ],
        "external_sources": [
            {
                "name": "W3C Portable Network Graphics (PNG) Specification, Third Edition",
                "url": "https://www.w3.org/TR/png-3/",
                "used_for": "APNG chunk order, textual chunks, private chunks, and safe-to-copy carrier policy anchors.",
            }
        ],
        "profile_count": len(profile_paths),
        "metadata_carrier_roundtrip_count": roundtrip_count,
        "metadata_carrier_roundtrip_success_count": roundtrip_success_count,
        "invalid_probe_count": invalid_probe_count,
        "invalid_probe_rejected_count": invalid_probe_rejected_count,
        "carrier_policies": APNG_METADATA_CARRIER_POLICIES,
        "metadata_carrier_results": carrier_results,
        "invalid_probe_results": invalid_probe_results,
        "metrics": {
            "metadata_carrier_roundtrip_success_rate": _ratio(
                roundtrip_success_count,
                roundtrip_count,
            ),
            "mean_semantic_fidelity": _mean(
                result["semantic_fidelity"] for result in carrier_results
            ),
            "mean_frame_pixel_fidelity": _mean(
                result["frame_pixel_fidelity"] for result in carrier_results
            ),
            "invalid_probe_rejection_rate": _ratio(
                invalid_probe_rejected_count,
                invalid_probe_count,
            ),
        },
        "closed_states": [
            "apng_textual_metadata_carrier_cross_product",
            "apng_private_metadata_carrier_cross_product",
            "apng_metadata_canonical_hash_validation",
            "apng_metadata_frame_hash_preservation",
            "apng_metadata_invalid_probe_rejection",
        ],
        "blocked_states": [
            "full_apng_png_conformance",
            "partial_frame_blend_over_disposal_variants",
            "live_external_editor_rewrite_validation",
            "final_png_production_carrier_selection",
            "package_runtime_lifecycle_integration",
            "manual_readability_calibration",
            "profile_weighted_evolution",
        ],
        "decision": "prototype_bounded_apng_metadata_carrier_cross_product",
        "next_research_step": (
            "Keep full APNG/PNG conformance, partial-frame APNG playback, live "
            "external editor validation, and final PNG carrier selection blocked "
            "until direct fixtures exist."
        ),
    }


def write_apng_metadata_carrier_cross_product_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(
        output_dir / "apng_metadata_carrier_cross_product_stage0.json",
        _json_report(report),
    )
    for result in report["metadata_carrier_results"]:
        (output_dir / result["png_file_name"]).write_bytes(
            bytes.fromhex(result["png_bytes_hex"])
        )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "apng_metadata_carrier_cross_product_data.js").write_text(
        "window.MECHAGOTCHI_APNG_METADATA_CARRIER_CROSS_PRODUCT = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _build_textual_variant(
    canonical_apng_bytes: bytes,
    metadata_base: dict,
    policy: dict,
    grid: dict,
    slip_profile: dict,
) -> dict:
    metadata = deepcopy(metadata_base)
    metadata.update(
        {
            "metadata_model": TEXTUAL_METADATA_MODEL,
            "keyword": TEXTUAL_METADATA_KEYWORD,
            "variant_id": policy["variant_id"],
            "chunk_type": policy["chunk_type"],
            "encoding_policy": policy["encoding_policy"],
            "compressed": policy["compressed"],
            "ascii_probe": ASCII_PROBE,
            "unicode_probe": UNICODE_PROBE,
        }
    )
    png_bytes = _insert_policy_chunk(
        canonical_apng_bytes,
        policy["chunk_type"],
        _encode_metadata_chunk(metadata, policy),
    )
    return {
        "variant_id": policy["variant_id"],
        "carrier_family": "textual",
        "chunk_type": policy["chunk_type"],
        "compressed": policy["compressed"],
        "encoding_policy": policy["encoding_policy"],
        "png_bytes": png_bytes,
        "canonical_apng_bytes": canonical_apng_bytes,
        "metadata": metadata,
        "png_file_name": f"{slip_profile['profile_id']}_{policy['variant_id']}_apng_carrier.png",
        "grid_id": grid["grid_id"],
        "profile_id": slip_profile["profile_id"],
    }


def _build_private_variant(
    canonical_apng_bytes: bytes,
    metadata_base: dict,
    grid: dict,
    slip_profile: dict,
) -> dict:
    metadata = deepcopy(metadata_base)
    metadata.update(
        {
            "metadata_model": PRIVATE_METADATA_MODEL,
            "chunk_type": PRIVATE_METADATA_CHUNK_TYPE,
            "chunk_type_properties": _chunk_type_properties(PRIVATE_METADATA_CHUNK_TYPE),
            "magic": PRIVATE_METADATA_MAGIC,
            "private_chunk_policy": PRIVATE_CHUNK_POLICY,
            "copy_note": "unsafe-to-copy private chunk because metadata is bound to canonical APNG bytes",
        }
    )
    png_bytes = _insert_private_chunk(
        canonical_apng_bytes,
        _encode_private_chunk_data(metadata),
    )
    return {
        "variant_id": "private_mgot",
        "carrier_family": "private",
        "chunk_type": PRIVATE_METADATA_CHUNK_TYPE,
        "compressed": False,
        "encoding_policy": "magic_prefixed_utf8_json_private_chunk",
        "png_bytes": png_bytes,
        "canonical_apng_bytes": canonical_apng_bytes,
        "metadata": metadata,
        "png_file_name": f"{slip_profile['profile_id']}_private_mgot_apng_carrier.png",
        "grid_id": grid["grid_id"],
        "profile_id": slip_profile["profile_id"],
    }


def _extract_metadata_carrier(png_bytes: bytes) -> dict:
    try:
        extracted = _extract_textual_metadata(png_bytes)
        return {
            **extracted,
            "carrier_family": "textual",
            "variant_id": extracted["metadata"]["variant_id"],
        }
    except PNGTextualMetadataPolicyError as exc:
        if exc.family != "png_textual_metadata_chunk_missing":
            raise

    try:
        extracted = _extract_private_chunk(png_bytes)
        return {
            **extracted,
            "carrier_family": "private",
            "variant_id": "private_mgot",
        }
    except PNGPrivateChunkPolicyError as exc:
        if exc.family == "png_private_chunk_missing":
            raise PNGTextualMetadataPolicyError(
                "apng_metadata_carrier_missing",
                "APNG does not contain a Mechagotchi textual or private metadata carrier",
            ) from exc
        raise


def _carrier_policy_summary(extracted: dict) -> dict:
    metadata = extracted["metadata"]
    summary = {
        "ok": True,
        "carrier_model": metadata.get("carrier_model"),
        "carrier_family": extracted["carrier_family"],
        "variant_id": extracted["variant_id"],
        "chunk_type": extracted["chunk_type"],
        "canonical_apng_hash": metadata["canonical_png_hash"],
        "sidecar_hash": metadata["sidecar_hash"],
        "live_external_editor_verified": False,
    }
    if extracted["carrier_family"] == "textual":
        summary.update(
            {
                "encoding_policy": metadata["encoding_policy"],
                "compressed": metadata["compressed"],
                "keyword": metadata["keyword"],
                "textual_chunk_count": extracted["textual_chunk_count"],
                "unicode_metadata_supported": extracted["chunk_type"] == "iTXt",
            }
        )
    else:
        properties = metadata["chunk_type_properties"]
        summary.update(
            {
                "magic": metadata["magic"],
                "private_chunk_policy": metadata["private_chunk_policy"],
                "ancillary": properties["ancillary"],
                "private": properties["private"],
                "reserved_bit_valid": properties["reserved_bit_valid"],
                "safe_to_copy": properties["safe_to_copy"],
                "private_chunk_count": extracted["private_chunk_count"],
            }
        )
    return summary


def _invalid_probe_results(reference_results: list[dict]) -> list[dict]:
    by_id = {result["variant_id"]: result for result in reference_results}
    text_png = bytes.fromhex(by_id["text_ascii"]["png_bytes_hex"])
    ztxt_png = bytes.fromhex(by_id["ztxt_ascii"]["png_bytes_hex"])
    itxt_png = bytes.fromhex(by_id["itxt_utf8_compressed"]["png_bytes_hex"])
    private_png = bytes.fromhex(by_id["private_mgot"]["png_bytes_hex"])
    probes = [
        ("missing_textual_carrier", remove_png_textual_metadata_chunks(text_png)),
        ("duplicate_textual_carrier", duplicate_png_textual_metadata_chunk(text_png)),
        ("corrupt_ztxt_stream", corrupt_png_textual_metadata_ztxt_stream(ztxt_png)),
        ("tamper_private_canonical_hash", tamper_png_private_chunk_canonical_hash(private_png)),
        ("missing_private_carrier", remove_png_private_chunks(private_png)),
        ("tamper_apng_sequence_number", tamper_apng_sequence_number(itxt_png)),
    ]
    return [
        {
            "probe_id": probe_id,
            **_compact_apng_import_result(import_apng_metadata_carrier(probe_png)),
        }
        for probe_id, probe_png in probes
    ]


def _metadata_summary(metadata: dict) -> dict:
    keys = [
        "carrier_model",
        "metadata_model",
        "variant_id",
        "keyword",
        "chunk_type",
        "encoding_policy",
        "compressed",
        "magic",
        "private_chunk_policy",
        "canonical_png_hash",
        "sidecar_hash",
        "hash_note",
    ]
    return {key: metadata[key] for key in keys if key in metadata}


def _json_report(report: dict) -> dict:
    payload = deepcopy(report)
    for result in payload["metadata_carrier_results"]:
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
                "metadata_carrier_roundtrip_count",
                "metadata_carrier_roundtrip_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "carrier_summaries": [
            {
                "profile_id": result["profile_id"],
                "variant_id": result["variant_id"],
                "carrier_family": result["carrier_family"],
                "chunk_type": result["chunk_type"],
                "metadata_carrier_policy": result["metadata_carrier_policy"],
                "semantic_fidelity": result["semantic_fidelity"],
                "frame_pixel_fidelity": result["frame_pixel_fidelity"],
            }
            for result in json_report["metadata_carrier_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# APNG Metadata Carrier Cross Product Stage 0\n\n"
        "Bounded APNG metadata-carrier cross product for existing textual and "
        "private PNG carrier policies.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Carrier round-trip successes: {report['metadata_carrier_roundtrip_success_count']}"
        f"/{report['metadata_carrier_roundtrip_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- Mean semantic fidelity: {metrics['mean_semantic_fidelity']}\n"
        f"- Mean frame-pixel fidelity: {metrics['mean_frame_pixel_fidelity']}\n"
        f"- Decision: {report['decision']}\n"
    )


def _mean(values) -> float:
    values = list(values)
    if not values:
        return 0.0
    return round(sum(values) / len(values), 6)


def _first_grid_path(profile: dict, generated_root: Path) -> Path:
    grid_paths = sorted((generated_root / profile["profile_id"]).glob("*.json"))
    if not grid_paths:
        raise ValueError(f"no generated grids found for profile: {profile['profile_id']}")
    return grid_paths[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "data/workshop_editor/apng_metadata_carrier_cross_product_stage0",
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
    report = run_apng_metadata_carrier_cross_product_lab(profile_paths, args.generated_root)
    write_apng_metadata_carrier_cross_product_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_APNG_METADATA_CARRIER_CROSS_PRODUCT = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
