# Asset Provenance Ledger Schema

Every external asset, palette, code sample, dataset, or imported reference used
by Mechagotchi research must have a ledger entry before it is committed into a
shipping path.

## Required Fields

```yaml
asset_id:
title:
asset_type:
creator:
source:
source_url:
download_date:
license:
spdx_id:
spdx_expression:
license_url:
derivative_of:
modifications:
hash_algorithm:
hash:
included_in_repo:
included_path:
shipping_scope:
commercial_allowed:
redistribution_allowed:
share_alike_required:
attribution_required:
attribution_text:
review_status:
reviewer:
decision_record:
notes:
```

## Field Rules

- `asset_id` must be unique and stable.
- `spdx_id` must use the primary SPDX short identifier when one exists.
- `spdx_expression` must be a valid SPDX license expression. It may be a
  single identifier, `LicenseRef-*`, or a compound expression using `AND`,
  `OR`, `WITH`, and parentheses.
- `included_in_repo` must be `true` only if the asset is actually committed.
- `included_path` must exist when `included_in_repo` is `true`.
- `hash` is required for committed assets and must match the committed file or
  directory tree.
- `shipping_scope` must be one of `research`, `optional_pack`, `core`, or
  `reference_only`.
- `review_status` must be one of `unreviewed`, `approved`, `rejected`,
  `reference_only`, or `needs_legal_review`.
- Copyleft or share-alike assets must not become default core assets without a
  decision record.
- Included copyleft or share-alike assets must include `decision_record`.
- Proprietary inspiration must be marked `reference_only` and excluded from the
  repository.
- External assets marked `reference_only` must not have an included path.

## Stage 0 Artifacts

The first executable ledger prototype lives in:

```txt
labs/asset_pipeline/provenance_ledger.py
data/asset_provenance/ledger.json
data/asset_provenance/validation_report.json
data/asset_provenance/provenance_ci_report.json
data/asset_provenance/attribution_manifest.json
```

Stage 0 validates three included internal research artifacts and four
reference-only external sources. The follow-up CI report parses SPDX
expressions, checks hashes, and fails risky included share-alike or copyleft
assets that lack decision-record metadata.

## Starting Policy

Mechagotchi should default to internally generated or hand-authored seed assets.
External assets are allowed for research, benchmarking, palette exploration, and
interoperability tests only when provenance is explicit.


## Correction, 2026-10-04: checkout portability

The original local provenance pass did not prove fresh-checkout portability.
DR 0061 identifies the working-tree line-ending and native-path-sort assumptions.
The original artifacts remain under `data/asset_provenance/baselines/stage0-windows/`;
the current ledger is explicitly restated under `raw-bytes-posix-lexical-v1`.
See `research/experiment_reports/2026-10-04-ci-portability-repair.md` and
`data/asset_provenance/portability_restatement_stage0.json` for measured deltas.

## Sources

- https://spdx.org/licenses/
- https://spdx.github.io/spdx-spec/v2.2.2/SPDX-license-expressions/
- https://reuse.software/spec-3.3/
- https://creativecommons.org/cc-licenses/
- https://opengameart.org/content/faq
