# Experiment Report: Asset Provenance Ledger Baseline

Date: 2026-05-12

## Objective

Continue the research plan by turning the asset provenance ledger from a schema
note into a testable workflow that can block untracked or risky assets before
they enter shipping paths.

## Source Basis

The provenance policy is anchored in SPDX identifiers, REUSE-style file-level
licensing practice, Creative Commons license distinctions, and OpenGameArt's
warnings that game art licensing must be checked per asset and derivative.

Sources:

- https://spdx.org/licenses/
- https://reuse.software/spec-3.3/
- https://creativecommons.org/cc-licenses/
- https://opengameart.org/content/faq

## Scope

Included:

- `labs/asset_pipeline/provenance_ledger.py`
- `labs/asset_pipeline/test_provenance_ledger.py`
- deterministic file and directory-tree hashing
- required-field validation
- SPDX identifier policy for the current research set
- reference-only external source handling
- share-alike and noncommercial core-asset gates
- attribution manifest generation
- Stage 0 ledger artifacts under `data/asset_provenance/`

Not included:

- full SPDX expression parser
- REUSE.toml generation
- CI integration
- legal review workflow
- third-party asset import UI
- automatic scanning of every repository file

## Verification

RED command:

```powershell
python -m unittest discover -s labs\asset_pipeline -p 'test_*.py'
```

Initial result:

```txt
ModuleNotFoundError: No module named 'provenance_ledger'
```

GREEN command:

```powershell
python -m unittest discover -s labs\asset_pipeline -p 'test_*.py'
```

Result:

```txt
Ran 7 tests in 0.062s
OK
```

Lab command:

```powershell
python labs\asset_pipeline\provenance_ledger.py --output-dir data\asset_provenance
```

Result:

```json
{
  "ok": true,
  "errors": [],
  "warnings": [],
  "summary": {
    "asset_count": 7,
    "included_count": 3,
    "reference_only_count": 4,
    "attribution_required_count": 3
  }
}
```

## Stage 0 Ledger Contents

Included internal research artifacts:

- `internal_seed_grid_corpus_v1`
- `cubff_synthetic_snapshot_corpus_stage0`
- `workshop_editor_stage0_export`

External reference-only sources:

- `piskel_reference_only`
- `pixelorama_reference_only`
- `libresprite_reference_only`
- `opengameart_policy_reference`

## Findings

The ledger can now distinguish included internal research artifacts from
external references. Included artifacts require deterministic hashes and existing
paths. External references remain outside repository payloads unless later
approved with explicit license and attribution handling.

The policy gate correctly rejects a share-alike asset marked for `core` shipping
without a decision record. That is the important safety behavior for future LPC,
OpenGameArt, or editor-derived experiments.

## Decision

Adopt the Stage 0 provenance ledger for research artifacts.

Do not import third-party visual assets into core paths until the ledger is
extended with CI scanning, SPDX expression parsing, and a decision-record link
for any share-alike or copyleft asset.


## Correction, 2026-10-04: checkout portability

The original local provenance pass did not prove fresh-checkout portability.
DR 0061 identifies the working-tree line-ending and native-path-sort assumptions.
The original artifacts remain under `data/asset_provenance/baselines/stage0-windows/`;
the current ledger is explicitly restated under `raw-bytes-posix-lexical-v1`.
See `research/experiment_reports/2026-10-04-ci-portability-repair.md` and
`data/asset_provenance/portability_restatement_stage0.json` for measured deltas.

## Sources

- `research/decision_records/0061-portable-provenance-and-ci-evidence.md`
