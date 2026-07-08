# Mecha Engine Scaffold Verification Gate

Date: 2026-05-12

## Status

Research verification gate. This document does not create `packages/mecha_engine`.

## Purpose

Define the exact acceptance checks for the first empty
`packages/mecha_engine` scaffold so package creation stays narrow, auditable,
and separate from lab-code promotion.

## Preconditions

- `research/decision_records/0004-mecha-engine-package-scaffold.md` is
  accepted.
- The user explicitly starts package implementation.
- `packages/mecha_engine` is absent before the scaffold step begins.
- No lab implementation is moved during scaffold creation.

## Required Scaffold Shape

```txt
packages/mecha_engine/
  pyproject.toml
  README.md
  src/
    mecha_engine/
      __init__.py
      py.typed
      genome/
        __init__.py
      generation/
        __init__.py
      lifecycle/
        __init__.py
      archive/
        __init__.py
      provenance/
        __init__.py
  tests/
    test_package_imports.py
```

## Metadata Acceptance

(Amended 2026-07-07, decision record 0028: the license decision now
EXISTS — Apache-2.0, declared in `pyproject.toml` `license` /
`license-files` pointing at the root `LICENSE`. The former
"license metadata stays unset" rule is closed. The same record permits
third-party `[project]` dependencies when a capability needs one.)

`pyproject.toml` must define:

- `[build-system]`
- `[project]`
- `name = "mecha-engine"`
- a pre-release/internal version such as `0.0.0`
- `requires-python`

`pyproject.toml` must declare `license = "Apache-2.0"` and
`license-files = ["../../LICENSE"]` (decision record 0028; before that
record, this rule was the inverse — no release license metadata until
the decision was explicit).

## Import Acceptance

The package import surface must work through `mecha_engine`, not `labs`.

Required import targets:

- `mecha_engine`
- `mecha_engine.genome`
- `mecha_engine.generation`
- `mecha_engine.lifecycle`
- `mecha_engine.archive`
- `mecha_engine.provenance`

The initial import tests must not mutate `sys.path` to point at `labs/`.

## Negative Checks

The scaffold is rejected if any of these are true:

- Package code imports `labs`.
- Package tests import `labs`.
- Package code contains non-placeholder implementation copied from `labs/`.
- The scaffold creates `learning`, `render`, `storage`, or `slip` modules
  before the first package boundary is verified. (`repair` left this list
  on 2026-07-05: decision record 0006 authorized its target after the
  wound-site stability blocker cleared; the executable gate tracks the
  current deferred set. `storage` left the deferred set on 2026-07-07:
  decision record 0022 authorized the target, the `campaign_store` lab's
  eight gates went green, and the C3 port shipped. `slip` left on
  2026-07-07: decision record 0027 authorized the target and the F2 port
  collapsed the four private mirrors after gate-1 reconciliation
  measured zero divergences. The remaining deferred set is `render`
  alone — dispositioned REJECTED-until-consumer by decision record
  0026, with its re-opener named.)
- The package metadata's license declaration does not match decision
  record 0028 (Apache-2.0 via the root `LICENSE`).
- The package-promotion gate is not rerun after scaffold creation.

## Future Verification Commands

Run these after scaffold creation:

```powershell
Test-Path .\packages\mecha_engine
Test-Path .\packages\mecha_engine\pyproject.toml
Test-Path .\packages\mecha_engine\src\mecha_engine\__init__.py
python -m pip install -e .\packages\mecha_engine
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
python -c "import mecha_engine, mecha_engine.genome, mecha_engine.generation, mecha_engine.lifecycle, mecha_engine.archive, mecha_engine.provenance"
rg -n "from labs|import labs|labs/|labs\\|sys\\.path" .\packages\mecha_engine
rg -n "^def |^class " .\packages\mecha_engine\src\mecha_engine
python -B .\labs\package_promotion\package_promotion_gate.py --root . --output-dir .\data\package_promotion
git diff --check
```

Expected scaffold-stage result:

- Import tests pass.
- `rg` finds no `labs` imports or `sys.path` package-test bypasses.
- The implementation-code scan finds no non-placeholder functions/classes.
- The package-promotion gate sees the package root but still blocks lab-code
  promotion until target package tests and candidate-specific blockers are
  satisfied.

## Research Sources

- `research/decision_records/0004-mecha-engine-package-scaffold.md`
- `research/reports/mechagotchi_research_report_v0_4.md`
- `data/architecture/mecha_engine_package_scaffold_decision_stage0.json`
- `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json`

## External Standards

- Python Packaging User Guide, `src` layout vs flat layout:
  https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/
- Python Packaging User Guide, `pyproject.toml` specification:
  https://packaging.python.org/en/latest/specifications/pyproject-toml/

