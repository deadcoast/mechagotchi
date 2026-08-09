# Mechagotchi Research Report v0.5

Date: 2026-05-12

## Executive Summary

The post-v0.4 research continuation completes the package-contract handoff for
the first `mecha_engine` surfaces without creating `packages/mecha_engine` and
without moving lab code.

The repository now has research acceptance gates for the scaffold and the five
initial package modules:

- `mecha_engine.genome`
- `mecha_engine.generation`
- `mecha_engine.lifecycle`
- `mecha_engine.archive`
- `mecha_engine.provenance`

The key conclusion is still conservative. The package boundary is now much
more precisely specified, but actual package implementation remains blocked
until the user explicitly starts package work. Human readability calibration is
still blocked because no filled reviewer CSV exists. Package license metadata
is still deferred until the repository/package license decision is explicit.

## Research Scope

This report consolidates the v0.4 follow-up package-contract sequence:

1. Define a scaffold verification gate before creating `packages/mecha_engine`.
2. Define the `mecha_engine.genome` validator contract.
3. Define the `mecha_engine.generation` constrained generator contract.
4. Define the `mecha_engine.lifecycle` bounded simulator contract.
5. Define the `mecha_engine.archive` MAP-Elites archive contract.
6. Define the `mecha_engine.provenance` provenance CI contract.

## Primary Artifacts

| Area | Artifact |
| --- | --- |
| Scaffold gate | `data/architecture/mecha_engine_scaffold_verification_gate_stage0.json` |
| Genome contract | `data/architecture/mecha_engine_genome_contract_gate_stage0.json` |
| Generation contract | `data/architecture/mecha_engine_generation_contract_gate_stage0.json` |
| Lifecycle contract | `data/architecture/mecha_engine_lifecycle_contract_gate_stage0.json` |
| Archive contract | `data/architecture/mecha_engine_archive_contract_gate_stage0.json` |
| Provenance contract | `data/architecture/mecha_engine_provenance_contract_gate_stage0.json` |
| Package specs index | `research/package_specs/README.md` |

## Contract Results

| Surface | Gate Status | Evidence Anchor | Decision |
| --- | --- | ---: | --- |
| Scaffold | `research_verification_gate_no_package_code` | 6 import targets; `src` layout | Scaffold only when explicitly authorized |
| Genome | `research_genome_contract_gate_no_package_code` | 50 seed grids, 200 invalid counterexamples | Adopt validator contract |
| Generation | `research_generation_contract_gate_no_package_code` | constrained validity `100/100`; SLIP-aligned `50/50` | Adopt constrained generator contract |
| Lifecycle | `research_lifecycle_contract_gate_no_package_code` | switchboard survives `72/72`; idle dies at 11; random dies at 21 | Adopt bounded simulator contract |
| Archive | `research_archive_contract_gate_no_package_code` | 29 extended occupied niches; best fitness `0.979592`; QD score `27.773545` | Adopt MAP-Elites contract |
| Provenance | `research_provenance_contract_gate_no_package_code` | 7 assets; 7/7 SPDX expressions parsed; CI `ok: true` | Adopt provenance CI contract |

## Cross-Module Handoff

The package flow is now specified as a contract sequence:

```txt
genome.validate_grid(seed_or_parent)
  -> generation.generate_candidate(...)
  -> genome.validate_grid(candidate)
  -> lifecycle.run_episode(candidate, ...)
  -> archive.score_candidate(candidate, metrics)
  -> archive.insert_candidate(...)
  -> provenance.build_ci_report(...)
  -> genome.render_packet_from_grid(...)
```

The future package surface is intentionally smaller than the full research
space. Online reward shaping, CA/NCA repair, readability calibration, real
CuBFF ingest, workshop editing, SLIP creator UI, render/storage modules, and
release compliance are not promoted by this report.

## Decisions

### Adopt

- The five module contract gates as acceptance checklists for future package
  implementation.
- The scaffold verification gate as the only allowed first package step.
- Package-facing API names that hide lab-specific naming, such as
  `provenance.build_ci_report`.
- `src/mecha_engine` as the future import boundary.
- `pyproject.toml` as the future package metadata file.

### Watch

- Generation remains constrained-generator-first; raw Markov output remains a
  proposal source only.
- Archive descriptors are richer but sparse; observed-niche context must stay
  attached to coverage claims.
- Lifecycle reward feedback remains lab-only because dynamic reward shaping
  has not beaten the frozen baseline.
- SPDX expression policy has version drift: Stage 0 rejects lowercase
  operators, while SPDX 3.0.1 allows lowercase operator forms. Any relaxation
  needs an explicit schema and test revision.

### Blocked

- Package promotion, because `packages/mecha_engine` does not exist.
- Lab-code migration, because package-level tests do not exist.
- Human readability calibration, because `data/readability/manual_ratings.csv`
  is not filled.
- Final archive descriptor thresholds, because human readability calibration is
  absent.
- Release license metadata, because the package/repository license decision is
  not explicit.
- Full provenance release compliance, because REUSE scanning, legal review,
  package license metadata, and SBOM generation are future gates.

## Implementation Boundary

This report does not authorize implementation by itself. The first allowed
implementation step remains the empty scaffold described by the v0.4 report:

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

The scaffold step must create only package metadata, package directories,
type-marker plumbing, README text, and import-surface tests. It must not copy
lab implementations.

## Next Research Sequence

1. Create the empty `packages/mecha_engine` `src`-layout scaffold only when the
   user explicitly starts package implementation.
2. Add import-surface tests that import `mecha_engine`, not `labs`.
3. Re-run the package-promotion gate after the scaffold exists.
4. Begin package implementation with `genome` contracts and validation tests.
5. Keep generation, lifecycle, archive, and provenance implementation behind
   their contract gates.
6. Collect real human readability ratings in
   `data/readability/manual_ratings.csv`.

## Publication Status

This is an internal research publication. It completes the package-contract
handoff sequence and records that the repository is still research-only until
package implementation is explicitly started.

## External References

- Python Packaging User Guide, `src` layout vs flat layout:
  `https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/`
- Python Packaging User Guide, `pyproject.toml` specification:
  `https://packaging.python.org/en/latest/specifications/pyproject-toml/`
- SPDX License Expressions v2.2.2:
  `https://spdx.github.io/spdx-spec/v2.2.2/SPDX-license-expressions/`
- SPDX License Expressions v3.0.1:
  `https://spdx.github.io/spdx-spec/v3.0.1/annexes/spdx-license-expressions/`
- REUSE Specification 3.3:
  `https://reuse.software/spec-3.3/`
