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

from aseprite_user_data_chunk_writer import (
    ASE_CHUNK_CEL,
    ASE_CHUNK_LAYER,
    ASE_CHUNK_USER_DATA,
    ASE_USER_DATA_PREFIX,
    AsepriteUserDataError,
    _chunk,
    _hash_bytes,
    _hash_payload,
    _hash_text,
    _pack_string,
    _parse_aseprite,
    _parse_cel_chunk,
    _parse_layer_chunk,
    _ratio,
    _unpack_string,
    _write_aseprite,
)
from external_metadata_sidecar import build_sidecar_for_grid, restore_grid_from_sidecar
from standard_image_sidecar_decoder import render_grid_rgba_pixels
from workshop_editor import compare_semantic_grid_fidelity


ASE_CHUNK_CEL_EXTRA = 0x2006
ASE_CHUNK_COLOR_PROFILE = 0x2007
ASE_CHUNK_EXTERNAL_FILES = 0x2008
ASE_EXTERNAL_PROPERTIES_VERSION = "mechagotchi.aseprite_external_properties.v1"
ASE_EXTERNAL_PROPERTIES_POLICY = "aseprite_external_properties_native_semantics"
ASE_EXTERNAL_PROPERTIES_NATIVE_LOCATION = (
    "frame[0].color_profile + frame[0].external_files + "
    "frame[0].layer.user_data.properties + frame[*].cel_extra"
)
REPORT_PATH = ROOT / "data/workshop_editor/aseprite_external_properties_semantics_stage0.json"
DATA_PATH = ROOT / "data/workshop_editor/aseprite_external_properties_semantics_data.js"


def export_aseprite_external_properties_project(grid: dict, slip_profile: dict) -> dict:
    canonical_project = _encode_aseprite_external_properties_project(
        grid,
        slip_profile,
        metadata=None,
    )
    canonical_hash = _hash_bytes(canonical_project)
    canonical_decoded = decode_aseprite_external_properties_project(canonical_project)
    asset = {
        "asset_id": f"{grid['grid_id']}_external_properties.aseprite",
        "format_id": "libresprite_project",
        "media_type": "application/octet-stream",
        "uri": f"generated://workshop/project-external-properties/{grid['grid_id']}.aseprite",
        "width": grid["grid_size"][0],
        "height": grid["grid_size"][1],
        "frame_count": 2,
        "content_hash": canonical_hash,
        "semantic_policy": ASE_EXTERNAL_PROPERTIES_POLICY,
    }
    sidecar = build_sidecar_for_grid(grid, slip_profile, asset)
    sidecar["sidecar_id"] = f"{grid['grid_id']}_aseprite_external_properties_sidecar"
    sidecar["asset_binding"]["semantic_policy"] = ASE_EXTERNAL_PROPERTIES_POLICY
    sidecar["project_binding"] = {
        "format_id": "libresprite_project",
        "decoder_scope": "aseprite_color_profile_external_files_user_data_properties_cel_extra_subset",
        "native_mechagotchi_semantics": True,
        "semantic_policy": ASE_EXTERNAL_PROPERTIES_POLICY,
        "native_metadata_version": ASE_EXTERNAL_PROPERTIES_VERSION,
    }
    sidecar["limitations"] = [
        "Stage 0 Aseprite/LibreSprite external-properties proof covers one Color Profile Chunk 0x2007, one External Files Chunk 0x2008, one User Data Chunk 0x2020 with property maps, and Cel Extra Chunk 0x2006 precise bounds.",
        "External file entries are deterministic references only; no external editor, palette file, tileset file, or extension package is executed by this lab.",
        "Live external editor rewrite validation is not verified by this lab.",
        "Arbitrary Aseprite project schemas, multiple color-depth documents, and full project-format coverage remain separate.",
    ]
    metadata = _build_external_properties_metadata(
        canonical_hash,
        grid,
        slip_profile,
        sidecar,
        canonical_decoded,
    )
    project_bytes = _encode_aseprite_external_properties_project(
        grid,
        slip_profile,
        metadata=metadata,
    )
    decoded = decode_aseprite_external_properties_project(project_bytes)
    return {
        "project_bytes": project_bytes,
        "canonical_project_bytes": canonical_project,
        "embedded_project_hash": _hash_bytes(project_bytes),
        "canonical_project_hash": canonical_hash,
        "metadata": metadata,
        "sidecar": sidecar,
        "decoded_project": decoded,
    }


def decode_aseprite_external_properties_project(project_bytes: bytes) -> dict:
    parsed = _parse_aseprite(project_bytes)
    color_profiles = []
    external_files = []
    layers = []
    cels = []
    cel_extras = []
    user_data_chunks = []
    property_maps = []
    native = False
    last_cel_index = None
    last_target = None
    total_chunk_count = 0

    for frame_index, frame in enumerate(parsed["frames"]):
        for chunk in frame["chunks"]:
            total_chunk_count += 1
            chunk_type = chunk["type"]
            if chunk_type == ASE_CHUNK_COLOR_PROFILE:
                color_profile = _parse_color_profile_chunk(chunk["data"])
                color_profile["frame_index"] = frame_index
                color_profiles.append(color_profile)
                last_target = {"target_type": "sprite", "target_name": "color_profile"}
            elif chunk_type == ASE_CHUNK_EXTERNAL_FILES:
                for entry in _parse_external_files_chunk(chunk["data"]):
                    entry["frame_index"] = frame_index
                    external_files.append(entry)
                last_target = {"target_type": "sprite", "target_name": "external_files"}
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
                cel = _parse_cel_chunk(
                    chunk["data"],
                    parsed["header"]["width"],
                    parsed["header"]["height"],
                )
                cel["index"] = len(cels)
                cel["frame_index"] = frame_index
                cels.append(cel)
                last_cel_index = cel["index"]
                last_target = {
                    "target_type": "cel",
                    "target_index": cel["index"],
                    "target_name": f"frame_{frame_index}_layer_{cel['layer_index']}",
                }
            elif chunk_type == ASE_CHUNK_CEL_EXTRA:
                cel_extra = _parse_cel_extra_chunk(chunk["data"])
                cel_extra["index"] = len(cel_extras)
                cel_extra["frame_index"] = frame_index
                cel_extra["target_cel_index"] = last_cel_index
                cel_extras.append(cel_extra)
                last_target = {
                    "target_type": "cel_extra",
                    "target_index": cel_extra["index"],
                    "target_name": f"cel_extra_{cel_extra['index']}",
                }
            elif chunk_type == ASE_CHUNK_USER_DATA:
                user_data = _parse_user_data_properties_chunk(chunk["data"])
                target = last_target or {
                    "target_type": "unknown",
                    "target_index": None,
                    "target_name": None,
                }
                text = user_data["text"]
                entry = {
                    "chunk_type": "0x2020",
                    "flags": user_data["flags"],
                    "text_present": text is not None,
                    "text_hash": _hash_text(text or ""),
                    "color_rgba": user_data["color"],
                    "property_map_count": len(user_data["property_maps"]),
                    "property_count": sum(len(item["properties"]) for item in user_data["property_maps"]),
                    "property_maps": user_data["property_maps"],
                    **target,
                }
                if isinstance(text, str) and text.startswith(ASE_USER_DATA_PREFIX):
                    try:
                        metadata = json.loads(text[len(ASE_USER_DATA_PREFIX) :])
                    except json.JSONDecodeError as exc:
                        raise AsepriteUserDataError("aseprite_external_properties_json_invalid", str(exc)) from exc
                    if metadata.get("metadata_version") == ASE_EXTERNAL_PROPERTIES_VERSION:
                        native = True
                user_data_chunks.append(entry)
                property_maps.extend(user_data["property_maps"])

    cel_hashes = _cel_hash_map(cels)
    return {
        "format_id": "libresprite_project",
        "magic": hex(parsed["header"]["magic"]),
        "frame_magic": hex(parsed["frames"][0]["magic"]) if parsed["frames"] else None,
        "dimensions": [parsed["header"]["width"], parsed["header"]["height"]],
        "frame_count": parsed["header"]["frames"],
        "chunk_count": total_chunk_count,
        "color_profile_chunk_count": len(color_profiles),
        "external_files_chunk_count": 1 if external_files else 0,
        "external_file_entry_count": len(external_files),
        "layer_count": len(layers),
        "cel_count": len(cels),
        "cel_extra_count": len(cel_extras),
        "user_data_chunk_count": len(user_data_chunks),
        "property_map_count": len(property_maps),
        "property_count": sum(len(item["properties"]) for item in property_maps),
        "color_depth_bpp": parsed["header"]["color_depth"],
        "first_frame_duration_ms": parsed["frames"][0]["duration_ms"] if parsed["frames"] else parsed["header"]["speed_ms"],
        "color_profile": color_profiles[0] if color_profiles else {},
        "color_profiles": color_profiles,
        "external_files": external_files,
        "layers": layers,
        "cels": [_cel_summary(cel) for cel in cels],
        "cel_visual_hashes": cel_hashes,
        "cel_extras": [_cel_extra_summary(entry) for entry in cel_extras],
        "cel_extra_semantics": [_cel_extra_semantic(entry) for entry in cel_extras],
        "user_data_chunks": user_data_chunks,
        "property_maps": property_maps,
        "native_mechagotchi_semantics": native,
    }


def extract_aseprite_external_properties_sidecar(project_bytes: bytes) -> dict:
    decoded = decode_aseprite_external_properties_project(project_bytes)
    metadata = _extract_external_properties_metadata(project_bytes)
    if metadata.get("metadata_version") != ASE_EXTERNAL_PROPERTIES_VERSION:
        raise AsepriteUserDataError(
            "aseprite_external_properties_version_unsupported",
            "unsupported Aseprite external-properties metadata version",
        )
    if metadata.get("format_id") != "libresprite_project":
        raise AsepriteUserDataError(
            "aseprite_external_properties_format_mismatch",
            "Aseprite external-properties metadata format id mismatch",
        )
    _validate_color_profile(decoded, metadata)
    _validate_external_files(decoded, metadata)
    _validate_property_maps(decoded, metadata)
    _validate_cel_extra(decoded, metadata)
    _validate_cel_hashes(decoded, metadata)

    sidecar = metadata.get("sidecar")
    if not isinstance(sidecar, dict):
        raise AsepriteUserDataError(
            "aseprite_external_properties_sidecar_missing",
            "Aseprite external-properties metadata must contain a sidecar object",
        )
    if _hash_payload(sidecar) != metadata.get("sidecar_hash"):
        raise AsepriteUserDataError(
            "aseprite_external_properties_sidecar_hash_mismatch",
            "Aseprite external-properties sidecar hash does not match the embedded sidecar",
        )
    canonical = strip_aseprite_external_properties_user_data_chunks(project_bytes)
    canonical_hash = _hash_bytes(canonical)
    if canonical_hash != metadata.get("canonical_project_hash"):
        raise AsepriteUserDataError(
            "aseprite_external_properties_canonical_hash_mismatch",
            "Aseprite external-properties canonical project hash does not match the stripped project",
        )
    if sidecar.get("asset_binding", {}).get("content_hash") != canonical_hash:
        raise AsepriteUserDataError(
            "aseprite_external_properties_sidecar_asset_hash_mismatch",
            "Aseprite external-properties sidecar asset hash does not match the canonical project hash",
        )
    return {
        "ok": True,
        "metadata": metadata,
        "sidecar": sidecar,
        "decoded_project": _decoded_project_summary(decoded),
        "canonical_project_hash": canonical_hash,
        "embedded_project_hash": _hash_bytes(project_bytes),
    }


def import_aseprite_external_properties_project(project_bytes: bytes, source_grid: dict | None = None) -> dict:
    try:
        extracted = extract_aseprite_external_properties_sidecar(project_bytes)
    except AsepriteUserDataError as exc:
        return _failed_import("aseprite_external_properties", exc.family, exc.message)

    sidecar = extracted["sidecar"]
    asset = deepcopy(sidecar["asset_binding"])
    try:
        restored = restore_grid_from_sidecar(sidecar, asset)
    except ValueError as exc:
        return _failed_import("sidecar", "aseprite_external_properties_sidecar_invalid", str(exc))

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
        "decoded_project": extracted["decoded_project"],
        "native_metadata": _metadata_summary(extracted["metadata"]),
        "restored_grid": restored,
        "restored_grid_validation": {
            "valid": grid_validation.ok,
            "errors": grid_validation.errors,
            "slip_aligned": alignment.ok,
            "slip_errors": alignment.errors,
        },
        "project_policy": {
            "semantic_policy": ASE_EXTERNAL_PROPERTIES_POLICY,
            "native_mechagotchi_semantics": True,
            "native_location": ASE_EXTERNAL_PROPERTIES_NATIVE_LOCATION,
            "color_profile_chunk_type": "0x2007",
            "external_files_chunk_type": "0x2008",
            "cel_extra_chunk_type": "0x2006",
            "properties_user_data_chunk_type": "0x2020",
            "external_property_map_key": 303,
            "live_external_editor_verified": False,
        },
        "semantic_diff": diff,
        "semantic_fidelity": fidelity,
        "errors": errors,
        "error_families": sorted({error["family"] for error in errors}),
    }


def strip_aseprite_external_properties_user_data_chunks(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    frames = []
    for frame in parsed["frames"]:
        frames.append(
            {
                "duration_ms": frame["duration_ms"],
                "chunks": [
                    chunk
                    for chunk in frame["chunks"]
                    if chunk["type"] != ASE_CHUNK_USER_DATA
                ],
            }
        )
    return _write_aseprite(parsed["header"], frames)


def strip_aseprite_external_file_chunks(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    frames = []
    for frame in parsed["frames"]:
        frames.append(
            {
                "duration_ms": frame["duration_ms"],
                "chunks": [
                    chunk
                    for chunk in frame["chunks"]
                    if chunk["type"] != ASE_CHUNK_EXTERNAL_FILES
                ],
            }
        )
    return _write_aseprite(parsed["header"], frames)


def strip_aseprite_user_data_properties(project_bytes: bytes) -> bytes:
    return _rewrite_first_external_properties_user_data(
        project_bytes,
        lambda user_data: _user_data_text_color_properties_data(
            user_data["text"],
            user_data["color"],
            [],
        ),
    )


def tamper_aseprite_color_profile_type(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    replaced = False
    frames = []
    for frame in parsed["frames"]:
        chunks = []
        for chunk in frame["chunks"]:
            if chunk["type"] == ASE_CHUNK_COLOR_PROFILE and not replaced:
                color_profile = _parse_color_profile_chunk(chunk["data"])
                color_profile["type"] = 0
                chunks.append(_chunk(ASE_CHUNK_COLOR_PROFILE, _color_profile_chunk_data(color_profile)))
                replaced = True
                continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    if not replaced:
        raise AsepriteUserDataError("aseprite_color_profile_missing", "no Color Profile Chunk found")
    return _write_aseprite(parsed["header"], frames)


def tamper_aseprite_extension_property_map_key(project_bytes: bytes) -> bytes:
    def replace(user_data: dict) -> bytes:
        maps = deepcopy(user_data["property_maps"])
        for item in maps:
            if item["map_key"] == 303:
                item["map_key"] = 404
                break
        return _user_data_text_color_properties_data(user_data["text"], user_data["color"], maps)

    return _rewrite_first_external_properties_user_data(project_bytes, replace)


def tamper_aseprite_cel_extra_precise_bounds(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    replaced = False
    frames = []
    for frame in parsed["frames"]:
        chunks = []
        for chunk in frame["chunks"]:
            if chunk["type"] == ASE_CHUNK_CEL_EXTRA and not replaced:
                cel_extra = _parse_cel_extra_chunk(chunk["data"])
                cel_extra["bounds"]["width"] = cel_extra["bounds"]["width"] + 1.0
                chunks.append(_chunk(ASE_CHUNK_CEL_EXTRA, _cel_extra_chunk_data(cel_extra["bounds"])))
                replaced = True
                continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    if not replaced:
        raise AsepriteUserDataError("aseprite_cel_extra_missing", "no Cel Extra Chunk found")
    return _write_aseprite(parsed["header"], frames)


def tamper_aseprite_external_properties_metadata(project_bytes: bytes) -> bytes:
    def replace(user_data: dict) -> bytes:
        text = user_data["text"]
        if not isinstance(text, str) or not text.startswith(ASE_USER_DATA_PREFIX):
            raise AsepriteUserDataError(
                "aseprite_external_properties_metadata_missing",
                "ASE project does not contain Mechagotchi external-properties metadata",
            )
        metadata = json.loads(text[len(ASE_USER_DATA_PREFIX) :])
        metadata["sidecar"]["sidecar_id"] = metadata["sidecar"]["sidecar_id"] + "_tampered"
        tampered_text = ASE_USER_DATA_PREFIX + json.dumps(metadata, sort_keys=True, separators=(",", ":"))
        return _user_data_text_color_properties_data(
            tampered_text,
            user_data["color"],
            user_data["property_maps"],
        )

    return _rewrite_first_external_properties_user_data(project_bytes, replace)


def tamper_aseprite_external_properties_metadata_json(project_bytes: bytes) -> bytes:
    def replace(user_data: dict) -> bytes:
        return _user_data_text_color_properties_data(
            ASE_USER_DATA_PREFIX + '{"metadata_version":',
            user_data["color"],
            user_data["property_maps"],
        )

    return _rewrite_first_external_properties_user_data(project_bytes, replace)


def run_aseprite_external_properties_semantics_lab(profile_paths: list[Path], generated_root: Path) -> dict:
    external_properties_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        exported = export_aseprite_external_properties_project(grid, profile)
        imported = import_aseprite_external_properties_project(exported["project_bytes"], source_grid=grid)
        diff = imported.get("semantic_diff", {"changed_cells": [], "missing_cells": [], "added_cells": []})
        external_properties_results.append(
            {
                "profile_id": profile["profile_id"],
                "profile_path": _portable(profile_path),
                "grid_path": _portable(grid_path),
                "format_id": "libresprite_project",
                "project_file_name": f"{profile['profile_id']}_external_properties.aseprite",
                "project_byte_count": len(exported["project_bytes"]),
                "embedded_project_hash": exported["embedded_project_hash"],
                "canonical_project_hash": exported["canonical_project_hash"],
                "metadata": _metadata_summary(exported["metadata"]),
                "native_sidecar": exported["sidecar"],
                "decoded_project": _decoded_project_summary(exported["decoded_project"]),
                "external_files": exported["metadata"]["external_file_semantics"],
                "color_profile": exported["metadata"]["color_profile_semantics"],
                "property_maps": exported["metadata"]["property_map_semantics"],
                "cel_extra_semantics": exported["metadata"]["cel_extra_semantics"],
                "import_result": _compact_import_result(imported),
                "restored_grid_validation": imported.get("restored_grid_validation"),
                "semantic_diff": diff,
                "semantic_fidelity": imported.get("semantic_fidelity", 0.0),
                "cel_visual_hashes_preserved": (
                    exported["decoded_project"]["cel_visual_hashes"]
                    == exported["metadata"]["cel_visual_hashes"]
                ),
                "property_maps_preserved": _property_maps_preserved(
                    exported["decoded_project"],
                    exported["metadata"],
                ),
                "project_bytes_hex": exported["project_bytes"].hex(),
            }
        )

    invalid_probe_results = _invalid_probe_results(external_properties_results[0])
    success_count = sum(1 for result in external_properties_results if result["import_result"]["ok"])
    invalid_rejected = sum(1 for result in invalid_probe_results if not result["ok"])
    visual_hash_preserved = sum(1 for result in external_properties_results if result["cel_visual_hashes_preserved"])
    properties_preserved = sum(1 for result in external_properties_results if result["property_maps_preserved"])
    return {
        "artifact_id": "aseprite_external_properties_semantics_stage0",
        "status": "research_aseprite_external_properties_semantics_no_package_code",
        "date": "2026-05-14",
        "purpose": (
            "Broaden Stage 0 Aseprite/LibreSprite chunk coverage beyond fixed "
            "visual and timeline carriers by proving Color Profile Chunk 0x2007, "
            "External Files Chunk 0x2008, User Data Chunk 0x2020 property maps, "
            "and Cel Extra Chunk 0x2006 precise bounds in a deterministic carrier."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
            "labs/workshop_editor/aseprite_external_properties_semantics.py",
        ],
        "external_anchors": [
            {
                "source": "Aseprite file-format specification",
                "url": "https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md",
                "used_for": "Color Profile Chunk 0x2007, External Files Chunk 0x2008, Cel Extra Chunk 0x2006, and User Data Chunk 0x2020 property-map layouts.",
            },
            {
                "source": "Aseprite properties API documentation",
                "url": "https://aseprite.org/api/properties",
                "used_for": "Workflow boundary for user-defined and extension-defined properties on sprite objects.",
            },
            {
                "source": "Aseprite color-profile documentation",
                "url": "https://www.aseprite.org/docs/color-profile/",
                "used_for": "Workflow boundary for color profiles saved inside .aseprite files.",
            },
            {
                "source": "Aseprite files documentation",
                "url": "https://www.aseprite.org/docs/files",
                "used_for": "Project-file boundary: .aseprite keeps sprite information intact but live editor open-save behavior is not proven by this lab.",
            },
            {
                "source": "LibreSprite GitHub",
                "url": "https://github.com/LibreSprite/LibreSprite",
                "used_for": "LibreSprite remains a compatibility boundary; no GPL editor code is embedded.",
            },
        ],
        "profile_count": len(external_properties_results),
        "external_properties_roundtrip_count": len(external_properties_results),
        "external_properties_roundtrip_success_count": success_count,
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected,
        "metrics": {
            "external_properties_roundtrip_success_rate": _ratio(success_count, len(external_properties_results)),
            "mean_semantic_fidelity": round(
                sum(result["semantic_fidelity"] for result in external_properties_results)
                / max(1, len(external_properties_results)),
                6,
            ),
            "cel_visual_hash_preservation_rate": _ratio(visual_hash_preserved, len(external_properties_results)),
            "property_map_preservation_rate": _ratio(properties_preserved, len(external_properties_results)),
            "invalid_probe_rejection_rate": _ratio(invalid_rejected, len(invalid_probe_results)),
            "live_external_editor_verified": False,
        },
        "external_properties_results": external_properties_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "aseprite_color_profile_subset",
            "aseprite_external_file_reference_subset",
            "aseprite_user_data_properties_subset",
            "aseprite_extension_property_map_subset",
            "aseprite_cel_extra_precise_bounds_subset",
            "aseprite_external_properties_hash_validation",
        ],
        "blocked_states": [
            "live_external_editor_rewrite_validation",
            "arbitrary_aseprite_project_schema_coverage",
            "multiple_aseprite_document_variants",
            "full_project_format_coverage",
            "package_runtime_lifecycle_integration",
            "manual_readability_calibration",
            "profile_weighted_evolution",
            "community_profile_packs",
        ],
        "decision": "prototype_aseprite_external_properties_native_semantics_subset",
        "next_research_step": (
            "Keep live external editor validation, arbitrary Aseprite schemas, "
            "multiple color-depth document variants, and full project-format "
            "coverage blocked until direct editor fixtures and broader schema "
            "tests exist."
        ),
    }


def write_aseprite_external_properties_semantics_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "aseprite_external_properties_semantics_stage0.json", _json_report(report))
    for result in report["external_properties_results"]:
        (output_dir / result["project_file_name"]).write_bytes(bytes.fromhex(result["project_bytes_hex"]))
    (output_dir / "aseprite_external_properties_semantics_data.js").write_text(
        "window.MECHAGOTCHI_ASEPRITE_EXTERNAL_PROPERTIES_SEMANTICS = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")


def _encode_aseprite_external_properties_project(grid: dict, slip_profile: dict, metadata: dict | None) -> bytes:
    width, height = grid["grid_size"]
    raw_rgba = _raw_rgba_for_grid(grid)
    frames = [
        {
            "duration_ms": 120,
            "chunks": [
                _chunk(ASE_CHUNK_COLOR_PROFILE, _color_profile_chunk_data(_color_profile_semantics())),
                _chunk(ASE_CHUNK_EXTERNAL_FILES, _external_files_chunk_data(_external_file_semantics(slip_profile))),
                _chunk(ASE_CHUNK_LAYER, _layer_chunk_data(width, height)),
            ],
        },
        {
            "duration_ms": 180,
            "chunks": [],
        },
    ]
    if metadata is not None:
        frames[0]["chunks"].append(
            _chunk(
                ASE_CHUNK_USER_DATA,
                _metadata_user_data_properties_chunk_data(
                    metadata,
                    _property_color_for_profile(slip_profile),
                    metadata["property_map_semantics"],
                ),
            )
        )
    frames[0]["chunks"].append(_chunk(ASE_CHUNK_CEL, _cel_chunk_data(0, width, height, raw_rgba, alpha_delta=0)))
    frames[0]["chunks"].append(_chunk(ASE_CHUNK_CEL_EXTRA, _cel_extra_chunk_data(_cel_extra_bounds(width, height, 0))))
    frames[1]["chunks"].append(_chunk(ASE_CHUNK_CEL, _cel_chunk_data(0, width, height, raw_rgba, alpha_delta=-31)))
    frames[1]["chunks"].append(_chunk(ASE_CHUNK_CEL_EXTRA, _cel_extra_chunk_data(_cel_extra_bounds(width, height, 1))))
    header = {
        "frames": 2,
        "width": width,
        "height": height,
        "color_depth": 32,
        "flags": 1,
        "speed_ms": 120,
        "transparent_index": 0,
        "color_count": 0,
        "pixel_width": 1,
        "pixel_height": 1,
        "grid_x": 0,
        "grid_y": 0,
        "grid_width": width,
        "grid_height": height,
    }
    return _write_aseprite(header, frames)


def _layer_chunk_data(width: int, height: int) -> bytes:
    return (
        struct.pack("<HHHHHHB3s", 3, 0, 0, width, height, 0, 255, b"\x00\x00\x00")
        + _pack_string("Mechagotchi external properties layer")
    )


def _cel_chunk_data(layer_index: int, width: int, height: int, raw_rgba: bytes, alpha_delta: int) -> bytes:
    expected_length = width * height * 4
    if len(raw_rgba) != expected_length:
        raise ValueError("raw RGBA payload does not match dimensions")
    payload = bytearray(raw_rgba)
    if alpha_delta:
        for offset in range(3, len(payload), 4):
            payload[offset] = max(0, min(255, payload[offset] + alpha_delta))
    return (
        struct.pack("<HhhBHh5sHH", layer_index, 0, 0, 255, 2, 0, b"\x00" * 5, width, height)
        + zlib.compress(bytes(payload))
    )


def _color_profile_chunk_data(color_profile: dict) -> bytes:
    return struct.pack(
        "<HHI8s",
        color_profile["type"],
        color_profile["flags"],
        _pack_fixed(color_profile["fixed_gamma"]),
        b"\x00" * 8,
    )


def _parse_color_profile_chunk(data: bytes) -> dict:
    minimum = struct.calcsize("<HHI8s")
    if len(data) < minimum:
        raise AsepriteUserDataError("aseprite_color_profile_truncated", "ASE Color Profile chunk is truncated")
    profile_type, flags, fixed_gamma, _reserved = struct.unpack("<HHI8s", data[:minimum])
    offset = minimum
    icc_profile_hash = None
    icc_profile_byte_count = 0
    if profile_type == 2:
        if offset + 4 > len(data):
            raise AsepriteUserDataError("aseprite_color_profile_icc_truncated", "ASE ICC color profile length is truncated")
        icc_profile_byte_count = struct.unpack("<I", data[offset : offset + 4])[0]
        offset += 4
        end = offset + icc_profile_byte_count
        if end > len(data):
            raise AsepriteUserDataError("aseprite_color_profile_icc_truncated", "ASE ICC color profile payload is truncated")
        icc_profile_hash = _hash_bytes(data[offset:end])
        offset = end
    if offset != len(data):
        raise AsepriteUserDataError("aseprite_color_profile_extra_bytes", "unexpected bytes after Color Profile chunk")
    return {
        "chunk_type": "0x2007",
        "type": profile_type,
        "flags": flags,
        "fixed_gamma": _unpack_fixed(fixed_gamma),
        "icc_profile_byte_count": icc_profile_byte_count,
        "icc_profile_hash": icc_profile_hash,
    }


def _external_files_chunk_data(entries: list[dict]) -> bytes:
    payload = bytearray(struct.pack("<I8s", len(entries), b"\x00" * 8))
    for entry in entries:
        payload.extend(struct.pack("<IB7s", entry["entry_id"], entry["type"], b"\x00" * 7))
        payload.extend(_pack_string(entry["name"]))
    return bytes(payload)


def _parse_external_files_chunk(data: bytes) -> list[dict]:
    minimum = struct.calcsize("<I8s")
    if len(data) < minimum:
        raise AsepriteUserDataError("aseprite_external_files_truncated", "ASE External Files chunk is truncated")
    count, _reserved = struct.unpack("<I8s", data[:minimum])
    offset = minimum
    entries = []
    entry_header_size = struct.calcsize("<IB7s")
    for _ in range(count):
        if offset + entry_header_size > len(data):
            raise AsepriteUserDataError("aseprite_external_file_entry_truncated", "ASE External Files entry is truncated")
        entry_id, entry_type, _entry_reserved = struct.unpack("<IB7s", data[offset : offset + entry_header_size])
        offset += entry_header_size
        name, offset = _unpack_string(data, offset)
        entries.append(
            {
                "chunk_type": "0x2008",
                "entry_id": entry_id,
                "type": entry_type,
                "type_name": _external_file_type_name(entry_type),
                "name": name,
            }
        )
    if offset != len(data):
        raise AsepriteUserDataError("aseprite_external_files_extra_bytes", "unexpected bytes after External Files chunk")
    return entries


def _cel_extra_chunk_data(bounds: dict) -> bytes:
    return struct.pack(
        "<IIIII16s",
        1,
        _pack_fixed(bounds["x"]),
        _pack_fixed(bounds["y"]),
        _pack_fixed(bounds["width"]),
        _pack_fixed(bounds["height"]),
        b"\x00" * 16,
    )


def _parse_cel_extra_chunk(data: bytes) -> dict:
    minimum = struct.calcsize("<IIIII16s")
    if len(data) != minimum:
        raise AsepriteUserDataError("aseprite_cel_extra_size_invalid", "ASE Cel Extra chunk size is invalid")
    flags, x, y, width, height, _reserved = struct.unpack("<IIIII16s", data)
    return {
        "chunk_type": "0x2006",
        "flags": flags,
        "bounds": {
            "x": _unpack_fixed(x),
            "y": _unpack_fixed(y),
            "width": _unpack_fixed(width),
            "height": _unpack_fixed(height),
        },
    }


def _metadata_user_data_properties_chunk_data(metadata: dict, color_rgba: list[int], property_maps: list[dict]) -> bytes:
    text = ASE_USER_DATA_PREFIX + json.dumps(metadata, sort_keys=True, separators=(",", ":"))
    return _user_data_text_color_properties_data(text, color_rgba, property_maps)


def _user_data_text_color_properties_data(
    text: str | None,
    color_rgba: list[int] | None,
    property_maps: list[dict],
) -> bytes:
    flags = 1
    if color_rgba is not None:
        flags |= 2
    if property_maps:
        flags |= 4
    payload = bytearray(struct.pack("<I", flags))
    payload.extend(_pack_string(text or ""))
    if color_rgba is not None:
        payload.extend(bytes(color_rgba))
    if property_maps:
        maps_payload = _property_maps_payload(property_maps)
        payload.extend(struct.pack("<II", len(maps_payload) + 8, len(property_maps)))
        payload.extend(maps_payload)
    return bytes(payload)


def _property_maps_payload(property_maps: list[dict]) -> bytes:
    payload = bytearray()
    for item in property_maps:
        payload.extend(struct.pack("<II", item["map_key"], len(item["properties"])))
        payload.extend(_property_entries_payload(item["properties"]))
    return bytes(payload)


def _property_entries_payload(properties: list[dict]) -> bytes:
    payload = bytearray()
    for prop in properties:
        type_id = _property_type_id(prop["type"])
        payload.extend(_pack_string(prop["name"]))
        payload.extend(struct.pack("<H", type_id))
        payload.extend(_property_value_payload(type_id, prop["value"]))
    return bytes(payload)


def _property_value_payload(type_id: int, value: object) -> bytes:
    if type_id == 0x0001:
        return struct.pack("<B", 1 if value else 0)
    if type_id == 0x0007:
        return struct.pack("<I", int(value))
    if type_id == 0x000B:
        return struct.pack("<f", float(value))
    if type_id == 0x000D:
        return _pack_string(str(value))
    if type_id == 0x000E:
        return struct.pack("<ll", int(value["x"]), int(value["y"]))
    if type_id == 0x000F:
        return struct.pack("<ll", int(value["width"]), int(value["height"]))
    if type_id == 0x0010:
        return struct.pack(
            "<llll",
            int(value["x"]),
            int(value["y"]),
            int(value["width"]),
            int(value["height"]),
        )
    if type_id == 0x0012:
        nested = [
            {"name": key, "type": "float", "value": nested_value}
            for key, nested_value in sorted(value.items())
        ]
        return struct.pack("<I", len(nested)) + _property_entries_payload(nested)
    raise AsepriteUserDataError(
        "aseprite_property_type_unsupported",
        f"unsupported Aseprite property type: {hex(type_id)}",
    )


def _parse_user_data_properties_chunk(data: bytes) -> dict:
    if len(data) < 4:
        raise AsepriteUserDataError("aseprite_user_data_chunk_truncated", "ASE User Data chunk is truncated")
    flags = struct.unpack("<I", data[:4])[0]
    offset = 4
    text = None
    color = None
    property_maps = []
    if flags & 1:
        text, offset = _unpack_string(data, offset)
    if flags & 2:
        if offset + 4 > len(data):
            raise AsepriteUserDataError("aseprite_user_data_color_truncated", "ASE User Data color is truncated")
        color = list(data[offset : offset + 4])
        offset += 4
    if flags & 4:
        if offset + 8 > len(data):
            raise AsepriteUserDataError("aseprite_user_data_properties_truncated", "ASE User Data properties header is truncated")
        property_size, map_count = struct.unpack("<II", data[offset : offset + 8])
        if property_size < 8:
            raise AsepriteUserDataError("aseprite_user_data_properties_size_invalid", "ASE User Data properties size is invalid")
        property_end = offset + property_size
        if property_end > len(data):
            raise AsepriteUserDataError("aseprite_user_data_properties_truncated", "ASE User Data properties payload is truncated")
        offset += 8
        for _ in range(map_count):
            if offset + 8 > property_end:
                raise AsepriteUserDataError("aseprite_property_map_truncated", "ASE property map is truncated")
            map_key, property_count = struct.unpack("<II", data[offset : offset + 8])
            offset += 8
            properties, offset = _parse_property_entries(data, offset, property_count, property_end)
            property_maps.append({"map_key": map_key, "properties": properties})
        if offset != property_end:
            raise AsepriteUserDataError("aseprite_user_data_properties_extra_bytes", "unexpected bytes after ASE property maps")
    if flags & ~0x07:
        raise AsepriteUserDataError("aseprite_user_data_flags_unsupported", "unsupported ASE User Data flags")
    if offset != len(data):
        raise AsepriteUserDataError("aseprite_user_data_extra_bytes", "unexpected bytes after ASE User Data chunk")
    return {
        "flags": flags,
        "text": text,
        "color": color,
        "property_maps": property_maps,
    }


def _parse_property_entries(data: bytes, offset: int, property_count: int, limit: int) -> tuple[list[dict], int]:
    properties = []
    for _ in range(property_count):
        name, offset = _unpack_string(data, offset)
        if offset + 2 > limit:
            raise AsepriteUserDataError("aseprite_property_type_truncated", "ASE property type is truncated")
        type_id = struct.unpack("<H", data[offset : offset + 2])[0]
        offset += 2
        value, offset = _parse_property_value(data, offset, type_id, limit)
        properties.append(
            {
                "name": name,
                "type": _property_type_name(type_id),
                "value": value,
            }
        )
    return properties, offset


def _parse_property_value(data: bytes, offset: int, type_id: int, limit: int) -> tuple[object, int]:
    if type_id == 0x0001:
        _require_bytes(offset, 1, limit, "aseprite_property_bool_truncated")
        return data[offset] != 0, offset + 1
    if type_id == 0x0007:
        _require_bytes(offset, 4, limit, "aseprite_property_uint32_truncated")
        return struct.unpack("<I", data[offset : offset + 4])[0], offset + 4
    if type_id == 0x000B:
        _require_bytes(offset, 4, limit, "aseprite_property_float_truncated")
        return round(struct.unpack("<f", data[offset : offset + 4])[0], 6), offset + 4
    if type_id == 0x000D:
        return _unpack_string(data, offset)
    if type_id == 0x000E:
        _require_bytes(offset, 8, limit, "aseprite_property_point_truncated")
        x, y = struct.unpack("<ll", data[offset : offset + 8])
        return {"x": x, "y": y}, offset + 8
    if type_id == 0x000F:
        _require_bytes(offset, 8, limit, "aseprite_property_size_truncated")
        width, height = struct.unpack("<ll", data[offset : offset + 8])
        return {"width": width, "height": height}, offset + 8
    if type_id == 0x0010:
        _require_bytes(offset, 16, limit, "aseprite_property_rect_truncated")
        x, y, width, height = struct.unpack("<llll", data[offset : offset + 16])
        return {"x": x, "y": y, "width": width, "height": height}, offset + 16
    if type_id == 0x0012:
        _require_bytes(offset, 4, limit, "aseprite_property_nested_map_truncated")
        nested_count = struct.unpack("<I", data[offset : offset + 4])[0]
        nested_properties, offset = _parse_property_entries(data, offset + 4, nested_count, limit)
        return {item["name"]: item["value"] for item in nested_properties}, offset
    raise AsepriteUserDataError(
        "aseprite_property_type_unsupported",
        f"unsupported Aseprite property type: {hex(type_id)}",
    )


def _rewrite_first_external_properties_user_data(project_bytes: bytes, replace) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    replaced = False
    frames = []
    for frame in parsed["frames"]:
        chunks = []
        for chunk in frame["chunks"]:
            if chunk["type"] == ASE_CHUNK_USER_DATA and not replaced:
                user_data = _parse_user_data_properties_chunk(chunk["data"])
                text = user_data["text"]
                if isinstance(text, str) and text.startswith(ASE_USER_DATA_PREFIX):
                    metadata = json.loads(text[len(ASE_USER_DATA_PREFIX) :])
                    if metadata.get("metadata_version") == ASE_EXTERNAL_PROPERTIES_VERSION:
                        chunks.append(_chunk(ASE_CHUNK_USER_DATA, replace(user_data)))
                        replaced = True
                        continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    if not replaced:
        raise AsepriteUserDataError(
            "aseprite_external_properties_metadata_missing",
            "ASE project does not contain Mechagotchi external-properties metadata",
        )
    return _write_aseprite(parsed["header"], frames)


def _extract_external_properties_metadata(project_bytes: bytes) -> dict:
    parsed = _parse_aseprite(project_bytes)
    for frame in parsed["frames"]:
        for chunk in frame["chunks"]:
            if chunk["type"] != ASE_CHUNK_USER_DATA:
                continue
            user_data = _parse_user_data_properties_chunk(chunk["data"])
            text = user_data["text"]
            if isinstance(text, str) and text.startswith(ASE_USER_DATA_PREFIX):
                try:
                    metadata = json.loads(text[len(ASE_USER_DATA_PREFIX) :])
                except json.JSONDecodeError as exc:
                    raise AsepriteUserDataError("aseprite_external_properties_json_invalid", str(exc)) from exc
                if metadata.get("metadata_version") == ASE_EXTERNAL_PROPERTIES_VERSION:
                    return metadata
    raise AsepriteUserDataError(
        "aseprite_external_properties_metadata_missing",
        "ASE project does not contain Mechagotchi external-properties User Data metadata",
    )


def _validate_color_profile(decoded: dict, metadata: dict) -> None:
    if decoded["color_profile_chunk_count"] != 1:
        raise AsepriteUserDataError(
            "aseprite_color_profile_missing",
            "Aseprite external-properties project must contain one Color Profile Chunk 0x2007",
        )
    current = _color_profile_semantic(decoded["color_profile"])
    expected = metadata.get("color_profile_semantics")
    if current != expected:
        raise AsepriteUserDataError(
            "aseprite_color_profile_mismatch",
            "Aseprite Color Profile chunk does not match embedded metadata",
        )


def _validate_external_files(decoded: dict, metadata: dict) -> None:
    if decoded["external_file_entry_count"] < 1:
        raise AsepriteUserDataError(
            "aseprite_external_files_missing",
            "Aseprite external-properties project must contain External Files Chunk 0x2008 entries",
        )
    current = [
        {key: entry[key] for key in ["entry_id", "type", "type_name", "name"]}
        for entry in decoded["external_files"]
    ]
    expected = metadata.get("external_file_semantics")
    if current != expected:
        raise AsepriteUserDataError(
            "aseprite_external_files_mismatch",
            "Aseprite External Files entries do not match embedded metadata",
        )


def _validate_property_maps(decoded: dict, metadata: dict) -> None:
    expected = metadata.get("property_map_semantics", [])
    if decoded["property_map_count"] != len(expected):
        raise AsepriteUserDataError(
            "aseprite_user_data_properties_missing",
            "Aseprite User Data Chunk 0x2020 must contain the expected property maps",
        )
    current_keys = {item["map_key"] for item in decoded["property_maps"]}
    if 303 not in current_keys:
        raise AsepriteUserDataError(
            "aseprite_extension_property_map_missing",
            "Aseprite User Data properties must include the extension property-map key from External Files",
        )
    if decoded["property_maps"] != expected:
        expected_keys = {item["map_key"] for item in expected}
        if expected_keys != current_keys:
            raise AsepriteUserDataError(
                "aseprite_extension_property_map_missing",
                "Aseprite User Data property-map keys do not match embedded metadata",
            )
        raise AsepriteUserDataError(
            "aseprite_user_data_properties_mismatch",
            "Aseprite User Data properties do not match embedded metadata",
        )


def _validate_cel_extra(decoded: dict, metadata: dict) -> None:
    if decoded["cel_extra_count"] != len(metadata.get("cel_extra_semantics", [])):
        raise AsepriteUserDataError(
            "aseprite_cel_extra_missing",
            "Aseprite external-properties project must contain Cel Extra Chunk 0x2006 entries",
        )
    if decoded["cel_extra_semantics"] != metadata.get("cel_extra_semantics"):
        raise AsepriteUserDataError(
            "aseprite_cel_extra_precise_bounds_mismatch",
            "Aseprite Cel Extra precise bounds do not match embedded metadata",
        )


def _validate_cel_hashes(decoded: dict, metadata: dict) -> None:
    if decoded["cel_visual_hashes"] != metadata.get("cel_visual_hashes"):
        raise AsepriteUserDataError(
            "aseprite_external_properties_visual_hash_mismatch",
            "Aseprite external-properties cel visual hashes do not match current cel payloads",
        )


def _build_external_properties_metadata(
    canonical_hash: str,
    grid: dict,
    slip_profile: dict,
    sidecar: dict,
    decoded: dict,
) -> dict:
    return {
        "metadata_version": ASE_EXTERNAL_PROPERTIES_VERSION,
        "format_id": "libresprite_project",
        "native_location": ASE_EXTERNAL_PROPERTIES_NATIVE_LOCATION,
        "writer_policy": ASE_EXTERNAL_PROPERTIES_POLICY,
        "canonical_project_hash": canonical_hash,
        "cel_visual_hashes": decoded["cel_visual_hashes"],
        "sidecar_hash": _hash_payload(sidecar),
        "sidecar": sidecar,
        "color_profile_semantics": _color_profile_semantics(),
        "external_file_semantics": _external_file_semantics(slip_profile),
        "property_map_semantics": _property_map_semantics(grid, slip_profile),
        "cel_extra_semantics": decoded["cel_extra_semantics"],
    }


def _color_profile_semantics() -> dict:
    return {
        "type": 1,
        "type_name": "srgb",
        "flags": 1,
        "fixed_gamma": 1.0,
    }


def _color_profile_semantic(color_profile: dict) -> dict:
    return {
        "type": color_profile.get("type"),
        "type_name": "srgb" if color_profile.get("type") == 1 else "other",
        "flags": color_profile.get("flags"),
        "fixed_gamma": color_profile.get("fixed_gamma"),
    }


def _external_file_semantics(slip_profile: dict) -> list[dict]:
    profile_id = slip_profile["profile_id"]
    return [
        {
            "entry_id": 101,
            "type": 0,
            "type_name": "external_palette",
            "name": f"palettes/{profile_id}.gpl",
        },
        {
            "entry_id": 202,
            "type": 1,
            "type_name": "external_tileset",
            "name": f"tilesets/{profile_id}.aseprite",
        },
        {
            "entry_id": 303,
            "type": 2,
            "type_name": "extension_properties",
            "name": "mechagotchi/slip-properties",
        },
    ]


def _property_map_semantics(grid: dict, slip_profile: dict) -> list[dict]:
    width, height = grid["grid_size"]
    body_mass = len(grid.get("cells", []))
    sensor_anchor = _first_organ_coordinate(grid, "sensors")
    return [
        {
            "map_key": 0,
            "properties": [
                {"name": "profile_id", "type": "string", "value": slip_profile["profile_id"]},
                {"name": "semantic_policy", "type": "string", "value": ASE_EXTERNAL_PROPERTIES_POLICY},
                {"name": "body_mass", "type": "uint32", "value": body_mass},
                {"name": "grid_size", "type": "size", "value": {"width": width, "height": height}},
                {"name": "sensor_anchor", "type": "point", "value": sensor_anchor},
            ],
        },
        {
            "map_key": 303,
            "properties": [
                {"name": "slip_alignment_required", "type": "bool", "value": True},
                {"name": "external_palette_entry_id", "type": "uint32", "value": 101},
                {"name": "external_tileset_entry_id", "type": "uint32", "value": 202},
                {
                    "name": "semantic_bounds",
                    "type": "rect",
                    "value": {"x": 0, "y": 0, "width": width, "height": height},
                },
                {
                    "name": "mutation_caps",
                    "type": "nested_map",
                    "value": {
                        key: round(float(value), 6)
                        for key, value in slip_profile["mutation"].items()
                    },
                },
            ],
        },
    ]


def _property_type_id(type_name: str) -> int:
    return {
        "bool": 0x0001,
        "uint32": 0x0007,
        "float": 0x000B,
        "string": 0x000D,
        "point": 0x000E,
        "size": 0x000F,
        "rect": 0x0010,
        "nested_map": 0x0012,
    }[type_name]


def _property_type_name(type_id: int) -> str:
    return {
        0x0001: "bool",
        0x0007: "uint32",
        0x000B: "float",
        0x000D: "string",
        0x000E: "point",
        0x000F: "size",
        0x0010: "rect",
        0x0012: "nested_map",
    }.get(type_id, f"unknown_{type_id:#06x}")


def _external_file_type_name(entry_type: int) -> str:
    return {
        0: "external_palette",
        1: "external_tileset",
        2: "extension_properties",
        3: "extension_tile_management",
    }.get(entry_type, "unknown")


def _cel_extra_bounds(width: int, height: int, frame_index: int) -> dict:
    if frame_index == 0:
        return {"x": 0.0, "y": 0.0, "width": float(width), "height": float(height)}
    return {"x": 0.5, "y": 0.5, "width": float(width) - 1.0, "height": float(height) - 1.0}


def _cel_extra_semantic(entry: dict) -> dict:
    return {
        "frame_index": entry["frame_index"],
        "target_cel_index": entry["target_cel_index"],
        "flags": entry["flags"],
        "bounds": entry["bounds"],
    }


def _cel_extra_summary(entry: dict) -> dict:
    summary = _cel_extra_semantic(entry)
    summary["chunk_type"] = entry["chunk_type"]
    summary["index"] = entry["index"]
    return summary


def _raw_rgba_for_grid(grid: dict) -> bytes:
    return bytes(channel for pixel in render_grid_rgba_pixels(grid) for channel in pixel)


def _cel_hash_map(cels: list[dict]) -> dict:
    return {
        f"frame_{cel['frame_index']}_layer_{cel['layer_index']}": cel["cel_visual_hash"]
        for cel in cels
    }


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
            "cel_visual_hash",
        ]
    }


def _property_color_for_profile(slip_profile: dict) -> list[int]:
    colors = {
        "slip_lcd_seed": [93, 187, 99, 255],
        "slip_gray_stable": [156, 164, 148, 255],
        "slip_amber_social": [255, 196, 87, 255],
    }
    return colors.get(slip_profile["profile_id"], [255, 255, 255, 255])


def _first_organ_coordinate(grid: dict, organ: str) -> dict:
    for cell in grid.get("cells", []):
        if cell.get("organ") == organ:
            return {"x": int(cell["x"]), "y": int(cell["y"])}
    return {"x": 0, "y": 0}


def _property_maps_preserved(decoded: dict, metadata: dict) -> bool:
    return decoded["property_maps"] == metadata["property_map_semantics"]


def _invalid_probe_results(reference_result: dict) -> list[dict]:
    project_bytes = bytes.fromhex(reference_result["project_bytes_hex"])
    return [
        _compact_import_result(import_aseprite_external_properties_project(strip_aseprite_external_file_chunks(project_bytes))),
        _compact_import_result(import_aseprite_external_properties_project(tamper_aseprite_color_profile_type(project_bytes))),
        _compact_import_result(import_aseprite_external_properties_project(strip_aseprite_user_data_properties(project_bytes))),
        _compact_import_result(import_aseprite_external_properties_project(tamper_aseprite_extension_property_map_key(project_bytes))),
        _compact_import_result(import_aseprite_external_properties_project(tamper_aseprite_cel_extra_precise_bounds(project_bytes))),
        _compact_import_result(import_aseprite_external_properties_project(tamper_aseprite_external_properties_metadata(project_bytes))),
        _compact_import_result(import_aseprite_external_properties_project(tamper_aseprite_external_properties_metadata_json(project_bytes))),
    ]


def _metadata_summary(metadata: dict) -> dict:
    return {
        key: metadata[key]
        for key in [
            "metadata_version",
            "format_id",
            "native_location",
            "writer_policy",
            "canonical_project_hash",
            "sidecar_hash",
        ]
    }


def _decoded_project_summary(decoded: dict) -> dict:
    keys = [
        "format_id",
        "magic",
        "frame_magic",
        "dimensions",
        "frame_count",
        "chunk_count",
        "color_profile_chunk_count",
        "external_file_entry_count",
        "layer_count",
        "cel_count",
        "cel_extra_count",
        "user_data_chunk_count",
        "property_map_count",
        "property_count",
        "color_depth_bpp",
        "native_mechagotchi_semantics",
    ]
    return {key: decoded[key] for key in keys if key in decoded}


def _compact_import_result(result: dict) -> dict:
    return {
        "ok": result["ok"],
        "format_id": result.get("format_id"),
        "asset": result.get("asset"),
        "decoded_project": result.get("decoded_project"),
        "native_metadata": result.get("native_metadata"),
        "project_policy": result.get("project_policy"),
        "semantic_fidelity": result.get("semantic_fidelity", 0.0),
        "errors": result.get("errors", []),
        "error_families": result.get("error_families", []),
    }


def _json_report(report: dict) -> dict:
    payload = deepcopy(report)
    for result in payload["external_properties_results"]:
        result.pop("project_bytes_hex", None)
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
                "external_properties_roundtrip_count",
                "external_properties_roundtrip_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "external_properties_summaries": [
            {
                "profile_id": result["profile_id"],
                "format_id": result["format_id"],
                "project_byte_count": result["project_byte_count"],
                "embedded_project_hash": result["embedded_project_hash"],
                "canonical_project_hash": result["canonical_project_hash"],
                "decoded_project": result["decoded_project"],
                "semantic_fidelity": result["semantic_fidelity"],
            }
            for result in json_report["external_properties_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# Aseprite External Properties Semantics Stage 0\n\n"
        "Aseprite/LibreSprite external file, color-profile, property-map, "
        "and Cel Extra semantic proof for one fixed two-frame carrier.\n\n"
        f"- External-properties round trips: {report['external_properties_roundtrip_success_count']}/"
        f"{report['external_properties_roundtrip_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}/"
        f"{report['invalid_probe_count']}\n"
        f"- Mean semantic fidelity: {metrics['mean_semantic_fidelity']}\n"
        f"- Cel visual hash preservation rate: {metrics['cel_visual_hash_preservation_rate']}\n"
        f"- Property map preservation rate: {metrics['property_map_preservation_rate']}\n"
        f"- Live external editor verified: {metrics['live_external_editor_verified']}\n\n"
        "This artifact does not claim live external editor validation, "
        "arbitrary Aseprite schemas, package runtime integration, or full "
        "project-format coverage.\n"
    )


def _pack_fixed(value: float) -> int:
    return int(round(float(value) * 65536))


def _unpack_fixed(value: int) -> float:
    return round(value / 65536, 6)


def _require_bytes(offset: int, length: int, limit: int, family: str) -> None:
    if offset + length > limit:
        raise AsepriteUserDataError(family, family.replace("_", " "))


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
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "data/workshop_editor/aseprite_external_properties_semantics_stage0",
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
    report = run_aseprite_external_properties_semantics_lab(profile_paths, args.generated_root)
    write_aseprite_external_properties_semantics_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_ASEPRITE_EXTERNAL_PROPERTIES_SEMANTICS = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(_json_report(report), indent=2))


if __name__ == "__main__":
    main()
