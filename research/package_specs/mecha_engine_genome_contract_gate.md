# Mecha Engine Genome Contract Gate

Date: 2026-05-12

## Status

Research acceptance gate. This document does not create or modify
`packages/mecha_engine`.

## Purpose

Define the package-level contract for the future `mecha_engine.genome` module
before validator code is moved out of `labs/grid_genome`.

## Source Evidence

The Stage 0 validator baseline already proves:

- 50 hand-authored seed grids accepted.
- 200 invalid counterexamples rejected.
- 8-neighbor body-core connectedness.
- Bounds, duplicate-coordinate, organ-reference, mutation-bound, anchor, sensor,
  body-mass, and connectedness failures are covered by lab tests.

The future package must reproduce these guarantees through the package import
surface, not through `labs/` imports.

## Required Public Surface

```python
from mecha_engine.genome import (
    ValidationResult,
    grid_signature,
    render_packet_from_grid,
    validate_grid,
    validate_grid_file,
)
```

Required contracts:

- `ValidationResult(ok: bool, errors: list[str], warnings: list[str])`
- `validate_grid(grid: dict) -> ValidationResult`
- `validate_grid_file(path: str | Path) -> ValidationResult`
- `grid_signature(grid: dict) -> str`
- `render_packet_from_grid(grid: dict, state: dict | None = None) -> dict`

## Validation Acceptance

`validate_grid` must:

- accept all 50 files under `data/seed_grids/`;
- reject all 200 files under `data/invalid_grids/`;
- reject out-of-bounds cells;
- reject duplicate occupied coordinates;
- reject missing animation anchors;
- reject missing required sensor or expression organ;
- reject organ coordinates that do not match a real cell;
- reject required body cores with fewer than 4 cells;
- reject disconnected required body cores using 8-neighbor connectivity;
- reject cell and mutation values outside `0..1`;
- return structured errors without throwing for ordinary invalid payloads;
- avoid mutating the input dictionary.

## Schema Acceptance

The package must preserve the JSON Schema 2020-12 contract in
`research/grid_genome/grid_genome.schema.json`.

Required checks:

- `grid_id`
- `schema_version`
- `grid_size`
- `cells`
- `organs`
- `palette`
- `mutation`

The package implementation may use a JSON Schema library or equivalent internal
checks, but package tests must prove the schema-level and semantic-level gates
remain aligned for the frozen seed and invalid corpora.

## Signature Acceptance

`grid_signature(grid)` must return a deterministic string that changes when any
of these change:

- cell coordinates
- cell roles/organs
- palette id or colors
- grid size
- schema version

The signature function must not include volatile metadata such as notes,
timestamps, or reviewer information.

## Render Packet Acceptance

`render_packet_from_grid(grid, state=None)` must return a JSON-serializable
dictionary with at least:

- `grid_id`
- `grid_size`
- `palette`
- `cells`
- `state`

It must fail or return an invalid result for grids that do not pass
`validate_grid`. It must not own frontend rendering, animation playback, or UI
layout.

`render_packet_v2(grid, lifecycle_state=None, *, animation=None,
slip_profile=None)` (T16; the `slip_profile` gate promoted cycle 05 E1)
wraps `render_packet_from_grid` and adds `animation`, `mood`, and
`animation_vocabulary`. With `slip_profile`, the species'
`visual_grammar.animation_vocab` bounds the vocabulary and a selected
state outside it falls back to a DISPLAYED `idle` while `mood` stays
honest; `slip_profile=None` is byte-identical to the pre-E1 contract
(full vocabulary, no fallback). Verbatim port of the lab authority
`labs/grid_genome/animation_states.build_render_packet_v2`, pinned by
`labs/grid_genome/test_package_animation_parity.py` (the parity scope
note's last carve-out, now closed). The workshop server's
`/api/preview/render` consumes this promoted surface instead of the lab
builder (E1's goal: no shipped surface depends on a lab for packet v2).

## Negative Checks

The genome package gate fails if:

- `packages/mecha_engine/src/mecha_engine/genome` imports `labs`;
- package tests import `labs`;
- package tests mutate `sys.path` to reach `labs`;
- package code silently accepts a known invalid counterexample;
- package code mutates input grids during validation;
- `render_packet_from_grid` becomes a frontend renderer rather than a neutral
  data boundary;
- the package implementation skips the frozen seed/invalid corpora.

## Future Verification Commands

Run these after the scaffold and `genome` implementation exist:

```powershell
python -m json.tool .\research\grid_genome\grid_genome.schema.json > $null
python -B .\labs\grid_genome\test_validator.py
python -B .\labs\grid_genome\test_corpus_builder.py
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
python -c "from mecha_engine.genome import validate_grid, validate_grid_file, grid_signature, render_packet_from_grid"
rg -n "from labs|import labs|labs/|labs\\|sys\\.path" .\packages\mecha_engine
python -B .\labs\package_promotion\package_promotion_gate.py --root . --output-dir .\data\package_promotion
git diff --check
```

Expected implementation-stage result:

- Lab validator tests still pass.
- Package genome tests pass through `mecha_engine.genome`.
- All 50 seed grids pass through the package API.
- All 200 invalid counterexamples fail through the package API.
- The package contains no runtime or test imports from `labs`.
- Package-promotion gate is rerun after package genome tests exist.

## Non-Goals

- No package creation in this research step.
- No generator implementation.
- No lifecycle simulation implementation.
- No frontend renderer.
- No migration of `labs/grid_genome` code until package tests exist.

## Sources

- `research/package_specs/mecha_engine_module_interfaces.md`
- `research/grid_genome/grid_invariants.md`
- `research/grid_genome/grid_genome.schema.json`
- `research/experiment_reports/2026-05-12-grid-validator-baseline.md`
- `data/architecture/mecha_engine_module_interface_specs_stage0.json`
- JSON Schema Draft 2020-12 validation specification:
  https://json-schema.org/draft/2020-12/json-schema-validation
- Python `unittest` documentation:
  https://docs.python.org/3/library/unittest.html

