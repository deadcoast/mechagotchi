# Mecha Engine Package Scaffold Creation

Date: 2026-07-04

## Goal

Execute the package-creation step that decision record 0004 authorized and the
scaffold verification gate specified: create the empty `packages/mecha_engine`
scaffold, prove the acceptance checklist with an executable lab, and rerun
every gate that observed package absence — without moving or copying any lab
implementation.

## What Was Created

- `packages/mecha_engine/` — src-layout scaffold exactly per decision record
  0004: `pyproject.toml` (name `mecha-engine`, version `0.0.0`,
  `requires-python`, `[build-system]`, no release license metadata),
  `README.md`, `src/mecha_engine/__init__.py`, `src/mecha_engine/py.typed`,
  docstring-only `__init__.py` for the five initial modules (`genome`,
  `generation`, `lifecycle`, `archive`, `provenance`), and
  `tests/test_package_imports.py`. Deferred modules (`learning`, `repair`,
  `render`, `storage`, `slip`) were not created.
- `labs/architecture/mecha_engine_scaffold_verification_gate.py`
  (+ `test_mecha_engine_scaffold_verification_gate.py`) — executes the
  checklist from
  `research/package_specs/mecha_engine_scaffold_verification_gate.md`
  (required paths, metadata rules, six-target import surface, import
  side-effect freedom, lab-boundary negative checks, placeholder-only source,
  deferred-module absence, package test suite, promotion-gate rerun) and
  regenerates
  `data/architecture/mecha_engine_scaffold_verification_gate_stage0.json`,
  which previously recorded only the gate definition authored while the
  scaffold was absent.

Import mechanics: the verification gate documents an editable-install flow
(`python -m pip install -e .\packages\mecha_engine`). To keep the import tests
runnable without requiring installation, `test_package_imports.py` exercises
every import in a `python -B -c` subprocess whose `PYTHONPATH` points at the
package's own `src` directory (standard src-layout semantics; the installed
surface satisfies the same probe). The test module never mutates the
interpreter module search path, so the documented
`rg -n "from labs|import labs|labs/|labs\\|sys\.path" .\packages\mecha_engine`
scan stays clean.

## Gate Outcomes (before -> after)

- Package promotion gate: `package_root_exists` false -> true;
  `package_root_absent` cleared from every candidate; every candidate keeps
  `target_package_absent` (the registry's target boundaries are module
  surfaces with package-level tests, which the empty scaffold does not
  provide); `promotion_ready_count` stays 0; decision
  `criteria_defined_no_package_promotion` ->
  `criteria_defined_no_ready_candidates` — the gate sees the package root but
  still blocks lab-code promotion, exactly the expected scaffold-stage result.
- Runtime boundary gate: `package_root_exists` false -> true; the lab-boundary
  negative probes now scan the real scaffold tree (7 Python files, zero lab imports,
  zero interpreter-path lab adapters) instead of holding vacuously;
  `package_runtime_integration_ready` now additionally requires the promotion
  gate to report promotion-ready candidates, so it honestly stays false;
  `package_import_surface_tests` moved from blocked to closed at scaffold
  scope (`scaffold_import_surface_tests_passing`, derived from the executed
  scaffold verification artifact) while the new
  `package_contract_surface_tests` blocked state keeps module contracts
  blocked; all 5 negative probes remain rejected.
- Scaffold verification gate: definition-only artifact -> executed evidence;
  9/9 checks pass; decision `accept_empty_package_scaffold`.
- SLIP schema migration gate: `package_root_exists` false -> true (recorded
  observation); all package-scoped dependency/validation states remain
  blocked.

## Verification

```powershell
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
# Ran 7 tests ... OK

python -B .\labs\architecture\mecha_engine_scaffold_verification_gate.py
# "checks_total": 9, "checks_passed": 9, "gate_passed": true,
# "decision": "accept_empty_package_scaffold"

python -B .\labs\package_promotion\package_promotion_gate.py --root . --output-dir .\data\package_promotion
# "package_root_exists": true, "promotion_ready_count": 0

python -B .\labs\architecture\mecha_engine_runtime_boundary_gate.py
# "package_root_exists": true, "package_runtime_integration_ready": false,
# "negative_probe_rejected_count": 5, "scaffold_import_surface_tests_passing": true

rg -n "from labs|import labs|labs/|labs\\|sys\.path" .\packages\mecha_engine
# no matches
rg -n "^def |^class " .\packages\mecha_engine\src\mecha_engine
# no matches
```

Full sweep: 12 lab suites, 481 tests, all OK (474 prior + 7 new architecture
gate tests), plus the 7 new package import tests.

## Limitations

- The scaffold carries no implementation: every module is a docstring-only
  boundary until its contract gate passes (genome first, per the traceability
  matrix test order).
- Release license metadata remains unset pending a license decision record.
- The promotion gate's candidate target paths (`packages/mecha_engine/<module>`)
  predate the src layout; they currently double as the "target boundary with
  package tests is absent" signal and must be revisited when the first module
  contract lands.

## Sources

- `research/decision_records/0004-mecha-engine-package-scaffold.md`
- `research/package_specs/mecha_engine_scaffold_verification_gate.md`
- `research/package_specs/mecha_engine_contract_traceability_matrix.md`
- `research/package_specs/mecha_engine_module_interfaces.md`
- `labs/architecture/mecha_engine_scaffold_verification_gate.py`
- `labs/architecture/mecha_engine_runtime_boundary_gate.py`
- `labs/package_promotion/package_promotion_gate.py`
- `labs/slip_validator/schema_migration_gate.py`
- `data/architecture/mecha_engine_scaffold_verification_gate_stage0.json`
- `data/architecture/mecha_engine_runtime_boundary_gate_stage0.json`
- `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json`
- `data/slips/slip_schema_migration_dependency_gate_stage0.json`
- `packages/mecha_engine/pyproject.toml`
