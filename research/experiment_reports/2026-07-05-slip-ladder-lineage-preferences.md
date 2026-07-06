# Experiment Report: SLIP Schema Ladder Rung T3.4 — lineage_preferences

Date: 2026-07-05

## Objective

Fourth ladder rung (DR 0012, audit T3.4): profile-authored parent
selection for evolution — which also delivers the parenting comparison
the stress-regime research queued (fitness-weighted vs uniform).

## Design

- Field: `lineage_preferences: {parent_selection: uniform |
  fitness_weighted}` (0.2.0-only, all four validation surfaces,
  showcase fixture extended, counts unchanged).
- **The package-boundary adapter**: promoted modules pin v0.1.0, so the
  authority gains `v01_projection(profile)` — v0.2 profiles project to
  the frozen baseline for package calls (generation, repair, episodes,
  archive metrics); ladder fields are consumed lab-side; v0.1 profiles
  pass through as the same object (bit-for-bit). This unlocks EVERY
  future lab experiment that drives package surfaces with v0.2
  profiles.
- Consumer: the evolution loop accepts `slip_profile` (default None =
  frozen fixture, byte-identical); `fitness_weighted` orders elite
  parents by fitness descending (deterministic truncation bias — with
  population <= elite count only the fittest breed), recorded as
  `parent_source: archive_elites_fitness_weighted` and a top-level
  `parent_selection` key (rung-conditional).

## Verification

RED (no projection, no parameter) → GREEN:

```txt
labs/runtime_integration  Ran 38 tests   OK  (8 new: validation, projection, both modes pick different parents, defaults carry no rung keys)
labs/grid_genome          Ran 108 tests  OK
labs/slip_validator       Ran 18 tests   OK
workshop/tests            Ran 32 tests   OK
packages tests            Ran 235 tests  OK
```

Pinned: uniform vs fitness_weighted produce different generation-1
parent sets under identical seeds; default runs carry no rung keys.

## Findings

1. The v01 projection is the ladder's missing bridge: v0.2 profiles now
   drive full engine experiments with ladder semantics consumed
   lab-side and the frozen contract flowing through package surfaces.
2. Fitness-weighted parenting is now a profile choice — the
   longer-horizon selection study (stress follow-up) can run as a SLIP
   A/B instead of a code fork.

## Sources

- `research/decision_records/0012-slip-schema-extension-ladder.md`
- `labs/grid_genome/slip.py` (v01_projection), `labs/runtime_integration/mecha_engine_runtime_loop.py`, `labs/runtime_integration/test_lineage_preferences.py`
- `labs/slip_validator/slip_validator.py`, `labs/slip_validator/pydantic_contract.py`
- `research/slip/slip.schema.json`, `research/slip/slip_pydantic_model.schema.json`
- `workshop/slip_creator/slip_creator.html`
