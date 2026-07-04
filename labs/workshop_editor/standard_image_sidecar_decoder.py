import argparse
import binascii
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

from external_metadata_sidecar import (
    SIDECAR_VERSION,
    build_sidecar_for_grid,
    restore_grid_from_sidecar,
    validate_sidecar_binding,
)
from png_chunk_reader import PNGChunkError, bounded_decompress, read_png_chunks
from workshop_editor import compare_semantic_grid_fidelity


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
REPORT_PATH = ROOT / "data/workshop_editor/standard_image_sidecar_decoder_stage0.json"
DATA_PATH = ROOT / "data/workshop_editor/standard_image_sidecar_decoder_data.js"


class PNGDecodeError(ValueError):
    def __init__(self, family: str, message: str):
        super().__init__(message)
        self.family = family
        self.message = message


def render_grid_rgba_pixels(grid: dict) -> list[tuple[int, int, int, int]]:
    width, height = grid["grid_size"]
    background = _hex_to_rgba(
        grid["palette"]["colors"][grid["palette"].get("background_index", 0)]
    )
    cells_by_coordinate = {
        (cell["x"], cell["y"]): cell for cell in grid.get("cells", [])
    }
    pixels = []
    for y in range(height):
        for x in range(width):
            cell = cells_by_coordinate.get((x, y))
            pixels.append(_hex_to_rgba(cell["visual"]) if cell else background)
    return pixels


def encode_png_rgba(
    width: int,
    height: int,
    pixels: list[tuple[int, int, int, int]],
) -> bytes:
    if width <= 0 or height <= 0:
        raise ValueError("PNG dimensions must be positive")
    if len(pixels) != width * height:
        raise ValueError("pixel count does not match PNG dimensions")

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    scanlines = bytearray()
    for y in range(height):
        scanlines.append(0)
        row = pixels[y * width : (y + 1) * width]
        for pixel in row:
            if len(pixel) != 4 or any(channel < 0 or channel > 255 for channel in pixel):
                raise ValueError("RGBA pixel channels must be in [0, 255]")
            scanlines.extend(pixel)

    return (
        PNG_SIGNATURE
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", zlib.compress(bytes(scanlines)))
        + _png_chunk(b"IEND", b"")
    )


def decode_png_rgba(png_bytes: bytes) -> dict:
    chunks = _read_png_chunks(png_bytes)
    if not chunks or chunks[0]["type"] != "IHDR":
        raise PNGDecodeError("png_ihdr_missing", "PNG IHDR chunk must be first")

    ihdr = chunks[0]["payload"]
    if len(ihdr) != 13:
        raise PNGDecodeError("png_ihdr_invalid", "PNG IHDR chunk length must be 13")
    width, height, bit_depth, color_type, compression, filter_method, interlace = (
        struct.unpack(">IIBBBBB", ihdr)
    )
    if width <= 0 or height <= 0:
        raise PNGDecodeError("png_dimensions_invalid", "PNG dimensions must be positive")
    if bit_depth != 8:
        raise PNGDecodeError("png_bit_depth_unsupported", "only 8-bit PNG is supported")
    if color_type != 6:
        raise PNGDecodeError("png_color_type_unsupported", "only RGBA PNG is supported")
    if compression != 0 or filter_method != 0 or interlace != 0:
        raise PNGDecodeError(
            "png_method_unsupported",
            "only standard compression, filter method 0, and no interlace are supported",
        )

    idat = b"".join(chunk["payload"] for chunk in chunks if chunk["type"] == "IDAT")
    if not idat:
        raise PNGDecodeError("png_idat_missing", "PNG IDAT chunk is required")
    if not any(chunk["type"] == "IEND" for chunk in chunks):
        raise PNGDecodeError("png_iend_missing", "PNG IEND chunk is required")
    stride = width * 4
    expected_length = (stride + 1) * height
    try:
        raw = bounded_decompress(idat, expected_length)
    except PNGChunkError as exc:
        raise PNGDecodeError("png_idat_decompression_failed", exc.message) from exc

    if len(raw) != expected_length:
        raise PNGDecodeError(
            "png_scanline_length_mismatch",
            "decoded scanline length does not match IHDR dimensions",
        )

    pixels = []
    offset = 0
    for _y in range(height):
        filter_type = raw[offset]
        offset += 1
        if filter_type != 0:
            raise PNGDecodeError(
                "png_filter_unsupported",
                "only PNG filter type 0 is supported in Stage 0",
            )
        row = raw[offset : offset + stride]
        offset += stride
        for x in range(width):
            index = x * 4
            pixels.append(tuple(row[index : index + 4]))

    return {
        "width": width,
        "height": height,
        "bit_depth": bit_depth,
        "color_type": color_type,
        "pixels": pixels,
        "chunks": [chunk["type"] for chunk in chunks],
    }


def export_standard_png_with_sidecar(grid: dict, slip_profile: dict) -> dict:
    width, height = grid["grid_size"]
    pixels = render_grid_rgba_pixels(grid)
    png_bytes = encode_png_rgba(width, height, pixels)
    asset = _asset_from_png_bytes(
        png_bytes,
        asset_id=f"{grid['grid_id']}.png",
        uri=f"generated://workshop/standard-image/{grid['grid_id']}.png",
    )
    sidecar = build_sidecar_for_grid(grid, slip_profile, asset)
    sidecar["sidecar_id"] = f"{grid['grid_id']}_standard_image_sidecar"
    sidecar["limitations"] = [
        "Stage 0 decoder supports static non-interlaced 8-bit RGBA PNG only.",
        "Semantic metadata is restored from the Mechagotchi sidecar, not inferred from pixels.",
    ]
    return {
        "png_bytes": png_bytes,
        "asset": asset,
        "sidecar": sidecar,
        "encoded_pixel_count": len(pixels),
    }


def import_standard_png_with_sidecar(png_bytes: bytes, sidecar: dict) -> dict:
    try:
        decoded = decode_png_rgba(png_bytes)
    except PNGDecodeError as exc:
        return _failed_import("png", exc.family, exc.message)

    binding = sidecar.get("asset_binding", {})
    asset = _asset_from_png_bytes(
        png_bytes,
        asset_id=binding.get("asset_id", "unknown.png"),
        uri=binding.get("uri", "unknown://png"),
    )
    validation = validate_sidecar_binding(sidecar, asset)
    if not validation["ok"]:
        return {
            "ok": False,
            "asset": asset,
            "decoded_png": _decoded_summary(decoded),
            "validation": validation,
            "errors": validation["errors"],
            "error_families": validation["error_families"],
        }

    restored = restore_grid_from_sidecar(sidecar, asset)
    expected_pixels = render_grid_rgba_pixels(restored)
    if decoded["pixels"] != expected_pixels:
        error = _error(
            "png.pixels",
            "png_sidecar_pixel_mismatch",
            "decoded pixels do not match the sidecar semantic overlay",
        )
        return {
            "ok": False,
            "asset": asset,
            "decoded_png": _decoded_summary(decoded),
            "validation": validation,
            "errors": [error],
            "error_families": [error["family"]],
        }

    source_grid = restore_grid_from_sidecar(sidecar, asset, validate=False)
    diff = compare_semantic_grid_fidelity(source_grid, restored)
    fidelity = _semantic_fidelity(diff, source_grid)
    return {
        "ok": True,
        "asset": asset,
        "decoded_png": _decoded_summary(decoded),
        "validation": validation,
        "restored_grid": restored,
        "semantic_diff": diff,
        "semantic_fidelity": fidelity,
        "pixel_fidelity": 1.0,
        "errors": [],
        "error_families": [],
    }


def run_standard_image_sidecar_decoder_lab(
    profile_paths: list[Path], generated_root: Path
) -> dict:
    png_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        exported = export_standard_png_with_sidecar(grid, profile)
        imported = import_standard_png_with_sidecar(
            exported["png_bytes"],
            exported["sidecar"],
        )
        restored = imported.get("restored_grid", {})
        grid_validation = validate_grid(restored) if restored else None
        alignment = is_grid_aligned(restored, profile) if restored else None
        png_results.append(
            {
                "profile_id": profile["profile_id"],
                "profile_path": _portable(profile_path),
                "grid_path": _portable(grid_path),
                "png_file_name": f"{profile['profile_id']}_standard_image.png",
                "sidecar_file_name": f"{profile['profile_id']}_standard_image_sidecar.json",
                "png_bytes_hex": exported["png_bytes"].hex(),
                "png_byte_count": len(exported["png_bytes"]),
                "asset": exported["asset"],
                "sidecar": exported["sidecar"],
                "decoded_png": imported.get("decoded_png"),
                "import_result": _compact_import_result(imported),
                "restored_grid_validation": {
                    "valid": bool(grid_validation and grid_validation.ok),
                    "errors": grid_validation.errors if grid_validation else [],
                    "slip_aligned": bool(alignment and alignment.ok),
                    "slip_errors": alignment.errors if alignment else [],
                },
                "semantic_diff": imported.get("semantic_diff", {}),
                "semantic_fidelity": imported.get("semantic_fidelity", 0.0),
                "pixel_fidelity": imported.get("pixel_fidelity", 0.0),
            }
        )

    invalid_probe_results = _invalid_probe_results(png_results[0])
    success_count = sum(
        1
        for result in png_results
        if result["import_result"]["ok"]
        and result["restored_grid_validation"]["valid"]
        and result["restored_grid_validation"]["slip_aligned"]
        and result["semantic_fidelity"] == 1.0
        and result["pixel_fidelity"] == 1.0
    )
    invalid_rejected_count = sum(
        1 for result in invalid_probe_results if not result["ok"]
    )
    mean_fidelity = round(
        sum(result["semantic_fidelity"] for result in png_results)
        / max(1, len(png_results)),
        6,
    )
    return {
        "artifact_id": "standard_image_sidecar_decoder_stage0",
        "status": "research_standard_image_sidecar_decoder_no_package_code",
        "date": "2026-05-12",
        "purpose": (
            "Prove a real static RGBA PNG import/export path can bind standard "
            "image pixels to a Mechagotchi sidecar and restore semantic grids "
            "without inferring organ metadata from pixels."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
            "labs/workshop_editor/external_metadata_sidecar.py",
            "labs/workshop_editor/standard_image_sidecar_decoder.py",
        ],
        "external_anchors": [
            {
                "source": "W3C PNG specification",
                "url": "https://www.w3.org/TR/png-3/",
                "used_for": "PNG signature, chunk, CRC, zlib IDAT, and filter constraints for the Stage 0 static RGBA decoder.",
            }
        ],
        "profile_count": len(png_results),
        "png_roundtrip_success_count": success_count,
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "metrics": {
            "png_roundtrip_success_rate": _ratio(success_count, len(png_results)),
            "mean_semantic_fidelity": mean_fidelity,
            "mean_pixel_fidelity": round(
                sum(result["pixel_fidelity"] for result in png_results)
                / max(1, len(png_results)),
                6,
            ),
            "invalid_probe_rejection_rate": _ratio(
                invalid_rejected_count,
                len(invalid_probe_results),
            ),
        },
        "png_results": png_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "standard_image_static_rgba_png_decoder",
            "standard_image_sidecar_export",
            "standard_image_sidecar_import",
            "png_signature_crc_and_idat_validation",
            "png_sidecar_semantic_restore",
        ],
        "blocked_states": [
            "png_adam7_interlace_decoder",
            "apng_decoder",
            "full_png_conformance",
            "spritesheet_packed_rotation_trim_decoder",
            "runtime_animation_playback",
            "full_project_format_coverage",
            "embedded_png_metadata_writer",
            "project_file_native_metadata_writer",
            "profile_weighted_evolution",
        ],
        "decision": "prototype_static_rgba_png_sidecar_decoder",
        "next_research_step": (
            "Run held-out long-horizon behavior tests and manual readability "
            "calibration before profile-weighted evolution claims."
        ),
    }


def write_standard_image_sidecar_decoder_artifacts(
    output_dir: Path, report: dict
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "standard_image_sidecar_decoder_stage0.json", _json_report(report))
    for result in report["png_results"]:
        (output_dir / result["png_file_name"]).write_bytes(
            bytes.fromhex(result["png_bytes_hex"])
        )
        _write_json(output_dir / result["sidecar_file_name"], result["sidecar"])
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "standard_image_sidecar_decoder_data.js").write_text(
        "window.MECHAGOTCHI_STANDARD_IMAGE_SIDECAR_DECODER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _read_png_chunks(png_bytes: bytes) -> list[dict]:
    try:
        return read_png_chunks(png_bytes)
    except PNGChunkError as exc:
        raise PNGDecodeError(exc.family, exc.message) from exc


def _png_chunk(chunk_type: bytes, payload: bytes) -> bytes:
    crc = binascii.crc32(payload, binascii.crc32(chunk_type)) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + chunk_type + payload + struct.pack(">I", crc)


def _asset_from_png_bytes(png_bytes: bytes, *, asset_id: str, uri: str) -> dict:
    decoded = decode_png_rgba(png_bytes)
    return {
        "asset_id": asset_id,
        "format_id": "png",
        "media_type": "image/png",
        "uri": uri,
        "width": decoded["width"],
        "height": decoded["height"],
        "frame_count": 1,
        "content_hash": _hash_bytes(png_bytes),
        "semantic_policy": "sidecar_required",
    }


def _invalid_probe_results(reference_result: dict) -> list[dict]:
    png_bytes = bytes.fromhex(reference_result["png_bytes_hex"])
    sidecar = reference_result["sidecar"]
    corrupt_png = b"not-a-png" + png_bytes[len(PNG_SIGNATURE) :]
    wrong_hash_sidecar = deepcopy(sidecar)
    wrong_hash_sidecar["asset_binding"]["content_hash"] = "sha256:not-the-png"
    return [
        _compact_import_result(import_standard_png_with_sidecar(corrupt_png, sidecar)),
        _compact_import_result(import_standard_png_with_sidecar(png_bytes, wrong_hash_sidecar)),
    ]


def _compact_import_result(result: dict) -> dict:
    return {
        "ok": result["ok"],
        "asset": result.get("asset"),
        "decoded_png": result.get("decoded_png"),
        "validation": result.get("validation"),
        "semantic_fidelity": result.get("semantic_fidelity", 0.0),
        "pixel_fidelity": result.get("pixel_fidelity", 0.0),
        "errors": result.get("errors", []),
        "error_families": result.get("error_families", []),
    }


def _decoded_summary(decoded: dict) -> dict:
    return {
        "width": decoded["width"],
        "height": decoded["height"],
        "bit_depth": decoded["bit_depth"],
        "color_type": decoded["color_type"],
        "pixel_count": len(decoded["pixels"]),
        "chunks": decoded["chunks"],
    }


def _hex_to_rgba(value: str) -> tuple[int, int, int, int]:
    if not isinstance(value, str) or len(value) != 7 or not value.startswith("#"):
        raise ValueError(f"expected #RRGGBB color, got {value!r}")
    return (
        int(value[1:3], 16),
        int(value[3:5], 16),
        int(value[5:7], 16),
        255,
    )


def _first_grid_path(profile: dict, generated_root: Path) -> Path:
    grid_paths = sorted((generated_root / profile["profile_id"]).glob("*.json"))
    if not grid_paths:
        raise ValueError(f"no generated grids found for profile: {profile['profile_id']}")
    return grid_paths[0]


def _semantic_fidelity(diff: dict, source: dict) -> float:
    source_count = max(1, len(source.get("cells", [])))
    problem_count = (
        len(diff["changed_cells"])
        + len(diff["missing_cells"])
        + len(diff["added_cells"])
    )
    return round(max(0.0, 1.0 - problem_count / source_count), 6)


def _failed_import(path: str, family: str, message: str) -> dict:
    error = _error(path, family, message)
    return {
        "ok": False,
        "errors": [error],
        "error_families": [family],
    }


def _error(path: str, family: str, message: str) -> dict:
    return {
        "path": path,
        "family": family,
        "message": message,
    }


def _hash_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _portable(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def _json_report(report: dict) -> dict:
    payload = deepcopy(report)
    for result in payload["png_results"]:
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
                "png_roundtrip_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "png_summaries": [
            {
                "profile_id": result["profile_id"],
                "asset": result["asset"],
                "decoded_png": result["decoded_png"],
                "semantic_fidelity": result["semantic_fidelity"],
                "pixel_fidelity": result["pixel_fidelity"],
            }
            for result in json_report["png_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# Standard Image Sidecar Decoder Stage 0\n\n"
        "Static 8-bit RGBA PNG import/export proof bound to Mechagotchi JSON "
        "sidecars.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- PNG round-trip successes: {report['png_roundtrip_success_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- Mean semantic fidelity: {metrics['mean_semantic_fidelity']}\n"
        f"- Mean pixel fidelity: {metrics['mean_pixel_fidelity']}\n"
        f"- Decision: {report['decision']}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "data/workshop_editor/standard_image_sidecar_decoder_stage0",
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
    report = run_standard_image_sidecar_decoder_lab(profile_paths, args.generated_root)
    write_standard_image_sidecar_decoder_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_STANDARD_IMAGE_SIDECAR_DECODER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(_json_report(report), indent=2))


if __name__ == "__main__":
    main()
