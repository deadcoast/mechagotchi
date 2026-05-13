# Experiment Report: Mecha Engine Provenance Contract Gate

Date: 2026-05-12

## Objective

Define the acceptance contract for the future `mecha_engine.provenance`
package module before moving provenance CI code out of `labs/asset_pipeline`.

## Method

1. Re-read the research plan's asset provenance and package-promotion sections.
2. Re-read the `mecha_engine` module interface spec.
3. Re-read the provenance CI algorithm card, ledger schema, experiment report,
   lab source, lab tests, ledger, CI report, and attribution manifest.
4. Checked official SPDX and REUSE references for expression syntax,
   identifier lists, and file-level licensing expectations.
5. Wrote a prose gate and a machine-readable architecture artifact.

## Outputs

- `research/package_specs/mecha_engine_provenance_contract_gate.md`
- `data/architecture/mecha_engine_provenance_contract_gate_stage0.json`

## Findings

The provenance package boundary must preserve the deterministic CI shape:

```txt
ledger + repo_root
  -> validate required fields
  -> parse SPDX expressions
  -> verify included hashes
  -> enforce review and decision-record policy
  -> emit CI report and attribution manifest
```

The current Stage 0 report is clean:

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

The lab test suite covers the critical negative paths: missing included hashes,
unknown license identifiers, lowercase operator rejection under current project
policy, and risky included share-alike or copyleft assets without
decision-record metadata.

The required public surface is:

```python
from mecha_engine.provenance import (
    build_ci_report,
    generate_attribution_manifest,
    hash_included_path,
    parse_spdx_expression,
    validate_ledger,
)
```

The package-facing `build_ci_report` name intentionally avoids exposing the
lab-specific `build_provenance_ci_report` name.

SPDX version drift is explicit in the gate. The Stage 0 parser follows the
project's current uppercase-operator policy, rooted in the v2.2.2 expression
grammar and lab tests. SPDX 3.0.1 allows lower-case operator forms, so accepting
them later requires an explicit schema and test revision rather than silent
behavior drift.

## Decision

Adopt the provenance contract gate as the package acceptance checklist for the
future `mecha_engine.provenance` module. Do not create `packages/mecha_engine`
in this research step.

Status: `research_provenance_contract_gate_no_package_code`

## Verification Targets

These checks are valid after package implementation begins:

```powershell
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
python -c "from mecha_engine.provenance import parse_spdx_expression, validate_ledger, build_ci_report, generate_attribution_manifest, hash_included_path"
rg -n "from labs|import labs|labs/|labs\\|sys\\.path" .\packages\mecha_engine
python -B .\labs\package_promotion\package_promotion_gate.py --root . --output-dir .\data\package_promotion
```

This research step only verifies the new gate artifacts and existing
provenance lab evidence.

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
