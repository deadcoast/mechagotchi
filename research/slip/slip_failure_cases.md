# SLIP Schema Failure Cases

Date: 2026-05-12

Status: `research_slip_schema_failure_corpus_no_package_code`

## Purpose

Define the Stage 0 negative profile corpus for the versioned SLIP schema. This
artifact satisfies the research plan's `slip_failure_cases.md` output without
creating package code or claiming final workshop authoring compatibility.

## Scope

The schema artifact is `research/slip/slip.schema.json`.

The executable Stage 0 checker is `labs/slip_validator/slip_validator.py`. It is
a dependency-free structural validator used because the repository defers a
`jsonschema` runtime dependency until a dependency manifest exists. It mirrors the authored schema's
required fields, enums, unit intervals, and additional-property restrictions,
then adds the semantic body-mass order check.

The Pydantic v2 lab model in `labs/slip_validator/pydantic_contract.py` now
validates the same corpus and emits
`research/slip/slip_pydantic_model.schema.json`.

The current validator proves profile payload acceptance and rejection only. It
does not prove behavior preview, mutation preview UI, profile-weighted
evolution, profile migration, or package import-surface behavior.

## Failure Corpus

| Fixture | Primary rejection family | Fault |
| --- | --- | --- |
| `slip_missing_version.json` | `schema_required` | missing `slip_version` |
| `slip_bad_version.json` | `schema_enum` | unsupported `slip_version` |
| `slip_profile_id_type.json` | `schema_type` | non-string `profile_id` |
| `slip_extra_top_level.json` | `schema_additional_properties` | unexpected top-level key |
| `slip_empty_palette_list.json` | `schema_min_items` | empty `grid.allowed_palettes` |
| `slip_unknown_palette.json` | `schema_enum` | unknown palette ID |
| `slip_body_mass_bounds_reversed.json` | `semantic_body_mass_bounds` | `body_mass_max` below `body_mass_min` |
| `slip_unknown_required_role.json` | `schema_enum` | unknown required organ role |
| `slip_missing_mutation_cap.json` | `schema_required` | missing mutation cap |
| `slip_boolean_behavior_weight.json` | `semantic_numeric_bool` | boolean used as numeric weight |
| `slip_behavior_weight_out_of_range.json` | `schema_range` | behavior weight outside `[0, 1]` |
| `slip_survival_extra_key.json` | `schema_additional_properties` | unexpected survival weight |

## Validation Result

The generated report is
`data/slips/slip_schema_validation_stage0.json`.

Observed result:

```txt
valid profiles accepted: 3/3
research examples accepted: 3/3
failure cases rejected: 12/12
unexpected rejections: 0
unexpected acceptances: 0
```

Observed error families:

- `schema_additional_properties`
- `schema_enum`
- `schema_min_items`
- `schema_range`
- `schema_required`
- `schema_type`
- `semantic_body_mass_bounds`
- `semantic_numeric_bool`

## Blocked States

The following claims remain blocked:

- runtime JSON Schema validation, because the dependency selection is not made;
- Pydantic package dependency declaration, because no repository dependency
  manifest exists;
- behavior preview and mutation preview UI, because this is a file-corpus
  validator only.

## Verification

```powershell
python -B -m unittest discover -s .\labs\slip_validator -p "test_*.py"
python -B .\labs\slip_validator\slip_validator.py --valid-dir .\data\slips\valid --failure-dir .\data\slips\failure_cases --examples-dir .\research\slip\slip_examples --output .\data\slips\slip_schema_validation_stage0.json
python -m json.tool .\research\slip\slip.schema.json
python -m json.tool .\data\slips\slip_schema_validation_stage0.json
```

## References

- `docs/02-research_plan.md`
- `research/slip/slip.schema.json`
- `research/slip/slip_examples/`
- `labs/slip_validator/slip_validator.py`
- `labs/slip_validator/pydantic_contract.py`
- `labs/slip_validator/schema_migration_gate.py`
- `labs/slip_validator/test_slip_validator.py`
- `labs/slip_validator/test_pydantic_contract.py`
- `labs/slip_validator/test_schema_migration_gate.py`
- `data/slips/failure_cases/`
- JSON Schema Draft 2020-12: https://json-schema.org/draft/2020-12
- Pydantic JSON Schema docs: https://docs.pydantic.dev/latest/concepts/json_schema/

## 2026-10-04: Mechanics corpus extension (DR 0063)

The v0.2 mechanics rung adds one valid opt-in and one invalid numeric-boolean
fixture: current census **5 valid / 15 malformed / 5 examples**. Historical
counts and blocked-state observations above describe their dated studies.
The authored schema, Pydantic model, generated schema, package authority and
both lab validators now agree on the 32-case strict mechanics matrix.
An absent/empty/false block is off; null, unknown keys and non-booleans fail;
v0.1 rejects the block. The generated schema explicitly represents the null
and version rules that model validators do not emit. Its committed body is
pinned against current generation. Original observations are not overwritten.

## Sources

- `research/decision_records/0063-covenant-mechanics-authorship.md`
- `research/experiment_reports/2026-10-04-slip-mechanics-authorship.md`
- `data/slips/mechanics_cases_stage0.json`
- `labs/slip_validator/test_mechanics_contract.py`
