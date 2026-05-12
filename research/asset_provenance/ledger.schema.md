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
notes:
```

## Field Rules

- `asset_id` must be unique and stable.
- `spdx_id` must use the SPDX short identifier when one exists.
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
- Proprietary inspiration must be marked `reference_only` and excluded from the
  repository.
- External assets marked `reference_only` must not have an included path.

## Stage 0 Artifacts

The first executable ledger prototype lives in:

```txt
labs/asset_pipeline/provenance_ledger.py
data/asset_provenance/ledger.json
data/asset_provenance/validation_report.json
data/asset_provenance/attribution_manifest.json
```

Stage 0 validates three included internal research artifacts and four
reference-only external sources.

## Starting Policy

Mechagotchi should default to internally generated or hand-authored seed assets.
External assets are allowed for research, benchmarking, palette exploration, and
interoperability tests only when provenance is explicit.

## Sources

- https://spdx.org/licenses/
- https://reuse.software/
- https://creativecommons.org/cc-licenses/
- https://opengameart.org/content/faq
