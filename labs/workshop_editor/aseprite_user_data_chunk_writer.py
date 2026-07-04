import argparse
import hashlib
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

from external_metadata_sidecar import build_sidecar_for_grid, restore_grid_from_sidecar
from standard_image_sidecar_decoder import render_grid_rgba_pixels
from png_chunk_reader import PNGChunkError, bounded_decompress
from workshop_editor import compare_semantic_grid_fidelity


REPORT_PATH = ROOT / "data/workshop_editor/aseprite_user_data_chunk_writer_stage0.json"
DATA_PATH = ROOT / "data/workshop_editor/aseprite_user_data_chunk_writer_data.js"

ASE_HEADER_FORMAT = "<IHHHHHIHII B3sHBBhhHH84s"
ASE_FRAME_HEADER_FORMAT = "<IHHH2sI"
ASE_MAGIC = 0xA5E0
ASE_FRAME_MAGIC = 0xF1FA
ASE_CHUNK_LAYER = 0x2004
ASE_CHUNK_CEL = 0x2005
ASE_CHUNK_USER_DATA = 0x2020
ASE_USER_DATA_VERSION = "mechagotchi.aseprite_user_data.v1"
ASE_USER_DATA_PREFIX = "MECHAGOTCHI_ASE_USER_DATA_V1:"
ASE_NATIVE_LOCATION = "frame[0].layer[0].user_data.text"
ASE_WRITER_POLICY = "aseprite_user_data_chunk"


class AsepriteUserDataError(ValueError):
    def __init__(self, family: str, message: str):
        super().__init__(message)
        self.family = family
        self.message = message


def export_aseprite_user_data_project(grid: dict, slip_profile: dict) -> dict:
    canonical_project = _encode_aseprite_project(grid, metadata=None)
    canonical_hash = _hash_bytes(canonical_project)
    visual_hash = _cel_visual_hash_from_grid(grid)
    asset = {
        "asset_id": f"{grid['grid_id']}.aseprite",
        "format_id": "libresprite_project",
        "media_type": "application/octet-stream",
        "uri": f"generated://workshop/project/{grid['grid_id']}.aseprite",
        "width": grid["grid_size"][0],
        "height": grid["grid_size"][1],
        "frame_count": 1,
        "content_hash": canonical_hash,
        "semantic_policy": ASE_WRITER_POLICY,
    }
    sidecar = build_sidecar_for_grid(grid, slip_profile, asset)
    sidecar["sidecar_id"] = f"{grid['grid_id']}_aseprite_user_data_sidecar"
    sidecar["asset_binding"]["semantic_policy"] = ASE_WRITER_POLICY
    sidecar["project_binding"] = {
        "format_id": "libresprite_project",
        "decoder_scope": "aseprite_frame_layer_user_data_and_compressed_rgba_cel_subset",
        "native_mechagotchi_semantics": True,
        "semantic_policy": ASE_WRITER_POLICY,
        "native_metadata_version": ASE_USER_DATA_VERSION,
    }
    sidecar["limitations"] = [
        "Stage 0 Aseprite/LibreSprite User Data writer covers one layer, one frame, one compressed RGBA cel, and one User Data text chunk.",
        "Live external editor rewrite validation is not verified by this lab.",
        "Full editor-native tags, timelines, tilemaps, linked cels, and arbitrary chunk coverage remain separate; palette/slice semantics are covered by a later Stage 0 lab.",
    ]
    metadata = _build_user_data_metadata(canonical_hash, visual_hash, sidecar)
    project_bytes = _encode_aseprite_project(grid, metadata=metadata)
    decoded = decode_aseprite_user_data_project(project_bytes)
    return {
        "project_bytes": project_bytes,
        "canonical_project_bytes": canonical_project,
        "embedded_project_hash": _hash_bytes(project_bytes),
        "canonical_project_hash": canonical_hash,
        "metadata": metadata,
        "sidecar": sidecar,
        "decoded_project": decoded,
    }


def decode_aseprite_user_data_project(project_bytes: bytes) -> dict:
    parsed = _parse_aseprite(project_bytes)
    layers = []
    cels = []
    user_data_chunks = []
    last_target = None
    native = False
    cel_visual_hash = None
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
            elif chunk_type == ASE_CHUNK_CEL:
                cel = _parse_cel_chunk(chunk["data"], parsed["header"]["width"], parsed["header"]["height"])
                cel["index"] = len(cels)
                cel["frame_index"] = frame_index
                cels.append(cel)
                cel_visual_hash = cel["cel_visual_hash"]
                last_target = {
                    "target_type": "cel",
                    "target_index": cel["index"],
                    "target_name": f"cel_{cel['index']}",
                }
            elif chunk_type == ASE_CHUNK_USER_DATA:
                user_data = _parse_user_data_chunk(chunk["data"])
                target = last_target or {
                    "target_type": "unknown",
                    "target_index": None,
                    "target_name": None,
                }
                entry = {
                    "chunk_type": "0x2020",
                    "flags": user_data["flags"],
                    "text_present": user_data["text"] is not None,
                    "text_hash": _hash_text(user_data["text"] or ""),
                    **target,
                }
                user_data_chunks.append(entry)
                if isinstance(user_data["text"], str) and user_data["text"].startswith(ASE_USER_DATA_PREFIX):
                    native = True

    return {
        "format_id": "libresprite_project",
        "magic": hex(parsed["header"]["magic"]),
        "frame_magic": hex(parsed["frames"][0]["magic"]) if parsed["frames"] else None,
        "dimensions": [parsed["header"]["width"], parsed["header"]["height"]],
        "frame_count": parsed["header"]["frames"],
        "layer_count": len(layers),
        "cel_count": len(cels),
        "chunk_count": total_chunk_count,
        "user_data_chunk_count": len(user_data_chunks),
        "color_depth_bpp": parsed["header"]["color_depth"],
        "first_frame_duration_ms": parsed["frames"][0]["duration_ms"] if parsed["frames"] else parsed["header"]["speed_ms"],
        "layers": layers,
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
        "user_data_chunks": user_data_chunks,
        "cel_visual_hash": cel_visual_hash,
        "native_mechagotchi_semantics": native,
    }


def extract_aseprite_user_data_sidecar(project_bytes: bytes) -> dict:
    decoded = decode_aseprite_user_data_project(project_bytes)
    metadata = _extract_metadata(project_bytes)
    if metadata.get("metadata_version") != ASE_USER_DATA_VERSION:
        raise AsepriteUserDataError(
            "aseprite_user_data_version_unsupported",
            "unsupported Aseprite User Data metadata version",
        )
    if metadata.get("format_id") != "libresprite_project":
        raise AsepriteUserDataError(
            "aseprite_user_data_format_mismatch",
            "Aseprite User Data metadata format id mismatch",
        )
    sidecar = metadata.get("sidecar")
    if not isinstance(sidecar, dict):
        raise AsepriteUserDataError(
            "aseprite_user_data_sidecar_missing",
            "Aseprite User Data metadata must contain a sidecar object",
        )
    if _hash_payload(sidecar) != metadata.get("sidecar_hash"):
        raise AsepriteUserDataError(
            "aseprite_user_data_sidecar_hash_mismatch",
            "Aseprite User Data sidecar hash does not match the embedded sidecar",
        )
    if decoded.get("cel_visual_hash") != metadata.get("cel_visual_hash"):
        raise AsepriteUserDataError(
            "aseprite_user_data_visual_hash_mismatch",
            "Aseprite User Data cel visual hash does not match the current cel payload",
        )
    canonical = strip_aseprite_user_data_chunks(project_bytes)
    canonical_hash = _hash_bytes(canonical)
    if canonical_hash != metadata.get("canonical_project_hash"):
        raise AsepriteUserDataError(
            "aseprite_user_data_canonical_hash_mismatch",
            "Aseprite User Data canonical project hash does not match the stripped project",
        )
    if sidecar.get("asset_binding", {}).get("content_hash") != canonical_hash:
        raise AsepriteUserDataError(
            "aseprite_user_data_sidecar_asset_hash_mismatch",
            "Aseprite User Data sidecar asset hash does not match the canonical project hash",
        )
    return {
        "ok": True,
        "metadata": metadata,
        "sidecar": sidecar,
        "decoded_project": _decoded_project_summary(decoded),
        "canonical_project_hash": canonical_hash,
        "embedded_project_hash": _hash_bytes(project_bytes),
    }


def import_aseprite_user_data_project(project_bytes: bytes, source_grid: dict | None = None) -> dict:
    try:
        extracted = extract_aseprite_user_data_sidecar(project_bytes)
    except AsepriteUserDataError as exc:
        return _failed_import("aseprite_user_data", exc.family, exc.message)

    sidecar = extracted["sidecar"]
    asset = deepcopy(sidecar["asset_binding"])
    try:
        restored = restore_grid_from_sidecar(sidecar, asset)
    except ValueError as exc:
        return _failed_import("sidecar", "aseprite_user_data_sidecar_invalid", str(exc))

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
                "cel_visual_hash",
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
            "semantic_policy": ASE_WRITER_POLICY,
            "native_mechagotchi_semantics": True,
            "native_location": ASE_NATIVE_LOCATION,
            "user_data_chunk_type": "0x2020",
            "live_external_editor_verified": False,
        },
        "semantic_diff": diff,
        "semantic_fidelity": fidelity,
        "errors": errors,
        "error_families": sorted({error["family"] for error in errors}),
    }


def strip_aseprite_user_data_chunks(project_bytes: bytes) -> bytes:
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


def tamper_aseprite_user_data_sidecar(project_bytes: bytes) -> bytes:
    parsed = _parse_aseprite(project_bytes)
    replaced = False
    frames = []
    for frame in parsed["frames"]:
        chunks = []
        for chunk in frame["chunks"]:
            if chunk["type"] == ASE_CHUNK_USER_DATA and not replaced:
                user_data = _parse_user_data_chunk(chunk["data"])
                if isinstance(user_data["text"], str) and user_data["text"].startswith(ASE_USER_DATA_PREFIX):
                    metadata = json.loads(user_data["text"][len(ASE_USER_DATA_PREFIX) :])
                    metadata["sidecar"]["asset_binding"]["width"] += 1
                    chunks.append(_chunk(ASE_CHUNK_USER_DATA, _user_data_chunk_data(metadata)))
                    replaced = True
                    continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    if not replaced:
        raise AsepriteUserDataError("aseprite_user_data_missing", "no Mechagotchi User Data chunk found")
    return _write_aseprite(parsed["header"], frames)


def tamper_aseprite_visual_payload(project_bytes: bytes) -> bytes:
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
                chunks.append(_chunk(ASE_CHUNK_CEL, _cel_chunk_data(parsed["header"]["width"], parsed["header"]["height"], bytes(raw))))
                replaced = True
                continue
            chunks.append(chunk)
        frames.append({"duration_ms": frame["duration_ms"], "chunks": chunks})
    if not replaced:
        raise AsepriteUserDataError("aseprite_cel_chunk_missing", "no compressed cel chunk found")
    return _write_aseprite(parsed["header"], frames)


def run_aseprite_user_data_chunk_writer_lab(profile_paths: list[Path], generated_root: Path) -> dict:
    user_data_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        exported = export_aseprite_user_data_project(grid, profile)
        imported = import_aseprite_user_data_project(exported["project_bytes"], source_grid=grid)
        user_data_results.append(
            {
                "profile_id": profile["profile_id"],
                "profile_path": _portable(profile_path),
                "grid_path": _portable(grid_path),
                "format_id": "libresprite_project",
                "project_file_name": f"{profile['profile_id']}_user_data.aseprite",
                "project_bytes_hex": exported["project_bytes"].hex(),
                "project_byte_count": len(exported["project_bytes"]),
                "embedded_project_hash": exported["embedded_project_hash"],
                "canonical_project_hash": exported["canonical_project_hash"],
                "metadata": _metadata_summary(exported["metadata"]),
                "native_sidecar": exported["sidecar"],
                "decoded_project": _decoded_project_summary(exported["decoded_project"]),
                "import_result": _compact_import_result(imported),
                "restored_grid_validation": imported.get("restored_grid_validation", {}),
                "semantic_diff": imported.get("semantic_diff", {}),
                "semantic_fidelity": imported.get("semantic_fidelity", 0.0),
                "cel_visual_hash_preserved": (
                    exported["metadata"]["cel_visual_hash"]
                    == exported["decoded_project"]["cel_visual_hash"]
                ),
            }
        )

    invalid_probe_results = _invalid_probe_results(user_data_results[0])
    success_count = sum(
        1
        for result in user_data_results
        if result["import_result"]["ok"]
        and result["restored_grid_validation"].get("valid")
        and result["restored_grid_validation"].get("slip_aligned")
        and result["semantic_fidelity"] == 1.0
    )
    invalid_rejected_count = sum(1 for result in invalid_probe_results if not result["ok"])
    visual_hash_preserved = sum(1 for result in user_data_results if result["cel_visual_hash_preserved"])
    return {
        "artifact_id": "aseprite_user_data_chunk_writer_stage0",
        "status": "research_aseprite_user_data_chunk_writer_no_package_code",
        "date": "2026-05-14",
        "purpose": (
            "Prove a Stage 0 Aseprite/LibreSprite User Data Chunk writer for "
            "one-frame compressed RGBA cel projects without claiming arbitrary "
            "editor project coverage or live external editor validation."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
            "labs/workshop_editor/third_party_project_decoder.py",
            "labs/workshop_editor/project_native_metadata_writer.py",
            "labs/workshop_editor/aseprite_user_data_chunk_writer.py",
        ],
        "external_anchors": [
            {
                "source": "Aseprite file-format specification",
                "url": "https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md",
                "used_for": "ASE header, frame header, Layer Chunk 0x2004, Cel Chunk 0x2005, and User Data Chunk 0x2020 layout.",
            },
            {
                "source": "LibreSprite GitHub",
                "url": "https://github.com/LibreSprite/LibreSprite",
                "used_for": "LibreSprite remains a compatibility boundary; no GPL editor code is embedded.",
            },
        ],
        "profile_count": len(profile_paths),
        "user_data_roundtrip_count": len(user_data_results),
        "user_data_roundtrip_success_count": success_count,
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "metrics": {
            "user_data_roundtrip_success_rate": _ratio(success_count, len(user_data_results)),
            "mean_semantic_fidelity": round(
                sum(result["semantic_fidelity"] for result in user_data_results)
                / max(1, len(user_data_results)),
                6,
            ),
            "cel_visual_hash_preservation_rate": _ratio(
                visual_hash_preserved,
                len(user_data_results),
            ),
            "invalid_probe_rejection_rate": _ratio(
                invalid_rejected_count,
                len(invalid_probe_results),
            ),
            "live_external_editor_verified": False,
        },
        "user_data_results": user_data_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "aseprite_libresprite_user_data_chunk_writer",
            "aseprite_layer_chunk_writer_subset",
            "aseprite_compressed_rgba_cel_chunk_writer_subset",
            "aseprite_user_data_sidecar_semantic_restore",
            "aseprite_user_data_hash_validation",
        ],
        "blocked_states": [
            "live_external_editor_rewrite_validation",
            "full_project_format_coverage",
            "advanced_tags_layers_timeline_schema_coverage",
            "arbitrary_aseprite_project_schema_coverage",
            "package_runtime_lifecycle_integration",
            "manual_readability_calibration",
            "profile_weighted_evolution",
            "community_profile_packs",
        ],
        "decision": "prototype_aseprite_user_data_chunk_writer_subset",
        "next_research_step": (
            "Keep live external editor validation, advanced tags/layers timeline "
            "schema coverage, and full project-format coverage blocked until "
            "direct editor fixtures and broader chunk/schema tests exist."
        ),
    }


def write_aseprite_user_data_chunk_writer_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "aseprite_user_data_chunk_writer_stage0.json", _json_report(report))
    for result in report["user_data_results"]:
        (output_dir / result["project_file_name"]).write_bytes(
            bytes.fromhex(result["project_bytes_hex"])
        )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "aseprite_user_data_chunk_writer_data.js").write_text(
        "window.MECHAGOTCHI_ASEPRITE_USER_DATA_CHUNK_WRITER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _encode_aseprite_project(grid: dict, metadata: dict | None) -> bytes:
    width, height = grid["grid_size"]
    raw_rgba = _raw_rgba_for_grid(grid)
    chunks = [
        _chunk(ASE_CHUNK_LAYER, _layer_chunk_data(width, height)),
    ]
    if metadata is not None:
        chunks.append(_chunk(ASE_CHUNK_USER_DATA, _user_data_chunk_data(metadata)))
    chunks.append(_chunk(ASE_CHUNK_CEL, _cel_chunk_data(width, height, raw_rgba)))
    header = {
        "frames": 1,
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
    return _write_aseprite(header, [{"duration_ms": 120, "chunks": chunks}])


def _write_aseprite(header: dict, frames: list[dict]) -> bytes:
    frame_payloads = []
    for frame in frames:
        chunk_payload = b"".join(_chunk_bytes(chunk) for chunk in frame["chunks"])
        frame_size = struct.calcsize(ASE_FRAME_HEADER_FORMAT) + len(chunk_payload)
        frame_payloads.append(
            struct.pack(
                ASE_FRAME_HEADER_FORMAT,
                frame_size,
                ASE_FRAME_MAGIC,
                len(frame["chunks"]),
                frame.get("duration_ms", 120),
                b"\x00\x00",
                0,
            )
            + chunk_payload
        )
    file_size = struct.calcsize(ASE_HEADER_FORMAT) + sum(len(payload) for payload in frame_payloads)
    header_bytes = struct.pack(
        ASE_HEADER_FORMAT,
        file_size,
        ASE_MAGIC,
        len(frames),
        header["width"],
        header["height"],
        header.get("color_depth", 32),
        header.get("flags", 1),
        header.get("speed_ms", 120),
        0,
        0,
        header.get("transparent_index", 0),
        b"\x00\x00\x00",
        header.get("color_count", 0),
        header.get("pixel_width", 1),
        header.get("pixel_height", 1),
        header.get("grid_x", 0),
        header.get("grid_y", 0),
        header.get("grid_width", header["width"]),
        header.get("grid_height", header["height"]),
        b"\x00" * 84,
    )
    return header_bytes + b"".join(frame_payloads)


def _parse_aseprite(project_bytes: bytes) -> dict:
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
    if header["color_depth"] != 32:
        raise AsepriteUserDataError("aseprite_color_depth_unsupported", "Stage 0 User Data writer only supports 32-bit RGBA")

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
    return (
        struct.pack("<HHHHHHB3s", 3, 0, 0, width, height, 0, 255, b"\x00\x00\x00")
        + _pack_string("Mechagotchi semantic layer")
    )


def _parse_layer_chunk(data: bytes) -> dict:
    minimum = struct.calcsize("<HHHHHHB3s")
    if len(data) < minimum:
        raise AsepriteUserDataError("aseprite_layer_chunk_truncated", "ASE Layer chunk is truncated")
    flags, layer_type, child_level, default_width, default_height, blend_mode, opacity, _reserved = struct.unpack(
        "<HHHHHHB3s",
        data[:minimum],
    )
    name, offset = _unpack_string(data, minimum)
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
    }


def _user_data_chunk_data(metadata: dict) -> bytes:
    return struct.pack("<I", 1) + _pack_string(
        ASE_USER_DATA_PREFIX
        + json.dumps(metadata, sort_keys=True, separators=(",", ":"))
    )


def _parse_user_data_chunk(data: bytes) -> dict:
    if len(data) < 4:
        raise AsepriteUserDataError("aseprite_user_data_chunk_truncated", "ASE User Data chunk is truncated")
    flags = struct.unpack("<I", data[:4])[0]
    offset = 4
    text = None
    color = None
    if flags & 1:
        text, offset = _unpack_string(data, offset)
    if flags & 2:
        if offset + 4 > len(data):
            raise AsepriteUserDataError("aseprite_user_data_color_truncated", "ASE User Data color is truncated")
        color = list(data[offset : offset + 4])
        offset += 4
    if flags & ~0x03:
        raise AsepriteUserDataError("aseprite_user_data_properties_unsupported", "Stage 0 User Data parser supports text and color flags only")
    if offset != len(data):
        raise AsepriteUserDataError("aseprite_user_data_extra_bytes", "unexpected bytes after ASE User Data chunk")
    return {"flags": flags, "text": text, "color": color}


def _cel_chunk_data(width: int, height: int, raw_rgba: bytes) -> bytes:
    expected_length = width * height * 4
    if len(raw_rgba) != expected_length:
        raise ValueError("raw RGBA payload does not match dimensions")
    return (
        struct.pack("<HhhBHh5sHH", 0, 0, 0, 255, 2, 0, b"\x00" * 5, width, height)
        + zlib.compress(raw_rgba)
    )


def _parse_cel_chunk(data: bytes, project_width: int, project_height: int) -> dict:
    prefix_size = struct.calcsize("<HhhBHh5s")
    if len(data) < prefix_size:
        raise AsepriteUserDataError("aseprite_cel_chunk_truncated", "ASE Cel chunk is truncated")
    layer_index, x, y, opacity, cel_type, z_index, _reserved = struct.unpack(
        "<HhhBHh5s",
        data[:prefix_size],
    )
    offset = prefix_size
    if cel_type != 2:
        raise AsepriteUserDataError("aseprite_cel_type_unsupported", "Stage 0 User Data writer only supports compressed image cels")
    if offset + 4 > len(data):
        raise AsepriteUserDataError("aseprite_cel_dimensions_truncated", "compressed ASE Cel dimensions are truncated")
    width, height = struct.unpack("<HH", data[offset : offset + 4])
    offset += 4
    if [width, height] != [project_width, project_height]:
        raise AsepriteUserDataError("aseprite_cel_dimensions_mismatch", "compressed ASE Cel dimensions must match project dimensions")
    try:
        raw = bounded_decompress(data[offset:], width * height * 4)
    except PNGChunkError as exc:
        raise AsepriteUserDataError("aseprite_cel_decompression_failed", exc.message) from exc
    if len(raw) != width * height * 4:
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
        "raw_rgba": raw,
        "cel_visual_hash": _hash_bytes(raw),
    }


def _extract_metadata(project_bytes: bytes) -> dict:
    parsed = _parse_aseprite(project_bytes)
    for frame in parsed["frames"]:
        for chunk in frame["chunks"]:
            if chunk["type"] != ASE_CHUNK_USER_DATA:
                continue
            user_data = _parse_user_data_chunk(chunk["data"])
            text = user_data["text"]
            if isinstance(text, str) and text.startswith(ASE_USER_DATA_PREFIX):
                try:
                    return json.loads(text[len(ASE_USER_DATA_PREFIX) :])
                except json.JSONDecodeError as exc:
                    raise AsepriteUserDataError("aseprite_user_data_json_invalid", str(exc)) from exc
    raise AsepriteUserDataError(
        "aseprite_user_data_missing",
        "ASE project does not contain a Mechagotchi User Data chunk",
    )


def _build_user_data_metadata(canonical_hash: str, visual_hash: str, sidecar: dict) -> dict:
    return {
        "metadata_version": ASE_USER_DATA_VERSION,
        "format_id": "libresprite_project",
        "native_location": ASE_NATIVE_LOCATION,
        "writer_policy": ASE_WRITER_POLICY,
        "canonical_project_hash": canonical_hash,
        "cel_visual_hash": visual_hash,
        "sidecar_hash": _hash_payload(sidecar),
        "sidecar": sidecar,
    }


def _chunk(chunk_type: int, data: bytes) -> dict:
    return {"type": chunk_type, "data": data, "size": len(data) + 6}


def _chunk_bytes(chunk: dict) -> bytes:
    return struct.pack("<IH", len(chunk["data"]) + 6, chunk["type"]) + chunk["data"]


def _pack_string(text: str) -> bytes:
    payload = text.encode("utf-8")
    if len(payload) > 0xFFFF:
        raise ValueError("ASE string exceeds 65535 bytes")
    return struct.pack("<H", len(payload)) + payload


def _unpack_string(data: bytes, offset: int) -> tuple[str, int]:
    if offset + 2 > len(data):
        raise AsepriteUserDataError("aseprite_string_truncated", "ASE string length is truncated")
    length = struct.unpack("<H", data[offset : offset + 2])[0]
    offset += 2
    end = offset + length
    if end > len(data):
        raise AsepriteUserDataError("aseprite_string_truncated", "ASE string payload is truncated")
    try:
        return data[offset:end].decode("utf-8"), end
    except UnicodeDecodeError as exc:
        raise AsepriteUserDataError("aseprite_string_utf8_invalid", str(exc)) from exc


def _invalid_probe_results(reference_result: dict) -> list[dict]:
    project_bytes = bytes.fromhex(reference_result["project_bytes_hex"])
    return [
        _compact_import_result(import_aseprite_user_data_project(strip_aseprite_user_data_chunks(project_bytes))),
        _compact_import_result(import_aseprite_user_data_project(tamper_aseprite_user_data_sidecar(project_bytes))),
        _compact_import_result(import_aseprite_user_data_project(tamper_aseprite_visual_payload(project_bytes))),
    ]


def _raw_rgba_for_grid(grid: dict) -> bytes:
    return bytes(channel for pixel in render_grid_rgba_pixels(grid) for channel in pixel)


def _cel_visual_hash_from_grid(grid: dict) -> str:
    return _hash_bytes(_raw_rgba_for_grid(grid))


def _metadata_summary(metadata: dict) -> dict:
    return {
        key: metadata[key]
        for key in [
            "metadata_version",
            "format_id",
            "native_location",
            "writer_policy",
            "canonical_project_hash",
            "cel_visual_hash",
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
        "cel_count",
        "chunk_count",
        "user_data_chunk_count",
        "color_depth_bpp",
        "cel_visual_hash",
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
    for result in payload["user_data_results"]:
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
                "user_data_roundtrip_count",
                "user_data_roundtrip_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "user_data_summaries": [
            {
                "profile_id": result["profile_id"],
                "format_id": result["format_id"],
                "project_byte_count": result["project_byte_count"],
                "embedded_project_hash": result["embedded_project_hash"],
                "canonical_project_hash": result["canonical_project_hash"],
                "decoded_project": result["decoded_project"],
                "semantic_fidelity": result["semantic_fidelity"],
            }
            for result in json_report["user_data_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# Aseprite User Data Chunk Writer Stage 0\n\n"
        "Aseprite/LibreSprite User Data Chunk writer proof for one-frame, "
        "one-layer, compressed RGBA cel payloads with embedded Mechagotchi "
        "sidecar metadata.\n\n"
        f"- User Data round trips: {report['user_data_roundtrip_success_count']}/"
        f"{report['user_data_roundtrip_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}/"
        f"{report['invalid_probe_count']}\n"
        f"- Mean semantic fidelity: {metrics['mean_semantic_fidelity']}\n"
        f"- Cel visual hash preservation rate: {metrics['cel_visual_hash_preservation_rate']}\n"
        f"- Live external editor verified: {metrics['live_external_editor_verified']}\n\n"
        "This artifact does not claim live external editor validation, "
        "arbitrary Aseprite schemas, advanced tags/layers timeline schema "
        "coverage, package runtime integration, or full project-format coverage.\n"
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


def _hash_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _hash_text(payload: str) -> str:
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _hash_payload(payload: object) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _semantic_fidelity(diff: dict, source: dict) -> float:
    source_count = max(1, len(source.get("cells", [])))
    problem_count = (
        len(diff["changed_cells"])
        + len(diff["missing_cells"])
        + len(diff["added_cells"])
    )
    return round(max(0.0, 1.0 - problem_count / source_count), 6)


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


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
        default=ROOT / "data/workshop_editor/aseprite_user_data_chunk_writer_stage0",
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
    report = run_aseprite_user_data_chunk_writer_lab(profile_paths, args.generated_root)
    write_aseprite_user_data_chunk_writer_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_ASEPRITE_USER_DATA_CHUNK_WRITER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(_json_report(report), indent=2))


if __name__ == "__main__":
    main()
