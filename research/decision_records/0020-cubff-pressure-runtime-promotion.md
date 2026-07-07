# Decision Record 0020: CuBFF Pressure into `runtime.evolve` (R2.5) — Plan

Date: 2026-07-07

## Status

**Accepted as the R2.5 plan** (queued by DR 0018/DR 0019; the DR 0018
checkpoint's recorded next step). This record is the checkpoint plan;
on its completion a fresh plan is required.

## The purpose

R2 proved CuBFF live lineage pressure in the lab harness
(`labs/runtime_integration`, DR 0018): Pipeline C — lineage dynamics →
mutation weights — measurably steering every generation. The promoted
package's `runtime.evolve` is the engine surface applications consume;
until the seam exists there, the identity-critical integration lives
only lab-side. R2.5 promotes it, by its own record like every prior
port (DR 0008/0013/0016 pattern).

## The design

### The seam in the package

`mecha_engine.runtime.evolve` already threads `dropout_rate` into
`live_cycle` per creature. The port: an optional keyword-only
`cubff_pressure_source: list[dict] | None` — per generation `g`,
snapshot `g % len(source)` → `extract_cubff_features` →
`features_to_traits(...)["mutation_pressure"]` → multiplier
`1 + 1.1·(pressure − 0.5)` clamped to `[0.5, 1.6]` → that generation's
effective `dropout_rate` for every `live_cycle` call. Constants and
formula VERBATIM from the lab loop (`CUBFF_PRESSURE_GAIN`,
`CUBFF_MULTIPLIER_BAND`, `_cubff_generation_pressure`).

### The mirror discipline (package may not import labs)

`runtime/_cubff.py`: verbatim private port of the lab authority's
`extract_cubff_features` and `features_to_traits` plus their stdlib
helpers (`_tape_values`, `_normalized_entropy`, `_motif_counts`,
`_motif_repetition_rate`, `_compression_ratio`, `_is_number`, `_mean`,
`_clamp`) — the `_slip` mirror discipline: synced verbatim from
`labs/cubff_transducer/cubff_transducer.py` whenever the authority
changes, drift caught by a lab-side parity pin.

### Contract and parity gates

- **Package contract** (`tests/test_runtime_cubff_contract.py`,
  subprocess driver with `PYTHONPATH=src`, the established pattern):
  signature accepts the keyword; absent source byte-identical to the
  DR 0016 contract; active source stamps a `cubff_pressure` report
  block (`semantic_rule`, gain, band, per-generation snapshot_id /
  mutation_pressure / dropout_multiplier — scalars ONLY, the
  semantic-compiler rule); deterministic; directional (high-instability
  source removes more cells than low, same seed); input validation
  (non-list / empty list raise ValueError in contract style).
- **Lab-side parity pin**
  (`labs/cubff_transducer/test_package_cubff_parity.py`): the package
  mirror's features and traits EQUAL the lab authority's on synthetic
  snapshots and edge fixtures; the multiplier band/gain equal the lab
  loop's.

### Honest scope (recorded, not faked)

- **Real snapshots**: `data/cubff_real_ingest/` currently holds ZERO
  real exports — the ingest gate reports `awaiting_real_cubff_snapshots`
  (`blocked_real_snapshot_absent`). The TODO's "real ingested snapshots
  exercised" clause therefore CANNOT be developed yet; it stays a
  recorded blocked state on the report and in the ledger until real
  soup/checkpoint exports are ingested through the existing gate. The
  contract runs on synthetic snapshots (the same
  `build_synthetic_snapshots` semantics R2 used) plus hand-built
  stable/chaotic fixtures.
- No changes to `live_cycle`'s own contract; the modulation is
  `evolve`-level.
- The workshop/`mechas` surfaces do not grow a flag in R2.5 — wiring
  applications to the promoted seam is future game-loop work (R4).

## Deliverables

1. `packages/mecha_engine/src/mecha_engine/runtime/_cubff.py` (verbatim
   mirror) and the `evolve` seam + report block.
2. `packages/mecha_engine/tests/test_runtime_cubff_contract.py` (+
   driver), RED-first.
3. `labs/cubff_transducer/test_package_cubff_parity.py` parity pin.
4. Experiment report `2026-07-07-cubff-pressure-runtime-promotion.md`,
   algorithm-card addendum, spec/traceability note, ledger, TODO.

## Consequences

- The engine's public `evolve` carries CuBFF lineage pressure natively;
  the game loop (R4) can consume it without touching labs.
- The real-snapshot blocked state is now visible on the promoted
  surface's own report, keeping the pressure honest.

## Sources

- `research/decision_records/0018-cubff-live-lineage-pressure.md`
- `labs/cubff_transducer/cubff_transducer.py` (the authority)
- `labs/runtime_integration/mecha_engine_runtime_loop.py` (R2 semantics)
- `packages/mecha_engine/src/mecha_engine/runtime/evolve.py` (the seam)
- `data/cubff_real_ingest/real_snapshot_ingest_stage0_report.json` (the honest blocker)
- `research/package_specs/mecha_engine_runtime_interface_spec.md`
