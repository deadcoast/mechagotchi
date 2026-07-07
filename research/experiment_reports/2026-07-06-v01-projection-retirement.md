# Experiment Report: v01_projection Retirement (DR 0013 follow-up)

Date: 2026-07-06

## Objective

The documented follow-up from the DR 0013 port: with the package
consuming SLIP v0.2 natively, does the evolution loop still need the
projection adapter?

## Verification

RED first, proving the point both directions: WITH the projection, an
all-off `learning_switches` profile produced fitness IDENTICAL to the
default run (the projection stripped the switches before package
episodes — ladder semantics never reached the engine). After
retirement, the same profile produces measurably DIFFERENT creature
fitness inside the loop (rules-only episodes) — native consumption end
to end, pinned by test. The frozen v0.1 default remains byte-identical
(pinned; full runtime suite of 44 green, incl. all wire/lineage/parity
tests and the DR 0013 evolve-parity file).

## Decision

The loop passes full profiles to every package surface. The
`v01_projection` helper REMAINS in the authority with its tests — it is
the documented adapter for any consumer that pins v0.1 (none in-tree
today), not dead code.

## Sources

- `labs/runtime_integration/mecha_engine_runtime_loop.py`, `labs/runtime_integration/test_v01_projection_retirement.py`
- `labs/grid_genome/slip.py` (the retained adapter)
- `research/decision_records/0013-port-slip-v2-and-packet-v2.md`
