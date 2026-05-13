import argparse
import base64
import binascii
import hashlib
import io
import json
import struct
import sys
import zipfile
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME_DIR = ROOT / "labs" / "grid_genome"
if str(GRID_GENOME_DIR) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME_DIR))

from slip import is_grid_aligned
from validator import validate_grid

from external_metadata_sidecar import (
    FORMAT_POLICIES,
    build_sidecar_for_grid,
    restore_grid_from_sidecar,
    validate_sidecar_binding,
)
from standard_image_sidecar_decoder import (
    PNGDecodeError,
    decode_png_rgba,
    encode_png_rgba,
    render_grid_rgba_pixels,
)
from workshop_editor import compare_semantic_grid_fidelity


REPORT_PATH = Path("data/workshop_editor/third_party_project_decoder_stage0.json")
DATA_PATH = Path("data/workshop_editor/third_party_project_decoder_data.js")


PROJECT_FORMATS = {
    "piskel_project": {
        "extension": ".piskel",
        "media_type": "application/json",
        "decoder_scope": "json_envelope_layer_chunk_metadata_and_png_chunk_dimensions",
        "external_anchor": "Piskel serializer/deserializer source",
    },
    "pixelorama_pxo": {
        "extension": ".pxo",
        "media_type": "application/octet-stream",
        "decoder_scope": "zip_container_data_json_and_frame_image_inventory",
        "external_anchor": "Pixelorama project documentation",
    },
    "libresprite_project": {
        "extension": ".aseprite",
        "media_type": "application/octet-stream",
        "decoder_scope": "aseprite_header_and_empty_frame_header_only",
        "external_anchor": "Aseprite file-format specification and LibreSprite fork boundary",
    },
}


class ProjectDecodeError(ValueError):
    def __init__(self, family: str, message: str):
        super().__init__(message)
        self.family = family
        self.message = message


def export_project_with_sidecar(
    grid: dict,
    slip_profile: dict,
    format_id: str,
) -> dict:
    if format_id == "piskel_project":
        project_bytes = encode_piskel_project(grid)
    elif format_id == "pixelorama_pxo":
        project_bytes = encode_pixelorama_pxo(grid)
    elif format_id == "libresprite_project":
        project_bytes = encode_aseprite_header_project(grid)
    else:
        raise ValueError(f"unsupported project format: {format_id}")

    decoded = decode_project_payload(project_bytes, format_id)
    asset = _asset_from_decoded_project(
        project_bytes,
        decoded,
        asset_id=f"{grid['grid_id']}{PROJECT_FORMATS[format_id]['extension']}",
        uri=f"generated://workshop/project/{grid['grid_id']}{PROJECT_FORMATS[format_id]['extension']}",
    )
    sidecar = build_sidecar_for_grid(grid, slip_profile, asset)
    sidecar["sidecar_id"] = f"{grid['grid_id']}_project_sidecar"
    sidecar["project_binding"] = {
        "format_id": format_id,
        "decoder_scope": PROJECT_FORMATS[format_id]["decoder_scope"],
        "decoded_project": _decoded_project_summary(decoded),
        "native_mechagotchi_semantics": False,
        "semantic_policy": "sidecar_required",
    }
    sidecar["limitations"] = [
        "Stage 0 parses third-party project container boundaries only.",
        "Semantic grid metadata is restored from the Mechagotchi sidecar.",
        "No embedded PNG metadata writer or native project-file writer is claimed.",
    ]
    return {
        "project_bytes": project_bytes,
        "asset": asset,
        "sidecar": sidecar,
        "decoded_project": decoded,
    }


def import_project_with_sidecar(project_bytes: bytes, sidecar: dict) -> dict:
    format_id = sidecar.get("asset_binding", {}).get("format_id")
    if format_id not in PROJECT_FORMATS:
        return _failed_import(
            "asset_binding.format_id",
            "unsupported_project_format",
            f"unsupported project format: {format_id!r}",
        )

    try:
        decoded = decode_project_payload(project_bytes, format_id)
    except ProjectDecodeError as exc:
        return _failed_import(format_id, exc.family, exc.message)

    binding = sidecar.get("asset_binding", {})
    asset = _asset_from_decoded_project(
        project_bytes,
        decoded,
        asset_id=binding.get("asset_id", f"unknown{PROJECT_FORMATS[format_id]['extension']}"),
        uri=binding.get("uri", "unknown://project"),
    )
    validation = validate_sidecar_binding(sidecar, asset)
    if not validation["ok"]:
        return {
            "ok": False,
            "asset": asset,
            "decoded_project": _decoded_project_summary(decoded),
            "validation": validation,
            "errors": validation["errors"],
            "error_families": validation["error_families"],
        }

    restored = restore_grid_from_sidecar(sidecar, asset)
    profile = sidecar["slip_binding"]["profile_snapshot"]
    grid_validation = validate_grid(restored)
    alignment = is_grid_aligned(restored, profile)
    source_grid = restore_grid_from_sidecar(sidecar, asset, validate=False)
    diff = compare_semantic_grid_fidelity(source_grid, restored)
    fidelity = _semantic_fidelity(diff, source_grid)
    project_policy = {
        "semantic_policy": "sidecar_required",
        "native_mechagotchi_semantics": False,
        "decoder_scope": PROJECT_FORMATS[format_id]["decoder_scope"],
    }
    return {
        "ok": grid_validation.ok and alignment.ok and fidelity == 1.0,
        "asset": asset,
        "decoded_project": _decoded_project_summary(decoded),
        "validation": validation,
        "restored_grid": restored,
        "restored_grid_validation": {
            "valid": grid_validation.ok,
            "errors": grid_validation.errors,
            "slip_aligned": alignment.ok,
            "slip_errors": alignment.errors,
        },
        "project_policy": project_policy,
        "semantic_diff": diff,
        "semantic_fidelity": fidelity,
        "errors": [],
        "error_families": [],
    }


def decode_project_payload(project_bytes: bytes, format_id: str) -> dict:
    if format_id == "piskel_project":
        return decode_piskel_project(project_bytes)
    if format_id == "pixelorama_pxo":
        return decode_pixelorama_pxo(project_bytes)
    if format_id == "libresprite_project":
        return decode_aseprite_header(project_bytes)
    raise ProjectDecodeError(
        "unsupported_project_format",
        f"unsupported project format: {format_id!r}",
    )


def encode_piskel_project(grid: dict) -> bytes:
    png_data_url = _png_data_url_for_grid(grid)
    layer = {
        "name": "Mechagotchi sidecar-bound layer",
        "opacity": 1,
        "frameCount": 1,
        "chunks": [
            {
                "layout": [[0]],
                "base64PNG": png_data_url,
            }
        ],
    }
    payload = {
        "modelVersion": 2,
        "piskel": {
            "name": grid["grid_id"],
            "description": "Mechagotchi workshop boundary fixture; semantics live in sidecar.",
            "fps": 12,
            "height": grid["grid_size"][1],
            "width": grid["grid_size"][0],
            "layers": [json.dumps(layer, separators=(",", ":"))],
            "hiddenFrames": [""],
        },
    }
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


def decode_piskel_project(project_bytes: bytes) -> dict:
    try:
        payload = json.loads(project_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProjectDecodeError("project_json_invalid", str(exc)) from exc

    piskel = payload.get("piskel")
    if not isinstance(piskel, dict):
        raise ProjectDecodeError("piskel_payload_missing", "piskel object is required")
    width = _positive_int(piskel.get("width"), "piskel.width")
    height = _positive_int(piskel.get("height"), "piskel.height")
    layers = piskel.get("layers")
    if not isinstance(layers, list) or not layers:
        raise ProjectDecodeError("piskel_layers_missing", "piskel layers are required")

    decoded_layers = []
    frame_count = 0
    chunk_count = 0
    for index, layer_string in enumerate(layers):
        if not isinstance(layer_string, str):
            raise ProjectDecodeError(
                "piskel_layer_invalid",
                f"layer {index} must be a JSON string",
            )
        try:
            layer = json.loads(layer_string)
        except json.JSONDecodeError as exc:
            raise ProjectDecodeError("piskel_layer_json_invalid", str(exc)) from exc
        layer_frame_count = _positive_int(layer.get("frameCount"), "layer.frameCount")
        chunks = layer.get("chunks")
        if not isinstance(chunks, list) or not chunks:
            raise ProjectDecodeError("piskel_chunks_missing", "layer chunks are required")
        for chunk in chunks:
            data_url = chunk.get("base64PNG") if isinstance(chunk, dict) else None
            chunk_png = _decode_png_data_url(data_url)
            try:
                decoded_png = decode_png_rgba(chunk_png)
            except PNGDecodeError as exc:
                raise ProjectDecodeError(
                    "piskel_chunk_png_invalid",
                    exc.message,
                ) from exc
            layout = chunk.get("layout")
            if not isinstance(layout, list) or not layout:
                raise ProjectDecodeError("piskel_chunk_layout_invalid", "chunk layout is required")
            if decoded_png["height"] != height:
                raise ProjectDecodeError(
                    "piskel_chunk_height_mismatch",
                    "chunk PNG height must match project height",
                )
            chunk_count += 1
        frame_count = max(frame_count, layer_frame_count)
        decoded_layers.append(
            {
                "name": layer.get("name", f"Layer {index + 1}"),
                "frame_count": layer_frame_count,
                "chunk_count": len(chunks),
            }
        )

    return {
        "format_id": "piskel_project",
        "model_version": payload.get("modelVersion"),
        "name": piskel.get("name", ""),
        "dimensions": [width, height],
        "frame_count": frame_count,
        "layer_count": len(decoded_layers),
        "chunk_count": chunk_count,
        "layers": decoded_layers,
        "native_mechagotchi_semantics": False,
    }


def encode_pixelorama_pxo(grid: dict) -> bytes:
    png_bytes = encode_png_rgba(
        grid["grid_size"][0],
        grid["grid_size"][1],
        render_grid_rgba_pixels(grid),
    )
    data = {
        "name": grid["grid_id"],
        "size": {
            "width": grid["grid_size"][0],
            "height": grid["grid_size"][1],
        },
        "fps": 12,
        "frames": [{"index": 0, "duration_ms": 120}],
        "layers": [{"name": "Mechagotchi sidecar-bound layer", "type": "pixel"}],
        "cels": [
            {
                "frame": 0,
                "layer": 0,
                "path": "image_data/frames/0/cel_0.png",
            }
        ],
        "mechagotchi_note": "Project payload is visual/editor metadata only; semantics live in sidecar.",
    }
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("data.json", json.dumps(data, indent=2))
        archive.writestr("image_data/frames/0/cel_0.png", png_bytes)
    return buffer.getvalue()


def decode_pixelorama_pxo(project_bytes: bytes) -> dict:
    if not zipfile.is_zipfile(io.BytesIO(project_bytes)):
        raise ProjectDecodeError("pxo_zip_invalid", "Pixelorama .pxo must be a zip container")
    try:
        with zipfile.ZipFile(io.BytesIO(project_bytes), "r") as archive:
            members = sorted(archive.namelist())
            if "data.json" not in members:
                raise ProjectDecodeError("pxo_data_json_missing", "data.json is required")
            try:
                data = json.loads(archive.read("data.json").decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ProjectDecodeError("pxo_data_json_invalid", str(exc)) from exc
            cel_paths = [
                cel.get("path")
                for cel in data.get("cels", [])
                if isinstance(cel, dict) and isinstance(cel.get("path"), str)
            ]
            if not cel_paths:
                cel_paths = [name for name in members if name.startswith("image_data/frames/")]
            if not cel_paths:
                raise ProjectDecodeError("pxo_frame_images_missing", "frame image data is required")
            try:
                decoded_png = decode_png_rgba(archive.read(cel_paths[0]))
            except PNGDecodeError as exc:
                raise ProjectDecodeError(
                    "pxo_frame_png_invalid",
                    exc.message,
                ) from exc
    except zipfile.BadZipFile as exc:
        raise ProjectDecodeError("pxo_zip_invalid", str(exc)) from exc

    size = data.get("size", {})
    width = _positive_int(size.get("width"), "data.size.width")
    height = _positive_int(size.get("height"), "data.size.height")
    if [decoded_png["width"], decoded_png["height"]] != [width, height]:
        raise ProjectDecodeError(
            "pxo_image_size_mismatch",
            "first cel image dimensions must match data.json size",
        )
    return {
        "format_id": "pixelorama_pxo",
        "is_zip": True,
        "members": members,
        "name": data.get("name", ""),
        "dimensions": [width, height],
        "frame_count": max(1, len(data.get("frames", []))),
        "layer_count": max(1, len(data.get("layers", []))),
        "cel_count": len(cel_paths),
        "native_mechagotchi_semantics": False,
    }


def encode_aseprite_header_project(grid: dict) -> bytes:
    width, height = grid["grid_size"]
    header_size = 128
    frame_header_size = 16
    file_size = header_size + frame_header_size
    header = struct.pack(
        "<IHHHHHIHII B3sHBBhhHH84s",
        file_size,
        0xA5E0,
        1,
        width,
        height,
        32,
        0,
        120,
        0,
        0,
        0,
        b"\x00\x00\x00",
        0,
        1,
        1,
        0,
        0,
        width,
        height,
        b"\x00" * 84,
    )
    frame_header = struct.pack("<IHHH2sI", frame_header_size, 0xF1FA, 0, 120, b"\x00\x00", 0)
    return header + frame_header


def decode_aseprite_header(project_bytes: bytes) -> dict:
    if len(project_bytes) < 128:
        raise ProjectDecodeError("aseprite_header_truncated", "ASE header must be 128 bytes")
    fields = struct.unpack("<IHHHHHIHII B3sHBBhhHH84s", project_bytes[:128])
    (
        file_size,
        magic,
        frames,
        width,
        height,
        color_depth,
        flags,
        speed_ms,
        _zero_a,
        _zero_b,
        transparent_index,
        _ignored,
        color_count,
        pixel_width,
        pixel_height,
        grid_x,
        grid_y,
        grid_width,
        grid_height,
        _reserved,
    ) = fields
    if magic != 0xA5E0:
        raise ProjectDecodeError("aseprite_magic_invalid", "ASE magic number must be 0xA5E0")
    if file_size != len(project_bytes):
        raise ProjectDecodeError("aseprite_file_size_mismatch", "ASE file size field must match payload length")
    if frames < 1:
        raise ProjectDecodeError("aseprite_frame_count_invalid", "ASE frame count must be positive")
    if width < 1 or height < 1:
        raise ProjectDecodeError("aseprite_dimensions_invalid", "ASE dimensions must be positive")
    if color_depth not in {8, 16, 32}:
        raise ProjectDecodeError("aseprite_color_depth_invalid", "ASE color depth must be 8, 16, or 32")
    frame_magic = None
    if len(project_bytes) >= 144:
        frame_size, frame_magic, old_chunks, frame_duration, _unused, new_chunks = struct.unpack(
            "<IHHH2sI",
            project_bytes[128:144],
        )
        if frame_size < 16:
            raise ProjectDecodeError("aseprite_frame_header_invalid", "ASE frame header size is invalid")
        if frame_magic != 0xF1FA:
            raise ProjectDecodeError("aseprite_frame_magic_invalid", "ASE frame magic must be 0xF1FA")
        chunk_count = new_chunks if new_chunks else old_chunks
    else:
        frame_duration = speed_ms
        chunk_count = 0
    return {
        "format_id": "libresprite_project",
        "magic": hex(magic),
        "frame_magic": hex(frame_magic) if frame_magic is not None else None,
        "dimensions": [width, height],
        "frame_count": frames,
        "layer_count": 0,
        "chunk_count": chunk_count,
        "color_depth_bpp": color_depth,
        "flags": flags,
        "speed_ms": speed_ms,
        "first_frame_duration_ms": frame_duration,
        "transparent_index": transparent_index,
        "color_count": color_count,
        "pixel_ratio": [pixel_width or 1, pixel_height or 1],
        "grid": {"x": grid_x, "y": grid_y, "width": grid_width, "height": grid_height},
        "native_mechagotchi_semantics": False,
    }


def run_third_party_project_decoder_lab(
    profile_paths: list[Path],
    generated_root: Path,
) -> dict:
    project_results = []
    format_sequence = ["piskel_project", "pixelorama_pxo", "libresprite_project"]
    for profile_path, format_id in zip(profile_paths, format_sequence, strict=True):
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        exported = export_project_with_sidecar(grid, profile, format_id)
        imported = import_project_with_sidecar(
            exported["project_bytes"],
            exported["sidecar"],
        )
        restored = imported.get("restored_grid", {})
        project_results.append(
            {
                "profile_id": profile["profile_id"],
                "profile_path": _portable(profile_path),
                "grid_path": _portable(grid_path),
                "format_id": format_id,
                "project_file_name": f"{profile['profile_id']}{PROJECT_FORMATS[format_id]['extension']}",
                "sidecar_file_name": f"{profile['profile_id']}_project_sidecar.json",
                "project_bytes_hex": exported["project_bytes"].hex(),
                "project_byte_count": len(exported["project_bytes"]),
                "asset": exported["asset"],
                "sidecar": exported["sidecar"],
                "decoded_project": _decoded_project_summary(exported["decoded_project"]),
                "import_result": _compact_import_result(imported),
                "restored_grid_validation": imported.get("restored_grid_validation", {}),
                "semantic_diff": imported.get("semantic_diff", {}),
                "semantic_fidelity": imported.get("semantic_fidelity", 0.0),
                "project_policy": imported.get("project_policy", {}),
                "restored_grid_present": bool(restored),
            }
        )

    invalid_probe_results = _invalid_probe_results(project_results[0])
    decoder_success_count = sum(
        1
        for result in project_results
        if result["import_result"]["ok"]
        and result["decoded_project"]["dimensions"]
        == [result["asset"]["width"], result["asset"]["height"]]
    )
    restore_success_count = sum(
        1
        for result in project_results
        if result["import_result"]["ok"]
        and result["restored_grid_validation"].get("valid")
        and result["restored_grid_validation"].get("slip_aligned")
        and result["semantic_fidelity"] == 1.0
    )
    invalid_rejected_count = sum(1 for result in invalid_probe_results if not result["ok"])
    return {
        "artifact_id": "third_party_project_decoder_stage0",
        "status": "research_third_party_project_decoder_boundary_no_package_code",
        "date": "2026-05-13",
        "purpose": (
            "Prove third-party project-file container boundaries can be decoded "
            "far enough to bind dimensions, frame count, and content hashes to a "
            "Mechagotchi sidecar without claiming native editor semantics."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
            "labs/workshop_editor/external_metadata_sidecar.py",
            "labs/workshop_editor/third_party_project_decoder.py",
        ],
        "external_anchors": [
            {
                "source": "Piskel Serializer.js",
                "url": "https://github.com/piskelapp/piskel/blob/master/src/js/utils/serialization/Serializer.js",
                "used_for": "Piskel JSON envelope fields, layer strings, chunks, and base64 PNG chunk layout.",
            },
            {
                "source": "Piskel Deserializer.js",
                "url": "https://github.com/piskelapp/piskel/blob/master/src/js/utils/serialization/Deserializer.js",
                "used_for": "Piskel modelVersion branching and layer JSON-string parsing boundary.",
            },
            {
                "source": "Pixelorama project documentation",
                "url": "https://pixelorama.org/concepts/project/",
                "used_for": ".pxo as a zip containing data.json and image_data frame assets.",
            },
            {
                "source": "Aseprite file-format specification",
                "url": "https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md",
                "used_for": "ASE little-endian header, magic number, dimensions, color depth, and frame header.",
            },
            {
                "source": "LibreSprite GitHub",
                "url": "https://github.com/LibreSprite/LibreSprite",
                "used_for": "LibreSprite is treated as a GPL fork boundary; this lab does not embed editor code.",
            },
        ],
        "profile_count": len(project_results),
        "project_decoder_success_count": decoder_success_count,
        "sidecar_restore_success_count": restore_success_count,
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "metrics": {
            "project_decoder_success_rate": _ratio(decoder_success_count, len(project_results)),
            "sidecar_restore_success_rate": _ratio(restore_success_count, len(project_results)),
            "mean_semantic_fidelity": round(
                sum(result["semantic_fidelity"] for result in project_results)
                / max(1, len(project_results)),
                6,
            ),
            "invalid_probe_rejection_rate": _ratio(
                invalid_rejected_count,
                len(invalid_probe_results),
            ),
            "native_metadata_writer_count": 0,
            "project_formats_covered": len(project_results),
        },
        "project_results": project_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "third_party_project_decoder_boundary",
            "piskel_project_json_boundary",
            "pixelorama_pxo_zip_data_json_boundary",
            "aseprite_libresprite_header_boundary",
            "project_file_sidecar_binding_integrity",
            "project_import_rejects_missing_or_mismatched_sidecar",
        ],
        "blocked_states": [
            "full_project_format_coverage",
            "png_adam7_interlace_decoder",
            "apng_decoder",
            "full_png_conformance",
            "spritesheet_variant_layout_coverage",
            "embedded_png_metadata_writer",
            "project_file_native_metadata_writer",
            "runtime_lifecycle_archive_selection",
            "profile_weighted_evolution",
        ],
        "decision": "prototype_third_party_project_decoder_boundary",
        "next_research_step": (
            "Broaden spritesheet layout coverage, "
            "or specify runtime lifecycle/archive selection integration before "
            "profile-weighted evolution claims."
        ),
    }


def write_third_party_project_decoder_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "third_party_project_decoder_stage0.json", _json_report(report))
    for result in report["project_results"]:
        (output_dir / result["project_file_name"]).write_bytes(
            bytes.fromhex(result["project_bytes_hex"])
        )
        _write_json(output_dir / result["sidecar_file_name"], result["sidecar"])
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "third_party_project_decoder_data.js").write_text(
        "window.MECHAGOTCHI_THIRD_PARTY_PROJECT_DECODER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _invalid_probe_results(reference_result: dict) -> list[dict]:
    project_bytes = bytes.fromhex(reference_result["project_bytes_hex"])
    sidecar = reference_result["sidecar"]
    wrong_hash_sidecar = deepcopy(sidecar)
    wrong_hash_sidecar["asset_binding"]["content_hash"] = "sha256:not-the-project"
    unsupported_sidecar = deepcopy(sidecar)
    unsupported_sidecar["asset_binding"]["format_id"] = "unsupported_project"
    return [
        _compact_import_result(import_project_with_sidecar(b"{not-json", sidecar)),
        _compact_import_result(import_project_with_sidecar(project_bytes, wrong_hash_sidecar)),
        _compact_import_result(import_project_with_sidecar(project_bytes, unsupported_sidecar)),
    ]


def _png_data_url_for_grid(grid: dict) -> str:
    png = encode_png_rgba(
        grid["grid_size"][0],
        grid["grid_size"][1],
        render_grid_rgba_pixels(grid),
    )
    return "data:image/png;base64," + base64.b64encode(png).decode("ascii")


def _decode_png_data_url(value: object) -> bytes:
    if not isinstance(value, str) or not value.startswith("data:image/png;base64,"):
        raise ProjectDecodeError("piskel_base64_png_invalid", "base64 PNG data URL is required")
    try:
        return base64.b64decode(value.split(",", 1)[1], validate=True)
    except (ValueError, binascii.Error) as exc:  # type: ignore[name-defined]
        raise ProjectDecodeError("piskel_base64_png_invalid", str(exc)) from exc


def _asset_from_decoded_project(
    project_bytes: bytes,
    decoded: dict,
    *,
    asset_id: str,
    uri: str,
) -> dict:
    format_id = decoded["format_id"]
    policy = FORMAT_POLICIES.get(format_id, {})
    width, height = decoded["dimensions"]
    return {
        "asset_id": asset_id,
        "format_id": format_id,
        "media_type": PROJECT_FORMATS[format_id]["media_type"],
        "uri": uri,
        "width": width,
        "height": height,
        "frame_count": decoded.get("frame_count", 1),
        "content_hash": _hash_bytes(project_bytes),
        "semantic_policy": policy.get("semantic_policy", "sidecar_required"),
    }


def _decoded_project_summary(decoded: dict) -> dict:
    keys = [
        "format_id",
        "model_version",
        "name",
        "is_zip",
        "magic",
        "frame_magic",
        "dimensions",
        "frame_count",
        "layer_count",
        "chunk_count",
        "cel_count",
        "color_depth_bpp",
        "native_mechagotchi_semantics",
    ]
    return {key: decoded[key] for key in keys if key in decoded}


def _compact_import_result(result: dict) -> dict:
    return {
        "ok": result["ok"],
        "asset": result.get("asset"),
        "decoded_project": result.get("decoded_project"),
        "validation": result.get("validation"),
        "project_policy": result.get("project_policy"),
        "semantic_fidelity": result.get("semantic_fidelity", 0.0),
        "errors": result.get("errors", []),
        "error_families": result.get("error_families", []),
    }


def _failed_import(path: str, family: str, message: str) -> dict:
    error = _error(path, family, message)
    return {
        "ok": False,
        "errors": [error],
        "error_families": [family],
    }


def _positive_int(value: object, path: str) -> int:
    if not isinstance(value, int) or value <= 0:
        raise ProjectDecodeError(
            "project_dimension_invalid",
            f"{path} must be a positive integer",
        )
    return value


def _semantic_fidelity(diff: dict, source: dict) -> float:
    source_count = max(1, len(source.get("cells", [])))
    problem_count = (
        len(diff["changed_cells"])
        + len(diff["missing_cells"])
        + len(diff["added_cells"])
    )
    return round(max(0.0, 1.0 - problem_count / source_count), 6)


def _hash_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


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


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def _json_report(report: dict) -> dict:
    payload = deepcopy(report)
    for result in payload["project_results"]:
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
                "project_decoder_success_count",
                "sidecar_restore_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "project_summaries": [
            {
                "profile_id": result["profile_id"],
                "format_id": result["format_id"],
                "asset": result["asset"],
                "decoded_project": result["decoded_project"],
                "semantic_fidelity": result["semantic_fidelity"],
                "project_policy": result["project_policy"],
            }
            for result in json_report["project_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# Third-Party Project Decoder Stage 0\n\n"
        "Project-file boundary decoder proof for Piskel JSON, Pixelorama .pxo, "
        "and Aseprite/LibreSprite header payloads bound to Mechagotchi JSON sidecars.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Project decoder successes: {report['project_decoder_success_count']}\n"
        f"- Sidecar restore successes: {report['sidecar_restore_success_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- Mean semantic fidelity: {metrics['mean_semantic_fidelity']}\n"
        f"- Native metadata writers: {metrics['native_metadata_writer_count']}\n"
        f"- Decision: {report['decision']}\n"
    )


def _error(path: str, family: str, message: str) -> dict:
    return {
        "path": path,
        "family": family,
        "message": message,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/workshop_editor/third_party_project_decoder_stage0"),
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
    report = run_third_party_project_decoder_lab(profile_paths, args.generated_root)
    write_third_party_project_decoder_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_THIRD_PARTY_PROJECT_DECODER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(_json_report(report), indent=2))


if __name__ == "__main__":
    main()
