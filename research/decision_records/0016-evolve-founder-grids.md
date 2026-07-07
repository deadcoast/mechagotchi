# Decision Record 0016: `runtime.evolve` Founder Grids (T1.5)

Date: 2026-07-06

## Status

**Accepted** (audit T1.5, owner-gated — authorized by the owner's
run-to-completion directive, 2026-07-06). The T1 wire's founder
semantics become part of the promoted `runtime.evolve` contract.

## Decision

`evolve(...)` gains `founder_grids: list[dict] | None = None`
(keyword-only): released creatures admitted through the ENGINE'S OWN
gates exactly as the T1 lab wire does — `validate_grid` + SLIP
alignment, rejections recorded with the engine's errors verbatim;
admitted founders LEAD the generation-0 parent pool so the wire is
always exercised. The report gains a rung-conditional `founders` block
(`admitted_ids`, `rejected`) and generation 0 reports
`parent_source: founders_plus_seed_pool` when founders exist. Default
`None` is byte-identical (every existing parity pin must pass
unmodified).

## Gates

Contract tests: admission + verbatim rejection errors, founders-lead
ordering pin, defaults carry no founder keys. Lab-side parity: evolve's
generation-0 parentage equals the T1 wire loop's under the same
founders.

## Sources

- `audits/TODO.md` (T1.5), `research/experiment_reports/2026-07-05-workshop-engine-wire.md`
- `labs/runtime_integration/mecha_engine_runtime_loop.py` (the lab semantics)
- `packages/mecha_engine/src/mecha_engine/runtime/evolve.py`
