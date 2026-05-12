import argparse
import hashlib
import json
from pathlib import Path


REQUIRED_FIELDS = [
    "asset_id",
    "title",
    "asset_type",
    "creator",
    "source",
    "source_url",
    "download_date",
    "license",
    "spdx_id",
    "license_url",
    "derivative_of",
    "modifications",
    "hash_algorithm",
    "hash",
    "included_in_repo",
    "included_path",
    "shipping_scope",
    "commercial_allowed",
    "redistribution_allowed",
    "share_alike_required",
    "attribution_required",
    "attribution_text",
    "review_status",
    "reviewer",
    "notes",
]

REVIEW_STATUSES = {
    "unreviewed",
    "approved",
    "rejected",
    "reference_only",
    "needs_legal_review",
}

KNOWN_SPDX_IDS = {
    "Apache-2.0",
    "CC-BY-4.0",
    "CC-BY-SA-4.0",
    "CC0-1.0",
    "GPL-2.0-only",
    "GPL-3.0-or-later",
    "MIT",
    "LicenseRef-Mechagotchi-Internal-Research",
    "LicenseRef-Reference-Only",
}


def hash_included_path(path: Path) -> dict:
    if path.is_file():
        return {
            "hash_algorithm": "sha256",
            "hash": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    if path.is_dir():
        digest = hashlib.sha256()
        for child in sorted(item for item in path.rglob("*") if item.is_file()):
            digest.update(child.relative_to(path).as_posix().encode("utf-8"))
            digest.update(b"\0")
            digest.update(hashlib.sha256(child.read_bytes()).hexdigest().encode("ascii"))
            digest.update(b"\0")
        return {"hash_algorithm": "sha256-tree", "hash": digest.hexdigest()}
    raise FileNotFoundError(path)


def build_stage0_ledger(repo_root: Path) -> dict:
    return {
        "ledger_version": "0.1.0",
        "generated_date": "2026-05-12",
        "policy": {
            "default_shipping_rule": "internal_or_approved_permissive_only",
            "reference_only_rule": "external research references are not shipped",
            "share_alike_rule": "share-alike or copyleft assets require a decision record before core use",
        },
        "assets": [
            _included_asset(
                repo_root,
                asset_id="internal_seed_grid_corpus_v1",
                title="Mechagotchi Seed Grid Corpus v1",
                asset_type="dataset",
                included_path="data/seed_grids",
                notes="Hand-authored internal semantic grid corpus.",
            ),
            _included_asset(
                repo_root,
                asset_id="cubff_synthetic_snapshot_corpus_stage0",
                title="Synthetic CUBFF-Style Snapshot Corpus Stage 0",
                asset_type="dataset",
                included_path="data/cubff_transducer/synthetic_snapshots.json",
                notes="Synthetic research data; not real CuBFF output.",
            ),
            _included_asset(
                repo_root,
                asset_id="workshop_editor_stage0_export",
                title="Workshop Editor Stage 0 Export",
                asset_type="grid_genome",
                included_path="data/workshop_editor/workshop_export_stage0.json",
                notes="Internally generated workshop export sample.",
            ),
            _reference_asset(
                asset_id="piskel_reference_only",
                title="Piskel",
                asset_type="tool_reference",
                creator="Piskel contributors",
                source_url="https://github.com/piskelapp/piskel",
                license="Apache License 2.0",
                spdx_id="Apache-2.0",
                license_url="https://www.apache.org/licenses/LICENSE-2.0",
                notes="Web sprite editor reference. No code or assets embedded.",
            ),
            _reference_asset(
                asset_id="pixelorama_reference_only",
                title="Pixelorama",
                asset_type="tool_reference",
                creator="Orama Interactive contributors",
                source_url="https://github.com/Orama-Interactive/Pixelorama",
                license="MIT License",
                spdx_id="MIT",
                license_url="https://opensource.org/license/mit",
                notes="Metadata and export workflow reference. No code or assets embedded.",
            ),
            _reference_asset(
                asset_id="libresprite_reference_only",
                title="LibreSprite",
                asset_type="tool_reference",
                creator="LibreSprite contributors",
                source_url="https://github.com/LibreSprite/LibreSprite",
                license="GNU General Public License v2.0 only",
                spdx_id="GPL-2.0-only",
                license_url="https://www.gnu.org/licenses/old-licenses/gpl-2.0.html",
                notes="Animation UX reference only; GPL code is not embedded.",
            ),
            _reference_asset(
                asset_id="opengameart_policy_reference",
                title="OpenGameArt FAQ",
                asset_type="license_policy_reference",
                creator="OpenGameArt.org",
                source_url="https://opengameart.org/content/faq",
                license="Reference only",
                spdx_id="LicenseRef-Reference-Only",
                license_url="https://opengameart.org/content/faq",
                notes="Used to define accepted/restricted art-license handling.",
            ),
        ],
    }


def validate_ledger(ledger: dict, repo_root: Path) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    assets = ledger.get("assets", [])
    if ledger.get("ledger_version") != "0.1.0":
        errors.append("ledger_version must be 0.1.0")
    if not isinstance(assets, list) or not assets:
        errors.append("assets must be a non-empty array")
        assets = []

    seen_ids: set[str] = set()
    for index, entry in enumerate(assets):
        prefix = f"asset[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix} must be an object")
            continue
        _validate_entry(entry, repo_root, seen_ids, errors, warnings)

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "asset_count": len(assets),
            "included_count": sum(
                1 for entry in assets if isinstance(entry, dict) and entry.get("included_in_repo") is True
            ),
            "reference_only_count": sum(
                1 for entry in assets if isinstance(entry, dict) and entry.get("review_status") == "reference_only"
            ),
            "attribution_required_count": sum(
                1 for entry in assets if isinstance(entry, dict) and entry.get("attribution_required") is True
            ),
        },
    }


def generate_attribution_manifest(ledger: dict) -> dict:
    attributions = []
    for entry in ledger.get("assets", []):
        if entry.get("attribution_required") is True:
            attributions.append(
                {
                    "asset_id": entry["asset_id"],
                    "title": entry["title"],
                    "creator": entry["creator"],
                    "license": entry["license"],
                    "spdx_id": entry["spdx_id"],
                    "source_url": entry["source_url"],
                    "attribution_text": entry["attribution_text"],
                    "included_in_repo": entry["included_in_repo"],
                    "included_path": entry["included_path"],
                }
            )
    return {
        "manifest_version": "0.1.0",
        "generated_date": ledger.get("generated_date", "2026-05-12"),
        "attributions": attributions,
    }


def write_stage0_artifacts(output_dir: Path, ledger: dict, repo_root: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    validation = validate_ledger(ledger, repo_root)
    attribution = generate_attribution_manifest(ledger)
    _write_json(output_dir / "ledger.json", ledger)
    _write_json(output_dir / "validation_report.json", validation)
    _write_json(output_dir / "attribution_manifest.json", attribution)
    (output_dir / "README.md").write_text(_readme_text(validation), encoding="utf-8")


def _validate_entry(
    entry: dict,
    repo_root: Path,
    seen_ids: set[str],
    errors: list[str],
    warnings: list[str],
) -> None:
    asset_id = entry.get("asset_id", "<missing>")
    for field in REQUIRED_FIELDS:
        if field not in entry:
            errors.append(f"{asset_id}: missing required field {field}")

    if asset_id in seen_ids:
        errors.append(f"{asset_id}: duplicate asset_id")
    seen_ids.add(asset_id)

    if entry.get("review_status") not in REVIEW_STATUSES:
        errors.append(f"{asset_id}: invalid review_status {entry.get('review_status')}")

    if entry.get("spdx_id") not in KNOWN_SPDX_IDS:
        errors.append(f"{asset_id}: unknown or unsupported SPDX identifier {entry.get('spdx_id')}")

    included = entry.get("included_in_repo") is True
    if included:
        included_path = entry.get("included_path", "")
        if not included_path:
            errors.append(f"{asset_id}: included asset missing included_path")
        else:
            path = repo_root / included_path
            if not path.exists():
                errors.append(f"{asset_id}: included path does not exist: {included_path}")
            else:
                actual = hash_included_path(path)
                if entry.get("hash_algorithm") != actual["hash_algorithm"]:
                    errors.append(f"{asset_id}: included asset hash algorithm mismatch")
                if not entry.get("hash"):
                    errors.append(f"{asset_id}: included asset missing hash")
                elif entry.get("hash") != actual["hash"]:
                    errors.append(f"{asset_id}: included asset hash mismatch")
        if entry.get("review_status") not in {"approved", "needs_legal_review"}:
            errors.append(f"{asset_id}: included asset must be approved or needs_legal_review")
    else:
        if entry.get("included_path"):
            errors.append(f"{asset_id}: excluded asset must not have included_path")
        if entry.get("hash"):
            warnings.append(f"{asset_id}: excluded asset hash is ignored")
        if entry.get("review_status") != "reference_only":
            warnings.append(f"{asset_id}: excluded asset is not marked reference_only")

    if entry.get("source") == "external" and included and entry.get("review_status") != "approved":
        errors.append(f"{asset_id}: included external asset must be approved")

    if entry.get("commercial_allowed") is False and entry.get("shipping_scope") == "core":
        errors.append(f"{asset_id}: noncommercial asset cannot be core")

    if entry.get("share_alike_required") is True and entry.get("shipping_scope") == "core":
        errors.append(f"{asset_id}: share-alike asset cannot be core without decision record")

    if entry.get("attribution_required") is True and not entry.get("attribution_text"):
        errors.append(f"{asset_id}: attribution required but attribution_text is empty")


def _included_asset(
    repo_root: Path,
    *,
    asset_id: str,
    title: str,
    asset_type: str,
    included_path: str,
    notes: str,
) -> dict:
    digest = hash_included_path(repo_root / included_path)
    return {
        "asset_id": asset_id,
        "title": title,
        "asset_type": asset_type,
        "creator": "Mechagotchi research team",
        "source": "internal",
        "source_url": "",
        "download_date": "2026-05-12",
        "license": "Mechagotchi internal research asset",
        "spdx_id": "LicenseRef-Mechagotchi-Internal-Research",
        "license_url": "",
        "derivative_of": "",
        "modifications": "created for Mechagotchi research",
        "hash_algorithm": digest["hash_algorithm"],
        "hash": digest["hash"],
        "included_in_repo": True,
        "included_path": included_path,
        "shipping_scope": "research",
        "commercial_allowed": True,
        "redistribution_allowed": True,
        "share_alike_required": False,
        "attribution_required": False,
        "attribution_text": "",
        "review_status": "approved",
        "reviewer": "research_lead",
        "notes": notes,
    }


def _reference_asset(
    *,
    asset_id: str,
    title: str,
    asset_type: str,
    creator: str,
    source_url: str,
    license: str,
    spdx_id: str,
    license_url: str,
    notes: str,
) -> dict:
    return {
        "asset_id": asset_id,
        "title": title,
        "asset_type": asset_type,
        "creator": creator,
        "source": "external",
        "source_url": source_url,
        "download_date": "2026-05-12",
        "license": license,
        "spdx_id": spdx_id,
        "license_url": license_url,
        "derivative_of": "",
        "modifications": "none; reference only",
        "hash_algorithm": "",
        "hash": "",
        "included_in_repo": False,
        "included_path": "",
        "shipping_scope": "reference_only",
        "commercial_allowed": True,
        "redistribution_allowed": False,
        "share_alike_required": spdx_id in {"CC-BY-SA-4.0", "GPL-2.0-only", "GPL-3.0-or-later"},
        "attribution_required": spdx_id not in {"CC0-1.0", "LicenseRef-Reference-Only"},
        "attribution_text": (
            f"{title} by {creator}, licensed under {license}. Source: {source_url}"
            if spdx_id not in {"CC0-1.0", "LicenseRef-Reference-Only"}
            else ""
        ),
        "review_status": "reference_only",
        "reviewer": "research_lead",
        "notes": notes,
    }


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _readme_text(validation: dict) -> str:
    summary = validation["summary"]
    return (
        "# Asset Provenance Ledger Stage 0\n\n"
        "Machine-readable provenance ledger for current Mechagotchi research artifacts.\n\n"
        f"- Validation ok: {validation['ok']}\n"
        f"- Asset count: {summary['asset_count']}\n"
        f"- Included count: {summary['included_count']}\n"
        f"- Reference-only count: {summary['reference_only_count']}\n"
        f"- Attribution-required count: {summary['attribution_required_count']}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("data/asset_provenance"))
    args = parser.parse_args()

    repo_root = Path(".")
    ledger = build_stage0_ledger(repo_root)
    write_stage0_artifacts(args.output_dir, ledger, repo_root)
    print(json.dumps(validate_ledger(ledger, repo_root), indent=2))


if __name__ == "__main__":
    main()
