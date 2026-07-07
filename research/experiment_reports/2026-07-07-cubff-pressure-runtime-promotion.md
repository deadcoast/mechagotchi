# Experiment Report: CuBFF Pressure into `runtime.evolve` (R2.5)

Date: 2026-07-07. Plan: decision record 0020.

## Objective

Promote the R2 seam (DR 0018 — Pipeline C: lineage dynamics → mutation
weights) from the lab harness into `mecha_engine.runtime.evolve`, the
engine surface applications consume, so CuBFF lineage pressure is
native to the promoted engine.

## Method (per DR 0020)

- `runtime/_cubff.py`: VERBATIM private mirror of the lab authority's
  `extract_cubff_features`/`features_to_traits` and their stdlib
  helpers, extracted programmatically from
  `labs/cubff_transducer/cubff_transducer.py` (the `_slip` mirror
  discipline).
- `evolve(..., cubff_pressure_source=None)`: keyword-only; per
  generation, snapshot `g % len(source)` → `mutation_pressure` →
  multiplier `1 + 1.1·(p − 0.5)` clamped to `[0.5, 1.6]` (constants and
  formula verbatim from the lab loop) applied to that generation's
  `live_cycle` damage severity. Report gains a `cubff_pressure` block —
  scalars only (the semantic-compiler rule).

## Verification

RED → GREEN: `packages/mecha_engine/tests/test_runtime_cubff_contract.py`
via the subprocess contract driver (signature, absent-source byte
parity, report block, scalars-only boundary, snapshot cycling order,
determinism, directional effect, ValueError on non-list/empty source).
Lab-side drift guard: `labs/cubff_transducer/test_package_cubff_parity.py`
pins the mirror's features/traits EQUAL to the lab authority on 12
synthetic + 4 edge snapshots and pins the promoted constants/formula to
the lab loop's. The runtime contract's keyword-only signature pin fired
during the port (the drift guard working) and was extended with a
DR 0020 traceability note, as DR 0016's port did before it. Full 11-lab
sweep + 268-test package suite + architecture scaffold gate green.

## Results (promoted surface, same seed)

```txt
                     dropout multiplier   total cells removed
chaotic soup            1.170             34
stable soup             0.900             28
```

The promoted `evolve` reproduces the R2 finding on the package surface:
turbulent computational-life substrates produce measurably more
turbulent generations, provenance-stamped per generation.

## Honest blocked state

`data/cubff_real_ingest/` holds ZERO real CuBFF exports — the ingest
gate reports `awaiting_real_cubff_snapshots` /
`blocked_real_snapshot_absent`. The TODO's "real ingested snapshots
exercised" clause is therefore NOT claimed: the contract runs on
synthetic and hand-built fixture snapshots. The clause unblocks when
real soup/checkpoint exports are ingested through the existing gate,
with no code change needed on this seam.

## Decision

Promoted. The game loop (R4) can consume CuBFF lineage pressure through
the package without touching labs. Next per the R-queue: R4 — the game
loop decision record.

## Sources

- `research/decision_records/0020-cubff-pressure-runtime-promotion.md`
- `packages/mecha_engine/src/mecha_engine/runtime/_cubff.py`, `packages/mecha_engine/src/mecha_engine/runtime/evolve.py`
- `packages/mecha_engine/tests/test_runtime_cubff_contract.py`, `packages/mecha_engine/tests/helpers/cubff_pressure_contract_driver.py`
- `labs/cubff_transducer/test_package_cubff_parity.py`
- `research/experiment_reports/2026-07-06-cubff-live-lineage-pressure.md` (R2)
- `data/cubff_real_ingest/real_snapshot_ingest_stage0_report.json` (the honest blocker)
