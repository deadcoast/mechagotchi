import argparse
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

from external_metadata_sidecar import restore_grid_from_sidecar
from project_native_metadata_writer import (
    NATIVE_METADATA_KEY,
    PISKEL_DESCRIPTION_PREFIX,
    ProjectNativeMetadataError,
    _read_pxo_member,
    extract_project_native_metadata,
    project_visual_hash,
    rebind_sidecar_to_project_hash,
    remove_project_native_metadata,
    write_project_native_metadata,
)
from third_party_project_decoder import (
    PROJECT_FORMATS,
    ProjectDecodeError,
    decode_project_payload,
    export_project_with_sidecar,
)
from workshop_editor import compare_semantic_grid_fidelity


REPORT_PATH = Path("data/workshop_editor/project_editor_rewrite_preservation_stage0.json")
DATA_PATH = Path("data/workshop_editor/project_editor_rewrite_preservation_data.js")
SUPPORTED_REWRITE_FORMATS = ["piskel_project", "pixelorama_pxo"]
_REWRITE_ZIP_DATE = (2026, 2, 1, 0, 0, 0)


def simulate_editor_rewrite(project_bytes: bytes, format_id: str, *, editor_id: str) -> dict:
    if format_id == "piskel_project":
        rewritten = _simulate_piskel_rewrite(project_bytes, editor_id)
    elif format_id == "pixelorama_pxo":
        rewritten = _simulate_pixelorama_rewrite(project_bytes, editor_id)
    else:
        raise ProjectNativeMetadataError(
            "project_rewrite_unsupported_format",
            f"editor rewrite simulation unsupported for {format_id!r}",
        )
    return {
        "project_bytes": rewritten,
        "format_id": format_id,
        "editor_id": editor_id,
        "visual_hash": project_visual_hash(rewritten, format_id),
        "canonical_project_hash": remove_project_native_metadata(rewritten, format_id)["content_hash"],
        "decoded_project": decode_project_payload(rewritten, format_id),
    }


def import_project_after_editor_rewrite(
    project_bytes: bytes,
    format_id: str,
    source_grid: dict | None = None,
) -> dict:
    try:
        extracted = extract_project_native_metadata(
            project_bytes,
            format_id,
            allow_rewrite=True,
        )
    except (ProjectNativeMetadataError, ProjectDecodeError) as exc:
        return _failed_import(
            "project_editor_rewrite",
            getattr(exc, "family", "project_editor_rewrite_invalid"),
            getattr(exc, "message", str(exc)),
        )

    sidecar = rebind_sidecar_to_project_hash(
        extracted["sidecar"],
        extracted["current_canonical_project_hash"],
    )
    asset = deepcopy(sidecar["asset_binding"])
    try:
        restored = restore_grid_from_sidecar(sidecar, asset)
    except ValueError as exc:
        return _failed_import("sidecar", "project_rewrite_sidecar_invalid", str(exc))

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
        "rewrite_detected": extracted["rewrite_detected"],
        "native_metadata": {
            "metadata_version": extracted["metadata"]["metadata_version"],
            "native_location": extracted["metadata"]["native_location"],
            "project_visual_hash": extracted["metadata"]["project_visual_hash"],
            "original_canonical_project_hash": extracted["metadata"]["canonical_project_hash"],
            "rewritten_canonical_project_hash": extracted["current_canonical_project_hash"],
        },
        "restored_grid": restored,
        "restored_grid_validation": {
            "valid": grid_validation.ok,
            "errors": grid_validation.errors,
            "slip_aligned": alignment.ok,
            "slip_errors": alignment.errors,
        },
        "project_policy": {
            "semantic_policy": "project_editor_rewrite_rebound",
            "native_mechagotchi_semantics": True,
            "live_external_editor_verified": False,
            "visual_hash_verified": True,
        },
        "semantic_diff": diff,
        "semantic_fidelity": fidelity,
        "errors": errors,
        "error_families": sorted({error["family"] for error in errors}),
    }


def tamper_project_visual_payload(project_bytes: bytes, format_id: str) -> bytes:
    if format_id == "piskel_project":
        payload = _read_piskel_payload(project_bytes)
        layer = json.loads(payload["piskel"]["layers"][0])
        layer["chunks"][0]["layout"] = [[0], [0]]
        payload["piskel"]["layers"][0] = json.dumps(layer, sort_keys=True, separators=(",", ":"))
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if format_id == "pixelorama_pxo":
        data, members = _read_pixelorama_archive(project_bytes)
        data["frames"] = list(reversed(data.get("frames", [])))
        return _write_pixelorama_archive(data, members, reverse_members=True)
    raise ProjectNativeMetadataError(
        "project_rewrite_unsupported_format",
        f"visual tamper unsupported for {format_id!r}",
    )


def run_project_editor_rewrite_preservation_lab(
    profile_paths: list[Path],
    generated_root: Path,
) -> dict:
    rewrite_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        for format_id in SUPPORTED_REWRITE_FORMATS:
            exported = export_project_with_sidecar(grid, profile, format_id)
            embedded = write_project_native_metadata(
                exported["project_bytes"],
                format_id,
                exported["sidecar"],
            )
            editor_id = (
                "piskel_save_v1"
                if format_id == "piskel_project"
                else "pixelorama_save_v1"
            )
            rewritten = simulate_editor_rewrite(
                embedded["project_bytes"],
                format_id,
                editor_id=editor_id,
            )
            imported = import_project_after_editor_rewrite(
                rewritten["project_bytes"],
                format_id,
                source_grid=grid,
            )
            slug = "piskel" if format_id == "piskel_project" else "pixelorama"
            extension = PROJECT_FORMATS[format_id]["extension"]
            rewrite_results.append(
                {
                    "profile_id": profile["profile_id"],
                    "profile_path": _portable(profile_path),
                    "grid_path": _portable(grid_path),
                    "format_id": format_id,
                    "editor_id": editor_id,
                    "project_file_name": f"{profile['profile_id']}_{slug}_rewritten{extension}",
                    "project_bytes_hex": rewritten["project_bytes"].hex(),
                    "project_byte_count": len(rewritten["project_bytes"]),
                    "original_canonical_project_hash": embedded["canonical_project_hash"],
                    "rewritten_canonical_project_hash": rewritten["canonical_project_hash"],
                    "project_visual_hash": rewritten["visual_hash"],
                    "visual_hash_preserved": (
                        embedded["metadata"]["project_visual_hash"] == rewritten["visual_hash"]
                    ),
                    "rewrite_detected": (
                        embedded["canonical_project_hash"] != rewritten["canonical_project_hash"]
                    ),
                    "decoded_project": _decoded_project_summary(rewritten["decoded_project"]),
                    "import_result": _compact_import_result(imported),
                    "restored_grid_validation": imported.get("restored_grid_validation", {}),
                    "semantic_diff": imported.get("semantic_diff", {}),
                    "semantic_fidelity": imported.get("semantic_fidelity", 0.0),
                }
            )

    invalid_probe_results = _invalid_probe_results(rewrite_results[0])
    success_count = sum(
        1
        for result in rewrite_results
        if result["import_result"]["ok"]
        and result["visual_hash_preserved"]
        and result["rewrite_detected"]
        and result["semantic_fidelity"] == 1.0
    )
    visual_preserved_count = sum(1 for result in rewrite_results if result["visual_hash_preserved"])
    invalid_rejected_count = sum(1 for result in invalid_probe_results if not result["ok"])
    return {
        "artifact_id": "project_editor_rewrite_preservation_stage0",
        "status": "research_project_editor_rewrite_preservation_no_package_code",
        "date": "2026-05-13",
        "purpose": (
            "Prove deterministic editor-save rewrite preservation for the "
            "Stage 0 Piskel and Pixelorama native metadata subset without "
            "claiming live external-editor validation."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
            "labs/workshop_editor/project_native_metadata_writer.py",
            "labs/workshop_editor/project_editor_rewrite_preservation.py",
        ],
        "external_anchors": [
            {
                "source": "Piskel Serializer.js",
                "url": "https://github.com/piskelapp/piskel/blob/master/src/js/utils/serialization/Serializer.js",
                "used_for": "Piskel writes description into the serialized project envelope.",
            },
            {
                "source": "Piskel Deserializer.js",
                "url": "https://github.com/piskelapp/piskel/blob/master/src/js/utils/serialization/Deserializer.js",
                "used_for": "Piskel reads description back into the project descriptor.",
            },
            {
                "source": "Pixelorama project documentation",
                "url": "https://pixelorama.org/concepts/project/",
                "used_for": "Pixelorama .pxo data.json and image_data folder rewrite boundary.",
            },
            {
                "source": "Aseprite file-format specification",
                "url": "https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md",
                "used_for": "User Data Chunk remains a future live chunk writer target.",
            },
        ],
        "profile_count": len(profile_paths),
        "simulated_editor_format_count": len(SUPPORTED_REWRITE_FORMATS),
        "rewrite_roundtrip_count": len(rewrite_results),
        "rewrite_roundtrip_success_count": success_count,
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "metrics": {
            "rewrite_roundtrip_success_rate": _ratio(success_count, len(rewrite_results)),
            "mean_semantic_fidelity": round(
                sum(result["semantic_fidelity"] for result in rewrite_results)
                / max(1, len(rewrite_results)),
                6,
            ),
            "visual_hash_preservation_rate": _ratio(
                visual_preserved_count,
                len(rewrite_results),
            ),
            "invalid_probe_rejection_rate": _ratio(
                invalid_rejected_count,
                len(invalid_probe_results),
            ),
            "live_external_editor_verified": False,
        },
        "rewrite_results": rewrite_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "project_editor_rewrite_preservation_simulated",
            "piskel_description_rewrite_preservation_simulated",
            "pixelorama_data_json_rewrite_preservation_simulated",
            "project_visual_hash_preservation_gate",
            "project_rewrite_sidecar_rebind_policy",
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
        "decision": "prototype_project_editor_rewrite_preservation_subset",
        "next_research_step": (
            "Keep live external-editor rewrite validation, arbitrary Aseprite "
            "project schema coverage, advanced tags/layers timeline coverage, "
            "and full project-format coverage blocked until direct editor or "
            "broader chunk/schema tests exist."
        ),
    }


def write_project_editor_rewrite_preservation_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "project_editor_rewrite_preservation_stage0.json", _json_report(report))
    for result in report["rewrite_results"]:
        (output_dir / result["project_file_name"]).write_bytes(
            bytes.fromhex(result["project_bytes_hex"])
        )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "project_editor_rewrite_preservation_data.js").write_text(
        "window.MECHAGOTCHI_PROJECT_EDITOR_REWRITE_PRESERVATION = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _simulate_piskel_rewrite(project_bytes: bytes, editor_id: str) -> bytes:
    payload = _read_piskel_payload(project_bytes)
    payload["piskel"]["editorRewriteSimulation"] = {
        "editor_id": editor_id,
        "preserves_description": True,
        "preserves_layer_chunks": True,
    }
    rewritten_layers = []
    for layer_string in payload["piskel"].get("layers", []):
        layer = json.loads(layer_string)
        rewritten_layers.append(json.dumps(layer, indent=2, sort_keys=True))
    payload["piskel"]["layers"] = rewritten_layers
    return (json.dumps(payload, indent=2, sort_keys=False) + "\n").encode("utf-8")


def _simulate_pixelorama_rewrite(project_bytes: bytes, editor_id: str) -> bytes:
    data, members = _read_pixelorama_archive(project_bytes)
    data["editor_rewrite_simulation"] = {
        "editor_id": editor_id,
        "preserves_data_json_metadata": True,
        "preserves_image_data": True,
    }
    return _write_pixelorama_archive(data, members, reverse_members=True)


def _invalid_probe_results(reference_result: dict) -> list[dict]:
    project_bytes = bytes.fromhex(reference_result["project_bytes_hex"])
    format_id = reference_result["format_id"]
    missing = remove_project_native_metadata(project_bytes, format_id)["project_bytes"]
    tampered_payload = _read_piskel_payload(project_bytes)
    metadata = extract_project_native_metadata(project_bytes, format_id, allow_rewrite=True)["metadata"]
    metadata = deepcopy(metadata)
    metadata["sidecar"]["asset_binding"]["width"] = 99
    tampered_payload["piskel"]["description"] = (
        PISKEL_DESCRIPTION_PREFIX
        + json.dumps(metadata, sort_keys=True, separators=(",", ":"))
    )
    visual_tampered = tamper_project_visual_payload(project_bytes, format_id)
    return [
        _compact_import_result(import_project_after_editor_rewrite(missing, format_id)),
        _compact_import_result(
            import_project_after_editor_rewrite(
                json.dumps(tampered_payload, sort_keys=True, separators=(",", ":")).encode("utf-8"),
                format_id,
            )
        ),
        _compact_import_result(import_project_after_editor_rewrite(visual_tampered, format_id)),
    ]


def _read_piskel_payload(project_bytes: bytes) -> dict:
    try:
        payload = json.loads(project_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProjectNativeMetadataError("project_json_invalid", str(exc)) from exc
    if not isinstance(payload.get("piskel"), dict):
        raise ProjectNativeMetadataError("piskel_payload_missing", "piskel object is required")
    return payload


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


def _write_pixelorama_archive(
    data: dict,
    members: dict[str, bytes],
    *,
    reverse_members: bool = False,
) -> bytes:
    buffer = io.BytesIO()
    names = sorted(members, reverse=reverse_members)
    with zipfile.ZipFile(buffer, "w") as archive:
        _writestr_stable(
            archive,
            "data.json",
            (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        )
        for name in names:
            _writestr_stable(archive, name, members[name])
    return buffer.getvalue()


def _writestr_stable(archive: zipfile.ZipFile, name: str, payload: bytes) -> None:
    info = zipfile.ZipInfo(name, _REWRITE_ZIP_DATE)
    info.compress_type = zipfile.ZIP_DEFLATED
    archive.writestr(info, payload)


def _compact_import_result(result: dict) -> dict:
    return {
        "ok": result["ok"],
        "format_id": result.get("format_id"),
        "asset": result.get("asset"),
        "decoded_project": result.get("decoded_project"),
        "rewrite_detected": result.get("rewrite_detected", False),
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
        "dimensions",
        "frame_count",
        "layer_count",
        "chunk_count",
        "cel_count",
        "native_mechagotchi_semantics",
    ]
    return {key: decoded[key] for key in keys if key in decoded}


def _json_report(report: dict) -> dict:
    payload = deepcopy(report)
    for result in payload["rewrite_results"]:
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
                "simulated_editor_format_count",
                "rewrite_roundtrip_count",
                "rewrite_roundtrip_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "rewrite_summaries": [
            {
                "profile_id": result["profile_id"],
                "format_id": result["format_id"],
                "editor_id": result["editor_id"],
                "rewrite_detected": result["rewrite_detected"],
                "visual_hash_preserved": result["visual_hash_preserved"],
                "semantic_fidelity": result["semantic_fidelity"],
            }
            for result in json_report["rewrite_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# Project Editor Rewrite Preservation Stage 0\n\n"
        "Deterministic editor-save rewrite simulation for the Stage 0 Piskel "
        "and Pixelorama native metadata subset.\n\n"
        f"- Rewrite round trips: {report['rewrite_roundtrip_success_count']}/"
        f"{report['rewrite_roundtrip_count']}\n"
        f"- Mean semantic fidelity: {metrics['mean_semantic_fidelity']}\n"
        f"- Visual hash preservation rate: {metrics['visual_hash_preservation_rate']}\n"
        f"- Invalid probe rejection rate: {metrics['invalid_probe_rejection_rate']}\n"
        f"- Live external editor verified: {metrics['live_external_editor_verified']}\n\n"
        "This artifact does not claim live Piskel/Pixelorama open-save testing, "
        "arbitrary Aseprite project schema coverage, advanced tags/layers "
        "timeline schema coverage, package runtime integration, or full "
        "project-format coverage.\n"
    )


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


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _first_grid_path(profile: dict, generated_root: Path) -> Path:
    return sorted((generated_root / profile["profile_id"]).glob("*.json"))[0]


def _portable(path: Path) -> str:
    return str(path).replace("\\", "/")


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
        default=Path("data/workshop_editor/project_editor_rewrite_preservation_stage0"),
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
    report = run_project_editor_rewrite_preservation_lab(profile_paths, args.generated_root)
    write_project_editor_rewrite_preservation_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_PROJECT_EDITOR_REWRITE_PRESERVATION = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(_json_report(report), indent=2))


if __name__ == "__main__":
    main()
