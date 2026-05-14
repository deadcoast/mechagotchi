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

from aseprite_tags_layers_semantics import ASE_CHUNK_TAGS, _parse_tags_chunk, _tags_chunk_data
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
    _parse_user_data_chunk,
    _ratio,
    _unpack_string,
    _write_aseprite,
)
from external_metadata_sidecar import build_sidecar_for_grid, restore_grid_from_sidecar
from workshop_editor import compare_semantic_grid_fidelity


ASE_NESTED_TIMELINE_VERSION = "mechagotchi.aseprite_nested_timeline.v1"
ASE_NESTED_TIMELINE_POLICY = "aseprite_nested_timeline_native_semantics"
ASE_NESTED_TIMELINE_NATIVE_LOCATION = (
    "frame[0].nested_layers[*].user_data.text + "
    "frame[0].tags[*].user_data.text_color + frame[*].image_cels"
)
REPORT_PATH = Path("data/workshop_editor/aseprite_nested_timeline_semantics_stage0.json")
DATA_PATH = Path("data/workshop_editor/aseprite_nested_timeline_semantics_data.js")


def export_aseprite_nested_timeline_project(grid: dict, slip_profile: dict) -> dict:
    canonical_project = _encode_aseprite_nested_timeline_project(grid, metadata=None)
    canonical_hash = _hash_bytes(canonical_project)
    cel_visual_hashes = _cel_visual_hashes(canonical_project)
    asset = {
        "asset_id": f"{grid['grid_id']}_nested_timeline.aseprite",
        "format_id": "libresprite_project",
        "media_type": "application/octet-stream",
        "uri": f"generated://workshop/project-nested-timeline/{grid['grid_id']}.aseprite",
        "width": grid["grid_size"][0],
        "height": grid["grid_size"][1],
        "frame_count": 4,
        "content_hash": canonical_hash,
        "semantic_policy": ASE_NESTED_TIMELINE_POLICY,
    }
    sidecar = build_sidecar_for_grid(grid, slip_profile, asset)
    sidecar["sidecar_id"] = f"{grid['grid_id']}_aseprite_nested_timeline_sidecar"
    sidecar["asset_binding"]["semantic_policy"] = ASE_NESTED_TIMELINE_POLICY
    sidecar["project_binding"] = {
        "format_id": "libresprite_project",
        "decoder_scope": "aseprite_nested_groups_tag_user_data_timeline_subset",
        "native_mechagotchi_semantics": True,
        "semantic_policy": ASE_NESTED_TIMELINE_POLICY,
        "native_metadata_version": ASE_NESTED_TIMELINE_VERSION,
    }
    sidecar["limitations"] = [
        "Stage 0 Aseprite/LibreSprite nested timeline proof covers two group layers, three image layers, four timeline loop directions, and tag-associated User Data chunks.",
        "Live external editor rewrite validation is not verified by this lab.",
        "Arbitrary Aseprite project schemas, external assets, multiple documents, and full project-format coverage remain separate.",
    ]
    metadata = _build_nested_timeline_metadata(canonical_hash, cel_visual_hashes, sidecar)
    project_bytes = _encode_aseprite_nested_timeline_project(grid, metadata=metadata)
    decoded = decode_aseprite_nested_timeline_project(project_bytes)
    return {
        "project_bytes": project_bytes,
        "canonical_project_bytes": canonical_project,
        "embedded_project_hash": _hash_bytes(project_bytes),
        "canonical_project_hash": canonical_hash,
        "metadata": metadata,
        "sidecar": sidecar,
        "decoded_project": decoded,
    }


def decode_aseprite_nested_timeline_project(project_bytes: bytes) -> dict:
    parsed = _parse_aseprite(project_bytes)
    layers = []
    tags = []
    cels = []
    user_data_chunks = []
    layer_user_data = []
    tag_user_data = []
    tag_user_data_targets = []
    last_target = None
    native = False
    total_chunk_count = 0

    for frame_index, frame in enumerate(parsed["frames"]):
        for chunk in frame["chunks"]:
            total_chunk_count += 1
            chunk_type = chunk["type"]
            if chunk_type == ASE_CHUNK_LAYER:
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
                tag_user_data_targets = []
                for tag in parsed_tags:
                    tag["index"] = len(tags)
                    tag["frame_index"] = frame_index
                    tags.append(tag)
                    tag_user_data_targets.append(
                        {
                            "target_type": "tag",
                            "target_index": tag["index"],
                            "target_name": tag["name"],
                        }
                    )
                last_target = {
                    "target_type": "tags",
                    "target_index": None,
                    "target_name": "tags",
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
                last_target = {
                    "target_type": "cel",
                    "target_index": cel["index"],
                    "target_name": f"frame_{frame_index}_layer_{cel['layer_index']}",
                }
            elif chunk_type == ASE_CHUNK_USER_DATA:
                user_data = _parse_user_data_chunk(chunk["data"])
                if tag_user_data_targets:
                    target = tag_user_data_targets.pop(0)
                else:
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
                    **target,
                }
                if isinstance(text, str) and text.startswith(ASE_USER_DATA_PREFIX):
                    native = True
                    metadata = json.loads(text[len(ASE_USER_DATA_PREFIX) :])
                    if target["target_type"] == "layer":
                        layer_binding = metadata.get("layer_binding", {})
                        entry["semantic_role"] = layer_binding.get("semantic_role")
                        entry["semantic_organ"] = layer_binding.get("semantic_organ")
                        entry["layer_type"] = layer_binding.get("layer_type")
                        layer_user_data.append(entry)
                    elif target["target_type"] == "tag":
                        tag_binding = metadata.get("tag_binding", {})
                        entry["tag_name"] = tag_binding.get("name", target["target_name"])
                        entry["semantic_phase"] = tag_binding.get("semantic_phase")
                        tag_user_data.append(entry)
                user_data_chunks.append(entry)

    cel_hashes = _cel_hash_map(cels)
    group_layers = [layer for layer in layers if layer["layer_type"] == 1]
    image_layers = [layer for layer in layers if layer["layer_type"] == 0]
    return {
        "format_id": "libresprite_project",
        "magic": hex(parsed["header"]["magic"]),
        "frame_magic": hex(parsed["frames"][0]["magic"]) if parsed["frames"] else None,
        "dimensions": [parsed["header"]["width"], parsed["header"]["height"]],
        "frame_count": parsed["header"]["frames"],
        "layer_count": len(layers),
        "group_layer_count": len(group_layers),
        "image_layer_count": len(image_layers),
        "max_child_level": max([layer["child_level"] for layer in layers], default=0),
        "tag_count": len(tags),
        "cel_count": len(cels),
        "chunk_count": total_chunk_count,
        "user_data_chunk_count": len(user_data_chunks),
        "layer_user_data_count": len(layer_user_data),
        "tag_user_data_count": len(tag_user_data),
        "color_depth_bpp": parsed["header"]["color_depth"],
        "first_frame_duration_ms": parsed["frames"][0]["duration_ms"] if parsed["frames"] else parsed["header"]["speed_ms"],
        "layers": layers,
        "tags": tags,
        "cels": [
            {
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
            for cel in cels
        ],
        "cel_visual_hashes": cel_hashes,
        "user_data_chunks": user_data_chunks,
        "layer_user_data": layer_user_data,
        "tag_user_data": tag_user_data,
        "native_mechagotchi_semantics": native,
    }


def extract_aseprite_nested_timeline_sidecar(project_bytes: bytes) -> dict:
    decoded = decode_aseprite_nested_timeline_project(project_bytes)
    metadata = _extract_nested_timeline_metadata(project_bytes)
    if metadata.get("metadata_version") != ASE_NESTED_TIMELINE_VERSION:
        raise AsepriteUserDataError(
            "aseprite_nested_timeline_version_unsupported",
            "unsupported Aseprite nested timeline metadata version",
        )
    if metadata.get("format_id") != "libresprite_project":
        raise AsepriteUserDataError(
            "aseprite_nested_timeline_format_mismatch",
            "Aseprite nested timeline metadata format id mismatch",
        )
    _validate_layers(decoded, metadata)
    _validate_timeline_tags(decoded, metadata)
    _validate_tag_user_data(decoded, metadata)

    sidecar = metadata.get("sidecar")
    if not isinstance(sidecar, dict):
        raise AsepriteUserDataError(
            "aseprite_nested_timeline_sidecar_missing",
            "Aseprite nested timeline metadata must contain a sidecar object",
        )
    if _hash_payload(sidecar) != metadata.get("sidecar_hash"):
        raise AsepriteUserDataError(
            "aseprite_nested_timeline_sidecar_hash_mismatch",
            "Aseprite nested timeline sidecar hash does not match the embedded sidecar",
        )
    if decoded.get("cel_visual_hashes") != metadata.get("cel_visual_hashes"):
        raise AsepriteUserDataError(
            "aseprite_nested_timeline_visual_hash_mismatch",
            "Aseprite nested timeline cel visual hashes do not match current cel payloads",
        )
    canonical = strip_aseprite_nested_timeline_user_data_chunks(project_bytes)
    canonical_hash = _hash_bytes(canonical)
    if canonical_hash != metadata.get("canonical_project_hash"):
        raise AsepriteUserDataError(
            "aseprite_nested_timeline_canonical_hash_mismatch",
            "Aseprite nested timeline canonical project hash does not match the stripped project",
        )
    if sidecar.get("asset_binding", {}).get("content_hash") != canonical_hash:
        raise AsepriteUserDataError(
            "aseprite_nested_timeline_sidecar_asset_hash_mismatch",
            "Aseprite nested timeline sidecar asset hash does not match the canonical project hash",
        )
    return {
        "ok": True,
        "metadata": metadata,
        "sidecar": sidecar,
        "decoded_project": _decoded_project_summary(decoded),
        "canonical_project_hash": canonical_hash,
        "embedded_project_hash": _hash_bytes(project_bytes),
    }


def import_aseprite_nested_timeline_project(project_bytes: bytes, source_grid: dict | None = None) -> dict:
    try:
        extracted = extract_aseprite_nested_timeline_sidecar(project_bytes)
    except AsepriteUserDataError as exc:
        return _failed_import("aseprite_nested_timeline", exc.family, exc.message)

    sidecar = extracted["sidecar"]
    asset = deepcopy(sidecar["asset_binding"])
    try:
        restored = restore_grid_from_sidecar(sidecar, asset)
    except ValueError as exc:
        return _failed_import("sidecar", "aseprite_nested_timeline_sidecar_invalid", str(exc))

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
            "semantic_policy": ASE_NESTED_TIMELINE_POLICY,
            "native_mechagotchi_semantics": True,
            "native_location": ASE_NESTED_TIMELINE_NATIVE_LOCATION,
            "group_layer_type": 1,
            "image_layer_type": 0,
            "max_child_level": 2,
            "layer_chunk_type": "0x2004",
            "tags_chunk_type": "0x2018",
            "tag_user_data_chunk_type": "0x2020",
            "cel_chunk_type": "0x2005",
            "live_external_editor_verified": False,
        },
        "semantic_diff": diff,
        "semantic_fidelity": fidelity,
        "errors": errors,
        "error_families": sorted({error["family"] for error in errors}),
    }


def strip_aseprite_nested_timeline_user_data_chunks(project_bytes: bytes) -> bytes:
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


def strip_aseprite_group_layer_chunks(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    frames = []
    for frame in parsed["frames"]:
        chunks = []
        for chunk in frame["chunks"]:
            if chunk["type"] == ASE_CHUNK_LAYER:
                layer = _parse_layer_chunk(chunk["data"])
                if layer["layer_type"] == 1:
                    continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    return _write_aseprite(parsed["header"], frames)


def strip_aseprite_tag_user_data_chunks(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    frames = []
    for frame in parsed["frames"]:
        chunks = []
        pending_tag_user_data = 0
        for chunk in frame["chunks"]:
            if chunk["type"] == ASE_CHUNK_TAGS:
                pending_tag_user_data = len(_parse_tags_chunk(chunk["data"]))
                chunks.append(chunk)
                continue
            if chunk["type"] == ASE_CHUNK_USER_DATA and pending_tag_user_data > 0:
                pending_tag_user_data -= 1
                continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    return _write_aseprite(parsed["header"], frames)


def tamper_aseprite_nested_child_level(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    replaced = False
    frames = []
    for frame in parsed["frames"]:
        chunks = []
        for chunk in frame["chunks"]:
            if chunk["type"] == ASE_CHUNK_LAYER and not replaced:
                layer = _parse_layer_chunk(chunk["data"])
                if layer["layer_type"] == 0 and layer["child_level"] > 0:
                    layer["child_level"] = 0
                    chunks.append(_chunk(ASE_CHUNK_LAYER, _layer_chunk_data_from_layer(layer)))
                    replaced = True
                    continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    if not replaced:
        raise AsepriteUserDataError("aseprite_image_layer_missing", "no nested image layer found")
    return _write_aseprite(parsed["header"], frames)


def tamper_aseprite_timeline_loop_direction(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    replaced = False
    frames = []
    for frame in parsed["frames"]:
        chunks = []
        for chunk in frame["chunks"]:
            if chunk["type"] == ASE_CHUNK_TAGS and not replaced:
                tags = _parse_tags_chunk(chunk["data"])
                tags[0]["direction"] = 9
                chunks.append(_chunk(ASE_CHUNK_TAGS, _tags_chunk_data(tags)))
                replaced = True
                continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    if not replaced:
        raise AsepriteUserDataError("aseprite_tags_missing", "no Aseprite Tags chunk found")
    return _write_aseprite(parsed["header"], frames)


def tamper_aseprite_tag_user_data_color(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    replaced = False
    frames = []
    for frame in parsed["frames"]:
        chunks = []
        pending_tag_user_data = 0
        for chunk in frame["chunks"]:
            if chunk["type"] == ASE_CHUNK_TAGS:
                pending_tag_user_data = len(_parse_tags_chunk(chunk["data"]))
                chunks.append(chunk)
                continue
            if chunk["type"] == ASE_CHUNK_USER_DATA and pending_tag_user_data > 0 and not replaced:
                user_data = _parse_user_data_chunk(chunk["data"])
                color = list(user_data["color"] or [0, 0, 0, 255])
                color[0] = (color[0] + 17) % 256
                chunks.append(_chunk(ASE_CHUNK_USER_DATA, _user_data_text_color_data(user_data["text"], color)))
                pending_tag_user_data -= 1
                replaced = True
                continue
            if chunk["type"] == ASE_CHUNK_USER_DATA and pending_tag_user_data > 0:
                pending_tag_user_data -= 1
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    if not replaced:
        raise AsepriteUserDataError("aseprite_tag_user_data_missing", "no Aseprite tag User Data chunk found")
    return _write_aseprite(parsed["header"], frames)


def tamper_aseprite_nested_timeline_metadata(project_bytes: bytes) -> bytes:
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
                    if metadata.get("metadata_version") == ASE_NESTED_TIMELINE_VERSION:
                        metadata["sidecar"]["asset_binding"]["width"] += 1
                        chunks.append(
                            _chunk(
                                ASE_CHUNK_USER_DATA,
                                _metadata_user_data_chunk_data(metadata, user_data["color"]),
                            )
                        )
                        replaced = True
                        continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    if not replaced:
        raise AsepriteUserDataError("aseprite_nested_timeline_metadata_missing", "no nested timeline metadata found")
    return _write_aseprite(parsed["header"], frames)


def run_aseprite_nested_timeline_semantics_lab(profile_paths: list[Path], generated_root: Path) -> dict:
    nested_timeline_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        exported = export_aseprite_nested_timeline_project(grid, profile)
        imported = import_aseprite_nested_timeline_project(exported["project_bytes"], source_grid=grid)
        diff = imported.get("semantic_diff", {"changed_cells": [], "missing_cells": [], "added_cells": []})
        nested_timeline_results.append(
            {
                "profile_id": profile["profile_id"],
                "profile_path": _portable(profile_path),
                "grid_path": _portable(grid_path),
                "format_id": "libresprite_project",
                "project_file_name": f"{profile['profile_id']}_nested_timeline.aseprite",
                "project_byte_count": len(exported["project_bytes"]),
                "embedded_project_hash": exported["embedded_project_hash"],
                "canonical_project_hash": exported["canonical_project_hash"],
                "metadata": _metadata_summary(exported["metadata"]),
                "native_sidecar": exported["sidecar"],
                "decoded_project": _decoded_project_summary(exported["decoded_project"]),
                "layer_hierarchy": exported["metadata"]["layer_semantics"],
                "tag_semantics": exported["metadata"]["tag_semantics"],
                "import_result": _compact_import_result(imported),
                "restored_grid_validation": imported.get("restored_grid_validation"),
                "semantic_diff": diff,
                "semantic_fidelity": imported.get("semantic_fidelity", 0.0),
                "cel_visual_hashes_preserved": (
                    exported["decoded_project"]["cel_visual_hashes"]
                    == exported["metadata"]["cel_visual_hashes"]
                ),
                "tag_user_data_preserved": _tag_user_data_preserved(exported["decoded_project"], exported["metadata"]),
                "project_bytes_hex": exported["project_bytes"].hex(),
            }
        )

    invalid_probe_results = _invalid_probe_results(nested_timeline_results[0])
    success_count = sum(1 for result in nested_timeline_results if result["import_result"]["ok"])
    invalid_rejected = sum(1 for result in invalid_probe_results if not result["ok"])
    visual_hash_preserved = sum(1 for result in nested_timeline_results if result["cel_visual_hashes_preserved"])
    tag_user_data_preserved = sum(1 for result in nested_timeline_results if result["tag_user_data_preserved"])
    return {
        "artifact_id": "aseprite_nested_timeline_semantics_stage0",
        "status": "research_aseprite_nested_timeline_semantics_no_package_code",
        "date": "2026-05-14",
        "purpose": (
            "Broaden Stage 0 Aseprite/LibreSprite chunk coverage beyond fixed "
            "layer/tag carriers by proving group layer child hierarchy, tag-"
            "associated User Data chunks, and all documented timeline loop "
            "directions in a deterministic semantic-organ carrier."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
            "labs/workshop_editor/aseprite_tags_layers_semantics.py",
            "labs/workshop_editor/aseprite_nested_timeline_semantics.py",
        ],
        "external_anchors": [
            {
                "source": "Aseprite file-format specification",
                "url": "https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md",
                "used_for": "ASE Layer Chunk 0x2004 group layer type 1, child levels, Tags Chunk 0x2018 loop directions/repeat counts, tag-associated User Data Chunk 0x2020 ordering, and compressed Cel Chunk 0x2005 layout.",
            },
            {
                "source": "Aseprite tags documentation",
                "url": "https://www.aseprite.org/docs/tags/",
                "used_for": "Tag workflow boundary: tags organize animations and expose Forward, Reverse, Ping-pong, and Ping-pong Reverse directions.",
            },
            {
                "source": "Aseprite layers documentation",
                "url": "https://www.aseprite.org/docs/layers/",
                "used_for": "Layer group workflow boundary; nested groups remain an editor organization structure, not a replacement for Mechagotchi semantic metadata.",
            },
            {
                "source": "LibreSprite GitHub",
                "url": "https://github.com/LibreSprite/LibreSprite",
                "used_for": "LibreSprite remains a compatibility boundary; no GPL editor code is embedded.",
            },
        ],
        "profile_count": len(nested_timeline_results),
        "nested_timeline_roundtrip_count": len(nested_timeline_results),
        "nested_timeline_roundtrip_success_count": success_count,
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected,
        "metrics": {
            "nested_timeline_roundtrip_success_rate": _ratio(success_count, len(nested_timeline_results)),
            "mean_semantic_fidelity": round(
                sum(result["semantic_fidelity"] for result in nested_timeline_results)
                / max(1, len(nested_timeline_results)),
                6,
            ),
            "cel_visual_hash_preservation_rate": _ratio(visual_hash_preserved, len(nested_timeline_results)),
            "tag_user_data_preservation_rate": _ratio(tag_user_data_preserved, len(nested_timeline_results)),
            "invalid_probe_rejection_rate": _ratio(invalid_rejected, len(invalid_probe_results)),
            "live_external_editor_verified": False,
        },
        "nested_timeline_results": nested_timeline_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "aseprite_nested_group_layer_subset",
            "aseprite_layer_child_level_hierarchy_subset",
            "aseprite_tag_user_data_subset",
            "aseprite_timeline_loop_direction_subset",
            "aseprite_nested_timeline_hash_validation",
        ],
        "blocked_states": [
            "live_external_editor_rewrite_validation",
            "arbitrary_aseprite_project_schema_coverage",
            "full_project_format_coverage",
            "package_runtime_lifecycle_integration",
            "manual_readability_calibration",
            "profile_weighted_evolution",
            "community_profile_packs",
        ],
        "decision": "prototype_aseprite_nested_timeline_native_semantics_subset",
        "next_research_step": (
            "Keep live external editor validation, arbitrary Aseprite schemas, "
            "external file references, multiple document variants, and full "
            "project-format coverage blocked until direct editor fixtures and "
            "broader schema tests exist."
        ),
    }


def write_aseprite_nested_timeline_semantics_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "aseprite_nested_timeline_semantics_stage0.json", _json_report(report))
    for result in report["nested_timeline_results"]:
        (output_dir / result["project_file_name"]).write_bytes(bytes.fromhex(result["project_bytes_hex"]))
    (output_dir / "aseprite_nested_timeline_semantics_data.js").write_text(
        "window.MECHAGOTCHI_ASEPRITE_NESTED_TIMELINE_SEMANTICS = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")


def _encode_aseprite_nested_timeline_project(grid: dict, metadata: dict | None) -> bytes:
    width, height = grid["grid_size"]
    layers = _layer_semantics()
    tags = _tag_semantics()
    frames = []
    for frame_index in range(4):
        chunks = []
        if frame_index == 0:
            for layer in layers:
                chunks.append(_chunk(ASE_CHUNK_LAYER, _layer_chunk_data(width, height, layer)))
                if metadata is not None:
                    layer_metadata = deepcopy(metadata)
                    layer_metadata["layer_binding"] = layer
                    chunks.append(_chunk(ASE_CHUNK_USER_DATA, _metadata_user_data_chunk_data(layer_metadata)))
            chunks.append(_chunk(ASE_CHUNK_TAGS, _tags_chunk_data(tags)))
            if metadata is not None:
                for tag in tags:
                    tag_metadata = deepcopy(metadata)
                    tag_metadata["tag_binding"] = tag
                    chunks.append(
                        _chunk(
                            ASE_CHUNK_USER_DATA,
                            _metadata_user_data_chunk_data(tag_metadata, tag["user_data_color_rgba"]),
                        )
                    )
        for layer in layers:
            if layer["layer_type"] != 0:
                continue
            raw_rgba = _raw_rgba_for_layer(grid, layer, frame_index)
            chunks.append(_chunk(ASE_CHUNK_CEL, _cel_chunk_data(layer["layer_index"], width, height, raw_rgba)))
        frames.append({"duration_ms": _frame_duration(frame_index), "chunks": chunks})
    header = {
        "frames": 4,
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


def _layer_chunk_data(width: int, height: int, layer: dict) -> bytes:
    flags = 35 if layer["layer_type"] == 1 else 3
    return (
        struct.pack(
            "<HHHHHHB3s",
            flags,
            layer["layer_type"],
            layer["child_level"],
            width,
            height,
            0,
            255,
            b"\x00\x00\x00",
        )
        + _pack_string(layer["name"])
    )


def _layer_chunk_data_from_layer(layer: dict) -> bytes:
    width, height = layer["default_size"]
    return (
        struct.pack(
            "<HHHHHHB3s",
            layer["flags"],
            layer["layer_type"],
            layer["child_level"],
            width,
            height,
            layer["blend_mode"],
            layer["opacity"],
            b"\x00\x00\x00",
        )
        + _pack_string(layer["name"])
    )


def _cel_chunk_data(layer_index: int, width: int, height: int, raw_rgba: bytes) -> bytes:
    expected_length = width * height * 4
    if len(raw_rgba) != expected_length:
        raise ValueError("raw RGBA payload does not match dimensions")
    return (
        struct.pack("<HhhBHh5sHH", layer_index, 0, 0, 255, 2, 0, b"\x00" * 5, width, height)
        + zlib.compress(raw_rgba)
    )


def _metadata_user_data_chunk_data(metadata: dict, color_rgba: list[int] | None = None) -> bytes:
    text = ASE_USER_DATA_PREFIX + json.dumps(metadata, sort_keys=True, separators=(",", ":"))
    return _user_data_text_color_data(text, color_rgba)


def _user_data_text_color_data(text: str | None, color_rgba: list[int] | None = None) -> bytes:
    if text is None:
        text = ""
    flags = 1 if color_rgba is None else 3
    payload = bytearray(struct.pack("<I", flags))
    payload.extend(_pack_string(text))
    if color_rgba is not None:
        payload.extend(bytes(color_rgba))
    return bytes(payload)


def _build_nested_timeline_metadata(canonical_hash: str, cel_visual_hashes: dict, sidecar: dict) -> dict:
    return {
        "metadata_version": ASE_NESTED_TIMELINE_VERSION,
        "format_id": "libresprite_project",
        "native_location": ASE_NESTED_TIMELINE_NATIVE_LOCATION,
        "writer_policy": ASE_NESTED_TIMELINE_POLICY,
        "canonical_project_hash": canonical_hash,
        "cel_visual_hashes": cel_visual_hashes,
        "sidecar_hash": _hash_payload(sidecar),
        "sidecar": sidecar,
        "layer_semantics": _layer_semantics(),
        "tag_semantics": _tag_semantics(),
    }


def _extract_nested_timeline_metadata(project_bytes: bytes) -> dict:
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
                    raise AsepriteUserDataError("aseprite_nested_timeline_json_invalid", str(exc)) from exc
                if metadata.get("metadata_version") == ASE_NESTED_TIMELINE_VERSION:
                    return metadata
    raise AsepriteUserDataError(
        "aseprite_nested_timeline_metadata_missing",
        "ASE project does not contain Mechagotchi nested timeline User Data metadata",
    )


def _validate_layers(decoded: dict, metadata: dict) -> None:
    expected = metadata.get("layer_semantics", [])
    if decoded["group_layer_count"] < 2:
        raise AsepriteUserDataError(
            "aseprite_nested_group_missing",
            "Aseprite nested timeline project must contain group layers",
        )
    if decoded["layer_count"] != len(expected):
        raise AsepriteUserDataError(
            "aseprite_layer_count_mismatch",
            "Aseprite nested timeline layer count does not match embedded layer semantics",
        )
    if decoded["layer_user_data_count"] != len(expected):
        raise AsepriteUserDataError(
            "aseprite_layer_user_data_missing",
            "Aseprite nested timeline layer User Data chunks must bind to every layer",
        )
    current = [
        {
            "layer_index": layer["index"],
            "name": layer["name"],
            "layer_type": layer["layer_type"],
            "child_level": layer["child_level"],
        }
        for layer in decoded["layers"]
    ]
    expected_summary = [
        {
            "layer_index": layer["layer_index"],
            "name": layer["name"],
            "layer_type": layer["layer_type"],
            "child_level": layer["child_level"],
        }
        for layer in expected
    ]
    if current != expected_summary:
        raise AsepriteUserDataError(
            "aseprite_layer_hierarchy_mismatch",
            "Aseprite nested layer hierarchy does not match embedded semantics",
        )
    if decoded["max_child_level"] != 2:
        raise AsepriteUserDataError(
            "aseprite_layer_hierarchy_mismatch",
            "Aseprite nested layer hierarchy must include child level 2",
        )


def _validate_timeline_tags(decoded: dict, metadata: dict) -> None:
    if decoded["tag_count"] < 1:
        raise AsepriteUserDataError(
            "aseprite_tags_missing",
            "Aseprite nested timeline project must contain a Tags Chunk 0x2018",
        )
    for tag in decoded["tags"]:
        if tag["from_frame"] > tag["to_frame"] or tag["to_frame"] >= decoded["frame_count"]:
            raise AsepriteUserDataError(
                "aseprite_tag_range_invalid",
                "Aseprite nested timeline tag frame range must be within project frames",
            )
        if tag["direction"] not in {0, 1, 2, 3}:
            raise AsepriteUserDataError(
                "aseprite_timeline_loop_direction_invalid",
                "Aseprite nested timeline tag direction must be one of the documented directions",
            )
    current = [
        {
            key: tag[key]
            for key in ["name", "from_frame", "to_frame", "direction", "repeat", "color_rgb"]
        }
        for tag in decoded["tags"]
    ]
    expected = [
        {
            key: tag[key]
            for key in ["name", "from_frame", "to_frame", "direction", "repeat", "color_rgb"]
        }
        for tag in metadata.get("tag_semantics", [])
    ]
    if current != expected:
        raise AsepriteUserDataError(
            "aseprite_timeline_tag_semantics_mismatch",
            "Aseprite nested timeline tag semantics do not match embedded metadata",
        )


def _validate_tag_user_data(decoded: dict, metadata: dict) -> None:
    expected_tags = metadata.get("tag_semantics", [])
    if decoded["tag_user_data_count"] != len(expected_tags):
        raise AsepriteUserDataError(
            "aseprite_tag_user_data_missing",
            "Aseprite nested timeline requires one User Data chunk for each tag",
        )
    current = [
        {
            "tag_name": entry.get("tag_name"),
            "semantic_phase": entry.get("semantic_phase"),
            "color_rgba": entry.get("color_rgba"),
        }
        for entry in decoded["tag_user_data"]
    ]
    expected = [
        {
            "tag_name": tag["name"],
            "semantic_phase": tag["semantic_phase"],
            "color_rgba": tag["user_data_color_rgba"],
        }
        for tag in expected_tags
    ]
    if current != expected:
        current_without_color = [
            {key: entry[key] for key in ["tag_name", "semantic_phase"]}
            for entry in current
        ]
        expected_without_color = [
            {key: entry[key] for key in ["tag_name", "semantic_phase"]}
            for entry in expected
        ]
        if current_without_color == expected_without_color:
            raise AsepriteUserDataError(
                "aseprite_tag_user_data_color_mismatch",
                "Aseprite nested timeline tag User Data colors do not match embedded metadata",
            )
        raise AsepriteUserDataError(
            "aseprite_tag_user_data_semantics_mismatch",
            "Aseprite nested timeline tag User Data semantics do not match embedded metadata",
        )


def _layer_semantics() -> list[dict]:
    return [
        {
            "layer_index": 0,
            "name": "Mechagotchi organs",
            "layer_type": 1,
            "child_level": 0,
            "semantic_role": "organ_group",
            "semantic_organ": None,
            "cell_selector": "group:organs",
        },
        {
            "layer_index": 1,
            "name": "Core mass",
            "layer_type": 0,
            "child_level": 1,
            "semantic_role": "body_core",
            "semantic_organ": "core",
            "cell_selector": "organ:core",
        },
        {
            "layer_index": 2,
            "name": "Mechagotchi affordances",
            "layer_type": 1,
            "child_level": 1,
            "semantic_role": "affordance_group",
            "semantic_organ": None,
            "cell_selector": "group:affordances",
        },
        {
            "layer_index": 3,
            "name": "Sensor affordances",
            "layer_type": 0,
            "child_level": 2,
            "semantic_role": "sensor",
            "semantic_organ": "sensors",
            "cell_selector": "organ:sensors",
        },
        {
            "layer_index": 4,
            "name": "Expression affordances",
            "layer_type": 0,
            "child_level": 2,
            "semantic_role": "expression",
            "semantic_organ": "expression",
            "cell_selector": "organ:expression",
        },
    ]


def _tag_semantics() -> list[dict]:
    return [
        {
            "name": "idle_forward",
            "from_frame": 0,
            "to_frame": 3,
            "direction": 0,
            "repeat": 0,
            "color_rgb": [93, 187, 99],
            "user_data_color_rgba": [93, 187, 99, 255],
            "semantic_phase": "full_body_idle_forward",
        },
        {
            "name": "repair_reverse",
            "from_frame": 1,
            "to_frame": 3,
            "direction": 1,
            "repeat": 1,
            "color_rgb": [140, 163, 255],
            "user_data_color_rgba": [140, 163, 255, 255],
            "semantic_phase": "reverse_repair_recovery",
        },
        {
            "name": "sensor_pingpong",
            "from_frame": 0,
            "to_frame": 2,
            "direction": 2,
            "repeat": 2,
            "color_rgb": [216, 255, 214],
            "user_data_color_rgba": [216, 255, 214, 255],
            "semantic_phase": "sensor_affordance_pingpong",
        },
        {
            "name": "expression_pingpong_reverse",
            "from_frame": 1,
            "to_frame": 3,
            "direction": 3,
            "repeat": 3,
            "color_rgb": [255, 196, 87],
            "user_data_color_rgba": [255, 196, 87, 255],
            "semantic_phase": "expression_pingpong_reverse",
        },
    ]


def _raw_rgba_for_layer(grid: dict, layer: dict, frame_index: int) -> bytes:
    width, height = grid["grid_size"]
    cells_by_coordinate = {
        (cell["x"], cell["y"]): cell for cell in grid.get("cells", [])
    }
    payload = bytearray()
    for y in range(height):
        for x in range(width):
            cell = cells_by_coordinate.get((x, y))
            if cell and cell.get("organ") == layer["semantic_organ"]:
                red, green, blue, alpha = _hex_to_rgba(cell["visual"])
                if layer["semantic_role"] == "body_core" and frame_index == 3:
                    alpha = 224
                elif layer["semantic_role"] == "sensor" and frame_index in {1, 2}:
                    alpha = 176
                elif layer["semantic_role"] == "expression" and frame_index in {2, 3}:
                    alpha = 208
                payload.extend([red, green, blue, alpha])
            else:
                payload.extend([0, 0, 0, 0])
    return bytes(payload)


def _hex_to_rgba(value: str) -> tuple[int, int, int, int]:
    if not isinstance(value, str) or len(value) != 7 or not value.startswith("#"):
        raise ValueError(f"expected #RRGGBB color, got {value!r}")
    return (
        int(value[1:3], 16),
        int(value[3:5], 16),
        int(value[5:7], 16),
        255,
    )


def _frame_duration(frame_index: int) -> int:
    return [120, 90, 140, 110][frame_index]


def _cel_visual_hashes(project_bytes: bytes) -> dict:
    parsed = _parse_aseprite(project_bytes)
    cels = []
    for frame_index, frame in enumerate(parsed["frames"]):
        for chunk in frame["chunks"]:
            if chunk["type"] == ASE_CHUNK_CEL:
                cel = _parse_cel_chunk(
                    chunk["data"],
                    parsed["header"]["width"],
                    parsed["header"]["height"],
                )
                cel["frame_index"] = frame_index
                cels.append(cel)
    return _cel_hash_map(cels)


def _cel_hash_map(cels: list[dict]) -> dict:
    return {
        f"frame_{cel['frame_index']}_layer_{cel['layer_index']}": cel["cel_visual_hash"]
        for cel in cels
    }


def _tag_user_data_preserved(decoded: dict, metadata: dict) -> bool:
    current = [
        {
            "tag_name": entry.get("tag_name"),
            "semantic_phase": entry.get("semantic_phase"),
            "color_rgba": entry.get("color_rgba"),
        }
        for entry in decoded["tag_user_data"]
    ]
    expected = [
        {
            "tag_name": tag["name"],
            "semantic_phase": tag["semantic_phase"],
            "color_rgba": tag["user_data_color_rgba"],
        }
        for tag in metadata["tag_semantics"]
    ]
    return current == expected


def _invalid_probe_results(reference_result: dict) -> list[dict]:
    project_bytes = bytes.fromhex(reference_result["project_bytes_hex"])
    return [
        _compact_import_result(import_aseprite_nested_timeline_project(strip_aseprite_group_layer_chunks(project_bytes))),
        _compact_import_result(import_aseprite_nested_timeline_project(tamper_aseprite_nested_child_level(project_bytes))),
        _compact_import_result(import_aseprite_nested_timeline_project(strip_aseprite_tag_user_data_chunks(project_bytes))),
        _compact_import_result(import_aseprite_nested_timeline_project(tamper_aseprite_timeline_loop_direction(project_bytes))),
        _compact_import_result(import_aseprite_nested_timeline_project(tamper_aseprite_tag_user_data_color(project_bytes))),
        _compact_import_result(import_aseprite_nested_timeline_project(tamper_aseprite_nested_timeline_metadata(project_bytes))),
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
        "group_layer_count",
        "image_layer_count",
        "max_child_level",
        "tag_count",
        "cel_count",
        "chunk_count",
        "user_data_chunk_count",
        "layer_user_data_count",
        "tag_user_data_count",
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
    for result in payload["nested_timeline_results"]:
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
                "nested_timeline_roundtrip_count",
                "nested_timeline_roundtrip_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "nested_timeline_summaries": [
            {
                "profile_id": result["profile_id"],
                "format_id": result["format_id"],
                "project_byte_count": result["project_byte_count"],
                "embedded_project_hash": result["embedded_project_hash"],
                "canonical_project_hash": result["canonical_project_hash"],
                "decoded_project": result["decoded_project"],
                "semantic_fidelity": result["semantic_fidelity"],
            }
            for result in json_report["nested_timeline_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# Aseprite Nested Timeline Semantics Stage 0\n\n"
        "Aseprite/LibreSprite nested group, tag User Data, and timeline "
        "loop-direction semantic proof for one fixed four-frame carrier.\n\n"
        f"- Nested timeline round trips: {report['nested_timeline_roundtrip_success_count']}/"
        f"{report['nested_timeline_roundtrip_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}/"
        f"{report['invalid_probe_count']}\n"
        f"- Mean semantic fidelity: {metrics['mean_semantic_fidelity']}\n"
        f"- Cel visual hash preservation rate: {metrics['cel_visual_hash_preservation_rate']}\n"
        f"- Tag User Data preservation rate: {metrics['tag_user_data_preservation_rate']}\n"
        f"- Live external editor verified: {metrics['live_external_editor_verified']}\n\n"
        "This artifact does not claim live external editor validation, "
        "arbitrary Aseprite schemas, package runtime integration, or full "
        "project-format coverage.\n"
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
        default=Path("data/workshop_editor/aseprite_nested_timeline_semantics_stage0"),
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
    report = run_aseprite_nested_timeline_semantics_lab(profile_paths, args.generated_root)
    write_aseprite_nested_timeline_semantics_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_ASEPRITE_NESTED_TIMELINE_SEMANTICS = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(_json_report(report), indent=2))


if __name__ == "__main__":
    main()
