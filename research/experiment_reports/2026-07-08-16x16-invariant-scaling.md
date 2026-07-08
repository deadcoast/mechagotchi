# Experiment Report: 16×16 Invariant Scaling — the Foundation Re-derived at Documented Scale (Cycle 09 · ENGINE · A1)

Date: 2026-07-08

## WHY

The gap analysis' first row is the foundational gap: the documents name
16×16 as the primary creature scale (validity-research §1.34 — the
creature that "proves the entire thesis"; the dossier's bake-off
protocol and its 16×16 invariants block), while every invariant, corpus,
and gate in this repository was proven at 8×8 with ~13-cell bodies.
DR 0014 committed 8×8 for its phase and required that any size adoption
take its own decision record backed by measurement — the 8×8 constants
must not be scaled by fiat. A1 is that measurement: re-derive the
hard/soft invariants at 16×16 empirically and ratify.

## WHAT

`labs/grid_genome/invariant_scaling.py` measures four populations and
evaluates candidate body-core floors:

1. **8×8 seed census** — the 50 proven seeds expressed as dimensionless
   statistics (core mass, occupancy fraction, symmetry, organ presence,
   4- vs 8-connectivity of the required core).
2. **2×-upscaled controls** — DR 0014's probe method applied to all 50
   seeds: the area-scaling anchor and the characterized "upscaled blob"
   anti-goal for A2.
3. **Ten hand-authored 16×16 pilot exemplars** — real morphology from
   the DR 0015 vocabulary (shell, joint, limb, antenna, sensor,
   decoration, effect) across all five palettes, valid against BOTH the
   lab and promoted-package validators, with deliberate probes: an
   18-core strider at the documented floor, a 60-core turtle near the
   occupancy ceiling (whose diagonal neck makes its core 8- but not
   4-connected), a 0.13-symmetry serpent, a 0.65-symmetry golem.
4. **Seeded noise experiments** — chance-pass probability of the
   mass+connectivity invariant for uniformly scattered cells (the
   validator's actual semantic; 4,000 trials per configuration), and
   largest-component characterization of density-matched scatter
   (1,000 trials).

Candidate floors {4 status-quo, 8 linear, 16 area-preserving,
18 documented, 24} were gated on: every pilot passes, every control
passes, chance-pass ≤ 2% (the standing false-accept bar), and
canvas-share within ±25% of the ratified 8×8 share (4/64).

## FINDINGS

| Measurement | 8×8 (proven corpus) | 16×16 (pilots) |
| --- | --- | --- |
| Core mass | 9–14 (p50 10) | 18–60 (p50 44) |
| Occupancy fraction | 0.1875–0.2656 (p50 0.2031) | 0.109–0.4375 |
| Symmetry (mirror formula) | 0.286–0.857, 4/5 bins | 0.128–1.0, 3/5 bins |
| Eyes per creature | 2–3 | 2–8 (2×2 eye blocks afforded) |
| Anchors per creature | exactly 1 | exactly 1 |
| Core 4-connected fraction | **0.74** | 0.80 |
| Chance-pass at own floor | 0.625% (k=4) | **0.0** (all candidates, 4,000 trials) |

- **The area law holds for silhouette-preserving upscaling**: control
  core mass is exactly 4× the parent and every dimensionless statistic
  is preserved — so a floor that preserves canvas share sits at 16–18
  cells, and the linear guess (8) is refutably wrong.
- **Floor verdicts**: 4 (1.6% share), 8 (3.1%), and 24 (9.4%) fail the
  ±25% share band; 16 and 18 pass every gate. **18 is adopted**: it is
  the documented dossier value AND it exceeds the p95 accidental blob
  of density-matched noise at 16×16 (**17 cells**; max observed 27),
  which 16 does not. The ratified law `max(4, 18·w·h // 256)`
  reproduces both ratified points (8×8 → 4 unchanged).
- **8-neighbor connectivity is load-bearing, not decorative**: 26% of
  the proven 8×8 seed cores and one pilot are 8- but not 4-connected.
  Topology unchanged.
- **Scale strengthens the invariant**: chance-pass rejection goes from
  0.625% at the 8×8 floor to unmeasurably small (0 in 4,000) for every
  16×16 candidate — comfortably under the ≤2% false-accept bar.
- **Sensor pair**: every 8×8 seed and every pilot already carries ≥2
  eyes; the dossier's `requires_sensor_pair` is ratified as a soft
  expectation and an A2 corpus gate, with hard-validator status
  deferred to A3 (generator evidence first). Hard invariant 7 is
  unchanged.
- **Soft bands at 16×16**: symmetry spans the full descriptor range
  with evidence at low/mid/high; occupancy soft ceiling ~0.44 (16×16
  affords much heavier silhouettes than the 8×8 band without filling
  the canvas); one animation anchor per creature remains the norm.

## VERDICT

**16×16 is ratified as the proven default target scale (DR 0029)**;
body-core floor 18 at 16×16 via the size-parametric law; 8×8 stays
ratified at 4 and remains valid input. Engine adoption of the law is
task A3 — RED-first, size-parametric, never size-replacing; the lab and
package validators deliberately keep the 8×8 constant (and its exact
error string) until then, so every parity pin stays unbroken. Honest
remainder, recorded as blocked states in the artifact: the engine
validator constant, SLIP fixture mass bounds, the generation model's
8×8-only emission, the archive's `mass/16` stress probe, and 16×16
readability calibration (learned-model retrain in A3; the human survey
stays the deferred fallback, never a blocker).

## Verification

RED (suite before the module existed):

```powershell
PS> python -B -m unittest discover -s labs/grid_genome -p "test_invariant_scaling.py"
ModuleNotFoundError: No module named 'invariant_scaling'
Ran 1 test in 0.000s
FAILED (errors=1)
```

GREEN (same command after implementation):

```powershell
PS> python -B -m unittest discover -s labs/grid_genome -p "test_invariant_scaling.py"
Ran 22 tests in 3.112s
OK
```

Lab (artifact production; summary excerpt):

```powershell
PS> python -B labs/grid_genome/invariant_scaling.py
{
  "artifact_id": "invariant_scaling_16x16_stage0",
  "status": "complete",
  "ratified": {
    "floor_16x16": 18,
    "floor_8x8": 4,
    "floor_law": "max(4, 18 * width * height // 256)",
    "floor_law_table": {"8x8": 4, "12x12": 10, "16x16": 18, "24x24": 40, "32x32": 72, "64x64": 288},
    ...
  },
  "pilot_core_mass": {"min": 18, "p50": 44.0, "max": 60}
}
```

Full lab suite (unchanged surfaces still green):

```powershell
PS> python -B -m unittest discover -s labs/grid_genome -p "test_*.py"
Ran 193 tests in 10.142s
OK
```

## Sources

- `labs/grid_genome/invariant_scaling.py`, `labs/grid_genome/test_invariant_scaling.py`
- `data/grid_genome/invariant_scaling_16x16_stage0.json`
- `data/grid_genome/pilot_16x16/`
- `research/algorithm_cards/invariant_scaling_16x16.md`
- `research/decision_records/0029-16x16-default-grid-scale.md`
- `research/grid_genome/grid_invariants.md`, `research/grid_genome/grid_genome.schema.json`
- `research/decision_records/0014-grid-size-commitment.md`, `0015-dormant-vocabulary-coverage.md`
- `docs/gap-analysis.md`, `audits/TODO.md` (cycle 09 A1)
- `docs/project-research/validity-research.md` (§1.34), `docs/project-research/deep-research/01/deep-research.md`
