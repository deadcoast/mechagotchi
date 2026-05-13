# Experiment Report: Mecha Engine Property and Negative Test Strategy

Date: 2026-05-12

## Objective

Continue the package-contract research handoff by defining how future
`mecha_engine` package tests should prove formal invariants through fixture
regression, single-fault negative tests, property-style checks, metamorphic
checks, and cross-module failure propagation.

## Method

1. Re-read `docs/02-research_plan.md` for the research loop, grid invariants,
   testability requirements, and evaluation framework.
2. Re-read the current package spec index, kickoff ledger, traceability matrix,
   fixture manifest, and formal invariant/dependency gate.
3. Rechecked package absence with `Test-Path .\packages`.
4. Queried current testing documentation: Python `unittest`, Hypothesis, and
   Python `jsonschema`.
5. Defined future test families and oracles without creating package code,
   package tests, package dependencies, or `packages/`.

## Outputs

- `research/package_specs/mecha_engine_property_negative_test_strategy.md`
- `data/architecture/mecha_engine_property_negative_test_strategy_stage0.json`

## Findings

The current package-contract handoff already defines module surfaces, fixture
corpora, and invariant dependencies. The missing layer was adversarial test
design:

```txt
fixtures + invariants -> future test generators + future oracles
```

The most important strategy choice is to derive negative cases from accepted
fixtures one fault at a time. That preserves clear failure attribution:

```txt
valid seed grid
  -> one structural corruption
  -> expected rejection family
```

This avoids the weak pattern of testing only existing examples that happen to
pass.

## Decision

Adopt the property and negative test strategy as a package-handoff artifact.
The first package test suite remains `unittest`-runnable. Hypothesis is useful
for future property-based broadening, but it is not a required dependency until
a future package dependency decision explicitly adds it.

Status: `research_property_negative_test_strategy_no_package_code`

## Blocked States

These states remain blocked:

- package implementation and package tests, because `packages/` is absent and
  this step is research-only;
- Hypothesis as a required gate, because no package/dev dependency decision
  exists yet;
- human-calibrated readability tests, because
  `data/readability/manual_ratings.csv` is absent;
- real CuBFF adoption tests, because real snapshot artifacts are absent;
- online reward-shaping promotion, because the required dynamic stress gate has
  not been beaten;
- release license metadata tests, because the package and explicit license
  decision records do not exist.

## Verification Plan

Research-step verification:

```powershell
python -m json.tool .\data\architecture\mecha_engine_property_negative_test_strategy_stage0.json
Test-Path .\packages
rg -n "mecha_engine_property_negative_test_strategy|research_property_negative_test_strategy_no_package_code" .\research .\data
git diff --check
```

Future package verification, valid only after package implementation begins:

```powershell
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
python -c "import mecha_engine, mecha_engine.genome, mecha_engine.generation, mecha_engine.lifecycle, mecha_engine.archive, mecha_engine.provenance"
rg -n "from labs|import labs|labs/|labs\\|sys\.path" .\packages\mecha_engine
python -B .\labs\package_promotion\package_promotion_gate.py --root . --output-dir .\data\package_promotion
git diff --check
```

## References

- `docs/01-brainstorming.md`
- `docs/02-research_plan.md`
- `research/package_specs/mecha_engine_module_interfaces.md`
- `research/package_specs/mecha_engine_contract_traceability_matrix.md`
- `research/package_specs/mecha_engine_test_fixture_manifest.md`
- `research/package_specs/mecha_engine_formal_invariant_dependency_gate.md`
- `data/architecture/mecha_engine_contract_traceability_matrix_stage0.json`
- `data/architecture/mecha_engine_test_fixture_manifest_stage0.json`
- `data/architecture/mecha_engine_formal_invariant_dependency_gate_stage0.json`
