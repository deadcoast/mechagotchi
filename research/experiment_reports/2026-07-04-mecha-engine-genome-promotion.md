# mecha_engine Genome Module Promotion

Date: 2026-07-04

Status: `package_genome_module_promoted_contract_evidence`

## Purpose

Execute the first module promotion into `packages/mecha_engine`, in the
order fixed by
`research/package_specs/mecha_engine_contract_traceability_matrix.md`
(genome first), against the interfaces and hard gates defined in
`research/package_specs/mecha_engine_module_interfaces.md` and
`research/package_specs/mecha_engine_genome_contract_gate.md`.

## What changed

`packages/mecha_engine/src/mecha_engine/genome/` now implements the full
contracted surface, self-contained (stdlib only, no `labs` imports, no
artifact writes, typed):

- `validation.py` — `ValidationResult` (frozen dataclass), `validate_grid`,
  `validate_grid_file`, and the exported invariant constants
  (`BODY_CORE_MIN_CELLS = 4`, grid-size range, schema version). A verbatim
  semantic port of `labs/grid_genome/validator.py`: identical invariants,
  identical error strings, same 8-connectivity BFS.
- `signature.py` — `grid_signature` (`sha256:` + canonical JSON). Keeps the
  lab's cell ordering/surface and extends it with the gate-required organ,
  palette, grid-size, and schema-version surfaces (gate spec wins over raw
  port).
- `render.py` — `render_packet_from_grid(grid, state=None)`; validates
  first, raises `ValueError` on invalid grids, returns a deep-copied packet
  per the genome contract gate's Render Packet Acceptance (no lab source
  exists for this surface; the gate definition is the source of truth).

Package tests (`tests/test_genome_contract.py`, 17 tests, subprocess-driven
with the same src-layout mechanics as the import tests — no `sys.path` text
anywhere in the package tree) prove the hard gates. A lab-side parity pin
(`labs/grid_genome/test_package_genome_parity.py`) runs both validators over
the full corpus (labs→package import is the allowed direction; the
traceability matrix forbids only package→labs).

The scaffold verification gate evolved per its own scoping: a module is
recorded as promoted when its contract test exists; the placeholder-only
check now covers unpromoted modules only. Artifact regenerated
(`promoted_modules: ["genome"]`, decision
`accept_package_scaffold_with_promoted_modules`, 9/9 checks pass).

## Result

- Seed corpus: **50/50 accepted**; render packets built for all 50.
- Invalid corpus: **200/200 rejected** with structured errors.
- No-input-mutation: deep-copy compare across all 250 files plus 17
  single-fault variants — zero mutations.
- Schema: Draft 2020-12 asserted; schema `required` == package
  `REQUIRED_TOP_LEVEL_FIELDS`; each required-field removal rejected.
- P1 single-fault set: 17 deterministic faults all rejected with the
  expected error family. (Two P1 entries — body-mass-above-maximum and
  palette-reference — have no backing invariant in the authoritative
  validator or genome gate and were excluded to preserve exact parity.)
- Parity: lab and package outcomes **byte-identical** over all 250 files
  (ok flags and full error lists).

```powershell
python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
# Ran 24 tests - OK  (7 import + 17 genome contract)
```

Full sweep: 487 lab tests + 24 package tests, all green.

## Decision

`mecha_engine.genome` is promoted with contract evidence. Next module in
the traceability order: `generation`. The promotion gate rerun happens
after the in-flight learning/repair research batch lands, so both evidence
changes are evaluated together.

## Verification

```powershell
python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
python -B -m unittest discover -s labs/grid_genome -p "test_package_genome_parity.py"
python -B labs/architecture/mecha_engine_scaffold_verification_gate.py
python -m json.tool data/architecture/mecha_engine_scaffold_verification_gate_stage0.json
```

## Sources

- `research/package_specs/mecha_engine_module_interfaces.md`
- `research/package_specs/mecha_engine_genome_contract_gate.md`
- `research/package_specs/mecha_engine_contract_traceability_matrix.md`
- `research/package_specs/mecha_engine_property_negative_test_strategy.md`
- `research/package_specs/mecha_engine_test_fixture_manifest.md`
- `labs/grid_genome/validator.py`
- `labs/grid_genome/grid_helpers.py`
- `packages/mecha_engine/src/mecha_engine/genome/`
- `packages/mecha_engine/tests/test_genome_contract.py`
- `labs/grid_genome/test_package_genome_parity.py`
- `data/architecture/mecha_engine_scaffold_verification_gate_stage0.json`
