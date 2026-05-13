# Decision Record 0004: Mecha Engine Package Scaffold

Date: 2026-05-12

## Status

Accepted as package-scaffold design. Package creation is deferred.

## Context

The v0.3 research report requires a package-scaffold decision record before
creating `packages/mecha_engine`. The current repository still has no
`packages/` directory and no `packages/mecha_engine` package root.

The package-promotion gate found zero promotion-ready candidates because the
package root and target package boundaries are absent. The MVP architecture and
module interface specs define the intended engine boundary, but they do not
authorize moving lab code into package code.

Current packaging guidance supports a `src` layout for importable Python code
because it helps tests exercise the installed package surface instead of
accidentally importing repository-root files. Current `pyproject.toml` guidance
also makes `[build-system]` and `[project]` metadata the modern package metadata
boundary.

## Decision

Adopt the following scaffold design for the first package-creation step:

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

The distribution package name should be `mecha-engine`; the import package name
should be `mecha_engine`.

The first scaffold may include package metadata, empty module boundaries,
type-marker plumbing, README text, and import-surface tests. It must not move
or copy lab implementations from `labs/` into `packages/`.

Initial modules:

- `genome`
- `generation`
- `lifecycle`
- `archive`
- `provenance`

Deferred modules:

- `learning`
- `repair`
- `render`
- `storage`
- `slip`

The first package implementation after scaffolding should start with stable
contracts and tests for `genome`, then add generation, lifecycle, archive, and
provenance surfaces only when each surface has package-level tests.

## Package Metadata Rules

- Use `pyproject.toml` as the package metadata boundary.
- Prefer static metadata where known.
- Keep release license metadata unset until the repository/package license is
  selected and provenance checks confirm release readiness.
- Keep the package private/internal until provenance and promotion gates are
  satisfied.
- Use absolute imports from `mecha_engine`.
- Tests must import through the package surface, not through `labs/`.

## Creation Gate

This decision authorizes the scaffold shape, not immediate creation. The package
root should be created only in an implementation step that explicitly creates
the scaffold and verifies:

1. `packages/mecha_engine/pyproject.toml` exists.
2. `packages/mecha_engine/src/mecha_engine/__init__.py` imports.
3. Package tests exercise `mecha_engine`, not `labs`.
4. No lab implementation code is moved during scaffold creation.
5. The package-promotion gate is re-run after the scaffold exists.
6. Provenance/release metadata remains blocked until a package license decision
   exists.

## Consequences

- The package boundary can be created without prematurely promoting research
  labs.
- Future tests can verify the installed import package rather than root-path
  imports.
- Package creation becomes a small, auditable step instead of a broad migration.
- Research-only systems remain in `labs/` until they clear their own gates.
- The first package should stay engine-core focused and defer learning/repair
  modules until current blockers are resolved.

## Evidence

- `docs/02-research_plan.md`
- `research/reports/mechagotchi_research_report_v0_3.md`
- `research/decision_records/0002-mecha-engine-package-promotion-gate.md`
- `research/decision_records/0003-mvp-architecture.md`
- `research/package_specs/mecha_engine_module_interfaces.md`
- `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json`
- `data/architecture/mecha_engine_module_interface_specs_stage0.json`

## External References

- Python Packaging User Guide, `src` layout vs flat layout:
  https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/
- Python Packaging User Guide, `pyproject.toml` specification:
  https://packaging.python.org/en/latest/specifications/pyproject-toml/

