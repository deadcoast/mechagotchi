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
    _parse_user_data_chunk,
    _ratio,
    _unpack_string,
    _user_data_chunk_data,
    _write_aseprite,
)
from external_metadata_sidecar import build_sidecar_for_grid, restore_grid_from_sidecar
from workshop_editor import compare_semantic_grid_fidelity


ASE_CHUNK_TAGS = 0x2018
ASE_TAGS_LAYERS_VERSION = "mechagotchi.aseprite_tags_layers.v1"
ASE_TAGS_LAYERS_POLICY = "aseprite_tags_layers_native_semantics"
ASE_TAGS_LAYERS_NATIVE_LOCATION = "frame[0].layers[*].user_data.text + frame[0].tags"
REPORT_PATH = ROOT / "data/workshop_editor/aseprite_tags_layers_semantics_stage0.json"
DATA_PATH = ROOT / "data/workshop_editor/aseprite_tags_layers_semantics_data.js"


def export_aseprite_tags_layers_project(grid: dict, slip_profile: dict) -> dict:
    canonical_project = _encode_aseprite_tags_layers_project(grid, metadata=None)
    canonical_hash = _hash_bytes(canonical_project)
    cel_visual_hashes = _cel_visual_hashes(canonical_project)
    asset = {
        "asset_id": f"{grid['grid_id']}_tags_layers.aseprite",
        "format_id": "libresprite_project",
        "media_type": "application/octet-stream",
        "uri": f"generated://workshop/project-tags-layers/{grid['grid_id']}.aseprite",
        "width": grid["grid_size"][0],
        "height": grid["grid_size"][1],
        "frame_count": 3,
        "content_hash": canonical_hash,
        "semantic_policy": ASE_TAGS_LAYERS_POLICY,
    }
    sidecar = build_sidecar_for_grid(grid, slip_profile, asset)
    sidecar["sidecar_id"] = f"{grid['grid_id']}_aseprite_tags_layers_sidecar"
    sidecar["asset_binding"]["semantic_policy"] = ASE_TAGS_LAYERS_POLICY
    sidecar["project_binding"] = {
        "format_id": "libresprite_project",
        "decoder_scope": "aseprite_multiframe_multilayer_tags_user_data_subset",
        "native_mechagotchi_semantics": True,
        "semantic_policy": ASE_TAGS_LAYERS_POLICY,
        "native_metadata_version": ASE_TAGS_LAYERS_VERSION,
    }
    sidecar["limitations"] = [
        "Stage 0 Aseprite/LibreSprite tags/layers proof covers three semantic layers, three frames, one Tags chunk, and compressed RGBA cels.",
        "Live external editor rewrite validation is not verified by this lab.",
        "Arbitrary Aseprite project schemas, tilemaps, tilesets, linked cels, nested groups, timeline variants, and full project-format coverage remain separate; palette/slice semantics are covered by a later Stage 0 lab.",
    ]
    metadata = _build_tags_layers_metadata(canonical_hash, cel_visual_hashes, sidecar)
    project_bytes = _encode_aseprite_tags_layers_project(grid, metadata=metadata)
    decoded = decode_aseprite_tags_layers_project(project_bytes)
    return {
        "project_bytes": project_bytes,
        "canonical_project_bytes": canonical_project,
        "embedded_project_hash": _hash_bytes(project_bytes),
        "canonical_project_hash": canonical_hash,
        "metadata": metadata,
        "sidecar": sidecar,
        "decoded_project": decoded,
    }


def decode_aseprite_tags_layers_project(project_bytes: bytes) -> dict:
    parsed = _parse_aseprite(project_bytes)
    layers = []
    tags = []
    cels = []
    user_data_chunks = []
    layer_user_data = []
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
                for tag in parsed_tags:
                    tag["index"] = len(tags)
                    tag["frame_index"] = frame_index
                    tags.append(tag)
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
                    native = True
                    try:
                        metadata = json.loads(text[len(ASE_USER_DATA_PREFIX) :])
                    except json.JSONDecodeError as exc:
                        raise AsepriteUserDataError("aseprite_tags_layers_json_invalid", str(exc)) from exc
                    layer_binding = metadata.get("layer_binding", {})
                    if target["target_type"] == "layer":
                        entry["semantic_role"] = layer_binding.get("semantic_role")
                        entry["semantic_organ"] = layer_binding.get("semantic_organ")
                        layer_user_data.append(entry)
                user_data_chunks.append(entry)

    cel_hashes = _cel_hash_map(cels)
    return {
        "format_id": "libresprite_project",
        "magic": hex(parsed["header"]["magic"]),
        "frame_magic": hex(parsed["frames"][0]["magic"]) if parsed["frames"] else None,
        "dimensions": [parsed["header"]["width"], parsed["header"]["height"]],
        "frame_count": parsed["header"]["frames"],
        "layer_count": len(layers),
        "tag_count": len(tags),
        "cel_count": len(cels),
        "chunk_count": total_chunk_count,
        "user_data_chunk_count": len(user_data_chunks),
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
        "native_mechagotchi_semantics": native,
    }


def extract_aseprite_tags_layers_sidecar(project_bytes: bytes) -> dict:
    decoded = decode_aseprite_tags_layers_project(project_bytes)
    metadata = _extract_tags_layers_metadata(project_bytes)
    if metadata.get("metadata_version") != ASE_TAGS_LAYERS_VERSION:
        raise AsepriteUserDataError(
            "aseprite_tags_layers_version_unsupported",
            "unsupported Aseprite tags/layers metadata version",
        )
    if metadata.get("format_id") != "libresprite_project":
        raise AsepriteUserDataError(
            "aseprite_tags_layers_format_mismatch",
            "Aseprite tags/layers metadata format id mismatch",
        )
    if not decoded["tags"]:
        raise AsepriteUserDataError(
            "aseprite_tags_missing",
            "Aseprite tags/layers project must contain a Tags Chunk 0x2018",
        )
    _validate_tags(decoded["tags"], decoded["frame_count"], metadata)
    _validate_layers(decoded, metadata)

    sidecar = metadata.get("sidecar")
    if not isinstance(sidecar, dict):
        raise AsepriteUserDataError(
            "aseprite_tags_layers_sidecar_missing",
            "Aseprite tags/layers metadata must contain a sidecar object",
        )
    if _hash_payload(sidecar) != metadata.get("sidecar_hash"):
        raise AsepriteUserDataError(
            "aseprite_tags_layers_sidecar_hash_mismatch",
            "Aseprite tags/layers sidecar hash does not match the embedded sidecar",
        )
    if decoded.get("cel_visual_hashes") != metadata.get("cel_visual_hashes"):
        raise AsepriteUserDataError(
            "aseprite_tags_layers_visual_hash_mismatch",
            "Aseprite tags/layers cel visual hashes do not match current cel payloads",
        )
    canonical = strip_aseprite_tags_layers_user_data_chunks(project_bytes)
    canonical_hash = _hash_bytes(canonical)
    if canonical_hash != metadata.get("canonical_project_hash"):
        raise AsepriteUserDataError(
            "aseprite_tags_layers_canonical_hash_mismatch",
            "Aseprite tags/layers canonical project hash does not match the stripped project",
        )
    if sidecar.get("asset_binding", {}).get("content_hash") != canonical_hash:
        raise AsepriteUserDataError(
            "aseprite_tags_layers_sidecar_asset_hash_mismatch",
            "Aseprite tags/layers sidecar asset hash does not match the canonical project hash",
        )
    return {
        "ok": True,
        "metadata": metadata,
        "sidecar": sidecar,
        "decoded_project": _decoded_project_summary(decoded),
        "canonical_project_hash": canonical_hash,
        "embedded_project_hash": _hash_bytes(project_bytes),
    }


def import_aseprite_tags_layers_project(project_bytes: bytes, source_grid: dict | None = None) -> dict:
    try:
        extracted = extract_aseprite_tags_layers_sidecar(project_bytes)
    except AsepriteUserDataError as exc:
        return _failed_import("aseprite_tags_layers", exc.family, exc.message)

    sidecar = extracted["sidecar"]
    asset = deepcopy(sidecar["asset_binding"])
    try:
        restored = restore_grid_from_sidecar(sidecar, asset)
    except ValueError as exc:
        return _failed_import("sidecar", "aseprite_tags_layers_sidecar_invalid", str(exc))

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
            "semantic_policy": ASE_TAGS_LAYERS_POLICY,
            "native_mechagotchi_semantics": True,
            "native_location": ASE_TAGS_LAYERS_NATIVE_LOCATION,
            "layer_user_data_chunk_type": "0x2020",
            "tags_chunk_type": "0x2018",
            "live_external_editor_verified": False,
        },
        "semantic_diff": diff,
        "semantic_fidelity": fidelity,
        "errors": errors,
        "error_families": sorted({error["family"] for error in errors}),
    }


def strip_aseprite_tags_layers_user_data_chunks(project_bytes: bytes) -> bytes:
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


def strip_aseprite_tags_chunk(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    frames = []
    for frame in parsed["frames"]:
        frames.append(
            {
                "duration_ms": frame["duration_ms"],
                "chunks": [
                    chunk
                    for chunk in frame["chunks"]
                    if chunk["type"] != ASE_CHUNK_TAGS
                ],
            }
        )
    return _write_aseprite(parsed["header"], frames)


def tamper_aseprite_tag_range(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    replaced = False
    frames = []
    for frame in parsed["frames"]:
        chunks = []
        for chunk in frame["chunks"]:
            if chunk["type"] == ASE_CHUNK_TAGS and not replaced:
                tags = _parse_tags_chunk(chunk["data"])
                tags[0]["to_frame"] = parsed["header"]["frames"] + 1
                chunks.append(_chunk(ASE_CHUNK_TAGS, _tags_chunk_data(tags)))
                replaced = True
                continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    if not replaced:
        raise AsepriteUserDataError("aseprite_tags_missing", "no Aseprite Tags chunk found")
    return _write_aseprite(parsed["header"], frames)


def tamper_aseprite_layer_user_data(project_bytes: bytes) -> bytes:
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
                    metadata["sidecar"]["asset_binding"]["width"] += 1
                    chunks.append(_chunk(ASE_CHUNK_USER_DATA, _user_data_chunk_data(metadata)))
                    replaced = True
                    continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    if not replaced:
        raise AsepriteUserDataError("aseprite_tags_layers_metadata_missing", "no Mechagotchi layer User Data chunk found")
    return _write_aseprite(parsed["header"], frames)


def tamper_aseprite_layer_user_data_json(project_bytes: bytes) -> bytes:
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
                    corrupted = struct.pack("<I", 1) + _pack_string(ASE_USER_DATA_PREFIX + '{"metadata_version":')
                    chunks.append(_chunk(ASE_CHUNK_USER_DATA, corrupted))
                    replaced = True
                    continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    if not replaced:
        raise AsepriteUserDataError("aseprite_tags_layers_metadata_missing", "no Mechagotchi layer User Data chunk found")
    return _write_aseprite(parsed["header"], frames)


def tamper_aseprite_layer_visual_payload(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    replaced = False
    frames = []
    for frame in parsed["frames"]:
        chunks = []
        for chunk in frame["chunks"]:
            if chunk["type"] == ASE_CHUNK_CEL and not replaced:
                cel = _parse_cel_chunk(chunk["data"], parsed["header"]["width"], parsed["header"]["height"])
                raw = bytearray(cel["raw_rgba"])
                raw[0] = (raw[0] + 1) % 256
                chunks.append(
                    _chunk(
                        ASE_CHUNK_CEL,
                        _cel_chunk_data(
                            cel["layer_index"],
                            parsed["header"]["width"],
                            parsed["header"]["height"],
                            bytes(raw),
                        ),
                    )
                )
                replaced = True
                continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    if not replaced:
        raise AsepriteUserDataError("aseprite_cel_chunk_missing", "no compressed cel chunk found")
    return _write_aseprite(parsed["header"], frames)


def run_aseprite_tags_layers_semantics_lab(profile_paths: list[Path], generated_root: Path) -> dict:
    tags_layers_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        exported = export_aseprite_tags_layers_project(grid, profile)
        imported = import_aseprite_tags_layers_project(exported["project_bytes"], source_grid=grid)
        decoded = exported["decoded_project"]
        tags_layers_results.append(
            {
                "profile_id": profile["profile_id"],
                "profile_path": _portable(profile_path),
                "grid_path": _portable(grid_path),
                "format_id": "libresprite_project",
                "project_file_name": f"{profile['profile_id']}_tags_layers.aseprite",
                "project_bytes_hex": exported["project_bytes"].hex(),
                "project_byte_count": len(exported["project_bytes"]),
                "embedded_project_hash": exported["embedded_project_hash"],
                "canonical_project_hash": exported["canonical_project_hash"],
                "metadata": _metadata_summary(exported["metadata"]),
                "native_sidecar": exported["sidecar"],
                "decoded_project": _decoded_project_summary(decoded),
                "layer_semantics": exported["metadata"]["layer_semantics"],
                "tag_semantics": exported["metadata"]["tag_semantics"],
                "import_result": _compact_import_result(imported),
                "restored_grid_validation": imported.get("restored_grid_validation", {}),
                "semantic_diff": imported.get("semantic_diff", {}),
                "semantic_fidelity": imported.get("semantic_fidelity", 0.0),
                "cel_visual_hashes_preserved": (
                    exported["metadata"]["cel_visual_hashes"]
                    == decoded["cel_visual_hashes"]
                ),
            }
        )

    invalid_probe_results = _invalid_probe_results(tags_layers_results[0])
    success_count = sum(
        1
        for result in tags_layers_results
        if result["import_result"]["ok"]
        and result["restored_grid_validation"].get("valid")
        and result["restored_grid_validation"].get("slip_aligned")
        and result["semantic_fidelity"] == 1.0
    )
    invalid_rejected_count = sum(1 for result in invalid_probe_results if not result["ok"])
    visual_hash_preserved = sum(1 for result in tags_layers_results if result["cel_visual_hashes_preserved"])
    return {
        "artifact_id": "aseprite_tags_layers_semantics_stage0",
        "status": "research_aseprite_tags_layers_semantics_no_package_code",
        "date": "2026-05-14",
        "purpose": (
            "Prove a Stage 0 Aseprite/LibreSprite native tags/layers semantic "
            "subset with three frames, three semantic layers, Tags Chunk 0x2018, "
            "Layer/User Data Chunk 0x2020 bindings, and compressed RGBA cels "
            "without claiming arbitrary project schema coverage or live editor validation."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
            "labs/workshop_editor/aseprite_user_data_chunk_writer.py",
            "labs/workshop_editor/aseprite_tags_layers_semantics.py",
        ],
        "external_anchors": [
            {
                "source": "Aseprite file-format specification",
                "url": "https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md",
                "used_for": "ASE header, frame header, Layer Chunk 0x2004, Tags Chunk 0x2018, User Data Chunk 0x2020, and compressed Cel Chunk 0x2005 layout.",
            },
            {
                "source": "LibreSprite GitHub",
                "url": "https://github.com/LibreSprite/LibreSprite",
                "used_for": "LibreSprite remains a compatibility boundary; no GPL editor code is embedded.",
            },
        ],
        "profile_count": len(profile_paths),
        "tags_layers_roundtrip_count": len(tags_layers_results),
        "tags_layers_roundtrip_success_count": success_count,
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "metrics": {
            "tags_layers_roundtrip_success_rate": _ratio(success_count, len(tags_layers_results)),
            "mean_semantic_fidelity": round(
                sum(result["semantic_fidelity"] for result in tags_layers_results)
                / max(1, len(tags_layers_results)),
                6,
            ),
            "cel_visual_hash_preservation_rate": _ratio(
                visual_hash_preserved,
                len(tags_layers_results),
            ),
            "invalid_probe_rejection_rate": _ratio(
                invalid_rejected_count,
                len(invalid_probe_results),
            ),
            "live_external_editor_verified": False,
        },
        "tags_layers_results": tags_layers_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "aseprite_tags_layers_native_semantics_subset",
            "aseprite_frame_tags_semantic_ranges",
            "aseprite_layer_user_data_semantic_roles",
            "aseprite_multilayer_compressed_rgba_cel_subset",
            "aseprite_tags_layers_sidecar_semantic_restore",
            "aseprite_tags_layers_hash_validation",
        ],
        "blocked_states": [
            "live_external_editor_rewrite_validation",
            "arbitrary_aseprite_project_schema_coverage",
            "advanced_tags_layers_timeline_schema_coverage",
            "full_project_format_coverage",
            "package_runtime_lifecycle_integration",
            "manual_readability_calibration",
            "profile_weighted_evolution",
            "community_profile_packs",
        ],
        "decision": "prototype_aseprite_tags_layers_native_semantics_subset",
        "next_research_step": (
            "Keep live external editor validation, arbitrary Aseprite project "
            "schemas, advanced layer/tag/timeline variants, and full "
            "project-format coverage blocked until direct editor fixtures and "
            "broader chunk/schema tests exist."
        ),
    }


def write_aseprite_tags_layers_semantics_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "aseprite_tags_layers_semantics_stage0.json", _json_report(report))
    for result in report["tags_layers_results"]:
        (output_dir / result["project_file_name"]).write_bytes(
            bytes.fromhex(result["project_bytes_hex"])
        )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "aseprite_tags_layers_semantics_data.js").write_text(
        "window.MECHAGOTCHI_ASEPRITE_TAGS_LAYERS_SEMANTICS = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _encode_aseprite_tags_layers_project(grid: dict, metadata: dict | None) -> bytes:
    width, height = grid["grid_size"]
    layers = _layer_semantics()
    tags = _tag_semantics()
    frames = []
    for frame_index in range(3):
        chunks = []
        if frame_index == 0:
            for layer in layers:
                chunks.append(_chunk(ASE_CHUNK_LAYER, _layer_chunk_data(width, height, layer["name"])))
                if metadata is not None:
                    layer_metadata = deepcopy(metadata)
                    layer_metadata["layer_binding"] = layer
                    chunks.append(_chunk(ASE_CHUNK_USER_DATA, _user_data_chunk_data(layer_metadata)))
            chunks.append(_chunk(ASE_CHUNK_TAGS, _tags_chunk_data(tags)))
        for layer in layers:
            raw_rgba = _raw_rgba_for_layer(grid, layer, frame_index)
            chunks.append(_chunk(ASE_CHUNK_CEL, _cel_chunk_data(layer["layer_index"], width, height, raw_rgba)))
        frames.append({"duration_ms": 120, "chunks": chunks})
    header = {
        "frames": 3,
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


def _layer_chunk_data(width: int, height: int, name: str) -> bytes:
    return (
        struct.pack("<HHHHHHB3s", 3, 0, 0, width, height, 0, 255, b"\x00\x00\x00")
        + _pack_string(name)
    )


def _cel_chunk_data(layer_index: int, width: int, height: int, raw_rgba: bytes) -> bytes:
    expected_length = width * height * 4
    if len(raw_rgba) != expected_length:
        raise ValueError("raw RGBA payload does not match dimensions")
    return (
        struct.pack("<HhhBHh5sHH", layer_index, 0, 0, 255, 2, 0, b"\x00" * 5, width, height)
        + zlib.compress(raw_rgba)
    )


def _tags_chunk_data(tags: list[dict]) -> bytes:
    payload = bytearray(struct.pack("<H8s", len(tags), b"\x00" * 8))
    for tag in tags:
        color = tag["color_rgb"]
        payload.extend(
            struct.pack(
                "<HHBH6sBBBB",
                tag["from_frame"],
                tag["to_frame"],
                tag["direction"],
                tag["repeat"],
                b"\x00" * 6,
                color[0],
                color[1],
                color[2],
                0,
            )
        )
        payload.extend(_pack_string(tag["name"]))
    return bytes(payload)


def _parse_tags_chunk(data: bytes) -> list[dict]:
    if len(data) < 10:
        raise AsepriteUserDataError("aseprite_tags_chunk_truncated", "Aseprite Tags chunk is truncated")
    tag_count = struct.unpack("<H", data[:2])[0]
    offset = 10
    tags = []
    fixed_size = struct.calcsize("<HHBH6sBBBB")
    for _index in range(tag_count):
        if offset + fixed_size > len(data):
            raise AsepriteUserDataError("aseprite_tags_chunk_truncated", "Aseprite tag entry is truncated")
        from_frame, to_frame, direction, repeat, _reserved, red, green, blue, extra = struct.unpack(
            "<HHBH6sBBBB",
            data[offset : offset + fixed_size],
        )
        offset += fixed_size
        name, offset = _unpack_string(data, offset)
        tags.append(
            {
                "chunk_type": "0x2018",
                "from_frame": from_frame,
                "to_frame": to_frame,
                "direction": direction,
                "repeat": repeat,
                "color_rgb": [red, green, blue],
                "extra": extra,
                "name": name,
            }
        )
    if offset != len(data):
        raise AsepriteUserDataError("aseprite_tags_chunk_extra_bytes", "unexpected bytes after Aseprite Tags chunk")
    return tags


def _build_tags_layers_metadata(canonical_hash: str, cel_visual_hashes: dict, sidecar: dict) -> dict:
    return {
        "metadata_version": ASE_TAGS_LAYERS_VERSION,
        "format_id": "libresprite_project",
        "native_location": ASE_TAGS_LAYERS_NATIVE_LOCATION,
        "writer_policy": ASE_TAGS_LAYERS_POLICY,
        "canonical_project_hash": canonical_hash,
        "cel_visual_hashes": cel_visual_hashes,
        "sidecar_hash": _hash_payload(sidecar),
        "sidecar": sidecar,
        "layer_semantics": _layer_semantics(),
        "tag_semantics": _tag_semantics(),
    }


def _extract_tags_layers_metadata(project_bytes: bytes) -> dict:
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
                    raise AsepriteUserDataError("aseprite_tags_layers_json_invalid", str(exc)) from exc
                if metadata.get("metadata_version") == ASE_TAGS_LAYERS_VERSION:
                    return metadata
    raise AsepriteUserDataError(
        "aseprite_tags_layers_metadata_missing",
        "ASE project does not contain Mechagotchi tags/layers User Data metadata",
    )


def _validate_tags(tags: list[dict], frame_count: int, metadata: dict) -> None:
    for tag in tags:
        if tag["from_frame"] > tag["to_frame"] or tag["to_frame"] >= frame_count:
            raise AsepriteUserDataError(
                "aseprite_tag_range_invalid",
                "Aseprite tag frame range must be within project frames",
            )
        if tag["direction"] not in {0, 1, 2, 3}:
            raise AsepriteUserDataError(
                "aseprite_tag_direction_invalid",
                "Aseprite tag direction must be one of the documented directions",
            )
    expected = [
        {
            key: tag[key]
            for key in ["name", "from_frame", "to_frame", "direction", "repeat", "color_rgb"]
        }
        for tag in metadata.get("tag_semantics", [])
    ]
    current = [
        {
            key: tag[key]
            for key in ["name", "from_frame", "to_frame", "direction", "repeat", "color_rgb"]
        }
        for tag in tags
    ]
    if current != expected:
        raise AsepriteUserDataError(
            "aseprite_tag_semantics_mismatch",
            "Aseprite tag semantics do not match embedded metadata",
        )


def _validate_layers(decoded: dict, metadata: dict) -> None:
    expected = metadata.get("layer_semantics", [])
    if decoded["layer_count"] != len(expected):
        raise AsepriteUserDataError(
            "aseprite_layer_count_mismatch",
            "Aseprite layer count does not match embedded layer semantics",
        )
    if decoded["user_data_chunk_count"] < len(expected):
        raise AsepriteUserDataError(
            "aseprite_layer_user_data_missing",
            "Aseprite layer User Data chunks are required for each semantic layer",
        )
    if len(decoded["layer_user_data"]) != len(expected):
        raise AsepriteUserDataError(
            "aseprite_layer_user_data_missing",
            "Aseprite layer User Data chunks must bind to each semantic layer",
        )
    current_names = [layer["name"] for layer in decoded["layers"]]
    expected_names = [layer["name"] for layer in expected]
    if current_names != expected_names:
        raise AsepriteUserDataError(
            "aseprite_layer_semantics_mismatch",
            "Aseprite layer names do not match embedded semantic layers",
        )
    current_bindings = [
        {
            "layer_index": entry["target_index"],
            "semantic_role": entry.get("semantic_role"),
            "semantic_organ": entry.get("semantic_organ"),
        }
        for entry in decoded["layer_user_data"]
    ]
    expected_bindings = [
        {
            "layer_index": layer["layer_index"],
            "semantic_role": layer["semantic_role"],
            "semantic_organ": layer["semantic_organ"],
        }
        for layer in expected
    ]
    if current_bindings != expected_bindings:
        raise AsepriteUserDataError(
            "aseprite_layer_user_data_semantics_mismatch",
            "Aseprite layer User Data semantic roles do not match embedded layer semantics",
        )


def _layer_semantics() -> list[dict]:
    return [
        {
            "layer_index": 0,
            "name": "Mechagotchi body",
            "semantic_role": "body_core",
            "semantic_organ": "core",
            "cell_selector": "organ:core",
        },
        {
            "layer_index": 1,
            "name": "Mechagotchi sensors",
            "semantic_role": "sensor",
            "semantic_organ": "sensors",
            "cell_selector": "organ:sensors",
        },
        {
            "layer_index": 2,
            "name": "Mechagotchi expression",
            "semantic_role": "expression",
            "semantic_organ": "expression",
            "cell_selector": "organ:expression",
        },
    ]


def _tag_semantics() -> list[dict]:
    return [
        {
            "name": "idle_loop",
            "from_frame": 0,
            "to_frame": 2,
            "direction": 0,
            "repeat": 0,
            "color_rgb": [93, 187, 99],
            "semantic_meaning": "baseline body persistence over the full three-frame loop",
        },
        {
            "name": "sensor_blink",
            "from_frame": 0,
            "to_frame": 1,
            "direction": 2,
            "repeat": 0,
            "color_rgb": [216, 255, 214],
            "semantic_meaning": "sensor affordance pulse over the first two frames",
        },
        {
            "name": "expression_pulse",
            "from_frame": 1,
            "to_frame": 2,
            "direction": 0,
            "repeat": 1,
            "color_rgb": [255, 196, 87],
            "semantic_meaning": "expression affordance pulse over the final two frames",
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
                if layer["semantic_role"] == "sensor" and frame_index == 1:
                    alpha = 176
                elif layer["semantic_role"] == "expression" and frame_index == 2:
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


def _invalid_probe_results(reference_result: dict) -> list[dict]:
    project_bytes = bytes.fromhex(reference_result["project_bytes_hex"])
    return [
        _compact_import_result(import_aseprite_tags_layers_project(strip_aseprite_tags_chunk(project_bytes))),
        _compact_import_result(import_aseprite_tags_layers_project(tamper_aseprite_tag_range(project_bytes))),
        _compact_import_result(import_aseprite_tags_layers_project(tamper_aseprite_layer_user_data(project_bytes))),
        _compact_import_result(import_aseprite_tags_layers_project(tamper_aseprite_layer_user_data_json(project_bytes))),
        _compact_import_result(import_aseprite_tags_layers_project(tamper_aseprite_layer_visual_payload(project_bytes))),
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
        "chunk_count",
        "user_data_chunk_count",
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
    for result in payload["tags_layers_results"]:
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
                "tags_layers_roundtrip_count",
                "tags_layers_roundtrip_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "tags_layers_summaries": [
            {
                "profile_id": result["profile_id"],
                "format_id": result["format_id"],
                "project_byte_count": result["project_byte_count"],
                "embedded_project_hash": result["embedded_project_hash"],
                "canonical_project_hash": result["canonical_project_hash"],
                "decoded_project": result["decoded_project"],
                "semantic_fidelity": result["semantic_fidelity"],
            }
            for result in json_report["tags_layers_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# Aseprite Tags/Layers Semantics Stage 0\n\n"
        "Aseprite/LibreSprite tags/layers semantic proof for three-frame, "
        "three-layer, compressed RGBA cel payloads with embedded Mechagotchi "
        "layer User Data and frame tags.\n\n"
        f"- Tags/layers round trips: {report['tags_layers_roundtrip_success_count']}/"
        f"{report['tags_layers_roundtrip_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}/"
        f"{report['invalid_probe_count']}\n"
        f"- Mean semantic fidelity: {metrics['mean_semantic_fidelity']}\n"
        f"- Cel visual hash preservation rate: {metrics['cel_visual_hash_preservation_rate']}\n"
        f"- Live external editor verified: {metrics['live_external_editor_verified']}\n\n"
        "This artifact does not claim live external editor validation, "
        "arbitrary Aseprite schemas, advanced timelines, package runtime "
        "integration, or full project-format coverage.\n"
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
        default=ROOT / "data/workshop_editor/aseprite_tags_layers_semantics_stage0",
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
    report = run_aseprite_tags_layers_semantics_lab(profile_paths, args.generated_root)
    write_aseprite_tags_layers_semantics_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_ASEPRITE_TAGS_LAYERS_SEMANTICS = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(_json_report(report), indent=2))


if __name__ == "__main__":
    main()
