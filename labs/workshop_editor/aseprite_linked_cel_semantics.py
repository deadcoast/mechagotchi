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

from aseprite_palette_slice_semantics import (
    ASE_CHUNK_PALETTE,
    ASE_CHUNK_SLICE,
    ASE_PALETTE_SLICE_VERSION,
    _palette_chunk_data,
    _palette_semantics,
    _parse_palette_chunk,
    _parse_slice_chunk,
    _slice_chunk_data,
    _slice_semantics,
    _validate_palette,
    _validate_slices,
)
from aseprite_tags_layers_semantics import (
    ASE_CHUNK_TAGS,
    _cel_chunk_data,
    _layer_chunk_data,
    _layer_semantics,
    _parse_tags_chunk,
    _raw_rgba_for_layer,
    _tag_semantics,
    _tags_chunk_data,
    _validate_layers,
    _validate_tags,
)
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
    _parse_aseprite,
    _parse_layer_chunk,
    _parse_user_data_chunk,
    _ratio,
    _user_data_chunk_data,
    _write_aseprite,
)
from external_metadata_sidecar import build_sidecar_for_grid, restore_grid_from_sidecar
from workshop_editor import compare_semantic_grid_fidelity


ASE_LINKED_CEL_VERSION = "mechagotchi.aseprite_linked_cel.v1"
ASE_LINKED_CEL_POLICY = "aseprite_linked_cel_native_semantics"
ASE_LINKED_CEL_NATIVE_LOCATION = (
    "frame[0].palette + frame[0].slices + frame[*].linked_cels + "
    "frame[0].layers[*].user_data.text"
)
REPORT_PATH = Path("data/workshop_editor/aseprite_linked_cel_semantics_stage0.json")
DATA_PATH = Path("data/workshop_editor/aseprite_linked_cel_semantics_data.js")


def export_aseprite_linked_cel_project(grid: dict, slip_profile: dict) -> dict:
    canonical_project = _encode_aseprite_linked_cel_project(grid, metadata=None)
    canonical_hash = _hash_bytes(canonical_project)
    cel_visual_hashes = _cel_visual_hashes(canonical_project)
    asset = {
        "asset_id": f"{grid['grid_id']}_linked_cel.aseprite",
        "format_id": "libresprite_project",
        "media_type": "application/octet-stream",
        "uri": f"generated://workshop/project-linked-cel/{grid['grid_id']}.aseprite",
        "width": grid["grid_size"][0],
        "height": grid["grid_size"][1],
        "frame_count": 3,
        "content_hash": canonical_hash,
        "semantic_policy": ASE_LINKED_CEL_POLICY,
    }
    sidecar = build_sidecar_for_grid(grid, slip_profile, asset)
    sidecar["sidecar_id"] = f"{grid['grid_id']}_aseprite_linked_cel_sidecar"
    sidecar["asset_binding"]["semantic_policy"] = ASE_LINKED_CEL_POLICY
    sidecar["project_binding"] = {
        "format_id": "libresprite_project",
        "decoder_scope": "aseprite_linked_cel_palette_slice_tags_layers_user_data_subset",
        "native_mechagotchi_semantics": True,
        "semantic_policy": ASE_LINKED_CEL_POLICY,
        "native_metadata_version": ASE_LINKED_CEL_VERSION,
    }
    sidecar["limitations"] = [
        "Stage 0 Aseprite/LibreSprite linked-cel proof covers Cel Chunk 0x2005 linked cel type 1 targets layered over palette, slice, tag, and semantic layer carrier chunks.",
        "Linked cels are resolved only to same-layer compressed RGBA targets inside this deterministic three-frame subset.",
        "Live external editor rewrite validation is not verified by this lab.",
        "Arbitrary Aseprite project schemas, tilemaps, tilesets, nested groups, advanced timeline variants, and full project-format coverage remain separate.",
    ]
    metadata = _build_linked_cel_metadata(
        canonical_hash,
        cel_visual_hashes,
        grid,
        sidecar,
    )
    project_bytes = _encode_aseprite_linked_cel_project(grid, metadata=metadata)
    decoded = decode_aseprite_linked_cel_project(project_bytes)
    return {
        "project_bytes": project_bytes,
        "canonical_project_bytes": canonical_project,
        "embedded_project_hash": _hash_bytes(project_bytes),
        "canonical_project_hash": canonical_hash,
        "metadata": metadata,
        "sidecar": sidecar,
        "decoded_project": decoded,
    }


def decode_aseprite_linked_cel_project(project_bytes: bytes) -> dict:
    parsed = _parse_aseprite(project_bytes)
    layers = []
    tags = []
    cels = []
    user_data_chunks = []
    layer_user_data = []
    palette = None
    palette_chunk_count = 0
    slices = []
    last_target = None
    native = False
    total_chunk_count = 0

    for frame_index, frame in enumerate(parsed["frames"]):
        for chunk in frame["chunks"]:
            total_chunk_count += 1
            chunk_type = chunk["type"]
            if chunk_type == ASE_CHUNK_PALETTE:
                palette = _parse_palette_chunk(chunk["data"])
                palette["frame_index"] = frame_index
                palette_chunk_count += 1
                last_target = {
                    "target_type": "palette",
                    "target_index": 0,
                    "target_name": "palette",
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
            elif chunk_type == ASE_CHUNK_TAGS:
                parsed_tags = _parse_tags_chunk(chunk["data"])
                for tag in parsed_tags:
                    tag["index"] = len(tags)
                    tag["frame_index"] = frame_index
                    tags.append(tag)
                last_target = {
                    "target_type": "tags",
                    "target_index": None,
                    "target_name": "tags",
                }
            elif chunk_type == ASE_CHUNK_SLICE:
                parsed_slice = _parse_slice_chunk(chunk["data"])
                parsed_slice["index"] = len(slices)
                parsed_slice["frame_index"] = frame_index
                slices.append(parsed_slice)
                last_target = {
                    "target_type": "slice",
                    "target_index": parsed_slice["index"],
                    "target_name": parsed_slice["name"],
                }
            elif chunk_type == ASE_CHUNK_CEL:
                cel = _parse_cel_or_linked_chunk(
                    chunk["data"],
                    parsed["header"]["width"],
                    parsed["header"]["height"],
                )
                cel["index"] = len(cels)
                cel["frame_index"] = frame_index
                cels.append(cel)
                target_suffix = (
                    f"linked_to_frame_{cel['linked_to_frame']}"
                    if cel["cel_type"] == 1
                    else "compressed"
                )
                last_target = {
                    "target_type": "cel",
                    "target_index": cel["index"],
                    "target_name": f"frame_{frame_index}_layer_{cel['layer_index']}_{target_suffix}",
                }
            elif chunk_type == ASE_CHUNK_USER_DATA:
                user_data = _parse_user_data_chunk(chunk["data"])
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
                    **target,
                }
                if isinstance(text, str) and text.startswith(ASE_USER_DATA_PREFIX):
                    metadata = json.loads(text[len(ASE_USER_DATA_PREFIX) :])
                    if metadata.get("metadata_version") == ASE_LINKED_CEL_VERSION:
                        native = True
                    layer_binding = metadata.get("layer_binding", {})
                    if target["target_type"] == "layer":
                        entry["semantic_role"] = layer_binding.get("semantic_role")
                        entry["semantic_organ"] = layer_binding.get("semantic_organ")
                        layer_user_data.append(entry)
                user_data_chunks.append(entry)

    _resolve_linked_cels(cels, parsed["header"]["frames"])
    cel_hashes = _cel_hash_map(cels)
    linked_cels = [cel for cel in cels if cel["cel_type"] == 1]
    compressed_cels = [cel for cel in cels if cel["cel_type"] == 2]
    return {
        "format_id": "libresprite_project",
        "magic": hex(parsed["header"]["magic"]),
        "frame_magic": hex(parsed["frames"][0]["magic"]) if parsed["frames"] else None,
        "dimensions": [parsed["header"]["width"], parsed["header"]["height"]],
        "frame_count": parsed["header"]["frames"],
        "layer_count": len(layers),
        "tag_count": len(tags),
        "cel_count": len(cels),
        "compressed_cel_count": len(compressed_cels),
        "linked_cel_count": len(linked_cels),
        "linked_cel_target_count": sum(1 for cel in linked_cels if cel.get("resolved_target_key")),
        "chunk_count": total_chunk_count,
        "user_data_chunk_count": len(user_data_chunks),
        "palette_chunk_count": palette_chunk_count,
        "palette_entry_count": len(palette["entries"]) if palette else 0,
        "slice_count": len(slices),
        "slice_key_count": sum(len(entry["keys"]) for entry in slices),
        "color_depth_bpp": parsed["header"]["color_depth"],
        "first_frame_duration_ms": parsed["frames"][0]["duration_ms"] if parsed["frames"] else parsed["header"]["speed_ms"],
        "layers": layers,
        "tags": tags,
        "palette": palette or {},
        "slices": slices,
        "cels": [_cel_summary(cel) for cel in cels],
        "linked_cel_semantics": [_linked_cel_summary(cel) for cel in linked_cels],
        "cel_visual_hashes": cel_hashes,
        "user_data_chunks": user_data_chunks,
        "layer_user_data": layer_user_data,
        "native_mechagotchi_semantics": native,
    }


def extract_aseprite_linked_cel_sidecar(project_bytes: bytes) -> dict:
    decoded = decode_aseprite_linked_cel_project(project_bytes)
    metadata = _extract_linked_cel_metadata(project_bytes)
    if metadata.get("metadata_version") != ASE_LINKED_CEL_VERSION:
        raise AsepriteUserDataError(
            "aseprite_linked_cel_version_unsupported",
            "unsupported Aseprite linked-cel metadata version",
        )
    if metadata.get("format_id") != "libresprite_project":
        raise AsepriteUserDataError(
            "aseprite_linked_cel_format_mismatch",
            "Aseprite linked-cel metadata format id mismatch",
        )
    _validate_palette(decoded, metadata)
    _validate_slices(decoded, metadata)
    _validate_tags(decoded["tags"], decoded["frame_count"], metadata)
    _validate_layers(decoded, metadata)
    _validate_linked_cels(decoded, metadata)

    sidecar = metadata.get("sidecar")
    if not isinstance(sidecar, dict):
        raise AsepriteUserDataError(
            "aseprite_linked_cel_sidecar_missing",
            "Aseprite linked-cel metadata must contain a sidecar object",
        )
    if _hash_payload(sidecar) != metadata.get("sidecar_hash"):
        raise AsepriteUserDataError(
            "aseprite_linked_cel_sidecar_hash_mismatch",
            "Aseprite linked-cel sidecar hash does not match the embedded sidecar",
        )
    if decoded.get("cel_visual_hashes") != metadata.get("cel_visual_hashes"):
        raise AsepriteUserDataError(
            "aseprite_linked_cel_visual_hash_mismatch",
            "Aseprite linked-cel resolved visual hashes do not match current cel payloads",
        )
    canonical = strip_aseprite_linked_cel_user_data_chunks(project_bytes)
    canonical_hash = _hash_bytes(canonical)
    if canonical_hash != metadata.get("canonical_project_hash"):
        raise AsepriteUserDataError(
            "aseprite_linked_cel_canonical_hash_mismatch",
            "Aseprite linked-cel canonical project hash does not match the stripped project",
        )
    if sidecar.get("asset_binding", {}).get("content_hash") != canonical_hash:
        raise AsepriteUserDataError(
            "aseprite_linked_cel_sidecar_asset_hash_mismatch",
            "Aseprite linked-cel sidecar asset hash does not match the canonical project hash",
        )
    return {
        "ok": True,
        "metadata": metadata,
        "sidecar": sidecar,
        "decoded_project": _decoded_project_summary(decoded),
        "canonical_project_hash": canonical_hash,
        "embedded_project_hash": _hash_bytes(project_bytes),
    }


def import_aseprite_linked_cel_project(project_bytes: bytes, source_grid: dict | None = None) -> dict:
    try:
        extracted = extract_aseprite_linked_cel_sidecar(project_bytes)
    except AsepriteUserDataError as exc:
        return _failed_import("aseprite_linked_cel", exc.family, exc.message)

    sidecar = extracted["sidecar"]
    asset = deepcopy(sidecar["asset_binding"])
    try:
        restored = restore_grid_from_sidecar(sidecar, asset)
    except ValueError as exc:
        return _failed_import("sidecar", "aseprite_linked_cel_sidecar_invalid", str(exc))

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
        "native_metadata": {
            key: extracted["metadata"][key]
            for key in [
                "metadata_version",
                "format_id",
                "native_location",
                "writer_policy",
                "canonical_project_hash",
                "sidecar_hash",
            ]
        },
        "restored_grid": restored,
        "restored_grid_validation": {
            "valid": grid_validation.ok,
            "errors": grid_validation.errors,
            "slip_aligned": alignment.ok,
            "slip_errors": alignment.errors,
        },
        "project_policy": {
            "semantic_policy": ASE_LINKED_CEL_POLICY,
            "native_mechagotchi_semantics": True,
            "native_location": ASE_LINKED_CEL_NATIVE_LOCATION,
            "linked_cel_chunk_type": "0x2005",
            "palette_chunk_type": "0x2019",
            "slice_chunk_type": "0x2022",
            "layer_user_data_chunk_type": "0x2020",
            "tags_chunk_type": "0x2018",
            "live_external_editor_verified": False,
        },
        "semantic_diff": diff,
        "semantic_fidelity": fidelity,
        "errors": errors,
        "error_families": sorted({error["family"] for error in errors}),
    }


def strip_aseprite_linked_cel_user_data_chunks(project_bytes: bytes) -> bytes:
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


def strip_aseprite_linked_cel_chunks(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    frames = []
    for frame in parsed["frames"]:
        chunks = []
        for chunk in frame["chunks"]:
            if chunk["type"] == ASE_CHUNK_CEL and _peek_cel_header(chunk["data"])["cel_type"] == 1:
                continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    return _write_aseprite(parsed["header"], frames)


def tamper_aseprite_linked_cel_target(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    replaced = False
    frames = []
    invalid_frame = parsed["header"]["frames"] + 1
    for frame in parsed["frames"]:
        chunks = []
        for chunk in frame["chunks"]:
            if chunk["type"] == ASE_CHUNK_CEL and not replaced:
                header = _peek_cel_header(chunk["data"])
                if header["cel_type"] == 1:
                    chunks.append(
                        _chunk(
                            ASE_CHUNK_CEL,
                            _linked_cel_chunk_data(
                                header["layer_index"],
                                invalid_frame,
                                x=header["x"],
                                y=header["y"],
                                opacity=header["opacity"],
                                z_index=header["z_index"],
                            ),
                        )
                    )
                    replaced = True
                    continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    if not replaced:
        raise AsepriteUserDataError("aseprite_linked_cels_missing", "no linked cel chunk found")
    return _write_aseprite(parsed["header"], frames)


def strip_aseprite_linked_cel_target(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    linked = _first_linked_cel_reference(parsed)
    removed = False
    frames = []
    for frame_index, frame in enumerate(parsed["frames"]):
        chunks = []
        for chunk in frame["chunks"]:
            if frame_index == linked["linked_to_frame"] and chunk["type"] == ASE_CHUNK_CEL and not removed:
                header = _peek_cel_header(chunk["data"])
                if header["cel_type"] == 2 and header["layer_index"] == linked["layer_index"]:
                    removed = True
                    continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    if not removed:
        raise AsepriteUserDataError(
            "aseprite_linked_cel_target_missing",
            "no compressed cel target found for first linked cel",
        )
    return _write_aseprite(parsed["header"], frames)


def tamper_aseprite_linked_cel_source_visual(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    linked = _first_linked_cel_reference(parsed)
    replaced = False
    frames = []
    for frame_index, frame in enumerate(parsed["frames"]):
        chunks = []
        for chunk in frame["chunks"]:
            if frame_index == linked["linked_to_frame"] and chunk["type"] == ASE_CHUNK_CEL and not replaced:
                header = _peek_cel_header(chunk["data"])
                if header["cel_type"] == 2 and header["layer_index"] == linked["layer_index"]:
                    cel = _parse_cel_or_linked_chunk(
                        chunk["data"],
                        parsed["header"]["width"],
                        parsed["header"]["height"],
                    )
                    raw = bytearray(cel["raw_rgba"])
                    raw[0] = (raw[0] + 1) % 256
                    chunks.append(
                        _chunk(
                            ASE_CHUNK_CEL,
                            _cel_chunk_data(
                                cel["layer_index"],
                                cel["width"],
                                cel["height"],
                                bytes(raw),
                            ),
                        )
                    )
                    replaced = True
                    continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    if not replaced:
        raise AsepriteUserDataError(
            "aseprite_linked_cel_target_missing",
            "no compressed cel target found for first linked cel",
        )
    return _write_aseprite(parsed["header"], frames)


def tamper_aseprite_linked_cel_metadata(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    replaced = False
    frames = []
    for frame in parsed["frames"]:
        chunks = []
        for chunk in frame["chunks"]:
            if chunk["type"] == ASE_CHUNK_USER_DATA and not replaced:
                user_data = _parse_user_data_chunk(chunk["data"])
                text = user_data["text"]
                if isinstance(text, str) and text.startswith(ASE_USER_DATA_PREFIX):
                    metadata = json.loads(text[len(ASE_USER_DATA_PREFIX) :])
                    if metadata.get("metadata_version") == ASE_LINKED_CEL_VERSION:
                        metadata["sidecar"]["asset_binding"]["width"] += 1
                        chunks.append(_chunk(ASE_CHUNK_USER_DATA, _user_data_chunk_data(metadata)))
                        replaced = True
                        continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    if not replaced:
        raise AsepriteUserDataError(
            "aseprite_linked_cel_metadata_missing",
            "no Mechagotchi linked-cel User Data chunk found",
        )
    return _write_aseprite(parsed["header"], frames)


def run_aseprite_linked_cel_semantics_lab(profile_paths: list[Path], generated_root: Path) -> dict:
    linked_cel_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        exported = export_aseprite_linked_cel_project(grid, profile)
        imported = import_aseprite_linked_cel_project(exported["project_bytes"], source_grid=grid)
        decoded = exported["decoded_project"]
        linked_cel_results.append(
            {
                "profile_id": profile["profile_id"],
                "profile_path": _portable(profile_path),
                "grid_path": _portable(grid_path),
                "format_id": "libresprite_project",
                "project_file_name": f"{profile['profile_id']}_linked_cel.aseprite",
                "project_bytes_hex": exported["project_bytes"].hex(),
                "project_byte_count": len(exported["project_bytes"]),
                "embedded_project_hash": exported["embedded_project_hash"],
                "canonical_project_hash": exported["canonical_project_hash"],
                "metadata": _metadata_summary(exported["metadata"]),
                "native_sidecar": exported["sidecar"],
                "decoded_project": _decoded_project_summary(decoded),
                "palette_semantics": exported["metadata"]["palette_semantics"],
                "slice_semantics": exported["metadata"]["slice_semantics"],
                "layer_semantics": exported["metadata"]["layer_semantics"],
                "tag_semantics": exported["metadata"]["tag_semantics"],
                "linked_cel_semantics": exported["metadata"]["linked_cel_semantics"],
                "import_result": _compact_import_result(imported),
                "restored_grid_validation": imported.get("restored_grid_validation", {}),
                "semantic_diff": imported.get("semantic_diff", {}),
                "semantic_fidelity": imported.get("semantic_fidelity", 0.0),
                "cel_visual_hashes_preserved": (
                    exported["metadata"]["cel_visual_hashes"]
                    == decoded["cel_visual_hashes"]
                ),
                "linked_cel_targets_resolved": decoded["linked_cel_target_count"] == decoded["linked_cel_count"],
            }
        )

    invalid_probe_results = _invalid_probe_results(linked_cel_results[0])
    success_count = sum(
        1
        for result in linked_cel_results
        if result["import_result"]["ok"]
        and result["restored_grid_validation"].get("valid")
        and result["restored_grid_validation"].get("slip_aligned")
        and result["semantic_fidelity"] == 1.0
    )
    invalid_rejected_count = sum(1 for result in invalid_probe_results if not result["ok"])
    visual_hash_preserved = sum(1 for result in linked_cel_results if result["cel_visual_hashes_preserved"])
    target_resolved = sum(1 for result in linked_cel_results if result["linked_cel_targets_resolved"])
    return {
        "artifact_id": "aseprite_linked_cel_semantics_stage0",
        "status": "research_aseprite_linked_cel_semantics_no_package_code",
        "date": "2026-05-14",
        "purpose": (
            "Broaden Stage 0 Aseprite/LibreSprite chunk coverage beyond the "
            "palette/slice subset by proving linked Cel Chunk 0x2005 type 1 "
            "target resolution in a deterministic three-frame, three-layer "
            "carrier, without claiming tilemap, arbitrary schema, or live "
            "external editor coverage."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
            "labs/workshop_editor/aseprite_palette_slice_semantics.py",
            "labs/workshop_editor/aseprite_linked_cel_semantics.py",
        ],
        "external_anchors": [
            {
                "source": "Aseprite file-format specification",
                "url": "https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md",
                "used_for": "ASE Cel Chunk 0x2005 linked cel type 1 layout and frame-position target field, plus Palette Chunk 0x2019, Slice Chunk 0x2022, Layer Chunk 0x2004, Tags Chunk 0x2018, User Data Chunk 0x2020, and compressed Cel Chunk 0x2005 layout.",
            },
            {
                "source": "LibreSprite GitHub",
                "url": "https://github.com/LibreSprite/LibreSprite",
                "used_for": "LibreSprite remains a compatibility boundary; no GPL editor code is embedded.",
            },
        ],
        "profile_count": len(profile_paths),
        "linked_cel_roundtrip_count": len(linked_cel_results),
        "linked_cel_roundtrip_success_count": success_count,
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "metrics": {
            "linked_cel_roundtrip_success_rate": _ratio(success_count, len(linked_cel_results)),
            "mean_semantic_fidelity": round(
                sum(result["semantic_fidelity"] for result in linked_cel_results)
                / max(1, len(linked_cel_results)),
                6,
            ),
            "cel_visual_hash_preservation_rate": _ratio(
                visual_hash_preserved,
                len(linked_cel_results),
            ),
            "linked_cel_target_resolution_rate": _ratio(
                target_resolved,
                len(linked_cel_results),
            ),
            "invalid_probe_rejection_rate": _ratio(
                invalid_rejected_count,
                len(invalid_probe_results),
            ),
            "live_external_editor_verified": False,
        },
        "linked_cel_results": linked_cel_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "aseprite_linked_cel_chunk_subset",
            "aseprite_linked_cel_target_resolution",
            "aseprite_linked_cel_visual_hash_validation",
            "aseprite_linked_cel_sidecar_semantic_restore",
            "aseprite_linked_cel_palette_slice_tags_layers_carrier_subset",
        ],
        "blocked_states": [
            "live_external_editor_rewrite_validation",
            "arbitrary_aseprite_project_schema_coverage",
            "advanced_tags_layers_timeline_schema_coverage",
            "aseprite_tilemap_tileset_schema_coverage",
            "full_project_format_coverage",
            "package_runtime_lifecycle_integration",
            "manual_readability_calibration",
            "profile_weighted_evolution",
            "community_profile_packs",
        ],
        "decision": "prototype_aseprite_linked_cel_native_semantics_subset",
        "next_research_step": (
            "Keep live external editor validation, arbitrary Aseprite schemas, "
            "advanced timeline variants, tilemap/tileset coverage, and "
            "full project-format coverage blocked until direct editor fixtures "
            "and broader chunk/schema tests exist."
        ),
    }


def write_aseprite_linked_cel_semantics_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "aseprite_linked_cel_semantics_stage0.json", _json_report(report))
    for result in report["linked_cel_results"]:
        (output_dir / result["project_file_name"]).write_bytes(
            bytes.fromhex(result["project_bytes_hex"])
        )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "aseprite_linked_cel_semantics_data.js").write_text(
        "window.MECHAGOTCHI_ASEPRITE_LINKED_CEL_SEMANTICS = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _encode_aseprite_linked_cel_project(grid: dict, metadata: dict | None) -> bytes:
    width, height = grid["grid_size"]
    layers = _layer_semantics()
    tags = _tag_semantics()
    palette = _palette_semantics(grid)
    slices = _slice_semantics(grid)
    frames = []
    for frame_index in range(3):
        chunks = []
        if frame_index == 0:
            chunks.append(_chunk(ASE_CHUNK_PALETTE, _palette_chunk_data(palette)))
            for layer in layers:
                chunks.append(_chunk(ASE_CHUNK_LAYER, _layer_chunk_data(width, height, layer["name"])))
                if metadata is not None:
                    layer_metadata = deepcopy(metadata)
                    layer_metadata["layer_binding"] = layer
                    chunks.append(_chunk(ASE_CHUNK_USER_DATA, _user_data_chunk_data(layer_metadata)))
            chunks.append(_chunk(ASE_CHUNK_TAGS, _tags_chunk_data(tags)))
            for semantic_slice in slices:
                chunks.append(_chunk(ASE_CHUNK_SLICE, _slice_chunk_data(semantic_slice)))
        for layer in layers:
            linked_to_frame = _linked_target_for(frame_index, layer["layer_index"])
            if linked_to_frame is None:
                raw_rgba = _raw_rgba_for_layer(grid, layer, frame_index)
                chunks.append(_chunk(ASE_CHUNK_CEL, _cel_chunk_data(layer["layer_index"], width, height, raw_rgba)))
            else:
                chunks.append(_chunk(ASE_CHUNK_CEL, _linked_cel_chunk_data(layer["layer_index"], linked_to_frame)))
        frames.append({"duration_ms": 120, "chunks": chunks})
    header = {
        "frames": 3,
        "width": width,
        "height": height,
        "color_depth": 32,
        "flags": 1,
        "speed_ms": 120,
        "transparent_index": 0,
        "color_count": len(palette),
        "pixel_width": 1,
        "pixel_height": 1,
        "grid_x": 0,
        "grid_y": 0,
        "grid_width": width,
        "grid_height": height,
    }
    return _write_aseprite(header, frames)


def _linked_cel_chunk_data(
    layer_index: int,
    linked_to_frame: int,
    *,
    x: int = 0,
    y: int = 0,
    opacity: int = 255,
    z_index: int = 0,
) -> bytes:
    if not 0 <= linked_to_frame <= 0xFFFF:
        raise ValueError("linked cel target frame must fit in WORD")
    return struct.pack(
        "<HhhBHh5sH",
        layer_index,
        x,
        y,
        opacity,
        1,
        z_index,
        b"\x00" * 5,
        linked_to_frame,
    )


def _parse_cel_or_linked_chunk(data: bytes, project_width: int, project_height: int) -> dict:
    prefix_size = struct.calcsize("<HhhBHh5s")
    if len(data) < prefix_size:
        raise AsepriteUserDataError("aseprite_cel_chunk_truncated", "ASE Cel chunk is truncated")
    layer_index, x, y, opacity, cel_type, z_index, _reserved = struct.unpack(
        "<HhhBHh5s",
        data[:prefix_size],
    )
    offset = prefix_size
    base = {
        "chunk_type": "0x2005",
        "layer_index": layer_index,
        "x": x,
        "y": y,
        "opacity": opacity,
        "cel_type": cel_type,
        "z_index": z_index,
    }
    if cel_type == 1:
        if offset + 2 > len(data):
            raise AsepriteUserDataError(
                "aseprite_linked_cel_target_truncated",
                "linked ASE Cel frame target is truncated",
            )
        linked_to_frame = struct.unpack("<H", data[offset : offset + 2])[0]
        offset += 2
        if offset != len(data):
            raise AsepriteUserDataError(
                "aseprite_linked_cel_extra_bytes",
                "unexpected bytes after linked ASE Cel target",
            )
        return {**base, "linked_to_frame": linked_to_frame}
    if cel_type == 2:
        if offset + 4 > len(data):
            raise AsepriteUserDataError(
                "aseprite_cel_dimensions_truncated",
                "compressed ASE Cel dimensions are truncated",
            )
        width, height = struct.unpack("<HH", data[offset : offset + 4])
        offset += 4
        if [width, height] != [project_width, project_height]:
            raise AsepriteUserDataError(
                "aseprite_cel_dimensions_mismatch",
                "compressed ASE Cel dimensions must match project dimensions",
            )
        try:
            raw = zlib.decompress(data[offset:])
        except zlib.error as exc:
            raise AsepriteUserDataError("aseprite_cel_decompression_failed", str(exc)) from exc
        if len(raw) != width * height * 4:
            raise AsepriteUserDataError(
                "aseprite_cel_payload_size_mismatch",
                "decoded ASE Cel payload size does not match dimensions",
            )
        return {
            **base,
            "width": width,
            "height": height,
            "raw_rgba": raw,
            "compressed_byte_count": len(data) - offset,
            "cel_visual_hash": _hash_bytes(raw),
        }
    if cel_type == 3:
        raise AsepriteUserDataError(
            "aseprite_tilemap_cel_unsupported",
            "Stage 0 linked-cel parser does not cover compressed tilemap cels",
        )
    raise AsepriteUserDataError(
        "aseprite_cel_type_unsupported",
        "Stage 0 linked-cel parser supports linked and compressed image cels only",
    )


def _peek_cel_header(data: bytes) -> dict:
    prefix_size = struct.calcsize("<HhhBHh5s")
    if len(data) < prefix_size:
        raise AsepriteUserDataError("aseprite_cel_chunk_truncated", "ASE Cel chunk is truncated")
    layer_index, x, y, opacity, cel_type, z_index, _reserved = struct.unpack(
        "<HhhBHh5s",
        data[:prefix_size],
    )
    return {
        "layer_index": layer_index,
        "x": x,
        "y": y,
        "opacity": opacity,
        "cel_type": cel_type,
        "z_index": z_index,
    }


def _resolve_linked_cels(cels: list[dict], frame_count: int) -> None:
    compressed_by_key = {
        (cel["frame_index"], cel["layer_index"]): cel
        for cel in cels
        if cel["cel_type"] == 2
    }
    for cel in cels:
        if cel["cel_type"] != 1:
            continue
        target_frame = cel["linked_to_frame"]
        if target_frame >= frame_count or target_frame == cel["frame_index"]:
            raise AsepriteUserDataError(
                "aseprite_linked_cel_target_invalid",
                "linked ASE Cel target frame must be inside the project and cannot self-link",
            )
        target = compressed_by_key.get((target_frame, cel["layer_index"]))
        if target is None:
            raise AsepriteUserDataError(
                "aseprite_linked_cel_target_missing",
                "linked ASE Cel target must resolve to a same-layer compressed cel",
            )
        cel["width"] = target["width"]
        cel["height"] = target["height"]
        cel["resolved_target_key"] = f"frame_{target_frame}_layer_{cel['layer_index']}"
        cel["resolved_visual_hash"] = target["cel_visual_hash"]
        cel["cel_visual_hash"] = target["cel_visual_hash"]


def _linked_target_for(frame_index: int, layer_index: int) -> int | None:
    linked_targets = {
        (1, 0): 0,
        (1, 2): 0,
        (2, 0): 0,
        (2, 1): 0,
    }
    return linked_targets.get((frame_index, layer_index))


def _linked_cel_semantics(cel_visual_hashes: dict | None = None) -> list[dict]:
    semantics = []
    for frame_index, layer_index, linked_to_frame in [
        (1, 0, 0),
        (1, 2, 0),
        (2, 0, 0),
        (2, 1, 0),
    ]:
        target_key = f"frame_{linked_to_frame}_layer_{layer_index}"
        entry = {
            "frame_index": frame_index,
            "layer_index": layer_index,
            "linked_to_frame": linked_to_frame,
            "target_key": target_key,
            "resolved_key": f"frame_{frame_index}_layer_{layer_index}",
        }
        if cel_visual_hashes is not None:
            entry["resolved_visual_hash"] = cel_visual_hashes[entry["resolved_key"]]
            entry["target_visual_hash"] = cel_visual_hashes[target_key]
        semantics.append(entry)
    return semantics


def _build_linked_cel_metadata(
    canonical_hash: str,
    cel_visual_hashes: dict,
    grid: dict,
    sidecar: dict,
) -> dict:
    slice_semantics = _slice_semantics(grid)
    return {
        "metadata_version": ASE_LINKED_CEL_VERSION,
        "supersedes_metadata_version": ASE_PALETTE_SLICE_VERSION,
        "format_id": "libresprite_project",
        "native_location": ASE_LINKED_CEL_NATIVE_LOCATION,
        "writer_policy": ASE_LINKED_CEL_POLICY,
        "canonical_project_hash": canonical_hash,
        "cel_visual_hashes": cel_visual_hashes,
        "sidecar_hash": _hash_payload(sidecar),
        "sidecar": sidecar,
        "palette_semantics": _palette_semantics(grid),
        "slice_semantics": slice_semantics,
        "slice_bounds_by_organ": {
            entry["semantic_organ"]: entry["bounds"] for entry in slice_semantics
        },
        "layer_semantics": _layer_semantics(),
        "tag_semantics": _tag_semantics(),
        "linked_cel_semantics": _linked_cel_semantics(cel_visual_hashes),
    }


def _extract_linked_cel_metadata(project_bytes: bytes) -> dict:
    parsed = _parse_aseprite(project_bytes)
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
                    raise AsepriteUserDataError("aseprite_linked_cel_json_invalid", str(exc)) from exc
                if metadata.get("metadata_version") == ASE_LINKED_CEL_VERSION:
                    return metadata
    raise AsepriteUserDataError(
        "aseprite_linked_cel_metadata_missing",
        "ASE project does not contain Mechagotchi linked-cel User Data metadata",
    )


def _validate_linked_cels(decoded: dict, metadata: dict) -> None:
    if decoded["linked_cel_count"] < 1:
        raise AsepriteUserDataError(
            "aseprite_linked_cels_missing",
            "Aseprite linked-cel project must contain linked Cel Chunk 0x2005 type 1 payloads",
        )
    if decoded["linked_cel_target_count"] != decoded["linked_cel_count"]:
        raise AsepriteUserDataError(
            "aseprite_linked_cel_target_missing",
            "all linked cels must resolve to compressed same-layer targets",
        )
    current = [
        {
            "frame_index": entry["frame_index"],
            "layer_index": entry["layer_index"],
            "linked_to_frame": entry["linked_to_frame"],
        }
        for entry in decoded["linked_cel_semantics"]
    ]
    expected = [
        {
            "frame_index": entry["frame_index"],
            "layer_index": entry["layer_index"],
            "linked_to_frame": entry["linked_to_frame"],
        }
        for entry in metadata.get("linked_cel_semantics", [])
    ]
    if current != expected:
        raise AsepriteUserDataError(
            "aseprite_linked_cel_semantics_mismatch",
            "Aseprite linked-cel frame/layer target semantics do not match embedded metadata",
        )


def _cel_visual_hashes(project_bytes: bytes) -> dict:
    decoded = decode_aseprite_linked_cel_project(project_bytes)
    return decoded["cel_visual_hashes"]


def _cel_hash_map(cels: list[dict]) -> dict:
    return {
        f"frame_{cel['frame_index']}_layer_{cel['layer_index']}": cel["cel_visual_hash"]
        for cel in cels
    }


def _first_linked_cel_reference(parsed: dict) -> dict:
    for frame_index, frame in enumerate(parsed["frames"]):
        for chunk in frame["chunks"]:
            if chunk["type"] != ASE_CHUNK_CEL:
                continue
            header = _peek_cel_header(chunk["data"])
            if header["cel_type"] != 1:
                continue
            linked_to_frame = struct.unpack("<H", chunk["data"][struct.calcsize("<HhhBHh5s") : struct.calcsize("<HhhBHh5s") + 2])[0]
            return {
                "frame_index": frame_index,
                "layer_index": header["layer_index"],
                "linked_to_frame": linked_to_frame,
            }
    raise AsepriteUserDataError("aseprite_linked_cels_missing", "no linked cel chunk found")


def _invalid_probe_results(reference_result: dict) -> list[dict]:
    project_bytes = bytes.fromhex(reference_result["project_bytes_hex"])
    return [
        _compact_import_result(import_aseprite_linked_cel_project(strip_aseprite_linked_cel_chunks(project_bytes))),
        _compact_import_result(import_aseprite_linked_cel_project(tamper_aseprite_linked_cel_target(project_bytes))),
        _compact_import_result(import_aseprite_linked_cel_project(strip_aseprite_linked_cel_target(project_bytes))),
        _compact_import_result(import_aseprite_linked_cel_project(tamper_aseprite_linked_cel_source_visual(project_bytes))),
        _compact_import_result(import_aseprite_linked_cel_project(tamper_aseprite_linked_cel_metadata(project_bytes))),
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
        "layer_count",
        "tag_count",
        "cel_count",
        "compressed_cel_count",
        "linked_cel_count",
        "linked_cel_target_count",
        "chunk_count",
        "user_data_chunk_count",
        "palette_chunk_count",
        "palette_entry_count",
        "slice_count",
        "slice_key_count",
        "color_depth_bpp",
        "native_mechagotchi_semantics",
    ]
    return {key: decoded[key] for key in keys if key in decoded}


def _cel_summary(cel: dict) -> dict:
    summary = {
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
        if key in cel
    }
    if cel["cel_type"] == 1:
        summary["linked_to_frame"] = cel["linked_to_frame"]
        summary["resolved_target_key"] = cel["resolved_target_key"]
        summary["resolved_visual_hash"] = cel["resolved_visual_hash"]
    return summary


def _linked_cel_summary(cel: dict) -> dict:
    return {
        "frame_index": cel["frame_index"],
        "layer_index": cel["layer_index"],
        "linked_to_frame": cel["linked_to_frame"],
        "target_key": cel["resolved_target_key"],
        "resolved_visual_hash": cel["resolved_visual_hash"],
    }


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
    for result in payload["linked_cel_results"]:
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
                "linked_cel_roundtrip_count",
                "linked_cel_roundtrip_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "linked_cel_summaries": [
            {
                "profile_id": result["profile_id"],
                "format_id": result["format_id"],
                "project_byte_count": result["project_byte_count"],
                "embedded_project_hash": result["embedded_project_hash"],
                "canonical_project_hash": result["canonical_project_hash"],
                "decoded_project": result["decoded_project"],
                "semantic_fidelity": result["semantic_fidelity"],
            }
            for result in json_report["linked_cel_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# Aseprite Linked-Cel Semantics Stage 0\n\n"
        "Aseprite/LibreSprite linked-cel semantic proof for Cel Chunk 0x2005 "
        "type 1 linked targets, Palette Chunk 0x2019 colors, Slice Chunk "
        "0x2022 organ bounds, three-frame tags/layers, and compressed RGBA "
        "cel target payloads.\n\n"
        f"- Linked-cel round trips: {report['linked_cel_roundtrip_success_count']}/"
        f"{report['linked_cel_roundtrip_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}/"
        f"{report['invalid_probe_count']}\n"
        f"- Mean semantic fidelity: {metrics['mean_semantic_fidelity']}\n"
        f"- Cel visual hash preservation rate: {metrics['cel_visual_hash_preservation_rate']}\n"
        f"- Linked-cel target resolution rate: {metrics['linked_cel_target_resolution_rate']}\n"
        f"- Live external editor verified: {metrics['live_external_editor_verified']}\n\n"
        "This artifact does not claim live external editor validation, "
        "arbitrary Aseprite schemas, tilemaps/tilesets, advanced timelines, "
        "package runtime integration, or full project-format coverage.\n"
    )


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
        default=Path("data/workshop_editor/aseprite_linked_cel_semantics_stage0"),
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
    report = run_aseprite_linked_cel_semantics_lab(profile_paths, args.generated_root)
    write_aseprite_linked_cel_semantics_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_ASEPRITE_LINKED_CEL_SEMANTICS = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(_json_report(report), indent=2))


if __name__ == "__main__":
    main()
