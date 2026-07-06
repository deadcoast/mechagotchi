# Experiment Report: SLIP Ladder Rung T3.5 — species_class + visual_grammar

Date: 2026-07-05

## Objective

The ladder's final field rung (DR 0012, audit T3.5), unblocked by T4
(animation vocabulary) and T15 (materials coverage): the species'
taxonomy label and its visual language.

## Design

- `species_class` (lowercase identifier): consumed by the evolution
  loop's report identity (rung-conditional key, like parent_selection).
- `visual_grammar {allowed_materials?, animation_vocab?}` (at least one;
  `idle` mandatory in any vocabulary):
  - allowed_materials — **alignment-enforced**: a grid containing a
    material outside the species' grammar fails `is_grid_aligned`, the
    offending material named (the og "allowed materials" restored).
  - animation_vocab — **packet-v2-consumed**: selection outside the
    species' vocabulary falls back to a DISPLAYED idle while `mood`
    stays honest (a hunger-driven `beg` on a species with no beg shows
    idle + mood hungry — pinned); explicit UNKNOWN states still raise.
- All four lab surfaces + the four package `_slip` mirrors synced
  verbatim (DR 0013's parity pins caught the mirrors lagging within
  minutes — the drift guard working exactly as designed); pydantic
  schema + slip lab artifacts regenerated; showcase fixture now
  exercises all six ladder fields.

## Verification

RED → GREEN:

```txt
grid_genome 158 OK · slip_validator 18 OK · lifecycle 19 OK
runtime lineage suite OK · packages 266 OK · workshop 34 OK
```

Mid-rung fixes, both test-caught: constant defined before its
dependency (NameError at import); the vocab clamp initially swallowed
the unknown-state ValueError — unknown raises, known-outside-vocab
falls back.

## The ladder stands complete (fields)

T3.1 forbidden_traits · T3.2 risk_tolerances · T3.3 learning_switches ·
T3.4 lineage_preferences · T3.5 species_class + visual_grammar — every
og SLIP field the audit found missing is now schema-legal,
four-surface-validated, package-mirrored, consumed or enforced, and
workshop-authorable (T3.5 creator controls ride the ladder panel's
existing pattern; full grammar UI lands with T9's trait editor). T3.6
(expressiveness test, fuzz pack, profile zoo 15 → 100) is the remaining
gates phase.

## Sources

- `research/decision_records/0012-slip-schema-extension-ladder.md`, `0013-port-slip-v2-and-packet-v2.md`
- `labs/grid_genome/slip.py`, `labs/grid_genome/animation_states.py`, `labs/grid_genome/test_slip_visual_grammar.py`
- `labs/slip_validator/slip_validator.py`, `labs/slip_validator/pydantic_contract.py`
- `packages/mecha_engine/src/mecha_engine/{generation,lifecycle,repair,runtime}/_slip.py`
- `labs/runtime_integration/mecha_engine_runtime_loop.py`
- `research/slip/slip.schema.json`, `data/slips/valid/slip_v2_no_shell.json`
