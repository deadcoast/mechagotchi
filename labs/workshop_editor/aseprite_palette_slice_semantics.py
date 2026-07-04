import argparse
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

from aseprite_tags_layers_semantics import (
    ASE_CHUNK_TAGS,
    ASE_TAGS_LAYERS_VERSION,
    _cel_chunk_data,
    _cel_hash_map,
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


ASE_CHUNK_PALETTE = 0x2019
ASE_CHUNK_SLICE = 0x2022
ASE_PALETTE_SLICE_VERSION = "mechagotchi.aseprite_palette_slice.v1"
ASE_PALETTE_SLICE_POLICY = "aseprite_palette_slice_native_semantics"
ASE_PALETTE_SLICE_NATIVE_LOCATION = (
    "frame[0].palette + frame[0].slices + frame[0].layers[*].user_data.text"
)
REPORT_PATH = ROOT / "data/workshop_editor/aseprite_palette_slice_semantics_stage0.json"
DATA_PATH = ROOT / "data/workshop_editor/aseprite_palette_slice_semantics_data.js"


def export_aseprite_palette_slice_project(grid: dict, slip_profile: dict) -> dict:
    canonical_project = _encode_aseprite_palette_slice_project(grid, metadata=None)
    canonical_hash = _hash_bytes(canonical_project)
    cel_visual_hashes = _cel_visual_hashes(canonical_project)
    asset = {
        "asset_id": f"{grid['grid_id']}_palette_slice.aseprite",
        "format_id": "libresprite_project",
        "media_type": "application/octet-stream",
        "uri": f"generated://workshop/project-palette-slice/{grid['grid_id']}.aseprite",
        "width": grid["grid_size"][0],
        "height": grid["grid_size"][1],
        "frame_count": 3,
        "content_hash": canonical_hash,
        "semantic_policy": ASE_PALETTE_SLICE_POLICY,
    }
    sidecar = build_sidecar_for_grid(grid, slip_profile, asset)
    sidecar["sidecar_id"] = f"{grid['grid_id']}_aseprite_palette_slice_sidecar"
    sidecar["asset_binding"]["semantic_policy"] = ASE_PALETTE_SLICE_POLICY
    sidecar["project_binding"] = {
        "format_id": "libresprite_project",
        "decoder_scope": "aseprite_palette_slice_tags_layers_user_data_subset",
        "native_mechagotchi_semantics": True,
        "semantic_policy": ASE_PALETTE_SLICE_POLICY,
        "native_metadata_version": ASE_PALETTE_SLICE_VERSION,
    }
    sidecar["limitations"] = [
        "Stage 0 Aseprite/LibreSprite palette/slice proof covers Palette Chunk 0x2019, semantic Slice Chunk 0x2022 bounds, three semantic layers, three frame tags, and compressed RGBA cels.",
        "Live external editor rewrite validation is not verified by this lab.",
        "Arbitrary Aseprite project schemas, tilemaps, tilesets, linked cels, nested groups, advanced timeline variants, and full project-format coverage remain separate.",
    ]
    metadata = _build_palette_slice_metadata(
        canonical_hash,
        cel_visual_hashes,
        grid,
        sidecar,
    )
    project_bytes = _encode_aseprite_palette_slice_project(grid, metadata=metadata)
    decoded = decode_aseprite_palette_slice_project(project_bytes)
    return {
        "project_bytes": project_bytes,
        "canonical_project_bytes": canonical_project,
        "embedded_project_hash": _hash_bytes(project_bytes),
        "canonical_project_hash": canonical_hash,
        "metadata": metadata,
        "sidecar": sidecar,
        "decoded_project": decoded,
    }


def decode_aseprite_palette_slice_project(project_bytes: bytes) -> dict:
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
                    try:
                        metadata = json.loads(text[len(ASE_USER_DATA_PREFIX) :])
                    except json.JSONDecodeError as exc:
                        raise AsepriteUserDataError("aseprite_palette_slice_json_invalid", str(exc)) from exc
                    if metadata.get("metadata_version") == ASE_PALETTE_SLICE_VERSION:
                        native = True
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


def extract_aseprite_palette_slice_sidecar(project_bytes: bytes) -> dict:
    decoded = decode_aseprite_palette_slice_project(project_bytes)
    metadata = _extract_palette_slice_metadata(project_bytes)
    if metadata.get("metadata_version") != ASE_PALETTE_SLICE_VERSION:
        raise AsepriteUserDataError(
            "aseprite_palette_slice_version_unsupported",
            "unsupported Aseprite palette/slice metadata version",
        )
    if metadata.get("format_id") != "libresprite_project":
        raise AsepriteUserDataError(
            "aseprite_palette_slice_format_mismatch",
            "Aseprite palette/slice metadata format id mismatch",
        )
    _validate_palette(decoded, metadata)
    _validate_slices(decoded, metadata)
    _validate_tags(decoded["tags"], decoded["frame_count"], metadata)
    _validate_layers(decoded, metadata)

    sidecar = metadata.get("sidecar")
    if not isinstance(sidecar, dict):
        raise AsepriteUserDataError(
            "aseprite_palette_slice_sidecar_missing",
            "Aseprite palette/slice metadata must contain a sidecar object",
        )
    if _hash_payload(sidecar) != metadata.get("sidecar_hash"):
        raise AsepriteUserDataError(
            "aseprite_palette_slice_sidecar_hash_mismatch",
            "Aseprite palette/slice sidecar hash does not match the embedded sidecar",
        )
    if decoded.get("cel_visual_hashes") != metadata.get("cel_visual_hashes"):
        raise AsepriteUserDataError(
            "aseprite_palette_slice_visual_hash_mismatch",
            "Aseprite palette/slice cel visual hashes do not match current cel payloads",
        )
    canonical = strip_aseprite_palette_slice_user_data_chunks(project_bytes)
    canonical_hash = _hash_bytes(canonical)
    if canonical_hash != metadata.get("canonical_project_hash"):
        raise AsepriteUserDataError(
            "aseprite_palette_slice_canonical_hash_mismatch",
            "Aseprite palette/slice canonical project hash does not match the stripped project",
        )
    if sidecar.get("asset_binding", {}).get("content_hash") != canonical_hash:
        raise AsepriteUserDataError(
            "aseprite_palette_slice_sidecar_asset_hash_mismatch",
            "Aseprite palette/slice sidecar asset hash does not match the canonical project hash",
        )
    return {
        "ok": True,
        "metadata": metadata,
        "sidecar": sidecar,
        "decoded_project": _decoded_project_summary(decoded),
        "canonical_project_hash": canonical_hash,
        "embedded_project_hash": _hash_bytes(project_bytes),
    }


def import_aseprite_palette_slice_project(project_bytes: bytes, source_grid: dict | None = None) -> dict:
    try:
        extracted = extract_aseprite_palette_slice_sidecar(project_bytes)
    except AsepriteUserDataError as exc:
        return _failed_import("aseprite_palette_slice", exc.family, exc.message)

    sidecar = extracted["sidecar"]
    asset = deepcopy(sidecar["asset_binding"])
    try:
        restored = restore_grid_from_sidecar(sidecar, asset)
    except ValueError as exc:
        return _failed_import("sidecar", "aseprite_palette_slice_sidecar_invalid", str(exc))

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
            "semantic_policy": ASE_PALETTE_SLICE_POLICY,
            "native_mechagotchi_semantics": True,
            "native_location": ASE_PALETTE_SLICE_NATIVE_LOCATION,
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


def strip_aseprite_palette_slice_user_data_chunks(project_bytes: bytes) -> bytes:
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


def strip_aseprite_palette_chunk(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    frames = []
    for frame in parsed["frames"]:
        frames.append(
            {
                "duration_ms": frame["duration_ms"],
                "chunks": [
                    chunk
                    for chunk in frame["chunks"]
                    if chunk["type"] != ASE_CHUNK_PALETTE
                ],
            }
        )
    return _write_aseprite(parsed["header"], frames)


def strip_aseprite_slice_chunks(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    frames = []
    for frame in parsed["frames"]:
        frames.append(
            {
                "duration_ms": frame["duration_ms"],
                "chunks": [
                    chunk
                    for chunk in frame["chunks"]
                    if chunk["type"] != ASE_CHUNK_SLICE
                ],
            }
        )
    return _write_aseprite(parsed["header"], frames)


def tamper_aseprite_palette_entry(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    replaced = False
    frames = []
    for frame in parsed["frames"]:
        chunks = []
        for chunk in frame["chunks"]:
            if chunk["type"] == ASE_CHUNK_PALETTE and not replaced:
                palette = _parse_palette_chunk(chunk["data"])
                palette["entries"][0]["rgba"][0] = (palette["entries"][0]["rgba"][0] + 1) % 256
                chunks.append(_chunk(ASE_CHUNK_PALETTE, _palette_chunk_data_from_palette(palette)))
                replaced = True
                continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    if not replaced:
        raise AsepriteUserDataError("aseprite_palette_missing", "no Aseprite Palette chunk found")
    return _write_aseprite(parsed["header"], frames)


def tamper_aseprite_slice_bounds(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    replaced = False
    frames = []
    for frame in parsed["frames"]:
        chunks = []
        for chunk in frame["chunks"]:
            if chunk["type"] == ASE_CHUNK_SLICE and not replaced:
                parsed_slice = _parse_slice_chunk(chunk["data"])
                parsed_slice["keys"][0]["bounds"]["x"] = parsed["header"]["width"] + 1
                chunks.append(_chunk(ASE_CHUNK_SLICE, _slice_chunk_data_from_slice(parsed_slice)))
                replaced = True
                continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    if not replaced:
        raise AsepriteUserDataError("aseprite_slices_missing", "no Aseprite Slice chunk found")
    return _write_aseprite(parsed["header"], frames)


def tamper_aseprite_palette_slice_metadata(project_bytes: bytes) -> bytes:
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
                    if metadata.get("metadata_version") == ASE_PALETTE_SLICE_VERSION:
                        metadata["sidecar"]["asset_binding"]["width"] += 1
                        chunks.append(_chunk(ASE_CHUNK_USER_DATA, _user_data_chunk_data(metadata)))
                        replaced = True
                        continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    if not replaced:
        raise AsepriteUserDataError(
            "aseprite_palette_slice_metadata_missing",
            "no Mechagotchi palette/slice User Data chunk found",
        )
    return _write_aseprite(parsed["header"], frames)


def tamper_aseprite_palette_slice_metadata_json(project_bytes: bytes) -> bytes:
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
        raise AsepriteUserDataError("aseprite_palette_slice_metadata_missing", "no Mechagotchi palette/slice User Data chunk found")
    return _write_aseprite(parsed["header"], frames)


def run_aseprite_palette_slice_semantics_lab(profile_paths: list[Path], generated_root: Path) -> dict:
    palette_slice_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        exported = export_aseprite_palette_slice_project(grid, profile)
        imported = import_aseprite_palette_slice_project(exported["project_bytes"], source_grid=grid)
        decoded = exported["decoded_project"]
        palette_slice_results.append(
            {
                "profile_id": profile["profile_id"],
                "profile_path": _portable(profile_path),
                "grid_path": _portable(grid_path),
                "format_id": "libresprite_project",
                "project_file_name": f"{profile['profile_id']}_palette_slice.aseprite",
                "project_bytes_hex": exported["project_bytes"].hex(),
                "project_byte_count": len(exported["project_bytes"]),
                "embedded_project_hash": exported["embedded_project_hash"],
                "canonical_project_hash": exported["canonical_project_hash"],
                "metadata": _metadata_summary(exported["metadata"]),
                "native_sidecar": exported["sidecar"],
                "decoded_project": _decoded_project_summary(decoded),
                "palette_semantics": exported["metadata"]["palette_semantics"],
                "slice_semantics": exported["metadata"]["slice_semantics"],
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

    invalid_probe_results = _invalid_probe_results(palette_slice_results[0])
    success_count = sum(
        1
        for result in palette_slice_results
        if result["import_result"]["ok"]
        and result["restored_grid_validation"].get("valid")
        and result["restored_grid_validation"].get("slip_aligned")
        and result["semantic_fidelity"] == 1.0
    )
    invalid_rejected_count = sum(1 for result in invalid_probe_results if not result["ok"])
    visual_hash_preserved = sum(1 for result in palette_slice_results if result["cel_visual_hashes_preserved"])
    return {
        "artifact_id": "aseprite_palette_slice_semantics_stage0",
        "status": "research_aseprite_palette_slice_semantics_no_package_code",
        "date": "2026-05-14",
        "purpose": (
            "Broaden Stage 0 Aseprite/LibreSprite chunk coverage beyond tags/layers "
            "by proving Palette Chunk 0x2019 color semantics and Slice Chunk 0x2022 "
            "organ bounds in a deterministic three-frame, three-layer compressed "
            "RGBA subset, without claiming arbitrary schema coverage or live editor validation."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
            "labs/workshop_editor/aseprite_tags_layers_semantics.py",
            "labs/workshop_editor/aseprite_palette_slice_semantics.py",
        ],
        "external_anchors": [
            {
                "source": "Aseprite file-format specification",
                "url": "https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md",
                "used_for": "ASE Palette Chunk 0x2019, Slice Chunk 0x2022, Layer Chunk 0x2004, Tags Chunk 0x2018, User Data Chunk 0x2020, and compressed Cel Chunk 0x2005 layout.",
            },
            {
                "source": "Aseprite slice documentation",
                "url": "https://www.aseprite.org/docs/slices/",
                "used_for": "Slice bounds and pivot semantics are treated as named regions, not as arbitrary Mechagotchi schema replacement.",
            },
            {
                "source": "LibreSprite GitHub",
                "url": "https://github.com/LibreSprite/LibreSprite",
                "used_for": "LibreSprite remains a compatibility boundary; no GPL editor code is embedded.",
            },
        ],
        "profile_count": len(profile_paths),
        "palette_slice_roundtrip_count": len(palette_slice_results),
        "palette_slice_roundtrip_success_count": success_count,
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "metrics": {
            "palette_slice_roundtrip_success_rate": _ratio(success_count, len(palette_slice_results)),
            "mean_semantic_fidelity": round(
                sum(result["semantic_fidelity"] for result in palette_slice_results)
                / max(1, len(palette_slice_results)),
                6,
            ),
            "cel_visual_hash_preservation_rate": _ratio(
                visual_hash_preserved,
                len(palette_slice_results),
            ),
            "invalid_probe_rejection_rate": _ratio(
                invalid_rejected_count,
                len(invalid_probe_results),
            ),
            "live_external_editor_verified": False,
        },
        "palette_slice_results": palette_slice_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "aseprite_palette_chunk_slip_colors_subset",
            "aseprite_slice_chunk_semantic_bounds_subset",
            "aseprite_palette_slice_sidecar_semantic_restore",
            "aseprite_palette_slice_hash_validation",
            "aseprite_palette_slice_multilayer_compressed_rgba_subset",
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
        "decision": "prototype_aseprite_palette_slice_native_semantics_subset",
        "next_research_step": (
            "Keep live external editor validation, arbitrary Aseprite schemas, "
            "advanced timeline variants, tilemap/tileset coverage, linked cels, "
            "and full project-format coverage blocked until direct editor fixtures "
            "and broader chunk/schema tests exist."
        ),
    }


def write_aseprite_palette_slice_semantics_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "aseprite_palette_slice_semantics_stage0.json", _json_report(report))
    for result in report["palette_slice_results"]:
        (output_dir / result["project_file_name"]).write_bytes(
            bytes.fromhex(result["project_bytes_hex"])
        )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "aseprite_palette_slice_semantics_data.js").write_text(
        "window.MECHAGOTCHI_ASEPRITE_PALETTE_SLICE_SEMANTICS = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _encode_aseprite_palette_slice_project(grid: dict, metadata: dict | None) -> bytes:
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
        "color_count": len(palette),
        "pixel_width": 1,
        "pixel_height": 1,
        "grid_x": 0,
        "grid_y": 0,
        "grid_width": width,
        "grid_height": height,
    }
    return _write_aseprite(header, frames)


def _palette_semantics(grid: dict) -> list[dict]:
    colors = grid.get("palette", {}).get("colors", [])
    background_index = grid.get("palette", {}).get("background_index", 0)
    entries = []
    for index, color in enumerate(colors):
        rgba = list(_hex_to_rgba(color))
        role = "background" if index == background_index else "foreground"
        entries.append(
            {
                "index": index,
                "name": f"slip_palette_{index}_{role}",
                "role": role,
                "hex": color.lower(),
                "rgba": rgba,
            }
        )
    if not entries:
        raise ValueError("grid palette must contain at least one color")
    return entries


def _palette_chunk_data(entries: list[dict]) -> bytes:
    if not entries:
        raise ValueError("palette chunk requires at least one entry")
    first_index = min(entry["index"] for entry in entries)
    last_index = max(entry["index"] for entry in entries)
    by_index = {entry["index"]: entry for entry in entries}
    payload = bytearray(struct.pack("<III8s", last_index + 1, first_index, last_index, b"\x00" * 8))
    for index in range(first_index, last_index + 1):
        entry = by_index[index]
        red, green, blue, alpha = entry["rgba"]
        payload.extend(struct.pack("<HBBBB", 1, red, green, blue, alpha))
        payload.extend(_pack_string(entry["name"]))
    return bytes(payload)


def _palette_chunk_data_from_palette(palette: dict) -> bytes:
    payload = bytearray(
        struct.pack(
            "<III8s",
            palette["palette_size"],
            palette["first_index"],
            palette["last_index"],
            b"\x00" * 8,
        )
    )
    for entry in palette["entries"]:
        red, green, blue, alpha = entry["rgba"]
        flags = 1 if entry.get("name") else 0
        payload.extend(struct.pack("<HBBBB", flags, red, green, blue, alpha))
        if flags & 1:
            payload.extend(_pack_string(entry["name"]))
    return bytes(payload)


def _parse_palette_chunk(data: bytes) -> dict:
    minimum = struct.calcsize("<III8s")
    if len(data) < minimum:
        raise AsepriteUserDataError("aseprite_palette_chunk_truncated", "Aseprite Palette chunk is truncated")
    palette_size, first_index, last_index, _reserved = struct.unpack("<III8s", data[:minimum])
    if palette_size < 1 or first_index > last_index or last_index >= palette_size:
        raise AsepriteUserDataError("aseprite_palette_range_invalid", "Aseprite Palette chunk range is invalid")
    offset = minimum
    entries = []
    fixed_size = struct.calcsize("<HBBBB")
    for index in range(first_index, last_index + 1):
        if offset + fixed_size > len(data):
            raise AsepriteUserDataError("aseprite_palette_entry_truncated", "Aseprite Palette entry is truncated")
        flags, red, green, blue, alpha = struct.unpack("<HBBBB", data[offset : offset + fixed_size])
        offset += fixed_size
        if flags & ~0x01:
            raise AsepriteUserDataError("aseprite_palette_entry_flags_unsupported", "Stage 0 palette parser supports the name flag only")
        name = None
        if flags & 1:
            name, offset = _unpack_string(data, offset)
        entries.append(
            {
                "index": index,
                "flags": flags,
                "name": name,
                "hex": _rgba_to_hex([red, green, blue, alpha]),
                "rgba": [red, green, blue, alpha],
            }
        )
    if offset != len(data):
        raise AsepriteUserDataError("aseprite_palette_chunk_extra_bytes", "unexpected bytes after Aseprite Palette chunk")
    return {
        "chunk_type": "0x2019",
        "palette_size": palette_size,
        "first_index": first_index,
        "last_index": last_index,
        "entries": entries,
        "colors_hex": [entry["hex"] for entry in entries],
    }


def _slice_semantics(grid: dict) -> list[dict]:
    role_by_organ = {
        "core": "body_core",
        "sensors": "sensor",
        "expression": "expression",
    }
    slices = []
    for organ in ["core", "sensors", "expression"]:
        cells = [cell for cell in grid.get("cells", []) if cell.get("organ") == organ]
        if not cells:
            raise ValueError(f"grid must contain cells for organ: {organ}")
        xs = [cell["x"] for cell in cells]
        ys = [cell["y"] for cell in cells]
        width = max(xs) - min(xs) + 1
        height = max(ys) - min(ys) + 1
        bounds = {
            "x": min(xs),
            "y": min(ys),
            "width": width,
            "height": height,
        }
        slices.append(
            {
                "name": f"organ_{organ}_bounds",
                "semantic_organ": organ,
                "semantic_role": role_by_organ[organ],
                "frame_number": 0,
                "bounds": bounds,
                "pivot": {
                    "x": width // 2,
                    "y": height // 2,
                },
            }
        )
    return slices


def _slice_chunk_data(semantic_slice: dict) -> bytes:
    bounds = semantic_slice["bounds"]
    pivot = semantic_slice["pivot"]
    payload = bytearray(
        struct.pack("<III", 1, 2, 0)
        + _pack_string(semantic_slice["name"])
    )
    payload.extend(
        struct.pack(
            "<IllIIll",
            semantic_slice["frame_number"],
            bounds["x"],
            bounds["y"],
            bounds["width"],
            bounds["height"],
            pivot["x"],
            pivot["y"],
        )
    )
    return bytes(payload)


def _slice_chunk_data_from_slice(parsed_slice: dict) -> bytes:
    payload = bytearray(
        struct.pack("<III", len(parsed_slice["keys"]), parsed_slice["flags"], 0)
        + _pack_string(parsed_slice["name"])
    )
    for key in parsed_slice["keys"]:
        bounds = key["bounds"]
        payload.extend(
            struct.pack(
                "<IllII",
                key["frame_number"],
                bounds["x"],
                bounds["y"],
                bounds["width"],
                bounds["height"],
            )
        )
        if parsed_slice["flags"] & 1:
            center = key.get("center", {"x": 0, "y": 0, "width": 0, "height": 0})
            payload.extend(
                struct.pack(
                    "<llII",
                    center["x"],
                    center["y"],
                    center["width"],
                    center["height"],
                )
            )
        if parsed_slice["flags"] & 2:
            pivot = key.get("pivot", {"x": 0, "y": 0})
            payload.extend(struct.pack("<ll", pivot["x"], pivot["y"]))
    return bytes(payload)


def _parse_slice_chunk(data: bytes) -> dict:
    minimum = struct.calcsize("<III")
    if len(data) < minimum:
        raise AsepriteUserDataError("aseprite_slice_chunk_truncated", "Aseprite Slice chunk is truncated")
    key_count, flags, _reserved = struct.unpack("<III", data[:minimum])
    if flags & ~0x03:
        raise AsepriteUserDataError("aseprite_slice_flags_unsupported", "Stage 0 slice parser supports 9-patch and pivot flags only")
    name, offset = _unpack_string(data, minimum)
    keys = []
    fixed_size = struct.calcsize("<IllII")
    for _index in range(key_count):
        if offset + fixed_size > len(data):
            raise AsepriteUserDataError("aseprite_slice_key_truncated", "Aseprite Slice key is truncated")
        frame_number, x, y, width, height = struct.unpack("<IllII", data[offset : offset + fixed_size])
        offset += fixed_size
        key = {
            "frame_number": frame_number,
            "bounds": {
                "x": x,
                "y": y,
                "width": width,
                "height": height,
            },
        }
        if flags & 1:
            if offset + struct.calcsize("<llII") > len(data):
                raise AsepriteUserDataError("aseprite_slice_center_truncated", "Aseprite Slice 9-patch center is truncated")
            center_x, center_y, center_width, center_height = struct.unpack(
                "<llII",
                data[offset : offset + struct.calcsize("<llII")],
            )
            offset += struct.calcsize("<llII")
            key["center"] = {
                "x": center_x,
                "y": center_y,
                "width": center_width,
                "height": center_height,
            }
        if flags & 2:
            if offset + struct.calcsize("<ll") > len(data):
                raise AsepriteUserDataError("aseprite_slice_pivot_truncated", "Aseprite Slice pivot is truncated")
            pivot_x, pivot_y = struct.unpack("<ll", data[offset : offset + struct.calcsize("<ll")])
            offset += struct.calcsize("<ll")
            key["pivot"] = {
                "x": pivot_x,
                "y": pivot_y,
            }
        keys.append(key)
    if offset != len(data):
        raise AsepriteUserDataError("aseprite_slice_chunk_extra_bytes", "unexpected bytes after Aseprite Slice chunk")
    return {
        "chunk_type": "0x2022",
        "name": name,
        "flags": flags,
        "key_count": key_count,
        "keys": keys,
    }


def _build_palette_slice_metadata(
    canonical_hash: str,
    cel_visual_hashes: dict,
    grid: dict,
    sidecar: dict,
) -> dict:
    slice_semantics = _slice_semantics(grid)
    return {
        "metadata_version": ASE_PALETTE_SLICE_VERSION,
        "supersedes_metadata_version": ASE_TAGS_LAYERS_VERSION,
        "format_id": "libresprite_project",
        "native_location": ASE_PALETTE_SLICE_NATIVE_LOCATION,
        "writer_policy": ASE_PALETTE_SLICE_POLICY,
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
    }


def _extract_palette_slice_metadata(project_bytes: bytes) -> dict:
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
                    raise AsepriteUserDataError("aseprite_palette_slice_json_invalid", str(exc)) from exc
                if metadata.get("metadata_version") == ASE_PALETTE_SLICE_VERSION:
                    return metadata
    raise AsepriteUserDataError(
        "aseprite_palette_slice_metadata_missing",
        "ASE project does not contain Mechagotchi palette/slice User Data metadata",
    )


def _validate_palette(decoded: dict, metadata: dict) -> None:
    if decoded["palette_chunk_count"] < 1:
        raise AsepriteUserDataError(
            "aseprite_palette_missing",
            "Aseprite palette/slice project must contain a Palette Chunk 0x2019",
        )
    current = [
        {
            "index": entry["index"],
            "name": entry.get("name"),
            "hex": entry["hex"],
            "rgba": entry["rgba"],
        }
        for entry in decoded["palette"]["entries"]
    ]
    expected = [
        {
            "index": entry["index"],
            "name": entry["name"],
            "hex": entry["hex"],
            "rgba": entry["rgba"],
        }
        for entry in metadata.get("palette_semantics", [])
    ]
    if current != expected:
        raise AsepriteUserDataError(
            "aseprite_palette_semantics_mismatch",
            "Aseprite Palette chunk colors or names do not match embedded palette semantics",
        )


def _validate_slices(decoded: dict, metadata: dict) -> None:
    if decoded["slice_count"] < 1:
        raise AsepriteUserDataError(
            "aseprite_slices_missing",
            "Aseprite palette/slice project must contain Slice Chunk 0x2022 semantics",
        )
    width, height = decoded["dimensions"]
    for parsed_slice in decoded["slices"]:
        if parsed_slice["key_count"] < 1:
            raise AsepriteUserDataError(
                "aseprite_slice_key_missing",
                "Aseprite semantic Slice chunk must contain at least one key",
            )
        for key in parsed_slice["keys"]:
            bounds = key["bounds"]
            if (
                key["frame_number"] >= decoded["frame_count"]
                or bounds["width"] < 1
                or bounds["height"] < 1
                or bounds["x"] < 0
                or bounds["y"] < 0
                or bounds["x"] + bounds["width"] > width
                or bounds["y"] + bounds["height"] > height
            ):
                raise AsepriteUserDataError(
                    "aseprite_slice_bounds_invalid",
                    "Aseprite semantic Slice bounds must be positive and inside the sprite dimensions",
                )

    current = [
        {
            "name": parsed_slice["name"],
            "frame_number": parsed_slice["keys"][0]["frame_number"],
            "bounds": parsed_slice["keys"][0]["bounds"],
            "pivot": parsed_slice["keys"][0].get("pivot"),
        }
        for parsed_slice in decoded["slices"]
    ]
    expected = [
        {
            "name": entry["name"],
            "frame_number": entry["frame_number"],
            "bounds": entry["bounds"],
            "pivot": entry["pivot"],
        }
        for entry in metadata.get("slice_semantics", [])
    ]
    if current != expected:
        raise AsepriteUserDataError(
            "aseprite_slice_semantics_mismatch",
            "Aseprite Slice chunk bounds do not match embedded slice semantics",
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


def _invalid_probe_results(reference_result: dict) -> list[dict]:
    project_bytes = bytes.fromhex(reference_result["project_bytes_hex"])
    return [
        _compact_import_result(import_aseprite_palette_slice_project(strip_aseprite_palette_chunk(project_bytes))),
        _compact_import_result(import_aseprite_palette_slice_project(tamper_aseprite_palette_entry(project_bytes))),
        _compact_import_result(import_aseprite_palette_slice_project(strip_aseprite_slice_chunks(project_bytes))),
        _compact_import_result(import_aseprite_palette_slice_project(tamper_aseprite_slice_bounds(project_bytes))),
        _compact_import_result(import_aseprite_palette_slice_project(tamper_aseprite_palette_slice_metadata(project_bytes))),
        _compact_import_result(import_aseprite_palette_slice_project(tamper_aseprite_palette_slice_metadata_json(project_bytes))),
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
        "palette_chunk_count",
        "palette_entry_count",
        "slice_count",
        "slice_key_count",
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
    for result in payload["palette_slice_results"]:
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
                "palette_slice_roundtrip_count",
                "palette_slice_roundtrip_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "palette_slice_summaries": [
            {
                "profile_id": result["profile_id"],
                "format_id": result["format_id"],
                "project_byte_count": result["project_byte_count"],
                "embedded_project_hash": result["embedded_project_hash"],
                "canonical_project_hash": result["canonical_project_hash"],
                "decoded_project": result["decoded_project"],
                "semantic_fidelity": result["semantic_fidelity"],
            }
            for result in json_report["palette_slice_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# Aseprite Palette/Slice Semantics Stage 0\n\n"
        "Aseprite/LibreSprite palette and slice semantic proof for Palette "
        "Chunk 0x2019 colors, Slice Chunk 0x2022 organ bounds, three-frame "
        "tags/layers, and compressed RGBA cel payloads.\n\n"
        f"- Palette/slice round trips: {report['palette_slice_roundtrip_success_count']}/"
        f"{report['palette_slice_roundtrip_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}/"
        f"{report['invalid_probe_count']}\n"
        f"- Mean semantic fidelity: {metrics['mean_semantic_fidelity']}\n"
        f"- Cel visual hash preservation rate: {metrics['cel_visual_hash_preservation_rate']}\n"
        f"- Live external editor verified: {metrics['live_external_editor_verified']}\n\n"
        "This artifact does not claim live external editor validation, "
        "arbitrary Aseprite schemas, tilemaps/tilesets, linked cels, advanced "
        "timelines, package runtime integration, or full project-format coverage.\n"
    )


def _hex_to_rgba(value: str) -> tuple[int, int, int, int]:
    if not isinstance(value, str) or len(value) != 7 or not value.startswith("#"):
        raise ValueError(f"expected #RRGGBB color, got {value!r}")
    return (
        int(value[1:3], 16),
        int(value[3:5], 16),
        int(value[5:7], 16),
        255,
    )


def _rgba_to_hex(rgba: list[int]) -> str:
    return f"#{rgba[0]:02x}{rgba[1]:02x}{rgba[2]:02x}"


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
        default=ROOT / "data/workshop_editor/aseprite_palette_slice_semantics_stage0",
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
    report = run_aseprite_palette_slice_semantics_lab(profile_paths, args.generated_root)
    write_aseprite_palette_slice_semantics_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_ASEPRITE_PALETTE_SLICE_SEMANTICS = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(_json_report(report), indent=2))


if __name__ == "__main__":
    main()
