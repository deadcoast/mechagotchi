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
    _parse_tags_chunk,
    _tag_semantics,
    _tags_chunk_data,
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
    _parse_user_data_chunk,
    _ratio,
    _unpack_string,
    _user_data_chunk_data,
    _write_aseprite,
)
from external_metadata_sidecar import build_sidecar_for_grid, restore_grid_from_sidecar
from png_chunk_reader import PNGChunkError, bounded_decompress
from workshop_editor import compare_semantic_grid_fidelity


ASE_CHUNK_TILESET = 0x2023
ASE_TILEMAP_TILESET_VERSION = "mechagotchi.aseprite_tilemap_tileset.v1"
ASE_TILEMAP_TILESET_POLICY = "aseprite_tilemap_tileset_native_semantics"
ASE_TILEMAP_TILESET_NATIVE_LOCATION = (
    "frame[0].tileset + frame[0].tilemap_layer.user_data.text + "
    "frame[*].tilemap_cels"
)
ASE_TILE_ID_MASK = 0x1FFFFFFF
ASE_TILE_X_FLIP_MASK = 0x20000000
ASE_TILE_Y_FLIP_MASK = 0x40000000
ASE_TILE_DIAGONAL_FLIP_MASK = 0x80000000
REPORT_PATH = Path("data/workshop_editor/aseprite_tilemap_tileset_semantics_stage0.json")
DATA_PATH = Path("data/workshop_editor/aseprite_tilemap_tileset_semantics_data.js")


def export_aseprite_tilemap_tileset_project(grid: dict, slip_profile: dict) -> dict:
    canonical_project = _encode_aseprite_tilemap_tileset_project(grid, metadata=None)
    canonical_hash = _hash_bytes(canonical_project)
    canonical_decoded = decode_aseprite_tilemap_tileset_project(canonical_project)
    asset = {
        "asset_id": f"{grid['grid_id']}_tilemap_tileset.aseprite",
        "format_id": "libresprite_project",
        "media_type": "application/octet-stream",
        "uri": f"generated://workshop/project-tilemap-tileset/{grid['grid_id']}.aseprite",
        "width": grid["grid_size"][0],
        "height": grid["grid_size"][1],
        "frame_count": 3,
        "content_hash": canonical_hash,
        "semantic_policy": ASE_TILEMAP_TILESET_POLICY,
    }
    sidecar = build_sidecar_for_grid(grid, slip_profile, asset)
    sidecar["sidecar_id"] = f"{grid['grid_id']}_aseprite_tilemap_tileset_sidecar"
    sidecar["asset_binding"]["semantic_policy"] = ASE_TILEMAP_TILESET_POLICY
    sidecar["project_binding"] = {
        "format_id": "libresprite_project",
        "decoder_scope": "aseprite_tilemap_tileset_palette_slice_tags_user_data_subset",
        "native_mechagotchi_semantics": True,
        "semantic_policy": ASE_TILEMAP_TILESET_POLICY,
        "native_metadata_version": ASE_TILEMAP_TILESET_VERSION,
    }
    sidecar["limitations"] = [
        "Stage 0 Aseprite/LibreSprite tilemap proof covers one Tilemap Layer type 2, one embedded Tileset Chunk 0x2023, and compressed Tilemap Cel Chunk 0x2005 type 3 payloads.",
        "Tile IDs encode empty/core/sensors/expression organ occupancy only; visual and full semantic restore still comes from the embedded sidecar.",
        "Live external editor rewrite validation is not verified by this lab.",
        "Arbitrary Aseprite project schemas, nested groups, advanced timeline variants, and full project-format coverage remain separate.",
    ]
    metadata = _build_tilemap_tileset_metadata(
        canonical_hash,
        grid,
        sidecar,
        canonical_decoded,
    )
    project_bytes = _encode_aseprite_tilemap_tileset_project(grid, metadata=metadata)
    decoded = decode_aseprite_tilemap_tileset_project(project_bytes)
    return {
        "project_bytes": project_bytes,
        "canonical_project_bytes": canonical_project,
        "embedded_project_hash": _hash_bytes(project_bytes),
        "canonical_project_hash": canonical_hash,
        "metadata": metadata,
        "sidecar": sidecar,
        "decoded_project": decoded,
    }


def decode_aseprite_tilemap_tileset_project(project_bytes: bytes) -> dict:
    parsed = _parse_aseprite(project_bytes)
    layers = []
    tags = []
    cels = []
    user_data_chunks = []
    tilemap_layer_user_data = []
    palette = None
    palette_chunk_count = 0
    slices = []
    tilesets = []
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
            elif chunk_type == ASE_CHUNK_TILESET:
                tileset = _parse_tileset_chunk(chunk["data"])
                tileset["index"] = len(tilesets)
                tileset["frame_index"] = frame_index
                tilesets.append(tileset)
                last_target = {
                    "target_type": "tileset",
                    "target_index": tileset["index"],
                    "target_name": tileset["name"],
                }
            elif chunk_type == ASE_CHUNK_LAYER:
                layer = _parse_tilemap_layer_chunk(chunk["data"])
                layer["index"] = len(layers)
                layer["frame_index"] = frame_index
                layers.append(layer)
                last_target = {
                    "target_type": "tilemap_layer" if layer["layer_type"] == 2 else "layer",
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
                cel = _parse_tilemap_or_compressed_cel_chunk(
                    chunk["data"],
                    parsed["header"]["width"],
                    parsed["header"]["height"],
                )
                cel["index"] = len(cels)
                cel["frame_index"] = frame_index
                cels.append(cel)
                suffix = "tilemap" if cel["cel_type"] == 3 else "compressed"
                last_target = {
                    "target_type": "cel",
                    "target_index": cel["index"],
                    "target_name": f"frame_{frame_index}_layer_{cel['layer_index']}_{suffix}",
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
                        raise AsepriteUserDataError("aseprite_tilemap_tileset_json_invalid", str(exc)) from exc
                    if metadata.get("metadata_version") == ASE_TILEMAP_TILESET_VERSION:
                        native = True
                    tilemap_binding = metadata.get("tilemap_layer_binding", {})
                    if target["target_type"] == "tilemap_layer":
                        entry["semantic_role"] = tilemap_binding.get("semantic_role")
                        entry["tileset_index"] = tilemap_binding.get("tileset_index")
                        tilemap_layer_user_data.append(entry)
                user_data_chunks.append(entry)

    tilemap_cels = [cel for cel in cels if cel["cel_type"] == 3]
    compressed_cels = [cel for cel in cels if cel["cel_type"] == 2]
    return {
        "format_id": "libresprite_project",
        "magic": hex(parsed["header"]["magic"]),
        "frame_magic": hex(parsed["frames"][0]["magic"]) if parsed["frames"] else None,
        "dimensions": [parsed["header"]["width"], parsed["header"]["height"]],
        "frame_count": parsed["header"]["frames"],
        "layer_count": len(layers),
        "tilemap_layer_count": sum(1 for layer in layers if layer["layer_type"] == 2),
        "tag_count": len(tags),
        "cel_count": len(cels),
        "compressed_cel_count": len(compressed_cels),
        "tilemap_cel_count": len(tilemap_cels),
        "chunk_count": total_chunk_count,
        "user_data_chunk_count": len(user_data_chunks),
        "palette_chunk_count": palette_chunk_count,
        "palette_entry_count": len(palette["entries"]) if palette else 0,
        "slice_count": len(slices),
        "slice_key_count": sum(len(entry["keys"]) for entry in slices),
        "tileset_chunk_count": len(tilesets),
        "tileset_tile_count": sum(tileset["tile_count"] for tileset in tilesets),
        "color_depth_bpp": parsed["header"]["color_depth"],
        "first_frame_duration_ms": parsed["frames"][0]["duration_ms"] if parsed["frames"] else parsed["header"]["speed_ms"],
        "layers": layers,
        "tags": tags,
        "palette": palette or {},
        "slices": slices,
        "tilesets": [_tileset_summary(tileset) for tileset in tilesets],
        "cels": [_cel_summary(cel) for cel in cels],
        "tilemap_semantics": _decoded_tilemap_semantics(tilemap_cels),
        "tilemap_hashes": _tilemap_hash_map(tilemap_cels),
        "user_data_chunks": user_data_chunks,
        "tilemap_layer_user_data": tilemap_layer_user_data,
        "native_mechagotchi_semantics": native,
    }


def extract_aseprite_tilemap_tileset_sidecar(project_bytes: bytes) -> dict:
    decoded = decode_aseprite_tilemap_tileset_project(project_bytes)
    metadata = _extract_tilemap_tileset_metadata(project_bytes)
    if metadata.get("metadata_version") != ASE_TILEMAP_TILESET_VERSION:
        raise AsepriteUserDataError(
            "aseprite_tilemap_tileset_version_unsupported",
            "unsupported Aseprite tilemap/tileset metadata version",
        )
    if metadata.get("format_id") != "libresprite_project":
        raise AsepriteUserDataError(
            "aseprite_tilemap_tileset_format_mismatch",
            "Aseprite tilemap/tileset metadata format id mismatch",
        )
    _validate_palette(decoded, metadata)
    _validate_slices(decoded, metadata)
    _validate_tags(decoded["tags"], decoded["frame_count"], metadata)
    _validate_tilemap_layer(decoded, metadata)
    _validate_tilesets(decoded, metadata)
    _validate_tilemap_cels(decoded, metadata)

    sidecar = metadata.get("sidecar")
    if not isinstance(sidecar, dict):
        raise AsepriteUserDataError(
            "aseprite_tilemap_tileset_sidecar_missing",
            "Aseprite tilemap/tileset metadata must contain a sidecar object",
        )
    if _hash_payload(sidecar) != metadata.get("sidecar_hash"):
        raise AsepriteUserDataError(
            "aseprite_tilemap_tileset_sidecar_hash_mismatch",
            "Aseprite tilemap/tileset sidecar hash does not match the embedded sidecar",
        )
    canonical = strip_aseprite_tilemap_tileset_user_data_chunks(project_bytes)
    canonical_hash = _hash_bytes(canonical)
    if canonical_hash != metadata.get("canonical_project_hash"):
        raise AsepriteUserDataError(
            "aseprite_tilemap_tileset_canonical_hash_mismatch",
            "Aseprite tilemap/tileset canonical project hash does not match the stripped project",
        )
    if sidecar.get("asset_binding", {}).get("content_hash") != canonical_hash:
        raise AsepriteUserDataError(
            "aseprite_tilemap_tileset_sidecar_asset_hash_mismatch",
            "Aseprite tilemap/tileset sidecar asset hash does not match the canonical project hash",
        )
    return {
        "ok": True,
        "metadata": metadata,
        "sidecar": sidecar,
        "decoded_project": _decoded_project_summary(decoded),
        "canonical_project_hash": canonical_hash,
        "embedded_project_hash": _hash_bytes(project_bytes),
    }


def import_aseprite_tilemap_tileset_project(project_bytes: bytes, source_grid: dict | None = None) -> dict:
    try:
        extracted = extract_aseprite_tilemap_tileset_sidecar(project_bytes)
    except AsepriteUserDataError as exc:
        return _failed_import("aseprite_tilemap_tileset", exc.family, exc.message)

    sidecar = extracted["sidecar"]
    asset = deepcopy(sidecar["asset_binding"])
    try:
        restored = restore_grid_from_sidecar(sidecar, asset)
    except ValueError as exc:
        return _failed_import("sidecar", "aseprite_tilemap_tileset_sidecar_invalid", str(exc))

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
            "semantic_policy": ASE_TILEMAP_TILESET_POLICY,
            "native_mechagotchi_semantics": True,
            "native_location": ASE_TILEMAP_TILESET_NATIVE_LOCATION,
            "tileset_chunk_type": "0x2023",
            "tilemap_layer_type": 2,
            "tilemap_cel_chunk_type": "0x2005",
            "tilemap_cel_type": 3,
            "palette_chunk_type": "0x2019",
            "slice_chunk_type": "0x2022",
            "tilemap_layer_user_data_chunk_type": "0x2020",
            "tags_chunk_type": "0x2018",
            "live_external_editor_verified": False,
        },
        "semantic_diff": diff,
        "semantic_fidelity": fidelity,
        "errors": errors,
        "error_families": sorted({error["family"] for error in errors}),
    }


def strip_aseprite_tilemap_tileset_user_data_chunks(project_bytes: bytes) -> bytes:
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


def strip_aseprite_tileset_chunks(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    frames = []
    for frame in parsed["frames"]:
        frames.append(
            {
                "duration_ms": frame["duration_ms"],
                "chunks": [
                    chunk
                    for chunk in frame["chunks"]
                    if chunk["type"] != ASE_CHUNK_TILESET
                ],
            }
        )
    return _write_aseprite(parsed["header"], frames)


def strip_aseprite_tilemap_cel_chunks(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    frames = []
    for frame in parsed["frames"]:
        chunks = []
        for chunk in frame["chunks"]:
            if chunk["type"] == ASE_CHUNK_CEL and _peek_cel_header(chunk["data"])["cel_type"] == 3:
                continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    return _write_aseprite(parsed["header"], frames)


def tamper_aseprite_tileset_image(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    replaced = False
    frames = []
    for frame in parsed["frames"]:
        chunks = []
        for chunk in frame["chunks"]:
            if chunk["type"] == ASE_CHUNK_TILESET and not replaced:
                tileset = _parse_tileset_chunk(chunk["data"])
                raw = bytearray(tileset["image_raw_rgba"])
                raw[0] = (raw[0] + 1) % 256
                tileset["image_raw_rgba"] = bytes(raw)
                chunks.append(_chunk(ASE_CHUNK_TILESET, _tileset_chunk_data_from_parsed(tileset)))
                replaced = True
                continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    if not replaced:
        raise AsepriteUserDataError("aseprite_tileset_missing", "no Tileset Chunk found")
    return _write_aseprite(parsed["header"], frames)


def tamper_aseprite_tilemap_tile_id(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    replaced = False
    frames = []
    for frame in parsed["frames"]:
        chunks = []
        for chunk in frame["chunks"]:
            if chunk["type"] == ASE_CHUNK_CEL and not replaced:
                header = _peek_cel_header(chunk["data"])
                if header["cel_type"] == 3:
                    cel = _parse_tilemap_or_compressed_cel_chunk(
                        chunk["data"],
                        parsed["header"]["width"],
                        parsed["header"]["height"],
                    )
                    tile_matrix = deepcopy(cel["tile_matrix"])
                    for y, row in enumerate(tile_matrix):
                        for x, tile_id in enumerate(row):
                            if tile_id != 0:
                                tile_matrix[y][x] = 0
                                chunks.append(
                                    _chunk(
                                        ASE_CHUNK_CEL,
                                        _tilemap_cel_chunk_data(
                                            cel["layer_index"],
                                            cel["width"],
                                            cel["height"],
                                            tile_matrix,
                                        ),
                                    )
                                )
                                replaced = True
                                break
                        if replaced:
                            break
                    if replaced:
                        continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    if not replaced:
        raise AsepriteUserDataError("aseprite_tilemap_cels_missing", "no tilemap cel chunk found")
    return _write_aseprite(parsed["header"], frames)


def tamper_aseprite_tilemap_metadata(project_bytes: bytes) -> bytes:
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
                    if metadata.get("metadata_version") == ASE_TILEMAP_TILESET_VERSION:
                        metadata["sidecar"]["asset_binding"]["width"] += 1
                        chunks.append(_chunk(ASE_CHUNK_USER_DATA, _user_data_chunk_data(metadata)))
                        replaced = True
                        continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    if not replaced:
        raise AsepriteUserDataError(
            "aseprite_tilemap_tileset_metadata_missing",
            "no Mechagotchi tilemap/tileset User Data chunk found",
        )
    return _write_aseprite(parsed["header"], frames)


def tamper_aseprite_tilemap_metadata_json(project_bytes: bytes) -> bytes:
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
        raise AsepriteUserDataError("aseprite_tilemap_tileset_metadata_missing", "no Mechagotchi tilemap User Data chunk found")
    return _write_aseprite(parsed["header"], frames)


def run_aseprite_tilemap_tileset_semantics_lab(profile_paths: list[Path], generated_root: Path) -> dict:
    tilemap_tileset_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        exported = export_aseprite_tilemap_tileset_project(grid, profile)
        imported = import_aseprite_tilemap_tileset_project(exported["project_bytes"], source_grid=grid)
        decoded = exported["decoded_project"]
        tilemap_tileset_results.append(
            {
                "profile_id": profile["profile_id"],
                "profile_path": _portable(profile_path),
                "grid_path": _portable(grid_path),
                "format_id": "libresprite_project",
                "project_file_name": f"{profile['profile_id']}_tilemap_tileset.aseprite",
                "project_bytes_hex": exported["project_bytes"].hex(),
                "project_byte_count": len(exported["project_bytes"]),
                "embedded_project_hash": exported["embedded_project_hash"],
                "canonical_project_hash": exported["canonical_project_hash"],
                "metadata": _metadata_summary(exported["metadata"]),
                "native_sidecar": exported["sidecar"],
                "decoded_project": _decoded_project_summary(decoded),
                "tileset_semantics": exported["metadata"]["tileset_semantics"],
                "tilemap_semantics": exported["metadata"]["tilemap_semantics"],
                "import_result": _compact_import_result(imported),
                "restored_grid_validation": imported.get("restored_grid_validation", {}),
                "semantic_diff": imported.get("semantic_diff", {}),
                "semantic_fidelity": imported.get("semantic_fidelity", 0.0),
                "tilemap_hashes_preserved": (
                    exported["metadata"]["tilemap_hashes"]
                    == decoded["tilemap_hashes"]
                ),
                "tileset_image_hash_preserved": (
                    exported["metadata"]["tileset_image_hash"]
                    == decoded["tilesets"][0]["image_hash"]
                ),
            }
        )

    invalid_probe_results = _invalid_probe_results(tilemap_tileset_results[0])
    success_count = sum(
        1
        for result in tilemap_tileset_results
        if result["import_result"]["ok"]
        and result["restored_grid_validation"].get("valid")
        and result["restored_grid_validation"].get("slip_aligned")
        and result["semantic_fidelity"] == 1.0
    )
    invalid_rejected_count = sum(1 for result in invalid_probe_results if not result["ok"])
    tilemap_hash_preserved = sum(1 for result in tilemap_tileset_results if result["tilemap_hashes_preserved"])
    tileset_hash_preserved = sum(1 for result in tilemap_tileset_results if result["tileset_image_hash_preserved"])
    return {
        "artifact_id": "aseprite_tilemap_tileset_semantics_stage0",
        "status": "research_aseprite_tilemap_tileset_semantics_no_package_code",
        "date": "2026-05-14",
        "purpose": (
            "Broaden Stage 0 Aseprite/LibreSprite chunk coverage beyond the "
            "linked-cel subset by proving Tilemap Layer type 2, Tileset Chunk "
            "0x2023, and compressed Tilemap Cel Chunk 0x2005 type 3 parsing in "
            "a deterministic semantic-organ tile ID carrier, without claiming "
            "arbitrary schema or live external editor coverage."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
            "labs/workshop_editor/aseprite_linked_cel_semantics.py",
            "labs/workshop_editor/aseprite_tilemap_tileset_semantics.py",
        ],
        "external_anchors": [
            {
                "source": "Aseprite file-format specification",
                "url": "https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md",
                "used_for": "ASE Layer Chunk 0x2004 tilemap layer type 2, Cel Chunk 0x2005 compressed tilemap cel type 3 layout, Tileset Chunk 0x2023 layout, and tile bitmask semantics.",
            },
            {
                "source": "Aseprite tilemap documentation",
                "url": "https://www.aseprite.org/docs/tilemap/",
                "used_for": "Tilemap remains a tile editing workflow boundary; semantic restore is still governed by Mechagotchi metadata.",
            },
            {
                "source": "LibreSprite GitHub",
                "url": "https://github.com/LibreSprite/LibreSprite",
                "used_for": "LibreSprite remains a compatibility boundary; no GPL editor code is embedded.",
            },
        ],
        "profile_count": len(profile_paths),
        "tilemap_tileset_roundtrip_count": len(tilemap_tileset_results),
        "tilemap_tileset_roundtrip_success_count": success_count,
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "metrics": {
            "tilemap_tileset_roundtrip_success_rate": _ratio(success_count, len(tilemap_tileset_results)),
            "mean_semantic_fidelity": round(
                sum(result["semantic_fidelity"] for result in tilemap_tileset_results)
                / max(1, len(tilemap_tileset_results)),
                6,
            ),
            "tilemap_hash_preservation_rate": _ratio(
                tilemap_hash_preserved,
                len(tilemap_tileset_results),
            ),
            "tileset_image_hash_preservation_rate": _ratio(
                tileset_hash_preserved,
                len(tilemap_tileset_results),
            ),
            "invalid_probe_rejection_rate": _ratio(
                invalid_rejected_count,
                len(invalid_probe_results),
            ),
            "live_external_editor_verified": False,
        },
        "tilemap_tileset_results": tilemap_tileset_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "aseprite_tilemap_layer_type_subset",
            "aseprite_tileset_chunk_subset",
            "aseprite_tilemap_cel_chunk_subset",
            "aseprite_tilemap_tile_id_semantic_restore",
            "aseprite_tilemap_tileset_hash_validation",
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
        "decision": "prototype_aseprite_tilemap_tileset_native_semantics_subset",
        "next_research_step": (
            "Keep live external editor validation, arbitrary Aseprite schemas, "
            "advanced timeline variants, and full project-format coverage "
            "blocked until direct editor fixtures and broader chunk/schema tests exist."
        ),
    }


def write_aseprite_tilemap_tileset_semantics_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "aseprite_tilemap_tileset_semantics_stage0.json", _json_report(report))
    for result in report["tilemap_tileset_results"]:
        (output_dir / result["project_file_name"]).write_bytes(
            bytes.fromhex(result["project_bytes_hex"])
        )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "aseprite_tilemap_tileset_semantics_data.js").write_text(
        "window.MECHAGOTCHI_ASEPRITE_TILEMAP_TILESET_SEMANTICS = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _encode_aseprite_tilemap_tileset_project(grid: dict, metadata: dict | None) -> bytes:
    width, height = grid["grid_size"]
    palette = _palette_semantics(grid)
    slices = _slice_semantics(grid)
    tags = _tag_semantics()
    tileset = _tileset_semantics(grid)
    tilemap = _tilemap_semantics(grid)
    frames = []
    for frame_index in range(3):
        chunks = []
        if frame_index == 0:
            chunks.append(_chunk(ASE_CHUNK_PALETTE, _palette_chunk_data(palette)))
            chunks.append(_chunk(ASE_CHUNK_TILESET, _tileset_chunk_data(tileset)))
            chunks.append(
                _chunk(
                    ASE_CHUNK_LAYER,
                    _tilemap_layer_chunk_data(width, height, "Mechagotchi semantic tilemap", 0),
                )
            )
            if metadata is not None:
                layer_metadata = deepcopy(metadata)
                layer_metadata["tilemap_layer_binding"] = _tilemap_layer_semantics()
                chunks.append(_chunk(ASE_CHUNK_USER_DATA, _user_data_chunk_data(layer_metadata)))
            chunks.append(_chunk(ASE_CHUNK_TAGS, _tags_chunk_data(tags)))
            for semantic_slice in slices:
                chunks.append(_chunk(ASE_CHUNK_SLICE, _slice_chunk_data(semantic_slice)))
        chunks.append(
            _chunk(
                ASE_CHUNK_CEL,
                _tilemap_cel_chunk_data(0, width, height, tilemap["tile_matrix"]),
            )
        )
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
        "grid_width": 1,
        "grid_height": 1,
    }
    return _write_aseprite(header, frames)


def _tilemap_layer_chunk_data(width: int, height: int, name: str, tileset_index: int) -> bytes:
    return (
        struct.pack("<HHHHHHB3s", 3, 2, 0, width, height, 0, 255, b"\x00\x00\x00")
        + _pack_string(name)
        + struct.pack("<I", tileset_index)
    )


def _parse_tilemap_layer_chunk(data: bytes) -> dict:
    minimum = struct.calcsize("<HHHHHHB3s")
    if len(data) < minimum:
        raise AsepriteUserDataError("aseprite_layer_chunk_truncated", "ASE Layer chunk is truncated")
    flags, layer_type, child_level, default_width, default_height, blend_mode, opacity, _reserved = struct.unpack(
        "<HHHHHHB3s",
        data[:minimum],
    )
    name, offset = _unpack_string(data, minimum)
    tileset_index = None
    if layer_type == 2:
        if offset + 4 > len(data):
            raise AsepriteUserDataError(
                "aseprite_tilemap_layer_tileset_index_missing",
                "Aseprite tilemap layer must include a tileset index",
            )
        tileset_index = struct.unpack("<I", data[offset : offset + 4])[0]
        offset += 4
    if offset != len(data):
        raise AsepriteUserDataError("aseprite_layer_chunk_extra_bytes", "unexpected bytes after ASE Layer chunk")
    return {
        "chunk_type": "0x2004",
        "flags": flags,
        "layer_type": layer_type,
        "child_level": child_level,
        "default_size": [default_width, default_height],
        "blend_mode": blend_mode,
        "opacity": opacity,
        "name": name,
        "tileset_index": tileset_index,
    }


def _tileset_chunk_data(tileset: dict) -> bytes:
    raw = _tileset_raw_image(tileset)
    compressed = zlib.compress(raw)
    return (
        struct.pack(
            "<IIIHHh14s",
            tileset["tileset_id"],
            tileset["flags"],
            len(tileset["tiles"]),
            tileset["tile_width"],
            tileset["tile_height"],
            tileset["base_index"],
            b"\x00" * 14,
        )
        + _pack_string(tileset["name"])
        + struct.pack("<I", len(compressed))
        + compressed
    )


def _tileset_chunk_data_from_parsed(tileset: dict) -> bytes:
    compressed = zlib.compress(tileset["image_raw_rgba"])
    return (
        struct.pack(
            "<IIIHHh14s",
            tileset["tileset_id"],
            tileset["flags"],
            tileset["tile_count"],
            tileset["tile_size"][0],
            tileset["tile_size"][1],
            tileset["base_index"],
            b"\x00" * 14,
        )
        + _pack_string(tileset["name"])
        + struct.pack("<I", len(compressed))
        + compressed
    )


def _parse_tileset_chunk(data: bytes) -> dict:
    fixed_size = struct.calcsize("<IIIHHh14s")
    if len(data) < fixed_size:
        raise AsepriteUserDataError("aseprite_tileset_chunk_truncated", "Aseprite Tileset chunk is truncated")
    tileset_id, flags, tile_count, tile_width, tile_height, base_index, _reserved = struct.unpack(
        "<IIIHHh14s",
        data[:fixed_size],
    )
    if tile_count < 1 or tile_width < 1 or tile_height < 1:
        raise AsepriteUserDataError(
            "aseprite_tileset_dimensions_invalid",
            "Aseprite Tileset chunk must contain positive tile dimensions and tile count",
        )
    name, offset = _unpack_string(data, fixed_size)
    external_file_id = None
    external_tileset_id = None
    if flags & 1:
        if offset + 8 > len(data):
            raise AsepriteUserDataError(
                "aseprite_tileset_external_reference_truncated",
                "Aseprite Tileset external reference is truncated",
            )
        external_file_id, external_tileset_id = struct.unpack("<II", data[offset : offset + 8])
        offset += 8
    image_raw = b""
    compressed_size = 0
    if flags & 2:
        if offset + 4 > len(data):
            raise AsepriteUserDataError(
                "aseprite_tileset_image_size_missing",
                "Aseprite Tileset embedded image size is missing",
            )
        compressed_size = struct.unpack("<I", data[offset : offset + 4])[0]
        offset += 4
        if offset + compressed_size > len(data):
            raise AsepriteUserDataError(
                "aseprite_tileset_image_truncated",
                "Aseprite Tileset embedded image payload is truncated",
            )
        compressed = data[offset : offset + compressed_size]
        offset += compressed_size
        expected_size = tile_width * tile_height * tile_count * 4
        try:
            image_raw = bounded_decompress(compressed, expected_size)
        except PNGChunkError as exc:
            raise AsepriteUserDataError("aseprite_tileset_image_decompression_failed", exc.message) from exc
        if len(image_raw) != expected_size:
            raise AsepriteUserDataError(
                "aseprite_tileset_image_size_mismatch",
                "decoded Aseprite Tileset image size does not match tile dimensions",
            )
    if offset != len(data):
        raise AsepriteUserDataError("aseprite_tileset_chunk_extra_bytes", "unexpected bytes after Aseprite Tileset chunk")
    return {
        "chunk_type": "0x2023",
        "tileset_id": tileset_id,
        "flags": flags,
        "tile_count": tile_count,
        "tile_size": [tile_width, tile_height],
        "base_index": base_index,
        "name": name,
        "external_file_id": external_file_id,
        "external_tileset_id": external_tileset_id,
        "compressed_image_byte_count": compressed_size,
        "image_raw_rgba": image_raw,
        "image_hash": _hash_bytes(image_raw),
        "tiles": _tileset_tile_entries_from_image(image_raw, tile_width, tile_height, tile_count),
    }


def _tilemap_cel_chunk_data(layer_index: int, width: int, height: int, tile_matrix: list[list[int]]) -> bytes:
    raw = _tilemap_raw_bytes(tile_matrix)
    return (
        struct.pack(
            "<HhhBHh5sHHHIIII10s",
            layer_index,
            0,
            0,
            255,
            3,
            0,
            b"\x00" * 5,
            width,
            height,
            32,
            ASE_TILE_ID_MASK,
            ASE_TILE_X_FLIP_MASK,
            ASE_TILE_Y_FLIP_MASK,
            ASE_TILE_DIAGONAL_FLIP_MASK,
            b"\x00" * 10,
        )
        + zlib.compress(raw)
    )


def _parse_tilemap_or_compressed_cel_chunk(data: bytes, project_width: int, project_height: int) -> dict:
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
            raw = bounded_decompress(data[offset:], width * height * 4)
        except PNGChunkError as exc:
            raise AsepriteUserDataError("aseprite_cel_decompression_failed", exc.message) from exc
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
            "cel_visual_hash": _hash_bytes(raw),
        }
    if cel_type != 3:
        raise AsepriteUserDataError(
            "aseprite_cel_type_unsupported",
            "Stage 0 tilemap parser supports compressed image and compressed tilemap cels only",
        )
    tilemap_header_size = struct.calcsize("<HHHIIII10s")
    if offset + tilemap_header_size > len(data):
        raise AsepriteUserDataError(
            "aseprite_tilemap_cel_header_truncated",
            "compressed Aseprite Tilemap Cel header is truncated",
        )
    (
        width,
        height,
        bits_per_tile,
        tile_id_mask,
        x_flip_mask,
        y_flip_mask,
        diagonal_flip_mask,
        _tilemap_reserved,
    ) = struct.unpack("<HHHIIII10s", data[offset : offset + tilemap_header_size])
    offset += tilemap_header_size
    if bits_per_tile != 32:
        raise AsepriteUserDataError(
            "aseprite_tilemap_bits_per_tile_unsupported",
            "Stage 0 tilemap parser supports 32-bit tile values only",
        )
    if [width, height] != [project_width, project_height]:
        raise AsepriteUserDataError(
            "aseprite_tilemap_dimensions_mismatch",
            "compressed Aseprite Tilemap Cel dimensions must match project dimensions",
        )
    expected_size = width * height * 4
    try:
        raw = bounded_decompress(data[offset:], expected_size)
    except PNGChunkError as exc:
        raise AsepriteUserDataError("aseprite_tilemap_decompression_failed", exc.message) from exc
    if len(raw) != expected_size:
        raise AsepriteUserDataError(
            "aseprite_tilemap_payload_size_mismatch",
            "decoded Aseprite Tilemap Cel payload size does not match dimensions",
        )
    tile_values = [
        struct.unpack("<I", raw[index : index + 4])[0]
        for index in range(0, len(raw), 4)
    ]
    tile_matrix = [
        [
            tile_values[y * width + x] & tile_id_mask
            for x in range(width)
        ]
        for y in range(height)
    ]
    return {
        **base,
        "width": width,
        "height": height,
        "bits_per_tile": bits_per_tile,
        "tile_id_mask": tile_id_mask,
        "x_flip_mask": x_flip_mask,
        "y_flip_mask": y_flip_mask,
        "diagonal_flip_mask": diagonal_flip_mask,
        "raw_tile_bytes": raw,
        "raw_tile_hash": _hash_bytes(raw),
        "tile_matrix": tile_matrix,
        "tile_values": tile_values,
    }


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


def _tilemap_layer_semantics() -> dict:
    return {
        "layer_index": 0,
        "name": "Mechagotchi semantic tilemap",
        "layer_type": 2,
        "semantic_role": "organ_tilemap",
        "tileset_index": 0,
    }


def _tileset_semantics(grid: dict) -> dict:
    visual_by_organ = _visual_by_organ(grid)
    tiles = [
        {
            "tile_id": 0,
            "semantic": "empty",
            "semantic_organ": None,
            "hex": "#000000",
            "rgba": [0, 0, 0, 0],
        },
        {
            "tile_id": 1,
            "semantic": "core",
            "semantic_organ": "core",
            "hex": visual_by_organ["core"],
            "rgba": list(_hex_to_rgba(visual_by_organ["core"])),
        },
        {
            "tile_id": 2,
            "semantic": "sensors",
            "semantic_organ": "sensors",
            "hex": visual_by_organ["sensors"],
            "rgba": list(_hex_to_rgba(visual_by_organ["sensors"])),
        },
        {
            "tile_id": 3,
            "semantic": "expression",
            "semantic_organ": "expression",
            "hex": visual_by_organ["expression"],
            "rgba": list(_hex_to_rgba(visual_by_organ["expression"])),
        },
    ]
    return {
        "tileset_id": 0,
        "flags": 6,
        "tile_width": 1,
        "tile_height": 1,
        "base_index": 1,
        "name": "Mechagotchi semantic organ tiles",
        "tiles": tiles,
    }


def _tilemap_semantics(grid: dict) -> dict:
    width, height = grid["grid_size"]
    tile_ids_by_semantic = {"empty": 0, "core": 1, "sensors": 2, "expression": 3}
    organ_by_coordinate = {
        (cell["x"], cell["y"]): cell.get("organ")
        for cell in grid.get("cells", [])
    }
    matrix = []
    counts = {"core": 0, "sensors": 0, "expression": 0}
    for y in range(height):
        row = []
        for x in range(width):
            organ = organ_by_coordinate.get((x, y))
            tile_id = tile_ids_by_semantic.get(organ or "empty", 0)
            row.append(tile_id)
            if organ in counts:
                counts[organ] += 1
        matrix.append(row)
    return {
        "width": width,
        "height": height,
        "tile_ids_by_semantic": tile_ids_by_semantic,
        "organ_by_tile_id": {
            "0": None,
            "1": "core",
            "2": "sensors",
            "3": "expression",
        },
        "tile_matrix": matrix,
        "organ_tile_counts": counts,
        "tile_id_mask": ASE_TILE_ID_MASK,
        "x_flip_mask": ASE_TILE_X_FLIP_MASK,
        "y_flip_mask": ASE_TILE_Y_FLIP_MASK,
        "diagonal_flip_mask": ASE_TILE_DIAGONAL_FLIP_MASK,
    }


def _build_tilemap_tileset_metadata(
    canonical_hash: str,
    grid: dict,
    sidecar: dict,
    decoded: dict,
) -> dict:
    slice_semantics = _slice_semantics(grid)
    tileset = _tileset_semantics(grid)
    return {
        "metadata_version": ASE_TILEMAP_TILESET_VERSION,
        "format_id": "libresprite_project",
        "native_location": ASE_TILEMAP_TILESET_NATIVE_LOCATION,
        "writer_policy": ASE_TILEMAP_TILESET_POLICY,
        "canonical_project_hash": canonical_hash,
        "tilemap_hashes": decoded["tilemap_hashes"],
        "tileset_image_hash": decoded["tilesets"][0]["image_hash"],
        "sidecar_hash": _hash_payload(sidecar),
        "sidecar": sidecar,
        "palette_semantics": _palette_semantics(grid),
        "slice_semantics": slice_semantics,
        "slice_bounds_by_organ": {
            entry["semantic_organ"]: entry["bounds"] for entry in slice_semantics
        },
        "tag_semantics": _tag_semantics(),
        "tilemap_layer_semantics": _tilemap_layer_semantics(),
        "tileset_semantics": {
            "tileset_id": tileset["tileset_id"],
            "flags": tileset["flags"],
            "tile_size": [tileset["tile_width"], tileset["tile_height"]],
            "base_index": tileset["base_index"],
            "name": tileset["name"],
            "tiles": tileset["tiles"],
        },
        "tilemap_semantics": _tilemap_semantics(grid),
    }


def _extract_tilemap_tileset_metadata(project_bytes: bytes) -> dict:
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
                    raise AsepriteUserDataError("aseprite_tilemap_tileset_json_invalid", str(exc)) from exc
                if metadata.get("metadata_version") == ASE_TILEMAP_TILESET_VERSION:
                    return metadata
    raise AsepriteUserDataError(
        "aseprite_tilemap_tileset_metadata_missing",
        "ASE project does not contain Mechagotchi tilemap/tileset User Data metadata",
    )


def _validate_tilemap_layer(decoded: dict, metadata: dict) -> None:
    expected = metadata.get("tilemap_layer_semantics", {})
    tilemap_layers = [layer for layer in decoded["layers"] if layer["layer_type"] == 2]
    if len(tilemap_layers) != 1:
        raise AsepriteUserDataError(
            "aseprite_tilemap_layer_count_mismatch",
            "Aseprite tilemap/tileset project must contain exactly one tilemap layer",
        )
    layer = tilemap_layers[0]
    current = {
        "layer_index": layer["index"],
        "name": layer["name"],
        "layer_type": layer["layer_type"],
        "semantic_role": "organ_tilemap",
        "tileset_index": layer["tileset_index"],
    }
    if current != expected:
        raise AsepriteUserDataError(
            "aseprite_tilemap_layer_semantics_mismatch",
            "Aseprite tilemap layer semantics do not match embedded metadata",
        )
    if len(decoded["tilemap_layer_user_data"]) != 1:
        raise AsepriteUserDataError(
            "aseprite_tilemap_layer_user_data_missing",
            "Aseprite tilemap layer User Data chunk must bind to the semantic tilemap layer",
        )


def _validate_tilesets(decoded: dict, metadata: dict) -> None:
    if decoded["tileset_chunk_count"] < 1:
        raise AsepriteUserDataError(
            "aseprite_tileset_missing",
            "Aseprite tilemap/tileset project must contain a Tileset Chunk 0x2023",
        )
    tileset = decoded["tilesets"][0]
    expected = metadata.get("tileset_semantics", {})
    current = {
        "tileset_id": tileset["tileset_id"],
        "flags": tileset["flags"],
        "tile_size": tileset["tile_size"],
        "base_index": tileset["base_index"],
        "name": tileset["name"],
    }
    expected_structure = {
        "tileset_id": expected.get("tileset_id"),
        "flags": expected.get("flags"),
        "tile_size": expected.get("tile_size"),
        "base_index": expected.get("base_index"),
        "name": expected.get("name"),
    }
    if current != expected_structure:
        raise AsepriteUserDataError(
            "aseprite_tileset_semantics_mismatch",
            "Aseprite Tileset chunk semantics do not match embedded metadata",
        )
    if tileset["image_hash"] != metadata.get("tileset_image_hash"):
        raise AsepriteUserDataError(
            "aseprite_tileset_image_hash_mismatch",
            "Aseprite Tileset image hash does not match embedded metadata",
        )
    if tileset["tiles"] != expected.get("tiles"):
        raise AsepriteUserDataError(
            "aseprite_tileset_semantics_mismatch",
            "Aseprite Tileset tile semantics do not match embedded metadata",
        )


def _validate_tilemap_cels(decoded: dict, metadata: dict) -> None:
    if decoded["tilemap_cel_count"] < 1:
        raise AsepriteUserDataError(
            "aseprite_tilemap_cels_missing",
            "Aseprite tilemap/tileset project must contain compressed Tilemap Cel Chunk 0x2005 type 3 payloads",
        )
    expected_semantics = metadata.get("tilemap_semantics", {})
    current_semantics = decoded["tilemap_semantics"]
    if current_semantics != expected_semantics:
        raise AsepriteUserDataError(
            "aseprite_tilemap_tile_ids_mismatch",
            "Aseprite Tilemap Cel tile IDs do not match embedded tilemap semantics",
        )
    if decoded["tilemap_hashes"] != metadata.get("tilemap_hashes"):
        raise AsepriteUserDataError(
            "aseprite_tilemap_hash_mismatch",
            "Aseprite Tilemap Cel hashes do not match embedded metadata",
        )


def _decoded_tilemap_semantics(tilemap_cels: list[dict]) -> dict:
    if not tilemap_cels:
        return {
            "width": 0,
            "height": 0,
            "tile_ids_by_semantic": {"empty": 0, "core": 1, "sensors": 2, "expression": 3},
            "organ_by_tile_id": {"0": None, "1": "core", "2": "sensors", "3": "expression"},
            "tile_matrix": [],
            "organ_tile_counts": {"core": 0, "sensors": 0, "expression": 0},
            "tile_id_mask": ASE_TILE_ID_MASK,
            "x_flip_mask": ASE_TILE_X_FLIP_MASK,
            "y_flip_mask": ASE_TILE_Y_FLIP_MASK,
            "diagonal_flip_mask": ASE_TILE_DIAGONAL_FLIP_MASK,
        }
    first = tilemap_cels[0]
    counts = {"core": 0, "sensors": 0, "expression": 0}
    organ_by_tile_id = {0: None, 1: "core", 2: "sensors", 3: "expression"}
    for row in first["tile_matrix"]:
        for tile_id in row:
            organ = organ_by_tile_id.get(tile_id)
            if organ in counts:
                counts[organ] += 1
    return {
        "width": first["width"],
        "height": first["height"],
        "tile_ids_by_semantic": {"empty": 0, "core": 1, "sensors": 2, "expression": 3},
        "organ_by_tile_id": {"0": None, "1": "core", "2": "sensors", "3": "expression"},
        "tile_matrix": first["tile_matrix"],
        "organ_tile_counts": counts,
        "tile_id_mask": first["tile_id_mask"],
        "x_flip_mask": first["x_flip_mask"],
        "y_flip_mask": first["y_flip_mask"],
        "diagonal_flip_mask": first["diagonal_flip_mask"],
    }


def _tilemap_hash_map(tilemap_cels: list[dict]) -> dict:
    return {
        f"frame_{cel['frame_index']}_layer_{cel['layer_index']}": cel["raw_tile_hash"]
        for cel in tilemap_cels
    }


def _tilemap_raw_bytes(tile_matrix: list[list[int]]) -> bytes:
    payload = bytearray()
    for row in tile_matrix:
        for tile_id in row:
            payload.extend(struct.pack("<I", tile_id))
    return bytes(payload)


def _tileset_raw_image(tileset: dict) -> bytes:
    payload = bytearray()
    for tile in sorted(tileset["tiles"], key=lambda item: item["tile_id"]):
        payload.extend(tile["rgba"])
    return bytes(payload)


def _tileset_tile_entries_from_image(image_raw: bytes, tile_width: int, tile_height: int, tile_count: int) -> list[dict]:
    if tile_width != 1 or tile_height != 1:
        raise AsepriteUserDataError(
            "aseprite_tileset_tile_size_unsupported",
            "Stage 0 tileset parser supports 1x1 semantic organ tiles only",
        )
    semantics = [
        ("empty", None),
        ("core", "core"),
        ("sensors", "sensors"),
        ("expression", "expression"),
    ]
    tiles = []
    for tile_id in range(tile_count):
        offset = tile_id * 4
        rgba = list(image_raw[offset : offset + 4])
        semantic, organ = semantics[tile_id] if tile_id < len(semantics) else (f"tile_{tile_id}", None)
        tiles.append(
            {
                "tile_id": tile_id,
                "semantic": semantic,
                "semantic_organ": organ,
                "hex": _rgba_to_hex(rgba),
                "rgba": rgba,
            }
        )
    return tiles


def _visual_by_organ(grid: dict) -> dict:
    visual = {}
    for organ in ["core", "sensors", "expression"]:
        cells = [cell for cell in grid.get("cells", []) if cell.get("organ") == organ]
        if not cells:
            raise ValueError(f"grid must contain cells for organ: {organ}")
        visual[organ] = cells[0]["visual"].lower()
    return visual


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
    if rgba[3] == 0:
        return "#000000"
    return f"#{rgba[0]:02x}{rgba[1]:02x}{rgba[2]:02x}"


def _invalid_probe_results(reference_result: dict) -> list[dict]:
    project_bytes = bytes.fromhex(reference_result["project_bytes_hex"])
    return [
        _compact_import_result(import_aseprite_tilemap_tileset_project(strip_aseprite_tileset_chunks(project_bytes))),
        _compact_import_result(import_aseprite_tilemap_tileset_project(strip_aseprite_tilemap_cel_chunks(project_bytes))),
        _compact_import_result(import_aseprite_tilemap_tileset_project(tamper_aseprite_tileset_image(project_bytes))),
        _compact_import_result(import_aseprite_tilemap_tileset_project(tamper_aseprite_tilemap_tile_id(project_bytes))),
        _compact_import_result(import_aseprite_tilemap_tileset_project(tamper_aseprite_tilemap_metadata(project_bytes))),
        _compact_import_result(import_aseprite_tilemap_tileset_project(tamper_aseprite_tilemap_metadata_json(project_bytes))),
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
        "tilemap_layer_count",
        "tag_count",
        "cel_count",
        "compressed_cel_count",
        "tilemap_cel_count",
        "chunk_count",
        "user_data_chunk_count",
        "palette_chunk_count",
        "palette_entry_count",
        "slice_count",
        "slice_key_count",
        "tileset_chunk_count",
        "tileset_tile_count",
        "color_depth_bpp",
        "native_mechagotchi_semantics",
    ]
    return {key: decoded[key] for key in keys if key in decoded}


def _tileset_summary(tileset: dict) -> dict:
    return {
        key: tileset[key]
        for key in [
            "index",
            "frame_index",
            "chunk_type",
            "tileset_id",
            "flags",
            "tile_count",
            "tile_size",
            "base_index",
            "name",
            "compressed_image_byte_count",
            "image_hash",
            "tiles",
        ]
        if key in tileset
    }


def _cel_summary(cel: dict) -> dict:
    keys = [
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
        "bits_per_tile",
        "tile_id_mask",
        "x_flip_mask",
        "y_flip_mask",
        "diagonal_flip_mask",
        "raw_tile_hash",
        "tile_matrix",
    ]
    return {key: cel[key] for key in keys if key in cel}


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
    for result in payload["tilemap_tileset_results"]:
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
                "tilemap_tileset_roundtrip_count",
                "tilemap_tileset_roundtrip_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "tilemap_tileset_summaries": [
            {
                "profile_id": result["profile_id"],
                "format_id": result["format_id"],
                "project_byte_count": result["project_byte_count"],
                "embedded_project_hash": result["embedded_project_hash"],
                "canonical_project_hash": result["canonical_project_hash"],
                "decoded_project": result["decoded_project"],
                "semantic_fidelity": result["semantic_fidelity"],
            }
            for result in json_report["tilemap_tileset_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# Aseprite Tilemap/Tileset Semantics Stage 0\n\n"
        "Aseprite/LibreSprite tilemap and tileset semantic proof for one "
        "Tilemap Layer type 2, one Tileset Chunk 0x2023, compressed Tilemap "
        "Cel Chunk 0x2005 type 3 payloads, Palette Chunk 0x2019 colors, "
        "Slice Chunk 0x2022 organ bounds, and frame tags.\n\n"
        f"- Tilemap/tileset round trips: {report['tilemap_tileset_roundtrip_success_count']}/"
        f"{report['tilemap_tileset_roundtrip_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}/"
        f"{report['invalid_probe_count']}\n"
        f"- Mean semantic fidelity: {metrics['mean_semantic_fidelity']}\n"
        f"- Tilemap hash preservation rate: {metrics['tilemap_hash_preservation_rate']}\n"
        f"- Tileset image hash preservation rate: {metrics['tileset_image_hash_preservation_rate']}\n"
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
        default=Path("data/workshop_editor/aseprite_tilemap_tileset_semantics_stage0"),
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
    report = run_aseprite_tilemap_tileset_semantics_lab(profile_paths, args.generated_root)
    write_aseprite_tilemap_tileset_semantics_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_ASEPRITE_TILEMAP_TILESET_SEMANTICS = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(_json_report(report), indent=2))


if __name__ == "__main__":
    main()
