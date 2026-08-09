# Mechagotchi Research Report v0.4

Date: 2026-05-12

## Executive Summary

The post-v0.3 research sequence completes the package-design handoff without
crossing into premature implementation. Mechagotchi now has module interface
specs for the first engine package surfaces, a rechecked human-readability
blocker, dynamic switchboard feedback stress evidence, a less-assisted repair
comparison against the assisted CA/NCA baseline, and an accepted package
scaffold decision.

The main conclusion remains conservative: the project is ready for a small
explicit package scaffold step, not lab-code migration. `packages/mecha_engine`
still does not exist, human readability ratings are still absent, dynamic
reward shaping does not beat the frozen baseline, and learned role-prior repair
does not beat the assisted target-template repair benchmark.

The next implementation boundary is intentionally narrow:

```txt
packages/mecha_engine/
  pyproject.toml
  src/mecha_engine/
    genome/
    generation/
    lifecycle/
    archive/
    provenance/
  tests/test_package_imports.py
```

## Research Scope

This report consolidates the v0.3 follow-up sequence:

1. Create package module interface specs for `genome`, `generation`,
   `lifecycle`, `archive`, and `provenance`.
2. Recheck whether real human readability ratings exist.
3. Stress switchboard feedback under changing needs and user-interaction
   patterns.
4. Compare a less-assisted learned repair rule against the assisted CA/NCA
   repair baseline.
5. Produce a package-scaffold decision record before creating
   `packages/mecha_engine`.

## Primary Artifacts

| Area | Artifact |
| --- | --- |
| Module interface specs | `data/architecture/mecha_engine_module_interface_specs_stage0.json` |
| Manual rating recheck | `data/readability/manual_rating_recheck_stage0.json` |
| Dynamic switchboard stress | `data/micro_learners/switchboard_feedback_dynamic_stress_stage0.json` |
| Learned repair comparison | `data/cellular_automata/ca_nca_learned_repair_comparison_stage0.json` |
| Package scaffold decision | `data/architecture/mecha_engine_package_scaffold_decision_stage0.json` |
| Package scaffold ADR | `research/decision_records/0004-mecha-engine-package-scaffold.md` |
| Package module specs | `research/package_specs/mecha_engine_module_interfaces.md` |

## Experiment Results

| Experiment | Result | Decision |
| --- | ---: | --- |
| Module interface specs | 5 modules specified; package root absent | Interface spec only; no package code |
| Manual rating recheck | `manual_ratings.csv` absent | Block human calibration |
| Dynamic switchboard stress | 3 scenarios; 6 dynamic events; mean need-balance delta `-0.002226`; no survival delta | Watch reward shaping |
| Learned repair comparison | 8 samples; 5 cycles each; learned validity `1.0`; learned final overlap `0.778563`; assisted final overlap `1.0` | Watch learned repair |
| Package scaffold decision | `src` layout accepted; package creation deferred | Create scaffold only when explicitly authorized |

## Decisions

### Adopt

- Package module interface specs for the first five engine surfaces.
- `src/mecha_engine` layout for the future package scaffold.
- `pyproject.toml` as the future package metadata boundary.
- Empty package scaffold as the next allowed implementation step when
  explicitly authorized.

### Prototype

- Dynamic switchboard stress suite as a harder feedback benchmark.
- Less-assisted role-prior repair as a comparison baseline.

### Watch

- Dynamic reward shaping. It updates under changing scenarios but does not
  clearly beat the frozen baseline.
- Learned repair. It is valid and less assisted, but trails the
  target-template baseline by `0.221437` final overlap.

### Blocked

- Human readability calibration, because no filled reviewer CSV exists.
- Package promotion, because `packages/mecha_engine` still does not exist and
  no lab implementation has package-level tests.

## Package Design Handoff

The package scaffold decision resolves the physical package shape:

```txt
packages/mecha_engine/
  pyproject.toml
  README.md
  src/
    mecha_engine/
      __init__.py
      py.typed
      genome/
      generation/
      lifecycle/
      archive/
      provenance/
  tests/
    test_package_imports.py
```

The distribution package name should be `mecha-engine`; the import package name
should be `mecha_engine`.

The first scaffold step must not move lab code. It may only create package
metadata, package directories, type-marker plumbing, README text, and import
surface tests.

## Risks

- Human readability ratings remain the largest evidence gap.
- Reward shaping remains lab-only and should not be production behavior.
- Learned repair is less assisted but not competitive enough for package
  promotion.
- Package creation is not the same as package promotion; lab code still needs
  package-level tests before migration.
- License metadata for the future Python package should remain deferred until
  the repository/package license decision is explicit.

## Next Research Sequence

1. Create the empty `packages/mecha_engine` `src`-layout scaffold only when the
   user explicitly starts package implementation.
2. Add import-surface tests that import `mecha_engine`, not `labs`.
3. Re-run the package-promotion gate after the scaffold exists.
4. Begin package implementation with `genome` contracts and validation tests.
5. Collect real human readability ratings in
   `data/readability/manual_ratings.csv`.

## Publication Status

This is an internal research publication. It completes the v0.3 follow-up
sequence and defines the narrow, auditable handoff from research into package
scaffolding.

## External References

- Python Packaging User Guide, `src` layout vs flat layout:
  `https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/`
- Python Packaging User Guide, `pyproject.toml` specification:
  `https://packaging.python.org/en/latest/specifications/pyproject-toml/`

---
