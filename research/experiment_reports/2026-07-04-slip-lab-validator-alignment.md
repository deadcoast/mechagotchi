# SLIP Lab Validator Alignment

Date: 2026-07-04

Status: `research_slip_lab_validator_alignment_no_package_code`

## Purpose

Fix review findings H-02, M-05, and M-06 from
`docs/03-code_review/2026-07-04-code_review.md`: the lightweight SLIP
validator in `labs/grid_genome/slip.py` — which gates seed selection through
`constrained_generator._filter_seed_pool` and grid↔profile alignment through
`is_grid_aligned` — had drifted from the authoritative contract
(`labs/slip_validator/slip_validator.py` + `research/slip/slip.schema.json`)
and accepted profiles the contract rejects.

## Drift evidence (RED)

Running both validators over the full Stage 0 corpus at commit `61c0f28`
found two failure cases accepted by the lab validator and rejected by the
authoritative one:

```txt
case                                    grid_genome  authoritative
slip_extra_top_level.json               ok=True      ok=False   <-- DISAGREE
slip_survival_extra_key.json            ok=True      ok=False   <-- DISAGREE
(other 10 failure cases, 3 valid, 3 examples: agree)
```

Additional latent drift (H-02/M-05/M-06 surfaces not present in the corpus):

- missing `behavior`/`survival_weights` keys were accepted (only present keys
  were range-checked);
- `True`/`False` were accepted as body-mass integers (`bool` is a subclass of
  `int`);
- `profile_id` pattern (`^[a-z0-9_]+$`) was unenforced;
- duplicate `allowed_palettes` / `required_organ_roles` entries were accepted;
- `is_grid_aligned` raised an untyped `TypeError` on non-numeric grid mutation
  values instead of reporting an alignment error.

## What changed

`labs/grid_genome/slip.py`:

1. Exact key-set enforcement (required + no extras) for the top level, `grid`,
   `mutation`, `behavior`, and `survival_weights`, mirroring the authored
   schema's `required` + `additionalProperties: false`.
2. Boolean rejection for body-mass bounds; `profile_id` pattern check;
   duplicate-item rejection in palette and organ-role arrays.
3. `is_grid_aligned` validates grid mutation values are numeric (and not bool)
   before comparing against SLIP caps, reporting a typed error string instead
   of crashing.

`labs/grid_genome/test_slip_constraints.py` adds:

- a cross-validator agreement test asserting `validate_slip` and the
  authoritative `validate_profile` agree on all 3 valid + 12 failure + 3
  example profiles;
- negative tests for extra/missing section keys, boolean body mass, duplicate
  palettes, and bad `profile_id`;
- rejection-path tests for each `is_grid_aligned` surface (palette, body
  mass, required role, mutation cap) — previously only the accept path was
  asserted (review finding L-01, first half);
- non-numeric / boolean grid mutation probes proving the typed-error path.

## Result (GREEN)

```powershell
python -B -m unittest discover -s labs/grid_genome -p "test_*.py"
# Ran 48 tests in 0.615s
# OK  (was 42 tests before this change)
```

All twelve lab suites re-run green after the change — the stricter contract
rejected nothing in-tree, confirming every committed profile and generated
corpus was already exact-key-conformant.

## Decision

The lab validator now agrees with the authoritative contract across the whole
Stage 0 corpus, and the agreement is pinned by a test so future drift fails
the suite. The three-validator duplication itself (`slip.py`,
`slip_validator.py`, `pydantic_contract.py`) remains tracked as review
finding L-04; this change aligns behavior without consolidating modules.

## Verification

```powershell
python -B -m unittest discover -s labs/grid_genome -p "test_*.py"
python -B -m unittest discover -s labs/slip_validator -p "test_*.py"
python -B -m unittest discover -s labs/workshop_editor -p "test_*.py"
```

## Sources

- `docs/03-code_review/2026-07-04-code_review.md`
- `labs/grid_genome/slip.py`
- `labs/grid_genome/test_slip_constraints.py`
- `labs/slip_validator/slip_validator.py`
- `research/slip/slip.schema.json`
- `data/slips/failure_cases/`
- `research/experiment_reports/2026-05-12-slip-constraint-baseline.md`
