# Algorithm Card: Provenance CI and SPDX Expression Parser

## Purpose

Turn the asset provenance ledger into a CI-style gate that can fail invalid
license expressions, stale hashes, and risky included assets before they enter
shipping paths.

## Mathematical Basis

This is a deterministic parser and policy checker, not a generative algorithm.
The parser follows the SPDX license-expression grammar for simple identifiers,
`LicenseRef-*`, `AND`, `OR`, `WITH`, and parentheses.

## Inputs

- `data/asset_provenance/ledger.json`
- Included asset file and directory paths
- SPDX short identifiers and license expressions
- Review status, shipping scope, and decision-record metadata

## Outputs

- `data/asset_provenance/provenance_ci_report.json`
- Parsed license IDs, exception IDs, and operators
- Pass/fail checks for ledger validation, expressions, hashes, and
  decision-record gates

## Strengths

- Blocks malformed SPDX expressions early
- Preserves the existing attribution manifest workflow
- Makes provenance validation suitable for CI execution through `--ci`
- Keeps reference-only copyleft tools outside shipping paths while still
  recording their license risk

## Weaknesses

- The parser validates only the project-supported SPDX ID subset plus
  `LicenseRef-*`
- It is not a substitute for legal review
- REUSE file-header scanning is still future work

## Failure Modes

- Unknown license IDs inside compound expressions
- Lowercase operators such as `or` instead of `OR`
- Included assets with stale hashes
- Included share-alike or copyleft assets with no decision record

## Integration Risk

Low for research artifacts. Medium if expanded into release gating without
adding full repository scanning and legal review workflow.

## License Status

Internal Mechagotchi research code. The source rules are based on official SPDX
and REUSE specifications.

Sources:

- https://spdx.org/licenses/
- https://spdx.github.io/spdx-spec/v2.2.2/SPDX-license-expressions/
- https://reuse.software/spec-3.3/

## Prototype Result

Implemented on 2026-05-12.

Artifacts:

- `labs/asset_pipeline/provenance_ledger.py`
- `labs/asset_pipeline/test_provenance_ledger.py`
- `data/asset_provenance/provenance_ci_report.json`
- `research/experiment_reports/2026-05-12-provenance-ci-spdx-parser.md`

Measured result:

- Ledger validation: pass
- SPDX expressions parsed: 7/7
- Included hashes: pass
- Decision-record gate: pass

## Decision

Adopt for research artifact CI. Keep full REUSE header scanning, `REUSE.toml`
generation, and legal-review workflow as later provenance work.


## Correction, 2026-10-04: checkout portability

The original local provenance pass did not prove fresh-checkout portability.
DR 0061 identifies the working-tree line-ending and native-path-sort assumptions.
The original artifacts remain under `data/asset_provenance/baselines/stage0-windows/`;
the current ledger is explicitly restated under `raw-bytes-posix-lexical-v1`.
See `research/experiment_reports/2026-10-04-ci-portability-repair.md` and
`data/asset_provenance/portability_restatement_stage0.json` for measured deltas.

## Sources

- `research/decision_records/0061-portable-provenance-and-ci-evidence.md`
