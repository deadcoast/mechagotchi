import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME_DIR = ROOT / "labs" / "grid_genome"
if str(GRID_GENOME_DIR) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME_DIR))

from aseprite_document_variant_resolution import (
    VARIANT_SPECS,
    export_aseprite_document_variant_bundle,
    import_aseprite_document_variant_project,
    _artifact_external_assets,
    _compact_import_result,
    _extract_document_variant_metadata,
    _failed_import,
    _hash_text,
    _portable,
    _ratio,
    _read_json,
    _write_json,
)
from aseprite_user_data_chunk_writer import AsepriteUserDataError


REPORT_PATH = Path("data/workshop_editor/aseprite_external_asset_resolver_matrix_stage0.json")
DATA_PATH = Path("data/workshop_editor/aseprite_external_asset_resolver_matrix_data.js")
RESOLVER_MATRIX_VERSION = "mechagotchi.aseprite_external_asset_resolver_matrix.v1"
RESOLVER_POLICY_IDS = [
    "direct_manifest",
    "relative_file_map",
    "content_addressed_pool",
    "multi_root_priority",
]


class AsepriteExternalAssetResolverError(ValueError):
    def __init__(self, family: str, message: str):
        super().__init__(message)
        self.family = family
        self.message = message


def export_aseprite_external_asset_resolver_matrix_bundle(grid: dict, slip_profile: dict) -> dict:
    document_bundle = export_aseprite_document_variant_bundle(grid, slip_profile)
    manifest = document_bundle["metadata"]["external_asset_manifest"]
    assets = _artifact_external_assets(document_bundle["external_assets"])
    resolver_cases = [
        _resolver_case_direct_manifest(assets),
        _resolver_case_relative_file_map(assets, slip_profile["profile_id"]),
        _resolver_case_content_addressed_pool(assets),
        _resolver_case_multi_root_priority(assets, slip_profile["profile_id"]),
    ]
    return {
        "metadata": {
            "resolver_matrix_version": RESOLVER_MATRIX_VERSION,
            "profile_id": slip_profile["profile_id"],
            "grid_id": grid["grid_id"],
            "resolver_policy_ids": RESOLVER_POLICY_IDS,
            "document_variant_ids": [spec["variant_id"] for spec in VARIANT_SPECS],
        },
        "external_asset_manifest": manifest,
        "external_assets": assets,
        "document_variants": [
            {
                "variant_id": variant["variant_id"],
                "color_depth_bpp": variant["color_depth_bpp"],
                "bytes_per_pixel": variant["bytes_per_pixel"],
                "project_bytes": variant["project_bytes"],
                "project_file_name": f"{slip_profile['profile_id']}_{variant['variant_id']}.aseprite",
                "project_byte_count": len(variant["project_bytes"]),
                "embedded_project_hash": variant["embedded_project_hash"],
                "canonical_project_hash": variant["canonical_project_hash"],
            }
            for variant in document_bundle["variants"]
        ],
        "resolver_cases": resolver_cases,
    }


def resolve_aseprite_external_assets(
    external_asset_manifest: list[dict],
    resolver_input: dict,
    *,
    strict: bool = True,
) -> list[dict]:
    policy_id = resolver_input.get("policy_id")
    if policy_id not in RESOLVER_POLICY_IDS:
        raise AsepriteExternalAssetResolverError(
            "aseprite_resolver_policy_unsupported",
            f"unsupported Aseprite external asset resolver policy: {policy_id}",
        )
    candidates = _candidate_assets(resolver_input)
    resolved = []
    for manifest_entry in external_asset_manifest:
        matches = [
            candidate
            for candidate in candidates
            if _candidate_matches_manifest(candidate, manifest_entry, policy_id)
        ]
        if not matches:
            if strict:
                raise AsepriteExternalAssetResolverError(
                    "aseprite_resolver_asset_missing",
                    f"resolver did not provide asset: {manifest_entry['name']}",
                )
            continue
        unique_paths = sorted({match.get("resolver_path", match["name"]) for match in matches})
        if len(unique_paths) > 1:
            raise AsepriteExternalAssetResolverError(
                "aseprite_resolver_asset_ambiguous",
                f"resolver returned multiple candidate paths for: {manifest_entry['name']}",
            )
        asset = _normal_asset(matches[0])
        payload_hash = _hash_text(asset.get("payload_text", ""))
        if (
            asset["content_hash"] != manifest_entry["content_hash"]
            or payload_hash != manifest_entry["content_hash"]
        ):
            raise AsepriteExternalAssetResolverError(
                "aseprite_resolver_asset_hash_mismatch",
                f"resolver asset hash mismatch for: {manifest_entry['name']}",
            )
        resolved.append(asset)
    return resolved


def import_aseprite_document_variant_with_resolver(
    project_bytes: bytes,
    resolver_input: dict,
    source_grid: dict | None = None,
) -> dict:
    try:
        metadata = _extract_document_variant_metadata(project_bytes)
        resolved_assets = resolve_aseprite_external_assets(
            metadata.get("external_asset_manifest", []),
            resolver_input,
        )
        imported = import_aseprite_document_variant_project(
            project_bytes,
            resolved_assets,
            source_grid=source_grid,
        )
    except AsepriteExternalAssetResolverError as exc:
        return _failed_import("aseprite_external_asset_resolver", exc.family, exc.message)
    except AsepriteUserDataError as exc:
        return _failed_import("aseprite_document_variant", exc.family, exc.message)

    if imported["ok"]:
        imported["project_policy"]["external_asset_resolver_policy"] = resolver_input["policy_id"]
        imported["project_policy"]["external_asset_resolver_version"] = RESOLVER_MATRIX_VERSION
        imported["project_policy"]["resolved_external_asset_count"] = len(resolved_assets)
        imported["resolved_external_assets"] = [
            _resolved_asset_summary(asset, resolver_input["policy_id"]) for asset in resolved_assets
        ]
    return imported


def make_missing_asset_resolver_input(resolver_input: dict) -> dict:
    mutated = deepcopy(resolver_input)
    key = _source_key(mutated)
    mutated[key] = mutated.get(key, [])[1:]
    return mutated


def make_tampered_payload_resolver_input(resolver_input: dict) -> dict:
    mutated = deepcopy(resolver_input)
    key = _source_key(mutated)
    if mutated.get(key):
        mutated[key][0]["payload_text"] = mutated[key][0].get("payload_text", "") + "\n# tampered\n"
    return mutated


def make_ambiguous_resolver_input(resolver_input: dict) -> dict:
    mutated = deepcopy(resolver_input)
    key = _source_key(mutated)
    if mutated.get(key):
        duplicate = deepcopy(mutated[key][0])
        duplicate["resolver_path"] = f"duplicate/{duplicate['name']}"
        duplicate["root_id"] = "ambiguous_duplicate_root"
        mutated[key].append(duplicate)
    return mutated


def make_path_traversal_resolver_input(resolver_input: dict) -> dict:
    mutated = deepcopy(resolver_input)
    key = _source_key(mutated)
    if mutated.get(key):
        mutated[key][0]["relative_path"] = f"../escape/{mutated[key][0]['name']}"
    return mutated


def run_aseprite_external_asset_resolver_matrix_lab(
    profile_paths: list[Path],
    generated_root: Path,
) -> dict:
    resolver_results = []
    bundles = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        bundle = export_aseprite_external_asset_resolver_matrix_bundle(grid, profile)
        bundles.append(bundle)
        for variant in bundle["document_variants"]:
            for resolver_case in bundle["resolver_cases"]:
                imported = import_aseprite_document_variant_with_resolver(
                    variant["project_bytes"],
                    resolver_case["resolver_input"],
                    source_grid=grid,
                )
                resolver_results.append(
                    {
                        "profile_id": profile["profile_id"],
                        "profile_path": _portable(profile_path),
                        "grid_path": _portable(grid_path),
                        "grid_id": grid["grid_id"],
                        "variant_id": variant["variant_id"],
                        "color_depth_bpp": variant["color_depth_bpp"],
                        "resolver_policy_id": resolver_case["policy_id"],
                        "project_file_name": variant["project_file_name"],
                        "project_byte_count": variant["project_byte_count"],
                        "project_bytes_hex": variant["project_bytes"].hex(),
                        "embedded_project_hash": variant["embedded_project_hash"],
                        "canonical_project_hash": variant["canonical_project_hash"],
                        "resolver_input_summary": _resolver_input_summary(resolver_case["resolver_input"]),
                        "external_asset_manifest": bundle["external_asset_manifest"],
                        "import_result": _compact_import_result(imported),
                        "resolved_external_assets": imported.get("resolved_external_assets", []),
                        "semantic_fidelity": imported.get("semantic_fidelity", 0.0),
                        "ok": imported["ok"],
                    }
                )

    invalid_probe_results = _invalid_probe_results(bundles[0])
    success_count = sum(1 for result in resolver_results if result["ok"])
    resolution_success = sum(
        1
        for result in resolver_results
        if result["ok"] and len(result["resolved_external_assets"]) == 3
    )
    invalid_rejected = sum(1 for result in invalid_probe_results if not result["ok"])
    return {
        "artifact_id": "aseprite_external_asset_resolver_matrix_stage0",
        "status": "research_aseprite_external_asset_resolver_matrix_no_package_code",
        "date": "2026-05-14",
        "purpose": (
            "Broaden Aseprite External Files Chunk evidence from generated direct "
            "asset lists to a bounded multi-policy resolver matrix with direct, "
            "relative path, content-addressed, and multi-root lookup."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "labs/workshop_editor/aseprite_document_variant_resolution.py",
            "data/slips/multi_profile_generation_stage0/",
        ],
        "external_anchors": [
            {
                "source": "Aseprite file-format specification",
                "url": "https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md",
                "used_for": "External Files Chunk 0x2008 and document-variant compatibility boundary.",
            }
        ],
        "profile_count": len(profile_paths),
        "resolver_policy_count": len(RESOLVER_POLICY_IDS),
        "document_variant_count_per_profile": len(VARIANT_SPECS),
        "resolver_roundtrip_count": len(resolver_results),
        "resolver_roundtrip_success_count": success_count,
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected,
        "resolver_policy_ids": RESOLVER_POLICY_IDS,
        "resolver_results": resolver_results,
        "invalid_probe_results": invalid_probe_results,
        "metrics": {
            "resolver_roundtrip_success_rate": _ratio(success_count, len(resolver_results)),
            "mean_semantic_fidelity": _mean(result["semantic_fidelity"] for result in resolver_results),
            "external_asset_resolution_rate": _ratio(resolution_success, len(resolver_results)),
            "invalid_probe_rejection_rate": _ratio(invalid_rejected, len(invalid_probe_results)),
            "live_external_editor_verified": False,
        },
        "closed_states": [
            "aseprite_direct_manifest_asset_resolver_subset",
            "aseprite_relative_file_asset_resolver_subset",
            "aseprite_content_addressed_asset_resolver_subset",
            "aseprite_multi_root_asset_resolver_subset",
            "aseprite_external_asset_resolver_invalid_probe_rejection",
        ],
        "blocked_states": [
            "live_external_editor_rewrite_validation",
            "editor_authored_aseprite_document_variants",
            "arbitrary_aseprite_project_schema_coverage",
            "full_project_format_coverage",
            "package_runtime_lifecycle_integration",
            "manual_readability_calibration",
            "profile_weighted_evolution",
        ],
        "decision": "prototype_aseprite_external_asset_resolver_matrix_subset",
        "next_research_step": (
            "Keep live editor validation, editor-authored Aseprite variants, "
            "arbitrary project schemas, and package runtime integration blocked "
            "until direct fixtures or explicit implementation authorization exist."
        ),
    }


def write_aseprite_external_asset_resolver_matrix_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    projects_dir = output_dir / "projects"
    sources_dir = output_dir / "resolver_sources"
    projects_dir.mkdir(parents=True, exist_ok=True)
    sources_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "aseprite_external_asset_resolver_matrix_stage0.json", _json_report(report))
    written_projects = set()
    written_assets = set()
    for result in report["resolver_results"]:
        project_name = result["project_file_name"]
        if project_name not in written_projects:
            (projects_dir / project_name).write_bytes(bytes.fromhex(result["project_bytes_hex"]))
            written_projects.add(project_name)
        for asset in result["resolver_input_summary"].get("sources", []):
            relative = asset.get("relative_path")
            payload = asset.get("payload_text")
            if not relative or payload is None:
                continue
            asset_path = sources_dir / relative
            if str(asset_path) in written_assets:
                continue
            asset_path.parent.mkdir(parents=True, exist_ok=True)
            asset_path.write_text(payload, encoding="utf-8")
            written_assets.add(str(asset_path))
    content_dir = sources_dir / "content_addressed"
    content_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "aseprite_external_asset_resolver_matrix_data.js").write_text(
        "window.MECHAGOTCHI_ASEPRITE_EXTERNAL_ASSET_RESOLVER_MATRIX = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _resolver_case_direct_manifest(assets: list[dict]) -> dict:
    return {
        "policy_id": "direct_manifest",
        "resolver_input": {
            "policy_id": "direct_manifest",
            "assets": deepcopy(assets),
        },
    }


def _resolver_case_relative_file_map(assets: list[dict], profile_id: str) -> dict:
    return {
        "policy_id": "relative_file_map",
        "resolver_input": {
            "policy_id": "relative_file_map",
            "sources": [
                {
                    **deepcopy(asset),
                    "root_id": "profile_asset_root",
                    "relative_path": f"{profile_id}/assets/{asset['name']}",
                    "resolver_path": f"profile_asset_root/{profile_id}/assets/{asset['name']}",
                }
                for asset in assets
            ],
        },
    }


def _resolver_case_content_addressed_pool(assets: list[dict]) -> dict:
    return {
        "policy_id": "content_addressed_pool",
        "resolver_input": {
            "policy_id": "content_addressed_pool",
            "sources": [
                {
                    **deepcopy(asset),
                    "root_id": "content_addressed",
                    "relative_path": f"content_addressed/{_hash_slug(asset['content_hash'])}.asset",
                    "resolver_path": f"content_addressed/{_hash_slug(asset['content_hash'])}.asset",
                }
                for asset in assets
            ],
        },
    }


def _resolver_case_multi_root_priority(assets: list[dict], profile_id: str) -> dict:
    return {
        "policy_id": "multi_root_priority",
        "resolver_input": {
            "policy_id": "multi_root_priority",
            "sources": [
                {
                    **deepcopy(asset),
                    "root_id": "profile_root",
                    "relative_path": f"{profile_id}/multi_root/{asset['type_name']}/{asset['name']}",
                    "resolver_path": f"profile_root/{profile_id}/multi_root/{asset['type_name']}/{asset['name']}",
                }
                for asset in assets
            ],
        },
    }


def _candidate_assets(resolver_input: dict) -> list[dict]:
    key = _source_key(resolver_input)
    candidates = []
    for item in resolver_input.get(key, []):
        _validate_relative_path(item)
        candidates.append(_normal_asset(item))
    return candidates


def _candidate_matches_manifest(candidate: dict, manifest_entry: dict, policy_id: str) -> bool:
    if policy_id == "content_addressed_pool":
        return candidate.get("content_hash") == manifest_entry["content_hash"]
    return candidate.get("name") == manifest_entry["name"]


def _normal_asset(asset: dict) -> dict:
    normalized = deepcopy(asset)
    normalized.setdefault("payload_text", normalized.get("payload", ""))
    normalized.setdefault("content_hash", _hash_text(normalized.get("payload_text", "")))
    return normalized


def _validate_relative_path(item: dict) -> None:
    relative_path = item.get("relative_path")
    if not relative_path:
        return
    path = Path(relative_path)
    if path.is_absolute() or ".." in path.parts:
        raise AsepriteExternalAssetResolverError(
            "aseprite_resolver_path_traversal",
            f"resolver relative path escapes the asset root: {relative_path}",
        )


def _source_key(resolver_input: dict) -> str:
    return "assets" if resolver_input.get("policy_id") == "direct_manifest" else "sources"


def _resolved_asset_summary(asset: dict, policy_id: str) -> dict:
    return {
        "resolver_policy_id": policy_id,
        "entry_id": asset["entry_id"],
        "type": asset["type"],
        "type_name": asset["type_name"],
        "name": asset["name"],
        "media_type": asset["media_type"],
        "content_hash": asset["content_hash"],
        "resolver_path": asset.get("resolver_path", asset["name"]),
    }


def _resolver_input_summary(resolver_input: dict) -> dict:
    key = _source_key(resolver_input)
    sources = []
    for source in resolver_input.get(key, []):
        summary = {
            item_key: source[item_key]
            for item_key in [
                "entry_id",
                "type",
                "type_name",
                "name",
                "media_type",
                "content_hash",
                "relative_path",
                "resolver_path",
                "root_id",
                "payload_text",
            ]
            if item_key in source
        }
        sources.append(summary)
    return {
        "policy_id": resolver_input.get("policy_id"),
        "source_count": len(sources),
        "sources": sources,
    }


def _invalid_probe_results(bundle: dict) -> list[dict]:
    variant = bundle["document_variants"][0]
    base_input = bundle["resolver_cases"][1]["resolver_input"]
    probes = [
        ("missing_asset", make_missing_asset_resolver_input(base_input)),
        ("tampered_payload", make_tampered_payload_resolver_input(base_input)),
        ("ambiguous_asset", make_ambiguous_resolver_input(base_input)),
        ("path_traversal", make_path_traversal_resolver_input(base_input)),
        ("unsupported_policy", {"policy_id": "unsupported_policy", "assets": []}),
    ]
    return [
        {
            "probe_id": probe_id,
            **_compact_import_result(
                import_aseprite_document_variant_with_resolver(
                    variant["project_bytes"],
                    resolver_input,
                )
            ),
        }
        for probe_id, resolver_input in probes
    ]


def _json_report(report: dict) -> dict:
    payload = deepcopy(report)
    for result in payload["resolver_results"]:
        result.pop("project_bytes_hex", None)
        for source in result.get("resolver_input_summary", {}).get("sources", []):
            source.pop("payload_text", None)
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
                "resolver_policy_count",
                "resolver_roundtrip_count",
                "resolver_roundtrip_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "resolver_summaries": [
            {
                "profile_id": result["profile_id"],
                "variant_id": result["variant_id"],
                "resolver_policy_id": result["resolver_policy_id"],
                "semantic_fidelity": result["semantic_fidelity"],
                "resolved_external_assets": result["resolved_external_assets"],
            }
            for result in json_report["resolver_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# Aseprite External Asset Resolver Matrix Stage 0\n\n"
        "Bounded resolver matrix for Aseprite/LibreSprite External Files Chunk "
        "asset references across direct, relative-path, content-addressed, and "
        "multi-root policies.\n\n"
        f"- Resolver round trips: {report['resolver_roundtrip_success_count']}/"
        f"{report['resolver_roundtrip_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}/"
        f"{report['invalid_probe_count']}\n"
        f"- Mean semantic fidelity: {metrics['mean_semantic_fidelity']}\n"
        f"- External asset resolution rate: {metrics['external_asset_resolution_rate']}\n"
        f"- Live external editor verified: {str(metrics['live_external_editor_verified']).lower()}\n\n"
        "This artifact does not claim live external editor validation, "
        "editor-authored Aseprite variants, arbitrary project schemas, package "
        "runtime integration, or full project-format coverage.\n"
    )


def _mean(values) -> float:
    values = list(values)
    if not values:
        return 0.0
    return round(sum(values) / len(values), 6)


def _hash_slug(content_hash: str) -> str:
    return content_hash.replace("sha256:", "")[:16]


def _first_grid_path(profile: dict, generated_root: Path) -> Path:
    grid_paths = sorted((generated_root / profile["profile_id"]).glob("*.json"))
    if not grid_paths:
        raise ValueError(f"no generated grids found for profile: {profile['profile_id']}")
    return grid_paths[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/workshop_editor/aseprite_external_asset_resolver_matrix_stage0"),
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
    report = run_aseprite_external_asset_resolver_matrix_lab(
        profile_paths,
        args.generated_root,
    )
    write_aseprite_external_asset_resolver_matrix_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, _json_report(report))
    DATA_PATH.write_text(
        "window.MECHAGOTCHI_ASEPRITE_EXTERNAL_ASSET_RESOLVER_MATRIX = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
