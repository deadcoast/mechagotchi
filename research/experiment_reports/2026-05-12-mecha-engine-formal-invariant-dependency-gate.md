# Experiment Report: Mecha Engine Formal Invariant Dependency Gate

Date: 2026-05-12

## Objective

Continue the package-contract handoff by defining the formal cross-module
invariants, dependency order, and failure-propagation rules that the future
`mecha_engine` package must preserve.

## Method

1. Re-read the research plan and brainstorming notes.
2. Re-read the current package spec index and kickoff ledger.
3. Rechecked package absence with `Test-Path .\packages`.
4. Reviewed the existing grid invariants, module interfaces, contract
   traceability matrix, and concrete fixture manifest.
5. Queried external primary sources for terminology anchors: JSON Schema Draft
   2020-12, Python `jsonschema` validation docs, MAP-Elites, Wave Function
   Collapse, and SPDX license expression/list documentation.
6. Converted the existing package-contract gates into a cross-module formal
   admissibility chain and machine-readable JSON artifact.

## Outputs

- `research/package_specs/mecha_engine_formal_invariant_dependency_gate.md`
- `data/architecture/mecha_engine_formal_invariant_dependency_gate_stage0.json`

## Findings

The research chain has enough evidence to define a stronger package handoff
rule than isolated module acceptance:

```txt
V(G).ok
  -> generation may use G as a parent
  -> generation returns C
  -> V(C.grid).ok
  -> lifecycle may simulate C.grid
  -> lifecycle returns finite bounded E
  -> archive may derive D and F from C and E
  -> archive may update A
  -> provenance R must be ok before package promotion
```

The key risk is not missing a module interface. The key risk is a future module
consuming a state that was valid only inside a lab context, then treating that
state as package-ready. The formal gate prevents that by making upstream
validation and trace preservation mandatory.

## Blocked States

These remain explicitly blocked:

- package implementation, because `packages/` is absent and this step is
  research-only;
- human-calibrated readability thresholds, because
  `data/readability/manual_ratings.csv` is absent;
- real CuBFF adoption, because no real upstream or local snapshot artifacts
  were available;
- online reward-shaping promotion, because it has not beaten the frozen
  baseline under the required dynamic stress gate;
- release license metadata, because the package root and license decision
  records are not yet present.

## Decision

Adopt the formal invariant/dependency gate as the next package-handoff layer.
Do not create `packages/mecha_engine` or package tests in this research step.

Status: `research_formal_invariant_dependency_gate_no_package_code`

## Verification Plan

Research-step verification:

```powershell
python -m json.tool .\data\architecture\mecha_engine_formal_invariant_dependency_gate_stage0.json
Test-Path .\packages
rg -n "mecha_engine_formal_invariant_dependency_gate|research_formal_invariant_dependency_gate_no_package_code" .\research .\data
git diff --check
```

Future package verification, valid only after package implementation begins:

```powershell
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
rg -n "from labs|import labs|labs/|labs\\|sys\.path" .\packages\mecha_engine
python -B .\labs\package_promotion\package_promotion_gate.py --root . --output-dir .\data\package_promotion
```

## References

- `docs/01-brainstorming.md`
- `docs/02-research_plan.md`
- `research/grid_genome/grid_invariants.md`
- `research/package_specs/mecha_engine_module_interfaces.md`
- `research/package_specs/mecha_engine_contract_traceability_matrix.md`
- `research/package_specs/mecha_engine_test_fixture_manifest.md`
- `data/architecture/mecha_engine_contract_traceability_matrix_stage0.json`
- `data/architecture/mecha_engine_test_fixture_manifest_stage0.json`
