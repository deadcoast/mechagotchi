# Experiment Report: Provenance CI and SPDX Parser

Date: 2026-05-12

## Objective

Continue the post-v0.1 research plan by extending the asset provenance ledger
with CI-style checks and SPDX expression parsing.

## Source Basis

SPDX license expressions allow single license IDs, `LicenseRef-*`, exceptions
with `WITH`, and compound expressions using `AND`, `OR`, and parentheses. SPDX
operators are case-sensitive. REUSE requires file licensing information to use
valid SPDX license expressions and defines `LicenseRef-*` for non-SPDX-list
licenses.

Sources:

- https://spdx.org/licenses/
- https://spdx.github.io/spdx-spec/v2.2.2/SPDX-license-expressions/
- https://reuse.software/spec-3.3/

## Scope

Included:

- SPDX expression parser for the project-supported license subset
- `LicenseRef-*` support
- `AND`, `OR`, `WITH`, `+`, and parentheses
- known exception support for current parser tests
- CI report generation at `data/asset_provenance/provenance_ci_report.json`
- `--ci` command mode with non-zero exit behavior on failed report
- decision-record gate for included share-alike or copyleft assets

Not included:

- full SPDX License List ingestion
- full REUSE header scanning
- `REUSE.toml` generation
- legal-review workflow

## TDD Evidence

RED command:

```powershell
python -B -m unittest discover -s labs\asset_pipeline -p 'test_*.py'
```

Initial result:

```txt
ImportError: cannot import name 'build_provenance_ci_report'
```

GREEN command:

```powershell
python -B -m unittest discover -s labs\asset_pipeline -p 'test_*.py'
```

Result:

```txt
Ran 11 tests in 0.075s
OK
```

Lab command:

```powershell
python -B labs\asset_pipeline\provenance_ledger.py --output-dir data\asset_provenance --ci
```

Result summary:

```json
{
  "ok": true,
  "checks": {
    "ledger_validation_ok": true,
    "spdx_expressions_ok": true,
    "included_hashes_ok": true,
    "decision_record_gate_ok": true
  },
  "spdx_summary": {
    "expression_count": 7,
    "parsed_expression_count": 7
  }
}
```

## Findings

The provenance ledger can now represent both a primary `spdx_id` and a full
`spdx_expression`. This keeps simple reporting stable while allowing future
dual-license or exception-bearing assets to be validated before import.

The CI report is clean for the current research ledger. The parser correctly
rejects lowercase operators and unknown license identifiers inside compound
expressions.

## Decision

Adopt the provenance CI report for research artifacts. Do not treat this as full
release compliance until repository-wide REUSE scanning and legal-review
workflow are added.


## Correction, 2026-10-04: checkout portability

The original local provenance pass did not prove fresh-checkout portability.
DR 0061 identifies the working-tree line-ending and native-path-sort assumptions.
The original artifacts remain under `data/asset_provenance/baselines/stage0-windows/`;
the current ledger is explicitly restated under `raw-bytes-posix-lexical-v1`.
See `research/experiment_reports/2026-10-04-ci-portability-repair.md` and
`data/asset_provenance/portability_restatement_stage0.json` for measured deltas.

## Sources

- `research/decision_records/0061-portable-provenance-and-ci-evidence.md`
