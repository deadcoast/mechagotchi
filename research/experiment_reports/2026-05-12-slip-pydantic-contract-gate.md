# Experiment Report: SLIP Pydantic Contract Gate

Date: 2026-05-12

## Objective

Continue the SLIP research track by selecting and testing the Python model path
from the compatibility matrix's next step: runtime schema/Pydantic model
selection before minimal profile-authoring panel work.

## Method

1. Re-read `docs/02-research_plan.md`,
   `research/slip/profile_compatibility_tests.md`, and the Stage 0 schema
   failure-corpus report.
2. Queried current Pydantic v2 documentation through Context7 and web search.
3. Queried current Python `jsonschema` documentation through Context7 and web
   search.
4. Measured local dependency availability. Pydantic is available at `2.12.5`;
   `jsonschema` is not installed; no repository dependency manifest exists.
5. Wrote a failing Pydantic contract test before adding implementation.
6. Added a lab-only Pydantic model that accepts current valid profiles and
   examples, rejects the expanded failure corpus, emits JSON Schema, and writes
   a machine-readable contract report.

## Outputs

- `labs/slip_validator/pydantic_contract.py`
- `labs/slip_validator/test_pydantic_contract.py`
- `research/slip/pydantic_contract.md`
- `research/slip/slip_pydantic_model.schema.json`
- `data/slips/slip_pydantic_contract_stage0.json`

## Result

```txt
Pydantic available: yes, 2.12.5
jsonschema available: no
valid profiles accepted: 3/3
research examples accepted: 3/3
failure cases rejected: 12/12
unexpected acceptances/rejections: 0
```

The generated schema preserves the Stage 0 contract shape: required top-level
fields, extra-forbid objects, palette enum, organ-role enum, required mutation
caps, required behavior weights, and required survival weights.

An additional numeric-string coercion check rejects string payload values before
Pydantic can convert them, matching the authored JSON Schema type boundary.

## Interpretation

The Pydantic-backed lab contract is now proven for the current Stage 0 corpus.
This closes the earlier "Pydantic model generation" gap at lab level.

This does not close runtime JSON Schema validation, package dependency
declaration, behavior preview, mutation preview, or profile-weighted evolution.
Supersession note: schema migration is covered by
`research/experiment_reports/2026-05-12-slip-schema-migration-dependency-gate.md`,
and the minimal profile-authoring panel is covered by
`research/experiment_reports/2026-05-12-slip-authoring-panel.md`.

## Decision

Use Pydantic v2 as the current Python model candidate for SLIP authoring and
validation. Keep the dependency-free validator as a runtime fallback until the
future package dependency manifest explicitly declares Pydantic and decides
whether `jsonschema` is required.

Status: `research_slip_pydantic_contract_no_package_code`

## Verification

```powershell
python -B -m unittest discover -s .\labs\slip_validator -p "test_pydantic_contract.py"
python -B .\labs\slip_validator\pydantic_contract.py
```

## References

- `docs/02-research_plan.md`
- `research/slip/profile_compatibility_tests.md`
- `research/slip/slip.schema.json`
- `research/slip/slip_failure_cases.md`
- `research/slip/pydantic_contract.md`
- `data/slips/slip_pydantic_contract_stage0.json`
- Pydantic JSON Schema docs: https://docs.pydantic.dev/latest/concepts/json_schema/
- Pydantic models docs: https://docs.pydantic.dev/latest/concepts/models/
- Python jsonschema validation docs: https://python-jsonschema.readthedocs.io/en/v4.22.0/validate/
