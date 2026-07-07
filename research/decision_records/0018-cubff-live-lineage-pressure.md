# Decision Record 0018: CuBFF Live Lineage Pressure (R2) — Plan

Date: 2026-07-06

## Status

**Accepted as the R2 plan** (DR 0017 R-queue; owner directive to plan
before developing, 2026-07-06). R2 is one task of the cycle-02 TODO;
development continues through that TODO's tasks until it is exhausted
and confirmed complete.

## The purpose (why this is the identity-critical task)

The application's whole claim (DR 0017 a.1/a.3) is that the Google CuBFF
experiment's computational-life dynamics produce real, unique engine
output at scale. Today the CuBFF transducer is a proven lab that nothing
in the running engine consumes — an exhibit, not the bloodstream. R2
wires it in: **real CuBFF lineage dynamics shape every generation of the
actual evolution loop.** This is og Pipeline C verbatim (`.depreciated`
research, ratified by the transducer lab): *lineage dynamics → mutation
weights → the ordinary generator*, NEVER tape → pixels (the owner's
original failure the semantic-compiler rule exists to prevent).

## The design

### The seam

The evolution loop already has the exact knob CuBFF should turn:
per-generation **damage severity** (`dropout_rate`) and the generation
model's mutation rates. Pipeline C modulates these from CuBFF features —
high computational-life instability → higher mutation pressure that
generation → a more turbulent, exploratory generation; stable
replication → calmer generations. The archive still selects; SLIP still
constrains; the validator still gates. CuBFF pressures, it never dictates.

### The mechanism (parity-safe by construction)

- A new optional `cubff_pressure_source` on the evolution loop: an
  ordered list of CuBFF snapshots (real ingested + synthetic), one
  consumed per generation (cycling if fewer than `generations`).
- Per generation `g`: `extract_cubff_features(snapshot[g])` →
  `features_to_traits(...)["mutation_pressure"]` ∈ [0,1] → a bounded
  multiplier `1 + PRESSURE_GAIN·(pressure − 0.5)` on that generation's
  effective `dropout_rate` (clamped to a safe band so the lifecycle
  never trivially collapses). The multiplier and source snapshot id are
  recorded per generation in the report.
- **Absent source = byte-identical**: every existing evolution parity
  pin, the sheltered baseline, the stress regime, the workshop wire, and
  the package `evolve` contract stay untouched. This is the same
  optional-consumer discipline the whole SLIP ladder used.

### What gets measured (the honest gate)

- **Determinism**: same snapshots + seed ⇒ identical report.
- **Effect is real and directional**: a high-instability CuBFF sequence
  produces measurably higher mean damage / lower mean survival than a
  low-instability sequence, under the same rng seed — CuBFF dynamics
  visibly moving the ecosystem (the player-noticeable claim, a.4).
- **The semantic-compiler rule holds**: CuBFF never sets cell tokens;
  only pressure scalars cross the boundary (asserted).
- **Lineage provenance**: each generation's report cites its source
  snapshot id, so the CuBFF→generation influence is auditable.

### Scope boundaries (recorded, not faked)

- Lab-first: the loop is the harness. A promoted-module change to
  `runtime.evolve` is a SEPARATE later decision record (like every port).
- Pipeline B (features → full trait vector → SLIP-conditioned
  generation) and the readability/human arms stay out of R2 — Pipeline
  C (mutation weights) is the highest-leverage, lowest-risk wiring and
  the og's own recommended first integration.
- Real-snapshot coverage: R2 uses the ingested real snapshots where
  available and synthetic ones (`build_synthetic_snapshots`) to reach
  `generations`; the real/synthetic split is recorded per run.

## Deliverables (the triad + wiring)

1. `labs/runtime_integration/mecha_engine_runtime_loop.py`:
   `cubff_pressure_source` parameter + per-generation modulation +
   report block; new artifact id when active.
2. `labs/runtime_integration/test_cubff_pressure.py`: RED-first —
   determinism, directional effect (high vs low instability), tokens
   never crossing the boundary, absent-source parity, provenance.
3. Experiment report `2026-07-06-cubff-live-lineage-pressure.md` with
   RED/GREEN + the measured directional result; algorithm-card addendum
   on `cubff_transducer.md`; ledger + TODO.

## Consequences

- CuBFF becomes the engine's bloodstream: the identity claim is now
  demonstrated in the running loop, not just a lab.
- The `runtime.evolve` promotion of this seam is queued as its own
  task (R2.5) in the cycle-02 TODO.

## Sources

- `research/decision_records/0017-recalibration-engine-game-duality.md` (R2)
- `labs/cubff_transducer/cubff_transducer.py` (extract_cubff_features, features_to_traits)
- `labs/cubff_transducer/real_snapshot_ingest.py`, `data/cubff_real_ingest/`
- `labs/runtime_integration/mecha_engine_runtime_loop.py` (the seam)
- `research/algorithm_cards/cubff_transducer.md`
