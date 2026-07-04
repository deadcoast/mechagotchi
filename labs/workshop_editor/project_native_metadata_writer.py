import argparse
import hashlib
import io
import json
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

from external_metadata_sidecar import build_sidecar_for_grid, restore_grid_from_sidecar
from third_party_project_decoder import (
    PROJECT_FORMATS,
    PXO_MEMBER_SIZE_CAP,
    ProjectDecodeError,
    decode_project_payload,
    export_project_with_sidecar,
)
from workshop_editor import compare_semantic_grid_fidelity


REPORT_PATH = ROOT / "data/workshop_editor/project_native_metadata_writer_stage0.json"
DATA_PATH = ROOT / "data/workshop_editor/project_native_metadata_writer_data.js"

NATIVE_METADATA_VERSION = "mechagotchi.project_native_metadata.v1"
NATIVE_METADATA_KEY = "mechagotchi_native_metadata"
PISKEL_DESCRIPTION_PREFIX = "MECHAGOTCHI_NATIVE_METADATA_V1:"
SUPPORTED_NATIVE_METADATA_FORMATS = {
    "piskel_project": {
        "native_location": "piskel.description",
        "writer_policy": "description_field_json_envelope",
        "artifact_slug": "piskel",
    },
    "pixelorama_pxo": {
        "native_location": "data.json.mechagotchi_native_metadata",
        "writer_policy": "data_json_namespaced_metadata_object",
        "artifact_slug": "pixelorama",
    },
}
UNSUPPORTED_NATIVE_METADATA_FORMATS = {
    "libresprite_project": {
        "format_id": "libresprite_project",
        "native_writer_supported": False,
        "delegated_state": "aseprite_libresprite_user_data_chunk_writer",
        "reason": (
            "Aseprite/LibreSprite User Data Chunk writing is handled by "
            "labs/workshop_editor/aseprite_user_data_chunk_writer.py; this "
            "generic native metadata writer remains scoped to JSON-friendly "
            "Piskel and Pixelorama project containers."
        ),
        "external_anchor": "Aseprite file-format User Data Chunk 0x2020",
    }
}
_FIXED_ZIP_DATE = (2026, 1, 1, 0, 0, 0)


class ProjectNativeMetadataError(ValueError):
    def __init__(self, family: str, message: str):
        super().__init__(message)
        self.family = family
        self.message = message


def write_project_native_metadata(
    project_bytes: bytes,
    format_id: str,
    sidecar: dict,
) -> dict:
    _ensure_supported_format(format_id)
    decode_project_payload(project_bytes, format_id)

    stripped = remove_project_native_metadata(project_bytes, format_id)
    metadata = _build_native_metadata(
        format_id,
        sidecar,
        stripped["content_hash"],
        stripped["project_bytes"],
    )
    embedded_bytes = _embed_project_native_metadata(project_bytes, format_id, metadata)

    normalized = remove_project_native_metadata(embedded_bytes, format_id)
    if normalized["content_hash"] != metadata["canonical_project_hash"]:
        metadata = _build_native_metadata(
            format_id,
            sidecar,
            normalized["content_hash"],
            normalized["project_bytes"],
        )
        embedded_bytes = _embed_project_native_metadata(project_bytes, format_id, metadata)
        normalized = remove_project_native_metadata(embedded_bytes, format_id)

    if normalized["content_hash"] != metadata["canonical_project_hash"]:
        raise ProjectNativeMetadataError(
            "project_native_canonical_hash_unstable",
            "native metadata canonical project hash is not stable after embedding",
        )

    return {
        "project_bytes": embedded_bytes,
        "format_id": format_id,
        "metadata": metadata,
        "decoded_project": decode_project_payload(embedded_bytes, format_id),
        "embedded_project_hash": _hash_bytes(embedded_bytes),
        "canonical_project_hash": normalized["content_hash"],
        "canonical_project_byte_count": len(normalized["project_bytes"]),
    }


def extract_project_native_metadata(
    project_bytes: bytes,
    format_id: str,
    *,
    allow_rewrite: bool = False,
) -> dict:
    _ensure_supported_format(format_id)
    metadata = _extract_project_native_metadata(project_bytes, format_id)
    if metadata.get("metadata_version") != NATIVE_METADATA_VERSION:
        raise ProjectNativeMetadataError(
            "project_native_metadata_version_unsupported",
            "unsupported project native metadata version",
        )
    if metadata.get("format_id") != format_id:
        raise ProjectNativeMetadataError(
            "project_native_metadata_format_mismatch",
            "native metadata format id does not match the project format",
        )
    sidecar = metadata.get("sidecar")
    if not isinstance(sidecar, dict):
        raise ProjectNativeMetadataError(
            "project_native_sidecar_missing",
            "native metadata must contain a sidecar object",
        )
    if _hash_payload(sidecar) != metadata.get("sidecar_hash"):
        raise ProjectNativeMetadataError(
            "project_native_sidecar_hash_mismatch",
            "native metadata sidecar hash does not match the embedded sidecar",
        )

    visual_hash = project_visual_hash(project_bytes, format_id)
    if metadata.get("project_visual_hash") != visual_hash:
        raise ProjectNativeMetadataError(
            "project_native_visual_hash_mismatch",
            "native metadata project visual hash does not match the current project carrier",
        )

    stripped = remove_project_native_metadata(project_bytes, format_id)
    canonical_hash_matches = stripped["content_hash"] == metadata.get("canonical_project_hash")
    if not canonical_hash_matches and not allow_rewrite:
        raise ProjectNativeMetadataError(
            "project_native_canonical_hash_mismatch",
            "native metadata canonical project hash does not match the stripped project",
        )
    if sidecar.get("asset_binding", {}).get("content_hash") != metadata.get("canonical_project_hash"):
        raise ProjectNativeMetadataError(
            "project_native_sidecar_asset_hash_mismatch",
            "native metadata sidecar asset hash does not match the metadata canonical project hash",
        )

    decoded = decode_project_payload(project_bytes, format_id)
    return {
        "ok": True,
        "format_id": format_id,
        "metadata": metadata,
        "sidecar": sidecar,
        "decoded_project": _decoded_project_summary(decoded),
        "canonical_project": stripped,
        "current_canonical_project_hash": stripped["content_hash"],
        "rewrite_detected": not canonical_hash_matches,
        "embedded_project_hash": _hash_bytes(project_bytes),
    }


def remove_project_native_metadata(project_bytes: bytes, format_id: str) -> dict:
    _ensure_supported_format(format_id)
    if format_id == "piskel_project":
        stripped_bytes = _strip_piskel_native_metadata(project_bytes)
    elif format_id == "pixelorama_pxo":
        stripped_bytes = _strip_pixelorama_native_metadata(project_bytes)
    else:
        raise AssertionError(f"unreachable unsupported format: {format_id}")
    return {
        "project_bytes": stripped_bytes,
        "format_id": format_id,
        "content_hash": _hash_bytes(stripped_bytes),
        "byte_count": len(stripped_bytes),
    }


def project_visual_hash(project_bytes: bytes, format_id: str) -> str:
    _ensure_supported_format(format_id)
    if format_id == "piskel_project":
        payload = _read_piskel_payload(project_bytes)
        piskel = payload["piskel"]
        layers = []
        for layer_string in piskel.get("layers", []):
            layer = json.loads(layer_string)
            chunks = []
            for chunk in layer.get("chunks", []):
                chunks.append(
                    {
                        "layout": chunk.get("layout"),
                        "base64_png_hash": _hash_text(chunk.get("base64PNG", "")),
                    }
                )
            layers.append(
                {
                    "opacity": layer.get("opacity"),
                    "frameCount": layer.get("frameCount"),
                    "chunks": chunks,
                }
            )
        return _hash_payload(
            {
                "format_id": format_id,
                "width": piskel.get("width"),
                "height": piskel.get("height"),
                "fps": piskel.get("fps"),
                "hiddenFrames": piskel.get("hiddenFrames", []),
                "layers": layers,
            }
        )
    data, members = _read_pixelorama_archive(project_bytes)
    image_members = {
        name: _hash_bytes(payload)
        for name, payload in members.items()
        if name.startswith("image_data/")
    }
    return _hash_payload(
        {
            "format_id": format_id,
            "size": data.get("size"),
            "fps": data.get("fps"),
            "frames": data.get("frames"),
            "layers": data.get("layers"),
            "cels": data.get("cels"),
            "image_members": image_members,
        }
    )


def rebind_sidecar_to_project_hash(sidecar: dict, project_hash: str) -> dict:
    return _sidecar_bound_to_project_hash(sidecar, project_hash)


def import_project_with_native_metadata(
    project_bytes: bytes,
    format_id: str,
    source_grid: dict | None = None,
) -> dict:
    try:
        extracted = extract_project_native_metadata(project_bytes, format_id)
    except (ProjectNativeMetadataError, ProjectDecodeError) as exc:
        family = getattr(exc, "family", "project_native_metadata_invalid")
        message = getattr(exc, "message", str(exc))
        return _failed_import("project_native_metadata", family, message)

    sidecar = extracted["sidecar"]
    asset = deepcopy(sidecar["asset_binding"])
    try:
        restored = restore_grid_from_sidecar(sidecar, asset)
    except ValueError as exc:
        return _failed_import("sidecar", "project_native_sidecar_invalid", str(exc))

    profile = sidecar["slip_binding"]["profile_snapshot"]
    grid_validation = validate_grid(restored)
    alignment = is_grid_aligned(restored, profile)
    semantic_source = source_grid or restore_grid_from_sidecar(sidecar, asset, validate=False)
    diff = compare_semantic_grid_fidelity(semantic_source, restored)
    fidelity = _semantic_fidelity(diff, semantic_source)
    ok = grid_validation.ok and alignment.ok and fidelity == 1.0
    errors = []
    if not grid_validation.ok:
        errors.extend(_error("$", "restored_grid_invalid", message) for message in grid_validation.errors)
    if not alignment.ok:
        errors.extend(_error("$", "restored_grid_not_slip_aligned", message) for message in alignment.errors)
    return {
        "ok": ok,
        "format_id": format_id,
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
                "project_visual_hash",
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
            "semantic_policy": "project_native_metadata",
            "native_mechagotchi_semantics": True,
            "native_location": extracted["metadata"]["native_location"],
            "live_external_editor_rewrite_validation_verified": False,
        },
        "semantic_diff": diff,
        "semantic_fidelity": fidelity,
        "errors": errors,
        "error_families": sorted({error["family"] for error in errors}),
    }


def run_project_native_metadata_writer_lab(
    profile_paths: list[Path],
    generated_root: Path,
) -> dict:
    native_results = []
    native_formats = ["piskel_project", "pixelorama_pxo"]
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        for format_id in native_formats:
            exported = export_project_with_sidecar(grid, profile, format_id)
            embedded = write_project_native_metadata(
                exported["project_bytes"],
                format_id,
                exported["sidecar"],
            )
            imported = import_project_with_native_metadata(
                embedded["project_bytes"],
                format_id,
                source_grid=grid,
            )
            slug = SUPPORTED_NATIVE_METADATA_FORMATS[format_id]["artifact_slug"]
            extension = PROJECT_FORMATS[format_id]["extension"]
            native_results.append(
                {
                    "profile_id": profile["profile_id"],
                    "profile_path": _portable(profile_path),
                    "grid_path": _portable(grid_path),
                    "format_id": format_id,
                    "native_location": embedded["metadata"]["native_location"],
                    "writer_policy": embedded["metadata"]["writer_policy"],
                    "project_file_name": f"{profile['profile_id']}_native_metadata{extension}",
                    "sidecar_file_name": f"{profile['profile_id']}_{slug}_native_sidecar.json",
                    "project_bytes_hex": embedded["project_bytes"].hex(),
                    "project_byte_count": len(embedded["project_bytes"]),
                    "embedded_project_hash": embedded["embedded_project_hash"],
                    "canonical_project_hash": embedded["canonical_project_hash"],
                    "canonical_project_byte_count": embedded["canonical_project_byte_count"],
                    "metadata": _metadata_summary(embedded["metadata"]),
                    "native_sidecar": embedded["metadata"]["sidecar"],
                    "decoded_project": _decoded_project_summary(embedded["decoded_project"]),
                    "import_result": _compact_import_result(imported),
                    "restored_grid_validation": imported.get("restored_grid_validation", {}),
                    "semantic_diff": imported.get("semantic_diff", {}),
                    "semantic_fidelity": imported.get("semantic_fidelity", 0.0),
                }
            )

    invalid_probe_results = _invalid_probe_results(native_results[0])
    success_count = sum(
        1
        for result in native_results
        if result["import_result"]["ok"]
        and result["restored_grid_validation"].get("valid")
        and result["restored_grid_validation"].get("slip_aligned")
        and result["semantic_fidelity"] == 1.0
    )
    invalid_rejected_count = sum(1 for result in invalid_probe_results if not result["ok"])
    return {
        "artifact_id": "project_native_metadata_writer_stage0",
        "status": "research_project_native_metadata_writer_no_package_code",
        "date": "2026-05-13",
        "purpose": (
            "Prove a Stage 0 native project-file metadata writer policy for "
            "JSON-friendly project containers without claiming live external "
            "editor rewrite validation or generic full project-format coverage."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
            "labs/workshop_editor/third_party_project_decoder.py",
            "labs/workshop_editor/project_native_metadata_writer.py",
        ],
        "external_anchors": [
            {
                "source": "Piskel Serializer.js",
                "url": "https://github.com/piskelapp/piskel/blob/master/src/js/utils/serialization/Serializer.js",
                "used_for": "Piskel serializes descriptor description into the project JSON envelope.",
            },
            {
                "source": "Piskel Deserializer.js",
                "url": "https://github.com/piskelapp/piskel/blob/master/src/js/utils/serialization/Deserializer.js",
                "used_for": "Piskel reads the project description back into the descriptor.",
            },
            {
                "source": "Pixelorama project documentation",
                "url": "https://pixelorama.org/concepts/project/",
                "used_for": "Pixelorama .pxo stores project metadata in data.json inside a zip container.",
            },
            {
                "source": "Aseprite file-format specification",
                "url": "https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md",
                "used_for": "Aseprite User Data Chunk 0x2020 is delegated to the dedicated Stage 0 User Data chunk writer lab.",
            },
        ],
        "profile_count": len(profile_paths),
        "native_writer_format_count": len(native_formats),
        "native_metadata_roundtrip_count": len(native_results),
        "native_metadata_roundtrip_success_count": success_count,
        "unsupported_native_writer_policy_count": len(UNSUPPORTED_NATIVE_METADATA_FORMATS),
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "metrics": {
            "native_metadata_roundtrip_success_rate": _ratio(success_count, len(native_results)),
            "mean_semantic_fidelity": round(
                sum(result["semantic_fidelity"] for result in native_results)
                / max(1, len(native_results)),
                6,
            ),
            "invalid_probe_rejection_rate": _ratio(
                invalid_rejected_count,
                len(invalid_probe_results),
            ),
            "live_external_editor_rewrite_validation_verified": False,
        },
        "native_results": native_results,
        "unsupported_native_writer_policies": list(UNSUPPORTED_NATIVE_METADATA_FORMATS.values()),
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "project_file_native_metadata_writer_policy",
            "piskel_description_native_metadata_writer",
            "pixelorama_data_json_native_metadata_writer",
            "project_native_metadata_sidecar_semantic_restore",
            "project_native_metadata_hash_validation",
        ],
        "blocked_states": [
            "full_project_format_coverage",
            "live_external_editor_rewrite_validation",
            "advanced_tags_layers_timeline_schema_coverage",
            "package_runtime_lifecycle_integration",
            "manual_readability_calibration",
            "profile_weighted_evolution",
            "community_profile_packs",
        ],
        "decision": "prototype_project_native_metadata_writer_subset",
        "next_research_step": (
            "Keep live external editor rewrite validation, advanced tags/layers "
            "timeline schema coverage, and full project-format coverage blocked "
            "until direct editor and broader native project chunk/schema tests exist."
        ),
    }


def write_project_native_metadata_writer_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "project_native_metadata_writer_stage0.json", _json_report(report))
    for result in report["native_results"]:
        (output_dir / result["project_file_name"]).write_bytes(
            bytes.fromhex(result["project_bytes_hex"])
        )
        _write_json(output_dir / result["sidecar_file_name"], result["native_sidecar"])
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "project_native_metadata_writer_data.js").write_text(
        "window.MECHAGOTCHI_PROJECT_NATIVE_METADATA_WRITER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _build_native_metadata(
    format_id: str,
    sidecar: dict,
    canonical_hash: str,
    canonical_project_bytes: bytes,
) -> dict:
    native_sidecar = _sidecar_bound_to_project_hash(sidecar, canonical_hash)
    policy = SUPPORTED_NATIVE_METADATA_FORMATS[format_id]
    return {
        "metadata_version": NATIVE_METADATA_VERSION,
        "format_id": format_id,
        "native_location": policy["native_location"],
        "writer_policy": policy["writer_policy"],
        "canonical_project_hash": canonical_hash,
        "project_visual_hash": project_visual_hash(canonical_project_bytes, format_id),
        "sidecar_hash": _hash_payload(native_sidecar),
        "sidecar": native_sidecar,
    }


def _sidecar_bound_to_project_hash(sidecar: dict, project_hash: str) -> dict:
    source_asset = deepcopy(sidecar["asset_binding"])
    source_grid = restore_grid_from_sidecar(sidecar, source_asset, validate=False)
    asset = deepcopy(source_asset)
    asset["content_hash"] = project_hash
    asset["semantic_policy"] = "project_native_metadata"
    rebuilt = build_sidecar_for_grid(
        source_grid,
        sidecar["slip_binding"]["profile_snapshot"],
        asset,
    )
    rebuilt["sidecar_id"] = sidecar.get("sidecar_id", rebuilt["sidecar_id"]).replace(
        "_project_sidecar",
        "_native_project_sidecar",
    )
    rebuilt["asset_binding"]["semantic_policy"] = "project_native_metadata"
    rebuilt["project_binding"] = deepcopy(sidecar.get("project_binding", {}))
    rebuilt["project_binding"].update(
        {
            "native_mechagotchi_semantics": True,
            "semantic_policy": "project_native_metadata",
            "native_metadata_version": NATIVE_METADATA_VERSION,
        }
    )
    rebuilt["limitations"] = [
        "Stage 0 native metadata writer covers Piskel description and Pixelorama data.json only.",
        "Live external editor rewrite validation is not verified by this lab.",
        "Aseprite/LibreSprite User Data chunks are covered by the separate Stage 0 User Data chunk writer lab.",
    ]
    return rebuilt


def _embed_project_native_metadata(
    project_bytes: bytes,
    format_id: str,
    metadata: dict,
) -> bytes:
    if format_id == "piskel_project":
        return _embed_piskel_native_metadata(project_bytes, metadata)
    if format_id == "pixelorama_pxo":
        return _embed_pixelorama_native_metadata(project_bytes, metadata)
    raise AssertionError(f"unreachable unsupported format: {format_id}")


def _extract_project_native_metadata(project_bytes: bytes, format_id: str) -> dict:
    if format_id == "piskel_project":
        return _extract_piskel_native_metadata(project_bytes)
    if format_id == "pixelorama_pxo":
        return _extract_pixelorama_native_metadata(project_bytes)
    raise AssertionError(f"unreachable unsupported format: {format_id}")


def _embed_piskel_native_metadata(project_bytes: bytes, metadata: dict) -> bytes:
    payload = _read_piskel_payload(project_bytes)
    piskel = payload["piskel"]
    description = piskel.get("description", "")
    if isinstance(description, str) and description.startswith(PISKEL_DESCRIPTION_PREFIX):
        try:
            existing = json.loads(description[len(PISKEL_DESCRIPTION_PREFIX) :])
            description = existing.get("editor_description_before_metadata", "")
        except json.JSONDecodeError:
            description = ""
    embedded_metadata = deepcopy(metadata)
    embedded_metadata["editor_description_before_metadata"] = description
    piskel["description"] = (
        PISKEL_DESCRIPTION_PREFIX
        + json.dumps(embedded_metadata, sort_keys=True, separators=(",", ":"))
    )
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _extract_piskel_native_metadata(project_bytes: bytes) -> dict:
    payload = _read_piskel_payload(project_bytes)
    description = payload["piskel"].get("description", "")
    if not isinstance(description, str) or not description.startswith(PISKEL_DESCRIPTION_PREFIX):
        raise ProjectNativeMetadataError(
            "project_native_metadata_missing",
            "Piskel project description does not contain Mechagotchi native metadata",
        )
    try:
        return json.loads(description[len(PISKEL_DESCRIPTION_PREFIX) :])
    except json.JSONDecodeError as exc:
        raise ProjectNativeMetadataError(
            "project_native_metadata_json_invalid",
            str(exc),
        ) from exc


def _strip_piskel_native_metadata(project_bytes: bytes) -> bytes:
    payload = _read_piskel_payload(project_bytes)
    description = payload["piskel"].get("description", "")
    if isinstance(description, str) and description.startswith(PISKEL_DESCRIPTION_PREFIX):
        try:
            metadata = json.loads(description[len(PISKEL_DESCRIPTION_PREFIX) :])
            payload["piskel"]["description"] = metadata.get(
                "editor_description_before_metadata",
                "",
            )
        except json.JSONDecodeError:
            payload["piskel"]["description"] = ""
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _read_piskel_payload(project_bytes: bytes) -> dict:
    try:
        payload = json.loads(project_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProjectNativeMetadataError("project_json_invalid", str(exc)) from exc
    if not isinstance(payload.get("piskel"), dict):
        raise ProjectNativeMetadataError("piskel_payload_missing", "piskel object is required")
    return payload


def _embed_pixelorama_native_metadata(project_bytes: bytes, metadata: dict) -> bytes:
    data, members = _read_pixelorama_archive(project_bytes)
    data[NATIVE_METADATA_KEY] = deepcopy(metadata)
    return _write_pixelorama_archive(data, members)


def _extract_pixelorama_native_metadata(project_bytes: bytes) -> dict:
    data, _members = _read_pixelorama_archive(project_bytes)
    metadata = data.get(NATIVE_METADATA_KEY)
    if not isinstance(metadata, dict):
        raise ProjectNativeMetadataError(
            "project_native_metadata_missing",
            "Pixelorama data.json does not contain Mechagotchi native metadata",
        )
    return metadata


def _strip_pixelorama_native_metadata(project_bytes: bytes) -> bytes:
    data, members = _read_pixelorama_archive(project_bytes)
    data.pop(NATIVE_METADATA_KEY, None)
    return _write_pixelorama_archive(data, members)


def _read_pxo_member(archive: zipfile.ZipFile, name: str) -> bytes:
    try:
        info = archive.getinfo(name)
    except KeyError as exc:
        raise ProjectNativeMetadataError(
            "pxo_member_missing",
            f".pxo member is missing from the archive: {name}",
        ) from exc
    if info.file_size > PXO_MEMBER_SIZE_CAP:
        raise ProjectNativeMetadataError(
            "pxo_member_too_large",
            f".pxo member exceeds the {PXO_MEMBER_SIZE_CAP} byte cap: {name}",
        )
    return archive.read(name)


def _read_pixelorama_archive(project_bytes: bytes) -> tuple[dict, dict[str, bytes]]:
    if not zipfile.is_zipfile(io.BytesIO(project_bytes)):
        raise ProjectNativeMetadataError("pxo_zip_invalid", "Pixelorama .pxo must be a zip container")
    try:
        with zipfile.ZipFile(io.BytesIO(project_bytes), "r") as archive:
            members = {
                name: _read_pxo_member(archive, name)
                for name in sorted(archive.namelist())
                if name != "data.json"
            }
            if "data.json" not in archive.namelist():
                raise ProjectNativeMetadataError("pxo_data_json_missing", "data.json is required")
            try:
                data = json.loads(_read_pxo_member(archive, "data.json").decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ProjectNativeMetadataError("pxo_data_json_invalid", str(exc)) from exc
    except zipfile.BadZipFile as exc:
        raise ProjectNativeMetadataError("pxo_zip_invalid", str(exc)) from exc
    return data, members


def _write_pixelorama_archive(data: dict, members: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        _writestr_stable(
            archive,
            "data.json",
            (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        )
        for name in sorted(members):
            _writestr_stable(archive, name, members[name])
    return buffer.getvalue()


def _writestr_stable(archive: zipfile.ZipFile, name: str, payload: bytes) -> None:
    info = zipfile.ZipInfo(name, _FIXED_ZIP_DATE)
    info.compress_type = zipfile.ZIP_DEFLATED
    archive.writestr(info, payload)


def _invalid_probe_results(reference_result: dict) -> list[dict]:
    project_bytes = bytes.fromhex(reference_result["project_bytes_hex"])
    format_id = reference_result["format_id"]
    stripped = remove_project_native_metadata(project_bytes, format_id)
    sidecar_tampered_metadata = deepcopy(_extract_project_native_metadata(project_bytes, format_id))
    sidecar_tampered_metadata["sidecar"]["asset_binding"]["content_hash"] = "sha256:tampered"
    sidecar_tampered = _embed_project_native_metadata(
        stripped["project_bytes"],
        format_id,
        sidecar_tampered_metadata,
    )
    project_tampered = _tamper_project_name(project_bytes, format_id)
    unsupported = {
        "ok": False,
        "errors": [
            _error(
                "format_id",
                "project_native_metadata_unsupported_format",
                "libresprite_project native writing is delegated to the Aseprite User Data chunk writer lab",
            )
        ],
        "error_families": ["project_native_metadata_unsupported_format"],
    }
    return [
        _compact_import_result(import_project_with_native_metadata(stripped["project_bytes"], format_id)),
        _compact_import_result(import_project_with_native_metadata(sidecar_tampered, format_id)),
        _compact_import_result(import_project_with_native_metadata(project_tampered, format_id)),
        unsupported,
    ]


def _tamper_project_name(project_bytes: bytes, format_id: str) -> bytes:
    if format_id == "piskel_project":
        payload = _read_piskel_payload(project_bytes)
        payload["piskel"]["name"] = "edited-after-native-metadata"
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    data, members = _read_pixelorama_archive(project_bytes)
    data["name"] = "edited-after-native-metadata"
    return _write_pixelorama_archive(data, members)


def _metadata_summary(metadata: dict) -> dict:
    return {
        key: metadata[key]
        for key in [
            "metadata_version",
            "format_id",
            "native_location",
            "writer_policy",
            "canonical_project_hash",
            "project_visual_hash",
            "sidecar_hash",
        ]
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


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# Project Native Metadata Writer Stage 0\n\n"
        "Native project-file metadata writer proof for the supported Stage 0 "
        "Piskel and Pixelorama project carriers.\n\n"
        f"- Native round trips: {report['native_metadata_roundtrip_success_count']}/"
        f"{report['native_metadata_roundtrip_count']}\n"
        f"- Mean semantic fidelity: {metrics['mean_semantic_fidelity']}\n"
        f"- Invalid probe rejection rate: {metrics['invalid_probe_rejection_rate']}\n"
        "- Live external editor rewrite validation verified: "
        f"{metrics['live_external_editor_rewrite_validation_verified']}\n"
        f"- Unsupported native writer policies: {report['unsupported_native_writer_policy_count']}\n\n"
        "This artifact does not claim Aseprite/LibreSprite User Data chunk "
        "dispatch, live external editor rewrite validation, advanced "
        "tags/layers timeline schema coverage, package runtime integration, or "
        "full project-format coverage.\n"
    )


def _json_report(report: dict) -> dict:
    payload = deepcopy(report)
    for result in payload["native_results"]:
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
                "native_writer_format_count",
                "native_metadata_roundtrip_count",
                "native_metadata_roundtrip_success_count",
                "unsupported_native_writer_policy_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "native_summaries": [
            {
                "profile_id": result["profile_id"],
                "format_id": result["format_id"],
                "native_location": result["native_location"],
                "writer_policy": result["writer_policy"],
                "project_byte_count": result["project_byte_count"],
                "embedded_project_hash": result["embedded_project_hash"],
                "canonical_project_hash": result["canonical_project_hash"],
                "semantic_fidelity": result["semantic_fidelity"],
            }
            for result in json_report["native_results"]
        ],
    }


def _ensure_supported_format(format_id: str) -> None:
    if format_id not in SUPPORTED_NATIVE_METADATA_FORMATS:
        raise ProjectNativeMetadataError(
            "project_native_metadata_unsupported_format",
            f"native metadata writer unsupported for {format_id!r}",
        )


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _first_grid_path(profile: dict, generated_root: Path) -> Path:
    return sorted((generated_root / profile["profile_id"]).glob("*.json"))[0]


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
        default=ROOT / "data/workshop_editor/project_native_metadata_writer_stage0",
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
    report = run_project_native_metadata_writer_lab(profile_paths, args.generated_root)
    write_project_native_metadata_writer_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_PROJECT_NATIVE_METADATA_WRITER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(_json_report(report), indent=2))


if __name__ == "__main__":
    main()
