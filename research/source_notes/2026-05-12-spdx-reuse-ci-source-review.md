# SPDX and REUSE CI Source Review - 2026-05-12

## Primary Sources

- https://spdx.org/licenses/
- https://spdx.github.io/spdx-spec/v2.2.2/SPDX-license-expressions/
- https://reuse.software/spec-3.3/

## Confirmed Facts

- The SPDX License List provides standardized short identifiers, full names,
  license text, and canonical URLs for licenses and exceptions.
- SPDX license expressions may use license identifiers, `LicenseRef-*`, `WITH`
  exceptions, `AND`, `OR`, `+`, and parentheses.
- SPDX expression operators are case-sensitive.
- `WITH` applies an exception to a simple license expression.
- REUSE requires licensing information to use valid SPDX license expressions.
- REUSE uses `LicenseRef-*` when a license is not in the SPDX License List.

## Mechagotchi Interpretation

The provenance ledger should keep a primary `spdx_id` for simple reporting and
add `spdx_expression` for the full machine-checkable expression. CI should fail
invalid expressions, stale hashes, and included copyleft/share-alike assets that
do not carry decision-record metadata.
