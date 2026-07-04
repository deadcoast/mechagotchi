import argparse
import json
import sys
import zlib
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME_DIR = ROOT / "labs" / "grid_genome"
if str(GRID_GENOME_DIR) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME_DIR))

from external_metadata_sidecar import _hash_payload
from png_embedded_sidecar_writer import (
    _chunk,
    _hash_bytes,
    _hash_json,
    _portable,
    _ratio,
    _read_json,
    _read_png_chunks,
    _write_json,
    _write_png_chunks,
)
from png_private_chunk_policy import (
    PRIVATE_METADATA_CHUNK_TYPE,
    _decode_private_chunk_data,
    _encode_private_chunk_data,
    _replace_private_chunk,
    export_png_private_chunk_bundle,
    import_png_private_chunk,
    remove_png_private_chunks,
)


REPORT_PATH = ROOT / "data/workshop_editor/png_private_chunk_preservation_matrix_stage0.json"
DATA_PATH = ROOT / "data/workshop_editor/png_private_chunk_preservation_matrix_data.js"
EDITOR_ANCILLARY_CHUNK_TYPE = "vpAg"


SCENARIO_POLICIES = [
    {
        "scenario_id": "preserve_exact_bytes",
        "editor_model": "identity_open_save_preserves_all_bytes",
        "critical_image_data_changed": False,
        "private_chunk_preserved": True,
        "mechagotchi_metadata_aware": False,
        "spec_copy_class": "no_editor_change",
        "expected_outcome": "private_chunk_preserved_valid",
    },
    {
        "scenario_id": "strip_private_without_visual_change",
        "editor_model": "metadata_stripping_open_save_without_visual_change",
        "critical_image_data_changed": False,
        "private_chunk_preserved": False,
        "mechagotchi_metadata_aware": False,
        "spec_copy_class": "unknown_private_chunk_dropped",
        "expected_outcome": "private_chunk_missing_after_editor_save",
    },
    {
        "scenario_id": "preserve_private_after_ancillary_append",
        "editor_model": "ancillary_metadata_append_preserves_unknown_private_chunk",
        "critical_image_data_changed": False,
        "private_chunk_preserved": True,
        "mechagotchi_metadata_aware": False,
        "spec_copy_class": "safe_to_copy_allowed_by_png_but_strict_hash_bound",
        "expected_outcome": "strict_hash_rejects_ancillary_change",
    },
    {
        "scenario_id": "strip_private_after_lossless_reencode",
        "editor_model": "lossless_reencode_drops_unknown_private_chunk",
        "critical_image_data_changed": True,
        "private_chunk_preserved": False,
        "mechagotchi_metadata_aware": False,
        "spec_copy_class": "unsafe_to_copy_dropped_after_critical_change",
        "expected_outcome": "private_chunk_missing_after_editor_save",
    },
    {
        "scenario_id": "preserve_private_after_lossless_reencode",
        "editor_model": "lossless_reencode_incorrectly_copies_unknown_unsafe_private_chunk",
        "critical_image_data_changed": True,
        "private_chunk_preserved": True,
        "mechagotchi_metadata_aware": False,
        "spec_copy_class": "unsafe_to_copy_stale_copy",
        "expected_outcome": "stale_private_chunk_rejected",
    },
    {
        "scenario_id": "mechagotchi_rebind_after_lossless_reencode",
        "editor_model": "metadata_aware_lossless_reencode_rebinds_private_chunk",
        "critical_image_data_changed": True,
        "private_chunk_preserved": True,
        "mechagotchi_metadata_aware": True,
        "spec_copy_class": "recognized_application_rewrites_binding",
        "expected_outcome": "private_chunk_rebound_valid",
    },
]


def simulate_png_editor_preservation_scenario(
    png_bytes: bytes,
    scenario_id: str,
) -> dict:
    policy = _scenario_policy(scenario_id)
    if scenario_id == "preserve_exact_bytes":
        transformed = png_bytes
    elif scenario_id == "strip_private_without_visual_change":
        transformed = remove_png_private_chunks(png_bytes)
    elif scenario_id == "preserve_private_after_ancillary_append":
        transformed = _append_editor_ancillary_chunk(png_bytes)
    elif scenario_id == "strip_private_after_lossless_reencode":
        transformed = remove_png_private_chunks(_lossless_reencode_idat(png_bytes))
    elif scenario_id == "preserve_private_after_lossless_reencode":
        transformed = _lossless_reencode_idat(png_bytes)
    elif scenario_id == "mechagotchi_rebind_after_lossless_reencode":
        transformed = _rebind_private_chunk_to_current_canonical(
            _lossless_reencode_idat(png_bytes)
        )
    else:
        raise ValueError(f"unsupported preservation scenario: {scenario_id}")

    return {
        **policy,
        "png_bytes": transformed,
        "input_byte_count": len(png_bytes),
        "output_byte_count": len(transformed),
        "byte_changed": transformed != png_bytes,
        "chunk_sequence": [chunk["type"] for chunk in _read_png_chunks(transformed)],
    }


def run_png_private_chunk_preservation_matrix_lab(
    profile_paths: list[Path],
    generated_root: Path,
) -> dict:
    matrix_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        bundle = export_png_private_chunk_bundle(grid, profile)
        for policy in SCENARIO_POLICIES:
            simulated = simulate_png_editor_preservation_scenario(
                bundle["png_bytes"],
                policy["scenario_id"],
            )
            imported = import_png_private_chunk(simulated["png_bytes"], source_grid=grid)
            actual_outcome = _actual_outcome(policy["scenario_id"], imported)
            matrix_results.append(
                {
                    "profile_id": profile["profile_id"],
                    "profile_path": _portable(profile_path),
                    "grid_path": _portable(grid_path),
                    "scenario_id": policy["scenario_id"],
                    "editor_model": policy["editor_model"],
                    "spec_copy_class": policy["spec_copy_class"],
                    "critical_image_data_changed": policy["critical_image_data_changed"],
                    "private_chunk_preserved": policy["private_chunk_preserved"],
                    "mechagotchi_metadata_aware": policy["mechagotchi_metadata_aware"],
                    "expected_outcome": policy["expected_outcome"],
                    "actual_outcome": actual_outcome,
                    "expected_outcome_matched": actual_outcome == policy["expected_outcome"],
                    "png_file_name": (
                        f"{profile['profile_id']}_{policy['scenario_id']}"
                        "_private_chunk_matrix.png"
                    ),
                    "png_bytes_hex": simulated["png_bytes"].hex(),
                    "input_byte_count": simulated["input_byte_count"],
                    "output_byte_count": simulated["output_byte_count"],
                    "byte_changed": simulated["byte_changed"],
                    "chunk_sequence": simulated["chunk_sequence"],
                    "import_result": _compact_import_result(imported),
                    "semantic_fidelity": imported.get("semantic_fidelity", 0.0),
                    "pixel_fidelity": imported.get("pixel_fidelity", 0.0),
                }
            )

    expected_matches = sum(1 for result in matrix_results if result["expected_outcome_matched"])
    recoverable = [result for result in matrix_results if result["import_result"]["ok"]]
    missing_count = sum(
        1
        for result in matrix_results
        if "png_private_chunk_missing" in result["import_result"]["error_families"]
    )
    stale_rejections = [
        result
        for result in matrix_results
        if "png_private_chunk_canonical_hash_mismatch"
        in result["import_result"]["error_families"]
    ]
    strict_ancillary_count = sum(
        1
        for result in stale_rejections
        if result["scenario_id"] == "preserve_private_after_ancillary_append"
    )
    return {
        "artifact_id": "png_private_chunk_preservation_matrix_stage0",
        "status": "research_png_private_chunk_preservation_matrix_no_package_code",
        "date": "2026-05-14",
        "purpose": (
            "Build a deterministic PNG editor-behavior matrix for the Stage 0 "
            "mgOT private chunk carrier, separating exact preservation, "
            "metadata stripping, stale unsafe-copy rejection, strict ancillary "
            "hash rejection, and Mechagotchi-aware rebinding."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "labs/workshop_editor/png_private_chunk_policy.py",
            "labs/workshop_editor/png_private_chunk_preservation_matrix.py",
        ],
        "external_sources": [
            {
                "name": "W3C Portable Network Graphics (PNG) Specification, Third Edition",
                "url": "https://www.w3.org/TR/png-3/",
                "used_for": (
                    "PNG editor behavior, ancillary chunk handling, private "
                    "chunk guidance, and safe-to-copy policy interpretation."
                ),
            }
        ],
        "profile_count": len(profile_paths),
        "scenario_count": len(SCENARIO_POLICIES),
        "matrix_result_count": len(matrix_results),
        "expected_outcome_match_count": expected_matches,
        "recoverable_import_count": len(recoverable),
        "missing_metadata_count": missing_count,
        "stale_private_chunk_rejection_count": len(stale_rejections),
        "strict_ancillary_rejection_count": strict_ancillary_count,
        "scenario_policies": deepcopy(SCENARIO_POLICIES),
        "matrix_results": matrix_results,
        "metrics": {
            "expected_outcome_match_rate": _ratio(expected_matches, len(matrix_results)),
            "recoverable_import_rate": _ratio(len(recoverable), len(matrix_results)),
            "metadata_loss_rate": _ratio(missing_count, len(matrix_results)),
            "stale_private_chunk_rejection_rate": _ratio(
                len(stale_rejections),
                len(matrix_results),
            ),
            "strict_ancillary_rejection_rate": _ratio(
                strict_ancillary_count,
                len(matrix_results),
            ),
            "recoverable_semantic_fidelity_mean": _mean(
                result["semantic_fidelity"] for result in recoverable
            ),
            "recoverable_pixel_fidelity_mean": _mean(
                result["pixel_fidelity"] for result in recoverable
            ),
            "live_external_editor_verified": False,
        },
        "closed_states": [
            "png_private_chunk_editor_preservation_matrix_simulated",
            "png_private_chunk_exact_preservation_gate",
            "png_private_chunk_stale_unsafe_copy_rejection_gate",
            "png_private_chunk_metadata_loss_detection_gate",
            "png_private_chunk_mechagotchi_rebind_gate",
        ],
        "blocked_states": [
            "live_external_editor_rewrite_validation",
            "final_png_production_carrier_selection",
            "APNG/full PNG conformance",
            "package_runtime_lifecycle_integration",
            "manual_readability_calibration",
            "profile_weighted_evolution",
        ],
        "decision": "prototype_png_private_chunk_preservation_matrix",
        "next_research_step": (
            "Use this simulated matrix as a carrier-selection input, but keep "
            "live external editor validation and final PNG production carrier "
            "selection blocked until real editor open-save fixtures exist."
        ),
    }


def write_png_private_chunk_preservation_matrix_artifacts(
    output_dir: Path,
    report: dict,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(
        output_dir / "png_private_chunk_preservation_matrix_stage0.json",
        _json_report(report),
    )
    for result in report["matrix_results"]:
        (output_dir / result["png_file_name"]).write_bytes(
            bytes.fromhex(result["png_bytes_hex"])
        )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "png_private_chunk_preservation_matrix_data.js").write_text(
        "window.MECHAGOTCHI_PNG_PRIVATE_CHUNK_PRESERVATION_MATRIX = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _lossless_reencode_idat(png_bytes: bytes) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    idat_payload = b"".join(chunk["data"] for chunk in chunks if chunk["type"] == "IDAT")
    raw = zlib.decompress(idat_payload)
    recompressed = zlib.compress(raw, level=0)
    updated = []
    wrote_idat = False
    for chunk in chunks:
        if chunk["type"] == "IDAT":
            if not wrote_idat:
                updated.append(_chunk("IDAT", recompressed))
                wrote_idat = True
            continue
        updated.append(chunk)
    return _write_png_chunks(updated)


def _append_editor_ancillary_chunk(png_bytes: bytes) -> bytes:
    chunks = _read_png_chunks(png_bytes)
    editor_chunk = _chunk(
        EDITOR_ANCILLARY_CHUNK_TYPE,
        b"mechagotchi.simulated.editor.ancillary.v1",
    )
    return _write_png_chunks(chunks[:-1] + [editor_chunk, chunks[-1]])


def _rebind_private_chunk_to_current_canonical(png_bytes: bytes) -> bytes:
    chunk = _single_private_chunk(png_bytes)
    metadata = _decode_private_chunk_data(chunk["data"])
    canonical_png_bytes = remove_png_private_chunks(png_bytes)
    canonical_hash = _hash_bytes(canonical_png_bytes)
    sidecar = deepcopy(metadata["sidecar"])
    sidecar["asset_binding"]["content_hash"] = canonical_hash
    sidecar["integrity"]["asset_content_hash"] = canonical_hash
    sidecar["integrity"]["binding_hash"] = _hash_payload(
        {
            "asset_hash": canonical_hash,
            "semantic_hash": sidecar["integrity"]["semantic_overlay_hash"],
            "profile_hash": sidecar["integrity"]["profile_hash"],
        }
    )
    sidecar["limitations"] = list(sidecar.get("limitations", [])) + [
        "Private chunk was rebound by a Mechagotchi-aware simulated editor after lossless IDAT reencoding.",
    ]
    metadata["canonical_png_hash"] = canonical_hash
    metadata["sidecar"] = sidecar
    metadata["sidecar_hash"] = _hash_json(sidecar)
    return _replace_private_chunk(
        png_bytes,
        PRIVATE_METADATA_CHUNK_TYPE,
        _encode_private_chunk_data(metadata),
    )


def _single_private_chunk(png_bytes: bytes) -> dict:
    chunks = _read_png_chunks(png_bytes)
    matches = [
        chunk
        for chunk in chunks
        if chunk["type"] == PRIVATE_METADATA_CHUNK_TYPE
        or chunk["data"].startswith(b"mechagotchi.private_chunk.v1\x00")
    ]
    if len(matches) != 1:
        raise ValueError("expected exactly one Mechagotchi private chunk")
    return matches[0]


def _actual_outcome(scenario_id: str, imported: dict) -> str:
    if imported["ok"]:
        if scenario_id == "mechagotchi_rebind_after_lossless_reencode":
            return "private_chunk_rebound_valid"
        return "private_chunk_preserved_valid"
    families = imported.get("error_families", [])
    if "png_private_chunk_missing" in families:
        return "private_chunk_missing_after_editor_save"
    if "png_private_chunk_canonical_hash_mismatch" in families:
        if scenario_id == "preserve_private_after_ancillary_append":
            return "strict_hash_rejects_ancillary_change"
        return "stale_private_chunk_rejected"
    return "unexpected_import_failure"


def _compact_import_result(result: dict) -> dict:
    return {
        "ok": result["ok"],
        "private_chunk_policy": result.get("private_chunk_policy"),
        "decoded_png": result.get("decoded_png"),
        "canonical_decoded_png": result.get("canonical_decoded_png"),
        "semantic_fidelity": result.get("semantic_fidelity", 0.0),
        "pixel_fidelity": result.get("pixel_fidelity", 0.0),
        "errors": result.get("errors", []),
        "error_families": result.get("error_families", []),
    }


def _scenario_policy(scenario_id: str) -> dict:
    for policy in SCENARIO_POLICIES:
        if policy["scenario_id"] == scenario_id:
            return deepcopy(policy)
    raise ValueError(f"unsupported preservation scenario: {scenario_id}")


def _first_grid_path(profile: dict, generated_root: Path) -> Path:
    grid_paths = sorted((generated_root / profile["profile_id"]).glob("*.json"))
    if not grid_paths:
        raise ValueError(f"no generated grids found for profile: {profile['profile_id']}")
    return grid_paths[0]


def _mean(values) -> float:
    values = list(values)
    if not values:
        return 0.0
    return round(sum(values) / len(values), 6)


def _json_report(report: dict) -> dict:
    payload = deepcopy(report)
    for result in payload["matrix_results"]:
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
                "scenario_count",
                "matrix_result_count",
                "expected_outcome_match_count",
                "recoverable_import_count",
                "missing_metadata_count",
                "stale_private_chunk_rejection_count",
                "strict_ancillary_rejection_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "scenario_policies": json_report["scenario_policies"],
        "matrix_summaries": [
            {
                "profile_id": result["profile_id"],
                "scenario_id": result["scenario_id"],
                "expected_outcome": result["expected_outcome"],
                "actual_outcome": result["actual_outcome"],
                "expected_outcome_matched": result["expected_outcome_matched"],
                "byte_changed": result["byte_changed"],
                "chunk_sequence": result["chunk_sequence"],
                "import_result": result["import_result"],
            }
            for result in json_report["matrix_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# PNG Private Chunk Preservation Matrix Stage 0\n\n"
        "Deterministic editor-behavior matrix for the Stage 0 `mgOT` private "
        "PNG metadata chunk carrier.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Scenarios: {report['scenario_count']}\n"
        f"- Matrix results: {report['matrix_result_count']}\n"
        "- Expected outcomes matched: "
        f"{report['expected_outcome_match_count']}/{report['matrix_result_count']}\n"
        f"- Recoverable imports: {report['recoverable_import_count']}\n"
        f"- Missing metadata outcomes: {report['missing_metadata_count']}\n"
        "- Stale private chunk rejections: "
        f"{report['stale_private_chunk_rejection_count']}\n"
        "- Strict ancillary-change rejections: "
        f"{report['strict_ancillary_rejection_count']}\n"
        "- Recoverable semantic fidelity mean: "
        f"{metrics['recoverable_semantic_fidelity_mean']}\n"
        "- Live external editor verified: "
        f"{metrics['live_external_editor_verified']}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "data/workshop_editor/png_private_chunk_preservation_matrix_stage0",
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
    report = run_png_private_chunk_preservation_matrix_lab(
        profile_paths,
        args.generated_root,
    )
    write_png_private_chunk_preservation_matrix_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_PNG_PRIVATE_CHUNK_PRESERVATION_MATRIX = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
