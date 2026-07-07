# Decision Record 0027: The `slip` Module — Disposition (E4)

Date: 2026-07-07

## Status

**Accepted** (cycle 05 E4). `slip` is the LAST deferred `mecha_engine`
module target (DR 0004's list; `render` dispositioned by DR 0026). The
DR 0024/0026 disposition method, applied — and unlike render, the
verdict is **PROMOTE: the target is authorized**. The port itself is
its own task under the established authorize-then-gate pattern
(DR 0022 → C2/C3): this record fixes the design; code moves when its
gates pass.

## The evidence — slip has what render lacked

| Disposition test | render (DR 0026) | slip (this record) |
| --- | --- | --- |
| A real consumer needing a promoted surface | none — pixel code is browser JS | FOUR package-internal consumers (`generation`, `lifecycle`, `repair`, `runtime` each carry a private `_slip.py` mirror, ~19–20 KB apiece) plus the workshop server, whose own charter docstring promises to "switch to a promoted `mecha_engine.slip` surface when one exists" while importing the LAB authority today |
| Verbatim-portable semantics | no Python drawing source | pure-stdlib validators (`validate_slip`, `is_grid_aligned`, the v0.2 ladder fields) — already living inside the package four times over |
| A cost to NOT promoting | none | ~80 KB of quadruplicated validator logic inside the promoted package, held in sync only by the DR 0013 parity pins (which have already caught mirrors lagging) — every ladder rung lands four times |

## Decision — authorize `mecha_engine.slip`; the port is its own task

A public `mecha_engine.slip` module becomes the tenth target: the
single in-package SLIP authority (`validate_slip`, `is_grid_aligned`,
and the ladder-field validation), which the four modules then import
PUBLICLY (the copy-never-import rule binds private files; a public
module is exactly how `runtime` already consumes `genome`/`lifecycle`/
`archive`). The four `_slip.py` mirrors collapse into thin imports or
disappear; the workshop server switches from the lab import, fulfilling
its docstring's standing promise.

**Gates for the port (its own queued task, not this record):**

1. **Mirror reconciliation first** — the four mirrors hash differently
   today; prove they are behaviorally identical over the SLIP zoo +
   fuzz corpora (or name any divergence and its reason) BEFORE
   collapsing them. The reconciled text, pinned against the lab
   authority (`labs/grid_genome/slip.py`), is the module source.
2. Contract tests through the package surface (the slip-zoo gates as
   the fixture corpus); lab-side parity pin against the Stage 0
   authority; every existing DR 0013 parity pin passes unmodified.
3. The four modules' behavior is byte-identical after the collapse
   (their full suites are the regression harness).
4. The workshop switch is behavior-identical (its endpoint suite).
5. Promotion-gate candidate registered; the gate says
   `promotion_ready` before the port merges (the C2/C3 precedent).

## Consequences

- The deferred-target list empties: all ten og module targets are now
  either promoted (nine) or authorized with a fixed design (this one).
- `pydantic_contract.py` (the jsonschema/pydantic mirror in
  `labs/slip_validator/`) stays LAB-SIDE by design — it exists to
  cross-check the stdlib authority from an independent implementation,
  and independence is its value; promoting it would collapse the
  redundancy the check depends on.

## Sources

- `research/decision_records/0004-mecha-engine-package-scaffold.md` (the deferral)
- `research/decision_records/0024-grid-schema-animation-species-resolution.md`, `0026-render-module-disposition.md` (the method)
- `research/decision_records/0022-storage-module.md` (the authorize-then-gate pattern)
- `research/decision_records/0013-port-slip-v2-and-packet-v2.md` (the mirrors and their parity pins)
- `packages/mecha_engine/src/mecha_engine/{generation,lifecycle,repair,runtime}/_slip.py` (the four mirrors)
- `labs/grid_genome/slip.py` (the Stage 0 authority), `labs/grid_genome/test_package_slip_parity.py`
- `workshop/server/workshop_server.py` (the consumer's standing promise, docstring line 7)
- `data/slips/zoo/` + `labs/slip_validator/slip_zoo_gates.py` (the port's fixture corpus)
