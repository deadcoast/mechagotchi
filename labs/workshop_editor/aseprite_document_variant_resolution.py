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

from slip import is_grid_aligned
from validator import validate_grid

from aseprite_external_properties_semantics import (
    ASE_CHUNK_EXTERNAL_FILES,
    _external_files_chunk_data,
    _parse_external_files_chunk,
)
from aseprite_palette_slice_semantics import (
    ASE_CHUNK_PALETTE,
    _palette_chunk_data,
    _palette_semantics,
    _parse_palette_chunk,
)
from aseprite_user_data_chunk_writer import (
    ASE_CHUNK_CEL,
    ASE_CHUNK_LAYER,
    ASE_CHUNK_USER_DATA,
    ASE_FRAME_HEADER_FORMAT,
    ASE_FRAME_MAGIC,
    ASE_HEADER_FORMAT,
    ASE_MAGIC,
    ASE_USER_DATA_PREFIX,
    AsepriteUserDataError,
    _chunk,
    _hash_bytes,
    _hash_payload,
    _hash_text,
    _pack_string,
    _parse_layer_chunk,
    _parse_user_data_chunk,
    _ratio,
    _user_data_chunk_data,
    _write_aseprite,
)
from external_metadata_sidecar import build_sidecar_for_grid, restore_grid_from_sidecar
from standard_image_sidecar_decoder import render_grid_rgba_pixels
from png_chunk_reader import PNGChunkError, bounded_decompress
from workshop_editor import compare_semantic_grid_fidelity


ASE_DOCUMENT_VARIANT_VERSION = "mechagotchi.aseprite_document_variant_resolution.v1"
ASE_DOCUMENT_VARIANT_POLICY = "aseprite_document_variant_external_asset_resolution"
ASE_DOCUMENT_VARIANT_NATIVE_LOCATION = (
    "frame[0].external_files + frame[0].palette[indexed_only] + "
    "frame[0].cel.pixel_payload + frame[0].layer.user_data.text"
)
REPORT_PATH = Path("data/workshop_editor/aseprite_document_variant_resolution_stage0.json")
DATA_PATH = Path("data/workshop_editor/aseprite_document_variant_resolution_data.js")


VARIANT_SPECS = [
    {
        "variant_id": "indexed_8",
        "color_depth_bpp": 8,
        "bytes_per_pixel": 1,
        "decoder_scope": "aseprite_indexed_8bpp_palette_compressed_cel_external_files_subset",
    },
    {
        "variant_id": "grayscale_alpha_16",
        "color_depth_bpp": 16,
        "bytes_per_pixel": 2,
        "decoder_scope": "aseprite_grayscale_alpha_16bpp_compressed_cel_external_files_subset",
    },
    {
        "variant_id": "rgba_32",
        "color_depth_bpp": 32,
        "bytes_per_pixel": 4,
        "decoder_scope": "aseprite_rgba_32bpp_compressed_cel_external_files_subset",
    },
]


def export_aseprite_document_variant_bundle(grid: dict, slip_profile: dict) -> dict:
    external_assets = _external_assets_for_grid(grid, slip_profile)
    external_file_entries = _external_file_entries(external_assets)
    raw_payloads = {
        spec["variant_id"]: _raw_payload_for_variant(grid, spec)
        for spec in VARIANT_SPECS
    }
    variant_pixel_hashes = {
        variant_id: _hash_bytes(payload) for variant_id, payload in raw_payloads.items()
    }

    variants = []
    metadata_summaries = {}
    for spec in VARIANT_SPECS:
        variant_id = spec["variant_id"]
        canonical_project = _encode_aseprite_document_variant_project(
            grid,
            spec,
            external_file_entries,
            raw_payloads[variant_id],
            metadata=None,
        )
        canonical_hash = _hash_bytes(canonical_project)
        asset = {
            "asset_id": f"{grid['grid_id']}_{variant_id}.aseprite",
            "format_id": "libresprite_project",
            "media_type": "application/octet-stream",
            "uri": f"generated://workshop/project-document-variant/{grid['grid_id']}/{variant_id}.aseprite",
            "width": grid["grid_size"][0],
            "height": grid["grid_size"][1],
            "frame_count": 1,
            "content_hash": canonical_hash,
            "semantic_policy": ASE_DOCUMENT_VARIANT_POLICY,
        }
        sidecar = build_sidecar_for_grid(grid, slip_profile, asset)
        sidecar["sidecar_id"] = f"{grid['grid_id']}_{variant_id}_aseprite_document_variant_sidecar"
        sidecar["asset_binding"]["semantic_policy"] = ASE_DOCUMENT_VARIANT_POLICY
        sidecar["project_binding"] = {
            "format_id": "libresprite_project",
            "decoder_scope": spec["decoder_scope"],
            "native_mechagotchi_semantics": True,
            "semantic_policy": ASE_DOCUMENT_VARIANT_POLICY,
            "native_metadata_version": ASE_DOCUMENT_VARIANT_VERSION,
        }
        sidecar["limitations"] = [
            "Stage 0 Aseprite/LibreSprite document-variant proof covers deterministic 8 bpp indexed, 16 bpp grayscale-alpha, and 32 bpp RGBA compressed cels.",
            "External Files Chunk entries are resolved against deterministic generated payloads and hashes only.",
            "Live external editor rewrite validation is not verified by this lab.",
            "Arbitrary Aseprite project schemas, arbitrary external asset resolution, and full project-format coverage remain separate.",
        ]
        metadata = _build_document_variant_metadata(
            canonical_hash,
            spec,
            variant_pixel_hashes,
            external_assets,
            sidecar,
            grid,
        )
        project_bytes = _encode_aseprite_document_variant_project(
            grid,
            spec,
            external_file_entries,
            raw_payloads[variant_id],
            metadata=metadata,
        )
        decoded = decode_aseprite_document_variant_project(project_bytes)
        metadata_summaries[variant_id] = _metadata_summary(metadata)
        variants.append(
            {
                "variant_id": variant_id,
                "color_depth_bpp": spec["color_depth_bpp"],
                "bytes_per_pixel": spec["bytes_per_pixel"],
                "project_bytes": project_bytes,
                "canonical_project_bytes": canonical_project,
                "embedded_project_hash": _hash_bytes(project_bytes),
                "canonical_project_hash": canonical_hash,
                "metadata": metadata,
                "sidecar": sidecar,
                "decoded_project": decoded,
            }
        )

    return {
        "grid_id": grid["grid_id"],
        "profile_id": slip_profile["profile_id"],
        "metadata": {
            "metadata_version": ASE_DOCUMENT_VARIANT_VERSION,
            "writer_policy": ASE_DOCUMENT_VARIANT_POLICY,
            "variant_ids": [spec["variant_id"] for spec in VARIANT_SPECS],
            "variant_pixel_hashes": variant_pixel_hashes,
            "variant_metadata": metadata_summaries,
            "external_asset_manifest": _external_asset_manifest(external_assets),
        },
        "external_assets": external_assets,
        "variants": variants,
    }


def decode_aseprite_document_variant_project(project_bytes: bytes) -> dict:
    parsed = _parse_aseprite_any_depth(project_bytes)
    color_depth = parsed["header"]["color_depth"]
    bytes_per_pixel = _bytes_per_pixel(color_depth)
    variant_id = _variant_id_for_depth(color_depth)
    layers = []
    cels = []
    external_files = []
    user_data_chunks = []
    palette = None
    palette_chunk_count = 0
    native = False
    total_chunk_count = 0
    last_target = None

    for frame_index, frame in enumerate(parsed["frames"]):
        for chunk in frame["chunks"]:
            total_chunk_count += 1
            chunk_type = chunk["type"]
            if chunk_type == ASE_CHUNK_EXTERNAL_FILES:
                for entry in _parse_external_files_chunk(chunk["data"]):
                    entry["frame_index"] = frame_index
                    external_files.append(entry)
                last_target = {
                    "target_type": "sprite",
                    "target_index": None,
                    "target_name": "external_files",
                }
            elif chunk_type == ASE_CHUNK_PALETTE:
                palette = _parse_palette_chunk(chunk["data"])
                palette["frame_index"] = frame_index
                palette_chunk_count += 1
                last_target = {
                    "target_type": "palette",
                    "target_index": 0,
                    "target_name": "indexed_palette",
                }
            elif chunk_type == ASE_CHUNK_LAYER:
                layer = _parse_layer_chunk(chunk["data"])
                layer["index"] = len(layers)
                layer["frame_index"] = frame_index
                layers.append(layer)
                last_target = {
                    "target_type": "layer",
                    "target_index": layer["index"],
                    "target_name": layer["name"],
                }
            elif chunk_type == ASE_CHUNK_CEL:
                cel = _parse_variant_cel_chunk(
                    chunk["data"],
                    parsed["header"]["width"],
                    parsed["header"]["height"],
                    bytes_per_pixel,
                )
                cel["index"] = len(cels)
                cel["frame_index"] = frame_index
                cels.append(cel)
                last_target = {
                    "target_type": "cel",
                    "target_index": cel["index"],
                    "target_name": f"frame_{frame_index}_layer_{cel['layer_index']}",
                }
            elif chunk_type == ASE_CHUNK_USER_DATA:
                user_data = _parse_user_data_chunk(chunk["data"])
                text = user_data["text"]
                target = last_target or {
                    "target_type": "unknown",
                    "target_index": None,
                    "target_name": None,
                }
                entry = {
                    "chunk_type": "0x2020",
                    "flags": user_data["flags"],
                    "text_present": text is not None,
                    "text_hash": _hash_text(text or ""),
                    **target,
                }
                if isinstance(text, str) and text.startswith(ASE_USER_DATA_PREFIX):
                    try:
                        metadata = json.loads(text[len(ASE_USER_DATA_PREFIX) :])
                    except json.JSONDecodeError as exc:
                        raise AsepriteUserDataError("aseprite_document_variant_json_invalid", str(exc)) from exc
                    if metadata.get("metadata_version") == ASE_DOCUMENT_VARIANT_VERSION:
                        native = True
                        variant_id = metadata.get("variant_id", variant_id)
                user_data_chunks.append(entry)

    variant_pixel_hash = cels[0]["variant_pixel_hash"] if cels else None
    return {
        "format_id": "libresprite_project",
        "magic": hex(parsed["header"]["magic"]),
        "frame_magic": hex(parsed["frames"][0]["magic"]) if parsed["frames"] else None,
        "variant_id": variant_id,
        "dimensions": [parsed["header"]["width"], parsed["header"]["height"]],
        "frame_count": parsed["header"]["frames"],
        "layer_count": len(layers),
        "cel_count": len(cels),
        "chunk_count": total_chunk_count,
        "external_files_chunk_count": 1 if external_files else 0,
        "external_file_entry_count": len(external_files),
        "user_data_chunk_count": len(user_data_chunks),
        "palette_chunk_count": palette_chunk_count,
        "palette_entry_count": len(palette["entries"]) if palette else 0,
        "indexed_palette_hash": _hash_payload(palette["entries"]) if palette else None,
        "color_depth_bpp": color_depth,
        "bytes_per_pixel": bytes_per_pixel,
        "first_frame_duration_ms": parsed["frames"][0]["duration_ms"] if parsed["frames"] else parsed["header"]["speed_ms"],
        "layers": layers,
        "external_files": external_files,
        "palette": palette or {},
        "cels": [_cel_summary(cel) for cel in cels],
        "variant_pixel_hash": variant_pixel_hash,
        "user_data_chunks": user_data_chunks,
        "native_mechagotchi_semantics": native,
    }


def import_aseprite_document_variant_project(
    project_bytes: bytes,
    external_assets: list[dict] | dict,
    source_grid: dict | None = None,
) -> dict:
    try:
        extracted = extract_aseprite_document_variant_sidecar(project_bytes, external_assets)
    except AsepriteUserDataError as exc:
        return _failed_import("aseprite_document_variant", exc.family, exc.message)

    sidecar = extracted["sidecar"]
    asset = deepcopy(sidecar["asset_binding"])
    try:
        restored = restore_grid_from_sidecar(sidecar, asset)
    except ValueError as exc:
        return _failed_import("sidecar", "aseprite_document_variant_sidecar_invalid", str(exc))

    profile = sidecar["slip_binding"]["profile_snapshot"]
    grid_validation = validate_grid(restored)
    alignment = is_grid_aligned(restored, profile)
    semantic_source = source_grid or restore_grid_from_sidecar(sidecar, asset, validate=False)
    diff = compare_semantic_grid_fidelity(semantic_source, restored)
    fidelity = _semantic_fidelity(diff, semantic_source)
    errors = []
    if not grid_validation.ok:
        errors.extend(_error("$", "restored_grid_invalid", message) for message in grid_validation.errors)
    if not alignment.ok:
        errors.extend(_error("$", "restored_grid_not_slip_aligned", message) for message in alignment.errors)
    return {
        "ok": grid_validation.ok and alignment.ok and fidelity == 1.0,
        "format_id": "libresprite_project",
        "asset": asset,
        "restored_grid": restored,
        "restored_grid_validation": {
            "valid": grid_validation.ok,
            "errors": grid_validation.errors,
            "slip_aligned": alignment.ok,
            "alignment_errors": alignment.errors,
        },
        "semantic_diff": diff,
        "semantic_fidelity": fidelity,
        "native_metadata": _metadata_summary(extracted["metadata"]),
        "decoded_project": _decoded_project_summary(extracted["decoded_project"]),
        "resolved_external_assets": extracted["resolved_external_assets"],
        "project_policy": {
            "semantic_policy": ASE_DOCUMENT_VARIANT_POLICY,
            "native_mechagotchi_semantics": extracted["decoded_project"]["native_mechagotchi_semantics"],
            "native_location": ASE_DOCUMENT_VARIANT_NATIVE_LOCATION,
            "native_metadata_version": ASE_DOCUMENT_VARIANT_VERSION,
            "external_asset_resolution_policy": "deterministic_stage0_resolver",
            "document_variant_count": len(VARIANT_SPECS),
            "resolved_external_asset_count": len(extracted["resolved_external_assets"]),
            "color_depth_bpp": extracted["decoded_project"]["color_depth_bpp"],
            "variant_id": extracted["decoded_project"]["variant_id"],
            "external_files_chunk_type": "0x2008",
            "palette_chunk_type": "0x2019" if extracted["decoded_project"]["color_depth_bpp"] == 8 else None,
            "cel_chunk_type": "0x2005",
            "live_external_editor_verified": False,
        },
        "errors": errors,
        "error_families": sorted({error["family"] for error in errors}),
    }


def extract_aseprite_document_variant_sidecar(
    project_bytes: bytes,
    external_assets: list[dict] | dict,
) -> dict:
    decoded = decode_aseprite_document_variant_project(project_bytes)
    metadata = _extract_document_variant_metadata(project_bytes)
    if metadata.get("metadata_version") != ASE_DOCUMENT_VARIANT_VERSION:
        raise AsepriteUserDataError(
            "aseprite_document_variant_version_unsupported",
            "unsupported Aseprite document-variant metadata version",
        )
    if metadata.get("format_id") != "libresprite_project":
        raise AsepriteUserDataError(
            "aseprite_document_variant_format_mismatch",
            "Aseprite document-variant metadata format id mismatch",
        )
    if metadata.get("writer_policy") != ASE_DOCUMENT_VARIANT_POLICY:
        raise AsepriteUserDataError(
            "aseprite_document_variant_policy_mismatch",
            "Aseprite document-variant writer policy mismatch",
        )
    if decoded["variant_id"] != metadata.get("variant_id"):
        raise AsepriteUserDataError(
            "aseprite_document_variant_id_mismatch",
            "Aseprite document variant id does not match metadata",
        )
    if decoded["color_depth_bpp"] != metadata.get("color_depth_bpp"):
        raise AsepriteUserDataError(
            "aseprite_document_variant_color_depth_mismatch",
            "Aseprite document variant color depth does not match metadata",
        )
    if decoded["bytes_per_pixel"] != metadata.get("bytes_per_pixel"):
        raise AsepriteUserDataError(
            "aseprite_document_variant_pixel_width_mismatch",
            "Aseprite document variant pixel width does not match metadata",
        )
    if decoded["external_file_entry_count"] == 0:
        raise AsepriteUserDataError(
            "aseprite_external_files_missing",
            "Aseprite document variant does not contain the required External Files chunk",
        )
    _validate_external_file_entries(decoded, metadata)
    if decoded["color_depth_bpp"] == 8:
        if decoded["palette_chunk_count"] != 1:
            raise AsepriteUserDataError(
                "aseprite_indexed_palette_missing",
                "indexed Aseprite document variant must contain one Palette chunk",
            )
        if decoded["indexed_palette_hash"] != metadata.get("indexed_palette_hash"):
            raise AsepriteUserDataError(
                "aseprite_indexed_palette_mismatch",
                "indexed Aseprite palette does not match document-variant metadata",
            )
    if decoded["variant_pixel_hash"] != metadata.get("variant_pixel_hash"):
        raise AsepriteUserDataError(
            "aseprite_variant_pixel_hash_mismatch",
            "Aseprite document variant pixel payload hash does not match metadata",
        )
    sidecar = metadata.get("sidecar")
    if not isinstance(sidecar, dict):
        raise AsepriteUserDataError(
            "aseprite_document_variant_sidecar_missing",
            "Aseprite document variant metadata must contain a sidecar object",
        )
    if _hash_payload(sidecar) != metadata.get("sidecar_hash"):
        raise AsepriteUserDataError(
            "aseprite_document_variant_sidecar_hash_mismatch",
            "Aseprite document variant sidecar hash does not match the embedded sidecar",
        )
    canonical = strip_aseprite_document_variant_metadata(project_bytes)
    canonical_hash = _hash_bytes(canonical)
    if canonical_hash != metadata.get("canonical_project_hash"):
        raise AsepriteUserDataError(
            "aseprite_document_variant_canonical_hash_mismatch",
            "Aseprite document variant canonical project hash does not match the stripped project",
        )
    if sidecar.get("asset_binding", {}).get("content_hash") != canonical_hash:
        raise AsepriteUserDataError(
            "aseprite_document_variant_sidecar_asset_hash_mismatch",
            "Aseprite document variant sidecar asset hash does not match the canonical project hash",
        )
    resolved_assets = _resolve_external_assets(decoded, metadata, external_assets)
    return {
        "ok": True,
        "metadata": metadata,
        "sidecar": sidecar,
        "decoded_project": decoded,
        "resolved_external_assets": resolved_assets,
        "canonical_project_hash": canonical_hash,
        "embedded_project_hash": _hash_bytes(project_bytes),
    }


def strip_aseprite_document_variant_metadata(project_bytes: bytes) -> bytes:
    return _rewrite_chunks(project_bytes, lambda chunk: chunk["type"] != ASE_CHUNK_USER_DATA)


def strip_aseprite_variant_external_file_chunks(project_bytes: bytes) -> bytes:
    return _rewrite_chunks(project_bytes, lambda chunk: chunk["type"] != ASE_CHUNK_EXTERNAL_FILES)


def tamper_aseprite_variant_external_asset_hash(external_assets: list[dict] | dict) -> list[dict]:
    assets = [_normal_asset(asset) for asset in _asset_iter(external_assets)]
    if not assets:
        return assets
    assets[0] = deepcopy(assets[0])
    assets[0]["payload_text"] = assets[0].get("payload_text", "") + "\n# tampered payload\n"
    return assets


def tamper_aseprite_variant_color_depth(project_bytes: bytes, color_depth_bpp: int) -> bytes:
    payload = bytearray(project_bytes)
    payload[12:14] = struct.pack("<H", color_depth_bpp)
    return bytes(payload)


def tamper_aseprite_indexed_palette(project_bytes: bytes) -> bytes:
    def mutate(chunk: dict) -> dict:
        if chunk["type"] != ASE_CHUNK_PALETTE:
            return chunk
        payload = bytearray(chunk["data"])
        first_red_offset = struct.calcsize("<III8s") + struct.calcsize("<H")
        if first_red_offset < len(payload):
            payload[first_red_offset] = (payload[first_red_offset] + 1) % 256
        return _chunk(ASE_CHUNK_PALETTE, bytes(payload))

    return _map_chunks(project_bytes, mutate)


def tamper_aseprite_variant_pixel_payload(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite_any_depth(project_bytes)
    bytes_per_pixel = _bytes_per_pixel(parsed["header"]["color_depth"])

    def mutate(chunk: dict) -> dict:
        if chunk["type"] != ASE_CHUNK_CEL:
            return chunk
        return _chunk(ASE_CHUNK_CEL, _tampered_cel_payload(chunk["data"], bytes_per_pixel))

    return _map_chunks(project_bytes, mutate)


def tamper_aseprite_document_variant_metadata(project_bytes: bytes) -> bytes:
    def mutate(chunk: dict) -> dict:
        if chunk["type"] != ASE_CHUNK_USER_DATA:
            return chunk
        user_data = _parse_user_data_chunk(chunk["data"])
        text = user_data.get("text")
        if not isinstance(text, str) or not text.startswith(ASE_USER_DATA_PREFIX):
            return chunk
        metadata = json.loads(text[len(ASE_USER_DATA_PREFIX) :])
        if metadata.get("metadata_version") != ASE_DOCUMENT_VARIANT_VERSION:
            return chunk
        tampered = deepcopy(metadata)
        tampered["sidecar"]["semantic_overlay"]["metadata"]["tampered"] = True
        return _chunk(ASE_CHUNK_USER_DATA, _user_data_chunk_data(tampered))

    return _map_chunks(project_bytes, mutate)


def tamper_aseprite_document_variant_metadata_json(project_bytes: bytes) -> bytes:
    def mutate(chunk: dict) -> dict:
        if chunk["type"] != ASE_CHUNK_USER_DATA:
            return chunk
        user_data = _parse_user_data_chunk(chunk["data"])
        text = user_data.get("text")
        if not isinstance(text, str) or not text.startswith(ASE_USER_DATA_PREFIX):
            return chunk
        corrupted = struct.pack("<I", 1) + _pack_string(ASE_USER_DATA_PREFIX + '{"metadata_version":')
        return _chunk(ASE_CHUNK_USER_DATA, corrupted)

    return _map_chunks(project_bytes, mutate)


def run_aseprite_document_variant_resolution_lab(profile_paths: list[Path], generated_root: Path) -> dict:
    document_variant_results = []
    bundles = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        bundle = export_aseprite_document_variant_bundle(grid, profile)
        bundles.append(bundle)
        for variant in bundle["variants"]:
            imported = import_aseprite_document_variant_project(
                variant["project_bytes"],
                bundle["external_assets"],
                source_grid=grid,
            )
            diff = imported.get("semantic_diff", {"changed_cells": [], "missing_cells": [], "added_cells": []})
            document_variant_results.append(
                {
                    "profile_id": profile["profile_id"],
                    "profile_path": _portable(profile_path),
                    "grid_path": _portable(grid_path),
                    "grid_id": grid["grid_id"],
                    "format_id": "libresprite_project",
                    "variant_id": variant["variant_id"],
                    "color_depth_bpp": variant["color_depth_bpp"],
                    "bytes_per_pixel": variant["bytes_per_pixel"],
                    "project_file_name": f"{profile['profile_id']}_{variant['variant_id']}.aseprite",
                    "project_byte_count": len(variant["project_bytes"]),
                    "embedded_project_hash": variant["embedded_project_hash"],
                    "canonical_project_hash": variant["canonical_project_hash"],
                    "metadata": _metadata_summary(variant["metadata"]),
                    "native_sidecar": variant["sidecar"],
                    "decoded_project": _decoded_project_summary(variant["decoded_project"]),
                    "external_assets": _artifact_external_assets(bundle["external_assets"]),
                    "import_result": _compact_import_result(imported),
                    "restored_grid_validation": imported.get("restored_grid_validation"),
                    "semantic_diff": diff,
                    "semantic_fidelity": imported.get("semantic_fidelity", 0.0),
                    "variant_pixel_hash_preserved": (
                        variant["decoded_project"]["variant_pixel_hash"]
                        == variant["metadata"]["variant_pixel_hash"]
                    ),
                    "external_assets_resolved": (
                        imported.get("project_policy", {}).get("resolved_external_asset_count", 0)
                        == len(bundle["external_assets"])
                    ),
                    "project_bytes_hex": variant["project_bytes"].hex(),
                }
            )

    invalid_probe_results = _invalid_probe_results(bundles[0])
    success_count = sum(1 for result in document_variant_results if result["import_result"]["ok"])
    invalid_rejected = sum(1 for result in invalid_probe_results if not result["ok"])
    pixel_hash_preserved = sum(1 for result in document_variant_results if result["variant_pixel_hash_preserved"])
    external_assets_resolved = sum(1 for result in document_variant_results if result["external_assets_resolved"])
    return {
        "artifact_id": "aseprite_document_variant_resolution_stage0",
        "status": "research_aseprite_document_variant_resolution_no_package_code",
        "date": "2026-05-14",
        "purpose": (
            "Broaden Stage 0 Aseprite/LibreSprite schema coverage beyond fixed "
            "RGBA carriers by proving deterministic indexed 8 bpp, grayscale-alpha "
            "16 bpp, and RGBA 32 bpp document variants with hashed External Files "
            "Chunk asset resolution."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
            "labs/workshop_editor/aseprite_document_variant_resolution.py",
        ],
        "external_anchors": [
            {
                "source": "Aseprite file-format specification",
                "url": "https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md",
                "used_for": "8/16/32 bpp pixel sizes, compressed Cel Chunk 0x2005, Palette Chunk 0x2019, and External Files Chunk 0x2008 layouts.",
            },
            {
                "source": "Aseprite files documentation",
                "url": "https://www.aseprite.org/docs/files",
                "used_for": "Project-file boundary; live editor open-save behavior remains unclaimed.",
            },
            {
                "source": "LibreSprite GitHub",
                "url": "https://github.com/LibreSprite/LibreSprite",
                "used_for": "LibreSprite remains a compatibility boundary; no GPL editor code is embedded.",
            },
        ],
        "profile_count": len(profile_paths),
        "document_variant_roundtrip_count": len(document_variant_results),
        "document_variant_roundtrip_success_count": success_count,
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected,
        "metrics": {
            "document_variant_roundtrip_success_rate": _ratio(success_count, len(document_variant_results)),
            "mean_semantic_fidelity": round(
                sum(result["semantic_fidelity"] for result in document_variant_results)
                / max(1, len(document_variant_results)),
                6,
            ),
            "variant_pixel_hash_preservation_rate": _ratio(pixel_hash_preserved, len(document_variant_results)),
            "external_asset_resolution_rate": _ratio(external_assets_resolved, len(document_variant_results)),
            "invalid_probe_rejection_rate": _ratio(invalid_rejected, len(invalid_probe_results)),
            "live_external_editor_verified": False,
        },
        "document_variant_results": document_variant_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "aseprite_indexed_8bpp_document_subset",
            "aseprite_grayscale_alpha_16bpp_document_subset",
            "aseprite_rgba_32bpp_document_subset",
            "aseprite_external_asset_resolution_subset",
            "aseprite_document_variant_hash_validation",
        ],
        "blocked_states": [
            "live_external_editor_rewrite_validation",
            "arbitrary_aseprite_project_schema_coverage",
            "arbitrary_external_asset_resolution",
            "full_project_format_coverage",
            "package_runtime_lifecycle_integration",
            "manual_readability_calibration",
            "profile_weighted_evolution",
            "community_profile_packs",
        ],
        "decision": "prototype_aseprite_document_variant_resolution_subset",
        "next_research_step": (
            "Keep live external editor validation, arbitrary Aseprite schemas, "
            "arbitrary external asset resolution, and full project-format coverage "
            "blocked until direct editor fixtures and broader schema tests exist."
        ),
    }


def write_aseprite_document_variant_resolution_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    external_dir = output_dir / "external_assets"
    external_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "aseprite_document_variant_resolution_stage0.json", _json_report(report))
    written_assets = set()
    for result in report["document_variant_results"]:
        (output_dir / result["project_file_name"]).write_bytes(bytes.fromhex(result["project_bytes_hex"]))
        for asset in result["external_assets"]:
            asset_path = external_dir / Path(asset["name"]).name
            if asset_path.name in written_assets:
                continue
            asset_path.write_text(asset["payload_text"], encoding="utf-8")
            written_assets.add(asset_path.name)
    (output_dir / "aseprite_document_variant_resolution_data.js").write_text(
        "window.MECHAGOTCHI_ASEPRITE_DOCUMENT_VARIANT_RESOLUTION = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")


def _encode_aseprite_document_variant_project(
    grid: dict,
    spec: dict,
    external_file_entries: list[dict],
    raw_payload: bytes,
    metadata: dict | None,
) -> bytes:
    width, height = grid["grid_size"]
    chunks = [
        _chunk(ASE_CHUNK_EXTERNAL_FILES, _external_files_chunk_data(external_file_entries)),
    ]
    if spec["color_depth_bpp"] == 8:
        chunks.append(_chunk(ASE_CHUNK_PALETTE, _palette_chunk_data(_palette_semantics(grid))))
    chunks.append(_chunk(ASE_CHUNK_LAYER, _layer_chunk_data(width, height)))
    if metadata is not None:
        chunks.append(_chunk(ASE_CHUNK_USER_DATA, _user_data_chunk_data(metadata)))
    chunks.append(
        _chunk(
            ASE_CHUNK_CEL,
            _variant_cel_chunk_data(0, width, height, spec["bytes_per_pixel"], raw_payload),
        )
    )
    header = {
        "frames": 1,
        "width": width,
        "height": height,
        "color_depth": spec["color_depth_bpp"],
        "flags": 1,
        "speed_ms": 120,
        "transparent_index": grid.get("palette", {}).get("background_index", 0),
        "color_count": len(grid.get("palette", {}).get("colors", [])) if spec["color_depth_bpp"] == 8 else 0,
        "pixel_width": 1,
        "pixel_height": 1,
        "grid_x": 0,
        "grid_y": 0,
        "grid_width": width,
        "grid_height": height,
    }
    return _write_aseprite(header, [{"duration_ms": 120, "chunks": chunks}])


def _parse_aseprite_any_depth(project_bytes: bytes) -> dict:
    header_size = struct.calcsize(ASE_HEADER_FORMAT)
    frame_header_size = struct.calcsize(ASE_FRAME_HEADER_FORMAT)
    if len(project_bytes) < header_size:
        raise AsepriteUserDataError("aseprite_header_truncated", "ASE header must be 128 bytes")
    fields = struct.unpack(ASE_HEADER_FORMAT, project_bytes[:header_size])
    header = {
        "file_size": fields[0],
        "magic": fields[1],
        "frames": fields[2],
        "width": fields[3],
        "height": fields[4],
        "color_depth": fields[5],
        "flags": fields[6],
        "speed_ms": fields[7],
        "transparent_index": fields[10],
        "color_count": fields[12],
        "pixel_width": fields[13],
        "pixel_height": fields[14],
        "grid_x": fields[15],
        "grid_y": fields[16],
        "grid_width": fields[17],
        "grid_height": fields[18],
    }
    if header["magic"] != ASE_MAGIC:
        raise AsepriteUserDataError("aseprite_magic_invalid", "ASE magic number must be 0xA5E0")
    if header["file_size"] != len(project_bytes):
        raise AsepriteUserDataError("aseprite_file_size_mismatch", "ASE file size field must match payload length")
    if header["frames"] < 1:
        raise AsepriteUserDataError("aseprite_frame_count_invalid", "ASE frame count must be positive")
    if header["width"] < 1 or header["height"] < 1:
        raise AsepriteUserDataError("aseprite_dimensions_invalid", "ASE dimensions must be positive")

    offset = header_size
    frames = []
    for _frame_index in range(header["frames"]):
        if offset + frame_header_size > len(project_bytes):
            raise AsepriteUserDataError("aseprite_frame_header_truncated", "ASE frame header is truncated")
        frame_size, magic, old_chunks, duration_ms, _unused, new_chunks = struct.unpack(
            ASE_FRAME_HEADER_FORMAT,
            project_bytes[offset : offset + frame_header_size],
        )
        if frame_size < frame_header_size:
            raise AsepriteUserDataError("aseprite_frame_header_invalid", "ASE frame size is invalid")
        if magic != ASE_FRAME_MAGIC:
            raise AsepriteUserDataError("aseprite_frame_magic_invalid", "ASE frame magic must be 0xF1FA")
        frame_end = offset + frame_size
        if frame_end > len(project_bytes):
            raise AsepriteUserDataError("aseprite_frame_size_invalid", "ASE frame exceeds file size")
        chunk_count = new_chunks if new_chunks else old_chunks
        chunk_offset = offset + frame_header_size
        chunks = []
        for _chunk_index in range(chunk_count):
            if chunk_offset + 6 > frame_end:
                raise AsepriteUserDataError("aseprite_chunk_header_truncated", "ASE chunk header is truncated")
            chunk_size, chunk_type = struct.unpack("<IH", project_bytes[chunk_offset : chunk_offset + 6])
            if chunk_size < 6:
                raise AsepriteUserDataError("aseprite_chunk_size_invalid", "ASE chunk size is invalid")
            chunk_end = chunk_offset + chunk_size
            if chunk_end > frame_end:
                raise AsepriteUserDataError("aseprite_chunk_size_invalid", "ASE chunk exceeds frame size")
            chunks.append(
                {
                    "type": chunk_type,
                    "data": project_bytes[chunk_offset + 6 : chunk_end],
                    "size": chunk_size,
                }
            )
            chunk_offset = chunk_end
        if chunk_offset != frame_end:
            raise AsepriteUserDataError("aseprite_frame_padding_unsupported", "unexpected ASE frame bytes after declared chunks")
        frames.append(
            {
                "magic": magic,
                "duration_ms": duration_ms,
                "chunks": chunks,
            }
        )
        offset = frame_end
    if offset != len(project_bytes):
        raise AsepriteUserDataError("aseprite_trailing_bytes", "unexpected bytes after ASE frames")
    return {"header": header, "frames": frames}


def _layer_chunk_data(width: int, height: int) -> bytes:
    from aseprite_user_data_chunk_writer import _pack_string

    return (
        struct.pack("<HHHHHHB3s", 3, 0, 0, width, height, 0, 255, b"\x00\x00\x00")
        + _pack_string("Mechagotchi document variant layer")
    )


def _variant_cel_chunk_data(
    layer_index: int,
    width: int,
    height: int,
    bytes_per_pixel: int,
    raw_payload: bytes,
) -> bytes:
    expected_length = width * height * bytes_per_pixel
    if len(raw_payload) != expected_length:
        raise ValueError("raw variant payload does not match dimensions")
    return (
        struct.pack("<HhhBHh5sHH", layer_index, 0, 0, 255, 2, 0, b"\x00" * 5, width, height)
        + zlib.compress(raw_payload)
    )


def _parse_variant_cel_chunk(
    data: bytes,
    project_width: int,
    project_height: int,
    bytes_per_pixel: int,
) -> dict:
    prefix_size = struct.calcsize("<HhhBHh5s")
    if len(data) < prefix_size:
        raise AsepriteUserDataError("aseprite_cel_chunk_truncated", "ASE Cel chunk is truncated")
    layer_index, x, y, opacity, cel_type, z_index, _reserved = struct.unpack(
        "<HhhBHh5s",
        data[:prefix_size],
    )
    offset = prefix_size
    if cel_type != 2:
        raise AsepriteUserDataError("aseprite_cel_type_unsupported", "Stage 0 document-variant lab only supports compressed image cels")
    if offset + 4 > len(data):
        raise AsepriteUserDataError("aseprite_cel_dimensions_truncated", "compressed ASE Cel dimensions are truncated")
    width, height = struct.unpack("<HH", data[offset : offset + 4])
    offset += 4
    if [width, height] != [project_width, project_height]:
        raise AsepriteUserDataError("aseprite_cel_dimensions_mismatch", "compressed ASE Cel dimensions must match project dimensions")
    try:
        raw = bounded_decompress(data[offset:], width * height * bytes_per_pixel)
    except PNGChunkError as exc:
        raise AsepriteUserDataError("aseprite_cel_decompression_failed", exc.message) from exc
    if len(raw) != width * height * bytes_per_pixel:
        raise AsepriteUserDataError("aseprite_cel_payload_size_mismatch", "decoded ASE Cel payload size does not match dimensions")
    return {
        "chunk_type": "0x2005",
        "layer_index": layer_index,
        "x": x,
        "y": y,
        "opacity": opacity,
        "cel_type": cel_type,
        "z_index": z_index,
        "width": width,
        "height": height,
        "bytes_per_pixel": bytes_per_pixel,
        "raw_payload": raw,
        "variant_pixel_hash": _hash_bytes(raw),
    }


def _extract_document_variant_metadata(project_bytes: bytes) -> dict:
    parsed = _parse_aseprite_any_depth(project_bytes)
    for frame in parsed["frames"]:
        for chunk in frame["chunks"]:
            if chunk["type"] != ASE_CHUNK_USER_DATA:
                continue
            user_data = _parse_user_data_chunk(chunk["data"])
            text = user_data["text"]
            if isinstance(text, str) and text.startswith(ASE_USER_DATA_PREFIX):
                try:
                    metadata = json.loads(text[len(ASE_USER_DATA_PREFIX) :])
                except json.JSONDecodeError as exc:
                    raise AsepriteUserDataError("aseprite_document_variant_json_invalid", str(exc)) from exc
                if metadata.get("metadata_version") == ASE_DOCUMENT_VARIANT_VERSION:
                    return metadata
    raise AsepriteUserDataError(
        "aseprite_document_variant_metadata_missing",
        "ASE project does not contain Mechagotchi document-variant metadata",
    )


def _build_document_variant_metadata(
    canonical_hash: str,
    spec: dict,
    variant_pixel_hashes: dict,
    external_assets: list[dict],
    sidecar: dict,
    grid: dict,
) -> dict:
    palette_entries = _indexed_palette_entries_for_hash(grid) if spec["color_depth_bpp"] == 8 else []
    return {
        "metadata_version": ASE_DOCUMENT_VARIANT_VERSION,
        "format_id": "libresprite_project",
        "native_location": ASE_DOCUMENT_VARIANT_NATIVE_LOCATION,
        "writer_policy": ASE_DOCUMENT_VARIANT_POLICY,
        "variant_id": spec["variant_id"],
        "variant_ids": [item["variant_id"] for item in VARIANT_SPECS],
        "color_depth_bpp": spec["color_depth_bpp"],
        "bytes_per_pixel": spec["bytes_per_pixel"],
        "canonical_project_hash": canonical_hash,
        "variant_pixel_hash": variant_pixel_hashes[spec["variant_id"]],
        "variant_pixel_hashes": variant_pixel_hashes,
        "indexed_palette_hash": _hash_payload(palette_entries) if palette_entries else None,
        "external_asset_manifest": _external_asset_manifest(external_assets),
        "sidecar_hash": _hash_payload(sidecar),
        "sidecar": sidecar,
    }


def _raw_payload_for_variant(grid: dict, spec: dict) -> bytes:
    pixels = render_grid_rgba_pixels(grid)
    if spec["color_depth_bpp"] == 32:
        return bytes(channel for pixel in pixels for channel in pixel)
    if spec["color_depth_bpp"] == 16:
        payload = bytearray()
        for red, green, blue, alpha in pixels:
            luminance = round((red * 299 + green * 587 + blue * 114) / 1000)
            payload.extend([luminance, alpha])
        return bytes(payload)
    if spec["color_depth_bpp"] == 8:
        palette = _palette_semantics(grid)
        by_rgba = {tuple(entry["rgba"]): entry["index"] for entry in palette}
        payload = bytearray()
        for pixel in pixels:
            rgba = tuple(pixel)
            if rgba not in by_rgba:
                raise ValueError(f"grid pixel color is not present in indexed palette: {rgba}")
            payload.append(by_rgba[rgba])
        return bytes(payload)
    raise AsepriteUserDataError(
        "aseprite_document_variant_color_depth_unsupported",
        "Stage 0 document-variant lab only supports 8, 16, and 32 bpp",
    )


def _indexed_palette_entries_for_hash(grid: dict) -> list[dict]:
    return [
        {
            "index": entry["index"],
            "flags": 1,
            "name": entry["name"],
            "hex": entry["hex"],
            "rgba": entry["rgba"],
        }
        for entry in _palette_semantics(grid)
    ]


def _external_assets_for_grid(grid: dict, slip_profile: dict) -> list[dict]:
    palette_text = _palette_asset_text(grid)
    tileset_text = json.dumps(_tileset_asset_payload(grid, slip_profile), indent=2) + "\n"
    resolver_text = json.dumps(_resolver_asset_payload(), indent=2) + "\n"
    return [
        _external_asset(1001, 0, f"{slip_profile['profile_id']}_palette.gpl", "text/plain", palette_text),
        _external_asset(1002, 1, f"{slip_profile['profile_id']}_tileset.json", "application/json", tileset_text),
        _external_asset(1003, 2, "mechagotchi_variant_resolver.json", "application/json", resolver_text),
    ]


def _external_asset(entry_id: int, entry_type: int, name: str, media_type: str, payload_text: str) -> dict:
    return {
        "entry_id": entry_id,
        "type": entry_type,
        "type_name": _external_type_name(entry_type),
        "name": name,
        "media_type": media_type,
        "content_hash": _hash_text(payload_text),
        "payload_text": payload_text,
    }


def _external_file_entries(external_assets: list[dict]) -> list[dict]:
    return [
        {
            "entry_id": asset["entry_id"],
            "type": asset["type"],
            "name": asset["name"],
        }
        for asset in external_assets
    ]


def _external_asset_manifest(external_assets: list[dict]) -> list[dict]:
    return [
        {
            "entry_id": asset["entry_id"],
            "type": asset["type"],
            "type_name": asset["type_name"],
            "name": asset["name"],
            "media_type": asset["media_type"],
            "content_hash": asset["content_hash"],
        }
        for asset in external_assets
    ]


def _validate_external_file_entries(decoded: dict, metadata: dict) -> None:
    decoded_entries = {
        (entry["entry_id"], entry["type"], entry["name"])
        for entry in decoded["external_files"]
    }
    manifest_entries = {
        (entry["entry_id"], entry["type"], entry["name"])
        for entry in metadata.get("external_asset_manifest", [])
    }
    if decoded_entries != manifest_entries:
        raise AsepriteUserDataError(
            "aseprite_external_files_mismatch",
            "Aseprite External Files entries do not match document-variant metadata",
        )


def _resolve_external_assets(
    decoded: dict,
    metadata: dict,
    external_assets: list[dict] | dict,
) -> list[dict]:
    provided = {_normal_asset(asset)["name"]: _normal_asset(asset) for asset in _asset_iter(external_assets)}
    resolved = []
    for manifest_entry in metadata.get("external_asset_manifest", []):
        name = manifest_entry["name"]
        decoded_entry = next(
            (
                entry
                for entry in decoded["external_files"]
                if entry["entry_id"] == manifest_entry["entry_id"]
                and entry["type"] == manifest_entry["type"]
                and entry["name"] == name
            ),
            None,
        )
        if decoded_entry is None:
            raise AsepriteUserDataError(
                "aseprite_external_file_entry_missing",
                "Aseprite External Files chunk is missing a required entry",
            )
        asset = provided.get(name)
        if asset is None:
            raise AsepriteUserDataError(
                "aseprite_external_asset_missing",
                f"external asset resolver did not provide asset: {name}",
            )
        payload_hash = _hash_text(asset.get("payload_text", ""))
        if payload_hash != manifest_entry["content_hash"] or asset.get("content_hash") != manifest_entry["content_hash"]:
            raise AsepriteUserDataError(
                "aseprite_external_asset_hash_mismatch",
                f"external asset hash mismatch for: {name}",
            )
        resolved.append(
            {
                "entry_id": manifest_entry["entry_id"],
                "type": manifest_entry["type"],
                "type_name": manifest_entry["type_name"],
                "name": name,
                "media_type": manifest_entry["media_type"],
                "content_hash": manifest_entry["content_hash"],
            }
        )
    return resolved


def _asset_iter(external_assets: list[dict] | dict):
    if isinstance(external_assets, dict):
        return list(external_assets.values())
    return list(external_assets)


def _normal_asset(asset: dict) -> dict:
    normalized = deepcopy(asset)
    if "payload_text" not in normalized and "payload" in normalized:
        normalized["payload_text"] = normalized["payload"]
    if "content_hash" not in normalized:
        normalized["content_hash"] = _hash_text(normalized.get("payload_text", ""))
    return normalized


def _palette_asset_text(grid: dict) -> str:
    lines = [
        "GIMP Palette",
        f"Name: {grid['grid_id']}",
        "Columns: 8",
        "# Deterministic Stage 0 Aseprite external palette reference.",
    ]
    for entry in _palette_semantics(grid):
        red, green, blue, _alpha = entry["rgba"]
        lines.append(f"{red:3d} {green:3d} {blue:3d}\t{entry['name']}")
    return "\n".join(lines) + "\n"


def _tileset_asset_payload(grid: dict, slip_profile: dict) -> dict:
    return {
        "asset_version": "mechagotchi.tileset_reference.v1",
        "grid_id": grid["grid_id"],
        "profile_id": slip_profile["profile_id"],
        "cell_count": len(grid.get("cells", [])),
        "grid_size": grid["grid_size"],
        "palette_id": grid.get("palette", {}).get("palette_id"),
        "organ_roles": sorted({cell.get("organ") for cell in grid.get("cells", [])}),
        "role_counts": _count_by_key(grid.get("cells", []), "role"),
        "organ_counts": _count_by_key(grid.get("cells", []), "organ"),
    }


def _resolver_asset_payload() -> dict:
    return {
        "resolver_version": "mechagotchi.aseprite_variant_resolver.v1",
        "policy": "deterministic_stage0_resolver",
        "variant_ids": [spec["variant_id"] for spec in VARIANT_SPECS],
        "supported_color_depths_bpp": [spec["color_depth_bpp"] for spec in VARIANT_SPECS],
        "claim_boundary": "hash-checked generated assets only; not arbitrary external asset resolution",
    }


def _count_by_key(items: list[dict], key: str) -> dict:
    counts = {}
    for item in items:
        value = item.get(key)
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _bytes_per_pixel(color_depth_bpp: int) -> int:
    if color_depth_bpp == 8:
        return 1
    if color_depth_bpp == 16:
        return 2
    if color_depth_bpp == 32:
        return 4
    raise AsepriteUserDataError(
        "aseprite_document_variant_color_depth_unsupported",
        "Stage 0 document-variant lab only supports 8, 16, and 32 bpp",
    )


def _variant_id_for_depth(color_depth_bpp: int) -> str:
    for spec in VARIANT_SPECS:
        if spec["color_depth_bpp"] == color_depth_bpp:
            return spec["variant_id"]
    _bytes_per_pixel(color_depth_bpp)
    return "unsupported"


def _external_type_name(entry_type: int) -> str:
    return {
        0: "external_palette",
        1: "external_tileset",
        2: "extension_properties",
        3: "extension_tile_management",
    }.get(entry_type, "unknown")


def _rewrite_chunks(project_bytes: bytes, keep) -> bytes:
    parsed = _parse_aseprite_any_depth(project_bytes)
    frames = []
    for frame in parsed["frames"]:
        frames.append(
            {
                "duration_ms": frame["duration_ms"],
                "chunks": [chunk for chunk in frame["chunks"] if keep(chunk)],
            }
        )
    return _write_aseprite(parsed["header"], frames)


def _map_chunks(project_bytes: bytes, mutate) -> bytes:
    parsed = _parse_aseprite_any_depth(project_bytes)
    frames = []
    for frame in parsed["frames"]:
        frames.append(
            {
                "duration_ms": frame["duration_ms"],
                "chunks": [mutate(chunk) for chunk in frame["chunks"]],
            }
        )
    return _write_aseprite(parsed["header"], frames)


def _tampered_cel_payload(data: bytes, bytes_per_pixel: int) -> bytes:
    prefix_size = struct.calcsize("<HhhBHh5s")
    layer_index, x, y, opacity, cel_type, z_index, reserved = struct.unpack(
        "<HhhBHh5s",
        data[:prefix_size],
    )
    if cel_type != 2:
        return data
    width, height = struct.unpack("<HH", data[prefix_size : prefix_size + 4])
    compressed = data[prefix_size + 4 :]
    raw = bytearray(zlib.decompress(compressed))
    if raw:
        raw[0] = (raw[0] + 1) % 256
    expected_length = width * height * bytes_per_pixel
    if len(raw) != expected_length:
        raise AsepriteUserDataError("aseprite_cel_payload_size_mismatch", "decoded ASE Cel payload size does not match dimensions")
    return (
        struct.pack("<HhhBHh5sHH", layer_index, x, y, opacity, cel_type, z_index, reserved, width, height)
        + zlib.compress(bytes(raw))
    )


def _invalid_probe_results(bundle: dict) -> list[dict]:
    reference = bundle["variants"][0]["project_bytes"]
    assets = bundle["external_assets"]
    return [
        _compact_import_result(
            import_aseprite_document_variant_project(strip_aseprite_variant_external_file_chunks(reference), assets)
        ),
        _compact_import_result(
            import_aseprite_document_variant_project(
                reference,
                tamper_aseprite_variant_external_asset_hash(assets),
            )
        ),
        _compact_import_result(
            import_aseprite_document_variant_project(tamper_aseprite_variant_color_depth(reference, 24), assets)
        ),
        _compact_import_result(
            import_aseprite_document_variant_project(tamper_aseprite_indexed_palette(reference), assets)
        ),
        _compact_import_result(
            import_aseprite_document_variant_project(tamper_aseprite_variant_pixel_payload(reference), assets)
        ),
        _compact_import_result(
            import_aseprite_document_variant_project(tamper_aseprite_document_variant_metadata(reference), assets)
        ),
        _compact_import_result(
            import_aseprite_document_variant_project(tamper_aseprite_document_variant_metadata_json(reference), assets)
        ),
    ]


def _cel_summary(cel: dict) -> dict:
    return {
        key: cel[key]
        for key in [
            "index",
            "frame_index",
            "layer_index",
            "x",
            "y",
            "opacity",
            "cel_type",
            "z_index",
            "width",
            "height",
            "bytes_per_pixel",
            "variant_pixel_hash",
        ]
    }


def _metadata_summary(metadata: dict) -> dict:
    return {
        key: metadata[key]
        for key in [
            "metadata_version",
            "format_id",
            "native_location",
            "writer_policy",
            "variant_id",
            "variant_ids",
            "color_depth_bpp",
            "bytes_per_pixel",
            "canonical_project_hash",
            "variant_pixel_hash",
            "variant_pixel_hashes",
            "indexed_palette_hash",
            "external_asset_manifest",
            "sidecar_hash",
        ]
    }


def _decoded_project_summary(decoded: dict) -> dict:
    keys = [
        "format_id",
        "magic",
        "frame_magic",
        "variant_id",
        "dimensions",
        "frame_count",
        "layer_count",
        "cel_count",
        "chunk_count",
        "external_files_chunk_count",
        "external_file_entry_count",
        "user_data_chunk_count",
        "palette_chunk_count",
        "palette_entry_count",
        "color_depth_bpp",
        "bytes_per_pixel",
        "variant_pixel_hash",
        "native_mechagotchi_semantics",
    ]
    return {key: decoded[key] for key in keys if key in decoded}


def _artifact_external_assets(external_assets: list[dict]) -> list[dict]:
    return [
        {
            "entry_id": asset["entry_id"],
            "type": asset["type"],
            "type_name": asset["type_name"],
            "name": asset["name"],
            "media_type": asset["media_type"],
            "content_hash": asset["content_hash"],
            "payload_text": asset["payload_text"],
        }
        for asset in external_assets
    ]


def _compact_import_result(result: dict) -> dict:
    return {
        "ok": result["ok"],
        "format_id": result.get("format_id"),
        "asset": result.get("asset"),
        "decoded_project": result.get("decoded_project"),
        "native_metadata": result.get("native_metadata"),
        "resolved_external_assets": result.get("resolved_external_assets", []),
        "project_policy": result.get("project_policy"),
        "semantic_fidelity": result.get("semantic_fidelity", 0.0),
        "errors": result.get("errors", []),
        "error_families": result.get("error_families", []),
    }


def _json_report(report: dict) -> dict:
    payload = deepcopy(report)
    for result in payload["document_variant_results"]:
        result.pop("project_bytes_hex", None)
        for asset in result.get("external_assets", []):
            asset.pop("payload_text", None)
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
                "document_variant_roundtrip_count",
                "document_variant_roundtrip_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "document_variant_summaries": [
            {
                "profile_id": result["profile_id"],
                "variant_id": result["variant_id"],
                "color_depth_bpp": result["color_depth_bpp"],
                "project_byte_count": result["project_byte_count"],
                "embedded_project_hash": result["embedded_project_hash"],
                "canonical_project_hash": result["canonical_project_hash"],
                "decoded_project": result["decoded_project"],
                "semantic_fidelity": result["semantic_fidelity"],
            }
            for result in json_report["document_variant_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# Aseprite Document Variant Resolution Stage 0\n\n"
        "Aseprite/LibreSprite document-variant proof for deterministic indexed "
        "8 bpp, grayscale-alpha 16 bpp, and RGBA 32 bpp compressed cels with "
        "hashed External Files Chunk asset resolution.\n\n"
        f"- Document variant round trips: {report['document_variant_roundtrip_success_count']}/"
        f"{report['document_variant_roundtrip_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}/"
        f"{report['invalid_probe_count']}\n"
        f"- Mean semantic fidelity: {metrics['mean_semantic_fidelity']}\n"
        f"- Variant pixel hash preservation rate: {metrics['variant_pixel_hash_preservation_rate']}\n"
        f"- External asset resolution rate: {metrics['external_asset_resolution_rate']}\n"
        f"- Live external editor verified: {str(metrics['live_external_editor_verified']).lower()}\n\n"
        "This artifact does not claim live external editor validation, arbitrary "
        "Aseprite schemas, arbitrary external asset resolution, package runtime "
        "integration, or full project-format coverage.\n"
    )


def _semantic_fidelity(diff: dict, source: dict) -> float:
    source_count = max(1, len(source.get("cells", [])))
    problem_count = (
        len(diff["changed_cells"])
        + len(diff["missing_cells"])
        + len(diff["added_cells"])
    )
    return round(max(0.0, 1.0 - problem_count / source_count), 6)


def _error(path: str, family: str, message: str | None = None) -> dict:
    return {
        "path": path,
        "family": family,
        "message": message or family.replace("_", " "),
    }


def _failed_import(path: str, family: str, message: str) -> dict:
    error = _error(path, family, message)
    return {
        "ok": False,
        "errors": [error],
        "error_families": [family],
    }


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/workshop_editor/aseprite_document_variant_resolution_stage0"),
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
    report = run_aseprite_document_variant_resolution_lab(profile_paths, args.generated_root)
    write_aseprite_document_variant_resolution_artifacts(args.output_dir, report)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_ASEPRITE_DOCUMENT_VARIANT_RESOLUTION = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(report["metrics"], indent=2))


if __name__ == "__main__":
    main()
