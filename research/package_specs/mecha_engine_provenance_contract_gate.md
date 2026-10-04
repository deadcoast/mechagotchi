# Mecha Engine Provenance Contract Gate

Date: 2026-05-12

## Status

Research acceptance gate. This document does not create or modify
`packages/mecha_engine`.

## Purpose

Define the package-level contract for the future `mecha_engine.provenance`
module before provenance CI code is moved out of `labs/asset_pipeline`.

## Source Evidence

The Stage 0 provenance labs already prove:

- The current ledger contains 7 assets.
- 3 assets are included in the repository.
- 4 assets are reference-only external sources.
- 3 assets require attribution text.
- Ledger validation passes.
- SPDX expression parsing passes for 7 of 7 ledger expressions.
- Included hash checks pass.
- The share-alike and copyleft decision-record gate passes for current assets.
- The test suite covers stable file and directory hashing, missing hashes,
  unknown license IDs, lowercase operators, risky core share-alike assets, CI
  report generation, and attribution manifest generation.

The package provenance module may adopt the deterministic parser, ledger
validator, hashing, CI report, and attribution-manifest contract. It must not
pretend this is full legal review or full repository-wide REUSE compliance.

## Compliance Model

Provenance is a deterministic policy gate:

```txt
ledger + repo_root
  -> validate required fields
  -> parse SPDX expressions
  -> verify included hashes
  -> enforce review and decision-record policy
  -> emit CI report and attribution manifest
```

The first package contract is a research and package-promotion gate, not a
license-attorney workflow. Any release-compliance claim requires a later gate
for repository-wide REUSE scanning, package license metadata, and legal review.

## Required Public Surface

```python
from mecha_engine.provenance import (
    build_ci_report,
    generate_attribution_manifest,
    hash_included_path,
    parse_spdx_expression,
    validate_ledger,
)
```

Required contracts:

- `parse_spdx_expression(expression: str) -> dict`
- `validate_ledger(ledger: dict, repo_root) -> dict`
- `build_ci_report(ledger: dict, repo_root) -> dict`
- `generate_attribution_manifest(ledger: dict) -> dict`
- `hash_included_path(path) -> dict`

The package function name `build_ci_report` intentionally hides the lab-only
name `build_provenance_ci_report`; package callers should not inherit lab file
names.

## Ledger Acceptance

`validate_ledger` must:

- require ledger version `0.1.0` until a schema migration gate exists;
- require a non-empty `assets` array;
- require every field listed in `research/asset_provenance/ledger.schema.md`;
- require stable unique `asset_id` values;
- require `review_status` to be one of `unreviewed`, `approved`, `rejected`,
  `reference_only`, or `needs_legal_review`;
- require `spdx_id` to be a supported SPDX short identifier or a supported
  `LicenseRef-*`;
- require `spdx_id` to appear inside `spdx_expression`;
- require included assets to have an existing `included_path`;
- require included assets to have `hash_algorithm` and `hash` values matching
  the committed file or directory tree;
- require included assets to be `approved` or `needs_legal_review`;
- require included external assets to be `approved`;
- reject core noncommercial assets;
- require included share-alike or copyleft assets to provide a
  `decision_record`;
- reject share-alike assets as default core assets without a decision record;
- require attribution text when `attribution_required` is true;
- return JSON-serializable `ok`, `errors`, `warnings`, and `summary`.

Required summary fields:

- `asset_count`
- `included_count`
- `reference_only_count`
- `attribution_required_count`

## SPDX Expression Acceptance

`parse_spdx_expression` must:

- accept project-supported SPDX identifiers;
- accept `LicenseRef-*`;
- accept `DocumentRef-...:LicenseRef-*`;
- accept `AND`, `OR`, `WITH`, `+`, and parentheses according to the supported
  Stage 0 subset;
- return sorted `license_ids`, `exception_ids`, and `operators`;
- return `contains_copyleft` when the expression contains a known copyleft or
  share-alike identifier;
- reject unknown SPDX license identifiers;
- reject unknown SPDX exception identifiers;
- reject malformed parentheses and unexpected tokens;
- reject lowercase operators under the current project policy.

SPDX specification v2.2.2 defines the uppercase operators `AND`, `OR`, and
`WITH` and states that operators should be matched case-sensitively. SPDX
3.0.1 permits upper-case or lower-case operator forms when matched
case-sensitively. The Stage 0 lab deliberately enforces uppercase canonical
operators. A future change to accept lowercase SPDX 3.x forms must be made by
explicit schema and test revision, not by accidental parser drift.

## Hash Acceptance

`hash_included_path` must:

- return `{"hash_algorithm": "sha256", "hash": <64 hex chars>}` for files;
- return `{"hash_algorithm": "sha256-tree", "hash": <64 hex chars>}` for
  directories;
- hash directory files in deterministic relative-path order;
- include both relative path names and child file digests in the tree hash;
- raise `FileNotFoundError` for absent paths;
- avoid network access and environment-dependent metadata.

The package gate must preserve the current Stage 0 included-artifact hashes
unless the source artifact changes and the provenance CI report is regenerated.

## CI Report Acceptance

`build_ci_report` must return:

- `report_version`
- `generated_date`
- `ok`
- `checks`
- `errors`
- `warnings`
- `validation`
- `spdx_summary`
- `spdx_results`

Required `checks` keys:

- `ledger_validation_ok`
- `spdx_expressions_ok`
- `included_hashes_ok`
- `decision_record_gate_ok`

Required `spdx_summary` keys:

- `expression_count`
- `parsed_expression_count`
- `license_ids`
- `exception_ids`
- `operators`

The current Stage 0 package-design baseline is:

| Metric | Value |
| --- | ---: |
| Ledger assets | 7 |
| Included assets | 3 |
| Reference-only assets | 4 |
| Attribution-required assets | 3 |
| SPDX expressions parsed | 7 / 7 |
| CI report ok | true |
| Included hashes ok | true |
| Decision-record gate ok | true |

## Attribution Manifest Acceptance

`generate_attribution_manifest` must:

- include only assets where `attribution_required` is true;
- preserve `asset_id`, title, creator, license, SPDX ID, SPDX expression,
  source URL, attribution text, inclusion status, and included path;
- exclude internal assets that do not require attribution;
- return a stable manifest version until a schema migration gate exists.

## Negative Checks

The provenance package gate fails if:

- `packages/mecha_engine/src/mecha_engine/provenance` imports `labs`;
- package tests import `labs`;
- package tests mutate `sys.path` to reach `labs`;
- package code writes Stage 0 artifacts as an import side effect;
- unknown SPDX identifiers pass silently;
- lowercase operators pass without an explicit schema revision;
- included assets can omit hashes;
- stale included hashes pass;
- included share-alike or copyleft assets can ship without decision-record
  metadata;
- reference-only assets are treated as shipped assets;
- attribution-required assets can be omitted from the attribution manifest;
- package metadata declares release license fields before the repository and
  package license decision is explicit;
- the gate is described as legal review or complete release compliance.

## Future Verification Commands

Run these after the scaffold and `provenance` implementation exist:

```powershell
python -B -m unittest discover -s .\labs\asset_pipeline -p "test_*.py"
python -B .\labs\asset_pipeline\provenance_ledger.py --output-dir .\data\asset_provenance --ci
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
python -c "from mecha_engine.provenance import parse_spdx_expression, validate_ledger, build_ci_report, generate_attribution_manifest, hash_included_path"
rg -n "from labs|import labs|labs/|labs\\|sys\\.path" .\packages\mecha_engine
python -B .\labs\package_promotion\package_promotion_gate.py --root . --output-dir .\data\package_promotion
git diff --check
```

Expected implementation-stage result:

- Lab provenance tests still pass.
- Package provenance tests pass through `mecha_engine.provenance`.
- Package CI report reproduces the Stage 0 clean checks or records an
  intentional schema revision in a new decision record.
- Included hashes are checked against committed files and directories.
- SPDX parsing remains deterministic.
- Reference-only external sources remain excluded from shipped package assets.
- The package contains no runtime or test imports from `labs`.
- Package-promotion gate is rerun after package provenance tests exist.

## Non-Goals

- No package creation in this research step.
- No provenance implementation migration.
- No repository-wide REUSE scanner.
- No `REUSE.toml` generation.
- No legal-review workflow.
- No final package license metadata decision.
- No full SPDX License List ingestion.
- No SBOM generation.


## Correction, 2026-10-04: checkout portability

The original local provenance pass did not prove fresh-checkout portability.
DR 0061 identifies the working-tree line-ending and native-path-sort assumptions.
The original artifacts remain under `data/asset_provenance/baselines/stage0-windows/`;
the current ledger is explicitly restated under `raw-bytes-posix-lexical-v1`.
See `research/experiment_reports/2026-10-04-ci-portability-repair.md` and
`data/asset_provenance/portability_restatement_stage0.json` for measured deltas.

## Sources

- `research/package_specs/mecha_engine_module_interfaces.md`
- `research/asset_provenance/ledger.schema.md`
- `research/algorithm_cards/provenance_ci_spdx.md`
- `research/experiment_reports/2026-05-12-provenance-ci-spdx-parser.md`
- `labs/asset_pipeline/provenance_ledger.py`
- `labs/asset_pipeline/test_provenance_ledger.py`
- `data/asset_provenance/ledger.json`
- `data/asset_provenance/provenance_ci_report.json`
- `data/asset_provenance/attribution_manifest.json`
- `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json`
- SPDX License Expressions v2.2.2:
  https://spdx.github.io/spdx-spec/v2.2.2/SPDX-license-expressions/
- SPDX License Expressions v3.0.1:
  https://spdx.github.io/spdx-spec/v3.0.1/annexes/spdx-license-expressions/
- SPDX License List:
  https://spdx.org/licenses/
- REUSE Specification 3.3:
  https://reuse.software/spec-3.3/
